# EIU Recruitment — Executor Prompt
## TASK-S00-004 — Browser/Server Credential Boundary + Trusted-Command Interface + Security/Logging Boundaries
### Prompt version: SLICE-00_TASK-004_v8

## 0. Execution Control

```text
SOURCE_BASELINE: Full Handover v1.17
SOURCE_SHA256: 0b39c3615dd5b34e998527a1d273e0b846458c7bd4170be46c9bb670bfcb3498
BUSINESS_STATUS: Business Logic Core v1.2 = FROZEN
TECHNICAL_STATUS: Technical Architecture v1.17 = TECHNICAL SPECIFICATION FROZEN
TASK_SCOPE: TASK-S00-004 Interface & Boundary Foundation Only
WORKTREE: D:/orca/recruitment/TASK-S00-004-boundaries
BRANCH: oanhpham-kobe/TASK-S00-004-boundaries
BASE_BRANCH: autonomy/continuous-integration-20260905-01
BASE_HEAD: f2d273847e4098ec12048049a40e96071b06e536
```

---

## 1. Role & Boundary

You are the Coding Executor for:
```text
TASK-S00-004: Browser/server credential boundary + trusted-command interface + security/logging boundaries
```

### Scope & Principles
This is an **interface-only and boundary foundation** task per Slice-00 rule ledger (S00-R03, S00-R04, S00-R07).
Establish typed contracts, dynamic security defenses, and boundary protections without implementing premature business feature logic.

### Authorized Scope
The Executor is authorized to perform:
1. Install official `@supabase/ssr`, `@supabase/supabase-js`, and `server-only` in `web/` and pin `package-lock.json`.
2. Implement typed environment and credential boundary in `web/src/lib/env/` using `server-only` for server secrets.
3. Implement browser and server Supabase client factories in `web/src/lib/supabase/`.
4. Configure framework-compatible per-request nonce-based CSP via `web/src/middleware.ts`, opt into dynamic rendering in `web/src/app/`, and configure static security headers in `web/next.config.ts`.
5. Implement same-origin CSRF validation helper (`web/src/lib/security/origin.ts`) and sensitive cache header helper (`web/src/lib/security/cache.ts`).
6. Implement structured logging with cycle-safe traversal and content-pattern sensitive data redaction in `web/src/lib/logging/logger.ts`.
7. Implement typed trusted-command envelope and staged execution runner strictly enforcing the mandated mutation order: `authenticate -> authorize -> validate -> execute` (`web/src/lib/commands/`).
8. Add automated tests under `web/src/__tests__/`:
   - client bundle negative scan (zero server secrets in `.next/static/`);
   - command runner fail-closed tests, including proof that unauthorized requests fail closed with `FORBIDDEN` without reaching full validation;
   - distinct nonces across requests;
   - browser-level smoke test asserting zero CSP violations;
   - cycle-safe and content-pattern redaction tests (e.g. numeric `{ otp: 123456 }`, bare JWTs, Bearer headers, signed URL query parameters, cyclic objects, and sanitized Error instances without raw stack traces).
9. Update project-control records (`EVIDENCE_INDEX.yaml`, `CURRENT_STATE.md`, `TASK_REGISTRY.yaml`, and track this prompt) with status `REVIEW` (pending independent review).
10. Commit all changes cleanly on `oanhpham-kobe/TASK-S00-004-boundaries`.

### Non-Goals
- Do NOT invert or alter the mandatory security sequence: `authenticate -> authorize -> validate -> execute`.
- Do NOT mark TASK-S00-004 as `DONE` in this commit. Per `TASK_EXECUTION_LIFECYCLE.md` and `REVIEWER_CONTRACT.md`, the Executor records `status: REVIEW`; the `DONE` transition is reserved for the Planner after an independent implementation review PASS.
- Do NOT create or expose any service-role client. Service-role usage is prohibited in this task per Sticky Rule 4 and rule S00-R03.
- Do NOT implement domain recruitment screens, forms, or candidate/HR UI pages.
- Do NOT implement business slice logic (Slice 01–08).
- Do NOT deploy to Vercel or mutate external databases.
- Do NOT commit `.env.local` or any secrets/keys.
- Do NOT use static insecure CSP (`unsafe-inline` or `unsafe-eval`); use per-request dynamic nonces with dynamic rendering.

