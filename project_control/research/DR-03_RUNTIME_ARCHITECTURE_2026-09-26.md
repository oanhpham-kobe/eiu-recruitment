# DR-03 — Runtime Architecture: Sound Boundaries vs Accidental Duplication

Status: IN PROGRESS
Research date: 2026-09-26
Evidence baseline: `8dcb0a5d7ce1be9d82e3448c01cdc1643e3ac8c4`
Parent index: `project_control/research/REPO_DEEP_RESEARCH_2026-09-26.md`
Research mode: read/diagnose only; no runtime implementation mutation.

## Work breakdown

- [x] DR-03A — map request/read/write boundaries for Candidate, HR Application, Interview and Report flows.
- [ ] DR-03B — inspect authorization/validation/RPC/RLS overlap and classify KEEP vs SIMPLIFY candidates.
- [ ] DR-03C — inspect cross-cutting infrastructure abstractions and identify real architecture risks versus ordinary refactor debt.

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

Important architectural nuance: this generic runner is used by some command families (for example Application lifecycle), but newer/other domains also implement domain-local equivalents. DR-03B will determine whether this is justified specialization or avoidable duplication.

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

Classification: **KEEP trust/transaction boundary; inspect duplication in DR-03B.** Interview implements its own actor/permission/validation/RPC wrapper instead of the generic command runner.

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

Classification: **KEEP server/RPC boundary; inspect permission granularity and duplicated command plumbing in DR-03B.**

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

### DR-03A debt signals to inspect next

Not yet classified as defects:

1. Multiple command frameworks/patterns coexist:
   - generic `createCommandRunner` + `TrustedCommandDefinition`;
   - Interview-local `actorContext` / `authorized` / `withPermission` / `executeRpc`;
   - Reports-local `authorizedClient` / validators / `normalizeCommandResponse`;
   - other command families may use additional patterns.
2. Permission checking occurs in UI capability calculation, server adapters, command adapters, RPCs and RLS. Some is necessary defense in depth; some may be semantic duplication.
3. Read adapters can become large because they own filtering, query composition and projection shaping.
4. Server Action files sometimes contain substantial read/workflow orchestration rather than being uniformly thin.

These are DR-03B questions, not rewrite evidence.

## Next checkpoint

`DR-03B — authorization/validation/RPC/RLS overlap`

Questions:

- Which checks are security boundaries versus UI convenience?
- Are permissions expressed consistently across Application, Interview and Report domains?
- Do domain-local command wrappers materially diverge in error handling/auth semantics?
- Can shared plumbing be simplified without moving business invariants out of PostgreSQL?
- Are there concrete missing checks, not merely duplicated checks?
