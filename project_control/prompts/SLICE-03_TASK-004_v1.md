# EIU Recruitment — Executor Prompt
## TASK-S03-004 — HR Application Inbox grouped table shell, search/filter, and expandable Candidate rows
### Prompt version: SLICE-03_TASK-004_v1

## 0. Execution Control

```text
SOURCE_BASELINE: Full Handover v1.17
TASK_SCOPE: TASK-S03-004 only
BASE_BRANCH: autonomy/continuous-integration-20260905-01
BASE_HEAD: resolve directly immediately before implementation
ONE_TASK_COMMIT: required on the task branch
NO_DEPLOY_NO_MAIN_NO_PRODUCTION_MUTATIONS
```

## 1. Governance & Compact Routing

```yaml
GOVERNANCE:
  SKILLS_REQUIRED:
    - react-patterns
    - vercel-react-best-practices
    - accessibility
    - react-testing
    - supabase
    - security-review
    - browser-qa
  SKILLS_RESOLVED:
    - react-patterns (.agents/skills/react-patterns/SKILL.md)
    - vercel-react-best-practices (C:\Users\Admin\.omp\agent\skills\vercel-react-best-practices\SKILL.md)
    - accessibility (.agents/skills/accessibility/SKILL.md)
    - react-testing (.agents/skills/react-testing/SKILL.md)
    - supabase (.agents/skills/supabase/SKILL.md)
    - security-review (.agents/skills/security-review/SKILL.md)
    - browser-qa (.agents/skills/browser-qa/SKILL.md)
  SKILLS_INTENDED_APPLICATION:
    - react-patterns: "minimal client boundary for local inbox interaction state; serializable server-to-client data"
    - vercel-react-best-practices: "server-first read model, small client island, no avoidable waterfall or bundle expansion"
    - accessibility: "semantic fixed-grid table, keyboard expand control, labels, status semantics, focus and reflow"
    - react-testing: "consumer-observable grouped-table/filter/keyboard-state tests"
    - supabase: "server-side Supabase read model, current RLS-aware client boundary, and only explicit selected fields"
    - security-review: "server-derived submissions.view/Root authorization before PII fetch and untrusted search input boundary"
    - browser-qa: "authorized local grouped-table responsive and keyboard journey when a runnable target exists"
  GRAPH_ROUTE: DIRECT_SOURCE_LSP_ONLY
  GRAPH_ROUTE_REASON: "Localized known page and shell work has direct canonical contracts and no shared API contract change."
  PRINCIPLE_PROFILE: "GROUPED_CANDIDATE_INBOX_ACCESSIBLE_READ_MODEL"
  EVIDENCE_DELTA: "APPLICATION-INBOX-001"
```

Before dependent implementation, read each effective resolved `SKILL.md`. Persist post-execution `SKILL_USAGE` under `TASK-S03-004` with `provider`, `availability`, `loaded`, `applied`, and concrete `applied_to`; declarations above are not runtime proof. Persist `GRAPH_USAGE` under `APPLICATION-INBOX-001`; direct route means `graph_used: NO` and names direct source/LSP surfaces. Do not fabricate skill, graph, or MCP usage. Use bundled Next 16.3 documentation first; Context7 only if material external clarification is actually required.

## 2. Canonical Source References

- `review_pack/04_HR_APPLICATION_INBOX.md` §§2–3, 10, 160–166.
- `review_pack/13_ACCEPTANCE_CRITERIA_AND_TEST_CASES.md` AC-05, AC-07, AC-08, AC-GRP-01, AC-OPEN-SUB-01/02.
- `review_pack/37_BACKEND_COMMAND_CONTRACTS.md` §bulk status selection semantics; `55_COMMAND_COVERAGE_MATRIX.md` grouped read contract.
- `review_pack/81_RESPONSIVE_PROTOTYPE_INTEGRATION.md` frozen Inbox corrections.
- Design System v1.8: `TABLE_LAYOUT.md` §§1–6, 10–14; `PATTERNS.md` §§1–5, 14; `ACCESSIBILITY.md` §§2–7; `TOKENS.md` §§3–9; `DESIGN_REVIEW_CHECKLIST.md` Tables/Status/Accessibility.
- Prototype evidence: `responsive_prototype/responsive-v12.js` `applicationsPage` only as interaction/visual reference, not production source.
- Existing source: `web/src/app/page.tsx`, `web/src/components/shell/*`, `web/src/styles/tokens.css`, `web/src/app/globals.css`, `web/src/lib/auth/session.ts`, `web/src/lib/supabase/server.ts`, and current S03 command modules.

## 3. Required Implementation

### 3.1 Scope and boundaries

Implement the internal HR Application Inbox route/page and only its grouped read UI: Candidate-group table shell, local PII search, non-sensitive filters, expandable historical Submission rows, selection presentation, pagination presentation, loading/empty/error states, and the minimal server read model necessary to populate it.

- Keep the page Server Component by default. Isolate only interactive search/filter/expanded/selection behavior in a focused Client Component; pass serializable data.
- Enforce internal authenticated `submissions.view` or Root Admin before fetching/rendering PII. Browser visibility is not authorization. Do not expose a service-role key or bypass RLS.
- Use existing trusted commands only where already relevant. This task does **not** invoke bulk mutations, open-drawer mutation, candidate lifecycle, Application creation, document preview, HR note editing, email, or any S03-005 Drawer flow.
- Do not create browser loops or mutate data. A `NEW` child row is not opened during this task; do not implement implicit read-status transition.
- Do not add a new reusable component framework, global state library, or speculative API layer.

