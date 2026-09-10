from pathlib import Path

TARGET = '68d96b39e309ee6f1edbe6cf4031c10a583b0269'
HANDOFF = 'project_control/reviews/S06_001_PROMPT_R2_REVIEW_GATE_68d96b3_v1.md'

# AUTONOMY_RUN_STATE
p = Path('project_control/AUTONOMY_RUN_STATE.yaml')
s = p.read_text()
s = s.replace('  current_prompt_review_target_sha: PENDING_S06_001_R2_MATERIALIZATION\n', f'  current_prompt_review_target_sha: "{TARGET}"\n', 1)
idx = s.index('slice_06_planning:\n')
pre, tail = s[:idx], s[idx:]
tail = tail.replace('  status: PROMPT_REPAIR_R2_PREPARATION\n', '  status: WAITING_EXTERNAL_REVIEW\n', 1)
tail = tail.replace('  prompt_review_target_sha: PENDING_R2_MATERIALIZATION\n', f'  prompt_review_target_sha: "{TARGET}"\n', 1)
tail = tail.replace('    status: COMPLETE_PENDING_MATERIALIZATION\n', '    status: MATERIALIZED\n', 1)
tail = tail.replace('    work_id: S06-001-PROMPT-REVIEW-002\n    reviewer: eiu-reviewer\n    status: PREPARING\n    reviewed_sha: PENDING_R2_MATERIALIZATION\n', f'    work_id: S06-001-PROMPT-REVIEW-002\n    reviewer: eiu-reviewer\n    status: WAITING_EXTERNAL_REVIEW\n    reviewed_sha: "{TARGET}"\n', 1)
tail = tail.replace('  execution_hold: "TASK-S06-001 prompt v2 repair materialization and independent rereview preparation"\n', '  execution_hold: "TASK-S06-001 independent exact-SHA prompt rereview R2"\n', 1)
old_gate = '''stop_gate:
  status: PREPARING_EXTERNAL_REVIEW
  type: OMP_PROMPT_REREVIEW_PREPARATION
  work_id: S06-001-PROMPT-REVIEW-002
  target: project_control/prompts/SLICE-06_TASK-001_v2.md
  reviewed_sha: PENDING_R2_MATERIALIZATION
  reviewer: eiu-reviewer
  verdict: PENDING
  source_reopen_required: PENDING
  resume_on: "materialize prompt v2 on integration, validate control CI, persist exact-SHA rereview handoff, then PASS + SOURCE_REOPEN_REQUIRED=false"

next_action: "Materialize bounded TASK-S06-001 prompt v2 repair on integration, validate exact materialization CI, then persist and transport an exact-SHA S06-001-PROMPT-REVIEW-002 handoff to independent OMP eiu-reviewer. Do not create the S06-001 implementation branch/checkpoint before rereview PASS. Do not merge/push main, deploy Vercel, or apply connected Supabase migrations without explicit Owner authorization."
'''
new_gate = f'''stop_gate:
  status: WAITING_EXTERNAL_REVIEW
  type: OMP_PROMPT_REREVIEW
  work_id: S06-001-PROMPT-REVIEW-002
  target: "project_control/prompts/SLICE-06_TASK-001_v2.md @ {TARGET}"
  reviewed_sha: "{TARGET}"
  reviewer: eiu-reviewer
  verdict: PENDING
  source_reopen_required: PENDING
  handoff_package_requirement: SATISFIED
  handoff_package: {HANDOFF}
  materialization_integration_ci: "34491648323 PASS"
  materialization_governance_ci: "34491648300 PASS"
  resume_on: "PASS + SOURCE_REOPEN_REQUIRED=false for exact repaired prompt v2 target"

next_action: "Transport {HANDOFF} to independent OMP eiu-reviewer for exact prompt v2 target {TARGET}. On PASS + SOURCE_REOPEN_REQUIRED=false, verify returned evidence coordinates if available, create immutable pre-S06-001 checkpoint and isolated implementation branch from the accepted reviewed planning baseline, then execute only the reviewed v2 prompt. Do not merge/push main, deploy Vercel, or apply connected Supabase migrations without explicit Owner authorization."
'''
if old_gate not in tail:
    raise SystemExit('R2 preparation stop gate missing')
tail = tail.replace(old_gate, new_gate, 1)
p.write_text(pre + tail)

