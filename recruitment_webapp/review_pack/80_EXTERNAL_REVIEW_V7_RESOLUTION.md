# 80. External Full Review v7 Resolution

**Status: HISTORICAL / SUPERSEDED.** Retained for traceability; current package behavior is governed by `source_registry.yaml` and `85_EXTERNAL_REVIEW_V8_IMPLEMENTATION_ALIGNMENT_V1_11.md`.
**External Review v7** resolution status: all specification findings targeted-resolved in v1.9. — v1.9

**Historical source review:** `review_inputs/external_full_review_v7_2026-09-03.md`. No new owner decision required; Business Logic Core v1.2 remains FROZEN.

## P0 resolution
- **P0-01:** canonical split retained: normal schedule/resource mutations use `resource_blocking`; parent Application Reactivate alone uses `reactivation_conflict_relevant = resource_blocking AND end_at > transaction_now`. Current sources/machine spec/acceptance use the same vocabulary.
- **P0-02:** manual `NEW` and `READ` are both rejected whenever any active Application exists. Derived calculator is exclusive authority in that state.
- **P0-03:** owner has operationally retained bulk UI; therefore Phase 1 now defines named batch commands for Candidate Active/Inactive, latest-Submission NEW/READ, Interview Delete/Inactive, Interview Schedule Status and HR Report Status. Lifecycle/status batches are ALL_OR_NOTHING; browser loops are forbidden.

## P1 resolution
- New/changed master references require active rows; unchanged historical inactive references remain valid.
- Re-add Participant requires active Internal User. Normal deactivation/HR-role removal is blocked while current participation exists on a non-elapsed resource-blocking Interview.
- EDIT Candidate Form Session target must belong to same Candidate.
- Published Privacy Notice DELETE is forbidden in normal Phase 1.
- `private.is_structurally_empty_default_round()` is the single Copy/delete predicate.
- Participant current/removed lifecycle and Candidate verified-email immutability receive DB guards.
- Implementation Notes defer to `source_registry.yaml` rather than stale numeric ranges.
- Email Outbox permits at most one initiating human actor.
- Retained PRODUCTION email usage is downstream Submission history and blocks unused hard-delete; exact `submission_id` trace remains.

## Responsive integration / owner UAT correction
Responsive Prototype v1.5 is included in the Full Handover. Interview/Report badges use 144px benchmark. Status menu opens from the Status badge/button bounds, not pointer coordinates; it uses the badge width for row menus and dismisses on outside click, Escape, selection or same-trigger toggle.

## Gate
Technical v1.9 is ready for external re-review but not frozen. Production remains NO.
