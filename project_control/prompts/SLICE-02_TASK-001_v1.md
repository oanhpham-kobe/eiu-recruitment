# EIU Recruitment — Executor Prompt
## TASK-S02-001 — Candidate Form Session, Privacy Notice & Upload Reservation Schema Migration
### Prompt version: SLICE-02_TASK-001_v1

## 0. Execution Control

```text
SOURCE_BASELINE: Full Handover v1.17
SOURCE_SHA256: 0b39c3615dd5b34e998527a1d273e0b846458c7bd4170be46c9bb670bfcb3498
BUSINESS_STATUS: Business Logic Core v1.2 = FROZEN
TECHNICAL_STATUS: Technical Architecture v1.17 = TECHNICAL SPECIFICATION FROZEN
TASK_SCOPE: TASK-S02-001 Candidate Form & Submission Schema Migration Only
WORKTREE: D:/orca/recruitment/TASK-S02-001-candidate-schema
BRANCH: oanhpham-kobe/TASK-S02-001-candidate-schema
BASE_BRANCH: autonomy/continuous-integration-20260905-01
BASE_HEAD: 07d1030f767d4ee1d067d60ce971e42f9881a3ab
```

---

## 1. Role & Boundary

You are the Coding Executor for:
```text
TASK-S02-001: Candidate Form Session, Privacy Notice & Upload Reservation schema migration
```

### Scope & Principles
This task creates the foundational schema for SLICE-02 (*Candidate Form / Submission / Privacy / Documents*) per review pack 12, 37, 40, 41, and 59.
No Submission is created merely by opening a form; staged form sessions and upload reservations manage draft lifecycle cleanly.

### Authorized Scope
The Executor is authorized to perform:
1. Create ordered migration file `supabase/migrations/20260905060000_candidate_form_and_submission_schema.sql` defining:
   - Master data: `public.recruitment_sources`, `public.document_types`, `public.qualification_levels`.
   - Privacy notices: `public.privacy_notice_versions` (with `one_current_privacy_notice_uq`), `public.privacy_acknowledgements`.
   - Submissions & children: `public.submissions` (with `submission_updater_ck`), `public.submission_education`, `public.submission_work_experiences`, `public.submission_activities`.
   - Document logicals & physicals: `public.submission_document_logicals` (with `one_submission_logical_creator_ck`), `public.submission_documents` (with `submission_current_logical_document_uq` and MIME/size check).
   - Form sessions & upload reservations: `public.candidate_form_sessions` (with `candidate_form_target_ck`), `public.upload_reservations` (with `upload_reservation_parent_ck`), `public.candidate_form_document_changes`, `public.storage_cleanup_queue`.
   - Triggers: attach `private.touch_version()` to `submissions`, `candidate_form_sessions`.
   - Row Level Security: enable RLS on all created tables with strict minimal grants (candidate own-record access; HR permission-based access; direct DML revoked).
2. Execute unlinked disposable local clean migration replay in a temporary directory outside git:
   - Assert all tables, columns, indexes, and check constraints created cleanly.
   - Assert check constraints reject invalid inserts (e.g. `candidate_form_target_ck`, `one_current_privacy_notice_uq`, `upload_reservation_parent_ck`).
   - Assert RLS policies deny unauthorized access (`anon` denied direct access; candidates isolated to own records).
3. Update project-control records (`EVIDENCE_INDEX.yaml`, `CURRENT_STATE.md`, `TASK_REGISTRY.yaml`, and track this prompt) with status `REVIEW` (pending independent review).
4. Commit all changes cleanly on `oanhpham-kobe/TASK-S02-001-candidate-schema`.

### Non-Goals
- Do NOT mark TASK-S02-001 as `DONE` in this commit. Per `TASK_EXECUTION_LIFECYCLE.md` and `REVIEWER_CONTRACT.md`, the Executor records `status: REVIEW`; the `DONE` transition is reserved for the Planner after an independent implementation review PASS.
- Do NOT implement transactional submission commands (those belong to TASK-S02-002, S02-003, S02-004).
- Do NOT implement application form UI screens (that belongs to TASK-S02-005).
- Do NOT deploy to Vercel or mutate external databases (`--linked` is forbidden).
- Do NOT modify tracked `supabase/config.toml` in the task worktree.
- Do NOT commit `.env.local` or any secrets/keys.

