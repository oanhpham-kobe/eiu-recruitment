# Responsive Browser QA — v1.3

Baseline: Full Handover **v1.8** + Design System **v1.7**.

> Fresh Playwright/Chromium evidence for the rebuilt responsive layer. This is prototype evidence, not production UAT.

| Case | Viewport | Result |
|---|---:|---|
| login_360 | 360x800 | PASS |
| candidate_form_360 | 360x800 | PASS |
| candidate_apps_390 | 390x844 | PASS |
| hr_inbox_390 | 390x844 | PASS |
| hr_inbox_430 | 430x932 | PASS |
| hr_overlay_short | 390x600 | PASS |
| permissions_430 | 430x932 | PASS |
| interview_tablet_portrait | 768x1024 | PASS |
| hr_report_tablet_landscape | 1024x768 | PASS |
| hr_inbox_desktop | 1280x800 | PASS |

## Checks

### login_360 — PASS
- PASS — no_page_horizontal_overflow
- PASS — no_js_errors
- PASS — no_console_errors
- PASS — document_lang
- PASS — no_duplicate_ids
- PASS — visible_buttons_have_names

### candidate_form_360 — PASS
- PASS — no_page_horizontal_overflow
- PASS — no_js_errors
- PASS — no_console_errors
- PASS — document_lang
- PASS — no_duplicate_ids
- PASS — visible_buttons_have_names
- PASS — closed_sidebar_hidden_from_at
- PASS — closed_sidebar_inert
- PASS — mobile_nav_opens
- PASS — mobile_nav_dialog_semantics
- PASS — nav_focus_moves_to_close
- PASS — background_inert_while_nav_open
- PASS — mobile_signout_available
- PASS — escape_closes_nav
- PASS — focus_restores_to_hamburger
- PASS — one_column_form
- PASS — language_switch_visible
- PASS — privacy_present
- PASS — sticky_actions_present
- PASS — labels_bound
- PASS — privacy_error_visible
- PASS — privacy_invalid_focus
- PASS — core_touch_targets_44

### candidate_apps_390 — PASS
- PASS — no_page_horizontal_overflow
- PASS — no_js_errors
- PASS — no_console_errors
- PASS — document_lang
- PASS — no_duplicate_ids
- PASS — visible_buttons_have_names
- PASS — closed_sidebar_hidden_from_at
- PASS — closed_sidebar_inert
- PASS — mobile_nav_opens
- PASS — mobile_nav_dialog_semantics
- PASS — nav_focus_moves_to_close
- PASS — background_inert_while_nav_open
- PASS — mobile_signout_available
- PASS — escape_closes_nav
- PASS — focus_restores_to_hamburger
- PASS — mobile_cards_visible
- PASS — desktop_candidate_table_hidden
- PASS — language_switch_visible
- PASS — core_touch_targets_44

### hr_inbox_390 — PASS
- PASS — no_page_horizontal_overflow
- PASS — no_js_errors
- PASS — no_console_errors
- PASS — document_lang
- PASS — no_duplicate_ids
- PASS — visible_buttons_have_names
- PASS — closed_sidebar_hidden_from_at
- PASS — closed_sidebar_inert
- PASS — mobile_nav_opens
- PASS — mobile_nav_dialog_semantics
- PASS — nav_focus_moves_to_close
- PASS — background_inert_while_nav_open
- PASS — mobile_signout_available
- PASS — escape_closes_nav
- PASS — focus_restores_to_hamburger
- PASS — structured_rows_on_phone
- PASS — filter_has_dialog_semantics
- PASS — app_inert_for_modal
- PASS — modal_focus_inside
- PASS — filter_escape_closes
- PASS — filter_focus_restored
- PASS — core_touch_targets_44

### hr_inbox_430 — PASS
- PASS — no_page_horizontal_overflow
- PASS — no_js_errors
- PASS — no_console_errors
- PASS — document_lang
- PASS — no_duplicate_ids
- PASS — visible_buttons_have_names
- PASS — closed_sidebar_hidden_from_at
- PASS — closed_sidebar_inert
- PASS — mobile_nav_opens
- PASS — mobile_nav_dialog_semantics
- PASS — nav_focus_moves_to_close
- PASS — background_inert_while_nav_open
- PASS — mobile_signout_available
- PASS — escape_closes_nav
- PASS — focus_restores_to_hamburger
- PASS — structured_rows_on_phone
- PASS — filter_has_dialog_semantics
- PASS — app_inert_for_modal
- PASS — modal_focus_inside
- PASS — filter_escape_closes
- PASS — filter_focus_restored
- PASS — core_touch_targets_44

