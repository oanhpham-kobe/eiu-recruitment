# DR-04 — Delivery Throughput, CI and Governance Lifecycle Cost

Status: DR-04A COMPLETE — DR-04B NEXT
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

For each sample, record the governed baseline, producer candidate, serialized product integration, CI/review evidence, accepted checkpoint, later governance-only closure, and whether each segment mutates runtime or only evidence/control state.

No claim that every extra commit is waste is allowed. Classification is about delivery cost and marginal control value, not simply commit volume.

---

## DR-04A.1 — TASK-S08-001 mini-lifecycle

Task: `Application Inbox Search and Indexed Pagination Hardening`
Status: SAMPLE COMPLETE

### Canonical evidence chain

- governed/pre-task baseline: `141146d52a05b0d698178ba7ef097690d5ef2a27`;
- reviewed implementation candidate: `d3fcdfc9c9f057e70f9c74b0dbaaa4d2594f0daf`;
- serialized product integration: `3070e56ae06d3364f15cdc5e08d91fce090d820d`;
  - Integration CI `35880657875 PASS`;
  - Governance CI `35880657901 PASS`;
- accepted checkpoint: `checkpoint/S08-001-accepted-001` at `0d8c5c2129ed4c78a58c8d37bd22e93c14a763eb`;
  - final-acceptance Integration CI `35882761018 PASS`;
  - final-acceptance Governance CI `35882761149 PASS`;
- governance lifecycle closure: `8dcb0a5d7ce1be9d82e3448c01cdc1643e3ac8c4`.

### Implementation-branch amplification

`141146d5 -> d3fcdfc9` is `25` producer commits. The final delta is substantive: one Supabase migration, SQL regressions, Application Inbox runtime/server/action/UI changes, web regressions, and CI regression wiring. Early commits explicitly decompose search-index hardening, page-size propagation, 300 ms debounce, accessibility/focus repair, and tests.

Therefore the 25 producer commits are not 25 governance commits. Most are implementation/test/repair iteration.

### Serialized integration compression

`141146d5 -> 3070e56a` is only `5` integration-lineage commits while retaining the substantive accepted product delta plus two review/baseline evidence artifacts. Candidate and integration branches diverge from the same governed baseline; accepted product serialization compresses the producer history.

### Post-product acceptance overhead

`3070e56a -> 0d8c5c2` is exactly `1` governance/evidence commit. It changes only four control-plane files and two S08 review artifacts; no runtime, migration or test file changes.

`0d8c5c2 -> 8dcb0a5d` is exactly `1` additional governance/evidence commit. It again changes only control-plane files and S08 acceptance/final-audit artifacts.

| Segment | Commit shape | Product/runtime mutation | Classification |
|---|---:|---|---|
| governed baseline -> reviewed candidate | 25 producer commits | YES | IMPLEMENTATION + TEST + REPAIR + limited evidence |
| governed baseline -> serialized integration | 5 integration-lineage commits | YES | PRODUCT INTEGRATION + retained evidence |
| product integration -> accepted checkpoint | 1 commit | NO | REVIEW / EVIDENCE / CONTROL-STATE |
| accepted checkpoint -> lifecycle closure | 1 commit | NO | ACCEPTANCE CLOSURE / CONTROL-STATE |

### S08 observation

The measurable governance tail begins after product integration has already passed both CI suites. Exact-SHA auditability is real value, but the same product is then carried through additional evidence/state commits and repeated CI.

---

## DR-04A.2 — TASK-S07-005 mini-lifecycle

Task: email UI consumers over accepted email contracts
Status: SAMPLE COMPLETE

### Canonical evidence chain

- final implementation baseline after prompt repair: `9492293bfe0125acdfd4c26921247d1e6151424d`;
- final reviewed candidate: `f4a568f87556e1d97da9fd315f50c73b00a60f5c`;
- serialized product integration: `c2474f2d83b5a7748fde49db04c4dba85398b216`;
  - Integration CI `35234321237 PASS`;
  - Governance CI `35234321180 PASS`;
- accepted checkpoint: `checkpoint/S07-005-accepted-001` at `0caf83354a1353d7fc807d3b3014720f9720e2e3`;
- later Slice-07 closure checkpoint: `b4e06a639f9e00126c1f76549067e1f6469ebc8b`.

### Pre-implementation prompt-gate cost

The prompt-review chain was not a single-pass formality:

- R1 at `0d5973ee...`: `BLOCKING_REPAIR` because the prompt/reconciliation incorrectly claimed format/room were rendered server-side into `body_text`;
- R2 at `44de446c...`: initially PASS but later superseded after an external prompt audit found the prompt claimed `UNAUTHENTICATED` while accepted backend RPC behavior fails closed with `FORBIDDEN` when actor resolution fails;
- R3 at `0c9646ec...`: `BLOCKING_REPAIR` because an acceptance criterion required `interviews.manage` instead of the accepted email/history capabilities;
- R4 at `9492293b...`: PASS after both semantic defects were reconciled.

`0d5973e -> 9492293` is `8` commits and changes only governance/prompt/review/source-reconciliation files. No runtime implementation is present in this segment.

This is genuine process cost, but the corrections were substantive contract/auth/capability corrections. The evidence does **not** support removing prompt review outright.

### Producer implementation cost

`9492293 -> f4a568f` is `47` producer commits across `19` runtime/test files. The final delta includes command adapters, interview email actions, preview/history/delete UI, bulk/row actions, large UI test harnesses and regressions. This is primarily product/test iteration, not governance-only churn.

### Integration and post-product tail

`9492293 -> c2474f2` is `50` integration-lineage commits. Unlike S08, this serialization largely retains the long implementation lineage rather than compressing it; the final tree includes the same product files plus control-plane state and prompt-review evidence.

`c2474f2 -> 0caf8335` is exactly `1` governance-only commit changing four control-plane files and adding `S07_005_EXTERNAL_INTEGRATION_AUDIT_c2474f2_v1.md`. No runtime change occurs after product CI has passed.

`0caf8335 -> b4e06a6` is `2` additional commits toward Slice-07 closure. The observed delta is again control-plane/final-acceptance evidence only, including `S07_005_FINAL_ACCEPTANCE_AUDIT_0caf833_v1.md`; no runtime product change is present in that compared segment.

| Segment | Commit shape | Product/runtime mutation | Classification |
|---|---:|---|---|
| first prompt-review checkpoint -> final implementation baseline | 8 commits | NO | PROMPT REPAIR + REVIEW + CONTROL-STATE |
| implementation baseline -> reviewed candidate | 47 commits | YES | IMPLEMENTATION + TEST + REPAIR |
| implementation baseline -> serialized integration | 50 integration-lineage commits | YES | PRODUCT INTEGRATION + retained governance history |
| product integration -> accepted checkpoint | 1 commit | NO | EXTERNAL AUDIT + CONTROL-STATE |
| accepted task -> slice closure | 2 commits | NO in observed delta | FINAL ACCEPTANCE / SLICE CLOSURE |

### S07 observation

S07 shows two different optimization opportunities:

1. **Do not eliminate semantic prompt review.** It caught real mismatches before implementation.
2. **Reduce persistence churn around the review.** Eight governance-only commits were used to arrive at the final prompt baseline, and additional governance-only transitions followed product CI. A canonical single repair workspace plus one immutable reviewed prompt checkpoint could retain the same safety with fewer branch/state transitions.

---

## DR-04A.3 — TASK-S06-002 mini-lifecycle

Task: `Internal User Directory, HR RBAC & Identity Lifecycle Trusted Contracts`
Status: SAMPLE COMPLETE

### Canonical evidence chain

- implementation baseline: `0a2ccdfedc477f9766c9aaa03739d16a7ed83c01`;
- reviewed implementation candidate: `63f6feba352852af5826dd582d1c42159edd66d6`;
- product serialization commit recorded by the final-gate state: `895d54576c47df7d98ea66ed2774b8fac50c6015`;
- application-verified integration before governance state sync: `80146bc5aab88f755312c7ffff6007c1099d6782`;
  - exact full Integration CI `34705140390 PASS`;
  - Governance CI `34705140378 PASS`;
- governance state-sync predecessor: `7cf39793969c10cd416e1ee5066b12d782645532`;
- exact final-gate SHA / accepted checkpoint target: `5f2b76c7f1e901b3cadb847906efcd1568c8cbc3`;
  - commit message: `chore(state): trigger exact S06-002 final gate [full-ci]`;
  - final Integration CI `34705634804 PASS`;
  - final Governance CI `34705634726 PASS`;
- accepted checkpoint: `checkpoint/S06-002-accepted-001` pointing to `5f2b76c7...`;
- subsequent bot acceptance/state-routing commit: `ba004a947e4e7d3c3e372ac5d3a2a4941428e8f9`, message `chore(state): accept TASK-S06-002 and route slice closure [full-ci]`.

### Implementation and repair cost

`0a2ccdf -> 63f6feba` is `22` producer commits. The delta contains major production migrations, web auth/session changes, command changes, concurrency regressions, and R2/R3/R4 repair migrations/tests.

The review blockers were materially security/concurrency relevant:

