# Astra Phase B — Current-State Audit

Date: 2026-09-27. Repository: `oanhpham-kobe/eiu-recruitment`.

- Immutable technical baseline: `8dcb0a5d7ce1be9d82e3448c01cdc1643e3ac8c4`.
- Inspection checkout: `f9457fe5490e54d4996f90955752da86616cf3e8`. Its complete delta from the technical baseline is eight research Markdown files, not product changes. Runtime, migrations, tests and governance findings below therefore refer to the technical baseline.
- Review-only branch: `review/astra-strategic-review-20260927`. This artifact does not change runtime, migrations, canonical requirements, task state or accepted checkpoints.
- Controlling handoff: `project_control/research/ASTRA_MEDIUM_MASTER_HANDOFF_2026-09-27.md`, Phase B, with the Owner's current filename and commit/push authorization taking precedence over its older output name/local-only default.
- Phase A remains accepted with its existing caveats, frozen and unmodified: `project_control/astra_review/ASTRA_GREENFIELD_PHASE1_ARCHITECTURE.md`; SHA-256 `646adc6ff4081c7f748b4191f740e0c3b1971857567788668ace41b2907dabe8`; marker `GREENFIELD_PHASE_A_FROZEN: YES`. Phase A was not reopened or retrospectively aligned to implementation.
- This is a descriptive audit, not Phase C, an implementation plan, a global KEEP/SIMPLIFY/REWRITE verdict, permission to materialize TASK-S08-002, or release authorization.

## 1. Executive assessment

**Phase-1 user-facing completeness and production readiness are not established. There are concrete blockers beyond the prior research's missing external runtimes and administrative UI.**

1. Actual local browser execution fails Candidate OTP initialization before Supabase contact: the public URL helper dynamically indexes `process.env[name]`, which Next does not inline into browser code. The Google entry path uses the same factory and also displayed its failure message. Correctly supplying the public URL/key to the dev process did not resolve this implementation defect.
2. Effective repository grants/RLS allow an assigned Interviewer to SELECT `interviews.hr_report_note` directly. The safe report DTO does not close this alternate base-table read. This is a source-proven confidentiality defect, not a claim that production data was accessed.
3. Source inspection found incompatible parent lock orders, nullable expected-version bypasses, missing Submission outcome recalculation on Interview reactivation, and a bulk delete function that can return failure after committing earlier items.
4. Master Data and Users & Permissions administration have substantive database implementations but no application management pages. Existing HR modules also omit explicit NEW-to-READ opening, whole permitted Submission editing, HR document editing and Interview document consumers. PDF generation is absent.
5. Email enqueue/history, scan request/lease/fencing and cleanup contracts are real implementations. They are not proof of email delivery, malware scanning or scheduled cleanup. Cleanup has a real provider-call runner; email/scanning have no located external execution engine.
6. Both control validators passed with 42 materialized tasks and an empty frontier. This demonstrates structural consistency, not source-backed feature coverage. Slice-06 is marked DONE despite its mandatory UI being absent; current policy says a slice denotes user/business completion.
7. Independent review and exact-SHA provenance have demonstrated value. Historical full-CI duplication is real, but the current impact resolver already skips product suites for eligible governance-only commits. Removing review or rewriting CI wholesale is not supported by those observations.

**Release distinction:** a synthetic-data, explicitly diagnostic Preview is different from a safe functional UAT Preview, and both differ from full Phase-1 production. The browser initialization defect blocks meaningful sign-in UAT. Confidential recruitment data must not be placed behind the identified Interviewer read exposure. A successful deployment or green component suite would not close either finding.

### Evidence method and limits

Four bounded, read-only reviewer slices covered product/UI, effective database invariants, external runtimes, and governance/history. The parent independently inspected decisive paths and ran the checks below. Worker success labels were not treated as acceptance evidence.

| Evidence | Result and limit |
|---|---|
| Actual Next dev process, installed Next 16.3.4 / React 19.2.8; loopback port 3417, synthetic loopback Supabase URL and synthetic publishable key, empty service-role key | Server started. `/auth/candidate` redirected to `/login?persona=candidate`; mobile-width login rendered. Candidate Send OTP caught `Error: NEXT_PUBLIC_SUPABASE_URL must be configured` at `requirePublicEnvironmentVariable -> getPublicSupabaseEnv -> createBrowserClient -> handleSendOtp`. CDP caught the exception; served bundle retained dynamic URL lookup while the synthetic key was inlined. No external credentials used. |
| Same live page, internal tab / Google button | Displayed `AUTH_EXCHANGE_FAILED`. Source confirms the shared failing browser factory. A separate extended CDP/locator attempt timed out; no independent Google provider exchange is claimed. |
| Local visual observation at initially configured 390x844 | Login had no observed horizontal overflow; screenshot inspected. Not an authenticated Candidate journey, desktop UAT, WCAG certification or full responsive acceptance. Later browser observation returned inconsistent viewport metadata, so it is not used as additional responsive proof. Browser tab and isolated server were closed. |
| `python project_control/validate_control_plane.py` | PASS: 10 slices, 42 tasks, 0 eligible frontier tasks, 0 active Executors. Existing durable AUTONOMOUS state was observed, not used to expand this Owner-bounded audit. |
| `python project_control/validate_omp_native.py` | PASS: 24 project skills, 5 project agents, native skill discovery. Does not prove product completeness or every process asset's value. |
| `node --conditions react-server --test --import tsx src/__tests__/storage-cleanup-runner.test.ts src/__tests__/upload-scanner.test.ts src/__tests__/auth-routes.test.ts src/__tests__/report-model.test.ts` from `web/` | 39 tests passed, 0 failed, exit 0. Auth/runner dependencies are controlled test ports; this proves the exercised boundaries, not real provider delivery, database RLS, session refresh or deployed E2E. |
| `docker ps --format "{{.Names}} {{.Status}}"` | Failed: Docker Desktop Linux engine pipe unavailable. No local database was started/reset, no SQL fixtures executed, no remote database substituted. SQL findings remain source-derived; concurrency scenarios were not replayed. |
| Read-only Git/GitHub inspection | Verified representative exact-SHA CI jobs, governance-only deltas and review/repair history; details in section 9. Historical CI is not a fresh run of this audit branch or current cloud proof. |
| Cloud inspection | No mounted Vercel/Supabase cloud inspection tools available. No current project status, deployments, applied schema, secrets, providers, redirects or runtime schedules independently observed. No cloud operation performed. |

Paths below are repository-relative. `M/` means `supabase/migrations/`; `T/` means `supabase/tests/`; `S/` means `recruitment_webapp/review_pack/`; `W/` means `web/src/`. Line ranges refer to the pinned technical tree. Absence claims are bounded to the inventoried repository/runtime, not a claim that an untracked external service cannot exist.

## 2. User-facing completeness matrix

These columns are deliberately separate: **CONTRACT_EXISTS**, **BACKEND_EXISTS**, **UI_EXISTS**, **RUNTIME_EXISTS**, **END_TO_END_CAPABILITY_EXISTS**. A database function, button, fixture or accepted task cannot substitute for the last column. No authenticated, connected full persona journey was demonstrated in this audit.

