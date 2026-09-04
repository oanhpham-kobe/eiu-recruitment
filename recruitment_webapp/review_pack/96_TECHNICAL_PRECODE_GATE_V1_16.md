# 96. Technical Pre-code / Implementation Authorization Gate — v1.16

> **HISTORICAL / SUPERSEDED:** retained as v1.16 evidence only. Current authority is v1.17 alignment/gate in `source_registry.yaml`.

**Status:** TECHNICAL SPECIFICATION FROZEN / READY TO IMPLEMENT  
**Date:** 03/09/2026

## Current authority
- Business Logic Core v1.2 = **FROZEN**
- Design System v1.8 = **CURRENT / REVIEWED**
- Technical Architecture v1.16 = **TECHNICAL SPECIFICATION FROZEN**
- Responsive Prototype v1.10 = **READY FOR OWNER VISUAL UAT / NOT FROZEN**
- Implementation Gate = **READY TO IMPLEMENT**
- Production Ready = **NO**

## Canonical gate sequence

### Gate 1 — Technical Specification Freeze — PASS
Purpose: freeze source semantics before production coding.

Required:
- Business/current normative source coherent;
- no blocking `SPEC_CONFLICT` in CURRENT/NORMATIVE authority;
- machine contracts conform to normative source;
- current package/design/prototype validators PASS;
- current review/alignment resolution incorporated.

**Not required at this gate:** production migrations, executable RLS/GRANT evidence, implemented RPCs/commands, race tests against production code, Storage provider integration, query plans against production schema, backup/restore or deployment rollback rehearsal. Those are implementation evidence and belong to Gate 3.

### Gate 2 — Approved for Implementation — PASS at source level
A Coding Executor may implement only from this frozen baseline and an executor prompt that explicitly says execution is authorized. A planner/user workflow may intentionally keep a generated prompt `DRAFT_ONLY_NOT_AUTHORIZED` until an independent review approves the prompt; that workflow hold does not reopen the Technical Specification.

Responsive Prototype v1.10 is an executable visual/interaction reference only. Owner Visual UAT remains required before UI visual sign-off and final Production UAT, but does not block Slice 00 Foundation implementation.

### Gate 3 — Implementation Validation / Migration Freeze — PENDING
After code exists, require evidence including:
- clean migration install from zero;
- executable RLS/GRANT adversarial tests;
- trusted command/RPC integration tests;
- schedule/document/status/batch concurrency and race tests;
- Supabase Storage + malware + cleanup-worker integration;
- FK/index audit and critical `EXPLAIN ANALYZE` evidence against NFR targets;
- dependency/security validation;
- backup/restore rehearsal;
- deployment/rollback rehearsal.

Failure here blocks migration/deployment freeze but does not retroactively redefine Gate 1.

### Gate 4 — Production UAT / Production Ready — PENDING
Requires current Production UAT Gate evidence, Owner Visual UAT/UI acceptance, security/accessibility/operations evidence, recovery evidence and explicit go-live approval.

## Copy Interview authority closure
`copy_interview_schedule` is the single dedicated trusted mutation for **Save Copy**. The pre-save Copy modal/draft is client-only and performs no DB mutation. See command registry, doc 37 and Coverage Matrix 55.

## Executor note
Source-level `READY TO IMPLEMENT` does not mean an already-generated draft Executor prompt is authorized. Prompts remain governed by their own `EXECUTION_STATUS` and must be regenerated/revalidated after baseline changes.
