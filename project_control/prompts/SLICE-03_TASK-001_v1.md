# EIU Recruitment — Executor Prompt
## TASK-S03-001 — Application Inbox status calculation schema and manual status transition commands
### Prompt version: SLICE-03_TASK-001_v1

## 0. Execution Control

```text
SOURCE_BASELINE: Full Handover v1.17
SOURCE_SHA256: 0b39c3615dd5b34e998527a1d273e0b846458c7bd4170be46c9bb670bfcb3498
BUSINESS_STATUS: Business Logic Core v1.2 = FROZEN
TECHNICAL_STATUS: Technical Architecture v1.17 = TECHNICAL SPECIFICATION FROZEN
TASK_SCOPE: TASK-S03-001 Application Inbox status calculation schema and manual status transition commands Only
WORKTREE: D:/orca/recruitment/TASK-S03-001-inbox-status
BRANCH: oanhpham-kobe/TASK-S03-001-inbox-status
BASE_BRANCH: autonomy/continuous-integration-20260905-01
BASE_HEAD: e2222c96cb24ee2170ffa1b52358261c270018f6
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
    - supabase: "defining applications/interviews schema, RLS policies, PostgREST grant separation, server client integration"
    - supabase-postgres-best-practices: "authoring secure RPC functions with search_path='', deterministic lock hierarchy (candidates -> submissions -> applications) preventing deadlocks, optimistic versioning, permission prerequisites check"
    - security-review: "authorizing submissions.view and submissions.status, conditional mutation on open_submission, blocking manual assignment of system-derived statuses (PROCESSED/DONE/CLOSED), historical submission status read-only protection, active Application guard preventing manual NEW/READ"
    - tdd: "risk-based unit and integration test suite covering status recalculation rules, conditional open mutations, permission boundaries, and concurrency serialization"
  GRAPH_ROUTE: DIRECT_SOURCE_LSP_ONLY
  GRAPH_ROUTE_REASON: "Localized database schema migration, RPC transition commands, and server command runner wrappers directly mapped to review pack specifications"
  PRINCIPLE_PROFILE: "SUBMISSION_STATUS_AND_INBOX_SECURITY"
  EVIDENCE_DELTA: "INBOX-STATUS-001"
```

---

## 2. Canonical Source References

- `recruitment_webapp/review_pack/04_HR_APPLICATION_INBOX.md` (§4 Submission status: NEW, READ, PROCESSED, DONE, CLOSED; conditional open NEW $\rightarrow$ READ; manual NEW $\leftrightarrow$ READ)
- `recruitment_webapp/review_pack/37_BACKEND_COMMAND_CONTRACTS.md` (§4 Candidate Submission commands: `open_submission`, `set_submission_manual_status`, `recalculate_submission_status`)
- `recruitment_webapp/review_pack/40_DATABASE_INVARIANTS.md` (§Application identity invariants, §Submission status recalculation invariants)
- `recruitment_webapp/review_pack/13_ACCEPTANCE_CRITERIA_AND_TEST_CASES.md` (`AC-STAT-01`, `AC-STAT-02`, `AC-OPEN-SUB-01`, `AC-OPEN-SUB-02`, `AC-HIST-SUB-01`)
- `recruitment_webapp/review_pack/database_schema.sql` (lines 448-505: `applications`, `interviews`, `application_durable_identity_uq`)
- `recruitment_webapp/review_pack/command_registry.yaml` (`open_submission`, `set_submission_manual_status`, `recalculate_submission_status`)

---

## 3. Implementation Specification

### 3.1 Migration File: `supabase/migrations/20260905100000_application_schema_and_status_commands.sql`

