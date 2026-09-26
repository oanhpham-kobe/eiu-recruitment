-- TASK-S08-002 focused Application Inbox Internal Search boundary regression.
-- Run only against an unlinked disposable local Supabase database after replay.
\set ON_ERROR_STOP on

begin;

delete from private.rate_limit_buckets
where policy_code = 'INTERNAL_SEARCH';

insert into public.app_users (
  app_user_id,
  auth_user_id,
  email,
  full_name,
  is_active,
  is_root_admin
) values
  (
    '83111111-1111-1111-1111-111111111111',
    '84111111-1111-1111-1111-111111111111',
    's08_inbox_root@eiu.edu.vn',
    'S08 Inbox Root',
    true,
    true
  ),
  (
    '83111111-2222-2222-2222-222222222222',
    '84111111-2222-2222-2222-222222222222',
    's08_inbox_viewer@eiu.edu.vn',
    'S08 Inbox Viewer',
    true,
    false
  ),
  (
    '83111111-3333-3333-3333-333333333333',
    '84111111-3333-3333-3333-333333333333',
    's08_inbox_denied@eiu.edu.vn',
    'S08 Inbox Denied',
    true,
    false
  );

insert into public.app_user_permissions (
  app_user_id,
  permission_code,
  granted_by
) values (
  '83111111-2222-2222-2222-222222222222',
  'submissions.view',
  '83111111-1111-1111-1111-111111111111'
);

-- The public compatibility surface must remain invoker-rights. The accepted
-- implementation also remains invoker-rights after being moved out of the API
-- exposed schemas.
do $$
declare
  v_public_definer boolean;
  v_public_volatility "char";
  v_internal_definer boolean;
begin
  select p.prosecdef, p.provolatile
    into v_public_definer, v_public_volatility
  from pg_catalog.pg_proc p
  join pg_catalog.pg_namespace n on n.oid = p.pronamespace
  where n.nspname = 'public'
    and p.proname = 'list_application_inbox'
    and pg_catalog.pg_get_function_identity_arguments(p.oid) =
      'p_query text, p_status text, p_date_from date, p_date_to date, p_candidate_activity text, p_new_read text, p_application text, p_page integer, p_page_size integer';

  assert v_public_definer = false,
    'public Application Inbox wrapper must remain SECURITY INVOKER';
  assert v_public_volatility = 'v',
    'rate-limited Application Inbox wrapper must be VOLATILE';

  select p.prosecdef
    into v_internal_definer
  from pg_catalog.pg_proc p
  join pg_catalog.pg_namespace n on n.oid = p.pronamespace
  where n.nspname = 'internal_search'
    and p.proname = 'list_application_inbox_unlimited';

  assert v_internal_definer = false,
    'accepted Application Inbox implementation must remain SECURITY INVOKER';

  assert pg_catalog.has_function_privilege(
    'authenticated',
    'public.list_application_inbox(text,text,date,date,text,text,text,integer,integer)',
    'EXECUTE'
  ), 'authenticated must retain the public Application Inbox RPC';
  assert not pg_catalog.has_function_privilege(
    'anon',
    'public.list_application_inbox(text,text,date,date,text,text,text,integer,integer)',
    'EXECUTE'
  ), 'anon must not execute the public Application Inbox RPC';
end;
$$;

select pg_catalog.set_config(
  'request.jwt.claim.sub',
  '84111111-2222-2222-2222-222222222222',
  false
);
set role authenticated;

-- Empty query remains free. The request itself runs as authenticated; private
-- limiter state is inspected only after RESET ROLE so the test does not weaken
-- the production privilege boundary it is meant to verify.
select pg_catalog.count(*)
from public.list_application_inbox(
  '', 'ALL', null, null,
  'ALL', 'ALL', 'ALL', 1, 25
);

reset role;

do $$
declare
  v_rows bigint;
begin
  select pg_catalog.count(*) into v_rows
  from private.rate_limit_buckets
  where policy_code = 'INTERNAL_SEARCH';
  assert v_rows = 0,
    'empty Application Inbox query must not create/debit search quota';
end;
$$;

set role authenticated;

-- Filter/pagination changes with empty free-text query also remain free.
select pg_catalog.count(*)
from public.list_application_inbox(
  '', 'NEW', '2026-09-01', '2026-09-30',
  'ACTIVE', 'NEW', 'NO_APPLICATION', 3, 50
);

reset role;

do $$
declare
  v_rows bigint;
