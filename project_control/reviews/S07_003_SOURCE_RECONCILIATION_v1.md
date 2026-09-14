# S07-003 source reconciliation — Storage cleanup trusted contracts

Producer reconciliation, not new product authority or independent review. Starting reporting SHA: `37b01169394378bf666a6baa440a2431407b22d6`. Owner-transported external ChatGPT S07-002 final audit/release recorded in `916febb43fb5ab87b1065de677bbcfaed4c74cf5`. Only the next prompt gate is authorized; implementation is not started.

## Decision and accepted inputs

Materialize exactly **TASK-S07-003 — Storage Cleanup Eligibility and Result-Fencing Trusted Contracts**. This is a bounded database/adapter contract cut before any physical cleanup runner, not a generic worker framework. Existing cleanup intent is durable, but cleanup eligibility and result ownership are not yet safe enough to authorize a later destructive consumer. It can be verified using disposable SQL/concurrency tests without choosing scanner/email providers or deleting Storage objects.

Direct dependencies: TASK-S02-003 (reservation/cleanup protocol), TASK-S02-004 (staged finalization), TASK-S04-002 (Interview reservation cleanup), TASK-S07-002 (scan terminal cleanup producer). These are DONE; S07-002 transitively includes S07-001 and S06 authorization prerequisites. Accepted checkpoints: S07-001 `checkpoint/S07-001-accepted-001` → `8397be35d64a65f4a693811e4fc6b9e43287a7cd`; S07-002 `checkpoint/S07-002-accepted-001` → `d99776aa6e07c0023ada9906211f6d1d4b17f5ed` (tag object `105506f6e68e1acb4e1b0cf732bbe5beb2b66136`). Neither moves.

## Canonical authority and current implementation

Current review-pack authority (source_registry v1.18): 11 §§5–9; 37 §§3,10,16; 41 Two-phase/Candidate staged/Interview hard-delete protocol; 42 Current business retention decision; 47 same-transaction audit/minimization and expiry cleanup summary; 48 idempotency/deterministic locking; 39/59 RLS; 66 approved archive/purge; 73 canonical predicates; app_spec `candidate_form_session`, `upload_reservation`, `interview_upload_cleanup`, `retention`. Accepted source reconciliations S07_001 and S07_002 establish downstream workers as separate cuts; their historical implementation observations are not descriptions of today's tree.

- `20260905060000_candidate_form_and_submission_schema.sql:322–339`: existing queue has unique bucket/path, source identity, status, attempts; current and historical document version rows are retained separately.
- `20260905080000_storage_reservation_and_upload_protocol.sql:1026–1117`: claim is bounded SKIP LOCKED with lease/reclaim; completion accepts cleanup ID/success/error only and writes without worker/attempt/token/lease compare. Service-role grant is broad. This is a concrete downstream protocol gap, not a claim that S07-002 scan fencing is wrong.
- Same migration cancellation producer defers `not_before` through reservation and signed-upload expiry. Other producers include `20260906010000_pre_s04_review_repairs.sql`, Interview lifecycle `20260906070000_interview_lifecycle_commands.sql`, and S07-002 `20260914090000_document_scan_request_protocol.sql` terminal scan intent.
- Interview replacement can enqueue an old path while an immutable historical document row still references it. Queue presence/reason alone is not deletion authority. Candidate cancellation also requires reference protection rather than assuming every queued reservation is unused.
- `web/src/lib/commands/storage-reservation.ts` wraps legacy claim/complete; no physical cleanup runner is accepted. Migrate those adapter callers and affected tests with the future contract change; do not implement Storage.remove or scheduler here.
- S07-002 claim/complete is candidate-session scoped and has its own worker role and lock order. No replacement of that protocol is needed. Interview scan integration is a distinct later gap.

## Scope and security model

Own only: forward-compatible cleanup schema/RPC hardening over the existing queue; bounded reservation-backed expiry discovery and durable intent capture; trusted eligibility authorization; attempt ownership/fencing/retry/exhaustion; minimal transactional audit; existing typed adapters and focused tests. Database discovery is limited to known server-generated reservation identities, not arbitrary Storage bucket listing or guessed prefixes.

