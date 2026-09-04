# EIU Recruitment — Executor Prompt
## TASK-S00-005 — Design v1.8 Foundation Shell + Accessibility/Test Harness
### Prompt version: SLICE-00_TASK-005_v1

## 0. Execution Control

```text
SOURCE_BASELINE: Full Handover v1.17
SOURCE_SHA256: 0b39c3615dd5b34e998527a1d273e0b846458c7bd4170be46c9bb670bfcb3498
BUSINESS_STATUS: Business Logic Core v1.2 = FROZEN
TECHNICAL_STATUS: Technical Architecture v1.17 = TECHNICAL SPECIFICATION FROZEN
DESIGN_VERSION: Design System v1.8 CURRENT / REVIEWED
TASK_SCOPE: TASK-S00-005 Design v1.8 Shell & Accessibility Harness Only
WORKTREE: D:/orca/recruitment/TASK-S00-005-shell
BRANCH: oanhpham-kobe/TASK-S00-005-shell
BASE_BRANCH: autonomy/continuous-integration-20260905-01
BASE_HEAD: bdf09a3d0a0f236c88dff219cb426bc9aab6824b
```

---

## 1. Role & Boundary

You are the Coding Executor for:
```text
TASK-S00-005: Design v1.8 foundation shell + accessibility/test harness
```

### Scope & Principles
This is a **foundation shell and design system token integration** task per Slice-00 rule ledger.
Establish institutional enterprise styling, semantic landmarks, accessibility skip-navigation, and error/loading boundaries without implementing domain business screens.

### Authorized Scope
The Executor is authorized to perform:
1. Integrate Design System v1.8 CSS custom properties and design tokens in `web/src/styles/tokens.css` (or `web/src/app/globals.css`).
2. Implement semantic App Shell components in `web/src/components/shell/`:
   - `SkipLink.tsx`: accessible keyboard skip-to-content link targeting `#main-content`.
   - `Sidebar.tsx`: 244px fixed sidebar with EIU brand mark, navigation items, and user card slot.
   - `Header.tsx`: sticky topbar with page title slot and utility region (`VI | EN` switcher placeholder).
   - `AppShell.tsx`: semantic layout wrapper combining SkipLink, Sidebar, Header, and `<main id="main-content">`.
3. Implement App Router state boundaries in `web/src/app/`:
   - `loading.tsx`: accessible loading state (`role="status"`, `aria-live="polite"`).
   - `error.tsx`: accessible error boundary with reset action.
   - `not-found.tsx`: accessible 404 page.
4. Update `web/src/app/layout.tsx` to include `globals.css`, render `AppShell`, preserve dynamic rendering opt-in (`export const dynamic = 'force-dynamic'`), and set `lang="vi"`.
5. Add automated accessibility and design token tests under `web/src/__tests__/`:
   - `tokens.test.ts`: validates presence and values of brand, sidebar, semantic, typography, and spacing tokens.
   - `shell-a11y.test.ts`: validates semantic landmarks (`<header>`, `<main id="main-content">`, `<aside>`, `<nav>`), skip-link target, focus visibility styles, and loading boundary status semantics.
   - `shell-smoke.test.ts`: live smoke check asserting AppShell renders cleanly without errors under dynamic nonce CSP.
6. Update project-control records (`EVIDENCE_INDEX.yaml`, `CURRENT_STATE.md`, `TASK_REGISTRY.yaml`, and track this prompt) with status `REVIEW` (pending independent review).
7. Commit all changes cleanly on `oanhpham-kobe/TASK-S00-005-shell`.

### Non-Goals
- Do NOT mark TASK-S00-005 as `DONE` in this commit. Per `TASK_EXECUTION_LIFECYCLE.md` and `REVIEWER_CONTRACT.md`, the Executor records `status: REVIEW`; the `DONE` transition is reserved for the Planner after an independent implementation review PASS.
- Do NOT implement domain recruitment tables, application inbox, candidate forms, or interview schedules (Slice 01–08).
- Do NOT deploy to Vercel or mutate external databases.
- Do NOT commit `.env.local` or any secrets/keys.
- Do NOT reduce typography sizes below 16px for body, table, badges, or labels.

---

## 2. Canonical Source References

- `recruitment_webapp/design_system/TOKENS.md` (Design System v1.8: brand colors, sidebar tokens, semantic status colors, typography, badge sizing, spacing scale)
- `recruitment_webapp/design_system/ACCESSIBILITY.md` (v1.8: typography >=16px, native semantic controls, focus & keyboard, skip-link, reflow/zoom, prefers-reduced-motion)
- `recruitment_webapp/design_system/MASTER.md` (v1.8: 244px fixed sidebar, sticky topbar, institutional clean UI)
- `recruitment_webapp/responsive_prototype/styles.css` (prototype styling and visual baseline)
- `project_control/prompts/SLICE-00_MASTER_PLAN_REFERENCE.md` (§Rule Ledger: Design v1.8 token integration)

---

## 3. Implementation Specification

All implementation code resides in `web/`:

### 3.1 Design System v1.8 Tokens (`web/src/styles/tokens.css` or `web/src/app/globals.css`)
Incorporate complete Design System v1.8 tokens:
- **Brand Colors**:
  `--eiu-blue: #144069;`
  `--eiu-gold: #A78656;`
  `--eiu-cream: #F6F1E8;`
  `--canvas: #F8F6F1;`
  `--surface: #FFFFFF;`
  `--ink-950: #303033;`
  `--ink-600: #68686B;`
  `--line: #E2D9CC;`
