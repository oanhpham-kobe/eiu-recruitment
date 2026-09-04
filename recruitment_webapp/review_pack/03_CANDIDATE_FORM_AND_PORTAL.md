# 03. Candidate Form & Candidate Portal

## 1. Nguyên tắc form

- Một form duy nhất trên một page.
- Không chia Step/Next.
- Chỉ dùng tiêu đề/section để phân nhóm thông tin.
- Candidate scroll xuống và Submit một lần.
- Không hỏi “Đã từng ứng tuyển EIU chưa?”.
- Mỗi lần submit luôn tạo một Submission mới.
- Candidate đăng nhập bằng **Email OTP**; verified email là identity/matching key, không phải DB PK.
- Email được hệ thống lấy từ Auth và không được Candidate/HR sửa trong hồ sơ.

## 2. Thông tin hiển thị trong form

### A. Thông tin chung (General Information)

| Field | Kiểu nhập đề xuất | Required hiện tại |
|---|---|---:|
| Họ tên | Text | ✅ |
| Ngày sinh | Date picker | ✅ |
| Giới tính | Dropdown: Nam / Nữ | ✅ |
| Địa chỉ hiện tại | Text | ✅ |
| Email | Read-only, auto từ Auth | ✅ |
| Số điện thoại | Text/Phone | ✅ |

### B. Thông tin chi tiết (Details)

#### 1. Quá trình học tập (Education)
Cho phép nhiều record.

| Field | Kiểu nhập |
|---|---|
| Thời gian | Khoảng thời gian / Year range |
| Học vấn | Searchable dropdown từ Danh mục |
| Chuyên ngành | Text |
| Trường | Text |

Nút: `+ Thêm quá trình học tập`. Phase 1 hiện **không bắt buộc tối thiểu 1 dòng Education và không đánh dấu 4 field Education là required**; nếu sau này đổi requiredness phải cập nhật Validation Contract/DTO/Acceptance trước khi đổi prototype.

### C. Hồ sơ đính kèm

Hỗ trợ:
- **CV/Resume — required**.
- Bằng cấp — optional.
- Bảng điểm — optional.
- Chứng chỉ — optional.
- Tài liệu khác — optional.

Upload policy Phase 1:
- PDF, DOC/DOCX, PPT/PPTX, PNG/JPG/JPEG;
- tối đa **5 current files / Submission**;
- tối đa **5 MB/file**;
- backend validate type/size và versioning, không chỉ dựa vào frontend.

### D. Xác nhận quyền riêng tư
- Candidate đọc server-pinned Privacy Notice và thực hiện **một Privacy acknowledgement** theo version được pin.
- Không có accuracy-attestation checkbox/DB record thứ hai trong Phase 1.
- NEW_SUBMISSION: acknowledgement **unchecked by default**; Candidate phải chủ động chọn trước Submit.
- EDIT_SUBMISSION: nếu exact pinned notice version đã được acknowledge cho Submission/version tương ứng thì UI có thể render satisfied; notice version mới phải yêu cầu acknowledgement mới.
- Submit.

## 3. Các section KHÔNG hiển thị cho Candidate

Vẫn có schema trong hệ thống nhưng chỉ HR thấy và edit:

### Working Experiences
- Thời gian bắt đầu.
- Thời gian kết thúc.
- Đang làm việc tại đây.
- Đơn vị công tác.
- Chức danh.
- Nội dung công việc / Kinh nghiệm chính.

### Activities to Participate in
- Thời gian.
- Tên hoạt động.
- Vai trò.
- Đơn vị tổ chức.
- Mô tả / Thành tích.

### Other
- Textarea thông tin khác.

Các trường này nên lưu theo Submission để bảo toàn snapshot của từng lần ứng tuyển.

## 4. Submit logic

```text
Candidate Login bằng Email OTP
  ↓
Trusted provisioning command find/create Candidate + bind Auth identity
  ↓
Candidate Submit
  ↓
Create submission_id
  ↓
Email snapshot lấy từ verified Auth identity
  ↓
Link Submission vào Candidate đã provision
```

Không overwrite Submission trước.

## 5. Candidate Portal – Phiếu của tôi

### Nếu chưa từng submit
- Mặc định hiển thị form Đăng ký mới.

### Nếu đã từng submit
Hiển thị 2 lựa chọn:
- `Đăng ký mới`
- `Phiếu của tôi`

### Danh sách Phiếu của tôi

| STT | Time stamp / Ngày ứng tuyển | Trạng thái |
|---:|---|---|

Candidate chỉ thấy 3 trạng thái:
- **Mới**
- **Đang xử lý**
- **Hoàn thành**

### Quyền edit
- Mới → được Edit.
- Đang xử lý → không được Edit.
- Hoàn thành → không được Edit.