---

## 2. Canonical Source References

- `recruitment_webapp/review_pack/12_IMPLEMENTATION_NOTES_VERCEL_SUPABASE.md` (§Data access, §Mutations)
- `recruitment_webapp/review_pack/37_BACKEND_COMMAND_CONTRACTS.md` (§1 Hard architecture rules, §2 Core error codes)
- `recruitment_webapp/review_pack/67_WEB_SECURITY_BASELINE.md` (§Transport and headers, §Cookies/session, §CSRF/origin, §Sensitive caching, §Logging/error redaction)
- `project_control/prompts/SLICE-00_MASTER_PLAN_REFERENCE.md` (§Rule Ledger S00-R03, S00-R04, S00-R07)
- `AGENTS.md` (Rule 12: Conceptual mutation order)

---

## 3. Implementation Specification

All implementation code resides in `web/`:

### 3.1 Dependencies
Under `web/`, install:
- `@supabase/ssr`
- `@supabase/supabase-js`
- `server-only`
Ensure `web/package-lock.json` updates cleanly via npm.

### 3.2 Environment & Credential Boundary (`web/src/lib/env/`)
- `client.ts`:
  - Validates and exports public environment variables:
    `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY` (or `NEXT_PUBLIC_SUPABASE_ANON_KEY`).
  - Safe for import into Client Components.
- `server.ts`:
  - Begins with `import 'server-only';`.
  - Validates and exports server-only environment variables (`SUPABASE_SERVICE_ROLE_KEY` if provided at runtime).
  - Throws at build/compile time if imported from any Client Component.

### 3.3 Supabase Client Factories (`web/src/lib/supabase/`)
- `client.ts`:
  - `createBrowserClient()` using `@supabase/ssr` `createBrowserClient` with public URL and publishable/anon key.
  - Client-safe, intended for Client Component interactions.
- `server.ts`:
  - Begins with `import 'server-only';`.
  - `createServerClient()` using `@supabase/ssr` `createServerClient` reading cookies via Next.js `cookies()` helper for Server Components, Server Actions, and Route Handlers.
  - Server-side caller identity must always be derived via `supabase.auth.getUser()`, never trusting client-provided actor IDs.

### 3.4 Dynamic Nonce-Based Web Security Baseline & Dynamic Rendering
Per Next.js App Router requirements and §67 ("*Prefer nonce/hash-compatible CSP rather than unsafe-inline where feasible*"):
- **Dynamic Rendering Opt-In**:
  In `web/src/app/layout.tsx` (and `page.tsx`), opt into dynamic rendering:
  ```ts
  export const dynamic = 'force-dynamic';
  ```
  Read the per-request nonce via:
  ```ts
  import { headers } from 'next/headers';
  const nonce = (await headers()).get('x-nonce') || undefined;
  ```
- **Middleware (`web/src/middleware.ts`)**:
  - For each request, generate a cryptographic nonce: `const nonce = Buffer.from(crypto.randomUUID()).toString('base64');`.
  - Derive Supabase origin dynamically from `process.env.NEXT_PUBLIC_SUPABASE_URL` (e.g. `new URL(url).origin`).
  - Construct dynamic CSP:
    `default-src 'self'; script-src 'self' 'nonce-${nonce}' 'strict-dynamic'; style-src 'self' 'nonce-${nonce}'; img-src 'self' data:; font-src 'self'; connect-src 'self' ${supabaseOrigin}; object-src 'none'; base-uri 'self'; form-action 'self'; frame-ancestors 'none'`
  - Set `x-nonce` and `Content-Security-Policy` on request headers for downstream server components.
  - Set `Content-Security-Policy`, `x-nonce`, `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`, `Permissions-Policy: camera=(), microphone=(), geolocation=()`, and `X-Frame-Options: DENY` on the outgoing response.
