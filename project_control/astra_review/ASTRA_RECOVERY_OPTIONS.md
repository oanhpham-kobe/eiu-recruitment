# EIU Recruitment — Phase D recovery options and strategic decision

## 1. Decision context

### Objective and authority

Optimize the **shortest safe path to a usable Phase-1 product**, including functional non-production UAT, complete mandatory capability and safe real-data production. Total recovery cost includes implementation, missing capability, security/concurrency repair, interfaces, retained data/history, operations, regression, verification, independent review, CI, deployment/recovery proof, knowledge transfer and rollback. Neither reused code nor newly written code earns value merely by existing.

Repository: `oanhpham-kobe/eiu-recruitment`. Review branch: `review/astra-strategic-review-20260927`. Starting pushed review commit: `0ef83091f552d76d022fc2719b8eeac4503a63e1`. Technical baseline: `8dcb0a5d7ce1be9d82e3448c01cdc1643e3ac8c4`. The complete baseline-to-start diff is eleven review/research Markdown files, not runtime changes. This is Phase D only, under `project_control/research/ASTRA_MEDIUM_MASTER_HANDOFF_2026-09-27.md:341-381` and the current Owner's more specific continuation. No Phase-E task plan, task materialization, code change, cloud mutation or deployment is authorized.

### Frozen evidence and limitations

All three byte hashes and final markers matched before analysis. No earlier artifact is edited; disagreements belong here.

| Frozen artifact under `project_control/astra_review/` | SHA-256 | Final marker |
|---|---|---|
| `ASTRA_GREENFIELD_PHASE1_ARCHITECTURE.md` (Greenfield A) | `646adc6ff4081c7f748b4191f740e0c3b1971857567788668ace41b2907dabe8` | `GREENFIELD_PHASE_A_FROZEN: YES` |
| `ASTRA_PHASE_B_CURRENT_STATE_AUDIT.md` (Audit B) | `a4e370c4cef7620c943acdbc417017ad7948cc3ee2098d7a7240bf142db7f83e` | `PHASE_B_CURRENT_STATE_AUDIT_FROZEN: YES` |
| `ASTRA_GAP_MATRIX.md` (Matrix C) | `d283981d28634bd88b79c4aaec088928c72c0d3bab73a92eeab3ae5a55efa55b` | `PHASE_C_GAP_MATRIX_FROZEN: YES` |

“Greenfield A” means the frozen proposal; “Option A” below means minimal repair. Matrix C's 62 KEEP, 34 ADD, 14 FIX, 12 SIMPLIFY and 4 REMOVE / DEFER rows are not a weighted vote. A small number of interacting defects could outweigh many retained components. Conversely, many missing screens do not erase the cost of rebuilding existing behavior.

Greenfield A remains accepted with isolation/product-ambiguity caveats. Audit B remains accepted with caveats: **F01 was browser-reproduced; F02/F04–F07 are source-derived, not observed production incidents or fresh Phase-D SQL reproductions.** Docker was unavailable in B; its availability is not retested here. Source presence and historical tests are not connected journey certification. Missing workers mean **NO LOCATED REPOSITORY RUNTIME**, not proof no undocumented external service exists. Cloud configuration, retained data volume and pending work remain unknown.

Two read-only adversarial reviews steelmanned minimal repair and substantial rebuild. The parent assessed selective recovery, checked decisive source and owns the final comparison. No worker success claim constitutes product acceptance. This document adds no new platform-version guarantee: platform details remain frozen evidence or canonical requirements, and must be verified for an actual target before deployment. No new external platform-documentation claim or cloud inspection is made.

### Evidence index for strategic claims

The immutable matrix supplies exact source aliases and citations; the following bounded source checks anchor the disputed economics.

| Evidence | Strategic significance |
|---|---|
| Matrix C §§1–8, row IDs P/S/D/A/X/R/G/Z; §9 F01–F23 crosswalk; §10 repair/replacement comparisons; §11 required complexity | Full capability, defect and retained-invariant accounting; no subsystem replacement advantage yet demonstrated |
| `web/src/lib/commands/runner.ts:12-127` | Small explicit actor→active→authorize→validate→execute/error boundary, not evidence a new command platform is needed |
| `web/src/lib/commands/interview-lifecycle.ts:36-147`; `web/src/lib/reports/hr-server.ts:98-160` | Different actor/result/error conventions really exist; their consolidation must preserve permission modes, validation and caller contracts |
| `web/src/components/reports/HrReportView.tsx:287-355` | Independently dirty note/report drafts and conflict bases survive refresh; state extraction/rebuild has behavioral cost |
| Matrix C E10–E15; Audit B §4 | Effective Interview grants, lock inversions, nullable expected versions, omitted reactivation recalculation and late-batch JSON failure are authoritative SQL problems; rewriting JSX does not cure them |
| Matrix C E18–E21, X01–X11 | Mail/scan/cleanup contracts and real cleanup runner have value, but provider execution/launch and generated PDF remain incomplete |
| `recruitment_webapp/review_pack/44_DEPLOYMENT_OPERATIONS.md:3-62,75-111` | Non-production isolation, additive-first migration, no rewritten accepted migrations, direct-role parity, separate DB/object recovery, monitoring, scan and cleanup requirements |
| Same deployment document :83-91 versus `project_control/AUTONOMY_PARALLEL_GOVERNANCE.md:343-347` and `.github/workflows/integration-ci.yml:40-99` | Canonical every-integration-commit DB-CI requirement conflicts with narrower governance/domain skips; no option may bank unauthorized skip savings |
| Matrix C G01–G16, E28–E31 | Independent review/composition caught real defects; current policy already narrows rechecks; false slice completeness and stale derived reporting need correction regardless of strategy |
| Matrix C Z01–Z08, E32–E36 | Notice/retention operations, performance/abuse proof, report precedence tension and normative prototype boundary remain obligations, not hidden deferrals |

### Four different completion boundaries

- **DIAGNOSTIC PREVIEW:** authorized, protected, isolated synthetic deployment to inspect limitations. A rendered shell or queue-only demonstration can qualify only as diagnostic, never as functional UAT.
- **FUNCTIONAL UAT PREVIEW:** a declared connected workflow on isolated non-production Supabase and Vercel Preview or equivalent authorized non-production target; no real recruitment PII; real test authentication, malware verdicts and provider effects wherever promised. Its bounded workflow scope must be disclosed.
- **PHASE-1 PRODUCT COMPLETENESS:** every mandatory persona, interaction, administration, document, report, language/mobile/accessibility and operational capability. The first connected case is not this boundary.
- **PRODUCTION-READY:** complete required capability plus real-data authorization/privacy, deployed parity, supported configuration, recovery, capacity/monitoring, runbook rehearsal and explicit Owner release authorization. This review grants none of that authorization.

## 2. Option A — Minimal repair

### Strongest credible definition

Keep the current modular Next application, Supabase Auth/private Storage, relational aggregate identities, PostgreSQL transactional intent authority, most typed adapters and existing page/state organization. Repair the actual crossed invariants and finish mandatory missing capabilities. “Minimal” describes architectural churn, **not reduced correctness, reduced scope or five independent SQL patches without composition proof**.

