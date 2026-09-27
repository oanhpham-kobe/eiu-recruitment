# EIU Recruitment — Phase E recommended recovery plan

## 1. Executive recovery strategy

RECOMMENDED_OPTION: A

FULL_REWRITE_JUSTIFIED: NO

PHASE_E_PLAN_STATUS: READY_FOR_OWNER_REVIEW

Implement the accepted strongest Option A: minimal architectural churn, full mandatory product scope and actual security/concurrency proof. Retain justified domain identities, PostgreSQL transaction authority, user-context clients, contextual RLS/RBAC, history, resource serialization, idempotency, private Storage, scan/cleanup fencing and useful current UI. Repair unsafe behavior; add missing capabilities. A necessary feature-owned extraction is allowed; a cross-project command/state rewrite is not.

This artifact is planning only. REC labels are not official tasks and create no execution permission. Nothing is inserted into task/slice/autonomy registries, no implementation branch is created, and no product/cloud/configuration change is made. Owner review and a separate bounded execution authorization are prerequisites to any implementation. All tests and operational actions below are future acceptance requirements, not claimed results.

The earliest package is REC-01 plus REC-03: a genuinely disposable database proof substrate and repaired direct-role confidentiality, including affected existing consumers. Auth/session work REC-02 can begin independently where it does not require the DB harness; composed SQL repair REC-04 uses that harness. No need to finish every new screen before the bounded functional cohort REC-13. No permission to call that cohort Phase-1 complete.

## 2. Planning assumptions and evidence limits

Repository: oanhpham-kobe/eiu-recruitment. Review branch: review/astra-strategic-review-20260927. Starting pushed commit: a270aaedfa20da63662352c05cf288eba73d4f6a. Immutable technical baseline: 8dcb0a5d7ce1be9d82e3448c01cdc1643e3ac8c4. Baseline-to-start diff contains only twelve review/research Markdown files; review commits are not runtime implementation.

Controlling handoff: project_control/research/ASTRA_MEDIUM_MASTER_HANDOFF_2026-09-27.md:385-439. Current Owner continuation specifies the fields, gates and five groups below. Frozen inputs under project_control/astra_review/ were checked before planning:

| Phase | Artifact | SHA-256 | Final marker |
|---|---|---|---|
| A | ASTRA_GREENFIELD_PHASE1_ARCHITECTURE.md | 646adc6ff4081c7f748b4191f740e0c3b1971857567788668ace41b2907dabe8 | GREENFIELD_PHASE_A_FROZEN: YES |
| B | ASTRA_PHASE_B_CURRENT_STATE_AUDIT.md | a4e370c4cef7620c943acdbc417017ad7948cc3ee2098d7a7240bf142db7f83e | PHASE_B_CURRENT_STATE_AUDIT_FROZEN: YES |
| C | ASTRA_GAP_MATRIX.md | d283981d28634bd88b79c4aaec088928c72c0d3bab73a92eeab3ae5a55efa55b | PHASE_C_GAP_MATRIX_FROZEN: YES |
| D | ASTRA_RECOVERY_OPTIONS.md | 8113d8dd59e506c425719abcb5af4ad8014a3de9ce7c75f85490adee260a618f | PHASE_D_RECOVERY_OPTIONS_FROZEN: YES |

A remains accepted with isolation/product-ambiguity caveats. B F01 has historical browser reproduction; F02/F04–F07 are source findings, not claimed production incidents or executed Phase-E SQL results. Docker was unavailable in B. REC-01 requires successful disposable execution, not another source-only substitute; unavailability blocks runtime acceptance but does not license shared/production testing. NO LOCATED REPOSITORY RUNTIME does not mean no external service exists. Current cloud/provider/data volume remains unknown. This planning phase performs no cloud inspection or mutation.

Evidence references A R01–R32 and C row IDs resolve through the frozen requirement ledger/matrix and its exact source catalog. D §§6–12 supply composed repair, migration and proof constraints. Additional decisive canonical checks: review_pack/38_NON_FUNCTIONAL_REQUIREMENTS.md (measured latency/load, recovery, logs, rate limits); 39_SECURITY_RLS_MATRIX.md:69-89 (direct-table confidentiality); 06_INTERVIEW_REPORT_HR_AND_INTERVIEWER.md:150-207 (source metadata, merge tension, Current Round PDF); 09_MASTER_DATA_CATALOG.md (all catalog entries, history and optional fields); 44_DEPLOYMENT_OPERATIONS.md; maintenance runbooks 66/78. All these filenames are under recruitment_webapp/review_pack/. No generic framework guidance overrides canonical requirements.

Two read-only specialist reviews checked trust-boundary and product/runtime omissions; the parent accepted only source-grounded constraints and owns this plan. Supported framework/SDK versions and current official docs must be checked during authorized implementation before prescribing Proxy APIs, key migration or hosting limits. This plan does not mandate a middleware rename, vendor or platform upgrade.

## 3. Completion-boundary definitions

| Boundary | Required meaning |
|---|---|
| DIAGNOSTIC PREVIEW | Explicitly authorized, isolated synthetic deployment for observing limitations. A static shell, queued message or mocked verdict is not functional UAT. Target isolation still required. No separate diagnostic detour is on the critical path. |
| FUNCTIONAL UAT PREVIEW | REC-13 declared multi-persona workflow with real test Auth/scan/mail effects, actual deployed SHA, denied/stale/pending/refresh evidence, no real recruitment PII. |
| PHASE-1 PRODUCT COMPLETENESS | Milestone PHASE1_COMPLETE: all mandatory capabilities and retained behaviors proven through REC-27, not a task count or a subset demonstration. |
| PRODUCTION | Milestone PRODUCTION_READY: complete product plus target-specific parity, recovery/monitoring/security/Legal evidence and separately approved production migration, app promotion and real-data admission. |

Priority does not determine execution order. A P1 provider/runtime or authority decision may gate demonstration of a P0 fix. Safety findings keep their frozen severity even where a composed slice has a different scheduling priority. No day/week estimates are invented.

## 4. Recovery slice ledger

There are **37 planning slices**, each with one dominant timing classification. Dependencies are acceptance edges: safe preparation can overlap, but acceptance waits for the named prerequisite. Each card's Owner gates apply in addition. A held authority gate is a real dependency, not implied approval. Group D essential product-truth correction is classified separately from optional process economy.

Groups: **A. PREVIEW BLOCKERS; B. PHASE-1 PRODUCT COMPLETION; C. PRODUCTION HARDENING; D. PROCESS / GOVERNANCE SIMPLIFICATION; E. EXPLICITLY DEFERRED WORK.**

Shared explicit profiles used by every card:

- **INV (not changed):** accepted historical migrations/checkpoints, durable identities/history/acknowledgements/audit, required permission/Root/ownership semantics, idempotency, resource conflicts, field merge, private object/scan/cleanup trust and frozen A/B/C/D. A named defect may change implementation, never silently reduce the invariant. No framework/database/full-frontend replacement or generic platform.
- **L1:** locked installed toolchain, type/lint/build for changed application domain; deterministic behavioral/validation/error tests where appropriate; actual changed-path smoke. Do not create source-text/wiring/mock-echo proof or repin incidental wording tests. Reuse adequate tests and retire inadequate incidental tests only within authorized touched scope.
- **PG1:** uniquely identified unlinked disposable local Supabase/PostgreSQL, clean ordered migration replay and baseline-to-repair upgrade on representative synthetic history; inspect exact effective function/policy/grant definitions. Privileged fixture setup is separate from assertions using real anon/authenticated/worker role and trusted synthetic identity; record current_user and non-superuser/non-BYPASSRLS status. Two independent sessions with deterministic barriers/observed waits, bounded timeouts and final-state assertions when concurrency is implicated, not sequential calls/blind sleeps. Never inherit hardcoded shared dev-container targets or use production as fallback. Reuse proof across slices only when unchanged invariant and exact candidate provenance justify it.
- **B1:** exercise actual application surfaces with legitimate synthetic identities, browser/server/RPC paths and observable persisted state; no harness-only or privileged fixture-login equivalence. Local Auth-issued test sessions can establish direct existing-consumer confidentiality before the broken browser-login consumer is repaired; that does not count as real provider UAT. Capture failure/stale/denied states, dirty/focus preservation and close test sessions afterward.
- **CI1:** exact candidate SHA and required domain gates; preserve independent high-risk review/re-review, accepted checkpoint and slice composition. Pending REC-34, satisfy both known obligations conservatively by including DB integration for integration commits and all affected/shared domains. This is not a source-conflict resolution or authorization to alter CI. If current procedure prevents acceptance, escalate O-CI-SOURCE rather than self-waive. Path selection and full-ci broadening cannot suppress mandatory proof; no remote apply/deploy secret use is automatic CI permission.
- **EV:** exact implementation SHA plus baseline/diff, approved scope, source/finding coverage, effective migration/catalog evidence when relevant, fresh command exit/results and actual runtime/browser/provider outcomes, independent review disposition, exact-SHA CI and compatible checkpoint. Record target/time and sanitized configuration/receipt identities; no tokens, secret values, signed private URLs or recruitment PII. Queue/schema/DTO presence is not delivered capability.

All mutation fields describe **future authorized execution only**. O-EXEC never bundles cloud approvals. Every cloud or provider change also requires its individually named gate in §12, even if a card says conditional or acceptance Preview. No current execution permission is created.

| Planning ID | Slice | Priority | Group | Dominant classification | Acceptance dependencies |
|---|---|---|---|---|---|
| REC-01 | Disposable database proof substrate | P0 | A | MUST_BEFORE_UAT | None; Owner gates still apply |
| REC-02 | Coordinated Auth/session repair | P0 | A | MUST_BEFORE_UAT | REC-01 |
| REC-03 | Confidentiality across alternate access paths | P0 | A | MUST_BEFORE_UAT | REC-01 |
| REC-04 | Coordinated transaction correctness | P1 | A | MUST_BEFORE_UAT | REC-01 |
| REC-05 | Explicit HR open and Candidate edit boundary | P1 | A | MUST_BEFORE_UAT | REC-02, REC-04 |
| REC-06 | Read-only target and provider inventory | P1 | A | MUST_BEFORE_UAT | None; Owner gates still apply |
| REC-07 | Isolated non-production target preparation | P1 | A | MUST_BEFORE_UAT | REC-06, REC-02, REC-03, REC-04, REC-12 |
| REC-08 | Real malware execution and CLEAN continuation | P0 | A | MUST_BEFORE_UAT | REC-07 |
| REC-09 | Real operational email delivery and recovery | P1 | A | MUST_BEFORE_UAT | REC-07 |
| REC-10 | Abuse-control authority resolution | P1 | A | MUST_BEFORE_UAT | None; Owner gates still apply |
| REC-11 | Approved abuse-boundary proof and only necessary completion | P1 | A | MUST_BEFORE_UAT | REC-10, REC-02, REC-06 |
| REC-12 | Report precedence and contextual concurrency proof | P1 | A | MUST_BEFORE_UAT | REC-01, REC-03, REC-04 |
| REC-13 | First trustworthy functional UAT deployment and cohort | P1 | A | MUST_BEFORE_UAT | REC-05, REC-07, REC-08, REC-09, REC-11, REC-12 |
| REC-14 | Recurring temporary cleanup | P1 | B | MUST_BEFORE_PHASE1_COMPLETE | REC-07 |
| REC-15 | Whole HR Submission editing | P1 | B | MUST_BEFORE_PHASE1_COMPLETE | REC-03, REC-04, REC-05 |
| REC-16 | HR Submission document editing | P1 | B | MUST_BEFORE_PHASE1_COMPLETE | REC-15, REC-08 |
| REC-17 | Interview materials | P1 | B | MUST_BEFORE_PHASE1_COMPLETE | REC-03, REC-04, REC-08 |
| REC-18 | Master Data management | P1 | B | MUST_BEFORE_PHASE1_COMPLETE | REC-02, REC-04 |
| REC-19 | Users and Permissions management | P1 | B | MUST_BEFORE_PHASE1_COMPLETE | REC-02, REC-03, REC-04 |
| REC-20 | Content-correct generated PDF | P1 | B | MUST_BEFORE_PHASE1_COMPLETE | REC-03, REC-12 |
| REC-21 | Complete VI/EN workflows | P1 | B | MUST_BEFORE_PHASE1_COMPLETE | REC-15, REC-16, REC-17, REC-18, REC-19, REC-20 |
| REC-22 | Candidate mobile completion acceptance | P1 | B | MUST_BEFORE_PHASE1_COMPLETE | REC-02, REC-08, REC-11, REC-21, REC-24 |
| REC-23 | WCAG and keyboard acceptance | P1 | B | MUST_BEFORE_PHASE1_COMPLETE | REC-15, REC-16, REC-17, REC-18, REC-19, REC-20, REC-21, REC-22 |
| REC-24 | Privacy notice publication and acknowledgement rollover | P1 | B | MUST_BEFORE_PHASE1_COMPLETE | REC-01, REC-02, REC-07 |
| REC-25 | Controlled export/archive/purge capability | P1 | B | MUST_BEFORE_PHASE1_COMPLETE | REC-01, REC-07 |
| REC-26 | Measured performance and capacity acceptance | P1 | B | MUST_BEFORE_PHASE1_COMPLETE | REC-13, REC-15, REC-17, REC-20 |
| REC-27 | Complete Phase-1 product composition | P1 | B | MUST_BEFORE_PHASE1_COMPLETE | REC-13, REC-14, REC-15, REC-16, REC-17, REC-18, REC-19, REC-20, REC-21, REC-22, REC-23, REC-24, REC-25, REC-26, REC-33 |
| REC-28 | Database backup and restore proof | P1 | C | MUST_BEFORE_PRODUCTION | REC-07 |
| REC-29 | Private-object recovery and DB/object reconciliation | P1 | C | MUST_BEFORE_PRODUCTION | REC-28 |
| REC-30 | Production monitoring and operator failure response | P1 | C | MUST_BEFORE_PRODUCTION | REC-08, REC-09, REC-14, REC-26 |
| REC-31 | Identity operations, credential lifecycle and break-glass | P1 | C | MUST_BEFORE_PRODUCTION | REC-02, REC-03, REC-04, REC-07 |
| REC-32 | Production candidate promotion and real-data release | P1 | C | MUST_BEFORE_PRODUCTION | REC-27, REC-28, REC-29, REC-30, REC-31, REC-34 |
| REC-33 | Truthful feature coverage and derived status | P1 | D | MUST_BEFORE_PHASE1_COMPLETE | None; Owner gates still apply |
| REC-34 | Canonical CI authority reconciliation | P1 | D | PROCESS_IMPROVEMENT | REC-03, REC-04 |
| REC-35 | Evidence serialization and duplicate-review economy | P2 | D | PROCESS_IMPROVEMENT | REC-27, REC-33, REC-34 |
| REC-36 | Evidence-driven Option-B reassessment | P2 | D | PROCESS_IMPROVEMENT | REC-13, REC-15, REC-17 |
| REC-37 | Explicit scope-exclusion envelope | P2 | E | DEFERRED | None; Owner gates still apply |

## 5. Preview-blocker plan

### A. PREVIEW BLOCKERS

Resolve source/abuse and inventory decisions in parallel with local proof where possible. REC-01/03 first package is entirely local; REC-02 code preparation does not wait for cloud credentials or governance economy. REC-04 combines F04–F07 because outcome calls, lock acquisition and rollback interact. REC-12 resolves report semantics before report acceptance, not before independent privacy repair. REC-10/11 conservatively require approved abuse coverage before exposed functional UAT; this does not lift the existing hold or assume a full implementation is missing.

### REC-01 — Disposable database proof substrate

- **Planning ID:** REC-01
- **Priority:** P0
- **Plan group:** A
- **Backlog classification:** MUST_BEFORE_UAT
- **Objective:** Disposable database proof substrate
- **Concrete user/product outcome:** Make real isolated SQL/security/race evidence possible; no product-readiness claim
- **Problem/finding IDs:** F02,F04–F07 evidence prerequisite
- **Likely source areas:** supabase/config.toml; supabase/tests/; existing local test harness and pinned toolchain
- **Dependencies:** None among REC labels; applicable Owner execution/access gate still required
- **What is preserved:** Accepted migrations, real roles and Auth-derived identity
- **What is changed:** Restore a disposable local Supabase/PostgreSQL test facility; diagnose local engine availability without touching shared data
- **What is explicitly NOT changed:** INV below; no unrelated domain/schema/framework replacement. Only the explicitly named required repair or capability may change behavior.
- **Acceptance criteria:** Successful clean replay, exact effective-definition inventory, authenticated persona harness and deterministic two-session smoke; fail closed if unavailable
- **Required local tests:** Pinned harness startup and reset isolation checks; no repeated F01 diagnosis required
- **Required PostgreSQL/RLS/concurrency tests:** PG1: zero replay, role/JWT setup, two independent connections, rollback isolation; minimal harness smoke only PG1 also records current_user/non-BYPASSRLS and baseline-to-new migration upgrade protocol; substantive defect counterexamples belong to REC-03/04.
- **Required browser/E2E tests:** N/A — no UI changed
- **Required provider/runtime tests:** N/A — no external effect
- **Independent review requirement:** Independent database reviewer verifies genuine role context and isolation
- **CI requirement:** CI1: harness/replay and DB domain; no source-regex substitute
- **Vercel mutation:** No
- **Supabase mutation:** Local disposable only; no remote
- **External provider configuration:** No
- **Exact Owner authorization gate:** O-EXEC; O-LOCAL for any needed local installation/service permission; never shared DB substitution
- **Rollback/reversibility:** Stop/delete only disposable test resources; no business data exists there
- **Evidence required for acceptance:** EV plus startup/version/replay/catalog/two-connection logs and isolation identity
- **What not to expand into:** Remote reset, production credentials, broad test-platform rewrite
- **Completion boundary unlocked:** FUNCTIONAL UAT PREVIEW prerequisite
- **Parallel safety:** Apply §14 ownership/isolation rules; dependencies are acceptance edges, not permission for concurrent writes to shared files/databases.

### REC-02 — Coordinated Auth/session repair

