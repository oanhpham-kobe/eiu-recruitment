# 77. External Review v6 Resolution — CURRENT

**Status: HISTORICAL / SUPERSEDED.** Retained for traceability only; current behavior is governed by `source_registry.yaml`, Review 80 and Gate 82.


Baseline reviewed: Full Handover v1.7 + Design System v1.6 (03/09/2026). This document maps every finding from `review_inputs/external_full_review_v6_2026-09-03.md` to the v1.8/DS v1.7 resolution.

## P0
- **P0-01 Report Status duplicate command:** RESOLVED. `change_report_status` is the only status writer; `update_hr_report_note` is note-only. Behavior-specific ACs and registry writes/side-effects added.
- **P0-02 staged historical logical target:** RESOLVED. DB stage-time + Save-time exactly-one-current-version guards; HR mutation shares invariant; adversarial ACs added.
- **P0-03 CURRENT source contradictions:** RESOLVED in place in docs 02/08/10; append-only canonical duplication removed from those sections and semantic validator checks legacy patterns.

## P1
- Registry side effects made exhaustive for outcome-changing commands.
- Email History gained `emails.history_view`, parent contextual authorization, environment-aware TEST cleanup and explicit WRONG cleanup reason with immutable audit.
- Active Application owner invariant enforced; HR deactivation/role removal cannot strand Active Applications.
- Reactivation conflicts use non-elapsed `schedule_conflict_relevant`; past-only overlaps do not strand lifecycle recovery.
- Non-root Directory Manager cannot inspect another user's granular effective permissions.
- Privacy publication/current-switch procedure frozen in doc 78.
- Candidate inactive metadata semantics frozen + DB constraint.
- Schema/Design metadata advanced to v1.8/v1.7.
- Interview Report lifecycle CHECK added.
- Command acceptance mappings now use behavior-specific guarantee tags/checks.

## P2 hardening
- **Application NULL-Team sentinel:** RESOLVED. The zero UUID used only inside the durable-identity expression index is now physically reserved by `department_team_zero_uuid_reserved_ck`; a real Team cannot use it.
- **Final Decision exact-tie hardening:** REVIEWED / NO CHANGE REQUIRED FOR PHASE 1. `decision_updated_at` plus stable tie-break remains accepted; monotonic decision revision is optional future hardening, not a current defect.
- **Audit actor ambiguity:** RESOLVED. Activity/Security Audit rows enforce at most one human actor (Internal User or Candidate).
- **SHA-256 field shape:** RESOLVED. Privacy/document/upload checksum fields enforce 64-hex shape where applicable.
- **CURRENT-source consolidation:** RESOLVED. Versioned clarification headings in CURRENT/NORMATIVE modules were consolidated into semantic sections; historical version narratives remain only in Changelog/Review evidence.
- **Browser QA/click-path evidence:** CORRECTLY DEFERRED TO IMPLEMENTATION/RELEASE GATE. The specification defines required evidence in doc 75; pre-code validation must not claim rendered-browser PASS.

**Business Logic Core v1.2 remains FROZEN. Technical Architecture v1.8 remains NOT FROZEN until external re-review and implementation evidence gates pass.**