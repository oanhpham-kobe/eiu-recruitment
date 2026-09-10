from pathlib import Path

accepted = "fe556dda76ebeda7107bcb9310cbaf338b30fc29"
candidate = "f4e1a04b59aef92aa55245c451386e0c0cfe3813"

# TASK_REGISTRY
p = Path("project_control/TASK_REGISTRY.yaml")
s = p.read_text()
start = s.index("  TASK-S05-002:\n")
block = s[start:]
block = block.replace("    status: READY\n", "    status: DONE\n", 1)
old = "    pre_task_checkpoint: checkpoint/pre-S05-002-001\n    notes: "
new = f'''    pre_task_checkpoint: checkpoint/pre-S05-002-001
    implementation_candidate_sha: "{candidate}"
    implementation_sha: "{accepted}"
    review_status: "PASS (S05-002-FINAL-INTEGRATION-EQUIVALENCE-001 @ {accepted}; source reopen: NO)"
    github_ci: "VERIFIED (Integration CI run 34461727271; Governance CI run 34461727266; exact SHA {accepted}; PASS)"
    accepted_checkpoint: "checkpoint/S05-002-accepted-001"
    acceptance:
      - "R3 implementation review: PASS @ {candidate}"
      - "Final integration equivalence review: PASS @ {accepted}"
      - "Integration CI 34461727271: PASS"
      - "Governance CI 34461727266: PASS"
      - "checkpoint/S05-002-accepted-001 @ {accepted}"
    notes: '''
if old not in block:
    raise SystemExit("TASK_REGISTRY marker missing")
block = block.replace(old, new, 1)
old_note = '"Materialized after exact-source eiu-reviewer prompt PASS. Scope: HR Report management over accepted report contracts; add missing set_report_visibility and bulk_change_report_status, repair delete permission to reports.delete + reports.view, preserve dedicated minimum-safe HR read projection, accepted Current Round/Final Decision/concurrency semantics, Design System v1.8, and no deployment or connected Supabase migration application."'
new_note = '"Accepted HR Report management experience. R1/R2 blockers were repaired; R3 implementation review passed; exact integration-equivalence review passed; full web/database exact-SHA CI passed. No Product/Business/Design source reopen, Vercel deployment, main mutation, or connected Supabase migration application occurred. ASSET-001 official pixel-perfect PDF template remains deferred/non-blocking."'
block = block.replace(old_note, new_note, 1)
p.write_text(s[:start] + block)

# AUTONOMY_RUN_STATE
p = Path("project_control/AUTONOMY_RUN_STATE.yaml")
s = p.read_text()
for a, b in {
    '  last_verified_application_checkpoint: "ef0bd9e534dec0cc85ef6503fbe0369eda56d555"': f'  last_verified_application_checkpoint: "{accepted}"',
    '  last_verified_application_ci_run: "34386549610"': '  last_verified_application_ci_run: "34461727271"',
    '  last_task_acceptance_attempt_sha: "ef0bd9e534dec0cc85ef6503fbe0369eda56d555"': f'  last_task_acceptance_attempt_sha: "{accepted}"',
    '  last_task_acceptance_integration_ci_run: "34386549610"': '  last_task_acceptance_integration_ci_run: "34461727271"',
    '  last_task_acceptance_governance_ci_run: "34386549725"': '  last_task_acceptance_governance_ci_run: "34461727266"',
}.items():
    if a not in s:
        raise SystemExit(f"AUTONOMY marker missing: {a}")
    s = s.replace(a, b, 1)

la = s.index("last_accepted_task:\n")
pa = s.index("previous_accepted_tasks:\n", la)
s = s[:la] + f'''last_accepted_task:
  id: TASK-S05-002
  commit: "{accepted}"
  evidence:
    - "prompt_review: PASS (S05-002-PROMPT-REVIEW-001)"
    - "implementation_review: PASS (R3 @ {candidate})"
    - "final_exact_sha_acceptance_review: PASS (S05-002-FINAL-INTEGRATION-EQUIVALENCE-001 @ {accepted})"
    - "github_ci: VERIFIED (Integration CI 34461727271; Governance CI 34461727266; PASS)"
    - "accepted_checkpoint: checkpoint/S05-002-accepted-001 @ {accepted}"

''' + s[pa:]
idx = s.index("previous_accepted_tasks:\n") + len("previous_accepted_tasks:\n")
prev = '  TASK-S05-001: {commit: "ef0bd9e534dec0cc85ef6503fbe0369eda56d555"}\n'
if prev not in s:
    s = s[:idx] + prev + s[idx:]