#### 1. Schema Definitions: `applications` & `interviews`
- **`public.applications` table**:
  ```sql
  create table if not exists public.applications (
    application_id uuid primary key default gen_random_uuid(),
    submission_id uuid not null references public.submissions(submission_id) on delete restrict,
    unit_id uuid not null references public.organizational_units(unit_id) on delete restrict,
    department_team_id uuid references public.department_teams(department_team_id) on delete restrict,
    position_id uuid not null references public.positions(position_id) on delete restrict,
    hr_owner_id uuid not null references public.app_users(app_user_id) on delete restrict,
    is_active boolean not null default true,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    updated_by uuid references public.app_users(app_user_id) on delete restrict,
    version_no bigint not null default 1
  );

  -- Zero UUID sentinel used for NULL-team durable identity uniqueness
  create unique index if not exists application_durable_identity_uq
    on public.applications(
      submission_id,
      unit_id,
      coalesce(department_team_id, '00000000-0000-0000-0000-000000000000'::uuid),
      position_id
    );

  create index if not exists applications_submission_idx on public.applications(submission_id);
  create index if not exists applications_hr_owner_idx on public.applications(hr_owner_id) where is_active = true;
  ```

- **`public.interviews` table**:
  ```sql
  create table if not exists public.interviews (
    interview_id uuid primary key default gen_random_uuid(),
    application_id uuid not null references public.applications(application_id) on delete restrict,
    round_no integer not null check (round_no > 0),
    demo_topic text,
    start_at timestamptz,
    end_at timestamptz,
    interview_format_id uuid references public.interview_formats(interview_format_id) on delete restrict,
    room_id uuid references public.rooms(room_id) on delete restrict,
    meeting_link text,
    schedule_status_code text not null default 'AVAILABLE'
      check (schedule_status_code in ('AVAILABLE','SCHEDULED','AWAITING','CONFIRMED','CANCELLED')),
    report_status_code text not null default 'INTERVIEW_SCHEDULING'
      check (report_status_code in ('INTERVIEW_SCHEDULING','AWAITING_INTERVIEW','WAITING_FOR_REPORT','REPORT_SUBMITTED','FOLLOW_UP','ON_HOLD','HIRED','REJECTED')),
    notes text,
    hr_report_note text,
    copied_from_interview_id uuid references public.interviews(interview_id) on delete set null,
    is_active boolean not null default true,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    version_no bigint not null default 1,
    unique(application_id, round_no)
  );

  create index if not exists interviews_application_idx on public.interviews(application_id);
  create index if not exists interviews_active_idx on public.interviews(is_active);
  ```

- **RLS & Grants**:
  - Enable RLS on `public.applications` and `public.interviews`.
  - Grants: Revoke all from `public`, `anon`. Grant `select` to `authenticated` (governed by RLS). Grant `all` to `postgres`, `service_role`.
  - Policies:
    * `applications_select`: internal staff with `submissions.view` or `applications.view` or `is_root_admin()`.
    * `interviews_select`: internal staff with `interviews.view` or `is_root_admin()`.

#### 2. Authoritative Status Recalculation RPC: `public.recalculate_submission_status(p_submission_id uuid)`
- `SECURITY DEFINER SET search_path = ''`.
- **Preconditions & Row Lock**:
  Locks parent `public.submissions` row `FOR UPDATE`:
  `SELECT status_code INTO v_current_status FROM public.submissions WHERE submission_id = p_submission_id FOR UPDATE`.
  If not found: `{ success: false, error_code: 'NOT_FOUND', message: 'Submission not found' }`.
- **Status Derivation Rules**:
  1. Count active applications:
     `SELECT count(*) INTO v_active_apps FROM public.applications WHERE submission_id = p_submission_id AND is_active = true`.
  2. If `v_active_apps = 0`:
     - If `v_current_status in ('PROCESSED', 'DONE', 'CLOSED')`: sets `v_new_status := 'READ'`.
     - Else (`NEW` or `READ`): preserves existing manual status (`v_new_status := v_current_status`).
  3. If `v_active_apps > 0`:
     - Check outcomes of active applications (via latest interview report status):
       * If ANY active application has a current interview with `report_status_code = 'HIRED'`: `v_new_status := 'DONE'`.
       * Else if ALL active applications have their latest interview with `report_status_code = 'REJECTED'`: `v_new_status := 'CLOSED'`.
       * Else: `v_new_status := 'PROCESSED'`.
