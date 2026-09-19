# TASK-S08-001 — Source Reconciliation

Work ID: `S08-001-SOURCE-RECONCILIATION-001`

Producer: `EXTERNAL_CHATGPT`

Baseline inspected: `17d330b4e2689f2c93809242d2680946ed78978b`

Result: `PASS`

Source reopen required: `false`

## Proposed task

`TASK-S08-001 — Application Inbox Search and Indexed Pagination Hardening`

This is a bounded hardening of the accepted Application Inbox read model. It is not a rewrite of the inbox and does not reopen accepted Slice-03 lifecycle/bulk semantics.

## Canonical authorities

Primary:

- `recruitment_webapp/review_pack/58_SEARCH_AND_INDEXING_STRATEGY.md`
- `recruitment_webapp/review_pack/38_NON_FUNCTIONAL_REQUIREMENTS.md`
- `recruitment_webapp/review_pack/67_WEB_SECURITY_BASELINE.md`
- `recruitment_webapp/review_pack/39_SECURITY_RLS_MATRIX.md`
- `recruitment_webapp/review_pack/59_RLS_POLICY_BLUEPRINT.md`
- `recruitment_webapp/review_pack/99_INDEPENDENT_REVIEW_IMPLEMENTATION_ALIGNMENT_V1_18.md`
- `recruitment_webapp/review_pack/100_TECHNICAL_PRECODE_GATE_V1_18.md`
- `recruitment_webapp/app_spec.yaml`

Accepted implementation inspected:

- `supabase/migrations/20260905060000_candidate_form_and_submission_schema.sql`
- `supabase/migrations/20260905130000_application_inbox_read_rpc.sql`
- `supabase/tests/application_inbox_read.sql`
- `web/src/app/application-inbox-actions.ts`
- `web/src/lib/application-inbox/server.ts`
- `web/src/lib/application-inbox/model.ts`
- `web/src/components/inbox/ApplicationInboxTable.tsx`
- existing Application Inbox web tests.

## Canonical contract

`58_SEARCH_AND_INDEXING_STRATEGY.md` requires growing datasets to use server-side search/pagination; a 300 ms text debounce; broad name search only from two characters; default page size 25 with 25/50/100 options; indexed search for Name/Email/Phone; a tested Vietnamese accent-insensitive strategy before performance UAT; Candidate-group pagination for Application Inbox; immutable-ID tie-breakers; and PII search text kept out of URL/history/telemetry.

The source explicitly says the starter schema already includes a trigram GIN index on `submissions.full_name`, a lower-case email index, a digit-normalized phone expression index, status/date indexes, and parent indexes. The hardening task should align the query predicates with those strategies and add only narrowly justified normalization/index support needed for accent-insensitive matching. It must not over-index unrelated fields.

## Accepted state already correct

The accepted tree already satisfies several important requirements:

1. Application Inbox is server-side. Browser actions call the trusted server adapter, which calls `public.list_application_inbox`; the browser does not load the full growing dataset and filter it as the production authority.
2. The RPC paginates Candidate groups, not child Submission rows. After selecting the Candidate page it returns that Candidate's full historical Submission group.
3. Existing SQL regression coverage asserts Candidate-group counts, deterministic group order, complete child history, and Asia/Ho_Chi_Minh date boundaries.
4. Stable ordering already includes immutable tie-breakers (`submission_id`, then `candidate_id`).
5. The PII search term is held in component/request state and sent through the server action/RPC. It is not intentionally serialized into list-page URL state.
6. RLS/permission authorization remains server/database authoritative through the accepted read model.

These behaviors are predecessor invariants and must remain intact.

## Concrete gaps at the accepted baseline

### G1 — Search predicates are not canonically normalized

`public.list_application_inbox` currently applies raw substring predicates:

- `full_name ILIKE '%' || p_query || '%'`
- `email ILIKE '%' || p_query || '%'`
- `phone ILIKE '%' || p_query || '%'`

This does not implement the source-required tested Vietnamese accent-insensitive strategy. It also does not align email and phone predicates with the starter schema's lower-case email and digit-normalized phone index strategy.

### G2 — Canonical page-size contract is not implemented

The server adapter currently defaults to page size `10`; the RPC also defaults to `10`. Canonical search strategy specifies default `25` and user-selectable `25/50/100` page sizes.

### G3 — Canonical debounce/minimum broad-name rule is not implemented

Application Inbox currently schedules filter reads after `250 ms`, while the source specifies `300 ms`. The server normalizer trims/caps the query but does not enforce the minimum two-character rule for broad name search.

The implementation must preserve exact/near-exact email/phone usability while preventing one-character broad-name scans. The producer must define a deterministic classification/normalization rule rather than trying to infer intent from arbitrary SQL wildcard behavior.

### G4 — Search performance proof is absent

Existing regression tests prove correctness but do not prove the Slice-08 search hardening contract or representative index/query-plan behavior. `38_NON_FUNCTIONAL_REQUIREMENTS.md` and `58_SEARCH_AND_INDEXING_STRATEGY.md` require query-plan/performance evidence before release hardening can close.

This task should add local/staging-equivalent query-plan evidence suitable for the canonical strategy, without pretending a tiny fixture database can prove production p95 by itself.

## Explicit non-gaps / do not reopen

- Do not replace server-side search with browser-side filtering.
- Do not change Candidate-group pagination into Submission-row pagination.
- Do not reopen accepted bulk status/candidate lifecycle semantics.
- Do not add applicant/application-code search: the current v1.8 Search authority for this inbox is Name/Email/Phone plus operational filters.
- Do not weaken RLS or expose a privileged client query.
- Do not persist Name/Email/Phone search text in URLs, browser history, telemetry, or audit payloads.
- Do not change accepted Interview, report, email, scan, cleanup, or user-management contracts.

## Task boundary

S08-001 may change only the bounded Application Inbox search/read path and directly supporting migration/tests/UI controls required by the canonical Search strategy.

Expected areas:

- one forward-only Supabase migration hardening `list_application_inbox` and narrowly required search normalization/indexing;
- SQL tests for normalized search, page-size bounds, deterministic grouping, RLS/permission preservation and regressions;
- `web/src/lib/application-inbox/*`, `web/src/app/application-inbox-actions.ts`, and `web/src/components/inbox/ApplicationInboxTable.tsx` as required;
- focused web tests for debounce, PII transport state, page-size selection and request parameters;
- query-plan/performance evidence on representative local/staging-style data.

## Sequencing after S08-001

Separate later Slice-08 domains remain outside this task:

- `TASK-S08-002` candidate: durable distributed rate limiting / abuse controls. `68_RATE_LIMIT_POLICY.md` requires durable multi-instance counters for OTP request/verify, Candidate Submit/Update, upload reserve/finalize, internal search, email enqueue and PDF generation. The accepted tree does not expose a shared durable limiter primitive; this is intentionally not mixed into search-query hardening.
- later performance/accessibility/release evidence, backup/restore, retention/archive/purge, rollback/deployment/UAT work must be separately reconciled and must respect the existing prohibition on production deployment and connected Supabase mutation without Owner authorization.

## Decision

`PASS`

Materialize `TASK-S08-001 — Application Inbox Search and Indexed Pagination Hardening` as the first Slice-08 task, with implementation prohibited until its exact prompt/baseline checkpoint receives an independent OMP/`eiu-reviewer` prompt review PASS.

`SOURCE_REOPEN_REQUIRED: false`
