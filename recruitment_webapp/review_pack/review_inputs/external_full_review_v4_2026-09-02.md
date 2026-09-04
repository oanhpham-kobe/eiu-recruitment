# EIU Recruitment Web App — Full Review Report
## Baseline: Full Handover v1.5 + Design System v1.4

**Ngày review:** 02/09/2026  
**Phạm vi:** review lại từ đầu, chỉ sử dụng hai package hiện tại làm nguồn sự thật nghiệp vụ/thiết kế:

1. `App_Tuyen_Dung_EIU_Full_Handover_v1.5.zip`
2. `EIU_Recruitment_Design_System_v1.4.zip`

**SHA-256 baseline**

- Full Handover v1.5: `ed8847d5a8021f54984463f2730360acfa808b0c252e2bff38289dd32cb80407`
- Design System v1.4: `7d4cea37a9eca22b00059d07516fca01ef659287d5793daf2792a2ba2c3e9c56`

> Các version cũ không được dùng để suy ra trạng thái hiện tại. Các nguyên tắc review từ các repository engineering bên ngoài chỉ được dùng như **lăng kính kiểm tra**, không thay thế source of truth của hai package này.

---

# 1. Executive Summary

Bản **Full Handover v1.5 + Design System v1.4** đã tiến thêm một bước đáng kể về độ chặt chẽ. Nhiều vấn đề kiến trúc khó đã được mô tả thành contract thực sự, đặc biệt:

- Candidate Form Session giải quyết pre-submit upload mà không pre-create Submission;
- Candidate edit dùng staged file changes + Save/Cancel atomic semantics;
- Submission status có một authoritative recalculation function và parent lock;
- Interview mutation đã đưa Interview-row-first locking vào contract;
- Internal Google first-bind tách khỏi privileged identity rebind;
- Root Admin có break-glass recovery runbook;
- Application Reactivate được đưa vào Phase 1;
- master-data structural immutability đã được đưa xuống database trigger;
- document logical header/version model tốt hơn;
- batch semantics, validation contract, PII-search restriction, malware requirement đã được bổ sung;
- Design System đã sửa HR Report table width thành 1610px, có sticky context columns, Privacy acknowledgement, SubmissionSelector, AuthBindingBadge, MasterUsageGuard và quy tắc contrast rõ hơn.

Khi chạy validator đúng cách:

- **Full Handover + cross-design validation:** `107/107 PASS, 0 FAIL`
- **Design System validation:** `21/21 PASS, 0 FAIL`

Tuy nhiên, **107/107 + 21/21 chưa đồng nghĩa semantic consistency hoàn chỉnh**. Review cross-layer vẫn phát hiện một số mâu thuẫn mà validator hiện chưa có khả năng bắt.

### Đánh giá của reviewer

| Lớp | Trạng thái đề nghị |
|---|---|
| Business Logic Core | **Giữ FROZEN**, nhưng cần sửa một contradiction status/reactivation |
| Domain/Data Model | **Gần FROZEN** |
| Backend Command Contracts | **REVIEW REQUIRED** |
| Physical Schema Starter | **Gần FROZEN, còn một số invariant/traceability gap** |
| Concurrency Architecture | **Khá tốt, cần thêm vài edge-case contract/test** |
| Security/Identity Architecture | **Gần FROZEN, còn governance + rebind edge cases** |
| Storage/Documents | **Khá tốt, còn HR/internal document mutation coverage** |
| Email | **Architecture tốt nhưng acceptance/design wording còn tự mâu thuẫn** |
| Privacy/Retention | **Khá tốt, còn notice-version authority + archive/purge procedure** |
| Design System v1.4 | **CURRENT, chưa nên Final Freeze** |
| Technical Architecture | **NOT YET FROZEN** |
| Production Ready | **NO**, phù hợp với chính package hiện tại |

---

# 2. Verification Evidence

## 2.1 Package validation

Validator của Handover cần được chạy với Design System v1.4 đã giải nén:

```bash
python review_pack/tools/validate_package.py \
  --design-dir /path/to/EIU_Recruitment_Design_System_v1.4
```

Kết quả thực tế:

```text
PACKAGE VALIDATION — Full Handover v1.5 / Design System v1.4 — 2026-09-02
TOTAL=107 PASS=107 FAIL=0
```

Design validator:

```text
DESIGN VALIDATION — EIU Recruitment Design System v1.4 — 2026-09-02
TOTAL=21 PASS=21 FAIL=0
```

### Lưu ý packaging

Nếu chạy `validate_package.py` mà không truyền `--design-dir` khi hai package nằm trong hai ZIP độc lập, validator có thể không auto-discover được Design System. Đây không phải lỗi nghiệp vụ; `START_HERE.txt` hiện đã mô tả đúng cách chạy cross-package.

---

# 3. Findings Summary

## P0 — nên đóng trước Technical Architecture Freeze

| ID | Finding | Loại |
|---|---|---|
| P0-01 | Candidate Reactivation và authoritative Submission recalculation đang cho hai kết quả khác nhau khi không có active Application | Business ↔ backend contradiction |
| P0-02 | UI có các mutation document/email-history nhưng Backend Command Coverage chưa khép kín | Command/security/data integrity |
| P0-03 | Email acceptance/design vẫn hứa “retry không duplicate send”, trái với chính at-least-once semantics | Spec contradiction |
| P0-04 | `users.directory_manage` chưa khóa rõ target nào được Active/Inactive; có nguy cơ HR thường vô hiệu hóa HR khác | Authorization governance |

## P1 — nên đóng trước implementation freeze / UAT

