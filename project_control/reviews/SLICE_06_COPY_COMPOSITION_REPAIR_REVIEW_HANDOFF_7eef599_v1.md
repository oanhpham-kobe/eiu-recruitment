# SLICE-06 Copy Composition Repair — Independent Review Handoff

WORK_ID: `SLICE-06-COPY-COMPOSITION-REPAIR-REVIEW-001`

REVIEWED_SHA: `7eef5992638da87dc12e3c3cdcfcd77ec070a706`

BLOCKED_CLOSING_BASELINE_SHA: `0fe24da54d5d471fee5afdba7f34620716642d2e`

ORIGINAL_BLOCKING_REVIEW: `SLICE-06-CLOSING-REVIEW-001`

ORIGINAL_VERDICT: `BLOCKING_REPAIR`

ORIGINAL_SOURCE_REOPEN_REQUIRED: `false`

## Review purpose

Perform an independent, read-only, exact-SHA review of the bounded S04 Save Copy ↔ S06-002 Internal User lifecycle/operationalization repair introduced after the Slice-06 closing review found two HIGH/P1 composition defects.

This is a repair review only. Do not treat this handoff, producer verification, or prior accepted constituent checkpoints as sufficient to serialize the repair into governed integration. The repair must independently PASS first.

## Governance boundaries

- Review exact commit `7eef5992638da87dc12e3c3cdcfcd77ec070a706`; do not substitute a moving branch.
- Read-only review: no product/test/prompt/governance/ref mutations.
- Do not push or merge `main`.
- Do not create or merge a PR.
- Do not deploy Vercel.
- Do not apply migrations to connected Supabase.
- CI/producer verification is supporting evidence only; do not infer PASS from it.
- Accepted checkpoints for TASK-S06-001 and TASK-S06-002 are immutable and must not move.
- Do not reopen unrelated closed S06-001/S06-002 R2–R5 contracts unless a concrete regression from this repair is found.

## Original blocking findings to close

### P1-A — requested participant could be silently omitted

The blocked `copy_interview_schedule()` checked requested participant activity before waiting on schedule resources, then later used an active-only `app_users` join during participant insertion. A participant could be deactivated and commit while Copy waited; the later join could silently remove the requested ID and still allow successful copy/idempotency with an incomplete participant set.

Required closure:

1. Lock the complete requested participant set deterministically before target mutation.
2. Revalidate every requested ID after those locks.
3. Fail atomically if any requested participant is missing/inactive.
4. Do not use an active-only insert join as a substitute for exact-set validation.
5. Preserve source snapshot and caller-visible participant ordering semantics.
6. Include a staged Copy-versus-deactivation regression demonstrating either atomic failure/no target mutation or success with the exact requested set.

### P1-B — unscheduled Copy could deadlock with operational scheduling

The blocked path could take `updated_by=R` FK lock first, then participant P, while a concurrent schedule/uncancel path locks P then R under the S06-002 operationalization protocol. For P < R and independent parents/resources this creates a valid `R → P` versus `P → R` cycle.

Required closure:

1. Include actor and complete requested participant User set in a deterministic command-level acquisition plan before Copy's first Interview write/FK acquisition.
2. Align with accepted S06-002 User-row/advisory operationalization ordering.
3. Preserve post-lock activity validation and snapshot/order behavior.
4. Include a staged unscheduled Copy-versus-schedule/uncancel regression using actor UUID greater than participant UUID and independent parent/resource identities.

## Exact repair delta

Compare blocked closing target `0fe24da54d5d471fee5afdba7f34620716642d2e` to repair candidate `7eef5992638da87dc12e3c3cdcfcd77ec070a706`.

The expected delta is exactly three paths:

1. `supabase/migrations/20260913004500_copy_interview_user_lock_composition_repair.sql` — new forward migration replacing the effective `public.copy_interview_schedule()` definition.
2. `supabase/tests/copy_interview_schedule_concurrency_test.sh` — new staged concurrency regression harness for the two closing-review findings.
3. `.github/workflows/integration-ci.yml` — exactly four added lines invoking the staged Copy/User concurrency test after retained S06-002 lifecycle concurrency and before crossed Application/Interview suites.

No historical migration, web source, policy, Master Data source, accepted checkpoint, or product-authority file should differ in this repair range.

## Production repair design to inspect

