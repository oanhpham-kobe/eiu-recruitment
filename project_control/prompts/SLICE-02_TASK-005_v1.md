# EIU Recruitment — Executor Prompt
## TASK-S02-005 — Candidate Portal application form UI shell, autosave, and document uploader
### Prompt version: SLICE-02_TASK-005_v1

## 0. Execution Control

```text
SOURCE_BASELINE: Full Handover v1.17
SOURCE_SHA256: 0b39c3615dd5b34e998527a1d273e0b846458c7bd4170be46c9bb670bfcb3498
BUSINESS_STATUS: Business Logic Core v1.2 = FROZEN
TECHNICAL_STATUS: Technical Architecture v1.17 = TECHNICAL SPECIFICATION FROZEN
TASK_SCOPE: TASK-S02-005 Candidate Portal application form UI shell, autosave, and document uploader Only
WORKTREE: D:/orca/recruitment/TASK-S02-005-portal-form
BRANCH: oanhpham-kobe/TASK-S02-005-portal-form
BASE_BRANCH: autonomy/continuous-integration-20260905-01
BASE_HEAD: c1b93380cf0e428c0c1692ae5e24bcfefbe88c42
```

---

## 1. Governance & Compact Routing

```yaml
GOVERNANCE:
  pack_version: "1.1"
  SKILLS_REQUIRED:
    - react-patterns
    - accessibility
    - vercel-react-best-practices
    - supabase
  SKILLS_RESOLVED:
    - react-patterns (skills/react-patterns)
    - accessibility (skills/accessibility)
    - vercel-react-best-practices (~/.omp/agent/skills/vercel-react-best-practices)
    - supabase (skills/supabase)
  SKILLS_APPLIED:
    - react-patterns: "accessible form composition, controlled and uncontrolled component boundaries, debounced autosave hook"
    - accessibility: "WCAG 2.2 Level AA compliance, semantic form structure (<form>, <fieldset>, <legend>), visible focus indicators, aria-describedby validation error association, touch targets >= 44x44px"
    - vercel-react-best-practices: "React 19 Server/Client component separation, zero client bundle bloat, responsive layouts"
    - supabase: "two-phase storage upload integration, server action/command runner binding"
  GRAPH_ROUTE: DIRECT_SOURCE_LSP_ONLY
  GRAPH_ROUTE_REASON: "Localized Next.js App Router UI pages, React form components, autosave hook, and client tests directly mapped to Design System v1.8 and document 03"
  PRINCIPLE_PROFILE: "CANDIDATE_PORTAL_ACCESSIBLE_FORM_SHELL"
  EVIDENCE_DELTA: "PORTAL-FORM-001"
```

---

## 2. Canonical Source References

- `recruitment_webapp/review_pack/03_CANDIDATE_FORM_AND_PORTAL.md` (§1 Form principles: single page, no wizard, auto email; §2 Form fields: General Info, Education, Document attachments, Privacy acknowledgement; §5 Candidate Portal – Phiếu của tôi: 3-status mapping)
- `recruitment_webapp/review_pack/10_UI_UX_SPEC.md` (§Candidate Portal mobile priority, §Typography hard rule: font >= 16px)
- `recruitment_webapp/design_system/TOKENS.md` / `web/src/styles/tokens.css` (Design System v1.8 color, spacing, radius, status badge tokens)
- `recruitment_webapp/review_pack/41_STORAGE_AND_UPLOAD_SECURITY.md` (Upload policy: PDF, DOC/DOCX, PPT/PPTX, PNG/JPG/JPEG, max 5MB, max 5 current files, CV required)
- `recruitment_webapp/review_pack/37_BACKEND_COMMAND_CONTRACTS.md` (§4 Candidate Submission commands: `submit_candidate_submission`, `update_candidate_submission`, form session lifecycle)

---

## 3. Implementation Specification

### 3.1 Component & Route Architecture

#### 1. Page Route: `web/src/app/candidate/page.tsx`
- Client entry point wrapped in candidate navigation layout.
- If candidate has prior submissions, renders tab switcher:
  - Tab 1: `Đăng ký mới / New Application`
  - Tab 2: `Phiếu của tôi / My Applications`
- If no prior submissions exist, defaults directly to `CandidateForm`.
- Displays candidate header with verified email, status, and logout action.