Nếu cần sửa khi không còn trạng thái Mới:
- Candidate liên hệ HR.
- HR phải đưa phiếu về trạng thái phù hợp cho phép sửa.

## 6. Candidate edit

- Candidate mở phiếu → `Edit` toàn bộ form **trừ Email**.
- Không edit từng section riêng.
- Save cập nhật Submission tương ứng.
- EDIT session cũng hiển thị Privacy Notice version do server pin. Candidate phải acknowledge version đó trước Save; nếu Submission đã acknowledge cùng version thì thao tác là idempotent, nếu version mới thì ghi thêm acknowledgement mới.
- HR Application Inbox thấy dữ liệu mới ngay.
- `updated_at` và Activity Log cập nhật.
- Gửi email thông báo HR sau mỗi lần Candidate tạo mới hoặc chỉnh sửa.

## 7. File replacement

Candidate upload file mới:
- UI dùng version mới làm current file;
- backend giữ `logical_document_id` và tăng `version_no`; version cũ chuyển `is_current=false`;
- upload dùng reserve/finalize two-phase protocol để tránh orphan/mất metadata.

## 8. Candidate-facing status mapping

Candidate chỉ thấy 3 trạng thái khi tài khoản đang Active:
- `NEW` → **Mới**.
- `READ`, `PROCESSED` → **Đang xử lý**.
- `DONE`, `CLOSED` → **Hoàn thành**.

### Candidate Inactive

`Inactive` là **manual override ở cấp Candidate/account theo email**, không phải thao tác xóa Submission. Khi HR Inactive Candidate:
- Candidate không đăng nhập được vào Candidate Portal bằng email đó.
- Candidate không xem được `Phiếu của tôi` và không tạo/chỉnh phiếu mới trong portal cho tới khi HR Active lại.
- Về mặt mapping nghiệp vụ, Inactive được xem là **Hoàn thành**, nhưng Candidate thực tế không nhìn thấy trạng thái này vì tài khoản đang bị khóa.
- Tất cả Submission/Application/Interview/Report cũ vẫn được giữ nguyên cho HR.

Khi HR Active lại Candidate, hệ thống tính lại trạng thái từng Submission theo Application hiện có:
- Có ít nhất một Application = `HIRED` → `DONE`.
- Tất cả Application = `REJECTED` → `CLOSED`.
- Có Application đang xử lý → `PROCESSED`.
- Không còn active Application → `READ`; HR có thể Mark New nếu muốn Candidate sửa.

## Candidate Form transaction model
- Opening a new form creates a short-lived Candidate Form Session, **not** a Submission.
- Files upload to temp/quarantine under that session.
- Submit atomically creates Submission + children + privacy acknowledgement + CLEAN document versions + HR notification.
- Editing a NEW Submission also uses a Form Session. File add/replace/delete is staged; Save applies text and file changes together, Cancel applies neither.
- Save/finalize re-checks Candidate Active + Submission still NEW because HR may have opened it during the edit/upload.
- Final Privacy section is required: localized notice, notice version, details link/view, required acknowledgement and validation.
- Candidate current profile is sourced from latest submitted snapshot; editing an older NEW Submission does not replace current profile if a newer Submission exists.

## Candidate reactivation lifecycle exception
Candidate reactivation is an explicit HR lifecycle action and has one deliberate exception to generic status recalculation:
- If at least one active Application is `HIRED` → `DONE`.
- If all active/effective Applications are `REJECTED` → `CLOSED`.
- If any active Application remains in progress → `PROCESSED`.
- If there is **no active Application** → force the Submission to `READ`, including a Submission that was `NEW` before Candidate inactivation.

Rationale: reactivation is an HR-controlled recovery step. Candidate editing must not silently resume after HR has deliberately re-enabled the account. HR may explicitly `Mark New` afterwards if Candidate editing should reopen.


## Candidate edit privacy and current-profile refresh
- Every NEW_SUBMISSION and EDIT_SUBMISSION Form Session pins one authoritative current/effective Privacy Notice version.
- Candidate EDIT Save requires acknowledgement of the pinned version. Same-version acknowledgement is reused idempotently; a new presented version creates a new acknowledgement for the same Submission.
- Successful Candidate Update includes exact-Submission HR notification in the same business transaction before commit.
- Candidate current-profile cache reflects the latest surviving submitted snapshot. Latest Candidate/HR edit refreshes it; older edits do not; MAINTENANCE_ONLY repair-delete of a non-production/legacy latest Submission falls back to the next latest snapshot.

## Candidate inactive metadata
`is_active=false` sets `inactive_at` and `inactive_by`; reactivation clears both fields. Full lifecycle history remains in immutable Security Audit. These physical fields describe the **current inactive state**, not the last historical inactivation after reactivation.