| ID | Finding |
|---|---|
| P1-01 | Candidate recreated Auth identity rebind chưa deterministic với `auth_user_id NOT NULL` |
| P1-02 | File-only Candidate Save cần bắt buộc bump Submission version |
| P1-03 | Privacy Notice version do client truyền nhưng chưa có authoritative published-version validation |
| P1-04 | Candidate Submission notification không có `submission_id` trong email_outbox/history |
| P1-05 | `reactivate_application()` thiếu duplicate-identity precheck và multi-child operational semantics |
| P1-06 | Room chưa nằm trong master structural-history guard |
| P1-07 | Rate limiting được đánh dấu RESOLVED nhưng chưa có endpoint/threshold/key strategy cụ thể |
| P1-08 | Export/archive/purge PII chưa có runbook/command/verification contract đủ dùng |
| P1-09 | Web security baseline còn quá tổng quát |
| P1-10 | `14_SCOPE_AND_OPEN_ITEMS.md` vẫn ghi DS v1.3 / Technical v1.4 |
| P1-11 | Design System còn Drawer rule `760–860px, max 55vw`, trái với TOKENS v1.4 |
| P1-12 | HR Submission Inbox Design component matrix thiếu FileList/FilePreview dù business UI có document management |
| P1-13 | Acceptance ID `AC-UP-03` bị trùng |
| P1-14 | Hard-delete unused Candidate/Submission dùng từ “authorized HR/Root” thay vì exact permission |
| P1-15 | `reports.manage_status` nói quản lý HR owner nhưng command chưa khóa rõ ownership mutation |
| P1-16 | `app_spec.yaml` conflict engine usage chưa phản ánh đầy đủ Application Reactivate |
| P1-17 | Hard-delete trong lúc Candidate Form Session/upload temp đang mở cần cleanup ordering rõ |
| P1-18 | Command Coverage Matrix tham chiếu một số command chưa có dedicated contract trong file 37 |

## P2 — hardening / agent-readability / maintainability

- frozen scope còn câu “bulk khác có thể bổ sung khi triển khai”;
- `15_ALL_IN_ONE_SPEC.md` nói Generated nhưng package chưa có generator script để chứng minh regeneration equality;
- Design `COMPONENTS.md` lặp numbering 18–21;
- `SIDEBAR_NAVIGATION.md` vẫn ghi title v1.3;
- một số current docs vẫn mang header version cũ dù đã nhận amendment mới;
- validator nên kiểm tra contradiction semantics, không chỉ tokens/counts;
- Candidate Form Session TTL/recovery UX cần explicit hơn;
- Danger semantic color chỉ vượt AA với margin tương đối nhỏ, nên regression-test bằng số.

---

# 4. P0-01 — Candidate Reactivation và Submission Recalculation đang mâu thuẫn

## Nguồn liên quan

### `03_CANDIDATE_FORM_AND_PORTAL.md`

Khi HR Active Candidate lại:

- có HIRED → `DONE`;
- tất cả REJECTED → `CLOSED`;
- có Application đang xử lý → `PROCESSED`;
- **không còn active Application → `READ`**.

### `37_BACKEND_COMMAND_CONTRACTS.md`

`recalculate_submission_status(submission_id)` lại quy định:

> no active Application → **preserve existing manual `NEW/READ`**; nếu từ derived state sau khi Application cuối bị remove thì về `READ`.

`set_candidate_active()` nói reactivation gọi recalculation theo Applications thực tế.

## Scenario gây contradiction

1. Candidate có Submission `NEW`.
2. Submission chưa có Application.
3. HR Inactive Candidate.
4. HR Active Candidate lại.

Theo Candidate Portal spec:

```text
NEW → READ
```

Theo authoritative recalculation:

```text
NEW → NEW
```

Cả hai không thể đồng thời là source of truth.

## Đề nghị

Chọn **một** trong hai rule.

### Phương án A — khuyến nghị nếu muốn Candidate không tự sửa ngay sau Reactivate

`set_candidate_active(true)` dùng một reactivation mode:

```text
NO_ACTIVE_APPLICATION => READ
```

Trong khi generic `recalculate_submission_status()` vẫn preserve NEW/READ cho các mutation khác.

Ví dụ:

```text
recalculate_submission_status(
  submission_id,
  reason = CANDIDATE_REACTIVATED
)
```

Hoặc không parameterize calculator mà command `set_candidate_active()` explicit chuyển NEW→READ sau khi kiểm tra không có active Application.

### Phương án B

Sửa `03`/`07`: Candidate Reactivate giữ manual state hiện tại nếu không có active Application.

## Acceptance nên bổ sung

```text
AC-CAND-REACT-01
Candidate inactive with NEW/no Application → Reactivate → expected state [owner-selected rule].

AC-CAND-REACT-02
Candidate inactive with READ/no Application → Reactivate → READ.

AC-CAND-REACT-03
Candidate inactive with active processing Application → Reactivate → PROCESSED.

AC-CAND-REACT-04
Candidate inactive with HIRED effective outcome → Reactivate → DONE.
```

**Mức:** P0 vì đây là contradiction trực tiếp giữa business flow và authoritative backend function.

---

# 5. P0-02 — Production mutations chưa map đầy đủ vào trusted commands

`37_BACKEND_COMMAND_CONTRACTS.md` mở đầu bằng nguyên tắc rất đúng:

> Every UI mutation maps to one explicit trusted backend command.

`55_COMMAND_COVERAGE_MATRIX.md` cũng nói:

> Rows without a command are not allowed to ship.

Nhưng current UI/business vẫn có mutation chưa được command contract hóa đầy đủ.

## 5.1 HR quản lý Submission Documents

`04_HR_APPLICATION_INBOX.md` cho HR:

- Preview;
- Download;
- **Upload thêm**;
- **Replace/Xóa theo quyền**.

Trong file 37 hiện có:

- Candidate staged document commands;
- Interview upload reserve/finalize;
- cleanup worker.

Nhưng chưa có dedicated HR Submission Document mutation command.

Điểm này không chỉ là coverage cosmetic. Candidate Submission có invariant quan trọng:

```text
effective current documents <= 5
AND at least one current CV exists
```

Candidate Save đã enforce invariant này bằng staged plan validator. Nếu HR có thể Delete/Replace trực tiếp theo một implementation riêng, HR có thể vô tình xóa current CV duy nhất hoặc vượt file count.

## Đề nghị

Thêm explicit commands, ví dụ:

```text
reserve_hr_submission_upload(submission_id)
finalize_hr_submission_upload(...)
replace_submission_document_by_hr(...)
delete_submission_document_by_hr(...)
```

Hoặc một deep command interface:

```text
mutate_submission_documents_by_hr(
  submission_id,
  expected_version,
  mutation_plan[]
)
```

Bất kể interface nào, server phải enforce:

- `submissions.edit + submissions.view`;
- Submission ownership/exists;
- document type scope;
- malware CLEAN;
- 5 MB;
- max current files;
- current CV invariant;
- logical-document version invariant;
- bump aggregate Submission version;
- audit;
- idempotency.

---

## 5.2 Interview Document Delete

Delete/Inactive matrix nói:

```text
Interview Document | Có thể hard-delete trực tiếp
```

Permission:

```text
interviews.documents = Manage interview documents
```

Nhưng file 37 chỉ định nghĩa reserve/finalize upload, chưa có delete command.

Cần command:

```text
delete_interview_document(...)
```

với exact authorization, historical/audit behavior và storage cleanup.

---

## 5.3 Email History Delete

`11_EMAIL_DOCUMENTS_AND_ACTIVITY_LOG.md` giữ frozen behavior:

- checkbox;
- Delete wrong/test records;
- immutable audit giữ lại sự kiện delete.

Nhưng Command Coverage không có explicit:

```text
delete_email_history(...)
```

Cần định nghĩa:

- permission chính xác;
- record eligible để delete;
- có được delete `SENT` production email hay chỉ wrong/test?
- retention/audit;
- transaction;
- batch semantics;
- storage/attachment không còn liên quan vì Phase 1 không attachment.

---

## 5.4 Command Coverage Matrix tham chiếu command chưa có dedicated contract

Ví dụ matrix có:

- `change_report_status`
- `set_report_visibility`
- `bulk_mark_submission_new`
- `bulk_create_or_update_applications`
- `bulk_enqueue_email`
- `delete_or_inactivate_master_item`
- `set_candidate_active`

Một số concept được mô tả bằng prose/grouped contract, nhưng nguyên tắc “explicit trusted command” nên được thực hiện nhất quán.

### Đề nghị validator mới

Tạo machine-readable:

```text
command_registry.yaml
```

Mỗi command:

```yaml
command: delete_email_history
actor:
permission:
preconditions:
locks:
transaction:
audit:
idempotency:
acceptance_tests:
```

Validator phải kiểm tra:

```text
UI Mutation
→ Permission
→ Command Registry
→ Contract section
→ Acceptance Test
```

Không chỉ search token.

**Mức:** P0 vì source hiện tự tuyên bố production mutation không có command thì không được ship.

---

# 6. P0-03 — Email delivery semantics đang tự mâu thuẫn

Kiến trúc email hiện tại **đúng hướng**:

`43_EMAIL_DELIVERY_SPEC.md`:

> Do not claim exactly-once delivery.  
> Target = at-least-once delivery + idempotent enqueue + best-effort/provider-assisted deduplication.

`37_BACKEND_COMMAND_CONTRACTS.md` cũng ghi:

> Acceptance criteria must not promise impossible exactly-once delivery.

Nhưng:

### `13_ACCEPTANCE_CRITERIA_AND_TEST_CASES.md`

```text
AC-55 Email outbox —
business transaction commits before external email delivery;
retries do not duplicate sends.
```

### Design `PATTERNS.md`

```text
retry must not create duplicate messages.
```

Trong cùng Acceptance file, mục v1.4/v1.5 lại thừa nhận:

> provider accepted + worker crash → duplicate delivery có thể xảy ra.

## Đây là contradiction

Có hai loại retry cần tách:

### 1. Browser/API retry

Phải guarantee:

```text
same logical request
→ no duplicate outbox enqueue
```

bằng idempotency.

### 2. Worker/provider delivery retry

Không thể guarantee tuyệt đối:

```text
no duplicate recipient delivery
```

nếu provider đã accept nhưng worker crash trước khi persist SENT.

## Sửa wording

### AC-55 mới

```text
AC-55 Email outbox —
business transaction commits before external delivery.
Browser/double-click/request retry with the same idempotency scope/key
must not create duplicate logical outbox rows.
Provider delivery remains at-least-once; duplicate recipient delivery
after provider-accept/worker-crash is possible and must be observable/audited.
```

### Design PATTERNS

Đổi:

```text
retry must not create duplicate messages
```

thành:

```text
client retry must not create duplicate logical enqueue;
delivery retry follows at-least-once semantics and may produce provider-level duplicates.
```

`11_EMAIL...` dòng “This prevents duplicate sends on browser retry/double click” cũng nên đổi thành “prevents duplicate logical enqueue”.

**Mức:** P0 vì acceptance criterion hiện đòi một guarantee mà architecture chính thức nói không thể guarantee.

---

# 7. P0-04 — Internal User Active/Inactive governance chưa đủ chặt

Permission catalog:

```text
users.directory_manage
```

cho phép quản lý directory/business profile và mô tả UI có Active/Inactive “user thường theo rule”.

Full HR mặc định nhận granular set khá rộng.

Root-only:

- HR role;
- permissions;
- bound identity rebind.

Nhưng current source chưa khóa deterministic:

> HR có `users.directory_manage` có được Inactive **một HR khác** không?

Nếu câu trả lời là Có, một HR không có quyền revoke role/permission vẫn có thể:

```text
Inactive another HR
→ effectively remove access
```

Tức là bypass governance boundary bằng lifecycle thay vì permission change.

## Đề nghị

Tách command:

```text
set_internal_user_active(target_user_id, active, expected_version)
```

và freeze target rules:

### Khuyến nghị

- ordinary non-HR internal user: `users.directory_manage`;
- target có HR role: **Root-only**;
- Root: protected;
- self-inactive: quyết định explicit (khuyến nghị không cho HR tự inactive qua UI);
- inactive phải revoke/expire session theo security policy nếu cần;
- audit bắt buộc.

Thêm acceptance:

```text
AC-USR-ACT-01 ordinary user lifecycle allowed.
AC-USR-ACT-02 non-root HR cannot deactivate HR-role target.
AC-USR-ACT-03 Root cannot be deactivated.
AC-USR-ACT-04 self-deactivation behavior is deterministic.
```

**Mức:** P0/security-governance trước Technical Freeze.

---

# 8. P1-01 — Candidate recreated Auth identity rebind còn ambiguity

Schema:

```sql
candidates.auth_user_id uuid not null unique
```

Auth model nói:

> safely bind recreated Auth identity to existing Candidate when appropriate.

Backend contract:

> fallback by verified email → safe bind if unbound → never duplicate Candidate solely because Supabase Auth ID recreated.

Vấn đề: một Candidate cũ có `auth_user_id` cũ **không phải “unbound”** vì column NOT NULL.

## Scenario

1. Candidate OTP account/Auth row cũ mất/recreated.
2. Email vẫn verified giống cũ.
3. New Auth ID khác old Auth ID.
4. Lookup current ID không thấy.
5. Fallback by verified email tìm Candidate cũ.
6. `auth_user_id` đang chứa old ID.

Current contract chưa nói chính xác khi nào được replace old→new.

## Đề nghị

Freeze một Candidate-specific safe-rebind rule:

```text
verified email controls identity
AND exact normalized email matches
AND no other Candidate uses new auth ID
AND no conflicting active identity state
→ lock Candidate
→ replace auth_user_id old→new
→ security audit old/new
→ invalidate old session/identity where possible
```

