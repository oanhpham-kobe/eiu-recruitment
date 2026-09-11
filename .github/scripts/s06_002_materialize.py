from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

BASE = "28e4baf8821c95a332dfcd390718b6af0a14a9bb"
PROMPT = "project_control/prompts/SLICE-06_TASK-002_v1.md"
REVIEW_GATE = "project_control/reviews/S06_002_PROMPT_REVIEW_GATE_v1.md"


def replace_one(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match, got {count}")
    return text.replace(old, new, 1)


def phase1() -> None:
    src = Path("/tmp/SLICE-06_TASK-002_v1.md")
    if not src.exists():
        raise SystemExit("staged prompt missing")
    dst = Path(PROMPT)
    if dst.exists():
        raise SystemExit(f"prompt already exists: {PROMPT}")
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)

    task_path = Path("project_control/TASK_REGISTRY.yaml")
    tasks = task_path.read_text(encoding="utf-8")
    if "  TASK-S06-002:\n" in tasks:
        raise SystemExit("TASK-S06-002 already materialized")
    if not tasks.endswith("\n"):
        tasks += "\n"
    tasks += """
  TASK-S06-002:
    title: "Internal User Directory, HR RBAC & Identity Lifecycle Trusted Contracts"
    slice: SLICE-06
    status: READY
    lane: LANE_A
    depends_on:
      - TASK-S06-001
    prompt: project_control/prompts/SLICE-06_TASK-002_v1.md
    prompt_review_status: "WAITING_EXTERNAL_REVIEW"
    notes: "High-risk shared backend/security prerequisite for Internal User directory lifecycle, HR role/permission administration, first-Google-login hardening, bound non-Root identity change, minimum-safe permission visibility, and race-safe owner/participant lifecycle guards. No Users/Permissions UI, main mutation, deployment, or connected Supabase migration application in this task."
"""
    task_path.write_text(tasks, encoding="utf-8")

    slice_path = Path("project_control/SLICE_REGISTRY.yaml")
    slices = slice_path.read_text(encoding="utf-8")
    slices = replace_one(
        slices,
        "  SLICE-06: {name: Master Data / Users & Permissions, status: IN_PROGRESS, current_task: TASK-S06-001}",
        "  SLICE-06: {name: Master Data / Users & Permissions, status: IN_PROGRESS, current_task: TASK-S06-002}",
        "slice_current_task",
    )
    slice_path.write_text(slices, encoding="utf-8")


