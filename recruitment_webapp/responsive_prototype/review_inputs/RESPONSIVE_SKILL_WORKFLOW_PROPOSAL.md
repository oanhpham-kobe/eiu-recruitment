# EIU RECRUITMENT APP — REBUILD RESPONSIVE / MOBILE USING SKILLS

You are working on the **EIU Recruitment App**.

The responsive/mobile implementation has already been started, but much of it was built freely without a disciplined skill-driven workflow.

Your task is to **audit, normalize, and rebuild the responsive/mobile implementation using the project's current source of truth and selected engineering skills**.

This is NOT permission to blindly delete the current responsive implementation.

The correct approach is:

```text
DISCOVER
→ AUDIT CURRENT IMPLEMENTATION
→ IDENTIFY WHAT IS ALREADY CORRECT
→ DEFINE RESPONSIVE CONTRACTS
→ REUSE
→ REFACTOR ONLY WHERE NECESSARY
→ IMPLEMENT
→ BROWSER VERIFY
→ REVIEW
→ USER VISUAL ACCEPTANCE

```

The current repository, current application behavior, current handover/specification documents, and current Design System are authoritative.

Do not redesign the Recruitment App from generic UI preferences.

---

# 0. SOURCE REPOSITORIES FOR SKILLS

The AI may not know where these skills come from.

Use these exact GitHub repository coordinates and inspect their CURRENT contents before installing/copying anything:

```text
Karpathy:
multica-ai/andrej-karpathy-skills

Vercel:
vercel-labs/agent-skills

ECC:
affaan-m/ECC

Front-End Checklist:
thedaviddias/Front-End-Checklist

Matt Pocock:
mattpocock/skills

Superpowers:
obra/superpowers

GitNexus:
abhigyanpatwari/GitNexus

```

Do not rely on remembered skill names or stale copies.

Inspect the current `SKILL.md` and its frontmatter `name:` before activation.

For example, Vercel's folder name and actual skill `name:` may differ.

Resolve the CURRENT name from the source rather than assuming an old alias.

Do not install an entire large skill catalog when only a small number of skills are needed.

---

# 1. REQUIRED SKILL LANE FOR THIS RESPONSIVE PROJECT

## Core — always use during responsive implementation

Use:

```text
karpathy-guidelines
Vercel React best-practices skill
accessibility

```

Resolve the actual current Vercel skill frontmatter name from:

```text
vercel-labs/agent-skills/skills/react-best-practices/

```

Do not hard-code a stale alias.

`karpathy-guidelines` is responsible for:

- thinking before changing code;
- keeping changes surgical;
- avoiding unnecessary abstractions;
- defining verifiable success criteria;
- preserving valid existing implementation.

Vercel React best practices is responsible for:

- React/Next.js implementation quality;
- Server/Client component boundaries;
- render behavior;
- bundle/performance implications;
- state and component implementation quality.

`accessibility` is responsible for:

- semantic HTML;
- accessible names;
- touch target sizing;
- keyboard operation;
- focus states;
- focus management;
- form labels/errors;
- dialogs/drawers;
- responsive reflow;
- zoom/text scaling;
- screen-reader semantics.

---

# 2. CONDITIONAL SKILLS

Do NOT load every skill for every task.

## Shared component architecture

Use Vercel composition patterns ONLY if responsive implementation requires redesigning shared component APIs.

Source:

```text
vercel-labs/agent-skills/skills/composition-patterns/

```

Use it particularly if existing code starts accumulating props such as:

```text
mobile
compact
stacked
condensed
hideColumns
mobileActions
mobileCard
isMobileVariant

```

Do not create boolean-prop explosion merely to support mobile.

Prefer explicit composition/variants only when the source architecture genuinely needs them.

For a localized CSS/grid/flex responsive change, do NOT unnecessarily invoke composition refactoring.

---

## Interactive responsive behavior

Use:

```text
react-testing

```

from:

```text
affaan-m/ECC/skills/react-testing/

```

when responsive/mobile changes affect behavior such as:

- navigation drawer;
- sidebar open/close;
- mobile filters;
- comboboxes;
- menus;
- dialogs;
- responsive actions;
- form state;
- pagination;
- selection;
- uploads;
- status changes;
- candidate/application actions.

Test observable user behavior, not implementation internals.

Do not introduce a new testing framework if the Recruitment repo already has an established testing stack.