- **Headers in `next.config.ts`**:
  Export static fallback security headers (`nosniff`, `DENY`, `strict-origin-when-cross-origin`, `Permissions-Policy`).

- **Same-Origin / CSRF Helper (`web/src/lib/security/origin.ts`)**:
  - `validateSameOrigin(request: Request): boolean`:
    Extracts `origin` or `referer` header and compares against `host` / `x-forwarded-host`. Rejects mismatched or untrusted origins for state-changing operations per §67.

- **Sensitive Cache Helper (`web/src/lib/security/cache.ts`)**:
  - `getSensitiveCacheHeaders(): Record<string, string>`:
    Returns `{ 'Cache-Control': 'private, no-store' }` for authenticated PII / mutation responses per §67.

### 3.5 Cycle-Safe & Content-Pattern Logging Redaction Engine (`web/src/lib/logging/logger.ts`)
Implement structured logging with cycle-safe and pattern-aware redaction:
- **Cycle-Safe Traversal**:
  Maintain a `WeakSet` of seen objects/arrays during recursive traversal. If an object has already been seen, return `'[CIRCULAR]'` instead of recursing, preventing infinite loops or stack overflow errors.
- **Key-Based Redaction**:
  For object entries whose keys match case-insensitively (`token`, `secret`, `password`, `cookie`, `authorization`, `otp`, `service_role`, `cv_text`, `document_url`), replace the **entire value** with `'[REDACTED]'`, regardless of runtime type (numbers like `{ otp: 123456 }`, strings, arrays, objects).
- **String Content-Pattern Redaction**:
  Inspect all string values (including bare strings, message fields, and URLs) and apply pattern redaction:
  - Bearer tokens: `/Bearer\s+[A-Za-z0-9\-._~+/]+=*/gi` -> `Bearer [REDACTED]`
  - Raw JWT tokens: `/\beyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*/g` -> `[REDACTED_JWT]`
  - Signed URL query parameters: `/[?&](token|signature|apikey|key|secret|sig)=[^&\s]+/gi` -> `?$1=[REDACTED]`
  - Embedded credentials in URLs: `/:\/\/([^:]+):([^@]+)@/g` -> `://$1:[REDACTED]@`
  - 6-digit OTP codes: `/\b(otp|code|one-time password)[\s:=]+(\d{6})\b/gi` -> `$1: [REDACTED]`
- **Error Instance Redaction**:
  When logging an `Error` instance:
  - Extract `{ name: err.name, message: redactString(err.message) }`.
  - Do NOT emit raw `err.stack` in logged payloads.

### 3.6 Trusted-Command Envelope & Staged Runner (`web/src/lib/commands/`)
The command runner strictly enforces the mandatory project mutation order:
`authenticate -> authorize -> validate -> invoke approved transactional command/RPC -> return stable result/error`

