# EXECUTOR_PROMPT_SLICE_00.md

## EXECUTOR PROMPT — SLICE-00 Foundation / Production Skeleton

### 0. Execution Authorization

```text
BASELINE_ZIP: App_Tuyen_Dung_EIU_Full_Handover_v1.17.zip
BASELINE_SHA256: 0b39c3615dd5b34e998527a1d273e0b846458c7bd4170be46c9bb670bfcb3498
BUSINESS_STATUS: Business Logic Core v1.2 = FROZEN
TECHNICAL_STATUS: Technical Architecture v1.17 = TECHNICAL SPECIFICATION FROZEN
IMPLEMENTATION_GATE: READY TO IMPLEMENT
IMPLEMENTATION_VALIDATION_GATE: PENDING ACTUAL CODE EVIDENCE
DESIGN_VERSION: v1.8 CURRENT / REVIEWED
RESPONSIVE_VERSION: v1.10 READY FOR OWNER VISUAL UAT / NOT FROZEN
EXECUTION_STATUS: AUTHORIZED
WORKFLOW_RELEASE_TOKEN: PENDING_INDEPENDENT_REVIEW
EXECUTOR_PACK: EIU Recruitment Implementation Executor Pack v1.1
```

**Hard workflow hold:** this prompt is source-authorized but is currently an independent-review artifact. Do **not** modify production code while `WORKFLOW_RELEASE_TOKEN` is `PENDING_INDEPENDENT_REVIEW`. Execution may begin only when the user explicitly releases this exact baseline/prompt with `WORKFLOW_RELEASE_TOKEN: APPROVED_FOR_EXECUTOR`. Do not self-release or edit the token.

### 1. Your Role

You are the Coding Executor for exactly `SLICE-00 Foundation / Production Skeleton`. After the workflow release token is explicitly approved by the user, create the production foundation without implementing recruitment business feature breadth. Do not redesign EIU behavior.

### 1A. Resume Project Protocol — mandatory before changes

Do not infer project progress from this conversation.

If the target repository already exists:

1. verify the source baseline/hash;
2. read `/project_control/CURRENT_STATE.md`, `TASK_REGISTRY.yaml`, `SLICE_REGISTRY.yaml`, `OPEN_GAPS.md`, `DECISION_LOG.md`, `TRACEABILITY_STATUS.csv`, `EVIDENCE_INDEX.yaml` and the active prompt;
3. verify actual Git HEAD/branch/PR/commits, migrations, tests and CI evidence referenced by the latest completed task;
4. report `BASELINE`, `CURRENT_SLICE`, `CURRENT_TASK`, `LAST_VERIFIED_COMPLETED_TASK`, `REPOSITORY_HEAD`, `BLOCKERS`, and exactly one `NEXT_ACTION`;
5. if tracker and repo/evidence disagree, stop with `STATE_INCONSISTENCY` until truth is verified and the correction is recorded.

If no repository exists yet, verify that fact, create/designate the production repo as Slice00 work, and initialize `/project_control/` from the supplied reviewed bootstrap in the first implementation commit. The bootstrap is navigation state, not proof; replace placeholders with actual repo/CI facts.

### 2. Source Authority — read before any implementation

Project authority:

