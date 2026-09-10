from pathlib import Path

# SLICE_REGISTRY
p = Path('project_control/SLICE_REGISTRY.yaml')
s = p.read_text()
s = s.replace('current_slice: SLICE-05', 'current_slice: SLICE-06', 1)
s = s.replace('SLICE-05: {name: Interviewer Reports / HR Report / Final Decision, status: IN_PROGRESS, current_task: TASK-S05-002}', 'SLICE-05: {name: Interviewer Reports / HR Report / Final Decision, status: DONE, current_task: TASK-S05-002}', 1)
s = s.replace('SLICE-06: {name: Master Data / Users & Permissions, status: NOT_STARTED}', 'SLICE-06: {name: Master Data / Users & Permissions, status: IN_PROGRESS, current_task: TASK-S06-001}', 1)
p.write_text(s)

# TASK_REGISTRY
p = Path('project_control/TASK_REGISTRY.yaml')
s = p.read_text()
s = s.replace('current_slice: SLICE-05', 'current_slice: SLICE-06', 1)
s = s.replace('current_task: TASK-S05-002', 'current_task: TASK-S06-001', 1)
if '  TASK-S06-001:\n' not in s:
    if not s.endswith('\n'):
        s += '\n'
    s += '''\n  TASK-S06-001:
    title: Master Data Lifecycle & Historical Semantics Trusted Contracts
    slice: SLICE-06
    status: PLANNED
    lane: LANE_A
    depends_on:
      - TASK-S05-002
    prompt: project_control/prompts/SLICE-06_TASK-001_v1.md
    prompt_review_status: PENDING
    prompt_review_evidence: PENDING
    pre_task_checkpoint: PENDING_AFTER_PROMPT_REVIEW
    branch: PENDING_AFTER_PROMPT_REVIEW
    notes: "Shared-contract backend prerequisite for Phase-1 business Master Data. Scope is limited to the 11 physical business masters and canonical create_master_item/update_master_item/delete_or_inactivate_master_item lifecycle/history contracts. Internal User directory, HR roles/permissions, bound identity, Root break-glass, and management UI are explicitly deferred to later Slice-06 tasks."
'''
p.write_text(s)

# AUTONOMY_RUN_STATE: preserve everything before prior slice-closing block, replace operational tail.
p = Path('project_control/AUTONOMY_RUN_STATE.yaml')
s = p.read_text()
marker = 'slice_05_closing_review:\n'
if marker not in s:
    raise SystemExit('slice_05_closing_review marker missing')
