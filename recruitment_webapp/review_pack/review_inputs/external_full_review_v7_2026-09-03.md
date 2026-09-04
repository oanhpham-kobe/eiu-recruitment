# EIU Recruitment Web App — Full Review Report
## Baseline: Full Handover v1.8 + Design System v1.7

**Ngày review:** 03/09/2026  
**Phạm vi:** review lại từ đầu, chỉ sử dụng hai package hiện tại làm **source of truth**:

1. `App_Tuyen_Dung_EIU_Full_Handover_v1.8.zip`
2. `EIU_Recruitment_Design_System_v1.7.zip`

**SHA-256 baseline**

- Full Handover v1.8: `70d606d4ce34a85c72aeaf74a96acf02e31640fe5bcdaf64542b38b5982984ed`
- Design System v1.7: `dfea3bdc0a61f4cf00240082f2f0a6668e3cc2d2bdb3ccff71bd4862cb31b892`

> Các version trước không được dùng để suy ra trạng thái hiện tại.  
> ECC / Superpowers / Matt Pocock / ByteByteGo chỉ được dùng như **review lenses** (domain, security, PostgreSQL, concurrency, React/a11y, testing, click-path, evidence); chúng không override source-of-truth EIU.

---

# 1. Executive Summary

v1.8 + Design System v1.7 đã đạt mức rất cao cho một **pre-code handover**. Nhiều vấn đề của các vòng trước đã được đưa xuống thành machine-readable registry, SQL constraints, semantic validator và release-evidence requirements.

## Fresh automated evidence

Tôi đã chạy lại validator trực tiếp trên đúng hai package này:

```text
PACKAGE VALIDATION — Full Handover v1.8 / Design System v1.7
TOTAL=299 PASS=299 FAIL=0
```

```text
DESIGN VALIDATION — EIU Recruitment Design System v1.7
TOTAL=65 PASS=65 FAIL=0
```

Đây là kết quả rất tốt.

Tuy nhiên:

> `299/299 PASS` và `65/65 PASS` chỉ chứng minh toàn bộ **checks hiện được implement** đã pass; chúng chưa chứng minh tất cả semantic contradiction và adversarial state paths đã được kiểm tra.

Manual review còn phát hiện một số vấn đề cần đóng trước **Technical Architecture Freeze**.

## Reviewer recommendation

| Layer | Đề nghị |
|---|---|
| Business Logic Core v1.2 | **Giữ FROZEN** |
| Domain model | **Rất gần FROZEN** |
| Canonical schedule predicates | **REVIEW REQUIRED** |
| Backend command/batch contracts | **REVIEW REQUIRED** |
| PostgreSQL starter | **REVIEW REQUIRED tại một số DB invariants** |
| RLS/Security architecture | **Gần FROZEN** |
| Privacy/Storage/Email | **Gần FROZEN** |
| Design System v1.7 | **CURRENT; không thấy visual blocker mới** |
| Technical Architecture v1.8 | **NOT YET FROZEN** |
| Implementation Gate | **NOT YET PASS** |
| Production Ready | **NO** |

---

# 2. Findings Summary

## P0 — Nên đóng trước Technical Architecture Freeze

| ID | Finding | Type |
|---|---|---|
| **P0-01** | `resource_blocking` và `schedule_conflict_relevant` đang được dùng như hai “canonical conflict predicates” khác nhau | Domain / concurrency contradiction |
| **P0-02** | HR có thể manual set Submission thành `READ` khi vẫn có active Application, phá derived-state authority | State-machine / SQL defect |
| **P0-03** | UI expose nhiều bulk actions nhưng không có named batch commands tương ứng, trái hard rule của Batch/Command architecture | UI → command contract gap |

## P1 — Nên đóng trước implementation freeze

| ID | Finding |
|---|---|
| P1-01 | Inactive master “không được chọn mới” chưa được enforce nhất quán cho Unit/Team/Position/Room/Qualification/Source/Reasons |
| P1-02 | Re-add Participant không yêu cầu Internal User vẫn Active; deactivation cũng có thể strand future current participants |
| P1-03 | Candidate Form Session chưa có DB invariant `target Submission belongs to same Candidate` |
| P1-04 | Published Privacy Notice bất biến khi UPDATE nhưng chưa được bảo vệ khỏi DELETE |
| P1-05 | “Structurally empty default Round 1” được dùng ở nhiều business commands nhưng chưa có exact canonical predicate |
| P1-06 | Participant lifecycle chưa có DB CHECK giữa `is_current` và `removed_at` |
| P1-07 | Candidate verified email được gọi immutable nhưng DB chưa có immutability guard |
| P1-08 | `12_IMPLEMENTATION_NOTES_VERCEL_SUPABASE.md` là CURRENT/NORMATIVE nhưng vẫn trỏ technical source về `37–50` |
| P1-09 | Email Outbox actor columns chưa có actor consistency CHECK |
| P1-10 | Submission hard-delete làm `email_history.submission_id` mất qua `SET NULL`; cần xác nhận đây là intentional traceability policy |

