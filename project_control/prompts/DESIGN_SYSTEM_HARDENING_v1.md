# DESIGN-SYSTEM-HARDENING-001 — Production Design-System Hardening before TASK-S04-004

## Authority and intent

This is a bounded production-implementation initiative. It does **not** replace or reopen Business Logic Core v1.2, Technical Architecture v1.18, Design System v1.8, or Responsive Prototype v1.10. Current source precedence remains unchanged.

Owner sequencing decision: harden the production Design System first, then proceed immediately to TASK-S04-004 from the accepted hardening checkpoint.

### Hard scope boundaries

Allowed:
- production UI shell/layout architecture;
- production design tokens and token consumption;
- reusable UI primitives already justified by current/near-frontier pages;
- presentation-only responsive convergence on already accepted routes;
- production design-contract static validation;
- production browser responsive/accessibility QA;
- narrowly necessary tests/fixtures/configuration for those concerns.

Forbidden unless a proven blocker forces an Owner decision:
- business-rule changes;
- new or changed Supabase migrations/RPC behavior;
- RLS/GRANT weakening;
- candidate/application/interview lifecycle changes;
- canonical product/design source rewrite;
- speculative theme engine, dark mode, dashboard framework, Storybook showcase, animation system, or unrelated visual redesign;
- deployment/main publication.

## Baseline / recovery

- Baseline SHA: `8897d08f01b9f4738500eecfd6170dc0a9c77f54`
- Immutable pre-hardening checkpoint: `checkpoint/pre-design-system-hardening-001`
- Target accepted checkpoint: `checkpoint/design-system-production-ready-001`
- S04-004 remains BLOCKED until DS-006 is DONE and the target checkpoint exists.

## Shared verification economy

During implementation/repair:
- run focused tests/checks for the changed scope;
- a failure reopens only the failed check, directly affected regressions, changed dependency/shared-contract checks, or concrete crossed invariants;
- do not rerun unrelated previously passed suites blindly.

Acceptance:
- each DS task must have focused PASS evidence;
- DS-006 runs one deliberate broader production responsive/browser matrix;
- final hardening acceptance runs lint + typecheck + build + relevant unit/browser/design-contract gates;
- database reset/regressions are not required because this initiative must not change database contracts.

## DS-001 — Canonical/runtime token convergence

Goals:
1. Fix known runtime token-name drift (`--font-size-title-page` consumer vs canonical `--font-size-page-title`).
2. Make Interview operational status badge semantics unambiguous: current Interview/HR Report page benchmark is 144px; do not silently reinterpret the generic initial 112px token as the page contract.
3. Remove/replace undefined CSS variables and feature-local Slate-like fallback palette in the in-scope production styles where canonical/approved tokens exist.
4. Add only semantic/layout tokens that are actually consumed by current production components; avoid speculative token proliferation.
5. Preserve >=16px hard rule for body/table/form/control/badge primary content; 14px remains secondary metadata only.

Acceptance:
- no known token typo remains;
- no unresolved undefined CSS variable use in in-scope styles;
- Interview operational badge has an explicit 144px production token/primitive contract that fits the frozen 170px status column;
- focused token/design tests PASS.

## DS-002 — Shell architecture + responsive navigation

Goals:
1. Stop routing Candidate pages through the Internal HR shell.
2. Separate Auth/Candidate/Internal shell responsibilities using App Router layout architecture or an equivalently explicit boundary; do not rely on broad pathname string matching for all product shells.
3. Internal desktop retains fixed 244px EIU sidebar.
4. Tablet/mobile Internal shell provides an accessible menu trigger, off-canvas navigation/scrim, Escape close, focus containment/restoration, background inertness/semantic hiding, and scroll lock.
5. Candidate shell remains external/mobile-oriented and does not inherit HR navigation.
6. Existing accepted routes/permissions/business behavior remain unchanged.

Acceptance:
- `/login`/auth UI, Candidate routes, and Internal routes resolve to the intended shell family;
- Internal responsive navigation keyboard/focus behavior is tested;
- desktop shell remains visually/structurally compatible with v1.8.

## DS-003 — Bounded reusable production primitives

