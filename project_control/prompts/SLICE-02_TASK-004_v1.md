# EIU Recruitment — Executor Prompt
## TASK-S02-004 — Candidate Submission transactional commands (submit and update)
### Prompt version: SLICE-02_TASK-004_v1

## 0. Execution Control

```text
SOURCE_BASELINE: Full Handover v1.17
SOURCE_SHA256: 0b39c3615dd5b34e998527a1d273e0b846458c7bd4170be46c9bb670bfcb3498
BUSINESS_STATUS: Business Logic Core v1.2 = FROZEN
TECHNICAL_STATUS: Technical Architecture v1.17 = TECHNICAL SPECIFICATION FROZEN
TASK_SCOPE: TASK-S02-004 Candidate Submission transactional commands (submit and update)
WORKTREE: D:/orca/recruitment/TASK-S02-004-candidate-submission
BRANCH: oanhpham-kobe/TASK-S02-004-candidate-submission
BASE_BRANCH: autonomy/continuous-integration-20260905-01
BASE_HEAD: 844516a36614f3b73fc6e7c77ece481ab648f30a
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
    - supabase: "atomic database RPC commands, outbox enqueueing, SSR server client integration"
    - supabase-postgres-best-practices: "authoring transactional RPCs with search_path='', canonical auth.uid()+candidates lookup distinguishing UNAUTHENTICATED vs USER_INACTIVE, deterministic lock hierarchy (candidates -> sessions -> submissions -> reservations) preventing deadlocks, optimistic versioning, post-lock status re-reads, child snapshot atomicity"
    - security-review: "authorizing candidate owner, immutable candidate verified email, server-pinned privacy notice acknowledgement, plan validation enforcing CLEAN scan and CV requirement before materialization, strict target submission NEW invariant for edits"
    - tdd: "risk-based unit and integration test suite covering state transitions, concurrency serialization, optimistic locking, and failure modes"
  GRAPH_ROUTE: DIRECT_SOURCE_LSP_ONLY
  GRAPH_ROUTE_REASON: "Localized database RPC commands, schema triggers, and server command runner wrappers directly mapped to review pack specifications"
  PRINCIPLE_PROFILE: "SUBMISSION_TRANSACTION_AND_CONCURRENCY"
  EVIDENCE_DELTA: "CANDIDATE-SUBMISSION-001"
```

---

## 2. Canonical Source References

- `recruitment_webapp/review_pack/37_BACKEND_COMMAND_CONTRACTS.md` (§4 Candidate Submission commands: `submit_candidate_submission`, `update_candidate_submission`)
- `recruitment_webapp/review_pack/40_DATABASE_INVARIANTS.md` (§Candidate Form Session invariants, §Submission immutability and versioning invariants)
- `recruitment_webapp/review_pack/41_STORAGE_AND_UPLOAD_SECURITY.md` (§Candidate staged upload/edit protocol: steps 6-7, plan validation, current version switching)
- `recruitment_webapp/review_pack/13_ACCEPTANCE_CRITERIA_AND_TEST_CASES.md` (`AC-UP-01`, `AC-UP-02`, `AC-UP-03`, `AC-UP-04`, `AC-UP-05`, `AC-UP-06`, `AC-DOC-TARGET-01`, `AC-DOC-TARGET-02`, `AC-DOC-TARGET-03`, `AC-DOC-TARGET-04`)
- `recruitment_webapp/review_pack/database_schema.sql` (lines 240-375, 614-648, 884-1016, 1252-1267: `submissions`, `submission_education`, `submission_work_experiences`, `submission_activities`, `submission_document_logicals`, `submission_documents`, `privacy_acknowledgements`, `email_outbox`, `private.validate_candidate_form_document_plan`, `private.refresh_candidate_current_profile`)
- `recruitment_webapp/review_pack/command_registry.yaml` (`submit_candidate_submission`, `update_candidate_submission`)

---

