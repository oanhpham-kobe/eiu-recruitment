# EIU Recruitment Web App — Full Review Report
## Baseline: Full Handover v1.6(3) + Design System v1.5(3)

**Ngày review:** 02/09/2026  
**Reviewer baseline:** review lại từ đầu, chỉ dùng hai package hiện tại làm **source of truth**:

1. `App_Tuyen_Dung_EIU_Full_Handover_v1.6(3).zip`
2. `EIU_Recruitment_Design_System_v1.5(3).zip`

**SHA-256 của ZIP được review**

- Full Handover v1.6(3): `26b452f72aa9fe54ff08a884828de145147f0283e362746cbe403ca9ec562106`
- Design System v1.5(3): `918ba68482dd1bba1ff52af543cb61eae49c42f2acce2b812c1ed24064bb2cfc`

> Các version v1.5/v1.4 trở về trước **không được dùng để suy ra trạng thái hiện tại**.  
> Các repo tham khảo ECC / Superpowers / Matt Pocock / ByteByteGo chỉ được dùng như **review lenses** để tìm contradiction, failure mode, security/accessibility/system-design gap; chúng không override source of truth EIU.

---

# 1. Executive Summary

Bản **Full Handover v1.6 + Design System v1.5** tiếp tục cải thiện rõ rệt và đã đóng được nhiều vấn đề của vòng trước.

## Automated evidence

Khi chạy đúng cross-package:

```text
Full Handover validator:
TOTAL=87 PASS=87 FAIL=0

Design System validator:
TOTAL=21 PASS=21 FAIL=0
```

Các kiểm tra tốt đã có gồm:

- Technical version 1.6 / Design 1.5;
- unique Acceptance IDs;
- 54 commands trong `command_registry.yaml`;
- command ↔ contract ↔ coverage presence;
- exact unused-delete permissions;
- Room structural guard;
- authoritative Privacy Notice capability;
- email `submission_id` trace;
- rate-limit defaults;
- web security baseline tokens;
- archive runbook;
- Design table arithmetic;
- Drawer old `55vw` contradiction removed;
- HR Inbox file components;
- deterministic `ALL_IN_ONE_SPEC` regeneration.

## Nhưng semantic review vẫn tìm thấy gap

Điểm quan trọng nhất của vòng này:

> **87/87 + 21/21 chỉ chứng minh các checks hiện có pass; không chứng minh toàn bộ source-of-truth không còn contradiction.**

Tôi xác nhận còn một số vấn đề phải sửa trước khi đánh dấu **Technical Architecture = FROZEN**.

### Mức độ hiện tại

| Layer | Reviewer assessment |
|---|---|
| Business domain/entity model | **Rất tốt, nhưng còn 1 status contradiction cần sửa** |
| Backend command model | **Khá mạnh, còn một số side-effect/lifecycle contract thiếu** |
| PostgreSQL starter | **Khá tốt, còn invariant/privacy/session gap** |
| Concurrency | **Tốt, nhưng “effective/current/resource-blocking” chưa canonical** |
| Auth/RLS/security | **Tốt, còn một cross-source contextual-access contradiction** |
| Storage/upload | **Tốt** |
| Email | **Architecture tốt, còn wording + Candidate Update side-effect drift** |
| Privacy | **Có nền tảng tốt, edit acknowledgement + notice immutability cần đóng** |
| Design System v1.5 | **Khá chặt, không thấy lỗi layout lớn mới** |
| AI/agent handover quality | **Cần sửa mạnh source pointers/version status** |
| Technical Architecture | **NOT YET FROZEN** |
| Production Ready | **NO** — phù hợp với package hiện tại |

---

# 2. Review Methodology

Review này áp dụng các lớp sau:

```text
SOURCE PINNING
→ DOMAIN / TERMINOLOGY
→ BUSINESS FLOW
→ UI ACTION
→ PERMISSION
→ TRUSTED COMMAND
→ LOCK / TRANSACTION
→ DATABASE INVARIANT
→ SIDE EFFECT
→ AUDIT
→ ACCEPTANCE TEST
→ DESIGN / ACCESSIBILITY
→ FAILURE / RETRY / CONCURRENCY
→ VERIFICATION EVIDENCE
```

Các skill/lens tham khảo đã được dùng có chọn lọc:

- **documentation-lookup**: xác minh framework/Supabase/Next.js bằng official current docs;
- **postgres-patterns**: schema/index/RLS/concurrency review;
- **security-review**: Auth, authorization, PII, file, session, secrets;
- **accessibility / frontend-a11y**: Design System/WCAG;
- **architecture-decision-records / domain modeling**: tìm thuật ngữ overloaded;
- **click-path-audit**: trace state/action interaction;
- **browser-qa / react-testing / tdd-workflow**: đánh giá readiness của test/release gate;
- **verification-before-completion**: không coi PASS nếu không có evidence thực tế.

---

# 3. Findings Summary

## P0 — Blocker trước Technical Architecture Freeze

| ID | Finding | Type |
|---|---|---|
| **P0-01** | Current source/gate navigation vẫn trỏ version cũ và bỏ sót docs 66–71; semantic validator vẫn PASS | Source-of-truth / agent reliability |
| **P0-02** | Submission `no active Application` có hai rule khác nhau | Business state-machine contradiction |
| **P0-03** | `effective active`, contextual access, resource blocking và Application Reactivate current-only chưa dùng cùng một predicate | Security / concurrency / domain semantics |
| **P0-04** | Candidate EDIT bắt buộc Privacy acknowledgement ở Form/Design nhưng `update_candidate_submission()` không xử lý acknowledgement | Privacy / workflow contradiction |

## P1 — Nên đóng trước implementation freeze / code handoff

