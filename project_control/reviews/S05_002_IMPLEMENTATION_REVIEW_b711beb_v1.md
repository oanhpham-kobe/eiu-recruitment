# S05-002 Independent Implementation Review

WORK_ID: S05-002-IMPLEMENTATION-REVIEW-001

REVIEWED_SHA: b711bebcb9da15ea4ea8a22f7f8594f49cc6c971

BASELINE: fdf5fd27d27f6e6d587aab034cce0f54df425cfc

VERDICT: BLOCKING_REPAIR

SOURCE_REOPEN_REQUIRED: false

## Exact scope

- Candidate SHA `b711bebcb9da15ea4ea8a22f7f8594f49cc6c971`, tree `df871c68f28b842ebbc12d243e62b302ae55f141`.
- Baseline is an ancestor of the candidate. The accepted S05-002 prompt is unchanged from reviewed prompt SHA `1f831a767906e4322e0fc2370d593b5c51e323d5`.
- Accepted S05-001 private surfaces are unchanged: `20260908124200_interviewer_report_contextual_read.sql`, `web/src/lib/reports/server.ts`, and `InterviewerReportPage.tsx` have no candidate delta.

## BLOCKING_FINDINGS

### S05-002-IR-001 — HIGH — HR RPC leaks a raw meeting link to reports.view-only users

**Accepted/source evidence:** The accepted prompt requires a minimum-safe HR DTO for a caller authorized by Root or `reports.view`, and says not to expose unrelated data merely because HR might hold other permissions. Canonical security authority separately grants Interview Session reads only to Root or `interviews.view`/`interviews.manage`.

**Implementation evidence:** `hr_report_private.get_hr_report_page_impl` authorizes with Root or `reports.view` at `supabase/migrations/20260910023000_hr_report_management.sql:73-80`, selects `i.meeting_link` at line 127, and serializes it into every row at line 219. `web/src/lib/reports/hr-model.ts:102,304,348` deliberately allowlists that raw value. The component uses it only as a boolean fallback to render an online-location label (`HrReportView.tsx:116-125`); it never needs to reveal the link itself.

**Why it matters:** A limited user with `reports.view` but without the separate Interview read permission receives a potentially sensitive meeting URL through the browser RPC. This violates the minimum-safe DTO and crosses the accepted Report-versus-Interview authorization boundary.

**Smallest required repair:** Remove `meeting_link` from the HR DTO and browser model. Compute a minimum-safe location display/online indicator in the trusted projection, or otherwise require the established Interview read authorization before returning a link. Add a DTO regression proving a reports.view-only response contains no raw meeting link.

### S05-002-IR-002 — HIGH — successful drawer mutations silently discard unrelated dirty drafts

**Accepted/source evidence:** The accepted prompt requires warning/protection when closing or navigating would discard unsaved long-form edits, and locale/state changes must preserve unsaved edits where safe.

**Implementation evidence:** `HrReportView.tsx:238-245` protects only explicit Drawer close. `refresh()` at lines `247-270` unconditionally replaces the note base/draft and calls `resetEditing()`. Successful `runVisibility`, `saveNote`, `saveParticipantReport`, and `confirmDeleteParticipant` call that refresh at lines `377`, `402`, `461`, and `496`. Therefore, for example, a dirty participant-report draft is erased after saving an HR Note, and a dirty HR Note is erased after saving a participant report, changing visibility, or confirming report deletion; no discard confirmation is shown. Starting Edit on another participant also replaces the existing dirty report draft at lines `414-419`.

**Why it matters:** A valid mutation on one Report field silently loses a different unsaved HR Note or Interviewer-report edit. This is actual user-data loss, not a speculative interaction concern.

**Smallest required repair:** Centralize a draft-transition guard. Before a mutation/refresh or participant switch that would replace a dirty unrelated draft, preserve that draft or require an explicit discard decision. Only reset the draft successfully saved by that operation. Add browser regression coverage for dirty Note + participant save/visibility/delete and dirty participant report + HR Note save/visibility.

### S05-002-IR-003 — MEDIUM — HR table violates frozen text-wrapping rules

**Accepted/source evidence:** `TABLE_LAYOUT.md` prohibits generic `overflow-wrap:anywhere` for normal table cells and requires normal business content to wrap; the accepted prompt repeats both requirements.

**Implementation evidence:** `web/src/components/reports/HrReportView.module.css:109-118` applies `overflow-wrap: anywhere` to every HR table header and data cell. Lines `179-184` additionally line-clamp the HR Note to three lines, hiding the rest rather than wrapping it in the declared Note column.

**Why it matters:** This contradicts the normative 1610px table content contract and can conceal/fragment operational HR Note content in the main table.

**Smallest required repair:** Restore normal word breaking for ordinary cells, reserve `.wrap-anywhere`-style handling for genuinely unbreakable identifiers only, and remove the default HR Note line clamp or replace it with a source-approved explicit disclosure behavior.

### S05-002-IR-004 — HIGH — required web quality and HR browser acceptance are red

