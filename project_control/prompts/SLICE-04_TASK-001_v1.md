# EIU Recruitment — Executor Prompt
## TASK-S04-001 — Interview Round and Schedule schema migration, conflict locking, and participant data model
### Prompt version: SLICE-04_TASK-001_v1

## 0. Execution Control

```text
SOURCE_BASELINE: Full Handover v1.17
SOURCE_SHA256: 0b39c3615dd5b34e998527a1d273e0b846458c7bd4170be46c9bb670bfcb3498
BUSINESS_STATUS: Business Logic Core v1.2 = FROZEN
TECHNICAL_STATUS: Technical Architecture v1.17 = TECHNICAL SPECIFICATION FROZEN
TASK_SCOPE: TASK-S04-001 Interview Round and Schedule schema migration, conflict locking, and participant data model Only
WORKTREE: D:/orca/recruitment/TASK-S04-001-interview-schema
BRANCH: oanhpham-kobe/TASK-S04-001-interview-schema
BASE_BRANCH: autonomy/continuous-integration-20260905-01
BASE_HEAD: 023ad0f032ab44292ee059be59f6da9ffab430c7
```

---

## 1. Governance & Compact Routing

```yaml
GOVERNANCE:
  pack_version: "1.1"
  SKILLS_REQUIRED:
    - supabase
    - supabase-postgres-best-practices
    - security-review
    - tdd
  SKILLS_RESOLVED:
    - supabase (skills/supabase)
    - supabase-postgres-best-practices (skills/supabase-postgres-best-practices)
    - security-review (skills/security-review)
    - tdd (skills/engineering/tdd)
  SKILLS_APPLIED:
    - supabase: "defining interviews and interview_participants tables, RLS policies, PostgREST grant separation, helper views, and server client integration"
    - supabase-postgres-best-practices: "authoring secure RPC functions with search_path='', deterministic advisory resource locking preventing deadlocks, optimistic versioning, permission prerequisites check"
    - security-review: "authorizing interviews.view, interviews.manage, interviews.status, interviews.participants, interviewer visibility isolation, and protecting participant lifecycle invariants"
    - tdd: "risk-based SQL integration test suite covering round creation, schedule conflict locking, participant uniqueness, inactive user operational rejection, and interval boundary edge cases"
  GRAPH_ROUTE: DIRECT_SOURCE_LSP_ONLY
  GRAPH_ROUTE_REASON: "Foundational database schema migration, conflict locking functions, and participant data model directly derived from review pack specifications"
  PRINCIPLE_PROFILE: "INTERVIEW_SCHEMA_AND_CONFLICT_LOCKING"
  EVIDENCE_DELTA: "INTERVIEW-SCHEMA-001"
```

---

## 2. Canonical Source References

- `recruitment_webapp/review_pack/05_HR_INTERVIEW_PAGE.md` (§Interview lifecycle, scheduling intervals, conflict rules, participant management)
- `recruitment_webapp/review_pack/08_DATA_MODEL_AND_FIELD_DICTIONARY.md` (`interviews`, `interview_participants`, `cancellation_reasons`, `rejection_reasons`)
- `recruitment_webapp/review_pack/37_BACKEND_COMMAND_CONTRACTS.md` (§6 Interview rounds, Copy and schedule; §7 Format normalization; §8 Participant management)
- `recruitment_webapp/review_pack/40_DATABASE_INVARIANTS.md` (§Interview invariants, §Participant lifecycle, §Resource conflict invariants)
- `recruitment_webapp/review_pack/48_IDEMPOTENCY_CONCURRENCY_SPEC.md` (§Mandatory schedule consistency, §Deterministic advisory resource locking, §Participant concurrency)
- `recruitment_webapp/review_pack/13_ACCEPTANCE_CRITERIA_AND_TEST_CASES.md` (`AC-22C`, `AC-SCH-SRC-01`, `AC-PART-OPER-03`, `AC-PART-OPER-04`, `AC-MASTER-04`)
- `recruitment_webapp/review_pack/database_schema.sql` (lines 475-540, lines 1066-1122, lines 1350-1360, lines 1397-1423, lines 1570-1600)

