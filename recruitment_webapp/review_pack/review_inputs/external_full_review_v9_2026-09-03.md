# EIU Recruitment Web App — Full Review Report
## Baseline: Full Handover v1.11 Bundle
### Includes Design System v1.8 + Responsive Prototype v1.7

**Ngày review:** 03/09/2026  
**Source of Truth:** chỉ sử dụng `App_Tuyen_Dung_EIU_Full_Handover_v1.11.zip` và các artifact nằm bên trong bundle này.

**SHA-256 ZIP:** `9cf29eccaaad51d31b6d474b55ee4c30adbe722e98aa2d7d29217809e6f24687`

> Các version trước không được dùng để suy ra trạng thái hiện tại. ECC / Superpowers / Matt Pocock / ByteByteGo chỉ được dùng như review lenses; không override Business/Technical/Design source của EIU.

---

# 1. Executive Summary

v1.11 là một bản rất mạnh về **machine-readable consistency** và đã sửa thực sự phần lớn các điểm của v1.10.

## Fresh validation evidence

Tôi đã chạy trực tiếp validator trên đúng bundle hiện tại:

```text
Full Handover v1.11 + Design v1.8 + Responsive v1.7
TOTAL=400 PASS=400 FAIL=0
```

```text
Design System v1.8
TOTAL=72 PASS=72 FAIL=0
```

```text
Responsive Prototype v1.7 browser QA
TOTAL=54 PASS=54 FAIL=0
```

Các cải thiện đã xác minh:

- bulk Interview Schedule Status đã dùng đúng `interviews.status + interviews.view`;
- `app_spec.yaml` đã ở v1.11 và bỏ legacy Mark-New key;
- Form Session / Upload Reservation expiry là synchronous fail-closed;
- `open_submission` có conditional mutation metadata;
- `save_interviewer_report` dùng machine-readable OR authorization;
- Candidate inactive single/bulk manual NEW/READ đã thống nhất;
- Education optional đúng source;
- NEW Privacy unchecked mặc định;
- Candidate/Submission tách đúng trong prototype;
- Final Decision prototype dùng `decisionUpdatedAt`;
- Current Interview giữ Report Status;
- Phase-1 navigation đã thu gọn;
- CV/staged EDIT prototype đã có evidence;
- source/gate pointers v1.11 nhìn chung đã coherent.

Tuy vậy, manual cross-layer review vẫn tìm được một số edge case **chưa nằm trong 400 checks**.

## Gate recommendation

| Layer | Reviewer recommendation |
|---|---|
| Business Logic Core v1.2 | **Giữ FROZEN** |
| Technical Architecture v1.11 | **Rất gần FROZEN nhưng cần targeted amendment** |
| Design System v1.8 | **CURRENT / không thấy blocker mới** |
| Responsive Prototype v1.7 | **Gần Owner UAT, còn interaction-semantic fixes** |
| Implementation Gate | **NOT YET PASS** |
| Production Ready | **NO** |

---

# 2. Findings Summary

## P0 — nên đóng trước Technical Freeze

| ID | Finding | Layer |
|---|---|---|
| **P0-01** | Interview có thể trở thành operational/resource-blocking với **current Participant đã Inactive** | Identity / lifecycle / scheduling |
| **P0-02** | `delete_unused_submission()` gần như **unreachable trong production** vì mọi Candidate Submit đều tạo production email trace, mà production email lại block delete | Delete lifecycle / email trace |
| **P0-03** | Schedule conflict source/prototype chưa nhất quán: authoritative model block Candidate + Room + Interviewer, nhưng HR Interview page bỏ Candidate và prototype chỉ check Interviewer | Source / prototype / concurrency |

## P1 — nên đóng trước implementation/prototype freeze

