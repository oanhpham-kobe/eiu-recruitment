-- TASK-S08-002 — HR Report Internal Search rate-limit boundary.
--
-- Preserve the accepted S05-002 authoritative read implementation and DTO
-- privacy contract. The public SECURITY DEFINER wrapper performs only a narrow
-- shadow preflight to decide whether quota may be debited, then delegates all
-- authoritative validation/read semantics to hr_report_private.

create or replace function public.get_hr_report_page(
  p_page integer default 1,
  p_page_size integer default 20,
  p_status_code text default null,
  p_visibility text default 'ALL',
  p_search text default null,
  p_sort text default 'CANDIDATE_ASC'
)
returns jsonb
language plpgsql
volatile
security definer
set search_path = ''
as $$
declare
  v_result jsonb;
  v_auth_uid uuid := auth.uid();
  v_actor uuid;
  v_actor_active boolean;
  v_is_root boolean := false;
  v_page integer := coalesce(p_page, 1);
  v_page_size integer := coalesce(p_page_size, 20);
  v_status text := nullif(upper(pg_catalog.btrim(coalesce(p_status_code, ''))), '');
  v_visibility text := upper(pg_catalog.btrim(coalesce(p_visibility, 'ALL')));
  v_search text := pg_catalog.btrim(coalesce(p_search, ''));
  v_sort text := upper(pg_catalog.btrim(coalesce(p_sort, 'CANDIDATE_ASC')));
  v_boundary_valid boolean := false;
begin
  -- This preflight never replaces the accepted S05-002 authorization or
  -- validation contract. It only prevents unauthenticated/forbidden/invalid
  -- requests from consuming another actor's search quota before delegation.
  if v_auth_uid is not null then
    select u.app_user_id, u.is_active
      into v_actor, v_actor_active
    from public.app_users u
    where u.auth_user_id = v_auth_uid;
  end if;

  if v_actor is not null and coalesce(v_actor_active, false) then
    v_is_root := private.is_root_admin();

    v_boundary_valid :=
      v_page >= 1
      and v_page_size >= 1
      and v_page_size <= 100
      and pg_catalog.char_length(v_search) <= 256
      and v_visibility in ('ALL', 'VISIBLE', 'HIDDEN')
      and v_sort in ('CANDIDATE_ASC', 'CANDIDATE_DESC', 'UPDATED_DESC')
      and (
        v_status is null
        or v_status in (
          'INTERVIEW_SCHEDULING',
          'AWAITING_INTERVIEW',
          'WAITING_FOR_REPORT',
          'REPORT_SUBMITTED',
          'FOLLOW_UP',
          'ON_HOLD',
          'HIRED',
          'REJECTED'
        )
      );

    if v_boundary_valid
       and (v_is_root or private.has_permission('reports.view')) then
      -- The shared gate normalizes whitespace, keeps empty/filter-only reads
      -- free, derives the actor from auth.uid(), and raises literal PostgREST
      -- HTTP 429 + Retry-After when the 120/60s actor window is exhausted.
      perform internal_search.enforce_internal_search_rate_limit(p_search);
    end if;
  end if;

  v_result := hr_report_private.get_hr_report_page_impl(
    p_page,
    p_page_size,
    p_status_code,
    p_visibility,
    p_search,
    p_sort
  );

  -- Preserve the accepted S05-002 minimum-safe DTO boundary exactly: reports
  -- readers never receive the raw Interview meeting URL through this RPC.
  if coalesce((v_result->>'success')::boolean, false)
     and pg_catalog.jsonb_typeof(v_result->'data'->'rows') = 'array' then
    v_result := pg_catalog.jsonb_set(
      v_result,
      '{data,rows}',
      coalesce(
        (
          select pg_catalog.jsonb_agg(row_value - 'meeting_link' order by ordinal)
          from pg_catalog.jsonb_array_elements(v_result->'data'->'rows')
            with ordinality as safe_rows(row_value, ordinal)
        ),
        '[]'::jsonb
      ),
      false
    );
  end if;

  return v_result;
end;
$$;

revoke all on function public.get_hr_report_page(integer, integer, text, text, text, text)
  from public, anon, authenticated;
grant execute on function public.get_hr_report_page(integer, integer, text, text, text, text)
  to authenticated, postgres, service_role;

comment on function public.get_hr_report_page(integer, integer, text, text, text, text) is
  'S08-002 rate-limited HR Report read RPC. Only authorized valid normalized non-empty free-text search consumes INTERNAL_SEARCH actor quota; filter/pagination reads remain free and the accepted meeting-link privacy boundary is preserved.';
