# EIU Recruitment — Responsive Clickable Prototype v1.10

## Status
**Responsive UX-UAT prototype — user visual corrections applied and button flows re-audited.**

Authority:
- Full Handover **v1.17**
- Design System **v1.8**

This package is a static HTML/CSS/JS prototype. It does not replace the Handover or Design System source of truth and does not implement backend/RLS/database behavior.

## v1.10 current alignment
- Single and bulk Interview Schedule Status activation now route through one shared operational-transition validator: current Participants must be Active and Candidate/Room/Interviewer conflicts must be clear; bulk is prevalidated ALL_OR_NOTHING.
- Browser QA includes inactive-Participant and Candidate/Room/Interviewer adversarial status-transition cases plus critical-control evidence.
- Schedule simulation now blocks Candidate, Room and Interviewer overlap using `[start,end)` and ignores CANCELLED/inactive/no-interval rows.
- Copy to another Application fills a structurally empty default Round 1; otherwise it creates the next legal round. Source date/time/format/location are prefilled and Demo Topic remains blank.
- Copy provenance is represented in prototype state so a copied Round is not treated as structurally empty.
- Browser QA now includes core-route overflow smoke coverage for Interview, Users/Permissions, Candidate Applications and Interviewer Report.

## v1.7 changes retained
- Candidate Inactive no longer creates a different single/bulk NEW/READ eligibility rule; internal HR status mutation remains available when no active Application exists.
- Education is optional under the current contract: no invented `required` markers or minimum-one row; user can remove the last row and add rows again.
- NEW_SUBMISSION Privacy acknowledgement is unchecked by default and must be explicit. EDIT demo may show satisfied only for the same pinned acknowledged notice version.
- Privacy acknowledgement is the only Phase-1 confirmation model; no separate accuracy-attestation checkbox is implied.

## v1.6 changes retained
- Candidate lifecycle is separate from Submission workflow; Candidate Inactive never overwrites Submission status.
- Candidate parent row derives Status/HR Note from deterministic latest Submission.
- Candidate-level bulk manual status now exposes only NEW/READ and behaves ALL_OR_NOTHING against latest Submission.
- Historical Submission status is read-only from the Candidate-level UX.
- Normal persona sidebar excludes FUTURE_HIDDEN / NOT_RENDERED routes.
- HR Report Status is stored on Current Interview; Application outcome is derived.
- Aggregate HR Report drawer has no generic Delete.
- Final Decision Source uses `decisionUpdatedAt`; qualitative-only edits do not move the source.
- Candidate EDIT has staged ADD/REPLACE/DELETE and authoritative CV-required validation.
- v1.5 anchored status-popover behavior is retained.

## v1.5 changes retained
- Status dropdown now opens from the status badge/Status toolbar button itself, not from the exact pointer click coordinate.
- Clicking the same trigger again closes the dropdown.
- Clicking outside closes it without changing status.
- Escape closes it and restores focus to the trigger.
- Fixed-position dropdown repositions with scrolling and closes on resize so it cannot remain detached from its source.
- Standard dropdown width remains 280px maximum and is clamped only for narrow mobile viewports.

## v1.4 changes retained
- Interview + Interview Report status badges use a compact **144px benchmark** based on `Đã gửi báo cáo`; long English states wrap inside that width instead of stretching the row/card.
- Interview time is displayed **time first, date second**: `14:00 – 15:30 · 20/05/2025`.
- Time/date stays on one line when space allows and wraps only when the value area is genuinely too narrow.
- Mobile HR Report reserves enough label width so `Thời gian phỏng vấn` / `Interview time` does not wrap.
- Bulk checkbox bug fixed: clicking a checkbox no longer gets cancelled by `preventDefault()`.
- Applications / Interview / HR Report bulk status flows were re-tested.
- Interview copy, email preview, delete confirmation, Candidate education Add/Remove, Candidate privacy validation and Users/Permissions prototype flows were re-tested.
- All visible buttons in core responsive routes and representative drawers are wired to a real prototype action or an explicit prototype-feedback action; no silent/dead buttons remain in the audited routes.
- v1.3 focus restoration edge case with an empty selector was fixed.

## Responsive representation
- Candidate applications: compact cards on phone; table on wider screens.
- Candidate Form: one-column phone layout, single-page business order retained.
- Internal HR/Admin/Interviewer: tablet keeps horizontal data tables; phone renders structured labelled rows.
- Drawer: bounded on tablet, full-screen on phone.
- Filters/Modal: responsive sheet/dialog pattern.

## Start here for v1.10 review
1. `VERSION.md`
2. `RESPONSIVE_BROWSER_QA_v1.10.md`
3. `RESPONSIVE_QA_RESULTS_v1.10.json`
4. `responsive-v110.js` / `responsive-v19.js` / `responsive-v18.css`
5. `RESPONSIVE_CONTRACT_v1.4.md` and `RESPONSIVE_BUTTON_FLOW_AUDIT_v1.4.md` remain the retained layout/interaction contract where not amended by v1.9.

## Open locally
Open `index.html` in a browser. Useful routes:
- `index.html?role=hr&page=interview`
- `index.html?role=hr&page=hr-report`
- `index.html?role=hr&page=applications`
- `index.html?role=admin&page=permissions`
- `index.html?role=candidate&page=candidate-form`
- `index.html?role=candidate&page=candidate-applications`

## Evidence boundary
Browser QA in this package verifies the static prototype only. It does not prove production React/Next.js, Supabase, RLS, email delivery or database behavior. Production engineering tests remain separate implementation/release gates.

## Production implementation note
This static prototype intentionally retains layered historical overrides so reviewers can trace incremental amendments. **Do not copy the override chain into production.** Production React/Next.js components and state transitions must be implemented fresh from the current Full Handover v1.17 + Design System v1.8 contracts, with Responsive v1.10 used only as executable interaction/reference evidence.
