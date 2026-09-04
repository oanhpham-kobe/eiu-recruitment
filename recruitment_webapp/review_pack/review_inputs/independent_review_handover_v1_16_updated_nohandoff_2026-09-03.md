# EIU Recruitment — Independent Review
## Full Handover v1.16 — Freeze / Implementation Readiness

**Ngày review:** 03/09/2026

## 1. Source of Truth

Chỉ sử dụng bundle hiện tại:

`App_Tuyen_Dung_EIU_Full_Handover_v1.16.zip`

**SHA-256**

`851170ca71da01f64f24e052519ae48d9a710d9c3b1a655c489c85c14535e476`

Không dùng v1.15 hoặc Planner Pack cũ để suy ra trạng thái hiện tại.

---

# 2. Fresh Independent Evidence

## Manifest

```text
MANIFEST VERIFICATION PASS
checks=549
failures=0
```

## Full Handover

```text
PACKAGE VALIDATION
Full Handover v1.16
Design System v1.8
Responsive Prototype v1.10

TOTAL=502
PASS=502
FAIL=0
```

## Design System

```text
73 / 73 PASS
```

## Responsive Prototype

```text
107 / 107 PASS
```

Các evidence trên được chạy lại trực tiếp từ ZIP v1.16, không lấy số từ file snapshot.

---

# 3. Major v1.15 Findings — Independently Reverified as Closed

## 3.1 Freeze / Implementation circularity — CLOSED

v1.16 hiện tách rõ 4 gate:

```text
Gate 1 — Technical Specification Freeze
Gate 2 — Approved for Implementation
Gate 3 — Implementation Validation / Migration Freeze
Gate 4 — Production UAT / Production Ready
```

Current source ghi:

```text
Technical Architecture v1.16
= TECHNICAL SPECIFICATION FROZEN

Implementation Gate
= READY TO IMPLEMENT

Implementation Validation / Migration Freeze
= PENDING ACTUAL CODE EVIDENCE

Production Ready
= NO
```

Điểm quan trọng: production migration/RLS/RPC/race/storage/performance/backup/deployment evidence đã được chuyển đúng sang **post-code Gate 3**, không còn là circular prerequisite cho Technical Specification Freeze.

**Independent conclusion: CLOSED correctly.**

---

## 3.2 Copy Interview command authority — CLOSED at primary contract level

v1.16 đã tạo dedicated trusted command:

`copy_interview_schedule`

Command Registry hiện có **59 commands / 59 unique names**.

`copy_interview_schedule` có actor HR, permission `interviews.manage`, audit, idempotency, target-round resolution, Active Participant guard, Candidate/Room/Interviewer conflict recheck, provenance, Submission recalculation và Acceptance mapping.

`37_BACKEND_COMMAND_CONTRACTS.md` đã ghi rõ:

```text
Copy draft → client-only → no DB mutation
Save Copy → exactly copy_interview_schedule
```

`55_COMMAND_COVERAGE_MATRIX.md` cũng tách đúng draft và Save Copy.

**Independent conclusion: Primary Copy command ambiguity from v1.15 is CLOSED.**

---

## 3.3 Interview upload reservation parent/delete integrity — CLOSED

SQL v1.16 có:

```sql
upload_reservations_interview_fk
foreign key (interview_id)
references public.interviews(interview_id)
on delete restrict
```

và `upload_reservations_interview_idx`.

Delete command yêu cầu durable cleanup intent vào `storage_cleanup_queue` trước khi reservation bị remove và Interview hard-delete; cleanup-capture failure aborts delete.

**Independent conclusion: CLOSED correctly.**

---

## 3.4 Education nullable Qualification guard — CLOSED

DB trigger hiện chỉ active-master validate khi `qualification_id IS NOT NULL`.

**Independent conclusion: CLOSED correctly.**

---

## 3.5 Responsive single/bulk Schedule Status bypass — CLOSED

Responsive v1.10 QA hiện có adversarial evidence cho inactive Participant, Candidate conflict, Room conflict, Interviewer conflict, bulk rollback và adjacent interval.

Fresh browser suite: **107/107 PASS**.

**Independent conclusion: CLOSED in current prototype.**

---

# 4. Current Findings

## P0-01 — Copy command chưa được propagate đầy đủ vào canonical schedule-engine machine declarations

Đây là finding cần sửa **trước khi phát hành Executor prompt AUTHORIZED**.

### Primary source nói Copy dùng shared conflict engine

