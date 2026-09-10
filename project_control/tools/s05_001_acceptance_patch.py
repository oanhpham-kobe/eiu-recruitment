from pathlib import Path

EF0 = "ef0bd9e534dec0cc85ef6503fbe0369eda56d555"
R6 = "63bb2f9eff9e36c11c704748c3ccf334cbcfc4ce"


def replace_section(src: str, start: str, end: str, replacement: str) -> str:
    if src.count(start) != 1 or src.count(end) != 1:
        raise SystemExit(f"section markers invalid: {start!r} -> {end!r}")
    a = src.index(start)
    b = src.index(end, a)
    return src[:a] + replacement.rstrip() + "\n\n" + src[b:]


# TASK_REGISTRY: replace only the final S05-001 block.
task_path = Path("project_control/TASK_REGISTRY.yaml")
text = task_path.read_text(encoding="utf-8")
marker = "  TASK-S05-001:\n"
if text.count(marker) != 1:
    raise SystemExit("TASK-S05-001 marker must occur exactly once")
prefix = text.split(marker, 1)[0]
block = f'''  TASK-S05-001:
    title: "Interviewer Report Experience over Accepted Report Contracts"
    slice: SLICE-05
    status: DONE
    lane: LANE_A
    branch: oanhpham-kobe/TASK-S05-001-interviewer-report-experience-skills
    depends_on:
      - TASK-S04-002
      - TASK-S04-005
      - TASK-S04-004
      - TASK-DS-006
    prompt: project_control/prompts/SLICE-05_TASK-001_v1.md
    prompt_sha256: "6dd884c22c4d58ac6120cfae133e9e27efb48ada228d3f7be1b790be37ad59c5"
    prompt_review_status: "PASS (S05-001-PROMPT-REVIEW-001-R2 @ 54a1f450b27bf8470e683cf66791fba7b7f62791; source reopen: NO)"
    prompt_review_evidence:
      branch: review/S05-001-PROMPT-54a1f45-v2
      commit: "36b5df1af4564853fb299af24696f0c8796228d0"
      artifact: project_control/reviews/S05_001_PROMPT_REVIEW_54a1f45_v2.md
    implementation_sha: "{EF0}"
    review_status: "PASS (S05-001-FINAL-INTEGRATION-EQUIVALENCE-001 @ {EF0}; source reopen: NO)"
    github_ci: "VERIFIED (Integration CI run 34386549610; Governance CI run 34386549725; exact SHA {EF0}; PASS)"
    accepted_checkpoint: "checkpoint/S05-001-accepted-001"
    acceptance:
      - "R6 implementation review: PASS @ {R6}"
      - "Final integration equivalence review: PASS @ {EF0}"
      - "Integration CI 34386549610: PASS"
      - "Governance CI 34386549725: PASS"
      - "checkpoint/S05-001-accepted-001 @ {EF0}"
    notes: "Accepted Interviewer Report experience. R4 product review passed; R5/R6 repaired only CI harness defects; final exact integration equivalence review passed. No deployment or connected Supabase migration application occurred. ASSET-001 official pixel-perfect PDF template remains deferred."
'''
task_path.write_text(prefix + block, encoding="utf-8")