Khác Internal User: Internal bound rebind là privileged Root-only; Candidate có thể cần controlled self-rebind vì email OTP là identity proof.

Cần concurrency test cho hai simultaneous OTP/rebind attempts.

---

# 9. P1-02 — File-only Candidate Save phải bump Submission version

Candidate Edit:

- Form Session stores base Submission version.
- Save checks expected version.
- file changes được stage riêng.

Nhưng contract chưa nói đủ rõ:

> Nếu Candidate chỉ Replace một file, không thay text field, Save có bắt buộc increment `Submission.version_no` không?

Nếu không:

1. Session A và B cùng mở ở version 5.
2. A chỉ replace CV → persisted documents đổi nhưng Submission vẫn version 5.
3. B Save stale form session → vẫn thấy version 5 và có thể commit dựa trên document state cũ.

## Rule nên freeze

Mọi successful Candidate Save làm thay đổi **text hoặc document aggregate**:

```text
touch submissions.updated_at
increment submissions.version_no exactly once
```

HR Submission document mutation cũng phải bump cùng aggregate version.

Acceptance:

```text
AC-CONC-DOC-01
Two edit sessions at same base version.
Session A performs file-only Save.
Session B Save must fail STALE_VERSION.
```

---

# 10. P1-03 — Privacy Notice version chưa có authoritative server source

Submit command nhận:

```text
privacy_notice_version
```

từ client.

Privacy spec yêu cầu record exact notice version. Design cũng hiển thị notice/version.

Nhưng chưa có authoritative server rule xác minh:

- version đó có tồn tại?
- có phải current published version?
- có phải chính version được server trình bày khi Form Session mở?
- có bị client sửa thành arbitrary string không?

## Đề nghị

Có thể dùng:

```text
privacy_notice_versions
```

hoặc server configuration:

```text
version
content_hash
locale
published_at
effective_from
is_current
```

Khi start form:

```text
form_session.presented_privacy_notice_version
```

Submit chỉ accept acknowledgement cho version do server đã pin trong session.

## Cleanup contradiction nhỏ trong file 42

File 42 vẫn có dòng:

```text
Suggested acknowledgement fields:
candidate_id, submission_id, notice_version...
```

nhưng phía sau và current SQL chủ ý nói Candidate derive qua Submission, không redundant `candidate_id`.

Xóa dòng legacy `candidate_id`.

---

# 11. P1-04 — Email Outbox/History thiếu `submission_id`

Candidate Submit/Update có HR notification.

Nhưng SQL hiện:

```text
email_outbox:
  interview_id
  application_id
  ...
  created_by_candidate_id

email_history:
  interview_id
  application_id
```

không có `submission_id`.

`created_by_candidate_id` là actor, không phải subject business record.

Nếu Candidate có nhiều Submission, support/audit không thể relationally truy ra chính xác notification nào thuộc Submission nào mà không dựa vào body/metadata gián tiếp.

## Đề nghị

Thêm:

```sql
submission_id uuid references public.submissions(...)
```

nullable.

Hoặc generic immutable subject:

```text
subject_entity_type
subject_entity_id
```

nhưng với PostgreSQL FK integrity thì explicit nullable FK thường đơn giản hơn.

Cần quyết định delete behavior khi unused Submission được hard-delete:

- cascade/set null;
- hoặc hard-delete chỉ khi outbox/history phù hợp cleanup rule.

Audit immutable vẫn giữ trace.

---

# 12. P1-05 — Application Reactivate còn hai edge case

## 12.1 Duplicate active identity

DB có partial unique active Application identity.

Một inactive Application cũ có thể tồn tại song song với một active Application mới cùng:

```text
submission + unit + team + position
```

Nếu user Reactivate old row, DB unique constraint có thể fail.

Backend nên pre-check và trả controlled:

```text
DUPLICATE_APPLICATION
```

thay vì raw DB violation.

Transaction cần lock identity scope hoặc parent Submission rồi kiểm tra.

---

## 12.2 Reactivate parent có thể làm nhiều child Interview effective-active

Effective active:

```text
Application.is_active AND Interview.is_active
```

Nếu Application inactive nhưng nhiều child Interview rows vẫn `is_active=true`, Reactivate parent có thể làm **nhiều Interview** operational cùng lúc.

Contract hiện dùng wording gần singular:

> if reactivation would make an Interview operational, use shared conflict framework.

Cần freeze:

- chỉ Current Round được operational?
- hay tất cả active child Interviews trở lại effective-active?
- nếu nhiều child có future schedule, phải lock/revalidate tất cả resource sets theo deterministic order.

Khuyến nghị invariant mạnh hơn:

> tại một thời điểm chỉ current/latest lifecycle-relevant active round được operational; historical rounds không block resources.

Nếu không chọn invariant này, `reactivate_application()` phải xử lý all newly-effective child sessions.

---

# 13. P1-06 — Room chưa được bảo vệ khỏi structural history mutation

`64_MASTER_DATA_HISTORY_POLICY.md` nói master đã referenced không được đổi structural business meaning.

SQL `private.protect_master_structural_semantics()` bảo vệ:

- Position;
- Department Team;
- Unit;
- Position Group;
- Interview Format;
- Document Type;
- Recruitment Source;
- Qualification;
- Cancellation/Rejection reasons.

Nhưng **Rooms không có branch** trong function này. Room chỉ có `rooms_touch_version`.

Vì vậy một Room đã được Interview tham chiếu vẫn có thể đổi:

- code;
- display_name;
- building;

và lịch sử Interview khi join master sẽ đổi nghĩa.

## Đề nghị

Thêm Room semantic guard.

Ví dụ:

```text
used Room:
  code/building/identity-bearing structural fields immutable
  typo-only display correction allowed only if owner accepts historical label correction
```

Nếu đổi phòng thực tế:

```text
create new Room
inactive old Room
```

---

# 14. P1-07 — Rate limiting bị đánh dấu “resolved” nhưng còn implementation-underdetermined

`technical_review_matrix.csv`:

```text
TR-26 Rate limiting/abuse prevention missing
→ ACCEPTED_TECH
→ Added auth/submit/upload/email/PDF rate-limit expectations
```

Nhưng NFR thực tế chủ yếu mới có:

```text
Candidate rate limits
```

Auth file nói OTP request/login/submission endpoints require limits.

Chưa có:

- endpoint matrix;
- burst/window;
- keying;
- IP vs identity;
- trusted proxy;
- `Retry-After`;
- distributed storage/provider-native strategy;
- abuse test.

## Đề nghị

Thêm `RATE_LIMIT_POLICY.md` hoặc section machine-readable:

| Endpoint/action | Key | Burst | Window | Response |
|---|---|---:|---:|---|
| OTP request | normalized email + IP | TBD owner/IT default | ... | 429 + Retry-After |
| OTP verify | session/email + IP | ... | ... | ... |
| Candidate submit | Candidate ID | ... | ... | ... |
| upload reserve/finalize | Candidate/User + IP | ... | ... | ... |
| internal search | User | ... | ... | ... |
| manual email | User + entity | ... | ... | ... |
| PDF generate | User | ... | ... | ... |

Nếu chưa muốn khóa con số cuối, ít nhất freeze strategy + initial defaults + configuration ownership.

Do đó TR-26 hiện nên là:

```text
PARTIALLY_RESOLVED
```

chứ chưa `ACCEPTED_TECH` hoàn toàn.

---

# 15. P1-08 — Data export/archive/purge chưa có runbook đủ production

Privacy/operations đã nói cần:

- export;
- archive;
- explicit purge;
- audit;
- capacity-driven procedure.

Nhưng chưa có operational contract chi tiết cho PII archive.

## Cần bổ sung

Ví dụ:

```text
66_DATA_EXPORT_ARCHIVE_PURGE_RUNBOOK.md
```

bao gồm:

- authorized role/operator;
- approval;
- export scope;
- format;
- encryption at rest/in transit;
- destination;
- access control;
- manifest;
- checksum;
- source row/document counts;
- Storage object reconciliation;
- chain of custody;
- audit event;
- restore verification;
- purge verification;
- failure/rollback;
- retention of audit after business data purge.

Đây đặc biệt quan trọng nếu capacity policy cho phép “export/archive local”.

---

# 16. P1-09 — Web Security Baseline còn quá tổng quát

NFR có:

```text
HTTPS
CSP/security headers
RLS
server-only secrets
```

nhưng current source chưa freeze một baseline đủ testable cho một hệ thống chứa PII.

Không tìm thấy contract explicit cho:

- CSP exact policy baseline;
- `frame-ancestors`;
- `base-uri`;
- `object-src`;
- `Referrer-Policy`;
- `Permissions-Policy`;
- HSTS;
- CORS allowlist;
- Cookie Secure/HttpOnly/SameSite;
- CSRF/origin strategy cho cookie-auth mutations;
- sensitive response/page `Cache-Control`;
- error/log redaction.

## Đề nghị

Thêm:

```text
WEB_SECURITY_BASELINE.md
```

Không cần hard-code framework implementation, nhưng phải xác định target security behavior và test evidence.

---

# 17. P1-10 — Current status document vẫn ghi version cũ

`14_SCOPE_AND_OPEN_ITEMS.md` title là v1.5 nhưng phần đầu ghi:

```text
Design System: v1.3 CURRENT
Technical Architecture: v1.4 REVIEWED...
```

Trong khi package hiện tại chính thức:

```text
Design System v1.4
Technical Architecture v1.5
```

Đây là source-of-truth drift.

## Sửa

```text
Design System v1.4 CURRENT
Technical Architecture v1.5 REVIEWED / READY FOR EXTERNAL RE-REVIEW / NOT FROZEN
```

Ngoài ra nên rà các header cũ kiểu `v1.3`, `v1.4` trong các current modular docs và phân loại:

- historical changelog → giữ;
- current source file có amendment mới → rename current version hoặc ghi “base + v1.5 amendments”.

---

# 18. P1-11 — Design System vẫn có Drawer contradiction

`TOKENS.md` v1.4 đã sửa đúng:

```text
drawer desktop:
preferred 820px
actual width = min(820px, available-content-width)
Do not combine a 760px minimum with a smaller 55vw cap.
```

Nhưng `COMPONENTS.md` vẫn nói:

```text
Desktop width 760–860px, max 55vw.
```

Ở viewport 1280:

```text
55vw = 704px
```

tức nhỏ hơn minimum 760px.

## Đáng chú ý

`DESIGN_VALIDATION.txt` lại báo:

```text
PASS | Drawer contradiction removed
```

=> validator hiện có **false positive semantic**; nhiều khả năng chỉ scan một file/phrase cụ thể.

## Sửa

`COMPONENTS.md` dùng đúng formula từ TOKENS, ví dụ:

```text
Desktop preferred 820px;
actual width = min(820px, available-content-width);
responsive sheet rule below breakpoint.
```

Validator search toàn Design package cho legacy `55vw`/`760–860` rule.

---

# 19. P1-12 — HR Submission Inbox component matrix thiếu file components

Business page `04_HR_APPLICATION_INBOX.md` cho HR:

- Preview;
- Download;
- Upload;
- Replace/Delete.

Nhưng Design `page_component_matrix.csv` cho:

```text
Quản lý phiếu ứng tuyển
```

không có:

```text
FileList
FilePreview
```

Trong khi Interview/Report pages đã khai các component tương tự.

## Sửa

Bổ sung:

```text
FileList
FilePreview
```

và nếu Design System muốn rõ mutation state:

```text
UploadProgress/AsyncStatus
ConfirmationDialog
```

Component/page override phải mô tả:

- permission-controlled actions;
- current version;
- malware scanning state;
- replace/delete confirmation;
- required CV guard error.

---

# 20. P1-13 — Duplicate Acceptance Test ID

`13_ACCEPTANCE_CRITERIA_AND_TEST_CASES.md` có:

```text
AC-UP-03
```

hai lần:

1. staged upload chưa VALIDATED+CLEAN không được commit;
2. HR mở Submission NEW→READ trong lúc Candidate upload thì Save phải block.

Đây là lỗi traceability.

## Sửa

Đổi test thứ hai thành:

```text
AC-UP-06
```

hoặc ID tiếp theo theo registry.

Validator nên enforce:

```text
all AC-* IDs unique
```

---

# 21. P1-14 — Hard-delete permission đang dùng từ mơ hồ

Command Coverage:

```text
Hard-delete unused Submission | authorized HR/Root
Hard-delete unused Candidate | authorized HR/Root
```

Trong hệ granular permission, “authorized HR” không đủ deterministic.

## Cần freeze

Ví dụ:

```text
Submission hard delete:
submissions.delete + submissions.view
```

Nếu không muốn thêm permission mới, map rõ vào permission hiện có.

