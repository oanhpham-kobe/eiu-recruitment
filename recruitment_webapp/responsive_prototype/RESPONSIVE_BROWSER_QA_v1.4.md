# Responsive Browser QA v1.4

## Environment
- Engine: Chromium via Playwright
- Artifact: static HTML/CSS/JS Responsive Prototype v1.4
- Business baseline: Full Handover v1.8
- Design baseline: Design System v1.7

## Automated result
**49 / 49 PASS — 0 FAIL**

### Viewport / overflow
Interview and HR Report were checked at:
- 360×800
- 390×844
- 430×844
- 768×1024
- 1024×768
- 1280×800

Result: no unexpected page-level horizontal overflow in the tested routes.

### Visual contract checks
- Interview badge width = 144px: PASS
- HR Report `Đã gửi báo cáo` badge width = 144px: PASS
- Long English `Awaiting Confirmation` stays 144px and wraps vertically: PASS
- Interview time order = time first, date second: PASS
- Interview time stays one visual line at 430px when space permits: PASS
- Mobile `Thời gian phỏng vấn` label = nowrap: PASS

### Interaction checks
- Application checkbox / delete-enable / email / bulk status: PASS
- Interview checkbox / bulk status / copy / participant email / delete confirmation: PASS
- HR Report checkbox / bulk status: PASS
- Candidate Education Add/Remove: PASS
- Candidate Privacy validation: PASS
- Users & Permissions Add/Assign flows: PASS
- No dead buttons across seven core routes: PASS
- No dead buttons in representative Candidate / Interview / HR Report / Candidate-own drawers: PASS
- JS/console errors during QA: 0

Machine-readable evidence: `RESPONSIVE_QA_RESULTS_v1.4.json`.