---

## 3. Implementation Specification

### 3.1 Migration File: `supabase/migrations/20260906060000_interview_schema_and_conflict_locking.sql`

#### 1. Alter `public.interviews` Table
Ensure `public.interviews` has all canonical columns and constraints:
- Add `cancellation_reason_id uuid references public.cancellation_reasons(cancellation_reason_id) on delete restrict`
- Add `rejection_reason_id uuid references public.rejection_reasons(rejection_reason_id) on delete restrict`
- Add `visible_to_interviewers boolean not null default true`
- Add `interview_note text` (migrate any existing `notes` column data into `interview_note`)
- Add `updated_by uuid references public.app_users(app_user_id) on delete restrict`
- Check constraint `interview_time_range_ck`: `check (start_at is null or end_at is null or start_at < end_at)`
- Foreign key `copied_from_interview_id` references `public.interviews(interview_id) on delete restrict`
- Add indexes:
  - `interviews_application_idx on public.interviews(application_id, round_no desc)`
  - `interviews_time_idx on public.interviews(start_at, end_at) where is_active = true`
  - `interviews_room_time_idx on public.interviews(room_id, start_at, end_at) where is_active = true and room_id is not null`

#### 2. Create `public.interview_participants` Table
```sql
create table if not exists public.interview_participants (
  interview_participant_id uuid primary key default gen_random_uuid(),
  interview_id uuid not null references public.interviews(interview_id) on delete restrict,
  app_user_id uuid not null references public.app_users(app_user_id) on delete restrict,
  participant_order integer not null check (participant_order > 0),
  snapshot_name text not null,
  snapshot_job_title text,
  snapshot_email citext not null,
  is_current boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  removed_at timestamptz,
  version_no bigint not null default 1
);

create unique index if not exists current_participant_user_uq
  on public.interview_participants(interview_id, app_user_id)
  where is_current = true;

create unique index if not exists current_participant_order_uq
  on public.interview_participants(interview_id, participant_order)
  where is_current = true;

create index if not exists participant_user_idx
  on public.interview_participants(app_user_id, interview_id)
  where is_current = true;
```

#### 3. Triggers & Guards
- `interviews_touch_version` before update on `public.interviews`
- `interview_participants_touch_version` before update on `public.interview_participants`
- `interview_format_requirements_guard` before insert or update of `start_at, end_at, interview_format_id, room_id, meeting_link, schedule_status_code` on `public.interviews` calling `private.validate_interview_format_requirements()`
- `interview_reason_normalize_guard` before insert or update of `schedule_status_code, report_status_code, cancellation_reason_id, rejection_reason_id` on `public.interviews` calling `private.normalize_interview_reason_fields()`
- `participant_lifecycle_user_guard` before insert or update of `is_current, removed_at, app_user_id` on `public.interview_participants` calling `private.validate_participant_lifecycle_and_user()`
- `interview_active_master_guard` before insert or update of `room_id, interview_format_id, cancellation_reason_id, rejection_reason_id` on `public.interviews` calling `private.validate_active_master_references()`
- Ensure `private.block_ineligible_hr_owner_lifecycle()` defends future interview participant reassignments when an internal user is deactivated.

#### 4. Helper Views
- `private.access_active_interviews`:
  ```sql
  create or replace view private.access_active_interviews with (security_invoker = true) as
  select i.*
  from public.interviews i
  join public.applications a on a.application_id = i.application_id
  where a.is_active = true and i.is_active = true;
  ```
- `private.resource_blocking_interviews`:
  ```sql
  create or replace view private.resource_blocking_interviews with (security_invoker = true) as
  select i.*
  from private.access_active_interviews i
  where i.schedule_status_code <> 'CANCELLED'
    and i.start_at is not null
    and i.end_at is not null;
  ```
