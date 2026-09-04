# Changelog v1.3 — Technical Closure Review

**Ngày:** 02/09/2026

## Business clarification
- Final Decision normally entered by one representative Interviewer after panel agreement.
- Added `decision_updated_at` / `decision_updated_by` semantics.
- Qualitative-field edits no longer move Final Decision Source.
- If another Interviewer later changes one of the 3 final fields, it becomes the latest agreed revision.

## External technical review accepted
- Application derives Candidate via Submission; duplicate `candidate_id` removed from Application starter schema.
- Unit/Team/Position invariant strengthened.
- Interview Report references `interview_participant_id`.
- Field-aware report concurrency; no stale whole-row overwrite.
- Backend command/transaction contracts added.
- Idempotency strategy added.
- DB version/invariant starter added.
- RLS + GRANT + view-security gate added.
- Storage private/access/upload-security spec added.
- Email outbox/retry spec added.
- Security audit separated from user-facing Activity/Email History.
- Auth identity model added.
- Deployment/backup/monitoring/NFR/UAT gate added.
- Privacy/retention workstream added as owner/legal go-live input.

## Vercel / Supabase audit alignment
- Next.js Server Actions treated as public mutation endpoints and re-authorized server-side.
- Supabase SSR cookie model documented.
- Service-role/secret never allowed in browser.
- Views kept private by default; exposed views require safe semantics and grants.
- Candidate/Interview files use private Storage.
- Preview/staging security smoke-test requirement added.
- Search/pagination/rate-limit/timezone expectations added.

## UI/Design alignment
- Design System v1.3 is current source-of-truth after Review v2 hardening.
- Table = semantic `<table>` + `<colgroup>` + fixed layout.
- Wide operational tables use `min-width + overflow-x:auto`.
- 16px minimum main content; 16px semibold table header/status badge.
- Whole-row expand with interactive-child event isolation.
- Status can be changed via one toolbar dropdown or authorized badge click.
- `VI | EN`, Vietnamese default.
- No scoring/rating.
- Demo Persona Switcher prototype/dev only.
- Candidate mobile Portal required before go-live.

## Still open
See `50_OWNER_DECISIONS_PENDING.md`.
