# EIU Recruitment Web App — Full Review Report
## Baseline: Full Handover v1.12 Bundle
### Includes Design System v1.8 + Responsive Prototype v1.8

**Ngày review:** 03/09/2026  
**Source of truth của vòng này:** chỉ sử dụng `App_Tuyen_Dung_EIU_Full_Handover_v1.12.zip`.

**SHA-256 ZIP:** `2c4f0973bc5927ebd90f7d2204819051d765eff5b1ee7ad52d4108138da73d64`

> Không sử dụng kết luận của v1.11 để suy ra trạng thái v1.12 nếu chưa xác minh lại. Các repo ECC / Superpowers / Matt Pocock / ByteByteGo chỉ được dùng như review lenses; chúng không override nguồn EIU.

---

# 1. Executive Summary

v1.12 đã sửa đúng phần lớn các vấn đề được package tự liệt kê trong `CHANGELOG_V1_12.md`: operational participant guard, classification của `delete_unused_submission`, Candidate/Room/Interviewer conflict, Copy Round1/provenance, latest-only manual Submission status và responsive schedule/copy alignment.

## Fresh executable evidence

Tôi đã chạy lại trực tiếp từ bundle đã giải nén:

```text
Full Handover validator
TOTAL=424 PASS=424 FAIL=0
```

```text
Design System validator
TOTAL=72 PASS=72 FAIL=0
```

```text
Responsive Prototype v1.8 Chromium QA
TOTAL=93 PASS=93 FAIL=0
```

```text
Manifest verification
checks=499 failures=0
```

Đây là mức automated validation rất tốt.

Tuy nhiên manual semantic/adversarial review vẫn tìm thấy một số lỗi mà 424 + 72 + 93 checks chưa bắt. Ba lỗi quan trọng nhất đều có thể tạo khác biệt giữa behavior được frozen và implementation/UAT thực tế.

## Gate recommendation

| Layer | Reviewer assessment |
|---|---|
| Business Logic Core v1.2 | **Giữ FROZEN** |
| Technical Architecture v1.12 | **Rất gần FROZEN — cần targeted amendment** |
| Design System v1.8 | **CURRENT — nhìn chung ổn** |
| Responsive Prototype v1.8 | **REVIEW REQUIRED trước Owner UAT sign-off** |
| Implementation Gate | **NOT YET PASS** |
| Production Ready | **NO** |

---

# 2. Findings Summary

## P0 — nên đóng trước Technical Freeze / Owner Visual UAT

| ID | Finding | Layer |
|---|---|---|
| **P0-01** | Education được freeze là optional/no required fields nhưng physical SQL bắt buộc cả 4 field khi row tồn tại | Validation ↔ DB schema |
| **P0-02** | Responsive Prototype vẫn tạo/update Application bằng Candidate-only selector, không phải exact `SubmissionSelector` | Prototype ↔ domain identity |
| **P0-03** | Create/Copy Interview trong prototype có thể operationalize Participant đã Inactive; current active-user invariant chưa được thực thi end-to-end | Prototype / schedule lifecycle |

## P1 — nên đóng trước implementation freeze

| ID | Finding |
|---|---|
| **P1-01** | SQL helper `private.set_submission_manual_status(submission_id, ...)` không tự enforce latest-only, trái command-level invariant |
| **P1-02** | `set_internal_user_active` machine registry/primary command section chưa thể hiện đầy đủ future-participant deactivation guard |
| **P1-03** | Current Design README vẫn ghi Responsive Prototype v1.6 trong status, dù current bundle là v1.8 |
| **P1-04** | Validator/manifest-verifier labels vẫn mang v1.11/v1.7 dù conditions/hash checks thực tế dùng v1.12/v1.8 |
| **P1-05** | Responsive QA chưa test exact SubmissionSelector và inactive-participant Create/Copy, nên current 93/93 có false-green coverage gap |

## P2 — cleanup / maintainability

