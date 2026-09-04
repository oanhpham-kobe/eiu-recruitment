# Changelog v1.1 – Pre-code Validation

## Business decisions resolved
- D-01 → D-14 fully resolved.
- Candidate email is Auth-derived and immutable in profile.
- Internal User email is maintained only in Danh mục by authorized HR/Admin.
- Exact duplicate Application updates existing record after warning/confirmation.
- Bulk assignment does not bulk-copy Demo Topic.
- Tạo lịch handles one Interview Session at a time.
- Copy lịch added; interviewer time conflict blocks save.
- Multiple Interview Sessions supported in Phase 1.
- Final report source uses qualifying report `updated_at`.
- Hired/Rejected blocks interviewer report editing.
- Re-add participant prompts Restore old / Create new.
- Internal User inactive cannot login or be selected for new Interview.
- Inconsistent statuses warn but do not block.
- Delete rule: unused → hard delete; used/referenced → inactive.

## Validation artifacts added
- Paper-UAT dry run.
- 110 edge cases reviewed.
- New findings after enabling multiple interview rounds.
- Pre-code gate status.

## UX/UI
Visual design system remains intentionally deferred until the owner provides the design-system repo.
