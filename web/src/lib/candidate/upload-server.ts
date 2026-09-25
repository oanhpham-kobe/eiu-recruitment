import "server-only";

import type { SupabaseClient } from "@supabase/supabase-js";
import {
  createSignedUploadUrlForReservation,
  recordInspectedUploadReservation,
} from "@/lib/commands/storage-reservation";
import { buildDurableRateLimitRules } from "@/lib/security/rate-limit";
import { inspectUploadReservation } from "@/lib/storage/upload-scanner";
import { createAdminClient } from "@/lib/supabase/admin";
import { createServerClient } from "@/lib/supabase/server";

export type ReserveCandidateUploadInput = {
  sessionId: string;
  intendedDocumentTypeId: string;
  filename: string;
  declaredMimeType?: string;
  expectedMaxSize?: number;
};

export type CompleteCandidateUploadInput = {
  sessionId: string;
  reservationId: string;
  intendedDocumentTypeId: string;
  actualSize: number;
  actionCode?: "ADD" | "REPLACE";
  targetLogicalDocumentId?: string;
  checksumSha256?: string;
  mimeType?: string;
};

export type CandidateUploadFailure = {
  success: false;
  error: string;
  code: string;
  retryAfterSeconds?: number;
};

export type ReserveCandidateUploadData = {
  reservationId: string;
  tempBucket: string;
  tempPath: string;
  signedUrl: string;
  token: string;
};

export type CompleteCandidateUploadData = {
  kind: "PENDING_SCAN";
  requestId: string;
  reservationId: string;
};

export type CandidateUploadBoundaryDeps = {
  sessionClient?: SupabaseClient;
  adminClient?: SupabaseClient | null;
  inspectReservation?: typeof inspectUploadReservation;
  createSignedUrl?: typeof createSignedUploadUrlForReservation;
  recordInspection?: typeof recordInspectedUploadReservation;
};

type RpcEnvelope<T> = {
  success?: boolean;
  error_code?: string;
  message?: string;
  data?: T & { retry_after_seconds?: number };
};

function fail(
  code: string,
  error: string,
  retryAfterSeconds?: number,
): CandidateUploadFailure {
  return {
    success: false,
    code,
    error,
    ...(retryAfterSeconds && retryAfterSeconds > 0
      ? { retryAfterSeconds: Math.trunc(retryAfterSeconds) }
      : {}),
  };
}

function parseRetryAfter(value: unknown): number | undefined {
  return typeof value === "number" && Number.isInteger(value) && value > 0
    ? value
    : undefined;
}

async function resolveCandidateActor(client: SupabaseClient) {
  const {
    data: { user },
    error,
  } = await client.auth.getUser();
  if (error || !user?.id || !user.email) {
    return null;
  }

  const { data: candidate, error: candidateError } = await client
    .from("candidates")
    .select("candidate_id, is_active")
    .eq("auth_user_id", user.id)
    .maybeSingle();

  if (
    candidateError ||
    !candidate?.candidate_id ||
    candidate.is_active !== true
  ) {
    return null;
  }

  return { authUserId: user.id, candidateId: candidate.candidate_id };
}

function buildUploadDigests(authUserId: string, trustedIp: string) {
  const rules = buildDurableRateLimitRules("UPLOAD", {
    identity: authUserId,
    trustedIp,
  });
  const identity = rules.find((rule) => rule.ruleCode === "IDENTITY_15M");
  const ip = rules.find((rule) => rule.ruleCode === "IP_15M");
  if (!identity || !ip) {
    throw new Error("UPLOAD rate-limit policy is incomplete");
  }
  return { identityDigest: identity.keyDigest, ipDigest: ip.keyDigest };
}

async function getClients(deps: CandidateUploadBoundaryDeps) {
  const sessionClient = deps.sessionClient ?? (await createServerClient());
  const adminClient = deps.adminClient ?? createAdminClient();
  return { sessionClient, adminClient };
}

export async function reserveCandidateUploadBoundary(
  input: ReserveCandidateUploadInput,
  trustedIp: string,
  deps: CandidateUploadBoundaryDeps = {},
): Promise<
  { success: true; data: ReserveCandidateUploadData } | CandidateUploadFailure
