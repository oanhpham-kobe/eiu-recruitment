import { type NextRequest, NextResponse } from "next/server";
import {
  type ReserveCandidateUploadInput,
  reserveCandidateUploadBoundary,
} from "@/lib/candidate/upload-server";
import { validateSameOrigin } from "@/lib/security/origin";
import { resolveTrustedClientIpFromHeaders } from "@/lib/security/trusted-client-ip";

export const dynamic = "force-dynamic";

export type CandidateUploadReserveRouteDeps = {
  resolveTrustedIp?: (request: NextRequest) => string | null;
  reserveBoundary?: typeof reserveCandidateUploadBoundary;
};

const NO_STORE = { "Cache-Control": "no-store" } as const;

function errorResponse(
  code: string,
  message: string,
  retryAfterSeconds?: number,
) {
  const status =
    code === "RATE_LIMITED"
      ? 429
      : code === "RATE_LIMIT_UNAVAILABLE"
        ? 503
        : code === "UNAUTHENTICATED"
          ? 401
          : code === "FORBIDDEN"
            ? 403
            : code === "INTERNAL_ERROR"
              ? 500
              : 400;
  const retry =
    code === "RATE_LIMITED" && retryAfterSeconds && retryAfterSeconds > 0
      ? Math.trunc(retryAfterSeconds)
      : undefined;
  return NextResponse.json(
    {
      success: false,
      error: {
        code,
        message,
        ...(retry ? { retryAfterSeconds: retry } : {}),
      },
    },
    {
      status,
      headers: retry
        ? { ...NO_STORE, "Retry-After": String(retry) }
        : NO_STORE,
    },
  );
}

function isReserveInput(value: unknown): value is ReserveCandidateUploadInput {
  if (!value || typeof value !== "object") return false;
  const input = value as Record<string, unknown>;
  return (
    typeof input.sessionId === "string" &&
    typeof input.intendedDocumentTypeId === "string" &&
    typeof input.filename === "string" &&
    (input.declaredMimeType === undefined ||
      typeof input.declaredMimeType === "string") &&
    (input.expectedMaxSize === undefined ||
      typeof input.expectedMaxSize === "number")
  );
}

export async function POST(
  request: NextRequest,
  _context?: unknown,
  deps: CandidateUploadReserveRouteDeps = {},
) {
  if (!validateSameOrigin(request)) {
    return errorResponse("FORBIDDEN", "Cross-origin request rejected");
  }

  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return errorResponse("VALIDATION_ERROR", "Invalid JSON request body");
  }
  if (!isReserveInput(body)) {
    return errorResponse("VALIDATION_ERROR", "Invalid upload reservation request");
  }

  const trustedIp = (deps.resolveTrustedIp ?? ((req: NextRequest) =>
    resolveTrustedClientIpFromHeaders(req.headers)))(request);
  if (!trustedIp) {
    return errorResponse(
      "RATE_LIMIT_UNAVAILABLE",
      "Request protection is temporarily unavailable",
    );
  }

  const result = await (deps.reserveBoundary ?? reserveCandidateUploadBoundary)(
    body,
    trustedIp,
  );
  if (!result.success) {
    return errorResponse(
      result.code,
      result.error,
      result.retryAfterSeconds,
    );
  }

  return NextResponse.json(result, { status: 200, headers: NO_STORE });
}
