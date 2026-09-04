# RESPONSIVE FOUNDATION — v1.8

## Status
Detailed iPad/mobile page layouts are **NOT FROZEN**. They follow Desktop v1.8 UX-UAT.

## Production scope principle
- Internal HR/Admin/Interviewer app: desktop-first.
- Candidate Login + Candidate Form + Phiếu của tôi: **mobile-ready is a go-live requirement** because external candidates are expected to use phones.

## Review viewport references
- mobile: 375–390px
- tablet portrait: 768px
- tablet landscape/small desktop: 1024px
- desktop/laptop: 1280–1440px+

These are review references, not brittle CSS device detections.

## Rules that never change
- main typography >=16px;
- no clipped VI/EN strings;
- status state remains legible/textual;
- touch controls large enough;
- Drawer/Modal content >=16px;
- long operational tables may scroll rather than shrink text.

## Desktop >=1280px
- sidebar 244px;
- sticky header + full toolbar;
- fixed colgroup table + horizontal overflow when required;
- desktop Drawer prefers 820px but is capped by available content width with safe gutters; no impossible fixed minimum vs vw cap.

## Tablet direction to prototype
- sidebar collapsed/off-canvas depending orientation;
- prioritize key table columns without changing data semantics;
- horizontal scroll remains acceptable for dense HR tables;
- toolbar may wrap or move secondary actions into More/overflow;
- Drawer may become 70–85vw or full-screen sheet in portrait;
- touch status badge/dropdown behavior tested explicitly.

## Mobile direction to prototype
### Candidate Portal
- mobile-first form flow while preserving single-page business structure;
- one-column fields;
- repeatable Education sections easy to add/remove;
- document upload optimized for phone file/photo workflows within security rules;
- full-width action area where useful;
- Phiếu của tôi uses a compact structured list/table appropriate to narrow width.

### Internal HR
- off-canvas navigation;
- filters in sheet/dialog;
- detail Drawer becomes full-screen sheet/page;
- per-page decision whether to retain horizontal table or use structured rows;
- never mechanically convert every HR table into cards if comparison is lost.

## UX-UAT order
1. Login
2. Candidate Form
3. Phiếu của tôi
4. Quản lý phiếu ứng tuyển
5. Interview
6. Báo cáo HR
7. Báo cáo Interviewer
8. Danh mục / Users & Permissions

- Candidate Form mobile includes Privacy Notice/acknowledgement before Submit.
- Candidate Inbox grouping on tablet/mobile still uses latest Submission as parent summary; historical submissions open in detail/history.


## Current owner-approved responsive UAT rules — v1.8

The executable reference is Responsive Prototype **v1.10** bundled with Full Handover v1.17. These rules are normative for the next production implementation/UAT:

- Representative QA widths: 360, 390, 430, 768, 1024 and desktop reference; constrained-height overlay checks are also required.
- Mobile Candidate forms use a one-column layout; tablet/desktop may use the approved multi-column layout. Do not reduce operational text below the Design System minimum merely to fit a desktop composition.
- Tablet data-heavy pages retain semantic tables with contained horizontal scrolling. Mobile may use structured summary rows/cards only where the page-specific contract allows it; business-critical data/actions remain reachable.
- Interview and HR Report row status badges use a **144px benchmark width**. Long English labels wrap within this width instead of stretching the cell.
- Row StatusDropdown is anchored to the status badge/button bounds, not pointer coordinates. It dismisses on selection, outside click/tap, Escape, or same-trigger toggle; Escape restores focus to the trigger.
- Interview time presentation is **time first, date after** and remains on one line whenever the available width is sufficient; wrapping occurs only when genuinely constrained.
- Mobile label `Thời gian phỏng vấn` must have enough label-column width to avoid unnecessary wrapping.
- Mobile navigation/drawers must use accessible focus management, Escape dismissal, focus restoration, background inertness/scroll lock, and must not leave visually hidden duplicate navigation available to assistive technology.
- Responsive presentation must not create a separate business workflow or duplicate server mutation semantics for mobile.
