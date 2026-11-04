# Internal interview feedback RPC wire contract

All RPCs use the authenticated Supabase session. No service credential, email-domain authorization, or bearer invitation access. Envelopes are `{success:true,data:...}` / `{success:false,error_code:string,message:string}`. Content is plain text; render escaped. UUIDs are opaque IDs. Dates are ISO timestamptz; versions are positive integers.

## Reads

- `get_interview_feedback_workspace(p_limit integer=50,p_offset integer=0)` → `{can_manage:boolean,templates:Template[],interviews:InterviewOption[],collections:CollectionSummary[],invitations:OwnInvitationSummary[]}`. Limit 1–100; offset >=0. For HR, templates/interviews/collections populated; own invitations are populated for any assigned caller. Non-HR receives empty management arrays. Each list uses the supplied page window independently. `interviews` contains only writable contexts, including a nullable `collection_id` if already collected. HR may select only active, bound current participant IDs supplied on the exact option.
- `get_interview_feedback_collection(p_collection_id uuid)` → `Detail`. HR management permission yields HR detail; otherwise only the caller's own invitation and readable context.
- `get_interview_feedback_invitation(p_invitation_id uuid)` → own `Detail` even if caller also has HR permissions. Opaque link is this invitation UUID; login is always required. Wrong owner, removed/revoked assignment or inactive user is denied.

`Template`: `{template_id,family_id,version_no,name,questions:[{key,label,required}],published_at}`.

`Context`: `{interview_id,application_id,candidate_name,position_name,unit_name,round_no,start_at,end_at,readable,writable}`. No contact, CV, notes or other dossier fields.

`InterviewOption`: Context fields plus `{collection_id:null|uuid,participants:[{participant_id,evaluator_name}]}`.

`Collection`: `{collection_id,interview_id,template_id,deadline_at,created_at}`.

`Invitation`: `{invitation_id,participant_id,evaluator_name,state:'DRAFT'|'SUBMITTED'|'REVOKED',answers:{[questionKey]:string},version_no,submitted_at,available:boolean,delivery_state:'PROVIDER_PAUSED'}`. Display delivery as **Queued — delivery not configured**. No actual email is sent.

`Detail`: `{mode:'HR'|'OWN',collection:Collection,context:Context,template:Template}` plus HR `{invitations:Invitation[],blockers:[{invitation_id,evaluator_name,reason}],consolidation:Consolidation|null}` or own `{invitation:Invitation}`. Own detail has no other invitations, blockers, or consolidation.

`CollectionSummary`: Collection fields plus `{context:Context,selected_count,submitted_count,blockers:[],consolidation_state:null|'DRAFT'|'APPROVED'}`.

`OwnInvitationSummary`: `{invitation_id,collection_id,evaluator_name,state,version_no,deadline_at,context:Context}`. Only still-assigned readable own invitations appear, including historical submitted responses.

## Mutations

- `publish_interview_feedback_template(p_name text,p_questions jsonb,p_previous_template_id uuid,p_idempotency_key uuid)` → Template. Previous ID null creates a new family; a prior ID publishes the next immutable version in that family. No template editing in place. Name 1–200 trimmed chars; 1–30 ordered questions; keys match `[a-z][a-z0-9_]{0,63}`, unique; label 1–1000 trimmed chars; required boolean. Only key/label/required properties accepted. Existing collections remain pinned.
- `create_interview_feedback_collection(p_interview_id uuid,p_template_id uuid,p_participant_ids uuid[],p_deadline_at timestamptz,p_idempotency_key uuid)` → Collection. Select 1–100 distinct exact-current-participant IDs. Deadline null or future. One collection per exact interview. Repeated create returns existing collection without a duplicate invitation or notification; inspect returned template/deadline and reload detail. Initial invitations are DRAFT/version1/empty answers. New idempotency key per new user action; preserve it for network retry.
- `save_interview_feedback_response(p_invitation_id uuid,p_answers jsonb,p_expected_version_no bigint,p_submit boolean)` → Invitation. Full answers object replaces draft; omitted optional questions remain unanswered. Values must be strings <=10000 chars, known keys only. Save (`false`) permits missing required values. Submit (`true`) requires every required answer nonblank. Deadline/context enforced for all writes. Submitted responses are immutable. Exact repeated submit with the original pre-submit or current version and same answers returns existing response without another audit. Other stale writes reject.
- `revoke_interview_feedback_invitation(p_invitation_id uuid,p_expected_version_no bigint)` → Invitation. HR only; outstanding DRAFT only. No silent denominator removal.
- `save_interview_feedback_consolidation(p_collection_id uuid,p_title text,p_overall_summary text,p_expected_version_no bigint,p_approve boolean)` → Consolidation. Expected version **0** and approve=false creates draft only when all original invitees remain valid and submitted. Existing draft requires its current version. Approve=true requires an existing draft and rechecks completeness and context. Title 1–200 trimmed chars; summary <=20000 chars (empty allowed). Draft edits do not regenerate the pinned snapshot. Approved reports are immutable.

`Consolidation`: `{collection_id,title,overall_summary,snapshot,version_no,state:'DRAFT'|'APPROVED',created_at,approved_at}`. Snapshot is `{context:Context,template:Template,evaluators:[{invitation_id,participant_id,evaluator_name,answer_version_no,submitted_at}],questions:[{key,label,required,answers:[{invitation_id,evaluator_name,answer:null|string}]}]}`. Null means no supplied answer; empty string remains empty. Render ordered question/answer arrays with attribution. HR only; browser print/save PDF is local convenience, no server export.

Stable expected errors: UNAUTHENTICATED, FORBIDDEN, NOT_FOUND, VALIDATION_ERROR, STALE_VERSION, CONTEXT_NOT_WRITABLE, DEADLINE_PASSED, REQUIRED_ANSWER_MISSING, ALREADY_SUBMITTED, INVITATION_REVOKED, COMPLETENESS_REQUIRED, ALREADY_APPROVED. Re-fetch detail after stale/context errors. COMPLETENESS_REQUIRED detail blockers distinguish INVITATION_REVOKED, EVALUATOR_UNAVAILABLE, RESPONSE_NOT_SUBMITTED; current context.writable=false also blocks consolidation. Deadlines restrict response writes, not HR consolidation of completed responses.
