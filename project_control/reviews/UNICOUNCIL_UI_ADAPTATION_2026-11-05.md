# UniCouncil-inspired recruitment UI — 2026-11-05

Owner explicitly requested applying the studied UniCouncil interface to the
existing Site. Development-branch synchronization and static demo refresh are
authorized; main/backend/recovery acceptance and final Owner visual UAT remain held.

Product: `29697ff98177fc51984c462c638b0ae5fb84c71e`.
Base: `97bad546cc3fc35165cd78b6755c0b6ad70407a0`.
Reference: `baonguyen-kobe/UniCouncil-Scheduler` at
`1be71591bba158ae6d14014e9c7944070ff9d46b`.
Canonical controlled trial: `CR-UNICOUNCIL-UI-ADAPTATION-20261105` in Design System
MASTER.md, matching typography/accessibility/component/responsive clauses and
review-pack UI specification. Generated All-in-One and manifests are synchronized.

## Result

- Real EIU logo with pinned provenance and one outline navigation icon family.
- Compact workspace header, one primary content heading and one visible header
  trial-workspace entry. Six role options, reset, guide and browser-local state
  remain; the optional shell slot supplies no real application authority.
- Shared scoped14px/21px operational hierarchy with16px names and body/form/
  dialog/detail/narrative/mobile input text.44px touch targets remain.
- Concise filters and contextual help; row selection exposes bulk controls while
  zero-selection announcements/focus fallback remain. Narrow cards retain full
  detail access, including birth date/gender.
- Inbox usable list height at390x844 increased164px to368px. Users More triggers
  fit as44px icon targets, preserving room for Edit in stable action columns.
- Fixed new page-help clipping using bounded native popovers; keyboard, outside
  dismissal, anchor movement and short-screen bounds verified. Explicit inline
  dialog restoration prevents compact typography leaking into full details.
- No domain/authorization/privacy/version-token/storage-schema/backend changes.
  EIU branding is the unmodified asset supplied in the reference; no new package.

## Fresh verification and review

All409 unique web tests are verified passing on this product state. The initial
complete run passed400;9 HTTP-based cases hit OS connect EACCES on localhost in
the restricted execution environment. Only the exact5 affected files were rerun
with the required local-network permission and all9 passed. No application code
was changed for this environmental retry; previously passed unrelated checks
remained closed. Production-bundle auth uses fake CI public values and intercepted
requests; no real authentication provider is contacted.

| Check | Evidence |
|---|---|
| Web checks |Lint232files, typecheck, design224files/84tokens and build PASS |
| Parent browser audit |72 final populated VI/EN scenes PASS at1440/1366x768/390x844/320x844 |
| Worker render audit |108 populated VI/EN scenes across six widths PASS; not counted as unique parent cases |
| Bounds/fonts |No global/local-table horizontal overflow or page errors; actual bundled fonts/glyphs loaded |
| Source/control |515 source,73 design,565 manifest checks and control/OMP25skills PASS |
| Exact-SHA independent review |PASS;20 focused tests and48 bilingual context-panel cases |

Reviewer independently verified workspace unique labels/six roles/inertness/Tab/
Escape/focus,44x44 language controls, inline forms and full HR note at16px without
clipping. This is independent Codex local review, not formal OMP acceptance.

## Published Site

Native deployment returned succeeded for existing Site version3:
https://eiu-recruitment-trial-20261105.tidyburl1.chatgpt.site

Current public Owner-configured audience (revision2) was preserved; this work
made no access-policy change. Source helper pushed the exact distribution and
packaged matching HTML with third-party notices and EIU asset provenance.

HTML SHA-256:
`6518c1548e3c9464203e0a7da3b8bc0d649a8b8bac2453c588c14282c25cda00`.
Version/deployment/source/archive identifiers are indexed under
`EVIDENCE_INDEX.yaml:implementation_evidence.UNICOUNCIL-UI-ADAPTATION-20261105`.

The Site remains a synthetic browser-local demo with no connected real EIU auth,
mail, private upload processing or recruitment database. No main integration,
accepted checkpoint, production application release or Package009 acceptance.
