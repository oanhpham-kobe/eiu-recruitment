#!/usr/bin/env bash
set -euo pipefail
container_name="supabase_db_eiu-recruitment-dev"
psql_exec() { docker exec -i "$container_name" psql -v ON_ERROR_STOP=1 -U postgres -d postgres "$@"; }
suffix="$(tr -d '-' < /proc/sys/kernel/random/uuid | cut -c1-12)"
psql_exec <<SQL
update public.email_outbox set next_attempt_at=clock_timestamp()+interval '1 day'
where request_fingerprint is not null;
do \$\$
declare v_actor uuid:=gen_random_uuid(); v_auth uuid:=gen_random_uuid();
begin
 insert into public.app_users(app_user_id,auth_user_id,email,full_name,is_active)
 values(v_actor,v_auth,'s07-worker-'||'${suffix}'||'@eiu.edu.vn','S07 Worker',true);
 insert into public.app_user_permissions(app_user_id,permission_code,granted_by,granted_at)
 values(v_actor,'interviews.email',v_actor,clock_timestamp());
end\$\$;
do \$\$
declare v_i uuid; v_a uuid; v_s uuid; v_snap jsonb; v_id uuid;
begin
 select i.interview_id,a.application_id,a.submission_id into v_i,v_a,v_s
 from public.interviews i join public.applications a on a.application_id=i.application_id
 where i.is_active and a.is_active
   and not exists (select 1 from public.interview_participants ip join public.app_users pu on pu.app_user_id=ip.app_user_id
                   where ip.interview_id=i.interview_id and ip.is_current and ip.removed_at is null and not pu.is_active)
 order by i.interview_id limit 1;
 if v_i is null then raise exception 'S07 requires an Interview-backed outbox fixture'; end if;
 v_snap:=private.email_snapshot('INTERVIEW_INVITATION',v_s,v_a,v_i);
 insert into public.email_outbox(submission_id,application_id,interview_id,email_type,environment_code,
   recipients,subject,body_text,template_version,idempotency_key,actor_scope,request_fingerprint,
   context_fingerprint,next_attempt_at)
 values(v_s,v_a,v_i,'INTERVIEW_INVITATION',v_snap->>'environment_code',v_snap->'recipients',
   v_snap->>'subject',v_snap->>'body_text',v_snap->>'template_version',gen_random_uuid(),
   's07:'||'${suffix}','${suffix}',v_snap->>'context_fingerprint',clock_timestamp())
 returning email_outbox_id into v_id;
 if not exists(select 1 from public.email_outbox where email_outbox_id=v_id and context_fingerprint is not null) then
   raise exception 'S07 snapshot-bound fixture missing context fingerprint';
 end if;
end\$\$;
SQL
actor_row="$(docker exec -i "$container_name" psql -qAt -F ' ' -v ON_ERROR_STOP=1 -U postgres -d postgres -c "select u.app_user_id,u.auth_user_id,i.interview_id,a.application_id,a.submission_id from public.app_users u join public.app_user_permissions p on p.app_user_id=u.app_user_id join public.interviews i on i.is_active join public.applications a on a.application_id=i.application_id where p.permission_code='interviews.email' and u.is_active and a.is_active and not exists (select 1 from public.interview_participants ip join public.app_users pu on pu.app_user_id=ip.app_user_id where ip.interview_id=i.interview_id and ip.is_current and ip.removed_at is null and not pu.is_active) order by i.interview_id limit 1")"
if [[ -z "$actor_row" ]]; then echo 'S07 setup failed: authenticated worker actor fixture missing' >&2; exit 1; fi
read -r actor actor_auth interview application submission <<<"$actor_row"
preview="$(docker exec -i "$container_name" psql -qAt -v ON_ERROR_STOP=1 -U postgres -d postgres -c "begin; select set_config('request.jwt.claim.sub','$actor_auth',true); select set_config('request.jwt.claims',jsonb_build_object('sub','$actor_auth')::text,true); set local role authenticated; select public.preview_email('INTERVIEW_INVITATION','$interview','$application','$submission'); commit" | tr -d '\r' | tail -n 1)"
if ! jq -e '.success == true' <<<"$preview" >/dev/null; then echo 'trusted preview fixture failed' >&2; exit 1; fi
fingerprint="$(jq -r '.data.preview_fingerprint' <<<"$preview")"
request="$(jq -cn --arg t INTERVIEW_INVITATION --arg i "$interview" --arg a "$application" --arg s "$submission" --arg f "$fingerprint" '{email_type:$t,interview_id:$i,application_id:$a,submission_id:$s,preview_fingerprint:$f}')"
same_key="$(uuidgen)"
enqueue_sql="begin; select set_config('request.jwt.claim.sub','$actor_auth',true); select set_config('request.jwt.claims',jsonb_build_object('sub','$actor_auth')::text,true); set local role authenticated; select public.enqueue_email('$request','$same_key'); commit"
docker exec -i "$container_name" psql -qAt -v ON_ERROR_STOP=1 -U postgres -d postgres -c "$enqueue_sql" >/tmp/s07-enqueue-a.txt &
p1=$!
docker exec -i "$container_name" psql -qAt -v ON_ERROR_STOP=1 -U postgres -d postgres -c "$enqueue_sql" >/tmp/s07-enqueue-b.txt &
p2=$!
wait "$p1"; wait "$p2"
enqueue_a="$(tr -d '\r' </tmp/s07-enqueue-a.txt | tail -n 1)"; enqueue_b="$(tr -d '\r' </tmp/s07-enqueue-b.txt | tail -n 1)"
if ! jq -e '.success == true' <<<"$enqueue_a" >/dev/null || ! jq -e '.success == true' <<<"$enqueue_b" >/dev/null ||
   [[ "$(jq -r '.data.email_outbox_id' <<<"$enqueue_a")" != "$(jq -r '.data.email_outbox_id' <<<"$enqueue_b")" ]]; then
  echo 'same-key concurrent enqueue must converge on one outbox row' >&2; exit 1;
