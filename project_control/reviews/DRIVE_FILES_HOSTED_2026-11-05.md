# Private Drive files and development deployment

Owner-authorized extension CR-DRIVE-FILES-HOSTED-20261105. Branch:
`codex/drive-files-hosted-deployment-20261105`, base `d88deffd2d64749ebc3c0c26d48e25eb50bef9e2`.
Code completion precedes Google Cloud configuration guidance, per Owner's latest instruction.

## Reviewed database boundary

Exact candidate `f2c8e03b266ea781723f449f6aeab0beb44668dc`: independent read-only
Codex review PASS, not formal OMP acceptance or hosted-runtime acceptance.
Candidate438eb82 initially failed review: the Drive read took a User advisory
lock before its audit actor FK needed the User row, opposing User lifecycle's
row-before-advisory order. The real read/lifecycle race reproduced a deadlock.
The repaired function locks the actor row first and rechecks identity, active
state and permission after waiting. Both real commands then commit.

Fresh parent actual-role SQL and all six synchronized races passed: competing
bind, cancellation, expiry, Supabase signed issuance, Storage insertion, and
read/audit versus User lifecycle. Worker clean replay of52 migrations passed
before the one-line lock repair; repaired function syntax/application and tests
passed afterward. Existing scan/cleanup SQL passed. Source515/515, generated
source equality, manifest567 checks and CRLF-aware diff check passed.
Both new test gates are wired into Integration CI. The race harness verifies
the explicit disposable project/container identity and Supabase Docker label.
An unintended local project is refused before database access. Final CI pending.

The additive migration preserves logical bucket/path and immutable versions.
Private permanent Drive bindings, narrow worker roles, upload fencing/sealing,
current contextual read/audit, exact scan and cleanup resolution are implemented.
No CLEAN verdict, OAuth credential or resumable capability is fabricated.
Supabase remains default. Runtime adapters and browser integration are pending.

## UI boundary

Reviewed `4e52a50ed9ef03ef68ac930e85bc747f5a38c35a` adds shared accessible
preview/download icons to the existing Inbox document actions. Parent17 focused
tests and independent read-only review passed. PDF/images alone show preview;
all currently allowed formats retain download. Candidate/interview access was
not invented. Runtime attachment handling remains the next implementation phase.

## Hosted preparation, verified

- Oanh's HR Recruitment Cloudflare and Supabase links are explicitly selected;
  Vercel identity also verified. No Primary switch or Bao disconnection needed.
- Owner completed CLI login privately; project list shows the intended EIU
  Recruitment dev project. Hosted Supabase is ACTIVE_HEALTHY, Singapore.
- Existing foundation extensions, private privileges and helper definition/grants
  match repository migration20260904164112. Immutable4e52a50 bundle dry-run
  reports50 pending migrations in original order. No hosted migration applied;
  do not use MCP-generated timestamps for this historical migration chain.
- Vercel staging deployment `dpl_AmSWuMhGz3RWQ3dvNvjVbTxpsFhW` at
  https://eiu-recruitment-54l62k9cy-kobe17.vercel.app/login returns200.
  Git source is4e52a50. It is not a functioning provider-integrated system.
- First deployment `dpl_7VSfUpXyK8QtXbwqXo4VgCu4wAxk` was automatically
  assigned production despite omitted target, and failed at runtime for missing
  environment. A repeated implicit-target action was rejected by automatic
  approval review; explicit API `preview` is invalid, and explicit `staging`
  succeeded. Use explicit staging on subsequent builds; preserve protection.
- Public Supabase URL/key configured only for preview/development. No runtime
  private credentials configured. Google Auth is currently disabled.
- Vercel region update `functionDefaultRegions: [sin1]` accepted; existing build
  remainsiad1. Final deployment must explicitly set and verify Singapore.
- Cloudflare account workers.dev subdomain created; no Worker deployed yet.
- Owner's HR Recruitment folder under Webapp (a Bảo) verified by metadata.
  No sharing change or real document upload. Folder identity stays runtime-only.

## Remaining work and boundaries

Finish authenticated byte gateway, exact-byte hash verification, server ports,
browser Blob upload/read handling, real-scanner adapter and fenced cleanup.
Then verify/review the complete code, sync GitHub and deploy reviewed development
resources. Only afterward guide Google Cloud setup, as Owner requested.
Runtime credentials, scanner and operational Root bootstrap remain prerequisites
for real hosted end-to-end verification. Plugin credentials are not runtime auth.
Package009 remains NOT ACCEPTED/NOT INTEGRATED; historical checkpoints and other
source holds remain. No main merge or production-ready declaration.
