# External Prompt Audit — TASK-S07-005 R2 Baseline

- **WORK_ID**: `S07-005-EXTERNAL-PROMPT-AUDIT-001`
- **AUDITOR_ROLE**: `EXTERNAL_CHATGPT`
- **AUDITED_REVIEW_BASELINE**: `checkpoint/pre-S07-005-002`
- **AUDITED_REVIEWED_SHA**: `44de446cef58d75507324664f4b36a47c3fc7e5c`
- **R2_REVIEW_WORK_ID**: `S07-005-PROMPT-REVIEW-002`
- **R2_REVIEW_VERDICT**: `PASS` (historical independent review evidence)
- **EXTERNAL_AUDIT_VERDICT**: `BLOCKING_REPAIR`
- **SOURCE_REOPEN_REQUIRED**: `false`
- **IMPLEMENTATION_AUTHORIZED**: `false`

## Scope

This external audit independently rechecked the R2 prompt against the accepted database contracts rather than relying on the prior PASS verdict. The audit verified the immutable R2 checkpoint and its reviewed SHA, re-read the accepted S07-001 email RPCs, and inspected the accepted definition of `private.interview_command_actor(...)` in the Interview lifecycle contracts.

## Blocking finding

### `S07-005-EXTERNAL-AUDIT-001` — Authentication error semantics mismatched accepted RPC behavior

The R2 prompt stated:

> `Unauthenticated callers receive UNAUTHENTICATED; unauthorized callers receive FORBIDDEN.`

That is not the accepted backend contract for the S07-001 email RPCs.

The accepted `private.interview_command_actor(...)` helper returns `NULL` when any of the following holds:

1. `auth.uid()` is null;
2. no active `public.app_users` actor resolves for the authenticated identity;
3. required permission is absent and the caller is not Root Admin.

The accepted S07-001 RPCs then fail closed as follows:

- `public.preview_email(...)`: null actor -> `FORBIDDEN`;
- `public.enqueue_email(...)`: null actor -> `FORBIDDEN`;
- `public.bulk_enqueue_email(...)`: null actor -> `FORBIDDEN`;
- `public.delete_email_history(...)`: null actor or missing required history-view authorization -> `FORBIDDEN`.

Therefore these accepted RPCs do **not** expose a distinct `UNAUTHENTICATED` response for missing `auth.uid()`.

A server action or UI may independently detect that no user session exists and present authentication/login UX, but that adapter behavior must not be documented as the trusted RPC error contract.

## Why this is blocking

TASK-S07-005 is explicitly a pure consumer of accepted S07-001 contracts. Its implementation prompt must not instruct adapters/tests to assert an error code that the accepted RPC layer does not return. Doing so would either create incorrect tests or encourage adapter logic to rewrite backend authorization semantics without an explicit product contract.

## Repair performed

`project_control/prompts/SLICE-07_TASK-005_v1.md` was repaired after this finding to:

- state the exact fail-closed `FORBIDDEN` semantics;
- distinguish trusted RPC behavior from optional server-action/UI missing-session UX;
- add an adapter test requirement that no synthetic `UNAUTHENTICATED` RPC result is fabricated;
- invalidate `checkpoint/pre-S07-005-002` as the future implementation baseline while preserving it as immutable historical R2 review evidence;
- require a new numbered immutable pre-task checkpoint and a fresh independent exact-SHA prompt/source review before implementation can be dispatched.

## Source reopen decision

`SOURCE_REOPEN_REQUIRED: false`.

The accepted S07-001 implementation is internally consistent. The defect was in TASK-S07-005 prompt wording, not in the accepted email persistence or Interview actor contracts. No accepted migration or predecessor checkpoint should be modified.

## Required next lifecycle step

1. Persist the repaired prompt baseline and this external-audit evidence.
2. Run governance validators locally.
3. Create the next unused immutable annotated pre-task checkpoint (expected `checkpoint/pre-S07-005-003` if still unused) at the exact repaired baseline SHA; never move `-001` or `-002`.
4. Perform a new read-only independent `eiu-reviewer` prompt/source review on that exact peeled checkpoint SHA.
5. If and only if that review is PASS with `SOURCE_REOPEN_REQUIRED: false`, persist R3 PASS governance truth and establish the reviewed checkpoint as the implementation baseline.
6. Implementation remains NOT_STARTED until explicit Owner dispatch.

## Boundary confirmation

- Product implementation changed: **NO**
- Accepted S07-001..S07-004 contracts changed: **NO**
- `main` modified: **NO**
- Vercel deployed: **NO**
- Connected Supabase mutated: **NO**
- Accepted/pre-task checkpoint force-moved: **NO**
- TASK-S07-005 implementation authorized: **NO**
