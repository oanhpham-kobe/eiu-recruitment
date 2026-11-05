#!/usr/bin/env bash
set -euo pipefail
: "${CONTAINER_NAME:?Explicit disposable container required}"
[[ "$CONTAINER_NAME" == supabase_db_eiu-workflow-check-20261105 ]] || {
  echo 'Refusing a database other than the designated disposable harness' >&2; exit 1;
}
sql() { docker exec -i "$CONTAINER_NAME" psql -X -qAt -v ON_ERROR_STOP=1 -U postgres -d postgres "$@" | tr -d '\r'; }
suffix="$(sql -c "select left(replace(gen_random_uuid()::text,'-',''),12)")"
scratch="$(mktemp -d)"
trap 'rm -f "$scratch"/*.log; rmdir "$scratch"' EXIT
c="$(sql -c 'select gen_random_uuid()')"
a="$(sql -c 'select gen_random_uuid()')"
s="$(sql -c 'select gen_random_uuid()')"
r="$(sql -c 'select gen_random_uuid()')"
t="$(sql -c 'select gen_random_uuid()')"
sql <<SQL
insert into public.candidates(candidate_id,auth_user_id,email,is_active) values('$c','$a','$c@example.invalid',true);
insert into public.privacy_notice_versions(notice_version,content_vi,content_hash_sha256,is_current)
values('$suffix','Drive race',repeat('a',64),false);
insert into public.document_types(document_type_id,code,name_vi,scope_code) values('$t','DR-$suffix','Drive','SUBMISSION');
insert into public.candidate_form_sessions(candidate_form_session_id,candidate_id,mode_code,presented_privacy_notice_version,expires_at)
values('$s','$c','NEW_SUBMISSION','$suffix',clock_timestamp()+interval '1 hour');
insert into public.upload_reservations(upload_reservation_id,candidate_form_session_id,intended_document_type_id,temp_bucket,temp_path,original_filename,actor_auth_user_id,idempotency_key,expires_at)
values('$r','$s','$t','candidate-quarantine','temp/$s/$r/cv.pdf','cv.pdf','$a',gen_random_uuid(),clock_timestamp()+interval '1 hour');
SQL

wait_query() {
  local query="$1"
  for i in $(seq 1 120); do
    [[ "$(sql -c "$query")" == t ]] && return 0
    sleep 0.05
  done
  cat "$scratch"/*.log >&2
  echo 'Synchronization condition not reached' >&2; exit 1
}

run_race() {
  local label="$1" holder_sql="$2" contender_sql="$3" expected="$4"
  local gate="drive-gate-$suffix-$label" holder="drive-holder-$suffix-$label" contender="drive-contender-$suffix-$label"
  sql -c "set application_name='$gate'; select pg_advisory_lock(hashtextextended('$gate',0)); select pg_sleep(30);" >"$scratch/gate.log" 2>&1 &
  local gp=$!
  wait_query "select exists(select 1 from pg_stat_activity where application_name='$gate' and wait_event='PgSleep');"
  sql -c "set application_name='$holder'; begin; $holder_sql; select pg_advisory_lock(hashtextextended('$gate',0)); commit;" >"$scratch/holder.log" 2>&1 &
  local hp=$!
  wait_query "select exists(select 1 from pg_stat_activity where application_name='$holder' and wait_event='advisory');"
  sql -c "set application_name='$contender'; set role drive_storage_worker; $contender_sql;" >"$scratch/contender.log" 2>&1 &
  local cp=$!
  wait_query "select exists(select 1 from pg_stat_activity h join pg_stat_activity c on h.pid=any(pg_blocking_pids(c.pid)) where h.application_name='$holder' and c.application_name='$contender');"
  sql -c "select pg_cancel_backend(pid) from pg_stat_activity where application_name='$gate';" >/dev/null
  wait "$gp" || true
  wait "$hp"
  if wait "$cp"; then echo 'Contender unexpectedly succeeded' >&2; exit 1; fi
  grep -q "$expected" "$scratch/contender.log"
  echo "PASS synchronized $label: $expected"
}

run_race bind \
  "set local role drive_storage_worker; select public.bind_candidate_drive_object('$r','$a','drive_$suffix')" \
  "select public.bind_candidate_drive_object('$r','$a','other_$suffix')" \
  IDEMPOTENCY_CONFLICT

# Cancel takes the exact session lock used by real cancellation. The waiting
# public worker operation must recheck the committed terminal state after wait.
run_race cancel \
  "update public.candidate_form_sessions set status_code='CANCELLED' where candidate_form_session_id='$s'" \
  "select public.claim_drive_upload_attempt('$r','$a','race-worker',120)" \
  INVALID_STATE

fresh_reservation() {
  s="$(sql -c 'select gen_random_uuid()')"
  r="$(sql -c 'select gen_random_uuid()')"
  sql <<SQL
insert into public.candidate_form_sessions(candidate_form_session_id,candidate_id,mode_code,presented_privacy_notice_version,expires_at)
values('$s','$c','NEW_SUBMISSION','$suffix',clock_timestamp()+interval '1 hour');
insert into public.upload_reservations(upload_reservation_id,candidate_form_session_id,intended_document_type_id,temp_bucket,temp_path,original_filename,actor_auth_user_id,idempotency_key,expires_at)
values('$r','$s','$t','candidate-quarantine','temp/$s/$r/cv.pdf','cv.pdf','$a',gen_random_uuid(),clock_timestamp()+interval '1 hour');
SQL
}
fresh_reservation
sql -c "set role drive_storage_worker; select public.bind_candidate_drive_object('$r','$a','expiry_$suffix');" >/dev/null
run_race expiry \
  "update public.candidate_form_sessions set expires_at=clock_timestamp()-interval '1 second' where candidate_form_session_id='$s'" \
  "select public.claim_drive_upload_attempt('$r','$a','race-worker',120)" \
  INVALID_STATE

fresh_reservation
run_race signed_issuance \
  "set local role authenticated; select set_config('request.jwt.claim.sub','$a',true); select public.prepare_signed_upload('$r')" \
  "select public.bind_candidate_drive_object('$r','$a','signed_$suffix')" \
  STORAGE_PROVIDER_CONFLICT

fresh_reservation
sql -c "insert into storage.buckets(id,name,public) values('candidate-quarantine','candidate-quarantine',false) on conflict do nothing;"
run_race storage_insert \
  "set local role service_role; insert into storage.objects(bucket_id,name) values('candidate-quarantine','temp/$s/$r/cv.pdf')" \
  "select public.bind_candidate_drive_object('$r','$a','storage_$suffix')" \
  STORAGE_PROVIDER_CONFLICT
echo 'Drive synchronized bind/cancel/expiry/signed-issuance/Storage races passed'
