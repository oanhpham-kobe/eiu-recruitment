\set ON_ERROR_STOP on
begin;
do $$ declare v_actor uuid:='00000000-0000-0000-0000-000000008202'::uuid; v_result jsonb; v_before bigint; v_after bigint; begin
  assert not pg_catalog.has_function_privilege('authenticated','public.reserve_interview_upload(uuid,uuid)','EXECUTE');
  assert not pg_catalog.has_function_privilege('authenticated','public.finalize_interview_upload(uuid,uuid,text,text,text,text,bigint,text,integer)','EXECUTE');
  assert pg_catalog.has_function_privilege('service_role','public.reserve_interview_upload(uuid,uuid)','EXECUTE');
  assert pg_catalog.has_function_privilege('service_role','public.finalize_interview_upload(uuid,uuid,text,text,text,text,bigint,text,integer)','EXECUTE');
  assert not pg_catalog.has_function_privilege('authenticated','public.reserve_interview_upload_rate_limited(uuid,text,text,uuid,uuid)','EXECUTE');
  assert not pg_catalog.has_function_privilege('authenticated','public.finalize_interview_upload_rate_limited(uuid,text,text,uuid,uuid,text,text,text,text,bigint,text,integer)','EXECUTE');
  select pg_catalog.count(*) into v_before from private.rate_limit_buckets;
  v_result:=public.reserve_interview_upload_rate_limited(v_actor,pg_catalog.repeat('a',64),pg_catalog.repeat('b',64),'00000000-0000-0000-0000-000000008203'::uuid,'00000000-0000-0000-0000-000000008204'::uuid);
  assert v_result->>'error_code' in ('UNAUTHENTICATED','FORBIDDEN');
  select pg_catalog.count(*) into v_after from private.rate_limit_buckets; assert v_after=v_before;
  assert pg_catalog.pg_get_functiondef('public.reserve_interview_upload_rate_limited(uuid,text,text,uuid,uuid)'::regprocedure) ~ $re$'limit'[[:space:]]*,[[:space:]]*30$re$;
  assert pg_catalog.pg_get_functiondef('public.finalize_interview_upload_rate_limited(uuid,text,text,uuid,uuid,text,text,text,text,bigint,text,integer)'::regprocedure) ~ $re$'limit'[[:space:]]*,[[:space:]]*100$re$;
end $$;
rollback;
