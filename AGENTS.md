# AGENTS.md — EIU Recruitment Agent Contract

## Purpose

This repository uses **oh-my-pi (OMP)** as the coding runtime inside a worktree and **Orca** for cross-worktree orchestration when needed. The current canonical project sources remain the business, product, design, security, and architecture authority.

This file defines repository rules. It does not replace OMP's native Todo, skill discovery, task-agent, review, tool, or MCP runtime.

---

## 1. Authority and source freshness

Use this precedence when instructions conflict:

1. non-bypassable security, authorization, privacy, data-integrity, concurrency, accessibility, secret, production, and destructive-action boundaries;
2. current canonical project sources;
3. explicit Owner instruction for the current work, when compatible with the boundaries above;
4. this `AGENTS.md` and `REVIEW.md`;
5. task-specific OMP skills;
6. generic framework/community guidance.

Before a non-trivial implementation or review:

- locate and read the current canonical source sections that govern the behavior;
- inspect the current implementation and affected tests/migrations;
- treat stale plans, old prompts, old review notes, and model memory as non-authoritative;
- if an Owner-authorized change reopens a canonical contract, update that contract through the controlled source-change path rather than silently overriding it in code.

Skills are advisory capability packs. They never become a second business or design source of truth.

---

## 2. OMP-native runtime ownership

### Main OMP session owns

The top-level OMP session owns:

- the visible native Todo;
- decomposition of the current user/requested work;
- selection and dispatch of task agents;
- acceptance of subagent results;
- focused verification;
- review/repair coordination;
- integration and next-frontier decisions when authorized.

For work with three or more distinct steps, use the native Todo. Project settings in `.omp/config.yml` intentionally enable eager Todo creation so implementation starts with a visible phased plan.

Todo is session execution state. It does **not** replace durable project state in `project_control/`.

### Subagents own bounded delegated work

OMP task agents are workers. They:

- receive a self-contained assignment;
- inspect and modify only the delegated scope;
- use their autoloaded or on-demand skills;
- perform focused verification appropriate to the assignment;
- return evidence and blockers to the parent.

Subagents do **not** own:

- the parent Todo;
- the autonomous safe frontier;
- project-wide task scheduling;
- integration-branch acceptance;
- dispatch of the next project task unless the parent explicitly delegates that responsibility.

Do not recreate Todo state inside subagent prompts or evidence files.

---

## 3. OMP project layout

Canonical OMP integration surfaces are:

```text
repo/
├─ AGENTS.md
├─ REVIEW.md
├─ SKILLS.md
├─ SKILLS_LOCK.yaml          # provenance/integrity metadata only
├─ .agents/
│  └─ skills/
└─ .omp/
   ├─ AGENTS.md              # imports root AGENTS.md
   ├─ RULES.md               # short sticky invariants
   ├─ WATCHDOG.md
   ├─ config.yml             # project OMP settings
   ├─ mcp.json
   └─ agents/                # OMP-native project task agents
```

Project skills live one level below `.agents/skills/`:

```text
.agents/skills/<skill-name>/SKILL.md
```

Each skill must have a unique `name` and a useful `description` in frontmatter.

Do not copy the same skill into multiple project providers. OMP already discovers providers and resolves same-name collisions by provider precedence.

`SKILLS_LOCK.yaml` is **not** a runtime resolver. Never make an executor manually resolve a filesystem skill path from that file.

Local linked worktrees are execution surfaces, not durable task records. New local Orca/Git worktrees should live below the gitignored `.worktrees/` container described in `project_control/README.md`. Do not add new machine-specific absolute worktree paths to durable task history; runtime ownership belongs in the live worker state when needed.

---

## 4. Native skill usage

OMP discovers skill metadata at session startup and exposes skill content through `skill://<name>` and `/skill:<name>`.

Use skills in two ways:

1. **Agent specialization:** `.omp/agents/*.md` declares `autoloadSkills`; OMP injects those skills before the child agent's first task prompt.
2. **On-demand specialization:** the main session or a worker reads `skill://<name>` when a newly discovered concern enters that domain.

Do not maintain a parallel `AVAILABLE / LOADED / APPLIED` receipt protocol. Runtime loading belongs to OMP. Evidence should describe the implementation/test/review decision, not ask the worker to self-certify a synthetic loader state.

### Database / Supabase work

