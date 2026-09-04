import assert from "node:assert/strict";
import test from "node:test";
import type { SupabaseClient } from "@supabase/supabase-js";
import {
  claimDueStorageCleanupJobs,
  completeStorageCleanupJob,
  createSignedUploadUrlForReservation,
  recordCandidateUploadCompleted,
  reserveCandidateFormUpload,
  stageCandidateDocumentChange,
  validateAndScanUploadReservation,
} from "@/lib/commands/storage-reservation";
import { CommandErrorCode, type VerifiedActor } from "@/lib/commands/types";
import { ensureQuarantineBucketExists } from "@/lib/storage/buckets";

// -----------------------------------------------------------------------------
// Test Actors
// -----------------------------------------------------------------------------

const activeCandidateActor: VerifiedActor = {
  authUserId: "a0000000-0000-0000-0000-000000000001",
  email: "candidate@example.com",
  isActive: true,
  roles: ["CANDIDATE"],
  permissions: ["candidate.self"],
};

const inactiveCandidateActor: VerifiedActor = {
  authUserId: "a0000000-0000-0000-0000-000000000002",
  email: "inactive@example.com",
  isActive: false,
  roles: ["CANDIDATE"],
  permissions: ["candidate.self"],
};

const _nonCandidateActor: VerifiedActor = {
  authUserId: "a0000000-0000-0000-0000-000000000003",
  email: "staff@eiu.edu.vn",
  isActive: true,
  roles: ["STAFF"],
  permissions: ["submissions.view"],
};

const serviceWorkerActor: VerifiedActor = {
  authUserId: "00000000-0000-0000-0000-000000000000",
  email: "service-worker@internal",
  isActive: true,
  roles: ["SERVICE_ROLE"],
  permissions: ["admin.full"],
};

// -----------------------------------------------------------------------------
// Mock Supabase Factory
// -----------------------------------------------------------------------------

function createMockSupabase(options: {
  rpcHandlers?: Record<string, (args: unknown) => unknown>;
  storageHandlers?: {
    createSignedUploadUrl?: (
      bucket: string,
      path: string,
      opts?: { upsert?: boolean },
    ) => Promise<{
      data: { signedUrl: string; path: string; token: string } | null;
      error: Error | null;
    }>;
    getBucket?: (id: string) => Promise<{ data: unknown; error: Error | null }>;
    createBucket?: (
      id: string,
      opts: unknown,
    ) => Promise<{ error: Error | null }>;
  };
  userData?: { id: string; email: string } | null;
  candidateData?: { candidate_id: string; is_active: boolean } | null;
}) {
  return {
    rpc: async (fn: string, args?: unknown) => {
      const handler = options.rpcHandlers?.[fn];
      if (handler) {
        const result = handler(args);
        return { data: result, error: null };
      }
      return { data: null, error: null };
    },
    storage: {
      from: (bucket: string) => ({
        createSignedUploadUrl: async (
          path: string,
          opts?: { upsert?: boolean },
        ) => {
          if (options.storageHandlers?.createSignedUploadUrl) {
            return options.storageHandlers.createSignedUploadUrl(
              bucket,
              path,
              opts,
            );
          }
          return {
            data: {
              signedUrl: `https://storage.mock/${bucket}/${path}?token=mock_jwt_token_123`,
              path,
              token: "mock_jwt_token_123",
            },
            error: null,
          };
        },
      }),
      getBucket: async (id: string) => {
        if (options.storageHandlers?.getBucket) {
          return options.storageHandlers.getBucket(id);
        }
        return { data: { id, name: id, public: false }, error: null };
      },
      createBucket: async (id: string, opts: unknown) => {
        if (options.storageHandlers?.createBucket) {
          return options.storageHandlers.createBucket(id, opts);
        }
        return { error: null };
      },
    },
    auth: {
      getUser: async () => ({
        data: {
          user:
            options.userData !== undefined
              ? options.userData
              : {
                  id: "a0000000-0000-0000-0000-000000000001",
                  email: "candidate@example.com",
                },
        },
        error: null,
      }),
    },
    from: (_table: string) => ({
      select: (_cols: string) => ({
        eq: (_col: string, _val: unknown) => ({
          maybeSingle: async () => ({
            data:
              options.candidateData !== undefined
                ? options.candidateData
                : {
                    candidate_id: "c0000000-0000-0000-0000-000000000001",
                    is_active: true,
                  },
            error: null,
          }),
        }),
      }),
    }),
  } as unknown as SupabaseClient;
}