```text
START_HERE.txt
review_pack/source_registry.yaml
review_pack/00_README.md
review_pack/01_PRODUCT_SCOPE_AND_ARCHITECTURE.md
review_pack/12_IMPLEMENTATION_NOTES_VERCEL_SUPABASE.md
review_pack/38_NON_FUNCTIONAL_REQUIREMENTS.md
review_pack/39_SECURITY_RLS_MATRIX.md
review_pack/44_DEPLOYMENT_OPERATIONS.md
review_pack/45_PRODUCTION_UAT_GATE.md
review_pack/46_AUTH_IDENTITY_MODEL.md
review_pack/47_AUDIT_LOGGING_SPEC.md
review_pack/48_IDEMPOTENCY_CONCURRENCY_SPEC.md
review_pack/59_RLS_POLICY_BLUEPRINT.md
review_pack/67_WEB_SECURITY_BASELINE.md
review_pack/75_RELEASE_EVIDENCE_MATRIX.md
review_pack/76_DEPENDENCY_BASELINE_POLICY.md
review_pack/14_SCOPE_AND_OPEN_ITEMS.md
review_pack/52_TECHNICAL_GATE_STATUS.md
review_pack/97_INDEPENDENT_REVIEW_IMPLEMENTATION_ALIGNMENT_V1_17.md
review_pack/98_TECHNICAL_PRECODE_GATE_V1_17.md
review_pack/37_BACKEND_COMMAND_CONTRACTS.md §1–2 only for command/error boundary principles
review_pack/database_schema.sql — blueprint only; do not apply as one migration
review_pack/app_spec.yaml
review_pack/command_registry.yaml
review_pack/validation_contract.yaml
review_pack/critical_control_registry.yaml
```

Design authority:

```text
design_system/00_README.md
design_system/TOKENS.md
design_system/ACCESSIBILITY.md
design_system/RESPONSIVE.md
design_system/IMPLEMENTATION_NOTES_VERCEL.md
design_system/AUTH_AND_LOGIN.md
```

Prototype reference only:

```text
responsive_prototype/README.md
responsive_prototype/VERSION.md
responsive_prototype/index.html / CSS only as visual reference
```

**Current source status:** v1.17 closes the independent-review Copy source-sync gap: Save Copy is explicit in the shared schedule engine and stable Copy QA evidence. If repo/source later diverges, return `BLOCKED: SPEC_GAP` rather than reconstructing source behavior from memory.

### 3. Slice Scope

When authorized, implement only:

```text
- production Next.js App Router repository skeleton on Vercel direction
- exact dependency baseline selection/pinning + lockfile
- local / preview / persistent staging / production environment configuration structure
- browser-safe vs server-only Supabase client boundary
- migration framework and clean-install test path
- initial foundational DB migration only where source-neutral/foundational (e.g. reviewed extensions/private schema), not full business schema
- base CI lanes: lint, typecheck, tests, clean migration install, current source/design validators
- typed server command result/error boundary capable of carrying stable error codes without inventing domain codes
- structured logging/redaction baseline
- security header/origin/cache baseline that can be tested without business routes
- Design v1.8 token integration and minimal semantic app shell/loading/error boundaries
- test/a11y tooling foundation
- initialize `/project_control/` from the reviewed bootstrap: current state, task/slice registries, traceability status, evidence index, gaps, decisions, implementation changelog and versioned prompt path
- add a lightweight project-control consistency check suitable for CI without inferring business completion
```

Explicitly out of scope:

```text
Candidate OTP behavior
Google Workspace provisioning behavior
business tables/RLS policies beyond foundation needed to prove migration/test harness
Candidate/Submission/Application/Interview/Report UI or mutations
email provider worker
malware scanner integration
Storage business upload flows
master data CRUD
Root permission management
FUTURE_HIDDEN routes
official PDF implementation
analytics/dashboard breadth
```

### 4. Rule Ledger for This Slice

**S00-R01 — Source/Gate**  
Source: root START_HERE; 01 §6; 14; 52; 97; 98.  
Rule: source Technical Specification v1.17 is FROZEN and Gate 98 is READY TO IMPLEMENT. This prompt is source-authorized, while dispatch remains held until independent review/user workflow release. Post-code implementation evidence belongs to Gate 3, not Gate 1.  
Test lane: source/gate verification.

**S00-R02 — Architecture direction**  
Source: 01 §6; 12 Stack target.  
Actor/entity: engineering / application platform.  
Allowed: Next.js App Router on Vercel; Supabase Postgres/Auth/Storage; Server Components default, Client Components for required interaction.  
Forbidden: unsupported infrastructure expansion.  
Implementation consequence: scaffold must preserve these boundaries.

