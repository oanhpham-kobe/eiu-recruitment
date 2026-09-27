# EIU Recruitment — Greenfield Phase-1 Architecture

## 1. Context, source inventory, and isolation disclosure

This is Phase A only of the Owner-authorized strategic review for `oanhpham-kobe/eiu-recruitment`. Controlling instruction: `project_control/research/ASTRA_MEDIUM_MASTER_HANDOFF_2026-09-27.md`, A1–A4, lines 68–152; isolation contingency, lines 49–64. This artifact proposes the simplest correct product on Vercel + Supabase. It makes no finding about the existing implementation, its quality, or any preservation/replacement strategy. It is not an implementation authorization, exact schema, RPC specification, ADR, or new canonical product source.

### Provenance and limits

- Before the correct worktree was supplied during planning, a listing of `D:/orca/recruitment` exposed directory/file names. A `git show` targeting only the handoff on a named branch failed. No implementation contents or commit history were read.
- Planning inspected the handoff, product-package listings, document 14, document 02, and headings/snippets of documents 03–07. This execution read the handoff first, checked the exact target artifact for freeze/provenance (path did not exist), and read the permitted product material below.
- Automatically injected repository instructions contain technical/governance information. Product documents mix behavior with physical field names, command names, RLS requirements, workflow prescriptions, source-gate assertions, and occasional implementation-path references. The headings search itself exposed technical freeze/gate metadata. Acceptance document 13 also exposed source-validation and implementation-governance assertions alongside behavior. These are context contamination, not evidence of implemented functionality.
- No runtime source, migrations, workflows, task/slice/autonomy registries, implementation evidence, source diffs/history, cloud state, other research files, or technical source registries were inspected. Linked technical documents were not followed. No delegation, external architecture examples, cloud operation, dependency install, or product tests occurred.
- Strict context isolation cannot be guaranteed. This review therefore ends after freezing Phase A. Phase B requires a separate Owner continuation invocation. The later technical baseline was not inspected.

### Citation convention and read inventory

References such as `[P03:50–61]` mean the exact repository path below and inclusive line range. These aliases apply throughout this artifact, including tables. Only the listed read portions support claims. Source headings that were merely discovered do not establish their bodies.

| Alias | Repository path | Read scope |
|---|---|---|
| P02 | `recruitment_webapp/review_pack/02_ROLES_PERMISSIONS_AND_NAVIGATION.md` | Full body, 1–158 |
| P03 | `recruitment_webapp/review_pack/03_CANDIDATE_FORM_AND_PORTAL.md` | Full body, 1–225 |
| P04 | `recruitment_webapp/review_pack/04_HR_APPLICATION_INBOX.md` | Full body, 1–164 |
| P05 | `recruitment_webapp/review_pack/05_HR_INTERVIEW_PAGE.md` | Full body, 1–275 |
| P06 | `recruitment_webapp/review_pack/06_INTERVIEW_REPORT_HR_AND_INTERVIEWER.md` | Full body, 1–216 |
| P07 | `recruitment_webapp/review_pack/07_STATUS_AND_BUSINESS_RULES.md` | Full body, 1–137 |
| P09 | `recruitment_webapp/review_pack/09_MASTER_DATA_CATALOG.md` | Headings; 3–71 and displayed closing reason rule at 74 |
| P10 | `recruitment_webapp/review_pack/10_UI_UX_SPEC.md` | Headings; 5–231 |
| P11 | `recruitment_webapp/review_pack/11_EMAIL_DOCUMENTS_AND_ACTIVITY_LOG.md` | Headings; 1–157 |
| P13 | `recruitment_webapp/review_pack/13_ACCEPTANCE_CRITERIA_AND_TEST_CASES.md` | Headings; 5–367, including mixed technical acceptance |
| P14 | `recruitment_webapp/review_pack/14_SCOPE_AND_OPEN_ITEMS.md` | Planning exposure; execution headings and 3–7, 12–21, 35–36; no linked gates |
| P38 | `recruitment_webapp/review_pack/38_NON_FUNCTIONAL_REQUIREMENTS.md` | Headings; 5–56 |
| P42 | `recruitment_webapp/review_pack/42_PRIVACY_RETENTION_COMPLIANCE.md` | Headings; 3–29 |
| D-R | `recruitment_webapp/design_system/RESPONSIVE.md` | Headings; 6–82 |
| D-T | `recruitment_webapp/design_system/TABLE_LAYOUT.md` | Headings; 3–162 |
| D-K | `recruitment_webapp/design_system/TOKENS.md` | Headings; 3–114 |

Labels: **Required** = cited product behavior or safety constraint; **Proposal** = this review's greenfield design; **Open** = unresolved wording or unavailable product input. Technical prescriptions encountered in product sources are disclosed rather than presented as independent discoveries. No platform quotas, installed versions, or existing configuration are assumed verified.

## 2. Canonical Phase-1 interpretation and requirement ledger

**Minimum scope is a complete recruitment operations loop:** Candidate verification and private application submission; HR receipt/correction/assignment; multiple interview rounds and conflict-safe scheduling; qualitative participant reporting and current-round Preview/PDF; permission, master-data, communication, privacy, and operational support. A backend-only capability or a button that never performs its external action is not this product.