# TASK_REGISTRY
p = Path('project_control/TASK_REGISTRY.yaml')
s = p.read_text()
idx = s.index('  TASK-S06-001:\n')
pre, tail = s[:idx], s[idx:]
tail = tail.replace('    prompt_review_status: "R1_BLOCKERS_REPAIRED_PREPARING_R2"\n', f'    prompt_review_status: "WAITING_EXTERNAL_REVIEW (S06-001-PROMPT-REVIEW-002 @ {TARGET})"\n', 1)
tail = tail.replace('    prompt_review_evidence: project_control/reviews/S06_001_PROMPT_REPAIR_RESPONSE_v2.md\n', f'    prompt_review_evidence: {HANDOFF}\n', 1)
p.write_text(pre + tail)

# EVIDENCE_INDEX
p = Path('project_control/EVIDENCE_INDEX.yaml')
s = p.read_text()
idx = s.index('  S06-001-PROMPT-REPAIR-V2-001:\n')
pre, tail = s[:idx], s[idx:]
tail = tail.replace('    status: PREPARING_R2_MATERIALIZATION\n', '    status: MATERIALIZED\n', 1)
if '    materialized_sha:' not in tail.split('\n  ', 1)[0]:
    tail = tail.replace('    next_review: S06-001-PROMPT-REVIEW-002\n', f'    materialized_sha: "{TARGET}"\n    materialization_integration_ci: "34491648323 PASS"\n    materialization_governance_ci: "34491648300 PASS"\n    next_review: S06-001-PROMPT-REVIEW-002\n', 1)
s = pre + tail
if '  S06-001-PROMPT-REVIEW-R2-GATE-001:\n' not in s:
    s += f'''\n  S06-001-PROMPT-REVIEW-R2-GATE-001:
    task: TASK-S06-001
    operation: INDEPENDENT_BOUNDED_PROMPT_REREVIEW
    status: WAITING_EXTERNAL_REVIEW
    reviewed_sha: "{TARGET}"
    reviewer: eiu-reviewer
    prompt: project_control/prompts/SLICE-06_TASK-001_v2.md
    repair_evidence: project_control/reviews/S06_001_PROMPT_REPAIR_RESPONSE_v2.md
    handoff: {HANDOFF}
    r1_blockers:
      - S06-PROMPT-01_IDEMPOTENCY_CONTRACT
      - S06-PROMPT-02_DELETE_INACTIVATE_EXPECTED_VERSION
    materialization_integration_ci: "34491648323 PASS"
    materialization_governance_ci: "34491648300 PASS"
    result: PENDING
    source_reopen_required: PENDING
'''
p.write_text(s)

# CURRENT_STATE
Path('project_control/CURRENT_STATE.md').write_text(f'''# Current Implementation State — Derived Handoff Snapshot

> **DERIVED / NON-AUTHORITATIVE REPORTING ONLY**
>
> Runtime authority: `project_control/AUTONOMY_RUN_STATE.yaml`.
> DAG/task/slice authority: `project_control/TASK_REGISTRY.yaml` and `project_control/SLICE_REGISTRY.yaml`.
> Exact code/history authority: Git.

## SLICE-05 — DONE

TASK-S05-001 and TASK-S05-002 are accepted; Slice-05 closing composition review passed with no source reopen.

## SLICE-06 / TASK-S06-001 — WAITING INDEPENDENT PROMPT R2

R1 target `5abbb5181405e0f5a468176edd93db8226a3efd5` received `BLOCKING_REPAIR / SOURCE_REOPEN_REQUIRED=false` for two bounded prompt defects:

1. missing idempotency/retry-replay contract;
2. missing expected-version validation for delete/inactivate.

Both are repaired in:

`project_control/prompts/SLICE-06_TASK-001_v2.md`

Exact R2 reviewed target:

`{TARGET}`

Materialization evidence:

- Integration CI `34491648323`: PASS
- Governance CI `34491648300`: PASS
- changed scope: control/state + prompt v2 + repair response only; no product code

R2 reviewer: `eiu-reviewer`

R2 handoff:

`{HANDOFF}`

TASK-S06-001 remains `PLANNED`. No implementation branch or pre-task checkpoint exists before R2 PASS.

Reviewer-reported R1 durable evidence coordinates were not GitHub-visible when Coordinator checked; R1 verdict is recorded from Owner transport without a false durable-verification claim.

## Do not cross

- Do not implement S06-001 before exact-SHA R2 independent prompt review PASS.
- Do not merge/push `main`.
- Do not deploy Vercel.
- Do not apply migrations to connected Supabase DEV/production without explicit Owner authorization.
''')
