# DR-03 — Runtime Architecture: Sound Boundaries vs Accidental Duplication

Status: COMPLETE
Research date: 2026-09-26
Evidence baseline: `8dcb0a5d7ce1be9d82e3448c01cdc1643e3ac8c4`
Parent index: `project_control/research/REPO_DEEP_RESEARCH_2026-09-26.md`
Research mode: read/diagnose only; no runtime implementation mutation.

## Work breakdown

- [x] DR-03A — map request/read/write boundaries for Candidate, HR Application, Interview and Report flows.
- [x] DR-03B — inspect authorization/validation/RPC/RLS overlap and classify KEEP vs SIMPLIFY candidates.
- [x] DR-03C — inspect cross-cutting infrastructure abstractions and identify real architecture risks versus ordinary refactor debt.

## DR-03A — Runtime boundary map

### Executive finding

The runtime is not a client-direct-to-database application. The dominant architecture is deliberate:

```text
React UI
  -> Next.js Server Action / Server Component
    -> read adapter OR trusted-command/domain adapter
      -> authenticated Supabase server client
        -> table/RLS read OR atomic trusted RPC mutation
          -> PostgreSQL constraints / transaction / concurrency rules
```

This separation is broadly sound and should be preserved unless later evidence shows a concrete security or consistency defect.

### Cross-cutting command runner

`web/src/lib/commands/runner.ts` is `server-only` and defines a reusable trusted-command pipeline:

1. resolve verified actor;
2. reject unauthenticated actor;
3. reject inactive actor;
4. extract command target;
5. authorize actor/target;
6. validate raw input;
7. execute command;
8. normalize command result;
9. map known command errors and hide/log unexpected errors.

This is a coherent application-layer policy boundary, not presentation logic.

Important architectural nuance: this generic runner is used by some command families (for example Application lifecycle), but newer/other domains also implement domain-local equivalents. DR-03B determines whether this is justified specialization or avoidable duplication.

### Candidate flow

Representative path:

```text
/candidate client page
  -> candidate-actions.ts ("use server")
    -> auth/provisioning + direct RLS-protected reads
    -> command adapters for session/submission/upload mutations
      -> RPC/storage trusted contracts
```

`candidate-actions.ts` directly performs read-oriented queries for privacy notice, document types, qualification levels, submissions and resumable session/edit data using the authenticated server client.

Mutating workflows are routed to dedicated command modules such as:

- `candidate-submission.ts`;
- `form-session.ts`;
- `storage-reservation.ts`;
- candidate identity provisioning/auth helpers.

Candidate upload handling also separates reservation/scan contract operations from scanner/provider abstraction.

Classification: **KEEP boundary shape.** The server-action file is large and mixes read orchestration with workflow transport, but the trust boundary itself is reasonable.

### HR Application Inbox flow

Representative path:

```text
/ page / ApplicationInboxTable
  -> application-inbox-actions.ts
    -> application-inbox/server.ts + submission-detail-server.ts for reads
    -> command modules for lifecycle/status mutations
      -> trusted RPC/database contract
```

`application-inbox-actions.ts` is primarily a transport/error-mapping layer. It delegates:

- inbox reads to `loadApplicationInbox`;
- submission detail, assignment options, signed document URL behavior to submission-detail server adapters;
- Application creation/update to `application-lifecycle.ts`;
- Candidate activity changes to `candidate-lifecycle.ts`;
- bulk/manual submission status to `submission-status.ts`.

`application-lifecycle.ts` uses the generic `createCommandRunner` / `TrustedCommandDefinition` model. Authorization and input validation are explicit before the RPC invocation.

Classification: **KEEP overall architecture.** This is the cleanest example of the intended typed trusted-command boundary.

### Interview flow

Representative path:

```text
/interviews page / InterviewPage client component
  -> interviews/actions.ts
    -> interview/server.ts for page/search/options reads
    -> interview-lifecycle.ts + email/application commands for writes
      -> trusted RPCs
```

`interviews/actions.ts` mainly exposes server-callable transport methods and revalidates `/interviews` after successful mutations.

`interview/server.ts`:

- is `server-only`;
- resolves the server session;
- requires an internal user and `interviews.view`/Root Admin;
- normalizes/sanitizes filters;
- performs authenticated/RLS-aware reads and builds UI permission capabilities.

`interview-lifecycle.ts`:

- is `server-only`;
- resolves internal actor context;
- performs permission checks;
- validates UUID/version/status/idempotency payload shape;
- invokes named PostgreSQL RPCs for atomic interview lifecycle operations;
- maps domain/RPC error codes to safe user-facing messages.

Classification: **KEEP trust/transaction boundary.** Interview implements its own actor/permission/validation/RPC wrapper instead of the generic command runner; the duplication is addressed below as a simplification opportunity.

### Reports flow

Representative path:

```text
/reports page
  -> reports/actions.ts
    -> reports/server.ts or reports/hr-server.ts
      -> authorized server client
        -> report read/mutation RPCs
```

`reports/actions.ts` is thin: load, save/mutate, then `revalidatePath("/reports")` on success.

`hr-server.ts`:

- is `server-only`;
- resolves a session and enforces Root Admin or `reports.view`;
- validates UUID/version/status/patch payload shape;
- uses RPCs for report page reads and report mutations;
- normalizes trusted command responses.

Classification: **KEEP server/RPC boundary.**

### Read-path vs write-path distinction

The repository does not force every server read through RPC. Read adapters sometimes query tables directly using the authenticated Supabase server client and depend on RLS plus application-level capability checks.

Writes with business invariants, concurrency/version semantics, idempotency or multi-row effects are generally pushed into trusted RPC/database contracts.

That split is architecturally sensible for this Supabase/PostgreSQL system:

- read composition can remain in server adapters where RLS protects row access;
- transactional business mutations remain database-authoritative;
- browser code does not receive privileged service-role credentials.

### DR-03A KEEP map

KEEP unless contradicted by later evidence:

- server-only separation for trusted backend code;
- authenticated Supabase server client for user-context reads;
- RLS as database read/write backstop;
- explicit application-layer permission checks for user experience and fail-fast behavior;
- trusted RPCs for atomic/versioned/idempotent business mutations;
- Server Actions as UI transport boundary;
- safe error normalization rather than exposing raw database failures.

## DR-03B — Authorization / validation / RPC / RLS overlap

Status: COMPLETE

### Executive conclusion

The repeated permission checks are **mostly legitimate defense in depth**, not evidence that authorization should be collapsed into one layer. The database RPC/RLS layer is the security authority; application-layer checks provide fail-fast behavior and UI capability shaping.

The simplification opportunity is narrower: **standardize duplicated command plumbing and permission-capability propagation while preserving database-authoritative business/security invariants.**

### 1. Interview mutation path — aligned multi-layer authorization

Representative operation: change interview schedule status.

Application/domain adapter:

- validates interview UUID/version/status;
- requires `interviews.status` **and** `interviews.view` unless Root Admin;
- calls the RPC.

Database RPC `change_interview_schedule_status` independently:

- resolves an active actor using `private.interview_command_actor('interviews.status')`;
- separately requires `interviews.view` unless Root Admin;
- validates target status;
- performs row/version/state checks under database transaction semantics.

Representative save-schedule operation similarly requires `interviews.manage` in both the application adapter and database command.

Classification: **KEEP.** The second database check protects direct RPC callers and future application drift; the application check improves error locality and UI behavior.

### 2. Interview read path — RLS remains a necessary backstop

The server read adapter requires an internal user and `interviews.view`/Root Admin before constructing the page query.

At the database level, report/document RLS policies separately restrict authenticated reads using permission/root checks and interviewer-scoped predicates. Email history RLS also combines `emails.history_view` with the relevant Interview/Application/Submission permissions.

Classification: **KEEP.** Read-adapter checks and RLS serve different trust boundaries. Removing RLS because the Next.js server already checks permissions would materially weaken the system.

### 3. HR Report capabilities — coarse server gate + fine database capabilities

`hr-server.ts` uses a coarse `reports.view`/Root Admin gate to obtain an authorized user-context client. It does not re-implement every fine-grained mutation permission in each TypeScript function.