- R1/R2 reconciliation required raw `app_users.auth_user_id` privacy, request-scoped session access, participant eligibility semantics, deterministic User/advisory lock order, and Google bind/rebind lock/revalidation ordering;
- R2/R3 reconciliation expanded this into Unit/User/Application lock graphs, deadlock-safe ordering, Interview participant/actor locking and post-lock active-user revalidation, plus fail-closed revalidation of verified Google email after locks;
- R4/R5 closure focused on synchronized contention proof and missing-auth Unit contention; R4 -> R5 changed only the concurrency test, not the production migration.

Therefore R2–R4 repair rounds cannot responsibly be classified as ceremony. They repaired or proved real security, deadlock and identity-consistency properties.

### Integration lineage

`0a2ccdf -> 5f2b76c7` is `20` integration-lineage commits and retains the large product/security delta plus control-plane/review evidence. Candidate and integration lineages diverge from the same baseline.

The important throughput signal is at the tail, not the existence of the repair rounds.

### Explicit governance-only full-CI tail

The final-gate commit `5f2b76c7` changes only `project_control/CURRENT_STATE.md`. Its own text records that `80146bc5` was the latest application-verified integration SHA and had already passed full Integration CI `34705140390` and Governance CI `34705140378`. The purpose of `5f2b76c7` is explicitly to request another `[full-ci]` on a governance-only follow-up SHA so the final integration-equivalence reviewer can review that exact immutable HEAD.

After `5f2b76c7` passes again, `ba004a94` advances one commit and changes only:

- `project_control/AUTONOMY_RUN_STATE.yaml`;
- `project_control/CURRENT_STATE.md`;
- `project_control/TASK_REGISTRY.yaml`.

No product/runtime file changes in this acceptance transition.

| Segment | Commit shape | Product/runtime mutation | Classification |
|---|---:|---|---|
| implementation baseline -> reviewed candidate | 22 producer commits | YES | IMPLEMENTATION + SECURITY/CONCURRENCY REPAIRS + TESTS |
| implementation baseline -> final integration lineage | 20 commits | YES overall | SERIALIZED PRODUCT + REGRESSIONS + GOVERNANCE |
| application-verified integration -> exact final-gate SHA | governance-only state transitions | NO | EXACT-SHA GATE + REPEATED FULL CI |
| final-gate SHA -> task acceptance/routing | 1 commit | NO | CONTROL-STATE / ACCEPTANCE |

### S06 observation

S06 gives the strongest evidence that current governance can require **full product CI on a commit whose only purpose is to update governance state**, despite the preceding application integration already passing full CI and no product files changing afterward. This preserves exact-SHA equivalence literally, but at substantial repeat-run cost.

---

## DR-04A cross-sample conclusion

DR-04A is COMPLETE.

Across all three representative tasks, three patterns are stable:

1. **Implementation/review iteration is often valuable.** Large producer commit counts include real tests and repairs. S06 in particular shows independent review catching security/concurrency defects that should not be traded away for speed.
2. **Prompt review has value but its state persistence is too chatty.** S07 demonstrates that semantic prompt review prevents contract drift, while also showing eight pre-implementation governance-only commits before the final implementation baseline.
3. **The repeated governance tail is the clearest throughput tax.** S08, S07 and especially S06 all carry accepted product through additional evidence/control-state commits after product CI. S06 explicitly triggers full CI on a governance-only SHA after a prior full product CI PASS.

### Provisional control classification before CI-runtime measurement

- `KEEP`: independent semantic prompt review for high-risk/contract-heavy tasks; independent implementation review; DB concurrency/security regressions; immutable accepted checkpoint semantics.
- `KEEP BUT AUTOMATE`: exact diff proof that a post-product commit is governance-only; automatic control-plane validation; evidence indexing; checkpoint/tag creation.
- `LIGHTEN CANDIDATE`: full Integration CI rerun when the only delta since an already-green product SHA is allow-listed governance/evidence files.
- `REMOVE-DUPLICATION CANDIDATE`: separate serial governance commits that only persist the same review result/state transition and then force another identical full-CI gate.

No control will be removed based on DR-04A alone. DR-04B will measure workflow structure and actual run duration/cost for the representative exact-SHA chains before final recommendations.

---

## DR-04B — CI workflow and repeat-run cost

Status: NEXT

Next measurements:

1. inspect baseline Integration CI and Governance CI workflow definitions;
2. identify expensive jobs and overlap between workflows;
3. fetch representative product-vs-governance-only run metadata for S08/S07/S06;
4. calculate elapsed repeat-run cost where timestamps are available;
5. design a path-aware verification policy that retains exact-SHA governance safety without rerunning unrelated product suites on evidence-only deltas.
