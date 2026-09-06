# EIU Recruitment — Executor Prompt
## TASK-S04-002 — Interview Report schema, lifecycle commands, participant mutations, schedule lifecycle commands, document storage, and derived views
### Prompt version: SLICE-04_TASK-002_v1

## 0. Execution Control

```text
SOURCE_BASELINE: Full Handover v1.18
SOURCE_SHA256: 8874551cb5a7f78ac28f64a94c1820dc7d2c3a62f85cfb93b2bad70b611438a0
BUSINESS_STATUS: Business Logic Core v1.2 = FROZEN
TECHNICAL_STATUS: Technical Architecture v1.18 = TECHNICAL SPECIFICATION FROZEN
TASK_SCOPE: TASK-S04-002 Interview Report schema, lifecycle commands, participant mutations, schedule lifecycle commands, document storage, and derived views Only
WORKTREE: D:/orca/recruitment/TASK-S04-002-interview-lifecycle
BRANCH: oanhpham-kobe/TASK-S04-002-interview-lifecycle
BASE_BRANCH: autonomy/continuous-integration-20260905-01
BASE_HEAD: 007a278b9f54663eb6d1dd32350b55758c6d814e
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
    - supabase: "interview_reports and interview_document tables, RLS policies, PostgREST grant separation, participant mutation RPCs, report RPCs, schedule lifecycle RPCs, document storage lifecycle"
    - supabase-postgres-best-practices: "enforce_report_decision_metadata trigger, field-aware merge with optimistic versioning, deterministic advisory resource locking for all operational mutations, participant lock-first ordering, bulk command deterministic lock ordering"
    - security-review: "RLS for interview_reports (Interviewer vs HR isolation), interview_documents (current participant + visible), hr_report_note column confidentiality, SECURITY DEFINER search_path guards, bulk-command authorization per item"
    - tdd: "risk-based SQL integration test suite covering report lifecycle, decision metadata trigger, field-aware patch/merge concurrency, participant add/remove/readd/reorder, schedule lifecycle including CONFIRMED reschedule, delete/inactivate round cleanup ordering, document finalization, bulk status command"
  GRAPH_ROUTE: DIRECT_SOURCE_LSP_ONLY
  GRAPH_ROUTE_REASON: "All implementation targets are directly specified in canonical review pack; no cross-module symbol ambiguity requiring graph analysis"
  PRINCIPLE_PROFILE: "INTERVIEW_REPORT_AND_LIFECYCLE"
  EVIDENCE_DELTA: "INTERVIEW-LIFECYCLE-001"
```

---

## 2. Canonical Source References

- `recruitment_webapp/review_pack/05_HR_INTERVIEW_PAGE.md` (§Participants, §Copy, §Schedule conflict engine, §Reactivation behavior, §Canonical schedule predicates)
- `recruitment_webapp/review_pack/06_INTERVIEW_REPORT_HR_AND_INTERVIEWER.md` (§Report Status, §Interviewer view, §Final Decision Source, §Field-aware merge, §Report delete semantics)
- `recruitment_webapp/review_pack/08_DATA_MODEL_AND_FIELD_DICTIONARY.md` (§Interview Session, §Interview Participant, §Interview Report)
- `recruitment_webapp/review_pack/37_BACKEND_COMMAND_CONTRACTS.md` (§6 Interview rounds/Copy/schedule; §7 Format normalization; §8 Participants; §9 Reports; §10 Documents; §Phase-1 named batch commands; §Interview hard-delete temp-upload cleanup ordering)
- `recruitment_webapp/review_pack/39_SECURITY_RLS_MATRIX.md` (§3 Read matrix, §4 Write matrix, §4A Direct-table/RPC access blueprint for interview_reports and interview_documents)
- `recruitment_webapp/review_pack/40_DATABASE_INVARIANTS.md` (§Interview invariants, §Participant lifecycle, §Resource conflict invariants, §Report lifecycle)
- `recruitment_webapp/review_pack/48_IDEMPOTENCY_CONCURRENCY_SPEC.md` (§Report concurrency & Field-Aware Merge, §Mandatory schedule consistency, §Confirmed Reschedule Concurrency, §Deterministic Bulk Locking, §Participant concurrency, §Mandatory lock order)
- `recruitment_webapp/review_pack/13_ACCEPTANCE_CRITERIA_AND_TEST_CASES.md` (§G Report, §F Participants, §I Delete/Inactive, §J Idempotency, AC-38, AC-42, AC-SCH-09)
- `recruitment_webapp/review_pack/database_schema.sql` (lines 541–611, lines 1269–1395, lines 1601–1640)

