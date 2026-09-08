from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]

def read(path): return (ROOT / path).read_text(encoding="utf-8")
def write(path, text): (ROOT / path).write_text(text.rstrip()+"\n", encoding="utf-8")
def once(text, old, new, label):
    if old not in text:
        if new in text: return text
        raise SystemExit(f"missing anchor: {label}")
    if text.count(old) != 1: raise SystemExit(f"non-unique anchor: {label}")
    return text.replace(old,new,1)
def set_task_status(text, task_id, status):
    pat=re.compile(rf"(^  {re.escape(task_id)}:\n.*?^    status: )(\S+)", re.M|re.S)
    m=pat.search(text)
    if not m: raise SystemExit(f"task status missing: {task_id}")
    return text[:m.start(2)]+status+text[m.end(2):]

p="project_control/TASK_REGISTRY.yaml"; t=read(p)
t=once(t,"current_slice: SLICE-DS","current_slice: SLICE-04","task current_slice")
t=once(t,"current_task: TASK-DS-006","current_task: TASK-S04-004","task current_task")
t=set_task_status(t,"TASK-S04-004","READY")
write(p,t)

p="project_control/SLICE_REGISTRY.yaml"; t=read(p)
t=once(t,"current_slice: SLICE-DS","current_slice: SLICE-04","slice current_slice")
write(p,t)

p="project_control/AUTONOMY_RUN_STATE.yaml"; t=read(p)
t=once(t,"  status: VERIFIED_PENDING_CHECKPOINT\n  owner_sequencing_decision:","  status: VERIFIED\n  owner_sequencing_decision:","ds status")
if "  accepted_checkpoint_sha:" not in t:
    t=once(t,'  exit_checkpoint: checkpoint/design-system-production-ready-001\n','  exit_checkpoint: checkpoint/design-system-production-ready-001\n  accepted_checkpoint_sha: "cb42f0fe301fba70cdc32704d605872b05d12515"\n  final_web_acceptance_run: "34172591716 PASS"\n  final_governance_ci_run: "34172664420 PASS"\n',"checkpoint evidence")
t=t.replace('  verified_web_candidate_sha: "d473b11217d6f6b2fc8c83fec9029e649f1b05a7"','  verified_web_candidate_sha: "cb42f0fe301fba70cdc32704d605872b05d12515"')
t=re.sub(r"safe_frontier:\n  eligible_tasks: \[\]\n  skipped_due_to_dependency:\n    - TASK-S04-004\n","safe_frontier:\n  eligible_tasks:\n    - TASK-S04-004\n  skipped_due_to_dependency: []\n",t,count=1)
t=re.sub(r'^next_action: .*$', 'next_action: "Dispatch TASK-S04-004 from checkpoint/design-system-production-ready-001 on a fresh task branch. Preserve accepted backend contracts and stop at the ChatGPT-reviewed exact candidate SHA for independent OMP review."', t, count=1, flags=re.M)
write(p,t)

p="project_control/EVIDENCE_INDEX.yaml"; t=read(p)
# only mutate the DS hardening block.
start=t.find("  DESIGN-SYSTEM-HARDENING-001:")
if start < 0: raise SystemExit("DS evidence block missing")
block=t[start:]
block=block.replace("    status: VERIFIED_PENDING_CHECKPOINT","    status: VERIFIED",1)
block=block.replace('    verified_web_candidate_sha: "d473b11217d6f6b2fc8c83fec9029e649f1b05a7"','    verified_web_candidate_sha: "cb42f0fe301fba70cdc32704d605872b05d12515"',1)
block=block.replace("    checkpoint: PENDING_PHASE_A_REF_CREATION",'    checkpoint: "checkpoint/design-system-production-ready-001 @ cb42f0fe301fba70cdc32704d605872b05d12515"\n    final_web_acceptance_run: "34172591716 PASS"\n    final_governance_ci_run: "34172664420 PASS"',1)
t=t[:start]+block
write(p,t)

p="project_control/CURRENT_STATE.md"; t=read(p)
t=once(t,"- `TASK-DS-001..006 = DONE`. Production Design-System hardening implementation and focused/browser verification are complete. `TASK-S04-004` remains `BLOCKED` only until immutable `checkpoint/design-system-production-ready-001` is created and verified in Phase B.","- `TASK-DS-001..006 = DONE` and `checkpoint/design-system-production-ready-001` is verified at `cb42f0fe301fba70cdc32704d605872b05d12515`. `TASK-S04-004 = READY` and is the sole safe-frontier task.","snapshot frontier")
t=once(t,"6. confirm `plan_reconciliation.status = VERIFIED`, `design_system_hardening.status = VERIFIED_PENDING_CHECKPOINT`, `TASK-DS-001..006 = DONE`, and `safe_frontier = []`;","6. confirm `plan_reconciliation.status = VERIFIED`, `design_system_hardening.status = VERIFIED`, `TASK-DS-001..006 = DONE`, `TASK-S04-004 = READY`, and `safe_frontier = [TASK-S04-004]`;","resume status")
t=once(t,"## Next action\n\nCreate and verify immutable `checkpoint/design-system-production-ready-001` at the exact Phase-A closure SHA. Then perform the explicit Phase-B control-plane release of `TASK-S04-004` and start it from that checkpoint.","## Next action\n\nCreate a fresh S04-004 task branch from `checkpoint/design-system-production-ready-001`, implement the released v3 prompt over the accepted trusted commands, self-review and run focused/browser verification, then stop at an exact candidate SHA for independent OMP review.","snapshot next")
write(p,t)

p="project_control/CHANGELOG_IMPLEMENTATION.md"; t=read(p)
if "Design-System production-ready checkpoint and S04-004 release" not in t:
    t += '''\n\n## 2026-09-08 — Design-System production-ready checkpoint and S04-004 release\n\n- Final exact-SHA web acceptance on `cb42f0fe301fba70cdc32704d605872b05d12515`: run `34172591716` PASS (audit, design contract, lint, typecheck, build, full web regression, seven-width browser acceptance).\n- Exact Phase-A Governance CI `34172664420`: PASS.\n- Created immutable `checkpoint/design-system-production-ready-001` at `cb42f0fe301fba70cdc32704d605872b05d12515`.\n- Released `TASK-S04-004` to READY as the sole safe-frontier task. No canonical source, SQL, RLS, migration, or accepted RPC behavior was changed by this release.\n'''
write(p,t)
print("DS Phase-B S04 release applied")
