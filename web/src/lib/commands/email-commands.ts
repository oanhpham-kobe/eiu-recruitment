import "server-only";

import type { SupabaseClient } from "@supabase/supabase-js";
import { getServerSession } from "@/lib/auth/session";
import { createServerClient } from "@/lib/supabase/server";

const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

export type ManualInterviewEmailType =
  | "INTERVIEW_INVITATION"
  | "INTERVIEW_PARTICIPANT_INVITATION";
export type EmailHistoryStatus = "SENT" | "FAILED" | "CANCELLED" | "ABANDONED";
export type EmailHistoryDeleteClassification = "TEST_RECORD" | "WRONG_RECORD";

export interface EmailRecipients {
  to: string[];
  cc: string[];
}

export interface InterviewEmailPreview {
  recipients: EmailRecipients;
  subject: string;
  body_text: string;
  template_version: string;
  environment_code: "TEST" | "PRODUCTION";
  context_fingerprint: string;
  preview_fingerprint: string;
  email_type: ManualInterviewEmailType;
  interview_id: string;
  application_id: string;
  submission_id: string;
}

export interface InterviewEmailRequest {
  email_type: ManualInterviewEmailType;
  interview_id: string;
  application_id: string;
  submission_id: string;
  preview_fingerprint: string;
}

export interface BulkEmailSuccess {
  id: string;
  email_type: ManualInterviewEmailType;
  application_id: string;
  submission_id: string;
  email_outbox_id: string;
}

export interface BulkEmailFailure {
  id: string;
  error_code: string;
}

export interface EmailHistoryEntry {
  emailHistoryId: string;
  interviewId: string;
  emailType: string;
  environmentCode: "TEST" | "PRODUCTION";
  recipients: EmailRecipients;
  subject: string | null;
  templateVersion: string | null;
  sentAt: string | null;
  createdAt: string;
  status: EmailHistoryStatus;
  errorCode: string | null;
}

export type EmailCommandResult<T> =
  | { success: true; data: T }
  | { success: false; error: { code: string; message: string } };

function safeMessage(code: string): string {
  const messages: Record<string, string> = {
    UNAUTHENTICATED: "Vui lòng đăng nhập lại.",
    FORBIDDEN: "Bạn không có quyền thực hiện thao tác này.",
    VALIDATION_ERROR: "Dữ liệu email chưa hợp lệ.",
    UNSUPPORTED_EMAIL_TYPE: "Loại email không được hỗ trợ.",
    PREVIEW_REQUIRED: "Vui lòng xem trước email trước khi gửi.",
    STALE_PREVIEW: "Thông tin phỏng vấn đã thay đổi, vui lòng xem lại bản xem trước.",
    BATCH_LIMIT_EXCEEDED: "Mỗi lần chỉ xử lý từ 1 đến 100 email.",
    IDEMPOTENCY_CONFLICT: "Yêu cầu gửi đã thay đổi. Vui lòng thực hiện lại.",
    EMAIL_RECIPIENTS_UNAVAILABLE: "Không có địa chỉ email hợp lệ để gửi.",
    CURRENT_PARTICIPANT_INACTIVE_REASSIGN_REQUIRED:
      "Có người tham dự hiện tại đã ngừng hoạt động. Vui lòng thay thế trước.",
  };
  return messages[code] ?? "Không thể hoàn tất thao tác email.";
}

function invalid(message: string): EmailCommandResult<never> {
  return { success: false, error: { code: "VALIDATION_ERROR", message } };
}

function isManualType(value: string): value is ManualInterviewEmailType {
  return value === "INTERVIEW_INVITATION" || value === "INTERVIEW_PARTICIPANT_INVITATION";
}

function hasPermission(
  session: Awaited<ReturnType<typeof getServerSession>>,
  permission: string,
): boolean {
  return Boolean(
    session.user?.roles.includes("ROOT_ADMIN") ||
      session.user?.permissions.includes(permission),
  );
}

async function authorizedClient(
  permission: string,
  client?: SupabaseClient,
): Promise<EmailCommandResult<SupabaseClient>> {
  const resolvedClient = client ?? (await createServerClient());
  const session = await getServerSession(resolvedClient);
  if (!session.user?.isInternal) {
    return {
      success: false,
      error: { code: "UNAUTHENTICATED", message: safeMessage("UNAUTHENTICATED") },
    };
  }
  if (!hasPermission(session, permission)) {
    return {
      success: false,
      error: { code: "FORBIDDEN", message: safeMessage("FORBIDDEN") },
    };
  }
  return { success: true, data: resolvedClient };
}

