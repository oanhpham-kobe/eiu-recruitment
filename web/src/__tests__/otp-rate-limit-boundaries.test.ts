import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import type { SupabaseClient } from "@supabase/supabase-js";
import { NextRequest } from "next/server";
import {
  type CandidateOtpRequestRateLimitDeps,
  POST as requestOtp,
} from "@/app/auth/candidate/request-otp/route";
import {
  type CandidateVerifyRateLimitDeps,
  POST as verifyOtp,
} from "@/app/auth/candidate/verify/route";
import type {
  RateLimitContext,
  RateLimitDecision,
} from "@/lib/security/rate-limit";
import type { RateLimitPolicyCode } from "@/lib/security/rate-limit-policy";

function sameOriginRequest(pathName: string, body: Record<string, unknown>) {
  return new NextRequest(`https://recruitment.example.test${pathName}`, {
    method: "POST",
    headers: {
      host: "recruitment.example.test",
      origin: "https://recruitment.example.test",
      "content-type": "application/json",
    },
    body: JSON.stringify(body),
  });
}

test("OTP request is same-origin server mediated and blocks before provider call", async () => {
  let providerCalls = 0;
  let capturedPolicy: RateLimitPolicyCode | undefined;
  let capturedContext: RateLimitContext | undefined;
  const client = {
    auth: {
      signInWithOtp: async () => {
        providerCalls += 1;
        return { error: null };
      },
    },
  } as unknown as SupabaseClient;
  const deps: CandidateOtpRequestRateLimitDeps = {
    resolveTrustedIp: () => "203.0.113.20",
    consumeRateLimit: async (policyCode, context) => {
      capturedPolicy = policyCode;
      capturedContext = context;
      return {
        allowed: false,
        code: "RATE_LIMITED",
        policyCode,
        retryAfterSeconds: 37,
        blockedRules: [],
      };
    },
  };

  const response = await requestOtp(
    sameOriginRequest("/auth/candidate/request-otp", {
      email: " Candidate@Example.Test ",
    }),
    undefined,
    client,
    deps,
  );

  assert.equal(response.status, 429);
  assert.equal(response.headers.get("Retry-After"), "37");
  assert.equal(providerCalls, 0);
  assert.equal(capturedPolicy, "CANDIDATE_OTP_REQUEST");
  assert.deepEqual(capturedContext, {
    email: "candidate@example.test",
    trustedIp: "203.0.113.20",
  });
  const body = await response.json();
  assert.equal(body.error.code, "RATE_LIMITED");
});

test("OTP request fails closed when trusted client IP is unavailable", async () => {
  let providerCalls = 0;
  const client = {
    auth: {
      signInWithOtp: async () => {
        providerCalls += 1;
        return { error: null };
      },
    },
  } as unknown as SupabaseClient;

  const response = await requestOtp(
    sameOriginRequest("/auth/candidate/request-otp", {
      email: "candidate@example.test",
    }),
    undefined,
    client,
    { resolveTrustedIp: () => null },
  );

  assert.equal(response.status, 503);
  assert.equal(providerCalls, 0);
  const body = await response.json();
  assert.equal(body.error.code, "RATE_LIMIT_UNAVAILABLE");
});

test("allowed OTP request invokes provider only after limiter success", async () => {
  let providerEmail: string | undefined;
  const client = {
    auth: {
      signInWithOtp: async (params: { email: string }) => {
        providerEmail = params.email;
        return { error: null };
      },
    },
  } as unknown as SupabaseClient;
  const deps: CandidateOtpRequestRateLimitDeps = {
    resolveTrustedIp: () => "203.0.113.21",
    consumeRateLimit: async (policyCode) => ({
      allowed: true,
      policyCode,
      rules: [],
    }),
  };

  const response = await requestOtp(
    sameOriginRequest("/auth/candidate/request-otp", {
      email: " Candidate@Example.Test ",
    }),
    undefined,
    client,
    deps,
  );

  assert.equal(response.status, 200);
  assert.equal(providerEmail, "candidate@example.test");
});

test("OTP verify blocks before provider and never uses token as limiter context", async () => {
  let verifyCalls = 0;
  let capturedContext: RateLimitContext | undefined;
  const client = {
    auth: {
      verifyOtp: async () => {
        verifyCalls += 1;
        return { error: null };
      },
    },
  } as unknown as SupabaseClient;
  const deps: CandidateVerifyRateLimitDeps = {
    resolveTrustedIp: () => "203.0.113.22",
    consumeRateLimit: async (policyCode, context) => {
      capturedContext = context;
      const decision: RateLimitDecision = {
        allowed: false,
        code: "RATE_LIMITED",
        policyCode,
        retryAfterSeconds: 11,
        blockedRules: [],
      };
      return decision;
    },
  };

  const response = await verifyOtp(
    sameOriginRequest("/auth/candidate/verify", {
      email: "candidate@example.test",
      token: "654321",
    }),
    undefined,
    client,
    deps,
  );

  assert.equal(response.status, 429);
  assert.equal(response.headers.get("Retry-After"), "11");
  assert.equal(verifyCalls, 0);
  assert.deepEqual(capturedContext, {
    identity: "candidate@example.test",
    trustedIp: "203.0.113.22",
  });
  assert.equal(JSON.stringify(capturedContext).includes("654321"), false);
});

test("OTP request rejects cross-origin traffic before limiter/provider", async () => {
  let limiterCalls = 0;
  const request = new NextRequest(
    "https://recruitment.example.test/auth/candidate/request-otp",
    {
      method: "POST",
      headers: {
        host: "recruitment.example.test",
        origin: "https://attacker.example.test",
        "content-type": "application/json",
      },
      body: JSON.stringify({ email: "candidate@example.test" }),
    },
  );
  const response = await requestOtp(request, undefined, undefined, {
    resolveTrustedIp: () => "203.0.113.23",
    consumeRateLimit: async (policyCode) => {
      limiterCalls += 1;
      return { allowed: true, policyCode, rules: [] };
    },
  });
  assert.equal(response.status, 403);
  assert.equal(limiterCalls, 0);
});

test("login client no longer invokes Supabase signInWithOtp directly", () => {
  const source = fs.readFileSync(
    path.join(process.cwd(), "src/app/login/page.tsx"),
    "utf8",
  );
  assert.doesNotMatch(source, /signInWithOtp/);
  assert.match(source, /\/auth\/candidate\/request-otp/);
});
