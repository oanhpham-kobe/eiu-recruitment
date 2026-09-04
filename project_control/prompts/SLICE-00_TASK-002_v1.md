# EIU Recruitment — Executor Prompt
## TASK-S00-002 — Dependency Selection/Pinning + Next.js App Router Scaffold
### Prompt version: SLICE-00_TASK-002_v1
### Independent-review release revision: TASK-S00-002 Pack v1.3

## 0. Execution Control

```text
SOURCE_BASELINE: Full Handover v1.17
SOURCE_SHA256: 0b39c3615dd5b34e998527a1d273e0b846458c7bd4170be46c9bb670bfcb3498
BUSINESS_STATUS: Business Logic Core v1.2 = FROZEN
TECHNICAL_STATUS: Technical Architecture v1.17 = TECHNICAL SPECIFICATION FROZEN
IMPLEMENTATION_GATE: READY TO IMPLEMENT
IMPLEMENTATION_VALIDATION_GATE: PENDING ACTUAL CODE EVIDENCE
DESIGN: v1.8 CURRENT / REVIEWED
RESPONSIVE: v1.10 READY FOR OWNER VISUAL UAT / NOT FROZEN

INDEPENDENT_REVIEW_STATUS: PASS
EXECUTION_STATUS: AUTHORIZED_BY_SOURCE
WORKFLOW_RELEASE_TOKEN: APPROVED_FOR_EXECUTOR
WORKFLOW_RELEASE_SCOPE: TASK-S00-002
DISPATCH_AUTHORITY: PLANNER_MAY_DISPATCH_TO_OMP_EXECUTOR
RELEASE_BINDING: INDEPENDENT_REVIEW_RELEASE_TASK_S00_002.md
```

### Hash-bound workflow release

This prompt is released for TASK-S00-002 only when the exact file bytes match the
SHA-256 recorded in `INDEPENDENT_REVIEW_RELEASE_TASK_S00_002.md`.

If the prompt bytes/hash do not match that release record:

```text
STOP: WORKFLOW_RELEASE_HASH_MISMATCH
```

Do not self-release, rewrite, broaden, or reinterpret the released scope.

---

## 1. Role

You are the Coding Executor for exactly:

```text
TASK-S00-002
Dependency selection/pinning + Next.js App Router scaffold
```

You are not authorized to start TASK-S00-003, TASK-S00-004, TASK-S00-005, or SLICE-01.

If implementation requires guessing or violating a current EIU source rule:

```text
BLOCKED: SPEC_GAP
```

with exact current source references.

---

## 2. Canonical Repository and Runtime Rehydration

Canonical remote:

```text
https://github.com/oanhpham-kobe/eiu-recruitment
default branch: main
repository visibility at Planner observation: PUBLIC
Planner-observed origin/main:
7c7c2b378c24e64d95a4b25c1c709b2ee6b38756
```

This SHA is an observation, not a permanent invariant.

Before writing:

1. fetch/re-observe canonical remote;
2. verify local canonical repository/worktree;
3. verify local HEAD, `origin/main`, visibility, branch/worktree and clean/dirty state;
4. read `project_control` state;
5. reconcile the known runtime metadata lag;
6. report:

```text
BASELINE
CURRENT_SLICE
CURRENT_TASK
LAST_VERIFIED_COMPLETED_TASK
LOCAL_HEAD
OBSERVED_ORIGIN_MAIN_AT_TASK_START
WORKTREE
BLOCKERS
NEXT_ACTION
```

Known committed metadata may still say older HEAD/private visibility. Treat verified differences matching repository publication as:

```text
RUNTIME_METADATA_LAG
```

not `SPEC_GAP`.

If repository/source/task facts materially disagree beyond known lag:

```text
STATE_INCONSISTENCY
```

Resolve/record truth before coding.

---

## 3. Project-Control Preconditions

Read:

```text
project_control/CURRENT_STATE.md
project_control/TASK_REGISTRY.yaml
project_control/SLICE_REGISTRY.yaml
project_control/OPEN_GAPS.md
project_control/DECISION_LOG.md
project_control/EVIDENCE_INDEX.yaml
project_control/TRACEABILITY_STATUS.csv
project_control/CHANGELOG_IMPLEMENTATION.md
project_control/README.md
project_control/prompts/SLICE-00_MASTER_PLAN_REFERENCE.md
```

The master Slice00 prompt is **reference only**. Do not execute it.

Required starting logical state:

```text
TASK-S00-001 = DONE
TASK-S00-002 = PLANNED / NOT_STARTED
TASK-S00-003 = NOT_STARTED / PLANNED
```

On released execution, store this exact reviewed prompt as:

```text
project_control/prompts/SLICE-00_TASK-002_v1.md
```

Do not overwrite previous executed prompt history.

---

