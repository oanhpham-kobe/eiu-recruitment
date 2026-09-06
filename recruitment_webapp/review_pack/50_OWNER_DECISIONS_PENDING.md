# 50. Owner Decisions — Current Resolved / Deferred

**Current status (v1.18): Owner Decisions A–K canonicalized.** Business Logic Core v1.2 remains FROZEN.

## Resolved owner decisions
- Candidate schedule conflict = **BLOCK** across Applications.
- Candidate Auth = **Email OTP**; Internal Auth = Google Workspace OAuth `@eiu.edu.vn`.
- Candidate edits only while Submission `NEW`; default HR receives Full HR permissions including status management.
- Candidate Inbox parent summary = **latest Submission**; older Submissions are history and do not drive parent summary.
- Upload = PDF, DOC/DOCX, PPT/PPTX, PNG/JPG/JPEG; max **5 current files/parent**, **5 MB/file**; CV required; malware `CLEAN` mandatory before finalize.
- Current retention business policy = **no automatic expiry/purge**; capacity warning → owner-directed storage upgrade or controlled export/archive/purge.
- Phase 1 system email attachments = **none**.
- Application Reactivate = supported Phase 1. Exact same `Submission + Unit + Team + Position` is one **durable global Application identity**; inactive exact identity is reactivated, not duplicated.
- Candidate Reactivate + no active Application → `READ`. Generic recalculation still preserves untouched manual `NEW/READ`.
- Internal bound identity rebind = Root-only; unbound email typo may be directory-edited.
- Internal User hard-delete = **Root maintenance-only** when unbound, non-HR, non-Root and never referenced; no normal HR UI delete.

## Owner Decisions A–K (Canonical in v1.18)
- **A. Interview Round / Schedule Status:** `HIRED` is terminal for future Interview rounds. Latest relevant active Interview `report_status_code = HIRED` => no next round. Latest relevant active Interview not `HIRED` => next round allowed, including when Schedule Status is `CANCELLED`. `CANCELLED` does not block a future round. Latest round being inactive continues to block new-round creation until valid Reactivate/hard-delete handling. Schedule Status has no mandatory sequential transition path; direct jumps are allowed. One Interview round has exactly one Schedule Status at a time.
- **B. Effective Outcome:** Keep current aggregation: any active Application whose effective Current Round outcome is `HIRED` causes Submission `DONE`; otherwise use the newest/highest relevant active round according to existing canonical aggregation.
- **C. HR Permissions:** Keep Phase 1 default Full HR permission policy plus granular revoke. Do not introduce HR role-profile redesign.
- **D. Candidate Reactivate:** Keep deliberate exception: no active Application after Candidate reactivation => Submission `READ`, not `NEW`.
- **E. Repository Visibility:** Keep repository PUBLIC intentionally.
- **F. Final Decision Content:** HR MAY set `HIRED` or `REJECTED` even when Conclusion, Expected Job, and Expected Recruitment Time are blank. Do not create a Conclusion-required invariant.
- **G. HR Candidate-data Correction:** HR may correct Candidate-entered full name, phone, date of birth, gender, and current address through a trusted Correction action (`correct_submission_candidate_fields_by_hr`) with actor, changed-field names, timestamp, Security Audit, and optional reason. Email is not changed through ordinary correction.
- **H. Candidate Email Recovery:** Root Admin OR delegated HR with specific permission (`candidates.identity_manage`) may replace a Candidate's lost old login email with a new email, preserving the same `candidate_id` and history. New email must not belong to another Candidate. Safely update/rebind verified Auth identity + Candidate account, revoke obsolete session/binding where supported, write Security Audit, preserve historical Submission `email_snapshot`, and use the new verified email for future submissions.
- **I. Historical Interviewer Access:** Interviewer may READ historical Interview rounds they personally participated in. They may not read unrelated Candidate/Interview history. Historical access is read-only. Removed/non-current participant loses access. WRITE requires target Interview is Application Current Round, participant current/eligible, and target Interview's OWN `report_status_code` writable/non-final.
- **J. Confirmed Reschedule:** `CONFIRMED` + successful schedule/room change => one atomic backend action (`reschedule_confirmed_interview`); conflict recheck + schedule mutation + status mutation occur in one transaction; on success status becomes `AWAITING`; on failure original schedule and `CONFIRMED` status remain unchanged. HR manually confirms again later.
- **K. Privacy Notice:** Strong-current semantics. Session may pin the notice presented at open, but Submit/Save re-resolves current effective published notice. If different, reject with stable code `PRIVACY_NOTICE_CHANGED`, preserve draft/session, and require acknowledgement of the current version before retry.

## Deferred owner artifact
Official EIU Interview Report pixel-perfect PDF template is **DEFERRED** until the owner supplies the approved template. Report data/logic remains current; this deferral blocks only final PDF layout/UAT, not foundation/schema work.

## External Full Review v9 (baseline Full v1.10 / DS v1.8 / Responsive v1.6)
No additional HR owner decision was required. The v1.12 package follows the already-frozen traceability priority: retained PRODUCTION exact-Submission email usage is downstream history. Therefore normal submitted Submissions are retention-managed and the old unused-Submission hard-delete command is classified MAINTENANCE_ONLY, not a normal HR production capability. PDF official layout remains deferred by prior owner decision.
