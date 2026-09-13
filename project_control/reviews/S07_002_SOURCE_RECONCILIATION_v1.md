# Slice-07 next-task source reconciliation — document scan contracts

Planning baseline: `93cd9942f928729ddd4e13179ccac0aafc734a51` on `autonomy/continuous-integration-20260905-01`. This is producer reconciliation, not independent review or a new product authority.

## Frontier result

`TASK-S07-001` is DONE and immutable at `checkpoint/S07-001-accepted-001` → `8397be35d64a65f4a693811e4fc6b9e43287a7cd`. The Owner-transported external ChatGPT final acceptance audit is PASS, source reopen is false, and the audit hold is released. No later S07 task exists, no Executor is active, and the accepted-to-planning delta contains governance evidence only.

The smallest next source-backed dependency cut is **durable document-scan request and result-fencing trusted contracts**. It is prerequisite security infrastructure for later provider-independent scan execution and document consumers. It does not reopen S07-001 and does not implement a scanner provider, physical cleanup worker, email provider runtime, or UI.

## Current source and implementation reality

- `source_registry.yaml` v1.18 marks review-pack modules 11, 37, 39, 41, 42, 47, 48, 55, 59, 63, 66, 73, 99 and 100 CURRENT/normative. Effective accepted migrations outrank starter schema.
- 11 §§5–9, 37 §10/§16, 41, 42, 47 and 48 require private two-phase upload, post-commit malware-scan orchestration, mandatory `CLEAN` before finalization, durable temp cleanup, and immutable minimal Security Audit distinct from ordinary Activity.
- Current `upload_reservations` records one Candidate-form or Interview parent, temp bucket/path, checksum, scan state and expiry. `storage_cleanup_queue` already persists cleanup intent and leased claims; it must remain separate from scan work.
- Current `web/src/app/candidate/candidate-actions.ts` invokes `upload-scanner.ts` in the request path. That scanner downloads the object through the admin client, calls a configured scanner URL, and submits a service-role result. No durable scan request/attempt protocol, exact object-generation binding, lease fencing, or durable scanner runner exists. `validate_and_scan_upload_reservation` accepts a worker result but cannot fence stale/replaced work.
- Candidate Save/Submit and Interview finalization already recheck unexpired reservation state and `VALIDATED` + `CLEAN`. Those synchronous guards remain authoritative: worker lag, retries, or cleanup never make a document finalizable.

## Reconciled next task boundary

Materialize one task only: `TASK-S07-002 — Document Scan Request and Result-Fencing Trusted Contracts`.

The task owns the durable scan-request state and trusted worker completion contract:

1. Record a post-upload scan request atomically against the exact reservation, private bucket/path, checksum, size and immutable object-generation/version identity; same reservation/retry must not create a second logical scan request.
2. Restrict claim and result transitions to a narrowly trusted server/worker boundary. Use bounded due claims, lease ownership/fencing and finite retry semantics; a stale completion must not overwrite a reclaimed/newer attempt.
3. Revalidate reservation ownership, parent/session current state, expiry, private object identity and checksum at result persistence. `CLEAN` is the only result that can enable existing finalization guards. `INFECTED`, `ERROR`, missing or stale results remain non-finalizable and preserve/trigger only the existing safe cleanup path.
4. Move request-path scanning out of the Candidate server action into the durable protocol. Browser data and arbitrary authenticated callers never provide a verdict, worker identity, object path, or `CLEAN` transition.
5. Keep Security Audit minimal and transactional for state transitions. Do not make Activity a Security Audit substitute or a business-retention reference.

No source contradiction requires reopening S07-001: email persistence and document scanning use different durable work identities, permissions, retention purposes and external boundaries.

## Deliberate exclusions and later cuts

The following are source-backed but intentionally unmaterialized:

- trusted scanner runtime/provider configuration and production credentials, consuming the S07-002 protocol;
- physical Storage cleanup worker execution and its own stale-claim fencing/retry repair over `storage_cleanup_queue`;
- email provider sender runtime consuming S07-001 outbox protocol;
- manual Email History/Activity/document UI consumers;
- archive/export/purge, which needs the separate owner-approved runbook and is never automatic.

Combining scanner runtime, Storage cleanup, email delivery and UI would blur independent post-commit work identities and violate verification economy. Each later cut must be reconciled at its own frontier.

## Source authority and gates

Primary authority: `11_EMAIL_DOCUMENTS_AND_ACTIVITY_LOG.md` §§5–9; `37_BACKEND_COMMAND_CONTRACTS.md` §§3, 10 and 16; `41_STORAGE_AND_UPLOAD_SECURITY.md`; `39_SECURITY_RLS_MATRIX.md`; `59_RLS_POLICY_BLUEPRINT.md`; `42_PRIVACY_RETENTION_COMPLIANCE.md`; `47_AUDIT_LOGGING_SPEC.md`; `48_IDEMPOTENCY_CONCURRENCY_SPEC.md`; `55_COMMAND_COVERAGE_MATRIX.md`; `63_BATCH_OPERATION_SEMANTICS.md`; `66_DATA_EXPORT_ARCHIVE_PURGE_RUNBOOK.md`; `73_DOMAIN_GLOSSARY_AND_CANONICAL_PREDICATES.md`; `99_INDEPENDENT_REVIEW_IMPLEMENTATION_ALIGNMENT_V1_18.md`; `100_TECHNICAL_PRECODE_GATE_V1_18.md`; and `app_spec.yaml`.

Accepted implementation authority to inspect before execution: S02 upload-reservation and form-session migrations, S04 interview lifecycle migration, accepted S06 authorization helpers, and S07-001 email persistence migration/test. No connected Supabase action, production scan, provider credential, deployment, main mutation or PR action is authorized.

SOURCE_REOPEN_REQUIRED: false.