**Preserve:** Candidate/Submission/Application ownership; durable Application and Interview-round identity; participant incarnations/history; report field patches and decision-source semantics; audited private documents; idempotency; resource serialization; scan/cleanup fencing; existing Candidate, Inbox, Interview and Report consumers; useful test fixtures and exact historical evidence. Preservation is conditional on repaired security and fresh acceptance, not grandfathering unsafe behavior.

**Fix:** F01 and F18 as an entry/session pair; F02 at the direct-table/grant/projection boundary; F04/F05/F06/F07 as interacting transaction-order, outcome, version and batch-rollback problems; F08 as explicit HR intent distinct from pure reads. Also complete locale/error safety, supported credential handling and truthful feature-completion reporting. Interface changes needed to repair confidentiality or atomicity are permitted; preserving architecture does not preserve unsafe signatures or grants.

**Add:** whole HR Submission editing and documents, Interview materials, Master Data and Users & Permissions management, actual PDF, real malware and email execution, cleanup discovery/launch, non-production configuration, connected acceptance, privacy/retention operations and production recovery proof. Existing UI may acquire feature-owned subcomponents where required to deliver those capabilities; there is no separate convention-unification or all-page extraction program.

**Intentionally retain awkwardness:** three adapter/result styles, large stateful workflow components, accumulated ordered repair migrations, explicit persisted-outcome callsite discipline and some manual evidence serialization. Fix dangerous error disclosure rather than tolerate it as debt. Old accepted migrations remain history, not a cleanup target.

**Known debt/cost:** contributors must learn multiple conventions; every later shared concern may need several careful edits; large state owners raise review cost; evidence can still require manual reconciliation. Knowledge transfer must explain those boundaries and their tests. This increases long-term maintenance burden and is charged in §§5–6. It is not assumed to be free because the code already exists.

**Verification:** all common security/concurrency/provider proof in §7, actual connected persona/dirty-state/mobile/locale paths, and capability-level composition acceptance. Existing green tests cannot close missing counterexamples. A coordinated inventory of outcome writers, parent/resource acquisition and exposed readers is essential repair analysis, not an optional broad redesign.

**Process:** retain independent high-risk review, targeted repair re-review, exact-SHA CI, append-only accepted checkpoints and slice composition. Correct false completeness, stale reporting and source-coverage blind spots using current authorities. Use already-authorized verification economy; resolve the canonical CI tension before changing skip policy. No new scheduler, evidence store or registry rewrite. A is not forced to repeat historical S06 inefficiencies that current rules already address.

**Best advantage [INFERENCE]:** shortest path without additional caller/state/provenance migration unrelated to a mandatory defect or capability. It can expose a real connected cohort early while preserving feature-by-feature acceptance.

## 3. Option B — Selective recovery/simplification

### Strongest credible definition

Pay the same mandatory recovery bill as A, and deliberately reduce demonstrated recurring delivery friction while touching affected areas. This is a real alternative, not A relabeled “balanced.” It changes reusable mechanics and ownership boundaries across several consumers, but not the domain architecture.

**Deliberate extra scope:** consolidate common verified-actor acquisition, safe error/result normalization and localized recovery conventions across the existing command families; extract feature-owned editing/document/overlay orchestration in touched Inbox/Interview/Report consumers; replace repeated same-fact evidence transcription with references/derived views in existing authorities. Extend future mandatory capabilities through those simpler seams. Domain-specific authorization, validation and conflict behavior remain explicit; no command bus, universal CRUD engine, new global state platform or generic workflow DSL.

**Best case [INFERENCE]:** whole HR editing/files, new document consumers and locale/error completion already touch substantial UI and adapter boundaries. One carefully bounded simplification could avoid editing the same tangled owner twice and reduce repeated security/error inconsistencies. More concise evidence and accurate derivation could shorten repeated review cycles and knowledge transfer. This is a credible compound advantage across the recovery, not merely cosmetic cleanliness.

**Precisely untouched:** entity keys and relationship ownership; Candidate snapshot/privacy-acknowledgement history; round numbering/current-versus-resource-blocking predicates; participant/report history; private object identity; outbox/job identities and lease protocols; correct RLS/RBAC and RPC business semantics; idempotency fingerprints/replay; resource locks; field-aware merge/decision timestamps; audit continuity; accepted migration and checkpoint history; framework/provider topology. The same identified SQL repairs apply as in A. Authorization checks are not deduplicated by deleting one layer. Untouched components are not migrated solely to reach a reuse target.

**Boundaries preventing stealth rewrite:** no shell/page replacement, wholesale actor-model change, new endpoint vocabulary, parallel legacy/new command stack or data conversion. Every chosen simplification must name a currently duplicated responsibility, fully migrate its affected callers and retire the obsolete local implementation in that bounded cutover. No permanent compatibility shims. If an extraction cannot preserve dirty bases, permission modes, focus, pending state and error contracts at lower total cost, exclude it rather than expand the program.

**Scheduling advantage is not assumed:** B can deliver the same first repaired cohort as A before nonessential extraction. It need not delay initial UAT for a generic refactor. However, to remain distinct, B commits to positive-evidence mechanical consolidation during product completion and to the extra behavior/review proof it creates. If all such work is deferred indefinitely, the executed recovery is A, not B.

**Process:** preserve every independent security/composition gate and exact-SHA binding. Compact same-fact evidence, make derived status fresh and remove redundant transitions only with provenance retained. Do not count mandatory truth corrections as exclusive B benefits: A and C owe them too. CI narrowing remains subject to the canonical-source reconciliation; B cannot remove a required DB gate by declaring it inefficient.

**Irreducible cost/risk:** extra caller migrations, state-boundary regressions, changed test seams, review of consolidated policy plumbing and evidence-derivation correctness. The small existing runner is not inherently expensive enough to justify replacing it. No measured net recovery-time saving from this extra scope is established by current evidence. Maintenance improvement is plausible, not a benchmark result.

## 4. Option C — Larger rebuild/rewrite

### C-app: strongest credible larger-rebuild candidate

Retain the **repaired database, Auth identities and private Storage**, but replace the substantial application layer with a coherent modular Next application: Candidate, Inbox, Interview and Report workflows; their draft/state ownership; Server Action/read/command adapters; actor/error/localization mechanics; auth/session integration; document/PDF consumers. New administration screens are still new work. Small independently useful primitives and design tokens may survive; old workflow orchestration is not hidden behind a compatibility wrapper. This is an application rebuild, not a full DB+application rewrite or a provider/framework migration.

**Best case [INFERENCE]:** if mandatory completion would otherwise repeatedly traverse nearly every inconsistent state owner and adapter, a coherent reconstruction may avoid “repair the convention, migrate the consumer, then rebuild that consumer again.” A single clear actor/result vocabulary and explicit workflow ownership could improve onboarding, full-journey tests and maintenance. Clean implementation is a benefit only if it reaches the same accepted behavior with lower total work.

**Retained, but repaired:** entity schema and IDs; RLS/RBAC and transactional RPCs that match requirements; idempotency, locks, report merge, history, notices, job and object state. F02/F04–F07 still require database repair and direct-role/race proof. New frontend projections cannot cure a raw-table leak. New state management cannot cure a SQL partial commit. Do not move multi-row transaction authority into sequences of application calls.

