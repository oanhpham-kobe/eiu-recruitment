# S07-005 source reconciliation — Email history projection and manual email outbox UI consumers

WORK_ID: S07-005-SOURCE-RECONCILIATION-001
PRODUCER: OMP
STARTING_REPORTING_HEAD: 80690a60a1ee09497bd3fd4114fcb790ea2a0e11
ACCEPTED_PREDECESSORS:
- TASK-S07-001 @ 8397be35d64a65f4a693811e4fc6b9e43287a7cd (checkpoint/S07-001-accepted-001)
- TASK-S07-002 @ d99776aa6e07c0023ada9906211f6d1d4b17f5ed (checkpoint/S07-002-accepted-001)
- TASK-S07-003 @ 7317138779270087e3e425f48b13785923b17f42 (checkpoint/S07-003-accepted-001)
- TASK-S07-004 @ 2c42533733257caa3567cd6c8cae80e13b3092b8 (checkpoint/S07-004-accepted-001)
SOURCE_REOPEN_REQUIRED: false

Producer reconciliation, not new product authority or independent review.
This dispatch authorizes prompt materialization and independent prompt review only. Implementation is NOT started.

## Decision and accepted inputs

Materialize **TASK-S07-005 — Email History Projection and Manual Email Outbox UI Consumers**.
Following the independent Slice-07 closing review (`SLICE-07-CLOSING-REVIEW-001`, finding `S07-CLOSING-001`), SLICE-07 cannot be closed as `DONE` through unapproved deferrals while source-required, dependency-safe feature consumers of accepted database contracts remain unimplemented.

TASK-S07-005 consumes the accepted database contracts delivered by `TASK-S07-001`:
1. `public.preview_email(p_email_type, p_source_entity_type, p_source_entity_id, p_recipient_type, p_recipient_id)`
2. `public.enqueue_email(p_email_type, p_source_entity_type, p_source_entity_id, p_recipient_type, p_recipient_id, p_idempotency_key)`
3. `public.bulk_enqueue_email(p_items)`
4. `public.delete_email_history(p_email_history_id, p_classification, p_reason)`
5. `public.email_history` contextual query view under existing RLS policies.

Direct dependencies:
- `TASK-S07-001` (email outbox & history persistence contracts) — DONE (`checkpoint/S07-001-accepted-001`)
- `TASK-S04-001` / `TASK-S04-002` / `TASK-S04-003` (Interview UI & lifecycle surfaces) — DONE
- `TASK-S07-004` (physical storage cleanup runner) — DONE (`checkpoint/S07-004-accepted-001`)

## Canonical authority and current implementation

Current review-pack authority (source_registry v1.18):
- `review_pack/11_EMAIL_DOCUMENTS_AND_ACTIVITY_LOG.md` §1 (Manual email actions):
  * "Gửi thư ứng viên / Send to Candidate"
  * "Gửi thư người tham dự / Send to Participants"
  * Rules: Preview before send; send does not automatically change Interview status; send from selected table rows or individual drawer where permitted.
- `review_pack/11_EMAIL_DOCUMENTS_AND_ACTIVITY_LOG.md` §3 (Email History vs Security Audit):
  * User-facing operational list with checkbox selection and deletion of wrong/test records.
  * Delete requires `emails.history_view + emails.history_delete` and accepted cleanup classification (`TEST_RECORD` or `WRONG_RECORD` with mandatory reason text).
  * Cleanup classification and reason are audited immutably.
- `review_pack/37_BACKEND_COMMAND_CONTRACTS.md` §§3, 10, 16:
  * Server-action and RPC boundary; untrusted browser input validated before execution.
- `review_pack/39_SECURITY_RLS_MATRIX.md` & `59_RLS_POLICY_BLUEPRINT.md`:
  * Contextual authorization: `emails.history_view` and `emails.history_delete` permissions.
  * Actor cannot read or delete history rows without parent entity authorization.
- `review_pack/47_AUDIT_LOGGING_SPEC.md` §1:
  * Distinguishes user-facing operational email history from privileged immutable Security Audit.
- `review_pack/48_IDEMPOTENCY_CONCURRENCY_SPEC.md`:
  * Client-generated idempotency keys prevent duplicate logical outbox enqueue.
- `app_spec.yaml`:
  * `email_outbox`, `email_history`, and interview email actions specifications.

