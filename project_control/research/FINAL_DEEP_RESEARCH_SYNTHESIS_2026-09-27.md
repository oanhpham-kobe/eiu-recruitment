# EIU Recruitment — Final Deep Research Synthesis

Status: COMPLETE
Date: 2026-09-27
Repository: `oanhpham-kobe/eiu-recruitment`
Research branch: `autonomy/continuous-integration-20260905-01`
Immutable technical evidence baseline: `8dcb0a5d7ce1be9d82e3448c01cdc1643e3ac8c4`
Accepted product checkpoint immediately below that governance-only closure: `0d8c5c2129ed4c78a58c8d37bd22e93c14a763eb`

## Purpose

This document reconciles DR-00 through DR-07 into one source of truth for strategic recovery review. It is intentionally evidence-oriented and distinguishes verified facts from connected-environment unknowns.

It does not authorize implementation, Vercel deployment, connected Supabase mutation, `main` changes, production-secret use, or TASK-S08-002 materialization.

## Executive verdict

**Do not full-rewrite the project.**

The shortest safe path is **selective recovery + productionization**:

1. preserve the sound Next.js + Supabase architecture, database invariants, RLS/RPC authorization, accepted business workflows, and high-value concurrency/security tests;
2. fix a small number of runtime/platform blockers;
3. add the missing Phase-1 user-facing and operational capabilities;
4. simplify command plumbing, component orchestration, governance serialization, and CI/evidence repetition without removing independent review where it has demonstrated value;
5. prove the system end-to-end on an isolated Supabase dev/staging environment and Vercel Preview before any production promotion.

The project is not mainly suffering from an unusable architecture. It is suffering from a combination of **product-completeness blind spots, operationalization gaps, and unusually high review/governance serialization cost**.

## Corrections made during final reconciliation

Two temporary research hypotheses were disproved and must not be carried forward:

- **Postgres-version mismatch: DISPROVED.** Local `supabase/config.toml` uses Postgres 17 and the currently connected Supabase project also reports Postgres 17. There is no verified PG17-vs-PG15 mismatch.
- **Existing READY Vercel Preview deployments: DISPROVED for current connected state.** The current Vercel project exists but currently returns zero deployments. There is therefore no current cloud deployment proving runtime behavior.

A prior cloud RLS-warning hypothesis is also excluded from this synthesis because the Supabase project is currently INACTIVE and live security/migration state cannot be reliably verified. Source migrations do explicitly enable RLS and local CI replays those migrations successfully.

## DR-01 — Product truth and completeness

Canonical Phase-1 user flow is broadly:

Candidate -> Submission -> Application -> Interview rounds -> Reports.

Canonical internal Phase-1 navigation requires five user-facing modules:

1. Phiếu ứng tuyển
2. Interview
3. Báo cáo
4. Danh mục
5. Người dùng & Phân quyền

Dashboard/KPI/Candidate Database are future scope and should remain deferred unless product authority changes.

### Verified gap

Runtime currently exposes the first three modules, while Master Data and Users & Permissions management UI are absent.

This is not merely missing navigation. TASK-S06-001 deliberately excluded the Master Data management page and TASK-S06-002 deliberately delivered backend/security contracts for a later Users & Permissions UI. Slice-06 nevertheless reached DONE with no materialized follow-on UI task.

**Conclusion:** backend prerequisite completion was allowed to stand in for user-facing slice completion.

## DR-02 — Control-plane/state semantics

The control plane is not fundamentally broken, but its completeness model has an important blind spot:

- task/slice validators reason over materialized tasks;
- therefore a mandatory product obligation that is never materialized can disappear from DONE logic;
- this explains how required UI work can remain missing while a supporting slice is marked DONE.

The planner/state model must distinguish:

- backend/platform contract completion;
- user-facing product requirement completion;
- operational production readiness.

A slice should not be considered product-complete merely because every currently materialized task is DONE.

## DR-03 — Runtime architecture verdict

### KEEP

The core architecture is coherent and worth preserving:

- Next.js application runtime in `web/`;
- Supabase/Postgres persistence;
- Server Actions/read adapters into typed command/domain layers;
- RPCs for mutation/transaction boundaries;
- RLS and database permission checks;
- optimistic version/concurrency contracts;
- server-only admin/service client boundaries;
- candidate, submission, application, interview, and report domain models already accepted through independent review;
- storage cleanup lease/fencing design.

Multiple authorization checks across UI capability, server command and DB/RLS layers are mostly valid defense-in-depth, not sufficient evidence of architectural failure.