`37_BACKEND_COMMAND_CONTRACTS.md`:

```text
copy_interview_schedule
→ Active Participant guard
→ shared deterministic Candidate/Room/Interviewer resource-lock + conflict framework
```

`command_registry.yaml`:

```yaml
copy_interview_schedule:
  side_effects:
    - validate_current_participants_operationally_eligible
    - shared_candidate_room_interviewer_conflict_recheck
```

### Nhưng `app_spec.yaml` chưa liệt kê Copy

Current:

```yaml
schedule_conflicts:
  engine_used_by:
    - save_or_reschedule
    - add_participant_when_resource_blocking
    - readd_participant_when_resource_blocking
    - reactivate_interview
    - cancelled_to_active
    - reactivate_application_non_elapsed_reactivation_conflict_relevant_children
```

Thiếu:

`copy_interview_schedule`

Trong structured current spec, `engine_used_by` nhìn như một danh sách authoritative.

### `48_IDEMPOTENCY_CONCURRENCY_SPEC.md` cũng chưa cập nhật list

Current prose nói shared engine áp dụng cho save/reschedule, add/re-add participant, reactivate và CANCELLED→active; Copy không được nêu, dù generic rule “every mutation that can create/restore an operational interval” vẫn bao phủ về nguyên tắc.

### Risk

Planner/Executor đọc command registry + doc 37 sẽ hiểu đúng, nhưng Planner Protocol cũng yêu cầu đọc `app_spec.yaml` + Concurrency spec và không được tự reconcile source discrepancy.

### Fix

`app_spec.yaml`:

```yaml
engine_used_by:
  - copy_interview_schedule
```

`48_IDEMPOTENCY_CONCURRENCY_SPEC.md`:

```text
Shared engine applies to Save Copy as well as save/reschedule,
add/re-add participant when scheduled, reactivate and CANCELLED→operational.
```

Nên thêm semantic validator check cho propagation này.

**Severity: P0 for final source coherence before authorized Executor prompt.**

Không cần reopen Business Logic hay redesign architecture.

---

# 5. P1-01 — Critical Control Registry references browser-QA IDs that do not exist

`critical_control_registry.yaml`:

```yaml
INTERVIEW-COPY-SAVE:
  browser_qa:
    - RP-COPY-01
    - RP-COPY-02
    - RP-COPY-03
    - RP-COPY-04
```

Independent search across current QA doc/results/script shows these exact IDs are **not present**.

Current QA does contain descriptive Copy tests:

- Copy modal prefills source date
- Copy fills empty target Round1
- Copy keeps Demo Topic blank
- Copy preserves source schedule logistics
- Copy records provenance
- Copy blocks inactive prefilled Participant

Nhưng registry reference không resolve machine-to-machine.

### Missing explicit scenario

The intended `RP-COPY-02` scenario is:

```text
target Round1 already used
→ create next legal round
```

Current v1.10 Browser QA demonstrates the empty Round1 fill path, but tôi không tìm thấy explicit test cho used-target-Round1 → create-next-round.

### Fix

Preferred:

- give actual QA cases stable IDs `RP-COPY-01..04`;
- implement all four scenarios;
- validator requires every `critical_controls[].browser_qa[]` ID to exist in current Responsive QA evidence.

**Severity: P1.**

Không block Slice00 Foundation nhưng nên đóng trước Owner Visual UAT / Interview slice sign-off.

---

# 6. P1-02 — All-in-One generator/evidence vẫn advertise v1.15

Current generated file begins:

```text
# 15. ALL-IN-ONE SPEC — GENERATED v1.15
```

`tools/generate_all_in_one.py` hard-code `GENERATED v1.15`, và `validate_package.py` hiện còn check names/expectation:

```text
All-in-One includes current v1.15 alignment
All-in-One generated v1.15
```

Nội dung body thực tế đã là Full v1.16 + alignment 95 + gate 96, nên đây **không phải business semantic defect**, nhưng là stale source-governance/evidence labeling.

### Fix

- generator → `GENERATED v1.16`;
- validator expectation/labels → v1.16;
- regenerate All-in-One.

**Severity: P1 source hygiene / agent reliability.**

---

# 7. P2 — Semantic validator checks Copy authority existence, not full Copy propagation

`70_SEMANTIC_VALIDATION_GATE.md` đã kiểm `copy_interview_schedule` tồn tại trong registry/coverage/contract và draft non-mutating, nhưng 502/502 vẫn PASS dù `app_spec.schedule_conflicts.engine_used_by` thiếu Copy.

