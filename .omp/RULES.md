# EIU Recruitment — OMP Sticky Rules

1. Current canonical project sources outrank memory, old plans, generic skills, examples, and historical task prompts.
2. Authentication is not authorization. Preserve server-side authorization, RLS/grants, validation, locking/concurrency, idempotency, privacy, private Storage, accessibility, and secret boundaries.
3. Supabase MCP defaults to non-production and read-only. Production writes, destructive live operations, deploys, main merges, or other external authorization boundaries require explicit Owner authorization.
4. Never let multiple writing agents concurrently modify the same worktree.
5. The main OMP session owns the visible Todo and task lifecycle. For non-trivial work, initialize and maintain the native Todo before and during implementation. Subagents must not own or recreate the parent Todo.
6. Skills use OMP-native discovery. Prefer project skills under `.agents/skills/<name>/SKILL.md`; use `autoloadSkills` on project agents for deterministic worker specialization and `skill://<name>` for additional on-demand skill reads. Do not manually resolve runtime skill paths through `SKILLS_LOCK.yaml`.
7. A skill is guidance, not project authority. Apply only skills relevant to the delegated work; do not create a second business/design source of truth from skill text.
8. Subagents are bounded workers. They implement, investigate, or review the assigned scope and return evidence to the parent; they do not select the autonomous frontier, integrate branches, or dispatch the next project task unless explicitly delegated by the main session.
9. Do not trust a subagent success claim by itself. The parent verifies the diff/result and obtains fresh evidence before accepting, committing, integrating, or claiming completion.
10. GitNexus is on-demand graph/impact assistance. Direct source, LSP, migrations, schema, SQL, and tests remain authoritative; never call graph tools ceremonially.
11. Autonomous scheduling authority remains `project_control/AUTONOMY_PARALLEL_GOVERNANCE.md` plus `project_control/AUTONOMY_RUN_STATE.yaml`. Durable registry state and OMP session Todo are separate concerns.
12. `execution_mode` is exactly `AUTONOMOUS` or `BOUNDED`. AUTONOMOUS may continue through review/repair/integration/CI/next frontier unless a true stop condition occurs; BOUNDED performs only the explicitly authorized work set and stops.
13. Repair verification is impact-selected: rerun failed/directly affected checks and crossed invariants; keep unrelated prior PASS areas closed unless changed code/dependency/shared-contract evidence reopens them.
14. Candidate-producer self-review is not the independent acceptance review. OMP `eiu-reviewer` is read-only and reviews exact candidate SHAs; a repair SHA requires fresh re-review.
15. OMP main session, not the reviewer, owns GitHub review-artifact persistence, exact-SHA CI/integration decisions, and immutable pre-task/accepted checkpoint refs. Accepted checkpoint requires OMP review SHA == CI SHA == checkpoint SHA.
16. Before context-pressure/session handoff, finish an atomic recoverable checkpoint and refresh durable state/CURRENT_STATE; do not start a new risky phase or hand off half-edited state.
