# 15. ALL-IN-ONE SPEC — GENERATED v1.17

> DO NOT EDIT MANUALLY. Generated deterministically from CURRENT normative numbered modules listed in `source_registry.yaml`.
> HISTORICAL/SUPERSEDED review and gate documents are excluded from the normative body.
> Regenerate after source changes; validation fails on byte drift.


---

<!-- SOURCE: 00_README.md -->

# App Tuyển dụng EIU — Full Handover v1.17

**Ngày cập nhật:** 03/09/2026  
**Business Logic Core:** v1.2 **FROZEN**  
**Design System:** v1.8 **CURRENT** — included in combined review bundle and supplied separately  
**Technical Architecture:** v1.17 **TECHNICAL SPECIFICATION FROZEN**  
**Production Ready:** **NO**

## 1. Mục đích của v1.17
v1.17 giữ nguyên Business Logic Core, four-gate implementation model và executable Responsive Prototype v1.10; đóng independent review của v1.16 bằng cách propagate `copy_interview_schedule` vào mọi canonical schedule-engine declaration, bổ sung stable Copy browser-QA evidence, làm sạch generated All-in-One labeling và pin lại current source/gate. Technical Architecture v1.17 vẫn TECHNICAL SPECIFICATION FROZEN; Implementation Gate = READY TO IMPLEMENT; Production Ready = NO.

## 2. Business đã chốt
- `Candidate → Submission → Application → Interview Session (1..N) → Participant → Report`.
- Application cố định theo `Submission + Khoa/Phòng + Ngành/Tổ + Vị trí`; tổ hợp khác = Application khác.
- Application selector luôn xác định **Submission cụ thể**, backend không tự chọn latest.
- Current Round = `access_active` Interview có `round_no` lớn nhất; chỉ dùng cho Report/Outcome/PDF, không giới hạn resource blocking.
- Page Báo cáo/Preview dùng Current Round; vòng cũ giữ lịch sử.
- Demo Topic thuộc Interview Session; vòng mới để trống.
- Không scoring/rating.
- Candidate chỉ edit khi `NEW`; HR mặc định mở `NEW → READ`. View-only HR không mutation.
- Candidate conflict / Room conflict / Interviewer conflict = **BLOCK**.
- Candidate Auth = **Email OTP**; Internal User = Google Workspace OAuth `@eiu.edu.vn`.
- Root Admin duy nhất. HR mặc định nhận **Full HR Permission Set**, Root có thể revoke granular rights.
- Delete unused → hard delete; used → inactive. Empty auto-created Round 1 chưa được coi là business history.
- Upload: PDF, DOC/DOCX, PPT/PPTX, PNG/JPG/JPEG; max 5 files/Submission or Interview; max 5 MB/file.
- Current retention business policy: no automatic purge; cảnh báo dung lượng, sau đó EIU chọn tăng dung lượng hoặc export/archive local + explicit purge.
- Official PDF pixel template intentionally deferred until owner provides approved source.

## 3. Final Decision
Thông thường 01 Interviewer đại diện nhập 3 final fields sau khi hội đồng thống nhất. Nếu người khác sửa một trong 3 field, đó là revision mới sau trao đổi.

`decision_updated_at/by` chỉ thay đổi khi một trong 3 final fields thay đổi. Sửa 5 qualitative fields không làm đổi Final Decision Source. Cả 3 final fields luôn lấy từ cùng một report.

## 4. Technical architecture hardening
- Application derive Candidate through Submission; no duplicate `candidate_id`.
- Null-safe Unit/Team/Position invariant.
- Interview Report belongs to Participant.
- Separate `interview_note` and HR-only `hr_report_note`.
- `access_active` Interview = active Application AND active Interview; `resource_blocking` thêm non-CANCELLED + interval.
- Mandatory transaction resource locks + conflict recheck for all schedule-activating mutations.
- Candidate first-login atomic provisioning/safe Auth rebind.
- Candidate/HR separate writable DTOs.
- Physical Phase-1 master data tables/FKs.
- Logical document versioning + private two-phase upload.
- Email outbox with leased worker and at-least-once/best-effort dedup semantics.
- Privacy notice acknowledgement versioning.
- RLS + explicit grants + private/security-invoker view rules.
- Root-only bound identity rebind; directory manager may only correct unbound email typo.
- Measurable NFR baseline and search/indexing strategy.
- Fail-closed consistency validation.

## 5. Design System v1.8 + Responsive Prototype v1.10
Current visual/interaction source-of-truth is the separate **EIU Recruitment Design System v1.8** ZIP. It preserves the v1.5 table/accessibility/security rules and adds explicit Candidate EDIT Privacy semantics plus measurable zoom/reflow/release evidence requirements.

Responsive Prototype v1.10 is bundled for desktop/tablet/mobile visual UAT against Design System v1.8. Responsive UI remains NOT FROZEN until owner visual UAT; Candidate Portal mobile remains a go-live requirement.

## 6. Cách đọc
### Reviewer tổng quát
1. `FINAL_REVIEW_GUIDE.md`
2. `97_INDEPENDENT_REVIEW_IMPLEMENTATION_ALIGNMENT_V1_17.md`
3. `73_DOMAIN_GLOSSARY_AND_CANONICAL_PREDICATES.md`
4. `78_PRIVACY_NOTICE_PUBLICATION_RUNBOOK.md`
5. `70_SEMANTIC_VALIDATION_GATE.md`
6. `98_TECHNICAL_PRECODE_GATE_V1_17.md`
7. `75_RELEASE_EVIDENCE_MATRIX.md`
8. `81_RESPONSIVE_PROTOTYPE_INTEGRATION.md`
8. `15_ALL_IN_ONE_SPEC.md` — generated from CURRENT normative sources only
9. Design System v1.8 ZIP

### Architect / Developer
Đọc thêm all CURRENT/NORMATIVE technical entries theo `source_registry.yaml`, cùng `database_schema.sql`, `app_spec.yaml`, `command_registry.yaml`, `validation_contract.yaml`.

## 7. Owner decisions status
`50_OWNER_DECISIONS_PENDING.md` is retained for continuity but now records **RESOLVED / DEFERRED**, not five unresolved items. Only official PDF pixel layout is deferred. Legal/privacy confirmation remains a go-live responsibility, not an unresolved HR workflow decision.

## 8. Machine-readable / starter artifacts
- `database_schema.sql` — implementation starter, not production migration bundle.
- `app_spec.yaml` — structured current spec.
- `seed_master_data.json`.
- `permissions_matrix.csv`, `status_mapping.csv`, `technical_review_matrix.csv`.
- `PACKAGE_VALIDATION.txt` — fail-closed consistency results.
- `tools/validate_package.py` — inspectable/re-runnable package validator; Design ZIP includes its own `tools/validate_design.py`.

## 9. Gate status
See `52_TECHNICAL_GATE_STATUS.md` and `98_TECHNICAL_PRECODE_GATE_V1_17.md`.

Business/Technical Specification Freeze does not mean Implementation Validation or Production Ready. Real migration/RLS/RPC/race/storage/performance/backup/deployment evidence is a post-coding gate.


## Historical review notes
Prior v1.5/v1.6 review/gate documents are retained as HISTORICAL/SUPERSEDED in `source_registry.yaml` and are not current source-of-truth.

> `LEGACY_LAYOUT_REFERENCE_ONLY_interview_report_excerpt.png` is layout inspiration only. Its field labels are legacy and must not override current report fields.




## Current review path — v1.17
Use `source_registry.yaml` as the authority. Current alignment = `97_INDEPENDENT_REVIEW_IMPLEMENTATION_ALIGNMENT_V1_17.md`; current gate = `98_TECHNICAL_PRECODE_GATE_V1_17.md`. Historical review/gate files never override current behavior. Responsive Prototype v1.10 remains the executable visual-UAT reference for Design System v1.8.

Current numbered technical/review modules extend through doc 96. `source_registry.yaml` remains the authority; do not infer current status from numeric range alone.

Current alignment resolution: `97_INDEPENDENT_REVIEW_IMPLEMENTATION_ALIGNMENT_V1_17.md`; current pre-code/implementation gate: `98_TECHNICAL_PRECODE_GATE_V1_17.md`. Independent Review of Full Handover v1.16 is the latest external source-readiness evidence; doc 97 records its alignment.



---

<!-- SOURCE: 01_PRODUCT_SCOPE_AND_ARCHITECTURE.md -->

# 01. Product Scope & Architecture

## 1. Mục tiêu

Xây dựng web app tuyển dụng nội bộ giúp HR xử lý hồ sơ từ lúc ứng viên tạo phiếu đến Interview và Báo cáo phỏng vấn mà không phải vừa thao tác ngoài hệ thống vừa nhập lại AppSheet.

Nguyên tắc:
> **Thiết kế xoay quanh hành động của HR; KPI/tracking là đầu ra của hành động.**

## 2. Kiến trúc nghiệp vụ cốt lõi

```text
Candidate
  └── Submission (Phiếu ứng tuyển)
        └── Application
              ├── Interview Session - Vòng 1
              │     ├── Participants
              │     ├── Interview Documents
              │     ├── Email History
              │     └── Interview Reports (1 người = 1 report)
              ├── Interview Session - Vòng 2
              └── Interview Session - Vòng N
```

### Candidate
Một tài khoản ứng viên theo verified email.

### Submission
Mỗi lần Candidate gửi form là một snapshot riêng. Cùng email có thể có nhiều Submission.

### Application
Một lần xét **một Submission** cho đúng một tổ hợp:

`Khoa/Phòng + Ngành/Tổ + Vị trí`

Tổ hợp này là identity của Application. Nếu một thông tin trong tổ hợp khác → tạo Application khác.

### Interview Session
Một vòng phỏng vấn của Application.
Một Application có thể có nhiều vòng ngay Phase 1.

### Interview Report
Mỗi participant có một report riêng theo từng Interview Session.

## 3. Current Round

`Current Round` = Interview Session có `round_no` lớn nhất trong tập `access_active` của Application (`Application.is_active AND Interview.is_active`).

- Page Interview quản lý tất cả vòng.
- Page Báo cáo phỏng vấn chỉ dùng Current Round cho bảng chính/Preview/PDF.
- Vòng cũ vẫn giữ lịch sử.
- Nếu current round bị inactive, hệ thống fallback về active round gần nhất trước đó.
- Không được tạo vòng mới nếu round có round_no lớn nhất đang inactive.

## 4. Application durable identity không được rewrite

Ngay từ khi Application được tạo, tổ hợp `Submission + Khoa/Phòng + Ngành/Tổ + Vị trí` là durable identity và **không được đổi** trên chính Application đó.
- Muốn xét tổ hợp khác → tạo/tìm Application khác theo identity mới.
- Exact duplicate cùng tổ hợp, dù Active hay Inactive, luôn resolve về cùng một Application ID.
- Nếu Active → warning + confirm rồi update các field không thuộc identity.
- Nếu Inactive → dùng Reactivate; không tạo duplicate Application ID.

## 5. Role model

### Root Admin
- Chỉ 1 user duy nhất.
- Có toàn quyền.
- Gán/revoke permission cho HR.
- Không được hard-delete/inactive trong Phase 1 để tránh lockout.

### HR
- Là internal user có role `Chuyên viên HR`.
- Quyền chi tiết được Root Admin gán theo permission.
- Có thể được cấp quyền sửa report của Interviewer.

### Interviewer
- Không cần role cố định riêng.
- Active internal user được chọn trong Participants sẽ có quyền contextual trên đúng Interview Session đó.

### Candidate
- Login bằng verified email.
- Chỉ xem/chỉnh dữ liệu Candidate Portal theo rule.

## 6. Tech direction

- Frontend/hosting: Vercel + Next.js App Router.
- Backend/Auth/DB/Storage: Supabase.
- PostgreSQL RLS + explicit grants bắt buộc.
- Sensitive implementation views để private/non-exposed hoặc security-invoker nếu expose.
- Mutations nhiều side effect qua authenticated Server Action + transactional RPC/DB command.
- Optimistic concurrency + idempotency cho action nhạy cảm.
- Business Logic v1.2 frozen; **Technical Specification Freeze** must pass before production coding. Production migration/RLS/RPC/race/storage/performance/backup/deployment evidence belongs to the post-coding **Implementation Validation / Migration Freeze**, not to the pre-code specification freeze.


## Architecture gate and authorization boundary
Business Logic remains frozen while Technical Architecture has a separate gate. v1.17 is the current implementation-contract **frozen specification package**, not a production migration bundle. One UI mutation must map to one explicit backend command; private data access is enforced by RLS/GRANT plus server authorization, not UI visibility.

## Candidate form sessions and lifecycle architecture
Pre-submit Candidate uploads live under a temporary Candidate Form Session; a Submission remains a submitted snapshot and is created only on Submit. Submission operational status has manual states NEW/READ and system-derived states PROCESSED/DONE/CLOSED. Candidate Inbox parent summary uses latest Submission; historical submissions remain preserved. Application can be Reactivated in Phase 1 under validation/audit.



---

<!-- SOURCE: 02_ROLES_PERMISSIONS_AND_NAVIGATION.md -->

# 02. Roles, Permissions & Navigation

## 1. Root Admin

- Hệ thống có **duy nhất 01 Root Admin**.
- Root Admin có toàn bộ permission.
- Chỉ Root Admin được:
  - gán/revoke permission của HR;
  - thay đổi role HR;
  - quản lý quyền hệ thống.
- Root Admin không được Inactive/Hard Delete trong Phase 1 để tránh mất quyền quản trị.
- Root Admin vẫn phải tuân thủ các business safety rule như `CONFIRMED` lock, conflict validation, confirmation dialog; “toàn quyền” không đồng nghĩa silent bypass.

## 2. HR

Một User muốn làm HR phải:
- là internal user Active;
- email hợp lệ `@eiu.edu.vn`;
- có role `Chuyên viên HR`.

Hệ thống vẫn dùng permission granular, nhưng **HR mới được tạo mặc định nhận Full HR Permission Set** để phù hợp vận hành thực tế. Root Admin có thể revoke từng permission để tạo HR hạn chế. Các quyền Root-only/security identity không thuộc Full HR Permission Set.

### Permission catalog đề xuất

| Permission code | Ý nghĩa |
|---|---|
| `submissions.view` | Xem Quản lý phiếu |
| `submissions.edit` | Edit dữ liệu HR-editable của phiếu |
| `submissions.status` | Mark New/Read, xử lý status |
| `candidates.active_manage` | Active/Inactive Candidate account |
| `candidates.delete_unused` | Hard-delete Candidate chưa có Submission/business usage |
| `applications.manage` | Tạo/update/delete-or-inactive Application |
| `interviews.view` | Xem page Interview |
| `interviews.manage` | Tạo/Edit/Copy/Delete-or-inactive Session |
| `interviews.status` | Đổi Interview Schedule Status |
| `interviews.participants` | Add/reorder/remove/re-add Participant |
| `interviews.documents` | Upload/xóa tài liệu Interview |
| `interviews.email` | Gửi thư ứng viên/người tham dự |
| `emails.history_view` | Xem Email History trong đúng parent/context |
| `emails.history_delete` | Xóa Email History với cleanup classification hợp lệ; requires `emails.history_view` |
| `reports.view` | Xem page Báo cáo/Preview/PDF |
| `reports.manage_status` | Đổi Report Status / HR Report Note |
| `reports.visibility` | Ẩn/Hiện với Interviewer |
| `reports.edit_interviewer` | **Sửa report của Interviewer** |
| `reports.delete` | Xóa/Inactive report theo rule |
| `master_data.manage` | Quản lý danh mục được phép |
| `users.directory_manage` | Thêm/sửa/inactive internal user directory; được sửa email typo **chỉ khi user chưa bind Auth** |
| `users.identity_manage` | Security identity rebinding; **Root Admin only trong Phase 1** |
| `users.permissions_manage` | **Root Admin only** |

Root Admin có implicit allow cho tất cả permission.

### Default HR Permission Set
Khi Root Admin tạo/gán role `Chuyên viên HR`, hệ thống mặc định cấp **toàn bộ HR permission codes** (không gồm `users.identity_manage`, `users.permissions_manage` và các Root-only recovery actions). Root Admin có thể revoke từng quyền sau đó.

Hệ quả quan trọng: HR mặc định có `submissions.status`, vì vậy workflow bình thường vẫn là **mở Submission NEW → READ**. Permission granular tồn tại để hỗ trợ HR Limited, không phải để HR mặc định thiếu quyền.

### Lưu ý User Directory
HR có `users.directory_manage` có thể:
- thêm internal user;
- sửa tên/chức vụ/business profile;
- Active/Inactive **non-HR, non-Root internal user** theo rule;
- sửa email `@eiu.edu.vn` để sửa typo **khi `auth_user_id` chưa được bind**.

Sau khi Google/Auth identity đã bind, `email`, `auth_user_id`, provider binding là **security identity**, không còn là directory text field. Rebinding user đã bind là Root-only trong Phase 1; Root Admin identity chỉ đổi qua recovery procedure riêng.

HR **không được tự cấp quyền HR**. Permission assignment chỉ Root Admin.

Permission dependencies are authoritative: edit/status/delete/email/manage capabilities require the corresponding view/context permission where one exists; Root permission UI auto-grants prerequisites or blocks invalid combinations. Normal Phase-1 Submission creation remains Candidate-owned.

Permission-detail visibility: Root may view every user's granular effective permissions. A non-root `users.directory_manage` user can view allowed directory/lifecycle fields but not another user's granular effective-permission list; non-root may view only their own effective permissions.

## 3. Interviewer

Interviewer là **contextual permission**.

Một active internal user chỉ thấy một record khi **toàn bộ** predicate sau đúng:
```text
application.is_active = true
AND interview.is_active = true
AND participant.user_id = current_user
AND participant.is_current = true
AND visible_to_interviewers = true
AND app_user.is_active = true
```
Hai điều kiện đầu là canonical `access_active`. Inactive parent Application thu hồi contextual access ngay nhưng không xóa lịch sử.

Được:
- xem Interview info của Session mình tham dự;
- xem/tải tài liệu;
- tạo/edit report của chính mình khi Report Status chưa final;
- xem shared Preview;
- tải PDF.

Không được:
- đổi Interview;
- sửa report người khác;
- đổi HR status;
- thấy HR Note/HR owner/final-source metadata;
- thấy Session khác nếu không phải participant.

## 4. Candidate

- Login/xác thực email.
- Candidate email lấy từ Auth, read-only.
- Không ai edit Candidate email trong Candidate/Profile/Submission.
- Candidate Active mới vào Portal.
- Tạo Submission mới.
- Xem Phiếu của tôi.
- Edit khi Candidate-facing status = `Mới`.
- Không thấy HR Note/Application/Interview/Report nội bộ.

## 5. Navigation

### Root Admin
Tất cả internal pages + quản trị permissions.

### HR
Sidebar item Phase 1 chỉ hiện khi có permission tương ứng:
- Quản lý phiếu ứng tuyển — `PHASE1_RENDERED`
- Interview — `PHASE1_RENDERED`
- Báo cáo phỏng vấn — `PHASE1_RENDERED`
- Danh mục — `PHASE1_RENDERED` khi có quyền
- Người dùng & Phân quyền — `PHASE1_RENDERED` khi có quyền

Các module sau hiện là `FUTURE_HIDDEN / NOT_RENDERED`, không tạo menu rỗng:
- Dashboard
- Nhu cầu tuyển dụng
- Candidate Database
- KPI & Reports

### Interviewer
- Báo cáo phỏng vấn

### Candidate
- Đăng ký mới
- Phiếu của tôi

## 6. HR sửa report của Interviewer

Nếu HR có `reports.edit_interviewer`:
- HR được mở report của từng interviewer và sửa.
- `updated_by/updated_at` ghi đúng HR.
- Nếu HR đang sửa bản stale và Interviewer đã cập nhật trước → HR bị block và phải reload.
- Nếu Interviewer đang dùng bản stale do HR vừa sửa → Interviewer được ưu tiên ghi bản của mình; conflict được log.
- HR-to-HR stale update → block/reload.
- Interviewer same-account multi-tab stale update → block/reload.

## 7. RLS bắt buộc

UI ẩn nút **không đủ**. Backend/RLS phải enforce:
- Candidate ownership + active + editable status.
- HR permission code cho từng action.
- Interviewer contextual access.
- Root Admin unique.
- Internal user Active/domain validation.



---

<!-- SOURCE: 03_CANDIDATE_FORM_AND_PORTAL.md -->

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



---

<!-- SOURCE: 04_HR_APPLICATION_INBOX.md -->

# 04. HR – Quản lý Phiếu Ứng tuyển

## 1. Mục đích

Đây là Application Inbox của HR – nơi nhận tất cả Submission từ Candidate và là điểm bắt đầu xử lý hồ sơ.

## 2. Bảng danh sách chính

Hiển thị gọn:

| Select | Tên | Email | Ngày sinh | Giới tính | SĐT | Trạng thái | HR Note |
|---|---|---|---|---|---|---|---|

Không hiển thị Ngày ứng tuyển ở dòng chính.

### Trường hợp Candidate có nhiều Submission

Hiển thị badge số phiếu cạnh tên, ví dụ:

`Nguyễn Văn A   [3 phiếu]`

Click dòng Candidate:
- Nếu chỉ có 1 Submission → mở Drawer trực tiếp.
- Nếu >1 Submission → bung danh sách phiếu con phía dưới.
- Chỉ một Candidate group được mở tại một thời điểm.

Phiếu con hiển thị:

```text
01/09/2026 14:35 | Processed | HR Note...
20/03/2026 09:10 | Closed    | HR Note...
15/08/2025 16:20 | Done      | HR Note...
```

Tên cột chính thức: **Ngày ứng tuyển**.

Click phiếu con → mở Drawer đúng Submission đó.

## 3. Search / Filter

Search theo kiểu autocomplete / combobox từng ký tự:
- Họ tên.
- Email.
- SĐT.

Filter đề xuất:
- Trạng thái.
- Ngày ứng tuyển.
- Active / Inactive.
- Mới / đã đọc.
- Có/Chưa có Application.

## 4. Submission status

Business status của Submission:
- `NEW` – Mới.
- `READ` – Đã đọc.
- `PROCESSED` – Đang xử lý / đã có Application.
- `DONE` – Hoàn tất thành công theo kết quả Application.
- `CLOSED` – Các Application kết thúc không tuyển.

### New / Read
- Submit mới → New.
- Candidate chỉ được edit khi Submission còn `NEW`. Đây là chủ ý nghiệp vụ để HR không bỏ sót thay đổi sau khi đã đọc.
- HR mặc định có quyền `submissions.status`; khi HR mở phiếu `NEW` → hệ thống tự chuyển `READ`.
- Nếu một HR Limited chỉ có `submissions.view` nhưng không có `submissions.status`, mở phiếu là read-only và **không mutation**.
- Candidate muốn sửa sau khi HR đã đọc phải liên hệ HR; HR chủ động Mark as New.
- HR có thể Mark as New để tự nhắc xử lý lại hoặc mở lại quyền chỉnh Candidate theo rule.

### Processed → New
Không cho chuyển trực tiếp nếu còn Application liên quan.

Phải xóa thông tin/Application gán tại page Interview trước, sau đó mới cho phép đưa Submission về New.

### Inactive (effective status từ Candidate account)
`Inactive` không phải Submission business status riêng. Đây là manual override ở **cấp Candidate/account**, được thao tác từ Page Quản lý phiếu.
- Không xóa Candidate, Submission hoặc Application.
- HR vẫn xem/filter được toàn bộ dữ liệu.
- Khi Candidate inactive, UI HR có thể hiển thị `INACTIVE` như effective status cho các phiếu thuộc Candidate đó, trong khi trạng thái workflow nền vẫn được bảo toàn để tính lại khi Active.
- Candidate không đăng nhập được vào Candidate Portal bằng email đó cho tới khi HR Active lại.
- Candidate inactive không xuất hiện trong selector `Ứng tuyển` mặc định ở page Interview.
- Application/Interview/Report đã tạo trước đó không bị xóa và vẫn tiếp tục tồn tại ở các page nội bộ.
- Khi Active lại, hệ thống recalculation trạng thái theo Application hiện hành.

## 5. HR Note

- `hr_note` chỉ HR thấy.
- Candidate không có field ghi chú này và không nhìn thấy.
- Hiển thị rút gọn ở table.
- Chỉnh sửa trong Drawer.

## 6. Drawer

Drawer rộng, desktop-first.
Bố cục cố định:

| Label | Nội dung |
|---|---|
| **Họ tên:** | Nguyễn Văn A |
| **Email:** | abc@email.com |
| **Ngày sinh:** | 01/01/1995 |
| **Giới tính:** | Nam |
| **SĐT:** | 090... |
| **Địa chỉ hiện tại:** | ... |

Không dùng bố cục 2x2. Là **1 cột label + 1 cột value**.

### Section trong Drawer
1. Thông tin chung.
2. Education.
3. Working Experiences – HR only.
4. Activities – HR only.
5. Other – HR only.
6. Documents.
7. HR Note / Nguồn tuyển dụng (optional HR metadata).
8. Cập nhật thông tin tuyển dụng.
9. Cập nhật gần nhất.

## 7. Edit Drawer

- Một nút `Edit` cho toàn bộ Drawer.
- Không Edit từng section.
- Khi Edit: toàn bộ field HR được phép sửa chuyển sang editable.
- Footer: `Cancel | Save Changes`.
- Nếu đóng drawer khi có dữ liệu chưa lưu → cảnh báo.

## 8. Documents

HR được:
- Preview.
- Download.
- Upload thêm.
- Replace/Xóa theo quyền.

## 9. Link sang Interview

Dòng gần cuối Drawer:

**Cập nhật thông tin tuyển dụng:**
- `Update` – chưa có Application.
- `Updated` – đã có Application.
- Nếu có nhiều Application có thể hiển thị số lượng, ví dụ `Updated (2)`.

Click → chuyển sang page Interview và mở/filter đúng Candidate/Submission.

## 10. Bulk actions

Checkbox trên bảng cho phép:
- Inactive.
- Active lại.
- Mark as New / Read theo rule.
- Các bulk action khác **OUT OF SCOPE Phase 1** trừ khi được phê duyệt qua Change Request.

## 11. Last updated

Chỉ hiển thị ở cuối Drawer, không hiển thị trong bảng:

`Cập nhật gần nhất: dd/mm/yyyy hh:mm - bởi ...`

## Parent Candidate row and grouped pagination
- Parent Candidate row uses **latest Submission only** for Submission-derived summary fields, ordered `submitted_at DESC, submission_id DESC`.
- This matches owner intent: older Submissions are failed/obsolete for operational summary; they remain historical child records but do not drive the parent summary.
- Parent row fields `Tên / DOB / Gender / Phone / Status / HR Note` therefore come from the latest Submission snapshot; Email remains the Candidate verified identity.
- Grouped pagination is by **Candidate**, never raw Submission row. Children are fetched with the Candidate group or lazy-loaded.
- Stable sort uses requested sort + Candidate ID tie-breaker.
- PII search value (name/email/phone) is not persisted in URL/query string.



---

<!-- SOURCE: 05_HR_INTERVIEW_PAGE.md -->

# 05. HR – Interview Page

## 1. Mục đích

Page Interview quản lý:
- Application;
- các vòng Interview;
- lịch/logistics;
- participants;
- tài liệu;
- email.

Không quản lý nội dung report cuối; report nằm ở Page Báo cáo phỏng vấn.

## 2. Application identity

Một Application = một Submission được xét cho đúng tổ hợp:

`Khoa/Phòng + Ngành/Tổ + Vị trí`

Nếu tổ hợp khác → Application khác.

Application identity không được rewrite ngay từ khi tạo. Muốn đổi Khoa/Phòng / Ngành/Tổ / Vị trí → tạo/tìm Application khác; exact same identity dùng lại cùng Application ID.

## 3. Bảng

| Tickbox | Họ và tên | Thời gian | Địa điểm | Trạng thái | Ghi chú |
|---|---|---|---|---|---|

Cột tên:

**Nguyễn Văn A**  
`Giảng viên Điện tử – Viễn thông - Khoa Kỹ thuật`

Không dùng dấu `·`.

### Nhiều vòng
Application là dòng cha; các Interview Session bung bên dưới:

```text
Nguyễn Văn A
Giảng viên Điện tử – Viễn thông - Khoa Kỹ thuật
  Vòng 1 | 08:30, Thứ Năm, 07/05/2026 | Confirmed
  Vòng 2 | 14:00, Thứ Sáu, 15/05/2026 | Scheduled
```

Chỉ một Application group mở tại một thời điểm nếu cần giữ UI gọn.

## 4. Interview Schedule Status

| Code | VI | Màu | Edit |
|---|---|---|---|
| `AVAILABLE` | Sẵn sàng | Đỏ | Có |
| `SCHEDULED` | Đã xếp lịch | Xanh dương | Có |
| `AWAITING` | Chờ xác nhận | Cam | Có |
| `CONFIRMED` | Đã xác nhận | Xanh lá | **Không** |
| `CANCELLED` | Hủy | Xám | Có |

- HR đổi thủ công.
- Không ép thứ tự.
- Save lịch không tự đổi status.
- Gửi email không tự đổi status.
- Muốn Edit `CONFIRMED` → đổi status khác trước.

## 5. Nút `Ứng tuyển`

UI label vẫn là **Ứng tuyển**, nhưng entity được chọn thực tế là **Submission cụ thể**, không phải Candidate chung chung.

