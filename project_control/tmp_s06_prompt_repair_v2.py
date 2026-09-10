from pathlib import Path

OLD_SHA = '5abbb5181405e0f5a468176edd93db8226a3efd5'
V1 = Path('project_control/prompts/SLICE-06_TASK-001_v1.md')
V2 = Path('project_control/prompts/SLICE-06_TASK-001_v2.md')

# -----------------------------------------------------------------------------
# 1. Derive prompt v2 deterministically from reviewed v1.
# -----------------------------------------------------------------------------
s = V1.read_text()

anchor = '''Do not build a generic arbitrary-table administration API.\n\n## Create semantics\n'''
insert = '''Do not build a generic arbitrary-table administration API.\n\n## Idempotency / retry-replay contract\n\nThe three trusted Master Data mutations must define and implement repository-consistent idempotency wherever a client/server retry can repeat the same logical command. Do not treat optimistic versioning as a substitute for idempotency.\n\nFor `create_master_item`, `update_master_item`, and `delete_or_inactivate_master_item`:\n\n- accept an explicit idempotency key (or the exact accepted repository equivalent) for retryable mutation entry points;\n- scope the key so a replay cannot cross authenticated actor, command, or `master_type`; update/delete scope must also bind the exact target identity;\n- re-run authentication, Active Internal User validation, and effective `master_data.manage` authorization **before** returning any stored replay result; a caller who is no longer authorized must not obtain or trigger a replay result solely because the key exists;\n- after closed-allowlist routing and DTO normalization, compute a deterministic request fingerprint over every field that changes command meaning. For update/delete this includes target identity and `expected_version_no`; create includes the normalized per-type create DTO. Transport-only noise must not affect the fingerprint;\n- same idempotency key + same scope + same fingerprint after a previously committed success returns the atomically stored prior typed result and performs **no second business mutation, no additional version bump, and no duplicate audit event**;\n- same key in the same scope + different fingerprint must fail closed with the repository's existing stable idempotency/validation mismatch behavior (or the smallest stable implementation-level code if the accepted helper has no mismatch code). It must never silently replay the old result and must never execute the new mutation;\n- a different actor, command, `master_type`, or update/delete target cannot use another scope's replay record;\n- concurrent duplicate requests for the same key/scope/fingerprint must serialize through the accepted idempotency primitive or an equivalent unique/lock protocol so exactly one logical mutation/audit/result commits and every successful duplicate observes that same committed result;\n- a failed or rolled-back attempt must not create a reusable successful replay record;\n- the successful idempotency record/result, business mutation, optimistic-version effect, and audit event must commit atomically.\n\nPrefer the accepted repository idempotency primitive if one already exists and satisfies these rules; do not fork a second incompatible replay store.\n\n## Create semantics\n'''
if anchor not in s:
    raise SystemExit('generic-command anchor missing')
s = s.replace(anchor, insert, 1)

old_delete = '''`delete_or_inactivate_master_item` must lock and revalidate the target and then deterministically apply:\n\n- no business/reference usage → hard delete allowed;\n'''
new_delete = '''`delete_or_inactivate_master_item` must require `expected_version_no` (or the repository's exact canonical equivalent), lock the target row, and compare the current version **while that lock is held and before deciding hard-delete versus inactivation**. A stale request must fail with `STALE_VERSION` and must leave both master state and audit unchanged. Only after that optimistic-version check passes may the command deterministically apply:\n\n- no business/reference usage → hard delete allowed;\n'''
if old_delete not in s:
    raise SystemExit('delete semantics anchor missing')
s = s.replace(old_delete, new_delete, 1)

old_anon = '- `anon` receives no business-table access for this feature;\n'
new_anon = '- S06-001 creates **no new anonymous Master Data management surface** and grants `anon` no mutation/admin capability. Preserve any already-accepted anonymous active lookup reads required by existing Candidate workflows; do not revoke or widen those unrelated lookup grants as part of this task;\n'
if old_anon not in s:
    raise SystemExit('anon security line missing')
s = s.replace(old_anon, new_anon, 1)

