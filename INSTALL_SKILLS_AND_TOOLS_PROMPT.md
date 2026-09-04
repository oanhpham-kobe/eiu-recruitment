# INSTALL_SKILLS_AND_TOOLS_PROMPT.md

Copy the prompt below into the coding agent that will prepare the EIU Recruitment development environment.

---

## PROMPT START

You are preparing the EIU Recruitment repository for **Orca + oh-my-pi (OMP)**.

Your goal is to install and configure the approved skills/tools **without duplicating skills, overwriting project instructions, exposing secrets, or creating a second source of truth**.

Read first:

- `AGENTS.md`
- `REVIEW.md`
- `SKILLS.md`
- `.omp/RULES.md`

The current canonical project sources remain authoritative.

Do not modify application/business behavior during this setup task.

---

# A. Hard Constraints

1. Use `.agents/skills/` as the single canonical project skill home.
2. Do not duplicate selected skills into:
   - `.claude/skills`
   - `.omp/skills`
   - `.codex/...`
3. Do not copy external repository-level:
   - `CLAUDE.md`
   - `AGENTS.md`
   - `REVIEW.md`
   into the project.
4. Do not overwrite:
   - root `AGENTS.md`
   - `REVIEW.md`
   - `SKILLS.md`
   - `.omp/AGENTS.md`
   - `.omp/RULES.md`
   - `.omp/WATCHDOG.md`
5. Do not modify business/design source documents.
6. Do not change live Supabase/Google/Vercel production settings.
7. Do not commit secrets.
8. Do not connect Supabase MCP to production.
9. Do not commit/push/merge/deploy production unless explicitly instructed.
10. Before any CLI command whose syntax may have changed, run the CLI's current `--help`.

---

# B. Inspect Runtime First

Confirm:

```text
- Orca installed and reachable
- OMP installed and reachable
- Node package manager available
- current repository root
- current Next.js version, if package.json exists
- whether .agents/skills already exists
- existing duplicate SKILL.md names
```

Do not assume Claude Code is installed or used.

Do not create a manually maintained project `CLAUDE.md`.

If Next.js later generates `CLAUDE.md` containing `@AGENTS.md`, treat it as a framework compatibility shim only.

---

# C. Inventory Existing Skills

Find every discovered project skill candidate under relevant project directories.

Extract the YAML frontmatter `name:` from each `SKILL.md`.

Create a table:

```text
skill_name | path | provider/location | action
```

Actions:

- KEEP
- UPDATE
- INSTALL
- REMOVE_DUPLICATE
- LEAVE_UNRELATED

Do not delete unrelated user-owned skills.

If the same selected skill name exists in multiple project providers, keep only the canonical `.agents/skills/<name>` project copy unless a runtime technical requirement proves otherwise.

---

# D. Create Canonical Skill Home

Ensure:

```text
.agents/skills/
```

Each selected skill must end at:

```text
.agents/skills/<skill-name>/SKILL.md
```

Keep that skill's required local references/scripts/assets under its own directory.

OMP provider scanning is one-level below `skills/`; do not nest skills under category folders.

---

# E. Install ECC Skills — 9 Only

Source:

`https://github.com/affaan-m/ECC.git`

Install only:

- `documentation-lookup`
- `react-patterns`
- `security-review`
- `accessibility`
- `react-testing`
- `browser-qa`
- `context-budget`
- `architecture-decision-records`
- `click-path-audit`

Do **not** install `postgres-patterns`.

Clone to a temporary directory, copy only selected complete skill directories into `.agents/skills`, then remove the temporary clone.

---

# F. Install Official Supabase Skills — 2

Source:

`https://github.com/supabase/agent-skills.git`

Install:

- `supabase`
- `supabase-postgres-best-practices`

Copy each full skill directory with its references.

These replace generic PostgreSQL guidance for this project.

Do not copy the Supabase repository's root `AGENTS.md`, `CLAUDE.md`, or `.mcp.json`.

---

# G. Install Matt Pocock Skills — 4 Only

Source:

`https://github.com/mattpocock/skills.git`

Install:

- `implement`
- `tdd`
- `code-review`
- `diagnosing-bugs`

Inspect current paths first; do not guess directory layout.

Copy only required selected skill directories/assets.

---

# H. Install Vercel Agent Skills — 4 Only

Source:

`https://github.com/vercel-labs/agent-skills.git`

Install canonical skill names:

- `vercel-react-best-practices`
- `vercel-composition-patterns`
- `deploy-to-vercel`
- `vercel-optimize`

The source directory name can differ from the `name:` in `SKILL.md`; preserve canonical `name:`.

