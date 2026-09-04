---
name: eiu-code-review
description: "Authoritative EIU code review skill enforcing REVIEW.md contract, graph intelligence routing (CRG broad triage, GitNexus precise impact), direct source verification, and database authority."
---

# EIU Code Review — Native Review Contract (v2.4)

## Purpose & Scope
Conduct systematic, evidence-grounded code reviews against the EIU Recruitment specification, `REVIEW.md`, and project contracts.

This skill is strictly read-only:
- NEVER automatically edit code.
- NEVER automatically commit.
- NEVER automatically push.
- NEVER automatically merge.
- NEVER automatically deploy.

## Review Process & Graph Routing Hierarchy

```text
1. Task Contract & Specification Check
        ↓
2. Direct Git Diff & Source Inspection
        ↓
3. Code Review Graph (CRG)
   - Use for broad diff/review triage: detect_changes_tool, get_review_context_tool
   - Identify broad architectural impact and risk zones
        ↓
4. GitNexus
   - Use for highest-risk exact symbol impact: impact, context, trace
   - Verify caller/callee and shared type/function blast radius
        ↓
5. Direct Source & Tests Verification
   - Mandatory source verification of all graph-indicated lines
   - Check declarative schema and ordered migration chain
        ↓
6. Final Review Verdict
   - Evidence-grounded report adhering to REVIEW.md
```

## Mandatory Invariants

### 1. No Graph Auto-Verdict
No graph tool (CRG or GitNexus) may issue the final review verdict automatically. Graph results are navigational and triage evidence only.

### 2. GRAPH_FINDING_NEEDS_SOURCE_CONFIRMATION
Every graph-material finding requires direct source confirmation (`GRAPH_FINDING_NEEDS_SOURCE_CONFIRMATION`). Never cite a graph node or edge without reading and verifying the corresponding source lines.

### 3. DB_EFFECTIVE_DEFINITION_VERIFIED
Database findings (RLS, RPC, functions, triggers, table constraints, migration order) require verification against direct SQL source, declarative schema, and the ordered migration chain before assigning a final defect (`DB_EFFECTIVE_DEFINITION_VERIFIED`). Remote dev inspection provides deployed evidence, not repository authority.

### 4. SQL_ABSENCE_RULE
Never conclude a function, trigger, RPC, or policy "does not exist" solely because CRG or GitNexus returned no match. Always verify against declarative schema, migration chain, and SQL files.
