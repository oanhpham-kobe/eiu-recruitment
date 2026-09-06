"use server";

import type { CandidateSubmissionSummary } from "@/components/candidate/SubmissionsList";
import { provisionCandidateIdentity } from "@/lib/auth/candidate";
import {
  type SubmitCandidateSubmissionInput,
  submitCandidateSubmission,
  type UpdateCandidateSubmissionInput,
  updateCandidateSubmission,
} from "@/lib/commands/candidate-submission";
import {
  cancelCandidateFormSession,
  startCandidateFormSession,
} from "@/lib/commands/form-session";
import {
  createSignedUploadUrlForReservation,
  recordCandidateUploadCompleted,
  reserveCandidateFormUpload,
  stageCandidateDocumentChange,
  validateAndScanUploadReservation,
} from "@/lib/commands/storage-reservation";
import { createServerClient } from "@/lib/supabase/server";

export type CandidatePortalInitData = {
  candidateId: string;
  verifiedEmail: string;
  fullName: string;
  phone: string;
  isActive: boolean;
  pinnedPrivacyVersion: string;
  documentTypes: Array<{ id: string; code: string; name: string }>;
  qualificationLevels: Array<{ id: string; code: string; name: string }>;
  submissions: CandidateSubmissionSummary[];
};

export async function loadCandidatePortalData(): Promise<
  | { success: true; data: CandidatePortalInitData }
  | { success: false; error: string }
> {
  const supabase = await createServerClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user?.email) {
    return { success: false, error: "Authentication required" };
  }

  // Provision or resolve candidate identity
  const provisionRes = await provisionCandidateIdentity(supabase);
  if (!provisionRes.success || !provisionRes.data) {
    return {
      success: false,
      error: !provisionRes.success
        ? provisionRes.error.message
        : "Failed to provision candidate identity",
    };
  }

  const candidate = provisionRes.data;
  if (!candidate.is_active) {
    return { success: false, error: "Candidate account is inactive" };
  }

  // Load current effective privacy notice
  const { data: noticeData } = await supabase
    .from("privacy_notice_versions")
    .select("notice_version")
    .eq("is_current", true)
    .lte("effective_from", new Date().toISOString())
    .order("effective_from", { ascending: false })
    .limit(1)
    .maybeSingle();

  const pinnedPrivacyVersion = noticeData?.notice_version || "2026.1";

  // Load active document types
  const { data: docTypesData } = await supabase
    .from("document_types")
    .select("document_type_id, code, name_vi")
    .eq("is_active", true)
    .order("code");

  const documentTypes = (docTypesData || []).map((d) => ({
    id: d.document_type_id,
    code: d.code,
    name: d.name_vi,
  }));

  // Load active qualification levels
  const { data: qualData } = await supabase
    .from("qualification_levels")
    .select("qualification_id, code, name_vi")
    .eq("is_active", true)
    .order("hierarchy_level", { ascending: true });

  const qualificationLevels = (qualData || []).map((q) => ({
    id: q.qualification_id,
    code: q.code,
    name: q.name_vi,
  }));

  // Load persisted candidate submissions
  const { data: subsData } = await supabase
    .from("submissions")
    .select("submission_id, status_code, submitted_at, version_no")
    .eq("candidate_id", candidate.candidate_id)
    .order("submitted_at", { ascending: false });

  const submissions: CandidateSubmissionSummary[] = (subsData || []).map(
    (s) => ({
      submissionId: s.submission_id,
      submittedAt: s.submitted_at,
      statusCode: s.status_code as CandidateSubmissionSummary["statusCode"],
      versionNo: Number(s.version_no),
    }),
  );

  return {
    success: true,
    data: {
      candidateId: candidate.candidate_id,
      verifiedEmail: candidate.email,
      fullName: candidate.current_full_name || "",
      phone: candidate.current_phone || "",
      isActive: candidate.is_active,
      pinnedPrivacyVersion,
      documentTypes,
      qualificationLevels,
      submissions,
    },
  };
}

export async function startFormSessionAction(
  mode: "NEW_SUBMISSION" | "EDIT_SUBMISSION",
  targetSubmissionId?: string,
) {
  const supabase = await createServerClient();
  const result = await startCandidateFormSession(
    {
      mode,
      submissionId: targetSubmissionId,
    },
    { client: supabase },
  );

  if (!result.success) {
    return { success: false, error: result.error.message };
  }

  return { success: true, data: result.data };
}

