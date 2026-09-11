from pathlib import Path

BASE = "0a2ccdfedc477f9766c9aaa03739d16a7ed83c01"
BRANCH = "oanhpham-kobe/TASK-S06-002-user-rbac-identity"
CHECKPOINT = "checkpoint/pre-S06-002-001"
PROMPT_TARGET = "f757e76f3f97077c608dab29bad45b8bd2126dc3"


def replace_one(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one match, got {count}")
    return text.replace(old, new, 1)

state_path = Path("project_control/AUTONOMY_RUN_STATE.yaml")
state = state_path.read_text(encoding="utf-8")
state = replace_one(state, "s06_002_planning:\n  status: PROMPT_REVIEW_PASS", "s06_002_planning:\n  status: IMPLEMENTATION_ACTIVE", "planning_status")
state = replace_one(state, '  implementation_hold: "Prompt/source reconciliation passed. Create immutable pre-task checkpoint and isolated implementation branch before any product/database mutation."', '  implementation_hold: "CLEARED — immutable pre-task checkpoint and isolated implementation branch are materialized at the exact validated baseline."', "implementation_hold")
old_impl = '''implementation_materialization:\n  task: TASK-S06-001\n  prompt_review: "PASS S06-001-PROMPT-REVIEW-002 @ 68d96b39e309ee6f1edbe6cf4031c10a583b0269"\n  source_reopen_required: false\n  prompt: project_control/prompts/SLICE-06_TASK-001_v2.md\n  checkpoint: checkpoint/pre-S06-001-001\n  branch: oanhpham-kobe/TASK-S06-001-master-data-lifecycle\n  baseline_sha: "0ec409915bdd00b61b1b7affdb77ec778c7c1dc7"\n  status: COMPLETE\n  current_candidate_sha: "9002c9be26c57a182494b9b0de46ae612f32d81e"\n  review_round: R3\n'''
new_impl = f'''implementation_materialization:\n  task: TASK-S06-002\n  prompt_review: "PASS S06-002-PROMPT-REVIEW-001 @ {PROMPT_TARGET}"\n  prompt_review_provenance: VERIFIED_FROM_OWNER_TRANSPORT\n  source_reopen_required: false\n  prompt: project_control/prompts/SLICE-06_TASK-002_v1.md\n  checkpoint: {CHECKPOINT}\n  branch: {BRANCH}\n  baseline_sha: "{BASE}"\n  status: COMPLETE\n  current_candidate_sha: PENDING\n  review_round: R0\n'''
state = replace_one(state, old_impl, new_impl, "implementation_materialization")
old_frontier = '''safe_frontier:\n  eligible_tasks:\n    - TASK-S06-002\n  skipped_due_to_dependency: []\n  materialization_frontier:\n    - TASK-S06-002\n  execution_hold: null\n\nstop_gate:\n  status: CLEAR\n  type: NONE\n  work_id: S06-002-PROMPT-REVIEW-001\n  target: "TASK-S06-002 prompt/source reconciliation @ f757e76f3f97077c608dab29bad45b8bd2126dc3"\n  reviewer: eiu-reviewer\n  source_reopen_required: false\n  resume_on: "Create immutable pre-task checkpoint and isolated implementation branch, then begin bounded S06-002 implementation."\n\nnext_action: "Create checkpoint/pre-S06-002-001 from this exact validated control state and create isolated implementation branch oanhpham-kobe/TASK-S06-002-user-rbac-identity. Then begin bounded implementation from the accepted prompt. Preserve boundaries: do not push/merge main, deploy Vercel, or apply connected Supabase migrations without explicit Owner authorization."'''
new_frontier = '''safe_frontier:\n  eligible_tasks: []\n  skipped_due_to_dependency: []\n  materialization_frontier: []\n  execution_hold: "TASK-S06-002 implementation is active on its isolated branch; no additional Slice-06 implementation frontier is materialized."\n\nstop_gate:\n  status: CLEAR\n  type: NONE\n  work_id: S06-002-IMPLEMENTATION-MATERIALIZATION-001\n  target: "TASK-S06-002 implementation baseline @ 0a2ccdfedc477f9766c9aaa03739d16a7ed83c01"\n  reviewer: eiu-reviewer\n  source_reopen_required: false\n  resume_on: "Implement the reviewed S06-002 contract on the isolated branch, verify locally/CI, then create exact candidate review gate before integration."\n\nnext_action: "Implement TASK-S06-002 on oanhpham-kobe/TASK-S06-002-user-rbac-identity from exact baseline 0a2ccdfedc477f9766c9aaa03739d16a7ed83c01. Preserve the reviewed scope and non-blocking observations. Do not push/merge main, deploy Vercel, or apply connected Supabase migrations without explicit Owner authorization."'''
state = replace_one(state, old_frontier, new_frontier, "frontier_active")
state_path.write_text(state, encoding="utf-8")

task_path = Path("project_control/TASK_REGISTRY.yaml")
tasks = task_path.read_text(encoding="utf-8")
tasks = replace_one(tasks, '    status: READY\n    lane: LANE_A\n    depends_on:\n      - TASK-S06-001\n    prompt: project_control/prompts/SLICE-06_TASK-002_v1.md', '    status: IN_PROGRESS\n    lane: LANE_A\n    depends_on:\n      - TASK-S06-001\n    prompt: project_control/prompts/SLICE-06_TASK-002_v1.md', "task_status")
tasks = replace_one(tasks, '    prompt_review_evidence: project_control/reviews/S06_002_PROMPT_REVIEW_OWNER_TRANSPORT_f757e76_v1.md\n    notes:', f'    prompt_review_evidence: project_control/reviews/S06_002_PROMPT_REVIEW_OWNER_TRANSPORT_f757e76_v1.md\n    implementation_baseline_sha: "{BASE}"\n    implementation_checkpoint: {CHECKPOINT}\n    implementation_branch: {BRANCH}\n    notes:', "task_materialization")
task_path.write_text(tasks, encoding="utf-8")

current = f'''# Current Implementation State — Derived Handoff Snapshot\n\n> **DERIVED / NON-AUTHORITATIVE REPORTING ONLY**\n> Runtime authority: `project_control/AUTONOMY_RUN_STATE.yaml`.\n> DAG/task/slice authority: `project_control/TASK_REGISTRY.yaml` and `project_control/SLICE_REGISTRY.yaml`.\n> Exact code/history authority: Git.\n\n## SLICE-06 / TASK-S06-001 — ACCEPTED\n\nTASK-S06-001 remains accepted at `59be9b2c92906065b8e4baa902fcec1d4cbefa12` / `checkpoint/S06-001-accepted-001`.\n\n## SLICE-06 / TASK-S06-002 — IMPLEMENTATION ACTIVE\n\n- Prompt review: `PASS`, work ID `S06-002-PROMPT-REVIEW-001`, exact reviewed SHA `{PROMPT_TARGET}`.\n- `SOURCE_REOPEN_REQUIRED=false`.\n- Review provenance: `VERIFIED_FROM_OWNER_TRANSPORT`.\n- Immutable pre-task checkpoint: `{CHECKPOINT} @ {BASE}`.\n- Isolated implementation branch: `{BRANCH}`.\n- Exact implementation baseline: `{BASE}`.\n- Task registry status: `IN_PROGRESS`.\n- Current candidate: not yet materialized.\n\n## Next action\n\nImplement the bounded backend/security contract on the isolated branch, incorporating the reviewer observations on lifecycle-writer serialization, minimum-safe permission projections, Unit-history lock ordering, and stable non-leaking adapter errors. Verify with repository-supported local/CI Supabase workflows before producing an exact candidate review gate.\n\n## Boundaries\n\n- Do not push/merge `main` without explicit Owner authorization.\n- Do not deploy Vercel without explicit Owner authorization.\n- Do not apply migrations to connected Supabase without explicit Owner authorization.\n'''
Path("project_control/CURRENT_STATE.md").write_text(current, encoding="utf-8")
