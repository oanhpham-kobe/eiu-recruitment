# TASK-S06-001 Prompt Producer Reconciliation — v1

## Identity

- WORK_ID: `S06-001-PROMPT-PRODUCER-RECONCILIATION-001`
- TARGET: `project_control/prompts/SLICE-06_TASK-001_v1.md`
- PRODUCER_RESULT: `PASS_PENDING_INDEPENDENT_REVIEW`
- SOURCE_REOPEN_REQUIRED: `false`

## Canonical sources reconciled

- `09_MASTER_DATA_CATALOG.md`
- `64_MASTER_DATA_HISTORY_POLICY.md`
- `08_DATA_MODEL_AND_FIELD_DICTIONARY.md`
- `37_BACKEND_COMMAND_CONTRACTS.md`
- `46_AUTH_IDENTITY_MODEL.md`
- `50_OWNER_DECISIONS_PENDING.md`
- `55_COMMAND_COVERAGE_MATRIX.md`
- `59_RLS_POLICY_BLUEPRINT.md`
- `61_ROOT_ADMIN_BREAK_GLASS_RECOVERY.md`
- `14_SCOPE_AND_OPEN_ITEMS.md`
- `command_registry.yaml`
- `database_schema.sql`
- accepted migration/RPC tree through Slice-05

## Reconciliation result

The first safe Slice-06 unit is the business Master Data lifecycle/history trusted contract, not the User/Identity/RBAC surface.

Reasons:

1. Canonical Master Data defines its own physical lookup entities, historical-reference rules, optimistic versioning, and explicit trusted commands: `create_master_item`, `update_master_item`, `delete_or_inactivate_master_item`.
2. Internal User/Identity/RBAC has a separate security model: directory-edit authority, Root-only HR role/permission actions, bound identity protection, active-owner/participant stranding guards, and break-glass recovery. Combining those with generic Master Data CRUD would produce an unnecessarily broad high-risk task.
3. Root break-glass is explicitly an operational recovery runbook rather than normal application UI.
4. Owner Decisions A–K are canonicalized; no unresolved Owner decision blocks Master Data implementation. The official PDF asset deferral is unrelated.

## Scope boundaries locked into prompt

In scope business masters:

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

Out of scope:

- app_users
- app_user_roles
- app_user_permissions / permission catalog administration
- users.identity_manage
- Root identity recovery
- Candidate identity recovery
- management UI

## Historical semantics locked into prompt

- unused row may hard-delete;
- referenced row becomes Inactive;
- referenced structural meaning cannot be mutated;
- structural replacement uses create-new + Inactive-old;
- display-label typo/translation correction may be allowed with optimistic version + audit when meaning is unchanged;
- inactive prevents new selection but does not invalidate historical references;
- existing operational history using inactive masters remains operable.

Examples explicitly covered: Team→Unit, Position→Unit/Team/Group, Interview Format room/link requirements, Document Type scope/code, Room identity-bearing code/building/location meaning.

The prompt deliberately does not classify all metadata as structural. `requires_demo_topic` remains advisory and must not gain a new blocking invariant.

## Security/architecture reconciliation

- all mutations remain trusted command/RPC paths;
- no arbitrary table/column admin API;
- generic master discriminator must be a closed allowlist;
- authenticated browser gets no broad direct DML;
- SECURITY DEFINER helpers require empty search_path and explicit ACLs;
- Root implicit permission does not bypass structural/data-integrity rules;
- audit is same-transaction.

## Accepted-tree observation to re-check during implementation review

The accepted Slice-01 foundation contains a technical `users.directory_read` helper permission used by RLS/dependency plumbing, while the current business permission catalog emphasizes `users.directory_manage` plus restricted permission-detail visibility. This is not part of S06-001 and is not treated as a Master Data blocker. It must be reconciled explicitly in the later User/Identity/RBAC task rather than opportunistically altered here.

## Producer verdict

The prompt is source-backed, dependency-bounded, and suitable for independent `eiu-reviewer` prompt/source reconciliation. No canonical source reopen is required.