from pathlib import Path

CANDIDATE = "7c37d46fa504b5d98b156735d7355f1d938be0bf"
BASELINE = "0a2ccdfedc477f9766c9aaa03739d16a7ed83c01"
EVIDENCE = "project_control/reviews/S06_002_IMPLEMENTATION_REVIEW_OWNER_TRANSPORT_7c37d46_v2.md"

state_path = Path("project_control/AUTONOMY_RUN_STATE.yaml")
state = state_path.read_text()
marker = "s06_002_planning:\n"
if marker not in state:
    raise SystemExit("missing s06_002_planning marker")
prefix = state.split(marker, 1)[0]
state_tail = f'''s06_002_planning:
  status: IMPLEMENTATION_REPAIR_ACTIVE
  task: TASK-S06-002
  title: "Internal User Directory, HR RBAC & Identity Lifecycle Trusted Contracts"
  prompt: project_control/prompts/SLICE-06_TASK-002_v1.md
  prompt_review_target_sha: "f757e76f3f97077c608dab29bad45b8bd2126dc3"
  prompt_review:
    work_id: S06-002-PROMPT-REVIEW-001
    reviewer: eiu-reviewer
    review_type: PROMPT_SOURCE_RECONCILIATION
    result: PASS
    source_reopen_required: false
    blocking_findings: NONE
    handoff: project_control/reviews/S06_002_PROMPT_REVIEW_GATE_v1.md
    evidence_persistence: VERIFIED_FROM_OWNER_TRANSPORT
    evidence_path: project_control/reviews/S06_002_PROMPT_REVIEW_OWNER_TRANSPORT_f757e76_v1.md
  source_reopen_expectation: false
  accepted_prerequisites:
    - "TASK-S06-001 accepted @ 59be9b2c92906065b8e4baa902fcec1d4cbefa12"
    - "accepted Slice-01 identity/auth schema and Internal first-login provisioning"
    - "accepted Application owner and Interview participant/resource lifecycle contracts"
  implementation_hold: "CLEARED FOR R3 REPAIR — independent R2 review returned BLOCKING_REPAIR with SOURCE_REOPEN_REQUIRED=false; repair remains confined to the isolated TASK-S06-002 branch."
  implementation_candidate:
    branch: oanhpham-kobe/TASK-S06-002-user-rbac-identity
    baseline_sha: "{BASELINE}"
    prior_candidate_sha: "{CANDIDATE}"
    candidate_sha: PENDING
    review_round: R3
    prior_exact_verifier_run: "34621266079 PASS"
    prior_review_gate: project_control/reviews/S06_002_IMPLEMENTATION_R2_GATE_v1.md
    prior_review_handoff: project_control/reviews/S06_002_IMPLEMENTATION_R2_HANDOFF_7c37d46_v1.md
  independent_implementation_review:
    work_id: S06-002-IMPLEMENTATION-REVIEW-001-R2
    reviewer: eiu-reviewer
    status: VERIFIED_FROM_OWNER_TRANSPORT
    reviewed_sha: "{CANDIDATE}"
    result: BLOCKING_REPAIR
    source_reopen_required: false
    blocking_findings:
      - "Unit-history deadlock remains between bulk owner assignment and lifecycle/RBAC app_users updates via S06-001 Unit history locking."
      - "Interview operationalization can take participant advisory locks before actor/current-participant app_users FK row locks, leaving a public-command deadlock with lifecycle administration."
      - "Dormant-history repair permits deactivation-first add/re-add of a newly inactive participant because new selection/restoration is not post-lock revalidated outside resource_blocking Interviews."
      - "First Google bind does not repeat trusted Google/confirmed-email Auth evidence validation after normalized-email, target-row, and Internal User locks."
    evidence_persistence: UNAVAILABLE
    evidence_path: {EVIDENCE}
  r3_repair_scope:
    - "Reconcile the complete Unit/User/Application lock graph while preserving S06-001 durable history and active-master validation; add public bulk-assignment vs lifecycle/HR-role-removal races with non-null Unit."
    - "Make Interview operationalization acquire relevant app_users rows before Internal User advisory locks and revalidate participants; cover uncancel/schedule by an HR who is also a current participant versus Root lifecycle."
    - "Serialize and post-lock revalidate new participant selection/restoration regardless of dormant/resource-blocking status while preserving historical remove/reorder maintenance; cover CANCELLED and unscheduled deactivation-first add/re-add races."
    - "Repeat private.verified_google_auth_email(auth.uid()) after the full first-bind lock set, require equality with the advisory-key email, fail closed on change, and add staged Auth-evidence-change regression."

safe_frontier:
  eligible_tasks: []
  skipped_due_to_dependency: []
  materialization_frontier: []
  execution_hold: "TASK-S06-002 R3 repair is active after independent R2 BLOCKING_REPAIR; no later Slice-06 frontier is materialized."

stop_gate:
  status: CLEAR
  type: NONE
  work_id: S06-002-IMPLEMENTATION-REPAIR-R3
  target: "Repair four R2 blockers from exact candidate {CANDIDATE}"
  reviewer: eiu-reviewer
  source_reopen_required: false
  resume_on: "Produce a new immutable task-branch SHA, rerun zero-state/static/web/DB/concurrency verification including the four R2 regressions, then route exact SHA to independent R3 review."

next_action: "Repair the four S06-002 R2 blockers on oanhpham-kobe/TASK-S06-002-user-rbac-identity without weakening accepted contracts. Do not serialize product into integration before independent PASS; do not push/merge main, create/merge a PR, deploy Vercel, or apply connected Supabase migrations."
'''
state_path.write_text(prefix + state_tail)

