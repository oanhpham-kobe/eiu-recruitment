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
**Status:** `PENDING_AUTHORIZATION`  
**Rule:** Authenticated with 0 projects; DEV organization/project to be provisioned during Slice00 Task 3.

### VERCEL-001 — Vercel project creation & linking
**Status:** `PENDING_FRAMEWORK_ROOT`  
**Rule:** Authenticated with 0 projects; Vercel project linking to occur when framework root is established.

### SOURCE-PARITY-001 — Source Parity Gate Resolution
**Status:** `RESOLVED`  
**Evidence:** Reconciled `recruitment_webapp` from authoritative Full Handover v1.17 payload (`App_Tuyen_Dung_EIU_Full_Handover_v1.17.zip`, SHA256: `0b39c3615dd5b34e998527a1d273e0b846458c7bd4170be46c9bb670bfcb3498`). 87 of 87 current-required paths verified present and 100% hash-identical (0 missing, 0 hash mismatches, 0 unknown extras). Legacy v1.8 assets backed up to external snapshot `recruitment-source-pre-v1.17-sync-20260904-004739`.

## MECH-001 — Exact dependency versions

**Type:** INTENTIONALLY_DEFERRED_IMPLEMENTATION_MECHANIC  
**Affected:** Slice00 scaffold.  
**Status:** `IN_PROGRESS_FOR_TASK_002`
**Rule:** choose current supported/patched Node/Next.js/React/Supabase/test provider versions from official docs/advisories at execution time; pin lockfile and evidence. Do not infer from prototype or historical artifacts.
