# EIU Recruitment — Continuous Autonomy & Parallel Execution Governance
## Document Version: 2.0 (PROPOSED / INACTIVE / PENDING OWNER REVIEW)
## Status: DRAFT_PENDING_OWNER_REVIEW (DO NOT ACTIVATE BEFORE OWNER SIGNOFF)

---

## 1. Governance Topology & Authority Boundaries (ONE_FACT_ONE_AUTHORITY)

Every project fact has exactly one canonical storage authority. Secondary files may reference, summarize, or derive views, but cannot maintain competing runtime copies:

1. **Product / Business Authority (`recruitment_webapp/`):**
   Sole authority for business logic, permissions, domain models, invariants, acceptance criteria, and Design System v1.8. Governance never alters these.
2. **Global Router & Invariants (`AGENTS.md` & `.omp/RULES.md`):**
   Portable router defining role split, security invariants, skill routing, and pointers to autonomy policies. Does not duplicate detailed scheduling logic.
3. **Autonomy & Scheduling Authority (`project_control/AUTONOMY_PARALLEL_GOVERNANCE.md`):**
   Sole authority for auto-advance, worker lifecycle, dual-lane scheduler, parallel eligibility, task isolation, and serial integration. No second scheduler policy file may exist.
4. **Live Runtime State Authority (`project_control/AUTONOMY_RUN_STATE.yaml`):**
   Sole live authority for run status, activation flags, active workers, bounded settled worker history, execution hold, frontier, stop gate, and verified CI checkpoints.
5. **DAG Structure & Task State (`project_control/TASK_REGISTRY.yaml` & `SLICE_REGISTRY.yaml`):**
   Authority for task dependencies, DAG definitions, slice completion, and materialized task status (`PLANNED`, `READY`, `IN_PROGRESS`, `REVIEW`, `DONE`, `BLOCKED`, `SUPERSEDED`, `CANCELLED`). Does not own live workers or active lanes.
6. **Evidence Index (`project_control/EVIDENCE_INDEX.yaml`):**
   Immutable index of compact verification receipts (exact SHA, test/review/CI links, policy gates). Does not duplicate full narrative or live state.
7. **Derived Reporting Surfaces (`project_control/CURRENT_STATE.md` & `TRACEABILITY_STATUS.csv`):**
   Strictly derived and non-authoritative reporting snapshots. Never used for scheduling, dispatch, or authorization.
8. **Active Gap Register (`project_control/OPEN_GAPS.md`):**
   Register for active unresolved gaps only. Historical resolutions are collapsed into references.

### Governance Extension Rule (Growth Control)
Before creating any new control-plane or governance document:
1. Verify if the concern belongs to an existing authority listed above. If so, update that existing file.
2. Create a new governance file only if it represents a fundamentally new authority domain and existing files would become incoherent if overloaded.
3. A newly observed failure mode must result in repairing existing policies, updating the dynamic validator, or adding a regression test—never creating another policy layer.

---

## 2. Activation Hold & Governance Overrides

Until explicit owner authorization activates this policy:

```yaml
governance_consolidation:
  status: READY_FOR_OWNER_REVIEW

autonomy_policy_activation:
  policy_path: project_control/AUTONOMY_PARALLEL_GOVERNANCE.md
  auto_advance: PENDING_OWNER_REVIEW
  parallel_scheduler: PENDING_OWNER_REVIEW
  max_active_implementation_tasks: 1

slice_04_execution:
  status: HELD_FOR_GOVERNANCE_REVIEW
  rule: "Frontier includes TASK-S04-001 for planning visibility only. Execution, worktree creation, prompt authoring, and executor launch are explicitly HELD until owner reviews governance."
```

- **Activation Override:** This activation hold overrides any auto-advance or continuous execution instruction.
- **Frontier Independence:** Frontier visibility of `TASK-S04-001` does **not** authorize starting it, creating worktrees, authoring prompts, or launching executors during this maintenance cycle.

---