| ID | Required behavior | Authority | Consequence for proposed design |
|---|---|---|---|
| R01 | One protected Root; active EIU HR with granular permissions; new HR defaults to full non-security HR set. Root still obeys business locks. | P02:3–73; P13:113–125 | Separate authentication, authorization and business validation; no Root bypass. |
| R02 | Candidate Email OTP; internal Google Workspace OAuth, active allowlisted exact EIU domain; first identity binding is atomic. | P03:5–12; P13:15,169,191,209,341 | Managed Auth, server-side eligibility and identity reconciliation. |
| R03 | Candidate owns a new snapshot per submit; one scrolling form, not wizard; read-only verified email. General identity/contact fields required; Education 0–20 rows with optional fields. | P03:3–39,87–103; P13:309–321 | Separate Candidate identity from Submission snapshots and repeatable Education. |
| R04 | Candidate sees only Mới/Đang xử lý/Hoàn thành; edits whole form only while active and NEW, version-current; HR-only fields survive untouched. | P03:63–85,105–170; P13:13 | Ownership-filtered projection and restricted patch input, not whole-object replacement. |
| R05 | Short-lived form session; refresh-safe session-only draft; staged file/text Save is atomic, Cancel applies neither; session expiry is authoritative. | P03:189–206; P13:182–187,285–287 | Temporary upload/session lifecycle separate from retained Submission. |
| R06 | Server-current published notice pinned to NEW/EDIT; new acknowledgement unchecked; recheck effective current notice on Save, preserve draft on change; immutable versions. | P03:56–62,218–221; P42:17–23; P13:359 | Transactional acknowledgement plus current-pointer check; no second accuracy attestation. |
| R07 | PDF/Word/PPT/PNG/JPEG; ≤5 current files/parent, ≤5 MB/file; current CV required for Submission; private, validated, CLEAN before exposure/finalization; replace retains versions. | P03:41–54,144–149; P11:62–98,138–150; P13:149,203–204,366 | Quarantine, scanning, immutable object versions; multiple same-type logical files allowed. |
| R08 | Inbox groups by Candidate; latest snapshot drives parent summary; exact historical child opens; server search/pagination; no PII in URL/history/telemetry. | P04:16–46,158–164 | Candidate-page pagination, stable ID tie-break, exact child navigation. |
| R09 | Passive detail read never marks READ. Explicit full-HR open changes NEW→READ; view-only HR open is pure read. Manual NEW/READ only without active Application. | P04:63–81; P07:23–34; P13:268–270,288–291,365 | Read and explicit-open intent distinct; Candidate Save races with HR open. |
| R10 | HR whole-drawer edit, HR-only notes/experience/activities/other, authorized identity-field correction except email; unsaved warning; bulk Active/Inactive/Mark New/Read only in Inbox. | P04:83–150; P03:63–85; P13:357 | HR edit projection distinct from Candidate projection; latest-only manual status nuance remains Open in §11. |
| R11 | Application uses selected Submission, immutable durable assignment identity Unit/optional Team/Position; exact duplicate confirm reuses/reactivates same identity; eligible HR owner. | P05:15–23,65–101; P13:31–43,212,243,258–259 | Unique identity across inactive history; atomic assignment and default Round 1. |
| R12 | Multiple rounds; new topic blank, status defaults; latest inactive or latest active HIRED blocks next round; only latest existing round delete/inactivate; no historical renumber. | P05:93–121; P07:70–79; P13:361 | Allocate rounds under Application serialization. |
| R13 | Schedule statuses manual with no forced sequence; Save/email do not change them. CONFIRMED locks ordinary edits; controlled reschedule resets AWAITING. | P05:49–63; P07:51–58; P13:360 | Separate explicit rescheduling intent; legacy wording conflict recorded in §11. |
| R14 | Candidate, Room and every current Interviewer overlap BLOCK; half-open intervals allow adjacency. All operational rounds count, not just Current Round; inactive/cancelled/no-interval do not. | P05:178–191,255–275; P07:133–137 | Resource-level serialization and transaction-time recheck on every activation path. |
| R15 | Ordered active participants, name/email/title snapshot; remove revokes access, warns with report; re-add restore old or create new. User lifecycle must not strand future active participation/ownership. | P05:143–161; P13:232–233,258–259,273,298–301 | Participant history is not a mutable directory join; lifecycle guards and reassignment. |
| R16 | Copy is draft-only until Save; target existing Application, blank topic; fill structurally empty default Round 1 with no copy provenance, else next legal round; conflict validation. | P05:163–176,263–268; P13:305–306,346 | Atomic copy/save, provenance retained as business usage; no hidden Application creation. |
| R17 | HR reports one row/Application using highest access-active round. Manual eight report statuses; outcome derives only from Current Round, then Submission derives across active Applications. | P06:3–53; P07:23–49 | One shared outcome calculation in outcome-changing transactions. |
| R18 | Five optional qualitative fields and three optional decision fields, no scoring/rating. HIRED/REJECTED allowed with blank decision. Latest eligible decision timestamp + UUID tie-break chooses whole block; evaluation-only edits do not change it; clear-all falls back. | P06:129–192; P13:93–105 | Versioned report content, separate decision-change metadata; no invented completion gate. |
| R19 | Interviewer reads participating visible access-active historical rounds but writes own Current Round only, non-final. Hidden/removed/inactive revokes contextual access. HR fields/source metadata never exposed. | P02:75–102; P06:92–128,186–192 | Read versus write policy differs; role-safe Preview/PDF projection. |
| R20 | HR report edits require permission. Field-aware merge preserves disjoint changes; same-field HR conflict rejects; eligible Interviewer-versus-HR owner wins, not whole-row overwrite; same-account stale tabs reject. | P02:141–149; P06:151–159,194–201; P13:363 | Field provenance/version evidence required, not generic last-write-wins; wording tension in §11. |
| R21 | Current Preview/PDF follows participant order, snapshots, blank fields, single current decision source; no cross-round merge or invented official elements; official pixel template deferred. | P06:160–207; P10:200–207; P14:19 | Real export capability retained; official-form use pending clarification. |
| R22 | Manual Candidate/participant email preview/send; notification for every Candidate create/edit atomically enqueued for exact Submission; delivery outside transaction, at-least-once, bounded retry, no attachments. | P11:3–31,52–60,138–154; P38:34–36 | Durable outbox plus recoverable sender; enqueue success is not delivery success. |
| R23 | Email history permission AND parent access; classified deletion TEST only in TEST or WRONG with reason; immutable audit survives deletion. Sensitive actions/files/PDF audited, no tokens or signed URLs logged. | P11:33–50,100–135,156–157 | Operational history separate from append-only security events. |
| R24 | Required masters include organization hierarchy, positions/groups, rooms, formats, qualifications, sources/types/reasons and directory. Inactive retained references remain valid; structural change creates replacement master. | P09:3–71 | Explicit small catalogs, active new selections, historical snapshots; no universal metadata platform. |
| R25 | No automatic business-data purge. Export, controlled archive/explicit purge, correction, capacity alerts required; retained production Submissions not normal hard-delete targets. | P42:3–29; P13:129–135,302; P38:38–43 | Authorized maintenance capability, not general HR delete button; no timed retention engine. |
| R26 | VI/EN throughout, VI default; ≥16px primary text, accessible semantic tables, fixed column alignment, keyboard controls, responsive Candidate portal, desktop-first internal. | P10:5–146,220–231; D-R:18–82; D-T:3–114; D-K:29–61,113–114 | Shared UI primitives with separate mobile presentation, same mutation semantics. |
| R27 | List p95 ≤1.5s at 10k Submissions/30k Interviews; mutations ≤2s excluding providers/transfers; shell p75 ≤2.5s; 50 internal/200 Candidate concurrency baseline. | P38:5–23 | Paginated indexed queries; bounded provider-independent requests; no speculative scale tiers. |
| R28 | 99.5% availability target; DB RPO ≤24h/RTO ≤8h; separate object backup, restore rehearsal; ≥30-day operational logs; WCAG 2.2 AA; malware/cleanup backlog alerting. | P38:28–54 | Restore and failure-path evidence before real data, not only happy-path tests. |
| R29 | Future product modules hidden, not empty menu placeholders. | P02:120–139; P14:35–36 | No Dashboard, demand, Candidate Database, KPI/analytics, offer/onboarding automation in launch scope. |
| R30 | Candidate NEW→Mới, READ/PROCESSED→Đang xử lý, DONE/CLOSED→Hoàn thành. Interviewer sees FOLLOW_UP/ON_HOLD/HIRED as Report Submitted, REJECTED as Rejected; other report labels map directly. | P03:151–170; P06:55–66 | Persona-specific status projection, not disclosure of internal hiring state. |
| R31 | Report Delete/Inactive targets a concrete participant report, never aggregate drawer; historical report state and current state remain distinct. Optional cancellation/rejection reasons clear when leaving their applicable status; demo-topic metadata is advisory. | P06:78,209–216; P13:263; P09:71,74 | Explicit entity-targeted actions; no invented required conclusion/topic/reason. |
| R32 | Business timezone Asia/Ho_Chi_Minh; date-only fields do not shift timezones. Search debounce 300ms, broad name minimum two characters, exact/prefix email/phone allowed; page sizes 25/50/100, stable groups. | P04:39–46,158–164; P38:5–11,25–26,55–56 | Consistent formatting and bounded server queries across pages. |