The forward migration keeps the existing command's authentication/authorization, validation, idempotency fingerprint, target/source/application/submission locking, format normalization, latest-round/default-round rules, schedule conflict handling, provenance, auditing, result shape, and ACL surface.

The intended lock composition is deliberately NOT a blanket User-before-resource reorder.

Existing scheduling commands use schedule-resource gates before S06-002 User-row operationalization. Therefore the repaired scheduled Copy is intended to preserve:

`Candidate resource → Room resource → Interviewer resource advisories → sorted actor ∪ requested participant User rows → matching per-user advisories → post-lock exact-set activity validation → first target Interview write/FK acquisition`

For an unscheduled Copy there are no schedule-resource gates, so the intended path is:

`sorted actor ∪ requested participant User rows → matching per-user advisories → post-lock exact-set activity validation → first target Interview write/FK acquisition`

Review specifically whether this avoids introducing a new RESOURCE↔USER inversion relative to retained scheduling commands.

The repair builds a sorted/distinct UUID set containing the actor plus every requested participant, locks `public.app_users` rows with `FOR UPDATE` in UUID order, then obtains the matching S06-002 per-user advisory locks through `private.lock_internal_user_ids(...)`.

After that full acquisition it performs authoritative exact-set revalidation: the number of requested IDs that still exist and are active must equal `cardinality(v_participant_ids)`. Failure returns `CURRENT_PARTICIPANT_INACTIVE_REASSIGN_REQUIRED` before any target Interview mutation.

The final participant `INSERT ... SELECT` is intended to use the already locked/revalidated identities without `u.is_active` as a filtering predicate. Source participant snapshots are retained where available; otherwise directory snapshots are used. `WITH ORDINALITY` retains caller-visible order.

## Staged regression harness to inspect

File: `supabase/tests/copy_interview_schedule_concurrency_test.sh`

The harness uses real public commands plus explicit lock holders and `pg_stat_activity` lock-wait observation.

### Scenario A — scheduled Copy versus participant deactivation

- Copy is made to wait on the target Candidate advisory resource gate.
- While Copy waits, an actual `set_internal_user_active(..., false, ...)` commits for the requested participant.
- After the resource gate is released, repaired Copy is expected to acquire/revalidate its User set and fail with `CURRENT_PARTICIPANT_INACTIVE_REASSIGN_REQUIRED`.
- Assertions require the deactivation to remain committed, target default Round 1 to remain structurally empty, zero target participants, and no copied child/provenance mutation.

Review whether this staging genuinely places deactivation in the previously vulnerable window and whether the no-mutation assertions are adequate to rule out silent partial success.

### Scenario B — unscheduled Copy versus independent scheduling command

Fixture UUID ordering deliberately uses participant `P < R` actor. A test-only AFTER INSERT gate pauses the unscheduled same-Application Copy after its first Interview insert. Under the repaired implementation, Copy should already hold sorted P+R User rows/advisories before reaching that gate.

While Copy is paused, an actual `save_interview_schedule()` on another Application/Interview with current participant P and actor R is launched. It is expected to wait on P rather than creating the prior R→P / P→R cycle. Releasing the Copy gate should allow both public commands to complete without `deadlock detected`.

Post-state assertions require:

- Copy allocates Round 2 with correct `copied_from_interview_id` and remains unscheduled.
- Copy has exactly requested participant P with `participant_order=1`.
- Independent schedule command applies the requested interval.

Review whether this staging genuinely recreates the old crossing far enough to demonstrate the repaired acquisition ordering, and whether the test-only trigger itself avoids masking the relevant lock graph.

## Permanent regression gate

Review `.github/workflows/integration-ci.yml` and confirm the new harness is permanently invoked after `TASK-S06-002 Internal User Lifecycle Concurrency Assertions` and before the crossed Application/Interview lifecycle/round/Copy suites. Confirm the change is only the intended four-line invocation and does not weaken/reorder existing required gates.

## Producer verification evidence — supporting only

Final repair candidate: `7eef5992638da87dc12e3c3cdcfcd77ec070a706`.

A verifier branch was created directly from that exact candidate:

- verifier branch: `verify/SLICE-06-copy-locking-7eef599`
- verifier HEAD: `44d355d14845ae4ab3e339e26117e4cb0266feb6`
- candidate → verifier delta: exactly one ephemeral file, `.github/workflows/verify-slice06-copy-locking.yml`
- workflow run: `34709317965`
- job: `103595034113`
- conclusion: SUCCESS

