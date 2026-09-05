# OPEN_GAPS — Active Unresolved Gap Register

> **ACTIVE UNRESOLVED GAPS ONLY**
> This file tracks active technical and operational gaps affecting upcoming implementation.
> It is not a scheduler authority. Historical resolutions are indexed below in summary form.

---

## 1. Active Unresolved Items

### UAT-001 — Owner Visual UAT
**Type:** RELEASE_UAT_HOLD  
**Affected:** Final visual sign-off / later UI slices / Production UAT.
**Status:** Responsive Prototype v1.10 is READY FOR OWNER VISUAL UAT / NOT FROZEN.  
**Safe work:** Slices 00 through 03 complete; Slice 04 onwards may proceed up to visual release boundaries.

### ASSET-001 — Official PDF Owner Template
**Type:** NON_BLOCKING_ASSET_GAP  
**Affected:** Slice 05 PDF pixel-perfect owner sign-off only.
**Status:** PENDING_OWNER_TEMPLATE. Implement report data/permissions/logic from canonical source; do not invent the official final PDF layout before owner template is provided.

### MCP-SUPABASE-401 — Supabase DEV MCP Startup Diagnostic
**Type:** NON_BLOCKING_TOOLING_LIMITATION
**Affected:** Read-only Supabase MCP inspection only.
**Status:** RETAINED_DIAGNOSTIC (HTTP 401 unauthenticated startup). Repository migrations, schema definitions, and SQL integration tests remain 100% authoritative.

---

## 2. Summary of Resolved Historical Gaps (Audit References)

| Gap ID | Category | Resolution Summary | Canonical Verification Ref |
| :--- | :--- | :--- | :--- |
| **EXEC-001** | Runtime Environment | Canonical repository `D:/orca/recruitment` operational with Orca + OMP | `project_control/CHANGELOG_IMPLEMENTATION.md` |
| **REPO-001** | First Git Baseline | First baseline commit `cdd1ea3e` established on `main` | `EVIDENCE_INDEX.yaml:BASELINE-COMMIT-001` |
| **GITHUB-001** | Origin Publication | Remote `origin` configured, pushed, and verified | `EVIDENCE_INDEX.yaml:GITHUB-PUBLICATION-001` |
| **SOURCE-PARITY-001** | Full Handover v1.17 | 87/87 paths hash-verified against v1.17 payload | `EVIDENCE_INDEX.yaml:SOURCE-PARITY-001` |
| **MECH-001** | Dependency Locking | Next 16.3.4, React 19, Supabase SSR locked in package.json & lockfile | `EVIDENCE_INDEX.yaml:SCAFFOLD-APP-001` |
| **SUPABASE-DEV-001** | DEV DB Provisioning | Project `eiu-recruitment-dev` (`yrjclhdvjlekwvfeczcj`) linked & migrations run | `EVIDENCE_INDEX.yaml:DEV-INFRA-001` |
| **VERCEL-001** | Project Linking | Project `eiu-recruitment` (`prj_9t5t1RBtgZp4hOLuSgEYgv5nt8qY`) linked | `EVIDENCE_INDEX.yaml:DEV-INFRA-001` |
| **WORKFLOW-001** | Independent Review | Established independent prompt & implementation review gates across S00-S03 | `project_control/TASK_REGISTRY.yaml` |
