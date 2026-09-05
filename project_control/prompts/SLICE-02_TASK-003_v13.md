# EIU Recruitment — Executor Prompt
## TASK-S02-003 — Private Storage reservation and upload signing protocol
### Prompt version: SLICE-02_TASK-003_v13

## 0. Execution Control

```text
SOURCE_BASELINE: Full Handover v1.17
SOURCE_SHA256: 0b39c3615dd5b34e998527a1d273e0b846458c7bd4170be46c9bb670bfcb3498
BUSINESS_STATUS: Business Logic Core v1.2 = FROZEN
TECHNICAL_STATUS: Technical Architecture v1.17 = TECHNICAL SPECIFICATION FROZEN
TASK_SCOPE: TASK-S02-003 Private Storage reservation and upload signing protocol
WORKTREE: D:/orca/recruitment/TASK-S02-003-storage-reservation
BRANCH: oanhpham-kobe/TASK-S02-003-storage-reservation
BASE_BRANCH: autonomy/continuous-integration-20260905-01
BASE_HEAD: dfac6d1556ff55d7193315d1bf2d3018f1a7d63c
```

---

## 1. Governance & Compact Routing

```yaml
GOVERNANCE:
  pack_version: "1.1"
  SKILLS_REQUIRED:
    - supabase
    - supabase-postgres-best-practices
    - security-review
  SKILLS_RESOLVED:
    - supabase (skills/supabase)
    - supabase-postgres-best-practices (skills/supabase-postgres-best-practices)
    - security-review (skills/security-review)
  SKILLS_APPLIED:
    - supabase: "Storage API bucket management, createSignedUploadUrl signing protocol, storage.objects RLS, worker-only public RPC routing for service_role client, zero URL/token persistence"
    - supabase-postgres-best-practices: "authoring secure RPC functions with search_path='', canonical auth.uid()+candidates lookup distinguishing UNAUTHENTICATED vs USER_INACTIVE, deterministic lock hierarchy (session -> submission -> reservation) preventing deadlocks, atomic FOR UPDATE SKIP LOCKED worker claim with lease recovery (leased_until), post-lock status re-reads, constraints, triggers, idempotency, strict grant revocation from authenticated/anon"
    - security-review: "preventing candidate self-attestation of malware scan status, authoritative scan evidence requiring magic bytes and reservation size limit, quarantine isolation with zero candidate read access, pre-call durable token expiry with latency buffer, deferred cleanup queue with not_before, two-worker claim exclusivity, crash-after-claim lease recovery, EDIT-session target submission NEW invariant enforced under row locks, competing-transition race safety"
  GRAPH_ROUTE: DIRECT_SOURCE_LSP_ONLY
  GRAPH_ROUTE_REASON: "Localized database RPC, storage RLS policies, and server command runner wrappers directly mapped to review pack specifications"
  PRINCIPLE_PROFILE: "STORAGE_SECURITY_AND_DATA_INTEGRITY"
  EVIDENCE_DELTA: "STORAGE-RESERVATION-001"
```

---

## 2. Canonical Source References

- `recruitment_webapp/review_pack/41_STORAGE_AND_UPLOAD_SECURITY.md` (§Approved file policy, §Buckets, §Two-phase protocol, §Candidate staged upload/edit protocol: "Candidate active + Submission NEW for edits... lock parent/session, synchronously re-check")
- `recruitment_webapp/review_pack/49_TECHNICAL_REVIEW_VERCEL_SUPABASE.md` (§3.3 Storage: line 116 "Không sửa/xóa trực tiếp metadata trong storage schema bằng SQL; dùng Storage API", line 117 "Ưu tiên signed URL TTL ngắn, không lưu signed URL dài hạn vào business table")
- `recruitment_webapp/review_pack/37_BACKEND_COMMAND_CONTRACTS.md` (§10 Documents / Storage: `reserve_candidate_form_upload`, `validate_staged_upload`, `stage_candidate_document_change`)
- `recruitment_webapp/review_pack/13_ACCEPTANCE_CRITERIA_AND_TEST_CASES.md` (`AC-UP-01`, `AC-UP-03`, `AC-UP-04`, `AC-UP-05`, `AC-UP-06`, `AC-DOC-TARGET-01`, `AC-DOC-TARGET-02`, `AC-UP-EXP-01`, `AC-FORM-EXP-01`)
- `recruitment_webapp/review_pack/database_schema.sql` (lines 376-444, 799-1017: `upload_reservations`, `candidate_form_document_changes`, `private.validate_candidate_form_document_change`, `private.validate_candidate_form_document_plan`)
- `recruitment_webapp/review_pack/command_registry.yaml` (`reserve_candidate_form_upload`, `stage_candidate_document_change`)

---

## 3. Implementation Specification

