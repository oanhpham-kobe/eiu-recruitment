# Responsive Browser QA — v1.2

Baseline: Full Handover v1.8 + Design System v1.7.

| Case | Viewport | Result |
|---|---:|---|
| login_mobile | 375x812 | PASS |
| candidate_form_mobile | 375x812 | PASS |
| candidate_apps_mobile | 390x844 | PASS |
| hr_inbox_mobile | 390x844 | PASS |
| permissions_mobile | 390x844 | PASS |
| interview_tablet_portrait | 768x1024 | PASS |
| hr_report_tablet_portrait | 768x1024 | PASS |
| hr_inbox_tablet_landscape | 1024x768 | PASS |
| hr_inbox_desktop | 1280x800 | PASS |

## Checks

### login_mobile — PASS
- PASS — no_page_horizontal_overflow
- PASS — no_js_errors

### candidate_form_mobile — PASS
- PASS — no_page_horizontal_overflow
- PASS — no_js_errors
- PASS — candidate_form_one_column
- PASS — privacy_present
- PASS — sticky_actions_present
- PASS — core_touch_height_44

### candidate_apps_mobile — PASS
- PASS — no_page_horizontal_overflow
- PASS — no_js_errors
- PASS — candidate_mobile_cards_visible
- PASS — candidate_desktop_table_hidden
- PASS — core_touch_height_44

### hr_inbox_mobile — PASS
- PASS — no_page_horizontal_overflow
- PASS — no_js_errors
- PASS — structured_rows_mobile
- PASS — mobile_nav_opens
- PASS — filter_sheet_opens
- PASS — drawer_full_screen_mobile
- PASS — core_touch_height_44

### permissions_mobile — PASS
- PASS — no_page_horizontal_overflow
- PASS — no_js_errors
- PASS — structured_rows_mobile
- PASS — mobile_nav_opens
- PASS — core_touch_height_44

### interview_tablet_portrait — PASS
- PASS — no_page_horizontal_overflow
- PASS — no_js_errors
- PASS — table_header_visible_tablet
- PASS — table_scroll_container

### hr_report_tablet_portrait — PASS
- PASS — no_page_horizontal_overflow
- PASS — no_js_errors
- PASS — table_header_visible_tablet
- PASS — table_scroll_container

### hr_inbox_tablet_landscape — PASS
- PASS — no_page_horizontal_overflow
- PASS — no_js_errors
- PASS — table_header_visible_tablet
- PASS — table_scroll_container

### hr_inbox_desktop — PASS
- PASS — no_page_horizontal_overflow
- PASS — no_js_errors
- PASS — sidebar_visible_desktop
- PASS — hamb_hidden_desktop

## Notes
- Screenshots are in `screenshots/`.
- This is prototype/browser evidence only; it is not production UAT or backend validation.
- Candidate mobile is a go-live UX target. Internal HR remains desktop-first; tablet keeps wide tables and mobile uses structured rows for UX-UAT.