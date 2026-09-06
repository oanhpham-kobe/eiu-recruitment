# CHANGELOG v1.18

**Date:** 06/09/2026

- Incorporate Owner Decisions A–K (Interview Round/Schedule Status, Effective Outcome, HR Permissions, Candidate Reactivate, Repo Public, Blank Conclusion, HR Candidate Correction, Candidate Email Recovery, Historical Interviewer Access, Confirmed Reschedule, Strong-Current Privacy Notice).
- Canonicalize Application HR read (`Root OR applications.view OR applications.manage`) and Interview HR read (`Root OR interviews.view OR interviews.manage`); remove reliance on `submissions.view` for Application and Interview table access.
- Add permissions `applications.view` and `candidates.identity_manage` with dependency `applications.manage -> applications.view`.
- Candidate Submit/Edit contracts align with canonical field ownership: mutable candidate fields (`full_name` <=200, `phone` <=32 normalized, `date_of_birth` 1900-01-01..today, `gender` MALE/FEMALE, `current_address` <=500, Education canonical fields, documents); verified email immutable from Auth; HR-only fields (`other_info`, `hr_note`, experiences, activities) protected from Candidate mutation.
- Strong-current Privacy Notice verification: session pins presentation version, submit/update requires current effective published version; mismatch returns `PRIVACY_NOTICE_CHANGED`.
- Distinguish pure detail read `get_submission_detail()` (pure read, no status mutation) from explicit user-intent command `open_submission()` (which executes NEW->READ transition when authorized).
- Define trusted commands: `reschedule_confirmed_interview`, `correct_submission_candidate_fields_by_hr`, `recover_candidate_email_identity`.
- Authoritative Application outcome resolver based on Current Round (highest `round_no` among access-active Interviews); Current Round HIRED => HIRED, REJECTED => REJECTED, otherwise IN_PROGRESS. Internal helper `recalculate_submission_status` protected by deny-by-default execution ACL (revoked from PUBLIC, anon, authenticated; granted to postgres, service_role).
- Candidate document materialization clarified: logical header per ADD without `UNIQUE(submission_id, document_type_id)`; REPLACE/DELETE target `logical_document_id`; candidate creator/uploader metadata.
- Candidate portal security: server route boundary `/candidate/*`, upload reservation protocol, sessionStorage autosave with session expiry, strict CSP without `unsafe-inline`.
- Database-enabled Integration CI gate and non-production Outbox `TEST` environment safety.
- Current review/gate moved to docs 99/100; v1.17 review/gate become HISTORICAL/SUPERSEDED.
- Technical Architecture v1.18 remains TECHNICAL SPECIFICATION FROZEN; source-level Implementation Gate remains READY TO IMPLEMENT.
- Responsive Prototype executable remains v1.10; Production Ready remains NO.
