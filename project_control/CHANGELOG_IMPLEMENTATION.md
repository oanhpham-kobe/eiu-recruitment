# Implementation Changelog

## 2026-09-03 — Bootstrap prepared by Planner

- No production repository/code exists in this Planner phase.
- Prepared persistent project-control bootstrap for first Slice00 commit.
- Source baseline pinned to Full Handover v1.17.
- Next action is independent review, not coding.

## 2026-09-04 — Source Parity Closure v1.3.1
- Reconciled canonical `recruitment_webapp/` losslessly against Full Handover v1.17 (`0b39c361...`).
- Preserved legacy v1.8 files in external backup `recruitment-source-pre-v1.17-sync-20260904-004739`.
- Source Parity Gate evaluated: 87/87 current-required paths PASS (0 missing, 0 mismatches, 0 unknown extras).
- Closed gap SOURCE-PARITY-001.

## 2026-09-04 — TASK-S00-001 First Baseline Commit Created
- Created first canonical Git baseline commit on `main`: `cdd1ea3` (`cdd1ea3e94dbedb6a1b880efd366759bcac1024d`).
- Commit message: "chore: establish EIU Recruitment baseline" (531 files, 78,277 insertions).
- Verified real HEAD: `cdd1ea3e94dbedb6a1b880efd366759bcac1024d`.
- Refreshed Code Review Graph 2.3.8 against real HEAD (`CRG_CURRENT_FOR_HEAD = PASS`).
- Refreshed GitNexus 1.6.10 against real HEAD (`GITNEXUS_CURRENT_FOR_HEAD = PASS`).
- Set TASK-S00-001 status to `IMPLEMENTATION_COMPLETE_PENDING_STATE_CLOSURE_REVIEW`.
- NEXT_ACTION: obtain Task001 post-commit state-closure review.

## 2026-09-04 — TASK-S00-001 State Closure
- TASK-S00-001 baseline established.
- Baseline SHA `cdd1ea3e94dbedb6a1b880efd366759bcac1024d` independently reviewed and accepted.
- Source parity closed (87/87 current-required paths 100% hash verified).
- CRG refreshed against baseline commit (`CRG: CURRENT_FOR_BASELINE_HEAD`).
- GitNexus refreshed against baseline commit (`GitNexus: CURRENT_FOR_BASELINE_HEAD`).
- Task001 state closure completed (status: `DONE`).
- Next action: Obtain explicit authorization to create the private GitHub repository, configure origin, and push main.

## 2026-09-04 — Repository Publication Gate (oanhpham-kobe/eiu-recruitment)
- Created private GitHub repository `oanhpham-kobe/eiu-recruitment`.
- Verified repository visibility: `PRIVATE`.
- Configured local origin to `https://github.com/oanhpham-kobe/eiu-recruitment.git`.
- Pushed canonical branch `main` (`d5d5640fdc59aeb224f08c20d38e0450fef5dfd5`).
- Verified remote HEAD equality: `local HEAD == origin/main == refs/heads/main == d5d5640fdc59aeb224f08c20d38e0450fef5dfd5`.
- Next action: Hand control to Planner to prepare and review TASK-S00-002.

## 2026-09-04 — TASK-S00-002 Started (Dependency Baseline + Next.js App Router Scaffold)
- Verified independent review PASS on `SLICE-00_TASK-002_v1.md` with release token `APPROVED_FOR_EXECUTOR`.
- Preserved released prompt copy at `project_control/prompts/SLICE-00_TASK-002_v1.md` (hash verified: `74032857f5b403e61a8939c690a0d11aadfdc2b8d949681746f4c6240bd82117`).
- Executed mandatory YAML machine-parse preflight with PyYAML on `TASK_REGISTRY.yaml`, `EVIDENCE_INDEX.yaml`, and `SLICE_REGISTRY.yaml`. Repaired syntax anomalies (`PROJECT_CONTROL_YAML_PARSE = PASS`).
- Verified initial task state: `TASK-S00-001 = DONE`, `TASK-S00-002 = PLANNED`, `TASK-S00-003 = PLANNED`.
- Normalized `.omp/mcp.json`: renamed project server `gitnexus` -> `gitnexus-recruitment`, set `supabase-dev.enabled = false`.
- Established isolated official Node.js 24.20.0 LTS and npm 11.19.0 acceptance runtime (SHA-256: `6cac9ffbca8f6a47091e4b5c772e0606049c3871cb67d900c0cedde630e545ba`).
- Promoted TASK-S00-002 to `IN_PROGRESS`.

## 2026-09-04 — TASK-S00-002 Completed (Next.js App Router Scaffold + Pinned Dependencies)
- Scaffolded minimal Next.js App Router TypeScript application under `web/` using `create-next-app@16.3.4` with `--ts`, `--biome`, `--app`, `--src-dir`, `--no-tailwind`, `--no-react-compiler`, `--import-alias "@/*"`, `--empty`, `--use-npm`, `--agents-md`, `--disable-git`, `--skip-install`.
- Pinned exact dependencies in `web/package.json`:
  - `next`: `16.3.4`
  - `react`: `19.2.8`
  - `react-dom`: `19.2.8`
  - `@biomejs/biome`: `2.5.12`
  - `typescript`: `6.0.3`
  - `@types/react`: `19.2.18`
  - `@types/react-dom`: `19.2.7`
  - `@types/node`: `24.13.3`
