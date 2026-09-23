# TASK-S08-001 — Implementation Re-review R8 Gate

WORK_ID: `S08-001-IMPLEMENTATION-REREVIEW-008`
REVIEWER: `OMP_EIU_REVIEWER`
TASK: `TASK-S08-001 — Application Inbox Search and Indexed Pagination Hardening`
BASELINE_SHA: `141146d52a05b0d698178ba7ef097690d5ef2a27`
PRIOR_REVIEWED_SHA: `c41392f8baf56931b6d2e22d8d082dfdf27076ef`
REVIEWED_SHA: `d3fcdfc9c9f057e70f9c74b0dbaaa4d2594f0daf`
REPAIR_DIFF: `c41392f8baf56931b6d2e22d8d082dfdf27076ef...d3fcdfc9c9f057e70f9c74b0dbaaa4d2594f0daf`
SOURCE_REOPEN_EXPECTATION: `false`

## Why R8 is required

OMP R7 independently PASSed exact candidate `c41392f8baf56931b6d2e22d8d082dfdf27076ef`, which added the two canonical S08 database regressions to Integration CI.

That reviewed workflow was serialized onto integration commit:

`1d68f9fea0116b0c279a053a06b4befa49fac1fc`

Fresh exact-SHA evidence:

- Governance CI `35878089081`: PASS.
- Integration CI `35878089069`: FAIL.
- Web verification: PASS.
- Database migration replay from zero: PASS.
- PRE-S04 regression suite: PASS.
- `Execute TASK-S08-001 Accepted Application Inbox SQL Regression Assertions`: FAIL.
- Search-hardening regression step was skipped after the failure.

Database job: `107239214938`.

The exact failure from `supabase/tests/application_inbox_read.sql` was:

```text
ERROR: duplicate key value violates unique constraint "one_root_admin_uq"
DETAIL: Key (is_root_admin)=(t) already exists.
```

## Failure classification

This is a CI test-isolation/order defect, not an S08 product/migration regression.

`supabase/tests/application_inbox_read.sql` is an accepted standalone SQL regression whose header says it must run against an unlinked disposable local Supabase database after all migrations. It opens a transaction, creates its own Root Admin fixture, and rolls back.

`supabase/tests/application_inbox_search_hardening_test.sql` likewise opens a transaction, creates its own Root Admin fixture, and rolls back.

In the R7 workflow, however, the PRE-S04 database integration suite ran first and left its Root Admin fixture in the shared local database. The subsequent standalone Application Inbox test therefore failed during fixture creation before testing the Inbox contract.

The two SQL test files themselves are unchanged at R8:

- `supabase/tests/application_inbox_read.sql` blob `de37cec7e4d0c8cf9f18b2590812c12de5e82fba`
- `supabase/tests/application_inbox_search_hardening_test.sql` blob `2e6d92459118bcdc67fc9809d20def612a3827ff`

## Producer R8 repair

Repair candidate:

`d3fcdfc9c9f057e70f9c74b0dbaaa4d2594f0daf`

Commit message:

`ci(s08-001): isolate inbox regressions before predecessor fixtures`

The R7→R8 delta modifies only:

`.github/workflows/integration-ci.yml`

Diff size:

`4 additions / 4 deletions`

The repair changes ordering only. After `supabase db reset`, the database job now runs:

1. `Execute TASK-S08-001 Accepted Application Inbox SQL Regression Assertions`
2. `Execute TASK-S08-001 Search Hardening Regression Assertions`
3. `Execute PRE-S04 Database Integration & Regression Assertions`
4. all existing later regression suites unchanged.

The two S08 command bodies and paths are unchanged and still use `psql -v ON_ERROR_STOP=1` against `supabase_db_eiu-recruitment-dev`.

No product code, migration, SQL test contents, Web code, search/index/RLS behavior, secrets, or hosted database interaction changed.

## Mandatory independent review

Review exact candidate `d3fcdfc9c9f057e70f9c74b0dbaaa4d2594f0daf`, not this gate commit.

Verify at minimum:

- R7→R8 changes only `.github/workflows/integration-ci.yml`;
- the delta is an ordering-only move of the two already-reviewed S08 database steps;
- `application_inbox_read.sql` and `application_inbox_search_hardening_test.sql` contents/blobs remain unchanged;
- both S08 tests execute after `supabase db reset` and before PRE-S04 fixture-producing regressions;
- both still use `-v ON_ERROR_STOP=1` against the disposable local Supabase DB;
- no prior database/web/governance gate is removed or weakened;
- no product/runtime/security contract is changed;
- `git diff --check` and project control validators pass.

If disposable local Docker/Supabase is available, the reviewer may execute the two S08 regressions in the repaired order. If unavailable, report NOT_RUN with exact reason. Never use connected/hosted Supabase.

OMP is reviewer only: do not edit, reorder, format, commit, mutate branches, deploy Vercel, apply hosted migrations, use production secrets, create checkpoints, or materialize TASK-S08-002.

## Required routing outcome

Return `PASS`, `BLOCKING_REPAIR`, or `OWNER_DECISION_REQUIRED` for exact SHA `d3fcdfc9c9f057e70f9c74b0dbaaa4d2594f0daf`, including explicit assessment of the R7 CI failure classification and whether the ordering repair closes it without weakening any gate.
