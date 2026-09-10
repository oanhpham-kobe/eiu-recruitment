from pathlib import Path

# Repair TASK_REGISTRY duplicate branch key when still present.
p=Path('project_control/TASK_REGISTRY.yaml')
s=p.read_text()
duplicate='''    pre_task_checkpoint: checkpoint/pre-S06-001-001\n    branch: oanhpham-kobe/TASK-S06-001-master-data-lifecycle\n    branch: PENDING_AFTER_PROMPT_REVIEW\n'''
clean='''    pre_task_checkpoint: checkpoint/pre-S06-001-001\n    branch: oanhpham-kobe/TASK-S06-001-master-data-lifecycle\n'''
if duplicate in s:
    s=s.replace(duplicate,clean,1)
elif clean not in s:
    raise SystemExit('expected S06-001 branch block missing')
p.write_text(s)

# A task held behind materialization CI is not yet execution-eligible.
p=Path('project_control/AUTONOMY_RUN_STATE.yaml')
s=p.read_text()
held='''safe_frontier:\n  eligible_tasks: [TASK-S06-001]\n  skipped_due_to_dependency: []\n  materialization_frontier: [TASK-S06-001]\n  execution_hold: "TASK-S06-001 implementation materialization must pass exact-SHA Integration/Governance CI before branch execution"\n'''
clean_frontier='''safe_frontier:\n  eligible_tasks: []\n  skipped_due_to_dependency: []\n  materialization_frontier: [TASK-S06-001]\n  execution_hold: "TASK-S06-001 implementation materialization must pass exact-SHA Integration/Governance CI before branch execution"\n'''
if held in s:
    s=s.replace(held,clean_frontier,1)
elif clean_frontier not in s:
    raise SystemExit('expected S06-001 materialization frontier missing')
p.write_text(s)
