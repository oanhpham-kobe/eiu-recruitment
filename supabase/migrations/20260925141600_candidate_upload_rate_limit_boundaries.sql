-- TASK-S08-002 — Candidate upload durable rate-limit boundaries.
-- User-initiated reserve and completion/staging share one aggregate UPLOAD
-- quota: 30/15m per authenticated Candidate identity and 100/15m per trusted IP.
-- Browser roles cannot bypass the quota by invoking legacy mutation RPCs.

revoke execute on function public.reserve_candidate_form_upload(
  uuid, uuid, text, text, bigint, uuid
) from public, anon, authenticated;
grant execute on function public.reserve_candidate_form_upload(
  uuid, uuid, text, text, bigint, uuid
) to postgres, service_role;

revoke execute on function public.record_candidate_upload_completed(
  uuid, bigint, text
) from public, anon, authenticated;
grant execute on function public.record_candidate_upload_completed(
  uuid, bigint, text
) to postgres, service_role;

revoke execute on function public.request_candidate_document_scan(
  uuid, uuid, text, uuid
) from public, anon, authenticated;
grant execute on function public.request_candidate_document_scan(
  uuid, uuid, text, uuid
) to postgres, service_role;

create or replace function public.reserve_candidate_form_upload_rate_limited(
  p_actor_auth_user_id uuid,
  p_identity_key_digest text,
  p_trusted_ip_key_digest text,
  p_candidate_form_session_id uuid,
  p_intended_document_type_id uuid,
  p_original_filename text,
  p_declared_mime_type text default null,
  p_expected_max_size_bytes bigint default 5242880,
  p_idempotency_key uuid default gen_random_uuid()
)
returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
  v_candidate public.candidates%rowtype;
  v_limit jsonb;
  v_previous_sub text;
  v_result jsonb;
begin
  select * into v_candidate
  from public.candidates
  where auth_user_id = p_actor_auth_user_id;

  if not found then
    return pg_catalog.jsonb_build_object(
      'success', false,
      'error_code', 'UNAUTHENTICATED',
      'message', 'Candidate authentication required'
    );
  end if;
  if not v_candidate.is_active then
    return pg_catalog.jsonb_build_object(
      'success', false,
      'error_code', 'USER_INACTIVE',
      'message', 'Candidate account is inactive'
    );
  end if;

  if coalesce(p_identity_key_digest, '') !~ '^[0-9a-f]{64}$'
    or coalesce(p_trusted_ip_key_digest, '') !~ '^[0-9a-f]{64}$'
  then
    return pg_catalog.jsonb_build_object(
      'success', false,
      'error_code', 'RATE_LIMIT_UNAVAILABLE',
      'message', 'Request protection context is unavailable'
    );
  end if;

  begin
    v_limit := public.consume_rate_limit_rules(
      'UPLOAD',
      pg_catalog.jsonb_build_array(
        pg_catalog.jsonb_build_object(
          'ruleCode', 'IDENTITY_15M',
          'keyDigest', p_identity_key_digest,
          'limit', 30,
          'windowSeconds', 900
        ),
        pg_catalog.jsonb_build_object(
          'ruleCode', 'IP_15M',
          'keyDigest', p_trusted_ip_key_digest,
          'limit', 100,
          'windowSeconds', 900
        )
      )
    );
  exception when others then
    return pg_catalog.jsonb_build_object(
      'success', false,
      'error_code', 'RATE_LIMIT_UNAVAILABLE',
      'message', 'Request protection is temporarily unavailable'
    );
  end;

  if coalesce((v_limit->>'allowed')::boolean, false) is not true then
    return pg_catalog.jsonb_build_object(
      'success', false,
      'error_code', 'RATE_LIMITED',
      'message', 'Too many upload requests. Please retry later.',
      'data', pg_catalog.jsonb_build_object(
        'retry_after_seconds', coalesce((v_limit->>'retryAfterSeconds')::integer, 1)
      )
    );
  end if;

  v_previous_sub := pg_catalog.current_setting('request.jwt.claim.sub', true);
  perform pg_catalog.set_config('request.jwt.claim.sub', p_actor_auth_user_id::text, true);

  v_result := public.reserve_candidate_form_upload(
    p_candidate_form_session_id => p_candidate_form_session_id,
    p_intended_document_type_id => p_intended_document_type_id,
    p_original_filename => p_original_filename,
    p_declared_mime_type => p_declared_mime_type,
    p_expected_max_size_bytes => p_expected_max_size_bytes,
    p_idempotency_key => p_idempotency_key
  );

  perform pg_catalog.set_config(
    'request.jwt.claim.sub',
    coalesce(v_previous_sub, ''),
    true
  );
  return v_result;