### 3.1 Declarative Storage Bucket Provisioning (Storage API / `config.toml`)

- **Rule**: Per `49_TECHNICAL_REVIEW_VERCEL_SUPABASE.md:116`, do NOT write `INSERT INTO storage.buckets` via SQL.
- **Local Dev / Declarative Configuration (`supabase/config.toml`)**:
  Add declarative bucket configuration under `[storage.buckets.candidate-quarantine]`:
  ```toml
  [storage.buckets.candidate-quarantine]
  public = false
  file_size_limit = "5MiB"
  allowed_mime_types = [
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-powerpoint",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "image/png",
    "image/jpeg"
  ]
  ```
- **Storage API Provisioning Helper (`web/src/lib/storage/buckets.ts`)**:
  Provide a trusted setup helper using the Supabase Storage API (`supabase.storage.createBucket('candidate-quarantine', { public: false, fileSizeLimit: 5242880, allowedMimeTypes: [...] })`) for runtime verification and testing environments.

---

### 3.2 Migration File: `supabase/migrations/20260905080000_storage_reservation_and_upload_protocol.sql`

#### 1. Schema Enhancements
- **Add `signed_upload_expires_at` to `public.upload_reservations`**:
  ```sql
  alter table public.upload_reservations
    add column if not exists signed_upload_expires_at timestamptz;

  create index if not exists upload_reservations_signed_expires_idx
    on public.upload_reservations(signed_upload_expires_at)
    where signed_upload_expires_at is not null;
  ```
- **Add `not_before` and `leased_until` to `public.storage_cleanup_queue`**:
  ```sql
  alter table public.storage_cleanup_queue
    add column if not exists not_before timestamptz not null default now(),
    add column if not exists leased_until timestamptz;

  create index if not exists storage_cleanup_queue_claim_idx
    on public.storage_cleanup_queue(not_before, leased_until)
    where status_code in ('PENDING', 'PROCESSING');
  ```

#### 2. `storage.objects` RLS Defense-in-Depth Policies
SQL is used strictly for authoring `storage.objects` RLS policies:
- **Quarantine SELECT Policy (Zero Candidate Access to Unscanned Files)**:
  Quarantined, unscanned files must NOT be readable by candidates. Only trusted background scanner (`service_role` / `postgres`) or root admin can inspect quarantine objects:
  ```sql
  create policy candidate_quarantine_select on storage.objects
    for select to authenticated
    using (
      bucket_id = 'candidate-quarantine'
      and private.is_root_admin()
    );
  ```
- **INSERT RLS Policy (Defense-in-depth with EDIT Submission NEW Invariant)**:
  ```sql
  create policy candidate_quarantine_insert on storage.objects
    for insert to authenticated
    with check (
      bucket_id = 'candidate-quarantine'
      and exists (
        select 1 from public.upload_reservations r
        join public.candidate_form_sessions fs on fs.candidate_form_session_id = r.candidate_form_session_id
        left join public.submissions s on s.submission_id = fs.target_submission_id
        where r.temp_bucket = 'candidate-quarantine'
          and r.temp_path = storage.objects.name
          and r.actor_auth_user_id = (select auth.uid())
          and r.status_code = 'RESERVED'
          and r.expires_at > clock_timestamp()
          and fs.status_code = 'OPEN'
          and fs.expires_at > clock_timestamp()
          and (
            fs.mode_code <> 'EDIT_SUBMISSION'
            or (s.submission_id is not null and s.status_code = 'NEW' and s.candidate_id = fs.candidate_id)
          )
      )
    );
  ```
- **Anti-Tamper Denials**:
  - NO UPDATE policy for `authenticated`: database-level guarantee that existing objects cannot be overwritten, enforcing `upsert: false`.
  - NO DELETE policy for `authenticated`: client cannot delete quarantine objects; cleanup is executed strictly via `public.storage_cleanup_queue`.

---

#### 3. Canonical Candidate Authentication & Inactive Account Check
In each candidate-facing RPC, authentication queries `auth.uid()` first, then queries `public.candidates` where `auth_user_id = v_auth_uid` without filtering on `is_active`, returning `UNAUTHENTICATED` if missing, or `USER_INACTIVE` if candidate account is inactive:
```sql
  -- Candidate authentication & active verification
  v_auth_uid := auth.uid();
  if v_auth_uid is null then
    return jsonb_build_object(
      'success', false,
      'error_code', 'UNAUTHENTICATED',
      'message', 'Candidate authentication required'
    );
  end if;

  select * into v_cand
  from public.candidates
  where auth_user_id = v_auth_uid;

  if not found then
    return jsonb_build_object(
      'success', false,
      'error_code', 'UNAUTHENTICATED',
      'message', 'Candidate authentication required'
    );
  end if;

  if not v_cand.is_active then
    return jsonb_build_object(
      'success', false,
      'error_code', 'USER_INACTIVE',
      'message', 'Candidate account is inactive'
    );
  end if;
```