old_tests = '''1. anon/no-auth/missing-permission denial;\n2. `master_data.manage` positive create/update/delete path;\n3. unknown master type / unknown fields rejected;\n4. optimistic stale update rejected with no partial write/audit drift;\n5. unreferenced master can hard-delete;\n6. referenced master becomes Inactive instead of being deleted;\n7. referenced structural mutation is rejected;\n8. allowed label-only correction on referenced row succeeds, version-bumps and audits;\n9. inactive item cannot be newly selected where canonical active selection is required;\n10. historical record with inactive master remains readable/operable;\n11. hierarchy invariants for Unit/Team/Position;\n12. Interview Format structural metadata history guard;\n13. Document Type scope structural history guard and explicit seed semantics;\n14. Room referenced identity-bearing field guard;\n15. authenticated role has no direct table DML and private helper ACLs cannot be used as bypass;\n16. Root obeys the same structural/history safety rules.\n'''
new_tests = '''1. anon/no-auth/missing-permission denial;\n2. `master_data.manage` positive create/update/delete path;\n3. unknown master type / unknown fields rejected;\n4. optimistic stale update rejected with no partial write/audit drift;\n5. stale unreferenced hard-delete request rejects with `STALE_VERSION` and no master/audit change;\n6. stale referenced inactivation request rejects with `STALE_VERSION` and no master/audit change;\n7. unreferenced master can hard-delete;\n8. referenced master becomes Inactive instead of being deleted;\n9. referenced structural mutation is rejected;\n10. allowed label-only correction on referenced row succeeds, version-bumps and audits;\n11. inactive item cannot be newly selected where canonical active selection is required;\n12. historical record with inactive master remains readable/operable;\n13. hierarchy invariants for Unit/Team/Position;\n14. Interview Format structural metadata history guard;\n15. Document Type scope structural history guard and explicit seed semantics;\n16. Room referenced identity-bearing field guard;\n17. authenticated role has no direct table DML and private helper ACLs cannot be used as bypass;\n18. Root obeys the same structural/history safety rules;\n19. sequential retry of the same successful idempotency key/scope/fingerprint returns the stored typed result with exactly one business mutation, one version effect and one audit event; cover all three command families across the focused suite;\n20. concurrent duplicate retry of the same key/scope/fingerprint commits exactly one logical mutation/audit/result and all successful duplicates observe the same result;\n21. same key/scope with a different fingerprint fails closed with no new mutation/audit;\n22. replay scope is isolated across actors, commands, `master_type`, and update/delete target identities; unauthorized callers cannot obtain a stored replay result;\n23. failed/rolled-back attempts do not create a successful replay record reusable by a later request.\n'''
if old_tests not in s:
    raise SystemExit('test list anchor missing')
s = s.replace(old_tests, new_tests, 1)

V2.write_text(s)

# -----------------------------------------------------------------------------
# 2. TASK_REGISTRY: point active planned task to v2 and record R1 repair.
# -----------------------------------------------------------------------------
p = Path('project_control/TASK_REGISTRY.yaml')
s = p.read_text()
start = s.index('  TASK-S06-001:\n')
head, block = s[:start], s[start:]
block = block.replace('    prompt: project_control/prompts/SLICE-06_TASK-001_v1.md\n', '    prompt: project_control/prompts/SLICE-06_TASK-001_v2.md\n', 1)
old = f'''    prompt_review_status: "WAITING_EXTERNAL_REVIEW (S06-001-PROMPT-REVIEW-001 @ {OLD_SHA})"\n    prompt_review_evidence: project_control/reviews/S06_001_PROMPT_REVIEW_GATE_5abbb51_v1.md\n'''
new = f'''    prior_prompt_review: "S06-001-PROMPT-REVIEW-001 @ {OLD_SHA} — BLOCKING_REPAIR; SOURCE_REOPEN_REQUIRED=false"\n    prior_prompt_review_evidence: "Owner transport; reviewer-reported review/S06-001-PROMPT-5abbb51-v1 @ a93659867e75f95109fa4826cb8b68114b031ddc was not GitHub-visible when Coordinator verified"\n    prompt_review_status: "R1_BLOCKERS_REPAIRED_PREPARING_R2"\n    prompt_review_evidence: project_control/reviews/S06_001_PROMPT_REPAIR_RESPONSE_v2.md\n'''
if old not in block:
    raise SystemExit('TASK_REGISTRY S06 review fields missing')