---

## 3. Implementation Specification

### 3.1 Migration File: `supabase/migrations/20260906070000_interview_lifecycle_commands.sql`

Write this as a single idempotent migration. Use `if not exists`, `create or replace`, `drop ... if exists` before recreate, and `alter table ... add column if not exists`. Do NOT drop and recreate tables.

#### 1. `public.interview_reports` Table

Create:
```sql
create table if not exists public.interview_reports (
  interview_report_id uuid primary key default gen_random_uuid(),
  interview_participant_id uuid not null references public.interview_participants(interview_participant_id) on delete restrict,
  professional_knowledge text,
  necessary_skills text,
  qualities_personality text,
  strengths_limitations text,
  other_comment text,
  conclusion text,
  expected_specific_job_assigned text,
  expected_recruitment_time text,
  decision_updated_at timestamptz,
  decision_updated_by uuid references public.app_users(app_user_id) on delete restrict,
  is_active boolean not null default true,
  is_archived boolean not null default false,
  created_at timestamptz not null default now(),
  created_by uuid references public.app_users(app_user_id) on delete restrict,
  updated_at timestamptz not null default now(),
  updated_by uuid references public.app_users(app_user_id) on delete restrict,
  version_no bigint not null default 1,
  constraint interview_report_lifecycle_ck check (
    (is_active = true and is_archived = false)
    or (is_active = false and is_archived = true)
  )
);
```

Index:
```sql
create unique index if not exists active_report_per_participant_uq
  on public.interview_reports(interview_participant_id)
  where is_active = true and is_archived = false;
```

RLS and grants:
- Enable RLS.
- `revoke all on public.interview_reports from public, anon;`
- `grant select on public.interview_reports to authenticated;`
- `grant all on public.interview_reports to postgres, service_role;`

Policies:
```sql
-- HR and root may view all; Interviewer may view their own assigned current-session reports
drop policy if exists interview_reports_select on public.interview_reports;
create policy interview_reports_select on public.interview_reports
  for select to authenticated
  using (
    private.has_permission('reports.view')
    or private.is_root_admin()
    or exists (
      select 1 from public.interview_participants ip
      join public.interviews i on i.interview_id = ip.interview_id
      join public.applications a on a.application_id = i.application_id
      where ip.interview_participant_id = interview_reports.interview_participant_id
        and ip.app_user_id = auth.uid()
        and ip.is_current = true
        and i.is_active = true
        and a.is_active = true
        and i.visible_to_interviewers = true
    )
  );
```

#### 2. `public.interview_document_logicals` Table

```sql
create table if not exists public.interview_document_logicals (
  logical_document_id uuid primary key default gen_random_uuid(),
  interview_id uuid not null references public.interviews(interview_id) on delete cascade,
  document_type_id uuid not null references public.document_types(document_type_id) on delete restrict,
  created_by uuid not null references public.app_users(app_user_id) on delete restrict,
  created_at timestamptz not null default now()
);

create index if not exists interview_document_logicals_parent_idx
  on public.interview_document_logicals(interview_id, document_type_id);
```

#### 3. `public.interview_documents` Table