- **Planning ID:** REC-02
- **Priority:** P0
- **Plan group:** A
- **Backlog classification:** MUST_BEFORE_UAT
- **Objective:** Coordinated Auth/session repair
- **Concrete user/product outcome:** Candidate and eligible staff can establish and sustain verified sessions
- **Problem/finding IDs:** F01,F18; F17 where auth errors cross boundary
- **Likely source areas:** web/src/lib/env/client.ts; lib/env/server.ts; lib/supabase/{client,server,admin}.ts; lib/auth/; app/login/; app/auth/; middleware/request entry; installed package lock
- **Dependencies:** REC-01
- **What is preserved:** Managed OTP/OAuth, business binding, user-context client, CSP and active-account checks
- **What is changed:** Static browser public-env access and supported request-layer refresh/cookie propagation; narrowly repair safe errors/cache/redirect handling
- **What is explicitly NOT changed:** INV below; no unrelated domain/schema/framework replacement. Only the explicitly named required repair or capability may change behavior.
- **Acceptance criteria:** Production-built local bundle initializes; expired/parallel refresh preserves correct request/response cookies; inactive/revoked actors denied; no privileged secret in browser; actual provider acceptance waits REC-07/13
- **Required local tests:** L1 plus env validation/build-output secret checks and refresh/redirect/cache failure cases
- **Required PostgreSQL/RLS/concurrency tests:** PG1 active/binding/Root/permission denials under refreshed identity
- **Required browser/E2E tests:** B1 local built login/refresh/locale; real OTP/Google and redirects repeated at REC-13 on target
- **Required provider/runtime tests:** Auth provider real effects in REC-07/13, not mocked acceptance here
- **Independent review requirement:** Independent auth/security review; verify actual supported Next version docs, not rename-only remedy
- **CI requirement:** CI1: web/auth plus DB persona acceptance at integration
- **Vercel mutation:** No here; target configuration in REC-07
- **Supabase mutation:** Local only here; target Auth config in REC-07
- **External provider configuration:** No here; real provider configuration separately gated
- **Exact Owner authorization gate:** O-EXEC; O-AUTH/O-ENV before connected config; future key modernization does not replace this fix
- **Rollback/reversibility:** Rollback only to safe compatible auth build; revoke test sessions; retain headers and database guards
- **Evidence required for acceptance:** EV plus built-browser trace, cookie/cache/header evidence with all tokens redacted
- **What not to expand into:** Framework upgrade/rewrite, shared actor refactor, secret-key migration as substitute for current auth
- **Completion boundary unlocked:** FUNCTIONAL UAT PREVIEW
- **Parallel safety:** Apply §14 ownership/isolation rules; dependencies are acceptance edges, not permission for concurrent writes to shared files/databases.

### REC-03 — Confidentiality across alternate access paths

- **Planning ID:** REC-03
- **Priority:** P0
- **Plan group:** A
- **Backlog classification:** MUST_BEFORE_UAT
- **Objective:** Confidentiality across alternate access paths
- **Concrete user/product outcome:** Interviewer cannot retrieve HR-only content while valid HR and contextual report access survive
- **Problem/finding IDs:** F02,F17 private-path leakage
- **Likely source areas:** New forward migration affecting effective Interview grants/RLS/projections; web/src/lib/reports/; lib/application-inbox/submission-detail-server.ts; app/api/documents/preview/[id]/route.ts; supabase/tests/
- **Dependencies:** REC-01
- **What is preserved:** Domain IDs, contextual authorization, HR access, private Storage and audit
- **What is changed:** Choose narrow grant/projection/policy repair after caller inventory; redact unexpected errors at affected boundaries; do not prescribe one physical solution
- **What is explicitly NOT changed:** INV below; no unrelated domain/schema/framework replacement. Only the explicitly named required repair or capability may change behavior.
- **Acceptance criteria:** Direct authenticated table, alternate projection, RPC, DTO and existing document/HTML paths deny HR-only fields/content to assigned/unassigned/removed Interviewers; valid HR/contextual reads pass; currently absent generated PDF has no enabled bypass and inherits REC-20 regression gate Include forbidden HR owner/final-source metadata; valid local Auth-issued persona sessions may exercise existing server/consumer paths without relying on broken browser login. This is not a privileged fixture bypass or connected UAT certification.
- **Required local tests:** L1 exposure/caller inventory and safe-error boundary checks
- **Required PostgreSQL/RLS/concurrency tests:** PG1 all exposed relations/RPCs, active/inactive/mixed roles and legitimate reader regression
- **Required browser/E2E tests:** B1 real HR vs assigned/unassigned/removed private-report/document paths; not merely hidden UI
- **Required provider/runtime tests:** Private object access/signing tests with synthetic files; remote parity repeated REC-13
- **Independent review requirement:** Independent security/database reviewer; require negative and positive direct-role proof
- **CI requirement:** CI1: DB RLS/grants plus affected web/private-document tests
- **Vercel mutation:** No
- **Supabase mutation:** Local forward migration only; remote application separately O-NP-MIG
- **External provider configuration:** No
- **Exact Owner authorization gate:** O-EXEC; O-NP-MIG only for later target application
- **Rollback/reversibility:** Keep security repair on rollback; compatible safe client or maintenance/forward repair, never restore leaking grants
- **Evidence required for acceptance:** EV plus failed-before/passed-after direct-role traces, effective grants and all-path matrix; no sensitive payload in logs
- **What not to expand into:** Generic authorization replacement, public buckets, UI-only confidentiality claim
- **Completion boundary unlocked:** FUNCTIONAL UAT PREVIEW
- **Parallel safety:** Apply §14 ownership/isolation rules; dependencies are acceptance edges, not permission for concurrent writes to shared files/databases.

### REC-04 — Coordinated transaction correctness

- **Planning ID:** REC-04
- **Priority:** P1
- **Plan group:** A
- **Backlog classification:** MUST_BEFORE_UAT
- **Objective:** Coordinated transaction correctness
- **Concrete user/product outcome:** Concurrent lifecycle actions preserve atomic outcomes, versions and resources
- **Problem/finding IDs:** F04,F05,F06,F07
- **Likely source areas:** New forward migrations over effective interview lifecycle, application reactivation/participant and copy/outcome functions; supabase/tests/; affected command consumers only if contract changes
- **Dependencies:** REC-01
- **What is preserved:** Aggregate identities, resource locks, replay fingerprints, report field merge, audit and retained history
- **What is changed:** Inventory all crossed writer/lock/outcome paths; align acquisition/revalidation, reject NULL expected versions, atomic late-batch failure, recalculate on reactivation
- **What is explicitly NOT changed:** INV below; no unrelated domain/schema/framework replacement. Only the explicitly named required repair or capability may change behavior.
- **Acceptance criteria:** Actual opposing transactions close lock-order counterexamples; successful prefix then stale failure leaves no row/outcome/audit/cleanup partial commit; reactivation derives correct latest outcome; legitimate disjoint report merge retained
- **Required local tests:** L1 only affected adapters/results; catalog effective-definition and writer inventory
- **Required PostgreSQL/RLS/concurrency tests:** PG1 plus two-session opposing create/copy/delete/reactivate/participant/resource cases; direct NULL/stale; late batch failures and replay; current/historical outcome transitions
- **Required browser/E2E tests:** B1 affected lifecycle/bulk stale/conflict results after SQL proof; no optimistic success hiding rejection
- **Required provider/runtime tests:** N/A — DB durable effects asserted, no new provider executor
- **Independent review requirement:** Independent database/concurrency review of composed order and side effects, not four isolated approvals
- **CI requirement:** CI1: full affected DB concurrency suite plus crossed web contracts at integration
- **Vercel mutation:** No
- **Supabase mutation:** Local forward migrations only; remote application O-NP-MIG later
- **External provider configuration:** No
- **Exact Owner authorization gate:** O-EXEC; O-NP-MIG for later dry run, O-PROD-MIG for production
- **Rollback/reversibility:** Additive forward repair; no unsafe down migration; safe app compatibility or scoped write pause
- **Evidence required for acceptance:** EV with exact functions, transaction timelines, bounded lock/deadlock evidence and atomic before/after sets
- **What not to expand into:** Domain/RPC platform replacement, global serialization shortcut, broad command refactor
- **Completion boundary unlocked:** FUNCTIONAL UAT PREVIEW
- **Parallel safety:** Apply §14 ownership/isolation rules; dependencies are acceptance edges, not permission for concurrent writes to shared files/databases.

### REC-05 — Explicit HR open and Candidate edit boundary

- **Planning ID:** REC-05
- **Priority:** P1
- **Plan group:** A
- **Backlog classification:** MUST_BEFORE_UAT
- **Objective:** Explicit HR open and Candidate edit boundary
- **Concrete user/product outcome:** Authorized explicit opening changes NEW to READ and ends Candidate editing
- **Problem/finding IDs:** F08; Candidate save/open race
- **Likely source areas:** web/src/components/inbox/{ApplicationInboxTable,SubmissionDetailDrawer}.tsx; app/application-inbox-actions.ts; lib/commands/submission-status.ts; Candidate edit consumer
- **Dependencies:** REC-02, REC-04
- **What is preserved:** Pure detail reads, view-only HR behavior, existing explicit open command and snapshots
- **What is changed:** Wire explicit authorized intent; handle version/stale and current-versus-historical context
- **What is explicitly NOT changed:** INV below; no unrelated domain/schema/framework replacement. Only the explicitly named required repair or capability may change behavior.
- **Acceptance criteria:** Click invokes intent once safely; passive reads and insufficient-permission reads remain nonmutating; Candidate Save vs HR-open has legal serialized result and preserved draft on rejection
- **Required local tests:** L1 intent/error/draft behavior
- **Required PostgreSQL/RLS/concurrency tests:** PG1 two-session HR open vs Candidate Save; permissions and latest/historical restrictions
- **Required browser/E2E tests:** B1 real click path, duplicate click, view-only HR, Candidate stale Save and reload
- **Required provider/runtime tests:** N/A — no new provider operation
- **Independent review requirement:** Independent product/security composition review
- **CI requirement:** CI1: affected web plus status/edit DB contracts
- **Vercel mutation:** No
- **Supabase mutation:** Local fixtures/tests only; no planned schema rewrite
- **External provider configuration:** No
- **Exact Owner authorization gate:** O-EXEC
- **Rollback/reversibility:** Revert consumer only to a safe nonmutating state with explicit incompleteness; never reopen processed history
- **Evidence required for acceptance:** EV including DB status/version and two-browser traces
- **What not to expand into:** Mutating every detail read, Inbox rewrite
- **Completion boundary unlocked:** FUNCTIONAL UAT PREVIEW
- **Parallel safety:** Apply §14 ownership/isolation rules; dependencies are acceptance edges, not permission for concurrent writes to shared files/databases.

### REC-06 — Read-only target and provider inventory

- **Planning ID:** REC-06
- **Priority:** P1
- **Plan group:** A
- **Backlog classification:** MUST_BEFORE_UAT
- **Objective:** Read-only target and provider inventory
- **Concrete user/product outcome:** Know actual isolation, schema and external runtime facts before proposing mutations
- **Problem/finding IDs:** F20; cloud/provider caveats
- **Likely source areas:** Read-only Vercel/Supabase/provider metadata; deployment source 44; no runtime edit
- **Dependencies:** None among REC labels; applicable Owner execution/access gate still required
- **What is preserved:** Existing projects and data; secret boundaries
- **What is changed:** Record sanitized names, IDs, statuses, versions and parity evidence; identify safe isolated target
- **What is explicitly NOT changed:** INV below; no unrelated domain/schema/framework replacement. Only the explicitly named required repair or capability may change behavior.
- **Acceptance criteria:** Inventory root/build/deployments/env names by environment; Supabase status/version/migrations/effective grants/RLS/auth triggers/providers/redirects/private Storage; workers/credentials presence without values; backups/recovery; unsuitable target rejected
- **Required local tests:** N/A — documentary inventory consistency
- **Required PostgreSQL/RLS/concurrency tests:** Read-only metadata only; no production business-row query or SQL mutation
- **Required browser/E2E tests:** N/A — no deploy or user-session access
- **Required provider/runtime tests:** Read-only host/provider identity and health/config evidence where allowed
- **Independent review requirement:** Independent operations/security review of isolation conclusions
- **CI requirement:** CI1 documentary scope/provenance; no platform mutation in CI
- **Vercel mutation:** Read-only only
- **Supabase mutation:** Read-only metadata only
- **External provider configuration:** Read-only only
- **Exact Owner authorization gate:** O-READ; if access unavailable record gap and block target mutation, not invent state
- **Rollback/reversibility:** No mutation to undo
- **Evidence required for acceptance:** EV sanitized inventory with observation time, target identity and unknowns
- **What not to expand into:** Dumping secrets/PII, auto-resume, provisioning replacement without decision
- **Completion boundary unlocked:** DIAGNOSTIC PREVIEW prerequisite; FUNCTIONAL UAT PREVIEW
- **Parallel safety:** Apply §14 ownership/isolation rules; dependencies are acceptance edges, not permission for concurrent writes to shared files/databases.

### REC-07 — Isolated non-production target preparation

- **Planning ID:** REC-07
- **Priority:** P1
- **Plan group:** A
- **Backlog classification:** MUST_BEFORE_UAT
- **Objective:** Isolated non-production target preparation
- **Concrete user/product outcome:** Safe synthetic environment supports real auth and reviewed database
- **Problem/finding IDs:** F20; F01/F18 environment proof
- **Likely source areas:** Vercel project/root/build/env mapping; isolated Supabase config/migrations/Auth/Storage; approved deployment configuration
- **Dependencies:** REC-06, REC-02, REC-03, REC-04, REC-12
- **What is preserved:** One modular application, reviewed migrations and existing suitable infrastructure
- **What is changed:** Create/resume only if needed and separately approved; configure nonprod env/Auth/redirects/private buckets; dry-run vetted forward migrations
- **What is explicitly NOT changed:** INV below; no unrelated domain/schema/framework replacement. Only the explicitly named required repair or capability may change behavior.
- **Acceptance criteria:** Explicit project separation, no production seed/keys, actual target effective grants/RLS/auth triggers match approved catalog; real OTP and Workspace test identities, correct redirect origin; no deployment silently promoted
- **Required local tests:** L1 configuration contracts without secret values
- **Required PostgreSQL/RLS/concurrency tests:** PG1 remote nonprod parity and representative baseline-upgrade dry run; never reset shared project
- **Required browser/E2E tests:** B1 connected Auth checks once approved preview exists at REC-13
- **Required provider/runtime tests:** Real isolated Auth SMTP/OAuth setup; business mail remains REC-09
- **Independent review requirement:** Independent operations+DB/security review of target and migration compatibility
- **CI requirement:** CI1 exact candidate build, DB replay/parity; no remote apply without gate
- **Vercel mutation:** Yes configuration; deployment only REC-13/O-DEPLOY
- **Supabase mutation:** Yes nonprod only; separate create/resume/config/migration gates
- **External provider configuration:** Yes Auth configuration where necessary
- **Exact Owner authorization gate:** O-NP-TARGET, O-ENV, O-AUTH, O-NP-MIG separately; no production scope; O-NP-CREATE or O-NP-RESUME individually if needed
- **Rollback/reversibility:** Revert safe nonprod configuration or recreate only approved disposable target; preserve evidence; forward repair schema
- **Evidence required for acceptance:** EV target IDs, approved changes, migration ledger diff, sanitized provider/redirect and catalog receipts
- **What not to expand into:** Assuming Preview equals production parity; shared PII fixtures
- **Completion boundary unlocked:** DIAGNOSTIC PREVIEW; FUNCTIONAL UAT PREVIEW
- **Parallel safety:** Apply §14 ownership/isolation rules; dependencies are acceptance edges, not permission for concurrent writes to shared files/databases.

### REC-08 — Real malware execution and CLEAN continuation

- **Planning ID:** REC-08
- **Priority:** P0
- **Plan group:** A
- **Backlog classification:** MUST_BEFORE_UAT
- **Objective:** Real malware execution and CLEAN continuation
- **Concrete user/product outcome:** Required synthetic CV is usable only after trustworthy real scanning
- **Problem/finding IDs:** F03; C X04–X06,D16
- **Likely source areas:** web/src/lib/storage/upload-scanner.ts; lib/commands/storage-reservation.ts; Candidate upload actions; new bounded executor/provider binding using existing scan SQL protocol
- **Dependencies:** REC-07
- **What is preserved:** Byte/MIME/hash inspection, reservation identity, durable claims, fencing and synchronous CLEAN finalization
- **What is changed:** Add real engine execution, narrow worker identity/launcher and authenticated result ingestion; choose vendor only after inventory/Owner decision
- **What is explicitly NOT changed:** INV below; no unrelated domain/schema/framework replacement. Only the explicitly named required repair or capability may change behavior.
- **Acceptance criteria:** Observe each seam: bytes/type/hash → durable request/claim → engine → fenced verdict → same-byte CLEAN continuation → submission; infected/unavailable/pending/forged/stale/expired/cancelled outcomes fail closed
- **Required local tests:** L1 adapter/format/error cases using deterministic local fixtures; mocks not engine proof
- **Required PostgreSQL/RLS/concurrency tests:** PG1 worker-only grants, stale fences, expiry/cancel/replay, unchanged object identity and last-CV transaction
- **Required browser/E2E tests:** B1 pending/failure/clean Candidate upload and submit with draft preservation
- **Required provider/runtime tests:** Actual selected engine with safe synthetic clean/detection fixtures, accepted Office formats, timeout/retry/privacy/runtime limits
- **Independent review requirement:** Independent storage/security and provider-privacy review
- **CI requirement:** CI1 storage/scan DB plus web; separately attributable real-engine acceptance
- **Vercel mutation:** Conditional host config/deploy only if chosen host is Vercel
- **Supabase mutation:** Yes nonprod worker credentials/config; any new SQL via O-NP-MIG
- **External provider configuration:** Yes scanner selection/credentials/host
- **Exact Owner authorization gate:** O-SCANNER, O-SECRETS, O-WORKER; O-ENV/O-DEPLOY if Vercel; O-NP-MIG if changed SQL
- **Rollback/reversibility:** Pause claims/revoke worker credentials; preserve pending/attempt evidence; never mark pending CLEAN on rollback
- **Evidence required for acceptance:** EV engine receipt/hash correlation, role/fence denials, real browser continuation and failure traces
- **What not to expand into:** Upload-model rebuild, vendor invented by agent, accepting MIME inspection as antivirus
- **Completion boundary unlocked:** FUNCTIONAL UAT PREVIEW
- **Parallel safety:** Apply §14 ownership/isolation rules; dependencies are acceptance edges, not permission for concurrent writes to shared files/databases.

