-- TASK-S06-001 R4: master_data.manage can read active and inactive managed lookup rows.
\set ON_ERROR_STOP on

begin;

insert into public.app_users(auth_user_id, email, full_name, is_active)
values (gen_random_uuid(), 's06001_read_manager_' || substr(gen_random_uuid()::text,1,8) || '@eiu.edu.vn', 'S06 Read Manager', true)
returning app_user_id as manager_id, auth_user_id as manager_auth \gset

insert into public.app_user_permissions(app_user_id, permission_code)
values (:'manager_id'::uuid, 'master_data.manage');

insert into public.app_users(auth_user_id, email, full_name, is_active)
values (gen_random_uuid(), 's06001_read_none_' || substr(gen_random_uuid()::text,1,8) || '@eiu.edu.vn', 'S06 Read No Permission', true)
returning app_user_id as no_perm_id, auth_user_id as no_perm_auth \gset

insert into public.recruitment_sources(code, name_vi, is_active)
values
  ('S06001_READ_SRC_ACTIVE_' || substr(gen_random_uuid()::text,1,8), 'Active source', true),
  ('S06001_READ_SRC_INACTIVE_' || substr(gen_random_uuid()::text,1,8), 'Inactive source', false)
returning code \gset src_

-- Use separately captured codes because INSERT ... RETURNING + \gset only supports one row.
delete from public.recruitment_sources where code in (:'src_code');

select 'S06001_READ_' || substr(gen_random_uuid()::text,1,8) as suffix \gset

insert into public.recruitment_sources(code, name_vi, is_active)
values
  ('SRC_ACTIVE_' || :'suffix', 'Active source', true),
  ('SRC_INACTIVE_' || :'suffix', 'Inactive source', false);

insert into public.document_types(code, name_vi, scope_code, is_active)
values
  ('DOC_ACTIVE_' || :'suffix', 'Active document', 'SUBMISSION', true),
  ('DOC_INACTIVE_' || :'suffix', 'Inactive document', 'SUBMISSION', false);

insert into public.qualification_levels(code, name_vi, is_active)
values
  ('QUAL_ACTIVE_' || :'suffix', 'Active qualification', true),
  ('QUAL_INACTIVE_' || :'suffix', 'Inactive qualification', false);

select set_config('request.jwt.claims', jsonb_build_object('sub', :'manager_auth')::text, true);
set local role authenticated;

do $$
begin
  assert (select count(*) from public.recruitment_sources where code in ('SRC_ACTIVE_' || current_setting('s06.test_suffix', true), 'SRC_INACTIVE_' || current_setting('s06.test_suffix', true))) = 2;
end;
$$;

reset role;
rollback;
