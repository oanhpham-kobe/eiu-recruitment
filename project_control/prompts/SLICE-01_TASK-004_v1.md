# EIU Recruitment — Executor Prompt
## TASK-S01-004 — Auth Callback Route Handlers, Server Session Validation, and Client Auth State Hooks
### Prompt version: SLICE-01_TASK-004_v1

## 0. Execution Control

```text
SOURCE_BASELINE: Full Handover v1.17
SOURCE_SHA256: 0b39c3615dd5b34e998527a1d273e0b846458c7bd4170be46c9bb670bfcb3498
BUSINESS_STATUS: Business Logic Core v1.2 = FROZEN
TECHNICAL_STATUS: Technical Architecture v1.17 = TECHNICAL SPECIFICATION FROZEN
TASK_SCOPE: TASK-S01-004 Auth Route Handlers & Session Validation Only
WORKTREE: D:/orca/recruitment/TASK-S01-004-auth-routes
BRANCH: oanhpham-kobe/TASK-S01-004-auth-routes
BASE_BRANCH: autonomy/continuous-integration-20260905-01
BASE_HEAD: 33686b362901214b8e6e6201951e366d7e59a091
```

---

## 1. Role & Boundary

You are the Coding Executor for:
```text
TASK-S01-004: Auth callback route handlers, server session validation, and client auth state hooks
```

### Scope & Principles
This task connects the database provisioning commands from Tasks S01-002 and S01-003 to Next.js App Router route handlers and server session validation per review pack 12 and 67.
Authentication is not authorization; session identity and roles must be derived server-side.

### Authorized Scope
The Executor is authorized to perform:
1. Implement Next.js App Router route handlers under `web/src/app/auth/`:
   - `callback/route.ts`:
     * Google OAuth callback handler.
     * Extracts `code` and optional `next` redirect target.
     * Defends against open-redirect: validates that `next` starts with `/` and not `//` or external protocols.
     * Exchanges code for session via `@supabase/ssr` server client (`exchangeCodeForSession`).
     * Calls `provisionInternalUserIdentity()` via server client.
     * Redirects to validated destination or `/login?error=...` on failure.
   - `candidate/verify/route.ts`:
     * Candidate OTP verification endpoint.
     * Enforces same-origin validation (`validateSameOrigin`).
     * Verifies OTP code via `@supabase/ssr` server client (`verifyOtp`).
     * Calls `provisionCandidateIdentity()` via server client.
     * Returns structured `CommandResult`.
   - `signout/route.ts`:
     * Signs out user via server client (`signOut`).
     * Clears cookies and redirects to `/login`.
2. Implement server-only session resolver in `web/src/lib/auth/session.ts`:
   - Begins with `import 'server-only';`.
   - `getServerSession()`: calls `supabase.auth.getUser()`, verifies active state, derives user role and permissions from `app_users` or `candidates`, and returns typed `AppSession`.
3. Implement client-side auth state hook & context in `web/src/lib/auth/context.tsx`:
   - Provides `AuthProvider` and `useAuth()` hook using `createBrowserClient()`.
4. Add automated tests under `web/src/__tests__/auth-routes.test.ts`:
   - Open redirect defense tests.
   - Callback missing code handling.
   - Candidate OTP same-origin CSRF defense.
   - Server session derivation distinguishing internal vs candidate identity.
   - Signout handler tests.
5. Run full verification: `npm run typecheck`, `npm run lint`, `npm run build`, `npm test`.
6. Update project-control records (`EVIDENCE_INDEX.yaml`, `CURRENT_STATE.md`, `TASK_REGISTRY.yaml`, and track this prompt) with status `REVIEW` (pending independent review).
7. Commit all changes cleanly on `oanhpham-kobe/TASK-S01-004-auth-routes`.

