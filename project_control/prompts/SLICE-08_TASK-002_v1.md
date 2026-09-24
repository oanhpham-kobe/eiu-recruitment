# TASK-S08-002 — Durable Distributed Rate Limiting and Abuse Controls v1

## Dispatch gate

This is a governed implementation prompt for future Owner dispatch. It is **not implementation authority by itself**.

Canonical source reconciliation:

- `project_control/reviews/S08_002_SOURCE_RECONCILIATION_v1.md`
- Work ID `S08-002-SOURCE-RECONCILIATION-001`
- independently reviewed by OMP under `S08-002-SOURCE-REVIEW-001`
- reviewed source SHA `a99375932e95805a8b52a6a159eb94a755c88986`
- verdict `PASS`
- `SOURCE_REOPEN_REQUIRED=false`
- task materialization authorized, implementation not authorized.

Persisted independent-review evidence:

- `project_control/reviews/S08_002_SOURCE_REVIEW_a993759_v1.md`

Implementation remains prohibited until all of the following are true:

1. TASK-S08-002, this prompt, the source reconciliation and source-review evidence are materialized in the control plane;
2. an immutable annotated `checkpoint/pre-S08-002-001` is created on that exact governed materialized baseline;
3. OMP/`eiu-reviewer` independently reviews this prompt plus the reconciled sources on the exact peeled checkpoint SHA and returns PASS with `SOURCE_REOPEN_REQUIRED=false`;
4. prompt-review PASS evidence is persisted; and
5. the Owner explicitly dispatches TASK-S08-002 implementation.

Never substitute a moving integration branch for the governed checkpoint SHA.

Accepted predecessor:

- `TASK-S08-001 — Application Inbox Search and Indexed Pagination Hardening`
- `checkpoint/S08-001-accepted-001` peels to `0d8c5c2129ed4c78a58c8d37bd22e93c14a763eb`.

Do not move or rewrite any accepted checkpoint.

---

## Source authority

Read first:

- `project_control/reviews/S08_002_SOURCE_RECONCILIATION_v1.md`
- `project_control/reviews/S08_002_SOURCE_REVIEW_a993759_v1.md`
- `recruitment_webapp/review_pack/68_RATE_LIMIT_POLICY.md`
- `recruitment_webapp/review_pack/38_NON_FUNCTIONAL_REQUIREMENTS.md`
- `recruitment_webapp/review_pack/67_WEB_SECURITY_BASELINE.md`
- `recruitment_webapp/review_pack/47_AUDIT_LOGGING_SPEC.md`
- `recruitment_webapp/review_pack/37_BACKEND_COMMAND_CONTRACTS.md`
- `recruitment_webapp/review_pack/55_COMMAND_COVERAGE_MATRIX.md`
- `recruitment_webapp/review_pack/63_BATCH_OPERATION_SEMANTICS.md`
- `recruitment_webapp/review_pack/100_TECHNICAL_PRECODE_GATE_V1_18.md`

Inspect the accepted implementation before changing anything, especially:

- `web/src/app/login/page.tsx`
- `web/src/app/auth/candidate/verify/route.ts`
- `web/src/app/candidate/candidate-actions.ts`
- `web/src/app/application-inbox-actions.ts`
- `web/src/app/interviews/actions.ts`
- `web/src/app/reports/actions.ts`
- `web/src/lib/security/`
- `web/src/lib/auth/session.ts`
- `web/src/lib/commands/candidate-submission.ts`
- `web/src/lib/commands/storage-reservation.ts`
- `web/src/lib/commands/email-commands.ts`
- `web/src/lib/application-inbox/server.ts`
- `web/src/lib/interview/server.ts`
- `web/src/lib/reports/hr-server.ts`
- accepted migrations that define Candidate Submit/Update, upload, Application Inbox read, email enqueue/bulk enqueue and Interview upload RPCs;
- relevant existing Web and SQL regression suites.

