# EIU Recruitment Web App — Full Review Report
## Baseline: Full Handover v1.10 + Design System v1.8 + Responsive Prototype v1.6

**Ngày review:** 03/09/2026  
**Source of truth duy nhất:** `App_Tuyen_Dung_EIU_Full_Handover_v1.10.zip`  
**SHA-256:** `7fbeb21a1d58a220f4e40f30cda2a3a0ae6f88eb7bcc4bb74bce4cfc24346759`

> Các version cũ không được dùng để suy ra trạng thái hiện tại. ECC / Superpowers / Matt Pocock / ByteByteGo chỉ được dùng như review lenses, không override source-of-truth EIU.

---

# 1. Executive Summary

Fresh validation trên đúng bundle hiện tại:

- **Full Handover:** `363/363 PASS`
- **Design System v1.8:** `72/72 PASS`
- **Responsive Prototype v1.6:** `47/47 PASS`

v1.10 đã sửa đúng phần lớn semantic mismatch lớn của v1.9: Candidate lifecycle tách khỏi Submission workflow; parent Candidate derive latest Submission; prototype chỉ cho manual NEW/READ; Report Status nằm trên Current Interview; Application Outcome derive riêng; Final Decision Source dùng `decisionUpdatedAt`; aggregate HR Report không còn generic Delete; staged Candidate documents/CV-required flow đã có; active-master/document/privacy/participant guards đã được harden; production Email trace đã block hard-delete Submission; critical-control registry đã có.

Tuy nhiên, manual cross-layer review vẫn phát hiện **2 P0** và một nhóm **P1** mà validator hiện chưa bắt. Tôi chưa khuyến nghị `Technical Architecture v1.10 = FROZEN` trước khi đóng P0.

| Layer | Đề nghị |
|---|---|
| Business Logic Core v1.2 | **Giữ FROZEN** |
| Design System v1.8 | **CURRENT / REVIEWED** |
| Responsive Prototype v1.6 | **READY FOR OWNER VISUAL UAT / NOT FROZEN** |
| Technical Architecture v1.10 | **TARGETED AMENDMENT REQUIRED / NOT FROZEN** |
| Implementation Gate | **NOT YET PASS** |
| Production Ready | **NO** |

---

# 2. Findings Summary

## P0 — sửa trước Technical Freeze

| ID | Finding |
|---|---|
| **P0-01** | Bulk Interview Schedule Status dùng `interviews.manage` trong machine registry/coverage thay vì `interviews.status`, tạo alternate permission path |
| **P0-02** | `app_spec.yaml` vẫn có root `version: '1.9'` và legacy `bulk_semantics.mark_submission_new` dù current là v1.10 và command legacy đã bị loại |

## P1 — sửa trước implementation freeze / Owner UAT

| ID | Finding |
|---|---|
| P1-01 | Candidate Form Session / Upload Reservation có `expires_at` nhưng stage/save/finalize chưa enforce expiry synchronously |
| P1-02 | `open_submission` registry không encode conditional NEW→READ mutation + conditional `submissions.status` |
| P1-03 | Single vs bulk manual Submission status khác nhau khi Candidate Inactive |
| P1-04 | Responsive Candidate Education tự bắt buộc ít nhất 1 row + 4 fields required, trong khi source chưa freeze requiredness |
| P1-05 | NEW privacy acknowledgement checkbox đang pre-checked trong prototype |
| P1-06 | Candidate Form còn “Xác nhận thông tin cung cấp” nhưng Design/DB chỉ model Privacy acknowledgement |
| P1-07 | Một số current source/version pointers còn drift nhỏ |
| P1-08 | `save_interviewer_report` registry dùng pseudo-permission `reports.edit_interviewer/context` thay vì machine-readable OR authorization |
| P1-09 | Form Session expiry/lifecycle transitions chưa đủ deterministic |

---

# 3. P0-01 — Bulk Interview Schedule Status dùng sai permission

Permission catalog cố ý tách:

```text
interviews.manage
= Create/Edit/Copy/Delete-or-inactive Session

interviews.status
= Change Interview Schedule Status
```

Single command đúng:

```text
change_interview_schedule_status
permission = interviews.status
```

Nhưng batch command hiện tại trong `command_registry.yaml`:

```text
bulk_change_interview_schedule_status
permission = interviews.manage
writes = interviews.schedule_status_code
```

`55_COMMAND_COVERAGE_MATRIX.md` cũng ghi `interviews.manage`, trong khi `37_BACKEND_COMMAND_CONTRACTS.md` lại nói đúng bằng prose: “Requires Interview schedule-status permission”.

## Impact

HR Limited có thể có:

```text
interviews.manage = granted
interviews.status = revoked
```