prefix = s[:s.index(marker)]
tail = '''slice_05_closure:
  work_id: SLICE-05-CLOSING-REVIEW-001
  result: PASS
  source_reopen_required: false
  reviewed_sha: "60e1f425d920ed9d76de68b49347188187054bd4"
  accepted_tasks:
    TASK-S05-001: "ef0bd9e534dec0cc85ef6503fbe0369eda56d555"
    TASK-S05-002: "fe556dda76ebeda7107bcb9310cbaf338b30fc29"
  broader_integration_ci_run: "34463405935"
  broader_integration_ci_result: PASS
  governance_ci_run: "34463405902"
  governance_ci_result: PASS
  reviewer: eiu-reviewer
  review_evidence_transport: "Owner returned PASS / SOURCE_REOPEN_REQUIRED=false for exact reviewed SHA. Reviewer-reported branch review/SLICE-05-CLOSING-60e1f42-v1, commit a276ae4dc10be8c245fffdfa278e40dba8350f87, and path project_control/reviews/SLICE_05_CLOSING_REVIEW_60e1f42_v1.md were not GitHub-visible when Coordinator checked commit/ref/path; no durable-verification claim is made."
  composition_verdict: "PASS — cross-task composition, security/privacy, Current Round/status/final decision, concurrency/lifecycle, design/UX/accessibility, and slice completeness"

slice_06_planning:
  status: PROMPT_REVIEW_PREPARATION
  proposed_first_task: TASK-S06-001
  materialized_task: TASK-S06-001
  task_status: PLANNED
  prompt: project_control/prompts/SLICE-06_TASK-001_v1.md
  producer_reconciliation:
    work_id: S06-001-PROMPT-PRODUCER-RECONCILIATION-001
    result: PASS
    source_reopen_required: false
    evidence_path: project_control/reviews/S06_001_PROMPT_PRODUCER_RECONCILIATION_v1.md
  canonical_sources:
    - recruitment_webapp/review_pack/09_MASTER_DATA_CATALOG.md
    - recruitment_webapp/review_pack/64_MASTER_DATA_HISTORY_POLICY.md
    - recruitment_webapp/review_pack/08_DATA_MODEL_AND_FIELD_DICTIONARY.md
    - recruitment_webapp/review_pack/37_BACKEND_COMMAND_CONTRACTS.md
    - recruitment_webapp/review_pack/39_SECURITY_RLS_MATRIX.md
    - recruitment_webapp/review_pack/40_DATABASE_INVARIANTS.md
    - recruitment_webapp/review_pack/55_COMMAND_COVERAGE_MATRIX.md
    - recruitment_webapp/review_pack/59_RLS_POLICY_BLUEPRINT.md
    - recruitment_webapp/review_pack/73_DOMAIN_GLOSSARY_AND_CANONICAL_PREDICATES.md
    - recruitment_webapp/review_pack/100_TECHNICAL_PRECODE_GATE_V1_18.md
    - recruitment_webapp/review_pack/command_registry.yaml
    - recruitment_webapp/review_pack/database_schema.sql
    - recruitment_webapp/review_pack/seed_master_data.json
  accepted_prerequisites:
    - TASK-S05-002
    - accepted identity/auth/master reference foundations from prior slices
  scope_split:
    s06_001: "business Master Data lifecycle/history trusted contracts"
    later_security_task: "Internal User directory, HR role/permission management, bound identity and lifecycle safeguards"
    later_ui_tasks: "Master Data and Users/Permissions management experiences"
  source_reopen_required: false
  prompt_review_target_sha: PENDING_INTEGRATION_MATERIALIZATION
  independent_prompt_review:
    work_id: S06-001-PROMPT-REVIEW-001
    reviewer: eiu-reviewer
    status: PREPARING
    reviewed_sha: PENDING_INTEGRATION_MATERIALIZATION
    result: PENDING
    source_reopen_required: PENDING
    evidence_branch: PENDING
    evidence_commit: PENDING
    evidence_path: PENDING
  reconciliation_note: "Accepted Slice-01 users.directory_read technical helper is intentionally left untouched by S06-001 and must be reconciled in the later User/Identity/RBAC task against current permission-detail visibility rules."

safe_frontier:
  eligible_tasks: []
  skipped_due_to_dependency: []
  materialization_frontier: []
  execution_hold: "TASK-S06-001 independent pre-implementation prompt/source review preparation"

stop_gate:
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
p.write_text(prefix + tail)

# EVIDENCE_INDEX
p = Path('project_control/EVIDENCE_INDEX.yaml')
s = p.read_text()
s = s.replace('status: SLICE_05_TASK_S05_002_ACCEPTED_PENDING_SLICE_CLOSURE', 'status: SLICE_05_CLOSED_S06_001_PROMPT_REVIEW', 1)
if '  SLICE-05-CLOSURE-001:\n' not in s:
    s += '''\n  SLICE-05-CLOSURE-001:
    operation: SLICE_05_CLOSING_COMPOSITION_ACCEPTANCE
    status: VERIFIED_FROM_OWNER_TRANSPORT
    reviewed_sha: "60e1f425d920ed9d76de68b49347188187054bd4"
    result: PASS
    source_reopen_required: false
    accepted_tasks:
      - "TASK-S05-001 @ ef0bd9e534dec0cc85ef6503fbe0369eda56d555"
      - "TASK-S05-002 @ fe556dda76ebeda7107bcb9310cbaf338b30fc29"
    broader_integration_ci: "34463405935 PASS"
    governance_ci: "34463405902 PASS"
    reviewer: eiu-reviewer
    reviewer_reported_evidence: "review/SLICE-05-CLOSING-60e1f42-v1 @ a276ae4dc10be8c245fffdfa278e40dba8350f87; project_control/reviews/SLICE_05_CLOSING_REVIEW_60e1f42_v1.md"
    durable_evidence_verification: "UNRESOLVED — reported branch/commit/path were not GitHub-visible at Coordinator verification time; verdict accepted from Owner transport without claiming durable verification"

  S06-001-PROMPT-PRODUCER-RECONCILIATION-001:
    task: TASK-S06-001
    operation: MASTER_DATA_PROMPT_SOURCE_RECONCILIATION
    status: PASS_PENDING_INDEPENDENT_REVIEW
    source_reopen_required: false
    prompt: project_control/prompts/SLICE-06_TASK-001_v1.md
    evidence_path: project_control/reviews/S06_001_PROMPT_PRODUCER_RECONCILIATION_v1.md
    scope: "business Master Data lifecycle/history trusted commands only; User/Identity/RBAC and UI split into later Slice-06 tasks"
'''
p.write_text(s)

# CURRENT_STATE derived snapshot
Path('project_control/CURRENT_STATE.md').write_text('''# Current Implementation State — Derived Handoff Snapshot

> **DERIVED / NON-AUTHORITATIVE REPORTING ONLY**
>
> Runtime authority: `project_control/AUTONOMY_RUN_STATE.yaml`.
> DAG/task/slice authority: `project_control/TASK_REGISTRY.yaml` and `project_control/SLICE_REGISTRY.yaml`.
> Exact code/history authority: Git.

## SLICE-05 — DONE / CLOSING REVIEW PASS

- TASK-S05-001 accepted: `ef0bd9e534dec0cc85ef6503fbe0369eda56d555`.
- TASK-S05-002 accepted: `fe556dda76ebeda7107bcb9310cbaf338b30fc29`.
- Closing composition target: `60e1f425d920ed9d76de68b49347188187054bd4`.
- Independent `eiu-reviewer`: PASS; `SOURCE_REOPEN_REQUIRED=false`; blockers NONE.
- Broader Integration CI `34463405935`: PASS (forced Web + Database).
- Governance CI `34463405902`: PASS.
- Reviewer-reported durable evidence coordinates were not GitHub-visible when checked; closure uses the Owner-transported exact-SHA verdict and does not claim durable evidence verification.

## SLICE-06 — IN PROGRESS / S06-001 PROMPT REVIEW PREPARATION

First source-backed task:

`TASK-S06-001 — Master Data Lifecycle & Historical Semantics Trusted Contracts`

Prompt:

`project_control/prompts/SLICE-06_TASK-001_v1.md`

Producer source reconciliation: PASS, no source reopen.

Scope is deliberately limited to the 11 Phase-1 business masters and canonical `create_master_item`, `update_master_item`, `delete_or_inactivate_master_item` backend/history contracts. Internal User directory, HR role/permission administration, security identity/rebind, Root break-glass, and management UI remain later Slice-06 tasks.

TASK-S06-001 remains `PLANNED`; no implementation branch/checkpoint is created before independent prompt review PASS.

## Do not cross

- Do not implement S06-001 before independent exact-target prompt review PASS.
- Do not merge/push `main`.
- Do not deploy Vercel.
- Do not apply migrations to connected Supabase DEV/production without explicit Owner authorization.
''')