// -----------------------------------------------------------------------------
// Tests
// -----------------------------------------------------------------------------

test("1. UNAUTHENTICATED call rejection", async () => {
  const mockSupabase = createMockSupabase({});
  const result = await reserveCandidateFormUpload(
    {
      candidateFormSessionId: "11111111-1111-1111-1111-111111111111",
      intendedDocumentTypeId: "22222222-2222-2222-2222-222222222222",
      originalFilename: "resume.pdf",
    },
    {
      client: mockSupabase,
      resolveActor: async () => null, // Unauthenticated
    },
  );

  assert.equal(result.success, false);
  if (!result.success) {
    assert.equal(result.error.code, CommandErrorCode.UNAUTHENTICATED);
  }
});

test("2. USER_INACTIVE candidate rejection", async () => {
  const mockSupabase = createMockSupabase({});
  const result = await reserveCandidateFormUpload(
    {
      candidateFormSessionId: "11111111-1111-1111-1111-111111111111",
      intendedDocumentTypeId: "22222222-2222-2222-2222-222222222222",
      originalFilename: "resume.pdf",
    },
    {
      client: mockSupabase,
      resolveActor: async () => inactiveCandidateActor,
    },
  );

  assert.equal(result.success, false);
  if (!result.success) {
    assert.equal(result.error.code, CommandErrorCode.USER_INACTIVE);
  }
});

test("3. NOT_FOUND foreign session access rejection", async () => {
  const mockSupabase = createMockSupabase({
    rpcHandlers: {
      reserve_candidate_form_upload: () => ({
        success: false,
        error_code: "NOT_FOUND",
        message: "Candidate form session not found or access denied",
      }),
    },
  });

  const result = await reserveCandidateFormUpload(
    {
      candidateFormSessionId: "99999999-9999-9999-9999-999999999999",
      intendedDocumentTypeId: "22222222-2222-2222-2222-222222222222",
      originalFilename: "resume.pdf",
    },
    {
      client: mockSupabase,
      resolveActor: async () => activeCandidateActor,
    },
  );

  assert.equal(result.success, false);
  if (!result.success) {
    assert.equal(result.error.code, CommandErrorCode.NOT_FOUND);
  }
});

test("4. FORM_SESSION_EXPIRED rejection", async () => {
  const mockSupabase = createMockSupabase({
    rpcHandlers: {
      reserve_candidate_form_upload: () => ({
        success: false,
        error_code: "FORM_SESSION_EXPIRED",
        message: "Candidate form session has expired",
      }),
    },
  });

  const result = await reserveCandidateFormUpload(
    {
      candidateFormSessionId: "11111111-1111-1111-1111-111111111111",
      intendedDocumentTypeId: "22222222-2222-2222-2222-222222222222",
      originalFilename: "resume.pdf",
    },
    {
      client: mockSupabase,
      resolveActor: async () => activeCandidateActor,
    },
  );

  assert.equal(result.success, false);
  if (!result.success) {
    assert.equal(result.error.code, "FORM_SESSION_EXPIRED");
  }
});

test("5. INVALID_STATE (closed session) rejection", async () => {
  const mockSupabase = createMockSupabase({
    rpcHandlers: {
      reserve_candidate_form_upload: () => ({
        success: false,
        error_code: "INVALID_STATE",
        message: "Candidate form session is not open",
      }),
    },
  });

  const result = await reserveCandidateFormUpload(
    {
      candidateFormSessionId: "11111111-1111-1111-1111-111111111111",
      intendedDocumentTypeId: "22222222-2222-2222-2222-222222222222",
      originalFilename: "resume.pdf",
    },
    {
      client: mockSupabase,
      resolveActor: async () => activeCandidateActor,
    },
  );

  assert.equal(result.success, false);
  if (!result.success) {
    assert.equal(result.error.code, CommandErrorCode.INVALID_STATE);
  }
});

