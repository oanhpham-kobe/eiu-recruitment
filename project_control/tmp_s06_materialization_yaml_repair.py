from pathlib import Path

# Repair TASK_REGISTRY duplicate branch key.
p=Path('project_control/TASK_REGISTRY.yaml')
s=p.read_text()
old='''    pre_task_checkpoint: checkpoint/pre-S06-001-001\n    branch: oanhpham-kobe/TASK-S06-001-master-data-lifecycle\n    branch: PENDING_AFTER_PROMPT_REVIEW\n'''
new='''    pre_task_checkpoint: checkpoint/pre-S06-001-001\n    branch: oanhpham-kobe/TASK-S06-001-master-data-lifecycle\n'''
if old not in s:
    raise SystemExit('duplicate branch block not found')
s=s.replace(old,new,1)
p.write_text(s)

# A task held behind materialization CI is not yet execution-eligible.
p=Path('project_control/AUTONOMY_RUN_STATE.yaml')
s=p.read_text()
old='''safe_frontier:\n  eligible_tasks: [TASK-S06-001]\n  skipped_due_to_dependency: []\n  materialization_frontier: [TASK-S06-001]\n  execution_hold: "TASK-S06-001 implementation materialization must pass exact-SHA Integration/Governance CI before branch execution"\n'''
new='''safe_frontier:\n  eligible_tasks: []\n  skipped_due_to_dependency: []\n  materialization_frontier: [TASK-S06-001]\n  execution_hold: "TASK-S06-001 implementation materialization must pass exact-SHA Integration/Governance CI before branch execution"\n'''
if old not in s:
    raise SystemExit('safe frontier materialization block not found')
s=s.replace(old,new,1)
p.write_text(s)
