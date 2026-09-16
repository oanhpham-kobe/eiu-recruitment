# Independent Prompt and Governance Review (R4) — TASK-S07-005

- **WORK_ID**: `S07-005-PROMPT-REVIEW-004`
- **REVIEWED_SHA**: `9492293bfe0125acdfd4c26921247d1e6151424d`
- **BASELINE_REF**: `checkpoint/pre-S07-005-004`
- **BASELINE_PEELED_SHA**: `9492293bfe0125acdfd4c26921247d1e6151424d`
- **ROLE**: `OMP_EIU_REVIEWER`
- **VERDICT**: `PASS`
- **SOURCE_REOPEN_REQUIRED**: `false`
- **IMPLEMENTATION_AUTHORIZED**: `false`

---

## Executive Summary

Independent re-review (R4) performed by `eiu-reviewer` on the peeled checkpoint baseline `checkpoint/pre-S07-005-004` at commit `9492293bfe0125acdfd4c26921247d1e6151424d`.

Both historical blocking findings (`S07-005-EXTERNAL-AUDIT-001` and `S07-005-R3-001`) are verified **RESOLVED**. All 10 review verification items passed inspection. No blocking or non-blocking findings remain.

`checkpoint/pre-S07-005-004` is established as the governed pre-task prompt/governance baseline.

**Implementation has NOT started and is NOT authorized.** Per handoff instructions, execution stops at prompt review PASS for external audit and explicit Owner implementation dispatch.

---

## Finding Resolutions

### 1. `S07-005-EXTERNAL-AUDIT-001`: RESOLVED
- Prompt §D explicitly preserves fail-closed `FORBIDDEN` when actor resolution returns `NULL`, rejects a distinct `UNAUTHENTICATED` RPC result, and separates optional missing-session/login UX from the trusted RPC contract.
- Local integration & unit test requirements item 1 expressly requires adapters to preserve `FORBIDDEN` without fabricating `UNAUTHENTICATED`.
- Verified against `private.interview_command_actor` and all four accepted S07-001 email RPCs (`preview_email`, `enqueue_email`, `bulk_enqueue_email`, `delete_email_history`).

### 2. `S07-005-R3-001`: RESOLVED
- At the exact reviewed SHA, `tasks.TASK-S07-005.acceptance` criterion 4 is exactly:
  `"Contextual permissions (interviews.email, emails.history_view, emails.history_delete) and RLS are strictly enforced, with accepted parent-context read predicates applied separately."`
- This completely removes the universal `interviews.manage` implication without modifying accepted permissions or database SQL.

---

## 10 Verification Items Assessment

| # | Verification Item | Result | Evidence / Assessment |
|---|---|---|---|
| 1 | `S07-005-EXTERNAL-AUDIT-001` remains resolved | PASS | Prompt §D and adapter test requirement 1 preserve backend `FORBIDDEN` on null actor; distinct `UNAUTHENTICATED` denied; session login UX separated. |
| 2 | `S07-005-R3-001` is resolved | PASS | Fourth registry acceptance criterion matches required replacement verbatim; `interviews.manage` removed as universal email prerequisite. |
| 3 | Manual email mutations use `interviews.email` | PASS | `preview_email`, `enqueue_email`, `bulk_enqueue_email` resolve `private.interview_command_actor('interviews.email')`. Prompt §D and reconciliation match. |
| 4 | History read uses `emails.history_view` + parent context | PASS | `email_history_select` requires `emails.history_view` and `private.can_read_email_context`. For Interview history, accepts `interviews.view` OR `interviews.manage` OR eligible contextual participant. |
| 5 | History deletion uses `emails.history_delete + emails.history_view` | PASS | `delete_email_history` requires `emails.history_delete` actor capability, `emails.history_view`, and parent context; validates `TEST_RECORD` / `WRONG_RECORD` ($\le 1000$ chars reason); atomic audit insert precedes deletion. |
| 6 | `interviews.manage` is not universal email capability | PASS | No operative requirement represents `interviews.manage` as universal email capability. Its valid role remains an alternative parent-read permission. |
| 7 | Prompt, reconciliation, and registry consistency | PASS | All three documents are mutually consistent on granular email permissions, contextual history access, accepted RPC consumption, preview fencing, unchanged Interview status, and pure-consumer scope. |
| 8 | Accepted predecessor SQL unchanged | PASS | Byte-for-byte preserved. `git diff --exit-code` confirms zero differences across `supabase/migrations` against `checkpoint/S07-001-accepted-001` and `checkpoint/S07-004-accepted-001`. |
| 9 | `SOURCE_REOPEN_REQUIRED: false` | PASS | Truthful and supported. Both repaired defects concerned consumer prompt/governance instructions, not accepted database behavior. Zero migration changes required. |
| 10 | Implementation unauthorized | PASS | Implementation remains unauthorized. Prompt dispatch gate, reconciliation, registry, and autonomy run state enforce stop at prompt PASS awaiting explicit Owner dispatch. |

---

## Review Findings

Zero blocking findings. Zero non-blocking findings.

---

## Decision and Lifecycle State

- **Prompt Review Status**: `PASS`
- **Governed Pre-Task Baseline**: `checkpoint/pre-S07-005-004` (`9492293bfe0125acdfd4c26921247d1e6151424d`)
- **Historical Checkpoints Preserved**:
  - `checkpoint/pre-S07-005-001` (`0d5973e...`)
  - `checkpoint/pre-S07-005-002` (`44de446...`)
  - `checkpoint/pre-S07-005-003` (`0c9646e...`)
- **Implementation Status**: `NOT_STARTED`
- **Active Executors**: `0`
- **Stop Gate**: `S07_005_PROMPT_REVIEW_PASS_AWAITING_OWNER_DISPATCH`
- **Next Action**: Await explicit Owner implementation dispatch for `TASK-S07-005`.