## 3A. Mandatory Project-Control YAML Structural Preflight

Before changing Task002 status or scaffolding application code, machine-parse:

```text
project_control/TASK_REGISTRY.yaml
project_control/EVIDENCE_INDEX.yaml
project_control/SLICE_REGISTRY.yaml
```

Known current issue: prior metadata closure left structurally suspect YAML, including concatenated sequence entries in `TASK_REGISTRY.yaml`.

Classify any repair as:

```text
CONTROL_PLANE_SYNTAX_REPAIR
RUNTIME_METADATA_LAG
```

Never as:

```text
SPEC_GAP
BUSINESS_DRIFT
TECHNICAL_ARCHITECTURE_DRIFT
```

Required procedure:

1. Use a real YAML parser. Text inspection alone is insufficient.
2. If parse fails, repair syntax/indentation only where required.
3. Preserve historical evidence and meaning; do not delete history merely to make parsing pass.
4. Re-parse all three files after repair.
5. Verify:

```text
TASK-S00-001 = DONE
TASK-S00-002 = PLANNED / NOT_STARTED
TASK-S00-003 = PLANNED / NOT_STARTED
```

6. Required gate:

```text
PROJECT_CONTROL_YAML_PARSE = PASS
```

7. **Only after PASS** may Task002 change to `IN_PROGRESS`.

If semantics cannot be preserved while repairing syntax:

```text
STATE_INCONSISTENCY
```

Stop and report evidence.

---

## 4. Source Root and Authority

```text
SOURCE_ROOT = recruitment_webapp
```

Resolve all EIU source paths relative to `SOURCE_ROOT`.

Read at minimum:

```text
recruitment_webapp/START_HERE.txt
recruitment_webapp/review_pack/source_registry.yaml
recruitment_webapp/review_pack/00_README.md
recruitment_webapp/review_pack/01_PRODUCT_SCOPE_AND_ARCHITECTURE.md
recruitment_webapp/review_pack/12_IMPLEMENTATION_NOTES_VERCEL_SUPABASE.md
recruitment_webapp/review_pack/38_NON_FUNCTIONAL_REQUIREMENTS.md
recruitment_webapp/review_pack/44_DEPLOYMENT_OPERATIONS.md
recruitment_webapp/review_pack/52_TECHNICAL_GATE_STATUS.md
recruitment_webapp/review_pack/67_WEB_SECURITY_BASELINE.md
recruitment_webapp/review_pack/76_DEPENDENCY_BASELINE_POLICY.md
recruitment_webapp/review_pack/97_INDEPENDENT_REVIEW_IMPLEMENTATION_ALIGNMENT_V1_17.md
recruitment_webapp/review_pack/98_TECHNICAL_PRECODE_GATE_V1_17.md
```

Follow references to other CURRENT/NORMATIVE sources when needed.

Historical 95/96 are evidence only, not current authority.

Do not change Full Handover source in this task.

---

## 5. Execution Authority Model

```text
Full Handover current source
= WHAT the EIU system must do

AGENTS.md / REVIEW.md / SKILLS.md
= HOW repository execution is governed

project_control/
= WHERE implementation currently is

skills / CRG / GitNexus
= supporting tools
```

Current EIU source always wins over runtime tools/skills/graphs.

Database authority remains:

```text
direct SQL + declarative schema + ordered migrations + tests
```

Graphs never prove SQL/RPC/RLS/policy/function absence or correctness.

---

## 6. ONE WRITER PER WORKTREE

Hard rule:

```text
ONE WRITER PER WORKTREE
```

Responsibility:

```text
Orca → task worktree/orchestration/handoff
OMP  → implementation inside assigned worktree
```

Do not mutate `main` directly.

Preferred branch:

```text
task/TASK-S00-002-next-app-scaffold
```

### Assignment boundary

Planner/Orca owns task worktree creation and assignment **before** Executor dispatch.
The Executor must not create, switch, delete, or repurpose Orca worktrees.

At Executor startup, verify that the current workspace is the Planner/Orca-assigned
Task002 worktree and that the current branch is task-scoped and not `main`.

If no task worktree has been assigned, or Executor is running on `main`:

```text
STOP: WORKTREE_NOT_ASSIGNED
```

If another writer owns the same worktree:

```text
STOP: WORKTREE_WRITE_CONFLICT
```

---

## 7. Exact Task Scope

Implement only:

1. Reconcile live runtime/project-control metadata at Task002 start.
2. Record the implementation decisions for app root/package manager/dependency baseline.
3. Establish production application root:
   ```text
   web/
   ```
4. Select/re-verify current supported dependency versions.
5. Scaffold a minimal Next.js App Router TypeScript app under `web/`.
6. Pin exact installed dependencies and one canonical `web/package-lock.json`.
7. Establish explicit build/typecheck/lint/dev validation.
8. Prove reproducible `npm ci`.
9. Prove dev startup and production build.
10. Prove no secret exposure and no source/control damage.
11. Update project_control/evidence.
12. Stop.