- `37_BACKEND_COMMAND_CONTRACTS.md` vẫn còn generic wording `Bulk Mark New: all-or-nothing` dù current batch writer là NEW/READ.
- `FINAL_REVIEW_GUIDE.md` là current entrypoint nhưng không nằm trong `source_registry.documents`; validator governance nên xác định rõ status của entrypoint này.
- `verify_manifests.py` hard-code display labels `Review Pack v1.11` / `Responsive Prototype v1.7`; hash verification vẫn đúng nhưng evidence text gây nhiễu.
- Responsive prototype giữ nhiều historical JS/CSS override layers; trước production implementation nên dùng prototype như reference behavior, không copy nguyên kiến trúc override chain.

---

# 3. P0-01 — Education Optional Contract mâu thuẫn Physical SQL

Đây là lỗi cross-layer rõ ràng.

## Business source

`03_CANDIDATE_FORM_AND_PORTAL.md` ghi:

```text
Phase 1 hiện không bắt buộc tối thiểu 1 dòng Education
và không đánh dấu 4 field Education là required.
```

Bốn field là:

- Thời gian;
- Học vấn;
- Chuyên ngành;
- Trường.

## Machine Validation Contract

`validation_contract.yaml`:

```yaml
education_rows:
  max_items: 20
  min_items: 0
  required_fields: []
```

Acceptance cũng xác nhận:

```text
AC-PROT-EDU-01:
current Phase 1 allows zero rows and does not mark the four Education fields required.
```

Responsive Prototype v1.8 cũng đúng ở layer UI: các Education inputs không có `required` và có thể để trống.

## Nhưng physical SQL lại bắt buộc

`database_schema.sql`:

```sql
create table public.submission_education (
  ...
  period_text text not null,
  qualification_id uuid not null,
  major text not null,
  institution text not null
);
```

Điều này có nghĩa:

```text
UI / DTO hợp lệ:
Education row có một vài field để trống

→ SQL:
NOT NULL violation
```

Đặc biệt `qualification_id` không thể biểu diễn option prototype:

```text
"Chọn nếu có / Select if applicable"
```

nếu một Education row được lưu.

## Vì sao đây không chỉ là UI issue

Current source cố ý freeze:

```text
required_fields: []
```

nên database không được tự thêm requiredness.

Nếu ý định thật sự là:

> Education row hoàn toàn trống được bỏ qua, nhưng khi đã tạo row thì 4 field bắt buộc,

thì source hiện **không nói vậy** và `required_fields: []` phải được sửa trước.

## Khuyến nghị

Theo source hiện tại, sửa SQL để cho phép nullable:

```sql
period_text text,
qualification_id uuid references ...,
major text,
institution text
```

và normalize:

```text
completely blank row → optionally omitted from persistence
partially filled row → allowed according to current Validation Contract
```

Nếu owner muốn “all-or-none per Education row”, hãy đổi Validation Contract/Acceptance/Prototype đồng thời; không nên để DB tự quyết định.

## Acceptance nên thêm

```text
AC-EDU-DB-01
Zero Education rows → accepted.

AC-EDU-DB-02
Partially populated Education row permitted by Validation Contract → persistence succeeds.

AC-EDU-DB-03
DB requiredness exactly matches validation_contract.yaml.
```

**Severity: P0 — valid frontend/DTO input có thể fail tại DB.**

---

# 4. P0-02 — Responsive Prototype vẫn dùng Candidate-only selector để tạo Application

Đây là regression/coverage gap quan trọng vì Application identity của hệ thống đã freeze theo **exact Submission** từ rất sớm.

## Current Business/Design source

`10_UI_UX_SPEC.md`:

```text
Ứng tuyển uses a dedicated SubmissionSelector,
never a Candidate-only selector.
```

Design System v1.8:

```text
SubmissionSelector
→ show Candidate Name
→ verified Email
→ submitted date
→ Submission status
→ return submission_id
```

`app_spec.yaml`:

