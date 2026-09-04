# EIU Recruitment — Executor Prompt
## TASK-S01-001 — Identity/Auth Schema Migration: app_users, candidates, roles, permissions, auth mapping, and RLS
### Prompt version: SLICE-01_TASK-001_v1

## 0. Execution Control

```text
SOURCE_BASELINE: Full Handover v1.17
SOURCE_SHA256: 0b39c3615dd5b34e998527a1d273e0b846458c7bd4170be46c9bb670bfcb3498
BUSINESS_STATUS: Business Logic Core v1.2 = FROZEN
TECHNICAL_STATUS: Technical Architecture v1.17 = TECHNICAL SPECIFICATION FROZEN
TASK_SCOPE: TASK-S01-001 Identity & Authorization Schema Migration Only
WORKTREE: D:/orca/recruitment/TASK-S01-001-identity-schema
BRANCH: oanhpham-kobe/TASK-S01-001-identity-schema
BASE_BRANCH: autonomy/continuous-integration-20260905-01
BASE_HEAD: 5aba0e5291dfc4400ac75facf780109efea55546
```

---

## 1. Role & Boundary

You are the Coding Executor for:
```text
TASK-S01-001: Identity/Auth schema migration: app_users, candidates, roles, permissions, auth mapping, and RLS
```

### Scope & Principles
This is a **database schema and authorization foundation** task for SLICE-01 (*Identity / Auth / User Provisioning*).
Establish tables, constraints, identity mapping, security definer helpers, and RLS policies from canonical source.

### Authorized Scope
The Executor is authorized to perform:
1. Create ordered migration file `supabase/migrations/20260905030000_identity_schema.sql` implementing:
   - `public.organizational_units`
   - `public.app_users` (internal personnel, domain check `@eiu.edu.vn`, partial unique index `one_root_admin_uq`)
   - `public.app_user_roles` (`role_code in ('HR')`)
   - `public.permissions` (`permission_code`, `description`)
   - `public.app_user_permissions` (`app_user_id`, `permission_code`, `granted_by`, `granted_at`)
   - `public.permission_dependencies` (`permission_code`, `requires_permission_code`)
   - `public.candidates` (`candidate_id`, `auth_user_id`, `email`, inactive check constraint)
   - Triggers attaching `private.touch_version()` to `organizational_units`, `app_users`, `candidates`
   - Private security definer helpers with empty `search_path`:
     * `private.current_app_user_id() returns uuid`
     * `private.is_root_admin() returns boolean`
     * `private.has_permission(p_permission_code text) returns boolean`
     * `private.current_candidate_id() returns uuid`
   - Row Level Security (RLS) enabled on all identity tables with minimal-grant policies.
2. Execute unlinked disposable local clean migration replay in a temporary directory outside git:
   - Assert all tables, columns, constraints, triggers, and helpers created without error.
   - Assert RLS policies deny unauthorized access (`anon` denied, candidates isolated to own record, internal users isolated).
3. Update project-control records (`EVIDENCE_INDEX.yaml`, `CURRENT_STATE.md`, `TASK_REGISTRY.yaml`, and track this prompt) with status `REVIEW` (pending independent review).
4. Commit all changes cleanly on `oanhpham-kobe/TASK-S01-001-identity-schema`.

### Non-Goals
- Do NOT mark TASK-S01-001 as `DONE` in this commit. Per `TASK_EXECUTION_LIFECYCLE.md` and `REVIEWER_CONTRACT.md`, the Executor records `status: REVIEW`; the `DONE` transition is reserved for the Planner after an independent implementation review PASS.
- Do NOT implement application UI screens, Next.js route handlers, or OTP email sending (those belong to later tasks in Slice 01).
- Do NOT deploy to Vercel or mutate external linked databases (`--linked` is forbidden).
- Do NOT modify tracked `supabase/config.toml` in the task worktree.
- Do NOT commit `.env.local` or any secrets/keys.

---

## 2. Canonical Source References