Searchable multi-select:
- search Tên/Email/SĐT;
- option hiển thị tối thiểu 3 dòng để phân biệt nhiều lần nộp:
  **Nguyễn Văn A**
  `abc@email.com`
  `Phiếu: 01/09/2026 14:35 · Đã đọc`
- backend nhận `submission_id` của option được chọn, không tự suy ra phiếu mới nhất;
- khi điều hướng từ Submission Drawer, `submission_id` được preselect/lock cho thao tác đó;
- `CLOSED` vẫn có thể tạo Application mới theo business rule; khi có Application active, Submission quay lại `PROCESSED`;
- checkbox `Trùng`.

Popup `Update Information`:
1. Khoa/Phòng – required.
2. Ngành/Tổ – optional.
3. Vị trí – required.
4. Demo Topic – chỉ cho single assignment hoặc edit riêng; nếu bulk thì để trống.
5. HR phụ trách – active user role `Chuyên viên HR`.

### Exact duplicate
Nếu đúng cùng Submission + Khoa/Phòng + Ngành/Tổ + Vị trí:
- warning;
- yêu cầu confirm;
- nếu tiếp tục: update Application hiện có, không tạo ID mới.

## 6. Tạo Vòng 1

Khi tạo Application mới, hệ thống tạo Interview Session Vòng 1:
- `round_no = 1`;
- `schedule_status = AVAILABLE`;
- `report_status = INTERVIEW_SCHEDULING`;
- Demo Topic:
  - single assignment có thể nhập ngay;
  - bulk assignment để trống.

## 7. Tạo vòng tiếp theo

- `1 Application → N Interview Sessions`.
- Vòng mới giữ nguyên identity của Application.
- `round_no = max(round_no) + 1`.
- Demo Topic **luôn để trống** ở vòng mới; HR tự điền.
- Chỉ được tạo vòng mới nếu record có round_no lớn nhất đang Active.
- Nếu round cuối đang Inactive → phải Reactivate hoặc Hard Delete hợp lệ trước; không tạo vòng mới.

### Delete/Inactive round
- Chỉ round có `round_no` lớn nhất hiện có mới được Delete/Inactive.
- Không được Delete/Inactive vòng giữa khi còn vòng sau.
- Muốn xử lý vòng giữa → xử lý vòng sau trước.
- Hard Delete round cuối chỉ khi chưa có business usage/reference.
- Nếu đã có usage → Inactive.
- Không renumber round lịch sử.
- Nếu round cuối hard-delete hoàn toàn vì chưa có lịch sử, số round đó có thể được dùng lại khi tạo mới.

## 8. Tạo lịch

Một Session/lần.

Field:
- ngày;
- giờ bắt đầu;
- giờ kết thúc;
- hình thức;
- phòng hoặc Meeting Link;
- Demo Topic;
- participants;
- Interview Note.

### Hình thức
Danh mục:
- Trực tiếp;
- Online;
- có thể mở rộng.

## 9. Participants

Nguồn: `Danh mục → Người dùng`.

- Chỉ User Active.
- Searchable.
- Mỗi dòng một người.
- Có icon Xóa.
- Không duplicate.
- Có drag/drop hoặc ↑ ↓.
- Thứ tự này quyết định Interviewer 1,2,3... trong PDF.
- Snapshot tên/email/chức vụ khi chọn.

Nếu remove người đã có report:
- warning;
- participant không còn current;
- report không render trong PDF hiện hành;
- user không còn thấy record.
Nếu add lại → hỏi Restore old / Create new.

## 10. Copy lịch

Icon `Copy lịch` ở đầu dòng.

Target phải là:
- cùng Application → tạo vòng tiếp theo; hoặc
- một Application khác đã tồn tại.

Không tự tạo Application ngầm.

Copy schedule/logistics phù hợp (ngày, giờ, format, room/location, participant prefill) nhưng:
- Demo Topic để trống;
- HR được đổi time/room/participants;
- `round_no` do target Application quyết định.

## 11. Conflict validation

Trước commit:
- Candidate overlap → **BLOCK**;
- Room overlap nếu dùng phòng → **BLOCK**;
- mọi current Interviewer overlap → **BLOCK**;
- interval semantics `[start_at,end_at)`; `end=start` là adjacent và được phép;
- bỏ qua `CANCELLED`, Interview inactive, parent Application inactive hoặc Interview chưa có interval.

Trước bất kỳ mutation nào làm Interview từ dormant/non-resource-blocking thành operational/resource-blocking, server cũng phải revalidate **mọi current Participant vẫn là Active Internal User**; nếu không, fail `CURRENT_PARTICIPANT_INACTIVE_REASSIGN_REQUIRED` và yêu cầu remove/replace Participant.

Candidate/Room/Interviewer conflict → **block Save**.

Server phải re-check trong transaction để tránh race condition giữa hai HR.

## 12. Drawer HR

Layout `Label | Nội dung`.

- Họ tên.
- Email.
- SĐT.
- Khoa/Phòng.
- Ngành/Tổ.
- Vị trí.
- Vòng.
- Demo Topic.
- Thời gian.
- Hình thức.
- Địa điểm/Meeting Link.
- Schedule Status.
- Participants.
- Interview Note.
- HR phụ trách.
- Cập nhật gần nhất.

Nút đầu:
`Edit | Xóa | Gửi thư ứng viên | Gửi thư người tham dự`

## 13. Toolbar

Sticky dưới page title:
- Ứng tuyển.
- Tạo lịch.
- Xóa.
- Đổi status.
- Gửi thư ứng viên.
- Gửi thư người tham dự.

`Tạo lịch` không bulk.

## 14. Email/Documents

- 2 nút email thủ công.
- Preview trước gửi.
- Không tự đổi status.
- Email History có tickbox + Delete.
- Documents optional cho HR upload.
- Candidate không thấy.
- Interviewer thấy/tải khi còn quyền thấy Session.

## 15. Search/Filter

Search: Tên/Email/SĐT.

Filter:
- Khoa/Phòng;
- Ngành/Tổ;
- Vị trí;
- Schedule Status;
- thời gian;
- địa điểm;
- hình thức;
- participant;
- HR phụ trách.


## Schedule conflict engine
Mọi mutation làm một Interview trở thành operationally active phải dùng cùng conflict engine server-side. Block overlap theo:
- Candidate;
- Room (nếu áp dụng);
- mọi current Interviewer.

Khoảng thời gian dùng semantic `[start_at, end_at)`, vì vậy `08:00–09:00` và `09:00–10:00` không overlap. `CANCELLED`, Interview inactive hoặc parent Application inactive không block resource.

## Reactivation, Copy and inactive-history behavior
- Application has explicit **Reactivate Application** action in Phase 1. Reactivation restores child `access_active` state and revalidates only non-elapsed children that would become `reactivation_conflict_relevant = resource_blocking AND end_at > transaction_now`; fully elapsed past-only overlaps do not block lifecycle recovery. Any still-relevant Candidate/Room/Interviewer conflict blocks the whole reactivation. Current Round remains report/outcome selector only.
- Interview list/filter exposes `Active | Inactive | All`; inactive rounds remain discoverable. A latest inactive round must be visible with `Vòng N — Không hoạt động` and Reactivate action when allowed.
- Copy to another Application: if target auto-created Round 1 is structurally empty **and has no incoming/outgoing Copy provenance**, Save fills Round 1; otherwise Save creates the next legal round. Copy UI itself is only a draft/prefill.
- Format switch normalizes stale resources: format not requiring Room clears `room_id`; format not requiring Meeting Link clears `meeting_link`; HYBRID may retain both when metadata requires both.
- Historical inactive Interview Format remains valid for lifecycle operations on an existing Interview but cannot be selected for a new/change reference.
- Grouped pagination is by **Application**, never raw Interview Session.

## Canonical schedule predicates
- `access_active` controls active/inactive context and Interviewer access.
- `current_round` selects report/outcome/PDF only.
- `resource_blocking` includes every access-active, non-CANCELLED Interview with a real interval; not limited to Current Round.
- Application Reactivate re-checks every **NON-ELAPSED** child that would become `reactivation_conflict_relevant = resource_blocking AND end_at > transaction_now` before commit. Fully elapsed historical intervals do **not** block lifecycle recovery.



---

<!-- SOURCE: 06_INTERVIEW_REPORT_HR_AND_INTERVIEWER.md -->

# 06. Báo cáo phỏng vấn – HR & Interviewer

## 1. Nguyên tắc nhiều vòng

Page Báo cáo phỏng vấn hiển thị **mỗi Application một dòng**.

Dòng đó lấy dữ liệu của:
> `Current Active Latest Interview Round`

Vòng cũ không hiển thị thành dòng chính riêng nhưng vẫn giữ lịch sử và có thể xem từ Application/Interview history.

Preview/PDF hiện hành **chỉ dùng Current Round**.

## 2. HR table

| Tickbox | Họ và tên | Vị trí | Thời gian phỏng vấn | Địa điểm | Trạng thái | Ghi chú |
|---|---|---|---|---|---|---|

Chỉ Application có ít nhất một Interview Session mới xuất hiện.

## 3. Report Status thuộc Interview Session

| Code | VI | English |
|---|---|---|
| `INTERVIEW_SCHEDULING` | Chờ xếp lịch | Interview Scheduling |
| `AWAITING_INTERVIEW` | Chờ phỏng vấn | Awaiting Interview |
| `WAITING_FOR_REPORT` | Chờ báo report | Waiting for Report |
| `REPORT_SUBMITTED` | Đã gửi Báo cáo | Report Submitted |
| `FOLLOW_UP` | Theo dõi thêm | Follow-up |
| `ON_HOLD` | Hoãn | On Hold |
| `HIRED` | Tuyển dụng | Hired |
| `REJECTED` | Từ chối | Rejected |

- HR đổi thủ công.
- Không ép thứ tự.
- Page Báo cáo dùng status của Current Round.

### Khi tạo vòng mới
Vòng mới trở thành Current Round và khởi tạo:
`INTERVIEW_SCHEDULING`.

Vì vậy report/status/PDF vòng cũ không còn là report hiện hành, nhưng dữ liệu cũ không bị xóa.

## 4. Application outcome

Application outcome không cần HR nhập riêng.

Derive từ Current Round:
- Current Report Status = `HIRED` → Application outcome `HIRED`.
- Current Report Status = `REJECTED` → Application outcome `REJECTED`.
- Còn lại → `IN_PROGRESS`.

Tạo vòng mới làm Application trở lại `IN_PROGRESS` vì Current Round mới chưa có kết quả final.

## 5. Interviewer-facing status

| HR Current Round | Interviewer thấy |
|---|---|
| Chờ xếp lịch | Chờ xếp lịch |
| Chờ phỏng vấn | Chờ phỏng vấn |
| Chờ báo report | Chờ báo report |
| Đã gửi Báo cáo | Đã gửi Báo cáo |
| Theo dõi thêm | Đã gửi Báo cáo |
| Hoãn | Đã gửi Báo cáo |
| Tuyển dụng | Đã gửi Báo cáo |
| Từ chối | Từ chối |

## 6. HR Drawer

**Chỉ hiển thị Report data, không lặp Interview data.**

Nút đầu:
- Edit HR Note / quản lý Report theo quyền.
- Ẩn/Hiện Interviewer.
- Xem.
- Tải PDF.

Không có nút `Xóa` ở aggregate drawer. Delete/Inactive chỉ nằm cạnh một `interview_report_id` cụ thể.

Nội dung:
- Report Status Current Round.
- HR phụ trách (Application-owned; changed via `applications.manage`).
- HR Report Note.
- Visibility.
- Danh sách interviewer reports.
- Nguồn decision block hiện hành – chỉ HR.
- Cập nhật gần nhất.
- Link `Xem thông tin phỏng vấn`.

Nếu HR có permission `reports.edit_interviewer`, ở từng interviewer report có action Edit.

## 7. Visibility

`visible_to_interviewers` thuộc Current Interview Session.

- Ẩn: tất cả participant của Current Round không thấy row.
- Không xóa participant/report/PDF.
- Hiện lại: dữ liệu cũ xuất hiện lại.
- HR filter: Tất cả / Đang hiển thị / Đang ẩn.

## 8. Interviewer View

Interviewer page cũng hiển thị một dòng theo Current Round nếu:
- họ là current participant của Current Round;
- Session visible;
- User active.

Drawer Interviewer = **Interview info + Report info**.

### Nút
Chưa có report:
`Báo cáo PV | Xem | Tải PDF`

Đã có:
`Edit | Xem | Tải PDF`

Nếu Report Status Current Round = `HIRED` hoặc `REJECTED`:
- Interviewer không được Edit.
- Muốn Edit lại → HR đổi status về non-final.

## 9. Form report cá nhân

**Hard rule:** Báo cáo phỏng vấn **không có chấm điểm/scoring/rating/star/thang điểm**. Không developer/AI nào được tự bổ sung cơ chế điểm nếu chưa có Change Request nghiệp vụ mới.

Các field không bắt buộc:

### Evaluation and Comment
1. Kiến thức chuyên môn / Professional Knowledge
2. Kỹ năng cần thiết / Necessary Skills
3. Phẩm chất, tính cách / Qualities and Personality
4. Điểm mạnh và hạn chế / Strengths and Limitations
5. Khác / Other

### Decision block
- Kết luận / Conclusion
- Dự kiến công việc cụ thể được phân công / Expected Specific Job Assigned
- Thời gian dự kiến tuyển dụng / Expected Recruitment Time

Mỗi interviewer có 1 report riêng cho mỗi Interview Session.

## 10. Preview/PDF

### Evaluation
Render tất cả participant hiện hành theo `participant_order`.

Tên + chức vụ:
- auto lấy từ User HR đã chọn ở Page Interview;
- dùng snapshot tại thời điểm chọn.

Field trống vẫn render đúng template.

Nếu participant bị remove:
- block của họ biến mất khỏi Preview/PDF hiện hành;
- thứ tự còn lại được đánh lại.

### Final Decision Source

Hội đồng phải trao đổi và thống nhất; **không yêu cầu mọi Interviewer cùng nhập 3 field final decision**. Thông thường chỉ 01 Interviewer đại diện điền. Nếu Interviewer khác sửa một trong 3 field sau đó, hệ thống hiểu đó là bản điều chỉnh mới sau trao đổi của hội đồng.

Trong **Current Round**, eligible report là report active/current có ít nhất một field decision block có nội dung. Final source = eligible report có `decision_updated_at` mới nhất.

- `decision_updated_at` / `decision_updated_by` **chỉ cập nhật khi một trong 3 field final decision thay đổi**.
- Sửa `Professional Knowledge`, `Necessary Skills`, `Qualities and Personality`, `Strengths and Limitations`, `Other` không làm đổi Final Decision Source.
- Cả 3 final fields luôn lấy từ cùng một report; không merge field từ nhiều Interviewer.
- Nếu source hiện hành xóa hết 3 decision fields → source fallback về eligible report có `decision_updated_at` gần nhất trước đó.

HR thấy:
- nguồn kết luận hiện hành;
- `decision_updated_by`;
- `decision_updated_at`;
- `updated_at` tổng thể của report có thể hiển thị riêng nếu cần audit.

Interviewer không thấy metadata kỹ thuật về source.

## 11. Concurrency khi HR sửa Interviewer Report

HR chỉ sửa được khi có `reports.edit_interviewer`.

- HR stale vs Interviewer newer → HR Save bị block, yêu cầu reload.
- Interviewer vs HR trên cùng report → dùng **field-aware patch/merge**; nếu sửa khác field thì giữ cả hai thay đổi; nếu cùng field thì Interviewer wins. Không whole-row overwrite từ stale form.
- HR vs HR → stale Save bị block.
- Interviewer same-user nhiều tab → stale Save bị block.

## 12. PDF nhiều vòng

- PDF hiện hành chỉ của Current Round.
- Report/PDF vòng cũ vẫn có dữ liệu lịch sử để truy xuất nội bộ nếu cần.
- Không merge nhiều vòng thành một PDF trong Phase 1.

## Report delete semantics and pagination
- HR Report page remains one row per Application using Current Round and paginates by **Application**.
- Remove ambiguous aggregate-level `Xóa` action. Aggregate drawer actions are: Edit HR Note, Change Report Status, Hide/Show Interviewer, Xem, Tải PDF.
- Delete/Inactive is only attached to a concrete `interview_report_id` for a specific participant report. Deleting/inactivating an Interview Session belongs to the Interview module.
- System email from Report has **no attachments in Phase 1**.

## Trusted mutation split
HR Report Status and HR Report Note are separate mutations. `change_report_status` is the only trusted writer of Report Status and always recalculates the parent Submission in the same transaction. `update_hr_report_note` edits only the HR-only note and never changes status or derived outcome.



---

<!-- SOURCE: 07_STATUS_AND_BUSINESS_RULES.md -->

# 07. Status & Business Rules

## 1. Candidate Account

`candidate.is_active` là manual override.

- Active → Candidate login Portal.
- Inactive → không login được.
- Khi Inactive, HR UI có thể hiển thị effective status `Inactive`.
- Active lại → Submission status được tính lại theo dữ liệu hiện hành.

## 2. Submission Status

Business status:
`NEW / READ / PROCESSED / DONE / CLOSED`

Candidate-facing:
- NEW → Mới
- READ / PROCESSED → Đang xử lý
- DONE / CLOSED → Hoàn thành
- Candidate Inactive → không truy cập Portal.

Rules:
- Submit → NEW.
- HR mở → READ.
- Mark New chỉ khi không còn active Application.
- Có active Application → PROCESSED.
- Any active Application outcome HIRED → DONE.
- All active Applications outcome REJECTED → CLOSED.
- Không còn active Application:
  - nếu current status là `NEW` hoặc `READ` → giữ nguyên manual state;
  - nếu current status là derived (`PROCESSED`/`DONE`/`CLOSED`) do Application cuối bị remove/inactivate → về `READ`.
- Candidate Reactivate là lifecycle exception: nếu không có active Application → `READ`.
- Candidate Inactive override không xóa status gốc.

## 3. Application identity/outcome

Identity:
`submission_id + unit_id + department_team_id + position_id`

Nếu khác identity → Application khác.

Effective outcome:
- Current Round report_status HIRED → HIRED
- Current Round report_status REJECTED → REJECTED
- Khác → IN_PROGRESS

## 4. Interview Schedule Status

`AVAILABLE / SCHEDULED / AWAITING / CONFIRMED / CANCELLED`

- HR đổi thủ công.
- Không ép sequence.
- CONFIRMED khóa Edit.
- CANCELLED/inactive session không block conflict.

## 5. Report Status

Thuộc Interview Session:

`INTERVIEW_SCHEDULING / AWAITING_INTERVIEW / WAITING_FOR_REPORT / REPORT_SUBMITTED / FOLLOW_UP / ON_HOLD / HIRED / REJECTED`

- HR đổi thủ công.
- Không ép sequence.
- HIRED/REJECTED khóa Edit của Interviewer.
- HR có permission `reports.edit_interviewer` vẫn được sửa report, nhưng concurrency rule phải áp dụng.

## 6. Current Round

Current Round = Session có `round_no` lớn nhất trong tập `access_active` (`Application.is_active AND Interview.is_active`).

- Page Báo cáo/Preview/PDF dùng Current Round.
- Tạo vòng mới → Current Round đổi sang vòng mới.
- Vòng mới report_status = INTERVIEW_SCHEDULING.
- Nếu latest created round inactive → không tạo round mới.
- Chỉ latest created round được Delete/Inactive.
- Không renumber lịch sử.

## 7. Warning vs Blocking

### Warning + cho tiếp tục
- status combination bất thường;
- exact duplicate Application (sau confirm sẽ update existing).

### Block
- Edit Interview khi CONFIRMED.
- Candidate edit khi không New.
- Mark New khi còn active Application.
- Tạo round mới khi latest round inactive.
- Delete/Inactive vòng giữa khi có vòng sau.
- Interviewer/room time overlap.
- Candidate time overlap: **BLOCK** across all `resource_blocking` Interview Sessions of the same Candidate.
- stale HR update.
- action không có permission.

## 8. Delete/Inactive

- Chưa có business usage/reference → Hard Delete.
- Có usage/reference → `is_active=false`.

Activity Log **không** tính là business reference để chặn hard delete.

Owned child data có thể cascade khi parent hợp lệ để hard-delete; downstream business reference mới là blocker.

## 9. Root Admin

- Chỉ 1.
- All permissions.
- Không cho Inactive/Delete trong Phase 1.
- Chỉ Root Admin gán/revoke HR permissions.


## 10. Final Decision Source

- Không yêu cầu tất cả Interviewer nhập 3 final decision fields.
- Hội đồng thống nhất; thông thường 01 Interviewer đại diện nhập.
- Nếu Interviewer khác sửa một trong 3 field sau đó, đó là decision revision mới.
- Final source dựa trên `decision_updated_at`, không dùng generic `updated_at`.
- `decision_updated_at/by` chỉ đổi khi Conclusion / Expected Specific Job / Expected Recruitment Time thay đổi.
- Sửa 5 evaluation fields không đổi Final Decision Source.
- Cả 3 field final luôn lấy từ cùng một source report.

## Submission lifecycle and master-history rules
Submission manual states: `NEW`, `READ`. Submission derived states: `PROCESSED`, `DONE`, `CLOSED`; only the authoritative recalculation function may set derived states. Outcome-changing transactions lock parent Submission before recalculation.

Application supports Reactivate in Phase 1. Inactive Application makes child Interview `access_active=false`; reactivation restores access-active semantics only after required validations/conflict checks.

Referenced inactive master values remain valid for history but cannot be newly selected.


## Canonical status and Interview predicates
- Generic Submission recalculation does **not** convert untouched `NEW` to `READ` merely because no Application exists.
- `access_active`, `current_round`, and `resource_blocking` are distinct; see `73_DOMAIN_GLOSSARY_AND_CANONICAL_PREDICATES.md`.
- Every active, non-CANCELLED Interview with a real `[start_at,end_at)` interval is resource-blocking even when it is not Current Round. Current Round is only the report/outcome/PDF selector.
- Application identity is durable/global for one `Submission + Unit + Team + Position`; exact same assignment is reactivated/updated, never duplicated.



---

<!-- SOURCE: 08_DATA_MODEL_AND_FIELD_DICTIONARY.md -->

# 08. Data Model & Field Ownership — v1.8

Business entity ownership remains based on Business Logic Core v1.2. Current v1.8 incorporates the accumulated schema-conformance amendments from prior external reviews.

## 1. Candidate
Physical fields:
- `candidate_id`
- `auth_user_id` — verified Supabase Auth identity
- `email` — verified, immutable as normal profile field
- `current_full_name` / `current_phone`
- `last_submission_at`
- `is_active`
- `inactive_at` / `inactive_by`
- `created_at` / `updated_at` / `version_no`

Rules:
- first verified OTP login provisions/finds Candidate atomically;
- fallback by verified normalized email is allowed only inside the trusted provisioning command to reconnect a recreated Auth identity without duplicating Candidate;
- inactive Candidate cannot access Portal but internal recruitment history/process remains.

## 2. Submission
One form submission snapshot:
- `submission_id`, `candidate_id`
- `status_code`
- `full_name`, `date_of_birth`, `gender_code`, `current_address`, `phone`, `email_snapshot`, `other_info`
- `hr_note`
- `submitted_at`, `created_at`, `updated_at`
- `updated_by_internal_user_id`, `updated_by_candidate_id`
- `version_no`

Invariant: `email_snapshot = Candidate.email` at creation/update of identity snapshot.

Candidate writable DTO excludes all internal/system fields. HR uses a separate HR patch DTO.

Children: Education, Working Experiences, Activities, Documents, Privacy Acknowledgement.

## 3. Submission Documents
### Submission Document Logical Header
Stable business identity for one document across immutable versions:
- `logical_document_id`
- `submission_id`
- `document_type_id`
- creator metadata

The logical header owns **parent Submission + document type**. Those semantic fields are immutable once created.

### Submission Document Version
Immutable storage/version record:
- `document_id`
- `logical_document_id`
- `version_no > 0`, `is_current`
- `storage_bucket`, `storage_path`, `original_filename`
- `mime_type`, `file_size_bytes`, `checksum_sha256`
- uploader identity + `uploaded_at`

A version row does **not** duplicate `submission_id` or `document_type_id`; those derive through the logical header.

Constraints:
- unique `(logical_document_id, version_no)`;
- unique current row per `logical_document_id`;
- unique `(storage_bucket, storage_path)`;
- `REPLACE`/`DELETE` may target only a logical header that has exactly one current version at both stage-time and Save-time;
- max 5 current logical files per Submission; max 5 MB/file; formats limited to approved PDF/Word/PPT/PNG/JPEG whitelist.

Candidate form requiredness is frozen: **CV required; Degree/Transcript/Certificate/Other optional**.

## 4. Application
Identity:
- `application_id`
- `submission_id`
- `unit_id`
- optional `department_team_id`
- `position_id`
- `hr_owner_id`
- `is_active`
- timestamps + `updated_by` + `version_no`

`candidate_id` is not duplicated; Candidate derives through Submission.

Hierarchy invariant is null-safe:
- Application Unit = Position Unit;
- Application Team **IS NOT DISTINCT FROM** Position Team, including NULL;
- Team, when non-null, belongs to Unit.

One Submission may have multiple Applications for different assignments. The durable identity `(submission_id, unit_id, department_team_id, position_id)` is globally unique across active/inactive history. Exact same assignment resolves the same Application ID: active row may be updated after duplicate confirmation; inactive row is Reactivated. Identity fields are immutable from creation.

## 5. Interview Session
Each round owns:
- `interview_id`, `application_id`, `round_no`
- `demo_topic`
- `start_at`, `end_at`
- `interview_format_id`, `room_id`, `meeting_link`
- `schedule_status_code`, `report_status_code`
- `interview_note` — Interview operational note
- `hr_report_note` — HR-only report-management note
- `visible_to_interviewers`
- `copied_from_interview_id`
- `is_active`
- timestamps + `updated_by` + `version_no`

`access_active = Application.is_active AND Interview.is_active` is the canonical contextual-access base. `current_round` is the highest round among access-active Interviews and is used for current report/outcome/PDF. `resource_blocking = access_active AND non-CANCELLED AND scheduled interval exists` is the conflict predicate and applies to every matching round, independent of Current Round. Candidate inactive does **not** turn internal Interview history/process off.

## 6. Interview Participant
- `interview_participant_id`, `interview_id`, `app_user_id`
- `participant_order > 0`
- snapshot Name/Job Title/Email
- `is_current`, `created_at`, `updated_at`, `removed_at`, `version_no`

Current participants are unique by user and by order inside an Interview. Add/re-add/reorder lock the Interview and re-run schedule conflict checks when the resulting participant becomes active.

## 7. Interview Report
Belongs directly to `interview_participant_id`.

Fields:
- 5 qualitative fields;
- 3 final-decision fields;
- `decision_updated_at`, `decision_updated_by`;
- `is_active`, `is_archived` — canonical lifecycle only: current `(true,false)` or historical archived `(false,true)`;
- `created_at`, `created_by`, `updated_at`, `updated_by`, `version_no`.

No scoring/rating exists.

### Final Decision
The panel discusses and normally one representative fills the final block. Other Interviewers are not required to fill it.

Only changes to Conclusion / Expected Specific Job Assigned / Expected Recruitment Time update decision metadata. Qualitative edits do not move the Final Decision Source. Current source is the eligible report in Current Round with latest `decision_updated_at`; all three final fields come from the same report.

## 8. Internal User & identity
`app_users` contains directory/business profile + Auth binding.

- HR `users.directory_manage` may correct email while `auth_user_id IS NULL`.
- once bound, email/Auth binding is security identity; rebinding is Root-only in Phase 1 (`users.identity_manage`).
- Root Admin identity cannot be changed by ordinary directory/security command; use recovery procedure.
- newly assigned HR receives Full HR Permission Set by default; Root may revoke individual HR permissions.

## 9. Master Data — physical Phase 1
Physical lookup entities exist for:
- Khoa/Phòng; Ngành/Tổ; Position; Position Group;
- Qualification;
- Interview Format including `requires_room` / `requires_meeting_link`;
- Room; Recruitment Source; Document Type;
- Cancellation Reason; Rejection Reason;
- Permission catalog.

Referenced master data is Inactive rather than hard-deleted.

## 10. Email delivery
`email_outbox` is operational delivery queue with lock/lease fields, attempts, provider ID and idempotency key. Semantics: **at-least-once delivery with idempotent enqueue and best-effort/provider-assisted deduplication**, not guaranteed exactly-once.

User-facing `email_history` may be deleted under the frozen business rule, while immutable security audit preserves the delete/send event.

## 11. Privacy acknowledgement
Technical capability records `notice_version`, acknowledgement timestamp, Submission and source. Legal wording/policy remains EIU-owned.

## 12. Upload reservation/finalization
Object Storage and PostgreSQL do not share one transaction. Upload follows reserve → temporary/quarantine object → validate → finalize metadata/current version → retire previous version → cleanup orphan flow.

## 13. Audit
Activity/audit includes actor, action, entity, request/correlation IDs, source/reason, diff and timestamp. No secrets/tokens. Security audit is immutable.

## 14. Derived views
Implementation views remain private by default and use access-active semantics. If exposed, `security_invoker`, explicit GRANT and adversarial RLS tests are mandatory.

## 15. Field classification
Each field is classified in `54_SCHEMA_CONFORMANCE_MATRIX.md` as PHYSICAL / DERIVED / SNAPSHOT / CONFIG / DEFERRED. That matrix is the conformance bridge between this dictionary and `database_schema.sql`.



