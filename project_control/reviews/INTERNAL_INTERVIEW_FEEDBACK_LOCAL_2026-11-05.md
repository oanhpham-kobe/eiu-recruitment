# Internal interview feedback — local implementation evidence

Date: 2026-11-05. Branch: `codex/interview-feedback-consolidation-20261105`.
Base: `c5a0a4243186d92287493f68973d88939e314476`.
State: local verification PASS; exact-candidate independent review/publication pending.
This is not OMP acceptance, recovery acceptance, production readiness or GitHub CI evidence.

## Implementation

Owner authorized local implementation/preview under CR-INTERVIEW-FEEDBACK-20261105,
selected the existing five optional qualitative questions and deferred real providers.
Normative module101 and command/permission/acceptance indexes are synchronized.

- Five private RLS-protected feature tables; immutable versions/terminal records and no raw authenticated access.
- Exact current-round/current-participant ownership, active bound identity, post-lock authorization, optimistic drafts and audited atomic submission.
- Unique collections/invitations/provider-paused notification intents; no outbound delivery.
- Own-only pages; HR inspection, original-denominator blockers, pinned attributed snapshots, versioned summary/title and immutable approval.
- Isolated synthetic preview shares production components; no auth bypass or privileged browser credentials.
- Browser printing retains every question/evaluator/answer. Official exports and candidate dossiers remain deferred.

## Fresh verification

| Surface | Result |
|---|---|
| Full web/browser suite | 400 PASS; zero failed/cancelled/skipped |
| Lint/typecheck/build/design contract | PASS; six existing unrelated lint warnings |
| Full isolated database sequence | 47/47 PASS: prior45 steps plus new SQL/concurrency suites |
| Clean replay | 51 migration history rows, including20261104221450; PASS |
| New actual-role SQL | 71 assertions PASS |
| New synchronized races | 7 PASS: create retry, draft collision, revoke/submit, removal/approval, permission revocation after wait, next-round/submit, email composition |
| Governance regressions | 10 PASS |
| Canonical source/design | 515/515 and73/73 PASS |
| Manifest integrity | 565 checks PASS; prototype baseline app.js stale receipt repaired without changing its source |
| Production entry smoke | Both feature paths preserve internal login return paths; zero browser errors |
| Synthetic preview | HTTP200; desktop/mobile/full workflow exercised |

SQL tests cover non-root dual-permission HR success and single-permission denial,
cross-user/private denial, exact rounds, immutable templates, stale versions,
required answers/deadlines, lifecycle rejection, pinned attribution and unchanged
legacy report/outcome data. All20 new function bodies matched migration source
before the parent independently replayed the full schema and workflow.

Browser tests prove draft reload, separate evaluator submissions, HR inspection,
approval/full print, explicit fresh reload after stale conflict, required-field
keyboard feedback, long submitted-answer keyboard scrolling and unequal paging
(51 interviews/one template), including publishing on a later page.

## Reproduced defects repaired

- Proposed parent UPDATE lock order conflicted with email; compatible SHARE fences passed forced composition races.
- Paging hid the selected template, then a reset stranded later interviews. A visible authorized template cache preserves selection; current-page counts still govern paging.
- Disabled submitted textareas hid long content from keyboard access; fields are now focusable/read-only, with mutation buttons disabled.
- Login server/client persona mismatch produced React418; server-resolved initial props now hydrate consistently, including server-only markup.
- OTP return paths allowed external URLs and callback prefix checks admitted control-character origin normalization. Shared validation now rejects protocols, double-slash paths, backslashes and raw controls while preserving legitimate invitation paths.
- A legacy CSS token failed the design check; current declared tokens now pass.
- The untouched baseline prototype app.js did not match its old manifest row. Working bytes equalled the base Git blob; only the stale size/hash receipt was corrected.

## Limits

Real Google/provider configuration was not performed; browser provider calls are
intercepted. Persistence/authorization proof uses actual local PostgreSQL roles.
Notification intents still require provider/worker integration. Initial contract
allows one collection per exact Interview; revocation never silently waives a
reviewer. No reopen/partial approval or official server PDF/Word export is claimed.
No main integration, production deployment, hosted mutation, Package009 acceptance
or accepted checkpoint occurred. The dedicated verification stack was stopped
with backup; existing user stacks were not reset/migrated. Restart the separate
preview using `npm run preview:feedback` from `web`.