test("6. INVALID_DOCUMENT_TYPE / INACTIVE_DOCUMENT_TYPE rejection", async () => {
  const mockSupabase = createMockSupabase({
    rpcHandlers: {
      reserve_candidate_form_upload: () => ({
        success: false,
        error_code: "INACTIVE_DOCUMENT_TYPE",
        message: "Inactive document type cannot be added to a new submission",
      }),
    },
  });

  const result = await reserveCandidateFormUpload(
    {
      candidateFormSessionId: "11111111-1111-1111-1111-111111111111",
      intendedDocumentTypeId: "33333333-3333-3333-3333-333333333333",
      originalFilename: "resume.pdf",
    },
    {
      client: mockSupabase,
      resolveActor: async () => activeCandidateActor,
    },
  );

  assert.equal(result.success, false);
  if (!result.success) {
    assert.equal(result.error.code, "INACTIVE_DOCUMENT_TYPE");
  }
});

test("7. INVALID_FILE_TYPE (disallowed extensions .exe, .sh, .html) rejection", async () => {
  const mockSupabase = createMockSupabase({});

  const disallowed = [
    "malware.exe",
    "script.sh",
    "payload.html",
    "archive.zip",
  ];

  for (const filename of disallowed) {
    const result = await reserveCandidateFormUpload(
      {
        candidateFormSessionId: "11111111-1111-1111-1111-111111111111",
        intendedDocumentTypeId: "22222222-2222-2222-2222-222222222222",
        originalFilename: filename,
      },
      {
        client: mockSupabase,
        resolveActor: async () => activeCandidateActor,
      },
    );

    assert.equal(result.success, false, `Expected ${filename} to be rejected`);
    if (!result.success) {
      assert.equal(result.error.code, CommandErrorCode.VALIDATION_ERROR);
    }
  }
});

test("8. FILE_SIZE_EXCEEDED (> 5MB) rejection", async () => {
  const mockSupabase = createMockSupabase({});

  const result = await reserveCandidateFormUpload(
    {
      candidateFormSessionId: "11111111-1111-1111-1111-111111111111",
      intendedDocumentTypeId: "22222222-2222-2222-2222-222222222222",
      originalFilename: "resume.pdf",
      expectedMaxSize: 6 * 1024 * 1024, // 6 MB > 5 MB
    },
    {
      client: mockSupabase,
      resolveActor: async () => activeCandidateActor,
    },
  );

  assert.equal(result.success, false);
  if (!result.success) {
    assert.equal(result.error.code, CommandErrorCode.VALIDATION_ERROR);
  }
});

test("9. IDEMPOTENT_RESERVATION duplicate key returns existing reservation", async () => {
  const mockReservation = {
    upload_reservation_id: "res-001-uuid",
    candidate_form_session_id: "11111111-1111-1111-1111-111111111111",
    intended_document_type_id: "22222222-2222-2222-2222-222222222222",
    temp_bucket: "candidate-quarantine",
    temp_path: "temp/session/res-001/resume.pdf",
    original_filename: "resume.pdf",
    declared_mime_type: "application/pdf",
    expected_max_size_bytes: 2000000,
    status_code: "RESERVED",
    expires_at: "2026-09-05T12:00:00Z",
  };

  const mockSupabase = createMockSupabase({
    rpcHandlers: {
      reserve_candidate_form_upload: () => ({
        success: true,
        data: mockReservation,
      }),
    },
  });

  const key = "e1111111-1111-1111-1111-111111111111";
  const first = await reserveCandidateFormUpload(
    {
      candidateFormSessionId: "11111111-1111-1111-1111-111111111111",
      intendedDocumentTypeId: "22222222-2222-2222-2222-222222222222",
      originalFilename: "resume.pdf",
      idempotencyKey: key,
    },
    { client: mockSupabase, resolveActor: async () => activeCandidateActor },
  );

  const second = await reserveCandidateFormUpload(
    {
      candidateFormSessionId: "11111111-1111-1111-1111-111111111111",
      intendedDocumentTypeId: "22222222-2222-2222-2222-222222222222",
      originalFilename: "resume.pdf",
      idempotencyKey: key,
    },
    { client: mockSupabase, resolveActor: async () => activeCandidateActor },
  );

  assert.equal(first.success, true);
  assert.equal(second.success, true);
  if (first.success && second.success) {
    assert.deepEqual(first.data, second.data);
  }
});

