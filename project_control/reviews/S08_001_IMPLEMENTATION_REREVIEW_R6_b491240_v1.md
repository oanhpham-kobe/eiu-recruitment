# TASK-S08-001 — Independent Implementation Re-review R6 Evidence

WORK_ID: `S08-001-IMPLEMENTATION-REREVIEW-006`

REVIEWER: `OMP_EIU_REVIEWER`

REVIEWED_SHA: `b4912401ed1fbbcbd441710581e8a165c5f68e2c`

PRIOR_REVIEWED_SHA: `2492625ac59f0314cb176cdbd60029d9a029f9f0`

BASELINE_SHA: `141146d52a05b0d698178ba7ef097690d5ef2a27`

VERDICT: `PASS`

SOURCE_REOPEN_REQUIRED: `false`

## Integration failure repair assessment

Integration CI run `35517082611` failed on the prior serialized candidate during local Supabase startup while applying `20260920010000_application_inbox_search_hardening.sql` with:

`ERROR: argument of OFFSET must not contain variables (SQLSTATE 42P10)`

The reviewer confirmed the root cause was the `paged` CTE referencing row variable `q.effective_page_size` from `cross join query_spec q` inside `OFFSET/LIMIT`.

Candidate `b4912401ed1fbbcbd441710581e8a165c5f68e2c` removes that row-variable dependency and restores the accepted PRE-S04 parameter-only expression:

```sql
case
  when p_page_size in (25, 50, 100) then p_page_size
  else 25
end
```

The reviewer assessed this as resolving SQLSTATE `42P10` while preserving canonical page sizes `25/50/100`, default `25`, and invalid-value fallback `25`.

## Blocking findings

`NONE`

## Non-blocking observations

- Pre-existing Biome diagnostics in `src/styles/interview.css` and `src/components/interview/InterviewPage.tsx` remain outside the S08-001 delta.
- All 10 task-diff files were assessed as compliant with repository invariants and canonical authorities.

## Verification executed by reviewer

- Detached clean worktree at exact candidate `b4912401ed1fbbcbd441710581e8a165c5f68e2c`.
- `python project_control/validate_control_plane.py`: PASS.
- `python project_control/validate_omp_native.py`: PASS.
- `git diff --check 141146d52a05b0d698178ba7ef097690d5ef2a27...b4912401ed1fbbcbd441710581e8a165c5f68e2c`: CLEAN.
- `git diff --check 2492625ac59f0314cb176cdbd60029d9a029f9f0...b4912401ed1fbbcbd441710581e8a165c5f68e2c`: CLEAN.
- `git status --short`: CLEAN.
- Biome check across the six touched web files: PASS, 0 errors.
- Focused S08 web test: PASS, 4/4.
- Predecessor Application Inbox web test: PASS, 8/8.
- `npm run design:check`: PASS.
- `npm run typecheck`: PASS.

## Verification not run

Local database replay / SQL tests were NOT_RUN in the reviewer Windows environment because Supabase CLI was unavailable and Docker was not running. The reviewer compared the repair with the accepted PRE-S04 parameter-only pagination form. `npm run build` was NOT_RUN locally because of the documented Windows Turbopack junction restriction; the prior exact-integration Linux build had already passed.

## Repair delta assessment

The repair diff `2492625ac59f0314cb176cdbd60029d9a029f9f0...b4912401ed1fbbcbd441710581e8a165c5f68e2c` modifies only:

`supabase/migrations/20260920010000_application_inbox_search_hardening.sql`

with `13 insertions / 9 deletions`.

It removes `q.effective_page_size` and `cross join query_spec q` from the `paged` CTE and replaces the pagination uses with the inline parameter-only CASE expression. No search predicates, index definitions, latest-row anti-joins, web code, or tests changed.

## Database replay assessment

The reviewer confirmed the repair restores the same pagination-expression form used by accepted migration `20260906005000_pre_s04_contract_repairs.sql`. The previous forbidden row-variable reference is removed.

## Regression assessment

Candidate-group pagination, page clamping, deterministic ordering, complete historical Submission children, version tokens, active-Application semantics, and `submissions.view` / Root Admin permissions remain intact. Web behavior including 300 ms debounce, canonical page sizes, selection reset, and request-local PII transport remains passing.

## Security assessment

PII search query text remains component/request-local and excluded from URL/history/analytics/server logs. Database access remains server-side through the `security invoker` RPC with pinned search path and qualified objects. Authorization and RLS remain authoritative.

## Acceptance statement

Candidate `b4912401ed1fbbcbd441710581e8a165c5f68e2c` received independent reviewer `PASS`.

`PASS applies strictly to exact SHA b4912401ed1fbbcbd441710581e8a165c5f68e2c.`

This evidence does not authorize OMP to serialize into integration, create an accepted checkpoint, mutate `main`, deploy Vercel, or apply hosted database changes.