| Capability | CONTRACT_EXISTS | BACKEND_EXISTS | UI_EXISTS | RUNTIME_EXISTS | END_TO_END_CAPABILITY_EXISTS |
|---|---|---|---|---|---|
| Candidate email OTP / provisioning / portal access | Yes: S/02, S/03, S/13 | Auth verification/provisioning routes and trusted commands | `/login`, `/auth/candidate`, `/candidate` | Actual login renders; OTP initialization fails locally, F01 | No successful sign-in demonstrated; F01 blocks before provider |
| Internal Google / active directory / HR / Root / Interviewer identity | Yes: S/02, identity contracts | Callback exchange, active trusted session RPC and permissions | Internal login tab and internal shells | Google button fails locally; provider/allowlist deployment unverified | Not demonstrated; domain suffix alone is not authorization |
| Candidate form, privacy, education, own submissions, NEW-only edit | Yes: S/03, S/07 | Sessions, privacy notice, Candidate read/submit/update RPC adapters | CandidateForm, EducationSection, DocumentUploader, SubmissionsList | Source paths exist; no connected session exercised | Incomplete operational chain: login and required CV scanning block |
| Candidate document upload, staged ADD/REPLACE/DELETE | Yes: S/03, S/11 | Reservation, byte inspection, durable scan request, CLEAN continuation and atomic commit | Candidate upload/pending/error controls | Inspection unit checks pass; scanner execution absent in repo | Not proven; inspection is not antivirus and PENDING is not usable CV |
| HR Inbox grouped list/search/filter/pagination | Yes: S/04 | Accepted indexed page read, permissioned adapters | ApplicationInboxTable and filters | Source present; latest historical acceptance exists; no authenticated UAT | Representative source chain exists, not certified E2E |
| HR explicitly opens NEW Submission | Yes: S/04:63-67 | `open_submission` command exists | Drawer opening invokes only pure detail read | Actual consumer missing, F08 | No: authorized full HR opening does not wire NEW-to-READ |
| HR whole permitted Submission edit / documents | Yes: S/04:117-131 | Note update and broader correction/document contracts exist; full composition not certified | Edit is note-only; documents preview/download only | Missing controls/consumers, F09 | No full required edit journey |
| Application assignment, ownership, lifecycle | Yes: S/04, S/05, S/07 | Durable identity, create/update/delete/reactivate commands | Inbox assignment and Interview UI | Source paths exist | Not certified; cross-command locks/outcomes need repair |
| Interview scheduling / status / copy / next round / reactivation | Yes: S/05, S/37 | Real transactional functions, versions, resource locks and idempotency | InterviewPage, InterviewDrawer, InterviewDialogs | Source path exists; no connected scheduling smoke | Not certified; F04-F07 are counterexamples to blanket correctness |
| Participant add/remove/re-add/reorder | Yes: S/05, S/06 | Current/archive semantics, eligibility guards and report ownership | Current/removed participant controls | Source implementation, existing SQL/concurrency tests not rerun | Not certified across all races |
| Interview materials for HR and contextual Interviewer | Yes: S/05 section 14, S/02 | Reservation/finalization/storage contracts present | No document section/action in Interview or Interviewer report UI | No located web upload/finalize/list/download consumers | Missing user capability, F10; optional attachment presence does not make capability optional |
| Interviewer own report, history, shared current preview | Yes: S/06 | Contextual DTO, owner-only write, changed-field/base-value merge | InterviewerReportView/DrawerContent | Source path; report-model tests passed, not DB execution | Not certified; raw table privacy flaw F02 bypasses safe DTO |
| HR reports, final decision/status/note/visibility/participant report edit | Yes: S/06, S/07 | HR page RPC/capabilities, status/note/edit/delete commands | HrReportView, dirty-state handling, HTML preview | Source path only in connected terms | Not full capability: PDF absent; nullable version and outcome defects |
| Master Data management | Yes: S/02:117-126, S/09 | Lifecycle/history contracts implemented | No page/nav/action consumers | No management surface to run | Absent through application, F11 |
| Users & Permissions management | Yes: S/02, internal-user contracts | Directory/RBAC/binding/lifecycle safeguards implemented | No page/nav/action consumers, including Root | No management surface to run | Absent through application, F12 |
| Email preview / enqueue / history | Yes: S/05, S/11 | Outbox/history/retry/worker protocol | Row/bulk preview/send/history/delete UI | UI expressly reports queued, not delivered | Enqueue path exists; actual external delivery absent/unverified, F13 |
| Malware verdict processing | Yes: S/11, S/44:102-106 | Claim/lease/fencing/result authorization | Pending/result consumer | No engine/provider runner located | Required new-Candidate completion blocked, F03 |
| Expired session/temp-object cleanup | Yes: S/44:102-106 | Discovery, trusted claim/authorize/complete, provenance/tombstones | Operational rather than end-user UI | Real TS deletion runner/provider, no scheduled invocation | Not established, F14; historical/current business documents deliberately retained |
| Generated PDF download | Yes: S/06 sections 8/10/12, S/13 AC-28/51 | No generated-report renderer/export handler located | Disabled HR button; no Interviewer export | None located | Missing, F15; HTML preview/uploaded PDF preview are not export |
| VI/EN, keyboard/accessibility, desktop/mobile | Yes: S/10, responsive design contract | Not a standalone backend | Shared primitives/locale exist; several operational drawers hardcode VI | Limited login visual smoke only | Partial translation and unproven full responsive/accessibility acceptance, F16 |

## 3. Actual runtime map

### Browser to authoritative mutation

The dominant boundary is React UI -> Next Server Action -> server-only read/domain adapter -> user-context Supabase client -> RLS read or trusted PostgreSQL RPC -> constraints/locks/audit. That is a real implemented boundary, not proof every consumer or alternate SQL surface is correct.

| Journey | Concrete source chain | Important boundary |
|---|---|---|
| Candidate | `W/app/candidate/page.tsx` -> `candidate-actions.ts` -> `lib/commands/candidate-submission.ts`, `form-session.ts`, `storage-reservation.ts` | Server action coordinates; DB owns multi-row submit/update/version/privacy rules. Upload inspection uses narrow admin access only after user authorization. |
| HR Inbox | `W/components/inbox/ApplicationInboxTable.tsx:302-304` -> SubmissionDetailDrawer:179-234 -> `W/app/application-inbox-actions.ts:54-79` -> `lib/application-inbox/submission-detail-server.ts:84-129` -> `get_submission_detail` | Detail is deliberately pure read. Explicit opening's separate write is missing, not hidden in the query. |
| Interview | `W/components/interview/InterviewPage.tsx` -> `W/app/interviews/actions.ts:144-228` -> `lib/commands/interview-lifecycle.ts:150-466` -> named schedule/lifecycle RPCs | Server permissions/shape validation complement, not replace, direct-RPC checks. |
| Reports | `W/app/reports/page.tsx` / actions -> `lib/reports/server.ts:110-189` or `hr-server.ts:138-298` -> owner-only or HR/mixed-role RPC | Distinct privacy/capability projections and field-aware merge. Raw-table access must also be safe. |
| Uploaded document preview | `W/app/api/documents/preview/[id]/route.ts:27-61` -> authorized/audited private Storage stream | Bytes streamed with no-store/nosniff/sandbox CSP; not report generation. Unexpected 500 reflects raw message, F17. |
| External jobs | DB outbox/scan/cleanup state -> restricted worker protocol -> external provider | SQL protocol completion and hosting/provider completion are different facts. Only cleanup's TS provider-call loop is located. |

