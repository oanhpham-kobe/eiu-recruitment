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
