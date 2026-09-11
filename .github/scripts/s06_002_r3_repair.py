import os
from pathlib import Path

migration_path = Path(os.environ["MIGRATION_PATH"])

migration = r'''-- TASK-S06-002 / R3 repair: complete Unit/User/Application and Interview/User
-- lock-order proof, distinguish dormant history from new participant selection,
-- and repeat trusted Auth proof after the full first-bind lock set.

-- -----------------------------------------------------------------------------
-- 1. Durable app_user Unit history: unchanged Unit is retained history, not a
--    newly-selected master reference. New/changed references still key-share
--    the Unit before the holder write commits.
-- -----------------------------------------------------------------------------
create or replace function private.capture_app_user_master_reference_history_r3()
returns trigger
language plpgsql
security definer
set search_path = ''
as $$
begin
  if tg_op <> 'INSERT' then
    perform private.record_master_reference_history('organizational_units', old.unit_id, false);
  end if;

  if tg_op = 'INSERT'
     or (tg_op = 'UPDATE' and new.unit_id is distinct from old.unit_id) then
    perform private.record_master_reference_history('organizational_units', new.unit_id, true);
  end if;

  if tg_op = 'DELETE' then
    return old;
  end if;
  return new;
end;
$$;

revoke all on function private.capture_app_user_master_reference_history_r3()
  from public, anon, authenticated;
grant execute on function private.capture_app_user_master_reference_history_r3()
  to postgres, service_role;

drop trigger if exists s06_master_reference_history_capture on public.app_users;
create trigger s06_master_reference_history_capture
  before insert or update or delete on public.app_users
  for each row execute function private.capture_app_user_master_reference_history_r3();

-- Directory updates that may select a new Unit or normalized email acquire those
-- resources before the target User row. The retained R2 implementation keeps all
-- canonical validation/idempotency/audit behavior and re-acquires the same locks
-- transaction-locally without changing the order.
alter function public.update_internal_user_directory(uuid, jsonb, bigint, uuid)
  rename to update_internal_user_directory_s06_002_r2_impl;

revoke all on function public.update_internal_user_directory_s06_002_r2_impl(uuid, jsonb, bigint, uuid)
  from public, anon, authenticated;
grant execute on function public.update_internal_user_directory_s06_002_r2_impl(uuid, jsonb, bigint, uuid)
  to postgres, service_role;

create or replace function public.update_internal_user_directory(
  p_target_user_id uuid,
  p_patch jsonb,
  p_expected_version_no bigint,
  p_idempotency_key uuid
)
returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
  v_email text;
  v_unit_id uuid;
begin
  if p_patch is not null and jsonb_typeof(p_patch) = 'object' then
    if p_patch ? 'email' and jsonb_typeof(p_patch -> 'email') = 'string' then
      begin
        v_email := private.normalize_internal_eiu_email(p_patch ->> 'email');
      exception
        when invalid_parameter_value then
          v_email := null;
      end;
      if v_email is not null then
        perform pg_advisory_xact_lock(hashtextextended('internal-email:' || v_email, 0));
      end if;
    end if;

    if p_patch ? 'unit_id' and jsonb_typeof(p_patch -> 'unit_id') = 'string' then
      begin
        v_unit_id := nullif(btrim(p_patch ->> 'unit_id'), '')::uuid;
      exception
        when invalid_text_representation then
          v_unit_id := null;
      end;
      if v_unit_id is not null then
        perform 1
        from public.organizational_units u
        where u.unit_id = v_unit_id
          and u.is_active = true
        for key share;
      end if;
    end if;
  end if;

  return public.update_internal_user_directory_s06_002_r2_impl(
    p_target_user_id,
    p_patch,
    p_expected_version_no,
    p_idempotency_key
  );
end;
$$;

revoke all on function public.update_internal_user_directory(uuid, jsonb, bigint, uuid)
  from public, anon;
grant execute on function public.update_internal_user_directory(uuid, jsonb, bigint, uuid)
  to authenticated, postgres, service_role;

-- -----------------------------------------------------------------------------
-- 2. Interview operationalization: lock every current participant and the actor
--    FK row before taking Internal User advisory locks, then revalidate current
--    participant activity after the complete row/advisory set.
-- -----------------------------------------------------------------------------
create or replace function private.guard_resource_blocking_interview_participants()
returns trigger
language plpgsql
security definer
set search_path = ''
as $$
declare
  v_application_active boolean;
  v_participant_ids uuid[];
  v_lock_ids uuid[];
begin
  if not new.is_active
     or new.schedule_status_code = 'CANCELLED'
     or new.start_at is null
     or new.end_at is null
     or new.end_at <= clock_timestamp() then
    return new;
  end if;

  select a.is_active
  into v_application_active
  from public.applications a
  where a.application_id = new.application_id;

  if not coalesce(v_application_active, false) then
    return new;
  end if;

  select coalesce(array_agg(distinct ip.app_user_id order by ip.app_user_id), array[]::uuid[])
  into v_participant_ids
  from public.interview_participants ip
  where ip.interview_id = new.interview_id
    and ip.is_current = true;

  select coalesce(array_agg(distinct q.app_user_id order by q.app_user_id), array[]::uuid[])
  into v_lock_ids
  from (
    select unnest(v_participant_ids) as app_user_id
    union all
    select new.updated_by
  ) q
  where q.app_user_id is not null;

  -- All User rows first, in deterministic UUID order. This includes updated_by
  -- so FK acquisition cannot occur after a participant advisory lock.
  perform 1
  from public.app_users u
  where u.app_user_id = any(v_lock_ids)
  order by u.app_user_id
  for update;

  perform private.lock_internal_user_ids(v_lock_ids);

  if exists (
    select 1
    from public.interview_participants ip
    left join public.app_users u on u.app_user_id = ip.app_user_id
    where ip.interview_id = new.interview_id
      and ip.is_current = true
      and coalesce(u.is_active, false) = false
  ) then
    raise exception 'CURRENT_PARTICIPANT_INACTIVE_REASSIGN_REQUIRED'
      using errcode = '23514';
  end if;

  return new;
end;
$$;

revoke all on function private.guard_resource_blocking_interview_participants()
  from public, anon, authenticated;
grant execute on function private.guard_resource_blocking_interview_participants()
  to postgres, service_role;

-- -----------------------------------------------------------------------------
-- 3. New participant selection/restoration is always lifecycle-sensitive, even
--    when the Interview itself is dormant. Historical remove/reorder operations
--    do not enter this branch and remain maintainable.
-- -----------------------------------------------------------------------------
create or replace function private.validate_participant_lifecycle_and_user()
returns trigger
language plpgsql
security definer
set search_path = ''
as $$
declare
  v_user_active boolean;
begin
  if not ((new.is_current = true and new.removed_at is null)
          or (new.is_current = false and new.removed_at is not null)) then
    raise exception 'PARTICIPANT_LIFECYCLE_INVALID' using errcode = '23514';
  end if;

  if new.is_current = true
     and (
       tg_op = 'INSERT'
       or old.is_current is distinct from new.is_current
       or old.app_user_id is distinct from new.app_user_id
     ) then
    -- Row -> advisory -> revalidate. A deactivation that owns the row first
    -- therefore commits before selection can continue, and selection fails shut.
    perform 1
    from public.app_users u
    where u.app_user_id = new.app_user_id
    for update;

    if not found then
      raise exception 'USER_INACTIVE_NOT_SELECTABLE' using errcode = '23514';
    end if;

    perform private.lock_internal_user_ids(array[new.app_user_id]);

    select u.is_active
    into v_user_active
    from public.app_users u
    where u.app_user_id = new.app_user_id;

    if coalesce(v_user_active, false) = false then
      raise exception 'USER_INACTIVE_NOT_SELECTABLE' using errcode = '23514';
    end if;
  end if;

  return new;
end;
$$;

revoke all on function private.validate_participant_lifecycle_and_user()
  from public, anon, authenticated;
grant execute on function private.validate_participant_lifecycle_and_user()
  to postgres, service_role;

-- -----------------------------------------------------------------------------
-- 4. First Google bind: trusted Auth proof must still match the exact normalized
--    email after normalized-email, target-row, and Internal User locks are held.
-- -----------------------------------------------------------------------------
create or replace function public.provision_internal_identity_on_first_google_login()
returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
  v_auth_user_id uuid := auth.uid();
  v_email text;
  v_post_lock_email text;
  v_target public.app_users%rowtype;
  v_roles jsonb;
  v_permissions jsonb;
  v_result jsonb;
begin
  if v_auth_user_id is null then
    return jsonb_build_object('success',false,'error_code','UNAUTHENTICATED','message','Authentication required');
  end if;

  v_email := private.verified_google_auth_email(v_auth_user_id);
  if v_email is null then
    return jsonb_build_object('success',false,'error_code','FORBIDDEN','message','Only @eiu.edu.vn Google Workspace accounts are permitted');
  end if;

  perform pg_advisory_xact_lock(hashtextextended('internal-email:' || v_email, 0));

  if exists (
    select 1
    from public.app_users u
    where u.auth_user_id = v_auth_user_id
      and lower(u.email::text) <> v_email
  ) then
    return jsonb_build_object('success',false,'error_code','IDENTITY_REBIND_FORBIDDEN','message','Account is already bound to a different identity');
  end if;

  select * into v_target
  from public.app_users u
  where lower(u.email::text) = v_email
  for update;

  if not found then
    return jsonb_build_object('success',false,'error_code','NOT_FOUND','message','User account not found in internal directory');
  end if;
  if not v_target.is_active then
    return jsonb_build_object('success',false,'error_code','USER_INACTIVE','message','User account is inactive');
  end if;

  perform private.lock_internal_user_ids(array[v_target.app_user_id]);

  v_post_lock_email := private.verified_google_auth_email(v_auth_user_id);
  if v_post_lock_email is null or v_post_lock_email <> v_email then
    return jsonb_build_object('success',false,'error_code','FORBIDDEN','message','Google identity changed during verification');
  end if;

  if v_target.auth_user_id is not null and v_target.auth_user_id <> v_auth_user_id then
    return jsonb_build_object('success',false,'error_code','IDENTITY_REBIND_FORBIDDEN','message','Account is already bound to a different identity');
  end if;

  if exists (
    select 1
    from public.app_users u
    where u.auth_user_id = v_auth_user_id
      and u.app_user_id <> v_target.app_user_id
  ) then
    return jsonb_build_object('success',false,'error_code','IDENTITY_REBIND_FORBIDDEN','message','Account is already bound to a different identity');
  end if;

  if v_target.auth_user_id is null then
    update public.app_users
    set auth_user_id = v_auth_user_id
    where app_user_id = v_target.app_user_id
    returning * into v_target;

    insert into public.security_audit_log(
      actor_auth_user_id,actor_app_user_id,action_code,entity_type,entity_id,
      source_code,result_code,metadata
    ) values (
      v_auth_user_id,v_target.app_user_id,'INTERNAL_IDENTITY_FIRST_BIND','APP_USER',v_target.app_user_id,
      'RPC','SUCCESS',jsonb_build_object(
        'changed_fields',jsonb_build_array('auth_user_id'),
        'auth_user_id',v_auth_user_id,
        'provider','google'
      )
    );
  end if;

  select coalesce(jsonb_agg(x.role_code order by x.role_code), '[]'::jsonb)
  into v_roles
  from public.app_user_roles x
  where x.app_user_id = v_target.app_user_id;

  if v_target.is_root_admin then
    select coalesce(jsonb_agg(p.permission_code order by p.permission_code), '[]'::jsonb)
    into v_permissions
    from public.permissions p;
  else
    select coalesce(jsonb_agg(p.permission_code order by p.permission_code), '[]'::jsonb)
    into v_permissions
    from public.app_user_permissions p
    where p.app_user_id = v_target.app_user_id;
  end if;

  v_result := jsonb_build_object('success',true,'data',jsonb_build_object(
    'app_user_id',v_target.app_user_id,
    'auth_user_id',v_auth_user_id,
    'email',v_target.email::text,
    'full_name',v_target.full_name,
    'job_title',v_target.job_title,
    'unit_id',v_target.unit_id,
    'is_active',v_target.is_active,
    'is_root_admin',v_target.is_root_admin,
    'version_no',v_target.version_no,
    'roles',v_roles,
    'permissions',v_permissions
  ));
  return v_result;
end;
$$;

revoke all on function public.provision_internal_identity_on_first_google_login()
  from public, anon;
grant execute on function public.provision_internal_identity_on_first_google_login()
  to authenticated, postgres, service_role;
'''
migration_path.write_text(migration)