# AUTONOMY_RUN_STATE: replace bounded top-level sections.
state_path = Path("project_control/AUTONOMY_RUN_STATE.yaml")
state = state_path.read_text(encoding="utf-8")
state = replace_section(
    state,
    "integration:\n",
    "authorization:\n",
    f'''integration:
  branch: autonomy/continuous-integration-20260905-01
  head_resolution: DIRECT_GIT_RUNTIME
  last_verified_application_checkpoint: "{EF0}"
  last_verified_application_ci_run: "34386549610"
  last_verified_slice_closing_sha: "e3daa6930374ecad1ad0e646b651ee076b515a8b"
  last_verified_slice_closing_ci_run: "34201054499"
  last_verified_control_plane_sha: "54a1f450b27bf8470e683cf66791fba7b7f62791"
  last_verified_control_plane_integration_ci_run: "34211382997"
  last_verified_control_plane_governance_ci_run: "34211383102"
  last_task_acceptance_attempt_sha: "{EF0}"
  last_task_acceptance_integration_ci_run: "34386549610"
  last_task_acceptance_integration_ci_result: PASS
  last_task_acceptance_governance_ci_run: "34386549725"
  last_task_acceptance_governance_ci_result: PASS''',
)
state = replace_section(state, "active_workers:\n", "active_task:\n", "active_workers: []")
state = replace_section(
    state,
    "active_task:\n",
    "last_accepted_task:\n",
    '''active_task:
  id: TASK-S05-001
  slice: SLICE-05
  phase: COMPLETED_HANDOFF
  reviewer_status: PASS''',
)
state = replace_section(
    state,
    "last_accepted_task:\n",
    "previous_accepted_tasks:\n",
    f'''last_accepted_task:
  id: TASK-S05-001
  commit: "{EF0}"
  evidence:
    - "prompt_review: PASS (S05-001-PROMPT-REVIEW-001-R2)"
    - "implementation_review: PASS (R6 @ {R6})"
    - "final_exact_sha_acceptance_review: PASS (S05-001-FINAL-INTEGRATION-EQUIVALENCE-001 @ {EF0})"
    - "github_ci: VERIFIED (Integration CI 34386549610; Governance CI 34386549725; PASS)"
    - "accepted_checkpoint: checkpoint/S05-001-accepted-001 @ {EF0}"''',
)

planning_start = "slice_05_planning:\n"
planning_end = "s05_001_acceptance:\n"
a = state.index(planning_start)
b = state.index(planning_end, a)
planning = state[a:b]
planning = planning.replace("  status: IMPLEMENTATION_RE_REVIEW_REQUIRED\n", "  status: POST_CI_HANDOFF\n", 1)
if "  proposed_next_task: TASK-S05-002\n" not in planning:
    planning = planning.replace(
        "  proposed_first_task: TASK-S05-001\n",
        "  proposed_first_task: TASK-S05-001\n  proposed_next_task: TASK-S05-002\n",
        1,
    )
state = state[:a] + planning + state[b:]

state = replace_section(
    state,
    "s05_001_acceptance:\n",
    "safe_frontier:\n",
    f'''s05_001_acceptance:
  result: ACCEPTED
  final_acceptance_sha: "{EF0}"
  r6_review:
    reviewed_sha: "{R6}"
    result: PASS
    evidence_branch: "review/S05-001-IMPL-63bb2f9-v6"
    evidence_commit: "03ea6eb5417023e52f54edf4e863b7e585bea975"
  final_integration_equivalence:
    reviewed_sha: "{EF0}"
    result: PASS
    evidence_branch: "review/S05-001-FINAL-ef0bd9e-v1"
    evidence_commit: "c1b9eaed5b314ce9f64cbe2301494b04922ab57e"
  exact_sha_ci:
    integration_ci_run: "34386549610"
    governance_ci_run: "34386549725"
    result: PASS
  accepted_checkpoint: "checkpoint/S05-001-accepted-001 @ {EF0}"
  source_reopen_required: false''',
)
state = replace_section(
    state,
    "safe_frontier:\n",
    "stop_gate:\n",
    '''safe_frontier:
  eligible_tasks: []
  skipped_due_to_dependency: []
  materialization_frontier:
    - TASK-S05-002''',
)
state = replace_section(
    state,
    "stop_gate:\n",
    "next_action:",
    '''stop_gate:
  status: OWNER_REQUESTED_HANDOFF
  type: SESSION_HANDOFF_AFTER_TASK_ACCEPTANCE
  target: "TASK-S05-001 accepted and checkpointed"
  resume_condition: "Owner opens a new chat; resume POST-CI by materializing and prompt-reviewing TASK-S05-002 from the accepted integration head."''',
)
pos = state.index("next_action:")
state = state[:pos] + 'next_action: "NEW CHAT: verify accepted integration/control-plane HEAD, then stage TASK-S05-002 HR Report Management prompt and run independent prompt review before implementation."\n'
state_path.write_text(state, encoding="utf-8")


