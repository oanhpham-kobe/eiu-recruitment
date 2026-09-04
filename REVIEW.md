# REVIEW.md — EIU Recruitment Review Contract

## Purpose

This file defines project-specific review priorities and reject conditions.

Always review against the **current canonical project sources**. This file is a guardrail summary, not a replacement for those sources.

If this file and the current source disagree, the current source wins and this file should be corrected.

---

# 1. Review Priority Order

1. **Current Source Conformance**
2. **Security & Authorization**
3. **Data Integrity & Concurrency**
4. **Privacy & Document Security**
5. **Authentication & Identity**
6. **Database / Migration Safety**
7. **Functional Correctness**
8. **Type / Boundary Safety**
9. **Accessibility & UI Contract**
10. **Performance & Reliability**
11. **Maintainability / Simplicity**
12. **Agent / Tooling Safety**

A lower-priority improvement must never introduce a higher-priority regression.

---

# 2. Current Source Conformance — BLOCKER

Reviewer must verify:

- [ ] Implementation uses the current canonical source, not a remembered/older rule.
- [ ] Entity ownership and relationships match current source.
- [ ] Status transitions/derived outcomes match current source.
- [ ] Permission predicates match current source.
- [ ] Delete/inactive/destructive behavior matches current source.
- [ ] Current-record/current-round/current-source derivations match current source.
- [ ] UI behavior matches current design source.
- [ ] No external skill has silently redesigned approved business logic.

Reject if:

- behavior was invented without source support;
- settled business logic was reopened without an explicit change request;
- stale memory/old docs are treated as more authoritative than current source;
- a generic best practice overrides a project-specific invariant.

---

# 3. Security & Authorization — BLOCKER

## Server-side authorization

Reject if:

- authorization exists only in UI;
- hidden/disabled controls are treated as security;
- a Server Action/Route Handler mutates without authenticating and authorizing;
- client-supplied role/permission/ownership is trusted where it must be server-derived;
- service-role/secret keys reach the browser;
- service-role usage skips caller reauthorization;
- private tables/views/functions are exposed more broadly than required;
- RLS or grants are weakened to make a feature work.

For mutation paths verify:

```text
authenticate
-> authorize
-> validate
-> approved transactional command/RPC
-> stable response/error
```

Browser code must not orchestrate a complex atomic business command through independent writes.

---

# 4. Supabase Security — BLOCKER

For affected Supabase paths verify:

- [ ] `supabase` skill/current Supabase docs were consulted for version-sensitive behavior.
- [ ] Exposed tables use required RLS.
- [ ] Grants and RLS are both reviewed; one does not replace the other.
- [ ] RLS policies include actual ownership/context authorization, not only `TO authenticated`.
- [ ] User-editable metadata is not trusted for authorization.
- [ ] Sensitive views preserve intended RLS/security semantics.
- [ ] `SECURITY DEFINER` is used only when justified.
- [ ] Privileged functions have controlled `search_path` and explicit execute privileges.
- [ ] `PUBLIC` execute privilege is revoked where required.
- [ ] service role / secret key is server-only.
- [ ] Storage policies preserve private document boundaries.

Reject if a permission error is “fixed” by broadly bypassing RLS.

---

# 5. Authentication & Google OAuth — BLOCKER

Primary technical reference:

`https://supabase.com/docs/guides/auth/social-login/auth-google`

## Google provider configuration

Verify:

- [ ] Google OAuth Client ID/Secret are outside source control.
- [ ] Client Secret is never bundled to browser code.
- [ ] Authorized origins match intended environments.
- [ ] Google authorized redirect URI matches the Supabase callback endpoint.
- [ ] Supabase Site URL / redirect allow list is deliberate.
- [ ] preview/staging/production redirects are not accidentally open-ended.
- [ ] OAuth scopes are limited to approved needs.

## SSR / PKCE

Where the current Supabase SSR flow uses PKCE:

- [ ] `signInWithOAuth` uses an approved `redirectTo`.
- [ ] callback exchanges the authorization code for a Supabase session.
- [ ] cookies/session handling uses current `@supabase/ssr` guidance.
- [ ] callback destination cannot become an open redirect.
- [ ] callback errors do not leak tokens/secrets.

## Authentication is not authorization

Critical rule:

> A valid Google/Supabase session does not automatically grant application access.

After auth, verify all current project-defined checks are enforced server-side, including whichever apply:

- allowed identity/domain;
- internal-user allowlist;
- active state;
- account binding;
- role/permission resolution;
- contextual authorization.

Reject browser-only domain/role checks as the sole enforcement.

## Provider tokens

If Google is only used for sign-in:

- do not persist provider access tokens;
- do not persist provider refresh tokens;
- do not request offline access/forced consent unnecessarily.

---

# 6. Data Integrity & Concurrency — BLOCKER

For race-prone commands compare implementation to the exact current concurrency contract.

Reject if:

- validation and write are separated without required locks/recheck;
- resource conflicts are checked outside required deterministic locking;
- stale whole-row writes can overwrite current data;
- required version checks are omitted;
- duplicate prevention exists only in UI;
- sequence allocation lacks required lock/transaction;
- aggregate/derived state is recalculated outside the authoritative transaction;
- retry-prone operations lack required idempotency;
- external provider calls occur inside a DB transaction contrary to current command/outbox design.

Checklist:

- [ ] one transaction maps to one business command where required;
- [ ] lock order is deterministic;
- [ ] state is re-read after locks where required;
- [ ] eligibility/conflict checks use current locked state;
- [ ] idempotency/version tokens are enforced;
- [ ] rollback cannot leave partial business state;
- [ ] concurrency tests cover meaningful competing operations.

---

# 7. SQL / Migration Review — BLOCKER/HIGH

Before approval:

- [ ] `supabase-postgres-best-practices` was used.
- [ ] schema changes are represented in repository migration/schema sources.
- [ ] clean-install/migration ordering remains viable.
- [ ] constraints encode durable invariants when appropriate.
- [ ] indexes support required query/search paths.
- [ ] no unbounded operational query is introduced.
- [ ] destructive change has an explicit recovery/migration plan.
- [ ] transaction/locking semantics match current source.
- [ ] privileged functions/views/grants were security-reviewed.
- [ ] realistic `EXPLAIN` evidence exists for critical performance paths when required.

Reject dashboard-only schema drift that is not represented in version-controlled database sources.

---

# 8. Supabase MCP Safety — BLOCKER

Supabase MCP is a developer tool, not an application dependency.

Reject project tooling configuration if:

- MCP is pointed at production by default;
- project scoping is omitted when a project can be scoped;
- write-capable mode is enabled by default;
- unnecessary feature groups are enabled;
- credentials/tokens are committed;
- live MCP SQL is treated as a replacement for migration files.

Default should be:

- non-production project;
- `project_ref` scoped;
- `read_only=true`;
- minimum feature groups.

Temporary write mode requires explicit task authorization and a non-production target.

---

# 9. Privacy & Private Documents — BLOCKER

Reject if:

- private documents are stored in a public bucket;
- long-lived signed URLs are persisted/logged;
- upload validation is bypassed;
- required scan/finalization state is bypassed;
- one user/context can access another unauthorized user's document;
- sensitive document content is logged;
- raw tokens/session/OTP/provider secrets are logged;
- purge/retention changes are invented outside current source.

Verify:

- [ ] preview/download authorization occurs before access is issued;
- [ ] signed access is short-lived;
- [ ] file type/size/count rules are enforced server-side;
- [ ] staging/finalization follows current contract;
- [ ] abandoned temporary files have a cleanup path.

---

# 10. TypeScript / Boundary Safety — HIGH

Reject:

- unjustified `any`;
- unvalidated untrusted payloads;
- client payloads cast directly into trusted domain types;
- secrets referenced from client components;
- security-sensitive ownership fields accepted from clients when they should be derived server-side;
- empty catch blocks or silently swallowed errors.

Prefer:

- `unknown` + validation/type guards for untrusted data;
- explicit request/response/domain types;
- validation at trust boundaries;
- stable machine-readable error codes;
- separate safe user-facing messages.

Do not add a new validation dependency merely because a generic skill prefers it.

---

# 11. React / Next.js — HIGH

## Version-matched Next.js docs

Do not approve framework-sensitive code written from stale memory when installed-version docs are available.

For modern Next.js, preserve the managed Next.js agent rules in root `AGENTS.md` if generated by the framework.

Do not install or rely on the retired `next-best-practices` skill.

## Server/client boundaries

Verify:

- [ ] Server Components remain default where appropriate.
- [ ] Client Components exist for real interaction/browser state.
- [ ] sensitive server data is not over-serialized to client.
- [ ] Server Actions are authenticated/authorized like public endpoints.
- [ ] independent server work is parallelized when safe.
- [ ] no avoidable fetch waterfall is introduced.

## React state

Reject:

- duplicated derived state that can diverge;
- effect-driven state that should be derived during render;
- stale closure/update patterns affecting important form state;
- global state introduced for a local concern without clear need.

## Components

Use composition when it removes real complexity.

Reject speculative provider/compound-component architecture for one-off needs.

---

# 12. Accessibility & UI Contract — HIGH

The current canonical design source is authoritative.

Verify where relevant:

- [ ] semantic interactive elements;
- [ ] keyboard operation;
- [ ] visible focus;
- [ ] accessible names/labels;
- [ ] programmatic form-error association;
- [ ] status meaning not conveyed only by color;
- [ ] semantic table headers/relationships;
- [ ] required responsive behavior;
- [ ] essential text reflows without clipping;
- [ ] reduced motion is respected;
- [ ] locale/bilingual behavior preserves required state.

For major UI/pre-release:

- run `frontend-checklist-global`;
- run `browser-qa` on preview/staging.

---

# 13. Performance & Reliability — HIGH/MEDIUM

Verify:

- [ ] server-side pagination for operational lists;
- [ ] no full-dataset browser filtering where server search is required;
- [ ] deterministic stable sorting;
- [ ] required DB indexes exist;
- [ ] no avoidable React/Next waterfalls;
- [ ] client bundle growth is justified;
- [ ] heavy UI can be deferred/lazy-loaded where appropriate;
- [ ] external delivery is retryable/after-commit where required;
- [ ] rate limiting is durable where required;
- [ ] PII responses follow required private/no-store behavior;
- [ ] code fits Vercel stateless/serverless runtime assumptions.

After deployment use `vercel-optimize` for Vercel-specific performance/cost investigation.

---

# 14. Semantic Duplication — MEDIUM

Before introducing shared reusable logic, reviewer must check whether equivalent behavior already exists using:

- GitNexus;
- OMP LSP/symbol search;
- focused grep/search.

Flag:

- duplicate business validators;
- duplicate mappers/formatters;
- duplicate auth/permission helpers;
- duplicate hooks/components that should share semantics.

Do not merge code solely because syntax is similar. Business semantics determine whether reuse is correct.

---

# 15. Maintainability / Simplicity — MEDIUM

Use `ponytail-review` when the diff adds meaningful abstraction/dependencies.

Flag:

- speculative abstraction;
- wrappers without policy;
- unnecessary dependency;
- generalized API with one real use;
- broad unrelated refactor;
- avoidable indirection.

Never simplify away:

- authorization;
- RLS/grants;
- validation;
- concurrency;
- idempotency;
- privacy;
- accessibility;
- audit requirements;
- explicit current-source requirements.

---

# 16. Orca / OMP Workflow Safety — HIGH

## Worktrees

Reject workflow if:

- two writing agents modify the same worktree concurrently;
- parallel Orca tasks own overlapping schema migrations without coordination;
- a handoff does not state current branch/worktree and verification state.

Use Orca for separate-worktree parallelism.

Use OMP subagents/advisor for bounded analysis/review around one writer.

## OMP instructions

Preferred project-native structure:

```text
.omp/AGENTS.md  -> imports root AGENTS.md
.omp/RULES.md   -> short sticky hard rules
.omp/WATCHDOG.md -> advisor-only review priorities
.agents/skills/ -> canonical project skills
```

Do not maintain a separate hand-written `CLAUDE.md` policy for this project.

A `CLAUDE.md` generated by Next.js as `@AGENTS.md` is a compatibility shim, not a second policy source.

---

# 17. OMP Advisor / Independent Review

For high-risk diffs, prefer independent review.

Suggested sequence:

```text
code-review
-> OMP /review
-> ponytail-review if complexity increased
-> verification-before-completion
```

Advisor/WATCHDOG should focus on:

- source drift;
- authn/authz confusion;
- RLS/grant bypass;
- races/lock ordering;
- stale writes/idempotency;
- private document exposure;
- unsafe MCP/live environment operations;
- overbroad changes.

Keep advisor investigative/read-only unless explicitly authorized otherwise.

---

# 18. React Doctor Gate

For meaningful React/Next.js changes run current syntax:

```bash
npx react-doctor@latest --verbose --scope changed
```

Do not use stale `--diff` examples as the preferred form.

Treat findings as review input; do not automatically rewrite unrelated code.

---

# 19. Graph Intelligence & Code Review Contracts (v2.4)

This project uses Code Review Graph for broad diff triage and GitNexus for precise caller/callee and blast-radius impact.

### Review Workflow:
1. `REVIEW.md` / task contract and acceptance criteria check.
2. Direct git diff and source inspection.
3. CRG minimal diff triage when useful (`detect_changes_tool`, `get_review_context_tool`).
4. Identify highest-risk changed symbols.
5. GitNexus precise impact for those symbols when useful (`impact`, `context`).
6. Direct source and tests verification.
7. Final review findings issued through `eiu-code-review`.

### Review Rules & Invariants:
- Do not require graph calls for trivial or localized diffs.
- Never issue findings or verdicts solely from graph output.
- `GRAPH_FINDING_NEEDS_SOURCE_CONFIRMATION`: Mandatory direct source confirmation for any graph-material finding.
- `DB_EFFECTIVE_DEFINITION_VERIFIED`: Database findings must be verified against direct SQL, declarative schema, and ordered migrations before assigning a defect.
- `SQL_ABSENCE_VERIFIED`: Never conclude a function, trigger, RPC, or policy is missing based on graph absence alone.
- Both CRG and GitNexus require explicit freshness verification before review evidence is accepted.

Verify:
- [ ] CRG MCP is available for broad triage;
- [ ] GitNexus MCP is available for precise impact analysis;
- [ ] freshness gates are checked before using graph evidence;
- [ ] shared/high-risk edits use impact analysis when relationships are not trivially local;
- [ ] large/high-risk final diffs receive GitNexus change-impact review where useful;
- [ ] actual source is inspected before assigning findings;
- [ ] database findings are verified against migrations, schema, and direct SQL;
- [ ] Graphify is recognized as dormant and non-authoritative.

---

# 20. Final Verification Gate

Before approval:

- [ ] current source conformance checked;
- [ ] affected auth/authorization paths tested;
- [ ] type/static checks pass;
- [ ] focused tests pass;
- [ ] database/RLS tests pass when applicable;
- [ ] concurrency/idempotency tests pass when applicable;
- [ ] React Doctor passes/has reviewed findings when applicable;
- [ ] UI/browser QA completed when applicable;
- [ ] final diff has no unrelated scope creep;
- [ ] independent review used for high-risk work;
- [ ] `verification-before-completion` evidence is fresh.

A green build alone is not sufficient proof of business/security correctness.

---

# 21. Reviewer Output Format

Use:

```text
BLOCKER
HIGH
MEDIUM
LOW
```

Every finding should include:

1. file/symbol;
2. violated current-source/review contract;
3. concrete failure mode;
4. smallest safe remediation;
5. verification required.

Prefer fewer high-confidence findings over speculative nitpicks.