Use `eiu-db-executor` for material Supabase/PostgreSQL implementation. It autoloads:

- `supabase`;
- `supabase-postgres-best-practices`;
- `security-review`;
- `tdd`;
- `verification-before-completion`.

Database authority remains repository migrations, declarative schema, direct SQL, and tests.

### React / UI work

Use `eiu-ui-executor` for material React/Next.js UI implementation. It autoloads:

- `react-patterns`;
- `accessibility`;
- `react-testing`;
- `verification-before-completion`.

When Next.js framework behavior matters, inspect the installed version and prefer its version-matched documentation before relying on memory.

### Debugging

Use `eiu-debugger` for defects that require diagnosis. It autoloads:

- `diagnosing-bugs`;
- `verification-before-completion`.

After root-cause narrowing, load additional domain skills through `skill://<name>` only if relevant.

### Other implementation

Use `eiu-general-executor` only when no more specific project agent fits. It autoloads `verification-before-completion`; load additional specialist skills on demand.

### Review

Use OMP's built-in reviewer or project `eiu-reviewer` for independent review. Reviewers are read-only. They use `REVIEW.md`, canonical project sources, the exact diff, direct source evidence, and specialist skills on demand.

A worker's claim of success is never acceptance evidence by itself.

---

## 5. Task dispatch contract

A delegated task must be self-contained and use OMP's native task semantics.

Provide:

```text
# Target
Exact files/symbols or bounded area; explicit non-goals.

# Change
Required behavior and constraints. Do not over-specify ordinary implementation choices when the canonical source leaves them open.

# Acceptance
Observable focused verification and expected result.
```

For independent work, batch task agents only when ownership does not overlap. Same-file or same-migration ownership must be serialized unless an explicit merge boundary has been designed first.

Never let multiple writing agents concurrently mutate the same worktree.

---

## 6. Supabase, security, and privacy invariants

Authentication is not authorization.

For mutation paths enforce, where applicable:

```text
authenticate
→ authorize server-side
→ validate untrusted input
→ execute the approved transactional command/RPC
→ return a stable safe result/error
```

Never weaken RLS, grants, locking, optimistic concurrency, idempotency, audit, private Storage, or authorization to make a feature pass.

Never expose service-role keys, Google Client Secret, session/refresh tokens, OTPs, signed private URLs, or other secrets.

Supabase MCP is developer tooling only. It must default to a non-production project and read-only access. Repository migrations/schema remain authority over live MCP inspection.

---

## 7. Graph and documentation tools

GitNexus is an optional impact/navigation aid for shared or high-risk code. Use it when graph evidence materially improves understanding; do not call or refresh it ceremonially.

Every material graph conclusion must be confirmed against direct source. Database definitions are never inferred from graph absence.

Use `documentation-lookup` when current library/framework documentation is needed. Current canonical project sources still outrank external documentation for project behavior.

---

## 8. Verification and completion

Before accepting a worker result or claiming work is fixed/complete:

1. inspect the actual diff/result;
2. run fresh focused verification that proves the claim;
3. read the output and exit status;
4. run broader verification only when the scope/risk requires it;
5. obtain independent review for the lifecycle when required;
6. report the actual state, including failures or blockers.

Do not treat a subagent `completed` status, a previous test run, or a CI result for another SHA as completion proof.

### Verification economy and failed-check closure

Use the smallest fresh verification set that proves the current claim. During implementation or repair:

- rerun the failed check/test plus directly affected regressions and crossed shared invariants;
- keep previously passed unrelated checks closed when changed code, dependencies, shared contracts, or concrete regression evidence do not implicate them;
- do not rerun unrelated database, browser, or UI suites merely because another domain failed;
- broaden verification only when the changed surface or risk requires it.

A final acceptance candidate still requires fresh exact-SHA CI for the impacted domain set. Domain-level lint/typecheck/build/test may be rerun at that acceptance boundary when the domain changed; that is distinct from blind full-system reruns on every repair commit.

---

## 9. Review lifecycle

`REVIEW.md` defines project-specific review priorities and reject conditions.

In `AUTONOMOUS`, the parent may run implementation → focused verification → independent review → bounded repair/re-review → serialized integration → exact-SHA CI → next safe frontier, subject to the durable autonomy policy.

In `BOUNDED`, perform only the Owner-authorized work set. Do not infer a next-frontier task. Integration/CI occurs only when the bounded authorization explicitly permits it.

