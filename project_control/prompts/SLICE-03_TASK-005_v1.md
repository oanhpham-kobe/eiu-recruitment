# EIU Recruitment — Executor Prompt
## TASK-S03-005 — Submission Detail Drawer, HR Note editor, document preview, and Application creation flow
### Prompt version: SLICE-03_TASK-005_v1

## 0. Execution Control

```text
SOURCE_BASELINE: Full Handover v1.17
TASK_SCOPE: TASK-S03-005 only
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
    - react-patterns: "focused client drawer/form islands; explicit pending/error state and serializable server props"
    - vercel-react-best-practices: "server-first read models, zero bundle bloat and bounded client mutation surfaces"
    - accessibility: "semantic dialog/drawer focus lifecycle, labelled forms, 16px text, keyboard controls and accessible errors"
    - react-testing: "consumer-observable detail, edit, preview and Application-create behavior"
    - supabase: "RLS-aware SSR/server action access to current private document and database interfaces"
    - supabase-postgres-best-practices: "effective ordered migration/function/policy verification; no weakened RLS or grants"
    - security-review: "contextual permission boundaries, untrusted form/file inputs, PII and short-lived 1-5min signed URLs"
    - tdd: "risk-based public seams for HR mutations, exact Submission identity, duplicate/reactivate states, audit and optimistic errors"
    - browser-qa: "authorized local read-only detail drawer, keyboard/focus and responsive journey when runnable"
  GRAPH_ROUTE: DIRECT_SOURCE_LSP_ONLY
  GRAPH_ROUTE_REASON: "Known localized inbox/detail flow; direct migration chain, source and tests are authoritative."
  PRINCIPLE_PROFILE: "PRIVATE_SUBMISSION_DETAIL_AND_ATOMIC_APPLICATION_COMMAND"
  EVIDENCE_DELTA: "APPLICATION-INBOX-DETAIL-001"
```

Before dependent implementation, read every required effective `SKILL.md`, current Next 16.3 bundled documentation for framework-sensitive work, and the canonical sources below. Persist post-execution `SKILL_USAGE` under `TASK-S03-005` with provider, availability, loaded, applied, and concrete applied_to. Persist `GRAPH_USAGE` under `APPLICATION-INBOX-DETAIL-001`; if LSP is unavailable, record `lsp_status: UNAVAILABLE` and use only direct source plus focused search. Do not fabricate graph, LSP, skill, MCP, preview, or browser-QA use. Supabase MCP remains non-production/read-only and is optional; repository migrations and direct tests remain authoritative.

## 2. Canonical Source References

- `review_pack/04_HR_APPLICATION_INBOX.md` §§2, 4–9, 154–166.
- `review_pack/13_ACCEPTANCE_CRITERIA_AND_TEST_CASES.md` AC-09 through AC-12H, AC-14, AC-42 through AC-45, AC-50 through AC-52.
- `review_pack/37_BACKEND_COMMAND_CONTRACTS.md` §§4–5, 10 and explicit contracts for `open_submission`, `update_submission_by_hr`, `create_or_update_application`, and `reactivate_application`.
- `review_pack/41_STORAGE_AND_UPLOAD_SECURITY.md` §§1–4 and `review_pack/11_EMAIL_DOCUMENTS_AND_ACTIVITY_LOG.md` document privacy/audit rules.
- `review_pack/47_AUDIT_LOGGING_SPEC.md` and `review_pack/39_SECURITY_RLS_MATRIX.md` for mandatory audit events, contextual permissions, private storage, and signed-URL boundaries.
- Design System v1.8: `PAGE_OVERRIDES_V1_8.md` §§14, 50–52; `TABLE_LAYOUT.md` §§4–5, 11–14; `ACCESSIBILITY.md` §§2–7; `PATTERNS.md` drawer/dialog patterns; `DESIGN_REVIEW_CHECKLIST.md` Tables, Drawer/Modal and Accessibility.
- Ordered repository migration authority: `20260905060000_candidate_form_and_submission_schema.sql`, `20260905080000_storage_reservation_and_upload_protocol.sql`, `20260905090000_candidate_submission_commands.sql`, `20260905100000_application_schema_and_status_commands.sql`, `20260905110000_application_lifecycle_commands.sql`, `20260905120000_bulk_submission_status_and_application_assignment.sql`, and `20260905130000_application_inbox_read_rpc.sql`.
- Existing source: `web/src/app/page.tsx`, `web/src/components/inbox/ApplicationInboxTable.tsx`, `web/src/components/inbox/ApplicationInboxTableRows.tsx`, `web/src/lib/application-inbox/*`, `web/src/lib/auth/session.ts`, `web/src/lib/supabase/*`, existing S03 command modules, and project test conventions.

