-- TASK-S08-002 — Interview upload durable rate-limit boundaries.
revoke execute on function public.reserve_interview_upload(uuid, uuid) from public, anon, authenticated;
grant execute on function public.reserve_interview_upload(uuid, uuid) to postgres, service_role;
revoke execute on function public.finalize_interview_upload(uuid, uuid, text, text, text, text, bigint, text, integer) from public, anon, authenticated;
grant execute on function public.finalize_interview_upload(uuid, uuid, text, text, text, text, bigint, text, integer) to postgres, service_role;

create or replace function public.reserve_interview_upload_rate_limited(
  p_actor_auth_user_id uuid, p_identity_key_digest text, p_trusted_ip_key_digest text,
  p_interview_id uuid, p_document_type_id uuid
) returns jsonb language plpgsql security definer set search_path = '' as $$
declare v_previous_sub text; v_actor uuid; v_limit jsonb; v_result jsonb;
begin
  if coalesce(p_identity_key_digest,'') !~ '^[0-9a-f]{64}$' or coalesce(p_trusted_ip_key_digest,'') !~ '^[0-9a-f]{64}$' then return pg_catalog.jsonb_build_object('success',false,'error_code','RATE_LIMIT_UNAVAILABLE'); end if;
  v_previous_sub:=pg_catalog.current_setting('request.jwt.claim.sub',true); perform pg_catalog.set_config('request.jwt.claim.sub',p_actor_auth_user_id::text,true);
  v_actor:=private.interview_command_actor('interviews.documents');
  if v_actor is null or (not private.is_root_admin() and not private.has_permission('interviews.manage')) then perform pg_catalog.set_config('request.jwt.claim.sub',coalesce(v_previous_sub,''),true); return pg_catalog.jsonb_build_object('success',false,'error_code',case when v_actor is null then 'UNAUTHENTICATED' else 'FORBIDDEN' end); end if;
  begin v_limit:=public.consume_rate_limit_rules('UPLOAD',pg_catalog.jsonb_build_array(pg_catalog.jsonb_build_object('ruleCode','IDENTITY_15M','keyDigest',p_identity_key_digest,'limit',30,'windowSeconds',900),pg_catalog.jsonb_build_object('ruleCode','IP_15M','keyDigest',p_trusted_ip_key_digest,'limit',100,'windowSeconds',900))); exception when others then perform pg_catalog.set_config('request.jwt.claim.sub',coalesce(v_previous_sub,''),true); return pg_catalog.jsonb_build_object('success',false,'error_code','RATE_LIMIT_UNAVAILABLE'); end;
  if coalesce((v_limit->>'allowed')::boolean,false) is not true then perform pg_catalog.set_config('request.jwt.claim.sub',coalesce(v_previous_sub,''),true); return pg_catalog.jsonb_build_object('success',false,'error_code','RATE_LIMITED','data',pg_catalog.jsonb_build_object('retry_after_seconds',coalesce((v_limit->>'retryAfterSeconds')::integer,1))); end if;
  v_result:=public.reserve_interview_upload(p_interview_id,p_document_type_id); perform pg_catalog.set_config('request.jwt.claim.sub',coalesce(v_previous_sub,''),true); return v_result;
exception when others then perform pg_catalog.set_config('request.jwt.claim.sub',coalesce(v_previous_sub,''),true); raise; end; $$;
revoke all on function public.reserve_interview_upload_rate_limited(uuid,text,text,uuid,uuid) from public, anon, authenticated;
grant execute on function public.reserve_interview_upload_rate_limited(uuid,text,text,uuid,uuid) to postgres, service_role;

create or replace function public.finalize_interview_upload_rate_limited(
  p_actor_auth_user_id uuid, p_identity_key_digest text, p_trusted_ip_key_digest text,
  p_reservation_id uuid, p_logical_document_id_or_null uuid, p_storage_bucket text,
  p_storage_path text, p_original_filename text, p_mime_type text, p_file_size_bytes bigint,
  p_checksum_sha256 text, p_expected_logical_version_or_null integer
) returns jsonb language plpgsql security definer set search_path = '' as $$
declare v_previous_sub text; v_actor uuid; v_limit jsonb; v_result jsonb;
begin
  if coalesce(p_identity_key_digest,'') !~ '^[0-9a-f]{64}$' or coalesce(p_trusted_ip_key_digest,'') !~ '^[0-9a-f]{64}$' then return pg_catalog.jsonb_build_object('success',false,'error_code','RATE_LIMIT_UNAVAILABLE'); end if;
  v_previous_sub:=pg_catalog.current_setting('request.jwt.claim.sub',true); perform pg_catalog.set_config('request.jwt.claim.sub',p_actor_auth_user_id::text,true);
  v_actor:=private.interview_command_actor('interviews.documents');
  if v_actor is null or (not private.is_root_admin() and not private.has_permission('interviews.manage')) then perform pg_catalog.set_config('request.jwt.claim.sub',coalesce(v_previous_sub,''),true); return pg_catalog.jsonb_build_object('success',false,'error_code',case when v_actor is null then 'UNAUTHENTICATED' else 'FORBIDDEN' end); end if;
  begin v_limit:=public.consume_rate_limit_rules('UPLOAD',pg_catalog.jsonb_build_array(pg_catalog.jsonb_build_object('ruleCode','IDENTITY_15M','keyDigest',p_identity_key_digest,'limit',30,'windowSeconds',900),pg_catalog.jsonb_build_object('ruleCode','IP_15M','keyDigest',p_trusted_ip_key_digest,'limit',100,'windowSeconds',900))); exception when others then perform pg_catalog.set_config('request.jwt.claim.sub',coalesce(v_previous_sub,''),true); return pg_catalog.jsonb_build_object('success',false,'error_code','RATE_LIMIT_UNAVAILABLE'); end;
  if coalesce((v_limit->>'allowed')::boolean,false) is not true then perform pg_catalog.set_config('request.jwt.claim.sub',coalesce(v_previous_sub,''),true); return pg_catalog.jsonb_build_object('success',false,'error_code','RATE_LIMITED','data',pg_catalog.jsonb_build_object('retry_after_seconds',coalesce((v_limit->>'retryAfterSeconds')::integer,1))); end if;
  v_result:=public.finalize_interview_upload(p_reservation_id,p_logical_document_id_or_null,p_storage_bucket,p_storage_path,p_original_filename,p_mime_type,p_file_size_bytes,p_checksum_sha256,p_expected_logical_version_or_null); perform pg_catalog.set_config('request.jwt.claim.sub',coalesce(v_previous_sub,''),true); return v_result;
exception when others then perform pg_catalog.set_config('request.jwt.claim.sub',coalesce(v_previous_sub,''),true); raise; end; $$;
revoke all on function public.finalize_interview_upload_rate_limited(uuid,text,text,uuid,uuid,text,text,text,text,bigint,text,integer) from public, anon, authenticated;
grant execute on function public.finalize_interview_upload_rate_limited(uuid,text,text,uuid,uuid,text,text,text,text,bigint,text,integer) to postgres, service_role;