```yaml
application:
  selector_entity: SUBMISSION
  backend_never_guesses_latest_submission: true
```

Durable identity:

```text
submission_id + unit_id + department_team_id + position_id
```

## Effective Responsive Prototype v1.8

`assignApplicationModal()` vẫn chỉ có:

```text
Ứng viên *
Nguyễn Văn A — nguyenvana@gmail.com
Trần Thị B — tranthib@gmail.com
```

Không có:

- submitted date;
- Submission status;
- exact Submission identity.

Duplicate warning trong modal còn ghi:

```text
Candidate + Khoa/Phòng + Ngành/Tổ + Vị trí
```

thay vì:

```text
Submission + Unit + Team + Position
```

Tôi đã render effective prototype và xác nhận modal hiện tại thực sự hiển thị Candidate-only options; không có override v1.8 thay thế function này.

## Failure scenario

Candidate A có:

```text
Submission S1 — older
Submission S2 — latest
```

HR muốn tạo Application từ S1 hoặc cần xác định chính xác S2.

Prototype chỉ cho chọn:

```text
Candidate A
```

→ user không thể biết Application sẽ gắn Submission nào.

Nếu developer implement theo prototype, họ buộc phải:

```text
auto-pick latest Submission
```

trái rule:

```text
backend_never_guesses_latest_submission = true
```

## Khuyến nghị

Thay modal bằng đúng `SubmissionSelector`:

```text
Nguyễn Văn A
nguyenvana@gmail.com
Submitted: 03/09/2026 09:15
Status: READ
```

value phải là:

```text
submission_id
```

Duplicate warning:

```text
Submission + Unit + Team + Position already exists
→ Update/Reactivate durable Application
```

## Validator / QA cần thêm

```text
AC-PROTO-SUBSEL-01
Application create/update modal returns exact submission_id.

AC-PROTO-SUBSEL-02
Two Submissions of same Candidate render as two distinct selectable options.

AC-PROTO-SUBSEL-03
No production-intent Application action uses Candidate-only selector.
```

**Severity: P0 — prototype hiện vi phạm entity identity frozen và có thể dẫn implementation chọn sai Submission.**

---

# 5. P0-03 — Active Participant Guard chưa được thực thi cho Create/Copy Prototype

v1.12 tuyên bố đây là một trong các closure chính:

```text
every current Participant must resolve to an Active Internal User
before scheduling/uncancelling/reactivation makes Interview resource-blocking
```

Stable error:

```text
CURRENT_PARTICIPANT_INACTIVE_REASSIGN_REQUIRED
```

## Source contract

`05_HR_INTERVIEW_PAGE.md` ghi rõ:

> Trước bất kỳ mutation nào làm Interview từ dormant/non-resource-blocking thành operational/resource-blocking, server phải revalidate mọi current Participant vẫn là Active Internal User.

`37_BACKEND_COMMAND_CONTRACTS.md` shared lock order cũng yêu cầu participant active before resource locks/conflict recheck.

## Prototype v1.8 hiện chỉ kiểm ở Edit path

`responsive-v18.js`:

```js
if(type==='editRound' && !allCurrentParticipantsActiveV18(...)) {
  ... CURRENT_PARTICIPANT_INACTIVE_REASSIGN_REQUIRED
  return;
}
```

Không có equivalent guard cho:

```text
createRound
copyRound
```

Trong khi cả hai path có thể tạo một resource-blocking Interview với participant list mới.

## Tôi đã chạy adversarial browser case

Tôi đặt:

```js
state.users.u1.active = false
```

sau đó Create Interview với participant list chứa `u1`.

Kết quả thực tế:

```text
rounds before = 1
rounds after  = 2
conflict/error = none
```

Tức prototype **đã tạo thành công Interview với inactive current Participant**.

## Copy còn rủi ro hơn

Copy có participant prefill từ source Interview.

Một source historical Interview có thể chứa user đã Inactive sau đó.

Nếu Copy không revalidate:

