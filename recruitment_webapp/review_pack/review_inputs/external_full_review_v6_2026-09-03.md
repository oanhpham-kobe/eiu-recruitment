# EIU Recruitment Web App — Full Review Report
## Baseline: Full Handover v1.7 + Design System v1.6

**Ngày review:** 03/09/2026  
**Phạm vi review:** review lại từ đầu, chỉ sử dụng hai package hiện tại làm **source of truth**:

1. `App_Tuyen_Dung_EIU_Full_Handover_v1.7.zip`
2. `EIU_Recruitment_Design_System_v1.6.zip`

**SHA-256**

- Full Handover v1.7: `81817fe463ccbdb8fcf2e4d15cff4fa37093343171a3fb845f3fb0df9f2dab43`
- Design System v1.6: `8f61d0654955e68caa324de688be2a2ae4eb0951e11ebb11ca8e83e33e0ca1fe`

> Các version cũ không được dùng để suy ra trạng thái hiện tại.  
> ECC / Superpowers / Matt Pocock / ByteByteGo chỉ được dùng như **review lenses**; chúng không override nghiệp vụ hoặc design source-of-truth EIU.

---

# 1. Executive Summary

v1.7 + Design System v1.6 đã tiến thêm đáng kể so với một pre-code specification thông thường. Source governance, canonical predicates, privacy/edit flow, command registry, release evidence, dependency policy và semantic validator đều đã được nâng cấp.

## Fresh automated evidence

Tôi đã chạy lại validator trực tiếp trên đúng hai package hiện tại:

```text
PACKAGE VALIDATION — Full Handover v1.7 / Design System v1.6
TOTAL=232 PASS=232 FAIL=0
```

```text
DESIGN VALIDATION — EIU Recruitment Design System v1.6
TOTAL=63 PASS=63 FAIL=0
```

Đây là kết quả rất tốt.

Tuy nhiên:

> `232/232 PASS` và `63/63 PASS` chỉ có nghĩa **toàn bộ check đang được implement đã pass**.  
> Nó không có nghĩa mọi semantic contradiction, security edge case hoặc cross-layer invariant đều đã được kiểm tra.

Manual semantic review vẫn tìm thấy một số vấn đề cần đóng trước **Technical Architecture Freeze**.

## Reviewer status recommendation

| Layer | Đề nghị |
|---|---|
| Business Logic Core v1.2 | **Giữ FROZEN** |
| Domain predicates v1.7 | **Gần FROZEN** |
| Backend Command Contracts | **REVIEW REQUIRED** |
| Physical PostgreSQL starter | **REVIEW REQUIRED tại một document-plan invariant** |
| RLS/Security architecture | **Gần FROZEN; còn Email History/User Permissions edge** |
| Concurrency architecture | **Tốt; cần chốt past-interval reactivation** |
| Privacy | **Tốt; publication lifecycle cần runbook/command rõ hơn** |
| Design System v1.6 | **CURRENT; không thấy layout blocker mới** |
| Technical Architecture v1.7 | **NOT YET FROZEN** |
| Implementation Gate | **NOT YET PASS** |
| Production Ready | **NO** |

---

# 2. Findings Summary

## P0 — nên sửa trước Technical Architecture Freeze

| ID | Finding | Loại |
|---|---|---|
| **P0-01** | Hai trusted commands cùng có quyền đổi **Report Status**, trái hard rule “one UI mutation → one command”; một path không explicit Submission recalculation | Command/domain consistency |
| **P0-02** | Candidate staged `REPLACE/DELETE` có thể target logical document lịch sử không còn current; document-plan validator giả định REPLACE không đổi cardinality | Data integrity / crafted-request bypass |
| **P0-03** | Một số file CURRENT/NORMATIVE vẫn chứa đoạn cũ mâu thuẫn với canonical v1.7 ở cuối file | Source-of-truth / agent reliability |

## P1 — nên đóng trước implementation freeze

| ID | Finding |
|---|---|
| P1-01 | `command_registry.yaml` side effects chưa exhaustive cho outcome-changing commands |
| P1-02 | `emails.history_delete` thiếu parent read/context dependency và “wrong/test record” chưa có eligibility rule máy có thể enforce |
| P1-03 | Active Application có thể giữ HR owner đã inactive/mất HR role; Reactivate không revalidate owner |
| P1-04 | Application Reactivate có thể bị block bởi **past-vs-past** schedule conflicts |
| P1-05 | Design Users & Permissions có `Effective permissions` column nhưng security matrix chỉ cho non-root HR self/effective view nếu cần |
| P1-06 | Privacy Notice publication/current-switch lifecycle chưa có trusted command hoặc maintenance runbook rõ |
| P1-07 | Candidate inactive metadata (`inactive_at/by`) chưa có lifecycle semantics rõ |
| P1-08 | `database_schema.sql` header và Design README còn reference version cũ |
| P1-09 | Report lifecycle `is_active/is_archived` chưa có DB CHECK canonical |
| P1-10 | Command Registry acceptance mapping có trường hợp “ID tồn tại nhưng không test đúng behavior” |