```sql
create table if not exists public.interview_documents (
  interview_document_id uuid primary key default gen_random_uuid(),
  logical_document_id uuid not null references public.interview_document_logicals(logical_document_id) on delete cascade,
  storage_bucket text not null,
  storage_path text not null,
  original_filename text not null check (char_length(original_filename) <= 255),
  mime_type text not null check (mime_type in (
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-powerpoint',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'image/png','image/jpeg'
  )),
  file_size_bytes bigint not null check (file_size_bytes > 0 and file_size_bytes <= 5242880),
  checksum_sha256 text check (checksum_sha256 is null or checksum_sha256 ~ '^[0-9A-Fa-f]{64}$'),
  malware_scan_status text not null default 'CLEAN' check (malware_scan_status = 'CLEAN'),
  exif_stripped boolean,
  version_no integer not null default 1 check (version_no > 0),
  is_current boolean not null default true,
  uploaded_by uuid not null references public.app_users(app_user_id) on delete restrict,
  uploaded_at timestamptz not null default now(),
  unique(logical_document_id, version_no),
  unique(storage_bucket, storage_path)
);

create unique index if not exists interview_current_logical_document_uq
  on public.interview_documents(logical_document_id)
  where is_current = true;
```

RLS and grants for `interview_document_logicals` and `interview_documents`:
- Enable RLS on both.
- Revoke all from `public, anon`; grant `select` to `authenticated`; grant all to `postgres, service_role`.
- Policy `interview_document_logicals_select`:
  ```sql
  create policy interview_document_logicals_select on public.interview_document_logicals
    for select to authenticated
    using (
      private.has_permission('interviews.view')
      or private.is_root_admin()
      or exists (
        select 1 from public.interview_participants ip
        join public.interviews i on i.interview_id = ip.interview_id
        join public.applications a on a.application_id = i.application_id
        where ip.interview_id = interview_document_logicals.interview_id
          and ip.app_user_id = auth.uid()
          and ip.is_current = true
          and i.is_active = true
          and a.is_active = true
          and i.visible_to_interviewers = true
      )
    );
  ```
- Policy `interview_documents_select` with same logic (join through `interview_document_logicals`).

#### 4. Triggers

- `interview_reports_touch_version`: `before update on public.interview_reports` calling `private.touch_version()`.
- `interview_document_logicals_touch_version`: not required (no updated_at/version_no on logicals — skip this trigger).
- `a_report_decision_metadata_guard`: `before insert or update on public.interview_reports` calling `private.enforce_report_decision_metadata()`.

Implement `private.enforce_report_decision_metadata()` exactly as per canonical schema (lines 1269–1310 of `database_schema.sql`):
- On INSERT: if any decision field is non-empty, set `decision_updated_at = now()` and `decision_updated_by = new.updated_by`.
- On UPDATE: if any of the 3 final fields actually changed value (text comparison, null-safe), update `decision_updated_at/by`; otherwise preserve existing.
- Return `new`.

#### 5. Private Derived Views

Create exactly as specified:

```sql
create or replace view private.interview_final_decision_source
with (security_invoker = true)
as
select ci.application_id,
       ci.interview_id,
       r.interview_report_id,
       r.interview_participant_id,
       r.conclusion,
       r.expected_specific_job_assigned,
       r.expected_recruitment_time,
       r.decision_updated_at,
       r.decision_updated_by
from private.application_current_interview ci
left join lateral (
  select r1.*
  from public.interview_reports r1
  join public.interview_participants ip
    on ip.interview_participant_id = r1.interview_participant_id
  where ip.interview_id = ci.interview_id
    and ip.is_current = true
    and r1.is_active = true
    and r1.is_archived = false
    and r1.decision_updated_at is not null
    and (
      nullif(btrim(r1.conclusion), '') is not null or
      nullif(btrim(r1.expected_specific_job_assigned), '') is not null or
      nullif(btrim(r1.expected_recruitment_time), '') is not null
    )
  order by r1.decision_updated_at desc, r1.interview_report_id desc
  limit 1
) r on true;

create or replace view private.application_effective_outcome
with (security_invoker = true)
as
select ci.application_id,
       ci.interview_id,
       i.report_status_code as current_report_status_code
from private.application_current_interview ci
left join public.interviews i on i.interview_id = ci.interview_id;
```

#### 6. Participant Mutation RPCs

All participant mutations lock the Interview row first. Implement these as `SECURITY DEFINER` functions in the `private` schema with `set search_path = ''`, exposed as wrappers in `public` with execute grants to `authenticated` only.