## P2 — Hardening / maintainability

- Nên rename `schedule_conflict_relevant` thành `reactivation_conflict_relevant` nếu nó thực sự chỉ là exception cho lifecycle recovery.
- Privacy Notice content hash cần canonical hashing procedure rõ.
- Nên thêm exact DB test cho inactive-master selection.
- Nên thêm FK/index/query-plan evidence trên migration thật.
- Browser QA / click-path / React Testing vẫn là implementation/release evidence, không thể PASS ở pre-code stage.
- Responsive detailed design vẫn NOT FROZEN; Candidate mobile vẫn là go-live gate — đây là intentional current status, không phải lỗi mới.

---

# 3. P0-01 — Canonical Schedule Conflict Predicate vẫn bị chia làm hai nghĩa

Đây là finding quan trọng nhất của vòng này.

## Current glossary

`73_DOMAIN_GLOSSARY_AND_CANONICAL_PREDICATES.md` định nghĩa:

```text
resource_blocking
=
access_active
AND schedule_status_code != CANCELLED
AND start_at/end_at exist
```

và:

```text
schedule_conflict_relevant
=
resource_blocking
AND end_at > transaction_now
```

Sau đó glossary nói:

```text
Operational schedule conflict checks use every schedule_conflict_relevant Interview.
```

Tức là **Interview đã kết thúc** không tham gia conflict checks.

---

## Nhưng Concurrency spec lại nói khác

`48_IDEMPOTENCY_CONCURRENCY_SPEC.md`:

```text
Every resource_blocking Interview participates in conflict checks,
whether or not it is Current Round.
```

Đây là predicate rộng hơn và bao gồm các interval đã trôi qua.

---

## app_spec.yaml cũng chia behavior

`app_spec.yaml`:

```yaml
engine_used_by:
  - save_or_reschedule
  - add_participant_when_resource_blocking
  - readd_participant_when_resource_blocking
  - reactivate_interview
  - cancelled_to_active
  - reactivate_application_non_elapsed_schedule_conflict_relevant_children
```

Điều này cho thấy intent thực tế dường như là:

### Direct schedule/resource mutation

```text
resource_blocking
```

### Application Reactivate lifecycle recovery

```text
resource_blocking AND end_at > now()
```

Trong `77_EXTERNAL_REVIEW_V6_RESOLUTION.md` cũng ghi:

```text
Reactivation conflicts use non-elapsed schedule_conflict_relevant;
past-only overlaps do not strand lifecycle recovery.
```

Như vậy câu trong Glossary:

```text
Operational schedule conflict checks use every schedule_conflict_relevant
```

đang rộng quá mức.

---

## Các file CURRENT còn lệch ở Application Reactivate

Ví dụ:

### `05_HR_INTERVIEW_PAGE.md`

```text
Application Reactivate ...
revalidates all child Interviews that would become resource_blocking
```

### `13_ACCEPTANCE... AC-APP-REACT-05`

```text
revalidates every child Interview that would become resource_blocking
```

### `59_RLS_POLICY_BLUEPRINT.md`

```text
every child that becomes resource_blocking participates in conflict checks
```

Trong khi authoritative v1.8 Reactivate contract nói:

```text
only non-elapsed schedule_conflict_relevant children
```

và:

```text
fully elapsed intervals do not block reactivation
```

---

## Vì sao đây là lỗi thực tế

Giả sử:

```text
Interview A lịch sử:
01/08 09:00–10:00

Interview B lịch sử:
01/08 09:30–10:30
```

Application A hiện inactive.

Ngày 03/09 HR Reactivate A để tiếp tục tuyển dụng.

Nếu code dùng:

```text
resource_blocking
```

A có thể bị block bởi một conflict **đã kết thúc hơn một tháng trước**.

Nếu dùng:

```text
schedule_conflict_relevant
```

A được Reactivate đúng theo v1.8 resolution.

Coding agent hiện có thể chọn cả hai interpretation tùy file đọc.

---

## Đề nghị

### Phương án tôi khuyến nghị

Giữ:

```text
resource_blocking
```

