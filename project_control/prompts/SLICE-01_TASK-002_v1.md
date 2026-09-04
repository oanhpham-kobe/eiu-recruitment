# EIU Recruitment — Executor Prompt
## TASK-S01-002 — Internal Google Workspace OAuth First-Login Provisioning Command
### Prompt version: SLICE-01_TASK-002_v1

## 0. Execution Control

```text
SOURCE_BASELINE: Full Handover v1.17
SOURCE_SHA256: 0b39c3615dd5b34e998527a1d273e0b846458c7bd4170be46c9bb670bfcb3498
BUSINESS_STATUS: Business Logic Core v1.2 = FROZEN
TECHNICAL_STATUS: Technical Architecture v1.17 = TECHNICAL SPECIFICATION FROZEN
TASK_SCOPE: TASK-S01-002 Internal Google Provisioning Command Only
WORKTREE: D:/orca/recruitment/TASK-S01-002-google-provisioning
BRANCH: oanhpham-kobe/TASK-S01-002-google-provisioning
BASE_BRANCH: autonomy/continuous-integration-20260905-01
BASE_HEAD: f8991b168b0f2e87ac7637254d47795a6126de20
```

---

## 1. Role & Boundary

You are the Coding Executor for:
```text
TASK-S01-002: Internal Google Workspace OAuth first-login provisioning command
```

### Scope & Principles
This task implements the **transactional first-login identity binding command** for internal EIU staff per review pack 12 and 37.
Internal Google first-login binding is an authenticated transactional provisioning command, not a direct directory edit.

### Authorized Scope
The Executor is authorized to perform:
1. Create ordered migration file `supabase/migrations/20260905040000_internal_user_provisioning.sql`:
   - Implement `public.provision_internal_user_identity()` (or private helper with public RPC wrapper):
     * Runs with `SECURITY DEFINER SET search_path = ''`.
     * Validates authenticated caller (`auth.uid()`). If absent, returns/raises `UNAUTHENTICATED`.
     * Validates caller email domain is `@eiu.edu.vn`. If non-EIU, returns/raises `FORBIDDEN`.
     * Matches pre-seeded/invited `public.app_users` record where `lower(email::text) = lower(session_email)`.
     * If no matching record exists -> returns/raises `NOT_FOUND`.
     * If matching user has `is_active = false` -> returns/raises `USER_INACTIVE`.
     * Rebind defense: if `auth_user_id IS NOT NULL` and `auth_user_id <> auth.uid()` -> returns/raises `IDENTITY_REBIND_FORBIDDEN`.
     * First bind: if `auth_user_id IS NULL`, updates `auth_user_id := auth.uid()`, `updated_at := now()`, `version_no := version_no + 1`.
     * Idempotent return: if `auth_user_id = auth.uid()`, returns user profile and permissions.
     * Returns structured payload: `{ app_user_id, email, full_name, is_root_admin, roles, permissions }`.
     * Revokes execute from `public` and `anon`; grants execute to `authenticated`, `postgres`, `service_role`.
2. Implement typed application command wrapper in `web/src/lib/auth/internal.ts` using the Task-004 command runner.
3. Add automated tests under `web/src/__tests__/internal-provisioning.test.ts` proving all 7 outcomes:
   - Unauthenticated caller -> `UNAUTHENTICATED`.
   - Non-EIU email domain -> `FORBIDDEN`.
   - Unlisted email -> `NOT_FOUND`.
   - Inactive user -> `USER_INACTIVE`.
   - Rebind attempt with different auth_user_id -> `IDENTITY_REBIND_FORBIDDEN`.
   - First-time binding -> successful bind, increments version_no, returns roles/permissions.
   - Subsequent login -> idempotent success.
4. Execute unlinked disposable local clean migration replay in a temporary directory outside git with SQL assertion suite proving all 7 outcomes.
5. Update project-control records (`EVIDENCE_INDEX.yaml`, `CURRENT_STATE.md`, `TASK_REGISTRY.yaml`, and track this prompt) with status `REVIEW` (pending independent review).
6. Commit all changes cleanly on `oanhpham-kobe/TASK-S01-002-google-provisioning`.

### Non-Goals
- Do NOT mark TASK-S01-002 as `DONE` in this commit. Per `TASK_EXECUTION_LIFECYCLE.md` and `REVIEWER_CONTRACT.md`, the Executor records `status: REVIEW`; the `DONE` transition is reserved for the Planner after an independent implementation review PASS.
- Do NOT implement Candidate Email OTP provisioning (that belongs to TASK-S01-003).
- Do NOT implement full login UI pages or auth callback endpoints (that belongs to TASK-S01-004 and TASK-S01-005).
- Do NOT deploy to Vercel or mutate external databases (`--linked` is forbidden).
- Do NOT modify tracked `supabase/config.toml` in the task worktree.
- Do NOT commit `.env.local` or any secrets/keys.

---

## 2. Canonical Source References

- `recruitment_webapp/review_pack/12_IMPLEMENTATION_NOTES_VERCEL_SUPABASE.md` (§Auth: Internal Google Workspace OAuth only, @eiu.edu.vn, internal first-login binding is an authenticated transactional provisioning command)
- `recruitment_webapp/review_pack/37_BACKEND_COMMAND_CONTRACTS.md` (§2 Core error codes, §3 Internal identity and first-login provisioning)
- `recruitment_webapp/review_pack/39_SECURITY_RLS_MATRIX.md` (§Identity helpers, §Read/Write matrix)
- `recruitment_webapp/review_pack/40_DATABASE_INVARIANTS.md` (§app_users invariants, §rebind invariants)

