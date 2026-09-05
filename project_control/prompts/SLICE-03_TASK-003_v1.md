# EIU Recruitment — Executor Prompt
## TASK-S03-003 — Bulk Submission status and bulk Application assignment transactional commands
### Prompt version: SLICE-03_TASK-003_v1

## 0. Execution Control

```text
SOURCE_BASELINE: Full Handover v1.17
SOURCE_SHA256: 0b39c3615dd5b34e998527a1d273e0b846458c7bd4170be46c9bb670bfcb3498
BUSINESS_STATUS: Business Logic Core v1.2 = FROZEN
TECHNICAL_STATUS: Technical Architecture v1.17 = TECHNICAL SPECIFICATION FROZEN
TASK_SCOPE: TASK-S03-003 Bulk Submission status and bulk Application assignment transactional commands Only
WORKTREE: D:/orca/recruitment/TASK-S03-003-bulk-commands
BRANCH: oanhpham-kobe/TASK-S03-003-bulk-commands
BASE_BRANCH: autonomy/continuous-integration-20260905-01
BASE_HEAD: resolve from the checked-out integration branch immediately before implementation; direct Git runtime wins
```

---

## 1. Governance & Compact Routing

```yaml
GOVERNANCE:
  pack_version: "1.1"
  SKILLS_REQUIRED:
    - supabase
    - supabase-postgres-best-practices
    - security-review
    - tdd
  SKILLS_RESOLVED:
    - supabase (.agents/skills/supabase)
    - supabase-postgres-best-practices (.agents/skills/supabase-postgres-best-practices)
    - security-review (.agents/skills/security-review)
    - tdd (.agents/skills/tdd)
  SKILLS_INTENDED_APPLICATION:
    - supabase: "secure Supabase RPC migrations, RLS/grants, server client command bindings, and local replay"
    - supabase-postgres-best-practices: "deterministic candidate/submission/application locking, short all-or-nothing transactions, durable idempotency"
    - security-review: "server-side authorization, untrusted batch-input validation, security-definer grant hardening, audit evidence"
    - tdd: "risk-based batch tests at command/RPC seams for atomicity, latest-row revalidation, stale versions, and authorization"
  GRAPH_ROUTE: DIRECT_SOURCE_LSP_ONLY
  GRAPH_ROUTE_REASON: "Localized batch RPCs and existing command wrappers have direct source contracts; no shared-symbol graph query is needed."
  PRINCIPLE_PROFILE: "BATCH_ATOMICITY_AND_LATEST_SUBMISSION_INTEGRITY"
  EVIDENCE_DELTA: "BULK-COMMANDS-001"
```

The executor MUST independently read every listed effective `SKILL.md` before dependent implementation and persist a post-execution `SKILL_USAGE` receipt under `TASK-S03-003.skill_usage` in `project_control/TASK_REGISTRY.yaml`, with `provider`, `availability`, `loaded`, `applied`, and concrete `applied_to` values. It MUST also persist `GRAPH_USAGE: { route: DIRECT_SOURCE_LSP_ONLY, graph_used: NO, reason: <localized direct-source/LSP reason> }` in `BULK-COMMANDS-001` under `project_control/EVIDENCE_INDEX.yaml`; the evidence entry MUST name direct source and LSP as the used discovery surfaces. Do not use the declarations above as runtime evidence.

---

## 2. Canonical Source References

- `recruitment_webapp/review_pack/37_BACKEND_COMMAND_CONTRACTS.md` (§15 bulk operations; `bulk_create_or_update_applications`; `bulk_set_latest_submission_manual_status`)
- `recruitment_webapp/review_pack/63_BATCH_OPERATION_SEMANTICS.md` (Phase-1 visible bulk action registry, named-command-only and ALL_OR_NOTHING rules)
- `recruitment_webapp/review_pack/13_ACCEPTANCE_CRITERIA_AND_TEST_CASES.md` (`AC-07`, `AC-12`, `AC-BULK-01`, `AC-STAT-MANUAL-READ-01`, `AC-STAT-MANUAL-NEW-01`, `AC-STAT-MANUAL-NOAPP-01`, `AC-STAT-INACTIVE-02`)
- `recruitment_webapp/review_pack/40_DATABASE_INVARIANTS.md` (manual state restriction and parent-submission locking)
- `recruitment_webapp/review_pack/55_COMMAND_COVERAGE_MATRIX.md` (named bulk status and application commands)
- `recruitment_webapp/review_pack/command_registry.yaml` (`bulk_create_or_update_applications`, `bulk_set_latest_submission_manual_status`)
- `recruitment_webapp/review_pack/database_schema.sql` (lines 665-724: authoritative audit and idempotency definitions)
- Existing implementation: `supabase/migrations/20260905100000_application_schema_and_status_commands.sql`, `supabase/migrations/20260905110000_application_lifecycle_commands.sql`, `web/src/lib/commands/submission-status.ts`, `web/src/lib/commands/application-lifecycle.ts`