### 3.2 Grouped data/read contract

- Page Candidate groups, never raw Submissions. Each parent summary derives `name / DOB / gender / phone / status / HR note` from its deterministic latest Submission ordered `submitted_at DESC, submission_id DESC`; verified Candidate email remains Candidate identity.
- Historical children remain tied to their Candidate and appear only within that group. Parent pagination never splits children.
- Preserve requested stable sorting with Candidate ID tie-breaker. Do not persist name/email/phone query text in URL. Non-sensitive filter/page/sort state may be URL state only if actually implemented without leaking PII.
- Search supports name, email, and phone matching. It must be debounced or otherwise avoid fetch per keystroke. Filters present only supported current values: Submission status, submitted-date range, Candidate active/inactive, NEW/READ, and has/no Application. Use explicit empty and error states; retain the table shell/column widths while loading.
- The read query must explicitly select only fields consumed by the view. Null-safe map database values to stable UI data; no client SQL/database credential.

### 3.3 Table and interaction contract

- Render the normative semantic `<table>` with one `<colgroup>`, `table-layout: fixed`, Application Inbox `min-width: 1560px`, and exact desktop columns/order/widths: `Select 48 | Tên 220 | Email 250 | Ngày sinh 130 | Giới tính 100 | SĐT 150 | Trạng thái 150 | HR Note 420 | Action 92`.
- Keep the toolbar outside the horizontal scroller; sticky header; sticky Select + name context columns; wrapping business text; `.wrap-anywhere` only for unbreakable email values. No font reduction or arbitrary inner-card children.
- Parent pointer row surface expands/collapses. Only one Candidate group is expanded. If one Submission, parent is non-expandable and remains a non-mutating read shell—do not open a drawer in this slice.
- First/name cell supplies native expand/collapse button with clear accessible Candidate context, `aria-expanded`, `aria-controls`, visible focus, and keyboard operation. Checkbox/filter/action controls stop propagation.
- Expanded children stay in the same table grid and expose `Ngày ứng tuyển`, textual Submission status, and HR Note aligned to approved parent columns. Historical child rows are read-only. Do not leave an unaligned free-floating card.
- Status always has a textual Submission status label; badges use approved 16px semantic contrast colors and `--badge-width-submission` behavior. Candidate Inactive is separately rendered as its own Candidate/account lifecycle badge using candidate badge semantics; it never replaces or mutates the underlying latest Submission status. A read-only badge is not a button. Selection UI does not claim a mutation is available; selected-count feedback may be presented as non-mutating context.
- Search input has a persistent accessible label and no PII query serialization. Filter controls have visible labels and keyboard operation. Provide a clear-search/reset affordance when state exists.

### 3.4 Design/responsive contract

- Use current shell/tokens; do not redesign sidebar/header. Main/table/body text and badge text stay 16px or larger. Use 42–44px controls and touch layouts ≥44px targets.
- At narrow widths retain intentional two-dimensional table scrolling rather than collapse essential columns or reduce text. Verify 200% text zoom, visible focus in sticky cells, and long Vietnamese/English text wrapping.
- Respect reduced motion. Do not use color alone for state. No Drawer, dialog, or status menu is introduced in this slice.

### 3.5 Tests and verification

Add only meaningful tests following project conventions. At minimum assert:

1. internal view-authorized page/read seam rejects unauthenticated, candidate, and internal caller without `submissions.view`, while Root bypass is allowed;
2. parent projection uses the latest Submission deterministically and groups/paginates by Candidate without split children;
3. PII search is local/request-only rather than URL state; supported filter predicates and reset state yield observable results;
4. table has the exact normative colgroup/header order, semantic expand buttons, one expanded group at a time, child alignment semantics, and nested control propagation isolation;
5. keyboard expand control changes `aria-expanded`; textual statuses, labels, loading, empty, and error feedback remain accessible;
6. wide-table responsive class/min width, sticky context, and no generic `overflow-wrap:anywhere` regression are observable.

Run focused tests and full `npm run test`, `npm run typecheck`, `npm run lint`, `npm run build`. For a meaningful React/Next diff run `npx react-doctor@latest --verbose --scope changed`. Browser QA is required if a runnable authorized local target exists; otherwise document why visual runtime evidence is unavailable and retain test/smoke evidence. Run `git diff --check` and a changed-scope secret scan.

## 4. Explicit Non-goals

- S03-005 Submission Detail Drawer, edit, notes, documents, Application creation, or child-click detail behavior.
- Any submission/candidate/application mutation, bulk status implementation, emails, deletion, inactive/reactivation, or dialog/menu flow.
- SQL schema/RLS/grant changes except a narrowly necessary existing read surface verified against canonical authority; no service-role workaround.
- Production deploy, main integration, unrelated shell redesign, dependencies, or speculative abstraction.

## 5. Delivery

Use exactly one implementation commit on the isolated task branch. Leave the task worktree clean. Persist `APPLICATION-INBOX-001` evidence and truthful post-execution receipts. Do not commit/push/merge/deploy outside that task branch.
