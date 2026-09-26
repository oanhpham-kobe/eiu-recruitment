-- TASK-S08-002 — Application Inbox Internal Search rate-limit boundary.
--
-- Keep the accepted S08-001 query implementation intact and SECURITY INVOKER,
-- but move it behind an unexposed schema so browser callers cannot bypass the
-- public rate-limited RPC. Supabase Data API exposes only public/graphql_public.

create schema if not exists internal_search;

revoke all on schema internal_search from public, anon;
grant usage on schema internal_search to authenticated, postgres, service_role;

comment on schema internal_search is
  'Unexposed server-side schema for authenticated Internal Search implementations. It is intentionally absent from Supabase api.schemas.';

-- Preserve the exact accepted S08-001 implementation by OID instead of copying
-- its large search query into this migration. Moving/renaming preserves its
-- SECURITY INVOKER behavior, body, defaults and dependent object identity.
alter function public.list_application_inbox(
  text, text, date, date, text, text, text, integer, integer
) set schema internal_search;

alter function internal_search.list_application_inbox(
  text, text, date, date, text, text, text, integer, integer
) rename to list_application_inbox_unlimited;

revoke all on function internal_search.list_application_inbox_unlimited(
  text, text, date, date, text, text, text, integer, integer
) from public, anon;
grant execute on function internal_search.list_application_inbox_unlimited(
  text, text, date, date, text, text, text, integer, integer
) to authenticated, postgres, service_role;

-- Narrow SECURITY DEFINER gate. The caller cannot choose a principal or a fake
-- evaluation time; private.consume_internal_search_rate_limit derives the active
-- app_user_id from auth.uid() and uses clock_timestamp().
create or replace function internal_search.enforce_internal_search_rate_limit(
  p_query text
)
returns void
language plpgsql
volatile
security definer
set search_path = ''
as $$
declare
  v_limit jsonb;
  v_retry_after integer;
begin
  v_limit := private.consume_internal_search_rate_limit(p_query);

  if coalesce((v_limit->>'allowed')::boolean, false) then
    return;
  end if;

  if v_limit->>'errorCode' = 'RATE_LIMIT_UNAVAILABLE' then
    raise sqlstate 'PGRST'
      using message = pg_catalog.jsonb_build_object(
        'code', 'RATE_LIMIT_UNAVAILABLE',
        'message', 'Internal Search rate limit is temporarily unavailable',
        'details', null,
        'hint', null
      )::text,
      detail = pg_catalog.jsonb_build_object(
        'status', 503,
        'headers', pg_catalog.jsonb_build_object()
      )::text;
  end if;

  v_retry_after := greatest(
    coalesce((v_limit->>'retryAfterSeconds')::integer, 1),
    1
  );

  -- PostgREST PGRST custom errors preserve both the literal HTTP status and the
  -- authoritative Retry-After header for direct RPC callers.
  raise sqlstate 'PGRST'
    using message = pg_catalog.jsonb_build_object(
      'code', 'INTERNAL_SEARCH_RATE_LIMITED',
      'message', 'Too many Internal Search requests',
      'details', 'Retry after the current search window resets',
      'hint', null
    )::text,
    detail = pg_catalog.jsonb_build_object(
      'status', 429,
      'headers', pg_catalog.jsonb_build_object(
        'Retry-After', v_retry_after::text
      )
    )::text;
end;
$$;

revoke all on function internal_search.enforce_internal_search_rate_limit(text)
  from public, anon;
grant execute on function internal_search.enforce_internal_search_rate_limit(text)
  to authenticated, postgres, service_role;

comment on function internal_search.enforce_internal_search_rate_limit(text) is
  'Unexposed S08-002 Application Inbox search gate. Empty query is free; blocked non-empty search raises PostgREST HTTP 429 with Retry-After.';

-- Public compatibility wrapper. It remains SECURITY INVOKER so the accepted
-- query implementation and all table/RLS behavior continue to run as the
-- authenticated caller. Unauthorized callers are rejected before quota debit.
create or replace function public.list_application_inbox(
  p_query text default '',
  p_status text default 'ALL',
  p_date_from date default null,
  p_date_to date default null,
  p_candidate_activity text default 'ALL',
  p_new_read text default 'ALL',
  p_application text default 'ALL',
  p_page integer default 1,
  p_page_size integer default 25
)
returns table (
  candidate_id uuid,
  email text,
  is_candidate_active boolean,
  candidate_version_no bigint,
  latest_submission_id uuid,
  latest_submission_version_no bigint,
  submission_id uuid,
  submission_version_no bigint,
  status_code text,
  full_name text,
  date_of_birth date,
  gender_code text,
  phone text,
  hr_note text,
  submitted_at timestamptz,
  has_application boolean,
  total_count bigint
)
language plpgsql
volatile
security invoker
set search_path = ''
as $$
begin
  if not (
    private.has_permission('submissions.view')
    or private.is_root_admin()
  ) then
    return;
  end if;

  perform internal_search.enforce_internal_search_rate_limit(p_query);

  return query
  select *
  from internal_search.list_application_inbox_unlimited(
    p_query,
    p_status,
    p_date_from,
    p_date_to,
    p_candidate_activity,
    p_new_read,
    p_application,
    p_page,
    p_page_size
  );
end;
$$;

revoke all on function public.list_application_inbox(
  text, text, date, date, text, text, text, integer, integer
) from public, anon;
grant execute on function public.list_application_inbox(
  text, text, date, date, text, text, text, integer, integer
) to authenticated;

comment on function public.list_application_inbox(
  text, text, date, date, text, text, text, integer, integer
) is
  'S08-002 rate-limited Application Inbox RPC. Only normalized non-empty free-text search consumes INTERNAL_SEARCH actor quota; filter/pagination reads remain free.';
