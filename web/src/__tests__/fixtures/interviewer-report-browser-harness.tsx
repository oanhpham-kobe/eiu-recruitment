import { createRoot } from "react-dom/client";
import { AppShell } from "@/components/shell/AppShell";
import {
  LocaleProvider,
  useAppLocale,
} from "@/components/shell/LocaleProvider";
import { InterviewerReportView } from "@/components/reports/InterviewerReportView";
import {
  EMPTY_REPORT_FIELDS,
  type InterviewerReportPageData,
} from "@/lib/reports/model";
import type {
  SaveInterviewerReportInput,
  SaveInterviewerReportResult,
} from "@/lib/reports/server";
import "@/app/globals.css";
import "@/styles/reports.css";

const CURRENT_INTERVIEW = "22222222-2222-4222-8222-222222222222";
const CURRENT_PARTICIPANT = "33333333-3333-4333-8333-333333333333";

function initialData(): InterviewerReportPageData {
  return {
    rounds: [
      {
        applicationId: "11111111-1111-4111-8111-111111111111",
        interviewId: CURRENT_INTERVIEW,
        roundNo: 2,
        isCurrentRound: true,
        candidateName: "Nguyễn Minh Anh",
        positionNameVi: "Giảng viên Kỹ thuật",
        positionNameEn: "Engineering Lecturer",
        startAt: "2026-09-08T02:00:00Z",
        endAt: "2026-09-08T03:00:00Z",
        formatNameVi: "Trực tuyến",
        formatNameEn: "Online",
        roomName: null,
        meetingLink: "https://meet.example.test/current",
        displayReportStatus: "WAITING_FOR_REPORT",
        canEdit: true,
        interviewParticipantId: CURRENT_PARTICIPANT,
        hasOwnReport: false,
        ownVersionNo: 1,
        ownReport: { ...EMPTY_REPORT_FIELDS },
        preview: {
          participants: [
            {
              participantOrder: 1,
              name: "Interviewer One",
              jobTitle: "Lecturer",
              report: { ...EMPTY_REPORT_FIELDS },
            },
            {
              participantOrder: 2,
              name: "Interviewer Two",
              jobTitle: "Professor",
              report: {
                ...EMPTY_REPORT_FIELDS,
                conclusion: "Trao đổi thêm",
              },
            },
          ],
          finalDecision: {
            conclusion: "Trao đổi thêm",
            expectedSpecificJobAssigned: null,
            expectedRecruitmentTime: null,
          },
        },
        updatedAt: "2026-09-08T03:00:00Z",
      },
      {
        applicationId: "11111111-1111-4111-8111-111111111111",
        interviewId: "44444444-4444-4444-8444-444444444444",
        roundNo: 1,
        isCurrentRound: false,
        candidateName: "Nguyễn Minh Anh",
        positionNameVi: "Giảng viên Kỹ thuật",
        positionNameEn: "Engineering Lecturer",
        startAt: "2026-08-20T02:00:00Z",
        endAt: "2026-08-20T03:00:00Z",
        formatNameVi: "Trực tiếp",
        formatNameEn: "In person",
        roomName: "B1.101",
        meetingLink: null,
        displayReportStatus: "REPORT_SUBMITTED",
        canEdit: false,
        interviewParticipantId: "55555555-5555-4555-8555-555555555555",
        hasOwnReport: true,
        ownVersionNo: 3,
        ownReport: {
          ...EMPTY_REPORT_FIELDS,
          professional_knowledge: "Historical knowledge",
          conclusion: "Historical conclusion",
        },
        preview: null,
        updatedAt: "2026-08-20T03:00:00Z",
      },
    ],
  };
}

let data = initialData();

async function save(
  input: SaveInterviewerReportInput,
): Promise<SaveInterviewerReportResult> {
  const current = data.rounds.find(
    (round) => round.interviewParticipantId === input.interviewParticipantId,
  );
  if (!current || !current.canEdit) {
    return {
      success: false,
      error: { code: "FORBIDDEN", message: "Read only" },
    };
  }
  const nextReport = { ...current.ownReport, ...input.patches };
  data = {
    rounds: data.rounds.map((round) =>
      round.interviewId === current.interviewId
        ? {
            ...round,
            hasOwnReport: true,
            ownVersionNo: round.ownVersionNo + 1,
            ownReport: nextReport,
          }
        : round,
    ),
  };
  return {
    success: true,
    data: {
      interviewReportId: "66666666-6666-4666-8666-666666666666",
      versionNo: current.ownVersionNo + 1,
    },
  };
}

async function refresh() {
  return data;
}

function ReportSurface() {
  return (
    <InterviewerReportView
      initialData={data}
      onSave={save}
      onRefresh={refresh}
    />
  );
}

function ProductionHarness() {
  return (
    <div id="app-root" data-harness-ready="production">
      <AppShell currentPath="/reports">
        <ReportSurface />
      </AppShell>
    </div>
  );
}

function LocaleHarnessContent() {
  const { setLocale } = useAppLocale();
  return (
    <>
      {/* Test-only control outside #app-root. It lets the browser test change
          the same production LocaleProvider while Drawer correctly keeps the
          real background inert. */}
      <button
        type="button"
        data-testid="test-switch-en"
        onClick={() => setLocale("en")}
      >
        Test switch EN
      </button>
      <div id="app-root" data-harness-ready="locale">
        <ReportSurface />
      </div>
    </>
  );
}

function LocaleHarness() {
  return (
    <LocaleProvider>
      <LocaleHarnessContent />
    </LocaleProvider>
  );
}

const mode = document.body.dataset.harness;
data = initialData();
createRoot(document.getElementById("root")!).render(
  mode === "locale" ? <LocaleHarness /> : <ProductionHarness />,
);