function rpcError<T>(data: unknown, error: { message: string } | null): EmailCommandResult<T> | null {
  if (error) {
    console.error("[email-command] RPC error", error.message);
    return {
      success: false,
      error: { code: "INTERNAL_ERROR", message: "Không thể hoàn tất thao tác email." },
    };
  }
  if (data && typeof data === "object" && "success" in data && data.success === false) {
    const code =
      "error_code" in data && typeof data.error_code === "string"
        ? data.error_code
        : "INTERNAL_ERROR";
    return { success: false, error: { code, message: safeMessage(code) } };
  }
  return null;
}

function recipients(value: unknown): EmailRecipients {
  if (!value || typeof value !== "object") return { to: [], cc: [] };
  const input = value as { to?: unknown; cc?: unknown };
  return {
    to: Array.isArray(input.to) ? input.to.filter((item): item is string => typeof item === "string") : [],
    cc: Array.isArray(input.cc) ? input.cc.filter((item): item is string => typeof item === "string") : [],
  };
}

export async function previewInterviewEmail(
  input: {
    emailType: ManualInterviewEmailType;
    interviewId: string;
    applicationId: string;
    submissionId: string;
  },
  client?: SupabaseClient,
): Promise<EmailCommandResult<InterviewEmailPreview>> {
  if (
    !isManualType(input.emailType) ||
    !UUID.test(input.interviewId) ||
    !UUID.test(input.applicationId) ||
    !UUID.test(input.submissionId)
  ) {
    return invalid("Loại email hoặc ngữ cảnh Interview không hợp lệ.");
  }
  const access = await authorizedClient("interviews.email", client);
  if (!access.success) return access;
  const { data, error } = await access.data.rpc("preview_email", {
    p_email_type: input.emailType,
    p_interview_id: input.interviewId,
    p_application_id: input.applicationId,
    p_submission_id: input.submissionId,
  });
  const failure = rpcError<InterviewEmailPreview>(data, error);
  if (failure) return failure;
  const envelope = data as { success?: boolean; data?: InterviewEmailPreview } | null;
  if (!envelope?.success || !envelope.data) {
    return { success: false, error: { code: "INTERNAL_ERROR", message: safeMessage("INTERNAL_ERROR") } };
  }
  return { success: true, data: { ...envelope.data, recipients: recipients(envelope.data.recipients) } };
}

export async function enqueueInterviewEmail(
  input: {
    emailType: ManualInterviewEmailType;
    interviewId: string;
    applicationId: string;
    submissionId: string;
    previewFingerprint: string;
  },
  idempotencyKey: string,
  client?: SupabaseClient,
): Promise<EmailCommandResult<{ email_outbox_id: string }>> {
  if (
    !isManualType(input.emailType) ||
    !UUID.test(input.interviewId) ||
    !UUID.test(input.applicationId) ||
    !UUID.test(input.submissionId) ||
    !input.previewFingerprint ||
    !UUID.test(idempotencyKey)
  ) {
    return invalid("Yêu cầu gửi email hoặc idempotency key không hợp lệ.");
  }
  const access = await authorizedClient("interviews.email", client);
  if (!access.success) return access;
  const request: InterviewEmailRequest = {
    email_type: input.emailType,
    interview_id: input.interviewId,
    application_id: input.applicationId,
    submission_id: input.submissionId,
    preview_fingerprint: input.previewFingerprint,
  };
  const { data, error } = await access.data.rpc("enqueue_email", {
    p_request: request,
    p_idempotency_key: idempotencyKey,
  });
  const failure = rpcError<{ email_outbox_id: string }>(data, error);
  if (failure) return failure;
  const envelope = data as { success?: boolean; data?: { email_outbox_id?: unknown } } | null;
  if (!envelope?.success || typeof envelope.data?.email_outbox_id !== "string") {
    return { success: false, error: { code: "INTERNAL_ERROR", message: safeMessage("INTERNAL_ERROR") } };
  }
  return { success: true, data: { email_outbox_id: envelope.data.email_outbox_id } };
}

export async function bulkEnqueueInterviewEmails(
  requests: InterviewEmailRequest[],
  idempotencyKey: string,
  client?: SupabaseClient,
): Promise<EmailCommandResult<{ success: BulkEmailSuccess[]; failed: BulkEmailFailure[] }>> {
  if (
    requests.length < 1 ||
    requests.length > 100 ||
    !UUID.test(idempotencyKey) ||
    requests.some(
      (item) =>
        !isManualType(item.email_type) ||
        !UUID.test(item.interview_id) ||
        !UUID.test(item.application_id) ||
        !UUID.test(item.submission_id) ||
        !item.preview_fingerprint,
    )
  ) {
    return invalid("Batch email phải có 1..100 yêu cầu preview-fenced hợp lệ.");
  }
  const access = await authorizedClient("interviews.email", client);
  if (!access.success) return access;
  const { data, error } = await access.data.rpc("bulk_enqueue_email", {
    p_requests: requests,
    p_idempotency_key: idempotencyKey,
  });
  const failure = rpcError<{ success: BulkEmailSuccess[]; failed: BulkEmailFailure[] }>(data, error);
  if (failure) return failure;
  const result = data as { success?: unknown; failed?: unknown } | null;
  if (!result || !Array.isArray(result.success) || !Array.isArray(result.failed)) {
    return { success: false, error: { code: "INTERNAL_ERROR", message: safeMessage("INTERNAL_ERROR") } };
  }
  return {
    success: true,
    data: {
      success: result.success as BulkEmailSuccess[],
      failed: result.failed as BulkEmailFailure[],
    },
  };
}

