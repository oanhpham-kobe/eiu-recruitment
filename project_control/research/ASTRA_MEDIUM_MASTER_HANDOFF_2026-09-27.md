# Astra Medium Master Handoff — EIU Recruitment Strategic Recovery Review

Date: 2026-09-27
Repository: `oanhpham-kobe/eiu-recruitment`
Mode: STRATEGIC REVIEW / READ-ONLY IMPLEMENTATION
Owner goal: determine the shortest safe path from the current project to a genuinely usable Phase-1 EIU Recruitment product on Vercel + Supabase.

## 0. Mission

You are acting as a principal product architect, software architect, recovery reviewer, and delivery-systems reviewer.

Your job is **not** to preserve the current implementation because it exists, and **not** to recommend a rewrite because a clean-sheet design feels simpler.

Optimize for:

> the shortest safe path from the actual current state to the intended Phase-1 product.

Use first principles.

Any recommendation to KEEP the current design must be justified from product, security, correctness, operational, and delivery principles — not sunk cost.

Any recommendation to REPLACE/REWRITE must show concrete evidence that replacement is faster/safer after accounting for migration, lost verified invariants, reimplementation, retesting, and deployment risk.

## 1. Hard Owner boundaries

During this review you MUST NOT:

- modify product/runtime source;
- modify migrations;
- deploy Vercel;
- restore, mutate, reset, migrate, or otherwise operate on connected Supabase;
- use or reveal production secrets;
- merge or push `main`;
- move immutable accepted checkpoints;
- materialize or implement TASK-S08-002;
- create product implementation commits;
- silently change canonical product scope.

You MAY:

- read repository files and Git history;
- inspect CI/review evidence;
- use read-only Vercel/Supabase information if available;
- consult current official Vercel/Supabase/Next.js documentation;
- write review-only Markdown artifacts under `project_control/astra_review/` locally.

Do not commit or push those review artifacts unless separately authorized by the Owner.

## 2. Critical anti-anchoring protocol

This review is deliberately staged.

**PHASE A MUST BE COMPLETED AND FROZEN BEFORE YOU READ CURRENT IMPLEMENTATION, RESEARCH FINDINGS, TASK HISTORY, OR CURRENT ARCHITECTURE.**

The purpose is to create an independent control architecture against which the current system can later be judged.

If your environment cannot guarantee that you can avoid reading later-phase material before completing Phase A, then:

1. perform PHASE A only;
2. write and freeze its output;
3. STOP;
4. tell the Owner that Phase A is frozen and ask for the Phase-B continuation invocation.

Do not preload Phase-B files merely to understand what you will do later.

---

# PHASE A — SOURCE-BLIND GREENFIELD PRODUCT / ARCHITECTURE REVIEW

## A1. What you MAY read

Read only product-facing authority needed to understand the intended system:

- product vision / business goals;
- personas and access roles at the product level;
- canonical Phase-1 workflows;
- UX/design-system material;
- screen/page behavior and user-visible requirements;
- non-negotiable privacy/security/business constraints;
- explicit Phase-1 vs future-scope boundaries.

You may locate these within product/design material such as `recruitment_webapp/`, but choose only product-facing documents. Design-system and responsive-prototype material may be used to understand intended UX.

## A2. What you MUST NOT read in Phase A

Do not read or inspect:

- `web/` implementation;
- `supabase/` implementation or migrations;
- `.github/workflows/`;
- `project_control/research/` other than this handoff file;
- `project_control/AUTONOMY_RUN_STATE.yaml`;
- `project_control/TASK_REGISTRY.yaml`;
- `project_control/SLICE_REGISTRY.yaml`;
- implementation prompts;
- implementation/re-review evidence;
- accepted implementation checkpoint details;
- source diffs or product commit history;
- current Vercel/Supabase cloud configuration;
- database schema/RPC/RLS technical design unless a product requirement explicitly requires a capability and you are reasoning about it abstractly.

Do not try to infer the current architecture from filenames or history.

## A3. Greenfield questions

Assume we had to begin delivering EIU Recruitment today and wanted the **simplest correct Phase-1 product** that could safely run on Vercel + Supabase.

Answer from first principles:

1. What is the minimum user-facing Phase-1 scope?
2. What personas exist and what must each be able to do end-to-end?
3. What is the simplest sensible module decomposition?
4. What is the minimum data model and ownership model at conceptual level?
5. Which business invariants must be transactional?
6. Which authorization/privacy guarantees are mandatory?
7. Which concurrency guarantees are genuinely required for this type of recruitment system?
8. What should be handled in application code versus PostgreSQL/Supabase?
9. What should run synchronously versus asynchronously?
10. Which external runtimes/providers are genuinely mandatory for launch?
11. Which capabilities can be deferred without breaking Phase-1 value?
12. What is the simplest safe Vercel + Supabase deployment topology?
13. What is the minimum test pyramid needed for confidence?
14. What process/governance would you use if optimizing for reliable delivery speed rather than ceremony?
15. What would you explicitly NOT build yet?
16. In what order would you implement the end-to-end vertical slices so that a working product appears as early as possible?

