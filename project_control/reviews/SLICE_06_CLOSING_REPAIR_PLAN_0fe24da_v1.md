# SLICE-06 Closing Repair Plan

Baseline closing target: `0fe24da54d5d471fee5afdba7f34620716642d2e`
Blocking review: `SLICE-06-CLOSING-REVIEW-001` — `BLOCKING_REPAIR`, `SOURCE_REOPEN_REQUIRED=false`.

Repair is bounded to the S04 Save Copy ↔ S06-002 lifecycle/operationalization composition:

1. Add a forward migration replacing `public.copy_interview_schedule()` so, after authentication/authorization/idempotency and target/source state locks but before schedule-resource waits or target Interview mutation, it acquires the deterministic sorted `actor ∪ requested participant` `app_users` row lock set, then the matching Internal User advisory lock set.
2. Revalidate the complete requested participant set after those locks; absent/inactive participants fail atomically with `CURRENT_PARTICIPANT_INACTIVE_REASSIGN_REQUIRED`.
3. Remove the active-only participant insert join as a filtering mechanism; the already locked/revalidated exact set is inserted in caller order while retaining source snapshots/directory fallback semantics.
4. Add staged concurrency coverage for Copy vs deactivation and unscheduled Copy vs schedule/uncancel lock-order crossing.
5. Preserve all accepted checkpoints, source authority, session/RBAC/privacy contracts, historical semantics, and unrelated S06 closures.

No `main` mutation, PR creation/merge, Vercel deployment, or connected Supabase migration application is authorized by this repair.
