-- TASK-S08-002 focused Internal Search limiter helper regression.
-- Run only against an unlinked disposable local Supabase database after replay.
\set ON_ERROR_STOP on

begin;

delete from private.rate_limit_buckets
where policy_code = 'INTERNAL_SEARCH';

-- Browser roles must not be able to choose a principal, a fake evaluation time,
-- or call this SECURITY DEFINER helper directly.
do $$
begin
  assert not pg_catalog.has_function_privilege(
    'anon',
    'private.consume_internal_search_rate_limit(text,timestamptz)',
    'EXECUTE'
  ), 'anon must not execute the Internal Search limiter helper';
  assert not pg_catalog.has_function_privilege(
    'authenticated',
    'private.consume_internal_search_rate_limit(text,timestamptz)',
    'EXECUTE'
  ), 'authenticated must not execute the Internal Search limiter helper';
  assert pg_catalog.has_function_privilege(
    'service_role',
    'private.consume_internal_search_rate_limit(text,timestamptz)',
    'EXECUTE'
  ), 'service_role must execute the trusted Internal Search limiter helper';
end;
$$;

-- Dedicated deterministic internal actor fixtures.
insert into public.app_users(
  app_user_id,
  auth_user_id,
  email,
  full_name,
  is_active,
  is_root_admin
) values
  (
    '81111111-1111-1111-1111-111111111111',
    '82111111-1111-1111-1111-111111111111',
    's08_search_actor_a@eiu.edu.vn',
    'S08 Search Actor A',
    true,
    false
  ),
  (
    '81111111-2222-2222-2222-222222222222',
    '82111111-2222-2222-2222-222222222222',
    's08_search_actor_b@eiu.edu.vn',
    'S08 Search Actor B',
    true,
    false
  );

-- Empty and whitespace-only search is free and creates no limiter state.
do $$
declare
  v_result jsonb;
  v_rows bigint;
begin
  perform pg_catalog.set_config('request.jwt.claim.sub', '', true);

  v_result := private.consume_internal_search_rate_limit(
    '   ',
    '2026-09-26 12:00:00+00'
  );
  assert (v_result->>'allowed')::boolean,
    'whitespace-only Internal Search must remain allowed';

  select pg_catalog.count(*) into v_rows
  from private.rate_limit_buckets
  where policy_code = 'INTERNAL_SEARCH';
  assert v_rows = 0,
    'whitespace-only Internal Search must not create/debit a bucket';
end;
$$;

-- A non-empty query derives the principal from the active app_user_id, not from
-- search text or a client-supplied identifier. Different query strings by the
-- same actor must share one ACTOR_1M bucket.
do $$
declare
  v_result jsonb;
  v_digest text;
  v_count integer;
begin
  perform pg_catalog.set_config(
    'request.jwt.claim.sub',
    '82111111-1111-1111-1111-111111111111',
    true
  );

  v_result := private.consume_internal_search_rate_limit(
    '  Nguyen Van A  ',
    '2026-09-26 12:00:00+00'
  );
  assert (v_result->>'allowed')::boolean,
    'first non-empty Internal Search must be allowed';

  select b.key_digest, b.request_count
    into v_digest, v_count
  from private.rate_limit_buckets b
  where b.policy_code = 'INTERNAL_SEARCH'
    and b.rule_code = 'ACTOR_1M';

  assert v_digest =
    '83c0fccdc8a2e3180ca07a35f36230a1b3294e16b45bff5b66fb8a1afe24971d',
    'SQL actor digest must match the canonical Node SHA-256 principal digest';
  assert v_count = 1,
    'first non-empty Internal Search must debit exactly once';

  v_result := private.consume_internal_search_rate_limit(
    'different search text',
    '2026-09-26 12:00:01+00'
  );
  assert (v_result->>'allowed')::boolean,
    'second query by same actor must still be allowed';

  select b.request_count into v_count
  from private.rate_limit_buckets b
  where b.policy_code = 'INTERNAL_SEARCH'
    and b.rule_code = 'ACTOR_1M'
    and b.key_digest =
      '83c0fccdc8a2e3180ca07a35f36230a1b3294e16b45bff5b66fb8a1afe24971d';
  assert v_count = 2,
    'different search text must share the same actor-wide bucket';

  perform private.consume_internal_search_rate_limit(
    E' \t ',
    '2026-09-26 12:00:02+00'
  );
  select b.request_count into v_count
  from private.rate_limit_buckets b
  where b.policy_code = 'INTERNAL_SEARCH'
    and b.rule_code = 'ACTOR_1M'
    and b.key_digest =
      '83c0fccdc8a2e3180ca07a35f36230a1b3294e16b45bff5b66fb8a1afe24971d';
  assert v_count = 2,
    'whitespace-only search must not debit an existing actor bucket';