block = block.replace(old, new, 1)
s = head + block
p.write_text(s)

# -----------------------------------------------------------------------------
# 3. AUTONOMY_RUN_STATE: record R1 and enter R2 materialization preparation.
# -----------------------------------------------------------------------------
p = Path('project_control/AUTONOMY_RUN_STATE.yaml')
s = p.read_text()
s = s.replace('  current_prompt_review_target_sha: "1f831a767906e4322e0fc2370d593b5c51e323d5"\n', '  current_prompt_review_target_sha: PENDING_S06_001_R2_MATERIALIZATION\n', 1)
# Work only inside Slice-06 tail so older Slice-05 text is not touched.
marker = 'slice_06_planning:\n'
idx = s.index(marker)
pre, tail = s[:idx], s[idx:]
tail = tail.replace('  status: WAITING_EXTERNAL_REVIEW\n', '  status: PROMPT_REPAIR_R2_PREPARATION\n', 1)
tail = tail.replace('  prompt: project_control/prompts/SLICE-06_TASK-001_v1.md\n', '  prompt: project_control/prompts/SLICE-06_TASK-001_v2.md\n', 1)
tail = tail.replace(f'  prompt_review_target_sha: "{OLD_SHA}"\n', '  prompt_review_target_sha: PENDING_R2_MATERIALIZATION\n', 1)
old_review = f'''  independent_prompt_review:\n    work_id: S06-001-PROMPT-REVIEW-001\n    reviewer: eiu-reviewer\n    status: WAITING_EXTERNAL_REVIEW\n    reviewed_sha: "{OLD_SHA}"\n    result: PENDING\n    source_reopen_required: PENDING\n    evidence_branch: PENDING\n    evidence_commit: PENDING\n    evidence_path: PENDING\n'''
new_review = f'''  prior_prompt_review:\n    work_id: S06-001-PROMPT-REVIEW-001\n    reviewer: eiu-reviewer\n    reviewed_sha: "{OLD_SHA}"\n    result: BLOCKING_REPAIR\n    source_reopen_required: false\n    blocking_findings:\n      - S06-PROMPT-01_MISSING_IDEMPOTENCY_CONTRACT\n      - S06-PROMPT-02_DELETE_INACTIVATE_MISSING_EXPECTED_VERSION\n    owner_transport_evidence:\n      reported_branch: review/S06-001-PROMPT-5abbb51-v1\n      reported_commit: "a93659867e75f95109fa4826cb8b68114b031ddc"\n      reported_path: project_control/reviews/S06_001_PROMPT_REVIEW_5abbb51_v1.md\n      github_verification: UNRESOLVED_NOT_VISIBLE\n  prompt_repair_v2:\n    status: COMPLETE_PENDING_MATERIALIZATION\n    source_reopen_required: false\n    prompt: project_control/prompts/SLICE-06_TASK-001_v2.md\n    repair_evidence: project_control/reviews/S06_001_PROMPT_REPAIR_RESPONSE_v2.md\n    repairs:\n      - "Idempotency contract: scoped key, pre-replay authorization, normalized request fingerprint, mismatch fail-closed, atomic stored result, sequential/concurrent replay safety, actor/type/target isolation."\n      - "Delete/inactivate: required expected_version_no checked under target lock before lifecycle decision; stale request returns STALE_VERSION with no master/audit change."\n      - "Clarified no new anonymous management surface while preserving accepted anonymous lookup reads required by Candidate flows."\n  independent_prompt_review:\n    work_id: S06-001-PROMPT-REVIEW-002\n    reviewer: eiu-reviewer\n    status: PREPARING\n    reviewed_sha: PENDING_R2_MATERIALIZATION\n    result: PENDING\n    source_reopen_required: PENDING\n    evidence_branch: PENDING\n    evidence_commit: PENDING\n    evidence_path: PENDING\n'''
if old_review not in tail:
    raise SystemExit('AUTONOMY S06 review block missing')
