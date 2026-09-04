# EIU Recruitment — Independent Review of Implementation Planner Pack v1.0
## Reviewed against Full Handover v1.15

**Ngày review:** 03/09/2026

## 1. Baseline được review

### Source of truth

`App_Tuyen_Dung_EIU_Full_Handover_v1.15.zip`

SHA-256:

`7c725d9041129e4ce672537d306353fe5f7bb05dea7c6c3614290efb588750e9`

### Planner output được kiểm chứng

`EIU_Recruitment_Implementation_Planner_Pack_v1.0.zip`

SHA-256:

`99c2aa9f278caa2a588c35534842bfebdc7ad3c9348f17078963f79184f017fb`

Review này xem **Full Handover v1.15 là source of truth**. Planner Pack chỉ là planning artifact cần được kiểm chứng ngược lại source.

---

# 2. Independent Verification Evidence

Tôi đã chạy lại trực tiếp trên bundle v1.15:

```text
Manifest verification:
541 checks / 0 failures
```

```text
Full Handover validator:
497 / 497 PASS
```

```text
Design System v1.8:
73 / 73 PASS
```

```text
Responsive Prototype v1.10:
107 / 107 PASS
```

Các con số Planner báo cáo là **chính xác**.

Tôi cũng kiểm tra programmatically Planner Traceability:

```text
command_registry commands = 58
Planner TRACEABILITY_MATRIX exact trusted-command rows = 58
missing commands = 0
```

Đối chiếu từng command:

```text
permission mismatch = 0
missing command-registry Acceptance IDs = 0
```

Tất cả Acceptance ID mà Planner viện dẫn trong pack:

```text
Planner AC references = 130 unique IDs
unknown/nonexistent AC IDs = 0
```

Đây là evidence mạnh cho thấy Planner đã thực hiện traceability nghiêm túc, không chỉ viết một bản summary bằng prose.

---

# 3. Executive Verdict

## Planner quality

```text
PLANNER ARTIFACT QUALITY:
APPROVED_WITH_REQUIRED_EDITS
```

Planner đã làm đúng phần lớn protocol:

- pin đúng ZIP/hash;
- đọc đúng `source_registry.yaml`;
- tách CURRENT/HISTORICAL tốt;
- không biến prototype thành business authority;
- audit code sẵn bằng ADOPT/ADAPT/DISCARD/REFERENCE_ONLY;
- trace đầy đủ 58 command;
- permission/acceptance mapping chính xác;
- vertical-slice strategy hợp lý;
- strict TDD tập trung đúng vùng rủi ro;
- first Executor prompt được đánh dấu `DRAFT_ONLY_NOT_AUTHORIZED`;
- không tự cho phép coding.

## Coding authorization

```text
EXECUTOR AUTHORIZATION:
BLOCKED_SPEC_OR_PLANNING_GAP
```

**Không gửi prompt hiện tại cho Coding Executor để code production.**

Nguyên nhân chính là source v1.15 hiện **chưa tự định nghĩa được một sequence Freeze → Implementation không mâu thuẫn**, và còn một command-mapping ambiguity Planner chưa phát hiện.

---

# 4. P0-01 — Freeze / Implementation Gate hiện bị circular và Gate 94 còn tự mâu thuẫn nội bộ

Planner đã phát hiện GAP-001 đúng hướng, nhưng finding cần được viết chính xác hơn.

## Source A — Product Architecture

`01_PRODUCT_SCOPE_AND_ARCHITECTURE.md` §6:

```text
Technical Architecture cần pass Technical Closure Gate
trước production coding.
```

Tức:

```text
Technical Gate / Freeze
→ production coding
```

## Source B — Scope & Open Items

`14_SCOPE_AND_OPEN_ITEMS.md` § Technical items before Technical Architecture Freeze:

trước Freeze yêu cầu:

```text
executable RLS/GRANT migrations + adversarial tests
RPC/command implementation + integration tests
schedule/document/concurrency race tests
schema migration clean-install test
Storage policies + two-phase upload tests
Auth implementation tests
query plan/performance
backup/restore rehearsal
...
```

Đây là **production implementation evidence**, không thể có đầy đủ nếu production coding chưa được phép bắt đầu.

Tức file 14 lại yêu cầu:

```text
production implementation
→ Technical Freeze
```

## Gate 94 còn có internal contradiction

`94_TECHNICAL_PRECODE_GATE_V1_15.md` line 19:

```text
Technical Freeze still requires ...
actual production implementation evidence
(migrations/RLS/race/storage/backup/deployment tests).
```

Nhưng line 21–22 lại ghi:

```text
Production migration evidence still required AFTER Technical Freeze
```

và liệt kê gần như cùng nhóm:

```text
clean install
FK/index audit
adversarial RLS
concurrency/race
Storage integration
EXPLAIN ANALYZE
backup/restore
deployment rollback
```

Như vậy source hiện có ba sequence không thể đồng thời đúng:

```text
A:
Technical Freeze
→ Coding

B:
Coding evidence
→ Technical Freeze

C:
Technical Freeze
→ implementation/migration evidence
```

## Independent assessment

Planner **đúng khi không tự resolve** và không cho Executor code.

Nhưng GAP-001 của Planner mới cite `01` + Gate 94 line 19. Cần mở rộng thành:

```text
01 §6
vs
14 §23–33
vs
94 line 19
vs
94 line 21–22
```

để owner sửa đúng root cause.

## Recommended governance sequence

Tôi khuyến nghị source tiếp theo định nghĩa rõ 4 gate:

```text
1. SPEC / TECHNICAL ARCHITECTURE FREEZE
   - source semantic review PASS
   - current validators PASS
   - Owner Visual UAT PASS
   - no blocking source contradiction
   ↓

2. APPROVED FOR IMPLEMENTATION
   - Coding Executor được phép bắt đầu Slice 00
   ↓

3. IMPLEMENTATION VALIDATION / MIGRATION FREEZE
   - real migrations
   - RLS adversarial
   - command integration
   - race/concurrency
   - Storage/malware
   - query plans
   - backup/restore
   - deployment rollback
   ↓

4. PRODUCTION UAT / PRODUCTION READY
```

Khi đó:

```text
Technical Architecture FROZEN
≠ Implementation validated
≠ Production Ready
```

và hết circular dependency.

**Severity: P0 — blocks production coding.**

---

# 5. P0-02 — Copy Interview trusted-command mapping đang mâu thuẫn; Planner đã tự chọn một interpretation

Đây là finding Planner **bỏ sót**.

## Source 37

`37_BACKEND_COMMAND_CONTRACTS.md` có heading:

```text
### copy_interview_schedule()
```

và mô tả Save behavior:

```text
same Application
→ create/fill next round

different Application
→ fill structurally empty default Round1
   or create next round
```

Cách trình bày này khiến nó trông như một trusted backend command.

## Nhưng command_registry không có command đó

Current registry có:

```text
58 commands
```

và **không có**:

```text
copy_interview_schedule
```

## Command Coverage Matrix lại nói khác

`55_COMMAND_COVERAGE_MATRIX.md`:

```text
Copy schedule draft
→ client draft + final normal save command
→ no DB mutation until Save
```

Điều này nói Copy **không phải một dedicated registry command**.

## Hard architecture rule

Current architecture cũng nói:

```text
One UI mutation
→ one explicit trusted backend command
```

Copy Save là một production mutation có:

- target-round selection;
- possible round creation;
- structurally-empty predicate;
- Participant active validation;
- schedule conflict validation;
- provenance;
- locking/idempotency.

Do đó "final normal save command" phải được định nghĩa **rất chính xác** nếu không có dedicated Copy command.

## Planner inconsistency

Planner `RULE_LEDGER.md` RL-024 ghi:

```text
Trusted Command:
copy_interview_schedule
```

nhưng `TRACEABILITY_MATRIX.md` chỉ trace đúng 58 registry commands và không có Copy command row.

Nghĩa là Planner output hiện tự có:

```text
Rule Ledger
→ copy_interview_schedule is trusted command

Traceability Matrix / registry
→ command does not exist
```

Planner đã vô tình làm điều protocol cấm:

> tự chọn/reconcile một current-source ambiguity.

## Required resolution

Không để Planner tự quyết.

Source phải chọn một trong hai:

### Option A — Dedicated trusted command

Thêm:

```text
copy_interview_schedule
```

vào:

- `command_registry.yaml`
- `55_COMMAND_COVERAGE_MATRIX.md`
- command contract
- permission
- side effects
- lock/transaction semantics
- idempotency
- acceptance IDs
- critical-control mapping.

Đây là option tôi thấy dễ audit nhất vì Copy có orchestration riêng.

### Option B — No dedicated command

Nếu owner/architecture cố ý dùng existing command:

source phải ghi exact:

```text
Copy UI Save
→ <EXACT EXISTING COMMAND NAME>
```

và chứng minh command đó atomically xử lý:

```text
fill existing default Round1
OR create next round
+ schedule
+ participant guard
+ provenance
+ conflicts
+ audit
```

Không được dùng phrase generic:

```text
final normal save command
```

## Planner update

Cho đến khi source chọn:

```text
GAP-COPY-COMMAND
Type: SPEC_CONFLICT
Blocks: Slice 04
```

và RL-024 không được tự ghi `copy_interview_schedule` là trusted command.

**Severity: P0 before Technical Freeze; does not by itself block Slice 00, but blocks a clean global implementation contract.**

---

# 6. P1-01 — Planner chưa output exact required `PLANNER_DECISION`

Planner Master Protocol yêu cầu kết thúc bằng **exactly one**:

```text
PLANNER_DECISION: READY_FOR_INDEPENDENT_REVIEW
PLANNER_DECISION: BLOCKED_SPEC_CONFLICT
PLANNER_DECISION: BLOCKED_FREEZE_GATE
PLANNER_DECISION: BLOCKED_MISSING_SOURCE
PLANNER_DECISION: BLOCKED_TOOLING_EVIDENCE
```

Trong uploaded Planner Pack, không tìm thấy token:

```text
PLANNER_DECISION:
```

Planner Report có prose `## Planner Decision`, nhưng không có machine-readable exact status.

Với current findings, exact status nên là:

```text
PLANNER_DECISION: BLOCKED_SPEC_CONFLICT
```

vì GAP-001 là source conflict và blocks execution.

Nếu muốn tách planning readiness khỏi execution readiness, Planner Report có thể thêm:

```text
PLANNING_ARTIFACT_STATUS: READY_FOR_INDEPENDENT_REVIEW
PLANNER_DECISION: BLOCKED_SPEC_CONFLICT
```

nhưng không thay thế mandatory final token.

**Severity: P1 — protocol compliance.**

---

# 7. P1-02 — `14_SCOPE_AND_OPEN_ITEMS.md` còn stale Responsive Prototype v1.9; Planner bỏ sót

Current baseline:

```text
Responsive Prototype v1.10
```

nhưng current/normative:

`14_SCOPE_AND_OPEN_ITEMS.md` line 33 vẫn ghi:

```text
responsive ... UAT using bundled Prototype v1.9
```

Planner đã bắt stale:

```text
design_system/START_HERE.txt
Full v1.12 / Responsive v1.8
```

nhưng chưa bắt stale v1.9 trong `14`.

Điều này quan trọng vì Planner tự khai:

```text
lossless rule extraction
current-source governance
```

và Source Inventory đã đọc file 14.

## Required update

Thêm source-governance gap:

```text
GAP-SOURCE-RESP-VERSION
Source: 14_SCOPE_AND_OPEN_ITEMS.md
Current expected: Responsive Prototype v1.10
Actual stale text: v1.9
Blocks: NO for planning; fix before Freeze/current package release.
```

Validator cũng nên scan current normative responsive baseline assertions.

**Severity: P1.**

---

# 8. P1-03 — Design `START_HERE.txt` stale: Planner phát hiện đúng, nhưng classification nên rõ hơn

Planner GAP-002 đúng:

`design_system/START_HERE.txt` vẫn ghi:

```text
Full Handover v1.12
Responsive Prototype v1.8
```

trong khi current:

```text
Full v1.15
Design v1.8
Responsive v1.10
```

Điểm tốt:

- Planner không để stale file override root authority.
- Executor Slice00 không list Design `START_HERE` như implementation source.
- Planner đưa gap ra review.

Tuy nhiên đây chủ yếu là:

```text
SOURCE_GOVERNANCE / STALE_ENTRYPOINT
```

hơn là semantic business conflict, vì:

- root `START_HERE` đúng;
- `source_registry` đúng;
- Design `00_README` đúng;
- Design source order nói current Business/Technical Handover đứng trên.

Tôi vẫn khuyến nghị sửa source, nhưng không cần coi đây là blocker architecture ngang GAP-001.

**Severity: P1 source hygiene.**

---

# 9. P1-04 — Vertical Slice Plan dùng shorthand command thay vì exact registry IDs

Global `TRACEABILITY_MATRIX` làm rất tốt: 58/58 exact commands.

Nhưng `VERTICAL_SLICE_PLAN.md` lại dùng các mô tả như:

```text
set/bulk latest status
set/bulk Candidate active
create/bulk Application
owner
reactivate/delete Application

create_next_round
save/status/reactivate/delete Interview
participant commands
copy

change/bulk report status
master commands
enqueue/bulk email
```

Điều này yếu hơn tiêu chuẩn Planner Protocol:

```text
task-specific exact command list
```

và đã góp phần che mất Copy ambiguity.

## Required update

Mỗi Slice phải có:

```text
Commands — Exact registry IDs
```

Ví dụ Slice 03:

```text
open_submission
update_submission_by_hr
mutate_submission_documents_by_hr
set_submission_manual_status
bulk_set_latest_submission_manual_status
set_candidate_active
bulk_set_candidate_active
create_or_update_application
bulk_create_or_update_applications
update_application_hr_owner
reactivate_application
delete_or_inactivate_application
```

Slice 04 phải liệt kê exact commands và Copy phải là `SPEC_CONFLICT` cho đến khi source resolve.

Có thể thêm một field riêng:

```text
Non-command helpers/jobs:
cleanup_abandoned_uploads
...
```

để không trộn job/helper với trusted UI command.

**Severity: P1 — planner precision.**

---

# 10. P1-05 — Slice 00 prompt nên đọc thêm gate/scope sources trực tiếp

Current Slice00 prompt đọc:

- root START_HERE
- source_registry
- 01
- 12
- NFR/security/deployment
- 93/94
- machine contracts

Đây là một source list tốt.

Nhưng vì chính execution authorization là blocker, authorized reissue nên thêm trực tiếp:

```text
review_pack/14_SCOPE_AND_OPEN_ITEMS.md
review_pack/52_TECHNICAL_GATE_STATUS.md
```

Hai file này chứa:

- current Technical/Implementation status;
- pre-Freeze items;
- current prototype status;
- implementation boundary.

Khi source gate được sửa, Slice00 Executor không nên chỉ dựa vào 01 + 94 để quyết định authorization.

**Severity: P1 before authorized reissue.**

---

# 11. P2 — `15_ALL_IN_ONE_SPEC` classification wording

Planner Source Inventory gọi:

```text
15_ALL_IN_ONE_SPEC.md
→ Generated current non-normative entrypoint/evidence
```

Nhưng `source_registry.current_entrypoints` không liệt kê file 15.

Planner ở các chỗ khác đã correctly nói:

```text
REFERENCE_ONLY
generated convenience
do not edit manually
```

Nên sửa description đơn giản thành:

```text
GENERATED_CURRENT / non-normative convenience reference
```

không gọi nó là current entrypoint.

**Severity: P2.**

---

# 12. Strengths — Những phần tôi APPROVE

## 12.1 Baseline pinning

Planner hash khớp source:

```text
7c725d9041129e4ce672537d306353fe5f7bb05dea7c6c3614290efb588750e9
```

Không reuse baseline cũ.

## 12.2 Validator evidence

Planner evidence khớp fresh independent runs:

```text
541 manifest
497 Full
73 Design
107 Responsive
```

Không bịa PASS.

## 12.3 Current/Historical governance

`SOURCE_INVENTORY` bao phủ toàn bộ document entries trong `source_registry.yaml`.

Independent check:

```text
source_registry documents absent from Planner inventory = 0
```

Planner hiểu đúng historical docs chỉ là evidence.

## 12.4 Trusted-command traceability

Đây là phần mạnh nhất.

Independent check:

```text
Registry trusted commands: 58
Traceability rows: 58
Missing registry command: 0
Permission mismatch: 0
Missing registry AC mapping: 0
```

Ngoại lệ Copy không phải registry command, và chính ngoại lệ này cần source resolution như P0-02.

## 12.5 Acceptance traceability

Planner references không có fabricated AC:

```text
unknown AC IDs = 0
```

## 12.6 Salvage strategy

Tôi đồng ý với hướng:

```text
Prototype JS domain logic → REFERENCE_ONLY
Prototype CSS/layout → ADAPT
Design → authority / ADAPT implementation
database_schema.sql → ADAPT into migrations
Machine contracts → ADOPT as contracts
Validators → ADOPT as supplementary CI
Historical → REFERENCE_ONLY
```

Đây chính xác là chiến lược phù hợp cho code có sẵn trong ZIP.

## 12.7 Vertical slices

Macro decomposition hợp lý:

```text
00 Foundation
01 Auth
02 Candidate
03 Application
04 Interview
05 Reports
06 Master/User
07 Async/Email/Cleanup
08 Hardening/Release
```

Đặc biệt Planner không làm:

```text
all frontend
→ all backend later
```

## 12.8 Test strategy

Planner tập trung strict TDD đúng vùng:

- RLS
- identity
- state
- concurrency
- batch
- upload
- privacy
- outbox
- lifecycle.

Không lạm dụng test-first cho CSS nhỏ.

## 12.9 First Executor prompt guard

Prompt Slice00 hiện:

```text
EXECUTION_STATUS: DRAFT_ONLY_NOT_AUTHORIZED
```

và:

```text
FILES CHANGED must be NONE
```

