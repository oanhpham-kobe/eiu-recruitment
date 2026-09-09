-- TASK-S05-001: Interviewer contextual report read projection regressions.
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
  report1 uuid;
  report2 uuid;
  r jsonb;
  visible_status text;
  status_code text;
  expected_status text;
  ts timestamptz;
begin
  raise notice '=== TASK-S05-001 interviewer report contextual read ===';

  assert not has_function_privilege(
    'anon',
    'public.get_interviewer_report_page()',
    'EXECUTE'
  ), 'anon must not execute interviewer report RPC';
  assert has_function_privilege(
    'authenticated',
    'public.get_interviewer_report_page()',
    'EXECUTE'
  ), 'authenticated role may invoke the per-user RPC';

  assert not has_schema_privilege(
    'anon',
    'interviewer_report_private',
    'USAGE'
  ), 'anon must not resolve the privileged helper schema';
  assert has_schema_privilege(
    'authenticated',
    'interviewer_report_private',
    'USAGE'
  ), 'authenticated wrapper may resolve the bounded helper schema';
  assert not (
    select p.prosecdef
    from pg_proc p
    join pg_namespace n on n.oid = p.pronamespace
    where n.nspname = 'public'
      and p.proname = 'get_interviewer_report_page'
  ), 'public API wrapper must remain SECURITY INVOKER';
  assert (
    select p.prosecdef
    from pg_proc p
    join pg_namespace n on n.oid = p.pronamespace
    where n.nspname = 'interviewer_report_private'
      and p.proname = 'get_interviewer_report_page_impl'
  ), 'privileged implementation stays outside exposed schemas';

  insert into public.organizational_units(code, name_vi, name_en)
  values ('S05001_U_' || s, 'Đơn vị S05', 'S05 Unit')
  returning public.organizational_units.unit_id into unit_id;

  insert into public.position_groups(code, name_vi, name_en)
  values ('S05001_PG_' || s, 'Nhóm S05', 'S05 Group')
  returning public.position_groups.position_group_id into position_group_id;

  insert into public.positions(
    unit_id, position_group_id, code, name_vi, name_en
  )
  values (
    unit_id, position_group_id, 'S05001_P_' || s,
    'Giảng viên S05', 'S05 Lecturer'
  )
  returning public.positions.position_id into position_id;

  insert into public.app_users(auth_user_id, full_name, email, is_active)
  values (
    hr_auth, 'S05 HR', 's05_hr_' || s || '@eiu.edu.vn', true
  )
  returning public.app_users.app_user_id into hr;

  insert into public.app_users(
    auth_user_id, full_name, email, job_title, is_active
  )
  values (
    i1_auth, 'S05 Interviewer One',
    's05_i1_' || s || '@eiu.edu.vn', 'Lecturer', true
  )
  returning public.app_users.app_user_id into i1;

  insert into public.app_users(
    auth_user_id, full_name, email, job_title, is_active
  )
  values (
    i2_auth, 'S05 Interviewer Two',
    's05_i2_' || s || '@eiu.edu.vn', 'Professor', true
  )
  returning public.app_users.app_user_id into i2;

  insert into public.app_users(
    auth_user_id, full_name, email, is_active
  )
  values (
    inactive_auth, 'S05 Inactive',
    's05_inactive_' || s || '@eiu.edu.vn', true
  )
  returning public.app_users.app_user_id into inactive_user;

  insert into public.candidates(auth_user_id, email, is_active)
  values (
    candidate_auth, 's05_candidate_' || s || '@example.com', true
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
    submission_id, unit_id, position_id, hr_owner_id, is_active
  )
  values (
    submission_id, unit_id, position_id, hr, true
  )
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
    application_id, 1, 'AVAILABLE', 'REPORT_SUBMITTED', true, true
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
    application_id, 2, 'AVAILABLE', 'WAITING_FOR_REPORT', true, true
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
  returning public.interview_participants.interview_participant_id into old_p1;

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
  returning public.interview_participants.interview_participant_id into current_p1;

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
  returning public.interview_participants.interview_participant_id into current_p2;

  -- The accepted decision trigger uses transaction-stable now(). Seed ordered
  -- UUIDs so equal timestamps deterministically exercise the UUID tie-break.
  report1 := (
    '10000000-0000-4000-8000-' || substr(md5(s || ':decision-source'), 1, 12)
  )::uuid;
  report2 := (
    '20000000-0000-4000-8000-' || substr(md5(s || ':decision-source'), 1, 12)
  )::uuid;

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
    'Tie-break decision job',
    i2,
    i2
  );

  -- Anonymous request has no authenticated identity even when called by the
  -- test owner role.
  perform set_config('request.jwt.claims', '{}'::jsonb::text, true);
  r := public.get_interviewer_report_page();
  assert r->>'error_code' = 'UNAUTHENTICATED',
    'missing auth identity fails closed';

  -- Candidate authentication is not internal Interviewer authorization.
  perform set_config(
    'request.jwt.claims',
    jsonb_build_object('sub', candidate_auth::text)::text,
    true
  );
  r := public.get_interviewer_report_page();
  assert r->>'error_code' = 'FORBIDDEN',
    'candidate identity cannot consume interviewer report projection';

  -- Another active internal user who participates only in the current round
  -- gets no transitive access to the historical round/Application context.
  perform set_config(
    'request.jwt.claims',
    jsonb_build_object('sub', i2_auth::text)::text,
    true
  );
  r := public.get_interviewer_report_page();
  assert (r->>'success')::boolean,
    'authorized internal participant request succeeds';
  assert jsonb_array_length(r->'data'->'rounds') = 1,
    'interviewer two sees only their directly participated round';

  -- Interviewer one participated in both exact rounds and may read both.
  perform set_config(
    'request.jwt.claims',
    jsonb_build_object('sub', i1_auth::text)::text,
    true
  );
  r := public.get_interviewer_report_page();
  assert (r->>'success')::boolean, 'interviewer read succeeds';
  assert jsonb_array_length(r->'data'->'rounds') = 2,
    'new current round does not revoke directly participated historical read';
  assert (r->'data'->'rounds'->0->>'is_current_round')::boolean,
    'current round is server-derived and sorted before historical round';
  assert not (r->'data'->'rounds'->1->>'is_current_round')::boolean,
    'older participated round remains historical read-only';
  assert not (r->'data'->'rounds'->1->>'can_edit')::boolean,
    'historical round is never writable';

  -- The returned DTO contains no HR-only or technical Final Decision Source
  -- metadata. These keys must be absent at the server boundary, not UI-hidden.
  assert position('hr_report_note' in r::text) = 0,
    'HR report note is absent from DTO';
  assert position('hr_owner' in r::text) = 0,
    'HR owner identity/control is absent from DTO';
  assert position('decision_updated_by' in r::text) = 0,
    'technical decision actor metadata is absent from DTO';
  assert position('decision_updated_at' in r::text) = 0,
    'technical source ordering metadata is absent from DTO';
  assert position('submission_id' in r::text) = 0,
    'unrelated Submission identity is absent from DTO';
  assert position('candidate_id' in r::text) = 0,
    'unrelated Candidate identity is absent from DTO';
  assert position('email_snapshot' in r::text) = 0,
    'unrelated Candidate email is absent from DTO';

  -- Canonical eight-state Interviewer projection. The raw status remains in
  -- the Interview row and is never serialized by the RPC.
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
    where public.interviews.interview_id = test.current_interview_id;

    r := public.get_interviewer_report_page();
    visible_status := r->'data'->'rounds'->0->>'display_report_status';
    expected_status := case
      when status_code in ('FOLLOW_UP', 'ON_HOLD', 'HIRED')
        then 'REPORT_SUBMITTED'
      else status_code
    end;

    assert visible_status = expected_status,
      'Interviewer status projection must match canonical mapping';

    if status_code in ('HIRED', 'REJECTED') then
      assert not (r->'data'->'rounds'->0->>'can_edit')::boolean,
        'raw final status remains non-writable even when display is masked';
    else
      assert (r->'data'->'rounds'->0->>'can_edit')::boolean,
        'current non-final status remains writable';
    end if;

    assert position('"HIRED"' in r::text) = 0 or status_code <> 'HIRED',
      'raw HIRED must not leak as Interviewer lifecycle state';
  end loop;

  -- Restore a writable state for the remaining checks.
  update public.interviews
  set report_status_code = 'REPORT_SUBMITTED'
  where public.interviews.interview_id = test.current_interview_id;

  r := public.get_interviewer_report_page();
  assert jsonb_array_length(
    r->'data'->'rounds'->0->'preview'->'participants'
  ) = 2, 'current preview renders all current participants';

  assert (
    r->'data'->'rounds'->0->'preview'->'final_decision'
      ->>'expected_specific_job_assigned'
  ) = 'Tie-break decision job',
    'equal decision timestamps use deterministic interview_report_id DESC tie-break';

  -- Controlled test metadata isolates timestamp ordering without changing the
  -- production trigger semantics. Newer timestamp must outrank a higher UUID.
  update public.interview_reports
  set decision_updated_at = clock_timestamp() + interval '1 second'
  where public.interview_reports.interview_report_id = test.report1;

  r := public.get_interviewer_report_page();
  assert (
    r->'data'->'rounds'->0->'preview'->'final_decision'->>'conclusion'
  ) = 'Primary decision',
    'newer decision timestamp outranks UUID tie-break';

  update public.interview_reports
  set decision_updated_at = clock_timestamp() - interval '1 second'
  where public.interview_reports.interview_report_id = test.report1;
  update public.interview_reports
  set decision_updated_at = clock_timestamp()
  where public.interview_reports.interview_report_id = test.report2;

  r := public.get_interviewer_report_page();
  assert (
    r->'data'->'rounds'->0->'preview'->'final_decision'
      ->>'expected_specific_job_assigned'
  ) = 'Tie-break decision job',
    'controlled timestamp fixture restores report two as latest source';

  select decision_updated_at into ts
  from public.interview_reports
  where public.interview_reports.interview_report_id = test.report2;

  update public.interview_reports
  set necessary_skills = 'Qualitative edit only',
      updated_by = i2
  where public.interview_reports.interview_report_id = test.report2;

  assert (
    select decision_updated_at = ts
    from public.interview_reports
    where public.interview_reports.interview_report_id = test.report2
  ), 'qualitative-only edit does not move decision timestamp';

  update public.interview_reports
  set expected_specific_job_assigned = null,
      updated_by = i2
  where public.interview_reports.interview_report_id = test.report2;

  r := public.get_interviewer_report_page();
  assert (
    r->'data'->'rounds'->0->'preview'->'final_decision'
      ->>'conclusion'
  ) = 'Primary decision',
    'clearing all source decision fields falls back to next eligible report';

  update public.interview_reports
  set conclusion = null,
      expected_specific_job_assigned = null,
      expected_recruitment_time = null,
      updated_by = i1
  where public.interview_reports.interview_report_id = test.report1;

  r := public.get_interviewer_report_page();
  assert (
    r->'data'->'rounds'->0->'preview'->'final_decision'
      ->>'conclusion'
  ) is null
  and (
    r->'data'->'rounds'->0->'preview'->'final_decision'
      ->>'expected_specific_job_assigned'
  ) is null
  and (
    r->'data'->'rounds'->0->'preview'->'final_decision'
      ->>'expected_recruitment_time'
  ) is null, 'no eligible source yields a blank decision block';

  -- Removing the exact participant revokes that round only.
  update public.interview_participants
  set is_current = false,
      removed_at = clock_timestamp()
  where public.interview_participants.interview_participant_id = test.old_p1;

  r := public.get_interviewer_report_page();
  assert jsonb_array_length(r->'data'->'rounds') = 1,
    'removed participant loses access to that exact historical round';

  -- Hiding the current session revokes current read without deleting history.
  update public.interviews
  set visible_to_interviewers = false
  where public.interviews.interview_id = test.current_interview_id;

  r := public.get_interviewer_report_page();
  assert jsonb_array_length(r->'data'->'rounds') = 0,
    'hidden session fails closed at read projection';

  update public.interviews
  set visible_to_interviewers = true
  where public.interviews.interview_id = test.current_interview_id;

  -- Inactive Application and Interview independently fail closed.
  update public.applications set is_active = false
  where public.applications.application_id = test.application_id;
  r := public.get_interviewer_report_page();
  assert jsonb_array_length(r->'data'->'rounds') = 0,
    'inactive parent Application is inaccessible';

  update public.applications set is_active = true
  where public.applications.application_id = test.application_id;
  update public.interviews set is_active = false
  where public.interviews.interview_id = test.current_interview_id;
  r := public.get_interviewer_report_page();
  assert jsonb_array_length(r->'data'->'rounds') = 0,
    'inactive Interview is inaccessible';

  update public.interviews set is_active = true
  where public.interviews.interview_id = test.current_interview_id;

  -- Inactive internal identity fails before any contextual rows are returned.
  -- Assign while active (participant lifecycle correctly rejects inactive users),
  -- then deactivate the user to prove the read RPC fails closed.
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
  where public.app_users.app_user_id = test.inactive_user;

  perform set_config(
    'request.jwt.claims',
    jsonb_build_object('sub', inactive_auth::text)::text,
    true
  );
  r := public.get_interviewer_report_page();
  assert r->>'error_code' = 'USER_INACTIVE',
    'inactive internal caller fails closed';

  raise notice '=== TASK-S05-001 interviewer report contextual read PASS ===';
end;
$$;
