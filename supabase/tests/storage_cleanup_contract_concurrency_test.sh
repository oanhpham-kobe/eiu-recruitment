#!/usr/bin/env bash
set -euo pipefail

: "${CONTAINER_NAME:?Set CONTAINER_NAME to the disposable Supabase Postgres container}"
container_name="$CONTAINER_NAME"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

psql_exec() {
  docker exec -i "$container_name" psql -qAt -v ON_ERROR_STOP=1 -U postgres -d postgres "$@"
}

suffix="$(uuidgen | tr -d '-')"
queue_id="$(psql_exec -c 'select gen_random_uuid()')"
reservation_id="$(psql_exec -c 'select gen_random_uuid()')"
parent_id="$(psql_exec -c 'select gen_random_uuid()')"
path="temp/00000000-0000-0000-0000-000000000001/00000000-0000-0000-0000-${suffix:0:12}/race.pdf"

psql_exec <<SQL
insert into private.storage_cleanup_provenance(
  bucket_name, object_path, upload_reservation_id, source_type, source_parent_id,
  reservation_expires_at, detached_at
) values (
  'candidate-quarantine', '$path', '$reservation_id', 'CANDIDATE_FORM', '$parent_id',
  clock_timestamp() - interval '2 hours', clock_timestamp()
);
insert into public.storage_cleanup_queue(
  storage_cleanup_id, source_type, source_parent_id, source_upload_reservation_id,
  bucket_name, object_path, reason_code, status_code, not_before
) values (
  '$queue_id', 'CANDIDATE_FORM', '$parent_id', '$reservation_id',
  'candidate-quarantine', '$path', 'RESERVATION_EXPIRED', 'PENDING',
  clock_timestamp() - interval '1 hour'
);
SQL

# Two independent database sessions race a single claim. Exactly one owns attempt one.
psql_exec -c "select public.claim_storage_cleanup_jobs('cleanup-a', 1, 60)" >"$tmp_dir/claim-a.json" &
claim_a_pid=$!
psql_exec -c "select public.claim_storage_cleanup_jobs('cleanup-b', 1, 60)" >"$tmp_dir/claim-b.json" &
claim_b_pid=$!
wait "$claim_a_pid"
wait "$claim_b_pid"
combined="$(jq -s --arg q "$queue_id" 'map(.data[]? | select(.storage_cleanup_id == $q)) | length' "$tmp_dir/claim-a.json" "$tmp_dir/claim-b.json")"
[[ "$combined" == "1" ]] || {
  echo 'concurrent cleanup claims must yield exactly one attempt owner' >&2
  exit 1
}

if [[ "$(jq -r --arg q "$queue_id" '.data[]? | select(.storage_cleanup_id == $q) | .attempt_id // empty' "$tmp_dir/claim-a.json")" != "" ]]; then
  claim_file="$tmp_dir/claim-a.json"
  old_worker='cleanup-a'
else
  claim_file="$tmp_dir/claim-b.json"
  old_worker='cleanup-b'
fi
old_attempt="$(jq -r --arg q "$queue_id" '.data[] | select(.storage_cleanup_id == $q) | .attempt_id' "$claim_file")"
old_token="$(jq -r --arg q "$queue_id" '.data[] | select(.storage_cleanup_id == $q) | .fencing_token' "$claim_file")"

# Reclaim invalidates both the old authorization and both old completion outcomes.
psql_exec -c "update public.storage_cleanup_queue set leased_until=clock_timestamp()-interval '1 second' where storage_cleanup_id='$queue_id'"
new_claim="$(psql_exec -c "select public.claim_storage_cleanup_jobs('cleanup-reclaimer', 10, 60)")"
new_attempt="$(printf '%s' "$new_claim" | jq -r --arg q "$queue_id" '.data[]? | select(.storage_cleanup_id == $q) | .attempt_id // empty')"
new_token="$(printf '%s' "$new_claim" | jq -r --arg q "$queue_id" '.data[]? | select(.storage_cleanup_id == $q) | .fencing_token // empty')"
[[ -n "$new_attempt" && "$new_attempt" != "$old_attempt" && "$new_token" != "$old_token" ]] || {
  echo 'reclaim must fence the prior attempt' >&2
  exit 1
}