### Non-Goals
- Do NOT mark TASK-S01-004 as `DONE` in this commit. Per `TASK_EXECUTION_LIFECYCLE.md` and `REVIEWER_CONTRACT.md`, the Executor records `status: REVIEW`; the `DONE` transition is reserved for the Planner after an independent implementation review PASS.
- Do NOT implement visual login UI pages or CSS design shells (that belongs to TASK-S01-005).
- Do NOT deploy to Vercel or mutate external databases (`--linked` is forbidden).
- Do NOT modify tracked `supabase/config.toml` in the task worktree.
- Do NOT commit `.env.local` or any secrets/keys.

---

## 2. Canonical Source References

- `recruitment_webapp/review_pack/12_IMPLEMENTATION_NOTES_VERCEL_SUPABASE.md` (§Auth: @supabase/ssr cookie-based auth in Next.js, Google OAuth callback, Candidate OTP verify, server session derivation)
- `recruitment_webapp/review_pack/37_BACKEND_COMMAND_CONTRACTS.md` (§3 Candidate identity and internal provisioning)
- `recruitment_webapp/review_pack/67_WEB_SECURITY_BASELINE.md` (§Cookies/session, §CSRF/origin, §Logging/error redaction)
- `AGENTS.md` (Rule 12: Conceptual mutation order; Sticky Rule 2: Authentication is not authorization)

---

## 3. Implementation Specification

All code resides in `web/`:

### 3.1 Route Handlers (`web/src/app/auth/`)

1. **Google OAuth Callback (`web/src/app/auth/callback/route.ts`)**:
   ```ts
   import { NextRequest, NextResponse } from 'next/server';
   import { createServerClient } from '@/lib/supabase/server';
   import { provisionInternalUserIdentity } from '@/lib/auth/internal';

   export async function GET(request: NextRequest) {
     const requestUrl = new URL(request.url);
     const code = requestUrl.searchParams.get('code');
     const rawNext = requestUrl.searchParams.get('next') || '/';

     // Open redirect defense
     const next = (rawNext.startsWith('/') && !rawNext.startsWith('//')) ? rawNext : '/';

     if (!code) {
       return NextResponse.redirect(new URL('/login?error=MISSING_CODE', request.url));
     }

     const supabase = await createServerClient();
     const { error: exchangeError } = await supabase.auth.exchangeCodeForSession(code);
     if (exchangeError) {
       return NextResponse.redirect(new URL('/login?error=AUTH_EXCHANGE_FAILED', request.url));
     }

     // Provision internal identity
     const provisionResult = await provisionInternalUserIdentity();
     if (!provisionResult.success) {
       await supabase.auth.signOut();
       const errCode = provisionResult.error.code;
       return NextResponse.redirect(new URL(`/login?error=${encodeURIComponent(errCode)}`, request.url));
     }

     return NextResponse.redirect(new URL(next, request.url));
   }
   ```

2. **Candidate OTP Verification (`web/src/app/auth/candidate/verify/route.ts`)**:
   ```ts
   import { NextRequest, NextResponse } from 'next/server';
   import { createServerClient } from '@/lib/supabase/server';
   import { provisionCandidateIdentity } from '@/lib/auth/candidate';
   import { validateSameOrigin } from '@/lib/security/origin';

   export async function POST(request: NextRequest) {
     if (!validateSameOrigin(request)) {
       return NextResponse.json({ success: false, error: { code: 'FORBIDDEN', message: 'Cross-origin request rejected' } }, { status: 403 });
     }

     const body = await request.json();
     const { email, token } = body;
     if (!email || !token) {
       return NextResponse.json({ success: false, error: { code: 'VALIDATION_ERROR', message: 'Email and OTP token are required' } }, { status: 400 });
     }

     const supabase = await createServerClient();
     const { error: otpError } = await supabase.auth.verifyOtp({ email, token, type: 'email' });
     if (otpError) {
       return NextResponse.json({ success: false, error: { code: 'UNAUTHENTICATED', message: 'Invalid or expired OTP code' } }, { status: 401 });
     }

     const provisionResult = await provisionCandidateIdentity();
     return NextResponse.json(provisionResult, { status: provisionResult.success ? 200 : 400 });
   }
   ```

