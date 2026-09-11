# TASK-S06-001 Independent Implementation Re-Review Gate R3

## Identity

- WORK_ID: `S06-001-IMPLEMENTATION-REVIEW-001-R3`
- REVIEWER: `eiu-reviewer`
- REPOSITORY: `oanhpham-kobe/eiu-recruitment`
- TASK_BRANCH: `oanhpham-kobe/TASK-S06-001-master-data-lifecycle`
- EXACT_REVIEWED_SHA: `9002c9be26c57a182494b9b0de46ae612f32d81e`
- PRIOR_REVIEWED_SHA: `dced5aac32e6b09181cd53d0011b9c951edf2814`
- ORIGINAL_TASK_BASELINE: `0ec409915bdd00b61b1b7affdb77ec778c7c1dc7`
- CANONICAL_PROMPT: `project_control/prompts/SLICE-06_TASK-001_v2.md`
- SOURCE_REOPEN_EXPECTATION: `false`

Review the immutable SHA above. Do not substitute a later mutable branch HEAD.

## R2 verdict being repaired

R2 returned `BLOCKING_REPAIR`, `SOURCE_REOPEN_REQUIRED=false`.

Its final clarification establishes one broad remaining contract gap: durable `ever referenced` history was still too narrow. Canonical Master Data history policy protects a master after semantic use even when an accepted workflow later replaces/deletes the current FK evidence.

R2's already-closed areas remain closed unless this repair changed a crossed invariant:

- cancellation/rejection durable history;
- inactive historical Candidate Document Type REPLACE/DELETE with ADD/new-selection denial;
- Interview Format first-use metadata race;
- `master_data.manage` inactive management reads;
- authorization, ACL, idempotency and optimistic-version mechanics.

## Exact R2 -> R3 delta

`dced5aac32e6b09181cd53d0011b9c951edf2814...9002c9be26c57a182494b9b0de46ae612f32d81e`

Exactly three files:

1. `.github/workflows/integration-ci.yml`
2. `supabase/migrations/20260911073228_master_data_durable_reference_history.sql`
3. `supabase/tests/master_data_durable_reference_history_test.sql`

No web/product UI file, canonical source, or unrelated implementation changed.

## R3 repair design

The repair introduces private durable semantic first-use evidence:

`private.master_reference_history(master_type, master_id, first_referenced_at)`

Properties to verify independently:

- closed allowlist of the 11 Phase-1 business-master types;
- no direct `anon` / `authenticated` read or execute path;
- backfill of every currently provable semantic reference;
- existing accepted reason-history evidence is imported rather than discarded;
- a static private recorder, not arbitrary dynamic table administration;
- new semantic references obtain a master-row `FOR KEY SHARE` lock before first-use recording;
- OLD references are captured before accepted UPDATE/DELETE lifecycle operations erase FK evidence;
- NEW references are captured before holder writes commit;
- history rows participate in the same transaction and roll back with failed holder writes;
- `private.master_usage_exists` consults durable history first and still retains current-reference scans for defense-in-depth/current temporary blockers.

### Durable semantic-holder inventory

The repair installs a closed trigger on exactly these retained semantic holders:

- `department_teams`
- `positions`
- `applications`
- `app_users`
- `submission_education`
- `submissions`
- `interviews`
- `submission_document_logicals`
- `interview_document_logicals`

Temporary upload reservations and Candidate staged-document changes intentionally remain current-only usage checks. Verify this distinction is correct: an abandoned reservation/staging row must not become permanent business-history proof by itself.

## Required blocker reconciliation

### Qualification Levels

Verify the actual trusted Candidate edit path:

`start_candidate_form_session(EDIT_SUBMISSION)`
→ `update_candidate_submission(...)`
→ accepted delete/rebuild of `submission_education`

now preserves the old Qualification in durable history before the child row disappears.

After removal:

- current FK evidence may be absent;
- structural repurposing must return `MASTER_STRUCTURAL_HISTORY`;
- delete/inactivate must return `INACTIVATED`, never hard-delete.

### Interview Format / Room replacement

Verify accepted schedule replacement through `save_interview_schedule`:

Format/Room A → Format/Room B

leaves A durably protected even though current `interviews` FKs point only to B.

After replacement, prior Format/Room A must:

- remain protected against structural repurpose;
- produce `INACTIVATED` under delete/inactivate.

Also verify the existing R2 first-use metadata race repair remains intact.

### Recruitment Source

A Submission's source may be replaced/cleared. Verify first semantic use survives clearing and prevents hard deletion of the formerly referenced source.

