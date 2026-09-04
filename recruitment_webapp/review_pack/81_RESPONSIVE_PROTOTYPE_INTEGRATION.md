# 81. Responsive Prototype Integration — v1.10 / Design System v1.8

**Status: CURRENT / NORMATIVE interaction/design amendment.**

**Responsive Prototype v1.10** is the executable responsive reference bundled with this handover.

The Full Handover v1.17 bundle includes `responsive_prototype/` v1.10 for one-package external + owner review. It is executable HTML/CSS/JS prototype evidence, not production React implementation.

## Frozen-for-current-UAT responsive corrections
- Candidate Inbox parent row derives Status/HR Note from deterministic latest Submission; Candidate Inactive is a separate lifecycle badge.
- Candidate-level bulk manual Submission status exposes only `NEW / READ`, resolves latest Submission and behaves ALL_OR_NOTHING.
- Historical child Submission status is read-only in Candidate-level bulk/manual UX.
- Normal persona navigation excludes `FUTURE_HIDDEN / NOT_RENDERED` routes.
- HR Report uses Current Interview Report Status; aggregate drawer has no generic Delete; Final Decision Source uses `decisionUpdatedAt`.
- Candidate EDIT exposes staged document `ADD / REPLACE / DELETE`; CV is authoritative-required on Save/Submit.
- Interview + HR Report status badges: **144px** benchmark; long English labels wrap inside this width, never stretch the full cell.
- Row StatusDropdown opens directly from the badge bounds and inherits badge width. Toolbar StatusDropdown opens from its Status button, with normal toolbar minimum width. No pointer-coordinate positioning.
- Dropdown dismisses by selection, outside pointer, Escape, or same-trigger toggle; Escape restores trigger focus.
- Interview time order: **time first, date after**; stay on one line while enough room exists and wrap only when genuinely constrained.
- Mobile `Thời gian phỏng vấn` label must have enough label-column width to avoid unnecessary wrapping.
- Mobile/Tablet/Desktop share business actions; bulk selection/status behavior uses the same underlying workflow and remains independently testable.

## Authority
Business/security/command semantics come from Full Handover v1.17. Visual/responsive tokens/components come from Design System v1.8. Owner-approved UAT corrections are recorded here and in Design System v1.8.