### REC-09 — Real operational email delivery and recovery

- **Planning ID:** REC-09
- **Priority:** P1
- **Plan group:** A
- **Backlog classification:** MUST_BEFORE_UAT
- **Objective:** Real operational email delivery and recovery
- **Concrete user/product outcome:** Promised notifications reach allowlisted test recipients with honest status/history
- **Problem/finding IDs:** F13; C X01–X03
- **Likely source areas:** Existing email outbox SQL/command adapters; web/src/components/interview/InterviewEmailActions.tsx; bounded sender/provider/launcher
- **Dependencies:** REC-07
- **What is preserved:** Durable intent/history, permission/parent binding, leases and audit; Auth OTP separate
- **What is changed:** Add actual sender and controlled invocation; reconcile finite retry budget with canonical up-to-24h/provider-equivalent requirement
- **What is explicitly NOT changed:** INV below; no unrelated domain/schema/framework replacement. Only the explicitly named required repair or capability may change behavior.
- **Acceptance criteria:** Actual create/edit notification and manual preview/send receipt; stale recipient/version rejects; TEST routing; transient retry, permanent failure, stale-SENDING recovery and accept-then-crash ambiguity visible; enqueue never labeled delivered; authorized email history and classified deletion preserve audit
- **Required local tests:** L1 payload/recipient/status/redaction checks
- **Required PostgreSQL/RLS/concurrency tests:** PG1 exact-parent authorization, same-key/fingerprint replay, lease takeover/completion fencing and history deletion permissions
- **Required browser/E2E tests:** B1 preview/send/stale/permanent-failure/history paths; observe actual test mailbox receipt
- **Required provider/runtime tests:** Real selected provider acceptance/receipt; controlled timeout/rate failure/crash ambiguity, bounded attempts and no exactly-once promise
- **Independent review requirement:** Independent email/security and operational review; source decision if retry equivalence unresolved
- **CI requirement:** CI1 mail DB/web tests plus separately recorded provider proof
- **Vercel mutation:** Conditional chosen launcher only
- **Supabase mutation:** Yes nonprod credential/config; forward SQL only if required
- **External provider configuration:** Yes mail selection, sender domain/test routing and credentials
- **Exact Owner authorization gate:** O-MAIL, O-SECRETS, O-WORKER; O-ENV/O-DEPLOY if applicable; O-NP-MIG for SQL; O-SOURCE for retry-policy ambiguity
- **Rollback/reversibility:** Pause new sends, preserve outbox/history/receipts, reconcile in-flight accepted sends before retry; cannot unsend
- **Evidence required for acceptance:** EV recipient allowlist, receipt/attempt correlation and failure/recovery evidence with no tokens
- **What not to expand into:** Campaigns, attachments, new broker, queue-success as delivery-success
- **Completion boundary unlocked:** FUNCTIONAL UAT PREVIEW
- **Parallel safety:** Apply §14 ownership/isolation rules; dependencies are acceptance edges, not permission for concurrent writes to shared files/databases.

### REC-10 — Abuse-control authority resolution

- **Planning ID:** REC-10
- **Priority:** P1
- **Plan group:** A
- **Backlog classification:** MUST_BEFORE_UAT
- **Objective:** Abuse-control authority resolution
- **Concrete user/product outcome:** Known approved abuse requirements govern a real exposed auth/form cohort
- **Problem/finding IDs:** C Z05; existing S08-002 hold
- **Likely source areas:** Canonical NFR/security/abuse requirements and existing hold authority; source decisions only
- **Dependencies:** None among REC labels; applicable Owner execution/access gate still required
- **What is preserved:** Existing hold and mandatory Candidate rate-limit requirement
- **What is changed:** Obtain Owner/source disposition defining scope, permitted test exposure and execution authority; do not lift hold by inference
- **What is explicitly NOT changed:** INV below; no unrelated domain/schema/framework replacement. Only the explicitly named required repair or capability may change behavior.
- **Acceptance criteria:** Written canonical disposition states required controls/coverage and explicit authorization status; absent decision blocks REC-11/13, not local P0 repairs
- **Required local tests:** N/A — source/authority review
- **Required PostgreSQL/RLS/concurrency tests:** N/A — no DB change
- **Required browser/E2E tests:** N/A — no surface changed
- **Required provider/runtime tests:** Inventory/provider limits from REC-06 may inform decision, not replace authority
- **Independent review requirement:** Independent source/security review
- **CI requirement:** CI1 authorized source-change checks only in future; no registry write here
- **Vercel mutation:** No
- **Supabase mutation:** No
- **External provider configuration:** No
- **Exact Owner authorization gate:** O-ABUSE; separate O-EXEC still required for implementation; no materialization of held task
- **Rollback/reversibility:** No runtime effect; preserve decision/history if superseded
- **Evidence required for acceptance:** Approved source decision and scoped authorization, not a task status inferred from this plan
- **What not to expand into:** Silently dropping rate limits or treating plan acceptance as lifting S08-002
- **Completion boundary unlocked:** FUNCTIONAL UAT PREVIEW prerequisite
- **Parallel safety:** Apply §14 ownership/isolation rules; dependencies are acceptance edges, not permission for concurrent writes to shared files/databases.

### REC-11 — Approved abuse-boundary proof and only necessary completion

- **Planning ID:** REC-11
- **Priority:** P1
- **Plan group:** A
- **Backlog classification:** MUST_BEFORE_UAT
- **Objective:** Approved abuse-boundary proof and only necessary completion
- **Concrete user/product outcome:** Real test entry/forms are protected without breaking legitimate users
- **Problem/finding IDs:** C Z05; mandatory rate-limit evidence, not preauthorization of S08-002
- **Likely source areas:** Only source-authorized OTP/form/request/provider controls determined REC-10
- **Dependencies:** REC-10, REC-02, REC-06
- **What is preserved:** Verified identity, privacy, safe errors and provider controls that meet approved requirement
- **What is changed:** Inventory and test existing coverage first; implement only missing approved controls under separate execution authority
- **What is explicitly NOT changed:** INV below; no unrelated domain/schema/framework replacement. Only the explicitly named required repair or capability may change behavior.
- **Acceptance criteria:** Approved abuse matrix passes across instances, restart/failure and legitimate retry; authenticated and anonymous boundaries explicit; provider-only limits not assumed sufficient; no UAT exemption inferred
- **Required local tests:** L1 deterministic limit/reset/failure/legitimate-user behavior; no implementation if hold unresolved
- **Required PostgreSQL/RLS/concurrency tests:** PG1 atomicity/concurrency if durable limiter required by decision; otherwise reasoned N/A
- **Required browser/E2E tests:** B1 OTP/form recoverable denial and legitimate flow, privacy-safe error UX
- **Required provider/runtime tests:** Actual isolated provider limiting/forwarded-identity trust and fail behavior where relevant
- **Independent review requirement:** Independent security/source review of exact authorized design
- **CI requirement:** CI1 affected domains; approval precedes any new runtime code
- **Vercel mutation:** Conditional nonprod config/deploy only
- **Supabase mutation:** Conditional nonprod config/forward migration only
- **External provider configuration:** Conditional provider configuration
- **Exact Owner authorization gate:** O-ABUSE plus O-EXEC; O-ENV/O-AUTH/O-SECRETS/O-NP-MIG individually when needed
- **Rollback/reversibility:** Disable only with approved equivalent protection or suspend exposed cohort; no fail-open convenience
- **Evidence required for acceptance:** EV approved coverage matrix and multi-instance/failure evidence
- **What not to expand into:** General anti-fraud platform or unauthorized held-task implementation
- **Completion boundary unlocked:** FUNCTIONAL UAT PREVIEW
- **Parallel safety:** Apply §14 ownership/isolation rules; dependencies are acceptance edges, not permission for concurrent writes to shared files/databases.

### REC-12 — Report precedence and contextual concurrency proof

- **Planning ID:** REC-12
- **Priority:** P1
- **Plan group:** A
- **Backlog classification:** MUST_BEFORE_UAT
- **Objective:** Report precedence and contextual concurrency proof
- **Concrete user/product outcome:** Own/HR report edits have unambiguous safe precedence and confidential shared Preview
- **Problem/finding IDs:** C Z06,D13,D14; report source tension
- **Likely source areas:** Source 06/45/48 report rules; effective owner-only/HR report RPCs; web/src/lib/reports/ and existing dirty-state consumers
- **Dependencies:** REC-01, REC-03, REC-04
- **What is preserved:** Field-aware patches, ownership, decision timestamps, historical reads/current writes, independent dirty bases
- **What is changed:** Resolve actor-pair × overlap × version/provenance precedence through source authority; prove effective behavior and repair only demonstrated violations
- **What is explicitly NOT changed:** INV below; no unrelated domain/schema/framework replacement. Only the explicitly named required repair or capability may change behavior.
- **Acceptance criteria:** Owner-approved precedence matrix; direct mixed-role/current-round/removed/hidden/final-state interleavings; qualitative edits do not move decision source; blank/clear/tie/fallback correct; refresh preserves unsaved input
- **Required local tests:** L1 genuine dirty-base/conflict behavior, not source regex/fixture echo
- **Required PostgreSQL/RLS/concurrency tests:** PG1 actor pairs, disjoint/same-field, intervening writer, current-round/lifecycle race and direct forbidden calls
- **Required browser/E2E tests:** B1 two-user report edit/refresh/history/shared Preview, private fields and final decision block
- **Required provider/runtime tests:** N/A — generated PDF separately REC-20
- **Independent review requirement:** Independent report-domain/security/concurrency review
- **CI requirement:** CI1 report SQL+web contract/browser boundaries
- **Vercel mutation:** No
- **Supabase mutation:** Local forward repair only if demonstrated; later O-NP-MIG
- **External provider configuration:** No
- **Exact Owner authorization gate:** O-SOURCE report precedence decision; O-EXEC; later O-NP-MIG if repair
- **Rollback/reversibility:** Retain accepted merge contract; compatible safe client or forward repair; never blanket whole-row overwrite
- **Evidence required for acceptance:** EV signed-off actor matrix plus actual DB/browser interleavings
- **What not to expand into:** Report rebuild, CRDT/global state, silently choosing merge-all or reject-all
- **Completion boundary unlocked:** FUNCTIONAL UAT PREVIEW
- **Parallel safety:** Apply §14 ownership/isolation rules; dependencies are acceptance edges, not permission for concurrent writes to shared files/databases.

### REC-13 — First trustworthy functional UAT deployment and cohort

- **Planning ID:** REC-13
- **Priority:** P1
- **Plan group:** A
- **Backlog classification:** MUST_BEFORE_UAT
- **Objective:** First trustworthy functional UAT deployment and cohort
- **Concrete user/product outcome:** First real bounded multi-persona synthetic recruitment journey
- **Problem/finding IDs:** F01–F08,F13,F18,F20 composed acceptance; not full closure of all features
- **Likely source areas:** Approved Vercel Preview target, isolated Supabase, current Candidate/Inbox/Interview/Report consumers and test providers
- **Dependencies:** REC-05, REC-07, REC-08, REC-09, REC-11, REC-12
- **What is preserved:** All repaired invariants and existing UI/domain architecture
- **What is changed:** Deploy exact reviewed candidate after explicit gate; exercise named cohort and declare all omissions
- **What is explicitly NOT changed:** INV below; no unrelated domain/schema/framework replacement. Only the explicitly named required repair or capability may change behavior.
- **Acceptance criteria:** FIRST_TRUSTWORTHY_FUNCTIONAL_UAT_PREVIEW checklist in §6 passes including real scan/mail, unauthorized denial, stale/concurrent mutation and refresh; no real PII; monitored bounded leftovers only
- **Required local tests:** L1 exact production build/config smoke
- **Required PostgreSQL/RLS/concurrency tests:** PG1 target parity plus direct-role and representative race smoke against synthetic data
- **Required browser/E2E tests:** B1 full §6 cohort and negative/failure cases on actual deployed build
- **Required provider/runtime tests:** Real OTP/Google, engine verdict and promised email receipt; cleanup not falsely called unattended yet
- **Independent review requirement:** Independent high-risk evidence review plus multi-persona composition reviewer
- **CI requirement:** CI1 exact deployed SHA with applicable full domain acceptance; deployment is not a CI substitute
- **Vercel mutation:** Yes explicit Preview deployment
- **Supabase mutation:** Only approved synthetic fixtures/parity and previously vetted nonprod migrations; no shared reset
- **External provider configuration:** Only already gated test integrations; changes need fresh matching gate
- **Exact Owner authorization gate:** O-DEPLOY plus O-NP-DATA; O-NP-MIG if not applied; no production approval
- **Rollback/reversibility:** Unpublish/suspend Preview or restore known-safe compatible build; preserve jobs/history; revoke test sessions if needed
- **Evidence required for acceptance:** EV deployed SHA/project IDs, actual traces/receipts, role/race evidence, declared omissions and Owner deployment receipt
- **What not to expand into:** Calling bounded UAT Phase-1 complete, exposing production PII, starting new architecture
- **Completion boundary unlocked:** FUNCTIONAL UAT PREVIEW
- **Parallel safety:** Apply §14 ownership/isolation rules; dependencies are acceptance edges, not permission for concurrent writes to shared files/databases.

## 6. FIRST_TRUSTWORTHY_FUNCTIONAL_UAT_PREVIEW

REC-13 is the single named milestone. Its acceptance is conjunctive, not a happy-path screenshot:

1. Authorized isolated Vercel Preview (or explicitly approved equivalent) talks only to non-production Supabase and approved test providers. No real recruitment PII or production seed/keys. Inventory, grant/RLS/Auth-trigger parity, cookie/cache/header behavior and deployed SHA are attributable.
2. Synthetic Candidate obtains real test OTP, verifies identity, opens an approved synthetic notice/session, uploads required CV, and observes actual same-byte trusted CLEAN after real engine execution. PENDING/infected/unavailable never becomes fake success. Submit persists the complete acknowledged snapshot and private references.
3. Eligible HR uses actual Workspace OAuth/session, deliberately opens Submission (NEW→READ); view-only reads remain pure. Candidate edit after READ fails without partial field/file changes. Assignment and interview scheduling use actual trusted commands and conflict checks.
4. Assigned Interviewer uses a genuine bound session, submits own report and reads authorized shared HTML Preview for the Current Round. Demonstrate unassigned/removed identity denial and direct HR-only note/source-metadata denial, not merely hidden fields.
5. Observe real receipt for promised create/edit/manual notification email; record queue/attempt/provider status distinctly. Show one approved stale/concurrent mutation (including required local wider SQL proof), one scan-pending/failure case and one actual session refresh. Failed/stale actions preserve draft and legal state.
6. Test clean/pending leftovers are monitored with an explicit bounded cohort lifetime, quota and approved cleanup/disposal responsibility. REC-14 recurring cleanup is not falsely certified by manual cleanup; a prolonged/unattended cohort waits for it. No business-data purge is implied.
7. Independent composition acceptance, required exact-SHA CI, deployment approval, logs and actual browser/DB/provider receipts all identify the same candidate and target.

**Explicitly incomplete at this milestone unless separately finished:** whole HR text/education/document Save; Interview materials; Master Data and Users/Permissions UIs; real generated PDF; full VI/EN, mobile/WCAG acceptance across all completed pages; recurring cleanup operations; notice publication/rollover and retention archive/purge rehearsal; representative load/capacity acceptance; full source-to-capability composition; production backup/object restore, credential/break-glass and monitoring proof. No mandatory capability is deferred out of Phase 1 by this list. Shared HTML Preview is not generated PDF. Synthetic notice use is not production Legal approval.

## 7. Phase-1 completion plan

### B. PHASE-1 PRODUCT COMPLETION

PHASE1_COMPLETE is REC-27 acceptance, not automatic completion when the slice list is exhausted. Every A R01–R32 obligation must have observable evidence, including retained Candidate NEW edit/session/privacy, Inbox grouping/search/history and bulk intents, assignment uniqueness, next-round/copy/manual reschedule/current-resource distinction, participant restore-versus-new/order, derived outcomes, qualitative reports without scoring, owner merge/decision source, authorized Email History/deletion/audit, catalog/identity lifecycle and private documents. Any newly located mandatory omission receives a later bounded authorization; it is not silently marked KEEP or waived.

New surfaces must meet locale, keyboard/focus and mobile requirements as built; REC-21–23 certify whole-product coverage rather than postponing basics as polish. REC-15/16 separate user-visible editing concerns but jointly prove atomic text/file Save. Catalog source09 has twelve entries; eleven business categories are covered by REC-18 and the Users entry by REC-19, with permission catalog treated as security administration. Optional reasons/source and advisory demo metadata must not become invented blocking requirements.

### REC-14 — Recurring temporary cleanup