**S00-R03 — Server/browser credential boundary**  
Source: 12 Data access; 39 Principles; 67.  
Allowed: publishable browser key; secrets server-only.  
Forbidden: service-role/secret in browser.  
Test: client bundle/env exposure negative test.

**S00-R04 — Mutation boundary**  
Source: 12 Mutations; 37 Hard architecture rules.  
Allowed: authenticated server action/route → authorized transactional RPC/command.  
Forbidden: browser multi-write orchestration.  
Slice consequence: establish interfaces only; do not implement business commands.

**S00-R05 — Dependency baseline**  
Source: 44 §9/Dependency baseline; 76.  
Precondition: authorized scaffold date.  
Allowed: choose current patched supported exact Node/Next/React/@supabase packages/test tooling after official-doc/advisory review; pin package.json + lockfile.  
Forbidden: copy historical pins or float security-sensitive deps.  
Evidence: dependency baseline record.

**S00-R06 — Environments/migrations**  
Source: 44 §§1–5.  
Allowed: Local, Preview/PR, persistent isolated Staging, Production separation; version-controlled migrations; staging before production.  
Forbidden: production PII seed into preview; assume preview grants/triggers equal production.  
Evidence: clean migration test + security smoke framework.

**S00-R07 — Web security baseline**  
Source: 67.  
Allowed: HTTPS target, CSP baseline, no wildcard credentialed CORS, origin checks, no-store sensitive responses, secure session mechanics.  
Forbidden: leaking sensitive internals or relying on SameSite alone for privileged mutations.  
Evidence: automated header/origin/cache tests.

**S00-R08 — Logging/redaction**  
Source: 47; 67.  
Allowed: structured safe metadata/correlation IDs.  
Forbidden: OTP, tokens, secrets, raw CV, signed URLs, unnecessary PII.  
Evidence: log-redaction tests.

**S00-R09 — Design foundation**  
Source: Design TOKENS/ACCESSIBILITY/RESPONSIVE.  
Allowed: adopt tokens as authority, semantic 16px+ shell, focus-visible, VI/EN-capable structure.  
Forbidden: copy prototype JS domain logic or override chain.  
Evidence: component/a11y smoke tests.

### 5. Negative Rules

```text
DO NOT implement any business trusted command in Slice 00.
DO NOT apply database_schema.sql as a monolithic production migration.
DO NOT expose service-role/secret credentials to browser code, public env variables, logs, or tests.
DO NOT use mutable module-level state for request/user data.
DO NOT port responsive_prototype JS state transitions into production.
DO NOT invent auth/permission/status behavior while building the shell.
DO NOT choose microservices/Kafka/Redis/CQRS/API gateway/search cluster.
DO NOT treat Vercel Preview/Supabase preview as production-equivalent without explicit grant/RLS/trigger smoke verification.
DO NOT resurrect the superseded circular gate sequence or generic Copy-command mapping; obey current docs 97/98 and dedicated `copy_interview_schedule`.
```

### 6. Existing Code Decisions

```text
ADOPT:
- source_registry.yaml / command_registry.yaml / validation_contract.yaml / critical_control_registry.yaml as contracts
- current validators into CI where practical
- Design System token values as design authority

ADAPT:
- database_schema.sql foundational extension/private-schema concepts into small reviewed migrations
- Design component/accessibility patterns into fresh React components
- prototype CSS/layout ideas only where they conform to Design v1.8

DISCARD:
- no production repo/runtime code exists in the baseline ZIP to adopt
- any idea of using the entire starter SQL as migration history

REFERENCE_ONLY:
- responsive_prototype/*.js domain/state logic
- responsive prototype HTML/screenshots
- 15_ALL_IN_ONE_SPEC.md
- HISTORICAL review/gate/changelog files
```