registry_path = Path("project_control/TASK_REGISTRY.yaml")
registry = registry_path.read_text()
repls = {
    "    status: REVIEW\n    lane: LANE_A\n": "    status: IN_PROGRESS\n    lane: LANE_A\n",
    '    prior_implementation_candidate_sha: "a7aa037e26cda6ba70153539c1dfc15c3fba37e6"\n': f'    prior_implementation_candidate_sha: "{CANDIDATE}"\n',
    f'    implementation_candidate_sha: "{CANDIDATE}"\n': '    implementation_candidate_sha: PENDING\n',
    "    repair_round: R2\n": "    repair_round: R3\n",
    f'    review_status: "WAITING_INDEPENDENT_REVIEW (S06-002-IMPLEMENTATION-REVIEW-001-R2 @ {CANDIDATE}); R1 was BLOCKING_REPAIR with SOURCE_REOPEN_REQUIRED=false"\n': f'    review_status: "BLOCKING_REPAIR (S06-002-IMPLEMENTATION-REVIEW-001-R2 @ {CANDIDATE}; SOURCE_REOPEN_REQUIRED=false; evidence persistence unavailable)"\n',
}
for old, new in repls.items():
    if old not in registry:
        raise SystemExit(f"registry anchor missing: {old!r}")
    registry = registry.replace(old, new, 1)
if "    review_evidence: project_control/reviews/S06_002_IMPLEMENTATION_REVIEW_OWNER_TRANSPORT_7c37d46_v2.md\n" not in registry:
    anchor = "    prior_review_evidence: project_control/reviews/S06_002_IMPLEMENTATION_REVIEW_OWNER_TRANSPORT_a7aa037_v1.md\n"
    if anchor not in registry:
        raise SystemExit("registry prior review evidence anchor missing")
    registry = registry.replace(anchor, anchor + f"    review_evidence: {EVIDENCE}\n", 1)
registry_path.write_text(registry)

current = f'''# Current Implementation State — Derived Handoff Snapshot

> **DERIVED / NON-AUTHORITATIVE REPORTING ONLY**
> Runtime authority: `project_control/AUTONOMY_RUN_STATE.yaml`.
> DAG/task/slice authority: `project_control/TASK_REGISTRY.yaml` and `project_control/SLICE_REGISTRY.yaml`.
> Exact code/history authority: Git.

## SLICE-06 / TASK-S06-001 — ACCEPTED

TASK-S06-001 remains accepted at `59be9b2c92906065b8e4baa902fcec1d4cbefa12` / `checkpoint/S06-001-accepted-001`.

## SLICE-06 / TASK-S06-002 — R3 REPAIR ACTIVE

- Independent R2 review target: `{CANDIDATE}`.
- R2 verdict: **BLOCKING_REPAIR**; `SOURCE_REOPEN_REQUIRED=false`.
- Reviewer persistence: `UNAVAILABLE`; Owner-transported evidence is recorded at `{EVIDENCE}`.
- Four remaining blockers: Unit/User/Application durable-history lock graph; Interview participant/actor-FK row→advisory ordering; dormant add/re-add inactive-selection race; first-bind post-lock trusted Auth evidence freshness.
- Prior exact producer verifier `34621266079` remains evidence only and is not acceptance.
- Task branch remains `oanhpham-kobe/TASK-S06-002-user-rbac-identity`; next candidate is PENDING.
- Task registry status: `IN_PROGRESS`; repair round: `R3`.

## Next action

Repair all four R2 blockers append-only on the isolated task branch, add focused staged regressions, then rerun exact-SHA zero-state/static/web/database/concurrency verification before independent R3 review.

## Boundaries

- Do not push/merge `main` without explicit Owner authorization.
- Do not create/merge a PR in this phase.
- Do not deploy Vercel without explicit Owner authorization.
- Do not apply migrations to connected Supabase without explicit Owner authorization.
'''
Path("project_control/CURRENT_STATE.md").write_text(current)