## 3. Implementation Specification

### 3.1 Migration File: `supabase/migrations/20260905090000_candidate_submission_commands.sql`

#### 1. Candidate Profile Cache Helper
- Ensure `private.refresh_candidate_current_profile(p_candidate_id uuid)` exists and operates correctly:
  - `SECURITY DEFINER SET search_path = ''`.
  - Locks candidate row `FOR UPDATE`.
  - Queries latest surviving submission by `submitted_at DESC, submission_id DESC LIMIT 1`.
  - Updates `public.candidates`: `current_full_name = s.full_name`, `current_phone = s.phone`, `last_submission_at = s.submitted_at`.
  - Revoked from `public`, `anon`, `authenticated`; granted to `postgres`, `service_role`.

#### 2. Deterministic Lock Hierarchy
Across both submission commands:
1. `candidates` (`FOR UPDATE`): locks candidate identity.
2. `candidate_form_sessions` (`FOR UPDATE`): locks form session.
3. `submissions` (`FOR UPDATE`, when `mode_code = 'EDIT_SUBMISSION'`): locks target submission.
4. `candidate_form_document_changes` & `upload_reservations` (`FOR UPDATE`): locks staged changes and backing reservations.

#### 3. `public.submit_candidate_submission(...)`
- Signature:
  ```sql
  public.submit_candidate_submission(
    p_candidate_form_session_id uuid,
    p_full_name text,
    p_phone text default null,
    p_date_of_birth date default null,
    p_gender text default null,
    p_address text default null,
    p_candidate_notes text default null,
    p_education jsonb default '[]'::jsonb,
    p_work_experiences jsonb default '[]'::jsonb,
    p_activities jsonb default '[]'::jsonb,
    p_privacy_notice_version text,
    p_idempotency_key uuid default gen_random_uuid()
  ) returns jsonb
  ```
