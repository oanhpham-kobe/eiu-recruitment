# TASK-S08-002 — Source Reconciliation v1

WORK_ID: S08-002-SOURCE-RECONCILIATION-001

PRODUCER: EXTERNAL_CHATGPT

BASELINE_SHA: 8dcb0a5d7ce1be9d82e3448c01cdc1643e3ac8c4

PREDECESSOR_ACCEPTED_TASK: TASK-S08-001

PREDECESSOR_ACCEPTED_CHECKPOINT: checkpoint/S08-001-accepted-001

PREDECESSOR_ACCEPTED_SHA: 0d8c5c2129ed4c78a58c8d37bd22e93c14a763eb

PROPOSED_TASK: TASK-S08-002 — Durable Distributed Rate Limiting and Abuse Controls

RESULT: PASS

SOURCE_REOPEN_REQUIRED: false

TASK_MATERIALIZED: false

IMPLEMENTATION_AUTHORIZED: false

---

## 1. Purpose and governance state

This reconciliation determines the canonical source contract and accepted-tree delta for the next Slice-08 candidate after accepted TASK-S08-001. It is a producer-authored planning artifact only.

It does **not**:
- add TASK-S08-002 to `TASK_REGISTRY.yaml` or any execution DAG;
- create an implementation branch;
- create an implementation prompt;
- authorize implementation;
- mutate product code, migrations, tests, Vercel, connected/hosted Supabase, production secrets, or `main`;
- move `checkpoint/S08-001-accepted-001`.

TASK-S08-002 remains NOT MATERIALIZED until this source reconciliation and its later governed prompt/source review lifecycle are separately accepted.

---

## 2. Canonical source authorities

Primary authority:
- `recruitment_webapp/review_pack/68_RATE_LIMIT_POLICY.md`

Supporting frozen/current authorities:
- `recruitment_webapp/review_pack/38_NON_FUNCTIONAL_REQUIREMENTS.md`
- `recruitment_webapp/review_pack/67_WEB_SECURITY_BASELINE.md`
- `recruitment_webapp/review_pack/47_AUDIT_LOGGING_SPEC.md`
- `recruitment_webapp/review_pack/37_BACKEND_COMMAND_CONTRACTS.md`
- `recruitment_webapp/review_pack/55_COMMAND_COVERAGE_MATRIX.md`
- `recruitment_webapp/review_pack/63_BATCH_OPERATION_SEMANTICS.md`
- `recruitment_webapp/review_pack/100_TECHNICAL_PRECODE_GATE_V1_18.md`

Accepted predecessor/source sequencing evidence:
- `project_control/reviews/S08_001_SOURCE_RECONCILIATION_v2.md`

The predecessor reconciliation explicitly separates durable multi-instance rate limiting from S08-001 and identifies it as the next distinct hardening domain.

---

## 3. Canonical rate-limit contract

`68_RATE_LIMIT_POLICY.md` defines initial defaults as configuration, not immutable business rules. The initial enforced matrix is:

| Action | Primary key | Secondary key | Initial default | Required response |
|---|---|---|---|---|
| Candidate OTP request | normalized email | trusted client IP | 5 / 15 min per email; 20 / 15 min per IP | 429 + Retry-After |
| OTP verify | auth/session/email identity | trusted client IP | 10 / 15 min identity; 50 / 15 min IP | 429 + Retry-After |
| Candidate Submit | candidate_id | trusted client IP | 5 / hour; 20 / day | 429 |
| Candidate Update Save | candidate_id | trusted client IP | 30 / 15 min | 429 + Retry-After |
| Upload reserve/completion-finalization boundary | candidate/app_user | trusted client IP | 30 / 15 min identity; 100 / 15 min IP | 429 |
| Internal search | app_user_id | none | 120 / min | 429 |
| Manual/system email enqueue | app_user_id + email_type | exact business entity | 60 / hour; burst 10 / min | 429 |
| PDF generation | app_user_id | exact entity | 20 / hour | 429 |

Canonical implementation rules:
1. Counter state MUST be durable/shared across multi-instance Vercel execution; process-local/in-memory-only counters are forbidden.
2. Counter consumption MUST be atomic under concurrency and must not allow overshoot caused by racing application instances.
3. Trusted client IP MUST come only from explicitly approved platform/proxy semantics. Arbitrary client-controlled forwarding headers MUST NOT be accepted as authority.
4. Rate limiting is additive defense. It MUST NOT replace authentication, RLS, permission checks, trusted-command validation, optimistic locking, idempotency, or same-origin enforcement.
5. Where the upstream auth/provider applies a stricter bound, the effective bound is the stricter one.
6. Repeated abuse/blocks require data-minimized Security Audit evidence without OTPs, tokens, raw file contents, signed URLs, unnecessary PII search terms, or other secrets.
7. Staging/CI evidence must cover burst behavior, distributed-instance behavior, concurrency, and forged-header/bypass attempts.
8. A rate-limited business mutation is rejected before the protected mutation starts. No partial business write is allowed.