### SIMPLIFY

- standardize several different command-adapter styles into one or two consistent patterns;
- split very large client orchestration components incrementally into workflow hooks/subcomponents;
- reduce repetitive manual DTO/error plumbing where it does not strengthen invariants;
- consolidate logging/error redaction conventions.

### HARDEN

- unexpected provider/database errors should not be reflected verbatim to clients;
- raw `console.error(...error.message)` usage should be normalized through a redacting logger;
- retain DB-side authorization as the final authority.

None of these issues justify a framework or data-model rewrite.

## DR-04 — Why delivery has taken so long

The answer is mixed: **some complexity bought real safety; some lifecycle ceremony amplified throughput cost.**

### High-value complexity to retain

Representative S06 review rounds caught real defects involving:

- private identity exposure (`auth_user_id`);
- lock ordering / deadlock risk;
- participant revalidation;
- Google identity rebind behavior;
- concurrency and authorization invariants.

Therefore independent review and high-risk concurrency/security regression coverage must not be removed indiscriminately.

### Process amplification to simplify

Representative task histories show large producer commit counts, repeated evidence persistence, exact-SHA re-review, state transitions and CI gates around comparatively smaller serialized product deltas.

One historical S06 governance-only `[full-ci]` final gate repeated a roughly four-minute full integration suite immediately after a similar full product verification. Later S07/S08 behavior improved: path-aware Integration CI can validate governance-only SHAs in seconds while skipping Web/DB.

Current policy already supports impacted-domain verification. The optimization target is therefore lifecycle convention, not fundamental CI capability.

Recommended governance shape:

1. review the actual serialized product SHA;
2. keep independent review evidence on append-only/non-candidate evidence branches where possible;
3. avoid making an evidence-only commit become a new review target unless necessary;
4. run impacted-domain CI rather than broad `[full-ci]` after an unchanged green product SHA;
5. atomically persist accepted task state once review/CI facts are known;
6. keep a separate slice-closure transition only when composition PASS creates a genuinely new fact.

Do not retain a mandatory second integration-audit gate when the final independent equivalence review already proves the same equivalence claim.

## DR-05 — Vercel + Supabase production readiness

### Current source/runtime

`web/` is the actual Next.js runtime. `recruitment_webapp/` is primarily design/review/prototype material and is not the main deployable runtime.

The app uses Next.js 16.3.4, React 19, `@supabase/ssr`, and `@supabase/supabase-js`.

The app's Supabase environment split is broadly sound:

- public URL + publishable/anon fallback for browser/server user-scoped clients;
- server-only privileged admin key;
- admin client disables session persistence/refresh.

### P0/P1 auth-session gap

The current `web/src/middleware.ts` adds CSP/security headers but does not implement Supabase SSR token refresh/cookie propagation.

At the same time, `web/src/lib/supabase/server.ts` explicitly relies on a proxy refreshing sessions when Server Components cannot set cookies.

Current Supabase Next.js guidance requires a request proxy that:

- creates a request-scoped Supabase SSR client;
- calls `auth.getClaims()` to refresh/validate the session;
- propagates refreshed cookies to both the request and response;
- preserves Supabase cache headers to prevent CDN/session leakage.

Next.js 16 also uses the `proxy.ts` convention rather than the old middleware convention.

**Recommended fix:** migrate/merge the current CSP/security-header logic into a Next.js 16 `proxy.ts` flow that also performs Supabase session refresh, while preserving all refreshed cookies and cache-control headers.

This should be completed before real production authentication is considered ready.

### Auth cloud configuration still unverified

Source implements:

- Candidate email OTP;
- internal Google OAuth restricted toward `eiu.edu.vn` through `hd` hint plus server provisioning controls;
- callback code exchange and open-redirect defense.

Before Vercel Preview/Production, cloud Supabase Auth must verify:

- preview/custom-domain redirect allow-list;
- production Site URL;
- Google provider configuration and callback URL;
- OTP/email settings appropriate for actual candidates.

Local `config.toml` localhost URLs are development configuration, not proof of cloud settings.

### Current API-key transition risk

Source already prefers `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY` for public use, with anon fallback.

The privileged admin path still reads `SUPABASE_SERVICE_ROLE_KEY`.

As of this research date, Supabase recommends migrating from legacy `anon` / `service_role` keys to publishable / secret keys; legacy keys are documented as continuing only through the end of 2026.

Recommended near-term release task:

- prefer a new server-only Supabase secret key with temporary legacy fallback;
- verify every worker/webhook/backend caller before deactivating legacy service-role use;
- never expose secret/admin keys to client bundles.

This key migration should not be allowed to obscure higher-priority functional Preview validation, but it is now close enough to the legacy sunset to belong in release-readiness planning.

### Connected Supabase state

Current connected project:

- name: `eiu-recruitment-dev`
- region: `ap-southeast-1`
- state: INACTIVE
- Postgres: 17
- current branch listing: empty

Because the project is inactive, live migration history, database contents, auth provider settings and security-advisor state are not considered verified by this research.

Source migrations do enable RLS and full local CI successfully replays migrations from zero.

Before any production claim, use a clean/isolated remote dev or staging target to prove remote migration replay and cloud behavior.

### Connected Vercel state

Current team contains Vercel project `eiu-recruitment`.

Current deployment list returns **zero deployments**.

Therefore CI build success has not yet been converted into a verified Vercel Preview runtime.

No production deployment should be attempted as the first cloud proof. The next safe cloud milestone is an isolated Preview connected to a dev/staging Supabase environment.

### Missing deployment/release operations

The repo currently lacks a trustworthy application deployment runbook:

- `web/README.md` is still the default create-next-app README;
- no dedicated production Vercel release workflow was found;
- no Supabase staging/production migration deployment workflow was found;
- env matrix / rollback procedure / remote migration recovery procedure are not captured as an operational contract.

These are ADD items, not reasons to redesign the business application.

## DR-06 — External runtime and Phase-1 operational gaps

### Email delivery

Current UI and command layer preview and enqueue interview email into durable DB contracts and expose Email History.

No actual email provider/sender runtime was found in the deployable web package. There is no SMTP/Resend/SendGrid/etc dependency and no sender worker/launcher.

**Current meaning of Send:** enqueue for delivery, not verified external delivery.

ADD:

- actual provider adapter;
- bounded/idempotent sender worker;
- retry/failure handling mapped to accepted outbox/history contracts;
- production secret/config boundary;
- operational invocation (cron/worker).

### Malware scanning

Current upload inspection is useful and should be kept. It verifies file size, checksum, magic bytes and MIME consistency against quarantined storage.

It is not an actual malware engine and does not independently produce a real malware verdict.

ADD either:

- a real scanning provider/worker integrated with the accepted result-fencing contracts; or
- an explicit product/security decision that narrows the launch requirement.

Do not silently treat magic-byte inspection as malware scanning.

### Storage cleanup

A strong bounded cleanup runner already exists with claim/lease, authorization, provider removal, fencing and completion semantics.

No production scheduler/API/daemon/worker launcher was found.

KEEP the runner core; ADD only the operational execution path and observability.

### PDF

HR Reports currently render/report-manage in UI, but the PDF action is intentionally disabled with an “official PDF template pending” message.

ADD PDF output only after the canonical template/output requirement is settled. Avoid architecture churn around PDF before the template contract is known.

## DR-07 — Recovery matrix

### KEEP

- Next.js + Supabase stack;
- Postgres schema core and migration history as source artifacts;
- RLS/RBAC model;
- RPC transaction/concurrency invariants;
- candidate/submission/application/interview/report accepted flows;
- storage quarantine/inspection contracts;
- cleanup fencing contracts and runner;
- email outbox/history contracts;
- path-aware Integration CI;
- independent review for security/concurrency/high-risk work;
- immutable accepted checkpoints as evidence.

### SIMPLIFY

- command adapter/plumbing styles;
- oversized client orchestration components, incrementally;
- review/evidence commit serialization;
- unnecessary exact-SHA evidence amplification;
- broad CI reruns after evidence-only changes;
- state/traceability semantics so product completeness cannot be inferred only from materialized tasks.

### FIX

Priority 0 / before trustworthy cloud preview:

- Supabase SSR session-refresh proxy on Next.js 16 while preserving CSP/security headers;
- establish a clean remote dev/staging migration target and prove migration replay/history;
- define Preview environment variables and auth redirect/provider configuration.

Priority 1:

- error/logging redaction consistency;
- product completeness state model;
- environment/runbook/rollback documentation;
- Supabase legacy privileged-key migration plan.

### ADD for Phase-1 completion

- Master Data management UI;
- Users & Permissions UI;
- real email sender/provider runtime;
- real malware scan runtime or explicitly narrowed launch requirement;
- cleanup scheduler/worker invocation;
- PDF generation after template authority is settled;
- Vercel Preview + smoke/E2E checks;
- remote Supabase release/migration workflow;
- `.env.example` or equivalent environment matrix without secrets;
- deployment and rollback runbook.

