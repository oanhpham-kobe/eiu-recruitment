# OMP_NATIVE_SETUP.md

This repository now carries its OMP project integration directly. Do **not** reinstall the old 23-skill topology or recreate machine-specific global skill dependencies.

## After cloning/pulling

Start from the repository root and inspect:

```text
AGENTS.md
REVIEW.md
SKILLS.md
.omp/AGENTS.md
.omp/RULES.md
.omp/config.yml
.omp/agents/
.omp/mcp.json
```

Restart OMP after pulling because skill/agent discovery occurs at session startup.

## Expected OMP-native behavior

1. Project skills are discovered from `.agents/skills/<name>/SKILL.md`.
2. Project task agents are discovered from `.omp/agents/*.md`.
3. The main OMP session owns the native Todo.
4. `.omp/config.yml` enables eager Todo creation for non-trivial work.
5. Specialized executors use `autoloadSkills` rather than manually resolving `SKILLS_LOCK.yaml` paths.
6. Additional skills are loaded on demand through `skill://<name>`.
7. `SKILLS_LOCK.yaml` is provenance/integrity metadata only.

## Project agents expected

```text
eiu-db-executor
eiu-ui-executor
eiu-debugger
eiu-general-executor
eiu-reviewer
```

## Required environment value

Set the development/test Supabase project reference outside source control:

```text
SUPABASE_PROJECT_REF=<development-or-test-project-ref>
```

`.omp/mcp.json` uses it for the read-only `supabase-dev` MCP definition.

## Validation

Run:

```bash
python project_control/validate_omp_native.py
python project_control/validate_control_plane.py
```

Then start/restart OMP and confirm:

- native Todo appears before a non-trivial implementation request;
- `/agents` (or the current OMP agent discovery surface) lists the EIU project agents;
- project skills are discoverable;
- `skill://verification-before-completion` can be read;
- a database task dispatched to `eiu-db-executor` starts with its declared skills autoloaded;
- a UI task dispatched to `eiu-ui-executor` starts with its declared skills autoloaded;
- subagents do not create or own the parent Todo.

## Do not recreate

Do not restore these as project workflow primitives:

```text
implement
code-review
context-budget
frontend-checklist-global
karpathy-guidelines
```

Do not make project correctness depend on user-global copies of:

```text
vercel-react-best-practices
vercel-composition-patterns
verification-before-completion
```

`verification-before-completion` is now project-local. The two optional Vercel skills may still be discovered from a user's profile, but project agents do not require them.

## Safety

Do not put secrets or production credentials in repository config. Do not point Supabase MCP at production by default. Do not deploy, mutate production, or merge to main without explicit authorization.
