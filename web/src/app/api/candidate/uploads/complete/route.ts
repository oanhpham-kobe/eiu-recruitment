import { type NextRequest, NextResponse } from "next/server";
import {
  type CompleteCandidateUploadInput,
  completeCandidateUploadBoundary,
} from "@/lib/candidate/upload-server";
import { validateSameOrigin } from "@/lib/security/origin";
import { resolveTrustedClientIpFromHeaders } from "@/lib/security/trusted-client-ip";

export const dynamic = "force-dynamic";
export type CandidateUploadCompleteRouteDeps = {
  resolveTrustedIp?: (request: NextRequest) => string | null;
  completeBoundary?: typeof completeCandidateUploadBoundary;
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
      error: { code, message, ...(retry ? { retryAfterSeconds: retry } : {}) },
    },
    {
      status,
      headers: retry ? { ...NO_STORE, "Retry-After": String(retry) } : NO_STORE,
    },
  );
}
function isCompleteInput(
  value: unknown,
): value is CompleteCandidateUploadInput {
  if (!value || typeof value !== "object") return false;
  const input = value as Record<string, unknown>;
  return (
    typeof input.sessionId === "string" &&
    typeof input.reservationId === "string" &&
    typeof input.intendedDocumentTypeId === "string" &&
    typeof input.actualSize === "number" &&
    (input.actionCode === undefined ||
      input.actionCode === "ADD" ||
      input.actionCode === "REPLACE") &&
    (input.targetLogicalDocumentId === undefined ||
      typeof input.targetLogicalDocumentId === "string") &&
    (input.mimeType === undefined || typeof input.mimeType === "string")
  );
}
export async function POST(
  request: NextRequest,
  _context?: unknown,
  deps: CandidateUploadCompleteRouteDeps = {},
) {
  if (!validateSameOrigin(request))
    return errorResponse("FORBIDDEN", "Cross-origin request rejected");
  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return errorResponse("VALIDATION_ERROR", "Invalid JSON request body");
  }
  if (!isCompleteInput(body))
    return errorResponse(
      "VALIDATION_ERROR",
      "Invalid upload completion request",
    );
  const trustedIp = (
    deps.resolveTrustedIp ??
    ((req: NextRequest) => resolveTrustedClientIpFromHeaders(req.headers))
  )(request);
  if (!trustedIp)
    return errorResponse(
      "RATE_LIMIT_UNAVAILABLE",
      "Request protection is temporarily unavailable",
    );
  const result = await (
    deps.completeBoundary ?? completeCandidateUploadBoundary
  )(body, trustedIp);
  if (!result.success)
    return errorResponse(result.code, result.error, result.retryAfterSeconds);
  return NextResponse.json(result, { status: 200, headers: NO_STORE });
}
