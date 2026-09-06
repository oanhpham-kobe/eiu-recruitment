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

Implement exactly one authenticated public trusted command, `public.copy_interview_schedule`, with a stable explicit signature covering:

- source interview identity and expected version;
- target application identity and expected target/latest-round version where applicable;
- copied schedule/logistics draft, participant selection, and idempotency key.

The command MUST:

1. Authenticate and authorize server-side with `interviews.manage` plus required view permission or root; direct table DML remains unavailable.
2. Treat browser Copy as draft-only; only this command creates/mutates target state.
3. Lock target Application, then relevant target/latest Interview rows, then Submission; re-read and validate after locks.
4. Select the target round atomically: populate an eligible default target round only when clean; otherwise create the next legal round without overwriting a business-used target round. Record `copied_from_interview_id` provenance.
5. Validate target application active/current lifecycle conditions and all selected participants are active and selectable. Preserve snapshots and deterministic participant ordering.
6. Normalize format/room/meeting-link under the existing shared format helper. For an operational interval, use the existing deterministic Candidate → Room → Interviewer resource lock and conflict engine; re-check conflicts before commit.
7. Use command idempotency keyed to the authenticated actor and a fingerprint of all mutation-relevant input. Same key/same request returns the persisted result; same key/different request fails closed.
8. Audit the copy command. Any validation/conflict/audit failure rolls back all target round, participant, and schedule changes.
9. Reuse existing canonical helpers/types/functions. Do not add duplicate lock engines, generic copy commands, browser-side multi-write orchestration, or compatibility aliases.

## 4. Tests

Add consumer-observable SQL integration coverage for:

- authorized success into an unused/default target round;
- used target Round 1 creates the next legal round and leaves Round 1 unchanged;
- provenance, copied snapshots/order, and copied logistics;
- candidate, room, and interviewer conflicts reject atomically;
- inactive participant and inactive target application reject;
- idempotent replay and mismatched replay reject;
- unauthorized/unauthenticated callers and direct-DML denial;
- no partial target mutation on every failure path.

## 5. Verification

Run local migration replay, the new test, and affected S04 regression tests. Run `git diff --check`. Do not deploy, push main, alter canonical source files, or implement Interview UI/PDF/email features.
