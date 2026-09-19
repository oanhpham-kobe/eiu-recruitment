# TASK-S08-001 — Source Reconciliation v2

Work ID: `S08-001-SOURCE-RECONCILIATION-002`

Producer: `EXTERNAL_CHATGPT`

Baseline inspected: `17d330b4e2689f2c93809242d2680946ed78978b`

Supersedes before any prompt checkpoint/review:

- `project_control/reviews/S08_001_SOURCE_RECONCILIATION_v1.md`
- reason: producer self-audit found that the starter lower-case email index is on `submissions.email_snapshot`, while the accepted `list_application_inbox` RPC currently searches `candidates.email`; v1 described the index strategy too loosely.

Result: `PASS`

Source reopen required: `false`

## Proposed task

`TASK-S08-001 — Application Inbox Search and Indexed Pagination Hardening`

This is a bounded hardening of the accepted Application Inbox read model. It is not a rewrite and does not reopen accepted Slice-03 lifecycle/bulk semantics.

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

- `supabase/migrations/20260905030000_identity_schema.sql`
- `supabase/migrations/20260905060000_candidate_form_and_submission_schema.sql`
- `supabase/migrations/20260905130000_application_inbox_read_rpc.sql`
- `supabase/tests/application_inbox_read.sql`
- `web/src/app/application-inbox-actions.ts`
- `web/src/lib/application-inbox/server.ts`
- `web/src/lib/application-inbox/model.ts`
- `web/src/components/inbox/ApplicationInboxTable.tsx`
- existing Application Inbox web tests.

## Canonical contract

The Search strategy requires growing datasets to use server-side search/pagination; 300 ms text debounce; broad Name search from two characters; exact/near-exact Email/Phone may query immediately; default page size 25 with 25/50/100 options; indexed Name/Email/Phone search; a tested Vietnamese accent-insensitive strategy before performance UAT; Candidate-group pagination for Application Inbox; immutable-ID tie-breakers; and PII search text kept out of URL/history/telemetry/log payloads.

The starter Submission schema provides:

- trigram GIN on `submissions.full_name`;
- lower-case index on `submissions.email_snapshot`;
- digit-normalized expression index on `submissions.phone`.

Important accepted-state mismatch: `public.list_application_inbox` currently returns/searches `candidates.email`, not `submissions.email_snapshot`. The Candidate table has a unique `citext` email constraint but no separate lower-expression search index matching a substring predicate. Therefore implementation must deliberately align the authoritative Email predicate and its supporting index; it must not assume the existing Submission email index automatically supports the current Candidate email predicate.

## Accepted state already correct

1. Application Inbox is server-side through the trusted server adapter and `public.list_application_inbox`.
2. RPC pagination unit is Candidate group, not child Submission row.
3. The selected Candidate page returns complete historical child Submission rows.
4. Existing SQL regression proves Candidate-group totals, page boundaries, deterministic order, full child history and Asia/Ho_Chi_Minh date boundaries.
5. Stable ordering already includes immutable tie-breakers.
6. PII search text is component/request state and is not intentionally serialized into list-page URL state.
7. Authorization remains database/server authoritative through accepted permission/RLS behavior.

These predecessor invariants must remain intact.

## Concrete gaps

### G1 — Search predicates are not canonically normalized/index-aligned

Current RPC applies raw substring predicates to latest-row values:

- `full_name ILIKE '%' || p_query || '%'`
- `email ILIKE '%' || p_query || '%'` where `email` is `candidates.email`
- `phone ILIKE '%' || p_query || '%'`

This does not provide the required tested Vietnamese accent-insensitive Name strategy and leaves the actual Email predicate disconnected from the starter `submissions.email_snapshot` lower-case index.

The implementation must explicitly decide and document which authoritative Email value the inbox search contract uses. Preserve the accepted displayed/current Candidate email behavior unless canonical source review proves otherwise. If current Candidate email remains the search authority, add only the narrowly justified normalized/index support for that predicate rather than pretending the Submission email index applies.

Phone search must align with digit normalization. Name search must use a safe accent-insensitive normalized strategy suitable for indexed execution.

### G2 — Page-size contract differs from canonical source

Server adapter and RPC default page size are `10`. Canonical default is `25`, with user-facing choices exactly `25/50/100`.

### G3 — Debounce/minimum broad-name rule differs

UI currently reloads after `250 ms`; canonical value is `300 ms`. Server-side normalization trims/caps query text but does not enforce the two-character minimum for broad Name search.

Exact/near-exact Email/Phone usability must remain possible without allowing one-character broad Name scans. Classification must be deterministic and enforced by trusted server/database behavior, not client-only validation.

### G4 — Search performance proof is absent

Correctness regressions exist, but there is no S08-specific representative query-plan evidence for the normalized predicates/indexes. This task must add evidence suitable for later performance/UAT work without claiming a tiny fixture DB proves production p95.

## Explicit non-gaps / do not reopen

- no browser-side full-dataset search authority;
- no Submission-row pagination rewrite;
- no accepted Candidate lifecycle/bulk rewrite;
- no applicant/application-code search requirement for this task;
- no RLS weakening or privileged client query;
- no PII query persistence in URLs/history/telemetry/audit/log payloads;
- no change to accepted Interview/report/email/scan/cleanup/user-management contracts.

## Bounded implementation areas

Expected changes are limited to:

- one forward-only Supabase migration replacing/hardening `list_application_inbox` and adding only justified normalization/index support;
- SQL tests for Name accent normalization, authoritative Email matching/index alignment, digit-normalized Phone matching, page-size bounds, deterministic grouping, permission/RLS preservation and predecessor regression;
- `web/src/lib/application-inbox/*`, `web/src/app/application-inbox-actions.ts`, `web/src/components/inbox/ApplicationInboxTable.tsx` as required;
- focused behavioral web tests for debounce, PII request transport, page-size selection/reset and request parameters;
- representative local/staging-style query-plan evidence.

Do not modify accepted predecessor migrations.

## Sequencing after S08-001

A separate later task candidate is `TASK-S08-002 — Durable Distributed Rate Limiting and Abuse Controls`, because `68_RATE_LIMIT_POLICY.md` requires durable multi-instance counters for OTP request/verify, Candidate Submit/Update, upload reserve/finalize, internal search, email enqueue and PDF generation. The accepted tree does not expose a shared durable limiter primitive. This domain must not be mixed into S08-001.

Later Slice-08 domains also include performance/accessibility/release evidence, backup/restore, retention/archive/purge, rollback/deployment and UAT reconciliation. Production deployment and connected Supabase mutation remain prohibited without explicit Owner authorization.

## Decision

`PASS`

Materialize `TASK-S08-001 — Application Inbox Search and Indexed Pagination Hardening` using this v2 reconciliation and a matching v2 prompt. Implementation remains prohibited until an immutable pre-task checkpoint receives independent OMP/`eiu-reviewer` prompt review PASS and the Owner explicitly dispatches implementation.

`SOURCE_REOPEN_REQUIRED: false`
