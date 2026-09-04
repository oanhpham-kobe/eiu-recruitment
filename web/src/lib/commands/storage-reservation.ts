import "server-only";

import type { SupabaseClient } from "@supabase/supabase-js";
import { createCommandRunner } from "@/lib/commands/runner";
import {
  CommandErrorCode,
  CommandExecutionError,
  type CommandResult,
  type TrustedCommandDefinition,
  type VerifiedActor,
} from "@/lib/commands/types";
import {
  extractExtension,
  isAllowedMimeForExtension,
  isApprovedExtension,
} from "@/lib/storage/buckets";
import { createServerClient } from "@/lib/supabase/server";

const UUID_REGEX =
  /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

// -----------------------------------------------------------------------------
// Type Definitions
// -----------------------------------------------------------------------------

export type ReserveCandidateFormUploadInput = {
  candidateFormSessionId: string;
  intendedDocumentTypeId: string;
  originalFilename: string;
  declaredMimeType?: string | null;
  expectedMaxSize?: number;
  idempotencyKey?: string;
};

export type UploadReservationData = {
  upload_reservation_id: string;
  candidate_form_session_id: string;
  intended_document_type_id: string;
  temp_bucket: string;
  temp_path: string;
  original_filename: string;
  declared_mime_type: string | null;
  expected_max_size_bytes: number;
  status_code: string;
  expires_at: string;
};

export type CreateSignedUploadUrlInput = {
  uploadReservationId: string;
};

export type SignedUploadUrlData = {
  signedUrl: string;
  path: string;
  token: string;
  expiresAt: string;
  signedUploadExpiresAt: string;
};

export type RecordUploadCompletedInput = {
  uploadReservationId: string;
  actualSizeBytes: number;
  checksumSha256?: string | null;
};

export type RecordUploadCompletedData = {
  upload_reservation_id: string;
  status_code: "UPLOADED";
  malware_scan_status: "PENDING";
};

export type StageCandidateDocumentChangeInput = {
  candidateFormSessionId: string;
  actionCode: "ADD" | "REPLACE" | "DELETE";
  intendedDocumentTypeId: string;
  uploadReservationId?: string | null;
  targetLogicalDocumentId?: string | null;
};

export type StagedDocumentChangeData = {
  candidate_form_document_change_id: string;
  candidate_form_session_id: string;
  action_code: "ADD" | "REPLACE" | "DELETE";
  intended_document_type_id: string;
  upload_reservation_id: string | null;
  target_logical_document_id: string | null;
  status_code: "PENDING";
};

export type ValidateAndScanUploadInput = {
  uploadReservationId: string;
  detectedMimeType: string;
  actualSizeBytes: number;
  malwareScanStatus: "CLEAN" | "INFECTED" | "ERROR";
  magicBytesVerified: boolean;
  checksumSha256?: string | null;
};

export type ScanResultData = {
  upload_reservation_id: string;
  status_code: "VALIDATED" | "REJECTED";
  malware_scan_status: "CLEAN" | "INFECTED" | "ERROR";
};

export type ClaimedStorageCleanupJob = {
  storage_cleanup_id: string;
  source_type: string;
  bucket_name: string;
  object_path: string;
  reason_code: string;
  attempts: number;
  not_before: string;
  leased_until: string;
};

export type StorageReservationCommandDeps = {
  client?: SupabaseClient;
  resolveActor?: () => Promise<VerifiedActor | null>;
};

// -----------------------------------------------------------------------------
// Actor Resolution
// -----------------------------------------------------------------------------

async function defaultResolveActor(
  client?: SupabaseClient,
): Promise<VerifiedActor | null> {
  const supabase = client ?? (await createServerClient());
  const {
    data: { user },
    error,
  } = await supabase.auth.getUser();

  if (error || !user || !user.email) {
    return null;
  }

  const { data: candidate } = await supabase
    .from("candidates")
    .select("candidate_id, is_active")
    .eq("auth_user_id", user.id)
    .maybeSingle();

  if (!candidate || typeof candidate !== "object") {
    return null;
  }

  const isActive = Boolean(
    "is_active" in candidate && candidate.is_active === true,
  );

  return {
    authUserId: user.id,
    email: user.email,
    isActive,
    roles: ["CANDIDATE"],
    permissions: ["candidate.self"],
  };
}