# CURRENT_STATE is derived; regenerate compactly.
Path("project_control/CURRENT_STATE.md").write_text(
    f'''# Current Implementation State — Derived Handoff Snapshot

> **DERIVED / NON-AUTHORITATIVE REPORTING ONLY**
>
> Runtime authority: `project_control/AUTONOMY_RUN_STATE.yaml`.
> DAG/task/slice authority: `project_control/TASK_REGISTRY.yaml` and `project_control/SLICE_REGISTRY.yaml`.
> Exact code/history authority: Git.

## TASK-S05-001 — DONE / ACCEPTED

- Final exact acceptance SHA: `{EF0}`
- R6 implementation review: PASS @ `{R6}`
- Final integration equivalence review: PASS @ `{EF0}`
- Integration CI `34386549610`: PASS
- Governance CI `34386549725`: PASS
- Immutable checkpoint: `checkpoint/S05-001-accepted-001 @ {EF0}`
- Source reopen required: NO
- Vercel deployment: NOT PERFORMED
- Connected Supabase migration application: NOT PERFORMED
- ASSET-001 official pixel-perfect PDF template: deferred / non-blocking

## Slice-05 continuation

Slice-05 remains IN_PROGRESS. The next source-backed materialization frontier is `TASK-S05-002 — HR Report Management Experience over Accepted Report Contracts`.

Known prompt-reconciliation points for S05-002:

- `set_report_visibility` is required by the canonical command coverage matrix but absent from the accepted backend tree.
- `bulk_change_report_status` is Phase-1 visible / ALL_OR_NOTHING but absent from the accepted backend tree.
- `delete_or_inactivate_report` exists but must be reconciled with canonical `reports.delete + reports.view` authority instead of silently preserving `reports.manage_status` if source requires otherwise.
- HR Report requires a dedicated safe server read projection; do not widen the accepted S05-001 Interviewer-contextual DTO.
- Official PDF template integration remains excluded until ASSET-001 is supplied.

## Handoff boundary

Owner requested a new-chat handoff after TASK-S05-001 completion. Resume by verifying the integration/control-plane HEAD, then stage `project_control/prompts/SLICE-05_TASK-002_v1.md` and perform independent OMP prompt review before implementation.
''',
    encoding="utf-8",
)


# EVIDENCE_INDEX: update top status/note and append one compact acceptance receipt.
evidence_path = Path("project_control/EVIDENCE_INDEX.yaml")
evidence = evidence_path.read_text(encoding="utf-8")
old_status = "  status: SLICE_04_IN_PROGRESS_TASK_S04_004_READY_PLAN_RECONCILED\n"
if old_status in evidence:
    evidence = evidence.replace(old_status, "  status: SLICE_05_TASK_S05_001_ACCEPTED\n", 1)
anchor = "implementation_evidence:\n"
if evidence.count(anchor) != 1:
    raise SystemExit("implementation_evidence marker invalid")
note_start = evidence.index("  note:", evidence.index(anchor))
note_end = evidence.index("\n", note_start)
note = '  note: "TASK-S05-001 accepted at exact SHA ef0bd9e534dec0cc85ef6503fbe0369eda56d555 after final OMP equivalence PASS, Integration CI 34386549610 PASS, Governance CI 34386549725 PASS, and immutable checkpoint. Owner requested handoff before S05-002 materialization."'
evidence = evidence[:note_start] + note + evidence[note_end:]
receipt_key = "  INTERVIEWER-REPORT-ACCEPTANCE-001:\n"
if receipt_key not in evidence:
    evidence = evidence.rstrip() + f'''\n\n  INTERVIEWER-REPORT-ACCEPTANCE-001:
    task: TASK-S05-001
    operation: INTERVIEWER_REPORT_EXPERIENCE_ACCEPTANCE
    status: VERIFIED
    implementation_review_sha: "{R6}"
    final_acceptance_sha: "{EF0}"
    implementation_review: "PASS (R6)"
    final_exact_sha_review: "PASS (S05-001-FINAL-INTEGRATION-EQUIVALENCE-001)"
    integration_ci: "34386549610 PASS"
    governance_ci: "34386549725 PASS"
    accepted_checkpoint: "checkpoint/S05-001-accepted-001 @ {EF0}"
    connected_supabase_migration_applied: false
    vercel_deployment_performed: false
    source_reopen_required: false
'''
evidence_path.write_text(evidence, encoding="utf-8")
