from pathlib import Path
import subprocess

BASE = "6d98a6fa200d32e29dbcaa0a64189811359529e0"
TARGETS = [
    ".omp/RULES.md",
    "AGENTS.md",
    "REVIEW.md",
    "project_control/AUTONOMY_PARALLEL_GOVERNANCE.md",
    "project_control/AUTONOMY_RUN_STATE.yaml",
    "project_control/CHANGELOG_IMPLEMENTATION.md",
    "project_control/CURRENT_STATE.md",
]
subprocess.run(["git", "diff", "--quiet", BASE, "HEAD", "--", *TARGETS], check=True)


def replace_one(path, old, new, label):
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: match count={count}")
    p.write_text(text.replace(old, new, 1), encoding="utf-8")

replace_one(
    "AGENTS.md",
    "The reviewer remains read-only and must not create or move Git refs. OMP main session owns review-result persistence, CI/integration decisions, and checkpoint creation. When the Owner requests GitHub-visible review handoff, OMP main may persist the reviewer result under `project_control/reviews/<TASK_ID>_OMP_REVIEW_<SHORT_SHA>_vN.md`; this is evidence only, not a new authority.\n\nAfter a repair creates a new candidate SHA, any prior PASS belongs to the old SHA and cannot accept the new one. Acceptance requires the OMP independent review PASS and exact-SHA CI PASS for the same final candidate SHA.\n\nBefore risky task implementation, create an immutable recovery ref such as `checkpoint/pre-S04-004-001`. After review and CI PASS, OMP main creates an immutable accepted ref such as `checkpoint/S04-004-accepted-001`. Never force-move an existing checkpoint; create a new numbered checkpoint for a later accepted repair.\n\nFor accepted task checkpoints:\n\n```text\nOMP_REVIEW_SHA == CI_SHA == CHECKPOINT_SHA\n```\n",
    "The reviewer remains read-only and must not create or move Git refs. OMP main session owns review-result persistence, CI/integration decisions, and checkpoint creation. When the Owner requests GitHub-visible review handoff, OMP main persists the reviewer result on a non-candidate evidence branch such as `review/<TASK_ID>-<SHORT_SHA>-vN`, with the artifact at `project_control/reviews/<TASK_ID>_OMP_REVIEW_<SHORT_SHA>_vN.md`. The evidence branch must not mutate the candidate ref; the artifact is evidence only, not a new authority.\n\nAfter a repair creates a new candidate SHA, any prior PASS belongs to the old SHA and cannot accept the new one. The pre-integration candidate review remains bound to that candidate SHA. After serialized integration, if the final integration SHA differs, OMP performs a targeted exact-SHA acceptance re-review/equivalence check on the integration SHA before CI. If serialized integration preserves the exact candidate SHA, the candidate review may serve as the final acceptance review.\n\nBefore risky task implementation, create an immutable recovery ref such as `checkpoint/pre-S04-004-001`. After final OMP acceptance review PASS and exact-SHA CI PASS, OMP main creates an immutable accepted ref such as `checkpoint/S04-004-accepted-001`. Never force-move an existing checkpoint; create a new numbered checkpoint for a later accepted repair.\n\nFor accepted task checkpoints:\n\n```text\nFINAL_OMP_ACCEPTANCE_REVIEW_SHA == CI_SHA == ACCEPTED_CHECKPOINT_SHA\n```\n",
    "AGENTS review SHA binding",
)

replace_one(
    "REVIEW.md",
    "The reviewer must not create/move checkpoint refs or mutate implementation. OMP main session may persist the reviewer result as evidence under `project_control/reviews/<TASK_ID>_OMP_REVIEW_<SHORT_SHA>_vN.md` so external implementers can consume it from GitHub.\n",
    "The reviewer must not create/move checkpoint refs or mutate implementation. OMP main session may persist the reviewer result on a non-candidate evidence branch such as `review/<TASK_ID>-<SHORT_SHA>-vN`, with the artifact under `project_control/reviews/<TASK_ID>_OMP_REVIEW_<SHORT_SHA>_vN.md`, so external implementers can consume it from GitHub without changing the reviewed candidate SHA.\n\nWhen serialized integration produces a different SHA from the reviewed candidate, perform a targeted exact-SHA acceptance re-review/equivalence check on the integration SHA before acceptance CI. That re-review confirms the reviewed implementation delta is preserved, no unauthorized integration drift was introduced, and all blocking findings remain closed. If integration preserves the exact candidate SHA, the candidate review can serve as the final acceptance review.\n",
    "REVIEW evidence branch/integration re-review",
)