Do not edit accepted predecessor migrations. Database changes use new forward-only migration(s).

---

## Bounded outcome

Implement one reusable, durable, distributed abuse-control layer over the **currently reachable accepted endpoints/actions only**.

Required properties:

1. shared durable state suitable for multiple Vercel instances;
2. atomic concurrency-safe quota consumption;
3. configurable canonical initial defaults from `68_RATE_LIMIT_POLICY.md`;
4. trusted client-IP resolution that cannot be selected by arbitrary spoofed forwarding headers;
5. literal HTTP `429` at user-facing rate-limited HTTP boundaries and `Retry-After` wherever canonical policy requires it;
6. no bypass of existing Auth, RLS, permission, same-origin, optimistic-lock, idempotency, malware-scan, outbox or trusted-command contracts;
7. no raw OTP, token, signed URL, file content or PII search text in counter state/logs/audit;
8. bounded counter lifecycle/cleanup;
9. behavior-driven local/CI proof for burst, concurrency, distributed-client, expiry/reset and forged-header cases;
10. no production deployment, no connected/hosted Supabase mutation and no production-secret use.

This task does **not** implement a new PDF feature or any missing business feature merely to attach a limiter.

---

## A. Canonical policy matrix

Initial values are configuration, not immutable business rules.

### A1. Candidate OTP request

Keys/limits:

- normalized email: `5 / 15 min`;
- trusted client IP: `20 / 15 min`.

Response:

- HTTP `429` + authoritative `Retry-After`.

The current browser-direct `supabase.auth.signInWithOtp(...)` path must move behind an application-controlled same-origin server boundary before provider dispatch.

Do not expose a service-role credential to the browser.

Rate-limit consumption happens before the Supabase OTP provider call. Provider-native stricter limits remain effective; application limiting never masks or weakens them.

OTP tokens are never limiter keys, logs or audit payloads.

### A2. Candidate OTP verify

Keys/limits:

- auth/session/email identity: `10 / 15 min`;
- trusted client IP: `50 / 15 min`.

Response:

- HTTP `429` + authoritative `Retry-After`.

Preserve existing same-origin validation, request validation, Supabase `verifyOtp`, session behavior and Candidate provisioning.

Consume the application quota before provider verification so failed OTP attempts are covered. Never use the submitted OTP token as key material.

### A3. Candidate Submit

Canonical limit:

- Candidate identity with the source-required IP dimension;
- `5 / hour`;
- `20 / day`;
- HTTP `429`.

Do **not** invent a separate numeric IP-only ceiling that canonical source does not specify.

Prompt/implementation review must verify the exact key composition used for the source's `candidate_id` primary + `IP` secondary semantics. The implementation must not shard the Candidate quota in a way that permits bypass by changing a non-authoritative dimension.

Resolve/authenticate the Candidate before quota consumption. A blocked Submit executes no Submission/document/privacy/outbox mutation.

The authoritative database mutation path must not be bypassable by calling an existing executable RPC directly.

### A4. Candidate Update Save

Canonical limit:

- `candidate_id + trusted IP`;
- `30 / 15 min`;
- HTTP `429` + `Retry-After` before mutation execution;
- no partial Save.

Preserve all accepted Candidate Update semantics, including strong-current privacy, optimistic versioning, DTO allowlist, document finalization, exact-Submission notification and idempotency.

The required Candidate system HR-notification remains a transactional Outbox side effect of a valid Save. It is **not** blocked by the manual/system email enqueue quota and provider delivery throttling cannot roll back a committed Candidate Save.

The authoritative database mutation path must not be bypassable by calling the underlying RPC directly.

### A5. Upload reserve/completion/finalize

Canonical limits:

- Candidate/app_user identity: `30 / 15 min`;
- trusted client IP: `100 / 15 min`;
- HTTP `429`.

Current Candidate interactive boundaries include:

- `reserveUploadAction(...)`;
- `completeAndStageUploadAction(...)`.

Rate-limit user-initiated reserve and completion/staging requests.

Do **not** double-charge:

- scanner worker claim/result;
- CLEAN continuation;
- cleanup worker operations;
- final document binding that occurs inside an already separately governed Candidate Submit/Update transaction.

Preserve reservation expiry, signed-upload security, malware scanning, fencing and cleanup contracts.

Canonical command coverage also defines `reserve_interview_upload` and `finalize_interview_upload`. At the governed baseline, inspect both Web reachability **and database EXECUTE reachability**. If an accepted app_user-accessible path can invoke them, enforce the same upload policy without inventing a new UI. If they are unreachable, record that evidence and leave them unexposed.

### A6. Internal search

Canonical aggregate limit:

- authenticated internal `app_user_id`;
- `120 / min`;
- HTTP `429`.

At minimum, cover every currently accepted free-text search server entry point identified by source review:

1. Application Inbox — `queryApplicationInbox(...)` / `loadApplicationInbox(...)`;
2. Interview/Application grouped page query — `queryInterviewPageAction(...)` / `loadInterviewPage(...)` when free-text query is non-empty;
3. Interview Submission option search — `searchSubmissionOptionsAction(...)`;
4. Interview Application option search — `searchApplicationOptionsAction(...)`;
5. HR Report search — `refreshHrReportPageAction(...)` / `loadHrReportPage(...)` when free-text search is non-empty.

Before implementation, re-enumerate the exact accepted baseline and add any other **currently reachable internal free-text server search boundary** found there.

Use one canonical `INTERNAL_SEARCH` app_user quota across covered internal free-text search surfaces unless independent prompt review finds source evidence for per-page quotas. Do not allow switching pages/endpoints to multiply the 120/min allowance.

Do not consume search quota for ordinary non-search page/filter refreshes whose free-text term is empty.

The raw Name/Email/Phone/query string must never appear in:

- limiter key/storage;
- URL/history/shareable links;
- logs/telemetry;
- Security Audit metadata;
- returned error messages.

S08-001 search indexes, normalization, minimum Name rule, page-size, debounce, Candidate-group pagination and latest-Submission semantics are not reopened.

### A7. Manual/system email enqueue

Canonical primary quota:

- `app_user_id + email_type`;
- `60 / hour`;
- burst `10 / min`;
- HTTP `429`.

Canonical secondary dimension:

- exact business entity.

Current accepted actions include:

- `enqueueInterviewEmailAction(...)`;
- `bulkEnqueueInterviewEmailsAction(...)`;
- underlying `enqueue_email` / `bulk_enqueue_email` trusted RPCs.

For bulk enqueue, rate-account **each enqueue item/entity**, preserving the existing `PER_ITEM_ENQUEUE_RESULT` contract.

The shared primary actor+email_type 60/hour and 10/min counters must be incremented once for each attempted new enqueue item; do not shard the primary quota by entity such that sending to many different entities bypasses the actor/type ceiling.

The exact entity remains the secondary per-item dimension for correct attribution/fencing. Do not weaken the aggregate primary ceilings.

Preserve:

- preview fencing;
- exact business context;
- idempotency;
- max batch size;
- `success[]` / `failed[]` semantics;
- asynchronous provider delivery;
- Email History retention/audit contracts.

The protected database enqueue path must not be bypassable by direct RPC invocation by an otherwise authenticated caller.

Candidate Submit/Update's required transactional HR notification is not reclassified as a manual enqueue and must not be rejected by this quota.

### A8. PDF generation

Canonical future policy remains:

- `app_user_id + exact entity`;
- `20 / hour`;
- HTTP `429`.

No runtime PDF generation endpoint exists at the reconciled baseline. Do not create one in this task.

The reusable policy registry/limiter API must be capable of representing this policy and unit tests may validate the configuration shape without inventing PDF product behavior.

