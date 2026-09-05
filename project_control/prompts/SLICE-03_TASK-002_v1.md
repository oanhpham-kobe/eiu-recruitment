# EIU Recruitment — Executor Prompt
## TASK-S03-002 — Application creation, assignment, and lifecycle commands
### Prompt version: SLICE-03_TASK-002_v1

## 0. Execution Control

```text
SOURCE_BASELINE: Full Handover v1.17
SOURCE_SHA256: 0b39c3615dd5b34e998527a1d273e0b846458c7bd4170be46c9bb670bfcb3498
BUSINESS_STATUS: Business Logic Core v1.2 = FROZEN
TECHNICAL_STATUS: Technical Architecture v1.17 = TECHNICAL SPECIFICATION FROZEN
TASK_SCOPE: TASK-S03-002 Application creation, assignment, and lifecycle commands Only
WORKTREE: D:/orca/recruitment/TASK-S03-002-app-lifecycle
BRANCH: oanhpham-kobe/TASK-S03-002-app-lifecycle
BASE_BRANCH: autonomy/continuous-integration-20260905-01
BASE_HEAD: d5d681d2f04b59a7d72b2f6787c5ee233db81f42
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
    - supabase: "application lifecycle commands, auto-round 1 allocation, server action/command runner binding"
    - supabase-postgres-best-practices: "authoring secure RPC functions with search_path='', deterministic lock hierarchy (submissions -> applications -> interviews), optimistic versioning, structurally empty default round predicate"
    - security-review: "authorizing applications.create/manage/delete and submissions.edit, immutable candidate email in HR updates, durable application identity uniqueness enforcement, active vs inactive duplicate handling"
    - tdd: "risk-based unit and integration test suite covering application creation, auto-round 1, duplicate identity handling, hard delete vs inactivation, and HR note editing"
  GRAPH_ROUTE: DIRECT_SOURCE_LSP_ONLY
  GRAPH_ROUTE_REASON: "Localized database schema migration, RPC lifecycle commands, and server command runner wrappers directly mapped to review pack specifications"
  PRINCIPLE_PROFILE: "APPLICATION_LIFECYCLE_AND_STRUCTURAL_INTEGRITY"
  EVIDENCE_DELTA: "APP-LIFECYCLE-001"
```

---

## 2. Canonical Source References

- `recruitment_webapp/review_pack/37_BACKEND_COMMAND_CONTRACTS.md` (§4 Candidate Submission commands: `update_submission_by_hr`; §5 Applications: `create_or_update_application`, `delete_or_inactivate_application`)
- `recruitment_webapp/review_pack/40_DATABASE_INVARIANTS.md` (§Application identity invariants, §Structurally empty default round invariants)
- `recruitment_webapp/review_pack/13_ACCEPTANCE_CRITERIA_AND_TEST_CASES.md` (`AC-APP-CREATE-01`, `AC-APP-DUP-01`, `AC-APP-DEL-01`, `AC-APP-INACT-01`, `AC-HR-NOTE-01`)
- `recruitment_webapp/review_pack/database_schema.sql` (lines 448-515, 1252-1267: `applications`, `interviews`, `application_durable_identity_uq`)
- `recruitment_webapp/review_pack/command_registry.yaml` (`create_or_update_application`, `delete_or_inactivate_application`, `update_submission_by_hr`)

---

## 3. Implementation Specification

### 3.1 Migration File: `supabase/migrations/20260905110000_application_lifecycle_commands.sql`

#### 1. Structurally Empty Default Round Predicate
- `private.is_structurally_empty_default_round(p_interview_id uuid) returns boolean`:
  - `SECURITY DEFINER SET search_path = ''`.
  - Checks if interview row exists:
    * `round_no = 1`
    * `schedule_status_code = 'AVAILABLE'` and `report_status_code = 'INTERVIEW_SCHEDULING'`
    * `start_at IS NULL` and `end_at IS NULL`
    * `notes IS NULL` and `hr_report_note IS NULL`
    * `copied_from_interview_id IS NULL` and not referenced by another interview's `copied_from_interview_id`
    * No participants in `interview_participants` (or 0 rows)
    * No reports in `interview_reports` (or 0 rows)
    * No documents in `interview_document_logicals` (or 0 rows)
    * No pending upload reservations in `upload_reservations`
  - Returns `true` if empty default round; `false` otherwise.
  - Revoked from `public, anon, authenticated`; granted to `postgres, service_role`.

#### 2. `public.create_or_update_application(...)`
- Signature:
  ```sql
  public.create_or_update_application(
    p_submission_id uuid,
    p_unit_id uuid,
    p_department_team_id uuid default null,
    p_position_id uuid,
    p_hr_owner_id uuid,
    p_idempotency_key uuid default gen_random_uuid()
  ) returns jsonb
  ```