Theo granular model, user đó không được đổi Schedule Status. Nhưng nếu backend derive authorization từ registry/coverage, batch endpoint có thể cho phép đổi status và bypass permission revoke.

## Fix

Canonical cho cả single + batch:

```text
interviews.status
+ prerequisite interviews.view
```

Sửa:

- `command_registry.yaml`
- `55_COMMAND_COVERAGE_MATRIX.md`
- generated policy/handler metadata nếu có
- acceptance tests

Nên tách row `Manage Interview` trong `permissions_matrix.csv` thành `Manage Interview` và `Change Interview Status` để không che granular distinction.

### Acceptance mới

```text
AC-PERM-INT-STATUS-01
interviews.manage without interviews.status → single status change FORBIDDEN.

AC-PERM-INT-STATUS-02
interviews.manage without interviews.status → bulk status change FORBIDDEN.

AC-PERM-INT-STATUS-03
interviews.status + interviews.view → single/bulk authorization equivalent.
```

**Severity: P0 / security authorization.**

---

# 4. P0-02 — `app_spec.yaml` còn stale machine-readable semantics

Đầu file đúng:

```yaml
product.document_version: '1.10'
technical_architecture.version: '1.10'
```

Nhưng gần cuối vẫn có:

```yaml
version: '1.9'
```

Cùng file còn legacy:

```yaml
bulk_semantics:
  mark_submission_new: ALL_OR_NOTHING
```

trong khi current architecture đã chốt:

```text
legacy bulk_mark_submission_new → removed/superseded
current writer → bulk_set_latest_submission_manual_status
```

Phía dưới `app_spec.yaml` lại có current:

```yaml
batch_operations:
  submission_manual_status: bulk_set_latest_submission_manual_status ...
```

Tức một structured CURRENT source chứa cả legacy lẫn current semantic.

## Fix

1. Đổi/bỏ root `version` để chỉ còn canonical v1.10.
2. Remove `bulk_semantics.mark_submission_new`, hoặc đổi thành `submission_manual_status`.
3. Validator fail nếu:
   - active version fields không coherent;
   - forbidden legacy command/semantic key còn tồn tại.
4. Có thể bổ sung current alignment flag cho Review/Alignment v1.10.

**Severity: P0 vì `app_spec.yaml` là machine-readable current source.**

---

# 5. P1-01 — `expires_at` chưa phải authoritative lifecycle gate

Schema có:

```text
candidate_form_sessions.status = OPEN/SUBMITTED/CANCELLED/EXPIRED
candidate_form_sessions.expires_at

upload_reservations.status = RESERVED/UPLOADED/VALIDATED/.../EXPIRED
upload_reservations.expires_at
```

Nhưng `validate_candidate_form_document_change()` và `validate_candidate_form_document_plan()` hiện kiểm `status=OPEN`, upload status/malware/size, **không kiểm `expires_at > transaction_now`**.

Cleanup worker là async. Vì vậy có cửa sổ:

```text
expires_at đã qua
nhưng status vẫn OPEN / VALIDATED
→ stage/save/finalize vẫn có thể pass trước khi cleanup chạy
```

## Fix

Stage/Save/Submit/Finalize phải recheck synchronous:

```text
form_session.status = OPEN
AND form_session.expires_at > transaction_now
```

và cho ADD/REPLACE:

```text
reservation.status = VALIDATED
AND malware = CLEAN
AND reservation.expires_at > transaction_now
```

Stable errors:

```text
FORM_SESSION_EXPIRED
UPLOAD_RESERVATION_EXPIRED
```

Cleanup worker chỉ housekeeping, không quyết định business validity.

---

# 6. P1-02 — `open_submission` registry thiếu conditional mutation metadata

Contract đúng:

```text
requires submissions.view
if actor also has submissions.status AND state=NEW → NEW→READ
otherwise pure read
```

Coverage Matrix cũng phân biệt view-only vs status-capable HR.

Nhưng registry hiện:

```yaml
permission: submissions.view
side_effects: []
writes: []
```

Nếu agent/tool dùng Registry làm authority thì có thể implement sai mutation hoặc authorization.

## Fix

Encode machine-readable conditional branch, ví dụ:

```yaml
base_permission: submissions.view
conditional_mutation:
  when: status == NEW
  permission: submissions.status
  writes: [submissions.status_code]
  transition: NEW_TO_READ
```

---

# 7. P1-03 — Single vs bulk manual status khác nhau khi Candidate Inactive

Single writer:

```text
set_submission_manual_status()
→ NEW/READ only
→ no active Application
```

không nói Candidate phải Active.

Bulk writer:

```text
bulk_set_latest_submission_manual_status()
→ Candidate Inactive OR active Application rejects whole batch
```