- Established `packageManager = npm@11.19.0`, `engines.node = 24.x`, and `web/.nvmrc = 24.20.0`.
- Generated canonical `web/package-lock.json` via clean peer resolution (`SHA-256: 2408b7b3b2ac53707719d8121fb6fd4fa57d25f6b5ce638f502984879584eb60`).
- Verified `npm ci` clean install (29 packages added cleanly).
- Verified `npm run lint` (`biome check` 6 files, 0 fixes, clean pass).
- Verified `npm run typecheck` (`tsc --noEmit` exit 0).
- Verified `npm run build` (`next build` compiled and prerendered static routes).
- Verified local dev startup smoke (port 3001, HTTP/1.1 200 OK).
- Verified production startup smoke (`next start`, port 3002, HTTP/1.1 200 OK).
- Verified secret scan: 0 credentials or secrets found.
- Verified source authority integrity: `recruitment_webapp/` completely untouched (0 diff).
- Verified root governance integrity: `.agents/`, `AGENTS.md`, `REVIEW.md`, `SKILLS.md`, `SKILLS_LOCK.yaml` untouched (0 diff).
- Verified React Doctor scan: Score 100/100, 0 issues.
- Updated project control: `TASK-S00-002 = DONE`, `TASK-S00-003 = PLANNED`.
- Next action: Return Task002 evidence/repository state to Planner for rehydration and TASK-S00-003 planning.

## 2026-09-04 — TASK-S00-003 Completed (DEV Infrastructure: Supabase DEV + Migration Foundation + Vercel Linking)
- Verified owner authorization for autonomous DEV-only infrastructure execution.
- Created Orca task worktree at `D:/orca/recruitment/TASK-S00-003-dev-infra` on branch `oanhpham-kobe/TASK-S00-003-dev-infra` from canonical baseline HEAD `eb64e381d9d86825b194df525ceed8e4930f30c2`.
- Authenticated and inspected Supabase CLI environment: account `oanhpham-kobe` (`oanh.pham@eiu.edu.vn`).
- Inspected organizations; created organization `EIU Recruitment` (`clfvovtyobekjaevdewe`).
- Provisioned dedicated Supabase DEV project:
  - Project name: `eiu-recruitment-dev`
  - Project ref: `yrjclhdvjlekwvfeczcj`
  - Region: `ap-southeast-1` (Singapore, nearest supported Southeast Asia region for Vietnam)
  - Engine: PostgreSQL 17.6.1.166
  - Status: `ACTIVE_HEALTHY`
- Linked repository worktree to Supabase DEV via `supabase link --project-ref yrjclhdvjlekwvfeczcj` (explicitly distinguished from local config `project_id = "eiu-recruitment-dev"` in `supabase/config.toml`). Verified link read-only with `supabase projects list` (`linked: true`).
- Audited ephemeral worktree-local secret and link files: `web/.env.local`, `.vercel/`, `web/.vercel/`, `supabase/.temp/` are 100% gitignored and uncommitted. Zero credentials committed.
- Verified billing/plan status: `NOT_OBSERVABLE` via read-only management endpoints; zero paid upgrade performed (`paid_upgrade_performed: false`).
- Established migration foundation:
  - Created `supabase/migrations/20260904164112_initial_foundation.sql`.
  - Enabled extensions `pgcrypto`, `citext`, `pg_trgm`, `unaccent` under `extensions` schema.
  - Created `private` schema with strict access revokes from `public`, `anon`, and `authenticated`.
  - Implemented `private.touch_version()` trigger function with `SECURITY DEFINER` and empty `search_path`.
- Applied migrations to Supabase DEV via `supabase db push --linked`.
- Tested local clean migration replay via `supabase start` and `supabase db reset`: verified as `BLOCKED` because Docker daemon is unavailable on host (`LegacyDockerLifecycleInspectError` at `//./pipe/dockerDesktopLinuxEngine`).
- Verified remote migration convergence and idempotency (`supabase db push --linked` reports remote database is up to date; all migrations applied in timestamp order).
- Verified database schema contracts and trigger behavior via direct SQL assertions against linked DEV database.
- Authenticated and inspected Vercel CLI environment: account `oanhpham-kobe` (`kobe17`).
- Created and configured Vercel project:
  - Project name: `eiu-recruitment` (ID: `prj_9t5t1RBtgZp4hOLuSgEYgv5nt8qY`)
  - Root directory: `web`
  - Framework preset: `nextjs`
  - Node version: `24.x`
- Linked repository worktree and `web/` to Vercel project via `vercel link --yes --project eiu-recruitment`.
- Preserved explicit non-deployment boundary: Vercel deployment was `NOT_PERFORMED`.
- Updated `.omp/mcp.json` to enable `supabase-dev` with `read_only=true` scoped to project `yrjclhdvjlekwvfeczcj`.
- Verified source authority integrity: `recruitment_webapp/` remains 100% byte-identical to baseline.
- Updated project control: `TASK-S00-003 = DONE`, `TASK-S00-004 = PLANNED`.
- Next action: Return Task003 evidence and repository state to Planner for TASK-S00-004 planning.