Current implementation reality:
- `supabase/migrations/20260913010000_email_persistence_contracts.sql`:
  Full database layer is accepted and active: tables `public.email_outbox`, `public.email_history`, `public.email_templates`, RLS policies, audit functions, and trusted RPCs (`preview_email`, `enqueue_email`, `bulk_enqueue_email`, `delete_email_history`).
- `web/src/components/interview/InterviewPage.tsx` and `InterviewDrawer.tsx`:
  Interview page and drawer display interview metadata, participants, status, and notes, but do not yet wire the manual email preview/enqueue actions.
- `web/src/lib/`:
  No typed command runners or server actions currently wrap `preview_email`, `enqueue_email`, or `delete_email_history`.

---

## Bounded scope for TASK-S07-005

TASK-S07-005 delivers the missing user-facing consumers over the accepted S07-001 database contracts:

1. **Server Actions & Command Adapters (`web/src/lib/commands/email-commands.ts`)**:
   - `previewInterviewEmail(interviewId, recipientType, recipientId)` $\rightarrow$ calls `public.preview_email`.
   - `enqueueInterviewEmail(interviewId, recipientType, recipientId, idempotencyKey)` $\rightarrow$ calls `public.enqueue_email`.
   - `bulkEnqueueInterviewEmails(items)` $\rightarrow$ calls `public.bulk_enqueue_email`.
   - `deleteEmailHistoryEntry(emailHistoryId, classification, reason)` $\rightarrow$ calls `public.delete_email_history`.
   - `loadEmailHistory(filters)` $\rightarrow$ queries `public.email_history` under RLS.

2. **Manual Email Actions on Interview Surface (`web/src/components/interview/EmailDialogs.tsx`)**:
   - **Send to Candidate**: Opens preview dialog showing sender, recipient email, subject, rendered body, and interview summary. User confirms send $\rightarrow$ enqueues outbox message with idempotency key. Toast notification on success.
   - **Send to Participants**: Multi-select participant list or individual participant send with preview before enqueue.
   - Preview-before-send is strictly enforced; send does not alter interview status.

3. **Email History Projection & Management View (`web/src/components/interview/EmailHistoryDrawer.tsx`)**:
   - Displays history records for the selected Interview (subject, recipient email, sent/queued timestamp, status, template code).
   - Multi-select checkbox selection.
   - Delete action opening confirmation modal requiring:
     * Classification selection (`TEST_RECORD` if test environment, or `WRONG_RECORD`).
     * Mandatory reason text for `WRONG_RECORD`.
   - Calls `deleteEmailHistoryEntry`; table refreshes on completion; deleted record is removed from operational view while remaining audited in Security Audit.

4. **Permissions & Contextual Access Control**:
   - Manual send requires `interviews.manage` (or `emails.send` where configured).
   - Email History view requires `emails.history_view`.
   - Email History delete requires `emails.history_delete`.
   - Unauthenticated and unauthorized users receive clean permission rejection.

5. **Testing & Verification**:
   - Unit tests for command runners, input validation, and error mapping (`web/src/__tests__/email-commands.test.ts`).
   - Component / browser smoke tests verifying preview render, send confirmation, history listing, and deletion dialog with reason validation (`web/src/__tests__/interview-email-ui.test.ts`).
   - S07-001 predecessor database regressions re-verified.

---

## Explicitly out of scope

- Live external email delivery provider integration (SMTP / SendGrid / Resend / AWS SES credentials).
- Production background cron / email sending daemon (deferred to preproduction/operations).
- Automated candidate email delivery daemon.
- Production deployment (Vercel / Supabase).
- Connected Supabase migrations or operations.
- General data archive/export/purge (`DATA-RETENTION-001`).
- S07-006 or next slice tasks.

---

## Preservation, verification and source reopen

Accepted predecessors `TASK-S07-001`, `TASK-S07-002`, `TASK-S07-003`, and `TASK-S07-004` remain fully intact at their immutable checkpoints.
- Database schema and migrations are NOT modified (contracts already exist).
- Zero predecessor database contracts reopened.
- Clean zero-state replay must continue to pass.
- Web unit tests, lint, and typecheck must pass.
- Governance validators must pass.

`SOURCE_REOPEN_REQUIRED: false`.
No canonical invariant requires modifying any accepted predecessor. TASK-S07-005 is a pure consumer of accepted S07-001 database contracts.
