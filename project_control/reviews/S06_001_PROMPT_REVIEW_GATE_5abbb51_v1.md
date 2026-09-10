# TASK-S06-001 — Independent Pre-Implementation Prompt / Source Reconciliation Review Gate

## Review identity

- WORK_ID: `S06-001-PROMPT-REVIEW-001`
- REVIEW_TYPE: `PRE_IMPLEMENTATION_PROMPT_SOURCE_RECONCILIATION`
- REVIEWER: `eiu-reviewer`
- REPOSITORY: `oanhpham-kobe/eiu-recruitment`
- INTEGRATION_BRANCH: `autonomy/continuous-integration-20260905-01`
- EXACT_REVIEWED_SHA: `5abbb5181405e0f5a468176edd93db8226a3efd5`
- TARGET_PROMPT: `project_control/prompts/SLICE-06_TASK-001_v1.md`
- PRODUCER_RECONCILIATION: `project_control/reviews/S06_001_PROMPT_PRODUCER_RECONCILIATION_v1.md`
- EXPECTED_SOURCE_REOPEN: `false` unless a concrete canonical contradiction is proven.

Review the immutable SHA above. Do not substitute a later mutable integration HEAD.

## Context

Slice-05 is closed after:

- TASK-S05-001 accepted at `ef0bd9e534dec0cc85ef6503fbe0369eda56d555`;
- TASK-S05-002 accepted at `fe556dda76ebeda7107bcb9310cbaf338b30fc29`;
- Slice-05 composition review PASS on `60e1f425d920ed9d76de68b49347188187054bd4` with `SOURCE_REOPEN_REQUIRED=false`;
- broader Integration CI `34463405935` PASS with forced Web + DB;
- Governance CI `34463405902` PASS.

The reviewer-reported Slice-05 evidence branch/commit/path was not GitHub-visible when Coordinator checked; this persistence discrepancy is recorded truthfully and is not part of the S06-001 prompt correctness question.

The exact S06 materialization SHA `5abbb5181405e0f5a468176edd93db8226a3efd5` changes only planning/control artifacts, the S06-001 prompt, and producer reconciliation. Integration CI `34488858134` PASS and Governance CI `34488858173` PASS on that exact SHA.

## Proposed first Slice-06 task

`TASK-S06-001 — Master Data Lifecycle & Historical Semantics Trusted Contracts`

This is deliberately a shared-contract backend prerequisite. It is not the Master Data UI and not the Internal User / Identity / RBAC task.

### In-scope Phase-1 business masters

- organizational_units
- department_teams
- positions
- position_groups
- qualification_levels
- rooms
- interview_formats
- recruitment_sources
- document_types
- cancellation_reasons
- rejection_reasons

### Canonical commands in scope

- `create_master_item(...)`
- `update_master_item(...)`
- `delete_or_inactivate_master_item(...)`

All use `master_data.manage` and must preserve historical semantics, optimistic versioning, audit, RLS/ACL boundaries and accepted downstream behavior.

### Explicitly out of scope

- app_users directory lifecycle commands
- assign/remove HR role
- granular permission grant/revoke
- bound internal identity rebind
- Root break-glass recovery
- Candidate identity recovery
- Master Data management UI
- Users & Permissions management UI
- Vercel deployment
- connected Supabase migration application
- main mutation

## Canonical sources to reconcile

Primary:

1. `recruitment_webapp/review_pack/09_MASTER_DATA_CATALOG.md`
2. `recruitment_webapp/review_pack/64_MASTER_DATA_HISTORY_POLICY.md`
3. `recruitment_webapp/review_pack/08_DATA_MODEL_AND_FIELD_DICTIONARY.md`
4. `recruitment_webapp/review_pack/37_BACKEND_COMMAND_CONTRACTS.md`
5. `recruitment_webapp/review_pack/55_COMMAND_COVERAGE_MATRIX.md`
6. `recruitment_webapp/review_pack/59_RLS_POLICY_BLUEPRINT.md`
7. `recruitment_webapp/review_pack/command_registry.yaml`
8. `recruitment_webapp/review_pack/database_schema.sql`
9. `recruitment_webapp/review_pack/seed_master_data.json`

Supporting:

- `39_SECURITY_RLS_MATRIX.md`
- `40_DATABASE_INVARIANTS.md`
- `73_DOMAIN_GLOSSARY_AND_CANONICAL_PREDICATES.md`
- `100_TECHNICAL_PRECODE_GATE_V1_18.md`
- `02_ROLES_PERMISSIONS_AND_NAVIGATION.md`
- `46_AUTH_IDENTITY_MODEL.md`
- `50_OWNER_DECISIONS_PENDING.md`
- `61_ROOT_ADMIN_BREAK_GLASS_RECOVERY.md`
- `14_SCOPE_AND_OPEN_ITEMS.md`

Also inspect the accepted migration/RPC tree at the exact reviewed SHA so the prompt does not duplicate or contradict existing reference-data/version/RLS primitives.

## Review questions / risk focus

### 1. Task split correctness

Determine whether Master Data lifecycle/history is a valid first independently implementable Slice-06 shared-contract task and whether separating User/Identity/RBAC into a later security task is consistent with canonical source and dependencies.

Block only if the split creates an actual missing prerequisite or impossible contract boundary.

### 2. Master catalog completeness

Verify the prompt's 11 business-master allowlist matches Phase-1 physical business master scope. Permission catalog and Users must not be treated as ordinary HR Master Data.

### 3. Trusted-command architecture