---

## 8. Explicit Non-Goals

Do NOT:

```text
create Supabase organization/project
supabase link
install/implement Supabase browser/server client factories unless a scaffold-only package check is explicitly required
apply DB migrations
implement business schema
implement RLS
implement RPC/trusted commands

create/link Vercel project
deploy to Vercel

implement full credential/security/logging boundary
implement Design v1.8 shell
implement recruitment business UI
implement Candidate/Application/Interview/Report behavior

start TASK-S00-003
start TASK-S00-004
start TASK-S00-005
start SLICE-01
```

Pinning/researching a future package is not authorization to implement the future feature.

---

## 9. Application Root Decision

Canonical implementation decision for this task:

```text
APPLICATION_ROOT = web
```

Do not place production code in:

```text
recruitment_webapp/
project_control/
.omp/
.agents/
```

Record the app-root decision in `project_control/DECISION_LOG.md` with rationale:

- isolates deployable application from source authority;
- does not introduce a monorepo framework;
- Vercel can later use `web` as Project Root Directory;
- no EIU behavior changes.

If local repo structure has materially changed and `web/` is no longer safe:

```text
STOP: IMPLEMENTATION_LAYOUT_DRIFT
```

Return evidence; do not silently choose another root.

---

## 10. Package Manager / Runtime Baseline

Selected Planner baseline:

```text
Node.js: 24.20.0 LTS
npm: 11.19.0
package manager: npm
canonical lockfile: web/package-lock.json
```

Before install, re-check current Node/Next official support and security advisories.

At task start, record the actually active host runtime:

```text
node --version
npm.cmd --version    # Windows PowerShell
```

The selected project acceptance baseline remains:

```text
Node.js = 24.20.0
npm = 11.19.0
```

Do **not** upgrade, downgrade, uninstall, or otherwise mutate machine-wide Node/npm
to satisfy Task002. If the exact selected runtime is not already active, use only an
existing verified version manager or an isolated/portable official runtime whose
provenance/checksum can be verified.

Because scaffold generation uses `--skip-install`, a compatible observed Node 24.x
runtime may be used only to generate the initial files. Task002 may not be marked
DONE until the dependency install/lockfile verification, `npm ci`, lint, typecheck,
build, and dev smoke evidence has been produced under the exact selected
Node 24.20.0 + npm 11.19.0 acceptance runtime.

If the exact acceptance runtime cannot be established safely without machine-wide
mutation:

```text
STOP: RUNTIME_VERSION_MISMATCH
```

If no new blocking advisory exists:

```text
web/.nvmrc = 24.20.0

web/package.json:
  packageManager = npm@11.19.0
  engines.node = 24.x
```

Use npm because it is shipped with selected Node LTS, is officially supported by `create-next-app`, avoids adding a new package-manager tool, and supports reproducible `npm ci`.

Only one canonical lockfile may result.

---

## 11. Dependency / Linter Baseline

### 11.1 Rejected baseline

```text
ESLint 9.x
= EOL since 2026-08-06
= NOT APPROVED
```

Do not install or retain ESLint 9 as the final production scaffold linter baseline.

### 11.2 ESLint 10 clean-support gate

Latest independently observed maintained ESLint release during planning:

```text
10.9.1
```

but you must re-check current ESLint v10 at execution.

`eslint-config-next@16.3.4` declares:

```text
eslint >=9.0.0
```

but that is not enough by itself. Current transitive/plugin peer metadata observed by Planner still contains packages whose declared support stops at ESLint 9.

Before choosing ESLint, prove the **actual full generated/current graph** resolves normally with a maintained ESLint 10.x.

Hard forbidden:

```text
--force
--legacy-peer-deps
npm overrides used solely to suppress unsupported peer ranges
```

Decision rule:

```text
IF maintained ESLint 10.x
   + eslint-config-next@16.3.4
   + actual plugin graph
   resolves cleanly under normal npm peer resolution
THEN:
   exact-pin current supported ESLint 10.x
   exact-pin eslint-config-next 16.3.4
   record proof
ELSE:
   DO NOT use ESLint 9
   use the supported Biome path below
```

If neither path is supportable:

```text
STOP: DEPENDENCY_SUPPORT_BLOCK
```

### 11.3 Current expected linter path — Biome

Current Planner-approved expected path:

```text
LINTER = Biome
@biomejs/biome = 2.5.12 exact
```

Next.js officially supports Biome and `create-next-app` exposes `--biome`.

Re-check current supported/patched Biome version immediately before scaffold. If `2.5.12` has been superseded by a relevant current patch, pin the new exact patch and record evidence.