---

<!-- SOURCE: 09_MASTER_DATA_CATALOG.md -->

# 09. Danh mục / Master Data — Phase 1 Physical Model

## 1. Menu cha: Danh mục
Các mục Phase 1 có physical table/FK tương ứng:
- Khoa/Phòng
- Ngành/Tổ
- Vị trí
- Nhóm vị trí
- Phòng/Địa điểm
- Hình thức phỏng vấn
- Người dùng
- Học vấn
- Nguồn tuyển dụng
- Loại tài liệu
- Lý do hủy
- Lý do từ chối

Permission catalog là cấu hình security; Root Admin quản trị, không phải danh mục nghiệp vụ thông thường cho HR.

## 2. Khoa/Phòng → Ngành/Tổ → Vị trí
Searchable dependent dropdown. Position physically references Unit and optional Team. Application repeats these as a historical/assignment snapshot but DB/RPC enforces null-safe equality with Position.

## 3. Nhóm vị trí
Physical table with at least:
- code; VI/EN label;
- `requires_demo_topic`;
- active.

Position references Position Group by FK.

## 4. Học vấn
Physical Qualification table. Education row references Qualification by FK; values remain HR-editable master data under Delete/Inactive rule.

## 5. Hình thức phỏng vấn
Fields:
- code, VI/EN label;
- `requires_room`;
- `requires_meeting_link`;
- active.

Scheduling command validates these metadata instead of hard-coding only the visible label.

## 6. Người dùng
Fields include Name, EIU Email, Job Title, Unit, Active, Auth binding, HR role and Root flag.

Identity rule:
- before Auth bind: directory manager may correct EIU email typo;
- after bind: email/Auth identity change is Root-only in Phase 1;
- Root identity change uses recovery process;
- inactive user cannot login or be newly selected; historical snapshots remain.

New HR receives Full HR Permission Set by default; Root Admin may revoke individual permissions.

## 7. Recruitment Source / Document Type / Reasons
All are physical lookup tables in Phase 1. Referenced values are inactivated rather than hard-deleted.

Document Type can carry scope/metadata used by UI and upload validation.

## 8. Delete rule
- no business reference → hard delete allowed;
- referenced → Inactive;
- inactive values excluded from default selectors;
- Root Admin protected.

## Historical master-data semantics
- Referenced master records cannot change **structural meaning**. Structural change = create a new record + Inactive old record.
- Display-label typo corrections may be allowed with optimistic versioning + audit when business meaning is unchanged.
- `Inactive` means unavailable for new selection, not invalid for historical records. Existing Interviews using an inactive Interview Format remain operable.
- All Phase-1 masters use consistent `updated_at + version_no`.
- `document_types.scope_code` must be seeded explicitly, not defaulted blindly: CV/Degree/Transcript/Certificates = SUBMISSION; Slide/Publication/Portfolio = INTERVIEW; Other = BOTH.
- `requires_demo_topic` is advisory UI metadata in Phase 1; it does not create an undocumented blocking rule. Cancellation/Rejection reason and Recruitment Source remain optional unless a future owner decision makes them required.

- `Recruitment Source` is optional HR-editable Submission metadata in Phase 1, not Candidate-required input.
- Cancellation reason is optional only while Schedule Status = CANCELLED; leaving CANCELLED clears current reason while audit retains history. Rejection reason is optional only while Report Status = REJECTED; leaving REJECTED clears current reason while audit retains history.



---

<!-- SOURCE: 10_UI_UX_SPEC.md -->

# 10. UI/UX Specification — aligned with Design System v1.8

> Visual source-of-truth is the separate **EIU Recruitment Design System v1.8** pack. This file records the product-specific UI behavior that must stay aligned with frozen business logic.

## 1. Global app shell

Internal desktop app:
- fixed left sidebar: **244px**;
- sticky Page Header;
- `VI | EN` in the top-right utility area, default **VI**;
- sticky Action Toolbar immediately below Page Header;
- page content scrolls independently;
- wide tables scroll horizontally inside their own table container; header/toolbar stay outside that horizontal scroller;
- right-side Detail Drawer does not cover desktop sidebar.

Candidate Portal uses the same visual language but simpler navigation and mobile-priority layouts.

## 2. Typography — hard rule

- Main/body/table content: **minimum 16px**.
- Table header: **16px / semibold (600)**.
- Status badge: **16px / semibold (600)**.
- Input/select/button/field value: **16px**.
- Drawer/modal/popup/preview body: **16px**.
- Labels: **16px / semibold**.
- Helper/meta text may use 14px only when genuinely secondary.

Do not shrink text to force dense operational tables into a laptop viewport.

## 3. Operational tables

Chosen implementation model:

> **Semantic `<table>` + `<colgroup>` + `table-layout: fixed`.**

Rules:
- each page owns one fixed column specification;
- parent rows, expanded rows, loading skeletons and child rows reuse that specification;
- long-content columns receive more width;
- compact columns have explicit width/min/max as needed;
- main table can define a page-specific `min-width` (often 1200–1700px for dense HR tables);
- wrap table in `overflow-x:auto`;
- sticky `<thead>` for long vertical lists;
- header and content cells are left-aligned;
- long business content wraps to new lines rather than default ellipsis;
- status badge itself is centered inside the Status cell;
- server-side pagination/search is expected as data grows.

### Horizontal scroll structure

```text
Sticky Page Header
Sticky Action Toolbar
────────────────────────────
Table Scroll Container
  └─ overflow-x:auto
      └─ table min-width=page spec
          ├─ colgroup
          ├─ sticky thead
          └─ tbody
```

The toolbar must not slide horizontally with the table.

## 4. Expandable row interaction

Pointer behavior:
- parent with children: click anywhere on the **non-interactive row surface** → expand/collapse;
- chevron is only an affordance, not the only click target;
- Checkbox, Status Badge, links, buttons, menus, comboboxes and action icons must stop propagation;
- parent without children: row click opens the Drawer;
- child row click opens the exact child/entity Drawer.

Accessibility:
- include a real semantic expand control/button with `aria-expanded` and accessible name in the first/name cell;
- keyboard users can expand/collapse without relying on a clickable `<tr>` only.

## 5. Status badges and status actions

Badge rules:
- equal width inside the same status group;
- width is sized to the longest approved label across **VI and EN**, with only modest horizontal padding;
- 16px semibold;
- badge text centered;
- color never carries status meaning alone.

Authorized HR/Root Admin can change status through either:
1. one toolbar `Status` dropdown for selected records;
2. clicking the individual row Status Badge.

Both entry points must invoke the same business validation/permission logic.

Read-only personas see a non-interactive badge.

## 6. Language / i18n

- Entire software supports Vietnamese and English.
- Default language: **Vietnamese**.
- Switcher: **`VI | EN`** at top right.
- Switch applies to navigation, page titles, table headers, buttons, status labels, filters, Drawer, modal, validation/warnings and previews.
- User-entered content is not automatically translated.
- Switching language preserves current route/filter state and unsaved form data where safe.
- Date/number formatting is locale-aware; business timezone is `Asia/Ho_Chi_Minh`.

## 7. Drawer

- Opens from right.
- Desktop typical width: **760–860px**, page-specific when needed.
- Layout uses one fixed Label column + one Value column.
- Values wrap for long content.
- Header/action/footer may be sticky when useful.
- One main `Edit` action edits all permitted fields in the Drawer.
- Save/Cancel + unsaved-change warning.

## 8. Modal / Popup

Use Modal for focused actions:
- create/update assignment;
- schedule interview;
- email preview;
- status confirmation;
- destructive confirmation.

Main content typography remains >=16px.

## 9. Searchable combobox / dependent dropdown

Searchable inputs match typed text and support Vietnamese normalization where appropriate.

`Ứng tuyển` uses a dedicated **SubmissionSelector**, never a Candidate-only selector. Search may match Candidate name, verified email and phone, but every selectable option identifies one exact Submission.

Submission option:

**Nguyễn Văn A**  
`abc@email.com`  
`Phiếu: 01/09/2026 · READ`

The component returns `submission_id`; backend never guesses the latest Submission. When opened from a Submission drawer, that `submission_id` is preselected/locked.

Dependent hierarchy:

`Khoa/Phòng → Ngành/Tổ → Vị trí`

- Unit filters Team;
- Team filters Position;
- if Team blank, Position can list Unit-level positions according to master-data rules.

## 10. Quản lý phiếu ứng tuyển

Main columns:

`Select | Tên | Email | Ngày sinh | Giới tính | SĐT | Trạng thái | HR Note | Action`

When Candidate has multiple Submissions:
- parent row click expands;
- child Submission rows reuse the same colgroup;
- business values `Ngày ứng tuyển | Status | HR Note` align to explicit compatible columns;
- no free-floating inner card with drifting columns;
- child row click opens the Submission Drawer.

Single Submission: main row click can open Drawer directly.

## 11. Interview page

Application row displays:

**Nguyễn Văn A**  
`Giảng viên Điện tử – Viễn thông - Khoa Kỹ thuật`

Do not use `·` as separator.

One Application may expand to Vòng 1/2/N. Round child rows remain aligned to the page column spec.

Copy action is independent and does not trigger row expansion.

## 12. Interview Report — no scoring

Hard rule:
- no score;
- no star rating;
- no competency scale;
- no pass percentage.

Each Interviewer report has only:

Qualitative fields:
1. Kiến thức chuyên môn / Professional Knowledge
2. Kỹ năng cần thiết / Necessary Skills
3. Phẩm chất, tính cách / Qualities and Personality
4. Điểm mạnh và hạn chế / Strengths and Limitations
5. Khác / Other

Final Decision block:
6. Kết luận / Conclusion
7. Dự kiến công việc cụ thể được phân công / Expected Specific Job Assigned
8. Thời gian dự kiến tuyển dụng / Expected Recruitment Time

The UI does **not** require every Interviewer to fill fields 6–8. Normally one representative enters the agreed decision. If another Interviewer later changes a final field, that becomes the later agreed revision under the business rule.

## 13. PDF/Print Preview

- Use Current Round only for the current Preview/PDF.
- Interviewer order follows `participant_order`.
- Historical rounds remain in database/history, not merged into the current PDF.
- Final Decision block is sourced from one report according to `decision_updated_at`.
- Do not invent Quốc hiệu/Tiêu ngữ/Tên Hội đồng or other administrative elements.
- Pixel-perfect print layout waits for the official EIU template.

## 14. Demo Persona Switcher — prototype only

Clickable prototype/development may include:
- Root Admin;
- HR Full;
- HR Limited;
- Interviewer;
- Candidate.

It must change menus/actions realistically, but **must not exist as a production authorization mechanism** and must be excluded from production builds.

## 15. Responsive status

Detailed iPad/mobile layout is not yet frozen.

Go-live requirement:
- Candidate Login;
- Candidate Form;
- Phiếu của tôi;

must be mobile-ready.

Internal HR/Admin/Interviewer operations remain desktop-first, then iPad/mobile are designed and UAT-tested after the Desktop prototype revision.



---

<!-- SOURCE: 11_EMAIL_DOCUMENTS_AND_ACTIVITY_LOG.md -->

# 11. Email, Documents & Activity/Audit Log — v1.8

## 1. Manual email actions

Page Interview keeps two manual actions:
1. **Gửi thư ứng viên / Send to Candidate**
2. **Gửi thư người tham dự / Send to Participants**

Rules:
- Preview before send.
- Send does not automatically change Interview status.
- Can send from selected table rows or individual drawer where permitted.
- Final email copy/templates are still owner input before UAT/go-live.

## 2. Transactional Outbox

Production implementation must not keep a business DB transaction open while calling an external email provider.

Pattern:

`Business command → create email_outbox → COMMIT → worker/server sender → update delivery state → create/update Email History → immutable audit`

Outbox supports:
- `QUEUED / SENDING / SENT / FAILED / CANCELLED`
- attempt number
- retry schedule
- provider message ID
- structured error
- idempotency key

This prevents duplicate **logical Outbox enqueue** on browser retry/double click and avoids partial business transactions. Provider recipient delivery remains at-least-once and can duplicate after provider-accepted/worker-crash edge case.

## 3. Email History vs Security Audit

These are intentionally separate concepts.

### Email History
User-facing operational list. Keep the frozen business behavior:
- checkbox selection;
- Delete available for wrong/test records;
- email-history records must not permanently block cleanup of test business data.

### Immutable audit
Regardless of whether a user-facing Email History row is later deleted, Security/Activity Audit retains events such as:
- send requested;
- send result;
- Email History deleted;
- who performed it and when.

Therefore operational cleanup does not destroy security traceability.

## 4. Candidate notifications

After:
- Candidate creates a Submission;
- Candidate updates a NEW Submission;

→ include HR notification Outbox enqueue **inside the same Candidate Submit/Update transaction before COMMIT**. External provider delivery occurs after commit.

Recipients are configuration/master data, not hard-coded source code.

## 5. Candidate documents

Candidate document groups:
- CV — required by business form;
- Degree;
- Transcript;
- Certificate;
- Other.

Technical rules:
- private Storage bucket;
- whitelist MIME/extensions;
- per-bucket/file-size limit;
- normalized storage object key;
- metadata captured in DB;
- replacement creates a new version of the same logical document;
- no public URL persisted;
- authenticated download or short-lived signed URL only.

Production whitelist/limits are frozen: PDF, DOC/DOCX, PPT/PPTX, PNG/JPG/JPEG; max 5 files per parent; max 5 MB/file.

## 6. Interview documents

HR may upload interview/demo materials. Interviewer may preview/download only while contextual access is valid.

Candidate never receives access to internal Interview documents.

Documents are scoped to the exact Interview Session so Round 1 and Round 2 do not overwrite one another.

## 7. Preview security

Do not browser-render arbitrary active content.

Phase-1 baseline under review:
- PDF / supported image formats may preview;
- DOCX/PPTX may download or use a controlled conversion/preview flow;
- HTML, SVG, executable and archive formats are not accepted without an explicit use case/security review.

## 8. Activity/Audit events — mandatory for sensitive actions

At minimum log:
- auth success/failure where available and policy-appropriate;
- Candidate Submission create/update;
- sensitive Candidate record read where auditing is required;
- document preview/download;
- HR edit / HR Note change;
- status change;
- Application create/update/delete/inactive;
- Interview create/copy/schedule/status/delete/inactive;
- participant add/remove/reorder/restore;
- Interviewer report save/edit;
- HR editing an Interviewer report;
- Final Decision block change;
- permission grant/revoke;
- Candidate/Internal User active/inactive;
- Root Admin actions;
- PDF generation/download;
- email enqueue/send/failure/history deletion;
- conflict override/confirmation when the business rule permits an override.

Audit log is append-only and is not treated as a business usage reference for the hard-delete/inactive rule.

## 9. Audit metadata

Recommended:
- `request_id`
- `correlation_id`
- actor IDs/type
- source
- reason where relevant
- old/new values with sensitive-field redaction policy
- optional `ip_hash` / `user_agent` if approved by privacy policy

Never store passwords, OTPs, refresh tokens, OAuth provider tokens, secret keys, or signed URLs as audit payloads.


## Document, email-delivery and privacy controls
- Candidate/Interview document limits: approved PDF/Word/PPT/PNG/JPEG; max 5 files per parent; max 5 MB/file.
- Upload uses reserve/finalize two-phase flow; abandoned temp objects are cleaned asynchronously.
- System email recipients are allowlisted/derived by email type. Phase 1 system emails have no attachments; any future attachment feature requires immutable document-version references and an explicit allowlist.
- Email Outbox delivery is at-least-once with best-effort deduplication, leased worker claims and stale-SENDING recovery.
- Privacy notice acknowledgement version/timestamp is persisted per Submission.

## Phase 1 email and Candidate-document behavior
- **Phase 1 system emails do not support attachments.** Preview fields are To/CC (where applicable), Subject and Body only.
- Delivery semantics are at-least-once with idempotent enqueue + best-effort deduplication; acceptance criteria must not claim guaranteed no duplicate after provider-accepted/worker-crash edge case.
- Candidate file changes during Edit are staged in a Candidate Form Session; Save atomically applies text + document versions, Cancel leaves persisted documents untouched and cleans pending temp objects.
- New Candidate Form uploads are associated with form/upload session, not a nonexistent Submission ID.
- External legacy Office formats are allowed by owner decision, therefore malware scanning is a go-live requirement before finalization/download exposure.


## Candidate notification transaction rule
Candidate Submit and Candidate Update both create one idempotent logical HR notification linked to exact `submission_id`. Candidate mutation rate limits run before mutation; notification delivery throttling must not roll back an otherwise valid Save.

## Email History authorization and cleanup
Email History has a separate `emails.history_view` permission. Read/delete always also requires parent contextual authorization derived from `email_type`; knowing an ID is not authorization. Delete requires `emails.history_view + emails.history_delete` and one accepted cleanup classification: `TEST_RECORD` only for `environment_code=TEST`, or `WRONG_RECORD` with mandatory reason text. The cleanup classification/reason is written to immutable Security Audit before the operational history row is removed.



---

<!-- SOURCE: 12_IMPLEMENTATION_NOTES_VERCEL_SUPABASE.md -->

> Current technical source-of-truth is determined by `source_registry.yaml`; do not stop at a remembered numeric file range.

# 12. Implementation Notes – Vercel + Supabase

> Tài liệu này là summary. Technical source-of-truth chi tiết nằm ở `37`–`50`.

## Stack target

- Next.js App Router on Vercel.
- Supabase Postgres + Auth + Storage.
- `@supabase/ssr` cho cookie-based auth trong Next.js.
- Server Components mặc định; Client Components chỉ cho interaction cần JS.

## Auth

Internal:
- Google Workspace OAuth only;
- `@eiu.edu.vn`;
- phải map tới active `app_users`.

Candidate:
- verified email identity; email immutable;
- Candidate production auth method: **Email OTP code**; Internal: Google Workspace OAuth only.

## Data access

- RLS all exposed business tables.
- explicit GRANT/REVOKE.
- publishable key browser-safe; secret/service-role server-only.
- server-side secret calls vẫn phải tự authorize.
- complex helpers `SECURITY DEFINER SET search_path=''`, private schema, restricted execute.

## Mutations

Không để browser tự orchestration nhiều writes. Dùng transactional commands/RPC từ authenticated Server Actions.

## Views

Current Round / outcome / final decision implementation views không expose trực tiếp mặc định; đặt `private` hoặc `security_invoker` + grants/RLS khi thật sự cần.

## Storage

Private buckets, Storage RLS, MIME/size policy, authenticated/short-lived preview. Không dùng public URL cho recruitment documents.

## Vercel/React

- authenticate Server Actions như API routes;
- avoid request waterfalls; parallel independent reads;
- minimize client serialization/bundle;
- server-side pagination/search;
- filters/page/sort nên deep-link qua URL;
- preview deploy before production.

## Deployment

- local / staging / production tách biệt;
- Vercel preview có thể map Supabase preview branch nhưng phải chạy grant/RLS/trigger smoke tests;
- production PII không seed sang preview.

## Production readiness

Chưa production-ready cho tới khi pass `45_PRODUCTION_UAT_GATE.md` và owner decisions ở `50_OWNER_DECISIONS_PENDING.md` được đóng.


## Server-side implementation requirements
- Pin Next.js/Supabase package versions and commit lockfile; auth upgrade regression in CI.
- Shared schedule RPCs use mandatory transaction advisory/resource locks before conflict recheck.
- Search uses server pagination + normalized/indexed fields (`pg_trgm`/normalized strategy), not whole-table browser filtering or unrestricted `%ILIKE%`.
- Private Storage only; reserve/finalize upload protocol.
- Never expose secret/service-role credential to browser; every privileged server path re-authorizes business permission/context.

## Form-session and lifecycle implementation additions
- Candidate pre-submit/edit file state must not be stored in mutable process memory; use persisted short-lived Form Session/Storage reservation.
- Internal Google first-login binding is an authenticated transactional provisioning command, not directory edit.
- Search terms containing PII must not be put into shareable URLs; use controlled request/server action state.
- Pin Supabase SSR/auth dependencies and lockfile; include first-bind and session authorization regression tests.
- Malware scan is mandatory before promoting candidate DOC/PPT/PDF/image uploads to final private objects.



---

<!-- SOURCE: 13_ACCEPTANCE_CRITERIA_AND_TEST_CASES.md -->

# 13. Acceptance Criteria — Business Core v1.2 + Technical Architecture v1.17

Business rules remain frozen except the explicitly accepted Final Decision timestamp correction. Technical architecture remains under Technical Closure Gate.

## A. Candidate / Auth

**AC-01 Verified email** — Candidate email comes from verified Auth identity and is not editable through Candidate/HR profile UI.

**AC-02 New Submission** — Each submit creates a new Submission snapshot.

**AC-03 Candidate inactive** — Candidate Inactive cannot access Portal; internal history remains.

**AC-04 Candidate edit** — Candidate can edit only when Candidate Active + Submission `NEW` + version is not stale.

**AC-04T Internal auth** — Internal users authenticate with Google Workspace OAuth, use `@eiu.edu.vn`, exist in `app_users`, and are Active.

## B. Submission

**AC-05 Group** — Same Candidate displays grouped Submissions; child columns: `Ngày ứng tuyển | Trạng thái | HR Note`.

**AC-06 Mark New** — Only when there is no active Application.

**AC-07 Bulk Mark New** — All-or-nothing.

**AC-08 Derived status** — any active Application `HIRED` → `DONE`; all active Applications `REJECTED` → `CLOSED`; active non-final → `PROCESSED`. With no active Application, generic recalculation preserves manual `NEW/READ`; only a Submission coming from a derived state falls back to `READ`. Candidate Reactivate is the deliberate lifecycle exception that forces no-active-Application to `READ`.

**AC-08T Submission identity** — DB/server rejects a Submission whose email does not match its Candidate verified identity.

## C. Application

**AC-09 Identity** — durable Application identity = Submission + Khoa/Phòng + Ngành/Tổ + Vị trí and is globally unique across active/inactive history; exact same assignment reuses/reactivates the same Application ID.

**AC-10 Different identity** — Different assignment identity → different Application.

**AC-11 Exact duplicate** — warning + explicit confirmation → update existing active Application; no duplicate ID.

**AC-12 Identity history** — Application with Interview history is not rewritten into a different assignment.

**AC-12T Candidate integrity** — Application derives Candidate through Submission; no independent `candidate_id` can disagree.

**AC-12U Hierarchy integrity** — Application Unit/Team must match Position hierarchy.

**AC-12H HR owner integrity** — HR owner must be Active and HR-eligible/root according to the permission model.

## D. Interview rounds

**AC-13 Multiple rounds** — One Application supports multiple Interview Sessions in Phase 1.

**AC-14 Round 1** — New Application creates Round 1 with default schedule/report statuses.

**AC-15 Demo Topic** — belongs to Interview Session; each new round begins blank.

**AC-16 Latest round lifecycle** — only latest existing round may Delete/Inactive.

**AC-17 Latest inactive** — latest inactive blocks creating a subsequent round.

**AC-18 No renumber** — historical round numbers are never renumbered.

**AC-18T Round allocation** — concurrent next-round requests cannot create duplicate `round_no`.

## E. Schedule

**AC-19 Manual status** — Save/email does not auto-change schedule status.

**AC-20 CONFIRMED lock** — schedule details cannot be edited while `CONFIRMED`; HR changes status first.

**AC-21 Interviewer conflict** — active, non-cancelled Interviewer overlap blocks Save.

**AC-22 Room conflict** — active, non-cancelled Room overlap blocks Save.

**AC-22C Candidate conflict** — BLOCK overlapping `resource_blocking` sessions of the same Candidate.

**AC-23 Copy** — Copy creates a new editable schedule context; Demo Topic is blank; server conflict check occurs before commit.

## F. Participants

**AC-24 Order** — current `participant_order` is unique within the session and drives PDF/display order.

**AC-25 Snapshot** — name/job title/email history remains unchanged when User Directory changes.

**AC-26 Remove/re-add** — remove with report warns; removed participant loses access/current PDF. Re-add offers Restore old report or Create new.

**AC-26T Report ownership** — active Interview Report must reference an Interview Participant; a non-participant cannot own a report.

## G. Report

**AC-27 One row/Application** — HR Report page uses Current Active Latest Round.

**AC-28 PDF Current Round** — Preview/PDF uses Current Round only; prior rounds remain history.

**AC-29 Separate reports** — each Participant has an independent report.

**AC-30 No scoring** — no star, score, rating, pass percentage, or competency scale.

**AC-31 Final Decision source** — panel normally agrees and one representative fills the 3 final fields. Current source is the eligible report with newest `decision_updated_at`, not generic `updated_at`.

**AC-32 Decision timestamp** — only changes to `Conclusion`, `Expected Specific Job Assigned`, or `Expected Recruitment Time` update `decision_updated_at`/`decision_updated_by`.

**AC-33 Qualitative edit isolation** — editing one of the 5 qualitative fields does not change Final Decision Source.

**AC-34 Whole decision block** — all three final fields are read from the same source report; never merge across Interviewers.

**AC-35 Fallback** — if current source clears all three final fields, fall back to the next eligible report if one exists.

**AC-36 Interviewer final lock** — `HIRED`/`REJECTED` prevents Interviewer edit until HR changes status away.

**AC-37 HR edit Interviewer report** — only with `reports.edit_interviewer`.

**AC-38 Field-aware concurrency** — HR/Interviewer different-field edits preserve both; same-field conflict resolves to Interviewer; stale HR reloads; no stale whole-row overwrite.

## H. Permissions / Security

**AC-39 Exactly one Root after bootstrap** — cannot create a second Root; existing Root cannot ordinary demote/inactive/delete.

**AC-40 HR granular permissions** — HR role alone does not authorize every action.

**AC-41 Permission assignment** — only Root Admin grants/revokes HR permissions.

**AC-42 Interviewer contextual** — must be current Participant + visible + Active user/session; backend/RLS denies otherwise.

**AC-43 RLS and GRANTs** — exposed business tables have RLS and explicit grants; frontend-hidden controls are not security boundaries.

**AC-44 View security** — derived views are private by default; exposed views must use safe invoker/grant strategy and pass role tests.

**AC-45 Secret isolation** — no Supabase secret/service-role key is shipped to browser; privileged server use still performs authorization.

## I. Delete / Inactive

**AC-46 Unused Candidate / empty Interview-owned default** — hard delete remains only where the current delete matrix explicitly permits it. A successfully submitted production Submission is retention-managed and is not a normal HR hard-delete target.

**AC-47 Used** — business history exists → inactive.

**AC-48 Audit does not block cleanup** — Activity/Audit Log alone does not turn an otherwise-unused business record into “used”.

**AC-49 Audit immutable** — business Email History may be removed per frozen rule, but immutable audit records of actions are not mutable/deletable through application UI.

## J. Idempotency / transactions

**AC-50 Atomic commands** — multi-side-effect mutations execute as one server/RPC transaction or equivalent atomic command boundary.

**AC-51 Idempotency** — retries/double-clicks do not duplicate Submission/Application/Round/email enqueue/document finalization/persisted PDF job where applicable.

**AC-52 Structured errors** — backend returns stable business/technical error codes for expected conflicts and stale state.

## K. Files / email / operations

**AC-53 Private files** — candidate/interview documents are stored privately; authorization is enforced for each access.

**AC-54 Upload policy** — server accepts only PDF/DOC/DOCX/PPT/PPTX/PNG/JPG/JPEG with signature/MIME validation; max 5 MB/file, max 5 current files/parent, current CV required, malware `CLEAN` mandatory, and active content is not arbitrarily browser-rendered.

**AC-55 Email outbox** — business transaction commits before external delivery. Browser/double-click/request retry with the same idempotency scope/key must not create duplicate logical Outbox rows. Provider delivery is at-least-once; duplicate recipient delivery after provider-accept/worker-crash is possible and must be observable/audited.

**AC-56 Timezone** — timestamps use `timestamptz`; UI business display uses `Asia/Ho_Chi_Minh`; date-only values do not undergo timezone conversion.

**AC-57 Candidate mobile** — Candidate Login/Form/Phiếu của tôi must pass mobile UAT before production go-live.

## L. Production gate

Production go-live additionally requires the checklist in `45_PRODUCTION_UAT_GATE.md`, including finalized RLS/GRANTs, Auth, upload limits, privacy/retention, backups/restore, monitoring, email provider, mobile Candidate Portal, and official PDF template if PDF is used operationally.


## Technical acceptance — authorization, concurrency and platform integrity
1. View-only HR opens NEW Submission → remains NEW; default/full HR opens → READ.
2. Candidate cannot edit READ; HR can Mark New and Candidate can then edit.
3. Bound user identity cannot be rebound by `users.directory_manage`; unbound email typo can be corrected.
4. Interview Note and HR Report Note persist separately; Interviewer can never retrieve HR Report Note.
5. Two concurrent conflicting schedule saves cannot both commit. Test Candidate, Room and Interviewer races.
6. Add/re-add participant to scheduled session blocks conflicting Interviewer. Reactivate/CANCELLED→active blocks conflicts.
7. Candidate first OTP login provisions exactly one Candidate; recreated Auth identity with same verified email does not duplicate.
8. Application create uses selected Submission ID, never implicit latest.
9. Position with NULL Team rejects Application carrying any Team.
10. Parent Application inactive makes child Interview `access_active=false` for current-view/RLS/conflict.
11. Empty auto-created Round 1 can be cascaded in unused Application hard-delete; any meaningful history prevents hard-delete.
12. Candidate patch rejects HR/system fields.
13. Upload rejects >5 MB, 6th current file, and unapproved MIME/signature.
14. Outbox worker duplicate/retry test demonstrates no exactly-once assumption; provider duplicate possibility is documented/audited.
15. Privacy acknowledgement records exact notice version.
16. Status token contrast passes WCAG AA target for normal 16px text.
17. Package consistency validator fails if a source parser unexpectedly returns zero expected permissions/fields.