sp = s.index("slice_05_planning:\n")
tail = s[sp:].replace("  status: WAITING_EXTERNAL_REVIEW\n", "  status: TASKS_ACCEPTED_PENDING_SLICE_CLOSURE\n", 1)
s = s[:sp] + tail
ir = s.index("  independent_implementation_review:\n", sp)
er = s.index("  external_review_transport:", ir)
s = s[:ir] + f'''  independent_implementation_review:
    work_id: S05-002-IMPLEMENTATION-REVIEW-001-R3
    reviewer: eiu-reviewer
    status: VERIFIED_FROM_OWNER_TRANSPORT
    reviewed_sha: "{candidate}"
    result: PASS
    source_reopen_required: false
    blocking_findings: NONE
    evidence_persistence: "Reviewer-reported coordinates were not GitHub-visible when checked; verdict accepted per Owner instruction to proceed from reviewer report."
  final_integration_equivalence:
    work_id: S05-002-FINAL-INTEGRATION-EQUIVALENCE-001
    reviewer: eiu-reviewer
    status: VERIFIED_FROM_OWNER_TRANSPORT
    source_implementation_sha: "{candidate}"
    reviewed_sha: "{accepted}"
    result: PASS
    source_reopen_required: false
    blocking_findings: NONE
    evidence_persistence: "Reviewer-reported coordinates were not GitHub-visible when checked; verdict accepted per Owner instruction to proceed from reviewer report."
    integration_ci_run: "34461727271 PASS"
    governance_ci_run: "34461727266 PASS"
    accepted_checkpoint: "checkpoint/S05-002-accepted-001 @ {accepted}"
''' + s[er:]

sf = s.index("safe_frontier:\n")
s = s[:sf] + f'''s05_002_acceptance:
  result: ACCEPTED
  implementation_candidate_sha: "{candidate}"
  final_acceptance_sha: "{accepted}"
  integration_ci_run: "34461727271"
  governance_ci_run: "34461727266"
  accepted_checkpoint: "checkpoint/S05-002-accepted-001 @ {accepted}"
  source_reopen_required: false
  connected_supabase_migration_applied: false
  vercel_deployment_performed: false

safe_frontier:
  eligible_tasks: []
  skipped_due_to_dependency: []
  materialization_frontier: []
  execution_hold: "SLICE-05 closing composition review and broader regression gate"

stop_gate:
  status: PREPARING_SLICE_CLOSING
  type: SLICE_CLOSING_PREPARATION
  slice: SLICE-05
  accepted_tasks: [TASK-S05-001, TASK-S05-002]
  latest_task_acceptance_sha: "{accepted}"
  broader_regression_required: true
  composition_review_required: true
  source_reopen_required: false
  resume_on: "fresh [full-ci] PASS on acceptance-bookkeeping integration SHA, then independent slice-closing composition review"

next_action: "Run the SLICE-05 broader [full-ci] regression on the acceptance-bookkeeping integration head. If PASS, persist exact-SHA SLICE-05 closing-review handoff and obtain independent composition verdict before marking SLICE-05 DONE or materializing SLICE-06 work. Do not merge/push main, deploy Vercel, or apply connected Supabase migrations without explicit Owner authorization."
'''
p.write_text(s)

# EVIDENCE_INDEX
p = Path("project_control/EVIDENCE_INDEX.yaml")
s = p.read_text()
s = s.replace("  status: SLICE_05_TASK_S05_001_ACCEPTED\n", "  status: SLICE_05_TASK_S05_002_ACCEPTED_PENDING_SLICE_CLOSURE\n", 1)
old_note = '  note: "TASK-S05-001 accepted at exact SHA ef0bd9e534dec0cc85ef6503fbe0369eda56d555 after final OMP equivalence PASS, Integration CI 34386549610 PASS, Governance CI 34386549725 PASS, and immutable checkpoint. Owner requested handoff before S05-002 materialization."\n'
new_note = f'  note: "TASK-S05-002 accepted at exact SHA {accepted} after final integration-equivalence PASS, Integration CI 34461727271 PASS, Governance CI 34461727266 PASS, and immutable checkpoint; SLICE-05 closure remains pending composition review and broader regression."\n'
if old_note in s:
    s = s.replace(old_note, new_note, 1)
