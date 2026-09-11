import assert from "node:assert/strict";
import test from "node:test";
import type { SupabaseClient } from "@supabase/supabase-js";
import { getServerSession } from "@/lib/auth/session";

function createInternalRpcClient(payload: unknown): SupabaseClient {
  return {
    auth: {
      getUser: async () => ({
        data: {
          user: {
            id: "auth-internal-s06-002",
            email: "hr.rpc@eiu.edu.vn",
          },
        },
        error: null,
      }),
    },
    rpc: async (functionName: string) => {
      assert.equal(functionName, "get_current_internal_session");
      return { data: payload, error: null };
    },
    from: () => {
      throw new Error("raw app_users fallback must not run for a valid S06-002 RPC payload");
    },
  } as unknown as SupabaseClient;
}

test("getServerSession: resolves internal authorization from minimum-safe S06-002 RPC", async () => {
  const client = createInternalRpcClient({
    success: true,
    data: {
      app_user_id: "70000000-0000-0000-0000-000000000003",
      is_active: true,
      is_root_admin: false,
      roles: ["HR"],
      permissions: ["interviews.view", "interviews.participants"],
    },
  });

  const session = await getServerSession(client);

  assert.equal(session.isAuthenticated, true);
  assert.deepEqual(session.user, {
    authUserId: "auth-internal-s06-002",
    email: "hr.rpc@eiu.edu.vn",
    isInternal: true,
    isCandidate: false,
    appUserId: "70000000-0000-0000-0000-000000000003",
    roles: ["HR"],
    permissions: ["interviews.view", "interviews.participants"],
  });
});

test("getServerSession: Root RPC result keeps implicit Root role without client metadata", async () => {
  const client = createInternalRpcClient({
    success: true,
    data: {
      app_user_id: "70000000-0000-0000-0000-000000000001",
      is_active: true,
      is_root_admin: true,
      roles: [],
      permissions: ["submissions.view", "users.permissions_manage"],
    },
  });

  const session = await getServerSession(client);

  assert.equal(session.isAuthenticated, true);
  assert.ok(session.user?.roles.includes("ROOT_ADMIN"));
  assert.deepEqual(session.user?.permissions, [
    "submissions.view",
    "users.permissions_manage",
  ]);
});

test("getServerSession: trusted RPC denial fails closed without raw-directory fallback", async () => {
  const client = createInternalRpcClient({
    success: false,
    error_code: "USER_INACTIVE",
    message: "User account is inactive",
  });

  const session = await getServerSession(client);

  assert.equal(session.isAuthenticated, false);
  assert.equal(session.user, null);
});
