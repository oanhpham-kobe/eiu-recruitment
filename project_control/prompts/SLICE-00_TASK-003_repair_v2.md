# EIU Recruitment — Executor Repair Prompt
## TASK-S00-003 — Close Infrastructure Acceptance Evidence via Deep Local Migration Replay
### Prompt version: SLICE-00_TASK-003_repair_v2

## 0. Execution Control

```text
SOURCE_BASELINE: Full Handover v1.17
SOURCE_SHA256: 0b39c3615dd5b34e998527a1d273e0b846458c7bd4170be46c9bb670bfcb3498
BUSINESS_STATUS: Business Logic Core v1.2 = FROZEN
TECHNICAL_STATUS: Technical Architecture v1.17 = TECHNICAL SPECIFICATION FROZEN
TASK_SCOPE: TASK-S00-003 Evidence Repair Only
WORKTREE: D:/orca/recruitment/TASK-S00-003-dev-infra
BRANCH: oanhpham-kobe/TASK-S00-003-dev-infra
```

---

## 1. Role & Boundary

You are the Coding Executor for the evidence repair of:
```text
TASK-S00-003: DEV infrastructure local clean migration replay verification
```

### Authorized Scope
The Executor is authorized to perform:
1. Disposable unlinked local Supabase replay in a temporary directory outside git.
2. SQL assertions validating extensions, privileges, and trigger execution.
3. Update and commit the following four files exclusively:
   - `project_control/EVIDENCE_INDEX.yaml`
   - `project_control/CURRENT_STATE.md`
   - `project_control/TASK_REGISTRY.yaml`
   - `project_control/prompts/SLICE-00_TASK-003_repair_v2.md`

### Non-Goals
- Do NOT modify tracked `supabase/config.toml` inside the task worktree.
- Do NOT copy or retain `supabase/.temp` in the disposable replay directory (must remain unlinked).
- Do NOT output secret keys (anon key, service role key) to logs or stdout.
- Do NOT run `supabase db reset --linked`.
- Do NOT start TASK-S00-004, TASK-S00-005, or SLICE-01.
- Do NOT deploy to Vercel or mutate production infrastructure.
- Do NOT touch application code in `web/` beyond existing verified scaffold.

---

## 2. Execution Procedure

1. **Create Strictly Unlinked Disposable Temp Environment with Trap Cleanup**:
   - Create a temporary directory outside git: `REPLAY_DIR=$(mktemp -d -t supabase-repair-XXXXXX)`
   - Set up bash trap to guarantee cleanup on any exit:
     ```bash
     trap 'cd "D:/orca/recruitment"; if [ -n "$REPLAY_DIR" ] && [ -d "$REPLAY_DIR" ]; then (cd "$REPLAY_DIR" && npx supabase stop --no-backup > /dev/null 2>&1 || true); rm -rf "$REPLAY_DIR"; fi' EXIT
     ```
   - Copy ONLY `config.toml` and `migrations/` from `D:/orca/recruitment/TASK-S00-003-dev-infra/supabase`:
     ```bash
     mkdir -p "$REPLAY_DIR/supabase/migrations"
     cp "D:/orca/recruitment/TASK-S00-003-dev-infra/supabase/config.toml" "$REPLAY_DIR/supabase/config.toml"
     cp "D:/orca/recruitment/TASK-S00-003-dev-infra/supabase/migrations/"*.sql "$REPLAY_DIR/supabase/migrations/"
     ```
   - Assert `test ! -d "$REPLAY_DIR/supabase/.temp"` to prove no linked state, project-ref, or remote credentials exist in replay workdir.
   - In `$REPLAY_DIR/supabase/config.toml`, configure `project_id = "eiu-recruitment-repair"` and remap ports to non-conflicting 5642x range:
     - `api.port = 56421`
     - `db.port = 56422`
     - `db.shadow_port = 56420`
     - `db.pooler.port = 56429`
     - `studio.port = 56423`
     - `inbucket.port = 56424`
     - `analytics.port = 56427`