Tức dù user gửi nhầm prompt cho Executor hiện nay, instruction vẫn cố ngăn production coding.

Đây là thiết kế tốt.

---

# 13. Required Edits to Planner Pack

Tôi không yêu cầu Planner làm lại từ đầu.

Chỉ cần một revision có kiểm soát.

## Required Edit A — GAP-001

Rewrite GAP-001 với đủ source:

```text
01 §6
14 §23–33
94 line 19
94 line 21–22
```

và ghi rõ Gate 94 internal contradiction.

## Required Edit B — Copy command gap

Thêm:

```text
GAP-COPY-COMMAND
Type: SPEC_CONFLICT
```

Xóa assumption:

```text
RL-024 Trusted Command = copy_interview_schedule
```

cho đến khi source chọn command mapping.

## Required Edit C — stale v1.9 source

Thêm gap/source cleanup cho:

```text
14_SCOPE_AND_OPEN_ITEMS.md line 33
Prototype v1.9 → v1.10
```

## Required Edit D — exact Planner decision

Thêm:

```text
PLANNER_DECISION: BLOCKED_SPEC_CONFLICT
```

## Required Edit E — exact commands by Slice

Replace command shorthand with exact command registry IDs.

Separate:

```text
Trusted commands
Internal helpers/jobs
Client drafts
```

## Required Edit F — authorized Slice00 source list

Khi reissue prompt sau source freeze, thêm:

```text
14_SCOPE_AND_OPEN_ITEMS.md
52_TECHNICAL_GATE_STATUS.md
```

vào gate/source reading list.

---

# 14. Required Edits to Full Handover before Coding

Planner alone cannot fix these.

Source package mới nên sửa:

## Source Fix 1 — Gate sequencing

Define unambiguously:

```text
Technical Spec Freeze
→ Approved for Implementation
→ implementation evidence
→ Implementation/Migration Validation Gate
→ Production UAT
```

Move implementation evidence out of a contradictory "required both before and after Technical Freeze" state.

## Source Fix 2 — Copy command authority

Choose one exact production mutation mapping:

```text
Dedicated copy_interview_schedule
```

OR

```text
exact existing trusted command with fully specified atomic behavior
```

Do not retain:

```text
37 says command-like copy_interview_schedule
55 says final normal save command
registry says no copy command
```

## Source Fix 3 — Design START

Update:

```text
Full v1.15+
Responsive v1.10+
```

according to the new baseline.

## Source Fix 4 — Scope responsive version

Fix:

```text
14_SCOPE... Prototype v1.9
```

to current prototype version.

---

# 15. Recommended Next Sequence

Do **not** send the current Slice00 prompt to executor for coding.

Recommended sequence:

```text
1. Owner/source team fixes source gate + Copy command mapping + stale pointers.
2. Produce new Full Handover baseline (e.g. v1.16).
3. New source explicitly says:
   Technical Architecture = FROZEN
   Implementation Gate = READY TO IMPLEMENT
4. Re-run all source/design/responsive validators.
5. Planner re-pins the NEW ZIP/hash.
6. Planner updates Report/Traceability/Slices.
7. Planner regenerates authorized Slice00 prompt from new baseline.
8. Send updated Planner Pack + source ZIP back for one final independent review.
9. Only after approval → Coding Executor starts Slice00.
```

Do **not** manually edit only the old Executor prompt's line:

```text
DRAFT_ONLY_NOT_AUTHORIZED → AUTHORIZED
```

The entire prompt must be regenerated/revalidated from the new baseline.

---

# 16. Independent Review Outcome

## Planner artifact

```text
APPROVED_WITH_REQUIRED_EDITS
```

The planning method is strong and worth keeping. No need to restart the Planner process.

## Executor handoff

```text
BLOCKED_SPEC_OR_PLANNING_GAP
```

Reasons:

1. current v1.15 Freeze/implementation sequence is circular;
2. Copy mutation command mapping is unresolved;
3. current source is explicitly NOT FROZEN;
4. Planner revision items above should be closed before authorized prompt generation.

---

# 17. Bottom Line

The Planner has done a substantially good job.

The strongest evidence is not stylistic; it is structural:

```text
58/58 registry commands traced
0 permission mismatches
0 missing registry acceptance mappings
0 fabricated Acceptance IDs
```

So I would **not** replace this Planner output or ask it to rewrite everything.

I would ask it to perform a **targeted revision** after the source package is corrected.

The project is now at the point where the main risk is no longer "Planner missed most rules". The remaining risk is:

> **a few unresolved authority/gate boundaries could make a very precise Executor implement the wrong thing very precisely.**

Fix those boundaries first, then authorize Slice00.