// -----------------------------------------------------------------------------
// 1. Reserve Candidate Form Upload Command
// -----------------------------------------------------------------------------

export function createReserveCandidateFormUploadCommand(
  supabase: SupabaseClient,
): TrustedCommandDefinition<
  ReserveCandidateFormUploadInput,
  string | undefined,
  ReserveCandidateFormUploadInput,
  UploadReservationData
> {
  return {
    name: "reserve_candidate_form_upload",
    extractTarget(input) {
      return input.candidateFormSessionId;
    },
    authorize(actor) {
      const isCandidate =
        actor.roles.includes("CANDIDATE") ||
        actor.permissions.includes("candidate.self");

      if (!isCandidate) {
        return {
          authorized: false,
          code: CommandErrorCode.FORBIDDEN,
          reason: "Candidate authorization required",
        };
      }

      return { authorized: true };
    },
    validate(input) {
      if (
        !input.candidateFormSessionId ||
        !UUID_REGEX.test(input.candidateFormSessionId)
      ) {
        return {
          success: false,
          error: "Invalid candidateFormSessionId UUID",
        };
      }

      if (
        !input.intendedDocumentTypeId ||
        !UUID_REGEX.test(input.intendedDocumentTypeId)
      ) {
        return {
          success: false,
          error: "Invalid intendedDocumentTypeId UUID",
        };
      }

      const filename = input.originalFilename?.trim();
      if (!filename || filename.length > 255) {
        return {
          success: false,
          error: "Original filename must be between 1 and 255 characters",
        };
      }

      const ext = extractExtension(filename);
      if (!ext || !isApprovedExtension(ext)) {
        return {
          success: false,
          error:
            "File extension not permitted. Approved formats: PDF, DOC, DOCX, PPT, PPTX, PNG, JPG, JPEG",
        };
      }

      if (input.declaredMimeType) {
        if (!isAllowedMimeForExtension(ext, input.declaredMimeType)) {
          return {
            success: false,
            error: "Declared MIME type does not match approved extension list",
          };
        }
      }

      const size = input.expectedMaxSize ?? 5242880;
      if (size <= 0 || size > 5242880) {
        return {
          success: false,
          error: "Expected max size must be between 1 and 5242880 bytes (5 MB)",
        };
      }

      if (input.idempotencyKey && !UUID_REGEX.test(input.idempotencyKey)) {
        return {
          success: false,
          error: "Idempotency key must be a valid UUID",
        };
      }

      return {
        success: true,
        data: {
          ...input,
          originalFilename: filename,
          expectedMaxSize: size,
        },
      };
    },
    async execute(_actor, validated) {
      const { data, error } = await supabase.rpc(
        "reserve_candidate_form_upload",
        {
          p_candidate_form_session_id: validated.candidateFormSessionId,
          p_intended_document_type_id: validated.intendedDocumentTypeId,
          p_original_filename: validated.originalFilename,
          p_declared_mime_type: validated.declaredMimeType ?? null,
          p_expected_max_size_bytes: validated.expectedMaxSize ?? 5242880,
          p_idempotency_key: validated.idempotencyKey ?? crypto.randomUUID(),
        },
      );

      if (error) {
        throw new CommandExecutionError(
          CommandErrorCode.INTERNAL_ERROR,
          error.message,
          error,
        );
      }

      const result = data as {
        success: boolean;
        error_code?: string;
        message?: string;
        data?: UploadReservationData;
      };

      if (!result.success || !result.data) {
        const rawCode = result.error_code ? String(result.error_code) : "";
        const code =
          CommandErrorCode[rawCode as keyof typeof CommandErrorCode] ??
          CommandErrorCode.INTERNAL_ERROR;
        return {
          success: false,
          error: {
            code,
            message: result.message || "Failed to reserve upload",
          },
        };
      }

      return {
        success: true,
        data: result.data,
      };
    },
  };
}

// -----------------------------------------------------------------------------
// 2. Create Signed Upload URL For Reservation Command
// Derives bucket and path EXCLUSIVELY from reservation row; upsert: false;
// zero token/URL persistence.
// -----------------------------------------------------------------------------

