# TASK-S06-002 — Independent Prompt & Source Reconciliation Review Handoff

## Review identity

- WORK_ID: `S06-002-PROMPT-REVIEW-001`
- REVIEW_TYPE: `PROMPT_SOURCE_RECONCILIATION`
- REPOSITORY: `oanhpham-kobe/eiu-recruitment`
- INTEGRATION_BRANCH: `autonomy/continuous-integration-20260905-01`
- REVIEWED_SHA: `f757e76f3f97077c608dab29bad45b8bd2126dc3`
- PROMPT: `project_control/prompts/SLICE-06_TASK-002_v1.md`
- REVIEWER: `eiu-reviewer` (read-only)

Review the exact prompt artifact and repository sources at the exact reviewed SHA. Do not review a moving branch tip as a substitute for `f757e76f3f97077c608dab29bad45b8bd2126dc3`.

## Canonical source authority

Read the current versions at `f757e76f3f97077c608dab29bad45b8bd2126dc3` of:

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
15. accepted migrations/tests on `f757e76f3f97077c608dab29bad45b8bd2126dc3`, especially Slice-01 identity/provisioning and accepted Application/Interview lifecycle contracts.

## Accepted prerequisites that must not be silently reopened

- TASK-S06-001 accepted at `59be9b2c92906065b8e4baa902fcec1d4cbefa12` / `checkpoint/S06-001-accepted-001`.
- Accepted identity/auth tables, Root uniqueness, direct-DML revokes and authorization helpers from Slice 01.
- Accepted Application-owner and Interview-participant/resource concurrency/business behavior from later slices.
- Accepted audit, idempotency and optimistic-concurrency primitives.

## Required review scope

Assess whether the prompt is sufficient, internally consistent and canonically faithful before any implementation begins. In particular inspect:

1. **Scope split** — backend/security prerequisite only; no Users/Permissions UI, RBAC redesign, ordinary Root break-glass RPC, deployment, connected Supabase application, or main mutation.
2. **First Google login reconciliation** — accepted Slice-01 bind path is preserved/repaired rather than duplicated; current canonical Google-provider + confirmed/verified EIU email proof is explicit; user-editable metadata is not trusted for authorization/security identity.
3. **Bound identity change** — Root-only for already-bound non-Root users, collision/takeover safe, Root identity excluded to break-glass, no secret exposure or false cross-system atomicity claim.
4. **Permission-detail visibility** — non-root directory management gets only minimum directory/lifecycle information and cannot enumerate another user's granular permissions/security binding; Root full admin and own-permission reads remain possible; inactive-user lifecycle management is not accidentally made impossible.
5. **Directory command boundaries** — create/update/Active semantics cannot mutate roles, permissions, Root state or bound identity through a business-profile command; optimistic concurrency is sufficient.
6. **HR role lifecycle** — Root-only assign/remove, Full HR default set and exclusions, Active target rules, role removal permission cleanup, historical preservation, Active Application owner safety.
7. **Granular permission dependencies** — Root-only grant/revoke, Root-only codes non-delegable, dependency graph enforced server-side, concurrency/idempotency behavior is explicit enough to avoid impossible states.
8. **Lifecycle concurrency** — deactivation/HR-role removal cannot race with new Active Application ownership or new/current non-elapsed resource-blocking Interview participation; prompt requires a shared deterministic serialization mechanism while preserving accepted lock order and avoiding deadlocks.
9. **RLS/ACL/SECURITY DEFINER safety** — no broad authenticated authorization, no direct DML widening, explicit execute ACLs, empty search path, safe views/projections, service-role/server authorization remains explicit.
10. **Idempotency/audit/errors** — replay never substitutes for authorization/stale checks, audit is same trusted boundary, stable errors and no raw internal leakage.
11. **Regression sufficiency** — tests cover target classes, races, first-bind competition, identity takeover, visibility, direct DML/ACLs and directly affected accepted Application/Interview/Auth/S06 behavior.
12. **Source reopening** — determine whether any real canonical contradiction requires source reopening. Do not request source reopening for ordinary implementation difficulty.

## Known producer reconciliation observations

These are observations to verify, not findings the reviewer must accept without checking:

- Accepted Slice-01 `public.provision_internal_user_identity()` already has useful row locking/domain/Active/conflicting-bind behavior but appears weaker than current canonical source on explicit Google-provider + confirmed-email proof.
- Accepted Slice-01 permission-read policy appears broader than current canonical permission-detail visibility because directory read can expose another user's granular permission rows.
- User lifecycle must compose with accepted Application owner and Interview participant/resource contracts; UI-only checks are insufficient under concurrent writes.

## Required structured verdict

Return the complete result in this structure:

```text
WORK_ID: S06-002-PROMPT-REVIEW-001
REVIEWED_REPOSITORY: oanhpham-kobe/eiu-recruitment
REVIEWED_BRANCH: autonomy/continuous-integration-20260905-01
REVIEWED_SHA: f757e76f3f97077c608dab29bad45b8bd2126dc3
REVIEW_TYPE: PROMPT_SOURCE_RECONCILIATION
VERDICT: PASS | BLOCKING_REPAIR | OWNER_DECISION_REQUIRED
SOURCE_REOPEN_REQUIRED: true | false

BLOCKING_FINDINGS:
- ... or None.

NON_BLOCKING_OBSERVATIONS:
- ... or None.

SOURCE_RECONCILIATION_ASSESSMENT:
- ...

SECURITY_AUTHORIZATION_ASSESSMENT:
- ...

CONCURRENCY_LIFECYCLE_ASSESSMENT:
- ...

TEST_ACCEPTANCE_ASSESSMENT:
- ...

SCOPE_GOVERNANCE_ASSESSMENT:
- ...

ACCEPTANCE_STATEMENT:
- State whether `project_control/prompts/SLICE-06_TASK-002_v1.md` at exact SHA `f757e76f3f97077c608dab29bad45b8bd2126dc3` is safe to release for implementation without canonical-source reopening.

EVIDENCE_PERSISTENCE:
- GitHub-visible evidence coordinates if OMP main persists them, otherwise UNAVAILABLE.
```

## Evidence persistence

Reviewer itself stays read-only. OMP main owns persistence. If GitHub-visible review evidence is persisted, use a non-candidate evidence branch such as `review/S06-002-PROMPT-f757e76-v1` and an artifact such as `project_control/reviews/S06_002_PROMPT_REVIEW_f757e76_v1.md`. Do not mutate the reviewed target to persist evidence.

## Do-not-cross boundaries

- Do not implement or repair product/database code in this review.
- Do not move integration/task/checkpoint refs from the reviewer.
- Do not push/merge `main`.
- Do not deploy Vercel.
- Do not apply migrations to connected Supabase.
- Do not treat this transport handoff as review evidence by itself.
