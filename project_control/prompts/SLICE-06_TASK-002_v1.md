# SLICE-06 / TASK-S06-002 — Internal User Directory, HR RBAC & Identity Lifecycle Trusted Contracts

## Task identity

- TASK_ID: `TASK-S06-002`
- SLICE: `SLICE-06 — Master Data / Users & Permissions`
- TYPE: shared security/backend contract prerequisite
- EXECUTION_MODE: `AUTONOMOUS`
- IMPLEMENTATION_STATUS: `PLANNED_PENDING_INDEPENDENT_PROMPT_REVIEW`
- SOURCE_REOPEN_EXPECTATION: `false` unless a concrete contradiction in current canonical source is proven.

## Objective

Implement the Phase-1 trusted backend/security contract for Internal User directory lifecycle, HR role and granular permission administration, safe Internal Google identity provisioning/rebinding, and the concurrency/authorization safeguards needed by later Users & Permissions management UI.

This is a backend/security task. It must not build the Users & Permissions management page, redesign RBAC, convert Root break-glass recovery into a normal app action, or mutate canonical Product/Business/Design source merely to simplify implementation.

## Canonical authority

Read and reconcile at the exact implementation baseline before coding:

1. `recruitment_webapp/review_pack/02_ROLES_PERMISSIONS_AND_NAVIGATION.md`
2. `recruitment_webapp/review_pack/08_DATA_MODEL_AND_FIELD_DICTIONARY.md`
3. `recruitment_webapp/review_pack/13_ACCEPTANCE_CRITERIA_AND_TEST_CASES.md`
4. `recruitment_webapp/review_pack/37_BACKEND_COMMAND_CONTRACTS.md`
5. `recruitment_webapp/review_pack/39_SECURITY_RLS_MATRIX.md`
6. `recruitment_webapp/review_pack/40_DATABASE_INVARIANTS.md`
7. `recruitment_webapp/review_pack/46_AUTH_IDENTITY_MODEL.md`
8. `recruitment_webapp/review_pack/55_COMMAND_COVERAGE_MATRIX.md`
9. `recruitment_webapp/review_pack/59_RLS_POLICY_BLUEPRINT.md`
10. `recruitment_webapp/review_pack/61_ROOT_ADMIN_BREAK_GLASS_RECOVERY.md`
11. `recruitment_webapp/review_pack/73_DOMAIN_GLOSSARY_AND_CANONICAL_PREDICATES.md`
12. `recruitment_webapp/review_pack/100_TECHNICAL_PRECODE_GATE_V1_18.md`
13. `recruitment_webapp/review_pack/command_registry.yaml`
14. `recruitment_webapp/review_pack/database_schema.sql`
15. Current accepted Supabase migrations/tests and directly affected server adapters on the exact implementation baseline.

Business Logic Core v1.2 and Technical Architecture v1.18 remain frozen. Skills/framework documentation are implementation guidance only; canonical project sources remain business authority.

## Accepted prerequisites / append-only repair rule

Consume accepted implementation rather than recreating it:

- Slice-01 identity schema: `app_users`, `app_user_roles`, `permissions`, `app_user_permissions`, `permission_dependencies`, private authorization helpers, direct-DML revokes, Root uniqueness.
- Slice-01 Internal first-login provisioning implementation.
- Accepted Application owner, Interview participant/resource, audit, optimistic-concurrency, idempotency and security helpers from later slices.
- Accepted S06-001 Master Data lifecycle/history contract for organizational/master references.

This task is append-only over accepted migration history:

- do not edit old accepted migrations;
- do not fork `private.current_app_user_id()`, `private.is_root_admin()`, or `private.has_permission()` into incompatible authorization systems;
- do not weaken existing direct-DML revokes, RLS, grants, audit, locking, idempotency, or accepted Application/Interview invariants;
- repair an accepted prerequisite only when current canonical source proves a concrete mismatch, and keep the repair narrowly scoped.

## Producer source reconciliation — known mismatches to resolve, not ignore

The implementation baseline must be inspected directly. At planning time, two accepted Slice-01 surfaces are known to require reconciliation against current canonical source:

### 1. Internal Google first-login proof is weaker than current canonical contract

Accepted `public.provision_internal_user_identity()` already provides useful row locking, EIU-domain validation, Active allowlist lookup and conflicting-bind rejection. Preserve those accepted strengths.

Current canonical source additionally requires first-login provisioning to prove:

- the authenticated identity is a Google identity;
- the email is verified/confirmed by the Auth system;
- the normalized email is `@eiu.edu.vn`;
- the matching `app_users` row is Active and unbound;
- the current Auth ID is not already bound elsewhere;
- the bind is atomic and audited;
- if the row is already bound to a different Auth identity, reject and require Root-only recovery/rebind; never auto-rebind.

Do not use user-editable `user_metadata` for authorization or identity proof. Use current Supabase-supported server/Auth evidence. Current Supabase documentation identifies provider information in `app_metadata` / Auth identities and confirmed-email state on the Auth user; verify exact available claims/schema against the pinned project/runtime before implementation.

Do not directly mutate Supabase Auth internals merely to satisfy the contract. If a framework-supported Auth admin/server action is required, keep secrets server-only and preserve truthful transaction/rollback semantics rather than pretending an external Auth API call is part of a PostgreSQL transaction.

### 2. Permission-detail visibility is broader than current canonical source allows

Current canonical source states:

- Root may view every user's granular effective permissions;
- a non-root `users.directory_manage` / directory-management user may view the directory/lifecycle fields needed for management, including protected-role state needed to decide allowed lifecycle actions;
- a non-root user must not gain another user's granular effective-permission list merely from directory read/manage permission;
- a non-root user may view their own effective permissions.

Inspect accepted `app_user_permissions`/directory read policies and all existing consumers. Tighten the minimum surface without breaking accepted legitimate participant/user selectors. Prefer a safe projection/RPC where whole-row table exposure would reveal security identity or permission details unnecessarily.

A directory manager must still be able to locate/manage inactive non-Root users where canonical lifecycle permits reactivation. Do not solve this by broadly exposing security identity fields or all granular permissions.

## Supabase implementation guidance

Before implementation, use the current Supabase skill and current Supabase documentation/changelog for Auth/RLS/function behavior that may have changed. At minimum preserve these platform-specific safety rules:

- no `service_role`/secret key in browser code;
- no security-sensitive authorization from user-editable `user_metadata`;
- every exposed `public` business table remains RLS-protected;
- `SECURITY DEFINER` is used only where justified, with `SET search_path = ''`, fully qualified references, explicit auth/authorization checks, and explicit execute ACLs;
- newly created functions receive explicit `REVOKE ... FROM PUBLIC, anon` before intended grants;
- do not use broad `TO authenticated` as authorization by itself;
- views exposed to untrusted roles must not silently bypass RLS;
- run repository-supported DB security/advisor checks before candidate completion.

## In-scope trusted command families

Implement/reconcile the canonical Internal User/RBAC commands below. Exact SQL function signatures may follow established repository conventions, but public behavior must remain stable and explicit.

### Directory lifecycle

- `create_internal_user(...)`
- `update_internal_user_directory(...)`
- `set_internal_user_active(...)`

### HR role / permission administration

- `assign_hr_role_with_defaults(...)`
- `remove_hr_role(...)`
- `grant_hr_permission(...)`
- `revoke_hr_permission(...)`

### Internal identity

- canonical first-Google-login provisioning behavior (`provision_internal_identity_on_first_google_login()` semantics), reconciled with the accepted Slice-01 function without creating two divergent bind paths;
- `change_internal_user_identity(...)` for already-bound **non-Root** users, Root-only in Phase 1.

Root Admin break-glass identity recovery remains the controlled operational path in `61_ROOT_ADMIN_BREAK_GLASS_RECOVERY.md`. It is not an ordinary application RPC/UI mutation in this task.

## Authorization and target-class rules

### Root Admin

- exactly one Root remains protected;
- Root has implicit application permissions through the accepted authorization helper;
- Root may not be ordinary-deactivated, demoted, hard-deleted, or identity-rebound through normal directory/security commands;
- Root still obeys data-integrity/concurrency safety guards;
- Root identity recovery remains break-glass only.

