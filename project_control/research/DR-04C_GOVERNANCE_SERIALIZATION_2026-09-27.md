# DR-04C — Governance / Evidence Serialization Simplification

Status: COMPLETE
Research date: 2026-09-27
Repository: `oanhpham-kobe/eiu-recruitment`
Technical evidence baseline: `8dcb0a5d7ce1be9d82e3448c01cdc1643e3ac8c4`
Parents:
- `project_control/research/DR-04_DELIVERY_THROUGHPUT_2026-09-27.md`
- `project_control/research/DR-04B_CI_COST_2026-09-27.md`

## Question

How many governance/evidence transitions are actually required to preserve independent exact-SHA review, exact-SHA CI, immutable accepted checkpoints and truthful canonical state?

This unit does not propose weakening review. It separates required lifecycle boundaries from historical persistence conventions that manufacture extra SHAs.

---

## 1. Current policy requirements

Baseline `AUTONOMY_PARALLEL_GOVERNANCE.md` requires the following high-value boundaries:

1. producer self-review is not independent acceptance review;
2. independent OMP reviewer reviews an exact candidate SHA;
3. a repair that changes candidate SHA invalidates acceptance of the old SHA and requires targeted fresh re-review;
4. if serialized integration changes Git identity, OMP performs a targeted exact-SHA final acceptance/equivalence review on the integration SHA;
5. if candidate SHA is preserved, the candidate review may serve as final acceptance review;
6. exact-SHA CI and immutable accepted checkpoint semantics are retained;
7. the accepted checkpoint is append-only and must not be force-moved;
8. after all tasks in a slice are individually accepted, a slice-closing composition review and broader regression gate are performed when appropriate.

These are KEEP controls.

### Evidence-branch rule

The same policy explicitly says that when GitHub-visible review handoff is required, reviewer output is persisted on a **non-candidate evidence branch**, e.g. `review/<TASK_ID>-<SHORT_SHA>-vN`.

The evidence branch:

- MUST NOT move or mutate the reviewed candidate ref;
- is evidence only;
- never becomes product, scheduling or authorization authority;
- is append-only.

This rule is important because it already provides the mechanism needed to persist reviewer evidence without manufacturing a new product/integration SHA.

### No policy requirement for a separate external integration audit

The baseline policy requires the independent OMP exact-SHA final acceptance/equivalence review when serialization changes SHA. It does **not** define a separate `EXTERNAL_CHATGPT` integration audit as another mandatory acceptance gate.

An external/producer equivalence check can still be a useful self-review, but it is not a substitute for OMP independence and need not become a separate integration-branch gate.

---

## 2. Validator constraints

### `validate_control_plane.py`

The validator enforces canonical state consistency, including:

- task/slice DAG consistency;
- current task/slice relationships;
- accepted-task state and exact SHA shape;
- `last_accepted_task.commit` matching task `implementation_sha` when present;
- safe-frontier/dependency validity;
- execution-mode/lane/runtime invariants;
- CI checkpoint consistency between `last_verified_application_checkpoint` and `github_ci.commit_sha`;
- existence and derived/non-authoritative marking of `CURRENT_STATE.md` and traceability output.

It does **not** require a reviewer artifact, `EVIDENCE_INDEX` update, acceptance transition, and closure transition to be separate commits.

`EVIDENCE_INDEX.yaml` is not directly loaded/validated by this validator at the baseline inspected.

### `validate_omp_native.py`

This validator checks OMP configuration, project agents/skills, MCP and lock/provenance rules. It does not impose task-acceptance evidence commit sequencing.

### Consequence

Multiple serial commits such as:

`persist integration audit -> gate final review -> persist final review -> mark accepted -> close lifecycle`

are not technically required by the validators. They are lifecycle/persistence conventions and therefore are valid optimization targets if policy semantics remain intact.

---

## 3. Historical S08-001 serialization behavior

Product integration:

- `3070e56ae06d3364f15cdc5e08d91fce090d820d`
- product Integration CI `35880657875 PASS`
- Governance CI `35880657901 PASS`

Pre-final governance target:

- `0d8c5c2129ed4c78a58c8d37bd22e93c14a763eb`
- parent = product integration `3070e56a`;
- changes exactly six governance/evidence files and zero product/test/migration/workflow files;
- includes persisted external integration audit and implementation rereview artifacts;
- task remains `REVIEW` and accepted checkpoint is deliberately absent;
- exact governance-sha Integration CI `35882761018 PASS` and Governance CI `35882761149 PASS`.