**Survival:** keep Auth UUID/business bindings, immutable Submission snapshots, participant incarnations, report versions, notice acknowledgements, document keys/bytes/hashes, audit/email history and pending job IDs/attempts/fences. Existing data is not converted simply because the UI changes. Reconcile objects and job state to metadata: retaining tables alone does not prove files or provider effects survived. New adapters must obey the retained identity/version/idempotency contracts.

**Cutover:** isolated branch and synthetic environment first. Replace old application entry paths in one controlled authority switch; no default dual-write or legacy runtime shim. Where active users/jobs exist, allow for a bounded maintenance window to drain requests, quiesce writes/claims, account for in-flight provider receipts, expire/fence obsolete leases and reject stale clients. Pending work resumes under one executor authority rather than being blindly re-enqueued. Historical audit remains immutable. No cutover duration is invented.

**Rollback:** a known-safe prior application compatible with repaired schema and new writes can be redeployed only if demonstrated. The vulnerable starting baseline is not a safe fallback. If no safe compatible artifact exists, maintenance plus forward repair is the honest fallback. Rollback does not unsend mail, reverse a private-file disclosure or recreate physically deleted bytes. Separate DB/object recovery remains necessary.

**Re-proof:** retain reusable SQL fixtures and canonical acceptance cases, but rebuild evidence for every new app→RPC mapping, user journey, dirty/conflict transition, auth lifecycle, private access, locale/mobile/accessibility behavior and provider integration. Historical UI success is not evidence for new components. Existing fixture/source-text tests may need replacement with actual behavior tests rather than cosmetic repinning.

### C-full: true DB+application rewrite variant

Rebuild schema, RLS and RPC implementations as well as the application. Preserve business meaning and preferably immutable public IDs, but transform/reconcile every relationship, version, historical record, acknowledgement, audit event, object reference and queued intent. Retaining IDs reduces mapping risk; it does not make structurally different data automatically compatible. Replacing the Supabase project additionally requires an authorized Auth/binding/session and object-transfer strategy; safe identity portability is not assumed.

Use a rehearsed single cutover with write/worker quiescence and verified referential/object/job reconciliation, not speculative dual-write infrastructure. Accepted migration history and original audit records remain archival evidence; do not erase them to manufacture a clean history. Additive compatibility may support a safe transition, but a truly incompatible schema needs a maintenance/cutover boundary and a proven reverse transformation or forward-only recovery contract. Once new-format writes occur, an old database snapshot is not lossless rollback.

C-full costs materially more than C-app: all security/concurrency semantics must be reimplemented, all data classes in §8 transformed or explicitly proved unchanged, and all direct-role/interleaving evidence recreated. Current evidence does not establish an incompatible domain model or irreconcilable migration chain that would buy enough benefit for this penalty. Therefore the main scorecard evaluates **C-app as the best credible C**, with C-full penalties made explicit rather than using the weakest rewrite as a strawman.

## 5. Comparative scorecard

All ratings are **[INFERENCE]**, conditional on equal mandatory scope and competent execution. Costs/risks use LOW / MEDIUM / HIGH / VERY HIGH. Time uses SHORTEST / SHORT / MEDIUM / LONG / LONGEST as **relative recovery paths, not calendar forecasts**. Coarse ties are intentional; no numeric sum or invented day/week estimate decides the result. Retention and reversibility rows explicitly use higher-is-better. Risks mean incremental transition/regression exposure after required repair, not current product safety.

| Criterion | A — minimal repair | B — selective recovery | C — C-app rebuild |
|---|---|---|---|
| 1. Time-to-DIAGNOSTIC-PREVIEW | SHORT | SHORT | SHORT; new shell alone proves little |
| 2. Time-to-FUNCTIONAL-UAT-PREVIEW | SHORTEST | SHORTEST if nonessential refactor stays off first cohort | LONG; new workflow must actually run |
| 3. Time-to-PHASE-1-COMPLETE | SHORTEST on present evidence | SHORT; added migrations of mechanics need payback | LONG; recreate existing plus missing journeys |
| 4. Time-to-PRODUCTION-READY | SHORT, conditional on common operations proof | SHORT; shared provider/recovery work can dominate | LONG; application cutover adds acceptance |
| 5. Implementation effort | HIGH; substantial missing capability remains | HIGH; same work plus bounded consolidation | VERY HIGH; same work plus app reconstruction |
| 6. Data migration risk | LOW with in-place identity retention; remote drift can raise it | LOW; no data-model change intended | LOW for retained records, MEDIUM transition interpretation; C-full VERY HIGH |
| 7. Security regression risk | HIGH around repaired exposure and new consumers | HIGH plus actor/error caller migration | HIGH across every new app boundary; C-full VERY HIGH |
| 8. Concurrency regression risk | HIGH; coordinated SQL and UI races | HIGH; same SQL plus state extraction | HIGH with retained repaired SQL and new clients; C-full VERY HIGH |
| 9. Product regression risk | MEDIUM; additions touch large existing state owners | HIGH during touched state extraction | VERY HIGH; all previous interaction semantics reopened |
| 10. External-provider integration burden | HIGH | HIGH | HIGH; reconstruction does not remove providers |
| 11. Verification/re-proof burden | HIGH; existing evidence cannot close omitted cases | HIGH; common proof plus changed seams | VERY HIGH across rebuilt application; still higher for C-full |
| 12. Operational deployment burden | HIGH; isolation, parity, restore, launch | HIGH; simpler wiring is not existing proof | HIGH plus application switch; C-full VERY HIGH |
| 13. Governance/review burden | MEDIUM under current valid economy; truth repair mandatory | MEDIUM; simplification costs first, possible later savings | HIGH; fresh implementation review and composition everywhere |
| 14. Long-term maintenance burden | HIGH; convention/state/evidence debt knowingly retained | MEDIUM if bounded consolidation succeeds | MEDIUM potential, not guaranteed by new code; knowledge transfer HIGH initially |
| 15. Rollback/reversibility, higher is better | HIGH at compatible app increments; never unsafe SQL rollback | HIGH with bounded complete caller cutovers | MEDIUM; safe old-app fallback conditional; C-full LOW |
| 16. Current valuable/verified behavior retained, higher is better | HIGH; unproved paths remain unproved | HIGH domain behavior; touched evidence recreated | MEDIUM overall: HIGH DB assets, LOW prior app evidence |
| 17. Existing behavior requiring rediscovery | MEDIUM; missing composition and subtle state still matter | MEDIUM; touched ownership contracts | HIGH for C-app, VERY HIGH for C-full |
| 18. Sensitivity to unknown cloud/provider state | HIGH for operations, MEDIUM for ranking | HIGH for operations, MEDIUM for ranking | HIGH; C-full VERY HIGH with unknown data/identity migration |

A and B are close. The ranking is not “LOW score wins”; common mandatory work dominates both. A currently avoids B's extra re-proof while using the same corrected contracts and existing review economy. B has a plausible maintenance advantage, but no observed benefit yet establishes that its additional changes shorten recovery through production. C-app retains enough database value to be credible, but cannot avoid the common repairs and adds substantial application rediscovery. C-full lengthens both the path and the uncertainty absent a newly demonstrated structural constraint.

