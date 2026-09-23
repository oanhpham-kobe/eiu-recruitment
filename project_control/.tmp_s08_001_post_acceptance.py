from pathlib import Path
import re

ACCEPTED_SHA = "0d8c5c2129ed4c78a58c8d37bd22e93c14a763eb"
PRODUCT_SHA = "3070e56ae06d3364f15cdc5e08d91fce090d820d"
CANDIDATE_SHA = "d3fcdfc9c9f057e70f9c74b0dbaaa4d2594f0daf"
BASELINE_SHA = "141146d52a05b0d698178ba7ef097690d5ef2a27"
TAG_OBJECT = "4617184e5f054b6ac3f4dea5be03e7a3b7fd66d7"
EVIDENCE_COMMIT = "ea0c3ec38aca2861ca2f59df9e2a1a8446aac492"


def sub_once(text: str, pattern: str, repl: str, label: str, flags: int = 0) -> str:
    out, count = re.subn(pattern, repl, text, count=1, flags=flags)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly 1 replacement, got {count}")
    return out

# TASK_REGISTRY.yaml — TASK-S08-001 is the final task block.
p = Path("project_control/TASK_REGISTRY.yaml")
text = p.read_text(encoding="utf-8")
task_block = '''  TASK-S08-001:
    title: "Application Inbox Search and Indexed Pagination Hardening"
    slice: SLICE-08
    status: DONE
    lane: LANE_A
    depends_on: [TASK-S03-004, TASK-S07-005]
    planning_baseline_sha: "6348fe9af137d18a2b148979583141bc8c8104b0"
    source_reconciliation: project_control/reviews/S08_001_SOURCE_RECONCILIATION_v2.md
    source_reconciliation_work_id: S08-001-SOURCE-RECONCILIATION-002
    source_reconciliation_status: PASS
    source_reopen_required: false
    prompt: project_control/prompts/SLICE-08_TASK-001_v2.md
    prompt_version: v2
    superseded_pre_review_artifacts:
      - project_control/reviews/S08_001_SOURCE_RECONCILIATION_v1.md
      - project_control/prompts/SLICE-08_TASK-001_v1.md
    governed_pre_task_checkpoint: checkpoint/pre-S08-001-001
    governed_pre_task_checkpoint_sha: "141146d52a05b0d698178ba7ef097690d5ef2a27"
    governed_pre_task_checkpoint_tag_object: "fc10664fdee1aa3676021b0049ec25e765ce1861"
    prompt_review_status: PASS
    prompt_review_work_id: S08-001-PROMPT-REVIEW-001
    prompt_review_reviewed_sha: "141146d52a05b0d698178ba7ef097690d5ef2a27"
    prompt_review_artifact: project_control/reviews/S08_001_PROMPT_REVIEW_141146d_v1.md
    prompt_review_implementation_authorized: false
    implementation_started: true
    implementation_authorized: true
    implementation_authorization_basis: "Explicit Owner implementation dispatch after independent prompt/source PASS."
    implementation_baseline_sha: "141146d52a05b0d698178ba7ef097690d5ef2a27"
    implementation_branch: chatgpt/TASK-S08-001-application-inbox-search-hardening
    producer: EXTERNAL_CHATGPT
    implementation_review_mode: OMP_EIU_REVIEWER
    implementation_review_status: PASS
    independent_implementation_review:
      work_id: S08-001-IMPLEMENTATION-REREVIEW-008
      reviewer: OMP_EIU_REVIEWER
      reviewed_sha: "d3fcdfc9c9f057e70f9c74b0dbaaa4d2594f0daf"
      prior_reviewed_sha: "c41392f8baf56931b6d2e22d8d082dfdf27076ef"
      verdict: PASS
      findings_count: 0
      source_reopen_required: false
      artifact: project_control/reviews/S08_001_IMPLEMENTATION_REREVIEW_R8_d3fcdfc_v1.md
    producer_verification:
      final_candidate_sha: "d3fcdfc9c9f057e70f9c74b0dbaaa4d2594f0daf"
      serialized_product_integration_sha: "3070e56ae06d3364f15cdc5e08d91fce090d820d"
      integration_ci: "35880657875 PASS @ 3070e56ae06d3364f15cdc5e08d91fce090d820d; resolver, full Web verification, Database integration, both S08 SQL gates, crossed regressions, standalone bulk replay, and DB lint PASS."
      governance_ci: "35880657901 PASS @ 3070e56ae06d3364f15cdc5e08d91fce090d820d"
      r7_failed_product_integration_sha: "1d68f9fea0116b0c279a053a06b4befa49fac1fc"
      r7_failed_integration_ci: "35878089069 FAIL — fixture-order collision at one_root_admin_uq before Inbox assertions; classified CI isolation only."
      r8_repair: "Ordering-only workflow repair; S08 transactional SQL suites execute immediately after clean db reset before PRE-S04 persistent fixtures."
      source_reopen_required: false
      implementation_reopen_required: false
    external_integration_audit:
      work_id: S08-001-EXTERNAL-INTEGRATION-AUDIT-001
      auditor: EXTERNAL_CHATGPT
      audited_candidate_sha: "d3fcdfc9c9f057e70f9c74b0dbaaa4d2594f0daf"
      audited_integration_sha: "3070e56ae06d3364f15cdc5e08d91fce090d820d"
      verdict: PASS
      source_reopen_required: false
      implementation_reopen_required: false
      blob_equivalence: "11/11 TASK-S08-001 delta blobs MATCH"
      artifact: project_control/reviews/S08_001_EXTERNAL_INTEGRATION_AUDIT_3070e56_v1.md
    final_acceptance_audit:
      status: PASS
      work_id: S08-001-FINAL-ACCEPTANCE-AUDIT-001
      reviewer: OMP_EIU_REVIEWER
      transport: OWNER_MESSAGE
      reviewed_sha: "0d8c5c2129ed4c78a58c8d37bd22e93c14a763eb"
      verdict: FINAL_ACCEPTANCE_PASS
      source_reopen_required: false
      implementation_reopen_required: false
      findings_count: 0
      artifact: project_control/reviews/S08_001_FINAL_ACCEPTANCE_AUDIT_0d8c5c2_v1.md
      evidence_branch: review/S08-001-FINAL-ACCEPTANCE-0d8c5c2-v1
      evidence_commit: "ea0c3ec38aca2861ca2f59df9e2a1a8446aac492"
    implementation_acceptance:
      accepted_sha: "0d8c5c2129ed4c78a58c8d37bd22e93c14a763eb"
      accepted_checkpoint: checkpoint/S08-001-accepted-001
      annotated_tag_object: "4617184e5f054b6ac3f4dea5be03e7a3b7fd66d7"
      implementation_review_work_id: S08-001-IMPLEMENTATION-REREVIEW-008
      implementation_review_verdict: PASS
      final_acceptance_work_id: S08-001-FINAL-ACCEPTANCE-AUDIT-001
      final_acceptance_verdict: PASS
      product_integration_sha: "3070e56ae06d3364f15cdc5e08d91fce090d820d"
      product_integration_ci: "35880657875 PASS"
      product_governance_ci: "35880657901 PASS"
      final_acceptance_integration_ci: "35882761018 PASS @ 0d8c5c2129ed4c78a58c8d37bd22e93c14a763eb"
      final_acceptance_governance_ci: "35882761149 PASS @ 0d8c5c2129ed4c78a58c8d37bd22e93c14a763eb"
      source_reopen_required: false
      implementation_reopen_required: false
      closure_artifact: project_control/reviews/S08_001_ACCEPTANCE_CLOSURE_0d8c5c2_v1.md
    acceptance:
      - "Existing server-side public.list_application_inbox architecture and Candidate-group pagination remain authoritative."
      - "Vietnamese Name search gains a tested accent-insensitive indexed normalization strategy without unsafe IMMUTABLE claims."
      - "Authoritative Email search predicate is explicitly aligned with its actual normalized/index support; the submissions.email_snapshot index is not misrepresented as supporting candidates.email."
      - "Phone search uses digit-normalized indexed behavior."
      - "User-facing default page size is 25 with exactly 25/50/100 choices; page-size changes reset page-scoped selection safely."
      - "Search/filter debounce is 300 ms and one-character generic Name queries cannot trigger broad trusted-database Name scans."
      - "PII Name/Email/Phone query text remains request state and is excluded from URL/history/logs/telemetry/audit payloads."
      - "RLS, submissions.view authorization, Root Admin behavior, deterministic immutable-ID tie-breakers and complete child history remain intact."
      - "Representative query-plan evidence is recorded without falsely claiming tiny-fixture production p95 proof."
      - "Focused/new and accepted Application Inbox regressions, full web gates, disposable local DB replay, DB lint, and governance validators PASS."
    out_of_scope: "Durable distributed rate limiting/TASK-S08-002, provider runtimes, production scheduler, archive/purge/retention, backup/restore, production deployment, connected Supabase mutation, Production UAT sign-off, global accessibility recertification, and unrelated search redesign."
    next_frontier_behavior: "Lifecycle CLOSED for TASK-S08-001. Slice-08 remains IN_PROGRESS. HARD STOP before TASK-S08-002 materialization until canonical source reconciliation and its governed prompt/source gate are explicitly materialized; no deployment, connected Supabase mutation, or main mutation."
'''
text = sub_once(text, r'(?ms)^  TASK-S08-001:\n.*\Z', task_block, "TASK_REGISTRY S08 block")
p.write_text(text, encoding="utf-8")

