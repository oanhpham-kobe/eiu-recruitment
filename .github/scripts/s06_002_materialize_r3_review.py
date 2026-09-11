from pathlib import Path
import re

candidate = "73f03e00b6c2f90874eb17419e57ca58715a6990"
prior = "7c37d46fa504b5d98b156735d7355f1d938be0bf"
worker_run = "34628250213"
verify_run = "34628766807"

gate_path = Path("project_control/reviews/S06_002_IMPLEMENTATION_R3_GATE_73f03e0_v1.md")
handoff_path = Path("project_control/reviews/S06_002_IMPLEMENTATION_R3_HANDOFF_73f03e0_v1.md")

gate_path.write_text(f'''# TASK-S06-002 Independent Implementation Re-Review Gate R3

## Identity

- WORK_ID: `S06-002-IMPLEMENTATION-REVIEW-001-R3`
- REVIEWER: `eiu-reviewer`
- REPOSITORY: `oanhpham-kobe/eiu-recruitment`
- TASK_BRANCH: `oanhpham-kobe/TASK-S06-002-user-rbac-identity`
- PRIOR_R2_REVIEWED_SHA: `{prior}`
- PRIOR_R2_VERDICT: `BLOCKING_REPAIR`
- SOURCE_REOPEN_REQUIRED: `false`
- EXACT_R3_SHA: `{candidate}`
- CANDIDATE_CONTAINED_GATE: `project_control/reviews/S06_002_IMPLEMENTATION_R3_GATE_v1.md`

## R2 blocker reconciliation required

1. Unit/User/Application lock graph: unchanged `app_users.unit_id` history capture must not introduce the prior User→Unit edge; true Unit changes preserve S06-001 durable history and active-master validation while public bulk/lifecycle/HR-role races terminate without deadlock.
2. Interview operationalization: current participant and actor FK User rows must be acquired before Internal User advisory locks and participants revalidated; schedule/uncancel races must remain deadlock-free.
3. Dormant add/re-add: new selection/restoration must use User-row → advisory → post-lock active revalidation even when the Interview is dormant, while historical remove/reorder maintenance remains allowed.
4. First Google bind: trusted Google/confirmed-email evidence must be repeated after normalized-email advisory + target User row + Internal User advisory locks and must equal the original normalized advisory-key email.

## Producer verification evidence

- Repair worker run `{worker_run}`: PASS — append-only R3 migration generation, zero-state replay, focused Internal User/RBAC/Identity regressions, R1/R2/R3 lifecycle concurrency, crossed Application/Interview regressions, DB lint, non-force task-branch push.
- Exact-SHA verifier run `{verify_run}`: PASS on `{candidate}`.
  - static: PASS;
  - web: npm ci, audit, design check, lint, typecheck, build, Chromium install, full tests PASS;
  - database: zero-state replay, focused Internal User/RBAC/Identity, R1/R2/R3 concurrency, fresh replay, crossed Application/Interview/copy/bulk, retained S06-001 seed/history/durable-history, `supabase db lint --local --level error` PASS.
- R3 delta from `{prior}` is one commit and is limited to one append-only migration plus R3 regression/review artifacts; accepted migrations were not rewritten.

## Review boundary

Review exact immutable SHA `{candidate}` only. Producer CI is context, not acceptance. Reviewer is read-only and must not modify implementation, refs, integration, `main`, PRs, Vercel, connected Supabase, or later Slice-06 state.

A PASS permits governed product serialization into the integration branch followed by exact integration CI and final integration-equivalence review. Any blocker returns TASK-S06-002 to repair; canonical source reopening remains false unless the reviewer explicitly identifies a source contradiction.
''', encoding="utf-8")