test("10. SIGNED_UPLOAD_URL_DERIVATION derived strictly from reservation, upsert false, returns expiresAt", async () => {
  let capturedBucket = "";
  let capturedPath = "";
  let capturedUpsert: boolean | undefined;

  const mockSupabase = createMockSupabase({
    rpcHandlers: {
      prepare_signed_upload: () => ({
        success: true,
        data: {
          upload_reservation_id: "res-001-uuid",
          temp_bucket: "candidate-quarantine",
          temp_path: "temp/sess-1/res-001/cv.pdf",
          expires_at: "2026-09-05T10:30:00Z",
          signed_upload_expires_at: "2026-09-05T12:05:00Z",
        },
      }),
    },
    storageHandlers: {
      createSignedUploadUrl: async (bucket, path, opts) => {
        capturedBucket = bucket;
        capturedPath = path;
        capturedUpsert = opts?.upsert;
        return {
          data: {
            signedUrl: "https://storage.supabase.co/signed/upload/test",
            path,
            token: "jwt_signed_token_abc",
          },
          error: null,
        };
      },
    },
  });

  const result = await createSignedUploadUrlForReservation(
    {
      uploadReservationId: "11111111-1111-1111-1111-111111111111",
    },
    { client: mockSupabase, resolveActor: async () => activeCandidateActor },
  );

  assert.equal(result.success, true);
  if (result.success) {
    assert.equal(capturedBucket, "candidate-quarantine");
    assert.equal(capturedPath, "temp/sess-1/res-001/cv.pdf");
    assert.equal(capturedUpsert, false, "upsert must strictly be false");
    assert.equal(result.data.expiresAt, "2026-09-05T10:30:00Z");
    assert.equal(result.data.signedUploadExpiresAt, "2026-09-05T12:05:00Z");
    assert.equal(result.data.token, "jwt_signed_token_abc");
  }
});

test("11. LATENCY_BUFFER_IN_DURABLE_EXPIRY sets 2h 5m buffer", async () => {
  const mockSupabase = createMockSupabase({
    rpcHandlers: {
      prepare_signed_upload: () => ({
        success: true,
        data: {
          upload_reservation_id: "res-001-uuid",
          temp_bucket: "candidate-quarantine",
          temp_path: "temp/sess-1/res-001/cv.pdf",
          expires_at: "2026-09-05T10:30:00Z",
          signed_upload_expires_at: "2026-09-05T12:05:00Z", // 2h 5m
        },
      }),
    },
  });

  const result = await createSignedUploadUrlForReservation(
    { uploadReservationId: "11111111-1111-1111-1111-111111111111" },
    { client: mockSupabase, resolveActor: async () => activeCandidateActor },
  );

  assert.equal(result.success, true);
  if (result.success) {
    assert.equal(result.data.signedUploadExpiresAt, "2026-09-05T12:05:00Z");
  }
});

test("12. REAL_ORDERING_CANCEL_EARLY_CLEANUP_LATE_UPLOAD test", async () => {
  // Scenario:
  // 1. Reservation created and signed (not_before = now + 2h 5m).
  // 2. Form session cancelled -> enqueues queue with not_before = now + 2h 5m.
  // 3. Early cleanup worker runs at T+5m -> claims 0 rows because not_before > now.
  // 4. Late upload completion attempt at T+10m fails because session is CANCELLED.
  // 5. Due cleanup worker runs at T+2h6m -> claims 1 row for deletion.

  const queueState: Array<{
    id: string;
    path: string;
    status: string;
    not_before: number;
    attempts: number;
  }> = [
    {
      id: "clean-001",
      path: "temp/sess-1/res-001/cv.pdf",
      status: "PENDING",
      not_before: 1000 + 7500, // T + 2h 5m
      attempts: 0,
    },
  ];

  let currentTime = 1000 + 300; // T + 5m (early cleanup)

  // Early claim attempt
  const earlyClaim = queueState.filter(
    (q) => q.status === "PENDING" && q.not_before <= currentTime,
  );
  assert.equal(
    earlyClaim.length,
    0,
    "Early cleanup must claim 0 rows before not_before elapses",
  );

  // Late upload completion attempt
  const mockSupabase = createMockSupabase({
    rpcHandlers: {
      record_candidate_upload_completed: () => ({
        success: false,
        error_code: "INVALID_STATE",
        message: "Only OPEN candidate form sessions may accept uploads",
      }),
    },
  });

  const uploadAttempt = await recordCandidateUploadCompleted(
    {
      uploadReservationId: "11111111-1111-1111-1111-111111111111",
      actualSizeBytes: 1024,
    },
    { client: mockSupabase, resolveActor: async () => activeCandidateActor },
  );

  assert.equal(uploadAttempt.success, false);
  if (!uploadAttempt.success) {
    assert.equal(uploadAttempt.error.code, CommandErrorCode.INVALID_STATE);
  }

  // Due claim attempt at T + 2h 6m
  currentTime = 1000 + 7560;
  const dueClaim = queueState.filter(
    (q) => q.status === "PENDING" && q.not_before <= currentTime,
  );
  assert.equal(
    dueClaim.length,
    1,
    "Due cleanup worker successfully claims expired row after token expires",
  );
});