là predicate của **normal schedule/resource integrity**.

Đổi tên:

```text
schedule_conflict_relevant
```

thành:

```text
reactivation_conflict_relevant
```

với definition:

```text
resource_blocking AND end_at > transaction_now
```

và ghi rõ:

> Đây là lifecycle-recovery exception chỉ dùng khi parent Application Reactivate.  
> Không phải canonical predicate thay thế `resource_blocking` cho mọi scheduling operation.

Sau đó sửa đồng bộ:

- `05`
- `13 AC-APP-REACT-05`
- `59`
- `73`
- `48`
- `app_spec.yaml`
- command registry guarantee tags.

Nếu owner thật sự muốn **mọi** conflict check bỏ qua fully elapsed intervals, thì phải đổi `48`, `40`, `app_spec` và direct mutation commands tương ứng. Nhưng current v1.8 resolution cho thấy intent gần với **reactivation-only exception** hơn.

## Validator mới

Fail nếu:

```text
Application Reactivate
→ resource_blocking
```

không kèm non-elapsed exception.

**Severity: P0.**

---

# 4. P0-02 — Manual `READ` có thể phá Derived Submission State

Đây là lỗi cụ thể trong business contract + SQL starter.

## Canonical model

`07_STATUS_AND_BUSINESS_RULES.md`:

```text
Manual:
NEW
READ

Derived:
PROCESSED
DONE
CLOSED
```

và:

```text
only authoritative recalculation may set derived states
```

Khi có active Application:

```text
non-final → PROCESSED
HIRED → DONE
all REJECTED → CLOSED
```

---

## Backend command hiện tại

`37_BACKEND_COMMAND_CONTRACTS.md`:

```text
Only NEW and READ are manually writable.
Cannot set NEW while active Application exists.
```

Chỉ block `NEW`, không block `READ`.

---

## SQL thực tế

`private.set_submission_manual_status()`:

```sql
if p_status not in ('NEW','READ') then
  reject;
end if;

if p_status = 'NEW'
   and active Application exists
then
  reject;
end if;

update submissions
set status_code = p_status;
```

Tức là:

```text
Submission = DONE
Active Application vẫn tồn tại
HR request READ
→ ACCEPTED
```

hoặc:

```text
PROCESSED → READ
```

Trong khi active Application vẫn tồn tại.

Đây là contradiction trực tiếp với derived-state authority.

---

## Consequence

Sau thao tác:

```text
Application outcome = HIRED
Submission = READ
```

Hệ thống ở trạng thái không hợp lệ cho tới một mutation khác vô tình trigger recalculation.

Không nên dựa vào “eventual recalculation” để sửa một illegal command.

---

## Đề nghị

Manual `NEW` và `READ` chỉ legal khi:

```text
NO active Application
```

Pseudo:

```sql
if exists (
  select 1
  from applications
  where submission_id = p_submission_id
    and is_active = true
) then
  raise CANNOT_SET_MANUAL_STATUS_WHILE_ACTIVE_APPLICATION_EXISTS;
end if;
```

Exception:

```text
open_submission():
NEW → READ
```

vẫn hợp lệ vì ở thời điểm Submission mới chưa có active Application.

---

## Acceptance cần thêm

```text
AC-STAT-05
Active Application + manual READ request → reject.

AC-STAT-06
Active Application + manual NEW request → reject.

AC-STAT-07
No active Application + NEW/READ manual request → allowed.

AC-STAT-08
PROCESSED/DONE/CLOSED can be changed only by authoritative recalculation.
```

**Severity: P0 — confirmed state-machine/SQL defect.**

---

# 5. P0-03 — Bulk UI và Batch Command Architecture chưa khớp

Đây là cross-layer gap.

## Hard rule

`63_BATCH_OPERATION_SEMANTICS.md`:

```text
Each action maps to a named batch command and declares atomicity.
```

`37_BACKEND_COMMAND_CONTRACTS.md`:

```text
Bulk delete/inactive/status:
explicit contract must state atomic vs partial before the UI exposes it.
```

Rất đúng.

---

## Nhưng UI hiện expose nhiều hơn command registry

### HR Submission Inbox

`04_HR_APPLICATION_INBOX.md`:

```text
Bulk:
- Inactive
- Active lại
- Mark as New / Read
```

Registry hiện chỉ có:

```text
bulk_mark_submission_new
```

Không có:

```text
bulk_set_candidate_active
bulk_mark_submission_read
```

Ngoài ra parent row là Candidate group, nên phải xác định bulk Active/Inactive đang target:

```text
Candidate?
latest Submission?
selected child Submission?
```

Không thể để frontend tự suy diễn.

---

## Interview Page

Toolbar:

```text
Xóa
Đổi status
Gửi thư ứng viên
Gửi thư người tham dự
```

và table có selection/checkbox.

Hiện:

```text
bulk_enqueue_email
```

có command.

Nhưng không có explicit:

```text
bulk_delete_or_inactivate_interviews
bulk_change_interview_schedule_status
```

Trong khi Batch spec nói UI không được expose trước khi command atomicity được freeze.

---

## Vì sao không nên gọi single command N lần từ browser

Ví dụ chọn 10 Interviews:

```text
1–6 thành công
7 conflict
8–10 chưa chạy
```

UI đã hứa bulk action nhưng kết quả trở thành partial mutation không có semantics thống nhất.

Điều này đặc biệt nguy hiểm với:

```text
Inactive
Reactivate
Schedule Status
Delete
```

vì chúng có conflict/usage/lifecycle invariants.

---

## Hai cách sửa hợp lệ

### Option A — đơn giản nhất

Nếu Phase 1 không thực sự cần những bulk actions:

> **Bỏ chúng khỏi UI/spec.**

Giữ:

- Bulk Mark New;
- Bulk common Application assignment;
- Bulk email.

Đây là hướng YAGNI tốt.

### Option B

Thêm explicit batch commands, ví dụ:

```text
bulk_set_candidate_active(...)
bulk_set_submission_manual_status(...)
bulk_delete_or_inactivate_interviews(...)
bulk_change_interview_schedule_status(...)
```

và mỗi command freeze:

```text
selection entity
permission
ALL_OR_NOTHING / PER_ITEM
locks
conflict behavior
audit
response
idempotency
acceptance
```

Tôi nghiêng **Option A** nếu vận hành EIU chưa có nhu cầu bulk thật sự.

**Severity: P0 vì current architecture tự quy định UI không được expose action thiếu batch contract.**

---

# 6. P1-01 — Inactive Master không được chọn mới nhưng DB enforcement còn không đồng đều

Business rule rất rõ:

```text
Inactive master
→ valid for historical reference
→ unavailable for new selection
```

Backend generic master section cũng nói:

```text
inactive historical masters remain readable/operable
but cannot be selected for new references
```

## SQL đã làm tốt cho

### Document Type

Có trigger chặn inactive type khi create logical document.

### Interview Format

Có rule:

```text
inactive format cannot be selected for new/change operation
```

và giữ historical format operable.

---

## Nhưng chưa thấy equivalent physical guard cho

- Unit;
- Department Team;
- Position;
- Position Group;
- Room;
- Qualification;
- Recruitment Source;
- Cancellation Reason;
- Rejection Reason.

Ví dụ `validate_position_hierarchy()` hiện kiểm:

```text
Position thuộc Unit/Team
```

nhưng không kiểm:

```text
Position.is_active
Unit.is_active
Team.is_active
```

khi Application mới được create.

`Room` cũng chưa được active-check khi đổi sang room mới.

---

## Rủi ro

Frontend có thể ẩn inactive option, nhưng crafted trusted request/RPC bug vẫn có thể tạo:

```text
new Application → inactive Position
new Interview → inactive Room
new Education row → inactive Qualification
```

trái frozen master lifecycle.

---

## Đề nghị

Canonical invariant:

```text
INSERT or changed FK:
referenced master must be ACTIVE.

Unchanged existing historical FK:
inactive remains valid.
```

Không phải reject mọi UPDATE lịch sử chỉ vì master sau này inactive.

Implement:

- trusted command validation;
- DB trigger/guard cho critical structural masters.

Ưu tiên DB guard cho:

```text
Application Unit/Team/Position
Interview Room
Qualification
Recruitment Source
Reason fields
```

Thêm acceptance theo **master family**, không cần một test cho từng table.

---

# 7. P1-02 — Re-add Participant cần yêu cầu User Active

Current master user rule:

```text
inactive user cannot login or be newly selected;
historical snapshots remain.
```

`add_interview_participant()` đúng:

```text
Active user
```

Nhưng `readd_interview_participant()` chỉ nói:

```text
historical Participant
RESTORE OLD / CREATE NEW
no duplicate
conflict re-check
```

không nói:

```text
app_user must still be Active
```

## Scenario

1. HR X từng là participant.
2. Remove X.
3. Root/Directory later inactive X.
4. HR Re-add historical X.
5. X trở thành `is_current=true`.
6. RLS/Auth lại chặn X vì `app_user.is_active=false`.