- **Atomic Update**:
  If `v_new_status <> v_current_status`:
  `UPDATE public.submissions SET status_code = v_new_status, updated_at = clock_timestamp() WHERE submission_id = p_submission_id;`
- Returns `{ success: true, data: { submission_id: p_submission_id, status_code: v_new_status, previous_status_code: v_current_status } }`.

#### 3. Conditional Open Submission RPC: `public.open_submission(p_submission_id uuid)`
- `SECURITY DEFINER SET search_path = ''`.
- **Authorization**:
  Requires `private.has_permission('submissions.view') OR private.is_root_admin()`.
  If unauthorized: `{ success: false, error_code: 'FORBIDDEN', message: 'Permission submissions.view required' }`.
- **Conditional Mutation**:
  Inspects submission:
  If caller ALSO has `private.has_permission('submissions.status') OR private.is_root_admin()`:
    - Locks row `FOR UPDATE`.
    - If `status_code = 'NEW'`:
      `UPDATE public.submissions SET status_code = 'READ', updated_at = clock_timestamp() WHERE submission_id = p_submission_id;`
- **Read Response**:
  Returns submission details, full name, email, phone, date of birth, gender, address, candidate notes, current status, submitted_at, version_no.

#### 4. Deterministic Manual Status Transition RPC: `public.set_submission_manual_status(...)`
- Signature:
  ```sql
  public.set_submission_manual_status(
    p_candidate_id uuid,
    p_status_code text,
    p_expected_latest_submission_id uuid,
    p_expected_version bigint,
    p_idempotency_key uuid default gen_random_uuid()
  ) returns jsonb
  ```
- `SECURITY DEFINER SET search_path = ''`.
- **Authorization**:
  Requires `private.has_permission('submissions.status') OR private.is_root_admin()`.
  If unauthorized: `{ success: false, error_code: 'FORBIDDEN', message: 'Permission submissions.status required' }`.
- **Allowed Status Guard (`AC-STAT-01`)**:
  `p_status_code` must be `'NEW'` or `'READ'`.
  If caller requests `'PROCESSED'`, `'DONE'`, or `'CLOSED'`:
  returns `{ success: false, error_code: 'INVALID_ACTION', message: 'PROCESSED, DONE, and CLOSED are system-derived only' }`.
- **Deterministic Lock Sequence**:
  1. Lock candidate row (Lock 1):
     `SELECT candidate_id FROM public.candidates WHERE candidate_id = p_candidate_id FOR UPDATE`.
     If not found: `{ success: false, error_code: 'NOT_FOUND', message: 'Candidate not found' }`.
  2. Resolve latest submission (Lock 2):
     `SELECT * INTO v_latest FROM public.submissions WHERE candidate_id = p_candidate_id ORDER BY submitted_at DESC, submission_id DESC LIMIT 1 FOR UPDATE`.
     If not found: `{ success: false, error_code: 'NOT_FOUND', message: 'No submissions found for candidate' }`.
  3. Historical Submission Guard (`AC-HIST-SUB-01`):
     If `v_latest.submission_id <> p_expected_latest_submission_id`:
     returns `{ success: false, error_code: 'HISTORICAL_SUBMISSION_READ_ONLY', message: 'Only the latest submission of a candidate may be manually changed' }`.
  4. Optimistic Version Guard:
     If `v_latest.version_no <> p_expected_version`:
     returns `{ success: false, error_code: 'STALE_VERSION', message: 'Submission version mismatch' }`.
  5. Active Application Guard:
     `SELECT count(*) INTO v_active_apps FROM public.applications WHERE submission_id = v_latest.submission_id AND is_active = true`.
     If `v_active_apps > 0`:
     returns `{ success: false, error_code: 'INVALID_STATE', message: 'Neither NEW nor READ may be written manually while any active Application exists' }`.
- **Status Mutation**:
  ```sql
  v_new_version := v_latest.version_no + 1;
  update public.submissions
  set
    status_code = p_status_code,
    version_no = v_new_version,
    updated_at = clock_timestamp()
  where submission_id = v_latest.submission_id;
  ```
