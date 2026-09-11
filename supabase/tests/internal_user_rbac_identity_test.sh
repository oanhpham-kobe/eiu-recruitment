#!/usr/bin/env bash
set -euo pipefail

container_name="supabase_db_eiu-recruitment-dev"
part1="supabase/tests/internal_user_rbac_identity_test.part1.sql"
part2="supabase/tests/internal_user_rbac_identity_test.part2.sql"

# The canonical candidates table requires an auth_user_id. The focused fixture
# uses one deterministic candidate-only UUID; the SQL parts stay byte-contiguous
# and are patched only at the fixture boundary before execution.
cat "$part1" "$part2" \
  | sed \
      -e "s/insert into public.candidates(candidate_id,email,current_full_name,is_active)/insert into public.candidates(candidate_id,auth_user_id,email,current_full_name,is_active)/" \
      -e "s/values(v_candidate,'candidate_s06_002@example.com'/values(v_candidate,'73000000-0000-0000-0000-000000000001','candidate_s06_002@example.com'/" \
  | docker exec -i "$container_name" psql -v ON_ERROR_STOP=1 -U postgres -d postgres