---

## 3. Required Implementation

### 3.1 Migration: `supabase/migrations/20260905120000_bulk_submission_status_and_application_assignment.sql`

Add exactly two public trusted batch RPCs. Use `SECURITY DEFINER SET search_path = ''`, revoke execute from `public`/`anon`, and grant only the needed `authenticated`, `postgres`, and `service_role` roles. Each routine returns the established JSON envelope: `{ success, data? }` or `{ success: false, error_code, message }`.

#### A. Audit and idempotency prerequisites

The current repository migration chain has not yet materialized the canonical `activity_log`, `security_audit_log`, or `idempotency_records` tables. Add only the authoritative definitions needed by these two commands from `database_schema.sql` lines 665-724, including RLS enablement, no direct anonymous/authenticated table mutations, privileged grants, and their authoritative unique/index constraints. Do not create an alternative logging or idempotency model.

For each batch command:
- derive actor identity server-side from `auth.uid()` and the active `app_users` row;
- require a non-null caller-stable `idempotency_key`; TypeScript validates and forwards it unchanged, while SQL rejects an absent key with `VALIDATION_ERROR`;
- canonicalize the complete request into a deterministic `request_fingerprint` that includes the command, ordered selection, expected IDs/versions, target state, and common assignment fields;
- acquire a transaction-scoped advisory lock derived from `(actor_scope, command_type, idempotency_key)` before reading `idempotency_records`;
- if an existing successful record has the same fingerprint, return only its stored result; if it has a different fingerprint, return `VALIDATION_ERROR`; failed attempts leave no reservation because the transaction rolls back;
- persist the successful fingerprint and result together in the authoritative `result_payload`, along with all writes and audit records;
- never treat a client-supplied actor, status, or selection as authorized merely because the UI permits it.

#### B. `public.bulk_set_latest_submission_manual_status(...)`

Use a signature equivalent to:

```sql
public.bulk_set_latest_submission_manual_status(
  p_candidate_ids uuid[],
  p_status_code text,
  p_expected_latest_submission_ids uuid[],
  p_expected_versions bigint[],
  p_idempotency_key uuid
) returns jsonb
```

Requirements:

1. Authorization is `submissions.status` or Root Admin only. `submissions.view` alone is read-only. Do not add an HR-role bypass.
2. SQL rejects a null or empty selection; null arrays/elements; zero/non-positive expected versions; duplicate candidate IDs; unequal parallel-array lengths; and a null idempotency key with `VALIDATION_ERROR`. Only `NEW` and `READ` are valid manual targets.
3. Lock selected Candidate rows in ascending `candidate_id` order. Missing Candidates fail the whole batch with `NOT_FOUND`.
4. While holding Candidate locks, resolve each deterministic latest Submission using `submitted_at DESC, submission_id DESC` but do not yet lock it. Then lock all resolved Submission rows in one ascending `submission_id` pass and re-resolve/revalidate each Candidate's latest Submission while holding both locks. A missing latest Submission returns `NOT_FOUND`; any expected latest ID or version mismatch returns `STALE_VERSION`, with no committed subset.
5. Lock/check all resolved latest Submissions' active Applications in ascending `(submission_id, application_id)` order. Any active Application blocks either `NEW` or `READ` for that row with `INVALID_STATE`; no selected Candidate mutates. Candidate account active/inactive state alone must not block the batch.
6. Only after the entire selected set has passed preflight, update every resolved latest Submission status, increment each `version_no`, and set `updated_at = clock_timestamp()`.
7. Historical child Submissions are never a direct or indirect mutation target. This candidate-then-submission lock progression is the required cross-command order; `data.items` preserves input ordinality so caller/result pairing is unambiguous.
8. Insert one `activity_log` row per changed Submission with `entity_type = 'SUBMISSION'`, `entity_id = <changed submission_id>`, `action_code = 'BULK_MANUAL_STATUS_SET'`, `actor_app_user_id = <server-derived active actor>`, `request_id = p_idempotency_key`, `old_values = {\"status_code\": <old>, \"version_no\": <old>}`, and `new_values = {\"status_code\": <new>, \"version_no\": <new>}`. Insert exactly one `security_audit_log` batch event with `actor_auth_user_id = auth.uid()`, `actor_app_user_id = <server-derived active actor>`, `action_code = 'BULK_LATEST_SUBMISSION_STATUS'`, `entity_type = 'BATCH'`, `entity_id = p_idempotency_key`, `request_id = p_idempotency_key`, and `metadata = {\"request_fingerprint\": <fingerprint>, \"selected_candidate_ids\": [<input order>]}`.
9. Return an input-ordered `data.items` list containing `candidate_id`, `submission_id`, `status_code`, and new `version_no`, plus `count` and `idempotency_key`.