```text
historical inactive interviewer
→ copied as current Participant
→ target Interview becomes operational
→ participant cannot login/contextually access report
```

## Khuyến nghị

`saveRound()` phải validate selected participant list cho **mọi path làm target resource-blocking**:

```js
const inactive = parts.filter(uid => !state.users[uid] || state.users[uid].active === false)
if (inactive.length) block CURRENT_PARTICIPANT_INACTIVE_REASSIGN_REQUIRED
```

Không chỉ `editRound`.

Production command contract nên nói explicit trong `copy_interview_schedule()`:

```text
copied/prefilled Participants are revalidated Active before commit;
copy may not resurrect an inactive historical Participant as current.
```

## QA cần thêm

```text
Create + inactive selected Participant → BLOCK
Copy + inactive source/prefilled Participant → BLOCK
Edit + inactive current Participant → BLOCK
Reactivate + inactive current Participant → BLOCK
CANCELLED→operational + inactive current Participant → BLOCK
```

Current Responsive QA 93/93 chỉ test conflict Candidate/Room/Interviewer, chưa test inactive Participant on Create/Copy.

**Severity: P0 — current v1.12 closure claim chưa đúng trong executable visual-UAT artifact.**

---

# 6. P1-01 — SQL manual-status helper không tự enforce latest-only

Current frozen rule:

```text
Single manual Submission status action is Candidate-level.
Backend resolves deterministic latest Submission.
Historical Submission status is read-only.
```

`command_registry.yaml` cũng đúng:

```yaml
set_submission_manual_status:
  input_entity: candidate
  side_effects:
    - resolve_and_lock_deterministic_latest_submission
    - verify_expected_latest_submission_id
```

Nhưng starter SQL lại có:

```sql
private.set_submission_manual_status(
  p_submission_id uuid,
  p_status text
)
```

Function chỉ kiểm:

- status ∈ NEW/READ;
- Submission tồn tại;
- không có active Application.

Nó **không kiểm Submission đó là deterministic latest của Candidate**.

## Risk

Một implementation server-side dùng helper này trực tiếp với historical `submission_id` có thể tạo:

```text
historical Submission READ → NEW
```

trái Phase-1 UI/domain rule.

Private schema giảm attack surface, nhưng không loại implementation-error risk — đặc biệt vì helper có cùng tên với trusted command trong docs.

## Khuyến nghị

Một trong hai:

### A — tốt nhất

Đổi helper thành Candidate-level:

```text
private.set_latest_submission_manual_status(
  candidate_id,
  expected_latest_submission_id,
  expected_version,
  status
)
```

và resolve/lock latest trong function.

### B

Rename helper hiện tại để thể hiện precondition:

```text
private.write_submission_manual_status_after_latest_validation(...)
```

và thêm explicit `assert_is_latest_submission()`.

Validator hiện check latest-only ở docs/registry nhưng chưa check SQL helper semantics.

**Severity: P1-high / defense-in-depth before freeze.**

---

# 7. P1-02 — Internal User lifecycle machine contract chưa exhaustive

Current source có rule:

```text
Normal Internal User deactivation is blocked when target user is a current Participant
on a non-elapsed resource_blocking Interview.
```

Stable error:

```text
FUTURE_INTERVIEW_PARTICIPANT_REASSIGN_REQUIRED
```

SQL `block_ineligible_hr_owner_lifecycle()` đã implement guard này.

Nhưng `command_registry.yaml` entry:

```yaml
set_internal_user_active:
  side_effects:
    - block_active_application_owner_without_reassignment
    - security_audit
```

không ghi:

```text
block_future_current_participant_without_reassignment
```

`55_COMMAND_COVERAGE_MATRIX.md` row cũng chỉ nhấn mạnh HR-target/Root lifecycle.

Trong khi v1.7+ architecture dùng Registry như machine-readable contract, side-effect omission có thể làm coding agent bỏ qua một guard đang có ở prose/SQL.

