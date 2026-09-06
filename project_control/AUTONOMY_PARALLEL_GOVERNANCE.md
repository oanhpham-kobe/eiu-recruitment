# EIU Recruitment — Continuous Autonomy & Parallel Execution Governance
## Document Version: 2.2
## Status: MODED_EXECUTION_POLICY

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

## 2. Execution Mode and Runtime Authority

`AUTONOMOUS` and `BOUNDED` are the only execution modes. Task type is
independent of execution mode and never creates a third mode.

The current live execution mode, activation state, worker state, safe frontier,
stop gate, and every other current-run fact are read exclusively from
`project_control/AUTONOMY_RUN_STATE.yaml`. This policy defines semantics and
must not embed a competing current-run snapshot.

`execution_mode` in `AUTONOMY_RUN_STATE.yaml` is the live operational selector:

- `AUTONOMOUS` permits the continuous lifecycle in §3. It requires explicit
  activation of auto-advance and retains all scheduler, lane, review,
  serialized-integration, and exact-SHA CI safeguards.
- `BOUNDED` permits only the explicit Planner-authorized work set recorded in
  `bounded_execution`. It forces automatic continuation off. The Executor
  verifies, commits, reports, and stops at the authorized boundary.

Mode changes require explicit Planner/Owner authorization and a corresponding
runtime-state update. `AUTONOMOUS` may not be inferred from a task type,
frontier visibility, a prior CI pass, or an Executor settlement.

---

## 3. Execution Lifecycles

### 3.1 AUTONOMOUS

When all activation, safety, and capacity gates permit it, the Coordinator
continues without a Planner checkpoint at ordinary lifecycle boundaries:

```text
safe frontier / authorized task
→ Executor
→ focused verification
→ OMP independent implementation review
→ BLOCKING_REPAIR? bounded repair in the active task lane
→ targeted exact-SHA re-review
→ PASS
→ serialized integration
→ exact-SHA CI
→ CI_VERIFIED
→ POST-CI CONTINUATION GATE
→ next safe frontier
```

#### Task lifecycle completion is not AUTONOMOUS run completion

`CI_VERIFIED` means the task completed its normal successful lifecycle: its
lane may be released and truthful task acceptance/evidence may be persisted.
It does **not** mean the AUTONOMOUS run or Coordinator turn is complete, a
Planner checkpoint is required, a task summary terminates execution, or a
task-scoped todo list can terminate execution.

When `execution_mode == AUTONOMOUS`, `auto_advance == ENABLED`, and no genuine
canonical stop condition exists, the Coordinator MUST enter the outer
continuation cycle.

#### POST-CI CONTINUATION GATE

For every successful AUTONOMOUS task lifecycle, before voluntarily yielding:

```text
TASK CI_VERIFIED
→ release completed lane
→ persist truthful task/evidence state
→ open or append a CONTINUATION phase
→ recompute DAG and slice state
→ inspect active workers, lane capacity, and current integration HEAD
→ inspect OPEN_GAPS, current incomplete slice, and next incomplete slice
→ inspect canonical source for remaining source-backed work
→ materialize next task(s) when canonical source is sufficient
→ recompute safe frontier
→ apply dependency, security, database, and shared-contract constraints
→ run Parallel Eligibility Gate when a second candidate is relevant
→ dispatch next safe task(s)
→ continue AUTONOMOUS
```

The only alternative is to establish and persist a genuine canonical stop
condition.

#### Todo and report semantics

A finite task-scoped todo list is subordinate to the AUTONOMOUS run loop. If
`execution_mode == AUTONOMOUS`, `auto_advance == ENABLED`, and no canonical
`stop_gate` has been established:

```text
TASK_TODO_EMPTY
→ OPEN / APPEND CONTINUATION TODO
→ RESOLVE NEXT FRONTIER
```

It MUST NOT transition to a final summary and top-level return. The
Coordinator may create a new continuation phase rather than keeping one
unbounded todo list.

