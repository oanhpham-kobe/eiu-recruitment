# 83. External Review v7 — v1.10 Implementation Alignment Resolution

> **HISTORICAL / SUPERSEDED by v1.11.** Retained for traceability only; do not use as current authority.

**Status: CURRENT / NORMATIVE.**  
**Nature:** follow-up alignment against the already received External Review v7 findings; **this is not a new external review**.  
**Baseline:** Full Handover v1.10 + Design System v1.8 + Responsive Prototype v1.6.

## Closed alignment findings
1. **Candidate lifecycle vs Submission workflow**
   - `candidate.is_active` is a lifecycle flag only.
   - Submission status remains `NEW / READ / PROCESSED / DONE / CLOSED`.
   - Inactivation never writes `INACTIVE` to Submission.
   - Candidate Inbox parent row derives Status/HR Note from deterministic latest Submission.

2. **Bulk manual Submission status**
   - Application Inbox selection entity is Candidate.
   - Canonical command: `bulk_set_latest_submission_manual_status(candidate_ids, status, expected_latest_submission_ids, expected_versions[])`.
   - Manual target is `NEW | READ` only.
   - Server resolves/locks deterministic latest Submission per Candidate, revalidates preview/version and active-Application guard.
   - Atomicity is **ALL_OR_NOTHING**.
   - Legacy overlapping `bulk_mark_submission_new` is removed from the active command registry.

3. **Phase-1 navigation**
   - Normal persona UAT renders only routes present in the Phase-1 navigation registry.
   - `FUTURE_HIDDEN / NOT_RENDERED` destinations are excluded from ordinary sidebar/navigation.

4. **HR Report semantics**
   - Aggregate drawer has no generic Delete.
   - Report Status is stored on Current Interview.
   - Application outcome is derived separately.
   - Final Decision Source uses `decisionUpdatedAt`; qualitative-only edits update `updatedAt` but not `decisionUpdatedAt`.

5. **Candidate form**
   - CV is authoritative-required on Submit/Save.
   - Candidate EDIT exposes staged document `ADD / REPLACE / DELETE`; Cancel discards staged state.
   - Save rechecks editable state and materializes staged changes atomically.

6. **Critical controls**
   - Production-intent critical controls require an expected transition/navigation/dialog contract; generic toast-only fallback is not sufficient evidence.

## Responsive integration
Responsive Prototype v1.6 is an additive correction layer on v1.5. It keeps the v1.5 status-popover anchoring/dismiss/focus behavior and aligns the above business semantics without creating a separate mobile business path.

## Gate consequence
These changes close the known source/prototype alignment blockers, but they do **not** constitute a fresh independent external re-review or Owner Visual UAT. Technical Architecture remains **NOT FROZEN** and Implementation Gate remains **NOT YET PASS** until the current validator/browser evidence and external/owner gates are completed.