---

#### 4. Deterministic Lock Hierarchy Across All Mutating RPCs
To prevent deadlocks and eliminate TOCTOU races against concurrent HR transitions (`NEW -> READ`), every mutating RPC MUST acquire row locks in this exact deterministic order:
1. `candidate_form_sessions` (FOR UPDATE)
2. `submissions` (FOR UPDATE, if session `mode_code = 'EDIT_SUBMISSION'`)
3. `upload_reservations` (FOR UPDATE, where applicable)
All status checks are re-evaluated AFTER acquiring these locks.

#### 5. `public.reserve_candidate_form_upload(...)`
- Signature:
  ```sql
  public.reserve_candidate_form_upload(
    p_candidate_form_session_id uuid,
    p_intended_document_type_id uuid,
    p_original_filename text,
    p_declared_mime_type text default null,
    p_expected_max_size_bytes bigint default 5242880,
    p_idempotency_key uuid default gen_random_uuid()
  ) returns jsonb
  ```
- `SECURITY DEFINER SET search_path = ''`.
- **Authentication**: uses §3.3 pattern (returning `UNAUTHENTICATED` if auth/candidate missing, `USER_INACTIVE` if candidate inactive).
- **Idempotency Guard**:
  Checks `upload_reservations` for `actor_auth_user_id = v_auth_uid` and `idempotency_key = p_idempotency_key`. If exists, returns `{ success: true, data: <existing_reservation_json> }`.
- **Lock Ordering & Invariant Checks**:
  1. Lock session row (Lock 1):
     `SELECT mode_code, status_code, expires_at, target_submission_id INTO v_mode, v_status, v_session_expires_at, v_target_sub_id FROM public.candidate_form_sessions WHERE candidate_form_session_id = p_candidate_form_session_id AND candidate_id = v_cand.candidate_id FOR UPDATE`.
     If not found: `{ success: false, error_code: 'NOT_FOUND', message: 'Form session not found' }`.
     If `v_status <> 'OPEN'`: `{ success: false, error_code: 'INVALID_STATE', message: 'Form session is not open' }`.
     If `v_session_expires_at <= clock_timestamp()`: `{ success: false, error_code: 'FORM_SESSION_EXPIRED', message: 'Form session has expired' }`.
  2. If `v_mode = 'EDIT_SUBMISSION'` (Lock 2):
     Lock target submission:
     `SELECT status_code, candidate_id INTO v_sub_status, v_sub_cand_id FROM public.submissions WHERE submission_id = v_target_sub_id FOR UPDATE`.
     Re-verify: if not found or `v_sub_cand_id <> v_cand.candidate_id` or `v_sub_status <> 'NEW'`:
     returns `{ success: false, error_code: 'INVALID_STATE', message: 'Target submission is no longer in editable NEW status' }`.
- **Document Type Validation**:
  Queries `public.document_types WHERE document_type_id = p_intended_document_type_id`.
  If not found: `{ success: false, error_code: 'NOT_FOUND', message: 'Document type not found' }`.
  If `scope_code NOT IN ('SUBMISSION', 'BOTH')`: `{ success: false, error_code: 'INVALID_DOCUMENT_TYPE', message: 'Document type not permitted for submissions' }`.
  If `v_mode = 'NEW_SUBMISSION' AND NOT is_active`: `{ success: false, error_code: 'INACTIVE_DOCUMENT_TYPE', message: 'Inactive document type cannot be added to a new submission' }`.
- **File Properties & Extension Validation**:
  Filename must be non-empty and `char_length <= 255`.
  Extract extension (lower-cased): must be in `('pdf', 'doc', 'docx', 'ppt', 'pptx', 'png', 'jpg', 'jpeg')`.
  Reject executable/archive/script/unapproved extensions (`exe`, `sh`, `bat`, `html`, `svg`, `zip`, etc.) with `{ success: false, error_code: 'INVALID_FILE_TYPE', message: 'File extension is not allowed' }`.
  `expected_max_size_bytes` must be `> 0` and `<= 5242880` (5 MB). If invalid: `{ success: false, error_code: 'FILE_SIZE_EXCEEDED', message: 'File size limit is 5 MB' }`.