## Technical acceptance — form sessions, documents and lifecycle
- **AC-UP-01:** Candidate can upload required CV before Submission exists using an open form session; Submit atomically creates Submission and binds CLEAN staged files.
- **AC-UP-02:** Candidate stages replace/delete then presses Cancel → persisted current file/version is unchanged.
- **AC-UP-03:** A staged ADD/REPLACE whose reservation is not `VALIDATED` + malware `CLEAN` cannot be committed by Submit/Save.
- **AC-UP-04:** Effective Candidate documents after applying pending ADD/REPLACE/DELETE cannot exceed 5 current files and must retain at least one current CV.
- **AC-UP-05:** NEW_SUBMISSION cannot stage REPLACE/DELETE; one upload reservation cannot back two staged document mutations; one target logical document cannot have two simultaneous pending mutations in one form session.
- **AC-UP-06:** Candidate starts upload while NEW, HR opens it to READ before Save → finalize/Save re-check blocks Candidate mutation.
- **AC-STAT-01:** HR may manually set only NEW/READ; direct PROCESSED/DONE/CLOSED request is rejected.
- **AC-STAT-02:** two concurrent Application outcome changes on same Submission serialize on parent lock and final derived status is correct.
- **AC-SCH-09:** concurrent reschedule vs add participant cannot create hidden Interviewer conflict because Interview row is locked before participant snapshot/resource locks.
- **AC-AUTH-04:** first Google login of active allowlisted unbound internal user atomically binds matching verified EIU identity; conflicting existing binding rejects.
- **AC-MASTER-03:** referenced Position structural reassignment is rejected; create-new/inactivate-old path succeeds.
- **AC-FMT-04:** historical Interview using later-inactivated format can still be cancelled/reactivated under lifecycle rules; inactive format cannot be newly selected.
- **AC-COPY-03:** copy to another Application fills structurally empty default Round 1; otherwise creates next round.
- **AC-GRP-01:** Candidate Inbox pagination never splits one Candidate's child submissions across different parent pages.
- **AC-EMAIL-04:** Phase 1 email preview/send contains no file attachments. Provider accepted + worker crash scenario is documented as possible duplicate under at-least-once delivery.
- **AC-PRIV-03:** privacy acknowledgement is bound to Submission; Candidate identity derives through Submission, no redundant mismatched candidate_id.
- **AC-DS-05:** HR Report table declared min-width equals sum of frozen columns; validator fails on mismatch.

## Technical acceptance — identity, reactivation and command coverage
- **AC-CAND-REACT-01:** Candidate inactive with Submission `NEW` and no active Application → Reactivate Candidate → Submission becomes `READ`.
- **AC-CAND-REACT-02:** Candidate inactive with active in-progress Application → Reactivate → `PROCESSED`; effective HIRED → `DONE`; all rejected → `CLOSED`.
- **AC-DOC-HR-01:** HR file-only Submission document Save increments aggregate `Submission.version_no` exactly once; a second edit session on the old version fails `STALE_VERSION`.
- **AC-DOC-HR-02:** HR cannot delete the only effective current CV or create >5 effective current files.
- **AC-EMAIL-05:** Client/API retry with same idempotency scope does not duplicate logical enqueue; provider-level duplicate after accepted-send/worker-crash is permitted and audited.
- **AC-USR-ACT-01:** `users.directory_manage` may Active/Inactive a non-HR internal user.
- **AC-USR-ACT-02:** non-root HR cannot deactivate an HR-role target.
- **AC-USR-ACT-03:** Root Admin cannot be deactivated; HR self-deactivation through normal UI is rejected.
- **AC-AUTH-05:** Candidate recreated Auth identity with same verified email safely rebinds exactly one existing Candidate under row lock; conflicting identity evidence rejects.
- **AC-PRIV-04:** Candidate Form Session pins a server-published Privacy Notice version; client cannot acknowledge an arbitrary/unpublished version.
- **AC-EMAIL-06:** Candidate Submit/Update notification Outbox/History is relationally linked to the exact `submission_id`.
- **AC-APP-REACT-04:** exact durable Application identity cannot exist twice. Create/assignment lookup for the same identity resolves the existing Application; if it is inactive, Reactivate that same row. Database global uniqueness prevents active/inactive duplicates.
- **AC-APP-REACT-05:** Application Reactivate revalidates every non-elapsed child Interview that would become `reactivation_conflict_relevant = resource_blocking AND end_at > transaction_now`; fully elapsed past-only overlaps do not block reactivation. Any still-relevant Candidate/Room/Interviewer conflict blocks entire reactivation. Current Round only selects report/outcome.
- **AC-MASTER-04:** referenced Room identity-bearing fields cannot be structurally repurposed; create-new/inactivate-old path succeeds.
- **AC-DEL-03:** hard-delete with OPEN Candidate Form Session first durably records temp Storage cleanup, cancels session, then deletes; cleanup-capture failure blocks delete.
- **AC-CMD-01:** every production UI mutation maps to an entry in `command_registry.yaml`, contract text and at least one acceptance identifier.



## Semantic acceptance — canonical state, privacy and identity
- **AC-STAT-03:** `NEW` + no active Application + generic recalc → `NEW`.
- **AC-STAT-04:** `READ` + no active Application + generic recalc → `READ`.
- **AC-STAT-05:** derived status + final active Application removed/inactivated → `READ`.
- **AC-PRIV-EDIT-01:** EDIT Form Session pins current/effective Privacy Notice and Save requires acknowledgement.
- **AC-PRIV-EDIT-02:** same notice version already acknowledged → idempotent, no duplicate acknowledgement.
- **AC-PRIV-EDIT-03:** new pinned notice version during later EDIT → exact version appended to acknowledgement history.
- **AC-PRIV-EDIT-04:** arbitrary/unpublished version rejected; no current/effective notice → `PRIVACY_NOTICE_UNAVAILABLE`.
- **AC-CAND-UPD-EMAIL-01:** Candidate Update creates one logical exact-Submission Outbox notification under idempotency replay.
- **AC-CONC-DOC-01:** file-only Save bumps Submission version exactly once; stale parallel session fails `STALE_VERSION`.
- **AC-CACHE-01:** latest Candidate/HR edit refreshes Candidate cache; older edit does not.
- **AC-CACHE-02:** MAINTENANCE_ONLY repair-delete of a non-production/legacy unused latest Submission refreshes cache to the next surviving snapshot or clears it; this is not normal HR production behavior.
- **AC-PART-RESTORE-01:** RESTORE_OLD_REPORT restores Participant current state + unarchives same Report and preserves decision source metadata.
- **AC-PART-RESTORE-02:** CREATE_NEW_REPORT leaves old history archived and creates new current Participant/report.
- **AC-APP-ID-01:** durable Application identity is globally unique across active/inactive rows.
- **AC-ACCESS-01:** inactive parent Application revokes Interviewer contextual access.
- **AC-RESOURCE-01:** non-current active/non-CANCELLED scheduled Interview still blocks resource overlap.
- **AC-PRIV-IMM-01:** published Privacy Notice content/hash/effective metadata cannot mutate; new content requires new version.

## Source-governance and lifecycle acceptance
- **AC-PRIV-SESSION-01:** starting NEW or EDIT Candidate Form Session server-selects exactly one current/effective Privacy Notice (`is_current=true`, `effective_from<=now()`), pins it in the session, and fails `PRIVACY_NOTICE_UNAVAILABLE` when none exists.
- **AC-CAND-DEL-SESSION-01:** hard-delete of an unused Candidate with OPEN form/temp uploads first durably captures cleanup paths, cancels sessions/reservations, then deletes; failed cleanup capture blocks delete.
- **AC-USR-DEL-01:** Internal User hard-delete is not exposed in normal HR UI; Root maintenance cleanup is eligible only for unbound, non-HR, non-Root, never-referenced rows.
- **AC-APP-ID-02:** identity fields of an existing Application are immutable even before Interview history; changing assignment resolves/creates another durable Application instead.
- **AC-NOTIFY-01:** Candidate Update rate limiting applies to the Candidate mutation endpoint; system HR-notification throttling/coalescing must not roll back an otherwise valid Candidate Save.
- **AC-PRIV-CURRENT-01:** published/effective Privacy Notice lookup fails closed when the current pointer is missing, future-dated, or otherwise unavailable.

## Behavior-specific acceptance — command ownership and adversarial integrity
- **AC-REPORT-STATUS-01:** exactly one trusted command, `change_report_status`, writes `interviews.report_status_code`; HR-note command cannot write status.
- **AC-REPORT-STATUS-02:** every successful Report Status change locks Current Round/parent Submission and recalculates Submission before commit.
- **AC-REPORT-STATUS-03:** stale/non-current-round Report Status mutation is rejected.
- **AC-HR-NOTE-01:** `update_hr_report_note` changes only `hr_report_note`; Interviewer cannot retrieve it and no Submission recalc occurs from note-only edit.
- **AC-DOC-TARGET-01:** staged Candidate REPLACE requires target logical document to have exactly one current version.
- **AC-DOC-TARGET-02:** staged Candidate DELETE requires target logical document to have exactly one current version.
- **AC-DOC-TARGET-03:** historical/no-current logical target cannot be resurrected or bypass max-five current-file invariant.
- **AC-DOC-TARGET-04:** if a valid staged target loses/changes its current version before Save, Save fails `INVALID_DOCUMENT_TARGET` with no materialization.
- **AC-EMAIL-HIST-01:** Email History SELECT/DELETE requires `emails.history_view` plus exact parent contextual read; cross-context ID access is denied.
- **AC-EMAIL-HIST-02:** Delete requires `emails.history_delete` and deterministic cleanup classification: TEST only for TEST environment; WRONG requires mandatory reason; immutable audit persists.
- **AC-OWNER-LIFE-01:** an Application cannot be activated/reactivated with an ineligible HR owner; same transaction may reassign to eligible owner.
- **AC-OWNER-LIFE-02:** HR deactivation/HR-role removal is blocked while Active Applications remain owned unless reassigned atomically.
- **AC-APP-REACT-PAST-01:** fully elapsed historical schedule overlaps do not block Application Reactivate; non-elapsed conflicts still block atomically.
- **AC-PRIV-PUBLISH-01:** future-effective Privacy Notice is published non-current; current pointer switches at/after effective time in one transaction without an unintended no-current/effective gap.
- **AC-CAND-INACTIVE-01:** Candidate inactive sets `inactive_at/by`; reactivate clears them; immutable audit preserves lifecycle history.
- **AC-REPORT-LIFE-01:** Interview Report lifecycle permits only current `(active=true, archived=false)` or historical `(active=false, archived=true)` states.
- **AC-PERM-VIEW-01:** non-root Directory Manager cannot view another user's granular effective permissions; Root can, and a user may view own effective permissions.


## Batch, state and invariant acceptance
- **AC-STAT-MANUAL-READ-01:** any active Application + manual `READ` request is rejected; authoritative derived status remains unchanged.
- **AC-STAT-MANUAL-NEW-01:** any active Application + manual `NEW` request is rejected.
- **AC-STAT-MANUAL-NOAPP-01:** with no active Application, manual `NEW/READ` remains permitted subject to permission/version rules.
- **AC-BULK-01:** every visible Phase-1 lifecycle/status bulk action maps to one named batch command with declared atomicity; browser loops over single-row commands are not the production contract.
- **AC-MASTER-ACTIVE-01:** new/changed Unit/Team/Position/Room/Qualification/Source/Reason references require active master rows; unchanged historical inactive references remain valid.
- **AC-PART-ACTIVE-01:** re-adding an inactive Internal User is rejected; normal deactivation is blocked while that user remains a current participant on a non-elapsed resource-blocking Interview.
- **AC-FORM-OWNER-01:** Candidate Form EDIT session cannot target another Candidate's Submission.
- **AC-PRIV-DELETE-01:** published Privacy Notice cannot be normally deleted.
- **AC-ROUND-EMPTY-01:** Copy and unused-Application delete use the same `private.is_structurally_empty_default_round()` predicate.
- **AC-PART-LIFE-01:** current Participant implies `removed_at IS NULL`; removed historical Participant implies `removed_at IS NOT NULL`.
- **AC-CAND-EMAIL-01:** Candidate verified email cannot be modified by normal profile/business mutation.


## Targeted review acceptance
- **AC-PERM-INT-STATUS-01:** HR with `interviews.manage` but without `interviews.status` cannot execute single Interview Schedule Status change (`FORBIDDEN`).
- **AC-PERM-INT-STATUS-02:** The same actor cannot execute `bulk_change_interview_schedule_status`; no selected Interview mutates.
- **AC-PERM-INT-STATUS-03:** `interviews.status` + prerequisite `interviews.view` authorizes equivalent single/bulk Schedule Status transitions, subject to the same state/conflict rules.
- **AC-FORM-EXP-01:** Form Session row still says `OPEN` but `expires_at <= transaction_now` → Stage/Save/Submit/Finalize fail `FORM_SESSION_EXPIRED`; cleanup timing cannot make it temporarily valid.
- **AC-UP-EXP-01:** ADD/REPLACE reservation still says `VALIDATED/CLEAN` but `expires_at <= transaction_now` → Stage/Save/Submit/Finalize fail `UPLOAD_RESERVATION_EXPIRED` (or the canonical expiry error wrapper) with no materialization.
- **AC-FORM-LIFE-01:** Only `OPEN → SUBMITTED`, `OPEN → CANCELLED`, `OPEN → EXPIRED` persist; terminal sessions never reopen and lifecycle transitions update timestamp/audit evidence.
- **AC-OPEN-SUB-01:** `submissions.view` without `submissions.status` can open a NEW Submission as pure read; status remains NEW.
- **AC-OPEN-SUB-02:** `submissions.view + submissions.status` opening NEW performs the one conditional NEW→READ mutation atomically.
- **AC-STAT-INACTIVE-01:** Candidate Inactive with latest Submission NEW/READ and no active Application remains eligible for single manual NEW/READ by authorized HR.
- **AC-STAT-INACTIVE-02:** The same Candidate is equally eligible inside Candidate-level bulk manual NEW/READ; Candidate inactivity alone must not abort the batch.
- **AC-PROT-EDU-01:** Prototype Education requiredness/min-items does not exceed Validation Contract; current Phase 1 allows zero rows and does not mark the four Education fields required.
- **AC-PRIV-NEW-UI-01:** NEW_SUBMISSION Privacy acknowledgement is unchecked on initial render and must be explicitly selected before Submit.
- **AC-REPORT-AUTH-01:** Interviewer may save only own report under current participant context; HR branch requires both `reports.view` and `reports.edit_interviewer`; pseudo-permission strings are not implementation authority.


## Lifecycle reachability + scheduling/copy acceptance
- **AC-PART-OPER-01:** Unscheduled Interview with an inactive current Participant cannot be scheduled; fail `CURRENT_PARTICIPANT_INACTIVE_REASSIGN_REQUIRED` before conflict commit.
- **AC-PART-OPER-02:** CANCELLED Interview with an inactive current Participant cannot transition to an operational schedule status.
- **AC-PART-OPER-03:** Inactive Application cannot reactivate a non-elapsed child Interview into operational state while any current Participant user is inactive.
- **AC-PART-OPER-04:** When every current Participant is active, normal Candidate/Room/Interviewer conflict locking/checks execute; adjacent `[start,end)` boundaries remain allowed.
- **AC-SUB-DEL-REACH-01:** Normal successful production Candidate Submit creates retained exact-Submission PRODUCTION email trace; `delete_unused_submission` is therefore classified MAINTENANCE_ONLY/not normal HR production capability. Maintenance delete must still reject retained production usage.
- **AC-SCH-SRC-01:** Normal schedule Save blocks Candidate, Room and Interviewer overlap, ignores CANCELLED/access-inactive/no-interval rows, and allows `end=start` adjacency.
- **AC-STAT-LATEST-01:** single manual Submission status mutation resolves and verifies deterministic latest Submission; historical child Submission cannot be mutated by a crafted exact-ID request.
- **AC-RP-COPY-01:** Copy to another Application fills structurally empty target Round 1; otherwise creates next legal round. Initial draft copies schedule/logistics and leaves Demo Topic blank.
- **AC-ROUND-PROV-01:** Round with outgoing or incoming Copy provenance is business-used for structural-empty/delete purposes and never falls through to an unexpected raw FK delete error.

## Cross-layer acceptance — Education, exact Submission identity and participant eligibility — Education, exact Submission identity and participant eligibility
- **AC-EDU-DB-01:** `validation_contract.yaml` Education `required_fields=[]` is reflected physically: zero rows and partially populated Education rows permitted by the contract persist without a DB `NOT NULL` contradiction.
- **AC-EDU-DB-02:** `submission_education` business columns `period_text`, `qualification_id`, `major`, `institution` remain nullable until/unless a future frozen Validation Contract explicitly adds per-row requiredness.
- **AC-PROTO-SUBSEL-01:** production-intent Application assignment UI uses exact `SubmissionSelector`; selected value is `submission_id`, never Candidate ID or implicit latest.
- **AC-PROTO-SUBSEL-02:** two Submissions from the same Candidate render as two distinct choices with Candidate name, verified email, submitted date and Submission status.
- **AC-PART-OPER-CREATE-01:** Create resource-blocking Interview with any selected inactive Internal User → `CURRENT_PARTICIPANT_INACTIVE_REASSIGN_REQUIRED`; no Interview is created.
- **AC-PART-OPER-COPY-01:** Copy schedule whose prefilled/selected Participant set contains an inactive Internal User → `CURRENT_PARTICIPANT_INACTIVE_REASSIGN_REQUIRED`; no target Round is created/filled.
- **AC-STAT-LATEST-SQL-01:** starter SQL manual-status helper locks Candidate, resolves deterministic latest Submission, verifies expected latest ID/version, and cannot mutate a historical child Submission by exact ID.
- **AC-USR-LIFE-REG-01:** `set_internal_user_active` machine registry declares both Active-Application owner reassignment guard and non-elapsed resource-blocking current-Participant reassignment guard.

## Cross-layer acceptance — nullable Education, bulk schedule parity, source coherence
- **AC-EDU-NULL-01:** Education row with `qualification_id=NULL` and another optional Education field populated is accepted; NULL skips active-master qualification validation.
- **AC-EDU-NULL-02:** Education row with a non-null inactive `qualification_id` is rejected with `INACTIVE_QUALIFICATION_NOT_SELECTABLE`.
- **AC-EDU-NULL-03:** An unchanged historical inactive non-null qualification remains readable/operable; the active-master guard applies only to INSERT or changed non-null selection.
- **AC-PART-OPER-BULK-01:** if any selected CANCELLED/dormant Interview would become resource-blocking while a current Participant is inactive, `bulk_change_interview_schedule_status` aborts the entire batch with `CURRENT_PARTICIPANT_INACTIVE_REASSIGN_REQUIRED`; no selected Interview mutates.
- **AC-BULK-SCH-01:** bulk Interview schedule-status mutation is ALL_OR_NOTHING across transition validation, Active-Participant eligibility and resource conflicts; one failure rolls back every selected Interview.
- **AC-SCH-CANDIDATE-BULK-01:** a same-Candidate overlap in any selected Interview blocks the whole schedule-status batch.
- **AC-SCH-ROOM-BULK-01:** a Room overlap in any selected Interview blocks the whole schedule-status batch when the format uses a Room.
- **AC-SCH-INTERVIEWER-BULK-01:** an Interviewer overlap in any selected Interview blocks the whole schedule-status batch.
- **AC-REACT-CANON-01:** Application Reactivate evaluates only non-elapsed children satisfying `reactivation_conflict_relevant`; fully elapsed historical intervals never block lifecycle recovery.
- **AC-SOURCE-BASELINE-01:** all CURRENT machine baseline declarations resolve to Full/Technical v1.17, Design v1.8 and Responsive v1.10, while historical versions are allowed only in explicitly historical/changelog evidence.
- **AC-RESP-AUTH-01:** Responsive `README.md` and `VERSION.md` both declare Responsive v1.10 authority against Full Handover v1.17 + Design System v1.8.


## Targeted acceptance additions — current
- **AC-INT-UP-FK-01:** Interview Upload Reservation with nonexistent `interview_id` is rejected by the physical FK; FK uses `ON DELETE RESTRICT`.
- **AC-INT-UP-DEL-01:** hard-delete Interview with temp/nonterminal Upload Reservation first durably records bucket/path in `storage_cleanup_queue`, then cancels/removes reservation; no orphan reservation/object is possible.
- **AC-INT-UP-DEL-02:** failure to persist any required temp-object cleanup intent aborts Interview hard-delete.
- **AC-BULK-CAND-LIFE-01:** Bulk Candidate Active/Inactive writes `is_active + inactive_at + inactive_by` atomically for every selected Candidate; one stale/ineligible item rolls back all.
- **AC-BULK-CAND-LIFE-02:** Bulk Candidate Reactivate applies the same per-Submission reactivation recalculation as single Candidate and records per-Candidate + batch audit.
- **AC-BULK-INT-DEL-01:** Bulk Interview delete/inactivate prevalidates all selected Interviews and all hard-delete temp-cleanup prerequisites before mutation; one failure leaves every selected Interview unchanged.
- **AC-BULK-REPORT-01:** Bulk Report Status re-resolves Current Round/versions for every selected Application; one stale/current-round mismatch rolls back all and successful commit recalculates all affected parent Submissions.
- **AC-CRIT-QA-01:** both Interview Schedule Status critical controls (single and bulk) map to named browser QA assertions; validation fails if either control lacks executable evidence in the current Owner-UAT prototype.
- **AC-INT-EMAIL-WS-01:** Internal User email must match the exact `@eiu.edu.vn` domain and the local part may not contain whitespace; lookalike/subdomain/suffix forms remain rejected.

## Implementation governance / Copy-command acceptance

- **AC-GATE-SEQ-01:** Technical Specification Freeze is a semantic/source gate before coding; production migrations/RLS/RPC/race/storage/performance/backup/deployment evidence is required at Implementation Validation/Migration Freeze after implementation exists, not both before and after Technical Freeze.
- **AC-COPY-CMD-01:** Copy draft performs no DB mutation; Save Copy maps to exactly `copy_interview_schedule`, which atomically selects/fills the target Round, records provenance, applies Active-Participant and Candidate/Room/Interviewer conflict guards, is idempotent, and audits.
- **AC-SOURCE-RESP-VERSION-01:** CURRENT scope/design/prototype authority declares Full/Technical v1.17 + Design v1.8 + Responsive Prototype v1.10; stale current v1.9/v1.12/v1.15 authority assertions are forbidden outside historical/changelog context.
## Source-sync / critical Copy evidence

- **AC-COPY-ENGINE-01:** `copy_interview_schedule` is declared as a user of the canonical shared Candidate/Room/Interviewer schedule-conflict engine in command contract, structured app spec and concurrency spec.
- **AC-RP-COPY-USED-01:** Save Copy to another Application whose default Round1 is already business-used creates the next legal round, preserves existing Round1 and records Copy provenance.
- **AC-CRIT-COPY-QA-01:** every `INTERVIEW-COPY-SAVE.browser_qa` ID resolves to a current Responsive Browser QA result; unresolved QA IDs fail package validation.
- **AC-ALLINONE-LABEL-01:** generated All-in-One header and validator expectation match current Full Handover v1.17; stale generated current-version labels are forbidden.



---

<!-- SOURCE: 14_SCOPE_AND_OPEN_ITEMS.md -->

# 14. Scope & Open Items — v1.17

## Business Logic
**v1.2 FROZEN.** Reopen only through Change Request or a proven contradiction.

## Design System
**v1.8 CURRENT.** Desktop foundation current; Desktop prototype must be resynced/UAT-approved. Detailed iPad/mobile design is not frozen. Candidate Portal mobile is a go-live requirement.

## Technical Architecture
**v1.17 TECHNICAL SPECIFICATION FROZEN / READY TO IMPLEMENT.** Current technical source extends through docs 97–98 and uses `source_registry.yaml` for CURRENT/HISTORICAL governance. Technical Specification Freeze is semantic/source freeze; post-coding implementation evidence is a separate gate.

## Owner decisions
Closed:
- Candidate conflict = BLOCK.
- Candidate Auth = Email OTP.
- Upload = PDF/Word/PPT/PNG/JPEG, max 5 files, max 5 MB/file.
- Current business retention = no automatic purge; capacity warning + owner-directed upgrade/archive/purge.

Official PDF pixel template is **DEFERRED** until owner supplies approved EIU template; it is not an unresolved core architecture question.

Independent Planner Review v1.0 introduced **no new HR owner decision**. v1.16 resolves gate sequencing and Copy trusted-command authority while retaining the v1.15 scheduling/storage/lifecycle fixes. The alignment is mapped in doc 97. Responsive Prototype v1.10 remains the executable visual-UAT reference against Design System v1.8 and is NOT FROZEN pending Owner Visual UAT.

## Implementation evidence required before Implementation Validation / Migration Freeze
- executable RLS/GRANT migrations + adversarial tests;
- RPC/command implementation + command coverage integration tests;
- mandatory schedule/document/concurrency race tests;
- schema migration clean-install test;
- Storage policies + two-phase upload tests;
- Auth provisioning/rebind/root-recovery tests;
- query plan/performance against NFR baseline;
- privacy publication + archive/purge runbook rehearsal;
- backup/restore rehearsal;
- responsive desktop/tablet/mobile UX/accessibility UAT using bundled Prototype v1.10 before UI visual sign-off / Production UAT.

## Future product modules — hidden in Phase 1
Dashboard; Nhu cầu tuyển dụng; Candidate Database; KPI & Reports; Offer/Approval/Onboarding automation; advanced analytics. These remain `FUTURE_HIDDEN / NOT_RENDERED` until explicitly promoted through Change Request.



---

<!-- SOURCE: 16_AI_REVIEW_AND_BUILD_PROMPT.md -->

# 16. AI Review & Build Prompt — CURRENT v1.17

Use only CURRENT normative sources from `source_registry.yaml`. HISTORICAL/SUPERSEDED review/gate files are evidence only. HISTORICAL files must never override current behavior.

## Review mode
Baseline: Business Logic v1.2 FROZEN, Design System v1.8 CURRENT, Technical Architecture v1.17 TECHNICAL SPECIFICATION FROZEN, Implementation Gate READY TO IMPLEMENT. Read core modules 01–14, current technical modules listed in `source_registry.yaml`, `73_DOMAIN_GLOSSARY_AND_CANONICAL_PREDICATES.md`, `97_INDEPENDENT_REVIEW_IMPLEMENTATION_ALIGNMENT_V1_17.md`, `78_PRIVACY_NOTICE_PUBLICATION_RUNBOOK.md`, and `98_TECHNICAL_PRECODE_GATE_V1_17.md`. Then inspect `app_spec.yaml`, `command_registry.yaml`, `database_schema.sql`, `validation_contract.yaml`, permissions/status matrices and Design System v1.8.
Current alignment resolution: `97_INDEPENDENT_REVIEW_IMPLEMENTATION_ALIGNMENT_V1_17.md`; current pre-code/implementation authorization gate: `98_TECHNICAL_PRECODE_GATE_V1_17.md`. Historical modules must never override current behavior.

Check cross-layer traceability: Actor → Permission → UI → exactly one trusted mutation command → lock/version/transaction → DB invariant → side effects → audit → behavior-specific acceptance. Flag contradiction rather than resolving it by guessing.

## Build mode
Do not invent business features. Browser code must not orchestrate multi-write business transactions or receive service secrets. Server Actions/Route Handlers/RPCs re-authenticate/re-authorize. Use RLS + explicit grants, private Storage, candidate Form Session staged files, immutable document versions, canonical interview predicates, outbox email semantics, and current Design System v1.8.

Prototype/demo persona switcher is development-only and cannot authorize production data. Official PDF layout remains deferred until owner supplies template.

Normal scheduling/resource integrity uses every `resource_blocking` Interview, **not only Current Round**. Only parent Application Reactivate uses `reactivation_conflict_relevant = resource_blocking AND end_at > transaction_now` so fully elapsed past-only overlaps do not strand lifecycle recovery. Current Round is for report/outcome/PDF selection.



---

<!-- SOURCE: 37_BACKEND_COMMAND_CONTRACTS.md -->

# 37. Backend Command Contracts — v1.12

## 1. Hard architecture rules
Every UI mutation maps to one explicit trusted backend command. The browser must not orchestrate multi-write business mutations. Commands run through authenticated Server Action/API → transactional RPC/database command.

Each command defines actor, permission, writable DTO, preconditions, lock order, idempotency, side effects, audit, output and structured error codes.

Shared requirements:
- Candidate DTO and HR DTO are separate allowlists.
- PII search values are not placed in URLs.
- Any outcome-changing command must call authoritative Submission recalculation in the same transaction.
- Any schedule-resource mutation must lock the Interview row first, then acquire deterministic resource locks and re-check conflicts.

