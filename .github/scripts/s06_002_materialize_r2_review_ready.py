from pathlib import Path

CANDIDATE = "7c37d46fa504b5d98b156735d7355f1d938be0bf"
R1 = "a7aa037e26cda6ba70153539c1dfc15c3fba37e6"
VERIFY_RUN = "34621266079"
HANDOFF = "project_control/reviews/S06_002_IMPLEMENTATION_R2_HANDOFF_7c37d46_v1.md"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


# AUTONOMY_RUN_STATE.yaml
p = Path("project_control/AUTONOMY_RUN_STATE.yaml")
text = p.read_text(encoding="utf-8")
section = text.index("s06_002_planning:")
prefix = text[:section]
s = text[section:]
s = replace_once(
    s,
    "s06_002_planning:\n  status: IMPLEMENTATION_REPAIR_ACTIVE",
    "s06_002_planning:\n  status: WAITING_INDEPENDENT_REVIEW",
    "run-state planning status",
)
s = replace_once(
    s,
    '  implementation_hold: "CLEARED FOR REPAIR — R1 independent implementation review returned BLOCKING_REPAIR with SOURCE_REOPEN_REQUIRED=false; repair remains confined to the isolated TASK-S06-002 branch."',
    '  implementation_hold: "HELD PENDING R2 INDEPENDENT REVIEW — exact candidate 7c37d46fa504b5d98b156735d7355f1d938be0bf is producer-verified but not accepted or integrated."',
    "run-state implementation hold",
)
start = s.index("  implementation_candidate:\n")
end = s.index("  independent_implementation_review:\n", start)
new_candidate = f'''  implementation_candidate:
    branch: oanhpham-kobe/TASK-S06-002-user-rbac-identity
    baseline_sha: "0a2ccdfedc477f9766c9aaa03739d16a7ed83c01"
    prior_candidate_sha: "{R1}"
    candidate_sha: "{CANDIDATE}"
    changed_files_count: 32
    source_reopen_required: false
    repair_round: R2
    producer_verification:
      exact_verifier_run: "{VERIFY_RUN} PASS"
      exact_verified_sha: "{CANDIDATE}"
      static: "PASS — exact SHA, candidate-contained review artifacts, baseline diff hygiene, three-file test-only tail, and no retained raw app_users.auth_user_id request-scoped server consumers"
      web: "PASS — npm ci, npm audit --audit-level=high, design:check, lint, typecheck, build, Chromium install, full npm run test"
      database: "PASS — Supabase 2.116.0 start, zero-state db reset, focused Internal User/RBAC/Identity plus dormant-history regression, public-command concurrency, crossed Application/Interview/copy/bulk regressions, retained S06-001 regressions, db lint --level error, clean stop"
    review_package: project_control/reviews/S06_002_IMPLEMENTATION_R2_GATE_v1.md
    coordinator_handoff: {HANDOFF}
'''
s = s[:start] + new_candidate + s[end:]
insert_at = s.index("implementation_materialization:\n")
r2_pending = f'''r2_independent_implementation_review:
  work_id: S06-002-IMPLEMENTATION-REVIEW-001-R2
  reviewer: eiu-reviewer
  status: PENDING
  reviewed_sha: "{CANDIDATE}"
  result: PENDING
  source_reopen_required: false
  review_gate: project_control/reviews/S06_002_IMPLEMENTATION_R2_GATE_v1.md
  coordinator_handoff: {HANDOFF}
  acceptance_rule: "No product serialization into integration until an independent exact-SHA PASS is returned and truthfully persisted."

'''
s = s[:insert_at] + r2_pending + s[insert_at:]
s = replace_once(
    s,
    f'''  status: COMPLETE
  prior_candidate_sha: "{R1}"
  current_candidate_sha: PENDING
  review_round: R2''',
    f'''  status: WAITING_INDEPENDENT_REVIEW
  prior_candidate_sha: "{R1}"
  current_candidate_sha: "{CANDIDATE}"
  exact_verifier_run: "{VERIFY_RUN} PASS"
  review_round: R2''',
    "run-state implementation materialization",
)
frontier = s.index("safe_frontier:\n")
new_tail = f'''safe_frontier:
  eligible_tasks: []
  skipped_due_to_dependency: []
  materialization_frontier: []
  execution_hold: "TASK-S06-002 R2 candidate {CANDIDATE} passed exact producer verification run {VERIFY_RUN}; later Slice-06 work remains held pending independent exact-SHA R2 review."

stop_gate:
  status: WAITING_EXTERNAL_REVIEW
  type: INDEPENDENT_IMPLEMENTATION_REVIEW
  work_id: S06-002-IMPLEMENTATION-REVIEW-001-R2
  target: "{CANDIDATE}"
  reviewer: eiu-reviewer
  source_reopen_required: false
  resume_on: "Independent exact-SHA R2 verdict for {CANDIDATE}. PASS may advance to governed product serialization; any blocker returns to repair without source reopen unless reviewer explicitly requires it."

next_action: "Obtain independent implementation re-review S06-002-IMPLEMENTATION-REVIEW-001-R2 on exact task-branch SHA {CANDIDATE} using {HANDOFF}. Do not serialize product into integration before PASS; do not push/merge main, create/merge a PR, deploy Vercel, or apply connected Supabase migrations."
'''
s = s[:frontier] + new_tail
p.write_text(prefix + s, encoding="utf-8")

