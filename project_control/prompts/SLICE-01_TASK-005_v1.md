# EIU Recruitment — Executor Prompt
## TASK-S01-005 — Login UI Shell & Authentication Feedback for Candidate OTP and Internal Google Login
### Prompt version: SLICE-01_TASK-005_v1

## 0. Execution Control

```text
SOURCE_BASELINE: Full Handover v1.17
SOURCE_SHA256: 0b39c3615dd5b34e998527a1d273e0b846458c7bd4170be46c9bb670bfcb3498
BUSINESS_STATUS: Business Logic Core v1.2 = FROZEN
TECHNICAL_STATUS: Technical Architecture v1.17 = TECHNICAL SPECIFICATION FROZEN
DESIGN_VERSION: Design System v1.8 CURRENT / REVIEWED
TASK_SCOPE: TASK-S01-005 Login UI Shell & Authentication Feedback Only
WORKTREE: D:/orca/recruitment/TASK-S01-005-login-ui
BRANCH: oanhpham-kobe/TASK-S01-005-login-ui
BASE_BRANCH: autonomy/continuous-integration-20260905-01
BASE_HEAD: 0bacba06984cf2caced490a3621f939a38bba54e
```

---

## 1. Role & Boundary

You are the Coding Executor for:
```text
TASK-S01-005: Login UI shell & authentication feedback for Candidate OTP and Internal Google login
```

### Scope & Principles
This task completes SLICE-01 (*Identity / Auth / User Provisioning*) by implementing the accessible login interface per `AUTH_AND_LOGIN.md` and Design System v1.8.
Deliver an institutional enterprise presentation supporting Candidate Email OTP and Internal Google Workspace OAuth with accessible error feedback.

### Authorized Scope
The Executor is authorized to perform:
1. Implement the login page component in `web/src/app/login/page.tsx`:
   - Dual-persona interface supporting:
     * **Ứng viên / Candidate**: Email OTP authentication (Step 1: enter email, request code; Step 2: enter 6-digit numeric OTP code, verify via `/auth/candidate/verify`).
     * **Cán bộ - Giảng viên EIU / Internal Personnel**: Google Workspace OAuth with `@eiu.edu.vn` enforcement and one-click sign-in button.
   - Error feedback banners with `role="alert"` for all canonical error codes:
     * `USER_INACTIVE`: Account is inactive or locked.
     * `FORBIDDEN`: Non-EIU domain account used for internal login.
     * `NOT_FOUND`: Account not provisioned in internal directory.
     * `IDENTITY_REBIND_FORBIDDEN`: Account bound to a different identity.
     * `INVALID_OTP` / `UNAUTHENTICATED`: Expired or incorrect OTP code.
     * `MISSING_CODE` / `AUTH_EXCHANGE_FAILED`: OAuth exchange errors.
   - Top-right `VI | EN` language toggle placeholder.
2. Implement responsive login styling in `web/src/styles/login.css` (or `globals.css`):
   - Desktop: 2-column split (visual brand panel + centered login card).
   - Mobile: clean single-column layout.
   - Institutional enterprise aesthetics adhering to Design System v1.8 (`--eiu-blue`, `--eiu-gold`, typography >= 16px).
3. Add automated tests under `web/src/__tests__/`:
   - `login-ui.test.ts`: tests persona toggle, inputs, accessible labels, button states, and error banner rendering for all error codes with `role="alert"`.
   - `login-smoke.test.ts`: live smoke check against Next.js (port 3003) verifying `/login` returns HTTP 200 and renders cleanly under dynamic nonce CSP with zero violations.
4. Run full verification: `npm run typecheck`, `npm run lint`, `npm run build`, `npm test`.
5. Update project-control records (`EVIDENCE_INDEX.yaml`, `CURRENT_STATE.md`, `TASK_REGISTRY.yaml`, and track this prompt) with status `REVIEW` (pending independent review).
6. Commit all changes cleanly on `oanhpham-kobe/TASK-S01-005-login-ui`.

### Non-Goals
- Do NOT mark TASK-S01-005 as `DONE` in this commit. Per `TASK_EXECUTION_LIFECYCLE.md` and `REVIEWER_CONTRACT.md`, the Executor records `status: REVIEW`; the `DONE` transition is reserved for the Planner after an independent implementation review PASS.
- Do NOT implement domain recruitment tables or candidate submission forms (Slice 02).
- Do NOT deploy to Vercel or mutate external databases.
- Do NOT commit `.env.local` or any secrets/keys.
- Do NOT reduce font size below 16px for form controls, body, or labels.