Do not install unrelated React Native/view-transition/writing/token skills.

---

# I. Do Not Install Old `next-best-practices`

Do not install from old mirrors or archived copies.

Current Vercel guidance has retired `next-best-practices`.

Instead:

1. detect the installed Next.js version;
2. if installed-version bundled docs exist, preserve/use them;
3. preserve any Next.js-managed block that `next dev` adds to root `AGENTS.md`;
4. do not overwrite the project's non-managed `AGENTS.md` content.

Do not install current Next workflow skills unless a later task specifically requires them.

Do not upgrade Next.js in this setup task.

---

# J. Install Ponytail Review — 1

Source:

`https://github.com/DietrichGebert/ponytail.git`

Install only:

- `ponytail-review`

---

# K. Install Superpowers Verification — 1

Source:

`https://github.com/obra/superpowers.git`

Install only:

- `verification-before-completion`

Do not install duplicate TDD/debugging workflows.

---

# L. Install Front-End Checklist Global — 1

Source:

`https://github.com/thedaviddias/Front-End-Checklist.git`

Install only:

- `frontend-checklist-global`

Do not copy hundreds of rule-specific skills.

If its MCP/retrieval dependency requires separate configuration, report it instead of silently adding broad infrastructure.

---

# M. Install Karpathy Skill — 1

Source:

`https://github.com/multica-ai/andrej-karpathy-skills.git`

The repository is small; clone it if convenient.

Install/activate only:

- `karpathy-guidelines`

Do not copy the repo's root `CLAUDE.md` or Cursor rules into the project.

---

# N. Verify Project Skill Count

Expected manually selected project skills:

```text
23
```

The 23 are:

```text
documentation-lookup
react-patterns
security-review
accessibility
react-testing
browser-qa
context-budget
architecture-decision-records
click-path-audit

supabase
supabase-postgres-best-practices

implement
tdd
code-review
diagnosing-bugs

vercel-react-best-practices
vercel-composition-patterns
deploy-to-vercel
vercel-optimize

ponytail-review
verification-before-completion
frontend-checklist-global
karpathy-guidelines
```

Check each `name:` is unique.

---

# O. Orca Runtime Skills

Do not vendor-copy Orca's own skills into `.agents/skills`.

Resolve the correct Orca executable for the installed environment, then use the installed binary's version-matched skill guides.

Verify at least:

```text
orca-cli
orchestration
```

Use the Orca binary's current `skills get`/help mechanism; do not guess flags from GitHub copies.

Report whether both runtime skills are available.

Do not add `computer-use`, emulators, Linear, or per-workspace VM skills unless separately requested.

---

# P. GitNexus — Controlled Setup

Source:

`https://github.com/abhigyanpatwari/GitNexus.git`

First:

1. read the current license;
2. report organizational-use implications;
3. continue only under the user's accepted use context.

Install/use GitNexus without letting it take ownership of project policy files.

## MCP

This project does not use Code Review Graph. GitNexus is therefore the default graph/impact engine rather than a disabled optional fallback.

The project `.omp/mcp.json` contains an **enabled** GitNexus stdio definition.

Before starting GitNexus:

1. review the current license and organizational-use implications;
2. if the user accepts/has accepted that use, keep the MCP entry enabled;
3. if licensing is not accepted, set only the GitNexus entry to `enabled: false` and report the blocked capability.

Do not disable GitNexus merely because Code Review Graph is absent. Its absence is the reason GitNexus should remain available after setup.

Expected MCP command shape from the current upstream project is:

```text
npx -y gitnexus@latest mcp
```

Validate against current GitNexus help before relying on it.

## Index

Run current GitNexus `analyze --help`.

When the current version supports them, use options that prevent regeneration of project policy files and duplicate skills, specifically the current equivalents of:

```text
--skip-agents-md
--skip-skills
```

Do not let `analyze` write or modify root `AGENTS.md` or create a competing project policy.

After indexing:

1. start/reload OMP;
2. verify the `gitnexus` MCP server is connected;
3. verify the repository appears in GitNexus;
4. verify index freshness;
5. perform one read-only smoke test such as repository context/query;
6. leave GitNexus enabled for normal development.

Do not require GitNexus on every trivial edit. Availability is default; invocation is task-routed by `AGENTS.md`.

## Standard GitNexus skills

Install exactly once into `.agents/skills`:

- `gitnexus-exploring`
- `gitnexus-impact-analysis`
- `gitnexus-debugging`
- `gitnexus-refactoring`
- `gitnexus-guide`
- `gitnexus-cli`

