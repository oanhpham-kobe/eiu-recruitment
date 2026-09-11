# TASK-S06-002 — Independent Implementation Re-Review Handoff R2

## Immutable review target

- WORK_ID: `S06-002-IMPLEMENTATION-REVIEW-001-R2`
- REPOSITORY: `oanhpham-kobe/eiu-recruitment`
- BRANCH: `oanhpham-kobe/TASK-S06-002-user-rbac-identity`
- EXACT_REVIEW_SHA: `7c37d46fa504b5d98b156735d7355f1d938be0bf`
- BASELINE_SHA: `0a2ccdfedc477f9766c9aaa03739d16a7ed83c01`
- R1_REVIEWED_SHA: `a7aa037e26cda6ba70153539c1dfc15c3fba37e6`
- R1_VERDICT: `BLOCKING_REPAIR`
- R1_SOURCE_REOPEN_REQUIRED: `false`
- CANDIDATE_CONTAINS_R2_GATE: `project_control/reviews/S06_002_IMPLEMENTATION_R2_GATE_v1.md`
- COORDINATOR_PRODUCER_VERIFIER: GitHub Actions run `34621266079`

The reviewer must independently verify `git rev-parse HEAD` equals `7c37d46fa504b5d98b156735d7355f1d938be0bf`. This handoff is coordinator-authored routing evidence, not reviewer evidence and not an acceptance claim.

## R1 blockers to re-review

1. **Immutable review gate/evidence** — R1 Owner-transported verdict evidence, the R1 gate, and the generic R2 gate now live inside the candidate tree. The exact SHA is supplied here because a commit cannot embed its own future hash.
2. **RLS/column-ACL consumer migration** — authenticated raw `public.app_users.auth_user_id` access remains narrowed; retained request-scoped server consumers were migrated to minimum-safe `get_current_internal_session()` / `get_current_internal_binding_status()` RPCs and related tests were reconciled.
3. **Dormant participant history** — statement-level current-participant eligibility recheck is scoped to canonical `resource_blocking` Interviews so CANCELLED/inactive/unscheduled/fully elapsed history can be maintained without re-selecting inactive historical participants.
4. **Application owner/lifecycle lock order** — owner writers acquire target `app_users` row before shared Internal User advisory serialization and revalidate after the full lock set, matching lifecycle/RBAC order.
5. **First-bind/Root-rebind lock order** — both identity paths use normalized-email advisory before target directory row, then Internal User advisory, with trusted Auth evidence revalidation.

## Producer verification evidence — exact SHA only

GitHub Actions run `34621266079` checked out `7c37d46fa504b5d98b156735d7355f1d938be0bf` independently in all jobs and completed PASS:

- static job `103335549527`: exact SHA, `git diff --check`, candidate-contained review artifacts, R2 three-test-file tail, and no retained raw `app_users.auth_user_id` query in the affected request-scoped production paths;
- web job `103335549460`: `npm ci`, `npm audit --audit-level=high`, design check, lint, typecheck, production build, Playwright Chromium install, and full `npm run test` — PASS;
- database job `103335549295`: Supabase CLI `2.116.0`, local start, zero-state `supabase db reset`, focused Internal User/RBAC/Identity + dormant-history regression, lifecycle/public-command concurrency, Application reactivation/participant, Interview lifecycle, round/conflict, copy, bulk assignment, all retained S06-001 seed/lifecycle/durable-history regressions, `supabase db lint --local --level error`, and clean local stop — PASS.

The candidate is 17 commits ahead of the pre-task baseline and changes 32 files. The R2 technical repair was append-only; accepted migration history was not rewritten.

## Independent review instructions

Review the exact candidate rather than trusting producer verification. Re-read the five R1 blockers against effective code and public command paths, including lock ordering across lifecycle/owner/participant/identity writers, RLS/column privileges, trusted session projections, dormant-history behavior, Root protections, idempotency, audit behavior, and accepted S06-001/Application/Interview contract reuse.

Return at minimum:

- `WORK_ID`
- `REVIEWED_REPOSITORY`
- `REVIEWED_BRANCH`
- `REVIEWED_SHA`
- `VERDICT` (`PASS` or `BLOCKING_REPAIR`)
- `SOURCE_REOPEN_REQUIRED`
- `BLOCKING_FINDINGS`
- `NON_BLOCKING_OBSERVATIONS`
- `VERIFICATION_EXECUTED`
- `IDENTITY_BIND_ASSESSMENT`
- `RBAC_VISIBILITY_ASSESSMENT`
- `LIFECYCLE_CONCURRENCY_ASSESSMENT`
- `SECURITY_ASSESSMENT`
- `ACCEPTED_CONTRACT_REUSE_ASSESSMENT`
- `ACCEPTANCE_STATEMENT`
- `EVIDENCE_PERSISTENCE` with truthful coordinates or `UNAVAILABLE`.

## Governance boundary

Reviewer is read-only. Do not modify implementation, refs, integration, `main`, PRs, Vercel, connected Supabase, or later Slice-06 state. A producer-verified candidate remains unaccepted until this independent exact-SHA review returns PASS.