Current business source nói Candidate Inactive khóa portal nhưng internal historical/recruitment data vẫn tồn tại và HR vẫn làm việc nội bộ. Vì vậy batch-only restriction cần được owner/contract chốt.

## Chọn một rule

- **Option A:** Single + bulk đều cho NEW/READ nếu không active Application, dù Candidate inactive.
- **Option B:** Single + bulk đều reject Candidate inactive.

Không nên có batch-only special rule.

---

# 8. P1-04 — Prototype tự tạo requiredness cho Education

Business Candidate Form ghi Education là repeatable và liệt kê:

- Thời gian
- Học vấn
- Chuyên ngành
- Trường

Nhưng **không freeze requiredness** cho các field này. `validation_contract.yaml` chỉ có:

```text
education_rows.max_items = 20
```

không có `min_items` hay required fields.

Responsive v1.6 lại render:

```text
Thời gian *
Học vấn *
Chuyên ngành *
Trường *
```

và HTML `required` cho cả 4; retained interaction còn không cho remove Education row cuối.

## Fix

- Nếu Education thực sự required: update Business + Validation Contract + DTO + Acceptance.
- Nếu chưa chốt: bỏ `*`, `required`, và minimum-one behavior khỏi prototype.

Prototype/UAT không nên tự tạo business validation rule.

---

# 9. P1-05 — Privacy acknowledgement trong NEW form đang pre-checked

Responsive v1.6 hiện:

```html
<input id="privacyAck" type="checkbox" checked required>
```

Source yêu cầu Candidate phải acknowledge server-pinned Privacy Notice. Với NEW Submission, checkbox đã checked ngay khi mở form khiến required state được thỏa trước khi Candidate thao tác.

## Khuyến nghị

### NEW_SUBMISSION

```text
unchecked by default
```

### EDIT_SUBMISSION

- same version already acknowledged: có thể render satisfied theo Design source;
- new pinned version: unchecked và yêu cầu acknowledgement mới.

Điều này làm Owner UAT kiểm được interaction thật, không chỉ presence.

---

# 10. P1-06 — “Xác nhận thông tin cung cấp” chưa được reconcile

`03_CANDIDATE_FORM_AND_PORTAL.md` section D có:

```text
- Xác nhận thông tin cung cấp.
- Đồng ý sử dụng thông tin cho mục đích tuyển dụng.
```

Nhưng current Design/DB/command model chỉ có explicit `PrivacyNoticeAcknowledgement`. Không thấy separate accuracy-attestation field/DB record/validation.

## Cần chọn

- Nếu chỉ Privacy acknowledgement là required interaction: sửa wording “Xác nhận thông tin cung cấp” để không ngụ ý checkbox/attestation thứ hai.
- Nếu Candidate phải attest accuracy riêng: thêm model + validation + audit rõ.

Current architecture thiên về phương án đầu.

---

# 11. P1-07 — Một số source metadata/pointers còn drift nhỏ

Phần lớn source governance v1.10 đã tốt, nhưng còn:

## `01_PRODUCT_SCOPE_AND_ARCHITECTURE.md`

CURRENT/NORMATIVE nhưng còn câu:

```text
v1.8 is an implementation-contract review package
```

Nếu là historical statement cần label; nếu mô tả current package thì đổi v1.10.

## `database_schema.sql`

Header ghi:

```text
Production requires ... docs 37–82
```

Current source đã có 83/84. Nên reference:

```text
CURRENT/NORMATIVE entries in source_registry.yaml + current gate
```

thay vì hard-code range.

## `START_HERE.txt`

Ghi Technical v1.10:

```text
READY FOR OWNER VISUAL UAT
```

nhưng README/Gate 84 nói Technical:

```text
READY FOR FRESH EXTERNAL RE-REVIEW
```

Owner Visual UAT là gate của Responsive Prototype, không phải Technical Architecture.

---

# 12. P1-08 — `save_interviewer_report` registry dùng pseudo-permission

Registry hiện:

```yaml
actor: participant_or_authorized_hr
permission: reports.edit_interviewer/context
```

Đây không phải permission code thật.

Authorization thực tế có hai nhánh:

### Interviewer

```text
current participant + contextual access + own report
```

### HR

```text
reports.view + reports.edit_interviewer
```

Nếu registry sẽ feed implementation, nên encode OR-authorization machine-readable thay vì một string shorthand.

---

# 13. P1-09 — Form Session lifecycle nên freeze transitions

Ngoài expiry check, nên có canonical state transition table:

```text
OPEN → SUBMITTED
OPEN → CANCELLED
OPEN → EXPIRED
```

và quy định:

- actor/worker nào được transition;
- expired session không reopen;
- expiry của reservation vs Form Session;
- cleanup ordering;
- status transition audit/updated_at.

Điều này làm Storage cleanup và concurrency deterministic hơn.