### A3 numbered coverage table

| A3 | Question | Answer location |
|---|---|---|
| 1 | Minimum user-facing scope | §2 opening and R01–R29; §10 |
| 2 | Personas and end-to-end abilities | §3 |
| 3 | Simplest module decomposition | §4 |
| 4 | Minimum conceptual data/ownership | §5.1 |
| 5 | Transactional invariants | §5.3 |
| 6 | Authorization/privacy guarantees | §5.2 |
| 7 | Required concurrency | §5.3–5.4 |
| 8 | Application versus PostgreSQL/Supabase | §6.1 |
| 9 | Synchronous versus asynchronous | §6.2 |
| 10 | Mandatory external runtimes/providers | §6.3 |
| 11 | Legitimate deferrals | §10; §6.3 |
| 12 | Simplest safe deployment topology | §7 |
| 13 | Minimum test pyramid | §8.1–8.2 |
| 14 | Reliable, low-ceremony delivery process | §8.3 |
| 15 | Explicitly not building | §10; §12 |
| 16 | Ordered vertical slices | §9 |

## 3. End-to-end user journeys

### Candidate

1. On phone or desktop, choose language, request Email OTP, verify, and enter only if Candidate active. Resolve one Candidate identity even on safe recreated-Auth recovery; do not create a second person just because Auth ID changed. Inactive accounts cannot enter protected portal; internal records survive. [R02, R04; P13:169,209]
2. First visit opens the single-page New Submission form. Later visits offer New and My Submissions. Read-only verified email, required personal fields, optional Education, required CV, other allowed documents, and privacy notice appear in one scroll. New acknowledgement starts unchecked. [R03–R07]
3. Upload enters private quarantine, then validation/scan. Progress and failed/rejected/expired states must be visible. An unavailable scanner never produces a fake CLEAN result; preserve the valid draft and allow retry/replacement. Submit cannot finish without a clean current CV. Starting a form does not create an empty business Submission. [R05–R07]
4. Submit atomically saves snapshot, children, acknowledgement, clean document references and exact-Submission notification intent. Show the created record, not a promise that email was delivered. Refresh/retry must not create another logical Submission. A deliberately new submission uses a new operation identity. [R03, R06, R22; P13:139–143]
5. My Submissions shows only own records and three statuses. Edit NEW with one whole-form Save/Cancel. Refresh can recover the same session draft; Cancel/logout/expiry/success clears it. If HR has opened the record, a stale edit, expired upload, or changed notice blocks commit without partial text/file changes. A changed notice explicitly asks for renewed acknowledgement while preserving draft. [R04–R06, R09]
6. For a processed record, contact HR. HR correction does not change login email; identity recovery is a separate privileged operation. Recovery preserves historical email snapshots and revokes obsolete sessions. Older snapshot edits cannot replace the newest Candidate summary. [P03:130–142,206,222; P13:357–359]

### HR, including permission-limited HR

1. Active allowlisted EIU Google login opens only permitted pages/actions. Full new HR gets the defined non-security set; role name alone is insufficient. View-only HR can open NEW without taking Candidate edit rights away. Authorized explicit open marks READ; background read/prefetch never does. [R01–R02, R09]
2. Search grouped Inbox without leaking search terms into URL/telemetry. Expand one Candidate, open exact Submission, inspect clean private documents, edit permitted fields and HR-only material, Save or Cancel with dirty-close warning. Stale edits require reload rather than lost updates. Bulk actions validate the whole supported set, not browser loops that leave partial results. [R08–R10; P13:271,336–339]
3. Link the exact Submission to a Unit/Team/Position and eligible owner. Duplicate confirmation updates/reactivates the same Application. New assignment atomically creates available Round 1 with scheduling report status. Different assignment does not rewrite history. [R11–R12]
4. Schedule one session, choose active participants in order and required room/link according to format. Save blocks all three resource overlaps, including another round or another Submission of the same Candidate. Status is manual. Ordinary CONFIRMED edit is locked; explicit reschedule is separately confirmed and revalidates conflicts. Copy is only a draft until validated Save. [R13–R16]
5. Preview and send Candidate/participant messages without attachments. Show queued, sent and failed honestly; sending never changes schedule status. View/delete history only with both permission and parent context and valid cleanup reason/classification. [R22–R23]
6. Review Current Round reports, set status without forcing sequence or filled conclusions, manage visibility, edit others only if allowed, preview/download current PDF. Note-only edits cannot change status. A stale Current Round selection must not update the newly current round. [R17–R21; P06:215–216; P13:250,339]
7. Create subsequent rounds until the latest active result is HIRED; handle latest inactive round explicitly. Remove/re-add participants through warned historical actions. Inactivate used records, retain discoverable history, reactivate only after owner/participant/resource validation. Candidate reactivation recalculates all its Submissions and sets no-active-Application records READ, not silently editable NEW. [R12–R17; P03:208–215]

### Interviewer

1. Active EIU login reveals only current-participant, visible, access-active sessions. A new round does not remove authorized read access to an earlier participated round, but grants no access to the new round. Hidden, removed, inactive parent/session or inactive account denies future access. [R19]
2. Read interview logistics and clean session documents, open own report on Current Round, write optional qualitative/decision content without scores. Save disjoint changes safely; eligible conflict against an intervening HR edit gives owner precedence, while own stale tab cannot overwrite newer work. Final target status blocks edit; HR must reopen it. [R18–R20]
3. Shared Preview/PDF contains ordered current participant evaluations and one whole decision block; no HR note/owner/final-source metadata. Historical read remains scoped to the participated round and does not unlock report write. Document/PDF requests reauthorize, and failures do not expose cached private output. [R19–R23]

### Root Admin