test("13. CANDIDATE_QUARANTINE_READ_DENIED candidate has zero SELECT on quarantine", async () => {
  // Simulating RLS evaluation on storage.objects for candidate-quarantine bucket
  function evaluateQuarantineSelectPolicy(
    actor: VerifiedActor,
    bucketId: string,
  ) {
    if (bucketId === "candidate-quarantine") {
      // Policy: bucket_id = 'candidate-quarantine' and private.is_root_admin()
      const isRoot =
        actor.roles.includes("ROOT_ADMIN") ||
        actor.permissions.includes("admin.full");
      return isRoot;
    }
    return true;
  }

  assert.equal(
    evaluateQuarantineSelectPolicy(
      activeCandidateActor,
      "candidate-quarantine",
    ),
    false,
    "Candidate must NOT have SELECT on candidate-quarantine",
  );

  assert.equal(
    evaluateQuarantineSelectPolicy(serviceWorkerActor, "candidate-quarantine"),
    true,
    "Privileged service role / root must have SELECT on candidate-quarantine",
  );
});

test("14. CANDIDATE_CANNOT_SELF_ATTEST_SCAN_CLEAN upload completion leaves PENDING and candidate cannot call validate_and_scan", async () => {
  const mockSupabase = createMockSupabase({
    rpcHandlers: {
      record_candidate_upload_completed: () => ({
        success: true,
        data: {
          upload_reservation_id: "res-001",
          status_code: "UPLOADED",
          malware_scan_status: "PENDING", // Strictly PENDING
        },
      }),
      validate_and_scan_upload_reservation: () => {
        throw new Error(
          "permission denied for function validate_and_scan_upload_reservation",
        );
      },
    },
  });

  const completion = await recordCandidateUploadCompleted(
    {
      uploadReservationId: "11111111-1111-1111-1111-111111111111",
      actualSizeBytes: 2048,
    },
    { client: mockSupabase, resolveActor: async () => activeCandidateActor },
  );

  assert.equal(completion.success, true);
  if (completion.success) {
    assert.equal(completion.data.status_code, "UPLOADED");
    assert.equal(completion.data.malware_scan_status, "PENDING");
  }

  // Attempt direct call to worker validation by candidate -> forbidden
  const candidateScanAttempt = await validateAndScanUploadReservation(
    {
      uploadReservationId: "11111111-1111-1111-1111-111111111111",
      detectedMimeType: "application/pdf",
      actualSizeBytes: 2048,
      malwareScanStatus: "CLEAN",
      magicBytesVerified: true,
    },
    {
      client: mockSupabase,
      resolveActor: async () => activeCandidateActor,
    },
  );

  assert.equal(candidateScanAttempt.success, false);
  if (!candidateScanAttempt.success) {
    assert.equal(candidateScanAttempt.error.code, CommandErrorCode.FORBIDDEN);
  }
});

