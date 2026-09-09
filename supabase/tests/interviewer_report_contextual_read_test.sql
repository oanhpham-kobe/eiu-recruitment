-- TASK-S05-001: contextual report read + owner-only mutation regressions.
\set ON_ERROR_STOP on

do $$
<<test>>
declare
  s text := substr(gen_random_uuid()::text, 1, 8);
  hr_auth uuid := gen_random_uuid();
  hr uuid;
  i1_auth uuid := gen_random_uuid();
  i1 uuid;
  i2_auth uuid := gen_random_uuid();
  i2 uuid;
  inactive_auth uuid := gen_random_uuid();
  inactive_user uuid;
  candidate_auth uuid := gen_random_uuid();
  candidate_id uuid;
  unit_id uuid;
  position_group_id uuid;
  position_id uuid;
  submission_id uuid;
  application_id uuid;
  old_interview_id uuid;
  current_interview_id uuid;
  old_p1 uuid;
  current_p1 uuid;
  current_p2 uuid;
  report1 uuid := gen_random_uuid();
  report2 uuid := gen_random_uuid();
  swap_report uuid;
  report_version bigint;
  r jsonb;
  visible_status text;
  status_code text;
  expected_status text;
  ts timestamptz;
begin
  raise notice '=== TASK-S05-001 interviewer report contextual read ===';

  if report1 > report2 then
    swap_report := report1;
    report1 := report2;
    report2 := swap_report;
  end if;

  assert not has_function_privilege(
    'anon',
    'public.get_interviewer_report_page()',
    'EXECUTE'
  ), 'anon must not execute interviewer report read RPC';
  assert has_function_privilege(
    'authenticated',
    'public.get_interviewer_report_page()',
    'EXECUTE'
  ), 'authenticated may invoke the contextual read RPC';
  assert not has_function_privilege(
    'anon',
    'public.save_own_interviewer_report(uuid,jsonb,bigint,jsonb)',
    'EXECUTE'
  ), 'anon must not execute owner-only report command';
  assert has_function_privilege(
    'authenticated',
    'public.save_own_interviewer_report(uuid,jsonb,bigint,jsonb)',
    'EXECUTE'
  ), 'authenticated may invoke owner-only report command';

  assert not has_schema_privilege(
    'anon',
    'interviewer_report_private',
    'USAGE'
  ), 'anon must not resolve the privileged read helper schema';
  assert has_schema_privilege(
    'authenticated',
    'interviewer_report_private',
    'USAGE'
  ), 'authenticated wrapper may resolve the bounded read helper schema';

  insert into public.organizational_units(code, name_vi, name_en)
  values ('S05001_U_' || s, 'Đơn vị S05', 'S05 Unit')
  returning unit_id into unit_id;

  insert into public.position_groups(code, name_vi, name_en)
  values ('S05001_PG_' || s, 'Nhóm S05', 'S05 Group')
  returning position_group_id into position_group_id;

  insert into public.positions(
    unit_id,
    position_group_id,
    code,
    name_vi,
    name_en
  )
  values (
    unit_id,
    position_group_id,
    'S05001_P_' || s,
    'Giảng viên S05',
    'S05 Lecturer'
  )
  returning position_id into position_id;

  insert into public.app_users(auth_user_id, full_name, email, is_active)
  values (hr_auth, 'S05 HR', 's05_hr_' || s || '@eiu.edu.vn', true)
  returning app_user_id into hr;

  insert into public.app_users(
    auth_user_id,
    full_name,
    email,
    job_title,
    is_active
  )
  values (
    i1_auth,
    'S05 Interviewer One',
    's05_i1_' || s || '@eiu.edu.vn',
    'Lecturer',
    true
  )
  returning app_user_id into i1;

  insert into public.app_users(
    auth_user_id,
    full_name,
    email,
    job_title,
    is_active
  )
  values (
    i2_auth,
    'S05 Interviewer Two',
    's05_i2_' || s || '@eiu.edu.vn',
    'Professor',
    true
  )
  returning app_user_id into i2;

  insert into public.app_users(auth_user_id, full_name, email, is_active)
  values (
    inactive_auth,
    'S05 Inactive',
    's05_inactive_' || s || '@eiu.edu.vn',
    true
  )
  returning app_user_id into inactive_user;

  insert into public.candidates(auth_user_id, email, is_active)
  values (
    candidate_auth,
    's05_candidate_' || s || '@example.com',
    true
  )
  returning public.candidates.candidate_id into candidate_id;

  insert into public.submissions(
    candidate_id,
    full_name,
    date_of_birth,
    gender_code,
    current_address,
    phone,
    email_snapshot,
    status_code
  )
  values (
    candidate_id,
    'S05 Candidate',
    '1990-01-01',
    'FEMALE',
    'S05 Address',
    '0900000000',
    's05_candidate_' || s || '@example.com',
    'PROCESSED'
  )
  returning public.submissions.submission_id into submission_id;

  insert into public.applications(
    submission_id,
    unit_id,
    position_id,
    hr_owner_id,
    is_active
  )
  values (submission_id, unit_id, position_id, hr, true)
  returning public.applications.application_id into application_id;

  insert into public.interviews(
    application_id,
    round_no,
    schedule_status_code,
    report_status_code,
    visible_to_interviewers,
    is_active
  )
  values (
    application_id,
    1,
    'AVAILABLE',
    'REPORT_SUBMITTED',
    true,
    true
  )
  returning public.interviews.interview_id into old_interview_id;

  insert into public.interviews(
    application_id,
    round_no,
    schedule_status_code,
    report_status_code,
    visible_to_interviewers,
    is_active
  )
  values (
    application_id,
    2,
    'AVAILABLE',
    'WAITING_FOR_REPORT',
    true,
    true
  )
  returning public.interviews.interview_id into current_interview_id;

  insert into public.interview_participants(
    interview_id,
    app_user_id,
    participant_order,
    snapshot_name,
    snapshot_job_title,
    snapshot_email,
    is_current
  )
  values (
    old_interview_id,
    i1,
    1,
    'S05 Interviewer One',
    'Lecturer',
    's05_i1_' || s || '@eiu.edu.vn',
    true
  )
  returning interview_participant_id into old_p1;

  insert into public.interview_participants(
    interview_id,
    app_user_id,
    participant_order,
    snapshot_name,
    snapshot_job_title,
    snapshot_email,
    is_current
  )
  values (
    current_interview_id,
    i1,
    1,
    'S05 Interviewer One',
    'Lecturer',
    's05_i1_' || s || '@eiu.edu.vn',
    true
  )
  returning interview_participant_id into current_p1;

  insert into public.interview_participants(
    interview_id,
    app_user_id,
    participant_order,
    snapshot_name,
    snapshot_job_title,
    snapshot_email,
    is_current
  )
  values (
    current_interview_id,
    i2,
    2,
    'S05 Interviewer Two',
    'Professor',
    's05_i2_' || s || '@eiu.edu.vn',
    true
  )
  returning interview_participant_id into current_p2;

  insert into public.interview_reports(
    interview_report_id,
    interview_participant_id,
    professional_knowledge,
    conclusion,
    created_by,
    updated_by
  )
  values (
    report1,
    current_p1,
    'Strong domain knowledge',
    'Primary decision',
    i1,
    i1
  );

  insert into public.interview_reports(
    interview_report_id,
    interview_participant_id,
    necessary_skills,
    expected_specific_job_assigned,
    created_by,
    updated_by
  )
  values (
    report2,
    current_p2,
    'Strong communication',
    'Newest decision job',
    i2,
    i2
  );

  insert into public.app_user_permissions(app_user_id, permission_code)
  select hr, p.permission_code
  from public.permissions p
  where p.permission_code in ('reports.view', 'reports.edit_interviewer')
  on conflict do nothing;

  -- Missing auth and Candidate identity fail closed.
  perform set_config('request.jwt.claims', '{}'::jsonb::text, true);
  r := public.get_interviewer_report_page();
  assert r->>'error_code' = 'UNAUTHENTICATED',
    'missing auth identity fails closed';

  perform set_config(
    'request.jwt.claims',
    jsonb_build_object('sub', candidate_auth::text)::text,
    true
  );
  r := public.get_interviewer_report_page();
  assert r->>'error_code' = 'FORBIDDEN',
    'candidate identity cannot consume Interviewer report projection';

  -- Exact-round contextual read: i2 participates only in Current Round.
  perform set_config(
    'request.jwt.claims',
    jsonb_build_object('sub', i2_auth::text)::text,
    true
  );
  r := public.get_interviewer_report_page();
  assert (r->>'success')::boolean,
    'authorized internal participant request succeeds';
  assert jsonb_array_length(r->'data'->'rounds') = 1,
    'no transitive access to a historical round';

  -- i1 participated directly in both rounds, so historical read remains valid.
  perform set_config(
    'request.jwt.claims',
    jsonb_build_object('sub', i1_auth::text)::text,
    true
  );
  r := public.get_interviewer_report_page();
  assert (r->>'success')::boolean, 'Interviewer read succeeds';
  assert jsonb_array_length(r->'data'->'rounds') = 2,
    'new Current Round does not revoke direct historical participation read';
  assert (r->'data'->'rounds'->0->>'is_current_round')::boolean,
    'Current Round is server-derived and sorted first';
  assert not (r->'data'->'rounds'->1->>'can_edit')::boolean,
    'historical round is never writable';

  -- DTO privacy is enforced at the server boundary.
  assert position('hr_report_note' in r::text) = 0,
    'HR report note is absent from DTO';
  assert position('hr_owner' in r::text) = 0,
    'HR owner identity is absent from DTO';
  assert position('decision_updated_by' in r::text) = 0,
    'technical decision actor is absent from DTO';
  assert position('decision_updated_at' in r::text) = 0,
    'technical decision ordering metadata is absent from DTO';
  assert position('submission_id' in r::text) = 0,
    'Submission identity is absent from DTO';
  assert position('candidate_id' in r::text) = 0,
    'Candidate identity is absent from DTO';
  assert position('email_snapshot' in r::text) = 0,
    'Candidate email is absent from DTO';

  -- Canonical eight-state Interviewer presentation mapping.
  foreach status_code in array array[
    'INTERVIEW_SCHEDULING',
    'AWAITING_INTERVIEW',
    'WAITING_FOR_REPORT',
    'REPORT_SUBMITTED',
    'FOLLOW_UP',
    'ON_HOLD',
    'HIRED',
    'REJECTED'
  ]
  loop
    update public.interviews
    set report_status_code = status_code
    where interview_id = current_interview_id;

    r := public.get_interviewer_report_page();
    visible_status := r->'data'->'rounds'->0->>'display_report_status';
    expected_status := case
      when status_code in ('FOLLOW_UP', 'ON_HOLD', 'HIRED')
        then 'REPORT_SUBMITTED'
      else status_code
    end;

    assert visible_status = expected_status,
      'Interviewer status projection matches canonical mapping';

    if status_code in ('HIRED', 'REJECTED') then
      assert not (r->'data'->'rounds'->0->>'can_edit')::boolean,
        'raw final status remains non-writable';
    else
      assert (r->'data'->'rounds'->0->>'can_edit')::boolean,
        'current non-final status remains writable';
    end if;
  end loop;

  update public.interviews
  set report_status_code = 'WAITING_FOR_REPORT'
  where interview_id = current_interview_id;

  -- Both inserts share transaction-stable now(); deterministic UUID DESC must
  -- choose report2 when decision timestamps tie.
  assert (
    select r1.decision_updated_at = r2.decision_updated_at
    from public.interview_reports r1
    join public.interview_reports r2 on r2.interview_report_id = report2
    where r1.interview_report_id = report1
  ), 'fixture starts with equal decision timestamps';

  r := public.get_interviewer_report_page();
  assert (
    r->'data'->'rounds'->0->'preview'->'final_decision'
      ->>'expected_specific_job_assigned'
  ) = 'Newest decision job',
    'equal timestamp tie-break uses interview_report_id DESC';

  -- Test-only metadata setup bypasses exactly the metadata guard; production
  -- trigger semantics remain unchanged. A newer timestamp must outrank UUID.
  execute 'alter table public.interview_reports disable trigger a_report_decision_metadata_guard';
  update public.interview_reports
  set decision_updated_at = timestamptz '2099-01-02 00:00:00+00',
      decision_updated_by = i1
  where interview_report_id = report1;
  update public.interview_reports
  set decision_updated_at = timestamptz '2099-01-01 00:00:00+00',
      decision_updated_by = i2
  where interview_report_id = report2;
  execute 'alter table public.interview_reports enable trigger a_report_decision_metadata_guard';

  r := public.get_interviewer_report_page();
  assert (
    r->'data'->'rounds'->0->'preview'->'final_decision'->>'conclusion'
  ) = 'Primary decision',
    'newer decision timestamp outranks the larger report UUID';

  execute 'alter table public.interview_reports disable trigger a_report_decision_metadata_guard';
  update public.interview_reports
  set decision_updated_at = timestamptz '2099-01-03 00:00:00+00',
      decision_updated_by = i2
  where interview_report_id = report2;
  execute 'alter table public.interview_reports enable trigger a_report_decision_metadata_guard';

  select decision_updated_at into ts
  from public.interview_reports
  where interview_report_id = report2;

  update public.interview_reports
  set necessary_skills = 'Qualitative edit only',
      updated_by = i2
  where interview_report_id = report2;

  assert (
    select decision_updated_at = ts
    from public.interview_reports
    where interview_report_id = report2
  ), 'qualitative-only edit does not move decision timestamp';

  update public.interview_reports
  set expected_specific_job_assigned = null,
      updated_by = i2
  where interview_report_id = report2;

  r := public.get_interviewer_report_page();
  assert (
    r->'data'->'rounds'->0->'preview'->'final_decision'->>'conclusion'
  ) = 'Primary decision',
    'clearing all source decision fields falls back to next eligible report';

  update public.interview_reports
  set conclusion = null,
      expected_specific_job_assigned = null,
      expected_recruitment_time = null,
      updated_by = i1
  where interview_report_id = report1;

  r := public.get_interviewer_report_page();
  assert (
    r->'data'->'rounds'->0->'preview'->'final_decision'->>'conclusion'
  ) is null
  and (
    r->'data'->'rounds'->0->'preview'->'final_decision'
      ->>'expected_specific_job_assigned'
  ) is null
  and (
    r->'data'->'rounds'->0->'preview'->'final_decision'
      ->>'expected_recruitment_time'
  ) is null,
    'no eligible source yields a blank final decision block';

  -- The accepted HR command remains separate, but the owner-only command does
  -- not inherit its broader edit-other authority.
  perform set_config(
    'request.jwt.claims',
    jsonb_build_object('sub', hr_auth::text)::text,
    true
  );
  select version_no into report_version
  from public.interview_reports
  where interview_report_id = report1;

  r := public.save_own_interviewer_report(
    current_p1,
    jsonb_build_object('other_comment', 'HR must not edit through owner command'),
    report_version,
    jsonb_build_object('other_comment', null)
  );
  assert r->>'error_code' = 'FORBIDDEN',
    'HR edit-other authority cannot cross the owner-only command boundary';

  -- Prove state change between a successful read and mutation is revalidated
  -- inside the transactional owner-only command.
  perform set_config(
    'request.jwt.claims',
    jsonb_build_object('sub', i1_auth::text)::text,
    true
  );
  r := public.get_interviewer_report_page();
  assert (r->'data'->'rounds'->0->>'can_edit')::boolean,
    'owner pre-read starts writable';

  update public.interviews
  set report_status_code = 'HIRED'
  where interview_id = current_interview_id;

  select version_no into report_version
  from public.interview_reports
  where interview_report_id = report1;

  r := public.save_own_interviewer_report(
    current_p1,
    jsonb_build_object('strengths_limitations', 'must not save after final state'),
    report_version,
    jsonb_build_object('strengths_limitations', null)
  );
  assert r->>'error_code' = 'FORBIDDEN',
    'mutation-time owner guard rejects a target that became final after pre-read';

  update public.interviews
  set report_status_code = 'WAITING_FOR_REPORT'
  where interview_id = current_interview_id;

  r := public.save_own_interviewer_report(
    old_p1,
    jsonb_build_object('other_comment', 'historical write denied'),
    1,
    jsonb_build_object('other_comment', null)
  );
  assert r->>'error_code' = 'FORBIDDEN',
    'historical participant is not writable through owner-only command';

  select version_no into report_version
  from public.interview_reports
  where interview_report_id = report1;
  r := public.save_own_interviewer_report(
    current_p1,
    jsonb_build_object('strengths_limitations', 'Owner save succeeds'),
    report_version,
    jsonb_build_object('strengths_limitations', null)
  );
  assert (r->>'success')::boolean,
    'current contextual owner may save through owner-only command';

  -- Exact participant removal revokes only that historical round.
  update public.interview_participants
  set is_current = false,
      removed_at = clock_timestamp()
  where interview_participant_id = old_p1;
  r := public.get_interviewer_report_page();
  assert jsonb_array_length(r->'data'->'rounds') = 1,
    'removed participant loses exact historical round access';

  update public.interviews
  set visible_to_interviewers = false
  where interview_id = current_interview_id;
  r := public.get_interviewer_report_page();
  assert jsonb_array_length(r->'data'->'rounds') = 0,
    'hidden current session fails closed';

  update public.interviews
  set visible_to_interviewers = true
  where interview_id = current_interview_id;
  update public.applications
  set is_active = false
  where public.applications.application_id = application_id;
  r := public.get_interviewer_report_page();
  assert jsonb_array_length(r->'data'->'rounds') = 0,
    'inactive Application is inaccessible';

  update public.applications
  set is_active = true
  where public.applications.application_id = application_id;
  update public.interviews
  set is_active = false
  where interview_id = current_interview_id;
  r := public.get_interviewer_report_page();
  assert jsonb_array_length(r->'data'->'rounds') = 0,
    'inactive Interview is inaccessible';

  update public.interviews
  set is_active = true
  where interview_id = current_interview_id;

  insert into public.interview_participants(
    interview_id,
    app_user_id,
    participant_order,
    snapshot_name,
    snapshot_email,
    is_current
  )
  values (
    current_interview_id,
    inactive_user,
    3,
    'S05 Inactive',
    's05_inactive_' || s || '@eiu.edu.vn',
    true
  );
  update public.app_users
  set is_active = false
  where app_user_id = inactive_user;

  perform set_config(
    'request.jwt.claims',
    jsonb_build_object('sub', inactive_auth::text)::text,
    true
  );
  r := public.get_interviewer_report_page();
  assert r->>'error_code' = 'USER_INACTIVE',
    'inactive internal caller fails closed';

  raise notice '=== TASK-S05-001 interviewer report regressions PASS ===';
end;
$$;