The HR Report read RPC computes and returns explicit capabilities:

- `reports.manage_status`;
- `reports.visibility`;
- `reports.edit_interviewer`;
- `reports.delete`.

The React view consumes those capabilities to block/hide status, visibility, interviewer-edit and delete operations before invocation.

The mutation RPCs independently enforce their fine-grained permissions. Examples verified:

- report status / HR report note: `reports.manage_status` plus `reports.view`;
- visibility: `reports.visibility` plus `reports.view`;
- HR edit of interviewer report: `reports.edit_interviewer` plus `reports.view` (with a separate own-interviewer path where allowed);
- report delete/inactivate: `reports.delete` plus `reports.view`.

Classification: **KEEP security model.** The coarse TypeScript gate is not a privilege-escalation defect because the database command remains authoritative and the UI capability model prevents expected users from invoking unavailable operations.

### 4. Application lifecycle — application check can be stricter than DB command

Representative `create_or_update_application`:

- TypeScript command definition requires `submissions.view` plus `applications.create` or `applications.manage` (Root Admin bypass);
- the database RPC independently requires `applications.create` or `applications.manage` (or Root Admin) and validates active hierarchy/owner/duplicate/locking rules.

This is not a security weakening: the application layer is stricter than the DB permission check. It does, however, demonstrate that permission policy is partly duplicated in two representations and therefore can drift semantically.

Classification: **KEEP DB authority; REVIEW/ALIGN policy expression.** Do not mechanically force equality if the extra `submissions.view` is an intentional UX/business precondition. Document or test intentional differences so future reviewers can distinguish policy from accidental drift.

### 5. Validation duplication — shape checks vs business invariants

The TypeScript command layer commonly validates cheap request-shape concerns such as:

- UUID syntax;
- positive version values;
- allowed enum/status values;
- array bounds/duplicates;
- required paired fields.

The database command then rechecks security-critical/domain-state invariants such as:

- active target/actor state;
- optimistic version equality;
- latest-round/current-round requirements;
- hierarchy consistency;
- scheduling conflicts;
- duplicate/idempotency semantics;
- row locking and transaction order;
- dependent lifecycle behavior and audit logging.

Some basic validation is repeated in SQL, which is appropriate because RPCs are directly executable by authenticated clients subject to grants.

Classification: **KEEP the split.** Do not move transactional/domain invariants upward merely to reduce apparent duplication.

### 6. Real maintainability debt — three command plumbing styles

There is a concrete consistency cost in the application layer:

**Application-style**
- generic `createCommandRunner`;
- `TrustedCommandDefinition`;
- standard actor/active/authorize/validate/execute/result behavior.

**Interview-style**
- local `actorContext`;
- local `authorized`/`withPermission`;
- local `executeRpc`;
- local safe-message mapping.

**HR Report-style**
- local `authorizedClient`;
- local validators;
- local `normalizeCommandResponse`;
- capability information supplied by the page RPC.

All three are workable, but each independently solves authentication, validation, RPC result normalization and error mapping. That increases the probability of inconsistent inactive-user handling, error codes, logging and permission prechecks.

Classification: **SIMPLIFY, not rewrite.** A shared thin infrastructure primitive can standardize actor resolution, coarse authorization, RPC response normalization and safe error mapping while leaving domain-specific permission sets, payload validation and SQL business rules in their domains.

### 7. Capability authority should remain database-derived where state/policy is DB-owned

HR Report demonstrates a strong pattern: the database projection returns capabilities derived from the same permission authority the mutation RPCs use, and the UI consumes them.

Interview currently reconstructs capability booleans in the server adapter from session permissions. This is acceptable, but creates another duplicated policy representation.

Potential simplification direction for DR-07:

- keep server-rendered capability objects for UX;
- prefer a single canonical permission mapping per domain;
- add contract tests proving UI/server capability gates match RPC permission expectations;
- avoid making React components or route files the policy authority.

### 8. No evidence supporting removal of RLS or trusted RPC authorization

Nothing in DR-03B supports any of these changes:

