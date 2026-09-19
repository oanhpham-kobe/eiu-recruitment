# TASK-S08-001 — Application Inbox Search and Indexed Pagination Hardening v2

## Dispatch gate

This is an implementation prompt for future Owner dispatch. It is NOT implementation authority by itself.

This v2 prompt supersedes `SLICE-08_TASK-001_v1.md` before any pre-task checkpoint or independent prompt review. Producer self-audit found one precision defect in v1: the starter lower-case Email index is on `submissions.email_snapshot`, while the accepted Application Inbox RPC currently searches/returns `candidates.email`. This v2 requires explicit authoritative Email/index alignment rather than assuming the starter index supports the current predicate.

Implementation is prohibited until:

1. this v2 prompt and `project_control/reviews/S08_001_SOURCE_RECONCILIATION_v2.md` are materialized in the control plane;
2. a new immutable annotated pre-task checkpoint is created for that exact governed baseline;
3. OMP/`eiu-reviewer` independently reviews the prompt/source reconciliation on the exact peeled checkpoint SHA and returns PASS;
4. PASS evidence is persisted; and
5. the Owner explicitly dispatches implementation.

Never substitute a moving integration branch for the governed checkpoint SHA.

Accepted Slice-07 prerequisite:

- `checkpoint/SLICE-07-accepted-001` → `b4e06a639f9e00126c1f76549067e1f6469ebc8b`
- annotated tag object `2e127b3dcd8e765f73366a8165dee26112788e33`
- closing review `SLICE-07-CLOSING-REVIEW-002`: PASS.

Functional predecessor: accepted Application Inbox implementation from Slice-03, especially `TASK-S03-004` and follow-on accepted repairs. Do not reopen unrelated lifecycle/bulk behavior.

## Source authority

Read first:

- `project_control/reviews/S08_001_SOURCE_RECONCILIATION_v2.md`
- `recruitment_webapp/review_pack/58_SEARCH_AND_INDEXING_STRATEGY.md`
- `recruitment_webapp/review_pack/38_NON_FUNCTIONAL_REQUIREMENTS.md`
- `recruitment_webapp/review_pack/67_WEB_SECURITY_BASELINE.md`
- `recruitment_webapp/review_pack/39_SECURITY_RLS_MATRIX.md`
- `recruitment_webapp/review_pack/59_RLS_POLICY_BLUEPRINT.md`
- `recruitment_webapp/review_pack/99_INDEPENDENT_REVIEW_IMPLEMENTATION_ALIGNMENT_V1_18.md`
- `recruitment_webapp/review_pack/100_TECHNICAL_PRECODE_GATE_V1_18.md`
- `recruitment_webapp/app_spec.yaml`

Inspect accepted implementation before changing anything:

- `supabase/migrations/20260905030000_identity_schema.sql`
- `supabase/migrations/20260905060000_candidate_form_and_submission_schema.sql`
- `supabase/migrations/20260905130000_application_inbox_read_rpc.sql`
- `supabase/tests/application_inbox_read.sql`
- `web/src/app/application-inbox-actions.ts`
- `web/src/lib/application-inbox/server.ts`
- `web/src/lib/application-inbox/model.ts`
- `web/src/components/inbox/ApplicationInboxTable.tsx`
- existing Application Inbox tests.

Do not modify accepted predecessor migrations. Use one new forward-only migration for database hardening.

## Bounded outcome

Harden the existing Application Inbox search/read path to conform to canonical v1.8 Search requirements while preserving all accepted Slice-03 behavior.

Required outcomes:

1. Keep search/pagination server-side through the existing trusted server adapter and `public.list_application_inbox`.
2. Implement/test a safe Vietnamese accent-insensitive Name strategy suitable for indexed execution.
3. Align the actual authoritative Email search predicate with supporting normalized/indexed storage deliberately.
4. Align Phone search with digit normalization and indexed execution.
5. Preserve Candidate-group pagination and complete historical child rows.
6. Preserve deterministic ordering with immutable ID tie-breakers.
7. User-facing default page size `25`, choices exactly `25/50/100`.
8. Search/filter debounce `300 ms`.
9. Prevent one-character broad Name scans while allowing deterministic exact/near-exact Email/Phone behavior.
10. Keep Name/Email/Phone query text out of URL/history/shareable state/logs/telemetry/audit payloads.
11. Preserve RLS, `submissions.view` authorization and Root Admin semantics.
12. Add representative query-plan/performance evidence without falsely claiming tiny-fixture production p95 proof.

## A. Forward-only database hardening

Create one new migration after the accepted migration sequence. It may replace `public.list_application_inbox(text,text,date,date,text,text,text,integer,integer)` while preserving the accepted public signature unless an independently reviewed source contradiction proves a change is required.

### A1. Name normalization

Choose and document one source-permitted Vietnamese accent-insensitive strategy:

- persisted/generated normalized searchable value maintained by trusted writes; or
- a vetted immutable normalization helper genuinely safe for expression-index use.

Do NOT label a mutable/locale/config-dependent function `IMMUTABLE` merely to satisfy PostgreSQL index syntax.

Name matching must be case-insensitive and accent-insensitive. Add only indexes justified by actual predicates.

### A2. Email authority/index alignment

The producer MUST account for this accepted-state fact:

- starter lower-case Email index: `submissions.email_snapshot`;
- accepted Inbox RPC currently projects/searches `candidates.email`.

Do not claim the Submission email index automatically supports the current Candidate-email predicate.

Preserve the accepted user-facing/current Candidate email behavior unless canonical source reconciliation demonstrates that Inbox search authority should instead include/use Submission snapshots. Whichever Email authority is retained must have an intentional normalized/indexed predicate suitable for the canonical Search strategy.

