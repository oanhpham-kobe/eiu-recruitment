from pathlib import Path

path = Path('project_control/AUTONOMY_RUN_STATE.yaml')
text = path.read_text()

slice_start = text.index('slice_06_planning:\n')
materialization_start = text.index('\nimplementation_materialization:\n', slice_start)
prefix = text[:slice_start]
s06 = text[slice_start:materialization_start]
tail = text[materialization_start + 1:]


def replace_between(src: str, start_marker: str, end_marker: str, replacement: str) -> str:
    start = src.index(start_marker)
    end = src.index(end_marker, start)
    return src[:start] + replacement + src[end:]


candidate_block = '''  implementation_candidate:
    branch: oanhpham-kobe/TASK-S06-001-master-data-lifecycle
    baseline_sha: "0ec409915bdd00b61b1b7affdb77ec778c7c1dc7"
    prior_candidate_sha: "0c4b94b29e08e1ad877583bdb90d522e5577dccc"
    candidate_sha: "dced5aac32e6b09181cd53d0011b9c951edf2814"
    changed_files_count: 7
    source_reopen_required: false
    prior_independent_review:
      work_id: S06-001-IMPLEMENTATION-REVIEW-001
      reviewer: eiu-reviewer
      status: VERIFIED_FROM_OWNER_TRANSPORT
      reviewed_sha: "0c4b94b29e08e1ad877583bdb90d522e5577dccc"
      result: BLOCKING_REPAIR
      source_reopen_required: false
      blocking_findings:
        - "Durable first-use history for cancellation/rejection reasons was not preserved after accepted lifecycle normalization cleared current reason FKs."
        - "Inactive historical Document Types incorrectly blocked trusted Candidate REPLACE/DELETE flows."
        - "Interview Format structural metadata was not locked across authoritative first-use validation, leaving a concurrent metadata-update race."
        - "master_data.manage could not read inactive master rows required for lifecycle/history management."
      evidence_persistence: "Reviewer report accepted through Owner/coordinator transport; no unverified GitHub evidence coordinates are claimed."
    r1_repair_scope:
      - "Capture durable cancellation/rejection reason first-use history before/through lifecycle normalization and include that history in master usage decisions."
      - "Allow trusted Candidate EDIT historical REPLACE/DELETE for the unchanged inactive Document Type while keeping ADD/new selection active-only."
      - "Make staged-document terminalization transition-aware so trusted PENDING->APPLIED/CANCELLED does not revalidate already-finalized staging prerequisites, while preserving immutable one-way state."
      - "Lock authoritative Interview Format metadata with transaction-scoped key-share semantics before room/link requirement validation."
      - "Expose inactive management rows only to authorized master_data.manage while preserving accepted anonymous active-only lookup semantics and deny-by-default DML."
      - "Use fresh isolated concurrent-idempotency fixtures and permanently wire reviewer regressions into Integration CI."
    producer_verification:
      focused_green_run: "34556347568 PASS"
      final_full_verification_run: "34571849619 PASS"
      verify_branch: verify/S06-001-R2-dced5aa
      verify_head: "350d32671ab9bd22b93758a19c80c4e4f56d995b"
      equivalence: "verify head is exact candidate dced5aac32e6b09181cd53d0011b9c951edf2814 plus only the temporary verification workflow"
      governance: PASS
      web: "PASS — npm ci/audit, design check, lint, typecheck, build, Chromium install, full web tests"
      database: "PASS — diff hygiene, zero-state replay, accepted PRE-S04/S05/S06 regressions, R1/R2/R4 regressions, concurrent idempotency, deterministic R3 race, DB advisors"
      initial_verify_harness_failure: "Run 34571769839 failed before DB startup because shallow checkout could not resolve the historical diff base; workflow-only fetch-depth repair produced PASS run 34571849619 with no candidate change."
    review_package: project_control/reviews/S06_001_IMPLEMENTATION_R2_GATE_dced5aa_v1.md
'''