2. **Run Clean Replay (Suppress Secret Output)**:
   - Change directory to `$REPLAY_DIR`.
   - Start Supabase suppressing secret-bearing output:
     ```bash
     npx supabase start > /dev/null 2>&1
     ```
   - Reset local DB from scratch:
     ```bash
     npx supabase db reset
     ```

3. **Execute SQL Privilege and Trigger Assertions**:
   Connect to `supabase_db_eiu-recruitment-repair` via `docker exec` using `psql -v ON_ERROR_STOP=1`:

   - **Assertion A (Extensions in schema extensions)**:
     ```sql
     DO $$
     DECLARE
       v_count int;
     BEGIN
       SELECT count(*) INTO v_count
       FROM pg_extension e JOIN pg_namespace n ON e.extnamespace = n.oid 
       WHERE n.nspname = 'extensions' AND extname IN ('pgcrypto', 'citext', 'pg_trgm', 'unaccent');
       IF v_count <> 4 THEN
         RAISE EXCEPTION 'Assertion A failed: expected 4 extensions in schema extensions, found %', v_count;
       END IF;
     END;
     $$;
     ```

   - **Assertion B (Privilege Invariants: PUBLIC grantee=0 check and role privileges)**:
     ```sql
     DO $$
     DECLARE
       v_pub_schema_count int;
       v_pub_func_count int;
     BEGIN
       -- Verify zero grants to PUBLIC (grantee OID 0) on schema private
       SELECT count(*) INTO v_pub_schema_count
       FROM (SELECT (aclexplode(nspacl)).* FROM pg_namespace WHERE nspname = 'private') a
       WHERE grantee = 0;
       IF v_pub_schema_count <> 0 THEN
         RAISE EXCEPTION 'Assertion B failed: schema private has % grants to PUBLIC, expected 0', v_pub_schema_count;
       END IF;

       -- Verify zero grants to PUBLIC (grantee OID 0) on function private.touch_version
       SELECT count(*) INTO v_pub_func_count
       FROM (SELECT (aclexplode(proacl)).* FROM pg_proc WHERE proname = 'touch_version' AND pronamespace = 'private'::regnamespace) a
       WHERE grantee = 0;
       IF v_pub_func_count <> 0 THEN
         RAISE EXCEPTION 'Assertion B failed: function private.touch_version has % grants to PUBLIC, expected 0', v_pub_func_count;
       END IF;

       -- Verify anon and authenticated roles have NO usage/execute
       IF has_schema_privilege('anon', 'private', 'USAGE') THEN
         RAISE EXCEPTION 'Assertion B failed: anon has USAGE on schema private';
       END IF;
       IF has_schema_privilege('authenticated', 'private', 'USAGE') THEN
         RAISE EXCEPTION 'Assertion B failed: authenticated has USAGE on schema private';
       END IF;
       IF has_function_privilege('anon', 'private.touch_version()', 'EXECUTE') THEN
         RAISE EXCEPTION 'Assertion B failed: anon has EXECUTE on private.touch_version()';
       END IF;
       IF has_function_privilege('authenticated', 'private.touch_version()', 'EXECUTE') THEN
         RAISE EXCEPTION 'Assertion B failed: authenticated has EXECUTE on private.touch_version()';
       END IF;

       -- Verify postgres and service_role DO have usage/execute
       IF NOT has_schema_privilege('postgres', 'private', 'USAGE') THEN
         RAISE EXCEPTION 'Assertion B failed: postgres lacks USAGE on schema private';
       END IF;
       IF NOT has_schema_privilege('service_role', 'private', 'USAGE') THEN
         RAISE EXCEPTION 'Assertion B failed: service_role lacks USAGE on schema private';
       END IF;
       IF NOT has_function_privilege('postgres', 'private.touch_version()', 'EXECUTE') THEN
         RAISE EXCEPTION 'Assertion B failed: postgres lacks EXECUTE on private.touch_version()';
       END IF;
       IF NOT has_function_privilege('service_role', 'private.touch_version()', 'EXECUTE') THEN
         RAISE EXCEPTION 'Assertion B failed: service_role lacks EXECUTE on private.touch_version()';
       END IF;
     END;
     $$;
     ```

   - **Assertion C (Trigger Execution via top-level autocommit statements and sentinel timestamp)**:
     ```sql
     CREATE TABLE public._test_touch (
       id serial primary key,
       name text,
       version_no integer default 0 not null,
       updated_at timestamptz default now() not null
     );
     CREATE TRIGGER trg_test_touch
       BEFORE UPDATE ON public._test_touch
       FOR EACH ROW EXECUTE FUNCTION private.touch_version();

     -- Step 1: Insert initial row with explicit old sentinel timestamp
     INSERT INTO public._test_touch (name, version_no, updated_at)
     VALUES ('initial', 0, '2000-01-01 00:00:00+00');

     -- Step 2: Top-level autocommit UPDATE 1
     UPDATE public._test_touch SET name = 'v1';

     -- Step 3: Assert version_no = 1 and updated_at was replaced by trigger with current time
     DO $$
     DECLARE
       v_rec record;
     BEGIN
       SELECT version_no, updated_at INTO v_rec FROM public._test_touch WHERE name = 'v1';
       IF v_rec.version_no <> 1 THEN
         RAISE EXCEPTION 'Assertion C failed: version_no after update 1 is %, expected 1', v_rec.version_no;
       END IF;
       IF v_rec.updated_at <= '2000-01-01 00:00:00+00'::timestamptz THEN
         RAISE EXCEPTION 'Assertion C failed: updated_at was not updated past sentinel';
       END IF;
     END;
     $$;

     -- Step 4: Top-level autocommit UPDATE 2
     UPDATE public._test_touch SET name = 'v2';

     -- Step 5: Assert version_no = 2
     DO $$
     DECLARE
       v_rec record;
     BEGIN
       SELECT version_no INTO v_rec FROM public._test_touch WHERE name = 'v2';
       IF v_rec.version_no <> 2 THEN
         RAISE EXCEPTION 'Assertion C failed: version_no after update 2 is %, expected 2', v_rec.version_no;
       END IF;
     END;
     $$;

     DROP TABLE public._test_touch CASCADE;
     ```