end;
$$;

revoke all on function public.reserve_candidate_form_upload_rate_limited(
  uuid, text, text, uuid, uuid, text, text, bigint, uuid
) from public, anon, authenticated;
grant execute on function public.reserve_candidate_form_upload_rate_limited(
  uuid, text, text, uuid, uuid, text, text, bigint, uuid
) to postgres, service_role;

create or replace function public.authorize_candidate_upload_completion_rate_limited(
  p_actor_auth_user_id uuid,
  p_identity_key_digest text,
  p_trusted_ip_key_digest text,
  p_candidate_form_session_id uuid,
  p_upload_reservation_id uuid
)
returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
  v_candidate public.candidates%rowtype;
  v_session public.candidate_form_sessions%rowtype;
  v_submission public.submissions%rowtype;
  v_reservation public.upload_reservations%rowtype;
  v_limit jsonb;
begin
  select * into v_candidate
  from public.candidates
  where auth_user_id = p_actor_auth_user_id;

  if not found then
    return pg_catalog.jsonb_build_object(
      'success', false,
      'error_code', 'UNAUTHENTICATED',
      'message', 'Candidate authentication required'
    );
  end if;
  if not v_candidate.is_active then
    return pg_catalog.jsonb_build_object(
      'success', false,
      'error_code', 'USER_INACTIVE',
      'message', 'Candidate account is inactive'
    );
  end if;

  select * into v_session
  from public.candidate_form_sessions
  where candidate_form_session_id = p_candidate_form_session_id
    and candidate_id = v_candidate.candidate_id
  for update;

  if not found then
    return pg_catalog.jsonb_build_object(
      'success', false,
      'error_code', 'NOT_FOUND',
      'message', 'Candidate form session not found or access denied'
    );
  end if;
  if v_session.status_code <> 'OPEN' then
    return pg_catalog.jsonb_build_object(
      'success', false,
      'error_code', 'INVALID_STATE',
      'message', 'Candidate form session is not open'
    );
  end if;
  if v_session.expires_at <= pg_catalog.clock_timestamp() then
    return pg_catalog.jsonb_build_object(
      'success', false,
      'error_code', 'FORM_SESSION_EXPIRED',
      'message', 'Candidate form session has expired'
    );
  end if;

  if v_session.mode_code = 'EDIT_SUBMISSION' then
    select * into v_submission
    from public.submissions
    where submission_id = v_session.target_submission_id
      and candidate_id = v_candidate.candidate_id
    for update;
    if not found or v_submission.status_code <> 'NEW' then
      return pg_catalog.jsonb_build_object(
        'success', false,
        'error_code', 'INVALID_STATE',
        'message', 'Target submission is no longer editable'
      );
    end if;
  end if;

  select * into v_reservation
  from public.upload_reservations
  where upload_reservation_id = p_upload_reservation_id
    and candidate_form_session_id = p_candidate_form_session_id
    and actor_auth_user_id = p_actor_auth_user_id
  for update;

  if not found then
    return pg_catalog.jsonb_build_object(
      'success', false,
      'error_code', 'NOT_FOUND',
      'message', 'Upload reservation not found or access denied'
    );
  end if;
  if v_reservation.status_code <> 'RESERVED' then
    return pg_catalog.jsonb_build_object(
      'success', false,
      'error_code', 'INVALID_STATE',
      'message', 'Upload reservation is not in reserved status'
    );
  end if;
  if v_reservation.expires_at <= pg_catalog.clock_timestamp() then
    return pg_catalog.jsonb_build_object(
      'success', false,
      'error_code', 'UPLOAD_RESERVATION_EXPIRED',
      'message', 'Upload reservation has expired'
    );
  end if;

  if coalesce(p_identity_key_digest, '') !~ '^[0-9a-f]{64}$'
    or coalesce(p_trusted_ip_key_digest, '') !~ '^[0-9a-f]{64}$'
  then
    return pg_catalog.jsonb_build_object(
      'success', false,
      'error_code', 'RATE_LIMIT_UNAVAILABLE',
      'message', 'Request protection context is unavailable'
    );
  end if;

  begin
    v_limit := public.consume_rate_limit_rules(
      'UPLOAD',
      pg_catalog.jsonb_build_array(
        pg_catalog.jsonb_build_object(
          'ruleCode', 'IDENTITY_15M',
          'keyDigest', p_identity_key_digest,
          'limit', 30,
          'windowSeconds', 900
        ),
        pg_catalog.jsonb_build_object(
          'ruleCode', 'IP_15M',
          'keyDigest', p_trusted_ip_key_digest,
          'limit', 100,
          'windowSeconds', 900
        )
      )
    );
  exception when others then
    return pg_catalog.jsonb_build_object(
      'success', false,
      'error_code', 'RATE_LIMIT_UNAVAILABLE',
      'message', 'Request protection is temporarily unavailable'
    );
  end;

  if coalesce((v_limit->>'allowed')::boolean, false) is not true then
    return pg_catalog.jsonb_build_object(
      'success', false,
      'error_code', 'RATE_LIMITED',
      'message', 'Too many upload requests. Please retry later.',
      'data', pg_catalog.jsonb_build_object(
        'retry_after_seconds', coalesce((v_limit->>'retryAfterSeconds')::integer, 1)
      )
    );
  end if;

  return pg_catalog.jsonb_build_object(
    'success', true,
    'data', pg_catalog.jsonb_build_object(
      'candidate_id', v_candidate.candidate_id,
      'candidate_form_session_id', p_candidate_form_session_id,
      'upload_reservation_id', p_upload_reservation_id
    )
  );