1. Bootstrap exactly one Root, authenticate as an eligible internal user, maintain directory, assign/revoke HR permissions with prerequisite validation, and inspect effective permissions. Non-root directory managers cannot inspect another user's granular grants or promote themselves. [R01; P02:60–73]
2. Maintain masters without changing the structural meaning of referenced values. Reassign active Application ownership/current future participation before deactivating affected internal users. Root cannot ordinary deactivate/delete/demote itself or bypass schedule/conflict locks. [R15, R24; P13:113,258–259,273]
3. Perform privileged bound-identity recovery through explicit verified operations, not directory text edit; normal internal-user hard delete is absent. Candidate email recovery is Root or explicitly delegated HR, excluded from default HR. [P02:49–67; P13:242,358]
4. Oversee capacity warnings, authorized export/archive/explicit purge, notice publication and operational failures. Published notice text never silently mutates. These are controlled maintenance capabilities, not a new general administration workflow engine. Legal notice/retention input and recovery authorization remain launch prerequisites. [R25, R28; P42:22–29]

## 4. Proposed simple architecture and module boundaries

**Proposal: one modular web application on Vercel, one Supabase project per environment, private object storage, and bounded background handlers.** Product complexity lives in a small number of explicit transactions, not in independently deployed business services. R27's baseline does not justify distributed domain services, a search cluster, or an event-stream platform.

| Module | Owns | Boundary and rationale |
|---|---|---|
| Identity and access | Auth integration, Candidate/internal eligibility, Root/HR permissions, lifecycle and recovery | One policy vocabulary across actions and read projections; R01–R02/R19 require context, not only roles. |
| Submissions | Candidate portal, form sessions, snapshots, Education, HR enrichment, Inbox | One Submission aggregate coordinates text/files/privacy/notification commit; R03–R10. |
| Recruitment operations | Assignment, rounds, schedules, participants, copy, current-round/outcome resolution | Keep scheduling and its lifecycle together to prevent divergent conflict rules; R11–R17. |
| Interview reports | Individual reports, HR status/note/visibility, shared Preview/PDF | Reuses Recruitment's current-round resolver, never a second outcome model; R17–R21. |
| Directory and catalogs | Organization, positions, formats, rooms, qualifications, types/reasons, directory UI | Explicit catalogs with common UI elements, not arbitrary schema-driven business editing; R24. |
| Delivery and document services | Private object authorization, quarantine/scanning, version publication, email outbox/history, cleanup | Infrastructure helpers called by owning domain transactions; they cannot invent business permissions; R07/R22–R23. |
| Audit and maintenance | Append-only events, notice publication, retention operations, capacity/backup visibility | Small secured operational functions, not a business Dashboard or second control plane; R23/R25/R28. |

Proposal UI: shared shell, form controls, drawers, confirmations, grouped tables and status controls, with page-specific columns and behavior. Use VI/EN messages and role-shaped server responses. Candidate mobile is a presentation of the same workflows, not a second backend. Adopt cited design tokens and semantic-table requirements; do not develop a generic design-system product. [R26]

Proposal reads: authorized paginated projections directly from PostgreSQL/Supabase through the application boundary; fetch child history on expansion where useful. Do not load the entire database into browser state. Prefer computing latest/current summaries in queries initially, with indexes and deterministic ordering; introduce persisted caches only if measured R27 targets require them. This is conceptual design, not a claim that any existing cache can be removed.

## 5. Conceptual data ownership, privacy, authorization, transactions and concurrency

### 5.1 Minimum conceptual model

| Concept | Ownership and relationships |
|---|---|
| Auth identity; Candidate; internal user; permission grant | Authentication credential binding is distinct from business person. Root is a protected singleton designation. Verified email is an identity/matching attribute, not a mutable profile key or conceptual primary key. |
| Submission and children | Candidate owns many immutable-identity submission snapshots; permitted content remains editable by lifecycle. Education and HR-only child content belong to exact Submission, with separate write boundaries. |
| Form session, staged change, upload reservation | Candidate-owned temporary intent, expiry and terminal lifecycle; new form exists before Submission. A staged replacement targets one logical document/current version. |
| Notice version and acknowledgement | Published notice immutable; acknowledgement belongs to Submission+version, reused for same version. Current/effective pointer is separate from content. |
| Logical document and immutable version | Belongs to Submission or exact Interview session, never both ambiguously; one current version per logical file, private object references and validation/scan evidence. |
| Application | Belongs to exact Submission and durable assignment; Candidate derives through Submission. Eligible HR owner belongs here, not separately in each report. |
| Interview round | Belongs to Application; owns logistics, schedule status, report status, visibility, topic and session documents. Current Round is a selector, not a second stored report aggregate. |
| Participant and individual report | Ordered participant snapshot belongs to round; report belongs to a specific participant incarnation. Restore retains identity/history; create-new archives old participation/report. |
| Catalog references | Organization hierarchy, position/group, room, format, qualification, source, document type and optional reasons retain historical meaning. |
| Outbox intent, operational Email History, audit | Exact business parent and recipient purpose; delivery state separate from retained append-only audit. Retry/cleanup state is operational, not the source of recruitment truth. |

This model is grounded in R01–R25. It intentionally omits table DDL, exact RPC signatures, transport objects and a generic polymorphic entity store.

### 5.2 Authorization and privacy

Required: active authenticated identity plus permission/context/ownership on every action and private read, including documents, email history, Preview/PDF and history. Recheck at mutation time; hiding navigation is not authorization. Database RLS and explicit grants protect exposed tables/views/storage paths; privileged server use must still authorize the actual actor. Never ship admin credentials to browser. [P02:151–158; P13:119–125]

Proposal: actor-scoped query projections omit HR-only fields before serialization, not after rendering. Candidate inputs have a strict allowed-field set. Interviewer reads omit HR owner, HR notes and final-source metadata. Sensitive output is private/non-shared-cacheable. Prefer authenticated download mediation for tight revocation; if short-lived object URLs are used, issuance is authorized and already-issued URL lifetime is an explicit residual risk, not a claim of instantaneous revocation. No public permanent URLs, token-bearing telemetry or PII search URLs. [R04/R08/R19/R23; P11:71–79,135]

Required identity recovery is a security operation distinct from editing a Submission snapshot. Proposal: fail closed when identity evidence conflicts, invalidate obsolete sessions, audit without full PII dumps. Historical submission email is retained even when verified login email legitimately changes; the older blanket equality wording requires clarification (§11), not rewriting history. [P13:27,357–358]

### 5.3 Atomic invariants and serialization