Nên mở rộng trace:

```text
Copy command
→ command registry
→ command contract
→ coverage
→ app_spec engine_used_by
→ concurrency shared-engine text
→ critical control
→ acceptance
→ responsive evidence
```

---

# 8. What is genuinely ready now?

Source-level gate model hiện đúng:

```text
Technical Architecture v1.16 = TECHNICAL SPECIFICATION FROZEN
Implementation Gate = READY TO IMPLEMENT
```

Tôi đồng ý với **gate model**.

Tuy nhiên vì P0-01, tôi khuyến nghị một source-sync patch nhỏ trước khi phát hành first **AUTHORIZED** executor prompt.

Đây không phải một vòng redesign khác. Required correction chỉ là:

```text
Copy
→ app_spec schedule engine
→ concurrency shared-engine list
```

Technical Spec Freeze có thể giữ nguyên sau correction; không cần reopen Business Logic.

---

# 9. Previous Planner Pack is now stale

Planner Pack trước đó dựa trên v1.15 có:

```text
58 trusted commands
DRAFT_ONLY_NOT_AUTHORIZED
GAP-001 gate circularity
Copy command ambiguity
```

v1.16 hiện có:

```text
59 trusted commands
gate circularity resolved
copy_interview_schedule added
source READY TO IMPLEMENT
```

Do đó **không được** chỉ sửa tay old Slice00 prompt từ DRAFT → AUTHORIZED.

Planner phải re-run từ exact v1.16 (hoặc patch baseline kế tiếp) và regenerate:

- baseline/hash;
- Source Inventory;
- Rule Ledger;
- Traceability Matrix **59/59 commands**;
- Open Gaps;
- exact command IDs per slice;
- exact `PLANNER_DECISION`;
- fresh Slice00 prompt.

---

# 10. Revised Planner expectation

Sau khi P0-01 được đóng, Planner expected final decision:

```text
PLANNER_DECISION: READY_FOR_INDEPENDENT_REVIEW
```

Fresh Slice00 prompt có thể mang:

```text
EXECUTION_STATUS: AUTHORIZED
```

nhưng vẫn chờ independent prompt review theo workflow người dùng đã chọn.

Slice00 source list nên bao gồm ít nhất:

- `START_HERE.txt`
- `source_registry.yaml`
- `00_README.md`
- `01_PRODUCT_SCOPE_AND_ARCHITECTURE.md`
- `12_IMPLEMENTATION_NOTES_VERCEL_SUPABASE.md`
- `14_SCOPE_AND_OPEN_ITEMS.md`
- `38_NON_FUNCTIONAL_REQUIREMENTS.md`
- `39_SECURITY_RLS_MATRIX.md`
- `44_DEPLOYMENT_OPERATIONS.md`
- `52_TECHNICAL_GATE_STATUS.md`
- `59_RLS_POLICY_BLUEPRINT.md`
- `67_WEB_SECURITY_BASELINE.md`
- `76_DEPENDENCY_BASELINE_POLICY.md`
- `95_INDEPENDENT_PLANNER_REVIEW_IMPLEMENTATION_ALIGNMENT_V1_16.md`
- `96_TECHNICAL_PRECODE_GATE_V1_16.md`
- current machine contracts.

---

# 11. Implementation Governance Recommendation — No-Handoff Continuity Protocol

> **Classification:** Reviewer recommendation / implementation-governance hardening.  
> Đây **không phải** là business/technical defect do Handover v1.16 tự định nghĩa và **không tự động làm mất trạng thái Technical Specification FROZEN**.  
> Tôi khuyến nghị bổ sung **trước Slice 00** vì nó giảm mạnh rủi ro khi đổi chat/section, đổi Planner, đổi Coding Executor hoặc quay lại dự án sau một khoảng thời gian.

## 11.1 Mục tiêu

Implementation Executor Pack hiện đã có continuity ở mức workflow:

```text
Slice/task hoàn thành
→ Planner đọc lại repo + CI
→ cập nhật plan
→ sinh prompt tiếp theo
```

Nhưng nếu trạng thái tiến độ chỉ tồn tại trong:

```text
chat history
Planner Report
Executor completion message
memory của một agent
```

thì một session mới vẫn phải handoff thủ công để biết:

- đang ở Slice nào;
- task nào `DONE / IN_PROGRESS / BLOCKED`;
- PR/commit nào đã merge;
- migration nào đã chạy;
- Acceptance nào đã có evidence;
- gap nào còn mở;
- decision kỹ thuật nào đã chốt;
- prompt nào là prompt hiện hành;
- current repo HEAD là gì;
- bước tiếp theo chính xác là gì.

Đối với dự án nhiều slice/PR và có thể đổi Planner/Executor, **chat memory không nên là execution authority**.

Mục tiêu của protocol này là:

> **Mở section/session mới → agent đọc repo → tự xác định đúng trạng thái → verify evidence → tiếp tục đúng `NEXT_ACTION` mà không cần handoff thủ công.**

---

## 11.2 Core model

Dùng:

```text
Frozen Source
+
Git Repository
+
Persistent Project-Control State
```

làm persistent working memory.

Recommended structure:

```text
/project_control/
  CURRENT_STATE.md
  SLICE_REGISTRY.yaml
  TASK_REGISTRY.yaml
  TRACEABILITY_STATUS.csv
  EVIDENCE_INDEX.yaml
  OPEN_GAPS.md
  DECISION_LOG.md
  CHANGELOG_IMPLEMENTATION.md

/project_control/prompts/
  SLICE-00_TASK-001.md
  SLICE-00_TASK-002.md
  SLICE-01_TASK-001.md
  ...
```

### Authority boundary

Handover/source vẫn quyết định:

```text
WHAT the system must do.
```

`project_control/` chỉ quyết định:

```text
WHERE implementation currently is.
WHAT has been completed.
WHAT evidence exists.
WHAT implementation decisions were accepted.
WHAT comes next.
```

`project_control/` **không được redefine business rules**.

---

## 11.3 `CURRENT_STATE.md` — primary resume entrypoint

File này phải:

- ngắn;
- dễ đọc;
- luôn phản ánh trạng thái hiện tại;
- được cập nhật trong cùng PR/task;
- là file đầu tiên Planner/Executor đọc khi resume.

Recommended template:

```text
# Current Implementation State

Source Baseline:
Full Handover v1.17

Source SHA256:
<exact hash>

Technical Status:
FROZEN

Implementation Gate:
READY TO IMPLEMENT

Current Slice:
SLICE-02 Candidate Submission

Current Task:
TASK-S02-014 Candidate document replacement

Task Status:
IN_PROGRESS

Repository HEAD:
<commit>

Current Branch:
feat/s02-candidate-documents

Latest Merged PR:
#41

Last Verified Completed Task:
TASK-S02-013 Privacy acknowledgement persistence

Blocking Issues:
NONE

Open Spec Gaps:
NONE

Current Prompt:
project_control/prompts/SLICE-02_TASK-014.md

Next Required Action:
Add RED integration tests for REPLACE current-target invariant.

Do Not Start Yet:
- SLICE-03 HR Application Inbox
- SLICE-04 Interview
- SLICE-05 Reports

Last Updated:
<timestamp>
```

### Rule

`CURRENT_STATE.md` là **navigation state**, không phải proof.

Agent mới phải verify các references trước khi tin trạng thái.

---

## 11.4 `TASK_REGISTRY.yaml`

Machine-readable tracker cho implementation tasks.

Recommended status enum:

```text
PLANNED
READY
IN_PROGRESS
BLOCKED
DONE
SUPERSEDED
CANCELLED
```

Không dùng trạng thái mơ hồ:

```text
almost done
mostly done
working
90%
```

Example:

```yaml
current_slice: SLICE-02
current_task: TASK-S02-014

tasks:
  TASK-S02-012:
    title: Candidate document ADD
    status: DONE
    slice: SLICE-02
    pr: 39
    commit: abc123
    acceptance:
      - AC-DOC-01
      - AC-DOC-02
    evidence:
      - tests/integration/document-add.test.ts
      - project_control/evidence/CI-12345.md

  TASK-S02-013:
    title: Privacy acknowledgement persistence
    status: DONE
    slice: SLICE-02
    pr: 40
    depends_on:
      - TASK-S02-012

  TASK-S02-014:
    title: Candidate document REPLACE
    status: IN_PROGRESS
    slice: SLICE-02
    depends_on:
      - TASK-S02-012

  TASK-S02-015:
    title: Candidate document DELETE
    status: READY
    slice: SLICE-02
    depends_on:
      - TASK-S02-014
```

### DONE rule

Task chỉ được `DONE` nếu:

```text
code merged or accepted
+
required tests pass
+
evidence references recorded
+
traceability state updated
+
CURRENT_STATE updated
```