def phase2() -> None:
    target = os.environ.get("TARGET_SHA", "").strip()
    if len(target) != 40:
        raise SystemExit("TARGET_SHA must be exact 40-char commit SHA")

    task_path = Path("project_control/TASK_REGISTRY.yaml")
    tasks = task_path.read_text(encoding="utf-8")
    tasks = replace_one(
        tasks,
        '    prompt_review_status: "WAITING_EXTERNAL_REVIEW"\n    notes:',
        f'    prompt_review_status: "WAITING_EXTERNAL_REVIEW (S06-002-PROMPT-REVIEW-001 @ {target})"\n    prompt_review_target_sha: "{target}"\n    notes:',
        "task_prompt_review_target",
    )
    task_path.write_text(tasks, encoding="utf-8")

    state_path = Path("project_control/AUTONOMY_RUN_STATE.yaml")
    state = state_path.read_text(encoding="utf-8")
    state = replace_one(
        state,
        '  current_prompt_review_target_sha: "68d96b39e309ee6f1edbe6cf4031c10a583b0269"',
        f'  current_prompt_review_target_sha: "{target}"',
        "current_prompt_review_target_sha",
    )
    state = replace_one(
        state,
        "  materialized_task: TASK-S06-001\n  task_status: DONE\n  prompt: project_control/prompts/SLICE-06_TASK-001_v2.md",
        "  materialized_task: TASK-S06-002\n  task_status: READY\n  prompt: project_control/prompts/SLICE-06_TASK-002_v1.md",
        "slice_06_current_materialization",
    )
    state = replace_one(
        state,
        '  reconciliation_note: "Accepted Slice-01 users.directory_read technical helper is intentionally left untouched by S06-001 and must be reconciled in the later User/Identity/RBAC task against current permission-detail visibility rules."',
        '  reconciliation_note: "TASK-S06-002 is now materialized as the governed User/Identity/RBAC reconciliation task. It must reconcile accepted Slice-01 first-login proof and permission-detail visibility against current canonical source without rewriting accepted migration history."',
        "reconciliation_note",
    )

    s06_002_block = f'''s06_002_planning:
  status: WAITING_EXTERNAL_REVIEW
  task: TASK-S06-002
  title: "Internal User Directory, HR RBAC & Identity Lifecycle Trusted Contracts"
  prompt: {PROMPT}
  prompt_review_target_sha: "{target}"
  prompt_review:
    work_id: S06-002-PROMPT-REVIEW-001
    reviewer: eiu-reviewer
    review_type: PROMPT_SOURCE_RECONCILIATION
    result: PENDING
    source_reopen_required: PENDING
    blocking_findings: PENDING
    handoff: {REVIEW_GATE}
  source_reopen_expectation: false
  accepted_prerequisites:
    - "TASK-S06-001 accepted @ 59be9b2c92906065b8e4baa902fcec1d4cbefa12"
    - "accepted Slice-01 identity/auth schema and Internal first-login provisioning"
    - "accepted Application owner and Interview participant/resource lifecycle contracts"
  known_reconciliation_targets:
    - "Accepted first-login bind must be hardened to current canonical verified Google-provider + confirmed EIU email proof without creating a divergent bind path."
    - "Non-root directory management must not expose another user's granular effective permissions/security identity; inactive lifecycle management still needs a minimum-safe read surface."
    - "User deactivation/HR-role removal must be concurrency-safe against new Active Application owner assignment and new/current non-elapsed resource-blocking Interview participation."
  implementation_hold: "No TASK-S06-002 implementation may start before independent prompt/source reconciliation PASS with SOURCE_REOPEN_REQUIRED=false."

'''
    if "s06_002_planning:\n" in state:
        raise SystemExit("s06_002_planning already exists")
    state = replace_one(
        state,
        "implementation_materialization:\n",
        s06_002_block + "implementation_materialization:\n",
        "insert_s06_002_planning",
    )

    old_frontier = '''safe_frontier:
  eligible_tasks: []
  skipped_due_to_dependency: []
  materialization_frontier: []
  execution_hold: "TASK-S06-001 is accepted. No later Slice-06 implementation task is materialized yet; derive the next governed frontier before implementation."

stop_gate:
  status: CLEAR
  type: NONE
  work_id: S06-001-FINAL-INTEGRATION-EQUIVALENCE-001
  target: "TASK-S06-001 final integration 59be9b2c92906065b8e4baa902fcec1d4cbefa12"
  reviewer: eiu-reviewer
  source_reopen_required: false
  resume_on: "No S06-001 hold remains; acceptance is complete at checkpoint/S06-001-accepted-001."

next_action: "Materialize the next governed Slice-06 task from the canonical Slice-06 scope split and registries before implementation. Preserve governance boundaries: do not push/merge main, deploy Vercel, or apply connected Supabase migrations without explicit Owner authorization."'''
    new_frontier = f'''safe_frontier:
  eligible_tasks: []
  skipped_due_to_dependency: []
  materialization_frontier: []
  execution_hold: "TASK-S06-002 is materialized but blocked on independent prompt/source reconciliation review of exact target {target}."

stop_gate:
  status: WAITING_EXTERNAL_REVIEW
  type: INDEPENDENT_PROMPT_SOURCE_REVIEW
  work_id: S06-002-PROMPT-REVIEW-001
  target: "TASK-S06-002 prompt/source reconciliation @ {target}"
  reviewer: eiu-reviewer
  source_reopen_required: PENDING
  resume_on: "Independent reviewer PASS + SOURCE_REOPEN_REQUIRED=false for exact prompt-review target {target}; on BLOCKING_REPAIR repair only the prompt/control scope and re-review; on OWNER_DECISION_REQUIRED stop for Owner."

next_action: "Send {REVIEW_GATE} to OMP main/eiu-reviewer for exact-target S06-002 prompt/source reconciliation review. Do not begin implementation before PASS + SOURCE_REOPEN_REQUIRED=false. Preserve boundaries: do not push/merge main, deploy Vercel, or apply connected Supabase migrations without explicit Owner authorization."'''
    state = replace_one(state, old_frontier, new_frontier, "safe_frontier_stop_gate")
    state_path.write_text(state, encoding="utf-8")

    current = f'''# Current Implementation State — Derived Handoff Snapshot

> **DERIVED / NON-AUTHORITATIVE REPORTING ONLY**
> Runtime authority: `project_control/AUTONOMY_RUN_STATE.yaml`.
> DAG/task/slice authority: `project_control/TASK_REGISTRY.yaml` and `project_control/SLICE_REGISTRY.yaml`.
> Exact code/history authority: Git.

## SLICE-06 / TASK-S06-001 — ACCEPTED

TASK-S06-001 **Master Data Lifecycle & Historical Semantics Trusted Contracts** remains accepted.

- Final acceptance SHA / immutable checkpoint: `59be9b2c92906065b8e4baa902fcec1d4cbefa12` / `checkpoint/S06-001-accepted-001`.
- Final integration-equivalence review: PASS, `SOURCE_REOPEN_REQUIRED=false`.
- Integration CI `34579159091`: PASS.
- Governance CI `34579159098`: PASS.

## SLICE-06 / TASK-S06-002 — PROMPT/SOURCE REVIEW GATE

TASK-S06-002 **Internal User Directory, HR RBAC & Identity Lifecycle Trusted Contracts** is materialized as the next governed security/backend task.

- Prompt: `{PROMPT}`.
- Exact prompt-review target: `{target}`.
- Review work ID: `S06-002-PROMPT-REVIEW-001`.
- Reviewer: `eiu-reviewer` (read-only independent review).
- Handoff: `{REVIEW_GATE}`.
- Current gate: `WAITING_EXTERNAL_REVIEW`.
- Implementation has **not** started and must not start before `PASS + SOURCE_REOPEN_REQUIRED=false`.

The prompt explicitly reconciles the accepted Slice-01 first-login implementation with current verified-Google/confirmed-email requirements, tightens non-root permission-detail visibility, and requires race-safe Internal User deactivation/HR-role removal against Active Application ownership and non-elapsed resource-blocking Interview participation.

## Next action

Send the persisted S06-002 prompt-review handoff to OMP main / `eiu-reviewer` and return the complete structured verdict. On `BLOCKING_REPAIR`, repair only prompt/control scope and re-review. On `OWNER_DECISION_REQUIRED`, stop for Owner. On PASS with `SOURCE_REOPEN_REQUIRED=false`, create the immutable pre-task checkpoint and isolated implementation branch before any product mutation.

## Boundaries

- Do not push/merge `main` without explicit Owner authorization.
- Do not deploy Vercel without explicit Owner authorization.
- Do not apply migrations to connected Supabase without explicit Owner authorization.
'''
    Path("project_control/CURRENT_STATE.md").write_text(current, encoding="utf-8")

    handoff = f'''# TASK-S06-002 — Independent Prompt & Source Reconciliation Review Handoff

## Review identity

- WORK_ID: `S06-002-PROMPT-REVIEW-001`
- REVIEW_TYPE: `PROMPT_SOURCE_RECONCILIATION`
- REPOSITORY: `oanhpham-kobe/eiu-recruitment`
- INTEGRATION_BRANCH: `autonomy/continuous-integration-20260905-01`
- REVIEWED_SHA: `{target}`
- PROMPT: `{PROMPT}`
- REVIEWER: `eiu-reviewer` (read-only)

Review the exact prompt artifact and repository sources at the exact reviewed SHA. Do not review a moving branch tip as a substitute for `{target}`.

## Canonical source authority

Read the current versions at `{target}` of:

1. `recruitment_webapp/review_pack/02_ROLES_PERMISSIONS_AND_NAVIGATION.md`
2. `recruitment_webapp/review_pack/08_DATA_MODEL_AND_FIELD_DICTIONARY.md`
3. `recruitment_webapp/review_pack/13_ACCEPTANCE_CRITERIA_AND_TEST_CASES.md`
4. `recruitment_webapp/review_pack/37_BACKEND_COMMAND_CONTRACTS.md`
5. `recruitment_webapp/review_pack/39_SECURITY_RLS_MATRIX.md`
6. `recruitment_webapp/review_pack/40_DATABASE_INVARIANTS.md`
7. `recruitment_webapp/review_pack/46_AUTH_IDENTITY_MODEL.md`
8. `recruitment_webapp/review_pack/55_COMMAND_COVERAGE_MATRIX.md`
9. `recruitment_webapp/review_pack/59_RLS_POLICY_BLUEPRINT.md`
10. `recruitment_webapp/review_pack/61_ROOT_ADMIN_BREAK_GLASS_RECOVERY.md`
11. `recruitment_webapp/review_pack/73_DOMAIN_GLOSSARY_AND_CANONICAL_PREDICATES.md`
12. `recruitment_webapp/review_pack/100_TECHNICAL_PRECODE_GATE_V1_18.md`
13. `recruitment_webapp/review_pack/command_registry.yaml`
14. `recruitment_webapp/review_pack/database_schema.sql`
15. accepted migrations/tests on `{target}`, especially Slice-01 identity/provisioning and accepted Application/Interview lifecycle contracts.

## Accepted prerequisites that must not be silently reopened

- TASK-S06-001 accepted at `59be9b2c92906065b8e4baa902fcec1d4cbefa12` / `checkpoint/S06-001-accepted-001`.
- Accepted identity/auth tables, Root uniqueness, direct-DML revokes and authorization helpers from Slice 01.
- Accepted Application-owner and Interview-participant/resource concurrency/business behavior from later slices.
- Accepted audit, idempotency and optimistic-concurrency primitives.

## Required review scope

Assess whether the prompt is sufficient, internally consistent and canonically faithful before any implementation begins. In particular inspect:

1. **Scope split** — backend/security prerequisite only; no Users/Permissions UI, RBAC redesign, ordinary Root break-glass RPC, deployment, connected Supabase application, or main mutation.
2. **First Google login reconciliation** — accepted Slice-01 bind path is preserved/repaired rather than duplicated; current canonical Google-provider + confirmed/verified EIU email proof is explicit; user-editable metadata is not trusted for authorization/security identity.
3. **Bound identity change** — Root-only for already-bound non-Root users, collision/takeover safe, Root identity excluded to break-glass, no secret exposure or false cross-system atomicity claim.
4. **Permission-detail visibility** — non-root directory management gets only minimum directory/lifecycle information and cannot enumerate another user's granular permissions/security binding; Root full admin and own-permission reads remain possible; inactive-user lifecycle management is not accidentally made impossible.
5. **Directory command boundaries** — create/update/Active semantics cannot mutate roles, permissions, Root state or bound identity through a business-profile command; optimistic concurrency is sufficient.
6. **HR role lifecycle** — Root-only assign/remove, Full HR default set and exclusions, Active target rules, role removal permission cleanup, historical preservation, Active Application owner safety.
7. **Granular permission dependencies** — Root-only grant/revoke, Root-only codes non-delegable, dependency graph enforced server-side, concurrency/idempotency behavior is explicit enough to avoid impossible states.
8. **Lifecycle concurrency** — deactivation/HR-role removal cannot race with new Active Application ownership or new/current non-elapsed resource-blocking Interview participation; prompt requires a shared deterministic serialization mechanism while preserving accepted lock order and avoiding deadlocks.
9. **RLS/ACL/SECURITY DEFINER safety** — no broad authenticated authorization, no direct DML widening, explicit execute ACLs, empty search path, safe views/projections, service-role/server authorization remains explicit.
10. **Idempotency/audit/errors** — replay never substitutes for authorization/stale checks, audit is same trusted boundary, stable errors and no raw internal leakage.
11. **Regression sufficiency** — tests cover target classes, races, first-bind competition, identity takeover, visibility, direct DML/ACLs and directly affected accepted Application/Interview/Auth/S06 behavior.
12. **Source reopening** — determine whether any real canonical contradiction requires source reopening. Do not request source reopening for ordinary implementation difficulty.

## Known producer reconciliation observations

These are observations to verify, not findings the reviewer must accept without checking:

- Accepted Slice-01 `public.provision_internal_user_identity()` already has useful row locking/domain/Active/conflicting-bind behavior but appears weaker than current canonical source on explicit Google-provider + confirmed-email proof.
- Accepted Slice-01 permission-read policy appears broader than current canonical permission-detail visibility because directory read can expose another user's granular permission rows.
- User lifecycle must compose with accepted Application owner and Interview participant/resource contracts; UI-only checks are insufficient under concurrent writes.

## Required structured verdict

Return the complete result in this structure:

```text
WORK_ID: S06-002-PROMPT-REVIEW-001
REVIEWED_REPOSITORY: oanhpham-kobe/eiu-recruitment
REVIEWED_BRANCH: autonomy/continuous-integration-20260905-01
REVIEWED_SHA: {target}
REVIEW_TYPE: PROMPT_SOURCE_RECONCILIATION
VERDICT: PASS | BLOCKING_REPAIR | OWNER_DECISION_REQUIRED
SOURCE_REOPEN_REQUIRED: true | false

BLOCKING_FINDINGS:
- ... or None.

NON_BLOCKING_OBSERVATIONS:
- ... or None.

SOURCE_RECONCILIATION_ASSESSMENT:
- ...

SECURITY_AUTHORIZATION_ASSESSMENT:
- ...

CONCURRENCY_LIFECYCLE_ASSESSMENT:
- ...

TEST_ACCEPTANCE_ASSESSMENT:
- ...

SCOPE_GOVERNANCE_ASSESSMENT:
- ...

ACCEPTANCE_STATEMENT:
- State whether `{PROMPT}` at exact SHA `{target}` is safe to release for implementation without canonical-source reopening.

EVIDENCE_PERSISTENCE:
- GitHub-visible evidence coordinates if OMP main persists them, otherwise UNAVAILABLE.
```

## Evidence persistence

Reviewer itself stays read-only. OMP main owns persistence. If GitHub-visible review evidence is persisted, use a non-candidate evidence branch such as `review/S06-002-PROMPT-{target[:7]}-v1` and an artifact such as `project_control/reviews/S06_002_PROMPT_REVIEW_{target[:7]}_v1.md`. Do not mutate the reviewed target to persist evidence.

## Do-not-cross boundaries

- Do not implement or repair product/database code in this review.
- Do not move integration/task/checkpoint refs from the reviewer.
- Do not push/merge `main`.
- Do not deploy Vercel.
- Do not apply migrations to connected Supabase.
- Do not treat this transport handoff as review evidence by itself.
'''
    review_path = Path(REVIEW_GATE)
    review_path.parent.mkdir(parents=True, exist_ok=True)
    review_path.write_text(handoff, encoding="utf-8")


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in {"phase1", "phase2"}:
        raise SystemExit("usage: s06_002_materialize.py phase1|phase2")
    if sys.argv[1] == "phase1":
        phase1()
    else:
        phase2()
