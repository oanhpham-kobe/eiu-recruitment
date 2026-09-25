import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import type { SupabaseClient } from "@supabase/supabase-js";
import {
  createSubmitCandidateSubmissionCommand,
  createUpdateCandidateSubmissionCommand,
  type SubmitCandidateSubmissionInput,
} from "@/lib/commands/candidate-submission";
import { CommandErrorCode, type VerifiedActor } from "@/lib/commands/types";

const actor: VerifiedActor = {
  authUserId: "00000000-0000-0000-0000-000000008010",
  candidateId: "00000000-0000-0000-0000-000000008011",
  email: "candidate@example.test",
  isActive: true,
  roles: ["candidate"],
  permissions: ["candidate_self"],
};

const input: SubmitCandidateSubmissionInput = {
  candidateFormSessionId: "00000000-0000-0000-0000-000000008012",
  fullName: "Candidate Rate Limited",
  phone: "0901234567",
  dateOfBirth: "1995-05-15",
  gender: "FEMALE",
  address: "Binh Duong",
  privacyNoticeVersion: "v1",
  education: [],
  idempotencyKey: "00000000-0000-0000-0000-000000008013",
};

function mockRpcClient(expectedName: string) {
  let captured: Record<string, unknown> | undefined;
  const client = {
    rpc: async (name: string, args: Record<string, unknown>) => {
      assert.equal(name, expectedName);
      captured = args;
      return {
        data: {
          success: true,
          data: {
            submission_id: "00000000-0000-0000-0000-000000008014",
            status_code: "NEW",
            version_no: 1,
          },
        },
        error: null,
      };
    },
  } as unknown as SupabaseClient;
  return { client, getCaptured: () => captured };
}

test("Candidate Submit uses only the service-only rate-limited wrapper", async () => {
  const mock = mockRpcClient("submit_candidate_submission_rate_limited");
  const command = createSubmitCandidateSubmissionCommand(
    mock.client,
    "203.0.113.80",
  );
  const result = await command.execute(actor, input);
  assert.equal((result as { success: boolean }).success, true);
  const args = mock.getCaptured();
  assert.equal(args?.p_actor_auth_user_id, actor.authUserId);
  assert.match(String(args?.p_candidate_key_digest), /^[0-9a-f]{64}$/);
  assert.match(String(args?.p_trusted_ip_key_digest), /^[0-9a-f]{64}$/);
  const serialized = JSON.stringify(args);
  assert.equal(serialized.includes("203.0.113.80"), false);
  assert.equal(serialized.includes("windowSeconds"), false);
  assert.equal(serialized.includes('"limit"'), false);
});

test("Candidate Update binds candidate+trusted-IP digest to wrapper", async () => {
  const first = mockRpcClient("update_candidate_submission_rate_limited");
  const second = mockRpcClient("update_candidate_submission_rate_limited");
  await createUpdateCandidateSubmissionCommand(
    first.client,
    "203.0.113.81",
  ).execute(actor, input);
  await createUpdateCandidateSubmissionCommand(
    second.client,
    "203.0.113.82",
  ).execute(actor, input);
  assert.match(
    String(first.getCaptured()?.p_candidate_ip_key_digest),
    /^[0-9a-f]{64}$/,
  );
  assert.notEqual(
    first.getCaptured()?.p_candidate_ip_key_digest,
    second.getCaptured()?.p_candidate_ip_key_digest,
  );
});

test("Candidate mutation fails closed before RPC without trusted IP", async () => {
  let calls = 0;
  const client = {
    rpc: async () => {
      calls += 1;
      return { data: null, error: null };
    },
  } as unknown as SupabaseClient;
  const result = await createSubmitCandidateSubmissionCommand(client).execute(
    actor,
    input,
  );
  assert.equal(calls, 0);
  assert.equal((result as any).success, false);
  assert.equal(
    (result as any).error.code,
    CommandErrorCode.RATE_LIMIT_UNAVAILABLE,
  );
});

test("Candidate Server Actions derive trusted IP and use admin wrapper client", () => {
  const source = fs.readFileSync(
    path.join(process.cwd(), "src/app/candidate/candidate-actions.ts"),
    "utf8",
  );
  assert.match(
    source,
    /resolveTrustedClientIpFromHeaders\(await headers\(\)\)/,
  );
  assert.match(source, /createAdminClient\(\)/);
  assert.match(source, /actorClient: supabase/);
  assert.match(source, /trustedIp/);
});
