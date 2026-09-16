# TASK-S07-005 — Email History Projection and Manual Email Outbox UI Consumers

## Dispatch gate and exact baseline

This is an implementation prompt for future Owner dispatch, NOT current implementation authority. Current continuation stops after independent prompt/source PASS. Execution is permitted only after external prompt audit and explicit dispatch.

Repository: `oanhpham-kobe/eiu-recruitment`. Integration: `autonomy/continuous-integration-20260905-01`. Starting reporting HEAD: `2270ec01343e4b1dedc4c617d42e0b0679831cc5`. Governed implementation baseline is the exact peeled commit of immutable `checkpoint/pre-S07-005-001`, or the latest independently PASS numbered replacement recorded in TASK_REGISTRY before dispatch. Resolve the ref and compare with the review's REVIEWED_SHA; never use a moving integration HEAD as a substitute. The baseline commit contains this prompt, so its own SHA is recorded by immutable ref and later evidence, not a fabricated self-hash.

Accepted predecessors:
- `checkpoint/S07-001-accepted-001` → `8397be35d64a65f4a693811e4fc6b9e43287a7cd`
- `checkpoint/S07-002-accepted-001` → `d99776aa6e07c0023ada9906211f6d1d4b17f5ed` (tag object `105506f6e68e1acb4e1b0cf732bbe5beb2b66136`)
- `checkpoint/S07-003-accepted-001` → `7317138779270087e3e425f48b13785923b17f42` (tag object `a2702995bb1b475d003ad8e85d4a2c58b7fcd75c`)
- `checkpoint/S07-004-accepted-001` → `2c42533733257caa3567cd6c8cae80e13b3092b8` (tag object `a0c9ed0e051b74c1db887e119064e022340ddc26`)
All predecessor checkpoints remain immutable.

Dependencies: `TASK-S07-001`, `TASK-S04-001`, `TASK-S04-002`, `TASK-S04-003`, `TASK-S07-004`; all DONE. Materialize and execute no sibling task or Slice-08.

## Source authority and preflight

Read `project_control/reviews/S07_005_SOURCE_RECONCILIATION_v1.md`, accepted S07_001 source reconciliation, REVIEW.md, and canonical current sections:
- `review_pack/11_EMAIL_DOCUMENTS_AND_ACTIVITY_LOG.md` §1 (Manual email actions) and §3 (Email History vs Security Audit);
- `review_pack/37_BACKEND_COMMAND_CONTRACTS.md` §§3, 10, 16 (trusted server commands, actor resolution);
- `review_pack/39_SECURITY_RLS_MATRIX.md`, `59_RLS_POLICY_BLUEPRINT.md` (`emails.history_view`, `emails.history_delete`);
- `review_pack/47_AUDIT_LOGGING_SPEC.md` §1 (Business Activity Log vs Security Audit);
- `review_pack/48_IDEMPOTENCY_CONCURRENCY_SPEC.md` (idempotent enqueue keys);
- `recruitment_webapp/design_system/` (components, dialogs, drawers, accessibility, i18n);
- `app_spec.yaml` email actions, outbox, and history specifications.

Inspect accepted S07-001 database migration `20260913010000_email_persistence_contracts.sql` and its trusted RPCs (`preview_email`, `enqueue_email`, `bulk_enqueue_email`, `delete_email_history`). Do not modify accepted database migrations; this task is a pure consumer. Use symbol references before changing exported adapters. Parent owns Todo and integration.

## Bounded outcome

Deliver the user-facing consumers of the accepted S07-001 email persistence contracts:
1. Typed command runners and server actions for manual email preview, enqueue, and history deletion.
2. Manual email actions on the Interview surface ("Gửi thư ứng viên" / "Gửi thư người tham dự") with preview-before-send dialogs.
3. User-facing Email History projection view and management drawer with multi-select and classification-based deletion (`TEST_RECORD` / `WRONG_RECORD` with mandatory reason).
4. Strict enforcement of contextual permissions (`emails.history_view`, `emails.history_delete`, `interviews.manage`) and RLS.

### A. Typed command runners and server actions

Create `web/src/lib/commands/email-commands.ts` wrapping accepted S07-001 RPCs:
- `previewInterviewEmail(interviewId, recipientType, recipientId, client?)`:
  Calls `public.preview_email`. Validates inputs (UUIDs, allowed recipient types). Returns rendered subject, body, sender snapshot, and recipient address.
- `enqueueInterviewEmail(interviewId, recipientType, recipientId, idempotencyKey, client?)`:
  Calls `public.enqueue_email`. Generates client-side idempotency key if not provided. Enqueues outbox message transactionally. Returns outbox ID and status `QUEUED`.
- `bulkEnqueueInterviewEmails(items, client?)`:
  Calls `public.bulk_enqueue_email`. Bounded batch (max 100 items). Idempotent enqueue across selected participants.
- `deleteEmailHistoryEntry(emailHistoryId, classification, reason, client?)`:
  Calls `public.delete_email_history`. Validates classification (`TEST_RECORD` or `WRONG_RECORD`) and requires non-empty reason text for `WRONG_RECORD`. Deletes operational history row while leaving immutable audit intact.