| ID | Finding |
|---|---|
| P1-01 | Copy prototype không thực hiện rule “target empty default Round 1 → fill Round 1” |
| P1-02 | `is_structurally_empty_default_round()` chưa tính `copied_from_interview_id` / incoming copy provenance |
| P1-03 | Single `set_submission_manual_status(submission_id)` có thể mutate historical child Submission dù Candidate-level manual UX chốt historical status read-only |
| P1-04 | `critical_control_registry.yaml` dùng permission token `candidate_own_submission`, trong khi command registry dùng `candidate_self` |
| P1-05 | Responsive Browser QA no-overflow matrix chưa cover Interview, Users/Permissions, Candidate Applications và Interviewer Report |
| P1-06 | Prototype Copy/Interview conflict behavior chưa có critical-control/behavioral QA tương xứng |
| P1-07 | Current source chưa có acceptance riêng cho “operationalize Interview phải revalidate all current Participants active” |

## P2 — hardening

- Nên add canonical `all_current_participants_selectable` helper/predicate để dùng chung.
- Nên mở rộng semantic validator từ command/token presence sang **reachability** của lifecycle commands.
- Nên add Copy provenance vào delete/usage definition.
- Nên phân biệt rõ “visual prototype evidence” và “business-interaction evidence” theo route.
- Detailed mobile/tablet design vẫn NOT FROZEN; đây là intentional gate, không phải defect mới.

---

# 3. P0-01 — Interview có thể operationalize với current Participant đã Inactive

Đây là finding kỹ thuật quan trọng nhất của v1.11.

## 3.1 Current rules đúng ở lúc Add/Re-add

`37_BACKEND_COMMAND_CONTRACTS.md`:

```text
add_interview_participant()
→ Active user
```

```text
readd_interview_participant()
→ inactive user rejected
```

SQL `private.validate_participant_lifecycle_and_user()` cũng kiểm tra `app_user.is_active=true` khi Participant được insert hoặc chuyển về `is_current=true`.

Đây là đúng.

---

## 3.2 Current deactivation guard chỉ bảo vệ Interview đang resource-blocking

SQL `private.block_ineligible_hr_owner_lifecycle()` chỉ block Internal User deactivation khi user đang là current Participant của Interview có:

```text
Application active
Interview active
schedule_status != CANCELLED
start/end exist
end_at > now()
```

Điều này có nghĩa user **vẫn được Inactive** nếu Participant hiện nằm trong Interview đang:

- `CANCELLED`;
- Interview `is_active=false`;
- parent Application `is_active=false`;
- chưa có lịch (`start_at/end_at NULL`).

Điều này tự nó hợp lý: những Interview đó chưa operational.

---

## 3.3 Gap xuất hiện khi Interview trở lại operational

Các command:

- `save_interview_schedule()`;
- `change_interview_schedule_status()` với `CANCELLED → operational`;
- `reactivate_interview()`;
- `reactivate_application()`;
- format/time mutation làm một Interview bắt đầu `resource_blocking`;

đều chạy conflict engine Candidate / Room / Interviewer.

Nhưng current contract **không yêu cầu revalidate rằng tất cả current Participants vẫn là Active Internal Users**.

Shared mutation lock order hiện làm:

```text
lock Interview
→ snapshot room + participant set
→ lock resources
→ re-read set
→ check schedule conflicts
→ apply
```

Không có bước:

```text
for each current Participant:
  app_user.is_active must be true
```

---

## 3.4 Concrete failure scenarios

### Scenario A — unscheduled Interview

1. Interview có current Participant X nhưng chưa có start/end.
2. X được Inactive — deactivation guard cho phép vì Interview chưa resource-blocking.
3. HR nhập lịch cho Interview.
4. `save_interview_schedule()` conflict-check passes.
5. Interview trở thành operational nhưng X vẫn inactive.
6. RLS/contextual access lại yêu cầu `app_user.is_active=true`.
7. X không thể truy cập/phỏng vấn/nộp report.

### Scenario B — CANCELLED

1. Interview CANCELLED có current Participant X.
2. X được Inactive.
3. HR đổi CANCELLED → SCHEDULED/CONFIRMED.
4. Schedule conflict có thể pass.
5. Interview operational với một current Participant không thể đăng nhập.

### Scenario C — Application Inactive

1. Application inactive; child Interview vẫn giữ current Participants.
2. X được Inactive vì `access_active=false`.
3. HR Reactivate Application.
4. Reactivate re-check Candidate/Room/Interviewer overlap nhưng không re-check participant account eligibility.
5. Application/Interview active trở lại với current Participant inactive.