# AUTONOMY_RUN_STATE.yaml
p = Path("project_control/AUTONOMY_RUN_STATE.yaml")
text = p.read_text(encoding="utf-8")

m = re.search(r'(?ms)^integration:\n.*?(?=^authorization:)', text)
if not m:
    raise SystemExit("AUTONOMY integration block not found")
block = m.group(0)
replacements = {
    r'(?m)^  last_verified_application_checkpoint:.*$': '  last_verified_application_checkpoint: "0d8c5c2129ed4c78a58c8d37bd22e93c14a763eb"',
    r'(?m)^  last_verified_application_ci_run:.*$': '  last_verified_application_ci_run: "35882761018"',
    r'(?m)^  accepted_checkpoint:.*$': '  accepted_checkpoint: checkpoint/S08-001-accepted-001',
    r'(?m)^  accepted_checkpoint_sha:.*$': '  accepted_checkpoint_sha: "0d8c5c2129ed4c78a58c8d37bd22e93c14a763eb"',
    r'(?m)^  last_task_acceptance_attempt_sha:.*$': '  last_task_acceptance_attempt_sha: "0d8c5c2129ed4c78a58c8d37bd22e93c14a763eb"',
    r'(?m)^  last_task_acceptance_integration_ci_run:.*$': '  last_task_acceptance_integration_ci_run: "35882761018"',
    r'(?m)^  last_task_acceptance_integration_ci_result:.*$': '  last_task_acceptance_integration_ci_result: PASS',
    r'(?m)^  acceptance_domain_verification:.*$': '  acceptance_domain_verification: "35880657875 @ 3070e56ae06d3364f15cdc5e08d91fce090d820d full product Web/DB verification PASS including both S08 SQL gates and DB lint; 35882761018 and 35882761149 PASS @ governance-reconciled accepted SHA 0d8c5c2129ed4c78a58c8d37bd22e93c14a763eb; independent final acceptance audit S08-001-FINAL-ACCEPTANCE-AUDIT-001 FINAL_ACCEPTANCE_PASS."',
    r'(?m)^  prior_incomplete_acceptance_ci:.*$': '  prior_incomplete_acceptance_ci: "35878089069 @ 1d68f9fea0116b0c279a053a06b4befa49fac1fc failed only on CI fixture ordering before Inbox assertions; repaired by independently reviewed R8 ordering-only workflow delta. Earlier 35517082611 @ 46b5a1f0516f1701195143636a019ff5af92d08e exposed SQLSTATE 42P10 and was repaired before final candidate."',
    r'(?m)^  last_task_acceptance_governance_ci_run:.*$': '  last_task_acceptance_governance_ci_run: "35882761149"',
    r'(?m)^  last_task_acceptance_governance_ci_result:.*$': '  last_task_acceptance_governance_ci_result: PASS',
    r'(?m)^  current_prompt_review_target_sha:.*$': '  current_prompt_review_target_sha: "141146d52a05b0d698178ba7ef097690d5ef2a27"',
}
for pattern, repl in replacements.items():
    block = sub_once(block, pattern, repl, f"integration key {pattern}")
