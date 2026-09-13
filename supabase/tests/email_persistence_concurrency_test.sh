#!/usr/bin/env bash
set -euo pipefail
container_name="supabase_db_eiu-recruitment-dev"
psql_exec() { docker exec -i "$container_name" psql -v ON_ERROR_STOP=1 -U postgres -d postgres "$@"; }
suffix="$(tr -d '-' < /proc/sys/kernel/random/uuid | cut -c1-12)"
psql_exec <<SQL
update public.email_outbox set next_attempt_at=clock_timestamp()+interval '1 day'
where request_fingerprint is not null;
update private.email_configuration set environment_code='TEST',delivery_paused=false;
insert into public.email_outbox(submission_id,application_id,interview_id,email_type,environment_code,recipients,subject,body_text,idempotency_key,actor_scope,request_fingerprint,next_attempt_at)
select a.submission_id,a.application_id,i.interview_id,'INTERVIEW_INVITATION','TEST',
  jsonb_build_object('to',jsonb_build_array('worker-'||'${suffix}'||'@example.invalid'),'cc','[]'::jsonb),'s07','s07',
  gen_random_uuid(),'s07:${suffix}','${suffix}',clock_timestamp()
from public.interviews i join public.applications a on a.application_id=i.application_id
where i.is_active and a.is_active
order by i.interview_id limit 1;
do \$\$
begin
  if not exists(select 1 from public.email_outbox where actor_scope='s07:${suffix}') then
    raise exception 'S07 requires an Interview-backed outbox fixture';
  end if;
end\$\$;
SQL
call="select public.claim_email_outbox('worker-${suffix}',1)::text;"
docker exec -i "$container_name" psql -qAt -v ON_ERROR_STOP=1 -U postgres -d postgres -c "$call" >/tmp/s07-worker-a.txt & p1=$!
docker exec -i "$container_name" psql -qAt -v ON_ERROR_STOP=1 -U postgres -d postgres -c "$call" >/tmp/s07-worker-b.txt & p2=$!
wait "$p1"; wait "$p2"
a="$(cat /tmp/s07-worker-a.txt)"; b="$(cat /tmp/s07-worker-b.txt)"
if [[ "$a" != *'success'* || "$b" != *'success'* ]]; then echo 'worker claims must return typed success' >&2; exit 1; fi
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
token="$(docker exec -i "$container_name" psql -qAt -v ON_ERROR_STOP=1 -U postgres -d postgres -c "select attempt_id from private.email_attempts ea join public.email_outbox eo on eo.attempt_id=ea.attempt_id where eo.actor_scope='s07:${suffix}' and eo.status_code='SENDING'")"
message="$(docker exec -i "$container_name" psql -qAt -v ON_ERROR_STOP=1 -U postgres -d postgres -c "select email_outbox_id from public.email_outbox where actor_scope='s07:${suffix}'")"
docker exec -i "$container_name" psql -v ON_ERROR_STOP=1 -U postgres -d postgres -c "update public.email_outbox set locked_until=clock_timestamp()-interval '1 second' where email_outbox_id='$message'"
docker exec -i "$container_name" psql -qAt -v ON_ERROR_STOP=1 -U postgres -d postgres -c "begin; set local statement_timeout='10s'; select public.authorize_email_send('$message','$token','worker-${suffix}'); commit" >/tmp/s07-authorize-late.txt &
p1=$!
docker exec -i "$container_name" psql -qAt -v ON_ERROR_STOP=1 -U postgres -d postgres -c "select public.claim_email_outbox('reclaim-${suffix}',1)" >/tmp/s07-reclaim.txt &
p2=$!
wait "$p1"; wait "$p2"
token="$(docker exec -i "$container_name" psql -qAt -v ON_ERROR_STOP=1 -U postgres -d postgres -c "select attempt_id from private.email_attempts ea join public.email_outbox eo on eo.attempt_id=ea.attempt_id where eo.actor_scope='s07:${suffix}' and eo.status_code='SENDING'")"
if [[ -z "$token" ]]; then echo 'reclaim versus late authorization did not produce a live staged attempt' >&2; exit 1; fi
docker exec -i "$container_name" psql -v ON_ERROR_STOP=1 -U postgres -d postgres -c "select public.authorize_email_send('$message','$token','reclaim-${suffix}')"
docker exec -i "$container_name" psql -qAt -v ON_ERROR_STOP=1 -U postgres -d postgres -c "begin; set local statement_timeout='10s'; select public.complete_email_attempt('$message','$token','reclaim-${suffix}','SENT','s07-provider',null); commit" >/tmp/s07-complete.txt &
p1=$!
docker exec -i "$container_name" psql -qAt -v ON_ERROR_STOP=1 -U postgres -d postgres -c "select public.authorize_email_send('$message','$token','reclaim-${suffix}')" >/tmp/s07-authorize-complete.txt &
p2=$!
wait "$p1"; wait "$p2"
echo "TASK-S07-001 staged lock-order assertions passed (${suffix})"
exit 0
