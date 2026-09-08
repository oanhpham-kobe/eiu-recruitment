# Independent Pre-Implementation Prompt & Source-Reconciliation Review — TASK-S05-001

WORK_ID: S05-001-PROMPT-REVIEW-001  
REVIEWED_SHA: 458b3856eafc812d8c8edca0b74c205fbfcd2f43  
TARGET: project_control/prompts/SLICE-05_TASK-001_v1.md  
RESULT: BLOCKING_REPAIR  
SOURCE_REOPEN_REQUIRED: NO  

## Summary
The bounded Interviewer-first vertical slice for TASK-S05-001 is sound, well-motivated, and preserves closed Slice-04 foundations and the ASSET-001 boundary. However, before materialization and dispatch, four blocking prompt gaps must be repaired using already-canonical sources:
1. Specify the normative Interviewer-facing 8-state status projection (hiding HR decision stages under `REPORT_SUBMITTED`).
2. Explicitly permit and bound the required safe contextual read projection/RPC without conflating it with forbidden S04 mutation recreation or granting overly broad HR permissions.
3. Explicitly define Final Decision Source eligibility, qualitative-only update isolation, and fallback semantics.
4. Replace generic viewport/responsive phrases with the normative 6-viewport matrix and bilingual (VI/EN) state preservation requirements.

No source contract reopening or Owner policy decisions are required; all repairs are directly supplied by existing canonical source documents.

## Findings

### F1 (HIGH) — BLOCKING_REPAIR
- **Context:** `Required product behavior / UI requirements / Verification`
- **Finding:** The prompt omits the Interviewer-facing status display contract. The accepted HR Interview read model returns raw `report_status_code`, but canonical rules explicitly define an 8-state Interviewer presentation where `FOLLOW_UP`, `ON_HOLD`, and `HIRED` are masked as `REPORT_SUBMITTED`, while `REJECTED` remains `REJECTED`. Without this, an implementation could pass all prompt criteria while leaking HR-only lifecycle states to Interviewers.
- **Evidence:** `recruitment_webapp/review_pack/06_INTERVIEW_REPORT_HR_AND_INTERVIEWER.md` §5.
- **Repair:** Specify the canonical 8-state Interviewer mapping in the prompt and require bilingual test verification across all eight states while maintaining raw target-round status for write authorization.

### F2 (HIGH) — BLOCKING_REPAIR
- **Context:** `Accepted implementation prerequisites / Preview / Security invariants / Database-change condition`
- **Finding:** The prompt mandates contextual discovery, historical detail access, and shared council report preview, but does not clarify how these reads interface with the existing backend. `loadInterviewPage` requires `interviews.view` (HR-only), and existing report SELECT policies authorize only the individual report author, with the final-source view kept in private schema. Disallowing any database adjustments without a "source contradiction" risks either deadlocking the task or encouraging unauthorized expansion of HR permissions or unsafe client assembly.
- **Evidence:** `supabase/migrations/20260906070000_interview_lifecycle_commands.sql` (`can_view_interview_report`), `web/src/lib/interview/server.ts` (`loadInterviewPage`), `recruitment_webapp/review_pack/39_SECURITY_RLS_MATRIX.md` §§3–5.
- **Repair:** Explicitly authorize a minimal additive contextual read projection/RPC for Slice-05 that safely projects permitted Interview/Application data, own editable report/version, and shared preview content, while strictly excluding HR notes, HR owner identity, and private technical metadata. Clarify that additive read models do not constitute recreating accepted Slice-04 mutations.

### F3 (MEDIUM) — BLOCKING_REPAIR
- **Context:** `Preview / Verification item 6`
- **Finding:** The Final Decision Source rule does not define source eligibility (must be current participant with at least one non-blank decision field), qualitative-only timestamp isolation, or all-clear fallback. Generic "preview semantics" verification could permit an empty or qualitative-only save to incorrectly seize the final decision block.
- **Evidence:** `06_INTERVIEW_REPORT_HR_AND_INTERVIEWER.md` §§9–10, `13_ACCEPTANCE_CRITERIA_AND_TEST_CASES.md` AC-31–AC-35, and `20260906070000_interview_lifecycle_commands.sql` (`interview_final_decision_source`).
- **Repair:** State the exact accepted eligibility criteria, deterministic ordering (`decision_updated_at DESC, interview_report_id DESC`), fallback to prior source when cleared, and whole-block atomic selection.