for stale_success in true false; do
  stale="$(psql_exec -c "select public.complete_storage_cleanup_attempt('$queue_id','$old_attempt','$old_token','$old_worker',$stale_success,'WORKER_ERROR')")"
  [[ "$(printf '%s' "$stale" | jq -r '.error_code')" == "STALE_ATTEMPT" ]] || {
    echo 'stale success/error must not alter the reclaimed attempt' >&2
    exit 1
  }
done
stale_authorization="$(psql_exec -c "select public.authorize_storage_cleanup_attempt('$queue_id','$old_attempt','$old_token','$old_worker')")"
[[ "$(printf '%s' "$stale_authorization" | jq -r '.error_code')" == "STALE_ATTEMPT" ]] || {
  echo 'stale authorization must be fenced after reclaim' >&2
  exit 1
}
authorized="$(psql_exec -c "select public.authorize_storage_cleanup_attempt('$queue_id','$new_attempt','$new_token','cleanup-reclaimer')")"
[[ "$(printf '%s' "$authorized" | jq -r '.success')" == "true" ]] || {
  echo 'current worker must authorize before reporting completion' >&2
  exit 1
}
completed="$(psql_exec -c "select public.complete_storage_cleanup_attempt('$queue_id','$new_attempt','$new_token','cleanup-reclaimer',true,null)")"
[[ "$(printf '%s' "$completed" | jq -r '.data.status_code')" == "DONE" ]] || {
  echo 'current authorized attempt must complete' >&2
  exit 1
}

# A fifth expired lease settles to ERROR and cannot create a sixth attempt.
exhausted_queue="$(psql_exec -c 'select gen_random_uuid()')"
exhausted_reservation="$(psql_exec -c 'select gen_random_uuid()')"
exhausted_path="temp/00000000-0000-0000-0000-000000000002/00000000-0000-0000-0000-${suffix:0:12}/exhausted.pdf"
psql_exec <<SQL
insert into private.storage_cleanup_provenance(
  bucket_name, object_path, upload_reservation_id, source_type, source_parent_id,
  reservation_expires_at, detached_at
) values (
  'candidate-quarantine', '$exhausted_path', '$exhausted_reservation', 'CANDIDATE_FORM',
  '$parent_id', clock_timestamp()-interval '2 hours', clock_timestamp()
);
insert into public.storage_cleanup_queue(
  storage_cleanup_id, source_type, source_parent_id, source_upload_reservation_id,
  bucket_name, object_path, reason_code, status_code, attempts, not_before, leased_until
) values (
  '$exhausted_queue', 'CANDIDATE_FORM', '$parent_id', '$exhausted_reservation',
  'candidate-quarantine', '$exhausted_path', 'RESERVATION_EXPIRED', 'PROCESSING',
  5, clock_timestamp()-interval '1 hour', clock_timestamp()-interval '1 second'
);
SQL
psql_exec -c "select public.claim_storage_cleanup_jobs('cleanup-exhaustion', 10, 60)" >/dev/null
[[ "$(psql_exec -c "select status_code || ':' || attempts from public.storage_cleanup_queue where storage_cleanup_id='$exhausted_queue'")" == "ERROR:5" ]] || {
  echo 'fifth expired lease must settle without a sixth attempt' >&2
  exit 1
}

# These are actual command races, not a mock lock-order assertion. The fixture keeps
# the entities private to this disposable test database and verifies that each pair
# terminates within the timeout rather than deadlocking.
candidate_auth="$(psql_exec -c 'select gen_random_uuid()')"
candidate_id="$(psql_exec -c 'select gen_random_uuid()')"
notice="s07-concurrency-${suffix}"
document_type="$(psql_exec -c 'select gen_random_uuid()')"
session_id="$(psql_exec -c 'select gen_random_uuid()')"
sign_reservation="$(psql_exec -c 'select gen_random_uuid()')"
scan_reservation="$(psql_exec -c 'select gen_random_uuid()')"
psql_exec <<SQL
insert into public.candidates(candidate_id,auth_user_id,email)
values('$candidate_id','$candidate_auth','s07-$candidate_id@example.test');
insert into public.privacy_notice_versions(notice_version,content_vi,content_hash_sha256,is_current)
values('$notice','s07 concurrency',repeat('d',64),false);
insert into public.document_types(document_type_id,code,name_vi,scope_code)
values('$document_type','S07C-${suffix:0:8}','S07 concurrency','SUBMISSION');
insert into public.candidate_form_sessions(candidate_form_session_id,candidate_id,mode_code,presented_privacy_notice_version,expires_at)
values('$session_id','$candidate_id','NEW_SUBMISSION','$notice',clock_timestamp()+interval '1 hour');
insert into public.upload_reservations(upload_reservation_id,candidate_form_session_id,intended_document_type_id,temp_bucket,temp_path,original_filename,actor_auth_user_id,idempotency_key,expires_at,status_code)
values
('$sign_reservation','$session_id','$document_type','candidate-quarantine','temp/$session_id/$sign_reservation/sign.pdf','sign.pdf','$candidate_auth',gen_random_uuid(),clock_timestamp()+interval '30 minutes','RESERVED'),
('$scan_reservation','$session_id','$document_type','candidate-quarantine','temp/$session_id/$scan_reservation/scan.pdf','scan.pdf','$candidate_auth',gen_random_uuid(),clock_timestamp()+interval '30 minutes','UPLOADED');
update public.upload_reservations
set actual_size_bytes=1, checksum_sha256=repeat('a',64), detected_mime_type='application/pdf'
where upload_reservation_id='$scan_reservation';
SQL