---

## 4. Accepted-tree inspection at baseline

Baseline inspected: `8dcb0a5d7ce1be9d82e3448c01cdc1643e3ac8c4`.

### 4.1 Shared limiter primitive

Accepted tree has no shared durable rate-limit primitive in `web/src/lib/security`; current security helpers contain origin/cache concerns but no durable multi-instance counter or trusted client-IP resolver.

GAP-S08-002-01: No reusable durable atomic limiter + trusted-IP abstraction exists.

### 4.2 Candidate OTP request

Current `web/src/app/login/page.tsx` performs Candidate OTP request directly in the browser through `supabase.auth.signInWithOtp(...)`.

Consequence: the application currently has no trusted server boundary at which it can resolve a platform-trusted client IP and atomically enforce the canonical normalized-email + IP limits before the provider call.

GAP-S08-002-02: Candidate OTP request must move behind an application-controlled same-origin server boundary before provider dispatch. Existing Candidate OTP user experience and provider semantics remain otherwise unchanged.

### 4.3 Candidate OTP verify

Current `web/src/app/auth/candidate/verify/route.ts` already:
- rejects invalid same-origin requests;
- parses email/token server-side;
- calls Supabase `verifyOtp`;
- provisions Candidate identity after successful verification.

It does not currently enforce the canonical identity + trusted-IP limiter or `Retry-After` response.

GAP-S08-002-03: Add limiter enforcement before OTP verification without weakening same-origin validation, provider verification, candidate provisioning, or session behavior.

### 4.4 Candidate Submit and Candidate Update Save

`web/src/lib/commands/candidate-submission.ts` already supplies trusted, server-only Submit/Update commands with actor re-resolution, payload validation, RPC business transactions, optimistic/idempotent behavior, privacy checks, document finalization, notification side effects, and audit semantics from the accepted backend contract.

No separate rate-limit stage is present.

GAP-S08-002-04:
- Candidate Submit must enforce 5/hour and 20/day by candidate identity before business mutation.
- Candidate Update Save must enforce 30/15 min by candidate identity before business mutation and return 429 + Retry-After when blocked.
- A blocked Save/Submit commits no partial Submission/document/privacy/outbox mutation.
- Existing trusted-command validation/RLS/idempotency/version semantics are not reopened.

### 4.5 Candidate upload reserve and completion/staging

Accepted Candidate server actions expose distinct user-facing boundaries:
- `reserveUploadAction(...)` → durable upload reservation + signed upload URL;
- `completeAndStageUploadAction(...)` → authorization + trusted private-storage inspection + durable scan request, leading later to staged document state.

The later scan worker/result continuation and cleanup paths are internal/background operations. Candidate Submit/Update subsequently finalize CLEAN staged documents atomically as part of their own business transaction.

GAP-S08-002-05:
- Apply the upload 30/15 min identity + 100/15 min IP policy to user-initiated reserve and completion/staging boundaries.
- Do not rate-limit or double-charge internal scanner claim/result, CLEAN continuation, cleanup workers, or document binding that occurs inside an already rate-governed Submit/Update transaction.
- Existing malware/fencing/reservation-expiry/storage contracts remain authoritative.

### 4.6 Internal search

Accepted internal read surfaces include free-text server-side search, including at least:
- Application Inbox through `queryApplicationInbox(...)` / accepted S08-001 read contract;
- Interview/Application grouped search in `web/src/lib/interview/server.ts`;
- HR Report filters containing free-text `search` in `web/src/lib/reports/hr-model.ts` / report server read path.

No shared 120/min per-app_user limiter is present at those accepted read entry points.

GAP-S08-002-06:
- Enforce 120/min by authenticated internal `app_user_id` on current internal free-text search entry points.
- The limiter key/audit/log path MUST NOT include the user-entered PII search string.
- S08-001 indexing, Candidate-group pagination, page-size, debounce, minimum-name-query and PII request-transport contracts are not reopened.
- Prompt review must enumerate every current accepted internal free-text search server entry point at the pinned baseline so the generic source policy is not applied to only one page.

### 4.7 Manual/system email enqueue

Accepted email commands already implement preview fencing, exact business context, idempotency, outbox persistence, single enqueue and `bulk_enqueue_email` with per-item result semantics.

No canonical 60/hour + 10/min burst limiter is currently enforced in the inspected server command wrapper.

