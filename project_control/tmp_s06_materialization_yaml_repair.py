from pathlib import Path
p=Path('project_control/TASK_REGISTRY.yaml')
s=p.read_text()
old='''    pre_task_checkpoint: checkpoint/pre-S06-001-001\n    branch: oanhpham-kobe/TASK-S06-001-master-data-lifecycle\n    branch: PENDING_AFTER_PROMPT_REVIEW\n'''
new='''    pre_task_checkpoint: checkpoint/pre-S06-001-001\n    branch: oanhpham-kobe/TASK-S06-001-master-data-lifecycle\n'''
if old not in s:
    raise SystemExit('duplicate branch block not found')
s=s.replace(old,new,1)
p.write_text(s)
