# EIU Recruitment Web App — Full Review Report
## Baseline: Full Handover v1.13 Bundle
### Includes Design System v1.8 + Responsive Prototype v1.9

**Ngày review:** 03/09/2026

## Source of Truth

Chỉ sử dụng bundle hiện tại:

`App_Tuyen_Dung_EIU_Full_Handover_v1.13.zip`

Bundle chứa:

1. `review_pack/` — Business + Technical source
2. `design_system/` — Design System v1.8
3. `responsive_prototype/` — Responsive Prototype v1.9

**SHA-256 ZIP:**  
`c7df7d4c2bb3860835f10a9568f2c4050a13901594ad04e8a364614cfebfe3ca`

> Không dùng version cũ bên ngoài bundle để suy ra trạng thái hiện tại.  
> ECC / Superpowers / Matt Pocock / ByteByteGo chỉ được dùng như review lenses; không override source-of-truth EIU.

---

# 1. Executive Summary

v1.13 tiếp tục cải thiện mạnh và đã đóng thực sự nhiều vấn đề của vòng trước:

- Education physical fields đã chuyển sang nullable;
- Application prototype dùng exact `SubmissionSelector`;
- Responsive Create/Copy/Edit đã chặn inactive Participant;
- manual Submission status SQL helper đã chuyển sang Candidate-level/latest-safe;
- `set_internal_user_active` machine registry đã có participant reassignment guard;
- Responsive Prototype v1.9 đã tăng adversarial browser QA.

## Fresh validation evidence

### Full Handover

```text
PACKAGE VALIDATION — Full Handover v1.13 / Design v1.8 / Responsive v1.9
TOTAL=449
PASS=449
FAIL=0
```

### Design System

```text
TOTAL=73
PASS=73
FAIL=0
```

### Responsive Prototype

```text
TOTAL=99
PASS=99
FAIL=0
```

### Clean-package manifest verification

Tôi re-extract ZIP sạch và chạy manifest verifier **trước khi sửa/chạy generated evidence**:

```text
MANIFEST VERIFICATION PASS
checks=517
failures=0
```

Package integrity gốc là tốt.

Tuy vậy, manual semantic/database review vẫn tìm thấy **3 blocker thực** mà 449 checks chưa bắt.

---

# 2. Gate Recommendation

| Layer | Reviewer assessment |
|---|---|
| Business Logic Core v1.2 | **Giữ FROZEN** |
| Design System v1.8 | **CURRENT / REVIEWED** |
| Responsive Prototype v1.9 | **Gần Owner Visual UAT** |
| Technical Architecture v1.13 | **TARGETED AMENDMENT REQUIRED / NOT FROZEN** |
| Implementation Gate | **NOT YET PASS** |
| Production Ready | **NO** |

Không cần redesign architecture.

---

# 3. Findings Summary

## P0 — đóng trước Technical Freeze

| ID | Finding |
|---|---|
| **P0-01** | Education fields nullable theo contract, nhưng DB active-master trigger vẫn reject Education row có `qualification_id = NULL` |
| **P0-02** | `bulk_change_interview_schedule_status` chưa inherit/declare Active-Participant operational guard như single status path |
| **P0-03** | Current `05_HR_INTERVIEW_PAGE.md` còn hai rule khác nhau cho Application Reactivate: non-elapsed-only vs every resource-blocking child |

## P1 — đóng trước implementation freeze / final handoff

| ID | Finding |
|---|---|
| P1-01 | CURRENT machine/docs vẫn có baseline/version drift (`validation_contract`, critical-control registry, README, semantic gate, Responsive README) |
| P1-02 | Dedicated `set_internal_user_active()` contract chưa ghi participant guard ngay tại command section |
| P1-03 | Bulk Interview status acceptance mapping chưa chứng minh operational Participant eligibility |
| P1-04 | Semantic validator kiểm “canonical token exists” nhưng chưa loại legacy contradictory sentence trong same CURRENT file |
| P1-05 | Responsive README vẫn tự nhận v1.8 / Full v1.12 dù executable artifact là v1.9 / Full v1.13 |