- **Planning ID:** REC-14
- **Priority:** P1
- **Plan group:** B
- **Backlog classification:** MUST_BEFORE_PHASE1_COMPLETE
- **Objective:** Recurring temporary cleanup
- **Concrete user/product outcome:** Expired temporary objects are discovered and safely reclaimed without deleting recruitment history
- **Problem/finding IDs:** F14; C X07–X10,D17
- **Likely source areas:** web/src/lib/storage/{cleanup-runner,cleanup-worker-client}.ts; lib/commands/storage-reservation.ts; existing cleanup SQL; approved scheduler/launcher
- **Dependencies:** REC-07
- **What is preserved:** Exact-object runner, discovery eligibility, provenance, leases/tombstones and retained references
- **What is changed:** Bind discovery plus claim/authorize/delete/fenced-complete loop to real authenticated recurring trigger; add backlog/recovery visibility
- **What is explicitly NOT changed:** INV below; no unrelated domain/schema/framework replacement. Only the explicitly named required repair or capability may change behavior.
- **Acceptance criteria:** Expired sessions produce jobs without manual enqueue; retained/current/historical/signed-window objects survive; stale worker cannot finalize; provider missing-object distinct from permission/bucket failure
- **Required local tests:** L1 plus behavior/error/validation regressions for the stated acceptance
- **Required PostgreSQL/RLS/concurrency tests:** PG1 expiry discovery/retained refs/provenance/lease/tombstone races and retry
- **Required browser/E2E tests:** B1 replace/cancel/delete states and authorized retained download after cleanup
- **Required provider/runtime tests:** Real scheduler invocation, missed/overlap/stale lease and provider-delete failure/recovery; alert test
- **Independent review requirement:** Independent domain reviewer; security/database specialist for crossed access/transaction boundaries
- **CI requirement:** CI1 affected web+DB and fresh actual browser acceptance; no repeated unchanged proof without impact
- **Vercel mutation:** Updated acceptance Preview only under O-DEPLOY
- **Supabase mutation:** Synthetic nonprod data O-NP-DATA; any necessary forward repair separately O-NP-MIG
- **External provider configuration:** Existing approved providers only; new configuration requires matching Owner gate
- **Exact Owner authorization gate:** O-EXEC, O-DEPLOY, O-NP-DATA; O-WORKER, O-SECRETS; O-ENV if Vercel scheduler config
- **Rollback/reversibility:** Revert safe compatible consumer; retain committed records/history/security repairs; forward repair DB if needed
- **Evidence required for acceptance:** EV plus exact named user flow, denied/stale/failure proof and reviewed source coverage
- **What not to expand into:** Unrelated refactors, generic platforms or reducing required scope
- **Completion boundary unlocked:** PHASE-1 PRODUCT COMPLETENESS
- **Parallel safety:** Apply §14 ownership/isolation rules; dependencies are acceptance edges, not permission for concurrent writes to shared files/databases.

### REC-15 — Whole HR Submission editing

- **Planning ID:** REC-15
- **Priority:** P1
- **Plan group:** B
- **Backlog classification:** MUST_BEFORE_PHASE1_COMPLETE
- **Objective:** Whole HR Submission editing
- **Concrete user/product outcome:** HR edits all permitted profile/education/recruitment-source fields with truthful Save/Cancel
- **Problem/finding IDs:** F09 text/metadata; C P08
- **Likely source areas:** web/src/components/inbox/SubmissionDetailDrawer.tsx; app/application-inbox-actions.ts; lib/commands/submission-status.ts; existing correction/Submission commands
- **Dependencies:** REC-03, REC-04, REC-05
- **What is preserved:** Immutable verified email, Candidate snapshots, HR-only data, note/assignment/read behavior
- **What is changed:** Add missing allowed controls and atomic versioned aggregate Save; bounded feature-owned extraction only if necessary
- **What is explicitly NOT changed:** INV below; no unrelated domain/schema/framework replacement. Only the explicitly named required repair or capability may change behavior.
- **Acceptance criteria:** Profile/education/optional source edit, Cancel/dirty warning and stale conflict pass; forbidden fields denied; exact-Submission navigation preserved; no partial Save
- **Required local tests:** L1 plus behavior/error/validation regressions for the stated acceptance
- **Required PostgreSQL/RLS/concurrency tests:** PG1 granular permissions, immutable email, latest/profile cache and concurrent aggregate save
- **Required browser/E2E tests:** B1 full/limited HR, dirty refresh/cancel, stale Save and exact Submission → Interview navigation
- **Required provider/runtime tests:** N/A — no new provider effect
- **Independent review requirement:** Independent domain reviewer; security/database specialist for crossed access/transaction boundaries
- **CI requirement:** CI1 affected web+DB and fresh actual browser acceptance; no repeated unchanged proof without impact
- **Vercel mutation:** Updated acceptance Preview only under O-DEPLOY
- **Supabase mutation:** Synthetic nonprod data O-NP-DATA; any necessary forward repair separately O-NP-MIG
- **External provider configuration:** Existing approved providers only; new configuration requires matching Owner gate
- **Exact Owner authorization gate:** O-EXEC, O-DEPLOY, O-NP-DATA; O-NP-MIG only if SQL changes
- **Rollback/reversibility:** Revert safe compatible consumer; retain committed records/history/security repairs; forward repair DB if needed
- **Evidence required for acceptance:** EV plus exact named user flow, denied/stale/failure proof and reviewed source coverage
- **What not to expand into:** Unrelated refactors, generic platforms or reducing required scope
- **Completion boundary unlocked:** PHASE-1 PRODUCT COMPLETENESS
- **Parallel safety:** Apply §14 ownership/isolation rules; dependencies are acceptance edges, not permission for concurrent writes to shared files/databases.

### REC-16 — HR Submission document editing

- **Planning ID:** REC-16
- **Priority:** P1
- **Plan group:** B
- **Backlog classification:** MUST_BEFORE_PHASE1_COMPLETE
- **Objective:** HR Submission document editing
- **Concrete user/product outcome:** HR safely adds/replaces/removes Submission files including file-only changes
- **Problem/finding IDs:** F09 documents; C P09
- **Likely source areas:** SubmissionDetailDrawer document consumers; authorized document actions/storage reservation and Submission finalize commands
- **Dependencies:** REC-15, REC-08
- **What is preserved:** Private versioned objects, required last CV, scan and history/cleanup contracts
- **What is changed:** Add staged document controls and compose with full HR Save
- **What is explicitly NOT changed:** INV below; no unrelated domain/schema/framework replacement. Only the explicitly named required repair or capability may change behavior.
- **Acceptance criteria:** ADD/REPLACE/DELETE, file-only Save, concurrent text+files, last CV, five files/5MB and allowed formats; failure never partially commits; dirty draft retained
- **Required local tests:** L1 plus behavior/error/validation regressions for the stated acceptance
- **Required PostgreSQL/RLS/concurrency tests:** PG1 file/text aggregate version/scan/last-CV/reference/audit atomicity and races
- **Required browser/E2E tests:** B1 HR document lifecycle plus valid Candidate/HR reads and forbidden Interviewer access
- **Required provider/runtime tests:** Actual approved scanner and private object provider; cleanup retention regression shared REC-14
- **Independent review requirement:** Independent domain reviewer; security/database specialist for crossed access/transaction boundaries
- **CI requirement:** CI1 affected web+DB and fresh actual browser acceptance; no repeated unchanged proof without impact
- **Vercel mutation:** Updated acceptance Preview only under O-DEPLOY
- **Supabase mutation:** Synthetic nonprod data O-NP-DATA; any necessary forward repair separately O-NP-MIG
- **External provider configuration:** Existing approved providers only; new configuration requires matching Owner gate
- **Exact Owner authorization gate:** O-EXEC, O-DEPLOY, O-NP-DATA; O-NP-MIG only if SQL changes
- **Rollback/reversibility:** Revert safe compatible consumer; retain committed records/history/security repairs; forward repair DB if needed
- **Evidence required for acceptance:** EV plus exact named user flow, denied/stale/failure proof and reviewed source coverage
- **What not to expand into:** Unrelated refactors, generic platforms or reducing required scope
- **Completion boundary unlocked:** PHASE-1 PRODUCT COMPLETENESS
- **Parallel safety:** Apply §14 ownership/isolation rules; dependencies are acceptance edges, not permission for concurrent writes to shared files/databases.

### REC-17 — Interview materials

- **Planning ID:** REC-17
- **Priority:** P1
- **Plan group:** B
- **Backlog classification:** MUST_BEFORE_PHASE1_COMPLETE
- **Objective:** Interview materials
- **Concrete user/product outcome:** HR manages exact-round materials and eligible Interviewer reads them contextually
- **Problem/finding IDs:** F10; C P14
- **Likely source areas:** web/src/components/interview/InterviewDrawer.tsx; reports/InterviewerReportDrawerContent.tsx; authorized document command/preview paths
- **Dependencies:** REC-03, REC-04, REC-08
- **What is preserved:** Round/history identity, resource eligibility, private Storage/fences
- **What is changed:** Add HR add/replace/remove and Interviewer contextual preview/download
- **What is explicitly NOT changed:** INV below; no unrelated domain/schema/framework replacement. Only the explicitly named required repair or capability may change behavior.
- **Acceptance criteria:** Exact-round scope; no Candidate access; denied new authorization after hide/removal/inactivation; bounded previously issued signed-link lifetime disclosed, not instant revocation claim
- **Required local tests:** L1 plus behavior/error/validation regressions for the stated acceptance
- **Required PostgreSQL/RLS/concurrency tests:** PG1 parent/current/history/context/scan/file-version permissions and lifecycle race
- **Required browser/E2E tests:** B1 both personas, removed/unassigned negative cases, stale file action
- **Required provider/runtime tests:** Actual clean/pending/infected scanner and private provider lifecycle
- **Independent review requirement:** Independent domain reviewer; security/database specialist for crossed access/transaction boundaries
- **CI requirement:** CI1 affected web+DB and fresh actual browser acceptance; no repeated unchanged proof without impact
- **Vercel mutation:** Updated acceptance Preview only under O-DEPLOY
- **Supabase mutation:** Synthetic nonprod data O-NP-DATA; any necessary forward repair separately O-NP-MIG
- **External provider configuration:** Existing approved providers only; new configuration requires matching Owner gate
- **Exact Owner authorization gate:** O-EXEC, O-DEPLOY, O-NP-DATA; O-NP-MIG only if SQL changes
- **Rollback/reversibility:** Revert safe compatible consumer; retain committed records/history/security repairs; forward repair DB if needed
- **Evidence required for acceptance:** EV plus exact named user flow, denied/stale/failure proof and reviewed source coverage
- **What not to expand into:** Unrelated refactors, generic platforms or reducing required scope
- **Completion boundary unlocked:** PHASE-1 PRODUCT COMPLETENESS
- **Parallel safety:** Apply §14 ownership/isolation rules; dependencies are acceptance edges, not permission for concurrent writes to shared files/databases.

### REC-18 — Master Data management

- **Planning ID:** REC-18
- **Priority:** P1
- **Plan group:** B
- **Backlog classification:** MUST_BEFORE_PHASE1_COMPLETE
- **Objective:** Master Data management
- **Concrete user/product outcome:** Authorized staff operate every required business catalog without direct SQL
- **Problem/finding IDs:** F11; C P20
- **Likely source areas:** New finite management routes using shell/navigation and accepted master_data_lifecycle_history contracts; source 09 catalog
- **Dependencies:** REC-02, REC-04
- **What is preserved:** Accepted backend semantics, structural history, versioning/audit and inactive historical references
- **What is changed:** Add finite catalog forms/dependent selectors/search/lifecycle; Users catalog entry links REC-19
- **What is explicitly NOT changed:** INV below; no unrelated domain/schema/framework replacement. Only the explicitly named required repair or capability may change behavior.
- **Acceptance criteria:** All source09 entries covered with Users separately REC-19; no hard delete of referenced master; structural change rejected; label correction permitted per contract; optional source/reasons remain optional
- **Required local tests:** L1 plus behavior/error/validation regressions for the stated acceptance
- **Required PostgreSQL/RLS/concurrency tests:** PG1 authorized lifecycle, dependency/FK/version races, inactive existing format remains operable
- **Required browser/E2E tests:** B1 manage catalog/dependent selection, inactive history and limited-HR denials
- **Required provider/runtime tests:** N/A — no new provider effect
- **Independent review requirement:** Independent domain reviewer; security/database specialist for crossed access/transaction boundaries
- **CI requirement:** CI1 affected web+DB and fresh actual browser acceptance; no repeated unchanged proof without impact
- **Vercel mutation:** Updated acceptance Preview only under O-DEPLOY
- **Supabase mutation:** Synthetic nonprod data O-NP-DATA; any necessary forward repair separately O-NP-MIG
- **External provider configuration:** Existing approved providers only; new configuration requires matching Owner gate
- **Exact Owner authorization gate:** O-EXEC, O-DEPLOY, O-NP-DATA; O-NP-MIG only if SQL changes
- **Rollback/reversibility:** Revert safe compatible consumer; retain committed records/history/security repairs; forward repair DB if needed
- **Evidence required for acceptance:** EV plus exact named user flow, denied/stale/failure proof and reviewed source coverage
- **What not to expand into:** Unrelated refactors, generic platforms or reducing required scope
- **Completion boundary unlocked:** PHASE-1 PRODUCT COMPLETENESS
- **Parallel safety:** Apply §14 ownership/isolation rules; dependencies are acceptance edges, not permission for concurrent writes to shared files/databases.

### REC-19 — Users and Permissions management

- **Planning ID:** REC-19
- **Priority:** P1
- **Plan group:** B
- **Backlog classification:** MUST_BEFORE_PHASE1_COMPLETE
- **Objective:** Users and Permissions management
- **Concrete user/product outcome:** Root/delegated staff manage directory and permissions through trusted contracts
- **Problem/finding IDs:** F12; C P21
- **Likely source areas:** New Users/Permissions routes and navigation using accepted internal-user RBAC/lifecycle commands
- **Dependencies:** REC-02, REC-03, REC-04
- **What is preserved:** Protected Root, Auth/business binding, exact permission dependencies and participant/owner lifecycle
- **What is changed:** Add permitted management UI, no privileged generic DML
- **What is explicitly NOT changed:** INV below; no unrelated domain/schema/framework replacement. Only the explicitly named required repair or capability may change behavior.
- **Acceptance criteria:** Bound-email change Root-only; inactive login/new selection denied; protected Root and grant dependency/escalation tests; historical identities preserved
- **Required local tests:** L1 plus behavior/error/validation regressions for the stated acceptance
- **Required PostgreSQL/RLS/concurrency tests:** PG1 direct non-root crafted calls, root protection, binding/rebind/owner/participant races and audit
- **Required browser/E2E tests:** B1 Root/full/limited HR create/edit/inactivate/grant workflows with actual session revocation semantics
- **Required provider/runtime tests:** N/A — no new provider effect
- **Independent review requirement:** Independent domain reviewer; security/database specialist for crossed access/transaction boundaries
- **CI requirement:** CI1 affected web+DB and fresh actual browser acceptance; no repeated unchanged proof without impact
- **Vercel mutation:** Updated acceptance Preview only under O-DEPLOY
- **Supabase mutation:** Synthetic nonprod data O-NP-DATA; any necessary forward repair separately O-NP-MIG
- **External provider configuration:** Existing approved providers only; new configuration requires matching Owner gate
- **Exact Owner authorization gate:** O-EXEC, O-DEPLOY, O-NP-DATA; O-NP-MIG only if SQL changes
- **Rollback/reversibility:** Revert safe compatible consumer; retain committed records/history/security repairs; forward repair DB if needed
- **Evidence required for acceptance:** EV plus exact named user flow, denied/stale/failure proof and reviewed source coverage
- **What not to expand into:** Unrelated refactors, generic platforms or reducing required scope
- **Completion boundary unlocked:** PHASE-1 PRODUCT COMPLETENESS
- **Parallel safety:** Apply §14 ownership/isolation rules; dependencies are acceptance edges, not permission for concurrent writes to shared files/databases.

### REC-20 — Content-correct generated PDF

- **Planning ID:** REC-20
- **Priority:** P1
- **Plan group:** B
- **Backlog classification:** MUST_BEFORE_PHASE1_COMPLETE
- **Objective:** Content-correct generated PDF
- **Concrete user/product outcome:** Authorized HR and Interviewer download a real current report PDF
- **Problem/finding IDs:** F15; C P18/X11; future F02 regression
- **Likely source areas:** web/src/components/reports/HrReportView.tsx and Interviewer report consumers; bounded generated-report handler/renderer over existing authorized snapshot
- **Dependencies:** REC-03, REC-12
- **What is preserved:** Current Round, participant snapshots/order, field merge, decision-source and confidentiality
- **What is changed:** Add real export, localized fonts, safe output/audit; rendering host chosen by measured limits
- **What is explicitly NOT changed:** INV below; no unrelated domain/schema/framework replacement. Only the explicitly named required repair or capability may change behavior.
- **Acceptance criteria:** Actual PDF bytes parse/render; VI glyphs, blank/clear/decision block/order and removed participants correct; no HR-only note/owner/final-source metadata leakage through any report artifact; export denial after context loss
- **Required local tests:** L1 plus behavior/error/validation regressions for the stated acceptance
- **Required PostgreSQL/RLS/concurrency tests:** PG1 snapshot/context/revocation and audit; same effective disclosure matrix as REC-03
- **Required browser/E2E tests:** B1 export both personas and inaccessible contexts; actual PDF visual/content checks
- **Required provider/runtime tests:** Real renderer in supported target runtime; duration/memory/font/privacy proof, no queue by default
- **Independent review requirement:** Independent domain reviewer; security/database specialist for crossed access/transaction boundaries
- **CI requirement:** CI1 affected web+DB and fresh actual browser acceptance; no repeated unchanged proof without impact
- **Vercel mutation:** Updated acceptance Preview only under O-DEPLOY
- **Supabase mutation:** Synthetic nonprod data O-NP-DATA; any necessary forward repair separately O-NP-MIG
- **External provider configuration:** Existing approved providers only; new configuration requires matching Owner gate
- **Exact Owner authorization gate:** O-EXEC, O-DEPLOY, O-NP-DATA; O-PDF-USE before operational use; O-WORKER/O-SECRETS only if approved external renderer needed
- **Rollback/reversibility:** Revert safe compatible consumer; retain committed records/history/security repairs; forward repair DB if needed
- **Evidence required for acceptance:** EV plus exact named user flow, denied/stale/failure proof and reviewed source coverage
- **What not to expand into:** Unrelated refactors, generic platforms or reducing required scope
- **Completion boundary unlocked:** PHASE-1 PRODUCT COMPLETENESS
- **Parallel safety:** Apply §14 ownership/isolation rules; dependencies are acceptance edges, not permission for concurrent writes to shared files/databases.

### REC-21 — Complete VI/EN workflows