### 11.4 Core Task002 exact pins

```text
next                 16.3.4
react                19.2.8
react-dom            19.2.8
typescript           6.0.3
@types/react         19.2.18
@types/react-dom     19.2.7
@types/node          exact current compatible 24.x patch resolved at execution
```

TypeScript wording:

```text
TypeScript 6.0.3
= intentional compatible TS6 baseline
```

It is **not** a claim that TypeScript 6 is the newest TypeScript major/current latest stable.

Required proof:

```text
npm run typecheck = PASS
npm run build = PASS
```

### 11.5 Feature packages remain deferred

Do not install in Task002:

```text
@supabase/supabase-js
@supabase/ssr
vitest
@playwright/test
```

Supabase packages → Task004.
Vitest/Playwright → Task005.

Supabase DEV remains:

```text
INACTIVE BY DESIGN
UNLINKED
```

throughout Task002.

### 11.6 Exact dependency rules

Final top-level reviewed dependencies are exact, not caret/tilde floating.

Required:

```text
normal npm peer dependency resolution = CLEAN
exactly one web/package-lock.json
npm ci = PASS
npm run lint = PASS
npm run typecheck = PASS
npm run build = PASS
```

No peer-force workaround.

---

## 12. Official Documentation Lookup — mandatory before scaffold

Use `documentation-lookup` and installed version-matched docs.

Verify current:

```text
Node 24 LTS support
Next.js 16 Active LTS and current security patch
create-next-app@16.3.4 options
Next.js Node minimum
Next.js App Router / Server Components
React version paired with selected Next line
TypeScript 6 compatibility; ESLint-10 full peer graph vs Biome support
npm package-manager mechanics
```

For each selected dependency record:

```text
package/tool
exact version
official/primary source
check timestamp/date
support/security conclusion
Task002 need
```

After install, prefer version-matched Next docs under:

```text
web/node_modules/next/dist/docs/
```

for framework-sensitive mechanics.

---

## 13. Scaffold Options

### Windows PowerShell execution rule

Direct runtime evidence in `D:/orca/recruitment` shows bare `npx` resolves to `npx.ps1` and is blocked by Windows ExecutionPolicy.

When the Executor shell is **Windows PowerShell**:

```text
use npx.cmd
use npm.cmd
```

where applicable.

Do **not** modify machine-wide PowerShell ExecutionPolicy merely to run npm/npx.

Equivalent commands in another shell are allowed only when directly verified.

Examples:

```text
npx.cmd -y gitnexus@1.6.10 --version
npm.cmd ci
npm.cmd run build
npm.cmd run typecheck
npm.cmd run lint
npm.cmd audit
```

The separately governed MCP server command may remain its configured executable string; this rule applies to interactive PowerShell command resolution.

### Scaffold command

First run in PowerShell:

```text
npx.cmd create-next-app@16.3.4 --help
```

Current expected path under the planning evidence is Biome.

Use this exact non-interactive PowerShell command:

```text
npx.cmd create-next-app@16.3.4 web --ts --biome --app --src-dir --no-tailwind --no-react-compiler --import-alias "@/*" --empty --use-npm --agents-md --disable-git --skip-install
```

Important exact-CLI notes for `create-next-app@16.3.4`:

- do **not** pass `--turbopack`; this exact CLI selects Turbopack by default when
  `--rspack` is absent;
- `--agents-md` is explicit by design so Next.js can create its version-matched
  managed agent-rule files;
- `--skip-install` is mandatory so the generated template's broad/stale ranges
  are normalized **before the first dependency installation**;
- `--disable-git` prevents a nested repository.

Decisions:

```text
App Router = YES
TypeScript = YES
src/ = YES
Linter = BIOME on current expected path
Tailwind = NO
React Compiler = DEFER
Turbopack = YES, by Next 16.3.4 default (no --rspack)
Next-managed agent files = YES, explicit --agents-md
import alias = @/*
Server Components = DEFAULT
CSS framework = NONE
nested Git init = DISABLED
initial dependency install = SKIPPED UNTIL EXACT PIN NORMALIZATION
```

The exact Next 16.3.4 template generates broader/older package declarations
(including an older Biome patch and a TypeScript range). Because install is skipped,
normalize the reviewed top-level versions before generating the canonical lockfile.

If, during mandatory execution-time re-check, the maintained ESLint-10 **full clean-peer gate** now passes, the Executor may use the equivalent `--eslint --skip-install` path and exact current ESLint 10.x + `eslint-config-next@16.3.4`, with evidence. It may not use ESLint 9.

Do not accept interactive defaults blindly.

`web/AGENTS.md` and `web/CLAUDE.md` generated by the exact Next.js agent-file
mechanism are allowed only if they match the stock/version-matched Next-managed
content and remain subordinate to the repository root governance and EIU source.
Do not manually invent or broaden a second instruction system.