---

## 2. Canonical Source References

- `recruitment_webapp/review_pack/database_schema.sql` (lines 69–101 master data; lines 231–343 submissions and logical documents; lines 345–430 privacy notices, candidate form sessions, upload reservations; lines 704–711 privacy acknowledgements)
- `recruitment_webapp/review_pack/40_DATABASE_INVARIANTS.md` (§Candidate Form Session invariants, §Upload Reservation invariants, §Privacy notice pinning invariants, §Submission invariants)
- `recruitment_webapp/review_pack/39_SECURITY_RLS_MATRIX.md` (§Read/Write matrix for candidate form sessions, upload reservations, submissions, documents)
- `recruitment_webapp/review_pack/59_RLS_POLICY_BLUEPRINT.md` (§Candidate temporary-resource and logical-document policies, §Candidate row, §Submission)

---

## 3. Implementation Specification

### 3.1 Migration File: `supabase/migrations/20260905060000_candidate_form_and_submission_schema.sql`

```sql
-- App Tuyển dụng EIU — Candidate Form & Submission Schema Migration
-- Slice 02 / TASK-S02-001: Master data, Privacy notices, Form sessions, Upload reservations, Submissions, Documents

-- 1. Master Data
create table if not exists public.recruitment_sources (
  recruitment_source_id uuid primary key default gen_random_uuid(),
  code text not null unique,
  name_vi text not null,
  name_en text,
  is_active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  version_no bigint not null default 1
);

create table if not exists public.document_types (
  document_type_id uuid primary key default gen_random_uuid(),
  code text not null unique,
  name_vi text not null,
  name_en text,
  scope_code text not null check (scope_code in ('SUBMISSION','INTERVIEW','BOTH')),
  is_active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  version_no bigint not null default 1
);

create table if not exists public.qualification_levels (
  qualification_id uuid primary key default gen_random_uuid(),
  code text not null unique,
  name_vi text not null,
  name_en text,
  is_active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  version_no bigint not null default 1
);

-- 2. Privacy Notices
create table if not exists public.privacy_notice_versions (
  notice_version text primary key,
  content_vi text not null,
  content_en text,
  content_hash_sha256 text not null check (content_hash_sha256 ~ '^[0-9A-Fa-f]{64}$'),
  published_at timestamptz not null default now(),
  effective_from timestamptz not null default now(),
  is_current boolean not null default false,
  created_by uuid references public.app_users(app_user_id) on delete restrict
);

create unique index if not exists one_current_privacy_notice_uq
  on public.privacy_notice_versions ((is_current))
  where is_current = true;

-- 3. Submissions & Children
create table if not exists public.submissions (
  submission_id uuid primary key default gen_random_uuid(),
  candidate_id uuid not null references public.candidates(candidate_id) on delete restrict,
  status_code text not null default 'NEW' check (status_code in ('NEW','READ','PROCESSED','DONE','CLOSED')),
  full_name text not null,
  date_of_birth date not null,
  gender_code text not null check (gender_code in ('MALE','FEMALE')),
  current_address text not null,
  phone text not null,
  email_snapshot extensions.citext not null,
  recruitment_source_id uuid references public.recruitment_sources(recruitment_source_id) on delete restrict,
  other_info text,
  hr_note text,
  submitted_at timestamptz not null default now(),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  updated_by_internal_user_id uuid references public.app_users(app_user_id) on delete restrict,
  updated_by_candidate_id uuid references public.candidates(candidate_id) on delete restrict,
  version_no bigint not null default 1,
  constraint submission_updater_ck check (
    (updated_by_internal_user_id is not null)::int + (updated_by_candidate_id is not null)::int <= 1
  )
);

create index if not exists submissions_candidate_idx on public.submissions(candidate_id, submitted_at desc);
create index if not exists submissions_status_idx on public.submissions(status_code, submitted_at desc);

create table if not exists public.submission_education (
  education_id uuid primary key default gen_random_uuid(),
  submission_id uuid not null references public.submissions(submission_id) on delete cascade,
  sort_order integer not null default 1 check (sort_order > 0),
  period_text text,
  qualification_id uuid references public.qualification_levels(qualification_id) on delete restrict,
  major text,
  institution text
);

create table if not exists public.submission_work_experiences (
  experience_id uuid primary key default gen_random_uuid(),
  submission_id uuid not null references public.submissions(submission_id) on delete cascade,
  sort_order integer not null default 1 check (sort_order > 0),
  start_date date,
  end_date date,
  is_current boolean not null default false,
  employer text,
  job_title text,
  job_description text
);

create table if not exists public.submission_activities (
  activity_id uuid primary key default gen_random_uuid(),
  submission_id uuid not null references public.submissions(submission_id) on delete cascade,
  sort_order integer not null default 1 check (sort_order > 0),
  period_text text,
  activity_name text,
  role_name text,
  organizer text,
  description text
);

-- 4. Document Management
create table if not exists public.submission_document_logicals (
  logical_document_id uuid primary key default gen_random_uuid(),
  submission_id uuid not null references public.submissions(submission_id) on delete cascade,
  document_type_id uuid not null references public.document_types(document_type_id) on delete restrict,
  created_at timestamptz not null default now(),
  created_by_candidate_id uuid references public.candidates(candidate_id) on delete restrict,
  created_by_app_user_id uuid references public.app_users(app_user_id) on delete restrict,
  constraint one_submission_logical_creator_ck check (
    (created_by_candidate_id is not null)::int + (created_by_app_user_id is not null)::int = 1
  )
);

create table if not exists public.submission_documents (
  document_id uuid primary key default gen_random_uuid(),
  logical_document_id uuid not null references public.submission_document_logicals(logical_document_id) on delete cascade,
  storage_bucket text not null,
  storage_path text not null unique,
  original_filename text not null check (char_length(original_filename) <= 255),
  mime_type text not null check (mime_type in (
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-powerpoint',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'image/png','image/jpeg'
  )),
  file_size_bytes bigint not null check (file_size_bytes > 0 and file_size_bytes <= 5242880),
  checksum_sha256 text check (checksum_sha256 is null or checksum_sha256 ~ '^[0-9A-Fa-f]{64}$'),
  malware_scan_status text not null default 'CLEAN' check (malware_scan_status = 'CLEAN'),
  exif_stripped boolean,
  version_no integer not null default 1 check (version_no > 0),
  is_current boolean not null default true,
  uploaded_by_candidate_id uuid references public.candidates(candidate_id) on delete restrict,
  uploaded_by_app_user_id uuid references public.app_users(app_user_id) on delete restrict,
  uploaded_at timestamptz not null default now(),
  constraint one_document_uploader_ck check (
    (uploaded_by_candidate_id is not null)::int + (uploaded_by_app_user_id is not null)::int = 1
  ),
  unique(logical_document_id, version_no)
);

create unique index if not exists submission_current_logical_document_uq
  on public.submission_documents(logical_document_id)
  where is_current = true;

-- 5. Staged Form Sessions & Upload Reservations
create table if not exists public.candidate_form_sessions (
  candidate_form_session_id uuid primary key default gen_random_uuid(),
  candidate_id uuid not null references public.candidates(candidate_id) on delete cascade,
  mode_code text not null check (mode_code in ('NEW_SUBMISSION','EDIT_SUBMISSION')),
  target_submission_id uuid references public.submissions(submission_id) on delete cascade,
  base_submission_version_no bigint,
  presented_privacy_notice_version text not null references public.privacy_notice_versions(notice_version) on delete restrict,
  status_code text not null default 'OPEN' check (status_code in ('OPEN','SUBMITTED','CANCELLED','EXPIRED')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  expires_at timestamptz not null,
  constraint candidate_form_target_ck check (
    (mode_code = 'NEW_SUBMISSION' and target_submission_id is null and base_submission_version_no is null)
    or (mode_code = 'EDIT_SUBMISSION' and target_submission_id is not null and base_submission_version_no is not null)
  )
);

create table if not exists public.upload_reservations (
  upload_reservation_id uuid primary key default gen_random_uuid(),
  candidate_form_session_id uuid references public.candidate_form_sessions(candidate_form_session_id) on delete cascade,
  interview_id uuid,
  intended_document_type_id uuid not null references public.document_types(document_type_id) on delete restrict,
  temp_bucket text not null,
  temp_path text not null unique,
  original_filename text not null check (char_length(original_filename) <= 255),
  declared_mime_type text,
  detected_mime_type text,
  expected_max_size_bytes bigint not null default 5242880 check (expected_max_size_bytes > 0 and expected_max_size_bytes <= 5242880),
  actual_size_bytes bigint,
  checksum_sha256 text check (checksum_sha256 is null or checksum_sha256 ~ '^[0-9A-Fa-f]{64}$'),
  malware_scan_status text not null default 'PENDING' check (malware_scan_status in ('PENDING','CLEAN','INFECTED','ERROR')),
  status_code text not null default 'RESERVED' check (status_code in ('RESERVED','UPLOADED','VALIDATED','FINALIZED','EXPIRED','REJECTED','CANCELLED')),
  actor_auth_user_id uuid not null,
  idempotency_key uuid not null,
  created_at timestamptz not null default now(),
  expires_at timestamptz not null,
  constraint upload_reservation_parent_ck check (
    (candidate_form_session_id is not null)::int + (interview_id is not null)::int = 1
  ),
  unique(actor_auth_user_id, idempotency_key)
);

create table if not exists public.candidate_form_document_changes (
  candidate_form_document_change_id uuid primary key default gen_random_uuid(),
  candidate_form_session_id uuid not null references public.candidate_form_sessions(candidate_form_session_id) on delete cascade,
  action_code text not null check (action_code in ('ADD','REPLACE','DELETE')),
  target_logical_document_id uuid references public.submission_document_logicals(logical_document_id) on delete restrict,
  upload_reservation_id uuid references public.upload_reservations(upload_reservation_id) on delete set null,
  document_type_id uuid references public.document_types(document_type_id) on delete restrict,
  created_at timestamptz not null default now()
);

create table if not exists public.storage_cleanup_queue (
  storage_cleanup_id uuid primary key default gen_random_uuid(),
  source_type text not null check (source_type in ('CANDIDATE_FORM','INTERVIEW_UPLOAD')),
  source_parent_id uuid,
  source_upload_reservation_id uuid,
  bucket_name text not null,
  object_path text not null,
  reason_code text not null,
  status_code text not null default 'PENDING' check (status_code in ('PENDING','PROCESSING','DONE','ERROR')),
  attempts integer not null default 0 check (attempts >= 0),
  last_error text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique(bucket_name, object_path)
);

create table if not exists public.privacy_acknowledgements (
  privacy_acknowledgement_id uuid primary key default gen_random_uuid(),
  submission_id uuid not null references public.submissions(submission_id) on delete cascade,
  notice_version text not null references public.privacy_notice_versions(notice_version) on delete restrict,
  acknowledged_at timestamptz not null default now(),
  source_code text not null default 'CANDIDATE_PORTAL',
  unique(submission_id, notice_version)
);

-- 6. Triggers
create trigger submissions_touch_version
  before update on public.submissions
  for each row execute function private.touch_version();

create trigger candidate_form_sessions_touch_version
  before update on public.candidate_form_sessions
  for each row execute function private.touch_version();

-- 7. Row Level Security
alter table public.recruitment_sources enable row level security;
alter table public.document_types enable row level security;
alter table public.qualification_levels enable row level security;
alter table public.privacy_notice_versions enable row level security;
alter table public.submissions enable row level security;
alter table public.submission_education enable row level security;
alter table public.submission_work_experiences enable row level security;
alter table public.submission_activities enable row level security;
alter table public.submission_document_logicals enable row level security;
alter table public.submission_documents enable row level security;
alter table public.candidate_form_sessions enable row level security;
alter table public.upload_reservations enable row level security;
alter table public.candidate_form_document_changes enable row level security;
alter table public.storage_cleanup_queue enable row level security;
alter table public.privacy_acknowledgements enable row level security;

-- Read policies
create policy privacy_notice_read on public.privacy_notice_versions
  for select using (is_current = true or private.is_root_admin());

create policy candidate_form_sessions_candidate_select on public.candidate_form_sessions
  for select using (candidate_id = private.current_candidate_id() or private.is_root_admin());

create policy upload_reservations_select on public.upload_reservations
  for select using (actor_auth_user_id = auth.uid() or private.is_root_admin());

create policy submissions_select on public.submissions
  for select using (candidate_id = private.current_candidate_id() or private.has_permission('submissions.view'));

create policy submission_education_select on public.submission_education
  for select using (exists (select 1 from public.submissions s where s.submission_id = submission_education.submission_id and (s.candidate_id = private.current_candidate_id() or private.has_permission('submissions.view'))));

create policy submission_work_experiences_select on public.submission_work_experiences
  for select using (exists (select 1 from public.submissions s where s.submission_id = submission_work_experiences.submission_id and (s.candidate_id = private.current_candidate_id() or private.has_permission('submissions.view'))));

create policy submission_activities_select on public.submission_activities
  for select using (exists (select 1 from public.submissions s where s.submission_id = submission_activities.submission_id and (s.candidate_id = private.current_candidate_id() or private.has_permission('submissions.view'))));

create policy submission_document_logicals_select on public.submission_document_logicals
  for select using (exists (select 1 from public.submissions s where s.submission_id = submission_document_logicals.submission_id and (s.candidate_id = private.current_candidate_id() or private.has_permission('submissions.view'))));

create policy submission_documents_select on public.submission_documents
  for select using (exists (select 1 from public.submission_document_logicals l join public.submissions s on s.submission_id = l.submission_id where l.logical_document_id = submission_documents.logical_document_id and (s.candidate_id = private.current_candidate_id() or private.has_permission('submissions.view'))));

-- Revoke direct DML from client roles
revoke insert, update, delete on public.submissions, public.candidate_form_sessions, public.upload_reservations, public.submission_documents, public.privacy_acknowledgements from anon, authenticated;
grant select on public.recruitment_sources, public.document_types, public.qualification_levels, public.privacy_notice_versions to anon, authenticated;
grant select on public.candidate_form_sessions, public.upload_reservations, public.submissions, public.submission_education, public.submission_work_experiences, public.submission_activities, public.submission_document_logicals, public.submission_documents to authenticated;
```

