# Changelog v1.5 — 02/09/2026

- Resolved External Review v3.
- Added Candidate Form Session for pre-submit and edit-file staging.
- Added authoritative Submission recalculation and parent locking.
- Closed add-participant/reschedule race with Interview-row-first lock order.
- Added Internal Google first-login provisioning and Root break-glass runbook.
- Hardened document logical parent/type model and privacy acknowledgement.
- Added referenced-master structural immutability policy.
- Added Application Reactivate.
- Frozen Candidate Inbox parent summary to latest Submission.
- Deferred system email attachments beyond Phase 1.
- Added grouped pagination, validation contract, malware scan go-live rule and PII-search URL restriction.
- Design System advanced to v1.4 with table width/accessibility/security-page corrections.
## Final consistency hardening
- Added DB guards for Candidate staged document changes: OPEN-session requirement, NEW_SUBMISSION ADD-only, reservation/session/type matching, one reservation per staged mutation and one pending mutation per target logical document.
- Added `private.validate_candidate_form_document_plan()` starter invariant to require finalizable CLEAN uploads, max 5 effective current files and at least one effective current CV before Candidate Save/Submit.
- Added acceptance/schema-conformance coverage for the staged document plan.