- **Sidebar Tokens**:
  `--sidebar-width: 244px;`
  `--sidebar-bg-top: #0E416F;`
  `--sidebar-bg-bottom: #082F52;`
  `--sidebar-text: #F7FAFC;`
  `--sidebar-muted: #D9E4EE;`
  `--sidebar-heading: #E6C88F;`
  `--sidebar-active-bg: #FFFFFF;`
  `--sidebar-active-text: #144069;`
  `--sidebar-border: rgba(255, 255, 255, 0.14);`
- **Semantic Status Colors (WCAG 2.2 AA >= 4.5:1 contrast)**:
  - Success: text `#3B6A2A`, bg `#EAF3E6`
  - Warning: text `#8A4F00`, bg `#FFF0DE`
  - Danger: text `#B44425`, bg `#F8E5E0`
  - Info: text `#144069`, bg `#E5EDF5`
  - Neutral: text `#68686B`, bg `#EEF0F1`
  - Follow-up: text `#4B479D`, bg `#ECEBFA`
- **Typography Hard Rule**:
  - Font stack: `"Be Vietnam Pro", "Segoe UI", system-ui, sans-serif;`
  - Body text, table headers, table cells, form labels, buttons, and status badges must be **>= 16px**.
  - Helper/meta text is 14px only when secondary.
- **Accessibility & Motion**:
  - Focus ring: `:focus-visible { outline: 2px solid var(--eiu-blue); outline-offset: 2px; }`
  - Reduced motion: `@media (prefers-reduced-motion: reduce) { * { animation-duration: 0.01ms !important; transition-duration: 0.01ms !important; } }`
- **Skip Link Styling**:
  - `.skip-link { position: absolute; top: -999px; left: 16px; background: var(--eiu-blue); color: #fff; padding: 12px 16px; z-index: 100; border-radius: 6px; font-weight: 600; text-decoration: none; }`
  - `.skip-link:focus { top: 16px; }`

### 3.2 Semantic App Shell (`web/src/components/shell/`)
- `SkipLink.tsx`:
  - Renders `<a href="#main-content" className="skip-link">Chuyển đến nội dung chính / Skip to main content</a>`.
- `Sidebar.tsx`:
  - Semantic `<aside className="sidebar" aria-label="Thanh điều hướng chính / Main sidebar">`.
  - Brand header with EIU text logo and gold accent mark.
  - `<nav aria-label="Menu chức năng / Navigation menu">`: navigation items with accessible active state (`aria-current="page"`).
  - Bottom user card container with accessible avatar and role indicator.
- `Header.tsx`:
  - Semantic `<header className="topbar">`.
  - Page title slot (`<h1>` or section title).
  - Utility region: language toggle `VI | EN` with accessible labels.
- `AppShell.tsx`:
  - Combines `<SkipLink />`, `<Sidebar />`, `<Header />`, and `<main id="main-content" tabIndex={-1}>`.

### 3.3 App Router Boundaries (`web/src/app/`)
- `loading.tsx`:
  - Accessible loading indicator with `<div role="status" aria-live="polite" className="loading-indicator">Đang tải... / Loading...</div>`.
- `error.tsx`:
  - Client component error boundary: displays accessible alert banner with reset button (`Thử lại / Try again`).
- `not-found.tsx`:
  - Accessible 404 page with return-home navigation link.

### 3.4 Automated Test Suite
Add automated tests under `web/src/__tests__/`:
- `tokens.test.ts`:
  - Reads `globals.css` / `tokens.css` and verifies that all canonical brand colors (`#144069`, `#A78656`), sidebar tokens (244px, `#0E416F`, `#082F52`), semantic colors (`#3B6A2A`, `#8A4F00`, `#B44425`), and typography minimum 16px rules are present.
- `shell-a11y.test.ts`:
  - Validates that `AppShell` renders semantic landmarks (`<aside>`, `<header>`, `<main id="main-content">`, `<nav>`).
  - Validates that `SkipLink` points to `#main-content`.
  - Validates that `loading.tsx` has `role="status"` and `aria-live="polite"`.
  - Validates `:focus-visible` ring and `prefers-reduced-motion` rules exist in CSS.
- `shell-smoke.test.ts`:
  - Live smoke check against Next.js (port 3003) verifying:
    - HTTP 200 on `/`.
    - Page HTML contains `<aside>`, `<nav>`, `<header>`, `<main id="main-content">`, and SkipLink.
    - Page renders cleanly under dynamic nonce CSP with zero CSP violations.

---

## 4. Acceptance Criteria

1. `npm run typecheck` PASS (`next typegen && tsc --noEmit`).
2. `npm run lint` PASS (`biome check`).
3. `npm run build` PASS (`next build`).
4. `npm test` PASS (all existing 17 tests + new token, shell a11y, and smoke tests passing).
5. All Design System v1.8 brand, sidebar, semantic, typography, and spacing tokens present and verified.
6. AppShell contains semantic landmarks (`<aside>`, `<nav>`, `<header>`, `<main id="main-content">`) and SkipLink.
7. Focus ring (`:focus-visible`) and reduced-motion rules present.
8. Live smoke test confirms HTTP 200 with AppShell rendered and zero CSP violations.
9. Secret scan PASS: zero credentials committed.
10. `project_control/EVIDENCE_INDEX.yaml` updated under `SHELL-001` with test evidence.
11. `project_control/CURRENT_STATE.md` and `project_control/TASK_REGISTRY.yaml` updated with `status: REVIEW` (pending independent review), with prompt SHA-256 bound.
12. Exactly one clean commit on `oanhpham-kobe/TASK-S00-005-shell`.