Adapt the skill to the repository's existing test framework.

---

## Bugs

Use:

```text
diagnosing-bugs

```

when a responsive bug is not obvious.

Typical examples:

```text
overflow only at one viewport
lost filter state
drawer scroll lock failure
modal focus failure
mobile menu closing unexpectedly
hydration mismatch
duplicate control rendering
desktop regression caused by mobile CSS
sticky element overlap
keyboard covering critical controls

```

Reproduce first.

Find the root cause.

Do not patch symptoms with page-specific CSS unless that is genuinely the narrowest correct solution.

---

## TDD

Use:

```text
tdd

```

only when responsive changes modify behavior or introduce a regression-prone interaction.

Do NOT force TDD onto simple visual CSS changes.

Examples where TDD is useful:

```text
drawer state
mobile filter persistence
action menu behavior
form validation
responsive navigation
selection behavior
modal behavior
responsive conditional actions

```

---

# 3. GITNEXUS — REQUIRED FOR SHARED RESPONSIVE CHANGES

Use GitNexus as the repository graph/impact engine.

Before modifying a shared component such as:

```text
application shell
sidebar
navigation
page container
page header
data table
toolbar
filters
form field
dialog
drawer
combobox
pagination
upload component
status/action component

```

use GitNexus to determine:

```text
definition
consumers
shared dependencies
execution/component relationships
affected routes/pages
blast radius

```

Then inspect the actual source.

Do not rely on GitNexus output alone.

Do not require GitNexus for a trivial page-local CSS edit whose scope is already obvious.

Do not introduce Graphify or Code Review Graph as a second graph system for this work.

---

# 4. FIRST ACTION — DO NOT CODE YET

Before changing responsive code, inspect the CURRENT Recruitment repository.

Report:

```text
repository root
branch
commit
git status
framework/runtime versions
existing responsive-related branches/worktrees if any
current Design System authority
current handover/spec authority
current responsive/mobile docs
current responsive tests
current browser/E2E tooling
current installed skills
GitNexus availability/index state

```

Locate the CURRENT canonical Recruitment documents.

Do not assume a remembered document version is latest.

If the repository contains newer versions than previous handovers or Design System documents, the newer current authority wins.

Read the relevant documents completely before implementation.

---

# 5. SOURCE OF TRUTH PRECEDENCE

Use:

```text
1. Explicit current user instruction

2. Current Recruitment business/security requirements

3. Current repository behavior and executable tests

4. Current canonical Recruitment handover/specification

5. Current canonical Recruitment Design System

6. Current approved page/component-specific design decisions

7. Existing desktop implementation where the Design System is silent

8. Selected implementation skills

9. Generic frontend recommendations

```

Skills must NOT override the Recruitment Design System.

Do not redesign colors, typography, density, branding, information architecture, terminology, workflow, permissions, status semantics, candidate data, application state, or business rules merely because a generic skill suggests another pattern.

---

# 6. AUDIT THE CURRENT FREE-FORM RESPONSIVE IMPLEMENTATION

Do not immediately rewrite it.

Inventory all responsive/mobile code.

Search for:

```text
media queries
Tailwind responsive prefixes
CSS breakpoint definitions
mobile-specific classes
hidden/block/flex/grid responsive switches
responsive tables
mobile cards
drawers/sheets
sidebar/mobile navigation
overflow-x
sticky/fixed elements
viewport sizing
100vh/dvh/svh
mobile-only components
desktop-only components
conditional rendering based on width
matchMedia
window.innerWidth
resize listeners
responsive utility functions
duplicate desktop/mobile markup

```

Produce a matrix:

```text
AREA
CURRENT IMPLEMENTATION
SOURCE/DESIGN CONTRACT
KEEP
ADAPT
REBUILD
REMOVE
REASON
SHARED CONSUMERS
RISK

```

Do not classify a section as `REBUILD` just because you would personally implement it differently.

Use:

```text
KEEP

```

when implementation already satisfies the current contract.

Use:

```text
ADAPT

```

when the architecture is sound but details are inconsistent.

Use:

```text
REBUILD

```

only when the implementation fundamentally conflicts with responsive requirements, accessibility, shared architecture, or maintainability.

Use:

```text
REMOVE

```

only for obsolete code made redundant by the approved replacement.

---

# 7. BUILD A RESPONSIVE DETAILED DESIGN CONTRACT BEFORE CODING