---

## B. Durable limiter architecture

### B1. Shared database state

Use a durable shared mechanism compatible with multi-instance Vercel execution and disposable local CI.

A Supabase/Postgres-backed limiter is the expected default for this repository because it introduces no new external provider dependency. A different provider-native durable store requires independent prompt/source approval before implementation.

Forbidden:

- module-global `Map`;
- process memory token bucket;
- one-instance-only cache;
- browser-owned counters;
- client-selected trusted identity/IP keys.

### B2. Atomic multi-rule consumption

A request may have multiple simultaneous rules/windows, for example Email+IP, identity+IP, hourly+daily or hourly+burst.

Evaluate all applicable rules in one authoritative atomic operation.

Requirements:

- deterministic lock/key ordering;
- no concurrency overshoot beyond configured quota;
- no partial quota debit when another mandatory rule for the same request blocks;
- blocked business operation starts no protected mutation/provider dispatch;
- returned retry timing derives from the authoritative limiting window(s), not a guessed constant.

The implementation may use fixed windows or an equivalently testable durable algorithm, but exact canonical limits/windows must be provable and configuration-driven.

### B3. Counter representation and privacy

Persist only minimum enforcement material, such as:

- action/policy code;
- opaque/pseudonymized key digest rather than raw email/IP/search text where feasible;
- window identity/timestamps;
- count;
- expiry/last-seen metadata;
- bounded safe audit marker metadata.

Never persist:

- OTP token;
- access/refresh token;
- session cookie;
- signed URL/token;
- uploaded file content;
- raw PII search term;
- service-role secret.

If hashing/pseudonymization is used, document the threat model and do not introduce an undeclared production secret dependency merely to satisfy tests.

### B4. Bounded state lifecycle

Limiter storage must not grow permanently by window rollover.

Use a bounded strategy, such as reusable per-key rows plus expiry/reset and a bounded opportunistic stale-row cleanup path, or another independently reviewed design.

Do not add a production cron/scheduler/daemon in this task.

Tests must prove window rollover/reset and stale-state cleanup behavior.

### B5. Security and grants

Limiter tables/helpers are private infrastructure.

- no direct browser SELECT/INSERT/UPDATE/DELETE;
- no arbitrary anon/authenticated function that lets a caller choose another user's limiter identity/IP key;
- narrow SECURITY DEFINER/helper grants only where justified;
- search_path hardened for definer functions;
- existing RLS/business permissions remain independently authoritative.

For authenticated business RPCs that remain directly executable, enforce the limiter inside or beneath the authoritative RPC path so bypassing the Web wrapper cannot bypass the quota.

---

## C. Trusted client-IP resolution

Implement one server-only trusted-IP resolver with explicit environment semantics.

Production Vercel behavior must be grounded in Vercel's documented platform headers. Vercel documents that its `x-forwarded-for` is the public client IP and is overwritten by Vercel to prevent spoofing; `x-vercel-forwarded-for` is the Vercel-specific equivalent. Prefer a narrow documented resolver rather than accepting arbitrary forwarded chains.

Requirements:

1. production Vercel mode trusts only the documented Vercel-controlled source selected by the implementation;
2. arbitrary client-supplied forwarding chains are never accepted merely because a header is present;
3. non-Vercel/self-hosted mode must fail closed for IP-keyed policies unless an explicitly configured trusted-proxy contract exists;
4. local/unit tests use dependency injection or an explicit test-only trusted-IP input, not a production spoof bypass;
5. normalize/validate IP before deriving limiter key material;
6. never log raw IP unless separately required by an accepted security policy.

Forged-header negative tests are mandatory.

---

## D. HTTP transport and 429 semantics

Canonical policy says `429`, and selected actions require `Retry-After`.

Route Handlers can explicitly control HTTP status and response headers. Existing Server Actions must not be assumed to satisfy literal 429/Retry-After merely because they return an object containing an error code.