end;
$$;

-- The canonical threshold is exactly 120 actor requests in a 60-second fixed
-- window. The blocked request must not overshoot the durable count.
do $$
declare
  v_i integer;
  v_result jsonb;
  v_count integer;
begin
  perform pg_catalog.set_config(
    'request.jwt.claim.sub',
    '82111111-1111-1111-1111-111111111111',
    true
  );

  for v_i in 3..120 loop
    v_result := private.consume_internal_search_rate_limit(
      'threshold fill',
      '2026-09-26 12:00:10+00'
    );
    assert (v_result->>'allowed')::boolean,
      'requests through the 120th actor search must be allowed';
  end loop;

  v_result := private.consume_internal_search_rate_limit(
    'threshold blocked',
    '2026-09-26 12:00:30+00'
  );
  assert not (v_result->>'allowed')::boolean,
    '121st actor search in the same minute must be blocked';
  assert (v_result->>'retryAfterSeconds')::integer = 30,
    'blocked Internal Search must expose authoritative retry-after seconds';

  select b.request_count into v_count
  from private.rate_limit_buckets b
  where b.policy_code = 'INTERNAL_SEARCH'
    and b.rule_code = 'ACTOR_1M'
    and b.key_digest =
      '83c0fccdc8a2e3180ca07a35f36230a1b3294e16b45bff5b66fb8a1afe24971d';
  assert v_count = 120,
    'blocked Internal Search must not overshoot the durable bucket';
end;
$$;

-- A different active internal actor receives an independent bucket.
do $$
declare
  v_result jsonb;
  v_count integer;
begin
  perform pg_catalog.set_config(
    'request.jwt.claim.sub',
    '82111111-2222-2222-2222-222222222222',
    true
  );

  v_result := private.consume_internal_search_rate_limit(
    'independent actor',
    '2026-09-26 12:00:30+00'
  );
  assert (v_result->>'allowed')::boolean,
    'different internal actor must have independent search quota';

  select b.request_count into v_count
  from private.rate_limit_buckets b
  where b.policy_code = 'INTERNAL_SEARCH'
    and b.rule_code = 'ACTOR_1M'
    and b.key_digest =
      '83bd46e31fc7f825ae2b96b6e1aef06b861b4c37d1124140962faddf8c9997e9';
  assert v_count = 1,
    'different internal actor must use a separate durable bucket';
end;
$$;

-- Inactive/missing internal actor context fails closed for non-empty search and
-- must not create or increment quota state.
do $$
declare
  v_result jsonb;
  v_before integer;
  v_after integer;
begin
  select b.request_count into v_before
  from private.rate_limit_buckets b
  where b.policy_code = 'INTERNAL_SEARCH'
    and b.rule_code = 'ACTOR_1M'
    and b.key_digest =
      '83bd46e31fc7f825ae2b96b6e1aef06b861b4c37d1124140962faddf8c9997e9';

  update public.app_users
  set is_active = false
  where app_user_id = '81111111-2222-2222-2222-222222222222';

  perform pg_catalog.set_config(
    'request.jwt.claim.sub',
    '82111111-2222-2222-2222-222222222222',
    true
  );
  v_result := private.consume_internal_search_rate_limit(
    'must fail closed',
    '2026-09-26 12:00:31+00'
  );

  assert not (v_result->>'allowed')::boolean,
    'inactive internal actor must fail closed';
  assert v_result->>'errorCode' = 'RATE_LIMIT_UNAVAILABLE',
    'inactive actor must surface unavailable protection context';

  select b.request_count into v_after
  from private.rate_limit_buckets b
  where b.policy_code = 'INTERNAL_SEARCH'
    and b.rule_code = 'ACTOR_1M'
    and b.key_digest =
      '83bd46e31fc7f825ae2b96b6e1aef06b861b4c37d1124140962faddf8c9997e9';

  assert v_after = v_before,
    'failed-closed actor resolution must not consume quota';
end;
$$;

rollback;