**`public.add_interview_participant(p_interview_id, p_app_user_id, p_idempotency_key)`**:
- Permission: `interviews.manage` or root.
- Lock Interview row `FOR UPDATE`.
- Verify target user is active (`app_users.is_active = true`).
- Verify no current duplicate for that `(interview_id, app_user_id)`.
- Snapshot current `snapshot_name`, `snapshot_job_title`, `snapshot_email` from `app_users`.
- Compute `participant_order = coalesce(max(participant_order), 0) + 1` among current participants.
- If Interview is `resource_blocking`, acquire deterministic advisory locks (Candidate + Room + Interviewers including new one); re-check conflicts; fail `SCHEDULE_CONFLICT_INTERVIEWER` if blocked.
- Insert `interview_participants` row.
- Write audit log.
- Idempotent on `p_idempotency_key` — replay returns existing participant.

**`public.remove_interview_participant(p_interview_participant_id, p_expected_version)`**:
- Permission: `interviews.manage` or root.
- Lock Interview row `FOR UPDATE`, then participant row.
- Set `is_current = false`, `removed_at = now()`, bump version.
- Re-sequence `participant_order` of remaining current participants atomically (temporary collision-safe strategy: set all to negative, then set final positive values in order).
- Write audit log. Warn if report exists (return info, do not block).

**`public.readd_interview_participant(p_interview_participant_id, p_restore_mode text, p_idempotency_key)`**:
- `p_restore_mode`: `RESTORE_OLD_REPORT` or `CREATE_NEW_REPORT`.
- Lock Interview row, verify no current duplicate.
- If Interview is `resource_blocking`, acquire deterministic advisory locks including re-added Interviewer; check for `SCHEDULE_CONFLICT_INTERVIEWER`.
- `RESTORE_OLD_REPORT`: set old participant `is_current = true, removed_at = NULL`, bump version; set corresponding report `is_active = true, is_archived = false`, bump version. Write audit `RESTORE_PARTICIPANT_REPORT`.
- `CREATE_NEW_REPORT`: old participant/report stay historical/archived; create new participant row from current directory identity; assign next `participant_order`; do NOT create report (report is created lazily or by Interviewer action).
- Idempotent on `p_idempotency_key`.

**`public.reorder_interview_participants(p_interview_id, p_ordered_participant_ids uuid[], p_expected_versions bigint[])`**:
- Permission: `interviews.manage` or root.
- Lock Interview row.
- Validate `p_ordered_participant_ids` matches exactly the current active participants set.
- Validate `p_expected_versions` matches each participant's current `version_no`.
- Use two-phase reorder: set all to a large negative offset, then set final positive sequential values.
- Write audit log.

#### 7. Schedule Lifecycle RPCs

**`public.save_interview_schedule(p_interview_id, p_start_at, p_end_at, p_interview_format_id, p_room_id, p_meeting_link, p_demo_topic, p_interview_note, p_expected_version, p_idempotency_key)`**:
- Permission: `interviews.manage` or root.
- Lock Interview row. Verify `schedule_status_code != 'CONFIRMED'`; otherwise reject `INVALID_STATE`.
- Validate time range: `start_at < end_at` if both present.
- If this mutation would make the Interview `resource_blocking` (status not CANCELLED, both interval endpoints present):
  - `private.all_current_participants_selectable(p_interview_id)` must be true; otherwise `CURRENT_PARTICIPANT_INACTIVE_REASSIGN_REQUIRED`.
  - Acquire deterministic Candidate/Room/Interviewer advisory locks.
  - Re-check `[start_at, end_at)` conflicts using `private.check_interview_conflicts()`.
- Apply format normalization: if `requires_room = false`, clear `room_id`; if `requires_meeting_link = false`, clear `meeting_link`.
- Update Interview fields; bump `version_no`; write audit.
- Idempotent on `p_idempotency_key`.

