# SLICE-07 / TASK-S07-001 — Email Outbox and History Trusted Persistence Contracts

## Identity and execution gate

- TASK_ID: TASK-S07-001
- SLICE: SLICE-07 — Email / Documents / Activity / Workers
- EXECUTION_MODE: AUTONOMOUS
- TYPE: backend persistence/security prerequisite; not provider delivery or UI
- Planning baseline: `26c186bae8eec12bf8b8d2571238709a6e597c24` on `autonomy/continuous-integration-20260905-01`.
- Audit-hold release commit: `ad597826c31a0c2d1ec3deaa9a11689c63292af2`.
- Implementation is NOT authorized by this prompt's creation. Require independent exact-SHA prompt/source PASS and a subsequent Owner/ChatGPT implementation-dispatch decision. Resolve the released exact implementation base at dispatch; if product changes after this planning baseline, reconcile affected contracts before execution. Never substitute a moving branch for a review SHA.
- SOURCE_REOPEN_EXPECTATION: false. Preserve immutable S01–S06 contracts; report concrete contradictions rather than silently redefining them.

## Accepted dependencies

Direct DAG dependencies: TASK-S06-001 and TASK-S06-002 (both DONE). Their transitive predecessor chain supplies identity, Candidate Submission/document transactions, Application/Interview/report context and audit/idempotency helpers.

Immutable checkpoints:
- `checkpoint/S06-001-accepted-001`: `59be9b2c92906065b8e4baa902fcec1d4cbefa12`.
- `checkpoint/S06-002-accepted-001`: `5f2b76c7f1e901b3cadb847906efcd1568c8cbc3`.
- `checkpoint/SLICE-06-accepted-001`: `51686bfe8c12581f5eb82a6cef4daed27dc93fe1`, including accepted Copy/User composition repair.

No accepted checkpoint moves. No second Slice-07 task is authorized by this artifact.

## Canonical source authority

`recruitment_webapp/review_pack/source_registry.yaml` selects CURRENT normative sources. Business v1.2 / Technical v1.18 remain frozen. `15_ALL_IN_ONE_SPEC.md` is a generated CURRENT-only navigation compilation, not an independent normative override; `app_spec.yaml` is the structured current contract. `database_schema.sql` is a starter, not a substitute for effective accepted migrations.

Read these current modules and the relevant named sections:
- `11_EMAIL_DOCUMENTS_AND_ACTIVITY_LOG.md`: manual actions, transactional outbox, history/audit separation, Candidate notification transaction, Email History authorization/cleanup.
- `37_BACKEND_COMMAND_CONTRACTS.md`: §§11/16, `bulk_enqueue_email`, `delete_email_history`, Candidate notification side effect, Submission hard-delete/retained production trace.
- `43_EMAIL_DELIVERY_SPEC.md`: logical enqueue versus delivery retry, lease fields, stale-preview guard, TEST environment default.
- `47_AUDIT_LOGGING_SPEC.md`: same-transaction audit/rollback, minimal payload, privileged access.
- `48_IDEMPOTENCY_CONCURRENCY_SPEC.md`: scope/key replay, fingerprint mismatch and deterministic bounded bulk ordering.
- `02_ROLES_PERMISSIONS_AND_NAVIGATION.md`, `39_SECURITY_RLS_MATRIX.md`, `59_RLS_POLICY_BLUEPRINT.md`: email permissions and exact parent context, Root semantics.
- `08_DATA_MODEL_AND_FIELD_DICTIONARY.md`, `40_DATABASE_INVARIANTS.md`, `55_COMMAND_COVERAGE_MATRIX.md`, `command_registry.yaml`: entity identity, explicit trusted writers and invariants.
- `42_PRIVACY_RETENTION_COMPLIANCE.md`, `66_DATA_EXPORT_ARCHIVE_PURGE_RUNBOOK.md`, `73_DOMAIN_GLOSSARY_AND_CANONICAL_PREDICATES.md`: no automatic purge, retained business trace, cleanup classifications; this task does not implement archive/purge.
- `63_BATCH_OPERATION_SEMANTICS.md`, `68_RATE_LIMIT_POLICY.md`: per-item email batch results, maximum 100 targets, delivery throttling separate from valid Candidate Save.
- `41_STORAGE_AND_UPLOAD_SECURITY.md`: document/scan boundaries retained, not implemented here.
- Current alignment/gate `99_INDEPENDENT_REVIEW_IMPLEMENTATION_ALIGNMENT_V1_18.md` and `100_TECHNICAL_PRECODE_GATE_V1_18.md`.

Historical/superseded review modules cannot override current source. Skills are implementation guidance, never product authority.

## Reconciled implementation starting point