---

## 3.5 Vì sao conflict check không đủ

Một inactive Participant vẫn có `app_user_id`, nên Interviewer-resource overlap query vẫn có thể chạy bình thường.

Nhưng:

```text
schedule integrity PASS
!=
participant access eligibility PASS
```

Security source yêu cầu active user cho contextual Interviewer access, nên state mới là internally inconsistent.

---

## Đề nghị

Tạo một canonical guard/helper:

```text
validate_current_participants_operationally_eligible(interview_id)
```

Rule:

```text
Before any mutation that makes an Interview resource_blocking/access-operational:
  every current Participant's app_user must exist and is_active=true.
```

Áp dụng cho:

- Save first schedule;
- reschedule nếu participant state cần revalidation;
- CANCELLED → operational;
- Reactivate Interview;
- Reactivate Application cho mọi non-elapsed child trở lại operational;
- any mutation that transitions from non-resource-blocking → resource-blocking.

Stable error:

```text
CURRENT_PARTICIPANT_INACTIVE_REASSIGN_REQUIRED
```

HR phải remove/replace Participant trước.

### DB / command defense

Không cần trigger trực tiếp trên `interviews` truy toàn bộ graph nếu làm transaction phức tạp. Có thể đặt authoritative check trong trusted commands/RPC và integration tests. Nếu muốn defense-in-depth, dùng deferred validation helper ở transaction boundary.

### Acceptance cần thêm

```text
AC-PART-OPER-01
Unscheduled Interview + inactive current Participant → scheduling rejected.

AC-PART-OPER-02
CANCELLED Interview + inactive current Participant → activation rejected.

AC-PART-OPER-03
Inactive Application with inactive current Participant → Application Reactivate rejected until participant is replaced/removed.

AC-PART-OPER-04
All current Participants active → normal operationalization proceeds to conflict engine.
```

**Severity: P0.**

---

# 4. P0-02 — `delete_unused_submission()` là dead production path theo chính current rules

v1.11 đang có ba source statements đều hợp lệ riêng lẻ nhưng khi kết hợp thì command trở nên gần như không thể dùng.

## 4.1 Candidate Submit luôn tạo HR notification

`submit_candidate_submission()` transaction:

```text
create Submission
→ create privacy acknowledgement
→ materialize CLEAN docs
→ update Candidate cache
→ enqueue HR notification
→ commit
```

Candidate Update cũng enqueue exact-Submission HR notification trong cùng transaction.

---

## 4.2 Production email trace lại block unused Submission delete

Current contract:

```text
retained PRODUCTION Email Outbox/History usage
= downstream business history
= blocks delete_unused_submission()
```

Mục đích là giữ exact `submission_id` relational trace.

Validator thậm chí kiểm:

```text
PASS | Production email trace blocks unused Submission delete
```

---

## 4.3 Consequence

Một **successful production Candidate Submit** ngay từ transaction đầu tiên đã có production Outbox row gắn `submission_id`.

Do đó ngay cả khi:

```text
no Application
no Interview
no business review downstream
```

Submission vẫn đã có:

```text
PRODUCTION email usage
```

và không đạt `delete_unused_submission()`.

Nói cách khác:

> mọi real submitted Submission production gần như lập tức trở thành “used” chỉ vì notification tự động mà chính hệ thống bắt buộc tạo.

---

## 4.4 Nhưng package vẫn advertise hard-delete unused Submission

Current artifacts còn có:

```text
submissions.delete_unused
```

Permission matrix:

```text
Hard-delete unused Submission → HR allowed if permission + view
```

Command coverage:

```text
delete_unused_submission
```

Acceptance/cache logic còn mô tả:

```text
deleting latest unused Submission → fallback Candidate cache
```

Do đó capability được mô tả là Phase-1 production behavior nhưng normal creation path làm nó unreachable.

---

## Đây không chỉ là edge case SQL

Đây là **lifecycle reachability contradiction**:

```text
Create Submission
ALWAYS → create production notification

Production notification
ALWAYS → delete blocker

Therefore
normal created Submission → NEVER unused-delete eligible
```

---

## Cần owner/architecture chọn một hướng

### Option A — khuyến nghị nếu traceability là ưu tiên

Chấp nhận rằng **submitted Submission không hard-delete trong normal production**.

Sau đó:

- remove `submissions.delete_unused` khỏi normal HR capability;
- remove/deprecate `delete_unused_submission()` production command;
- dùng lifecycle/retention purge process thay vì normal hard-delete;
- giữ hard-delete chỉ cho data repair/test/migration nếu cần.

Đây là model sạch nhất với policy “production email exact trace phải giữ”.

### Option B — giữ unused Submission delete

Phải định nghĩa automatic HR notification là **owned lifecycle side effect**, không phải downstream usage blocker cho unused-delete.

Khi delete:

- cleanup Outbox/History theo explicit rule;
- Security Audit giữ deletion evidence;
- chấp nhận mất exact live `submission_id` relational row sau delete hoặc snapshot identity trước delete.

Option này mâu thuẫn với traceability policy hiện tại nên cần owner/Legal/Operations xác nhận.

### Option C — phân loại email blocker tinh hơn

Ví dụ chỉ email/manual downstream hoặc delivered business communication mới block, còn automatic receipt/HR internal notification không block.

Nhưng phải machine-readable bằng `email_type`/classification, không dựa vào prose.

---

## Validator mới

Không chỉ kiểm “email blocks delete”, mà phải kiểm **reachability**:

```text
Given normal create path,
exists at least one production state where delete_unused_submission eligibility can be true.
```

Nếu không, command/permission phải được classified `UNREACHABLE / MAINTENANCE_ONLY / REMOVE`.

**Severity: P0 trước Technical Freeze**, vì package đang quảng bá một trusted production command có precondition bị chính mandatory create side effect vô hiệu hóa.

---

# 5. P0-03 — Schedule conflict semantics chưa đồng nhất giữa source và prototype

Authoritative technical model hiện chốt:

```text
Candidate overlap = BLOCK
Room overlap = BLOCK
Interviewer overlap = BLOCK
```

Trên mọi relevant `resource_blocking` Interview.

## 5.1 Acceptance đúng

`13_ACCEPTANCE_CRITERIA_AND_TEST_CASES.md` có:

```text
AC-21 Interviewer conflict
AC-22 Room conflict
AC-22C Candidate conflict
```

`37_BACKEND_COMMAND_CONTRACTS.md` cũng nói `save_interview_schedule()` block cả Candidate / Room / Interviewer.

---

## 5.2 Current HR Interview Page vẫn thiếu Candidate conflict

`05_HR_INTERVIEW_PAGE.md` section **Conflict validation** chỉ ghi:

```text
check interviewer overlap
check room overlap
skip CANCELLED
skip inactive
```

Không có Candidate overlap trong canonical section đó.

Later Application Reactivate section có nhắc Candidate/Room/Interviewer, nhưng normal Save section vẫn incomplete.

Vì file `05` là CURRENT/NORMATIVE, đây là source inconsistency.

---

## 5.3 Responsive Prototype thực tế chỉ check Interviewer

Current effective `saveRound()` override trong `responsive_prototype/v11-overrides.js` kiểm:

```text
other active non-CANCELLED rounds
same date/time overlap
shared participant
```

Tức chỉ Interviewer conflict.

Nó không check:

```text
same Candidate overlap
same Room overlap
```

Nhưng UI error message lại nói prototype đang block theo business rule.

---

## 5.4 Responsive QA cũng không test Interview conflict matrix

`validate_responsive_v17.py` kiểm rất kỹ Candidate/Report/Privacy, nhưng không test:

- Candidate conflict;
- Room conflict;
- Interviewer conflict on Interview page;
- adjacent boundary `end=start`;
- CANCELLED/inactive exclusion.

Do đó prototype có thể `54/54 PASS` trong khi core Interview scheduling behavior vẫn incomplete.

---

## Đề nghị

### Source

Sửa `05_HR_INTERVIEW_PAGE.md` conflict section thành:

```text
Before commit:
- Candidate overlap → BLOCK
- Room overlap when room is used → BLOCK
- Interviewer overlap → BLOCK
- ignore CANCELLED
- ignore inactive/non-resource-blocking
- interval semantics [start,end); adjacent end=start is allowed
```

### Prototype

Nếu prototype muốn simulate scheduling behavior, implement đủ 3 conflict types.

Nếu không muốn implement backend-like conflict logic trong visual prototype, phải ghi rõ:

```text
Prototype conflict simulation is illustrative only and not business-complete.
```

và không dùng nó làm behavioral PASS evidence.

### Responsive QA

Thêm:

```text
RP-SCH-01 Interviewer overlap blocked
RP-SCH-02 Room overlap blocked
RP-SCH-03 Candidate overlap blocked
RP-SCH-04 adjacent intervals allowed
RP-SCH-05 CANCELLED ignored
```

**Severity: P0 vì conflict prevention là core scheduling invariant và source CURRENT hiện không đồng nhất.**

---

# 6. P1-01 — Copy prototype không tuân thủ empty default Round 1 rule

Frozen contract:

```text
Copy to another Application:
if target auto-created Round 1 is structurally empty
→ fill Round 1
else
→ create next legal round
```

`AC-COPY-03` và `AC-ROUND-EMPTY-01` cùng xác nhận rule này.

## Prototype behavior

Current `saveRound(type, srcId)` khi Copy sang target Application luôn làm gần như:

```text
no = max(target.round_no) + 1
push new round
```

Do đó nếu target có:

```text
Round 1 = auto-created + empty
```

prototype vẫn tạo:

```text
Round 2
```

và để Round 1 rỗng.

Đây là trực tiếp trái source.

## Ngoài ra copy date chưa thật sự copy source

`roundModal()` copy:

- start/end từ source;
- location từ source;
- participants từ selected option;
- Demo Topic blank;

nhưng Date đang dùng một fixed demo date thay vì source date.

Vì source nói copy schedule/logistics rồi HR có thể chỉnh, initial copy context nên phản ánh source logistics đầy đủ hơn.

## Đề nghị

Prototype:

```text
if target Round1 satisfies same structural-empty predicate
  mutate/fill target Round1
else
  create next round
```

Thêm QA:

```text
RP-COPY-01 target empty Round1 → still one Round1, now filled
RP-COPY-02 used target Round1 → new legal next round
RP-COPY-03 Demo Topic blank
RP-COPY-04 source schedule/logistics prefills consistently
```

---

# 7. P1-02 — `is_structurally_empty_default_round()` chưa tính Copy provenance

Current helper kiểm rất nhiều usage:

- round_no=1;
- schedule fields empty;
- initial statuses;
- no note;
- no participants;
- no documents;
- no email Outbox/History.

Nhưng không kiểm:

```text
copied_from_interview_id IS NULL
```

và cũng không kiểm incoming references:

```text
NOT EXISTS (
  SELECT 1 FROM interviews x
  WHERE x.copied_from_interview_id = i.interview_id
)
```

Trong schema:

```text
copied_from_interview_id REFERENCES interviews ON DELETE RESTRICT
```

## Consequence

Một Round được coi “structurally empty” có thể vẫn là một provenance node.

Nếu round đó có incoming copy reference, delete flow có thể:

```text
helper = true
→ attempt hard delete
→ raw FK RESTRICT failure
```

thay vì controlled “used/history” decision.

Nếu round có `copied_from_interview_id` nhưng copied data vẫn default/empty, helper có thể delete provenance metadata mà business có thể muốn giữ.

## Đề nghị

Chốt một trong hai:

### Provenance counts as business usage — khuyến nghị

Add to helper:

```text
copied_from_interview_id IS NULL
AND no incoming copied_from reference
```

### Provenance does not count

Thì FK/reference lifecycle phải cho phép controlled unlink (`SET NULL`) và audit trước delete.

Current `ON DELETE RESTRICT` cho thấy design hiện nghiêng về **provenance counts as usage**.

---

# 8. P1-03 — Single manual Submission command chưa enforce latest-only UX

