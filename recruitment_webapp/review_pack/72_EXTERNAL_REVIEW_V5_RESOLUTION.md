# 72. External Review v5 Resolution — baseline Full Handover v1.6 / Design System v1.5

> **STATUS: HISTORICAL / SUPERSEDED.** Retained as review/gate evidence only; current behavior is defined by v1.8 CURRENT sources and docs 77–79.

**Status: CURRENT resolution log for Technical v1.7 / Design System v1.6.**  
**Source review:** `review_inputs/external_full_review_v5_2026-09-02.md`.  
Business Logic Core v1.2 remains **FROZEN**. The changes below resolve contradictions/ambiguity; they do not add a new product module.

## P0 resolution matrix
| Review ID | Resolution in v1.7 |
|---|---|
| P0-01 Source/gate navigation drift | `source_registry.yaml` marks CURRENT/HISTORICAL; current entrypoints are 72/73/74; historical 49/56/57/60/65/69/71 are bannered and excluded from normative All-in-One; README/Guide/AI Prompt/Gate point to v1.7 + DS v1.6. |
| P0-02 Submission no-active-Application contradiction | Generic recalc preserves manual `NEW/READ`; derived state falls back to `READ`; Candidate Reactivate is the explicit lifecycle exception forcing no-active-Application to `READ`. |
| P0-03 access/current/resource semantics | Canonical `access_active`, `current_round`, `resource_blocking` defined in doc 73 + YAML + SQL views. Interviewer access requires active parent Application. Every resource-blocking round blocks Candidate/Room/Interviewer, regardless of Current Round. Application Reactivate revalidates all child sessions that would become resource-blocking. |
| P0-04 Candidate EDIT Privacy | NEW and EDIT Form Sessions both pin server-authoritative current/effective Privacy Notice. EDIT Save requires acknowledgement; same version is idempotent, newly pinned version appends acknowledgement. |

## P1 resolution matrix
| Review ID | Resolution in v1.7 |
|---|---|
| P1-01 Candidate Update notification | `update_candidate_submission` enqueues exact-`submission_id` HR Outbox event inside the same business transaction. Candidate endpoint abuse limits apply before mutation; downstream email throttling/coalescing cannot roll back a valid Save. |
| P1-02 Privacy Notice immutability | Published/referenced notice version/content/hash/published/effective metadata immutable; new wording = new version. Current/effective lookup fails closed with `PRIVACY_NOTICE_UNAVAILABLE`. |
| P1-03 Form Session constraints | `presented_privacy_notice_version NOT NULL`; NEW requires null target/base version; EDIT requires non-null target/base version. |
| P1-04 Candidate current profile cache | `refresh_candidate_current_profile()` selects latest surviving Submission; called after newest submit/edit/HR edit and latest unused Submission delete; older edits cannot overwrite cache. |
| P1-05 RESTORE_OLD_REPORT | Exact Participant restore + Report unarchive transitions frozen; content and original decision metadata preserved; CREATE_NEW_REPORT keeps old history archived and creates a new current lifecycle. |
| P1-06 Application identity ambiguity | **Durable global identity** chosen: `(submission_id, unit_id, department_team_id, position_id)` globally unique and immutable from creation. Exact inactive row is reactivated; exact active row is reused/updated after confirmation. |
| P1-07 Internal User hard delete | **MAINTENANCE_ONLY** Root cleanup for unbound/non-HR/non-Root/never-referenced row; no normal HR UI hard-delete command. |
| P1-08 Application empty Round 1 delete | Delete matrix explicitly treats auto-created structurally-empty Round 1 as an owned default child that may be deleted atomically with an otherwise-unused Application. |
| P1-09 Malware UAT wording | Production scanner mandatory/fail-closed; PENDING/INFECTED/ERROR/unavailable cannot silently finalize; only CLEAN is eligible. |
| P1-10 Email wording/transaction | Client retry prevents duplicate logical Outbox enqueue; provider delivery remains at-least-once. Candidate Submit/Update Outbox insert occurs before business COMMIT; provider send occurs after commit. |
| P1-11 AC-54 stale approval | Replaced with executable frozen whitelist/5 MB/max-5/current-CV/CLEAN/controlled-preview acceptance. |
| P1-12 Historical file 49 | File 49 and older review/gate docs are historical/superseded; AI Prompt forbids using their old GAP/OPEN tables as current decisions. |

## P2 / hardening closure
- `private.bump_submission_aggregate_version()` now only touches aggregate row; version trigger remains single authoritative increment.
- Current source headers/pointers corrected; Design current target = v1.6, Technical current target = v1.7.
- `73_DOMAIN_GLOSSARY_AND_CANONICAL_PREDICATES.md` added.
- `75_RELEASE_EVIDENCE_MATRIX.md` adds browser/click-path/viewports/accessibility/query-plan evidence requirements.
- `76_DEPENDENCY_BASELINE_POLICY.md` defines implementation-time exact dependency pinning + lockfile policy.
- Design validation numerically checks semantic status contrast; 200% zoom / 400% reflow expectations are explicit.
- Semantic package validator checks source navigation, historical exclusion, status outcomes, access/resource predicates, EDIT Privacy, notification/cache side effects, durable identity, participant restore, upload/email semantics and command side-effect coverage.

## Result after amendment
Specification target for re-review:
- Business Logic Core v1.2 = **FROZEN**.
- Design System v1.6 = **CURRENT / re-review pending**.
- Technical Architecture v1.7 = **READY FOR EXTERNAL RE-REVIEW / NOT FROZEN**.
- Implementation Gate = **NOT YET PASS**.
- Production Ready = **NO**.