- `types.ts`:
  - Define `CommandErrorCode` enum containing exactly the 24 canonical codes from `37_BACKEND_COMMAND_CONTRACTS.md`:
    `UNAUTHENTICATED`, `FORBIDDEN`, `NOT_FOUND`, `INVALID_STATE`, `VALIDATION_ERROR`, `STALE_VERSION`, `FORM_SESSION_EXPIRED`, `UPLOAD_RESERVATION_EXPIRED`, `DUPLICATE_APPLICATION`, `APPLICATION_DURABLE_IDENTITY_IMMUTABLE`, `PRIVACY_NOTICE_UNAVAILABLE`, `SCHEDULE_CONFLICT_CANDIDATE`, `SCHEDULE_CONFLICT_INTERVIEWER`, `SCHEDULE_CONFLICT_ROOM`, `LATEST_ROUND_REQUIRED`, `ROOT_ADMIN_PROTECTED`, `IDENTITY_REBIND_FORBIDDEN`, `USER_INACTIVE`, `UPLOAD_LIMIT_EXCEEDED`, `UNSUPPORTED_FILE_TYPE`, `MALWARE_SCAN_REQUIRED`, `IDEMPOTENCY_REPLAY`, `INVALID_PERMISSION_DEPENDENCY`, `INTERNAL_ERROR`.
  - Define `CommandResult<T>`:
    `{ success: true; data: T } | { success: false; error: CommandError }`
  - Define `CommandError`:
    `{ code: CommandErrorCode; message: string; details?: unknown }`
  - Define `VerifiedActor`:
    `{ authUserId: string; email: string; isActive: boolean; roles: string[]; permissions: string[] }`
    Identity and permissions must be derived on the server side, never accepted from browser arguments.
  - Define `AuthorizationResult`:
    `{ authorized: true } | { authorized: false; reason?: string; code?: CommandErrorCode }`
  - Define `TrustedCommandDefinition<TRawInput, TTarget, TValidatedInput, TOutput>`:
    - `name: string`
    - `extractTarget?: (rawInput: TRawInput) => TTarget` (minimal untrusted payload decoding to extract entity ID / context target)
    - `authorize: (actor: VerifiedActor, target?: TTarget) => Promise<AuthorizationResult> | AuthorizationResult`
    - `validate: (rawInput: TRawInput) => { success: true; data: TValidatedInput } | { success: false; error: string; details?: unknown }`
    - `execute: (actor: VerifiedActor, input: TValidatedInput) => Promise<TOutput>`

- `runner.ts`:
  - Begins with `import 'server-only';`.
  - `createCommandRunner(deps: { resolveActor: () => Promise<VerifiedActor | null> })`:
    Returns `executeCommand<TRawInput, TTarget, TValidatedInput, TOutput>(command: TrustedCommandDefinition<TRawInput, TTarget, TValidatedInput, TOutput>, rawInput: TRawInput): Promise<CommandResult<TOutput>>`.
    Enforces the following stages in strict order:
    1. **Stage 1 (Authenticate)**:
       - Call `deps.resolveActor()`.
       - If `!actor` -> return `{ success: false, error: { code: 'UNAUTHENTICATED', message: 'Authentication required' } }`.
       - If `!actor.isActive` -> return `{ success: false, error: { code: 'USER_INACTIVE', message: 'User account is inactive' } }`.
    2. **Stage 2 (Authorize)**:
       - Extract minimal target if command defines `extractTarget`: `const target = command.extractTarget ? command.extractTarget(rawInput) : undefined;`
       - Evaluate authorization predicate: `const authResult = await command.authorize(actor, target);`
       - If `!authResult.authorized`: return `{ success: false, error: { code: authResult.code || 'FORBIDDEN', message: authResult.reason || 'Insufficient permissions' } }`.
       - **CRITICAL**: If authorization fails, execution STOPS immediately. Full DTO validation is NEVER reached!
    3. **Stage 3 (Validate)**:
       - Call `command.validate(rawInput)`.
       - If validation fails -> return `{ success: false, error: { code: 'VALIDATION_ERROR', message: validation.error, details: validation.details } }`.
    4. **Stage 4 (Execute Transactional Command)**:
       - Call `await command.execute(actor, validation.data)`.
       - Return `{ success: true, data: result }`.
    5. **Stage 5 (Error Redaction & Handling)**:
       - Catches any unhandled exception, logs it using `redactSensitiveData`, and returns `{ success: false, error: { code: 'INTERNAL_ERROR', message: 'Internal command error' } }`.