## 2. Core error codes
`UNAUTHENTICATED`, `FORBIDDEN`, `NOT_FOUND`, `INVALID_STATE`, `VALIDATION_ERROR`, `STALE_VERSION`, `FORM_SESSION_EXPIRED`, `UPLOAD_RESERVATION_EXPIRED`, `DUPLICATE_APPLICATION`, `APPLICATION_DURABLE_IDENTITY_IMMUTABLE`, `PRIVACY_NOTICE_UNAVAILABLE`, `SCHEDULE_CONFLICT_CANDIDATE`, `SCHEDULE_CONFLICT_INTERVIEWER`, `SCHEDULE_CONFLICT_ROOM`, `LATEST_ROUND_REQUIRED`, `ROOT_ADMIN_PROTECTED`, `IDENTITY_REBIND_FORBIDDEN`, `USER_INACTIVE`, `UPLOAD_LIMIT_EXCEEDED`, `UNSUPPORTED_FILE_TYPE`, `MALWARE_SCAN_REQUIRED`, `IDEMPOTENCY_REPLAY`, `INVALID_PERMISSION_DEPENDENCY`, `INTERNAL_ERROR`.

## 3. Candidate identity and first-login provisioning
### `provision_candidate_identity()`
Verified Candidate OTP session only. Normalize verified email → find by current `auth_user_id` → trusted fallback by verified email → create Candidate if absent → safe bind if unbound → block inactive Candidate → audit. Never create a duplicate Candidate solely because Supabase Auth user ID was recreated.

### `start_candidate_form_session(mode, submission_id?)`
Creates short-lived `candidate_form_session`. Server selects the single published Privacy Notice where `is_current=true AND effective_from<=now()` and pins its `notice_version` into `presented_privacy_notice_version`; if none is available, fail closed with `PRIVACY_NOTICE_UNAVAILABLE`. `NEW_SUBMISSION` has no Submission parent and `base_submission_version_no=NULL`. `EDIT_SUBMISSION` requires owner + Active Candidate + Submission `NEW`, stores non-null base Submission version. Session creation is audited and never trusts a client-supplied notice version.

### `cancel_candidate_form_session()`
Marks an `OPEN` unexpired session `CANCELLED` and schedules temp-object cleanup. No persisted Submission/file version is changed. `SUBMITTED`, `CANCELLED` and `EXPIRED` are terminal and cannot reopen.

### Candidate Form Session authoritative lifecycle
Canonical transitions are `OPEN → SUBMITTED`, `OPEN → CANCELLED`, `OPEN → EXPIRED` only. Candidate submit/save/cancel commands may move their own OPEN session to SUBMITTED/CANCELLED; the expiry worker may persist OPEN→EXPIRED for housekeeping. **Business validity never waits for the worker:** Stage, Save, Submit and Finalize synchronously require `status_code = OPEN AND expires_at > transaction_now`. Once wall-clock expiry has passed, the command returns `FORM_SESSION_EXPIRED` even if the row has not yet been marked EXPIRED. Expired/terminal sessions never reopen. Every persisted lifecycle transition updates `updated_at` and is audited.

Upload Reservations are subordinate to the Form Session. ADD/REPLACE Stage and Save/Submit/Finalize synchronously require the reservation to belong to the session and `expires_at > transaction_now`; finalization additionally requires `VALIDATED` + malware `CLEAN`. A wall-clock-expired reservation returns `UPLOAD_RESERVATION_EXPIRED` even if cleanup has not yet changed its status. Reservation expiry cannot extend the parent Form Session; cleanup may mark expired/cancelled reservations after business commands have already failed closed.

## 4. Candidate Submission commands
### `submit_candidate_submission(form_session_id, payload, privacy_notice_version, idempotency_key)`
Actor: Candidate. Preconditions: verified identity, active Candidate, unexpired `OPEN` NEW_SUBMISSION form session (`expires_at > transaction_now`), required CV pending/finalizable, max 5 files, all ADD/REPLACE reservations unexpired + `VALIDATED` + malware `CLEAN`.

Transaction:
1. lock Candidate/form session and synchronously recheck `status=OPEN AND expires_at > transaction_now`;
2. validate `CandidateSubmissionCreate` allowlist and privacy acknowledgement;
3. run the locked staged-document-plan validator (all ADD/REPLACE uploads VALIDATED+CLEAN, effective file count ≤5, effective current CV exists);
4. create Submission snapshot and children;
5. bind/finalize staged document changes into logical document headers + immutable versions;
6. enforce current CV invariant again after materialization;
7. create privacy acknowledgement;
8. update Candidate current profile only because this becomes latest submitted snapshot;
9. enqueue HR notification;
10. mark form session SUBMITTED;
11. audit + commit.

No Submission row is pre-created merely by opening the form.

### `update_candidate_submission(form_session_id, payload, privacy_acknowledged, idempotency_key)`
Actor: Candidate owner. Re-check on Save: Candidate active, Form Session still `OPEN` and unexpired, Submission still `NEW`, expected version matches; every staged ADD/REPLACE reservation is also unexpired at transaction time. The Form Session has server-pinned `presented_privacy_notice_version`; Save requires acknowledgement of that exact version. Same Submission/version acknowledgement is idempotently reused; a new version is inserted. Text/file changes save atomically; Cancel applies neither. Validate the locked staged-document plan before materialization; finalization re-checks Candidate Active + Submission NEW. Any text or file-only successful Save touches the Submission aggregate and increments `version_no` exactly once. Refresh Candidate current-profile only if this is the latest surviving snapshot. Enqueue exact-`submission_id` HR notification inside the same transaction before commit; provider delivery is asynchronous. Older Submission edit never overwrites newer profile cache.

### `update_submission_by_hr()`
`submissions.edit`; HR-specific DTO only. Candidate verified email/security identity is immutable. After update, call `refresh_candidate_current_profile(candidate_id)` when the edited Submission is latest; older Submission edits do not alter Candidate cache.

### `open_submission()`
Requires `submissions.view`. If actor also has `submissions.status` and current state is `NEW`, atomically set `READ`. Otherwise pure read. Default HR has both permissions.

### `set_submission_manual_status(candidate_id, status, expected_latest_submission_id, expected_version)`
Only the **deterministic latest Submission** of the Candidate may be manually changed. Backend locks Candidate, resolves latest Submission by `submitted_at DESC, submission_id DESC`, compares `expected_latest_submission_id` + optimistic version, then allows only `NEW`/`READ` when no active Application exists. **Neither `NEW` nor `READ` may be written manually while any active Application exists.** Historical child Submission status is read-only for the Phase-1 workflow and crafted exact-Submission requests cannot bypass this rule. Starter SQL must expose only a Candidate-level/latest-safe helper (or an equivalently guarded helper); an exact historical `submission_id` writer is forbidden. `PROCESSED`, `DONE`, `CLOSED` are system-derived only. Candidate Active/Inactive does not restrict internal HR manual NEW/READ; inactivity affects Candidate Portal access only. Bulk manual-status mutation is ALL_OR_NOTHING and uses the exact same latest-only eligibility rule.

### `recalculate_submission_status(submission_id)`
Single authoritative status calculator. Mandatory parent `Submission FOR UPDATE` lock before evaluating Applications. Rules: no active Application → preserve existing manual `NEW/READ`; if coming from a derived state after the final Application is removed, return `READ`; any effective current Application `HIRED` → `DONE`; all active Applications `REJECTED` → `CLOSED`; otherwise with active Application → `PROCESSED`. Every Application/current-round/report-outcome mutation invokes this before commit.

### Submission delete reachability + `delete_unused_candidate()`
**Normal production HR does not hard-delete a successfully submitted Submission.** Candidate Submit/Update mandatorily creates retained PRODUCTION email trace bound to the exact `submission_id`; that trace is downstream business history, therefore every normal production submitted Submission is retention-managed rather than eligible for a Phase-1 HR hard-delete command. `delete_unused_submission` is classified **MAINTENANCE_ONLY** for test/import/data-repair states that never acquired retained production business usage; it is not exposed in normal HR UI/permissions. Retained PRODUCTION email usage still **blocks `delete_unused_submission()`** even in that maintenance path.

`delete_unused_candidate()` remains Phase-1 HR behavior only for a truly unused Candidate. It locks the Candidate, discovers OPEN Form Sessions/temp reservations (including a never-submitted form), durably captures Storage cleanup paths, cancels sessions/reservations, then deletes only when no submitted/business usage exists. If durable cleanup capture cannot commit, deletion fails. Exact production permission is `candidates.delete_unused`; Root maintenance is separate. Used records are Inactive/retention-managed; Security Audit is immutable.

## 5. Applications
### `create_or_update_application()`
Input identifies one specific `submission_id`; backend never guesses latest Submission. Durable Application identity is globally unique by `(submission_id, unit_id, department_team_id, position_id)`. Exact duplicate active or inactive resolves to the same row: active duplicate requires confirmation/update; inactive duplicate uses Reactivate rather than creating a second identity. Locks parent Submission; validates hierarchy/owner; creates Application + empty Round 1 only when identity does not exist; recalculates Submission.

### `reactivate_application()`
Supported Phase 1. Expected version; referenced masters may be inactive historically but durable identity remains valid. Lock parent Submission/Application and require an eligible Active HR/root owner (or atomically reassign one). Enumerate only non-elapsed child Interviews that would become `reactivation_conflict_relevant = resource_blocking AND end_at > transaction_now` at transaction time; for each, require every current Participant user active **before** running shared conflict locking/re-check. A fully elapsed interval (`end_at <= transaction_now`) remains historical and **does not block lifecycle reactivation**. Any still-relevant Candidate/Room/Interviewer conflict blocks reactivation atomically. Then enable Application, restore `access_active` context for active children, recalculate Submission and audit. Current Round only selects report/outcome; it does not limit future/current resource conflicts.

### `delete_or_inactivate_application()`
Empty auto-created Round 1 is an owned default child and does not count as business history. If truly unused, delete that Round and Application atomically. Otherwise Inactive. Inactivation makes all child Interviews `access_active=false` without erasing history. Recalculate Submission.

## 6. Interview rounds, Copy and schedule
### `create_next_interview_round()`
Lock Application + latest Interview. Latest round must be active. Allocate `max(round_no)+1`; Demo Topic blank; idempotent. Recalculate Submission if current-round semantics change.

### `copy_interview_schedule()` — dedicated trusted Save-Copy command
The Copy UI may create a client-side draft/prefill, but that draft performs **no DB mutation**. Pressing **Save Copy** invokes exactly this trusted command; no generic “normal save command” may infer Copy semantics.

Input identifies the source `interview_id`, exact target `application_id`, expected source/target versions, copied schedule/logistics draft, selected current Participants and an idempotency key. The command locks the target Application and relevant latest/target Interview rows before choosing the target Round.

Atomic target rule:
- same Application → create/fill the next legal round under the normal round-allocation rule;
- different Application → if `private.is_structurally_empty_default_round(target_round1_id)` returns true, fill that exact default Round 1; otherwise create the next legal round. Copy/delete flows share this exact predicate.

Before commit, the command revalidates every selected/current Participant is an Active Internal User, applies the shared deterministic Candidate/Room/Interviewer resource-lock + `[start,end)` conflict framework, writes `copied_from_interview_id`, preserves copied schedule/logistics, keeps Demo Topic blank for a newly-created target Round, recalculates affected Submission status when current-round semantics change, audits, and commits atomically. Retry with the same idempotency key must not create a second Round.

**Copy provenance counts as business usage.** `private.is_structurally_empty_default_round()` returns false when the Round has `copied_from_interview_id` or when any other Interview references it through `copied_from_interview_id`. Delete/copy flows therefore never attempt a raw FK-restricted delete of a provenance node.

### Shared Interview mutation lock order
Used by reschedule, add/re-add participant on a scheduled Interview, reactivate, CANCELLED→operational, format/room/time change:
1. lock target Interview row;
2. resolve effective parent Application/Candidate;
3. snapshot current room + current participant set;
4. **revalidate every current Participant maps to an existing `app_user` with `is_active=true`; otherwise fail `CURRENT_PARTICIPANT_INACTIVE_REASSIGN_REQUIRED`;**
5. acquire deterministic transaction resource locks for Candidate, Room and Interviewers;
6. re-read participant/resource set; if changed, recompute locks/retry command and repeat participant-eligibility validation;
7. re-check `[start_at,end_at)` Candidate/Room/Interviewer conflicts;
8. apply mutation;
9. audit;
10. commit.

### `save_interview_schedule()`
Validates time, format metadata and normalized room/link. Before a first schedule/reschedule can leave the Interview resource-blocking, `validate_current_participants_operationally_eligible(interview_id)` must PASS. Candidate, Room, Interviewer conflicts are blocking. Adjacent intervals where end=start do not overlap.

### `change_interview_schedule_status()`
Flexible order. `CANCELLED → operational` first revalidates all current Participants active, then runs the shared Candidate/Room/Interviewer conflict framework. Historical inactive Interview Format does not block lifecycle changes when the same format remains referenced.

### `reactivate_interview()`
Latest applicable round only; Application must be active; expected version; revalidate all current Participants active before operationalization; shared conflict framework; no middle-round reactivation when later active round exists.

### `delete_or_inactivate_interview()`
Latest round only. Empty/unused → hard delete; used → inactive. No renumber. Before any Interview hard-delete, lock the Interview and its `upload_reservations`; for every reservation/temp object, snapshot `temp_bucket/temp_path` into `storage_cleanup_queue` durably, mark/cancel the reservation as appropriate, then remove the reservation row so the `ON DELETE RESTRICT` parent FK can pass. **Cleanup-capture failure aborts hard-delete.** A trusted delete must never rely on FK cascade to silently discard reservation metadata while a temp object may still exist. Recalculate parent Submission when current/effective outcome changes.

## 7. Interview format normalization
When changing format, command reads master metadata. If `requires_room=false`, clear `room_id`; if `requires_meeting_link=false`, clear `meeting_link`. HYBRID may keep both when metadata requires both. Inactive format is not selectable for a new/change operation but remains valid for historical Interviews already using it.

## 8. Participants
All participant mutations lock Interview row first.

### `add_interview_participant()`
Active user, no duplicate, snapshot current Directory identity. If schedule is operational, shared conflict framework includes the new Interviewer before insert.

### `remove_interview_participant()`
Warn if report exists. Mark participant not current/archive report per history policy. Reorder remaining participants atomically.

### `readd_interview_participant()`
Ask `RESTORE_OLD_REPORT` or `CREATE_NEW_REPORT`. Lock Interview, verify no current duplicate, and re-check conflict if Interview is `resource_blocking`.
- `RESTORE_OLD_REPORT`: selected historical Participant → `is_current=true`, `removed_at=NULL`, deterministic order, version bump; its Report → `is_active=true`, `is_archived=false`, preserve content and original `decision_updated_at/by`, version bump; audit `RESTORE_PARTICIPANT_REPORT`.
- `CREATE_NEW_REPORT`: old Participant/report stay historical/archived; create new Participant snapshot from current Directory identity and new empty report lifecycle.
Both paths are atomic.

### `reorder_interview_participants()`
Input complete current list; expected versions; temporary ordering strategy prevents unique collisions.

## 9. Reports
### `save_interviewer_report()`
No scoring. Field-aware patch. HR stale edit blocks/reloads; Interviewer wins same-field conflict under merge rule. Only changes to the 3 Final Decision fields update `decision_updated_at/by`; qualitative edits never move Final Decision Source.

### `update_hr_report_note(interview_id, hr_report_note, expected_version)`
Requires `reports.view + reports.manage_status`. Edits **only** HR-only `hr_report_note`; it never changes `report_status_code`, Application `hr_owner_id`, or `interview_note`. Optimistic versioning + audit are mandatory. `hr_report_note` remains excluded from every Interviewer-readable projection.

### `delete_or_inactivate_report(report_id)`
Report-specific action only. The aggregate HR Report drawer does not expose an ambiguous top-level Delete. Used/historical report inactivation must enter canonical archived state `is_active=false, is_archived=true`; restored/current state is `is_active=true, is_archived=false`. No third boolean combination is legal. Interview Session deletion belongs to Interview module.

## 10. Documents / Storage
### `reserve_candidate_form_upload(form_session_id)` / `reserve_interview_upload(interview_id)`
Create short-lived temp/quarantine reservation. Validate requested type/scope and max intent. Candidate form upload does not require a Submission ID. Interview reservation must reference an existing Interview through a physical FK; nonexistent `interview_id` is rejected.

### `validate_staged_upload()`
Validate extension + declared MIME + detected MIME/magic bytes + size ≤5 MB; run malware scanning. Images strip EXIF/geolocation metadata where practical. A file is not finalizable unless scan is `CLEAN`.

### `stage_candidate_document_change()`
Records ADD/REPLACE/DELETE against an unexpired `OPEN` form session; synchronous stage validation requires `expires_at > transaction_now` for the Form Session and, for ADD/REPLACE, the Upload Reservation; no current persisted document is altered until Save/Submit. NEW_SUBMISSION accepts ADD only. Reservation/session/type identity must match, and DB guards prevent one reservation or one target logical document from being staged ambiguously more than once. **REPLACE/DELETE require the target logical document to have exactly one current version at stage-time.** Save/Submit locks the logical header + current version and re-checks the same invariant; a target that became historical/stale is rejected with `INVALID_DOCUMENT_TARGET` and can never be silently resurrected.

### `finalize_interview_upload()`
Locks Interview/document logical header; validates scope/count/scan; creates immutable version/current switch.

### `cleanup_abandoned_uploads()`
Scheduled worker removes expired/cancelled temp objects and stale reservations; never deletes current logical document versions.

Approved formats remain PDF, DOC/DOCX, PPT/PPTX, PNG, JPG/JPEG; malware scanning is a production go-live requirement because external legacy Office formats are allowed.

## 11. Email
### `enqueue_email()` / `send_email()`
Phase 1 system-generated emails have **no attachments**. Recipients are derived/validated from entity + email type; arbitrary recipient override is not permitted for system flows unless an explicit privileged command exists. Business transaction inserts Outbox; worker sends after commit.

Semantics: at-least-once delivery with idempotent enqueue + best-effort deduplication. Outbox records deployment `environment_code`; worker-created Email History preserves that environment. Worker uses leased claim (`FOR UPDATE SKIP LOCKED` or equivalent), stale SENDING recovery, attempts and provider IDs. Acceptance criteria must not promise impossible exactly-once delivery.

## 12. Candidate lifecycle
`set_candidate_active()` preserves history. Inactive blocks Candidate Portal only; internal recruitment may continue.
- `active=false`: set `inactive_at=now()` and `inactive_by=actor` atomically.
- `active=true`: clear `inactive_at/inactive_by`, then evaluate all Submissions. If a Submission has no active Application, explicitly set it to `READ`; otherwise derive `PROCESSED/DONE/CLOSED` from actual Applications.
Generic recalculation outside this lifecycle action may still preserve manual `NEW/READ` when no Application exists. Immutable Security Audit is the historical record of every inactive/reactivate event.

## 13. Internal Users / RBAC
### `create_internal_user()`
Directory manager may create approved EIU directory row.

### `provision_internal_identity_on_first_google_login()`
Verified Google provider + verified normalized `@eiu.edu.vn` email + active allowlisted `app_users` row + `auth_user_id IS NULL` + no conflicting binding → atomic bind + audit. If row already bound to a different Auth ID, reject; never auto-rebind.

### `assign_hr_role_with_defaults()`
Root only. Adds HR role and Full HR Permission Set. Permission prerequisites are included automatically.

### `remove_hr_role()`
Root only. Before role removal, server checks Active Applications owned by the target HR. If any exist, role removal is blocked with `ACTIVE_APPLICATION_OWNER_REASSIGN_REQUIRED` unless those Applications are reassigned atomically to another eligible Active HR/root in the same trusted administrative operation. After the owner invariant is satisfied, remove HR role and revoke HR-default/custom HR permissions by Phase-1 default; historical inactive ownership/snapshots remain. Active sessions re-resolve effective authorization on the next request; security-sensitive UI refreshes immediately.

### `update_internal_user_directory()`
Directory business profile. Email typo correction only while Auth unbound. This command does not alter HR role, permissions, bound identity or Root status.

### `set_internal_user_active(target_user_id, active, expected_version)`
Actor with `users.directory_manage` may change Active state only for a **non-HR, non-Root** internal user. A target with HR role is Root-only; Root is protected; HR self-deactivation is not allowed through normal UI. Before any `active=true → false` transition, the trusted command locks the target User and blocks two stranding cases: **(1)** Active Application owner without atomic reassignment → `ACTIVE_APPLICATION_OWNER_REASSIGN_REQUIRED`; **(2)** current Participant on any non-elapsed `resource_blocking` Interview without remove/replace/reassignment → `FUTURE_INTERVIEW_PARTICIPANT_REASSIGN_REQUIRED`. The same participant guard applies regardless of HR/non-HR target authority; Root privilege does not bypass the business invariant. After guards pass, apply lifecycle change, force authorization/session re-evaluation on subsequent requests, and write immutable security audit.

### `change_internal_user_identity()`
Root-only for already-bound non-root users. Root Admin identity uses break-glass runbook only.

### Permission dependencies
Effective permission grants must enforce prerequisites: `*.edit/status/delete/email/manage` requires corresponding `*.view` where a view permission exists. Root UI auto-grants prerequisites or blocks invalid combinations. Backend command checks required read/context permission as well.

## 14. Master Data
`create_master_item`, `update_master_item`, `delete_or_inactivate_master_item` use optimistic versioning. Referenced master structural semantics are immutable: changing meaning requires a new row and Inactive old row. Typo/display-label corrections may be allowed with audit when they do not change business meaning. Inactive historical masters remain readable/operable but cannot be selected for new references.

Metadata with no hard Phase-1 effect is explicitly advisory/optional in `seed_master_data.json`; coding agents must not invent blocking behavior.

## 15. Bulk operations
Bulk behavior is command-specific, never inferred by the frontend:
- Bulk latest Submission manual status NEW/READ: all-or-nothing.
- Bulk common Application assignment: all-or-nothing.
- Bulk email: per-item result because delivery is asynchronous.
- Bulk delete/inactive/status: explicit contract must state atomic vs partial before the UI exposes it.

Batch responses expose `success[]` and `failed[{id,error_code}]` when partial semantics are chosen.

## 16. Background boundary
Critical audit, permission changes, status recalculation and invariants are inside business transactions. Email delivery, malware scan orchestration, orphan cleanup and non-critical telemetry run after commit through durable workers, while finalization waits for required security scan results.

## Explicit trusted-command contracts
The following commands close remaining UI → command gaps. Each is a trusted server/RPC command; direct browser table mutation is not an alternative.

### `mutate_submission_documents_by_hr(submission_id, expected_version, mutation_plan, idempotency_key)`
Requires `submissions.view + submissions.edit`. Locks Submission + affected logical-document headers + current versions. REPLACE/DELETE may target only a logical header with exactly one current version and re-check that target-current invariant inside the transaction. Validates document scope, approved type, 5 MB/file, max 5 effective current files, malware `CLEAN`, current CV invariant and logical-version invariants. Applies ADD/REPLACE/DELETE atomically, increments `Submission.version_no` exactly once even for file-only changes, audits and is idempotent.

### `delete_interview_document(interview_document_id, expected_version)`
Requires `interviews.view + interviews.documents`. Validates exact Interview context and document usage, deletes only under the existing Interview Document delete rule, durably schedules Storage object cleanup before metadata loss, and audits.

### `delete_email_history(email_history_id, cleanup_reason_code, reason_text)`
Requires `emails.history_view + emails.history_delete` **and parent contextual read permission** for the subject record (`submissions.view`, `interviews.view`, `reports.view`, or Application context through its Submission, according to `email_type`). RLS must hide history rows when that parent context is unavailable.

Deletion is machine-deterministic:
- `TEST_RECORD` is accepted only for a row created in `environment_code=TEST`;
- `WRONG_RECORD` is an explicit authorized human cleanup classification and requires non-empty `reason_text`.

Any other reason is rejected. Immutable Security Audit stores actor, parent context, classification and reason. Outbox/provider records are not silently rewritten.

### `update_application_hr_owner(application_id, hr_owner_id, expected_version)`
Requires `applications.manage`. HR owner is an Application concern, not a Report permission. Locks Application, validates target owner is Active HR/root, writes old/new owner audit and optimistic version update.

**Operational owner invariant:** every Active Application must have an eligible Active HR/root owner. `reactivate_application()` revalidates this invariant before enabling the Application. Root cannot deactivate an HR or remove the HR role while that user owns Active Applications unless those Applications are reassigned atomically to another eligible Active HR/root first. Historical Inactive Applications may retain an inactive former owner reference.


### `provision_candidate_identity()` — recreated Auth branch
When verified OTP email matches an existing Candidate but `auth_user_id` contains an obsolete/recreated Auth identity, command may replace old→new only under the Candidate-specific safe-rebind predicate: exact verified normalized email, Candidate row lock, no other Candidate uses new Auth ID, no contradictory identity state, security audit old/new. Internal User rebind rules are separate and remain privileged.

### `set_candidate_active(candidate_id, active, expected_version)` — reactivation mode
On `active=true`, evaluate all Submissions. If a Submission has no active Application, result is `READ`; otherwise derive `PROCESSED/DONE/CLOSED` from actual Applications. This lifecycle exception is authoritative for Candidate reactivation.

### `change_report_status(interview_id, status, expected_version)`
Requires `reports.view + reports.manage_status`. This is the **single trusted mutation path** for `interviews.report_status_code`. It may change Current Round Report Status only. Transaction locks Current Round + parent Application/Submission, validates permission/state/version, updates status, calls authoritative `recalculate_submission_status()` before commit, writes audit, then commits. It does not change `hr_report_note` or Application HR owner.

### `set_report_visibility(interview_id, visible, expected_version)`
Requires `reports.view + reports.visibility`; updates current Interview visibility with optimistic concurrency and audit.

### `bulk_create_or_update_applications(items[])`
Requires `applications.manage + submissions.view`; **ALL_OR_NOTHING** for common assignment operation. Every item names an exact Submission; no implicit latest selection.

### `bulk_enqueue_email(items[])`
Requires the corresponding email/context permission for each item. Per-item enqueue result; client/idempotency retry does not duplicate logical Outbox rows. Delivery remains at-least-once.

### `create_master_item(...)` / `update_master_item(...)` / `delete_or_inactivate_master_item(...)`
Require `master_data.manage`. Referenced structural semantics are immutable; unused may hard-delete, used becomes Inactive. Historical inactive values remain usable by existing records but cannot be newly selected.

### `grant_hr_permission(...)` / `revoke_hr_permission(...)`
Root-only. Enforce permission dependencies; security audit required.

### `root_admin_break_glass_recovery(...)`
Not a normal UI command. Runs only under `61_ROOT_ADMIN_BREAK_GLASS_RECOVERY.md` with approval, controlled migration/function, verification, immutable audit and rehearsal evidence.

### Interview hard-delete temp-upload cleanup ordering
`delete_or_inactivate_interview()` and its batch equivalent must lock Interview + related Upload Reservations, insert durable `storage_cleanup_queue` rows for every temp object, then cancel/remove reservations before hard-delete. `upload_reservations.interview_id` uses `ON DELETE RESTRICT`; raw/cascade deletion is forbidden. If cleanup intent cannot be committed, the Interview hard-delete fails.

### Hard-delete session/temp cleanup ordering
`delete_unused_candidate()` production flow must lock target, discover OPEN Candidate Form Sessions/temp reservations, durably enqueue Storage cleanup references, cancel sessions, then delete only a truly never-used Candidate. `delete_unused_submission` is MAINTENANCE_ONLY and may run only against non-production/import/test repair data with no retained business trace; it is not an HR production permission. If durable cleanup capture cannot commit, hard-delete fails.



## Canonical helpers and maintenance-only lifecycle
### `refresh_candidate_current_profile(candidate_id)`
Internal helper: lock Candidate; select latest surviving Submission by `submitted_at DESC, submission_id DESC`; set `current_full_name/current_phone/last_submission_at`, or clear them if no Submission remains. Called after new Submission, latest Candidate/HR edit, MAINTENANCE_ONLY Submission repair-delete, and repair/migration. A maintenance repair-delete refreshes Candidate current profile afterward.

### Internal User unused cleanup
Hard-delete Internal User is MAINTENANCE_ONLY / Root-operated, not an HR UI command. Eligible only if unbound (`auth_user_id IS NULL`), non-Root, no HR role/permissions and never referenced. Otherwise Inactive. Audit required.

### Privacy Notice publication
Published Privacy Notice content/locale/hash/published/effective fields are immutable; only `is_current` may change. New wording creates new `notice_version`. Publication/current switching is **maintenance/deployment-only in Phase 1**, not a Candidate/HR UI mutation, and follows `78_PRIVACY_NOTICE_PUBLICATION_RUNBOOK.md`. A future-effective notice is inserted with `is_current=false`; the current pointer is switched only at/after `effective_from` in one transaction so an existing effective current notice is never intentionally removed first. Starting Form Session fails `PRIVACY_NOTICE_UNAVAILABLE` if no current notice with `effective_from <= now()`.

## Candidate notification side-effect rule
Candidate Submit/Update HR notification is a system side effect inserted into Outbox in the same business transaction. Candidate endpoint abuse controls apply before the business command. Notification coalescing/throttling may delay or merge downstream delivery but **must not invalidate or roll back an otherwise valid Candidate Save** merely because an email-specific delivery quota is reached. The committed Outbox/event remains traceable to exact `submission_id`.


## Phase-1 named batch commands

All lifecycle/status batches below are **ALL_OR_NOTHING**. The server validates the full selected set, acquires deterministic locks, performs all writes/derived recalculations/audit in one transaction, or rolls back the entire batch. Browser-side loops over single-row commands are forbidden as the production contract.

