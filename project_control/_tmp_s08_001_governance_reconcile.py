from pathlib import Path
import re

PRODUCT_SHA = "3070e56ae06d3364f15cdc5e08d91fce090d820d"
CANDIDATE_SHA = "d3fcdfc9c9f057e70f9c74b0dbaaa4d2594f0daf"
BASELINE_SHA = "141146d52a05b0d698178ba7ef097690d5ef2a27"


def replace_once(path: str, pattern: str, replacement: str) -> None:
    p = Path(path)
    source = p.read_text(encoding="utf-8")
    updated, count = re.subn(pattern, replacement, source, count=1, flags=re.MULTILINE | re.DOTALL)
    if count != 1:
        raise SystemExit(f"expected exactly one replacement in {path}, got {count}")
    p.write_text(updated, encoding="utf-8", newline="\n")


audit = f"""# TASK-S08-001 — External Integration Audit

Work ID: `S08-001-EXTERNAL-INTEGRATION-AUDIT-001`

Auditor role: `EXTERNAL_CHATGPT`

Audited candidate SHA: `{CANDIDATE_SHA}`

Audited product integration SHA: `{PRODUCT_SHA}`

Governed implementation baseline: `{BASELINE_SHA}`

Verdict: `PASS`

`SOURCE_REOPEN_REQUIRED: false`

`IMPLEMENTATION_REOPEN_REQUIRED: false`

## Integration equivalence

The governed baseline-to-candidate delta contains exactly the following 11 TASK-S08-001 files, and the product integration preserves all 11 blobs byte-for-byte. The baseline-to-integration delta contains the same task delta plus the previously persisted independent prompt-review evidence artifact.

1. `.github/workflows/integration-ci.yml` — `074deecbcc94970e5e783ef6c4690158f3b04ba0`
2. `project_control/reviews/S08_001_IMPLEMENTATION_BASELINE_CORRECTION_v1.md` — `52931d6468c29f16bbf44fdcfe3ea4cc0db0663d`
3. `supabase/migrations/20260920010000_application_inbox_search_hardening.sql` — `613b18d83af46483ee944ef3f21810eb1a97e91e`
4. `supabase/tests/application_inbox_read.sql` — `de37cec7e4d0c8cf9f18b2590812c12de5e82fba`
5. `supabase/tests/application_inbox_search_hardening_test.sql` — `2e6d92459118bcdc67fc9809d20def612a3827ff`
6. `web/src/__tests__/application-inbox-search-pagination.test.ts` — `8c318d82428e1f43a933419cb683b239ade748cd`
7. `web/src/__tests__/application-inbox.test.ts` — `fa752089e55dbb610d09ee37cf6000b318ac42a6`
8. `web/src/app/application-inbox-actions.ts` — `bd6090b7b66bb85a142f3982a55a26463ba53b22`
9. `web/src/components/inbox/ApplicationInboxTable.tsx` — `adaacb249ba1378dd349dc5cbcbc4b8b393875e8`
10. `web/src/lib/application-inbox/model.ts` — `5106433bbf8f31fab1c01223fd57d403de2472a2`
11. `web/src/lib/application-inbox/server.ts` — `490e9aac927b425eff44392d18491d3899965746`

No task product/test/control artifact drift was found during serialization.

## Independent review chain

- Pre-implementation prompt/source review `S08-001-PROMPT-REVIEW-001`: PASS on `{BASELINE_SHA}`; source reopen false.
- Final implementation re-review `S08-001-IMPLEMENTATION-REREVIEW-008`: PASS on `{CANDIDATE_SHA}`; source reopen false; findings none.
- R8 review evidence is persisted at `project_control/reviews/S08_001_IMPLEMENTATION_REREVIEW_R8_d3fcdfc_v1.md` on the independent review branch.

## R7 failure and R8 repair classification

The earlier product integration `1d68f9fea0116b0c279a053a06b4befa49fac1fc` exposed a CI fixture-order defect: PRE-S04 left a singleton Root Admin fixture before `application_inbox_read.sql`, causing `one_root_admin_uq` before Inbox assertions executed. The product migration had replayed successfully and Web verification passed.

R8 changed only workflow ordering so the two transactional S08 SQL suites execute immediately after clean `supabase db reset` and roll back before PRE-S04 persistent fixtures. No SQL test body, migration, application code, permission, RLS, indexing, pagination, search, or PII behavior changed.

## Exact product-integration verification

Product integration: `{PRODUCT_SHA}`

- Integration CI `35880657875`: PASS on exact `{PRODUCT_SHA}`.
- Governance CI `35880657901`: PASS on exact `{PRODUCT_SHA}`.
- Web verification: PASS, including dependency audit, design contract, lint, typecheck, production build, Playwright install, and full Web test set.
- Database integration: PASS.
- Clean migration replay: PASS.
- `application_inbox_read.sql`: PASS.
- `application_inbox_search_hardening_test.sql`: PASS.
- PRE-S04 regression: PASS after both S08 transactional suites.
- All configured S05/S06/S07 crossed and concurrency regressions: PASS.
- Standalone bulk replay: PASS.
- `supabase db lint --local --level error`: PASS.

## Security and scope

- No production secrets were used.
- No connected or hosted Supabase mutation occurred.
- No Vercel deployment occurred.
- `main` was not mutated.
- TASK-S08-002 remains not materialized.
- PII transport, RLS, contextual authorization, immutable tie-breakers, Candidate-group pagination, and historical child completeness remain within the independently reviewed contract.

## Audit conclusion

`PASS` applies to the equivalence between independently reviewed candidate `{CANDIDATE_SHA}` and exact product integration `{PRODUCT_SHA}`.

The task is eligible to move to a governance-reconciled **final acceptance audit gate**. This audit does not self-accept TASK-S08-001 and does not authorize creation of `checkpoint/S08-001-accepted-001` before independent OMP final acceptance PASS.
"""
Path("project_control/reviews/S08_001_EXTERNAL_INTEGRATION_AUDIT_3070e56_v1.md").write_text(audit, encoding="utf-8", newline="\n")