Complete route inventory: six pages (`/`, `/login`, `/auth/candidate`, `/candidate`, `/interviews`, `/reports`) and four handlers (auth callback, Candidate verify, signout, document preview). `W/components/shell/navigation.ts:7-29,36-57` defines only Applications, Interviews and Reports; Root receives that same three-item array. No administrative route is hidden behind a different Root menu.

Three command styles coexist: generic `createCommandRunner`/`TrustedCommandDefinition` in Application commands; local `actorContext`/`withPermission`/`executeRpc` in Interview commands; `authorizedClient`/validators/normalization in HR Report adapters. This is an evidenced consistency burden, not grounds to remove database checks or introduce a general application framework.

## 4. Database, concurrency and security

Ordered migrations are the effective repository execution authority. `S/database_schema.sql:1-4` explicitly identifies a reviewed starter, not the production migration bundle. Later replacements were considered; early function names alone were not treated as final definitions. No live catalog parity is claimed.

### Five source-backed defects

**F02 — P0: Interviewer base-row HR-note disclosure.** `M/20260905100000_application_schema_and_status_commands.sql:133-167` puts `hr_report_note` in `public.interviews` and grants authenticated table SELECT. The effective `interviews_select` policy and `private.can_view_visible_interview` in `M/20260906060000_interview_schema_and_conflict_locking.sql:645-705` allow a current active assigned Interviewer to read a visible active Interview under an active Application. No later SELECT revocation/policy replacement was found in the ordered migration inventory. RLS restricts rows, not the confidential column. A direct authenticated query such as `/rest/v1/interviews?select=interview_id,hr_report_note` bypasses the safe report DTO. `S/39_SECURITY_RLS_MATRIX.md:81` explicitly prohibits this broad shape; `T/interviewer_report_contextual_read_test.sql:377-388` checks the DTO, not direct table confidentiality. High source confidence; no live data accessed. Safe release requires direct-role confidentiality proof, not another frontend-hidden-field assertion.

**F04 — P1: composed parent lock cycles.** `create_next_interview_round`, effective in `M/20260906060000_interview_schema_and_conflict_locking.sql:772-806`, locks Application -> latest Interview -> Submission. `delete_or_inactivate_application`, effective in `M/20260906090000_application_reactivation_and_participant_contract_repair.sql:33-45`, locks Submission -> Application. Interleaving A owns Application; B owns Submission and waits Application; A requests Submission forms a cycle. `reactivate_interview` in `M/20260906070000_interview_lifecycle_commands.sql:664-676` locks Interview -> Application, another inversion against round creation. The later Copy repair `M/20260913004500_copy_interview_user_lock_composition_repair.sql:124-135,185-197` addresses user-lock composition but still takes target Application before Submission. This is a potential PostgreSQL deadlock/aborted valid operation, not a claim of silent corruption or an observed production incident. Deterministic two-session proof remains required; a retry-only workaround would not repair the composed order.

**F05 — P1: Interview reactivation omits persisted outcome recalculation.** The complete effective `reactivate_interview` body at the range above sets `is_active=true`, audits and returns. It does not recalculate Submission. Effective resolver/recalculator: `M/20260906005000_pre_s04_contract_repairs.sql:105-243`; no compensating Interview lifecycle recalculation trigger/later replacement was found. Scenario: latest HIRED round is inactivated, parent status recalculates from an earlier in-progress round; reactivate the HIRED round and effective outcome changes back without persisted Submission status following. Deletion/inactivation explicitly recalculates at `20260906070000:704-710`. Contract: `S/07_STATUS_AND_BUSINESS_RULES.md:36-50,125-128`. Existing lifecycle test :137-140 checks active flag rather than parent status. Source finding, not executed SQL result.

**F06 — P1: SQL NULL version tokens bypass expected-version checks.** Effective `save_interview_schedule` at `M/20260906070000_interview_lifecycle_commands.sql:600-622` uses `if v_i.version_no <> p_expected_version` at :609 without rejecting NULL. PL/pgSQL does not enter that IF for an unknown/null comparison. Related schedule-status, reschedule, reactivation and HR-note functions repeat the form at :632,651,670,793; functions are executable by authenticated callers at :968-969. Authorized direct-RPC callers can bypass stale-write rejection with JSON null regardless of TypeScript's number type. Other commands use `IS DISTINCT FROM` or explicit missing-version rejection, demonstrating drift. Do not replace the report field-aware merge with indiscriminate whole-row version equality; this finding concerns required token validation at the affected SQL boundaries.

**F07 — P1: bulk Interview deletion is not ALL_OR_NOTHING on a late JSON error.** `M/20260906070000_interview_lifecycle_commands.sql:885-898` locks selected Interviews, loops sorted IDs, invokes the mutating `private.delete_or_inactivate_interview_core`, and returns the first unsuccessful JSON without raising/rolling back. Core :678-712 performs writes/audit/recalculation before successful return and returns ordinary stale-version JSON at :683. Two independent eligible items, first current version and second stale, can commit the first while the RPC returns failure. Contract `S/37_BACKEND_COMMAND_CONTRACTS.md:384-393` requires all-or-nothing; existing test `T/interview_lifecycle_test.sql:175-178` is a one-item success. No later wrapper/core replacement was found. High source confidence; database reproduction unavailable.

### Material safeguards that actually exist

| Invariant | Effective source evidence | Assessment and limit |
|---|---|---|
| Identity/RBAC/RLS/SECURITY DEFINER | `M/20260905030000_identity_schema.sql:127-200`; command actor in `20260906070000:303-322`; private helper revokes :377-382; later internal-user repairs | Active identity derived from `auth.uid()`, granular permissions/Root checks, empty search paths and qualified relations are substantial safeguards. F02 prevents blanket confidentiality approval. |
| Durable Application identity / round allocation | `20260905100000:108-155`; `20260906060000:712-902` | Unique Submission+Unit+coalesced Team+Position and unique Application+round; Application locking, latest/inactive/HIRED guards and idempotency. Lock composition still needs F04 closure. |
| Schedule resource serialization | `20260906060000:519-639`; `20260906090000:150-256`; `20260911173229_internal_user_r3_review_repairs.sql:119-252` | Candidate, Room, sorted Interviewer resource locks; half-open overlap; later row/user fencing. Real domain complexity. Not proof every command pair is deadlock-free. |
| Idempotency | `20260906060000:435-514`; storage at `20260905120000_bulk_submission_status_and_application_assignment.sql:46-57` | Actor/command/key serialization, fingerprint mismatch detection, stored result. Preserve; does not imply bulk atomicity or NULL-version safety. |
| Current Round / Application Outcome / final decision source | `20260906005000:105-243`; `20260906060000:369-384`; `20260906070000:264-298` | Effective business outcome and resource-blocking rounds are distinct concepts. Central resolver is valuable; F05 is a missing integration call. |
| Report merge/owner semantics | Latest core/wrappers `M/20260909012000_interviewer_report_owner_only_command.sql:5-341`; later HR read wrapper `20260910024500_hr_report_review_repairs.sql:5-61` | Patched fields/base values, owner/HR distinctions, current/visibility checks; owner-only branch locks Application -> Interview -> Participant. Mixed-role branch's unlocked context reads remain a targeted race-review gap, not an independently established sixth SQL defect. |
| Participant history/lifecycle | `20260906090000:283-392`; current uniqueness/order indexes `20260906060000:133-139` | Remove/archive/restore/reorder semantics are implemented, not disposable CRUD complexity. Later eligibility/locking repairs must remain composed. |
| Document safety | `M/20260914090000_document_scan_request_protocol.sql:91-261`; `20260915010000_storage_cleanup_trusted_contracts.sql:276-352,660-843,854-1034`; `20260916010000_storage_cleanup_worker_runtime_binding.sql:11-33` | Reservation-derived identity, worker-only verdict, lease/fencing, provenance/tombstones, signed-upload lifetime and current/historical-reference retention. These cannot be replaced by broad bucket deletion or trusting browser scan results. |