tail = tail.replace(old_review, new_review, 1)
tail = tail.replace('  execution_hold: "TASK-S06-001 independent pre-implementation prompt/source review"\n', '  execution_hold: "TASK-S06-001 prompt v2 repair materialization and independent rereview preparation"\n', 1)
old_gate = f'''stop_gate:\n  status: WAITING_EXTERNAL_REVIEW\n  type: OMP_PROMPT_REVIEW\n  work_id: S06-001-PROMPT-REVIEW-001\n  target: "project_control/prompts/SLICE-06_TASK-001_v1.md @ {OLD_SHA}"\n  reviewed_sha: "{OLD_SHA}"\n  reviewer: eiu-reviewer\n  verdict: PENDING\n  source_reopen_required: PENDING\n  handoff_package_requirement: SATISFIED\n  handoff_package: project_control/reviews/S06_001_PROMPT_REVIEW_GATE_5abbb51_v1.md\n  materialization_integration_ci: "34488858134 PASS"\n  materialization_governance_ci: "34488858173 PASS"\n  resume_on: "PASS + SOURCE_REOPEN_REQUIRED=false for exact S06-001 prompt target"\n\nnext_action: "Transport project_control/reviews/S06_001_PROMPT_REVIEW_GATE_5abbb51_v1.md to independent OMP eiu-reviewer for exact prompt target {OLD_SHA}. On PASS + SOURCE_REOPEN_REQUIRED=false, verify returned evidence coordinates if available, create immutable pre-S06-001 checkpoint and isolated implementation branch from the accepted planning baseline, then execute the reviewed prompt. Do not merge/push main, deploy Vercel, or apply connected Supabase migrations without explicit Owner authorization."\n'''
new_gate = '''stop_gate:\n  status: PREPARING_EXTERNAL_REVIEW\n  type: OMP_PROMPT_REREVIEW_PREPARATION\n  work_id: S06-001-PROMPT-REVIEW-002\n  target: project_control/prompts/SLICE-06_TASK-001_v2.md\n  reviewed_sha: PENDING_R2_MATERIALIZATION\n  reviewer: eiu-reviewer\n  verdict: PENDING\n  source_reopen_required: PENDING\n  resume_on: "materialize prompt v2 on integration, validate control CI, persist exact-SHA rereview handoff, then PASS + SOURCE_REOPEN_REQUIRED=false"\n\nnext_action: "Materialize bounded TASK-S06-001 prompt v2 repair on integration, validate exact materialization CI, then persist and transport an exact-SHA S06-001-PROMPT-REVIEW-002 handoff to independent OMP eiu-reviewer. Do not create the S06-001 implementation branch/checkpoint before rereview PASS. Do not merge/push main, deploy Vercel, or apply connected Supabase migrations without explicit Owner authorization."\n'''
if old_gate not in tail:
    raise SystemExit('AUTONOMY old stop gate missing')
tail = tail.replace(old_gate, new_gate, 1)
p.write_text(pre + tail)