---

## 14. Exact-Pin Procedure

After scaffold and **before the first dependency install**:

1. inspect generated `web/package.json`;
2. verify actual compatibility and current advisories;
3. convert all reviewed top-level dependencies/devDependencies to exact versions;
4. keep exact `next@16.3.4`, `react@19.2.8`, and `react-dom@19.2.8` unless the mandatory security re-check requires a reviewed patch change;
5. set intentional `typescript@6.0.3` compatibility baseline and align `@types/node` to the current compatible Node 24.x exact patch;
6. normalize the selected maintained linter to an exact pin;
7. add/verify explicit `dev`, `build`, `start`, `typecheck`, and `lint` scripts;
8. set `packageManager = npm@11.19.0`, `engines.node = 24.x`, and `web/.nvmrc = 24.20.0`;
9. generate exactly one canonical lockfile with normal peer resolution:
   ```text
   npm.cmd install --package-lock-only
   ```
10. perform the first actual dependency installation reproducibly:
   ```text
   npm.cmd ci
   ```
11. do not use `--force`, `--legacy-peer-deps`, peer-range overrides, or another lockfile merely to suppress incompatibility;
12. record `npm.cmd ls --depth=0`;
13. run the advisory/audit check;
14. run `npm.cmd run lint`, `npm.cmd run typecheck`, and `npm.cmd run build`.

Do not add Supabase, Vitest, Playwright, Tailwind, state libraries, UI kits, or other packages merely because they are popular. Biome is permitted only as the selected lint/static-quality tool under this hotfix.

---

## 15. Required Scripts / Verification

Task002 must have an explicit way to run:

```text
dev
build
typecheck
lint
```

Preferred typecheck:

```text
tsc --noEmit
```

No dedicated test runner is required in Task002.

If no test runner is introduced, report:

```text
TEST_RUNNER_STATUS = DEFERRED_TO_TASK-S00-005
```

Do not create fake domain tests.

---

## 16. Public Repository Security

Repository is PUBLIC.

Assume every committed byte can be read publicly.

Hard rules:

```text
no secrets
no credentials
no access/refresh tokens
no service-role/secret key
no private environment values
no private signed URLs
no internal sensitive values not already authorized for public source
```

Do not create real `.env.local`.

If an env example is not required by the scaffold, defer it.

If a placeholder file is needed later, it must contain placeholders only and must be separately reviewed.

Run a secret scan plus direct diff review before completion.

---

## 17. Source / Control Integrity

Must remain untouched except the explicitly authorized Task002 control-plane changes:

```text
recruitment_webapp/          = NO DIFF
.agents/                     = NO DIFF
AGENTS.md                    = NO DIFF
REVIEW.md                    = NO DIFF
SKILLS.md                    = NO DIFF
SKILLS_LOCK.yaml             = NO DIFF
project_control/             = Task002 state/evidence updates only
.omp/mcp.json                = exact MCP normalization in §22A only
all other .omp/ content      = NO DIFF
```

The `.omp/mcp.json` exception is narrow and mandatory:

```text
project MCP key: gitnexus -> gitnexus-recruitment
project command: preserve npx -y gitnexus@1.6.10 mcp
supabase-dev.enabled = false
Context7 definition = unchanged
Code Review Graph definition = unchanged
no credentials/secrets added
user-level/global MCP config = untouched
```

Required proof:

```text
no unauthorized diff under recruitment_webapp/
source parity/source hash remains unaffected
root execution controls are not overwritten
.omp diff is limited exactly to approved .omp/mcp.json normalization
```

The stock `web/AGENTS.md` / `web/CLAUDE.md` generated by Next.js under `web/`
is application-scaffold output, not permission to modify repository-root governance.

---

## 18. Runtime Metadata Normalization

At task start, re-observe:

```text
local HEAD
origin/main
repository visibility
task worktree
current task
```

Normalize stale runtime fields in project_control without pretending a committed file can forever equal the commit containing itself.

Prefer stable fields:

```text
BASELINE_COMMIT
LAST_COMPLETED_TASK
LAST_RECORDED_HEAD
OBSERVED_ORIGIN_MAIN_AT_TASK_START
OBSERVED_REPOSITORY_VISIBILITY_AT_TASK_START
TASK_WORKTREE
```

Do not create TASK-S00-001A.

Do not rewrite source/business rules.

---

## 19. Project-Control State Transition — Start

After workflow release:

1. run the mandatory three-file YAML machine-parse/repair gate;
2. require `PROJECT_CONTROL_YAML_PARSE = PASS`;
3. verify Task001 remains DONE and Task003 remains PLANNED;
4. only then update Task002 to IN_PROGRESS.

After that preflight, update the task state in the task branch:

```text
TASK_REGISTRY:
  current_task = TASK-S00-002
  TASK-S00-002.status = IN_PROGRESS
  active_prompt = project_control/prompts/SLICE-00_TASK-002_v1.md

SLICE_REGISTRY:
  SLICE-00.status = IN_PROGRESS
  SLICE-00.current_task = TASK-S00-002

CURRENT_STATE:
  current task = TASK-S00-002
  observed origin/main at task start = verified SHA
  visibility = observed actual state
  baseline commit / last completed Task001 retained
  runtime lag normalized

TRACEABILITY_STATUS:
  all 59 business trusted commands remain NOT_STARTED

OPEN_GAPS:
  retain UAT/asset gaps
  update runtime/infrastructure entries to observed truth
  do not classify routine implementation choices as SPEC_GAP

CHANGELOG:
  record Task002 start

DECISION_LOG:
  record APPLICATION_ROOT=web
  record npm/runtime/scaffold baseline decisions
```

---

## 20. Task002 Acceptance Contract

Task-local IDs:

```text
S00-002-AC-01  verified canonical origin/main start
S00-002-AC-02  runtime metadata reconciled without reopening Task001
S00-002-AC-03  app root decision recorded
S00-002-AC-04  dependency support/advisory evidence recorded
S00-002-AC-05  exact acceptance runtime/framework/package-manager baseline pinned; required install/ci/lint/typecheck/build/dev evidence runs under Node 24.20.0 + npm 11.19.0 without machine-wide runtime mutation
S00-002-AC-06  exactly one canonical app lockfile
S00-002-AC-07  Next App Router TS scaffold under web/
S00-002-AC-08  npm ci clean install succeeds
S00-002-AC-09  production build succeeds
S00-002-AC-10  explicit typecheck succeeds
S00-002-AC-11  lint succeeds
S00-002-AC-12  local dev startup responds
S00-002-AC-13  secret scan/direct review finds no credentials
S00-002-AC-14  recruitment_webapp remains unchanged/hash-safe
S00-002-AC-15  project/root controls remain intact; `.omp/` diff is limited to the authorized `.omp/mcp.json` normalization
S00-002-AC-16  no Supabase resource/link/migration mutation
S00-002-AC-17  no Vercel project/link/deployment mutation
S00-002-AC-18  no recruitment business feature/trusted command implementation
S00-002-AC-19  TASK-S00-003 remains NOT_STARTED/PLANNED
S00-002-AC-20  project_control/evidence updated + exactly one NEXT_ACTION
S00-002-AC-21  direct diff + REVIEW.md + eiu-code-review + verification-before-completion pass
S00-002-AC-22  project `.omp/mcp.json` normalized persistently: `gitnexus-recruitment` exact 1.6.10 command + `supabase-dev.enabled=false`; GitNexus runtime evidence used only if non-ambiguous/tested
S00-002-AC-23  CRG package-pin evidence records `code-review-graph 2.3.8` and does not confuse MCP server label 3.4.7 with package version
S00-002-AC-24  Supabase DEV remains INACTIVE / UNLINKED throughout Task002
S00-002-AC-25  PROJECT_CONTROL_YAML_PARSE = PASS for TASK_REGISTRY.yaml, EVIDENCE_INDEX.yaml, and SLICE_REGISTRY.yaml before Task002 becomes IN_PROGRESS
S00-002-AC-26  maintained linter support gate passes: clean ESLint 10.x graph OR current supported Biome; no ESLint 9, --force, --legacy-peer-deps, or peer-suppression workaround
S00-002-AC-27  Windows PowerShell uses `.cmd` npm/npx launchers or a directly verified equivalent shell, with no machine-wide ExecutionPolicy change
```

Any failed required acceptance keeps Task002 non-DONE.

---

## 21. Test / Evidence Boundary

Do not force business TDD.

Use test-first only if you introduce custom foundation invariants that warrant it.

Required checks:

```text
npm.cmd ci                         # Windows PowerShell
npm.cmd run build                  # Windows PowerShell
npm.cmd run typecheck              # Windows PowerShell
npm.cmd run lint                   # Windows PowerShell
dev startup smoke
npm.cmd audit / advisory check     # Windows PowerShell
secret scan
git diff --check
source/control integrity check
```

No fake Candidate/HR domain tests.

---

## 22. Skill Routing

Use only as needed:

```text
documentation-lookup
architecture-decision-records
security-review
react-patterns
diagnosing-bugs
eiu-code-review
verification-before-completion
```

Potentially relevant global reuse:

```text
vercel-react-best-practices
vercel-composition-patterns
```

For Task002, `react-testing` and `tdd` are optional and should not be invoked merely because installed.

Do not reference obsolete/raw skill aliases from superseded Planner artifacts.

---


