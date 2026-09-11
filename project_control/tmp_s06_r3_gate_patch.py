from pathlib import Path

p = Path('project_control/AUTONOMY_RUN_STATE.yaml')
text = p.read_text(encoding='utf-8')

slice_pos = text.index('slice_06_planning:\n')
impl_pos = text.index('  implementation_candidate:\n', slice_pos)

prefix = text[:impl_pos]
new_tail = '''  implementation_candidate:
    branch: oanhpham-kobe/TASK-S06-001-master-data-lifecycle
    baseline_sha: "0ec409915bdd00b61b1b7affdb77ec778c7c1dc7"
    prior_candidate_sha: "dced5aac32e6b09181cd53d0011b9c951edf2814"
    candidate_sha: "9002c9be26c57a182494b9b0de46ae612f32d81e"
    changed_files_count: 3
    source_reopen_required: false
    prior_independent_reviews:
      r1:
        work_id: S06-001-IMPLEMENTATION-REVIEW-001
        reviewer: eiu-reviewer
        status: VERIFIED_FROM_OWNER_TRANSPORT
        reviewed_sha: "0c4b94b29e08e1ad877583bdb90d522e5577dccc"
        result: BLOCKING_REPAIR
        source_reopen_required: false
        blocking_findings:
          - "Cancellation/rejection ever-use history was lost after accepted lifecycle normalization cleared current reason FKs."
          - "Inactive historical Document Types incorrectly blocked trusted Candidate REPLACE/DELETE."
          - "Interview Format authoritative metadata was read before the first-use lock."
          - "master_data.manage lacked inactive management reads."
        evidence_persistence: "Owner/reviewer transport; no unverified GitHub persistence claim."
      r2:
        work_id: S06-001-IMPLEMENTATION-REVIEW-001-R2
        reviewer: eiu-reviewer
        status: VERIFIED_FROM_OWNER_TRANSPORT
        reviewed_sha: "dced5aac32e6b09181cd53d0011b9c951edf2814"
        result: BLOCKING_REPAIR
        source_reopen_required: false
        blocking_findings:
          - "Durable ever-reference history remained incomplete when accepted workflows replace/delete semantic FK evidence; final reviewer clarification required a shared solution across replaceable semantic Master Data references."
        closed_areas:
          - "Cancellation/rejection durable history."
          - "Inactive historical Candidate Document Type REPLACE/DELETE while ADD remains Active-only."
          - "Interview Format first-use metadata race."
          - "master_data.manage inactive-row management reads."
        evidence_persistence: "UNAVAILABLE per reviewer report returned through Owner transport."
    r2_to_r3_repair_scope:
      - "Introduce private.master_reference_history for durable first semantic use across the closed 11-type Master Data allowlist."
      - "Backfill every currently provable retained semantic reference and import existing reason-history evidence."
      - "Capture OLD semantic references before UPDATE/DELETE erases FK evidence and capture/lock NEW references before holder writes commit."
      - "Cover nine retained semantic-holder tables; keep temporary upload reservations and staged Candidate document changes current-only rather than permanent history."
      - "Make master_usage_exists consult durable history before current-reference defense-in-depth scans."
      - "Add behavior regression for trusted Candidate Qualification removal, prior Interview Format/Room after schedule replacement, Recruitment Source clear, mutable master-to-master replacement, rollback/no-false-positive, trigger/ACL inventory."
      - "Permanently gate the durable semantic-reference regression in Integration CI without removing or weakening existing verification."
    producer_verification:
      focused_green_run: "34575487063 PASS"
      final_full_verification_run: "34575867899 PASS"
      verify_branch: verify/S06-001-R3-9002c9b
      verify_head: "66bb96f9409eadd89f61fe009521ef583cdb2d99"
      equivalence: "verify head is exact candidate 9002c9be26c57a182494b9b0de46ae612f32d81e plus only .github/workflows/s06-001-r3-final-verify.yml"
      governance: PASS
      web: "PASS — npm ci/audit, design check, lint, typecheck, build, Chromium install, full web tests"
      database: "PASS — diff hygiene, zero-state replay, accepted PRE-S04/S05/S06 regressions, durable semantic history regression, concurrent idempotency, deterministic Interview Format race, DB advisors, cleanup"
    review_package: project_control/reviews/S06_001_IMPLEMENTATION_R3_GATE_9002c9b_v1.md
  independent_implementation_review:
    work_id: S06-001-IMPLEMENTATION-REVIEW-001-R3
    reviewer: eiu-reviewer
    status: WAITING_EXTERNAL_REVIEW
    reviewed_sha: "9002c9be26c57a182494b9b0de46ae612f32d81e"
    result: PENDING
    source_reopen_required: PENDING
    blocking_findings: PENDING
    evidence_branch: PENDING
    evidence_commit: PENDING
    evidence_path: PENDING
  implementation_execution_hold: "Exact-SHA independent R3 implementation review; no product serialization to integration before PASS + SOURCE_REOPEN_REQUIRED=false."
  implementation_safe_frontier: NONE

implementation_materialization:
  task: TASK-S06-001
  prompt_review: "PASS S06-001-PROMPT-REVIEW-002 @ 68d96b39e309ee6f1edbe6cf4031c10a583b0269"
  source_reopen_required: false
  prompt: project_control/prompts/SLICE-06_TASK-001_v2.md
  checkpoint: checkpoint/pre-S06-001-001
  branch: oanhpham-kobe/TASK-S06-001-master-data-lifecycle
  baseline_sha: "0ec409915bdd00b61b1b7affdb77ec778c7c1dc7"
  status: COMPLETE
  current_candidate_sha: "9002c9be26c57a182494b9b0de46ae612f32d81e"
  review_round: R3

safe_frontier:
  eligible_tasks: []
  skipped_due_to_dependency: []
  materialization_frontier: []
  execution_hold: "TASK-S06-001 waits for independent R3 implementation review of exact SHA 9002c9be26c57a182494b9b0de46ae612f32d81e."

stop_gate:
  status: WAITING_EXTERNAL_REVIEW
  type: INDEPENDENT_IMPLEMENTATION_REREVIEW
  work_id: S06-001-IMPLEMENTATION-REVIEW-001-R3
  target: "TASK-S06-001 R3 repair candidate 9002c9be26c57a182494b9b0de46ae612f32d81e"
  reviewer: eiu-reviewer
  source_reopen_required: PENDING
  resume_on: "Independent reviewer PASS + SOURCE_REOPEN_REQUIRED=false for exact candidate SHA, then verify review report and compose reviewed product delta onto integration."

next_action: "Obtain independent S06-001 R3 implementation review for exact SHA 9002c9be26c57a182494b9b0de46ae612f32d81e using project_control/reviews/S06_001_IMPLEMENTATION_R3_GATE_9002c9b_v1.md. On BLOCKING_REPAIR, repair only the minimum task-branch scope and repeat verification/review. On OWNER_DECISION_REQUIRED, stop for Owner. On PASS + SOURCE_REOPEN_REQUIRED=false, proceed to governed integration composition; do not push/merge main, deploy Vercel, or apply connected Supabase migrations without explicit Owner authorization."
'''

p.write_text(prefix + new_tail, encoding='utf-8')