---

## 3. Implementation Specification

### 3.1 Migration File: `supabase/migrations/20260905040000_internal_user_provisioning.sql`

```sql
-- Transactional provisioning function
create or replace function public.provision_internal_user_identity()
returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
  v_auth_uid uuid;
  v_auth_email text;
  v_user record;
  v_roles text[];
  v_permissions text[];
begin
  -- 1. Authenticate
  v_auth_uid := auth.uid();
  if v_auth_uid is null then
    return jsonb_build_object('success', false, 'error_code', 'UNAUTHENTICATED', 'message', 'Authentication required');
  end if;

  -- Read email from auth.jwt() or auth.users
  v_auth_email := lower(coalesce(
    auth.jwt() ->> 'email',
    (select email from auth.users where id = v_auth_uid)
  ));

  if v_auth_email is null or v_auth_email = '' then
    return jsonb_build_object('success', false, 'error_code', 'UNAUTHENTICATED', 'message', 'Verified email required');
  end if;

  -- 2. Domain check
  if v_auth_email !~ '^[^@[:space:]]+@eiu\.edu\.vn$' then
    return jsonb_build_object('success', false, 'error_code', 'FORBIDDEN', 'message', 'Only @eiu.edu.vn Google Workspace accounts are permitted');
  end if;

  -- 3. Lookup pre-seeded/invited user
  select * into v_user
  from public.app_users
  where lower(email::text) = v_auth_email;

  if not found then
    return jsonb_build_object('success', false, 'error_code', 'NOT_FOUND', 'message', 'User account not found in internal directory');
  end if;

  -- 4. Active check
  if not v_user.is_active then
    return jsonb_build_object('success', false, 'error_code', 'USER_INACTIVE', 'message', 'User account is inactive');
  end if;

  -- 5. Rebind defense
  if v_user.auth_user_id is not null and v_user.auth_user_id <> v_auth_uid then
    return jsonb_build_object('success', false, 'error_code', 'IDENTITY_REBIND_FORBIDDEN', 'message', 'Account is already bound to a different identity');
  end if;

  -- 6. First-time bind
  if v_user.auth_user_id is null then
    update public.app_users
    set auth_user_id = v_auth_uid,
        updated_at = now(),
        version_no = coalesce(version_no, 0) + 1
    where app_user_id = v_user.app_user_id;
  end if;

  -- 7. Collect roles and permissions
  select coalesce(array_agg(role_code), '{}') into v_roles
  from public.app_user_roles
  where app_user_id = v_user.app_user_id;

  select coalesce(array_agg(permission_code), '{}') into v_permissions
  from public.app_user_permissions
  where app_user_id = v_user.app_user_id;

  return jsonb_build_object(
    'success', true,
    'data', jsonb_build_object(
      'app_user_id', v_user.app_user_id,
      'auth_user_id', v_auth_uid,
      'email', v_user.email,
      'full_name', v_user.full_name,
      'is_root_admin', v_user.is_root_admin,
      'roles', v_roles,
      'permissions', v_permissions
    )
  );
end;
$$;

revoke all on function public.provision_internal_user_identity() from public, anon;
grant execute on function public.provision_internal_user_identity() to authenticated, postgres, service_role;
```

### 3.2 Application Interface (`web/src/lib/auth/internal.ts`)
- Implement `provisionInternalUserIdentity`:
  Invokes `supabase.rpc('provision_internal_user_identity')` via the Server Supabase client.
  Maps error codes to standard `CommandResult<InternalUserIdentity>`.

### 3.3 Unlinked Disposable Replay Verification
- Setup disposable temporary directory outside git with bash trap cleanup.
- Copy `config.toml` and `migrations/` only (assert no `.temp`).
- Configure non-conflicting 5642x ports and `project_id = "eiu-recruitment-replay"`.
- Run `npx supabase start` and `npx supabase db reset`.
- Execute SQL assertions testing:
  1. Anonymous call returns `UNAUTHENTICATED`.
  2. Non-EIU email returns `FORBIDDEN`.
  3. Unlisted email returns `NOT_FOUND`.
  4. Inactive user returns `USER_INACTIVE`.
  5. Rebind attempt returns `IDENTITY_REBIND_FORBIDDEN`.
  6. First-time bind succeeds and increments version_no.
  7. Subsequent login returns idempotent success.
- Clean teardown of disposable runtime.

---

## 4. Acceptance Criteria

1. Migration applies cleanly on top of existing migrations.
2. All 7 boundary assertions PASS in disposable replay verification with zero errors.
3. Disposable runtime cleanly stopped; zero residual containers or temp files.
4. `npm run typecheck`, `npm run lint`, `npm run build`, and `npm test` PASS.
5. Zero secrets or credentials committed.
6. `project_control/EVIDENCE_INDEX.yaml` updated under `PROVISION-001` with assertion results.
7. `project_control/CURRENT_STATE.md` and `project_control/TASK_REGISTRY.yaml` updated with `status: REVIEW` (pending independent review), with prompt SHA-256 bound.
8. Exactly one clean commit on `oanhpham-kobe/TASK-S01-002-google-provisioning`.
