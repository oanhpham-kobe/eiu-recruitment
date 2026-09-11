# TASK-S06-002 Independent Implementation Review Gate

## Identity

- WORK_ID: `S06-002-IMPLEMENTATION-REVIEW-001`
- REVIEWER: `eiu-reviewer`
- REPOSITORY: `oanhpham-kobe/eiu-recruitment`
- TASK_BRANCH: `oanhpham-kobe/TASK-S06-002-user-rbac-identity`
- ORIGINAL_TASK_BASELINE: `0a2ccdfedc477f9766c9aaa03739d16a7ed83c01`
- EXACT_REVIEWED_SHA: `a7aa037e26cda6ba70153539c1dfc15c3fba37e6`
- REVIEW_DIFF: `0a2ccdfedc477f9766c9aaa03739d16a7ed83c01...a7aa037e26cda6ba70153539c1dfc15c3fba37e6`
- CANONICAL_PROMPT: `project_control/prompts/SLICE-06_TASK-002_v1.md`
- PROMPT_REVIEW_SHA: `f757e76f3f97077c608dab29bad45b8bd2126dc3`
- SOURCE_REOPEN_EXPECTATION: `false` unless the reviewer proves a concrete canonical contradiction.

Review the immutable SHA above. Do not substitute a later mutable branch HEAD. Producer verification is evidence, not independent acceptance.

## Frozen candidate scope

The net task diff from the pre-task baseline contains 18 files and no README/noop net artifact. Production/control-relevant implementation paths are:

1. `.github/workflows/integration-ci.yml`
2. `supabase/migrations/20260911104500_internal_user_serialization_contracts.sql`
3. `supabase/migrations/20260911104530_internal_user_read_contracts.sql`
4. `supabase/migrations/20260911104600_internal_user_directory_commands.sql`
5. `supabase/migrations/20260911104630_internal_user_rbac_commands.sql`
6. `supabase/migrations/20260911104700_internal_user_identity_commands.sql`
7. `web/src/lib/auth/internal.ts`
8. `web/src/lib/auth/session.ts`
9. `web/src/__tests__/internal-provisioning.test.ts`
10. `web/src/__tests__/internal-session-rpc.test.ts`
11. `supabase/tests/internal_user_rbac_identity_test.part1.sql`
12. `supabase/tests/internal_user_rbac_identity_test.part2.sql`
13. `supabase/tests/internal_user_rbac_identity_test.sh`
14. `supabase/tests/internal_user_lifecycle_concurrency_test.sh`
15. `supabase/tests/interview_lifecycle_test.sql`
16. `supabase/tests/copy_interview_schedule_test.sql`
17. `supabase/tests/master_data_lifecycle_history_test.sql`
18. `supabase/tests/master_data_durable_reference_history_test.sql`

No Users/Permissions UI, `main` mutation, PR merge, Vercel deployment, or connected Supabase migration application is part of this candidate.

## Test-only repair provenance after web verification

Exact product/web tree `014e22f737463b049eacca041a0c204ce0699cd1` received full web acceptance. Six later paths differ from that SHA and are test-only repairs:

- `supabase/tests/copy_interview_schedule_test.sql`
- `supabase/tests/internal_user_lifecycle_concurrency_test.sh`
- `supabase/tests/internal_user_rbac_identity_test.sh`
- `supabase/tests/interview_lifecycle_test.sql`
- `supabase/tests/master_data_durable_reference_history_test.sql`
- `supabase/tests/master_data_lifecycle_history_test.sql`

The final static gate proves `web/` at `a7aa037e26cda6ba70153539c1dfc15c3fba37e6` is byte-equivalent to `014e22f737463b049eacca041a0c204ce0699cd1`. The fixture repairs align retained tests with already-canonical owner eligibility (`Active + HR role`) and accepted `reports.delete + reports.view` authorization; they did not relax production guards. Independently verify that characterization rather than trusting it.

## Canonical contract areas to review

### Trusted first Google bind and identity lifecycle

Verify first bind requires trusted Auth evidence for Google provider plus confirmed/verified email, normalized EIU email, an Active allowlisted Internal User locked for binding, and no competing Auth binding. Security decisions must not trust user-editable metadata. Binding must be atomic with audit, exact replay only, and no auto-rebind. Bound non-Root identity change must remain Root-only; Root identity remains break-glass rather than an ordinary recovery path.

### Internal User directory commands

Verify `create_internal_user`, `update_internal_user_directory`, `set_internal_user_active`, and identity-change commands enforce authoritative actor resolution, protected-field ownership, optimistic version checks where canonical, normalized email/domain rules, and stable/non-leaking errors. Preserve accepted S06-001 Unit lifecycle/history locking and durable-reference behavior.

### HR RBAC commands

Verify `assign_hr_role_with_defaults`, `remove_hr_role`, `grant_hr_permission`, and `revoke_hr_permission` use canonical Full HR authority rather than treating historical seed inventory as authority. Check dependency guards, exact role/permission semantics, atomic audit, and Root behavior.

### Permission-read minimization

Verify the historical cross-user granular permission exposure is closed. Root may inspect all effective granular permissions; non-root directory managers receive only minimum-safe directory/lifecycle information; a user may still obtain their own permission details required for session behavior. Inspect all migrated session/selector consumers to ensure no broad fallback remains.

### Lifecycle concurrency and lock graph

Independently inventory every writer that can operationalize an owner or participant, including assignment, reactivation, scheduling, uncancel, copy, add/re-add and bulk paths. Verify deterministic serialization with:

- user deactivation versus Active Application owner assignment/reactivation;
- user deactivation versus current participant on a non-elapsed `resource_blocking` Interview;
- HR-role removal versus owner assignment and permission mutation;
- Unit-history trigger locks and accepted S06-001 durable-reference locks.

