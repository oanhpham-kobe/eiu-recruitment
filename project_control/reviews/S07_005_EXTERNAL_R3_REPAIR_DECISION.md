# External Repair Decision — TASK-S07-005 R3 Finding

WORK_ID: S07-005-EXTERNAL-R3-REPAIR-001
ROLE: EXTERNAL_CHATGPT_PRODUCER
SOURCE_FINDING: S07-005-R3-001
REVIEWED_REVIEW_ARTIFACT: project_control/reviews/S07_005_PROMPT_REVIEW_0c9646e_v3.md
R3_BASELINE_REF: checkpoint/pre-S07-005-003
R3_BASELINE_PEELED_SHA: 0c9646ecfc71665fdeba1a41023b36ec0e5c0e9a
R3_REVIEW_RECORDING_HEAD: d4117636d5285dd3a622ba01e0d46b6d7914f715
DECISION: ACCEPT_FINDING_AND_REPAIR_GOVERNANCE
SOURCE_REOPEN_REQUIRED: false
IMPLEMENTATION_AUTHORIZED: false

## Independent producer verification

The R3 finding is valid.

Accepted S07-001 email contracts use the granular permission `interviews.email` for the manual email mutation capability:

- `public.preview_email(...)` resolves `private.interview_command_actor('interviews.email')`.
- `public.enqueue_email(...)` resolves `private.interview_command_actor('interviews.email')` and preserves the same permission after locking.
- `public.bulk_enqueue_email(...)` resolves `private.interview_command_actor('interviews.email')` and preserves the same permission after locking.

Email History authorization is separate:

- SELECT requires `emails.history_view` plus `private.can_read_email_context(...)` under RLS.
- `private.can_read_email_context(...)` applies accepted parent-context read predicates; for Interview email history it may be satisfied by `interviews.view`, `interviews.manage`, or the accepted eligible contextual-interviewer predicate. `interviews.manage` is therefore not a universal email capability.
- `public.delete_email_history(...)` requires `emails.history_delete`, `emails.history_view`, and the same accepted parent-context read predicate.

Therefore the existing TASK-S07-005 registry acceptance criterion that names `interviews.manage` as one of the task's contextual permission capabilities is contradictory and must be repaired.

## Required bounded repair

In `project_control/TASK_REGISTRY.yaml`, under `tasks.TASK-S07-005.acceptance`, replace the fourth criterion:

```text
Contextual permissions (emails.history_view, emails.history_delete, interviews.manage) and RLS are strictly enforced.
```

with:

```text
Contextual permissions (interviews.email, emails.history_view, emails.history_delete) and RLS are strictly enforced, with accepted parent-context read predicates applied separately.
```

This is a governance-only repair.

Do NOT:

- modify accepted S07-001 SQL or any accepted predecessor;
- broaden or narrow database permissions;
- change the already-correct TASK-S07-005 implementation prompt or source reconciliation for this finding;
- start TASK-S07-005 implementation;
- move any existing checkpoint;
- start S07-006 or Slice-08.

## Re-review requirement

After the governance repair is committed and validators pass, create a new immutable annotated pre-task checkpoint using the next unused suffix (expected `checkpoint/pre-S07-005-004`) and perform a new independent exact-checkpoint prompt/source/governance review.

The next review must explicitly verify:

1. `interviews.email` is the manual email mutation permission;
2. `emails.history_view` controls operational history visibility together with accepted parent-context predicates;
3. `emails.history_delete` plus `emails.history_view` and accepted parent-context predicates control deletion;
4. `interviews.manage` is not reintroduced as a universal email capability;
5. all historical checkpoints remain immutable;
6. `SOURCE_REOPEN_REQUIRED: false` remains truthful;
7. implementation remains unauthorized until explicit Owner dispatch after independent PASS.
