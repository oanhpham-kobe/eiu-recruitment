# EIU Recruitment — Executor Prompt
## TASK-S03-006 — Candidate Account Lifecycle & Application Inbox Bulk Actions
### Prompt version: SLICE-03_TASK-006_v1

## 0. Execution Control

```text
SOURCE_BASELINE: Full Handover v1.17
TASK_SCOPE: TASK-S03-006 only
BASE_BRANCH: autonomy/continuous-integration-20260905-01
BASE_HEAD: resolve directly immediately before implementation
ONE_TASK_COMMIT: required on the task branch
NO_DEPLOY_NO_MAIN_NO_PRODUCTION_MUTATIONS
```

## 1. Governance & Compact Routing

```yaml
GOVERNANCE:
  SKILLS_REQUIRED:
    - react-patterns
    - vercel-react-best-practices
    - accessibility
    - react-testing
    - supabase
    - supabase-postgres-best-practices
    - security-review
    - tdd
    - browser-qa
  SKILLS_INTENDED_APPLICATION:
    - react-patterns: "accessible bulk action toolbar and dialog state in client ApplicationInboxTable island; serializable props"
    - vercel-react-best-practices: "server actions for bulk commands, optimistic UI boundaries, zero extra client dependencies"
    - accessibility: "semantic bulk action toolbar, dialog/modal focus trap, accessible confirmation dialogs, aria-live status announcements"
    - react-testing: "consumer-observable rendered bulk action state transitions, selection count, confirmation, and error display"
    - supabase: "atomic RPC implementation of candidate lifecycle and bulk status commands under strict RLS and search_path = ''"
    - supabase-postgres-best-practices: "FOR UPDATE locking hierarchy (Candidate -> Submissions -> Applications), touch_version, audit logging"
    - security-review: "server-side permission verification (candidates.active_manage, submissions.status), fail-closed error handling"
    - tdd: "risk-based tests for atomic all-or-nothing batch execution, portal lockout, recalculation, and optimistic concurrency"
    - browser-qa: "local browser verification of bulk selection, toolbar actions, confirmation modals, and responsive layout"
  GRAPH_ROUTE: DIRECT_SOURCE_LSP_ONLY
  GRAPH_ROUTE_REASON: "Localized known slice completion; direct migration chain, source, and tests are authoritative."
  PRINCIPLE_PROFILE: "CANDIDATE_LIFECYCLE_AND_INBOX_BULK_ACTIONS"
  EVIDENCE_DELTA: "APPLICATION-INBOX-BULK-001"
```

Before implementation, read every required effective `SKILL.md`, current Next 16.3 bundled documentation for framework-sensitive work, and the canonical sources below. Persist post-execution `SKILL_USAGE` under `TASK-S03-006` with provider, availability, loaded, applied, and concrete applied_to. Persist `GRAPH_USAGE` under `APPLICATION-INBOX-BULK-001`; if LSP is unavailable, record `lsp_status: UNAVAILABLE` and use only direct source plus focused search. Do not fabricate graph, LSP, skill, MCP, preview, or browser-QA use.

## 2. Canonical Source References

- `review_pack/04_HR_APPLICATION_INBOX.md` §§4, 10 (Submission status, Candidate inactive lifecycle, Bulk actions).
- `review_pack/13_ACCEPTANCE_CRITERIA_AND_TEST_CASES.md` AC-03, AC-07, AC-08, AC-GRP-01.
- `review_pack/37_BACKEND_COMMAND_CONTRACTS.md` §12 (`set_candidate_active`), §15 (`bulk_set_candidate_active`, `bulk_set_latest_submission_manual_status`).
- `review_pack/command_registry.yaml` entries for `set_candidate_active`, `bulk_set_candidate_active`, `bulk_set_latest_submission_manual_status` (AC-BULK-CAND-LIFE-01 through 03, AC-BULK-SUB-STAT-01 through 03).
- Design System v1.8: `TABLE_LAYOUT.md` §11, `PATTERNS.md` toolbar & dialog patterns, `ACCESSIBILITY.md` focus and alert patterns.
- Ordered repository migration authority: `20260905030000_identity_schema.sql` (candidate schema & constraints `candidate_inactive_metadata_ck`), `20260905100000_application_schema_and_status_commands.sql`, `20260905120000_bulk_submission_status_and_application_assignment.sql`, `20260905130000_application_inbox_read_rpc.sql`, and `20260905140000_submission_detail_and_open_submission_repair.sql`.
- Existing source: `web/src/components/inbox/ApplicationInboxTable.tsx`, `web/src/lib/application-inbox/model.ts`, `web/src/lib/application-inbox/server.ts`, `web/src/app/application-inbox-actions.ts`, `web/src/lib/commands/submission-status.ts`.

## 3. Required Implementation

### 3.1 Scope and boundaries

Implement the remaining Application Inbox Phase-1 bulk and candidate lifecycle features to complete SLICE-03:

1. **Read Model & Version Exposure (`list_application_inbox` & models):**
   - The Application Inbox read RPC and models (`model.ts`, `server.ts`) must expose `candidate_version_no` (the candidate row's version) and `latest_submission_version_no` + `latest_submission_id`.
   - These optimistic tokens are required by both bulk commands (`bulk_set_candidate_active` requires candidate expected versions; `bulk_set_latest_submission_manual_status` requires expected candidate IDs, expected latest submission IDs, and expected latest submission versions).
   - The UI table must forward these row-bound tokens directly from the selected rows rather than re-fetching fresh versions, preserving canonical stale-preview detection.

2. **Transactional Commands & RPCs:**
   - Implement `set_candidate_active(candidate_id, active, expected_version)` and `bulk_set_candidate_active(candidate_ids, active, expected_versions[])`:
     - Permission: `candidates.active_manage` or Root Admin. Enforce permission server-side; unauthorized callers are rejected with `FORBIDDEN` before mutation.
     - `active=false`: set `is_active=false`, `inactive_at=clock_timestamp()`, `inactive_by=actor`. Candidate Portal access is blocked. Existing internal Applications/Interviews/Submissions are NOT deleted or inactivated.
     - `active=true`: clear `inactive_at=null`, `inactive_by=null`. Re-evaluate all Submissions for the candidate: if a Submission has no active Application, explicitly set its status to `READ`; otherwise derive `PROCESSED/DONE/CLOSED` from active Applications.
     - Enforce `candidate_inactive_metadata_ck` constraint.
     - Record audit entries in `public.security_audit_log`: For `bulk_set_candidate_active`, each affected candidate receives an individual audit entry, plus exactly one batch audit event is recorded (`AC-BULK-CAND-LIFE-02`).
     - `bulk_set_candidate_active` is strictly **ALL_OR_NOTHING**. Any stale version or ineligible candidate aborts the entire batch without partial mutation.
   - Connect the existing `bulk_set_latest_submission_manual_status` command to the Application Inbox UI.

3. **Application Inbox Bulk UI Integration (`ApplicationInboxTable.tsx`):**
   - Active bulk actions in the table toolbar when candidates are selected:
     - **Mark as NEW / Mark as READ**: calls `bulk_set_latest_submission_manual_status` passing the selected row tokens. Selection entity is Candidate. Only latest submissions with NO active application may transition.
     - **Set Inactive / Set Active (Reactivate)**: calls `bulk_set_candidate_active`. Confirmation dialog required before setting inactive.
     - Selection summary updates reactively (`X Candidate được chọn`).
     - Actions are disabled when 0 candidates are selected.
   - Accessible confirmation modal/dialog for bulk Inactive:
     - WAI-ARIA dialog semantics (`role="dialog"`, `aria-modal="true"`, `aria-labelledby`) with labelled title.
     - Keyboard focus trap (Tab/Shift+Tab containment), initial focus on cancel/action, Escape key dismissal, and focus restoration to the opening trigger button upon close.
   - Body typography >= 16px. Touch targets >= 44px.
   - Error and success feedback presented via accessible status regions (`role="status"` / `role="alert"` / `aria-live="polite"`).

### 3.2 Tests and verification

Use risk-based TDD. At minimum assert:

1. `set_candidate_active` & `bulk_set_candidate_active` authorization:
   - Non-root caller without `candidates.active_manage` receives `FORBIDDEN` on both single and bulk RPC/server boundaries before any mutation occurs.
   - Root Admin and caller with `candidates.active_manage` are authorized.
2. Candidate lifecycle & reactivation parity:
   - Inactivating sets `is_active=false`, `inactive_at`, `inactive_by`. Candidate login/portal is denied. Submissions/Applications retained.
   - Reactivating sets `is_active=true`, clears inactive metadata, and sets no-application submissions to `READ`, while active-application submissions derive `PROCESSED/DONE/CLOSED`.
   - Exact audit cardinality: `bulk_set_candidate_active` records one audit entry per candidate plus exactly one batch audit event.
   - All-or-nothing batch semantics: if one candidate version is stale in `bulk_set_candidate_active`, the entire batch aborts with `STALE_VERSION` and zero rows are mutated.
3. Application Inbox Bulk UI & Keyboard Contract:
   - Selecting checkboxes activates toolbar bulk buttons and displays selected count.
   - Bulk Mark Read/New forwards row-bound tokens and refreshes list.
   - Bulk Inactive displays confirmation dialog; dialog traps Tab focus, dismisses on Escape, restores focus to the trigger button, and mutates upon confirmation.
   - Error banners render accessible alerts on failure without leaking internal details.
4. Non-regression:
   - All existing 228 tests pass. Full `npm test`, `npm run typecheck`, `npm run lint`, `npm run build`, `git diff --check`, and secret scan pass.

## 4. Explicit Non-goals

- Out of scope bulk actions (bulk delete, bulk email, bulk export).
- S04 (Interview Scheduling) features.
- Any change to pre-existing RLS, foundation schemas, or prompt authority.