| ID | Finding |
|---|---|
| P1-01 | Candidate Update HR notification không được ghi trong update command; rate-limit key cũng chưa phù hợp Candidate system notification |
| P1-02 | Published Privacy Notice content/version chưa được bảo vệ bất biến |
| P1-03 | Candidate Form Session physical constraints chưa enforce privacy/base-version invariants |
| P1-04 | Candidate current profile cache có thể stale sau HR edit/latest edit/hard-delete latest Submission |
| P1-05 | Participant `RESTORE_OLD_REPORT` chưa định nghĩa exact state transitions |
| P1-06 | Application “identity” vs active-only DB uniqueness / inactive duplicate semantics chưa canonical |
| P1-07 | Internal User hard-delete có trong frozen delete matrix nhưng chưa có command/permission/UI classification |
| P1-08 | Application hard-delete matrix vẫn ghi “không có Interview Session” dù auto Round 1 rỗng được phép cascade |
| P1-09 | Production UAT còn câu malware rule “if enabled” dù scanner là mandatory |
| P1-10 | Email doc cũ vẫn dùng wording “prevents duplicate sends” và Candidate notification wording chưa khớp outbox transaction |
| P1-11 | Acceptance `AC-54` vẫn nói upload policy chưa owner/IT approved dù whitelist/limits đã freeze |
| P1-12 | Historical Technical Review `49` vẫn chứa owner/gap status cũ nhưng AI Prompt B vẫn yêu cầu đọc như current review source |

## P2 — Hardening / maintainability / release-quality

- `bump_submission_aggregate_version()` có expression `version_no + 1` dư thừa vì `BEFORE UPDATE touch_version()` đã authoritative tăng version;
- current headers/version metadata của một số modular docs còn cũ;
- nên thêm exact dependency baseline khi coding bắt đầu;
- nên chạy FK/index audit + `EXPLAIN (ANALYZE, BUFFERS)` trên migration thật;
- nên bổ sung Browser QA / Click-path evidence matrix;
- accessibility zoom/reflow acceptance nên đo được rõ hơn;
- nên tạo Domain Glossary / ADR cho các predicate và lifecycle khó.

---

# 4. P0-01 — Source-of-truth / Review Gate hiện vẫn có version drift

Đây là finding quan trọng vì package này được thiết kế để giao cho **AI reviewer / coding agent**.

## 4.1 `FINAL_REVIEW_GUIDE.md` tự mâu thuẫn

Current file:

```text
# Final Review Guide — Full Handover v1.6
```

nhưng ngay đầu file vẫn ghi:

```text
Design System: v1.4 CURRENT
Technical Architecture: v1.5 ...
```

trong khi dòng sau lại hướng người review tới **Design System v1.5**.

Guide vẫn ưu tiên:

```text
60_EXTERNAL_REVIEW_V3_RESOLUTION.md
65_TECHNICAL_PRECODE_GATE_V1_5.md
```

thay vì current:

```text
69_EXTERNAL_REVIEW_V4_RESOLUTION.md
70_SEMANTIC_VALIDATION_GATE.md
71_TECHNICAL_PRECODE_GATE_V1_6.md
```

Security reviewer còn được hướng tới:

```text
docs 39–48, 54–65
```

nên **66–71 có thể bị bỏ qua**.

---

## 4.2 `00_README.md` vẫn trỏ current reviewer về gate cũ

Current README đúng ở đầu:

```text
Design System v1.5 CURRENT
Technical Architecture v1.6
```

nhưng phần đọc tài liệu vẫn dùng:

```text
60_EXTERNAL_REVIEW_V3_RESOLUTION
65_TECHNICAL_PRECODE_GATE_V1_5
Architect / Developer: 37–65
```

và Gate Status:

```text
See ... 65_TECHNICAL_PRECODE_GATE_V1_5.md
```

Trong khi v1.6 đã có docs **66–71**.

README còn ghi:

```text
Desktop clickable prototype still needs resync to v1.4
```

trong khi Design System hiện là **v1.5**.

---

## 4.3 `16_AI_REVIEW_AND_BUILD_PROMPT.md` là rủi ro lớn nhất cho coding agent

Prompt A:

```text
Technical Closure docs 37–65
```

→ bỏ toàn bộ:

```text
66 Archive/Purge
67 Web Security
68 Rate Limits
69 External Review v4
70 Semantic Gate
71 Pre-code Gate v1.6
```

Prompt B còn bắt agent đọc `49_TECHNICAL_REVIEW_VERCEL_SUPABASE.md`, trong khi file 49 vẫn có summary lịch sử như:

```text
Candidate conflict — owner confirmation còn mở
Candidate auth — còn cần chốt
Privacy/retention — OWNER/LEGAL DECISION REQUIRED
```

Các vấn đề này đã được package hiện tại đóng ở các file khác.

Prompt v1.6 cũng vẫn ghi:

```text
Design v1.4 table/security/privacy updates
```

---

## 4.4 `15_ALL_IN_ONE_SPEC.md` deterministic nhưng chứa source cũ như source hiện hành

Generator equality đang PASS.

Nhưng All-in-One vẫn đưa nguyên khối:

```text
# 65. Technical Pre-code Gate — v1.5
Design System v1.4 CURRENT
Technical Architecture v1.5 ...
```

rồi sau đó mới tới v1.6 docs.

Điều này chứng minh:

> **Deterministic generation ≠ semantic currentness.**

Một agent đọc từ trên xuống có thể nhận hai “Current status”.

---

## 4.5 Validator không thực hiện đầy đủ chính Gate 70

`70_SEMANTIC_VALIDATION_GATE.md` yêu cầu:

> Current status docs contain no stale CURRENT Technical/Design version labels.

Nhưng `validate_package.py` hiện chủ yếu kiểm:

```text
14_SCOPE_AND_OPEN_ITEMS.md
```

cho version coherence.

Nó không scan đầy đủ:

- `FINAL_REVIEW_GUIDE.md`;
- `00_README.md` navigation/gate pointers;
- `16_AI_REVIEW_AND_BUILD_PROMPT.md`;
- `52_TECHNICAL_GATE_STATUS.md`;
- old current-status blocks trong `15_ALL_IN_ONE_SPEC.md`.

Do đó `87/87 PASS` hiện là **false green về semantic source governance**.

## Đề nghị

### Bắt buộc

1. `FINAL_REVIEW_GUIDE`:
   - Design v1.5;
   - Technical v1.6;
   - Review v4;
   - Gate 71.

2. `00_README`:
   - reviewer current path = `69 → 70 → 71`;
   - architect docs = `37–71`;
   - prototype sync = DS v1.5.

3. `16_AI_REVIEW_AND_BUILD_PROMPT`:
   - source range = `37–71`;
   - Review v4/current security docs;
   - file 49 chỉ được đọc như historical background nếu vẫn giữ.

4. `52`:
   - prototype target v1.5.

