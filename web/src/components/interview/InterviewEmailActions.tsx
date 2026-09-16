"use client";

import { useEffect, useMemo, useState } from "react";
import { getInterviewEmailCapabilitiesAction } from "@/app/interviews/actions";
import { Button } from "@/components/ui/Button";
import type { InterviewEmailType } from "@/lib/commands/email-commands";
import {
  formatInterviewTime,
  type InterviewApplicationGroup,
  type InterviewRound,
} from "@/lib/interview/model";
import { EmailPreviewDialog } from "./EmailPreviewDialog";

export function InterviewEmailActions({
  application,
  round,
  pending,
}: {
  application: InterviewApplicationGroup;
  round: InterviewRound;
  pending: boolean;
}) {
  const [canSend, setCanSend] = useState<boolean | null>(null);
  const [emailType, setEmailType] = useState<InterviewEmailType | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    void getInterviewEmailCapabilitiesAction()
      .then((capabilities) => {
        if (active) setCanSend(capabilities.canSend);
      })
      .catch(() => {
        if (active) setCanSend(false);
      });
    return () => {
      active = false;
    };
  }, []);

  const hasCurrentParticipants = useMemo(
    () => round.participants.some((participant) => participant.isCurrent),
    [round.participants],
  );
  const operational = application.isActive && round.isActive;
  const disabled = pending || canSend !== true || !operational;
  const contextSummary = `Vòng ${round.roundNo} · ${formatInterviewTime(round.startAt, round.endAt)}`;

  if (canSend === false) return null;

  return (
    <section
      className="interview-drawer-section"
      aria-labelledby="interview-email-actions-heading"
    >
      <h3 id="interview-email-actions-heading">Gửi thư / Email</h3>
      <p className="interview-field-hint">
        Người nhận và nội dung được server xác định lại khi xem trước và khi đưa
        vào hàng đợi. Gửi thư không thay đổi trạng thái Interview.
      </p>
      <div className="interview-drawer-actions">
        <Button
          disabled={disabled || !application.candidateEmail}
          onClick={() => {
            setNotice(null);
            setEmailType("INTERVIEW_INVITATION");
          }}
        >
          Gửi thư ứng viên
        </Button>
        <Button
          disabled={disabled || !hasCurrentParticipants}
          onClick={() => {
            setNotice(null);
            setEmailType("INTERVIEW_PARTICIPANT_INVITATION");
          }}
        >
          Gửi thư người tham dự
        </Button>
      </div>
      {canSend === null ? (
        <p className="interview-field-hint" role="status">
          Đang kiểm tra quyền gửi thư…
        </p>
      ) : null}
      {notice ? (
        <p
          className="interview-field-hint"
          role="status"
          aria-live="polite"
        >
          {notice}
        </p>
      ) : null}
      {emailType ? (
        <EmailPreviewDialog
          open
          emailType={emailType}
          interviewId={round.interviewId}
          applicationId={application.applicationId}
          submissionId={application.submissionId}
          contextSummary={contextSummary}
          onClose={() => setEmailType(null)}
          onQueued={() => setNotice("Đã đưa vào hàng đợi gửi thư")}
        />
      ) : null}
    </section>
  );
}
