# Responsive Status Menu UAT — v1.5

## User correction implemented
- Status dropdown opens from the **badge/button anchor**, never from pointer coordinates.
- Clicking the same status badge again closes the menu without selecting.
- Clicking anywhere outside closes the menu without selecting.
- `Escape` closes the menu and restores focus to the trigger.
- Menu position is clamped to the viewport while preserving the badge/button as its anchor.
- Scrolling repositions the fixed menu from its anchor; resize closes stale layout state instead of leaving a detached menu.

## Visual contract
- Status badge width remains the v1.4 compact benchmark.
- Dropdown uses one standard width: up to 280px, reduced only when the viewport is narrower.
- Default placement is below the badge/control with an 8px gap; if there is insufficient space below, it opens above.

## UX-UAT checks
- [ ] Click near the left edge of a badge: dropdown still starts from the badge, not the click point.
- [ ] Close and click near the right edge: dropdown appears in the same anchored position.
- [ ] Click the badge a second time: menu closes.
- [ ] Click outside: menu closes without changing status.
- [ ] Press Escape: menu closes and focus returns to badge.
- [ ] On mobile, menu remains inside viewport and does not create page-level horizontal overflow.