## P2 — hardening

- `critical_control_registry.yaml` nên thêm Bulk Interview Schedule Status như critical control.
- Validation evidence generation nên tránh ghi benign subprocess `stderr` vào PASS output.
- Nên làm verification workflow không phụ thuộc thứ tự giữa “rerun validator” và “manifest hash verification”.
- Consolidate current files in-place thay vì tiếp tục giữ old baseline heading/paragraph trong artifact CURRENT.

---

# 4. P0-01 — Education Optional Contract vẫn fail ở DB khi qualification = NULL

Đây là confirmed physical-schema contradiction.

## Validation Contract

`validation_contract.yaml`:

```yaml
education_rows:
  max_items: 20
  min_items: 0
  required_fields: []
```

Nghĩa là:

- Education có thể có 0 row;
- khi có row, contract **không freeze field nào là mandatory**.

## SQL table v1.13

`submission_education` đã sửa đúng thành:

```sql
period_text text,
qualification_id uuid references ...,
major text,
institution text
```

Tất cả business fields đều nullable.

Đây là sửa đúng.

## Nhưng active-master trigger vẫn sai với nullable qualification

`private.validate_active_master_references()` hiện có nhánh:

```sql
elsif tg_table_name='submission_education' then
  if tg_op='INSERT'
     or new.qualification_id is distinct from old.qualification_id
  then
    select is_active ...
    where qualification_id=new.qualification_id;

    if coalesce(ok,false)=false then
      raise 'INACTIVE_QUALIFICATION_NOT_SELECTABLE';
    end if;
  end if;
```

### Scenario hợp lệ theo contract

Candidate thêm Education row:

```text
Institution = Eastern International University
Major       = Nursing
Qualification = NULL
Period = NULL
```

UI/Validation Contract: **valid**.

DB trigger:

```text
INSERT => condition true
qualification_id=NULL => no master row found
ok=NULL => coalesce(false)
→ INACTIVE_QUALIFICATION_NOT_SELECTABLE
```

Tức DB vẫn ngầm biến Qualification thành required.

## Fix

Giống các nullable master references khác:

```sql
if new.qualification_id is not null
   and (
     tg_op='INSERT'
     or new.qualification_id is distinct from old.qualification_id
   )
then
   ...
end if;
```

Nếu `qualification_id IS NULL`:

```text
skip active-master validation
```

## Acceptance cần thêm

```text
AC-EDU-NULL-01
Education row with qualification_id=NULL and another optional field populated → accepted.

AC-EDU-NULL-02
Education row with inactive non-null qualification_id → rejected.

AC-EDU-NULL-03
Historical unchanged inactive qualification remains readable/operable.
```

## Validator

Không chỉ check:

```text
education columns are nullable
```

mà phải test nullable-reference guard semantics.

**Severity: P0 — contract-valid payload can fail physical DB.**

---

# 5. P0-02 — Bulk Interview Schedule Status có thể bỏ qua Active Participant guard

Đây là cross-layer command-parity gap.

## Frozen operational invariant

v1.13 đã xác định rõ:

> Không trusted mutation nào được làm Interview trở thành `resource_blocking` nếu current Participant map tới inactive Internal User.

Stable error:

```text
CURRENT_PARTICIPANT_INACTIVE_REASSIGN_REQUIRED
```

## Single paths đã đúng

`save_interview_schedule` registry:

```yaml
side_effects:
  - validate_current_participants_operationally_eligible
  - shared_candidate_room_interviewer_conflict_recheck
```

`change_interview_schedule_status`:

```yaml
side_effects:
  - validate_current_participants_operationally_eligible
  - shared_candidate_room_interviewer_conflict_recheck
```

`reactivate_interview` và Application Reactivate cũng có equivalent guard.

## Bulk path chưa parity

`bulk_change_interview_schedule_status` hiện:

```yaml
side_effects:
  - shared_schedule_conflict_recheck
  - normalize_format_reason_fields
```

Không có:

```text
validate_current_participants_operationally_eligible
```

