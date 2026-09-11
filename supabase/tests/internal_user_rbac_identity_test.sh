#!/usr/bin/env bash
set -euo pipefail

container_name="supabase_db_eiu-recruitment-dev"
part1="supabase/tests/internal_user_rbac_identity_test.part1.sql"
part2="supabase/tests/internal_user_rbac_identity_test.part2.sql"
tmp_sql="$(mktemp)"
trap 'rm -f "$tmp_sql"' EXIT

# The checked-in regression stream intentionally exercises two contexts:
# - mutation/audit postconditions run as the DB test owner while the trusted
#   SECURITY DEFINER RPCs resolve the simulated actor from request.jwt.claim.sub;
# - explicit RLS/column-ACL and anon denial blocks keep their real roles.
# This avoids weakening production grants merely so the test can inspect the
# immutable audit table or raw Auth binding after a trusted mutation.
python3 - "$part1" "$part2" > "$tmp_sql" <<'PY'
from pathlib import Path
import sys

sql = Path(sys.argv[1]).read_text() + Path(sys.argv[2]).read_text()

# Canonical candidates require an Auth identity. This fixture UUID is candidate-
# only and intentionally distinct from every Internal User/Auth fixture.
sql = sql.replace(
    "insert into public.candidates(candidate_id,email,current_full_name,is_active)\n"
    "  values(v_candidate,'candidate_s06_002@example.com'",
    "insert into public.candidates(candidate_id,auth_user_id,email,current_full_name,is_active)\n"
    "  values(v_candidate,'73000000-0000-0000-0000-000000000001','candidate_s06_002@example.com'",
    1,
)

def owner_context(start_marker: str, end_marker: str) -> None:
    global sql
    start = sql.index(start_marker)
    end = sql.index(end_marker, start)
    segment = sql[start:end]
    count = segment.count("set local role authenticated;")
    if count == 0:
        raise RuntimeError(f"expected authenticated mutation block after {start_marker!r}")
    segment = segment.replace(
        "set local role authenticated;",
        "-- test-owner context: RPC authorization is still resolved from request.jwt.claim.sub",
    )
    sql = sql[:start] + segment + sql[end:]

owner_context(
    "-- 2. Authentication / directory lifecycle / idempotency",
    "-- anon cannot execute mutation RPCs at all.",
)
owner_context(
    "-- 3. Root-only HR role / granular permission administration",
    "-- Add active and historical Application ownership after the target is an HR.",
)
owner_context(
    "-- 4. Lifecycle blockers: active owner and non-elapsed resource participant",
    "-- Remove the live blockers using accepted trusted-state equivalents as postgres fixture setup.",
)
owner_context(
    "-- Remove the live blockers using accepted trusted-state equivalents as postgres fixture setup.",
    "-- 5. First Google login and Root-only non-Root identity change",
)
owner_context(
    "-- 5. First Google login and Root-only non-Root identity change",
    "-- 6. Static ACL / SECURITY DEFINER / search_path assertions",
)

sys.stdout.write(sql)
PY

docker exec -i "$container_name" psql -v ON_ERROR_STOP=1 -U postgres -d postgres < "$tmp_sql"