handoff_path.write_text(f'''# TASK-S06-002 — Independent Implementation Review R3 Handoff

Copy-ready independent review request for `eiu-reviewer`.

## Review identity

- WORK_ID: `S06-002-IMPLEMENTATION-REVIEW-001-R3`
- REPOSITORY: `oanhpham-kobe/eiu-recruitment`
- TASK_BRANCH: `oanhpham-kobe/TASK-S06-002-user-rbac-identity`
- EXACT_REVIEW_SHA: `{candidate}`
- PRIOR_BLOCKED_SHA: `{prior}`
- PRIOR_VERDICT: `BLOCKING_REPAIR`
- SOURCE_REOPEN_EXPECTATION: `false`
- REVIEW_GATE: `project_control/reviews/S06_002_IMPLEMENTATION_R3_GATE_73f03e0_v1.md`
- CANDIDATE_CONTAINED_GATE: `project_control/reviews/S06_002_IMPLEMENTATION_R3_GATE_v1.md`

## Reviewer instruction

Check out or inspect **exact SHA `{candidate}`**. Confirm HEAD equality before review. Treat worker run `{worker_run}` and exact verifier `{verify_run}` only as producer evidence; do not infer acceptance from CI.

Re-review the four R2 blockers end-to-end:

1. Unit/User/Application durable-history lock graph and public bulk assignment versus lifecycle/HR-role administration.
2. Interview operationalization ordering for actor/current-participant User rows versus Internal User advisories, including schedule/uncancel races.
3. Dormant/CANCELLED/unscheduled new participant add/re-add restoration versus deactivation while retaining allowed historical maintenance.
4. First Google bind trusted Auth evidence freshness after the full lock set and equality with the original normalized email key.

Also verify no regression in: safe directory read surface, granular permission privacy, HR default/granular permission semantics, Root-only non-root identity change, no auto-rebind, optimistic versioning/idempotency/audit contracts, accepted S06-001 durable history, Application owner eligibility, canonical resource-blocking participation semantics, and stable server-side error mapping.

## Required verdict

Return:

- `WORK_ID: S06-002-IMPLEMENTATION-REVIEW-001-R3`
- `REVIEWED_SHA: {candidate}`
- `VERDICT: PASS | BLOCKING_REPAIR`
- `SOURCE_REOPEN_REQUIRED: true | false`
- blocking findings, if any, ordered highest risk first;
- evidence persistence coordinates if the reviewer can persist them, otherwise explicitly `UNAVAILABLE`.

Do not write product code, mutate refs, integrate the candidate, push/merge `main`, create/merge a PR, deploy Vercel, or apply connected Supabase migrations.
''', encoding="utf-8")

# TASK_REGISTRY: TASK-S06-002 is the final registry entry at this control baseline.
task_path = Path("project_control/TASK_REGISTRY.yaml")
task_text = task_path.read_text(encoding="utf-8")
marker = "  TASK-S06-002:\n"
if marker not in task_text:
    raise SystemExit("TASK-S06-002 marker missing")
prefix = task_text.split(marker, 1)[0]
new_task = f'''  TASK-S06-002:
    title: "Internal User Directory, HR RBAC & Identity Lifecycle Trusted Contracts"
    slice: SLICE-06
    status: REVIEW
    lane: LANE_A
    depends_on:
      - TASK-S06-001
    prompt: project_control/prompts/SLICE-06_TASK-002_v1.md
    prompt_review_status: "PASS (S06-002-PROMPT-REVIEW-001 @ f757e76f3f97077c608dab29bad45b8bd2126dc3; VERIFIED_FROM_OWNER_TRANSPORT)"
    prompt_review_target_sha: "f757e76f3f97077c608dab29bad45b8bd2126dc3"
    prompt_review_source_reopen_required: false
    prompt_review_evidence: project_control/reviews/S06_002_PROMPT_REVIEW_OWNER_TRANSPORT_f757e76_v1.md
    implementation_baseline_sha: "0a2ccdfedc477f9766c9aaa03739d16a7ed83c01"
    implementation_checkpoint: checkpoint/pre-S06-002-001
    implementation_branch: oanhpham-kobe/TASK-S06-002-user-rbac-identity
    prior_implementation_candidate_sha: "{prior}"
    implementation_candidate_sha: "{candidate}"
    repair_round: R3
    review_status: "WAITING_INDEPENDENT_REVIEW (S06-002-IMPLEMENTATION-REVIEW-001-R3 @ {candidate}); R2 was BLOCKING_REPAIR with SOURCE_REOPEN_REQUIRED=false"
    prior_review_evidence: project_control/reviews/S06_002_IMPLEMENTATION_REVIEW_OWNER_TRANSPORT_7c37d46_v2.md
    review_evidence: PENDING
    review_gate: project_control/reviews/S06_002_IMPLEMENTATION_R3_GATE_73f03e0_v1.md
    review_handoff: project_control/reviews/S06_002_IMPLEMENTATION_R3_HANDOFF_73f03e0_v1.md
    producer_verification: "PASS (worker run {worker_run}; exact verifier run {verify_run}; static/full web/two zero-state DB replays/focused R1-R3 concurrency/crossed Application-Interview/S06-001 history/db lint PASS; exact SHA {candidate})"
    notes: "R3 repairs the four independent R2 blockers without canonical source reopen: complete Unit/User/Application lock graph; Interview participant/actor row-before-advisory ordering; dormant add/re-add post-lock active revalidation; and first-bind post-lock trusted Auth evidence freshness. Candidate is producer-verified only and must not enter governed product integration before independent exact-SHA R3 PASS. Dangling historical R2 gate/handoff pointers were not fabricated; the verified R2 Owner-transport evidence remains the historical source of truth. No Users/Permissions UI, main mutation, PR, deployment, or connected Supabase migration application occurred."
'''
task_path.write_text(prefix + new_task, encoding="utf-8")

