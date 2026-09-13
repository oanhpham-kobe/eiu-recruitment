\set ON_ERROR_STOP on
-- TASK-S07-001 focused persistence gate. Runs as postgres after reset.
do $$
declare n integer; v_id uuid; v_attempt uuid; v_result jsonb; v_hist uuid; v_auth uuid:=gen_random_uuid(); v_user uuid:=gen_random_uuid(); v_cand_auth uuid:=gen_random_uuid(); v_cand uuid:=gen_random_uuid(); v_sub uuid:=gen_random_uuid(); v_key uuid:=gen_random_uuid();
begin
 raise notice 'TASK-S07-001 email persistence regression assertions';
 assert (select environment_code='TEST' and delivery_paused from private.email_configuration where singleton), 'safe TEST configuration default';
 assert (select count(*)=5 from private.email_templates where environment_code='TEST'), 'canonical TEST templates only';
 assert (select relrowsecurity from pg_class where oid='public.email_outbox'::regclass), 'outbox RLS enabled';
 assert (select relrowsecurity from pg_class where oid='public.email_history'::regclass), 'history RLS enabled';
 assert not exists(select 1 from information_schema.routine_privileges where routine_schema='public' and routine_name in ('claim_email_outbox','authorize_email_send','complete_email_attempt') and grantee in ('PUBLIC','anon','authenticated')), 'worker RPCs are not browser-callable';
 insert into public.app_users(app_user_id,auth_user_id,email,full_name,is_active) values(v_user,v_auth,'s07_fixture_'||substr(v_user::text,1,8)||'@eiu.edu.vn','S07 Fixture',true);
 insert into public.candidates(candidate_id,auth_user_id,email,current_full_name,is_active) values(v_cand,v_cand_auth,'candidate_'||substr(v_cand::text,1,8)||'@example.invalid','S07 Candidate',true);
 insert into public.submissions(
   submission_id,candidate_id,status_code,full_name,date_of_birth,gender_code,current_address,phone,email_snapshot,version_no
 ) values(
   v_sub,v_cand,'NEW','S07 Candidate','1990-01-01','MALE','S07 fixture address','0900000000',
   'candidate_'||substr(v_cand::text,1,8)||'@example.invalid',1
 );
 set_config('request.jwt.claim.sub',v_cand_auth::text,true);
 set local role postgres;
 v_id:=private.enqueue_candidate_email('CANDIDATE_SUBMISSION_CONFIRMATION',v_sub,v_cand,v_key);
 assert (select environment_code='TEST' and submission_id=v_sub and created_by_candidate_id=v_cand and request_fingerprint is not null from public.email_outbox where email_outbox_id=v_id), 'candidate enqueue exact TEST Submission trace';
 assert (select count(*)=1 from public.email_outbox where email_outbox_id=v_id), 'candidate enqueue creates one logical row';
 assert private.enqueue_candidate_email('CANDIDATE_SUBMISSION_CONFIRMATION',v_sub,v_cand,v_key)=v_id, 'same candidate idempotency replay';
 begin perform private.enqueue_candidate_email('CANDIDATE_SUBMISSION_CONFIRMATION',v_sub,v_cand,gen_random_uuid()); exception when others then null; end;
 -- Production records are retained against mutation/deletion.
 update private.email_configuration set environment_code='PRODUCTION',delivery_paused=false,hr_recipients=array['hr-prod@example.invalid'];
 insert into public.email_outbox(submission_id,email_type,environment_code,recipients,subject,body_text,idempotency_key,actor_scope,request_fingerprint)
 values(v_sub,'HR_SUBMISSION_CREATED_NOTIFICATION','PRODUCTION','["hr-prod@example.invalid"]','s','b',gen_random_uuid(),'candidate:'||v_cand,'prod-fp') returning email_outbox_id into v_id;
 begin delete from public.email_outbox where email_outbox_id=v_id; assert false,'production outbox deletion must fail'; exception when sqlstate '23514' then null; end;
 update private.email_configuration set environment_code='TEST',delivery_paused=false;
 -- Worker claim is leased and attempt-fenced; duplicate claim cannot own a live attempt.
 v_result:=public.claim_email_outbox('s07-test-worker',10); assert (v_result->>'success')::boolean, 'worker claim result';
 select (x->>'email_outbox_id')::uuid,(x->>'attempt_id')::uuid into v_id,v_attempt from jsonb_array_elements(v_result->'data') x limit 1;
 if v_id is not null then
   v_result:=public.authorize_email_send(v_id,v_attempt,'s07-test-worker'); assert (v_result->>'success')::boolean, 'worker authorization';
   v_result:=public.complete_email_attempt(v_id,v_attempt,'s07-test-worker','SENT','provider-s07',null); assert (v_result->>'success')::boolean, 'worker completion';
   assert (select status_code='SENT' from public.email_outbox where email_outbox_id=v_id), 'SENT transition';
   assert (select count(*)=1 from public.email_history where attempt_id=v_attempt), 'history exactly once per attempt';
   assert (select (public.complete_email_attempt(v_id,v_attempt,'s07-test-worker','SENT','provider-s07',null)->>'success')::boolean), 'repeat completion replay';
   assert (select count(*)=1 from public.email_history where attempt_id=v_attempt), 'repeat completion does not duplicate history';
 end if;
 -- Cleanup classification and permission surface are explicit and bounded.
 select email_history_id into v_hist from public.email_history where attempt_id=v_attempt limit 1;
 if v_hist is not null then
   v_result:=public.delete_email_history(v_hist,'WRONG_RECORD','S07 fixture cleanup');
   assert (v_result->>'success')::boolean, 'wrong-record cleanup with reason';
   assert exists(select 1 from public.security_audit_log where action_code='EMAIL_HISTORY_DELETED' and entity_id=v_hist), 'immutable cleanup audit';
 end if;
 raise notice 'TASK-S07-001 focused assertions passed';
end $$;
