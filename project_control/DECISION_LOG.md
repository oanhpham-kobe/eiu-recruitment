# Implementation Decision Log — Bootstrap

## IMP-DEC-001 — Persistent execution state
Date: 2026-09-03  
Context: Multi-session/multi-agent implementation continuity.  
Decision: Adopt repository `/project_control/` No-Handoff Continuity protocol.  
Why source behavior is preserved: It records implementation progress/evidence only and cannot redefine EIU business/security rules.
Affected: Slice00 onward.

## IMP-DEC-002 — Dependency versions deferred to execution lookup
Date: 2026-09-03  
Context: Version-sensitive framework mechanics.  
Decision: Choose exact supported/patched versions from current official documentation during Slice00 and pin with lockfile/evidence.  
Why source behavior is preserved: External docs choose mechanics only, never EIU business behavior.

## IMP-DEC-003 — Application root established at web/
Date: 2026-09-04
Context: TASK-S00-002 requires an isolated production application root.
Decision: Set APPLICATION_ROOT = web/.
Why source behavior is preserved: Isolates deployable application code from source authority (`recruitment_webapp/`) and project control without introducing monorepo overhead; compatible with Vercel Project Root Directory.
Affected: All application implementation slices.

## IMP-DEC-004 — Acceptance runtime baseline Node 24.20.0 LTS and npm 11.19.0
Date: 2026-09-04
Context: TASK-S00-002 runtime selection.
Decision: Pin acceptance runtime to Node.js 24.20.0 LTS and npm 11.19.0 via isolated official portable runtime (verified SHA-256: `6cac9ffbca8f6a47091e4b5c772e0606049c3871cb67d900c0cedde630e545ba`) without mutating machine-wide Node/npm installations. Set `web/.nvmrc = 24.20.0`, `packageManager = npm@11.19.0`, and `engines.node = 24.x`.
Why source behavior is preserved: Provides deterministic runtime and reproducible builds via `npm ci`.
Affected: TASK-S00-002 and subsequent implementation tasks.

## IMP-DEC-005 — Linter selection and ESLint 9 rejection (Biome selected on expected path)
Date: 2026-09-04
Context: ESLint 9 is EOL since 2026-08-06 and not approved.
Decision: Use official Next.js supported Biome (`@biomejs/biome`) on the Planner-approved path; reject ESLint 9, `--force`, `--legacy-peer-deps`, and peer overrides.
Why source behavior is preserved: Preserves clean dependency resolution and zero unsupported transitive peer issues.
Affected: web/ application tooling.

## IMP-DEC-006 — Supabase DEV infrastructure and region selection
Date: 2026-09-04
Context: TASK-S00-003 requires dedicated DEV-only Supabase infrastructure under explicit owner authorization.
Decision: Provisioned dedicated Supabase DEV project `eiu-recruitment-dev` (remote ref: `yrjclhdvjlekwvfeczcj`) under organization `EIU Recruitment` (`clfvovtyobekjaevdewe`) in region `ap-southeast-1` (Singapore, the nearest officially supported Southeast Asia region for Vietnam). Pinned PostgreSQL 17 engine. Linked repository worktree via `supabase link --project-ref yrjclhdvjlekwvfeczcj`, maintaining explicit distinction between local configuration `project_id = "eiu-recruitment-dev"` (`supabase/config.toml`) and remote project reference `yrjclhdvjlekwvfeczcj`. Verified plan status as `NOT_OBSERVABLE` (default non-production tier; zero paid upgrade performed). Stored all non-production database credentials in gitignored `web/.env.local` and `.env.local`. Zero secrets committed.
Why source behavior is preserved: Satisfies non-production DEV provisioning requirements without modifying production or introducing unapproved paid tiers.
Affected: Database development, migrations, and local verification.

## IMP-DEC-007 — Migration foundation, schema isolation, and Vercel project linking
Date: 2026-09-04
Context: TASK-S00-003 requires reproducible migration foundation, strict schema boundaries, and Vercel project linking without deployment.
Decision: Established migration foundation `20260904164112_initial_foundation.sql` establishing reviewed extensions (`pgcrypto`, `citext`, `pg_trgm`, `unaccent`) under `extensions` schema, created `private` internal schema with strict revokes from `public`, `anon`, and `authenticated`, and implemented `private.touch_version()` trigger function with `SECURITY DEFINER` and empty `search_path`. Created and linked Vercel project `eiu-recruitment` (`prj_9t5t1RBtgZp4hOLuSgEYgv5nt8qY`) with root directory `web` and framework `nextjs`. Held all preview/production deployments as `NOT_PERFORMED` per explicit owner authorization.
Why source behavior is preserved: Conforms to `review_pack/database_schema.sql`, `review_pack/40_DATABASE_INVARIANTS.md`, and `review_pack/59_RLS_POLICY_BLUEPRINT.md`.
Affected: All database migrations, schema boundaries, and Vercel deployment infrastructure.
