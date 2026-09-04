# Responsive Browser QA — v1.5

## Scope
Regression of v1.4 plus the user-requested status dropdown correction.

## Fresh result
`57/57 PASS — 0 FAIL`

## New v1.5 checks
- Status menu is positioned from the badge/control bounding box, not pointer coordinates.
- Clicking different points inside the same badge yields the same anchored dropdown position.
- Same badge toggles the menu closed.
- Outside click dismisses without status mutation.
- Escape dismisses and restores focus to the trigger.
- Trigger exposes `aria-haspopup=menu` and `aria-expanded` state.
- Dropdown is viewport-clamped on mobile.
- Existing v1.4 badge width, time layout, bulk selection/status, Candidate form, User/Permissions and no-dead-button checks remain PASS.
- No JS/console errors.

## Representative screenshots
- `screenshots_v15/interview_status_dropdown_1280.png`
- `screenshots_v15/interview_status_dropdown_430.png`