text = text[:m.start()] + block + text[m.end():]

last_accepted = '''last_accepted_task:
  id: TASK-S08-001
  commit: "0d8c5c2129ed4c78a58c8d37bd22e93c14a763eb"
  accepted_checkpoint: checkpoint/S08-001-accepted-001
  accepted_checkpoint_sha: "0d8c5c2129ed4c78a58c8d37bd22e93c14a763eb"
  annotated_tag_object: "4617184e5f054b6ac3f4dea5be03e7a3b7fd66d7"
  evidence:
    - "prompt_review: PASS (S08-001-PROMPT-REVIEW-001 @ 141146d52a05b0d698178ba7ef097690d5ef2a27)"
    - "implementation_review: PASS (S08-001-IMPLEMENTATION-REREVIEW-008 @ d3fcdfc9c9f057e70f9c74b0dbaaa4d2594f0daf)"
    - "external_integration_audit: PASS (S08-001-EXTERNAL-INTEGRATION-AUDIT-001 @ product integration 3070e56ae06d3364f15cdc5e08d91fce090d820d)"
    - "final_acceptance_audit: FINAL_ACCEPTANCE_PASS (S08-001-FINAL-ACCEPTANCE-AUDIT-001 @ 0d8c5c2129ed4c78a58c8d37bd22e93c14a763eb)"
    - "product_ci: VERIFIED (Integration CI 35880657875 and Governance CI 35880657901 PASS @ 3070e56ae06d3364f15cdc5e08d91fce090d820d)"
    - "final_acceptance_ci: VERIFIED (Integration CI 35882761018 and Governance CI 35882761149 PASS @ 0d8c5c2129ed4c78a58c8d37bd22e93c14a763eb)"
    - "checkpoint: checkpoint/S08-001-accepted-001; annotated tag object 4617184e5f054b6ac3f4dea5be03e7a3b7fd66d7; peeled target 0d8c5c2129ed4c78a58c8d37bd22e93c14a763eb"

previous_accepted_tasks:
  TASK-S07-005: {commit: "0caf83354a1353d7fc807d3b3014720f9720e2e3"}
'''
text = sub_once(text, r'(?ms)^last_accepted_task:\n.*?^previous_accepted_tasks:\n', last_accepted, "last accepted task")

