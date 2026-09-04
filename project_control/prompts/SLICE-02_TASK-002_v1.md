# EIU Recruitment — Executor Prompt
## TASK-S02-002 — Form Session Lifecycle and Privacy Notice Pinning Commands
### Prompt version: SLICE-02_TASK-002_v1

## 0. Execution Control

```text
SOURCE_BASELINE: Full Handover v1.17
SOURCE_SHA256: 0b39c3615dd5b34e998527a1d273e0b846458c7bd4170be46c9bb670bfcb3498
BUSINESS_STATUS: Business Logic Core v1.2 = FROZEN
TECHNICAL_STATUS: Technical Architecture v1.17 = TECHNICAL SPECIFICATION FROZEN
TASK_SCOPE: TASK-S02-002 Form Session Lifecycle and Privacy Notice Pinning Commands Only
WORKTREE: D:/orca/recruitment/TASK-S02-002-form-session
BRANCH: oanhpham-kobe/TASK-S02-002-form-session
BASE_BRANCH: autonomy/continuous-integration-20260905-01
BASE_HEAD: b7456bde5dfeb915bc746eaf738d7718f3069abe
```

---

## 1. Governance & Routing

### Skill Routing
```yaml
SKILL_ROUTING:
  required:
    - supabase-postgres-best-practices
    - security-review
  optional:
    - tdd
  not_needed:
    react-patterns: "no UI components modified in this backend RPC / command task"
    accessibility: "no UI components touched"
    browser-qa: "no browser UI journeys modified"
```

### Graph Route
```text
GRAPH_ROUTE: DIRECT_SOURCE_LSP_ONLY
Reason: Localized database RPC and command implementation directly specified in review pack 37 and 40.
```

---

## 2. Canonical Source References

- `recruitment_webapp/review_pack/37_BACKEND_COMMAND_CONTRACTS.md` (§2 Core error codes, §3 start_candidate_form_session, cancel_candidate_form_session, authoritative lifecycle)
- `recruitment_webapp/review_pack/40_DATABASE_INVARIANTS.md` (§Candidate Form Session invariants, §Privacy notice pinning invariants)
- `recruitment_webapp/review_pack/39_SECURITY_RLS_MATRIX.md`
- `recruitment_webapp/review_pack/59_RLS_POLICY_BLUEPRINT.md` (§Candidate temporary-resource policies)

---

## 3. Implementation Specification

### 3.1 Migration File: `supabase/migrations/20260905070000_form_session_commands.sql`

1. **`public.start_candidate_form_session(p_mode text, p_submission_id uuid default null)`**:
   - `SECURITY DEFINER SET search_path = ''`.
   - **Authentication**: calls `private.current_candidate_id()`. If null, returns `{ success: false, error_code: 'UNAUTHENTICATED', message: 'Candidate authentication required' }`.
   - **Privacy Notice Pinning**:
     Queries `public.privacy_notice_versions` where `is_current = true and effective_from <= now()`.
     If not found, fails closed with `{ success: false, error_code: 'PRIVACY_NOTICE_UNAVAILABLE', message: 'No active privacy notice is available' }`.
   - **Mode Validation**:
     - `p_mode = 'NEW_SUBMISSION'`:
       * `target_submission_id` must be null; `base_submission_version_no` must be null.
     - `p_mode = 'EDIT_SUBMISSION'`:
       * `p_submission_id` is required.
       * Lookup `public.submissions` where `submission_id = p_submission_id` and `candidate_id = v_cand_id`. If not found, returns `NOT_FOUND`.
       * Verify `status_code = 'NEW'`. If not `NEW`, returns `INVALID_STATE`.
       * Sets `target_submission_id = p_submission_id`, `base_submission_version_no = sub.version_no`.
     - Invalid mode returns `VALIDATION_ERROR`.
   - **Session Creation**:
     Inserts into `public.candidate_form_sessions` with:
     * `candidate_id = v_cand_id`
     * `mode_code = p_mode`
     * `presented_privacy_notice_version = v_notice_version`
     * `status_code = 'OPEN'`
     * `expires_at = now() + interval '4 hours'`
   - Returns `{ success: true, data: { candidate_form_session_id, mode_code, presented_privacy_notice_version, status_code, expires_at } }`.

2. **`public.cancel_candidate_form_session(p_session_id uuid)`**:
   - `SECURITY DEFINER SET search_path = ''`.
   - **Authentication & Ownership**:
     Calls `private.current_candidate_id()`.
     Lookup session where `candidate_form_session_id = p_session_id` and `candidate_id = v_cand_id`. If not found, returns `NOT_FOUND`.
   - **Terminal State Check**:
     If `status_code in ('SUBMITTED', 'CANCELLED', 'EXPIRED')`, returns `{ success: false, error_code: 'INVALID_STATE', message: 'Session is in terminal state and cannot be cancelled' }`.
   - **Wall-Clock Expiry Check**:
     If `expires_at <= now()`, updates `status_code = 'EXPIRED'`, returns `{ success: false, error_code: 'FORM_SESSION_EXPIRED', message: 'Form session has expired' }`.
   - **Cancellation**:
     Updates `status_code = 'CANCELLED'`, `updated_at = now()`.
     Enqueues cleanup records in `public.storage_cleanup_queue` for any associated reservations in `upload_reservations`.
   - Returns `{ success: true, data: { candidate_form_session_id, status_code: 'CANCELLED' } }`.

3. **Grants**:
   Revoke from `public` and `anon`; grant execute to `authenticated`, `postgres`, `service_role`.

### 3.2 Application Interface (`web/src/lib/commands/form-session.ts`)
- Implement `startCandidateFormSession` and `cancelCandidateFormSession` using the Task-004 command runner.
- Enforce the required mutation sequence: `authenticate -> authorize -> validate -> execute`.

### 3.3 Automated Test Suite (`web/src/__tests__/form-session.test.ts`)
Add automated tests proving:
1. Unauthenticated call -> `UNAUTHENTICATED`.
2. Inactive candidate -> `USER_INACTIVE`.
3. Missing active privacy notice -> fails closed with `PRIVACY_NOTICE_UNAVAILABLE`.
4. NEW_SUBMISSION creates OPEN session with pinned notice and 4-hour expiry.
5. EDIT_SUBMISSION on foreign or non-existent submission -> `NOT_FOUND`.
6. EDIT_SUBMISSION on non-NEW submission -> `INVALID_STATE`.
7. Wall-clock expired session -> fails closed with `FORM_SESSION_EXPIRED`.
8. Cancellation moves OPEN -> CANCELLED, enqueues cleanup, and prevents re-cancelling terminal session.

### 3.4 Unlinked Disposable Replay Verification
- Staged in temporary directory with trap cleanup, non-conflicting ports, and `.temp` excluded.
- Automated SQL assertions verify all 8 outcomes against the local container.

---

## 4. Acceptance Criteria

1. Migration applies cleanly on top of existing migrations.
2. All 8 boundary test cases PASS in disposable replay verification with zero errors.
3. `npm run typecheck`, `npm run lint`, `npm run build`, and `npm test` PASS.
4. Zero secrets or credentials committed.
5. `project_control/EVIDENCE_INDEX.yaml` updated under `FORM-SESSION-001` with assertion results.
6. `project_control/CURRENT_STATE.md` and `project_control/TASK_REGISTRY.yaml` updated with `status: REVIEW` (pending independent review), with prompt SHA-256 bound.
7. Exactly one clean commit on `oanhpham-kobe/TASK-S02-002-form-session`.
