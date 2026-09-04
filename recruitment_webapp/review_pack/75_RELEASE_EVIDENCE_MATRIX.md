# 75. Release Evidence Matrix — v1.8

**Status: CURRENT implementation/UAT evidence contract; it does not claim pre-code evidence exists.**

Viewports: 375, 768, 1280, 1440px.

Candidate journeys: OTP → new form → CV → Privacy → Submit; Candidate Edit while NEW; staged file Cancel; HR opens during edit → Save blocked; Phiếu của tôi; VI/EN; mobile.

HR journeys: NEW→READ; exact Submission Application create; durable duplicate/update/reactivate; multi-round schedule/conflicts; participant remove/restore/new report; Report/email; Application Inactive → filter Inactive → Reactivate/conflict; permissions/master lifecycle.

Critical click paths include row vs checkbox/status/action, Copy draft Cancel/Save, Application Reactivate conflict, Bound user edit no rebind, referenced Master guard, email double-click one logical enqueue, dirty language switch, Drawer focus return, bulk rollback.

Accessibility evidence: axe plus keyboard-only journey, focus visibility/return, screen-reader form/landmark sanity, 200% text zoom no loss, 400% reflow where SC 1.4.10 applies (wide semantic tables may intentionally retain two-dimensional scrolling). Missing visual baseline = `INCONCLUSIVE`, not PASS.

After migrations exist: audit FK/index coverage; `EXPLAIN (ANALYZE, BUFFERS)` at NFR-sized staging; grouped pagination/RLS plans; inspect `pg_stat_statements` after realistic journeys.
