from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]

def read(path):
    return (ROOT / path).read_text(encoding="utf-8")

def write(path, text):
    (ROOT / path).write_text(text.rstrip() + "\n", encoding="utf-8")

def replace_once(text, old, new, label):
    if old not in text:
        if new in text:
            return text
        raise SystemExit(f"missing expected anchor: {label}")
    if text.count(old) != 1:
        raise SystemExit(f"anchor not unique: {label}")
    return text.replace(old, new, 1)

def set_task_status(text, task_id, status):
    pat = re.compile(rf"(^  {re.escape(task_id)}:\n.*?^    status: )(\S+)", re.M | re.S)
    m = pat.search(text)
    if not m:
        raise SystemExit(f"task block/status not found: {task_id}")
    return text[:m.start(2)] + status + text[m.end(2):]

# TASK_REGISTRY — close bounded DS DAG, keep S04-004 blocked until checkpoint exists.
p = "project_control/TASK_REGISTRY.yaml"
t = read(p)
t = replace_once(t, "current_task: TASK-DS-001", "current_task: TASK-DS-006", "task current_task")
for task in ["TASK-DS-001","TASK-DS-002","TASK-DS-003","TASK-DS-004","TASK-DS-005","TASK-DS-006"]:
    t = set_task_status(t, task, "DONE")
t = set_task_status(t, "TASK-S04-004", "BLOCKED")
write(p, t)

# SLICE_REGISTRY — DS is complete, current task remains the completed exit gate for Phase A.
p = "project_control/SLICE_REGISTRY.yaml"
t = read(p)
t = replace_once(
    t,
    "SLICE-DS: {name: Production Design System Hardening / Responsive Convergence, status: IN_PROGRESS, current_task: TASK-DS-001}",
    "SLICE-DS: {name: Production Design System Hardening / Responsive Convergence, status: DONE, current_task: TASK-DS-006}",
    "slice ds state",
)
write(p, t)

# AUTONOMY_RUN_STATE — verified implementation, checkpoint still pending; no executable frontier yet.
p = "project_control/AUTONOMY_RUN_STATE.yaml"
t = read(p)
t = replace_once(t, "  status: IN_PROGRESS\n  owner_sequencing_decision:", "  status: VERIFIED_PENDING_CHECKPOINT\n  owner_sequencing_decision:", "ds runtime status")
if "  verified_web_candidate_sha:" not in t:
    t = replace_once(t, "  exit_checkpoint: checkpoint/design-system-production-ready-001\n", "  exit_checkpoint: checkpoint/design-system-production-ready-001\n  verified_web_candidate_sha: \"d473b11217d6f6b2fc8c83fec9029e649f1b05a7\"\n  verification_evidence:\n    - \"DS-006 seven-width browser acceptance: PASS (360/390/430/768/1024/1280/1440)\"\n    - \"design:check: PASS\"\n    - \"lint: PASS\"\n    - \"typecheck: PASS\"\n    - \"build: PASS before focused post-review repairs; post-review production repairs reverified by focused lint/typecheck/browser gates\"\n    - \"web regression baseline: 263/265 PASS; two stale shell tests repaired and focused reverified\"\n    - \"CandidateShell landmark repair focused gate: PASS (run 34171263268)\"\n    - \"primitive keyboard/stacked-overlay focused gate: PASS (run 34171925884)\"\n", "ds exit checkpoint")
t = re.sub(r"safe_frontier:\n  eligible_tasks:\n(?:    - .*\n)*  skipped_due_to_dependency:\n(?:    - .*\n)*", "safe_frontier:\n  eligible_tasks: []\n  skipped_due_to_dependency:\n    - TASK-S04-004\n", t, count=1)
t = re.sub(r'^next_action: .*$', 'next_action: "Create and verify immutable checkpoint/design-system-production-ready-001 at the Phase-A closure SHA. Keep TASK-S04-004 BLOCKED until that checkpoint exists; then perform Phase-B release."', t, count=1, flags=re.M)
write(p, t)