fi
bulk_key="$(uuidgen)"
bulk_sql="begin; select set_config('request.jwt.claim.sub','$actor_auth',true); select set_config('request.jwt.claims',jsonb_build_object('sub','$actor_auth')::text,true); set local role authenticated; select public.bulk_enqueue_email(jsonb_build_array('$request'::jsonb),'$bulk_key'); commit"
docker exec -i "$container_name" psql -qAt -v ON_ERROR_STOP=1 -U postgres -d postgres -c "$bulk_sql" >/tmp/s07-bulk-a.txt &
p1=$!
docker exec -i "$container_name" psql -qAt -v ON_ERROR_STOP=1 -U postgres -d postgres -c "$bulk_sql" >/tmp/s07-bulk-b.txt &
p2=$!
wait "$p1"; wait "$p2"
bulk_a="$(tr -d '\r' </tmp/s07-bulk-a.txt | tail -n 1)"; bulk_b="$(tr -d '\r' </tmp/s07-bulk-b.txt | tail -n 1)"
if [[ "$bulk_a" != "$bulk_b" ]] || ! jq -e '.success | length == 1' <<<"$bulk_a" >/dev/null; then
  echo 'overlapping bulk requests must converge without duplicate target outcome' >&2; exit 1;
fi
participant="$(docker exec -i "$container_name" psql -qAt -v ON_ERROR_STOP=1 -U postgres -d postgres -c "select interview_participant_id from public.interview_participants where interview_id='$interview' and is_current limit 1")"
if [[ -z "$participant" ]]; then echo 'participant-change race requires a participant fixture' >&2; exit 1; fi
participant_key="$(uuidgen)"
participant_sql="begin; select set_config('request.jwt.claim.sub','$actor_auth',true); select set_config('request.jwt.claims',jsonb_build_object('sub','$actor_auth')::text,true); set local role authenticated; select public.enqueue_email('$request','$participant_key'); commit"
docker exec -i "$container_name" psql -qAt -v ON_ERROR_STOP=1 -U postgres -d postgres -c "begin; select 1 from public.interviews where interview_id='$interview' for update; select pg_sleep(1); update public.interview_participants set is_current=false,removed_at=clock_timestamp() where interview_participant_id='$participant'; commit" >/tmp/s07-participant-holder.txt &
p1=$!
sleep 0.1
participant_result="$(docker exec -i "$container_name" psql -qAt -v ON_ERROR_STOP=1 -U postgres -d postgres -c "$participant_sql" | tr -d '\r' | tail -n 1)"
wait "$p1"
if ! jq -e '.success == false and (.error_code == "STALE_PREVIEW" or .error_code == "FORBIDDEN")' <<<"$participant_result" >/dev/null; then
  echo 'participant change must invalidate concurrent enqueue' >&2; exit 1;