| Boundary | Required invariant | Proposal mechanism and cost |
|---|---|---|
| Auth binding and Root lifecycle | One business identity per valid binding; exactly one protected Root after bootstrap | Database uniqueness plus locked trusted lifecycle operation; modest identity-specific code, no generic identity bus. |
| Candidate Submit/Edit | Active+ownership+NEW+version/session validity; current notice acknowledged; effective CV/count limits; all text/file references/audit/notification intent commit together | Lock/recheck aggregate, stage external bytes first, atomic metadata publication; no external transfer inside transaction. |
| Document finalization | Valid nonexpired reservation, immutable scanned bytes, current-target still matches, one reservation not reused, no partial replacement | Bind scan result to immutable object/version; aggregate version check for file-only HR changes too. Failed/expired jobs remain inaccessible and cleanable. |
| Assignment/rounds | Durable identity, hierarchy/owner eligibility, default round and next-round gates; allocate max existing round + 1 without renumbering history; an unused hard-deleted latest number may be reused [P05:107–121] | Unique constraints plus Application serialization; include copied-round provenance and all side effects. |
| Scheduling/activation | No concurrent Candidate/Room/Interviewer overlap and all selected current participants eligible | Stable resource lock order plus transaction conflict recheck; lock Interview before participant snapshot. Per-resource coordination is necessary; one global scheduler lock is not. |
| Outcomes/lifecycle | Current-round-only outcome and consistent parent Submission state; no manual derived status | Serialize affected parent Submission and re-resolve Current Round; one shared calculation, no asynchronous eventual status repair. |
| Batch operations | Supported bulk lifecycle/status changes all succeed or none; stale/invalid/conflicting item aborts batch | One bounded server batch with deterministic lock order; never client loops. Recheck newly overlapping selected rows against each other. |
| Participants and directory | Remove immediately revokes context; restore/create-new history correct; no ineligible active owner or future operational participant stranded | Atomic lifecycle/reassignment checks and report/participant history changes. |
| Report content | Disjoint fields preserved; authorized owner conflict precedence; own stale tab rejected; decision timestamp only on actual decision change | Locked versioned report patch with trusted field-change provenance/base verification; no stale whole-row replace or arbitrary client claim of provenance. |
| Notices/audit/deletion | Effective notice continuity; immutable published text/audit; delete only eligible unused records and preserve cleanup intent | Locked publication switch, restricted audit writes, durable cleanup capture before eligible hard delete. Retention purge is separately authorized. |

Evidence: P03:199–225; P05:103–121,178–191,263–275; P06:151–159,194–216; P07:23–49,98–105,125–137; P13:137–143,182–215,232–278,285–306,322–339,346,358–366. These are required guarantees; locking layout is a proposal, not inspected implementation.

### 5.4 Distinct predicates and failure semantics

- **Access-active:** both Application and Interview active. Candidate inactivity denies Candidate portal; it does not erase internal history or itself substitute for Application/Interview lifecycle. [P04:73–81; P05:271–275]
- **Current Round:** highest round number among access-active rounds, for report/outcome/current PDF only. Older operational rounds still reserve resources. [P07:43–49,70–79,133–137]
- **Resource-blocking:** access-active, non-CANCELLED, real interval; all current participants count. Half-open intervals allow end=start. For Application reactivation, revalidate non-elapsed children that become blocking; elapsed historical overlap alone does not block. [P05:263–275]
- **Read versus write:** a historical participating Interviewer may read but not edit. Stale report status cannot silently apply to a different Current Round. [P06:101–128; P13:250]
- **Idempotency:** scope retry identity to actor/action/intent; replay returns the same committed result, while a conflicting reused key must not mean a fresh mutation. Required duplicate-prone operations include Submission, assignment, round, email enqueue and document finalization; persisted PDF job only if such a job is chosen. No promise of exactly-once provider delivery. [P13:139–151]
- Proposal: keep synchronous conflicts stable and actionable, with no partial commit; preserve unsaved input where safe, show reload/reconfirm/reassign instructions, and audit permitted override cases. Error codes are not generic internal stack traces. [P13:143; P03:58; P05:187]

## 6. Application versus PostgreSQL/Supabase, sync/async, external runtimes

### 6.1 Responsibility split

**Proposal — application:** session verification and safe actor context; input parsing/validation feedback; locale/form/drawer/table presentation; role-shaped reads; email preview/template rendering; safe PDF rendering; provider adapters; retry UI; protected job entrypoints and redacted operational logs. Share ordinary validation vocabulary, but do not rely on client validation for safety.

**Required database/Supabase boundary:** durable ownership and uniqueness, authorization/RLS/grants, atomic aggregate changes, current-round/outcome rules, versions/field conflict decisions, ordered participants, resource concurrency, idempotent intents, audit and durable work state. Supabase Auth manages credential proof; business eligibility is not inferred from a successful login. Private Storage holds immutable object bytes; database metadata controls lifecycle. [R01–R25]

Proposal: implement a small explicit transactional operation per business intent, using PostgreSQL where multiple records must commit together. Do not spread one command across independent HTTP writes. Do not build a generic command framework merely because multiple operations exist. Exact physical schema/functions remain later implementation work.

### 6.2 Synchronous versus asynchronous

| Synchronous before user success | Asynchronous after durable intent |
|---|---|
| Authorization, validation, session/current-notice/version checks | External email delivery and bounded retries |
| Text/metadata changes, schedule conflicts, derived statuses | Malware scan processing; user sees pending until trustworthy result |
| Atomic notification enqueue and audit intent | Abandoned/expired temporary object cleanup and retried deletion |
| Upload reservation/staging and safe finalization checks | Capacity/backlog alerts and scheduled backup/export operations |
| Read authorization and consistent Preview/PDF data snapshot | Large authorized export/archive if it exceeds request budget |

Proposal: small current-round PDFs initially generated on demand from one authorized consistent snapshot, within a measured request budget; no durable PDF queue unless measured need. A generated artifact must not include inaccessible HR fields. If persisted, it stays private, version-bound and reauthorized. Upload scanning is asynchronous, but finalization's CLEAN decision is synchronous and mandatory. A scheduled cleanup delay never extends session/reservation validity. [R05–R07/R21–R28]

### 6.3 Capability-by-capability launch decision

