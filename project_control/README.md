# EIU Recruitment Project Control Navigation

`project_control/` is the durable coordination surface for implementation, review, CI, and cross-session continuation.

The current business/product/design authority remains under `recruitment_webapp/`. This folder controls HOW implementation work is scheduled, evidenced, resumed, and integrated; it does not redefine product behavior.

## Authority map

Use one fact from one authority:

- `AUTONOMY_PARALLEL_GOVERNANCE.md` — lifecycle, scheduler, lane, review, repair, integration, CI, and continuation semantics.
- `AUTONOMY_RUN_STATE.yaml` — live execution mode, activation, workers, lane reservations, safe frontier, stop gate, integration checkpoint.
- `TASK_REGISTRY.yaml` — task DAG, dependencies, task status, prompt/implementation/review/CI references.
- `SLICE_REGISTRY.yaml` — slice status and current task pointer.
- `EVIDENCE_INDEX.yaml` — compact durable verification evidence.
- `CURRENT_STATE.md` — derived human/AI handoff snapshot only; never scheduling authority.
- `TRACEABILITY_STATUS.csv` — derived reporting surface only.
- `CHANGELOG_IMPLEMENTATION.md` — chronological implementation narrative/history.
- `prompts/` — released task contracts.
- `validate_control_plane.py` — machine validation of the durable control plane.
- `validate_omp_native.py` — machine validation of the OMP-native project runtime configuration.

## Cross-session resume protocol

A new OMP session, ChatGPT session, or other authorized coding runtime should resume in this order:

1. Read `AGENTS.md` and `.omp/RULES.md`.
2. Read `project_control/CURRENT_STATE.md` for navigation only.
3. Verify the current Git repository, branch, and exact HEAD directly.
4. Read `AUTONOMY_RUN_STATE.yaml`, `TASK_REGISTRY.yaml`, and `SLICE_REGISTRY.yaml` as the durable truth.
5. Run:

   ```text
   python project_control/validate_omp_native.py
   python project_control/validate_control_plane.py
   ```

6. Reconcile any stale derived snapshot against Git and the registries.
7. Read the active task prompt and the canonical source/design sections it references.
8. Continue only from the current authorized safe frontier.

`CURRENT_STATE.md` should be refreshed after every accepted task and after any meaningful interruption that changes the correct resume action. It is intentionally small and must point to evidence instead of copying the evidence store.

Do not create runtime-specific memory authorities such as `AI_MEMORY.md`, `OMP_STATE.yaml`, or `CHATGPT_STATE.yaml`.

## Local worktree layout

The many `TASK-*`, `governance-*`, `GOV-*`, and `PRE-*` directories visible beside the root checkout on a developer machine are Git linked worktrees, not repository subfolders and not durable task records.

GitHub stores their commits/branches; it does not mirror the local linked-worktree directory layout. A linked worktree is a full checkout of the repository at another branch/commit.

For new local execution, use one ignored container under the repository root:

```text
repo/
├─ .worktrees/
│  ├─ tasks/
│  │  └─ TASK-S04-004-interview-ui/
│  ├─ maintenance/
│  │  └─ governance-example/
│  └─ other/
├─ project_control/
├─ recruitment_webapp/
├─ supabase/
└─ web/
```

Rules:

- `.worktrees/` is local-only and gitignored.
- Use `git worktree move` to relocate registered worktrees; never move them manually in Explorer.
- Never `git clean`, hard-reset, delete, or unregister a worktree merely to tidy the root directory.
- Unregistered directories are not moved automatically.
- Worktree paths are ephemeral local runtime metadata. Do not add new machine-specific absolute worktree paths to durable task history.
- `active_workers` may record the current runtime worktree needed to prevent concurrent ownership collisions.
- Completed linked worktrees are disposable execution surfaces. Preserve history in Git plus `TASK_REGISTRY.yaml`, `EVIDENCE_INDEX.yaml`, and the implementation changelog, not by retaining a full checkout forever.

## Safe local consolidation helper

`project_control/tools/reorganize_worktrees.ps1` inspects registered linked worktrees and plans a move into `.worktrees/`.

Dry run first:

```powershell
powershell -ExecutionPolicy Bypass -File project_control/tools/reorganize_worktrees.ps1
```

Apply only after reviewing the plan:

```powershell
powershell -ExecutionPolicy Bypass -File project_control/tools/reorganize_worktrees.ps1 -Apply
```

The helper:

- skips the main/root worktree;
- only considers registered child worktrees physically located below the repository root;
- leaves ordinary unregistered folders such as temporary Supabase scratch directories alone;
- preserves each worktree branch and HEAD and verifies them after the move;
- aborts on destination collisions or failed verification;
- performs no reset, clean, stash, checkout, branch deletion, or content deletion.

## Task record style going forward

Historical task entries may contain old loader receipts, machine-specific provider paths, or verbose execution evidence from earlier governance versions. Keep them as historical audit data unless a focused migration is justified.

New task records should be compact:

```yaml
TASK-SXX-YYY:
  title: "..."
  slice: SLICE-XX
  status: READY | IN_PROGRESS | REVIEW | BLOCKED | DONE
  lane: LANE_A | LANE_B
  depends_on: [...]
  prompt: project_control/prompts/...
  implementation_sha: "<exact sha>"   # when available
  review_status: "PASS ..."           # when available
  github_ci: "VERIFIED ..."           # when available
  notes: "short factual lifecycle note"
```

Do not add `SKILLS_REQUIRED`, `SKILLS_RESOLVED`, `SKILLS_APPLIED`, `AVAILABLE / LOADED / APPLIED` receipts, runtime filesystem skill providers, or machine-specific global paths. OMP owns native skill discovery/loading; task evidence should describe behavior, tests, review, and exact-SHA CI.

## Handoff principle

The resume model is deliberately small:

```text
CURRENT_STATE.md          -> where to resume
AUTONOMY_RUN_STATE.yaml   -> live execution truth
TASK/SLICE_REGISTRY       -> DAG truth
EVIDENCE_INDEX.yaml       -> durable proof
Git                       -> exact code/history truth
```

A handoff never overrides Git or the registries. If they disagree, repair the derived handoff instead of changing authoritative state to match stale prose.
