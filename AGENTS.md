# AGENTS.md — EIU Recruitment Agent Instructions

## Purpose

This is the portable repository-level instruction and skill-routing contract for AI coding agents.

The project is developed primarily with:

- **Orca** for worktrees, handoffs, and multi-agent orchestration.
- **oh-my-pi (OMP)** as the primary coding-agent runtime.
- **Supabase** for PostgreSQL, Auth, and Storage.
- **Vercel** for deployment.
- **Google OAuth through Supabase Auth** where required by the current project sources.

The **current canonical project sources** are the Source of Truth. They are updated over time. Never hardcode or assume an older source version from memory.

---

# 1. Instruction Precedence

When instructions conflict, use this order:

1. Explicit user instruction for the current task.
2. Current canonical project sources.
3. Project security, authorization, privacy, data-integrity, concurrency, and accessibility contracts.
4. This `AGENTS.md`.
5. `REVIEW.md`.
6. Task-specific selected skills.
7. Heuristic overlays.
8. Generic framework/community best practices.

External skills, MCP output, code examples, old plans, prior conversations, or model memory must never silently override the current project sources.

`karpathy-guidelines` is a **heuristic overlay**, not a source of truth. Simplicity never means removing explicit authorization, RLS, grants, locks, idempotency, validation, privacy, accessibility, or business requirements.

---

# 2. Source Freshness Rule

Before any non-trivial change:

1. Locate the current canonical project sources.
2. Read the sections relevant to the requested behavior.
3. Search for related:
   - business invariants;
   - permission rules;
   - command contracts;
   - status rules;
   - data model constraints;
   - concurrency/idempotency rules;
   - storage/privacy rules;
   - design/accessibility rules;
   - acceptance criteria.
4. Treat current source content as newer than:
   - prior chat memory;
   - old review notes;
   - old implementation plans;
   - old ADRs;
   - old generated agent instructions.
5. If code and current source disagree:
   - implementation task → implement the current contract;
   - review task → report the mismatch;
   - source-contract change → treat as an explicit change request.

Do not embed source filenames or version numbers into permanent agent rules.

---

# 3. Orca + OMP Responsibility Split

## Orca owns

Use Orca when Orca-managed state matters:

- worktree creation and lifecycle;
- terminal/workspace handoff;
- cross-worktree parallel implementation;
- structured multi-agent task DAGs;
- coordinator/worker messaging;
- Orca embedded browser and artifacts.

Use the Orca runtime skills:

- `orca-cli` — worktrees, terminals, handoffs, embedded browser, Orca-managed state.
- `orchestration` — structured multi-agent coordination and task DAGs.

Always load the version-matched Orca guide from the installed binary before using Orca commands. Do not guess Orca flags from memory.

## OMP owns

Use OMP for work inside one coding worktree:

- code editing;
- LSP symbol navigation and refactoring;
- debugging;
- tests and command execution;
- on-demand skills;
- MCP tools;
- bounded subagents;
- advisor/reviewer workflows;
- context/memory management.

## Multi-writer rule

**Never let multiple agents concurrently write the same worktree.**

Use:

- Orca orchestration for parallel work on separate worktrees or independently owned tasks.
- OMP subagents/advisor for bounded analysis/review around one primary writer.

If tasks touch the same files, schema objects, migrations, or shared contract, serialize ownership or explicitly coordinate the merge boundary.

---

# 4. OMP-Native Project Layout

The recommended project setup is:

```text
repo/
├─ AGENTS.md
├─ REVIEW.md
├─ SKILLS.md
├─ .agents/
│  └─ skills/
└─ .omp/
   ├─ AGENTS.md
   ├─ RULES.md
   ├─ WATCHDOG.md
   └─ mcp.json
```

Rules:

- `AGENTS.md` at project root is the portable canonical agent instruction file.
- `.omp/AGENTS.md` imports the root file so OMP uses native high-priority discovery without duplicating content.
- `.omp/RULES.md` contains only short sticky hard rules.
- `.omp/WATCHDOG.md` contains advisor-only review guidance.
- `.agents/skills/` is the **single canonical project skill home**.
- Do not duplicate the same skill into `.claude/skills`, `.codex`, `.omp/skills`, and `.agents/skills`.

OMP discovers skills by name and resolves collisions by provider precedence. Duplicate copies create drift and warnings even when one copy wins.

---

# 5. Next.js Version-Matched Documentation

Do **not** install the old `next-best-practices` skill.