### Mutable master-to-master references

Verify prior parent/semantic master references survive replacement where the child remains mutable before it itself becomes referenced. The focused regression exercises Position Group replacement on an otherwise-unused Position.

Review Unit/Team/Position hierarchy paths as needed to ensure the shared history mechanism does not accidentally allow structural-history escape.

### Rollback / false-positive safety

The focused regression inserts a semantic Qualification holder row inside a subtransaction and intentionally rolls it back.

Verify:

- holder row is absent after rollback;
- durable history marker is also absent;
- the never-committed Qualification may still legitimately hard-delete.

This is required so history protection remains atomic rather than conservative-but-wrong leakage.

## Security / concurrency focus

Verify:

- new private table and functions are not exposed to `anon` or `authenticated`;
- `SECURITY DEFINER` functions use `SET search_path = ''` and schema-qualified references;
- the closed static CASE prevents arbitrary master/table routing;
- first-use locking closes structural-update/delete races without introducing an obvious lock-order cycle with accepted Master Data commands;
- old-reference capture is safe under competing lifecycle operations;
- `master_usage_exists` remains minimum and deterministic;
- Root does not bypass history/data-integrity rules;
- existing R2 authorization/idempotency/version guarantees remain unchanged.

## Permanent CI gate

`.github/workflows/integration-ci.yml` adds only the focused durable semantic-reference regression step:

`supabase/tests/master_data_durable_reference_history_test.sql`

Verify no existing verification was removed or weakened.

## Producer verification

Focused GREEN run:

- `34575487063` — PASS
- exact product tree: `416fdb42ed0e30063d820e4dadbef9b629af80f2`
- verification head: product tree plus one temporary workflow only
- Governance: PASS
- Database: PASS
  - diff hygiene
  - zero-state migration replay
  - PRE-S04
  - S05 interviewer report
  - S05 HR report + privacy
  - existing S06 regressions
  - new durable semantic-reference history regression
  - concurrent idempotency
  - deterministic Interview Format first-use race
  - DB advisors
  - cleanup

Final full verification after permanent CI wiring:

- `34575867899` — PASS
- exact candidate: `9002c9be26c57a182494b9b0de46ae612f32d81e`
- verify branch: `verify/S06-001-R3-9002c9b`
- verify head: `66bb96f9409eadd89f61fe009521ef583cdb2d99`
- equivalence: exact candidate plus only `.github/workflows/s06-001-r3-final-verify.yml`
- Web: PASS — install/audit/design/lint/typecheck/build/Chromium/full tests
- Database: PASS — zero-state + all accepted regressions including R3 history + concurrency/race/advisors
- Governance: PASS

Producer evidence is not independent acceptance. Read the exact implementation and form your own verdict.

## Review-only boundaries

Do not modify implementation, refs, integration state, `main`, Vercel, or connected Supabase. Do not select the next task.

## Required output

Return:

- `WORK_ID: S06-001-IMPLEMENTATION-REVIEW-001-R3`
- `REVIEWED_REPOSITORY: oanhpham-kobe/eiu-recruitment`
- `REVIEWED_BRANCH: oanhpham-kobe/TASK-S06-001-master-data-lifecycle`
- `REVIEWED_SHA: 9002c9be26c57a182494b9b0de46ae612f32d81e`
- `VERDICT: PASS | BLOCKING_REPAIR | OWNER_DECISION_REQUIRED`
- `SOURCE_REOPEN_REQUIRED: true | false`
- `BLOCKING_FINDINGS`
- `NON_BLOCKING_OBSERVATIONS`
- `VERIFICATION_EXECUTED`
- `DURABLE_HISTORY_ASSESSMENT`
- `SECURITY_CONCURRENCY_ASSESSMENT`
- `R2_BLOCKER_RECONCILIATION`
- `ACCEPTED_CONTRACT_REUSE_ASSESSMENT`
- `ACCEPTANCE_STATEMENT`

For PASS explicitly state that exact SHA `9002c9be26c57a182494b9b0de46ae612f32d81e` may proceed to governed integration without canonical source reopen.

## Durable evidence

Suggested evidence branch:

`review/S06-001-IMPL-9002c9b-v3`

Suggested path:

`project_control/reviews/S06_001_IMPLEMENTATION_REVIEW_9002c9b_v3.md`

If persistence is available, return actual branch, full 40-character evidence commit, and path. If not, state `EVIDENCE_PERSISTENCE: UNAVAILABLE`. Never invent coordinates.