export function createSignedUploadUrlForReservationCommand(
  supabase: SupabaseClient,
): TrustedCommandDefinition<
  CreateSignedUploadUrlInput,
  string | undefined,
  CreateSignedUploadUrlInput,
  SignedUploadUrlData
> {
  return {
    name: "create_signed_upload_url_for_reservation",
    extractTarget(input) {
      return input.uploadReservationId;
    },
    authorize(actor) {
      const isCandidate =
        actor.roles.includes("CANDIDATE") ||
        actor.permissions.includes("candidate.self");

      if (!isCandidate) {
        return {
          authorized: false,
          code: CommandErrorCode.FORBIDDEN,
          reason: "Candidate authorization required",
        };
      }

      return { authorized: true };
    },
    validate(input) {
      if (
        !input.uploadReservationId ||
        !UUID_REGEX.test(input.uploadReservationId)
      ) {
        return {
          success: false,
          error: "Invalid uploadReservationId UUID",
        };
      }
      return { success: true, data: input };
    },
    async execute(_actor, validated) {
      // Step 1: Pre-call durable token expiry registration via prepare_signed_upload RPC.
      // Locks reservation row in deterministic hierarchy and records signed_upload_expires_at
      // with latency buffer BEFORE Storage API is invoked.
      const { data: prepareData, error: prepareError } = await supabase.rpc(
        "prepare_signed_upload",
        {
          p_upload_reservation_id: validated.uploadReservationId,
        },
      );

      if (prepareError) {
        throw new CommandExecutionError(
          CommandErrorCode.INTERNAL_ERROR,
          prepareError.message,
          prepareError,
        );
      }

      const prepResult = prepareData as {
        success: boolean;
        error_code?: string;
        message?: string;
        data?: {
          upload_reservation_id: string;
          temp_bucket: string;
          temp_path: string;
          expires_at: string;
          signed_upload_expires_at: string;
        };
      };

      if (!prepResult.success || !prepResult.data) {
        const rawCode = prepResult.error_code
          ? String(prepResult.error_code)
          : "";
        const code =
          CommandErrorCode[rawCode as keyof typeof CommandErrorCode] ??
          CommandErrorCode.INTERNAL_ERROR;
        return {
          success: false,
          error: {
            code,
            message: prepResult.message || "Failed to prepare signed upload",
          },
        };
      }
      const res = prepResult.data;

      // Step 2: Mint signed upload URL using Storage API.
      // Bucket and path are derived EXCLUSIVELY from the database row.
      // upsert is strictly set to false.
      const { data: signData, error: signError } = await supabase.storage
        .from(res.temp_bucket)
        .createSignedUploadUrl(res.temp_path, { upsert: false });

      if (signError || !signData) {
        throw new CommandExecutionError(
          CommandErrorCode.INTERNAL_ERROR,
          signError?.message || "Storage service failed to generate signed URL",
          signError,
        );
      }

      // Step 3: Return signed URL and metadata.
      // Zero persistence or logging of token or signed URL.
      return {
        signedUrl: signData.signedUrl,
        path: signData.path,
        token: signData.token,
        expiresAt: res.expires_at,
        signedUploadExpiresAt: res.signed_upload_expires_at,
      };
    },
  };
}

// -----------------------------------------------------------------------------
// 3. Record Candidate Upload Completed Command
// -----------------------------------------------------------------------------

export function createRecordCandidateUploadCompletedCommand(
  supabase: SupabaseClient,
): TrustedCommandDefinition<
  RecordUploadCompletedInput,
  string | undefined,
  RecordUploadCompletedInput,
  RecordUploadCompletedData