| Capability | Required user capability and minimum safe launch behavior | External runtime/provider decision | Legitimately deferred |
|---|---|---|---|
| Email | OTP reaches Candidate; manual preview/send works; create/edit HR notifications queued atomically; show failed delivery, retry transient failures bounded to 24h/equivalent; leased claims and stale-send recovery, best-effort dedup; no attachments. [P11:3–31,52–60,138–157; P38:34–36] | A real delivery provider is mandatory, including production Auth mail delivery. Proposal: one provider for both where supported; durable database outbox and bounded sender on existing hosting. Dedicated always-on mail service is not inherently required. Verify provider/scheduler capabilities before launch. | Attachment sending, campaign builder, marketing automation, guaranteed exactly-once delivery. Live mail cannot be deferred for real launch. |
| Upload safety/scanning | Required CV and permitted Office/image/PDF uploads remain private; validated content and reliable CLEAN result before finalization/download; pending/failure/rejected states visible; never fail open. [P13:149,182–187; P11:150] | Trustworthy scanning computation is mandatory. Proposal: managed malware service with contracted private handling, or an isolated scanner runtime if the approved service cannot meet privacy/format requirements. Vercel+Supabase alone is not assumed to provide the engine. Exact vendor/placement unresolved. | Office preview conversion may be omitted in favor of safe download. Cannot defer malware scanning while admitting the approved external Office types; narrowing the whitelist needs Owner source change. |
| PDF | Authorized actual downloadable current-round report plus shared preview, correct ordering/snapshots/blank fields/whole decision block, no HR leakage. [P06:160–207] | No separate provider inherently required. Proposal: bounded server-side PDF library/rendering in existing app runtime with embedded VI-capable font; measure output/runtime. Add external rendering only with evidence. Do not label HTML-only preview as PDF delivery. | Official EIU pixel-template fidelity is deferred, not report/PDF functionality. Operational official-form approval conflict remains §11; no invented administrative text. |
| Cleanup | Expired/cancelled/abandoned temporary uploads reclaimed with observable backlog; durable cleanup capture before eligible delete; stale jobs recoverable; no automatic retained-data purge. [P11:140,148; P13:215,334–335; P38:54; P42:3–15] | A dependable recurring trigger and executor are mandatory for unattended cleanup. Proposal: one existing-platform scheduler plus bounded DB-backed handlers; exact placement selected after quota/runtime verification. No separate queue broker/daemon by default. | Business-record TTL purge and generic workflow engine. Temp cleanup automation is not deferrable by calling it a retention feature. |

Google Workspace identity provision is also a launch dependency for internal login [P13:15]. Monitoring, private-object backup/export and a restore destination are required operational capabilities [P38:28–40]; they may use managed/native facilities rather than extra application services. No new runtime is justified merely by a preference for containers.

## 7. Simplest safe Vercel + Supabase deployment shape

**Proposal:** one Vercel application containing the UI/server boundary and bounded job handlers, backed by one Supabase project's Auth, PostgreSQL and private Storage per environment. External integrations are Google Workspace, production email and approved malware scanning. Use one recurring scheduler for durable outbox/cleanup processing unless verified platform constraints require separate triggers. Stateless request handlers never own the sole copy of pending work.

1. Local development and an isolated non-production Supabase-backed Vercel Preview use synthetic data/test recipients. Production has separate project, storage, credentials, callback allowlists and delivery configuration; preview cannot access production private records. Environment isolation is a proposal to satisfy R23/R28, not an observation of existing cloud state.
2. Application server verifies actor and calls actor-authorized transactional operations. RLS/grants remain effective even if browser/API routes are called directly. Worker privileges are server-only and narrow; human request paths cannot inherit unrestricted worker authority. [R01/R19/R23]
3. Database, storage, app and scanner placement must be chosen with actual latency, privacy, format limits, memory/runtime and transfer costs verified later. No claim that a particular Vercel/Supabase tier meets them has been made. Prefer one region pair near users, not multi-region writes. [R27/R28]
4. Proposal: private personalized responses and generated artifacts are not shared cached; rate limits protect OTP/forms; HTTPS, CSP without unsafe-inline on Candidate routes, and safe headers apply. No service secret, OTP, token or signed URL enters client bundles or logs. [P03:196–198; P38:45–46; P11:135]
5. Launch evidence must cover real OTP, Google login, provider send, scan, clean/private download, cleanup retry and database+object restoration. Queue counts/age, delivery failures, scan failures, cleanup backlog, quota and redacted request correlation are sufficient initial operational visibility; no product analytics Dashboard is implied. [R22/R23/R28]
6. Proposal deployment process: reviewed reproducible app build and reviewed migration per release; apply in non-production first, exercise role/race tests and journeys, then explicitly authorized production promotion. A schema change must be compatible with the app rollout or use a short controlled maintenance window. Backout means known compatible app plus tested data recovery, not assuming destructive migrations can be reversed. No deployment is performed by this review.

## 8. Minimum verification strategy

### 8.1 Test pyramid: few layers, risk-directed depth

**Proposal, not executed tests:**

- Small unit tests for pure outcome/status mapping, half-open interval edges, report decision-source selection and field merge conflict classification. Avoid mirroring framework wiring or snapshotting source text.
- Most safety proof at real PostgreSQL/Auth/Storage integration boundaries: role matrix, direct unauthorized calls, parent/context access, immutable history, unique identity, version checks, idempotency, staged upload commit/cancel, notice rollover and all-or-nothing batches. Use two genuine concurrent transactions for resource/round/outcome/report races, not sequential mocks.
- Small browser suite for complete Candidate→HR→Interviewer→HR result flow, Root/limited-HR authorization, inactive/revoked sessions, failure/retry and private document/PDF access. Verify actual generated PDF data and downloaded artifact, actual synthetic email receipt and real scanner acceptance/rejection before production, not mocked provider echoes.
- UX/UAT on VI and EN, keyboard-only and assistive-technology use, zoom/contrast, mobile Candidate at 360/390/430 and tablet 768/1024 plus desktop reference and constrained-height overlays. Preserve drafts across language changes; verify table alignment, status dropdown focus return, dirty-close and no hidden duplicate navigation. [R26; D-R:74–82]
- Baseline load and recovery exercises at R27/R28 targets. Measure pagination groups and stable order, not just endpoint latency. Restore both records and private objects, then prove authorized retrieval.

### 8.2 Mandatory adversarial scenarios

1. Candidate A cannot read/edit Candidate B or supply HR fields; removed/hidden/inactive Interviewer loses future file/PDF/history access; HR without corresponding view permission cannot infer records through email history.
2. Passive prefetch versus explicit open; limited-HR open leaves NEW. Candidate upload begins NEW, HR opens READ, Save fails with no partial document/text commit.
3. Notice switches mid-form; Save returns changed-notice error, preserves draft/session, and succeeds only after new acknowledgement. Missing/future current notice fails closed.
4. Sixth file, oversized/spoofed file, scan failure, expired reservation, replacing changed/deleted target, deleting only CV, cancelled form and duplicate finalization. Verify quarantine bytes cannot mutate after scan and before publication.
5. Concurrent conflicting schedules for Candidate across separate Submissions, Room and Interviewer; adjacency succeeds. Add-participant versus reschedule; cancellation reversal/reactivation/copy/bulk use identical invariants. Past-only Application reactivation allowed; future conflict aborts all.
6. Concurrent next-round allocation, latest inactive/HIRED gates, copy provenance and empty default round, inactivation of latest round and current-outcome fallback; no historical renumber.
7. Concurrent outcomes across two Applications preserve Submission derivation; NEW without Application remains NEW under generic recalculation, while Candidate reactivation forces READ. Latest-only manual status issue tested after §11 resolution.
8. Disjoint HR/Interviewer edits preserve both; eligible same-field owner wins only over HR; HR stale and same-user stale conflicts reject; malicious base values cannot manufacture authorization. Evaluation-only change leaves decision source unchanged; cleared decisions fallback; blank decision permits final status.
9. Email provider accepts then sender crashes: no duplicate logical intent; possible physical duplicate documented/audited. Permanent failure visible, lease recovery works, no attachments. Notification delivery throttling does not undo valid Candidate Save.
10. Duplicate assignment uses same active/inactive identity; revoked/ineligible owner/participant lifecycle blocked until reassigned. Root cannot disappear; non-root cannot self-promote/rebind others or inspect others' effective permissions.
11. Email History cleanup enforces TEST/WRONG rules and preserves audit. Temp-object cleanup capture failure aborts eligible hard delete; retries do not purge retained production data.
12. PDF current-round data/order/privacy and historical participant access; no scoring, cross-round merge, or leaking HR-only source metadata.

