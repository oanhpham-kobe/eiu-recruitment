# TASK-S08-001 — Application Inbox Search and Indexed Pagination Hardening

## Dispatch gate

This is an implementation prompt for future Owner dispatch. It is NOT implementation authority by itself.

Implementation is prohibited until:

1. this prompt and `project_control/reviews/S08_001_SOURCE_RECONCILIATION_v1.md` are materialized in the control plane;
2. a new immutable annotated pre-task checkpoint is created for that exact governed baseline;
3. OMP/`eiu-reviewer` independently reviews the prompt/source reconciliation on the exact peeled checkpoint SHA and returns PASS;
4. the PASS evidence is persisted; and
5. the Owner explicitly dispatches implementation.

Never substitute a moving integration branch for the governed checkpoint SHA.

Accepted Slice-07 closure prerequisite:

- `checkpoint/SLICE-07-accepted-001` → `b4e06a639f9e00126c1f76549067e1f6469ebc8b`
- annotated tag object `2e127b3dcd8e765f73366a8165dee26112788e33`
- closing review `SLICE-07-CLOSING-REVIEW-002`: PASS

Functional predecessor: accepted Application Inbox implementation from Slice-03, especially `TASK-S03-004` and its follow-on accepted repairs. Do not reopen unrelated lifecycle/bulk behavior.

## Source authority

Read first:

- `project_control/reviews/S08_001_SOURCE_RECONCILIATION_v1.md`
- `recruitment_webapp/review_pack/58_SEARCH_AND_INDEXING_STRATEGY.md`
- `recruitment_webapp/review_pack/38_NON_FUNCTIONAL_REQUIREMENTS.md`
- `recruitment_webapp/review_pack/67_WEB_SECURITY_BASELINE.md`
- `recruitment_webapp/review_pack/39_SECURITY_RLS_MATRIX.md`
- `recruitment_webapp/review_pack/59_RLS_POLICY_BLUEPRINT.md`
- `recruitment_webapp/review_pack/99_INDEPENDENT_REVIEW_IMPLEMENTATION_ALIGNMENT_V1_18.md`
- `recruitment_webapp/review_pack/100_TECHNICAL_PRECODE_GATE_V1_18.md`
- `recruitment_webapp/app_spec.yaml`

Inspect accepted implementation before changing anything:

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

Harden the existing Application Inbox search/read path so it conforms to the canonical v1.8 Search strategy while preserving all accepted Slice-03 behavior.

Required outcomes:

1. Keep search and pagination server-side through `public.list_application_inbox` and the existing server action/adapter boundary.
2. Implement and test a safe Vietnamese accent-insensitive Name search strategy suitable for indexed execution.
3. Align Email and Phone search predicates with normalized/indexed representations rather than leaving raw unindexed `%term%` scans as the only strategy.
4. Preserve Candidate-group pagination: page Candidate parents first, then return complete historical child Submission rows for each selected Candidate.
5. Preserve deterministic ordering with immutable ID tie-breakers.
6. Make the canonical UI paging contract default `25` with user choices `25 / 50 / 100`.
7. Use a `300 ms` search/filter debounce and prevent one-character broad Name searches.
8. Keep Name/Email/Phone query values out of browser URL/history/shareable filter state and out of logs/telemetry/audit payloads.
9. Preserve RLS, `submissions.view` authorization and Root Admin semantics.
10. Add representative correctness and query-plan evidence without claiming that a tiny fixture dataset proves production p95.

## A. Forward-only search/index migration

Create one new migration after the accepted Slice-07 migration sequence. The migration may replace `public.list_application_inbox(...)` while keeping its existing public signature unless an independently reviewed source contradiction requires otherwise.

### A1. Normalization strategy

Choose and document one source-permitted Vietnamese accent-insensitive strategy:

- a persisted/generated normalized searchable value maintained by trusted writes; or
- a vetted immutable normalization helper that is genuinely safe for expression-index use.

Do NOT mark a mutable/locale/config-dependent function `IMMUTABLE` merely to satisfy PostgreSQL index syntax. The implementation review must be able to explain why the chosen normalization is safe and deterministic.

The normalized Name strategy must be case-insensitive and accent-insensitive. Add only the indexes justified by the actual predicates.

### A2. Name / Email / Phone behavior

Search authority is exactly the canonical Application Inbox set:

- Submission/Candidate name;
- email;
- phone;
- operational filters already accepted.

Do not invent applicant/application-code search for this task.

Requirements:

- broad Name search requires at least 2 trimmed characters;
- empty query means no text filter;
- Email matching is case-normalized;
- Phone matching uses digit normalization so formatting punctuation does not defeat a legitimate match;
- exact/near-exact Email/Phone behavior may remain responsive within the canonical strategy, but no single-character broad Name scan is allowed;
- wildcard characters supplied by a user are data, not authority to construct unintended SQL wildcard semantics. If `LIKE`/`ILIKE` is used, explicitly handle escaping or use an alternative safe predicate.

### A3. Preserve group pagination

The existing accepted read model already:

1. ranks latest Submission per Candidate;
2. filters Candidate groups;
3. counts Candidate groups;
4. pages Candidate groups;
5. returns the complete historical Submission group for each Candidate on the selected page.

Preserve this architecture.

Ordering must remain deterministic and include immutable IDs as tie-breakers. Do not paginate child Submission rows independently.

