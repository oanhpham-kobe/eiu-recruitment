# Workflow UI refinement — local verification

Date: 2026-11-05. Branch: `codex/workflow-ui-refinement-20261105`.
Base: `356648930ec22be692867235dfcff56c2de534d1`.
Candidate: `5e346d61cef8e725b3ce25e99ad1d38eab99480b`.
State: locally verified; independent exact-candidate review PASS.

Read-only Codex collaboration review found no blocking presentation regressions.
It checked overlay scrolling/focus, constrained-height actions, table columns,
feedback print rules and skill registration, and independently passed the focused
browser test. This review is not formal OMP acceptance or a production release.

## Owner scope and source

Owner supplied `workflow-app-ui-2026-11-04.zip` and requested installation in
the project plus application to the current interface. Earlier explicit GitHub
synchronization authorization remains applicable to this development work.

Archive SHA-256: `7e65491d2e18b54f13e7d85729063d10a036df60f2cc1c1af123265a10de5116`.
All eight installed files match the archive byte-for-byte. `SKILLS.md` documents
the skill; `SKILLS_LOCK.yaml` records provenance only. Native discovery recognizes
25 skills. Archive examples are presentation guidance, not EIU Recruitment domain
authority; UniCouncil roles, statuses, page sizes and scheduling rules were not
imported. Canonical EIU design contracts and 16px primary typography remain intact.

The eight committed skill blobs were also compared against the original archive:
8/8 byte-identical PASS. The refreshed HTTP response was compared byte-for-byte
with the exported HTML; parity, all eight guide steps, locale switching and zero
browser errors PASS.

## Actual application changes

- Shared Dialog/Drawer now constrain long content within a scrollable body, retain
  accessible header/actions and close control, and provide a very-short-height
  fallback. Desktop drawers preserve sidebar space.
- Candidate, Inbox, Interview, reports, Users, Catalogs and questionnaires share
  existing EIU control borders, typography and semantic styling more consistently.
- Admin pages remove nested padding, preserve explicit semantic table columns,
  improve mobile control sizing and keep horizontal overflow within the table.
- Grouped filters and bounded table scrolling preserve business data and pagination
  semantics. No mobile-specific mutation path or new dependency was added.
- Standalone preview has a compact localized role banner and numbered guide. Its
  `app-root` wrapper now enables the real overlay background inertness mechanism.

## Fresh verification

| Check | Result |
|---|---|
| Full web suite | 409 PASS; zero failed/cancelled/skipped |
| Lint/typecheck/design/build | PASS; six pre-existing lint warnings |
| Focused browser cases | Four PASS; included in full suite |
| Responsive | Existing design matrix plus actual preview screens at 360,390,430,768,1024,1440px; no page-wide overflow |
| Long overlays | 1440x900,768x600,390x360,360x360; body scroll, final-field focus, fixed actions, Tab/Escape and stacked locks PASS |
| Admin dialogs | 1440x600,768x360,390x360,360x360; final field/actions reachable and trigger focus restored |
| Workflow | Offline Candidate submit through scheduling, original report, both feedback submissions, consolidation approval/print/reset PASS |
| Preview background | Actual Interview drawer sets/removes `app-root` inert state on open/Escape |
| Visual inspection | Rendered desktop/mobile guide, Users, Catalogs, questionnaire and short admin dialog inspected; before/after screenshots retained in local artifacts |

The long shared Dialog regression was reproduced failing before the CSS repair.
Its body was not scrollable; the regression now verifies the observable repair.
The existing status-menu keyboard assertion also waits for its intentional
animation-frame focus transfer before reading focus.

Refreshed standalone HTML SHA-256:
`fd43afe8a1329ec0d6a6283d1bb9d8411ec7aac769d48f4c7b4d86d6f7d59db3`.
Generate using `npm run preview:project:build`; serve at localhost3427 with
`npm run preview:project`. Generated HTML remains outside version control.

## Bounds

Actual application presentation and isolated preview presentation changed.
Authentication/authorization, database schema, transactional commands, provider
configuration and domain state transitions did not change. No database replay was
required. This is local development verification, not comprehensive accessibility
certification, formal OMP acceptance, production deployment or Package009 acceptance.