## P2 — hardening

- Application nullable-Team global unique index dùng zero-UUID sentinel; có thể thay bằng `NULLS NOT DISTINCT` nếu target PostgreSQL hỗ trợ và team zero UUID không được cấm.
- Final Decision Source timestamp tie hiện fallback UUID; có thể dùng monotonic decision revision nếu cần tuyệt đối deterministic.
- Audit rows chưa có DB check “at most one human actor”.
- Privacy `content_hash_sha256` / document checksums chưa có format-length CHECK.
- Consolidate current docs **in place** thay vì tiếp tục append “v1.x clarification” làm source ngày càng dài.
- Browser QA / click-path evidence vẫn là implementation/release gate, chưa thể PASS ở pre-code stage.

---

# 3. P0-01 — Hai trusted commands cùng thay đổi Report Status

## Hard architecture rule

`37_BACKEND_COMMAND_CONTRACTS.md` mở đầu:

```text
Every UI mutation maps to one explicit trusted backend command.
```

Nhưng current report contract có hai command:

### Path A

```text
update_hr_report_management()
→ edits HR-only hr_report_note AND Report Status
```

### Path B

```text
change_report_status(interview_id, status, expected_version)
→ changes current-round Report Status
→ outcome-changing status invokes parent Submission recalculation
```

`55_COMMAND_COVERAGE_MATRIX.md` còn map một UI capability:

```text
HR Report status/note
→ change_report_status / update_hr_report_management
```

Tức là cùng một field `report_status_code` có **hai mutation paths**.

## Vì sao nguy hiểm

Report Status ảnh hưởng:

```text
Current Round report status
→ Application effective outcome
→ Submission DONE/CLOSED/PROCESSED
```

`change_report_status()` explicit nói phải recalculate parent Submission.

`update_hr_report_management()` lại không explicit cùng side effect.

Một implementation agent có thể triển khai:

```text
Edit HR Note dialog
→ update_hr_report_management(report_status=HIRED)
→ Interview status đổi
→ Submission không recalc
```

=> derived state drift.

Ngoài ra đây trực tiếp vi phạm nguyên tắc “one mutation → one trusted command”.

## Đề nghị

### Khuyến nghị sạch nhất

Tách responsibility:

```text
update_hr_report_note(interview_id, hr_report_note, expected_version)
```

chỉ sửa:

```text
hr_report_note
```

và:

```text
change_report_status(interview_id, status, expected_version)
```

chỉ sửa:

```text
report_status_code
```

`change_report_status` bắt buộc:

```text
lock Current Round
→ validate permission/state
→ update status
→ recalculate_submission_status()
→ audit
→ commit
```

Hoặc nếu muốn một command duy nhất:

```text
update_hr_report_management(...)
```

thì **xóa `change_report_status`** và contract chính phải bao phủ đầy đủ outcome recalculation.

Không nên giữ cả hai.

## Acceptance gap

Cả hai command registry hiện trỏ `AC-27`.

Nhưng `AC-27` thực tế chỉ test:

```text
HR Report page one row/Application using Current Active Latest Round
```

Nó không test:

- status mutation;
- HR Note confidentiality;
- recalculation;
- stale version.

### Nên tạo

```text
AC-REPORT-STATUS-01
HIRED/REJECTED/non-final Report Status mutation recalculates parent Submission in same transaction.

AC-REPORT-STATUS-02
Only Current Round Report Status is mutable from HR Report page.

AC-HR-NOTE-01
HR Report Note mutation never writes Interview Note and never exposes note to Interviewer.

AC-REPORT-STATUS-03
There is exactly one trusted mutation path for report_status_code.
```

**Severity: P0.**

---

# 4. P0-02 — Staged REPLACE có thể resurrect historical logical document và bypass max-file plan

Đây là finding ở `database_schema.sql`.

## Current document model

Persisted Submission files:

```text
submission_document_logicals
→ immutable logical parent/type

submission_documents
→ versions
→ one current version/logical ID
```

Đúng hướng.

Candidate EDIT stages:

```text
ADD
REPLACE
DELETE
```

trong `candidate_form_document_changes`.

## Guard hiện tại

`private.validate_candidate_form_document_change()` khi `REPLACE/DELETE` chỉ kiểm tra:

```text
logical belongs to target Submission
AND logical document type matches
```

Nó **không kiểm tra target logical hiện đang có một current version**.

## Plan validator lại giả định

Trong `private.validate_candidate_form_document_plan()`:

```text
Existing current logical documents
- DELETE
+ ADD

REPLACE keeps cardinality/type.
```

`effective_count` chỉ bắt đầu từ logical documents có:

```text
exists submission_documents where is_current=true
```

## Crafted-request scenario

Giả sử Submission từng có:

```text
Logical A
v1 → is_current=false
```

và không còn current version của Logical A.

Candidate hiện có đủ:

```text
5 current logical files
```

Một request thủ công stage:

```text
REPLACE target_logical_document_id = historical Logical A
```

Guard hiện tại cho phép vì Logical A vẫn thuộc đúng Submission/type.

Plan validator:

```text
current count = 5
REPLACE assumed cardinality-neutral
effective_count = 5
```

Nếu materialization tạo version mới:

```text
Logical A v2 → current=true
```

thì persisted state thực tế thành:

```text
6 current logical files
```

Ngoài max-file bypass, action này còn **resurrect** một logical document đã không còn current mà UI bình thường có thể không hiển thị.

## Đề nghị

Với `REPLACE` và `DELETE`, cả stage-time và Save-time phải enforce:

```text
target logical belongs to Submission
AND exactly one current version exists
```

Pseudo check:

```sql
if action_code in ('REPLACE','DELETE') then
  if not exists (
    select 1
    from submission_documents v
    where v.logical_document_id = target_logical_document_id
      and v.is_current = true
  ) then
    raise INVALID_DOCUMENT_TARGET;
  end if;
end if;
```

Save transaction phải lock:

```text
logical header
+ current version
```

để target không đổi giữa stage và Save.

HR command:

```text
mutate_submission_documents_by_hr()
```

cũng phải dùng cùng target-current invariant.

## Acceptance cần thêm

```text
AC-DOC-TARGET-01
REPLACE historical logical document with no current version → reject.

AC-DOC-TARGET-02
DELETE historical logical document with no current version → reject.

AC-DOC-TARGET-03
Crafted REPLACE cannot raise effective current file count beyond 5.

AC-DOC-TARGET-04
Stage valid current target, target changes before Save → stale/invalid target, no silent resurrection.
```

**Severity: P0 — real data-integrity gap in starter schema/plan validator.**

---

# 5. P0-03 — CURRENT source files vẫn giữ nội dung cũ mâu thuẫn với canonical v1.7

v1.7 đã cải thiện `source_registry.yaml` rất nhiều:

```text
CURRENT
HISTORICAL
normative
```

và historical review/gate docs được exclude khỏi normative All-in-One.

Điểm còn lại:

> Một số **file đang được đánh dấu CURRENT/NORMATIVE** tự chứa đoạn cũ và đoạn canonical mới khác nhau.

Với coding agent, “đọc file đến đâu” không nên quyết định semantics.

---

## 5.1 Interviewer contextual access — cùng file `02`

Section đầu của `02_ROLES_PERMISSIONS_AND_NAVIGATION.md` ghi:

```text
participant.user_id = current_user
AND participant.is_current = true
AND interview.is_active = true
AND visible_to_interviewers = true
AND app_user.is_active = true
```

Thiếu:

```text
application.is_active = true
```

Trong cuối cùng file, canonical v1.7 lại đúng:

```text
Application.is_active
AND Interview.is_active
AND participant.is_current
AND visibility
AND active user
```

Security docs 39/59 cũng dùng canonical parent-active predicate.

### Risk

Agent chỉ đọc section “Interviewer” sớm có thể triển khai authorization thiếu parent Application.

Đây là security-sensitive source contradiction.

### Sửa

**Thay trực tiếp block cũ** bằng canonical predicate.

Không nên giữ:

```text
old block
...
later clarification says old block incomplete
```

trong một source CURRENT.

---

## 5.2 Candidate selector — file `10`

Section 9 hiện vẫn ghi generic:

```text
Candidate selector searches:
name / email / phone

Candidate option:
Nguyễn Văn A
abc@email.com
```

Nhưng v1.7 domain đã chốt:

```text
Application source = exact Submission
```

và cuối file mới clarify:

```text
SubmissionSelector
→ Candidate name
→ email
→ submitted date
→ status
→ returns submission_id
```

Design System v1.6 cũng đã đúng.

### Sửa

Section 9 phải viết thẳng:

```text
SubmissionSelector
```

không còn “Candidate selector”.

---

## 5.3 Submission Document Data Dictionary — file `08`

Current section:

```text
Document version record:
document_id
logical_document_id
submission_id
document_type_id
version_no...
```

Nhưng physical v1.7 model đúng là:

```text
submission_document_logicals
  logical_document_id
  submission_id
  document_type_id

submission_documents
  document_id
  logical_document_id
  version/storage metadata
```

`54_SCHEMA_CONFORMANCE_MATRIX.md` cũng nói parent/type nằm trên logical header.

### Risk

Coding agent có thể thêm:

```text
submission_id
document_type_id
```

vào version row để “match Data Dictionary”, tạo redundant/inconsistent schema.

### Sửa

Thay section 3 bằng hai entity rõ ràng:

```text
Submission Document Logical Header
Submission Document Version
```

---

## Review rule đề nghị

Đối với `CURRENT + normative` files:

> Canonical v1.7 phải được **consolidate in place**.  
> “v1.4/v1.5/v1.6 clarification” chỉ nên ở Changelog/Resolution logs.

Validator nên scan các known canonical sections để không còn legacy block tương phản.

**Severity: P0 cho source-of-truth reliability trước AI implementation handoff.**

---

# 6. P1-01 — Machine-readable command side-effects chưa exhaustive

`37` hard rule:

```text
Each command defines side effects.
Any outcome-changing command must recalculate Submission in same transaction.
```

