# TASK-S08-001 — Implementation Re-review R4 Gate

WORK_ID: S08-001-IMPLEMENTATION-REREVIEW-004
REVIEWER_ROLE: OMP_EIU_REVIEWER
REPOSITORY: oanhpham-kobe/eiu-recruitment
TASK_BRANCH: chatgpt/TASK-S08-001-application-inbox-search-hardening
BASELINE_SHA: 141146d52a05b0d698178ba7ef097690d5ef2a27
PRIOR_REVIEWED_SHA: b006cc930fd3f93aaf48cf23f5939bfe522090c9
REVIEWED_SHA: 3f67d4c5d16766a4ada5aa1b70742f7c986e39d6
REPAIR_DIFF: b006cc930fd3f93aaf48cf23f5939bfe522090c9...3f67d4c5d16766a4ada5aa1b70742f7c986e39d6
SOURCE_REOPEN_EXPECTATION: false unless a concrete canonical contradiction is found.

## Reviewer boundary

OMP is reviewer only. Do not implement, repair, format with --write, edit files, mutate branches, deploy Vercel, apply connected/hosted Supabase migrations, use production secrets, or materialize TASK-S08-002.

## Prior finding to close

S08-001-IMPL-002-R3 remained blocking because `web/src/__tests__/application-inbox-search-pagination.test.ts` failed Biome format validation. OMP reported that the two timeout tests still used the multiline test-call shape whose callback bodies remained indented four spaces, while Biome expected the call signature flattened and the callback body indented two spaces.

## Producer R4 repair

Exact candidate commit: `3f67d4c5d16766a4ada5aa1b70742f7c986e39d6`

Commit message: `style(s08-001): apply Biome test callback layout`

Only file changed from R3:

- `web/src/__tests__/application-inbox-search-pagination.test.ts`

Repair intent:

- flatten both `test("...", { timeout: 60_000 }, async () => {` signatures;
- dedent each callback body from four spaces to two spaces;
- preserve every assertion, timeout, search value, URL/history assertion, page-size assertion, and behavior;
- no production code, SQL, RPC, authorization, RLS, or PII transport change.

## Mandatory verification

At exact SHA `3f67d4c5d16766a4ada5aa1b70742f7c986e39d6` run at minimum:

```bash
cd web
npx biome check src/__tests__/application-inbox-search-pagination.test.ts
node --conditions react-server --test --import tsx src/__tests__/application-inbox-search-pagination.test.ts
node --conditions react-server --test --import tsx src/__tests__/application-inbox.test.ts
npm run typecheck
npm run design:check
```

Also run `npm run lint` when supported and distinguish unrelated pre-existing diagnostics from S08-001 candidate diagnostics.

Run read-only governance checks:

```bash
python project_control/validate_control_plane.py
python project_control/validate_omp_native.py
git diff --check 141146d52a05b0d698178ba7ef097690d5ef2a27...3f67d4c5d16766a4ada5aa1b70742f7c986e39d6
git diff --check b006cc930fd3f93aaf48cf23f5939bfe522090c9...3f67d4c5d16766a4ada5aa1b70742f7c986e39d6
```

If local build or Supabase verification remains unavailable for the same environment reasons, report `NOT_RUN` with the exact reason. Do not substitute hosted Supabase.

## Required output

Return:

- WORK_ID: `S08-001-IMPLEMENTATION-REREVIEW-004`
- REVIEWER: `OMP_EIU_REVIEWER`
- REVIEWED_SHA: `3f67d4c5d16766a4ada5aa1b70742f7c986e39d6`
- PRIOR_REVIEWED_SHA: `b006cc930fd3f93aaf48cf23f5939bfe522090c9`
- BASELINE_SHA: `141146d52a05b0d698178ba7ef097690d5ef2a27`
- VERDICT: `PASS | BLOCKING_REPAIR | OWNER_DECISION_REQUIRED`
- SOURCE_REOPEN_REQUIRED: `true | false`
- PRIOR_FINDING_CLOSURE with `S08-001-IMPL-002-R3: CLOSED | OPEN`
- BLOCKING_FINDINGS
- NON_BLOCKING_OBSERVATIONS
- VERIFICATION_EXECUTED
- VERIFICATION_NOT_RUN
- REPAIR_DELTA_ASSESSMENT
- REGRESSION_ASSESSMENT
- SECURITY_ASSESSMENT
- ACCEPTANCE_STATEMENT

A PASS applies only to exact SHA `3f67d4c5d16766a4ada5aa1b70742f7c986e39d6` and does not authorize OMP to serialize into integration, create checkpoints, mutate main, deploy, or apply hosted database changes.