slice8_tail = '''slice_08_planning:
  status: S08_001_ACCEPTED_HARD_STOP_BEFORE_S08_002_MATERIALIZATION
  lifecycle: ACTIVE
  selected_task: TASK-S08-001
  planning_source_prompt_head: "6348fe9af137d18a2b148979583141bc8c8104b0"
  source_reconciliation: project_control/reviews/S08_001_SOURCE_RECONCILIATION_v2.md
  source_reconciliation_work_id: S08-001-SOURCE-RECONCILIATION-002
  source_reconciliation_status: PASS
  source_reopen_required: false
  prompt: project_control/prompts/SLICE-08_TASK-001_v2.md
  prompt_version: v2
  governed_pre_task_checkpoint: checkpoint/pre-S08-001-001
  governed_pre_task_checkpoint_sha: "141146d52a05b0d698178ba7ef097690d5ef2a27"
  governed_pre_task_checkpoint_tag_object: "fc10664fdee1aa3676021b0049ec25e765ce1861"
  prompt_review_status: PASS
  prompt_review_work_id: S08-001-PROMPT-REVIEW-001
  implementation_started: true
  implementation_authorized: true
  implementation_baseline_sha: "141146d52a05b0d698178ba7ef097690d5ef2a27"
  implementation_branch: chatgpt/TASK-S08-001-application-inbox-search-hardening
  producer_role: EXTERNAL_CHATGPT
  independent_implementation_reviewer: OMP_EIU_REVIEWER
  implementation_review_status: PASS
  implementation_review_work_id: S08-001-IMPLEMENTATION-REREVIEW-008
  final_candidate_sha: "d3fcdfc9c9f057e70f9c74b0dbaaa4d2594f0daf"
  serialized_product_integration_sha: "3070e56ae06d3364f15cdc5e08d91fce090d820d"
  serialized_integration_ci: "35880657875 PASS"
  serialized_governance_ci: "35880657901 PASS"
  external_integration_audit: PASS
  external_integration_audit_work_id: S08-001-EXTERNAL-INTEGRATION-AUDIT-001
  final_acceptance_audit_status: PASS
  final_acceptance_audit_work_id: S08-001-FINAL-ACCEPTANCE-AUDIT-001
  final_acceptance_reviewed_sha: "0d8c5c2129ed4c78a58c8d37bd22e93c14a763eb"
  final_acceptance_verdict: FINAL_ACCEPTANCE_PASS
  final_acceptance_evidence_branch: review/S08-001-FINAL-ACCEPTANCE-0d8c5c2-v1
  final_acceptance_evidence_commit: "ea0c3ec38aca2861ca2f59df9e2a1a8446aac492"
  final_acceptance_evidence_artifact: project_control/reviews/S08_001_FINAL_ACCEPTANCE_AUDIT_0d8c5c2_v1.md
  accepted_checkpoint: checkpoint/S08-001-accepted-001
  accepted_checkpoint_sha: "0d8c5c2129ed4c78a58c8d37bd22e93c14a763eb"
  accepted_checkpoint_tag_object: "4617184e5f054b6ac3f4dea5be03e7a3b7fd66d7"
  final_acceptance_integration_ci: "35882761018 PASS"
  final_acceptance_governance_ci: "35882761149 PASS"
  source_reopen_required_after_acceptance: false
  implementation_reopen_required_after_acceptance: false
  materialized_next_task_count: 1
  deferred_candidate_tasks:
    - "TASK-S08-002 candidate: Durable Distributed Rate Limiting and Abuse Controls — identified but NOT materialized."

safe_frontier:
  eligible_tasks: []
  skipped_due_to_dependency:
    - "TASK-S08-001 is ACCEPTED. TASK-S08-002 remains an unmaterialized candidate and cannot enter the DAG without canonical source reconciliation and a governed prompt/source gate."
  materialization_frontier: []
  execution_hold: "HARD STOP after TASK-S08-001 acceptance. Do not materialize TASK-S08-002, mutate main, deploy Vercel, or mutate connected Supabase from this acceptance event."

stop_gate:
  status: ACTIVE
  type: S08_002_SOURCE_RECONCILIATION_BEFORE_MATERIALIZATION_GATE
  source_reopen_required: false
  resume_on: "A separately materialized canonical TASK-S08-002 source reconciliation and governed prompt/source lifecycle; TASK-S08-001 acceptance alone does not authorize it."

next_action: "SAFE CHECKPOINT: TASK-S08-001 lifecycle is CLOSED_ACCEPTED at checkpoint/S08-001-accepted-001. Stop before TASK-S08-002 materialization; the next work, if separately authorized by governance, is source reconciliation only."
'''
text = sub_once(text, r'(?ms)^slice_08_planning:\n.*\Z', slice8_tail, "slice8 runtime tail")
p.write_text(text, encoding="utf-8")