Nhưng `command_registry.yaml` hiện vẫn để:

```yaml
side_effects: []
```

cho các command mà contract Markdown nói có recalculation, ví dụ:

```text
create_or_update_application
delete_or_inactivate_application
create_next_interview_round
delete_or_inactivate_interview
change_report_status
set_candidate_active
```

Ví dụ:

```text
create_or_update_application()
→ recalculates Submission
```

nhưng Registry:

```yaml
side_effects: []
```

`reactivate_application` lại có:

```yaml
recalculate_submission_status
```

nên machine contract hiện không đồng nhất.

## Vì sao đáng sửa

v1.7 đã cố ý chuyển sang:

```text
command_registry.yaml
```

để coding agent/validator có machine-readable truth.

Nếu Registry chỉ exhaustive cho một subset side effects thì agent không biết field này là:

```text
authoritative
```

hay:

```text
illustrative.
```

## Đề nghị

Thêm minimum required side effects:

```yaml
create_or_update_application:
  - recalculate_submission_status

delete_or_inactivate_application:
  - recalculate_submission_status

create_next_interview_round:
  - recalculate_submission_status_when_current_changes

delete_or_inactivate_interview:
  - recalculate_submission_status_when_outcome_changes

change_report_status:
  - recalculate_submission_status

set_candidate_active:
  - recalculate_all_candidate_submissions_by_reactivation_rule
```

Nếu dùng conditional effect, encode condition explicit.

Validator:

```text
all outcome-changing commands
→ registry contains recalculate side-effect
```

không chỉ selected command list.

---

# 7. P1-02 — Email History Delete chưa có enforceable context/eligibility model

Current permission:

```text
emails.history_delete
```

Command:

```text
delete_email_history(email_history_id)
Requires emails.history_delete.
```

Permission dependency table không yêu cầu:

```text
submissions.view
interviews.view
reports.view
```

hay một:

```text
emails.history_view
```

Security read matrix cũng không có generic Email History read permission.

## Risk 1 — Delete without parent contextual read

Một HR Limited có thể được cấp:

```text
emails.history_delete
```

nhưng không có quyền xem parent Submission/Interview.

Nếu biết/nhận được `email_history_id`, contract hiện không nói command phải verify parent context.

Đây là authorization asymmetry.

## Risk 2 — “wrong/test record” không machine-enforceable

Business nói Delete chỉ cho:

```text
wrong/test records
```

Nhưng `email_history` schema không có:

```text
is_test
environment
history_classification
deletable_reason_code
```

Vì vậy backend không có deterministic predicate để biết row nào là “wrong/test”, trừ việc tin actor tự xác nhận.

## Chọn một semantics

### Option A — operational rows broadly deletable

Nếu HR có đúng quyền thì mọi Email History operational row có thể delete:

```text
mandatory reason
+ immutable audit
```

→ sửa wording “wrong/test only”.

### Option B — đúng “wrong/test only”

Thêm classification:

```text
history_classification = PRODUCTION | TEST | ERROR
```

hoặc eligibility rule machine-readable.

Và authorization:

```text
emails.history_delete
AND parent contextual read
```

hoặc tạo:

```text
emails.history_view
```

và dependency:

```text
emails.history_delete -> emails.history_view
```

---

# 8. P1-03 — HR owner invariant không được giữ qua User lifecycle

Application creation/owner update đúng:

```text
hr_owner must be Active HR/root
```

DB trigger:

```text
application_owner_identity_guard
```

chỉ chạy khi update:

```text
submission_id
unit_id
department_team_id
position_id
hr_owner_id
```

Nó **không chạy khi chỉ Reactivate Application**.

Trong khi Root có thể:

```text
Inactive HR user
remove HR role
```

và source nói historical ownership vẫn giữ.

## Scenario

1. Application A đang Inactive.
2. `hr_owner_id = HR X`.
3. Root remove HR role hoặc inactive X.
4. HR khác Reactivate A.
5. `reactivate_application()` không yêu cầu owner vẫn Active HR/root.
6. Application active trở lại với owner không còn eligible.

Cùng vấn đề có thể tồn tại với một Application vẫn active khi owner bị inactive/role removed.

## Cần chốt semantics

### Khuyến nghị

Historical Application:

```text
inactive owner reference được giữ
```

Operational Active Application:

```text
must have eligible active HR/root owner
```

Khi Root inactive/remove-role một HR đang own active Applications:

- warn/block cho tới khi reassigned; hoặc
- allow but set explicit `UNASSIGNED/OWNER_INACTIVE` operational state.

Với current non-null `hr_owner_id`, đơn giản nhất:

```text
require reassignment before HR deactivation/role removal
```

hoặc Reactivate yêu cầu chọn new active owner atomically.

Thêm acceptance:

```text
AC-OWNER-LIFE-01
Cannot reactivate Application with ineligible owner without reassignment.

AC-OWNER-LIFE-02
Root deactivating/removing HR role with active owned Applications follows one deterministic reassignment/block policy.
```

---

# 9. P1-04 — Past Interview conflicts có thể chặn Reactivate Application vì lịch đã qua