**`public.change_interview_schedule_status(p_interview_id, p_schedule_status_code, p_expected_version)`**:
- Permission: `interviews.status` + `interviews.view` or root.
- Lock Interview row.
- Flexible order — no forced transition path.
- If transition would make Interview `resource_blocking` (i.e., target status is not CANCELLED, and interval endpoints are present):
  - Revalidate all current Participants active.
  - Acquire deterministic Candidate/Room/Interviewer locks.
  - Re-check conflicts.
- Historical inactive Interview Format does not block lifecycle changes when format remains referenced.
- Update `schedule_status_code`; bump version; write audit.

**`public.reschedule_confirmed_interview(p_interview_id, p_start_at, p_end_at, p_interview_format_id, p_room_id, p_meeting_link, p_expected_version, p_idempotency_key)`**:
- Permission: `interviews.manage` or root.
- Lock Interview row; verify `schedule_status_code = 'CONFIRMED'` and `expected_version`.
- Revalidate every current Participant is an Active Internal User.
- Acquire deterministic Candidate/Room/Interviewer advisory locks.
- Re-check `[start_at, end_at)` schedule conflicts.
- Update schedule time, format, room/link and set `schedule_status_code = 'AWAITING'`.
- Write Security Audit.
- On any validation, conflict, or audit failure: rollback all; original schedule and `CONFIRMED` status intact.
- Idempotent on `p_idempotency_key`.

**`public.reactivate_interview(p_interview_id, p_expected_version)`**:
- Permission: `interviews.manage` or root.
- Latest applicable round only; Application must be active; expected version.
- Revalidate all current Participants active before operationalization.
- Shared conflict framework.
- No middle-round reactivation when a later active round exists.
- Update `is_active = true`; bump version; write audit.

**`public.delete_or_inactivate_interview(p_interview_id, p_expected_version)`**:
- Permission: `interviews.manage` + `interviews.view` or root.
- Latest round only (`round_no = max(round_no)` among access-active Interviews for that Application).
- If truly unused (no business history: no participants, no documents/reports, no email outbox/history, no copy provenance): hard delete that Interview. Before hard delete, lock Interview + related `upload_reservations`; for each reservation, insert `storage_cleanup_queue` rows, cancel/remove reservation; then delete Interview. If cleanup capture fails, hard delete fails.
- Otherwise: set `is_active = false` (making all child `interview_participants.is_current` effectively `access_active = false` via Application + Interview active compound). Do NOT erase history.
- Recalculate parent Submission when current-round outcome changes.
- Write audit.

#### 8. Report RPCs

**`public.save_interviewer_report(p_interview_participant_id, p_field_patches jsonb, p_expected_version_no, p_base_values jsonb)`**:

`p_field_patches` is a JSON object with subset of: `professional_knowledge, necessary_skills, qualities_personality, strengths_limitations, other_comment, conclusion, expected_specific_job_assigned, expected_recruitment_time`.

`p_base_values` has the same keys for those fields the caller is patching.