> {
  if (!trustedIp?.trim()) {
    return fail(
      "RATE_LIMIT_UNAVAILABLE",
      "Request protection is temporarily unavailable",
    );
  }

  const { sessionClient, adminClient } = await getClients(deps);
  if (!adminClient) {
    return fail(
      "RATE_LIMIT_UNAVAILABLE",
      "Request protection is temporarily unavailable",
    );
  }

  const actor = await resolveCandidateActor(sessionClient);
  if (!actor) {
    return fail("UNAUTHENTICATED", "Candidate authentication required");
  }

  let digests: ReturnType<typeof buildUploadDigests>;
  try {
    digests = buildUploadDigests(actor.authUserId, trustedIp);
  } catch {
    return fail(
      "RATE_LIMIT_UNAVAILABLE",
      "Request protection is temporarily unavailable",
    );
  }

  const { data, error } = await adminClient.rpc(
    "reserve_candidate_form_upload_rate_limited",
    {
      p_actor_auth_user_id: actor.authUserId,
      p_identity_key_digest: digests.identityDigest,
      p_trusted_ip_key_digest: digests.ipDigest,
      p_candidate_form_session_id: input.sessionId,
      p_intended_document_type_id: input.intendedDocumentTypeId,
      p_original_filename: input.filename,
      p_declared_mime_type: input.declaredMimeType ?? null,
      p_expected_max_size_bytes: input.expectedMaxSize ?? 5242880,
      p_idempotency_key: crypto.randomUUID(),
    },
  );

  if (error || !data || typeof data !== "object") {
    return fail(
      "RATE_LIMIT_UNAVAILABLE",
      "Request protection is temporarily unavailable",
    );
  }

  const result = data as RpcEnvelope<{
    upload_reservation_id: string;
    temp_bucket: string;
    temp_path: string;
  }>;
  if (result.success !== true || !result.data) {
    return fail(
      result.error_code ?? "INTERNAL_ERROR",
      result.message ?? "Unable to reserve upload",
      parseRetryAfter(result.data?.retry_after_seconds),
    );
  }

  const createSignedUrl =
    deps.createSignedUrl ?? createSignedUploadUrlForReservation;
  const signed = await createSignedUrl(
    { uploadReservationId: result.data.upload_reservation_id },
    { client: sessionClient },
  );
  if (!signed.success) {
    return fail(signed.error.code, signed.error.message);
  }

  return {
    success: true,
    data: {
      reservationId: result.data.upload_reservation_id,
      tempBucket: result.data.temp_bucket,
      tempPath: result.data.temp_path,
      signedUrl: signed.data.signedUrl,
      token: signed.data.token,
    },
  };
}

export async function completeCandidateUploadBoundary(
  input: CompleteCandidateUploadInput,
  trustedIp: string,
  deps: CandidateUploadBoundaryDeps = {},
): Promise<
  { success: true; data: CompleteCandidateUploadData } | CandidateUploadFailure
> {
  if (!trustedIp?.trim()) {
    return fail(
      "RATE_LIMIT_UNAVAILABLE",
      "Request protection is temporarily unavailable",
    );
  }

  const { sessionClient, adminClient } = await getClients(deps);
  if (!adminClient) {
    return fail(
      "RATE_LIMIT_UNAVAILABLE",
      "Request protection is temporarily unavailable",
    );
  }

  const actor = await resolveCandidateActor(sessionClient);
  if (!actor) {
    return fail("UNAUTHENTICATED", "Candidate authentication required");
  }

  let digests: ReturnType<typeof buildUploadDigests>;
  try {
    digests = buildUploadDigests(actor.authUserId, trustedIp);
  } catch {
    return fail(
      "RATE_LIMIT_UNAVAILABLE",
      "Request protection is temporarily unavailable",
    );
  }

  const gate = await adminClient.rpc(
    "authorize_candidate_upload_completion_rate_limited",
    {
      p_actor_auth_user_id: actor.authUserId,
      p_identity_key_digest: digests.identityDigest,
      p_trusted_ip_key_digest: digests.ipDigest,
      p_candidate_form_session_id: input.sessionId,
      p_upload_reservation_id: input.reservationId,
    },
  );
  if (gate.error || !gate.data || typeof gate.data !== "object") {
    return fail(
      "RATE_LIMIT_UNAVAILABLE",
      "Request protection is temporarily unavailable",
    );
  }

  const gateResult = gate.data as RpcEnvelope<Record<string, never>>;
  if (gateResult.success !== true) {
    return fail(
      gateResult.error_code ?? "INTERNAL_ERROR",
      gateResult.message ?? "Unable to authorize upload completion",
      parseRetryAfter(gateResult.data?.retry_after_seconds),
    );
  }

  const inspectReservation =
    deps.inspectReservation ?? inspectUploadReservation;
  const inspected = await inspectReservation(input.reservationId);
  if (!inspected.success) {
    return fail(inspected.code, inspected.error);
  }

  const recordInspection =
    deps.recordInspection ?? recordInspectedUploadReservation;
  const recorded = await recordInspection(
    {
      uploadReservationId: input.reservationId,
      actualSizeBytes: inspected.data.actualSizeBytes,
      detectedMimeType: inspected.data.detectedMimeType,
      checksumSha256: inspected.data.checksumSha256,
      magicBytesVerified: inspected.data.magicBytesVerified,
    },
    adminClient,
  );
  if (!recorded.success) {
    return fail(recorded.error.code, recorded.error.message);
  }

  const scan = await adminClient.rpc(
    "request_candidate_document_scan_as_actor",
    {
      p_actor_auth_user_id: actor.authUserId,
      p_candidate_form_session_id: input.sessionId,
      p_upload_reservation_id: input.reservationId,
      p_action_code: input.actionCode ?? "ADD",
      p_target_logical_document_id: input.targetLogicalDocumentId ?? null,
    },
  );
  if (scan.error || !scan.data || typeof scan.data !== "object") {
    return fail("INTERNAL_ERROR", "Unable to create document scan request");
  }

  const scanResult = scan.data as RpcEnvelope<{
    kind: "PENDING_SCAN";
    document_scan_request_id: string;
    upload_reservation_id: string;
  }>;
  if (scanResult.success !== true || !scanResult.data) {
    return fail(
      scanResult.error_code ?? "INTERNAL_ERROR",
      scanResult.message ?? "Unable to create document scan request",
    );
  }

  return {
    success: true,
    data: {
      kind: "PENDING_SCAN",
      requestId: scanResult.data.document_scan_request_id,
      reservationId: scanResult.data.upload_reservation_id,
    },
  };
}
