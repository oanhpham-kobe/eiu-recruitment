# TASK-S07-005 — Email History Projection and Manual Email Outbox UI Consumers

## Dispatch gate and exact baseline

This is an implementation prompt for future Owner dispatch, NOT current implementation authority. The prior R2 prompt review PASS at `checkpoint/pre-S07-005-002` remains immutable historical evidence, but an external prompt audit found one blocking contract mismatch in authentication-error semantics after that review. Implementation is prohibited until this repaired prompt is captured by a new immutable numbered pre-task checkpoint, independently re-reviewed PASS on that exact peeled SHA, recorded as the governed implementation baseline, and explicitly dispatched by the Owner.

The governed implementation baseline is therefore NOT `checkpoint/pre-S07-005-002`. Use only the latest independently PASS numbered replacement recorded in TASK_REGISTRY after this external-audit repair. The expected next replacement is `checkpoint/pre-S07-005-003` if that ref remains unused; never move or overwrite `checkpoint/pre-S07-005-001` or `checkpoint/pre-S07-005-002`. Resolve the chosen immutable ref and compare its peeled SHA with the independent review's `REVIEWED_SHA`; never use a moving integration HEAD as a substitute. The baseline commit contains this prompt, so its own SHA is recorded by immutable ref and later evidence, not a fabricated self-hash.

Accepted predecessors:
- `checkpoint/S07-001-accepted-001` → `8397be35d64a65f4a693811e4fc6b9e43287a7cd`
- `checkpoint/S07-002-accepted-001` → `d99776aa6e07c0023ada9906211f6d1d4b17f5ed` (tag object `105506f6e68e1acb4e1b0cf732bbe5beb2b66136`)
- `checkpoint/S07-003-accepted-001` → `7317138779270087e3e425f48b13785923b17f42` (tag object `a2702995bb1b475d003ad8e85d4a2c58b7fcd75c`)
- `checkpoint/S07-004-accepted-001` → `2c42533733257caa3567cd6c8cae80e13b3092b8` (tag object `a0c9ed0e051b74c1db887e119064e022340ddc26`)
All predecessor checkpoints remain immutable.

Dependencies: `TASK-S07-001`, `TASK-S04-001`, `TASK-S04-002`, `TASK-S04-003`, `TASK-S07-004`; all DONE. Materialize and execute no sibling task or Slice-08.

## Source authority and preflight

Read `project_control/reviews/S07_005_SOURCE_RECONCILIATION_v1.md`, accepted S07_001 source reconciliation, REVIEW.md, the latest external prompt-audit artifact for this task, and canonical current sections:
- `review_pack/11_EMAIL_DOCUMENTS_AND_ACTIVITY_LOG.md` §1 (Manual email actions) and §3 (Email History vs Security Audit);
- `review_pack/37_BACKEND_COMMAND_CONTRACTS.md` §§3, 10, 16 (trusted server commands, actor resolution);
- `review_pack/39_SECURITY_RLS_MATRIX.md`, `59_RLS_POLICY_BLUEPRINT.md` (`interviews.email`, `emails.history_view`, `emails.history_delete`);
- `review_pack/47_AUDIT_LOGGING_SPEC.md` §1 (Business Activity Log vs Security Audit);
- `review_pack/48_IDEMPOTENCY_CONCURRENCY_SPEC.md` (idempotent enqueue keys);
- `recruitment_webapp/design_system/` (components, dialogs, drawers, accessibility, i18n);
- `app_spec.yaml` email actions, outbox, and history specifications.

Inspect accepted S07-001 database migration `20260913010000_email_persistence_contracts.sql` and its trusted RPCs (`preview_email`, `enqueue_email`, `bulk_enqueue_email`, `delete_email_history`). Also inspect the accepted definition of `private.interview_command_actor(...)` in the Interview lifecycle contracts. Do not modify accepted database migrations; this task is a pure consumer. Use symbol references before changing exported adapters. Parent owns Todo and integration.

## Bounded outcome