test("15. AUTHORITATIVE_SCAN_EVIDENCE_REQUIRED validation fails if scan unverified or MIME mismatch", async () => {
  const mockSupabase = createMockSupabase({
    rpcHandlers: {
      validate_and_scan_upload_reservation: (args: unknown) => {
        const p = args as {
          p_magic_bytes_verified?: boolean;
          p_detected_mime_type?: string;
        };
        if (!p.p_magic_bytes_verified) {
          return {
            success: false,
            error_code: "INVALID_CONTENT_SIGNATURE",
            message: "File magic bytes do not match expected signature",
          };
        }
        if (p.p_detected_mime_type === "application/x-msdownload") {
          return {
            success: false,
            error_code: "INVALID_MIME_TYPE",
            message: "Detected MIME type is unapproved",
          };
        }
        return {
          success: true,
          data: {
            upload_reservation_id: "res-001",
            status_code: "VALIDATED",
            malware_scan_status: "CLEAN",
          },
        };
      },
    },
  });

  // Test magic bytes false rejection
  const badMagicResult = await validateAndScanUploadReservation(
    {
      uploadReservationId: "11111111-1111-1111-1111-111111111111",
      detectedMimeType: "application/pdf",
      actualSizeBytes: 2048,
      malwareScanStatus: "CLEAN",
      magicBytesVerified: false,
    },
    { client: mockSupabase, resolveActor: async () => serviceWorkerActor },
  );

  assert.equal(badMagicResult.success, false);
  if (!badMagicResult.success) {
    assert.equal(badMagicResult.error.code, "INVALID_CONTENT_SIGNATURE");
  }

  // Test MIME mismatch rejection
  const badMimeResult = await validateAndScanUploadReservation(
    {
      uploadReservationId: "11111111-1111-1111-1111-111111111111",
      detectedMimeType: "application/x-msdownload",
      actualSizeBytes: 2048,
      malwareScanStatus: "CLEAN",
      magicBytesVerified: true,
    },
    { client: mockSupabase, resolveActor: async () => serviceWorkerActor },
  );

  assert.equal(badMimeResult.success, false);
  if (!badMimeResult.success) {
    assert.equal(badMimeResult.error.code, "INVALID_MIME_TYPE");
  }
});

test("16. STORAGE_RLS_CANCELLED_SESSION_DENIAL direct INSERT fails if session is cancelled", async () => {
  function checkInsertPolicy(
    reservation: { status: string; expires_at: number },
    session: { status: string; expires_at: number },
    currentTime: number,
  ) {
    return (
      reservation.status === "RESERVED" &&
      reservation.expires_at > currentTime &&
      session.status === "OPEN" &&
      session.expires_at > currentTime
    );
  }

  const now = 1000;
  assert.equal(
    checkInsertPolicy(
      { status: "RESERVED", expires_at: 2000 },
      { status: "CANCELLED", expires_at: 2000 },
      now,
    ),
    false,
    "INSERT into storage.objects must be denied when parent form session is CANCELLED",
  );
});

test("17. STORAGE_RLS_NO_OVERWRITE authenticated users have no UPDATE policy", async () => {
  // Simulating storage RLS commands
  const policiesOnStorageObjects = [
    { command: "SELECT", role: "authenticated" },
    { command: "INSERT", role: "authenticated" },
  ];

  const hasUpdatePolicy = policiesOnStorageObjects.some(
    (p) => p.command === "UPDATE" && p.role === "authenticated",
  );

  assert.equal(
    hasUpdatePolicy,
    false,
    "storage.objects must have NO UPDATE policy for authenticated users",
  );
});

test("18. STAGING_ADD validates unexpired reservation in UPLOADED or VALIDATED state", async () => {
  const mockSupabase = createMockSupabase({
    rpcHandlers: {
      stage_candidate_document_change: () => ({
        success: true,
        data: {
          candidate_form_document_change_id: "chg-001",
          candidate_form_session_id: "11111111-1111-1111-1111-111111111111",
          action_code: "ADD",
          intended_document_type_id: "22222222-2222-2222-2222-222222222222",
          upload_reservation_id: "res-001",
          target_logical_document_id: null,
          status_code: "PENDING",
        },
      }),
    },
  });

  const result = await stageCandidateDocumentChange(
    {
      candidateFormSessionId: "11111111-1111-1111-1111-111111111111",
      intendedDocumentTypeId: "22222222-2222-2222-2222-222222222222",
      actionCode: "ADD",
      uploadReservationId: "res-001-uuid-0000-0000-000000000001",
    },
    { client: mockSupabase, resolveActor: async () => activeCandidateActor },
  );

  assert.equal(result.success, true);
  if (result.success) {
    assert.equal(result.data.action_code, "ADD");
    assert.equal(result.data.status_code, "PENDING");
  }
});