# EVIDENCE_INDEX.yaml
p = Path("project_control/EVIDENCE_INDEX.yaml")
text = p.read_text(encoding="utf-8")
text = sub_once(
    text,
    r'(?ms)^implementation_evidence:\n  status:.*?\n  note:.*?\n\n',
    'implementation_evidence:\n  status: S08_001_ACCEPTED_HARD_STOP_BEFORE_S08_002_MATERIALIZATION\n  note: "TASK-S08-001 is accepted at immutable checkpoint/S08-001-accepted-001 -> 0d8c5c2129ed4c78a58c8d37bd22e93c14a763eb after independent final acceptance PASS. TASK-S08-002 remains not materialized and is not authorized by this acceptance."\n\n',
    "evidence status",
)
evidence_block = '''  S08-001-SOURCE-GATE-001:
    task: TASK-S08-001
    operation: APPLICATION_INBOX_SEARCH_AND_INDEXED_PAGINATION_HARDENING
    status: ACCEPTED
    planning_source_prompt_head: "6348fe9af137d18a2b148979583141bc8c8104b0"
    source_reconciliation: project_control/reviews/S08_001_SOURCE_RECONCILIATION_v2.md
    source_reconciliation_work_id: S08-001-SOURCE-RECONCILIATION-002
    source_reconciliation_result: PASS
    source_reopen_required: false
    prompt: project_control/prompts/SLICE-08_TASK-001_v2.md
    prompt_version: v2
    governed_pre_task_checkpoint: checkpoint/pre-S08-001-001
    governed_pre_task_checkpoint_sha: "141146d52a05b0d698178ba7ef097690d5ef2a27"
    governed_pre_task_checkpoint_tag_object: "fc10664fdee1aa3676021b0049ec25e765ce1861"
    prompt_review_status: PASS
    prompt_review_work_id: S08-001-PROMPT-REVIEW-001
    prompt_review_reviewed_sha: "141146d52a05b0d698178ba7ef097690d5ef2a27"
    implementation_started: true
    implementation_authorized: true
    implementation_branch: chatgpt/TASK-S08-001-application-inbox-search-hardening
    implementation_baseline_sha: "141146d52a05b0d698178ba7ef097690d5ef2a27"
    producer: EXTERNAL_CHATGPT
    independent_implementation_review:
      work_id: S08-001-IMPLEMENTATION-REREVIEW-008
      reviewer: OMP_EIU_REVIEWER
      reviewed_sha: "d3fcdfc9c9f057e70f9c74b0dbaaa4d2594f0daf"
      verdict: PASS
      findings_count: 0
      source_reopen_required: false
    producer_verification:
      final_candidate_sha: "d3fcdfc9c9f057e70f9c74b0dbaaa4d2594f0daf"
      product_integration_sha: "3070e56ae06d3364f15cdc5e08d91fce090d820d"
      product_integration_ci: "35880657875 PASS"
      product_governance_ci: "35880657901 PASS"
      web_verification: PASS
      database_integration: PASS
      accepted_application_inbox_sql_regression: PASS
      search_hardening_sql_regression: PASS
      db_lint: PASS
      r7_fixture_order_failure: "35878089069 FAIL @ 1d68f9fea0116b0c279a053a06b4befa49fac1fc; one_root_admin_uq before Inbox assertions; classified CI isolation only."
      r8_isolation_repair: "Ordering-only; both transactional S08 suites execute immediately after clean reset before PRE-S04 persistent fixtures."
      source_reopen_required: false
      implementation_reopen_required: false
    external_integration_audit:
      work_id: S08-001-EXTERNAL-INTEGRATION-AUDIT-001
      auditor: EXTERNAL_CHATGPT
      audited_candidate_sha: "d3fcdfc9c9f057e70f9c74b0dbaaa4d2594f0daf"
      audited_integration_sha: "3070e56ae06d3364f15cdc5e08d91fce090d820d"
      verdict: PASS
      blob_equivalence: "11/11 MATCH"
      source_reopen_required: false
      implementation_reopen_required: false
      artifact: project_control/reviews/S08_001_EXTERNAL_INTEGRATION_AUDIT_3070e56_v1.md
    final_acceptance_audit:
      work_id: S08-001-FINAL-ACCEPTANCE-AUDIT-001
      reviewer: OMP_EIU_REVIEWER
      reviewed_sha: "0d8c5c2129ed4c78a58c8d37bd22e93c14a763eb"
      verdict: FINAL_ACCEPTANCE_PASS
      source_reopen_required: false
      implementation_reopen_required: false
      findings_count: 0
      evidence_branch: review/S08-001-FINAL-ACCEPTANCE-0d8c5c2-v1
      evidence_commit: "ea0c3ec38aca2861ca2f59df9e2a1a8446aac492"
      artifact: project_control/reviews/S08_001_FINAL_ACCEPTANCE_AUDIT_0d8c5c2_v1.md
    implementation_acceptance:
      accepted_checkpoint: checkpoint/S08-001-accepted-001
      accepted_checkpoint_sha: "0d8c5c2129ed4c78a58c8d37bd22e93c14a763eb"
      annotated_tag_object: "4617184e5f054b6ac3f4dea5be03e7a3b7fd66d7"
      product_integration_ci: "35880657875 PASS @ 3070e56ae06d3364f15cdc5e08d91fce090d820d"
      product_governance_ci: "35880657901 PASS @ 3070e56ae06d3364f15cdc5e08d91fce090d820d"
      final_acceptance_integration_ci: "35882761018 PASS @ 0d8c5c2129ed4c78a58c8d37bd22e93c14a763eb"
      final_acceptance_governance_ci: "35882761149 PASS @ 0d8c5c2129ed4c78a58c8d37bd22e93c14a763eb"
      closure_artifact: project_control/reviews/S08_001_ACCEPTANCE_CLOSURE_0d8c5c2_v1.md
      source_reopen_required: false
      implementation_reopen_required: false
    accepted_predecessor_slice_checkpoint: checkpoint/SLICE-07-accepted-001
    accepted_predecessor_slice_sha: "b4e06a639f9e00126c1f76549067e1f6469ebc8b"
    bounded_scope: "Existing Application Inbox search/read hardening only: accent-insensitive Name normalization/indexing, authoritative Email/index alignment, digit-normalized Phone search, canonical page-size/debounce/minimum-query behavior, PII-safe request transport, and representative query-plan evidence."
    deferred_candidate: "TASK-S08-002 Durable Distributed Rate Limiting and Abuse Controls — identified but NOT materialized."

'''
text = sub_once(text, r'(?ms)^  S08-001-SOURCE-GATE-001:\n.*?(?=^  PLAN-RECONCILIATION-S04-005-001:)', evidence_block, "evidence S08 block")
p.write_text(text, encoding="utf-8")