## 6. Total recovery-cost analysis

### All options pay the same base bill

| Cost category | A | B | C-app / C-full |
|---|---|---|---|
| Domain identities and relational ownership | Preserve and verify legitimate existing behavior | Same; explicitly outside simplification | C-app retains; C-full transforms/recreates with reconciliation |
| Candidate/Submission/Application and round/history structure | Finish consumer composition, retain IDs | Same plus touched ownership extraction | Rebuild all consumers; C-full also reconstructs durable relationships |
| Contextual auth, RLS/RBAC, trusted RPCs | Repair unsafe exposure and enforce existing contract | Same plus safe common app mechanics migration | C-app same DB repair plus every new app boundary; C-full complete security rebuild |
| Locks, versions, idempotency, report merge | Coordinated repair/proof, not removal | Same plus changed client/state seam proof | C-app same plus new client behavior; C-full all algorithms reimplemented |
| Private Storage and scan/cleanup protocols | Retain identities/fences, add real execution | Same; simplify invocation only where demonstrated | C-app retains contracts; C-full additionally migrates objects/references/attempts |
| Existing Candidate/Inbox/Interview/Report UI | Preserve, fix and extend | Preserve behavior with bounded owner/mechanics migration | Substantially replace and rediscover every prior interaction |
| Exact-SHA tests/review/CI evidence | Reuse unchanged evidence only within valid scope; new gates remain | Same, plus provenance/derived-view migration review | Historical DB evidence useful; new application evidence recreated; C-full broadest invalidation |
| Interfaces and knowledge transfer | Explain existing conventions and amended contracts | Teach common conventions and fully migrate touched callers | Teach new app, reconstruct DTO/command mappings; C-full additionally new schema/operations |
| Rollback and operational proof | Compatible incremental releases plus forward repair | Same, with caller-cutover checkpoints | Controlled app switch; C-full data reverse/forward-recovery problem |

Historical expenditure is excluded. Valuable retained behavior saves future work only because it independently matches requirements and can be tested at the repaired boundary.

### Existing defects: reuse never means accepting them

| Finding | Required treatment in every option | Differential cost |
|---|---|---|
| F01 browser public-env initialization | Correct build-visible browser configuration and prove actual entry | A/B repair current seam; C writes/proves new seam, no free framework cure |
| F02 direct-table HR-note exposure | Close alternate readable shape, retain legitimate projections, verify direct roles | All retained-DB options repair grants/read contracts; C-full re-proves every new policy and projection |
| F04 composed lock ordering | Consistent parent/resource acquisition and post-lock revalidation across crossed commands | All need real opposing-command proof; app rebuild does not change SQL topology |
| F05 reactivation outcome | Same-transaction parent recalculation under compatible locking | Must be proved with F04, not added independently and assumed safe |
| F06 nullable expected versions | Null-safe validation at authoritative RPC boundary, preserving legitimate report disjoint merge | Every caller/direct caller rechecked; new TypeScript types do not repair SQL |
| F07 late-batch partial commit | All-or-nothing rows, outcomes, audit and cleanup effects on late failure | All must test successful prefix followed by stale/invalid target; idempotency alone is insufficient |
| F08 explicit HR open | Intentful authorized NEW→READ transition; passive/view-only reads remain pure | A/B connect current consumer; C recreates consumer and Candidate edit race proof |
| F18 session refresh | Real request/session refresh with verified identity, safe cookie/header behavior | A/B supply missing behavior; C reconstructs/proves it; filename rename alone earns no credit |

F03 scan execution and F09–F15 missing capability are charged below. F16 locale, F17 errors, F19 false feature closure, F20 operations evidence and F23 credential lifecycle remain mandatory where their boundary applies. F21/F22 simplification opportunities do not erase their distinct correctness/truth obligations.

### Missing product and external capability: no option gets a discount

| Capability | Common implementation/integration and acceptance cost | Option-specific consequence |
|---|---|---|
| Whole HR Submission editing | All permitted fields/children, immutable email boundary, versioned atomic Save and Candidate/HR interaction | A extends existing drawer; B extracts touched owner where justified; C rebuilds existing note/read/assignment behavior as well |
| HR documents | ADD/REPLACE/DELETE, last-CV rule, scan/retention/private access and file-only Save | Same private lifecycle obligation in all options |
| Interview documents | HR management plus contextual Interviewer consumption/revocation | Optional attachment instance is not optional capability |
| Master Data UI | Finite catalog lifecycle/history/selection and permission acceptance | Backend presence helps A/B/C-app; C-full reimplements it too |
| Users & Permissions UI | Root protection, delegated permission dependencies, inactivity/binding and denied calls | Generic privileged CRUD is not an acceptable shortcut |
| Generated PDF | Real authorized snapshot, actual downloadable bytes, VI fonts, ordering/blank/decision/privacy/audit | Same renderer/provider-budget proof; official pixel-template deferral does not defer PDF |
| VI/EN completion | Controls, errors, warnings, formatting and draft-preserving language changes | A repairs consumers; B consolidates touched messages; C translates/proves new and prior surfaces |
| Mobile/accessibility/product acceptance | Actual Candidate flow, keyboard/focus/errors, required viewports/personas and WCAG acceptance | New code or shared primitives do not certify these outcomes |
| Malware execution | Approved private engine, supported formats, trustworthy immutable-byte verdict, narrow worker identity, unavailable/infected/stale cases | All integrate existing external service if real and adequate; otherwise all must supply one; no fake CLEAN |
| Email sender/provider | Real authorized test delivery, receipt/history, bounded retries and accepted-send crash ambiguity | Auth SMTP is distinct from business outbox; both need actual proof |
| Cleanup discovery/scheduling | Invoke expiry discovery and bounded runner, private exact-object removal, fencing and backlog/error evidence | Scheduling claims alone misses discovery; all need real launch/identity |
| Environment/deployment configuration | Isolated targets, built public env, secret separation, redirects/providers, migration/grant/auth parity | Usable current config can reduce all options; absence of config file is not proof cloud absence |
| Recovery/backup proof | DB plus separate object restore, metadata reconciliation, RPO/RTO, compatible backout and operator rehearsal | All pay; C-full adds migration reconciliation and new-format write recovery |
| Privacy/retention/abuse/capacity | Notice publication/acknowledgement, authorized archive/export/purge, no automatic business purge, abuse/load/monitoring proof | No optional legal-admin platform or product Dashboard inferred; held abuse work is not authorized by this review |

### Interaction test: localized versus systemic failure

The evidence rejects two extremes: “independent tiny patches” and “the entire domain model is wrong.” The strongest supported diagnosis is **a compatible architecture with serious cross-command composition and acceptance failures**.

