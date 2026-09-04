# 76. Dependency Baseline Policy — v1.8

**Status: CURRENT policy; exact versions are recorded at implementation scaffold time, not guessed in long-lived spec.**

At implementation scaffold, create/review `package.json` and record exact reviewed/patched versions for Node, Next.js, React, `@supabase/supabase-js`, `@supabase/ssr`, package manager/lockfile, test runner, Playwright, upload/scanner packages, and provider SDKs. Pin versions + commit lockfile; record advisory/source review date; rerun Auth/RLS/upload/email regression on security-sensitive upgrades. Historical review version numbers must not become long-lived dependency pins.