### Directory manager

An Active Internal User with effective `users.directory_manage` may:

- create a normal Internal User directory row;
- edit allowed business profile fields;
- correct an `@eiu.edu.vn` email typo **only while `auth_user_id IS NULL`**;
- Active/Inactive a **non-HR, non-Root** Internal User under the lifecycle guards below.

This permission must never grant:

- HR role mutation;
- granular permission mutation;
- Root state mutation;
- bound identity/email/Auth/provider mutation;
- another user's full granular permission list.

### Root-only administration

Only Root may:

- assign/remove HR role;
- grant/revoke granular HR permissions;
- rebind an already-bound non-Root Internal User identity.

The permission codes `users.identity_manage` and `users.permissions_manage` remain Root-only Phase-1 capabilities and must not become delegable HR permissions. `candidates.identity_manage` remains outside the default HR set and may only be explicitly delegated where the current canonical permission model allows it.

## Directory create semantics

`create_internal_user` must:

- authenticate and authorize at mutation time;
- normalize and validate an `@eiu.edu.vn` email;
- reject duplicate normalized email;
- create an unbound ordinary directory row (`auth_user_id = NULL`, non-Root, no HR role/permissions) unless the exact canonical source explicitly authorizes a stronger Root-only administrative variant;
- validate writable business profile fields and referenced Unit using accepted active-master rules;
- prevent client control of `is_root_admin`, Auth binding, role, or permission rows;
- create Active by canonical default;
- audit atomically;
- define repository-consistent retry/idempotency semantics.

## Directory update semantics

`update_internal_user_directory` must:

- require `users.directory_manage` or Root implicit permission;
- lock the target and enforce optimistic `expected_version_no` (or the exact accepted equivalent);
- allow only canonical directory/business profile fields;
- permit email typo correction only while target `auth_user_id IS NULL` and only to a valid normalized `@eiu.edu.vn` address not used by another Internal User/Auth binding;
- reject bound email/Auth/provider changes with a stable identity-protection error;
- reject attempts to alter role, granular permissions, Root state, or Active state through this profile command;
- preserve exact accepted user-history snapshots on Applications/Interview Participants;
- audit changed-field metadata without dumping unnecessary sensitive identity data;
- be idempotency/retry safe where the public command can be replayed.

## Active/Inactive lifecycle semantics

`set_internal_user_active(target_user_id, active, expected_version_no, ...)` must be race-safe, not merely UI-safe.

Target rules:

- non-root directory manager may change Active only for non-HR, non-Root targets;
- an HR-role target is Root-only;
- Root target is rejected with `ROOT_ADMIN_PROTECTED` (or the exact stable accepted equivalent);
- HR self-deactivation through normal UI/command is rejected;
- stale version rejects before lifecycle effects/audit.

Before `active=true -> false`, the trusted operation must prevent both stranding classes:

1. target is owner of any Active Application and the operation would leave it without an eligible Active HR/root owner;
2. target is a current Participant of any **non-elapsed `resource_blocking` Interview** and the operation would leave that current/future operational Interview with an inactive current Participant.

Canonical stable errors include the accepted owner/participant reassignment-required semantics. Fully elapsed historical participation must not block lifecycle recovery merely because history exists.

If the administrative action includes owner/participant reassignment, that reassignment and deactivation must be one trusted atomic operation. Browser code must not orchestrate a multi-write sequence and claim atomicity. If the command surface does not include a valid atomic reassignment plan, fail closed and require the prerequisite reassignment to be completed through its own accepted trusted action before retrying deactivation.

### Cross-command race closure

The final database contract must also prevent a concurrent writer from assigning a soon-to-be-inactive user as a new Active Application owner or new/current participant after the lifecycle command's safety check.

Reconcile with accepted Application/Interview lock order rather than introducing deadlocks. Use one deterministic shared serialization/eligibility mechanism across the lifecycle writer and directly affected owner/participant writers. Any minimal hardening of accepted owner/participant commands must preserve their already-accepted semantics and receive regression coverage.

## HR role lifecycle

### `assign_hr_role_with_defaults`

Root only. The operation must:

- require an Active eligible Internal User target;
- lock/serialize the target's security administration state;
- add the HR role;
- grant the canonical Full HR Permission Set and required prerequisites atomically;
- exclude Root-only/security-identity permissions and every permission explicitly excluded from the default HR set by canonical source;
- never change Root state or bound identity;
- audit the role/default-permission changes atomically;
- be retry/idempotency safe.

### `remove_hr_role`

Root only. Before role removal:

- serialize against concurrent owner assignment and permission administration for the target;
- block with `ACTIVE_APPLICATION_OWNER_REASSIGN_REQUIRED` when the target still owns Active Applications unless a canonical same-transaction reassignment plan moves every affected Active Application to an eligible Active HR/root;
- do not erase historical inactive ownership/snapshots;
- remove HR role and revoke HR-default/custom HR permissions according to the Phase-1 canonical contract;
- preserve Root-only protections;
- cause effective authorization to be re-evaluated on subsequent requests rather than trusting stale client state;
- audit atomically and remain retry/idempotency safe.

Removing HR role does not, by itself, erase the person's ordinary Internal User / Interviewer identity.

## Granular permission lifecycle

`grant_hr_permission` and `revoke_hr_permission` are Root-only and operate only on canonical delegable permission codes for an eligible HR target.

Requirements:

- serialize per target user so concurrent role removal/grant/revoke cannot commit an impossible state;
- enforce `permission_dependencies` server-side, never only in UI;
- granting an action permission must leave every prerequisite satisfied atomically; if the repository/canonical contract does not explicitly auto-grant prerequisites, reject with `INVALID_PERMISSION_DEPENDENCY` rather than inventing silent grants;
- revoking a prerequisite while a dependent permission remains must fail closed unless the explicit trusted operation atomically removes the dependent permissions required by canonical behavior;
- Root-only permission codes cannot be granted to HR;
- Full HR default assignment excludes security/recovery permissions that canonical source marks non-default;
- security audit is mandatory;
- replay/double-click must not create duplicate logical grants/audits.

## First Google login semantics

Reconcile the accepted Slice-01 function into one canonical bind path. Required behavior:

1. resolve authenticated Supabase Auth user;
2. prove current identity is Google according to current supported Auth evidence;
3. prove confirmed/verified email using current supported Auth evidence;
4. normalize email and require `@eiu.edu.vn`;
5. resolve exact Active allowlisted `app_users` row by normalized email under lock;
6. require `auth_user_id IS NULL` for first bind, except an exact already-bound-to-current-Auth replay may safely return the existing result;
7. require current Auth ID is not bound to another `app_users` row;
8. bind once, audit once, and return minimum-safe identity/authorization data;
9. if target row is bound to a different Auth ID, reject `IDENTITY_REBIND_FORBIDDEN`; never silently rebind;
10. inactive/no-allowlist/non-Google/unverified identity fails closed.

Do not rely on user-editable metadata for provider or verified-email proof. Do not introduce a second public bind command with divergent semantics merely to preserve an old function name; preserve compatibility through a safe wrapper/repair if needed.

## Bound non-Root identity change

`change_internal_user_identity` is Root-only, security-sensitive and must never target the Root Admin.

At minimum:

- lock the target Internal User;
- require target is already bound and non-Root;
- validate the replacement Auth identity using supported server/Auth evidence: Google provider, confirmed normalized `@eiu.edu.vn` email, expected exact Auth user ID;
- reject an Auth ID or email already bound/owned by another Internal User;
- prevent account takeover / cross-row rebinding;
- update the Internal User's canonical security identity binding coherently;
- ensure the old Auth ID no longer resolves to this Internal User after commit;
- never expose Auth admin credentials or provider tokens;
- write immutable security audit in the trusted administrative boundary;
- define truthful failure/rollback semantics if any required Auth-provider/admin action cannot participate in the same database transaction.

Root identity remains outside this command and follows the break-glass runbook.

## Read / RLS / data-minimization contract

Provide only the minimum read surfaces required by later Users & Permissions UI and accepted operational consumers.

Required visibility:

- Root: full directory plus roles/effective granular permissions needed for administration;
- non-root directory reader/manager: allowed directory/business/lifecycle data, including enough role/protected-state to know whether an Active toggle is allowed; management must be able to find eligible inactive users;
- non-root user: own effective permissions may be read where needed;
- Interviewer/contextual consumers: only the minimum identity snapshot/current selector fields already required by accepted Interview behavior;
- anonymous/candidate: no Internal User directory or permission administration surface.

Do not expose another user's `auth_user_id`, provider binding detail, full granular permissions, audit metadata, or other security identity data merely because the caller can manage directory business profile.

Inspect existing web/server consumers before narrowing an accepted table policy. If compatibility requires a dedicated projection/RPC, implement that minimum-safe contract and migrate directly affected consumers rather than keeping an over-broad table grant.

## Idempotency / retry contract

Reuse the accepted repository idempotency primitive where applicable; do not create a third incompatible replay store.

For retryable trusted mutations in this task:

- authorize before replay return;
- scope replay by authenticated actor + command + target identity (and other semantic discriminator where needed);
- fingerprint all meaning-changing normalized inputs, including expected versions and reassignment plans;
- same key/scope/fingerprint after committed success returns the stored safe result without a second mutation/audit/version effect;
- same key/scope with different fingerprint fails closed;
- different actor/command/target cannot replay another scope;
- concurrent duplicate requests serialize to one logical mutation;
- failed/rolled-back attempts do not create successful replay state;
- replay record, business/security mutation, and audit commit atomically where they share the database transaction.

Do not use idempotency as authorization, stale-version bypass, or identity-proof bypass.

## Audit and error behavior

Every successful security-sensitive mutation writes the canonical immutable security audit in the same trusted boundary as the state change where technically possible.

Audit actor, action, entity, changed field names/security event type, target identity IDs where needed, correlation/request metadata and reason where canonical; do not store tokens, secrets, raw provider credentials, or gratuitous PII snapshots.

Reuse stable errors where applicable, including:

- `UNAUTHENTICATED`
- `FORBIDDEN`
- `NOT_FOUND`
- `VALIDATION_ERROR`
- `STALE_VERSION`
- `ROOT_ADMIN_PROTECTED`
- `IDENTITY_REBIND_FORBIDDEN`
- `USER_INACTIVE`
- `INVALID_PERMISSION_DEPENDENCY`
- accepted owner/participant reassignment-required errors
- `IDEMPOTENCY_REPLAY` / repository-equivalent replay mismatch behavior.

Do not leak raw PostgreSQL/internal/Auth-provider errors to untrusted UI adapters.

## Test-first acceptance

Add focused SQL/server regression coverage before/with production logic. At minimum prove:

1. anon/Candidate/missing-permission denial for directory/RBAC mutations;
2. directory manager creates only an ordinary unbound non-Root non-HR user with valid unique EIU email;
3. duplicate/non-EIU/unknown-field/protected-field create attempts fail with no partial write/audit;
4. directory profile update obeys optimistic versioning and DTO allowlist;
5. unbound email typo correction succeeds; bound email/Auth/provider mutation through directory command fails;
6. non-root directory manager can Active/Inactive eligible non-HR user;
7. non-root cannot deactivate an HR target; Root cannot be deactivated; normal self-deactivation rule is deterministic;
8. Active Application owner deactivation/removal is blocked unless every affected active owner is safely reassigned under the accepted atomic rule;
9. non-elapsed `resource_blocking` current-Participant deactivation is blocked without safe remove/replace/reassignment; fully elapsed historical participation does not create a false permanent block;
10. concurrent deactivation vs new Active Application owner assignment cannot commit a stranded inactive owner;
11. concurrent deactivation vs add/re-add/current-participant activation cannot commit a resource-blocking Interview with an inactive current participant;
12. HR role assignment is Root-only, requires eligible Active target, grants canonical Full HR defaults/prerequisites, and excludes Root-only/non-default recovery permissions;
13. HR role removal is Root-only, preserves history, revokes canonical HR permissions, and races safely with owner assignment and permission changes;
14. granular grant/revoke is Root-only, rejects Root-only codes, enforces dependencies and concurrent consistency;
15. first Google login succeeds only for verified/confirmed Google + normalized EIU email + Active allowlist; non-Google/unverified/inactive/not-allowlisted users fail;
16. two competing first-login Auth identities for the same directory row serialize so at most one binding wins; conflicting bind rejects;
17. exact first-login replay does not duplicate bind/audit;
18. bound non-Root identity change is Root-only, collision-safe, takeover-safe, and makes old Auth mapping ineffective after commit;
19. Root identity change through ordinary command is rejected and break-glass remains separate;
20. non-root directory management can read the minimum inactive/active lifecycle surface but cannot enumerate another user's granular effective permissions/security binding; Root can administer full permission detail; own-permission read remains valid;
21. direct table DML remains denied to `anon`/`authenticated` for security-admin tables;
22. private/security helpers and all new `SECURITY DEFINER` functions have explicit safe ACLs, empty search path and qualified references;
23. inactive Internal User cannot regain authorization through stale client assumptions; accepted authorization helpers remain Active-gated;
24. idempotency replay/mismatch/scope/concurrent-duplicate/rollback behavior is covered for every retryable command family added here;
25. accepted Application owner, Interview participant/resource, first-login, report, Master Data and existing security regressions still pass after zero-state replay.