Independent final acceptance audit then targets `0d8c5c2`, not the product integration SHA. The final audit explicitly re-verifies:

- product candidate -> product integration byte equivalence;
- product CI on `3070e56a`;
- governance-only diff `3070e56a -> 0d8c5c2`;
- control validators at `0d8c5c2`;
- exact-SHA governance CI.

After that PASS, the accepted checkpoint points to `0d8c5c2`, while a later governance closure commit `8dcb0a5d...` persists the final audit / acceptance state.

### Amplification mechanism

Persisting review evidence into the integration branch **before** final acceptance changes the SHA. That new SHA then becomes the thing that must be independently audited and CI-verified.

This is self-induced SHA churn. The policy's non-candidate evidence-branch rule already provides a way to avoid review evidence mutating its own review target.

---

## 4. Historical S07-005 confirms the same pattern

Product integration:

- `c2474f2d83b5a7748fde49db04c4dba85398b216`
- product Integration CI `35234321237 PASS`;
- Governance CI `35234321180 PASS`.

Governance-reconciled target:

- `0caf83354a1353d7fc807d3b3014720f9720e2e3`;
- exactly five governance/evidence paths differ from product integration;
- no product/test/migration/workflow path differs;
- task remains `REVIEW` before final audit;
- exact governance-sha CI passes.

Final OMP acceptance audit then targets `0caf8335`, verifies the product integration and the governance-only reconciliation, authorizes checkpoint creation, and is persisted later in the slice-closure lineage.

Again, the extra exact-SHA review target is created by moving evidence/state onto the integration branch before the final independent audit.

---

## 5. What is actually necessary for an ordinary task?

### Structurally necessary

For a normal task where serialization changes SHA:

1. **Product integration SHA `P`** containing the reviewed product/test delta.
2. **Independent OMP final equivalence/acceptance review of exact `P`**.
3. **Applicable exact-SHA CI on `P`** according to impact/full-gate policy.
4. **Immutable accepted checkpoint** pointing to `P` after both review + CI PASS.
5. **One canonical governance closure commit `G`** after acceptance to record facts that could not truthfully exist before the review/checkpoint:
   - task `DONE` / accepted implementation SHA `P`;
   - accepted checkpoint/tag identity;
   - final review evidence pointer;
   - CI provenance;
   - lane release / settled worker record;
   - recomputed frontier and continuation state;
   - derived `CURRENT_STATE` / traceability refresh.
6. Path-aware Integration CI + Governance CI on `G`; expensive product domains remain closed when `G` is governance-only.

One post-acceptance canonical state commit is logically justified because the final verdict/checkpoint does not exist before the independent review completes.

### Not structurally necessary

The following do not require separate integration-branch commits:

- producer/external integration self-audit;
- OMP review artifact persistence;
- evidence-index staging before final OMP review;
- a dedicated `gate final acceptance audit` integration commit whose only purpose is to carry evidence/state and manufacture the exact SHA that will then be audited;
- another standalone lifecycle-closure commit if its facts can be included in the single post-acceptance canonical state transition.

Review outputs can be persisted to append-only evidence branches during the gate and referenced by `G` after acceptance.

---

## 6. Proposed minimal ordinary-task serialization

When serialized integration changes candidate identity:

```text
reviewed candidate C
-> serialize product/test delta to integration SHA P
-> producer self/equivalence check (optional evidence, no integration mutation)
-> independent OMP exact-SHA equivalence/final acceptance review of P
   -> persist reviewer output on review/<...> evidence branch
-> exact-SHA Integration/Governance CI on P
   (or CI then review if the gate contract chooses that order; both bind P)
-> review PASS + CI PASS
-> create immutable checkpoint/TASK-accepted tag -> P
-> one governance closure commit G
   * TASK_REGISTRY = DONE, implementation_sha=P
   * AUTONOMY_RUN_STATE = accepted/checkpoint/CI provenance + lane release/frontier
   * EVIDENCE_INDEX = pointers to evidence-branch artifacts
   * CURRENT_STATE / TRACEABILITY = regenerated derived views
-> path-aware CI + Governance CI on G
-> continue AUTONOMOUS
```

Core invariant remains:

`FINAL_OMP_ACCEPTANCE_REVIEW_SHA == PRODUCT_CI_SHA == ACCEPTED_CHECKPOINT_SHA == P`

The later canonical-state commit `G` is not misrepresented as a new accepted product SHA. It records acceptance of `P`.

---

## 7. Last-task-of-slice behavior