Kết quả:

```text
Current Interview Participant
→ cannot access Interview
→ cannot submit report
```

## Đề nghị

Cả hai re-add modes yêu cầu:

```text
app_user.is_active = true
```

Nếu inactive:

```text
USER_INACTIVE_NOT_SELECTABLE
```

Historical Participant/Report vẫn đọc được cho internal history.

---

## Internal User deactivation cũng cần future-participant policy

`set_internal_user_active()` hiện xử lý rất tốt Active Application ownership.

Nhưng chưa có rule cho HR/User đang là:

```text
current participant
of a future/non-elapsed Interview
```

Nếu deactivate, một panel sắp diễn ra có thể thiếu interviewer.

Cần một deterministic policy:

### A — khuyến nghị

Block deactivation khi user là current participant của:

```text
schedule_conflict_relevant / future Interview
```

cho tới khi remove/replace participant.

Hoặc:

### B

Allow deactivation nhưng tạo explicit operational warning/action-required.

Không nên im lặng strand lịch phỏng vấn.

---

# 8. P1-03 — Candidate Form Session thiếu DB ownership invariant

Schema:

```text
candidate_form_sessions:
candidate_id
target_submission_id
```

DB check chỉ enforce:

```text
NEW → target NULL
EDIT → target NOT NULL
```

Không có physical invariant:

```text
target_submission.candidate_id
=
candidate_form_session.candidate_id
```

Normal trusted command/RLS có owner checks nên đường chuẩn an toàn.

Nhưng physical starter vẫn có thể biểu diễn:

```text
Candidate A Form Session
→ targets Submission of Candidate B
```

nếu có trusted-function bug/migration/admin mistake.

Với một system đang chủ động dùng defense-in-depth, đây nên được khóa.

## Đề nghị

Trigger:

```text
EDIT_SUBMISSION
→ target Submission must belong to same candidate_id
```

và recheck under lock khi Save.

---

# 9. P1-04 — Published Privacy Notice chưa được bảo vệ khỏi DELETE

Current schema có:

```text
privacy_notice_immutable_guard
BEFORE UPDATE
```

và function bảo vệ:

- version;
- content VI/EN;
- content hash;
- published date;
- effective date;
- creator.

Đúng.

Nhưng không có:

```text
BEFORE DELETE
```

guard.

## Scenario

Một Privacy Notice published nhưng chưa có:

- Form Session;
- acknowledgement;

thì FK `ON DELETE RESTRICT` chưa chặn.

Direct maintenance delete có thể:

- xóa lịch sử publish;
- xóa current row;
- tạo `PRIVACY_NOTICE_UNAVAILABLE` outage.

## Đề nghị

Published notice:

```text
DELETE forbidden
```

trừ một documented break-glass/legal purge process nếu sau này thật sự cần.

New wording:

```text
create new version
→ switch current
→ old version retained
```

là sạch nhất.

---

# 10. P1-05 — “Structurally Empty Round 1” chưa có exact definition

Concept này đang được dùng cho ít nhất:

```text
unused Application hard-delete
copy to another Application
fill default Round1 vs create next round
```

Nhưng tôi không thấy một canonical predicate trả lời chính xác:

> Khi nào Round 1 được coi là structurally empty?

Hai developer có thể hiểu khác nhau.

## Đề nghị định nghĩa một helper/invariant

Ví dụ:

```text
round_no = 1
AND auto_created_default = true / inferable default
AND no real schedule interval
AND no non-default format/room/link
AND no Demo Topic
AND no Participant
AND no Report
AND no Interview Document
AND no operational Email usage
AND no Interview/HR notes
AND schedule/report statuses still default initial values
AND no meaningful business transition history
```

Activity/Security Audit alone không nên biến nó thành “used” nếu delete matrix hiện đã chốt như vậy.

Tốt nhất tạo:

```text
is_structurally_empty_default_round(interview_id)
```

dùng chung cho:

- copy;
- hard-delete;
- acceptance tests.

---

# 11. P1-06 — Participant lifecycle cần DB CHECK

Schema hiện có:

```text
is_current
removed_at
```

nhưng không có constraint giữa hai field.

Commands imply canonical states:

### Current

```text
is_current = true
removed_at = NULL
```

### Removed historical

```text
is_current = false
removed_at != NULL
```

DB hiện vẫn cho:

```text
is_current=true, removed_at!=NULL
```

hoặc:

```text
is_current=false, removed_at=NULL
```

Nếu không có legitimate third state, thêm CHECK:

```sql
check (
  (is_current = true and removed_at is null)
  or
  (is_current = false and removed_at is not null)
)
```

Điều này hỗ trợ RLS/current participant logic rất tốt.

---

# 12. P1-07 — Candidate verified email chưa có DB immutability guard

Source truth:

```text
Candidate email = verified identity
immutable normal profile field
```

Candidate/Auth rebind hiện thay:

```text
auth_user_id
```

chứ không phải email.

Submission snapshot guard cũng đảm bảo Submission email khớp Candidate.

Nhưng SQL vẫn cho direct:

```sql
UPDATE candidates SET email = ...
```

nếu một privileged function/migration viết nhầm.

## Đề nghị

Normal DB guard:

```text
Candidate.email immutable after creation.
```

Nếu tương lai EIU thật sự cần legal identity/email change:

```text
dedicated privileged identity-change procedure
```

với verification/audit, không dùng generic UPDATE.

---

# 13. P1-08 — CURRENT Implementation Notes vẫn trỏ source technical về `37–50`

`source_registry.yaml` đánh dấu:

```text
12_IMPLEMENTATION_NOTES_VERCEL_SUPABASE.md
CURRENT / NORMATIVE
```

Nhưng đầu file vẫn ghi:

```text
Technical source-of-truth chi tiết nằm ở 37–50.
```

Trong v1.8, các source technical quan trọng kéo dài qua:

```text
59 RLS
62 Validation
63 Batch
64 Master History
67 Web Security
68 Rate Limits
70 Semantic Gate
73 Canonical Predicates
75 Release Evidence
76 Dependency Baseline
78 Privacy Publication
79 Current Pre-code Gate
```

Một implementer đọc file 12 có thể dừng quá sớm.

## Đề nghị

Không hard-code range.

Sửa thành:

```text
Current technical source-of-truth is determined by source_registry.yaml.
Use CURRENT/NORMATIVE technical entries and current Review/Gate entrypoints.
```

Validator nên fail stale source ranges trong bất kỳ file:

```text
CURRENT + normative
```

---

# 14. P1-09 — Email Outbox actor attribution nên có CHECK

`email_outbox` có:

```text
created_by_app_user_id
created_by_candidate_id
```

nhưng chưa thấy DB constraint tương tự:

```text
at most one human actor
```

Trong khi Activity/Security Audit đã được harden theo hướng đó.

Nếu `actor_scope`/command semantics xác định một email logical enqueue chỉ có một initiating human actor, thêm CHECK:

```text
not both populated
```

và nếu actor type yêu cầu người dùng:

```text
exactly one
```

System-generated email có thể để cả hai NULL nếu đó là intentional state.

Đây là audit-quality hardening.

---

# 15. P1-10 — Submission hard-delete và Email traceability cần owner-confirmed policy

Email Outbox/History đã thêm:

```text
submission_id
```

để trace exact Candidate Submission.

Nhưng nếu unused Submission được hard-delete, FK có thể:

```text
ON DELETE SET NULL
```

cho email trace.

Điều này cho phép delete đúng frozen unused rule, nhưng sau đó Email History mất relational link tới exact Submission.

Không nhất thiết sai.

Cần chỉ ghi rõ policy:

### Nếu intentional

```text
Business Submission may hard-delete when unused.
Operational email row may remain with immutable message/audit metadata
but relational submission_id becomes NULL.
Security Audit preserves deletion context.
```

### Nếu exact-submission trace phải tồn tại suốt retention

thì hard-delete eligibility phải coi Email History/Outbox production usage là downstream reference.

Chỉ cần owner/Legal/Operations chọn một hướng; không nên để behavior là side effect ngầm của FK.

---

# 16. Design System v1.7 Review

Manual review + validator không phát hiện visual architecture regression mới.

## Verified good

### Tables

- Application Inbox: **1560px**
- Interview: **1480px**
- HR Report: **1610px**

### Drawer

Không còn legacy contradiction `760px minimum + 55vw cap`.

### Candidate Form

Có:

- NEW/EDIT Privacy acknowledgement;
- server-pinned notice version;
- Save/Submit validity;
- mobile direction.

### SubmissionSelector

Đúng exact Submission identity, không chỉ Candidate name/email.

### Users & Permissions

Design v1.7 đã phân persona:

- Root xem granular effective permissions;
- non-root Directory Manager không xem permission list của người khác;
- user có thể xem own effective permissions.

### Accessibility

Đã có:

- 16px operational text;
- touch target goal 44px;
- 200% text zoom;
- 400% reflow where applicable;
- keyboard semantic controls;
- sticky-column focus;
- gold not used as normal body text;
- focus/live/error requirements.