## 3. Auto-Advance Policy (Future Rule — Currently Inactive)

### 3.1 Auto-Advance Invariant
When explicitly enabled by the owner:
```text
IF:
  run.status == ACTIVE
  AND stop_gate == null
  AND safe_frontier.eligible_tasks is non-empty
  AND autonomy_policy_activation.auto_advance == ENABLED

THEN:
  Coordinator MUST advance to the earliest eligible task on the safe frontier.
```
- Computing, persisting, or reporting the frontier does **not** satisfy auto-advance. Auto-advance requires active progression through formal lifecycle stages.

### 3.2 Observable Task Lifecycle Stages
1. `FRONTIER_AVAILABLE`: Task dependencies are satisfied; task is recognized on the computed safe frontier.
2. `TASK_MATERIALIZED`: Task contract derived from canonical sources; prompt authored.
3. `PROMPT_REVIEWING`: Independent prompt review is running.
4. `TASK_READY`: Prompt passed independent review with zero blockers.
5. `TASK_STARTED`: Dedicated task branch and isolated worktree created.
6. `EXECUTOR_RUNNING`: Writing executor is implementing approved scope.
7. `IMPLEMENTATION_REVIEWING`: Pre-review gate passed; independent reviewer evaluating exact task SHA.
8. `TASK_ACCEPTED`: Independent review passed; task commit verified.
9. `TASK_INTEGRATED`: Task commit merged into authorized integration branch.
10. `CI_VERIFIED`: Exact merge SHA pushed and verified on GitHub Actions CI.

*Rule:* Never state "continuing autonomously" when only `FRONTIER_AVAILABLE` is true.

### 3.3 Informational Boundaries vs True Stop Conditions
Once auto-advance is activated, normal lifecycle completions are **informational only** and do not pause execution:
- Task completed or executor settled normally.
- Prompt passed independent review.
- Implementation passed independent review.
- Integration merge completed.
- Exact-SHA GitHub Actions CI passed.
- Slice completed.
- Safe frontier recomputed.

**True Stop Conditions Only:**
The coordinator must STOP and seek owner instructions only when:
1. A genuine owner/business/product/UX decision is required.
2. Current authorization boundary is reached (e.g. review cap exhausted without scoped exception).
3. A production, main-branch, or destructive external operation would be required.
4. Safe dependency frontier is genuinely empty or blocked with no eligible tasks.
5. A safety, security, privacy, or authorization invariant cannot be preserved.
6. Canonical project sources materially conflict and cannot be safely reconciled under canonical precedence.
7. Continuing requires architecture, data-model, or scope alterations outside current authority.

---

## 4. Active Worker & Lane Ownership Model

`active_workers` in `project_control/AUTONOMY_RUN_STATE.yaml` is the sole
runtime worker and concurrency authority.

Worker records use the existing runtime shape:

```yaml
active_workers:
  - task_id: string
    lane: "LANE_A" | "LANE_B"
    role: "EXECUTOR" | "REVIEWER"
    branch: string
    worktree: string
    exact_sha: string | null
    state: "STARTING" | "RUNNING" | "WAITING" | "REVIEWING" | "SETTLED" | "BLOCKED"
    started_at: string
    last_observed_at: string

worker_settled_history:
  - task_id: string
    lane: "LANE_A" | "LANE_B"
    role: "EXECUTOR" | "REVIEWER"
    result: "COMPLETED" | "PASS" | "FAIL" | "CANCELLED"
    exact_sha: string
    settled_at: string
```

### Worker invariants

- Exactly one writing Executor may own one implementation task/worktree.
- Two Executors must never write the same worktree.
- A task must never have duplicate active writing Executors.
- Reviewers are read-only and independent.
- Worker process settlement is informational and does not itself release the
  task's implementation lane.
- `worker_settled_history` retains at most the latest 10 settled worker
  operations.
- Permanent task completion evidence belongs in
  `project_control/EVIDENCE_INDEX.yaml`.

### Lane ownership invariant