# -----------------------------------------------------------------------------
# 4. EVIDENCE_INDEX: resolve R1 gate and add repair preparation record.
# -----------------------------------------------------------------------------
p = Path('project_control/EVIDENCE_INDEX.yaml')
s = p.read_text()
marker = '  S06-001-PROMPT-REVIEW-GATE-001:\n'
idx = s.index(marker)
pre, tail = s[:idx], s[idx:]
tail = tail.replace('    status: WAITING_EXTERNAL_REVIEW\n', '    status: BLOCKING_REPAIR_FROM_OWNER_TRANSPORT\n', 1)
tail = tail.replace('    result: PENDING\n    source_reopen_required: PENDING\n', '    result: BLOCKING_REPAIR\n    source_reopen_required: false\n    blocking_findings: "S06-PROMPT-01 missing idempotency contract; S06-PROMPT-02 delete/inactivate missing expected-version validation"\n    reviewer_reported_evidence: "review/S06-001-PROMPT-5abbb51-v1 @ a93659867e75f95109fa4826cb8b68114b031ddc; project_control/reviews/S06_001_PROMPT_REVIEW_5abbb51_v1.md"\n    durable_evidence_verification: "UNRESOLVED — reported commit/branch/path not GitHub-visible at Coordinator verification time"\n', 1)
s = pre + tail
if '  S06-001-PROMPT-REPAIR-V2-001:\n' not in s:
    s += '''\n  S06-001-PROMPT-REPAIR-V2-001:\n    task: TASK-S06-001\n    operation: BOUNDED_PROMPT_REPAIR_AFTER_R1\n    status: PREPARING_R2_MATERIALIZATION\n    source_reopen_required: false\n    prior_reviewed_sha: "5abbb5181405e0f5a468176edd93db8226a3efd5"\n    prior_result: BLOCKING_REPAIR\n    repaired_prompt: project_control/prompts/SLICE-06_TASK-001_v2.md\n    repair_evidence: project_control/reviews/S06_001_PROMPT_REPAIR_RESPONSE_v2.md\n    repairs:\n      - S06-PROMPT-01_IDEMPOTENCY_CONTRACT\n      - S06-PROMPT-02_DELETE_INACTIVATE_EXPECTED_VERSION\n      - NONBLOCKING_ANON_MANAGEMENT_SURFACE_CLARIFICATION\n    next_review: S06-001-PROMPT-REVIEW-002\n'''
p.write_text(s)

# -----------------------------------------------------------------------------
# 5. CURRENT_STATE is derived; rewrite concise accurate snapshot.
# -----------------------------------------------------------------------------
Path('project_control/CURRENT_STATE.md').write_text(f'''# Current Implementation State — Derived Handoff Snapshot\n\n> **DERIVED / NON-AUTHORITATIVE REPORTING ONLY**\n>\n> Runtime authority: `project_control/AUTONOMY_RUN_STATE.yaml`.\n> DAG/task/slice authority: `project_control/TASK_REGISTRY.yaml` and `project_control/SLICE_REGISTRY.yaml`.\n> Exact code/history authority: Git.\n\n## SLICE-05 — DONE\n\n- TASK-S05-001 accepted: `ef0bd9e534dec0cc85ef6503fbe0369eda56d555`.\n- TASK-S05-002 accepted: `fe556dda76ebeda7107bcb9310cbaf338b30fc29`.\n- Closing composition review: PASS; `SOURCE_REOPEN_REQUIRED=false`.\n\n## SLICE-06 / TASK-S06-001 — PROMPT V2 REPAIR PREPARATION\n\nR1 exact target: `{OLD_SHA}`.\n\nIndependent `eiu-reviewer` R1 verdict: `BLOCKING_REPAIR`; `SOURCE_REOPEN_REQUIRED=false`.\n\nAccepted bounded blockers:\n\n1. `S06-PROMPT-01` — add executable idempotency/replay contract and sequential/concurrent/mismatch/isolation regressions.\n2. `S06-PROMPT-02` — require `expected_version_no` for delete/inactivate under lock, with stale hard-delete/inactivation regressions.\n\nReviewer-reported R1 evidence coordinates were not GitHub-visible when Coordinator checked; no durable-verification claim is made.\n\nActive repaired prompt:\n\n`project_control/prompts/SLICE-06_TASK-001_v2.md`\n\nRepair response:\n\n`project_control/reviews/S06_001_PROMPT_REPAIR_RESPONSE_v2.md`\n\nThe v2 repair also clarifies that S06-001 creates no new anonymous **management** surface while preserving accepted anonymous active lookup reads required by existing Candidate workflows.\n\nTASK-S06-001 remains `PLANNED`. No implementation branch/checkpoint exists yet. Next gate is exact-SHA `S06-001-PROMPT-REVIEW-002` by `eiu-reviewer`.\n\n## Do not cross\n\n- Do not implement S06-001 before R2 independent prompt review PASS.\n- Do not merge/push `main`.\n- Do not deploy Vercel.\n- Do not apply migrations to connected Supabase DEV/production without explicit Owner authorization.\n''')
