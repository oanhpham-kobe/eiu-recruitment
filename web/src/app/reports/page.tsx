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
    const accessDenied = error instanceof InterviewerReportAccessError;
    return (
      <section
        className="interviewer-report"
        aria-labelledby="interviewer-report-title"
      >
        <h1 id="interviewer-report-title">
          Báo cáo phỏng vấn / Interview Reports
        </h1>
        <div className="ui-alert ui-alert--error" role="alert">
          {accessDenied
            ? "Bạn không có quyền xem Báo cáo phỏng vấn. / You do not have access to Interview Reports."
            : "Không thể tải Báo cáo phỏng vấn. Vui lòng thử lại. / Interview Reports could not be loaded. Please try again."}
        </div>
      </section>
    );
  }
}
