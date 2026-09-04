# Recruitment Responsive Rebuild — Discovery v1.3

## Repository
- root: static prototype folder `eiu_recruitment_clickable_prototype_responsive_v1_3`
- branch: N/A — this artifact is not a Git repository
- commit: N/A
- dirty state: N/A; work is versioned by artifact folder/ZIP
- framework/runtime: plain HTML + CSS + vanilla JavaScript; no React/Next.js/Tailwind/package manager in this prototype

## Source authorities
- current handover/spec: **Full Handover v1.8**
- current Design System: **Design System v1.7**
- current responsive authority: `RESPONSIVE.md`, `ACCESSIBILITY.md`, `PAGE_OVERRIDES_V1_7.md`, `MASTER.md`
- responsive prototype baseline audited: v1.2

## Existing responsive implementation
- shared foundations: app shell, sidebar, toolbar, tables, drawer/modal, Candidate form grid
- page-specific responsive code: `responsive-v12.css` + `responsive-v12.js`
- mobile representation: Candidate submissions use summary cards; HR operational tables use one semantic table rendered as structured rows through CSS
- tablet representation: wide semantic tables retained inside horizontal scroll containers
- browser QA: Playwright/Chromium script already present
- E2E stack: Playwright only; no React/component test stack

## Skills / engineering lanes applied
- Karpathy-style guidelines: **applied as workflow** — audit first, surgical changes, preserve correct code, define fresh verification
- accessibility: **applied directly** — semantics, labels, focus management, keyboard, touch target, reduced motion, responsive reflow
- browser-qa: **applied directly** with Playwright/Chromium and fresh responsive cases
- frontend checklist: **applied as final prototype audit**, limited to relevant frontend/responsive concerns
- verification-before-completion: **applied** — final claims require fresh artifact validation/browser evidence
- Vercel React best practices: **not applicable to this static prototype**; reserved for production React/Next implementation
- composition patterns: **not triggered**; no shared React component API exists here
- react-testing / tdd: **not triggered**; responsive behavior is verified in the browser rather than adding a new framework to static HTML
- diagnosing-bugs: used only where QA exposed a concrete responsive issue (44px filter width)
- GitNexus: **not applicable** because this artifact is not a Git/source-code repository with a component dependency graph

## GitNexus
- available/index current: N/A for this artifact
- shared consumers were identified by direct source audit instead: shell, sidebar, toolbar, table shell, form fields, Drawer/Modal

## Audit classification
| Area | Classification | Reason |
|---|---|---|
| Candidate mobile cards | KEEP | Correct narrow-screen summary pattern; data/action semantics preserved |
| HR mobile structured table rows | KEEP | Reuses one table/business render path; avoids duplicate mobile business logic |
| Tablet wide tables | KEEP | Matches Design System: horizontal scroll is intentional for dense HR tables |
| Off-canvas sidebar | ADAPT | Visual behavior correct; needed inert/ARIA/focus/Escape/restore semantics |
| Drawer / Modal | ADAPT | Sizing correct; needed dialog semantics, focus trap, Escape, background inert, focus restore |
| Candidate form layout/upload/privacy | ADAPT | Structure correct; needed label normalization, privacy error/focus strategy, narrow-width polish |
| Toolbar/filter actions | ADAPT | Actions remained available; 390px filter control was 42px wide and required 44px correction |
| Candidate header language switch | ADAPT | v1.2 hid VI/EN at <=390px; current authority requires it remain reachable |
| Base business JS/state | KEEP | Responsive rebuild must not create separate mobile business behavior |
| React/GitNexus architecture | REMOVE FROM THIS PHASE | Not relevant to static prototype; defer to production repository |

## Proposed responsive architecture
1. Keep one underlying business/action implementation.
2. Use CSS for layout changes whenever possible; no width-driven JS rendering logic.
3. Candidate portal may use a compact mobile presentation generated from the same submission data.
4. HR operational tables remain one semantic data source; tablet uses horizontal scroll, phone uses structured row presentation.
5. Sidebar, Drawer and Modal share one overlay/focus-management contract.
6. Responsive state changes must not hide business-critical actions or VI/EN access.
7. Browser verification covers width and constrained-height cases.

## Implementation order used
1. audit + contract
2. shared accessibility/focus foundation
3. shell/navigation
4. toolbar/actions
5. forms
6. table/list behavior
7. drawers/modals
8. browser QA
9. final frontend audit
10. user visual acceptance

## Risks
- Static prototype cannot prove React hydration/component behavior; that belongs to production implementation.
- CSS structured rows preserve table DOM semantics but final screen-reader/browser combinations must be tested again on the real application.
- Browser QA here does not replace production axe/manual screen-reader UAT.
