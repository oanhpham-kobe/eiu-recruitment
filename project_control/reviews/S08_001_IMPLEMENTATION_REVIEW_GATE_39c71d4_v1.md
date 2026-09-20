# TASK-S08-001 Independent Implementation Review Gate

## Identity

- WORK_ID: `S08-001-IMPLEMENTATION-REVIEW-001`
- REVIEWER_ROLE: `OMP_EIU_REVIEWER`
- REPO: `oanhpham-kobe/eiu-recruitment`
- TASK_BRANCH: `chatgpt/TASK-S08-001-application-inbox-search-hardening`
- PRE_TASK_BASELINE_SHA: `141146d52a05b0d698178ba7ef097690d5ef2a27`
- REVIEWED_SHA: `39c71d4f958de5cb99e249fc3c5a88e5597c9be3`
- REVIEW_DIFF: `141146d52a05b0d698178ba7ef097690d5ef2a27...39c71d4f958de5cb99e249fc3c5a88e5597c9be3`
- SOURCE_REOPEN_EXPECTATION: `false` unless a concrete canonical contradiction is proven.

The reviewed candidate is frozen at the exact `REVIEWED_SHA`. Do not review a moving branch tip as a substitute. The review-gate branch may contain this gate artifact after the reviewed candidate; that does not change `REVIEWED_SHA`.

## Reviewer boundary

OMP is an independent reviewer only.

OMP MUST NOT:

- implement or repair product code;
- edit migrations or tests;
- modify Web/UI production files;
- mutate the task branch, integration branch, or `main`;
- deploy Vercel;
- apply connected/hosted Supabase migrations;
- use production secrets;
- materialize TASK-S08-002.

Perform read-only inspection and local disposable verification only. Return findings/evidence to ChatGPT for producer repair if needed.

## Frozen implementation scope

Exactly nine files differ from the governed pre-task baseline:

1. `project_control/reviews/S08_001_IMPLEMENTATION_BASELINE_CORRECTION_v1.md`
2. `supabase/migrations/20260920010000_application_inbox_search_hardening.sql`
3. `supabase/tests/application_inbox_read.sql`
4. `supabase/tests/application_inbox_search_hardening_test.sql`
5. `web/src/__tests__/application-inbox-search-pagination.test.ts`
6. `web/src/app/application-inbox-actions.ts`
7. `web/src/components/inbox/ApplicationInboxTable.tsx`
8. `web/src/lib/application-inbox/model.ts`
9. `web/src/lib/application-inbox/server.ts`

No S08-002 implementation is part of this candidate.

## Mandatory baseline correction

Before judging the implementation, inspect:

- `project_control/reviews/S08_001_IMPLEMENTATION_BASELINE_CORRECTION_v1.md`
- `supabase/migrations/20260906005000_pre_s04_contract_repairs.sql`, especially the final PRE-S04 Application Inbox Search & Pagination Alignment section.

The source reconciliation originally emphasized an older Inbox RPC baseline. The later accepted PRE-S04 migration is the effective predecessor and already provided default page size 25, 25/50/100 page-size semantics, Name minimum length 2, Email/Phone prefix behavior, Candidate-group pagination, complete historical children, deterministic ordering, active-Application semantics, and version tokens.

The S08 implementation therefore hardens that final PRE-S04 RPC rather than resurrecting an older Slice-03 definition.

The current producer decision is stricter than the optional compatibility language in the canonical task prompt: database/server page sizes are canonical `25/50/100`, and invalid values fall back to `25`. Do not require arbitrary small page sizes merely because the prompt allowed them if necessary for predecessor compatibility.

## Canonical contract to review

Review against:

- `project_control/prompts/SLICE-08_TASK-001_v2.md`
- `project_control/reviews/S08_001_SOURCE_RECONCILIATION_v2.md`
- `recruitment_webapp/review_pack/58_SEARCH_AND_INDEXING_STRATEGY.md`
- `recruitment_webapp/review_pack/38_NON_FUNCTIONAL_REQUIREMENTS.md`
- `recruitment_webapp/review_pack/67_WEB_SECURITY_BASELINE.md`
- `recruitment_webapp/review_pack/39_SECURITY_RLS_MATRIX.md`
- `recruitment_webapp/review_pack/59_RLS_POLICY_BLUEPRINT.md`
- `recruitment_webapp/review_pack/99_INDEPENDENT_REVIEW_IMPLEMENTATION_ALIGNMENT_V1_18.md`
- `recruitment_webapp/review_pack/100_TECHNICAL_PRECODE_GATE_V1_18.md`
- `recruitment_webapp/app_spec.yaml`

Explicitly verify all of the following:

1. Vietnamese Name normalization is accent-insensitive, case-insensitive, deterministic, and genuinely safe to declare `IMMUTABLE`.
2. The Name trigram index expression exactly matches the production Name predicate.
3. Application Inbox Email authority remains current `candidates.email`; the supporting lower-case prefix index matches that actual predicate.
4. Phone normalization strips non-digits consistently and the prefix index expression matches the production predicate.
5. User `%`, `_`, and backslash wildcard characters are escaped safely for LIKE semantics.
6. Query classification is deterministic across `EMPTY`, `EMAIL`, `PHONE`, `NAME`, and `NONE`; one-character generic Name queries cannot trigger broad scans.
7. Name and Phone matching apply only to the Candidate's latest Submission; an older matching Submission must not promote the Candidate.
8. Candidate-group pagination remains parent-based and returns complete historical Submission children for every paged Candidate.
9. Candidate-group `total_count`, deterministic ordering, immutable-ID tie-breakers, and page clamping remain correct.
10. Page-size contract is exactly `25/50/100`, default `25`, invalid values including `1` fall back to `25` across DB, adapter, action, model, UI, and focused tests.
11. Web action/adapter/component types and all relevant call-sites agree on the page-size contract.
12. Search/filter debounce is exactly `300 ms`; filter/search/page-size changes reload page 1 as required.
13. Page-size/filter/search/page context changes clear page-scoped selection as intended.
14. Name/Email/Phone query text never enters URL query params, browser history, shareable filter state, analytics, telemetry, audit payloads, clear-text server logs, or clear-text errors.
15. No privileged DB query is moved into browser code; no service-role credential exposure is introduced.
16. `submissions.view` plus Root Admin behavior remains intact and RLS remains authoritative.
17. Candidate/submission optimistic version tokens are preserved.
18. Active-Application projection/filter semantics are preserved.
19. Accepted `application_inbox_read.sql` predecessor behavior remains compatible.
20. New S08 SQL regression meaningfully covers accent-insensitive Name, Candidate email authority, Phone normalization, wildcard safety, latest-row negative behavior, authorization, full child history, page-size fallback, and query-plan/index eligibility.
21. Query-plan evidence demonstrates index eligibility without falsely claiming tiny-fixture production p95 proof.
22. No unrelated task or TASK-S08-002 materialization is present.

## Producer verification state

Do not treat producer claims as independent evidence.

Producer has performed static exact-source self-audit and repaired two self-audit findings before freezing this SHA:

- stale focused Web adapter test expectations for invalid page sizes;
- stale page-size wording in the implementation baseline-correction artifact.

No full exact-candidate CI PASS is claimed for `39c71d4f958de5cb99e249fc3c5a88e5597c9be3`.

## Independent verification requested

When the reviewer environment supports it, independently run at least:

```bash
git status --short
git rev-parse HEAD
git diff --check 141146d52a05b0d698178ba7ef097690d5ef2a27...39c71d4f958de5cb99e249fc3c5a88e5597c9be3
git diff --stat 141146d52a05b0d698178ba7ef097690d5ef2a27...39c71d4f958de5cb99e249fc3c5a88e5597c9be3
```

Review the exact diff and exact files at `39c71d4f958de5cb99e249fc3c5a88e5597c9be3`.

For Web, run the repository-supported gates, including at minimum the focused S08 test and, where feasible:

```bash
cd web
npm run test -- --test-name-pattern="Application Inbox" || npm run test
npm run lint
npm run typecheck
npm run build
npm run design:check
```

Use the repository's actual test runner syntax if the focused command above is not supported; report the exact command actually executed rather than silently skipping the gate.

For DB, use only an unlinked/disposable local Supabase environment. Where feasible:

```bash
supabase start
supabase db reset
# Execute the repository's accepted predecessor Inbox regression and the S08 focused regression
# using the local disposable Postgres container/database naming actually present in the environment.
supabase db lint
supabase stop
```

At minimum execute:

- `supabase/tests/application_inbox_read.sql`
- `supabase/tests/application_inbox_search_hardening_test.sql`

Also run relevant crossed predecessor Inbox/Candidate/Application lifecycle regressions when available and practical.

Run control-plane validators read-only:

```bash
python project_control/validate_control_plane.py
python project_control/validate_omp_native.py
```

If a command cannot run because of environment/tooling limitations, report `NOT_RUN` with the concrete reason. Do not convert an unavailable check into PASS.

## Required reviewer output

Return a self-contained review report with these exact routing fields:

- `WORK_ID: S08-001-IMPLEMENTATION-REVIEW-001`
- `REVIEWER: OMP_EIU_REVIEWER`
- `REVIEWED_SHA: 39c71d4f958de5cb99e249fc3c5a88e5597c9be3`
- `BASELINE_SHA: 141146d52a05b0d698178ba7ef097690d5ef2a27`
- `VERDICT: PASS | BLOCKING_REPAIR | OWNER_DECISION_REQUIRED`
- `SOURCE_REOPEN_REQUIRED: true | false`
- `BLOCKING_FINDINGS`
- `NON_BLOCKING_OBSERVATIONS`
- `VERIFICATION_EXECUTED`
- `VERIFICATION_NOT_RUN`
- `SEARCH_AND_INDEX_ASSESSMENT`
- `LATEST_ROW_AND_GROUPING_ASSESSMENT`
- `PAGE_SIZE_AND_WEB_BEHAVIOR_ASSESSMENT`
- `PII_AND_SECURITY_ASSESSMENT`
- `REGRESSION_COMPATIBILITY_ASSESSMENT`
- `QUERY_PLAN_EVIDENCE_ASSESSMENT`
- `ACCEPTANCE_STATEMENT`

For every blocking finding include file/path, concrete evidence, why it violates the governed contract, and a repair requirement. Do not repair it yourself.

A `PASS` means no blocking implementation defect is found at the exact reviewed SHA. It does not authorize integration, acceptance checkpoint creation, `main` mutation, deployment, or connected Supabase mutation.

Return the report to ChatGPT/Owner. Do not edit or commit product files.