### Strong recommendation

Mỗi modular document thêm metadata:

```text
status: CURRENT | HISTORICAL | SUPERSEDED
superseded_by: ...
```

All-in-One current spec:

- exclude historical/superseded source from normative body;
- hoặc đưa xuống appendix **HISTORY ONLY / NOT SOURCE OF CURRENT BEHAVIOR**.

### Validator

Scan exact current-navigation set thay vì chỉ một file.

**Severity: P0** vì package này là handover cho AI/developer và current source pointer đang sai.

---

# 5. P0-02 — Submission State Machine vẫn còn contradiction

## Source A — `07_STATUS_AND_BUSINESS_RULES.md`

Rules hiện ghi:

```text
Submit → NEW
HR mở → READ
Có active Application → PROCESSED
...
Không còn active Application → READ
```

Nếu đọc literal:

```text
Candidate Submit
→ NEW
→ chưa có Application
→ READ
```

thì `NEW` không thể tồn tại.

---

## Source B — authoritative calculator

`37_BACKEND_COMMAND_CONTRACTS.md` và SQL helper lại xác định:

```text
no active Application
→ preserve current NEW/READ
→ nếu đang ở derived state và final Application removed thì về READ
```

Đây là rule hợp lý hơn.

Candidate Reactivation là exception riêng:

```text
no active Application
→ force READ
```

---

## Acceptance cũng còn generic

`AC-08`:

```text
no active Application → Read according to frozen workflow
```

trái với calculator ở case untouched `NEW`.

## Canonical rule đề nghị

```text
SUBMISSION STATUS

Submit
→ NEW

HR opens with submissions.status
→ READ

Active Application exists:
  any HIRED    → DONE
  all REJECTED → CLOSED
  otherwise    → PROCESSED

No active Application:
  if current status ∈ {NEW, READ}
      preserve current manual state
  else
      READ

Candidate Reactivation:
  deliberate lifecycle exception
  no active Application → READ
```

## Sửa

- `07_STATUS...`
- `AC-08`
- All-in-One regenerated
- validator test matrix.

Thêm acceptance:

```text
NEW + no Application + generic recalc → NEW
READ + no Application + generic recalc → READ
PROCESSED + last Application removed → READ
Candidate Reactivate NEW/no Application → READ
```

**Severity: P0.**

---

# 6. P0-03 — Cần tách 3 khái niệm: Access Active / Current Round / Resource Blocking

Đây là finding domain + security + concurrency.

Hiện nhiều tài liệu dùng từ “effective active / operational” theo nghĩa khác nhau.

---

## 6.1 Business Interviewer contextual access thiếu parent Application active

`02_ROLES_PERMISSIONS_AND_NAVIGATION.md` và:

```text
logic_validation/33_PERMISSION_MODEL_FINAL.md
```

đang ghi Interviewer được thấy khi:

```text
participant.user_id = current_user
participant.is_current = true
interview.is_active = true
visible_to_interviewers = true
app_user.is_active = true
```

**Thiếu:**

```text
application.is_active = true
```

Trong khi Security spec `39` lại đúng:

```text
application.is_active
AND interview.is_active
AND participant.is_current
...
```

Acceptance cũng nói:

> parent Application inactive revokes contextual access.

Đây là cross-source security contradiction.

---

## 6.2 SQL định nghĩa `effective_interviews`

```sql
where application.is_active = true
  and interview.is_active = true
```

Không loại `CANCELLED`.

---

## 6.3 Concurrency doc dùng “effective active” theo nghĩa khác

`48_IDEMPOTENCY_CONCURRENCY_SPEC.md`:

```text
Effective active requires:
active Application
+ active Interview
+ non-CANCELLED schedule
```

Tức là cùng thuật ngữ nhưng khác SQL.

---

## 6.4 Application Reactivate current-only chưa được physical model biểu diễn

v1.6 đã chốt:

```text
Application Reactivate
→ only Current Round operational
→ historical rounds non-blocking
```

`app_spec.yaml`:

```text
reactivation_operational_round: CURRENT_ACTIVE_LATEST_ONLY
```

Acceptance:

```text
AC-APP-REACT-05
```

Nhưng `private.effective_interviews` sau khi Application active trở lại vẫn trả:

```text
mọi Interview có i.is_active=true
```

Không có field/predicate nào đánh dấu old active rounds là:

```text
historical_non_blocking
```

Global conflict spec lại nói block trên effective-active Sessions.

### Kết quả

Current-only reactivation behavior **không thể được suy ra chắc chắn từ physical starter hiện tại**.

---

## Canonical domain model đề nghị

Đừng dùng một chữ `effective_active` cho 3 nghĩa.

### A. `access_active`

```text
application.is_active
AND interview.is_active
```

Dùng cho:

- Interviewer contextual access;
- current-round candidate set;
- UI current/inactive visibility.

### B. `current_round`

```text
highest round_no among access_active Interviews
```

Dùng cho:

- Report page;
- current outcome;
- Preview/PDF.

### C. `resource_blocking`

Phải chốt **một** rule:

```text
access_active
AND schedule_status != CANCELLED
AND start_at/end_at exist
[AND current_round only ?]
```

Phần `[current_round only ?]` phải được quyết định rõ.

### Khuyến nghị kỹ thuật

Nếu muốn giữ v1.6 “current-only operational”:

```text
resource_blocking :=
access_active
AND interview = application_current_interview
AND schedule_status != CANCELLED
```

và tất cả conflict queries/locks dùng đúng predicate này.

Nếu owner muốn mọi scheduled active historical round vẫn block, thì bỏ câu “historical rounds non-blocking/current-only” khỏi reactivation contract và Reactivate phải revalidate mọi child interval trở lại effective.

Không nên giữ trạng thái nửa current-only, nửa all-active.

## Sửa

- `02`
- `logic_validation/33`
- `48`
- `37 reactivate_application`
- `app_spec`
- conflict-engine implementation blueprint
- acceptance race/reactivation tests.

**Severity: P0** vì ảnh hưởng RLS/contextual access và double-booking semantics.

---

# 7. P0-04 — Candidate EDIT Privacy acknowledgement chưa khép kín

## Business source

`03_CANDIDATE_FORM_AND_PORTAL.md`:

```text
Editing a NEW Submission also uses a Form Session.
...
Final Privacy section is required:
localized notice
notice version
details
required acknowledgement
validation
```

Design v1.5 cũng nói Candidate Form kết thúc bằng:

```text
PrivacyNoticeAcknowledgement
required checkbox
Submit disabled until valid
```

---

## Backend CREATE path

`submit_candidate_submission(...)`:

- receives privacy version;
- validates;
- creates `privacy_acknowledgement`.

Đúng.

---

## Backend EDIT path

`update_candidate_submission(form_session_id, payload)` hiện:

- active Candidate;
- Submission NEW;
- version match;
- text/file staged Save;
- document validation.

Nhưng không nói:

- privacy version;
- required acknowledgement;
- create/update acknowledgement;
- behavior nếu Privacy Notice version đổi trong thời gian Submission còn NEW.

---

## Physical model

`candidate_form_sessions` có:

```text
presented_privacy_notice_version
```

cho cả NEW và EDIT.

`privacy_acknowledgements` cho phép:

```text
unique(submission_id, notice_version)
```

→ về kỹ thuật hoàn toàn có thể lưu acknowledgement mới theo version.

## Cần chọn một rule duy nhất

### Option A — phù hợp với wording current source

Candidate EDIT cũng phải acknowledge pinned notice.

Save:

```text
lock Form Session
→ validate acknowledgement of presented version
→ if Submission has not acknowledged this notice_version:
     insert acknowledgement
→ save text/doc
→ complete session
```

### Option B

Privacy acknowledgement chỉ required cho **NEW_SUBMISSION**.

Nếu chọn B thì phải sửa:

- `03` “Final Privacy section required”;
- Design Candidate Form;
- Form Session UI behavior;
- privacy session pin rules cho EDIT.

Hiện source thiên rõ về **Option A**, nên tôi khuyến nghị implement Option A nếu Legal/Owner không có yêu cầu khác.

Thêm AC:

```text
AC-PRIV-EDIT-01
EDIT session pins notice version and requires acknowledgement.

AC-PRIV-EDIT-02
Same notice version already acknowledged → Save remains idempotent.

AC-PRIV-EDIT-03
New notice version during existing NEW Submission edit → exact pinned version recorded.

AC-PRIV-EDIT-04
Client arbitrary version rejected.
```

**Severity: P0** vì hiện UI/business yêu cầu nhưng command không persist/validate.

---

# 8. P1-01 — Candidate Update notification side effect chưa nằm trong update command

`03`:

```text
Gửi email thông báo HR sau mỗi lần Candidate tạo mới hoặc chỉnh sửa.
```

`43_EMAIL_DELIVERY_SPEC.md`:

```text
Candidate Submit/Update notification
is enqueued in the same business transaction as Submission change.
```

Nhưng:

```text
update_candidate_submission()
```

không liệt kê enqueue side-effect.

Coding agent đọc command contract có thể triển khai:

```text
Save update
→ audit
→ no HR notification
```

## Cần thêm vào command

```text
update_candidate_submission(
  form_session_id,
  payload,
  idempotency_key
)
```

Transaction:

```text
...
apply Submission/file changes
refresh Candidate cache if applicable
enqueue exact-submission HR notification
mark form session completed
audit
commit
```

Client retry phải trả lại cùng logical result/outbox.

---

## Rate-limit gap

`68_RATE_LIMIT_POLICY.md` có:

```text
Candidate Submit
```

nhưng không có Candidate Update.

`Manual/system email enqueue` lại dùng primary key:

```text
app_user_id + email_type
```

không phù hợp Candidate-generated notification.

Đề nghị thêm:

```text
Candidate Update / Candidate system notification
key = candidate_id + submission_id + email_type
```

hoặc coalescing/throttling policy riêng.

Không nên để rate-limit email làm rollback một legitimate Candidate Save; nếu notification bị throttle, cần xác định transaction semantics rõ.

---

# 9. P1-02 — Published Privacy Notice phải bất biến về nội dung

Schema:

```text
privacy_notice_versions
notice_version PK
content_vi
content_en
content_hash_sha256
published_at
effective_from
is_current
```

Nhưng không có guard ngăn:

```text
UPDATE content_vi
UPDATE content_hash
UPDATE effective_from
```

sau khi Candidate đã acknowledgement version đó.

Nếu row bị edit:

```text
Candidate acknowledged v2026-01
```

nhưng nội dung `v2026-01` sau đó thay đổi, historical proof không còn chắc chắn.

## Đề nghị

Sau khi version được published/referenced:

Immutable:

```text
notice_version
content_vi
content_en
content_hash_sha256
published_at
effective_from
```

Cho phép thay đổi lifecycle:

```text
is_current
```

Nội dung mới:

```text
create new notice_version
```

Ngoài ra start Form Session phải fail-safe nếu:

- không có current effective notice;
- current notice `effective_from > now()`.

Thêm stable error:

```text
PRIVACY_NOTICE_UNAVAILABLE
```

---

# 10. P1-03 — Candidate Form Session physical constraints chưa đủ mạnh

Schema hiện:

```text
presented_privacy_notice_version nullable
base_submission_version_no nullable
```

Check chỉ enforce:

```text
NEW → target_submission_id NULL
EDIT → target_submission_id NOT NULL
```

Nhưng source truth nói:

- every Form Session pins Privacy Notice;
- EDIT stores base Submission version.

## Đề nghị

Database check:

```text
presented_privacy_notice_version IS NOT NULL

NEW_SUBMISSION:
  target_submission_id IS NULL
  base_submission_version_no IS NULL

EDIT_SUBMISSION:
  target_submission_id IS NOT NULL
  base_submission_version_no IS NOT NULL
```

Trusted command vẫn là primary control, DB guard là defense-in-depth.

---

# 11. P1-04 — Candidate current-profile cache có lifecycle gap

Candidate physical fields:

```text
current_full_name
current_phone
last_submission_at
```

Invariant:

> current Candidate profile cache = latest submitted snapshot only.

Submit command có update cache.

Candidate edit command nói:

> editing older Submission does not overwrite cache.

Nhưng các paths sau chưa explicit:

### A. Candidate edits latest NEW Submission

Phải update cache.

### B. HR edits latest Submission

`update_submission_by_hr()` không nói refresh cache.

