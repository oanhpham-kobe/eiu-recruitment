# EIU Recruitment — Executor Prompt
## TASK-S04-003 — Dedicated copy interview schedule command
### Prompt version: SLICE-04_TASK-003_v1

## 0. Execution Control

```text
SOURCE_BASELINE: Full Handover v1.18
SOURCE_SHA256: 8874551cb5a7f78ac28f64a94c1820dc7d2c3a62f85cfb93b2bad70b611438a0
BUSINESS_STATUS: Business Logic Core v1.2 = FROZEN
TECHNICAL_STATUS: Technical Architecture v1.18 = TECHNICAL SPECIFICATION FROZEN
TASK_SCOPE: TASK-S04-003 copy_interview_schedule trusted mutation only
BASE_BRANCH: autonomy/continuous-integration-20260905-01
BASE_HEAD: d2db7030fb3d19f563eb56365bb63f57f43fa4fd
```

## 1. Required authority

Read before editing:

- `recruitment_webapp/review_pack/05_HR_INTERVIEW_PAGE.md` — Copy behavior, current-round semantics, participant and conflict rules.
- `recruitment_webapp/review_pack/37_BACKEND_COMMAND_CONTRACTS.md` — `copy_interview_schedule()` contract.
- `recruitment_webapp/review_pack/39_SECURITY_RLS_MATRIX.md` — command authorization boundaries.
- `recruitment_webapp/review_pack/40_DATABASE_INVARIANTS.md` — round/provenance and resource invariants.
- `recruitment_webapp/review_pack/48_IDEMPOTENCY_CONCURRENCY_SPEC.md` — shared schedule engine, idempotency, lock order.
- `recruitment_webapp/review_pack/13_ACCEPTANCE_CRITERIA_AND_TEST_CASES.md` — AC-COPY-CMD-01, AC-COPY-ENGINE-01, AC-RP-COPY-USED-01.
- `recruitment_webapp/review_pack/database_schema.sql` — effective schema and constraints.
- Ordered prior migrations, especially `20260906060000_interview_schema_and_conflict_locking.sql` and `20260906070000_interview_lifecycle_commands.sql`.

## 2. Required skills

Load and apply: `supabase`, `supabase-postgres-best-practices`, `security-review`, and `tdd`.

## 3. Implementation

Create one new idempotent migration after `20260906070000_interview_lifecycle_commands.sql` and one focused SQL integration test.

Implement exactly one authenticated public trusted command:

```sql
public.copy_interview_schedule(
  p_source_interview_id uuid,
  p_target_application_id uuid,
  p_expected_source_version bigint,
  p_expected_target_application_version bigint,
  p_expected_target_round_id uuid,
  p_expected_target_round_version bigint,
  p_start_at timestamptz,
  p_end_at timestamptz,
  p_interview_format_id uuid,
  p_room_id uuid,
  p_meeting_link text,
  p_interview_note text,
  p_participant_app_user_ids uuid[],
  p_idempotency_key uuid
)
```

The caller MUST provide the current target Application and current target/latest Round identity/version observed before Save Copy. The command locks and compares source, target Application, and target Round versions; each mismatch returns `STALE_VERSION`. Never infer these values, accept a null target round, or act on a later round allocated after the caller's read.

The command MUST:

1. Authenticate and authorize server-side. Root is allowed; every non-root caller MUST independently hold both `interviews.manage` and `interviews.view`. Do not pass those permissions as the two alternatives of `private.interview_command_actor`; direct table DML remains unavailable. Test manage-only and view-only denial separately.
2. Treat browser Copy as draft-only; only this command creates/mutates target state.
3. Lock target Application, then source/target Interview rows in deterministic identity order, then affected Submission rows; re-read and validate after locks.
4. Replace `private.is_structurally_empty_default_round(uuid)` with the current canonical `database_schema.sql` definition in this migration. `copy_interview_schedule` MUST call that exact predicate and MUST NOT use `private.is_interview_clean()`. It rejects every business-use/provenance condition, including participant/report, document, email outbox/history, copied-from, and reverse-copy references.
5. Select the target round atomically: for the **same Application**, always create the next legal round under normal allocation; for a **different Application**, fill its exact default Round 1 only if the canonical structural-empty predicate returns true, otherwise create the next legal round. Never overwrite a business-used target round. Record `copied_from_interview_id` provenance.
6. Validate target application active/current lifecycle conditions and all selected participants are active and selectable. Preserve snapshots and deterministic participant ordering.
7. Normalize format/room/meeting-link under the existing shared format helper. Copy only `start_at`, `end_at`, format, room/link, and `interview_note`; `demo_topic` MUST be NULL/blank on every copied target round. For an operational interval, use the existing deterministic Candidate → Room → Interviewer resource lock and conflict engine; re-check conflicts before commit.
8. Use command idempotency keyed to the authenticated actor and a fingerprint of every mutation-relevant argument. Same key/same request returns the persisted result; same key/different request fails closed.
9. Recalculate affected Submission status when current-round semantics change, audit the copy command, and rollback all target round, participant, and schedule changes on validation, conflict, or audit failure.
10. Reuse existing canonical helpers/types/functions. Do not add duplicate lock engines, generic copy commands, browser-side multi-write orchestration, or compatibility aliases.

## 4. Tests

Add consumer-observable SQL integration coverage for:

- authorized cross-Application success into an unused/default target Round 1;
- same-Application Copy always allocates the next legal round, even if Round 1 is structurally empty;
- used/default target Round 1 and every structural-empty exclusion (participant/report, document, email outbox/history, provenance) allocate the next legal round and leave existing data unchanged;
- provenance, copied snapshots/order, copied logistics, and blank `demo_topic` for both filled-default and newly-created target rounds;
- stale source, target Application, and target Round versions reject with `STALE_VERSION`, including competing round allocation/Copy;
- candidate, room, and interviewer conflicts reject atomically;
- inactive participant and inactive target application reject;
- idempotent replay and mismatched replay reject;
- unauthenticated, view-only, manage-only, and direct-DML callers are denied;
- no partial target mutation on every failure path.

## 5. Verification

Run local migration replay, the new test, and affected S04 regression tests. Run `git diff --check`. Do not deploy, push main, alter canonical source files, or implement Interview UI/PDF/email features.
