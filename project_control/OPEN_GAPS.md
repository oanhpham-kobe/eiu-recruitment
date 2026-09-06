# OPEN_GAPS — Active Unresolved Gap Register

> **ACTIVE UNRESOLVED GAPS ONLY**
> This file tracks active technical and operational gaps affecting upcoming implementation.
> It is not a scheduler authority. Historical resolutions are indexed below in summary form.

## Mandatory Entry Shape for Active Items

```text
ITEM:
TYPE:
STATUS: OPEN | DEFER_UNTIL_FEATURE | DEFER_UNTIL_PREPROD | BLOCKED
PRIORITY: HIGH | MEDIUM | LOW
BLOCKING: YES | NO
AFFECTED:
WHEN_TO_HANDLE:
TRIGGER:
DO_NOT:
EXIT_CONDITION:
EVIDENCE_REF:
```

Rules:
- `CLOSED_AS_DESIGNED` does NOT belong in Active Unresolved Items.
- `STALE_OR_NOT_APPLICABLE` does NOT belong in Active Unresolved Items.
- Resolved items move/collapse into the existing historical-resolution summary with an evidence/canonical reference.
- A non-blocking deferred item must never silently become a current feature blocker before its recorded trigger.
- When its trigger occurs, the Planner must materialize the concern into that feature's acceptance criteria or pre-production gate and keep it open until the exit condition passes.

---

## 1. Active Unresolved Items

### UAT-001 — Owner Visual UAT
```text
ITEM: UAT-001 — Owner Visual UAT
TYPE: RELEASE_UAT_HOLD
STATUS: DEFER_UNTIL_PREPROD
PRIORITY: MEDIUM
BLOCKING: NO
AFFECTED: Final visual sign-off / later UI slices / Production UAT
WHEN_TO_HANDLE: Before final production release and visual sign-off
TRIGGER: Visual release boundary / Production UAT phase
DO_NOT: Block Slices 00 through 04 from proceeding up to visual release boundaries
EXIT_CONDITION: Owner signs off on Responsive Prototype / production visual UI
EVIDENCE_REF: 52_TECHNICAL_GATE_STATUS.md
```

### ASSET-001 — Official PDF Owner Template
```text
ITEM: ASSET-001 — Official PDF Owner Template
TYPE: NON_BLOCKING_ASSET_GAP
STATUS: DEFER_UNTIL_FEATURE
PRIORITY: LOW
BLOCKING: NO
AFFECTED: Slice 05 PDF pixel-perfect owner sign-off only
WHEN_TO_HANDLE: When Slice 05 PDF generation feature is materialized
TRIGGER: Start of Slice 05 PDF template integration
DO_NOT: Invent the official final PDF layout before owner template is provided
EXIT_CONDITION: Official PDF template provided by Owner and integrated in Slice 05
EVIDENCE_REF: 14_SCOPE_AND_OPEN_ITEMS.md
```

### MCP-SUPABASE-401 — Supabase DEV MCP Startup Diagnostic
```text
ITEM: MCP-SUPABASE-401 — Supabase DEV MCP Startup Diagnostic
TYPE: NON_BLOCKING_TOOLING_LIMITATION
STATUS: OPEN
PRIORITY: LOW
BLOCKING: NO
AFFECTED: Read-only Supabase MCP inspection only
WHEN_TO_HANDLE: When Supabase MCP service or credentials are refreshed
TRIGGER: Local tooling or MCP runtime maintenance
DO_NOT: Block development or migration testing; migrations and direct SQL tests remain 100% authoritative
EXIT_CONDITION: Supabase DEV MCP connects successfully or is superseded by CLI workflows
EVIDENCE_REF: project_control/CHANGELOG_IMPLEMENTATION.md
```

### DATA-RETENTION-001 — Future Archive/Purge/Retention Implementation
```text
ITEM: DATA-RETENTION-001 — Future Archive/Purge/Retention Implementation
TYPE: DEFERRED_FEATURE_HARDENING
STATUS: DEFER_UNTIL_FEATURE
PRIORITY: MEDIUM
BLOCKING: NO
AFFECTED: future archive/purge/retention implementation
WHEN_TO_HANDLE: when archive, purge, retention, or destructive record cleanup is materialized
TRIGGER: first task that implements archive/purge/retention behavior
DO_NOT: block S04 merely because archive/purge is not implemented yet
EXIT_CONDITION: retention + dependency-closure + Legal Hold behavior is canonicalized, implemented, and acceptance-tested for the actual feature
EVIDENCE_REF: 42_PRIVACY_RETENTION_COMPLIANCE.md; 66_DATA_EXPORT_ARCHIVE_PURGE_RUNBOOK.md
```