- `20260906005000_pre_s04_contract_repairs.sql` creates `public.email_outbox`: exact entity FKs, TEST default, QUEUED/SENDING/SENT/FAILED/CANCELLED, lease/attempt/provider fields, unique actor_scope/email_type/idempotency_key, server-only DML. Its effective Candidate Submit/Update writers enqueue inside their transactions. Earlier migration PRODUCTION literals are superseded; inspect latest effective definitions rather than patching history.
- `20260906070000_interview_lifecycle_commands.sql` creates `email_history`, contextual SELECT policy and entity FKs. History currently defaults PRODUCTION, while outbox defaults TEST: reconcile new history to trusted source-outbox environment, never relabel historical records.
- `20260905120000_bulk_submission_status_and_application_assignment.sql` supplies Activity/Security Audit and idempotency infrastructure. Reuse current effective helpers and ACLs.
- `20260905030000_identity_schema.sql` seeds `interviews.email`, `emails.history_view`, `emails.history_delete` and dependencies. Use accepted S06 authorization helpers/trusted session; never create another permission model.
- No implemented public email enqueue/bulk/history-delete or durable sender runtime was found in planning. Confirm against actual implementation base.

## Smallest coherent task boundary

Deliver a complete database-backed email persistence command surface usable by a later trusted provider worker and later UI: validated logical enqueue, same-transaction required Candidate notification, worker-only claim/result persistence, contextual history read/cleanup. These share one message identity, state machine, audit and retention boundary and are reviewed together.

Out of scope: external provider calls/credentials/SMTP configuration, actual scheduler/worker service deployment, final Owner email copy/templates, email/history/Activity UI, malware scan workers or scan-provider choice, document upload changes, storage cleanup worker implementation, generic queue platform, archive/export/purge, automatic business retention, PDF assets, branch protection, Slice-08, and all unrelated predecessor repairs. Database worker protocol is included; production provider delivery is explicitly not claimed by this task.

## Required trusted contracts

### Logical enqueue and Candidate transactions

Implement one canonical trusted enqueue core and authorized entry points matching `enqueue_email`/`send_email` semantics; `send` means enqueue, never a provider call inside PostgreSQL/business transaction. Manual Interview actions require `interviews.email` and exact parent/context permission. Do not change Interview status by sending.

Derive/validate recipients from email type and exact entity/current participants or trusted HR-recipient configuration. No arbitrary recipient override, arbitrary actor, parent reassignment, environment selection or attachments from the browser. Existing canonical recipient configuration must be reused; if missing, introduce the smallest trusted configuration surface, not hardcoded real recipient addresses or invented production templates. Validate related Submission/Application/Interview IDs form the same actual parent chain. Unsupported types fail closed.

Snapshot To/CC where applicable, subject/body/template version, and authoritative schedule/participant fingerprint. Require preview/version binding at enqueue for manual email; reject stale schedule or recipient sets. Recheck the same authoritative fingerprint at the worker send-authorization boundary before returning deliverable payload. This DB gate cannot make an external provider call atomic with later business changes; do not promise that guarantee. No provider call is in this task.

Required Candidate Submit/Update HR notification remains inside the accepted business transaction, linked to exact submission_id. No second client send call. Preserve accepted confirmation behavior. Reuse existing writers; any narrow forward replacement must preserve every existing privacy/session/document/status/result invariant and receive crossed regressions. Delivery quotas delay downstream delivery, never roll back otherwise-valid Candidate Save; failure to persist mandatory logical enqueue/audit does roll back transaction.

Environment is trusted deployment configuration with safe TEST default in Local/CI/DEV, never a caller-controlled switch or hardcoded PRODUCTION RPC. A trusted PRODUCTION configuration must produce retained PRODUCTION outbox/history with exact Submission linkage. Do not rewrite existing historical classifications.

### Idempotency and bulk

Same actor/scope/command/key with same normalized request returns stored logical result; changed payload rejects, no duplicate enqueue. Serialize concurrent same-key requests and persist result/audit atomically. Authorization happens before exposing a replay. Preserve accepted Candidate form-session idempotency and exact notification identity across Save retries.

`bulk_enqueue_email` has per-item enqueue results (`success[]`, `failed[{id,error_code}]`), not all-or-nothing delivery. Bound to 100, validate every target/context, acquire shared locks in deterministic order and use stable per-item idempotency identities so retries do not recreate successful items. Invalid/unauthorized item must not leak hidden parent data or roll back unrelated successful items. Keep bounded transaction/subtransaction behavior explicit; no browser loops masquerading as batch command.

### Durable worker database protocol

Implement worker-only bounded claim and result transitions over existing outbox, not a second queue: QUEUED -> SENDING -> SENT or retryable/terminal FAILED, with explicit CANCELLED handling. Define finite retry policy/backoff, due-time checks, lease expiry/reclaim, attempts, worker ownership, structured safe errors and provider IDs using existing fields plus minimal necessary attempt identity/history.

Concurrent workers cannot own one live attempt; use SKIP LOCKED/equivalent and an attempt/lease fencing token. Late completion from an expired/replaced lease must not overwrite a newer attempt. Crash before completion permits recovery; provider-accepted then crash can duplicate external delivery and must remain auditable as distinct attempts of ONE logical message. Never promise exactly-once delivery or synthesize SENT without trusted worker result. Repeated completion of the same attempt must not duplicate history/audit. Preserve logical trace across attempts; canceled/terminal work is not claimable without an explicitly authorized retry contract.