- `SECURITY DEFINER SET search_path = ''`.
- **Preconditions & Lock Sequence**:
  1. Authentication & Active Candidate:
     Inspect `auth.uid()`. Look up `public.candidates` without initial `is_active` filter. Return `UNAUTHENTICATED` if not found; return `USER_INACTIVE` if not `is_active`.
     Lock candidate row (Lock 1): `SELECT candidate_id, email, is_active FROM public.candidates WHERE candidate_id = v_cand.candidate_id FOR UPDATE`.
  2. Lock session row (Lock 2):
     `SELECT mode_code, status_code, expires_at, presented_privacy_notice_version FROM public.candidate_form_sessions WHERE candidate_form_session_id = p_candidate_form_session_id AND candidate_id = v_cand.candidate_id FOR UPDATE`.
     If not found: `{ success: false, error_code: 'NOT_FOUND', message: 'Candidate form session not found' }`.
     If `status_code <> 'OPEN'`: `{ success: false, error_code: 'INVALID_STATE', message: 'Candidate form session is not open' }`.
     If `expires_at <= clock_timestamp()`: `{ success: false, error_code: 'FORM_SESSION_EXPIRED', message: 'Candidate form session has expired' }`.
     If `mode_code <> 'NEW_SUBMISSION'`: `{ success: false, error_code: 'INVALID_ACTION', message: 'submit_candidate_submission requires a NEW_SUBMISSION form session' }`.
  3. Privacy notice pinning verification:
     If `p_privacy_notice_version <> v_session.presented_privacy_notice_version`:
     returns `{ success: false, error_code: 'VALIDATION_ERROR', message: 'Privacy notice version must match server-pinned notice version' }`.
  4. Input Validation:
     - `p_full_name`: non-empty, `char_length <= 120`.
     - `p_phone`: optional, `char_length <= 30`.
     - `p_gender`: optional, must be in `('MALE', 'FEMALE', 'OTHER')` if provided.
     - `p_address`: optional, `char_length <= 255`.
  5. Run Authoritative Plan Validator (Lock 3: changes + reservations):
     `perform private.validate_candidate_form_document_plan(p_candidate_form_session_id);`
     (Validates effective file count <= 5, effective CV >= 1, all staged reservations `VALIDATED` + `CLEAN`).
  6. Insert `public.submissions`:
     ```sql
     v_submission_id := gen_random_uuid();
     insert into public.submissions (
       submission_id,
       candidate_id,
       status_code,
       full_name,
       email,
       phone,
       date_of_birth,
       gender,
       address,
       candidate_notes,
       submitted_at,
       version_no,
       created_at,
       updated_at
     ) values (
       v_submission_id,
       v_cand.candidate_id,
       'NEW',
       btrim(p_full_name),
       v_cand.email, -- Immutable verified email from candidate record
       nullif(btrim(p_phone), ''),
       p_date_of_birth,
       p_gender,
       nullif(btrim(p_address), ''),
       nullif(btrim(p_candidate_notes), ''),
       clock_timestamp(),
       1,
       clock_timestamp(),
       clock_timestamp()
     );
     ```
  7. Insert Child Arrays (`submission_education`, `submission_work_experiences`, `submission_activities`).
  8. Materialize Staged Document Changes:
     Iterate through `candidate_form_document_changes` where `candidate_form_session_id = p_candidate_form_session_id AND status_code = 'PENDING'` for update:
     - Look up reservation:
       `SELECT * INTO v_res FROM public.upload_reservations WHERE upload_reservation_id = chg.upload_reservation_id FOR UPDATE`.
     - Create/lookup logical header:
       Insert `submission_document_logicals(submission_id, document_type_id)` on conflict do nothing.
       Get `logical_document_id`.
     - Insert `submission_documents`:
       `logical_document_id = v_log_id`,
       `storage_bucket = v_res.temp_bucket`,
       `storage_path = v_res.temp_path`,
       `original_filename = v_res.original_filename`,
       `mime_type = coalesce(v_res.detected_mime_type, v_res.declared_mime_type, 'application/octet-stream')`,
       `file_size_bytes = v_res.actual_size_bytes`,
       `checksum_sha256 = v_res.checksum_sha256`,
       `version_no = 1`,
       `is_current = true`,
       `uploaded_by = v_auth_uid`,
       `uploaded_at = clock_timestamp()`
     - Update reservation `status_code = 'FINALIZED'`.
     - Update staged change `status_code = 'APPLIED'`.
  9. Record Privacy Acknowledgement:
     ```sql
     insert into public.privacy_acknowledgements (
       candidate_id,
       submission_id,
       submission_version_no,
       privacy_notice_version,
       acknowledged_at
     ) values (
       v_cand.candidate_id,
       v_submission_id,
       1,
       v_session.presented_privacy_notice_version,
       clock_timestamp()
     );
     ```
  10. Refresh Candidate Current Profile Cache:
      `perform private.refresh_candidate_current_profile(v_cand.candidate_id);`
  11. Enqueue Confirmation Email in `public.email_outbox`:
      ```sql
      insert into public.email_outbox (
        submission_id,
        email_type,
        environment_code,
        recipients,
        subject,
        body_text,
        status_code,
        idempotency_key,
        actor_scope,
        created_by_candidate_id
      ) values (
        v_submission_id,
        'CANDIDATE_SUBMISSION_CONFIRMATION',
        'PRODUCTION',
        jsonb_build_array(v_cand.email),
        'Application Submission Confirmation',
        'Thank you for submitting your application to Eastern International University.',
        'QUEUED',
        p_idempotency_key,
        'CANDIDATE',
        v_cand.candidate_id
      )
      on conflict (actor_scope, email_type, idempotency_key) do nothing;
      ```
  12. Transition Session Status:
      `UPDATE public.candidate_form_sessions SET status_code = 'SUBMITTED', updated_at = clock_timestamp() WHERE candidate_form_session_id = p_candidate_form_session_id;`
  13. Return:
      `{ success: true, data: { submission_id: v_submission_id, status_code: 'NEW', version_no: 1, submitted_at: ... } }`.

