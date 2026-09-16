# Independent Prompt and Source Reconciliation Review (R3) — TASK-S07-005

- **WORK_ID**: `S07-005-PROMPT-REVIEW-003`
- **REVIEWED_SHA**: `0c9646ecfc71665fdeba1a41023b36ec0e5c0e9a`
- **BASELINE_REF**: `checkpoint/pre-S07-005-003`
- **BASELINE_PEELED_SHA**: `0c9646ecfc71665fdeba1a41023b36ec0e5c0e9a`
- **ROLE**: `OMP_EIU_REVIEWER`
- **VERDICT**: `BLOCKING_REPAIR`
- **SOURCE_REOPEN_REQUIRED**: `false`
- **IMPLEMENTATION_AUTHORIZED**: `false`

---

## Executive Summary

Independent re-review (R3) performed by `eiu-reviewer` on the peeled checkpoint baseline `checkpoint/pre-S07-005-003` at commit `0c9646ecfc71665fdeba1a41023b36ec0e5c0e9a`.

Finding `S07-005-EXTERNAL-AUDIT-001` from the external prompt audit is verified **RESOLVED**: prompt §D explicitly states fail-closed `FORBIDDEN` semantics for the S07-001 email RPCs, denies a distinct `UNAUTHENTICATED` RPC error code, clearly separates optional missing-session/login UX at the server-action/UI layer, and requires adapter tests preserving backend `FORBIDDEN` without fabricating synthetic `UNAUTHENTICATED` results.

However, a new blocking finding was identified in governance acceptance criteria:
**`S07-005-R3-001`**: `TASK_REGISTRY.yaml` acceptance criterion 4 requires `interviews.manage`, contradicting prompt §D and accepted S07-001 database contracts, which require granular permission `interviews.email` for email operations.

**Implementation has NOT started and is NOT authorized.** Per handoff instructions, execution stops immediately and returns the finding package to the Owner / External ChatGPT producer.

---

## External Audit Finding Resolution

### Finding `S07-005-EXTERNAL-AUDIT-001`: RESOLVED

- **Actor Helper**: In accepted `supabase/migrations/20260906070000_interview_lifecycle_commands.sql`, `private.interview_command_actor(text, text)` returns `NULL` if `auth.uid()` is null, if no active `app_users` record resolves, or if a non-Root caller lacks the required permission.
- **Accepted RPC Behavior**: In accepted `supabase/migrations/20260913010000_email_persistence_contracts.sql`, `preview_email`, `enqueue_email`, and `bulk_enqueue_email` return `{"success": false, "error_code": "FORBIDDEN"}` immediately upon a null actor; `delete_email_history` returns `FORBIDDEN` on a null actor or missing history-view permission. None of these functions return `UNAUTHENTICATED`.
- **Prompt Verification**: Prompt §D explicitly reflects fail-closed `FORBIDDEN`, denies `UNAUTHENTICATED` RPC results, distinguishes optional missing-session UI/adapter login UX, and requires adapter tests verifying this contract. Verified resolved.

---

## Blocking Findings

### `S07-005-R3-001` — Replace task's `interviews.manage` acceptance requirement with `interviews.email`

- **Severity**: `P2`
- **Disposition**: `BLOCKING_REPAIR`
- **Location**: `project_control/TASK_REGISTRY.yaml` — `tasks.TASK-S07-005.acceptance`, fourth criterion
- **Evidence**:
  1. `TASK_REGISTRY.yaml` requires: `"Contextual permissions (emails.history_view, emails.history_delete, interviews.manage) and RLS are strictly enforced."`
  2. The reviewed prompt §D instead correctly requires `interviews.email` for `preview_email`, `enqueue_email`, and `bulk_enqueue_email`.
  3. Accepted `20260913010000_email_persistence_contracts.sql`: `public.preview_email`, `public.enqueue_email`, and `public.bulk_enqueue_email` resolve `private.interview_command_actor('interviews.email')`. `private.can_read_email_context` separately accepts `interviews.view` OR `interviews.manage` OR eligible contextual participant predicate; `interviews.manage` is not a universal requirement.
  4. Canonical `review_pack/59_RLS_POLICY_BLUEPRINT.md` (HR section) distinguishes Interview read authorization from mutations requiring their granular permission.
- **Impact**: An executor or acceptance reviewer following the registry can impose `interviews.manage` as an additional email/history gate, denying users authorized by accepted contracts, or treat management permission as the email capability. This leaves contradictory authorization instructions in a file explicitly included in this review.
- **Required Repair**: Change the `TASK-S07-005` acceptance criterion in `TASK_REGISTRY.yaml` to name `interviews.email`, `emails.history_view`, and `emails.history_delete`, with accepted parent-context predicates applied separately. Do not modify accepted SQL or broaden permissions. Capture and independently review the repaired exact checkpoint.

---

## 10 Control Assessment Summary

| Control Area | Result | Evidence |
|---|---|---|
| Exact preview contract | PASS | Matches 4-parameter `public.preview_email` SQL signature. Snapshot fields and fingerprint retained; no sender field invented. |
| Exact enqueue contract & fencing | PASS | Exactly 5 keys in `p_request` + UUID idempotency key. Fingerprint fencing and `STALE_PREVIEW` handled. Returns `email_outbox_id`. |
| Bulk bounds & participant derivation | PASS | 1..100 complete requests. Server-derived participants for invitations; client subsetting prohibited. Per-item results. |
| Preview body & presentation context | PASS | Displays returned `body_text` unchanged. Format/room/date/time summary in header is presentation-only context from Interview projection. |
| History lifecycle | PASS | Strictly `SENT`, `FAILED`, `CANCELLED`, `ABANDONED`. Prohibits synthetic `QUEUED` or querying `email_outbox` directly. |
| History deletion | PASS | Matches `delete_email_history(uuid, text, text)`. `TEST_RECORD` (TEST only) or `WRONG_RECORD` ($\le 1000$ chars reason). Atomic audit. |
| Contextual authorization | BLOCKING_REPAIR | Prompt §D correctly uses `interviews.email`, but `TASK_REGISTRY.yaml` acceptance criterion requires `interviews.manage` (Finding `S07-005-R3-001`). |
| Unit & integration requirements | PASS | Adapter contract/error tests, preview-fingerprint, `STALE_PREVIEW` refresh, status constraints, deletion validation, regression suites specified. |
| Scope boundaries | PASS | Excludes SMTP/SendGrid runtime, background cron daemon, deployment, connected Supabase mutations, S07-006, Slice-08. |
| Source reopen | PASS | `SOURCE_REOPEN_REQUIRED: false` is truthful. Zero database contract or predecessor changes required. |

---

## Decision and Lifecycle State

- **Prompt Review Status**: `BLOCKING_REPAIR`
- **Lifecycle Result**: `PROMPT_REVIEW_BLOCKING_REPAIR`
- **Implementation Status**: `NOT_STARTED`
- **Active Executors**: `0`
- **Next Action**: Return finding package `S07-005-R3-001` to Owner / External ChatGPT producer for prompt/governance repair.
