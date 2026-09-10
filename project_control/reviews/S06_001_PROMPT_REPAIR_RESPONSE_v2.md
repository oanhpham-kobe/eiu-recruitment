# TASK-S06-001 Prompt Repair Response — v2

## Review identity

- PRIOR_WORK_ID: `S06-001-PROMPT-REVIEW-001`
- PRIOR_REVIEWED_SHA: `5abbb5181405e0f5a468176edd93db8226a3efd5`
- PRIOR_TARGET: `project_control/prompts/SLICE-06_TASK-001_v1.md`
- PRIOR_VERDICT: `BLOCKING_REPAIR`
- SOURCE_REOPEN_REQUIRED: `false`
- REVIEWER: `eiu-reviewer`

## Durable evidence verification

Reviewer reported:

- branch: `review/S06-001-PROMPT-5abbb51-v1`
- commit: `a93659867e75f95109fa4826cb8b68114b031ddc`
- path: `project_control/reviews/S06_001_PROMPT_REVIEW_5abbb51_v1.md`

At Coordinator verification time, the commit, branch and path were not resolvable through the connected GitHub repository. The review verdict is therefore recorded as Owner-transported evidence; no durable-evidence verification claim is made.

## Blocking findings accepted

### S06-PROMPT-01 — Missing idempotency contract

Accepted as blocking. Prompt v1 named the three trusted commands and required authorization, locking, optimistic versioning and audit, but did not make retry/replay semantics executable.

Prompt v2 must require, for each mutation where retry is applicable:

- explicit idempotency key input and deterministic scope;
- scope isolation by authenticated actor plus master type and logical command target/operation as applicable;
- authorization and current actor eligibility revalidated before serving any replay result;
- canonical request fingerprint over the normalized validated command payload (excluding transport-only noise but including fields that change command meaning, expected version and target identity where applicable);
- same key + same scope + same fingerprint returns the atomically stored prior success result without repeating master mutation, version bump or audit;
- same key in the same scope + different fingerprint rejects with a stable idempotency mismatch error and performs no mutation;
- different actor or different master type cannot replay another scope's result;
- concurrent duplicate submissions serialize to one logical mutation/result;
- failed/non-committed attempts do not create a reusable successful replay record;
- idempotency result persistence is committed atomically with the business mutation and audit.

Required regressions: sequential replay, concurrent replay, fingerprint mismatch, actor isolation and master-type isolation.

### S06-PROMPT-02 — Delete/inactivate missing expected-version validation

Accepted as blocking. Prompt v1 required optimistic concurrency for update but did not explicitly require it for the delete/inactivate command.

Prompt v2 must require `expected_version_no` (or exact canonical equivalent) for `delete_or_inactivate_master_item`. While holding the target row lock, the command must compare the expected version before deciding hard-delete versus inactivation. A stale request must return `STALE_VERSION` and leave both master state and audit unchanged.

Required regressions: stale hard-delete target and stale inactivation target.

## Non-blocking clarification incorporated

The v1 wording `anon receives no business-table access for this feature` can be misread as revoking already-accepted anonymous active lookup reads used by Candidate workflows. Prompt v2 will state instead that S06-001 creates no new anonymous **management** surface and must preserve any accepted anonymous lookup reads required by existing Candidate flows.

## Scope held constant

No source reopen. No new Owner decision. No expansion into Users/Identity/RBAC or UI. The 11-master allowlist, historical semantics, structural examples, accepted active-master guards and append-only implementation rule remain unchanged.

## Producer repair verdict

`READY_FOR_EXACT_SHA_INDEPENDENT_PROMPT_REREVIEW` once prompt v2 is materialized on integration and its exact target SHA is frozen.