## A4. Required Phase-A artifact

Write:

`project_control/astra_review/ASTRA_GREENFIELD_PHASE1_ARCHITECTURE.md`

It must include:

- canonical Phase-1 interpretation;
- user journeys;
- proposed simple architecture;
- module boundaries;
- conceptual data/security boundaries;
- external-runtime decisions;
- Vercel + Supabase deployment shape;
- minimum verification strategy;
- implementation order;
- deferred scope;
- assumptions and unresolved product questions;
- a section titled `Complexity We Would Refuse To Add Without Evidence`.

End with:

`GREENFIELD_PHASE_A_FROZEN: YES`

Once written, do not revise this artifact after seeing the current implementation. Later disagreement must be documented as reconciliation, not retroactive editing.

---

# PHASE B — CURRENT-STATE AUDIT

Only begin Phase B after `ASTRA_GREENFIELD_PHASE1_ARCHITECTURE.md` is frozen.

## B1. Pin the implementation baseline

Use this immutable technical evidence baseline for current-product conclusions:

`8dcb0a5d7ce1be9d82e3448c01cdc1643e3ac8c4`

Later commits on the integration branch may contain research-only documents. Do not mistake research-document commits for product changes.

## B2. Read the research pack

Now read:

1. `project_control/research/RESEARCH_STATUS_2026-09-27.md`
2. `project_control/research/FINAL_DEEP_RESEARCH_SYNTHESIS_2026-09-27.md`
3. `project_control/research/DR-03_RUNTIME_ARCHITECTURE_2026-09-26.md`
4. `project_control/research/DR-04_DELIVERY_THROUGHPUT_2026-09-26.md`
5. `project_control/research/DR-04B_CI_COST_2026-09-27.md`
6. `project_control/research/DR-04C_GOVERNANCE_SERIALIZATION_2026-09-27.md`
7. older `REPO_DEEP_RESEARCH_2026-09-26.md` only when needed for DR-00/01/02 evidence.

Treat these as a researcher's evidence pack, **not as authority**. Independently verify important claims against exact source/history and explicitly record any finding you reject or revise.

## B3. Read authoritative current-state/control material

Inspect at minimum:

- `project_control/AUTONOMY_RUN_STATE.yaml`
- `project_control/TASK_REGISTRY.yaml`
- `project_control/SLICE_REGISTRY.yaml`
- relevant evidence/index files only as needed;
- `web/`;
- `supabase/`;
- `.github/workflows/`;
- accepted implementation/review artifacts needed to understand why a design exists;
- relevant Git history and CI runs.

If current Vercel/Supabase read-only tooling is available, inspect current cloud state without changing anything.

Use current official documentation for time-sensitive platform questions, especially:

- Next.js 16 runtime/proxy conventions;
- Supabase SSR auth/session handling;
- Supabase API-key model;
- Supabase migration/environment best practice;
- Vercel Preview/Production and artifact-promotion behavior.

## B4. Audit questions

Audit the current project for:

### Product completeness

- Which Phase-1 journeys actually work end-to-end?
- Which modules only have backend contracts but no usable UI?
- Which buttons/actions imply behavior that does not happen externally?
- Which future-scope features are incorrectly on the critical path?

### Correctness/security

- Auth/session lifecycle;
- RBAC/RLS boundaries;
- server/admin-key isolation;
- privacy/data exposure;
- transaction/concurrency design;
- idempotency/fencing;
- unsafe error propagation/logging;
- storage/document safety.

### Architecture

- Which layers solve real problems?
- Which layers duplicate responsibility without added safety?
- Which abstractions are inconsistent?
- Which large components should be split only when it materially improves delivery?

### Operational readiness

- Vercel deployment readiness;
- Supabase remote migration readiness;
- environment-variable contracts;
- auth redirects/providers;
- external email delivery;
- malware scanning;
- scheduled workers/cleanup;
- PDF/export behavior;
- runbook/rollback/observability.

### Delivery system

- which review gates found real bugs and must stay;
- which gates duplicate the same proof;
- commit/evidence SHA amplification;
- CI cost and path-awareness;
- planner/task-state blind spots;
- whether `DONE` means technical prerequisite complete or user-facing product complete.

### Maintainability

- complexity hot spots;
- test maintenance cost;
- migration maintenance risk;
- dead code/prototype/review artifacts that confuse execution;
- whether repo-local skills/process assets help or obstruct normal engineering.

## B5. Required Phase-B artifact

Write:

`project_control/astra_review/ASTRA_CURRENT_STATE_AUDIT.md`

Every major finding must have:

- severity: P0 / P1 / P2 / P3;
- evidence path/SHA/run where applicable;
- impact on user/product/security/delivery;
- whether the deep-research pack was CONFIRMED / REVISED / REJECTED;
- confidence level;
- whether it blocks a safe Vercel Preview, production, or neither.

Do not modify implementation.

---

# PHASE C — FROZEN-GREENFIELD VS CURRENT GAP MATRIX

Compare Phase A without editing it.

For each subsystem classify the current state as one of:

