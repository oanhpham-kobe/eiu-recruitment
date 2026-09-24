# TASK-S08-002 — Independent Prompt & Source Review Evidence v1

WORK_ID: S08-002-PROMPT-REVIEW-001

REVIEWER: OMP_EIU_REVIEWER

TRANSPORT: OWNER_MESSAGE

REVIEWED_SHA: c3fd09b5cbe38205802b079560aff8452c6bbe3b

GOVERNED_CHECKPOINT: checkpoint/pre-S08-002-001

CHECKPOINT_TAG_OBJECT: f5d9b5b2d5e3ef86514d23bb76f8ccc76b9ef003

EXPECTED_PEELED_SHA: c3fd09b5cbe38205802b079560aff8452c6bbe3b

SOURCE_BASELINE_SHA: 8dcb0a5d7ce1be9d82e3448c01cdc1643e3ac8c4

SOURCE_RECONCILIATION_REVIEWED_SHA: a99375932e95805a8b52a6a159eb94a755c88986

VERDICT: PASS

SOURCE_REOPEN_REQUIRED: false

PROMPT_REPAIR_REQUIRED: false

IMPLEMENTATION_AUTHORIZED: NO

FINDINGS: NONE

EVIDENCE_ORIGIN: Owner-transported OMP output. This artifact is persisted by the producer/coordinator; it does not claim reviewer-native repository mutation.

---

## Exact SHA and checkpoint assessment

OMP verified exact reviewed commit `c3fd09b5cbe38205802b079560aff8452c6bbe3b` and immutable pre-task checkpoint `checkpoint/pre-S08-002-001`.

Checkpoint verification:

- annotated tag object: `f5d9b5b2d5e3ef86514d23bb76f8ccc76b9ef003`
- peeled target: `c3fd09b5cbe38205802b079560aff8452c6bbe3b`

The materialization delta from `b5240c7df268ee8989f2c1d7faefa6b69f56a4b0` contained exactly five governance files:

- `project_control/AUTONOMY_RUN_STATE.yaml`
- `project_control/CURRENT_STATE.md`
- `project_control/EVIDENCE_INDEX.yaml`
- `project_control/SLICE_REGISTRY.yaml`
- `project_control/TASK_REGISTRY.yaml`

No runtime product source, migration, SQL test, Web source, or workflow file changed in the materialization commit. `git diff --check` passed.

## Canonical rate matrix assessment

OMP confirmed prompt `project_control/prompts/SLICE-08_TASK-002_v1.md` faithfully preserves the canonical configurable initial policies:

1. Candidate OTP request — normalized email 5/15 min; trusted client IP 20/15 min; 429 + Retry-After.
2. OTP verify — identity 10/15 min; trusted client IP 50/15 min; 429 + Retry-After.
3. Candidate Submit — candidate identity with required IP dimension; 5/hour and 20/day; 429.
4. Candidate Update Save — candidate_id + trusted IP; 30/15 min; 429 + Retry-After before mutation; zero partial Save.
5. Upload reserve/completion/finalize — candidate/app_user identity 30/15 min and trusted client IP 100/15 min; 429.
6. Internal Search — aggregate authenticated app_user_id 120/min; 429.
7. Email Enqueue — app_user_id + email_type 60/hour with 10/min burst, exact entity secondary dimension; 429.
8. PDF Generation — future app_user + exact entity 20/hour; no synthetic runtime PDF endpoint.

## Accepted-tree boundary assessment

OMP confirmed:

- browser-direct Candidate `signInWithOtp` must move behind an app-controlled server boundary without exposing service-role credentials;
- OTP verification remains same-origin/provider-backed and gains limiter enforcement before provider verification;
- Candidate Submit/Update limiting is additive to accepted trusted-command/RPC contracts and must not reopen privacy/version/idempotency/document/outbox semantics;
- Candidate interactive upload boundaries are `reserveUploadAction` and `completeAndStageUploadAction`;
- scanner workers, CLEAN continuation, cleanup operations and document binding inside Submit/Update are not double-charged;
- internal search uses one aggregate quota across Application Inbox, Interview/Application grouped search, Interview option searches and HR Report free-text search;
- empty ordinary page/filter refreshes are not charged;
- bulk email is rate-accounted per attempted new enqueue item while preserving `PER_ITEM_ENQUEUE_RESULT` and aggregate actor/type ceilings;
- provider delivery throttling remains distinct from queue-side enqueue limiting;
- no runtime PDF endpoint currently exists and none is invented by this task.

## Architecture and security assessment

OMP accepted the prompt architecture requiring:

- durable shared multi-instance state;
- PostgreSQL/Supabase-backed enforcement as repository-default architecture;
- atomic multi-rule/window consumption with deterministic ordering;
- no partial quota debit when another mandatory rule blocks;
- no concurrency overshoot;
- private limiter state;
- bounded expiry/cleanup;
- trusted client-IP resolution using documented platform/proxy authority only;
- forged forwarding-header negative tests;
- literal HTTP 429 at user-facing protected boundaries and Retry-After where required;
- narrow same-origin Route Handler transport when Server Actions cannot prove literal HTTP status/header semantics;
- additive defense that never replaces Auth, RLS, RBAC, same-origin, validation, optimistic locking or idempotency;
- direct database RPC paths protected wherever browser-authenticated execution would otherwise bypass the limiter;
- data-minimized Security Audit that excludes OTP/token/session/signed URL/file content/raw PII search values and is bounded against audit amplification.

## Verification contract assessment

OMP confirmed the prompt requires adequate proof for:

- exact threshold/window behavior;
- multi-rule atomic debit;
- reset/expiry boundaries and stale-row cleanup;
- concurrent independent clients sharing durable state;
- forged-header resistance;
- direct-RPC bypass attempts;
- literal 429 / Retry-After transport;
- raw-query sanitization;
- blocked protected-state no-op behavior;
- bulk email per-item behavior;
- Candidate notification atomicity;
- upload non-double-charge semantics;
- all reachable internal-search surfaces;
- Integration CI wiring for new SQL/Web tests;
- clean disposable-local Supabase replay and DB lint;
- Web lint/typecheck/build/security regression coverage.

Web/database runtime suites were not run during this review because the reviewed delta was planning/governance/prompt-only.

## Governance assessment

OMP verified:

- `TASK-S08-002.status = PLANNED`;
- `slice_08_planning.status = S08_002_MATERIALIZED_AWAITING_INDEPENDENT_PROMPT_REVIEW`;
- prompt review was PENDING at review time;
- `implementation_started = false`;
- `implementation_authorized = false`;
- prompt-review hard stop was active;
- `python project_control/validate_control_plane.py`: PASS — 10 slices, 43 tasks, execution mode AUTONOMOUS;
- `python project_control/validate_omp_native.py`: PASS — 24 project skills, 5 project agents, 0 machine-specific paths.

## Blocking findings

NONE.

## Non-blocking observations

NONE.

## Final review statement

PASS applies strictly to exact SHA `c3fd09b5cbe38205802b079560aff8452c6bbe3b` at `checkpoint/pre-S08-002-001`.

This prompt-review PASS authorizes only readiness for explicit Owner implementation dispatch. It does not itself authorize implementation.

The review does not authorize mutation of `main`, deployment, Vercel configuration, connected/hosted Supabase, production secrets, or movement of accepted checkpoints.
