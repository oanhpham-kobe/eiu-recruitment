# Responsive Detailed Design Contract — v1.3

Authority: Full Handover v1.8 + Design System v1.7.

## Review widths
- very narrow mobile: **360px**
- mobile: **390px**
- large mobile: **430px**
- tablet portrait: **768px**
- tablet landscape: **1024px**
- desktop regression: **1280px**

These are QA references, not device sniffing rules.

## Rules that never change
- operational content stays >=16px except clearly secondary helper/meta text;
- VI/EN text must not be clipped;
- status always has text, never color only;
- touch controls target >=44x44 on narrow layouts;
- business-critical data/actions remain reachable;
- responsive presentation never creates a second business workflow;
- PII search is not serialized into URL;
- wide HR tables may scroll; text is not shrunk to fit.

## App shell/navigation
### Desktop
- fixed 244px sidebar, visible to assistive technology;
- hamburger hidden.

### Tablet/mobile
- sidebar becomes off-canvas;
- when closed: `aria-hidden` + `inert`;
- when open: dialog-like overlay semantics, main content inert, body scroll locked;
- focus moves to Close; Escape closes; focus returns to hamburger;
- sign-out remains reachable from sidebar when topbar sign-out is compacted/hidden.

## Page headers/actions
- title wraps; never ellipsizes required VI/EN title text;
- primary action remains visible;
- secondary toolbar actions may scroll horizontally rather than overflow page;
- filter becomes a sheet/dialog on phone;
- Candidate VI|EN remains reachable at 360–430px.

## Candidate Form
### Desktop/tablet
- existing two-column layout where defined.

### Mobile
- one column;
- single-page business order preserved;
- sticky action area uses safe-area padding;
- upload tiles are touch-friendly;
- Privacy acknowledgement is final section;
- validation error is visible, programmatically associated and moves focus to invalid acknowledgement;
- controls have persistent labels.

## Candidate applications
### Desktop/tablet
- semantic table.
### Mobile
- compact submission cards are allowed because the workflow is item-centric rather than cross-row comparison;
- status + submitted time + Edit/View remain accessible;
- same submission dataset/actions feed both presentations.

## Internal HR operational tables
### Desktop/tablet
- retain semantic table and frozen widths;
- horizontal scroll stays inside table container;
- sticky Select + identity where specified;
- horizontal scroller is keyboard focusable when overflow exists.

### Mobile
- structured row presentation uses the same semantic table DOM/data;
- no business-critical column is deleted solely to fit width;
- labels are derived from table headers;
- action controls remain explicit and >=44px.

## Drawer/Modal
### Desktop
- Drawer follows Design System width token; Modal remains focused dialog.
### Tablet
- bounded Drawer up to 820px / available viewport.
### Mobile
- Drawer = full-screen sheet;
- Modal/filter = bottom sheet, height-constrained with internal scrolling;
- role/dialog name, focus trap, Escape, close button, background inert, scroll lock and focus restoration are mandatory.

## Accessibility/reflow
- visible `:focus-visible`;
- native controls before ARIA;
- icon-only buttons have accessible names;
- toast/status messages use live region semantics;
- reduced motion respected;
- 200% text zoom and 400% reflow remain production UAT requirements; wide data tables are intentional two-dimensional-scroll exception.
