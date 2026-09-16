"use client";

import { useCallback, useEffect, useState } from "react";
import {
  enqueueInterviewEmailAction,
  previewInterviewEmailAction,
} from "@/app/interviews/actions";
import { Button } from "@/components/ui/Button";
import { Dialog } from "@/components/ui/Dialog";
import type {
  InterviewEmailPreview,
  ManualInterviewEmailType,
} from "@/lib/commands/email-commands";
import {
  formatInterviewTime,
  type InterviewApplicationGroup,
  type InterviewRound,
} from "@/lib/interview/model";

export function EmailPreviewDialog({
  open,
  application,
  round,
  emailType,
  onClose,
  onQueued,
}: {
  open: boolean;
  application: InterviewApplicationGroup;
  round: InterviewRound;
  emailType: ManualInterviewEmailType;
  onClose: () => void;
  onQueued?: () => void;
}) {
  const [preview, setPreview] = useState<InterviewEmailPreview | null>(null);
  const [pending, setPending] = useState(false);
  const [feedback, setFeedback] = useState<
    { tone: "error" | "success" | "info"; message: string } | null
  >(null);

  const loadPreview = useCallback(async () => {
    setPending(true);
    setFeedback(null);
    const result = await previewInterviewEmailAction({
      emailType,
      interviewId: round.interviewId,
      applicationId: application.applicationId,
      submissionId: application.submissionId,
    });
    if (result.success) {
      setPreview(result.data);
    } else {
      setPreview(null);
      setFeedback({ tone: "error", message: result.error.message });
    }
    setPending(false);
  }, [application.applicationId, application.submissionId, emailType, round.interviewId]);

  useEffect(() => {
    if (!open) return;
    void loadPreview();
  }, [loadPreview, open]);

  const confirmSend = async () => {
    if (!preview) return;
    setPending(true);
    setFeedback(null);
    const result = await enqueueInterviewEmailAction({
      emailType,
      interviewId: round.interviewId,
      applicationId: application.applicationId,
      submissionId: application.submissionId,
      previewFingerprint: preview.preview_fingerprint,
      idempotencyKey: crypto.randomUUID(),
    });
    if (result.success) {
      setFeedback({
        tone: "success",
        message: "Đã đưa vào hàng đợi gửi thư.",
      });
      onQueued?.();
      setPending(false);
      return;
    }
    if (result.error.code === "STALE_PREVIEW") {
      setFeedback({
        tone: "info",
        message: "Thông tin phỏng vấn đã thay đổi, vui lòng xem lại bản xem trước.",
      });
      await loadPreview();
      return;
    }
    setFeedback({ tone: "error", message: result.error.message });
    setPending(false);
  };

  const recipientLabel =
    emailType === "INTERVIEW_INVITATION"
      ? "Gửi thư ứng viên"
      : "Gửi thư người tham dự";

  return (
    <Dialog
      open={open}
      title={`Bản xem trước email — ${recipientLabel}`}
      onClose={onClose}
      footer={
        <div className="interview-confirm-actions">
          <Button disabled={pending} onClick={onClose}>
            Đóng
          </Button>
          <Button
            variant="primary"
            pending={pending}
            disabled={!preview || feedback?.tone === "success"}
            onClick={() => void confirmSend()}
          >
            Xác nhận gửi
          </Button>
        </div>
      }
    >
      <dl className="interview-detail-grid">
        <dt>Ứng viên</dt>
        <dd>{application.candidateName}</dd>
        <dt>Vòng</dt>
        <dd>Vòng {round.roundNo}</dd>
        <dt>Thời gian</dt>
        <dd>{formatInterviewTime(round.startAt, round.endAt)}</dd>
        <dt>Meeting</dt>
        <dd>{round.meetingLink ?? "—"}</dd>
      </dl>
      {pending && !preview ? <p role="status">Đang tải bản xem trước…</p> : null}
      {feedback ? (
        <div
          className={`ui-alert ui-alert--${feedback.tone === "error" ? "error" : "info"}`}
          role={feedback.tone === "error" ? "alert" : "status"}
          aria-live="polite"
        >
          {feedback.message}
        </div>
      ) : null}
      {preview ? (
        <section aria-label="Nội dung email xem trước">
          <dl className="interview-detail-grid">
            <dt>To</dt>
            <dd>{preview.recipients.to.join(", ") || "—"}</dd>
            <dt>CC</dt>
            <dd>{preview.recipients.cc.join(", ") || "—"}</dd>
            <dt>Subject</dt>
            <dd>{preview.subject}</dd>
            <dt>Template</dt>
            <dd>{preview.template_version}</dd>
            <dt>Môi trường</dt>
            <dd>{preview.environment_code}</dd>
          </dl>
          <h3>Nội dung</h3>
          <pre className="interview-email-preview-body">{preview.body_text}</pre>
        </section>
      ) : null}
    </Dialog>
  );
}