- **Reservation Insertion**:
  Generate `v_reservation_id := gen_random_uuid()`.
  `v_temp_bucket := 'candidate-quarantine'`.
  `v_temp_path := format('temp/%s/%s/%s', p_candidate_form_session_id, v_reservation_id, regexp_replace(p_original_filename, '[^a-zA-Z0-9._-]', '_', 'g'))`.
  `v_expires_at := least(clock_timestamp() + interval '30 minutes', v_session_expires_at)`.
  Insert into `public.upload_reservations` with `status_code = 'RESERVED'`, `malware_scan_status = 'PENDING'`.
  Return `{ success: true, data: { upload_reservation_id, candidate_form_session_id, intended_document_type_id, temp_bucket, temp_path, original_filename, declared_mime_type, expected_max_size_bytes, status_code, expires_at } }`.

#### 6. `public.prepare_signed_upload(...)`
- Signature:
  ```sql
  public.prepare_signed_upload(p_upload_reservation_id uuid) returns jsonb
  ```
- `SECURITY DEFINER SET search_path = ''`.
- **Authentication**: uses §3.3 pattern (returning `UNAUTHENTICATED` if auth/candidate missing, `USER_INACTIVE` if candidate inactive).
- **Deterministic Lock Ordering**:
  1. Peek session ID from reservation without lock:
     `SELECT candidate_form_session_id INTO v_session_id FROM public.upload_reservations WHERE upload_reservation_id = p_upload_reservation_id`.
     If not found: `{ success: false, error_code: 'NOT_FOUND', message: 'Upload reservation not found' }`.
  2. Lock session row FIRST (Lock 1):
     `SELECT mode_code, status_code, expires_at, target_submission_id INTO v_mode, v_status, v_session_expires_at, v_target_sub_id FROM public.candidate_form_sessions WHERE candidate_form_session_id = v_session_id AND candidate_id = v_cand.candidate_id FOR UPDATE`.
     If not found or `v_status <> 'OPEN'` or `v_session_expires_at <= clock_timestamp()`:
     returns `{ success: false, error_code: 'INVALID_STATE', message: 'Form session is not open or expired' }`.
  3. If `v_mode = 'EDIT_SUBMISSION'` (Lock 2):
     Lock target submission SECOND:
     `SELECT status_code, candidate_id INTO v_sub_status, v_sub_cand_id FROM public.submissions WHERE submission_id = v_target_sub_id FOR UPDATE`.
     Re-verify: if `v_sub_status <> 'NEW'`:
     returns `{ success: false, error_code: 'INVALID_STATE', message: 'Target submission is no longer in editable NEW status' }`.
  4. Lock reservation THIRD (Lock 3):
     `SELECT status_code, expires_at, temp_bucket, temp_path INTO v_res_status, v_res_expires_at, v_bucket, v_path FROM public.upload_reservations WHERE upload_reservation_id = p_upload_reservation_id AND actor_auth_user_id = v_auth_uid FOR UPDATE`.
     Re-verify: if `v_res_status <> 'RESERVED'` or `v_res_expires_at <= clock_timestamp()`:
     returns `{ success: false, error_code: 'INVALID_STATE', message: 'Reservation is not in reserved state or has expired' }`.
- **Durable Pre-Storage Registration with Latency Buffer**:
  Sets `signed_upload_expires_at = clock_timestamp() + interval '2 hours 5 minutes'` BEFORE returning to caller.
- **Returns Both Expirations**:
  Returns `{ success: true, data: { upload_reservation_id: p_upload_reservation_id, temp_bucket: v_bucket, temp_path: v_path, expires_at: v_res_expires_at, signed_upload_expires_at: clock_timestamp() + interval '2 hours 5 minutes' } }`.

#### 7. `public.record_candidate_upload_completed(...)`
- Signature:
  ```sql
  public.record_candidate_upload_completed(
    p_upload_reservation_id uuid,
    p_actual_size_bytes bigint,
    p_checksum_sha256 text default null
  ) returns jsonb
  ```