### C. Hard-delete latest unused Submission

Candidate có thể có:

```text
S1 old
S2 latest, no Application
```

Hard-delete S2 hợp lệ.

Sau delete:

```text
current_full_name/current_phone/last_submission_at
```

phải fallback về S1.

Nếu không, Candidate cache vi phạm invariant.

## Đề nghị

Một helper:

```text
refresh_candidate_current_profile(candidate_id)
```

dùng sau:

- new Submission;
- Candidate update latest;
- HR update latest;
- hard-delete Submission;
- migration/data repair.

Nguồn chọn:

```text
ORDER BY submitted_at DESC, submission_id DESC
LIMIT 1
```

Nếu không còn Submission:

```text
current_full_name = NULL
current_phone = NULL
last_submission_at = NULL
```

---

# 12. P1-05 — `RESTORE_OLD_REPORT` cần exact transition

Current command:

```text
remove:
participant not current
archive report

re-add:
RESTORE_OLD_REPORT
or CREATE_NEW_REPORT
```

Nhưng Restore chưa nói chính xác:

- participant `is_current`;
- `removed_at`;
- participant `version_no`;
- report `is_active`;
- report `is_archived`;
- report version;
- decision metadata;
- audit;
- duplicate current participant race.

Final Decision Source chỉ nhận:

```text
participant.is_current = true
report.is_active = true
report.is_archived = false
```

Vì vậy “Restore old” sẽ không hoạt động đúng nếu chỉ restore participant mà không unarchive report.

## Canonical Restore đề nghị

```text
lock Interview
lock historical Participant instance
verify no current duplicate for same user
re-check schedule conflict
set participant:
  is_current = true
  removed_at = NULL
  participant_order = assigned order
  bump version

restore report:
  is_active = true
  is_archived = false
  preserve report content
  preserve original decision_updated_at
  bump version

audit RESTORE_PARTICIPANT_REPORT
```

Nếu `CREATE_NEW_REPORT`:

- old participant/report remain historical;
- new participant snapshot gets current Directory identity;
- new empty report lifecycle starts separately.

Thêm acceptance cho PDF/final source after restore.

---

# 13. P1-06 — “Application identity” cần định nghĩa rõ là global hay active dedupe key

Business dùng:

```text
submission + unit + team + position
```

và gọi đó là **Application identity**.

AC:

```text
Exact duplicate active Application → update existing.
```

DB:

```sql
unique (...) WHERE is_active = true
```

Do đó DB cho phép:

```text
Application A inactive
Application B active
same submission/unit/team/position
```

v1.6 còn có:

```text
reactivate old A
→ DUPLICATE_APPLICATION if B active
```

Điều này có thể là chủ ý để hỗ trợ historical reuse, đặc biệt vì frozen rule cho phép CLOSED Submission tạo Application mới.

Vấn đề không phải chắc chắn DB sai; vấn đề là thuật ngữ **identity** đang làm người đọc nghĩ “globally unique”.

## Cần ghi rõ một trong hai

### Model A — Durable global identity

Same combination = same Application forever.

→ non-partial UNIQUE;
→ inactive duplicate không tạo mới;
→ use Reactivate + new Interview rounds.

### Model B — Active dedupe identity

Same combination unique **chỉ trong active lifecycle**.

→ partial UNIQUE hiện tại đúng;
→ inactive historical Application + new active Application được phép;
→ docs đổi wording thành:

```text
active_application_dedupe_key
```

và quy định rõ khi CLOSED/reuse tạo new vs Reactivate.

Với current DB, package đang gần Model B hơn.

Tôi **không đề nghị tự đổi UNIQUE** trước khi owner xác nhận semantics này.

---

# 14. P1-07 — Internal User hard-delete tồn tại trong Matrix nhưng chưa có command path

Frozen delete matrix:

```text
Internal User
Hard Delete khi chưa từng được tham chiếu
Inactive khi đã từng được dùng
```

Nhưng:

- không có `delete_unused_internal_user`;
- không có exact delete permission;
- User Directory spec chỉ create/edit/active-inactive;
- Design không có hard-delete semantics riêng.

## Nên chọn

### Option A — maintenance-only

```text
Unreferenced + unbound internal directory row
→ Root maintenance cleanup only

Bound identity or historical user
→ Inactive
```

Không expose HR UI delete.

### Option B

Thêm Root-only trusted command:

```text
delete_unused_internal_user()
```

với:

- no business reference;
- no HR role;
- not Root;
- Auth binding policy;
- audit.

Tôi nghiêng **Option A** cho an toàn security identity.

---

# 15. P1-08 — Application hard-delete Matrix chưa phản ánh auto Round 1 exception

`logic_validation/35_DELETE_INACTIVE_MATRIX.md`:

```text
Application hard-delete:
Không có Interview Session/business downstream
```

Nhưng mọi Application mới đều auto-create Round 1.

Current authoritative command lại đúng hơn:

```text
empty auto-created Round 1
does not count as business history
→ delete Round 1 + Application atomically
```

Matrix literal khiến developer hiểu:

> Application không bao giờ hard-delete được.

## Sửa row

```text
Application hard-delete:
Không có meaningful Interview/business usage.
Auto-created structurally-empty Round 1 may be deleted atomically with Application.
```

Thêm exact definition “structurally empty” trong một chỗ authoritative.

---

# 16. P1-09 — Malware UAT wording vẫn cũ

Production source hiện chốt:

```text
malware_scan_before_finalize = REQUIRED_PRODUCTION
```

NFR:

> scan required because legacy `.doc/.ppt` external formats are accepted.

UAT section F vẫn có:

```text
malware/quarantine rule if enabled
```

Trong cùng UAT phía dưới lại có:

```text
Malware scan blocks INFECTED/ERROR/not-clean.
```

## Sửa

Bỏ `if enabled`.

Production must test:

```text
PENDING  → no finalize
INFECTED → reject
ERROR    → fail closed / defined retry
CLEAN    → eligible
scanner unavailable → no silent bypass
```

---

# 17. P1-10 — Email source vẫn còn wording cũ

`43_EMAIL_DELIVERY_SPEC` hiện rất tốt:

```text
client retry → no duplicate logical enqueue
provider retry → at-least-once; duplicate delivery possible
```

Nhưng `11_EMAIL_DOCUMENTS_AND_ACTIVITY_LOG.md` còn:

```text
This prevents duplicate sends on browser retry/double click
```

Nên đổi thành:

```text
This prevents duplicate logical Outbox enqueue on browser retry/double click.
```

Ngoài ra Candidate notification ghi:

```text
enqueue HR notification after the core transaction succeeds
```

trong khi authoritative email spec yêu cầu:

```text
insert outbox inside same business transaction
then COMMIT
```

Sửa thành:

```text
Candidate business transaction includes Outbox enqueue before commit.
External provider delivery occurs after commit.
```

Validator email semantics hiện chỉ scan Acceptance + 43 nên bỏ lọt file 11.

---

# 18. P1-11 — AC-54 vẫn thể hiện upload policy chưa freeze

Acceptance:

```text
AC-54 Upload policy —
MIME/size/preview rules must be owner/IT-approved before go-live.
```

Nhưng owner decisions hiện đã freeze:

- PDF;
- DOC/DOCX;
- PPT/PPTX;
- PNG/JPG/JPEG;
- max 5 current files;
- max 5 MB/file;
- malware scan mandatory;
- preview controlled.

## Sửa AC-54 thành executable criterion

Ví dụ:

```text
AC-54 Upload policy —
server accepts only approved Phase-1 formats/signatures,
max 5 MB/file and max 5 current files/parent;
active-content preview is not browser-rendered arbitrarily;
malware CLEAN is mandatory before finalize.
```

Legal/IT operational scanner approval có thể để Production UAT, không để AC nói business policy còn chưa chốt.

---

# 19. P1-12 — Historical file 49 đang được AI Prompt đọc như current review input

`49_TECHNICAL_REVIEW_VERCEL_SUPABASE.md` vẫn có early-review status:

```text
Candidate conflict: GAP / owner confirmation open
Candidate auth: partial / method needs decision
Privacy retention: owner/legal decision
...
```

Các mục này đã được resolve trong v1.4–v1.6.

Nếu vẫn muốn giữ file 49:

```text
STATUS: HISTORICAL REVIEW
CURRENT OUTCOME SUPERSEDED BY 56/60/69/71
DO NOT USE ITS GAP TABLE AS CURRENT STATUS
```

Hoặc cập nhật summary hiện tại nhưng giữ historical section riêng.

`16_AI_REVIEW_AND_BUILD_PROMPT.md` không nên đưa file 49 vào current production review list nếu không có banner này.

---

# 20. P2 — `bump_submission_aggregate_version()` không double-increment nhưng code gây hiểu nhầm

Tôi đã kiểm tra kỹ finding này.

Helper:

```sql
UPDATE submissions
SET version_no = version_no + 1
```

nhưng bảng có `BEFORE UPDATE` trigger:

```sql
NEW.version_no := OLD.version_no + 1;
```

Kết quả thực tế vẫn là:

```text
+1 exactly once
```

vì trigger **gán lại** từ `OLD`.

Do đó **không phải bug**.

Tuy nhiên implementation gây hiểu nhầm cho reviewer/developer.

Đề nghị helper chỉ làm:

```sql
UPDATE submissions
SET updated_at = now()
WHERE ...
```

hoặc một no-op semantic touch field phù hợp, để trigger là single authoritative version increment.

Nếu giữ code hiện tại, thêm comment:

```text
touch_version trigger overrides NEW.version_no from OLD;
this statement does not produce +2.
```

---

# 21. Design System v1.5 Review

## 21.1 Không thấy lỗi table arithmetic mới

Validator và manual arithmetic đều khớp:

| Page | Frozen width |
|---|---:|
| Application Inbox | **1560px** |
| Interview | **1480px** |
| HR Report | **1610px** |

HR Report 1610px đã được sửa đúng.

---

## 21.2 Drawer contradiction cũ đã được sửa

Current token:

```text
preferred 820px
actual = min(820px, available-content-width)
```

Không còn legacy:

```text
760–860px + max 55vw
```

trong current component rule.

`MASTER.md` vẫn dùng mô tả rộng “typically 760–860px or page-specific token”; không sai toán vì 820 nằm trong range, nhưng để giảm source duplication nên chỉ reference Drawer token.

**P2 cleanup.**

---

## 21.3 HR Inbox file management đã đồng bộ

`page_component_matrix.csv` hiện có:

```text
FileList
FilePreview
AsyncStatus
ConfirmationDialog
```

phù hợp business Upload/Replace/Delete.

Đây là sửa đúng.

---

## 21.4 Privacy/SubmissionSelector đã đồng bộ Design

Design hiện có:

```text
SubmissionSelector
→ returns submission_id
→ shows Candidate name/email/date/status
```

và:

```text
PrivacyNoticeAcknowledgement
```

Đây là hướng đúng.

Gap còn lại là **EDIT-mode privacy semantics**, không phải visual component thiếu.

---

## 21.5 Accessibility status tốt

Current Design đã có:

- min 16px operational content;
- semantic keyboard expansion;
- row click không thay semantic control;
- focus restore;
- no generic `overflow-wrap:anywhere`;
- sticky identity columns;
- gold body-text restriction;
- >=44x44 touch target goal;
- VI/EN state preservation;
- privacy errors;
- unsaved warning.

Không phát hiện contrast regression mới từ các status token hiện tại.

### Hardening đề nghị

Đưa acceptance từ “zoom remains usable” thành đo được hơn:

```text
200% text zoom → no loss of functionality
400% reflow where WCAG SC 1.4.10 applies
wide data tables may retain two-dimensional horizontal scrolling
focus remains visible in sticky-column layouts
```

---

# 22. Click-path Audit — Spec Readiness

Chưa có React code/staging nên chưa thể chạy ECC `click-path-audit` thật trên handlers/store.

Tuy nhiên spec hiện đã chuẩn bị khá tốt các critical paths:

- parent row pointer expansion + semantic keyboard control;
- nested status badge stops row interaction;
- Candidate staged Save/Cancel;
- HR NEW→READ race;
- Copy Interview = draft until Save;
- status badge/menu same action;
- Language switch preserves unsaved values.

## Critical click paths bắt buộc audit khi code có

