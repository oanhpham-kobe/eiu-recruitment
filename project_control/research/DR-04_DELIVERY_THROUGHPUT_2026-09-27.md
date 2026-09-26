# DR-04 — Delivery Throughput, CI and Governance Lifecycle Cost

Status: IN PROGRESS
Research date: 2026-09-27
Repository: `oanhpham-kobe/eiu-recruitment`
Research branch: `autonomy/continuous-integration-20260905-01`
Technical evidence baseline: `8dcb0a5d7ce1be9d82e3448c01cdc1643e3ac8c4`
Research-document head when DR-04 started: `653a785c1db22ad074ee8addc8cecb620621aba4`

## Purpose

Measure representative task lifecycles so throughput recommendations are based on exact commit/evidence chains rather than raw repository commit counts. Separate product/runtime work from review, evidence, serialization, acceptance and governance-state work.

## Method

Representative tasks:

1. `TASK-S08-001` — recent cross-stack search/UI/DB hardening task.
2. `TASK-S07-005` — UI consumer task with multiple prompt-review rounds.
3. `TASK-S06-002` — backend/RBAC task with multiple implementation repair rounds.

For each sample, record:

- governed/pre-task baseline;
- implementation candidate and implementation-branch commit amplification;
- serialized product integration SHA and product diff;
- CI/review evidence;
- accepted checkpoint and any later governance-only closure commit;
- whether post-product commits mutate runtime or only `project_control` evidence/state.

No claim that every extra commit is waste is allowed. Classification is about delivery cost and marginal control value, not simply commit volume.

---

## DR-04A.1 — TASK-S08-001 mini-lifecycle

Task: `Application Inbox Search and Indexed Pagination Hardening`
Status: SAMPLE COMPLETE

### Canonical evidence chain

- Materialized governed/pre-task baseline: `141146d52a05b0d698178ba7ef097690d5ef2a27`
  - commit message: `chore(governance): materialize TASK-S08-001 prompt gate`
  - implementation was still prohibited pending prompt review / owner dispatch.
- Final reviewed implementation candidate: `d3fcdfc9c9f057e70f9c74b0dbaaa4d2594f0daf`
- Serialized product integration: `3070e56ae06d3364f15cdc5e08d91fce090d820d`
  - Integration CI: `35880657875 PASS`
  - Governance CI: `35880657901 PASS`
- Final accepted checkpoint: `checkpoint/S08-001-accepted-001`
  - accepted SHA: `0d8c5c2129ed4c78a58c8d37bd22e93c14a763eb`
  - final-acceptance Integration CI: `35882761018 PASS`
  - final-acceptance Governance CI: `35882761149 PASS`
- Governance lifecycle closure after acceptance: `8dcb0a5d7ce1be9d82e3448c01cdc1643e3ac8c4`
  - commit message recorded at research baseline: `chore(governance): close accepted TASK-S08-001 lifecycle`.

### Implementation-branch amplification

GitHub compare from governed baseline `141146d5` to reviewed candidate `d3fcdfc9` reports:

- `25` commits ahead;
- final delta concentrated in `11` product/verification files plus the task baseline-correction evidence artifact;
- runtime/product areas changed include:
  - one Supabase migration;
  - two SQL test files;
  - four Application Inbox web/runtime files;
  - two web test files;
  - Integration CI regression wiring;
  - one implementation-baseline correction review artifact.

The first implementation commits show genuine product decomposition rather than pure governance churn, including:

- search-index migration hardening;
- SQL regression tests;
- Application Inbox page-size contract;
- server/action propagation;
- 300 ms debounce/UI behavior;
- accessibility/focus-wrap repair;
- additional search/page-size regression tests.

Therefore the 25 candidate-branch commits MUST NOT be treated as 25 governance-only commits. They include incremental feature/test/repair work.

### Serialized integration compression

Compare from `141146d5` directly to product integration `3070e56a` reports:

- `5` integration-lineage commits;
- the same substantive S08-001 runtime/test/CI delta;
- two prompt/baseline review artifacts also present on integration.

The candidate branch and integration branch diverge from the same governed baseline; serialization compresses/replays the accepted product delta instead of preserving the full 25-commit producer history.

This is an important distinction for throughput analysis:

- producer iteration count = 25 commits;
- serialized integration product lineage = 5 commits;
- commit amplification exists, but most producer commits are not evidence-only.

### Post-product acceptance overhead

`3070e56a -> 0d8c5c2` is exactly `1` commit and changes only governance/evidence files:

- `project_control/AUTONOMY_RUN_STATE.yaml`;
- `project_control/CURRENT_STATE.md`;
- `project_control/EVIDENCE_INDEX.yaml`;
- `project_control/TASK_REGISTRY.yaml`;
- `project_control/reviews/S08_001_EXTERNAL_INTEGRATION_AUDIT_3070e56_v1.md`;
- `project_control/reviews/S08_001_IMPLEMENTATION_REREVIEW_R8_d3fcdfc_v1.md`.

No runtime, migration, test or application file changes in this segment.

`0d8c5c2 -> 8dcb0a5d` is exactly `1` additional commit and also changes only governance/evidence files:

- four control-plane files;
- `S08_001_ACCEPTANCE_CLOSURE_0d8c5c2_v1.md`;
- `S08_001_FINAL_ACCEPTANCE_AUDIT_0d8c5c2_v1.md`.

Again, no runtime/product change.

### S08-001 classification

| Segment | Commit shape | Product/runtime mutation | Classification |
|---|---:|---|---|
| Governed baseline -> reviewed candidate | 25 producer commits | YES | IMPLEMENTATION + TEST + REPAIR + limited evidence |
| Governed baseline -> serialized integration | 5 integration-lineage commits | YES | PRODUCT INTEGRATION + retained evidence |
| Product integration -> accepted checkpoint | 1 commit | NO | REVIEW / EVIDENCE / CONTROL-STATE |
| Accepted checkpoint -> lifecycle closure | 1 commit | NO | ACCEPTANCE CLOSURE / CONTROL-STATE |

### S08-001 throughput observation

The strongest measurable governance cost is not the raw 25 producer commits. It is the **mandatory post-product exact-SHA acceptance chain** after product integration already passed both Integration and Governance CI:

1. external integration audit / implementation re-review evidence is persisted and control state is rewritten into an accepted checkpoint candidate;
2. both CI suites run again on that governance-only SHA;
3. a final acceptance audit/closure artifact is then persisted in another governance-only commit.

This chain buys immutable exact-SHA auditability and independent review separation. DR-04B must determine whether both post-product commits and both repeated CI executions are necessary at full strength, or whether equivalent safety can be retained with fewer serialization/state transitions.

---

## DR-04A.2 — TASK-S07-005

Status: NEXT

Known evidence to verify in exact commit graph:

- implementation baseline: `9492293bfe0125acdfd4c26921247d1e6151424d`;
- final reviewed candidate: `f4a568f87556e1d97da9fd315f50c73b00a60f5c`;
- serialized integration: `c2474f2d83b5a7748fde49db04c4dba85398b216`;
- product Integration CI `35234321237 PASS`;
- product Governance CI `35234321180 PASS`;
- accepted checkpoint/SHA: `checkpoint/S07-005-accepted-001` / `0caf83354a1353d7fc807d3b3014720f9720e2e3`.

Prompt-gate history is known to contain at least four prompt-review checkpoints, including two blocking-repair rounds and one externally identified semantic mismatch. Exact lifecycle cost will be classified next rather than assumed.

---

## DR-04A.3 — TASK-S06-002

Status: PENDING AFTER S07-005

Known evidence to verify in exact commit graph:

- implementation baseline: `0a2ccdfedc477f9766c9aaa03739d16a7ed83c01`;
- implementation candidate: `63f6feba352852af5826dd582d1c42159edd66d6`;
- serialized/accepted integration SHA: `5f2b76c7f1e901b3cadb847906efcd1568c8cbc3`;
- implementation repair round: `R5`;
- R5 implementation review: PASS;
- exact integration-equivalence review: PASS;
- producer verifier run `34642569919` PASS;
- Integration CI `34705634804 PASS`;
- Governance CI `34705634726 PASS`;
- accepted checkpoint: `checkpoint/S06-002-accepted-001`.

Known registry note says R2/R3/R4 blockers were repaired before R5 PASS. Exact commit amplification and which repairs were product-critical vs process-induced remain to be measured.

---

## Provisional DR-04A finding

`S08-001` demonstrates two separate phenomena that must not be conflated:

1. **Healthy implementation iteration:** many small feature/test/fix commits can collapse into a compact accepted product delta.
2. **Governance tail after product CI:** additional exact-SHA evidence/control-state commits occur after product integration CI has already passed, with no product mutation.

DR-04A will test whether S07-005 and S06-002 repeat the same pattern before DR-04B recommends KEEP / LIGHTEN / AUTOMATE / REMOVE-DUPLICATION controls.
