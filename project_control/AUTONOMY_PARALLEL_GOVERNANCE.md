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
governance_maintenance:
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

## 4. Active Worker Model & Visibility

`active_workers` in `project_control/AUTONOMY_RUN_STATE.yaml` is the sole concurrency authority.

```yaml
active_workers:
  - task_id: string          # e.g. TASK-S04-001
    lane: "LANE_A" | "LANE_B"
    role: "EXECUTOR" | "REVIEWER"
    branch: string           # e.g. oanhpham-kobe/TASK-S04-001-...
    worktree: string         # filesystem path to isolated worktree
    exact_sha: string | null # checked-out or reviewed commit SHA
    state: "STARTING" | "RUNNING" | "WAITING" | "REVIEWING" | "SETTLED" | "BLOCKED"
    started_at: string       # ISO timestamp
    last_observed_at: string # ISO timestamp

worker_settled_history:
  - task_id: string
    lane: "LANE_A" | "LANE_B"
    role: "EXECUTOR" | "REVIEWER"
    result: "COMPLETED" | "PASS" | "FAIL" | "CANCELLED"
    exact_sha: string
    settled_at: string
```

### Worker Invariants & Retention
- **One Writer Per Worktree:** Exactly one writing executor may operate in an implementation worktree. Never allow two executors to write to the same worktree.
- **No Duplicate Workers:** Exactly one executor per active task.
- **Reviewer Independence:** Reviewers are strictly read-only and execute independently in separate processes.
- **Settlement Persistence:** Terminal idle appearance alone does not mean a worker has ceased to exist; state must be explicitly tracked.
- **Normal Settlement:** Worker process exit after successful task completion is normal and does not halt the autonomy loop.
- **Bounded Retention Rule:** `worker_settled_history` retains only the last 10 settled worker operations (operational debug window). Permanent task completion evidence belongs in `EVIDENCE_INDEX.yaml`.
- **Legacy Compatibility Pointers:** `active_task`, `current_task`, and `current_slice` are summary/compatibility pointers only. They must never overwrite multi-worker state or serve as concurrency authority.

---

## 5. Dual-Lane Execution Policy (Up to 2 Tasks)

- **Capacity ceiling:** `max_active_implementation_tasks = 2`.
- **Activation:** Permitted only when `autonomy_policy_activation.parallel_scheduler == ENABLED` and `max_active_implementation_tasks == 2`.
- **Conservative scheduling:** The coordinator must **never** force two tasks merely to fill capacity. If only one safe task exists, run one lane.
- **Scheduling Algorithm:**
  1. Pick earliest safe eligible task A on frontier $\rightarrow$ dispatch to Lane A.
  2. If capacity remains, evaluate candidate task B from frontier.
  3. Execute Parallel Eligibility Gate (A $\leftrightarrow$ B).
  4. If PASS: dispatch B to Lane B. If FAIL: serialize.
- **Lane Refill:** When a lane frees up (task accepted, worker settled), check for a new candidate B on the current frontier, evaluate compatibility against the remaining active task, and launch B only if the gate passes.

---

## 6. Parallel Eligibility Policy & Gate

Before scheduling two tasks concurrently (Task A and Task B):
1. **DAG Precondition:** Both tasks must independently belong to the safe dependency frontier (`depends_on` completely satisfied). The absence of a direct dependency edge is necessary, but **not sufficient**.
2. **Eligibility Verification:** The coordinator evaluates the 5-point parallel eligibility checklist and persists an audit receipt in `EVIDENCE_INDEX.yaml`:

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

## 7. Graph Policy for Parallelization

- Graph intelligence (CRG and GitNexus) is **mandatory** when evaluating parallel eligibility between concurrent candidate tasks, but **not required mechanically** for trivial or localized single-task implementation.
- **CRG:** Broad module boundary discovery and changed-area diff triage.
- **GitNexus:** Precise symbol caller/callee tracing, import analysis, and blast-radius overlap checks.
- **Freshness Rule:** A graph query is invalid as evidence unless refreshed against the current integration HEAD.
- **Database Authority:** Repository migrations, declarative schemas, and SQL test replays always outrank graph representations for database structure and RLS behavior.
- **Graph Fallback:** If graph tooling is unavailable, fall back to direct dependency, source, and write-surface inspection; if independence is not overwhelmingly obvious, **default to SERIALIZE**. Never fabricate graph use.

---

## 8. Do-Not-Parallel Rules (Mandatory Serialization)

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

## 9. Worktree & Worker Isolation Policy

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

## 10. Serial Integration & Exact-SHA Reconciliation Policy

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

## 11. Lane Failure Isolation Policy

- A failure or review rejection in Lane A does **not** automatically halt Lane B, provided Lane B remains independent and uncoupled.
- Freeze Lane B only if Lane A's defect affects a shared contract, schema, security invariant, or assumption on which Lane B materially depends.

---

## 12. UI Pre-Review & Behavioral Verification Policy

Before releasing an independent reviewer for material interactive UI work:
- The executor must execute and persist a pre-review acceptance gate covering the applicable Design System v1.8 checklist, accessibility standards, and behavioral tests.
- **Verification Rule:** `SOURCE_PRESENCE != INTERACTION_PROOF`. Asserting that a handler function, state setter, ref, or DOM attribute exists in source code does **not** prove interaction.
- Rendered behavior claims (e.g. focus transitions, dialog traps, dropdown dismissals, reactive selection updates) require executed rendered assertions in a real browser engine (Playwright / Chromium).
- Static source assertions are permitted only for true static invariants (e.g. token definitions, CSS custom properties).
- Browser QA must be executed against runnable targets when authorized; otherwise, limitations must be recorded truthfully.

---

## 13. Technical Decision Principle for Planners & Reviewers

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
