from pathlib import Path

target = '5abbb5181405e0f5a468176edd93db8226a3efd5'

# AUTONOMY_RUN_STATE
p = Path('project_control/AUTONOMY_RUN_STATE.yaml')
s = p.read_text()
s = s.replace('  status: PROMPT_REVIEW_PREPARATION\n', '  status: WAITING_EXTERNAL_REVIEW\n', 1)
s = s.replace('  prompt_review_target_sha: PENDING_INTEGRATION_MATERIALIZATION\n', f'  prompt_review_target_sha: "{target}"\n', 1)
s = s.replace('    status: PREPARING\n    reviewed_sha: PENDING_INTEGRATION_MATERIALIZATION\n', f'    status: WAITING_EXTERNAL_REVIEW\n    reviewed_sha: "{target}"\n', 1)
s = s.replace('  execution_hold: "TASK-S06-001 independent pre-implementation prompt/source review preparation"\n', '  execution_hold: "TASK-S06-001 independent pre-implementation prompt/source review"\n', 1)
old_gate = '''stop_gate:
  status: PREPARING_EXTERNAL_REVIEW
  type: OMP_PROMPT_REVIEW_PREPARATION
  work_id: S06-001-PROMPT-REVIEW-001
  target: project_control/prompts/SLICE-06_TASK-001_v1.md
  reviewed_sha: PENDING_INTEGRATION_MATERIALIZATION
  reviewer: eiu-reviewer
  verdict: PENDING
  source_reopen_required: PENDING
  resume_on: "freeze exact integration prompt target, then PASS + SOURCE_REOPEN_REQUIRED=false from independent eiu-reviewer"

next_action: "Materialize Slice-05 closure and TASK-S06-001 prompt/planning on integration, validate control CI, then persist exact-SHA prompt-review handoff and enter WAITING_EXTERNAL_REVIEW. Do not create the risky S06-001 implementation branch/checkpoint until prompt review PASS. Do not merge/push main, deploy Vercel, or apply connected Supabase migrations without explicit Owner authorization."
'''
new_gate = f'''stop_gate:
  status: WAITING_EXTERNAL_REVIEW
  type: OMP_PROMPT_REVIEW
  work_id: S06-001-PROMPT-REVIEW-001
  target: "project_control/prompts/SLICE-06_TASK-001_v1.md @ {target}"
  reviewed_sha: "{target}"
  reviewer: eiu-reviewer
  verdict: PENDING
  source_reopen_required: PENDING
  handoff_package_requirement: SATISFIED
  handoff_package: project_control/reviews/S06_001_PROMPT_REVIEW_GATE_5abbb51_v1.md
  materialization_integration_ci: "34488858134 PASS"
  materialization_governance_ci: "34488858173 PASS"
  resume_on: "PASS + SOURCE_REOPEN_REQUIRED=false for exact S06-001 prompt target"

next_action: "Transport project_control/reviews/S06_001_PROMPT_REVIEW_GATE_5abbb51_v1.md to independent OMP eiu-reviewer for exact prompt target 5abbb5181405e0f5a468176edd93db8226a3efd5. On PASS + SOURCE_REOPEN_REQUIRED=false, verify returned evidence coordinates if available, create immutable pre-S06-001 checkpoint and isolated implementation branch from the accepted planning baseline, then execute the reviewed prompt. Do not merge/push main, deploy Vercel, or apply connected Supabase migrations without explicit Owner authorization."
'''
if old_gate not in s:
    raise SystemExit('old prompt gate block missing')
s = s.replace(old_gate, new_gate, 1)
# Record closure/materialization control verification inside closure block once.
needle = '  composition_verdict: "PASS — cross-task composition, security/privacy, Current Round/status/final decision, concurrency/lifecycle, design/UX/accessibility, and slice completeness"\n'
if 'closure_transition_sha:' not in s:
    s = s.replace(needle, needle + f'  closure_transition_sha: "{target}"\n  closure_transition_integration_ci: "34488858134 PASS"\n  closure_transition_governance_ci: "34488858173 PASS"\n', 1)
p.write_text(s)

# TASK_REGISTRY
p = Path('project_control/TASK_REGISTRY.yaml')
s = p.read_text()
start = s.index('  TASK-S06-001:\n')
block = s[start:]
block = block.replace('    prompt_review_status: PENDING\n', f'    prompt_review_status: "WAITING_EXTERNAL_REVIEW (S06-001-PROMPT-REVIEW-001 @ {target})"\n', 1)
block = block.replace('    prompt_review_evidence: PENDING\n', '    prompt_review_evidence: project_control/reviews/S06_001_PROMPT_REVIEW_GATE_5abbb51_v1.md\n', 1)
s = s[:start] + block
p.write_text(s)

# EVIDENCE_INDEX
p = Path('project_control/EVIDENCE_INDEX.yaml')
s = p.read_text()
if '  S06-001-PROMPT-REVIEW-GATE-001:\n' not in s:
    s += f'''\n  S06-001-PROMPT-REVIEW-GATE-001:
    task: TASK-S06-001
    operation: INDEPENDENT_PRE_IMPLEMENTATION_PROMPT_SOURCE_REVIEW_GATE
    status: WAITING_EXTERNAL_REVIEW
    reviewed_sha: "{target}"
    reviewer: eiu-reviewer
    prompt: project_control/prompts/SLICE-06_TASK-001_v1.md
    handoff: project_control/reviews/S06_001_PROMPT_REVIEW_GATE_5abbb51_v1.md
    producer_reconciliation: project_control/reviews/S06_001_PROMPT_PRODUCER_RECONCILIATION_v1.md
    materialization_integration_ci: "34488858134 PASS"
    materialization_governance_ci: "34488858173 PASS"
    result: PENDING
    source_reopen_required: PENDING
'''
p.write_text(s)

# CURRENT_STATE
p = Path('project_control/CURRENT_STATE.md')
s = p.read_text()
s = s.replace('## SLICE-06 — IN PROGRESS / S06-001 PROMPT REVIEW PREPARATION', '## SLICE-06 — IN PROGRESS / S06-001 WAITING INDEPENDENT PROMPT REVIEW', 1)
s = s.replace('Producer source reconciliation: PASS, no source reopen.\n', f'Producer source reconciliation: PASS, no source reopen.\n\nExact independent prompt-review target: `{target}`.\n\n- materialization Integration CI `34488858134`: PASS\n- materialization Governance CI `34488858173`: PASS\n- reviewer: `eiu-reviewer`\n- handoff: `project_control/reviews/S06_001_PROMPT_REVIEW_GATE_5abbb51_v1.md`\n', 1)
s = s.replace('TASK-S06-001 remains `PLANNED`; no implementation branch/checkpoint is created before independent prompt review PASS.', 'TASK-S06-001 remains `PLANNED`; live state is `WAITING_EXTERNAL_REVIEW`. No implementation branch/checkpoint is created before independent prompt review PASS.')
p.write_text(s)