Derive the responsive rules from the CURRENT Design System and source.

Do not invent breakpoints if the project already defines them.

For every major component/page family determine:

```text
Desktop
Tablet
Mobile
Very narrow mobile

```

For each family explicitly answer:

```text
What remains visible?
What wraps?
What stacks?
What scrolls?
What collapses?
What becomes a drawer?
What becomes an action menu?
What changes order?
What never disappears?
What remains sticky?
What loses stickiness?
What remains full fidelity?
What can be summarized?
Where is horizontal scrolling intentionally allowed?
How are destructive/primary actions exposed?
How does keyboard/focus behave?
How do loading/error/empty states behave?

```

Do not shrink fonts to make desktop layouts fit mobile.

Do not hide required information or required actions merely to avoid overflow.

Do not convert every table to cards automatically.

Choose the representation based on actual information architecture and user workflow.

---

# 8. RESPONSIVE FOUNDATION — IMPLEMENT FIRST

Before fixing individual pages repeatedly, determine whether the issue belongs to shared foundations.

Inspect and normalize, where the source requires it:

```text
App shell
Sidebar/navigation
Mobile navigation
Page container
Page gutters
Page header
Section spacing
Responsive typography
Toolbar
Filter area
Form layout
Grid primitives
Tables/list shells
Dialog/drawer sizing
Action placement
Scrollable regions
Sticky regions
Safe area behavior

```

Prefer fixing a shared contract once over applying the same page-specific patch repeatedly.

But do not over-generalize a behavior that genuinely belongs to one page.

---

# 9. APPLICATION SHELL / MOBILE NAVIGATION

Verify at minimum:

```text
sidebar behavior
mobile navigation trigger
drawer/sheet behavior
focus movement
Escape behavior
focus restoration
scroll lock
active navigation indication
header height
page content offset
z-index layering
safe touch area
viewport height behavior

```

Do not leave both mobile and desktop navigation simultaneously accessible to screen readers when one is visually hidden.

Avoid JS viewport checks when CSS responsive behavior is sufficient.

If JS is required for behavioral reasons, implement it deliberately and verify hydration/server-render implications.

---

# 10. PAGE HEADERS / ACTIONS

For every responsive page header verify:

```text
title
description/metadata
primary action
secondary actions
back navigation
status
filters
bulk actions

```

At narrow widths:

- actions must remain discoverable;
- primary action must not disappear;
- dangerous actions must not become easier to trigger accidentally;
- long titles must wrap safely;
- action groups must not create page overflow.

Use an overflow/action menu only when consistent with the Design System and business importance.

---

# 11. TABLES / DATA-HEAVY SCREENS

Recruitment is data-heavy.

Do not solve mobile tables by blindly hiding columns.

For each table classify columns as:

```text
identity-critical
workflow-critical
status-critical
action-critical
secondary metadata
optional/detail-only

```

Then derive the mobile representation.

Allowed patterns, only when appropriate:

```text
horizontal table scroll
priority-column reduction
row detail expansion
mobile summary row
mobile list/card representation
responsive action menu

```

The mobile representation must preserve access to all business-critical information and actions.

If desktop and mobile use separate markup, ensure:

- logic is not duplicated unnecessarily;
- IDs are not duplicated;
- inaccessible hidden controls are not exposed;
- test selectors remain intentional;
- both render paths cannot cause duplicate side effects.

Before changing a shared table component, use GitNexus impact analysis.

---

# 12. FORMS

Audit all Recruitment forms for:

```text
1-column mobile layout
multi-column desktop layout
label association
required indicators
help text
validation errors
date/time inputs
select/combobox
long option labels
file upload
textarea
button placement
sticky footer/action area
keyboard behavior
mobile scrolling
focus-on-error

```

Do not reorder fields in a way that changes business meaning unless the Design System/spec explicitly allows it.

Do not use placeholder text as a substitute for labels.

---

# 13. DIALOGS / DRAWERS / OVERLAYS

For narrow mobile viewports verify:

```text
max height
viewport units
internal scrolling
header visibility
footer/action visibility
focus trap
initial focus
Escape
close button
focus restoration
background scroll lock
keyboard overlap
destructive confirmations

```

A desktop modal may become a mobile drawer/full-screen dialog only when that behavior fits the current Design System.

Do not redesign every dialog automatically.

---

# 14. RECRUITMENT WORKFLOW SAFETY

Responsive changes must NOT change:

```text
candidate/application identity
permissions
role checks
workflow state
status derivation
commands
server mutations
validation
document semantics
interviewer permissions
selection rules
bulk-action semantics
security behavior
database behavior

```

If responsive code currently duplicates business logic between mobile and desktop, refactor toward one underlying business/action implementation with multiple presentation surfaces.

Do not create:

```text
desktop business logic
+
mobile business logic

```

for the same workflow.

Presentation may differ.

Business behavior must remain shared.

---

# 15. ACCESSIBILITY REQUIREMENTS

Use the ECC `accessibility` skill during implementation.

Verify:

```text
semantic controls
accessible names
form labels
error association
focus visibility
focus order
keyboard operation
Escape behavior
dialog/drawer focus
minimum usable pointer targets
non-color-only status meaning
zoom/reflow
screen-reader landmarks
icon-only button labels
aria-expanded / aria-controls where applicable
live updates where applicable

```

Use native HTML semantics before ARIA whenever possible.

Do not declare the app “accessible” merely because axe reports zero violations.

---

# 16. REPRESENTATIVE VIEWPORT VERIFICATION

First use breakpoints defined by the Recruitment Design System.

If the project does not define concrete QA viewport sizes, verify representative widths including approximately:

```text
360px
390px
430px
768px
1024px
current desktop reference width

```

Test height-sensitive UI as well, not width only.

Verify both portrait mobile and at least one constrained-height scenario for overlays/sticky regions.

Do not optimize only for one iPhone-sized screenshot.

---

# 17. BROWSER-QA — REQUIRED

After each meaningful responsive family is implemented, use:

```text
browser-qa

```

from:

```text
affaan-m/ECC/skills/browser-qa/

```

Use the repository's existing browser automation environment where available.

Test only a safe local/development/preview environment.

Do not run destructive or mutating Recruitment workflows against production.

For each relevant page verify:

```text
page loads
no unexpected horizontal page overflow
no clipped controls
no overlapping layers
navigation usable
forms usable
dialogs usable
actions reachable
scroll regions usable
keyboard/focus behavior
console errors
network failures
responsive breakpoint behavior

```

Capture concrete evidence.

Do not report PASS from static source review alone.

---

# 18. REACT TESTING

For responsive components with behavior, use ECC:

```text
react-testing

```

Focus on observable behaviors.

Examples:

```text
drawer opens/closes
focus returns to trigger
mobile filter state persists
action menu exposes correct commands
dialog closes correctly
form errors remain reachable
responsive selection works

```

Do not test CSS layout through JSDOM if the behavior requires an actual browser layout engine.

Use browser/E2E for actual layout/overflow/responsive assertions.

---

# 19. FINAL FRONTEND AUDIT

After the responsive/mobile implementation is substantially complete, run:

```text
frontend-checklist-global

```

Source:

```text
thedaviddias/Front-End-Checklist

```

This is a FINAL audit layer.

Do not use the global checklist as permission to refactor unrelated Recruitment code.

Classify findings:

```text
BLOCKER
HIGH
MEDIUM
LOW
OUT_OF_SCOPE
CONFLICTS_WITH_PROJECT_AUTHORITY

```

Project authority wins over generic checklist advice.

---

# 20. FINAL CODE REVIEW

Use:

```text
code-review

```

from the currently installed/retrieved Matt Pocock skill source.

Review specifically for:

```text
desktop regressions
duplicate render paths
duplicated business logic
unnecessary viewport JS
hydration risks
accessibility failures
shared-component blast radius
CSS specificity problems
page-specific hacks
boolean-prop explosion
unnecessary abstractions
unrelated changes

```

If responsive work created significant component architecture complexity, additionally run the project's complexity/overengineering review skill if installed.

---

# 21. VERIFICATION-BEFORE-COMPLETION

Use:

```text
verification-before-completion

```

from:

```text
obra/superpowers

```

Do not say:

```text
done
responsive complete
mobile complete
all pages fixed
ready
pass

```

without fresh evidence.

---

# 22. USER VISUAL ACCEPTANCE GATE

Do not finalize the entire responsive/mobile redesign solely from automated checks.

For major page/component families use:

```text
implement
→ technical verification
→ browser QA
→ provide preview
→ user visual review
→ apply approved corrections
→ regression verification

```

User-approved detailed design decisions become project authority.

Do not repeatedly reinterpret an approved visual correction.