Where local SQL fixtures cannot reproduce a hosted Auth-provider signal exactly, keep production checks real and add the strongest deterministic fixture/helper-level coverage possible. Do not weaken production Google/verified-email proof merely to make local tests convenient.

## Verification

Use impact-selected verification during implementation/repair, then a fresh exact-candidate acceptance boundary:

- current Supabase changelog/docs check for Auth/RLS/function behavior used by the implementation;
- SQL/static security review;
- zero-state Supabase migration replay;
- new Internal User/RBAC/identity lifecycle regressions;
- directly crossed accepted Application owner and Interview participant/resource concurrency regressions;
- accepted first-login/auth and permission/RLS regressions;
- S06-001 and other directly affected database regressions;
- DB advisors/security checks supported by the repository/toolchain;
- web lint/typecheck/build/tests only if server/web consumer code changes;
- `git diff --check`;
- governance validation.

Do not claim a check as PASS unless it actually ran for the stated SHA/environment.

## Server adapter / UI boundary

If this task adds Next.js server adapters only to expose these trusted commands/read models to later UI, they must be `server-only`, validate DTOs, call the approved RPC/Auth admin boundary, map stable errors, and never perform direct multi-table business/security DML from browser code.

Do not build the Users & Permissions management page in TASK-S06-002.

## Non-goals

Do NOT implement in this task:

- Users & Permissions management UI/table/drawer;
- Master Data management UI;
- generic arbitrary-role or arbitrary-permission system redesign;
- a second Root Admin;
- ordinary UI/API for Root break-glass recovery;
- hard-delete Internal User as a normal HR command (unused Internal User cleanup remains MAINTENANCE_ONLY / Root-operated where canonical source allows it);
- Candidate identity recovery (`recover_candidate_email_identity`) except preserving any accepted prerequisite it depends on;
- production Vercel deployment;
- connected Supabase migration application;
- `main` mutation.

## Required producer handoff

Before independent implementation review, report:

- exact baseline and candidate SHA;
- exact changed files;
- source reconciliation decisions for accepted Slice-01 first-login and directory/permission read policies;
- current Supabase documentation/changelog checks used for provider/verified-email/RLS/function behavior;
- command/RLS/ACL/audit/idempotency design;
- concurrency design for user deactivation vs Application owner / Interview participant writers, including lock/serialization order and deadlock analysis;
- exact Root/HR/directory-manager target-class behavior;
- focused and broader verification evidence, including unexecuted checks;
- any accepted prerequisite minimally hardened and why;
- `SOURCE_REOPEN_REQUIRED` only if a genuine canonical contradiction remains.

The independent reviewer is `eiu-reviewer`. This high-risk shared security/auth contract is not eligible for downstream Users/Permissions UI consumption until exact-SHA independent review PASS, serialized integration/equivalence requirements, exact-SHA CI PASS, and immutable accepted checkpoint creation under repository governance.