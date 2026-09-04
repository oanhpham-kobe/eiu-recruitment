# EIU Recruitment — First Baseline Commit Manifest

## Baseline Purpose
Establish the canonical Git baseline for the EIU Recruitment repository, incorporating the fully validated v2.4 control plane, canonical project skills, and initial design/logic assets, while strictly excluding runtime databases, caches, and archive files.

- **Repository Root:** `D:/orca/recruitment`
- **Baseline Date:** `2026-09-04`
- **Control-Plane Version:** `v2.4` (Graph + Skills Architecture)
- **Application Root:** `recruitment_webapp/`

---

## Included Categories & Tracked Scope

1. **Root Control Files:**
   - `.gitignore` (canonical ignore rules)
   - `.gitnexusrc` (GitNexus pure index configuration)
   - `AGENTS.md` (portable agent policy & authority hierarchy)
   - `REVIEW.md` (review contract & verification checklists)
   - `SKILLS.md` (skill catalog & tool topology)
   - `SKILLS_LOCK.yaml` (full provenance lockfile for skills & tools)
   - `README_SETUP.md` (runtime & architecture operational guide)
   - `INSTALL_SKILLS_AND_TOOLS_PROMPT.md` (canonical setup instructions)
   - `FIRST_COMMIT_MANIFEST.md` (this baseline manifest)

2. **OMP Configuration (`.omp/`):**
   - `.omp/AGENTS.md` (OMP import anchor)
   - `.omp/RULES.md` (10 sticky hard rules)
   - `.omp/WATCHDOG.md` (advisor review guidance)
   - `.omp/mcp.json` (MCP definitions: Context7, Supabase dev read-only, GitNexus 1.6.10, Code Review Graph 2.3.8)
   - `.omp/skills/eiu-code-review/SKILL.md` (authoritative EIU review skill)

3. **Canonical Project Skills (`.agents/skills/`):**
   - 13 Active Project Specialists (`documentation-lookup`, `react-patterns`, `security-review`, `accessibility`, `react-testing`, `browser-qa`, `architecture-decision-records`, `click-path-audit`, `supabase`, `supabase-postgres-best-practices`, `tdd`, `diagnosing-bugs`, `ponytail-review`)
   - 2 Release-Only Skills (`deploy-to-vercel`, `vercel-optimize`)
   - 8 GitNexus On-Demand Skills (`gitnexus-exploring`, `gitnexus-impact-analysis`, `gitnexus-debugging`, `gitnexus-refactoring`, `gitnexus-guide`, `gitnexus-cli`, `gitnexus-pdg-query`, `gitnexus-taint-analysis`)

4. **Recruitment Application Core Assets (`recruitment_webapp/`):**
   - `design_system/` (markdown specifications, design tokens CSS/JSON, page component matrices)
   - `image_reference/` (UI layout and screen references)
   - `recruitment_logic/` (workflow models and business logic)

---

## Excluded Categories (Ignored by `.gitignore`)

- **Generated Graph Databases & Indexes:**
  - `.code-review-graph/` (CRG SQLite database and cache)
  - `.gitnexus/` (GitNexus LadybugDB index and FTS files)
- **Archive & Legacy Inputs:**
  - `App_Tuyen_Dung_EIU_Full_Handover_v1.8.zip`
  - `EIU_Recruitment_Design_System_v1.7.zip`
  - `Skills set.zip`
  - `Skills set/` (historical reference folder)
- **Environment & Credentials:**
  - `.env`, `.env.*` (except `.env.example` if created later)
  - `.vercel/`
- **Build & Dependency Artifacts:**
  - `node_modules/`, `.next/`, `dist/`, `build/`, `coverage/`, `*.log`
  - Python caches (`__pycache__/`, `*.pyc`), virtual environments (`.venv/`)

---

## Graph Intelligence Architecture (Approved v2.4)
- **Primary Implementation Evidence:** Direct Source + LSP
- **Broad Discovery & Diff Triage:** Code Review Graph 2.3.8 (`code-review-graph==2.3.8`, restricted MCP allowlist)
- **Precise Call & Impact Graph:** GitNexus 1.6.10 (`gitnexus@1.6.10`, pure index mode)
- **Database Authority:** Declarative Schema + Ordered Migrations + Direct SQL + Tests
- **Dormant Optional Tool:** Graphify 0.9.47 (isolated virtualenv, not baseline active)

---

## Safety & Boundary Assertions
- **No Secrets Included:** Pre-commit secret scanning verified zero credential literals or private keys.
- **No Remote Services Linked:** GitHub remote is unconfigured; Supabase and Vercel projects are unlinked.
- **Planner Deferred:** Planner, `project_control/`, and Slice 00 execution remain unstarted.