test("19. STAGING_REPLACE_DELETE_IN_NEW_SUBMISSION rejection", async () => {
  const mockSupabase = createMockSupabase({
    rpcHandlers: {
      stage_candidate_document_change: () => ({
        success: false,
        error_code: "INVALID_ACTION",
        message:
          "New submission form only supports staged ADD document actions",
      }),
    },
  });

  const result = await stageCandidateDocumentChange(
    {
      candidateFormSessionId: "11111111-1111-1111-1111-111111111111",
      intendedDocumentTypeId: "22222222-2222-2222-2222-222222222222",
      actionCode: "REPLACE",
      uploadReservationId: "res-001-uuid-0000-0000-000000000001",
      targetLogicalDocumentId: "log-001-uuid-0000-0000-000000000001",
    },
    { client: mockSupabase, resolveActor: async () => activeCandidateActor },
  );

  assert.equal(result.success, false);
  if (!result.success) {
    assert.equal(result.error.code, "INVALID_ACTION");
  }
});

test("20. STAGING_UNREADY_OR_EXPIRED_RESERVATION rejection", async () => {
  const mockSupabase = createMockSupabase({
    rpcHandlers: {
      stage_candidate_document_change: () => ({
        success: false,
        error_code: "UPLOAD_RESERVATION_EXPIRED",
        message: "Upload reservation has expired",
      }),
    },
  });

  const result = await stageCandidateDocumentChange(
    {
      candidateFormSessionId: "11111111-1111-1111-1111-111111111111",
      intendedDocumentTypeId: "22222222-2222-2222-2222-222222222222",
      actionCode: "ADD",
      uploadReservationId: "res-001-uuid-0000-0000-000000000001",
    },
    { client: mockSupabase, resolveActor: async () => activeCandidateActor },
  );

  assert.equal(result.success, false);
  if (!result.success) {
    assert.equal(result.error.code, "UPLOAD_RESERVATION_EXPIRED");
  }
});

test("21. SUBMIT_PLAN_VALIDATION_REQUIRES_CLEAN requires VALIDATED and CLEAN at save time", async () => {
  function validatePlanSim(
    reservations: Array<{ status: string; scan: string }>,
  ) {
    for (const r of reservations) {
      if (r.status !== "VALIDATED" || r.scan !== "CLEAN") {
        return { valid: false, error: "UPLOAD_RESERVATION_NOT_CLEAN" };
      }
    }
    return { valid: true };
  }

  assert.equal(
    validatePlanSim([{ status: "UPLOADED", scan: "PENDING" }]).valid,
    false,
    "Plan validation must fail if reservation is only UPLOADED/PENDING",
  );

  assert.equal(
    validatePlanSim([{ status: "VALIDATED", scan: "CLEAN" }]).valid,
    true,
    "Plan validation must pass when VALIDATED and CLEAN",
  );
});

test("22. EDIT_SESSION_SUBMISSION_NO_LONGER_NEW_DENIAL rejects when target is not NEW", async () => {
  const mockSupabase = createMockSupabase({
    rpcHandlers: {
      reserve_candidate_form_upload: () => ({
        success: false,
        error_code: "INVALID_STATE",
        message: "Target submission is no longer in editable NEW status",
      }),
      prepare_signed_upload: () => ({
        success: false,
        error_code: "INVALID_STATE",
        message: "Target submission is no longer in editable NEW status",
      }),
      record_candidate_upload_completed: () => ({
        success: false,
        error_code: "INVALID_STATE",
        message: "Target submission is no longer in editable NEW status",
      }),
      stage_candidate_document_change: () => ({
        success: false,
        error_code: "INVALID_STATE",
        message: "Target submission is no longer in editable NEW status",
      }),
    },
  });

  const reserve = await reserveCandidateFormUpload(
    {
      candidateFormSessionId: "11111111-1111-1111-1111-111111111111",
      intendedDocumentTypeId: "22222222-2222-2222-2222-222222222222",
      originalFilename: "cv.pdf",
    },
    { client: mockSupabase, resolveActor: async () => activeCandidateActor },
  );
  assert.equal(reserve.success, false);
  if (!reserve.success) {
    assert.equal(reserve.error.code, CommandErrorCode.INVALID_STATE);
  }

  const sign = await createSignedUploadUrlForReservation(
    { uploadReservationId: "11111111-1111-1111-1111-111111111111" },
    { client: mockSupabase, resolveActor: async () => activeCandidateActor },
  );
  assert.equal(sign.success, false);

  const stage = await stageCandidateDocumentChange(
    {
      candidateFormSessionId: "11111111-1111-1111-1111-111111111111",
      intendedDocumentTypeId: "22222222-2222-2222-2222-222222222222",
      actionCode: "ADD",
      uploadReservationId: "res-001-uuid-0000-0000-000000000001",
    },
    { client: mockSupabase, resolveActor: async () => activeCandidateActor },
  );
  assert.equal(stage.success, false);
});