- **Planning ID:** REC-21
- **Priority:** P1
- **Plan group:** B
- **Backlog classification:** MUST_BEFORE_PHASE1_COMPLETE
- **Objective:** Complete VI/EN workflows
- **Concrete user/product outcome:** All required surfaces, warnings and recovery paths work in either language
- **Problem/finding IDs:** F16; C P22
- **Likely source areas:** Existing LocaleProvider and page-specific consumers/messages, Candidate form and shell
- **Dependencies:** REC-15, REC-16, REC-17, REC-18, REC-19, REC-20
- **What is preserved:** Current locale model, drafts, focus and business timezone/date semantics
- **What is changed:** Replace missing hardcoded consumers without new i18n/state platform
- **What is explicitly NOT changed:** INV below; no unrelated domain/schema/framework replacement. Only the explicitly named required repair or capability may change behavior.
- **Acceptance criteria:** Both languages across all Phase-1 surfaces, stale/forbidden/scan/mail errors; switching language preserves dirty state and expected bases
- **Required local tests:** L1 plus behavior/error/validation regressions for the stated acceptance
- **Required PostgreSQL/RLS/concurrency tests:** N/A — presentation only unless a changed command contract is identified; existing PG proof remains required
- **Required browser/E2E tests:** B1 language switch mid-draft, lengthy labels/reflow, Asia/Ho_Chi_Minh/date-only display and localized validation
- **Required provider/runtime tests:** N/A — no new provider effect
- **Independent review requirement:** Independent domain reviewer; security/database specialist for crossed access/transaction boundaries
- **CI requirement:** CI1 affected web+DB and fresh actual browser acceptance; no repeated unchanged proof without impact
- **Vercel mutation:** Updated acceptance Preview only under O-DEPLOY
- **Supabase mutation:** Synthetic nonprod data O-NP-DATA; any necessary forward repair separately O-NP-MIG
- **External provider configuration:** Existing approved providers only; new configuration requires matching Owner gate
- **Exact Owner authorization gate:** O-EXEC, O-DEPLOY, O-NP-DATA; O-NP-MIG only if SQL changes
- **Rollback/reversibility:** Revert safe compatible consumer; retain committed records/history/security repairs; forward repair DB if needed
- **Evidence required for acceptance:** EV plus exact named user flow, denied/stale/failure proof and reviewed source coverage
- **What not to expand into:** Unrelated refactors, generic platforms or reducing required scope
- **Completion boundary unlocked:** PHASE-1 PRODUCT COMPLETENESS
- **Parallel safety:** Apply §14 ownership/isolation rules; dependencies are acceptance edges, not permission for concurrent writes to shared files/databases.

### REC-22 — Candidate mobile completion acceptance

- **Planning ID:** REC-22
- **Priority:** P1
- **Plan group:** B
- **Backlog classification:** MUST_BEFORE_PHASE1_COMPLETE
- **Objective:** Candidate mobile completion acceptance
- **Concrete user/product outcome:** Candidate can complete and safely edit the real form on supported mobile devices
- **Problem/finding IDs:** C P23/P24; A R26
- **Likely source areas:** Candidate portal/form/upload interactions; design responsive sources
- **Dependencies:** REC-02, REC-08, REC-11, REC-21, REC-24
- **What is preserved:** Single form/session/notice model, existing UI primitives
- **What is changed:** Test actual mobile journey and fix only observed responsive/interaction defects
- **What is explicitly NOT changed:** INV below; no unrelated domain/schema/framework replacement. Only the explicitly named required repair or capability may change behavior.
- **Acceptance criteria:** OTP→notice→draft/education→scan/upload→submit→own history/NEW edit; keyboard/upload/error states at 360/390/430 plus canonical 375/768/1280/1440 widths; no lost input
- **Required local tests:** L1 plus behavior/error/validation regressions for the stated acceptance
- **Required PostgreSQL/RLS/concurrency tests:** PG1 existing Candidate/notice/file contracts rerun only if changed/shared risk
- **Required browser/E2E tests:** B1 real mobile viewport/device interactions, scrolling/focus/keyboard/reflow; not login screenshot only
- **Required provider/runtime tests:** Real approved Auth/scan pipeline on synthetic accounts
- **Independent review requirement:** Independent domain reviewer; security/database specialist for crossed access/transaction boundaries
- **CI requirement:** CI1 affected web+DB and fresh actual browser acceptance; no repeated unchanged proof without impact
- **Vercel mutation:** Updated acceptance Preview only under O-DEPLOY
- **Supabase mutation:** Synthetic nonprod data O-NP-DATA; any necessary forward repair separately O-NP-MIG
- **External provider configuration:** Existing approved providers only; new configuration requires matching Owner gate
- **Exact Owner authorization gate:** O-EXEC, O-DEPLOY, O-NP-DATA; O-NP-MIG only if SQL changes
- **Rollback/reversibility:** Revert safe compatible consumer; retain committed records/history/security repairs; forward repair DB if needed
- **Evidence required for acceptance:** EV plus exact named user flow, denied/stale/failure proof and reviewed source coverage
- **What not to expand into:** Unrelated refactors, generic platforms or reducing required scope
- **Completion boundary unlocked:** PHASE-1 PRODUCT COMPLETENESS
- **Parallel safety:** Apply §14 ownership/isolation rules; dependencies are acceptance edges, not permission for concurrent writes to shared files/databases.

### REC-23 — WCAG and keyboard acceptance

- **Planning ID:** REC-23
- **Priority:** P1
- **Plan group:** B
- **Backlog classification:** MUST_BEFORE_PHASE1_COMPLETE
- **Objective:** WCAG and keyboard acceptance
- **Concrete user/product outcome:** All supported Phase-1 users can operate UI accessibly
- **Problem/finding IDs:** C P25; A R26/R28
- **Likely source areas:** Actual production components/dialogs/drawers/status controls/forms; design tokens only where defect shown
- **Dependencies:** REC-15, REC-16, REC-17, REC-18, REC-19, REC-20, REC-21, REC-22
- **What is preserved:** Shared focus/overlay primitives, semantic controls and domain behavior
- **What is changed:** Audit then narrowly repair keyboard/focus/labels/errors/contrast/reflow issues
- **What is explicitly NOT changed:** INV below; no unrelated domain/schema/framework replacement. Only the explicitly named required repair or capability may change behavior.
- **Acceptance criteria:** WCAG2.2AA target; keyboard/overlay trap/restore, screen-reader sanity, zoom/reflow, contrast and language semantics across personas/new pages; automation alone not certification
- **Required local tests:** L1 plus behavior/error/validation regressions for the stated acceptance
- **Required PostgreSQL/RLS/concurrency tests:** N/A — UI acceptance unless fixes cross command contracts
- **Required browser/E2E tests:** B1 actual keyboard + assistive tech/manual checks and automated accessibility regression across supported widths
- **Required provider/runtime tests:** N/A — no new provider effect
- **Independent review requirement:** Independent domain reviewer; security/database specialist for crossed access/transaction boundaries
- **CI requirement:** CI1 affected web+DB and fresh actual browser acceptance; no repeated unchanged proof without impact
- **Vercel mutation:** Updated acceptance Preview only under O-DEPLOY
- **Supabase mutation:** Synthetic nonprod data O-NP-DATA; any necessary forward repair separately O-NP-MIG
- **External provider configuration:** Existing approved providers only; new configuration requires matching Owner gate
- **Exact Owner authorization gate:** O-EXEC, O-DEPLOY, O-NP-DATA; O-NP-MIG only if SQL changes
- **Rollback/reversibility:** Revert safe compatible consumer; retain committed records/history/security repairs; forward repair DB if needed
- **Evidence required for acceptance:** EV plus exact named user flow, denied/stale/failure proof and reviewed source coverage
- **What not to expand into:** Unrelated refactors, generic platforms or reducing required scope
- **Completion boundary unlocked:** PHASE-1 PRODUCT COMPLETENESS
- **Parallel safety:** Apply §14 ownership/isolation rules; dependencies are acceptance edges, not permission for concurrent writes to shared files/databases.

### REC-24 — Privacy notice publication and acknowledgement rollover

- **Planning ID:** REC-24
- **Priority:** P1
- **Plan group:** B
- **Backlog classification:** MUST_BEFORE_PHASE1_COMPLETE
- **Objective:** Privacy notice publication and acknowledgement rollover
- **Concrete user/product outcome:** Approved notice can change without losing drafts or rewriting historical acknowledgements
- **Problem/finding IDs:** C Z01/Z02; A R06
- **Likely source areas:** Existing notice/session/Candidate commands; canonical publication runbook78; maintenance-only operation
- **Dependencies:** REC-01, REC-02, REC-07
- **What is preserved:** Immutable notice versions and historical consent linkage
- **What is changed:** Verify/provide restricted publish/current-switch operation and Candidate renewed-acknowledgement flow
- **What is explicitly NOT changed:** INV below; no unrelated domain/schema/framework replacement. Only the explicitly named required repair or capability may change behavior.
- **Acceptance criteria:** Approved immutable VI/EN content; no unintended no-current gap; stale acknowledgement rejected/refreshed with draft preserved; concurrent publish/Save atomic; old legal history unchanged
- **Required local tests:** L1 plus behavior/error/validation regressions for the stated acceptance
- **Required PostgreSQL/RLS/concurrency tests:** PG1 notice/session/current-save publication interleavings and actor/audit permissions
- **Required browser/E2E tests:** B1 open form→notice rollover→renewed acknowledgement→safe Save without lost draft
- **Required provider/runtime tests:** N/A — maintenance DB operation only
- **Independent review requirement:** Independent domain reviewer; security/database specialist for crossed access/transaction boundaries
- **CI requirement:** CI1 affected web+DB and fresh actual browser acceptance; no repeated unchanged proof without impact
- **Vercel mutation:** Updated acceptance Preview only under O-DEPLOY
- **Supabase mutation:** Synthetic nonprod data O-NP-DATA; any necessary forward repair separately O-NP-MIG
- **External provider configuration:** Existing approved providers only; new configuration requires matching Owner gate
- **Exact Owner authorization gate:** O-EXEC, O-DEPLOY, O-NP-DATA; O-LEGAL and O-NP-MAINT for nonprod rehearsal; O-PROD-MAINT separately before any live publication
- **Rollback/reversibility:** Revert safe compatible consumer; retain committed records/history/security repairs; forward repair DB if needed
- **Evidence required for acceptance:** EV plus exact named user flow, denied/stale/failure proof and reviewed source coverage
- **What not to expand into:** Unrelated refactors, generic platforms or reducing required scope
- **Completion boundary unlocked:** PHASE-1 PRODUCT COMPLETENESS
- **Parallel safety:** Apply §14 ownership/isolation rules; dependencies are acceptance edges, not permission for concurrent writes to shared files/databases.

### REC-25 — Controlled export/archive/purge capability

- **Planning ID:** REC-25
- **Priority:** P1
- **Plan group:** B
- **Backlog classification:** MUST_BEFORE_PHASE1_COMPLETE
- **Objective:** Controlled export/archive/purge capability
- **Concrete user/product outcome:** Authorized operators can retain and recover selected data before an expressly approved purge
- **Problem/finding IDs:** C Z08; A R25
- **Likely source areas:** Canonical retention42 and runbook66; restricted maintenance tooling; existing records/object/audit model
- **Dependencies:** REC-01, REC-07
- **What is preserved:** No timed business purge; historical links and immutable audit
- **What is changed:** Verify/provide scoped encrypted export/manifest/checksum/sample restore and exact authorized purge with restart-safe evidence
- **What is explicitly NOT changed:** INV below; no unrelated domain/schema/framework replacement. Only the explicitly named required repair or capability may change behavior.
- **Acceptance criteria:** Synthetic selected dataset+objects archive validates/restores; approval and retained audit survive; no unrelated data deleted; resumable exact scope; failed verification blocks purge
- **Required local tests:** L1 plus behavior/error/validation regressions for the stated acceptance
- **Required PostgreSQL/RLS/concurrency tests:** PG1 referential consistency, exact selection/authorization, audit and partial-failure recovery
- **Required browser/E2E tests:** N/A — no general HR purge/admin console; operator runbook observed instead
- **Required provider/runtime tests:** Actual private object export/restore on disposable nonprod target with checksum match
- **Independent review requirement:** Independent domain reviewer; security/database specialist for crossed access/transaction boundaries
- **CI requirement:** CI1 affected web+DB and fresh actual browser acceptance; no repeated unchanged proof without impact
- **Vercel mutation:** Updated acceptance Preview only under O-DEPLOY
- **Supabase mutation:** Synthetic nonprod data O-NP-DATA; any necessary forward repair separately O-NP-MIG
- **External provider configuration:** Existing approved providers only; new configuration requires matching Owner gate
- **Exact Owner authorization gate:** O-EXEC, O-DEPLOY, O-NP-DATA; O-LEGAL, O-ARCHIVE, O-NP-MAINT; any real purge needs distinct O-PROD-MAINT with exact dataset
- **Rollback/reversibility:** Revert safe compatible consumer; retain committed records/history/security repairs; forward repair DB if needed
- **Evidence required for acceptance:** EV plus exact named user flow, denied/stale/failure proof and reviewed source coverage
- **What not to expand into:** Unrelated refactors, generic platforms or reducing required scope
- **Completion boundary unlocked:** PHASE-1 PRODUCT COMPLETENESS
- **Parallel safety:** Apply §14 ownership/isolation rules; dependencies are acceptance edges, not permission for concurrent writes to shared files/databases.

### REC-26 — Measured performance and capacity acceptance

- **Planning ID:** REC-26
- **Priority:** P1
- **Plan group:** B
- **Backlog classification:** MUST_BEFORE_PHASE1_COMPLETE
- **Objective:** Measured performance and capacity acceptance
- **Concrete user/product outcome:** Required list/mutation experience works at canonical synthetic scale
- **Problem/finding IDs:** C Z04; NFR38
- **Likely source areas:** Existing paginated/search/read/mutation paths and measured hot spots only
- **Dependencies:** REC-13, REC-15, REC-17, REC-20
- **What is preserved:** Stable grouped pagination, immutable tie-breakers, server-side filtering and PII-safe search
- **What is changed:** Measure representative workload then repair demonstrated bottlenecks without speculative infrastructure
- **What is explicitly NOT changed:** INV below; no unrelated domain/schema/framework replacement. Only the explicitly named required repair or capability may change behavior.
- **Acceptance criteria:** 10k Submissions/30k Interviews; list/search p95≤1.5s, mutation p95≤2s excluding provider transfer; shell p75 target≤2.5s; 50 internal/200 Candidate sessions; no full dataset browser filtering; record environment/exclusions Nonprod basic capacity/staged-backlog warning capability is demonstrated; production routing/retention is REC-30.
- **Required local tests:** L1 plus behavior/error/validation regressions for the stated acceptance
- **Required PostgreSQL/RLS/concurrency tests:** PG1 query/lock contention and synthetic load; include report/resource correctness under load
- **Required browser/E2E tests:** B1 bounded actual table/form latency and mobile evidence, PII not in URL/history
- **Required provider/runtime tests:** Measure provider contribution separately; no vendor latency concealed as DB result
- **Independent review requirement:** Independent domain reviewer; security/database specialist for crossed access/transaction boundaries
- **CI requirement:** CI1 affected web+DB and fresh actual browser acceptance; no repeated unchanged proof without impact
- **Vercel mutation:** Updated acceptance Preview only under O-DEPLOY
- **Supabase mutation:** Synthetic nonprod data O-NP-DATA; any necessary forward repair separately O-NP-MIG
- **External provider configuration:** Existing approved providers only; new configuration requires matching Owner gate
- **Exact Owner authorization gate:** O-EXEC, O-DEPLOY, O-NP-DATA; O-NP-LOAD for quotas/load test; no production stress test
- **Rollback/reversibility:** Revert safe compatible consumer; retain committed records/history/security repairs; forward repair DB if needed
- **Evidence required for acceptance:** EV plus exact named user flow, denied/stale/failure proof and reviewed source coverage
- **What not to expand into:** Unrelated refactors, generic platforms or reducing required scope
- **Completion boundary unlocked:** PHASE-1 PRODUCT COMPLETENESS
- **Parallel safety:** Apply §14 ownership/isolation rules; dependencies are acceptance edges, not permission for concurrent writes to shared files/databases.

### REC-27 — Complete Phase-1 product composition

- **Planning ID:** REC-27
- **Priority:** P1
- **Plan group:** B
- **Backlog classification:** MUST_BEFORE_PHASE1_COMPLETE
- **Objective:** Complete Phase-1 product composition
- **Concrete user/product outcome:** Every mandatory Phase-1 capability is observably complete, not merely backend accepted
- **Problem/finding IDs:** F09–F16,F19 and all A requirement ledger R01–R32; no KEEP exemption
- **Likely source areas:** All existing and completed personas/journeys; source-to-capability evidence, not new framework
- **Dependencies:** REC-13, REC-14, REC-15, REC-16, REC-17, REC-18, REC-19, REC-20, REC-21, REC-22, REC-23, REC-24, REC-25, REC-26, REC-33
- **What is preserved:** All retained required behavior including multi-round/copy/participants/outcomes/history/email audit
- **What is changed:** Perform independent full composition acceptance; repair only actual missing behavior under new bounded approval
- **What is explicitly NOT changed:** INV below; no unrelated domain/schema/framework replacement. Only the explicitly named required repair or capability may change behavior.
- **Acceptance criteria:** PHASE1_COMPLETE gate in §7: all required behaviors including retained KEEP rows demonstrated; closed source ambiguities; no placeholder/disabled required controls; actual language/mobile/accessibility/runtime proof
- **Required local tests:** L1 plus behavior/error/validation regressions for the stated acceptance
- **Required PostgreSQL/RLS/concurrency tests:** PG1 full affected invariant/persona/direct-call suite at accepted candidate; preserve report/race proof
- **Required browser/E2E tests:** B1 Candidate/HR/limited-HR/Interviewer/Root complete end-to-end matrix including copy/restore/new/history/bulk
- **Required provider/runtime tests:** Actual scan/mail/cleanup/PDF integrations, failure/retry and privacy/retention evidence
- **Independent review requirement:** Independent domain reviewer; security/database specialist for crossed access/transaction boundaries
- **CI requirement:** CI1 affected web+DB and fresh actual browser acceptance; no repeated unchanged proof without impact
- **Vercel mutation:** Updated acceptance Preview only under O-DEPLOY
- **Supabase mutation:** Synthetic nonprod data O-NP-DATA; any necessary forward repair separately O-NP-MIG
- **External provider configuration:** Existing approved providers only; new configuration requires matching Owner gate
- **Exact Owner authorization gate:** O-EXEC, O-DEPLOY, O-NP-DATA; O-EXEC acceptance scope; O-DEPLOY/O-NP-DATA for candidate; operational PDF use still O-PDF-USE
- **Rollback/reversibility:** Revert safe compatible consumer; retain committed records/history/security repairs; forward repair DB if needed
- **Evidence required for acceptance:** EV plus exact named user flow, denied/stale/failure proof and reviewed source coverage
- **What not to expand into:** Unrelated refactors, generic platforms or reducing required scope
- **Completion boundary unlocked:** PHASE-1 PRODUCT COMPLETENESS
- **Parallel safety:** Apply §14 ownership/isolation rules; dependencies are acceptance edges, not permission for concurrent writes to shared files/databases.