export async function loadInterviewEmailHistory(
  interviewId: string,
  client?: SupabaseClient,
): Promise<EmailCommandResult<EmailHistoryEntry[]>> {
  if (!UUID.test(interviewId)) return invalid("Interview không hợp lệ.");
  const access = await authorizedClient("emails.history_view", client);
  if (!access.success) return access;
  const { data, error } = await access.data
    .from("email_history")
    .select(
      "email_history_id,interview_id,email_type,environment_code,recipients,subject,template_version,sent_at,created_at,status_code,error_code",
    )
    .eq("interview_id", interviewId)
    .in("status_code", ["SENT", "FAILED", "CANCELLED", "ABANDONED"])
    .order("created_at", { ascending: false });
  if (error) {
    console.error("[email-command] email_history read error", error.message);
    return {
      success: false,
      error: { code: "INTERNAL_ERROR", message: "Không thể tải lịch sử gửi thư." },
    };
  }
  const rows = (data ?? []) as Array<Record<string, unknown>>;
  return {
    success: true,
    data: rows.flatMap((row) => {
      const status = row.status_code;
      if (
        status !== "SENT" &&
        status !== "FAILED" &&
        status !== "CANCELLED" &&
        status !== "ABANDONED"
      ) {
        return [];
      }
      if (
        typeof row.email_history_id !== "string" ||
        typeof row.interview_id !== "string" ||
        typeof row.email_type !== "string" ||
        (row.environment_code !== "TEST" && row.environment_code !== "PRODUCTION") ||
        typeof row.created_at !== "string"
      ) {
        return [];
      }
      return [
        {
          emailHistoryId: row.email_history_id,
          interviewId: row.interview_id,
          emailType: row.email_type,
          environmentCode: row.environment_code,
          recipients: recipients(row.recipients),
          subject: typeof row.subject === "string" ? row.subject : null,
          templateVersion:
            typeof row.template_version === "string" ? row.template_version : null,
          sentAt: typeof row.sent_at === "string" ? row.sent_at : null,
          createdAt: row.created_at,
          status,
          errorCode: typeof row.error_code === "string" ? row.error_code : null,
        },
      ];
    }),
  };
}

export async function deleteEmailHistoryEntry(
  emailHistoryId: string,
  classification: EmailHistoryDeleteClassification,
  reason: string | null,
  client?: SupabaseClient,
): Promise<EmailCommandResult<{ email_history_id: string }>> {
  const trimmedReason = reason?.trim() ?? "";
  if (!UUID.test(emailHistoryId)) return invalid("Email History không hợp lệ.");
  if (classification !== "TEST_RECORD" && classification !== "WRONG_RECORD") {
    return invalid("Phân loại xóa không hợp lệ.");
  }
  if (classification === "WRONG_RECORD" && (!trimmedReason || trimmedReason.length > 1000)) {
    return invalid("WRONG_RECORD yêu cầu lý do từ 1 đến 1000 ký tự.");
  }
  if (trimmedReason.length > 1000) return invalid("Lý do xóa tối đa 1000 ký tự.");
  const access = await authorizedClient("emails.history_delete", client);
  if (!access.success) return access;
  if (!hasPermission(await getServerSession(access.data), "emails.history_view")) {
    return { success: false, error: { code: "FORBIDDEN", message: safeMessage("FORBIDDEN") } };
  }
  const { data, error } = await access.data.rpc("delete_email_history", {
    p_email_history_id: emailHistoryId,
    p_classification: classification,
    p_reason: classification === "WRONG_RECORD" ? trimmedReason : null,
  });
  const failure = rpcError<{ email_history_id: string }>(data, error);
  if (failure) return failure;
  const envelope = data as { success?: boolean; data?: { email_history_id?: unknown } } | null;
  if (!envelope?.success || typeof envelope.data?.email_history_id !== "string") {
    return { success: false, error: { code: "INTERNAL_ERROR", message: safeMessage("INTERNAL_ERROR") } };
  }
  return { success: true, data: { email_history_id: envelope.data.email_history_id } };
}