begin
  select pg_catalog.count(*) into v_rows
  from private.rate_limit_buckets
  where policy_code = 'INTERNAL_SEARCH';
  assert v_rows = 0,
    'filter and pagination changes with empty free-text query must remain free';
end;
$$;

set role authenticated;

-- Any normalized non-empty free-text attempt debits exactly one actor bucket,
-- even when the search happens to return no rows.
select pg_catalog.count(*)
from public.list_application_inbox(
  'Nguyen', 'ALL', null, null,
  'ALL', 'ALL', 'ALL', 1, 25
);

reset role;

do $$
declare
  v_rows bigint;
  v_count integer;
begin
  select pg_catalog.count(*), pg_catalog.max(request_count)
    into v_rows, v_count
  from private.rate_limit_buckets
  where policy_code = 'INTERNAL_SEARCH'
    and rule_code = 'ACTOR_1M';

  assert v_rows = 1,
    'first non-empty Application Inbox search must create one actor bucket';
  assert v_count = 1,
    'first non-empty Application Inbox search must debit exactly once';
end;
$$;

-- Caller without submissions.view/root authority receives no rows and is
-- rejected before the rate-limit gate, so denied probes cannot burn quota.
select pg_catalog.set_config(
  'request.jwt.claim.sub',
  '84111111-3333-3333-3333-333333333333',
  false
);
set role authenticated;

do $$
declare
  v_result_count bigint;
begin
  select pg_catalog.count(*) into v_result_count
  from public.list_application_inbox(
    'Denied Probe', 'ALL', null, null,
    'ALL', 'ALL', 'ALL', 1, 25
  );
  assert v_result_count = 0,
    'unauthorized Application Inbox caller must receive no rows';
end;
$$;

reset role;

do $$
declare
  v_bucket_count bigint;
  v_request_count integer;
begin
  select pg_catalog.count(*), pg_catalog.max(request_count)
    into v_bucket_count, v_request_count
  from private.rate_limit_buckets
  where policy_code = 'INTERNAL_SEARCH';

  assert v_bucket_count = 1 and v_request_count = 1,
    'unauthorized Application Inbox caller must not consume search quota';
end;
$$;

-- Force the authorized actor bucket to the canonical threshold in the current
-- fixed window, then verify the public RPC surfaces the transport contract.
select pg_catalog.set_config(
  'request.jwt.claim.sub',
  '84111111-2222-2222-2222-222222222222',
  false
);

update private.rate_limit_buckets
set request_count = 120,
    window_seconds = 60,
    window_started_at = pg_catalog.to_timestamp(
      pg_catalog.floor(
        pg_catalog.extract(epoch from pg_catalog.clock_timestamp()) / 60
      ) * 60
    ),
    expires_at = pg_catalog.to_timestamp(
      pg_catalog.floor(
        pg_catalog.extract(epoch from pg_catalog.clock_timestamp()) / 60
      ) * 60
    ) + pg_catalog.make_interval(secs => 60),
    updated_at = pg_catalog.clock_timestamp()
where policy_code = 'INTERNAL_SEARCH'
  and rule_code = 'ACTOR_1M';

set role authenticated;

do $$
declare
  v_message text;
  v_detail text;
  v_detail_json jsonb;
begin
  begin
    perform pg_catalog.count(*)
    from public.list_application_inbox(
      'Blocked Search', 'ALL', null, null,
      'ALL', 'ALL', 'ALL', 1, 25
    );

    assert false,
      'blocked Application Inbox search must raise a PostgREST transport error';
  exception when sqlstate 'PGRST' then
    get stacked diagnostics
      v_message = message_text,
      v_detail = pg_exception_detail;

    assert (v_message::jsonb)->>'code' = 'INTERNAL_SEARCH_RATE_LIMITED',
      'blocked Application Inbox search must expose canonical rate-limit code';

    v_detail_json := v_detail::jsonb;
    assert (v_detail_json->>'status')::integer = 429,
      'blocked Application Inbox search must request literal HTTP 429';
    assert ((v_detail_json->'headers'->>'Retry-After')::integer) between 1 and 60,
      'blocked Application Inbox search must expose authoritative Retry-After';
  end;
end;
$$;

reset role;

do $$
declare
  v_request_count integer;
begin
  select request_count into v_request_count
  from private.rate_limit_buckets
  where policy_code = 'INTERNAL_SEARCH'
    and rule_code = 'ACTOR_1M';

  assert v_request_count = 120,
    'blocked Application Inbox search must not overshoot durable quota';
end;
$$;

rollback;
