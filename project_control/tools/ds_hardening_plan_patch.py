from __future__ import annotations

from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one match, found {count}")
    return text.replace(old, new, 1)


def write(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8", newline="\n")

# -----------------------------------------------------------------------------
# TASK_REGISTRY.yaml
# -----------------------------------------------------------------------------
task_path = ROOT / "project_control" / "TASK_REGISTRY.yaml"
task = task_path.read_text(encoding="utf-8")
task = replace_once(
    task,
    "version: 1\ncurrent_slice: SLICE-04\ncurrent_task: TASK-S04-004\n",
    "version: 1\ncurrent_slice: SLICE-DS\ncurrent_task: TASK-DS-001\n",
    "task current pointer",
)
old_s04 = '''  TASK-S04-004:\n    title: "HR Interview scheduling UI over accepted trusted commands"\n    slice: SLICE-04\n    status: READY\n    lane: LANE_A\n    depends_on:\n      - TASK-S04-005\n    prompt: project_control/prompts/SLICE-04_TASK-004_v3.md\n    prompt_sha256: ae622650bd9d79af28c30a870f2c84d15aeac764ab4393cd5f7b343040b9c7ce\n    prompt_review_status: "PASS (ChatGPT exact-source reconciliation re-review @ a4d85a9033b3b54195265a893710d08a626ef9bb; blockers: NONE)"\n    notes: "TASK-S04-005 dependency is satisfied and CI-verified. Reconciliation review found and repaired the v2 backend-baseline/idempotency ambiguities in v3. Exact-source v3 re-review passed with no canonical-source reopening; TASK-S04-004 is READY for the authorized frontier after reconciliation release."\n'''
new_s04 = '''  TASK-S04-004:\n    title: "HR Interview scheduling UI over accepted trusted commands"\n    slice: SLICE-04\n    status: BLOCKED\n    lane: LANE_A\n    depends_on:\n      - TASK-S04-005\n      - TASK-DS-006\n    prompt: project_control/prompts/SLICE-04_TASK-004_v3.md\n    prompt_sha256: ae622650bd9d79af28c30a870f2c84d15aeac764ab4393cd5f7b343040b9c7ce\n    prompt_review_status: "PASS (ChatGPT exact-source reconciliation re-review @ a4d85a9033b3b54195265a893710d08a626ef9bb; blockers: NONE)"\n    notes: "TASK-S04-005 remains satisfied and CI-verified. Owner sequencing decision 2026-09-08 requires Production Design-System Hardening (TASK-DS-001..006) before S04-004 implementation so Interview desktop/responsive UI consumes a converged production design foundation. This is planning/implementation sequencing only; no Product/Business/Design source reopening is required. Release S04-004 only after TASK-DS-006 is DONE and checkpoint/design-system-production-ready-001 exists."\n'''
task = replace_once(task, old_s04, new_s04, "S04-004 rebaseline")

append_tasks = '''\n\n  TASK-DS-001:\n    title: "Design-system canonical/runtime token convergence and production token hygiene"\n    slice: SLICE-DS\n    status: READY\n    lane: LANE_A\n    depends_on:\n      - TASK-S04-005\n    prompt: project_control/prompts/DESIGN_SYSTEM_HARDENING_v1.md\n    plan_section: DS-001\n    notes: "Reconcile documented/runtime token semantics, fix known token-name drift, remove scoped undefined/fallback palette debt, and establish unambiguous Interview 144px operational badge handling without reopening Design System v1.8."\n\n  TASK-DS-002:\n    title: "Production shell architecture and responsive internal navigation"\n    slice: SLICE-DS\n    status: PLANNED\n    lane: LANE_A\n    depends_on:\n      - TASK-DS-001\n    prompt: project_control/prompts/DESIGN_SYSTEM_HARDENING_v1.md\n    plan_section: DS-002\n    notes: "Separate Auth/Candidate/Internal shell responsibilities and implement desktop/tablet/mobile InternalAppShell navigation with focus, Escape, inertness, scroll-lock, and restoration semantics while preserving accepted business routes."\n\n  TASK-DS-003:\n    title: "Reusable production UI primitive layer for current and near-frontier operational pages"\n    slice: SLICE-DS\n    status: PLANNED\n    lane: LANE_B\n    depends_on:\n      - TASK-DS-001\n    prompt: project_control/prompts/DESIGN_SYSTEM_HARDENING_v1.md\n    plan_section: DS-003\n    notes: "Materialize a bounded shared primitive layer (buttons/status/menu/dialog/drawer/form/table-scroller/async feedback as justified by current consumers) and stop feature-local primitive duplication. No speculative theme/framework rewrite."\n\n  TASK-DS-004:\n    title: "Existing production responsive convergence on in-scope accepted routes"\n    slice: SLICE-DS\n    status: PLANNED\n    lane: LANE_A\n    depends_on:\n      - TASK-DS-002\n      - TASK-DS-003\n    prompt: project_control/prompts/DESIGN_SYSTEM_HARDENING_v1.md\n    plan_section: DS-004\n    notes: "Converge Login, Candidate shell/Form/Phiếu của tôi, Application Inbox, and shared overlays/navigation to Design System v1.8 + Responsive Prototype v1.10 presentation without changing accepted business/RPC/schema behavior."\n\n  TASK-DS-005:\n    title: "Production design-contract static linting and enforcement"\n    slice: SLICE-DS\n    status: PLANNED\n    lane: LANE_A\n    depends_on:\n      - TASK-DS-004\n    prompt: project_control/prompts/DESIGN_SYSTEM_HARDENING_v1.md\n    plan_section: DS-005\n    notes: "Extend design validation from documentation-only checks into production token/CSS/TSX contract checks that are statically provable; avoid pretending static lint proves runtime accessibility."\n\n  TASK-DS-006:\n    title: "Production responsive browser acceptance gate for the hardened design foundation"\n    slice: SLICE-DS\n    status: PLANNED\n    lane: LANE_A\n    depends_on:\n      - TASK-DS-005\n    prompt: project_control/prompts/DESIGN_SYSTEM_HARDENING_v1.md\n    plan_section: DS-006\n    notes: "Run production browser QA at representative phone/tablet/desktop widths with focused repair reruns and one full hardening acceptance matrix; acceptance creates checkpoint/design-system-production-ready-001 before S04-004 is released."\n'''
if "  TASK-DS-001:" in task:
    raise RuntimeError("DS tasks already materialized")
task = task.rstrip() + append_tasks + "\n"
write(task_path, task)

# -----------------------------------------------------------------------------
# SLICE_REGISTRY.yaml
# -----------------------------------------------------------------------------
slice_path = ROOT / "project_control" / "SLICE_REGISTRY.yaml"
slice_text = slice_path.read_text(encoding="utf-8")
slice_text = replace_once(slice_text, "current_slice: SLICE-04\n", "current_slice: SLICE-DS\n", "slice current pointer")
anchor = "  SLICE-04: {name: Interview Scheduling / Participants / Copy / Reactivate, status: IN_PROGRESS, current_task: TASK-S04-004}\n"
insert = anchor + "  SLICE-DS: {name: Production Design System Hardening / Responsive Convergence, status: IN_PROGRESS, current_task: TASK-DS-001}\n"
slice_text = replace_once(slice_text, anchor, insert, "SLICE-DS insertion")
write(slice_path, slice_text)

# -----------------------------------------------------------------------------
# AUTONOMY_RUN_STATE.yaml
# -----------------------------------------------------------------------------
run_path = ROOT / "project_control" / "AUTONOMY_RUN_STATE.yaml"
run = run_path.read_text(encoding="utf-8")
plan_anchor = '''  feature_dispatch: RELEASED\n\nactive_workers: []\n'''
plan_insert = '''  feature_dispatch: RELEASED\n\ndesign_system_hardening:\n  initiative_id: DESIGN-SYSTEM-HARDENING-001\n  status: IN_PROGRESS\n  owner_sequencing_decision: "2026-09-08: harden the production Design System before TASK-S04-004, then resume S04-004 immediately after DS acceptance."\n  baseline_sha: "8897d08f01b9f4738500eecfd6170dc0a9c77f54"\n  pre_hardening_checkpoint: checkpoint/pre-design-system-hardening-001\n  canonical_design_system: "v1.8 CURRENT"\n  responsive_reference: "v1.10 executable UX/UAT evidence"\n  product_source_reopen_required: false\n  design_source_reopen_required: false\n  task_dag:\n    - TASK-DS-001\n    - TASK-DS-002\n    - TASK-DS-003\n    - TASK-DS-004\n    - TASK-DS-005\n    - TASK-DS-006\n  exit_checkpoint: checkpoint/design-system-production-ready-001\n  blocked_frontier_after_acceptance: TASK-S04-004\n\nactive_workers: []\n'''
run = replace_once(run, plan_anchor, plan_insert, "run-state DS initiative")
old_frontier = '''safe_frontier:\n  eligible_tasks:\n    - TASK-S04-004\n  skipped_due_to_dependency: []\nnext_action: "Before any TASK-S04-004 application edit, verify immutable recovery ref checkpoint/pre-S04-004-001 points to the final reviewed governance baseline; then dispatch TASK-S04-004 using project_control/prompts/SLICE-04_TASK-004_v3.md under producer self-review -> OMP candidate review -> serialized integration -> final exact-SHA OMP acceptance re-review if SHA changes -> impact-selected exact-SHA CI -> immutable accepted-checkpoint."\n'''
new_frontier = '''safe_frontier:\n  eligible_tasks:\n    - TASK-DS-001\n  skipped_due_to_dependency:\n    - TASK-S04-004\nnext_action: "Execute DESIGN-SYSTEM-HARDENING-001 from checkpoint/pre-design-system-hardening-001. Start TASK-DS-001; advance only through the materialized DAG and focused verification gates. TASK-S04-004 remains BLOCKED until TASK-DS-006 is DONE and checkpoint/design-system-production-ready-001 is created."\n'''
run = replace_once(run, old_frontier, new_frontier, "safe frontier")
write(run_path, run)

# -----------------------------------------------------------------------------
# CURRENT_STATE.md (derived handoff only)
# -----------------------------------------------------------------------------
current_path = ROOT / "project_control" / "CURRENT_STATE.md"
current = current_path.read_text(encoding="utf-8")
old_section = '''## Plan reconciliation result and current frontier\n\n`SOURCE → IMPLEMENTATION → PLAN RECONCILIATION @ TASK-S04-005` is **VERIFIED**.\n\n- Accepted implementation is reconciled through `TASK-S04-005`.\n- No canonical Business Logic v1.2 / Technical Architecture v1.18 reopening was required.\n- The initial v2 prompt re-review found two blocking ambiguities (missing accepted `20260906060000` baseline and retry-key wording); both were repaired in v3.\n- Exact-source v3 re-review at `a4d85a9033b3b54195265a893710d08a626ef9bb` passed with no remaining blockers.\n- Authoritative task state is now `TASK-S04-004 = READY`.\n- Safe frontier is `TASK-S04-004`.\n\nReleased prompt:\n\n`project_control/prompts/SLICE-04_TASK-004_v3.md`\n'''
new_section = '''## Plan reconciliation result and current frontier\n\n`SOURCE → IMPLEMENTATION → PLAN RECONCILIATION @ TASK-S04-005` remains **VERIFIED**.\n\n- Accepted application implementation remains reconciled through `TASK-S04-005`.\n- No canonical Business Logic v1.2 / Technical Architecture v1.18 reopening is required.\n- `SLICE-04_TASK-004_v3.md` remains the released S04-004 product/technical prompt.\n- Owner sequencing decision on 2026-09-08 inserts a bounded **Production Design-System Hardening** initiative before S04-004 so the Interview page consumes a converged responsive production foundation.\n- This is planning/implementation sequencing, not a Product/Business/Design source rewrite.\n- Current authoritative frontier is `TASK-DS-001`; `TASK-S04-004 = BLOCKED` until `TASK-DS-006 = DONE` and `checkpoint/design-system-production-ready-001` exists.\n\nDesign-System hardening DAG:\n\n`DS-001 Tokens → (DS-002 Shell || DS-003 Primitives) → DS-004 Responsive convergence → DS-005 Design-contract lint → DS-006 Browser acceptance → S04-004`\n\nHardening plan:\n\n`project_control/prompts/DESIGN_SYSTEM_HARDENING_v1.md`\n'''
current = replace_once(current, old_section, new_section, "CURRENT_STATE frontier section")
old_resume = '''6. confirm `plan_reconciliation.status = VERIFIED`, `TASK-S04-004 = READY`, and `safe_frontier = [TASK-S04-004]`;\n7. read `SLICE-04_TASK-004_v3.md` plus its canonical business/design/backend sources and the accepted ordered migration chain through `20260906090000_application_reactivation_and_participant_contract_repair.sql`;\n8. verify `checkpoint/pre-S04-004-001` resolves to the final governance baseline before any application edit;\n9. continue S04-004 implementation → focused verification → ChatGPT producer self-review/repair → OMP read-only candidate review persisted by OMP main on a non-candidate review evidence branch → targeted repair/re-review if needed → serialized integration → final exact-SHA OMP acceptance re-review/equivalence check if SHA changes → impact-selected exact-SHA CI → immutable accepted checkpoint → slice-closing review if S04 completes.\n'''
new_resume = '''6. confirm `plan_reconciliation.status = VERIFIED`, `design_system_hardening.status = IN_PROGRESS`, `TASK-DS-001 = READY`, and `safe_frontier = [TASK-DS-001]`;\n7. read `DESIGN_SYSTEM_HARDENING_v1.md`, current Design System v1.8 and Responsive Prototype v1.10 authority before production UI hardening;\n8. verify `checkpoint/pre-design-system-hardening-001` resolves to `8897d08f01b9f4738500eecfd6170dc0a9c77f54`;\n9. complete DS-001..006 under focused verification and stop the hardening initiative once its explicit exit criteria pass; create `checkpoint/design-system-production-ready-001`; then re-release/rebase S04-004 on that exact checkpoint and resume the established ChatGPT producer → OMP independent review → exact-SHA acceptance lifecycle.\n'''
current = replace_once(current, old_resume, new_resume, "CURRENT_STATE resume protocol")
old_next = '''## Next action\n\nVerify `checkpoint/pre-S04-004-001` points to this final governance baseline, then use `SLICE-04_TASK-004_v3.md` to dispatch `TASK-S04-004` under producer self-review → OMP candidate review → serialized integration → final exact-SHA OMP acceptance re-review if needed → impact-selected exact-SHA CI → immutable accepted-checkpoint lifecycle.\n'''
new_next = '''## Next action\n\nExecute `TASK-DS-001` from `checkpoint/pre-design-system-hardening-001`, then advance through the bounded Design-System Hardening DAG. Do not start S04-004 application implementation until DS-006 is accepted and `checkpoint/design-system-production-ready-001` is verified.\n'''
current = replace_once(current, old_next, new_next, "CURRENT_STATE next action")
write(current_path, current)

# -----------------------------------------------------------------------------
# Master implementation prompt / bounded initiative contract
# -----------------------------------------------------------------------------
prompt_path = ROOT / "project_control" / "prompts" / "DESIGN_SYSTEM_HARDENING_v1.md"
if prompt_path.exists():
    raise RuntimeError("hardening prompt already exists")
prompt = r'''# DESIGN-SYSTEM-HARDENING-001 — Production Design-System Hardening before TASK-S04-004

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
'''
write(prompt_path, prompt)

# Validate parse/control plane before commit.
subprocess.run(["python", "project_control/validate_omp_native.py"], cwd=ROOT, check=True)
subprocess.run(["python", "project_control/validate_control_plane.py"], cwd=ROOT, check=True)
subprocess.run(["git", "diff", "--check"], cwd=ROOT, check=True)

subprocess.run(["git", "add", "project_control/TASK_REGISTRY.yaml", "project_control/SLICE_REGISTRY.yaml", "project_control/AUTONOMY_RUN_STATE.yaml", "project_control/CURRENT_STATE.md", "project_control/prompts/DESIGN_SYSTEM_HARDENING_v1.md"], cwd=ROOT, check=True)
subprocess.run(["git", "commit", "-m", "plan: materialize production design-system hardening gate"], cwd=ROOT, check=True)
subprocess.run(["git", "push", "origin", "HEAD:governance/design-system-hardening-001"], cwd=ROOT, check=True)
