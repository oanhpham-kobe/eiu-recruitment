import { useState } from "react";
import { createRoot } from "react-dom/client";
import { EmailHistoryDrawer } from "@/components/interview/EmailHistoryDrawer";
import { EmailPreviewDialog } from "@/components/interview/EmailPreviewDialog";
import type { ManualInterviewEmailType } from "@/lib/commands/email-commands";
import type {
  InterviewApplicationGroup,
  InterviewRound,
} from "@/lib/interview/model";
import "@/app/globals.css";
import "@/styles/interview.css";

declare global {
  interface Window {
    __EMAIL_HARNESS_DATA__?: {
      emailType?: ManualInterviewEmailType;
      canDelete?: boolean;
    };
  }
}

const round: InterviewRound = {
  interviewId: "10000000-0000-0000-0000-000000000001",
  applicationId: "20000000-0000-0000-0000-000000000001",
  roundNo: 1,
  demoTopic: "Demo topic",
  startAt: "2026-09-18T02:00:00.000Z",
  endAt: "2026-09-18T03:00:00.000Z",
  interviewFormatId: "70000000-0000-0000-0000-000000000001",
  roomId: null,
  meetingLink: "https://meet.example.invalid/interview",
  scheduleStatus: "CONFIRMED",
  reportStatus: "INTERVIEW_SCHEDULING",
  interviewNote: null,
  isActive: true,
  versionNo: 1,
  updatedAt: "2026-09-16T10:00:00.000Z",
  participants: [
    {
      interviewParticipantId: "80000000-0000-0000-0000-000000000001",
      appUserId: "90000000-0000-0000-0000-000000000001",
      order: 1,
      name: "Interviewer One",
      email: "interviewer.one@eiu.edu.vn",
      jobTitle: "Lecturer",
      isCurrent: true,
      removedAt: null,
      versionNo: 1,
      hasReportHistory: false,
    },
  ],
};

const application: InterviewApplicationGroup = {
  applicationId: round.applicationId,
  submissionId: "30000000-0000-0000-0000-000000000001",
  candidateId: "40000000-0000-0000-0000-000000000001",
  candidateName: "Nguyễn Thị An",
  candidateEmail: "candidate@example.com",
  candidatePhone: "0901234567",
  submissionDate: "2026-09-01T02:00:00.000Z",
  submissionStatus: "READ",
  unitId: "50000000-0000-0000-0000-000000000001",
  unitName: "Engineering",
  departmentTeamId: null,
  departmentTeamName: null,
  positionId: "60000000-0000-0000-0000-000000000001",
  positionName: "Lecturer",
  hrOwnerId: "a0000000-0000-0000-0000-000000000001",
  hrOwnerName: "HR Owner",
  isActive: true,
  versionNo: 1,
  rounds: [round],
};

function InterviewEmailHarness() {
  const [previewOpen, setPreviewOpen] = useState(false);
  const [historyOpen, setHistoryOpen] = useState(false);
  return (
    <main>
      <button type="button" onClick={() => setPreviewOpen(true)}>
        Open Email Preview
      </button>
      <button type="button" onClick={() => setHistoryOpen(true)}>
        Open Email History
      </button>
      <EmailPreviewDialog
        open={previewOpen}
        application={application}
        round={round}
        emailType={
          window.__EMAIL_HARNESS_DATA__?.emailType ?? "INTERVIEW_INVITATION"
        }
        onClose={() => setPreviewOpen(false)}
      />
      <EmailHistoryDrawer
        open={historyOpen}
        interviewId={round.interviewId}
        canDelete={window.__EMAIL_HARNESS_DATA__?.canDelete ?? true}
        onClose={() => setHistoryOpen(false)}
      />
    </main>
  );
}

const root = document.getElementById("root");
if (!root) throw new Error("Missing harness root");
createRoot(root).render(<InterviewEmailHarness />);
