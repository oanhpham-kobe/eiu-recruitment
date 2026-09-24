-- TASK-S08-002 focused durable limiter foundation regression.
-- Run only against an unlinked disposable local Supabase database after replay.
\set ON_ERROR_STOP on

begin;

delete from private.rate_limit_buckets;

-- Private state and narrow service-only EXECUTE are mandatory. Browser roles
-- must not be able to choose arbitrary principals or mutate limiter state.
do $$
declare
  v_rls boolean;
begin
  select c.relrowsecurity
    into v_rls
  from pg_catalog.pg_class c
  join pg_catalog.pg_namespace n on n.oid = c.relnamespace
  where n.nspname = 'private'
    and c.relname = 'rate_limit_buckets';

  assert v_rls is true, 'rate_limit_buckets must have RLS enabled';
  assert not pg_catalog.has_table_privilege(
    'anon', 'private.rate_limit_buckets', 'SELECT'
  ), 'anon must not read limiter state';
  assert not pg_catalog.has_table_privilege(
    'authenticated', 'private.rate_limit_buckets', 'SELECT'
  ), 'authenticated must not read limiter state';
  assert not pg_catalog.has_function_privilege(
    'anon',
    'public.consume_rate_limit_rules(text,jsonb,timestamptz)',
    'EXECUTE'
  ), 'anon must not execute the limiter';
  assert not pg_catalog.has_function_privilege(
    'authenticated',
    'public.consume_rate_limit_rules(text,jsonb,timestamptz)',
    'EXECUTE'
  ), 'authenticated must not execute the limiter';
  assert pg_catalog.has_function_privilege(
    'service_role',
    'public.consume_rate_limit_rules(text,jsonb,timestamptz)',
    'EXECUTE'
  ), 'service_role must execute the narrow limiter RPC';
end;
$$;

-- Fixed-window threshold, stable Retry-After and no overshoot.
do $$
declare
  v_rules jsonb := pg_catalog.jsonb_build_array(
    pg_catalog.jsonb_build_object(
      'ruleCode', 'EMAIL_15M',
      'keyDigest', pg_catalog.repeat('a', 64),
      'limit', 2,
      'windowSeconds', 900
    )
  );
  v_result jsonb;
  v_count integer;
begin
  v_result := public.consume_rate_limit_rules(
    'CANDIDATE_OTP_REQUEST', v_rules, '2026-09-24 12:00:00+00'
  );
  assert (v_result->>'allowed')::boolean,
    'first request must be allowed';

  v_result := public.consume_rate_limit_rules(
    'CANDIDATE_OTP_REQUEST', v_rules, '2026-09-24 12:00:01+00'
  );
  assert (v_result->>'allowed')::boolean,
    'second request at limit must be allowed';

  v_result := public.consume_rate_limit_rules(
    'CANDIDATE_OTP_REQUEST', v_rules, '2026-09-24 12:00:02+00'
  );
  assert not (v_result->>'allowed')::boolean,
    'request above threshold must be blocked';
  assert (v_result->>'retryAfterSeconds')::integer = 898,
    'Retry-After must derive from authoritative window expiry';

  select request_count into v_count
  from private.rate_limit_buckets
  where policy_code = 'CANDIDATE_OTP_REQUEST'
    and rule_code = 'EMAIL_15M'
    and key_digest = pg_catalog.repeat('a', 64);
  assert v_count = 2, 'blocked request must not overshoot counter';
end;
$$;

-- Independent principals must not share a bucket.
do $$
declare
  v_a jsonb := pg_catalog.jsonb_build_array(
    pg_catalog.jsonb_build_object(
      'ruleCode', 'IP_15M',
      'keyDigest', pg_catalog.repeat('b', 64),
      'limit', 1,
      'windowSeconds', 900
    )
  );
  v_b jsonb := pg_catalog.jsonb_build_array(
    pg_catalog.jsonb_build_object(
      'ruleCode', 'IP_15M',
      'keyDigest', pg_catalog.repeat('c', 64),
      'limit', 1,
      'windowSeconds', 900
    )
  );
begin
  assert (
    public.consume_rate_limit_rules(
      'UPLOAD', v_a, '2026-09-24 12:00:00+00'
    )->>'allowed'
  )::boolean, 'first IP must be allowed';

  assert not (
    public.consume_rate_limit_rules(
      'UPLOAD', v_a, '2026-09-24 12:00:01+00'
    )->>'allowed'
  )::boolean, 'same IP must be blocked at its limit';

  assert (
    public.consume_rate_limit_rules(
      'UPLOAD', v_b, '2026-09-24 12:00:01+00'
    )->>'allowed'
  )::boolean, 'different IP digest must have an independent bucket';