### hr_overlay_short — PASS
- PASS — no_page_horizontal_overflow
- PASS — no_js_errors
- PASS — no_console_errors
- PASS — document_lang
- PASS — no_duplicate_ids
- PASS — visible_buttons_have_names
- PASS — closed_sidebar_hidden_from_at
- PASS — closed_sidebar_inert
- PASS — mobile_nav_opens
- PASS — mobile_nav_dialog_semantics
- PASS — nav_focus_moves_to_close
- PASS — background_inert_while_nav_open
- PASS — mobile_signout_available
- PASS — escape_closes_nav
- PASS — focus_restores_to_hamburger
- PASS — drawer_full_width_mobile
- PASS — drawer_dialog_semantics
- PASS — drawer_header_visible_short_height
- PASS — drawer_body_scrollable_short_height
- PASS — drawer_focus_inside
- PASS — drawer_escape_closes
- PASS — core_touch_targets_44

### permissions_430 — PASS
- PASS — no_page_horizontal_overflow
- PASS — no_js_errors
- PASS — no_console_errors
- PASS — document_lang
- PASS — no_duplicate_ids
- PASS — visible_buttons_have_names
- PASS — closed_sidebar_hidden_from_at
- PASS — closed_sidebar_inert
- PASS — mobile_nav_opens
- PASS — mobile_nav_dialog_semantics
- PASS — nav_focus_moves_to_close
- PASS — background_inert_while_nav_open
- PASS — mobile_signout_available
- PASS — escape_closes_nav
- PASS — focus_restores_to_hamburger
- PASS — root_permissions_visible
- PASS — core_touch_targets_44

### interview_tablet_portrait — PASS
- PASS — no_page_horizontal_overflow
- PASS — no_js_errors
- PASS — no_console_errors
- PASS — document_lang
- PASS — no_duplicate_ids
- PASS — visible_buttons_have_names
- PASS — closed_sidebar_hidden_from_at
- PASS — closed_sidebar_inert
- PASS — mobile_nav_opens
- PASS — mobile_nav_dialog_semantics
- PASS — nav_focus_moves_to_close
- PASS — background_inert_while_nav_open
- PASS — mobile_signout_available
- PASS — escape_closes_nav
- PASS — focus_restores_to_hamburger
- PASS — table_header_visible_tablet
- PASS — table_scroller_present
- PASS — wide_scroller_keyboard_reachable

### hr_report_tablet_landscape — PASS
- PASS — no_page_horizontal_overflow
- PASS — no_js_errors
- PASS — no_console_errors
- PASS — document_lang
- PASS — no_duplicate_ids
- PASS — visible_buttons_have_names
- PASS — closed_sidebar_hidden_from_at
- PASS — closed_sidebar_inert
- PASS — mobile_nav_opens
- PASS — mobile_nav_dialog_semantics
- PASS — nav_focus_moves_to_close
- PASS — background_inert_while_nav_open
- PASS — mobile_signout_available
- PASS — escape_closes_nav
- PASS — focus_restores_to_hamburger
- PASS — table_header_visible_tablet
- PASS — table_scroller_present
- PASS — wide_scroller_keyboard_reachable

### hr_inbox_desktop — PASS
- PASS — no_page_horizontal_overflow
- PASS — no_js_errors
- PASS — no_console_errors
- PASS — document_lang
- PASS — no_duplicate_ids
- PASS — visible_buttons_have_names
- PASS — sidebar_visible_desktop
- PASS — hamb_hidden_desktop
- PASS — sidebar_not_dialog_desktop

## Evidence boundaries
- Viewports include 360, 390, 430, 768, 1024 and 1280 widths plus a constrained 390×600 overlay case.
- Keyboard evidence covers mobile navigation and Modal/Drawer Escape/focus restoration.
- Candidate Form checks one-column layout, visible VI|EN, associated labels and privacy-error focus.
- No axe package was added to this static prototype. Production implementation still requires axe plus manual keyboard/screen-reader sanity evidence.
- Screenshots are in `screenshots_v13/`.