replace_one(
    "REVIEW.md",
    "- for accepted task checkpoints, confirm `OMP_REVIEW_SHA == CI_SHA == CHECKPOINT_SHA`;\n",
    "- for accepted task checkpoints, confirm `FINAL_OMP_ACCEPTANCE_REVIEW_SHA == CI_SHA == ACCEPTED_CHECKPOINT_SHA`;\n",
    "REVIEW final equality",
)

replace_one(
    ".omp/RULES.md",
    "15. OMP main session, not the reviewer, owns GitHub review-artifact persistence, exact-SHA CI/integration decisions, and immutable pre-task/accepted checkpoint refs. Accepted checkpoint requires OMP review SHA == CI SHA == checkpoint SHA.\n",
    "15. OMP main session, not the reviewer, owns GitHub review-artifact persistence on non-candidate evidence branches, integration/CI decisions, and immutable checkpoints. If serialized integration changes SHA, run targeted final exact-SHA OMP acceptance re-review; accepted checkpoint requires final OMP acceptance-review SHA == CI SHA == accepted-checkpoint SHA.\n",
    "sticky final equality",
)

replace_one(
    "project_control/AUTONOMY_PARALLEL_GOVERNANCE.md",
    "When GitHub-visible handoff is required, OMP main session may persist the reviewer output under:\n\n```text\nproject_control/reviews/<TASK_ID>_OMP_REVIEW_<SHORT_SHA>_vN.md\n```\n\nThat file is evidence only. At minimum it records task ID, exact 40-character reviewed SHA, `PASS | BLOCKING_REPAIR | OWNER_DECISION_REQUIRED`, evidence-backed findings, and `SOURCE_REOPEN_REQUIRED: YES | NO`. It never becomes product, scheduling, or authorization authority.\n\nA repair that changes the candidate SHA invalidates acceptance of the old SHA. The new SHA receives producer re-review plus targeted OMP re-review before acceptance.\n",
    "When GitHub-visible handoff is required, OMP main session persists the reviewer output on a non-candidate evidence branch, for example:\n\n```text\nreview/<TASK_ID>-<SHORT_SHA>-vN\n```\n\nwith the artifact at:\n\n```text\nproject_control/reviews/<TASK_ID>_OMP_REVIEW_<SHORT_SHA>_vN.md\n```\n\nThe evidence branch MUST NOT move or mutate the reviewed candidate ref. The file is evidence only. At minimum it records task ID, exact 40-character reviewed SHA, `PASS | BLOCKING_REPAIR | OWNER_DECISION_REQUIRED`, evidence-backed findings, and `SOURCE_REOPEN_REQUIRED: YES | NO`. It never becomes product, scheduling, or authorization authority. Evidence branches are append-only review handoff surfaces, not integration or task branches.\n\nA repair that changes the candidate SHA invalidates acceptance of the old SHA. The new SHA receives producer re-review plus targeted OMP re-review before acceptance.\n\nSerialized integration may preserve the candidate SHA (fast-forward) or produce a new integration SHA (for example by cherry-pick/merge). If the SHA changes, OMP MUST perform a targeted exact-SHA final acceptance re-review/equivalence check on the integration SHA before acceptance CI. The targeted review verifies that the independently reviewed implementation delta is preserved, integration introduced no unauthorized behavioral drift, and all blocking findings remain closed. If the exact SHA is preserved, the candidate review may serve as the final acceptance review.\n",
    "AUTONOMY evidence/integration semantics",
)

replace_one(
    "project_control/AUTONOMY_PARALLEL_GOVERNANCE.md",
    "After independent OMP review PASS and exact-SHA CI PASS on the same final candidate, OMP main session creates an immutable accepted ref, for example:\n\n```text\ncheckpoint/S04-004-accepted-001\n```\n\nCheckpoint refs are append-only recovery anchors. Never force-move an existing checkpoint. A later accepted repair receives a new numbered ref. Task acceptance requires:\n\n```text\nOMP_REVIEW_SHA == CI_SHA == CHECKPOINT_SHA\n```\n",
    "After final OMP acceptance review PASS and exact-SHA CI PASS on the final integration SHA, OMP main session creates an immutable accepted ref, for example:\n\n```text\ncheckpoint/S04-004-accepted-001\n```\n\nCheckpoint refs are append-only recovery anchors. Never force-move an existing checkpoint. A later accepted repair receives a new numbered ref. Task acceptance requires:\n\n```text\nFINAL_OMP_ACCEPTANCE_REVIEW_SHA == CI_SHA == ACCEPTED_CHECKPOINT_SHA\n```\n\nThe earlier candidate-review SHA may differ from this final triple when serialized integration changes Git identity; that difference is valid only when the final exact-SHA acceptance re-review/equivalence check passes.\n",
    "AUTONOMY accepted checkpoint equality",
)