> {
  return {
    name: "record_candidate_upload_completed",
    extractTarget(input) {
      return input.uploadReservationId;
    },
    authorize(actor) {
      const isCandidate =
        actor.roles.includes("CANDIDATE") ||
        actor.permissions.includes("candidate.self");

      if (!isCandidate) {
        return {
          authorized: false,
          code: CommandErrorCode.FORBIDDEN,
          reason: "Candidate authorization required",
        };
      }

      return { authorized: true };
    },
    validate(input) {
      if (
        !input.uploadReservationId ||
        !UUID_REGEX.test(input.uploadReservationId)
      ) {
        return {
          success: false,
          error: "Invalid uploadReservationId UUID",
        };
      }

      if (
        typeof input.actualSizeBytes !== "number" ||
        input.actualSizeBytes <= 0 ||
        input.actualSizeBytes > 5242880
      ) {
        return {
          success: false,
          error: "actualSizeBytes must be between 1 and 5242880 bytes (5 MB)",
        };
      }

      if (
        input.checksumSha256 &&
        !/^[0-9a-fA-F]{64}$/.test(input.checksumSha256)
      ) {
        return {
          success: false,
          error: "checksumSha256 must be a 64-character hexadecimal string",
        };
      }

      return { success: true, data: input };
    },
    async execute(_actor, validated) {
      const { data, error } = await supabase.rpc(
        "record_candidate_upload_completed",
        {
          p_upload_reservation_id: validated.uploadReservationId,
          p_actual_size_bytes: validated.actualSizeBytes,
          p_checksum_sha256: validated.checksumSha256 ?? null,
        },
      );

      if (error) {
        throw new CommandExecutionError(
          CommandErrorCode.INTERNAL_ERROR,
          error.message,
          error,
        );
      }

      const result = data as {
        success: boolean;
        error_code?: string;
        message?: string;
        data?: RecordUploadCompletedData;
      };

      if (!result.success || !result.data) {
        const rawCode = result.error_code ? String(result.error_code) : "";
        const code =
          CommandErrorCode[rawCode as keyof typeof CommandErrorCode] ??
          CommandErrorCode.INTERNAL_ERROR;
        return {
          success: false,
          error: {
            code,
            message: result.message || "Failed to record upload completion",
          },
        };
      }

      return {
        success: true,
        data: result.data,
      };
    },
  };
}

// -----------------------------------------------------------------------------
// 4. Stage Candidate Document Change Command
// -----------------------------------------------------------------------------

export function createStageCandidateDocumentChangeCommand(
  supabase: SupabaseClient,
): TrustedCommandDefinition<
  StageCandidateDocumentChangeInput,
  string | undefined,
  StageCandidateDocumentChangeInput,
  StagedDocumentChangeData
> {
  return {
    name: "stage_candidate_document_change",
    extractTarget(input) {
      return input.candidateFormSessionId;
    },
    authorize(actor) {
      const isCandidate =
        actor.roles.includes("CANDIDATE") ||
        actor.permissions.includes("candidate.self");

      if (!isCandidate) {
        return {
          authorized: false,
          code: CommandErrorCode.FORBIDDEN,
          reason: "Candidate authorization required",
        };
      }

      return { authorized: true };
    },
    validate(input) {
      if (
        !input.candidateFormSessionId ||
        !UUID_REGEX.test(input.candidateFormSessionId)
      ) {
        return {
          success: false,
          error: "Invalid candidateFormSessionId UUID",
        };
      }

      if (
        !input.intendedDocumentTypeId ||
        !UUID_REGEX.test(input.intendedDocumentTypeId)
      ) {
        return {
          success: false,
          error: "Invalid intendedDocumentTypeId UUID",
        };
      }

      if (!["ADD", "REPLACE", "DELETE"].includes(input.actionCode)) {
        return {
          success: false,
          error: "actionCode must be ADD, REPLACE, or DELETE",
        };
      }

      if (input.actionCode === "ADD") {
        if (!input.uploadReservationId) {
          return {
            success: false,
            error: "ADD action requires an uploadReservationId",
          };
        }
        if (input.targetLogicalDocumentId) {
          return {
            success: false,
            error: "ADD action cannot have a targetLogicalDocumentId",
          };
        }
      } else if (input.actionCode === "REPLACE") {
        if (!input.uploadReservationId || !input.targetLogicalDocumentId) {
          return {
            success: false,
            error:
              "REPLACE action requires both uploadReservationId and targetLogicalDocumentId",
          };
        }
      } else if (input.actionCode === "DELETE") {
        if (input.uploadReservationId) {
          return {
            success: false,
            error: "DELETE action cannot have an uploadReservationId",
          };
        }
        if (!input.targetLogicalDocumentId) {
          return {
            success: false,
            error: "DELETE action requires a targetLogicalDocumentId",
          };
        }
      }

      return { success: true, data: input };
    },
    async execute(_actor, validated) {
      const { data, error } = await supabase.rpc(
        "stage_candidate_document_change",
        {
          p_candidate_form_session_id: validated.candidateFormSessionId,
          p_action_code: validated.actionCode,
          p_intended_document_type_id: validated.intendedDocumentTypeId,
          p_upload_reservation_id: validated.uploadReservationId ?? null,
          p_target_logical_document_id:
            validated.targetLogicalDocumentId ?? null,
        },
      );

      if (error) {
        throw new CommandExecutionError(
          CommandErrorCode.INTERNAL_ERROR,
          error.message,
          error,
        );
      }

      const result = data as {
        success: boolean;
        error_code?: string;
        message?: string;
        data?: StagedDocumentChangeData;
      };

      if (!result.success || !result.data) {
        const rawCode = result.error_code ? String(result.error_code) : "";
        const code =
          CommandErrorCode[rawCode as keyof typeof CommandErrorCode] ??
          CommandErrorCode.INTERNAL_ERROR;
        return {
          success: false,
          error: {
            code,
            message: result.message || "Failed to stage document change",
          },
        };
      }

      return {
        success: true,
        data: result.data,
      };
    },
  };
}

