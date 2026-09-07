from __future__ import annotations

import re
from collections import Counter
from pathlib import Path
from typing import Any

import yaml
from yaml.constructor import ConstructorError
from yaml.resolver import BaseResolver


ROOT = Path(__file__).resolve().parents[1]

RUN_STATE_PATH = ROOT / "project_control" / "AUTONOMY_RUN_STATE.yaml"
TASK_REGISTRY_PATH = ROOT / "project_control" / "TASK_REGISTRY.yaml"
SLICE_REGISTRY_PATH = ROOT / "project_control" / "SLICE_REGISTRY.yaml"
CURRENT_STATE_PATH = ROOT / "project_control" / "CURRENT_STATE.md"
TRACEABILITY_PATH = ROOT / "project_control" / "TRACEABILITY_STATUS.csv"

ALLOWED_ACTIVATION = {
    "PENDING_OWNER_REVIEW",
    "ENABLED",
    "DISABLED",
}

DEPENDENCY_ENFORCED_STATUSES = {
    "READY",
    "IN_PROGRESS",
    "REVIEW",
    "DONE",
}

ALLOWED_EXECUTION_MODES = {
    "AUTONOMOUS",
    "BOUNDED",
}

REVIEWER_STATUSES = {
    "REVIEWING",
    "RE_REVIEWING",
}

REVIEW_SCOPES = {
    "INITIAL",
    "INCREMENTAL_REPAIR",
}

BOUNDED_REQUIRED_FALSE_PERMITS = {
    "implementation_reviewer",
    "automatic_repair_rereview",
    "next_frontier_task",
}

BOUNDED_OPTIONAL_PERMITS = {
    "integration",
    "integration_ci",
}


class UniqueKeyLoader(yaml.SafeLoader):
    pass


def construct_unique_mapping(
    loader: UniqueKeyLoader,
    node: yaml.nodes.MappingNode,
    deep: bool = False,
) -> dict[Any, Any]:
    mapping: dict[Any, Any] = {}

    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)

        if key in mapping:
            raise ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"found duplicate key: {key!r}",
                key_node.start_mark,
            )

        mapping[key] = loader.construct_object(
            value_node,
            deep=deep,
        )

    return mapping


UniqueKeyLoader.add_constructor(
    BaseResolver.DEFAULT_MAPPING_TAG,
    construct_unique_mapping,
)


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(
            f"Missing required file: {path.relative_to(ROOT)}"
        )

    with path.open("r", encoding="utf-8") as handle:
        data = yaml.load(
            handle,
            Loader=UniqueKeyLoader,
        )

    if not isinstance(data, dict):
        raise RuntimeError(
            f"Expected YAML mapping in "
            f"{path.relative_to(ROOT)}"
        )

    return data


def require_list(
    value: Any,
    field: str,
    errors: list[str],
) -> list[Any]:
    if value is None:
        return []

    if not isinstance(value, list):
        errors.append(
            f"{field} must be a list"
        )
        return []

    return value


def is_exact_sha(value: Any) -> bool:
    return (
        isinstance(value, str)
        and re.fullmatch(
            r"[0-9a-f]{40}",
            value,
        )
        is not None
    )