- `SECURITY DEFINER SET search_path = ''`.
- **Authentication**: uses §3.3 pattern (returning `UNAUTHENTICATED` if auth/candidate missing, `USER_INACTIVE` if candidate inactive).
- **Deterministic Lock Ordering**:
  1. Peek session ID from reservation:
     `SELECT candidate_form_session_id INTO v_session_id FROM public.upload_reservations WHERE upload_reservation_id = p_upload_reservation_id`.
     If not found: `{ success: false, error_code: 'NOT_FOUND', message: 'Upload reservation not found' }`.
  2. Lock session row FIRST (Lock 1):
     `SELECT mode_code, status_code, expires_at, target_submission_id INTO v_mode, v_status, v_session_expires_at, v_target_sub_id FROM public.candidate_form_sessions WHERE candidate_form_session_id = v_session_id AND candidate_id = v_cand.candidate_id FOR UPDATE`.
     If not found or `v_status <> 'OPEN'` or `v_session_expires_at <= clock_timestamp()`:
     returns `{ success: false, error_code: 'INVALID_STATE', message: 'Form session is not open or expired' }`.
  3. If `v_mode = 'EDIT_SUBMISSION'` (Lock 2):
     Lock target submission SECOND:
     `SELECT status_code FROM public.submissions WHERE submission_id = v_target_sub_id FOR UPDATE`.
     Re-verify: if `status_code <> 'NEW'`:
     returns `{ success: false, error_code: 'INVALID_STATE', message: 'Target submission is no longer in editable NEW status' }`.
  4. Lock reservation THIRD (Lock 3):
     `SELECT status_code, expires_at, expected_max_size_bytes INTO v_res_status, v_res_expires_at, v_expected_max FROM public.upload_reservations WHERE upload_reservation_id = p_upload_reservation_id AND actor_auth_user_id = v_auth_uid FOR UPDATE`.
     Re-verify: if `v_res_status <> 'RESERVED'` or `v_res_expires_at <= clock_timestamp()`:
     returns `{ success: false, error_code: 'INVALID_STATE', message: 'Reservation is not in reserved state or has expired' }`.
  5. Validate size:
     `p_actual_size_bytes > 0 and <= v_expected_max and <= 5242880`. If invalid: `{ success: false, error_code: 'FILE_SIZE_EXCEEDED', message: 'Uploaded file size exceeds reservation limit' }`.
- **Updates Status (Anti-Tamper)**:
  Updates `actual_size_bytes = p_actual_size_bytes`, `checksum_sha256 = p_checksum_sha256`, `status_code = 'UPLOADED'`.
  `malware_scan_status` remains strictly `'PENDING'`.
  Returns `{ success: true, data: { upload_reservation_id: p_upload_reservation_id, status_code: 'UPLOADED', malware_scan_status: 'PENDING' } }`.

#### 8. Trusted Worker Scan & Validation Procedure (ROUTED VIA `public`, WORKER-ONLY GRANTS)
- Signature:
  ```sql
  create or replace function public.validate_and_scan_upload_reservation(
    p_upload_reservation_id uuid,
    p_detected_mime_type text,
    p_actual_size_bytes bigint,
    p_malware_scan_status text,
    p_magic_bytes_verified boolean,
    p_checksum_sha256 text default null
  ) returns jsonb
  language plpgsql
  security definer
  set search_path = ''
  as $$
  ...
  $$;

  revoke all on function public.validate_and_scan_upload_reservation from public, anon, authenticated;
  grant execute on function public.validate_and_scan_upload_reservation to postgres, service_role;
  ```
- **Authoritative Validation Enforcement**:
  - `p_malware_scan_status` has NO default: must be explicitly `'CLEAN'`, `'INFECTED'`, or `'ERROR'`.
  - `p_detected_mime_type` has NO default: must match approved MIME list for the reservation file extension.
  - `p_actual_size_bytes` has NO default: must be `> 0`, `<= r.expected_max_size_bytes`, and `<= 5242880`.
  - Enforces declared MIME compatibility: if `r.declared_mime_type` is present, verifies it is compatible with the file extension.
  - Enforces `p_magic_bytes_verified = true`. If false, rejects with `{ success: false, error_code: 'INVALID_CONTENT_SIGNATURE', message: 'File magic bytes do not match expected signature' }`.
  - Works on reservations in `RESERVED` or `UPLOADED` status.
  - If `p_malware_scan_status = 'CLEAN'`:
    Updates `status_code = 'VALIDATED'`, `detected_mime_type = p_detected_mime_type`, `actual_size_bytes = p_actual_size_bytes`, `checksum_sha256 = coalesce(p_checksum_sha256, r.checksum_sha256)`, `malware_scan_status = 'CLEAN'`.
  - If `p_malware_scan_status in ('INFECTED', 'ERROR')`:
    Updates `status_code = 'REJECTED'`, `malware_scan_status = p_malware_scan_status`, enqueues cleanup into `public.storage_cleanup_queue` with:
    `not_before = greatest(r.expires_at, coalesce(r.signed_upload_expires_at, r.expires_at))`.
  - Returns `{ success: true, data: { upload_reservation_id: p_upload_reservation_id, status_code: v_new_status, malware_scan_status: p_malware_scan_status } }`.

#### 9. `public.stage_candidate_document_change(...)`
- Signature:
  ```sql
  public.stage_candidate_document_change(
    p_candidate_form_session_id uuid,
    p_action_code text,
    p_intended_document_type_id uuid,
    p_upload_reservation_id uuid default null,
    p_target_logical_document_id uuid default null
  ) returns jsonb
  ```
