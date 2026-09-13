# SLICE-07 / TASK-S07-002 — Document Scan Request and Result-Fencing Trusted Contracts

## Identity and execution gate

- TASK_ID: `TASK-S07-002`
- SLICE: `SLICE-07 — Email / Documents / Activity / Workers`
- TYPE: backend persistence/security prerequisite; not scanner-provider delivery, Storage cleanup execution or UI.
- AUDIT-RELEASE BASE SHA: `93cd9942f928729ddd4e13179ccac0aafc734a51` on `autonomy/continuous-integration-20260905-01`.
- GOVERNED IMPLEMENTATION START REF: `checkpoint/pre-S07-002-001`. It must be created from and resolve exactly to the frozen prompt-review baseline before any implementation worktree or Executor starts.
- This prompt authorizes no implementation by itself. Require an independent `eiu-reviewer` PASS against the exact frozen prompt baseline, then a subsequent ChatGPT/Owner implementation-dispatch decision. Resolve the governed ref directly at dispatch; never substitute a moving branch.
- SOURCE_REOPEN_EXPECTATION: false. Preserve accepted S01–S07-001 contracts and report concrete contradictions rather than redefining predecessors.

## Accepted dependencies

Direct DAG dependencies: `TASK-S02-003`, `TASK-S02-004`, `TASK-S04-002`, `TASK-S06-002`, and `TASK-S07-001`; all are DONE.

Required predecessor coordinates:

- `checkpoint/S07-001-accepted-001` → `8397be35d64a65f4a693811e4fc6b9e43287a7cd`.
- S07-001 reviewed application, serialized Integration CI, and accepted checkpoint all remain that exact SHA.
- S02 supplies private two-phase Candidate upload reservation/staging and synchronous finalization guards; S04 supplies Interview upload/finalization and durable pre-hard-delete cleanup capture; S06 supplies accepted authorization/RBAC helpers.

No accepted checkpoint moves. This prompt materializes no later Slice-07 task.

## Canonical source authority

`recruitment_webapp/review_pack/source_registry.yaml` v1.18 selects the current normative modules. Business v1.2 and Technical v1.18 remain frozen. `15_ALL_IN_ONE_SPEC.md` is navigation only; `app_spec.yaml` is structured current contract; effective accepted migrations outrank the starter schema.

Read and reconcile these before implementation:

- `11_EMAIL_DOCUMENTS_AND_ACTIVITY_LOG.md` §§5–9: private document identity, immutable Security Audit versus Activity and retention boundary.
- `37_BACKEND_COMMAND_CONTRACTS.md` §§3, 10 and 16: Form/Reservation expiry, trusted upload commands, cleanup and post-commit worker boundary.
- `41_STORAGE_AND_UPLOAD_SECURITY.md`: private two-phase upload, mandatory scan `CLEAN`, exact logical/version identity and async cleanup.
- `39_SECURITY_RLS_MATRIX.md` and `59_RLS_POLICY_BLUEPRINT.md`: exact parent context, private Storage and server-authorized signed URLs.
- `42_PRIVACY_RETENTION_COMPLIANCE.md`, `47_AUDIT_LOGGING_SPEC.md`, `48_IDEMPOTENCY_CONCURRENCY_SPEC.md`, `55_COMMAND_COVERAGE_MATRIX.md`, `63_BATCH_OPERATION_SEMANTICS.md`, `66_DATA_EXPORT_ARCHIVE_PURGE_RUNBOOK.md`, `73_DOMAIN_GLOSSARY_AND_CANONICAL_PREDICATES.md`, `99_INDEPENDENT_REVIEW_IMPLEMENTATION_ALIGNMENT_V1_18.md` and `100_TECHNICAL_PRECODE_GATE_V1_18.md`.
- Existing effective migrations/commands/tests for Candidate form uploads, Interview uploads, `storage_cleanup_queue`, and accepted S07-001 persistence. Inspect current `web/src/lib/storage/upload-scanner.ts`, Candidate upload action and storage command adapters before changing them.

## Scope

Implement one durable, provider-independent document-scan protocol for existing upload reservations.

1. **Durable request identity.** After a private object upload is recorded, persist one logical scan request bound to the exact `upload_reservation_id`, parent/session, private bucket/path, object generation or equivalent immutable object identity, checksum, detected/declared metadata and expiry. Retrying the same reservation must replay the same logical request; a changed object identity/fingerprint fails closed and never silently reuses an old clean verdict.
2. **Post-commit worker protocol.** Replace request-path scanner invocation with durable scan work. Implement bounded due claims, finite retry/backoff, worker/attempt identity, lease expiry/reclaim and a fencing token. Concurrent workers must not own one live attempt. Late completion from an expired or replaced lease must not mutate the current request.
3. **Trusted result persistence.** Only a narrow trusted server/worker path may claim or complete scan work. Recheck the exact reservation, form/interview parent, expiry, bucket/path, immutable object identity and checksum at completion. Browser input, ordinary authenticated callers and arbitrary service-facing adapters cannot assert worker identity, scanner verdict, `CLEAN`, object path or result metadata.
4. **Security outcome.** `CLEAN` can make the existing reservation eligible for finalization only after the authoritative existing finalization guards recheck `VALIDATED`, `CLEAN`, unexpired state, parent/session eligibility, exact current target and count/CV rules. `INFECTED`, `ERROR`, absent, expired or stale results must remain non-finalizable; preserve or schedule only the existing safe cleanup path. Never synthesize `CLEAN` because a scanner is absent or a worker retries.
5. **Server/action cutover.** Candidate upload completion records server-derived object facts and returns safe pending state. It does not download/scan the object inline, accept a browser verdict or stage/finalize a file before durable trusted `CLEAN`. Preserve existing Candidate authorization and structured errors; do not add a UI feature.
6. **Audit/privacy.** Security-relevant request/result/rejection transitions record minimal immutable Security Audit in the same relevant database transaction. Do not store object content, signed URLs, scanner tokens, secrets or whole PII rows. Activity remains an operational concept and is not an audit substitute or a business-usage/retention reference.

