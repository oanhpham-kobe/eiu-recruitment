# TASK-S06-001 — Independent Prompt Re-Review Gate (R2)

## Review identity

- WORK_ID: `S06-001-PROMPT-REVIEW-002`
- REVIEW_TYPE: `BOUNDED_PRE_IMPLEMENTATION_PROMPT_REREVIEW`
- REVIEWER: `eiu-reviewer`
- REPOSITORY: `oanhpham-kobe/eiu-recruitment`
- INTEGRATION_BRANCH: `autonomy/continuous-integration-20260905-01`
- EXACT_REVIEWED_SHA: `68d96b39e309ee6f1edbe6cf4031c10a583b0269`
- TARGET_PROMPT: `project_control/prompts/SLICE-06_TASK-001_v2.md`
- REPAIR_RESPONSE: `project_control/reviews/S06_001_PROMPT_REPAIR_RESPONSE_v2.md`
- PRIOR_REVIEW: `S06-001-PROMPT-REVIEW-001 @ 5abbb5181405e0f5a468176edd93db8226a3efd5`
- PRIOR_VERDICT: `BLOCKING_REPAIR`
- SOURCE_REOPEN_REQUIRED_FROM_R1: `false`

Review the immutable SHA above. Do not substitute a later mutable integration HEAD.

## Materialization evidence

The repaired prompt was materialized at exact SHA `68d96b39e309ee6f1edbe6cf4031c10a583b0269`.

Exact-SHA CI:

- Integration CI `34491648323` — PASS
- Governance CI `34491648300` — PASS

The diff from prior control HEAD `ccac13265d44731933fcb98e3c1791d2f609cb23` contains only:

- `project_control/AUTONOMY_RUN_STATE.yaml`
- `project_control/CURRENT_STATE.md`
- `project_control/EVIDENCE_INDEX.yaml`
- `project_control/TASK_REGISTRY.yaml`
- `project_control/prompts/SLICE-06_TASK-001_v2.md`
- `project_control/reviews/S06_001_PROMPT_REPAIR_RESPONSE_v2.md`

No product code, migration, workflow, `main`, Vercel deployment, or connected Supabase state changed.

## R1 blockers to verify as repaired

### S06-PROMPT-01 — Idempotency contract

R1 required explicit retry/replay behavior for `create_master_item`, `update_master_item`, and `delete_or_inactivate_master_item`.

Verify prompt v2 now requires all of the following:

1. explicit idempotency key or exact accepted repository equivalent for retryable mutation entry points;
2. deterministic scope isolation across authenticated actor, command, `master_type`, and update/delete target identity;
3. authentication, Active Internal User state, and `master_data.manage` authorization revalidated before serving any replay result;
4. normalized request fingerprint covering every command-meaning field, including target identity and `expected_version_no` for update/delete;
5. same key/scope/fingerprint after committed success returns the stored typed result with no second mutation, version bump, or audit;
6. same key/scope with different fingerprint fails closed and executes neither old nor new mutation;
7. concurrent duplicates serialize to one logical mutation/audit/result;
8. failed/rolled-back attempts do not create reusable successful replay state;
9. idempotency result, business mutation, version effect, and audit commit atomically;
10. implementation prefers an accepted repository idempotency primitive rather than creating an incompatible duplicate store;
11. SQL regressions cover sequential replay, concurrent replay, fingerprint mismatch, actor isolation, master-type/target isolation, unauthorized replay, and failed-attempt reuse.

Block only if the prompt still leaves a concrete replay ambiguity capable of causing duplicate mutation/version/audit or replay authorization leakage.

### S06-PROMPT-02 — Delete/inactivate expected version

Verify prompt v2 now requires:

- `expected_version_no` or exact canonical equivalent on `delete_or_inactivate_master_item`;
- target row lock first;
- current version comparison while the target lock is held and before the usage/lifecycle decision;
- stale request → `STALE_VERSION`;
- stale request leaves both master state and audit unchanged;
- only after version validation may the command choose hard delete versus inactivation;
- regressions for stale unreferenced hard-delete and stale referenced inactivation.

## Non-blocking R1 clarification to verify