### `bulk_set_candidate_active(candidate_ids, active, expected_versions[])`
Requires Candidate lifecycle permission for every selected Candidate. Selection entity = Candidate. Candidate lifecycle rules, inactive metadata, portal effects and per-Submission reactivation recalculation are identical to the single-Candidate command. Each Candidate receives per-item audit plus one batch audit event. Any stale/ineligible item aborts the whole batch; Internal-User owner/participant guards are not part of Candidate lifecycle.

### `bulk_set_latest_submission_manual_status(candidate_ids, status, expected_latest_submission_ids, expected_versions[])`
Requires Submission status permission for every selected Candidate. **Selection entity = Candidate**, matching the Application Inbox checkbox model. For each selected Candidate the server locks the Candidate, resolves deterministic latest Submission (`submitted_at DESC, submission_id DESC`), rechecks it against `expected_latest_submission_ids`, and rechecks optimistic versions. Only `NEW`/`READ` are legal manual targets. Any active Application on any resolved latest Submission rejects the **entire batch**. Candidate Active/Inactive does **not** change internal HR manual-status eligibility; the batch matches `set_submission_manual_status()` exactly. No historical child Submission may be mutated from this Candidate-level UX. This is the single batch writer for visible bulk Mark New/Read; browser loops and overlapping legacy Mark-New batch writers are forbidden.

### `bulk_delete_or_inactivate_interviews(interview_ids, expected_versions[])`
Requires Interview manage/delete rights for every selected Interview. Applies the same current/highest-round, meaningful-history, document/email/report/participant, Interview upload-reservation cleanup and parent-Submission recalculation rules as the single command. Every hard-delete target must durably capture temp-object cleanup before any Interview is deleted. Any item that cannot take the requested lifecycle action aborts the whole batch; no reservation/object cleanup is left orphaned.

### `bulk_change_interview_schedule_status(interview_ids, target_status, expected_versions[])`
Requires `interviews.status` + prerequisite `interviews.view` for every selected Interview. For every selected Interview whose transition would make it `resource_blocking`, the transaction locks the Interview, validates every current Participant resolves to an Active Internal User, acquires Candidate/Room/Interviewer resource locks, re-reads the Participant/resource snapshot, repeats eligibility when the set changed, then runs the same deterministic Candidate/Room/Interviewer conflict engine as the single writer. Stable inactive-participant failure is `CURRENT_PARTICIPANT_INACTIVE_REASSIGN_REQUIRED`. **ALL_OR_NOTHING:** one invalid transition, inactive current Participant or resource conflict aborts the entire selected batch; no Interview changes.

### `bulk_change_report_status(interview_ids, target_report_status, expected_versions[])`
Requires Report status permission for every selected Current Round. `change_report_status()` semantics remain the only underlying writer for `report_status_code`; the batch command applies that writer atomically to the selected set and recalculates every affected parent Submission before commit.


### Internal User lifecycle guard for future/current Interview participation
Normal Internal User deactivation is blocked when the target user is a current Participant on any non-elapsed `resource_blocking` Interview. The stable business error is `FUTURE_INTERVIEW_PARTICIPANT_REASSIGN_REQUIRED`; HR/Root must remove/replace the Participant first. Historical removed participation remains readable. Re-add requires `app_user.is_active = true` and otherwise returns `USER_INACTIVE_NOT_SELECTABLE`.


### Submission hard-delete and retained production-email trace
For Phase 1, retained **PRODUCTION** Email Outbox/Email History usage is downstream business history and **makes normal production Submission hard-delete ineligible; `delete_unused_submission` is MAINTENANCE_ONLY**. This preserves the exact `submission_id` relational trace. TEST/WRONG operational email history may be removed only through its dedicated cleanup rules; immutable Security Audit remains. Therefore the maintenance-only delete path must reject a Submission referenced by retained production email records rather than relying on `ON DELETE SET NULL`.


Plain contract summary: retained PRODUCTION email usage is downstream history and makes normal production Submission hard-delete ineligible; `delete_unused_submission` is MAINTENANCE_ONLY.



---

<!-- SOURCE: 38_NON_FUNCTIONAL_REQUIREMENTS.md -->

# 38. Non-functional Requirements — Phase 1 Baseline Targets — v1.8

These are initial acceptance targets for architecture/UAT. IT may revise them before Technical Freeze through documented change control, but “TBD everywhere” is no longer allowed.

## Performance
- List/search API p95: **≤1.5 s** at 10,000 Submissions / 30,000 Interviews test dataset, excluding client network beyond normal Vietnam broadband.
- Core mutation p95: **≤2.0 s** excluding external provider delivery/upload transfer.
- Initial page shell/navigation p75: target **≤2.5 s** on normal office broadband; large table data loads independently.
- Server pagination: 25 default, options 25/50/100.
- Search debounce: 300 ms; minimum 2 characters for broad name search; exact email/phone may search immediately.
- No full-dataset browser filtering.

## Capacity baseline
- 10,000 Candidate Submissions/year baseline sizing target.
- 50 concurrent internal users, 200 concurrent Candidate sessions during spikes.
- 5 files max per Submission or Interview Session; 5 MB/file.
- Architecture should scale upward without schema redesign; capacity is not a contractual ceiling.

## Reliability / concurrency
- Atomic commands; idempotency for duplicate-prone mutations.
- Mandatory schedule resource lock + conflict recheck.
- Optimistic locking with `version_no`.
- Email Outbox separated from business transaction.

## Timezone
DB events = `timestamptz`; UI business timezone = `Asia/Ho_Chi_Minh`; date-only fields remain PostgreSQL `date`.

## Availability / backup baseline
- Application availability target for Phase 1 internal service: **99.5% monthly**, excluding approved maintenance/provider-wide incidents.
- Database target RPO: **≤24 hours** minimum; target RTO **≤8 hours**. If the purchased Supabase plan supports stronger PITR, use it.
- Storage objects require separate backup/export strategy; DB backup alone is insufficient.
- Restore rehearsal before go-live and at least annually or after material architecture change.

## Email
- Retry transient failures with bounded exponential backoff for up to **24 hours** or provider-specific equivalent.
- Permanent failure is surfaced to HR; no infinite retry.

## Logging / Audit
- Operational application logs: at least **30 days** searchable in the chosen observability platform.
- Business/security audit: **no automatic purge under current EIU business policy**; capacity monitoring applies.

## Storage/capacity warning
No automatic business-data expiry/purge. Admin capacity dashboard/alerts should support configurable thresholds; recommended initial warnings at 70%, 85%, 95% of purchased quota. EIU then decides upgrade capacity or export/archive locally and explicitly purge selected data.

## Security
HTTPS, RLS + explicit grants, server-only secrets, Candidate rate limits, CSP/security headers, dependency scanning, auth regression tests, no service-role in browser.

## Accessibility
Target WCAG 2.2 AA for supported production UI. Candidate Portal must be mobile-ready before go-live.

## Privacy, upload and grouped-pagination requirements
- PII search terms must not be stored in URL/browser history.
- Malware scan pipeline is required for production because `.doc/.ppt` from external candidates are allowed.
- Candidate form temp upload/session cleanup job must have observable backlog and alert on stale objects.
- Grouped pagination unit: Candidate for Application Inbox; Application for Interview/HR Report.
- Stable sorting always includes an immutable ID tie-breaker.



---

<!-- SOURCE: 39_SECURITY_RLS_MATRIX.md -->

# 39. Security / RLS Matrix — v1.8

## 1. Principles

- RLS bắt buộc cho exposed business tables.
- `anon`: không đọc/ghi dữ liệu tuyển dụng.
- `authenticated`: chỉ quyền tối thiểu.
- Browser dùng Supabase publishable key; **không bao giờ** secret/service-role key.
- Service-role/server code vẫn phải tự authorize trước khi thao tác vì service-role bypass RLS.
- Mutations phức tạp ưu tiên RPC/Server Action, không direct table DML.

## 2. Identity helpers

Private helpers đề xuất:
- `private.current_app_user_id()`
- `private.is_root_admin()`
- `private.has_permission(code)`
- `private.is_candidate_owner(candidate_id)`
- `private.is_current_interview_participant(interview_id)`

Nếu dùng `SECURITY DEFINER`:
- `set search_path=''`;
- explicit qualified table names;
- revoke execute khỏi public/anon; chỉ grant nơi cần.

## 3. Read matrix

| Entity | Candidate | HR | Interviewer | Root Admin |
|---|---|---|---|---|
| Candidate | own | permission | no | all |
| Submission | own | permission | no | all |
| Submission documents | own | permission | no | all |
| Application | no/internal-hidden | permission | contextual minimal | all |
| Interview Session | no | permission | participant + visible | all |
| Participants | no | permission | own/current session list | all |
| Interview documents | no | permission | current participant + visible | all |
| Interview reports | no | permission | current session; read shared report per business | all |
| HR notes | no | permission | no | all |
| User directory | no | allowed subset | contextual names needed | all |
| Permissions | no | own effective view if desired | no | all |
| Audit log | no | restricted admin/security | no | all |

## 4. Write matrix

Candidate:
- writes own Submission only through command and only while `NEW`;
- email immutable;
- own Storage path only.

HR:
- command permission checks by granular code;
- `reports.edit_interviewer` required to edit Interviewer report;
- `users.permissions_manage` Root Admin only.

Interviewer:
- write own active report for current participation only;
- cannot update another participant report;
- cannot edit when Current Round report status is final.

Root Admin:
- implicit all app permissions;
- still subject to business safety guards unless specific recovery procedure.


## 4A. Direct-table/RPC access blueprint

| Entity | Candidate SELECT | Candidate write | HR SELECT | HR write | Interviewer SELECT | Interviewer write |
|---|---|---|---|---|---|---|
| `candidates` | own active | provisioning/profile command only | permissioned | candidate-active command | no | no |
| `submissions` | own | Candidate command only while NEW | `submissions.view` | `submissions.edit/status` commands | no | no |
| `submission_documents` | own | upload commands | `submissions.view/edit` as defined | document commands | no | no |
| `applications` | no | no | `applications.manage` or page-read permission path | commands | contextual minimal if needed | no |
| `interviews` | no | no | `interviews.view`/manage | commands | access-active participant + visible | no |
| `interview_participants` | no | no | permissioned | participant commands | current session list only | no |
| `interview_documents` | no | no | permissioned | document commands | access-active participant + visible | no |
| `interview_reports` | no | no | `reports.view` | report commands | shared current-session read | own report command only |
| `app_users` | no | no | allowed directory subset | directory command | contextual identity subset | no |
| `app_user_permissions` | no | no | own/effective if needed | Root commands only | no | no |
| `email_outbox/audit` | no | no | restricted server/admin view | server/worker only | no | no |

`hr_report_note` should not be exposed through a broad Interviewer-readable row shape. Prefer a safe projection/RPC or field-separated query contract so column confidentiality is not dependent on frontend hiding.

## 5. Views

Implementation views (`Current Round`, `Application Outcome`, `Final Decision Source`) nằm ở `private` schema.

Nếu một view bắt buộc expose:
- use `security_invoker=true`;
- explicit grants;
- test RLS with Candidate/HR/Interviewer identities.

## 6. Storage

Private buckets only.

Storage RLS phải kiểm soát:
- candidate own submission paths;
- HR permission-based read/write;
- interviewer read only interview-document paths của session current + visible;
- no public bucket for CV/degrees/transcripts/reports.

## 7. RLS performance

- index FK/ownership columns dùng trong policies;
- use `(select auth.uid())` where appropriate;
- tránh self-recursive RLS;
- complex permission lookup có thể dùng private `SECURITY DEFINER` helper đã khóa execute.

## 8. Required security test personas

- anonymous;
- Candidate A;
- Candidate B;
- HR full;
- HR limited;
- Interviewer A;
- Interviewer B;
- inactive internal user;
- inactive candidate;
- Root Admin.


## Authorization hardening rules
- Interviewer contextual SELECT requires `application.is_active AND interview.is_active AND participant.is_current AND visible_to_interviewers AND app_user.is_active`.
- Candidate inactive does not hide internal records from authorized HR.
- `hr_report_note` is HR-only; never selected through Interviewer policy/view.
- `users.directory_manage` never authorizes rebinding an already-bound Auth identity. `users.identity_manage` is Root-only in Phase 1.
- `submissions.view` by itself is read-only; NEW→READ side effect requires `submissions.status`.
- Storage policies mirror the same ownership/context rules; signed URL creation is itself authorized server-side.


## Migration blueprint
See `59_RLS_POLICY_BLUEPRINT.md` for per-persona predicate intent and adversarial test requirements. Final executable policies/GRANTs must be reviewed on the actual Supabase migration bundle before **Implementation Validation / Migration Freeze**. The pre-code Technical Specification Freeze reviews policy intent/blueprints, not nonexistent production migrations.

## Candidate Form Session and logical-document RLS scope
Policies/migrations must cover `candidate_form_sessions`, `candidate_form_document_changes`, `submission_document_logicals`, `interview_document_logicals` and revised `upload_reservations`. Candidate may access only own open Form Session and own staged uploads; Interview upload remains HR-permission controlled. Logical headers inherit parent authorization.

Permission dependency is not delegated to UI: an action command requires its action permission plus view/context prerequisite.


## Canonical Interviewer contextual predicate
Interviewer RLS/contextual access must include `Application.is_active=true AND Interview.is_active=true` before participant/visibility/user checks. Do not use schedule status for access authorization. `resource_blocking` is a scheduling predicate, not an RLS predicate.

## Email History, permission-display and owner-lifecycle rules
- Email History SELECT requires `emails.history_view` **plus** the parent/context read predicate derived from `email_type`; a raw `email_history_id` never grants access.
- Email History DELETE requires `emails.history_view + emails.history_delete` plus the same parent context and accepted cleanup classification. Root bypass remains audited.
- Non-root `users.directory_manage` does not grant visibility into another user's granular effective-permission list. Root may view all; non-root may see only the role/protected-state needed for lifecycle plus their own effective permissions.
- Active Application owner invariant: `hr_owner_id` must resolve to Active HR/root. HR-role removal/deactivation is blocked while Active Applications remain owned unless reassignment is part of the same trusted operation.



---

<!-- SOURCE: 40_DATABASE_INVARIANTS.md -->

# 40. Database Invariants — v1.12

Hard invariants must not depend only on frontend behavior.

1. Exactly one Root Admin **after bootstrap**: partial unique prevents >1; protected bootstrap/recovery command prevents 0 in normal operation. Root email/auth binding cannot be changed through ordinary directory update.
2. Candidate verified email unique; Submission email snapshot must match Candidate email at snapshot write.
3. Application references Submission only; Candidate derives through Submission.
4. Application hierarchy uses null-safe equality: Unit and Team must match Position, including `NULL = NULL` semantics via `IS DISTINCT FROM`.
5. `round_no > 0`, unique `(application_id, round_no)`.
6. `start_at < end_at` when both exist; operational overlap semantics `[start,end)`.
7. `access_active` Interview = active parent Application AND active Interview. `resource_blocking` additionally requires non-CANCELLED status + complete interval; Current Round is highest `round_no` among access-active Interviews.
8. Current participant user/order unique; participant order >0.
9. Active report belongs to a Participant; one active/non-archived report per Participant.
10. Decision metadata moves only when one of the 3 final fields changes.
11. Logical documents: unique `(logical_document_id,version_no)`, unique current version per logical document, unique storage path, ≤5 MB/file. Max 5 current files per parent enforced in parent-locked finalize command.
12. Interview operational/report notes are separate columns with separate authorization.
13. Internal bound Auth identity cannot be rebound by ordinary directory update; Root identity protected.
14. Master-data FK/reference integrity; referenced item is inactive rather than hard-deleted.
15. Email Outbox logical enqueue idempotency unique; audit log append-only.
16. Schedule mutation obtains deterministic advisory locks on Candidate/Room/Interviewers and rechecks conflicts before commit.
17. Auto-created empty Round 1 does not by itself make Application “used”; hard-delete command may delete both atomically only while the round is structurally empty.

## invariants
- Candidate Form Session is the parent for pre-Submission uploads; no Submission is created on form open.
- Staged Candidate document mutation rows are valid only while the Form Session is `OPEN` **and `expires_at > transaction_now`**; NEW_SUBMISSION permits staged `ADD` only; reservation/session/type identity must match; one reservation cannot back multiple staged mutations; one persisted logical document cannot have multiple simultaneous pending mutations in the same session.
- Before Candidate Submit/Save, `private.validate_candidate_form_document_plan()` must run under the locked Form Session and enforce: Form Session unexpired; every ADD/REPLACE reservation unexpired + `VALIDATED` + malware `CLEAN`; effective current file count ≤5; at least one effective current CV remains. Cleanup workers are housekeeping only and never define business validity.
- Document logical header fixes parent + document type; every version under a logical ID inherits the same parent/type.
- Privacy acknowledgement stores `submission_id`; Candidate derives via Submission.
- Submission status manual set is limited to NEW/READ. PROCESSED/DONE/CLOSED are derived by one authoritative recalculation function.
- Outcome-changing transactions lock parent Submission before recalculation.
- Schedule-resource transactions lock target Interview before reading participant set and acquiring Candidate/Room/Interviewer locks.
- Referenced master structural semantics are immutable; inactive historical references remain valid.
- Current Candidate profile cache, when used, is sourced only from latest submitted snapshot; editing an older Submission cannot overwrite it.


## invariants
- Durable Application identity `(submission_id, unit_id, department_team_id, position_id)` is globally unique across Active/Inactive history.
- Candidate Form Session always pins Privacy Notice; EDIT requires target Submission + base version; NEW requires neither.
- Published Privacy Notice content/hash/publish/effective fields are immutable; only `is_current` lifecycle pointer may change.
- Candidate current-profile cache refreshes from latest surviving Submission through one helper.
- All `resource_blocking` Interviews participate in conflict checks regardless of Current Round.
- Interviewer contextual access requires active parent Application as part of `access_active`.

## Current semantic invariants
- Candidate Form Session always pins non-null server-published Privacy Notice; EDIT additionally requires non-null base Submission version.
- Published/referenced Privacy Notice content/hash/published/effective metadata is immutable; new content uses a new version.
- Candidate current-profile cache equals latest surviving Submission by `submitted_at DESC, submission_id DESC`; repair helper is authoritative after latest edit/delete.
- Application durable identity is globally unique and immutable from creation, irrespective of interview history.
- Interviewer contextual access uses `access_active = application.is_active AND interview.is_active`; `resource_blocking` additionally requires non-CANCELLED scheduled interval, independent of Current Round.

## Additional invariants
- Candidate staged/HR Submission `REPLACE` or `DELETE` may target only a logical document with exactly one current version; stage-time and transaction Save-time both enforce it.
- Active Application owner must resolve to an Active HR/root; HR deactivation/role removal cannot strand Active Applications.
- Candidate inactive metadata matches current lifecycle state: Active => inactive fields null; Inactive => timestamp/actor present.
- Interview Report lifecycle is canonical: current = `is_active=true AND is_archived=false`; historical = `is_active=false AND is_archived=true`.
- Privacy/document SHA-256 values use 64 hexadecimal characters when present.
- Operational Email History stores deployment environment; deletion is contextual + classified + audited.


## Zero-UUID Team sentinel
The durable Application identity index uses `00000000-0000-0000-0000-000000000000` only as the SQL sentinel for a NULL `department_team_id`. `department_teams.department_team_id` has a DB CHECK that forbids this UUID as a real master key, so the expression index cannot collide with a legitimate Team row.

## Candidate Form Session lifecycle — v1.12 current contract
- Canonical persisted transitions: `OPEN → SUBMITTED | CANCELLED | EXPIRED`; terminal states never reopen.
- Stage/Save/Submit/Finalize use wall-clock expiry synchronously; stale `OPEN` rows past `expires_at` fail `FORM_SESSION_EXPIRED`.
- ADD/REPLACE reservations past `expires_at` fail `UPLOAD_RESERVATION_EXPIRED` even before cleanup persists `EXPIRED`.
- Lifecycle persistence updates `updated_at`; business mutation/terminal transition is auditable.


## Operational Participant invariant — v1.12
No trusted mutation may make an Interview resource-blocking unless `private.all_current_participants_selectable(interview_id)=true`. Dormant/CANCELLED/access-inactive Interviews may retain historical current Participant rows whose users later become inactive, but scheduling/uncancelling/reactivation must fail until HR removes/replaces them.

## Copy provenance invariant — v1.12
`private.is_structurally_empty_default_round()` is false for outgoing or incoming `copied_from_interview_id` provenance. Provenance nodes are business-used and protected from accidental raw FK-restricted hard-delete attempts.

## Interview upload reservation integrity — v1.16
- `upload_reservations.interview_id` references a real Interview and uses `ON DELETE RESTRICT`.
- Interview hard-delete must first durably snapshot every temp object into `storage_cleanup_queue`, then cancel/remove reservation rows; cleanup-capture failure blocks delete.
- `storage_cleanup_queue` intentionally stores snapshot IDs/paths without parent FK so the worker can complete cleanup after the business parent has been removed.
- No trusted single or bulk Interview delete may leave an orphan reservation or uncaptured temp object.



---

<!-- SOURCE: 41_STORAGE_AND_UPLOAD_SECURITY.md -->

# 41. Storage & Upload Security — v1.8

## Approved file policy
- PDF: `.pdf`
- Word: `.doc`, `.docx`
- PowerPoint: `.ppt`, `.pptx`
- Images: `.png`, `.jpg`, `.jpeg`
- **5 MB maximum per file**
- **5 current files maximum per Submission and per Interview Session**
- Candidate form: CV required; Degree/Transcript/Certificate/Other optional.

Reject HTML, SVG, executable, script, archive and unapproved formats. Extension alone is insufficient: validate claimed MIME and content signature/magic bytes where feasible.

## Buckets
Private buckets only. No public CV/degree/report/demo URL. Browser gets short-lived authorized signed URL; initial target TTL 1–5 minutes for sensitive documents.

## Two-phase protocol
1. `reserve_upload` authorizes actor, parent, intended type/count/size and creates temp/quarantine path.
2. Client/server uploads object to temp path.
3. Validation verifies extension/MIME/signature/size and **mandatory production malware scan** before final promotion.
4. Lock parent, enforce max current files, insert metadata/version atomically, switch current version, retire previous version.
5. Async cleanup removes expired/orphan temp objects.

DB rollback cannot rollback Object Storage, so direct “upload then hope metadata insert succeeds” is prohibited.

## Preview/download
PDF/image may preview in hardened same-origin viewer where safe. Word/PPT normally download unless a vetted converter/viewer is added. Never inline-render arbitrary HTML/SVG.

## Path/metadata
Server-generated object key; preserve original filename only as metadata; normalize header/content-disposition; unique bucket/path; checksum when available.

## Candidate staged upload/edit protocol
1. Open short-lived Candidate Form Session (NEW or EDIT); persisted lifecycle is `OPEN → SUBMITTED | CANCELLED | EXPIRED` only.
2. Reserve temp/quarantine path against Form Session; no Submission ID is required for a new form.
3. Validate extension + declared/detected MIME + magic bytes + 5 MB limit.
4. Run malware scan; because DOC/PPT are allowed, `CLEAN` is mandatory before finalization.
5. Candidate document ADD/REPLACE/DELETE remains pending in form session; stage requires Form Session `OPEN` and unexpired, and ADD/REPLACE reservation unexpired.
6. Submit/Save locks parent/session, synchronously re-checks Form Session `OPEN` + unexpired, Candidate active + Submission NEW for edits, calls the authoritative staged-plan validator (`private.validate_candidate_form_document_plan()` or its migration-equivalent), validates max 5 effective current files + required current CV + every staged ADD/REPLACE as unexpired + `VALIDATED/CLEAN`, then atomically writes logical headers/versions and marks staged changes applied.
7. Cancel/expiry cleans pending objects; persisted current versions remain unchanged. Async cleanup is housekeeping only; wall-clock expiry blocks Stage/Save/Submit/Finalize synchronously.
8. Image EXIF/geolocation metadata is stripped where practical before final object promotion.

Logical model uses a header (`submission_document_logicals` / `interview_document_logicals`) that fixes parent + `document_type_id`, and version rows cannot switch parent/type.

## Interview reservation / hard-delete protocol
- `upload_reservations.interview_id` is a real FK to `interviews(interview_id)` with `ON DELETE RESTRICT`; an Interview reservation cannot reference a nonexistent parent.
- Interview hard-delete must lock parent + reservations, durably insert each temp bucket/path into `storage_cleanup_queue`, then cancel/remove reservation rows before deleting the Interview.
- Durable cleanup-capture failure blocks the hard-delete. The Storage cleanup worker may run later, but the cleanup intent must already survive the parent deletion.
- `is_structurally_empty_default_round()` remains a business-history predicate; temp reservations are a separate **cleanup prerequisite**, not a reason to pretend the Round has meaningful recruitment history.
- FK cascade is forbidden for Interview reservations because PostgreSQL deletion cannot remove the corresponding Object Storage object transactionally.



---

<!-- SOURCE: 42_PRIVACY_RETENTION_COMPLIANCE.md -->

# 42. Privacy, Retention & Compliance Capability — v1.8

## Current business retention decision
**No automatic expiry/purge under current EIU business policy.** Recruitment records are retained until EIU explicitly decides otherwise. When capacity approaches limits, system warns Admin; EIU may purchase more capacity or export/archive selected data to local controlled storage and then explicitly delete selected online records. This is a business storage policy, not a legal conclusion.

## Required technical capabilities
- immutable published Privacy Notice versions;
- acknowledgement per Submission and notice version;
- data export and authorized explicit purge/archive with audit;
- capacity monitoring/alerts;
- candidate correction workflow;
- sensitive file access/download audit;
- no silent automatic purge.

Acknowledgement stores `submission_id`, `notice_version`, `acknowledged_at`, `source_code`; Candidate derives through Submission. Normal production submitted Submissions are retention-managed because retained production email trace is business history. MAINTENANCE_ONLY repair-delete of non-production/legacy unused data may cascade acknowledgement while immutable Security Audit preserves the deletion event.

## Privacy Notice authority
`privacy_notice_versions` is server-authoritative. Once published, `notice_version`, localized content, content hash, `published_at`, `effective_from` and creator metadata are immutable. New wording creates a new version; only the current-pointer lifecycle may change.

Every NEW/EDIT Candidate Form Session pins exactly one current/effective notice (`is_current=true AND effective_from<=now()`). None available → fail closed `PRIVACY_NOTICE_UNAVAILABLE`. Client arbitrary/unpublished version is rejected. EDIT Save acknowledges the pinned version; same-version acknowledgement is idempotent and a newly pinned version appends another historical acknowledgement.

## Publication/current switch
Phase 1 publication is maintenance/deployment-only and follows `78_PRIVACY_NOTICE_PUBLICATION_RUNBOOK.md`. A future-effective version is inserted non-current; pointer switch occurs only at/after `effective_from` in one transaction, preserving an effective current notice until the switch commits.

## Retention operations
Operational export/archive/purge follows `66_DATA_EXPORT_ARCHIVE_PURGE_RUNBOOK.md`. Current business policy remains no automatic expiry/purge.

## Deferred legal inputs
Exact notice wording and legally mandated retention/deletion rules are confirmed by EIU Legal/DPO-equivalent before production go-live. System capability must not assume indefinite retention is legally required or always permitted.



---

<!-- SOURCE: 43_EMAIL_DELIVERY_SPEC.md -->

# 43. Email Delivery Specification — v1.8

## Delivery semantics
Business transaction inserts an Outbox row and commits. Worker delivers later. Do **not** claim exactly-once delivery. Target semantics: **at-least-once delivery with idempotent enqueue + best-effort/provider-assisted deduplication**.

## Outbox lease fields
`locked_at`, `locked_until`, `worker_id`, `attempt_no`, `next_attempt_at`, `last_error`, `provider_message_id`. Worker claims with `FOR UPDATE SKIP LOCKED` or equivalent, supports stale-SENDING recovery and bounded retry.

## Enqueue
Candidate Submit/Update notification is enqueued in the same business transaction as Submission change; frontend never performs a second independent “send” call for required system notifications.

## Recipient allowlist
System email recipients derive from the referenced Candidate/Participant/entity and email type. Arbitrary recipient override requires a separately authorized manual-email capability.

Phase 1 has no system-email attachments. A future attachment feature requires a separate change request with immutable document-version references and attachment-class allowlists.

## User-facing history
Frozen business rule remains: HR may delete wrong/test Email History. The immutable audit still records send/delete activity.

## Provider
Production uses approved custom SMTP/provider with SPF/DKIM/DMARC. Auth OTP and recruitment operational email may share infrastructure but have separate templates/rate limits/telemetry.

## Phase 1 attachment policy
System-generated email attachments are **deferred beyond Phase 1**. Outbox does not resolve mutable logical documents for sending. Preview and send use recipient/subject/body only.

Delivery guarantee wording: **at-least-once with idempotent enqueue and best-effort deduplication**. A provider-accepted email followed by worker crash before `SENT` persistence may be delivered twice unless the selected provider offers its own idempotency guarantee.

## Retry and delivery semantics
Two retry layers are distinct:
1. **Client/API retry:** same logical idempotency scope/key must not create a duplicate logical Outbox row.
2. **Worker/provider delivery retry:** remains at-least-once. Provider-accepted mail followed by worker failure before local `SENT` persistence can result in duplicate recipient delivery.

Specifications and acceptance tests must use “prevent duplicate logical enqueue” for layer 1 and must never promise exactly-once recipient delivery for layer 2.

