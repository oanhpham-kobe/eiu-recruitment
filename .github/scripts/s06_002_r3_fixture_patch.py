from pathlib import Path

path = Path('supabase/tests/internal_user_r3_review_concurrency_test.sh')
text = path.read_text()
old = """insert into public.interview_participants(interview_participant_id,interview_id,app_user_id,participant_order,snapshot_name,snapshot_email,is_current) values
 ('$part_cancel'::uuid,'$int_cancel'::uuid,'$target_id'::uuid,1,'R3 Target','target_r3_${suffix}@eiu.edu.vn',true),
 ('$part_unsched'::uuid,'$int_unsched'::uuid,'$target_id'::uuid,1,'R3 Target','target_r3_${suffix}@eiu.edu.vn',true),
 ('$historical_part'::uuid,'$int_readd'::uuid,'$dormant_id'::uuid,1,'R3 Dormant','dormant_r3_${suffix}@eiu.edu.vn',false);
update public.interview_participants set removed_at=clock_timestamp() where interview_participant_id='$historical_part'::uuid;
"""
new = """insert into public.interview_participants(interview_participant_id,interview_id,app_user_id,participant_order,snapshot_name,snapshot_email,is_current,removed_at) values
 ('$part_cancel'::uuid,'$int_cancel'::uuid,'$target_id'::uuid,1,'R3 Target','target_r3_${suffix}@eiu.edu.vn',true,null),
 ('$part_unsched'::uuid,'$int_unsched'::uuid,'$target_id'::uuid,1,'R3 Target','target_r3_${suffix}@eiu.edu.vn',true,null),
 ('$historical_part'::uuid,'$int_readd'::uuid,'$dormant_id'::uuid,1,'R3 Dormant','dormant_r3_${suffix}@eiu.edu.vn',false,clock_timestamp());
"""
if old not in text:
    raise SystemExit('historical participant fixture anchor missing')
path.write_text(text.replace(old, new, 1))
