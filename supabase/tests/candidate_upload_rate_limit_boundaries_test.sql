\set ON_ERROR_STOP on
begin;

do $$
declare
  v_candidate uuid := gen_random_uuid();
  v_auth uuid := gen_random_uuid();
  v_session uuid := gen_random_uuid();
  v_doc_type uuid;
  v_notice text := 's08-upload-' || replace(gen_random_uuid()::text, '-', '');
  v_identity_digest text := repeat('1', 64);
  v_ip_digest text := repeat('2', 64);
  v_blocked_identity_digest text := repeat('3', 64);
  v_blocked_ip_digest text := repeat('4', 64);
  v_result jsonb;
  v_reservation uuid;
  v_blocked_reservation uuid := gen_random_uuid();
  v_window_start timestamptz;
  v_request uuid;
begin
  assert not has_function_privilege(
    'authenticated',
    'public.reserve_candidate_form_upload(uuid,uuid,text,text,bigint,uuid)',
    'EXECUTE'
  ), 'legacy reserve RPC must not be browser executable';
  assert not has_function_privilege(
    'authenticated',
    'public.record_candidate_upload_completed(uuid,bigint,text)',
    'EXECUTE'
  ), 'legacy completion mutation must not be browser executable';
  assert not has_function_privilege(
    'authenticated',
    'public.request_candidate_document_scan(uuid,uuid,text,uuid)',
    'EXECUTE'
  ), 'scan-request mutation must not be browser executable';
  assert has_function_privilege(
    'authenticated',
    'public.continue_clean_candidate_document_scan(uuid,uuid)',
    'EXECUTE'
  ), 'CLEAN continuation remains candidate reachable and uncharged';

  assert not has_function_privilege(
    'authenticated',
    'public.reserve_candidate_form_upload_rate_limited(uuid,text,text,uuid,uuid,text,text,bigint,uuid)',
    'EXECUTE'
  ), 'rate-limited reserve wrapper is service-only';
  assert has_function_privilege(
    'service_role',
    'public.reserve_candidate_form_upload_rate_limited(uuid,text,text,uuid,uuid,text,text,bigint,uuid)',
    'EXECUTE'
  ), 'service role may execute reserve wrapper';
  assert not has_function_privilege(
    'authenticated',
    'public.authorize_candidate_upload_completion_rate_limited(uuid,text,text,uuid,uuid)',
    'EXECUTE'
  ), 'completion limiter gate is service-only';
  assert has_function_privilege(
    'service_role',
    'public.authorize_candidate_upload_completion_rate_limited(uuid,text,text,uuid,uuid)',
    'EXECUTE'
  ), 'service role may execute completion limiter gate';
  assert not has_function_privilege(
    'authenticated',
    'public.request_candidate_document_scan_as_actor(uuid,uuid,uuid,text,uuid)',
    'EXECUTE'
  ), 'actor-bound scan bridge is service-only';

  select document_type_id into v_doc_type
  from public.document_types
  where code = 'CV_RESUME'
  limit 1;
  if v_doc_type is null then
    insert into public.document_types(code,name_vi,name_en,scope_code,is_active)
    values('CV_RESUME','S08 upload CV','S08 upload CV','SUBMISSION',true)
    on conflict(code) do update set is_active=true
    returning document_type_id into v_doc_type;
  end if;

  insert into public.candidates(candidate_id,auth_user_id,email,current_full_name,is_active)
  values(v_candidate,v_auth,'upload-'||v_candidate||'@example.invalid','Upload Candidate',true);
  insert into public.privacy_notice_versions(
    notice_version,content_vi,content_en,content_hash_sha256,published_at,effective_from,is_current
  ) values(
    v_notice,'S08 upload notice','S08 upload notice',repeat('f',64),clock_timestamp(),clock_timestamp(),false
  );
  insert into public.candidate_form_sessions(
    candidate_form_session_id,candidate_id,mode_code,status_code,presented_privacy_notice_version,expires_at
  ) values(
    v_session,v_candidate,'NEW_SUBMISSION','OPEN',v_notice,clock_timestamp()+interval '1 hour'
  );

  -- Positive reserve consumes one unit in BOTH shared UPLOAD buckets and then
  -- performs the accepted reservation mutation.
  v_result := public.reserve_candidate_form_upload_rate_limited(
    v_auth,
    v_identity_digest,
    v_ip_digest,
    v_session,
    v_doc_type,
    'cv.pdf',
    'application/pdf',
    100,
    gen_random_uuid()
  );
  assert (v_result->>'success')::boolean, 'rate-limited reserve succeeds below quota';
  v_reservation := (v_result->'data'->>'upload_reservation_id')::uuid;
  assert exists(
    select 1 from public.upload_reservations where upload_reservation_id=v_reservation
  ), 'successful reserve creates one reservation';
  assert (
    select request_count = 1
    from private.rate_limit_buckets
    where policy_code='UPLOAD' and rule_code='IDENTITY_15M' and key_digest=v_identity_digest
  ), 'reserve debits shared identity bucket once';
  assert (
    select request_count = 1
    from private.rate_limit_buckets
    where policy_code='UPLOAD' and rule_code='IP_15M' and key_digest=v_ip_digest
  ), 'reserve debits shared IP bucket once';

  -- Completion reuses the SAME UPLOAD identity/IP buckets rather than a
  -- per-boundary quota. No protected mutation occurs in this authorization gate.
  v_result := public.authorize_candidate_upload_completion_rate_limited(
    v_auth,v_identity_digest,v_ip_digest,v_session,v_reservation
  );
  assert (v_result->>'success')::boolean, 'completion gate succeeds below quota';
  assert (
    select request_count = 2
    from private.rate_limit_buckets
    where policy_code='UPLOAD' and rule_code='IDENTITY_15M' and key_digest=v_identity_digest
  ), 'completion increments the same identity bucket';
  assert (
    select request_count = 2
    from private.rate_limit_buckets
    where policy_code='UPLOAD' and rule_code='IP_15M' and key_digest=v_ip_digest
  ), 'completion increments the same IP bucket';
  assert not exists(
    select 1 from public.document_scan_requests where upload_reservation_id=v_reservation
  ), 'completion limiter gate itself creates no scan request';

  -- Seed an identity bucket at limit and prove atomic rejection: the IP bucket
  -- is not partially debited and no business reservation is created.
  v_window_start := pg_catalog.to_timestamp(
    pg_catalog.floor(extract(epoch from pg_catalog.clock_timestamp()) / 900) * 900
  );
  insert into private.rate_limit_buckets(
    policy_code,rule_code,key_digest,window_seconds,window_started_at,request_count,expires_at,updated_at
  ) values(
    'UPLOAD','IDENTITY_15M',v_blocked_identity_digest,900,v_window_start,30,
    v_window_start+interval '15 minutes',clock_timestamp()
  );

  v_result := public.reserve_candidate_form_upload_rate_limited(
    v_auth,
    v_blocked_identity_digest,
    v_blocked_ip_digest,
    v_session,
    v_doc_type,
    'blocked.pdf',
    'application/pdf',
    100,
    gen_random_uuid()
  );
  assert v_result->>'error_code'='RATE_LIMITED', 'reserve blocks at identity ceiling';
  assert (v_result->'data'->>'retry_after_seconds')::integer >= 1,
    'blocked reserve returns authoritative retry timing';
  assert not exists(
    select 1 from private.rate_limit_buckets
    where policy_code='UPLOAD' and rule_code='IP_15M' and key_digest=v_blocked_ip_digest
  ), 'blocked multi-rule request does not partially debit IP quota';
  assert not exists(
    select 1 from public.upload_reservations where original_filename='blocked.pdf'
  ), 'blocked reserve performs no reservation mutation';

  -- A valid reservation is still blocked by the same exhausted aggregate
  -- identity quota before inspection/scan mutation can begin.
  insert into public.upload_reservations(
    upload_reservation_id,candidate_form_session_id,intended_document_type_id,temp_bucket,temp_path,
    original_filename,declared_mime_type,expected_max_size_bytes,actor_auth_user_id,idempotency_key,expires_at
  ) values(
    v_blocked_reservation,v_session,v_doc_type,'candidate-quarantine',
    'temp/'||v_session||'/'||v_blocked_reservation||'/blocked-completion.pdf',
    'blocked-completion.pdf','application/pdf',100,v_auth,gen_random_uuid(),clock_timestamp()+interval '1 hour'
  );
  v_result := public.authorize_candidate_upload_completion_rate_limited(
    v_auth,v_blocked_identity_digest,v_blocked_ip_digest,v_session,v_blocked_reservation
  );
  assert v_result->>'error_code'='RATE_LIMITED', 'completion blocks at shared identity ceiling';
  assert not exists(
    select 1 from public.document_scan_requests where upload_reservation_id=v_blocked_reservation
  ), 'blocked completion creates no scan request';
  assert (
    select status_code='RESERVED' from public.upload_reservations
    where upload_reservation_id=v_blocked_reservation
  ), 'blocked completion leaves reservation business state unchanged';

  -- After trusted inspection metadata is present, only the service bridge can
  -- create a scan request; the legacy browser path remains closed.
  update public.upload_reservations
  set status_code='UPLOADED', malware_scan_status='PENDING', actual_size_bytes=100,
      detected_mime_type='application/pdf', checksum_sha256=repeat('a',64)
  where upload_reservation_id=v_reservation;

  perform pg_catalog.set_config('request.jwt.claim.sub',v_auth::text,true);
  execute 'set local role authenticated';
  begin
    perform public.request_candidate_document_scan(v_session,v_reservation,'ADD',null);
    raise exception 'browser scan-request mutation unexpectedly permitted';
  exception when insufficient_privilege then null;
  end;
  execute 'reset role';

  v_result := public.request_candidate_document_scan_as_actor(
    v_auth,v_session,v_reservation,'ADD',null
  );
  assert (v_result->>'success')::boolean, 'service actor bridge creates scan request';
  v_request := (v_result->'data'->>'document_scan_request_id')::uuid;
  assert exists(
    select 1 from public.document_scan_requests where document_scan_request_id=v_request
  ), 'scan request persists only through protected service path';
end $$;
rollback;