Candidate Submission notification rows carry nullable `submission_id` so a Submit/Update email is traceable to the exact Submission even when one Candidate has many historical Submissions.



---

<!-- SOURCE: 44_DEPLOYMENT_OPERATIONS.md -->

# 44. Deployment & Operations — v1.8

## 1. Environments

Tối thiểu:
- Local Development;
- Staging/UAT;
- Production.

Vercel Preview có thể dùng cho PR. Supabase preview branch có thể map với Vercel preview, nhưng mỗi preview phải chạy security/invariant smoke tests.

Production data không dùng làm seed cho preview.

## 2. Recommended mapping

- Vercel Development → local Supabase hoặc dedicated dev.
- Vercel Preview/PR → Supabase preview branch/isolated non-prod data.
- Staging final UAT → persistent isolated Supabase environment.
- Vercel Production → production Supabase only.

## 3. Environment variables

Browser-safe:
- Supabase URL;
- Supabase publishable key.

Server-only:
- Supabase secret/service role;
- mail provider keys;
- Vercel deployment token;
- other secrets.

Không commit secret vào repo. Deployment/API tokens phải nằm trong secure CI/Vercel secrets hoặc sensitive environment variables; không hard-code trong source hoặc shell history.

## 4. Migrations

- schema changes qua version-controlled migrations;
- migration CI checks;
- apply staging before production;
- rollback/forward-fix runbook;
- seed only master/test data phù hợp, không production PII.

## 5. Preview branch risk guard

