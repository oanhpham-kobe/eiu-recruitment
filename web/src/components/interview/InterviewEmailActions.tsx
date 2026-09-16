"use client";

import { useState } from "react";
import { Button } from "@/components/ui/Button";
import type { ManualInterviewEmailType } from "@/lib/commands/email-commands";
import type {
  InterviewApplicationGroup,
  InterviewPermissions,
  InterviewRound,
} from "@/lib/interview/model";
import { EmailHistoryDrawer } from "./EmailHistoryDrawer";
import { EmailPreviewDialog } from "./EmailPreviewDialog";

export function InterviewEmailActions({
  application,
  round,
  permissions,
  compact = false,
}: {
  application: InterviewApplicationGroup;
  round: InterviewRound;
  permissions: InterviewPermissions;
  compact?: boolean;
}) {
  const [emailType, setEmailType] = useState<ManualInterviewEmailType | null>(null);
  const [historyOpen, setHistoryOpen] = useState(false);
  const operational = application.isActive && round.isActive;
  const hasParticipants = round.participants.some((participant) => participant.isCurrent);

  if (!permissions.canEmail && !permissions.canViewEmailHistory) return null;

  const controls = (
    <>
      {permissions.canEmail && operational ? (
        <Button
          variant="ghost"
          onClick={() => setEmailType("INTERVIEW_INVITATION")}
        >
          {compact ? "Gửi ứng viên" : "Gửi thư ứng viên"}
        </Button>
      ) : null}
      {permissions.canEmail && operational && hasParticipants ? (
        <Button
          variant="ghost"
          onClick={() => setEmailType("INTERVIEW_PARTICIPANT_INVITATION")}
        >
          {compact ? "Gửi tham dự" : "Gửi thư người tham dự"}
        </Button>
      ) : null}
      {permissions.canViewEmailHistory ? (
        <Button variant="ghost" onClick={() => setHistoryOpen(true)}>
          {compact ? "Lịch sử thư" : "Lịch sử gửi thư / Email History"}
        </Button>
      ) : null}
    </>
  );

  return (
    <>
      {compact ? controls : <div className="interview-drawer-actions">{controls}</div>}

      {emailType ? (
        <EmailPreviewDialog
          open
          application={application}
          round={round}
          emailType={emailType}
          onClose={() => setEmailType(null)}
        />
      ) : null}

      <EmailHistoryDrawer
        open={historyOpen}
        interviewId={round.interviewId}
        canDelete={permissions.canDeleteEmailHistory}
        onClose={() => setHistoryOpen(false)}
      />
    </>
  );
}