- `SECURITY DEFINER SET search_path = ''`.
- **Authentication**: uses §3.3 pattern (returning `UNAUTHENTICATED` if auth/candidate missing, `USER_INACTIVE` if candidate inactive).
- **Deterministic Lock Ordering**:
  1. Lock session row FIRST (Lock 1):
     `SELECT mode_code, status_code, expires_at, target_submission_id INTO v_mode, v_status, v_session_expires_at, v_target_sub_id FROM public.candidate_form_sessions WHERE candidate_form_session_id = p_candidate_form_session_id AND candidate_id = v_cand.candidate_id FOR UPDATE`.
     If not found or `status_code <> 'OPEN'` or `expires_at <= clock_timestamp()`:
     returns `{ success: false, error_code: 'INVALID_STATE', message: 'Form session is not open or expired' }`.
  2. If `v_mode = 'EDIT_SUBMISSION'` (Lock 2):
     Lock target submission SECOND:
     `SELECT status_code, candidate_id INTO v_sub_status, v_sub_cand_id FROM public.submissions WHERE submission_id = v_target_sub_id FOR UPDATE`.
     Re-verify: if `v_sub_status <> 'NEW'`:
     returns `{ success: false, error_code: 'INVALID_STATE', message: 'Target submission is no longer in editable NEW status' }`.
  3. If `p_upload_reservation_id` provided (Lock 3):
     Lock reservation THIRD:
     `SELECT status_code, expires_at, intended_document_type_id INTO v_res_status, v_res_expires_at, v_res_type FROM public.upload_reservations WHERE upload_reservation_id = p_upload_reservation_id AND candidate_form_session_id = p_candidate_form_session_id FOR UPDATE`.
     Re-verify: must have `v_res_status in ('UPLOADED', 'VALIDATED')`, `v_res_expires_at > clock_timestamp()`, and `v_res_type = p_intended_document_type_id`.
- Action guards:
  - `NEW_SUBMISSION` allows `ADD` only (`REPLACE`/`DELETE` rejected with `INVALID_ACTION`).
  - `ADD` requires `upload_reservation_id` NOT NULL, `target_logical_document_id` NULL.
  - `REPLACE` requires both `upload_reservation_id` and `target_logical_document_id` NOT NULL.
  - `DELETE` requires `upload_reservation_id` NULL, `target_logical_document_id` NOT NULL.
  - For `REPLACE` and `DELETE`, verifies target logical document belongs to session target submission and has exactly 1 current version.
- Inserts into `public.candidate_form_document_changes`.
- Returns `{ success: true, data: { candidate_form_document_change_id, candidate_form_session_id, action_code, intended_document_type_id, upload_reservation_id, target_logical_document_id, status_code } }`.

#### 10. Deferred Cleanup Producers & Atomic Claim / Complete RPCs
- **Update `public.cancel_candidate_form_session`**:
  Update the enqueue query in `cancel_candidate_form_session`:
  ```sql
  insert into public.storage_cleanup_queue (
    source_type,
    source_parent_id,
    source_upload_reservation_id,
    bucket_name,
    object_path,
    reason_code,
    status_code,
    not_before
  )
  select
    'CANDIDATE_FORM',
    p_session_id,
    r.upload_reservation_id,
    r.temp_bucket,
    r.temp_path,
    'SESSION_CANCELLED',
    'PENDING',
    greatest(r.expires_at, coalesce(r.signed_upload_expires_at, r.expires_at))
  from public.upload_reservations r
  where r.candidate_form_session_id = p_session_id
  on conflict (bucket_name, object_path) do update set
    not_before = greatest(storage_cleanup_queue.not_before, excluded.not_before);
  ```
- **Atomic Exclusive Worker Claim RPC with Stale Lease Recovery**:
  ```sql
  create or replace function public.claim_due_storage_cleanup_jobs(
    p_limit integer default 10,
    p_lease_seconds integer default 300
  )
  returns jsonb
  language plpgsql
  security definer
  set search_path = ''
  as $$
  declare
    v_claimed jsonb;
  begin
    with due_rows as (
      select storage_cleanup_id
      from public.storage_cleanup_queue
      where (
        (status_code = 'PENDING' and not_before <= clock_timestamp())
        or (status_code = 'PROCESSING' and leased_until <= clock_timestamp() and attempts < 5)
      )
      order by not_before asc
      limit greatest(1, least(p_limit, 100))
      for update skip locked
    ),
    updated_rows as (
      update public.storage_cleanup_queue q
      set
        status_code = 'PROCESSING',
        leased_until = clock_timestamp() + (greatest(30, least(p_lease_seconds, 3600)) || ' seconds')::interval,
        attempts = q.attempts + 1,
        updated_at = clock_timestamp()
      from due_rows d
      where q.storage_cleanup_id = d.storage_cleanup_id
      returning
        q.storage_cleanup_id,
        q.source_type,
        q.bucket_name,
        q.object_path,
        q.reason_code,
        q.attempts,
        q.not_before,
        q.leased_until
    )
    select coalesce(jsonb_agg(to_jsonb(u)), '[]'::jsonb)
    into v_claimed
    from updated_rows u;

    return jsonb_build_object(
      'success', true,
      'data', v_claimed
    );
  end;
  $$;

  revoke all on function public.claim_due_storage_cleanup_jobs from public, anon, authenticated;
  grant execute on function public.claim_due_storage_cleanup_jobs to postgres, service_role;
  ```
