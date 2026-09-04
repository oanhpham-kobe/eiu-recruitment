# EIU Recruitment — Executor Prompt
## TASK-S01-003 — Candidate Email OTP Identity Verification and Provisioning Command
### Prompt version: SLICE-01_TASK-003_v1

## 0. Execution Control

```text
SOURCE_BASELINE: Full Handover v1.17
SOURCE_SHA256: 0b39c3615dd5b34e998527a1d273e0b846458c7bd4170be46c9bb670bfcb3498
BUSINESS_STATUS: Business Logic Core v1.2 = FROZEN
TECHNICAL_STATUS: Technical Architecture v1.17 = TECHNICAL SPECIFICATION FROZEN
TASK_SCOPE: TASK-S01-003 Candidate Identity Provisioning Command Only
WORKTREE: D:/orca/recruitment/TASK-S01-003-candidate-provisioning
BRANCH: oanhpham-kobe/TASK-S01-003-candidate-provisioning
BASE_BRANCH: autonomy/continuous-integration-20260905-01
BASE_HEAD: d2412cc0d5175ca4b04100ac5c5b801454289637
```

---

## 1. Role & Boundary

You are the Coding Executor for:
```text
TASK-S01-003: Candidate Email OTP identity verification and provisioning command
```

### Scope & Principles
This task implements the **transactional Candidate OTP identity verification and provisioning command** per review pack 12, 37, and 40.
Candidate verified email identity is immutable; OTP provisioning ensures safe binding without duplicate candidates.

### Authorized Scope
The Executor is authorized to perform:
1. Create ordered migration file `supabase/migrations/20260905050000_candidate_provisioning.sql`:
   - Implement `public.provision_candidate_identity()`:
     * Runs with `SECURITY DEFINER SET search_path = ''`.
     * Validates authenticated caller (`auth.uid()`). If absent, returns `{ success: false, error_code: 'UNAUTHENTICATED', message: '...' }`.
     * Extracts verified email from `auth.jwt() ->> 'email'` or `auth.users`. If absent, returns `{ success: false, error_code: 'UNAUTHENTICATED', message: 'Verified email required' }`.
     * Normalizes email (`lower(trim(email))`).
     * Lookup by `auth_user_id = auth.uid()`:
       - If found: checks `is_active` (fails with `USER_INACTIVE` if false); returns candidate profile.
     * Fallback lookup by normalized `email`:
       - If found:
         - Checks `is_active` (fails with `USER_INACTIVE` if false).
         - Safe rebind: updates `auth_user_id := auth.uid()`, `updated_at := now()`, `version_no := version_no + 1`. Prevents creating duplicate Candidate when Auth ID changes.
         - Returns candidate profile.
       - If not found:
         - Inserts new `public.candidates` row: `auth_user_id := auth.uid()`, `email := normalized_email`, `is_active := true`, `version_no := 1`.
         - Returns candidate profile.
     * Returns structured payload: `{ candidate_id, auth_user_id, email, current_full_name, current_phone, is_active }`.
     * Revokes execute from `public` and `anon`; grants execute to `authenticated`, `postgres`, `service_role`.
2. Implement typed application command wrapper in `web/src/lib/auth/candidate.ts` using the Task-004 command runner.
3. Add automated tests under `web/src/__tests__/candidate-provisioning.test.ts` proving all boundary outcomes:
   - Unauthenticated caller -> `UNAUTHENTICATED`.
   - Missing verified email -> `UNAUTHENTICATED`.
   - Inactive candidate -> `USER_INACTIVE`.
   - First-time new candidate registration -> creates candidate row, returns profile.
   - Subsequent login with same auth_user_id -> idempotent success without extra version increments.
   - Recreated auth session with same verified email -> safe rebind updates auth_user_id, increments version_no, avoids duplicate candidate.
4. Execute unlinked disposable local clean migration replay in a temporary directory outside git with SQL assertion suite proving all boundary cases.
5. Update project-control records (`EVIDENCE_INDEX.yaml`, `CURRENT_STATE.md`, `TASK_REGISTRY.yaml`, and track this prompt) with status `REVIEW` (pending independent review).
6. Commit all changes cleanly on `oanhpham-kobe/TASK-S01-003-candidate-provisioning`.

### Non-Goals
- Do NOT mark TASK-S01-003 as `DONE` in this commit. Per `TASK_EXECUTION_LIFECYCLE.md` and `REVIEWER_CONTRACT.md`, the Executor records `status: REVIEW`; the `DONE` transition is reserved for the Planner after an independent implementation review PASS.
- Do NOT implement Candidate form submission or document upload (that belongs to Slice 02).
- Do NOT implement full login UI pages or auth callback endpoints (that belongs to TASK-S01-004 and TASK-S01-005).
- Do NOT deploy to Vercel or mutate external databases (`--linked` is forbidden).
- Do NOT modify tracked `supabase/config.toml` in the task worktree.
- Do NOT commit `.env.local` or any secrets/keys.

---

## 2. Canonical Source References

- `recruitment_webapp/review_pack/12_IMPLEMENTATION_NOTES_VERCEL_SUPABASE.md` (§Auth: Candidate verified email identity; email immutable; Candidate production auth method: Email OTP code)
- `recruitment_webapp/review_pack/37_BACKEND_COMMAND_CONTRACTS.md` (§2 Core error codes, §3 provision_candidate_identity())
- `recruitment_webapp/review_pack/39_SECURITY_RLS_MATRIX.md` (§Identity helpers, §Read/Write matrix)
- `recruitment_webapp/review_pack/40_DATABASE_INVARIANTS.md` (§Candidate invariants, §Safe rebind)