Verify the prompt correctly requires the three canonical commands and avoids browser direct DML / arbitrary-table administration.

A generic discriminator design must be a closed server-side allowlist with per-type DTOs/static routing. Flag any wording that could accidentally authorize arbitrary table/column dynamic SQL.

### 4. Historical structural semantics

Verify the prompt accurately captures:

- unused → hard delete allowed;
- referenced → Inactive, never hard delete;
- structural meaning of referenced master cannot be mutated;
- structural replacement = create new + Inactive old;
- label typo/translation corrections may be allowed with optimistic version + audit when meaning is unchanged;
- inactive prevents new selection but preserves readable/operable history.

Review structural examples: Team parent Unit, Position Unit/Team/Group, Interview Format room/link requirements, Document Type scope/code, Room identity-bearing code/building/location meaning.

Ensure the prompt does not over-classify advisory metadata such as `requires_demo_topic` into a new blocking invariant.

### 5. Usage predicate completeness

Verify the prompt is sufficiently explicit that delete/inactivate and structural-history checks must consider all relevant current accepted FK/business references, including references from other master rows, instead of checking only one consumer table.

### 6. Downstream compatibility

Verify inactive historical masters remain operational for accepted Candidate/Application/Interview/Report behavior, especially:

- Position hierarchy/durable Application identity;
- Qualification historical education rows;
- Document Type logical history;
- Interview Format historical Interview lifecycle;
- Room historical identity;
- cancellation/rejection reason history;
- recruitment source history.

The prompt must not authorize opportunistic rewrites of accepted workflow commands.

### 7. Versioning / audit

Verify consistent `updated_at + version_no`, optimistic stale rejection and same-transaction canonical audit requirements are source-backed and sufficient.

### 8. Security / RLS / ACL

Verify:

- actor is active authenticated internal user;
- `master_data.manage` is required;
- Root implicit allow does not bypass data-integrity/history rules;
- no anon/direct broad DML;
- explicit RPC/helper ACLs;
- SECURITY DEFINER uses empty search_path and schema-qualified references;
- no service-role/browser privilege escape;
- minimum read surface only.

### 9. Existing `users.directory_read` observation

The accepted Slice-01 technical foundation contains `users.directory_read` in some RLS/dependency plumbing while current business source emphasizes `users.directory_manage` and restricted permission-detail visibility.

The producer intentionally leaves this untouched in S06-001 and defers reconciliation to the later User/Identity/RBAC task.

Confirm this deferral is safe for the Master Data task. Do not reopen or repair User/Identity/RBAC in S06-001 unless a concrete dependency proves it is necessary for Master Data correctness.

### 10. Testability

Verify the prompt gives enough executable acceptance coverage for:

- permission denial/positive paths;
- optimistic stale behavior;
- used vs unused lifecycle;
- structural mutation denial;
- label correction;
- inactive new-selection denial vs historical operation;
- hierarchy/format/document-type/room cases;
- direct-DML/private-helper bypass denial;
- Root obeying structural-history safety;
- zero-state migration replay and directly affected regressions.

### 11. Source completeness / Owner decisions

Confirm no unresolved Owner decision is required before S06-001. `50_OWNER_DECISIONS_PENDING.md` states A–K are canonicalized; PDF deferral is unrelated.

If implementation ambiguity can be resolved from current canonical source, do not request Owner decision.

## Required reviewer behavior

This is a prompt/source review only.

Do not:

- implement code;
- edit the prompt yourself;
- create the implementation branch/checkpoint;
- mutate integration;
- start later Slice-06 tasks;
- push/merge main;
- deploy Vercel;
- apply connected Supabase migrations.

Report exact evidence-backed defects in the prompt. Prefer the smallest prompt repair if blocking.

## Required response format

Return:

`WORK_ID: S06-001-PROMPT-REVIEW-001`

`REVIEWED_REPOSITORY: oanhpham-kobe/eiu-recruitment`

`REVIEWED_BRANCH: autonomy/continuous-integration-20260905-01`

`REVIEWED_SHA: 5abbb5181405e0f5a468176edd93db8226a3efd5`

`TARGET_PROMPT: project_control/prompts/SLICE-06_TASK-001_v1.md`

`VERDICT: PASS | BLOCKING_REPAIR | OWNER_DECISION_REQUIRED`

`SOURCE_REOPEN_REQUIRED: true | false`

Then include:

- BLOCKING_FINDINGS
- SOURCE_RECONCILIATION_ASSESSMENT
- TASK_SPLIT_AND_DEPENDENCY_ASSESSMENT
- MASTER_LIFECYCLE_HISTORY_ASSESSMENT
- SECURITY_RLS_ACL_ASSESSMENT
- TESTABILITY_ASSESSMENT
- ACCEPTED_TREE_COMPATIBILITY_ASSESSMENT
- VERIFICATION_EXECUTED
- ACCEPTANCE_STATEMENT

For PASS, explicitly state that the exact prompt at reviewed SHA may be materialized for implementation without reopening canonical source.

## Durable evidence

Persist the complete review if possible.

Suggested branch:

`review/S06-001-PROMPT-5abbb51-v1`

Suggested path:

`project_control/reviews/S06_001_PROMPT_REVIEW_5abbb51_v1.md`

Return actual:

- EVIDENCE_BRANCH
- EVIDENCE_COMMIT (full 40-char SHA)
- EVIDENCE_PATH

If persistence is unavailable, say `EVIDENCE_PERSISTENCE: UNAVAILABLE`. Never invent coordinates.