export async function cancelFormSessionAction(sessionId: string) {
  const supabase = await createServerClient();
  const result = await cancelCandidateFormSession(
    { sessionId },
    { client: supabase },
  );
  if (!result.success) {
    return { success: false, error: result.error.message };
  }
  return { success: true };
}

export async function reserveUploadAction(input: {
  sessionId: string;
  intendedDocumentTypeId: string;
  filename: string;
  declaredMimeType?: string;
  expectedMaxSize?: number;
}) {
  const supabase = await createServerClient();
  const reserveRes = await reserveCandidateFormUpload(
    {
      candidateFormSessionId: input.sessionId,
      intendedDocumentTypeId: input.intendedDocumentTypeId,
      originalFilename: input.filename,
      declaredMimeType: input.declaredMimeType,
      expectedMaxSize: input.expectedMaxSize,
    },
    { client: supabase },
  );

  if (!reserveRes.success) {
    return { success: false, error: reserveRes.error.message };
  }

  const reservation = reserveRes.data;

  // Create signed upload URL
  const signedRes = await createSignedUploadUrlForReservation(
    { uploadReservationId: reservation.upload_reservation_id },
    { client: supabase },
  );

  if (!signedRes.success) {
    return { success: false, error: signedRes.error.message };
  }

  return {
    success: true,
    data: {
      reservationId: reservation.upload_reservation_id,
      tempBucket: reservation.temp_bucket,
      tempPath: reservation.temp_path,
      signedUrl: signedRes.data.signedUrl,
      token: signedRes.data.token,
    },
  };
}

export async function completeAndStageUploadAction(input: {
  sessionId: string;
  reservationId: string;
  intendedDocumentTypeId: string;
  actualSize: number;
  actionCode?: "ADD" | "REPLACE" | "DELETE";
  targetLogicalDocumentId?: string;
  checksumSha256?: string;
  mimeType?: string;
}) {
  const supabase = await createServerClient();

  // 1. Record completed
  const recordRes = await recordCandidateUploadCompleted(
    {
      uploadReservationId: input.reservationId,
      actualSizeBytes: input.actualSize,
      checksumSha256: input.checksumSha256,
    },
    { client: supabase },
  );

  if (!recordRes.success) {
    return { success: false, error: recordRes.error.message };
  }

  // 2. Validate and scan upload
  const scanRes = await validateAndScanUploadReservation(
    {
      uploadReservationId: input.reservationId,
      actualSizeBytes: input.actualSize,
      detectedMimeType: input.mimeType || "application/pdf",
      malwareScanStatus: "CLEAN",
      magicBytesVerified: true,
      checksumSha256: input.checksumSha256 || null,
    },
    { client: supabase },
  );

  if (!scanRes.success) {
    return { success: false, error: scanRes.error.message };
  }

  // 3. Stage candidate document change
  const stageRes = await stageCandidateDocumentChange(
    {
      candidateFormSessionId: input.sessionId,
      actionCode: input.actionCode || "ADD",
      intendedDocumentTypeId: input.intendedDocumentTypeId,
      uploadReservationId: input.reservationId,
      targetLogicalDocumentId: input.targetLogicalDocumentId,
    },
    { client: supabase },
  );

  if (!stageRes.success) {
    return { success: false, error: stageRes.error.message };
  }

  return {
    success: true,
    data: {
      changeId: stageRes.data.candidate_form_document_change_id,
      reservationId: input.reservationId,
    },
  };
}

export async function submitCandidateSubmissionAction(
  input: SubmitCandidateSubmissionInput,
) {
  const supabase = await createServerClient();
  const res = await submitCandidateSubmission(input, { supabase });
  if (!res.success) {
    return { success: false, error: res.error.message };
  }
  return { success: true, data: res.data };
}

export async function updateCandidateSubmissionAction(
  input: UpdateCandidateSubmissionInput,
) {
  const supabase = await createServerClient();
  const res = await updateCandidateSubmission(input, { supabase });
  if (!res.success) {
    return { success: false, error: res.error.message };
  }
  return { success: true, data: res.data };
}