---

## 3. Implementation Specification

### 3.1 Migration File: `supabase/migrations/20260905050000_candidate_provisioning.sql`

```sql
-- Transactional candidate provisioning function
create or replace function public.provision_candidate_identity()
returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
  v_auth_uid uuid;
  v_auth_email text;
  v_norm_email text;
  v_cand record;
begin
  -- 1. Authenticate
  v_auth_uid := auth.uid();
  if v_auth_uid is null then
    return jsonb_build_object('success', false, 'error_code', 'UNAUTHENTICATED', 'message', 'Authentication required');
  end if;

  -- 2. Read email
  v_auth_email := coalesce(
    auth.jwt() ->> 'email',
    (select email from auth.users where id = v_auth_uid)
  );

  if v_auth_email is null or trim(v_auth_email) = '' then
    return jsonb_build_object('success', false, 'error_code', 'UNAUTHENTICATED', 'message', 'Verified email required');
  end if;

  v_norm_email := lower(trim(v_auth_email));

  -- 3. Lookup by auth_user_id
  select * into v_cand
  from public.candidates
  where auth_user_id = v_auth_uid;

  if found then
    if not v_cand.is_active then
      return jsonb_build_object('success', false, 'error_code', 'USER_INACTIVE', 'message', 'Candidate account is inactive');
    end if;

    return jsonb_build_object(
      'success', true,
      'data', jsonb_build_object(
        'candidate_id', v_cand.candidate_id,
        'auth_user_id', v_cand.auth_user_id,
        'email', v_cand.email,
        'current_full_name', v_cand.current_full_name,
        'current_phone', v_cand.current_phone,
        'is_active', v_cand.is_active
      )
    );
  end if;

  -- 4. Fallback lookup by normalized email
  select * into v_cand
  from public.candidates
  where email = v_norm_email::extensions.citext;

  if found then
    if not v_cand.is_active then
      return jsonb_build_object('success', false, 'error_code', 'USER_INACTIVE', 'message', 'Candidate account is inactive');
    end if;

    -- Safe rebind
    update public.candidates
    set auth_user_id = v_auth_uid,
        updated_at = now(),
        version_no = coalesce(version_no, 0) + 1
    where candidate_id = v_cand.candidate_id
    returning * into v_cand;

    return jsonb_build_object(
      'success', true,
      'data', jsonb_build_object(
        'candidate_id', v_cand.candidate_id,
        'auth_user_id', v_cand.auth_user_id,
        'email', v_cand.email,
        'current_full_name', v_cand.current_full_name,
        'current_phone', v_cand.current_phone,
        'is_active', v_cand.is_active
      )
    );
  end if;

  -- 5. Create new candidate
  insert into public.candidates (
    auth_user_id,
    email,
    is_active,
    version_no
  ) values (
    v_auth_uid,
    v_norm_email::extensions.citext,
    true,
    1
  ) returning * into v_cand;

  return jsonb_build_object(
    'success', true,
    'data', jsonb_build_object(
      'candidate_id', v_cand.candidate_id,
      'auth_user_id', v_cand.auth_user_id,
      'email', v_cand.email,
      'current_full_name', v_cand.current_full_name,
      'current_phone', v_cand.current_phone,
      'is_active', v_cand.is_active
    )
  );
end;
$$;

revoke all on function public.provision_candidate_identity() from public, anon;
grant execute on function public.provision_candidate_identity() to authenticated, postgres, service_role;
```

### 3.2 Application Interface (`web/src/lib/auth/candidate.ts`)
- Implement `provisionCandidateIdentity`:
  Invokes `supabase.rpc('provision_candidate_identity')` via the Server Supabase client.
  Maps error codes to standard `CommandResult<CandidateIdentity>`.

### 3.3 Unlinked Disposable Replay Verification
- Setup disposable temporary directory outside git with bash trap cleanup.
- Copy `config.toml` and `migrations/` only (assert no `.temp`).
- Configure non-conflicting 5642x ports and `project_id = "eiu-recruitment-replay"`.
- Run `npx supabase start` and `npx supabase db reset`.
- Execute SQL assertions testing:
  1. Anonymous call returns `UNAUTHENTICATED`.
  2. Missing email returns `UNAUTHENTICATED`.
  3. Inactive candidate returns `USER_INACTIVE`.
  4. New candidate created on first OTP login.
  5. Subsequent login returns idempotent success without version bump.
  6. Rebind on recreated auth session with same email updates `auth_user_id` and increments `version_no`.
- Clean teardown of disposable runtime.

---

## 4. Acceptance Criteria

1. Migration applies cleanly on top of existing migrations.
2. All 6 boundary assertions PASS in disposable replay verification with zero errors.
3. Disposable runtime cleanly stopped; zero residual containers or temp files.
4. `npm run typecheck`, `npm run lint`, `npm run build`, and `npm test` PASS.
5. Zero secrets or credentials committed.
6. `project_control/EVIDENCE_INDEX.yaml` updated under `CAND-PROVISION-001` with assertion results.
7. `project_control/CURRENT_STATE.md` and `project_control/TASK_REGISTRY.yaml` updated with `status: REVIEW` (pending independent review), with prompt SHA-256 bound.
8. Exactly one clean commit on `oanhpham-kobe/TASK-S01-003-candidate-provisioning`.