#### 4. `public.update_candidate_submission(...)`
- Signature:
  ```sql
  public.update_candidate_submission(
    p_candidate_form_session_id uuid,
    p_full_name text,
    p_phone text default null,
    p_date_of_birth date default null,
    p_gender text default null,
    p_address text default null,
    p_candidate_notes text default null,
    p_education jsonb default '[]'::jsonb,
    p_work_experiences jsonb default '[]'::jsonb,
    p_activities jsonb default '[]'::jsonb,
    p_privacy_notice_version text,
    p_idempotency_key uuid default gen_random_uuid()
  ) returns jsonb
  ```
- `SECURITY DEFINER SET search_path = ''`.
- **Preconditions & Lock Sequence**:
  1. Authentication & Active Candidate:
     Inspect `auth.uid()`. Look up `public.candidates` without initial `is_active` filter. Return `UNAUTHENTICATED` if not found; return `USER_INACTIVE` if not `is_active`.
     Lock candidate row (Lock 1): `FOR UPDATE`.
  2. Lock session row (Lock 2):
     `SELECT mode_code, status_code, expires_at, target_submission_id, base_submission_version_no, presented_privacy_notice_version FROM public.candidate_form_sessions WHERE candidate_form_session_id = p_candidate_form_session_id AND candidate_id = v_cand.candidate_id FOR UPDATE`.
     If not found: `{ success: false, error_code: 'NOT_FOUND', message: 'Candidate form session not found' }`.
     If `status_code <> 'OPEN'`: `{ success: false, error_code: 'INVALID_STATE', message: 'Candidate form session is not open' }`.
     If `expires_at <= clock_timestamp()`: `{ success: false, error_code: 'FORM_SESSION_EXPIRED', message: 'Candidate form session has expired' }`.
     If `mode_code <> 'EDIT_SUBMISSION'`: `{ success: false, error_code: 'INVALID_ACTION', message: 'update_candidate_submission requires an EDIT_SUBMISSION form session' }`.
  3. Lock target submission (Lock 3):
     `SELECT * INTO v_submission FROM public.submissions WHERE submission_id = v_session.target_submission_id AND candidate_id = v_cand.candidate_id FOR UPDATE`.
     If not found: `{ success: false, error_code: 'NOT_FOUND', message: 'Target submission not found' }`.
     If `v_submission.status_code <> 'NEW'`:
     returns `{ success: false, error_code: 'INVALID_STATE', message: 'Target submission is no longer in editable NEW status' }`.
     If `v_submission.version_no <> v_session.base_submission_version_no`:
     returns `{ success: false, error_code: 'STALE_VERSION', message: 'Submission version has changed since session opened' }`.
  4. Privacy notice acknowledgement check:
     If `p_privacy_notice_version <> v_session.presented_privacy_notice_version`:
     returns `{ success: false, error_code: 'VALIDATION_ERROR', message: 'Privacy notice version must match server-pinned notice version' }`.
  5. Input Validation:
     - `p_full_name`: non-empty, `char_length <= 120`.
     - `p_phone`: optional, `char_length <= 30`.
     - `p_gender`: optional, `('MALE', 'FEMALE', 'OTHER')`.
     - `p_address`: optional, `char_length <= 255`.
  6. Run Authoritative Plan Validator (Lock 4: changes + reservations):
     `perform private.validate_candidate_form_document_plan(p_candidate_form_session_id);`
  7. Bump submission aggregate version:
     `v_new_version_no := v_submission.version_no + 1;`
  8. Update `public.submissions`:
     ```sql
     update public.submissions
     set
       full_name = btrim(p_full_name),
       phone = nullif(btrim(p_phone), ''),
       date_of_birth = p_date_of_birth,
       gender = p_gender,
       address = nullif(btrim(p_address), ''),
       candidate_notes = nullif(btrim(p_candidate_notes), ''),
       version_no = v_new_version_no,
       updated_at = clock_timestamp()
     where submission_id = v_session.target_submission_id;
     ```
  9. Replace child arrays atomically:
     Delete existing rows for `submission_id` from `submission_education`, `submission_work_experiences`, `submission_activities`.
     Insert new rows from `p_education`, `p_work_experiences`, `p_activities`.
  10. Apply Staged Document Changes:
      Iterate through `candidate_form_document_changes` where `candidate_form_session_id = p_candidate_form_session_id AND status_code = 'PENDING'` for update:
      - `ADD`: insert logical document header if not exists; insert `submission_documents` with `is_current = true`, `version_no = max(version_no) + 1`; mark reservation `FINALIZED`, change `APPLIED`.
      - `REPLACE`: set existing versions for `target_logical_document_id` to `is_current = false`; insert `submission_documents` with `is_current = true`, `version_no = max(version_no) + 1`; mark reservation `FINALIZED`, change `APPLIED`.
      - `DELETE`: set existing versions for `target_logical_document_id` to `is_current = false`; mark change `APPLIED`.
  11. Re-verify post-materialization document plan.
  12. Record Privacy Acknowledgement:
      ```sql
      insert into public.privacy_acknowledgements (
        candidate_id,
        submission_id,
        submission_version_no,
        privacy_notice_version,
        acknowledged_at
      ) values (
        v_cand.candidate_id,
        v_session.target_submission_id,
        v_new_version_no,
        v_session.presented_privacy_notice_version,
        clock_timestamp()
      )
      on conflict (submission_id, submission_version_no) do update set
        acknowledged_at = clock_timestamp();
      ```
  13. Refresh Candidate Current Profile Cache:
      `perform private.refresh_candidate_current_profile(v_cand.candidate_id);`
  14. Enqueue HR Update Notification:
      ```sql
      insert into public.email_outbox (
        submission_id,
        email_type,
        environment_code,
        recipients,
        subject,
        body_text,
        status_code,
        idempotency_key,
        actor_scope,
        created_by_candidate_id
      ) values (
        v_session.target_submission_id,
        'SUBMISSION_UPDATE_HR_NOTIFICATION',
        'PRODUCTION',
        jsonb_build_array('hr@eiu.edu.vn'),
        'Candidate Submission Updated',
        format('Candidate %s has updated Submission %s (version %s).', v_cand.email, v_session.target_submission_id, v_new_version_no),
        'QUEUED',
        p_idempotency_key,
        'CANDIDATE',
        v_cand.candidate_id
      )
      on conflict (actor_scope, email_type, idempotency_key) do nothing;
      ```
  15. Transition Session Status:
      `UPDATE public.candidate_form_sessions SET status_code = 'SUBMITTED', updated_at = clock_timestamp() WHERE candidate_form_session_id = p_candidate_form_session_id;`
  16. Return:
      `{ success: true, data: { submission_id: v_session.target_submission_id, status_code: 'NEW', version_no: v_new_version_no, updated_at: ... } }`.

