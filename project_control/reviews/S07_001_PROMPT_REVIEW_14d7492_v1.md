# Coordinator transport of independent prompt review

Exact eiu-reviewer result below. Reviewer-native evidence persistence: UNAVAILABLE. This file is coordinator transport only, not reviewer-native persistence.

WORK_ID: S07-001-PROMPT-REVIEW-001
REVIEWED_SHA: 14d7492c34c7fd1dcbeb96f28ada9515c1448ec7
TARGET_PROMPT: project_control/prompts/SLICE-07_TASK-001_v1.md
VERDICT: PASS
SOURCE_REOPEN_REQUIRED: false

## Review basis and exact diff
The exact SHA diff was inspected first. It contains only the six expected planning/control-plane files: the new task prompt, the producer source reconciliation, and changes to AUTONOMY_RUN_STATE.yaml, CURRENT_STATE.md, SLICE_REGISTRY.yaml, and TASK_REGISTRY.yaml. There is no product implementation delta. The prompt and reconciliation are internally consistent with the control-plane authority split in AUTONOMY_PARALLEL_GOVERNANCE.md §§1–2: runtime state is in AUTONOMY_RUN_STATE.yaml, task/slice state in the registries, and CURRENT_STATE.md is derived.

The target state records TASK-S07-001 as PLANNED, prompt review pending, implementation_started=false, second_task_materialized=false, and the stop gate as WAITING_INDEPENDENT_PROMPT_REVIEW. SLICE_REGISTRY.yaml marks Slice-07 IN_PROGRESS for planning with only TASK-S07-001 as current task. TASK_REGISTRY.yaml gives only the accepted S06-001 and S06-002 dependencies. This is a legitimate first-task frontier, not unauthorized implementation or a second task.

## External audit hold, provenance, and source authority
The prompt correctly makes creation non-authorizing and requires a separate exact implementation-SHA review and later Owner/ChatGPT dispatch decision (prompt §Identity and execution gate). The external Slice-06 closure/audit is treated as hold-release provenance, not as an implementation or source-authority substitute. The accepted Slice-06 checkpoint and predecessor checkpoints are explicitly immutable, and SOURCE_REOPEN_EXPECTATION=false is appropriate because the prompt says to report contradictions rather than redefine S01–S06.

Current authority is correctly identified as source_registry.yaml CURRENT normative modules and accepted ordered migrations, while 15_ALL_IN_ONE_SPEC.md and database_schema.sql are not elevated over them (prompt §Canonical source authority; source_registry.yaml v1.18). The prompt references the relevant current sources rather than historical reviews.

## Dependencies, title, and bounded scope
The title accurately describes one cohesive persistence prerequisite: logical enqueue/bulk, Candidate transaction integration, worker state transitions, and Email History read/cleanup all share the outbox logical identity, parent binding, environment, audit, and retention boundary. The scope is broad but is not a mega-task on this evidence: provider calls/runtime/deployment, UI, document/scan/storage workers, archive/purge, automatic retention, templates/assets, and unrelated predecessor repair are expressly excluded (prompt §§Smallest coherent task boundary and Prohibited actions). The prompt also prohibits materializing a second Slice-07 task.

The split matches current source: 11_EMAIL_DOCUMENTS_AND_ACTIVITY_LOG.md §§1–4 and 145–157; 37_BACKEND_COMMAND_CONTRACTS.md §§11, 16, and lines 406–410; 43_EMAIL_DELIVERY_SPEC.md §§Delivery semantics, Enqueue, and Non-production environment safety.

## Transaction, logical identity, environment, parent, retention, and history
The contract preserves the required sequence business mutation → outbox insert → commit → worker delivery/state update → Email History → immutable audit, and keeps required Candidate Submit/Update notification enqueue in the same transaction (prompt §Logical enqueue and Candidate transactions; 11_EMAIL_DOCUMENTS_AND_ACTIVITY_LOG.md lines 21 and 153–157; 43_EMAIL_DELIVERY_SPEC.md lines 9–10). It explicitly forbids a provider call inside the transaction and does not claim atomicity with a later external provider.

Logical identity is adequately specified: normalized request replay is keyed by actor/scope/command/key, concurrent same-key requests serialize, mismatched payloads reject, and Candidate form-session idempotency is preserved (prompt §Idempotency and bulk; 48_IDEMPOTENCY_CONCURRENCY_SPEC.md lines 3–4 and 58). Parent identity is protected by derived recipients, exact entity/context checks, Submission/Application/Interview chain validation, and trusted outbox-sourced bindings. The source requires recipient derivation and exact parent context (37 lines 256–259 and 318–325; 39 lines 145–146).

Environment handling is correctly non-caller-controlled with TEST as the non-production default and trusted PRODUCTION configuration only (prompt §Logical enqueue and Candidate transactions; 43 lines 37–41). History is required to copy the outbox environment rather than trust worker replacements. This explicitly addresses the current migration asymmetry: outbox defaults TEST (`supabase/migrations/20260906005000_pre_s04_contract_repairs.sql:33–40`) while existing history defaults PRODUCTION (`supabase/migrations/20260906070000_interview_lifecycle_commands.sql:213–221`). The existing candidate writer's hardcoded TEST/recipient values (`20260906005000_pre_s04_contract_repairs.sql:1347–1389,1850–1892`) are a required implementation seam to forward-reconcile, not a prompt defect; the prompt expressly forbids caller-controlled environment, hardcoded real addresses, and independent notification calls.