### DEFER / REMOVE FROM CRITICAL PATH

- Dashboard/KPI/Candidate Database future scope;
- broad framework rewrite;
- data-model rewrite without concrete broken invariant evidence;
- cosmetic architecture refactors that do not unblock Phase-1;
- full decomposition of every large component before end-to-end validation;
- duplicate governance/audit gates that prove the same already-covered fact.

## Recommended release topology

The preferred safe delivery sequence is:

1. pin an accepted product baseline;
2. run local Web + DB verification, including `supabase db reset` from zero;
3. prepare or restore an **isolated non-production Supabase dev/staging target**;
4. compare migration history and dry-run pending migrations before applying anything remotely;
5. apply migrations only to that non-production target;
6. configure a Vercel Preview against that target;
7. verify Candidate OTP, internal Google OAuth, redirect allow-list and session refresh over time;
8. run smoke/E2E for Submission -> Application -> Interview -> Reports;
9. verify document quarantine/scan decision, email delivery path, cleanup invocation and report/PDF behavior according to the accepted launch scope;
10. only after Preview/staging passes, define an explicit production migration gate;
11. build once and promote the verified Vercel artifact rather than rebuilding an unverified variant where practical;
12. perform production smoke checks with a documented rollback procedure.

The currently connected Supabase project is named `eiu-recruitment-dev`; treat it as development/staging unless the Owner explicitly assigns another role.

## Facts versus currently unverified cloud state

### Verified from source / CI / current connectors

- accepted S08 product candidate received full Web + DB Integration CI PASS;
- DB CI replays migrations from zero and executes extensive regression/concurrency assertions;
- source migrations explicitly establish RLS across protected domain tables;
- connected Supabase project exists, is PG17 and currently INACTIVE;
- connected Vercel project exists and currently has zero deployments;
- source lacks complete Supabase SSR refresh proxy behavior;
- source lacks two required Phase-1 admin UIs;
- email delivery provider/worker is absent;
- true malware provider/runtime is absent;
- cleanup runner exists but production invocation is absent;
- PDF output is intentionally pending.

### Not verified while connected Supabase is inactive / Vercel has no deployments

- remote migration history parity;
- remote schema/data parity;
- current cloud RLS/policy state;
- Google OAuth provider settings;
- candidate OTP production email behavior;
- production/preview auth redirect allow-list;
- Vercel root-directory/build/env configuration correctness;
- Vercel server/edge runtime behavior;
- production secrets and key rotation readiness;
- real-world external email/scanner/cleanup/PDF behavior.

These must be resolved through a controlled non-production Preview/staging proof, not by inference from local CI.

## Final strategic conclusion

The project has significant sunk work, but the recommendation to preserve much of it is **not based on sunk cost**. It is based on first-principles evidence that the current DB authorization/concurrency model, accepted workflows and CI regression set solve real hard problems correctly enough to be reusable.

The largest opportunity is to stop treating more contracts/reviews as a substitute for end-to-end product completion. The next planning system should optimize for the shortest safe route to a real Vercel Preview backed by a validated Supabase dev/staging environment, then close the visible and operational Phase-1 gaps.

A full rewrite should be selected only if a fresh greenfield architecture review demonstrates a materially shorter safe route after accounting for migration, re-validation and reimplementation of already-proven security/concurrency invariants.

## Astra review entry points

Astra should not consume this file before completing its source-blind greenfield Phase A.

After Phase A is frozen, the recommended source pack is:

- `project_control/research/RESEARCH_STATUS_2026-09-27.md`
- `project_control/research/FINAL_DEEP_RESEARCH_SYNTHESIS_2026-09-27.md`
- `project_control/research/DR-03_RUNTIME_ARCHITECTURE_2026-09-26.md`
- `project_control/research/DR-04_DELIVERY_THROUGHPUT_2026-09-26.md`
- `project_control/research/DR-04B_CI_COST_2026-09-27.md`
- `project_control/research/DR-04C_GOVERNANCE_SERIALIZATION_2026-09-27.md`
- authoritative `project_control/AUTONOMY_RUN_STATE.yaml`, `TASK_REGISTRY.yaml`, `SLICE_REGISTRY.yaml`
- actual `web/`, `supabase/`, `.github/workflows/`
- technical baseline `8dcb0a5d7ce1be9d82e3448c01cdc1643e3ac8c4`

Astra is expected to independently verify or reject these findings rather than treating this synthesis as authority.
