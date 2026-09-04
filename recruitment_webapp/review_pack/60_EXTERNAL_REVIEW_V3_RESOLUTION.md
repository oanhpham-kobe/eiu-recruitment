# 60. External Review v3 — Resolution Log

> **STATUS: HISTORICAL / SUPERSEDED.** Historical resolution log; current behavior is in v1.7 normative modules.

Source: `review_inputs/external_review_v3_2026-09-02.txt`. Business Logic Core v1.2 remains FROZEN. This document records how v1.5 resolves Review v3 without reopening frozen owner decisions.

## Owner decisions confirmed
1. Candidate Inbox parent summary = **Option A / latest Submission**. Older submissions are historical only and do not drive parent DOB/Gender/Phone/Status/HR Note.
2. System email attachments = **deferred beyond Phase 1**.
3. Application Reactivate = **supported Phase 1**.
4. Existing owner rules remain: Candidate conflict BLOCK; Candidate Email OTP; allowed PDF/DOC/DOCX/PPT/PPTX/PNG/JPG/JPEG; max 5 current files and 5 MB/file; no automatic retention purge; PDF official layout deferred.

## Review v3 P0/P1 resolution
| Review item | v1.5 resolution |
|---|---|
| Pre-submit upload has no Submission parent | Candidate Form Session + temp/quarantine upload; Submission created only on Submit |
| Save/Cancel vs file mutation | staged document changes; Save commits text+files atomically; Cancel leaves persisted versions unchanged |
| Staged document-plan integrity | DB guards require OPEN form session, NEW-form ADD-only, reservation/session/type matching and unambiguous pending changes; Save/Submit validates CLEAN/finalizable uploads, max 5 effective current files and current CV |
| Derived Submission status scattered | single `private.recalculate_submission_status()` |
| Recalc race across Applications | parent Submission row lock is mandatory |
| Add participant ↔ reschedule race | Interview row lock first, then resource locks/re-read |
| Internal first Google login | dedicated atomic first-bind provisioning command |
| Root Admin recovery | dedicated break-glass runbook |
| Permission dependencies | action permissions require view/context prerequisites |
| HR create Submission ambiguity | removed from normal Phase-1 permission matrix |
| HR role remove lifecycle | explicit remove command; revoke HR permissions by default |
| Document logical identity | logical header fixes parent/type; versions reference header |
| Historical master mutation | referenced structural semantics immutable; create new + inactivate old |
| Inactive Interview Format | existing historical reference remains operable; inactive blocks new selection only |
| Format switch stale Room/Link | command/DB normalizes based on format metadata |
| Application inactive UX | Active/Inactive/All + Reactivate Application |
| Copy to different Application | fill empty default Round 1 else create next |
| Grouped pagination | Candidate group for Inbox; Application group for Interview/Report |
| Parent Candidate row ambiguity | latest Submission summary, owner-selected |
| Candidate current cache | latest submitted snapshot only |
| Bulk semantics | command-specific, explicitly documented |
| Email exactly-once wording | at-least-once + idempotent enqueue + best-effort dedup |
| Email attachment mutability | no Phase-1 attachments |
| Privacy acknowledgement redundancy | Candidate derives via Submission |
| Hard delete | keep frozen rule: unused hard delete, used inactive; implement commands |
| HR Report aggregate Delete | removed; report-specific delete only |
| Table width arithmetic | Design v1.4 fixes HR Report min-width to 1610px and validates sum |
| Table spec cross-package drift | single Page Table Specification in Design v1.4 |
| Submission selector | dedicated Submission selector |
| Candidate Privacy section | explicit Design component/section |
| User/Permissions security UI | Bound/Unbound and Root-only identity action separated |
| Catalog lifecycle | Active/Inactive/All + usage guard messaging |
| Legacy report image | renamed/annotated legacy layout-only reference |
| Sticky context | checkbox + primary identity sticky for wide operational tables, tested for focus/z-index |
| Drawer width conflict | responsive available-width formula, no impossible min/max combination |
| Gold contrast | gold restricted to accent/large/decorative use on light surfaces |
| Legacy Office security | malware scan mandatory before go-live/finalization |
| Validation contract | centralized `validation_contract.yaml` |
| PII search in URL | prohibited |
| Validator gaps | expanded fail-closed cross-layer checks |

## Not reopened
- Previous Submission history remains stored despite not driving parent summary.
- Closed Submission may still return to Processed if a new Application is created.
- No scoring/rating.
- Email History business deletion rule remains, with immutable security audit.
- Official PDF layout remains deferred until owner supplies the approved template.