task_block = f'''  TASK-S08-001:
    title: "Application Inbox Search and Indexed Pagination Hardening"
    slice: SLICE-08
    status: REVIEW
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
    governed_pre_task_checkpoint_sha: "{BASELINE_SHA}"
    governed_pre_task_checkpoint_tag_object: "fc10664fdee1aa3676021b0049ec25e765ce1861"
    prompt_review_status: PASS
    prompt_review_work_id: S08-001-PROMPT-REVIEW-001
    prompt_review_reviewed_sha: "{BASELINE_SHA}"
    prompt_review_artifact: project_control/reviews/S08_001_PROMPT_REVIEW_141146d_v1.md
    prompt_review_implementation_authorized: false
    implementation_started: true
    implementation_authorized: true
    implementation_authorization_basis: "Explicit Owner implementation dispatch after independent prompt/source PASS."
    implementation_baseline_sha: "{BASELINE_SHA}"
    implementation_branch: chatgpt/TASK-S08-001-application-inbox-search-hardening
    producer: EXTERNAL_CHATGPT
    implementation_review_mode: OMP_EIU_REVIEWER
    implementation_review_status: PASS
    independent_implementation_review:
      work_id: S08-001-IMPLEMENTATION-REREVIEW-008
      reviewer: OMP_EIU_REVIEWER
      reviewed_sha: "{CANDIDATE_SHA}"
      prior_reviewed_sha: "c41392f8baf56931b6d2e22d8d082dfdf27076ef"
      verdict: PASS
      findings_count: 0
      source_reopen_required: false
      artifact: project_control/reviews/S08_001_IMPLEMENTATION_REREVIEW_R8_d3fcdfc_v1.md
    producer_verification:
      final_candidate_sha: "{CANDIDATE_SHA}"
      serialized_product_integration_sha: "{PRODUCT_SHA}"
      integration_ci: "35880657875 PASS @ {PRODUCT_SHA}; resolver, full Web verification, Database integration, both S08 SQL gates, crossed regressions, standalone bulk replay, and DB lint PASS."
      governance_ci: "35880657901 PASS @ {PRODUCT_SHA}"
      r7_failed_product_integration_sha: "1d68f9fea0116b0c279a053a06b4befa49fac1fc"
      r7_failed_integration_ci: "35878089069 FAIL — fixture-order collision at one_root_admin_uq before Inbox assertions; classified CI isolation only."
      r8_repair: "Ordering-only workflow repair; S08 transactional SQL suites now execute immediately after clean db reset before PRE-S04 persistent fixtures."
      source_reopen_required: false
      implementation_reopen_required: false
    external_integration_audit:
      work_id: S08-001-EXTERNAL-INTEGRATION-AUDIT-001
      auditor: EXTERNAL_CHATGPT
      audited_candidate_sha: "{CANDIDATE_SHA}"
      audited_integration_sha: "{PRODUCT_SHA}"
      verdict: PASS
      source_reopen_required: false
      implementation_reopen_required: false
      blob_equivalence: "11/11 TASK-S08-001 delta blobs MATCH"
      artifact: project_control/reviews/S08_001_EXTERNAL_INTEGRATION_AUDIT_3070e56_v1.md
    final_acceptance_audit:
      status: PENDING
      required_reviewer: OMP_EIU_REVIEWER
      checkpoint_before_pass: FORBIDDEN
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
    next_frontier_behavior: "HARD STOP at the governance-reconciled TASK-S08-001 integration SHA pending independent OMP final acceptance audit; no accepted checkpoint, TASK-S08-002 materialization, deployment, connected Supabase mutation, or main mutation before PASS."
'''
replace_once(
    "project_control/TASK_REGISTRY.yaml",
    r"^  TASK-S08-001:\n.*\Z",
    task_block,
)


