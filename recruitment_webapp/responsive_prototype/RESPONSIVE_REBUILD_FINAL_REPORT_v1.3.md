# Recruitment Responsive/Mobile Rebuild — v1.3

## Source authorities followed
- Full Handover v1.8
- Design System v1.7
- Current responsive/accessibility/page override rules from that Design System

## Engineering guidance actually applied
- audit-before-change / surgical-change / fresh-verification principles;
- accessibility semantics/focus/keyboard/touch/reflow guidance;
- browser QA with real Chromium layout;
- scoped frontend checklist;
- verification-before-completion discipline.

React-specific, composition-pattern, TDD and GitNexus lanes were intentionally not forced onto this static prototype.

## GitNexus impact analysis
Not applicable: this artifact is not a Git/React component repository. Shared consumers were audited directly in source.

## Kept from v1.2
- Candidate mobile cards;
- Candidate one-column form;
- touch upload tiles and Privacy section;
- HR structured rows on phone using the same table DOM;
- tablet horizontal table scroll;
- off-canvas navigation visual design;
- mobile full-screen Drawer and bottom-sheet Modal visual direction;
- sticky table context columns and frozen table widths.

## Rebuilt/adapted
- overlay/navigation accessibility state;
- keyboard/Escape/focus restore/focus trap;
- background inert + scroll lock;
- form label normalization;
- Candidate privacy validation focus/error path;
- Candidate very-narrow header so VI|EN remains reachable;
- narrow mobile sign-out access;
- icon-only accessible labels;
- keyboard focusability for overflowing table containers;
- reduced motion;
- constrained-height overlay behavior;
- 44px compact Filter action correction.

## Removed / superseded
Old v1.2 current QA/next-phase documents are retained only as files marked `HISTORICAL`; v1.3 documents are the current prototype evidence.

## Shared areas changed
- responsive shell/sidebar
- page toolbar accessibility/presentation
- form label/error behavior
- table scroll container
- Modal/Drawer focus behavior

No backend/business/security workflow was altered.

## Pages/families verified
- Login
- Candidate Form
- Candidate Applications
- HR Application Inbox
- Users & Permissions
- Interview tablet
- HR Report tablet
- mobile Navigation
- mobile Filters
- mobile full-screen Drawer

## Viewports verified
- 360x800
- 390x844
- 430x932
- 390x600 constrained height
- 768x1024
- 1024x768
- 1280x800

## Accessibility
- keyboard: mobile nav and dialog/drawer Escape/focus paths verified
- focus: visible focus + restore verified
- touch targets: core narrow-layout controls >=44x44 verified
- labels/errors: Candidate fields normalized; Privacy error/focus verified
- screen-reader semantics: off-canvas hidden when closed; dialog semantics added
- axe: not added/run in this static artifact; remains production/UAT evidence

## Browser QA
- environment: local inline prototype in headless Chromium via Playwright
- console/page errors: none in audited cases
- page overflow: none in audited cases
- evidence: `RESPONSIVE_BROWSER_QA_v1.3.md`, JSON results, screenshots

## React tests
Not applicable to static HTML/CSS/JS prototype. No testing framework was introduced solely for this pass.

## Front-End Checklist
See `RESPONSIVE_FRONTEND_AUDIT_v1.3.md`.

## Desktop regression
1280px shell/sidebar/hamburger behavior included in fresh QA. Production desktop UX remains governed by Design System and actual implementation UAT.

## Remaining issues
- user visual acceptance is still required;
- real production React/Next implementation must repeat responsive/accessibility tests;
- axe/manual screen-reader/real-device evidence remains implementation/release scope.

## User visual acceptance
**READY FOR USER REVIEW**

## Git state
- branch/commit: N/A, static versioned artifact
- push/deploy: none
