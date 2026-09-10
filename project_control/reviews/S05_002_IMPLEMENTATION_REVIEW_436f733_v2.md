# S05-002 Independent Targeted Implementation Re-review

WORK_ID: S05-002-IMPLEMENTATION-REVIEW-001-R2

REVIEWED_SHA: 436f733224cf9cb3776b5783afd86f577572d542

PRIOR_REVIEWED_SHA: b711bebcb9da15ea4ea8a22f7f8594f49cc6c971

BASELINE: fdf5fd27d27f6e6d587aab034cce0f54df425cfc

VERDICT: BLOCKING_REPAIR

SOURCE_REOPEN_REQUIRED: false

## Exact scope and evidence availability

- The exact repaired candidate exists locally and remotely. Its direct parent is prior reviewed SHA `b711bebcb9da15ea4ea8a22f7f8594f49cc6c971`.
- Targeted diff reviewed: `b711bebcb9da15ea4ea8a22f7f8594f49cc6c971...436f733224cf9cb3776b5783afd86f577572d542`.
- The stated handoff path `project_control/reviews/S05_002_IMPLEMENTATION_REREVIEW_GATE_436f733_v1.md` is absent from the exact candidate tree and locally fetched refs. This did not block an exact-source review; it is a non-product evidence-coordinate discrepancy.
- An independent `eiu-reviewer` performed a separate read-only static review of this exact diff. Its material findings were independently checked against direct source and fresh command output below.

## BLOCKING_FINDINGS

### S05-002-IR2-001 — HIGH — filtered refresh still silently drops dirty Drawer state and silently weakens field-level conflict detection

`HrReportView.refresh()` preserves the Drawer only by finding its Interview inside the refreshed, currently filtered page (`web/src/components/reports/HrReportView.tsx:278-305`). A visibility change from a `VISIBLE` filter to hidden, or a status change that excludes the row from the active status filter, makes `fresh` absent. Line 304 then calls `closeDrawerNow()`, clearing both a dirty HR Note and dirty participant-report draft without a warning or discard confirmation.

The same refresh path sets `reportBase` to newly fetched fields and reapplies local patches at lines `292-297`. If another actor changed a field after the user began editing, this silently adopts the remote value as the user's base. The next save presents that remote value as `p_base_values`, allowing the user's old draft to overwrite the same-field remote update instead of producing the accepted `STALE_VERSION` conflict.

This violates the accepted unsaved-edit protection and field-aware concurrency contract.

**Required repair:** Preserve or separately refetch the Drawer row when a filter removes it; do not call `closeDrawerNow()` while drafts are dirty without an explicit discard decision. Retain the original field bases for dirty participant fields, or surface a conflict, while merging only untouched remote fields. Add browser/regression coverage using VISIBLE/HIDDEN and status-filter row exclusion plus a same-field concurrent-edit case.

### S05-002-IR2-002 — HIGH — HR participant report save names the accepted RPC version parameter incorrectly

`web/src/lib/reports/hr-server.ts:267-272` calls `save_interviewer_report` with `p_expected_version`. The accepted public function signature uses `p_expected_version_no` in both `supabase/migrations/20260906070000_interview_lifecycle_commands.sql:725` and `supabase/migrations/20260909012000_interviewer_report_owner_only_command.sql:289-304`.

PostgREST resolves RPCs by argument name. This adapter cannot resolve the accepted four-argument command and blocks HR participant-report saving at runtime.

**Required repair:** Change the adapter key to `p_expected_version_no`; add a server/RPC boundary regression that asserts the emitted parameter names for `save_interviewer_report`.

### S05-002-IR2-003 — HIGH — required narrow-width Status interaction still fails in the repaired candidate

Fresh `npm run test` exits 1. The candidate's own HR browser test fails at `web/src/__tests__/hr-report-browser.test.ts:154`: at the 390px viewport, Playwright cannot click `Đổi trạng thái của Nguyễn Minh Anh`. The trigger is repeatedly outside the viewport or its containing `<td>` intercepts pointer events. The repaired CSS does not make the required row StatusMenu interaction usable under the actual harness.

Because the first click fails, the same end-to-end run cannot prove the requested trigger anchoring, Escape focus restoration, or downstream draft-preservation flows.

**Required repair:** Make the row Status trigger physically reachable in the horizontally scrollable 390px table without breaking the fixed geometry or menu anchoring; rerun the full browser suite, including Escape focus restoration.

### S05-002-IR2-004 — HIGH — candidate lint gate remains red

Fresh `npm run lint` exits 1 with 10 diagnostics. Candidate-owned diagnostics include:

- `web/src/components/reports/HrReportView.tsx:3,34` import organization and unused `ReportFieldKey`;
- `HrReportView.tsx:615,896` unsupported `aria-*` usage on elements without compatible roles;
- `web/src/__tests__/fixtures/hr-report-browser-harness.tsx:4` import organization;
- `web/src/__tests__/hr-report-model.test.ts:4` import organization.

Four existing diagnostics in unchanged `src/styles/interview.css` are not attributed to this candidate. The candidate-owned diagnostics independently keep the required lint verification red.

**Required repair:** Remove/organize the candidate imports and correct the unsupported ARIA usage using the existing semantic pattern; rerun lint with no candidate diagnostics.

