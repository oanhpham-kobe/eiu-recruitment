# Workflow UI skill v2 — 2026-11-05

Owner scope: install the updated supplied skill and synchronize the current app
interface and its existing ChatGPT demo. Development-branch publication remains
authorized. Main/backend/recovery release and final visual acceptance remain held.

Product candidate: `5e53d4dfa9f6ec0ce355b6d2a53b00d438da19ab`.
Base: `686b1b19b7c5ce0e5745a0b08ba8cc2962b9c7a0`.
Controlled trial: `CR-WORKFLOW-UI-SKILL-V2-20261105` in
`recruitment_webapp/design_system/RESPONSIVE.md`.

## Changes and actual defects repaired

- Installed all nine original archive files, including the new layout/alignment
  reference. Archive/committed byte parity and provenance hash verified.
- One responsive gutter across workspaces; consistent heading, badge internals,
  header/data axes, edit semantic colors and form/control alignment.
- Fluid semantic tables with stable selection/status/action targets. Narrow
  workspaces use labelled cards with all existing detail actions available.
- Replaced unsupported percentage/pixel calc on table columns: Chromium had
  silently distributed content columns equally. Three real cell-rectangle
  regressions reproduced RED, then pass1393/1440/1920 with native percentages.
  Notes retain at least120px at the tested table transition; long excerpts open
  to full detail.
- Normal-height lists scroll independently with pagination outside; short screens
  and expanded filters use reachable document flow. Positioning the shared scroll
  boundary also repairs invisible extra page height caused by off-screen labels.
- Portalled schedule/participant forms, drawers and admin dialogs retain viewport
  media rules; workspace container queries apply to in-content lists. Candidate
  portal retains its own outer gutter outside the internal shell.
- No domain/authentication/authorization/backend changes or new dependencies.

## Fresh verification

| Check | Result |
|---|---|
| Full web suite |409 PASS;0 failed/cancelled/skipped |
| Lint/typecheck/design/build |PASS; zero lint warnings |
| Populated browser scenes |144 PASS:81 VI at nine widths320–1920;18 EN;9 laptop1366x768;36 long names/emails/notes |
| Browser bounds |No global or local-table horizontal overflow; no runtime errors; bundled font faces/glyphs loaded |
| Focus/overlays |Narrow/short schedule/participant field geometry, keyboard reachability, Escape/focus return PASS |
| Source/design/manifests |515/515 source;73/73 design;565 manifest checks PASS |
| Control/skills |Control plane and OMP-native validation PASS;25 skills |

The production-bundle auth smoke uses the same fake public build-time environment
as Integration CI; requests are intercepted and no real provider is contacted.
Tests formerly asserting fixed artboard widths were updated to prove the scoped
v2 workspace, alignment and target contract; permission/token/draft/focus cases
remain intact.

Independent read-only Codex review of the exact product SHA: PASS, no actionable
findings. Reviewer reran10 focused browser tests, ZIP parity, header/name axes,
badge/action boundary checks and short-screen keyboard/focus checks. This is not
formal OMP acceptance. Owner visual UAT remains pending.

## Published static demo

Existing Site updated successfully to version2, preserving the Owner's current
public access configuration (revision2 observed); this work did not change access.
URL: https://eiu-recruitment-trial-20261105.tidyburl1.chatgpt.site

HTML SHA-256:
`4ff36aea2208fdd964fd4d9dbfddd4ec6191292957ae8a3e3dbc0f69c2b3f06e`.
The packaged HTML is byte-identical to the verified export; bundled license
notices remain. Native helper synchronized source and matching archive; native
deployment returned succeeded. Exact version/deployment/source identifiers live
in `EVIDENCE_INDEX.yaml:implementation_evidence.WORKFLOW-UI-SKILL-V2-20261105`.

Six synthetic personas and browser-local storage remain. No real EIU auth, mail,
private upload processing or recruitment database is connected. No main merge,
accepted checkpoint, production application release or Package009 acceptance.
