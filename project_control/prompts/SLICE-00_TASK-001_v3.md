# EXECUTOR_PROMPT_SLICE_00.md (TASK-S00-001 Execution Prompt)

## EXECUTOR PROMPT — TASK-S00-001 Baseline Establishment & Verification

### 0. Execution Authorization & Distinct Gates

```text
BASELINE_ZIP: App_Tuyen_Dung_EIU_Full_Handover_v1.17.zip
BASELINE_SHA256: 0b39c3615dd5b34e998527a1d273e0b846458c7bd4170be46c9bb670bfcb3498
BUSINESS_STATUS: Business Logic Core v1.2 = FROZEN
TECHNICAL_STATUS: Technical Architecture v1.17 = TECHNICAL SPECIFICATION FROZEN
IMPLEMENTATION_GATE: READY TO IMPLEMENT
SOURCE_ROOT: recruitment_webapp
SOURCE_PARITY_GATE: PASS (87/87 current-required paths 100% hash verified)

WORKFLOW_RELEASE_TOKEN: PENDING_INDEPENDENT_REVIEW
WORKFLOW_RELEASE_SCOPE: TASK-S00-001
WORKFLOW_RELEASE_PROMPT: project_control/prompts/SLICE-00_TASK-001_v3.md
FIRST_BASELINE_COMMIT_AUTHORIZATION: PENDING_EXPLICIT_USER_AUTHORIZATION

EXECUTOR_PACK: EIU Recruitment Implementation Executor Pack v1.3.2
```

**Hard Two-Gate Workflow Hold:**
Execution of `TASK-S00-001` and the creation of the first baseline Git commit require TWO independent approvals:
1. `WORKFLOW_RELEASE_TOKEN: APPROVED_FOR_EXECUTOR` (authorizes this exact prompt and task scope).
2. `FIRST_BASELINE_COMMIT_AUTHORIZATION: APPROVED` (explicit user authorization to create the first Git commit).

Do **not** create a Git commit while either token is pending. Do not self-release either token.

---

### 1. Task Scope & Strict Task Isolation

You are the Coding Executor for **strictly TASK-S00-001**:
`Finalize canonical pre-implementation repository baseline, verify source parity, materialize persistent project-control state, and establish the first Git baseline`

#### Explicit Non-Goals (Belong to Later Tasks):
- DO NOT create `package.json` or choose dependencies (TASK-S00-002).
- DO NOT scaffold Next.js App Router (TASK-S00-002).
- DO NOT provision Supabase project or write database migrations (TASK-S00-003).
- DO NOT configure CI or link Vercel (TASK-S00-003).
- DO NOT implement credential boundaries, trusted commands, or logging (TASK-S00-004).
- DO NOT implement Design v1.8 shell or accessibility harness (TASK-S00-005).
- DO NOT implement business feature commands or application logic.
- Master planning reference for later tasks is preserved in `SLICE-00_MASTER_PLAN_REFERENCE.md`.

---

### 2. Multi-Agent & Worktree Ownership Contract

- **ONE WRITER PER WORKTREE:** Multiple writing agents concurrently touching the same worktree is strictly prohibited.
- **Orca owns:** Worktree lifecycle, orchestration DAGs, terminal handoffs, and embedded browser QA.
- **OMP owns:** In-worktree code implementation, LSP navigation, tests, and watchdog review.

---

### 3. Source Root Portability Hard Rule

- **SOURCE_ROOT:** `recruitment_webapp`
- All Full Handover paths (`START_HERE.txt`, `review_pack/...`, `design_system/...`, `responsive_prototype/...`) resolve relative to `SOURCE_ROOT = recruitment_webapp`, never the repository root.
- If any required authority file cannot be resolved under `SOURCE_ROOT`:
  `STOP: SOURCE_ROOT_INCONSISTENCY`

---

### 4. Graph Intelligence & Freshness Contracts (v2.4)