Materialize only primitives justified by current accepted pages and S04/S05 near frontier, preferring semantic/native behavior:
- Button / IconButton where duplication exists;
- StatusBadge + anchored StatusMenu behavior;
- Alert / AsyncStatus;
- Dialog / ConfirmationDialog;
- Drawer / ResponsiveSheet;
- FormField helpers where useful;
- PageHeader / ActionToolbar where current duplication warrants it;
- TableScrollContainer and table layout helpers.

Rules:
- primitives own shared dimensions/focus/disabled/pending semantics;
- feature modules own business composition and exact page columns;
- no generic primitive may encode recruitment business rules;
- stop introducing feature-global `.btn-*`, `.status-badge`, `.drawer` collisions.

Acceptance:
- primitives have focused unit/interaction coverage;
- at least existing in-scope consumers use them enough to prove the layer is real rather than paper architecture;
- no required feature behavior regresses.

## DS-004 — Existing responsive convergence

In-scope accepted production routes/components:
- Login/auth presentation;
- Candidate shell + Candidate Form;
- Candidate `Phiếu của tôi` / submissions list;
- Application Inbox table/shell/overlays;
- shared Internal shell/navigation/overlays.

Requirements:
- presentation-only convergence; preserve existing trusted-command/business behavior;
- Candidate desktop table contract and mobile structured presentation remain semantically equivalent;
- no primary/control text below 16px in the in-scope routes;
- practical touch targets target >=44px where interactive on touch layouts;
- existing good Application Inbox 1560px semantic table pattern is preserved;
- drawers use current responsive width/sheet rules rather than copying the old 760px/36px debt forward.

Acceptance:
- focused existing unit tests remain PASS;
- new responsive behavior has focused interaction/browser coverage;
- no PII is introduced into URL state.

## DS-005 — Design-contract static linting

Extend production enforcement for statically provable rules. At minimum detect:
- undefined CSS custom properties in in-scope production CSS;
- known invalid/deprecated design-token names;
- primary/control font sizes below 16px where statically expressible;
- forbidden feature-local duplication of shared primitive global selectors after migration;
- unnecessary raw fallback colors where an approved token is required by the hardening scope.

Do not claim static lint proves runtime focus management, contrast, zoom/reflow or full WCAG compliance.

Acceptance:
- validator is inspectable, deterministic, and fails on seeded negative fixtures or focused unit checks;
- current hardened production source passes.

## DS-006 — Production responsive browser acceptance gate

Run production browser QA at representative widths:
- 360
- 390
- 430
- 768
- 1024
- 1280
- 1440

Critical pages/flows at hardening acceptance:
- Login/auth shell;
- Candidate Form;
- Candidate `Phiếu của tôi`;
- Application Inbox;
- Internal navigation/shell;
- representative Dialog/Drawer/Status interactions supplied by current consumers/fixtures.

Check at minimum:
- no unintended page-level horizontal overflow;
- intentional wide tables scroll only in their table container;
- correct shell/navigation family;
- hidden navigation is not keyboard/screen-reader reachable;
- drawer/dialog/sheet focus containment, Escape, backdrop inertness and focus restoration;
- sticky columns/header remain usable;
- long VI/EN text does not clip;
- no critical control drops below the design typography/touch contract;
- no browser console errors in audited flows.

Repair reruns remain focused. One complete matrix is required only for final DS-006 acceptance.

## Initiative exit criteria

The initiative is DONE only when all are true:
1. DS-001..DS-006 are DONE.
2. Product/Business/Technical/Design canonical source reopening remains NO.
3. Canonical/runtime token drift identified by this initiative is reconciled.
4. Auth/Candidate/Internal production shell responsibilities are explicit.
5. Internal responsive navigation passes focused keyboard/focus/browser checks.
6. Bounded reusable primitives exist and are consumed by current production UI.
7. In-scope accepted routes converge to the current responsive/design hard rules without business behavior changes.
8. Production design-contract static validator passes.
9. Final responsive browser matrix passes.
10. Lint, typecheck and production build pass on the exact final hardening SHA.
11. ChatGPT exact-diff self-review has no blockers.
12. `checkpoint/design-system-production-ready-001` is created immutably at that accepted SHA.

After criterion 12, STOP hardening. Reconcile control-plane back to `SLICE-04 / TASK-S04-004`, rebase/recreate the S04-004 task branch from the accepted checkpoint, and implement S04-004 under its existing v3 product/technical prompt plus the hardened production design foundation.