# TASK_REGISTRY.yaml
p = Path("project_control/TASK_REGISTRY.yaml")
text = p.read_text(encoding="utf-8")
section = text.index("  TASK-S06-002:\n")
prefix = text[:section]
s = text[section:]
s = replace_once(s, "    status: IN_PROGRESS", "    status: REVIEW", "task status")
old = f'''    prior_implementation_candidate_sha: "{R1}"
    implementation_candidate_sha: PENDING
    repair_round: R2
    review_status: "BLOCKING_REPAIR (S06-002-IMPLEMENTATION-REVIEW-001 @ {R1}; SOURCE_REOPEN_REQUIRED=false; evidence persistence unavailable)"
    review_evidence: project_control/reviews/S06_002_IMPLEMENTATION_REVIEW_OWNER_TRANSPORT_a7aa037_v1.md
    prior_producer_verification: "PASS (final exact DB/static verifier run 34611668782; exact prior web job 34602347683/103272463530 PASS on web-equivalent 014e22f737463b049eacca041a0c204ce0699cd1)"
    notes: "High-risk shared backend/security prerequisite for Internal User directory lifecycle, HR role/permission administration, first-Google-login hardening, bound non-Root identity change, minimum-safe permission visibility, and race-safe owner/participant lifecycle guards. No Users/Permissions UI, main mutation, deployment, or connected Supabase migration application in this task."'''
new = f'''    prior_implementation_candidate_sha: "{R1}"
    implementation_candidate_sha: "{CANDIDATE}"
    repair_round: R2
    review_status: "WAITING_INDEPENDENT_REVIEW (S06-002-IMPLEMENTATION-REVIEW-001-R2 @ {CANDIDATE}); R1 was BLOCKING_REPAIR with SOURCE_REOPEN_REQUIRED=false"
    prior_review_evidence: project_control/reviews/S06_002_IMPLEMENTATION_REVIEW_OWNER_TRANSPORT_a7aa037_v1.md
    review_gate: project_control/reviews/S06_002_IMPLEMENTATION_R2_GATE_v1.md
    review_handoff: {HANDOFF}
    producer_verification: "PASS (exact verifier run {VERIFY_RUN}: static PASS, full web PASS, zero-state/focused/concurrency/crossed/S06-001 DB regressions PASS, db lint PASS; exact SHA {CANDIDATE})"
    notes: "R2 repairs all five R1 blockers without source reopen: candidate-contained review evidence/gate; trusted current-session/current-binding RPC migration after auth_user_id ACL narrowing; resource_blocking-only participant recheck; deterministic owner/lifecycle row->advisory ordering; deterministic first-bind/rebind email->row->user-advisory ordering. Candidate is producer-verified only and must not enter governed integration before independent exact-SHA PASS. No Users/Permissions UI, main mutation, PR, deployment, or connected Supabase migration application occurred."'''
