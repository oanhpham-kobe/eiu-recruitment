# TASK-S08-001 — Implementation Re-review R6 Gate

WORK_ID: `S08-001-IMPLEMENTATION-REREVIEW-006`
REVIEWER: `OMP_EIU_REVIEWER`
TASK: `TASK-S08-001 — Application Inbox Search and Indexed Pagination Hardening`
BASELINE_SHA: `141146d52a05b0d698178ba7ef097690d5ef2a27`
PRIOR_REVIEWED_SHA: `2492625ac59f0314cb176cdbd60029d9a029f9f0`
REVIEWED_SHA: `b4912401ed1fbbcbd441710581e8a165c5f68e2c`
REPAIR_DIFF: `2492625ac59f0314cb176cdbd60029d9a029f9f0...b4912401ed1fbbcbd441710581e8a165c5f68e2c`
SOURCE_REOPEN_EXPECTATION: `false`

## Why R6 is required

OMP R5 independently PASSed exact candidate `2492625ac59f0314cb176cdbd60029d9a029f9f0`. The producer serialized those exact candidate blobs onto integration commit `46b5a1f0516f1701195143636a019ff5af92d08e` while preserving the integration-only prompt-review evidence.

Exact-integration checks on that SHA produced:

- Governance CI run `35517082663`: PASS.
- Integration CI run `35517082611`: FAIL.
- Web verification: PASS, including Linux lint, typecheck, build, Playwright installation, and full affected web acceptance tests.
- Database integration: FAIL during `supabase start`, while applying migration `20260920010000_application_inbox_search_hardening.sql`, before later DB assertions.

The exact PostgreSQL error was:

`ERROR: argument of OFFSET must not contain variables (SQLSTATE 42P10)`

The failing expression used `q.effective_page_size`, a row value introduced by `cross join query_spec q`, inside `OFFSET/LIMIT`.

## Canonical predecessor evidence

The accepted PRE-S04 predecessor `supabase/migrations/20260906005000_pre_s04_contract_repairs.sql` already uses a PostgreSQL-valid pattern: the canonical `25/50/100 -> else 25` `CASE` references the function parameter `p_page_size` directly inside `OFFSET` and `LIMIT`, rather than a FROM/CTE row variable.

## Producer repair

Repair commit:

`b4912401ed1fbbcbd441710581e8a165c5f68e2c`

Message:

`fix(s08-001): restore parameter-only pagination expressions`

The R5→R6 repair touches only:

`supabase/migrations/20260920010000_application_inbox_search_hardening.sql`

Diff size: 13 additions / 9 deletions.

Repair mechanics:

1. Remove the `effective_page_size` column from `query_input`.
2. Remove `cross join query_spec q` from the `paged` CTE.
3. Replace `q.effective_page_size` in page-count divisor, OFFSET multiplier, and LIMIT with the accepted predecessor form:

```sql
case
  when p_page_size in (25, 50, 100) then p_page_size
  else 25
end
```

No Name/Email/Phone search logic, indexes, latest-row proof, Candidate grouping, historical child projection, RLS/permission boundary, web behavior, or tests were changed.

## Mandatory independent review

Review exact candidate `b4912401ed1fbbcbd441710581e8a165c5f68e2c`, not this gate commit.

Verify at minimum:

- repair diff contains only the intended migration change;
- no `q.effective_page_size` remains in `OFFSET/LIMIT`;
- PRE-S04 accepted parameter-only pagination pattern is restored faithfully;
- canonical page-size contract remains exactly 25/50/100, default/fallback 25;
- page clamping and Candidate-group pagination semantics remain unchanged;
- no regression to search/index/latest-row/RLS/PII contracts;
- `git diff --check` and control-plane validators pass.

If disposable local Supabase/Docker is available, replay migrations and run relevant Application Inbox SQL tests. If unavailable, report NOT_RUN with exact reason; do not use connected/hosted Supabase. Exact-integration full CI will be rerun only after independent PASS.

OMP is reviewer only: do not edit/format/commit/mutate branches, deploy Vercel, apply hosted migrations, use production secrets, or materialize TASK-S08-002.

## Required routing outcome

Return `PASS`, `BLOCKING_REPAIR`, or `OWNER_DECISION_REQUIRED` for exact SHA `b4912401ed1fbbcbd441710581e8a165c5f68e2c`, with `SOURCE_REOPEN_REQUIRED`, blocking findings, verification executed/not-run, repair-delta assessment, regression/security assessment, and an acceptance statement.