## Sửa

Registry:

```yaml
side_effects:
  - block_active_application_owner_without_reassignment
  - block_nonelapsed_resource_blocking_current_participant_without_reassignment
  - security_audit

guarantees:
  - active_user_lifecycle_cannot_strand_future_current_participant
```

Coverage matrix cũng nên ghi cả owner + participant lifecycle guards.

**Severity: P1.**

---

# 8. P1-03 — Design System README còn stale Responsive Prototype status

`design_system/RESPONSIVE.md` đã đúng:

```text
Responsive Prototype v1.8 bundled with Full Handover v1.12
```

Nhưng `design_system/00_README.md` phần Status vẫn ghi:

```text
Responsive Prototype: v1.6 alignment-corrected
```

Trong cùng file phía dưới lại nói:

```text
Responsive Prototype v1.8 is the executable reference
```

Đây là current-source self-contradiction nhỏ.

## Sửa

Status block:

```text
Responsive Prototype v1.8 — READY FOR OWNER VISUAL UAT / NOT FROZEN
```

Design validator hiện chỉ kiểm v1.8 authority trong `RESPONSIVE.md`, nên không bắt stale block trong `00_README.md`.

**Severity: P1 source governance.**

---

# 9. P1-04 — Validator evidence labels vẫn mang version cũ

Actual conditions/hashes đều đang kiểm current data, nhưng tên check vẫn stale.

## Package validator

`tools/validate_package.py`:

```python
c('Technical version 1.11',
  prod.document_version == '1.12' ...)
```

Output vì vậy ghi:

```text
PASS | Technical version 1.11
```

trong package v1.12.

Các label khác:

```text
All-in-One includes current v1.11 alignment
All-in-One generated v1.11
CURRENT/NORMATIVE baseline assertions are v1.11 coherent
```

nhưng predicates thực tế đang target v1.12.

## Design validator

Output:

```text
PASS | Responsive prototype v1.7 authority
```

trong khi expression tìm `Responsive Prototype v1.8`.

## Manifest verifier

`verify_manifests.py` hard-code display labels:

```text
App ... Review Pack v1.11
Responsive Prototype v1.7
```

Dù manifest title thực tế đã là v1.12/v1.8 và hash verification PASS.

## Impact

Không làm hash/check sai, nhưng:

- evidence report gây nhầm cho reviewer;
- machine-generated proof không self-consistent;
- có thể làm CI parser hoặc release reviewer hiểu sai baseline.

## Sửa

Không hard-code version text trong check labels.

Derive từ:

```text
source_registry.yaml
app_spec.yaml
responsive VERSION.md
MANIFEST title
```

**Severity: P1 evidence quality.**

---

# 10. P1-05 — Current QA coverage chưa test hai P0 prototype paths

Responsive QA v1.8 có 93 tests và đã kiểm rất tốt:

- Phase-1 nav;
- Candidate/Submission separation;
- latest manual status;
- aggregate report delete;
- Report Status ownership;
- decisionUpdatedAt;
- Education optionality;
- CV/staged document behavior;
- Candidate/Room/Interviewer conflict;
- Copy empty Round1;
- responsive overflow.

Nhưng nó không test:

### A. Exact SubmissionSelector

Không mở `assignApplicationModal()` và không assert:

```text
option identity = submission_id
```

nên P0-02 pass lọt.

### B. Inactive Participant on Create/Copy

QA helper conflict test chỉ kiểm Candidate/Room/Interviewer time overlap.

Không inject:

```text
state.users[u].active = false
```

rồi Create/Copy.

nên P0-03 pass lọt.

## Thêm QA

```text
Application create modal:
- same Candidate, 2 Submissions → 2 choices
- choice returns exact submission_id

Schedule:
- Create with inactive participant → blocked
- Copy with inactive participant → blocked
```

**Severity: P1 — false-green test coverage.**

---

# 11. P2 — Documentation / maintainability cleanup