## 22A. MCP Runtime Preflight — mandatory before graph-assisted evidence

The canonical OMP runtime has the following independently verified mechanics:

### Context7

```text
CONNECTED
Server: Context7 v4.0.5
Tools:
- resolve-library-id
- query-docs
```

Use it only to support current documentation lookup. It never overrides EIU source authority.

### Code Review Graph

Pinned package version:

```text
code-review-graph 2.3.8
```

Independent verification command:

```text
uvx --from code-review-graph==2.3.8 code-review-graph --version
```

Restricted project MCP exposes exactly:

```text
get_minimal_context_tool
query_graph_tool
detect_changes_tool
get_review_context_tool
get_architecture_overview_tool
list_graph_stats_tool
```

Important:

```text
/mcp test code-review-graph may display:
Server version 3.4.7
```

Do **not** treat that MCP server label as the package version. Package-pin evidence is the explicit package command above.

### GitNexus name collision

Exact Recruitment project package pin:

```text
npx.cmd -y gitnexus@1.6.10 --version
→ 1.6.10
```

Current collision:

```text
user-level MCP name:
gitnexus
→ 1.6.9

project-level MCP name:
gitnexus
configured command:
npx -y gitnexus@1.6.10 mcp
```

Because same-name resolution currently routes `/mcp test gitnexus` to the user-level 1.6.9 server:

```text
MCP_GITNEXUS_NAME_COLLISION = CONFIRMED
```

### Required project MCP normalization inside Task002 preflight

Do **not** create a separate setup task. This is an authorized Task002
control-plane correction and must be persisted in the task branch.

Normalize the project `.omp/mcp.json` **before graph-assisted evidence** and before
claiming MCP preflight complete:

```text
1. Preserve user-level/global `gitnexus` unchanged.
2. Rename the Recruitment project MCP server only:
     gitnexus
   → gitnexus-recruitment
3. Preserve exact project command:
     npx -y gitnexus@1.6.10 mcp
4. Persist:
     supabase-dev.enabled = false
5. Leave Context7 definition unchanged.
6. Leave Code Review Graph definition unchanged.
7. Verify no credential/secret was introduced.
8. Re-read the resulting project config and record the diff.
```

Then attempt:

```text
/mcp list
/mcp test gitnexus-recruitment
```

Preferred runtime result:

```text
project gitnexus-recruitment = connected
Server: gitnexus v1.6.10
supabase-dev = inactive
```

OMP MCP reload/rebinding has previously shown session-level reporting instability.
Therefore:

- if `gitnexus-recruitment` tests PASS, it may be used only after its normal graph
  freshness gate;
- if the config normalization is correct but active-session rebinding/test remains
  unreliable, classify:
  ```text
  MCP_RUNTIME_BINDING = DEGRADED_NOT_BLOCKING
  GitNexus = UNAVAILABLE_FOR_TASK_EVIDENCE
  fallback = direct source + LSP/search
  ```
  and do not use GitNexus evidence;
- do **not** repeatedly reload/re-authenticate merely to obtain ceremonial graph
  evidence for this localized task.

Do not use ambiguous/stale GitNexus output.

### Supabase DEV runtime state

```text
Supabase DEV = INACTIVE BY DESIGN
```

For Task002, this state must be represented persistently in project `.omp/mcp.json`:

```text
supabase-dev.enabled = false
DO NOT enable
DO NOT authenticate
DO NOT create/link DEV project
```

Activation belongs to TASK-S00-003 after a real DEV `project_ref` exists.


## 23. Graph Routing / Freshness

```text
known/local scaffold
→ direct source + LSP

broad/unfamiliar discovery
→ CRG after freshness gate

exact caller/callee/blast radius
→ `gitnexus-recruitment` only after MCP name-collision normalization + freshness gate

final implementation decision
→ direct source

final review
→ direct diff + tests + REVIEW.md + eiu-code-review
```

Graphify:

```text
DORMANT / FUTURE_OPTIONAL / DO NOT INVOKE
```

Because repository HEAD has advanced since previous graph evidence, before the **first graph query used as evidence**:

- verify CRG freshness; refresh only if needed;
- verify `gitnexus status`; refresh `analyze --index-only` only if needed.

If no graph evidence is needed for this localized task:

```text
CRG = NOT_NEEDED
GitNexus = NOT_NEEDED
```

That is preferred over ceremonial graph refresh.

---

## 24. Recommended Commit / Review Boundaries

The Planner/Orca-assigned task branch/worktree is the only authorized write surface.

Executor may create scoped **local task-branch commits** required to preserve Task002
evidence. This release does not authorize:

```text
direct commits to main
force-push
self-merge
deployment
Supabase/Vercel resource mutation
```

Remote task-branch push / PR creation occurs only if the surrounding Planner/Orca
workflow has explicit repository-write authorization for that action. Otherwise,
stop after local commit evidence and return control to Planner.