---

## 2. Canonical Source References

- `recruitment_webapp/design_system/AUTH_AND_LOGIN.md` (v1.8: visual direction, internal Google OAuth only, candidate Email OTP only, error states, responsive behavior)
- `recruitment_webapp/design_system/TOKENS.md` (Design System v1.8 tokens: brand colors, typography >=16px, button heights, spacing)
- `recruitment_webapp/design_system/ACCESSIBILITY.md` (Native semantic controls, labels >=16px, focus rings, accessible alert banners)
- `recruitment_webapp/review_pack/12_IMPLEMENTATION_NOTES_VERCEL_SUPABASE.md` (§Auth)
- `recruitment_webapp/review_pack/67_WEB_SECURITY_BASELINE.md` (§Transport, CSRF, no secrets)

---

## 3. Implementation Specification

All implementation code resides in `web/`:

### 3.1 Login Page Component (`web/src/app/login/page.tsx`)
Create a responsive client component:
- **Layout & Structure**:
  - Container with `role="main"` or `<main id="main-content">`.
  - Brand identity with EIU text logo and institutional gold accent.
  - Persona selector tabs: `Ứng viên / Candidate` and `Cán bộ - Giảng viên / Internal Staff` with `role="tablist"` and `aria-selected`.
- **Candidate Persona**:
  - Input field for email (`type="email"`, `name="email"`, required, label >= 16px, `aria-required="true"`).
  - "Gửi mã xác thực / Send OTP" button.
  - When OTP requested, displays 6-digit numeric input (`name="otp"`, `inputMode="numeric"`, `maxLength={6}`).
  - "Xác nhận & Đăng nhập / Verify & Sign in" button.
  - Invokes `/auth/candidate/verify` route handler.
- **Internal Personnel Persona**:
  - Clear institutional instruction: "Đăng nhập bằng tài khoản Google Workspace trường (@eiu.edu.vn)".
  - Button with Google icon: "Đăng nhập với Google / Sign in with Google Workspace".
  - Initiates Supabase OAuth flow redirecting to `/auth/callback`.
- **Accessible Error Alerts**:
  - Container with `role="alert"` and `aria-live="assertive"`.
  - Maps error codes (`USER_INACTIVE`, `FORBIDDEN`, `NOT_FOUND`, `IDENTITY_REBIND_FORBIDDEN`, `INVALID_OTP`, `MISSING_CODE`) to clear, bilingual text messages.

### 3.2 Responsive Styling (`web/src/styles/login.css` or `globals.css`)
- Use Design System v1.8 tokens:
  - Background: `linear-gradient(135deg, #f8fbfd, #eef4f8)`.
  - Login card: white surface, `--eiu-blue` title, `--ink-950` text, `border: 1px solid var(--line)`.
  - Form controls: `min-height: 48px`, `font-size: 16px`, `:focus-visible` ring.
  - Responsive breakpoint at `820px`: switches from split layout to stacked layout.

### 3.3 Automated Test Suite (`web/src/__tests__/`)
- `login-ui.test.ts`:
  - Verifies inputs, labels, and buttons are present with correct semantic attributes.
  - Verifies persona tab switching updates active tab and form fields.
  - Verifies error banners render accessible alerts with `role="alert"` for all error codes.
- `login-smoke.test.ts`:
  - Live smoke check against Next.js (port 3003):
    * Proves HTTP status 200 on `/login`.
    * Proves response headers contain dynamic `nonce-` CSP.
    * Proves page renders cleanly with zero browser CSP violations.

---

## 4. Acceptance Criteria

1. `npm run typecheck` PASS (`next typegen && tsc --noEmit`).
2. `npm run lint` PASS (`biome check`).
3. `npm run build` PASS (`next build`).
4. `npm test` PASS (all existing 70 tests + new login UI and smoke tests pass).
5. Persona switcher, Candidate OTP inputs, Internal Google button, and accessible error banners verified.
6. Responsive behavior and typography >= 16px rule verified.
7. Zero secrets or credentials committed.
8. `project_control/EVIDENCE_INDEX.yaml` updated under `LOGIN-UI-001` with test evidence.
9. `project_control/CURRENT_STATE.md` and `project_control/TASK_REGISTRY.yaml` updated with `status: REVIEW` (pending independent review), with prompt SHA-256 bound.
10. Exactly one clean commit on `oanhpham-kobe/TASK-S01-005-login-ui`.