---

## 11.5 `SLICE_REGISTRY.yaml`

Macro roadmap state.

Example:

```yaml
SLICE-00:
  name: Foundation
  status: DONE
  completed_prs:
    - 5
    - 8

SLICE-01:
  name: Identity/Auth
  status: DONE

SLICE-02:
  name: Candidate Submission
  status: IN_PROGRESS
  current_task: TASK-S02-014

SLICE-03:
  name: HR Application Inbox
  status: NOT_STARTED

SLICE-04:
  name: Interview
  status: NOT_STARTED
```

Recommended slice statuses:

```text
NOT_STARTED
READY
IN_PROGRESS
BLOCKED
DONE
SUPERSEDED
```

---

## 11.6 `TRACEABILITY_STATUS.csv`

Planner Traceability Matrix là design-time mapping.

`TRACEABILITY_STATUS.csv` là **implementation-time completion state**.

Recommended columns:

```text
Requirement/Rule ID
Source
Command
Implementation Path
Test/Evidence
Status
PR
Commit
Notes
```

Example:

```text
AC-PART-OPER-BULK-01,
13_ACCEPTANCE...,
bulk_change_interview_schedule_status,
src/server/interviews/bulk-status.ts,
tests/integration/interview-bulk-status.test.ts,
PASS,
#83,
abc456,
Inactive participant rollback proven
```

Statuses:

```text
NOT_STARTED
IMPLEMENTED_UNVERIFIED
PASS
BLOCKED
SUPERSEDED
```

Điều này tách:

```text
"code exists"
```

khỏi:

```text
"requirement has proof".
```

---

## 11.7 `EVIDENCE_INDEX.yaml`

Task `DONE` không đồng nghĩa requirement đã được chứng minh.

`EVIDENCE_INDEX.yaml` phải index proof.

Example:

```yaml
AC-STAT-05:
  status: PASS
  evidence:
    - type: INTEGRATION_TEST
      path: tests/db/submission-status.test.ts
    - type: CI
      run: 123456

AC-DOC-TARGET-01:
  status: PASS
  evidence:
    - type: INTEGRATION_TEST
      path: tests/integration/document-replace.test.ts

AC-PART-OPER-BULK-01:
  status: NOT_IMPLEMENTED
```

Recommended evidence types:

```text
MIGRATION
DB_INVARIANT
RLS_ADVERSARIAL
INTEGRATION
CONCURRENCY
REACT
PLAYWRIGHT
A11Y
SECURITY
PERFORMANCE
BACKUP_RESTORE
DEPLOYMENT_REHEARSAL
MANUAL_UAT
```

---

## 11.8 `OPEN_GAPS.md`

Persist toàn bộ unresolved:

```text
SPEC_GAP
STATE_INCONSISTENCY
IMPLEMENTATION_BLOCKER
EXTERNAL_DEPENDENCY
SECURITY_FINDING
MIGRATION_GAP
```

Each gap:

```text
Gap ID:
Type:
Source:
Affected Slice:
Affected Tasks:
Description:
Decision Needed:
Safe Work That May Continue:
Owner:
Status:
```

Không để blocker chỉ tồn tại trong chat.

---

## 11.9 `DECISION_LOG.md`

Dùng cho implementation decisions/ADRs đã chốt nhưng không thay đổi business behavior.

Examples:

- migration file organization;
- server module boundaries;
- test database strategy;
- chosen package after official-doc review;
- retry implementation mechanism;
- logging library;
- CI architecture.

Each record:

```text
Decision ID
Date
Context
Options
Decision
Why it preserves source behavior
Affected files/slices
Supersedes
```

Nếu decision thay đổi business/security rule:

```text
không dùng DECISION_LOG để tự quyết
→ SPEC_GAP
→ source amendment.
```

---

## 11.10 `CHANGELOG_IMPLEMENTATION.md`

Record implementation progression:

```text
date
slice/task
PR
important behavior completed
migration/schema changes
new evidence
known residual risk
```

Không thay thế Git history.

Mục đích là giúp Planner mới đọc progression nhanh.

---

## 11.11 Versioned prompts in repo

Store every executed Planner/Executor prompt:

```text
/project_control/prompts/
```

Example:

```text
SLICE-02_TASK-014_v1.md
```

Prompt file should record:

```text
Source baseline
Source SHA256
Planner revision
Task ID
Generated date
Execution authorization
```

This gives trace:

```text
Task
→ prompt AI actually received
→ source baseline
→ implementation PR
→ commit
→ tests/evidence
```

Không overwrite prompt cũ sau khi đã execute.

Nếu prompt thay đổi:

```text
v1 → v2
```

và task registry phải chỉ prompt active.

---

## 11.12 Resume Protocol — mandatory for every new session

Bất kỳ Planner/Executor session mới nào cũng phải chạy:

```text
RESUME PROJECT PROTOCOL
```

### Step 1 — Read source baseline

Read:

```text
latest frozen Handover identity/hash
```

Verify it matches project-control state.

### Step 2 — Read persistent state

At minimum:

```text
project_control/CURRENT_STATE.md
project_control/SLICE_REGISTRY.yaml
project_control/TASK_REGISTRY.yaml
project_control/OPEN_GAPS.md
project_control/DECISION_LOG.md
project_control/EVIDENCE_INDEX.yaml
```

### Step 3 — Verify actual repository

Check:

```text
git HEAD
current branch
latest merged PRs if available
referenced commits
migration files
tests/evidence referenced by last completed task
CI result if accessible
```

### Step 4 — Detect drift

If persistent state disagrees with repo:

```text
STATE_DRIFT
```

Do not continue based on stale tracker.

### Step 5 — Determine one exact next action

Agent reports:

```text
BASELINE
CURRENT_SLICE
CURRENT_TASK
LAST_VERIFIED_COMPLETED_TASK
REPOSITORY_HEAD
BLOCKERS
NEXT_ACTION
```

### Step 6 — only then modify code

Do not immediately start coding from chat request alone.

---

## 11.13 State Drift / State Inconsistency Protocol

Persistent state is not automatically trusted.

Examples:

### Case A

```text
TASK_REGISTRY = DONE
but referenced commit does not exist
```

Result:

```text
STATE_INCONSISTENCY
```

### Case B

```text
task = DONE
but required test file/evidence missing
```

Result:

```text
STATE_INCONSISTENCY
```

### Case C

```text
CURRENT_STATE says HEAD abc
repo HEAD = def
```

Agent must determine whether:

- expected new merge;
- tracker stale;
- wrong branch;
- wrong repo.

Do not silently rewrite state.

### Allowed resolution

```text
verify truth
→ update project_control
→ record correction
→ continue
```

---

## 11.14 Planner bootstrap order for every new Planner session

Recommended mandatory order:

```text
1. latest frozen Handover/source registry
2. project_control/CURRENT_STATE.md
3. TASK_REGISTRY.yaml
4. SLICE_REGISTRY.yaml
5. OPEN_GAPS.md
6. DECISION_LOG.md
7. TRACEABILITY_STATUS.csv
8. EVIDENCE_INDEX.yaml
9. git log / merged PRs
10. current production code
11. current migrations
12. CI evidence
13. only then generate/update plan/prompt
```

Planner must not reconstruct progress from chat history.

---

## 11.15 Executor bootstrap order for every new Coding Executor session

Executor starts with:

```text
Do not infer project progress from conversation memory.

Read and verify:
- current frozen source baseline;
- CURRENT_STATE.md;
- TASK_REGISTRY.yaml;
- SLICE_REGISTRY.yaml;
- OPEN_GAPS.md;
- DECISION_LOG.md;
- relevant TRACEABILITY_STATUS;
- relevant EVIDENCE_INDEX;
- active task prompt;
- actual repository HEAD/code/tests.
```

Then report resume state before implementation.

---

## 11.16 Mandatory state update before Executor completion

Current Implementation Executor Pack asks Executor for completion report.

Strengthen rule to:

> **A task is not complete until repository project-control state is updated.**

Required sequence:

```text
code
→ tests
→ CI/evidence
→ update TRACEABILITY_STATUS
→ update EVIDENCE_INDEX
→ update TASK_REGISTRY
→ update SLICE_REGISTRY if needed
→ update OPEN_GAPS
→ update CURRENT_STATE
→ update CHANGELOG_IMPLEMENTATION
→ commit/PR
```

All state updates should be in the same PR or a tightly coupled follow-up required by the gate.

---

## 11.17 Planner state update policy

Three planning layers:

### A. Macro Plan

```text
Vertical Slice Plan
```

Changes infrequently.

### B. Execution State

```text
TASK_REGISTRY
SLICE_REGISTRY
CURRENT_STATE
```

Changes continuously.

### C. Source Traceability

```text
Rule Ledger
Traceability Matrix
```

