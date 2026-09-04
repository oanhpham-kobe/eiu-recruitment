# 91. External Review v11 Implementation Alignment v1.14

> **HISTORICAL / SUPERSEDED.** Retained for review evidence only; current behavior is defined by Review 93 / Gate 94 and `source_registry.yaml`.
> **CURRENT / NORMATIVE — 03/09/2026.** Resolves `review_inputs/external_full_review_v11_2026-09-03.md` against Full Handover v1.13.

## Targeted amendments applied without reopening Business Logic Core
1. Education Qualification remains optional: `submission_education.qualification_id=NULL` skips active-master selection validation; a changed non-null inactive qualification is still rejected.
2. `bulk_change_interview_schedule_status` now inherits the same Active-current-Participant operational eligibility guard and Candidate/Room/Interviewer conflict engine as the single status writer, with ALL_OR_NOTHING rollback.
3. Application Reactivate has one canonical meaning in CURRENT source: only non-elapsed children satisfying `reactivation_conflict_relevant = resource_blocking AND end_at > transaction_now` are rechecked; fully elapsed historical intervals do not block lifecycle recovery.
4. `set_internal_user_active()` is self-contained: deactivation checks both Active Application ownership and non-elapsed resource-blocking current-Participant reassignment before commit.
5. Validation Contract, critical-control registry, README/gate/source pointers and Responsive README/VERSION authority are coherent with Full/Technical v1.14 + Design v1.8 + Responsive v1.9.
6. Semantic validation now checks forbidden legacy Reactivate wording, nullable Education master-reference behavior, bulk participant guard parity, behavior-specific bulk acceptance mapping and current-baseline declarations.
7. Review verification can run validators in `--no-write` mode after manifest verification, so external validation no longer invalidates tracked evidence merely by rerunning checks.

## Gate impact
Business Logic Core v1.2 remains FROZEN. Design System v1.8 remains CURRENT/REVIEWED. Responsive Prototype v1.9 remains the executable Owner Visual UAT reference; executable UI behavior is unchanged in this amendment. Technical Architecture advances to v1.14 AMENDED + VALIDATED / READY FOR FREEZE REVIEW / NOT FROZEN. Production Ready remains NO.
