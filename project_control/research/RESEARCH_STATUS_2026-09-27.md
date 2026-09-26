# EIU Recruitment Deep Research — Continuation Index

Status: COMPLETE
Updated: 2026-09-27
Repository: `oanhpham-kobe/eiu-recruitment`
Research branch: `autonomy/continuous-integration-20260905-01`
Immutable technical evidence baseline: `8dcb0a5d7ce1be9d82e3448c01cdc1643e3ac8c4`
Accepted product checkpoint below the governance-only baseline closure: `0d8c5c2129ed4c78a58c8d37bd22e93c14a763eb`

## Primary resume artifact

Read this first after the source-blind Astra greenfield phase:

- `project_control/research/FINAL_DEEP_RESEARCH_SYNTHESIS_2026-09-27.md`

It reconciles all final findings, corrections, cloud-state limitations, recovery classification and recommended Vercel + Supabase release topology.

Do not infer runtime/product changes from research-document commits after the immutable technical baseline. Those commits only persist research evidence.

## Completed research units

- [x] DR-00 — immutable baseline / repository map.
- [x] DR-01 — canonical Phase-1 scope vs runtime completeness.
- [x] DR-02 — control-plane state semantics / task-materialization blind spots.
- [x] DR-03 — runtime architecture / security boundary analysis.
- [x] DR-04A — representative delivery lifecycle / review churn analysis.
- [x] DR-04B — CI cost and path-aware verification analysis.
- [x] DR-04C — governance/evidence serialization analysis.
- [x] DR-05 — Vercel + Supabase deployment/runtime readiness.
- [x] DR-06 — user-facing and external-runtime completion gaps.
- [x] DR-07 — final KEEP / SIMPLIFY / FIX / ADD / DEFER recovery classification.
- [x] DR-08 — Astra Medium strategic-review handoff prepared in the owner conversation.

## Durable detailed artifacts

- `project_control/research/REPO_DEEP_RESEARCH_2026-09-26.md`
- `project_control/research/DR-03_RUNTIME_ARCHITECTURE_2026-09-26.md`
- `project_control/research/DR-04_DELIVERY_THROUGHPUT_2026-09-26.md`
- `project_control/research/DR-04B_CI_COST_2026-09-27.md`
- `project_control/research/DR-04C_GOVERNANCE_SERIALIZATION_2026-09-27.md`
- `project_control/research/FINAL_DEEP_RESEARCH_SYNTHESIS_2026-09-27.md`

## Reconciled strategic verdict

**Do not full-rewrite by default.**

Evidence supports selective recovery + productionization:

- KEEP Next.js + Supabase, DB/RPC/RLS concurrency/security invariants, accepted workflows, high-value regression tests, path-aware CI and independent review for high-risk work.
- SIMPLIFY command plumbing, oversized frontend orchestration, evidence/governance serialization and unnecessary broad CI repetition.
- FIX Supabase SSR session-refresh proxy, product-completeness state semantics, error/logging boundaries, release/runbook/environment contracts and cloud migration validation.
- ADD missing Master Data UI, Users & Permissions UI, real email sender, real malware-scanning runtime or explicit requirement narrowing, cleanup scheduler, PDF output after template authority, Vercel Preview and remote Supabase release proof.
- DEFER future Dashboard/KPI/Candidate Database and non-blocking architecture refactors.

## Final cloud-state corrections

- Local Supabase Postgres and currently connected Supabase project are both Postgres 17. Any earlier PG17-vs-PG15 hypothesis is disproved.
- Current connected Vercel project `eiu-recruitment` exists but currently has zero deployments. Earlier temporary assumptions of READY previews must not be used.
- Connected Supabase project `eiu-recruitment-dev` is currently INACTIVE. Remote migration history, RLS/security-advisor state, Auth provider configuration and live DB parity remain unverified until a safe non-production environment is available.

## Astra anti-anchoring rule

Astra must complete and freeze a source-blind greenfield Phase A before reading any of these research artifacts or implementation source.

Only after Phase A is frozen should Astra read this index, the final synthesis, authoritative control-plane files, `web/`, `supabase/`, workflows and task history.

Astra must independently verify or reject the research findings; the synthesis is evidence input, not an answer key.

## Owner boundary

Research is complete, but no external mutation is authorized by this status:

- do not deploy Vercel;
- do not mutate/restore/apply migrations to connected Supabase;
- do not merge/push `main`;
- do not use production secrets;
- do not materialize or implement TASK-S08-002 without a separate governed Owner decision.