## 8. Production-hardening plan

### C. PRODUCTION HARDENING

PRODUCTION_READY requires REC-32 and all prerequisites. Data recovery and operator rehearsal can begin on synthetic nonprod while product work continues; they must not be postponed until a production incident. Basic worker failure/backlog and capacity visibility already belongs to runtime/product slices. REC-30 adds target-specific alert routing, searchable retention and rehearsed operations, not a product Dashboard.

The source NFR targets are list/search p95 ≤1.5s at 10,000 Submissions/30,000 Interviews; core mutation p95 ≤2s excluding provider transfer; shell p75 target ≤2.5s; 50 internal/200 Candidate concurrent sessions. Backup minimum RPO ≤24h/RTO ≤8h; private objects require separate recovery. Availability target 99.5% monthly is an operational target, not a future uptime claim at release. Operational logs ≥30 searchable days; business audit has no automatic purge. Measure and document exclusions, purchased-plan constraints and any formally approved source change rather than moving targets silently.

### REC-28 — Database backup and restore proof

- **Planning ID:** REC-28
- **Priority:** P1
- **Plan group:** C
- **Backlog classification:** MUST_BEFORE_PRODUCTION
- **Objective:** Database backup and restore proof
- **Concrete user/product outcome:** Operators can restore a representative database within approved recovery targets
- **Problem/finding IDs:** F20; C R10
- **Likely source areas:** Managed backup/PITR configuration and runbook44; isolated restore target
- **Dependencies:** REC-07
- **What is preserved:** Migration/audit/history authority and identity/relationship integrity
- **What is changed:** Verify purchased backup capability and perform authorized isolated restore, not merely enable a checkbox
- **What is explicitly NOT changed:** INV below; no unrelated domain/schema/framework replacement. Only the explicitly named required repair or capability may change behavior.
- **Acceptance criteria:** Measured RPO≤24h and RTO≤8h minimum targets or approved stronger commitment; restored grants/Auth triggers/RLS and critical data relationships validated; failure drill documented
- **Required local tests:** Restore tooling/runbook commands smoke on disposable target
- **Required PostgreSQL/RLS/concurrency tests:** PG1 restored effective catalog, representative records/versions/audit/idempotency and authorized calls
- **Required browser/E2E tests:** B1 smoke of safe recovered app against restored synthetic DB
- **Required provider/runtime tests:** Actual backup acquisition/restore; provider plan limits and retention observed
- **Independent review requirement:** Independent operations/security review; DB/storage specialist for recovery evidence
- **CI requirement:** CI1 exact release candidate and relevant operational evidence; no remote mutation automatically authorized
- **Vercel mutation:** Only explicitly approved rehearsal/config/release changes
- **Supabase mutation:** Only approved isolated rehearsal or separately gated production changes
- **External provider configuration:** Only individually approved relevant configuration
- **Exact Owner authorization gate:** O-EXEC; O-BACKUP, O-RESTORE, O-NP-TARGET; production backup configuration separately O-PROD-CONFIG
- **Rollback/reversibility:** Destroy only approved disposable restore target; keep original source intact; no production overwrite
- **Evidence required for acceptance:** EV plus timed rehearsal, sanitized target/version/approval and observed failure/recovery evidence
- **What not to expand into:** Custom platform, unsafe production experiments, automatic purge or unsupported rollback promises
- **Completion boundary unlocked:** PRODUCTION
- **Parallel safety:** Apply §14 ownership/isolation rules; dependencies are acceptance edges, not permission for concurrent writes to shared files/databases.

### REC-29 — Private-object recovery and DB/object reconciliation

- **Planning ID:** REC-29
- **Priority:** P1
- **Plan group:** C
- **Backlog classification:** MUST_BEFORE_PRODUCTION
- **Objective:** Private-object recovery and DB/object reconciliation
- **Concrete user/product outcome:** Restored recruitment records retain correct accessible private files
- **Problem/finding IDs:** F20; C R11
- **Likely source areas:** Private Storage recovery tooling/manifests; document version/scan/reference records; runbooks44/66
- **Dependencies:** REC-28
- **What is preserved:** Private keys/bytes/hash/history and contextual access
- **What is changed:** Rehearse separate object recovery and DB/object reconciliation against recovered synthetic DB
- **What is explicitly NOT changed:** INV below; no unrelated domain/schema/framework replacement. Only the explicitly named required repair or capability may change behavior.
- **Acceptance criteria:** Current/historical/staged files accounted for by manifest/hash; missing/orphan/denied objects classified; scan provenance not forged; restored access matches persona and no public bucket
- **Required local tests:** Manifest/checksum and failure-resume validation
- **Required PostgreSQL/RLS/concurrency tests:** PG1 document metadata/reference/scan/cleanup consistency after DB restore
- **Required browser/E2E tests:** B1 legitimate recovered preview/download plus forbidden context
- **Required provider/runtime tests:** Actual private object restore and missing/corrupt/version mismatch tests
- **Independent review requirement:** Independent operations/security review; DB/storage specialist for recovery evidence
- **CI requirement:** CI1 exact release candidate and relevant operational evidence; no remote mutation automatically authorized
- **Vercel mutation:** Only explicitly approved rehearsal/config/release changes
- **Supabase mutation:** Only approved isolated rehearsal or separately gated production changes
- **External provider configuration:** Only individually approved relevant configuration
- **Exact Owner authorization gate:** O-EXEC; O-RESTORE, O-ARCHIVE, O-NP-TARGET; production object backup config O-PROD-CONFIG
- **Rollback/reversibility:** Keep original immutable objects until reconciliation; rollback restore target only; real data recovery requires new exact scope
- **Evidence required for acceptance:** EV plus timed rehearsal, sanitized target/version/approval and observed failure/recovery evidence
- **What not to expand into:** Custom platform, unsafe production experiments, automatic purge or unsupported rollback promises
- **Completion boundary unlocked:** PRODUCTION
- **Parallel safety:** Apply §14 ownership/isolation rules; dependencies are acceptance edges, not permission for concurrent writes to shared files/databases.

### REC-30 — Production monitoring and operator failure response

- **Planning ID:** REC-30
- **Priority:** P1
- **Plan group:** C
- **Backlog classification:** MUST_BEFORE_PRODUCTION
- **Objective:** Production monitoring and operator failure response
- **Concrete user/product outcome:** Operators detect/recover failed auth, writes, providers and capacity before silent loss
- **Problem/finding IDs:** F20,F17; C R12–R14
- **Likely source areas:** Existing safe logging/events and selected observability/runbooks; deployment and worker configuration
- **Dependencies:** REC-08, REC-09, REC-14, REC-26
- **What is preserved:** Audit continuity, narrow logging and retained data policy
- **What is changed:** Bind redacted logs/alerts/runbooks to actual release environment; rehearse failures and escalation
- **What is explicitly NOT changed:** INV below; no unrelated domain/schema/framework replacement. Only the explicitly named required repair or capability may change behavior.
- **Acceptance criteria:** ≥30 days searchable operational logs configured; no secrets/signed URLs/PII dumps; auth/RPC/storage/backup/deployment and mail/scan/cleanup backlog alerts; configurable capacity warnings 70/85/95%; 99.5% monthly target monitoring without claiming future availability measured
- **Required local tests:** Log redaction/error classification/alert routing tests
- **Required PostgreSQL/RLS/concurrency tests:** PG1 audit survives denied/failed mutations; read-only quota/query evidence
- **Required browser/E2E tests:** B1 actionable user failures distinct from operator telemetry
- **Required provider/runtime tests:** Real test alert delivery, stalled queue/lease/provider outage and recovery drills
- **Independent review requirement:** Independent operations/security review; DB/storage specialist for recovery evidence
- **CI requirement:** CI1 exact release candidate and relevant operational evidence; no remote mutation automatically authorized
- **Vercel mutation:** Only explicitly approved rehearsal/config/release changes
- **Supabase mutation:** Only approved isolated rehearsal or separately gated production changes
- **External provider configuration:** Only individually approved relevant configuration
- **Exact Owner authorization gate:** O-EXEC; O-OBSERVE, O-SECRETS, O-WORKER, O-PROD-CONFIG; nonprod drills O-NP-DATA
- **Rollback/reversibility:** Revert bad routing safely while retaining logs/audit; pause affected exposed workflow if observability lost
- **Evidence required for acceptance:** EV plus timed rehearsal, sanitized target/version/approval and observed failure/recovery evidence
- **What not to expand into:** Custom platform, unsafe production experiments, automatic purge or unsupported rollback promises
- **Completion boundary unlocked:** PRODUCTION
- **Parallel safety:** Apply §14 ownership/isolation rules; dependencies are acceptance edges, not permission for concurrent writes to shared files/databases.

### REC-31 — Identity operations, credential lifecycle and break-glass

- **Planning ID:** REC-31
- **Priority:** P1
- **Plan group:** C
- **Backlog classification:** MUST_BEFORE_PRODUCTION
- **Objective:** Identity operations, credential lifecycle and break-glass
- **Concrete user/product outcome:** Authorized operators recover/revoke identities without losing historical evidence
- **Problem/finding IDs:** F23; C S04/S05,R05/R14 and canonical recovery procedures
- **Likely source areas:** Server-only privileged configuration; narrow worker credentials; trusted identity recovery/break-glass runbooks and commands
- **Dependencies:** REC-02, REC-03, REC-04, REC-07
- **What is preserved:** Root protection, Auth/business separation, historical snapshots and least privilege
- **What is changed:** Inventory actual key types/consumers; plan supported rotation; rehearse Root break-glass, inactive/rebound session revocation and authorized Candidate email recovery if canonical path applies
- **What is explicitly NOT changed:** INV below; no unrelated domain/schema/framework replacement. Only the explicitly named required repair or capability may change behavior.
- **Acceptance criteria:** No browser privileged key; rotated credentials retain narrow worker role (not blanket admin); old secrets revoked safely; old identity loses access; historical Submission email unchanged and future snapshot uses newly verified identity; audit preserved
- **Required local tests:** Secret boundary and key-name/type compatibility checks; no secret content in report
- **Required PostgreSQL/RLS/concurrency tests:** PG1 Root/permission/binding/recovery direct roles, post-lock identity and historical snapshot invariants
- **Required browser/E2E tests:** B1 inactive/rebound/old-session denial, valid new login and operator recovery smoke
- **Required provider/runtime tests:** Actual nonprod credential rotation, Auth revoke/recovery and worker continuation; production separate approvals
- **Independent review requirement:** Independent operations/security review; DB/storage specialist for recovery evidence
- **CI requirement:** CI1 exact release candidate and relevant operational evidence; no remote mutation automatically authorized
- **Vercel mutation:** Only explicitly approved rehearsal/config/release changes
- **Supabase mutation:** Only approved isolated rehearsal or separately gated production changes
- **External provider configuration:** Only individually approved relevant configuration
- **Exact Owner authorization gate:** O-EXEC; O-KEYS, O-AUTH, O-IDENTITY; production rotation/config O-PROD-CONFIG; no live recovery under rehearsal approval
- **Rollback/reversibility:** Validated overlap only for rotation window; revoke old material; safe recovery/forward repair, never reopen old unauthorized binding
- **Evidence required for acceptance:** EV plus timed rehearsal, sanitized target/version/approval and observed failure/recovery evidence
- **What not to expand into:** Custom platform, unsafe production experiments, automatic purge or unsupported rollback promises
- **Completion boundary unlocked:** PRODUCTION
- **Parallel safety:** Apply §14 ownership/isolation rules; dependencies are acceptance edges, not permission for concurrent writes to shared files/databases.

### REC-32 — Production candidate promotion and real-data release

- **Planning ID:** REC-32
- **Priority:** P1
- **Plan group:** C
- **Backlog classification:** MUST_BEFORE_PRODUCTION
- **Objective:** Production candidate promotion and real-data release
- **Concrete user/product outcome:** Complete product can safely serve real recruitment users after explicit approval
- **Problem/finding IDs:** F20 final boundary; all unresolved acceptance findings
- **Likely source areas:** Exact production candidate, vetted forward migration and Vercel release/config plus runbooks
- **Dependencies:** REC-27, REC-28, REC-29, REC-30, REC-31, REC-34
- **What is preserved:** Accepted domain/history/security/evidence and tested nonprod candidate
- **What is changed:** Compare current remote inventory, rehearse compatible expand/contract promotion/backout, then separately authorize production DB, app and real-data admission
- **What is explicitly NOT changed:** INV below; no unrelated domain/schema/framework replacement. Only the explicitly named required repair or capability may change behavior.
- **Acceptance criteria:** PRODUCTION_READY gate §8 met: all approvals distinct; exact deployed SHA/schema/parity verified; production smoke without unauthorized PII; no real data until release approval; official PDF/privacy decisions settled
- **Required local tests:** L1 exact locked build/dependency security and configuration validation
- **Required PostgreSQL/RLS/concurrency tests:** PG1 production catalog parity read-only; authorized migration then safe role smoke; no destructive live test
- **Required browser/E2E tests:** B1 post-deploy safe smoke and session/private access; real-data use only after final gate
- **Required provider/runtime tests:** Approved production provider configuration/health and alert routing; test recipients until final admission
- **Independent review requirement:** Independent operations/security review; DB/storage specialist for recovery evidence
- **CI requirement:** CI1 exact release candidate and relevant operational evidence; no remote mutation automatically authorized
- **Vercel mutation:** Only explicitly approved rehearsal/config/release changes
- **Supabase mutation:** Only approved isolated rehearsal or separately gated production changes
- **External provider configuration:** Only individually approved relevant configuration
- **Exact Owner authorization gate:** O-EXEC; O-PROD-CONFIG, O-PROD-MIG, O-PROD-DEPLOY, O-REALDATA separately; O-LEGAL/O-PDF-USE and all applicable provider gates
- **Rollback/reversibility:** Known-safe compatible app rollback; irreversible DB changes forward-repair or explicitly approved restore with data-loss reconciliation; no automatic DOWN
- **Evidence required for acceptance:** EV plus timed rehearsal, sanitized target/version/approval and observed failure/recovery evidence
- **What not to expand into:** Custom platform, unsafe production experiments, automatic purge or unsupported rollback promises
- **Completion boundary unlocked:** PRODUCTION
- **Parallel safety:** Apply §14 ownership/isolation rules; dependencies are acceptance edges, not permission for concurrent writes to shared files/databases.


## 9. Process/governance simplification plan

### D. PROCESS / GOVERNANCE SIMPLIFICATION

Essential product truth REC-33 may be prepared early and requires later explicit registry/governance-write authorization. It does not reopen legitimate accepted backend work; it corrects the false inference that backend/task closure proves complete features. It is mandatory before PHASE1_COMPLETE, not a gate on first local P0 code. This artifact itself modifies no registry.

The canonical deployment document demands DB integration for every integration commit; current governance/workflow permits narrower skips. REC-34 requires controlled Owner/source reconciliation before changing that rule. Conservatively satisfying both pending reconciliation is not selecting one as authoritative. If the existing process literally cannot accept a safe repair, escalate this gate early; otherwise do not put optional CI economy ahead of local correctness.

REC-35 follows product truth and completion, reduces only duplicate equivalent proof, and preserves distinct high-risk implementation/re-review/composition facts. Current path-aware mechanism and immutable accepted evidence remain valuable. REC-36 is a decision checkpoint, not permission to refactor.

### REC-33 — Truthful feature coverage and derived status

- **Planning ID:** REC-33
- **Priority:** P1
- **Plan group:** D
- **Backlog classification:** MUST_BEFORE_PHASE1_COMPLETE
- **Objective:** Truthful feature coverage and derived status
- **Concrete user/product outcome:** Accepted backend work is not confused with finished user capability
- **Problem/finding IDs:** F19,F22 stale traceability; C G12–G16
- **Likely source areas:** Existing task/slice/traceability authorities only after later governance-write approval; canonical feature coverage and composition evidence
- **Dependencies:** None among REC labels; applicable Owner execution/access gate still required
- **What is preserved:** Valid historical task acceptance, single authority and explicit hold
- **What is changed:** Correct false feature-complete representation/stale derived reports and require source→capability coverage for unmaterialized requirements
- **What is explicitly NOT changed:** INV below; no unrelated domain/schema/framework replacement. Only the explicitly named required repair or capability may change behavior.
- **Acceptance criteria:** Every A R01–R32 requirement has implemented/proved/explicitly unresolved status; absent UI not DONE; empty frontier not source exhaustion; prior accepted backend facts retained
- **Required local tests:** Existing control validators plus semantic source/evidence review, not validator-only certification
- **Required PostgreSQL/RLS/concurrency tests:** N/A — no runtime DB change
- **Required browser/E2E tests:** N/A — consumes actual product browser evidence without inventing it
- **Required provider/runtime tests:** N/A — consumes runtime receipts
- **Independent review requirement:** Independent governance/source and product composition reviewer
- **CI requirement:** CI1 governance validation; integration DB rule satisfied or Owner-reconciled, no skip assumed
- **Vercel mutation:** No
- **Supabase mutation:** No
- **External provider configuration:** No
- **Exact Owner authorization gate:** O-GOV-WRITE; no registries changed by Phase E and no approval to materialize work inferred
- **Rollback/reversibility:** Versioned corrections preserve old evidence; no rewrite of accepted checkpoints
- **Evidence required for acceptance:** EV exact authority diff, source coverage and fresh derived-report consistency
- **What not to expand into:** Second registry/scheduler; retroactively erasing valid acceptance
- **Completion boundary unlocked:** PHASE-1 PRODUCT COMPLETENESS
- **Parallel safety:** Apply §14 ownership/isolation rules; dependencies are acceptance edges, not permission for concurrent writes to shared files/databases.