test_path = Path("supabase/tests/internal_user_r3_review_concurrency_test.sh")
test_path.write_text(r'''#!/usr/bin/env bash
set -euo pipefail

container_name="supabase_db_eiu-recruitment-dev"
new_uuid() { cat /proc/sys/kernel/random/uuid; }
suffix="$(tr -d '-' < /proc/sys/kernel/random/uuid | cut -c1-12)"
unit1="$(new_uuid)"; unit2="$(new_uuid)"; group_id="$(new_uuid)"; pos1="$(new_uuid)"; pos2="$(new_uuid)"; format_id="$(new_uuid)"
root_id="$(new_uuid)"; root_auth="$(new_uuid)"; target_id="$(new_uuid)"; target_auth="$(new_uuid)"; dormant_id="$(new_uuid)"
candidate_id="$(new_uuid)"; candidate_auth="$(new_uuid)"; submission_id="$(new_uuid)"; application_id="$(new_uuid)"
int_cancel="$(new_uuid)"; int_unsched="$(new_uuid)"; int_add="$(new_uuid)"; int_readd="$(new_uuid)"
part_cancel="$(new_uuid)"; part_unsched="$(new_uuid)"; historical_part="$(new_uuid)"
bind_user="$(new_uuid)"; bind_auth="$(new_uuid)"; bind_email="bind_r3_${suffix}@eiu.edu.vn"

psql_exec() { docker exec -i "$container_name" psql -v ON_ERROR_STOP=1 -U postgres -d postgres "$@"; }
run_sql() { local sql="$1" out="$2"; printf '%s ' "$sql" | docker exec -i "$container_name" psql -v ON_ERROR_STOP=1 -U postgres -d postgres >"$out" 2>&1; }

cleanup() {
  psql_exec >/dev/null 2>&1 <<SQL || true
begin;
delete from public.interview_reports where interview_participant_id in ('$part_cancel'::uuid,'$part_unsched'::uuid,'$historical_part'::uuid);
delete from public.interview_participants where interview_id in ('$int_cancel'::uuid,'$int_unsched'::uuid,'$int_add'::uuid,'$int_readd'::uuid);
delete from public.interviews where interview_id in ('$int_cancel'::uuid,'$int_unsched'::uuid,'$int_add'::uuid,'$int_readd'::uuid);
delete from public.applications where application_id='$application_id'::uuid;
delete from public.submissions where submission_id='$submission_id'::uuid;
delete from public.candidates where candidate_id='$candidate_id'::uuid;
delete from public.app_user_permissions where app_user_id in ('$root_id'::uuid,'$target_id'::uuid,'$dormant_id'::uuid,'$bind_user'::uuid);
delete from public.app_user_roles where app_user_id in ('$root_id'::uuid,'$target_id'::uuid,'$dormant_id'::uuid,'$bind_user'::uuid);
delete from public.app_users where app_user_id in ('$root_id'::uuid,'$target_id'::uuid,'$dormant_id'::uuid,'$bind_user'::uuid);
delete from auth.identities where user_id='$bind_auth'::uuid;
delete from auth.users where id='$bind_auth'::uuid;
delete from public.positions where position_id in ('$pos1'::uuid,'$pos2'::uuid);
delete from public.interview_formats where interview_format_id='$format_id'::uuid;
delete from public.position_groups where position_group_id='$group_id'::uuid;
delete from public.organizational_units where unit_id in ('$unit1'::uuid,'$unit2'::uuid);
commit;
SQL
}
trap cleanup EXIT

psql_exec <<SQL
insert into public.position_groups(position_group_id,name_vi,code,is_active) values('$group_id'::uuid,'R3 group','R3G_${suffix}',true);
insert into public.organizational_units(unit_id,name_vi,code,is_active) values
 ('$unit1'::uuid,'R3 unit 1','R3U1_${suffix}',true),('$unit2'::uuid,'R3 unit 2','R3U2_${suffix}',true);
insert into public.positions(position_id,unit_id,position_group_id,code,name_vi,is_active) values
 ('$pos1'::uuid,'$unit1'::uuid,'$group_id'::uuid,'R3P1_${suffix}','R3 pos 1',true),
 ('$pos2'::uuid,'$unit2'::uuid,'$group_id'::uuid,'R3P2_${suffix}','R3 pos 2',true);
insert into public.interview_formats(interview_format_id,code,name_vi,requires_room,requires_meeting_link,is_active)
 values('$format_id'::uuid,'R3F_${suffix}','R3 format',false,false,true);
insert into public.app_users(app_user_id,auth_user_id,email,full_name,unit_id,is_active,is_root_admin) values
 ('$root_id'::uuid,'$root_auth'::uuid,'root_r3_${suffix}@eiu.edu.vn','R3 Root','$unit1'::uuid,true,true),
 ('$target_id'::uuid,'$target_auth'::uuid,'target_r3_${suffix}@eiu.edu.vn','R3 Target','$unit1'::uuid,true,false),
 ('$dormant_id'::uuid,null,'dormant_r3_${suffix}@eiu.edu.vn','R3 Dormant','$unit1'::uuid,true,false),
 ('$bind_user'::uuid,null,'$bind_email','R3 Bind','$unit1'::uuid,true,false);
insert into public.app_user_roles(app_user_id,role_code) values('$target_id'::uuid,'HR');
insert into public.app_user_permissions(app_user_id,permission_code)
select '$target_id'::uuid,p.permission_code from public.permissions p
where p.permission_code in ('interviews.view','interviews.status','interviews.manage','interviews.participants');
insert into public.candidates(candidate_id,auth_user_id,email,current_full_name,is_active)
 values('$candidate_id'::uuid,'$candidate_auth'::uuid,'candidate_r3_${suffix}@example.test','R3 Candidate',true);
insert into public.submissions(submission_id,candidate_id,status_code,full_name,date_of_birth,gender_code,current_address,phone,email_snapshot,version_no)
 values('$submission_id'::uuid,'$candidate_id'::uuid,'READ','R3 Candidate','1990-01-01','MALE','Address','0900000000','candidate_r3_${suffix}@example.test',1);
insert into public.applications(application_id,submission_id,unit_id,position_id,hr_owner_id,is_active)
 values('$application_id'::uuid,'$submission_id'::uuid,'$unit1'::uuid,'$pos1'::uuid,'$root_id'::uuid,true);
insert into public.interviews(interview_id,application_id,round_no,start_at,end_at,interview_format_id,schedule_status_code,report_status_code,is_active) values
 ('$int_cancel'::uuid,'$application_id'::uuid,1,clock_timestamp()+interval '2 days',clock_timestamp()+interval '2 days 1 hour','$format_id'::uuid,'CANCELLED','FOLLOW_UP',true),
 ('$int_unsched'::uuid,'$application_id'::uuid,2,null,null,null,'AVAILABLE','FOLLOW_UP',true),
 ('$int_add'::uuid,'$application_id'::uuid,3,clock_timestamp()+interval '3 days',clock_timestamp()+interval '3 days 1 hour','$format_id'::uuid,'CANCELLED','FOLLOW_UP',true),
 ('$int_readd'::uuid,'$application_id'::uuid,4,null,null,null,'AVAILABLE','FOLLOW_UP',true);
insert into public.interview_participants(interview_participant_id,interview_id,app_user_id,participant_order,snapshot_name,snapshot_email,is_current) values
 ('$part_cancel'::uuid,'$int_cancel'::uuid,'$target_id'::uuid,1,'R3 Target','target_r3_${suffix}@eiu.edu.vn',true),
 ('$part_unsched'::uuid,'$int_unsched'::uuid,'$target_id'::uuid,1,'R3 Target','target_r3_${suffix}@eiu.edu.vn',true),
 ('$historical_part'::uuid,'$int_readd'::uuid,'$dormant_id'::uuid,1,'R3 Dormant','dormant_r3_${suffix}@eiu.edu.vn',false);
update public.interview_participants set removed_at=clock_timestamp() where interview_participant_id='$historical_part'::uuid;
insert into auth.users(id,instance_id,aud,role,email,encrypted_password,email_confirmed_at,raw_app_meta_data,raw_user_meta_data,created_at,updated_at)
 values('$bind_auth'::uuid,'00000000-0000-0000-0000-000000000000','authenticated','authenticated','$bind_email','',clock_timestamp(),'{}','{}',clock_timestamp(),clock_timestamp());
insert into auth.identities(provider_id,user_id,identity_data,provider,last_sign_in_at,created_at,updated_at)
 values('google-r3-${suffix}','$bind_auth'::uuid,jsonb_build_object('sub','google-r3-${suffix}','email','$bind_email'),'google',clock_timestamp(),clock_timestamp(),clock_timestamp());
SQL

root_prefix="set local role authenticated; select set_config('request.jwt.claim.sub','$root_auth',true);"
target_prefix="set local role authenticated; select set_config('request.jwt.claim.sub','$target_auth',true);"

# 1A. Non-null Unit: public lifecycle queued before bulk owner assignment.
ver="$(psql_exec -qAt -c "select version_no from public.app_users where app_user_id='$target_id'::uuid")"; k1="$(new_uuid)"; bk="$(new_uuid)"
block="begin; select 1 from public.app_users where app_user_id='$target_id'::uuid for update; select pg_sleep(3); commit;"
life="begin; set local statement_timeout='10s'; $root_prefix select public.set_internal_user_active('$target_id'::uuid,false,$ver,'$k1'::uuid); commit;"
bulk="begin; set local statement_timeout='10s'; $root_prefix select public.bulk_create_or_update_applications(array['$submission_id'::uuid],'$unit1'::uuid,null::uuid,'$pos1'::uuid,'$target_id'::uuid,'$bk'::uuid); commit;"
run_sql "$block" /tmp/r3-u-block & p0=$!; sleep .25; run_sql "$life" /tmp/r3-u-life & p1=$!; sleep .25; run_sql "$bulk" /tmp/r3-u-bulk & p2=$!; set +e; wait $p0; s0=$?; wait $p1; s1=$?; wait $p2; s2=$?; set -e
[[ $s0 -eq 0 && $s1 -eq 0 && $s2 -eq 0 ]] || { cat /tmp/r3-u-* >&2; exit 1; }
! grep -qi 'deadlock detected' /tmp/r3-u-life /tmp/r3-u-bulk
grep -q '"success": true' /tmp/r3-u-life
grep -q 'NOT_FOUND' /tmp/r3-u-bulk
psql_exec -qAt -c "update public.app_users set is_active=true where app_user_id='$target_id'::uuid"

# 1B. Non-null Unit: HR-role removal queued before bulk owner assignment.
ver="$(psql_exec -qAt -c "select version_no from public.app_users where app_user_id='$target_id'::uuid")"; k2="$(new_uuid)"; bk2="$(new_uuid)"
remove="begin; set local statement_timeout='10s'; $root_prefix select public.remove_hr_role('$target_id'::uuid,$ver,'$k2'::uuid); commit;"
bulk2="begin; set local statement_timeout='10s'; $root_prefix select public.bulk_create_or_update_applications(array['$submission_id'::uuid],'$unit1'::uuid,null::uuid,'$pos1'::uuid,'$target_id'::uuid,'$bk2'::uuid); commit;"
run_sql "$block" /tmp/r3-r-block & p0=$!; sleep .25; run_sql "$remove" /tmp/r3-r-remove & p1=$!; sleep .25; run_sql "$bulk2" /tmp/r3-r-bulk & p2=$!; set +e; wait $p0; s0=$?; wait $p1; s1=$?; wait $p2; s2=$?; set -e
[[ $s0 -eq 0 && $s1 -eq 0 && $s2 -eq 0 ]] || { cat /tmp/r3-r-* >&2; exit 1; }
! grep -qi 'deadlock detected' /tmp/r3-r-remove /tmp/r3-r-bulk
grep -q '"success": true' /tmp/r3-r-remove
grep -q 'NOT_FOUND' /tmp/r3-r-bulk
psql_exec -qAt -c "insert into public.app_user_roles(app_user_id,role_code) values('$target_id'::uuid,'HR') on conflict do nothing"

# 1C. Directory Unit selection locks Unit before target User; bulk shares Unit->User.
ver="$(psql_exec -qAt -c "select version_no from public.app_users where app_user_id='$target_id'::uuid")"; dk="$(new_uuid)"; bk3="$(new_uuid)"
dir="begin; set local statement_timeout='10s'; $root_prefix select public.update_internal_user_directory('$target_id'::uuid,jsonb_build_object('unit_id','$unit2'),$ver,'$dk'::uuid); commit;"
bulk3="begin; set local statement_timeout='10s'; $root_prefix select public.bulk_create_or_update_applications(array['$submission_id'::uuid],'$unit2'::uuid,null::uuid,'$pos2'::uuid,'$target_id'::uuid,'$bk3'::uuid); commit;"
run_sql "$block" /tmp/r3-d-block & p0=$!; sleep .25; run_sql "$dir" /tmp/r3-d-dir & p1=$!; sleep .25; run_sql "$bulk3" /tmp/r3-d-bulk & p2=$!; set +e; wait $p0; s0=$?; wait $p1; s1=$?; wait $p2; s2=$?; set -e
[[ $s0 -eq 0 && $s1 -eq 0 && $s2 -eq 0 ]] || { cat /tmp/r3-d-* >&2; exit 1; }
! grep -qi 'deadlock detected' /tmp/r3-d-dir /tmp/r3-d-bulk
grep -q '"success": true' /tmp/r3-d-dir
grep -q '"success": true' /tmp/r3-d-bulk
psql_exec -qAt -c "update public.applications set unit_id='$unit1'::uuid,position_id='$pos1'::uuid,hr_owner_id='$root_id'::uuid where application_id='$application_id'::uuid"

# 2A. HR is current participant: uncancel vs Root lifecycle must row-lock before advisory.
ver="$(psql_exec -qAt -c "select version_no from public.app_users where app_user_id='$target_id'::uuid")"; ik="$(new_uuid)"; iv="$(psql_exec -qAt -c "select version_no from public.interviews where interview_id='$int_cancel'::uuid")"
life2="begin; set local statement_timeout='10s'; $root_prefix select public.set_internal_user_active('$target_id'::uuid,false,$ver,'$ik'::uuid); commit;"
uncancel="begin; set local statement_timeout='10s'; $target_prefix select public.change_interview_schedule_status('$int_cancel'::uuid,'AVAILABLE',$iv); commit;"
run_sql "$block" /tmp/r3-i-block & p0=$!; sleep .25; run_sql "$life2" /tmp/r3-i-life & p1=$!; sleep .25; set +e; run_sql "$uncancel" /tmp/r3-i-uncancel & p2=$!; wait $p0; s0=$?; wait $p1; s1=$?; wait $p2; s2=$?; set -e
[[ $s0 -eq 0 && $s1 -eq 0 && $s2 -ne 0 ]] || { cat /tmp/r3-i-* >&2; exit 1; }
! grep -qi 'deadlock detected' /tmp/r3-i-life /tmp/r3-i-uncancel
grep -q 'CURRENT_PARTICIPANT_INACTIVE_REASSIGN_REQUIRED' /tmp/r3-i-uncancel
psql_exec -qAt -c "update public.app_users set is_active=true where app_user_id='$target_id'::uuid"

# 2B. Same actor/participant scheduling an unscheduled Interview vs lifecycle.
ver="$(psql_exec -qAt -c "select version_no from public.app_users where app_user_id='$target_id'::uuid")"; ik2="$(new_uuid)"; iv2="$(psql_exec -qAt -c "select version_no from public.interviews where interview_id='$int_unsched'::uuid")"; sk="$(new_uuid)"
life3="begin; set local statement_timeout='10s'; $root_prefix select public.set_internal_user_active('$target_id'::uuid,false,$ver,'$ik2'::uuid); commit;"
schedule="begin; set local statement_timeout='10s'; $target_prefix select public.save_interview_schedule('$int_unsched'::uuid,clock_timestamp()+interval '4 days',clock_timestamp()+interval '4 days 1 hour','$format_id'::uuid,null::uuid,null::text,null::text,null::text,$iv2,'$sk'::uuid); commit;"
run_sql "$block" /tmp/r3-s-block & p0=$!; sleep .25; run_sql "$life3" /tmp/r3-s-life & p1=$!; sleep .25; set +e; run_sql "$schedule" /tmp/r3-s-schedule & p2=$!; wait $p0; s0=$?; wait $p1; s1=$?; wait $p2; s2=$?; set -e
[[ $s0 -eq 0 && $s1 -eq 0 && $s2 -ne 0 ]] || { cat /tmp/r3-s-* >&2; exit 1; }
! grep -qi 'deadlock detected' /tmp/r3-s-life /tmp/r3-s-schedule
grep -q 'CURRENT_PARTICIPANT_INACTIVE_REASSIGN_REQUIRED' /tmp/r3-s-schedule
psql_exec -qAt -c "update public.app_users set is_active=true where app_user_id='$target_id'::uuid"

# 3A. Deactivation owns dormant target row first; CANCELLED add must wait/revalidate and fail.
ver="$(psql_exec -qAt -c "select version_no from public.app_users where app_user_id='$dormant_id'::uuid")"; dk1="$(new_uuid)"; ak="$(new_uuid)"
deact_hold="begin; set local statement_timeout='10s'; $root_prefix select public.set_internal_user_active('$dormant_id'::uuid,false,$ver,'$dk1'::uuid); select pg_sleep(2); commit;"
add="begin; set local statement_timeout='10s'; $root_prefix select public.add_interview_participant('$int_add'::uuid,'$dormant_id'::uuid,'$ak'::uuid); commit;"
run_sql "$deact_hold" /tmp/r3-a-deact & p1=$!; sleep .25; set +e; run_sql "$add" /tmp/r3-a-add & p2=$!; wait $p1; s1=$?; wait $p2; s2=$?; set -e
[[ $s1 -eq 0 && $s2 -ne 0 ]] || { cat /tmp/r3-a-* >&2; exit 1; }
grep -q 'USER_INACTIVE_NOT_SELECTABLE' /tmp/r3-a-add
psql_exec -qAt -c "select count(*) from public.interview_participants where interview_id='$int_add'::uuid and app_user_id='$dormant_id'::uuid and is_current" | grep -qx 0
psql_exec -qAt -c "update public.app_users set is_active=true where app_user_id='$dormant_id'::uuid"

# 3B. Deactivation owns row first; unscheduled re-add/restoration must wait/revalidate and fail.
ver="$(psql_exec -qAt -c "select version_no from public.app_users where app_user_id='$dormant_id'::uuid")"; dk2="$(new_uuid)"; rk="$(new_uuid)"
deact_hold2="begin; set local statement_timeout='10s'; $root_prefix select public.set_internal_user_active('$dormant_id'::uuid,false,$ver,'$dk2'::uuid); select pg_sleep(2); commit;"
readd="begin; set local statement_timeout='10s'; $root_prefix select public.readd_interview_participant('$historical_part'::uuid,'RESTORE_OLD_REPORT','$rk'::uuid); commit;"
run_sql "$deact_hold2" /tmp/r3-ra-deact & p1=$!; sleep .25; set +e; run_sql "$readd" /tmp/r3-ra-readd & p2=$!; wait $p1; s1=$?; wait $p2; s2=$?; set -e
[[ $s1 -eq 0 && $s2 -ne 0 ]] || { cat /tmp/r3-ra-* >&2; exit 1; }
grep -q 'USER_INACTIVE_NOT_SELECTABLE' /tmp/r3-ra-readd
psql_exec -qAt -c "select is_current::text from public.interview_participants where interview_participant_id='$historical_part'::uuid" | grep -qx false

# 4. Trusted Google evidence changes while first-bind waits on target row.
bind_block="begin; select 1 from public.app_users where app_user_id='$bind_user'::uuid for update; select pg_sleep(3); commit;"
bind="begin; set local statement_timeout='10s'; set local role authenticated; select set_config('request.jwt.claim.sub','$bind_auth',true); select public.provision_internal_identity_on_first_google_login(); commit;"
run_sql "$bind_block" /tmp/r3-b-block & p0=$!; sleep .25; run_sql "$bind" /tmp/r3-b-bind & p1=$!; sleep .5
psql_exec -qAt -c "update auth.users set email_confirmed_at=null where id='$bind_auth'::uuid"
set +e; wait $p0; s0=$?; wait $p1; s1=$?; set -e
[[ $s0 -eq 0 && $s1 -eq 0 ]] || { cat /tmp/r3-b-* >&2; exit 1; }
grep -q 'FORBIDDEN' /tmp/r3-b-bind
psql_exec -qAt -c "select (auth_user_id is null)::text from public.app_users where app_user_id='$bind_user'::uuid" | grep -qx true
psql_exec -qAt -c "select count(*) from public.security_audit_log where entity_id='$bind_user'::uuid and action_code='INTERNAL_IDENTITY_FIRST_BIND'" | grep -qx 0

echo "TASK-S06-002 R3 lock/evidence concurrency regressions PASS ($suffix)"
''')
test_path.chmod(0o755)

