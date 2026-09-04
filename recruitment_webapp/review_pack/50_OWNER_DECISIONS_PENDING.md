# 50. Owner Decisions — Current Resolved / Deferred

**Current status (v1.17): no unresolved owner decision from the v1.16 independent implementation-readiness review.** Business Logic Core v1.2 remains FROZEN.

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

## Deferred owner artifact
Official EIU Interview Report pixel-perfect PDF template is **DEFERRED** until the owner supplies the approved template. Report data/logic remains current; this deferral blocks only final PDF layout/UAT, not foundation/schema work.

## External Full Review v9 (baseline Full v1.10 / DS v1.8 / Responsive v1.6)
No additional HR owner decision was required. The v1.12 package follows the already-frozen traceability priority: retained PRODUCTION exact-Submission email usage is downstream history. Therefore normal submitted Submissions are retention-managed and the old unused-Submission hard-delete command is classified MAINTENANCE_ONLY, not a normal HR production capability. PDF official layout remains deferred by prior owner decision.
