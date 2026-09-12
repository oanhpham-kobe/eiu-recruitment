# SLICE-06 Closing Review — Owner-Transport Evidence

WORK_ID: SLICE-06-CLOSING-REVIEW-001
REVIEWED_SHA: 0fe24da54d5d471fee5afdba7f34620716642d2e
VERDICT: BLOCKING_REPAIR
SOURCE_REOPEN_REQUIRED: false
EVIDENCE_PERSISTENCE: UNAVAILABLE

## Exact-SHA confirmation

The independent reviewer confirmed a detached target HEAD exactly equal to `0fe24da54d5d471fee5afdba7f34620716642d2e`, parent `ba004a947e4e7d3c3e372ac5d3a2a4941428e8f9`, with the target commit changing only `project_control/CURRENT_STATE.md`. Review was static/read-only; no tests, builds, lint, migrations, services, edits, or ref mutations were performed.

## Constituent acceptance/provenance

The reviewer confirmed repository registry evidence for both accepted constituent tasks:

- TASK-S06-001 accepted at `59be9b2c92906065b8e4baa902fcec1d4cbefa12`, checkpoint `checkpoint/S06-001-accepted-001`, final-equivalence PASS, Integration CI `34579159091`, Governance CI `34579159098`.
- TASK-S06-002 accepted at `5f2b76c7f1e901b3cadb847906efcd1568c8cbc3`, checkpoint `checkpoint/S06-002-accepted-001`, R5/final-equivalence PASS, Integration CI `34705634804`, Governance CI `34705634726`.

The accepted checkpoints remain immutable. The reviewer did not independently resolve the checkpoint refs in the detached local checkout and relied on the supplied immutable coordinates plus repository registry provenance.

## Composition areas confirmed

The reviewer confirmed that Master Data ↔ Internal User Unit semantics, active Application owner guards, lifecycle/RBAC user gates, participant add/re-add freshness, durable master-reference history, trusted identity/RBAC/session consumers, Root identity protections, and the previously closed S06-002 R2–R5 areas remain internally consistent within their demonstrated scope. No Product, Business, Design, identity-policy, or Master Data-history source reopen was required.

## Blocking findings

### P1 — Save Copy may silently omit a requested participant

`public.copy_interview_schedule()` validates requested participants as active before schedule-resource locking, but its later participant `INSERT ... SELECT` inner-joins `app_users` with `u.is_active`. A requested user can be deactivated and commit while Copy is waiting on resource locks. The later active-only join then silently drops that requested participant, allowing Copy to commit success/idempotency with an incomplete participant set. The row/statement participant guards cannot reject an ID that never reaches the INSERT.

Required repair: before changing target state, lock the complete requested participant set in deterministic shared order and revalidate every requested ID after those locks. Fail atomically if any requested participant is absent/inactive. Preserve snapshot and user-visible ordering semantics. Add staged Copy-vs-deactivation coverage proving failure with no target mutation or success with the exact requested set.

### P1 — Unscheduled Save Copy can deadlock with operational scheduling

The reviewer established an actor/participant lock-order inversion. An unscheduled Copy can first acquire the immediate `interviews.updated_by` FK lock on actor R, then later request participant P. Concurrent schedule/uncancel on another Interview locks P then R under the S06-002 operationalization protocol. With `P < R`, this yields `R → P` versus `P → R` and a valid deadlock cycle.

Required repair: include the actor and complete selected participant User set in one deterministic command-level acquisition plan before Copy's first Interview write/FK acquisition, aligned with the operationalization protocol. Preserve post-lock activity validation and participant snapshot/order behavior. Add a staged unscheduled-Copy-vs-schedule/uncancel regression using actor UUID greater than participant UUID and independent parent/resource identities.

## Reopen assessment

The reviewer directed a bounded S06-002/S04 Copy-composition implementation and crossed-regression repair only. `SOURCE_REOPEN_REQUIRED=false`. Immutable accepted checkpoints must not move. Any repaired Slice-06 closing candidate requires a new exact-SHA closing review.

## CI treatment

The reviewer treated Governance CI `34707599823` and Integration CI `34707599687` on exact target `0fe24da54d5d471fee5afdba7f34620716642d2e` as supporting evidence only. Those PASS results do not cover the two missing Copy concurrency interleavings above.

## Coordinator disposition

Slice-06 remains open. Downstream Slice-07 materialization remains held. Repair scope is bounded to Copy command locking/revalidation and the missing staged regressions; unrelated accepted S06-001/S06-002 contracts remain closed.