---

# 14. Design System v1.8 Review

**72/72 PASS.** Không phát hiện blocker visual mới.

Đang tốt:

- table widths ổn định;
- Drawer rule nhất quán;
- exact SubmissionSelector;
- Candidate EDIT Privacy;
- Users/Permissions persona visibility;
- semantic controls;
- 16px operational text;
- keyboard/focus;
- target-size/reflow requirements;
- sticky table context;
- status không chỉ dựa màu;
- release evidence boundary rõ.

Không đề nghị redesign Design System.

---

# 15. Responsive Prototype v1.6 Review

**47/47 PASS.** v1.6 đã sửa phần lớn mismatch của v1.5.

Đã verify tốt:

- Candidate lifecycle separate;
- latest Submission parent summary;
- manual NEW/READ only;
- Phase-1 navigation;
- Current Interview Report Status;
- decision-specific timestamp;
- aggregate HR Report no Delete;
- staged ADD/REPLACE/DELETE;
- CV-required flow;
- status menu anchor/outside/Escape/focus restoration.

Trước Owner UAT chính thức, nên sửa:

1. Education requiredness;
2. NEW Privacy checkbox pre-check;
3. accuracy-confirmation wording/behavior.

---

# 16. Validator Improvements

Nên bổ sung các check sau:

### V-01 — Batch permission parity

```text
single writer permission == batch writer permission
```

cho cùng protected field.

### V-02 — app_spec version coherence

Check mọi active version field và source registry.

### V-03 — Forbidden legacy structured keys

Fail `bulk_semantics.mark_submission_new` khi command đã superseded.

### V-04 — Expiry authority

Expired OPEN session / VALIDATED reservation phải fail stage/save/finalize.

### V-05 — Conditional command metadata

`open_submission` phải encode conditional write/permission.

### V-06 — Single/batch parity

Cùng logical mutation không được có Candidate-Inactive rule khác nhau.

### V-07 — Prototype requiredness conformance

Prototype required fields/min-items phải match Validation Contract.

### V-08 — NEW Privacy default state

NEW acknowledgement không được auto-satisfied trừ khi owner freeze khác.

### V-09 — Current gate wording

`START_HERE` Technical status phải match Gate 84.

---

# 17. Recommended Fix Order

## Batch 1 — Blockers

1. `bulk_change_interview_schedule_status` → `interviews.status`.
2. Fix Coverage Matrix + authorization acceptance.
3. `app_spec.yaml` root version → v1.10.
4. Remove legacy `mark_submission_new` structured semantic.

## Batch 2 — Session / machine contract

5. Enforce Form Session expiry.
6. Enforce Upload Reservation expiry.
7. Encode `open_submission` conditional mutation in Registry.
8. Normalize `save_interviewer_report` authorization metadata.
9. Freeze Candidate-Inactive manual-status parity.

## Batch 3 — Prototype/UAT

10. Freeze Education requiredness and align prototype.
11. NEW privacy checkbox default unchecked.
12. Reconcile accuracy confirmation vs Privacy acknowledgement.

## Batch 4 — Source cleanup

13. Fix Product Scope v1.8 sentence.
14. Replace schema `37–82` pointer with source registry.
15. Fix START_HERE Technical vs Visual-UAT status.
16. Extend validator V-01…V-09.

---

# 18. Proposed Gate Status

```text
Business Logic Core v1.2 = FROZEN
Design System v1.8 = CURRENT / REVIEWED
Responsive Prototype v1.6 = READY FOR OWNER VISUAL UAT / NOT FROZEN
Technical Architecture v1.10 = REVIEWED / TARGETED AMENDMENT REQUIRED / NOT FROZEN
Implementation Gate = NOT YET PASS
Production Ready = NO
```

---

# 19. Final Assessment

v1.10 **rất gần Technical Freeze** và không cần redesign architecture chính:

```text
Candidate → Submission → Application → Interview → Participant → Report
```

Hai việc quan trọng nhất còn lại là:

1. **permission parity giữa single/batch writers** — không được có alternate path bypass granular revoke;
2. **machine-readable current sources phải thật sự authoritative** — không còn version/legacy key superseded.

Sau đó, phần còn lại chủ yếu là lifecycle hardening và Owner-UAT interaction details.

Tiêu chuẩn trước Technical Freeze:

> Mỗi protected mutable field phải có một authorization model duy nhất xuyên suốt:  
> **Permission → single command → batch command → registry → SQL/RLS → acceptance.**

v1.10 đã đạt phần lớn điều kiện này.

---

# Appendix — Fresh Evidence

```text
Full Handover v1.10: 363/363 PASS
Design System v1.8: 72/72 PASS
Responsive Prototype v1.6: 47/47 PASS
```
