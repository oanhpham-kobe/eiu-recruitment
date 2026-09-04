# 87. External Review v9 Implementation Alignment v1.12

> **HISTORICAL / SUPERSEDED by v1.13.** Retained as review evidence only; not current source-of-truth.

> **CURRENT / NORMATIVE — 03/09/2026.** Resolves `review_inputs/external_full_review_v9_2026-09-03.md` against Full Handover v1.11.

## Decisions applied without reopening Business Logic Core
1. Operational Interview invariant: every current Participant must resolve to an Active Internal User before scheduling, uncancelling or reactivation makes the Interview resource-blocking. Stable error: `CURRENT_PARTICIPANT_INACTIVE_REASSIGN_REQUIRED`.
2. Retained PRODUCTION exact-Submission email trace remains authoritative. Therefore `delete_unused_submission` is **MAINTENANCE_ONLY**, removed from normal HR production permissions/UI; normal submitted Submissions use retention/lifecycle rather than hard-delete.
3. Schedule conflicts are identical across source/contract/prototype: Candidate + Room + Interviewer BLOCK using `[start,end)`; CANCELLED/access-inactive/no-interval rows do not block.
4. Copy to another Application fills structurally empty default Round 1 else creates next legal round; source schedule/logistics prefill and Demo Topic blank. Incoming/outgoing Copy provenance counts as business usage.
5. Single manual Submission status is latest-only, matching Candidate-level UI and bulk semantics.
6. Authorization vocabulary uses `candidate_self` consistently.
7. Responsive Prototype v1.8 adds schedule/copy behavior QA and route-level overflow smoke coverage.

## Gate impact
Business Logic Core v1.2 remains FROZEN. Technical Architecture advances to v1.12 AMENDED + VALIDATED / NOT FROZEN. Design System remains v1.8. Responsive Prototype advances to v1.8 / READY FOR OWNER VISUAL UAT / NOT FROZEN. Production Ready remains NO.