Retention and cleanup are correctly preserved: production email trace remains exact-Submission business history and blocks normal hard-delete; `delete_unused_submission` remains MAINTENANCE_ONLY; operational history cleanup cannot rewrite outbox/provider attempts or erase Security Audit. TEST_RECORD is restricted to TEST and WRONG_RECORD requires a nonblank reason (prompt §History, cleanup, retention and audit; 42 lines 3–15; 66 lines 29–33; 73 lines 32–33; 37 lines 318–325 and 406–410). No automatic purge or invented retention policy is introduced.

## Document/scan boundaries
The prompt explicitly retains Candidate document/session/version, private-storage, current-target, expiry, and CLEAN/VALIDATED boundaries through crossed regressions, while excluding upload changes and scan workers (prompt §Out of scope and regression acceptance item 7; source reconciliation §§Candidate/document/scan boundaries). This matches 41_STORAGE_AND_UPLOAD_SECURITY.md and the accepted Candidate Submit/Update contracts. It does not incorrectly make scan completion asynchronous or treat a document worker as part of the email task.

## Activity versus Security Audit
The distinction is explicit and correct. Operational Email History is deletable only under the constrained command; immutable Security Audit survives deletion and records send/failure/delete events. Activity/Audit alone is not a business-usage reference. Audit payload minimization excludes PII rows, tokens, signed URLs, secrets, and document contents (prompt §History, cleanup, retention and audit; 11 lines 33–50 and 100–122; 47 lines 5–17 and 66–69). RLS source also keeps email outbox/audit server/worker restricted and requires history permission plus exact parent context (39 lines 79 and 144–146).

## Concurrency, idempotency, and lease protocol
The worker boundary is appropriately database-only and later-provider-consumable: bounded claim, QUEUED→SENDING→SENT/retryable-or-terminal FAILED, CANCELLED handling, due times, stale lease recovery, SKIP LOCKED/equivalent, fencing token, worker ownership, retry/backoff, and repeat-completion protection are all required (prompt §Durable worker database protocol; 11 lines 21–31; 43 lines 4–7 and 28–32). It correctly allows provider-accepted/crash duplicate external delivery while requiring one logical message and auditable distinct attempts, and never promises exactly-once delivery.

Bulk semantics are consistent with the source: maximum 100, deterministic lock ordering, stable per-item identities, partial success/error results, no hidden-parent leakage, and no browser loop in place of a command (prompt §Idempotency and bulk; 37 line 348–349; 63 lines 24–25). Required tests exercise meaningful races, lease expiry/reclaim, stale completion fencing, retry exhaustion, cancellation, and overlapping bulk targets rather than only serial happy paths.

## Trusted security boundaries
The prompt requires authenticated/authorized trusted entry points, derived actor and recipients, no browser-supplied role/actor/parent/environment/attachments, worker-only claim/result access, explicit RLS/grants/revokes, justified SECURITY DEFINER with empty search_path and qualified references, and no browser service-role bridge (prompt §§Logical enqueue, Durable worker database protocol, and Implementation discipline). These requirements conform to 02_ROLES_PERMISSIONS_AND_NAVIGATION.md lines 38–41, 39_SECURITY_RLS_MATRIX.md lines 79 and 145–146, and 59_RLS_POLICY_BLUEPRINT.md line 68. Unsupported email types fail closed. Authentication is not substituted for authorization.

## Regression and verification feasibility
The acceptance matrix is behavior-oriented and feasible with a disposable local database and simulated provider outcomes: same-key and fingerprint behavior, Candidate rollback/retention, forged inputs, staged stale-preview checks, worker races/fencing, history permission/classification, partial bulk, and crossed predecessor/document regressions are enumerated (prompt §Concurrency and regression acceptance). The verification discipline correctly requires forward migrations, repository-native conventions, focused SQL/RLS/concurrency testing, cumulative predecessor gates, exact implementation-SHA independent review, and official CI without claiming provider/scanner/UAT/production readiness (prompt §Implementation and verification discipline; 100_TECHNICAL_PRECODE_GATE_V1_18.md lines 12–34). No live provider, connected Supabase, deployment, remote mutation, or production credential is required or authorized.

The prompt's implementation checks must resolve the known current seams (TEST/default history asymmetry, hardcoded candidate writer values, and existing history policy's need for exact contextual authorization) against current source before implementation. Those are intentionally within this task's stated reconciliation work and do not create a planning contradiction.

## CI treatment and evidence persistence
Per the supplied task context, official Integration run 34725394415 and Governance run 34725394349 are SUCCESS at the target SHA. They are support-only provenance for this planning review, not independent prompt-review evidence, and no CI rerun was performed. The exact-SHA tracked control-plane evidence inspected here does not persist either run ID in EVIDENCE_INDEX.yaml or a reviewer-native S07 evidence path; therefore evidence persistence for those two runs is **UNAVAILABLE**. This is non-blocking for the requested read-only prompt/source review. No validation command, test, build, lint, formatter, service, ref, or external action was run or performed.

## Findings and verdict
No evidence-backed actionable planning defect or current-source contradiction was found. No blocker citations apply. The prompt is internally consistent, preserves accepted predecessor contracts and trust boundaries, materializes only the authorized first task, and stops at the requested independent prompt/source gate.

VERDICT: PASS
SOURCE_REOPEN_REQUIRED: false
