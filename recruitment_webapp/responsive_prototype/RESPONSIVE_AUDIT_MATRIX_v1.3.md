# Responsive Audit Matrix — v1.3

| Area | Current implementation | Contract | Decision | Change |
|---|---|---|---|---|
| App shell | Desktop sidebar; off-canvas below 1280 | Desktop-first internal app; off-canvas tablet/mobile | ADAPT | add inert/aria-hidden, focus management, Escape, restore |
| Candidate navigation | Same off-canvas shell | Candidate mobile-ready | ADAPT | preserve language and add mobile sign-out access |
| Page title | Wraps after v1.2 correction | no clipped VI/EN strings | KEEP | retain wrap rules |
| Language switch | hidden in Candidate header <=390 | always reachable in header/menu | ADAPT | no longer hidden; narrow layout stacks only when required |
| Toolbars | scroll/wrap | primary/action access remains discoverable | KEEP/ADAPT | normalize 44px touch target for compact filter control |
| Candidate form | one-column phone | single-page business form; one-column mobile | KEEP/ADAPT | label association + privacy error focus + safe scroll padding |
| File upload | touch-friendly tiles | max 5/current CV/security rule visible | KEEP | no business change |
| Candidate list | mobile cards | compact structured list appropriate to narrow width | KEEP | generated from same submission array |
| HR tables phone | CSS structured rows | per-page structured rows allowed; never hide critical data/actions | KEEP | preserve all columns through labelled rows |
| HR tables tablet | semantic table + horizontal scroll | intentional wide-table exception | KEEP | keyboard-reachable scroll container |
| Sticky context columns | desktop/tablet | Select + identity sticky | KEEP | focus ring preserved |
| Drawer | full-screen on phone; bounded on tablet | full-screen sheet allowed mobile | ADAPT | dialog semantics/focus trap/Escape/restore/background inert |
| Modal/filter | bottom sheet on phone | sheet/dialog allowed | ADAPT | same overlay contract as Drawer |
| Toast | visual only | async feedback accessible | ADAPT | role=status + aria-live |
| Motion | animation present | reduced motion respected | ADAPT | add prefers-reduced-motion |
| Icon buttons | mixed accessible labels | icon-only controls need names | ADAPT | post-render accessible-name normalization |
| Mobile sign-out | topbar hidden | action must remain reachable | ADAPT | place sign-out control in sidebar footer on narrow layouts |
| Width JS | none for presentation | CSS preferred | KEEP | only JS behavior checks viewport for accessibility state, not business rendering |
