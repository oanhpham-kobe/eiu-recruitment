# 55. UI Action → Backend Command Coverage Matrix — v1.8

Every production mutation maps to one explicit trusted command. Rows without a command are not allowed to ship.

| UI/business action | Permission/context | Command | Transaction/lock | Audit | Acceptance |
|---|---|---|---|---|---|
| Candidate first OTP login | verified Candidate | `provision_candidate_identity` | atomic identity bind | yes | auth provisioning |
| Open new Candidate form | owner active | `start_candidate_form_session(NEW)` | form-session create | yes | pre-submit parent |
| Open Edit Candidate form | owner + Submission NEW | `start_candidate_form_session(EDIT)` | target/version snapshot | yes | edit eligibility |
| Stage Candidate file add/replace/delete | owner form session | `reserve_candidate_form_upload` + `stage_candidate_document_change` | temp only | yes | Cancel safety |
| Candidate Cancel | owner form session | `cancel_candidate_form_session` | no persisted doc mutation | yes | temp cleanup |
| Candidate Submit | owner active | `submit_candidate_submission` | Candidate/session lock + idempotency | yes | atomic Submission/files/privacy/outbox |
| Candidate Save Edit | owner + NEW | `update_candidate_submission` | Submission/session lock + optimistic version | yes | text+files atomic |
| HR opens NEW | `submissions.view` + `submissions.status` | `open_submission` | atomic NEW→READ | yes | view-only vs full HR |
| View-only HR opens | `submissions.view` | `open_submission` | no mutation | no write audit required; read audit per policy | view-only |
| HR edits Submission | `submissions.edit` + view | `update_submission_by_hr` | optimistic | yes | DTO separation |
| HR add/replace/delete Submission documents | `submissions.edit` + `submissions.view` | `mutate_submission_documents_by_hr` | Submission/logical locks + version bump | yes | max5/CV/CLEAN |
| Manual Submission status | `submissions.status` + view | `set_submission_manual_status` | parent lock | yes | only NEW/READ |
| Derived Submission status | system/internal | `recalculate_submission_status` | Submission FOR UPDATE | yes | concurrent outcomes |
| MAINTENANCE-only Submission repair delete | `MAINTENANCE_ONLY` | `delete_unused_submission` | rejects retained PRODUCTION trace; cache repair | security audit | not normal HR production |
| Hard-delete unused Candidate | `candidates.delete_unused` | `delete_unused_candidate` | usage + session/temp cleanup | security audit | unused only |
| Active/Inactive Candidate | `candidates.active_manage` | `set_candidate_active` | recalc on reactivate | yes | login block |
| Create/update Application | `applications.manage` + submission view | `create_or_update_application` | Submission lock + Round1 | yes | exact selected Submission |
| Reactivate Application | `applications.manage` | `reactivate_application` | Application/Submission + eligible-owner check + non-elapsed `reactivation_conflict_relevant` children | yes | past-only overlaps do not strand lifecycle recovery |
| Delete/Inactive Application | `applications.manage` | `delete_or_inactivate_application` | child usage + Submission recalc | yes | empty Round1 exception |
| Create next round | `interviews.manage` + view | `create_next_interview_round` | Application/latest Interview lock | yes | round race |
| Copy schedule draft/prefill | `interviews.manage` + view | client draft only — **no trusted mutation** | no DB mutation until Save | no | draft only |
| Save Copy Interview schedule | `interviews.manage` + view | `copy_interview_schedule` | target Application/Interview locks + deterministic resource locks + idempotency | yes | AC-23 / AC-COPY-03 / AC-COPY-CMD-01 / AC-PART-OPER-COPY-01 |
| Save/reschedule | `interviews.manage` + view | `save_interview_schedule` | Interview row → resource locks | yes | race conflicts |
| Change schedule status | `interviews.status` + view | `change_interview_schedule_status` | shared conflict framework if operational | yes | CANCELLED→active |
| Reactivate Interview | `interviews.manage` + view | `reactivate_interview` | Interview row → resource locks | yes | middle-round block |
| Delete/Inactive Interview | `interviews.manage` + view | `delete_or_inactivate_interview` | latest guard + durable Interview temp cleanup + Submission recalc | yes | used/unused + no orphan reservation/object |
| Add participant | `interviews.participants` + view | `add_interview_participant` | Interview row first + resource locks | yes | reschedule race |
| Remove participant | `interviews.participants` + view | `remove_interview_participant` | Interview lock + reorder | yes | report warning |
| Re-add participant | `interviews.participants` + view | `readd_interview_participant` | Interview row first + conflict | yes | restore/new |
| Reorder participants | `interviews.participants` + view | `reorder_interview_participants` | Interview lock | yes | concurrent reorder |
| Reserve Interview upload | `interviews.documents` + view | `reserve_interview_upload` | temp reservation | yes | scope/type/count |
| Finalize Interview upload | `interviews.documents` + view | `finalize_interview_upload` | Interview/logical lock | yes | CLEAN scan/version |
| Delete Interview document | `interviews.documents` + view | `delete_interview_document` | usage/path cleanup guard | yes | document-specific delete |
| Save own report | current participant | `save_interviewer_report` | field-aware optimistic | yes | owner conflict |
| HR edits Interviewer report | `reports.edit_interviewer` + view | `save_interviewer_report` | field-aware optimistic | yes | HR stale |
| HR Report Status | `reports.manage_status + reports.view` | `change_report_status` | Current Round + parent Submission lock/recalc | yes | single status writer |
| HR Report Note | `reports.manage_status + reports.view` | `update_hr_report_note` | optimistic note-only | yes | HR-only confidentiality |
| Change Application HR owner | `applications.manage` | `update_application_hr_owner` | Application lock + owner validation | yes | ownership entity boundary |
| Hide/show Interviewer | `reports.visibility` + view | `set_report_visibility` | optimistic | yes | contextual access |
| Delete/Inactive one participant report | `reports.delete` + view | `delete_or_inactivate_report(report_id)` | report-specific guard | yes | no aggregate ambiguity |
| Send system email | corresponding email/context permission | `enqueue_email` | outbox insert | yes | no attachments Phase 1 |
| View Email History | `emails.history_view` + parent context | query/RLS | parent-context filtered | no | no cross-context disclosure |
| Delete Email History | `emails.history_view + emails.history_delete` + parent context | `delete_email_history` | explicit TEST/WRONG cleanup classification | security audit | deterministic eligibility/reason |
| Bulk Application assignment | application permission | `bulk_create_or_update_applications` | ALL_OR_NOTHING | yes | common fields |
| Bulk email | email permission | `bulk_enqueue_email` | per-item enqueue result | yes | success/failed arrays |
| Create master | `master_data.manage` | `create_master_item` | version + structural reference guard | yes | historical semantics |
| Update master | `master_data.manage` | `update_master_item` | version + structural reference guard | yes | historical semantics |
| Delete/Inactive master | `master_data.manage` | `delete_or_inactivate_master_item` | usage guard | yes | unused delete/used inactive |
| Create directory user | directory manage/root | `create_internal_user` | unique email | yes | duplicate |
| First Google bind | verified internal login | `provision_internal_identity_on_first_google_login` | atomic exact-match bind | security audit | conflicting bind reject |
| Assign HR role/defaults | Root | `assign_hr_role_with_defaults` | role + prerequisites/grants | security audit | Full HR defaults |
| Remove HR role | Root | `remove_hr_role` | role + HR permission revoke | security audit | history preserved |
| Edit directory profile | `users.directory_manage` | `update_internal_user_directory` | optimistic | yes | unbound email only |
| Active/Inactive non-HR directory user | `users.directory_manage` | `set_internal_user_active` | target role/root guard + Active Application owner reassignment guard + non-elapsed resource-blocking current-Participant reassignment guard | security audit | HR target Root-only; cannot strand future/current Participant |
| Rebind bound identity | Root | `change_internal_user_identity` | privileged transaction | security audit | takeover prevention |
| Root identity recovery | break-glass operators | `root_admin_break_glass_recovery` | maintenance/recovery | immutable security audit | staging rehearsal |
| Grant permission | Root | `grant_hr_permission` | dependency validation | security audit | invalid combination rejected |
| Revoke permission | Root | `revoke_hr_permission` | dependency validation | security audit | invalid combination rejected |

