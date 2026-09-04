## Approved v2.4 Tool & Authority Hierarchy

```text
DIRECT_SOURCE_LSP
  = DEFAULT_LOCAL_IMPLEMENTATION_PATH (Primary implementation evidence)

CODE_REVIEW_GRAPH
  = BROAD_DISCOVERY_AND_REVIEW_GRAPH (Broad discovery, diff triage, context)

GITNEXUS
  = PRECISE_CODE_RELATIONSHIP_GRAPH (Caller/callee, blast radius, symbol tracing)

DATABASE_AUTHORITY
  = DECLARATIVE_SCHEMA + ORDERED_MIGRATIONS + DIRECT_SQL + TESTS

GRAPHIFY
  = FUTURE_OPTIONAL_DISCOVERY_TOOL (Dormant, not baseline active)
```

## Skill Topology Overview

- **Project Specialists (13):** `documentation-lookup`, `react-patterns`, `security-review`, `accessibility`, `react-testing`, `browser-qa`, `architecture-decision-records`, `click-path-audit`, `supabase`, `supabase-postgres-best-practices`, `tdd`, `diagnosing-bugs`, `ponytail-review`.
- **Release-Only (2):** `deploy-to-vercel`, `vercel-optimize`.
- **GitNexus On-Demand (8):** `gitnexus-exploring`, `gitnexus-impact-analysis`, `gitnexus-debugging`, `gitnexus-refactoring`, `gitnexus-guide`, `gitnexus-cli`, `gitnexus-pdg-query`, `gitnexus-taint-analysis`.
- **EIU Native (1):** `.omp/skills/eiu-code-review`.
- **Global Reuse (3):** `vercel-react-best-practices`, `vercel-composition-patterns`, `verification-before-completion` (native p100 copies in `~/.omp/agent/skills/`).
- **Deliberately Excluded (5):** `implement`, `code-review`, `context-budget`, `frontend-checklist-global`, `karpathy-guidelines` (removed from project provider to prevent workflow conflicts).



# SKILLS.md — EIU Recruitment Skill & Tool Inventory

## Purpose

This file defines the approved project skill set for **Orca + OMP**.

Skills are capabilities, not source authority.

`AGENTS.md` defines when each skill is used.

---

# 1. Canonical Skill Location

Use one project skill home:

```text
.agents/skills/<skill-name>/SKILL.md
```

Why:

- OMP discovers `.agents/skills`.
- Orca can work with Agent Skills / OMP skill homes.
- It is portable across agent runtimes.
- It avoids maintaining duplicate `.claude/skills`, `.omp/skills`, and `.agents/skills` copies.

Every installed skill must have:

```yaml
---
name: ...
description: ...
---
```

Keep references/scripts/assets inside the same skill directory.

Do not install multiple active copies of the same `name:`.

---

# 2. Project Skills — 23 Selected

## `affaan-m/ECC` — selective

| Skill | Priority | Use |
|---|---:|---|
| `documentation-lookup` | ★★★★★ | Current library/framework docs through Context7 |
| `react-patterns` | ★★★★★ | React / App Router implementation patterns |
| `security-review` | ★★★★★ | Auth/authz, PII, uploads, secrets, APIs |
| `accessibility` | ★★★★★ | WCAG 2.2 AA |
| `react-testing` | ★★★★★ | React/component/form testing |
| `browser-qa` | ★★★★★ | Preview/staging UI journeys |
| `architecture-decision-records` | ★★★★☆ | Durable technical decisions |
| `click-path-audit` | ★★★★☆ | Sequential UI state/side-effect analysis |

### Removed from previous list
`postgres-patterns` is **not installed** (Supabase Postgres skill used instead).
`context-budget` is **not installed** (superseded by Token Efficiency Policy).
It is replaced by Supabase's official `supabase-postgres-best-practices` to avoid duplicate PostgreSQL/RLS/concurrency guidance.

---

## `supabase/agent-skills` — install both official skills

| Skill | Priority | Use |
|---|---:|---|
| `supabase` | ★★★★★ | Supabase Auth/SSR/Storage/CLI/MCP/debugging |
| `supabase-postgres-best-practices` | ★★★★★ | SQL/schema/RLS/index/locking/concurrency/performance |

These are maintained by Supabase and are the primary Supabase/Postgres specialist skills.

---

## `mattpocock/skills` — selective

| Skill | Priority | Use |
|---|---:|---|
| `tdd` | ★★★★★ | Risk-based TDD for critical behavior |
| `diagnosing-bugs` | ★★★★★ | Root-cause debugging |

`implement` and `code-review` are **deliberately not installed**:
- implementation is performed by OMP task Executor + applicable specialist skills;
- review is performed by independent implementation Reviewer (`eiu-code-review` where applicable).
Do not install discovery/domain-modeling/spec-reopening workflows by default.

---

## `vercel-labs/agent-skills` — selective

