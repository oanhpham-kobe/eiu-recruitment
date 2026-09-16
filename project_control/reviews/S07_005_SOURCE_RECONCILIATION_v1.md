# S07-005 source reconciliation — Email history projection and manual email outbox UI consumers

WORK_ID: S07-005-SOURCE-RECONCILIATION-001
PRODUCER: OMP
STARTING_REPORTING_HEAD: 570ffb6c4d5e560b6c5c858a859003683bb7890e
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
1. `public.preview_email(p_email_type, p_interview_id, p_application_id, p_submission_id) -> jsonb`
2. `public.enqueue_email(p_request, p_idempotency_key) -> jsonb`
3. `public.bulk_enqueue_email(p_requests, p_idempotency_key) -> jsonb`
4. `public.delete_email_history(p_email_history_id, p_classification, p_reason) -> jsonb`
5. `public.email_history` contextual query view under existing RLS policies.

Direct dependencies:
- `TASK-S07-001` (email outbox & history persistence contracts) — DONE (`checkpoint/S07-001-accepted-001`)
- `TASK-S04-001` / `TASK-S04-002` / `TASK-S04-003` (Interview UI & lifecycle surfaces) — DONE
- `TASK-S07-004` (physical storage cleanup runner) — DONE (`checkpoint/S07-004-accepted-001`)

---

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

Current implementation reality (`supabase/migrations/20260913010000_email_persistence_contracts.sql`):
Full database layer is accepted and active. A pre-review audit reconciled the concrete RPC contracts:

### 1. Trusted Email Preview Contract (`public.preview_email`)
```sql
public.preview_email(
  p_email_type text,
  p_interview_id uuid,
  p_application_id uuid,
  p_submission_id uuid
) returns jsonb
```
- **Allowed manual email types**: `INTERVIEW_INVITATION`, `INTERVIEW_PARTICIPANT_INVITATION`.
- **Actor verification**: Enforced via `private.interview_command_actor('interviews.email')`.
- **Authoritative derivation**: Recipients, subject, and body text are rendered strictly server-side from current authoritative database records:
  * `INTERVIEW_INVITATION`: recipient is candidate's `email_snapshot`.
  * `INTERVIEW_PARTICIPANT_INVITATION`: recipients are server-aggregated from all active current participants of the interview (`public.interview_participants`). The RPC does NOT accept arbitrary client-selected participant IDs.
- **Return payload structure**:
  ```json
  {
    "success": true,
    "data": {
      "recipients": { "to": ["..."], "cc": [] },
      "subject": "...",
      "body_text": "...",
      "template_version": "...",
      "environment_code": "...",
      "context_fingerprint": "...",
      "email_type": "...",
      "interview_id": "...",
      "application_id": "...",
      "submission_id": "...",
      "preview_fingerprint": "..."
    }
  }
  ```
- **Important**: The RPC does NOT return a `sender` field. Under accepted S07-001 contracts (`private.email_snapshot`), the server renders Start, End, Meeting link, and Topic into `body_text` appended to the template body; room and format IDs enter `v_context` and its fingerprint, but are NOT rendered into `body_text`. The UI displays the returned `body_text` verbatim and unchanged; any format, room, or date/time summary shown in the dialog header comes from the authorized Interview projection for presentation only, never as additional RPC-returned fields or send authority.

### 2. Trusted Email Enqueue Contract (`public.enqueue_email`)
```sql
public.enqueue_email(
  p_request jsonb,
  p_idempotency_key uuid
) returns jsonb
```
- **Strict request payload validation**: `p_request` is restricted to EXACTLY five keys:
  `email_type`, `interview_id`, `application_id`, `submission_id`, `preview_fingerprint`.
  Any extra key raises `VALIDATION_ERROR` (errcode `P0701`).
- **Mandatory preview-fingerprint fencing**: The RPC re-derives `email_snapshot` in the transaction and compares `preview_fingerprint`. If interview schedule, participants, or candidate details changed since preview was rendered, the RPC raises `STALE_PREVIEW`.
- **Return payload**:
  `{ "success": true, "data": { "email_outbox_id": "..." } }`
- **Important**: The RPC returns the created `email_outbox_id`. It does NOT return a `status: "QUEUED"` property. Enqueueing into the transactional outbox implies queued status for delivery, but `QUEUED` is an outbox state, not a history state.

### 3. Trusted Bulk Enqueue Contract (`public.bulk_enqueue_email`)
```sql
public.bulk_enqueue_email(
  p_requests jsonb,
  p_idempotency_key uuid
) returns jsonb
```
- `p_requests` must be a JSON array of 1..100 complete request objects.
- Each item must carry the exact 5 keys (`email_type`, `interview_id`, `application_id`, `submission_id`, and its own `preview_fingerprint`).
- Bulk enqueue operates across multiple selected Interview rows.
- It does NOT accept arbitrary participant-subset selections within a single interview. "Send to Participants" enqueues an invitation snapshot targeting all current active participants of that interview.