These scenarios derive from ledger sources, especially P13:162–366. They describe future acceptance, not a passing test result for this review.

### 8.3 Delivery process optimized for reliability rather than ceremony

**Proposal:** maintain one prioritized list of complete user journeys with acceptance IDs, one owner per change, and short reviewable vertical slices. For each slice: cite product rule → implement UI/transaction/integration together → run focused tests and real smoke → independent risk-focused review → repair → CI on the exact candidate release → demonstrate user outcome. Keep one evidence record per accepted slice/release, referencing checks rather than copying their output into multiple registries.

Review authorization, concurrency, retention and external side effects independently; ordinary label/layout changes need proportionate review, not every database gate. Use path-aware CI but rerun cross-cutting role/race suites when shared policy/transaction code changes. Require Owner decision only for actual product contradictions, scope changes or external authorization boundaries. Do not open implementation tasks or modify durable registries from this artifact.

“Accepted” means the stated journey works, including real external effects where promised. A delivered schema/function or mocked green test is a dependency milestone, not user-facing completion. Proposed process changes here are greenfield recommendations, not permission to bypass this repository's current lifecycle.

## 9. Ordered end-to-end implementation slices

These are proposed future slices, not dispatched tasks. Each includes UI, authorization, persistence, error handling and its evidence; none calls a backend-only scaffold a usable product. Dependencies are ordered to expose a real preview early without admitting real PII prematurely.

| Order | Observable user value | Scope/dependencies | Minimum acceptance |
|---|---|---|---|
| 1 | Candidate sends a real synthetic application and HR receives/opens it in isolated Preview | Bootstrap protected Root and eligible HR; actual OTP/Google auth; minimal necessary masters/notice; mobile single-page form; private scanned CV, Submit and notification, own list and basic exact-Submission Inbox | Real test-provider receipt and scanned download; Candidate ownership; view-only versus full-HR open; idempotent Submit; no production data. This is the first working loop, not just login. |
| 2 | Candidate revises safely; HR corrects/processes grouped historical submissions | Complete form edit/draft/privacy rollover/staged replace/Cancel; latest summaries, search/filters/pagination; HR enrichment/correction; supported bulk Candidate/manual status lifecycle | Race with explicit HR open, stale/file-only save, privacy switch, inactive/reactivation mapping, no HR-field overwrite/PII URL. Resolve latest-only manual status wording first. |
| 3 | HR creates real assignments and conflict-safe interview appointments | Exact selector/hierarchy/owner; default and subsequent rounds, participant order, schedule statuses and explicit reschedule | Duplicate identity reuse, same Candidate across Submissions overlaps, Room/Interviewer races, blank next topic, inactive/HIRED gate; ordinary confirmed edit blocked. |
| 4 | HR coordinates meetings and participants receive actionable information | Manual preview/send/history; session documents; copy, remove/restore/new participant, inactive/reactivate and permitted bulk schedule/lifecycle | Actual send with status unchanged; private document access revoked; copy draft has no effects; atomic batch conflicts and non-elapsed reactivation. |
| 5 | Interviewers submit qualitative reports and HR closes the hiring result | Own current report, historical read; HR status/note/visibility/edit; outcome propagation; shared Preview and downloadable PDF | Field-aware concurrency, decision-source fallback, blank-final allowed, no scoring/HR leakage, current-only PDF and real file download; resolve stale wording and official-form operational question. |
| 6 | Root and authorized HR operate the complete directory/catalog and security lifecycle | Complete masters, limited permission combinations, directory/owner/participant lifecycle, identity recovery; dependencies are existing real records from slices 1–5 | Root protection, prerequisite grants, history-preserving masters, bound identity recovery and obsolete-session denial, no non-root permission-list disclosure. Basic security was required in slice 1, not postponed here. |
| 7 | EIU can launch and recover safely with real data | Authorized retention export/archive/purge capability, notice maintenance, capacity/queue alerts, bounded retries/cleanup, backup/restore, performance, VI/EN/accessibility/mobile UAT and approved legal/mail content | Measured R27 targets and R28 recovery; test all persona journeys and external failure paths; explicit production approval. Earlier slices already include scan/cleanup/email safety; this slice verifies operational completeness, not first introduction of safeguards. |

A slice cannot defer one of its required safety properties to a later slice. Real-data launch waits for the whole Phase-1 requirement set and resolved launch inputs. Official pixel-template work remains separately deferred as in §10, subject to §11's operational-use question.

## 10. Deferred scope

**Canonically future-hidden:** Dashboard, recruitment demand, Candidate Database, KPI & Reports/advanced analytics, offer/approval/onboarding automation. Render no empty menu items. Operational capacity alerts required by retention are not permission to add those product modules. [P14:35–36; P38:42–43]

**Explicitly deferred:** pixel-perfect official EIU PDF template until supplied; internal detailed mobile/tablet design follows desktop work, whereas Candidate mobile cannot be deferred. No current cross-round merged PDF; no Phase-1 email attachments. [P14:7,19; P10:200–231; P06:203–213; P11:145–150]

**Proposal deferrals:** dedicated microservices, broker/search/cache clusters, real-time collaborative editing, multi-region writes, generalized workflow/rules engine, configurable form builder, advanced dashboards, Office-to-HTML conversion, persisted PDF job orchestration absent measurement, fully self-service notice/legal-retention administration. Maintenance publication/export/purge capability itself is required, not deferred.

Not deferrable: OTP and internal auth, permission/context checks, Candidate mobile, allowed private uploads with real malware scanning, actual required email delivery, reports/multi-round/concurrency semantics, report PDF capability, temporary cleanup automation, audit/privacy/capacity safeguards and restore readiness. Removing any requires explicit controlled product change, not a claim that a simpler system does not need it.

## 11. Assumptions and unresolved product questions

The proposed architecture keeps the required capabilities while surfacing these issues. No unread technical source is used to decide them.