- `recruitment_webapp/review_pack/database_schema.sql` (lines 30–80 organizational units; lines 163–208 app_users, roles, permissions; lines 213–230 candidates)
- `recruitment_webapp/review_pack/40_DATABASE_INVARIANTS.md` (§Identity invariants, §Root admin constraints, §Candidate constraints)
- `recruitment_webapp/review_pack/39_SECURITY_RLS_MATRIX.md` (§Identity helpers, §Read/Write matrix)
- `recruitment_webapp/review_pack/59_RLS_POLICY_BLUEPRINT.md` (§Candidate, §HR, §Internal identity, §Adversarial tests required)

---

## 3. Implementation Specification

### 3.1 Migration File: `supabase/migrations/20260905030000_identity_schema.sql`

1. **Organizational Units**:
   ```sql
   create table if not exists public.organizational_units (
     unit_id uuid primary key default gen_random_uuid(),
     code text unique,
     name_vi text not null,
     name_en text,
     is_active boolean not null default true,
     created_at timestamptz not null default now(),
     updated_at timestamptz not null default now(),
     version_no bigint not null default 1
   );
   ```

2. **Internal App Users**:
   ```sql
   create table if not exists public.app_users (
     app_user_id uuid primary key default gen_random_uuid(),
     auth_user_id uuid unique,
     email extensions.citext not null unique,
     full_name text not null,
     job_title text,
     unit_id uuid references public.organizational_units(unit_id) on delete restrict,
     is_active boolean not null default true,
     is_root_admin boolean not null default false,
     created_at timestamptz not null default now(),
     updated_at timestamptz not null default now(),
     version_no bigint not null default 1,
     constraint internal_email_domain_ck check (lower(email::text) ~ '^[^@[:space:]]+@eiu\.edu\.vn$')
   );

   create unique index if not exists one_root_admin_uq
     on public.app_users ((is_root_admin))
     where is_root_admin = true;
   ```

3. **User Roles & Permissions**:
   ```sql
   create table if not exists public.app_user_roles (
     app_user_id uuid not null references public.app_users(app_user_id) on delete restrict,
     role_code text not null check (role_code in ('HR')),
     created_at timestamptz not null default now(),
     primary key (app_user_id, role_code)
   );

   create table if not exists public.permissions (
     permission_code text primary key,
     description text not null
   );

   create table if not exists public.app_user_permissions (
     app_user_id uuid not null references public.app_users(app_user_id) on delete restrict,
     permission_code text not null references public.permissions(permission_code) on delete restrict,
     granted_by uuid references public.app_users(app_user_id) on delete restrict,
     granted_at timestamptz not null default now(),
     primary key (app_user_id, permission_code)
   );

   create table if not exists public.permission_dependencies (
     permission_code text not null references public.permissions(permission_code) on delete cascade,
     requires_permission_code text not null references public.permissions(permission_code) on delete cascade,
     primary key (permission_code, requires_permission_code),
     constraint permission_dependency_not_self_ck check (permission_code <> requires_permission_code)
   );
   ```

4. **Candidates Table**:
   ```sql
   create table if not exists public.candidates (
     candidate_id uuid primary key default gen_random_uuid(),
     auth_user_id uuid not null unique,
     email extensions.citext not null unique,
     current_full_name text,
     current_phone text,
     last_submission_at timestamptz,
     is_active boolean not null default true,
     inactive_at timestamptz,
     inactive_by uuid references public.app_users(app_user_id) on delete restrict,
     created_at timestamptz not null default now(),
     updated_at timestamptz not null default now(),
     version_no bigint not null default 1,
     constraint candidate_inactive_metadata_ck check (
       (is_active = true and inactive_at is null and inactive_by is null)
       or (is_active = false and inactive_at is not null and inactive_by is not null)
     )
   );
   ```

5. **Triggers**:
   Attach `private.touch_version()` trigger before update on `organizational_units`, `app_users`, and `candidates`.

