# Workflow UI visual polish — local verification

Date: 2026-11-05. Branch: `codex/workflow-ui-visual-polish-20261105`.
Base: `2c0b3decc426582763cdf33a8245d1e9efb5a563`.
Product candidate: `b95a80e3ef5e04fc1f2f73962e91237dbc881c36`.
State: locally verified; exact-candidate independent re-review PASS.

The read-only Codex reviewer inspected the repaired360/390px footer images and
independently passed the complete offline workflow with text-bounds assertions.
No remaining blocking findings were identified in this scope. This review is
not final Owner aesthetic approval or formal OMP acceptance.

## Owner scope and design authority

Owner rejected the earlier result as uneven and poorly proportioned and asked
for closer use of the supplied `workflow-app-ui` skill, including typography.
The skill remains unchanged. Canonical responsive trial amendment
`CR-WORKFLOW-UI-UAT-20261105` records the authorized presentation changes; final
Owner visual acceptance is pending. Frozen desktop Interview/HR report columns,
16px primary text, authorization, data and command semantics are preserved.

## Repairs and presentation changes

- Fixed an actual missing-font implementation: the previous font family was only
  declared. Bundled four original Be Vietnam Pro weights, license and source/hash
  provenance; all application and offline-browser fixtures now load those assets.
- Kept admin action cells as table cells with inner action wrappers; rebalanced
  admin columns and removed technical version counters from primary content while
  retaining the optimistic-concurrency tokens used by commands.
- Compact localized headings/actions, disclosed secondary filters, one Inbox bulk
  Status menu, and keyboard-accessible row More popovers reduce control clutter.
  Popovers stay above table clipping and dismiss safely on Escape/anchor movement.
- Desktop list frames use the remaining app area. Phone summaries group identity,
  contact, schedule/status and actions; note excerpts open to complete detail.
  Removed the contradictory mobile overflow-visible/max-height combination that
  had allowed pagination to overlap long card lists.
- Questionnaire assignment fields use two desktop columns with a bounded deadline
  input; assignment/template setup is secondary to tracking existing collections.
- Corrected expanded-round headers that used grid directly on a table cell. A real
  browser regression failed before repair (header76px versus sibling136px) and now
  proves aligned cell heights at all tested desktop/tablet widths.

## Fresh evidence

Independent review of initial candidate `67b126c32f21ff5f700b77cc4d1be9c0c8744f0c`
returned BLOCKING_REPAIR for phone Candidate submit text overflowing its fixed
44px button. Primary buttons now use automatic height with a44px minimum, and
phone Candidate footer actions stack at full width. A real text Range/target
rectangle regression failed at360px before repair and passes at360/390px after
repair. The full suite/build and36-scene audit were rerun successfully after this
bounded repair; fresh footer screenshots were visually inspected. Font assets,
delivery and CSP are unchanged from the actual Next font integration smoke.

| Check | Result |
|---|---|
| Full web suite | 409 PASS; zero failed/cancelled/skipped |
| Lint/typecheck/design/build | PASS; zero lint warnings |
| Populated browser audit | 36 scenes: nine page/role contexts at1440,1280,390,360px; zero page-wide overflow or runtime errors |
| Font delivery | Four loaded faces at400/500/600/700; Chromium confirms actual custom-font glyphs in offline HTML |
| Actual Next app smoke | Login200; four local font asset requests200 under existing self-only font CSP; custom BeVietnamPro-Bold glyphs rendered; zero page errors |
| Workflow/permissions | Existing Candidate-to-consolidation, admin/reference/permission, email and own-report cases remain in the passing full suite |
| Interaction regressions | Mobile expanded-list/pager geometry, More keyboard/Escape/resize/focus and long overlays PASS |
| Source/design | Package515/515; design validator PASS;565 manifest checks PASS |
| Control plane | Control and OMP-native validators PASS;25 project skills |

The audit uses isolated synthetic state generated through current preview adapters:
four application assignments, six rounds, twelve original reports, two submitted
feedback responses and a draft consolidation. It does not touch the Owner's
browser storage. Before/after images and machine-readable metrics are retained
as local artifacts; they are observations, not Owner visual approval.

Updated static assertions retain the frozen desktop full-text/geometry guards
while allowing the explicitly documented phone note excerpts. The selection
refresh case now opens the More menu before exercising the same next-round
command; it still verifies selection pruning and restored lifecycle authority.

HTML SHA-256: `34aa3828234d97867c7133b57973d26fce1e5ca24b44ba6bac4590da3e121ffb`.
Served HTTP/exported HTML byte parity PASS. The previous feedback preview still
responds200. No new dependency, backend change, database replay, hosted operation,
main merge, production release, formal OMP acceptance or Package009 acceptance.