replace_one(
    "project_control/AUTONOMY_RUN_STATE.yaml",
    'next_action: "Before any TASK-S04-004 application edit, verify immutable recovery ref checkpoint/pre-S04-004-001 points to the final reviewed governance baseline; then dispatch TASK-S04-004 using project_control/prompts/SLICE-04_TASK-004_v3.md under the producer-self-review -> OMP independent review -> impact-selected exact-SHA CI -> immutable accepted-checkpoint lifecycle."\n',
    'next_action: "Before any TASK-S04-004 application edit, verify immutable recovery ref checkpoint/pre-S04-004-001 points to the final reviewed governance baseline; then dispatch TASK-S04-004 using project_control/prompts/SLICE-04_TASK-004_v3.md under producer self-review -> OMP candidate review -> serialized integration -> final exact-SHA OMP acceptance re-review if SHA changes -> impact-selected exact-SHA CI -> immutable accepted-checkpoint."\n',
    "run state lifecycle correction",
)

replace_one(
    "project_control/CURRENT_STATE.md",
    "- OMP `eiu-reviewer` performs the independent read-only exact-SHA review. OMP main session may commit its result under `project_control/reviews/` so ChatGPT can consume findings directly from GitHub.\n",
    "- OMP `eiu-reviewer` performs the independent read-only exact-SHA review. OMP main persists its result on a non-candidate `review/<TASK_ID>-<SHORT_SHA>-vN` evidence branch under `project_control/reviews/`, so ChatGPT can consume findings directly from GitHub without changing the reviewed candidate SHA.\n",
    "CURRENT evidence branch",
)

replace_one(
    "project_control/CURRENT_STATE.md",
    "- After OMP review PASS and exact-SHA CI PASS on the same candidate, OMP main creates `checkpoint/S04-004-accepted-001` (or the next numbered accepted checkpoint after a later repair). Existing checkpoint refs are never force-moved.\n",
    "- After serialized integration, if Git identity changes, OMP performs a targeted final exact-SHA acceptance re-review/equivalence check. OMP main creates `checkpoint/S04-004-accepted-001` only when final OMP acceptance-review SHA == exact CI SHA == accepted-checkpoint SHA. Existing checkpoint refs are never force-moved.\n",
    "CURRENT final equality",
)

replace_one(
    "project_control/CURRENT_STATE.md",
    "9. continue S04-004 implementation → focused verification → ChatGPT producer self-review/repair → OMP read-only exact-SHA review persisted by OMP main under `project_control/reviews/` → targeted repair/re-review if needed → impact-selected exact-SHA CI → immutable accepted checkpoint → slice-closing review if S04 completes.\n",
    "9. continue S04-004 implementation → focused verification → ChatGPT producer self-review/repair → OMP read-only candidate review persisted by OMP main on a non-candidate review evidence branch → targeted repair/re-review if needed → serialized integration → final exact-SHA OMP acceptance re-review/equivalence check if SHA changes → impact-selected exact-SHA CI → immutable accepted checkpoint → slice-closing review if S04 completes.\n",
    "CURRENT resume lifecycle correction",
)

replace_one(
    "project_control/CURRENT_STATE.md",
    "Verify `checkpoint/pre-S04-004-001` points to this final governance baseline, then use `SLICE-04_TASK-004_v3.md` to dispatch `TASK-S04-004` under the producer-self-review → OMP independent review → impact-selected exact-SHA CI → immutable accepted-checkpoint lifecycle.\n",
    "Verify `checkpoint/pre-S04-004-001` points to this final governance baseline, then use `SLICE-04_TASK-004_v3.md` to dispatch `TASK-S04-004` under producer self-review → OMP candidate review → serialized integration → final exact-SHA OMP acceptance re-review if needed → impact-selected exact-SHA CI → immutable accepted-checkpoint lifecycle.\n",
    "CURRENT next lifecycle correction",
)

replace_one(
    "project_control/CHANGELOG_IMPLEMENTATION.md",
    "- OMP main session owns GitHub review-artifact persistence plus immutable pre-task/accepted checkpoint refs; accepted checkpoint binds OMP review SHA, CI SHA, and checkpoint SHA.\n",
    "- OMP main session owns review-artifact persistence on non-candidate evidence branches plus immutable pre-task/accepted checkpoint refs; if serialized integration changes SHA, a targeted final exact-SHA OMP acceptance re-review binds the final review SHA, CI SHA, and accepted-checkpoint SHA.\n",
    "changelog binding correction",
)

changed = subprocess.check_output(["git", "diff", "--name-only"], text=True).splitlines()
if sorted(changed) != sorted(TARGETS):
    raise SystemExit(f"unexpected changed target set: {changed}")
print("REVIEW SHA BINDING REPAIR TARGET SET: PASS")