- `SECURITY DEFINER SET search_path = ''`.
- **Authorization**:
  Requires `private.has_permission('applications.create') OR private.has_permission('applications.manage') OR private.is_root_admin()`.
  If unauthorized: `{ success: false, error_code: 'FORBIDDEN', message: 'Permission applications.create or applications.manage required' }`.
- **Hierarchy & HR Owner Validations**:
  - `unit_id` must exist in `public.organizational_units` and be active.
  - If `p_department_team_id` provided: must exist in `public.department_teams`, be active, and have `unit_id = p_unit_id`.
  - `position_id` must exist in `public.positions`, be active, have `unit_id = p_unit_id`, and match `department_team_id`.
  - `p_hr_owner_id` must exist in `public.app_users` and have `is_active = true`.
- **Deterministic Lock Sequence**:
  1. Lock parent submission (Lock 1):
     `SELECT submission_id, candidate_id, status_code FROM public.submissions WHERE submission_id = p_submission_id FOR UPDATE`.
     If not found: `{ success: false, error_code: 'NOT_FOUND', message: 'Submission not found' }`.
  2. Check Durable Identity Uniqueness (Lock 2):
     ```sql
     select * into v_existing_app
     from public.applications
     where submission_id = p_submission_id
       and unit_id = p_unit_id
       and coalesce(department_team_id, '00000000-0000-0000-0000-000000000000'::uuid) =
           coalesce(p_department_team_id, '00000000-0000-0000-0000-000000000000'::uuid)
       and position_id = p_position_id
     for update;
     ```
     - If active duplicate exists (`v_existing_app.is_active = true`):
       Updates existing application: `hr_owner_id = p_hr_owner_id`, `version_no = version_no + 1`, `updated_at = clock_timestamp()`.
     - If inactive duplicate exists (`v_existing_app.is_active = false`):
       Returns `{ success: false, error_code: 'ALREADY_EXISTS_INACTIVE', message: 'An inactive application already exists for this position. Use reactivate instead.' }`.
     - If no duplicate exists:
       Inserts `public.applications`:
       `submission_id = p_submission_id`, `unit_id = p_unit_id`, `department_team_id = p_department_team_id`, `position_id = p_position_id`, `hr_owner_id = p_hr_owner_id`, `is_active = true`, `version_no = 1`.
       Creates auto-created default **Round 1** in `public.interviews`:
       `application_id = v_app_id`, `round_no = 1`, `schedule_status_code = 'AVAILABLE'`, `report_status_code = 'INTERVIEW_SCHEDULING'`, `is_active = true`, `version_no = 1`.
- **Submission Status Recalculation**:
  Calls `perform public.recalculate_submission_status(p_submission_id);`.
- Returns `{ success: true, data: { application_id, submission_id, is_active, version_no, round1_interview_id } }`.

#### 3. `public.delete_or_inactivate_application(...)`
- Signature:
  ```sql
  public.delete_or_inactivate_application(
    p_application_id uuid
  ) returns jsonb
  ```
- `SECURITY DEFINER SET search_path = ''`.
- **Authorization**:
  Requires `private.has_permission('applications.delete') OR private.is_root_admin()`.
  If unauthorized: `{ success: false, error_code: 'FORBIDDEN', message: 'Permission applications.delete required' }`.
- **Deterministic Lock Sequence**:
  1. Lock application row (Lock 1):
     `SELECT * INTO v_app FROM public.applications WHERE application_id = p_application_id FOR UPDATE`.
     If not found: `{ success: false, error_code: 'NOT_FOUND', message: 'Application not found' }`.
  2. Lock parent submission (Lock 2):
     `SELECT submission_id FROM public.submissions WHERE submission_id = v_app.submission_id FOR UPDATE`.
  3. Inspect child interviews:
     Count total rounds: `SELECT count(*) INTO v_round_count FROM public.interviews WHERE application_id = p_application_id`.
     Get Round 1: `SELECT * INTO v_round1 FROM public.interviews WHERE application_id = p_application_id AND round_no = 1`.
  4. Evaluate Structural Emptiness:
     If `v_round_count = 1` AND `private.is_structurally_empty_default_round(v_round1.interview_id)`:
       - Truly unused default Round 1: hard delete round 1 and application row atomically.
       - Action: `'DELETED'`.
     Else:
       - Application has business history or multiple rounds:
       - Set `is_active = false`, `updated_at = clock_timestamp()` on `public.applications`.
       - Set `is_active = false` on all child interviews.
       - Action: `'INACTIVATED'`.
- **Submission Status Recalculation**:
  Calls `perform public.recalculate_submission_status(v_app.submission_id);`.
