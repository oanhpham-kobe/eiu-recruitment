# 73. Domain Glossary & Canonical Predicates — v1.8

**Status: CURRENT / NORMATIVE.** If another current document uses these terms differently, this file wins and that document must be corrected.

| Term | Canonical meaning |
|---|---|
| Submission Manual State | `NEW`, `READ` |
| Submission Derived State | `PROCESSED`, `DONE`, `CLOSED` |
| Candidate Reactivation Rule | lifecycle exception: no active Application → `READ` |
| Interview `access_active` | `Application.is_active AND Interview.is_active` |
| Current Round | highest `round_no` among `access_active` Interviews |
| Interview `resource_blocking` | `access_active AND schedule_status_code != CANCELLED AND start_at/end_at exist` |
| `reactivation_conflict_relevant` | **Application Reactivate-only**: `resource_blocking AND end_at > transaction_now`; fully elapsed rows are historical and do not block lifecycle recovery |
| Application Durable Identity | globally unique `(submission_id, unit_id, department_team_id, position_id)` across history |
| Privacy Notice Version | server-published immutable content version pinned to Form Session |
| Logical Document | stable document identity across immutable versions under fixed parent/type |

## Usage
Contextual Interviewer access uses `access_active` + current participant + visibility + active user. Report/outcome/PDF uses Current Round. Normal schedule/resource mutations use every `resource_blocking` Interview, regardless of Current Round. `reactivation_conflict_relevant = resource_blocking AND end_at > transaction_now` is an **Application Reactivate-only** lifecycle-recovery predicate. Application Reactivate revalidates only children that become `reactivation_conflict_relevant`; fully elapsed intervals remain history and do not block reactivation.

Exact same durable Application identity never creates a second Application row. If inactive, Reactivate it; if active, update after duplicate confirmation. CLOSED Submission may get a new Application only for a different assignment identity.

## Schedule Conflict Relevant
`resource_blocking AND end_at > transaction_now` for operational conflict/re-activation checks. Fully elapsed intervals remain history and do not block a current lifecycle recovery.

## Active Application Owner
Every Active Application has one `hr_owner_id` that resolves to an Active HR/root user. Inactive historical Applications may retain a former inactive owner.

## Email History Cleanup Classification
Operational Email History deletion requires explicit `TEST_RECORD` or `WRONG_RECORD` classification, exact delete/view/context permission, reason text where required, and immutable security audit.


## Operational participant eligibility
`all_current_participants_selectable(interview_id)` = every `interview_participants.is_current=true` row resolves to an existing Active `app_user`. This predicate is required before a mutation makes an Interview `resource_blocking`; failure uses `CURRENT_PARTICIPANT_INACTIVE_REASSIGN_REQUIRED`.

## Copy provenance usage
A Round is not structurally empty when `copied_from_interview_id IS NOT NULL` or any Interview references it as `copied_from_interview_id`. Copy provenance therefore counts as business usage for copy/delete decisions.
