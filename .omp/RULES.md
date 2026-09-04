# EIU Recruitment — Sticky Rules

1. The **current canonical project sources** always outrank memory, old plans, old docs, generic skills, and examples.
2. Authentication is not authorization. Enforce application permissions server-side.
3. Never weaken RLS, grants, validation, concurrency/locking, idempotency, privacy, private Storage, or accessibility requirements for convenience.
4. Never expose service-role keys, Google Client Secret, session/refresh tokens, OTPs, signed private URLs, or other secrets.
5. Supabase MCP must default to a non-production project, project-scoped and read-only. Never use AI-driven production DB writes without explicit authorization.
6. Never let multiple writing agents concurrently modify the same worktree.
7. Do not commit, push, merge, production-deploy, apply destructive live migrations, or delete production data unless explicitly authorized.
8. Do not claim `done`, `fixed`, `pass`, or `ready` without fresh verification evidence.
9. External skills/tools are advisory implementation aids, never a second business/design Source of Truth.
10. After accepted setup, keep GitNexus MCP available as the default graph/impact engine; use it selectively for cross-module/shared/high-risk work, not mechanically for trivial edits.
