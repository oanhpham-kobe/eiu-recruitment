from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected one match for {old!r}, got {count}")
    p.write_text(text.replace(old, new, 1), encoding="utf-8")


def replace_between(path: str, start: str, end: str, new_block: str) -> None:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    i = text.find(start)
    if i < 0:
        raise SystemExit(f"{path}: start marker missing: {start}")
    j = text.find(end, i + len(start))
    if j < 0:
        raise SystemExit(f"{path}: end marker missing: {end}")
    p.write_text(text[:i] + new_block + text[j:], encoding="utf-8")


inbox = "web/src/__tests__/application-inbox.test.ts"
replace_once(
    inbox,
    "function internalSession(permissions: string[], isInternal = true): AppSession {",
    'function internalSession(\n  permissions: string[],\n  isInternal = true,\n  roles = isInternal ? ["HR"] : ["CANDIDATE"],\n): AppSession {',
)
replace_once(
    inbox,
    '      roles: isInternal ? ["HR"] : ["CANDIDATE"],',
    "      roles,",
)
replace_once(
    inbox,
    "    resolveSession: async () => internalSession([]),\n  });\n\n  assert.equal(client.getSubmissionQueryCount(), 1);",
    '    resolveSession: async () => internalSession([], true, ["ROOT_ADMIN"]),\n  });\n\n  assert.equal(client.getSubmissionQueryCount(), 1);',
)

auth = "web/src/__tests__/auth-routes.test.ts"
auth_start = 'test("getServerSession: resolves internal permissions strictly from database, ignoring client claims", async () => {'
auth_end = 'test("getServerSession: returns unauthenticated if internal user is inactive", async () => {'
auth_block = '''test("getServerSession: resolves internal permissions strictly from trusted database RPC, ignoring client claims", async () => {
  const client = createMockClient({
    getUser: async () => ({
      data: { user: { id: "auth-internal-1", email: "hr.manager@eiu.edu.vn" } },
      error: null,
    }),
    rpc: async (fnName) => {
      assert.equal(fnName, "get_current_internal_session");
      return {
        data: {
          success: true,
          data: {
            app_user_id: "app-user-999",
            is_active: true,
            is_root_admin: false,
            roles: ["HR"],
            permissions: ["candidates.view", "submissions.evaluate"],
          },
        },
        error: null,
      };
    },
  });

  const session = await getServerSession(client);
  assert.equal(session.isAuthenticated, true);
  assert.notEqual(session.user, null);
  if (session.user) {
    assert.equal(session.user.authUserId, "auth-internal-1");
    assert.equal(session.user.email, "hr.manager@eiu.edu.vn");
    assert.equal(session.user.isInternal, true);
    assert.equal(session.user.isCandidate, false);
    assert.equal(session.user.appUserId, "app-user-999");
    assert.deepEqual(session.user.roles, ["HR"]);
    assert.deepEqual(session.user.permissions, [
      "candidates.view",
      "submissions.evaluate",
    ]);
  }
});

'''
replace_between(auth, auth_start, auth_end, auth_block)

detail = "web/src/__tests__/submission-detail.test.ts"
p = Path(detail)
text = p.read_text(encoding="utf-8")
fn_marker = "function createMockSupabase(options: {"
fi = text.find(fn_marker)
if fi < 0:
    raise SystemExit("createMockSupabase marker missing")
rpc_start = text.find("    rpc: async (fn: string, args?: unknown) => {", fi)
auth_marker = text.find("    auth: {", rpc_start)
if rpc_start < 0 or auth_marker < 0:
    raise SystemExit("createMockSupabase rpc/auth markers missing")
new_rpc = '''    rpc: async (fn: string, args?: unknown) => {
      const handler = options.rpcHandlers?.[fn];
      if (handler) {
        const result = handler(args);
        return { data: result, error: null };
      }
      const isInternal =
        options.userSession?.email.toLowerCase().endsWith("@eiu.edu.vn") === true;
      if (fn === "get_current_internal_session" && isInternal) {
        return {
          data: {
            success: true,
            data: {
              app_user_id: options.userSession?.id ?? "user-1",
              is_active: isActive,
              is_root_admin: options.isRootAdmin ?? false,
              roles,
              permissions,
            },
          },
          error: null,
        };
      }
      if (fn === "get_current_internal_binding_status" && isInternal) {
        return {
          data: {
            success: true,
            data: {
              bound: true,
              app_user_id: options.userSession?.id ?? "user-1",
              is_active: isActive,
              is_root_admin: options.isRootAdmin ?? false,
            },
          },
          error: null,
        };
      }
      return { data: null, error: null };
    },
'''
p.write_text(text[:rpc_start] + new_rpc + text[auth_marker:], encoding="utf-8")

t10_start = 'test("10. Actor resolution using is_root_admin prevents real authorized HR callers from being classified as GUEST", async () => {'
t10_end = 'test("11. Drawer typography: all drawer body text, labels, document names/meta, and alerts satisfy >=16px", async () => {'
t10_block = '''test("10. Actor resolution uses trusted session RPC and never raw-queries app_users auth binding", async () => {
  let rawAppUsersQueried = false;
  const trustedSessionClient = {
    auth: {
      getUser: async () => ({
        data: { user: { id: "hr-user-id", email: "hr@eiu.edu.vn" } },
        error: null,
      }),
    },
    rpc: async (fn: string) => {
      if (fn === "get_current_internal_session") {
        return {
          data: {
            success: true,
            data: {
              app_user_id: "hr-user-id",
              is_active: true,
              is_root_admin: false,
              roles: ["HR"],
              permissions: ["submissions.edit"],
            },
          },
          error: null,
        };
      }
      if (fn === "update_submission_by_hr") {
        return {
          data: {
            success: true,
            data: {
              submission_id: sampleSubmissionId,
              hr_note: "Test note",
              version_no: 2,
            },
          },
          error: null,
        };
      }
      return { data: null, error: null };
    },
    from: (table: string) => {
      if (table === "app_users") rawAppUsersQueried = true;
      throw new Error(`Unexpected raw table query: ${table}`);
    },
  } as unknown as SupabaseClient;

  const res = await saveSubmissionHrNote(sampleSubmissionId, "Test note", 1, {
    client: trustedSessionClient,
  });
  assert.equal(
    rawAppUsersQueried,
    false,
    "Must not raw-query app_users identity binding",
  );
  assert.equal(
    res.success,
    true,
    "Authorized HR actor must resolve through trusted session RPC",
  );
});

'''
replace_between(detail, t10_start, t10_end, t10_block)