### 3.2 Unlinked Disposable Replay Verification
- Setup disposable temporary directory outside git with bash trap cleanup.
- Copy `config.toml` and `migrations/` only (assert no `.temp`).
- Configure non-conflicting 5642x ports and `project_id = "eiu-recruitment-replay"`.
- Run `npx supabase start` and `npx supabase db reset`.
- Execute SQL assertions testing:
  1. All 14 tables exist with correct columns and check constraints.
  2. `one_current_privacy_notice_uq` rejects two concurrent `is_current = true` rows.
  3. `candidate_form_target_ck` rejects NEW_SUBMISSION with non-null target_submission_id.
  4. `upload_reservation_parent_ck` rejects row with both session_id and interview_id null.
  5. `touch_version` triggers increment version_no on update.
  6. RLS policies deny unauthorized access (`anon` denied direct submission access; candidate isolated to own submissions/sessions).
- Clean teardown of disposable runtime.

---

## 4. Acceptance Criteria

1. Migration applies cleanly on top of existing migrations.
2. All SQL assertion groups PASS in disposable replay verification with zero errors.
3. Disposable runtime cleanly stopped; zero residual containers or temp files.
4. `npm run typecheck`, `npm run lint`, `npm run build`, and `npm test` PASS.
5. Zero secrets or credentials committed.
6. `project_control/EVIDENCE_INDEX.yaml` updated under `FORM-SCHEMA-001` with assertion results.
7. `project_control/CURRENT_STATE.md` and `project_control/TASK_REGISTRY.yaml` updated with `status: REVIEW` (pending independent review), with prompt SHA-256 bound.
8. Exactly one clean commit on `oanhpham-kobe/TASK-S02-001-candidate-schema`.