Current responsive/design amendment chốt:

```text
Historical child Submission status is read-only in Candidate-level bulk/manual UX.
```

Prototype cũng không render clickable status cho historical rows.

Bulk command đúng:

```text
Candidate selection
→ deterministic latest Submission only
```

Nhưng single command vẫn là:

```text
set_submission_manual_status(submission_id)
```

và backend chỉ kiểm:

- target status NEW/READ;
- no active Application.

Nó không kiểm target đó là deterministic latest Submission.

## Risk

Một authorized HR có thể gửi crafted request với `submission_id` của historical child và đổi NEW/READ dù UI chốt read-only.

Đây không phải privilege escalation — HR có `submissions.status` — nhưng là **business-state bypass qua hidden API path**.

## Cần chọn rõ

### Nếu historical status thật sự immutable từ Candidate-level workflow

Single command nên nhận:

```text
candidate_id
expected_latest_submission_id
expected_version
```

hoặc re-check target Submission = deterministic latest.

### Nếu exact historical status mutation là intentionally supported backend capability

Phải ghi rõ đây là privileged/non-UI operation; không gọi historical row “read-only” theo nghĩa system-wide.

Current package chưa nói có use case nào cần mutation này, nên tôi nghiêng về latest-only guard.

---

# 9. P1-04 — Critical Control Registry dùng permission vocabulary khác Command Registry

`critical_control_registry.yaml`:

```text
CANDIDATE-FORM-SUBMIT
permission: candidate_own_submission
```

Trong `command_registry.yaml`, Candidate commands dùng:

```text
permission: candidate_self
```

Hai token đều không phải granular HR permission, nhưng machine-readable registries đang dùng hai vocabulary khác nhau cho cùng authorization concept.

## Risk

Validator hiện chưa check:

```text
critical control permission token
↔ command authorization token
```

Agent/tool có thể hiểu chúng là hai policies khác nhau.

## Đề nghị

Dùng một canonical token:

```text
candidate_self
```

hoặc tạo authorization vocabulary registry:

```yaml
candidate_self:
  aliases: []
  meaning: authenticated active Candidate owns target/session
```

Không để ad-hoc synonym trong machine contracts.

---

# 10. P1-05 — Responsive no-overflow evidence chưa cover toàn core route matrix

Current browser QA no-overflow test chạy các viewport:

```text
360
390
430
768
1024
1280
```

nhưng chỉ trên 3 routes:

```text
admin/applications
admin/hr-report
candidate/candidate-form
```

Chưa cover page-level overflow cho:

- `admin/interview`;
- `admin/permissions`;
- `candidate/candidate-applications`;
- `interviewer/interviewer-report`;
- Catalogs nếu nằm Phase 1 UAT.

## Vì sao đáng bổ sung

Interview là page có wide table/complex drawer/status/copy schedule; Users & Permissions có security-sensitive columns; Candidate Applications là một trong hai core Candidate routes.

Package đang ghi:

```text
Responsive Prototype v1.7 READY FOR OWNER VISUAL UAT
```

Không cần automated-test mọi pixel, nhưng evidence matrix nên cover mọi core persona route ít nhất smoke/overflow.

## Đề nghị

Thêm route × breakpoint smoke matrix, tối thiểu:

```text
applications
interview
hr-report
permissions
candidate-form
candidate-applications
interviewer-report
```

Ở 375/430/768/1280 hoặc current chosen matrix.

---

# 11. P1-06 — Copy/Scheduling chưa nằm trong current Responsive behavioral QA

Responsive README nói Copy đã từng “re-tested” ở retained older audit, nhưng current v1.7 executable QA không test:

- Copy same Application;
- Copy different Application;
- empty default Round1 behavior;
- Candidate conflict;
- Room conflict;
- Interviewer conflict;
- cancellation/inactive exclusions.

Do v1.7 hiện được dùng làm Owner Visual UAT artifact, các flow này nên có ít nhất representative behavioral cases.

Không cần biến static prototype thành full backend simulator; chỉ cần hoặc:

1. implement accurate prototype transitions; hoặc
2. classify those controls `visual_only / backend_semantics_not_simulated` và không coi chúng là business QA evidence.

---

# 12. P1-07 — Thiếu Acceptance cho participant eligibility lúc Operationalize

Current Acceptance có:

```text
AC-PART-ACTIVE-01
re-add inactive user rejected;
deactivation blocked while already current participant on non-elapsed resource-blocking Interview.
```

Nhưng chưa test dormant → operational transition.

Đây chính là lý do P0-01 lọt qua validators.

Nên thêm AC-PART-OPER-01…04 như section P0-01.

---

# 13. Design System v1.8 Review

Fresh validator:

```text
72/72 PASS
```

Manual review vòng này không phát hiện Design System regression đáng kể.

Các phần vẫn tốt:

- Application Inbox 1560px;
- Interview 1480px;
- HR Report 1610px;
- Drawer formula nhất quán;
- Candidate Edit privacy;
- exact SubmissionSelector;
- permission-display persona separation;
- 16px operational text;
- 44px touch target goal;
- 200% zoom / 400% reflow requirements;
- sticky context/focus;
- status menu anchored/focus-restoring;
- Phase-1 nav rules.

Các finding của vòng này chủ yếu nằm ở **technical lifecycle + responsive prototype interaction semantics**, không phải visual design token/component architecture.

---

# 14. Responsive Prototype v1.7 Review

Fresh browser evidence:

```text
54/54 PASS
```

Điểm tốt đã xác minh:

- Candidate/Submission lifecycle tách đúng;
- inactive Candidate không overwrite Submission status;
- historical Submission non-clickable trong UI;
- single/bulk NEW/READ parity;
- aggregate Report không có generic Delete;
- Report Status nằm Current Interview;
- Final Decision qualitative edit không đổi source;
- Education optional;
- Privacy unchecked mặc định;
- CV required;
- staged EDIT Replace/Delete/Cancel;
- Phase-1 navigation sạch;
- no console errors trong tested flows.

## Nhưng status nên giữ

```text
READY FOR OWNER VISUAL UAT
NOT FROZEN
```

và **chưa sign-off** các scheduling/copy behaviors trước khi đóng P0-03 + P1-01/P1-06.

---

# 15. Validator Improvements đề nghị cho v1.12

Current 400 checks đã mạnh. Những checks mới có leverage cao nhất:

## V-01 — Operational participant eligibility

Executable/contract check:

```text
non-resource-blocking Interview with inactive current Participant
→ attempt schedule/reactivate/uncancel
→ FAIL
```

---

## V-02 — Lifecycle command reachability

For each Phase-1 production command:

```text
there exists at least one normal reachable state satisfying its preconditions
```

Sẽ bắt `delete_unused_submission()` dead path.

---

## V-03 — Schedule conflict source consistency

Check `05_HR_INTERVIEW_PAGE.md` canonical conflict section contains:

```text
Candidate
Room
Interviewer
[start,end)
CANCELLED/inactive exclusions
```

---

## V-04 — Prototype schedule conflict

If prototype claims conflict simulation:

```text
Candidate / Room / Interviewer representative tests
```

Nếu không thì artifact phải explicitly label simulation incomplete.

---

## V-05 — Copy semantics

```text
target empty default Round1 → fill Round1
used target → create next round
Demo Topic blank
```

---

## V-06 — Empty Round provenance

`is_structurally_empty_default_round` must account for copy provenance according to frozen policy.

---

## V-07 — Critical-control authorization vocabulary

```text
critical control permission/context token
must resolve to command authorization vocabulary
```

---

## V-08 — Responsive route coverage

Every frozen Phase-1 core route appears in at least one responsive smoke/overflow test.

---

# 16. Recommended Fix Order

## Batch 1 — Technical Freeze blockers

1. Add operational participant Active-user revalidation to every Interview operationalization path.
2. Resolve `delete_unused_submission()` reachability vs mandatory production email trace.
3. Add Candidate conflict to canonical HR Interview source section.
4. Either implement Candidate+Room+Interviewer conflict simulation in prototype or explicitly stop claiming business-complete schedule validation.

## Batch 2 — Copy/delete semantics