end;
$$;

-- Multi-rule decision is all-or-nothing: when one mandatory rule blocks, an
-- otherwise-allowable peer rule is not debited.
do $$
declare
  v_block_only jsonb := pg_catalog.jsonb_build_array(
    pg_catalog.jsonb_build_object(
      'ruleCode', 'BLOCKER',
      'keyDigest', pg_catalog.repeat('d', 64),
      'limit', 1,
      'windowSeconds', 60
    )
  );
  v_combined jsonb := pg_catalog.jsonb_build_array(
    pg_catalog.jsonb_build_object(
      'ruleCode', 'BLOCKER',
      'keyDigest', pg_catalog.repeat('d', 64),
      'limit', 1,
      'windowSeconds', 60
    ),
    pg_catalog.jsonb_build_object(
      'ruleCode', 'PEER',
      'keyDigest', pg_catalog.repeat('e', 64),
      'limit', 5,
      'windowSeconds', 60
    )
  );
  v_result jsonb;
  v_peer_count bigint;
begin
  perform public.consume_rate_limit_rules(
    'ATOMIC_TEST', v_block_only, '2026-09-24 12:00:00+00'
  );

  v_result := public.consume_rate_limit_rules(
    'ATOMIC_TEST', v_combined, '2026-09-24 12:00:01+00'
  );
  assert not (v_result->>'allowed')::boolean,
    'combined request must block when one mandatory rule is exhausted';

  select pg_catalog.count(*) into v_peer_count
  from private.rate_limit_buckets
  where policy_code = 'ATOMIC_TEST'
    and rule_code = 'PEER'
    and key_digest = pg_catalog.repeat('e', 64);
  assert v_peer_count = 0,
    'blocked multi-rule request must not partially debit peer quota';
end;
$$;

-- Window rollover reuses the same principal row instead of appending an
-- unbounded row per window.
do $$
declare
  v_rules jsonb := pg_catalog.jsonb_build_array(
    pg_catalog.jsonb_build_object(
      'ruleCode', 'ACTOR_1M',
      'keyDigest', pg_catalog.repeat('f', 64),
      'limit', 1,
      'windowSeconds', 60
    )
  );
  v_rows bigint;
  v_count integer;
begin
  assert (
    public.consume_rate_limit_rules(
      'INTERNAL_SEARCH', v_rules, '2026-09-24 12:00:00+00'
    )->>'allowed'
  )::boolean, 'first minute request must be allowed';

  assert not (
    public.consume_rate_limit_rules(
      'INTERNAL_SEARCH', v_rules, '2026-09-24 12:00:30+00'
    )->>'allowed'
  )::boolean, 'same minute must remain blocked';

  assert (
    public.consume_rate_limit_rules(
      'INTERNAL_SEARCH', v_rules, '2026-09-24 12:01:00+00'
    )->>'allowed'
  )::boolean, 'next fixed window must reset quota';

  select pg_catalog.count(*), pg_catalog.max(request_count)
    into v_rows, v_count
  from private.rate_limit_buckets
  where policy_code = 'INTERNAL_SEARCH'
    and rule_code = 'ACTOR_1M'
    and key_digest = pg_catalog.repeat('f', 64);
  assert v_rows = 1, 'window rollover must reuse one row per principal/rule';
  assert v_count = 1, 'rolled-over reusable row must reset count to one';
end;
$$;

-- Allowed requests perform bounded opportunistic cleanup of idle expired rows.
do $$
declare
  v_rules jsonb := pg_catalog.jsonb_build_array(
    pg_catalog.jsonb_build_object(
      'ruleCode', 'CLEANUP_TRIGGER',
      'keyDigest', pg_catalog.repeat('1', 64),
      'limit', 5,
      'windowSeconds', 60
    )
  );
  v_stale bigint;
begin
  insert into private.rate_limit_buckets (
    policy_code, rule_code, key_digest, window_seconds,
    window_started_at, request_count, expires_at, updated_at
  ) values (
    'STALE_TEST', 'STALE', pg_catalog.repeat('2', 64), 60,
    '2026-09-24 10:00:00+00', 1,
    '2026-09-24 10:01:00+00', '2026-09-24 10:00:00+00'
  );

  perform public.consume_rate_limit_rules(
    'CLEANUP_TEST', v_rules, '2026-09-24 12:00:00+00'
  );

  select pg_catalog.count(*) into v_stale
  from private.rate_limit_buckets
  where policy_code = 'STALE_TEST';
  assert v_stale = 0, 'expired idle row must be cleanup-eligible';
end;
$$;

rollback;