def main() -> int:
    errors: list[str] = []

    try:
        run_state = load_yaml(RUN_STATE_PATH)
        task_registry = load_yaml(TASK_REGISTRY_PATH)
        slice_registry = load_yaml(SLICE_REGISTRY_PATH)
    except Exception as exc:
        print("CONTROL PLANE VALIDATION: FAIL")
        print(
            f" - YAML load/structure error: {exc}"
        )
        return 1

    tasks = task_registry.get("tasks", {})
    slices = slice_registry.get("slices", {})

    if not isinstance(tasks, dict):
        errors.append(
            "TASK_REGISTRY.tasks must be a mapping"
        )
        tasks = {}

    if not isinstance(slices, dict):
        errors.append(
            "SLICE_REGISTRY.slices must be a mapping"
        )
        slices = {}

    # ---------------------------------------------------------
    # DAG / registry consistency
    # ---------------------------------------------------------

    for task_id, task in tasks.items():
        if not isinstance(task, dict):
            errors.append(
                f"{task_id}: task entry must be a mapping"
            )
            continue

        slice_id = task.get("slice")

        if slice_id not in slices:
            errors.append(
                f"{task_id}: references unknown slice "
                f"{slice_id!r}"
            )

        dependencies = require_list(
            task.get("depends_on", []),
            f"{task_id}.depends_on",
            errors,
        )

        for dependency in dependencies:
            if dependency not in tasks:
                errors.append(
                    f"{task_id}: depends on unknown task "
                    f"{dependency}"
                )

        status = task.get("status")

        if status in DEPENDENCY_ENFORCED_STATUSES:
            for dependency in dependencies:
                dependency_entry = tasks.get(
                    dependency
                )

                if (
                    isinstance(
                        dependency_entry,
                        dict,
                    )
                    and dependency_entry.get(
                        "status"
                    )
                    != "DONE"
                ):
                    errors.append(
                        f"{task_id}: status={status} but "
                        f"dependency {dependency} is "
                        f"{dependency_entry.get('status')}"
                    )

    for slice_id, slice_entry in slices.items():
        if not isinstance(slice_entry, dict):
            errors.append(
                f"{slice_id}: slice entry must be a mapping"
            )
            continue

        if slice_entry.get("status") != "DONE":
            continue

        members = [
            (task_id, task)
            for task_id, task in tasks.items()
            if isinstance(task, dict)
            and task.get("slice") == slice_id
        ]

        for task_id, task in members:
            if task.get("status") != "DONE":
                errors.append(
                    f"{slice_id}: DONE but contains "
                    f"{task_id}={task.get('status')}"
                )

    # ---------------------------------------------------------
    # Current pointer / accepted-task semantic consistency
    # ---------------------------------------------------------

    task_current_slice = task_registry.get("current_slice")
    slice_current_slice = slice_registry.get("current_slice")
    task_current_task = task_registry.get("current_task")

    if task_current_slice != slice_current_slice:
        errors.append(
            "TASK_REGISTRY.current_slice does not match "
            "SLICE_REGISTRY.current_slice"
        )

    current_task_entry = tasks.get(task_current_task)
    if not isinstance(current_task_entry, dict):
        errors.append(
            f"TASK_REGISTRY.current_task references unknown task {task_current_task!r}"
        )
    else:
        if current_task_entry.get("slice") != task_current_slice:
            errors.append(
                "TASK_REGISTRY.current_task does not belong to current_slice"
            )

    current_slice_entry = slices.get(slice_current_slice)
    if isinstance(current_slice_entry, dict):
        if current_slice_entry.get("current_task") != task_current_task:
            errors.append(
                "SLICE_REGISTRY current slice current_task does not match "
                "TASK_REGISTRY.current_task"
            )

        if (
            current_slice_entry.get("status") == "IN_PROGRESS"
            and isinstance(current_task_entry, dict)
            and current_task_entry.get("status") == "DONE"
        ):
            incomplete_members = [
                task_id
                for task_id, task in tasks.items()
                if isinstance(task, dict)
                and task.get("slice") == slice_current_slice
                and task.get("status")
                not in {"DONE", "SUPERSEDED", "CANCELLED"}
            ]
            if incomplete_members:
                errors.append(
                    "current_slice is IN_PROGRESS but current_task is DONE while "
                    "non-terminal members remain: "
                    + ", ".join(sorted(incomplete_members))
                )

    last_accepted = run_state.get("last_accepted_task")
    if last_accepted is not None:
        if not isinstance(last_accepted, dict):
            errors.append("last_accepted_task must be a mapping")
        else:
            accepted_id = last_accepted.get("id")
            accepted_commit = last_accepted.get("commit")
            accepted_task = tasks.get(accepted_id)
            if not isinstance(accepted_task, dict):
                errors.append(
                    f"last_accepted_task references unknown task {accepted_id!r}"
                )
            else:
                if accepted_task.get("status") != "DONE":
                    errors.append(
                        f"last_accepted_task {accepted_id} is not DONE"
                    )
                if not is_exact_sha(accepted_commit):
                    errors.append(
                        "last_accepted_task.commit must be an exact 40-character SHA"
                    )
                implementation_sha = accepted_task.get("implementation_sha")
                if (
                    implementation_sha is not None
                    and accepted_commit != implementation_sha
                ):
                    errors.append(
                        "last_accepted_task.commit does not match "
                        f"{accepted_id}.implementation_sha"
                    )

    # ---------------------------------------------------------
    # Safe frontier
    # ---------------------------------------------------------

    safe_frontier = run_state.get(
        "safe_frontier",
        {},
    )

    if not isinstance(safe_frontier, dict):
        errors.append(
            "AUTONOMY_RUN_STATE.safe_frontier "
            "must be a mapping"
        )
        safe_frontier = {}

    eligible_tasks = require_list(
        safe_frontier.get(
            "eligible_tasks",
            [],
        ),
        "safe_frontier.eligible_tasks",
        errors,
    )

    execution_hold = safe_frontier.get("execution_hold")
    if execution_hold and eligible_tasks:
        errors.append(
            "safe_frontier.execution_hold is set while eligible_tasks is non-empty"
        )

    for task_id in eligible_tasks:
        task = tasks.get(task_id)

        if not isinstance(task, dict):
            errors.append(
                f"safe_frontier: unknown task "
                f"{task_id}"
            )
            continue

        if task.get("status") == "DONE":
            errors.append(
                f"safe_frontier: {task_id} "
                f"is already DONE"
            )

        dependencies = require_list(
            task.get(
                "depends_on",
                [],
            ),
            f"{task_id}.depends_on",
            errors,
        )

        for dependency in dependencies:
            dependency_entry = tasks.get(
                dependency
            )

            if (
                not isinstance(
                    dependency_entry,
                    dict,
                )
                or dependency_entry.get(
                    "status"
                )
                != "DONE"
            ):
                errors.append(
                    f"safe_frontier: {task_id} "
                    f"dependency {dependency} "
                    f"is not DONE"
                )


    # ---------------------------------------------------------
    # Execution mode / bounded authorization
    # ---------------------------------------------------------
    execution_mode = run_state.get(
        "execution_mode"
    )

    if execution_mode not in ALLOWED_EXECUTION_MODES:
        errors.append(
            "invalid execution_mode: "
            f"{execution_mode!r}"
        )

    bounded_execution = run_state.get(
        "bounded_execution"
    )
    bounded_task_ids: set[str] = set()

    if execution_mode == "BOUNDED":
        if not isinstance(
            bounded_execution,
            dict,
        ):
            errors.append(
                "BOUNDED requires "
                "bounded_execution mapping"
            )
            bounded_execution = {}

        work_set_id = bounded_execution.get(
            "authorized_work_set_id"
        )

        if (
            not isinstance(work_set_id, str)
            or not work_set_id.strip()
        ):
            errors.append(
                "BOUNDED requires "
                "authorized_work_set_id"
            )

        authorized_task_ids = require_list(
            bounded_execution.get(
                "authorized_task_ids",
                [],
            ),
            "bounded_execution."
            "authorized_task_ids",
            errors,
        )
        bounded_task_ids = {
            task_id
            for task_id in authorized_task_ids
            if isinstance(task_id, str)
            and task_id.strip()
        }

        if not bounded_task_ids:
            errors.append(
                "BOUNDED requires at least one "
                "authorized_task_id"
            )

        authorized_paths = require_list(
            bounded_execution.get(
                "authorized_paths",
                [],
            ),
            "bounded_execution."
            "authorized_paths",
            errors,
        )

        if not authorized_paths or any(
            not isinstance(path, str)
            or not path.strip()
            for path in authorized_paths
        ):
            errors.append(
                "BOUNDED requires non-empty "
                "authorized_paths"
            )

        permits = bounded_execution.get(
            "permits",
            {},
        )

        if not isinstance(permits, dict):
            errors.append(
                "bounded_execution.permits "
                "must be a mapping"
            )
            permits = {}

        for permit in BOUNDED_REQUIRED_FALSE_PERMITS:
            if permits.get(permit) is not False:
                errors.append(
                    "BOUNDED requires "
                    f"permits.{permit}=false"
                )

        for permit in BOUNDED_OPTIONAL_PERMITS:
            if not isinstance(
                permits.get(permit),
                bool,
            ):
                errors.append(
                    "BOUNDED requires boolean "
                    f"permits.{permit}"
                )

        if (
            permits.get("integration_ci") is True
            and permits.get("integration") is not True
        ):
            errors.append(
                "BOUNDED integration_ci requires "
                "permits.integration=true"
            )
    elif bounded_execution is not None:
        errors.append(
            "AUTONOMOUS must not retain "
            "bounded_execution"
        )
    # ---------------------------------------------------------
    # Runtime policy activation
    # ---------------------------------------------------------

    activation = run_state.get(
        "autonomy_policy_activation",
        {},
    )

    if not isinstance(activation, dict):
        errors.append(
            "AUTONOMY_RUN_STATE."
            "autonomy_policy_activation "
            "must be a mapping"
        )
        activation = {}

    policy_path = activation.get(
        "policy_path"
    )

    if (
        not isinstance(policy_path, str)
        or not policy_path.strip()
    ):
        errors.append(
            "autonomy_policy_activation."
            "policy_path is missing"
        )
    elif not (ROOT / policy_path).exists():
        errors.append(
            f"autonomy policy path does not "
            f"exist: {policy_path}"
        )

    auto_advance = activation.get(
        "auto_advance"
    )

    parallel_scheduler = activation.get(
        "parallel_scheduler"
    )

    max_active = activation.get(
        "max_active_implementation_tasks"
    )

    if auto_advance not in ALLOWED_ACTIVATION:
        errors.append(
            f"invalid auto_advance state: "
            f"{auto_advance!r}"
        )

    if (
        parallel_scheduler
        not in ALLOWED_ACTIVATION
    ):
        errors.append(
            f"invalid parallel_scheduler state: "
            f"{parallel_scheduler!r}"
        )

    if parallel_scheduler == "ENABLED":
        if max_active != 2:
            errors.append(
                "parallel_scheduler=ENABLED "
                "requires "
                "max_active_implementation_tasks=2"
            )
    else:
        if max_active != 1:
            errors.append(
                "parallel_scheduler not ENABLED "
                "requires "
                "max_active_implementation_tasks=1"
            )

    if execution_mode == "BOUNDED":
        if auto_advance != "DISABLED":
            errors.append(
                "BOUNDED requires "
                "auto_advance=DISABLED"
            )

        if parallel_scheduler != "DISABLED":
            errors.append(
                "BOUNDED requires "
                "parallel_scheduler=DISABLED"
            )

    # ---------------------------------------------------------
    # Active workers / concurrency
    # ---------------------------------------------------------

    active_workers = require_list(
        run_state.get(
            "active_workers",
            [],
        ),
        "active_workers",
        errors,
    )

    executors: list[dict[str, Any]] = []
    reviewers: list[dict[str, Any]] = []

    for worker in active_workers:
        if not isinstance(worker, dict):
            errors.append(
                "active_workers entries "
                "must be mappings"
            )
            continue

        role = str(
            worker.get(
                "role",
                "",
            )
        ).upper()
        task_id = worker.get("task_id")

        if role == "EXECUTOR":
            executors.append(worker)

            if (
                task_id not in tasks
                and not (
                    execution_mode == "BOUNDED"
                    and task_id in bounded_task_ids
                )
            ):
                errors.append(
                    "active executor references "
                    f"unknown task {task_id}"
                )
        elif role == "REVIEWER":
            reviewers.append(worker)

            if not is_exact_sha(
                worker.get("exact_sha")
            ):
                errors.append(
                    "active Reviewer requires "
                    "an exact 40-character SHA"
                )
        else:
            errors.append(
                "active worker has invalid role: "
                f"{role!r}"
            )

    executor_task_ids = [
        str(worker.get("task_id"))
        for worker in executors
    ]

    duplicate_task_ids = [
        value
        for value, count in Counter(
            executor_task_ids
        ).items()
        if count > 1
    ]

    if duplicate_task_ids:
        errors.append(
            "duplicate active Executor "
            "task ownership: "
            + ", ".join(
                sorted(
                    duplicate_task_ids
                )
            )
        )

    executor_worktrees = [
        str(worker.get("worktree"))
        for worker in executors
        if worker.get("worktree")
    ]

    duplicate_worktrees = [
        value
        for value, count in Counter(
            executor_worktrees
        ).items()
        if count > 1
    ]

    if duplicate_worktrees:
        errors.append(
            "multiple active Executors "
            "share worktree: "
            + ", ".join(
                sorted(
                    duplicate_worktrees
                )
            )
        )

    executor_lanes = [
        str(worker.get("lane"))
        for worker in executors
        if worker.get("lane")
    ]

    duplicate_lanes = [
        value
        for value, count in Counter(
            executor_lanes
        ).items()
        if count > 1
    ]

    if duplicate_lanes:
        errors.append(
            "multiple active Executors "
            "share lane: "
            + ", ".join(
                sorted(
                    duplicate_lanes
                )
            )
        )

    if (
        isinstance(max_active, int)
        and len(executors) > max_active
    ):
        errors.append(
            f"{len(executors)} active Executors "
            f"exceeds "
            f"max_active_implementation_tasks="
            f"{max_active}"
        )

    if parallel_scheduler != "ENABLED":
        lane_b_executors = [
            worker
            for worker in executors
            if worker.get("lane")
            == "LANE_B"
        ]

        if lane_b_executors:
            errors.append(
                "LANE_B Executor exists while "
                "parallel_scheduler is not ENABLED"
            )

    for task_id in eligible_tasks:
        if task_id in executor_task_ids:
            errors.append(
                f"safe_frontier task {task_id} "
                "already has an active "
                "writing Executor"
            )

    active_task = run_state.get(
        "active_task",
        {},
    )

    if not isinstance(active_task, dict):
        errors.append(
            "active_task must be a mapping"
        )
        active_task = {}

    active_task_id = active_task.get("id")
    active_review = active_task.get("review")

    if execution_mode == "BOUNDED":
        if reviewers:
            errors.append(
                "BOUNDED must not schedule "
                "an internal Reviewer"
            )

        if (
            active_task_id is not None
            and active_task_id not in bounded_task_ids
        ):
            errors.append(
                "BOUNDED active_task is outside "
                "authorized_task_ids"
            )

        for worker in executors:
            if worker.get("task_id") not in bounded_task_ids:
                errors.append(
                    "BOUNDED Executor is outside "
                    "authorized_task_ids"
                )

        if active_review is not None:
            errors.append(
                "BOUNDED must not retain "
                "active_task.review"
            )
    else:
        reviewer_status = str(
            active_task.get(
                "reviewer_status",
                "",
            )
        ).upper()

        if reviewers and not isinstance(
            active_review,
            dict,
        ):
            errors.append(
                "active Reviewer requires "
                "active_task.review"
            )

        if reviewer_status in REVIEWER_STATUSES:
            if not isinstance(active_task_id, str):
                errors.append(
                    "active review requires "
                    "active_task.id"
                )

            if not isinstance(active_review, dict):
                errors.append(
                    "active review requires "
                    "active_task.review"
                )

        if active_review is not None:
            if not isinstance(active_review, dict):
                errors.append(
                    "active_task.review "
                    "must be a mapping"
                )
            else:
                review_scope = active_review.get("scope")
                review_sha = active_review.get("exact_sha")

                if review_scope not in REVIEW_SCOPES:
                    errors.append(
                        "invalid active_task.review."
                        f"scope: {review_scope!r}"
                    )

                if not is_exact_sha(review_sha):
                    errors.append(
                        "active_task.review requires "
                        "an exact 40-character SHA"
                    )

                matching_reviewers = [
                    worker
                    for worker in reviewers
                    if worker.get("task_id")
                    == active_task_id
                    and worker.get("exact_sha")
                    == review_sha
                ]

                if len(matching_reviewers) != 1:
                    errors.append(
                        "active_task.review requires "
                        "one matching active Reviewer"
                    )

                if review_scope == "INCREMENTAL_REPAIR":
                    for field in (
                        "prior_blocking_findings",
                        "repair_delta_paths",
                        "affected_invariants",
                    ):
                        values = require_list(
                            active_review.get(
                                field,
                                [],
                            ),
                            "active_task.review."
                            f"{field}",
                            errors,
                        )

                        if not values:
                            errors.append(
                                "INCREMENTAL_REPAIR requires "
                                f"{field}"
                            )

                reopened_areas = require_list(
                    active_review.get(
                        "reopened_areas",
                        [],
                    ),
                    "active_task.review."
                    "reopened_areas",
                    errors,
                )

                if reopened_areas:
                    reopening_evidence = require_list(
                        active_review.get(
                            "reopening_evidence",
                            [],
                        ),
                        "active_task.review."
                        "reopening_evidence",
                        errors,
                    )

                    if not reopening_evidence:
                        errors.append(
                            "reopened review areas require "
                            "reopening_evidence"
                        )

    # ---------------------------------------------------------
    # Governance-review hold
    # ---------------------------------------------------------

    consolidation = run_state.get(
        "governance_consolidation",
        {},
    )

    if (
        isinstance(consolidation, dict)
        and consolidation.get("status")
        == "READY_FOR_OWNER_REVIEW"
    ):
        expected_activation = (
            "DISABLED"
            if execution_mode == "BOUNDED"
            else "PENDING_OWNER_REVIEW"
        )

        if auto_advance != expected_activation:
            errors.append(
                "READY_FOR_OWNER_REVIEW requires "
                f"auto_advance={expected_activation}"
            )

        if parallel_scheduler != expected_activation:
            errors.append(
                "READY_FOR_OWNER_REVIEW requires "
                "parallel_scheduler="
                f"{expected_activation}"
            )

        if max_active != 1:
            errors.append(
                "READY_FOR_OWNER_REVIEW requires "
                "max_active_implementation_tasks=1"
            )
        slice_04_execution = run_state.get(
            "slice_04_execution",
            {},
        )

        if (
            not isinstance(
                slice_04_execution,
                dict,
            )
            or slice_04_execution.get(
                "status"
            )
            != "HELD_FOR_GOVERNANCE_REVIEW"
        ):
            errors.append(
                "READY_FOR_OWNER_REVIEW "
                "requires "
                "slice_04_execution="
                "HELD_FOR_GOVERNANCE_REVIEW"
            )

        for worker in executors:
            task = tasks.get(
                worker.get(
                    "task_id"
                )
            )

            if (
                isinstance(task, dict)
                and task.get("slice")
                == "SLICE-04"
            ):
                errors.append(
                    "SLICE-04 Executor exists "
                    "while governance review "
                    "hold is active"
                )

    # ---------------------------------------------------------
    # Bounded settled-worker history
    # ---------------------------------------------------------

    settled_history = require_list(
        run_state.get(
            "worker_settled_history",
            [],
        ),
        "worker_settled_history",
        errors,
    )

    if len(settled_history) > 10:
        errors.append(
            "worker_settled_history exceeds "
            "retention limit of 10"
        )

    # ---------------------------------------------------------
    # CI checkpoint consistency
    # ---------------------------------------------------------

    integration = run_state.get(
        "integration",
        {},
    )

    github_ci = run_state.get(
        "github_ci",
        {},
    )

    if (
        isinstance(integration, dict)
        and isinstance(github_ci, dict)
        and github_ci.get("result")
        == "PASS"
    ):
        checkpoint = str(
            integration.get(
                "last_verified_application_checkpoint",
                "",
            )
        )

        ci_commit = str(
            github_ci.get(
                "commit_sha",
                "",
            )
        )

        if checkpoint != ci_commit:
            errors.append(
                "last_verified_application_checkpoint "
                "does not match "
                "github_ci.commit_sha"
            )

        checkpoint_run = str(
            integration.get(
                "last_verified_application_ci_run",
                "",
            )
        )

        ci_run = str(
            github_ci.get(
                "run_id",
                "",
            )
        )

        if checkpoint_run != ci_run:
            errors.append(
                "last_verified_application_ci_run "
                "does not match "
                "github_ci.run_id"
            )

    # ---------------------------------------------------------
    # Derived reporting designation
    # ---------------------------------------------------------

    if not CURRENT_STATE_PATH.exists():
        errors.append(
            "CURRENT_STATE.md missing"
        )
    else:
        current_state = (
            CURRENT_STATE_PATH.read_text(
                encoding="utf-8"
            )
        )

        if (
            "DERIVED / NON-AUTHORITATIVE"
            not in current_state
        ):
            errors.append(
                "CURRENT_STATE.md must be "
                "marked DERIVED / "
                "NON-AUTHORITATIVE"
            )

    if not TRACEABILITY_PATH.exists():
        errors.append(
            "TRACEABILITY_STATUS.csv missing"
        )
    else:
        traceability = (
            TRACEABILITY_PATH.read_text(
                encoding="utf-8"
            )
        )

        if (
            "DERIVED / NON-AUTHORITATIVE"
            not in traceability
        ):
            errors.append(
                "TRACEABILITY_STATUS.csv "
                "must be marked DERIVED / "
                "NON-AUTHORITATIVE"
            )

    # ---------------------------------------------------------
    # No unresolved governance self-SHA placeholder
    # ---------------------------------------------------------

    run_state_text = RUN_STATE_PATH.read_text(
        encoding="utf-8"
    )

    if (
        "PENDING_GOVERNANCE_COMMIT"
        in run_state_text
    ):
        errors.append(
            "AUTONOMY_RUN_STATE contains "
            "unresolved "
            "PENDING_GOVERNANCE_COMMIT "
            "placeholder"
        )

    # ---------------------------------------------------------
    # Result
    # ---------------------------------------------------------

    if errors:
        print(
            "CONTROL PLANE VALIDATION: FAIL"
        )

        for error in errors:
            print(
                f" - {error}"
            )

        return 1

    print(
        "CONTROL PLANE VALIDATION: PASS"
    )

    print(
        f" - slices: {len(slices)}"
    )

    print(
        f" - tasks: {len(tasks)}"
    )

    print(
        " - frontier eligible tasks: "
        f"{len(eligible_tasks)}"
    )

    print(
        f" - active Executors: "
        f"{len(executors)}"
    )
    print(
        f" - execution_mode: "
        f"{execution_mode}"
    )

    print(
        " - max active implementation "
        f"tasks: {max_active}"
    )

    print(
        f" - auto_advance: "
        f"{auto_advance}"
    )

    print(
        f" - parallel_scheduler: "
        f"{parallel_scheduler}"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
