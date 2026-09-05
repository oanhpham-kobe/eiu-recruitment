# OPEN_GAPS

## Blocking specification conflicts

**NONE known in CURRENT/NORMATIVE Full Handover v1.17.**

The v1.16 independent-review P0 was source-synced in v1.17:
- `copy_interview_schedule` is explicit in `app_spec.schedule_conflicts.engine_used_by`;
- `48_IDEMPOTENCY_CONCURRENCY_SPEC.md` explicitly includes Save Copy in the shared Candidate/Room/Interviewer engine;
- stable Copy Browser-QA IDs `RP-COPY-01..04` resolve to current evidence;
- used target Round1 -> next legal round is explicitly tested;
- All-in-One current label is v1.17.

## WORKFLOW-001 — Independent prompt review

**Type:** WORKFLOW_RELEASE_HOLD  
**Status:** `RESOLVED_FOR_TASK_002`.
**Evidence:** Prompt `SLICE-00_TASK-002_v1.md` independently reviewed (`PASS`), hash verified (`74032857f5b403e61a8939c690a0d11aadfdc2b8d949681746f4c6240bd82117`), released with token `APPROVED_FOR_EXECUTOR`, and stored in `project_control/prompts/SLICE-00_TASK-002_v1.md`.
## UAT-001 — Owner Visual UAT

**Type:** RELEASE_UAT_HOLD  
**Affected:** final visual sign-off / later UI slices / Production UAT.  
**Status:** Responsive Prototype v1.10 is READY FOR OWNER VISUAL UAT / NOT FROZEN.  
**Safe work:** Slice00 Foundation may proceed after workflow release.

## ASSET-001 — Official PDF owner template

**Type:** NON_BLOCKING_ASSET_GAP  
**Affected:** Slice05 PDF pixel-perfect owner sign-off only.  
**Rule:** implement report data/permissions/logic from source; do not invent the official final template.

## Historical Gap Resolutions

### EXEC-001 — Target production repository/workspace
**Status:** `RESOLVED`  
**Evidence:** Canonical repository `D:/orca/recruitment` is directly observed in Orca 1.4.196 / OMP 18.1.6 runtime. Git is initialized on `main` branch; canonical runtime is operational with Code Review Graph 2.3.8 and GitNexus 1.6.10.

## Current Execution Prerequisites (Implementation / Infrastructure State)

### REPO-001 — First baseline Git commit authorization
**Status:** `RESOLVED`
**Evidence:** Created first baseline commit `cdd1ea3e94dbedb6a1b880efd366759bcac1024d` on `main`.

### GITHUB-001 — GitHub repository creation & publication
**Status:** `RESOLVED`
**Evidence:** Remote `origin` configured to `https://github.com/oanhpham-kobe/eiu-recruitment.git`, pushed, and published.
### SUPABASE-DEV-001 — Supabase DEV organization/project provisioning
**Status:** `RESOLVED`
**Evidence:** Dedicated DEV project `eiu-recruitment-dev` provisioned (`yrjclhdvjlekwvfeczcj`, ap-southeast-1) under organization `EIU Recruitment` (`clfvovtyobekjaevdewe`). Linked via `supabase link --project-ref yrjclhdvjlekwvfeczcj`. Local/remote migrations converge through `20260905150000`. Direct SQL/migrations remain database authority; Supabase MCP configured as read-only diagnostic (HTTP 401 unauthenticated startup retained).

### VERCEL-001 — Vercel project creation & linking
**Status:** `RESOLVED`
**Evidence:** Vercel project `eiu-recruitment` (`prj_9t5t1RBtgZp4hOLuSgEYgv5nt8qY`) created and linked to root directory `web` under account `oanhpham-kobe`. Production deployment held per owner governance.
### SOURCE-PARITY-001 — Source Parity Gate Resolution
**Status:** `RESOLVED`  
**Evidence:** Reconciled `recruitment_webapp` from authoritative Full Handover v1.17 payload (`App_Tuyen_Dung_EIU_Full_Handover_v1.17.zip`, SHA256: `0b39c3615dd5b34e998527a1d273e0b846458c7bd4170be46c9bb670bfcb3498`). 87 of 87 current-required paths verified present and 100% hash-identical (0 missing, 0 hash mismatches, 0 unknown extras). Legacy v1.8 assets backed up to external snapshot `recruitment-source-pre-v1.17-sync-20260904-004739`.

## MECH-001 — Exact dependency versions

**Type:** INTENTIONALLY_DEFERRED_IMPLEMENTATION_MECHANIC  
**Affected:** Slice00 scaffold.  
**Status:** `RESOLVED`
**Evidence:** Managed dependencies locked in `web/package.json` (`next@16.3.4`, `react@19.2.8`, `react-dom@19.2.8`, `typescript@6.0.3`, `@biomejs/biome@2.5.12`, `@supabase/ssr@^0.12.6`, `@supabase/supabase-js@^2.115.0`) with exact hashes locked in `web/package-lock.json`. Acceptance runtime locked to Node.js 24.20.0 LTS and npm 11.19.0.
