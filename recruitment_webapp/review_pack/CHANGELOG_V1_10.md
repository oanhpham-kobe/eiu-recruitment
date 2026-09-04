# CHANGELOG v1.10 — 03/09/2026

Baseline upgraded from Full Handover v1.9 to v1.10 without reopening Business Logic Core v1.2.

## Source/contract alignment
- Candidate lifecycle separated from Submission workflow; `INACTIVE` removed from demo Submission data.
- Candidate-level bulk manual Submission status standardized on `bulk_set_latest_submission_manual_status`.
- Legacy overlapping `bulk_mark_submission_new` removed from active command registry.
- Active command registry now contains 58 unique commands.
- Report Status clarified as Current Interview state; Application outcome is derived.
- Final Decision Source uses `decisionUpdatedAt`.
- Exact internal email DB constraint hardened to the exact `@eiu.edu.vn` domain.
- Current source governance advanced to docs 83/84.

## Responsive Prototype v1.6
- Additive v1.6 layer loaded after v1.5.
- Candidate parent Status/HR Note derives from deterministic latest Submission.
- Candidate Inactive is a separate lifecycle overlay.
- Candidate-level manual status exposes NEW/READ only and is all-or-nothing.
- Historical Submission status is read-only in Candidate-level UX.
- FUTURE_HIDDEN routes removed from normal persona navigation.
- Aggregate HR Report drawer no longer has generic Delete.
- Candidate form now demonstrates CV-required staged ADD/REPLACE/DELETE with Cancel discard and stale-edit block.
- v1.5 anchored/dismissible status menu behavior retained.

## Gate
Technical Architecture v1.10 and Responsive Prototype v1.6 remain NOT FROZEN pending current validation, fresh external re-review and Owner Visual UAT. Production Ready remains NO.