candidate_sql_prefix="begin; select set_config('request.jwt.claim.sub','$candidate_auth',true);"
timeout 20 bash -c "printf \"%s select public.prepare_signed_upload('$sign_reservation'); commit;\" \"$candidate_sql_prefix\" | docker exec -i '$container_name' psql -qAt -v ON_ERROR_STOP=1 -U postgres -d postgres" >"$tmp_dir/sign.json" &
sign_pid=$!
timeout 20 bash -c "printf \"%s select public.cancel_candidate_form_session('$session_id'); commit;\" \"$candidate_sql_prefix\" | docker exec -i '$container_name' psql -qAt -v ON_ERROR_STOP=1 -U postgres -d postgres" >"$tmp_dir/cancel.json" &
cancel_pid=$!
wait "$sign_pid"
wait "$cancel_pid"

scan_session="$(psql_exec -c 'select gen_random_uuid()')"
scan_request_reservation="$(psql_exec -c 'select gen_random_uuid()')"
psql_exec <<SQL
insert into public.candidate_form_sessions(candidate_form_session_id,candidate_id,mode_code,presented_privacy_notice_version,expires_at)
values('$scan_session','$candidate_id','NEW_SUBMISSION','$notice',clock_timestamp()+interval '1 hour');
insert into public.upload_reservations(upload_reservation_id,candidate_form_session_id,intended_document_type_id,temp_bucket,temp_path,original_filename,actor_auth_user_id,idempotency_key,expires_at,status_code,actual_size_bytes,checksum_sha256,detected_mime_type)
values('$scan_request_reservation','$scan_session','$document_type','candidate-quarantine','temp/$scan_session/$scan_request_reservation/request.pdf','request.pdf','$candidate_auth',gen_random_uuid(),clock_timestamp()+interval '30 minutes','UPLOADED',1,repeat('b',64),'application/pdf');
SQL
timeout 20 bash -c "printf \"%s select public.request_candidate_document_scan('$scan_session','$scan_request_reservation','ADD',null); commit;\" \"$candidate_sql_prefix\" | docker exec -i '$container_name' psql -qAt -v ON_ERROR_STOP=1 -U postgres -d postgres" >"$tmp_dir/scan.json" &
scan_pid=$!
timeout 20 bash -c "printf \"%s select public.cancel_candidate_form_session('$scan_session'); commit;\" \"$candidate_sql_prefix\" | docker exec -i '$container_name' psql -qAt -v ON_ERROR_STOP=1 -U postgres -d postgres" >"$tmp_dir/scan-cancel.json" &
scan_cancel_pid=$!
wait "$scan_pid"
wait "$scan_cancel_pid"