# EVIDENCE_INDEX — append compact durable evidence once.
p = "project_control/EVIDENCE_INDEX.yaml"
t = read(p)
if "DESIGN-SYSTEM-HARDENING-001:" not in t:
    t += '''\n\n  DESIGN-SYSTEM-HARDENING-001:\n    operation: PRODUCTION_DESIGN_SYSTEM_HARDENING\n    status: VERIFIED_PENDING_CHECKPOINT\n    source_reopen_required: false\n    baseline_sha: "8897d08f01b9f4738500eecfd6170dc0a9c77f54"\n    pre_hardening_checkpoint: checkpoint/pre-design-system-hardening-001\n    verified_web_candidate_sha: "d473b11217d6f6b2fc8c83fec9029e649f1b05a7"\n    tasks:\n      - TASK-DS-001\n      - TASK-DS-002\n      - TASK-DS-003\n      - TASK-DS-004\n      - TASK-DS-005\n      - TASK-DS-006\n    verification:\n      design_contract: PASS\n      lint: PASS\n      typecheck: PASS\n      seven_width_browser_acceptance: PASS\n      candidate_landmark_repair_run: "34171263268 PASS"\n      primitive_interaction_repair_run: "34171925884 PASS"\n      database_required: false\n    checkpoint: PENDING_PHASE_A_REF_CREATION\n'''
write(p, t)

# CURRENT_STATE — derived snapshot only.
p = "project_control/CURRENT_STATE.md"
t = read(p)
old = "- Current authoritative frontier is `TASK-DS-001`; `TASK-S04-004 = BLOCKED` until `TASK-DS-006 = DONE` and `checkpoint/design-system-production-ready-001` exists."
new = "- `TASK-DS-001..006 = DONE`. Production Design-System hardening implementation and focused/browser verification are complete. `TASK-S04-004` remains `BLOCKED` only until immutable `checkpoint/design-system-production-ready-001` is created and verified in Phase B."
t = replace_once(t, old, new, "current-state frontier")
t = replace_once(t, "6. confirm `plan_reconciliation.status = VERIFIED`, `design_system_hardening.status = IN_PROGRESS`, `TASK-DS-001 = READY`, and `safe_frontier = [TASK-DS-001]`;", "6. confirm `plan_reconciliation.status = VERIFIED`, `design_system_hardening.status = VERIFIED_PENDING_CHECKPOINT`, `TASK-DS-001..006 = DONE`, and `safe_frontier = []`;", "resume status")
t = replace_once(t, "## Next action\n\nExecute `TASK-DS-001` from `checkpoint/pre-design-system-hardening-001`, then advance through the bounded Design-System Hardening DAG. Do not start S04-004 application implementation until DS-006 is accepted and `checkpoint/design-system-production-ready-001` is verified.", "## Next action\n\nCreate and verify immutable `checkpoint/design-system-production-ready-001` at the exact Phase-A closure SHA. Then perform the explicit Phase-B control-plane release of `TASK-S04-004` and start it from that checkpoint.", "next action snapshot")
write(p, t)

# CHANGELOG — compact closure narrative.
p = "project_control/CHANGELOG_IMPLEMENTATION.md"
t = read(p)
if "Design-System production hardening implementation complete" not in t:
    t += '''\n\n## 2026-09-08 — Design-System production hardening implementation complete\n\n- Completed bounded TASK-DS-001..006 without reopening frozen Product/Business/Design authority.\n- Converged runtime design tokens, Auth/Candidate/Internal shell responsibilities, responsive Internal navigation, bounded shared UI primitives, existing responsive production surfaces, static production design-contract validation, and seven-width browser acceptance.\n- Preserved the accepted Application/Interview backend contracts; no Supabase migration/RLS/RPC changes were made.\n- Final self-review repaired Candidate landmark ownership plus StatusMenu keyboard semantics and re-entrant/topmost overlay focus/lock behavior.\n- Focused verification remained impact-scoped; unrelated database verification was not rerun.\n- Phase A intentionally keeps TASK-S04-004 blocked until immutable checkpoint/design-system-production-ready-001 is created and verified.\n'''
write(p, t)

print("DS Phase-A control-plane patch applied")