The run performed local-only verification and did not touch connected Supabase. Supporting observations from the run:

- zero-state migration replay applied `20260913004500_copy_interview_user_lock_composition_repair.sql` successfully;
- S06-002 focused RBAC/Identity regressions PASS;
- retained S06-002 R2 command lock-order concurrency regressions PASS;
- retained S06-002 R3 lock/evidence concurrency regressions PASS;
- retained S06-002 owner/participant concurrency PASS;
- staged Copy/User harness printed `SLICE-06 Copy/User concurrency composition assertions passed`;
- crossed S04 Application reactivation/participant regression PASS;
- crossed Interview lifecycle regression PASS;
- crossed Interview round/conflict regression PASS;
- retained Copy Interview Schedule suite PASS;
- local DB lint step exited successfully;
- local Supabase stopped successfully.

### Pre-existing DB lint diagnostics

Do not interpret the lint step as diagnostic-free. It emits two `level: error` diagnostics while still exiting successfully:

- `public.update_master_item`: `record "v_row" has no field "unit_id"`
- `public.update_candidate_submission`: `record "v_log" is not assigned to tuple structure`

These exact two diagnostics were also present on the blocked baseline closing Integration run `34707599687`, job `103590391233`, before this repair. Treat them as unchanged pre-existing tooling diagnostics, not as evidence created by or resolved by this bounded patch. Do not expand this repair's scope to fix them unless direct inspection shows the repair materially changes them.

## Constituent accepted checkpoints

TASK-S06-001:
- accepted SHA: `59be9b2c92906065b8e4baa902fcec1d4cbefa12`
- checkpoint: `checkpoint/S06-001-accepted-001`

TASK-S06-002:
- accepted SHA: `5f2b76c7f1e901b3cadb847906efcd1568c8cbc3`
- checkpoint: `checkpoint/S06-002-accepted-001`

Neither checkpoint is moved by this bounded repair. Integration branch remains at blocked closing target `0fe24da54d5d471fee5afdba7f34620716642d2e` pending independent repair PASS.

## Required independent assessment

At minimum, explicitly assess:

1. Exact-SHA confirmation for `7eef5992638da87dc12e3c3cdcfcd77ec070a706`.
2. Exact repair-delta containment to the three expected paths.
3. Preservation of original Copy command behavior outside the bounded concurrency repair.
4. Scheduled lock order: resource gates remain before User-row/advisory acquisition, avoiding a new inversion.
5. Unscheduled lock order: actor + complete participant User set is acquired before first Interview write/`updated_by` FK.
6. Deterministic UUID ordering and per-user advisory coverage for actor + all requested participants.
7. Authoritative post-lock exact-set existence/activity revalidation and atomic failure semantics.
8. Removal of the active-only final insert filter as a mechanism that could silently omit a requested ID.
9. Snapshot preservation, participant ordering, idempotency, conflict, default-round/new-round, provenance, audit, and result semantics.
10. Scenario A's staging and post-state proof for the Copy-vs-deactivation race.
11. Scenario B's P<R staging and proof that the old Copy/schedule deadlock cycle is closed without test masking.
12. Permanent Integration CI placement and non-weakening of existing gates.
13. No regression or reason to reopen unrelated accepted S06-001/S06-002 R2–R5 contracts.
14. Proper treatment of producer CI as supporting evidence only.
15. Proper classification of the two unchanged pre-existing lint diagnostics.
16. Whether the repair can be serialized into governed integration for a new exact-SHA Slice-06 closing gate.

## Required output

Return:

`WORK_ID: SLICE-06-COPY-COMPOSITION-REPAIR-REVIEW-001`

`REVIEWED_SHA: 7eef5992638da87dc12e3c3cdcfcd77ec070a706`

`VERDICT: PASS | BLOCKING_REPAIR`

`SOURCE_REOPEN_REQUIRED: true | false`

Then provide concise but concrete sections covering exact-SHA confirmation, delta/provenance, production lock composition, requested-participant atomicity, deadlock closure, staged regression quality, retained semantics/non-regression, CI treatment, any blocking findings, reopen assessment, and evidence persistence.

If PASS, state whether the exact three-path candidate is suitable for governed serialization and a new exact-SHA Slice-06 closing review. If BLOCKING_REPAIR, identify the minimum bounded repair required and whether any accepted source contract must reopen.
