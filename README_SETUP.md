# EIU Recruitment — Orca + OMP Agent Control Bundle (v2.4)

## Recommended Normal State

- **Orca:** Worktrees / handoffs / multi-agent orchestration.
- **OMP:** Primary coding runtime (PID 2056, OMP 18.1.6).
- **Project Skills:** `.agents/skills/` (13 active specialists + 2 release-only + 8 GitNexus on-demand skills).
- **Native Review Skill:** `.omp/skills/eiu-code-review/`.
- **Global Reuse Skills:** `~/.omp/agent/skills/` (verified native p100 copies for vercel-react-best-practices, composition-patterns, verification-before-completion).
- **Context7 MCP:** Enabled (`https://mcp.context7.com/mcp/oauth`).
- **Supabase MCP:** Non-production, project-scoped, read-only by default (`SUPABASE_PROJECT_REF`).
- **Code Review Graph (CRG 2.3.8):** Broad discovery and diff triage graph; manually configured MCP with restricted tool allowlist; hooks, watch, and daemon OFF; explicit freshness gate before task evidence.
- **GitNexus (1.6.10):** Primary precise code relationship graph (caller/callee, blast radius, symbol tracing); project-pinned; `indexOnly: true`; explicit freshness gate before task evidence.
- **Graphify (0.9.47):** Retained in isolated virtual environment (`uv tool`) as a future optional tool (`DORMANT`, `NOT_BASELINE_ACTIVE`); no baseline graph built; no MCP; no git hooks; no agent rules; live PostgreSQL introspection disabled. Retained solely to avoid destructive uninstall and for potential future heterogeneous architecture visualization.

## Approved v2.4 Graph Architecture

```text
                     REPOSITORY AUTHORITY
                            │
                    DIRECT SOURCE + LSP
                            │
        ┌───────────────────┴───────────────────┐
        │                                       │
 CODE REVIEW GRAPH                          GitNexus
 broad / discovery                         precise
 review / diff triage                      symbol graph
 minimal context                           callers/callees
 changed-area risk                         blast radius
        │                                       │
        └───────────────────┬───────────────────┘
                            │
                    SOURCE CROSS-CHECK
                            │
                         TESTS
                            │
                    EIU CODE REVIEW


DATABASE PATH:

App source
   ↓
Supabase boundary
   ↓
direct SQL/schema/migrations
   ↓
DATABASE AUTHORITY

Graphs may assist discovery only.
```

## Freshness Contracts
- **CRG:** Freshness must be established before first use via `code-review-graph status`. Rebuild/update explicitly when source changes.
- **GitNexus:** Freshness checked via `gitnexus status`. If stale, rerun `gitnexus analyze --index-only`.
- After material source edits, all previous graph evidence is considered STALE until refreshed.