autonomy_suffix = f'''slice_08_planning:
  status: S08_001_INTEGRATED_AWAITING_FINAL_ACCEPTANCE_AUDIT
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
  governed_pre_task_checkpoint_sha: "{BASELINE_SHA}"
  governed_pre_task_checkpoint_tag_object: "fc10664fdee1aa3676021b0049ec25e765ce1861"
  prompt_review_status: PASS
  prompt_review_work_id: S08-001-PROMPT-REVIEW-001
  prompt_review_reviewed_sha: "{BASELINE_SHA}"
  prompt_review_artifact: project_control/reviews/S08_001_PROMPT_REVIEW_141146d_v1.md
  prompt_review_implementation_authorized: false
  implementation_started: true
  implementation_authorized: true
  implementation_authorization_basis: "Explicit Owner implementation dispatch after prompt/source PASS."
  implementation_baseline_sha: "{BASELINE_SHA}"
  implementation_branch: chatgpt/TASK-S08-001-application-inbox-search-hardening
  producer_role: EXTERNAL_CHATGPT
  independent_implementation_reviewer: OMP_EIU_REVIEWER
  implementation_review_status: PASS
  implementation_review_work_id: S08-001-IMPLEMENTATION-REREVIEW-008
  final_candidate_sha: "{CANDIDATE_SHA}"
  serialized_product_integration_sha: "{PRODUCT_SHA}"
  serialized_integration_ci: "35880657875 PASS"
  serialized_governance_ci: "35880657901 PASS"
  external_integration_audit: PASS
  external_integration_audit_work_id: S08-001-EXTERNAL-INTEGRATION-AUDIT-001
  external_integration_audit_artifact: project_control/reviews/S08_001_EXTERNAL_INTEGRATION_AUDIT_3070e56_v1.md
  final_acceptance_audit_status: PENDING
  final_acceptance_reviewer: OMP_EIU_REVIEWER
  accepted_checkpoint_before_final_pass: FORBIDDEN
  materialized_next_task_count: 1
  deferred_candidate_tasks:
    - "TASK-S08-002 candidate: Durable Distributed Rate Limiting and Abuse Controls — identified by source reconciliation but NOT materialized."

safe_frontier:
  eligible_tasks: []
  skipped_due_to_dependency:
    - "TASK-S08-001 implementation, independent implementation review, exact product serialization, full Web/DB Integration CI, Governance CI, and external integration audit are PASS; awaiting independent OMP final acceptance audit."
  materialization_frontier: []
  execution_hold: "HARD STOP at governance-reconciled S08-001 integration pending independent OMP final acceptance audit; checkpoint/S08-001-accepted-001 and TASK-S08-002 materialization are forbidden before PASS."

stop_gate:
  status: ACTIVE
  type: S08_001_FINAL_ACCEPTANCE_AUDIT_GATE
  source_reopen_required: false
  resume_on: "Owner-transported independent OMP final acceptance PASS or BLOCKING_REPAIR verdict for the exact governance-reconciled integration SHA."

next_action: "Return the exact governance-reconciled S08-001 integration SHA and evidence packet to OMP_EIU_REVIEWER for independent final acceptance audit; do not create checkpoint/S08-001-accepted-001 or materialize TASK-S08-002 before PASS."
'''
replace_once(
    "project_control/AUTONOMY_RUN_STATE.yaml",
    r"^slice_08_planning:\n.*\Z",
    autonomy_suffix,
)