1. **Auth and confidentiality interact:** F01/F18 can prevent trustworthy sessions; fixing them exposes actual data paths, where F02 makes safe UI projections insufficient. Shared actor plumbing does not replace direct-role proof. A new login/page stack cannot bypass this sequence safely.
2. **Transaction repairs interact:** F05 adds parent outcome work; F04 determines how that parent is acquired relative to Submission/Interview/resource locks; F06 changes rejection conditions; F07 must roll back earlier mutations and all side effects. Each function passing alone is inadequate. A single crossed-invariant repair boundary is needed under all three options, with report-specific merge exceptions retained.
3. **Open/edit/documents interact:** F08 closes Candidate editing; new HR edits and file-only saves share versions, scan continuation and retention. A drawer redesign may improve ownership, but it does not remove the multi-actor transaction contract.
4. **Reports/privacy/lifecycle interact:** current-round/context changes, removed participants, dirty field bases and decision-source selection cross UI and SQL. Matrix C Z06 records unresolved source precedence and mixed-role proof. Resolve authority before “simplifying” to blanket stale rejection or merge-all.
5. **Providers/data/recovery interact:** email/scan/cleanup are external effects fenced by durable intent. Deploying or rolling back workers without respecting in-flight attempts can duplicate delivery or delete retained objects. A cleaner application still needs the same accounting.
6. **Acceptance failure is systemic at the process level:** backend-only closure and missing consumers show that task acceptance did not guarantee user value. Correct requirement-to-capability coverage and independent composition under every option. That does not prove schema or application topology must be discarded.

| Systemic-failure hypothesis | Present evidence and consequence |
|---|---|
| Incompatible ownership/domain decomposition | No established contradiction: frozen requirements independently need these aggregates, histories and actor contexts; keep testing composition rather than infer fit from names alone |
| Duplicated authoritative business truth | Persisted outcome callsite omission is real; one shared resolver exists. No demonstrated need for two competing outcome models; repair invocation/locking and prove all writers |
| Pervasive authorization bypass | F02 is serious alternate-path exposure and demands broader direct-role inventory. Source also shows auth-derived RPC/active checks and narrow worker roles. No established pervasive unrepairable bypass; absence is not certification |
| Unfixable transaction topology | Several composed order defects exist, but no evidence establishes that a consistent acquisition/revalidation design cannot fit existing intents. If bounded repair cannot close the full interleaving matrix, reopen this assumption |
| Impossible migration/history semantics | No current proof of irreconcilability; actual live state unknown. Existing repair migrations and immutable IDs favor in-place correction, not a guarantee remote parity exists |
| Framework/platform incompatibility | No demonstrated requirement impossible on current modular topology. F01 is a configuration-access defect; scanner runtime can be external without moving domain authority |
| Inability to release incrementally | Existing interfaces permit a plausible additive repair path; must prove compatibility. Unsafe old builds cannot be used as rollback merely because they run |

**Active challenge to Matrix C:** many KEEP rows could conceal a global graph of untestable repairs. That challenge is charged as HIGH composed verification, not dismissed by row count. Current evidence nevertheless identifies repairable seams, meaningful working structures and no demonstrated architecture-level impossibility. App reconstruction adds rather than removes the hardest SQL/provider proof. B's bounded mechanics changes can still win if those seams demonstrably dominate repeated delivery cost; current source shows duplication, not net payback.

## 7. Security/concurrency re-proof comparison

All options require fresh direct-boundary evidence for changed/shared invariants and exact release composition. Existing tests are inputs, not substitute proof. The matrix below is a charge ledger, not a detailed test implementation plan.

| Required invariant | A | B | C-app; additional C-full penalty |
|---|---|---|---|
| Direct-role authorization | Actual grants/table/RPC allow/deny including crafted calls | Same plus migrated actor/result callers | Same database proof plus every new transport; C-full complete privilege surface |
| RLS | Exposed relations, active/context and denied alternate reads | Same; no weakened policy for convenience | Same retained policies; C-full all new policies/functions |
| HR/Interviewer confidentiality | Raw table versus safe projection/private output after F02 | Same plus consolidated DTO/mechanics consumers | Every new DTO/export plus raw access; C-full all confidentiality boundaries |
| Root protections | Protected account, grant dependencies, delegated/non-root denials | Same after any actor plumbing change | New admin consumers; C-full protected identity/grants rebuilt |
| Candidate ownership | Verified binding, own historical/new/edit/private-object cases | Same; no shared actor cache leakage | New login/form/adapters; C-full identity/data mapping too |
| Resource conflict races | Candidate/Room/Interviewer competing operational intervals | Same, all touched scheduling callers | Same SQL plus new schedule clients; C-full serialization rebuilt |
| Lock ordering | Opposing parent/resource command pairs and revalidation | Same; refactor does not waive two-session proof | Same retained SQL; C-full new global acquisition graph |
| Round allocation | Concurrent create/copy, uniqueness, latest/HIRED gates | Same with touched consumers | New round/copy orchestration; C-full allocator/history model |
| Idempotency | Same-key replay, fingerprint mismatch, concurrent intent and provider ambiguity | Same through normalized wrappers | New key lifetime/caller behavior; C-full durable replay-state migration |
| Report owner precedence | Actor-pair/field conflict after canonical tension resolved | Same across extracted state/bases | Entire new editing model; C-full merge/provenance algorithm |
| Stale-write handling | Direct NULL/stale RPC and allowed disjoint report patch | Same plus moved client bases | All new callers; C-full version translation and semantics |
| Lifecycle reactivation | Eligibility/conflicts/history/outcome atomicity | Same after touched owner extraction | New UI commands plus retained repair; C-full entire lifecycle |
| Batch atomicity | Late failure rolls back rows/outcomes/audit/cleanup | Same across normalized responses | New bulk selection/result behavior; C-full transaction implementation |
| Scan fencing | Trusted worker only, immutable bytes, expired/cancelled/stale result | Same with runtime binding | Same plus new upload continuation; C-full attempt-state migration |
| Cleanup fencing | Exact retained-reference safety, lease/tombstone/stale completion/provider errors | Same with invocation simplification | Same plus cutover worker authority; C-full job/object provenance migration |

Security/concurrency cannot be priced only by the number of changed SQL lines. A pays HIGH coordinated proof; B adds re-proof of altered mechanical/state seams; C-app adds all application boundary evidence; C-full pays VERY HIGH reimplementation and migration proof across this whole ledger. Removing safeguards would be a different, incorrect product rather than a cheaper recovery.

## 8. Data migration/cutover comparison

**No empty-production assumption.** Obtain authorized read-only inventory before choosing any data-changing cutover. None is obtained or mutated here. A/B/C-app preserve records in place on the existing approved database project when compatible; this does not mean Preview may copy production PII. UAT uses synthetic records in a separate non-production target.