S07-005 provides a concrete slice-closing sample.

After final acceptance target `0caf8335`, the branch advanced through exactly two commits before the Slice-07 composition rereview target:

1. `63563a7c09205ece81f334ecbedb49333faba44e`
   - `docs(governance): persist S07-005 final acceptance audit`
2. `b4e06a639f9e00126c1f76549067e1f6469ebc8b`
   - `chore(governance): close accepted S07-005 task`
   - changes task status `REVIEW -> DONE` and routes the control plane to independent Slice-07 closing composition rereview.

Evidence later records:

- `SLICE-07-CLOSING-REVIEW-002`;
- closing rereview SHA `b4e06a639f9e00126c1f76549067e1f6469ebc8b`;
- verdict `PASS`;
- source reopen `false`;
- slice completeness `true`;
- findings `NONE`.

### What can be consolidated

The two S07 commits above represent one logical post-task-acceptance transition and can be one atomic closure bundle:

- persist/link final task review evidence;
- mark task DONE;
- record checkpoint/CI provenance;
- regenerate derived views;
- route directly to slice composition review.

There is no policy/validator requirement for `persist audit` and `close accepted task` to be separate integration commits.

### What should remain separate

The **slice acceptance transition after composition review** is a genuinely new fact and should remain a separate canonical transition.

Policy explicitly orders slice composition review after individual task acceptance. Before composition PASS, the system cannot truthfully claim:

- Slice DONE;
- slice accepted checkpoint;
- next-slice advancement authorized by slice closure.

Therefore the minimal safe last-task-of-slice flow is:

```text
product SHA P
-> task final review + task CI PASS on P
-> task checkpoint -> P
-> one task-closure / slice-review-target commit G
   (task DONE; slice still IN_PROGRESS; composition review pending)
-> independent slice composition review of G
-> broader exact-SHA regression gate on G when required
-> slice review PASS + CI PASS
-> immutable slice accepted checkpoint -> G
-> one slice-closure / continuation commit H
   (slice DONE; persist composition evidence; recompute/materialize next frontier)
-> path-aware governance validation on H
-> continue
```

This preserves temporal truth. Trying to mark Slice DONE in `G` before composition review would weaken the current ordering and is not recommended.

For the last task in a slice, **two post-product governance state transitions are therefore justified**: one after task acceptance and one after slice acceptance. More than those requires specific evidence of a distinct fact boundary.

---

## 8. Final control classification

### KEEP

- independent prompt/source review where contract risk warrants it;
- independent candidate implementation review;
- targeted re-review after repair;
- final OMP exact integration equivalence review when serialization changes SHA;
- exact-SHA CI;
- immutable task checkpoint;
- slice-closing composition review + slice checkpoint;
- append-only evidence branch semantics;
- one truthful state transition after each independently established acceptance boundary.

### REMOVE DUPLICATION / STOP TREATING AS MANDATORY GATE

- separate `EXTERNAL_CHATGPT integration audit` as a mandatory gate when independent OMP final equivalence review already covers serialization equivalence;
- integration-branch commit solely to import review artifacts before final acceptance;
- final audit of a governance SHA that only exists because review evidence was copied onto integration first;
- separate `persist audit` and `close accepted task` commits when both can be one atomic post-acceptance closure bundle.

### CONSOLIDATE

Ordinary accepted task:

- target = one post-acceptance governance closure commit.

Last task of slice:

- target = one task-closure/slice-review-target commit;
- then one separate slice-closure/continuation commit after composition PASS.

### AUTOMATE

Generate each closure bundle atomically from verified facts:

- accepted task/slice checkpoint SHA;
- OMP evidence branch + evidence commit/path;
- exact CI run IDs/results;
- changed-file / product-provenance proof;
- lane release and safe-frontier recomputation;
- task/slice registry mutation;
- derived state regeneration.

Add validator rules that reject partial acceptance bundles instead of relying on multiple intermediate commits to make missing fields visible.

---

## 9. DR-04C verdict

DR-04C is COMPLETE.

The existing governance model does not need fewer independent safety gates; it needs **cleaner separation between immutable reviewed product SHAs, append-only evidence, and canonical state transitions**.

The highest-value simplification is:

> Review the actual product integration SHA, keep review artifacts off that target until acceptance is decided, checkpoint that reviewed/CI-proven SHA, then persist all resulting canonical state atomically.

This removes self-induced SHA churn while preserving exact-SHA review, CI provenance, immutable recovery anchors, and truthful AUTONOMOUS continuation semantics.