# Permanently route the R3 concurrency gate through the existing S06-002 CI step.
lifecycle = Path("supabase/tests/internal_user_lifecycle_concurrency_test.sh")
text = lifecycle.read_text()
anchor = 'bash supabase/tests/internal_user_r2_command_concurrency_test.sh\necho "TASK-S06-002 Internal User owner/participant concurrency assertions passed with fresh fixture $suffix"\n'
if anchor not in text:
    raise SystemExit("lifecycle test anchor missing")
text = text.replace(
    anchor,
    'bash supabase/tests/internal_user_r2_command_concurrency_test.sh\n'
    'bash supabase/tests/internal_user_r3_review_concurrency_test.sh\n'
    'echo "TASK-S06-002 Internal User owner/participant concurrency assertions passed with fresh fixture $suffix"\n',
    1,
)
lifecycle.write_text(text)

Path("project_control/reviews/S06_002_IMPLEMENTATION_R3_GATE_v1.md").write_text(r'''# TASK-S06-002 Independent Implementation Re-Review Gate R3

## Identity

- WORK_ID: `S06-002-IMPLEMENTATION-REVIEW-001-R3`
- REVIEWER: `eiu-reviewer`
- REPOSITORY: `oanhpham-kobe/eiu-recruitment`
- TASK_BRANCH: `oanhpham-kobe/TASK-S06-002-user-rbac-identity`
- R2_REVIEWED_SHA: `7c37d46fa504b5d98b156735d7355f1d938be0bf`
- R2_VERDICT: `BLOCKING_REPAIR`
- SOURCE_REOPEN_EXPECTATION: `false`
- EXACT_R3_SHA: supplied in the immutable coordinator handoff; reviewer must verify that exact SHA contains this gate before review.

## R2 blocker reconciliation required

1. Prove the complete Unit/User/Application graph. Unchanged `app_users.unit_id` history capture must not take a new-reference Unit lock; true directory Unit selection must lock Unit before target User; bulk/lifecycle/HR-role public races with non-null Unit must terminate without deadlock while preserving S06-001 durable history and active-master validation.
2. Interview operationalization must row-lock all current participant and actor FK User rows before Internal User advisory locks, then revalidate current participants. Cover uncancel and schedule by an HR who is also a current participant racing Root lifecycle administration.
3. New participant selection/restoration must use User row -> advisory -> post-lock active revalidation regardless of Interview dormancy. Historical remove/reorder maintenance remains allowed. Cover deactivation-first CANCELLED add and unscheduled re-add.
4. First Google bind must repeat `private.verified_google_auth_email(auth.uid())` after normalized-email advisory, target User row and Internal User advisory locks; it must equal the original advisory-key email and fail closed on evidence change.

## Required verification

- zero-state migration replay;
- focused Internal User/RBAC/Identity tests;
- R2 dormant-history and lock-order tests;
- R3 public-command staged concurrency tests;
- crossed Application/Interview/copy/bulk regressions;
- all retained S06-001 seed/history/durable-history regressions;
- full web install/audit/design/lint/typecheck/build/test;
- `supabase db lint --local --level error`;
- `git diff --check`;
- static proof that accepted migrations were not rewritten.

## Review boundary

Review exact immutable R3 SHA only. Reviewer is read-only and must not modify implementation, refs, integration, `main`, PRs, Vercel, connected Supabase, or later Slice-06 state.
''')
