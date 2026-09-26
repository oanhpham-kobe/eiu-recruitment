-- TASK-S08-002 — Internal Search durable actor limiter helper.
-- This private helper is the single database-side quota primitive for internal
-- free-text search. Browser roles cannot execute it directly. Authoritative
-- search RPCs call it after their own authentication/authorization checks.
--
-- Empty/whitespace-only search is intentionally free. Non-empty search derives
-- the quota principal only from auth.uid() -> active app_users.app_user_id and
-- persists only the existing opaque SHA-256 actor digest in limiter state.

create or replace function private.consume_internal_search_rate_limit(
  p_query text,
  p_now timestamptz default pg_catalog.clock_timestamp()
)
returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
  v_query text := pg_catalog.regexp_replace(
    coalesce(p_query, ''),
    '^[[:space:]]+|[[:space:]]+$',
    '',
    'g'
  );
  v_actor uuid;
  v_key_digest text;
  v_limit jsonb;
begin
  -- Operational filter/pagination reads and option preloads pass an empty
  -- free-text query and must not consume INTERNAL_SEARCH quota. POSIX space
  -- normalization keeps tabs/newlines equivalent to String.trim() at the web
  -- boundary instead of treating invisible whitespace as a billable search.
  if v_query = '' then
    return pg_catalog.jsonb_build_object(
      'allowed', true,
      'policyCode', 'INTERNAL_SEARCH',
      'retryAfterSeconds', null,
      'blockedRules', '[]'::jsonb,
      'rules', '[]'::jsonb
    );
  end if;

  v_actor := private.current_app_user_id();
  if v_actor is null then
    return pg_catalog.jsonb_build_object(
      'allowed', false,
      'errorCode', 'RATE_LIMIT_UNAVAILABLE',
      'policyCode', 'INTERNAL_SEARCH',
      'retryAfterSeconds', null,
      'blockedRules', '[]'::jsonb,
      'rules', '[]'::jsonb
    );
  end if;

  -- Keep the SQL digest exactly aligned with web/src/lib/security/rate-limit.ts:
  -- sha256("s08-002:v1:ACTOR:" + lower(trim(app_user_id))).
  v_key_digest := pg_catalog.encode(
    extensions.digest(
      pg_catalog.convert_to(
        's08-002:v1:ACTOR:'
          || pg_catalog.lower(pg_catalog.btrim(v_actor::text)),
        'UTF8'
      ),
      'sha256'
    ),
    'hex'
  );

  begin
    v_limit := public.consume_rate_limit_rules(
      'INTERNAL_SEARCH',
      pg_catalog.jsonb_build_array(
        pg_catalog.jsonb_build_object(
          'ruleCode', 'ACTOR_1M',
          'keyDigest', v_key_digest,
          'limit', 120,
          'windowSeconds', 60
        )
      ),
      p_now
    );
  exception when others then
    -- Fail closed without leaking database details to the eventual HTTP layer.
    return pg_catalog.jsonb_build_object(
      'allowed', false,
      'errorCode', 'RATE_LIMIT_UNAVAILABLE',
      'policyCode', 'INTERNAL_SEARCH',
      'retryAfterSeconds', null,
      'blockedRules', '[]'::jsonb,
      'rules', '[]'::jsonb
    );
  end;

  return v_limit;
end;
$$;

revoke all on function private.consume_internal_search_rate_limit(text, timestamptz)
  from public, anon, authenticated;
grant execute on function private.consume_internal_search_rate_limit(text, timestamptz)
  to postgres, service_role;

comment on function private.consume_internal_search_rate_limit(text, timestamptz) is
  'S08-002 private Internal Search limiter. Empty query is free; non-empty query uses the active internal app_user_id actor principal at 120 requests per 60-second fixed window.';