- **Worker Job Completion / Failure RPC**:
  ```sql
  create or replace function public.complete_storage_cleanup_job(
    p_storage_cleanup_id uuid,
    p_success boolean,
    p_error text default null
  )
  returns jsonb
  language plpgsql
  security definer
  set search_path = ''
  as $$
  begin
    if p_success then
      update public.storage_cleanup_queue
      set
        status_code = 'DONE',
        leased_until = null,
        last_error = null,
        updated_at = clock_timestamp()
      where storage_cleanup_id = p_storage_cleanup_id;
    else
      update public.storage_cleanup_queue
      set
        last_error = p_error,
        status_code = case when attempts >= 5 then 'ERROR' else 'PENDING' end,
        not_before = case when attempts < 5 then clock_timestamp() + interval '5 minutes' else not_before end,
        leased_until = null,
        updated_at = clock_timestamp()
      where storage_cleanup_id = p_storage_cleanup_id;
    end if;

    return jsonb_build_object('success', true);
  end;
  $$;

  revoke all on function public.complete_storage_cleanup_job from public, anon, authenticated;
  grant execute on function public.complete_storage_cleanup_job to postgres, service_role;
  ```

#### 11. Triggers and Helper Functions from Canonical Blueprint
- `private.validate_candidate_form_document_change()` trigger function and `candidate_form_document_change_guard` trigger on `public.candidate_form_document_changes` (lines 799-880 in `database_schema.sql`).
- `private.validate_candidate_form_document_plan(p_candidate_form_session_id uuid)` authoritative plan validator (lines 884-1016 in `database_schema.sql`).

---

### 3.3 Web Command Layer: `web/src/lib/commands/storage-reservation.ts`

- Implement typed commands using `createCommandRunner`:
  1. `reserveCandidateFormUpload(input, deps)`:
     Invokes `public.reserve_candidate_form_upload` RPC. Returns reservation data.
  2. `createSignedUploadUrlForReservation(input, deps)`:
     - Input: `{ uploadReservationId: string }`.
     - Calls `public.prepare_signed_upload` RPC to lock rows in deterministic order and record `signed_upload_expires_at` BEFORE calling Supabase Storage API.
     - Derives `bucket` and `path` EXCLUSIVELY from the returned verified reservation data.
     - Calls `supabase.storage.from(data.temp_bucket).createSignedUploadUrl(data.temp_path, { upsert: false })`.
     - Maps `data.expires_at` explicitly to `expiresAt` and `data.signed_upload_expires_at` to `signedUploadExpiresAt`.
     - Returns `{ signedUrl, path, token, expiresAt, signedUploadExpiresAt }`.
     - **Zero Persistence / Logging**: Signed URLs or tokens are never persisted in database tables, audit logs, or server logs.
  3. `recordCandidateUploadCompleted(input, deps)`:
     Invokes `public.record_candidate_upload_completed`.
  4. `stageCandidateDocumentChange(input, deps)`:
     Invokes `public.stage_candidate_document_change`.
  5. `validateAndScanUploadReservation(input, deps)`:
     Invokes `public.validate_and_scan_upload_reservation` via service role client (trusted backend worker path only; requires authoritative scan result, detected MIME, magic bytes verified flag, and size check).
  6. `claimDueStorageCleanupJobs(limit, leaseSeconds, supabaseServiceClient)`:
     Invokes `public.claim_due_storage_cleanup_jobs` via service role client.
  7. `completeStorageCleanupJob(id, success, error, supabaseServiceClient)`:
     Invokes `public.complete_storage_cleanup_job` via service role client.
- Type definitions, input validation schemas, error mapping to `CommandErrorCode`.

---

### 3.4 Verification Tests: `web/src/__tests__/storage-reservation.test.ts`

