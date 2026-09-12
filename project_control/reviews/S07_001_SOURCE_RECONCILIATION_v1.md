# Slice-07 first-task source reconciliation

Planning baseline: `26c186bae8eec12bf8b8d2571238709a6e597c24`. Producer reconciliation, not independent review or new product authority.

## Frontier and authority

Live integration and all Slice-06 checkpoint refs matched Owner coordinates. Runtime has zero active workers, both S06 tasks DONE, Slice-06 DONE, Slice-07 NOT_STARTED and no TASK-S07 entry. OPEN_GAPS contains deferred scanner/ops/UAT/assets/retention work, no blocker to an email persistence planning gate. External ChatGPT audit PASS was provided by Owner, releasing only EXTERNAL_CHATGPT_CLOSURE_AUDIT. No accepted source reopened. Current governance authority is AUTONOMY_PARALLEL_GOVERNANCE §§3/9, runtime and DAG registries, not old source plans or historical review notes.

Current source registry v1.18 marks modules 11/37/39/41/42/43/47/48/55/59/63/66/68/73/99/100 normative/current. Generated 15_ALL_IN_ONE_SPEC is a current-only compilation; app_spec is structured contract. Historical/superseded modules are excluded. Accepted ordered migrations—not database_schema starter—define implementation reality.

## Transaction and workers

37 §16, 11 §§2/4, 43 and 47: permissions, recalculation, mandatory immutable audit and business invariants commit in business transaction. Email enqueue commits there; provider call never does. Delivery, scans, orphan/temp cleanup and noncritical telemetry execute after commit. Security scan result is mandatory for document finalization; asynchronous orchestration cannot bypass synchronous CLEAN/VALIDATED and expiry/current-version gates.

## Email and retained trace

11/43/37 §§11, explicit bulk/delete/history and notification sections: one logical message per idempotency scope, recipient derivation, exact entity binding, trusted environment TEST default, no attachments. PRODUCTION Submit/Update trace is retained business usage bound to exact Submission; failures/retries do not expose normal HR hard-delete. 42/66 prohibit automatic business purge and reserve approved archive/purge for separate scope. History view/delete is separate permission plus parent context; TEST_RECORD only TEST, WRONG_RECORD requires reason and immutable audit; outbox/provider records cannot be silently rewritten.

Current outbox DDL and effective Submit/Update enqueue: `20260906005000_pre_s04_contract_repairs.sql` (outbox lines 31–77, effective Candidate writers). Earlier PRODUCTION literals are superseded. History schema/RLS: `20260906070000_interview_lifecycle_commands.sql:213–254`; current history default PRODUCTION differs from safe outbox TEST default and must not classify worker output independently. No enqueue/bulk/delete-history or provider runtime found. Existing lease columns do not by themselves implement claim/recovery/fencing. This makes email trusted persistence a coherent first task, before provider/UI consumers.

## Candidate/document/scan boundaries

Authority: 37 §§Candidate Form Session, Documents/Storage; 41; app_spec upload; 11; 42. Existing `20260905060000_candidate_form_and_submission_schema.sql` has logical-document headers/current immutable versions, reservation and cleanup identities. `20260905080000_storage_reservation_and_upload_protocol.sql` has reserve/sign/record/scan/stage/plan/cancel and cleanup claim/complete RPCs. `20260905090000_candidate_submission_commands.sql` plus later effective repairs materializes staged plans atomically.

Retain NEW form ADD-only, EDIT staged ADD/REPLACE/DELETE, exact logical/current target revalidation at stage AND Save, matching session/reservation/type, max 5 effective files, required current CV, private object identity and synchronous unexpired OPEN + VALIDATED/CLEAN checks. Cancel does not alter persisted versions. Never equate current references with historical versions or erase snapshots.

Current candidate scanner (`web/src/lib/storage/upload-scanner.ts`, candidate-actions completeAndStageUploadAction) runs on request path with trusted service-role validation after caller authorization. No durable scan-request queue/runtime found. Existing scan RPC locks reservation, but explicit attempt/object-generation/expiry fencing is incomplete; subsequent plan checks still gate commit. Later scan orchestration must bind request/result to exact reservation/object bytes/checksum/version, reject stale or expired/replaced results, preserve unsafe/CLEAN authority and quarantine, retry without letting worker lag grant eligibility. This is later bounded work, not a reason to weaken accepted finalization or redesign auth now.

Interview reserve/finalize (`20260906070000...:779–883`) retains CLEAN/metadata/current-version checks; signing/scanner web integration is incomplete. Later document task owns that integration. Existing cleanup queue captures canceled/rejected/replaced/deleted object paths and defers deletion until reservation/signed URL safety bounds; cleanup RPCs lease/retry but no durable runner/sweeper found. Later housekeeping must durably capture expired temp/orphan identities, protect current/historical retained versions, fence stale claims/results and respect signed-upload windows. It must not become business-record purge. No generic queue abstraction is required by source.

## Activity and Security Audit

11 §§3/8/9, 47 and 73 distinguish operational activity/history from immutable privileged audit. Mandatory audit failure rolls back business mutation. User-facing history deletion preserves security audit. Activity/Audit alone does not count as business usage; retained production email does. Reuse existing activity/security tables and private helpers from `20260905120000...`, not a duplicate audit system. Payload minimization and trusted access remain mandatory.

## Worker design boundary

43 requires leased claim, locked_at/until, worker_id, attempt_no, next_attempt_at, provider IDs/errors, stale SENDING recovery, bounded retries. First task implements email-specific DB protocol with attempt fencing and history/audit atomicity; later provider runtime consumes it. Provider-accepted/crash can duplicate delivery, never duplicate logical enqueue. Protocol tests simulate provider outcomes without real email or production credentials. Scan/storage workers have distinct security/identity contracts and are not bundled into first task.

## Dependencies and decomposition

Accepted S01 auth/session; S02 Submit/document/privacy; S03 Application; S04 Interview/Copy; S05 report/context; S06 Master Data/User/RBAC are inputs, not replacement targets. Direct first-task DAG dependencies S06-001 and S06-002 represent the accepted transitive chain. Read existing exact parent/context predicates and latest trusted writers before modifying any narrow enqueue seam.

Materialize ONLY TASK-S07-001: Email Outbox and History Trusted Persistence Contracts. Scope: trusted enqueue/bulk, Candidate transaction compatibility, worker DB state protocol, contextual history/cleanup. No provider runtime, UI, scanner/document worker or archive/purge implementation. Later domains are proposed, unnumbered and unmaterialized: provider sender; document/scan/temp-cleanup orchestration; manual email/history/Activity experiences. They are not active frontier authorizations.

## Known debt and gates

Unchanged lint diagnostics v_row.unit_id and unassigned v_log remain unrelated debt. Checkpoint immutability is process-enforced; do not change branch protection. Real scanner/provider operational thresholds, production templates, UAT/PDF assets remain at their canonical later gates. No fake evidence or provider success.

Validate both native/control-plane validators, exact official governance CI and established impacted Integration policy, independent exact-SHA prompt/source review. Any prompt findings repaired/reviewed before implementation. STOP at prompt PASS for external audit/dispatch decision.