R1 clarified that `no anon business-table access for this feature` must not revoke existing accepted anonymous lookup reads required by Candidate flows.

Verify v2 now says:

- no new anonymous Master Data **management** surface;
- no anonymous mutation/admin capability;
- preserve already-accepted anonymous active lookup reads required by existing Candidate workflows;
- do not widen those lookup grants.

## Regression check — unchanged valid R1 findings

R1 already found the following source-backed and safe. Confirm v2 repair did not regress them:

- exactly 11 Phase-1 business masters in scope;
- Permission catalog and Users excluded from generic Master Data;
- User/Identity/RBAC remains a later Slice-06 task;
- `users.directory_read` reconciliation remains deferred and is not a Master Data blocker;
- usage checks include direct and indirect references, including `app_users.unit_id` where relevant;
- unused→hard-delete and referenced→Inactive semantics;
- referenced structural meaning immutable; replacement = create-new + Inactive-old;
- label-only typo/translation correction may be allowed with optimistic version + audit;
- inactive prevents new selection but historical references remain readable/operable;
- `requires_demo_topic` remains advisory and does not become a blocking invariant;
- closed master-type allowlist and per-type field allowlists;
- no arbitrary-table/column admin API;
- no browser direct DML/service-role exposure;
- explicit ACLs and empty `SECURITY DEFINER search_path`;
- Root does not bypass structural/history integrity;
- accepted Candidate/Application/Interview/Report behavior remains append-only compatible.

## Source reopen / Owner decision

Do not reopen canonical source unless a genuine contradiction is found.

R1 found no Owner decision requirement and returned `SOURCE_REOPEN_REQUIRED=false`.

A remaining defect in prompt v2 should normally be `BLOCKING_REPAIR / SOURCE_REOPEN_REQUIRED=false`, not source reopen.

## Required reviewer behavior

This remains prompt review only.

Do not:

- implement TASK-S06-001;
- edit the prompt;
- create the implementation branch/checkpoint;
- mutate integration;
- start later Slice-06 tasks;
- push/merge `main`;
- deploy Vercel;
- apply connected Supabase migrations.

## Required response format

Return:

`WORK_ID: S06-001-PROMPT-REVIEW-002`

`REVIEWED_REPOSITORY: oanhpham-kobe/eiu-recruitment`

`REVIEWED_BRANCH: autonomy/continuous-integration-20260905-01`

`REVIEWED_SHA: 68d96b39e309ee6f1edbe6cf4031c10a583b0269`

`TARGET_PROMPT: project_control/prompts/SLICE-06_TASK-001_v2.md`

`VERDICT: PASS | BLOCKING_REPAIR | OWNER_DECISION_REQUIRED`

`SOURCE_REOPEN_REQUIRED: true | false`

Then include:

- BLOCKING_FINDINGS
- R1_BLOCKER_REPAIR_ASSESSMENT
- SOURCE_RECONCILIATION_ASSESSMENT
- TASK_SPLIT_AND_DEPENDENCY_ASSESSMENT
- MASTER_LIFECYCLE_HISTORY_ASSESSMENT
- IDEMPOTENCY_ASSESSMENT
- CONCURRENCY_VERSION_ASSESSMENT
- SECURITY_RLS_ACL_ASSESSMENT
- TESTABILITY_ASSESSMENT
- ACCEPTED_TREE_COMPATIBILITY_ASSESSMENT
- VERIFICATION_EXECUTED
- ACCEPTANCE_STATEMENT

For PASS, explicitly state that prompt v2 at exact reviewed SHA may be materialized for implementation without reopening canonical source.

## Durable evidence

Persist the complete review if possible.

Suggested branch:

`review/S06-001-PROMPT-68d96b3-v2`

Suggested path:

`project_control/reviews/S06_001_PROMPT_REVIEW_68d96b3_v2.md`

Return actual:

- EVIDENCE_BRANCH
- EVIDENCE_COMMIT — full 40-character SHA
- EVIDENCE_PATH

If persistence is unavailable, state `EVIDENCE_PERSISTENCE: UNAVAILABLE`. Never invent coordinates.