#### C. `public.bulk_create_or_update_applications(...)`

Use a common-assignment signature equivalent to:

```sql
public.bulk_create_or_update_applications(
  p_submission_ids uuid[],
  p_unit_id uuid,
  p_department_team_id uuid,
  p_position_id uuid,
  p_hr_owner_id uuid,
  p_idempotency_key uuid
) returns jsonb
```

Requirements:

1. Authorization requires both `applications.manage` and `submissions.view`, or Root Admin. Do not permit `applications.create` alone for the batch command.
2. `p_submission_ids`, `p_unit_id`, `p_position_id`, `p_hr_owner_id`, and `p_idempotency_key` are mandatory and non-null. `p_department_team_id` is the sole nullable common field. SQL rejects a null/empty submission array, null array elements, duplicate Submission IDs, missing required UUID fields, and a null idempotency key with `VALIDATION_ERROR`.
3. Lock and validate active common reference rows before selected Submissions in this fixed order: organizational Unit, optional Department Team, Position, then HR owner. Validate Unit/Team/Position hierarchy and active HR ownership while holding those locks, matching `create_or_update_application` semantics.
4. Lock all selected parent Submissions in ascending `submission_id` order; every input must name an exact existing Submission. There is no implicit latest-Submission selection.
5. Lock every selected durable Application identity in ascending `(submission_id, application_id)` order. An inactive exact duplicate returns `ALREADY_EXISTS_INACTIVE` and aborts the entire batch. An active duplicate updates only `hr_owner_id`, `version_no`, and `updated_at`; it MUST NOT rewrite identity fields or create a second Round 1. A new identity creates exactly one Application and default active Round 1 with `AVAILABLE` / `INTERVIEW_SCHEDULING` and blank demo topic.
6. Prevalidate every selected item before the first Application/Interview write; one invalid hierarchy, missing submission, or inactive duplicate rolls back every selected Application mutation. Deterministic reference/parent/identity locks and the durable unique index resolve concurrent competing assignment attempts; do not invent an expected-version input for this create/update contract.
7. Recalculate every affected parent Submission once before commit, after the Application mutations.
8. Insert one `activity_log` row per Application with `entity_type = 'APPLICATION'`, `entity_id = <changed application_id>`, `action_code = 'BULK_APPLICATION_ASSIGNMENT'`, `actor_app_user_id = <server-derived active actor>`, `request_id = p_idempotency_key`, `old_values = {\"hr_owner_id\": <old|null>, \"version_no\": <old|null>}`, and `new_values = {\"hr_owner_id\": <new>, \"version_no\": <new>, \"action\": \"CREATED\"|\"UPDATED\"}`. Insert exactly one `security_audit_log` batch event with `actor_auth_user_id = auth.uid()`, `actor_app_user_id = <server-derived active actor>`, `action_code = 'BULK_APPLICATION_ASSIGNMENT'`, `entity_type = 'BATCH'`, `entity_id = p_idempotency_key`, `request_id = p_idempotency_key`, and `metadata = {\"request_fingerprint\": <fingerprint>, \"selected_submission_ids\": [<input order>]}`.
9. Return input-ordered `data.items` containing `submission_id`, `application_id`, `action` (`CREATED` or `UPDATED`), `version_no`, and `round1_interview_id`, plus `count` and `idempotency_key`.

Do not call single-row RPCs in a loop from browser or TypeScript. SQL may reuse existing deterministic logic only if all preconditions are validated before the first write and all writes/audit/idempotency remain in one transaction.

### 3.2 Server command layer

Extend existing, closest command modules—`web/src/lib/commands/submission-status.ts` for bulk manual status and `web/src/lib/commands/application-lifecycle.ts` for bulk application assignment—using `createCommandRunner`.