If the current Candidate email remains authoritative, introduce only narrowly justified index support for that actual field/predicate. Do not add duplicate/unrelated indexes.

Email matching is case-normalized. User wildcard characters are data, not authority to create unintended SQL wildcard semantics.

### A3. Phone normalization

Phone search must normalize digits so punctuation/spacing differences do not defeat legitimate matching and must align with an indexable predicate. Preserve accepted returned/displayed Phone semantics.

### A4. Search classification / minimum Name rule

Empty query means no text filter.

A one-character generic text query must not trigger a broad Name scan.

Exact/near-exact Email or Phone input may search immediately as allowed by canonical source. Define a deterministic classification rule based on normalized input shape; do not rely on client-only checks or arbitrary wildcard behavior.

Trusted server/database behavior must remain safe when invoked directly.

### A5. Preserve grouped pagination

Keep the accepted architecture:

1. rank latest Submission per Candidate;
2. apply current Candidate-group filters;
3. count Candidate groups;
4. page Candidate parents;
5. return the complete historical Submission group for each selected Candidate.

Do not paginate child Submission rows independently.

Preserve deterministic ordering and immutable ID tie-breakers.

### A6. Page bounds

User-facing sizes:

`25`, `50`, `100`.

Default user/server adapter size:

`25`.

The RPC may preserve bounded explicit small page sizes for regression/internal calls if necessary for predecessor compatibility, but invalid/unbounded values must be clamped and the RPC default must become 25. The user-facing adapter/UI exposes only 25/50/100.

## B. Web adapter/UI hardening

### B1. Server adapter

Update `web/src/lib/application-inbox/server.ts` as needed:

- default page size 25;
- typed/bounded user-facing sizes 25/50/100;
- retain query trim/length cap;
- never log clear-text search value;
- preserve authenticate/authorize behavior and structured read errors;
- preserve RPC-only growing-dataset access.

Update `queryApplicationInbox` typing/transport as needed to carry the selected page size.

### B2. Component behavior

Update `ApplicationInboxTable.tsx` as needed:

- 300 ms search/filter debounce;
- accessible page-size selector with exactly 25/50/100;
- default 25;
- page-size change resets to page 1;
- page/filter/page-size/search context change preserves existing page-scoped selection-reset semantics;
- no Name/Email/Phone value in URL/history;
- no client-only minimum-query safety assumption.

## C. Security and PII boundaries

- no browser-side privileged DB query;
- no service-role credentials in browser bundles;
- RLS/permission remains authoritative;
- no clear-text PII search term in URL/history/analytics/audit/server logs;
- errors must not echo sensitive query values;
- search hardening never replaces Auth/RLS/permission checks.

## D. Query-plan / NFR evidence

Add focused local evidence that covers at least:

1. accented stored Name matched by unaccented query;
2. case-normalized authoritative Email match;
3. digit-normalized Phone match across formatted/unformatted forms;
4. deterministic Candidate-group pagination with full child history;
5. page-size default and bounds;
6. authorization denial/RLS preservation;
7. wildcard/special-character safety;
8. representative planner/index evidence on sufficiently populated local data.

Use `EXPLAIN (ANALYZE, BUFFERS)` or equivalent planner evidence appropriate to the chosen index strategy. Avoid brittle assertions forcing an index on a tiny table. Record what the evidence proves and what remains for later staging p95 UAT.

This task does NOT close the global Production UAT/performance gate.

## E. Required regression coverage

Preserve and run at minimum:

- `supabase/tests/application_inbox_read.sql`;
- Candidate lifecycle/inbox bulk-token database regressions;
- Application Inbox web tests;
- bulk Application Inbox UI tests;
- relevant Application lifecycle regressions.

Add behavior-driven focused tests for new Search/page-size behavior, not source-regex-only acceptance.

Expected web gates:

- focused Application Inbox tests;
- full `npm run test`;
- `npm run lint`;
- `npm run typecheck`;
- `npm run build`;
- `npm run design:check`;
- browser/design verification when interactive page-size behavior changes.

Expected database gates:

- clean disposable/unlinked local migration replay;
- new S08-001 Search contract test;
- accepted Application Inbox SQL regression;
- relevant crossed predecessor regressions;
- DB lint.

Governance:

- `python project_control/validate_control_plane.py`
- `python project_control/validate_omp_native.py`
- fresh exact-SHA Integration CI and Governance CI after serialized integration.

## F. Explicit out of scope

Do NOT implement in S08-001:

- durable distributed rate limiting / abuse controls (`68_RATE_LIMIT_POLICY.md`);
- live email provider runtime;
- scanner provider runtime;
- production scheduler/daemon;
- archive/purge/long-term retention;
- backup/restore implementation;
- Vercel production deployment;
- connected Supabase migration/application;
- Production UAT sign-off;
- global accessibility re-certification;
- unrelated Interview/Report/User search redesign;
- accepted Candidate lifecycle/bulk command rewrites;
- `TASK-S08-002` implementation or materialization in this lifecycle step.

## G. Producer/reviewer boundaries

ChatGPT is producer/executor/coordinator.

OMP/`eiu-reviewer` is the independent prompt/implementation/final reviewer where required and must not implement or repair its own findings.

Any OMP local mechanical action must be explicitly authored by ChatGPT and non-discretionary.

No accepted predecessor checkpoint may move.

No `main` mutation, Vercel deployment or connected Supabase mutation is authorized.

## Stop condition

For the current pre-implementation lifecycle, stop after this exact v2 prompt/source baseline is materialized, captured by an immutable pre-task checkpoint, independently prompt-reviewed PASS, and that PASS evidence is persisted. Implementation begins only on explicit Owner dispatch.

`SOURCE_REOPEN_REQUIRED: false`