Deliver the user-facing consumers of the accepted S07-001 email persistence contracts:
1. Typed command runners and server actions wrapping the accepted database RPCs with exact parameter matching.
2. Manual email actions on the Interview surface ("Gửi thư ứng viên" / "Gửi thư người tham dự") with preview-before-send dialogs and mandatory preview-fingerprint fencing.
3. User-facing Email History projection view and management drawer with multi-select and classification-based deletion (`TEST_RECORD` / `WRONG_RECORD` with mandatory reason).
4. Strict enforcement of contextual permissions (`interviews.email`, `emails.history_view`, `emails.history_delete`) and RLS.

### A. Typed command runners and server actions

Create `web/src/lib/commands/email-commands.ts` wrapping accepted S07-001 RPCs:

- `previewInterviewEmail(input, client?)`:
  Calls `public.preview_email(p_email_type, p_interview_id, p_application_id, p_submission_id)`.
  * `input` shape:
    ```ts
    {
      emailType: "INTERVIEW_INVITATION" | "INTERVIEW_PARTICIPANT_INVITATION";
      interviewId: string;
      applicationId: string;
      submissionId: string;
    }
    ```
  * Validates UUIDs and email type. Returns server snapshot data: `recipients` (`{ to: string[], cc: string[] }`), `subject`, `body_text`, `template_version`, `environment_code`, `context_fingerprint`, and `preview_fingerprint`.
  * Note: The RPC does NOT return a `sender` field. Under accepted S07-001 contracts (`private.email_snapshot`), the server renders Start, End, Meeting link, and Topic into `body_text` appended to the template body; format and room IDs enter the context fingerprint, but are not rendered into `body_text`.

- `enqueueInterviewEmail(input, idempotencyKey, client?)`:
  Calls `public.enqueue_email(p_request, p_idempotency_key)`.
  * `input` request object is strictly bounded to EXACTLY five keys:
    ```ts
    {
      email_type: "INTERVIEW_INVITATION" | "INTERVIEW_PARTICIPANT_INVITATION";
      interview_id: string;
      application_id: string;
      submission_id: string;
      preview_fingerprint: string;
    }
    ```
    No extra keys are permitted (backend raises `VALIDATION_ERROR` on unrecognized keys).
  * Passes client-generated UUID `idempotencyKey`.
  * Handles `STALE_PREVIEW` gracefully: When the server snapshot changed between preview and send, returns a structured error instructing the UI to refresh the preview.
  * On success, returns `{ email_outbox_id: string }`.
  * Note: The RPC returns the created `email_outbox_id`; it does not return `status: "QUEUED"`. Successful enqueue means the item is queued in the transactional outbox for worker delivery.

- `bulkEnqueueInterviewEmails(requests, idempotencyKey, client?)`:
  Calls `public.bulk_enqueue_email(p_requests, p_idempotency_key)`.
  * `requests`: Array of 1..100 complete 5-key request objects, each carrying its own `preview_fingerprint`.
  * Operates across multiple selected Interview rows.
  * For `INTERVIEW_PARTICIPANT_INVITATION`, recipients are derived server-side from all current active participants of that interview. Client-side arbitrary participant-subset selection is prohibited by the trusted contract.

- `deleteEmailHistoryEntry(emailHistoryId, classification, reason, client?)`:
  Calls `public.delete_email_history(p_email_history_id, p_classification, p_reason)`.
  * Validates classification: must be `'TEST_RECORD'` (valid only in TEST environment) or `'WRONG_RECORD'` (requires non-empty trimmed `reason` string $\le 1000$ characters).
  * Returns `{ email_history_id: string }`.

- `loadInterviewEmailHistory(interviewId, client?)`:
  Queries `public.email_history` under contextual RLS for the given interview. Returns history records.
  * Note: `public.email_history.status_code` values are strictly: `SENT`, `FAILED`, `CANCELLED`, `ABANDONED`.
  * `QUEUED` is an outbox state, NOT an email_history status code. Do not attempt to query `email_outbox` directly or synthesize `QUEUED` history rows.

