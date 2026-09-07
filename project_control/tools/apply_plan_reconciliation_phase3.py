from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPECTED_BRANCH = "governance/source-plan-reconciliation-s04-005-001"
EXPECTED_PROMPT_SHA256 = "dacac3a2b6f4bdc622aa170445a9aa5f0febabdc78bffb7f30f047639bc97353"


def run(*args: str) -> str:
    result = subprocess.run(
        args,
        cwd=ROOT,
        text=True,
        check=False,
        capture_output=True,
    )
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="")
    if result.returncode != 0:
        raise subprocess.CalledProcessError(
            result.returncode,
            result.args,
            output=result.stdout,
            stderr=result.stderr,
        )
    return result.stdout.strip()


def replace_exact(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one match, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def insert_once(path: Path, anchor: str, insertion: str, marker: str) -> None:
    text = path.read_text(encoding="utf-8")
    if marker in text:
        print(f"{path.relative_to(ROOT)}: marker already present; leaving unchanged")
        return
    count = text.count(anchor)
    if count != 1:
        raise RuntimeError(
            f"{path.relative_to(ROOT)}: expected exactly one insertion anchor, found {count}"
        )
    path.write_text(text.replace(anchor, insertion + anchor, 1), encoding="utf-8")


def main() -> int:
    branch = run("git", "branch", "--show-current")
    if branch != EXPECTED_BRANCH:
        raise RuntimeError(f"refusing to run on branch {branch!r}")

    prompt_path = ROOT / "project_control/prompts/SLICE-04_TASK-004_v2.md"
    prompt_hash = hashlib.sha256(prompt_path.read_bytes()).hexdigest()
    if prompt_hash != EXPECTED_PROMPT_SHA256:
        raise RuntimeError(
            f"S04-004 v2 prompt hash mismatch: {prompt_hash} != {EXPECTED_PROMPT_SHA256}"
        )

    task_path = ROOT / "project_control/TASK_REGISTRY.yaml"
    replace_exact(
        task_path,
        "current_task: TASK-S04-003",
        "current_task: TASK-S04-004",
        "TASK_REGISTRY current_task",
    )

    old_task_block = '''  TASK-S04-004:\n    title: "HR Interview scheduling UI over accepted trusted commands"\n    slice: SLICE-04\n    status: BLOCKED\n    lane: LANE_A\n    depends_on:\n      - TASK-S04-005\n    prompt: project_control/prompts/SLICE-04_TASK-004_v1.md\n    prompt_sha256: 67a4e356d63343a93dbeba1394bca351795da22da51408eeb549b32a257a9c16\n    prompt_review_status: "BLOCKING_REPAIR (agent://TaskS04004PromptReview)"\n    notes: "Prompt review proved missing reactivate_application and noncanonical/ambiguous participant RPC contracts. UI dispatch is blocked until TASK-S04-005 is accepted."\n'''
    new_task_block = '''  TASK-S04-004:\n    title: "HR Interview scheduling UI over accepted trusted commands"\n    slice: SLICE-04\n    status: BLOCKED\n    lane: LANE_A\n    depends_on:\n      - TASK-S04-005\n    prompt: project_control/prompts/SLICE-04_TASK-004_v2.md\n    prompt_sha256: dacac3a2b6f4bdc622aa170445a9aa5f0febabdc78bffb7f30f047639bc97353\n    prompt_review_status: "PENDING_INDEPENDENT_REVIEW"\n    notes: "TASK-S04-005 dependency is satisfied and CI-verified. The original v1 prompt blocker was repaired by the accepted S04-005 backend contract. Dispatch remains blocked only by PLAN_RECONCILIATION_GATE_S04_005 and independent review of the rebaselined v2 prompt."\n'''
    replace_exact(task_path, old_task_block, new_task_block, "TASK-S04-004 block")

    policy_path = ROOT / "project_control/AUTONOMY_PARALLEL_GOVERNANCE.md"
    policy_anchor = "\n---\n\n## 2. Execution Mode and Runtime Authority\n"
    policy_insertion = '''\n### Cross-slice accepted prerequisite rule\n\nSlice status represents completion of that slice's user/business feature scope; it does not imply exclusive ownership of every implementation artifact later consumed by that slice.\n\nIf an earlier accepted task legitimately materializes a backend, schema, infrastructure, or trusted-command prerequisite that a later slice will consume:\n\n- the later slice may remain `NOT_STARTED` until its own feature work begins;\n- the accepted prerequisite remains authoritative implementation and must be recorded in planning/traceability;\n- future task materialization must consume that accepted prerequisite instead of recreating, forking, or silently superseding it;\n- a later slice's `NOT_STARTED` state is never evidence that its already-accepted prerequisite is unimplemented; and\n- any real contradiction between the accepted prerequisite and current canonical source is a reconciliation/source gate, not permission to duplicate the contract.\n\nThis rule preserves slice-status meaning while preventing downstream reimplementation drift (for example, report backend prerequisites accepted in Slice-04 and later consumed by Slice-05).\n\n'''
    insert_once(
        policy_path,
        policy_anchor,
        policy_insertion,
        "### Cross-slice accepted prerequisite rule",
    )

    validator_path = ROOT / "project_control/validate_control_plane.py"
    validator_anchor = "    # ---------------------------------------------------------\n    # Safe frontier\n    # ---------------------------------------------------------\n"
    validator_insertion = '''    # ---------------------------------------------------------\n    # Current pointer / accepted-task semantic consistency\n    # ---------------------------------------------------------\n\n    task_current_slice = task_registry.get("current_slice")\n    slice_current_slice = slice_registry.get("current_slice")\n    task_current_task = task_registry.get("current_task")\n\n    if task_current_slice != slice_current_slice:\n        errors.append(\n            "TASK_REGISTRY.current_slice does not match "\n            "SLICE_REGISTRY.current_slice"\n        )\n\n    current_task_entry = tasks.get(task_current_task)\n    if not isinstance(current_task_entry, dict):\n        errors.append(\n            f"TASK_REGISTRY.current_task references unknown task {task_current_task!r}"\n        )\n    else:\n        if current_task_entry.get("slice") != task_current_slice:\n            errors.append(\n                "TASK_REGISTRY.current_task does not belong to current_slice"\n            )\n\n    current_slice_entry = slices.get(slice_current_slice)\n    if isinstance(current_slice_entry, dict):\n        if current_slice_entry.get("current_task") != task_current_task:\n            errors.append(\n                "SLICE_REGISTRY current slice current_task does not match "\n                "TASK_REGISTRY.current_task"\n            )\n\n        if (\n            current_slice_entry.get("status") == "IN_PROGRESS"\n            and isinstance(current_task_entry, dict)\n            and current_task_entry.get("status") == "DONE"\n        ):\n            incomplete_members = [\n                task_id\n                for task_id, task in tasks.items()\n                if isinstance(task, dict)\n                and task.get("slice") == slice_current_slice\n                and task.get("status")\n                not in {"DONE", "SUPERSEDED", "CANCELLED"}\n            ]\n            if incomplete_members:\n                errors.append(\n                    "current_slice is IN_PROGRESS but current_task is DONE while "\n                    "non-terminal members remain: "\n                    + ", ".join(sorted(incomplete_members))\n                )\n\n    last_accepted = run_state.get("last_accepted_task")\n    if last_accepted is not None:\n        if not isinstance(last_accepted, dict):\n            errors.append("last_accepted_task must be a mapping")\n        else:\n            accepted_id = last_accepted.get("id")\n            accepted_commit = last_accepted.get("commit")\n            accepted_task = tasks.get(accepted_id)\n            if not isinstance(accepted_task, dict):\n                errors.append(\n                    f"last_accepted_task references unknown task {accepted_id!r}"\n                )\n            else:\n                if accepted_task.get("status") != "DONE":\n                    errors.append(\n                        f"last_accepted_task {accepted_id} is not DONE"\n                    )\n                if not is_exact_sha(accepted_commit):\n                    errors.append(\n                        "last_accepted_task.commit must be an exact 40-character SHA"\n                    )\n                implementation_sha = accepted_task.get("implementation_sha")\n                if (\n                    implementation_sha is not None\n                    and accepted_commit != implementation_sha\n                ):\n                    errors.append(\n                        "last_accepted_task.commit does not match "\n                        f"{accepted_id}.implementation_sha"\n                    )\n\n'''
    insert_once(
        validator_path,
        validator_anchor,
        validator_insertion,
        "# Current pointer / accepted-task semantic consistency",
    )

    frontier_anchor = '''    eligible_tasks = require_list(\n        safe_frontier.get(\n            "eligible_tasks",\n            [],\n        ),\n        "safe_frontier.eligible_tasks",\n        errors,\n    )\n\n'''
    frontier_check = '''    execution_hold = safe_frontier.get("execution_hold")\n    if execution_hold and eligible_tasks:\n        errors.append(\n            "safe_frontier.execution_hold is set while eligible_tasks is non-empty"\n        )\n\n'''
    replace_exact(
        validator_path,
        frontier_anchor,
        frontier_anchor + frontier_check,
        "safe frontier hold/eligibility ordering",
    )

    changed = run("git", "diff", "--name-only").splitlines()
    allowed = {
        "project_control/TASK_REGISTRY.yaml",
        "project_control/AUTONOMY_PARALLEL_GOVERNANCE.md",
        "project_control/validate_control_plane.py",
    }
    if set(changed) != allowed:
        raise RuntimeError(f"unexpected patch surface: {changed!r}")

    run("python", "project_control/validate_omp_native.py")
    run("python", "project_control/validate_control_plane.py")
    run("git", "diff", "--check")

    print("PLAN RECONCILIATION P2-B PATCH: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