### 3.7 Automated Test Suite & Browser Verification
Add automated tests under `web/src/__tests__/`:
- `client-bundle-scan.test.ts`:
  - Scans client build output chunks in `web/.next/static/` and asserts that server secret identifiers do not appear anywhere in client chunks (satisfying S00-R03 negative scan requirement).
- `security-headers.test.ts`:
  - Proves middleware generates dynamic nonces and sets CSP allowlisting the Supabase origin alongside `'self'`, with `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`, `Permissions-Policy`, and `X-Frame-Options: DENY`.
  - Proves two distinct requests receive distinct nonces (`nonce1 !== nonce2`), and each `x-nonce` matches the `'nonce-${nonce}'` in its CSP.
- `origin.test.ts`:
  - Proves `validateSameOrigin` accepts matching origin/host and rejects mismatched/spoofed origins (satisfying S00-R07 CSRF requirement).
- `cache.test.ts`:
  - Proves `getSensitiveCacheHeaders` returns `Cache-Control: private, no-store` (satisfying S00-R07 sensitive caching requirement).
- `logger.test.ts`:
  - Proves key-based redaction (numeric `{ otp: 123456 }` and `{ password: 'xyz' }`).
  - Proves pattern redaction on raw strings (Bearer tokens, raw JWTs, signed URL query parameters like `?token=...&signature=...`).
  - Proves cycle-safe handling on circular references (asserts no recursion crash, returns `[CIRCULAR]`).
  - Proves `Error` instance redaction with sanitized messages and zero raw stack trace emissions.
- `commands.test.ts`:
  - Proves each command runner stage fails closed and in strict order:
    1. Unauthenticated actor -> returns `UNAUTHENTICATED`.
    2. Inactive actor -> returns `USER_INACTIVE`.
    3. Unauthorized actor submitting an INVALID payload -> returns `FORBIDDEN` (proves full validation is never reached for unauthorized callers).
    4. Authorized actor submitting an INVALID payload -> returns `VALIDATION_ERROR` (proves validation executes only when authorized).
    5. Authenticated, active, authorized actor with VALID payload -> returns `success: true`.
    6. Handler exception -> caught, redacted, returns `INTERNAL_ERROR`.
- `csp-browser-smoke.test.ts`:
  - Runs a live smoke test against Next.js:
    1. Proves HTTP status 200.
    2. Proves response headers contain dynamic `nonce-` CSP and `x-nonce`.
    3. Uses headless browser or page evaluation listening for `securitypolicyviolation` events to assert zero CSP violations occur during page render.

Configure `"test": "node --test"` or tsx test runner in `web/package.json`.

---

## 4. Acceptance Criteria

1. `npm run typecheck` PASS (`next typegen && tsc --noEmit`).
2. `npm run lint` PASS (`biome check`).
3. `npm run build` PASS (`next build`).
4. `npm test` PASS (all boundary, bundle-scan, header, origin, cache, cycle-safe & pattern logger, command runner order, and browser CSP smoke tests passing).
5. Client bundle negative scan PASS: zero server secret identifiers in `.next/static/`.
6. Negative authorization test confirms unauthorized request with invalid payload returns `FORBIDDEN` without reaching validation.
7. Logger tests confirm cycle safety, signed URL parameter redaction, and no raw stack emissions.
8. Live smoke check confirms distinct nonces across requests and zero browser CSP violations.
9. Secret scan PASS: zero credentials committed (`git show --check` and secret audit PASS).
10. Tracked source files in `recruitment_webapp` remain 100% byte-identical.
11. `project_control/EVIDENCE_INDEX.yaml` updated under `BOUNDARY-001` with test evidence.
12. `project_control/CURRENT_STATE.md` and `project_control/TASK_REGISTRY.yaml` updated with `status: REVIEW` (pending independent review), with prompt SHA-256 bound.
13. Exactly one clean commit on `oanhpham-kobe/TASK-S00-004-boundaries`.