evidence = f'''# TASK-S06-002 — Independent Implementation Review R2 Owner Transport

- WORK_ID: `S06-002-IMPLEMENTATION-REVIEW-001-R2`
- REVIEWER: `eiu-reviewer`
- REVIEWED_REPOSITORY: `oanhpham-kobe/eiu-recruitment`
- REVIEWED_BRANCH: `oanhpham-kobe/TASK-S06-002-user-rbac-identity`
- REVIEWED_SHA: `{CANDIDATE}`
- VERDICT: `BLOCKING_REPAIR`
- SOURCE_REOPEN_REQUIRED: `false`
- REVIEWER_EVIDENCE_PERSISTENCE: `UNAVAILABLE`
- COORDINATOR_PROVENANCE: `VERIFIED_FROM_OWNER_TRANSPORT`

This file records the independent verdict returned through the Owner transport. It is not evidence that the reviewer wrote to GitHub.

## Blocking findings

1. **Unit-history lock graph** — lifecycle/RBAC commands hold target User row + Internal User advisory before final `app_users` update; accepted durable-reference history then key-shares unchanged `unit_id`, while `bulk_create_or_update_applications()` locks Unit before HR owner User. This leaves deterministic Unit→User / User→Unit deadlock potential. Repair the complete Unit/User/Application graph while preserving S06-001 durable history and active-master validation, with staged bulk-assignment vs lifecycle and HR-role-removal regressions using a non-null Unit.
2. **Interview operationalization ordering** — resource-blocking Interview trigger takes Internal User advisory locks before participant/actor FK User-row locks. An HR who is also a current participant can race Root lifecycle administration into advisory↔FK-row deadlock during schedule/uncancel. Repair to shared row→advisory→revalidate order and test the public-command race.
3. **Dormant new-selection race** — dormant/CANCELLED/unscheduled/elapsed historical remove/reorder maintenance is correctly allowed, but new add/re-add/restoration can read Active before deactivation commits and then insert/restore after deactivation because the post-statement resource-blocking check is skipped. Distinguish unchanged history maintenance from new selection/restoration; serialize and post-lock revalidate new selections regardless of schedule status. Add deactivation-first CANCELLED and unscheduled add/re-add races.
4. **First-bind Auth freshness** — first Google bind verifies trusted Auth evidence before normalized-email/User/advisory locking but does not repeat `private.verified_google_auth_email(auth.uid())` after the full lock set. Re-run trusted evidence post-lock, require equality with the advisory-key email, fail closed on change, and test staged Auth evidence mutation while waiting.

## Non-blocking observations

- Candidate-contained R2 gate, R1 gate, and Owner-transported R1 evidence are present; R1 artifact blocker is closed.
- Raw `app_users.auth_user_id` consumer regression is statically closed; authenticated remains denied direct column access and inspected Internal User consumers use trusted session/binding RPCs.
- Original first-bind/rebind normalized-email resource-order inversion is repaired; only first-bind Auth evidence freshness remains.
- No canonical business/security/product contradiction was identified.

## Reviewer verification statement

The reviewer checked detached HEAD equality to `{CANDIDATE}`, inspected effective R2 source and targeted tests, and reported `git diff --check` success. Local runtime SQL was not executed because Docker Desktop Linux engine was unavailable. Producer CI evidence was treated as context only, not acceptance.

## Acceptance statement

`{CANDIDATE}` must not proceed to governed product integration. Repair the four findings, retain narrow binding ACL and allowed dormant-history maintenance, rerun exact-SHA verification, and submit a new immutable candidate for independent review. Canonical source reopening is not required.
'''
Path(EVIDENCE).write_text(evidence)
