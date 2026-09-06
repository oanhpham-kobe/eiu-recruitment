# 99. Independent Review — Implementation Alignment v1.18

**Status:** CURRENT / NORMATIVE  
**Date:** 06/09/2026  
**Baseline:** Full Handover v1.18 + Design System v1.8 + Responsive Prototype v1.10

## Purpose
This alignment incorporates Owner Decisions A–K and closes the external review and implementation-branch stabilization findings prior to Slice 04. It does **not** reopen Business Logic Core v1.2 or change the four-gate implementation model. Technical Specification remains frozen.

## Closed findings and canonical clarifications

### 1. Owner Decisions A–K canonicalized
- **A. Interview Round / Schedule Status:** `HIRED` is terminal for future rounds. Latest relevant active Interview report_status `HIRED` => no next round. Latest active not `HIRED` => next round allowed, including when Schedule Status is `CANCELLED`. `CANCELLED` does not block a future round. Latest inactive round continues to block until Reactivate/hard-delete. Schedule Status has no mandatory sequence; direct jumps allowed. Exactly one Schedule Status per round.
- **B. Effective Outcome:** Aggregation unchanged: any active Application with Current Round `HIRED` causes Submission `DONE`; otherwise newest/highest relevant active round.
- **C. HR Permissions:** Phase 1 default Full HR permission policy plus granular revoke retained.
- **D. Candidate Reactivate:** Deliberate exception: no active Application after Candidate reactivation => Submission `READ`, not `NEW`.
- **E. Repository Visibility:** Repository remains PUBLIC intentionally.
- **F. Final Decision Content:** Blank Conclusion, Expected Job, Expected Recruitment Time allowed with `HIRED` / `REJECTED`.
- **G. HR Candidate-data Correction:** Trusted correction action `correct_submission_candidate_fields_by_hr` with actor, changed field names, timestamp, Security Audit, optional reason.
- **H. Candidate Email Recovery:** Trusted action `recover_candidate_email_identity`, permission `candidates.identity_manage` (Root implicit), unique new email, update verified Auth identity and Candidate account, preserve historical Submission `email_snapshot`.
- **I. Historical Interviewer Access:** Interviewer may READ historical Interview rounds personally participated in (read-only); WRITE requires Application Current Round, current participant, non-final/writable report_status.
- **J. Confirmed Reschedule:** Dedicated trusted action `reschedule_confirmed_interview`, atomic conflict recheck + schedule update + status reset to `AWAITING`.
- **K. Privacy Notice:** Strong-current semantics: session pins presentation version, submit/update requires current effective published version; mismatch => `PRIVACY_NOTICE_CHANGED`.

### 2. Permissions and RLS separation
- Added `applications.view` and `candidates.identity_manage`.
- Dependency: `applications.manage -> applications.view`.
- Application HR read requires Root OR `applications.view` OR `applications.manage`.
- Interview HR read requires Root OR `interviews.view` OR `interviews.manage`.
- Neither table uses `submissions.view` as a substitute read permission.

### 3. Candidate field ownership and validation bounds
- Candidate-owned fields: `full_name` (<=200), `phone` (<=32 normalized), `date_of_birth` (1900-01-01..today), `gender` (MALE/FEMALE), `current_address` (<=500), Education child rows, Candidate documents.
- Verified email is immutable from Auth.
- HR-only fields (`other_info`, `hr_note`, experiences, activities) are not accepted or cleared by Candidate Submit/Edit.
- Education child model aligns with physical schema: `period_text`, `qualification_id`, `major`, `institution`, `sort_order`.

### 4. Detail read vs explicit open
- `get_submission_detail()` is a pure read and never mutates `NEW -> READ`.
- `open_submission()` is the explicit user-intent command that executes `NEW -> READ` when authorized.

### 5. Authoritative Application outcome resolver
- Current Round is the highest `round_no` among access-active Interviews for that Application.
- Current Round `HIRED` => `HIRED`; `REJECTED` => `REJECTED`; otherwise `IN_PROGRESS`.
- Single internal resolver shared by Submission recalculation and Candidate reactivation.
- Internal helper `recalculate_submission_status(uuid)` has deny-by-default execution ACL.

### 6. Document materialization and portal security
- Candidate document ADD creates a new logical header; no `UNIQUE(submission_id, document_type_id)` constraint.
- Server derives one-based `sort_order` (1..n).
- Privacy acknowledgement table physical identity: `(submission_id, notice_version)`.
- Server route boundary `/candidate/*` redirects unauthenticated users to `/auth/candidate`.
- Upload UI follows authoritative reservation protocol.
- Draft autosave uses `sessionStorage` with Form Session ID binding and expiry cleanup.
- Strict CSP without `unsafe-inline`.

### 7. Integration CI and email safety
- Database-enabled Integration CI gate executes zero-base migration replay, schema smoke, RLS persona checks, Candidate Submit/Update and document protocol tests.
- Non-production Outbox environment defaults to `TEST`.

## Freeze consequence
Technical Architecture v1.18 remains **TECHNICAL SPECIFICATION FROZEN**. Source-level Implementation Gate remains **READY TO IMPLEMENT**. Gate 3 still requires actual post-code migration/RLS/RPC/race/storage/performance/backup/deployment evidence. Production Ready remains **NO**.