Candidate hard delete:

```text
candidates.active_manage
```

có thể không nên tự động bao gồm irreversible delete; cân nhắc permission riêng:

```text
candidates.delete_unused
submissions.delete_unused
```

Root implicit.

Hard-delete là security-sensitive nên exact permission tốt hơn tái sử dụng lifecycle permission mơ hồ.

---

# 22. P1-15 — HR owner mutation chưa khép kín với Report permission

Permission catalog nói:

```text
reports.manage_status
= Đổi Report Status / HR Note / HR owner
```

HR owner thực tế nằm ở Application.

`update_hr_report_management()` hiện nói:

- `hr_report_note`;
- report status/management fields.

Command Coverage row mô tả chủ yếu status/note.

## Cần chọn architecture

### Option A — reports.manage_status được phép đổi HR owner

Command phải explicit:

```text
update_hr_report_management(
  application_id,
  expected_application_version,
  hr_owner_id?,
  hr_report_note?,
  report_status?
)
```

và:

- lock Application;
- validate owner Active HR/root;
- audit old/new owner;
- concurrency/version;
- permission.

### Option B — cleaner

HR owner thuộc Application management:

```text
applications.manage
```

Report management chỉ status/note.

Tôi nghiêng Option B vì ownership là Application concern, không phải Report concern.

---

# 23. P1-16 — app_spec conflict engine chưa phản ánh đầy đủ Application Reactivate

`app_spec.yaml` đã khai:

```text
reactivate_application: true
```

Backend contract nói nếu reactivation làm Interview operational thì phải dùng shared Interview conflict framework.

Nhưng `schedule_conflicts.engine_used_by` cần được rà để đảm bảo Application Reactivate được liệt kê rõ, không chỉ interview-level operations.

Đây là cross-artifact consistency issue: coding agent đọc YAML có thể bỏ validation mà Markdown có yêu cầu.

## Sửa

Thêm explicit:

```yaml
engine_used_by:
  - save_interview_schedule
  - add_interview_participant
  - readd_interview_participant
  - reactivate_interview
  - activate_from_cancelled
  - reactivate_application_when_child_becomes_operational
```

---

# 24. P1-17 — Hard-delete vs open Form Session/temp objects cần ordering rõ

Form Session / upload reservation có FK cascade theo target Submission trong một số paths.

Scenario:

1. Candidate đang có OPEN edit form session và temp objects.
2. HR hard-delete một unused Submission/Candidate theo delete rule.
3. DB cascade xóa session/reservation metadata.
4. Nếu temp Storage paths chưa được durable-enqueue cleanup trước cascade, cleanup worker có thể mất reference để xóa object.

`delete_unused_*` nói “schedule Storage cleanup”, nhưng ordering cần freeze.

## Đề nghị

Trước DB delete:

```text
lock target
find open sessions/reservations
capture temp object paths
enqueue durable cleanup records
cancel sessions
then delete business rows
```

Hoặc:

```text
block hard-delete while OPEN Form Session exists
→ force-cancel session first
```

Thêm acceptance test.

---

# 25. P1-18 — Command Coverage Matrix và Contract file chưa cùng mức explicit

Command Coverage Matrix có một số command literal không có dedicated heading/contract tương ứng trong file 37, như:

- `change_report_status`;
- `set_report_visibility`;
- bulk commands;
- master delete/inactive;
- `set_candidate_active`.

Có thể implementation team suy ra từ sections chung, nhưng điều này trái mục tiêu của v1.5 là “không để coding agent tự suy diễn”.

## Đề nghị

Mỗi command trong Coverage Matrix phải có một entry trong Command Registry/Contract.

Validator:

```text
set(coverage.command_names)
==
set(command_registry.command_names)
```

với exceptions explicit cho:

- client draft/no mutation;
- system internal helper.

---

# 26. Design Review — những điểm đã xác minh tốt

## 26.1 Table widths

Current frozen widths khớp số học:

### Application Inbox

```text
48 + 220 + 250 + 130 + 100 + 150 + 150 + 420 + 92
= 1560px
```

### Interview

```text
48 + 340 + 250 + 220 + 170 + 360 + 92
= 1480px
```

### HR Report

```text
48 + 240 + 300 + 240 + 200 + 190 + 300 + 92
= 1610px
```

Đây là cải thiện tốt. Validator đã kiểm tra arithmetic.

---

## 26.2 Current semantic color contrast

Tính trên các token hiện tại:

| Token | Foreground / Background | Contrast xấp xỉ | AA normal text |
|---|---|---:|---|
| Success | `#3B6A2A` / `#EAF3E6` | **5.63:1** | PASS |
| Warning | `#8A4F00` / `#FFF0DE` | **5.87:1** | PASS |
| Danger | `#B44425` / `#F8E5E0` | **4.55:1** | PASS, margin nhỏ |
| Info | `#144069` / `#E5EDF5` | **9.03:1** | PASS |
| Neutral | `#68686B` / `#EEF0F1` | **4.86:1** | PASS |
| Purple | `#4B479D` / `#ECEBFA` | **6.63:1** | PASS |

Brand gold:

```text
#A78656 on white ≈ 3.39:1
```

không phù hợp normal body text; Design v1.4 đã **đúng khi cấm dùng gold làm normal 14–16px text trên nền sáng**.

Sidebar gold:

```text
#E6C88F on #0E416F ≈ 6.50:1
```

tốt.

### Khuyến nghị

Danger đang chỉ trên ngưỡng 4.5 một khoảng nhỏ. Không nhất thiết đổi màu, nhưng CI/design validator nên **tính ratio bằng numeric formula**, không chỉ search token values.

---

# 27. P2 — Design/component documentation cleanup

## 27.1 COMPONENTS numbering bị lặp

Sau:

```text
18. LanguageSwitcher
19. Pagination
20. AsyncStatus
21. DemoPersonaSwitcher
```

file lại dùng:

```text
18. SubmissionSelector
19. PrivacyNoticeAcknowledgement
20. AuthBindingBadge
21. MasterUsageGuard
```

Không ảnh hưởng runtime nhưng gây reference ambiguity.

Đổi thành 22–25.

---

## 27.2 SIDEBAR title còn v1.3

Package là Design System v1.4 nhưng:

```text
# SIDEBAR & NAVIGATION — v1.3
```

Nên đổi current source header sang v1.4.

---

# 28. P2 — Frozen scope còn wording mời scope creep

`04_HR_APPLICATION_INBOX.md`:

```text
Các thao tác bulk khác có thể bổ sung khi triển khai.
```

Trong một handover nhằm giảm agent inference, câu này không phù hợp.

Đổi thành:

```text
Other bulk actions are OUT OF SCOPE for Phase 1 unless approved through Change Request.
```

Không để developer/coding agent “tiện tay” thêm bulk chức năng.

---

# 29. P2 — ALL_IN_ONE_SPEC là generated artifact nhưng chưa có generator

`15_ALL_IN_ONE_SPEC.md` ghi:

> Generated from modular current source files.

Nhưng `tools/` hiện chỉ có:

```text
validate_package.py
```

không có generator script.

Validator hiện check presence của các token/current fragments, nhưng chưa chứng minh:

```text
ALL_IN_ONE_SPEC
==
regenerate(modular_sources)
```

## Đề nghị

Thêm:

```text
tools/generate_all_in_one.py
```

CI:

```text
generate temp
compare hash/bytes to committed 15_ALL_IN_ONE_SPEC.md
mismatch => FAIL
```

Và header:

```text
DO NOT EDIT MANUALLY
```

Điều này rất quan trọng vì file All-in-One dài và duplication dễ drift.

---

# 30. Validator — nên nâng từ syntactic consistency sang semantic consistency

Validator current đã có giá trị, nhưng các finding trong report cho thấy `PASS` hiện chủ yếu chứng minh:

- file/section/token tồn tại;
- counts match;
- widths arithmetic;
- selected current strings có mặt.

Nó chưa bắt các contradiction kiểu:

```text
A says exactly-once-like guarantee
B says at-least-once
```

hoặc:

```text
Design TOKENS bans 55vw pattern
COMPONENTS still contains it
```

hoặc:

```text
Coverage Matrix mentions mutation
Contract has no matching command
```

## Validator checks nên bổ sung

### V-01 — Version coherence

Current status files phải match package versions:

```text
DS = 1.4
Technical = 1.5
```

### V-02 — Unique Acceptance IDs

Regex tất cả:

```text
AC-[A-Z0-9-]+
```

và fail duplicates ngoài intentional cross-reference.

### V-03 — Command registry coverage

```text
UI mutation
→ permission
→ command
→ contract
→ acceptance
```

### V-04 — Email semantics

Fail legacy phrases:

```text
retry must not create duplicate messages
retries do not duplicate sends
exactly once
```

trừ section explicitly mô tả chúng là impossible/forbidden.

### V-05 — Drawer old rule

Search toàn Design package, không chỉ RESPONSIVE:

```text
55vw
760–860px
```

nếu current rule đã thay.

### V-06 — Master guard completeness

Master declared `Phase1 + structural history protected` phải có:

- schema trigger/command guard;
- usage check.

### V-07 — Rate-limit closure

Nếu technical matrix nói RESOLVED, phải có rate-limit policy table với endpoint/key/window/default.

### V-08 — Generated All-in-One equality

Regenerate and compare.

### V-09 — Current docs only

Detect stale “CURRENT v1.3/v1.4” labels trong current v1.5 package, excluding changelog/history.

### V-10 — Document action coverage

Nếu UI page chứa:

```text
Upload / Replace / Delete
```

command registry phải có corresponding mutation.

---

# 31. Known intentional open gates — không tính là lỗi mới

Các mục sau đã được package hiện tại thừa nhận là **chưa production-frozen**; tôi không coi chúng là “bị bỏ sót”:

1. executable RLS/GRANT migrations;
2. adversarial RLS tests;
3. actual RPC/command implementation;
4. schedule race tests;
5. migration clean-install test;
6. Storage policies/two-phase upload integration;
7. malware scanner/provider integration;
8. auth provisioning/recovery implementation tests;
9. query-plan/performance testing;
10. backup/restore rehearsal;
11. desktop prototype sync/UAT;
12. Candidate mobile UAT;
13. official EIU PDF pixel template nếu operational PDF được dùng.

Đây là các **implementation/go-live gates**, không nên bị trộn với specification findings phía trên.

---

# 32. Những phần hiện đã có chất lượng tốt và nên giữ

## Domain architecture

```text
Candidate
→ Submission
→ Application
→ Interview
→ Participant
→ Report
```

vẫn là decomposition sạch.

## Candidate form

Form Session + staged upload là hướng tốt vì:

- không tạo Submission giả/DRAFT ngoài business model;
- file và text có Save/Cancel semantics chung;
- malware validation xảy ra trước materialization;
- HR NEW→READ race được re-check.

## Submission state

Single authoritative recalculation + `Submission FOR UPDATE` là thiết kế tốt. Chỉ cần đóng contradiction Candidate Reactivate và aggregate version cho file-only edit.

## Interview concurrency

Interview-row-first + deterministic resource locking + recheck là một contract mạnh và phù hợp với race cases thực tế.

## Identity

Internal first Google bind đã tách đúng khỏi identity rebind. Root break-glass được đưa thành procedure riêng là đúng hướng.

## Documents

Logical header + immutable versions + current index + malware CLEAN requirement là nền tảng tốt.

## Email

Transactional outbox + worker lease + stale-SENDING recovery + provider metadata + at-least-once wording là đúng. Việc còn lại chủ yếu là làm acceptance/design wording khớp architecture.

## Design

- 16px operational text;
- explicit table widths;
- sticky identity columns;
- no generic `overflow-wrap:anywhere`;
- Privacy component;
- SubmissionSelector;
- AuthBindingBadge;
- MasterUsageGuard;
- PII search không serialize URL;
- gold accessibility restriction;

đều là cải thiện đúng và nên giữ.

---

# 33. Recommended Fix Order

## Batch 1 — đóng contradiction/blocker

1. **P0-01** Candidate Reactivation status.
2. **P0-03** Email delivery wording trong Acceptance + Design.
3. **P0-04** Internal User deactivate target rules.
4. **P0-02** HR Submission docs / Interview doc delete / Email History delete command coverage.

## Batch 2 — data/security invariants

5. Candidate Auth recreated rebind.
6. File-only Submission version bump.
7. Privacy Notice authoritative version.
8. Email Outbox/History `submission_id`.
9. Application Reactivate duplicate/multi-child semantics.
10. Room historical master guard.

## Batch 3 — technical closure

11. Rate-limit matrix.
12. Web security baseline.
13. Export/archive/purge runbook.
14. exact hard-delete permissions.
15. HR owner permission/command boundary.
16. `app_spec` conflict-engine consistency.
17. hard-delete/open-form-session cleanup ordering.