### EXPORT-CSV-001 — Future CSV/Export Formula-Injection Hardening
```text
ITEM: EXPORT-CSV-001 — Future CSV/Export Formula-Injection Hardening
TYPE: DEFERRED_FEATURE_SECURITY
STATUS: DEFER_UNTIL_FEATURE
PRIORITY: MEDIUM
BLOCKING: NO
AFFECTED: future CSV/export functionality
WHEN_TO_HANDLE: when CSV/export feature is materialized
TRIGGER: first task that emits spreadsheet/CSV cells from Candidate or HR-controlled text
DO_NOT: build speculative export sanitization before an export feature exists
EXIT_CONDITION: formula-injection-safe export encoding/sanitization is implemented and tested
EVIDENCE_REF: 66_DATA_EXPORT_ARCHIVE_PURGE_RUNBOOK.md; 67_WEB_SECURITY_BASELINE.md
```

### SCANNER-OPS-001 — Production Candidate Upload Scanner/Session Resilience
```text
ITEM: SCANNER-OPS-001 — Production Candidate Upload Scanner/Session Resilience
TYPE: DEFERRED_OPERATIONAL_HARDENING
STATUS: DEFER_UNTIL_PREPROD
PRIORITY: MEDIUM
BLOCKING: NO
AFFECTED: production Candidate upload scanner/session resilience
WHEN_TO_HANDLE: after real scanner/provider is selected and measured, before production Candidate upload release
TRIGGER: pre-production upload/security readiness review with real scanner latency data
DO_NOT: redesign session TTL from hypothetical latency before real scanner evidence exists
EXIT_CONDITION: scanner latency/failure behavior, session interaction, retry/cleanup, and operational thresholds pass pre-production acceptance
EVIDENCE_REF: 41_STORAGE_AND_UPLOAD_SECURITY.md
```

### AUTH-NAT-001 — Candidate OTP Rate-Limit Under Shared NAT/Proxy
```text
ITEM: AUTH-NAT-001 — Candidate OTP Rate-Limit Under Shared NAT/Proxy
TYPE: DEFERRED_OPERATIONAL_HARDENING
STATUS: DEFER_UNTIL_PREPROD
PRIORITY: MEDIUM
BLOCKING: NO
AFFECTED: Candidate OTP abuse/rate-limit behavior under shared NAT/proxy traffic
WHEN_TO_HANDLE: pre-production auth/load/security validation
TRIGGER: realistic OTP abuse/load testing with shared-IP/NAT cases
DO_NOT: redesign auth throttling from hypothetical traffic before evidence exists
EXIT_CONDITION: supported OTP throttling/anti-enumeration behavior passes realistic pre-production abuse tests
EVIDENCE_REF: 46_AUTH_IDENTITY_MODEL.md; 68_RATE_LIMIT_POLICY.md
```

### PRIVACY-PREPROD-001 — Production Candidate PII/Data-Minimization Readiness
```text
ITEM: PRIVACY-PREPROD-001 — Production Candidate PII/Data-Minimization Readiness
TYPE: DEFERRED_PRIVACY_REVIEW
STATUS: DEFER_UNTIL_PREPROD
PRIORITY: MEDIUM
BLOCKING: NO
AFFECTED: production Candidate PII/data-minimization readiness
WHEN_TO_HANDLE: pre-production privacy/release review
TRIGGER: production Candidate portal readiness
DO_NOT: block current implementation solely to invent an organizational DPO process
EXIT_CONDITION: production data-minimization/privacy review is completed against the actual implemented data flows and retention behavior
EVIDENCE_REF: 42_PRIVACY_RETENTION_COMPLIANCE.md
```

### OPS-SLO-001 — Production SLO/Alert/Restore Thresholds
```text
ITEM: OPS-SLO-001 — Production SLO/Alert/Restore Thresholds
TYPE: DEFERRED_OPERATIONAL_READINESS
STATUS: DEFER_UNTIL_PREPROD
PRIORITY: MEDIUM
BLOCKING: NO
AFFECTED: production SLO/alert/restore thresholds
WHEN_TO_HANDLE: pre-production operational readiness
TRIGGER: production release-readiness phase
DO_NOT: block S04 on arbitrary SLO numbers without observed environment evidence
EXIT_CONDITION: production SLO, alert thresholds, backup/restore evidence, and operating ownership are explicitly accepted
EVIDENCE_REF: 44_DEPLOYMENT_OPERATIONS.md
```

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