Vercel has retired it. Modern Next.js uses version-matched bundled documentation and managed `AGENTS.md` rules.

Before material Next.js framework work:

1. Inspect the installed `next` version.
2. Prefer the documentation that matches the installed framework version.
3. Then use `documentation-lookup` for current external clarification when needed.

## Next.js 16.3+

`next dev` can maintain a managed Next.js rule block inside root `AGENTS.md` that directs agents to:

```text
node_modules/next/dist/docs/
```

Preserve that managed block if Next.js writes it.

Next.js may also generate:

```text
CLAUDE.md
@AGENTS.md
```

This is only a compatibility shim generated by Next.js. Do not manually maintain a separate Claude-specific instruction set. OMP's `.omp/AGENTS.md` remains the native project entry point.

## Next.js 16.2

Bundled docs exist, but automatic agent rules may not. Read:

```text
node_modules/next/dist/docs/
```

before framework-sensitive edits.

## Earlier versions

Use the current official Next.js AI-agent guidance or `documentation-lookup` rather than installing a stale `next-best-practices` copy.

Do not upgrade Next.js merely to gain agent tooling unless the user explicitly requests the framework upgrade.

## Conditional Next workflow skills

Do not install by default:

- `next-dev-loop`
- `next-cache-components-adoption`
- `next-cache-components-optimizer`
- `next-partial-prefetching-adoption`

Only add them if their specific feature and prerequisites are actually used by the current project.

---

# 6. Skill Routing — MANDATORY

Load only skills relevant to the task.

## 6.1 General implementation

For a well-defined implementation task:

1. `implement`
2. task-specific specialist skills
3. focused verification
4. `code-review`
5. `verification-before-completion`

## 6.2 React / TypeScript UI

For material `.ts` / `.tsx`, React components, hooks, forms, client state, or interactive UI:

1. `react-patterns`
2. `vercel-react-best-practices`

Add only when relevant:

- `vercel-composition-patterns` — reusable component API or real composition complexity.
- `accessibility` — interactive forms, tables, dialogs, menus, focus, keyboard, errors.
- `react-testing` — meaningful component/form behavior tests.
- `click-path-audit` — sequential handlers/state updates produce a wrong final UI state.

Do not add abstractions merely because a skill demonstrates them.

## 6.3 Next.js / App Router / Server Boundary

For App Router routes/layouts/pages, Server Components, Client Components, Route Handlers, Server Actions, SSR, cookies, middleware/proxy, metadata, caching, images/fonts/scripts, or framework behavior:

1. read version-matched Next.js docs;
2. `documentation-lookup` when current external documentation is needed;
3. `react-patterns`;
4. `vercel-react-best-practices`.

Treat every mutation-capable Server Action or Route Handler as a public mutation endpoint.

## 6.4 Supabase general work

For **any** Supabase-specific implementation or debugging task:

1. `supabase`

This includes:

- Supabase Auth;
- `@supabase/ssr`;
- Storage;
- Supabase CLI;
- Supabase MCP;
- PostgREST/Data API;
- logs and debugging;
- RLS surprises;
- Supabase-specific configuration.

Use the current Supabase documentation and changelog, not model memory.

## 6.5 PostgreSQL / SQL / RLS / migration

Before writing or modifying anything that lives in PostgreSQL:

1. `supabase-postgres-best-practices`

This includes:

- tables/columns/types;
- constraints;
- indexes;
- migrations;
- RLS policies;
- grants;
- functions/triggers/views;
- transaction design;
- locking/concurrency;
- query plans;
- connection behavior.

Additionally invoke `security-review` when the change touches:

- RLS or grants;
- `SECURITY DEFINER`;
- privileged views/functions;
- service-role usage;
- PII;
- authorization;
- sensitive documents;
- authentication-derived identity.

The official Supabase Postgres skill replaces the older generic `postgres-patterns` skill in this project to avoid duplicate guidance.

## 6.6 Google OAuth / Supabase Auth

For Google OAuth, Supabase sessions, callbacks, cookies, allowlists, identity binding, or login failures:

1. `supabase`
2. `documentation-lookup` when current docs must be fetched
3. `security-review`

Primary technical reference:

`https://supabase.com/docs/guides/auth/social-login/auth-google`

Hard rule:

> Successful Google/Supabase authentication is not application authorization.

After authentication, enforce the current project-defined access predicates server-side.

Never rely only on:

- UI hiding;
- email-domain text checks in the browser;
- Google account selection;
- client-supplied role/permission data.

Keep Google Client Secret and other secrets server-side.

Request only scopes required for the approved feature.

Do not persist Google provider access/refresh tokens unless the project explicitly needs Google APIs beyond authentication.

## 6.7 Files / Storage / private documents

For upload, preview, signed URLs, replacement, deletion, bucket policies, scanning/finalization:

1. `supabase`
2. `security-review`
3. `tdd` when authorization or state transitions are high risk.

Never make private business documents public for convenience.

## 6.8 High-risk business behavior

Use **risk-based TDD** with `tdd` for behavior where a regression can corrupt data or violate authorization, including:

- auth/authorization;
- RLS-sensitive behavior;
- status transitions;
- duplicate prevention;
- sequence/round allocation;
- scheduling/resource conflicts;
- locking/races;
- optimistic concurrency;
- idempotency;
- outcome/report derivation;
- document ownership/visibility;
- destructive actions.

Do not force TDD on trivial copy or styling-only edits.

## 6.9 Debugging

For a reported bug or performance regression:

1. `diagnosing-bugs`;
2. create a tight reproduction/feedback loop;
3. identify the root-cause domain;
4. invoke only the relevant specialist skill;
5. add a regression test at a meaningful public seam when valuable.

Use `click-path-audit` when individual UI handlers appear correct but combined side effects produce the wrong final state.

## 6.10 Architecture decisions

Use `architecture-decision-records` only when a technical decision is durable and materially affects future implementation.

Do not create ADRs for routine code choices.

## 6.11 Context budget

Use `context-budget` when:

- many skills/tools have accumulated;
- duplicate skills may exist;
- agent context feels bloated;
- quality degrades over long sessions.

---

# 7. MCP & Graph Tool Routing (v2.4)

## Context7 MCP

`documentation-lookup` depends on Context7.

Use Context7 for current library/framework/API documentation.

Never send secrets, access tokens, passwords, private CV content, or sensitive PII in documentation queries.

## Supabase MCP

Use Supabase MCP only against a **development/test project** by default.

Project MCP configuration must:
- scope to one project;
- default to `read_only=true`;
- expose only required feature groups;
- contain no committed credentials.

Do not connect an AI coding agent to production Supabase data by default.

Any temporary writable MCP access must:
1. target a non-production project;
2. be explicitly authorized for the task;
3. be removed or returned to read-only afterward.

Database schema changes must still be represented in repository migrations/schema sources. Live MCP mutations are not a substitute for migration history.

## Code Review Graph (CRG 2.3.8) — Broad Discovery & Review Graph

Code Review Graph is the primary tool for broad codebase discovery, unfamiliar feature exploration, and initial PR/diff triage.
- **Scope:** Broad exploration ("Where is candidate approval handled?", "What files participate in workflow?").
- **MCP Tool Allowlist:** Restricted strictly to:
  `get_minimal_context_tool`, `query_graph_tool`, `detect_changes_tool`, `get_review_context_tool`, `get_architecture_overview_tool`, `list_graph_stats_tool`.
- **Query Policy:** `detail_level=minimal`, `include_source=false`, small result limits. Do not fetch source code via graph unless direct reading is insufficient.
- **Operational Policy:** Hooks OFF, watch daemon OFF, auto-rules OFF. Freshness is verified explicitly before use.

## GitNexus (1.6.10) — Precise Code Relationship Graph

GitNexus is the primary code graph engine for precise symbol, import, caller/callee, and change blast-radius analysis.
- **Scope:** Precise questions ("What calls this?", "What does this call?", "What is the exact blast radius of changing this interface?").
- **Configuration:** Pinned to `gitnexus@1.6.10`, pure index mode `indexOnly: true`.
- **Standard & On-Demand Skills:** Available on-demand under `.agents/skills/`.

## Graphify — DORMANT / Future Optional Tool

Graphify is NOT baseline active (`DORMANT`, `FUTURE_OPTIONAL_DISCOVERY_TOOL`).
- Binary retained in isolated virtual environment to avoid destructive churn.
- No baseline graph built (`GRAPHIFY_GRAPH = NOT_BUILT`).
- No MCP configured, no hooks, no agent rules, live PostgreSQL introspection disabled.

## Code Intelligence Routing & Escalation Model

