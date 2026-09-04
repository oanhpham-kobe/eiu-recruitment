# Changelog v1.12

- Added authoritative Active-current-Participant guard before Interview operationalization.
- Classified `delete_unused_submission` MAINTENANCE_ONLY; removed normal HR production permission/capability because mandatory retained production email trace makes normal submitted Submissions retention-managed.
- Unified Candidate/Room/Interviewer schedule conflict source and prototype behavior.
- Fixed cross-Application Copy to fill structurally empty Round 1; copy logistics source date/time/location and leave Demo Topic blank.
- Copy provenance now counts as Round usage in structural-empty predicate.
- Single manual Submission status now resolves deterministic latest Submission only.
- Normalized Candidate critical-control auth token to `candidate_self`.
- Responsive Prototype v1.8 broadens core-route overflow/browser QA.
