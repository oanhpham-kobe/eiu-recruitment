# EIU Recruitment Deep Research — Continuation Index

Status: ACTIVE
Updated: 2026-09-27
Repository: `oanhpham-kobe/eiu-recruitment`
Research branch: `autonomy/continuous-integration-20260905-01`
Immutable technical evidence baseline: `8dcb0a5d7ce1be9d82e3448c01cdc1643e3ac8c4`

## Resume rule

This file is the compact continuation index for long-context recovery.

Do not infer runtime/product changes from later research-document commits. Runtime conclusions remain anchored to `8dcb0a5d...` unless a later research unit explicitly declares another evidence baseline.

For Astra/OMP handoff, read:

1. this index;
2. the active DR file named below;
3. older detailed DR files only when needed for dependency evidence.

The original master remains available at:

- `project_control/research/REPO_DEEP_RESEARCH_2026-09-26.md`

It contains detailed DR-00/01/02 history but its top checklist predates completion of DR-03/04, so use this index for current progress.

## Progress

- [x] DR-00 — immutable baseline / repo map.
- [x] DR-01 — canonical Phase-1 scope vs runtime.
- [x] DR-02 — control-plane state semantics / materialization blind spots.
- [x] DR-03 — runtime architecture/security boundary analysis.
  - File: `project_control/research/DR-03_RUNTIME_ARCHITECTURE_2026-09-26.md`
  - Verdict: KEEP core architecture; SIMPLIFY command plumbing; HARDEN logging/error boundaries; no rewrite.
- [x] DR-04 — CI/governance/review throughput analysis.
  - DR-04A lifecycle samples: `project_control/research/DR-04_DELIVERY_THROUGHPUT_2026-09-27.md`
  - DR-04B CI cost: `project_control/research/DR-04B_CI_COST_2026-09-27.md`
  - DR-04C governance serialization: `project_control/research/DR-04C_GOVERNANCE_SERIALIZATION_2026-09-27.md`
- [ ] DR-05 — production readiness: deployment, external email delivery, storage/documents/scanning/PDF, security/operations.
- [ ] DR-06 — frontend maintainability and UX completion.
- [ ] DR-07 — final KEEP / SIMPLIFY / ADD / DEFER recovery plan.
- [ ] DR-08 — independent Astra/OMP review handoff if needed.

## DR-04 final synthesis

Do not optimize by deleting independent review. Representative history proves some review rounds caught real auth, concurrency, identity and contract defects.

Recommended process shape:

- KEEP independent prompt/source review for contract-heavy/high-risk work;
- KEEP independent implementation review and targeted repair re-review;
- KEEP exact-SHA product CI, immutable checkpoints and slice composition review;
- KEEP path-aware Integration CI; S07/S08 show governance-only exact-SHA validation can complete cheaply;
- do not force `[full-ci]` on evidence-only SHAs after a just-green full product SHA unless a new explicit shared-contract reason exists;
- review the actual serialized product SHA rather than creating a governance-only review target by copying evidence onto integration first;
- persist OMP reviewer output on append-only evidence branches as the current policy already specifies;
- after acceptance, atomically persist canonical task state in one governance closure bundle;
- for the last task of a slice, one additional slice-closure transition after composition PASS is justified because Slice DONE is a new fact;
- remove a mandatory separate external-ChatGPT integration-audit gate when the independent OMP final equivalence review already covers the same equivalence claim.

## High-priority findings carried forward

1. Phase-1 user-facing scope is incomplete: Master Data and Users & Permissions UI are missing despite Slice-06 = DONE.
2. Slice-DONE validation proves all materialized tasks DONE, not canonical requirement coverage; missing tasks can disappear from completeness checks.
3. Traceability/reporting can be stale without blocking scheduling.
4. Runtime layering is broadly sound; DB/RPC/RLS boundaries should be preserved.
5. Command plumbing, error redaction and frontend orchestration are simplification/hardening targets, not rewrite justification.
6. Email feature evidence currently proves outbox/contract behavior, not external delivery.
7. Storage upload path performs trusted inspection and leaves `PENDING_SCAN`; actual malware verdict worker/runtime remains a DR-05 production-readiness question.

## Active next unit

`DR-05A — Deployment / Release Runtime Readiness`

Scope:

- inspect deployment topology and environment contracts;
- determine whether Vercel/Supabase production deployment is implemented, merely documented, or explicitly out of scope;
- inspect release/runbook/secret/migration boundaries;
- distinguish code readiness from connected-environment readiness;
- record blockers without deploying Vercel or mutating connected Supabase.

Owner boundary remains unchanged: research only; do not deploy Vercel, mutate connected Supabase, push/merge `main`, or perform production operations without explicit Owner authorization.
