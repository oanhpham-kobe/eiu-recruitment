import assert from "node:assert/strict";
import test from "node:test";
import {
  buildDurableRateLimitRules,
  consumeRateLimit,
  RATE_LIMITED_CODE,
} from "@/lib/security/rate-limit";
import { RATE_LIMIT_POLICIES } from "@/lib/security/rate-limit-policy";
import {
  normalizeTrustedIp,
  resolveTrustedClientIp,
} from "@/lib/security/trusted-client-ip";

test("rate-limit policy registry preserves canonical S08-002 defaults", () => {
  assert.deepEqual(
    RATE_LIMIT_POLICIES.CANDIDATE_OTP_REQUEST.rules.map((r) => [
      r.ruleCode,
      r.limit,
      r.windowSeconds,
    ]),
    [
      ["EMAIL_15M", 5, 900],
      ["IP_15M", 20, 900],
    ],
  );
  assert.deepEqual(
    RATE_LIMIT_POLICIES.CANDIDATE_OTP_VERIFY.rules.map((r) => [
      r.ruleCode,
      r.limit,
      r.windowSeconds,
    ]),
    [
      ["IDENTITY_15M", 10, 900],
      ["IP_15M", 50, 900],
    ],
  );
  assert.deepEqual(
    RATE_LIMIT_POLICIES.CANDIDATE_SUBMIT.rules.map((r) => [
      r.ruleCode,
      r.limit,
      r.windowSeconds,
    ]),
    [
      ["CANDIDATE_1H", 5, 3600],
      ["CANDIDATE_1D", 20, 86400],
    ],
  );
  assert.deepEqual(
    RATE_LIMIT_POLICIES.CANDIDATE_UPDATE.rules.map((r) => [
      r.ruleCode,
      r.limit,
      r.windowSeconds,
    ]),
    [["CANDIDATE_IP_15M", 30, 900]],
  );
  assert.deepEqual(
    RATE_LIMIT_POLICIES.UPLOAD.rules.map((r) => [
      r.ruleCode,
      r.limit,
      r.windowSeconds,
    ]),
    [
      ["IDENTITY_15M", 30, 900],
      ["IP_15M", 100, 900],
    ],
  );
  assert.deepEqual(
    RATE_LIMIT_POLICIES.INTERNAL_SEARCH.rules.map((r) => [
      r.ruleCode,
      r.limit,
      r.windowSeconds,
    ]),
    [["ACTOR_1M", 120, 60]],
  );
  assert.deepEqual(
    RATE_LIMIT_POLICIES.EMAIL_ENQUEUE.rules.map((r) => [
      r.ruleCode,
      r.limit,
      r.windowSeconds,
    ]),
    [
      ["ACTOR_TYPE_1H", 60, 3600],
      ["ACTOR_TYPE_1M", 10, 60],
    ],
  );
  assert.deepEqual(
    RATE_LIMIT_POLICIES.PDF_GENERATION.rules.map((r) => [
      r.ruleCode,
      r.limit,
      r.windowSeconds,
    ]),
    [["ACTOR_ENTITY_1H", 20, 3600]],
  );
});

test("durable rule materialization stores only opaque digests", () => {
  const email = "  Candidate.Example@Example.Test ";
  const ip = "203.0.113.8";
  const rules = buildDurableRateLimitRules("CANDIDATE_OTP_REQUEST", {
    email,
    trustedIp: ip,
  });

  assert.equal(rules.length, 2);
  for (const rule of rules) {
    assert.match(rule.keyDigest, /^[0-9a-f]{64}$/);
    assert.equal(rule.keyDigest.includes("candidate.example"), false);
    assert.equal(rule.keyDigest.includes(ip), false);
  }
});

test("Candidate Submit quota is Candidate-wide and cannot be sharded by changing IP", () => {
  const first = buildDurableRateLimitRules("CANDIDATE_SUBMIT", {
    candidateId: "00000000-0000-0000-0000-000000000123",
    trustedIp: "203.0.113.10",
  });
  const second = buildDurableRateLimitRules("CANDIDATE_SUBMIT", {
    candidateId: "00000000-0000-0000-0000-000000000123",
    trustedIp: "203.0.113.11",
  });

  assert.deepEqual(
    first.map((r) => r.keyDigest),
    second.map((r) => r.keyDigest),
  );
  assert.throws(
    () =>
      buildDurableRateLimitRules("CANDIDATE_SUBMIT", {
        candidateId: "00000000-0000-0000-0000-000000000123",
      }),
    /trusted IP/,
  );
});