- Returns `{ success: true, data: { submission_id: v_latest.submission_id, status_code: p_status_code, version_no: v_new_version } }`.

---

### 3.2 Web Command Layer: `web/src/lib/commands/submission-status.ts`

- Implement typed commands using `createCommandRunner`:
  1. `openSubmission(input, deps)`:
     - Input: `{ submissionId: string }`.
     - Validates `submissionId` UUID.
     - Authorizes actor (`submissions.view` or `ROOT_ADMIN`).
     - Calls `public.open_submission` RPC.
  2. `setSubmissionManualStatus(input, deps)`:
     - Input: `{ candidateId: string, statusCode: "NEW" | "READ", expectedLatestSubmissionId: string, expectedVersion: number, idempotencyKey?: string }`.
     - Validates inputs, rejects non-NEW/READ statuses at validation layer.
     - Authorizes actor (`submissions.status` or `ROOT_ADMIN`).
     - Calls `public.set_submission_manual_status` RPC.
  3. `recalculateSubmissionStatus(input, deps)`:
     - Input: `{ submissionId: string }`.
     - Validates `submissionId` UUID.
     - Calls `public.recalculate_submission_status` RPC.
- Type definitions, error mapping to `CommandErrorCode` (`FORBIDDEN`, `NOT_FOUND`, `INVALID_STATE`, `STALE_VERSION`, `VALIDATION_ERROR`).

---

### 3.3 Verification Tests: `web/src/__tests__/submission-status.test.ts`

- Test suite verifying:
  1. `AC-OPEN-SUB-01`: View-only HR (`submissions.view` without `submissions.status`) opens `NEW` submission $\rightarrow$ status remains `NEW` (pure read-only).
  2. `AC-OPEN-SUB-02`: Full HR (`submissions.view + submissions.status`) opens `NEW` submission $\rightarrow$ atomically transitions `NEW` $\rightarrow$ `READ`.
  3. `AC-OPEN-SUB-03`: Unauthorized caller without `submissions.view` opening submission rejected with `FORBIDDEN`.
  4. `AC-STAT-01`: Direct manual request to set `PROCESSED`, `DONE`, or `CLOSED` rejected with `INVALID_ACTION`.
  5. `AC-STAT-02`: Manual transition `NEW` $\leftrightarrow$ `READ` succeeds when no active Application exists, bumping `version_no`.
  6. `AC-STAT-03`: Manual transition `NEW` $\leftrightarrow$ `READ` rejected with `INVALID_STATE` when an active Application exists.
  7. `AC-HIST-SUB-01`: Attempt to change historical child submission status rejected with `HISTORICAL_SUBMISSION_READ_ONLY`.
  8. `AC-STAT-STALE-01`: Version mismatch in `set_submission_manual_status` rejected with `STALE_VERSION`.
  9. `AC-RECALC-01`: Recalculation with 0 applications preserves existing manual `NEW` or `READ`.
  10. `AC-RECALC-02`: Recalculation after removing last application from `PROCESSED`/`DONE`/`CLOSED` returns `READ`.
  11. `AC-RECALC-03`: Recalculation with active applications returns `PROCESSED` when in progress.
  12. `AC-RECALC-04`: Recalculation with any active application `HIRED` returns `DONE`.
  13. `AC-RECALC-05`: Recalculation with all active applications `REJECTED` returns `CLOSED`.
  14. `AC-STAT-CONCURRENCY-01`: Two concurrent status recalculations serialize safely on parent submission lock.

---

## 4. Acceptance & Verification Contract

1. `npm run typecheck` in `web/` PASS with 0 errors.
2. `npm run lint` in `web/` PASS with 0 errors.
3. `npm run build` in `web/` PASS.
4. `npm run test` in `web/` PASS (all existing + new tests green).
5. Clean local migration replay test on ephemeral test port PASS.
6. Secret scan PASS.
7. Git diff clean, exactly one commit on `oanhpham-kobe/TASK-S03-001-inbox-status`.