## Current intentional design gates

Package vẫn ghi:

```text
Detailed iPad/mobile layouts = NOT FROZEN
Desktop prototype requires v1.7 resync/UAT
Candidate mobile = go-live requirement
```

Tôi không xem đây là defect mới vì package đã self-declare đúng trạng thái.

---

# 17. Click-path / Browser-QA Readiness

Chưa có rendered implementation/staging trong hai ZIP nên không thể claim:

```text
Browser QA PASS
Click-path PASS
React tests PASS
```

Điều đúng hiện tại là:

```text
spec defines required evidence
→ implementation must produce it later
```

Các critical click paths nên giữ trong Release Evidence:

1. Candidate stage replace/delete → Cancel.
2. Candidate edit → HR opens NEW→READ → Candidate Save fails safely.
3. Row click vs checkbox vs status badge vs Action.
4. Copy Interview draft → Cancel/Save.
5. Remove/Re-add Participant → Restore/Create new.
6. Application Reactivate → future conflict vs past-only overlap.
7. Bulk operation failure/rollback.
8. Bound Internal identity generic Edit cannot rebind.
9. Master inactive row cannot be newly selected.
10. Privacy version switch while Candidate has open Form Session.
11. VI/EN switch with dirty form.
12. Drawer Escape/close/focus restoration.

---

# 18. PostgreSQL Review — Current Direction

Current schema has improved substantially:

- global Application durable identity;
- zero-UUID sentinel physically reserved;
- logical document current-version constraints;
- staged target current-version checks;
- Report lifecycle CHECK;
- owner lifecycle guard;
- Candidate inactive lifecycle CHECK;
- Privacy SHA shape;
- audit actor constraints;
- current/access/resource implementation views;
- RLS baseline notes.

Các P1 phía trên là **hardening/invariant completion**, không phải lý do redesign PostgreSQL model.

Before production migration freeze, still require:

```text
clean install migration
adversarial RLS tests
concurrent race tests
FK/index audit
EXPLAIN (ANALYZE, BUFFERS) on realistic data
backup/restore rehearsal
```

Đây là implementation evidence, không phải missing business spec.

---

# 19. Validator Improvements

Current validator **299 checks** đã rất mạnh.

Để bắt findings vòng này, tôi đề nghị thêm:

## V-01 — Manual status derived-state invariant

Executable DB/static test:

```text
active Application + set READ
→ FAIL
```

---

## V-02 — Conflict-predicate vocabulary

Machine check:

```text
Direct schedule/resource mutation
→ resource_blocking

Application Reactivate
→ non-elapsed reactivation predicate
```

Không cho current docs gọi cả hai là universal conflict predicate.

---

## V-03 — Bulk UI → Batch command

Parse known Phase-1 bulk action registry:

```text
UI bulk action
→ named bulk command
→ atomicity
→ acceptance
```

Nếu không có command:

```text
UI action must be OUT OF SCOPE / removed.
```

---

## V-04 — Active master reference guards

For every Phase-1 selectable master:

```text
new/changed FK requires active
historical unchanged inactive allowed
```

---

## V-05 — Participant user lifecycle

```text
readd inactive user → FAIL
```

và deactivation future-participant policy has acceptance.

---

## V-06 — Candidate Form Session ownership

```text
EDIT session Candidate A → Candidate B Submission
→ FAIL
```

---

## V-07 — Privacy DELETE immutability

Published notice normal DELETE:

```text
FAIL
```

---

## V-08 — CURRENT source pointer

Any:

```text
CURRENT + normative
```

file containing obsolete technical range like:

```text
37–50
```

must fail.

---

# 20. Recommended Fix Order

## Batch 1 — P0

1. Canonicalize schedule predicates / Reactivation exception.
2. Block manual NEW **and READ** whenever active Application exists.
3. Remove unsupported bulk UI actions **or** add named batch commands.

## Batch 2 — Data/security invariants

4. Active-master new-reference guards.
5. Re-add requires Active user + freeze deactivation/future-participant policy.
6. Candidate Form Session candidate/target consistency.
7. Privacy Notice DELETE guard.
8. Define `structurally_empty_default_round`.
9. Participant current/removed DB CHECK.
10. Candidate email immutability.

## Batch 3 — documentation/traceability

11. Fix file 12 stale source pointer.
12. Freeze Submission-delete ↔ Email-history trace policy.
13. Add Outbox actor consistency CHECK.
14. Extend validator V-01…V-08.

## Batch 4 — implementation evidence