| Skill | Priority | Use |
|---|---:|---|
| `vercel-react-best-practices` | ★★★★★ | React/Next performance |
| `vercel-composition-patterns` | ★★★★☆ | Component composition |
| `deploy-to-vercel` | ★★★★★ | Vercel deployment |
| `vercel-optimize` | ★★★★☆ | Deployed Vercel performance/reliability/cost |

---

## `DietrichGebert/ponytail` — selective

| Skill | Priority | Use |
|---|---:|---|
| `ponytail-review` | ★★★★☆ | Over-engineering review |

---

## `obra/superpowers` — selective

| Skill | Priority | Use |
|---|---:|---|
| `verification-before-completion` | ★★★★★ | Fresh verification evidence before completion |

---

## `thedaviddias/Front-End-Checklist` — selective

`frontend-checklist-global` is **deliberately not installed** (superseded by `web-design-guidelines` and Design Review Checklist).
---

## `multica-ai/andrej-karpathy-skills`

`karpathy-guidelines` is **deliberately not installed** (heuristic overlay preserved in core engineering principles without external skill dependency).
Do not copy its root `CLAUDE.md` into this project.

---

# 3. Skill Count

```text
ECC                                  9
Supabase official                    2
Matt Pocock                          4
Vercel Labs                          4
Ponytail                             1
Superpowers                          1
Front-End Checklist                  1
Karpathy                             1
--------------------------------------
TOTAL PROJECT SKILLS                23
```

GitNexus skills and Orca runtime skills are managed separately and are not included in the 23.

---

# 4. Next.js — No `next-best-practices` Skill

Do **not** install `next-best-practices`.

Vercel moved/retired that skill. Next.js now delivers best-practice/reference knowledge through version-matched bundled docs and managed agent rules.

Current official approach:

- Next.js 16.3+:
  - `next dev` can maintain an `AGENTS.md` managed block.
  - docs live in `node_modules/next/dist/docs/`.
- Next.js 16.2:
  - bundled docs are available but agent rule generation differs.
- earlier versions:
  - follow the current official AI-agent guide / codemod as appropriate.

Reference:
`https://nextjs.org/docs/app/guides/ai-agents`

## Conditional Next workflow skills — not initial install

Available from current `vercel/next.js` only when needed:

- `next-dev-loop`
- `next-cache-components-adoption`
- `next-cache-components-optimizer`
- `next-partial-prefetching-adoption`

Do not install unless the current project actually uses their required feature/version/runtime.

---

# 5. Orca Runtime Skills — Do Not Vendor-Copy

Orca ships/version-matches its own operating skills.

Required runtime capabilities:

| Orca skill | Priority | Use |
|---|---:|---|
| `orca-cli` | ★★★★★ | Orca worktrees, terminals, handoffs, embedded browser |
| `orchestration` | ★★★★☆ | Multi-agent DAG/coordinator workflows |

Do not copy these from GitHub into `.agents/skills` as static project copies.

Use the installed Orca binary's version-matched guide, e.g. the current binary's:

```text
ORCA skills get orca-cli
ORCA skills get orchestration
```

where `ORCA` means the correct executable resolved by the Orca skill/runtime.

## Orca skills not needed initially

- `computer-use` — only if external OS/window UI automation is actually needed.
- `orca-linear` — only if Linear becomes a workflow dependency.
- `orca-emulator`
- `orca-emulator-android`
- `orca-per-workspace-env` — only if disposable per-workspace VM/cloud environments are later adopted.

---

# 6. GitNexus — PRIMARY Code Graph Engine + Controlled Skills

Repository:

`abhigyanpatwari/GitNexus` (pinned version: `1.6.10`, `indexOnly: true`)

GitNexus is the primary code graph engine for TypeScript/React symbols, call hierarchies, and change blast radius.

Keep these 6 standard GitNexus skills installed into `.agents/skills`:
- `gitnexus-exploring`
- `gitnexus-impact-analysis`
- `gitnexus-debugging`
- `gitnexus-refactoring`
- `gitnexus-guide`
- `gitnexus-cli`

# 7. Graphify — OPTIONAL Architecture & Semantic Discovery Tool

Repository:

`https://github.com/Graphify-Labs/graphify` (version: `0.9.47`, PyPI `graphifyy[sql]==0.9.47`, commit `b14b52e94ec3d9840413d81777f4c134eac0a40d`)

Category: `OPTIONAL_DISCOVERY_TOOL`

- On-demand architecture visualization, community mapping, and semantic discovery.
- Not an always-on skill, not a source of truth, not database authority.
- Isolated CLI execution via `uv tool`; no auto-hooks or persistent agent modifications.
- Live PostgreSQL introspection disabled; semantic LLM extraction disabled by default during baseline.
- Graph build is on-demand only (baseline: `GRAPHIFY_GRAPH = NOT_BUILT`).

---

# 7. MCP Tools

