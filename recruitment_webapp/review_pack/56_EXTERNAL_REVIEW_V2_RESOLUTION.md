# 56. External Review v2 Resolution

> **STATUS: HISTORICAL / SUPERSEDED.** Historical resolution log; current behavior is in v1.7 normative modules.

Source: `review_inputs/external_review_v2_2026-09-02.txt`. This file records how v1.4 handled the review without reopening already frozen business choices unnecessarily.

## Accepted P0/P1 changes
1. `submissions.view` is read-only; NEW→READ requires `submissions.status`. Default HR receives it.
2. Bound Internal User identity rebinding separated from directory management; Root-only Phase 1.
3. `interview_note` and `hr_report_note` are separate physical fields with different visibility.
4. Schedule conflict protection uses mandatory advisory/resource locking + recheck; interval `[start,end)`.
5. Shared conflict engine runs on save/reschedule, participant add/re-add when scheduled, reactivate and CANCELLED→active.
6. Added `reactivate_interview` contract.
7. Added atomic Candidate first-login provisioning/rebind flow.
8. Application selection resolves explicit Submission; never guesses latest.
9. Added schema conformance matrix and physical columns previously missing.
10. Fixed null-team hierarchy bug using null-safe equality.
11. Physicalized Phase 1 master data.
12. Defined `effective_interview_active = application.is_active AND interview.is_active`.
13. Empty auto-created Round 1 may be deleted with unused Application.
14. Added command coverage matrix and missing mutation contracts.
15. Candidate and HR use separate writable DTO allowlists.
16–17. Hardened logical document versioning + two-phase upload.
18–19. Corrected email semantics and added recipient/attachment allowlists.
20. Locked participant lifecycle concurrency rules.
21. Added privacy notice acknowledgement capability.
22. Darkened Success/Warning status foregrounds for WCAG AA target.
24. Added deterministic desktop colgroup widths.
25. Future navigation modules are hidden, not rendered placeholders.
26. Rebuilt consistency validator to fail closed on empty parsed sources.
28. Added measurable NFR baseline targets.
29. Added indexed/server-side search strategy baseline.
30. Pin dependency versions/lockfile + auth upgrade regression in CI.

## Already resolved / not reopened
- CLOSED Submission may still receive a new Application per frozen business rule.
- CV remains required; other Candidate document categories optional.
- Nam/Nữ gender choice remains frozen Phase 1.
- User-facing Email History remains deletable; immutable audit is separate.
- Generic `overflow-wrap:anywhere` was already prohibited by the current Design System; v1.3 makes it more explicit.
- `decision_revision_no` remains optional P2; decision timestamp + UUID tie-break retained.

## Owner decisions closed after v1.3
Candidate overlap = BLOCK; Candidate Auth = Email OTP; uploads = approved PDF/Word/PPT/PNG/JPEG, 5 files, 5MB; current business retention = no automatic purge + capacity warning/archive decision; official PDF layout = intentionally deferred.