5. Fix Copy-to-other-Application empty Round1 behavior in prototype.
6. Freeze Copy provenance as usage and update `is_structurally_empty_default_round()` accordingly.
7. Add Copy behavioral QA.

## Batch 3 — API/machine consistency

8. Decide/enforce latest-only single manual Submission status.
9. Normalize `candidate_own_submission` vs `candidate_self` authorization token.
10. Add dormant-participant operationalization Acceptance cases.

## Batch 4 — UAT evidence

11. Expand responsive smoke/overflow routes.
12. Add Interview scheduling/copy click-path cases.
13. Re-run package/design/responsive validators.
14. Then proceed to Owner Visual UAT + Technical Freeze Review.

---

# 17. Proposed Gate Status

```text
Business Logic Core v1.2
= FROZEN
```

Không có finding nào yêu cầu redesign core recruitment workflow.

```text
Design System v1.8
= CURRENT / REVIEWED
```

Không thấy blocker Design mới.

```text
Responsive Prototype v1.7
= CURRENT / READY FOR LIMITED VISUAL UAT / NOT FROZEN
```

Nên đóng scheduling/copy interaction findings trước final Owner sign-off.

```text
Technical Architecture v1.11
= REVIEWED / TARGETED AMENDMENT REQUIRED / NOT FROZEN
```

```text
Implementation Gate
= NOT YET PASS
```

```text
Production Ready
= NO
```

---

# 18. Final Assessment

v1.11 đã đạt chất lượng rất cao cho một pre-code handover. 400 automated checks cho thấy project đã chuyển từ “tài liệu mô tả” sang một bộ source có khả năng tự kiểm consistency đáng kể.

Những lỗi còn lại hiện có đặc điểm khác các vòng đầu:

- không phải thiếu module lớn;
- không phải thiết kế entity sai;
- không phải RLS/auth architecture cần viết lại;
- chủ yếu là **reachability và lifecycle transition edge cases** mà token-based validator khó phát hiện.

Ba boundary cần khóa trước Technical Freeze:

```text
Current Participant
→ Active while Interview becomes operational
```

```text
Mandatory Submit side effects
→ must not make an advertised delete command impossible by construction
```

```text
Schedule conflict
→ same Candidate + Room + Interviewer semantics in source, command, acceptance and prototype
```

Sau khi đóng ba nhóm này, tôi đánh giá v1.11/v1.12 có thể chuyển trọng tâm gần như hoàn toàn sang **actual implementation evidence**: migrations, executable RLS, race tests, React tests, browser QA, backup/restore và deployment rehearsal.

---

# Appendix A — Fresh Evidence

```text
Full Handover v1.11: 400/400 PASS
Design System v1.8: 72/72 PASS
Responsive Prototype v1.7: 54/54 PASS
Command Registry: 58/58 unique command names
```

---

# Appendix B — Suggested Acceptance Additions

```text
AC-PART-OPER-01
Unscheduled Interview with inactive current Participant cannot be scheduled.

AC-PART-OPER-02
CANCELLED Interview with inactive current Participant cannot become operational.

AC-PART-OPER-03
Inactive Application with inactive current Participant cannot reactivate into an operational Interview.

AC-PART-OPER-04
Active current Participants pass eligibility then normal Candidate/Room/Interviewer conflict checks run.

AC-SUB-DEL-REACH-01
Unused-Submission delete policy has at least one reachable normal production state, or command is classified maintenance-only/removed.

AC-SCH-SRC-01
Candidate, Room and Interviewer overlaps are all blocking in normal schedule Save.

AC-RP-SCH-01
Responsive schedule simulation blocks Interviewer overlap.

AC-RP-SCH-02
Responsive schedule simulation blocks Room overlap.

AC-RP-SCH-03
Responsive schedule simulation blocks same-Candidate overlap.

AC-RP-COPY-01
Copy to another Application fills structurally empty target Round1; otherwise creates next legal round.

AC-ROUND-PROV-01
A Round with copy provenance/incoming copy reference follows the frozen used-vs-empty policy and never fails as an unexpected raw FK delete error.
```