- disabling RLS because Next.js is server-side;
- using service-role for ordinary user workflows;
- trusting hidden/disabled UI controls as authorization;
- moving concurrency/version checks out of PostgreSQL;
- exposing direct table DML in place of trusted command RPCs.

Those would reduce security/correctness without addressing the actual maintainability issue.

### DR-03B KEEP / SIMPLIFY classification

**KEEP**

- DB-authoritative permission checks for trusted RPCs;
- RLS for user-context table reads;
- active-user verification at trusted command boundaries;
- optimistic version / locking / current-round / hierarchy / conflict rules in SQL;
- UI/server capability gates as UX/fail-fast controls;
- cheap payload-shape validation before RPC invocation.

**SIMPLIFY / STANDARDIZE**

- repeated TypeScript actor/session-resolution plumbing;
- repeated RPC response normalization;
- repeated safe-error mapping/logging infrastructure;
- undocumented differences between application permission prechecks and DB permission requirements;
- capability-policy duplication where one domain can expose a canonical capability contract.

**NOT A VERIFIED SECURITY DEFECT**

- HR Report TypeScript mutation functions using a coarse `reports.view` authorized client. Fine-grained authorization remains enforced by both DB-returned UI capabilities and the mutation RPCs themselves.

## DR-03C — Cross-cutting infrastructure and actual architecture risks

Status: COMPLETE

### 1. Service-role / admin client boundary — broadly sound, keep narrow

`web/src/lib/supabase/admin.ts` is `server-only`; the service-role key is read only by `web/src/lib/env/server.ts`, also `server-only`. The ordinary server client remains a user-context client, while admin access is explicitly opt-in through `createAdminClient()`.

The repository also has a build/client-bundle test that scans `.next/static` for service-role secret identifiers.

Verified production-oriented admin uses include operations that genuinely require privileged storage/service behavior, such as:

- inspecting a private/quarantine upload after a user-context authorization step;
- recording trusted upload inspection metadata;
- generating a short-lived storage signed URL only after authenticated `submissions.view` authorization and a fail-closed document-access audit RPC.

The document preview route streams bytes server-side instead of returning the signed storage URL to the browser.

Classification: **KEEP.** No evidence was found of ordinary HR/Candidate business mutations being performed wholesale through service-role.

Maintainability guard: the generic `createAdminClient()` primitive is powerful. Prefer continuing to wrap it behind narrow provider/operation functions rather than increasing direct admin-client call sites.

### 2. Upload inspection and malware scanning are intentionally separate contracts

`upload-scanner.ts` performs trusted **content inspection**, not malware adjudication. It validates actual byte length, computes SHA-256, detects supported magic signatures/MIME shape and records whether extension/MIME agree.

`completeAndStageUploadAction` explicitly states that the request path does **not** contact a malware scanner or supply a verdict. It records inspection metadata and creates a durable scan request, returning `PENDING_SCAN`. A separate continuation path stages the document only after a CLEAN worker result exists.

Classification: **KEEP architecture boundary.** Do not mislabel magic-byte inspection as antivirus scanning and do not collapse the durable worker boundary into the web request just to simplify code.

Whether a real production scanner/worker/provider is connected is a DR-05 production-readiness question.

### 3. Storage cleanup provider abstraction is appropriately narrow

`StorageCleanupProvider` exposes exact-object removal and normalizes provider errors into timeout/temporary/unavailable categories. It carefully distinguishes an authoritative missing object from bucket missing/permission/generic errors rather than treating every 404 as success.

Classification: **KEEP.** This is a good example of a provider boundary that isolates external-service semantics without creating a general repository abstraction layer.

### 4. Security headers / browser boundary — strong baseline

Middleware applies a nonce-based CSP and headers including:

- `default-src 'self'`;
- nonce/strict-dynamic scripts;
- no objects;
- no framing (`frame-ancestors 'none'`, `X-Frame-Options: DENY`);
- same-origin forms/base;
- `nosniff`;
- restrictive referrer policy;
- camera/microphone/geolocation disabled.

The repository also includes focused security-header/CSP browser tests. Sensitive response helpers use `private, no-store`, and the document-preview endpoint adds no-store, `nosniff`, and a sandboxed document CSP.