## 11.1 Legacy bulk wording

`37_BACKEND_COMMAND_CONTRACTS.md` generic section vẫn có:

```text
Bulk Mark New: all-or-nothing
```

Current actual batch writer là:

```text
bulk_set_latest_submission_manual_status
→ NEW / READ
```

Đổi thành:

```text
Bulk latest Submission manual status NEW/READ: ALL_OR_NOTHING.
```

## 11.2 FINAL_REVIEW_GUIDE classification

`FINAL_REVIEW_GUIDE.md` là current entrypoint nhưng không nằm trong `source_registry.documents`.

Không nhất thiết phải normative, nhưng registry nên explicit:

```yaml
file: FINAL_REVIEW_GUIDE.md
status: CURRENT
normative: false
kind: ENTRYPOINT_GUIDE
```

để semantic version scans có coverage rõ.

## 11.3 Prototype override chain

Prototype effective behavior hiện được tạo từ:

```text
app.js
→ v11-overrides.js
→ responsive-v12.js
→ ...
→ responsive-v18.js
```

Đây chấp nhận được cho review artifact, nhưng **không nên copy sang production React architecture**.

Production implementation phải derive fresh components/state from current Handover + Design System.

---

# 12. What v1.12 has fixed correctly

Manual review xác nhận các cải thiện hiện tại sau là có thật trong source/SQL/prototype:

- Candidate lifecycle và Submission workflow đã tách.
- Latest Submission parent summary/bulk semantics đã rõ.
- Legacy bulk Mark-New command đã remove khỏi registry.
- Report Status có một trusted writer.
- Final Decision Source dùng decision-specific timestamp.
- Candidate CV required + staged ADD/REPLACE/DELETE + Cancel semantics đã được prototype hóa.
- Internal email DB exact-domain regex đã được cải thiện.
- Inactive master new-selection DB guards đã được bổ sung.
- Form Session ownership guard đã có.
- Published Privacy Notice DELETE đã bị block.
- Participant lifecycle DB check đã có.
- Candidate verified email immutability guard đã có.
- Application durable identity vẫn global unique.
- Resource predicates `access_active/current_round/resource_blocking/reactivation_conflict_relevant` nhìn chung đã coherent.
- Submission normal production hard-delete đã chuyển MAINTENANCE_ONLY, phù hợp retained production email trace.
- Copy provenance được tính là usage trong structural-empty helper.
- Responsive v1.8 đã kiểm Candidate + Room + Interviewer conflict và empty Round1 Copy path.

Không cần redesign architecture.

---

# 13. Validator Improvements Recommended for v1.13

## V-01 — Validation Contract ↔ SQL nullable/required parity

Machine compare selected DTO/collection requiredness with physical columns.

At minimum:

```text
Education required_fields=[]
→ SQL Education business fields may not all be NOT NULL.
```

## V-02 — Application selector semantics in Prototype

Assert:

```text
assignApplication modal contains Submission date + status
and option value identifies exact submission_id.
```

## V-03 — Operational participant guard — all schedule paths

Browser QA matrix:

```text
Create
Copy
Edit
Reactivate
CANCELLED→operational
```

with inactive current/selected participant.

## V-04 — Latest-only manual status SQL guard

Test historical Submission cannot be changed through any starter helper used by production command.

## V-05 — Machine side-effect completeness

`set_internal_user_active` must declare both:

- Active Application owner guard;
- future/current participant guard.

## V-06 — Version-label self-consistency

Check label text itself, not just predicate truth:

```text
Technical v1.12
Responsive v1.8
```

for validators/manifest proof.

## V-07 — Current Design README status

Scan full `00_README.md`, not only `RESPONSIVE.md`, for stale current Responsive versions.

---

# 14. Recommended Fix Order

## Batch 1 — Technical/Prototype blockers

1. **Resolve Education requiredness SQL mismatch.**
2. **Replace Candidate-only Application selector with exact SubmissionSelector in prototype.**
3. **Apply Active Participant guard to Create/Copy as well as Edit; add browser tests.**