Canonical:

```text
resource_blocking =
access_active
AND non-CANCELLED
AND interval exists
```

Không có điều kiện thời gian hiện tại.

`reactivate_application()`:

```text
enumerates every child that would become resource_blocking
→ re-check Candidate/Room/Interviewer overlap
→ any conflict blocks entire reactivation
```

Concurrency doc nói:

```text
Past intervals remain historical rows and naturally do not overlap future intervals.
```

Điều này đúng với **past-vs-future**.

Nhưng chưa xử lý **past-vs-past**.

## Scenario

- Application A bị inactive.
- A có Interview cũ: 01/08 09:00–10:00.
- Trong lúc A inactive, Application B hợp lệ có record 01/08 09:30–10:30 cùng room/interviewer.
- Ngày 03/09 HR muốn Reactivate A để tạo vòng mới trong tương lai.

Reactivation có thể re-check hai interval lịch sử:

```text
09:00–10:00
09:30–10:30
```

và block toàn Application mặc dù conflict không còn khả năng ảnh hưởng vận hành.

## Đề nghị

Không nhất thiết đổi `resource_blocking` nếu từ này dùng cho historical modeling.

Có thể định nghĩa predicate riêng:

```text
schedule_conflict_relevant
=
resource_blocking
AND end_at > transaction_now
```

Hoặc rule command:

```text
Reactivate validates only intervals not fully elapsed.
```

Past history vẫn được giữ/access, nhưng không ngăn một lifecycle recovery hiện tại.

Nếu owner cố ý muốn past conflict block reactivation thì phải ghi rõ rationale + recovery path.

---

# 10. P1-05 — Users & Permissions Design có thể lộ permission data ngoài security intent

Design v1.6 `PAGE_OVERRIDES_V1_6.md` quy định exact columns:

```text
Họ tên
Email EIU
Auth binding
Active
HR role
Effective permissions
Cập nhật gần nhất
Action
```

Business cho HR mặc định:

```text
users.directory_manage
```

nhưng không cho:

```text
users.permissions_manage
```

Security matrix lại ghi:

```text
Permissions:
HR → own effective view if desired
Root → all
```

## Ambiguity

HR Directory Manager có được xem `Effective permissions` của **mọi user** hay không?

Design table hiện nhìn như có.

## Đề nghị

### Root

```text
Effective permissions column/details = full
Permission editor = available
```

### non-root with `users.directory_manage`

Directory data:

```text
Name
Email
Bound/Unbound
Active
role/protected state needed for lifecycle
```

Nhưng permission detail:

```text
hidden
or self-only
```

trừ khi owner chủ ý tạo thêm read permission.

Nếu HR cần xem permission của người khác để support vận hành, thêm explicit:

```text
users.permissions_view
```

thay vì ngầm lộ qua directory page.

---

# 11. P1-06 — Privacy Notice publication lifecycle chưa có operational command/runbook

Current model đã tốt:

```text
privacy_notice_versions
immutable published fields
is_current pointer
Form Session selects:
is_current=true AND effective_from<=now()
fail closed if none
```

Nhưng việc **publish/switch current** chưa có trusted command trong `command_registry.yaml`.

Schema Conformance nói:

```text
controlled admin/deployment
```

nhưng operational procedure chưa rõ.

## Failure scenario

Admin/deployment:

1. insert notice version có `effective_from` ngày mai;
2. set nó `is_current=true` ngay hôm nay;
3. old row current=false.

Form Session query:

```text
current=true AND effective_from<=now()
```

→ không có row.

Toàn Candidate Form fail:

```text
PRIVACY_NOTICE_UNAVAILABLE
```

Có thể fail-safe là đúng, nhưng publish flow không nên vô tình tạo outage.

## Đề nghị

Hoặc:

### Deployment-only runbook

```text
publish_privacy_notice_version
```

với transaction:

- insert new immutable version;
- schedule current switch at effective time;
- preserve one current/effective row throughout;
- audit;
- rollback instructions.

Hoặc trusted Root/Admin command riêng.

Không cần UI nếu Legal/IT chỉ thay bằng deployment, nhưng process phải deterministic.

---

# 12. P1-07 — Candidate inactive metadata semantics chưa được định nghĩa

Schema:

```text
candidates.is_active
candidates.inactive_at
candidates.inactive_by
```

Data Dictionary gọi đây là physical inactive metadata.

Nhưng `set_candidate_active()` chưa nói:

### Inactivate

```text
inactive_at = now?
inactive_by = actor?
```

### Reactivate

- clear `inactive_at/by`?
- hay retain latest inactivation metadata?

Audit Log đã giữ full history, nên physical fields cần một nghĩa rõ.

## Khuyến nghị

Nếu tên giữ như hiện tại:

```text
is_active=false:
  inactive_at = now()
  inactive_by = actor

is_active=true:
  inactive_at = NULL
  inactive_by = NULL
```

Security Audit lưu toàn bộ lịch sử.

Nếu muốn retain lần inactive gần nhất ngay cả khi active thì rename:

```text
last_inactive_at
last_inactive_by
```

