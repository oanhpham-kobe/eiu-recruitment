-- TASK-S08-002 — Durable Distributed Rate Limiting and Abuse Controls
-- Shared fixed-window primitive for multi-instance application enforcement.
--
-- Threat model: callers persist only opaque SHA-256 key digests. Digests are
-- pseudonymous enforcement material, not anonymization: low-entropy source
-- values such as email/IP may still be guessable by an infrastructure actor.
-- No production-only HMAC secret is introduced by this task.

-- -----------------------------------------------------------------------------
-- 1. Private reusable limiter state
-- -----------------------------------------------------------------------------

create table private.rate_limit_buckets (
  policy_code text not null,
  rule_code text not null,
  key_digest text not null,
  window_seconds integer not null,
  window_started_at timestamptz not null,
  request_count integer not null,
  expires_at timestamptz not null,
  updated_at timestamptz not null default pg_catalog.clock_timestamp(),
  constraint rate_limit_buckets_pk
    primary key (policy_code, rule_code, key_digest),
  constraint rate_limit_buckets_policy_code_ck
    check (policy_code ~ '^[A-Z0-9_]{1,64}$'),
  constraint rate_limit_buckets_rule_code_ck
    check (rule_code ~ '^[A-Z0-9_]{1,64}$'),
  constraint rate_limit_buckets_key_digest_ck
    check (key_digest ~ '^[0-9a-f]{64}$'),
  constraint rate_limit_buckets_window_seconds_ck
    check (window_seconds between 1 and 604800),
  constraint rate_limit_buckets_request_count_ck
    check (request_count >= 0),
  constraint rate_limit_buckets_expiry_ck
    check (expires_at > window_started_at)
);

create index rate_limit_buckets_expires_at_idx
  on private.rate_limit_buckets (expires_at);

alter table private.rate_limit_buckets enable row level security;

revoke all on table private.rate_limit_buckets from public, anon, authenticated;

comment on table private.rate_limit_buckets is
  'Private reusable S08-002 fixed-window limiter state. key_digest is pseudonymous SHA-256 enforcement material; raw email/IP/search text is forbidden.';

-- -----------------------------------------------------------------------------
-- 2. Atomic multi-rule consumption
-- -----------------------------------------------------------------------------

create or replace function public.consume_rate_limit_rules(
  p_policy_code text,
  p_rules jsonb,
  p_now timestamptz default pg_catalog.clock_timestamp()
)
returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
  v_rule jsonb;
  v_policy_code text := pg_catalog.btrim(coalesce(p_policy_code, ''));
  v_rule_code text;
  v_key_digest text;
  v_limit integer;
  v_window_seconds integer;
  v_window_started_at timestamptz;
  v_window_ends_at timestamptz;
  v_existing_window_started_at timestamptz;
  v_existing_window_seconds integer;
  v_existing_count integer;
  v_current_count integer;
  v_retry_after integer;
  v_max_retry_after integer := 0;
  v_blocked_rules jsonb := '[]'::jsonb;
  v_rule_results jsonb := '[]'::jsonb;
  v_rule_count integer;
  v_distinct_rule_count integer;
