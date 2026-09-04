# 16. AI Review & Build Prompt — CURRENT v1.17

Use only CURRENT normative sources from `source_registry.yaml`. HISTORICAL/SUPERSEDED review/gate files are evidence only. HISTORICAL files must never override current behavior.

## Review mode
Baseline: Business Logic v1.2 FROZEN, Design System v1.8 CURRENT, Technical Architecture v1.17 TECHNICAL SPECIFICATION FROZEN, Implementation Gate READY TO IMPLEMENT. Read core modules 01–14, current technical modules listed in `source_registry.yaml`, `73_DOMAIN_GLOSSARY_AND_CANONICAL_PREDICATES.md`, `97_INDEPENDENT_REVIEW_IMPLEMENTATION_ALIGNMENT_V1_17.md`, `78_PRIVACY_NOTICE_PUBLICATION_RUNBOOK.md`, and `98_TECHNICAL_PRECODE_GATE_V1_17.md`. Then inspect `app_spec.yaml`, `command_registry.yaml`, `database_schema.sql`, `validation_contract.yaml`, permissions/status matrices and Design System v1.8.
Current alignment resolution: `97_INDEPENDENT_REVIEW_IMPLEMENTATION_ALIGNMENT_V1_17.md`; current pre-code/implementation authorization gate: `98_TECHNICAL_PRECODE_GATE_V1_17.md`. Historical modules must never override current behavior.

Check cross-layer traceability: Actor → Permission → UI → exactly one trusted mutation command → lock/version/transaction → DB invariant → side effects → audit → behavior-specific acceptance. Flag contradiction rather than resolving it by guessing.

## Build mode
Do not invent business features. Browser code must not orchestrate multi-write business transactions or receive service secrets. Server Actions/Route Handlers/RPCs re-authenticate/re-authorize. Use RLS + explicit grants, private Storage, candidate Form Session staged files, immutable document versions, canonical interview predicates, outbox email semantics, and current Design System v1.8.

Prototype/demo persona switcher is development-only and cannot authorize production data. Official PDF layout remains deferred until owner supplies template.

Normal scheduling/resource integrity uses every `resource_blocking` Interview, **not only Current Round**. Only parent Application Reactivate uses `reactivation_conflict_relevant = resource_blocking AND end_at > transaction_now` so fully elapsed past-only overlaps do not strand lifecycle recovery. Current Round is for report/outcome/PDF selection.
