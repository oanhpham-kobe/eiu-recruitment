-- TASK-S08-001 — Application Inbox Search & Indexed Pagination Hardening
-- Forward-only repair over the accepted PRE-S04 list_application_inbox definition.
-- Canonical authority: recruitment_webapp/review_pack/58_SEARCH_AND_INDEXING_STRATEGY.md
--
-- Important baseline fact: PRE-S04 already changed the RPC default to 25,
-- enforced Name length >= 2, and used prefix Email/Phone predicates. This
-- migration preserves those accepted semantics while adding safe Vietnamese
-- accent normalization, wildcard-safe deterministic query classification, and
-- indexes aligned to the actual authoritative predicates.

-- -----------------------------------------------------------------------------
-- 1. Immutable, index-safe search helpers
-- -----------------------------------------------------------------------------

create or replace function private.normalize_vietnamese_search_text(p_value text)
returns text
language sql
immutable
parallel safe
strict
set search_path = ''
as $$
  select translate(
    lower(p_value),
    'áàảãạăắằẳẵặâấầẩẫậđéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵ',
    'aaaaaaaaaaaaaaaaadeeeeeeeeeeeiiiiiooooooooooooooooouuuuuuuuuuuyyyyy'
  );
$$;

create or replace function private.escape_search_like(p_value text)
returns text
language sql
immutable
parallel safe
strict
set search_path = ''
as $$
  select replace(
    replace(
      replace(p_value, '\', '\\'),
      '%', '\%'
    ),
    '_', '\_'
  );
$$;

revoke all on function private.normalize_vietnamese_search_text(text) from public, anon;
revoke all on function private.escape_search_like(text) from public, anon;
grant execute on function private.normalize_vietnamese_search_text(text) to authenticated, postgres, service_role;
grant execute on function private.escape_search_like(text) to authenticated, postgres, service_role;

-- -----------------------------------------------------------------------------
-- 2. Indexes aligned to the predicates actually used by Application Inbox
-- -----------------------------------------------------------------------------

-- Name: accent-insensitive contains search. Keep the predecessor raw-name GIN
-- because it may serve other callers; this expression index is not a duplicate.
create index if not exists submissions_full_name_vi_search_trgm_idx
  on public.submissions using gin (
    private.normalize_vietnamese_search_text(full_name) extensions.gin_trgm_ops
  );

-- Email authority for Application Inbox remains candidates.email. The accepted
-- submissions.email_snapshot lower-case index does NOT support this predicate.
create index if not exists candidates_email_lower_prefix_idx
  on public.candidates ((lower(email::text)) text_pattern_ops);

-- Phone remains Submission snapshot data and is searched by normalized digits.
-- text_pattern_ops makes the prefix predicate indexable under non-C collations.
create index if not exists submissions_phone_digits_prefix_idx
  on public.submissions (
    (regexp_replace(phone, '[^0-9]', '', 'g')) text_pattern_ops
  );

-- -----------------------------------------------------------------------------
-- 3. Harden the accepted Candidate-group Application Inbox RPC
-- -----------------------------------------------------------------------------

drop function if exists public.list_application_inbox(
  text, text, date, date, text, text, text, integer, integer
);

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
language sql
security invoker
set search_path = ''
stable
as $$
  with query_input as (
    select
      btrim(coalesce(p_query, '')) as raw_query,
      private.normalize_vietnamese_search_text(
        btrim(coalesce(p_query, ''))
      ) as normalized_query,
      lower(btrim(coalesce(p_query, ''))) as lower_query,
      regexp_replace(
        btrim(coalesce(p_query, '')),
        '[^0-9]',
        '',
        'g'
      ) as phone_query,
      least(greatest(coalesce(p_page_size, 25), 1), 100) as effective_page_size
  ), query_spec as (
    select
      qi.*,
      case
        when qi.raw_query = '' then 'EMPTY'
        when position('@' in qi.raw_query) > 1
          and char_length(qi.raw_query) >= 3 then 'EMAIL'
        when qi.raw_query ~ '^[0-9+(). -]+$'
          and char_length(qi.phone_query) >= 3 then 'PHONE'
        when char_length(qi.normalized_query) >= 2 then 'NAME'
        else 'NONE'
      end as query_mode,
      private.escape_search_like(qi.normalized_query) as escaped_name_query,
      private.escape_search_like(qi.lower_query) as escaped_email_query
    from query_input qi
  ), ranked as (
    select
      s.submission_id,
      s.candidate_id,
      s.status_code,
      s.full_name,
      s.date_of_birth,
      s.gender_code,
      s.phone,
      s.hr_note,
      s.submitted_at,
      s.version_no as submission_version_no,
      c.email::text as email,
      c.is_active as is_candidate_active,
      c.version_no as candidate_version_no,
      exists (
        select 1
        from public.applications a
        where a.submission_id = s.submission_id
          and a.is_active = true
      ) as has_application,
      row_number() over (
        partition by s.candidate_id
        order by s.submitted_at desc, s.submission_id desc
      ) as submission_rank
    from public.submissions s
    join public.candidates c on c.candidate_id = s.candidate_id
    where private.has_permission('submissions.view') or private.is_root_admin()
  ), latest as (
    select *
    from ranked
    where submission_rank = 1
  ), filtered as (
    select l.*
    from latest l
    cross join query_spec q
    where (
      q.query_mode = 'EMPTY'
      or (
        q.query_mode = 'NAME'
        and private.normalize_vietnamese_search_text(l.full_name)
          like '%' || q.escaped_name_query || '%' escape '\'
      )
      or (
        q.query_mode = 'EMAIL'
        and lower(l.email)
          like q.escaped_email_query || '%' escape '\'
      )
      or (
        q.query_mode = 'PHONE'
        and regexp_replace(l.phone, '[^0-9]', '', 'g')
          like q.phone_query || '%' escape '\'
      )
    )
    and (p_status = 'ALL' or l.status_code = p_status)
    and (
      p_date_from is null
      or l.submitted_at >= p_date_from::timestamp at time zone 'Asia/Ho_Chi_Minh'
    )
    and (
      p_date_to is null
      or l.submitted_at < (p_date_to + 1)::timestamp at time zone 'Asia/Ho_Chi_Minh'
    )
    and (
      p_candidate_activity = 'ALL'
      or (p_candidate_activity = 'ACTIVE') = l.is_candidate_active
    )
    and (p_new_read = 'ALL' or l.status_code = p_new_read)
    and (
      p_application = 'ALL'
      or (p_application = 'HAS_APPLICATION') = l.has_application
    )
  ), counted as (
    select f.*, count(*) over () as total_count
    from filtered f
  ), paged as (
    select c.*
    from counted c
    cross join query_spec q
    order by c.submitted_at desc, c.submission_id desc, c.candidate_id asc
    offset (
      (
        least(
          greatest(coalesce(p_page, 1), 1),
          greatest(
            ceil(
              (select count(*) from filtered)::numeric
              / q.effective_page_size
            )::integer,
            1
          )
        ) - 1
      ) * q.effective_page_size
    )
    limit q.effective_page_size
  )
  select
    p.candidate_id,
    p.email,
    p.is_candidate_active,
    p.candidate_version_no,
    p.submission_id as latest_submission_id,
    p.submission_version_no as latest_submission_version_no,
    s.submission_id,
    s.version_no as submission_version_no,
    s.status_code,
    s.full_name,
    s.date_of_birth,
    s.gender_code,
    s.phone,
    s.hr_note,
    s.submitted_at,
    exists (
      select 1
      from public.applications a
      where a.submission_id = s.submission_id
        and a.is_active = true
    ) as has_application,
    p.total_count
  from paged p
  join public.submissions s on s.candidate_id = p.candidate_id
  order by
    p.submitted_at desc,
    p.submission_id desc,
    p.candidate_id asc,
    s.submitted_at desc,
    s.submission_id desc;
$$;

revoke all on function public.list_application_inbox(
  text, text, date, date, text, text, text, integer, integer
) from public, anon;
grant execute on function public.list_application_inbox(
  text, text, date, date, text, text, text, integer, integer
) to authenticated;
