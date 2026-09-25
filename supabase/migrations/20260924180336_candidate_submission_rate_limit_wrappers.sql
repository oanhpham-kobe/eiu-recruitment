-- TASK-S08-002 — Candidate Submit/Update durable rate-limit wrappers.
-- Browser roles lose direct EXECUTE on the legacy mutation RPCs. The server
-- calls these narrow service-role-only wrappers with server-derived opaque
-- principal digests; policy limits/windows are fixed here, never client-supplied.

revoke execute on function public.submit_candidate_submission(
  uuid, text, text, date, text, text, jsonb, text, uuid
) from public, anon, authenticated;
grant execute on function public.submit_candidate_submission(
  uuid, text, text, date, text, text, jsonb, text, uuid
) to postgres, service_role;

revoke execute on function public.update_candidate_submission(
  uuid, text, text, date, text, text, jsonb, text, uuid
) from public, anon, authenticated;
grant execute on function public.update_candidate_submission(
  uuid, text, text, date, text, text, jsonb, text, uuid
) to postgres, service_role;

create or replace function public.submit_candidate_submission_rate_limited(
  p_actor_auth_user_id uuid,
  p_candidate_key_digest text,
  p_trusted_ip_key_digest text,
  p_candidate_form_session_id uuid,
  p_full_name text,
  p_phone text default null,
  p_date_of_birth date default null,
  p_gender text default null,
  p_address text default null,
  p_education jsonb default '[]'::jsonb,
  p_privacy_notice_version text default null,
  p_idempotency_key uuid default gen_random_uuid()
)
returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
  v_candidate record;
  v_limit jsonb;
  v_previous_sub text;
  v_result jsonb;
begin
  select c.candidate_id, c.is_active
    into v_candidate
  from public.candidates c
  where c.auth_user_id = p_actor_auth_user_id;

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

  if coalesce(p_candidate_key_digest, '') !~ '^[0-9a-f]{64}$'
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
      'CANDIDATE_SUBMIT',
      pg_catalog.jsonb_build_array(
        pg_catalog.jsonb_build_object(
          'ruleCode', 'CANDIDATE_1H',
          'keyDigest', p_candidate_key_digest,
          'limit', 5,
          'windowSeconds', 3600
        ),
        pg_catalog.jsonb_build_object(
          'ruleCode', 'CANDIDATE_1D',
          'keyDigest', p_candidate_key_digest,
          'limit', 20,
          'windowSeconds', 86400
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
      'message', 'Too many submission attempts. Please retry later.',
      'data', pg_catalog.jsonb_build_object(
        'retry_after_seconds', coalesce((v_limit->>'retryAfterSeconds')::integer, 1)
      )
    );
  end if;

  v_previous_sub := pg_catalog.current_setting('request.jwt.claim.sub', true);
  perform pg_catalog.set_config('request.jwt.claim.sub', p_actor_auth_user_id::text, true);

  v_result := public.submit_candidate_submission(
    p_candidate_form_session_id => p_candidate_form_session_id,
    p_full_name => p_full_name,
    p_phone => p_phone,
    p_date_of_birth => p_date_of_birth,
    p_gender => p_gender,
    p_address => p_address,
    p_education => p_education,
    p_privacy_notice_version => p_privacy_notice_version,
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

revoke all on function public.submit_candidate_submission_rate_limited(
  uuid, text, text, uuid, text, text, date, text, text, jsonb, text, uuid
) from public, anon, authenticated;
grant execute on function public.submit_candidate_submission_rate_limited(
  uuid, text, text, uuid, text, text, date, text, text, jsonb, text, uuid
) to postgres, service_role;

create or replace function public.update_candidate_submission_rate_limited(
  p_actor_auth_user_id uuid,
  p_candidate_ip_key_digest text,
  p_candidate_form_session_id uuid,
  p_full_name text,
  p_phone text default null,
  p_date_of_birth date default null,
  p_gender text default null,
  p_address text default null,
  p_education jsonb default '[]'::jsonb,
  p_privacy_notice_version text default null,
  p_idempotency_key uuid default gen_random_uuid()
)
returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
  v_candidate record;
  v_limit jsonb;
  v_previous_sub text;
  v_result jsonb;
begin
  select c.candidate_id, c.is_active
    into v_candidate
  from public.candidates c
  where c.auth_user_id = p_actor_auth_user_id;

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

  if coalesce(p_candidate_ip_key_digest, '') !~ '^[0-9a-f]{64}$' then
    return pg_catalog.jsonb_build_object(
      'success', false,
      'error_code', 'RATE_LIMIT_UNAVAILABLE',
      'message', 'Request protection context is unavailable'
    );
  end if;

  begin
    v_limit := public.consume_rate_limit_rules(
      'CANDIDATE_UPDATE',
      pg_catalog.jsonb_build_array(
        pg_catalog.jsonb_build_object(
          'ruleCode', 'CANDIDATE_IP_15M',
          'keyDigest', p_candidate_ip_key_digest,
          'limit', 30,
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
      'message', 'Too many update attempts. Please retry later.',
      'data', pg_catalog.jsonb_build_object(
        'retry_after_seconds', coalesce((v_limit->>'retryAfterSeconds')::integer, 1)
      )
    );
  end if;

  v_previous_sub := pg_catalog.current_setting('request.jwt.claim.sub', true);
  perform pg_catalog.set_config('request.jwt.claim.sub', p_actor_auth_user_id::text, true);

  v_result := public.update_candidate_submission(
    p_candidate_form_session_id => p_candidate_form_session_id,
    p_full_name => p_full_name,
    p_phone => p_phone,
    p_date_of_birth => p_date_of_birth,
    p_gender => p_gender,
    p_address => p_address,
    p_education => p_education,
    p_privacy_notice_version => p_privacy_notice_version,
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

revoke all on function public.update_candidate_submission_rate_limited(
  uuid, text, uuid, text, text, date, text, text, jsonb, text, uuid
) from public, anon, authenticated;
grant execute on function public.update_candidate_submission_rate_limited(
  uuid, text, uuid, text, text, date, text, text, jsonb, text, uuid
) to postgres, service_role;

comment on function public.submit_candidate_submission_rate_limited(
  uuid, text, text, uuid, text, text, date, text, text, jsonb, text, uuid
) is 'S08-002 service-only Candidate Submit wrapper. Enforces 5/hour and 20/day Candidate-wide quota before authoritative mutation.';
comment on function public.update_candidate_submission_rate_limited(
  uuid, text, uuid, text, text, date, text, text, jsonb, text, uuid
) is 'S08-002 service-only Candidate Update wrapper. Enforces 30/15m candidate+trusted-IP quota before authoritative mutation.';