### 4. Email History Lifecycle & Statuses (`public.email_history`)
- Under accepted migration `20260913010000_email_persistence_contracts.sql` line 38, `email_history.status_code` is strictly constrained to:
  `SENT`, `FAILED`, `CANCELLED`, `ABANDONED`.
- `QUEUED` is NOT an email_history status code (`email_outbox != email_history`). An outbox item only creates/updates `email_history` once an attempt is executed or settled by the worker.
- The UI Email History view queries `public.email_history` under RLS (`emails.history_view`) and must display only the accepted history statuses (`SENT`, `FAILED`, `CANCELLED`, `ABANDONED`).

### 5. Trusted Email History Deletion Contract (`public.delete_email_history`)
```sql
public.delete_email_history(
  p_email_history_id uuid,
  p_classification text,
  p_reason text default null
) returns jsonb
```
- **Actor verification**: Enforced via `private.interview_command_actor('emails.history_delete')` and requires `emails.history_view`.
- **Classification validation**: Must be `'TEST_RECORD'` (valid only when `environment_code = 'TEST'`) or `'WRONG_RECORD'` (requires non-empty trimmed `p_reason` string up to 1000 characters).
- **Audit & deletion**: Inserts `EMAIL_HISTORY_DELETED` into `public.security_audit_log` with actor, classification, and reason, then deletes the row from `public.email_history`.

---

## Bounded scope for TASK-S07-005

TASK-S07-005 delivers the missing user-facing consumers over the accepted S07-001 database contracts:

1. **Server Actions & Command Adapters (`web/src/lib/commands/email-commands.ts`)**:
   - `previewInterviewEmail({ emailType, interviewId, applicationId, submissionId }, client?)`:
     Calls `public.preview_email`. Returns typed preview data including `preview_fingerprint`.
   - `enqueueInterviewEmail({ emailType, interviewId, applicationId, submissionId, previewFingerprint }, idempotencyKey, client?)`:
     Calls `public.enqueue_email` with the exact 5-key request object. Handles `STALE_PREVIEW` gracefully. Returns `{ email_outbox_id }`.
   - `bulkEnqueueInterviewEmails(items, idempotencyKey, client?)`:
     Calls `public.bulk_enqueue_email` with array of complete preview-fenced request objects across selected interviews.
   - `deleteEmailHistoryEntry(emailHistoryId, classification, reason, client?)`:
     Calls `public.delete_email_history` with classification and mandatory reason validation.
   - `loadInterviewEmailHistory(interviewId, client?)`:
     Queries `public.email_history` under contextual RLS for the interview.

2. **Manual Email Actions on Interview Surface (`web/src/components/interview/EmailDialogs.tsx`)**:
   - **Send to Candidate**: Action in Interview drawer / row menu. Opens preview modal loading `preview_email` with `INTERVIEW_INVITATION`.
   - **Send to Participants**: Action in Interview drawer / row menu. Opens preview modal loading `preview_email` with `INTERVIEW_PARTICIPANT_INVITATION` targeting current participants.
   - **Mandatory Preview-Before-Send Flow**:
     User clicks send action $\rightarrow$ dialog fetches server preview $\rightarrow$ displays authoritative recipients, subject, and rendered body $\rightarrow$ user reviews $\rightarrow$ confirms send $\rightarrow$ enqueues outbox message using the server-returned `preview_fingerprint` and client-generated idempotency key.
   - Invariant: Send does NOT alter interview status (`schedule_status_code` remains untouched).

3. **Email History Projection & Management View (`web/src/components/interview/EmailHistoryDrawer.tsx`)**:
   - Accessible via "Lịch sử gửi thư / Email History" button.
   - Displays history records for the interview: recipient email, subject, status (`SENT`, `FAILED`, `CANCELLED`, `ABANDONED`), sent/attempt timestamp, error code if failed.
   - Row deletion action opening confirmation modal:
     * Radio: `TEST_RECORD` (disabled if production environment) or `WRONG_RECORD`.
     * Mandatory trimmed reason textarea for `WRONG_RECORD`.
     * Deletion calls `deleteEmailHistoryEntry`; row disappears from operational view while security audit remains.

4. **Permissions & Security Separation**:
   - Manual preview and enqueue check `interviews.email` through `private.interview_command_actor('interviews.email')`.
   - Email History view requires `emails.history_view` under RLS.
   - Email History delete requires `emails.history_view + emails.history_delete`.
   - All mutations route through server actions / RPCs; no direct database writes from browser.

---

## Explicitly out of scope

- Live external email delivery provider integration (SMTP / SendGrid / Resend / AWS SES credentials).
- Production background cron / email sending daemon (deferred to preproduction/operations).
- Automated candidate email delivery daemon.
- Production deployment (Vercel / Supabase).
- Connected Supabase migrations or operations.
- General data archive/export/purge (`DATA-RETENTION-001`).
- Arbitrary participant subsetting within a single interview.
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
