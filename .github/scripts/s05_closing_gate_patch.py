from pathlib import Path

reviewed = "60e1f425d920ed9d76de68b49347188187054bd4"

p = Path("project_control/AUTONOMY_RUN_STATE.yaml")
s = p.read_text()
for a, b in {
    '  last_verified_control_plane_sha: "16bf76c5ad306b1144d3ef6c76f832463c32c62b"': f'  last_verified_control_plane_sha: "{reviewed}"',
    '  last_verified_control_plane_integration_ci_run: "34429901224"': '  last_verified_control_plane_integration_ci_run: "34463405935"',
    '  last_verified_control_plane_governance_ci_run: "34429901220"': '  last_verified_control_plane_governance_ci_run: "34463405902"',
}.items():
    if a in s:
        s = s.replace(a, b, 1)

sp = s.index("slice_05_planning:\n")
tail = s[sp:]
if "  status: TASKS_ACCEPTED_PENDING_SLICE_CLOSURE\n" not in tail:
    raise SystemExit("slice_05_planning status marker missing")
tail = tail.replace("  status: TASKS_ACCEPTED_PENDING_SLICE_CLOSURE\n", "  status: WAITING_EXTERNAL_REVIEW\n", 1)
s = s[:sp] + tail

sf = s.index("safe_frontier:\n")
closing = f'''slice_05_closing_review:
  work_id: SLICE-05-CLOSING-REVIEW-001
  reviewer: eiu-reviewer
  status: WAITING_EXTERNAL_REVIEW
  reviewed_sha: "{reviewed}"
  accepted_tasks:
    TASK-S05-001: "ef0bd9e534dec0cc85ef6503fbe0369eda56d555"
    TASK-S05-002: "fe556dda76ebeda7107bcb9310cbaf338b30fc29"
  broader_integration_ci_run: "34463405935"
  broader_integration_ci_result: PASS
  governance_ci_run: "34463405902"
  governance_ci_result: PASS
  source_reopen_required: PENDING
  verdict: PENDING
  evidence_branch: PENDING
  evidence_commit: PENDING
  evidence_path: PENDING
  handoff_package: project_control/reviews/SLICE_05_CLOSING_REVIEW_GATE_60e1f42_v1.md

safe_frontier:
  eligible_tasks: []
  skipped_due_to_dependency: []
  materialization_frontier: []
  execution_hold: "SLICE-05 independent closing composition review"

stop_gate:
  status: WAITING_EXTERNAL_REVIEW
  type: OMP_SLICE_CLOSING_REVIEW
  work_id: SLICE-05-CLOSING-REVIEW-001
  target: "autonomy/continuous-integration-20260905-01 @ {reviewed}"
  reviewed_sha: "{reviewed}"
  reviewer: eiu-reviewer
  verdict: PENDING
  source_reopen_required: PENDING
  broader_integration_ci_run: "34463405935 PASS"
  governance_ci_run: "34463405902 PASS"
  handoff_package_requirement: SATISFIED
  handoff_package: project_control/reviews/SLICE_05_CLOSING_REVIEW_GATE_60e1f42_v1.md
  resume_on: "PASS + SOURCE_REOPEN_REQUIRED=false for exact SLICE-05 closing target"

next_action: "Transport project_control/reviews/SLICE_05_CLOSING_REVIEW_GATE_60e1f42_v1.md to independent OMP eiu-reviewer for exact Slice-05 composition target {reviewed}. On PASS + SOURCE_REOPEN_REQUIRED=false, mark SLICE-05 DONE, persist closure evidence/state, recompute frontier, and inspect/materialize SLICE-06 source-backed work. Do not merge/push main, deploy Vercel, or apply connected Supabase migrations without explicit Owner authorization."
'''
s = s[:sf] + closing
p.write_text(s)

Path("project_control/CURRENT_STATE.md").write_text(f'''# Current Implementation State — Derived Handoff Snapshot

> **DERIVED / NON-AUTHORITATIVE REPORTING ONLY**
>
> Runtime authority: `project_control/AUTONOMY_RUN_STATE.yaml`.
> DAG/task/slice authority: `project_control/TASK_REGISTRY.yaml` and `project_control/SLICE_REGISTRY.yaml`.
> Exact code/history authority: Git.

## SLICE-05 — WAITING INDEPENDENT CLOSING REVIEW

Both constituent tasks are individually accepted:

- TASK-S05-001: `ef0bd9e534dec0cc85ef6503fbe0369eda56d555`, checkpoint `checkpoint/S05-001-accepted-001`.
- TASK-S05-002: `fe556dda76ebeda7107bcb9310cbaf338b30fc29`, checkpoint `checkpoint/S05-002-accepted-001`.

Exact Slice-05 composition review target:

`{reviewed}`

Fresh broader closing regression on that SHA:

- Integration CI `34463405935`: PASS — forced web + database via `[full-ci]`.
- Governance CI `34463405902`: PASS.
- Acceptance-bookkeeping delta from TASK-S05-002 acceptance SHA changes only five project_control/derived files; no product drift.

Independent closing review:

- work ID: `SLICE-05-CLOSING-REVIEW-001`
- reviewer: `eiu-reviewer`
- handoff: `project_control/reviews/SLICE_05_CLOSING_REVIEW_GATE_60e1f42_v1.md`
- verdict: PENDING
- source reopen: PENDING

SLICE-05 remains `IN_PROGRESS` until this composition review passes. Slice-06 must not be materialized before the closing verdict.

## Do not cross

- Do not mark SLICE-05 DONE before closing review PASS.
- Do not merge/push `main`.
- Do not deploy Vercel.
- Do not apply migrations to connected Supabase DEV/production without explicit Owner authorization.
- ASSET-001 official pixel-perfect PDF template remains deferred / non-blocking.
''')