Use the current shipped GitNexus skill sources, preserving their `name:` and `description:` frontmatter.

These six are **separate from the 23 project-domain skills**.

Do not install every newer/experimental GitNexus skill automatically.

---

# Q. Context7 MCP

Use `.omp/mcp.json`.

The provided configuration uses:

```text
https://mcp.context7.com/mcp/oauth
```

OMP supports remote OAuth MCP.

Do not commit Context7 credentials.

Authenticate interactively through OMP only after the MCP definition is loaded.

Verify Context7 exposes the documentation tools required by `documentation-lookup`.

If OAuth is unavailable in the installed OMP build, use the current Context7-supported API-key/remote method with secrets supplied outside source control.

---

# R. Supabase MCP

Use the existing `.omp/mcp.json` template.

Required defaults:

```text
development/test project only
project_ref = environment variable
read_only = true
features = docs,database,debugging,development
```

Do not put a real project ref directly into committed config if the repository should remain environment-neutral.

Set the local environment variable:

```text
SUPABASE_PROJECT_REF
```

to the **development/test** project reference.

Authenticate through OMP's MCP OAuth flow.

Do not point this MCP server at production.

Do not switch it to write mode in this setup task.

---

# S. React Doctor CLI

Do not install another React Doctor skill.

Verify the current CLI command works:

```bash
npx react-doctor@latest --version
```

Then, if React source exists, run a non-destructive changed-scope scan:

```bash
npx react-doctor@latest --verbose --scope changed
```

If there is no meaningful React diff yet, record the command as a future quality gate instead of manufacturing changes.

Do not run auto-fixes.

---

# T. OMP Native Control Files

Verify these files exist:

```text
.omp/AGENTS.md
.omp/RULES.md
.omp/WATCHDOG.md
.omp/mcp.json
```

Expected behavior:

- `.omp/AGENTS.md` imports root `AGENTS.md`.
- `.omp/RULES.md` is short sticky policy.
- `.omp/WATCHDOG.md` imports/references `REVIEW.md`.
- `.omp/mcp.json` owns project MCP definitions.

Do not create a separate Claude-specific policy.

Restart OMP after adding skills because skill discovery occurs at session startup.

After restart, verify selected skills are discoverable by OMP. Prefer OMP-native discovery/`skill://` inspection rather than assuming filesystem presence equals runtime discovery.

---

# U. OMP Advisor

Do not enable a costly always-on advisor blindly.

Verify `.omp/WATCHDOG.md` is discoverable.

Recommended policy:

- routine/trivial work → advisor optional/off;
- auth/RLS/concurrency/migration/privacy/high-risk change → advisor recommended;
- final large/high-risk diff → run OMP independent `/review`.

Keep advisor tools read-only/investigative by default.

---

# V. Do Not Add Sample-Repo-Specific Duplicates

Do not install/configure:

- Code Review Graph merely to mirror the sample repository;
- AgentMemory;
- context-mode MCP;
- WarpGrep;
- Morph edit;
- OpenSpec;
- custom Claude `post_implementation_reviewer`;
- `context-engineering`;
- old `next-best-practices`;
- `code-deduplication` skill from an unknown source;
- React Doctor skill;
- Lefthook unless later requested.

OMP + selected skills + GitNexus already cover the needed capabilities.

---

# W. Final Validation

Produce:

```markdown
## Environment setup result

### Runtime
- Orca:
- OMP:
- Next.js detected version:

### Project skills
- expected: 23
- discovered: N
- missing:
- duplicate names:

### GitNexus skills
- expected selected standard: 6
- discovered:
- index status:
- license reviewed: YES/NO

### Orca runtime skills
- orca-cli:
- orchestration:

### MCP
- Context7 definition: PASS/FAIL
- Context7 auth/tool discovery: PASS/FAIL/USER ACTION
- Supabase dev definition: PASS/FAIL
- Supabase target is non-production: VERIFIED/NOT VERIFIED
- Supabase read-only: YES/NO
- GitNexus MCP: ENABLED/DISABLED (expected ENABLED after accepted setup)

### Tooling
- React Doctor CLI:
- OMP advisor/WATCHDOG:
- OMP /review availability:

### Safety
- root AGENTS.md unchanged except approved Next.js managed block: YES/NO
- REVIEW.md unchanged: YES/NO
- SKILLS.md unchanged: YES/NO
- no manually maintained CLAUDE policy added: YES/NO
- no secrets committed: YES/NO
- no production MCP target configured: YES/NO

### User actions required
...
```

Do not claim success unless you actually perform discovery/config validation.

## PROMPT END
