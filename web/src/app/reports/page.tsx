import { InterviewerReportErrorState } from "@/components/reports/InterviewerReportErrorState";
import { InterviewerReportPage } from "@/components/reports/InterviewerReportPage";
import {
  InterviewerReportAccessError,
  loadInterviewerReportPage,
} from "@/lib/reports/server";
import "@/styles/reports.css";

export const dynamic = "force-dynamic";

export default async function ReportsPage() {
  try {
    const data = await loadInterviewerReportPage();
    return <InterviewerReportPage initialData={data} />;
  } catch (error) {
    return (
      <InterviewerReportErrorState
        kind={error instanceof InterviewerReportAccessError ? "access" : "load"}
      />
    );
  }
}
