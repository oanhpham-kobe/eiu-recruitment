# 54. Schema Conformance Matrix — v1.8

Purpose: make the bridge between business Data Dictionary and physical PostgreSQL deterministic. Classification: `PHYSICAL`, `DERIVED`, `SNAPSHOT`, `CONFIG`, `DEFERRED`.

| Entity | Business field/concept | Classification | Physical/Derived source | Writable by | Notes |
|---|---|---|---|---|---|
| Candidate | verified email | PHYSICAL | `candidates.email` | Auth/provision command only | immutable normal profile field |
| Candidate | current name/phone | PHYSICAL | `candidates.current_full_name/current_phone` | submission commands | convenience current profile |
| Candidate | inactive metadata | PHYSICAL | `inactive_at/inactive_by/is_active` | HR candidate-active command | history preserved |
| Candidate | last submission | PHYSICAL | `last_submission_at` | submit command | derived update persisted |
| Submission | snapshot identity/form | PHYSICAL/SNAPSHOT | `submissions.*` + child tables | Candidate/HR DTO-specific commands | email snapshot guarded |
| Submission | HR Note | PHYSICAL | `submissions.hr_note` | HR only | Candidate never sees |
| Submission | updater identity | PHYSICAL | `updated_by_internal_user_id/updated_by_candidate_id` | command | max one |
| Education | qualification | PHYSICAL FK | `qualification_id -> qualification_levels` | Candidate/HR | master data |
| Candidate Form Document Plan | staged file mutations | PHYSICAL + VALIDATED PLAN | `candidate_form_sessions` + `candidate_form_document_changes` + `upload_reservations`; plan validator before Save/Submit | Candidate form commands | staged changes do not mutate persisted current file until commit; DB guards enforce open-session/shape/identity uniqueness |
| Submission Document | logical file identity | PHYSICAL | `submission_document_logicals.logical_document_id` | finalize/save command | header fixes Submission + type across versions |
| Submission Document | type | PHYSICAL FK | `submission_document_logicals.document_type_id` | create logical header only | immutable within one logical document |
| Application | Candidate | DERIVED | Application→Submission→Candidate | none | no duplicate candidate_id |
| Application | durable identity: Submission/Unit/Team/Position | PHYSICAL REFERENCE IDENTITY | `submission_id/unit_id/department_team_id/position_id` + global unique index + null-safe hierarchy guard | create/reactivate command; identity immutable after create | referenced masters cannot change structural meaning once used |
| Application | effective outcome | DERIVED | Current Round report status | none | private view/RPC |
| Interview | operational note | PHYSICAL | `interview_note` | HR | may be contextually visible if page allows |
| Interview | HR report note | PHYSICAL | `hr_report_note` | HR only | never Interviewer |
| Interview | `access_active` | DERIVED | `application.is_active AND interview.is_active` | none | contextual access base predicate |
| Interview | `resource_blocking` | DERIVED | access-active + non-CANCELLED + start/end | none | schedule conflict predicate; independent of Current Round |
| Interview | copy origin | PHYSICAL | `copied_from_interview_id` | copy command | audit lineage |
| Interview | cancel/reject reasons | PHYSICAL FK | reason master tables | HR status command | optional by status/rule |
| Participant | snapshots/order/lifecycle | PHYSICAL | participant table | HR participant commands | versioned |
| Report | qualitative fields | PHYSICAL | report table | owner Interviewer / authorized HR | no scoring |
| Report | final decision fields | PHYSICAL | report table | owner Interviewer / authorized HR | representative entry |
| Report | decision metadata | PHYSICAL | `decision_updated_at/by` | DB/command | changes only with final block |
| Report | current final source | DERIVED | private final-decision view | none | latest decision timestamp |
| Interview Document | logical parent/type | PHYSICAL | `interview_document_logicals` | HR upload command | header fixes Interview + type |
| Interview Document | version/storage metadata | PHYSICAL | `interview_documents` | finalize command | max 5 current/session; CLEAN scan required |
| Email | delivery queue | PHYSICAL | email_outbox | enqueue/worker | leased worker |
| Email | user history | PHYSICAL | email_history | HR business rule | deletable UI history |
| Audit | security trace | PHYSICAL | security_audit_log | system only | immutable |
| Privacy | notice acknowledgement | PHYSICAL | `privacy_acknowledgements.submission_id + notice_version` | Candidate Submit/Edit commands | Candidate derives via Submission; pinned version; same-version idempotent |
| Search | normalized strategy | CONFIG/INDEX | trigram/email/phone indexes + server normalization | system | exact plan verified in perf UAT |
| PDF | pixel layout | DEFERRED | owner official template | later phase | data logic frozen |

## Conformance rule
A coding agent must not invent a DB column merely because a concept appears in prose. If a concept is DERIVED, compute it from the stated source. If PHYSICAL, `database_schema.sql` must contain it or a migration must explicitly supersede the starter.

## Core physical conformance rules
- Pre-submit upload → `candidate_form_sessions` + `upload_reservations`; no premature Submission.
- Submission document parent/type → `submission_document_logicals`; versions → `submission_documents`.
- Interview document parent/type → `interview_document_logicals`; versions → `interview_documents`.
- Privacy acknowledgement → Submission only; Candidate derived.
- Every Phase-1 editable master has optimistic `version_no` where contract claims versioning.
- Manual vs derived Submission status mapping is explicit.

## Privacy, email and master-history conformance
| Entity | Business field/concept | Classification | Physical/Derived source | Writable by | Notes |
|---|---|---|---|---|---|
| Privacy Notice | published version | PHYSICAL/CONFIG | `privacy_notice_versions` | controlled admin/deployment | form session pins published version |
| Candidate Form Session | presented privacy version | PHYSICAL | `presented_privacy_notice_version` | server command | client cannot invent |
| Email Outbox/History | Submission subject | PHYSICAL FK | `submission_id` | enqueue/worker | exact Submission trace |
| Room | historical identity | PHYSICAL MASTER | `rooms` + structural guard | master command | referenced identity cannot be repurposed |
| Submission | aggregate version | PHYSICAL | `version_no` | text/document mutation commands | file-only save bumps once |
