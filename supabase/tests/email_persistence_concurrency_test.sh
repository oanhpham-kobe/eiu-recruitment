#!/usr/bin/env bash
set -euo pipefail
container_name="supabase_db_eiu-recruitment-dev"
psql_exec() { docker exec -i "$container_name" psql -v ON_ERROR_STOP=1 -U postgres -d postgres "$@"; }
suffix="$(tr -d '-' < /proc/sys/kernel/random/uuid | cut -c1-12)"
psql_exec <<SQL
update private.email_configuration set environment_code='TEST',delivery_paused=false;
insert into public.email_outbox(email_type,environment_code,recipients,subject,body_text,idempotency_key,actor_scope,request_fingerprint,next_attempt_at)
values('CANDIDATE_SUBMISSION_CONFIRMATION','TEST','["worker-${suffix}@example.invalid"]','s07','s07',gen_random_uuid(),'s07:${suffix}','${suffix}',clock_timestamp());
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
echo "TASK-S07-001 staged worker concurrency assertions passed (${suffix})"