- `loadInterviewEmailHistory(interviewId, client?)`:
  Queries `public.email_history` under contextual RLS for the interview. Returns paginated/ordered list of sent/queued emails.

### B. Manual email actions on Interview surface

Update `web/src/components/interview/InterviewPage.tsx` and `InterviewDrawer.tsx`:
- Add action buttons on Interview drawer / table row actions:
  * **Gửi thư ứng viên / Send to Candidate**: Available when interview has an application/candidate.
  * **Gửi thư người tham dự / Send to Participants**: Available when interview has participants. Allows selecting all or subset of participants.
- **Preview Dialog (`web/src/components/interview/EmailPreviewDialog.tsx`)**:
  * Preview-before-send is mandatory: User clicks action $\rightarrow$ dialog opens $\rightarrow$ loads preview from `previewInterviewEmail`.
  * Dialog displays: Sender, Recipient email, Subject line, Formatted body preview, and Interview date/time/location summary.
  * Confirm button: "Xác nhận gửi / Confirm send" $\rightarrow$ calls `enqueueInterviewEmail`.
  * Toast notification upon successful enqueue: "Đã đưa vào hàng đợi gửi thư / Queued for delivery".
  * Invariant: Manual email send does NOT alter interview status (`schedule_status_code` remains unchanged).

### C. User-facing Email History projection and management

Create `web/src/components/interview/EmailHistoryDrawer.tsx`:
- Accessible from Interview page / drawer via "Lịch sử gửi thư / Email History" button.
- Displays table of email history records for the interview:
  * Recipient email / name
  * Subject
  * Template code / type
  * Status (`QUEUED`, `SENT`, `FAILED`)
  * Sent / created timestamp
- **Deletion of wrong/test records**:
  * Row action or multi-select checkbox: "Xóa / Delete".
  * Opens confirmation modal (`web/src/components/interview/DeleteEmailHistoryDialog.tsx`):
    - Explains that deletion removes the record from operational history while audit remains immutable.
    - Classification radio/select: `TEST_RECORD` (if test record) or `WRONG_RECORD` (wrong recipient/content).
    - Mandatory reason textarea when `WRONG_RECORD` is selected (must not be empty/whitespace).
    - Confirm button calls `deleteEmailHistoryEntry`.
    - Table refreshes on success; toast confirmation displayed.

### D. Security and contextual permissions

- `preview_email`, `enqueue_email`, `bulk_enqueue_email` require `interviews.manage` permission and active user session.
- `email_history` query requires `emails.history_view` and parent contextual authorization.
- `delete_email_history` requires `emails.history_view + emails.history_delete`.
- Unauthenticated callers receive `UNAUTHENTICATED`; unauthorized callers receive `FORBIDDEN`.
- All operations execute via server actions / RPCs; no direct business table writes from browser.

### E. Design System and UX conventions

- Match existing Design System (Dialog, Drawer, Button, StatusBadge, Toast).
- Keyboard accessibility: Escape closes dialogs/drawers; focus trapped in modals and restored on close.
- Vietnamese default text with standard system chrome:
  * "Gửi thư ứng viên", "Gửi thư người tham dự", "Lịch sử gửi thư", "Bản xem trước email", "Xác nhận gửi", "Lý do xóa".
- User-authored report or email body text is not machine-translated.

## Local integration & unit test requirements

1. **Unit tests (`web/src/__tests__/email-commands.test.ts`)**:
   - `previewInterviewEmail`: validates input, handles RPC response, returns rendered preview.
   - `enqueueInterviewEmail`: enforces idempotency key, handles success, maps errors.
   - `bulkEnqueueInterviewEmails`: handles batch array, maps errors.
   - `deleteEmailHistoryEntry`: requires classification, validates non-empty reason for `WRONG_RECORD`, calls RPC.
   - `loadInterviewEmailHistory`: queries history under RLS with interview scoping.
2. **Component / browser tests (`web/src/__tests__/interview-email-ui.test.ts`)**:
   - Preview modal renders sender, recipient, subject, and body before send.
   - Confirming send calls enqueue and displays success toast.
   - Email history drawer lists sent emails with correct status badges.
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
- `TASK-S07-006` or Slice-08 tasks.

## Verification plan

- Web tests: `npm run test -- src/__tests__/email-commands.test.ts src/__tests__/interview-email-ui.test.ts`.
- Full web test suite: `npm run test`.
- Web quality gates: `npm run lint`, `npm run typecheck`, `npm run build`, `npm run design:check`.
- Predecessor database regressions: `email_persistence_contracts_test.sql`, `email_persistence_concurrency_test.sh`.
- Governance validators: `validate_control_plane.py`, `validate_omp_native.py`.
- Exact-SHA formal CI: fresh Integration CI and Governance CI on integration branch.

## Stop conditions and source reopen

Stop immediately at prompt review PASS. Do not begin implementation. Do not dispatch an executor.

`SOURCE_REOPEN_REQUIRED: false`.
No canonical invariant requires modifying any accepted predecessor. TASK-S07-005 is a pure consumer of accepted S07-001 database contracts.