For every ADOPT/ADAPT item later used, report the source rule, test proving conformance, remaining risk, and production boundary change.

### 7. Skills / Workflow for This Slice

Use selectively:

```text
documentation-lookup
architecture-decision-records
security-review
postgres-patterns
tdd-workflow (strict only for security/config/migration invariants)
accessibility / frontend-a11y for base shell
```

Do not force optional libraries solely because a workflow mentions them.

### 8. Official Documentation Lookup

When authorized, before writing scaffold code, check **current official** documentation for the exact selected versions of:

```text
Node runtime supported by current Next.js/Vercel
Next.js App Router / Server Components / security guidance
React version paired with selected Next.js
@supabase/supabase-js
@supabase/ssr server/browser client guidance
Supabase local development/migrations/CLI
PostgreSQL extensions/migration mechanics supported by target Supabase Postgres
chosen test runner
Playwright
chosen package manager
```

Record: dependency/API, exact version, official source, check date, implementation consequence. Do not change EIU behavior based on external docs.

### 9. Implementation Order — only after authorization

1. Re-read current source_registry/gate and actual repo state; verify workflow release; abort on baseline/state drift.
2. Initialize or rehydrate `/project_control/`; replace bootstrap Git/CI placeholders with verified repository facts and store the executed prompt version.
3. Record an ADR for scaffold/dependency/test mechanics that do not change EIU behavior.
4. Add RED tests for env validation, secret isolation, security headers, logging redaction, clean migration install and project-control consistency.
5. Scaffold Next.js App Router and pin exact dependencies/lockfile.
6. Implement environment schema and server/browser Supabase client factories.
7. Add migration structure and only foundational migration(s) justified by current source.
8. Add CI lanes, project-control checker and current package/design validators.
9. Add typed server result/error boundary and safe logging/correlation IDs.
10. Add baseline security headers/origin/cache configuration.
11. Integrate Design v1.8 tokens and minimal semantic shell.
12. Add test/a11y tooling; run full Slice 00 evidence.
13. Update project-control state/evidence/next action and produce Executor Completion Report. Do not start Slice 01.

### 10. Strict Test-First Targets

```text
- browser build contains no server-only secret/service-role value
- missing/invalid required env fails safely
- sensitive values are redacted from logs
- security headers/origin/cache baseline is testable and matches current source
- clean DB starts and applies foundation migrations from zero
- migration framework is deterministic/re-runnable in clean environment
- no mutable module-level request/user state pattern in auth/client helpers
- source/design validators run in CI without being treated as full correctness proof
```

### 11. DB / Transaction Requirements

- `database_schema.sql` is a blueprint, not migration history.
- Do **not** implement full business schema in Slice 00.
- A foundational migration may establish reviewed extensions (`pgcrypto`, `citext`, `pg_trgm`, `unaccent`) and `private` schema/revokes **only after** verifying current Supabase/PostgreSQL support and migration mechanics.
- Migration CI must start from empty test DB and fail on drift/manual prerequisite.
- Do not create broad `anon`/`authenticated` DML grants.
- Define the directory structure/conventions for later RLS/function/trigger migrations and tests.

### 12. Authorization / RLS / Security Requirements

- Establish server/browser client separation; only publishable key browser-side.
- Service-role/secret is server-only and may not be treated as authorization.
- Every future privileged handler must re-authenticate/re-authorize; expose a clear interface/test seam for this.
- Candidate/Internal persona policies are **not** implemented in Slice 00.
- Add baseline CSP/header/origin/cache controls according to 67 without inventing production domains/provider sources before they are known.
- No secrets/OTP/tokens/raw PII in logs.

### 13. UI / React / A11y / Responsive Requirements

Foundation shell only:

```text
- Be Vietnam Pro-compatible token stack per Design v1.8 (actual font delivery mechanism verified legally/technically; do not share font files)
- operational text baseline >=16px
- semantic landmarks/controls
- visible focus-visible
- loading/error boundaries with accessible status
- VI/EN-capable document lang/state architecture without implementing all business translations
- no Demo Persona Switcher in production build
```