Fully elapsed participation must not block deactivation, and Current Round must not be substituted for the canonical `resource_blocking` predicate. Check for deadlock cycles and fail-closed reassignment-required outcomes.

### Database security

Verify all exposed-table RLS/ACL boundaries, `SECURITY DEFINER` functions with `SET search_path = ''` and schema-qualified objects, narrow function execute grants, no `service_role` leakage, no authorization from editable `user_metadata`, and atomic audit/security logs.

## Producer verification already executed

Final exact candidate verifier run `34611668782`: PASS. It checked exact SHA `a7aa037e26cda6ba70153539c1dfc15c3fba37e6` and executed:

- patch hygiene and six-path test-only delta check;
- final `web/` tree equivalence to `014e22f737463b049eacca041a0c204ce0699cd1`;
- local Supabase start;
- `supabase db reset` from zero;
- focused S06-002 Internal User/RBAC/Identity regressions;
- real two-session owner/participant lifecycle concurrency regressions;
- crossed Application reactivation/participant contract regression;
- Interview lifecycle, round/conflict and copy regressions;
- bulk Application assignment replay regression;
- retained S06-001 canonical seed/guard, lifecycle/history and durable-reference-history regressions;
- `supabase db lint --local --level error`;
- clean local Supabase stop.

Exact web acceptance evidence: workflow run `34602347683`, job `103272463530` PASS on exact SHA `014e22f737463b049eacca041a0c204ce0699cd1`. That web job passed dependency install/audit, design contract, lint, typecheck, build, Chromium install and full web acceptance suite. The overall `34602347683` was not green because an earlier database test fixture failed; do not misstate the overall run. Final run `34611668782` subsequently closed the database/test-fixture boundary and proved web-tree equivalence.

## Independent verification requested

When supported, rerun at minimum:

```bash
git diff --check 0a2ccdfedc477f9766c9aaa03739d16a7ed83c01...a7aa037e26cda6ba70153539c1dfc15c3fba37e6
supabase start
supabase db reset
bash supabase/tests/internal_user_rbac_identity_test.sh
bash supabase/tests/internal_user_lifecycle_concurrency_test.sh
docker exec -i supabase_db_eiu-recruitment-dev psql -v ON_ERROR_STOP=1 -U postgres -d postgres < supabase/tests/application_reactivation_and_participant_contract_repair_test.sql
docker exec -i supabase_db_eiu-recruitment-dev psql -v ON_ERROR_STOP=1 -U postgres -d postgres < supabase/tests/interview_lifecycle_test.sql
docker exec -i supabase_db_eiu-recruitment-dev psql -v ON_ERROR_STOP=1 -U postgres -d postgres < supabase/tests/interview_round_and_conflict_locking_test.sql
docker exec -i supabase_db_eiu-recruitment-dev psql -v ON_ERROR_STOP=1 -U postgres -d postgres < supabase/tests/copy_interview_schedule_test.sql
docker exec -i supabase_db_eiu-recruitment-dev psql -v ON_ERROR_STOP=1 -U postgres -d postgres < supabase/tests/bulk_commands_replay.sql
docker exec -i supabase_db_eiu-recruitment-dev psql -v ON_ERROR_STOP=1 -U postgres -d postgres < supabase/tests/master_data_seed_guard_test.sql
docker exec -i supabase_db_eiu-recruitment-dev psql -v ON_ERROR_STOP=1 -U postgres -d postgres < supabase/tests/master_data_lifecycle_history_test.sql
docker exec -i supabase_db_eiu-recruitment-dev psql -v ON_ERROR_STOP=1 -U postgres -d postgres < supabase/tests/master_data_durable_reference_history_test.sql
supabase db lint --local --level error
supabase stop
```

Also inspect the exact web/session changes and Integration CI diff. If full web rerun is unavailable, verify the final candidate's `web/` tree identity against `014e22f737463b049eacca041a0c204ce0699cd1` and review the prior exact web evidence.

## Review-only boundaries

Do not modify implementation, refs, integration state, `main`, Vercel, or connected Supabase. Do not select the next task.

## Required reviewer output

Return:

- `WORK_ID: S06-002-IMPLEMENTATION-REVIEW-001`
- `REVIEWED_REPOSITORY: oanhpham-kobe/eiu-recruitment`
- `REVIEWED_BRANCH: oanhpham-kobe/TASK-S06-002-user-rbac-identity`
- `REVIEWED_SHA: a7aa037e26cda6ba70153539c1dfc15c3fba37e6`
- `VERDICT: PASS | BLOCKING_REPAIR | OWNER_DECISION_REQUIRED`
- `SOURCE_REOPEN_REQUIRED: true | false`
- `BLOCKING_FINDINGS`
- `NON_BLOCKING_OBSERVATIONS`
- `VERIFICATION_EXECUTED`
- `IDENTITY_BIND_ASSESSMENT`
- `RBAC_VISIBILITY_ASSESSMENT`
- `LIFECYCLE_CONCURRENCY_ASSESSMENT`
- `SECURITY_ASSESSMENT`
- `ACCEPTED_CONTRACT_REUSE_ASSESSMENT`
- `ACCEPTANCE_STATEMENT`

For PASS explicitly state that exact SHA `a7aa037e26cda6ba70153539c1dfc15c3fba37e6` may proceed to governed integration without canonical source reopen.

## Durable evidence

Suggested evidence branch: `review/S06-002-IMPL-a7aa037-v1`

Suggested path: `project_control/reviews/S06_002_IMPLEMENTATION_REVIEW_a7aa037_v1.md`

If persistence is available, return actual branch, full 40-character evidence commit, and path. If not, state `EVIDENCE_PERSISTENCE: UNAVAILABLE`. Never invent coordinates.
