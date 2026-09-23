# TASK-S08-001 — Implementation Re-review R7 Gate

WORK_ID: `S08-001-IMPLEMENTATION-REREVIEW-007`

REVIEWER: `OMP_EIU_REVIEWER`

TASK: `TASK-S08-001 — Application Inbox Search and Indexed Pagination Hardening`

BASELINE_SHA: `141146d52a05b0d698178ba7ef097690d5ef2a27`

PRIOR_REVIEWED_SHA: `b4912401ed1fbbcbd441710581e8a165c5f68e2c`

REVIEWED_SHA: `c41392f8baf56931b6d2e22d8d082dfdf27076ef`

REPAIR_DIFF: `b4912401ed1fbbcbd441710581e8a165c5f68e2c...c41392f8baf56931b6d2e22d8d082dfdf27076ef`

SOURCE_REOPEN_EXPECTATION: `false`

## Why R7 is required

OMP R6 independently PASSed exact candidate `b4912401ed1fbbcbd441710581e8a165c5f68e2c` after the PostgreSQL pagination repair.

The producer serialized the exact repaired migration blob onto integration commit:

`ffec3235f888b4247752e5a4dfa7d0f1b98a5235`

Fresh exact-SHA integration gates then completed successfully:

- Integration CI run `35875164497`: PASS.
- Governance CI run `35875164427`: PASS.
- Web verification: PASS, including lint, typecheck, Linux build and full affected web tests.
- Database integration: PASS, including local Supabase startup, migration replay, crossed predecessor regressions and DB lint.

The SQLSTATE `42P10` failure from the prior integration attempt is therefore resolved.

## Producer self-audit acceptance gap

Before creating an acceptance checkpoint, the producer compared the canonical prompt against the actual integration workflow.

Canonical prompt `project_control/prompts/SLICE-08_TASK-001_v2.md`, section **E. Required regression coverage**, explicitly requires the expected database gates to include:

- clean disposable/unlinked local migration replay;
- new S08-001 Search contract test;
- accepted Application Inbox SQL regression;
- relevant crossed predecessor regressions;
- DB lint.

The existing `.github/workflows/integration-ci.yml` did replay migrations, crossed predecessor regressions and DB lint, but it did not execute either of the two S08 Application Inbox SQL files:

- `supabase/tests/application_inbox_read.sql`
- `supabase/tests/application_inbox_search_hardening_test.sql`

OMP R6 could not execute those locally because Supabase CLI/Docker were unavailable in its Windows environment. Therefore the exact candidate had not yet obtained executable evidence for those two canonical database gates.

Acceptance is intentionally withheld until this gap is closed.

## Producer R7 repair

Repair commit:

`c41392f8baf56931b6d2e22d8d082dfdf27076ef`

Message:

`ci(s08-001): execute application inbox database regressions`

The R6→R7 diff changes only:

`.github/workflows/integration-ci.yml`

Diff size:

`8 additions / 0 deletions`

It adds exactly two database verification steps immediately after the PRE-S04 regression:

```yaml
- name: Execute TASK-S08-001 Accepted Application Inbox SQL Regression Assertions
  run: |
    docker exec -i supabase_db_eiu-recruitment-dev psql -v ON_ERROR_STOP=1 -U postgres -d postgres < supabase/tests/application_inbox_read.sql

- name: Execute TASK-S08-001 Search Hardening Regression Assertions
  run: |
    docker exec -i supabase_db_eiu-recruitment-dev psql -v ON_ERROR_STOP=1 -U postgres -d postgres < supabase/tests/application_inbox_search_hardening_test.sql
```

No migration, SQL test content, Web code, RLS, permission, query logic, index definition, page-size behavior or PII transport behavior changed.

## Mandatory independent review

Review exact candidate:

`c41392f8baf56931b6d2e22d8d082dfdf27076ef`

Do not review this gate commit as the candidate.

Verify at minimum:

1. R6→R7 changes only `.github/workflows/integration-ci.yml`.
2. The diff consists only of the two required S08 database test invocations.
3. Both commands use the same disposable local Supabase database as the rest of the DB integration job.
4. Both commands use `-v ON_ERROR_STOP=1` so SQL assertion failures fail CI.
5. The paths are exact and exist in the candidate.
6. The added steps run after migration replay and before later crossed predecessor tests.
7. The change closes the canonical prompt database-gate evidence gap without weakening any previous CI gate.
8. No product/runtime behavior changes are introduced.
9. `git diff --check` and control-plane validators pass.

If a disposable local Supabase environment is available, the reviewer may execute the two SQL files read-only against a locally replayed database. If unavailable, report NOT_RUN with the precise environment reason. Do not use connected or hosted Supabase.

## Reviewer boundary

OMP is reviewer only. Do NOT edit files, repair findings, commit changes, mutate task/review/integration/main branches, deploy Vercel, apply hosted Supabase migrations, use production secrets, create/move acceptance checkpoints, or materialize TASK-S08-002.

## Required routing outcome

Return `PASS`, `BLOCKING_REPAIR`, or `OWNER_DECISION_REQUIRED` for exact SHA `c41392f8baf56931b6d2e22d8d082dfdf27076ef`, with `SOURCE_REOPEN_REQUIRED`, canonical-gate closure assessment, blocking findings, verification executed/not-run, repair-delta assessment, regression/security assessment, and acceptance statement.
