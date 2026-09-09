import assert from "node:assert/strict";
import test from "node:test";
import { resolveInternalNavItems } from "@/components/shell/navigation";

function hrefs(roles: string[], permissions: string[]): string[] {
  return resolveInternalNavItems({ roles, permissions }).map(
    (item) => item.href,
  );
}

test("Interviewer navigation exposes only the contextual report module", () => {
  assert.deepEqual(hrefs([], []), ["/reports"]);
});

test("limited HR navigation follows granted view permissions", () => {
  assert.deepEqual(hrefs(["HR"], ["submissions.view"]), ["/", "/reports"]);
  assert.deepEqual(hrefs(["HR"], ["interviews.view"]), [
    "/interviews",
    "/reports",
  ]);
  assert.deepEqual(
    hrefs(["HR"], ["submissions.view", "interviews.view", "reports.view"]),
    ["/", "/interviews", "/reports"],
  );
});

test("Root Admin sees all implemented internal modules", () => {
  assert.deepEqual(hrefs(["ROOT_ADMIN"], []), ["/", "/interviews", "/reports"]);
});

test("missing identity fails closed", () => {
  assert.deepEqual(resolveInternalNavItems(null), []);
});