#### 2. Main Form Shell: `web/src/components/candidate/CandidateForm.tsx`
- Single-page form (no wizard or pagination steps per document 03).
- Structured with semantic `<fieldset>` and `<legend>` groups:
  1. **Thông tin chung / General Information**:
     - `fullName` (Họ và tên): text input, required.
     - `dateOfBirth` (Ngày sinh): date input, required.
     - `gender` (Giới tính): select input with `MALE` (Nam), `FEMALE` (Nữ), `OTHER` (Khác), required.
     - `address` (Địa chỉ hiện tại): text input, required.
     - `email` (Email liên hệ): read-only input, pre-populated from verified Auth.
     - `phone` (Số điện thoại): tel input, required.
  2. **Quá trình học tập / Education History** (`EducationSection.tsx`):
     - Multi-row education entries.
     - Per row: `institutionName` (Trường), `degreeName` (Bằng cấp/Học vị), `major` (Chuyên ngành), `startYear` (Năm bắt đầu), `endYear` (Năm tốt nghiệp), `gpa` (Điểm TB/GPA).
     - `+ Thêm quá trình học tập` button.
     - Remove button per row.
     - Optional in Phase 1 (not required to submit).
  3. **Hồ sơ đính kèm / Document Attachments** (`DocumentUploader.tsx`):
     - Document types: `CV_RESUME` (Required), `DEGREE` (Optional), `TRANSCRIPT` (Optional), `CERTIFICATE` (Optional), `OTHER` (Optional).
     - Two-phase upload workflow:
       * Client file selection: checks extension (`.pdf`, `.doc`, `.docx`, `.ppt`, `.pptx`, `.png`, `.jpg`, `.jpeg`) and size <= 5 MB.
       * Calls `reserveCandidateFormUpload` to obtain temp reservation.
       * Direct upload to private quarantine bucket via Storage client.
       * Calls `recordCandidateUploadCompleted`.
       * Calls `stageCandidateDocumentChange` with `ADD` or `REPLACE`.
       * Renders list of attached files with filename, size, type, and remove/replace actions.
  4. **Xác nhận quyền riêng tư / Privacy Notice Acknowledgement**:
     - Displays server-pinned privacy notice version.
     - Single required checkbox: "Tôi đã đọc và đồng ý với Thông báo về quyền riêng tư của Đại học Quốc tế Miền Đông".
     - Unchecked by default for new submissions.
     - View notice dialog / expandable panel.
  5. **Action Controls**:
     - `Nộp hồ sơ / Submit Application` button (primary).
     - `Hủy / Cancel` button (calls `cancelCandidateFormSession`, discards staged uploads, clears draft).

#### 3. Autosave Hook: `web/src/hooks/useAutosave.ts`
- Debounced client-side draft persistence to `localStorage` (`eiu_candidate_form_draft_${sessionId}`).
- Automatically restores form inputs on page refresh or reload.
- Renders accessible autosave status indicator (`role="status"`, `aria-live="polite"`).
- Automatically clears draft upon successful submission or cancellation.

#### 4. Submissions List View: `web/src/components/candidate/SubmissionsList.tsx`
- Table of candidate's past submissions:
  - Columns: `STT` (No.), `Ngày ứng tuyển` (Submitted At), `Trạng thái` (Status), `Thao tác` (Actions).
- 3-Status Display Mapping per document 03 §5:
  - `NEW` $\rightarrow$ **Mới** (Badge: Info/Primary). Actions: `Chỉnh sửa / Edit` (opens form in EDIT mode).
  - `READ` or `PROCESSED` $\rightarrow$ **Đang xử lý** (Badge: Warning). Actions: `Xem chi tiết` (Read-only).
  - `DONE` or `CLOSED` $\rightarrow$ **Hoàn thành** (Badge: Success). Actions: `Xem chi tiết` (Read-only).

#### 5. Responsive Styling: `web/src/styles/candidate-portal.css`
- Design System v1.8 token alignment (`--eiu-blue`, `--eiu-gold`, `--canvas`, `--surface`, `--ink-950`).
- Typography hard rule: font size $\ge 16\text{px}$ for all labels, inputs, table text, and buttons.
- Touch targets $\ge 44\times 44\text{px}$ for buttons and inputs.
- Accessible focus outlines (`outline: 2px solid var(--eiu-blue); outline-offset: 2px`).
- Mobile responsive column-stack layout for small viewports.

---

### 3.2 Verification Tests: `web/src/__tests__/candidate-portal.test.ts`

- Test suite verifying:
  1. Form renders all required semantic sections (`General Info`, `Education`, `Attachments`, `Privacy`).
  2. Required field validation: empty name, phone, date of birth, address, or unchecked privacy notice displays accessible error.
  3. Immutable email: verified email is read-only.
  4. Dynamic education rows: adding and removing education items updates form state.
  5. Document uploader client validation: rejects `.exe`, `.html`, `.zip` files and files $> 5\text{MB}$.
  6. Two-phase upload flow: reservation $\rightarrow$ upload $\rightarrow$ completion $\rightarrow$ stage change.
  7. Document constraints: required CV check prevents submit if CV is missing; max 5 files constraint enforced.
  8. Autosave hook: persists draft to storage, debounces writes, restores data, and clears on submit.
  9. Submissions list 3-status mapping: maps `NEW` $\rightarrow$ "Mới", `READ`/`PROCESSED` $\rightarrow$ "Đang xử lý", `DONE`/`CLOSED` $\rightarrow$ "Hoàn thành".
  10. Edit submission transition: clicking edit on `NEW` submission opens form in `EDIT_SUBMISSION` mode with prefilled data.
  11. Cancel action: invokes cancel command and discards changes.
  12. WCAG 2.2 AA accessibility: labels associated with inputs, `aria-required`, `aria-invalid`, focus visible styles, and status announcements.

---

## 4. Acceptance & Verification Contract

1. `npm run typecheck` in `web/` PASS with 0 errors.
2. `npm run lint` in `web/` PASS with 0 errors.
3. `npm run build` in `web/` PASS.
4. `npm run test` in `web/` PASS (all existing + new tests green).
5. Clean local migration replay test on ephemeral test port PASS.
6. Secret scan PASS.
7. Git diff clean, exactly one commit on `oanhpham-kobe/TASK-S02-005-portal-form`.
