# TASK-S07-003 — Storage Cleanup Eligibility and Result-Fencing Trusted Contracts

## Dispatch gate and exact baseline

This is an implementation prompt for future Owner dispatch, NOT current implementation authority. Current continuation stops after independent prompt/source PASS. Execution is permitted only after external prompt audit and explicit dispatch.

Repository: `oanhpham-kobe/eiu-recruitment`. Integration: `autonomy/continuous-integration-20260905-01`. Starting audited reporting SHA: `37b01169394378bf666a6baa440a2431407b22d6`; external audit-release commit: `916febb43fb5ab87b1065de677bbcfaed4c74cf5`. Governed implementation baseline is the exact peeled commit of immutable `checkpoint/pre-S07-003-001`, or the latest independently PASS numbered replacement recorded in TASK_REGISTRY before dispatch. Resolve the ref and compare with the review's REVIEWED_SHA; never use a moving integration HEAD as a substitute. The baseline commit contains this prompt, so its own SHA is recorded by immutable ref and later evidence, not a fabricated self-hash.

Accepted predecessors: S07-001 `checkpoint/S07-001-accepted-001` → `8397be35d64a65f4a693811e4fc6b9e43287a7cd`; S07-002 `checkpoint/S07-002-accepted-001` → `d99776aa6e07c0023ada9906211f6d1d4b17f5ed`. S07-002 formal exact-SHA Web+DB CI `34765432362` PASS; R9 and integration equivalence PASS. These checkpoints remain immutable.

Dependencies: TASK-S02-003, TASK-S02-004, TASK-S04-002, TASK-S07-002; all DONE. Materialize/execute no sibling task or Slice-08.

## Source authority and preflight

Read `project_control/reviews/S07_003_SOURCE_RECONCILIATION_v1.md`, accepted S07_001/S07_002 source reconciliations, current runtime/DAG, REVIEW.md and canonical current sections:

- review_pack/11_EMAIL_DOCUMENTS_AND_ACTIVITY_LOG.md §§5–9;
- 37_BACKEND_COMMAND_CONTRACTS.md §§3,10,16 and trusted document deletion;
- 41_STORAGE_AND_UPLOAD_SECURITY.md (private buckets, staged lifecycle, signed bounds, durable Interview cleanup);
- 42_PRIVACY_RETENTION_COMPLIANCE.md and 66_DATA_EXPORT_ARCHIVE_PURGE_RUNBOOK.md;
- 39_SECURITY_RLS_MATRIX.md, 59_RLS_POLICY_BLUEPRINT.md;
- 47_AUDIT_LOGGING_SPEC.md, 48_IDEMPOTENCY_CONCURRENCY_SPEC.md, 73_DOMAIN_GLOSSARY_AND_CANONICAL_PREDICATES.md;
- source_registry.yaml and app_spec.yaml cleanup/retention/session sections.

Effective ordered migrations and actual callers outrank starter schema and historical observations. Inspect queue schema, all effective queue producers, reservation signing/finalization and current/historical version references. Use symbol references before changing exported adapters; preserve user changes. Parent owns Todo and integration. Material DB work uses the project DB executor when delegated; no concurrent writers in one worktree.

## Bounded outcome

Provide a safe trusted database contract for a **later** physical cleanup worker over the existing storage_cleanup_queue. This task owns eligibility, bounded reservation-backed expiry capture, attempt leases/fencing, retry/exhaustion, minimal audit, adapter migration and tests. It does not own physical object deletion, bucket sweeps, provider execution, scheduling or deployment. Protocol-only acceptance is intentional, not a claim that physical cleanup now works.

### A. Durable discovery and capture

Add a bounded trusted command to discover expired known Form Sessions/upload reservations and durably capture managed temp paths. Same identity replays without duplicate logical work. OPEN→EXPIRED only; do not change submitted/cancelled terminal sessions or persisted documents. Respect wall-clock expiry independently of housekeeping. Capture provenance and safety bounds before any permitted reservation cleanup; do not delete evidence required by FK/scan requests. Existing detached-parent queue rows must remain assessable after parent deletion; add narrow forward producer changes where needed for durable provenance, without rewriting accepted business semantics.

Discovery, state transition, durable intent and mandatory safe expiry-summary audit commit atomically. Audit/capture failure rolls back. Use bounded batches and deterministic ordering. No Storage listing, arbitrary path ingestion or business-record TTL purge.

### B. Eligibility and reference protection

Queue presence and reason_code do not authorize deletion. Before exposing executable cleanup work prove:

1. server-generated private managed temp bucket/path identity and safe durable provenance;
2. terminal/expired unused reservation or valid detached-parent intent;
3. elapsed maximum reservation/signed-upload/not_before bounds;
4. no live reservation can still write/finalize that identity;
5. no current OR historical Submission/Interview document version references the object.

Recheck eligibility with current lease at a narrow authorization seam immediately before a future external delete, and on completion where relevant. Define a stable handoff: terminal/non-reusable identity and rejected future finalization prevent check-to-use resurrection. If existing metadata cannot prove identity, fail closed and retain a diagnosable withheld outcome rather than guessing. Never authorize historical replacement objects simply because DOCUMENT_REPLACED is queued. No current-only reference test. Unsafe/protected jobs are not reported physically DONE and must not loop unboundedly.