## REPAIRED R1 FINDINGS CONFIRMED STATICALLY

- **Meeting-link privacy:** `20260910024500_hr_report_review_repairs.sql:5-49` routes the public RPC through the existing private helper and strips `meeting_link` from every returned row before return. Lines `55-57` revoke authenticated execution and schema usage for the private helper. `hr-model.ts:89-108,285-362` no longer declares or allowlists a meeting-link field; its exact-key parser rejects it. The HR UI contains no meeting-link path. `supabase/tests/hr_report_dto_privacy_test.sql` asserts a reports.view-only actor receives neither the key nor seeded URL. Local SQL execution remains unavailable.
- **Frozen table text rules:** `HrReportView.module.css:102-184` retains 1610px fixed geometry, normal wrapping, sticky Select and Name offsets, 144px status badge styling, and removes both generic `overflow-wrap:anywhere` and the Note line clamp. `npm run design:check` passes.
- **`!important` removal:** The candidate HR styles have no `!important`; however lint and the actual narrow browser interaction remain failing as described above.

## NON_BLOCKING_OBSERVATIONS

- The claimed R2 handoff artifact is absent at the exact candidate SHA and locally available refs. Direct target and canonical source evidence was used instead.
- The public RPC removes the raw link in a second JSON-processing pass after the private projection. It is privacy-correct statically, but selecting an already minimum-safe row shape in the trusted helper would avoid allocation and JSON re-aggregation. This is not an acceptance blocker.
- Local Docker Desktop Linux engine is unavailable. No local Supabase start, migration replay, or SQL regression was attempted against a connected project.

## VERIFICATION_EXECUTED

- `git diff --check b711beb...436f733` — PASS.
- `npm ci` — PASS; installed 45 packages. npm reported its local allowScripts policy blocked the `esbuild` postinstall script.
- `npm audit --audit-level=high` — PASS; 0 vulnerabilities.
- `npm run design:check` — PASS; 146 production CSS/TS/TSX files and 83 runtime tokens scanned.
- `npm run lint` — FAIL; 10 diagnostics, including six candidate-owned diagnostics listed in S05-002-IR2-004.
- `npm run typecheck` — PASS.
- `npm run build` — PASS; production build includes `/reports`. Existing Next middleware deprecation and missing build-cache notices were emitted.
- `npx playwright install chromium` — PASS.
- `npm run test` — FAIL; candidate HR browser test `HR Report narrow status and drawer mutations preserve unrelated unsaved drafts` times out on its initial 390px row Status trigger click.
- `npx supabase@2.116.0 --version` — PASS (2.116.0).
- `docker version` and `npx supabase@2.116.0 status` — FAIL because `dockerDesktopLinuxEngine` is unavailable. Therefore `supabase start`, `supabase db reset`, and the named SQL regression files were not run.

## SECURITY_ASSESSMENT

- The R1 raw meeting-link disclosure repair is statically sound: authenticated callers no longer have schema usage or execute access to the private helper, and the authenticated public wrapper removes the raw field.
- Browser HR mutations continue through server RPC adapters; no direct HR business-table browser DML was found.
- Overall assessment is **BLOCKING_REPAIR** because the repaired rebase path can turn a same-field concurrent participant-report change into a silent overwrite, violating the accepted optimistic-concurrency boundary. The invalid RPC parameter name separately prevents authorized HR report editing from reaching its command.
- Database behavior cannot be accepted as runtime-proven until Docker/Supabase verification is available and the blockers are repaired.

## DESIGN_SYSTEM_ASSESSMENT

- The exact 1610px table structure remains `48 | 240 | 300 | 240 | 200 | 190 | 300 | 92`; Select and identity cells remain sticky; normal wrapping and unclamped Notes are restored; the declared 144px badge benchmark remains.
- The responsive user-facing Status control remains unclickable in the required 390px browser acceptance path. Candidate ARIA lint errors also prevent design/accessibility acceptance.
- Overall assessment: **BLOCKING_REPAIR**.

## ACCEPTED_CONTRACT_REUSE_ASSESSMENT

- S05-001 Interviewer private surfaces remain unchanged versus baseline: `20260908124200_interviewer_report_contextual_read.sql`, `web/src/lib/reports/server.ts`, and `InterviewerReportPage.tsx` have no delta.
- No new Current Round or Final Decision source implementation was added; the HR query continues to use the accepted helpers.
- The qualitative eight-field Report schema remains intact.
- The candidate invokes the accepted `save_interviewer_report` command but currently uses the wrong RPC argument name and its refresh rebase defeats its field-aware same-field conflict protection. This must be repaired before accepted-contract reuse can be approved.
- No Product/Business/Design source reopen is indicated.

## ACCEPTANCE_STATEMENT

Do not accept, merge, or integrate `436f733224cf9cb3776b5783afd86f577572d542`. The raw meeting-link and table-wrap repairs are substantively present, but the candidate retains/introduces blocking unsaved-edit and concurrency failures, a broken participant-report RPC adapter, a failing narrow-width StatusMenu browser path, and candidate-owned lint failures. Repair those bounded defects, then provide a new exact SHA for re-review. No source reopen is required.
