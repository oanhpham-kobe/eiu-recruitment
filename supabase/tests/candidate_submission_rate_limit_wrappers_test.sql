-- TASK-S08-002 Candidate Submit/Update wrapper regression.
-- Run on a disposable local DB after full migration replay.
\set ON_ERROR_STOP on

begin;

do $$
declare
  v_actor uuid := '00000000-0000-0000-0000-000000008002'::uuid;
  v_result jsonb;
  v_before bigint;
  v_after bigint;
begin
  -- Browser roles cannot bypass the wrapper through legacy mutation RPCs.
  assert not pg_catalog.has_function_privilege(
    'authenticated',
    'public.submit_candidate_submission(uuid,text,text,date,text,text,jsonb,text,uuid)',
    'EXECUTE'
  ), 'authenticated must not execute legacy submit RPC';
  assert not pg_catalog.has_function_privilege(
    'authenticated',
    'public.update_candidate_submission(uuid,text,text,date,text,text,jsonb,text,uuid)',
    'EXECUTE'
  ), 'authenticated must not execute legacy update RPC';

  assert pg_catalog.has_function_privilege(
    'service_role',
    'public.submit_candidate_submission(uuid,text,text,date,text,text,jsonb,text,uuid)',
    'EXECUTE'
  ), 'service_role must retain inner submit RPC execution';
  assert pg_catalog.has_function_privilege(
    'service_role',
    'public.update_candidate_submission(uuid,text,text,date,text,text,jsonb,text,uuid)',
    'EXECUTE'
  ), 'service_role must retain inner update RPC execution';

  -- New wrapper itself is service-only, so a browser cannot choose arbitrary
  -- opaque principal digests or quota buckets.
  assert not pg_catalog.has_function_privilege(
    'authenticated',
    'public.submit_candidate_submission_rate_limited(uuid,text,text,uuid,text,text,date,text,text,jsonb,text,uuid)',
    'EXECUTE'
  ), 'authenticated must not execute submit limiter wrapper';
  assert not pg_catalog.has_function_privilege(
    'authenticated',
    'public.update_candidate_submission_rate_limited(uuid,text,uuid,text,text,date,text,text,jsonb,text,uuid)',
    'EXECUTE'
  ), 'authenticated must not execute update limiter wrapper';
  assert pg_catalog.has_function_privilege(
    'service_role',
    'public.submit_candidate_submission_rate_limited(uuid,text,text,uuid,text,text,date,text,text,jsonb,text,uuid)',
    'EXECUTE'
  ), 'service_role must execute submit limiter wrapper';
  assert pg_catalog.has_function_privilege(
    'service_role',
    'public.update_candidate_submission_rate_limited(uuid,text,uuid,text,text,date,text,text,jsonb,text,uuid)',
    'EXECUTE'
  ), 'service_role must execute update limiter wrapper';

  -- The transaction-local handoff used by wrappers is the same source consumed
  -- by auth.uid(); prove it works on the actual local Supabase auth schema.
  perform pg_catalog.set_config('request.jwt.claim.sub', v_actor::text, true);
  assert auth.uid() = v_actor,
    'transaction-local request.jwt.claim.sub must drive auth.uid()';
  perform pg_catalog.set_config('request.jwt.claim.sub', '', true);

  -- Actor verification precedes quota consumption. An arbitrary service-role
  -- caller cannot burn a candidate quota for a non-candidate auth UUID.
  select pg_catalog.count(*) into v_before
  from private.rate_limit_buckets;

  v_result := public.submit_candidate_submission_rate_limited(
    p_actor_auth_user_id => v_actor,
    p_candidate_key_digest => pg_catalog.repeat('a', 64),
    p_trusted_ip_key_digest => pg_catalog.repeat('b', 64),
    p_candidate_form_session_id => '00000000-0000-0000-0000-000000008003'::uuid,
    p_full_name => 'Rate Limit Test'
  );
  assert v_result->>'error_code' = 'UNAUTHENTICATED',
    'non-candidate actor must fail before limiter/mutation';

  select pg_catalog.count(*) into v_after
  from private.rate_limit_buckets;
  assert v_after = v_before,
    'unauthorized actor must not debit any limiter bucket';

  -- Fixed policies must live inside the DB wrapper, not arrive as client args.
  assert pg_catalog.pg_get_functiondef(
    'public.submit_candidate_submission_rate_limited(uuid,text,text,uuid,text,text,date,text,text,jsonb,text,uuid)'::regprocedure
  ) like '%''CANDIDATE_SUBMIT''%',
    'submit wrapper must bind canonical policy code';
  assert pg_catalog.pg_get_functiondef(
    'public.submit_candidate_submission_rate_limited(uuid,text,text,uuid,text,text,date,text,text,jsonb,text,uuid)'::regprocedure
  ) like '%''limit'', 5%',
    'submit wrapper must bind 5/hour limit';
  assert pg_catalog.pg_get_functiondef(
    'public.update_candidate_submission_rate_limited(uuid,text,uuid,text,text,date,text,text,jsonb,text,uuid)'::regprocedure
  ) like '%''limit'', 30%',
    'update wrapper must bind 30/15m limit';
end;
$$;

rollback;