Task completion reports are informational. In active AUTONOMOUS execution,
ordinary reporting of exact SHAs, verification, review, integration, CI, lane
release, or the next frontier is not a stop event: `REPORT != STOP`.

#### FRONTIER RESOLUTION and true no-safe-frontier

`safe_frontier.eligible_tasks == []` alone is not `NO_SAFE_FRONTIER`. Before
classifying a true no-safe-frontier condition, the Coordinator MUST:

1. recompute `TASK_REGISTRY` dependencies;
2. inspect active workers;
3. inspect tasks in review, integration, or CI lifecycle;
4. inspect the current incomplete `SLICE_REGISTRY` entry;
5. inspect the next incomplete `SLICE_REGISTRY` entry;
6. inspect canonical source for remaining source-backed work;
7. determine whether work exists but remains unmaterialized;
8. materialize that work when canonical source authority is sufficient;
9. recompute dependencies and the safe frontier;
10. inspect `OPEN_GAPS`;
11. inspect Owner-decision requirements and infrastructure blockers; and
12. inspect security, privacy, and data-integrity blockers.

Source-backed work that can be materialized MUST be materialized and the
frontier recomputed. An incomplete dependency is a truthful dependency block,
not a terminal no-safe-frontier decision; other safe work may continue.
`NO_SAFE_FRONTIER` is valid only when all authorized/source-backed work is
genuinely exhausted and no active, pending-review, pending-integration, or
pending-CI lifecycle remains.

Therefore:

```text
TEMPORARILY_EMPTY_MATERIALIZED_FRONTIER
!=
PROVEN_NO_SAFE_FRONTIER
```

#### Outer loop and yield rule

Conceptually, while AUTONOMOUS is active:

```text
resolve current integration truth
resolve/materialize frontier

if genuine canonical stop condition:
    persist stop reason and evidence
    yield

dispatch safe work subject to scheduler capacity
→ Executor
→ focused verification
→ independent implementation review
→ blocking repair and targeted exact-SHA re-review when required
→ PASS
→ serialized integration
→ exact-SHA CI
→ CI_VERIFIED
release lane only at CI_VERIFIED
execute POST-CI CONTINUATION GATE
continue
```

The Coordinator MUST NOT voluntarily top-level return solely because an
Executor settled, review passed, a task became accepted or integrated,
`CI_VERIFIED` occurred, a task todo became empty, a task summary was emitted,
or the materialized frontier is temporarily empty before FRONTIER RESOLUTION.

A top-level yield is valid only after a genuine canonical stop condition is
persisted, or while an external operation is genuinely awaiting completion and
the runtime cannot continue synchronously. In the latter case, persist a
truthful waiting state where applicable; do not misclassify it as completion.

The first implementation review covers the full task delta, task acceptance
criteria, relevant invariants, and directly affected dependency, security,
privacy, and data-integrity surfaces. After a repair, the fresh exact-SHA
re-review covers every unresolved `BLOCKING_REPAIR` finding, the repair delta,
directly affected invariants/dependencies, and concrete repair regressions.
Previously passed areas remain closed unless changed code, a materially changed
dependency, a crossed shared invariant, or concrete regression evidence
justifies reopening them.

AUTONOMOUS stops only for:
1. `OWNER_DECISION_REQUIRED`;
2. a business, architecture, or source-contract reopening;
3. a security, safety, authorization, privacy, or data-integrity ambiguity
   that current authority cannot resolve;
4. a production, main-branch, destructive, or other authorization boundary;
5. repair exhaustion;
6. an unrecoverable infrastructure blocker; or
7. proven true `NO_SAFE_FRONTIER` after FRONTIER RESOLUTION.

### 3.2 BOUNDED

```text
Planner-authorized work set
→ Executor completes that work set
→ focused verification
→ commit
→ report exact SHA and evidence
→ HARD STOP
```

BOUNDED has no internal OMP implementation reviewer or repair/re-review chain.
Integration or CI is allowed only when the bounded Planner prompt explicitly
includes that action; a next-frontier task is never inferred or dispatched.
The Executor may correct implementation-local verification failures caused by
the authorized work and reports unrelated discoveries without adding them to
the work set.