3. **Signout (`web/src/app/auth/signout/route.ts`)**:
   ```ts
   import { NextRequest, NextResponse } from 'next/server';
   import { createServerClient } from '@/lib/supabase/server';

   export async function POST(request: NextRequest) {
     const supabase = await createServerClient();
     await supabase.auth.signOut();
     return NextResponse.redirect(new URL('/login', request.url), { status: 303 });
   }
   ```

### 3.2 Server-Only Session Resolver (`web/src/lib/auth/session.ts`)
```ts
import 'server-only';
import { createServerClient } from '@/lib/supabase/server';

export interface AppUserSession {
  authUserId: string;
  email: string;
  isInternal: boolean;
  isCandidate: boolean;
  appUserId?: string;
  candidateId?: string;
  roles: string[];
  permissions: string[];
}

export interface AppSession {
  user: AppUserSession | null;
  isAuthenticated: boolean;
}

export async function getServerSession(): Promise<AppSession> {
  const supabase = await createServerClient();
  const { data: { user }, error } = await supabase.auth.getUser();

  if (error || !user || !user.email) {
    return { user: null, isAuthenticated: false };
  }

  const isInternal = user.email.toLowerCase().endsWith('@eiu.edu.vn');
  if (isInternal) {
    const { data: appUser } = await supabase
      .from('app_users')
      .select('app_user_id, is_active, is_root_admin, app_user_roles(role_code), app_user_permissions(permission_code)')
      .eq('auth_user_id', user.id)
      .single();

    if (!appUser || !appUser.is_active) {
      return { user: null, isAuthenticated: false };
    }

    const roles = ((appUser as any).app_user_roles || []).map((r: any) => r.role_code);
    const permissions = ((appUser as any).app_user_permissions || []).map((p: any) => p.permission_code);

    return {
      isAuthenticated: true,
      user: {
        authUserId: user.id,
        email: user.email,
        isInternal: true,
        isCandidate: false,
        appUserId: appUser.app_user_id,
        roles,
        permissions,
      },
    };
  } else {
    const { data: candidate } = await supabase
      .from('candidates')
      .select('candidate_id, is_active')
      .eq('auth_user_id', user.id)
      .single();

    if (!candidate || !candidate.is_active) {
      return { user: null, isAuthenticated: false };
    }

    return {
      isAuthenticated: true,
      user: {
        authUserId: user.id,
        email: user.email,
        isInternal: false,
        isCandidate: true,
        candidateId: candidate.candidate_id,
        roles: ['CANDIDATE'],
        permissions: ['candidate.self'],
      },
    };
  }
}
```

### 3.3 Client-Side Auth Context (`web/src/lib/auth/context.tsx`)
Create a lightweight `AuthProvider` and `useAuth()` hook subscribing to `onAuthStateChange`.

### 3.4 Automated Test Suite (`web/src/__tests__/auth-routes.test.ts`)
Add tests verifying:
1. Open redirect defense: target URLs with `//evil.com` or `https://evil.com` normalize to `/`.
2. Missing code in callback handler redirects to `/login?error=MISSING_CODE`.
3. Candidate OTP verify route rejects requests failing `validateSameOrigin`.
4. `getServerSession()` returns unauthenticated when no session exists.
5. `getServerSession()` resolves internal permissions from database, not client arguments.

---

## 4. Acceptance Criteria

1. `npm run typecheck` PASS (`next typegen && tsc --noEmit`).
2. `npm run lint` PASS (`biome check`).
3. `npm run build` PASS (`next build`).
4. `npm test` PASS (all existing 46 tests + new auth route and session tests pass).
5. Open redirect defense and CSRF origin validation verified.
6. Zero secrets or credentials committed.
7. `project_control/EVIDENCE_INDEX.yaml` updated under `AUTH-ROUTES-001` with test results.
8. `project_control/CURRENT_STATE.md` and `project_control/TASK_REGISTRY.yaml` updated with `status: REVIEW` (pending independent review), with prompt SHA-256 bound.
9. Exactly one clean commit on `oanhpham-kobe/TASK-S01-004-auth-routes`.
