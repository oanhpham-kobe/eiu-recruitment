#!/usr/bin/env bash
set -euo pipefail

container_name="supabase_db_eiu-recruitment-dev"
part1="supabase/tests/internal_user_rbac_identity_test.part1.sql"
part2="supabase/tests/internal_user_rbac_identity_test.part2.sql"

cat "$part1" "$part2" \
  | docker exec -i "$container_name" psql -v ON_ERROR_STOP=1 -U postgres -d postgres