### Candidate producer, independent OMP review, and checkpoint acceptance

For tasks implemented outside OMP (for example, by ChatGPT through GitHub), the producer performs a first self-review, but that self-review is not the independent acceptance review. OMP then uses the read-only `eiu-reviewer` (or built-in reviewer) against the exact candidate SHA.

Review waves may contain at most two independent task candidates. Each task keeps its own exact SHA, findings, verdict, CI evidence, and checkpoint. A downstream task must not consume an unaccepted dependency merely because both were implemented in the same wave.

The reviewer remains read-only and must not create or move Git refs. OMP main session owns review-result persistence, CI/integration decisions, and checkpoint creation. When the Owner requests GitHub-visible review handoff, OMP main persists the reviewer result on a non-candidate evidence branch such as `review/<TASK_ID>-<SHORT_SHA>-vN`, with the artifact at `project_control/reviews/<TASK_ID>_OMP_REVIEW_<SHORT_SHA>_vN.md`. The evidence branch must not mutate the candidate ref; the artifact is evidence only, not a new authority.

After a repair creates a new candidate SHA, any prior PASS belongs to the old SHA and cannot accept the new one. The pre-integration candidate review remains bound to that candidate SHA. After serialized integration, if the final integration SHA differs, OMP performs a targeted exact-SHA acceptance re-review/equivalence check on the integration SHA before CI. If serialized integration preserves the exact candidate SHA, the candidate review may serve as the final acceptance review.

Before risky task implementation, create an immutable recovery ref such as `checkpoint/pre-S04-004-001`. After final OMP acceptance review PASS and exact-SHA CI PASS, OMP main creates an immutable accepted ref such as `checkpoint/S04-004-accepted-001`. Never force-move an existing checkpoint; create a new numbered checkpoint for a later accepted repair.

For accepted task checkpoints:

```text
FINAL_OMP_ACCEPTANCE_REVIEW_SHA == CI_SHA == ACCEPTED_CHECKPOINT_SHA
```

After all tasks in a slice are individually accepted, run an additional slice-level composition review/broader regression gate when the slice risk warrants it. Slice review supplements task review; it does not replace it.

---

## 10. Durable autonomy state

For scheduling, task-start, integration, CI, or next-frontier decisions, read:

- `project_control/AUTONOMY_PARALLEL_GOVERNANCE.md` — lifecycle/scheduling authority;
- `project_control/AUTONOMY_RUN_STATE.yaml` — live durable runtime state;
- `project_control/TASK_REGISTRY.yaml` and `SLICE_REGISTRY.yaml` — task/slice DAG.

OMP Todo mirrors the currently executing work for the session. It is not a competing durable registry and must not be persisted as another control-plane authority.

`project_control/CURRENT_STATE.md` is the single derived cross-session handoff/navigation snapshot. Refresh it after accepted task checkpoints or meaningful interruptions, but never let it override Git or the durable registries. Do not create runtime-specific memory/state files that duplicate it.

When a long-running assistant/session approaches context pressure or another interruption boundary, do not start another risky/write-heavy phase. Finish the current atomic mutation, commit/push a recoverable SHA, run the relevant validators/checks, refresh durable state plus `CURRENT_STATE.md`, and hand off the exact branch/SHA, task status, test/review/CI state, unresolved findings, checkpoint refs, next action, and do-not-repeat boundaries. Never intentionally hand off half-edited or identity-ambiguous repository state.

`execution_mode` is exactly `AUTONOMOUS` or `BOUNDED`.

---

## 11. External actions

Do not push/merge to `main`, production-deploy, apply destructive live migrations, delete production data, or cross another explicit external authorization boundary unless the Owner has authorized that action.

Routine work on an Owner-authorized development/governance branch may be committed and pushed when the active task explicitly authorizes repository writes.

---

## 12. Simplicity rule

Prefer OMP-native primitives over repository-invented runtime abstractions:

- native Todo instead of Markdown/checklist lifecycle emulation;
- native task agents instead of prose-only Executor roles;
- `autoloadSkills` / `skill://` instead of custom skill-path loaders;
- native reviewer/task tooling instead of workflow skills that duplicate OMP;
- project config instead of machine-specific assumptions.

Add governance only where it protects a project invariant that OMP itself cannot know.