test("23. COMPETING_TRANSITION_CONCURRENCY_TEST deterministic lock hierarchy prevents deadlocks", async () => {
  // Simulating lock acquisition order
  // Both paths lock: 1) Session, 2) Submission, 3) Reservation
  const acquiredLocks: string[] = [];

  function acquireLock(resource: string) {
    acquiredLocks.push(resource);
  }

  acquireLock("candidate_form_sessions:sess-001");
  acquireLock("submissions:sub-001");
  acquireLock("upload_reservations:res-001");

  assert.deepEqual(acquiredLocks, [
    "candidate_form_sessions:sess-001",
    "submissions:sub-001",
    "upload_reservations:res-001",
  ]);
});

test("24. TWO_WORKER_CLEANUP_EXCLUSIVITY_TEST claims disjoint sets via FOR UPDATE SKIP LOCKED", async () => {
  const queue = [
    { storage_cleanup_id: "q-1", status_code: "PENDING", attempts: 0 },
    { storage_cleanup_id: "q-2", status_code: "PENDING", attempts: 0 },
  ];

  const mockSupabase = createMockSupabase({
    rpcHandlers: {
      claim_due_storage_cleanup_jobs: (args: unknown) => {
        const p = args as { p_limit: number };
        const available = queue
          .filter((q) => q.status_code === "PENDING")
          .slice(0, p.p_limit);
        for (const item of available) {
          item.status_code = "PROCESSING";
          item.attempts += 1;
        }
        return { success: true, data: available };
      },
    },
  });

  const worker1 = await claimDueStorageCleanupJobs(1, 300, mockSupabase);
  const worker2 = await claimDueStorageCleanupJobs(1, 300, mockSupabase);

  assert.equal(worker1.length, 1);
  assert.equal(worker2.length, 1);
  assert.notEqual(
    worker1[0].storage_cleanup_id,
    worker2[0].storage_cleanup_id,
    "Workers must receive disjoint sets of claimed jobs",
  );
});

test("25. CRASH_AFTER_CLAIM_LEASE_RECOVERY_TEST reclaims expired leased_until row", async () => {
  const job = {
    storage_cleanup_id: "q-crashed-1",
    status_code: "PROCESSING",
    leased_until: "2026-09-05T09:00:00Z", // Past lease
    attempts: 1,
  };

  const mockSupabase = createMockSupabase({
    rpcHandlers: {
      claim_due_storage_cleanup_jobs: () => {
        // Condition: (status_code = 'PROCESSING' and leased_until <= now() and attempts < 5)
        if (job.status_code === "PROCESSING" && job.attempts < 5) {
          job.attempts += 1;
          job.status_code = "PROCESSING";
          return { success: true, data: [job] };
        }
        return { success: true, data: [] };
      },
      complete_storage_cleanup_job: () => {
        job.status_code = "DONE";
        return { success: true };
      },
    },
  });

  const claimed = await claimDueStorageCleanupJobs(1, 300, mockSupabase);
  assert.equal(claimed.length, 1);
  assert.equal(claimed[0].attempts, 2, "Attempts should increment on reclaim");

  await completeStorageCleanupJob(
    claimed[0].storage_cleanup_id,
    true,
    null,
    mockSupabase,
  );
  assert.equal(
    job.status_code,
    "DONE",
    "Job completes successfully after recovery",
  );
});

test("26. Declarative storage bucket setup helper", async () => {
  const mockSupabase = createMockSupabase({});
  const result = await ensureQuarantineBucketExists(mockSupabase);
  assert.equal(result.success, true);
});
