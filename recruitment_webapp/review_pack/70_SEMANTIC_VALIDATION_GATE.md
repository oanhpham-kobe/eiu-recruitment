# 70. Semantic Cross-layer Validation Gate — v1.17

**Status:** CURRENT / NORMATIVE

The validator must fail on semantic drift, not only missing files or tokens. Current expected package versions are **Technical Architecture v1.17** and **Design System v1.8**.

## Mandatory semantic checks
1. **Source governance:** CURRENT entrypoints point to Alignment Resolution 93, Domain Glossary 73, Privacy Publication Runbook 78, Responsive Integration 81 and Pre-code Gate 94. HISTORICAL/SUPERSEDED modules are excluded from normative All-in-One.
2. **Acceptance traceability:** Acceptance IDs are unique; command acceptance references exist and behavior-specific commands carry required guarantee tags.
3. **One protected mutable field → one command:** `interviews.report_status_code` has exactly one trusted writer (`change_report_status`); `update_hr_report_note` cannot write Report Status.
4. **Outcome side effects:** every Application/current-round/outcome-changing command declares authoritative Submission recalculation where required.
5. **Submission state matrix:** generic no-active-Application recalculation preserves manual NEW/READ; derived states fall to READ; Candidate Reactivation/no-active-Application is the explicit READ exception.
6. **Canonical Interview predicates:** `access_active`, `current_round`, and `resource_blocking` are the normal domain predicates. `reactivation_conflict_relevant` is explicitly **Application Reactivate-only** (`resource_blocking AND end_at > transaction_now`). Interviewer access always includes parent Application active.
7. **Document target integrity:** Candidate and HR REPLACE/DELETE require the target logical document to have exactly one current version at stage/mutation time and again under lock at Save; historical logical targets cannot resurrect or bypass max-five/CV invariants.
8. **Candidate EDIT privacy:** EDIT Form Session pins an authoritative current/effective Privacy Notice and Save records/reuses the exact acknowledgement. Published notice content is immutable; publication switching follows Runbook 78.
9. **Candidate side effects:** Candidate Update notification is enqueued in the same business transaction; file-only changes bump aggregate version; latest-surviving Submission drives current-profile cache.
10. **Email History:** view/delete uses exact permissions plus parent contextual access; cleanup eligibility is deterministic and audited.
11. **Owner lifecycle:** active/reactivated Applications require an eligible Active HR/root owner; HR deactivation/role removal cannot strand active owned Applications.
12. **Application Reactivation:** fully elapsed historical intervals do not block lifecycle recovery; non-elapsed conflict-relevant intervals use the shared conflict engine.
13. **Permission-display scope:** non-root directory managers do not see another user's granular effective permissions.
14. **Report lifecycle:** only canonical active/current or inactive/archived report flag combinations are physically valid.
15. **Application durable identity:** exact Submission+Unit+Team+Position is globally unique; the zero UUID used for NULL-Team indexing is physically reserved and cannot be a real Team key.
16. **Email/malware/upload:** provider delivery is at-least-once; client retry prevents duplicate logical enqueue only; malware CLEAN and frozen Phase-1 whitelist/5 MB/max-five rules are mandatory.
17. **Delete lifecycle:** unused hard-delete capabilities map to exact permissions or explicit MAINTENANCE_ONLY paths; empty auto Round 1 exception is consistent.
18. **Current-source consolidation:** CURRENT/NORMATIVE modules state canonical behavior in place and do not rely on later versioned clarification blocks to override earlier text.
19. **Version coherence:** schema/design/current status headers match Technical v1.17 / Design v1.8 / Responsive Prototype v1.10.
20. **Batch selection entity coherence:** Application Inbox checkbox entity = Candidate; `bulk_set_latest_submission_manual_status` accepts Candidate IDs, resolves deterministic latest Submission under lock, revalidates expected latest IDs/versions, and is the only active batch writer for manual NEW/READ.
21. **Candidate lifecycle separation:** Candidate Inactive never appears in the Submission status enum or writes `INACTIVE` to Submission; parent Candidate summary derives latest Submission state.
22. **Phase-1 navigation:** rendered persona routes are a subset of the frozen Phase-1 navigation registry; `FUTURE_HIDDEN / NOT_RENDERED` routes are absent from ordinary UAT navigation.
23. **Report decision/source semantics:** Report Status writes Current Interview only; qualitative-only report edits do not move `decisionUpdatedAt` or Final Decision Source; aggregate HR Report drawer has no generic Delete.
24. **Candidate CV/edit semantics:** CV remains required after staged ADD/REPLACE/DELETE; Cancel discards staged changes; Save revalidates editability before atomic materialization.
25. **Critical controls:** critical production-intent controls require a declared expected transition/navigation/dialog and cannot PASS solely on generic toast fallback.
26. **Generated artifact equality:** `15_ALL_IN_ONE_SPEC.md` regenerates byte-for-byte from CURRENT/NORMATIVE numbered modules only.

PASS proves specification consistency against implemented checks only. It does **not** prove executable migrations/RLS, real race behavior, provider integrations, security configuration, backup/restore, rendered UI, accessibility or production readiness.
21. **Forbidden legacy canonical patterns:** CURRENT/NORMATIVE source must not contain the legacy Application-Reactivate rule `re-checks every child that would become resource-blocking`; canonical behavior is non-elapsed `reactivation_conflict_relevant` only.
22. **Nullable master-reference parity:** optional Education `qualification_id=NULL` must bypass active-master validation; changed non-null references still require an Active master.
23. **Bulk schedule operational parity:** single and bulk schedule-status writers share Active-current-Participant eligibility plus Candidate/Room/Interviewer conflict recheck.
24. **Current baseline coherence:** machine current-baseline blocks and current README/VERSION authority must resolve to Full/Technical v1.17 + Design v1.8 + Responsive v1.10.

25. **Critical-control executable parity:** single and bulk Interview Schedule Status critical controls must map to Responsive browser QA and share operational guards.
26. **Interview upload delete integrity:** `upload_reservations.interview_id` is FK RESTRICT; hard-delete requires durable `storage_cleanup_queue` capture before reservation removal.
27. **Bulk Candidate lifecycle parity:** machine registry declares inactive metadata, per-Submission reactivation recalculation and per-item/batch audit.
28. **Forbidden stale current path:** CURRENT/NORMATIVE docs must not advertise Review 89/Gate 90 or v1.12 as the current implementation-contract package.

25. **Gate sequencing:** CURRENT source must distinguish pre-code Technical Specification Freeze from post-code Implementation Validation/Migration Freeze; forbidden current wording may not require the same implementation evidence both before and after Technical Freeze.
26. **Copy command authority:** `copy_interview_schedule` must exist in command registry/coverage/contract and client Copy draft must be explicitly non-mutating.


## Additional fail-closed checks for current Copy evidence
- **Copy schedule-engine propagation:** `copy_interview_schedule` must exist in Registry/contract/coverage **and** in `app_spec.schedule_conflicts.engine_used_by` plus the current Concurrency shared-engine declaration.
- **Critical Copy QA resolvability:** every `critical_control_registry.INTERVIEW-COPY-SAVE.browser_qa` stable ID must resolve to current Responsive Browser QA evidence.
- **Used-target Copy branch:** current QA must prove used target Round1 → next legal round.
- **Generated-label coherence:** generated All-in-One header/generator/validator labels must equal current Full Handover version.
