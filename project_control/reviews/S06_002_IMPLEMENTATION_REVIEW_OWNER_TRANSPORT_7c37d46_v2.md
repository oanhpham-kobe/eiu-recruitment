# TASK-S06-002 — Independent Implementation Review R2 Owner Transport

- WORK_ID: `S06-002-IMPLEMENTATION-REVIEW-001-R2`
- REVIEWER: `eiu-reviewer`
- REVIEWED_REPOSITORY: `oanhpham-kobe/eiu-recruitment`
- REVIEWED_BRANCH: `oanhpham-kobe/TASK-S06-002-user-rbac-identity`
- REVIEWED_SHA: `7c37d46fa504b5d98b156735d7355f1d938be0bf`
- VERDICT: `BLOCKING_REPAIR`
- SOURCE_REOPEN_REQUIRED: `false`
- REVIEWER_EVIDENCE_PERSISTENCE: `UNAVAILABLE`
- COORDINATOR_PROVENANCE: `VERIFIED_FROM_OWNER_TRANSPORT`

This file records the independent verdict returned through the Owner transport. It is not evidence that the reviewer wrote to GitHub.

## Blocking findings

1. **Unit-history lock graph** — lifecycle/RBAC commands hold target User row + Internal User advisory before final `app_users` update; accepted durable-reference history then key-shares unchanged `unit_id`, while `bulk_create_or_update_applications()` locks Unit before HR owner User. This leaves deterministic Unit→User / User→Unit deadlock potential. Repair the complete Unit/User/Application graph while preserving S06-001 durable history and active-master validation, with staged bulk-assignment vs lifecycle and HR-role-removal regressions using a non-null Unit.
2. **Interview operationalization ordering** — resource-blocking Interview trigger takes Internal User advisory locks before participant/actor FK User-row locks. An HR who is also a current participant can race Root lifecycle administration into advisory↔FK-row deadlock during schedule/uncancel. Repair to shared row→advisory→revalidate order and test the public-command race.
3. **Dormant new-selection race** — dormant/CANCELLED/unscheduled/elapsed historical remove/reorder maintenance is correctly allowed, but new add/re-add/restoration can read Active before deactivation commits and then insert/restore after deactivation because the post-statement resource-blocking check is skipped. Distinguish unchanged history maintenance from new selection/restoration; serialize and post-lock revalidate new selections regardless of schedule status. Add deactivation-first CANCELLED and unscheduled add/re-add races.
4. **First-bind Auth freshness** — first Google bind verifies trusted Auth evidence before normalized-email/User/advisory locking but does not repeat `private.verified_google_auth_email(auth.uid())` after the full lock set. Re-run trusted evidence post-lock, require equality with the advisory-key email, fail closed on change, and test staged Auth evidence mutation while waiting.

## Non-blocking observations

- Candidate-contained R2 gate, R1 gate, and Owner-transported R1 evidence are present; R1 artifact blocker is closed.
- Raw `app_users.auth_user_id` consumer regression is statically closed; authenticated remains denied direct column access and inspected Internal User consumers use trusted session/binding RPCs.
- Original first-bind/rebind normalized-email resource-order inversion is repaired; only first-bind Auth evidence freshness remains.
- No canonical business/security/product contradiction was identified.

## Reviewer verification statement

The reviewer checked detached HEAD equality to `7c37d46fa504b5d98b156735d7355f1d938be0bf`, inspected effective R2 source and targeted tests, and reported `git diff --check` success. Local runtime SQL was not executed because Docker Desktop Linux engine was unavailable. Producer CI evidence was treated as context only, not acceptance.

## Acceptance statement

`7c37d46fa504b5d98b156735d7355f1d938be0bf` must not proceed to governed product integration. Repair the four findings, retain narrow binding ACL and allowed dormant-history maintenance, rerun exact-SHA verification, and submit a new immutable candidate for independent review. Canonical source reopening is not required.