| Potential retained class | A / B | C-app | C-full |
|---|---|---|---|
| Candidates and Auth/business bindings | Preserve IDs/bindings; repair authorization without re-keying | Preserve, prove new session/provisioning callers | Explicit mapping or preserved IDs; authorized Auth/session continuity proof; no assumed password/token portability |
| Submissions | Keep immutable identity/email/profile snapshots | New UI interprets old snapshots without rewriting them | Transform/reconcile every snapshot and child relation |
| Applications | Keep durable identity/owner/current outcomes; repair recalculation | Retained keys and new caller interpretation | Preserve or map uniqueness/history/FKs and derived outcomes |
| Interview rounds | Keep numbering, lifecycle and schedule history | Rebuilt views/commands honor existing round identity | Reconstruct allocation/current/resource predicates without renumbering history silently |
| Participant history | Keep restore-versus-new incarnations and directory snapshots | New client must distinguish current/removed/historical | Map incarnations/order/archive links, not join history to mutable directory |
| Reports | Preserve content, versions, decision metadata and owner links | Recreate field-base handling against retained versions | Transform version/provenance/decision fields with actor-pair proof |
| Document objects | Keep private keys/bytes/hash/version references; no bulk move | No object migration required if same project; reconcile metadata/bytes/access | Authorized verified byte copy/reference mapping if changed; private ACL/hash/scan/history continuity |
| Privacy acknowledgements | Preserve immutable notice version and acknowledgement linkage | New forms retain historical legal evidence | Migrate immutable linkage with no silent re-acknowledgement or backdated consent |
| Email history and pending outbox | Keep IDs, attempts, recipient evidence and replay scope | Single executor resumes existing intent, no wholesale re-enqueue | Map history/pending intents and receipt ambiguity; no duplicate-send promise based solely on copying rows |
| Audit records | Preserve append-only event identity/provenance | Keep old events and attribute new app effects | Preserve original events and explicit migration lineage; never rewrite actors/history |
| Pending scan jobs | Preserve attempt/fence/object identity and continuation state | Quiesce/fence in-flight work at switch; resume or safely retry under same protocol | Migrate only with trustworthy byte identity/result provenance; unknown verdict never becomes CLEAN |
| Cleanup records | Preserve tombstone/lease/eligibility/reference state | Reconcile claims/completions and enable one worker authority | Transform queue/provenance/retention, reconcile already removed objects before retry |
| Active form sessions, staged uploads and idempotency receipts | Preserve where protocol-compatible; explicit expiry/retry where not | Account for old client drafts/tokens; prevent obsolete clients writing after switch | Reconcile or explicitly retire with safe user recovery; no silent loss of committed submission or duplicate intent |

| Transition question | A | B | C-app | C-full |
|---|---|---|---|---|
| Business-data migration required? | Not by strategy; bounded corrective changes only if evidence requires | No; domain data untouched | No if retained project/contracts compatible | Yes: transformation or exhaustive unchanged-data proof across new model |
| Compatibility adapters required? | No standing adapter; complete changed callers | No permanent shim; migrate bounded callers completely | No old-app wrapper; new app speaks retained contracts | Avoid default adapters; any necessary bridge needs explicit cost/authority, not presumed free |
| Dual-read/write required? | No | No | No; single authoritative app/worker switch | Not default; complexity and divergent-write risk strongly penalize this variant |
| Cutover downtime required? | Not inherently; scoped write pause may be needed for specific safe migration | Same; caller changes can be compatible | Plan for bounded quiescence if users/jobs active; zero downtime not promised | Likely maintenance boundary; depends on measured volume and proven migration design |
| Rollback still possible? | Compatible safe app release; SQL safety repair retained | Same after complete caller migration | Only safe compatible old app with new writes; otherwise maintenance/forward repair | Only with tested reverse transform/reconciliation; snapshot restore alone loses later writes |

Unknown volume and in-flight work raise C-full uncertainty most. Even confirmed zero business records would remove only data-copy cost, not authorization/concurrency/UX/provider re-proof. Unknown data is not a reason to provision a replacement project or reset the current one.

## 9. Functional UAT Preview comparison

### Same credible acceptance cohort for all options

A trustworthy first cohort is a **synthetic, connected recruitment case**, not a complete Phase-1 declaration: Candidate real test OTP/session refresh → acknowledged Submission with privately uploaded CV and actual trustworthy CLEAN scan → HR authorized explicit open ending Candidate NEW editing → assignment/scheduled interview → assigned Interviewer own report and authorized shared HTML Preview. Observe real test notification receipt when that case promises email; verify an unassigned/removed identity cannot read confidential notes/files. Include a competing session for the crossed lifecycle/version/batch risks rather than infer safety from one happy-path user.

All use isolated non-production Supabase, authorized Vercel Preview or equivalent non-production target, verified project/environment/redirect/secret mapping and no real recruitment PII. Test recipient allowlists and synthetic files do not permit mocked delivery/verdict claims. Root/limited-HR test identities must have real trusted bindings and grants, not a privileged fixture bypass. Scan-pending/infected/unavailable and stale/forbidden outcomes must stay truthful. Independent review and applicable exact-SHA/connected smoke evidence attach to the actual deployed build.

This cohort intentionally does not claim Master Data/User-management UI, whole HR editing, Interview materials, generated PDF or full language/mobile/accessibility completion. Those are visibly incomplete and remain mandatory before PHASE-1 PRODUCT COMPLETENESS. A narrower Candidate-only flow could be useful functional testing, but does not satisfy this comparison's multi-persona cohort. Unsupported actions cannot be advertised as working. Cleanup discovery/execution must be exercised for unattended-lifecycle acceptance; any earlier bounded cohort explicitly limits duration, monitors synthetic leftovers and does not claim unattended readiness.

| Option | Smallest route to that same first functional cohort | What cannot be counted as success |
|---|---|---|
| A | Repair shared auth/session, direct-role privacy and crossed SQL invariants; connect existing HR-open consumer; bind real test scan/mail to existing protocols; deploy existing connected UI against verified isolated schema/config | Static login rendering, enqueue-only mail, fake CLEAN, source tests or backend task closure |
| B | Same initial path; only already-justified touched error/actor or document ownership consolidation may accompany it. Other simplification waits behind this cohort rather than becoming an entry ticket | Claiming unmeasured refactor savings or skipping required CI to make time-to-preview appear shorter |
| C-app | Repair the same DB/privacy/concurrency and integrate the same providers, then implement that cohort through the new Candidate/Inbox/Interview/Report application and new session/adapters | Showing the repaired old app while calling it rewrite UAT, or a new shell that forwards all old orchestration |

C-full additionally requires a safe representative migrated synthetic/history dataset and direct-role/transaction proof against its new schema before the same cohort counts. Every option's PHASE-1 and PRODUCTION bars remain unchanged. Provider isolation/configuration may dominate the elapsed path for all three; no approach is credited for making that work disappear.

## 10. Cloud/provider uncertainty sensitivity

No scenario below asserts current cloud facts. These are decision sensitivities, not authorization to inspect secrets, resume projects or mutate services.