s = replace_once(s, old, new, "task candidate/review block")
p.write_text(prefix + s, encoding="utf-8")

# CURRENT_STATE.md is derived; rewrite it compactly and exactly.
Path("project_control/CURRENT_STATE.md").write_text(f'''# Current Implementation State — Derived Handoff Snapshot

> **DERIVED / NON-AUTHORITATIVE REPORTING ONLY**
> Runtime authority: `project_control/AUTONOMY_RUN_STATE.yaml`.
> DAG/task/slice authority: `project_control/TASK_REGISTRY.yaml` and `project_control/SLICE_REGISTRY.yaml`.
> Exact code/history authority: Git.

## SLICE-06 / TASK-S06-001 — ACCEPTED

TASK-S06-001 remains accepted at `59be9b2c92906065b8e4baa902fcec1d4cbefa12` / `checkpoint/S06-001-accepted-001`.

## SLICE-06 / TASK-S06-002 — WAITING INDEPENDENT R2 REVIEW

- R1 reviewed candidate: `{R1}` — `BLOCKING_REPAIR`, `SOURCE_REOPEN_REQUIRED=false`.
- R2 exact candidate: `{CANDIDATE}` on `oanhpham-kobe/TASK-S06-002-user-rbac-identity`.
- R2 producer verification: **PASS**, exact verifier run `{VERIFY_RUN}`.
- Static gate: PASS — candidate-contained R1 evidence/R2 gate, diff hygiene, affected-consumer scan.
- Web gate: PASS — install/audit/design/lint/typecheck/build/Chromium/full tests.
- Database gate: PASS — zero-state replay; focused Internal User/RBAC/Identity; dormant-history; public-command concurrency; crossed Application/Interview/copy/bulk; retained S06-001 regressions; DB lint.
- Review handoff: `{HANDOFF}`.
- Task registry status: `REVIEW`; independent work ID: `S06-002-IMPLEMENTATION-REVIEW-001-R2`.
- Candidate is **not accepted** and its product diff has **not** been serialized into integration.

## Next action

Independent reviewer must inspect exact SHA `{CANDIDATE}` and return `PASS` or blockers. Only an exact-SHA independent PASS may advance to governed product serialization/integration-equivalence checks.

## Boundaries

- Do not push/merge `main` without explicit Owner authorization.
- Do not create/merge a PR in this phase.
- Do not deploy Vercel without explicit Owner authorization.
- Do not apply migrations to connected Supabase without explicit Owner authorization.
''', encoding="utf-8")