- Returns `{ success: true, data: { application_id: p_application_id, action: v_action, submission_id: v_app.submission_id } }`.

#### 4. `public.update_submission_by_hr(...)`
- Signature:
  ```sql
  public.update_submission_by_hr(
    p_submission_id uuid,
    p_hr_note text default null,
    p_expected_version bigint default null
  ) returns jsonb
  ```
- `SECURITY DEFINER SET search_path = ''`.
- **Authorization**:
  Requires `private.has_permission('submissions.edit') OR private.is_root_admin()`.
  If unauthorized: `{ success: false, error_code: 'FORBIDDEN', message: 'Permission submissions.edit required' }`.
- **Lock & Optimistic Concurrency**:
  Lock submission `FOR UPDATE`:
  `SELECT * INTO v_sub FROM public.submissions WHERE submission_id = p_submission_id FOR UPDATE`.
  If not found: `{ success: false, error_code: 'NOT_FOUND', message: 'Submission not found' }`.
  If `p_expected_version IS NOT NULL` AND `v_sub.version_no <> p_expected_version`:
  returns `{ success: false, error_code: 'STALE_VERSION', message: 'Submission version mismatch' }`.
- **Update HR Note**:
  Candidate verified email and identity are completely immutable.
  Updates `hr_note = p_hr_note`, `version_no = version_no + 1`, `updated_at = clock_timestamp()`.
- **Profile Cache Refresh**:
  `perform private.refresh_candidate_current_profile(v_sub.candidate_id);`.
- Returns `{ success: true, data: { submission_id: p_submission_id, hr_note: p_hr_note, version_no: v_sub.version_no + 1 } }`.

---

### 3.2 Web Command Layer: `web/src/lib/commands/application-lifecycle.ts`

- Implement typed commands using `createCommandRunner`:
  1. `createOrUpdateApplication(input, deps)`:
     - Inputs: `submissionId`, `unitId`, `departmentTeamId`, `positionId`, `hrOwnerId`, `idempotencyKey`.
     - Validates UUID formats.
     - Authorizes actor (`applications.create` or `applications.manage` or `ROOT_ADMIN`).
     - Calls `public.create_or_update_application` RPC.
  2. `deleteOrInactivateApplication(input, deps)`:
     - Input: `applicationId`.
     - Authorizes actor (`applications.delete` or `ROOT_ADMIN`).
     - Calls `public.delete_or_inactivate_application` RPC.
  3. `updateSubmissionByHr(input, deps)`:
     - Inputs: `submissionId`, `hrNote`, `expectedVersion`.
     - Authorizes actor (`submissions.edit` or `ROOT_ADMIN`).
     - Calls `public.update_submission_by_hr` RPC.
- Type definitions, error mapping to `CommandErrorCode`.

---

### 3.3 Verification Tests: `web/src/__tests__/application-lifecycle.test.ts`

- Test suite verifying:
  1. `AC-APP-CREATE-01`: Create application allocates default Round 1 with AVAILABLE and INTERVIEW_SCHEDULING.
  2. `AC-APP-DUP-01`: Active duplicate identity updates existing application with version bump; inactive duplicate returns `ALREADY_EXISTS_INACTIVE`.
  3. `AC-APP-DEL-01`: Deleting structurally empty default Round 1 performs hard delete of round and application atomically.
  4. `AC-APP-INACT-01`: Application with business usage (participants, schedule, or reports) inactivates application and child rounds instead of deleting.
  5. `AC-APP-RECALC-01`: Application creation triggers submission status recalculation to `PROCESSED`.
  6. `AC-APP-RECALC-02`: Application deletion triggers submission status recalculation back to `READ`.
  7. `AC-HR-NOTE-01`: `update_submission_by_hr` edits only `hr_note`, bumps version, and preserves candidate email immutability.
  8. `AC-HR-NOTE-STALE`: Version mismatch in `update_submission_by_hr` returns `STALE_VERSION`.
  9. `AC-APP-AUTH-01`: Unauthorized caller without required permissions rejected with `FORBIDDEN`.
  10. `AC-APP-HIERARCHY-01`: Mismatched department_team or position hierarchy rejected.

---

## 4. Acceptance & Verification Contract

1. `npm run typecheck` in `web/` PASS with 0 errors.
2. `npm run lint` in `web/` PASS with 0 errors.
3. `npm run build` in `web/` PASS.
4. `npm run test` in `web/` PASS (all existing + new tests green).
5. Clean local migration replay test on ephemeral test port PASS.
6. Secret scan PASS.
7. Git diff clean, exactly one commit on `oanhpham-kobe/TASK-S03-002-app-lifecycle`.