### REC-34 — Canonical CI authority reconciliation

- **Planning ID:** REC-34
- **Priority:** P1
- **Plan group:** D
- **Backlog classification:** PROCESS_IMPROVEMENT
- **Objective:** Canonical CI authority reconciliation
- **Concrete user/product outcome:** Operators know which exact-SHA integration gates are required
- **Problem/finding IDs:** C Z07; F22 policy tension
- **Likely source areas:** Canonical deployment44:83–91, autonomy policy and integration CI selector through controlled source path
- **Dependencies:** REC-03, REC-04
- **What is preserved:** Independent high-risk review, exact SHA, checkpoints, composition and path-selection mechanism
- **What is changed:** Owner/source authority resolves every-integration-commit DB rule versus governance-only skips; only then align affected policy/workflow
- **What is explicitly NOT changed:** INV below; no unrelated domain/schema/framework replacement. Only the explicitly named required repair or capability may change behavior.
- **Acceptance criteria:** Written authorized disposition and selector fixtures demonstrate no affected/shared domain can be suppressed; unknown paths broaden; no mandatory source silently overruled
- **Required local tests:** Policy/selector fixture checks after decision; existing control validation
- **Required PostgreSQL/RLS/concurrency tests:** Required DB integration remains satisfied under conservative union pending decision; this is not a claim conflict resolved
- **Required browser/E2E tests:** N/A — no product UI change
- **Required provider/runtime tests:** N/A — no provider change
- **Independent review requirement:** Independent canonical-source/governance and CI security review
- **CI requirement:** CI1 exact workflow candidate with all required domains and selector regression
- **Vercel mutation:** No
- **Supabase mutation:** Local CI DB only if mandated; no remote
- **External provider configuration:** No
- **Exact Owner authorization gate:** O-CI-SOURCE plus O-GOV-WRITE before policy/workflow edits; can be escalated earlier only if current procedure literally blocks acceptance
- **Rollback/reversibility:** Restore previously safe gate configuration while retaining source decision; never silently weaken checks
- **Evidence required for acceptance:** EV authority decision and exact-SHA selector/CI evidence
- **What not to expand into:** Making optional CI economy prerequisite to local P0 repair
- **Completion boundary unlocked:** PRODUCTION acceptance governance; not a new product capability
- **Parallel safety:** Apply §14 ownership/isolation rules; dependencies are acceptance edges, not permission for concurrent writes to shared files/databases.

### REC-35 — Evidence serialization and duplicate-review economy

- **Planning ID:** REC-35
- **Priority:** P2
- **Plan group:** D
- **Backlog classification:** PROCESS_IMPROVEMENT
- **Objective:** Evidence serialization and duplicate-review economy
- **Concrete user/product outcome:** Repeated same-fact proof costs less without losing independent acceptance
- **Problem/finding IDs:** F22; C G08–G13
- **Likely source areas:** Existing evidence links/derived reports/review transition conventions only
- **Dependencies:** REC-27, REC-33, REC-34
- **What is preserved:** Distinct prompt/implementation/repair/composition facts and exact reviewed/CI/checkpoint provenance
- **What is changed:** Consolidate only equivalent same-fact serialization, derive existing views where justified and remove reporting-only broadening under reconciled rule
- **What is explicitly NOT changed:** INV below; no unrelated domain/schema/framework replacement. Only the explicitly named required repair or capability may change behavior.
- **Acceptance criteria:** Measured duplicate transitions removed; changed fixture/workflow/shared risks retain fresh review; no claim external producer audit substitutes independent acceptance
- **Required local tests:** Existing control/derived-view/provenance checks and before/after workflow evidence
- **Required PostgreSQL/RLS/concurrency tests:** N/A except integration gate required by resolved policy
- **Required browser/E2E tests:** N/A — no UI change
- **Required provider/runtime tests:** N/A — no runtime provider
- **Independent review requirement:** Independent governance review of preserved proof obligations
- **CI requirement:** CI1 under REC-34 authorized selector; no blanket full-ci or blanket skip
- **Vercel mutation:** No
- **Supabase mutation:** No remote
- **External provider configuration:** No
- **Exact Owner authorization gate:** O-GOV-WRITE; separate approved scope, not automatic after product completion
- **Rollback/reversibility:** Revert evidence mechanics with links/history intact; no checkpoint movement
- **Evidence required for acceptance:** EV actual duplicated work and equivalent preserved obligations, not projected savings
- **What not to expand into:** New control platform, repeated fresh review of unchanged facts
- **Completion boundary unlocked:** No independent completion gate; PROCESS_IMPROVEMENT
- **Parallel safety:** Apply §14 ownership/isolation rules; dependencies are acceptance edges, not permission for concurrent writes to shared files/databases.

### REC-36 — Evidence-driven Option-B reassessment

- **Planning ID:** REC-36
- **Priority:** P2
- **Plan group:** D
- **Backlog classification:** PROCESS_IMPROVEMENT
- **Objective:** Evidence-driven Option-B reassessment
- **Concrete user/product outcome:** Observe whether bounded consolidation now lowers total remaining recovery cost
- **Problem/finding IDs:** Phase D narrow A/B decision; C A04–A08/G09
- **Likely source areas:** Actual recovery diffs, review defects, caller/state changes and effort/evidence logs; no source modification at checkpoint
- **Dependencies:** REC-13, REC-15, REC-17
- **What is preserved:** Option A and all domain/security/concurrency/history guarantees
- **What is changed:** Evaluate OPTION_B_REASSESSMENT_GATE; authorize no implementation by the checkpoint itself
- **What is explicitly NOT changed:** INV below; no unrelated domain/schema/framework replacement. Only the explicitly named required repair or capability may change behavior.
- **Acceptance criteria:** Record duplicated mechanics fixes, repeated actor/error review defects, state-owner change proportion, review churn and observed friction; choose only named outcomes in §13 with scoped Owner decision
- **Required local tests:** N/A — evidence analysis, not benchmark invention
- **Required PostgreSQL/RLS/concurrency tests:** N/A — retain all existing proof when later scoped changes are authorized
- **Required browser/E2E tests:** N/A — use actual accepted behavior evidence
- **Required provider/runtime tests:** N/A — provider delays separated from mechanics cost
- **Independent review requirement:** Independent architecture/source reviewer challenges claimed savings including migration/re-proof
- **CI requirement:** CI1 documentary scope only; any later code has separate gates
- **Vercel mutation:** No
- **Supabase mutation:** No
- **External provider configuration:** No
- **Exact Owner authorization gate:** O-OPTION-B before bounded consolidation; FULL_REWRITE unavailable without reopening Phase-D threshold
- **Rollback/reversibility:** Continue A if benefit unproved; no code or authority changed by analysis
- **Evidence required for acceptance:** Actual before/after evidence and decision with costs, excluded scope and no invented durations
- **What not to expand into:** Automatic broad refactor or full rewrite from this checkpoint
- **Completion boundary unlocked:** No independent completion gate; PROCESS_IMPROVEMENT
- **Parallel safety:** Apply §14 ownership/isolation rules; dependencies are acceptance edges, not permission for concurrent writes to shared files/databases.


## 10. External-runtime integration plan

There is no located repository malware engine or operational mail launcher, and cleanup lacks complete discovery/scheduling. Inventory may reveal reusable external execution; do not build a duplicate before checking. Execution is mandatory even if host/provider choice remains open.

| Runtime | Preserved seam | Required real effect and proof | Boundary |
|---|---|---|---|
| Auth OTP/Google | Managed credential proof plus trusted business binding | Real test OTP/Workspace exchange, redirects, request/response refresh, inactive/revoked denial; REC-02/07/13 | First functional UAT; not supplied by business outbox |
| Malware | Byte/MIME/hash check, durable reservation/request/lease, worker-only verdict, CLEAN continuation | REC-08 proves actual approved engine, same immutable bytes, accepted PDF/Word/PPT/PNG/JPEG formats, forged/stale/cancelled/unavailable/infected fail-closed; no file becomes usable from MIME inspection alone | Required CV makes real execution first-UAT critical |
| Email | Existing outbox/history/replay/leases and contextual preview/send | REC-09 real allowlisted receipt, retry/reclaim/permanent failure, stale preview recipient/version, audit and parent-authorized history/deletion. Canonical up-to-24h/provider-equivalent retry must be reconciled with finite current attempts; no automatic infinite retry or exactly-once delivery promise | Real effect for promised UAT notifications; full behavior before Phase1 |
| Cleanup | Existing discovery SQL, exact-object runner, provenance/tombstone/fence | REC-14 expiry discovery plus actual authenticated recurring launch, provider delete failures, stale lease and backlog alert. Manual synthetic disposal for bounded UAT is not unattended acceptance | Before Phase1; earlier if UAT becomes prolonged/unattended |
| PDF | Authorized report projection/current-round model | REC-20 content-correct actual bytes/fonts/blank/decision/order/private metadata/audit and measured runtime budget | Mandatory Phase1; only official pixel fidelity deferred |

No queue/broker/daemon fleet is presumed. One bounded approved invocation mechanism per runtime suffices if it meets actual provider/runtime limits. All provider credential, project, schedule and deployment changes require individual §12 gates. Production provider activation is separately approved; it is not inherited from test setup.

## 11. Database migration/recovery strategy

1. Establish REC-01 disposable proof first. Separate privileged fixture creation from actual authenticated/anon/worker assertions. Record target identity/version and reject accidental shared/production targets. No database availability means no SQL acceptance; source evidence remains useful but insufficient.
2. Build **new forward migrations** over the effective baseline. Do not edit/squash accepted migration files or execute starter schema as an alternative production bundle. Inspect later effective definitions/grants/policies and every impacted caller.
3. Prove both clean replay and representative baseline-to-repair upgrade with synthetic retained Candidates/Submissions/Applications/rounds/participants/reports/objects/acknowledgements/email/audit/attempts. Preserve IDs, historical snapshots, versions, replay keys and pending job provenance. No empty-live-data assumption.
4. REC-03 handles alternate-path confidentiality and legitimate readers; REC-04 treats lock order, reactivation outcome, NULL tokens and batch rollback as a single composed boundary. Deterministic two-session proof must include opposing create/copy/reactivate/delete and participant/resource crossings, post-lock revalidation and side-effect rollback. REC-12 preserves source-approved report disjoint/owner behavior instead of imposing whole-row equality.
5. Before **each** remote apply, compare current remote migration history/catalog/Auth triggers/grants/private Storage; stop on unexplained drift. Rehearse exact reviewed forward set in isolated nonprod with explicit O-NP-MIG. No reset of an unknown shared project, no automatic resume.
6. Plan additive-first schema/application compatibility, bounded lock/statement limits and complete caller migration. Repaired confidentiality may intentionally remove unsafe direct access; any old app depending on that access is not a valid fallback. Do not build a permanent legacy shim to keep a leak working.
7. Pause/fence affected writes/claims only where necessary and approved; account for in-flight external attempts, accepted mail ambiguity and object deletion. No default dual-writing or whole-job re-enqueue. Pending work survives under one authoritative executor.
8. For a logically irreversible migration, rollback means safe compatible application rollback plus retained security fixes, **forward repair**, or an explicitly approved DB-and-object restore with RPO loss/reconciliation. A fictional DOWN migration, old vulnerable build or DB-only backup is not a recovery strategy.
9. Production apply and Vercel promotion are distinct O-PROD-MIG/O-PROD-DEPLOY gates after REC-28/29 and compatibility proof. Real data enters only after O-REALDATA. All accepted evidence refers to exact candidate SHA/catalog/target; historical CI for another SHA is not sufficient.

## 12. Owner Decision Ledger

These are separate decisions, not one bundled cloud permission. Read-only inspection is normally allowed where available; it cannot resume a project, reveal secret values or authorize later writes. O-EXEC governs later implementation only; every external boundary below remains independently gated. Decisions should record target, exact candidate/config/migration scope, permitted data, operator, effects and backout. No gate is exercised in Phase E.

| Gate | Boundary | Required decision |
|---|---|---|
| O-EXEC | Implementation scope | Separate Owner acceptance of this review and authorization of an exact bounded code/test/document workset; plan approval is not automatic execution or Git integration authority. |
| O-LOCAL | Local environment change | Explicit permission for any needed install/service/system change; ordinary read-only checks normally allowed. Only disposable database setup within authorized scope. |
| O-READ | Read-only inspection | Normally allowed where available and within access policy; metadata only, no secret/PII export. Access absence is a gap, not mutation authority. |
| O-NP-TARGET | Non-production target selection | Approve exact isolated project/environment mapping and synthetic-data boundary after inventory; no production reuse inferred. |
| O-NP-CREATE | New Supabase project | Separate approval for new isolated project, region/cost/ownership; never automatic when existing target is inconvenient. |
| O-NP-RESUME | Resume project | Separate approval naming exact non-production project and effects; read-only inventory cannot resume it. |
| O-ENV | Non-production environment/configuration | Approve exact Vercel root/build/env-name mapping and configuration changes; values remain in secure channel. |
| O-AUTH | Auth providers and redirects | Approve exact nonprod OTP/SMTP/Google/redirect/site configuration and test identities; production changes additionally O-PROD-CONFIG. |
| O-NP-MIG | Remote non-production migration | Approve target, reviewed migration set/SHA, parity diff, rehearsal and forward-repair/backout; no reset implied. |
| O-DEPLOY | Non-production Vercel deployment | Approve target and exact reviewed candidate plus synthetic exposure/protection; not production promotion. |
| O-NP-DATA | Non-production synthetic writes | Approve isolated fixture accounts/records/object/mailbox scope and cleanup responsibility; never production PII. |
| O-NP-LOAD | Non-production load tests | Approve target, quotas, recipient isolation and provider impact; no production stress test. |
| O-SCANNER | Scanner operational decision | Approve engine/service, supported formats, private processing/location, retention, costs and trust boundary after inventory; no vendor preselected. |
| O-MAIL | Email operational decision | Approve provider/domain/sender/test routing/recipient allowlist and retry equivalence where source permits; Auth mail remains distinct. |
| O-SECRETS | Provider/worker secret configuration | Approve each credential/role binding and secure destination; never place values in review logs; not a general service-role bypass. |
| O-WORKER | External host/scheduler/invocation | Approve exact runtime/trigger/cadence/identity, lease and pause procedure; Vercel deployment/config has its own gates. |
| O-SOURCE | Canonical behavior resolution | Approve controlled source disposition for report actor/field/version precedence or unresolved retry semantics before acceptance/code assumes an answer. |
| O-ABUSE | S08-002 hold and abuse authority | Owner/governance-authority resolution of current hold and mandatory rate-limit scope, followed by distinct bounded execution approval if needed. This plan neither lifts hold nor materializes TASK-S08-002. |
| O-PDF-USE | PDF operational use | Approve wording/operational use of nonofficial content-correct PDF; official pixel template supplied/approved separately. Generic PDF capability remains mandatory. |
| O-LEGAL | Privacy/legal content | Approve notice VI/EN text, retention/vendor-location policy and lawful operations; immutable historical acknowledgements cannot be rewritten. |
| O-NP-MAINT | Non-production maintenance rehearsal | Approve exact synthetic notice publication/export/archive/purge rehearsal, target and audit trail. |
| O-PROD-MAINT | Production maintenance operation | Separate approval for each live notice switch, selected archive/purge or destructive restoration; exact records/objects, reason, custody, backups and audit required. |
| O-ARCHIVE | Archive/custody/export | Approve recipients, encrypted custody, manifest/checksum and sample-restore handling; no blanket data export permission. |
| O-BACKUP | Backup configuration | Approve provider plan/retention/PITR/export settings; production additionally O-PROD-CONFIG. |
| O-RESTORE | Restore rehearsal/operation | Approve exact isolated target and data class; production overwrite is a new O-PROD-MAINT decision with explicit loss/reconciliation, not a drill side effect. |
| O-PROD-CONFIG | Production configuration | Approve exact production env/Auth/Storage/provider/backup/monitoring changes independently of UAT approvals; no deployment implicit. |
| O-OBSERVE | Monitoring/alerts | Approve destination/retention/access/redaction and alert recipients; test alerts remain synthetic. |
| O-KEYS | Credential rotation | Approve actual key types, narrow consumers, rotation overlap/revocation and recovery scope; never infer material from variable name alone. |
| O-IDENTITY | Break-glass/recovery/revocation | Approve rehearsal or named live recovery separately, authorized operator and audit; never grant general root impersonation. |
| O-PROD-MIG | Production database migration | Approve exact reviewed forward migrations, current parity/data inventory, backup/compatibility/recovery and maintenance scope. |
| O-PROD-DEPLOY | Production Vercel promotion | Approve exact production-target built artifact/env/schema compatibility and safe rollback; no automatic promotion of Preview config. |
| O-REALDATA | Production real-data admission | Final explicit release decision after complete product, security/provider/privacy/recovery evidence; deploy approval alone does not permit recruitment PII. |
| O-GOV-WRITE | Governance/registry changes | Separate bounded authority to correct registries/traceability or evidence mechanics; no new task materialization follows from REC labels. |
| O-CI-SOURCE | CI canonical-authority reconciliation | Controlled Owner/source decision resolving deployment rule versus governance skips before narrowing or claiming conformity; retain independent review and exact SHA. |
| O-OPTION-B | Bounded consolidation | Approve specific evidence-backed area, total-cost case, preserved interfaces and proof before any Option-B implementation. |
| O-NEW-SCOPE | Deferred scope reopening | New canonical need or measured constraint plus Owner-approved bounded scope; full rewrite additionally reopens Phase-D threshold. |

If a target-creation gate is needed during a backup/restore drill, O-NP-CREATE applies in addition to O-RESTORE; resuming an existing target similarly needs O-NP-RESUME. A provider credential change never rides implicitly on permission to read provider metadata. Conditional mutations in cards require the same specific gate when they become necessary.

## 13. OPTION_B_REASSESSMENT_GATE