end;
$$;

revoke all on function public.authorize_candidate_upload_completion_rate_limited(
  uuid, text, text, uuid, uuid
) from public, anon, authenticated;
grant execute on function public.authorize_candidate_upload_completion_rate_limited(
  uuid, text, text, uuid, uuid
) to postgres, service_role;

create or replace function public.request_candidate_document_scan_as_actor(
  p_actor_auth_user_id uuid,
  p_candidate_form_session_id uuid,
  p_upload_reservation_id uuid,
  p_action_code text,
  p_target_logical_document_id uuid default null
)
returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
  v_candidate public.candidates%rowtype;
  v_previous_sub text;
  v_result jsonb;
begin
  select * into v_candidate
  from public.candidates
  where auth_user_id = p_actor_auth_user_id;

  if not found then
    return pg_catalog.jsonb_build_object(
      'success', false,
      'error_code', 'UNAUTHENTICATED',
      'message', 'Candidate authentication required'
    );
  end if;
  if not v_candidate.is_active then
    return pg_catalog.jsonb_build_object(
      'success', false,
      'error_code', 'USER_INACTIVE',
      'message', 'Candidate account is inactive'
    );
  end if;

  v_previous_sub := pg_catalog.current_setting('request.jwt.claim.sub', true);
  perform pg_catalog.set_config('request.jwt.claim.sub', p_actor_auth_user_id::text, true);
  v_result := public.request_candidate_document_scan(
    p_candidate_form_session_id => p_candidate_form_session_id,
    p_upload_reservation_id => p_upload_reservation_id,
    p_action_code => p_action_code,
    p_target_logical_document_id => p_target_logical_document_id
  );
  perform pg_catalog.set_config(
    'request.jwt.claim.sub',
    coalesce(v_previous_sub, ''),
    true
  );
  return v_result;
end;
$$;

revoke all on function public.request_candidate_document_scan_as_actor(
  uuid, uuid, uuid, text, uuid
) from public, anon, authenticated;
grant execute on function public.request_candidate_document_scan_as_actor(
  uuid, uuid, uuid, text, uuid
) to postgres, service_role;

comment on function public.reserve_candidate_form_upload_rate_limited(
  uuid, text, text, uuid, uuid, text, text, bigint, uuid
) is 'S08-002 service-only Candidate upload reservation wrapper. Consumes shared UPLOAD identity+trusted-IP quota before reservation mutation.';
comment on function public.authorize_candidate_upload_completion_rate_limited(
  uuid, text, text, uuid, uuid
) is 'S08-002 service-only completion authorization gate. Validates Candidate/session/reservation then consumes shared UPLOAD quota before Storage inspection or scan-request mutation.';
comment on function public.request_candidate_document_scan_as_actor(
  uuid, uuid, uuid, text, uuid
) is 'S08-002 service-only actor-bound bridge to the accepted document-scan request RPC after upload completion quota has passed.';