1. Candidate Edit → stage Replace/Delete → Cancel.
2. Candidate Edit → HR opens → Save gets stale/state error.
3. Row click vs Checkbox vs Status Badge vs Action button.
4. Interview Copy draft → Cancel / Save.
5. Remove Participant with report → Restore old / Create new.
6. Application Inactive → filter Inactive → Reactivate → conflict.
7. User Bound identity → generic Edit must not expose rebind.
8. Master referenced row → Edit/Delete → MasterUsageGuard.
9. Email Preview → double click/retry → one logical enqueue.
10. Language switch while form dirty.
11. Drawer close/Escape/focus return.
12. Bulk all-or-nothing failure rollback.

Tôi đề nghị thêm chúng vào Release/UAT evidence matrix.

---

# 23. Browser QA / Release Gate Improvement

`45_PRODUCTION_UAT_GATE.md` đã có responsive + a11y smoke test, nhưng chưa đủ cụ thể để thay cho browser QA.

Trước release nên có automated + manual evidence trên staging:

### Breakpoints

```text
375px
768px
1280px
1440px
```

### Candidate journeys

```text
OTP
new submission
upload CV
privacy acknowledge
submit
NEW edit
staged file cancel
READ lock
Phiếu của tôi
VI/EN
mobile
```

### HR journeys

```text
open NEW
create Application from exact Submission
duplicate handling
schedule
conflict
participant
report
email
inactive/reactivate
permissions
master lifecycle
```

### Accessibility

- axe automated;
- keyboard-only journey;
- focus order/return;
- live errors/status;
- sticky table focus;
- screen-reader landmark/form sanity pass.

> axe PASS không được coi là toàn bộ WCAG PASS.

### Visual

- baseline screenshots;
- nếu chưa có baseline → result phải là `INCONCLUSIVE`, không silent PASS.

---

# 24. PostgreSQL / Indexing Review

Schema hiện có core indexes quan trọng:

- Submission Candidate/date;
- Submission status/date;
- trigram name;
- email normalization;
- phone normalization;
- Application Submission;
- active Application key;
- Interview Application/round;
- interview time;
- room/time;
- Participant user/interview;
- current participant uniqueness;
- report per Participant.

Đây là baseline tốt.

## Tuy nhiên

Không nên coi starter SQL là đủ index production.

Trước Technical Freeze của **actual migration**:

1. audit every high-cardinality FK used in joins/delete checks;
2. run `EXPLAIN (ANALYZE, BUFFERS)` với NFR dataset;
3. test grouped Candidate/Application pagination;
4. test RLS predicate plans by persona;
5. check `pg_stat_statements` staging after realistic flows.

Đây là implementation evidence, không phải business gap.

---

# 25. Current Framework Documentation Verification
## External verification — không phải EIU source of truth

Tôi đã kiểm tra current official docs ở ngày review.

### Supabase SSR

Current Supabase docs vẫn khuyến nghị:

```text
cookie-based Next.js SSR → @supabase/ssr
```

nhưng package hiện vẫn được Supabase ghi là **beta / API unstable**.

Điều này xác nhận policy hiện tại của Handover là đúng:

```text
pin dependencies
commit lockfile
rerun Auth regression on upgrades
```

### Supabase RLS

Current docs tiếp tục xác nhận:

- Grants và RLS là hai checks riêng;
- views cần được bảo vệ cẩn thận;
- secret/service-role style access bypasses RLS và phải server-only.

Current EIU security architecture đang đi đúng hướng.

### Supabase Storage

Current docs xác nhận signed URL:

- time-limited;
- không tự revoke khi Auth signing key thay đổi;
- vẫn valid tới expiry.

Target EIU **1–5 phút** cho PII files là hợp lý.

### Next.js security/dependency baseline

Current Next.js security release ngày 25/08/2026 yêu cầu patched maintained versions (Active LTS 16.3.3 / Maintenance LTS 15.5.24 tại thời điểm review).

Handover nói “pin reviewed versions” nhưng chưa có exact dependency baseline vì code repo chưa bắt đầu.

## Đề nghị trước coding

Khi scaffold implementation:

```text
DEPENDENCY_BASELINE.md / package.json
```

ghi exact:

- Node;
- Next.js;
- React;
- `@supabase/supabase-js`;
- `@supabase/ssr`;
- test runner;
- Playwright;
- security-sensitive upload/scanner packages.

Không hard-code các version nêu trong report này vào long-lived spec; lấy **current patched version tại ngày implementation**, pin bằng lockfile và record ADR/build evidence.

---

# 26. Validator Improvements

Current validator đã tốt hơn trước nhưng cần nâng semantic coverage.

## V-01 — Current source navigation

Fail nếu current guide/readme/prompt/gate trỏ:

```text
Design v1.4
Technical v1.5
37–65
Review v3 as current
Gate 65 as current
```

Current expected:

```text
Design 1.5
Technical 1.6
37–71
69/70/71
```

---

## V-02 — Historical source metadata

Every review/gate doc:

```text
CURRENT
HISTORICAL
SUPERSEDED
```

All-in-One generator phải phân biệt.

---

## V-03 — Submission state matrix

Machine-check:

```text
NEW/no app generic recalc = NEW
READ/no app = READ
derived/no app = READ
reactivate/no app = READ
```

---

## V-04 — Contextual-access predicate

Check business/security/app spec cùng chứa parent Application active.

---

## V-05 — Active/resource predicate vocabulary

Fail nếu `effective_active` được định nghĩa khác nhau ở nhiều file.

---

## V-06 — Candidate EDIT privacy

If Design says required acknowledgement for Edit, registry/contract/acceptance must map the side-effect.

---

## V-07 — Command side-effect coverage

Current registry mostly checks **command name presence**.

Mở rộng registry:

```yaml
side_effects:
  - enqueue_hr_notification
  - refresh_candidate_cache
  - privacy_acknowledgement
  - submission_recalculate
```

Validator so side-effect requirements, không chỉ tên command.

---

## V-08 — Email semantics scan

Scan all current normative docs, including file 11, not only Acceptance + 43.

Forbidden current wording:

```text
prevents duplicate sends
retry never duplicates delivery
exactly once
```

unless paragraph explicitly states it is impossible/not guaranteed.

---

## V-09 — Delete matrix conformance

Check auto Round 1 exception appears in:

- matrix;
- command;
- invariant;
- acceptance.

Check every entity hard-delete capability maps either to:

```text
UI trusted command
or explicitly MAINTENANCE_ONLY
```

---

## V-10 — Privacy version immutability

Schema/contract must protect acknowledged published content.

---

# 27. Recommended Fix Order

## Batch 1 — P0 source/domain corrections

1. Fix current source pointers + status metadata + All-in-One historical handling.
2. Fix Submission generic no-Application rule.
3. Define canonical:
   - `access_active`;
   - `current_round`;
   - `resource_blocking`.
4. Align Interviewer contextual access with parent Application.
5. Close Candidate EDIT privacy acknowledgement semantics.

## Batch 2 — Data/side effects

6. Candidate Update notification + idempotency + rate-limit.
7. Privacy Notice immutability/current-effective fail-safe.
8. Form Session DB constraints.
9. Candidate current-profile cache refresh helper.
10. Participant Restore exact transitions.
11. Application identity/dedupe terminology.
12. Internal User unused-delete classification.
13. Empty Round1 delete matrix rule.

## Batch 3 — UAT/docs

14. Malware mandatory wording.
15. Email doc wording.
16. AC-54.
17. File 49 historical banner.
18. current version headers cleanup.

## Batch 4 — pre-implementation/release evidence

19. exact dependency baseline at scaffold time.
20. migration index/query-plan audit.
21. React/testing TDD lane.
22. click-path audit.
23. Browser QA / visual/a11y staging evidence.

---

# 28. Proposed Gate Status

Sau review này tôi đề nghị:

```text
Business Logic Core v1.2
= FROZEN
```

Không cần reopen toàn bộ business.

Nhưng các contradiction trong P0 phải được coi là **clarification/fix to source consistency**, không phải feature expansion.

```text
Design System v1.5
= CURRENT / RE-REVIEW REQUIRED
```

Không có visual architecture blocker lớn mới; chủ yếu cần sync với privacy mode semantics và release evidence.

```text
Technical Architecture v1.6
= REVIEWED / NEEDS TARGETED AMENDMENT / NOT FROZEN
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

# 29. What v1.6/v1.5 has done well

Không nên hiểu danh sách finding là package còn yếu. Các phần sau hiện có chất lượng tốt và nên giữ:

- Candidate → Submission → Application → Interview → Participant → Report decomposition;
- dedicated Submission selector;
- Candidate pre-submit Form Session;
- staged file Save/Cancel;
- malware CLEAN requirement;
- Candidate safe Auth rebind;
- Internal first Google bind;
- Root break-glass;
- separate HR Report Note;
- participant-owned reports;
- final-decision timestamp semantics;
- parent Submission lock for recalculation;
- Interview-row-first conflict lock;
- Candidate/Room/Interviewer conflict blocking;
- private storage;
- document logical versioning;
- transactional Outbox;
- honest at-least-once provider semantics;
- `submission_id` email trace;
- exact User lifecycle governance;
- structural master-history guard including Room;
- Web Security baseline;
- Rate-limit policy;
- Archive/Purge runbook;
- 54-command registry;
- Design table width arithmetic;
- dedicated Privacy component;
- sticky context columns;
- Candidate mobile go-live requirement;
- PII search not stored in URL.

v1.6 không cần redesign tổng thể.

Mục tiêu tiếp theo nên là:

> **giảm ambiguity và làm mọi source cùng nói chính xác một điều**, thay vì thêm chức năng.

---

# 30. Final Assessment

Bộ **Full Handover v1.6 + Design System v1.5** hiện đã ở mức cao đối với một pre-code handover.

Khoảng cách còn lại trước Technical Freeze chủ yếu nằm ở 4 loại:

1. **source governance** — current/historical docs chưa tách hoàn toàn;
2. **canonical semantics** — status / active / operational terminology;
3. **cross-layer side effects** — Privacy Edit, Candidate Update notification/cache;
4. **evidence depth** — validator kiểm presence tốt nhưng chưa kiểm đủ semantic outcome.

Tiêu chuẩn tôi khuyến nghị trước khi chuyển `Technical Architecture = FROZEN`:

```text
For every production action:

Actor
→ exact Permission
→ UI state
→ canonical business transition
→ Trusted Command
→ lock/transaction
→ physical invariant
→ side effects
→ audit
→ acceptance test
→ release evidence

must resolve to exactly one interpretation.
```

Hiện package đã rất gần điều kiện đó, nhưng **chưa đạt hoàn toàn** do các P0/P1 nêu trên.

---

# Appendix A — Baseline Validation Evidence

```text
Full Handover:
TOTAL=87
PASS=87
FAIL=0

Design System:
TOTAL=21
PASS=21
FAIL=0
```

Lưu ý:

```text
PASS = all implemented checks passed
```

không được diễn giải thành:

```text
all possible semantic contradictions were checked
```

---

# Appendix B — Review Sources Used

## EIU source of truth

- Full Handover v1.6(3)
- Design System v1.5(3)

## External lenses only

- ECC:
  - documentation-lookup
  - react-patterns
  - postgres-patterns
  - security-review
  - accessibility
  - react-testing
  - browser-qa
  - architecture-decision-records
  - tdd-workflow
  - frontend-a11y
  - click-path-audit
  - context-budget (agent setup only)
  - api-design where applicable
- Superpowers:
  - systematic debugging
  - verification before completion
- Matt Pocock skills:
  - domain modeling
  - spec-vs-standards review
  - writing for agents
- ByteByteGo:
  - system design failure/concurrency/storage/delivery lenses

External material was **not used to override EIU business decisions**.

---

# Appendix C — Recommended New Domain Glossary Terms

To prevent future agent drift, add a short authoritative glossary:

```text
Submission Manual State
NEW / READ

Submission Derived State
PROCESSED / DONE / CLOSED

Candidate Reactivation Rule
Lifecycle exception: no active Application → READ

Interview Access Active
Application active AND Interview active

Current Round
Highest round_no among Access-Active Interviews

Interview Resource Blocking
Canonical predicate to be frozen; do not reuse “effective active” ambiguously

Application Active Dedupe Key
Clarify whether identity is globally unique or active-lifecycle unique

Privacy Notice Version
Published immutable content version presented/pinned by server

Logical Document
Stable document identity across immutable versions
```

This is one of the highest-leverage documentation improvements for future AI-assisted coding/review.