## Context7 MCP — ADD

Needed by `documentation-lookup`.

Preferred OMP project config:

```text
.omp/mcp.json
```

Use the Context7 remote OAuth endpoint:

`https://mcp.context7.com/mcp/oauth`

No Context7 skill needs to be added because `documentation-lookup` already provides the project routing behavior.

---

## Supabase MCP — ADD, restricted

Official server:

`https://mcp.supabase.com/mcp`

Project defaults:

- development/test project only;
- scope using `project_ref`;
- `read_only=true`;
- minimum feature groups;
- credentials through OMP OAuth/user profile, never committed.

Recommended initial feature groups:

```text
docs,database,debugging,development
```

Do not enable account management, branching, functions, or storage-management groups unless the task requires them.

Official safety guidance:
`https://supabase.com/docs/guides/ai-tools/mcp`

---

## GitNexus MCP — ENABLE AFTER SETUP

Canonical stdio shape:

```json
{
  "enabled": true,
  "command": "npx",
  "args": ["-y", "gitnexus@latest", "mcp"]
}
```

Normal project state after successful setup/license acceptance:

```text
GitNexus MCP = ENABLED
GitNexus index = CURRENT
```

This does **not** mean every task must call GitNexus. Use it selectively according to `AGENTS.md`.

If organizational-use licensing has not been accepted, do not run GitNexus; disable the MCP entry until the license decision is complete.

---

# 8. Tooling — Add Without Another Skill

## React Doctor CLI — ADD

Use as a focused quality gate:

```bash
npx react-doctor@latest --verbose --scope changed
```

Do not install its agent skill initially because React review is already covered by selected React/testing/review skills.

Use the current `--scope changed` syntax; old `--diff` is deprecated.

---

# 9. OMP Built-ins — Use Instead of Installing Duplicates

Do not add external duplicates for capabilities OMP already provides.

Use OMP built-ins for:

- LSP symbol navigation/rename/refactor support;
- debugger/DAP;
- bounded subagents;
- advisor;
- `/review`;
- memory/recall;
- context compaction;
- shell/edit/search primitives.

Therefore do not add from the sample repo:

- AgentMemory;
- WarpGrep;
- Morph editing;
- context-mode MCP;
- custom Claude `post_implementation_reviewer`.

---

# 10. Sample Repo Items Not Added

| Item | Decision | Reason |
|---|---|---|
| `next-best-practices` | SKIP | Retired by Vercel; use version-matched Next docs |
| `context-engineering` | SKIP | overlaps OMP + `context-budget` |
| `context-mode` MCP | SKIP | environment-specific; OMP already manages context |
| AgentMemory | SKIP | OMP has memory capabilities |
| Code Review Graph | SKIP | not required; OMP LSP/search is first-pass, GitNexus is graph/impact engine |
| WarpGrep | SKIP | OMP search/LSP + GitNexus |
| Morph edit | SKIP | OMP editing/LSP |
| OpenSpec | SKIP | would create second spec authority |
| `generate-tests` | SKIP | `tdd` + `react-testing` |
| `web-design-guidelines` | SKIP | canonical design + accessibility + Front-End Checklist |
| `grill-with-docs` | SKIP | coding phase source is already defined |
| `grilling` | SKIP | same |
| `domain-modeling` | SKIP | risks reopening settled domain rules |
| `wayfinder` | SKIP | Orca orchestration handles larger work decomposition |
| custom `post_implementation_reviewer` | SKIP | OMP `/review` + advisor |
| `code-deduplication` skill | SKIP for now | source unclear; use GitNexus/LSP/search rule |
| Lefthook | DEFER | add after project verification scripts/CI stabilize |
| React Doctor skill | SKIP | use CLI, avoid React-skill overlap |

---

# 11. Quick Router

```text
Any Supabase task
  -> supabase

SQL / migration / RLS
  -> supabase-postgres-best-practices
  -> security-review if security-sensitive

Google OAuth / Supabase Auth
  -> supabase
  -> documentation-lookup
  -> security-review

React / TSX
  -> react-patterns
  -> vercel-react-best-practices

Next.js framework behavior
  -> installed-version Next docs
  -> documentation-lookup
  -> react-patterns

High-risk behavior
  -> tdd

Bug
  -> diagnosing-bugs
  -> specialist after root-cause narrowing

Shared/high-impact symbol
  -> GitNexus impact/context
  -> OMP LSP/search

Pre-merge
  -> independent implementation Reviewer (`eiu-code-review` where applicable)
  -> OMP independent /review for high-risk
  -> ponytail-review if complexity grew
  -> React Doctor for meaningful React diff
  -> verification-before-completion

Major UI / pre-release
  -> web-design-guidelines
  -> browser-qa
Vercel deployment
  -> deploy-to-vercel

Cross-worktree parallel implementation
  -> Orca orchestration

Orca worktree/terminal/handoff
  -> orca-cli
```
