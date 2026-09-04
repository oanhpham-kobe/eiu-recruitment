# Changelog v1.11

- Resolved External Full Review v8 P0/P1 findings on v1.10 baseline.
- Fixed bulk Interview Schedule Status authorization to `interviews.status` + view parity.
- Removed stale app-spec v1.9/legacy Mark-New structured semantics; current version is v1.11.
- Added synchronous Form Session / Upload Reservation expiry authority and canonical lifecycle transitions.
- Added machine-readable conditional mutation metadata for `open_submission`.
- Replaced `save_interviewer_report` pseudo-permission with OR authorization branches.
- Aligned single/bulk manual NEW/READ for inactive Candidates: inactivity alone does not block internal HR action.
- Responsive Prototype v1.7: Education no invented requiredness/min-one; NEW Privacy unchecked by default; Privacy-only acknowledgement wording.
- Corrected current source/version pointers and strengthened validators for review v8 findings.