| Scenario | Consequence for A | Consequence for B | Consequence for C | Could ranking change? |
|---|---|---|---|---|
| Scenario 1 — No useful external email/scanner/cleanup runtime exists | Build/integrate all missing bounded execution and proof | Same; invocation conventions may be shared where useful | Same in addition to app reconstruction; C-full also queue migration | Normally no. Shared provider cost dominates but does not favor rewrite; integration difficulty alone is not app failure |
| Scenario 2 — Some runtime exists but undocumented/unintegrated | Inventory identity, provider semantics, leases, formats, privacy and receipt/failure evidence; integrate if compatible | Same, possibly stronger return from consolidating inconsistent invocation | Can reuse compatible runtime too; new app still needs its contracts | A/B gap could change if integration repeatedly crosses divergent adapters; C only improves if actual interface incompatibility makes its replacement cheaper after re-proof. External existence alone does not |
| Scenario 3 — Remote Supabase schema/config differs materially from baseline | Stop promotion; reconcile catalog/migrations/grants/auth triggers/data before choosing repair | Same; app simplification cannot reconcile unknown data | C-app inherits mismatch; C-full adds migration rather than automatic escape | Yes, the most consequential structural uncertainty. Repairable drift favors in-place recovery; irreconcilable ownership/security/history could reopen C-full, subject to §15 proof. Never normalize unknown live schema by reset |
| Scenario 4 — Vercel project/environment is already partly usable | Reuse verified isolated mapping/build configuration; still fix F01/source and refresh | Same; no duplicate environment platform needed | Reuse suitable target for new app, still prove new artifact/session semantics | Usually reduces all options' setup cost, not a reversal. If a demonstrated runtime constraint prevents current app behavior and cannot be isolated, revisit architecture evidence |

Remote parity and provider inventory are the largest uncertainty in absolute recovery cost. A-versus-B economics also depend on observed repeated repair/review work, which historical anecdotes and file size do not quantify. Confirmed usable external services can turn ADD implementation into integration/proof, but never into acceptance without evidence. Production data/history and pending-provider effects could sharply increase rewrite risk.

## 11. Failure modes and mitigations

Exactly five principal failure modes per option; each mitigation is an acceptance/control principle, not a Phase-E task assignment.

| Failure mode | Mitigation |
|---|---|
| A1 — Local fixes leave cross-command cycles or partial side effects | Treat F04–F07/outcome writers as one crossed-invariant boundary; direct-role and deterministic opposing-transaction/late-failure proof |
| A2 — Confidentiality repair hides UI data but leaves alternate read or breaks valid consumers | Inventory exposed tables/RPCs/projections and prove both allowed and denied personas, including mixed-role and historical contexts |
| A3 — Extending large UI state owners loses drafts, file atomicity or explicit-open semantics | Actual connected dirty-refresh/locale/focus/Candidate-vs-HR scenarios; bounded feature-owned extraction only when required for correctness |
| A4 — Contract presence and green mocks conceal provider/session failures | Real test auth, scan, receipt and cleanup discovery→delete→fenced completion; visible failure/backlog evidence and exact deployed build |
| A5 — Retained debt/process friction again hides unfinished product | Source-to-capability composition acceptance, accurate derived status and independent review; reopen B if repeated mechanics-related effort demonstrably dominates |
| B1 — Selective cleanup expands into a stealth rewrite before usable UAT | Fix finite ownership boundaries; keep initial cohort independent of optional refactor; stop unproved scope expansion |
| B2 — Shared actor/result abstraction erases domain-specific authorization or errors | Preserve user context, permission modes, trusted RPCs and explicit domain validation; direct-call/consumer regression evidence |
| B3 — State extraction silently resets conflict bases, history or focus | Preserve independently dirty fields/pending guards and actual overlay/refresh behavior; no generic global store without evidence |
| B4 — Evidence/CI simplification weakens provenance or violates canonical DB gate | Retain exact reviewed/CI/checkpoint identities and independent composition; resolve source tension before skipping required checks |
| B5 — Refactor investment does not amortize while providers stall | Charge actual caller/proof costs, integrate real providers early, and stop optional consolidation when it does not reduce observed remaining recovery work |
| C1 — New app inherits SQL privacy/concurrency defects under a cleaner UI | Repair retained DB and run full §7 proof; C-full recreates all boundaries rather than assuming fresh design safe |
| C2 — Rewrite rediscovery loses historical, owner-precedence, draft or mobile semantics | Canonical behavior ledger and real multi-persona/concurrent journey acceptance; reuse valid fixtures without counting them as new runtime proof |
| C3 — Prolonged half-rewrite duplicates authority or never reaches cutover | One bounded application replacement boundary, isolated branch, no dual writes or permanent legacy wrappers, complete cohort acceptance before switch |
| C4 — Cutover loses objects/jobs or duplicates irreversible provider effects | Reconcile data/objects/attempts/receipts, quiesce and fence executor authority, preserve audit and prove restore separately |
| C5 — Attractive new demo omits administration/providers/recovery and lacks safe rollback | Same full capability ledger as A/B; actual provider effects and compatible safe fallback or explicit maintenance/forward repair before operational use |

## 12. Reversibility comparison

| Property | A | B | C-app / C-full |
|---|---|---|---|
| Isolated branch development | Yes; bounded changes against synthetic environment | Yes; complete bounded caller/state cutovers | Yes; new app in isolated environment; separate branch is not production acceptance |
| Incremental rollback | Strong for compatible app additions; never revert safety repairs into exposure | Strong if each mechanical migration is behavior-compatible and complete | Coarser application switch; C-full weakest after transformed writes |
| Old application fallback | Only a tested safe build compatible with repaired schema and new data | Same; no assumed legacy shim | C-app conditional; starting vulnerable app not acceptable. C-full needs reverse mapping or cannot fall back |
| Schema compatibility | Retain interfaces unless safety requires narrow change; additive-first release | Same; no domain/schema simplification program | C-app retains repaired contracts; C-full must explicitly manage or surrender compatibility |
| Feature-by-feature acceptance | Strong; complete real journeys within existing app | Strong if cleanup does not become broad prerequisite | New app features can be tested independently, but total replacement cutover still needs cross-feature composition |
| External-effect reversibility | Mail/access/deletion not undone by code rollback | Same | Same plus switch/replay risk; database restoration cannot unsend messages |

No option may cross an irreversible data migration boundary merely to start clean. A/B preserve the most freedom to change the later strategy after obtaining runtime evidence. C-app is more reversible than C-full because it retains data authority, but operational fallback is still a proved property, not a benefit automatically granted by Git history.

## 13. Recommended option

RECOMMENDED_OPTION: A

**Select the strongest minimal-repair strategy, ranked A first, B second, C-app third.** Confidence is MEDIUM overall and narrower between A/B than between A/C. This is a decision under incomplete live evidence, not a claim the current product is safe.

### Why A wins on total cost, not sunk cost

The mandatory work is substantial but mostly shared: composed SQL/security repair, missing end-user capabilities, real providers and operational proof. The retained domain/transaction/storage boundaries independently match frozen product requirements. Existing actor/error conventions are inconsistent but small and explicit; rebuilding them does not fix direct-table exposure, SQL NULL semantics, batch rollback, scanner absence or unimplemented administration. Existing report refresh code contains required behavior that any extraction or rebuild must preserve.

A permits **coordinated** repairs and necessary feature-owned changes, not whack-a-mole patches. It also owes completeness truth and independent composition review, so B cannot win merely by claiming those essential controls exclusively. Current governance already contains targeted re-review/verification economy; historical S06 repetition is not an unavoidable future cost of A. Canonical CI ambiguity prevents assuming additional skip savings today.

