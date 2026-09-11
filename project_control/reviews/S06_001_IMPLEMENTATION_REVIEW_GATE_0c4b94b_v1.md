# TASK-S06-001 Independent Implementation Review Gate

## Identity

- WORK_ID: `S06-001-IMPLEMENTATION-REVIEW-001`
- REVIEWER: `eiu-reviewer`
- REPO: `oanhpham-kobe/eiu-recruitment`
- TARGET_BRANCH: `oanhpham-kobe/TASK-S06-001-master-data-lifecycle`
- BASELINE_SHA: `0ec409915bdd00b61b1b7affdb77ec778c7c1dc7`
- REVIEWED_SHA: `0c4b94b29e08e1ad877583bdb90d522e5577dccc`
- REVIEW_DIFF: `0ec409915bdd00b61b1b7affdb77ec778c7c1dc7...0c4b94b29e08e1ad877583bdb90d522e5577dccc`
- SOURCE_REOPEN_EXPECTATION: `false` unless a concrete canonical contradiction is proven.

## Frozen implementation scope

Exactly six files differ from the accepted integration baseline:

1. `.github/workflows/integration-ci.yml`
2. `supabase/migrations/20260910153441_master_data_lifecycle_history_contracts.sql`
3. `supabase/migrations/20260910155734_master_data_lifecycle_guard_repairs.sql`
4. `supabase/tests/master_data_idempotency_concurrency_test.sh`
5. `supabase/tests/master_data_lifecycle_history_test.sql`
6. `supabase/tests/master_data_seed_guard_test.sql`

No web/UI implementation, Internal User/RBAC management, Vercel deployment, connected Supabase application, `main` mutation, or unrelated workflow is part of this candidate.

## Canonical contract to review

Review against `project_control/prompts/SLICE-06_TASK-001_v2.md` and its listed canonical sources. In particular verify:

- closed allowlist of the 11 Phase-1 business master entities and closed per-type writable DTOs;
- Active Internal User + effective `master_data.manage`, with Root only through the accepted authorization helper;
- no broad authenticated/anon direct business-master DML and no private-helper bypass;
- `SECURITY DEFINER` wrappers use `SET search_path = ''` and schema-qualified references;
- explicit idempotency key scope/fingerprint/replay semantics across create/update/delete-or-inactivate, including authorization before replay and real concurrent duplicate serialization;
- target row lock + optimistic version check before update/delete lifecycle decisions;
- complete reference predicate for hard-delete versus Inactive;
- referenced structural history immutability while label correction remains allowed and `requires_demo_topic` remains advisory;
- inactive masters unavailable for new selection while retained historical references remain operable;
- Unit/Team/Position hierarchy and active-parent selection;
- Interview Format room/link structural semantics; Room identity-bearing fields; Document Type scope semantics;
- canonical Document Type seed scopes materialized safely, including fail-closed handling of referenced scope conflicts;
- parent/master `FOR KEY SHARE` guards correctly close selection-vs-inactivation races without invalidating unchanged history;
- same-transaction canonical audit events and idempotency records;
- Integration CI includes the three S06 database acceptance regressions without weakening existing gates.

## Producer verification already executed

Validation v3 run `34551607089`: PASS.

Exact-candidate validation v4 run `34551826518`: PASS.

The exact-candidate run executed:

- local Supabase start;
- `supabase db reset` from zero;
- PRE-S04 accepted database regression;
- TASK-S05-001 accepted contextual-report regression;
- TASK-S05-002 HR report management regression;
- TASK-S05-002 HR report DTO privacy regression;
- TASK-S06-001 canonical seed/active-reference guard regression;
- TASK-S06-001 lifecycle/history/security/idempotency regression;
- TASK-S06-001 real two-session concurrent idempotency regression;
- `git diff --check` and static security/CI marker checks;
- Supabase stop.

These are producer claims only; independent review must form its own verdict and rerun checks when supported.

## Independent verification requested

At minimum, when the reviewer environment supports them:

```bash
git diff --check 0ec409915bdd00b61b1b7affdb77ec778c7c1dc7...0c4b94b29e08e1ad877583bdb90d522e5577dccc
supabase start
supabase db reset
docker exec -i supabase_db_eiu-recruitment-dev psql -U postgres -d postgres < supabase/tests/pre_s04_contract_repairs_test.sql
docker exec -i supabase_db_eiu-recruitment-dev psql -U postgres -d postgres < supabase/tests/interviewer_report_contextual_read_test.sql
docker exec -i supabase_db_eiu-recruitment-dev psql -U postgres -d postgres < supabase/tests/hr_report_management_test.sql
docker exec -i supabase_db_eiu-recruitment-dev psql -U postgres -d postgres < supabase/tests/hr_report_dto_privacy_test.sql
docker exec -i supabase_db_eiu-recruitment-dev psql -U postgres -d postgres < supabase/tests/master_data_seed_guard_test.sql
docker exec -i supabase_db_eiu-recruitment-dev psql -U postgres -d postgres < supabase/tests/master_data_lifecycle_history_test.sql
bash supabase/tests/master_data_idempotency_concurrency_test.sh
supabase stop
```

Also independently inspect the migrations for injection safety, privilege/ACL behavior, lock ordering, race safety, structural-field classification, historical semantics, audit atomicity, and compatibility with accepted commands. Web acceptance is not a product-code requirement for this backend-only candidate, but the Integration CI workflow modification itself must be reviewed for correctness.

## Required reviewer output

Return exactly enough durable information to route the gate:

- `WORK_ID: S06-001-IMPLEMENTATION-REVIEW-001`
- `REVIEWED_SHA: 0c4b94b29e08e1ad877583bdb90d522e5577dccc`
- `VERDICT: PASS | BLOCKING_REPAIR | OWNER_DECISION_REQUIRED`
- `SOURCE_REOPEN_REQUIRED: true | false`
- `BLOCKING_FINDINGS`
- `NON_BLOCKING_OBSERVATIONS`
- `VERIFICATION_EXECUTED`
- `SECURITY_ASSESSMENT`
- `ACCEPTED_CONTRACT_REUSE_ASSESSMENT`
- `ACCEPTANCE_STATEMENT`

Suggested durable evidence coordinates:

- branch: `review/S06-001-IMPL-0c4b94b-v1`
- path: `project_control/reviews/S06_001_IMPLEMENTATION_REVIEW_0c4b94b_v1.md`

Persist the actual review evidence in a commit descended from the reviewed candidate (or otherwise make the reviewed SHA relationship unambiguous). Do not invent evidence coordinates.