# CURRENT_STATE.md — replace the Slice-08 tail.
p = Path("project_control/CURRENT_STATE.md")
text = p.read_text(encoding="utf-8")
current_tail = '''## TASK-S08-001 accepted state

- `TASK-S08-001 — Application Inbox Search and Indexed Pagination Hardening` is accepted at `checkpoint/S08-001-accepted-001` → `0d8c5c2129ed4c78a58c8d37bd22e93c14a763eb`.
- Immutable implementation baseline: `checkpoint/pre-S08-001-001` → `141146d52a05b0d698178ba7ef097690d5ef2a27`; annotated tag object `fc10664fdee1aa3676021b0049ec25e765ce1861`.
- Independent prompt/source review `S08-001-PROMPT-REVIEW-001`: PASS on `141146d52a05b0d698178ba7ef097690d5ef2a27`, source reopen false.
- Final independently reviewed candidate: `d3fcdfc9c9f057e70f9c74b0dbaaa4d2594f0daf`; independent implementation re-review `S08-001-IMPLEMENTATION-REREVIEW-008`: PASS, findings NONE, source reopen false.
- Product integration `3070e56ae06d3364f15cdc5e08d91fce090d820d`: Integration CI `35880657875` PASS and Governance CI `35880657901` PASS. Full Web verification, clean DB replay, both S08 SQL gates, predecessor/crossed/concurrency regressions, standalone bulk replay, and DB lint PASS.
- External integration audit `S08-001-EXTERNAL-INTEGRATION-AUDIT-001`: PASS with 11/11 governed task-delta blobs byte-equivalent between candidate and product integration.
- Governance-reconciled acceptance SHA `0d8c5c2129ed4c78a58c8d37bd22e93c14a763eb`: Integration CI `35882761018` PASS and Governance CI `35882761149` PASS.
- Independent final acceptance audit `S08-001-FINAL-ACCEPTANCE-AUDIT-001`: `FINAL_ACCEPTANCE_PASS`, source reopen false, implementation reopen false, findings NONE. Owner-transported evidence persisted on `review/S08-001-FINAL-ACCEPTANCE-0d8c5c2-v1` at `ea0c3ec38aca2861ca2f59df9e2a1a8446aac492`.
- Accepted checkpoint verified: annotated tag object `4617184e5f054b6ac3f4dea5be03e7a3b7fd66d7` peels exactly to `0d8c5c2129ed4c78a58c8d37bd22e93c14a763eb`, message `Accept TASK-S08-001 @ 0d8c5c2129ed4c78a58c8d37bd22e93c14a763eb`.
- No `main` mutation, Vercel deployment, connected/hosted Supabase mutation, or production-secret use was authorized or performed by this acceptance lifecycle.

## Slice-08 frontier

- Slice-08 remains `IN_PROGRESS`; accepting TASK-S08-001 does not close the slice or authorize a next task automatically.
- `TASK-S08-002` remains an identified future candidate only and is **not materialized**.
- Safe frontier is empty. The next possible activity is source reconciliation for a future S08 task only after a separately governed materialization decision; no implementation authority is implied.

## Scope boundary

TASK-S08-001 lifecycle is `CLOSED_ACCEPTED`. HARD STOP before TASK-S08-002 materialization. Do not mutate `main`, deploy Vercel, mutate connected Supabase, use production secrets, or move the immutable TASK-S08-001 checkpoint from this reporting transition.
'''
text = sub_once(text, r'(?ms)^## Slice-08 planning state\n.*\Z', current_tail, "CURRENT_STATE Slice-08 tail")
p.write_text(text, encoding="utf-8")

