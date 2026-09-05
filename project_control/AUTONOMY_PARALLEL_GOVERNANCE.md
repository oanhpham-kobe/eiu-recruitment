# EIU Recruitment — Continuous Autonomy & Parallel Execution Governance
## Document Version: 1.0 (PROPOSED / INACTIVE / PENDING OWNER REVIEW)
## Status: DRAFT_PENDING_OWNER_REVIEW (DO NOT ACTIVATE BEFORE OWNER SIGNOFF)

---

## 1. Activation Hold & Governance Overrides

Until explicit owner authorization activates this policy:

```yaml
GOVERNANCE_MAINTENANCE:
  status: IN_PROGRESS

AUTONOMY_POLICY_ACTIVATION:
  auto_advance: PENDING_OWNER_REVIEW
  parallel_scheduler: PENDING_OWNER_REVIEW
  max_active_implementation_tasks: 1

SLICE_04_EXECUTION:
  status: HELD_FOR_GOVERNANCE_REVIEW
```

- **Activation Override:** This activation hold explicitly overrides any prior auto-advance or continuous continuation instruction.
- **Safe Frontier Visibility:** The presence of `TASK-S04-001` in the computed safe frontier does **not** authorize starting it, creating its worktree, authoring its execution prompt, launching its executor, or merging it during this governance maintenance cycle.

---

## 2. Auto-Advance Policy (Future Rule — Currently Inactive)

### 2.1 Auto-Advance Invariant
When explicitly enabled by the owner:
```text
IF:
  run.status == ACTIVE
  AND stop_gate == null
  AND safe_frontier.eligible_tasks is non-empty
  AND auto_advance_policy == ENABLED

THEN:
  Coordinator MUST automatically advance to the earliest eligible task on the safe frontier.
```
- Merely computing, persisting, or reporting the frontier does **not** satisfy auto-advance.
- Auto-advance requires actively transitioning the task through its formal lifecycle stages.

### 2.2 Task Lifecycle Stages
To prevent ambiguous execution claims, each task must transition through distinct, observable states:
1. `FRONTIER_AVAILABLE`: Task dependencies are satisfied; task is recognized on the computed safe frontier.
2. `TASK_MATERIALIZED`: Task contract is derived from canonical sources; prompt file is authored.
3. `PROMPT_REVIEWING`: Independent prompt review is running.
4. `TASK_READY`: Prompt passed independent review with zero blockers.
5. `TASK_STARTED`: Dedicated task branch and isolated worktree are created.
6. `EXECUTOR_RUNNING`: Writing executor is actively implementing the approved prompt scope.
7. `IMPLEMENTATION_REVIEWING`: Pre-review gate passed; independent read-only reviewer is evaluating the task SHA.
8. `TASK_ACCEPTED`: Independent review passed; task commit is verified.
9. `TASK_INTEGRATED`: Task commit is merged into the authorized integration branch.
10. `CI_VERIFIED`: Exact merge SHA is pushed to remote origin and verified on GitHub Actions CI.

*Rule:* Never state "continuing autonomously" when only `FRONTIER_AVAILABLE` is true.

### 2.3 Informational Boundaries vs True Stop Conditions
Once activated, normal lifecycle completions are **informational only** and must not pause execution:
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
2. Current authorization does not permit the necessary operation (e.g. review cap exhausted without scoped exception).
3. A production, main-branch, or destructive external operation would be required.
4. Safe dependency frontier is genuinely empty or blocked with no eligible tasks.
5. A safety, security, privacy, or authorization invariant cannot be preserved.
6. Canonical project sources materially conflict and cannot be safely reconciled under canonical precedence.
7. Continuing requires architecture, data-model, or scope alterations outside current authority.

---

## 3. Active Worker State Visibility & Registry

To support future concurrent execution lanes cleanly, the coordinator maintains durable worker visibility in `AUTONOMY_RUN_STATE.yaml`:

```yaml
ACTIVE_WORKERS:
  - task_id: string         # e.g. TASK-S04-001
    lane: "LANE_A" | "LANE_B"
    role: "EXECUTOR" | "REVIEWER"
    branch: string          # e.g. oanhpham-kobe/TASK-S04-001-...
    worktree: string        # filesystem path to isolated worktree
    exact_sha: string | null # checked-out or reviewed commit SHA
    state: "STARTING" | "RUNNING" | "WAITING" | "REVIEWING" | "SETTLED" | "BLOCKED"
    started_at: string      # ISO timestamp
    last_observed_at: string # ISO timestamp

WORKER_SETTLED_HISTORY:
  - task_id: string
    lane: "LANE_A" | "LANE_B"
    role: "EXECUTOR" | "REVIEWER"
    result: "COMPLETED" | "PASS" | "FAIL" | "CANCELLED"
    exact_sha: string
    settled_at: string
```

### Worker Invariants
- **One Writer Per Worktree:** Exactly one writing executor may operate in an implementation worktree. Never allow two executors to write to the same worktree.
- **No Duplicate Workers:** Exactly one executor per active task.
- **Reviewer Independence:** Reviewers are strictly read-only and independently executed in separate processes.
- **Settlement Persistence:** Terminal idle appearance alone does not mean a worker has ceased to exist; state must be explicitly tracked.
- **Normal Settlement:** Worker process exit after successful task completion is normal and does not halt the autonomy loop.