If the repository has a canonical Design System/change log, record the approved responsive rule at the correct shared/page level rather than creating unexplained CSS exceptions.

---

# 23. DO NOT DO THESE THINGS

Do NOT:

```text
blindly delete all current responsive work
redesign the entire visual identity
replace the current Design System
change business behavior
change permissions
change workflow states
change database schema for responsive reasons
add a second mobile business workflow
hide required data/actions just to fit mobile
reduce font size excessively
convert every table to cards
introduce viewport-JS when CSS is enough
duplicate mobile/desktop action logic
create dozens of one-off breakpoints
add arbitrary pixel values without a design reason
bulk-format unrelated files
upgrade framework/dependencies for this task
install an entire skill catalog
introduce Graphify or Code Review Graph
make unrelated refactors
push/merge/deploy without authorization
touch production data

```

---

# 24. IMPLEMENTATION ORDER

Do not attack pages randomly.

Use this order unless current source dependencies prove another order is better:

```text
A. Audit + responsive contract

B. Shared responsive foundations

C. App shell/navigation

D. Shared page headers/toolbars/filters

E. Shared form/layout primitives

F. Shared tables/list/data presentation

G. Shared dialog/drawer/action patterns

H. Individual page families

I. Interactive responsive behaviors

J. Browser QA + accessibility

K. Regression against desktop

L. Final frontend checklist

M. Code review

N. Verification-before-completion

O. User visual acceptance / final polish

```

Within each group, use GitNexus to identify actual consumers before modifying shared code.

---

# 25. DO NOT TRY TO COMPLETE THE WHOLE APPLICATION IN ONE UNREVIEWED GIANT DIFF

Work by coherent responsive families.

Recommended checkpoint pattern:

```text
Foundation
→ verify

Shell/navigation
→ verify

Tables/list family
→ verify

Forms
→ verify

Dialogs/drawers
→ verify

Page families
→ verify

Final full regression

```

Keep each diff understandable.

If Orca parallelism is used, separate worktrees by clearly non-overlapping ownership.

Never allow two writing agents to modify the same shared responsive foundation concurrently.

---

# 26. REQUIRED REPORT BEFORE IMPLEMENTATION

Before making the first substantial rebuild, return:

```markdown
# Recruitment Responsive Rebuild — Discovery

## Repository
- root:
- branch:
- commit:
- dirty state:

## Source authorities
- current handover/spec:
- current Design System:
- current responsive/mobile specification:
- relevant current decisions:

## Existing responsive implementation
- shared foundations:
- page-specific code:
- responsive components:
- current breakpoints:
- current testing:
- current browser QA:

## Skills
- karpathy-guidelines:
- Vercel React best-practices:
- accessibility:
- composition patterns:
- react-testing:
- browser-qa:
- diagnosing-bugs:
- tdd:
- code-review:
- frontend-checklist-global:
- verification-before-completion:

## GitNexus
- available:
- index current:
- major shared responsive consumers identified:

## Audit classification
| Area | KEEP | ADAPT | REBUILD | REMOVE | Reason |

## Proposed responsive architecture
...

## Implementation order
...

## Risks
...

```

After this discovery, proceed with implementation unless there is a genuine blocker that makes safe implementation impossible.

Do not ask broad design questions that can be answered from the repository, source, Design System or current approved implementation.

---

# 27. REQUIRED FINAL REPORT

At completion return:

```markdown
# Recruitment Responsive/Mobile Rebuild

## Source authorities followed
...

## Skills actually used
...

## GitNexus impact analysis
...

## Kept from old responsive implementation
...

## Rebuilt
...

## Removed
...

## Shared components changed
...

## Pages/families verified
...

## Viewports verified
...

## Accessibility
- keyboard:
- focus:
- touch targets:
- labels/errors:
- axe/browser findings:

## Browser QA
- environment:
- scenarios:
- console:
- network:
- overflow:
- screenshots/evidence:

## React tests
...

## Front-End Checklist
...

## Code review
...

## Desktop regression verification
...

## Remaining issues
...

## User visual acceptance
- READY FOR USER REVIEW / APPROVED / BLOCKED

## Git state
- branch:
- commit:
- uncommitted diff:
- push/deploy status:

```

Completion means the responsive/mobile experience has been verified against the CURRENT Recruitment source and Design System.

It does NOT mean generic mobile best practices were applied indiscriminately.