- `private.application_current_interview`:
  ```sql
  create or replace view private.application_current_interview with (security_invoker = true) as
  select a.application_id, i.interview_id, i.round_no
  from public.applications a
  left join lateral (
    select i1.interview_id, i1.round_no
    from private.access_active_interviews i1
    where i1.application_id = a.application_id
    order by i1.round_no desc
    limit 1
  ) i on true
  where a.is_active = true;
  ```

#### 5. Operational Eligibility & Clean Interview Functions
- `private.all_current_participants_selectable(p_interview_id uuid)` returning boolean
- `private.is_interview_clean(p_interview_id uuid)` returning boolean

#### 6. Conflict Locking & Detection
- `private.lock_interview_resources(p_candidate_id uuid, p_room_id uuid, p_interviewer_ids uuid[])`:
  Acquires transaction-level advisory locks in deterministic sorted resource order (Candidate -> Room -> Interviewers).
- `private.check_interview_conflicts(p_interview_id uuid, p_candidate_id uuid, p_room_id uuid, p_interviewer_ids uuid[], p_start_at timestamptz, p_end_at timestamptz)`:
  Queries `private.resource_blocking_interviews` for overlapping intervals (`start_at < p_end_at and end_at > p_start_at`) for Candidate, Room, and any of the Interviewers.
  Returns table/record of detected conflicts. Note: adjacent intervals where `end_at = start_at` do NOT overlap.

#### 7. RLS & Grants
- Enable RLS on `public.interview_participants`
- Revoke all from `public`, `anon`; grant `select` to `authenticated`; grant all to `postgres`, `service_role`
- Policy `interview_participants_select` on `public.interview_participants`:
  ```sql
  create policy interview_participants_select on public.interview_participants
    for select to authenticated
    using (
      private.has_permission('interviews.view')
      or private.has_permission('submissions.view')
      or private.is_root_admin()
      or app_user_id = auth.uid()
    );
  ```
- Update `interviews_select` policy on `public.interviews` to allow interviewers to view their active assigned interviews:
  ```sql
  drop policy if exists interviews_select on public.interviews;
  create policy interviews_select on public.interviews
    for select to authenticated
    using (
      private.has_permission('interviews.view')
      or private.has_permission('submissions.view')
      or private.is_root_admin()
      or (
        visible_to_interviewers = true
        and is_active = true
        and exists (
          select 1 from public.interview_participants ip
          join public.applications a on a.application_id = interviews.application_id
          where ip.interview_id = interviews.interview_id
            and ip.app_user_id = auth.uid()
            and ip.is_current = true
            and a.is_active = true
        )
      )
    );
  ```

#### 8. Core Functions / RPCs
- `create_next_interview_round(p_application_id uuid, p_idempotency_key text default null)`:
  Locks Application row, finds current max round, validates prerequisites, allocates round+1, creates empty Round N, writes audit log, returns new `interview_id`.
- `check_interview_schedule_conflicts(p_interview_id uuid, p_start_at timestamptz, p_end_at timestamptz, p_room_id uuid, p_interviewer_ids uuid[])`:
  Exposes conflict checking with clear conflict breakdown (`candidate_conflict`, `room_conflict`, `interviewer_conflict`).

### 3.2 Verification
Write and execute comprehensive SQL test suite in `supabase/tests/interview_round_and_conflict_locking_test.sql` proving:
1. `interviews` column additions and constraints (`start_at < end_at` check).
2. `interview_participants` creation, snapshot copying from `app_users`, and unique order/user constraints.
3. Inactive participant operational rejection (`all_current_participants_selectable`).
4. Conflict detection for candidate, room, and interviewer overlaps.
5. Adjacent interval allowance (`[09:00, 10:00)` and `[10:00, 11:00)` do not conflict).
6. CANCELLED or inactive interviews do not cause conflicts (`resource_blocking` predicate).
7. RLS policies allow authorized HR and assigned interviewers to view appropriate rows.
8. Round creation allocates sequential rounds and enforces application active requirement.