`63_BATCH_OPERATION_SEMANTICS.md` defines Bulk Email as `PER_ITEM_ENQUEUE_RESULT`; `68_RATE_LIMIT_POLICY.md` defines the secondary key as exact entity. Reconciliation therefore resolves rate accounting as **per enqueue item/entity**, not one counter unit for an entire bulk request. A bulk request may return a mixture of success/failed item results consistent with the existing batch contract.

GAP-S08-002-07:
- Apply the enqueue limiter to each single enqueue and each item in bulk enqueue using authenticated app_user + email_type and the exact entity dimension.
- Preserve current per-item bulk result contract and max batch bound.
- Queue-side rate limiting is distinct from asynchronous provider delivery throttling.
- Candidate Submit/Update's required system HR notification remains an atomic accepted business side effect. Provider delivery throttling after commit MUST NOT roll back a valid Candidate Save/Submit. The implementation prompt must preserve this distinction and must not introduce a non-transactional notification gap.

### 4.8 PDF generation

The canonical rate policy requires 20/hour by app_user + entity for PDF generation. The accepted runtime baseline inspected for `/reports` contains report read/write actions but no implemented PDF generation route/action.

RECONCILIATION-S08-002-PDF:
- Do not invent a new PDF generation business feature solely to satisfy the rate-limit policy.
- The reusable limiter contract produced by this task must be capable of supporting the canonical PDF policy later.
- The first real PDF-generation endpoint must consume that policy before generation as part of its own governed implementation lifecycle.
- Official PDF/template/UAT work remains outside this task.

### 4.9 Interview upload commands

Canonical command coverage also defines explicit internal-user Interview upload boundaries `reserve_interview_upload` and `finalize_interview_upload`. Because the rate policy keys upload by `candidate/app_user`, the implementation prompt must verify whether these accepted internal upload commands are reachable in the pinned implementation baseline and, if reachable, include their user-facing reserve/finalize boundaries under the same upload policy. Internal scan/cleanup worker operations are not counted as interactive upload requests.

GAP-S08-002-08: Prompt/source review must prove complete coverage of all currently reachable Candidate and app_user upload reserve/finalize entry points rather than protecting Candidate upload only.

---

## 5. Architecture constraints for the later implementation prompt

This reconciliation intentionally does not freeze a vendor-specific limiter implementation, but the implementation MUST satisfy all of the following:

1. **Durable and multi-instance:** shared state survives/reconciles independent Vercel instances. A module-global `Map`, memory cache, per-process token bucket, or equivalent is non-compliant.
2. **Atomic consumption:** concurrent requests against one key/window cannot both pass beyond the configured limit due to races.
3. **Existing platform first:** a Supabase/Postgres-backed primitive is compatible with the current architecture and disposable local CI, but the later prompt may choose another provider-native durable mechanism only if it introduces no hidden deployment/security dependency and receives independent review.
4. **No hosted mutation during development/review:** database work is forward-only migration + disposable local Supabase/CI only. Connected/hosted Supabase mutation remains prohibited.
5. **Private limiter state:** counter/storage primitives are not directly client-readable or client-writable. Browser code cannot choose trusted limiter identity/IP keys.
6. **Trusted IP resolution:** platform/proxy header acceptance is explicit and allowlisted; generic user-supplied forwarding chains are not blindly trusted. Negative forged-header tests are mandatory.
7. **Configurable defaults:** policy values are configuration with canonical initial defaults. Do not hard-code them as irreversible business invariants.
8. **Bounded state:** counter data requires bounded window/expiry/cleanup behavior so abuse protection does not create unbounded permanent operational data.
9. **PII/security minimization:** never use OTP token, raw search query, access/refresh token, signed URL/token, file content, or service secret as counter/audit payload. Required email/IP identity dimensions must be stored/derived only to the minimum necessary extent for enforcement and must not become general-purpose logs.
10. **Stable rejection contract:** blocked requests return a stable rate-limit code/status; `Retry-After` is present wherever required by canonical policy and is derived from the authoritative active window, not a guessed constant.
11. **Auth/RLS first-class:** limiting does not grant access. Existing auth, same-origin, RLS, permissions and trusted-command checks remain independently enforced.
12. **Mutation ordering:** limiter decision is obtained before protected mutation/provider dispatch. A denied mutation makes zero protected business changes.

---

## 6. Verification contract for the later implementation prompt

At minimum, automated evidence must prove:

1. Exact initial limit/window behavior for every materialized policy action.
2. `Retry-After` correctness for OTP request, OTP verify and Candidate Update Save; stable 429 behavior for all policy actions.
3. Email primary + secondary key behavior and both 60/hour and 10/min burst limits.
4. Bulk email rate accounting per enqueue item/entity while preserving `success[]` / `failed[]` semantics.
5. Candidate Submit 5/hour + 20/day and Candidate Update 30/15 min are distinct policies.
6. Upload identity + IP combined limits on user-facing reserve/completion/finalize boundaries, without charging worker/cleanup continuations.
7. Internal search 120/min per app_user across every reachable accepted free-text internal-search entry point; query text absent from URLs, limiter state, logs and Security Audit metadata.
8. Atomic concurrent counter consumption with no over-limit race success.
9. Multi-instance simulation using independent application/database clients/processes against one durable backend state.
10. Window expiry/reset boundary behavior and safe cleanup/expiry behavior.
11. Forged/unapproved forwarding headers cannot select or bypass the trusted client-IP key; approved platform semantics are tested separately.
12. Rate limiting does not bypass or replace existing same-origin/auth/RLS/permission checks.
13. Blocked Submit/Update/upload/email mutations leave protected business state unchanged.
14. OTP request is app-server mediated before provider dispatch; no OTP token or sensitive auth data is logged.
15. Provider-native stricter OTP rejection remains effective and is not masked by application-side limits.
16. Existing S08-001 Application Inbox regressions remain green.
17. Existing Candidate Submission/Upload/Email/Interview regression suites remain green.
18. Database replay from zero and DB lint pass for any new migration.
19. Web lint/typecheck/build and relevant security tests pass.
20. Control-plane validators pass after any eventual task materialization/integration.

---

## 7. Explicit non-goals / contracts not reopened

TASK-S08-002 must not reopen or redesign:
- S08-001 search normalization/indexes/grouped pagination/page-size/debounce/latest-Submission semantics;
- Candidate business DTOs, privacy strong-current checks, optimistic versioning, idempotency, Submission status derivation, or Candidate identity rules;
- upload malware scanning, scan fencing, storage cleanup fencing, reservation expiry or signed-URL security;
- email preview fencing, outbox identity, idempotency, history retention, worker delivery retry/backoff or provider-runtime implementation;
- Interview scheduling/resource conflict semantics;
- Report lifecycle/status/final-decision semantics;
- PDF generation/template product implementation;
- production deployment, Vercel environment mutation, hosted/connected Supabase mutation, production secrets, or `main`.

---

## 8. Source reconciliation findings

### Blocking findings

NONE.

### Reconciled ambiguities

1. **Bulk email accounting** — resolved from `63_BATCH_OPERATION_SEMANTICS.md` + `68_RATE_LIMIT_POLICY.md`: each enqueue item/entity is independently rate-accounted; a bulk transport call is not one universal rate unit. Existing `PER_ITEM_ENQUEUE_RESULT` remains authoritative.
2. **Candidate upload finalize wording** — resolved against accepted server actions/backend command lifecycle: user-facing upload reserve plus completion/staging are upload-rate boundaries; later CLEAN scan continuation and Submit/Update document binding are not separately double-charged. Candidate Submit/Update retain their own dedicated mutation limits.
3. **PDF policy vs runtime** — policy obligation is canonical, but no accepted runtime PDF generation endpoint exists at this baseline. Endpoint implementation is deferred; reusable limiter capability remains required.
4. **Generic internal search** — applies to all current authenticated internal free-text search entry points, not only Application Inbox. Exact endpoint enumeration is mandatory in the future prompt review against its pinned baseline.
5. **Interview upload reachability** — command-source contract includes app_user reserve/finalize. Future prompt review must verify accepted implementation reachability and include all reachable user-facing upload endpoints; no worker/cleanup operations are to be counted as interactive upload requests.

No owner/business decision is required by these reconciliations.

---

## 9. Recommended task boundary

Proposed future materialized task:

`TASK-S08-002 — Durable Distributed Rate Limiting and Abuse Controls`

Recommended implementation boundary:
- reusable durable atomic rate-limit primitive;
- trusted client-IP resolver;
- app-server OTP request boundary + OTP verify enforcement;
- Candidate Submit/Update enforcement;
- reachable Candidate/app_user upload reserve/finalize enforcement;
- all reachable internal free-text search enforcement;
- single/bulk email enqueue enforcement;
- data-minimized abuse-block auditing;
- deterministic concurrency/distributed/forged-header tests;
- reusable registered policy support for future PDF generation without implementing PDF generation itself.

This is a source-reconciled candidate only. It is not yet in the task DAG and carries no implementation authorization.

---

## 10. Exit statement

`S08-002-SOURCE-RECONCILIATION-001` is PASS at exact inspected baseline `8dcb0a5d7ce1be9d82e3448c01cdc1643e3ac8c4`.

SOURCE_REOPEN_REQUIRED: false

TASK_MATERIALIZED: false

IMPLEMENTATION_AUTHORIZED: false

Next valid gate: independent source-reconciliation review of this exact artifact/baseline. Only after independent PASS may the producer materialize the governed task/prompt review lifecycle. Implementation remains forbidden until a later exact prompt/source review PASS and explicit Owner/authorized dispatch under the active governance model.