Recommended commits:

```text
1. chore(TASK-S00-002): reconcile runtime state and record scaffold decisions
2. feat(TASK-S00-002): scaffold pinned Next.js web application
3. chore(TASK-S00-002): record verification evidence and task state
```

Before PR/merge gate:

```text
npm ci
build
typecheck
lint
dev smoke
security/advisory scan
secret scan
diff/source-integrity checks
direct review
eiu-code-review
verification-before-completion
```

Do not self-merge solely because CI is green.

---

## 25. Evidence Required in Completion Report

Return:

```text
TASK ID
SOURCE BASELINE/HASH
STARTING ORIGIN/MAIN SHA
LOCAL START SHA
TASK BRANCH
WORKTREE
APPLICATION ROOT
NODE/NPM BASELINE
DEPENDENCY TABLE WITH EXACT INSTALLED VERSIONS
PACKAGE.JSON PINNING STATUS
LOCKFILE PATH + HASH
SCAFFOLD COMMAND + OPTIONS
OFFICIAL DOCS/ADVISORIES CONSULTED
PROJECT_CONTROL_YAML_PARSE RESULT
LINTER SUPPORT / PEER-RESOLUTION DECISION EVIDENCE
NPM CI RESULT
NPM AUDIT/SECURITY RESULT
BUILD RESULT
TYPECHECK RESULT
LINT RESULT (`npm run lint`; current supported Biome path or clean maintained ESLint-10 path)
DEV STARTUP RESULT
TEST RUNNER STATUS
SECRET SCAN RESULT
GIT DIFF --CHECK
DIFF STAT
CHANGED-FILE CLASSIFICATION
SOURCE AUTHORITY INTEGRITY
CONTROL-PLANE INTEGRITY
CRG STATUS / NOT_NEEDED
CRG PACKAGE PIN VERIFICATION IF USED
GITNEXUS STATUS / NOT_NEEDED
MCP PROJECT CONFIG NORMALIZATION RESULT (MANDATORY)
GITNEXUS RUNTIME TEST / NOT_USED
SUPABASE DEV STATE = INACTIVE / UNLINKED
WINDOWS POWERSHELL COMMAND-RESOLUTION EVIDENCE IF POWERSHELL USED
EIU-CODE-REVIEW RESULT
COMMIT SHAS
PR URL/NUMBER IF CREATED
PROJECT_CONTROL UPDATES
TASK-S00-003 STATUS
OPEN GAPS
EXACTLY ONE NEXT_ACTION
```

Pre-code source validators must not be presented as implementation correctness proof.

---

## 26. Project-Control State Transition — Completion

Only if every required Task002 acceptance passes:

```text
TASK-S00-002 = DONE
TASK-S00-001 remains DONE
TASK-S00-003 remains PLANNED / NOT_STARTED

SLICE-00 remains IN_PROGRESS or READY_FOR_NEXT_TASK
TRACEABILITY_STATUS trusted commands remain NOT_STARTED
EVIDENCE_INDEX records Task002 scaffold proof
CURRENT_STATE records last completed Task002 and stable repository references
CHANGELOG records Task002 completion
```

Exactly one next action:

```text
NEXT_ACTION:
Return Task002 evidence/repository state to Planner for rehydration and TASK-S00-003 planning.
```

Do NOT start TASK-S00-003.

---

## 27. Stop Conditions

Stop and report, without guessing, on:

```text
BLOCKED: SPEC_GAP
STATE_INCONSISTENCY
WORKTREE_NOT_ASSIGNED
WORKTREE_WRITE_CONFLICT
RUNTIME_VERSION_MISMATCH
IMPLEMENTATION_LAYOUT_DRIFT
DEPENDENCY_SECURITY_BLOCK
DEPENDENCY_SUPPORT_BLOCK
SOURCE_AUTHORITY_DRIFT
MCP_RUNTIME_AMBIGUITY_IF_GRAPH_EVIDENCE_IS_REQUIRED
WORKFLOW_RELEASE_HASH_MISMATCH
WORKFLOW_RELEASE_NOT_APPROVED
```

A normal implementation mechanics choice is not a SPEC_GAP.

---

## 28. Final Execution Boundary

This exact prompt is independently reviewed and released only for TASK-S00-002.

Before execution, Planner must:

```text
1. verify the SHA-256 of this exact prompt against
   INDEPENDENT_REVIEW_RELEASE_TASK_S00_002.md;
2. create/assign the Orca task worktree/branch;
3. dispatch this exact prompt, unmodified, to OMP Executor inside that worktree.
```

If any of those conditions is false:

```text
STOP: WORKFLOW_RELEASE_NOT_APPROVED
```

Do not start TASK-S00-003.
