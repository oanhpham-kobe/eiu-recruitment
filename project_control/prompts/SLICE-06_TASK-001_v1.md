# SLICE-06 / TASK-S06-001 — Master Data Lifecycle & Historical Semantics Trusted Contracts

## Task identity

- TASK_ID: `TASK-S06-001`
- SLICE: `SLICE-06 — Master Data / Users & Permissions`
- TYPE: shared-contract backend prerequisite
- EXECUTION_MODE: `AUTONOMOUS`
- IMPLEMENTATION_STATUS: `PLANNED_PENDING_INDEPENDENT_PROMPT_REVIEW`
- SOURCE_REOPEN_EXPECTATION: `false` unless a concrete canonical contradiction is proven.

## Objective

Implement the Phase-1 business-master backend contract that later Master Data UI and downstream workflows can safely consume. This task is deliberately limited to business master-data lifecycle/read-write semantics and their database/security tests. It must not absorb Internal User directory, HR role/permission management, bound identity recovery, Root break-glass, or management-page UI work.

## Canonical authority

Read and reconcile at the exact implementation baseline before coding:

1. `recruitment_webapp/review_pack/09_MASTER_DATA_CATALOG.md`
2. `recruitment_webapp/review_pack/64_MASTER_DATA_HISTORY_POLICY.md`
3. `recruitment_webapp/review_pack/08_DATA_MODEL_AND_FIELD_DICTIONARY.md`
4. `recruitment_webapp/review_pack/37_BACKEND_COMMAND_CONTRACTS.md`
5. `recruitment_webapp/review_pack/39_SECURITY_RLS_MATRIX.md`
6. `recruitment_webapp/review_pack/40_DATABASE_INVARIANTS.md`
7. `recruitment_webapp/review_pack/55_COMMAND_COVERAGE_MATRIX.md`
8. `recruitment_webapp/review_pack/59_RLS_POLICY_BLUEPRINT.md`
9. `recruitment_webapp/review_pack/73_DOMAIN_GLOSSARY_AND_CANONICAL_PREDICATES.md`
10. `recruitment_webapp/review_pack/100_TECHNICAL_PRECODE_GATE_V1_18.md`
11. `recruitment_webapp/review_pack/command_registry.yaml`
12. `recruitment_webapp/review_pack/database_schema.sql`
13. `recruitment_webapp/review_pack/seed_master_data.json`
14. Current accepted migration/RPC tree on the exact implementation baseline.

Business Logic Core v1.2 and Technical Architecture v1.18 are frozen. Do not invent a new business policy to make implementation convenient.

## Accepted prerequisites / reuse rule

The accepted tree already contains foundational identity/auth tables, master/reference tables consumed by Candidate/Application/Interview flows, RLS helpers, versioning primitives, and trusted workflow commands. Treat accepted behavior as authoritative implementation unless it concretely conflicts with current canonical source.

This task is append-only repair/extension over that tree:

- do not rewrite old accepted migrations;
- do not fork Current Round, interview scheduling, document, candidate, or application invariants;
- do not weaken existing active-master checks used by accepted commands;
- historical records using inactive masters must remain readable/operable;
- if an accepted helper can be reused without widening authorization, reuse it.

## In-scope business master entities

The generic Master Data contract may address only the Phase-1 business masters below:

- `organizational_units` — Khoa/Phòng
- `department_teams` — Ngành/Tổ
- `positions` — Vị trí
- `position_groups` — Nhóm vị trí
- `qualification_levels` — Học vấn
- `rooms` — Phòng/Địa điểm
- `interview_formats` — Hình thức phỏng vấn
- `recruitment_sources` — Nguồn tuyển dụng
- `document_types` — Loại tài liệu
- `cancellation_reasons` — Lý do hủy
- `rejection_reasons` — Lý do từ chối

The permission catalog is security configuration, not ordinary HR-managed business Master Data. `app_users`, roles, effective permissions, and identity bindings are explicitly out of scope here.

## Required trusted commands

Implement or reconcile the canonical commands:

- `create_master_item(...)`
- `update_master_item(...)`
- `delete_or_inactivate_master_item(...)`

All require an authenticated Active Internal User with effective `master_data.manage` permission, with Root implicit permission only through the existing canonical authorization helper. Browser code must not directly INSERT/UPDATE/DELETE business master tables.

### Generic-command safety

If a generic `master_type`/kind discriminator is used:

- it must be a closed server-side allowlist of the 11 entities above;
- table/column names must never be accepted as arbitrary client strings;
- writable fields must be allowlisted per master type;
- implementation must use explicit CASE/static SQL or an equally injection-safe design;
- DTO validation must reject unknown fields rather than silently ignoring them.

Do not build a generic arbitrary-table administration API.

## Create semantics

`create_master_item` must:

- validate the actor and `master_data.manage` at mutation time;
- validate the exact per-type DTO, code/label bounds and hierarchy/FK rules already defined by schema/source;
- reject invalid parent combinations such as Team→wrong Unit or Position→inconsistent Unit/Team/Group;
- preserve canonical metadata semantics (`requires_room`, `requires_meeting_link`, `scope_code`, `requires_demo_topic` etc.) without inventing undocumented blockers;
- create Active records by the canonical Phase-1 default unless the exact source explicitly specifies otherwise;
- initialize/retain canonical `updated_at + version_no` behavior;
- write the canonical same-transaction audit event;
- return a minimum-safe typed result useful for server-side refresh.

## Update semantics / structural-history guard

`update_master_item` must use optimistic concurrency (`expected_version_no` or the repository's exact canonical equivalent) and re-resolve the target under lock before writing.

For a master row that has ever been referenced by business/history:

- structural business meaning is immutable;
- a structural change must be rejected with a stable error; the operational remedy is create a new row and Inactive the old row;
- display-label typo/translation correction may be allowed when it does not change business meaning, with version bump + audit.

Structural examples that must be protected include, at minimum:

- Team parent Unit;
- Position Unit / Team / Position Group assignment;
- Interview Format room/link requirement semantics;
- Document Type scope/code semantics;
- Room identity-bearing code/building/location meaning once referenced;
- any other identity/FK/behavior metadata classified structural by current canonical source/schema conformance.

Do not assume every metadata field is structural. For example, `requires_demo_topic` is advisory Phase-1 UI metadata and must not gain a new undocumented blocking rule. Resolve ambiguous field classification from current canonical source rather than inventing policy.

For an unreferenced row, structural edits may occur only where allowed by the exact per-type canonical schema/contract and still require optimistic versioning + audit.

Do not use this command to mutate security permissions, internal-user identity, or Root state.

## Delete / Inactive semantics

`delete_or_inactivate_master_item` must lock and revalidate the target and then deterministically apply:

- no business/reference usage → hard delete allowed;
- any business/history/reference usage → do not hard delete; mark Inactive instead;
- Inactive means unavailable for new selection, not invalid history;
- historical FK references remain intact and operationally usable by accepted workflows;
- Root Admin/user lifecycle protections are out of scope because users are not business Master Data in this command.

The usage predicate must consider all relevant direct and indirect FK/business references in the accepted schema, including references from other master rows where those references give the row historical/structural meaning. Do not implement a partial guard that checks only one consumer table.

The command must report whether the result was `DELETED` or `INACTIVATED` (or an equally explicit typed result), bump version for inactivation through canonical versioning, and audit the mutation atomically.

## Inactive selection / historical operation invariant

Across the implementation and regression tests, prove:

- inactive master rows are excluded from default/new-selection surfaces;
- accepted create/update commands cannot newly reference inactive masters when canonical rules require Active selection;
- existing historical records retain and can resolve inactive references;
- existing Interviews using an inactive Interview Format remain cancellable/reactivatable/processable as long as the historical format reference is unchanged;
- no cascade/hard-delete path destroys retained business history.

This task may repair a missing active-reference guard only where current canonical source and accepted command ownership clearly establish that this Master Data contract owns the guard. Do not opportunistically refactor unrelated accepted workflows.

## Phase-1 master-specific invariants

At minimum preserve/test:

- Position references Unit and optional Team with null-safe hierarchy consistency; Position references Position Group.
- Department Team belongs to one Unit.
- Interview Format has canonical `requires_room` / `requires_meeting_link` metadata; do not hard-code behavior by display label.
- Document Type `scope_code` is explicit and seed semantics remain: CV/Degree/Transcript/Certificates = `SUBMISSION`; Slide/Publication/Portfolio = `INTERVIEW`; Other = `BOTH`.
- `requires_demo_topic` remains advisory in Phase 1.
- Recruitment Source is optional HR-editable Submission metadata, not Candidate-required input.
- cancellation/rejection reasons remain optional under the frozen status rules; this task does not introduce requiredness.
- all Phase-1 business masters have consistent `updated_at + version_no` semantics.

## Read/security surface

Provide only the minimum read surface necessary for trusted server-side Master Data management and later UI consumption. Prefer existing safe RLS/projections where they already meet the contract.

Requirements:

- authenticated role receives no broad direct DML;
- `anon` receives no business-table access for this feature;
- `authenticated` execute grants are only for intended public RPC wrappers;
- private helpers remain private and have explicit ACL restrictions;
- any `SECURITY DEFINER` function uses `SET search_path = ''` and schema-qualified references;
- do not expose arbitrary query/table selection;
- do not expose service-role credentials or build browser-side privileged endpoints;
- Root implicit permission must not bypass structural-history/data-integrity rules.

If a dedicated admin read projection is needed, it must be minimum-safe, permission-gated and persona-tested. Do not widen unrelated accepted lookup reads just to support the management page.

## Audit requirements

Every successful create/update/delete/inactivate writes the repository's canonical audit event in the same transaction. Record actor/action/entity/version/reason or changed-field metadata as appropriate, but no secrets/tokens. Failed validation or permission checks must not leave partial master/audit writes.

## Error behavior

Reuse existing stable error codes where applicable (`UNAUTHENTICATED`, `FORBIDDEN`, `NOT_FOUND`, `VALIDATION_ERROR`, `STALE_VERSION`, etc.). Add the smallest stable Master Data structural-history code only if no current canonical code covers the condition. Do not leak raw PostgreSQL/internal errors to UI adapters.

## Test-first acceptance

Add focused SQL regression coverage before/with production mutation logic. At minimum prove:

1. anon/no-auth/missing-permission denial;
2. `master_data.manage` positive create/update/delete path;
3. unknown master type / unknown fields rejected;
4. optimistic stale update rejected with no partial write/audit drift;
5. unreferenced master can hard-delete;
6. referenced master becomes Inactive instead of being deleted;
7. referenced structural mutation is rejected;
8. allowed label-only correction on referenced row succeeds, version-bumps and audits;
9. inactive item cannot be newly selected where canonical active selection is required;
10. historical record with inactive master remains readable/operable;
11. hierarchy invariants for Unit/Team/Position;
12. Interview Format structural metadata history guard;
13. Document Type scope structural history guard and explicit seed semantics;
14. Room referenced identity-bearing field guard;
15. authenticated role has no direct table DML and private helper ACLs cannot be used as bypass;
16. Root obeys the same structural/history safety rules.

Regression must run after zero-state migration replay and coexist with accepted Candidate/Application/Interview/Report SQL suites.

## Server adapter / UI boundary

If this task adds Next.js server adapters solely to expose the trusted commands for future UI, they must be `server-only`, validate DTOs, call RPCs, map stable errors, and perform no direct business-table mutation. Do not build the Master Data management page in TASK-S06-001.

## Verification

Use impact-selected verification, then the domain acceptance gate:

- SQL/static security review;
- zero-state Supabase migration replay;
- new Master Data SQL regressions;
- directly affected accepted database regressions, especially Application/Interview/document master-reference behavior;
- web lint/typecheck/build/tests only if web/server adapter code is changed;
- `git diff --check`;
- governance validation.

Do not claim a check as PASS unless it actually ran in the available environment/CI.

## Non-goals

Do NOT implement in this task:

- Master Data management UI/table/drawer;
- Internal User CRUD/lifecycle UI or commands;
- HR role assignment/removal;
- granular permission grant/revoke UI or commands;
- bound identity change/recovery;
- Root Admin break-glass implementation as normal app UI;
- Candidate identity recovery;
- Email/Documents/Activity workers;
- Vercel deployment;
- connected Supabase migration application;
- `main` mutation.

## Required producer handoff

Before independent implementation review, report:

- exact baseline and candidate SHA;
- exact changed files;
- source reconciliation decisions, especially structural-field classification and accepted-tree reuse;
- migration/RPC/ACL/audit design;
- test evidence and unexecuted checks;
- any accepted prerequisite touched and why;
- `SOURCE_REOPEN_REQUIRED` only if a genuine canonical contradiction exists.

The independent reviewer is `eiu-reviewer`. A candidate changing this shared schema/security contract is not accepted until exact-SHA independent review PASS and final integration/CI requirements in repository governance are satisfied.