Classification: **KEEP.** This is not where simplification effort should be spent.

### 5. Same-origin helper exists; no broad origin-bypass finding established

`validateSameOrigin` derives the expected origin from forwarded host/protocol and rejects missing or mismatched Origin/Referer inputs. The repository includes origin tests.

DR-03 did not perform an exhaustive endpoint-by-endpoint CSRF audit, so no claim is made that every state-changing route manually invokes this helper. Next.js Server Actions also have their own framework-level request protections. A dedicated external security review, if desired later, should test behavior rather than infer it from helper presence alone.

### 6. MEDIUM — error/logging hygiene is inconsistent across architecture paths

A redacting logger exists and removes bearer/JWT/signed-URL/credential/OTP patterns plus sensitive-key fields. The generic command runner uses the shared logging path for unexpected errors.

Other paths still use local/raw error handling. In particular, the document preview route returns `error.message` directly in the unexpected `500` response branch. Upstream known document failures are mostly converted to safe domain errors, but an unexpected thrown provider/runtime error can therefore be reflected to the client.

Classification: **HARDEN, not architectural rewrite.** Replace unexpected external response bodies with a fixed safe message/request ID and log the redacted detail server-side. Standardize command/route logging on the shared redaction helper.

This is a verified error-boundary weakness; it is **not** evidence that sensitive data has actually been leaked in production.

### 7. Large UI/read modules are refactorability debt, not trust-boundary failure

At the baseline tree, several workflow files are large:

- `SubmissionDetailDrawer.tsx` ≈ 51.5 KB;
- `HrReportView.tsx` ≈ 44.5 KB;
- `InterviewPage.tsx` ≈ 42.4 KB;
- `ApplicationInboxTable.tsx` ≈ 34.1 KB;
- `interview/server.ts` ≈ 27.7 KB;
- `candidate-actions.ts` ≈ 23.0 KB.

The large components coordinate legitimate workflow state, stale-version refresh, dialogs, drawers, email/document operations and optimistic/dirty-state behavior. Their size increases change-collision and regression risk, but their existence does not invalidate the server/RPC/RLS architecture.

Classification: **SIMPLIFY incrementally.** Extract workflow-specific hooks/subcomponents/adapters when touching those areas; do not create a standalone rewrite project unless measured change cost justifies it.

## DR-03 final architecture verdict

### KEEP

- Next.js server boundary around trusted logic;
- user-context Supabase server client for ordinary reads/mutations;
- PostgreSQL RPCs for transactional business commands;
- RLS as database backstop;
- optimistic version/idempotency/locking rules in SQL;
- narrow service-role operations for trusted storage/worker infrastructure;
- server-side signed-URL streaming and fail-closed document access auditing;
- CSP/security headers and sensitive-cache controls;
- durable worker boundary for scan/cleanup/provider work.

### SIMPLIFY / STANDARDIZE

- three different TypeScript command-plumbing styles;
- actor/session/RPC-result/error-mapping duplication;
- capability-policy representations where contract tests can keep UI and RPC expectations aligned;
- large workflow components and oversized read/action modules, incrementally;
- redacted logging usage across all command/route paths.

### HARDEN

- never reflect unexpected raw `error.message` from API 500 responses;
- prefer narrow privileged providers around service-role use;
- keep intentional permission differences documented/tested to prevent drift.

### REWRITE?

**NO.** The evidence does not justify a framework, data-model or authorization rewrite. The core architecture is coherent and security-conscious. The identified problems are localized consistency/refactor/error-boundary issues that can be repaired while preserving accepted contracts.

## Next research unit

`DR-04 — CI / governance / review lifecycle throughput`

Split into small checkpoints:

- `DR-04A` — quantify representative task lifecycle stages and commit/review churn from Git history/evidence.
- `DR-04B` — inspect CI workflow cost/serialization and distinguish necessary regression protection from repeated full-suite expense.
- `DR-04C` — classify governance controls as KEEP / LIGHTEN / AUTOMATE / REMOVE-DUPLICATION and identify the critical-path bottlenecks.
