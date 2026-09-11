# TASK-S06-002 Implementation Review R1 — Owner-Transported Evidence

## Provenance

- WORK_ID: `S06-002-IMPLEMENTATION-REVIEW-001`
- REVIEWER: `eiu-reviewer`
- REVIEWED_REPOSITORY: `oanhpham-kobe/eiu-recruitment`
- REVIEWED_BRANCH: `oanhpham-kobe/TASK-S06-002-user-rbac-identity`
- REVIEWED_SHA: `a7aa037e26cda6ba70153539c1dfc15c3fba37e6`
- VERDICT: `BLOCKING_REPAIR`
- SOURCE_REOPEN_REQUIRED: `false`
- REVIEWER_EVIDENCE_PERSISTENCE: `UNAVAILABLE`
- COORDINATOR_PROVENANCE: `VERIFIED_FROM_OWNER_TRANSPORT`

This artifact records the review text transported by the Owner. It is not evidence that the reviewer itself wrote to GitHub.

## Blocking findings

1. The required review gate artifact was absent from the reviewed candidate/task branch. The R2 candidate must carry its review-gate artifact in the reviewed tree so the reviewer does not depend on a control-only integration commit outside the reviewed SHA.
2. `20260911104530_internal_user_read_contracts.sql` revoked authenticated SELECT on `app_users.auth_user_id` while retained request-scoped server consumers still filtered by that column. Migrate every affected consumer to the narrow session RPC/projection before retaining the column ACL.
3. `private.recheck_current_participants_after_statement()` rejected any current inactive participant touched by transition-table reorder updates, breaking permitted dormant/CANCELLED historical maintenance. Scope enforcement to transitions that can make an Interview resource-blocking/current participation operational.
4. `set_internal_user_active()` acquired the target `app_users` row before the shared advisory lock while Application owner guards acquired advisory then later FK `KEY SHARE`, creating a lifecycle/owner-writer deadlock cycle. Establish one deterministic order across all owner writers and revalidate after locking.
5. First Google bind acquired normalized-email advisory before target row while Root identity change acquired target row before replacement-email advisory, creating an identity bind/rebind deadlock cycle. Apply one deterministic identity lock order to both paths.

## Reviewer assessments

- Identity proof, Active allowlisting, exact replay, Root-only non-Root rebind, SECURITY DEFINER/search_path discipline, version/idempotency/audit structure were directionally correct.
- Permission visibility narrowing was directionally correct but incomplete because affected trusted server consumers were not migrated.
- Shared owner/participant serialization covered important races but had the trigger-scope and lock-order defects above.
- No canonical source contradiction was found. Repairs are technically defined and canonical source reopening is not required.

## Acceptance statement

Exact SHA `a7aa037e26cda6ba70153539c1dfc15c3fba37e6` cannot proceed to governed integration. Repair all five blockers, run gate-required verification on a new immutable SHA, and submit that SHA for independent re-review.
