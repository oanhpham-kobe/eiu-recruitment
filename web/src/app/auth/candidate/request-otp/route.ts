import type { SupabaseClient } from "@supabase/supabase-js";
import { type NextRequest, NextResponse } from "next/server";
import { validateSameOrigin } from "@/lib/security/origin";
import {
  consumeRateLimit as consumeDurableRateLimit,
  type RateLimitContext,
  type RateLimitDecision,
} from "@/lib/security/rate-limit";
import {
  rateLimitResponseIfBlocked,
  rateLimitUnavailableResponse,
} from "@/lib/security/rate-limit-http";
import type { RateLimitPolicyCode } from "@/lib/security/rate-limit-policy";
import { resolveTrustedClientIpFromHeaders } from "@/lib/security/trusted-client-ip";
import { createServerClient } from "@/lib/supabase/server";

export const dynamic = "force-dynamic";

type RateLimitConsumer = (
  policyCode: RateLimitPolicyCode,
  context: RateLimitContext,
) => Promise<RateLimitDecision>;

export type CandidateOtpRequestRateLimitDeps = {
  resolveTrustedIp?: (request: NextRequest) => string | null;
  consumeRateLimit?: RateLimitConsumer;
};

function validationError(message: string) {
  return NextResponse.json(
    {
      success: false,
      error: { code: "VALIDATION_ERROR", message },
    },
    { status: 400, headers: { "Cache-Control": "no-store" } },
  );
}

export async function POST(
  request: NextRequest,
  _context?: unknown,
  clientOverride?: SupabaseClient,
  deps: CandidateOtpRequestRateLimitDeps = {},
) {
  if (!validateSameOrigin(request)) {
    return NextResponse.json(
      {
        success: false,
        error: {
          code: "FORBIDDEN",
          message: "Cross-origin request rejected",
        },
      },
      { status: 403, headers: { "Cache-Control": "no-store" } },
    );
  }

  let body: { email?: unknown };
  try {
    body = await request.json();
  } catch {
    return validationError("Invalid JSON request body");
  }

  const rawEmail = body?.email;
  if (typeof rawEmail !== "string") {
    return validationError("Email is required");
  }
  const email = rawEmail.trim().toLowerCase();
  if (!email || email.length > 320 || !/^[^\s@]+@[^\s@]+$/.test(email)) {
    return validationError("A valid email is required");
  }

  const resolveTrustedIp =
    deps.resolveTrustedIp ??
    ((req: NextRequest) => resolveTrustedClientIpFromHeaders(req.headers));
  const trustedIp = resolveTrustedIp(request);
  if (!trustedIp) {
    return rateLimitUnavailableResponse();
  }

  const consumeRateLimit = deps.consumeRateLimit ?? consumeDurableRateLimit;
  const decision = await consumeRateLimit("CANDIDATE_OTP_REQUEST", {
    email,
    trustedIp,
  });
  const blocked = rateLimitResponseIfBlocked(decision);
  if (blocked) {
    return blocked;
  }

  const supabase = clientOverride ?? (await createServerClient());
  const { error } = await supabase.auth.signInWithOtp({
    email,
    options: { shouldCreateUser: true },
  });
  if (error) {
    return NextResponse.json(
      {
        success: false,
        error: {
          code: "OTP_REQUEST_FAILED",
          message: "Unable to send OTP code",
        },
      },
      { status: 400, headers: { "Cache-Control": "no-store" } },
    );
  }

  return NextResponse.json(
    { success: true },
    { status: 200, headers: { "Cache-Control": "no-store" } },
  );
}