An implementation lane belongs to the TASK LIFECYCLE, not to the Executor
process.

A task occupies its implementation lane from:

TASK_STARTED

until:

CI_VERIFIED

for that task's accepted integration checkpoint.

Therefore:

- EXECUTOR SETTLED does NOT release the lane.
- IMPLEMENTATION REVIEW PASS does NOT release the lane.
- TASK_ACCEPTED does NOT release the lane.
- TASK_INTEGRATED does NOT release the lane.
- Only CI_VERIFIED releases the lane on the normal successful path.

If a task is explicitly CANCELLED or SUPERSEDED before integration, the
Coordinator must first persist that terminal task state and confirm there is
no pending integration or reconciliation work before reusing the lane.

`active_task`, `current_task`, and `current_slice`, if retained elsewhere,
are compatibility or human-summary pointers only.

They are never concurrency authority.

They must never overwrite, replace, or hide `active_workers`.

### Lane reservation persistence

The Executor entry in `active_workers` also acts as the durable lane-reservation
record for a started implementation task.

At `TASK_STARTED`, the Coordinator MUST create exactly one Executor entry for
the task and assigned lane with:

state: STARTING

When the Executor process begins implementation, transition that same entry to:

state: RUNNING

If the Executor process finishes or settles before the task reaches
`CI_VERIFIED`, DO NOT remove the Executor entry from `active_workers`.

Instead, retain the same task/lane entry and transition it to:

state: SETTLED

The `SETTLED` state means the writing process has stopped, but the task still
owns the implementation lane.

`worker_settled_history` may record the process-settlement event, but it does
not replace or release the corresponding lane-reservation entry.

During implementation review, reconciliation, integration, or CI waiting, the
task's Executor lane-reservation entry remains present in `active_workers`,
even when no writing Executor process is currently running.

Only after the task reaches:

CI_VERIFIED

may the Coordinator remove that task's Executor lane-reservation entry from
`active_workers`.

Removal of that entry is the normal successful lane-release event.

Therefore, concurrency capacity MUST be calculated from Executor entries in
`active_workers`, including entries whose state is `SETTLED`.

This rule intentionally avoids introducing a separate lane registry,
pending-integration registry, or additional runtime-state authority.

---

## 5. Dual-Lane Scheduler — Simple Conservative Model

Runtime capacity is controlled only by:

autonomy_policy_activation.parallel_scheduler

and:

autonomy_policy_activation.max_active_implementation_tasks

Dual-lane scheduling is allowed only when:

autonomy_policy_activation.parallel_scheduler == ENABLED

AND

autonomy_policy_activation.max_active_implementation_tasks == 2

The Coordinator must never launch a second task merely to fill capacity.

No optimizer, scoring engine, predictive scheduler, or additional scheduling
state file is permitted.

### Initial dispatch

When no implementation task is active:

1. Select the earliest safe-frontier eligible Task A.
2. Task A may start in Lane A.
3. If another frontier-eligible Task B exists and capacity remains:
   - run the Parallel Eligibility Gate for A <-> B;
   - if the decision is PARALLEL_ALLOWED, start B in Lane B;
   - otherwise SERIALIZE.

For initial dual dispatch:

- Task A MUST be safe-frontier eligible.
- Task B MUST be safe-frontier eligible.

### Lane refill

If one task remains active and the other lane becomes free after CI_VERIFIED:

1. recompute the safe frontier;
2. select candidate Task B from the current frontier;
3. compare candidate B against the still-active Task A;
4. run the Parallel Eligibility Gate;
5. launch B only when the decision is PARALLEL_ALLOWED.

For lane refill:

- active Task A does NOT need to remain in `safe_frontier`;
- candidate Task B MUST be safe-frontier eligible.

Worker settlement, review completion, TASK_ACCEPTED, or TASK_INTEGRATED alone
must never trigger lane refill.

---

## 6. Parallel Eligibility Gate

The Coordinator uses one compact parallel-admission gate.

The gate evaluates exactly these surfaces:

1. dependency / DAG relationship;
2. graph-assisted impact relationship;
3. direct write-surface overlap;
4. shared API / type / security / global contracts;
5. database / migration overlap.

### Initial-dispatch precondition

For initial A + B dispatch:

A is safe-frontier eligible

AND

B is safe-frontier eligible

### Lane-refill precondition

For refill while A is already active:

A is an active implementation task

AND

B is safe-frontier eligible

Active Task A does NOT need to remain listed in `safe_frontier`.

### Evidence receipt

Persist one compact immutable receipt in
`project_control/EVIDENCE_INDEX.yaml` using this shape:

```yaml
PARALLEL_ELIGIBILITY:
  task_a: TASK-A-ID
  task_b: TASK-B-ID
  mode: INITIAL_DISPATCH | LANE_REFILL
  analyzed_integration_head: <commit-sha>

  dependency_check:
    direct_dependency: NONE | <details>
    transitive_dependency: NONE | <details>
    result: PASS | FAIL

  graph_check:
    crg_used: YES | NO
    gitnexus_used: YES | NO
    graph_freshness: VERIFIED | UNAVAILABLE
    analyzed_head: <commit-sha>
    shared_symbols: NONE | <details>
    caller_callee_dependency: NONE | <details>
    blast_radius_overlap: NONE | <details>
    result: PASS | FAIL

  write_surface:
    overlapping_primary_files: NONE | <details>
    overlapping_modules: NONE | <details>
    result: PASS | FAIL

  shared_contracts:
    api_type_contract_dependency: NONE | <details>
    auth_security_core_overlap: NONE | <details>
    global_config_overlap: NONE | <details>
    result: PASS | FAIL

  database_surface:
    structural_migration_a: YES | NO
    structural_migration_b: YES | NO
    migration_order_dependency: NONE | <details>
    shared_tables: NONE | <details>
    shared_functions: NONE | <details>
    shared_rls_grants: NONE | <details>
    result: PASS | FAIL

  decision: PARALLEL_ALLOWED | SERIALIZE
```

If any material uncertainty remains:

SERIALIZE.

Mandatory serialization applies when ANY of the following is true:

1. A direct dependency exists.
2. A transitive dependency exists.
3. One task produces an API, RPC, schema, type, or contract consumed by the
   other.
4. Primary implementation files overlap materially.
5. Shared core modules overlap materially.
6. Both tasks modify auth/security core.
7. Both tasks materially modify shared global configuration.
8. Both tasks modify package dependencies or lockfiles in interacting ways.
9. Both tasks modify the same global design/application shell infrastructure.
10. Both tasks modify the same database table, SQL function, trigger, RLS
    policy, grant, or locking contract.
11. Migration execution order may interact.
12. Correctness of one task relies on an unresolved finding or assumption in
    the other.

If BOTH tasks introduce structural database migrations:

SERIALIZE

by default.

An exception requires exceptionally clear proof of independence across
separate domains.

---

## 7. Graph Routing for Parallel Admission

Graph analysis supports the parallel-admission decision but never replaces
direct source authority.

### CRG

When CRG is callable, use CRG as the default BROAD graph check for a proposed
parallel pair.

Use CRG to inspect:

- shared modules;
- changed-area overlap;
- broad dependency coupling;
- possible write-surface interaction;
- possible blast-radius interaction.

Before using CRG evidence:

- verify freshness against the current integration code HEAD;
- refresh only if actually required;
- persist analyzed HEAD;
- persist freshness evidence.

Do not refresh CRG ceremonially.

### GitNexus

GitNexus is NOT mechanically required for every proposed parallel pair.

Use GitNexus only when one or more of the following applies:

- CRG indicates possible shared-symbol coupling;
- direct source leaves dependency direction unclear;
- caller/callee relationships are material to the decision;
- shared or high-impact symbols are involved;
- precise blast-radius confirmation is required.

### Direct source

Direct source remains final authority.

For database work:

- ordered migrations;
- SQL definitions;
- schema contracts;
- RLS/grants;
- locking rules;
- database tests

outrank graph representations.

### Graph unavailability

If graph tooling is unavailable:

- perform DAG inspection;
- perform direct-source inspection;
- inspect write surfaces;
- inspect shared contracts;
- inspect database surfaces where applicable.

Allow PARALLEL_ALLOWED only when independence is exceptionally clear.

Otherwise:

SERIALIZE.

Never fabricate graph use.

---

## 8. Worktree & Worker Isolation Policy

In dual-lane mode:
```text
Lane A: Task A  ->  Branch A  ->  Worktree A  ->  Executor A
Lane B: Task B  ->  Branch B  ->  Worktree B  ->  Executor B
```
- No cross-worktree writes: Executor A never writes in Worktree B; Executor B never writes in Worktree A.
- No shared commits or co-mingled task branches.
- No cross-task repair hiding: Defects in Task A must be repaired solely on Branch A and amended into Task A's commit.
- Each task maintains its own independent prompt, branch, worktree, implementation commit, pre-review gate, evidence entry, and independent review.

---

## 9. Serial Integration & Exact-SHA Reconciliation Policy

While implementation and review may run concurrently across lanes, **integration into the integration branch MUST remain strictly serialized** under a single coordinator writer:

```text
Task A passes Review
  ↓
Integrate Task A into integration branch
  ↓
Push integration branch checkpoint
  ↓
Verify exact-SHA GitHub Actions CI passes
  ↓
Before integrating Task B:
  Compare Task B to NEW integration HEAD without mutating Task B.
  ↓
Case 1: If reviewed Task B SHA and content remain unchanged and fully compatible:
  Integrate Task B -> Push -> Verify exact-SHA CI.
Case 2: If ANY change, rebase, cherry-pick, conflict repair, or reconciliation is required:
  Do NOT resolve substantive logic on integration branch!
  Reconcile inside Worktree B -> Amend Task B commit -> Rerun affected tests ->
  Obtain fresh independent review on exact amended SHA -> Integrate only after PASS.
```

*Rule:* Never inherit review approval across a changed commit SHA.

---

## 10. Lane Failure Isolation Policy

- A failure or review rejection in Lane A does **not** automatically halt Lane B, provided Lane B remains independent and uncoupled.
- Freeze Lane B only if Lane A's defect affects a shared contract, schema, security invariant, or assumption on which Lane B materially depends.

---

## 11. UI Pre-Review & Behavioral Verification Policy

Before releasing an independent reviewer for material interactive UI work:
- The executor must execute and persist a pre-review acceptance gate covering the applicable Design System v1.8 checklist, accessibility standards, and behavioral tests.
- **Verification Rule:** `SOURCE_PRESENCE != INTERACTION_PROOF`. Asserting that a handler function, state setter, ref, or DOM attribute exists in source code does **not** prove interaction.
- Rendered behavior claims (e.g. focus transitions, dialog traps, dropdown dismissals, reactive selection updates) require executed rendered assertions in a real browser engine (Playwright / Chromium).
- Static source assertions are permitted only for true static invariants (e.g. token definitions, CSS custom properties).
- Browser QA must be executed against runnable targets when authorized; otherwise, limitations must be recorded truthfully.

---

## 12. Technical Decision Principle for Planners & Reviewers

- When canonical project sources and the current implementation provide sufficient information to resolve a technical defect, planners, reviewers, and executors must make the **safest minimal canonical technical decision directly**.
- Do **not** defer internally resolvable technical choices to the project owner merely because multiple implementation options exist.
- Escalate to the owner **only** when an unresolved decision materially alters:
  1. Business behavior or invariants.
  2. Approved product/UX behavior.
  3. Authorization, authentication, or permission policy.
  4. Privacy, storage, or data retention policy.
  5. Architecture or data-model foundations not already canonical.
  6. Task scope or slice boundaries.
  7. Production, deployment, main-branch, or destructive actions.