# Exact coordinator handoff. This is control evidence, not reviewer-authored evidence.
Path(HANDOFF).write_text(f'''# TASK-S06-002 — Independent Implementation Re-Review Handoff R2

## Immutable review target

- WORK_ID: `S06-002-IMPLEMENTATION-REVIEW-001-R2`
- REPOSITORY: `oanhpham-kobe/eiu-recruitment`
- BRANCH: `oanhpham-kobe/TASK-S06-002-user-rbac-identity`
- EXACT_REVIEW_SHA: `{CANDIDATE}`
- BASELINE_SHA: `0a2ccdfedc477f9766c9aaa03739d16a7ed83c01`
- R1_REVIEWED_SHA: `{R1}`
- R1_VERDICT: `BLOCKING_REPAIR`
- R1_SOURCE_REOPEN_REQUIRED: `false`
- CANDIDATE_CONTAINS_R2_GATE: `project_control/reviews/S06_002_IMPLEMENTATION_R2_GATE_v1.md`
- COORDINATOR_PRODUCER_VERIFIER: GitHub Actions run `{VERIFY_RUN}`

The reviewer must independently verify `git rev-parse HEAD` equals `{CANDIDATE}`. This handoff is coordinator-authored routing evidence, not reviewer evidence and not an acceptance claim.

## R1 blockers to re-review

1. **Immutable review gate/evidence** — R1 Owner-transported verdict evidence, the R1 gate, and the generic R2 gate now live inside the candidate tree. The exact SHA is supplied here because a commit cannot embed its own future hash.
2. **RLS/column-ACL consumer migration** — authenticated raw `public.app_users.auth_user_id` access remains narrowed; retained request-scoped server consumers were migrated to minimum-safe `get_current_internal_session()` / `get_current_internal_binding_status()` RPCs and related tests were reconciled.
3. **Dormant participant history** — statement-level current-participant eligibility recheck is scoped to canonical `resource_blocking` Interviews so CANCELLED/inactive/unscheduled/fully elapsed history can be maintained without re-selecting inactive historical participants.
4. **Application owner/lifecycle lock order** — owner writers acquire target `app_users` row before shared Internal User advisory serialization and revalidate after the full lock set, matching lifecycle/RBAC order.
5. **First-bind/Root-rebind lock order** — both identity paths use normalized-email advisory before target directory row, then Internal User advisory, with trusted Auth evidence revalidation.

## Producer verification evidence — exact SHA only

GitHub Actions run `{VERIFY_RUN}` checked out `{CANDIDATE}` independently in all jobs and completed PASS:

- static job `103335549527`: exact SHA, `git diff --check`, candidate-contained review artifacts, R2 three-test-file tail, and no retained raw `app_users.auth_user_id` query in the affected request-scoped production paths;
- web job `103335549460`: `npm ci`, `npm audit --audit-level=high`, design check, lint, typecheck, production build, Playwright Chromium install, and full `npm run test` — PASS;
- database job `103335549295`: Supabase CLI `2.116.0`, local start, zero-state `supabase db reset`, focused Internal User/RBAC/Identity + dormant-history regression, lifecycle/public-command concurrency, Application reactivation/participant, Interview lifecycle, round/conflict, copy, bulk assignment, all retained S06-001 seed/lifecycle/durable-history regressions, `supabase db lint --local --level error`, and clean local stop — PASS.

The candidate is 17 commits ahead of the pre-task baseline and changes 32 files. The R2 technical repair was append-only; accepted migration history was not rewritten.

## Independent review instructions

Review the exact candidate rather than trusting producer verification. Re-read the five R1 blockers against effective code and public command paths, including lock ordering across lifecycle/owner/participant/identity writers, RLS/column privileges, trusted session projections, dormant-history behavior, Root protections, idempotency, audit behavior, and accepted S06-001/Application/Interview contract reuse.

Return at minimum:

- `WORK_ID`
- `REVIEWED_REPOSITORY`
- `REVIEWED_BRANCH`
- `REVIEWED_SHA`
- `VERDICT` (`PASS` or `BLOCKING_REPAIR`)
- `SOURCE_REOPEN_REQUIRED`
- `BLOCKING_FINDINGS`
- `NON_BLOCKING_OBSERVATIONS`
- `VERIFICATION_EXECUTED`
- `IDENTITY_BIND_ASSESSMENT`
- `RBAC_VISIBILITY_ASSESSMENT`
- `LIFECYCLE_CONCURRENCY_ASSESSMENT`
- `SECURITY_ASSESSMENT`
- `ACCEPTED_CONTRACT_REUSE_ASSESSMENT`
- `ACCEPTANCE_STATEMENT`
- `EVIDENCE_PERSISTENCE` with truthful coordinates or `UNAVAILABLE`.

## Governance boundary

Reviewer is read-only. Do not modify implementation, refs, integration, `main`, PRs, Vercel, connected Supabase, or later Slice-06 state. A producer-verified candidate remains unaccepted until this independent exact-SHA review returns PASS.
''', encoding="utf-8")