evidence_prefix = f'''implementation_evidence:
  status: S08_001_INTEGRATED_AWAITING_FINAL_ACCEPTANCE_AUDIT
  note: "TASK-S08-001 has independent implementation PASS, exact product serialization, full Web/DB Integration CI PASS, Governance CI PASS, and external integration audit PASS. Accepted checkpoint creation and TASK-S08-002 materialization remain forbidden pending independent OMP final acceptance audit."

  S08-001-SOURCE-GATE-001:
    task: TASK-S08-001
    operation: APPLICATION_INBOX_SEARCH_AND_INDEXED_PAGINATION_HARDENING
    status: INTEGRATED_AWAITING_FINAL_ACCEPTANCE_AUDIT
    planning_source_prompt_head: "6348fe9af137d18a2b148979583141bc8c8104b0"
    source_reconciliation: project_control/reviews/S08_001_SOURCE_RECONCILIATION_v2.md
    source_reconciliation_work_id: S08-001-SOURCE-RECONCILIATION-002
    source_reconciliation_result: PASS
    source_reopen_required: false
    prompt: project_control/prompts/SLICE-08_TASK-001_v2.md
    prompt_version: v2
    governed_pre_task_checkpoint: checkpoint/pre-S08-001-001
    governed_pre_task_checkpoint_sha: "{BASELINE_SHA}"
    governed_pre_task_checkpoint_tag_object: "fc10664fdee1aa3676021b0049ec25e765ce1861"
    prompt_review_status: PASS
    prompt_review_work_id: S08-001-PROMPT-REVIEW-001
    prompt_review_reviewed_sha: "{BASELINE_SHA}"
    prompt_review_artifact: project_control/reviews/S08_001_PROMPT_REVIEW_141146d_v1.md
    prompt_review_implementation_authorized: false
    implementation_started: true
    implementation_authorized: true
    implementation_branch: chatgpt/TASK-S08-001-application-inbox-search-hardening
    implementation_baseline_sha: "{BASELINE_SHA}"
    producer: EXTERNAL_CHATGPT
    independent_implementation_review:
      work_id: S08-001-IMPLEMENTATION-REREVIEW-008
      reviewer: OMP_EIU_REVIEWER
      reviewed_sha: "{CANDIDATE_SHA}"
      verdict: PASS
      findings_count: 0
      source_reopen_required: false
    producer_verification:
      final_candidate_sha: "{CANDIDATE_SHA}"
      product_integration_sha: "{PRODUCT_SHA}"
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
      audited_candidate_sha: "{CANDIDATE_SHA}"
      audited_integration_sha: "{PRODUCT_SHA}"
      verdict: PASS
      blob_equivalence: "11/11 MATCH"
      source_reopen_required: false
      implementation_reopen_required: false
      artifact: project_control/reviews/S08_001_EXTERNAL_INTEGRATION_AUDIT_3070e56_v1.md
    final_acceptance_audit:
      status: PENDING
      required_reviewer: OMP_EIU_REVIEWER
      checkpoint_before_pass: FORBIDDEN
    accepted_predecessor_slice_checkpoint: checkpoint/SLICE-07-accepted-001
    accepted_predecessor_slice_sha: "b4e06a639f9e00126c1f76549067e1f6469ebc8b"
    superseded_before_review:
      - project_control/reviews/S08_001_SOURCE_RECONCILIATION_v1.md
      - project_control/prompts/SLICE-08_TASK-001_v1.md
    bounded_scope: "Existing Application Inbox search/read hardening only: accent-insensitive Name normalization/indexing, authoritative Email/index alignment, digit-normalized Phone search, canonical page-size/debounce/minimum-query behavior, PII-safe request transport, and representative query-plan evidence."
    deferred_candidate: "TASK-S08-002 Durable Distributed Rate Limiting and Abuse Controls — identified but NOT materialized."

'''
replace_once(
    "project_control/EVIDENCE_INDEX.yaml",
    r"^implementation_evidence:\n.*?(?=^  PLAN-RECONCILIATION-S04-005-001:)",
    evidence_prefix,
)