---

## 4. Dual-Lane Execution Policy (Up to 2 Tasks)

- **Capacity ceiling:** `MAX_ACTIVE_IMPLEMENTATION_TASKS = 2`.
- **Default state:** `PARALLEL_SCHEDULER_ENABLED = false` (currently disabled pending owner review).
- **Conservative scheduling:** The coordinator must **never** force a second task merely to fill capacity. If only one safe task exists, run one lane.
- **Lane B Admission:** Lane B may only be launched when the candidate task independently passes the **Parallel Eligibility Gate**.

---

## 5. Parallel Eligibility Policy & Gate

Before scheduling two tasks concurrently (Task A and Task B):
1. **DAG Precondition:** Both tasks must independently belong to the safe dependency frontier (`depends_on` completely satisfied). The absence of a direct dependency edge is necessary, but **not sufficient**.
2. **Eligibility Verification:** The coordinator must evaluate the 5-point parallel eligibility checklist and persist an audit receipt in `EVIDENCE_INDEX.yaml`:

```yaml
PARALLEL_ELIGIBILITY:
  task_a: TASK-A-ID
  task_b: TASK-B-ID
  analyzed_integration_head: <commit-sha>

  dependency_check:
    direct_dependency: NONE
    transitive_dependency: NONE
    result: PASS | FAIL

  graph_check:
    crg_used: YES | NO
    gitnexus_used: YES | NO
    graph_freshness: VERIFIED | UNAVAILABLE
    analyzed_head: <commit-sha>
    shared_symbols: NONE | <list>
    caller_callee_dependency: NONE | <list>
    blast_radius_overlap: NONE | <list>
    result: PASS | FAIL

  write_surface:
    overlapping_primary_files: NONE | <list>
    overlapping_modules: NONE | <list>
    result: PASS | FAIL

  shared_contracts:
    api_type_contract_dependency: NONE | <list>
    auth_security_core_overlap: NONE | <list>
    result: PASS | FAIL

  database_surface:
    structural_migration_a: YES | NO
    structural_migration_b: YES | NO
    migration_order_dependency: NONE | <list>
    shared_tables: NONE | <list>
    shared_functions: NONE | <list>
    shared_rls_grants: NONE | <list>
    result: PASS | FAIL

  decision: PARALLEL_ALLOWED | SERIALIZE
```

*Rule:* If any check fails, or if there is material uncertainty: **SERIALIZE**.

---

## 6. Graph Policy for Parallelization

- Graph intelligence (CRG and GitNexus) is **mandatory** when evaluating parallel eligibility between concurrent candidate tasks, but **not required mechanically** for trivial or localized single-task implementation.
- **CRG:** Used for broad module boundary discovery and changed-area diff triage.
- **GitNexus:** Used for precise symbol caller/callee tracing, import analysis, and blast-radius overlap checks.
- **Freshness Rule:** A graph query is invalid as evidence unless refreshed against the current integration HEAD.
- **Database Authority:** Repository migrations, declarative schemas, and SQL test replays always outrank graph representations for database structure and RLS behavior.
- **Graph Fallback:** If graph tooling is unavailable, fall back to direct dependency, source, and write-surface inspection; if independence is not overwhelmingly obvious, **default to SERIALIZE**. Never fabricate graph use.

---

## 7. Do-Not-Parallel Rules (Mandatory Serialization)

Two candidate tasks MUST serialize if ANY of the following apply:
1. A direct dependency exists between them.
2. A transitive dependency exists between them.
3. One task produces an API, RPC, schema, type, or contract consumed by the other.
4. Primary implementation files overlap.
5. Shared core modules overlap.
6. Both tasks modify the authentication or authorization security core.
7. Both tasks modify shared global configuration (e.g. `globals.css`, `tokens.css`, `AppShell`, root layout).
8. Both tasks modify package dependencies or `package-lock.json`.
9. Both tasks modify the design system shell infrastructure.
10. Both tasks modify the same database table, SQL function, trigger, RLS policy, or locking protocol.
11. Migration execution order between the two tasks is interdependent.
12. One task's correctness relies on an unresolved finding or assumption in the other.

**Default Database Serialization Rule:**
If **both** tasks introduce structural database migrations: **SERIALIZE**. Override only with exceptional proof of total independence across distinct domains.

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

## 9. Serial Integration & Reconciliation Policy

While implementation and review may run in parallel across lanes, **integration into the integration branch MUST remain strictly serialized** under a single coordinator writer:

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
  Rebase / compare Task B against NEW integration HEAD (containing Task A)
  Verify Task B assumptions and contracts remain unbroken
  ↓
If compatible:
  Merge Task B -> Push -> Verify exact-SHA CI
If reconciliation required:
  Do NOT resolve substantive logic on integration branch!
  Reconcile inside Worktree B -> Amend Task B commit -> Rerun affected tests ->
  Obtain fresh independent review on exact amended SHA -> Integrate only after PASS.
```

---

## 10. Lane Failure Isolation Policy

- A failure or review rejection in Lane A does **not** automatically halt Lane B, provided Lane B remains independent and uncoupled.
- Freeze Lane B only if Lane A's defect affects a shared contract, schema, security invariant, or assumption on which Lane B materially depends.

---

## 11. UI Pre-Review & Behavioral Verification Policy

Before releasing an independent reviewer for material UI tasks:
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