## 3. Required Implementation

### 3.1 Scope and boundaries

Implement only the next Application Inbox detail slice:

1. open the exact selected Submission from the parent-row Action and historical child-row interaction;
2. render the canonical desktop-first Submission Detail Drawer;
3. support authorized HR edit of the Drawer’s HR-writable Submission field (`hr_note`) with explicit Cancel, Save Changes, optimistic concurrency (`expected_version`), validation, stale/error feedback and unsaved-change warning;
4. render private Submission document metadata and authorized Preview/Download controls using an approved short-lived server-authorized document access path with signed URL TTL strictly bounded to 1–5 minutes;
5. expose exact-Submission Application creation/update flow through the existing trusted command contract, including durable-identity duplicate/reactivate results and the created/default Round 1 result;
6. record mandatory audit log entries for sensitive read/edit/create actions.

Do not add a global state library, a generic modal framework, a new document upload protocol, a client-side database mutation sequence, an email flow, bulk action, candidate lifecycle action, Interview scheduling, or S03-006+ functionality. Do not alter business/RLS rules merely to make a UI path work.

### 3.2 Detail read and Drawer contract

- A parent-row detail action selects the deterministic latest Submission; a historical child-row action selects its exact `submission_id`. A one-Submission Candidate opens that exact only Submission. Do not infer a Submission from a Candidate ID after interaction starts.
- Load/render sensitive detail only after server-side internal authorization for `submissions.view` or Root; UI visibility is not authorization. Candidate and unauthorized internal callers receive no HR-only detail, `hr_note`, documents or signed preview/download URL.
- `open_submission()` side effect is permitted only through its approved trusted behavior: `NEW → READ` only when the actor also has `submissions.status`; a view-only actor sees a pure read. Do not perform this mutation in browser code or manufacture a status change.
- Drawer is wide/desktop-first with the required one-column `Label | Value` layout, never a 2×2 card. Render sections in authoritative order: general information, Education, Working Experiences, Activities, Other, Documents, HR Note/source metadata, Application update, and last updated.
- **HR-writable DTO specification:** For this task, the writable Submission DTO is strictly limited to `hr_note` (via the existing `update_submission_by_hr` command contract). Candidate verified email and other candidate-entered profile fields remain immutable to this HR editing flow.
- `hr_note` is HR-only and must not be exposed in a Candidate DTO, page output, browser error, client logs, URL, or unauthorized projection. Long business text wraps; no text is rendered as unsanitized HTML.
- Implement the canonical single whole-drawer Edit mode per `04_HR_APPLICATION_INBOX.md` §7: one `Edit` button for the entire Drawer; do not implement per-section editing. In Edit mode, all HR-editable fields (for this task, `hr_note`) become editable while immutable candidate-entered fields remain read-only. Accessible footer: `Cancel | Save Changes`. Dirty close/backdrop/Escape requests an accessible discard confirmation; confirmed discard restores pre-edit state. Successful save refreshes observed detail without stale overwrite; expected-version conflict returns stable stale feedback (`STALE_VERSION`) and requires reload.
- The Drawer must have dialog semantics, labelled title, visible focus, keyboard operation, Escape close, focus trap and focus restoration to the trigger. Do not let an overlay hide the desktop sidebar contrary to the design contract. Respect reduced motion. Body typography in Drawer must be >= 16px.

### 3.3 Documents and preview contract

- Render only authorized document metadata supplied by a server allowlist. Private documents remain private; no public bucket, static path, long-lived signed URL, service-role key, provider token, full file content, or signed URL is persisted, logged, serialized into history/evidence, or placed in a URL.
- Browser may obtain a short-lived preview/download URL only from a server-authorized path after current server authorization (`submissions.view` or Root Admin).
- **Signed URL Lifetime Invariant:** Generated signed URLs for private document preview/download must enforce an expiration TTL between 60 seconds (1 minute) and 300 seconds (5 minutes) maximum, per `review_pack/41_STORAGE_AND_UPLOAD_SECURITY.md` §Buckets.
- Preview only PDF/image through a hardened same-origin presentation. DOC/DOCX/PPT/PPTX must offer download, not arbitrary inline rendering. Never inline HTML or SVG.
- This task does not implement HR document upload, replace or delete mutation UI unless an already-existing complete trusted interface is directly reused without changes. Do not create a new upload reservation, scanning, finalization, cleanup, or storage mutation path.

### 3.4 Application creation contract

