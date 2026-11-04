# Local workflow repair and verification — 2026-11-05

Status: **VERIFIED LOCALLY / NOT ACCEPTED OR INTEGRATED**.

Product repair commit: `118c87cfb2d0385a8e2135bbedfb547bb699d186`.
Base reporting commit: `325d3a5e5357d94ec0db891231345bb4606abb93`.
Branch: `implementation/recovery-package-009-rec04-residual-deadlocks`.

## Authorized scope

Owner requested repair of audited defects, local workflow verification, and planning for internal template-based interviewer feedback. Owner confirmed reviewers are internal `@eiu.edu.vn` users and selected local work first; hosted mail/scanner configuration is deferred. No new questionnaire/report-template feature was implemented without its source/template decisions.

## Repairs

1. **Assignment / Internal User deadlock:** new forward migration `20261104172334_internal_user_actor_target_lock_order.sql` amends seven effective existing-target writers to lock sorted actor/target rows before User advisories. It preserves existing Email/Unit ordering, idempotency, versions, protected Root behavior, audit and grants; actor authorization is rechecked after waiting. Historical migrations/checkpoints remain unchanged.
2. **Meaningful regression:** `internal_user_actor_lock_concurrency_test.sh` exercises both actor/target UUID orders, committed state, version, audit/replay and permission revocation during a wait. Parent reproduced RED on the 49-migration base; high target deadlocked. After repair both orders and post-wait denial pass. It is included in the lifecycle suite.
3. **R3 stale assertion:** role-removal/assignment race now asserts the existing precise structured `NOT_FOUND` owner rejection rather than requiring a late trigger exception. It also asserts removed role, unchanged owner and zero failed-bulk audit.
4. **Management route composition:** root layout owns AppShell; Users and Master Data render content only. Browser fixtures use an external shell, and production-route tests assert one shell/main and no nested main.
5. **Private document failures:** removed runtime fake-PDF success for mock-host fetch failures. Both transport failures and unexpected preview exceptions return safe HTTP 500 without leaking signed URLs. Authorization, relationship checks, audit and signing order are preserved.
6. **Test credibility:** removed three self-asserting Candidate tests; retained adapter tests describe adapter behavior rather than claiming database idempotency/concurrency proof.
7. **REC-05 fixture:** resolves canonical active `CV_RESUME` by code/scope instead of assuming a seed UUID. The original clean-database setup failure was reproduced; corrected original suite now passes.
8. **CI coverage:** added REC-05/REC-15 concurrency and real physical Storage checks to Integration CI, including Node/dependency setup and clean isolation before physical checks. Storage runtime/reservation/dependency changes select both web/database; synthetic Git-range tests verify selectors.
9. **Recovery truth:** active recovery lives in run state; ledger is derived. Corrected Package006/007 complete SHAs, removed false REC-20 readiness, retained historical acceptance and current unaccepted status. Validator regressions reject hidden/unrecorded active work and premature next-REC reporting.
10. **Dependency patches:** Next 16.3.4 → 16.4.5, matching SWC/transitive patches and current compatible security fixes in lockfile. No forced major upgrade. Policy source: `76_DEPENDENCY_BASELINE_POLICY.md`.

Dependency advisory sources inspected on 2026-11-05:

- [Next.js Image Optimization advisory](https://github.com/vercel/next.js/security/advisories/GHSA-2464-fhr4-w9xw).
- [Next.js Server Actions advisory](https://github.com/vercel/next.js/security/advisories/GHSA-p3m5-59mp-jv5r).
- [sharp / librsvg advisory](https://github.com/lovell/sharp/security/advisories/GHSA-wq5f-xc86-pv6w).

The installed versions were affected according to npm audit. This is dependency exposure evidence, not proof the application was exploited or every advisory path was reachable.

## Fresh parent verification

| Check | Observed result | Scope / limit |
|---|---|---|
| New concurrency regression, base49 | RED | Low target passed, high target produced actual PostgreSQL deadlock |
| New concurrency regression, final50 | PASS | Both UUID orders, audit/version/replay and post-wait authorization |
| Full lifecycle suite | PASS | Former CI blocker and R2/R3/new regression |
| Full local Integration-CI-shaped database sequence | **45/45 steps PASS** | Includes clean replay, affected/crossed SQL, real-role confidentiality, concurrency/fencing, upgrade, REC05/15/18/19, standalone bulk, physical Storage, DB lint |
| Independent clean replay | **50 migrations PASS** | Isolated PostgreSQL platform bootstrap, no business data copied |
| Base49 → final50 upgrade smoke | PASS | Complete Candidate sentinel row unchanged; not a representative populated production upgrade |
| Web tests | **383 PASS / 0 fail / 0 skipped** | Fresh build; unit/model/adapters/browser fixtures and production smoke tests; test counts are not product-completeness percentages |
| Production management routes | PASS | Actual anonymous `/users` and `/master-data` routes each have one shell/main; authorized CRUD separately covered by fixtures/DB tests, not asserted from anonymous smoke |
| Typecheck / build | PASS | Next16.4.5 |
| Lint / design contract | PASS | Lint retains six pre-existing warnings, no lint errors |
| Dependency audit | **0 vulnerabilities** | Fresh npm audit; temporal snapshot |
| Governance regression | **10 PASS** | Recovery reporting and actual impact-shell execution against synthetic Git histories |
| Control-plane / OMP validators | PASS | Does not itself establish product completeness |
| Independent review | PASS | Separate read-only reviewer inspected SQL/effective catalog, web/privacy, CI, recovery reporting and manifests. Producer results were not used as sole acceptance evidence |

All runtime data was synthetic. Original Docker stacks and root-checkout personal edits were preserved. Verification used a separate PostgreSQL container and a separately named Supabase project with independent ports.

The full Supabase sequence used CLI **2.116.0** and repository configuration/migrations/tests. Local Node was **24.18.0**, npm **12.0.2**; CI pins Node24.20.0/npm11.19.0. This local run is not a claim that GitHub CI ran or passed.

Windows-host adaptations were outside the repository: the Docker development-container alias was redirected to the isolated project, Linux `/proc` UUID reads used equivalent random UUID generation, and Python/jq used installed native executables. SQL, business assertions and role boundaries were retained. Linux PostgreSQL reproduction separately exercised the original concurrency code. Initial host/setup errors were corrected before the final all-green run; they were not relabeled as product failures or ignored.

Raw sanitized logs and structured step results remain in the chat's local artifact workspace; this report is the compact durable verification receipt. No secrets or real recruitment records are included.

## Feature plan delivered

`project_control/research/INTERNAL_INTERVIEW_FEEDBACK_PLAN_2026-11-05.md` is a draft, not a released source contract:

- HR selects Application/Interview round, a fixed template version and participants, then sends invitations.
- Each internal reviewer logs in, sees allowlisted Candidate details, saves draft answers and submits their own response.
- HR tracks completion, produces an attributed consolidated draft from pinned revisions, reviews and publishes it using the Owner's report template.
- Template changes do not silently rewrite old responses/reports; knowing a URL never grants access.
- No scoring or automatic hiring decision is added; no AI consolidation or change to current Final Decision Source is assumed.
- Candidate dossier generation remains a separate scope awaiting the Owner's description.

## Remaining completion boundaries

This repair does **not** claim the whole Phase-1 product is complete. In particular:

- HR document mutation UI, Interview materials, content-correct PDF and remaining full VI/EN/mobile/accessibility composition work were not implemented by this defect-repair checkpoint.
- REC-12 report-precedence source decision and abuse-control authority remain open. A generic PDF renderer must not be falsely gated solely on deferred official pixel layout; its actual source dependencies still need resolution.
- Hosted mail delivery, real malware-provider execution, recurring operational workers and deployed multi-persona UAT remain unverified and are deferred by Owner's local-first choice.
- Backup/private-object restore, legal/privacy/archive/purge, operational response and production promotion have not been accepted.
- The new feedback page/report templates need the Owner's question/report samples and a controlled source change before implementation.

Package009 remains **unaccepted and unintegrated**. No GitHub push, main mutation, hosted migration, deployment, live mail or malware-provider request occurred. A selected final acceptance candidate still needs independent exact-SHA lifecycle closure and authorized Integration/Governance CI; governance-only reporting commits must not substitute skipped product jobs for proof. Use `full_verification=true` when the approved acceptance procedure requires full domain proof.

The previously requested Package004/REC-05 retrospective now has its fixture defect reproduced and repaired locally; it is not a claim every historical acceptance obligation was re-certified. Do not auto-release another REC from this checkpoint.