## Batch 4 — design/docs/validator

18. Drawer contradiction.
19. HR Inbox FileList/FilePreview.
20. duplicate Acceptance ID.
21. stale version labels.
22. component numbering.
23. remove open-ended bulk wording.
24. generator + All-in-One equality.
25. semantic validator expansion.

---

# 34. Proposed Gate Status After This Review

Tôi đề nghị giữ trạng thái:

```text
Business Logic Core        = FROZEN
Design System v1.4         = CURRENT / REVIEW REQUIRED on identified inconsistencies
Technical Architecture v1.5 = REVIEWED / NOT YET FROZEN
Implementation Gate        = NOT YET PASS
Production Ready           = NO
```

Không cần reopen toàn bộ Business Logic. Chỉ cần issue một **targeted amendment** cho P0-01 và các exact permission/command semantics liên quan.

Sau khi P0 + P1 source contradictions được sửa, chạy lại:

```text
1. Package validator
2. Design validator
3. Semantic cross-layer validator
4. External review
5. Technical Pre-code Gate
```

Chỉ khi tất cả pass với **fresh evidence** mới chuyển:

```text
Technical Architecture = FROZEN
Implementation Gate = PASS
```

---

# 35. Final Assessment

Bản v1.5/v1.4 đã ở mức **rất gần một handover có thể giao cho engineering/coding agent mà không phải tự sáng tạo nghiệp vụ**. Phần lớn rủi ro còn lại không phải là “thiếu chức năng lớn”, mà là các chỗ rất cụ thể nơi:

- hai tài liệu hiện cùng đúng theo cách riêng nhưng cho kết quả khác nhau;
- UI cho phép mutation nhưng command layer chưa có contract tương ứng;
- validation tự động kiểm tra presence nhưng chưa kiểm tra semantic contradiction;
- một số security/governance boundary chưa được chuyển từ ngôn ngữ “theo rule/authorized” thành exact authorization predicate.

Đây là giai đoạn phù hợp để **giảm ambiguity thay vì thêm feature**.

Ưu tiên cao nhất là làm cho source of truth đạt điều kiện:

> Với bất kỳ UI action hoặc business event nào, một reviewer có thể lần theo đúng một đường:
>
> **Actor → Permission → UI State → Command → Lock/Transaction → DB Invariant → Side Effects → Audit → Acceptance Test**
>
> và không có hai tài liệu khác nhau trả lời khác nhau về cùng một outcome.

Khi đạt điều đó, package sẽ đủ mạnh để chuyển từ “reviewed specification” sang “implementation contract”.

---

## Appendix A — Source files trọng tâm đã đối chiếu

### Full Handover v1.5

- `00_README.md`
- `01_PRODUCT_SCOPE_AND_ARCHITECTURE.md`
- `02_ROLES_PERMISSIONS_AND_NAVIGATION.md`
- `03_CANDIDATE_FORM_AND_PORTAL.md`
- `04_HR_APPLICATION_INBOX.md`
- `05_HR_INTERVIEW_PAGE.md`
- `06_INTERVIEW_REPORT_HR_AND_INTERVIEWER.md`
- `07_STATUS_AND_BUSINESS_RULES.md`
- `08_DATA_MODEL_AND_FIELD_DICTIONARY.md`
- `09_MASTER_DATA_CATALOG.md`
- `10_UI_UX_SPEC.md`
- `11_EMAIL_DOCUMENTS_AND_ACTIVITY_LOG.md`
- `13_ACCEPTANCE_CRITERIA_AND_TEST_CASES.md`
- `14_SCOPE_AND_OPEN_ITEMS.md`
- `15_ALL_IN_ONE_SPEC.md`
- `37_BACKEND_COMMAND_CONTRACTS.md`
- `38_NON_FUNCTIONAL_REQUIREMENTS.md`
- `39_SECURITY_RLS_MATRIX.md`
- `40_DATABASE_INVARIANTS.md`
- `41_STORAGE_AND_UPLOAD_SECURITY.md`
- `42_PRIVACY_RETENTION_COMPLIANCE.md`
- `43_EMAIL_DELIVERY_SPEC.md`
- `44_DEPLOYMENT_OPERATIONS.md`
- `45_PRODUCTION_UAT_GATE.md`
- `46_AUTH_IDENTITY_MODEL.md`
- `47_AUDIT_LOGGING_SPEC.md`
- `48_IDEMPOTENCY_CONCURRENCY_SPEC.md`
- `52_TECHNICAL_GATE_STATUS.md`
- `53_FINAL_CONSISTENCY_VALIDATION.md`
- `54_SCHEMA_CONFORMANCE_MATRIX.md`
- `55_COMMAND_COVERAGE_MATRIX.md`
- `58_SEARCH_AND_INDEXING_STRATEGY.md`
- `59_RLS_POLICY_BLUEPRINT.md`
- `61_ROOT_ADMIN_BREAK_GLASS_RECOVERY.md`
- `62_VALIDATION_CONTRACT.md`
- `63_BATCH_OPERATION_SEMANTICS.md`
- `64_MASTER_DATA_HISTORY_POLICY.md`
- `65_TECHNICAL_PRECODE_GATE_V1_5.md`
- `app_spec.yaml`
- `database_schema.sql`
- `technical_review_matrix.csv`
- `permissions_matrix.csv`
- `validation_contract.yaml`
- `logic_validation/*`
- `tools/validate_package.py`

### Design System v1.4

- `00_README.md`
- `MASTER.md`
- `TOKENS.md`
- `COMPONENTS.md`
- `PATTERNS.md`
- `TABLE_LAYOUT.md`
- `RESPONSIVE.md`
- `ACCESSIBILITY.md`
- `AUTH_AND_LOGIN.md`
- `SIDEBAR_NAVIGATION.md`
- `PAGE_OVERRIDES_V1_4.md`
- `DESIGN_REVIEW_CHECKLIST.md`
- `page_component_matrix.csv`
- `component_inventory.csv`
- `tools/validate_design.py`
- `DESIGN_VALIDATION.txt`

---

## Appendix B — Suggested next review criterion

Ở vòng kế tiếp, ngoài validator hiện có, nên review theo 5 trục độc lập:

```text
1. Business / Spec
2. Technical Integrity / Concurrency
3. Security / Privacy
4. Design / Accessibility
5. Evidence / Testability
```

Một feature chỉ được PASS khi cả năm trục đều pass hoặc có documented intentional deferral.