---

### 3.2 Web Command Layer: `web/src/lib/commands/candidate-submission.ts`

- Implement typed commands using `createCommandRunner`:
  1. `submitCandidateSubmission(input, deps)`
  2. `updateCandidateSubmission(input, deps)`
- Type definitions:
  - `EducationInput`, `WorkExperienceInput`, `ActivityInput`
  - `SubmitCandidateSubmissionInput`, `SubmitCandidateSubmissionData`
  - `UpdateCandidateSubmissionInput`, `UpdateCandidateSubmissionData`
- Input validation:
  - Validates session UUID, name, email regex, date formats, child array items, pinned notice version.
- Authorize:
  - Candidate actor check (`roles.includes("CANDIDATE") || permissions.includes("candidate.self")`).
- Error mapping to `CommandErrorCode` (`UNAUTHENTICATED`, `USER_INACTIVE`, `NOT_FOUND`, `INVALID_STATE`, `STALE_VERSION`, `VALIDATION_ERROR`, `FORM_SESSION_EXPIRED`, `REQUIRED_CV_DOCUMENT_MISSING`, `MAX_FIVE_CURRENT_DOCUMENTS_EXCEEDED`).

---

### 3.3 Verification Tests: `web/src/__tests__/candidate-submission.test.ts`

- Test suite verifying:
  1. `UNAUTHENTICATED` call rejection (missing auth.uid or no candidate identity row)
  2. `USER_INACTIVE` candidate rejection (is_active = false)
  3. `NOT_FOUND` / foreign session access rejection
  4. `FORM_SESSION_EXPIRED` rejection
  5. `INVALID_STATE` (closed / cancelled session) rejection
  6. `INVALID_ACTION`: submit rejected if mode is not `NEW_SUBMISSION`
  7. `INVALID_ACTION`: update rejected if mode is not `EDIT_SUBMISSION`
  8. `PRIVACY_VERSION_MISMATCH` rejection: notice version does not match pinned version
  9. `VALIDATION_ERROR`: empty full_name, invalid gender, malformed UUIDs rejected
  10. `SUBMIT_NEW_SUBMISSION_SUCCESS`: atomic creation of submission, child snapshots, document materialization, privacy acknowledgement, outbox confirmation email, session marked SUBMITTED
  11. `IMMUTABLE_VERIFIED_EMAIL`: candidate submission email derives strictly from candidate record, cannot be overwritten by client payload
  12. `EDIT_SUBMISSION_SUCCESS`: updates text fields, replaces child snapshots, applies staged document changes (ADD, REPLACE, DELETE), increments version_no from 1 to 2, enqueues HR outbox notification, marks session SUBMITTED
  13. `EDIT_NON_NEW_SUBMISSION_REJECTION`: edit rejected with INVALID_STATE if target submission is no longer NEW (e.g. READ or PROCESSED)
  14. `EDIT_STALE_VERSION_REJECTION`: edit rejected with STALE_VERSION if base_submission_version_no does not match current version_no
  15. `DOCUMENT_PLAN_REQUIRED_CV_MISSING`: rejected if no current CV document is staged
  16. `DOCUMENT_PLAN_MAX_FIVE_FILES`: rejected if effective current document count exceeds 5
  17. `DOCUMENT_PLAN_UNSCANNED_FILE`: rejected if staged reservation is not VALIDATED + CLEAN
  18. `DOCUMENT_PLAN_TARGET_NO_CURRENT`: replace/delete rejected if target logical document has no current version
  19. `CANDIDATE_PROFILE_CACHE_REFRESH`: latest submitted/updated submission updates candidates current_full_name, current_phone, last_submission_at
  20. `OUTBOX_NOTIFICATION_ENQUEUED`: submission confirmation and HR update notifications are recorded in email_outbox
  21. `TERMINAL_SESSION_GUARD`: submitted session cannot be re-submitted or re-edited (status <> OPEN)
  22. `COMPETING_CONCURRENT_EDIT_SERIALIZATION`: deterministic lock sequence prevents deadlocks against concurrent HR status transition
  23. `IDEMPOTENT_SUBMISSION_REPLAY`: duplicate idempotency key handles submission retry safely

---

## 4. Acceptance & Verification Contract

1. `npm run typecheck` in `web/` PASS with 0 errors.
2. `npm run lint` in `web/` PASS with 0 errors.
3. `npm run build` in `web/` PASS.
4. `npm run test` in `web/` PASS (all existing + new tests green).
5. Clean local migration replay test on ephemeral test port PASS.
6. Secret scan PASS.
7. Git diff clean, exactly one commit on `oanhpham-kobe/TASK-S02-004-candidate-submission`.