begin
  if p_now is null then
    raise exception 'rate limit evaluation time is required';
  end if;

  if v_policy_code !~ '^[A-Z0-9_]{1,64}$' then
    raise exception 'invalid rate limit policy code';
  end if;

  if p_rules is null or pg_catalog.jsonb_typeof(p_rules) <> 'array' then
    raise exception 'rate limit rules must be a JSON array';
  end if;

  v_rule_count := pg_catalog.jsonb_array_length(p_rules);
  if v_rule_count < 1 or v_rule_count > 8 then
    raise exception 'rate limit rules must contain between 1 and 8 entries';
  end if;

  select pg_catalog.count(*), pg_catalog.count(distinct value->>'ruleCode')
    into v_rule_count, v_distinct_rule_count
  from pg_catalog.jsonb_array_elements(p_rules);

  if v_rule_count <> v_distinct_rule_count then
    raise exception 'duplicate rate limit rule code';
  end if;

  -- Lock every prospective bucket before reading any count. Advisory locks also
  -- serialize the absent-row case, so concurrent first requests cannot race an
  -- INSERT. Sorting makes multi-rule lock acquisition deterministic.
  for v_rule in
    select value
    from pg_catalog.jsonb_array_elements(p_rules)
    order by value->>'ruleCode', value->>'keyDigest'
  loop
    v_rule_code := coalesce(v_rule->>'ruleCode', '');
    v_key_digest := coalesce(v_rule->>'keyDigest', '');
    v_limit := (v_rule->>'limit')::integer;
    v_window_seconds := (v_rule->>'windowSeconds')::integer;

    if v_rule_code !~ '^[A-Z0-9_]{1,64}$'
      or v_key_digest !~ '^[0-9a-f]{64}$'
      or v_limit < 1
      or v_limit > 1000000
      or v_window_seconds < 1
      or v_window_seconds > 604800
    then
      raise exception 'invalid rate limit rule';
    end if;

    perform pg_catalog.pg_advisory_xact_lock(
      pg_catalog.hashtextextended(
        v_policy_code || '|' || v_rule_code || '|' || v_key_digest,
        0
      )
    );
  end loop;

  -- Evaluate all rules without writing. If any rule blocks, the function
  -- returns before any quota debit, preserving all-or-nothing consumption.
  for v_rule in
    select value
    from pg_catalog.jsonb_array_elements(p_rules)
    order by value->>'ruleCode', value->>'keyDigest'
  loop
    v_rule_code := v_rule->>'ruleCode';
    v_key_digest := v_rule->>'keyDigest';
    v_limit := (v_rule->>'limit')::integer;
    v_window_seconds := (v_rule->>'windowSeconds')::integer;
    v_window_started_at := pg_catalog.to_timestamp(
      pg_catalog.floor(
        extract(epoch from p_now) / v_window_seconds
      ) * v_window_seconds
    );
    v_window_ends_at := v_window_started_at
      + pg_catalog.make_interval(secs => v_window_seconds);

    v_existing_count := null;
    v_existing_window_started_at := null;
    v_existing_window_seconds := null;

    select b.request_count, b.window_started_at, b.window_seconds
      into v_existing_count, v_existing_window_started_at, v_existing_window_seconds
    from private.rate_limit_buckets b
    where b.policy_code = v_policy_code
      and b.rule_code = v_rule_code
      and b.key_digest = v_key_digest;

    if found
      and v_existing_window_seconds = v_window_seconds
      and v_existing_window_started_at = v_window_started_at
    then
      v_current_count := v_existing_count;
    else
      v_current_count := 0;
    end if;

    if v_current_count >= v_limit then
      v_retry_after := greatest(
        1,
        pg_catalog.ceil(
          extract(epoch from (v_window_ends_at - p_now))
        )::integer
      );
      v_max_retry_after := greatest(v_max_retry_after, v_retry_after);
      v_blocked_rules := v_blocked_rules || pg_catalog.jsonb_build_array(
        pg_catalog.jsonb_build_object(
          'ruleCode', v_rule_code,
          'limit', v_limit,
          'windowSeconds', v_window_seconds,
          'retryAfterSeconds', v_retry_after,
          'resetAt', v_window_ends_at
        )
      );
    end if;
  end loop;

  if pg_catalog.jsonb_array_length(v_blocked_rules) > 0 then
    return pg_catalog.jsonb_build_object(
      'allowed', false,
      'policyCode', v_policy_code,
      'retryAfterSeconds', v_max_retry_after,
      'blockedRules', v_blocked_rules,
      'rules', '[]'::jsonb
    );
  end if;

  -- Every mandatory rule passed. Debit each bucket while the same advisory
  -- locks remain held for this transaction.
  for v_rule in
    select value
    from pg_catalog.jsonb_array_elements(p_rules)
    order by value->>'ruleCode', value->>'keyDigest'
  loop
    v_rule_code := v_rule->>'ruleCode';
    v_key_digest := v_rule->>'keyDigest';
    v_limit := (v_rule->>'limit')::integer;
    v_window_seconds := (v_rule->>'windowSeconds')::integer;
    v_window_started_at := pg_catalog.to_timestamp(
      pg_catalog.floor(
        extract(epoch from p_now) / v_window_seconds
      ) * v_window_seconds
    );
    v_window_ends_at := v_window_started_at
      + pg_catalog.make_interval(secs => v_window_seconds);

    insert into private.rate_limit_buckets (
      policy_code,
      rule_code,
      key_digest,
      window_seconds,
      window_started_at,
      request_count,
      expires_at,
      updated_at
    ) values (
      v_policy_code,
      v_rule_code,
      v_key_digest,
      v_window_seconds,
      v_window_started_at,
      1,
      v_window_ends_at,
      p_now
    )
    on conflict (policy_code, rule_code, key_digest) do update
      set window_seconds = excluded.window_seconds,
          window_started_at = excluded.window_started_at,
          request_count = case
            when private.rate_limit_buckets.window_seconds = excluded.window_seconds
             and private.rate_limit_buckets.window_started_at = excluded.window_started_at
            then private.rate_limit_buckets.request_count + 1
            else 1
          end,
          expires_at = excluded.expires_at,
          updated_at = excluded.updated_at
    returning request_count into v_current_count;

    v_rule_results := v_rule_results || pg_catalog.jsonb_build_array(
      pg_catalog.jsonb_build_object(
        'ruleCode', v_rule_code,
        'limit', v_limit,
        'windowSeconds', v_window_seconds,
        'remaining', greatest(0, v_limit - v_current_count),
        'resetAt', v_window_ends_at
      )
    );
  end loop;

  -- Opportunistic bounded cleanup. Reusable rows prevent per-window growth;
  -- this removes principals that have gone completely idle without a cron.
  delete from private.rate_limit_buckets b
  where b.ctid in (
    select stale.ctid
    from private.rate_limit_buckets stale
    where stale.expires_at <= p_now
    order by stale.expires_at
    limit 100
  );

  return pg_catalog.jsonb_build_object(
    'allowed', true,
    'policyCode', v_policy_code,
    'retryAfterSeconds', null,
    'blockedRules', '[]'::jsonb,
    'rules', v_rule_results
  );
end;
$$;

revoke all on function public.consume_rate_limit_rules(text, jsonb, timestamptz)
  from public, anon, authenticated;
grant execute on function public.consume_rate_limit_rules(text, jsonb, timestamptz)
  to postgres, service_role;

comment on function public.consume_rate_limit_rules(text, jsonb, timestamptz) is
  'Service-only S08-002 atomic multi-rule fixed-window consumer. Browser roles cannot select limiter principals or mutate counters.';