**Evidence:** Fresh `npm run lint` exits 1. Candidate-owned diagnostics include three `noImportantStyles` violations in `HrReportView.module.css:166-168`, import-order violations in `src/__tests__/fixtures/hr-report-browser-harness.tsx:4` and `src/__tests__/hr-report-model.test.ts:4`, and formatter violations in the new HR browser fixture/test files.

Fresh `npm run test` exits 1: 302 passed, 1 failed. `src/__tests__/hr-report-browser.test.ts:148` cannot click the 390px row Status trigger because its containing `<td>` intercepts pointer events; the test times out after 30 seconds. This is the required HR Report responsive/status browser acceptance path.

**Why it matters:** Candidate CI cannot pass, and the required narrow-width authorized StatusBadge interaction is not verified or usable under the project’s browser acceptance harness.

**Smallest required repair:** Make the status trigger reachable/clickable through the contained horizontal-table interaction at the tested narrow viewport, preserve trigger-anchored menu behavior, format/organize the new files, remove candidate-introduced `!important` cascade overrides, then rerun lint and the full web suite.

## NON_BLOCKING_OBSERVATIONS

- Local Supabase integration verification could not run because Docker Desktop's Linux engine is unavailable on this reviewer runtime. `npx supabase@2.116.0 status` reports failure to connect to `npipe:////./pipe/dockerDesktopLinuxEngine`; no connected Supabase environment was used.
- Six lint warnings in unchanged Interview files also exist, but they are not candidate-owned findings. Candidate-owned lint errors above independently make the candidate red.

## VERIFICATION_EXECUTED

- `npm ci && npm audit --audit-level=high` — PASS; 0 vulnerabilities. npm warned that the `esbuild` install script is not approved by the local allowScripts policy.
- `npm run design:check` — PASS; 146 production CSS/TS/TSX files and 83 runtime tokens scanned.
- `npm run typecheck` — PASS.
- `npm run build` — PASS; production build includes `/reports`.
- `npx playwright install chromium` — PASS.
- `npm run lint` — FAIL; candidate-owned diagnostics documented in S05-002-IR-004.
- `npm run test` — FAIL; 302 pass / 1 fail. The failing test is `HR Report status, drawer, unsaved-change and report-specific destructive UX share production primitives` at `hr-report-browser.test.ts:148`.
- `supabase --version` system binary — unavailable. `npx supabase@2.116.0 --version` — available. Local database start/replay and SQL regressions — unavailable because Docker Desktop Linux engine is not running.
- `git diff --check baseline candidate` — PASS.

## SECURITY_ASSESSMENT

- Trusted mutation architecture is otherwise preserved: server actions call RPC wrappers; no direct Report business-table write was found in the changed Reports UI/server surface.
- New SQL commands use active actor resolution, permission-plus-view enforcement, optimistic versions, `SECURITY DEFINER`, `search_path = ''`, qualified references, and explicit function ACLs.
- `set_report_visibility` is Current-Round-gated and mutates only the intended visibility field.
- `bulk_change_report_status` validates 1–100 unique IDs and aligned versions, locks Applications/Interviews/Submissions in deterministic order, performs full-set preflight before updates, and recalculates affected Submissions in the transaction.
- `delete_or_inactivate_report` now starts from `reports.delete` and retains the accepted report lifecycle body.
- S05-002-IR-001 blocks acceptance because the HR read projection violates the minimum-safe DTO and permission boundary by returning raw `meeting_link`.

## DESIGN_SYSTEM_ASSESSMENT

- Table structure, colgroup values, fixed 1610px geometry, sticky Select + identity columns, 144px status badge target, single toolbar StatusMenu, participant-specific destructive action, disabled PDF affordance, VI/EN labels, and overlay primitives are implemented.
- S05-002-IR-003 blocks design conformance: generic `overflow-wrap:anywhere` and default three-line HR Note truncation conflict with the frozen table contract.
- S05-002-IR-004 blocks responsive/browser acceptance: the narrow-width StatusMenu interaction test fails.

## ACCEPTED_CONTRACT_REUSE_ASSESSMENT

- Current Round: reused through `private.application_current_interview`; static implementation joins only active Application/Interview and emits one Application group.
- Final Decision Source: reused through `private.interview_final_decision_source`; no alternate source algorithm was added.
- Report schema: qualitative eight-field schema remains unchanged; no scoring mechanism added.
- Field-aware concurrency: HR edit calls accepted `save_interviewer_report` with patches/base values; no whole-row overwrite path was added.
- S05-001 Interviewer privacy/read projection: accepted private helper and interviewer server surface are unchanged; HR uses a distinct projection.
- Existing trusted commands: visibility/bulk/delete reconciliation is correctly shaped statically, subject to unavailable local database execution.

## ACCEPTANCE_STATEMENT

Do not accept or serialize candidate `b711bebcb9da15ea4ea8a22f7f8594f49cc6c971`. Repair the four bounded findings, especially raw meeting-link disclosure and silent unsaved-draft loss, then provide a new exact SHA for targeted re-review. No Product or canonical source reopen is required.