15. Actual RLS migrations/tests.
16. DB concurrency tests.
17. React component tests.
18. Click-path audit.
19. Browser QA + responsive/a11y UAT.
20. Backup/restore + deployment rehearsal.

---

# 21. Gate Recommendation

Tôi đề nghị:

```text
Business Logic Core v1.2
= FROZEN
```

Không cần reopen workflow tuyển dụng tổng thể.

```text
Design System v1.7
= CURRENT / REVIEWED
```

Không phát hiện blocker visual mới.

Nhưng:

```text
Technical Architecture v1.8
= REVIEWED / TARGETED AMENDMENT REQUIRED / NOT FROZEN
```

vì P0-02 là một confirmed state/SQL defect, còn P0-01/P0-03 là contract ambiguity/gap có thể làm hai implementation khác nhau.

```text
Implementation Gate = NOT YET PASS
Production Ready = NO
```

---

# 22. Final Assessment

v1.8 + Design System v1.7 hiện **rất gần Technical Freeze**.

Không cần thay đổi kiến trúc chính:

```text
Candidate
→ Submission
→ Application
→ Interview
→ Participant
→ Report
```

Không cần thêm microservice, Kafka, Redis hay framework mới chỉ để “đúng best practice”.

Các việc có leverage cao nhất lúc này là:

1. **làm predicate và state machine tuyệt đối đơn nghĩa**;
2. **không expose UI mutation nếu chưa có trusted command tương ứng**;
3. **đưa các frozen business rules xuống DB defense-in-depth ở những chỗ security/data integrity quan trọng**;
4. **giảm semantic drift trong CURRENT/NORMATIVE docs**;
5. sau đó chuyển trọng tâm từ review spec sang **implementation evidence**.

Tiêu chuẩn nên đạt trước Technical Freeze:

> Với mỗi production action, phải có đúng một đường:
>
> **Actor → Permission → UI action → Trusted Command → Lock/Transaction → DB invariant → Side effects → Audit → Acceptance Test**
>
> và không có tài liệu CURRENT nào tạo interpretation thứ hai.

v1.8 đã đạt phần lớn điều kiện này. Ba P0 nêu trên là những điểm tôi khuyên đóng trước khi chuyển sang Freeze.

---

# Appendix A — Fresh Validation Evidence

```text
Full Handover v1.8 + Design v1.7
TOTAL=299
PASS=299
FAIL=0
```

```text
Design System v1.7
TOTAL=65
PASS=65
FAIL=0
```

---

# Appendix B — External Review Lenses Applied

Chỉ dùng để **đặt câu hỏi và stress-test**, không làm source-of-truth:

- ECC:
  - documentation-lookup
  - postgres-patterns
  - security-review
  - accessibility
  - react-patterns
  - react-testing
  - browser-qa
  - architecture-decision-records
  - tdd-workflow
  - frontend-a11y
  - click-path-audit
  - api-design where applicable
- Superpowers:
  - systematic debugging
  - verification-before-completion
- Matt Pocock skills:
  - domain/source-of-truth
  - spec-vs-standards
  - writing for agents
- ByteByteGo:
  - concurrency
  - locking/isolation
  - upload/storage
  - delivery semantics
  - pagination/system-design failure modes

---

# Appendix C — Suggested New Acceptance Cases

```text
AC-STAT-05
Active Application + manual READ → reject.

AC-STAT-06
Active Application + manual NEW → reject.

AC-SCH-PRED-01
Normal schedule/resource mutations use the frozen direct-conflict predicate.

AC-SCH-PRED-02
Application Reactivate ignores fully elapsed past-only overlap exactly according to frozen lifecycle-recovery rule.

AC-BULK-01
Every visible Phase-1 bulk action maps to one named batch command with declared atomicity.

AC-MASTER-ACTIVE-01
New/change reference cannot select inactive Unit/Team/Position/Room/Qualification/Source/Reason; existing unchanged historical reference remains valid.

AC-PART-ACTIVE-01
Re-add inactive Internal User → reject.

AC-FORM-OWNER-01
Candidate Form EDIT session cannot target another Candidate's Submission.

AC-PRIV-DELETE-01
Published Privacy Notice cannot be deleted through normal/maintenance path.

AC-ROUND-EMPTY-01
Default Round1 structural-empty predicate produces identical result in Copy and unused-Application delete flows.

AC-PART-LIFE-01
Current Participant implies removed_at NULL; removed historical Participant implies removed_at non-NULL.

AC-CAND-EMAIL-01
Candidate verified email cannot be modified by normal profile/business mutation.
```
