# Full-project interactive HTML — local verification

Date: 2026-11-05. Branch: `codex/full-project-interactive-preview-20261105`.
Base: `dc10e3d9e3fb27121dbafc82620677582ab774d2`.
Candidate: `0d6e60a0e6c8a0dd694133efea2afe7960e53474`.
Status: locally verified and independently reviewed PASS on the exact candidate;
development-branch publication is Owner-authorized and checked directly from Git.

Read-only Codex collaboration review found no blocking findings. It confirmed
read guards, inactive-format historical handling, fixture-only aliases, offline
packaging and deterministic 299/300 ms debounce assertions. Reviewer independently
ran the seven model regressions. This is not formal OMP acceptance.

## Delivered scope

Owner requested an interactive HTML to test the complete current project and
explicitly requested GitHub updates for fixes found during the work.

- Standalone UTF-8 HTML embeds JavaScript, CSS and fonts; hash navigation works with file:// and offline mode.
- Six sample roles share browser-local state; guide actions select the appropriate role/screen, observations reflect saved actions, reset affects only this preview, and readable notes export as TXT.
- Actual current components cover Candidate form, Inbox/details/assignment, interviews/schedule/participants/rounds, original HR/interviewer reports, new questionnaires/consolidation, users/permissions and eleven master catalogs.
- Simulated service page shows local email intents and document metadata. OAuth/OTP, external delivery, scanning, real private files and official document export remain disconnected.
- Aliases are limited to this test fixture tree. No production route, authentication bypass, privileged credential, database migration or production application implementation was added/changed.

## Verification

| Check | Observed result |
|---|---|
| Full web suite | 409 PASS; zero failed/cancelled/skipped |
| Lint/typecheck/build/design | PASS; six existing warnings |
| Shared-model regressions | Seven PASS |
| Offline browser lifecycle | Candidate submit/upload-metadata → HR explicit READ → exact assignment → schedule/two participants → own original report → both feedback drafts/reload/submissions → HR consolidation/approval/print → reset; PASS |
| Guide/admin browser case | Automatic role shortcuts, all eleven catalog create forms, TXT notes/download/reload and language switch; PASS |
| Standalone boundary | file:// works with browser offline; zero HTTP(S) requests and browser errors; embedded assets |
| Responsive | 360/1440 browser checks PASS; separate390px offline smoke PASS |

HTML SHA-256: `daed5fc10649de9f5d87e405e8160bb49efb3e73e94049dbeaa2255d7ed54d9e`.
Generate with `npm run preview:project:build`; serve with `npm run preview:project`
at localhost3427. Optional `-- --output ABSOLUTE_PATH` selects the standalone file.
The generated `.preview/` output is ignored; source/adapters/tests remain versioned.

## Repairs discovered during construction

- Matched real component action payloads and returned DTOs so mutations persist across views and role changes.
- Preserved education when editing Candidate snapshots, enforced current-round feedback writes, and allowed authorized HR corrections after final status.
- Added granular write/read capability effects, inactive/unbound account guards and own-only context. These correct the preview model, not a newly discovered production authorization failure.
- Kept inactive exact assignments on explicit Reactivate, protected referenced catalogs, retained historical inactive interview-format metadata while rejecting new inactive selections, and checked candidate/room/participant overlap.
- Made bulk report-status changes atomic on validation failure and preserved decision-source timestamps on qualitative edits.
- Preserved draft/reset isolation, storage-unavailable fallback, frozen question/answer/report snapshots and the original evaluator denominator.
- Existing search debounce test failed under parallel browser load because a270ms host sleep could observe more than300ms browser time. Replaced it with the installed Playwright clock: zero calls at299ms, dispatch at300ms; search/privacy/URL assertions remain intact. Production debounce behavior is unchanged.

## Bounds

This artifact exercises UI interactions and representative in-memory domain rules.
It does not replace real Auth/RLS/database/concurrency/provider acceptance. No
database replay was required because database implementation is unchanged.
Previous questionnaire product/recovery evidence remains independently recorded.
No main merge, hosted operation, production deployment or accepted checkpoint.