# AUTONOMY_RUN_STATE: replace the active R3 repair tail with immutable review-wait state.
run_path = Path("project_control/AUTONOMY_RUN_STATE.yaml")
run_text = run_path.read_text(encoding="utf-8")
start = run_text.find("s06_002_planning:\n")
if start < 0:
    raise SystemExit("s06_002_planning marker missing")
new_tail = f'''s06_002_planning:
  status: WAITING_INDEPENDENT_REVIEW
  task: TASK-S06-002
  title: "Internal User Directory, HR RBAC & Identity Lifecycle Trusted Contracts"
  prompt: project_control/prompts/SLICE-06_TASK-002_v1.md
  prompt_review_target_sha: "f757e76f3f97077c608dab29bad45b8bd2126dc3"
  prompt_review:
    work_id: S06-002-PROMPT-REVIEW-001
    reviewer: eiu-reviewer
    review_type: PROMPT_SOURCE_RECONCILIATION
    result: PASS
    source_reopen_required: false
    blocking_findings: NONE
    handoff: project_control/reviews/S06_002_PROMPT_REVIEW_GATE_v1.md
    evidence_persistence: VERIFIED_FROM_OWNER_TRANSPORT
    evidence_path: project_control/reviews/S06_002_PROMPT_REVIEW_OWNER_TRANSPORT_f757e76_v1.md
  source_reopen_expectation: false
  accepted_prerequisites:
    - "TASK-S06-001 accepted @ 59be9b2c92906065b8e4baa902fcec1d4cbefa12"
    - "accepted Slice-01 identity/auth schema and Internal first-login provisioning"
    - "accepted Application owner and Interview participant/resource lifecycle contracts"
  implementation_hold: "HELD PENDING R3 INDEPENDENT REVIEW — exact candidate {candidate} is producer-verified but not accepted or product-integrated."
  implementation_candidate:
    branch: oanhpham-kobe/TASK-S06-002-user-rbac-identity
    baseline_sha: "0a2ccdfedc477f9766c9aaa03739d16a7ed83c01"
    prior_candidate_sha: "{prior}"
    candidate_sha: "{candidate}"
    source_reopen_required: false
    repair_round: R3
    producer_verification:
      worker_run: "{worker_run} PASS"
      exact_verifier_run: "{verify_run} PASS"
      exact_verified_sha: "{candidate}"
      static: "PASS — exact SHA, one-commit R3 delta, append-only migration, review artifacts, diff hygiene, accepted migrations not rewritten"
      web: "PASS — npm ci, npm audit --audit-level=high, design:check, lint, typecheck, build, Chromium install, full npm run test"
      database: "PASS — two zero-state replays, focused Internal User/RBAC/Identity, R1/R2/R3 lifecycle concurrency, crossed Application/Interview/copy/bulk, retained S06-001 seed/history/durable-history, db lint --level error, clean stop"
    review_package: project_control/reviews/S06_002_IMPLEMENTATION_R3_GATE_73f03e0_v1.md
    coordinator_handoff: project_control/reviews/S06_002_IMPLEMENTATION_R3_HANDOFF_73f03e0_v1.md
  prior_independent_implementation_review:
    work_id: S06-002-IMPLEMENTATION-REVIEW-001-R2
    reviewer: eiu-reviewer
    status: VERIFIED_FROM_OWNER_TRANSPORT
    reviewed_sha: "{prior}"
    result: BLOCKING_REPAIR
    source_reopen_required: false
    evidence_persistence: UNAVAILABLE
    evidence_path: project_control/reviews/S06_002_IMPLEMENTATION_REVIEW_OWNER_TRANSPORT_7c37d46_v2.md
  independent_implementation_review:
    work_id: S06-002-IMPLEMENTATION-REVIEW-001-R3
    reviewer: eiu-reviewer
    status: PENDING
    reviewed_sha: "{candidate}"
    result: PENDING
    source_reopen_required: false
    review_gate: project_control/reviews/S06_002_IMPLEMENTATION_R3_GATE_73f03e0_v1.md
    coordinator_handoff: project_control/reviews/S06_002_IMPLEMENTATION_R3_HANDOFF_73f03e0_v1.md
    acceptance_rule: "No product serialization into integration until an independent exact-SHA R3 PASS is returned and truthfully persisted."
  r3_repair_closure:
    - "Unit/User/Application durable-history lock graph repaired with staged non-null Unit public races."
    - "Interview operationalization repaired to row-before-advisory ordering with current participant revalidation and schedule/uncancel concurrency coverage."
    - "Dormant add/re-add restoration now serializes and post-lock revalidates active eligibility while permitted historical maintenance remains intact."
    - "First Google bind repeats verified Google/confirmed-email proof after the full lock set and fails closed on evidence drift."

implementation_materialization:
  task: TASK-S06-002
  prompt_review: "PASS S06-002-PROMPT-REVIEW-001 @ f757e76f3f97077c608dab29bad45b8bd2126dc3"
  prompt_review_provenance: VERIFIED_FROM_OWNER_TRANSPORT
  source_reopen_required: false
  prompt: project_control/prompts/SLICE-06_TASK-002_v1.md
  checkpoint: checkpoint/pre-S06-002-001
  branch: oanhpham-kobe/TASK-S06-002-user-rbac-identity
  baseline_sha: "0a2ccdfedc477f9766c9aaa03739d16a7ed83c01"
  status: WAITING_INDEPENDENT_REVIEW
  prior_candidate_sha: "{prior}"
  current_candidate_sha: "{candidate}"
  exact_verifier_run: "{verify_run} PASS"
  review_round: R3

safe_frontier:
  eligible_tasks: []
  skipped_due_to_dependency: []
  materialization_frontier: []
  execution_hold: "TASK-S06-002 R3 candidate {candidate} passed exact producer verification run {verify_run}; later Slice-06 work remains held pending independent exact-SHA R3 review."

stop_gate:
  status: WAITING_EXTERNAL_REVIEW
  type: INDEPENDENT_IMPLEMENTATION_REVIEW
  work_id: S06-002-IMPLEMENTATION-REVIEW-001-R3
  target: "{candidate}"
  reviewer: eiu-reviewer
  source_reopen_required: false
  resume_on: "Independent exact-SHA R3 verdict for {candidate}. PASS may advance to governed product serialization; any blocker returns to repair without source reopen unless reviewer explicitly requires it."

next_action: "Obtain independent implementation re-review S06-002-IMPLEMENTATION-REVIEW-001-R3 on exact task-branch SHA {candidate} using project_control/reviews/S06_002_IMPLEMENTATION_R3_HANDOFF_73f03e0_v1.md. Do not serialize product into integration before PASS; do not push/merge main, create/merge a PR, deploy Vercel, or apply connected Supabase migrations."
'''
run_path.write_text(run_text[:start] + new_tail, encoding="utf-8")