For any current user-facing protected action where the existing Server Action transport cannot prove the required HTTP contract, introduce a **narrow same-origin POST Route Handler** and have it call the existing accepted server adapter/trusted command.

Do not duplicate business logic in the handler.

Examples of likely transport boundaries include:

- Candidate OTP request;
- existing Candidate OTP verify route;
- Candidate Submit/Update;
- Candidate upload reserve/completion;
- internal free-text search calls;
- manual/bulk email enqueue.

The implementation may consolidate transport only when route-level authorization, DTOs and error semantics remain explicit; do not create a generic privileged mutation dispatcher.

Every new state-changing route must preserve same-origin validation and authenticated session checks appropriate to the accepted command.

PII search terms remain in POST request bodies/component state, never query strings.

Rate-limit rejection payloads use a stable code such as `RATE_LIMITED` plus safe retry metadata; they never echo the sensitive limiter key/input.

`Retry-After` is an integer number of seconds or another RFC-compatible value derived from authoritative expiry.

---

## E. Audit / abuse evidence

Security Audit must record blocked/repeated abuse in a data-minimized manner.

Do not write one unbounded audit row for every subsequent denied packet if that would create an audit-amplification DoS. Prefer a bounded/deduplicated per-key/window block event or equivalently safe source-compliant strategy.

Allowed safe metadata may include:

- policy/action code;
- actor ID when already authenticated;
- entity type/id when non-sensitive and source-required;
- window/limit metadata;
- result `DENIED`;
- source (`WEB`/`RPC`);
- retry-after seconds;
- opaque limiter fingerprint.

Do not include raw email/IP/search term/OTP/token/signed URL/file content.

Existing business Security Audit rules and same-transaction mutation audit requirements remain unchanged.

---

## F. Idempotency and rate accounting

Do not weaken accepted idempotency contracts.

A limiter must not create duplicate business mutations/outbox rows.

Prompt/implementation review must explicitly document how exact idempotency replay is counted for Candidate Submit/Update, upload reserve and email enqueue. A replay that returns a previously committed result without executing a new protected mutation must not become a quota-bypass mechanism, and implementation must not silently change accepted replay semantics.

Bulk email remains per-item result semantics.

---

## G. Required database verification

Add behavior-driven SQL tests for the durable primitive and every database-enforced protected path.

At minimum prove:

1. exact threshold pass/block behavior for each configured window;
2. independent OTP email/IP and verify identity/IP limits;
3. Candidate Submit hourly+daily behavior;
4. Candidate Update 30/15 behavior;
5. upload identity+IP behavior;
6. shared internal-search 120/min behavior where database-enforced;
7. email 60/hour + 10/min aggregate actor/type behavior with per-item bulk accounting;
8. no entity-sharding bypass for primary email quota;
9. concurrency with simultaneous clients cannot overshoot;
10. multi-rule request is all-or-nothing for quota debit;
11. retry-after/window expiry correctness;
12. stale counter cleanup/reset;
13. grants prevent arbitrary client counter manipulation;
14. direct protected RPC invocation cannot bypass database-enforced quota;
15. denial leaves protected business state unchanged.

Run:

- clean disposable/unlinked local migration replay;
- focused S08-002 SQL suites;
- affected Candidate Submission/Upload/Email/Application Inbox regressions;
- relevant S08-001 search SQL regressions;
- crossed security/RLS regressions where directly affected;
- DB lint.

Do not mutate connected/hosted Supabase.

---

## H. Required Web / transport verification

Add focused Web tests for:

1. OTP request now server-mediated before provider dispatch;
2. OTP request 429 + Retry-After;
3. OTP verify 429 + Retry-After while preserving same-origin behavior;
4. Candidate Update 429 + Retry-After with zero mutation dispatch;
5. Candidate Submit 429;
6. upload reserve/completion 429;
7. internal search 429 with raw query absent from URL/log/error/limiter inputs;
8. shared internal-search quota across Application Inbox, Interview searches and HR Report search;
9. single and bulk email 429/per-item result mapping;
10. exact `Retry-After` propagation where required;
11. forged/unapproved forwarding headers cannot choose the trusted client-IP key;
12. approved Vercel trusted-IP behavior is tested through a testable resolver boundary;
13. no service-role credential reaches browser bundles;
14. existing auth/RLS/permission denial behavior remains effective;
15. no generic privileged dispatcher is introduced.

Expected Web gates:

- focused S08-002 tests;
- affected existing auth/Candidate/Inbox/Interview/Report/Email tests;
- full `npm run test`;
- `npm run lint`;
- `npm run typecheck`;
- `npm run build`;
- `npm run design:check` when touched UI behavior requires it.

---

## I. Multi-instance / burst evidence

The source explicitly requires distributed-instance and burst verification.

Add a deterministic local/CI harness using multiple independent application/database clients against one shared disposable limiter state.

Prove at minimum:

- concurrent independent clients share the same counter;
- total success count never exceeds configured limit;
- denied clients receive stable rate-limit metadata;
- after window rollover the quota resets correctly;
- forged client-IP headers cannot create arbitrary trusted keys;
- one process/client restart does not reset durable quota.

Do not claim production-scale load proof from tiny fixtures. Record what local CI proves and what remains for staging/Production UAT.

---

## J. CI wiring

S08-002 acceptance requires exact-SHA automated evidence.

Wire focused SQL/Web tests into Integration CI so a new test file cannot exist without executing.

Final candidate/integration verification must include:

- dependency install/audit;
- lint;
- typecheck;
- production build;
- affected Web tests;
- clean local Supabase start/reset/replay;
- S08-002 SQL contract tests;
- concurrency/distributed limiter tests;
- accepted S08-001 SQL tests;
- directly affected predecessor regressions;
- DB lint;
- `python project_control/validate_control_plane.py`;
- `python project_control/validate_omp_native.py`;
- exact-SHA Integration CI PASS;
- exact-SHA Governance CI PASS.

Any CI-only wiring repair after an implementation review is still an implementation delta and must receive independent re-review before acceptance.

---

## K. Explicit non-goals / contracts not reopened

Do **not** implement or redesign in TASK-S08-002:

- S08-001 Name/Email/Phone normalization, indexes, grouped pagination, page-size, debounce or latest-Submission semantics;
- Candidate DTO/business rules, privacy strong-current behavior, optimistic locking, Submission status derivation or Candidate identity recovery;
- upload malware scanner provider/runtime, scan fencing, storage cleanup worker or reservation lifecycle semantics;
- email template/preview fencing, Outbox identity, Email History retention, provider sender runtime or retry/backoff algorithm;
- Interview scheduling/resource-conflict logic;
- Report status/final-decision logic;
- a PDF generation product endpoint/template;
- production scheduler/daemon;
- archive/purge/retention redesign;
- backup/restore implementation;
- Production UAT sign-off;
- global accessibility recertification;
- Vercel deployment/environment mutation;
- connected/hosted Supabase migration application;
- production secret creation/use;
- `main` mutation.

Do not materialize a subsequent TASK-S08-003 during this lifecycle.

---

## L. Producer / reviewer boundaries

ChatGPT/EXTERNAL_CHATGPT is producer/executor/coordinator.

OMP/`eiu-reviewer` is independent prompt/implementation/final reviewer and must not implement or repair its own findings.

Lifecycle after prompt PASS and explicit Owner dispatch:

`ChatGPT implementation → ChatGPT self-audit → OMP exact-SHA implementation review → ChatGPT repair findings → OMP re-review → serialized integration → exact-SHA CI → final acceptance review → immutable accepted checkpoint`

A prompt-review PASS authorizes only readiness for explicit Owner implementation dispatch. It does not itself authorize implementation.