Preserve signed-upload deferral for all producers, including S07-002 rejection/error and detached Interview deletion. Do not weaken finalized version retention or turn housekeeping into archive/purge.

### C. Narrow worker protocol

Use the existing queue rather than a generic queue framework. Add worker identity, per-claim attempt identity/fencing and unexpired lease compare-and-set. Bounded SKIP LOCKED claims; stale reclamation invalidates prior token. Complete only the active matching worker/attempt/token; reject stale success and stale failure without altering a newer claim. Same valid completion replay must have defined idempotent behavior. Finite retry/backoff must preserve existing policy where compatible, safely classify terminal/withheld work, and recover final-attempt lease expiration without a permanently PROCESSING row or unbounded sixth attempt.

Narrow non-login worker role, explicit schema/function grants, no browser/anon/authenticated capability to claim/authorize/complete or forge cleanup audit; remove obsolete broad result APIs/grants after migrating all callers. Avoid broad service-role worker bypass. Safe error codes only; no raw provider/body/file/secret/signed-URL audit data. Audit transitions transactionally, separate from operational Activity and retained email history.

DB transactions never include a Storage/network call. Completion records a trusted report; tests simulate that report but do not claim a real object was removed. Future deployment binds worker credentials separately.

### D. Locking and predecessor compatibility

Map effective locking of Candidate Save/Submit/cancel, Interview finalize/delete, scan completion/cancellation and queue producers. Parent/session → reservation → scan/cleanup acquisition must remain compatible; do not lock cleanup then acquire a producer's parent in reverse order. Refresh wall-clock validity after blocked locks. Protect eligibility against concurrent finalize, cancellation, signed-URL registration and replacement.

Preserve S07-002 browser/verdict separation, exact fingerprint, worker fencing, stale rejection, CLEAN necessary but insufficient, PENDING_SCAN distinction, exactly-once logical continuation and expiry/cancellation fences. Preserve S07-001 logical enqueue idempotency, leases, trusted environment, exact Submission production trace and contextual history. No replacement of accepted migrations: forward migration only. A downstream eligibility refusal is not source reopen; escalate only a concrete irreconcilable canonical predecessor contradiction.

### E. Existing consumers

Update `web/src/lib/commands/storage-reservation.ts` cleanup adapters and all real callers/tests for the clean contract cutover. No old ID-only completion alias. No UI changes or new browser cleanup route. Inspect migration-specific producer and assertion callers rather than assuming wrappers are the only callers. Preserve non-cleanup adapters unchanged.

## Non-goals and external boundaries

No scanner adapter/provider/credentials; no email sender/provider/templates; no physical Storage.remove or cleanup runner/scheduler; no connected Supabase operation; no real email; no document/Activity/Email History UI; no Interview scan integration; no archive/export/purge/automatic retention; no TTL tuning from imagined provider latency; no Vercel deploy; no main push/merge; no PR. Local disposable SQL fixtures are permitted during future implementation, not destructive live execution. Existing accepted checkpoints never move.

## Verification and acceptance

Keep regression tests that defend observable uncertain safety edges, not source-text assertions or mock echoes. Required focused evidence:

- clean migration replay and SQL role/grant denials, including direct helper/audit/legacy API bypass;
- known expired reservation discovery is bounded/idempotent, deferred through signed window, audit rollback, terminal session safety and detached-parent provenance;
- current and historical candidate/interview references, live reservations, unknown identity and protected replacement intent never yield executable cleanup authority;
- two actual concurrent DB sessions: one claim owner; reclaim invalidates old completion/authorization; stale success/error cannot clobber new work; final lease exhaustion settles safely;
- expiry/cleanup versus Save/Submit/finalize/cancel races preserve versions and lock order;
- typed adapter contract/error handling and explicit no-physical-deletion claim.

Crossed tests: affected S02 reservation/staged plan/cancel/finalization; S04 Interview delete/finalize and retained-version references; S07-002 protocol/fencing/terminal cleanup; S07-001 tests only if email/retention seams actually change. Use source impact to select, never run the whole repository repeatedly. Do not weaken tests. Run broader impacted verification once on final candidate; exact acceptance SHA must actually run every impacted domain (likely Web+Database), not only an impact resolver that skips jobs on a governance-looking merge. One authorized broadened acceptance run may be needed after serialization; avoid repeated full CI.

## Review, serialization and stop

After future authorized implementation: focused proof → independent exact-SHA implementation review → bounded repairs/re-review → serialized integration and exact integration equivalence when SHA changes → fresh exact-SHA impacted domain CI → immutable `checkpoint/S07-003-accepted-001` only after all gates pass → governance evidence sync. Parent verifies worker output and actual diff. Preserve previous failed review/CI evidence, label skipped jobs truthfully, and distinguish accepted product SHA from later governance reporting HEAD. Changes to accepted SHA invalidate old exact review/CI coordinates; never move an accepted checkpoint to hide that change.

Current planning lifecycle instead freezes numbered pre-task checkpoints, obtains `eiu-reviewer` prompt/source PASS with SOURCE_REOPEN_REQUIRED:false, and stops for ChatGPT audit/dispatch. No implementation may start merely because this prompt is PASS or dependencies are DONE.