Update when:

- source baseline changes;
- source amendment occurs;
- implementation exposes SPEC_GAP;
- command/acceptance mapping changes.

Do not rewrite whole planning corpus after every small task.

---

## 11.18 Next-action discipline

Every session should end with exactly one primary:

```text
NEXT_ACTION
```

Example:

```text
NEXT_ACTION:
TASK-S02-015 — add RED test for Candidate document DELETE current-target rule.
```

Avoid vague:

```text
continue Candidate feature
work on documents
finish remaining tasks
```

This makes new-session resume deterministic.

---

## 11.19 No-Handoff behavior across different AI tools

The protocol should work even when switching between:

```text
ChatGPT Web
Codex
Claude Code
Cursor
other coding agents
```

Every agent uses:

```text
source + repo + project_control
```

instead of proprietary memory.

This is more reliable than depending on cross-session AI memory.

---

## 11.20 CI validation of project-control state

Recommended later hardening:

Add a lightweight CI checker that validates:

```text
CURRENT_STATE current_task exists in TASK_REGISTRY
TASK_REGISTRY slice exists
DONE task has evidence reference
referenced prompt exists
Acceptance IDs exist
no duplicate task IDs
only allowed task statuses
current baseline/hash fields are present
```

For completed slice:

```text
all required tasks DONE/SUPERSEDED
no blocking gaps assigned to slice
required evidence gates PASS
```

Do not let CI automatically infer business completion from code coverage alone.

---

## 11.21 Branch/PR discipline

Each task/PR should include task identity:

```text
TASK-S02-014
```

Recommended:

```text
branch:
feat/TASK-S02-014-candidate-document-replace

PR title:
[TASK-S02-014] Candidate document replacement
```

PR body includes:

```text
Source baseline
Rules/Acceptance IDs
Tests/evidence
project_control files updated
Open gaps
```

This makes repository history searchable by task.

---

## 11.22 Migration state continuity

DB changes need explicit persistence.

Task registry/evidence should record:

```text
migration files
clean-install result
forward migration result
rollback strategy if applicable
schema invariant tests
```

Never rely on:

```text
"migration ran in previous chat"
```

---

## 11.23 Definition of Done extension

Implementation Executor Pack's DoD should be extended with:

```text
[ ] CURRENT_STATE updated
[ ] TASK_REGISTRY updated
[ ] SLICE_REGISTRY updated if applicable
[ ] TRACEABILITY_STATUS updated
[ ] EVIDENCE_INDEX updated
[ ] OPEN_GAPS updated
[ ] CHANGELOG_IMPLEMENTATION updated
[ ] active prompt path recorded
[ ] repo HEAD/PR references recorded
[ ] next action explicit
```

Without these:

```text
task cannot be marked DONE
```

even if application tests pass.

---

## 11.24 Initial bootstrap before Slice 00

I recommend creating `project_control/` as part of Slice 00 Foundation, or immediately before Slice00 execution.

Initial state should contain:

```text
Current source baseline/hash
SLICE-00 = READY
TASK-S00-001 = READY
all later slices = NOT_STARTED
all current known gaps
initial traceability status
initial evidence index
approved Slice00 prompt
```

Thus continuity is established from the **first production commit**, not retrofitted after dozens of PRs.

---

## 11.25 Suggested Global Executor Contract addition

Add this exact principle to the next Implementation Executor Pack revision:

```text
PERSISTENT EXECUTION STATE

Do not rely on chat history or model memory to determine project progress.

At the start of every session:
1. read the current frozen source baseline;
2. read project_control/CURRENT_STATE.md;
3. read TASK_REGISTRY, SLICE_REGISTRY, OPEN_GAPS, DECISION_LOG,
   TRACEABILITY_STATUS and EVIDENCE_INDEX;
4. verify referenced repository commits/tests/evidence;
5. report the current verified state and exactly one NEXT_ACTION;
6. only then modify code.

At completion:
update project-control state and evidence in the repository.
A task is not DONE until code, tests, evidence and persistent state agree.

If tracker and repository disagree, return STATE_INCONSISTENCY
and resolve the drift before continuing.
```

---

## 11.26 Suggested Planner Protocol addition

Add:

```text
Before generating any new Executor prompt, Planner must rehydrate state
from repository project_control files and verify them against Git/CI.

Planner must not assume the previous conversation represents current state.

Planner may update the macro plan only when needed,
but must refresh task state/evidence and generate the next prompt
from the actual post-merge repository.
```