Guarantees cũng chỉ:

```text
ALL_OR_NOTHING
exact_interview_selection
```

## Contract prose

Batch section nói:

```text
transition that activates resource blocking
uses Candidate/Room/Interviewer conflict framework
```

nhưng không explicitly yêu cầu:

```text
all current Participants still Active
```

Trong architecture này, Active Participant validation là **separate operational invariant**, không phải chỉ một “conflict type”.

## Risk scenario

1. Interview = CANCELLED.
2. Participant X vẫn current.
3. X bị Inactive lúc Interview dormant.
4. HR bulk-select Interview và đổi status CANCELLED → SCHEDULED.
5. Batch path chỉ conflict-check Candidate/Room/Interviewer.
6. Interview trở resource-blocking.
7. X không thể login / không có contextual access.

Single status path sẽ block; bulk path có thể không.

## Fix

Registry:

```yaml
bulk_change_interview_schedule_status:
  side_effects:
    - validate_current_participants_operationally_eligible
    - shared_candidate_room_interviewer_conflict_recheck
    - normalize_format_reason_fields
  guarantees:
    - ALL_OR_NOTHING
    - exact_interview_selection
    - no_resource_blocking_interview_with_inactive_current_participant
```

Contract:

```text
For every selected Interview whose transition would become resource_blocking:
1. lock Interview;
2. validate every current Participant is Active;
3. acquire resource locks;
4. re-read participant set;
5. repeat eligibility if set changed;
6. conflict-check Candidate/Room/Interviewer;
7. mutate.
```

Acceptance:

```text
AC-PART-OPER-BULK-01
One selected CANCELLED Interview has inactive current Participant
→ entire bulk status batch aborts
→ no selected Interview changes.
```

Registry acceptance nên map cả:

```text
AC-BULK-01
AC-PART-OPER-02
AC-PART-OPER-BULK-01
```

**Severity: P0 — alternate batch path can violate a frozen operational security invariant.**

---

# 6. P0-03 — Application Reactivate vẫn có hai canonical meanings trong cùng CURRENT file

Canonical v1.13 ở các nguồn chính:

`48_IDEMPOTENCY_CONCURRENCY_SPEC.md`:

```text
reactivation_conflict_relevant
=
resource_blocking AND end_at > transaction_now
```

Application Reactivate:

```text
recheck non-elapsed children only
fully elapsed past-only overlaps do not block lifecycle recovery
```

`13_ACCEPTANCE... AC-APP-REACT-05` cũng đúng:

```text
every non-elapsed child
fully elapsed overlaps do not block
```

## Nhưng `05_HR_INTERVIEW_PAGE.md` vẫn tự mâu thuẫn

Trong section Reactivation:

```text
Reactivation ...
revalidates only non-elapsed children that would become
reactivation_conflict_relevant
```

Đúng.

Nhưng cuối same CURRENT/NORMATIVE file, section:

```text
## Canonical schedule predicates
...
Application Reactivate re-checks every child
that would become resource-blocking before commit.
```

Câu này lại bao gồm fully elapsed children.

## Failure scenario

Past Interview A:

```text
01/08 09:00–10:00
```

Historical record B overlaps same resource:

```text
01/08 09:30–10:30
```

Ngày 03/09 HR Reactivate Application.

Interpretation A:

```text
non-elapsed only
→ past overlap ignored
→ Reactivate succeeds
```

Interpretation B:

```text
every resource-blocking child
→ past overlap rechecked
→ Reactivate may fail
```

Hai developer đọc cùng file có thể implement khác nhau.

## Fix

Replace final line with exact canonical wording:

```text
Application Reactivate re-checks every NON-ELAPSED child
that would become reactivation_conflict_relevant
(resource_blocking AND end_at > transaction_now).
Fully elapsed historical intervals do not block lifecycle recovery.
```

Không giữ old phrase để “clarification phía trên thắng”.

## Validator

Semantic check phải fail legacy phrase:

```text
Application Reactivate re-checks every child that would become resource-blocking
```