- Define typed public inputs and data models; accept item objects at the TypeScript seam, require a caller-stable `idempotencyKey`, validate UUIDs, positive integer expected versions, non-empty selection, duplicate prevention, and allowed statuses, then map to the RPC arrays. `departmentTeamId` alone may be null for bulk assignment; `unitId`, `positionId`, and `hrOwnerId` are required.
- Resolve/authorize actors server-side. Enforce the exact required permission sets stated above; UI/role labels are not authorization.
- Map canonical RPC error codes to `CommandErrorCode`; add only missing domain error codes that the RPC can return.
- Preserve existing single-command APIs and semantics. No UI work, no browser loops, no relaxed single-command authorization, and no unrelated refactor.

### 3.3 Tests

Add behavior tests at the command/RPC boundary using existing test conventions. They must fail against missing/broken behavior and assert observable contract values, not source text. Cover at least:

1. Bulk latest `NEW`/`READ` updates all selected deterministic latest Submissions atomically and returns items in input order.
2. Any active Application in one selected latest Submission returns `INVALID_STATE` and commits none.
3. Missing latest Submission returns `NOT_FOUND`; expected latest ID or expected version mismatch returns `STALE_VERSION`; neither commits a subset.
4. Candidate inactive state does not independently block an otherwise eligible manual-status batch.
5. Historical Submission cannot be selected/mutated through the Candidate-level batch API.
6. Bulk common Application assignment creates an Application + default Round 1 for every exact selected Submission.
7. Active exact duplicates update owner/version only; inactive exact duplicate aborts the full batch with `ALREADY_EXISTS_INACTIVE`.
8. One invalid/missing submission or hierarchy error yields a single failure and no batch subset changes.
9. Positive exact permission paths execute both TypeScript commands and direct authenticated RPC calls: `submissions.status` for manual status, conjunction of `applications.manage` and `submissions.view` for bulk assignment, and Root Admin bypass. Authorization denial occurs before validation/execution for both layers, including these near misses: `submissions.view` without `submissions.status`, HR-role-only access, `applications.create` alone, `applications.manage` without `submissions.view`, and `submissions.view` without `applications.manage`. `anon`/`PUBLIC` direct execution is denied.
10. Same actor/command/idempotency key with an identical fingerprint returns stored success without repeated Application/Submission mutation or audit records; a different fingerprint returns `VALIDATION_ERROR`. Different actor or command scopes cannot replay another actor/command's stored result, and each selection/expected-ID/expected-version/target/common-field fingerprint component is material.
11. Direct-RPC invalid empty/null array, null element, duplicate IDs, unequal status parallel-array lengths, null expected-ID/version arrays or elements, invalid/null status, missing Candidate/latest Submission, null idempotency key, invalid expected version, and missing required bulk-assignment field cases return the required `VALIDATION_ERROR` or `NOT_FOUND`.
12. Assert exact audit persistence: one `activity_log` row per changed entity with its exact `entity_id`, and one `security_audit_log` batch event with the exact action code, server-derived actor identities, request ID, metadata keys, and value shapes above.
13. In disposable local replay, two overlapping bulk status calls submitted in opposite input orders and an overlapping bulk-status versus bulk-assignment call do not deadlock. Competing same-identity bulk assignments produce one durable Application and one Round 1 without duplicate identity rows.
14. Force a post-write failure (recalculation, audit insert, or idempotency-result persistence) in disposable replay and assert rollback of every Application, Interview, Submission status/version, audit row, and idempotency record in that batch.

### 3.4 Explicit non-goals

- No HR inbox UI, bulk toolbar, dialog, or browser-side mutation loop.
- No candidate lifecycle, interview, report, email, master-data, or reactivation command.
- No permissive RLS/grants, service-role browser code, production migration, or deployment.
- No changes to canonical source documents.

---

## 4. Acceptance & Verification Contract

1. `npm run typecheck` in `web/` passes with 0 errors.
2. `npm run lint` in `web/` passes with 0 errors.
3. `npm run build` in `web/` passes.
4. `npm run test` in `web/` passes, including all new batch tests.
5. Clean local migration replay passes in an unlinked disposable runtime; execute focused SQL assertions for both RPCs, all-or-nothing rollback, idempotency replay/fingerprint conflict, exact audit counts/metadata, direct-RPC validation, and default Round 1 creation.
6. Verify new public tables/RPCs have RLS/grants consistent with the canonical security boundary and no `PUBLIC` execution on security-definer functions.
7. Run secret scan and `git diff --check`.
8. Exactly one task implementation commit on `oanhpham-kobe/TASK-S03-003-bulk-commands`; no commit/push/merge/deploy outside the task branch.