A knowingly carries higher maintenance and knowledge-transfer cost. That cost is real, but the evidence does not establish enough repeated future mechanics work to outweigh B's immediate caller/state/provenance migration and re-proof through Phase-1 recovery. Keeping optional simplification off the critical path preserves the ability to measure this tradeoff against functioning journeys. The decision is **not** “fewest changed files”: necessary safety repairs can cross many files/functions, and missing screens can be large. It is “do not pay to replace a behavioral seam unless the replacement reduces the total remaining recovery bill.”

### Why second-best B loses narrowly

B offers the best plausible longer-term maintenance improvement and could tie first-cohort time. Its strongest case is avoiding repeated changes while adding HR/document/localization features. But source duplication and large components show an opportunity, not demonstrated net savings. The mandatory error/privacy/feature-truth fixes are common costs; there is no evidence that migrating all affected adapter/state conventions is needed to obtain the same safe behavior. Evidence-serialization simplification also has provenance/re-proof cost, and CI savings remain constrained by canonical authority.

This is not a ban on local clarity during repair. A small extraction needed to safely implement a requested feature belongs to A. A planned cross-consumer convention and evidence-mechanics consolidation program is B. If repeated mechanics-caused regressions, re-review churn or mandatory near-total state-owner changes become observable, **switching to B could be justified without changing the global rewrite conclusion**.

### Why third-best C loses

C-app's coherent reconstruction is credible, but it inherits the same repaired database and providers while discarding existing consumer behavior and evidence. It must rediscover dirty-state, history, permission-limited personas, current-round and document semantics before reaching the same UAT cohort. No current proof shows those application layers are cheaper to rebuild than to complete. C-full adds identity/data/object/job migration and complete security/concurrency reconstruction without an established incompatible domain model, unrepairable topology or platform impossibility.

Retained code is not sacred. The ranking must change if comparative accepted-outcome evidence contradicts these assumptions; it must not change solely because one option is aesthetically cleaner or has more new code.

## 14. Full-rewrite decision

FULL_REWRITE_JUSTIFIED: NO

A full DB+application rewrite is not justified by the current evidence. Nor is the strongest substantial application-only rebuild currently the shortest safe recovery path. The two statements are distinct: C-app could become the recommended large rebuild without proving the database should be replaced. “NO” does not mean preserve every file, every RPC body, unsafe grants, missing runtime, stale status or duplicated incidental test. It requires material security/concurrency repair and mandatory capability completion.

The decisive penalty is future work, not past effort: rebuilding the same authorization, resource, history, merge, idempotency and private-document guarantees; retaining or migrating actual data; re-proving every changed boundary; integrating the same providers; and demonstrating a safe cutover/fallback. Defect count and clean-file count are not proxies for that bill.

## 15. Evidence that would flip the rewrite decision

**What evidence would have to change for the global rewrite answer to flip?** A substantiated structural problem plus a validated lower-total-cost alternative, including migration and proof, must replace the current compatible-but-incomplete diagnosis. The following are concrete reopening triggers, not authorization to run experiments or mutate systems now.

| Evidence category | Evidence strong enough to reopen the conclusion | What would NOT suffice |
|---|---|---|
| Systemic DB/RLS unsafety | Effective-catalog/direct-role review finds authorization ownership fundamentally incompatible across aggregates, and bounded repair cannot establish required allow/deny guarantees without replacing essentially the whole policy/data authority; an alternative passes the same persona/projection suite | F02 alone, many policy files, or a safer-looking DTO |
| Transaction topology | Deterministic cross-command tests and complete writer/lock inventory show required operations cannot meet atomicity/conflict semantics in the retained ownership model at acceptable constraints, while a redesigned model does with migration/recovery proved | A few source lock inversions, missing recalculation, or declaring all locks expensive |
| Domain incompatibility | Canonical requirements conclusively require incompatible identity/history/ownership semantics that cannot be added compatibly; explicit conversion preserves old snapshots, legal evidence and current references | Preference for generic recruitment entities or dropping participant/report history |
| Migration-history irreconcilability | Authorized catalog/data inventory and rehearsals show no safe bounded forward-repair path from actual retained schema/data, but a fully reconciled new model has demonstrably safer cutover and recovery | Remote drift that can be repaired, many historical migrations, or assuming an empty database |
| Measured platform/performance impossibility | Representative load/provider/privacy tests show the current topology cannot meet required behavior and the limitation cannot be isolated to a worker/query/runtime seam; an alternative meets the same targets including operational recovery | File size, framework fashion, lack of benchmarks, or a scanner requiring an external process |
| Lower verified rewrite cost | Comparable representative high-risk journeys implemented/proved under repair versus replacement show less total implementation, rediscovery, review, CI, data/job reconciliation and rollback work for replacement, with a credible extrapolation across remaining scope | New code compiling, a polished demo, optimistic estimates excluding providers or a percentage-reuse claim |
| Unusable application plus unreliable evidence | Actual required extensions repeatedly force near-total existing application replacement and accepted behavior cannot be preserved more cheaply; new app meets the same complete persona/concurrency/UX matrix | Missing connected tests alone: both strategies still need to create them; this may favor C-app without justifying DB rewrite |
| External constraints invalidate topology | Verified security/residency/provider/hosting requirements prohibit the retained authority/data arrangement, and a replacement satisfies them with authorized identity/object migration and operational proof | Undocumented provider state or partially configured Vercel environment |

No single application-layer trigger automatically flips the full DB+app conclusion. To justify full rewrite, retaining and repairing the database must also lose the total-cost/safety comparison. Confirmed empty data reduces migration exposure but does not remove re-proof. Evidence that simply favors bounded mechanics consolidation changes A to B, not the global verdict. Conversely, demonstrated pervasive unsafe assumptions cannot be dismissed by pointing to Matrix C's many KEEP rows.

## 16. High-level recovery shape for Phase E

This is only the shape for a separately authorized Phase E; no detailed slices, task IDs, prompts, implementers or registry changes are created.

1. **Establish trustworthy boundaries:** verify target inventory without assuming current cloud facts; repair auth/session and direct-role confidentiality, and prove the composed transaction/version/outcome/batch invariants.
2. **Obtain real isolated functional UAT:** bind actual test auth/scan/mail and connected existing workflows on authorized non-production infrastructure; disclose the cohort's incomplete product scope and unattended-runtime limits.
3. **Complete mandatory Phase-1 value:** administration, whole HR editing/documents, Interview materials, generated PDF, VI/EN, mobile/accessibility and truthful capability composition; operational scan/mail/cleanup must be real, not merely queued contracts.
4. **Prove real-data operations before production:** deployed schema/grant/auth parity, private access, backups plus object restore, compatible rollback/forward repair, capacity/abuse/monitoring, privacy/retention procedures and operator rehearsal under explicit release authorization.
5. **Reassess optional simplification using delivery evidence:** retain current architecture unless observed total-cost evidence favors a bounded B change or the explicit rewrite threshold. Never defer safety/completeness truth as optional cleanup.

The canonical CI requirement must be reconciled through its controlled authority path, not silently overruled by any of these steps. Frozen A/B/C remain immutable. Phase E has not begun. Artifact validation and GitHub byte verification establish only completion of this strategic review, not runtime readiness.

PHASE_D_RECOVERY_OPTIONS_FROZEN: YES
