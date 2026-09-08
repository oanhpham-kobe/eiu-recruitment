# Implementation Acceptance Review — TASK-S04-004

WORK_ID: S04-004-IMPLEMENTATION-REVIEW-001  
TASK: TASK-S04-004  
BASE_SHA: 052a82841ab158a9dea29063de9e1601e65fe9bc  
REVIEWED_SHA: 1990afa41841edc6b25b89a5cdbb3cbfc1faa762  
RESULT: BLOCKING_REPAIR  
SOURCE_REOPEN_REQUIRED: NO  

## Summary
The exact GitHub diff from `052a82841ab158a9dea29063de9e1601e65fe9bc` to candidate `1990afa41841edc6b25b89a5cdbb3cbfc1faa762` was reviewed independently against canonical Handover v1.18, current backend command contracts, Design System v1.8, and REVIEW.md.

The candidate's core architecture is well-structured:
- Mutations run through authenticated Next.js Server Actions with internal permission checks.
- Browser code performs zero direct table writes or client mutation orchestration.
- Trusted commands propagate all required optimistic versions (`expected_version`, `expected_source_version`, `expected_target_application_version`, `expected_target_round_id`, `expected_target_round_version`), alignment arrays for reordering, and operation-scoped idempotency keys preserved across retries.
- The 1480px table grid, sticky columns, group expansion, phone row/card reflow, status menu trigger positioning/clamping, and drawer accessibility contracts are met.

However, a concrete functional blocker was identified in the read model:
In `web/src/lib/interview/server.ts`, `searchApplicationOptions()` calls `matchingSubmissionIds(client, rawQuery)`, which queries `submissions` with a hardcoded `.limit(250)`. When a query (e.g. common name/domain) matches more than 250 submissions, any active Applications associated with subsequent matching submissions are silently omitted from the Copy target selector. This violates Area D ("no arbitrary result cap introduces false negatives") and prevents reliable target Application resolution.

## Findings
- **[VALID BLOCKER] `web/src/lib/interview/server.ts:145-163` (`matchingSubmissionIds`):**  
  `matchingSubmissionIds` executes `.select('submission_id').or(...).limit(250)`. In `searchApplicationOptions(rawQuery)`, these IDs are passed directly to `appBuilder.in('submission_id', ids)`. If more than 250 submissions match a search query, matching applications linked to later submissions are permanently dropped without feedback.  
  *Required repair:* In `searchApplicationOptions`, use an inner-join or direct PostgREST referenced table filter on `submissions` directly from `applications` (matching the pattern successfully applied in `loadInterviewPage` via `filtered_submission:submissions!inner`), or paginate/stream the full matching set, removing the artificial 250-row cap that causes false negatives.
- **[VALID NON-BLOCKER] `web/src/lib/interview/server.ts:580,634`:**  
  Typeahead result lists in `searchSubmissionOptions` (.limit 25) and `searchApplicationOptions` (.limit 50) return bounded windows without visual pagination or an "additional results exist" indicator. This is standard for typeaheads, but adding explicit query refinement hints or pagination improves usability.
- **[FALSE POSITIVE] Dev database table absence:**  
  The connected Supabase dev environment does not currently have Application/Interview tables migrated. Per task constraints, TASK-S04-004 is strictly a UI/Server seam task; modifying database schemas or running live migrations is out of scope. This is environment state debt, not candidate code failure.

## Supabase Verdict
**PASS (subject to resolving the search pre-match cap).**  
All mutations map directly to accepted repository RPCs (`create_next_interview_round`, `save_interview_schedule`, `reschedule_confirmed_interview`, `copy_interview_schedule`, `change_interview_schedule_status`, `reactivate_application`, `reactivate_interview`, `delete_or_inactivate_interview`, `delete_or_inactivate_application`, `add_interview_participant`, `remove_interview_participant`, `readd_interview_participant`, `reorder_interview_participants`). No raw table inserts/updates occur. Supabase service-role keys are not referenced in client components.

## Vercel Verdict
**PASS.**  
Next.js Server Actions and Server Components follow current Next.js runtime standards. Pages and actions are properly isolated using `server-only` and `force-dynamic`. No node/runtime incompatibilities found.

## Design / Responsive Verdict
**PASS.**  
- Semantic `<table>` with exact `INTERVIEW_COLUMNS` totaling 1480px (`48, 340, 250, 220, 170, 360, 92`).
- 48px Select and 340px Candidate/Application remain sticky on horizontal scrolling.
- Single Application group expansion preserved.
- Phone view converts to structured rows/cards at 640px breakpoint without dropping business data.
- Operational Interview status badge scoped to 144px, wrapping long English text cleanly.
- StatusMenu panel clamped to viewport boundaries on mobile (390px) and anchored to trigger rect.
- Drawer meets focus-trap and Escape restoration requirements.
- Typography maintains >=16px operational body/control text scale.

## Verification Assessment
- Verified exact GitHub compare API diff and source tree.
- Verified test suite covers:
  - Unit/command tests: `web/src/__tests__/interview-commands.test.ts` (RPC naming, idempotency reuse, expected version forwarding, Application vs Interview reactivate distinction).
  - Model tests: `web/src/__tests__/interview-model.test.ts` (1480px grid, single expansion, PII bounds, timezone formatting).
  - Browser tests: `web/src/__tests__/interview-browser-acceptance.test.ts` (seven-width viewport validation 360–1440, zero page overflow, 44px touch targets, drawer contracts, sticky headers).
- Existing CI runs (34190624398, 34189208309, 34175490863) verify lint, typecheck, build, and browser QA passed.
- No broad tests or CI were re-run during this review.

## Follow-up Non-Blockers
1. Add visual feedback or scroll pagination when selector search results exceed typeahead limits.
2. Ensure deployment pipeline runs database migrations for S04-001 through S04-005 in dev before live UAT.