// -----------------------------------------------------------------------------
// 5. Worker-Only Validate & Scan Command (Service Role Client)
// -----------------------------------------------------------------------------

export function createValidateAndScanUploadCommand(
  supabaseAdmin: SupabaseClient,
): TrustedCommandDefinition<
  ValidateAndScanUploadInput,
  string | undefined,
  ValidateAndScanUploadInput,
  ScanResultData
> {
  return {
    name: "validate_and_scan_upload_reservation",
    extractTarget(input) {
      return input.uploadReservationId;
    },
    authorize(actor) {
      // Worker-only execution: requires SERVICE_ROLE or root admin
      const isPrivileged =
        actor.roles.includes("SERVICE_ROLE") ||
        actor.roles.includes("ROOT_ADMIN") ||
        actor.permissions.includes("admin.full");

      if (!isPrivileged) {
        return {
          authorized: false,
          code: CommandErrorCode.FORBIDDEN,
          reason: "Trusted worker authorization required",
        };
      }

      return { authorized: true };
    },
    validate(input) {
      if (
        !input.uploadReservationId ||
        !UUID_REGEX.test(input.uploadReservationId)
      ) {
        return {
          success: false,
          error: "Invalid uploadReservationId UUID",
        };
      }

      if (!input.detectedMimeType?.trim()) {
        return {
          success: false,
          error: "detectedMimeType is required",
        };
      }

      if (
        typeof input.actualSizeBytes !== "number" ||
        input.actualSizeBytes <= 0 ||
        input.actualSizeBytes > 5242880
      ) {
        return {
          success: false,
          error: "actualSizeBytes must be between 1 and 5242880 bytes",
        };
      }

      if (!["CLEAN", "INFECTED", "ERROR"].includes(input.malwareScanStatus)) {
        return {
          success: false,
          error: "malwareScanStatus must be CLEAN, INFECTED, or ERROR",
        };
      }

      if (typeof input.magicBytesVerified !== "boolean") {
        return {
          success: false,
          error: "magicBytesVerified boolean flag is required",
        };
      }

      return { success: true, data: input };
    },
    async execute(_actor, validated) {
      const { data, error } = await supabaseAdmin.rpc(
        "validate_and_scan_upload_reservation",
        {
          p_upload_reservation_id: validated.uploadReservationId,
          p_detected_mime_type: validated.detectedMimeType,
          p_actual_size_bytes: validated.actualSizeBytes,
          p_malware_scan_status: validated.malwareScanStatus,
          p_magic_bytes_verified: validated.magicBytesVerified,
          p_checksum_sha256: validated.checksumSha256 ?? null,
        },
      );

      if (error) {
        throw new CommandExecutionError(
          CommandErrorCode.INTERNAL_ERROR,
          error.message,
          error,
        );
      }

      const result = data as {
        success: boolean;
        error_code?: string;
        message?: string;
        data?: ScanResultData;
      };

      if (!result.success || !result.data) {
        const rawCode = result.error_code ? String(result.error_code) : "";
        const code =
          CommandErrorCode[rawCode as keyof typeof CommandErrorCode] ??
          CommandErrorCode.INTERNAL_ERROR;
        return {
          success: false,
          error: {
            code,
            message: result.message || "Validation and scan failed",
          },
        };
      }

      return {
        success: true,
        data: result.data,
      };
    },
  };
}