review_block = '''  independent_implementation_review:
    work_id: S06-001-IMPLEMENTATION-REVIEW-001-R2
    reviewer: eiu-reviewer
    status: WAITING_EXTERNAL_REVIEW
    reviewed_sha: "dced5aac32e6b09181cd53d0011b9c951edf2814"
    result: PENDING
    source_reopen_required: PENDING
    blocking_findings: PENDING
    evidence_branch: PENDING
    evidence_commit: PENDING
    evidence_path: PENDING
'''

s06 = replace_between(
    s06,
    '  implementation_candidate:\n',
    '  independent_implementation_review:\n',
    candidate_block,
)
s06 = replace_between(
    s06,
    '  independent_implementation_review:\n',
    '  implementation_execution_hold:',
    review_block,
)

hold_start = s06.index('  implementation_execution_hold:')
frontier_start = s06.index('  implementation_safe_frontier:', hold_start)
hold_block = '  implementation_execution_hold: "Exact-SHA independent R2 implementation review; no product serialization to integration before PASS + SOURCE_REOPEN_REQUIRED=false."\n'
s06 = s06[:hold_start] + hold_block + s06[frontier_start:]
frontier_start = s06.index('  implementation_safe_frontier:')
frontier_end = s06.find('\n', frontier_start)
s06 = s06[:frontier_start] + '  implementation_safe_frontier: NONE' + s06[frontier_end:]

for marker in ('implementation_materialization:\n', 'safe_frontier:\n', 'stop_gate:\n', 'next_action:'):
    if marker not in tail:
        raise SystemExit(f'missing expected tail marker: {marker!r}')

new_tail = '''implementation_materialization:
  task: TASK-S06-001
  prompt_review: "PASS S06-001-PROMPT-REVIEW-002 @ 68d96b39e309ee6f1edbe6cf4031c10a583b0269"
  source_reopen_required: false
  prompt: project_control/prompts/SLICE-06_TASK-001_v2.md
  checkpoint: checkpoint/pre-S06-001-001
  branch: oanhpham-kobe/TASK-S06-001-master-data-lifecycle
  baseline_sha: "0ec409915bdd00b61b1b7affdb77ec778c7c1dc7"
  status: COMPLETE
  current_candidate_sha: "dced5aac32e6b09181cd53d0011b9c951edf2814"
  review_round: R2

safe_frontier:
  eligible_tasks: []
  skipped_due_to_dependency: []
  materialization_frontier: []
  execution_hold: "TASK-S06-001 waits for independent R2 implementation review of exact SHA dced5aac32e6b09181cd53d0011b9c951edf2814."

stop_gate:
  status: WAITING_EXTERNAL_REVIEW
  type: INDEPENDENT_IMPLEMENTATION_REREVIEW
  work_id: S06-001-IMPLEMENTATION-REVIEW-001-R2
  target: "TASK-S06-001 R2 repair candidate dced5aac32e6b09181cd53d0011b9c951edf2814"
  reviewer: eiu-reviewer
  source_reopen_required: PENDING
  resume_on: "Independent reviewer PASS + SOURCE_REOPEN_REQUIRED=false for exact candidate SHA, then verify review report and compose reviewed product delta onto integration."

next_action: "Obtain independent S06-001 R2 implementation review for exact SHA dced5aac32e6b09181cd53d0011b9c951edf2814 using project_control/reviews/S06_001_IMPLEMENTATION_R2_GATE_dced5aa_v1.md. On BLOCKING_REPAIR, repair only the minimum task-branch scope and repeat verification/review. On OWNER_DECISION_REQUIRED, stop for Owner. On PASS + SOURCE_REOPEN_REQUIRED=false, proceed to governed integration composition; do not push/merge main, deploy Vercel, or apply connected Supabase migrations without explicit Owner authorization."
'''

path.write_text(prefix + s06 + '\n' + new_tail)