```text
LOCALIZED / KNOWN WORK (single file, known symbol, small fix)
    -> DIRECT SOURCE + LSP (NO graph required)

BROAD / UNFAMILIAR PROBLEM
    -> Code Review Graph (CRG) minimal context
    -> candidate files / symbols
    -> direct source
    -> GitNexus (ONLY if exact caller/callee or blast radius is needed)

SHARED SYMBOL / CONTRACT CHANGE
    -> GitNexus precise impact analysis (after freshness gate)
    -> direct callers / source verification

PR / DIFF REVIEW
    -> direct git diff & source
    -> CRG diff triage (identify risk zones)
    -> GitNexus impact selectively for high-risk symbols
    -> direct source / tests verification
    -> eiu-code-review verdict
```

Do NOT call both graph systems for the same broad discovery question without a concrete reason.

## Mandatory Graph Freshness Contract

A graph query is invalid as task evidence until freshness has been established for the current working tree:
1. **CRG Freshness Gate:** Before first query, inspect working tree and CRG status (`code-review-graph status`). If stale, run `code-review-graph update` (or `build`).
2. **GitNexus Freshness Gate:** Before first query, verify index freshness (`gitnexus status`). If stale, refresh index (`gitnexus analyze --skip-git --index-only`).
3. **Stale Fallback:** If freshness cannot be established, graph evidence is UNAVAILABLE; fall back to direct source, LSP, and search. Never use stale graph evidence.
4. **Post-Change Invalidation:** Once implementation materially modifies source, all prior graph conclusions are STALE until refreshed if reused.

## Graph Authority Policy — Mandatory Hierarchy

Graph tools (CRG, GitNexus, Graphify) are discovery and evidence systems. They are **NEVER** repository or database definition authority.

Mandatory hierarchy:
```text
DIRECT SOURCE / LSP
        >
declarative schema + ordered migrations for DB behavior
        >
GitNexus / CRG discovery evidence
```

A graph result must never by itself justify:
- business behavior
- authorization behavior
- RLS behavior
- SQL effective definition
- trigger execution semantics
- RPC behavior
- database migration order
- security decision

Always cross-check graph findings against actual source files.

## Database Source-of-Truth Contract

For Supabase / PostgreSQL, repository authority explicitly distinguishes:
```text
DISCOVERY VIEW  vs  EFFECTIVE DEFINITION
```
- **Discovery View:** May use grep/search, LSP, CRG, GitNexus, and Supabase read-only inspection.
- **Effective Definition:** Must be reconstructed strictly from:
  `declarative schema + ordered migration chain + direct function/policy/trigger SQL + applicable tests`

Remote read-only introspection in dev provides deployed evidence, not repository authority.

## SQL Absence Rule

**NEVER** conclude:
```text
"function/trigger/policy/RPC does not exist"
```
solely because CRG or GitNexus does not return it.

Before concluding absence, inspect:
1. declarative schema;
2. all ordered migrations;
3. SQL/functions directory if present;
4. RPC definitions;
5. RLS policies;
6. triggers;
7. relevant Supabase configuration.

## App -> Supabase Cross-Layer Rule

For cross-layer flows:
```text
React component -> server action/API -> Supabase RPC -> SQL function -> table/RLS/trigger
```
CRG may narrow context and GitNexus may trace symbol relationships, but every critical boundary must be directly verified:
1. app caller
2. API/server implementation
3. Supabase client call
4. RPC/function identifier
5. actual SQL definition
6. RLS/policy dependencies
7. trigger dependencies if applicable
8. migration ordering

No inferred cross-layer graph edge is sufficient alone.

---

# 8. Semantic Reuse / Deduplication Rule

Do not add a separate `code-deduplication` skill unless a trusted maintained source is later selected.

Before adding reusable:

- hooks;
- components;
- validators;
- mappers;
- formatters;
- services;
- helpers;
- shared types;
- utility functions;

search existing code first using:

1. GitNexus query/context/impact;
2. OMP LSP/symbol search;
3. focused grep/search.

Reuse an existing implementation when it already expresses the same behavior and using it does not violate locality or the current source contract.

Do not force deduplication when two pieces of code only look syntactically similar but have different business semantics.

---

# 9. OMP Advisor and Independent Review

OMP already provides reviewer infrastructure. Do not add the sample repository's Claude-specific `post_implementation_reviewer`.

## Advisor

`.omp/WATCHDOG.md` supplies reviewer priorities without bloating the primary executor context.

Recommended use:

- enable advisor for high-risk auth/RLS/concurrency/migration/privacy work;
- keep advisor investigative/read-only by default;
- do not grant mutating advisor tools unless explicitly needed.

Advisor output is advice, not source authority.

## OMP `/review`

Use OMP's independent review for:

- large/high-risk diffs;
- pre-merge security/data changes;
- final review after a major implementation slice.

It supplements, not replaces, `code-review`.

Suggested review stack for high-risk changes:

```text
code-review
-> OMP independent /review
-> ponytail-review if complexity increased
-> verification-before-completion
```

Do not run multiple heavyweight reviewers for trivial changes.

---

# 10. React Doctor

Use React Doctor as a **tool/quality gate**, not as another always-loaded skill.

For meaningful React/Next.js diffs:

```bash
npx react-doctor@latest --verbose --scope changed
```

Use the current CLI syntax. Do not copy old sample-repo commands blindly.

React Doctor is supplementary static/runtime-oriented analysis. Its findings do not override the project's current design/business source.

Do not auto-fix large sets of findings without reviewing scope and source conformance.

---

# 11. Database Mutation Discipline

For high-risk mutations, preserve the current authoritative transactional command model.

Reject implementation patterns that:

- validate mutable state then write later without required locks/rechecks;
- split an atomic business command across browser-orchestrated writes;
- allow stale whole-row writes to overwrite newer data;
- bypass required idempotency;
- compute sequences without required locking;
- weaken RLS/grants to solve permission errors;
- put service-role credentials in browser code;
- assume a server boundary alone replaces authorization;
- call external providers inside a DB transaction when the current project contract requires after-commit/outbox behavior.

Lock ordering must be deterministic where multiple resources are involved.

---

# 12. Server Boundary Discipline

Conceptual mutation order:

```text
authenticate
-> authorize
-> validate
-> invoke approved transactional command/RPC
-> return stable result/error
```

UI visibility and disabled controls are UX only, never authorization.

Derive security-sensitive caller identity/permissions server-side.

---

# 13. UI / Accessibility Discipline

The current canonical design source is authoritative.

Preserve at minimum:

- semantic HTML;
- proper labels and accessible names;
- keyboard operation;
- visible focus;
- accessible validation/error association;
- status meaning not conveyed by color alone;
- correct operational table semantics;
- responsive behavior required by the project;
- readable/reflowable business text;
- reduced-motion handling where motion exists.

Use `frontend-checklist-global` for major UI/pre-release audit, not as permission to redesign the product.

Use `browser-qa` against preview/staging for required user journeys.

---

# 14. Vercel

For deployment:

- use `deploy-to-vercel`;
- prefer preview deployment before production.

For deployed performance/reliability/cost:

- use `vercel-optimize`.

Do not deploy to production without explicit authorization or a repository workflow that clearly authorizes it.

Do not put secrets into Vercel-visible client environment variables.

---

# 15. Minimal-Diff Rule

Every changed line should trace to:

- the requested task;
- a necessary consequence of that task;
- a required test/verification adjustment.

Do not bundle unrelated:

- refactors;
- formatting rewrites;
- dependency upgrades;
- cleanup;
- architecture changes.

Report unrelated issues separately.

---

# 16. Verification Before Completion

No claim such as `done`, `fixed`, `pass`, or `ready` without fresh evidence.

Before completion:

1. identify checks that prove the claim;
2. run them fresh;
3. inspect exit status and actual failures;
4. run focused tests for changed behavior;
5. run broader checks appropriate to the change;
6. run React Doctor for meaningful React/Next diffs;
7. run RLS/concurrency/auth tests when applicable;
8. review final diff for scope creep;
9. run `verification-before-completion`;
10. only then state the result.

A green typecheck/build does not prove authorization, race safety, accessibility, or business correctness.

---

# 17. Git / Deployment Safety

Unless explicitly authorized by the user or an existing repository workflow:

- do not commit;
- do not push;
- do not merge;
- do not production-deploy;
- do not apply destructive live migrations;
- do not delete production data;
- do not rotate credentials;
- do not change Google/Supabase/Vercel production settings.

Never use `--no-verify` to bypass repository hooks without explicit authorization.

---

# 18. Completion Handoff

For non-trivial work report:

- scope implemented;
- current source contract followed;
- files materially changed;
- specialist skills/tools used;
- tests/checks executed and results;
- unresolved risks/follow-up;
- Git/worktree state;
- deployment state if applicable.

Do not promise background/future work.