### A4. Page bounds

Canonical user-facing page sizes:

`25`, `50`, `100`

Default user/server adapter page size:

`25`

The public RPC may preserve its accepted bounded compatibility for explicit test/internal page sizes if needed, but it must still clamp invalid/unbounded input and must default to 25. The user-facing adapter/UI must expose only 25/50/100.

Page-size changes reset to page 1 and clear page-scoped selection consistently with existing filter/page changes.

## B. Web adapter/UI hardening

### B1. Server adapter

Update `web/src/lib/application-inbox/server.ts` as required:

- default page size 25;
- bounded user-facing page-size validation for 25/50/100;
- query trim/length cap retained;
- do not log the clear-text search value;
- preserve session/authorization ordering and existing structured read errors;
- preserve RPC-only data access for the growing inbox dataset.

`queryApplicationInbox` must accept/pass the selected page size in a typed bounded form.

### B2. Component behavior

Update `ApplicationInboxTable.tsx` as required:

- debounce search/filter reload at 300 ms;
- provide an accessible page-size selector with exactly 25/50/100;
- default 25;
- changing page size resets page to 1;
- preserve existing selection-reset behavior when the page/filter/search context changes;
- no Name/Email/Phone search text in URL state or browser history;
- operational non-sensitive filters may remain local state for this bounded task; broader URL-state refactoring is not required unless needed for the accepted implementation contract.

For the minimum broad-Name rule, UI and server behavior must be deterministic. A one-character generic text query must not cause a broad database Name scan. Do not rely only on client validation; the trusted server/database path must remain safe when called directly.

## C. Security / PII boundaries

- No browser-side privileged DB query.
- No service-role credential in browser bundles.
- RLS/permission behavior remains authoritative.
- Search terms containing Name/Email/Phone are sensitive request data and must not be serialized into browser URLs, browser history, analytics events, audit metadata, or server logs.
- Existing logging redaction utilities remain authoritative; do not add search-term logging for performance diagnostics.
- Error messages must not echo the sensitive query.
- Search hardening does not replace Auth/RLS/permission checks.

## D. Query-plan and NFR evidence

Add a dedicated local test/evidence path for representative search/index behavior.

At minimum cover:

1. accent-insensitive Name match (for example accented stored name vs unaccented query);
2. case-normalized Email match;
3. digit-normalized Phone match across formatted/unformatted forms;
4. deterministic Candidate-group pagination with complete child history;
5. page-size default/bounds;
6. authorization denial and RLS preservation;
7. wildcard/special-character handling;
8. representative `EXPLAIN (ANALYZE, BUFFERS)` or planner evidence on sufficiently populated local data for the implemented predicates/indexes.

Do not make a brittle assertion that PostgreSQL must choose a specific index on a tiny table. The performance evidence should seed enough representative rows and/or use planner inspection appropriate to the chosen index strategy, and should document what it proves and what remains for staging p95 UAT.

The task does NOT close the global Production UAT/performance gate. It only produces trustworthy Search hardening evidence that later Slice-08 release work can consume.

## E. Required regression coverage

Preserve and run accepted predecessor regressions, especially:

- `supabase/tests/application_inbox_read.sql`;
- Candidate lifecycle/inbox bulk token regressions;
- Application Inbox web tests;
- bulk Application Inbox UI tests;
- Application lifecycle tests where the inbox read state is consumed.

New focused tests must assert behavior, not merely source-regex presence.

Expected web gates:

- focused Application Inbox tests;
- full `npm run test`;
- `npm run lint`;
- `npm run typecheck`;
- `npm run build`;
- `npm run design:check`;
- browser/design gate if the page-size UI changes interactive behavior.

Expected database gates:

- clean local migration replay on disposable/unlinked Supabase;
- new S08-001 search contract test;
- existing Application Inbox SQL regressions;
- relevant crossed predecessor regressions;
- DB lint.

Governance:

- `python project_control/validate_control_plane.py`
- `python project_control/validate_omp_native.py`
- exact-SHA Integration CI and Governance CI after serialized integration.

## F. Explicit out of scope

Do NOT implement in S08-001:

- durable distributed rate limiting (`68_RATE_LIMIT_POLICY.md`) — reconcile as a separate later task;
- live email provider runtime;
- scanner provider runtime;
- production scheduler/daemon;
- archive/purge/long-term retention operations;
- backup/restore implementation;
- Vercel production deployment;
- connected Supabase migration/application;
- production UAT sign-off;
- global accessibility re-certification;
- unrelated Interview/Report/User search redesign;
- accepted Candidate lifecycle/bulk command rewrites.

## G. Review and producer boundaries

ChatGPT is implementation producer/executor/coordinator.

OMP/`eiu-reviewer` is the independent reviewer and must not implement or repair its own findings.

Any local mechanical command delegated to OMP must be explicitly authored by ChatGPT and must not become discretionary implementation.

No accepted predecessor checkpoint may be moved.

No `main` mutation, Vercel deployment, or connected Supabase mutation is authorized.

## Stop condition

For the current pre-implementation lifecycle, stop after the exact prompt/source baseline receives an independent prompt review PASS and the governed implementation baseline is recorded. Implementation begins only on explicit Owner dispatch.

`SOURCE_REOPEN_REQUIRED: false`
