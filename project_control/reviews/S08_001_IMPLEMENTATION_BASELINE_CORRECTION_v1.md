# TASK-S08-001 — Implementation-Time Baseline Correction

Producer: `EXTERNAL_CHATGPT`

Task: `TASK-S08-001 — Application Inbox Search and Indexed Pagination Hardening`

Prompt authority remains:

- `project_control/prompts/SLICE-08_TASK-001_v2.md`

Pre-task review remains historical evidence:

- `S08-001-PROMPT-REVIEW-001`
- reviewed SHA `141146d52a05b0d698178ba7ef097690d5ef2a27`
- verdict `PASS`

Source reopen required: `false`

## Why this correction exists

During producer implementation self-audit, before any product implementation edit was written, the producer inspected the later accepted migration:

`supabase/migrations/20260906005000_pre_s04_contract_repairs.sql`

Section 11 (`Application Inbox Search & Pagination Alignment`) redefines `public.list_application_inbox` after the migrations emphasized in `S08_001_SOURCE_RECONCILIATION_v2.md`.

The v2 reconciliation and the independent prompt review therefore overstated three accepted-state gaps. This correction records the actual final accepted baseline instead of hiding the discrepancy.

## Correct final accepted baseline

The final PRE-S04 definition already provides:

1. `p_page_size integer default 25`;
2. user-facing DB page-size normalization to `25/50/100`;
3. broad Name search only when `length(btrim(p_query)) >= 2`;
4. Email prefix search using `lower(email) like lower(query) || '%'`;
5. digit-normalized Phone prefix search;
6. Candidate-group pagination, immutable-ID tie-breakers, complete child history, version tokens, active-Application semantics, and accepted RLS/permission authority.

Therefore these are **not** S08-001 implementation gaps by themselves.

## Gaps that remain real

The reviewed task outcome remains coherent and bounded because the final accepted baseline still lacks:

- a Vietnamese accent-insensitive Name normalization strategy aligned to an index;
- an index aligned to the actual authoritative Application Inbox Email predicate (`candidates.email`), rather than the unrelated starter `submissions.email_snapshot` index;
- a Phone prefix index explicitly aligned to the digit-normalized prefix predicate under ordinary collations;
- wildcard-safe treatment of user-supplied `%`, `_`, and escape characters;
- deterministic query classification preventing generic one-character Name scans while allowing Email/Phone shapes;
- web/server-adapter default page size 25 and user-facing 25/50/100 page-size control;
- 300 ms UI debounce;
- S08-specific behavioral/search-index/query-plan regression evidence.

## Implementation consequence

The producer will **harden the final PRE-S04 RPC rather than copy or resurrect an older Slice-03 definition**.

The new forward-only migration must preserve:

- the nine-argument RPC signature;
- Candidate-group pagination;
- complete historical child Submission rows;
- candidate/submission optimistic version tokens;
- current Candidate Email projection;
- active-Application semantics;
- deterministic immutable-ID ordering;
- `submissions.view` / Root Admin authorization and RLS behavior.

The implemented S08-001 contract further canonicalizes page size consistently across DB, server adapter, Server Action, UI, and regressions: only `25`, `50`, or `100` are valid, the default is `25`, and every invalid value (including values below `25`) falls back to `25`.

## Governance classification

This is an implementation-time accepted-baseline correction, not a canonical-source contradiction.

`SOURCE_REOPEN_REQUIRED: false`

The task title, canonical sources, security boundaries, migration boundary, and intended user-facing outcomes do not change. The independent implementation reviewer must explicitly inspect this correction and verify that the candidate is based on the final PRE-S04 RPC rather than an older definition.