| Issue | Evidence and unresolved question | Effect / safe proposed treatment |
|---|---|---|
| Confirmed rescheduling wording | P05:63 says “Muốn Edit `CONFIRMED` → đổi status khác trước”; P13:65 says “HR changes status first.” P07:57 names a trusted reschedule action, and P13:360 says it atomically updates details and resets `AWAITING`. Must both UI paths exist, or is the explicit reschedule action the intended combined path? | Keep ordinary edit locked and conflict-safe explicit reschedule capability; do not claim workflow wording is reconciled. Resolve before final interaction acceptance. |
| Stale report semantics | P06:198 says “HR stale vs Interviewer newer → HR Save bị block”; P06:157 says “các field khác nhau (disjoint) được merge tự động”; P13:363 also requires disjoint merge. P06:200–201 requires stale HR-vs-HR and same-user tab blocking. Does a disjoint stale HR-vs-HR edit merge, or always reload? | Preserve field-aware design and owner-vs-HR same-field rule; require explicit precedence matrix for actor pair/field conflict before implementation acceptance. Blanket reject-all and blanket merge-all each lose a stated requirement. |
| Older NEW Submission and manual status | P03:112,125–139 permits editing NEW submissions; P04:130–142 navigation opens exact historical Submission; P13:304 says “historical child Submission cannot be mutated” by manual status, with deterministic latest selection. How does HR reopen an older processed Submission when Candidate is told to contact HR? | Retain historical read and allowed NEW edit; no architecture-level permission to reopen old status. Resolve latest-only manual-status UX and explain unsupported recovery explicitly. |
| Operational official PDF | P13:159 requires “official PDF template if PDF is used operationally”; P14:19 says official pixel template is “DEFERRED”; P10:207 waits for it while P06 requires download. Is a non-official, content-correct PDF approved for operational use before the template arrives? | Build real semantic Preview/PDF; do not claim official fidelity or permission for official use. Owner decision controls operational acceptance, not whether capability is silently omitted. |
| Snapshot email equality after recovery | P13:27 rejects Submission email not matching verified Candidate identity; P13:358 requires recovery “preserving historical Submission email snapshots.” Is equality a create-time/new-snapshot rule rather than a perpetual invariant? | Propose create-time identity validation and immutable historical snapshots; never rewrite history to satisfy blanket equality. Confirm recovery semantics before release. |
| Exact desktop table widths | D-T:120 gives Inbox minimum 1560px, but listed widths sum to 1660px; D-T:144 gives Report minimum 1610px, listed widths sum to 1610px. P13:198 demands Report sum match. Are Inbox widths authoritative over the named minimum? | Preserve readable 16px aligned columns/horizontal overflow; do not silently adjust frozen design. Resolve Inbox dimension inconsistency during visual UAT. |
| Badge guidance | D-K:66–70 marks initial targets 112px Interview/168px Report; D-R:77 later specifies 144px benchmark with wrapping. | Initial token targets are expressly adjustable; propose normative responsive benchmark with no truncation. Confirm final VI/EN visual acceptance, not a new product workflow. |
| Legal and content inputs | P42:28–29 defers exact legal notice/retention rules to Legal; P11:13 requires final email copy; P14:19 waits for official PDF. | Capability can be built with approved non-production content, but real-data launch needs legal-approved notices/handling and approved message content. No claim indefinite retention is legally permissible. |
| Scanner/provider/runtime selection | Product requires scan, mail, retry/cleanup and latency, but permitted material establishes no approved vendor, data-processing location, purchased quotas or runtime limits. | Select/verify before launch; managed scan proposed only if privacy and allowed formats fit. External scheduler/worker placement remains an implementation choice; no current cloud inspection in Phase A. |
| Recovery and retention authorization details | Product sources identify privileged recovery and maintenance-only publication/export/purge, but linked operational runbooks were not read under isolation. | Architecture reserves restricted audited maintenance operations; exact identity evidence, approval steps, export format and purge safeguards require permitted Owner clarification/later authorized investigation. No invented unrestricted admin endpoint. |

Assumptions labeled as proposals: a single-region modular application can meet the stated baseline; bounded existing-platform handlers can deliver mail/cleanup within verified quotas; content-correct PDF can be rendered without an external browser fleet. These are testable design choices, not verified platform facts. If measurements disprove them, add only the failing boundary's runtime, not a distributed rewrite of the conceptual model.

## 12. Complexity We Would Refuse To Add Without Evidence

- Microservices or separate frontend/backend deployments for each page: R11–R20 favor shared transactions and policy; extra network boundaries buy no demonstrated product value.
- A message broker/event-stream cluster for email and temp cleanup: durable DB intent plus bounded handlers meets the stated behavior if measured; keep real leases/retries, not a pretend synchronous send.
- Generic policy/command/workflow DSLs or user-configurable form engines: explicit granular permissions and a finite approved workflow are sufficient. Keep the actual role/context checks.
- Scoring, stars, competency scales, AI ranking or automatic hiring decisions: scoring is explicitly forbidden, not merely low priority. [P06:131]
- Event sourcing for every entity, full-row report last-write-wins, or universal CRDT collaboration: only bounded report field merge is required. Audit is retained traceability, not an alternate business database.
- Search clusters, browser-wide datasets, speculative materialized caches, realtime subscriptions or global store machinery before measuring the paginated baseline. Latest/current truth must not depend on asynchronously repaired caches.
- Universal PDF orchestration, headless-browser fleet or document-conversion service before a bounded renderer is measured. Do not confuse refusing machinery with refusing required PDF download or malware scanning.
- Exactly-once email delivery promises, treating queue acceptance as recipient delivery, or infinite retries. Provider crash ambiguity is explicit product acceptance. [P11:147]
- Automatic business-record expiry/purge, “delete all” administration, or treating temporary cleanup as authority to remove retained recruitment data. [P42:3–15]
- Empty future-module navigation, broad analytics, offer/onboarding automation or a product Dashboard disguised as capacity monitoring. [P14:35–36]
- Duplicate delivery registries, repeated prose evidence receipts and gates proving the same unchanged behavior: propose one attributable acceptance result per risk/slice, without bypassing mandatory authorization or independent review.
- Architecture conclusions about the current code from product command names, repository filenames, injected instructions or unread research. Phase A supplies a frozen comparison target, not a current-system verdict.

### Pre-freeze validation record

Substantive document validation: the sixteen A3 questions are mapped in §2; all A4 sections are present in §§2–12. Required claims are grounded in the permitted source ledger; architecture/runtime/process choices are labeled proposals. Candidate mobile, multi-round reports, no scoring, private scanned uploads, required email/PDF/cleanup, retention and field-aware concurrency remain in scope. Future-hidden modules and deferred pixel-template fidelity are distinguished from mandatory capabilities. Conflicting wording and unverified operational inputs are explicit in §11. No application/cloud verification is represented as performed. Final file read and fingerprint are reported outside this artifact after freeze.

GREENFIELD_PHASE_A_FROZEN: YES