# Interview finalization now takes the same parent -> reservation order as deletion.
# The application ancestors are intentionally fixture-only; the two RPCs operate on
# actual Interview/reservation rows and must serialize without a lock-order deadlock.
staff_auth="$(psql_exec -c 'select gen_random_uuid()')"
staff_id="$(psql_exec -c 'select gen_random_uuid()')"
interview_candidate_auth="$(psql_exec -c 'select gen_random_uuid()')"
interview_candidate_id="$(psql_exec -c 'select gen_random_uuid()')"
interview_submission="$(psql_exec -c 'select gen_random_uuid()')"
interview_unit="$(psql_exec -c 'select gen_random_uuid()')"
interview_group="$(psql_exec -c 'select gen_random_uuid()')"
interview_position="$(psql_exec -c 'select gen_random_uuid()')"
interview_document_type="$(psql_exec -c 'select gen_random_uuid()')"
interview_id="$(psql_exec -c 'select gen_random_uuid()')"
application_id="$(psql_exec -c 'select gen_random_uuid()')"
interview_reservation="$(psql_exec -c 'select gen_random_uuid()')"
psql_exec <<SQL
insert into public.app_users(app_user_id,auth_user_id,email,full_name)
values('$staff_id','$staff_auth','s07-$staff_id@eiu.edu.vn','S07 concurrency');
insert into public.app_user_roles(app_user_id,role_code)
values('$staff_id','HR');
insert into public.permissions(permission_code,description)
values('interviews.manage','S07 test permission'),('interviews.view','S07 test permission')
on conflict(permission_code) do nothing;
insert into public.app_user_permissions(app_user_id,permission_code)
values('$staff_id','interviews.manage'),('$staff_id','interviews.view');
insert into public.candidates(candidate_id,auth_user_id,email)
values('$interview_candidate_id','$interview_candidate_auth','s07-$interview_candidate_id@example.test');
insert into public.submissions(
  submission_id,candidate_id,full_name,date_of_birth,gender_code,current_address,phone,email_snapshot
) values (
  '$interview_submission','$interview_candidate_id','S07',date '2000-01-01','FEMALE',
  'test','0000000000','s07-$interview_submission@example.test'
);
insert into public.organizational_units(unit_id,code,name_vi)
values('$interview_unit','S07U-${suffix:0:8}','S07 concurrency');
insert into public.position_groups(position_group_id,code,name_vi)
values('$interview_group','S07G-${suffix:0:8}','S07 concurrency');
insert into public.positions(position_id,unit_id,position_group_id,code,name_vi)
values('$interview_position','$interview_unit','$interview_group','S07P-${suffix:0:8}','S07 concurrency');
insert into public.document_types(document_type_id,code,name_vi,scope_code)
values('$interview_document_type','S07I-${suffix:0:8}','S07 concurrency','INTERVIEW');
insert into public.applications(application_id,submission_id,unit_id,position_id,hr_owner_id)
values('$application_id','$interview_submission','$interview_unit','$interview_position','$staff_id');
insert into public.interviews(interview_id,application_id,round_no)
values('$interview_id','$application_id',1);
insert into public.upload_reservations(
  upload_reservation_id,interview_id,intended_document_type_id,temp_bucket,temp_path,
  original_filename,actor_auth_user_id,idempotency_key,expires_at,status_code,
  malware_scan_status,actual_size_bytes,checksum_sha256,detected_mime_type
) values (
  '$interview_reservation','$interview_id','$interview_document_type','interview-quarantine',
  'temp/interview/$interview_id/$interview_reservation','finalize.pdf','$staff_auth',
  gen_random_uuid(),clock_timestamp()+interval '30 minutes','UPLOADED','CLEAN',
  1,repeat('c',64),'application/pdf'
);
SQL
staff_sql_prefix="begin; set local request.jwt.claim.sub='$staff_auth';"
timeout 20 bash -c "printf \"%s select public.finalize_interview_upload('$interview_reservation',null,'interview-quarantine','temp/interview/$interview_id/$interview_reservation','finalize.pdf','application/pdf',1,repeat('c',64),null); commit;\" \"$staff_sql_prefix\" | docker exec -i '$container_name' psql -qAt -v ON_ERROR_STOP=1 -U postgres -d postgres" >"$tmp_dir/finalize.json" &
finalize_pid=$!
timeout 20 bash -c "printf \"%s select public.delete_or_inactivate_interview('$interview_id',1); commit;\" \"$staff_sql_prefix\" | docker exec -i '$container_name' psql -qAt -v ON_ERROR_STOP=1 -U postgres -d postgres" >"$tmp_dir/interview-delete.json" &
delete_pid=$!
wait "$finalize_pid"
wait "$delete_pid"
[[ "$(jq -s 'length == 1' "$tmp_dir/finalize.json")" == "true" ]] || {
  echo 'finalize race did not return a protocol result' >&2
  exit 1
}
[[ "$(jq -s 'length == 1' "$tmp_dir/interview-delete.json")" == "true" ]] || {
  echo 'Interview deletion race did not return a protocol result' >&2
  exit 1
}

echo "TASK-S07-003 concurrent cleanup, reclaim, signing/cancel, scan/cancel, and Interview finalize/delete assertions passed ($suffix)"
