#!/usr/bin/env bash
set -euo pipefail

container_name="supabase_db_eiu-recruitment-dev"
new_uuid() { cat /proc/sys/kernel/random/uuid; }
suffix="$(tr -d '-' < /proc/sys/kernel/random/uuid | cut -c1-12)"
unit_id="$(new_uuid)"
root_id="$(new_uuid)"; root_auth="$(new_uuid)"
caller_id="$(new_uuid)"; caller_auth="$(new_uuid)"
target_id="$(new_uuid)"; target_auth="$(new_uuid)"
blocked_email="r4_blocked_${suffix}@eiu.edu.vn"
final_email="r4_final_${suffix}@eiu.edu.vn"

psql_exec() { docker exec -i "$container_name" psql -v ON_ERROR_STOP=1 -U postgres -d postgres "$@"; }
run_sql() { local sql="$1" out="$2"; printf '%s ' "$sql" | docker exec -i "$container_name" psql -v ON_ERROR_STOP=1 -U postgres -d postgres >"$out" 2>&1; }

cleanup() {
  psql_exec >/dev/null 2>&1 <<SQL || true
begin;
delete from public.app_user_permissions where app_user_id in ('$root_id'::uuid,'$caller_id'::uuid,'$target_id'::uuid);
delete from public.app_user_roles where app_user_id in ('$root_id'::uuid,'$caller_id'::uuid,'$target_id'::uuid);
delete from public.app_users where app_user_id in ('$root_id'::uuid,'$caller_id'::uuid,'$target_id'::uuid);
delete from public.organizational_units where unit_id='$unit_id'::uuid;
commit;
SQL
}
trap cleanup EXIT

psql_exec <<SQL
insert into public.organizational_units(unit_id,name_vi,code,is_active)
values('$unit_id'::uuid,'R4 auth-before-lock unit','R4ABL_${suffix}',true);

insert into public.app_users(app_user_id,auth_user_id,email,full_name,is_active,is_root_admin) values
 ('$root_id'::uuid,'$root_auth'::uuid,'root_r4_${suffix}@eiu.edu.vn','R4 Root',true,true),
 ('$caller_id'::uuid,'$caller_auth'::uuid,'caller_r4_${suffix}@eiu.edu.vn','R4 Unauthorized',true,false),
 ('$target_id'::uuid,'$target_auth'::uuid,'target_r4_${suffix}@eiu.edu.vn','R4 Target',true,false);
SQL

root_prefix="set local role authenticated; select set_config('request.jwt.claim.sub','$root_auth',true);"
unauthz_prefix="set local role authenticated; select set_config('request.jwt.claim.sub','$caller_auth',true);"

# 1. An authenticated principal without users.directory_manage must return
# FORBIDDEN before waiting on the normalized-email advisory lock.
email_block="begin; select pg_advisory_xact_lock(hashtextextended('internal-email:$blocked_email',0)); select pg_sleep(2); commit;"
unauthz_email="begin; set local statement_timeout='700ms'; $unauthz_prefix select public.update_internal_user_directory('$target_id'::uuid,jsonb_build_object('email','$blocked_email'),1,'$(new_uuid)'::uuid); commit;"
run_sql "$email_block" /tmp/r4-email-block & p0=$!; sleep .2
set +e
run_sql "$unauthz_email" /tmp/r4-email-call; s1=$?
set -e
[[ $s1 -eq 0 ]] || { cat /tmp/r4-email-call >&2; kill "$p0" >/dev/null 2>&1 || true; wait "$p0" >/dev/null 2>&1 || true; exit 1; }
grep -q 'FORBIDDEN' /tmp/r4-email-call
! grep -qi 'statement timeout' /tmp/r4-email-call
wait "$p0"

# 2. The same unauthorized principal must return FORBIDDEN before waiting on a
# contended Unit row that the wrapper would otherwise request FOR KEY SHARE.
unit_block="begin; select 1 from public.organizational_units where unit_id='$unit_id'::uuid for update; select pg_sleep(2); commit;"
unauthz_unit="begin; set local statement_timeout='700ms'; $unauthz_prefix select public.update_internal_user_directory('$target_id'::uuid,jsonb_build_object('unit_id','$unit_id'),1,'$(new_uuid)'::uuid); commit;"
run_sql "$unit_block" /tmp/r4-unit-block & p0=$!; sleep .2
set +e
run_sql "$unauthz_unit" /tmp/r4-unit-call; s2=$?
set -e
[[ $s2 -eq 0 ]] || { cat /tmp/r4-unit-call >&2; kill "$p0" >/dev/null 2>&1 || true; wait "$p0" >/dev/null 2>&1 || true; exit 1; }
grep -q 'FORBIDDEN' /tmp/r4-unit-call
! grep -qi 'statement timeout' /tmp/r4-unit-call
wait "$p0"

# 3. Missing auth context must likewise return UNAUTHENTICATED before the email
# prelock path. Role authenticated is retained so function invocation itself is
# permitted; only the trusted JWT subject is absent.
email_block2="begin; select pg_advisory_xact_lock(hashtextextended('internal-email:$blocked_email',0)); select pg_sleep(2); commit;"
noauth_email="begin; set local role authenticated; set local statement_timeout='700ms'; select public.update_internal_user_directory('$target_id'::uuid,jsonb_build_object('email','$blocked_email'),1,'$(new_uuid)'::uuid); commit;"
run_sql "$email_block2" /tmp/r4-noauth-block & p0=$!; sleep .2
set +e
run_sql "$noauth_email" /tmp/r4-noauth-call; s3=$?
set -e
[[ $s3 -eq 0 ]] || { cat /tmp/r4-noauth-call >&2; kill "$p0" >/dev/null 2>&1 || true; wait "$p0" >/dev/null 2>&1 || true; exit 1; }
grep -q 'UNAUTHENTICATED' /tmp/r4-noauth-call
! grep -qi 'statement timeout' /tmp/r4-noauth-call
wait "$p0"

# 4. Authorized callers retain the accepted R3 prelock behavior and still reach
# the delegated implementation successfully after authorization.
ver="$(psql_exec -qAt -c "select version_no from public.app_users where app_user_id='$target_id'::uuid")"
authorized="begin; set local statement_timeout='5s'; $root_prefix select public.update_internal_user_directory('$target_id'::uuid,jsonb_build_object('email','$final_email','unit_id','$unit_id'),$ver,'$(new_uuid)'::uuid); commit;"
run_sql "$authorized" /tmp/r4-authorized-call
grep -q '"success": true' /tmp/r4-authorized-call
psql_exec -qAt -c "select lower(email::text)||'|'||unit_id::text from public.app_users where app_user_id='$target_id'::uuid" | grep -qx "$final_email|$unit_id"

printf '%s\n' 'TASK-S06-002 R4 authorization-before-prelock regression: PASS'