- KEEP
- SIMPLIFY
- FIX
- ADD
- REPLACE
- REMOVE / DEFER

At minimum cover:

- product scope and navigation;
- Candidate/Auth;
- Application/Submission Inbox;
- Interview;
- Reports;
- Master Data;
- Users & Permissions;
- DB schema;
- RLS/RBAC;
- RPC/command architecture;
- Storage/upload;
- malware scanning;
- Email;
- cleanup/background work;
- PDF/export;
- error/logging/observability;
- CI;
- independent review;
- governance/control plane;
- Vercel release;
- Supabase release/migrations;
- environment/secrets/runbooks.

For every row include:

- Greenfield target;
- Current state;
- Classification;
- Evidence;
- User/business value;
- correctness/security risk;
- estimated effort (S/M/L/XL, not fake calendar precision);
- migration cost;
- dependencies;
- confidence;
- why KEEP is justified from first principles, or why replacement beats repair.

Write:

`project_control/astra_review/ASTRA_GAP_MATRIX.md`

---

# PHASE D — THREE RECOVERY OPTIONS

Produce three genuinely distinct options.

## Option A — Continue current architecture with minimal repair

Preserve nearly everything and close only critical gaps.

## Option B — Selective recovery / simplification

Preserve proven invariants and flows, simplify costly plumbing/process, and add missing end-to-end/product/operational pieces.

## Option C — Larger rebuild / rewrite

Rebuild substantial layers or the whole system only where the evidence supports it.

Do NOT assume Option B wins just because it sounds balanced.

For each option quantify qualitatively:

- time-to-first-working Vercel Preview;
- time-to-usable Phase-1;
- implementation effort;
- regression/security risk;
- migration risk;
- amount of current work retained;
- amount of verified behavior that must be re-proven;
- operational/deployment work;
- ongoing maintenance burden;
- governance/review burden;
- reversibility.

Then choose one recommended option and explain why the others lose.

Explicitly answer:

> Is a full rewrite justified? YES or NO. What evidence would have to change your answer?

Write:

`project_control/astra_review/ASTRA_RECOVERY_OPTIONS.md`

---

# PHASE E — RECOMMENDED RECOVERY PLAN

Planning only. Do not implement.

Create the shortest safe execution plan for the chosen option.

The plan must separate:

1. **Preview blockers** — required before a trustworthy Vercel + Supabase non-production preview.
2. **Phase-1 product completion** — required for real user workflows.
3. **Production hardening** — required before real candidate/personnel data and production promotion.
4. **Process simplification** — governance/CI/review improvements that reduce cycle time without weakening meaningful safeguards.
5. **Deferred work** — explicitly outside the critical path.

For each proposed execution slice include:

- objective;
- exact user/product outcome;
- source area likely affected;
- dependencies;
- acceptance criteria;
- minimum tests/review required;
- whether connected Vercel/Supabase mutation is required;
- explicit Owner approval gate if an external mutation is required;
- rollback/reversibility notes;
- what NOT to expand into during that slice.

Use P0/P1/P2 priority and dependency order rather than invented deadlines.

The first milestones should maximize the chance of seeing a real end-to-end product running safely on Vercel Preview with non-production Supabase as early as possible.

Write:

`project_control/astra_review/ASTRA_RECOMMENDED_RECOVERY_PLAN.md`

---

# REQUIRED CROSS-CHECK QUESTIONS

Before finalizing Phase E, answer all of these explicitly:

1. Why has this project taken so long? Separate useful robustness from avoidable process overhead.
2. Which security/concurrency mechanisms caught real defects and must remain?
3. Which review/CI/governance transitions can be simplified without weakening safety?
4. Are mandatory user-facing requirements being masked by backend-only task/slice completion semantics?
5. Which current modules are genuinely end-to-end usable today?
6. What is the fastest safe route to the first real Vercel Preview backed by non-production Supabase?
7. What cloud state must be verified before any production deployment?
8. Which external runtimes are genuinely mandatory for launch?
9. Must live email, malware scanning, PDF and cleanup automation all block Phase-1 launch, or should any product requirement be narrowed? Justify individually.
10. What must be operational before real candidate data is allowed into the system?
11. Which current architecture decisions would you make again today from first principles?
12. Which current complexity would you refuse to rebuild if starting today?
13. What should be deleted/deferred from the critical path immediately?
14. Is full rewrite justified? Give a binary answer and evidence.

# FINAL RESPONSE FORMAT

After all phases are complete, return a concise executive summary containing:

1. `Recommended strategy`
2. `Full rewrite verdict`
3. `Top 5 reasons delivery has been slow`
4. `Top 5 things worth preserving`
5. `Top 10 recovery actions in dependency order`
6. `First safe Vercel + Supabase Preview path`
7. `Owner decisions required`
8. links/paths to the five Astra review artifacts.

Do not bury blockers in prose. Surface P0/P1 findings first.

# Governing principle

> Do not optimize for preserving sunk cost. Do not optimize for rewriting either. Optimize for the shortest safe path from the actual current state to the intended product.

And:

> Any recommendation to preserve the current design must be justified from first principles, not merely because the implementation already exists.