Grouped pagination/search are read contracts rather than mutations: Candidate Inbox pages Candidate groups; Interview/Report pages Application groups; PII search value is not persisted in URL.

| MAINTENANCE_ONLY unused Internal User cleanup | Root operator only | maintenance procedure (no HR UI command) | unbound/non-HR/non-Root/unreferenced | yes | explicitly outside normal UI command coverage |

| Bulk Candidate Active/Inactive | `candidates.active_manage` | `bulk_set_candidate_active` | Candidate selection + inactive metadata + reactivation recalculation + per-item/batch audit | yes | ALL_OR_NOTHING; AC-BULK-CAND-LIFE-01/02 |
| Bulk latest Submission NEW/READ | `submissions.status` | `bulk_set_latest_submission_manual_status` | Candidate selection → deterministic latest Submission; preview/version recheck; no active Application | yes | ALL_OR_NOTHING |
| Bulk Interview delete/inactivate | `interviews.manage` | `bulk_delete_or_inactivate_interviews` | exact Interview IDs + delete/inactive rules + durable temp cleanup prerequisite | yes | ALL_OR_NOTHING; AC-BULK-INT-DEL-01 |
| Bulk Interview schedule status | `interviews.status` + view | `bulk_change_interview_schedule_status` | exact Interview IDs + Active-current-Participant operational guard + Candidate/Room/Interviewer conflict recheck | yes | ALL_OR_NOTHING; one invalid/ineligible Interview aborts all |
| Bulk HR Report status | `reports.manage_status` | `bulk_change_report_status` | Current Round exact Interview IDs + affected Submission recalculation | yes | ALL_OR_NOTHING; AC-BULK-REPORT-01 |