## 2026-09-08 — Accepted implementation reconciliation through TASK-S04-005

This compact backfill records accepted checkpoints that were already present in Git, task/evidence registries, review records, and exact-SHA CI, but were missing from this chronological narrative. It does not reopen accepted implementation.

- `SLICE-00`: DONE through `TASK-S00-005` (foundation shell/runtime/security baseline accepted).
- `SLICE-01`: DONE through `TASK-S01-005` (identity/auth/provisioning/login accepted).
- `SLICE-02`: DONE through `TASK-S02-005` (candidate form/submission/privacy/document portal accepted).
- `SLICE-03`: DONE through `TASK-S03-006` (HR inbox/application/detail/bulk lifecycle accepted).
- `TASK-S04-001`: DONE — Interview round/schedule schema, conflict locking, participant data model.
- `TASK-S04-002`: DONE — Interview/report lifecycle trusted commands, participant/schedule mutations, document-storage foundations, derived views.
- `TASK-S04-003`: DONE — dedicated atomic `copy_interview_schedule` trusted command.
- `TASK-S04-005`: DONE — application reactivation and participant public-contract repair.
- `TASK-S04-004` was intentionally not dispatched after its prompt review identified the missing S04-005 contract repair.
- Latest accepted application implementation SHA: `ab6c5194d15eb29e2ee285106c6bef14f0291ec3`.
- Latest verified application integration checkpoint: `8819d9fec1143e94aea7721e47ae84a8abcd82b9`.
- Exact integration CI run: `34039979411` — PASS.
- Workspace/worktree maintenance completed after S04-005 and is no longer an implementation stop reason.
- Source-to-implementation-to-plan reconciliation started before releasing S04-004. No canonical Business Logic v1.2 / Technical Architecture v1.18 reopening was identified by the read-only audit that triggered this reconciliation.


## 2026-09-08 — S04-005 source-to-plan reconciliation released

- Reconciled task/slice/runtime/traceability/downstream prerequisite state against Full Handover v1.18 and accepted implementation through TASK-S04-005.
- Confirmed no canonical Business Logic v1.2 / Technical Architecture v1.18 reopening is required.
- Initial S04-004 v2 reconciliation review found two blocking prompt defects: omitted accepted migration `20260906060000_interview_schema_and_conflict_locking.sql` from the effective backend chain and ambiguous idempotency retry-key wording.
- Repaired both defects in `project_control/prompts/SLICE-04_TASK-004_v3.md` (`ae622650bd9d79af28c30a870f2c84d15aeac764ab4393cd5f7b343040b9c7ce`).
- Exact-source v3 re-review at reconciliation review head `a4d85a9033b3b54195265a893710d08a626ef9bb`: PASS, blockers NONE.
- Released `TASK-S04-004` to READY and materialized it as the sole safe-frontier task.


## 2026-09-08 — Review, checkpoint, CI-economy, and safe-handoff protocol

- Formalized producer self-review followed by separate read-only OMP exact-SHA review; producer self-review is not independent acceptance evidence.
- OMP main session owns review-artifact persistence on non-candidate evidence branches plus immutable pre-task/accepted checkpoint refs; if serialized integration changes SHA, a targeted final exact-SHA OMP acceptance re-review binds the final review SHA, CI SHA, and accepted-checkpoint SHA.
- Independent review waves may contain up to two dependency-independent candidates with separate verdicts; downstream work cannot consume an unaccepted dependency.
- Formalized targeted repair verification: unrelated prior PASS areas remain closed unless changed code/dependency/shared invariant or concrete regression evidence reopens them.
- Integration CI now resolves impacted web/database domains before dispatching expensive jobs; `[full-ci]` only broadens scope for explicit slice/shared-contract gates.
- Removed unused Playwright Chromium installation from normal Integration CI; browser QA remains an explicit task/slice verification concern.
- Added safe context-pressure/cross-session handoff rule using Git + existing durable authorities + CURRENT_STATE, without creating a second memory/state authority.


## 2026-09-08 — Design-System production hardening implementation complete

- Completed bounded TASK-DS-001..006 without reopening frozen Product/Business/Design authority.
- Converged runtime design tokens, Auth/Candidate/Internal shell responsibilities, responsive Internal navigation, bounded shared UI primitives, existing responsive production surfaces, static production design-contract validation, and seven-width browser acceptance.
- Preserved the accepted Application/Interview backend contracts; no Supabase migration/RLS/RPC changes were made.
- Final self-review repaired Candidate landmark ownership plus StatusMenu keyboard semantics and re-entrant/topmost overlay focus/lock behavior.
- Focused verification remained impact-scoped; unrelated database verification was not rerun.
- Phase A intentionally keeps TASK-S04-004 blocked until immutable checkpoint/design-system-production-ready-001 is created and verified.