Permission and access:
- Caller must be either:
  - An HR user with `reports.view` + `reports.edit_interviewer`; OR
  - The Interviewer who owns the report (caller's `auth.uid()` matches the `app_user_id` on the linked `interview_participant`).
- For Interviewer write: additionally require the Interview is the Current Round of its Application; the caller is a current, active participant; the Interview is `access_active` and `visible_to_interviewers = true`; AND `report_status_code` of the Interview is non-final (not `HIRED` or `REJECTED`).

Transaction:
1. Lock `interview_reports` row `FOR UPDATE`. If not found, create empty report row first, then re-lock.
2. Compare current DB values for each patched field against `base_values`:
   - If `current == base`: safe to patch.
   - If `current != base`: same-field conflict.
     - HR: reject with `STALE_VERSION` for any same-field conflict.
     - Interviewer (own report): apply owner-wins for same-field conflict on eligible fields.
3. Apply patched values; let trigger `a_report_decision_metadata_guard` manage `decision_updated_at/by` automatically.
4. Bump `version_no`, set `updated_by = caller`, `updated_at = now()`.
5. Write audit.
6. Commit.

**`public.change_report_status(p_interview_id, p_report_status_code, p_expected_version)`**:
- Permission: `reports.view` + `reports.manage_status` or root.
- This is the **single trusted mutation path** for `interviews.report_status_code`.
- Lock Current Round Interview `FOR UPDATE`.
- Lock parent Application.
- Lock parent Submission.
- Validate permission, state, version.
- Update `report_status_code`.
- Call `private.recalculate_submission_status(p_submission_id)`.
- Write audit.
- Commit.
- Does NOT change `hr_report_note`, `updated_by` (of Application), or Application HR owner.

**`public.update_hr_report_note(p_interview_id, p_hr_report_note, p_expected_version)`**:
- Permission: `reports.view` + `reports.manage_status` or root.
- Edits **only** `interviews.hr_report_note` on the Interview row.
- Lock Interview `FOR UPDATE`; verify `expected_version`.
- Update `hr_report_note`, bump `version_no`, write audit.
- Does NOT change `report_status_code`, Application `hr_owner_id`, or `interview_note`.

**`public.delete_or_inactivate_report(p_interview_report_id, p_expected_version)`**:
- Permission: `reports.view` + `reports.manage_status` or root.
- Lock report row.
- If no meaningful content/history (qualitative fields all null or empty, no decision fields, never had final state): hard delete.
- Otherwise: set `is_active = false, is_archived = true`, bump version. Write audit.
- Return stable current state or confirm deletion.

#### 9. `reserve_interview_upload` and `finalize_interview_upload`

**`public.reserve_interview_upload(p_interview_id, p_document_type_id)`**:
- Permission: `interviews.manage` + `interviews.documents` (or root).
- Validate `p_interview_id` exists (`NOT_FOUND` otherwise; reject non-existent).
- Create short-lived `upload_reservations` row with `interview_id = p_interview_id`, `expires_at = now() + interval '30 minutes'`, status `PENDING`.
- Validate `document_type_id` is active and in scope.
- Return reservation ID and presigned upload URL info (leave URL generation as a comment noting it requires Supabase Storage API call from server action; the RPC records the reservation intent).

**`public.finalize_interview_upload(p_reservation_id, p_logical_document_id_or_null, p_storage_bucket, p_storage_path, p_original_filename, p_mime_type, p_file_size_bytes, p_checksum_sha256, p_expected_logical_version_or_null)`**:
- Lock Interview + document logical header if REPLACE; validate scope/count/scan.
- For ADD: create new `interview_document_logicals` header + `interview_documents` current version.
- For REPLACE: lock logical header; verify exactly one current version; create new version; mark previous `is_current = false`, bump `version_no`.
- Enforce: malware `CLEAN`, max 5 current files per Interview, approved MIME list, ≤ 5 MB.
- Write audit; create `storage_cleanup_queue` entry for previous version path on REPLACE.

#### 10. Bulk Commands

**`public.bulk_delete_or_inactivate_interviews(p_interview_ids uuid[], p_expected_versions bigint[])`**:
- Permission: `interviews.manage` + `interviews.view` for every item.
- Sort `p_interview_ids` ascending before acquiring row locks (deterministic deadlock prevention).
- Bounded batch: reject if `array_length(p_interview_ids, 1) > 100`.
- For each: apply same current/highest-round, meaningful-history, cleanup ordering rules as single command.
- ALL_OR_NOTHING.

**`public.bulk_change_interview_schedule_status(p_interview_ids uuid[], p_target_status text, p_expected_versions bigint[])`**:
- Permission: `interviews.status` + `interviews.view` for every item.
- Sort ascending for deterministic lock ordering.
- Bounded batch: ≤ 100.
- For every transition that would make the Interview `resource_blocking`: lock, revalidate participants, acquire resource locks, check conflicts.
- ALL_OR_NOTHING.

---

### 3.2 Verification

Write and execute a comprehensive SQL test suite in `supabase/tests/interview_lifecycle_test.sql` proving:

1. `interview_reports` row creation, `active_report_per_participant_uq` unique constraint, `interview_report_lifecycle_ck` constraint.
2. `private.enforce_report_decision_metadata()` trigger: decision metadata set only when a final field changes; qualitative field update does not move `decision_updated_at`.
3. HR field-conflict: concurrent same-field patch by HR is rejected `STALE_VERSION`; disjoint fields merge.
4. Interviewer owner-wins: same-field conflict on own report, Interviewer wins.
5. `change_report_status()`: updates `report_status_code`; recalculates parent Submission; does not touch `hr_report_note`.
6. `private.interview_final_decision_source` view: returns the report with the newest `decision_updated_at`; fallback when first source clears all fields.
7. Participant add: snapshot copied correctly; duplicate rejected.
8. Participant remove: re-sequences remaining participant_order; removed participant loses `is_current`.
9. Participant re-add: RESTORE_OLD_REPORT restores report active state; CREATE_NEW_REPORT creates new participant leaving old archived.
10. Participant reorder: unique `participant_order` maintained without transient collision.
11. `save_interview_schedule()`: blocked by CONFIRMED status; resource locks prevent Interviewer conflict.
12. `change_interview_schedule_status()`: CANCELLED→operational re-runs conflict check; rejects inactive participant.
13. `reschedule_confirmed_interview()`: locks resources; rolls back on conflict; transitions to AWAITING.
14. `delete_or_inactivate_interview()`: latest-round-only enforcement; cleanup-capture ordering for hard delete with upload reservations.
15. `interview_document_logicals` and `interview_documents` creation; `interview_current_logical_document_uq` uniqueness; max 5 current files enforced.
16. RLS for `interview_reports`: HR with `reports.view` sees all; current participant sees own session when visible; non-participant cannot see.
17. RLS for `interview_documents`: current participant + visible can select.
18. Bulk schedule status: ALL_OR_NOTHING — one inactive participant aborts entire batch.

---

## 4. Acceptance Criteria

**INTERVIEW-LIFECYCLE-001: VERIFIED** requires ALL of:

- `interview_reports`, `interview_document_logicals`, `interview_documents` tables exist with all canonical columns, constraints, and indexes.
- `private.enforce_report_decision_metadata` trigger fires correctly.
- `private.interview_final_decision_source` and `private.application_effective_outcome` views exist and are correct.
- All participant mutation RPCs (`add`, `remove`, `readd`, `reorder`) are implemented and tested.
- All schedule lifecycle RPCs (`save`, `change_status`, `reschedule_confirmed`, `reactivate`, `delete_or_inactivate`) are implemented and tested.
- `save_interviewer_report` with field-aware merge is implemented and tested.
- `change_report_status`, `update_hr_report_note`, `delete_or_inactivate_report` are implemented and tested.
- `reserve_interview_upload`, `finalize_interview_upload` are implemented and tested.
- `bulk_delete_or_inactivate_interviews`, `bulk_change_interview_schedule_status` are implemented and tested.
- RLS policies for `interview_reports`, `interview_document_logicals`, `interview_documents` pass adversarial tests.
- `supabase db reset --local`: PASS (migration replay from zero).
- All tests in `supabase/tests/interview_lifecycle_test.sql`: PASS.

---

## 5. Evidence Requirements

```text
EVIDENCE_DELTA: INTERVIEW-LIFECYCLE-001
CHECKS:
  - supabase db reset --local: PASS
  - interview_lifecycle_test.sql: PASS
  - prompt_reviewed: PASS
  - implementation_reviewed: PASS (independent reviewer)
  - github_ci: VERIFIED (Integration CI exact SHA; PASS)
```

---

## 6. Non-Goals

- Do NOT implement application-layer Server Actions or React UI in this task.
- Do NOT implement the HR Application Inbox read RPCs (already done in S03).
- Do NOT implement copy_interview_schedule RPC (that is TASK-S04-003 scope).
- Do NOT implement create_or_update_application, reactivate_application, delete_or_inactivate_application (already done in S03).
- Do NOT create or modify any files outside:
  - `supabase/migrations/20260906070000_interview_lifecycle_commands.sql`
  - `supabase/tests/interview_lifecycle_test.sql`
- Do NOT modify existing migration files.
- Do NOT touch main branch.
- Do NOT deploy to production.
