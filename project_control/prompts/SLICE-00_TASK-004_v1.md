# EIU Recruitment — Executor Prompt
## TASK-S00-004 — Browser/Server Credential Boundary + Trusted-Command Interface + Security/Logging Boundaries
### Prompt version: SLICE-00_TASK-004_v1

## 0. Execution Control

```text
SOURCE_BASELINE: Full Handover v1.17
SOURCE_SHA256: 0b39c3615dd5b34e998527a1d273e0b846458c7bd4170be46c9bb670bfcb3498
BUSINESS_STATUS: Business Logic Core v1.2 = FROZEN
TECHNICAL_STATUS: Technical Architecture v1.17 = TECHNICAL SPECIFICATION FROZEN
TASK_SCOPE: TASK-S00-004 Browser/Server Boundaries & Trusted-Command Interface
BASE_BRANCH: autonomy/continuous-integration-20260905-01
BASE_HEAD: f2d273847e4098ec12048049a40e96071b06e536
```

---

## 1. Role & Boundary

You are the Coding Executor for:
```text
TASK-S00-004: Browser/server credential boundary + trusted-command interface + security/logging boundaries
```

### Non-Goals
- Do NOT implement domain recruitment screens or candidate/HR UI pages.
- Do NOT implement full business slice features (Slice 01–08).
- Do NOT deploy to Vercel or mutate production infrastructure.
- Do NOT commit `.env.local` or any secrets/keys.
- Do NOT weaken RLS, search_path, or grant requirements.

---

## 2. Canonical Source References

- `recruitment_webapp/review_pack/12_IMPLEMENTATION_NOTES_VERCEL_SUPABASE.md`
- `recruitment_webapp/review_pack/37_BACKEND_COMMAND_CONTRACTS.md`
- `recruitment_webapp/review_pack/67_WEB_SECURITY_BASELINE.md`
- `recruitment_webapp/review_pack/39_SECURITY_RLS_MATRIX.md`

---

## 3. Implementation Requirements

All code lives inside `web/`:

### 3.1 Dependencies
Install required runtime/type dependencies cleanly under `web/`:
- `@supabase/ssr`
- `@supabase/supabase-js`
- `zod`
Ensure lockfile `web/package-lock.json` is updated cleanly via `npm install` and audit passes.

### 3.2 Environment & Credential Boundary (`web/src/lib/env.ts`)
- Validate environment variables using Zod.
- Public variables: `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`, `NEXT_PUBLIC_APP_URL`.
- Server-only variables: `SUPABASE_SERVICE_ROLE_KEY`.
- Enforce that `SUPABASE_SERVICE_ROLE_KEY` is accessible ONLY on the server:
  - If `typeof window !== 'undefined'`, accessing server secrets must throw or fail compile-time.
  - Provide a safe accessor `getServerEnv()` and `getClientEnv()`.

### 3.3 Supabase Client Factories (`web/src/lib/supabase/`)
- `client.ts`: `createBrowserClient` using `@supabase/ssr` with public URL and anon key.
- `server.ts`: `createServerClient` using `@supabase/ssr` reading and setting cookie store for Server Components, Server Actions, and Route Handlers.
- `admin.ts`: `createAdminClient` using `@supabase/supabase-js` with `SUPABASE_SERVICE_ROLE_KEY`. Guarded with:
  ```ts
  if (typeof window !== 'undefined') {
    throw new Error('Admin client cannot be created in browser environment');
  }
  ```

### 3.4 Security Headers (`web/next.config.ts`)
Configure Next.js HTTP headers per `67_WEB_SECURITY_BASELINE.md`:
- `Content-Security-Policy`: `default-src 'self'; script-src 'self' 'unsafe-eval' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; font-src 'self'; connect-src 'self' https:; frame-ancestors 'none'; object-src 'none'; base-uri 'self'; form-action 'self'`
- `X-Content-Type-Options: nosniff`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy: camera=(), microphone=(), geolocation=()`
- `X-Frame-Options: DENY`

### 3.5 Logging Redaction Engine (`web/src/lib/logging/logger.ts`)
- Implement a structured logger (`info`, `warn`, `error`, `debug`).
- Implement redaction that automatically masks sensitive patterns:
  - Passwords, OTP codes, session tokens, authorization headers, private keys, service role keys, and PII terms.
  - Test evidence must prove tokens and OTPs are redacted into `[REDACTED]`.

### 3.6 Trusted-Command Envelope & Runner (`web/src/lib/commands/`)
- `types.ts`:
  - Enumerate the 24 canonical error codes from `37_BACKEND_COMMAND_CONTRACTS.md`:
    `UNAUTHENTICATED`, `FORBIDDEN`, `NOT_FOUND`, `INVALID_STATE`, `VALIDATION_ERROR`, `STALE_VERSION`, `FORM_SESSION_EXPIRED`, `UPLOAD_RESERVATION_EXPIRED`, `DUPLICATE_APPLICATION`, `APPLICATION_DURABLE_IDENTITY_IMMUTABLE`, `PRIVACY_NOTICE_UNAVAILABLE`, `SCHEDULE_CONFLICT_CANDIDATE`, `SCHEDULE_CONFLICT_INTERVIEWER`, `SCHEDULE_CONFLICT_ROOM`, `LATEST_ROUND_REQUIRED`, `ROOT_ADMIN_PROTECTED`, `IDENTITY_REBIND_FORBIDDEN`, `USER_INACTIVE`, `UPLOAD_LIMIT_EXCEEDED`, `UNSUPPORTED_FILE_TYPE`, `MALWARE_SCAN_REQUIRED`, `IDEMPOTENCY_REPLAY`, `INVALID_PERMISSION_DEPENDENCY`, `INTERNAL_ERROR`.
  - Define `CommandResult<T>`:
    `{ success: true, data: T } | { success: false, error: { code: CommandErrorCode, message: string, details?: unknown } }`.
  - Define `CommandContext`:
    `{ actor: { id: string, email: string, role: string }, permissions: string[] }`.
- `runner.ts`:
  - Implement `createCommandHandler<TInput, TOutput>`:
    Pipeline:
    1. Authenticate check: fail closed with `UNAUTHENTICATED` if no actor.
    2. Authorize check: fail closed with `FORBIDDEN` if actor lacks required permission.
    3. Input validation: validate against Zod schema; fail with `VALIDATION_ERROR` and field details.
    4. Execution: call transaction / business handler.
    5. Error handling: catch unhandled errors, log with redaction, return stable `INTERNAL_ERROR` code without leaking stack traces.

### 3.7 Verification Suite
Add automated tests under `web/src/__tests__/`:
- `credential-boundary.test.ts`: verify server secret is not accessible on client.
- `logger.test.ts`: verify token, OTP, password redaction.
- `command-runner.test.ts`: verify authentication, authorization, validation, and success pipelines.
Configure `"test": "node --test"` or tsx test runner in `web/package.json`.

---

## 4. Acceptance Criteria

1. `npm run typecheck` PASS (`next typegen && tsc --noEmit`).
2. `npm run lint` PASS (`biome check`).
3. `npm run build` PASS (`next build`).
4. Automated tests PASS (credential boundary, redaction, command runner).
5. Secret scan PASS: zero credentials committed.
6. Tracked source files in `recruitment_webapp` remain 100% byte-identical.
7. `project_control/EVIDENCE_INDEX.yaml` updated under `BOUNDARY-001` with full test evidence.
8. `project_control/CURRENT_STATE.md` and `project_control/TASK_REGISTRY.yaml` updated.
9. Exactly one scoped commit on the task branch.
