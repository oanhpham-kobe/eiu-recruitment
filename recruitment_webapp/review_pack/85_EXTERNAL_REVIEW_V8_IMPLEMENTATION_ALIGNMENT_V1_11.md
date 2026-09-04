# 85. External Review v8 — Implementation Alignment v1.11

> **HISTORICAL / SUPERSEDED by v1.12.** Retained for traceability only; do not use as current authority.

**Status:** CURRENT / NORMATIVE  
**Input review:** `review_inputs/external_full_review_v8_2026-09-03.md`  
**Baseline reviewed:** Full Handover v1.10 + Design System v1.8 + Responsive Prototype v1.6  
**Alignment target:** Full Handover v1.11 + Design System v1.8 + Responsive Prototype v1.7

## Owner decisions
No new owner decision is required for this alignment. The three apparent choices are resolved from already-frozen/current semantics:
1. Candidate inactive blocks Candidate Portal only; internal HR work continues, therefore single/bulk manual NEW/READ use the same rule and do not reject solely because Candidate is inactive.
2. Education requiredness was not frozen in the Validation Contract, therefore the prototype must not invent `required`/minimum-one constraints.
3. Current DB/design model contains Privacy acknowledgement only, therefore Phase 1 does not add a separate accuracy-attestation checkbox/model.

## P0 resolved
- **P0-01:** `bulk_change_interview_schedule_status` now requires `interviews.status` + prerequisite `interviews.view`, matching the single writer. Coverage and permissions matrix are aligned; acceptance explicitly tests manage-without-status denial.
- **P0-02:** `app_spec.yaml` active version fields are coherent at v1.11; legacy `bulk_semantics.mark_submission_new` is removed/replaced by `submission_manual_status`.

## P1 resolved
- Form Session/Upload Reservation expiry is synchronous authority at Stage/Save/Submit/Finalize; cleanup is housekeeping only; canonical terminal transitions are frozen.
- `open_submission` registry encodes base read permission plus conditional NEW→READ mutation requiring `submissions.status`.
- Single/bulk manual Submission status share Candidate-inactive semantics.
- Education fields/min-items are not marked required in current prototype/contract.
- NEW Privacy acknowledgement is unchecked by default; EDIT may only pre-satisfy exact already-acknowledged pinned version.
- Candidate confirmation wording maps to Privacy acknowledgement only; no second attestation model is implied.
- Stale current source pointers are corrected.
- `save_interviewer_report` registry encodes machine-readable OR authorization instead of a pseudo-permission.

## Gate consequence
Business Logic Core v1.2 remains FROZEN. Design System v1.8 remains CURRENT/REVIEWED. Technical Architecture v1.11 is amended + validated and is a freeze-review candidate, not yet production. Responsive Prototype v1.7 is ready for Owner Visual UAT and remains NOT FROZEN until that UAT closes.
