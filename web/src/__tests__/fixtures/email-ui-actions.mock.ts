const INTERVIEW_ID = "10000000-0000-0000-0000-000000000001";
const APPLICATION_ID = "20000000-0000-0000-0000-000000000001";
const SUBMISSION_ID = "30000000-0000-0000-0000-000000000001";

let previewVersion = 0;
let staleNext = false;
let lastEnqueueInput: unknown = null;
let deletedHistoryIds: string[] = [];

function fingerprint(version: number): string {
  return String.fromCharCode(96 + Math.max(1, Math.min(version, 26))).repeat(64);
}

export function resetEmailHarnessState() {
  previewVersion = 0;
  staleNext = false;
  lastEnqueueInput = null;
  deletedHistoryIds = [];
}

export function makeNextEnqueueStale() {
  staleNext = true;
}

export function getEmailHarnessSnapshot() {
  return {
    previewVersion,
    lastEnqueueInput,
    deletedHistoryIds: [...deletedHistoryIds],
  };
}

export async function getInterviewEmailCapabilitiesAction() {
  return { canSend: true, canViewHistory: true, canDeleteHistory: true };
}

export async function previewInterviewEmailAction(input: {
  emailType: "INTERVIEW_INVITATION" | "INTERVIEW_PARTICIPANT_INVITATION";
  interviewId: string;
  applicationId: string;
  submissionId: string;
}) {
  previewVersion += 1;
  return {
    success: true as const,
    data: {
      recipients: {
        to:
          input.emailType === "INTERVIEW_INVITATION"
            ? ["candidate@example.com"]
            : ["interviewer-a@example.com", "interviewer-b@example.com"],
        cc: [],
      },
      subject: `Interview invitation v${previewVersion}`,
      body_text: `Rendered body v${previewVersion}`,
      template_version: "test-1",
      environment_code: "TEST" as const,
      context_fingerprint: "f".repeat(64),
      preview_fingerprint: fingerprint(previewVersion),
      email_type: input.emailType,
      interview_id: input.interviewId,
      application_id: input.applicationId,
      submission_id: input.submissionId,
    },
  };
}

export async function enqueueInterviewEmailAction(input: {
  request: {
    email_type: "INTERVIEW_INVITATION" | "INTERVIEW_PARTICIPANT_INVITATION";
    interview_id: string;
    application_id: string;
    submission_id: string;
    preview_fingerprint: string;
  };
  idempotencyKey: string;
}) {
  lastEnqueueInput = input;
  if (staleNext) {
    staleNext = false;
    return {
      success: false as const,
      error: {
        code: "STALE_PREVIEW",
        message: "Thông tin phỏng vấn đã thay đổi, vui lòng xem lại bản xem trước.",
      },
    };
  }
  return {
    success: true as const,
    data: { email_outbox_id: "60000000-0000-0000-0000-000000000001" },
  };
}

export async function bulkEnqueueInterviewEmailsAction() {
  throw new Error("Bulk action is not exercised by the single-email behavioral harness");
}

export async function loadInterviewEmailHistoryAction(interviewId: string) {
  const base = {
    interview_id: interviewId,
    email_type: "INTERVIEW_INVITATION",
    environment_code: "TEST" as const,
    recipients: { to: ["candidate@example.com"], cc: [] },
    subject: "Interview invitation",
    template_version: "test-1",
    sent_at: "2026-09-16T10:00:00.000Z",
    created_at: "2026-09-16T09:59:00.000Z",
    error_code: null,
  };
  const rows = [
    { ...base, email_history_id: "40000000-0000-0000-0000-000000000001", status_code: "SENT" as const },
    { ...base, email_history_id: "40000000-0000-0000-0000-000000000002", status_code: "FAILED" as const, error_code: "PROVIDER_ERROR" },
    { ...base, email_history_id: "40000000-0000-0000-0000-000000000003", status_code: "CANCELLED" as const },
    { ...base, email_history_id: "40000000-0000-0000-0000-000000000004", status_code: "ABANDONED" as const },
  ].filter((row) => !deletedHistoryIds.includes(row.email_history_id));
  return { success: true as const, data: rows };
}

export async function deleteEmailHistoryEntryAction(input: {
  emailHistoryId: string;
  classification: "TEST_RECORD" | "WRONG_RECORD";
  reason: string | null;
}) {
  deletedHistoryIds.push(input.emailHistoryId);
  return { success: true as const, data: { email_history_id: input.emailHistoryId } };
}

export const EMAIL_HARNESS_CONTEXT = {
  interviewId: INTERVIEW_ID,
  applicationId: APPLICATION_ID,
  submissionId: SUBMISSION_ID,
};