- Test suite verifying:
  1. `UNAUTHENTICATED` call rejection (missing auth.uid or no candidate identity row)
  2. `USER_INACTIVE` candidate rejection (candidate row exists but is_active = false)
  3. `NOT_FOUND` / foreign session access rejection
  4. `FORM_SESSION_EXPIRED` rejection
  5. `INVALID_STATE` (closed session) rejection
  6. `INVALID_DOCUMENT_TYPE` / `INACTIVE_DOCUMENT_TYPE` rejection
  7. `INVALID_FILE_TYPE` (disallowed extensions .exe, .sh, .html) rejection
  8. `FILE_SIZE_EXCEEDED` (> 5MB) rejection
  9. `IDEMPOTENT_RESERVATION` duplicate key returns existing reservation
  10. `SIGNED_UPLOAD_URL_DERIVATION`: signed upload URL derives bucket/path strictly from owned unexpired reservation; caller-supplied path is impossible; upsert is false; zero URL/token persistence; records `signed_upload_expires_at` before token issuance and returns `expiresAt`.
  11. `LATENCY_BUFFER_IN_DURABLE_EXPIRY`: `signed_upload_expires_at` is set with buffer (`clock_timestamp() + interval '2 hours 5 minutes'`) to cover signing delay.
  12. `REAL_ORDERING_CANCEL_EARLY_CLEANUP_LATE_UPLOAD`:
      - Reservation created, signed upload prepared (`signed_upload_expires_at = now() + 2h 5m`).
      - Session cancelled: `storage_cleanup_queue` row enqueued with `not_before = now() + 2h 5m`.
      - Early cleanup execution at T+5min: claims 0 rows because `not_before > now()` (early cleanup deferred).
      - Late upload completion attempt at T+10min: `recordCandidateUploadCompleted` fails with `INVALID_STATE` (session cancelled).
      - Due cleanup query at `clock_timestamp() >= not_before` successfully claims row for physical deletion.
  13. `CANDIDATE_QUARANTINE_READ_DENIED`: candidate cannot SELECT / read objects from `candidate-quarantine` (fails RLS); only root admin or trusted service role can read.
  14. `CANDIDATE_CANNOT_SELF_ATTEST_SCAN_CLEAN`: authenticated candidate calling `recordCandidateUploadCompleted` leaves `malware_scan_status = 'PENDING'`; direct execution of `public.validate_and_scan_upload_reservation` by `authenticated` role fails with permission denied (revoked); direct update of `upload_reservations` by authenticated candidate is rejected by grants/RLS.
  15. `AUTHORITATIVE_SCAN_EVIDENCE_REQUIRED`: `validate_and_scan_upload_reservation` fails if malware status is omitted, if detected MIME does not match approved extension whitelist, if magic bytes are not verified, or if size exceeds `expected_max_size_bytes` (tested directly against `RESERVED` path).
  16. `STORAGE_RLS_CANCELLED_SESSION_DENIAL`: direct INSERT into `storage.objects` fails if parent form session is cancelled or expired, even if reservation row is unexpired.
  17. `STORAGE_RLS_NO_OVERWRITE`: authenticated caller cannot overwrite an existing object (no UPDATE policy).
  18. `STAGING_ADD` validates unexpired reservation in `UPLOADED` or `VALIDATED` state.
  19. `STAGING_REPLACE_DELETE_IN_NEW_SUBMISSION` rejection
  20. `STAGING_UNREADY_OR_EXPIRED_RESERVATION` rejection
  21. `SUBMIT_PLAN_VALIDATION_REQUIRES_CLEAN`: plan validation fails if reservation is not `VALIDATED` + `CLEAN`.
  22. `EDIT_SESSION_SUBMISSION_NO_LONGER_NEW_DENIAL`: when a target submission transitions from `NEW` to `READ`, `reserve_candidate_form_upload`, `prepare_signed_upload`, `record_candidate_upload_completed`, `stage_candidate_document_change`, and direct `storage.objects` INSERT are all rejected with `INVALID_STATE` / RLS denial.
  23. `COMPETING_TRANSITION_CONCURRENCY_TEST`: competing transition test executing deterministic lock sequence (session -> submission -> reservation) verifying safe serialization without deadlocks against concurrent HR status transition.
  24. `TWO_WORKER_CLEANUP_EXCLUSIVITY_TEST`: concurrent calls to `public.claim_due_storage_cleanup_jobs` via service role claim disjoint sets via `FOR UPDATE SKIP LOCKED` without double-claiming.
  25. `CRASH_AFTER_CLAIM_LEASE_RECOVERY_TEST`: simulated worker crash leaving a row in `PROCESSING` with expired `leased_until` is automatically reclaimed by next worker, processed, and marked `DONE` via `complete_storage_cleanup_job`.

---

## 4. Acceptance & Verification Contract

1. `npm run typecheck` in `web/` PASS with 0 errors.
2. `npm run lint` in `web/` PASS with 0 errors.
3. `npm run build` in `web/` PASS.
4. `npm run test` in `web/` PASS (all existing + new tests green).
5. Clean local migration replay test on ephemeral test port PASS.
6. Secret scan PASS.
7. Git diff clean, exactly one commit on `oanhpham-kobe/TASK-S02-003-storage-reservation`.