### F4 (MEDIUM) — BLOCKING_REPAIR
- **Context:** `UI/accessibility/responsive requirements / Verification items 9–10`
- **Finding:** The prompt's generic "representative phone/tablet/desktop" requirement is weaker than the normative Design System matrix, and bilingual requirements are omitted.
- **Evidence:** `recruitment_webapp/design_system/RESPONSIVE.md` (360, 390, 430, 768, 1024, desktop, and constrained-height viewports) and `recruitment_webapp/design_system/I18N.md` §§2–3, 8–9 (VI/EN translation, state preservation during locale switch).
- **Repair:** Mandate the canonical 6-viewport matrix and bilingual (VI/EN) test coverage, ensuring user form drafts and filter state persist across locale switches.

## Area Verdicts
- **TASK_BOUNDARY_VERDICT:** PASS. Clean Interviewer vertical slice; HR aggregate, deletion, and email features correctly deferred.
- **SLICE04_CONTRACT_REUSE_VERDICT:** PASS WITH REQUIRED CLARIFICATION (F2). `save_interviewer_report`, decision triggers, participant lifecycle, and optimistic locking are reusable.
- **INTERVIEWER_ACCESS_VERDICT:** PASS. Access predicates and participant removal revocation are accurate.
- **REPORT_WRITE_AUTHORIZATION_VERDICT:** PASS. Confines writes to own current participant in Current Round with non-final status.
- **REPORT_EDITING_CONCURRENCY_VERDICT:** PASS. Field-aware disjoint merge and stale multi-tab protections preserved.
- **FINAL_DECISION_SOURCE_VERDICT:** BLOCKING_REPAIR (F3). Requires explicit eligibility, isolation, and fallback definitions.
- **STATUS_VISIBILITY_VERDICT:** BLOCKING_REPAIR (F1). Missing Interviewer 8-state presentation mapping.
- **DESIGN_RESPONSIVE_ACCESSIBILITY_VERDICT:** BLOCKING_REPAIR (F4). Viewports and bilingual coverage must match Design System v1.8.
- **PDF_ASSET_BOUNDARY_VERDICT:** PASS. ASSET-001 correctly deferred; no speculative layout invented.
- **BACKEND_SCOPE_VERDICT:** BLOCKING_REPAIR (F2). Explicitly authorize safe additive read models while prohibiting mutation recreation.
- **SECURITY_RLS_VERDICT:** BLOCKING_REPAIR (F2). Ensure confidentiality of HR notes and private metadata at the projection boundary.
- **READ_MODEL_VERDICT:** BLOCKING_REPAIR (F2). Clarify contextual discovery/preview contract and Current Round calculation.
- **TEST_ACCEPTANCE_VERDICT:** BLOCKING_REPAIR (F1–F4). Expand verification acceptance criteria to cover status projection, fallback, DTO security, and viewports.
- **CROSS_SLICE_COMPOSITION_VERDICT:** PASS WITH PROMPT REPAIRS. Composition with Slice-04 remains coherent.

## Required Repairs
1. **F1:** Add the canonical 8-state Interviewer status mapping and verification criteria.
2. **F2:** Authorize a minimal additive contextual read RPC/adapter returning a safe Interviewer DTO with HR data stripped.
3. **F3:** Explicitly define Final Decision Source eligibility, qualitative update isolation, and fallback rules.
4. **F4:** Specify the canonical 6-viewport matrix and bilingual (VI/EN) state preservation requirements.

## Follow-up Non-Blockers
- Source authority hierarchy verified normative (Handover v1.18, Business Logic v1.2, Tech Arch v1.18, Design System v1.8).
- Hard rule against numerical scoring, ratings, or stars strictly preserved.
- Official PDF template (ASSET-001) properly isolated to later tasks.

## Final Release Decision
**PROMPT NOT APPROVED — REPAIR AND RE-REVIEW REQUIRED**