No comprehensive audit of every Candidate submit/update, master-data, internal-user or email SQL branch is claimed. Existing SQL and synchronized concurrency tests are meaningful evidence assets but were not executed here. No migration was edited or replayed remotely.

## 5. Authentication / SSR / secrets and current official guidance

### F01: browser public environment access is broken

`W/lib/env/client.ts:6-12` uses `process.env[name]?.trim()`; :28 calls that helper with `NEXT_PUBLIC_SUPABASE_URL`. Publishable/anon key lookups at :18-19 are static. `W/lib/supabase/client.ts:5-8` invokes the helper. Login OTP at `W/app/login/page.tsx:194-215` and Google at :283-315 both instantiate that browser client.

The local process had explicit synthetic URL/key values. The served Next bundle retained dynamic URL access and inlined the key; clicking Send OTP caught the exact configuration exception before network Auth. The UI remapped it to an incorrect OTP/session message (`UNAUTHENTICATED`, login error mapping :58-101), which can misdirect diagnosis. Google displayed its generic exchange error through the same failing factory. This is not a missing Vercel setting inferred from an unconfigured environment.

[Next environment-variable guidance](https://nextjs.org/docs/app/guides/environment-variables), retrieved during the audit (page reported 16.3.6), explicitly says dynamic lookups such as `process.env[varName]` are not inlined, and public variables are fixed at build time. Installed code was 16.3.4; no dependency upgrade was made. A production build/provider login was not executed; source and actual dev-bundle behavior establish the implementation issue.

### F18: no request-layer SSR refresh path

`W/lib/supabase/server.ts:1-38` provides cookie getAll/setAll but catches cookie mutation failures in Server Components, with a comment that a proxy refreshes sessions. `W/src` is not a path prefix here: the actual sole request middleware is `W/middleware.ts:1-74`; it sets CSP/security headers and has no Supabase refresh call. Complete proxy/middleware inventory found no proxy implementation.

[Supabase SSR creating-a-client guidance](https://supabase.com/docs/guides/auth/server-side/creating-a-client) requires a request-layer refresh path because Server Components cannot write cookies: verify/refresh, propagate request cookies to the rendering request and response cookies to the browser, and preserve response/cache headers. Callback cookie exchange alone is not lifecycle coverage. Source gap is high confidence; no expired-token connected scenario was run, so exact refresh failure frequency is unmeasured.

[Next 16 upgrade guidance](https://nextjs.org/docs/app/guides/upgrading/version-16) deprecates the middleware filename in favor of proxy; deprecation does **not** mean the existing middleware stopped running. Local CSP headers and the Next warning demonstrated middleware execution. Renaming alone would not add refresh and must not discard nonce/CSP behavior.

### Existing authorization and secret boundaries

- `W/lib/auth/session.ts:148-204` calls `auth.getUser()` then resolves internal identity/roles/permissions using trusted `get_current_internal_session`; inactive/invalid results fail closed and no forbidden raw binding-column fallback is used. Candidate identity requires active own binding. A verified email ending `@eiu.edu.vn` selects a branch; trusted provisioning/directory authorization is still necessary.
- Supabase guidance distinguishes verified `getClaims()`/fresh network `getUser()` from raw `getSession()`. Existing server `getUser()` is valid verification, not an authorization bug just because current examples prefer `getClaims()`. `W/lib/auth/context.tsx:30-85` using browser getSession for display state is not evidence of server trust in an unverified session.
- Callback `W/app/auth/callback/route.ts:1-51` normalizes safe relative next destinations, exchanges code, provisions and signs out on provisioning failure. Candidate verify `W/app/auth/candidate/verify/route.ts:1-85` checks same origin and verifies OTP before provisioning. Focused tests exercised invalid/missing origin, redirect normalization and failure handling through controlled clients.
- `W/lib/supabase/admin.ts:1-19` and `W/lib/env/server.ts:1-17` are server-only. Privileged access is explicit for private Storage inspection/authorized streaming, not ordinary wholesale user mutations. No production secret values were read; no comprehensive bundle-secret scan was run in this phase, so this is boundary-source evidence, not leak certification.
- [Supabase API-key migration guidance](https://supabase.com/docs/guides/getting-started/migrating-to-new-api-keys), fetched directly, says legacy anon/service_role keys are deprecated by end-2026, permits coexistence during migration, and recommends publishable/secret replacements. Client code already accepts publishable with anon fallback; server configuration still names `SUPABASE_SERVICE_ROLE_KEY`. A new secret key remains privileged/RLS-bypassing, not a substitute for a narrow worker role. This is time-sensitive migration work, not proof of a current key leak or immediate legacy-key outage. Do not copy the guide's Edge Function JWT settings into nonexistent project functions.

## 6. Vercel / Supabase deployment readiness

| Surface | Repository/current-doc evidence | Current readiness conclusion |
|---|---|---|
| Build/runtime | `web/package.json:5-26`: Node 24.x, npm 11.19.0, Next 16.3.4, React 19.2.8; CI pins Node 24.20.0, Supabase CLI 2.116.0 | Local smoke used installed Node 24.18.0 / npm 12.0.2 and direct Node CLI. Not a production-build or exact CI toolchain pass. |
| Vercel mapping | Next app under `web/`; `web/README.md:1-34` remains generic scaffold; no located project deployment workflow/config/run evidence | Root/build/env/domain/protection mapping and deployed target SHA unverified. Absence of vercel.json alone is not a defect: dashboard settings can suffice, but were not observed. |
| Browser env | F01 plus Next build-time public-variable semantics | Supplying env alone cannot fix dynamic URL access. Separate non-production and production public values must be verified in built artifacts. |
| Preview vs production promotion | [Vercel promotion documentation](https://vercel.com/docs/deployments/promoting-a-deployment), direct page dated 2026-06-26 | Preview-to-production promotion rebuilds with production env. A staged production-target deployment can be promoted without rebuild. Generic “build Preview once and promote unchanged” is not an appropriate environment-isolation assumption. Rollback does not retroactively update embedded env. |
| Supabase migrations | `supabase/config.toml:33-63` uses PostgreSQL 17, migrations enabled, empty schema_paths; CI replays local migrations | Local/remote PG15 mismatch is not a supported finding. Current remote version/history/catalog not queried; prior research's PG17 cloud observation is historical only. Starter SQL is not an alternate deployment baseline. |
| Remote migration discipline | S/44:35-53; [Supabase database migrations](https://supabase.com/docs/guides/local-development/database-migrations), [managing environments](https://supabase.com/docs/guides/deployment/managing-environments) consulted via official Context7 sources | Versioned migrations, isolated staging rehearsal, remote history/drift reconciliation and exact grants/auth functions verification are required before production. No link/push/reset/pull operation was performed. |
| Auth operational setup | Provider/redirect/SMTP behavior cannot be established from local source | Google Workspace allowlist/provider and callback URLs, Candidate OTP delivery/limits, cookies/refresh/inactive-user deployed behavior need isolated live proof. Local SMTP capture is not email delivery. |
| Worker identities | Email/scan custom roles; cleanup authenticator role binding in `20260916010000` | Runtime credentials/role-switch mapping not proven for email/scan. Do not assume service-role can invoke intentionally revoked worker RPCs. |
| Recovery/monitoring | S/44:55-80,99-111 requires DB backup/PITR, object recovery, RPO/RTO, restore drill, alerting, capacity, privacy publication and break-glass rehearsal | Canonical operations requirements exist. Missing evidence is an executable environment-specific runbook/configuration and rehearsal, not “no operations contract anywhere.” |
| External runtime delivery | Section 7 | Absent/unverified workers and PDF prevent a full release claim. |

No assertion of “zero current Vercel deployments” or “currently inactive Supabase” is made. Those were prior research observations and cannot be refreshed with available tools. This audit neither deploys a diagnostic Preview nor authorizes a production release.

## 7. Email / scan / cleanup / PDF runtime matrix

| Capability | Contract / backend | Concrete runtime implemented | Missing boundary and user effect | Preview vs production |
|---|---|---|---|---|
| Operational email | `M/20260913010000_email_persistence_contracts.sql:231-537`: claim/authorize/complete, lease, retries/backoff/history, restricted worker; fresh config :1-31 is TEST/paused | Enqueue/preview/history web consumers. `InterviewEmailActions.tsx:75-76,126` accurately says queued and unchanged Interview status | No sender/provider launcher located. Auth OTP SMTP is separate. Need actual delivery/result/failure proof and credential/role wiring; queue success is not sent mail | Diagnostic Preview can explicitly test enqueue only; production communication cannot be accepted on that evidence |
| Malware scan | `20260914090000:91-310`: request, worker attempt/token/lease, verdict, CLEAN continuation | `W/app/candidate/candidate-actions.ts:634-704` authorizes, inspects, records, requests and returns PENDING_SCAN; :707-727 continues CLEAN. `lib/storage/upload-scanner.ts:121-204` checks bytes/MIME/hash only | No malware engine/provider/worker/result integration located. Required CV cannot safely become usable for a new Candidate; fail-closed behavior is correct but workflow incomplete | Blocks true new-Candidate E2E Preview and production. Never bypass CLEAN to make demonstration pass |
| Cleanup | `20260915010000:378-852,1031-1064` plus `20260916010000`: durable discovery/claim/authorize/complete and constrained runtime role | `W/lib/storage/cleanup-runner.ts:117-205` calls authorize -> exact provider remove -> fenced completion; provider/worker client exists and unit checks passed | No production invocation/cron/launcher found. Runner does not itself discover expired jobs, so scheduling only its batch loop is insufficient; discovery + batch + credentials/metrics needed | Short-lived synthetic diagnostics may inspect protocol; retention/storage production readiness not established |
| Generated report PDF | S/06 current-round, ordering/privacy/output rules; S/14:19 defers official pixel template only | HTML shared preview. HR button at `W/components/reports/HrReportView.tsx:637-645` permanently disabled. No renderer/export handler located | No downloadable generated output, no font/render/layout/privacy artifact exercised. Uploaded-PDF streaming is unrelated. Official visual template remains separate from generic required export | Blocks full report acceptance/Phase-1 production claim; does not prevent limited non-export diagnostic Preview |

Private storage, current/historical reference retention, signed-upload expiry and cleanup tombstones are legitimate safety constraints. No automatic business-data purge is required or recommended. External hosting outside the repository remains unverified rather than logically disproved.

## 8. Frontend maintainability and verification quality

Large orchestration is measurable: SubmissionDetailDrawer 1,411 lines/21 syntactic useState calls; ApplicationInboxTable 1,069/11; InterviewPage 1,254/10; InterviewDrawer 560/10; HrReportView 1,296/15; InterviewerReportView 302/7. These are source counts, not cyclomatic complexity, bundle costs or performance measurements.

Concrete defects are more useful than size labels:

- Drawer opening uses only `getSubmissionDetailAction`; `openSubmission` appears in its command definition and isolated tests, not runtime consumers (F08). The pure-read/explicit-intent distinction is correct; its composition is incomplete.
- `SubmissionDetailDrawer.tsx:236-242,776-1045,1296-1313` makes dirty state/Edit/Save HR-note-only, renders profile/education/HR-only sections as display values, and documents as preview/download (F09). The “Edit” affordance overstates scope relative to S/04.
- Full searches in Interview/Report components and interview actions found no interview document management consumer; drawer props at `InterviewDrawer.tsx:55-92` expose scheduling/participants/lifecycle, not documents (F10).
- `LocaleProvider.tsx:22-45` changes context and document language, while SubmissionDetailDrawer and InterviewDrawer hardcode Vietnamese labels/actions; CandidateForm:260-411 mixes fixed bilingual labels and VI-only helper text. Reports use the shared locale. S/10 section 6 requires operational filters/drawers/warnings/preview to follow VI/EN without discarding unsaved input (F16). No screen-reader language behavior or dirty-form language switch was certified in this phase.
- HrReportView:287-355 deliberately preserves independently dirty report/note values and old conflict bases across refresh. Simplifying that into whole-row resets would lose required user edits/merge semantics. Any future extraction should follow ownership and behavior, not an arbitrary line cap.

Testing distinction: `W/__tests__/hr-report-browser.test.ts:9-49` bundles a fake-data harness into a blank browser page; `fixtures/hr-report-browser-harness.tsx:293-323` models merge behavior in memory. Those interactions can be useful but cannot establish database merge/RLS or full Next wiring. `hr-report-server-adapter.test.ts:5-20` regex-checks argument names, not adapter behavior. The live login smoke found an integration defect that rendering/controlled-port tests did not establish. No tests were rewritten or deleted in this review-only phase.

Accessibility evidence is partial: shared Drawer/Dialog/StatusMenu primitives, semantic tables and Candidate error relationships exist; actual keyboard/focus/assistive-technology behavior across all workflows is unverified. No blanket WCAG pass/fail is inferred from source or a single mobile screenshot.

## 9. Governance / CI throughput and completeness semantics

### The Slice-06 counterexample

`project_control/SLICE_REGISTRY.yaml:17` marks Master Data / Users & Permissions DONE. `TASK_REGISTRY.yaml:1169-1234` materializes only two Slice-06 tasks, both trusted backend contracts and DONE. `AUTONOMY_RUN_STATE.yaml:370-374` explicitly leaves management experiences to later UI tasks. Canonical S/02:117-126 requires those rendered pages; route/nav inventory confirms absence.

`AUTONOMY_PARALLEL_GOVERNANCE.md:34-46` says slice status means user/business completion. `validate_control_plane.py:231-254` only checks statuses of existing members of a DONE slice; :288-305 permits current IN_PROGRESS slice pointing at a DONE task when no unfinished materialized member remains. Both validators passed freshly. Therefore:

- **Task acceptance:** bounded reviewed implementation/CI/checkpoint facts can be valid.
- **Slice feature completeness:** not implied by all materialized members DONE; Slice-06's label contradicts the stated meaning.
- **Phase-1 completeness:** not implied by 42/42 materialized tasks DONE; required UI/export/runtime pieces are missing and Slice-08 is IN_PROGRESS.
- **Production readiness:** requires deployed/runtime/security/operations evidence independent of those statuses.

**Can the scheduler remain procedurally consistent while mandatory unmaterialized UI is missing? Yes, for a scheduler/validator restricted to known tasks and dependencies. No, that does not make the whole feature-completion claim policy-conformant.** An unrestricted autonomous coordinator must reconcile sources/materialization, not equate empty frontier with finished product. Here `AUTONOMY_RUN_STATE.yaml:820-833` also contains an explicit acceptance-boundary hard stop before S08-002; respecting that hold is not a declaration that Phase 1 is complete. This audit does not remove it or create tasks.

Derived reporting is stale: `TRACEABILITY_STATUS.csv:1,39-55` says reconciled through S05-002 and leaves already-accepted backend commands NOT_STARTED. Validator :1120-1163 checks existence/disclaimer, not semantic freshness. A non-authoritative label prevents authority conflict but does not make stale navigation accurate.

### Concrete review value

- `project_control/reviews/S06_002_IMPLEMENTATION_REVIEW_OWNER_TRANSPORT_a7aa037_v1.md:17-29` records unmigrated consumers after auth binding-column revocation, dormant-participant regression, owner/lifecycle deadlock and bind/rebind lock inversion. Subsequent R2 review at `...7c37d46_v2.md:7-23` records additional Unit/User ordering and post-lock identity freshness concerns.
- Actual repair source exists: `M/20260912014500_internal_user_r4_authorization_prelock.sql:21-62` checks auth/permission before Email/Unit contention; `20260911173229_internal_user_r3_review_repairs.sql:273-305` rechecks verified Google evidence after locking; `W/lib/auth/session.ts:157-172` uses the narrow RPC after `app_users.auth_user_id` SELECT revocation.
- `T/internal_user_r4_authorization_prelock_test.sh:72-90,115-175` uses synchronized held-lock readiness and unauthorized/missing-auth cases. Historical candidate `63f6feba352852af5826dd582d1c42159edd66d6` and later exact integration acceptance are distinct; review records explicitly disclose Owner-transport/static-only provenance, not reviewer-native runtime proof.
- `project_control/reviews/SLICE_07_CLOSING_REVIEW_GATE_v1.md:123-150` caught missing manual email UI despite accepted backend work; the closing rereview `SLICE_07_CLOSING_REREVIEW_b4e06a6_v1.md:17-66` records its closure and explicitly defers scanner/live email/scheduler/deployment. This is evidence to retain composition review, not task-count closure.

### CI cost: verified examples, not a universal multiplier

| Exact history | Independently checked result | Interpretation |
|---|---|---|
| S06 product `80146bc5aab88f755312c7ffff6007c1099d6782`, run [34705140390](https://github.com/oanhpham-kobe/eiu-recruitment/actions/runs/34705140390) | Reviewer read successful Web 85s / DB 233s job metadata | Real historical product verification, not present DB execution |
| S06 governance-only `5f2b76c7f1e901b3cadb847906efcd1568c8cbc3`, run [34705634804](https://github.com/oanhpham-kobe/eiu-recruitment/actions/runs/34705634804) | Parent fresh `gh run view`: success; Web 16:34:20-16:35:43 UTC (83s), DB 16:34:20-16:38:15 (235s), 2026-09-12 | Git delta after product is only control files; CURRENT_STATE-only commit requests `[full-ci]`. Concrete repeated product verification. Durations are concurrent job elapsed time, not summed wall latency or billed cost |
| S08 acceptance `0d8c5c2129ed4c78a58c8d37bd22e93c14a763eb`, run [35882761018](https://github.com/oanhpham-kobe/eiu-recruitment/actions/runs/35882761018) | Parent fresh `gh run view`: impact success, Web SKIPPED, Database SKIPPED | Exact-SHA acceptance does not necessarily repeat full suites. Governance-only product-equivalence still needs evidence |

Parent Git inspection confirmed S06 `7cf3979 -> 5f2b76c -> ba004a9` changes only run/current/task state, and S08 `3070e56 -> 8dcb0a5` only control/review evidence. No full-history compute/billing estimate is made.

Current `.github/workflows/integration-ci.yml:40-99` selects web/db by path; canonical spec/workflow/unknown changes broaden, governance paths normally do not, and `[full-ci]`/dispatch can broaden both. Governance CI runs Python validators, not duplicate Web/DB jobs. This is path-level domain selection, not semantic dependency analysis; shared invariants still need judgment.

| Process control | Classification for this audit only | Evidence-based reason |
|---|---|---|
| Independent high-risk review, bounded repairs/re-review | KEEP | S06 caught concrete security/locking/consumer defects |
| Source-to-user-capability slice composition review | KEEP | S07 caught unmaterialized UI; Slice-06 demonstrates task-count blind spot |
| Exact-SHA CI/checkpoint and integration-equivalence proof | KEEP | Prevents acceptance of an unreviewed/different tree; checkpoint branches require process/protection, not assumed immutable Git semantics |
| Path-aware CI and justified full-domain escape hatch | KEEP | S08 demonstrates savings without falsely equating skipped tests with newly executed tests |
| Full product CI solely to manufacture a reporting SHA | LIGHTEN | S06 repeat had no intervening product change; policy already prefers impact-selected verification |
| Derived status, changed-file/equivalence receipts, evidence indexing | AUTOMATE | Mechanical facts are repeated/stale; generate from existing authorities, not a new registry |
| Separate audits proving exactly the same unchanged equivalence | REMOVE DUPLICATION | Only where scope/provenance/authority truly coincide; changed fixtures/workflows and slice composition are distinct proof obligations |
| Repeated mutable acceptance narratives/live historical snapshots | LIGHTEN | Retain concise current state and immutable links without erasing failure provenance |

These are classifications of process controls, not Phase-C system architecture decisions or permission to edit governance now.

## 10. Severity-ranked findings

Severity is launch/product/security impact, not estimated repair effort. P0 blocks the affected safe user journey or confidentiality boundary; P1 is a material required behavior/release gap; P2 is significant hardening/maintenance debt. “Preview” below distinguishes functional UAT from explicitly limited synthetic diagnostics. High source confidence does not mean live reproduction.

| ID | Severity / finding | Primary evidence | Prior research disposition | Confidence | Safe Preview / production impact |
|---|---|---|---|---|---|
| F01 | P0 browser public URL access breaks Auth initialization | env/client:6-28; login:194-215,283-315; actual browser exception and bundle | REVISED: new blocker beyond prior auth summary | High, runtime + source + official docs | Blocks functional sign-in Preview and production; static diagnostic page still renders |
| F02 | P0 direct Interviewer HR-note disclosure | `20260905100000:133-167`; `20260906060000:645-705`; S/39:81 | REVISED: contradicts blanket privacy endorsement | High source; live unverified | Blocks any real confidential-data Preview and production |
| F03 | P0 required CV has no located malware execution runtime | candidate-actions:634-727; scan protocol; S/44:104 | CONFIRMED, elevated to required user-journey consequence | High repository absence; external unknown | Blocks new-Candidate E2E and production; synthetic protocol inspection possible |
| F04 | P1 cross-command parent lock-order cycles | Effective round/create/delete/reactivate functions, section 4 | REVISED: new correctness counterexample | High source; race not run | Needs repair/proof for concurrent functional UAT and production |
| F05 | P1 reactivation leaves persisted Submission outcome stale | `20260906070000:664-710`; effective resolver | REVISED: new correctness counterexample | High source; SQL unexecuted | Affected lifecycle UAT/production blocked |
| F06 | P1 NULL version bypass at direct SQL boundary | `20260906070000:609,632,651,670,793,968-969` | REVISED: validation coverage overestimated | High source | Affected write-safety acceptance/production blocked |
| F07 | P1 bulk delete commits prefix on late JSON failure | `20260906070000:678-712,885-898`; S/37:384-393 | REVISED: transaction composition overestimated | High source | Bulk lifecycle acceptance/production blocked |
| F08 | P1 explicit HR open never calls NEW-to-READ command | Inbox/Drawer/action/pure-RPC chain; S/04:63-67 | REVISED: additional incomplete accepted-module behavior | High source | Required HR/Candidate edit lifecycle incomplete |
| F09 | P1 whole HR Submission edit/document editing missing | Drawer:236-242,776-1045,1296-1313; S/04:117-131 | REVISED: additional product gap | High source | Full HR UAT/Phase-1 production incomplete |
| F10 | P1 Interview document UI/consumers missing | InterviewDrawer:55-92; report drawer; bounded searches; S/05 | REVISED: additional product gap | High bounded absence | Full Interview/Interviewer capability incomplete |
| F11 | P1 Master Data management UI absent | Route/nav inventory; `20260910153441:319-369`; S/02,09 | CONFIRMED | High bounded absence | Limited Preview possible, full Phase-1 release incomplete |
| F12 | P1 Users & Permissions UI absent | Route/nav; `20260911104630:262-311` and later repairs; S/02 | CONFIRMED | High bounded absence | Limited Preview possible, full Phase-1 release incomplete |
| F13 | P1 email sender runtime absent/unverified | `20260913010000:231-537`; enqueue copy | CONFIRMED within repository | High source; external unknown | Enqueue-only Preview not delivery UAT; production gap |
| F14 | P1 cleanup discovery/scheduling/credential launch absent | cleanup-runner:117-205; worker binding/discovery SQL | CONFIRMED with runner distinction | High source; external unknown | Short diagnostics possible; operational production gap |
| F15 | P1 generated PDF absent | HrReportView:637-645; S/06 vs S/14:19 | REVISED: pixel deferral is not export deferral | High source | No complete report/export acceptance |
| F16 | P2 incomplete global VI/EN; responsive/accessibility proof partial | LocaleProvider and hardcoded drawers; S/10 section 6 | REVISED: more concrete than component-size debt | High source for locale, other UAT unverified | Limited Preview possible; required language/accessibility acceptance unresolved |
| F17 | P2 unexpected error message reflection | preview route:58-60; Inbox action:70-75 | CONFIRMED for preview route, additional analogous boundary | High source; no secret leak observed | Harden before real-data use; no claim every thrown error leaks secrets |
| F18 | P1 SSR request-layer refresh missing | server client catch/comment; sole headers-only middleware | CONFIRMED; filename deprecation itself not failure | High source; expiry UAT unexecuted | Session lifecycle acceptance/production gap |
| F19 | P1 Slice-06 DONE misstates feature completeness | registry/run-state/validator/source/nav, section 9 | CONFIRMED; validator consistency is insufficient | High + fresh validators | Blocks truthful full-scope acceptance, not page rendering |
| F20 | P1 deployment/operations evidence incomplete | S/44 exists; workflows local checks; cloud unavailable | REVISED: requirements exist, execution not proven | High evidence-gap confidence; current cloud unknown | Cannot certify safe deployed UAT or production |
| F21 | P2 command/error/coverage conventions drift | Three adapter styles; F06/F08/F17 and harness limits | CONFIRMED in bounded form, no automatic generic-framework prescription | High source | Neither alone; increases regression/change cost |
| F22 | P2 stale/repeated process evidence and historical CI amplification | Traceability disclaimer; S06/S08 exact runs/deltas | REVISED: current path-aware CI already helps | High bounded history | Neither runtime blocker alone; reporting/delivery cost |
| F23 | P2 legacy privileged-key configuration migration due | env/server:1-17; current Supabase key docs | REVISED: time-sensitive migration, not demonstrated leak/outage | High source/docs, cloud key type unknown | Not automatically a current Preview blocker; production credential lifecycle must be verified |

Remediation directions in this audit name violated boundaries and needed proof. They are not implementation authorization, assigned tasks or a replacement architecture plan.

## 11. Prior research reconciliation — fourteen claims

The following ledger uses explicit claim text to avoid conflating differently numbered questions across the research pack. Dispositions are CONFIRMED / REVISED / REJECTED / UNVERIFIED; “new finding” means additional evidence, not an assertion the researcher tested and missed that exact scenario.

| # | Prior claim | Disposition | Independent conclusion / evidence |
|---|---|---|---|
| 1 | Core Next/Supabase/PostgreSQL architecture is broadly sound | REVISED | Meaningful server/RPC/RLS/locking primitives exist, but F01-F07 contradict any broad working/security/correctness endorsement. Architecture primitives and composed behavior must be assessed separately. No Phase-C conclusion follows. |
| 2 | A full rewrite is unsupported / should not be the default | UNVERIFIED | Strategic verdict deliberately deferred to Phase C. This phase supplies contrary/confirming evidence without endorsing or rejecting a global rewrite. |
| 3 | Master Data management UI is absent | CONFIRMED | Complete six-page/four-handler inventory, three-item Root nav and absent management consumers; real backend lifecycle functions exist. |
| 4 | Users & Permissions management UI is absent | CONFIRMED | Same route/nav/consumer bounds; directory/RBAC backend exists and includes later security repairs. |
| 5 | All materialized tasks DONE can conceal unmaterialized required UI, especially Slice-06 | CONFIRMED | Fresh validators pass with 42 tasks and empty frontier; only two backend S06 tasks; later_ui_tasks explicit. Slice DONE nevertheless violates policy's business-completeness meaning. |
| 6 | Multiple command styles and large UI orchestration create maintenance debt | REVISED | Three adapter styles and concentrated state are real. Size alone does not prove over-engineering. Concrete omissions/error/version drift matter; field-aware dirty-state/merge complexity is required. |
| 7 | Actual operational email sender is absent | CONFIRMED | No provider/launcher found in bounded runtime inventory; robust outbox/worker protocol and truthful enqueue UI exist. External untracked runtime remains unknown. |
| 8 | Actual malware scanner runtime is absent | CONFIRMED | Byte inspection explicitly excludes scanner/verdict; worker protocol lacks located engine/provider. This blocks required new-Candidate CV completion, not merely optional infrastructure. |
| 9 | Cleanup runtime scheduling is absent | CONFIRMED | Real provider-call runner exists; no launcher/scheduler. Discovery is separate and also needs invocation. Not “cleanup backend absent.” |
| 10 | PDF is incomplete and can wait until official template arrives | REVISED | Missing generated output confirmed. REJECTED subclaim: deferring official pixel template permits deferring all PDF. S/06 still requires export; S/14:19 is narrower. |
| 11 | Vercel/Supabase operational deployment readiness is not proven | REVISED | Readiness remains unproven, but S/44 does provide normative operations requirements. Present cloud deployment count/status/version is UNVERIFIED; do not repeat historical “zero/inactive” as current fact or resurrect the PG15 mismatch. |
| 12 | SSR refresh middleware/proxy is missing | CONFIRMED | Sole middleware handles headers; cookie catch assumes an absent proxy. REJECTED subclaims: deprecated filename means nonexecution, or existing verified server getUser is inherently invalid. |
| 13 | Independent review caught real security/concurrency defects | CONFIRMED | S06 review records, actual later repairs, synchronized test source and exact historical CI substantiate bounded examples. Owner-transport provenance and non-reproduction limits retained. |
| 14 | Governance/evidence serialization duplicates work and full CI | REVISED | S06 concrete repeat confirmed; S08 exact-SHA acceptance skips Web/DB. Composition review and integration-equivalence are distinct valuable controls. Blanket removal or “all governance CI repeats product tests” is rejected. |

Research actually read: status, final synthesis, DR-03, DR-04 delivery, DR-04B and DR-04C. The handoff's DR-04 filename dated 2026-09-26 does not exist; directory discovery resolved the actual `DR-04_DELIVERY_THROUGHPUT_2026-09-27.md`. Research was treated as leads, not authority. Older broad research was not required to reassert unobservable cloud facts.

## 12. What is worth preserving as evidence-backed assets

This section is not a final KEEP plan. Preservation-worthy assets include:

- Canonical domain distinctions: Candidate/Submission/Application/round/participant/report, Current Round versus schedule-blocking history, and final-decision source.
- User-context server clients, explicit server-only privileged boundary, database-authoritative permissions and direct-RPC validation/RLS obligations.
- Durable uniqueness, idempotency fingerprints/replay, resource locking, active-user revalidation and immutable lifecycle/history rules, with composed defects repaired rather than safeguards discarded.
- Field-aware report merge and independently dirty form state; contextual projections and participant ordering.
- Private Storage streaming/audit, scan trust separation, durable cleanup provenance/tombstones and stale-attempt fencing.
- Real operational UI already present: Candidate form, grouped Inbox, Interview scheduling/participants, both report views, email preview/enqueue/history, shared interaction primitives.
- Focused behavioral tests and synchronized concurrency harnesses; exact-SHA review/CI/checkpoint provenance and source-to-capability composition review.

None of these assets proves full release readiness or resolves F01-F23 by itself.

## 13. What is incomplete

User-facing: both administration experiences; explicit-open status transition; whole HR Submission editing/documents; Interview document consumers; generated PDF; complete VI/EN coverage; connected multi-persona/mobile/accessibility UAT.

Correctness/security: public Auth initialization; direct Interviewer column confidentiality; composed parent lock order; reactivation outcome recalculation; NULL-token stale protection; all-or-nothing bulk failure; request-layer refresh; safe unexpected error boundaries.

Operational: real email delivery; real malware result processing; cleanup discovery/schedule/identity hosting; verified environment mapping/build values/provider redirects; exact remote migration/grant parity; restore/Storage consistency, alerting and runbook rehearsal.

Reporting: source-backed slice completeness distinct from materialized task closure, fresh derived traceability and clear historical-versus-current runtime proof. No missing item is silently removed from Phase 1. No new task is materialized here.

## 14. What appears over-engineered — only where evidence supports it

- Repeated actor/RPC/error plumbing in three TS styles creates extra conventions without a demonstrated distinct trust-boundary benefit for the repeated mechanics. Domain-specific permission/merge/SQL logic remains necessary; replacing all adapters with another framework is not justified by this finding.
- S06 full product CI on a CURRENT_STATE-only follow-up repeats previously green unchanged product checks. Current impact-aware CI already offers the simpler path; the excess was gate placement/marker use, not lack of a new CI engine.
- Multiple mutable narratives and stale derived reports repeat acceptance facts. Evidence should resolve to existing authorities and immutable links; another manually curated completeness registry would compound the problem.
- Source-text argument-name tests and fake merge harnesses cannot be counted as independent proof of actual adapter/database behavior. They add maintenance cost when used as substitutes rather than appropriately bounded component checks.

Not established as over-engineering: component size alone; number of migrations alone; multiple security layers; database constraints/locks; participant history; scan/cleanup durable state; exact-SHA provenance; every prompt/review round. No measured bundle/render bottleneck or universal commit-to-cost ratio was established.

## 15. What is required complexity

Authentication is not authorization. Verified identity, active binding, granular permissions, RLS/grants and contextual projections protect different attack surfaces. F02 demonstrates why safe UI cannot replace SQL confidentiality.

Multiple actors can edit schedules/reports and change directory eligibility concurrently. Row/resource locks, deterministic ordering, after-lock revalidation, expected versions, field-level merge and idempotency address different failure modes. F04/F06/F07 are composition defects, not reasons to remove concurrency controls.

Uploads and external side effects cross transactions and provider time. Quarantine/inspection/scan verdict separation, leases/fencing, exact object identity, signed lifetime and retained historical references prevent unsafe acceptance/deletion. Durable email history and outbox attempts distinguish queued, attempted and delivered work.

User workflows need unsaved-state protection, stale-data recovery, historical/current distinctions, permission-aware actions and bilingual accessible interaction. Extracting components must preserve those semantics.

Independent high-risk review, repaired-invariant proof, slice composition and integration equivalence answer different questions. They can be made less repetitive without pretending a task registry or passing fixture proves the whole product.

## 16. Evidence gaps and Owner questions

### Missing proof, not permission to bypass it

1. No current cloud read access was available: need read-only Vercel deployment/build/env-name/target evidence and Supabase project status/version/migration/grants/provider/redirect/worker-runtime evidence. No secret values are needed in an audit artifact.
2. Docker engine unavailable: the five SQL findings need disposable local migration replay and focused direct-role/two-session scenarios. Existing passing historical CI does not negate source counterexamples. Do not run cleanup/concurrency fixtures against shared or production data; some harnesses perform setup/deletion.
3. Expired-token SSR refresh, signout/inactive-account revocation, Workspace onboarding/rebind and Candidate OTP delivery were not exercised against an actual Auth environment.
4. No authenticated persona E2E, real external email/scan/cleanup run, generated PDF artifact, full keyboard/assistive-tech run or Candidate mobile form submission was observed.
5. Mixed-role report command context locking, full Candidate transaction families and every effective ACL were not exhaustively verified. This audit is not a penetration-test or formal concurrency proof.
6. Dependency audit/production build/full suite were not rerun. Fresh evidence is the actual local Auth smoke, 39 focused tests, two validators and read-only historical Git/CI retrieval described above.

### Owner decisions needed for a later authorized phase

- Identify the isolated non-production target and explicitly authorize any future live rehearsal/deployment; do not use production PII for Preview. Current review authorization did not cross that boundary.
- Supply/confirm official PDF visual template and its operational acceptance role. Generic export remains a current requirement independently; no request to shrink that scope is implied.
- Confirm operational ownership/provider choices for email, malware scanning, cleanup hosting/credentials and monitoring/recovery; untracked external implementations, if any, need evidence before being counted.
- Confirm the acceptance scope of any proposed diagnostic Preview: limited synthetic inspection versus full Phase-1 UAT. Missing mandatory capabilities cannot be relabeled optional by the implementer.

No clarification blocks this Phase-B artifact. Phase C, implementation, governance repair, task materialization, migration/deployment and any broader branch integration remain outside this completed audit scope. The final handoff reports the artifact hashes and exact pushed review commit separately to avoid a self-referential hash/commit claim inside frozen content.

PHASE_B_CURRENT_STATE_AUDIT_FROZEN: YES
