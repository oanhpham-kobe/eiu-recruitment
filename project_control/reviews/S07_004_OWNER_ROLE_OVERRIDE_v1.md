# TASK-S07-004 Owner Role Override — ChatGPT Producer / OMP Reviewer

WORK_ID: S07-004-OWNER-ROLE-OVERRIDE-001
DATE: 2026-09-16
TASK: TASK-S07-004 — Physical Storage Cleanup Runner and Local Storage Integration
OWNER_DECISION: ACTIVE

## Decision

The Owner reverses the S07-004 implementation review roles from the previously planned arrangement.

For TASK-S07-004 implementation only:

- ChatGPT is the implementation producer/executor.
- OMP / `eiu-reviewer` is the independent implementation reviewer.
- ChatGPT must not self-accept its implementation.
- OMP must review the exact frozen implementation candidate SHA before serialization/acceptance.
- The prior S07-003 task-local reviewer override remains historical and is not rewritten.

## Governed baseline

- Pre-task checkpoint: `checkpoint/pre-S07-004-002`
- Peeled baseline SHA: `9af517c0f83af1c3337f6e7b12dd50595aaea9f0`
- Prompt: `project_control/prompts/SLICE-07_TASK-004_v1.md`
- Prompt review: `S07-004-PROMPT-REVIEW-003` — PASS @ `06f8635da5438424a69e0cff12e91fc2389dfd48`
- Source reopen required: false

Implementation branch:

`chatgpt/TASK-S07-004-physical-storage-cleanup-runner`

## Boundaries

This role change does not expand product scope.

Still prohibited without separate Owner authorization:

- mutation or merge of `main`;
- PR creation/merge;
- Vercel deployment;
- connected/hosted Supabase migration or Storage mutation;
- production secrets/credential provisioning;
- production scheduler/cron/daemon;
- TASK-S07-005 or any sibling task;
- arbitrary Storage listing, prefix sweep, or wildcard deletion.

Physical Storage integration for S07-004 is restricted to disposable local Supabase only.

## Review sequencing

1. ChatGPT implements on the task branch in bounded safe checkpoints.
2. ChatGPT runs the available focused verification for each checkpoint and records limitations truthfully.
3. ChatGPT freezes one exact implementation candidate SHA.
4. ChatGPT stops and returns a copy-ready OMP review handoff.
5. OMP independently reviews the exact candidate and returns PASS or bounded repair findings.
6. Serialization, exact-SHA acceptance CI, accepted checkpoint creation, and next-frontier release remain separately gated.

No implementation acceptance is implied by this override.