Tại thời điểm technical review 02/09/2026 có open Supabase GitHub issue (#49426) báo cáo preview branch có thể diverge ở một số object privileges và `auth.users` triggers. Đây là **risk signal, không phải platform guarantee**.

Vì vậy không mặc định Preview = Production-equivalent. CI/UAT bắt buộc verify:
- RLS enabled;
- expected grants/revokes;
- auth triggers/functions;
- root admin protection;
- security-invoker/private views.

## 6. Backup / restore

Go-live checklist:
- DB scheduled backups/PITR phù hợp;
- Storage object recovery strategy;
- documented RPO/RTO;
- restore drill trên non-prod;
- verify document metadata ↔ object consistency sau restore.

## 7. Monitoring

Alert tối thiểu:
- auth anomaly/failure spikes;
- application/RPC error rate;
- DB resource/slow query;
- storage failures;
- email failure queue;
- backup failures;
- deployment failures.

## 8. Deployment discipline

- default preview deployment;
- production deploy qua protected branch/review;
- no direct manual production DB edits ngoài emergency runbook;
- post-deploy smoke tests.


## 9. Dependency pinning / Auth regression
- Commit package lockfile.
- Pin Next.js, Supabase JS/SSR and security-sensitive dependencies to reviewed versions; do not let coding agents silently float to latest during implementation.
- Renovate/Dependabot-style updates run through CI.
- Any Supabase Auth/SSR upgrade reruns login, refresh, callback, inactive-user, Candidate OTP provisioning and RLS persona regression tests.

## 10. Capacity monitoring
No automatic business-data purge. Monitor purchased DB/Storage quota and alert Admin at configurable thresholds (recommended 70/85/95%). Capacity response is upgrade or controlled export/archive + explicit purge under approved procedure.

## Form-session, malware and recovery operations
- Deploy a scheduled cleanup for expired Candidate Form Sessions/temp uploads with metrics and alerting.
- Malware scanning service/process is a go-live dependency because legacy external Office formats are accepted.
- Root Admin break-glass procedure is documented in `61_ROOT_ADMIN_BREAK_GLASS_RECOVERY.md` and must be rehearsed in staging.
- Monitor Storage capacity and staged-upload backlog separately from final document storage.

## Dependency baseline at implementation scaffold
Before the code repository is scaffolded, follow `76_DEPENDENCY_BASELINE_POLICY.md`: select current patched supported Node/Next.js/React/Supabase packages at implementation date, pin exact reviewed versions through `package.json` + lockfile, record the baseline, and rerun Auth/security regression on upgrades. Do not copy transient version numbers from historical review notes into the long-lived product specification.

Privacy Notice publication/current-switch rehearsal follows `78_PRIVACY_NOTICE_PUBLICATION_RUNBOOK.md`; production evidence must show no unintended no-current/effective gap.



---

<!-- SOURCE: 45_PRODUCTION_UAT_GATE.md -->

# 45. Production UAT Gate — v1.8

Không go-live nếu còn P0/P1 security/data-integrity blocker.

## A. Business regression

- Candidate → Submission → Application → multi-round Interview → Report → final outcome.
- Multiple Applications.
- Delete/Inactive.
- permission variants.
- VI/EN.
- current round/PDF.
- decision source based on `decision_updated_at`.

## B. Auth/RBAC

- Candidate cannot access another Candidate.
- HR limited cannot call forbidden RPC even via devtools/direct request.
- Interviewer cannot access non-participant records.
- Inactive user blocked.
- Root Admin protected.
- service-role never present in client bundle/network.

## C. RLS/View/Grant

Test all SELECT/INSERT/UPDATE/DELETE/RPC combinations by persona.

Verify private/security-invoker views do not leak rows.

## D. Schedule

- interviewer conflict block;
- room conflict block;
- Candidate conflict blocking;
- race: 2 HR save overlapping schedule simultaneously.

## E. Concurrency

- HR vs HR stale block;
- same Interviewer multi-tab stale block;
- HR vs Interviewer different fields merge safely;
- same field conflict follows Interviewer-wins rule;
- qualitative edit does not change Final Decision Source;
- decision-field edit does.

## F. Storage

- forbidden MIME/size block;
- block 6th current file and >5 MB file;
- reserve/finalize/orphan cleanup test;
- Candidate path isolation;
- Interviewer document isolation;
- inactive access block;
- signed/authenticated preview expiration/access tests;
- malware scanning is mandatory: `PENDING` cannot finalize; `INFECTED` rejects; `ERROR`/scanner unavailable fails closed under defined retry; only `CLEAN` is eligible.

## G. Email

- outbox idempotency;
- retry temporary failure;
- permanent failure visible;
- no duplicate enqueue on refresh/double click; provider retry semantics tested/documented as at-least-once;
- deleted user-facing History still leaves audit event.

## H. Responsive

Before go-live:
- Candidate Login/Form/Phiếu của tôi mobile-ready;
- internal HR target viewport documented;
- keyboard/focus/a11y smoke tests.

## I. Recovery

- DB restore test PASS;
- Storage recovery test PASS;
- root admin recovery procedure tested without weakening normal protections.

## J. Compliance

- privacy notice approved;
- current no-auto-purge policy + capacity/archive procedure approved; legal review confirms any mandatory retention/deletion obligations;
- data request/purge process documented;
- vendor/data-location review approved if required.


## K. Technical conformance
- Schema Conformance Matrix matches migrations.
- Command Coverage Matrix has no unmapped production mutation.
- Package validator fails closed when a source parser unexpectedly returns zero expected values.
- Search/index performance meets NFR baseline using realistic staging data.
- Status color contrast meets WCAG 2.2 AA for normal 16px text.

## Candidate Form, concurrency and identity gate checks
- [ ] Pre-submit upload works without pre-creating Submission.
- [ ] Candidate Cancel after staged replace/delete leaves persisted current documents unchanged.
- [ ] Malware scan blocks INFECTED/ERROR/not-clean file finalization.
- [ ] Concurrent Submission outcome changes produce correct derived status.
- [ ] Concurrent reschedule/add-participant race test passes.
- [ ] First Google login binds only exact active allowlisted unbound internal user.
- [ ] Root break-glass recovery rehearsed with audit evidence.
- [ ] Referenced master structural changes are rejected; inactive historical references remain operable.
- [ ] Grouped pagination does not split Candidate/Application groups.
- [ ] System emails contain no attachments in Phase 1.


## L. Browser / click-path / accessibility evidence
Run staging evidence at 375, 768, 1280, 1440px per `75_RELEASE_EVIDENCE_MATRIX.md`. Evidence includes axe plus keyboard-only journeys, focus visibility/return, screen-reader form/landmark sanity, 200% text zoom without functional loss, and 400% reflow where WCAG SC 1.4.10 applies. Wide semantic data tables may intentionally retain two-dimensional scrolling. Missing visual baseline = `INCONCLUSIVE`, not PASS.

## Scanner fail-closed evidence
Production malware scanning is mandatory, not feature-optional. UAT must evidence: `PENDING` cannot finalize; `INFECTED` rejects; `ERROR`/scanner unavailable fails closed with controlled retry/recovery; only `CLEAN` is eligible for finalize. There is no production bypass for accepted Candidate/Interview files.

Privacy Notice publication/current-switch rehearsal follows `78_PRIVACY_NOTICE_PUBLICATION_RUNBOOK.md`; production evidence must show no unintended no-current/effective gap.



---

<!-- SOURCE: 46_AUTH_IDENTITY_MODEL.md -->

# 46. Authentication & Identity Model — v1.8

## Internal User
Production: Google Workspace OAuth only. Access requires verified `@eiu.edu.vn`, matching Active `app_users`. OAuth does not grant HR permissions by itself.

### Identity change
- `auth_user_id IS NULL`: HR with `users.directory_manage` may correct an EIU email typo.
- after bind: email/auth/provider binding is security identity; Root-only `users.identity_manage` in Phase 1.
- Root Admin identity itself changes only through documented recovery procedure.

## Candidate
Production method is **Email OTP code**. Verified email is Candidate identity; email is read-only in form/profile. Inactive Candidate cannot access Portal. OTP request/login/submission endpoints require rate limits.

### First login/provisioning
Trusted atomic provisioning: resolve current `auth_user_id`; fallback by verified normalized email; create Candidate if absent; safely bind recreated Auth identity to existing Candidate when appropriate; block inactive Candidate; audit. Frontend cannot create duplicate Candidate directly.

## Next.js/Supabase SSR
Use App Router + cookie session and the supported Supabase SSR approach for the pinned project version. Pin package versions + lockfile; CI includes auth/session regression when upgrading Supabase/Next.js dependencies.

## Internal first Google login
`provision_internal_identity_on_first_google_login()` is distinct from identity-change/rebind. Preconditions: provider Google, verified normalized `@eiu.edu.vn`, active allowlisted `app_users` exact email match, `auth_user_id IS NULL`, and current Auth ID is not bound elsewhere. It atomically binds + audits. If the directory row is already bound to a different Auth identity, reject and require Root-only recovery/rebind path.

Root Admin identity recovery is governed by `61_ROOT_ADMIN_BREAK_GLASS_RECOVERY.md`, never ordinary directory edit.



---

<!-- SOURCE: 47_AUDIT_LOGGING_SPEC.md -->

# 47. Audit Logging Specification — v1.8

## 1. Hai khái niệm tách biệt

### Business Activity Log
Dùng cho HR xem lịch sử nghiệp vụ.

### Security Audit Log
Immutable/privileged, phục vụ trace quyền và dữ liệu nhạy cảm.

Việc HR xóa một Email History record **không xóa Security Audit Log**.

## 2. Events bắt buộc

- login success/failure (theo privacy policy);
- candidate submit/update;
- sensitive candidate read/download nếu policy yêu cầu;
- HR edit;
- status change;
- candidate active/inactive;
- Application create/update/delete/inactive;
- Interview create/copy/reschedule/delete/inactive;
- participant add/remove/reorder/re-add;
- report create/edit;
- final decision source change;
- permission grant/revoke;
- root admin action;
- PDF generation/download;
- email queue/send/fail/delete-history;
- file upload/download/delete;
- concurrency conflict/override outcome.

## 3. Fields

- audit id;
- timestamp;
- actor auth/app user id;
- actor type/persona;
- action;
- entity type/id;
- request id;
- correlation id;
- old/new selected values or diff;
- reason when applicable;
- source (`WEB/RPC/SYSTEM/WORKER`);
- result (`SUCCESS/DENIED/FAILED`);
- safe metadata.

## 4. Không log

- passwords/OTP;
- access/refresh token;
- secret/service-role key;
- full uploaded file content;
- long-lived signed URL token;
- unnecessary sensitive personal content.

## 5. Access

Security audit log không accessible cho Candidate/Interviewer và chỉ accessible cho Root Admin hoặc explicitly authorized security/admin role.

## Mandatory lifecycle and security audit events
Mandatory audit events include internal first-bind, Root break-glass recovery, HR-role removal, Application Reactivate, referenced-master structural-change denial, Candidate Form Session submit/cancel/expiry cleanup summary, malware-scan rejection and unused hard-delete commands. Do not store OTPs, signed URLs, secrets or file contents in audit metadata.



---

<!-- SOURCE: 48_IDEMPOTENCY_CONCURRENCY_SPEC.md -->

# 48. Idempotency & Concurrency Specification — v1.8

## Idempotency
Required for Candidate Submit, Create Application, Create Next Round, Copy/Save logical schedule mutation where retry can duplicate, enqueue email, finalize upload, persisted PDF generation. Same actor/scope/command/key returns prior result.

## Optimistic locking
Mutable entities use `version_no`; client sends expected version. Stale update fails unless the specific report merge algorithm safely merges disjoint patches.

## Report concurrency
Each Interviewer owns a distinct report. HR may edit that report with permission. Patch only changed fields. Disjoint field changes can merge. Same-field conflict: Interviewer ownership wins; HR stale write is rejected/reloaded. No stale whole-row overwrite.

Decision fields form one logical block for source semantics; any final-field change updates `decision_updated_at/by`; qualitative edits do not. Timestamp + report UUID tie-break is sufficient Phase 1; revision sequence is optional P2 hardening.

## Mandatory schedule consistency
Transaction alone under Read Committed is insufficient. Every mutation that can create/restore an operational interval must:
1. identify Candidate, Room, current Interviewers;
2. acquire transaction-level advisory locks in deterministic sorted resource order;
3. re-query conflicts;
4. mutate;
5. commit.

Shared engine applies to **Save Copy (`copy_interview_schedule`)**, save/reschedule, add/re-add participant when scheduled, reactivate, and CANCELLED→active status. Save Copy is not a client-only final mutation: the client draft remains non-mutating, while the trusted Save Copy command uses this shared deterministic Candidate/Room/Interviewer lock + conflict engine before commit.

Interval semantic: `[start_at,end_at)`. Do not use the legacy overloaded `effective_active` term. Canonical predicates are:
- `access_active` = active Application + active Interview;
- `resource_blocking` = `access_active` + schedule status not `CANCELLED` + both interval endpoints present.
Every `resource_blocking` Interview participates in conflict checks, whether or not it is Current Round.

## Participant concurrency
Add/remove/re-add/reorder lock the Interview. Reorder writes a complete ordered set; no duplicate current order. Re-add to an already scheduled Interview revalidates conflict.

## Round allocation
Lock Application, then allocate max round+1.

## Mandatory lock order
For all Interview resource mutations: lock **Interview row first** → resolve parent/Candidate → snapshot current Room/Participants → acquire deterministic advisory/resource locks → re-read participant/resource set → conflict check → mutate. This closes reschedule ↔ add/re-add participant races.

For all Application/current-round/report-outcome mutations: lock parent **Submission** before authoritative status recalculation.

Candidate Save/Submit uses form-session idempotency; staged file changes and text commit together.


## Application Reactivate concurrency
`reactivate_application()` locks the durable Application identity/Submission, revalidates eligible Active HR/root ownership, then enumerates every non-elapsed child Interview that would become `reactivation_conflict_relevant = resource_blocking AND end_at > transaction_now`. It acquires resource locks in deterministic global order and re-checks Candidate/Room/Interviewer overlaps before enabling the parent. Reactivation is all-or-nothing for non-elapsed operational intervals. Fully elapsed intervals remain historical and do not block lifecycle recovery even if another historical record overlaps the same past interval.



---

<!-- SOURCE: 50_OWNER_DECISIONS_PENDING.md -->

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



---

<!-- SOURCE: 51_SOURCE_REFERENCES.md -->

# 51. Source References Used for Technical / Design Audit

**Reviewed:** 02/09/2026

These references inform implementation guardrails. They do not override frozen EIU business decisions.

## Product / Design references
- EIU MedLabs repository: `https://github.com/baonguyen1301/eiu-medlabs`
- UI/UX Pro Max Skill: `https://github.com/nextlevelbuilder/ui-ux-pro-max-skill`
- Vercel Agent Skills: `https://github.com/vercel-labs/agent-skills`
  - React Best Practices
  - Web Design Guidelines

## Platform references
- Supabase monorepo: `https://github.com/supabase/supabase`
- Supabase Row Level Security docs: `https://supabase.com/docs/guides/database/postgres/row-level-security`
- Supabase Tables/View security docs: `https://supabase.com/docs/guides/database/tables`
- Supabase SSR/Auth server package guidance: `https://supabase.com/docs/guides/auth/choosing-a-server-package`
- Supabase Next.js SSR client guidance: `https://supabase.com/docs/guides/auth/server-side/creating-a-client`
- Supabase Storage buckets/private access: `https://supabase.com/docs/guides/storage/buckets/fundamentals`
- Supabase Storage downloads/signed URLs: `https://supabase.com/docs/guides/storage/serving/downloads`
- Supabase Auth rate limits: `https://supabase.com/docs/guides/auth/rate-limits`
- Supabase Database Backups: `https://supabase.com/docs/guides/platform/backups`
- Supabase Production Checklist: `https://supabase.com/docs/guides/deployment/going-into-prod`

## Next.js / Vercel platform references
- Next.js Authentication / Authorization guide: `https://nextjs.org/docs/app/guides/authentication`
- Next.js Production Checklist: `https://nextjs.org/docs/app/guides/production-checklist`
- Vercel Environments: `https://vercel.com/docs/deployments/environments`
- Vercel Environment Variables: `https://vercel.com/docs/environment-variables`
- Vercel Deployment Protection: `https://vercel.com/docs/deployment-protection`

## Preview-branch risk note
An open Supabase GitHub issue reported preview branches not preserving some object privileges and `auth.users` triggers at the time of review:
- `https://github.com/supabase/supabase/issues/49426`

This is treated as a **risk signal, not a platform guarantee**. Therefore final UAT uses persistent isolated staging and CI verifies grants/RLS/triggers explicitly.



---

<!-- SOURCE: 52_TECHNICAL_GATE_STATUS.md -->

# 52. Technical Gate Status — CURRENT v1.17

- Business Logic Core v1.2: **FROZEN**
- Design System v1.8: **CURRENT / REVIEWED**
- Responsive Prototype v1.10: **CROSS-LAYER-ALIGNED / READY FOR OWNER VISUAL UAT / NOT FROZEN**
- Technical Architecture v1.17: **TECHNICAL SPECIFICATION FROZEN**
- Implementation Gate: **READY TO IMPLEMENT**
- Implementation Validation / Migration Freeze: **PENDING ACTUAL CODE EVIDENCE**
- Production Ready: **NO**

Current review-alignment resolution: `97_INDEPENDENT_REVIEW_IMPLEMENTATION_ALIGNMENT_V1_17.md`.
Latest independent planning review evidence: `review_inputs/independent_planner_review_v1_0_vs_handover_v1_15_2026-09-03.md`; doc 97 records its source alignment.
Current canonical predicates: `73_DOMAIN_GLOSSARY_AND_CANONICAL_PREDICATES.md`.
Privacy publication procedure: `78_PRIVACY_NOTICE_PUBLICATION_RUNBOOK.md`.
Current responsive integration: `81_RESPONSIVE_PROTOTYPE_INTEGRATION.md`.
Current pre-code/implementation authorization gate: `98_TECHNICAL_PRECODE_GATE_V1_17.md`.

`READY TO IMPLEMENT` is a source gate, not an instruction to run an old/draft executor prompt. Executor authorization remains explicit in the current prompt/workflow.



---

<!-- SOURCE: 53_FINAL_CONSISTENCY_VALIDATION.md -->

# 53. Final Consistency Validation — v1.17

**Validation date:** 03/09/2026  
**Baseline:** Full Handover v1.17 + Technical Architecture v1.17 + Design System v1.8 + Responsive Prototype v1.10

## Working-package validation evidence
- Full Handover semantic/cross-design/responsive validator: **511/511 PASS**.
- Design System validator: **73/73 PASS — 0 FAIL**.
- Responsive Browser QA v1.10: **108/108 PASS** across 360 / 390 / 430 / 768 / 1024 / 1280 px.
- Acceptance IDs: unique.
- Trusted commands: **59 unique**; the overlapping bulk writer was removed and Candidate-level bulk latest-Submission semantics are ALL_OR_NOTHING.
- Source registry/current pointers: current Review Alignment **97** / Gate **98**; superseded review/gate files are historical only.
- Candidate lifecycle and Submission workflow are separated; parent rows derive deterministic latest Submission state.
- Report Status belongs to Current Interview; Application outcome is derived; Final Decision Source uses `decisionUpdatedAt`.
- Candidate NEW/EDIT enforces CV required and staged ADD / REPLACE / DELETE with Cancel-discard and stale-save blocking.
- Internal user email DB invariant uses exact `@eiu.edu.vn` domain matching.
- Critical production-intent controls require a named state transition; generic toast-only fallback is not accepted as PASS.
- Deterministic CURRENT-only All-in-One regeneration equality: PASS.

## Meaning of PASS
These results prove consistency of the **specification and executable review prototype against the implemented validators/browser QA**. They do not prove future executable migrations/RLS, real concurrency, Storage/provider integrations, production accessibility conformance, backup/restore, deployment, or production security configuration.

## Required final-delivery verification
The released ZIP must be extracted and validated again from extracted contents, including MANIFEST SHA-256 verification, deterministic All-in-One check, Responsive v1.10 browser QA evidence and ZIP integrity test. Final extracted-package counts are recorded in `PACKAGE_VALIDATION.txt`, `DESIGN_VALIDATION.txt`, and `responsive_prototype/RESPONSIVE_BROWSER_QA_v1.10.md`.

## Gate status
Business Logic Core remains **FROZEN**. Technical Architecture v1.17 is **TECHNICAL SPECIFICATION FROZEN** and the source-level Implementation Gate is **READY TO IMPLEMENT**. Responsive Prototype v1.10 remains **READY FOR OWNER VISUAL UAT / NOT YET FROZEN**. Actual migration/RLS/RPC/race/storage/performance/backup/deployment evidence is required later at **Implementation Validation / Migration Freeze**. Production Ready remains **NO**.



---

<!-- SOURCE: 54_SCHEMA_CONFORMANCE_MATRIX.md -->

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



---

<!-- SOURCE: 55_COMMAND_COVERAGE_MATRIX.md -->

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



---

<!-- SOURCE: 58_SEARCH_AND_INDEXING_STRATEGY.md -->

# 58. Search & Indexing Strategy — v1.8

## Goal
Support HR search by Candidate/Submission Name, Email, Phone and operational filters without browser-side full scans.

## Query model
- Server-side search/pagination only for growing datasets.
- Text input debounce: 300 ms.
- Name broad search: minimum 2 characters.
- Exact/near-exact email and phone may query immediately.
- Default page size 25; options 25/50/100.

## Index baseline
Starter schema enables `pg_trgm` and includes:
- trigram GIN on `submissions.full_name`;
- lower-case email index;
- digit-normalized phone expression index;
- status/date and parent FK indexes.

For Vietnamese accent-insensitive search, implementation must choose and test one normalized strategy before performance UAT:
1. persist normalized searchable value during trusted write command; or
2. use a vetted immutable normalization wrapper/function suitable for an expression index.

Do not ship an unindexed `ILIKE '%keyword%'` full-table strategy as the only implementation for large datasets.

## Selector search
Application selector returns **Submission rows**, not Candidate-only rows. Result item includes Candidate name/email plus Submission timestamp/status and stable `submission_id`.

## URL state
Where practical, list page filters/sort/page are represented in URL query state so back/forward/share/reload are predictable. Sensitive search terms should not be copied into telemetry.

## Performance gate
Use the NFR dataset baseline and verify p95 list/search target with realistic indexes via `EXPLAIN (ANALYZE, BUFFERS)` in staging.

## Grouped pagination and PII search rule
- Application Inbox paginates Candidate groups; child submissions are included/lazy fetched under that Candidate.
- Interview and HR Report paginate Application groups.
- Stable sort always adds immutable ID tie-breaker.
- Name/email/phone search text is not persisted in URL, browser history or shareable filter links. URL may carry page/sort/status/non-sensitive filters.

## PII request transport
Name/email/phone search values are request/client state and are not serialized into browser URLs. URL may carry page/sort/non-sensitive filters only. Server logs/analytics must redact sensitive query payloads according to `67_WEB_SECURITY_BASELINE.md`.



---

<!-- SOURCE: 59_RLS_POLICY_BLUEPRINT.md -->

# 59. RLS / GRANT Policy Blueprint — v1.8

This is a policy blueprint for migrations, not executable final SQL. It complements `39_SECURITY_RLS_MATRIX.md`.

## Global rules
- `anon`: no direct business-table grants.
- `authenticated`: no broad table DML; grant only minimal SELECT/RPC execute as designed.
- Candidate/HR/Interviewer mutations should primarily use explicit commands/RPCs.
- Secret/service-role stays server-only and must re-authorize before any privileged action.

## Candidate
### Candidate row
SELECT own active Candidate identity. No ordinary UPDATE of email/auth binding.

### Submission
SELECT own. Direct UPDATE is discouraged; command checks Candidate active + `NEW` and DTO allowlist. Candidate cannot SELECT `hr_note` through a broad table/view; expose a candidate-safe projection/RPC if necessary.

### Submission documents
Candidate can access own Submission document metadata/path only through authorized command/signed URL generation.

## HR
Permission helpers evaluate active `app_users`, role/permission, with Root implicit allow.
- `submissions.view`: read only.
- `submissions.status`: authorizes status mutation including open NEW→READ.
- other mutations require their granular code.
- default HR receives all HR codes, but RLS/command still evaluates explicit effective permissions.

## Interviewer
Contextual visibility requires all:
`app_user.is_active`
`application.is_active`
`interview.is_active`
`participant.is_current`
`visible_to_interviewers=true`.

Interviewer report write is limited to the report associated with that current Participant and non-final Report Status. Interviewer may read shared report preview fields but **never** `hr_report_note`.

## Internal identity
`users.directory_manage` can mutate business profile and unbound email typo only. Bound `auth_user_id/email/provider binding` cannot be changed by this permission. Root-only identity command executes through a protected RPC/recovery path.

## Private views
Current Round / effective outcome / final decision views remain `private`. If any public API view is required, use `security_invoker=true`, explicit grants and persona tests.

## Storage
Private buckets. Signed URL generation is a server-authorized operation:
- Candidate → own Submission docs;
- HR → permission-based;
- Interviewer → access-active current Participant + visible Interview docs only.
No Candidate access to HR/interview reports/internal notes.

## Adversarial tests required
Candidate A must fail to access Candidate B; Interviewer A must fail on non-participating session; HR Limited must fail missing permission; inactive internal user fails; parent Application inactive revokes Interviewer contextual access; service-role endpoints must still deny unauthorized caller at server authorization layer.

## Candidate temporary-resource and logical-document policies
Candidate Form Sessions and staged document changes are candidate-owned temporary resources. Candidate access requires authenticated Candidate mapping + active account + ownership; EDIT session additionally requires target Submission `NEW` at mutation time. Final logical document access derives from parent Submission/Interview authorization. `privacy_acknowledgements` authorization derives solely through Submission.

## Identity, lifecycle and delete-permission policies
- Candidate self-rebind is never direct table UPDATE; only trusted OTP provisioning may replace obsolete Auth ID under safe-rebind predicate.
- Directory manager lifecycle predicates exclude HR-role targets and Root.
- Production HR delete permission: `candidates.delete_unused`; Email History delete uses `emails.history_delete`. Submission repair-delete is MAINTENANCE_ONLY, not a normal HR permission.
- Reactivated Application restores `access_active` for active child Interviews. Only non-elapsed children satisfying `reactivation_conflict_relevant = resource_blocking AND end_at > transaction_now` participate in the reactivation conflict re-check; fully elapsed historical overlaps do not block lifecycle recovery. Current Round remains only report/outcome selector.


## Canonical Interviewer predicate source
Use `private.access_active_interviews` (or equivalent inline predicate) for contextual access. Never infer access from `resource_blocking` or Current Round.



---

<!-- SOURCE: 61_ROOT_ADMIN_BREAK_GLASS_RECOVERY.md -->

# 61. Root Admin Break-Glass Recovery Runbook — v1.8

## Purpose
Recover the single Root Admin identity only when normal Google/Auth binding can no longer be used. This is an operational emergency path, not an application UI feature.

## Preconditions
- Incident ticket/change record exists.
- Identity of replacement/recovered EIU account is independently verified.
- Approval by the designated EIU system owner and one additional authorized approver.
- Operator has controlled production database migration/admin access; application secret keys are not used in browser.

## Procedure
1. Put privileged user-management changes into maintenance/restricted mode if practical.
2. Export current Root directory row, Auth mapping reference and relevant audit entries.
3. Verify new Google Workspace email is `@eiu.edu.vn`, active and not bound to another `app_users` row.
4. Execute a **versioned, reviewed one-time migration/function** that is allowed to bypass the normal Root identity trigger only for the exact Root row and exact verified target identity. Never use ad-hoc direct SQL without change record.
5. Update Root `email/auth_user_id` binding atomically; do not change `is_root_admin=true` or Active status.
6. Insert immutable `ROOT_BREAK_GLASS_RECOVERY` security audit event with ticket/change ID, approvers and before/after identity IDs (no tokens/secrets).
7. Revoke old sessions/credentials where supported and force fresh Google login.
8. Verify Root can login and Root-only actions work; verify old identity cannot.
9. Exit maintenance/restricted mode.
10. Record post-incident review and rollback evidence.

## Rollback
The recovery migration must include a reviewed inverse operation using the pre-change snapshot. Rollback is allowed only while the prior identity is still verified and safe.

## Secret custody
- Database/production administrative credentials live in approved secret management, never repository/browser/local shared notes.
- At least two authorized operators should be able to recover access under EIU policy; no single undocumented personal credential should be the only path.

## Testing
Rehearse in isolated staging before go-live and after major Auth/identity changes. Production rehearsal should not change the real Root identity; validate the controlled migration path using a test privileged account.



---

<!-- SOURCE: 62_VALIDATION_CONTRACT.md -->

# 62. Validation Contract — v1.8

Machine-readable source: `validation_contract.yaml`.

The same limits/normalization rules must be consumed or mirrored by frontend validation, trusted backend DTO validation, database checks where appropriate, and automated acceptance tests. Frontend-only validation is never authorization.

Key rules: Candidate email comes from verified Auth; notes/report fields are plain text; raw HTML input is forbidden; HTTPS meeting links in production; max 5 MB/file and max 5 current files; approved extension/MIME/magic-byte validation; max collection sizes; DOB/date sanity; safe filename normalization; PII search is not persisted in URL.



---

<!-- SOURCE: 63_BATCH_OPERATION_SEMANTICS.md -->

# 63. Batch Operation Semantics — v1.12

Bulk UI does not imply one universal transaction policy. Each action maps to a named batch command and declares atomicity.

| Operation | Phase-1 semantics |
|---|---|
| Candidate-level latest Submission Mark New/Read | ALL_OR_NOTHING |
| Bulk common Application assignment | ALL_OR_NOTHING |
| Bulk Inactive/Delete where offered | ALL_OR_NOTHING by default; command may narrow scope before mutation |
| Bulk status transition | ALL_OR_NOTHING unless the specific status command documents per-item mode |
| Bulk email | PER_ITEM_ENQUEUE_RESULT; delivery remains asynchronous |

Partial-mode response must return `success[]` and `failed[{id,error_code}]`. Atomic commands return a single failure with no committed subset. UI must describe the chosen behavior before confirmation.


## Phase-1 visible bulk action registry

| UI bulk action | Selection entity | Named command | Atomicity |
|---|---|---|---|
| Candidate Active/Inactive | Candidate | `bulk_set_candidate_active` | ALL_OR_NOTHING |
| Latest Submission Mark New/Read | Candidate | `bulk_set_latest_submission_manual_status` | ALL_OR_NOTHING |
| Interview Delete/Inactive | Interview | `bulk_delete_or_inactivate_interviews` | ALL_OR_NOTHING |
| Interview Schedule Status | Interview | `bulk_change_interview_schedule_status` | ALL_OR_NOTHING |
| HR Report Status | Current-Round Interview | `bulk_change_report_status` | ALL_OR_NOTHING |
| Email enqueue | exact business recipients/entities | `bulk_enqueue_email` | governed by existing email batch contract |

For Application Inbox manual Submission status, Candidate is the UI selection entity; the server resolves and revalidates each deterministic latest Submission under lock. Historical child Submissions are read-only in this bulk UX.

Frontend code must not emulate these lifecycle/status batches by invoking single-row commands in a loop. A failed precondition/conflict on one selected item returns structured failure and commits none of the selected mutations.

## Permission and lifecycle parity clarification
- `bulk_change_interview_schedule_status` requires `interviews.status` + `interviews.view`, exactly matching the single protected field authorization.
- `bulk_set_latest_submission_manual_status` uses the same manual-status eligibility as the single writer: active Application blocks; Candidate Active/Inactive alone does not.

## Command-specific batch parity — current
- **Candidate lifecycle batch parity:** each selected Candidate receives the same `is_active/inactive_at/inactive_by` state transition and per-Submission reactivation recalculation as `set_candidate_active`; per-Candidate audit plus one batch audit event; any stale item aborts all.
- **Interview delete/inactivate batch:** prevalidate all hard-delete temp-upload cleanup prerequisites and durably capture all required cleanup intents before deleting any selected Interview.
- **Report Status batch:** re-resolve Current Round + optimistic versions for the full set; one stale/current-round mismatch aborts all; successful commit recalculates every affected Submission.



---

<!-- SOURCE: 64_MASTER_DATA_HISTORY_POLICY.md -->

# 64. Master Data Historical Semantics — v1.8

## Core rule
If a master row has never been referenced, it may follow the existing hard-delete rule. Once referenced, it cannot be hard-deleted and its **structural business meaning** cannot be mutated.

Structural examples: Position Unit/Team/Group; Department Team parent Unit; Interview Format room/link requirements; Document Type scope/code. To change structural meaning, create a new row and mark old row Inactive.

## Allowed corrections
Display-label typo/translation corrections may be allowed with optimistic version + audit when they do not change business meaning.

## Inactive semantics
Inactive prevents new selection. Historical records keep the reference and remain readable/operable. An Interview using a format later made inactive can still be cancelled/reactivated/processed as long as the format reference itself is unchanged.

## Room historical-identity policy
A Room already referenced by Interview history cannot be repurposed by changing identity-bearing fields such as room `code` or `building` in a way that changes meaning. Create a new Room and Inactive the old one for a real location change. Typo-only display correction may be allowed with audit when owner accepts historical label correction.



---

<!-- SOURCE: 66_DATA_EXPORT_ARCHIVE_PURGE_RUNBOOK.md -->

# 66. Data Export / Archive / Purge Runbook — v1.8

## Purpose
Operational procedure for the owner-approved capacity policy: retain recruitment data online until EIU decides to expand capacity or export/archive selected data to controlled local storage and explicitly purge selected online copies. This is not an automatic retention scheduler.

## Authorization and approval
- Execution: Root Admin + designated IT/database operator.
- Business approval: HR owner/authorized EIU approver.
- Legal/privacy approval when required by current policy.
- No single operator may silently export then purge without recorded approval.

## Export scope manifest
Before export freeze a manifest: entity/date scope, Candidates, Submissions, Applications, Interviews, Reports, Email History, documents, row counts, object counts, schema/app version, UTC timestamp and operator IDs.

## Archive format/security
- Structured data: documented machine-readable export (CSV/JSON/SQL dump as appropriate).
- Files: original immutable object versions + metadata manifest.
- Encrypt archive at rest and in transit; keys stored separately under EIU-controlled custody.
- Destination must be EIU-controlled access-restricted local/archive storage.
- Generate SHA-256 manifest for every archive bundle/object set.

## Verification before purge
1. Compare source vs archive row/object counts.
2. Verify checksums.
3. Restore a representative sample into isolated environment and prove records/files readable.
4. Reconcile orphan/missing Storage objects.
5. Record approval to proceed.

## Purge
Purge only the exact approved scope through trusted maintenance command/migration. Preserve immutable security audit required by policy. Delete Storage objects and relational rows in a documented order. Never purge a partially verified archive.

## Failure / rollback
If export, checksum, restore or reconciliation fails: stop; do not purge. If purge partially fails, retain failure manifest and resume only with idempotent scope tracking.

## Evidence
Store approval IDs, manifest, checksums, counts, restore-test evidence, purge result, operator IDs, timestamps and audit references.



---

<!-- SOURCE: 67_WEB_SECURITY_BASELINE.md -->

# 67. Web Security Baseline — v1.8

This is the production target behavior for Vercel/Next.js + Supabase. Framework syntax may differ, but evidence must prove the behavior.

## Transport and headers
- HTTPS only. Production HSTS target: `max-age=31536000; includeSubDomains` after domain readiness is verified.
- `Content-Security-Policy`: default deny-by-omission; baseline includes `default-src 'self'`, `object-src 'none'`, `base-uri 'self'`, `frame-ancestors 'none'`, `form-action 'self'`; script/style/connect/img/font sources are allowlisted for the pinned app/Supabase/Vercel assets actually used. Prefer nonce/hash-compatible CSP rather than `unsafe-inline` where feasible.
- `X-Content-Type-Options: nosniff`.
- `Referrer-Policy: strict-origin-when-cross-origin` or stricter.
- `Permissions-Policy`: deny camera/microphone/geolocation and other unused powerful features.
- Clickjacking protection: CSP `frame-ancestors 'none'`; `X-Frame-Options: DENY` fallback where supported.

## Cookies/session
Auth/session cookies: Secure in production, HttpOnly when managed server-side, appropriate SameSite (normally Lax unless a verified OAuth flow requires otherwise), scoped Path/Domain, no secrets in browser storage.

## CSRF / origin
Cookie-authenticated state-changing Server Actions/RPC/API routes validate authenticated session plus same-origin/approved Origin/Host semantics. Do not rely on SameSite alone for privileged mutations.

## CORS
No wildcard CORS for credentialed recruitment APIs. Allow only explicit production/staging origins that need browser access.

## Sensitive caching
PII HTML/API/RPC/file metadata responses default `Cache-Control: private, no-store` unless a reviewed safer exception exists. Private file URLs are short-lived; no shared CDN cache of authenticated PII responses.

## Logging/error redaction
Do not log OTP, session cookies, access/refresh tokens, secret keys, raw CV content, full document URLs with signatures, or unnecessary PII search terms. Production errors return stable codes; sensitive internals stay server logs with redaction.

## Test evidence
Automated header tests, CSRF/origin negative tests, CORS tests, cookie flags, cache-control tests, log-redaction tests and security scan evidence are Production UAT gates.



---

<!-- SOURCE: 68_RATE_LIMIT_POLICY.md -->

# 68. Rate Limit Policy — v1.8

Initial defaults are configuration, not immutable business rules. Security/load testing may tune them before go-live while preserving the strategy and auditability.

| Action | Primary key | Secondary key | Initial default | Response |
|---|---|---|---|---|
| Candidate OTP request | normalized email | client IP | 5 / 15 min per email; 20 / 15 min per IP | 429 + Retry-After |
| OTP verify | auth/session/email | client IP | 10 / 15 min identity; 50 / 15 min IP | 429 + Retry-After |
| Candidate Submit | candidate_id | IP | 5 / hour; 20 / day | 429 |
| Upload reserve/finalize | candidate/app_user | IP | 30 / 15 min identity; 100 / 15 min IP | 429 |
| Internal search | app_user_id | — | 120 / min | 429 |
| Manual/system email enqueue | app_user_id + email_type | entity | 60 / hour; burst 10 / min | 429 |
| PDF generation | app_user_id | entity | 20 / hour | 429 |

## Implementation rules
- Use provider-native/distributed durable counters suitable for multi-instance Vercel execution; never in-process memory only.
- Resolve trusted client IP only through approved proxy/platform headers; do not trust arbitrary forwarded headers.
- Rate-limit decisions do not replace Auth/RLS/permission checks.
- OTP provider limits may be stricter; the effective limit is the stricter bound.
- Security Audit records repeated abuse/blocks without storing secrets.
- Staging includes burst, distributed-instance and bypass/forged-header tests.


## Candidate Update / system notification
| Endpoint/action | Primary key | Default | Behavior |
|---|---|---:|---|
| Candidate Update Save | `candidate_id + IP` | 30 / 15 min | `429 + Retry-After` before mutation execution; no partial Save |
| Candidate system HR-notification enqueue | `candidate_id + submission_id + email_type + mutation idempotency key` | idempotent per successful Save | Delivery throttle must not roll back valid Candidate Save; Outbox enqueue is transactional and provider delivery asynchronous |

## Candidate Update system-side-effect rule
Candidate Update uses the Candidate mutation endpoint limit keyed by Candidate identity + IP/session according to the table above. The exact-Submission HR notification is a committed system Outbox side effect; downstream email throttling/coalescing must not roll back a valid Candidate Save. Provider delivery rate controls act asynchronously after commit.



---

<!-- SOURCE: 70_SEMANTIC_VALIDATION_GATE.md -->

# 70. Semantic Cross-layer Validation Gate — v1.17

**Status:** CURRENT / NORMATIVE

The validator must fail on semantic drift, not only missing files or tokens. Current expected package versions are **Technical Architecture v1.17** and **Design System v1.8**.

## Mandatory semantic checks
1. **Source governance:** CURRENT entrypoints point to Alignment Resolution 93, Domain Glossary 73, Privacy Publication Runbook 78, Responsive Integration 81 and Pre-code Gate 94. HISTORICAL/SUPERSEDED modules are excluded from normative All-in-One.
2. **Acceptance traceability:** Acceptance IDs are unique; command acceptance references exist and behavior-specific commands carry required guarantee tags.
3. **One protected mutable field → one command:** `interviews.report_status_code` has exactly one trusted writer (`change_report_status`); `update_hr_report_note` cannot write Report Status.
4. **Outcome side effects:** every Application/current-round/outcome-changing command declares authoritative Submission recalculation where required.
5. **Submission state matrix:** generic no-active-Application recalculation preserves manual NEW/READ; derived states fall to READ; Candidate Reactivation/no-active-Application is the explicit READ exception.
6. **Canonical Interview predicates:** `access_active`, `current_round`, and `resource_blocking` are the normal domain predicates. `reactivation_conflict_relevant` is explicitly **Application Reactivate-only** (`resource_blocking AND end_at > transaction_now`). Interviewer access always includes parent Application active.
7. **Document target integrity:** Candidate and HR REPLACE/DELETE require the target logical document to have exactly one current version at stage/mutation time and again under lock at Save; historical logical targets cannot resurrect or bypass max-five/CV invariants.
8. **Candidate EDIT privacy:** EDIT Form Session pins an authoritative current/effective Privacy Notice and Save records/reuses the exact acknowledgement. Published notice content is immutable; publication switching follows Runbook 78.
9. **Candidate side effects:** Candidate Update notification is enqueued in the same business transaction; file-only changes bump aggregate version; latest-surviving Submission drives current-profile cache.
10. **Email History:** view/delete uses exact permissions plus parent contextual access; cleanup eligibility is deterministic and audited.
11. **Owner lifecycle:** active/reactivated Applications require an eligible Active HR/root owner; HR deactivation/role removal cannot strand active owned Applications.
12. **Application Reactivation:** fully elapsed historical intervals do not block lifecycle recovery; non-elapsed conflict-relevant intervals use the shared conflict engine.
13. **Permission-display scope:** non-root directory managers do not see another user's granular effective permissions.
14. **Report lifecycle:** only canonical active/current or inactive/archived report flag combinations are physically valid.
15. **Application durable identity:** exact Submission+Unit+Team+Position is globally unique; the zero UUID used for NULL-Team indexing is physically reserved and cannot be a real Team key.
16. **Email/malware/upload:** provider delivery is at-least-once; client retry prevents duplicate logical enqueue only; malware CLEAN and frozen Phase-1 whitelist/5 MB/max-five rules are mandatory.
17. **Delete lifecycle:** unused hard-delete capabilities map to exact permissions or explicit MAINTENANCE_ONLY paths; empty auto Round 1 exception is consistent.
18. **Current-source consolidation:** CURRENT/NORMATIVE modules state canonical behavior in place and do not rely on later versioned clarification blocks to override earlier text.
19. **Version coherence:** schema/design/current status headers match Technical v1.17 / Design v1.8 / Responsive Prototype v1.10.
20. **Batch selection entity coherence:** Application Inbox checkbox entity = Candidate; `bulk_set_latest_submission_manual_status` accepts Candidate IDs, resolves deterministic latest Submission under lock, revalidates expected latest IDs/versions, and is the only active batch writer for manual NEW/READ.
21. **Candidate lifecycle separation:** Candidate Inactive never appears in the Submission status enum or writes `INACTIVE` to Submission; parent Candidate summary derives latest Submission state.
22. **Phase-1 navigation:** rendered persona routes are a subset of the frozen Phase-1 navigation registry; `FUTURE_HIDDEN / NOT_RENDERED` routes are absent from ordinary UAT navigation.
23. **Report decision/source semantics:** Report Status writes Current Interview only; qualitative-only report edits do not move `decisionUpdatedAt` or Final Decision Source; aggregate HR Report drawer has no generic Delete.
24. **Candidate CV/edit semantics:** CV remains required after staged ADD/REPLACE/DELETE; Cancel discards staged changes; Save revalidates editability before atomic materialization.
25. **Critical controls:** critical production-intent controls require a declared expected transition/navigation/dialog and cannot PASS solely on generic toast fallback.
26. **Generated artifact equality:** `15_ALL_IN_ONE_SPEC.md` regenerates byte-for-byte from CURRENT/NORMATIVE numbered modules only.

PASS proves specification consistency against implemented checks only. It does **not** prove executable migrations/RLS, real race behavior, provider integrations, security configuration, backup/restore, rendered UI, accessibility or production readiness.
21. **Forbidden legacy canonical patterns:** CURRENT/NORMATIVE source must not contain the legacy Application-Reactivate rule `re-checks every child that would become resource-blocking`; canonical behavior is non-elapsed `reactivation_conflict_relevant` only.
22. **Nullable master-reference parity:** optional Education `qualification_id=NULL` must bypass active-master validation; changed non-null references still require an Active master.
23. **Bulk schedule operational parity:** single and bulk schedule-status writers share Active-current-Participant eligibility plus Candidate/Room/Interviewer conflict recheck.
24. **Current baseline coherence:** machine current-baseline blocks and current README/VERSION authority must resolve to Full/Technical v1.17 + Design v1.8 + Responsive v1.10.

25. **Critical-control executable parity:** single and bulk Interview Schedule Status critical controls must map to Responsive browser QA and share operational guards.
26. **Interview upload delete integrity:** `upload_reservations.interview_id` is FK RESTRICT; hard-delete requires durable `storage_cleanup_queue` capture before reservation removal.
27. **Bulk Candidate lifecycle parity:** machine registry declares inactive metadata, per-Submission reactivation recalculation and per-item/batch audit.
28. **Forbidden stale current path:** CURRENT/NORMATIVE docs must not advertise Review 89/Gate 90 or v1.12 as the current implementation-contract package.

25. **Gate sequencing:** CURRENT source must distinguish pre-code Technical Specification Freeze from post-code Implementation Validation/Migration Freeze; forbidden current wording may not require the same implementation evidence both before and after Technical Freeze.
26. **Copy command authority:** `copy_interview_schedule` must exist in command registry/coverage/contract and client Copy draft must be explicitly non-mutating.


## Additional fail-closed checks for current Copy evidence
- **Copy schedule-engine propagation:** `copy_interview_schedule` must exist in Registry/contract/coverage **and** in `app_spec.schedule_conflicts.engine_used_by` plus the current Concurrency shared-engine declaration.
- **Critical Copy QA resolvability:** every `critical_control_registry.INTERVIEW-COPY-SAVE.browser_qa` stable ID must resolve to current Responsive Browser QA evidence.
- **Used-target Copy branch:** current QA must prove used target Round1 → next legal round.
- **Generated-label coherence:** generated All-in-One header/generator/validator labels must equal current Full Handover version.



---

<!-- SOURCE: 73_DOMAIN_GLOSSARY_AND_CANONICAL_PREDICATES.md -->

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



---

<!-- SOURCE: 75_RELEASE_EVIDENCE_MATRIX.md -->

# 75. Release Evidence Matrix — v1.8

**Status: CURRENT implementation/UAT evidence contract; it does not claim pre-code evidence exists.**

Viewports: 375, 768, 1280, 1440px.

Candidate journeys: OTP → new form → CV → Privacy → Submit; Candidate Edit while NEW; staged file Cancel; HR opens during edit → Save blocked; Phiếu của tôi; VI/EN; mobile.

HR journeys: NEW→READ; exact Submission Application create; durable duplicate/update/reactivate; multi-round schedule/conflicts; participant remove/restore/new report; Report/email; Application Inactive → filter Inactive → Reactivate/conflict; permissions/master lifecycle.

Critical click paths include row vs checkbox/status/action, Copy draft Cancel/Save, Application Reactivate conflict, Bound user edit no rebind, referenced Master guard, email double-click one logical enqueue, dirty language switch, Drawer focus return, bulk rollback.

Accessibility evidence: axe plus keyboard-only journey, focus visibility/return, screen-reader form/landmark sanity, 200% text zoom no loss, 400% reflow where SC 1.4.10 applies (wide semantic tables may intentionally retain two-dimensional scrolling). Missing visual baseline = `INCONCLUSIVE`, not PASS.

After migrations exist: audit FK/index coverage; `EXPLAIN (ANALYZE, BUFFERS)` at NFR-sized staging; grouped pagination/RLS plans; inspect `pg_stat_statements` after realistic journeys.



---

<!-- SOURCE: 76_DEPENDENCY_BASELINE_POLICY.md -->

# 76. Dependency Baseline Policy — v1.8

**Status: CURRENT policy; exact versions are recorded at implementation scaffold time, not guessed in long-lived spec.**

At implementation scaffold, create/review `package.json` and record exact reviewed/patched versions for Node, Next.js, React, `@supabase/supabase-js`, `@supabase/ssr`, package manager/lockfile, test runner, Playwright, upload/scanner packages, and provider SDKs. Pin versions + commit lockfile; record advisory/source review date; rerun Auth/RLS/upload/email regression on security-sensitive upgrades. Historical review version numbers must not become long-lived dependency pins.



---

<!-- SOURCE: 78_PRIVACY_NOTICE_PUBLICATION_RUNBOOK.md -->

# 78. Privacy Notice Publication / Current-Switch Runbook — CURRENT

## Scope
Phase 1 maintenance/deployment-only procedure. No Candidate/HR UI publishes Privacy Notice versions. Published content is immutable.

## Preconditions
- authorized Root/operations change with recorded approval;
- exact VI/EN content and SHA-256 hash reviewed;
- unique new `notice_version`;
- `effective_from` agreed;
- rollback operator identified.

## Publish future version
1. Insert new immutable version with `is_current=false`.
2. Verify stored content/hash and `effective_from`.
3. Do **not** unset the existing effective current notice early.
4. Record audit/change evidence.

## Current switch at/after effective time
Single DB transaction:
1. lock current notice row + target version;
2. assert target exists and `effective_from <= transaction_now`;
3. assert target content/hash metadata unchanged;
4. set old `is_current=false`;
5. set target `is_current=true`;
6. query exactly one current/effective notice; if not exactly one, raise/rollback;
7. commit + audit.

Because both pointer changes are in one transaction, a failure rolls back to the former current notice. A future-effective version is never made current before its effective time.

## Verification
- start a NEW and EDIT Form Session; both pin target notice;
- arbitrary client notice version rejected;
- prior acknowledgements still resolve immutable old version;
- `AC-PRIV-PUBLISH-01` passes.

## Rollback
If a post-switch operational issue requires rollback, switch current pointer back to the prior already-published effective version in one audited transaction. Never edit published content in place.



---

<!-- SOURCE: 81_RESPONSIVE_PROTOTYPE_INTEGRATION.md -->

# 81. Responsive Prototype Integration — v1.10 / Design System v1.8

**Status: CURRENT / NORMATIVE interaction/design amendment.**

**Responsive Prototype v1.10** is the executable responsive reference bundled with this handover.

The Full Handover v1.17 bundle includes `responsive_prototype/` v1.10 for one-package external + owner review. It is executable HTML/CSS/JS prototype evidence, not production React implementation.

## Frozen-for-current-UAT responsive corrections
- Candidate Inbox parent row derives Status/HR Note from deterministic latest Submission; Candidate Inactive is a separate lifecycle badge.
- Candidate-level bulk manual Submission status exposes only `NEW / READ`, resolves latest Submission and behaves ALL_OR_NOTHING.
- Historical child Submission status is read-only in Candidate-level bulk/manual UX.
- Normal persona navigation excludes `FUTURE_HIDDEN / NOT_RENDERED` routes.
- HR Report uses Current Interview Report Status; aggregate drawer has no generic Delete; Final Decision Source uses `decisionUpdatedAt`.
- Candidate EDIT exposes staged document `ADD / REPLACE / DELETE`; CV is authoritative-required on Save/Submit.
- Interview + HR Report status badges: **144px** benchmark; long English labels wrap inside this width, never stretch the full cell.
- Row StatusDropdown opens directly from the badge bounds and inherits badge width. Toolbar StatusDropdown opens from its Status button, with normal toolbar minimum width. No pointer-coordinate positioning.
- Dropdown dismisses by selection, outside pointer, Escape, or same-trigger toggle; Escape restores trigger focus.
- Interview time order: **time first, date after**; stay on one line while enough room exists and wrap only when genuinely constrained.
- Mobile `Thời gian phỏng vấn` label must have enough label-column width to avoid unnecessary wrapping.
- Mobile/Tablet/Desktop share business actions; bulk selection/status behavior uses the same underlying workflow and remains independently testable.

## Authority
Business/security/command semantics come from Full Handover v1.17. Visual/responsive tokens/components come from Design System v1.8. Owner-approved UAT corrections are recorded here and in Design System v1.8.



---

<!-- SOURCE: 97_INDEPENDENT_REVIEW_IMPLEMENTATION_ALIGNMENT_V1_17.md -->

# 97. Independent Review — Implementation Alignment v1.17

**Status:** CURRENT / NORMATIVE  
**Date:** 03/09/2026  
**Baseline:** Full Handover v1.17 + Design System v1.8 + Responsive Prototype v1.10

## Purpose
This alignment closes the independent review of Full Handover v1.16 (Freeze / Implementation Readiness). It does **not** reopen Business Logic Core v1.2 or change the four-gate implementation model. Technical Specification remains frozen.

## Closed findings

### 1. Copy command is propagated through the canonical schedule engine
`copy_interview_schedule` is now listed in `app_spec.yaml -> schedule_conflicts.engine_used_by`. `48_IDEMPOTENCY_CONCURRENCY_SPEC.md` explicitly includes **Save Copy** in the shared deterministic Candidate/Room/Interviewer lock + conflict engine. The client Copy draft remains non-mutating.

### 2. Critical Copy controls have resolvable browser-QA evidence
`INTERVIEW-COPY-SAVE.browser_qa` IDs `RP-COPY-01..04` now resolve to current Responsive v1.10 browser evidence. Coverage includes:
- structurally empty target Round1 → fill Round1;
- used target Round1 → create next legal round;
- Demo Topic remains blank;
- source schedule/logistics are preserved in the Copy draft/save simulation.

### 3. Generated All-in-One evidence is labeled v1.17
The generator and validator no longer advertise stale v1.15 generation labels. `15_ALL_IN_ONE_SPEC.md` is regenerated from CURRENT/NORMATIVE numbered modules and remains non-normative convenience evidence.

### 4. No-Handoff Continuity is implementation governance, not business authority
The independent review's No-Handoff Continuity recommendation is accepted for the **Implementation Executor/Planner workflow**. It is implemented in the revised Executor/Planner packs and initial `project_control/` bootstrap, not as a Candidate/HR business rule. Frozen EIU source continues to define WHAT the system must do; repository-backed `project_control/` records WHERE implementation currently is and its evidence.

## Freeze consequence
Technical Architecture v1.17 remains **TECHNICAL SPECIFICATION FROZEN**. Source-level Implementation Gate remains **READY TO IMPLEMENT**. Gate 3 still requires actual post-code migration/RLS/RPC/race/storage/performance/backup/deployment evidence. Production Ready remains **NO**.



---

<!-- SOURCE: 98_TECHNICAL_PRECODE_GATE_V1_17.md -->

# 98. Technical Pre-code / Implementation Authorization Gate — v1.17

**Status:** TECHNICAL SPECIFICATION FROZEN / READY TO IMPLEMENT  
**Date:** 03/09/2026

## Current authority
- Business Logic Core v1.2 = **FROZEN**
- Design System v1.8 = **CURRENT / REVIEWED**
- Technical Architecture v1.17 = **TECHNICAL SPECIFICATION FROZEN**
- Responsive Prototype v1.10 = **READY FOR OWNER VISUAL UAT / NOT FROZEN**
- Implementation Gate = **READY TO IMPLEMENT**
- Implementation Validation / Migration Freeze = **PENDING ACTUAL CODE EVIDENCE**
- Production Ready = **NO**

## Gate sequence
The v1.16 four-gate model remains unchanged:
1. Technical Specification Freeze — PASS.
2. Approved for Implementation — PASS at source level.
3. Implementation Validation / Migration Freeze — PENDING actual code evidence.
4. Production UAT / Production Ready — PENDING.

## Copy schedule-engine closure
`copy_interview_schedule` is the dedicated Save-Copy trusted mutation and is explicitly part of the shared schedule-conflict engine in both structured `app_spec.yaml` and `48_IDEMPOTENCY_CONCURRENCY_SPEC.md`. It must acquire/recheck deterministic Candidate/Room/Interviewer resources and Active current-Participant eligibility before committing an operational interval.

## Critical browser-evidence closure
Copy critical-control IDs `RP-COPY-01..04` resolve to current Responsive v1.10 browser evidence, including the used-target-Round1 → next legal round branch.

## Implementation-governance note
Before Slice 00 executes, the implementation repository should initialize the approved `project_control/` No-Handoff Continuity state from the revised Executor/Planner workflow. This is an implementation-governance requirement and does not redefine EIU business behavior.

## Executor authorization
This source baseline is **READY TO IMPLEMENT**. A Planner may issue an `EXECUTION_STATUS: AUTHORIZED` Slice00 prompt only after re-pinning this exact ZIP/hash and completing the user's independent prompt-review workflow. Production Ready remains NO.