trong CURRENT/NORMATIVE source.

**Severity: P0 — same current source has two outcomes for the same transaction.**

---

# 7. P1-01 — Current machine/source baseline drift vẫn còn

v1.13 source registry đúng:

```text
Technical v1.13
Design v1.8
Responsive v1.9
Review 89
Gate 90
```

Nhưng một số CURRENT/machine artifacts chưa sync.

## `validation_contract.yaml`

```yaml
version: '1.11'

current_baseline:
  full_handover: '1.10'
  technical_architecture: '1.10'
  design_system: '1.8'
  responsive_prototype: '1.6'
```

Tôi không coi `version: 1.11` tự động là lỗi nếu đó là schema-contract revision riêng.

Nhưng `current_baseline` rõ ràng đã stale.

## `critical_control_registry.yaml`

```yaml
baseline:
  Full Handover v1.12 / Responsive Prototype v1.8
```

Current phải là:

```text
Full v1.13 / Responsive v1.9 / Design v1.8
```

## `00_README.md`

Cuối file vẫn có:

```text
## Current review path — v1.12
```

và:

```text
Current technical normative modules extend through doc 88
```

nhưng current normative Review/Gate là 89/90.

## `70_SEMANTIC_VALIDATION_GATE.md`

Ngay đầu:

```text
Current expected package versions = Technical v1.13 / Design v1.8
```

nhưng item 19 lại nói:

```text
Version coherence:
Technical v1.12 / Design v1.8 / Responsive v1.9
```

Tự mâu thuẫn.

## `53_FINAL_CONSISTENCY_VALIDATION.md`

Current text nói Responsive v1.9 nhưng final-delivery path vẫn trỏ:

```text
responsive_prototype/RESPONSIVE_BROWSER_QA_v1.8.md
```

## `responsive_prototype/README.md`

Header:

```text
Responsive Clickable Prototype v1.8
```

Authority:

```text
Full Handover v1.12
Design System v1.8
```

Trong khi:

`VERSION.md` đúng:

```text
Responsive v1.9
Full Handover v1.13
Design v1.8
```

## Why this matters

Package v1.13 đã trở thành AI/coding-agent handover.

Một machine source/current README không nên yêu cầu agent tự suy luận:

```text
“dòng mới thắng dòng cũ”
```

## Fix

Sync all baseline declarations.

Tốt hơn:

- machine artifacts derive baseline từ `source_registry.yaml`;
- validator không hard-code baseline ở nhiều file;
- CURRENT README generated version block nên lấy từ một source.

**Severity: P1 source governance.**

---

# 8. P1-02 — Dedicated `set_internal_user_active()` section chưa self-contained

v1.13 alignment nói machine registry đã thêm:

```text
block_nonelapsed_resource_blocking_current_participant_without_reassignment
```

SQL trigger cũng đúng:

```text
FUTURE_INTERVIEW_PARTICIPANT_REASSIGN_REQUIRED
```

Acceptance cũng có participant lifecycle rule.

Nhưng dedicated command section:

```text
set_internal_user_active(...)
```

chủ yếu nói:

- target HR/Root restrictions;
- Active Application owner guard;
- session/authorization refresh;
- audit.

Nó chưa ghi ngay tại command:

```text
deactivation is also blocked if the user is a current Participant
on a non-elapsed resource-blocking Interview
```

Một later generic section trong file có nói rule này, nhưng current-source consolidation principle của chính package yêu cầu canonical behavior ở nơi implementer tìm command.

## Fix

Add directly to command preconditions:

```text
Before any active=true→false:
- block Active Application owner unless reassigned;
- block current Participant of any non-elapsed resource-blocking Interview unless removed/replaced.
```

**Severity: P1.**

---

# 9. P1-03 — Bulk status acceptance traceability còn quá generic

Registry:

```text
bulk_change_interview_schedule_status
acceptance:
  - AC-BULK-01
```

`AC-BULK-01` chỉ chứng minh:

```text
visible bulk action has named command + declared atomicity
```

Nó không chứng minh:

- Participant Active guard;
- CANCELLED→operational behavior;
- Candidate conflict;
- Room conflict;
- Interviewer conflict;
- all-or-nothing rollback after one failure.

## Fix

Map behavior-specific acceptance:

```text
AC-BULK-SCH-01
AC-PART-OPER-BULK-01
AC-SCH-CANDIDATE-BULK-01
AC-SCH-ROOM-BULK-01
AC-SCH-INTERVIEWER-BULK-01
```

At minimum include operational eligibility plus one full rollback test.

**Severity: P1 evidence gap.**

---

# 10. P1-04 — Semantic validator still checks presence more than exclusion

`70_SEMANTIC_VALIDATION_GATE.md` says:

```text
CURRENT/NORMATIVE modules state canonical behavior in place
and do not rely on later clarification
```

Yet current package still contains:

```text
05: non-elapsed Reactivate rule
AND
05: every resource-blocking child rule
```

and validator reports 449/449 PASS.

Likewise version coherence passes despite stale current-baseline lines.

## Validator improvement

For important canonical rules, test both:

### Required presence

```text
reactivation_conflict_relevant
non-elapsed
fully elapsed do not block
```

### Forbidden legacy patterns

```text
"Application Reactivate re-checks every child that would become resource-blocking"
```

Same principle for version labels:

```text
CURRENT source may contain historical v1.12 only inside an explicitly tagged historical/changelog context.
```

**Severity: P1 validator quality.**

---

# 11. P1-05 — Responsive Prototype README authority is stale even though executable v1.9 is correct

Responsive behavior itself is much better and Browser QA is strong:

```text
99/99 PASS
```

`VERSION.md` correctly says:

```text
v1.9
Full Handover v1.13
Design v1.8
```

But README still presents itself as:

```text
Responsive Clickable Prototype v1.8
Authority: Full Handover v1.12
```

This is particularly risky because README is the natural “start here” file.

## Fix

Update:

```text
Responsive Prototype v1.9
Authority: Full Handover v1.13 + Design v1.8
```

Also rename:

```text
Start here for v1.8 review
```

to v1.9.

**Severity: P1 before Owner UAT handoff.**

---

# 12. P2 — Validation evidence / manifest workflow robustness

Clean ZIP manifest verification:

```text
517 checks / 0 failures
```

So package integrity is valid.

During my review I then reran `validate_package.py`.

In this runtime, a benign Python startup warning from the nested All-in-One check was captured into PASS detail and written into `PACKAGE_VALIDATION.txt`.

After that, manifest verification reported only:

```text
PACKAGE_VALIDATION.txt size mismatch
PACKAGE_VALIDATION.txt SHA mismatch
```

This is expected because a manifest-tracked generated file was rewritten.

## Recommendation

To make external verification less order-sensitive:

Option A:

```text
verify manifests first
then run validators
```

and document the order explicitly.

Better Option B:

```text
validator --check / --no-write
```

for reviewers.

Or:

```text
generated evidence output goes to temp/stdout;
release process explicitly regenerates evidence then manifests.
```

Also avoid embedding arbitrary subprocess `stderr` in a PASS detail line unless it is actually relevant to the check.

**Severity: P2 verification ergonomics; original ZIP integrity is PASS.**

---

# 13. Design System v1.8 Review

Design validator:

```text
73/73 PASS
```

I did not find a new design-system blocker.

Verified good:

- Application Inbox width 1560px
- Interview width 1480px
- HR Report width 1610px
- Drawer formula consistent
- Candidate EDIT privacy states
- exact SubmissionSelector component
- Users/Permissions visibility separation
- 16px operational text
- 44px target baseline
- 200% zoom / 400% reflow acceptance
- sticky table focus
- status badge/menu accessibility
- responsive prototype authority target = v1.9

Most current issues are Handover/DB/source-governance, not Design System.

---

# 14. Responsive Prototype v1.9 Review

Browser QA:

```text
99/99 PASS
```

Important corrected behaviors are real:

- Phase-1 nav hides FUTURE_HIDDEN routes;
- Candidate lifecycle separate from Submission workflow;
- derived Submission statuses are not manually selectable;
- Candidate/Room/Interviewer conflict cases all block;
- adjacent `[start,end)` allowed;
- CANCELLED ignored;
- Copy fills structurally-empty target Round1;
- Copy records provenance;
- exact SubmissionSelector distinguishes multiple Submissions;
- Create/Copy inactive Participant tests block correctly;
- Candidate Education UI no longer invents required fields;
- zero Education rows allowed;
- CV remains required;
- staged document Cancel/Replace behavior tested;
- Final Decision Source uses decision-specific semantics.

The major prototype issue now is mainly **README authority metadata**, not the effective executable behavior.

---

# 15. Recommended Fix Order

## Batch 1 — P0

1. Fix Education active-master trigger for nullable `qualification_id`.
2. Add Active Participant eligibility to `bulk_change_interview_schedule_status`.
3. Remove the legacy “every resource-blocking child” Application Reactivate sentence from `05`.

## Batch 2 — machine/source coherence

4. Refresh `validation_contract.current_baseline`.
5. Refresh `critical_control_registry.baseline`.
6. Fix `00_README` v1.12 review-path label and doc-88 range.
7. Fix `70` item 19 Technical v1.12.
8. Fix `53` Responsive QA path v1.8.
9. Fix Responsive README to v1.9 / Full v1.13.

## Batch 3 — command/test completeness

10. Add participant deactivation guard directly to `set_internal_user_active()` command section.
11. Add behavior-specific batch schedule acceptance tests.
12. Add Bulk Interview Schedule Status to critical-control registry.
13. Extend semantic validator with forbidden-legacy-pattern checks.

## Batch 4 — evidence ergonomics

14. Add no-write/check mode or define manifest-before-validator verification order.
15. Rebuild evidence/manifests.
16. Re-extract final ZIP and rerun:
    - manifest verification;
    - Full validator;
    - Design validator;
    - Responsive v1.9 browser QA.

---

# 16. Proposed Gate Status

```text
Business Logic Core v1.2
= FROZEN
```

```text
Design System v1.8
= CURRENT / REVIEWED
```

```text
Responsive Prototype v1.9
= READY FOR OWNER VISUAL UAT AFTER METADATA/SOURCE SYNC
```

```text
Technical Architecture v1.13
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

# 17. Final Assessment

v1.13 is **very close to Technical Freeze** and clearly stronger than previous iterations.

No architecture redesign is needed.

The remaining highest-value work is precise:

1. close one real nullable-Education DB defect;
2. close batch/single operational Participant parity;
3. remove one remaining Reactivation semantic contradiction;
4. make all machine/current baselines actually current;
5. strengthen validator exclusion checks.

The target before Freeze remains:

> **One business behavior → one canonical meaning → one permission → one command path → one transaction/invariant → one acceptance proof.**

v1.13 is close, but the three P0 findings above should be closed first.

---

# Appendix A — Fresh Evidence

```text
ZIP SHA-256
c7df7d4c2bb3860835f10a9568f2c4050a13901594ad04e8a364614cfebfe3ca
```

```text
Clean Manifest Verification
517 checks
0 failures
```

```text
Full Handover
449 / 449 PASS
```

```text
Design System
73 / 73 PASS
```

```text
Responsive Prototype v1.9
99 / 99 PASS
```

---

# Appendix B — Suggested Acceptance Additions

```text
AC-EDU-NULL-01
Nullable qualification Education row is valid.

AC-EDU-NULL-02
Non-null inactive qualification is rejected.

AC-PART-OPER-BULK-01
Bulk CANCELLED→operational status change with one inactive current Participant
aborts entire batch.

AC-REACT-CANON-01
Fully elapsed historical intervals never block Application Reactivate.

AC-SOURCE-BASELINE-01
All CURRENT machine baseline declarations equal source_registry current versions.

AC-RESP-AUTH-01
Responsive README/VERSION authority both equal Full v1.13 / Design v1.8 / Responsive v1.9.
```