- **Direct Source + LSP:** Primary implementation evidence for localized work.
- **Code Review Graph (2.3.8):** Broad discovery and diff triage only (restricted MCP allowlist).
- **GitNexus (1.6.10):** Precise symbol, caller/callee, and blast-radius analysis (`indexOnly: true`).
- **Freshness Hard Gate:** Check freshness before first query (`code-review-graph status` / `gitnexus status`).
- **Database Authority:** Direct SQL + declarative schema + ordered migrations + tests. Graphs are non-authoritative for database behavior.
- **SQL Absence Rule:** Never conclude an object is missing based on graph absence alone.

---

### 5. Step-by-Step Task001 Execution Procedure

1. **Resume & Re-observe Canonical Repository:**
   - Verify `D:/orca/recruitment`.
   - Verify `git branch --show-current == main`.
   - Verify `git rev-parse HEAD` returns `UNBORN`.
   - Verify `git remote -v` is empty (`origin = NONE`).
   - Verify `SOURCE_ROOT = recruitment_webapp` exists and is portable.

2. **Verify Pre-Commit Gates:**
   - Verify `SOURCE_PARITY_GATE = PASS` (87/87 paths match Full Handover v1.17).
   - Read the current expected staged baseline from project_control/CURRENT_STATE.md, independently count the actual staged paths from Git, and require exact equality before commit.
   - Verify staged secret scan passes (zero literal credentials, private keys, or tokens).
   - Verify `project_control/` is consistent with live repository facts.

3. **Check Authorizations Before Commit:**
   - Confirm `WORKFLOW_RELEASE_TOKEN == APPROVED_FOR_EXECUTOR`.
   - Confirm `FIRST_BASELINE_COMMIT_AUTHORIZATION == APPROVED`.
   - If either authorization is missing: STOP and report pending gate. Do NOT commit.

4. **Execute First Baseline Commit (Once Authorized):**
   - Execute:
     ```bash
     git commit -m "chore(baseline): initialize EIU Recruitment canonical v2.4 repository foundation"
     ```
   - Verify new real `HEAD` commit SHA via `git rev-parse HEAD`.

5. **Post-Commit Synchronization & Refresh:**
   - Refresh Code Review Graph:
     ```bash
     code-review-graph update
     code-review-graph status
     ```
   - Refresh GitNexus index:
     ```bash
     npx -y gitnexus@1.6.10 analyze --index-only
     npx -y gitnexus@1.6.10 status
     ```
   - Update `project_control/CURRENT_STATE.md` with:
     - `HEAD: <actual commit SHA>`
     - `Baseline Commit: COMMITTED (<actual commit SHA>)`
     - `Task Status: DONE`
     - `NEXT_ACTION: prepare and review TASK-S00-002 prompt (Dependency Selection & Next.js Scaffold)`
   - Record commit SHA in `project_control/TASK_REGISTRY.yaml` and `EVIDENCE_INDEX.yaml`.
   - Update `project_control/CHANGELOG_IMPLEMENTATION.md`.

6. **STOP & Report:**
   - Do NOT proceed to TASK-S00-002.
   - Do NOT create a GitHub remote.
   - Hand off to reviewer/user with commit SHA and refreshed graph status.

---

### 6. Definition of Done (TASK-S00-001)

```text
[ ] Canonical repository root and main branch verified
[ ] SOURCE_ROOT (recruitment_webapp) and portability verified
[ ] SOURCE_PARITY_GATE verified PASS (87/87)
[ ] Actual staged path count equals CURRENT_STATE expected staged baseline
[ ] Staged secret scan verified clean
[ ] Both authorization gates (Workflow Release & Commit Auth) verified prior to commit
[ ] First baseline commit created on main branch
[ ] Real HEAD commit SHA captured and recorded in project_control
[ ] CRG graph refreshed for real HEAD
[ ] GitNexus index refreshed and verified up-to-date
[ ] project_control/CURRENT_STATE.md and registries updated
[ ] Exactly one NEXT_ACTION recorded
```