current_state_suffix = f'''## Slice-08 TASK-S08-001 final-acceptance gate

- Slice-07 remains `CLOSED_ACCEPTED` at `checkpoint/SLICE-07-accepted-001`.
- Canonical source reconciliation `S08-001-SOURCE-RECONCILIATION-002` and prompt `project_control/prompts/SLICE-08_TASK-001_v2.md` remain authoritative; source reopen is false.
- Immutable implementation baseline: `checkpoint/pre-S08-001-001` → `{BASELINE_SHA}`; annotated tag object `fc10664fdee1aa3676021b0049ec25e765ce1861` peels to that exact SHA.
- Independent prompt/source review `S08-001-PROMPT-REVIEW-001`: PASS on `{BASELINE_SHA}`. Its `IMPLEMENTATION_AUTHORIZED: NO` applies to the prompt-review event itself; explicit Owner implementation dispatch occurred afterward and is the authority under which implementation proceeded.
- Final independently reviewed task candidate: `{CANDIDATE_SHA}` on `chatgpt/TASK-S08-001-application-inbox-search-hardening`.
- Independent implementation re-review `S08-001-IMPLEMENTATION-REREVIEW-008`: PASS, findings NONE, source reopen false.
- Product integration: `{PRODUCT_SHA}`. External integration audit `S08-001-EXTERNAL-INTEGRATION-AUDIT-001`: PASS; 11/11 governed task-delta blobs match the reviewed candidate; source reopen false; implementation reopen false.
- Exact product Integration CI `35880657875`: PASS. Web verification, migration replay, both canonical S08 SQL gates, PRE-S04 and crossed predecessor/concurrency regressions, standalone bulk replay, and DB lint all PASS.
- Exact product Governance CI `35880657901`: PASS.
- Historical R7 product-integration failure `35878089069` at `1d68f9fea0116b0c279a053a06b4befa49fac1fc` was a CI fixture-order/isolation defect (`one_root_admin_uq`) before Inbox assertions; R8 repaired workflow ordering only and the exact repaired sequence is now proven by CI.
- No TASK-S08-001 accepted checkpoint exists yet. `checkpoint/S08-001-accepted-001` is forbidden until independent OMP final acceptance audit PASSes on the exact governance-reconciled integration SHA.
- TASK-S08-002 remains **not materialized**.

## Scope boundary

SLICE-08 remains `IN_PROGRESS`. TASK-S08-001 is at the independent final-acceptance-audit gate after reviewed candidate `{CANDIDATE_SHA}`, product integration `{PRODUCT_SHA}`, Integration CI `35880657875` PASS, Governance CI `35880657901` PASS, and external integration audit PASS. No accepted checkpoint, TASK-S08-002 materialization, production deployment, connected Supabase mutation, or `main` mutation is allowed before final acceptance audit PASS.
'''
replace_once(
    "project_control/CURRENT_STATE.md",
    r"^## Slice-08 planning state\n.*\Z",
    current_state_suffix,
)

print("S08-001 governance reconciliation staged successfully")
