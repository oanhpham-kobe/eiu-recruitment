# 48. Idempotency & Concurrency Specification — v1.8

## Idempotency
Required for Candidate Submit, Create Application, Create Next Round, Copy/Save logical schedule mutation where retry can duplicate, enqueue email, finalize upload, persisted PDF generation. Same actor/scope/command/key returns prior result.

## Optimistic locking
Mutable entities use `version_no`; client sends expected version. Stale update fails unless the specific report merge algorithm safely merges disjoint patches.

## Report concurrency
Each Interviewer owns a distinct report. HR may edit that report with permission. Patch only changed fields. Disjoint field changes can merge. Same-field conflict: Interviewer ownership wins; HR stale write is rejected/reloaded. No stale whole-row overwrite.

Decision fields form one logical block for source semantics; any final-field change updates `decision_updated_at/by`; qualitative edits do not. Timestamp + report UUID tie-break is sufficient Phase 1; revision sequence is optional P2 hardening.

## Mandatory schedule consistency
Transaction alone under Read Committed is insufficient. Every mutation that can create/restore an operational interval must:
1. identify Candidate, Room, current Interviewers;
2. acquire transaction-level advisory locks in deterministic sorted resource order;
3. re-query conflicts;
4. mutate;
5. commit.

Shared engine applies to **Save Copy (`copy_interview_schedule`)**, save/reschedule, add/re-add participant when scheduled, reactivate, and CANCELLED→active status. Save Copy is not a client-only final mutation: the client draft remains non-mutating, while the trusted Save Copy command uses this shared deterministic Candidate/Room/Interviewer lock + conflict engine before commit.

Interval semantic: `[start_at,end_at)`. Do not use the legacy overloaded `effective_active` term. Canonical predicates are:
- `access_active` = active Application + active Interview;
- `resource_blocking` = `access_active` + schedule status not `CANCELLED` + both interval endpoints present.
Every `resource_blocking` Interview participates in conflict checks, whether or not it is Current Round.

## Participant concurrency
Add/remove/re-add/reorder lock the Interview. Reorder writes a complete ordered set; no duplicate current order. Re-add to an already scheduled Interview revalidates conflict.

## Round allocation
Lock Application, then allocate max round+1.

## Mandatory lock order
For all Interview resource mutations: lock **Interview row first** → resolve parent/Candidate → snapshot current Room/Participants → acquire deterministic advisory/resource locks → re-read participant/resource set → conflict check → mutate. This closes reschedule ↔ add/re-add participant races.

For all Application/current-round/report-outcome mutations: lock parent **Submission** before authoritative status recalculation.

Candidate Save/Submit uses form-session idempotency; staged file changes and text commit together.


## Application Reactivate concurrency
`reactivate_application()` locks the durable Application identity/Submission, revalidates eligible Active HR/root ownership, then enumerates every non-elapsed child Interview that would become `reactivation_conflict_relevant = resource_blocking AND end_at > transaction_now`. It acquires resource locks in deterministic global order and re-checks Candidate/Room/Interviewer overlaps before enabling the parent. Reactivation is all-or-nothing for non-elapsed operational intervals. Fully elapsed intervals remain historical and do not block lifecycle recovery even if another historical record overlaps the same past interval.