fi
call="select public.claim_email_outbox('worker-${suffix}',1)::text;"
docker exec -i "$container_name" psql -qAt -v ON_ERROR_STOP=1 -U postgres -d postgres -c "$call" >/tmp/s07-worker-a.txt & p1=$!
docker exec -i "$container_name" psql -qAt -v ON_ERROR_STOP=1 -U postgres -d postgres -c "$call" >/tmp/s07-worker-b.txt & p2=$!
wait "$p1"; wait "$p2"
a="$(cat /tmp/s07-worker-a.txt)"; b="$(cat /tmp/s07-worker-b.txt)"
if ! jq -e '.success == true' <<<"$a" >/dev/null || ! jq -e '.success == true' <<<"$b" >/dev/null; then
  echo 'worker claims must return typed success=true' >&2; exit 1;
fi
psql_exec <<SQL
do \$\$
declare n integer;
begin
 select count(*) into n from public.email_outbox where actor_scope='s07:${suffix}' and status_code='SENDING';
 assert n=1, 'SKIP LOCKED permits one live owner';
 select count(*) into n from private.email_attempts ea join public.email_outbox eo on eo.email_outbox_id=ea.email_outbox_id where eo.actor_scope='s07:${suffix}';
 assert n=1, 'one attempt identity for one logical message';
end\$\$;
SQL
token="$(docker exec -i "$container_name" psql -qAt -v ON_ERROR_STOP=1 -U postgres -d postgres -c "select ea.attempt_id from private.email_attempts ea join public.email_outbox eo on eo.attempt_id=ea.attempt_id where eo.actor_scope='s07:${suffix}' and eo.status_code='SENDING'")"
message="$(docker exec -i "$container_name" psql -qAt -v ON_ERROR_STOP=1 -U postgres -d postgres -c "select email_outbox_id from public.email_outbox where actor_scope='s07:${suffix}'")"
docker exec -i "$container_name" psql -v ON_ERROR_STOP=1 -U postgres -d postgres -c "update public.email_outbox set locked_until=clock_timestamp()-interval '1 second' where email_outbox_id='$message'"
docker exec -i "$container_name" psql -qAt -v ON_ERROR_STOP=1 -U postgres -d postgres -c "begin; set local statement_timeout='10s'; select public.authorize_email_send('$message','$token','worker-${suffix}'); commit" >/tmp/s07-authorize-late.txt &
p1=$!
docker exec -i "$container_name" psql -qAt -v ON_ERROR_STOP=1 -U postgres -d postgres -c "select public.claim_email_outbox('reclaim-${suffix}',1)" >/tmp/s07-reclaim.txt &
p2=$!
wait "$p1"; wait "$p2"
token="$(docker exec -i "$container_name" psql -qAt -v ON_ERROR_STOP=1 -U postgres -d postgres -c "select ea.attempt_id from private.email_attempts ea join public.email_outbox eo on eo.attempt_id=ea.attempt_id where eo.actor_scope='s07:${suffix}' and eo.status_code='SENDING'")"
if [[ -z "$token" ]]; then echo 'reclaim versus late authorization did not produce a live staged attempt' >&2; exit 1; fi
auth_result="$(docker exec -i "$container_name" psql -qAt -v ON_ERROR_STOP=1 -U postgres -d postgres -c "select public.authorize_email_send('$message','$token','reclaim-${suffix}')")"
if ! jq -e '.success == true' <<<"$auth_result" >/dev/null; then echo 'reclaimed snapshot-bound attempt must authorize' >&2; exit 1; fi
docker exec -i "$container_name" psql -qAt -v ON_ERROR_STOP=1 -U postgres -d postgres -c "begin; set local statement_timeout='10s'; select public.complete_email_attempt('$message','$token','reclaim-${suffix}','SENT','s07-provider',null); commit" >/tmp/s07-complete.txt &
p1=$!
docker exec -i "$container_name" psql -qAt -v ON_ERROR_STOP=1 -U postgres -d postgres -c "select public.authorize_email_send('$message','$token','reclaim-${suffix}')" >/tmp/s07-authorize-complete.txt &
p2=$!
wait "$p1"; wait "$p2"
psql_exec <<SQL
do \$\$
declare n integer;
begin
 select count(*) into n from public.email_history h
   join private.email_attempts ea on ea.attempt_id=h.attempt_id
   where ea.email_outbox_id='$message'::uuid and ea.status_code='SENT';
 assert n=1, 'completion/authorization race must retain one SENT history row';
 assert (select status_code='SENT' and attempt_id='$token'::uuid from public.email_outbox where email_outbox_id='$message'::uuid),
   'completion/authorization race must finalize the fenced attempt';
 select count(*) into n from public.security_audit_log where entity_id='$message'::uuid and action_code='EMAIL_SENT';
 assert n=1, 'completion must write one immutable send audit';
end\$\$;
SQL
echo "TASK-S07-001 staged lock-order assertions passed (${suffix})"
exit 0