A queue record is a request, not permission to destroy. Eligibility must prove a private managed temp object, safe source identity, terminal/expired unused reservation or durable detached-parent cleanup provenance, elapsed `not_before` and signed-upload safety bound, and absence of **any current or historical** Submission/Interview document reference. Unknown path/provenance, retained version, live reservation or ambiguous ownership fails closed; do not erase that evidence or mark physical deletion DONE. Historical replacement rows remain protected until a separately approved purge.

Use a narrow non-login worker role and explicit grants; browser/anon/authenticated cannot claim, authorize, complete, forge audit or enumerate private paths. No broad service-role completion bypass. Inputs are server-derived and bounded. Keep paths/contents/signed URLs/secrets out of user-facing results and audit payloads; record stable IDs, counts, safe outcome/error codes.

Expiry discovery, intent, reservation/session state changes and mandatory audit commit atomically. Lock compatible parent/session → reservation → scan/cleanup rows in deterministic order; no reverse acquisition against accepted Save/Submit/cancel/scan paths. Only OPEN sessions may become EXPIRED. Wall-clock expiry continues to block business commands synchronously even when discovery is delayed. Do not delete retained business rows or reservation evidence required by accepted FK contracts.

Future physical deletion remains post-commit. Authorization must recheck lease token and current eligibility; terminal reservation state, non-reusable keys and denied reactivation/finalization must make that proof stable across the future external call. A mere check-then-delete promise is insufficient; ambiguous identity is withheld. Completion requires current worker+attempt+token, unexpired lease and permissible state. Reclaim invalidates old tokens; stale success/error cannot overwrite new attempt or retry state. Preserve existing finite retry policy where possible, close final-lease-exhaustion recovery, distinguish retryable failure from retained/unsafe refusal. DB DONE represents a trusted worker report, not proof that this task physically deleted anything.

## Proposed remaining graph (unnumbered, unmaterialized)

- Accepted S07-002 → this cleanup eligibility/fencing contract → separately authorized physical cleanup runner and local Storage integration → operational deployment readiness.
- Accepted S07-002 → scanner execution/adapter with trusted object-read seam → provider selection/credentials and measured preproduction readiness. Interview scan request integration is a separate domain prerequisite for Interview upload consumers; do not pretend candidate protocol covers it.
- Accepted S07-001 → email sender execution/adapter → approved provider/config/templates and delivery operations. At-least-once provider delivery is not exactly-once logical enqueue.
- Accepted S07-001 history/RLS/delete contracts → Email History projection/UI. Seeded trusted history allows independent UI acceptance; live sender delivery is not a hard dependency.
- Existing Activity writers → contextual operational Activity projection/UI. Privileged immutable Security Audit presentation is separate; Submission profile activities are not this feed.
- Existing HR document read/signed-download surface + appropriate trusted upload/finalization contracts → HR/Interview document mutation consumers.
- Archive/export/purge remains separate Owner-approved scope under 42/66, never automatic housekeeping or a prerequisite for deleting genuinely unused temp objects.

These branches need not be serially numbered now. No canonical source mandates cleanup before Email History UI; this is a producer sequencing decision: establish the missing destructive-consumer safety contract before a physical runner, without provider or UI coupling. Exactly one task is materialized.

## Preservation, verification and source reopen

S07-002 retains no browser verdict, exact fingerprint, claim/lease/fencing, stale rejection, CLEAN necessary but not sufficient, PENDING_SCAN distinct from staged, one logical continuation, cancellation/expiry. S07-001 retains enqueue idempotency, worker fencing, trusted TEST/PRODUCTION provenance, exact Submission trace, contextual history and immutable audit. Neither provider contract is rewritten.

Future implementation verifies clean-install migrations, real SQL role denials, safety eligibility with current/historical references and detached-parent capture, signed-window deferral, expiry/finalize/cancel races, two-worker reclaim and stale result rejection, final lease exhaustion, audit rollback and idempotent discovery. Exercise only directly crossed S02/S04/S07 regressions plus adapter contracts. No live Storage/provider calls; physical deletion remains unverified debt. Exact accepted implementation SHA must run all impacted Web/DB jobs even after governance-only merge deltas; independent source review is never replaced by CI.

SOURCE_REOPEN_REQUIRED: false. An accepted predecessor would require reopening only if a current canonical invariant cannot be preserved by a downstream forward migration/consumer guard without changing that predecessor's business semantics. A missing worker, unsafe old queue row, provider-read seam, or stale historical planning prose is not itself such a contradiction. Escalate concrete incompatibility; never loosen retention, security or scan guards to make cleanup eligible.