REC-36 occurs after an accepted functional cohort and representative Option-A HR/Interview changes (REC-13/15/17, including report proof REC-12). It is not a prerequisite to completing unrelated product work. If evidence is insufficient, record that and continue A; do not refactor to manufacture a sample.

Collect actual counts of duplicated fixes across command styles; repeated review findings attributable to inconsistent actor/error mechanics; number and proportion of state-owner statements/behaviors changed in Inbox/Interview/Reports with an explicit denominator and semantic explanation; review rounds reopened for the same mechanics; observed maintenance/knowledge-transfer friction. Separate provider waiting, business-scope additions and canonical ambiguity from code-mechanics cost. Raw line count or code churn alone is not causation.

Permitted decision outcomes are exactly:

- **CONTINUE_OPTION_A:** no credible lower remaining total-cost case, or evidence incomplete.
- **AUTHORIZE_BOUNDED_OPTION_B_SIMPLIFICATION:** only after O-OPTION-B approves a specific repeated responsibility, all affected callers, preserved behavior, migration/re-proof/rollback cost, independent review and an observable stopping condition. No cross-project program by default.

FULL_REWRITE is not an outcome of this gate. It requires a separate reopening of Phase D with structural evidence and comparative security/concurrency/data/provider/cutover proof. A small feature-owned extraction needed for the accepted fix does not require declaring a strategy switch; systematic consolidation across consumers does. No optional refactor is part of the first execution package.

## 14. Critical path and parallelizable work

This is a dependency graph expressed as prerequisite sets, not invented durations. The exact longest elapsed path cannot be known without provider/cloud facts. The **shortest safe chain** avoids optional process work and deferred architecture while respecting every safety gate.

### To FIRST_TRUSTWORTHY_FUNCTIONAL_UAT_PREVIEW

- Independent starting lanes: REC-01 disposable substrate; REC-06 read-only inventory; REC-10 abuse authority; REC-02 code preparation under O-EXEC without waiting for cloud.
- REC-01 permits accepted local REC-02, REC-03 confidentiality and REC-04 composed SQL proof. REC-03 + REC-04 permit REC-12 report precedence/context proof once O-SOURCE resolves semantics. REC-02 + REC-04 permit REC-05 explicit-open composition.
- Join REC-06 + REC-02 + REC-03 + REC-04 + REC-12 at REC-07 approved target preparation. Only then accept real target integrations REC-08 scanner and REC-09 mail; they can be built locally earlier but cannot claim connected proof before target/credential approval.
- REC-10 + REC-02 + REC-06 permit REC-11 approved abuse-boundary proof. Unresolved hold blocks functional exposure, not local security repair. No implicit exemption is invented.
- Join REC-05 + REC-07 + REC-08 + REC-09 + REC-11 + REC-12 at REC-13: deployed real synthetic cohort. REC-34/35/36 are not unconditional predecessors; CI rules must nevertheless be satisfied, and a literal procedure block triggers early O-CI-SOURCE escalation.

### Shortest continuation to PHASE1_COMPLETE

While UAT runtime work proceeds, safely prepare independently visible product slices: REC-15 HR fields, REC-17 Interview documents, REC-18 masters, REC-19 users, REC-20 PDF and REC-24 notice operations after their own prerequisites. REC-16 adds files over accepted HR editing; REC-14 supplies recurring cleanup. REC-25 retention and REC-26 measured load use isolated targets and approval. No need to wait for the first deployment before local UI work, but its acceptance still requires real target proof.

REC-21 closes language coverage over the completed surfaces; REC-22 proves actual Candidate mobile/notice behavior; REC-23 independently certifies full keyboard/WCAG coverage. REC-33 corrects source-completeness truth. **Join all of REC-13 through REC-26 plus REC-33 at REC-27 → PHASE1_COMPLETE.** Nothing in deferred REC-37 is required; none of these mandatory features may be silently moved there. Reuse unchanged local/security evidence with provenance, but run fresh complete composition on the final candidate.

### Shortest continuation to PRODUCTION_READY

REC-28 DB restore may start after isolated target REC-07; REC-29 proves objects against that recovered DB. REC-31 identity operations follows local trust plus target. REC-30 production observability builds on accepted runtime and measured capacity. REC-34 resolves release-governance authority independently of optional economy. **Join REC-27 + REC-28 + REC-29 + REC-30 + REC-31 + REC-34 at REC-32 → PRODUCTION_READY**, with distinct production configuration/migration/promotion and final real-data gates. REC-35 process economy follows completion rather than delaying value; REC-36 may proceed at its earlier evidence checkpoint without blocking either release milestone.

### Safe parallelism and ownership

| Independent lanes | Conditions / serialization boundary |
|---|---|
| Auth code preparation; disposable DB setup; inventory; source decisions | Distinct files/roles, no cloud mutation under read permission; auth DB acceptance waits for harness |
| Confidentiality REC-03 and SQL REC-04 | Separate writing worktrees/isolated DBs only; serialize migration integration and jointly re-prove catalog/callers/order; overlapping function or consumer ownership serializes |
| Scanner and mail integrations | Independent provider identities/outboxes; no shared secret or worker role; target approval first; shared configuration has one integration owner |
| HR edit/docs; Interview materials; masters; users; PDF | Partition real file/state ownership. REC-15/16 same drawer serialize. Interview/report materials and PDF may share report consumers: serialize overlap or keep separate bounded interfaces, never concurrent same-file writers |
| Notice/retention, load, DB/object recovery and monitoring | Distinct approved disposable targets/datasets where destructive/load drills could interfere; object restore acceptance follows recovered DB; no shared live-data drills |
| Source-coverage truth and product implementation | Governance writes separately authorized; consume verified evidence rather than predeclare completion; no competing registry |

Never let multiple writing agents modify one worktree. Separate branches/worktrees would themselves require later execution authorization; none are created here. Shared migration chronology, schema/catalog acceptance, final CI and target deployment are serialized by one integration owner. Independent code authoring is not independent acceptance of crossed invariants.

## 15. Deferred/non-goals

### E. EXPLICITLY DEFERRED WORK

| Excluded work | Why outside the shortest safe path / reopening condition |
|---|---|
| Framework rewrite | F01 is an env/session defect, not demonstrated platform impossibility; reopen only on measured unsupported requirement |
| DB rewrite | Required identities/transactions remain compatible; migration and full security/concurrency re-proof add cost without established gain |
| Generalized command bus | Existing explicit intents suffice; no evidence a new dispatch abstraction reduces the bounded repair bill |
| Universal workflow engine | Phase-1 rules are finite; generic configuration does not fix current omitted commands/providers |
| Global state platform | Dirty bases and scoped ownership must survive; introduce only if measured unavoidable state-coordination problem beats local extraction |
| Generic master-data engine | Eleven finite business categories plus Users security surface need actual forms, not metadata infrastructure |
| Search cluster | Canonical indexed/paginated workload must be measured first; no demonstrated need |
| Distributed microservices | Would add auth/transaction/network boundaries without solving current composition failures |
| Multi-region writes | No approved requirement; conflicts/history/recovery costs are substantial |
| Event sourcing | Audit is required evidence, not a mandate to replace transactional state authority |
| Full frontend component rewrite | Existing Candidate/Inbox/Interview/Report behavior has value and expensive rediscovery; no measured replacement win |
| Historical migration squashing | Accepted history is provenance and unknown live upgrade input; forward repair instead |
| Dashboard/KPI/Candidate Database | Canonically future-hidden product modules; operational capacity/alerts remain mandatory and are not deferred with them |
| Offer/onboarding automation | Outside Phase-1 workflow scope; do not create placeholders or side queues |
| Pixel-perfect official PDF before approved template | No approved pixels to implement; generic content-correct export remains mandatory, operational wording needs O-PDF-USE |
| Broad cosmetic refactoring | Adds review/behavior risk without required user outcome; local feature-owned clarity is allowed |
| Automatic business TTL purge / campaign platform / speculative broker | Conflicts with retention policy or absent requirement; real temporary cleanup, bounded mail and scan execution remain mandatory |

### REC-37 — Explicit scope-exclusion envelope

- **Planning ID:** REC-37
- **Priority:** P2
- **Plan group:** E
- **Backlog classification:** DEFERRED
- **Objective:** Explicit scope-exclusion envelope
- **Concrete user/product outcome:** Protect the shortest safe path from speculative architecture and future product work
- **Problem/finding IDs:** A deferred scope; C P19/P26/X12/Z03; D verdict
- **Likely source areas:** Only planning scope ledger §15; no runtime source area authorized
- **Dependencies:** None among REC labels; applicable Owner execution/access gate still required
- **What is preserved:** All mandatory PDF/provider/security/product requirements remain in active slices
- **What is changed:** No implementation; reconsider only under separately approved requirement/evidence
- **What is explicitly NOT changed:** INV below; no unrelated domain/schema/framework replacement. Only the explicitly named required repair or capability may change behavior.
- **Acceptance criteria:** Every §15 exclusion has rationale and reopening evidence; official template fidelity does not disable generic export
- **Required local tests:** N/A — no change
- **Required PostgreSQL/RLS/concurrency tests:** N/A — no change
- **Required browser/E2E tests:** N/A — no change
- **Required provider/runtime tests:** N/A — no change
- **Independent review requirement:** Owner/source review required before scope reopening
- **CI requirement:** N/A — no implementation commit planned
- **Vercel mutation:** No
- **Supabase mutation:** No
- **External provider configuration:** No
- **Exact Owner authorization gate:** O-NEW-SCOPE; template publication alone does not authorize architecture rewrite
- **Rollback/reversibility:** No runtime state to roll back
- **Evidence required for acceptance:** Explicit excluded scope and authority needed to reopen
- **What not to expand into:** Treating mandatory operations as deferred analytics
- **Completion boundary unlocked:** No completion boundary unlocked; DEFERRED
- **Parallel safety:** Apply §14 ownership/isolation rules; dependencies are acceptance edges, not permission for concurrent writes to shared files/databases.


## 16. Acceptance/evidence model

Every slice card answers the quality questions: observable user value or safety boundary (objective/outcome/acceptance); minimal dependency (ledger); retained invariants (preserved/INV); bounded changed/not-changed scope; real tests/provider effects; reversible or explicit forward repair; named Owner gates; isolated parallelism. No card exists only to manufacture a task status. REC-01 is a blocking evidence substrate, REC-10/12 resolve real behavior/authority ambiguity, REC-37 protects scope and performs no implementation. Distinct user-visible features and DB/object recovery proof are intentionally not one catch-all ticket.

Acceptance requires EV, not a worker completion claim. The parent examines actual diff/result, obtains fresh focused verification and independent high-risk review, closes bounded repairs with appropriate re-review, binds CI/deployment to exact SHA, and checks full composition at REC-13/27/32. A task can be accepted within scope without claiming its whole feature complete. Review fields apply to negative paths and external effects, not just happy paths. New tests should catch consumer-visible failures and follow existing isolation conventions; actual direct-role SQL and two-session evidence are mandatory where specified.

Safety counterexamples retain provenance: use B's F01 reproduction without rerunning merely to dispute it; reproduce unexecuted SQL counterexamples in disposable infrastructure and retain failing-before/passing-after evidence where practical. Never claim tests run in this planning phase. Missing runtime access/DB availability/Owner decision is a named blocker, not permission to substitute mocks, shared data, source-text assertions or a simpler product.

For all cloud mutations record the separate gate decision and actual target. For privacy/audit export, preserve custody and redaction. Deployed auth/private documents require current context; signed-download lifetime remains a bounded residual exposure to assess, not a promise of immediate invalidation. Revoke newly authorized access after participant removal/inactivity and prove applicable expiry semantics.

This document's own verification is structural and documentary: required sections, every field for 37 unique REC cards, valid priority/group/classification, all dependencies resolving with no cycles, explicit gate coverage, UAT/Phase1/production joins, immutable A/B/C/D, final declarations/marker and remote bytes. It does not certify the product or approve execution.

## 17. Recommended immediate first execution package

**Proposed first package after separate Owner execution approval: REC-01 + REC-03.** This is a bounded local confidentiality repair, not a standalone test scaffold. It establishes disposable proof and closes the most fundamental known direct-data trust defect before connecting a functional cloud cohort.

- **Bounded scope/findings:** F02 alternate-path Interviewer disclosure and safe errors on those paths; disposable evidence prerequisite. Inventory all legitimate exposed Interview readers and affected DTO/private-document consumers, implement a narrow forward grant/projection/policy repair selected from evidence, migrate impacted current callers, and prove their behavior. No blanket redesign prescribed.
- **Why first:** F02 is P0 and cannot be repaired by hiding a field or rewriting a page. Actual authenticated role proof is unavailable without the disposable substrate. This package produces a safety result, not merely a runnable database.
- **Expected result:** Interviewer cannot retrieve HR-only notes/content or protected source metadata through current direct tables, projections, RPCs, DTOs and private/HTML paths, while valid HR/contextual historical reads survive. Candidate/unassigned/removed/hidden/inactive negative cases are included. Future generated PDF remains REC-20 with inherited confidentiality regression; absence of PDF is not pretended to be its security proof.
- **Likely areas:** new forward migration over effective Interview grants/policies/read projections; supabase/tests and the minimal existing test harness; web/src/lib/reports, application-inbox detail adapters and existing private preview/action error boundaries only when caller migration requires it. No accepted migration edits.
- **Tests:** successful isolated startup/clean replay and representative baseline-upgrade/effective catalog; privileged fixture setup separate from genuine authenticated/anon non-BYPASSRLS assertions; failing-before/passing-after direct column/table/projection/RPC counterexample; allowed-reader regression and real current consumer/private-path checks. Use legitimate disposable Auth-issued test sessions for local server/consumer proof if browser login is still broken; do not bypass server identity. This does not certify OTP/Google UAT. If a current consumer cannot be exercised, disclose and block that package acceptance rather than call it complete. Test actual authorization recheck/context loss and safe error redaction.
- **Independent review/CI:** database-security reviewer plus affected consumer review; inspect exact effective grants, legitimate callers and denied paths; fresh focused checks and required exact-SHA integration gates. No source-regex/DTO-only substitute. Local auth/session REC-02 and coordinated SQL REC-04 may be developed independently with separate ownership; their defects are not declared fixed by this package.
- **Locality/Owner gate:** entirely local under O-EXEC and any needed O-LOCAL setup approval. **No Vercel, remote Supabase or provider mutation required.** No production secret or shared database. If Docker/local Supabase cannot run, restore an approved local disposable facility or remain blocked; do not move the tests to production/shared dev.
- **Completion evidence:** exact diff/SHA, effective catalog and role identity, actual counterexample/positive-reader outputs, affected consumer traces, independent review and exact-SHA CI, compatible forward-repair/backout note. No runtime readiness claimed outside this boundary.
- **Deliberately excluded:** F01/F18 implementation, F04–F07 transaction repair, missing UI/PDF/provider code, new cloud configuration, held abuse implementation, governance economy, optional abstractions and broad cosmetic extraction. All remain active planned obligations, not dropped scope.

No task is created by this package description. Owner review of the strategic artifact and a separate explicit bounded execution authorization are still required.

## 18. Final strategic handoff

The selected strategy remains Option A with no full rewrite; see the unique declarations in §1. Review ends at the stated Owner-review status. The plan neither begins implementation nor authorizes production data, cloud mutation, registry materialization or a strategy switch.

### Master-handoff cross-checks

| Question | Planning conclusion |
|---|---|
| Why slow? | Mandatory security/concurrency/history robustness is real work; missing provider execution and UI composition, inadequate boundary tests, backend-only completeness and repeated equivalent evidence/CI transitions add avoidable delay. No invented duration attribution. |
| What safeguards caught defects? | Independent security/locking review and slice composition caught actual omissions (C E30); retain direct-role RLS/RPC, transactional/resource/scan/cleanup fences and exact-SHA evidence rather than deleting complexity indiscriminately. |
| What process can simplify? | REC-35 same-fact serialization/equivalent obligations only after REC-34 source authority; current targeted re-review economy already useful. |
| Are mandatory features masked? | Yes: backend-only S06 closure did not prove Master/User UI. REC-33 source coverage and REC-27 composition correct that inference without erasing accepted backend work. |
| Which modules are end-to-end usable today? | Frozen evidence does not certify a complete deployed journey; F01 was reproduced and critical provider/SQL proof remains missing. Source-level functional assets are not a claim none work, nor proof UAT is ready. |
| Fastest safe Preview? | The §14 prerequisite join and REC-13 real synthetic multi-persona cohort, not every Phase-1 screen first. |
| Cloud facts before production? | Current target/version/migration/grants/RLS/Auth/Storage/provider/deployment/env/backup parity via REC-06 and fresh REC-32 inventory; no stale-research assumptions. |
| Mandatory external runtimes? | Real scanner, mail delivery, recurring temporary cleanup and actual PDF rendering; bounded hosting choice remains gated, not an obligatory broker/fleet. |
| Can provider/PDF requirements narrow? | No silent narrowing: actual scan/claimed mail before functional cohort; full mail/cleanup/content-correct PDF before Phase1; only official pixels deferred. Any policy change requires Owner-controlled source decision. |
| Before real data? | Complete product plus all REC-28–32 recovery/identity/ops/parity/Legal proof and distinct final O-REALDATA, not deployment alone. |
| First-principles design to retain? | Modular app, distinct durable aggregates/history, managed verified identity plus granular contextual authorization, explicit DB transactions/resource locks, private objects and durable fenced intent. |
| Complexity not to rebuild? | New command/workflow/global-state platforms, distributed topology, redundant evidence authorities and speculative caches/queues without measured need. |
| What leaves the critical path? | §15 exclusions and optional REC-35/36 mechanics; never mandatory security, product truth, scan/mail/cleanup/PDF or recovery. |
| Rewrite verdict? | Accepted Phase-D NO, not reopened. REC-36 cannot authorize full rewrite; new evidence must satisfy the Phase-D structural and total-cost threshold. |

Later execution must remain bounded by current canonical sources and separate Owner authorization. Frozen predecessors are not edited to resolve new disagreements. The only repository deliverable from this phase is this Markdown, committed/pushed to the review-only branch and verified remotely. Local and remote byte hashes belong in the external handoff, not self-referential file content.

PHASE_E_RECOVERY_PLAN_FROZEN: YES
