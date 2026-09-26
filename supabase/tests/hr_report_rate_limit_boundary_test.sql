-- TASK-S08-002 focused HR Report Internal Search boundary regression.
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
    '85111111-1111-1111-1111-111111111111',
    '86111111-1111-1111-1111-111111111111',
    's08_hr_root@eiu.edu.vn',
    'S08 HR Root',
    true,
    true
  ),
  (
    '85111111-2222-2222-2222-222222222222',
    '86111111-2222-2222-2222-222222222222',
    's08_hr_viewer@eiu.edu.vn',
    'S08 HR Viewer',
    true,
    false
  ),
  (
    '85111111-3333-3333-3333-333333333333',
    '86111111-3333-3333-3333-333333333333',
    's08_hr_denied@eiu.edu.vn',
    'S08 HR Denied',
    true,
    false
  );

insert into public.app_user_permissions (
  app_user_id,
  permission_code,
  granted_by
) values (
  '85111111-2222-2222-2222-222222222222',
  'reports.view',
  '85111111-1111-1111-1111-111111111111'
);

-- Public HR Report remains the only browser-callable authority. Its wrapper is
-- SECURITY DEFINER for DTO privacy and must now be VOLATILE because it may debit
-- durable limiter state. The private implementation remains non-browser-callable.
do $$
declare
  v_public_definer boolean;
  v_public_volatility "char";
begin
  select p.prosecdef, p.provolatile
    into v_public_definer, v_public_volatility
  from pg_catalog.pg_proc p
  join pg_catalog.pg_namespace n on n.oid = p.pronamespace
  where n.nspname = 'public'
    and p.proname = 'get_hr_report_page'
    and pg_catalog.pg_get_function_identity_arguments(p.oid) =
      'p_page integer, p_page_size integer, p_status_code text, p_visibility text, p_search text, p_sort text';

  assert v_public_definer = true,
    'public HR Report wrapper must remain SECURITY DEFINER for DTO privacy';
  assert v_public_volatility = 'v',
    'rate-limited HR Report wrapper must be VOLATILE';

  assert pg_catalog.has_function_privilege(
    'authenticated',
    'public.get_hr_report_page(integer,integer,text,text,text,text)',
    'EXECUTE'
  ), 'authenticated must retain the public HR Report RPC';
  assert not pg_catalog.has_function_privilege(
    'anon',
    'public.get_hr_report_page(integer,integer,text,text,text,text)',
    'EXECUTE'
  ), 'anon must not execute the public HR Report RPC';
  assert not pg_catalog.has_schema_privilege(
    'authenticated',
    'hr_report_private',
    'USAGE'
  ), 'authenticated must not have direct HR Report private schema access';
  assert not pg_catalog.has_function_privilege(
    'authenticated',
    'hr_report_private.get_hr_report_page_impl(integer,integer,text,text,text,text)',
    'EXECUTE'
  ), 'authenticated must not bypass the public rate-limited HR Report RPC';
end;
$$;

select pg_catalog.set_config(
  'request.jwt.claim.sub',
  '86111111-2222-2222-2222-222222222222',
  false
);
set role authenticated;

-- Empty free-text is free.
select public.get_hr_report_page(
  1, 20, null, 'ALL', '', 'CANDIDATE_ASC'
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
    'empty HR Report query must not create/debit search quota';
end;
$$;

set role authenticated;

-- Filter, sort and pagination changes with empty search remain free.
select public.get_hr_report_page(
  3, 50, 'WAITING_FOR_REPORT', 'VISIBLE', null, 'UPDATED_DESC'
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
    'HR Report filter/sort/pagination reads with empty search must remain free';
end;
$$;

set role authenticated;

-- A valid non-empty free-text attempt debits exactly once even with zero rows.
select public.get_hr_report_page(
  1, 20, null, 'ALL', 'Candidate', 'CANDIDATE_ASC'
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
    'first non-empty HR Report search must create one actor bucket';
  assert v_count = 1,
    'first non-empty HR Report search must debit exactly once';
end;
$$;

-- A forbidden caller must be rejected before quota debit.
select pg_catalog.set_config(
  'request.jwt.claim.sub',
  '86111111-3333-3333-3333-333333333333',
  false
);
set role authenticated;

do $$
declare
  v_result jsonb;
begin
  v_result := public.get_hr_report_page(
    1, 20, null, 'ALL', 'Denied Probe', 'CANDIDATE_ASC'
  );

  assert v_result->>'error_code' = 'FORBIDDEN',
    'unauthorized HR Report caller must preserve accepted FORBIDDEN contract';
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
    'unauthorized HR Report caller must not consume search quota';
end;
$$;

-- Invalid requests preserve authoritative validation and also do not burn quota.
select pg_catalog.set_config(
  'request.jwt.claim.sub',
  '86111111-2222-2222-2222-222222222222',
  false
);
set role authenticated;

do $$
declare
  v_result jsonb;
begin
  v_result := public.get_hr_report_page(
    0, 20, null, 'ALL', 'Invalid Probe', 'CANDIDATE_ASC'
  );

  assert v_result->>'error_code' = 'VALIDATION_ERROR',
    'invalid HR Report request must preserve accepted VALIDATION_ERROR contract';
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

  assert v_request_count = 1,
    'invalid HR Report request must not consume search quota';
end;
$$;

-- Force the authorized actor bucket to the canonical threshold in the current
-- fixed window and verify the direct public RPC transport contract.
update private.rate_limit_buckets
set request_count = 120,
    window_seconds = 60,
    window_started_at = pg_catalog.to_timestamp(
      pg_catalog.floor(
        pg_catalog.date_part('epoch', pg_catalog.clock_timestamp()) / 60
      ) * 60
    ),
    expires_at = pg_catalog.to_timestamp(
      pg_catalog.floor(
        pg_catalog.date_part('epoch', pg_catalog.clock_timestamp()) / 60
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
    perform public.get_hr_report_page(
      1, 20, null, 'ALL', 'Blocked Search', 'CANDIDATE_ASC'
    );

    assert false,
      'blocked HR Report search must raise a PostgREST transport error';
  exception when sqlstate 'PGRST' then
    get stacked diagnostics
      v_message = message_text,
      v_detail = pg_exception_detail;

    assert (v_message::jsonb)->>'code' = 'INTERNAL_SEARCH_RATE_LIMITED',
      'blocked HR Report search must expose canonical rate-limit code';

    v_detail_json := v_detail::jsonb;
    assert (v_detail_json->>'status')::integer = 429,
      'blocked HR Report search must request literal HTTP 429';
    assert ((v_detail_json->'headers'->>'Retry-After')::integer) between 1 and 60,
      'blocked HR Report search must expose authoritative Retry-After';
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
    'blocked HR Report search must not overshoot durable quota';
end;
$$;

rollback;