## Explicit non-goals

Do not implement a scanner provider/runtime, call a real scanner, add scanner credentials, deploy a worker/scheduler, or claim malware production readiness. Do not implement physical Storage deletion/cleanup worker execution or redesign its existing queue; do not implement email sender runtime, email/history/Activity/document UI, attachment delivery, archive/export/purge, automatic business retention, document preview conversion, generic queues, or any Slice-08 work. Do not change accepted S07-001 email contracts, checkpoints, production data, main, PRs, deployments or connected Supabase.

## Required trust, database and Storage constraints

- Forward migrations only. Never edit accepted migrations or weaken S02/S04 form-session, reservation, document-version, cleanup-capture, RLS, grants or S07-001 contracts.
- Private Storage only; object keys are server-generated. Signed URLs remain short-lived and server-authorized under exact Candidate/HR/Interviewer parent context. No browser direct table mutation or service-role credential exposure.
- Preserve one-parent reservation invariant, 5 MB/file and five-current-file limits, required CV, approved MIME/extension and magic-byte validation. HTML/SVG/executables/scripts/archives remain rejected.
- Finalization is business-transactional. Scan orchestration is post-commit durable work; database rollback cannot undo object upload. Cleanup is housekeeping only and must not relax wall-clock expiry or current-version/retention guards.
- Use SECURITY DEFINER only where necessary, with empty `search_path`, fully-qualified references, strict grants/revokes and no caller-controlled worker/result authority.
- Do not promise exactly-once scanning or deletion. One logical scan request may have retried attempts; stale/replayed results are fenced and auditable.

## Concurrency, idempotency and regression acceptance

Before review, prove at least these observable contracts:

1. sequential and concurrent upload-completion retries create/replay one logical scan request; changed checksum/path/object identity is rejected;
2. two workers cannot claim one live scan attempt; expiry permits bounded reclaim; stale completion cannot overwrite a newer claim;
3. worker result for an expired, cancelled, replaced or wrong-parent reservation is rejected without marking it `CLEAN`;
4. `CLEAN`, `INFECTED`, `ERROR` and missing scanner result preserve correct finalization eligibility; finalization remains denied until all existing synchronous guards pass;
5. Candidate/browser and untrusted authenticated/service-facing callers cannot claim or complete scan work, forge result metadata, or access unrelated private object/reservation context;
6. minimal immutable audit persists for relevant transitions, audit failure rolls back its mutation, and no signed URL/token/content is persisted;
7. crossed S02 Candidate form/session/staged-document tests, S04 Interview document/finalization/hard-delete cleanup-capture tests, S06 authorization/RLS tests and S07-001 email persistence tests remain unchanged except for direct, justified contract adaptations.

Use a fresh disposable local Supabase replay and provider-independent simulated worker outcomes. Do not call external scanners or connected Supabase. Add permanent tests only for plausible contract failures above; do not add source-text or plumbing assertions.

## Verification economy and lifecycle

Run focused SQL/RLS/staged-concurrency tests for the new scan protocol, affected server-action/adapter tests, and directly crossed S02/S04 regressions. Run DB lint/advisors only when their usual scope is touched. Do not rerun unrelated email, web UI, browser, PRE-S04/S05/S06 or full suites without impact evidence. Never set `full_verification=true` for planning or prompt artifacts; exact Integration CI selects impacted domains.

Require focused verification, producer self-review, independent exact implementation-SHA `eiu-reviewer` PASS/no source reopen, serialized integration, exact-SHA CI, final equivalence review if integration changes SHA, and an immutable accepted checkpoint. The review/repair loop is bounded to concrete findings. A changed SHA invalidates prior approval.

## Prohibited actions and next-frontier behavior

No main push/merge, PR creation/merge, deployment, Vercel action, production mail, provider/SMTP/scanner credentials, real provider/scanner invocation, connected Supabase migration, force push, accepted checkpoint rewrite or second task materialization. No Executor starts in this prompt-gate continuation.

After independent prompt review PASS, stop and return the exact baseline, prompt and review evidence to ChatGPT for implementation-dispatch decision. Do not infer or dispatch implementation in this continuation.