test("Candidate Update uses the canonical Candidate + trusted-IP composite", () => {
  const first = buildDurableRateLimitRules("CANDIDATE_UPDATE", {
    candidateId: "00000000-0000-0000-0000-000000000123",
    trustedIp: "203.0.113.10",
  });
  const second = buildDurableRateLimitRules("CANDIDATE_UPDATE", {
    candidateId: "00000000-0000-0000-0000-000000000123",
    trustedIp: "203.0.113.11",
  });

  assert.notEqual(first[0]?.keyDigest, second[0]?.keyDigest);
});

test("Email primary quota aggregates by actor + type and is not entity-sharded", () => {
  const first = buildDurableRateLimitRules("EMAIL_ENQUEUE", {
    actorId: "00000000-0000-0000-0000-000000000999",
    emailType: "INTERVIEW_INVITE",
    entityId: "entity-a",
  });
  const second = buildDurableRateLimitRules("EMAIL_ENQUEUE", {
    actorId: "00000000-0000-0000-0000-000000000999",
    emailType: "INTERVIEW_INVITE",
    entityId: "entity-b",
  });

  assert.deepEqual(
    first.map((r) => r.keyDigest),
    second.map((r) => r.keyDigest),
  );
  assert.throws(
    () =>
      buildDurableRateLimitRules("EMAIL_ENQUEUE", {
        actorId: "00000000-0000-0000-0000-000000000999",
        emailType: "INTERVIEW_INVITE",
      }),
    /entity attribution/,
  );
});

test("trusted IP resolver trusts only the selected Vercel-controlled source", () => {
  const headers = new Headers({
    "x-vercel-forwarded-for": "203.0.113.44",
    "x-forwarded-for": "198.51.100.66",
    "x-real-ip": "198.51.100.77",
  });

  assert.equal(
    resolveTrustedClientIp({ headers, isVercel: true }),
    "203.0.113.44",
  );
  assert.equal(
    resolveTrustedClientIp({ headers, isVercel: false }),
    null,
  );

  const forgedOnly = new Headers({
    "x-forwarded-for": "203.0.113.45",
    "x-real-ip": "203.0.113.46",
  });
  assert.equal(
    resolveTrustedClientIp({ headers: forgedOnly, isVercel: true }),
    null,
  );
});

test("trusted IP normalization rejects chains and canonicalizes IPv6", () => {
  assert.equal(normalizeTrustedIp("203.0.113.1, 198.51.100.2"), null);
  assert.equal(normalizeTrustedIp("not-an-ip"), null);
  assert.equal(
    normalizeTrustedIp("2001:0DB8:0000:0000:0000:0000:0000:0001"),
    "2001:db8::1",
  );
});

test("test-only trusted IP injection is explicit and still validated", () => {
  const headers = new Headers({ "x-forwarded-for": "198.51.100.1" });
  assert.equal(
    resolveTrustedClientIp({
      headers,
      isVercel: false,
      testTrustedIp: "192.0.2.7",
    }),
    "192.0.2.7",
  );
  assert.equal(
    resolveTrustedClientIp({
      headers,
      isVercel: false,
      testTrustedIp: "forged",
    }),
    null,
  );
});

test("consumeRateLimit sends only digests and parses a durable denial", async () => {
  let capturedArgs: Record<string, unknown> | undefined;
  const client = {
    rpc: async (name: string, args: Record<string, unknown>) => {
      assert.equal(name, "consume_rate_limit_rules");
      capturedArgs = args;
      return {
        data: {
          allowed: false,
          policyCode: "CANDIDATE_OTP_REQUEST",
          retryAfterSeconds: 42,
          blockedRules: [
            {
              ruleCode: "EMAIL_15M",
              limit: 5,
              windowSeconds: 900,
              retryAfterSeconds: 42,
              resetAt: "2026-09-24T12:15:00+00:00",
            },
          ],
          rules: [],
        },
        error: null,
      };
    },
  };

  const result = await consumeRateLimit(
    "CANDIDATE_OTP_REQUEST",
    {
      email: "candidate@example.test",
      trustedIp: "203.0.113.20",
    },
    { client },
  );

  assert.equal(result.allowed, false);
  if (result.allowed || result.code !== RATE_LIMITED_CODE) {
    assert.fail("expected RATE_LIMITED decision");
  }
  assert.equal(result.retryAfterSeconds, 42);

  const serialized = JSON.stringify(capturedArgs);
  assert.equal(serialized.includes("candidate@example.test"), false);
  assert.equal(serialized.includes("203.0.113.20"), false);
  assert.match(serialized, /[0-9a-f]{64}/);
});
