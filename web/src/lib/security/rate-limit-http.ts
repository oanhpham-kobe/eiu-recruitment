import "server-only";

import { NextResponse } from "next/server";
import {
  RATE_LIMITED_CODE,
  type RateLimitDecision,
} from "@/lib/security/rate-limit";

const NO_STORE_HEADERS = { "Cache-Control": "no-store" } as const;

export function rateLimitUnavailableResponse() {
  return NextResponse.json(
    {
      success: false,
      error: {
        code: "RATE_LIMIT_UNAVAILABLE",
        message: "Request protection is temporarily unavailable",
      },
    },
    { status: 503, headers: NO_STORE_HEADERS },
  );
}

export function rateLimitResponseIfBlocked(
  decision: RateLimitDecision,
): NextResponse | null {
  if (decision.allowed) {
    return null;
  }

  if (decision.code !== RATE_LIMITED_CODE) {
    return rateLimitUnavailableResponse();
  }

  const retryAfterSeconds = Math.max(1, Math.trunc(decision.retryAfterSeconds));
  return NextResponse.json(
    {
      success: false,
      error: {
        code: RATE_LIMITED_CODE,
        message: "Too many requests. Please retry later.",
        retryAfterSeconds,
      },
    },
    {
      status: 429,
      headers: {
        ...NO_STORE_HEADERS,
        "Retry-After": String(retryAfterSeconds),
      },
    },
  );
}