Delivery result and corresponding Email History/send/failure Security Audit commit together. History copies environment and exact parent binding from trusted outbox, not worker-supplied replacements. Only narrowly trusted server/worker credentials may claim/complete; authenticated/Candidate/Interviewer callers cannot forge worker identity/results. No secrets or unrestricted service-role surface in browser. Test the database protocol with simulated outcomes, not live external mail.

### History, cleanup, retention and audit

History SELECT requires `emails.history_view` plus current exact parent read context derived from email_type; raw IDs, broad role membership and unrelated parent permission do not grant access. Reuse accepted S04/S05 contextual and S06 Root rules; minimum safe projections must not expose body/recipient PII outside authorized context. Root implicit permission still obeys integrity guards and audit requirements.

`delete_email_history` requires history view+delete and same parent context. Accept TEST_RECORD only for environment TEST, or WRONG_RECORD with nonblank reason. Reject all other classifications. Lock/revalidate row and context, atomically append immutable audit (actor, parent, classification/reason) then remove operational history. Audit failure rolls back deletion. Do not silently delete/rewrite outbox/provider attempts or security audit to make cleanup succeed.

Normal successful production Submit/Update produces retained PRODUCTION logical email trace bound to exact Submission immediately at enqueue, before delivery. Retained outbox/history continues to block normal Submission hard-delete; delivery failure/cancellation/history cleanup must not create a normal HR hard-delete route. `delete_unused_submission` remains MAINTENANCE_ONLY. Truly unused test cleanup is distinct from production retention; do not add automatic purge or weaken retained FK/usage checks. Domain email business trace is not the same as Activity/Security Audit: Activity/Audit alone is not a business-usage reference for cleanup decisions.

All mandatory permission/status/business invariants and Security Audit remain in business transactions. Payloads include event/actor/entity/version/changed-field names and necessary reason, not whole PII rows, tokens, signed URLs or secrets. Operational Activity visibility cannot expose immutable privileged Security Audit.

## Concurrency and regression acceptance

Before review, keep permanent behavior tests for plausible failures:
1. Sequential/concurrent same-key enqueue; mismatched fingerprint; different actor/context isolation; lost-permission replay denied.
2. Exact Candidate Submit/Update transaction rollback on enqueue/audit failure and success with exact Submission trace; no delivery-quota rollback; TEST default and trusted PRODUCTION retention behavior.
3. Forged email type/recipient/parent/environment/attachment and stale preview rejected; current participant changes versus enqueue/send authorization staged under locks.
4. Two worker claims, expiry/reclaim, stale completion fencing, retry exhaustion, canceled work, repeat completion, provider-accepted/crash attempt trace and one logical message identity.
5. History permission+parent matrix, unrelated parent denied, TEST/WRONG cleanup classification and reason, immutable audit survival and rollback, production outbox retention after operational history cleanup.
6. Partial bulk success/error contract, 100 bound, replay and deterministic overlapping-target locking.
7. Crossed retained Candidate Submit/Update/document staging, normal production deletion denial, Application/Interview/Copy and S06 RBAC/identity tests; no accepted assertion weakening.

## Implementation and verification discipline

Forward migrations only; never edit accepted migrations or starter source as production implementation. Reuse repository error/result/idempotency/audit and private helpers. Explicit RLS/grants/revokes; SECURITY DEFINER only justified with empty search_path and fully qualified references. No direct browser table mutation. Any new adapter must use trusted session and explicit server authorization; no raw identity fallback.

Eventual Executor: load relevant project Supabase/Postgres/security skills, inspect pinned versions and current docs before platform-specific implementation. Use repository-native migration convention, fresh disposable local replay, focused SQL/RLS and staged concurrency tests; prove failed conditions pre-fix where practical. Existing official cumulative Integration CI must retain its ordering including standalone bulk reset. Add focused email persistence gate without replacing predecessor gates. Run both control-plane validators if governance changes, applicable web tests only if adapters change, DB lint/advisors per repo, and official exact-SHA Integration/Governance gates. Known unchanged lint diagnostics (update_master_item v_row.unit_id; update_candidate_submission v_log) must be reported accurately, not suppressed or opportunistically fixed.

Provider-independent protocol tests do not certify real delivery, scanner behavior, UAT templates or production readiness. Record those boundaries explicitly.

Require independent `eiu-reviewer` exact implementation-SHA PASS/no source reopen before serialization; verify equivalence, exact official CI and accepted checkpoint under governance. Repair loop stays bounded to concrete findings. Current continuation ends at prompt/source PASS and does NOT dispatch that Executor.

## Prohibited actions and next frontier

No main push/merge, PR creation/merge, deployment, connected Supabase migration, production mail, force push, accepted checkpoint rewrite, source-policy weakening or second task materialization. Local disposable Supabase only for required verification. No broad service-role/browser bridge. No provider secrets in evidence.

Proposed later domains (not tasks or authorizations): provider sender runtime consuming this protocol; document/scan and temp-cleanup orchestration preserving CLEAN gates; manual email/history and Activity UI consuming trusted contracts. Reconcile dependencies when each later task is actually authorized; do not materialize them now.

STOP after this first task's independent prompt/source PASS. Return handoff to ChatGPT for audit and implementation-dispatch decision.
