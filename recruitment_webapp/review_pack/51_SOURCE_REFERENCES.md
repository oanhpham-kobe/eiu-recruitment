# 51. Source References Used for Technical / Design Audit

**Reviewed:** 02/09/2026

These references inform implementation guardrails. They do not override frozen EIU business decisions.

## Product / Design references
- EIU MedLabs repository: `https://github.com/baonguyen1301/eiu-medlabs`
- UI/UX Pro Max Skill: `https://github.com/nextlevelbuilder/ui-ux-pro-max-skill`
- Vercel Agent Skills: `https://github.com/vercel-labs/agent-skills`
  - React Best Practices
  - Web Design Guidelines

## Platform references
- Supabase monorepo: `https://github.com/supabase/supabase`
- Supabase Row Level Security docs: `https://supabase.com/docs/guides/database/postgres/row-level-security`
- Supabase Tables/View security docs: `https://supabase.com/docs/guides/database/tables`
- Supabase SSR/Auth server package guidance: `https://supabase.com/docs/guides/auth/choosing-a-server-package`
- Supabase Next.js SSR client guidance: `https://supabase.com/docs/guides/auth/server-side/creating-a-client`
- Supabase Storage buckets/private access: `https://supabase.com/docs/guides/storage/buckets/fundamentals`
- Supabase Storage downloads/signed URLs: `https://supabase.com/docs/guides/storage/serving/downloads`
- Supabase Auth rate limits: `https://supabase.com/docs/guides/auth/rate-limits`
- Supabase Database Backups: `https://supabase.com/docs/guides/platform/backups`
- Supabase Production Checklist: `https://supabase.com/docs/guides/deployment/going-into-prod`

## Next.js / Vercel platform references
- Next.js Authentication / Authorization guide: `https://nextjs.org/docs/app/guides/authentication`
- Next.js Production Checklist: `https://nextjs.org/docs/app/guides/production-checklist`
- Vercel Environments: `https://vercel.com/docs/deployments/environments`
- Vercel Environment Variables: `https://vercel.com/docs/environment-variables`
- Vercel Deployment Protection: `https://vercel.com/docs/deployment-protection`

## Preview-branch risk note
An open Supabase GitHub issue reported preview branches not preserving some object privileges and `auth.users` triggers at the time of review:
- `https://github.com/supabase/supabase/issues/49426`

This is treated as a **risk signal, not a platform guarantee**. Therefore final UAT uses persistent isolated staging and CI verifies grants/RLS/triggers explicitly.