if "  HR-REPORT-ACCEPTANCE-001:\n" not in s:
    s += f'''\n  HR-REPORT-ACCEPTANCE-001:
    task: TASK-S05-002
    operation: HR_REPORT_MANAGEMENT_EXPERIENCE_ACCEPTANCE
    status: VERIFIED
    source_reopen_required: false
    implementation_candidate_sha: "{candidate}"
    final_acceptance_sha: "{accepted}"
    implementation_review: "PASS (S05-002-IMPLEMENTATION-REVIEW-001-R3; Owner-transported reviewer report)"
    final_exact_sha_review: "PASS (S05-002-FINAL-INTEGRATION-EQUIVALENCE-001; Owner-transported reviewer report)"
    integration_ci: "34461727271 PASS"
    governance_ci: "34461727266 PASS"
    accepted_checkpoint: "checkpoint/S05-002-accepted-001 @ {accepted}"
    review_evidence_coordinates: "reported by reviewer but not GitHub-visible at Coordinator verification time"
    connected_supabase_migration_applied: false
    vercel_deployment_performed: false
'''
p.write_text(s)

# TRACEABILITY_STATUS
p = Path("project_control/TRACEABILITY_STATUS.csv")
s = p.read_text()
s = s.replace("Reconciled through accepted checkpoint TASK-S04-004", "Reconciled through accepted checkpoint TASK-S05-002", 1)
s = s.replace(",review_pack/command_registry.yaml,set_report_visibility,,,NOT_STARTED,,,No accepted public command implementation found through TASK-S04-005.", ",review_pack/command_registry.yaml,set_report_visibility,supabase/migrations/20260910023000_hr_report_management.sql,HR-REPORT-ACCEPTANCE-001,IMPLEMENTED,,fe556dd,TASK-S05-002 accepted reports.visibility + reports.view command.")
s = s.replace(",review_pack/command_registry.yaml,delete_or_inactivate_report,supabase/migrations/20260906070000_interview_lifecycle_commands.sql,INTERVIEW-LIFECYCLE-001,IMPLEMENTED,,52f35ee,TASK-S04-002 report backend prerequisite for SLICE-05", ",review_pack/command_registry.yaml,delete_or_inactivate_report,supabase/migrations/20260910023000_hr_report_management.sql,HR-REPORT-ACCEPTANCE-001,IMPLEMENTED,,fe556dd,TASK-S05-002 effective accepted permission repair to reports.delete + reports.view")
s = s.replace(",review_pack/command_registry.yaml,bulk_change_report_status,,,NOT_STARTED,,,No accepted public command implementation found through TASK-S04-005.", ",review_pack/command_registry.yaml,bulk_change_report_status,supabase/migrations/20260910023000_hr_report_management.sql,HR-REPORT-ACCEPTANCE-001,IMPLEMENTED,,fe556dd,TASK-S05-002 accepted atomic max-100 ALL_OR_NOTHING bulk status command.")
p.write_text(s)

Path("project_control/CURRENT_STATE.md").write_text(f'''# Current Implementation State — Derived Handoff Snapshot

> **DERIVED / NON-AUTHORITATIVE REPORTING ONLY**
>
> Runtime authority: `project_control/AUTONOMY_RUN_STATE.yaml`.
> DAG/task/slice authority: `project_control/TASK_REGISTRY.yaml` and `project_control/SLICE_REGISTRY.yaml`.
> Exact code/history authority: Git.

## TASK-S05-001 — DONE / ACCEPTED

- Final exact acceptance SHA: `ef0bd9e534dec0cc85ef6503fbe0369eda56d555`
- Immutable checkpoint: `checkpoint/S05-001-accepted-001`

## TASK-S05-002 — DONE / ACCEPTED

- Reviewed candidate: `{candidate}`
- Final integration / acceptance SHA: `{accepted}`
- Final integration-equivalence review: PASS
- Source reopen required: NO
- Integration CI `34461727271`: PASS (web + database)
- Governance CI `34461727266`: PASS
- Immutable checkpoint: `checkpoint/S05-002-accepted-001 @ {accepted}`
- Connected Supabase migration application: NOT PERFORMED
- Vercel deployment: NOT PERFORMED

## SLICE-05 — PENDING CLOSING GATE

Both Slice-05 tasks are individually accepted. Governance requires a slice-closing composition review and broader regression before SLICE-05 may be marked DONE.

Next action: commit this bookkeeping with `[full-ci]`, require fresh web + database CI, then obtain independent exact-SHA Slice-05 composition review. Only after that PASS may the outer loop inspect/materialize SLICE-06.

## Do not cross

- Do not mark SLICE-05 DONE before the closing gate passes.
- Do not merge/push `main`.
- Do not deploy Vercel.
- Do not apply migrations to connected Supabase DEV/production without explicit Owner authorization.
- ASSET-001 official pixel-perfect PDF template remains deferred / non-blocking.
''')