- Application creation requires **both** `submissions.view` **and** (`applications.create` or `applications.manage` or Root Admin). The server boundary must strictly enforce both prerequisites before invoking `create_or_update_application`.
- Application selection names one exact `submission_id`; it never guesses the latest Submission. Use the existing authoritative trusted `create_or_update_application` command only through a server boundary that authenticates, authorizes and validates before RPC invocation.
- Before exposing controls or choices, load master/owner options only from authorized current sources. Server validates active Unit/Team/Position hierarchy and eligible active HR/root owner. The browser must not be a source of truth for permission, hierarchy or owner eligibility.
- Preserve durable identity `(submission_id, unit_id, department_team_id, position_id)`: exact active duplicate requires explicit confirmation/update of the same Application, inactive duplicate clearly reports Reactivate (`ALREADY_EXISTS_INACTIVE`) rather than silently creating a second Application, and different identity creates a distinct Application. Do not rewrite an Application with Interview history into a different identity.
- A new identity must use the existing atomic command that creates exactly one default Round 1 and recalculates the Submission in the same transaction. Never split this into browser-orchestrated writes. Use an idempotency key where the command contract requires one; disable/reconcile duplicate submits.
- Show stable expected conflict/validation messages without leaking raw database or storage detail. On success, render only the returned Application/round result and route/filter intent; do not mutate cache optimistically beyond an observed trusted result.

### 3.5 Mandatory Audit Logging
- Authorize and record audit entries in `public.security_audit_log` (coupled with the business operation or RPC) for:
  1. Sensitive document preview/download access (recording actor, submission_id, document logical/version id, and action `DOCUMENT_ACCESS`);
  2. HR Note update via `update_submission_by_hr` (recording actor, submission_id, version bump, action `SUBMISSION_HR_NOTE_UPDATE`);
  3. Application creation/update via `create_or_update_application` (recording actor, application_id, submission_id, position_id, action `APPLICATION_CREATE_OR_UPDATE`).
- Audit payloads must never contain passwords, tokens, full file contents, or signed URLs.

### 3.6 Tests and verification

Use risk-based TDD at agreed public seams. Add only durable consumer-observable tests. At minimum prove:

1. server detail/read seam rejects unauthenticated, Candidate and insufficient-permission callers before HR PII, note, document metadata or signed URL access; view-only `NEW` read does not mutate while status-authorized open follows the trusted `NEW → READ` contract;
2. parent Action and historical child Action select the exact intended Submission and Drawer sections preserve the canonical `Label | Value` presentation;
3. HR-only `hr_note` is absent from Candidate/unauthorized projection, valid authorized HR edit saves through `update_submission_by_hr`, immutable fields cannot be edited, Cancel/dirty confirmation does not save, and stale version (`STALE_VERSION`) / error feedback is observable;
4. Drawer keyboard/focus lifecycle is observable: semantic dialog/title, focus into drawer, Escape/close restore focus, and controls/validation have accessible names and messages;
5. document controls distinguish previewable PDF/image from download-only Office formats, enforce short-lived signed URL TTL between 1 and 5 minutes (60–300s), and never expose public/static storage paths or a persisted signed URL;
6. Application create requires both `submissions.view` and `applications.create`/`manage`, names an exact Submission, rejects invalid hierarchy/owner and unauthorized caller at the server seam, handles active duplicate confirmation and inactive Reactivate outcome, and observes a new identity’s one default Round 1/idempotent retry result;
7. sensitive document access, HR note update, and Application creation produce corresponding verifiable audit records;
8. full page interaction does not regress S03-004 grouping, exact 1560px table grid or PII-search URL rule.

Run focused tests, direct isolated database replay against effective ordered migrations/RPCs where SQL changes are required, full `npm test`, `npm run typecheck`, `npm run lint`, `npm run build`, `npx react-doctor@latest --verbose --scope changed`, `git diff --check`, and a changed-scope secret/security scan. Browser QA is mandatory when an authorized runnable local target exists; otherwise record the truthful runtime limitation. Never use a production project, production credentials or live migration.

## 4. Explicit Non-goals

- New candidate data capture/session/Storage reservation/scanning/finalization protocol.
- Bulk status/assignment, candidate active/inactive, submission delete, email, report or Interview scheduling flows.
- Any change to pre-existing Application durability, status recalculation, RLS/grants, security definer/search-path, idempotency or locking guarantees except a minimal source-contract-required repair directly tested against the effective migration chain.
- Production deploy, main integration, unrelated design/system refactor, dependency upgrade, or speculative abstraction.

## 5. Delivery

Use exactly one implementation commit on an isolated TASK-S03-005 branch. Leave the task worktree clean. Persist truthful `APPLICATION-INBOX-DETAIL-001` evidence plus `TASK-S03-005` skill receipts. Do not commit/push/merge/deploy outside the task branch.