---

## 11.27 Governance assessment

I recommend classifying No-Handoff Continuity as:

```text
IMPLEMENTATION GOVERNANCE CORE
```

rather than:

```text
BUSINESS LOGIC CORE
TECHNICAL DOMAIN CONTRACT
```

This distinction prevents progress-tracking mechanics from contaminating business source authority.

It should become mandatory for the **implementation repository/process**, not a new Candidate/HR business rule.

---

## 11.28 Expected benefit

With this protocol:

```text
new section/session
→ read source + project_control
→ verify repo/evidence
→ identify exact current task
→ continue
```

instead of:

```text
new session
→ user manually explains previous work
→ agent guesses missing details
→ possible duplicated/stale work
```

It also makes switching executors safer and improves auditability:

```text
Requirement
→ Planner prompt
→ Task
→ PR
→ Commit
→ Tests
→ Evidence
→ Completion state
```

---

# 12. Updated Recommended Next Sequence

Based on the v1.16 review **plus** the No-Handoff Continuity recommendation:

```text
1. Patch v1.16 source:
   - app_spec schedule_conflicts.engine_used_by += copy_interview_schedule
   - Concurrency shared-engine coverage += Save Copy

2. Strongly recommended source/evidence cleanup:
   - fix Copy browser-QA IDs
   - add used-target-Round1 → next legal round QA
   - update All-in-One GENERATED v1.16 labeling

3. Rebuild source ZIP + manifest + validators.

4. Re-run Planner against the exact new ZIP/hash.

5. Planner traces all current commands and emits:
   PLANNER_DECISION: READY_FOR_INDEPENDENT_REVIEW

6. Before Slice00 execution, update Implementation Executor Pack with
   No-Handoff Continuity Protocol.

7. Initialize repository:
   /project_control/
   CURRENT_STATE.md
   TASK_REGISTRY.yaml
   SLICE_REGISTRY.yaml
   TRACEABILITY_STATUS.csv
   EVIDENCE_INDEX.yaml
   OPEN_GAPS.md
   DECISION_LOG.md
   CHANGELOG_IMPLEMENTATION.md
   /project_control/prompts/

8. Planner generates a fresh authorized Slice00 prompt and stores/version-controls it.

9. Send:
   - new source ZIP
   - revised Planner Pack
   - fresh Slice00 prompt
   - initial project_control state
   for final independent review.

10. If approved:
    Coding Executor starts Slice00.

11. Every task:
    code
    → tests
    → evidence
    → persistent state update
    → PR/merge.

12. Every new Planner/Executor session:
    run Resume Protocol before any modification.

13. After each merged task/slice:
    Planner rehydrates from repository,
    updates plan only as needed,
    and generates the next task/slice prompt.

14. Gate 3 remains pending until actual:
    migrations/RLS/RPC/race/storage/performance/backup/deployment
    evidence exists.

15. Production Ready remains a separate final gate.
```

---

# 13. Independent Review Outcome

## Full Handover v1.16

```text
APPROVED_WITH_ONE_REQUIRED SOURCE-SYNC FIX
```

The architecture/gate redesign from v1.15 is correct.

No new HR/business owner decision is required.

## No-Handoff Continuity

```text
STRONGLY RECOMMENDED BEFORE SLICE 00
```

This is an implementation-governance enhancement, not a source-business blocker.

## Immediate Coding Executor

```text
NOT YET — PATCH SOURCE + REGENERATE PLANNER ARTIFACT
```

After the narrow Copy source-sync fix, Planner regeneration, and final prompt review, expected outcome:

```text
APPROVED_FOR_EXECUTOR — SLICE 00
```

with `project_control/` initialized from the first implementation commit.

---

# 14. Bottom Line

v1.16 has crossed the important architecture threshold:

> **The source architecture and gate model are now structurally ready for implementation.**

The remaining source correction is narrow and does not require redesign.

Before real coding begins, I additionally recommend making **repository-backed persistent execution state** part of the implementation process from day one.

The desired operating model becomes:

```text
Frozen EIU Source
        +
Implementation Executor Protocol
        +
Git Repository
        +
Persistent Project-Control State
        ↓
Planner
        ↓
Independent Review
        ↓
Coding Executor
        ↓
Tests / Evidence / State Update
        ↓
Any new session can resume without handoff
```

This gives the project both:

1. **semantic correctness** — source drives behavior; and
2. **execution continuity** — repository drives progress state.