## Batch 2 — Technical hardening

4. Make manual Submission SQL helper latest-safe.
5. Complete `set_internal_user_active` Registry side effects/guarantees.
6. Add exact Application selector and inactive-participant QA cases.

## Batch 3 — Source/evidence cleanup

7. Fix Design README Responsive v1.6 stale status.
8. Fix validator/manifest display labels.
9. Clean legacy Bulk Mark New wording.
10. Register FINAL_REVIEW_GUIDE explicitly as a current non-normative entrypoint.

Then rerun:

```text
validate_package.py
validate_design.py
validate_responsive_v18.py
verify_manifests.py
All-in-One deterministic check
```

---

# 15. Proposed Gate Status

Tôi đề nghị sau review này:

```text
Business Logic Core v1.2
= FROZEN
```

```text
Design System v1.8
= CURRENT / REVIEWED WITH MINOR SOURCE-METADATA FIX
```

```text
Responsive Prototype v1.8
= CURRENT / RE-REVIEW REQUIRED / NOT FROZEN
```

```text
Technical Architecture v1.12
= AMENDED + VALIDATED / TARGETED FIX REQUIRED / NOT YET FROZEN
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

# 16. Final Assessment

v1.12 tiếp tục tiến gần Technical Freeze và không có dấu hiệu cần thay đổi architecture cốt lõi:

```text
Candidate
→ Submission
→ Application
→ Interview
→ Participant
→ Report
```

Ba vấn đề P0 còn lại đều là **cross-layer implementation-contract issues**, không phải yêu cầu thêm feature:

1. Validation nói optional nhưng DB nói required.
2. Domain nói exact Submission nhưng prototype nói Candidate.
3. Operational invariant nói Active Participant nhưng Create/Copy prototype chưa enforce.

Đây chính là loại lỗi dễ lọt qua validator kiểu token/presence và chỉ xuất hiện khi trace:

```text
Business
→ Machine Contract
→ SQL
→ Effective Prototype
→ Adversarial interaction
```

Sau khi đóng ba P0 trên, tôi đánh giá v1.12 sẽ rất gần mức phù hợp để thực hiện **Technical Freeze Review**, rồi chuyển trọng tâm sang executable migrations/RLS/race tests/production implementation evidence thay vì tiếp tục mở rộng specification.

---

# Appendix A — Fresh Evidence

```text
ZIP SHA-256
2c4f0973bc5927ebd90f7d2204819051d765eff5b1ee7ad52d4108138da73d64
```

```text
Full Handover v1.12
424 / 424 PASS
```

```text
Design System v1.8
72 / 72 PASS
```

```text
Responsive Prototype v1.8 Browser QA
93 / 93 PASS
```

```text
Manifest verification
499 checks / 0 failures
```

## Additional adversarial prototype evidence run during this review

```text
Application assignment modal:
Candidate-only options confirmed; no exact Submission identity displayed.
```

```text
Create Interview with state.users.u1.active=false:
round count 1 → 2
no blocking error
```

---

# Appendix B — Highest-leverage new Acceptance Cases

```text
AC-EDU-DB-01
Validation Contract Education requiredness equals physical DB requiredness.

AC-PROTO-SUBSEL-01
Application creation uses exact SubmissionSelector and returns submission_id.

AC-PROTO-SUBSEL-02
Two Submissions from one Candidate remain distinguishable/selectable.

AC-PART-OPER-CREATE-01
Create resource-blocking Interview with inactive selected Participant → BLOCK.

AC-PART-OPER-COPY-01
Copy schedule with inactive copied/prefilled Participant → BLOCK.

AC-STAT-LATEST-SQL-01
Historical non-latest Submission cannot be manually NEW/READ through production SQL/helper path.

AC-USR-LIFE-REG-01
Machine registry for set_internal_user_active declares future-current-participant reassignment guard.
```