6. **Private Identity Helpers**:
   Define in `private` schema with `SECURITY DEFINER SET search_path = ''`:
   - `private.current_app_user_id() returns uuid`:
     Looks up `app_user_id` from `public.app_users` where `auth_user_id = auth.uid()` and `is_active = true`.
   - `private.is_root_admin() returns boolean`:
     Returns true if `auth.uid()` matches an active `app_users` row with `is_root_admin = true`.
   - `private.has_permission(p_permission_code text) returns boolean`:
     Returns true if `private.is_root_admin()` is true, OR if `private.current_app_user_id()` has an active grant in `public.app_user_permissions`.
   - `private.current_candidate_id() returns uuid`:
     Looks up `candidate_id` from `public.candidates` where `auth_user_id = auth.uid()` and `is_active = true`.
   - Revoke execute from `public` and `anon`; grant execute to `authenticated`, `postgres`, `service_role`.

7. **Row Level Security (RLS)**:
   - Enable RLS on `organizational_units`, `app_users`, `app_user_roles`, `permissions`, `app_user_permissions`, `permission_dependencies`, `candidates`.
   - Revoke direct INSERT/UPDATE/DELETE from `anon` and `authenticated`.
   - SELECT Policies:
     - `app_users`: authenticated users can SELECT own record (`auth_user_id = auth.uid()`), or all active records if `private.has_permission('users.directory_read')`.
     - `candidates`: authenticated candidate can SELECT own record (`auth_user_id = auth.uid()`), or internal user if `private.has_permission('submissions.view')`.
     - `app_user_roles`, `app_user_permissions`: users can SELECT own roles and permissions, or if user has `users.directory_read`.
     - `organizational_units`, `permissions`, `permission_dependencies`: readable by authenticated internal users.

### 3.2 Unlinked Disposable Replay Verification

1. Create disposable temp directory with bash trap cleanup:
   - Copy only `config.toml` and `migrations/` from task worktree.
   - Assert `test ! -d $REPLAY_DIR/supabase/.temp`.
   - Configure non-conflicting 5642x ports and `project_id = "eiu-recruitment-replay"`.
2. Start and reset:
   - `npx supabase start > /dev/null 2>&1`
   - `npx supabase db reset`
3. Execute SQL assertions:
   - **Assertion A (Structure & Constraints)**: Verify all 7 tables exist; verify check constraints (`internal_email_domain_ck`, `one_root_admin_uq`, `candidate_inactive_metadata_ck`) reject violating inserts.
   - **Assertion B (Helpers)**: Verify `private.current_app_user_id`, `is_root_admin`, `has_permission`, `current_candidate_id` exist with `prosecdef = true` and empty search path.
   - **Assertion C (Triggers)**: Verify `touch_version` triggers increment `version_no` on update.
   - **Assertion D (RLS Denial & Isolation)**:
     * As `anon`: verify SELECT on `app_users` and `candidates` returns 0 rows.
     * As simulated candidate A: verify cannot SELECT candidate B record.
     * As simulated staff: verify cannot SELECT other staff records without permission.
4. Stop and delete disposable runtime cleanly.

---

## 4. Acceptance Criteria

1. Migration `supabase/migrations/20260905030000_identity_schema.sql` applies cleanly on top of foundation migration.
2. All 4 SQL assertion groups (Structure, Helpers, Triggers, RLS Denial) PASS with zero errors in disposable replay.
3. Disposable runtime cleanly stopped; zero residual containers or temp directories.
4. Tracked `supabase/config.toml` untouched.
5. Zero secrets or credentials committed.
6. `project_control/EVIDENCE_INDEX.yaml` updated under `IDENTITY-001` with assertion results.
7. `project_control/CURRENT_STATE.md` and `project_control/TASK_REGISTRY.yaml` updated with `status: REVIEW` (pending independent review), with prompt SHA-256 bound.
8. Exactly one clean commit on `oanhpham-kobe/TASK-S01-001-identity-schema`.
