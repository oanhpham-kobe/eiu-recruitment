from pathlib import Path

path = Path('supabase/tests/internal_user_r3_review_concurrency_test.sh')
text = path.read_text()

old_fixture = """insert into public.interview_participants(interview_participant_id,interview_id,app_user_id,participant_order,snapshot_name,snapshot_email,is_current) values
 ('$part_cancel'::uuid,'$int_cancel'::uuid,'$target_id'::uuid,1,'R3 Target','target_r3_${suffix}@eiu.edu.vn',true),
 ('$part_unsched'::uuid,'$int_unsched'::uuid,'$target_id'::uuid,1,'R3 Target','target_r3_${suffix}@eiu.edu.vn',true),
 ('$historical_part'::uuid,'$int_readd'::uuid,'$dormant_id'::uuid,1,'R3 Dormant','dormant_r3_${suffix}@eiu.edu.vn',false);
update public.interview_participants set removed_at=clock_timestamp() where interview_participant_id='$historical_part'::uuid;
"""
new_fixture = """insert into public.interview_participants(interview_participant_id,interview_id,app_user_id,participant_order,snapshot_name,snapshot_email,is_current,removed_at) values
 ('$part_cancel'::uuid,'$int_cancel'::uuid,'$target_id'::uuid,1,'R3 Target','target_r3_${suffix}@eiu.edu.vn',true,null),
 ('$part_unsched'::uuid,'$int_unsched'::uuid,'$target_id'::uuid,1,'R3 Target','target_r3_${suffix}@eiu.edu.vn',true,null),
 ('$historical_part'::uuid,'$int_readd'::uuid,'$dormant_id'::uuid,1,'R3 Dormant','dormant_r3_${suffix}@eiu.edu.vn',false,clock_timestamp());
"""
if old_fixture not in text:
    raise SystemExit('historical participant fixture anchor missing')
text = text.replace(old_fixture, new_fixture, 1)

old_role_race = """run_sql \"$block\" /tmp/r3-r-block & p0=$!; sleep .25; run_sql \"$remove\" /tmp/r3-r-remove & p1=$!; sleep .25; run_sql \"$bulk2\" /tmp/r3-r-bulk & p2=$!; set +e; wait $p0; s0=$?; wait $p1; s1=$?; wait $p2; s2=$?; set -e
[[ $s0 -eq 0 && $s1 -eq 0 && $s2 -eq 0 ]] || { cat /tmp/r3-r-* >&2; exit 1; }
! grep -qi 'deadlock detected' /tmp/r3-r-remove /tmp/r3-r-bulk
grep -q '\"success\": true' /tmp/r3-r-remove
grep -q 'NOT_FOUND' /tmp/r3-r-bulk
"""
new_role_race = """run_sql \"$block\" /tmp/r3-r-block & p0=$!; sleep .25; run_sql \"$remove\" /tmp/r3-r-remove & p1=$!; sleep .25; run_sql \"$bulk2\" /tmp/r3-r-bulk & p2=$!; set +e; wait $p0; s0=$?; wait $p1; s1=$?; wait $p2; s2=$?; set -e
[[ $s0 -eq 0 && $s1 -eq 0 && $s2 -ne 0 ]] || { cat /tmp/r3-r-* >&2; exit 1; }
! grep -qi 'deadlock detected' /tmp/r3-r-remove /tmp/r3-r-bulk
grep -q '\"success\": true' /tmp/r3-r-remove
grep -q 'APPLICATION_OWNER_NOT_ELIGIBLE' /tmp/r3-r-bulk
"""
if old_role_race not in text:
    raise SystemExit('HR-role/bulk race assertion anchor missing')
text = text.replace(old_role_race, new_role_race, 1)

old_restore = """psql_exec -qAt -c \"insert into public.app_user_roles(app_user_id,role_code) values('$target_id'::uuid,'HR') on conflict do nothing\"
"""
new_restore = """psql_exec -qAt -c \"insert into public.app_user_roles(app_user_id,role_code) values('$target_id'::uuid,'HR') on conflict do nothing\"
psql_exec -qAt -c \"insert into public.app_user_permissions(app_user_id,permission_code) select '$target_id'::uuid,p.permission_code from public.permissions p where p.permission_code in ('interviews.view','interviews.status','interviews.manage','interviews.participants') on conflict do nothing\"
"""
if old_restore not in text:
    raise SystemExit('post-HR-removal restore anchor missing')
text = text.replace(old_restore, new_restore, 1)

path.write_text(text)