### B. Manual email actions on Interview surface

Update `web/src/components/interview/InterviewPage.tsx` and `InterviewDrawer.tsx`:
- Add action triggers on Interview drawer and table row menus:
  * **Gửi thư ứng viên / Send to Candidate**: Available when interview has an associated candidate.
  * **Gửi thư người tham dự / Send to Participants**: Available when interview has participants. Targets all active current participants of the interview.
- **Preview-Before-Send Dialog (`web/src/components/interview/EmailPreviewDialog.tsx`)**:
  * Mandatory flow: User clicks action $\rightarrow$ dialog opens $\rightarrow$ calls `previewInterviewEmail`.
  * Displays:
    - Authoritative recipients list (To: candidate email or participant email list).
    - Subject line.
    - Rendered body preview: Displays the returned `body_text` verbatim and unchanged as formatted server-side (which includes Start, End, Meeting link, and Topic appended to the template body). Any format, room, or additional interview details displayed in the dialog header/summary are presentation-only context from the authorized Interview projection, never additional RPC-returned fields or send authority.
  * Retains the server-returned `preview_fingerprint`.
  * User reviews $\rightarrow$ clicks "Xác nhận gửi / Confirm send" $\rightarrow$ calls `enqueueInterviewEmail` with the exact 5 keys and the retained `preview_fingerprint`.
  * If the interview was rescheduled or modified while preview was open, server returns `STALE_PREVIEW`; dialog catches this, displays notification ("Thông tin phỏng vấn đã thay đổi, vui lòng xem lại bản xem trước"), and refreshes the preview.
  * Toast notification on successful enqueue: "Đã đưa vào hàng đợi gửi thư".
  * Invariant: Manual email send does NOT alter interview status (`schedule_status_code` remains untouched).

### C. User-facing Email History projection and management

Create `web/src/components/interview/EmailHistoryDrawer.tsx`:
- Accessible from Interview page / drawer via "Lịch sử gửi thư / Email History" button.
- Displays history table for the interview:
  * Recipient email
  * Subject
  * Template type
  * Status badge (`SENT`, `FAILED`, `CANCELLED`, `ABANDONED`)
  * Sent / attempt timestamp
  * Error description if `FAILED`
- **Deletion of wrong/test records**:
  * Row action or multi-select checkbox: "Xóa / Delete".
  * Confirmation dialog (`web/src/components/interview/DeleteEmailHistoryDialog.tsx`):
    - Explains that operational history is removed while security audit remains immutable.
    - Classification selection: `TEST_RECORD` (disabled in production environment) or `WRONG_RECORD`.
    - Mandatory reason textarea when `WRONG_RECORD` is selected (must not be blank or whitespace-only, max 1000 characters).
    - Confirms deletion $\rightarrow$ calls `deleteEmailHistoryEntry` $\rightarrow$ table refreshes on success.

### D. Security and contextual permissions

- `preview_email`, `enqueue_email`, `bulk_enqueue_email` require `interviews.email` permission (or Root Admin) enforced via `private.interview_command_actor('interviews.email')`.
- `email_history` query requires `emails.history_view` and parent contextual authorization under RLS policy `email_history_select`.
- `delete_email_history` requires `emails.history_view` AND `emails.history_delete` enforced by RPC and `private.interview_command_actor('emails.history_delete')`.
- **Accepted backend error semantics are fail-closed `FORBIDDEN` for these email RPCs when actor resolution fails.** `private.interview_command_actor(...)` returns `NULL` when `auth.uid()` is absent, when no active internal app user resolves, or when required permission is missing. `preview_email`, `enqueue_email`, `bulk_enqueue_email`, and `delete_email_history` then return `FORBIDDEN`; these accepted RPCs do NOT distinguish unauthenticated callers with an `UNAUTHENTICATED` error code. A server action/UI may separately detect a missing session and present login UX, but it must not misstate or change the trusted RPC contract.
- All operations execute via server actions / RPCs; no direct database writes from browser.