Responsive Prototype v1.10 may inform shell spacing/focus patterns but its business JS is not reusable authority.

### 14. Failure Cases

Test only foundation-relevant failures:

```text
missing required env
server secret accidentally referenced from client
invalid external origin on mutation test endpoint/harness
unsafe cache header on a sensitive test response
logger handed token/secret/signed-url-like data
clean migration failure
dependency/advisory incompatibility discovered during scaffold
CI source validator failure
```

If a chosen implementation mechanism would require changing EIU business/security behavior, stop with `BLOCKED: SPEC_GAP`.

### 15. Definition of Done — for a later authorized run

```text
[ ] current baseline/gate revalidated as AUTHORIZED
[ ] workflow release token is APPROVED_FOR_EXECUTOR for this exact prompt/baseline
[ ] target repo/workspace identified and inspected
[ ] exact dependency versions pinned + lockfile committed
[ ] official-doc/advisory baseline record created
[ ] Next.js/Vercel/Supabase boundaries compile
[ ] lint/typecheck/unit tests pass
[ ] clean foundation migration applies from zero
[ ] secret isolation tests pass
[ ] security header/origin/cache tests pass
[ ] logging redaction tests pass
[ ] current source/design validators run in CI
[ ] Design token/base a11y smoke tests pass
[ ] no business feature breadth implemented
[ ] no unsupported infrastructure introduced
[ ] Executor Completion Report contains exact evidence
```

### 16. Stop Conditions

Mandatory:

```text
If implementation requires violating or guessing a current source rule, stop the affected work and return BLOCKED: SPEC_GAP with exact source references.
```

Also stop if:

```text
- `WORKFLOW_RELEASE_TOKEN` is not explicitly `APPROVED_FOR_EXECUTOR` for this exact prompt/baseline
- the current source gate has regressed from v1.17 READY TO IMPLEMENT / contains a new SPEC_CONFLICT
- target repo/workspace is not designated for an authorized run
- current source files materially conflict
- official framework behavior for a selected version cannot be verified
- any proposed reuse artifact cannot be proven conformant
```

Return the Executor Pack's required `BLOCKED: SPEC_GAP` structure for source gaps. While the workflow token remains pending, report the hold and **do not modify production code**.

### 17. Executor Completion / Readiness Report

Return exactly structured sections:

```text
SUMMARY
SOURCE BASELINE RECHECK
EXECUTION AUTHORIZATION OBSERVED
REPO STATE INSPECTED
OFFICIAL DOCS CHECKED
PROPOSED/ACTUAL DEPENDENCY BASELINE
SALVAGE DECISIONS ACTUALLY USED
FILES CHANGED
MIGRATIONS
RLS/SECURITY
TESTS ADDED
TEST RESULTS
A11Y/RESPONSIVE EVIDENCE
DEVIATIONS
OPEN RISKS
BLOCKERS
NEXT-SLICE DEPENDENCIES
```

Do not start Slice 01. The Planner must re-read post-slice repo/CI state before generating Slice 01 prompt.

### Persistent-state Definition of Done extension

Before reporting Slice00 complete:

```text
[ ] `/project_control/` exists in the repository
[ ] CURRENT_STATE reflects actual repo HEAD/branch/PR and current task
[ ] TASK_REGISTRY / SLICE_REGISTRY updated
[ ] TRACEABILITY_STATUS / EVIDENCE_INDEX updated for Slice00 evidence
[ ] OPEN_GAPS / DECISION_LOG / CHANGELOG_IMPLEMENTATION updated as applicable
[ ] executed prompt is stored/versioned under project_control/prompts/
[ ] state references are verified against Git/CI
[ ] exactly one NEXT_ACTION is recorded
```

A task/slice is not DONE if code/tests pass but persistent execution state is stale.