// -----------------------------------------------------------------------------
// 6. Public Helper Functions
// -----------------------------------------------------------------------------

export async function reserveCandidateFormUpload(
  input: ReserveCandidateFormUploadInput,
  deps: StorageReservationCommandDeps = {},
): Promise<CommandResult<UploadReservationData>> {
  const supabase = deps.client ?? (await createServerClient());
  const resolveActor =
    deps.resolveActor ?? (() => defaultResolveActor(supabase));
  const runner = createCommandRunner({ resolveActor });
  return runner(createReserveCandidateFormUploadCommand(supabase), input);
}

export async function createSignedUploadUrlForReservation(
  input: CreateSignedUploadUrlInput,
  deps: StorageReservationCommandDeps = {},
): Promise<CommandResult<SignedUploadUrlData>> {
  const supabase = deps.client ?? (await createServerClient());
  const resolveActor =
    deps.resolveActor ?? (() => defaultResolveActor(supabase));
  const runner = createCommandRunner({ resolveActor });
  return runner(createSignedUploadUrlForReservationCommand(supabase), input);
}

export async function recordCandidateUploadCompleted(
  input: RecordUploadCompletedInput,
  deps: StorageReservationCommandDeps = {},
): Promise<CommandResult<RecordUploadCompletedData>> {
  const supabase = deps.client ?? (await createServerClient());
  const resolveActor =
    deps.resolveActor ?? (() => defaultResolveActor(supabase));
  const runner = createCommandRunner({ resolveActor });
  return runner(createRecordCandidateUploadCompletedCommand(supabase), input);
}

export async function stageCandidateDocumentChange(
  input: StageCandidateDocumentChangeInput,
  deps: StorageReservationCommandDeps = {},
): Promise<CommandResult<StagedDocumentChangeData>> {
  const supabase = deps.client ?? (await createServerClient());
  const resolveActor =
    deps.resolveActor ?? (() => defaultResolveActor(supabase));
  const runner = createCommandRunner({ resolveActor });
  return runner(createStageCandidateDocumentChangeCommand(supabase), input);
}

export async function validateAndScanUploadReservation(
  input: ValidateAndScanUploadInput,
  deps: {
    client: SupabaseClient; // Requires service role client
    resolveActor?: () => Promise<VerifiedActor | null>;
  },
): Promise<CommandResult<ScanResultData>> {
  const resolveActor =
    deps.resolveActor ??
    (async () => ({
      authUserId: "00000000-0000-0000-0000-000000000000",
      email: "service-worker@internal",
      isActive: true,
      roles: ["SERVICE_ROLE"],
      permissions: ["admin.full"],
    }));
  const runner = createCommandRunner({ resolveActor });
  return runner(createValidateAndScanUploadCommand(deps.client), input);
}

export async function claimDueStorageCleanupJobs(
  limit = 10,
  leaseSeconds = 300,
  supabaseServiceClient: SupabaseClient,
): Promise<ClaimedStorageCleanupJob[]> {
  const { data, error } = await supabaseServiceClient.rpc(
    "claim_due_storage_cleanup_jobs",
    {
      p_limit: limit,
      p_lease_seconds: leaseSeconds,
    },
  );

  if (error) {
    throw new Error(`claim_due_storage_cleanup_jobs error: ${error.message}`);
  }

  const result = data as {
    success: boolean;
    data?: ClaimedStorageCleanupJob[];
  };

  return result.data ?? [];
}

export async function completeStorageCleanupJob(
  storageCleanupId: string,
  success: boolean,
  errorText: string | null = null,
  supabaseServiceClient: SupabaseClient,
): Promise<void> {
  const { error } = await supabaseServiceClient.rpc(
    "complete_storage_cleanup_job",
    {
      p_storage_cleanup_id: storageCleanupId,
      p_success: success,
      p_error: errorText,
    },
  );

  if (error) {
    throw new Error(`complete_storage_cleanup_job error: ${error.message}`);
  }
}