### E. Design System and UX conventions

- Match existing Design System components (Dialog, Drawer, Button, StatusBadge, Toast).
- Keyboard accessibility: Escape closes dialogs/drawers; focus trapped in modals and restored on close.
- Vietnamese default text with standard system chrome:
  * "Gửi thư ứng viên", "Gửi thư người tham dự", "Lịch sử gửi thư", "Bản xem trước email", "Xác nhận gửi", "Lý do xóa".
- User-authored report or email body text is not machine-translated.

## Local integration & unit test requirements

1. **Unit tests (`web/src/__tests__/email-commands.test.ts`)**:
   - `previewInterviewEmail`: sends exact 4 parameters (`p_email_type`, `p_interview_id`, `p_application_id`, `p_submission_id`), handles RPC response, returns `preview_fingerprint`.
   - `enqueueInterviewEmail`: sends exact 5-key request object (`email_type`, `interview_id`, `application_id`, `submission_id`, `preview_fingerprint`), supplies idempotency key, handles `STALE_PREVIEW`, extracts `email_outbox_id`.
   - `bulkEnqueueInterviewEmails`: sends array of 1..100 complete request objects carrying `preview_fingerprint`, maps per-item results.
   - `deleteEmailHistoryEntry`: validates classification, requires non-empty trimmed reason for `WRONG_RECORD`, passes to RPC.
   - `loadInterviewEmailHistory`: queries history under RLS with interview scoping, asserts accepted statuses only.
   - Authentication/authorization contract: verifies adapters preserve backend `FORBIDDEN` for email RPC actor-resolution failures and do not fabricate an `UNAUTHENTICATED` RPC result; any separate missing-session UX remains an adapter/UI concern.
2. **Component / browser tests (`web/src/__tests__/interview-email-ui.test.ts`)**:
   - Preview modal renders recipients, subject, and body before send.
   - Retains `preview_fingerprint` and passes it on confirmation.
   - Handles `STALE_PREVIEW` by displaying notification and re-fetching preview.
   - Confirming send calls enqueue and displays success toast without changing interview status.
   - Email history drawer lists sent emails with correct status badges (`SENT`, `FAILED`, `CANCELLED`, `ABANDONED`) and no synthetic `QUEUED`.
   - Delete dialog enforces classification and reason validation before deletion.
3. **Predecessor regressions**:
   - S07-001 database outbox and history tests pass.
   - S04 Interview lifecycle and UI tests pass without regression.

## Implementation out of scope

- Live external email delivery provider integration (SMTP / SendGrid / Resend credentials).
- Background cron / daemon for external email delivery.
- Scanner provider runtime.
- Storage cleanup modifications (S07-003/S07-004 remain complete and intact).
- Production deployment (Vercel / Supabase).
- Connected Supabase migrations or operations.
- General data archive/export/purge (`DATA-RETENTION-001`).
- Arbitrary participant subsetting within a single interview.
- `TASK-S07-006` or Slice-08 tasks.

## Verification plan

- Web tests: `npm run test -- src/__tests__/email-commands.test.ts src/__tests__/interview-email-ui.test.ts`.
- Full web test suite: `npm run test`.
- Web quality gates: `npm run lint`, `npm run typecheck`, `npm run build`, `npm run design:check`.
- Predecessor database regressions: `email_persistence_contracts_test.sql`, `email_persistence_concurrency_test.sh`.
- Governance validators: `validate_control_plane.py`, `validate_omp_native.py`.
- Exact-SHA formal CI: fresh Integration CI and Governance CI on integration branch.

## Stop conditions and source reopen

Stop immediately after the new independent prompt/source re-review PASS has been persisted. Do not begin implementation and do not dispatch an executor until the Owner explicitly dispatches TASK-S07-005.

`SOURCE_REOPEN_REQUIRED: false`.
The external audit defect concerns prompt-level error-code semantics only. No canonical invariant requires modifying any accepted predecessor; TASK-S07-005 remains a pure consumer of accepted S07-001 database contracts.