Path("project_control/CURRENT_STATE.md").write_text(f'''# Current Implementation State — Derived Handoff Snapshot

> **DERIVED / NON-AUTHORITATIVE REPORTING ONLY**
> Runtime authority: `project_control/AUTONOMY_RUN_STATE.yaml`.
> DAG/task/slice authority: `project_control/TASK_REGISTRY.yaml` and `project_control/SLICE_REGISTRY.yaml`.
> Exact code/history authority: Git.

## SLICE-06 / TASK-S06-001 — ACCEPTED

TASK-S06-001 remains accepted at `59be9b2c92906065b8e4baa902fcec1d4cbefa12` / `checkpoint/S06-001-accepted-001`.

## SLICE-06 / TASK-S06-002 — WAITING INDEPENDENT R3 REVIEW

- Exact R3 candidate: `{candidate}` on `oanhpham-kobe/TASK-S06-002-user-rbac-identity`.
- Prior R2 target `{prior}` was **BLOCKING_REPAIR** with `SOURCE_REOPEN_REQUIRED=false`; verified historical evidence remains `project_control/reviews/S06_002_IMPLEMENTATION_REVIEW_OWNER_TRANSPORT_7c37d46_v2.md`.
- R3 repair worker `{worker_run}`: **PASS**.
- Exact-SHA verifier `{verify_run}`: **PASS** — static, full web, two zero-state DB replays, focused Internal User/RBAC/Identity, R1/R2/R3 concurrency, crossed Application/Interview/copy/bulk, retained S06-001 history regressions, and DB lint.
- R3 review gate: `project_control/reviews/S06_002_IMPLEMENTATION_R3_GATE_73f03e0_v1.md`.
- R3 reviewer handoff: `project_control/reviews/S06_002_IMPLEMENTATION_R3_HANDOFF_73f03e0_v1.md`.
- Task registry status: `REVIEW`; review round: `R3`.
- Product candidate has **not** been serialized into integration and is not accepted until independent exact-SHA R3 PASS.

## Next action

Obtain independent review `S06-002-IMPLEMENTATION-REVIEW-001-R3` on exact SHA `{candidate}`. A PASS may advance to governed product serialization, exact integration CI, and final integration-equivalence review; any blocker returns to repair.

## Boundaries

- Do not push/merge `main` without explicit Owner authorization.
- Do not create/merge a PR in this phase.
- Do not deploy Vercel without explicit Owner authorization.
- Do not apply migrations to connected Supabase without explicit Owner authorization.
''', encoding="utf-8")