# Acceptance closure evidence authored by coordinator after immutable checkpoint verification.
closure = Path("project_control/reviews/S08_001_ACCEPTANCE_CLOSURE_0d8c5c2_v1.md")
closure.write_text('''# TASK-S08-001 — Acceptance Closure Evidence

Work ID: `S08-001-ACCEPTANCE-CLOSURE-001`

Coordinator: `EXTERNAL_CHATGPT`

Accepted task: `TASK-S08-001 — Application Inbox Search and Indexed Pagination Hardening`

## Immutable acceptance identity

- Accepted SHA: `0d8c5c2129ed4c78a58c8d37bd22e93c14a763eb`
- Accepted checkpoint: `checkpoint/S08-001-accepted-001`
- Annotated tag object: `4617184e5f054b6ac3f4dea5be03e7a3b7fd66d7`
- Peeled target: `0d8c5c2129ed4c78a58c8d37bd22e93c14a763eb`
- Tag message: `Accept TASK-S08-001 @ 0d8c5c2129ed4c78a58c8d37bd22e93c14a763eb`

The accepted checkpoint was created only after the owner-transported independent final acceptance verdict had been durably persisted.

## Review and CI chain

- Governed implementation baseline: `141146d52a05b0d698178ba7ef097690d5ef2a27`
- Final independently reviewed candidate: `d3fcdfc9c9f057e70f9c74b0dbaaa4d2594f0daf`
- Independent implementation review: `S08-001-IMPLEMENTATION-REREVIEW-008` — PASS
- Product integration: `3070e56ae06d3364f15cdc5e08d91fce090d820d`
- Product Integration CI: `35880657875` — PASS
- Product Governance CI: `35880657901` — PASS
- External integration audit: `S08-001-EXTERNAL-INTEGRATION-AUDIT-001` — PASS, 11/11 task-delta blobs MATCH
- Final acceptance audit: `S08-001-FINAL-ACCEPTANCE-AUDIT-001` — `FINAL_ACCEPTANCE_PASS`
- Final acceptance Integration CI: `35882761018` — PASS @ accepted SHA
- Final acceptance Governance CI: `35882761149` — PASS @ accepted SHA
- Final audit evidence branch: `review/S08-001-FINAL-ACCEPTANCE-0d8c5c2-v1`
- Final audit evidence commit: `ea0c3ec38aca2861ca2f59df9e2a1a8446aac492`
- Final audit evidence path: `project_control/reviews/S08_001_FINAL_ACCEPTANCE_AUDIT_0d8c5c2_v1.md`

## Boundary

- `SOURCE_REOPEN_REQUIRED: false`
- `IMPLEMENTATION_REOPEN_REQUIRED: false`
- TASK-S08-001 lifecycle: `CLOSED_ACCEPTED`
- Slice-08 remains `IN_PROGRESS`.
- TASK-S08-002 remains **not materialized** and is not authorized by TASK-S08-001 acceptance.
- No `main` mutation, Vercel deployment, connected/hosted Supabase mutation, or production-secret use is authorized by this closure.

This artifact is reporting evidence after the immutable accepted checkpoint. It does not alter the accepted SHA and does not authorize movement of the checkpoint.
''', encoding="utf-8")