`bounded_execution` records the finite work-set identity, authorized task
identifiers where represented, authorized paths, and continuation permissions.
This is the existing runtime-state authority, not a second registry.

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

### Mode-specific reviewer bookkeeping

In `AUTONOMOUS`, an active implementation review uses the existing
`active_workers` record with `role: REVIEWER` and a 40-character exact SHA.
The optional `active_task.review` record carries either `INITIAL` or
`INCREMENTAL_REPAIR` scope. Incremental scope records unresolved blocking
finding identifiers, repair-delta paths, affected invariants/dependencies, and
any reopened area with its concrete reopening evidence.

`BOUNDED` has neither an active `REVIEWER` worker nor `active_task.review`.
Its external Planner/Reviewer inspection happens after the Executor's bounded
commit and is not an internal scheduled lifecycle stage.


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
- An `AUTONOMOUS` task maintains its independent prompt, branch, worktree,
  implementation commit, pre-review gate, evidence entry, and internal
  exact-SHA review. A `BOUNDED` task maintains its authorized work set, branch,
  worktree, implementation commit, focused verification, and report without an
  internally scheduled OMP Reviewer. External Planner/Reviewer inspection of a
  bounded committed SHA is outside this worker lifecycle.

---

## 9. Serial Integration & Exact-SHA Reconciliation Policy

Integration into the integration branch remains strictly serialized under a
single coordinator writer.

### AUTONOMOUS integration

```text
Executor
  ↓
focused verification
  ↓
internal OMP implementation review PASS
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
Case 1: unchanged compatible reviewed Task B:
  Integrate Task B -> Push -> Verify exact-SHA CI.
Case 2: changed/rebased/cherry-picked/conflicted Task B:
  Reconcile inside Worktree B -> focused affected verification -> new exact SHA
  -> targeted fresh internal exact-SHA review -> PASS -> integrate.
```

### BOUNDED integration

A bounded implementation task does not enter integration automatically. If a
later bounded prompt explicitly authorizes integration, its prerequisite is
external Planner/Reviewer acceptance of the exact committed SHA unless that
prompt explicitly defines another permitted condition. No internal OMP
Reviewer is inserted merely because integration is considered.

If an explicitly authorized bounded reconciliation changes the SHA:

```text
reconcile inside authorized bounded scope
→ focused verification
→ commit new exact SHA
→ report
→ HARD STOP
```

The external Planner/Reviewer then inspects that new SHA and may issue a new
bounded prompt. BOUNDED never performs reconcile → internal OMP review → PASS
→ continued integration.

*Rule:* Never inherit an AUTONOMOUS internal-review approval across a changed
commit SHA.

---

## 10. Lane Failure Isolation Policy

- A failure or review rejection in Lane A does **not** automatically halt Lane B, provided Lane B remains independent and uncoupled.
- Freeze Lane B only if Lane A's defect affects a shared contract, schema, security invariant, or assumption on which Lane B materially depends.

---

## 11. UI Pre-Review & Behavioral Verification Policy

In `AUTONOMOUS`, before releasing an independent reviewer for material
interactive UI work:
- The executor must execute and persist a pre-review acceptance gate covering the applicable Design System v1.8 checklist, accessibility standards, and behavioral tests.
- **Verification Rule:** `SOURCE_PRESENCE != INTERACTION_PROOF`. Asserting that a handler function, state setter, ref, or DOM attribute exists in source code does **not** prove interaction.
- Rendered behavior claims (e.g. focus transitions, dialog traps, dropdown dismissals, reactive selection updates) require executed rendered assertions in a real browser engine (Playwright / Chromium).
- Static source assertions are permitted only for true static invariants (e.g. token definitions, CSS custom properties).
- Browser QA must be executed against runnable targets when authorized; otherwise, limitations must be recorded truthfully.

In `BOUNDED`, those applicable behavioral checks remain focused verification
inside the authorized work set; they do not release an internal reviewer.

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