4. **Tear Down Disposable Environment**:
   - `npx supabase stop --no-backup > /dev/null 2>&1`
   - Remove `$REPLAY_DIR`.

5. **Update Evidence & Commit**:
   - In `D:/orca/recruitment/TASK-S00-003-dev-infra/project_control/EVIDENCE_INDEX.yaml` under `DEV-INFRA-001`, update `local_clean_migration_replay` to record:
     `PASS (verified via unlinked disposable local Supabase clean reset on Docker Desktop Linux engine; extensions pgcrypto, citext, pg_trgm, unaccent confirmed in extensions schema; zero PUBLIC grants via aclexplode grantee=0; anon/authenticated usage and execute denied; postgres/service_role usage and execute granted; private.touch_version() trigger execution verified across top-level updates replacing sentinel timestamp and incrementing version_no 0->1->2; local and remote migrations converge at 20260904164112)`
   - Update `project_control/CURRENT_STATE.md` with matching evidence.
   - Reconcile `project_control/TASK_REGISTRY.yaml`:
     - Bind `active_prompt: project_control/prompts/SLICE-00_TASK-003_repair_v2.md`
     - Record AC-12 as PASS (unlinked disposable clean replay verified)
     - Record LOCAL_CLEAN_MIGRATION_REPLAY as PASS
   - Track this prompt file: `project_control/prompts/SLICE-00_TASK-003_repair_v2.md`
   - Commit on branch `oanhpham-kobe/TASK-S00-003-dev-infra` with commit message:
     `fix(TASK-S00-003): record deep local migration replay privilege and trigger verification`

---

## 3. Acceptance Criteria

- All 3 executable SQL assertion blocks (Extensions, Privilege Invariants with aclexplode grantee=0, Trigger Execution with sentinel timestamp check) PASS with zero errors.
- Disposable runtime stopped; zero residual replay containers or temp files (guaranteed by trap).
- No project ref or linked state present during local replay (`supabase/.temp` excluded).
- No secrets or credentials printed to stdout or committed.
- Tracked `supabase/config.toml` in task worktree remains byte-identical to committed HEAD.
- Exactly the 4 authorized files updated and committed on `oanhpham-kobe/TASK-S00-003-dev-infra`.