để tránh semantic mismatch.

---

# 13. P1-08 — Version metadata drift nhỏ vẫn còn

## `database_schema.sql`

Header hiện:

```text
Technical starter schema v1.6
Production requires ... docs 37–71
```

Current package:

```text
Technical v1.7
current technical docs extends to 76
```

## Design `00_README.md`

Ghi:

```text
technical amendments are tracked in Full Handover v1.6
```

Current là Full Handover v1.7.

Không ảnh hưởng runtime, nhưng với AI-agent handover đây là stale reference.

## Sửa

```text
database_schema.sql:
Technical starter schema v1.7
production source registry / docs 37–76 as CURRENT

Design README:
technical amendments tracked in Full Handover v1.7
```

Validator thêm header/current-reference checks.

---

# 14. P1-09 — Report lifecycle nên có DB CHECK

`interview_reports` có hai flags:

```text
is_active
is_archived
```

Current normal states dường như:

### current

```text
is_active=true
is_archived=false
```

### historical archived

```text
is_active=false?
is_archived=true
```

Restore:

```text
is_active=true
is_archived=false
```

Nhưng schema hiện có thể chứa:

```text
is_active=true
is_archived=true
```

hoặc:

```text
is_active=false
is_archived=false
```

Unique index chỉ coi:

```text
active=true AND archived=false
```

là active report.

## Đề nghị

Nếu business chỉ có hai canonical lifecycle states, thêm CHECK.

Ví dụ:

```sql
check (
  (is_active = true and is_archived = false)
  or
  (is_active = false and is_archived = true)
)
```

Nếu `inactive non-archived` là một legitimate state, document nó rõ và dùng enum/status sẽ sạch hơn hai booleans độc lập.

Đây là defense-in-depth, không phải current flow blocker.

---

# 15. P1-10 — Acceptance traceability hiện mới kiểm “ID tồn tại”, chưa kiểm “ID chứng minh command”

Validator hiện kiểm:

```text
Registry acceptance reference exists
```

Đó là tốt nhưng chưa đủ.

Ví dụ:

```text
change_report_status
update_hr_report_management
```

đều trỏ:

```text
AC-27
```

Trong khi `AC-27` chỉ test:

```text
one row/Application on HR Report Current Round
```

Nó không chứng minh behavior của hai commands.

## Đề nghị

Command registry acceptance phải là **behavioral evidence**, không chỉ một ID hợp lệ.

Có thể thêm metadata:

```yaml
acceptance:
  - id: AC-REPORT-STATUS-01
    guarantees:
      - current_round_only
      - submission_recalculated_same_transaction
      - permission_and_stale_version
```

Validator không cần hiểu prose NLP; chỉ cần check required guarantee tags.

---

# 16. Design System v1.6 Review

## 16.1 Những điểm đã verify tốt

Không thấy regression lớn ở Design System.

### Table arithmetic

| Page | Frozen width |
|---|---:|
| Application Inbox | **1560px** |
| Interview | **1480px** |
| HR Report | **1610px** |

### Candidate Form

Đã có:

```text
NEW_SUBMISSION Privacy
EDIT_SUBMISSION Privacy
server-pinned version
Save disabled until acknowledgement
```

### SubmissionSelector

Design component đúng:

```text
Candidate name
verified email
Submission date
Submission status
returns submission_id
```

### Accessibility

Có:

- semantic controls;
- focus management;
- 44px target goal;
- 200% text zoom;
- 400% reflow where applicable;
- sticky-column focus;
- keyboard row expansion;
- status not color-only;
- normal operational text 16px;
- gold restricted from normal body text.

### Release evidence

`75_RELEASE_EVIDENCE_MATRIX.md` đã đưa:

- 375 / 768 / 1280 / 1440;
- Candidate/HR journeys;
- click-path cases;
- axe + manual keyboard/screen-reader sanity;
- visual baseline missing = `INCONCLUSIVE`.

Đây là hướng tốt.

---

## 16.2 Design finding còn lại

Finding chính của Design System là **Users & Permissions permission visibility** ở P1-05.

Ngoài ra, `10_UI_UX_SPEC.md` generic Candidate selector là lỗi ở Handover source, không phải Design v1.6 — Design đã sửa đúng thành `SubmissionSelector`.

---

# 17. Concurrency / Failure-path Review

## Đã tốt

Current v1.7 đã tách rõ:

```text
access_active
current_round
resource_blocking
```

và:

```text
resource_blocking rounds all participate in conflicts
```

Interview-row-first locking + deterministic resource locks là contract tốt.

Candidate/Room/Interviewer đều BLOCK.

Application durable identity đã chuyển thành global unique, loại bỏ active/inactive duplicate identity ambiguity.

## Còn cần đóng

Chủ yếu:

1. P1-04 past-vs-past conflict khi Reactivate.
2. P1-03 owner lifecycle khi Reactivate.
3. P0-02 staged-document target race/currentness.
4. Report Status command collision vì outcome recalculation là cross-transaction invariant.

---

# 18. Security Review

Current architecture nhìn chung đúng hướng:

- public browser không dùng secret/service role;
- RLS + grants tách riêng;
- private implementation views;
- `security_invoker`;
- Candidate ownership;
- Interviewer parent-Application contextual access;
- private Storage;
- short signed URL;
- bound identity rebind privileged;
- PII search không URL;
- malware CLEAN fail-closed;
- CSP/CORS/CSRF/cache/redaction baseline.

External current Supabase documentation vẫn xác nhận các assumptions cốt lõi này: grants và RLS là hai checks khác nhau, views cần xử lý RLS riêng, và secret/service-role access bypasses RLS nên phải server-only.

### Security gaps còn lại

- Email History delete contextual authorization/eligibility.
- Users Permissions display scope.
- Current `02` early Interviewer predicate phải consolidate để không tạo implementation drift.

---

# 19. Framework / Dependency Lens

`76_DEPENDENCY_BASELINE_POLICY.md` chọn đúng cách:

> Không hard-code một version framework lâu dài trong business spec; khi scaffold implementation phải lấy current patched supported version, pin exact dependency + lockfile + regression evidence.

Điều này đặc biệt phù hợp vì Next.js vẫn có security release mới trong tháng 08/2026.

Do đó tôi **không đề nghị sửa Handover để ghi cứng một Next.js version cụ thể ngay bây giờ**.

Khi implementation bắt đầu:

```text
package.json exact versions
lockfile
DEPENDENCY_BASELINE evidence
security advisory check
Auth/RSC/SSR regression suite
```

là đúng.

---

# 20. Validator Improvements

v1.7 validator đã mạnh hơn nhiều: **232 checks**.

Các check mới tôi đề nghị để bắt findings vòng này:

## V-01 — One mutable field → one command

Machine registry thêm:

```yaml
writes:
  - interviews.report_status_code
```

Validator fail nếu hai production commands cùng claim write cùng protected field, trừ explicit merge/alias group.

Điều này sẽ bắt P0-01.

---

## V-02 — Outcome command side effects exhaustive

All commands touching:

```text
Application active/create
Current Round lifecycle
report_status_code
```

phải include:

```text
recalculate_submission_status
```

trong registry side effects.

---

## V-03 — Staged REPLACE/DELETE current-target

Schema static check hoặc migration test:

```text
REPLACE/DELETE historical logical no-current
→ FAIL
```

---

## V-04 — CURRENT source canonical block replacement

Không chỉ tìm canonical token ở đâu đó trong file.

Check legacy patterns bị loại:

```text
Interviewer predicate missing Application.is_active
Candidate selector option only name/email
Document version row contains submission_id/document_type_id
```

---

## V-05 — Acceptance relevance

Command Registry dùng guarantee tags, không chỉ existing AC ID.

---

## V-06 — Security display scope

Cross-check Design components requiring permission detail với security read matrix.

---

## V-07 — Current version headers

Check:

```text
database_schema.sql v1.7
Design README → Full Handover v1.7
```

---

# 21. Recommended Fix Order

## Batch 1 — blockers

1. **Unify Report Status mutation command.**
2. Add **current-version target guard** for Candidate/HR REPLACE/DELETE.
3. Consolidate canonical v1.7 text **in place** in `02`, `08`, `10`.

## Batch 2 — machine contract/security

4. Make Registry side-effects exhaustive.
5. Define Email History view/delete context + eligibility.
6. Define HR owner lifecycle/reassignment.
7. Fix Users & Permissions visibility by persona.

## Batch 3 — lifecycle/operations

8. Freeze past-interval Reactivate conflict rule.
9. Add Privacy Notice publication/current-switch runbook.
10. Define Candidate inactive metadata.
11. Add Report lifecycle DB constraint if only two states are legal.

## Batch 4 — cleanup/evidence

12. Fix stale version headers.
13. Add behavior-specific Acceptance IDs.
14. Extend semantic validator with V-01…V-07.
15. Re-run external review + Pre-code Gate 74.

---

# 22. Gate Recommendation

Tôi đề nghị giữ:

```text
Business Logic Core v1.2 = FROZEN
```

Không có finding nào buộc redesign workflow HR tổng thể.

```text
Design System v1.6 = CURRENT / REVIEWED
```

Không thấy visual architecture blocker mới.

Nhưng:

```text
Technical Architecture v1.7
= REVIEWED / TARGETED AMENDMENT REQUIRED / NOT FROZEN
```

vì P0-01 và P0-02 là implementation-contract/data-integrity issues thật.

```text
Implementation Gate = NOT YET PASS
Production Ready = NO
```

---

# 23. Final Assessment

v1.7 + Design System v1.6 đã ở mức **rất gần Technical Freeze**.

Điểm đáng mừng là các vấn đề còn lại không yêu cầu thay đổi architecture chính:

```text
Candidate → Submission → Application → Interview → Participant → Report
```

vẫn hợp lý.

Không cần thêm microservice, queue platform mới, state-management framework mới hay module nghiệp vụ mới.

Những việc có leverage cao nhất lúc này là:

1. **remove duplicate semantics**, không thêm features;
2. **make machine registry truly authoritative**, không chỉ token-complete;
3. **enforce adversarial DB invariants**, đặc biệt staged document mutations;
4. **consolidate CURRENT docs**, không dựa vào “amendment ở cuối file thắng đoạn đầu”;
5. sau đó chuyển trọng tâm sang actual migration/RLS/race/React/browser evidence.

Điều kiện tôi khuyến nghị trước Technical Freeze:

> Với mỗi mutable business field, phải trả lời được duy nhất:
>
> **Who may write it → through exactly which command → under what lock/version → which derived state/side effects run → which acceptance test proves it.**

Hiện v1.7 đã đạt phần lớn điều kiện đó, nhưng **Report Status** và **staged document target invariant** vẫn là hai chỗ cần sửa trước tiên.

---

# Appendix A — Fresh Validation Evidence

```text
Full Handover v1.7 + Design v1.6
TOTAL=232
PASS=232
FAIL=0
```

```text
Design System v1.6
TOTAL=63
PASS=63
FAIL=0
```

---

# Appendix B — Source-of-truth files reviewed most deeply

## Full Handover v1.7

- `00_README.md`
- `FINAL_REVIEW_GUIDE.md`
- `02_ROLES_PERMISSIONS_AND_NAVIGATION.md`
- `03_CANDIDATE_FORM_AND_PORTAL.md`
- `06_INTERVIEW_REPORT_HR_AND_INTERVIEWER.md`
- `07_STATUS_AND_BUSINESS_RULES.md`
- `08_DATA_MODEL_AND_FIELD_DICTIONARY.md`
- `10_UI_UX_SPEC.md`
- `11_EMAIL_DOCUMENTS_AND_ACTIVITY_LOG.md`
- `13_ACCEPTANCE_CRITERIA_AND_TEST_CASES.md`
- `16_AI_REVIEW_AND_BUILD_PROMPT.md`
- `37_BACKEND_COMMAND_CONTRACTS.md`
- `39_SECURITY_RLS_MATRIX.md`
- `40_DATABASE_INVARIANTS.md`
- `41_STORAGE_AND_UPLOAD_SECURITY.md`
- `42_PRIVACY_RETENTION_COMPLIANCE.md`
- `43_EMAIL_DELIVERY_SPEC.md`
- `45_PRODUCTION_UAT_GATE.md`
- `46_AUTH_IDENTITY_MODEL.md`
- `48_IDEMPOTENCY_CONCURRENCY_SPEC.md`
- `52_TECHNICAL_GATE_STATUS.md`
- `54_SCHEMA_CONFORMANCE_MATRIX.md`
- `55_COMMAND_COVERAGE_MATRIX.md`
- `59_RLS_POLICY_BLUEPRINT.md`
- `66_DATA_EXPORT_ARCHIVE_PURGE_RUNBOOK.md`
- `67_WEB_SECURITY_BASELINE.md`
- `68_RATE_LIMIT_POLICY.md`
- `70_SEMANTIC_VALIDATION_GATE.md`
- `72_EXTERNAL_REVIEW_V5_RESOLUTION.md`
- `73_DOMAIN_GLOSSARY_AND_CANONICAL_PREDICATES.md`
- `74_TECHNICAL_PRECODE_GATE_V1_7.md`
- `75_RELEASE_EVIDENCE_MATRIX.md`
- `76_DEPENDENCY_BASELINE_POLICY.md`
- `app_spec.yaml`
- `command_registry.yaml`
- `source_registry.yaml`
- `database_schema.sql`
- `tools/validate_package.py`

## Design System v1.6

- `00_README.md`
- `MASTER.md`
- `TOKENS.md`
- `COMPONENTS.md`
- `PATTERNS.md`
- `TABLE_LAYOUT.md`
- `RESPONSIVE.md`
- `ACCESSIBILITY.md`
- `PAGE_OVERRIDES_V1_6.md`
- `DESIGN_REVIEW_CHECKLIST.md`
- `page_component_matrix.csv`
- `component_inventory.csv`
- `tools/validate_design.py`

---

# Appendix C — Suggested next-version acceptance additions

```text
AC-REPORT-STATUS-01
Exactly one trusted command mutates report_status_code.

AC-REPORT-STATUS-02
Outcome-changing report status recalculates Submission in same transaction.

AC-DOC-TARGET-01
Candidate REPLACE requires target logical document to have a current version.

AC-DOC-TARGET-02
Candidate DELETE requires target logical document to have a current version.

AC-DOC-TARGET-03
Historical logical target cannot bypass max-five current-file invariant.

AC-EMAIL-HIST-01
Email History deletion requires correct parent/context authorization.

AC-EMAIL-HIST-02
Email History deletion eligibility is machine-deterministic.

AC-OWNER-LIFE-01
Active/reactivated Application cannot retain an operationally ineligible HR owner.

AC-APP-REACT-PAST-01
Past-only schedule overlaps follow the frozen Reactivation policy and cannot unexpectedly strand a recoverable Application.

AC-PRIV-PUBLISH-01
Privacy Notice current switch never creates an unintended no-current/effective outage.
```
