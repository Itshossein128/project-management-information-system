import { useParams } from "react-router";
import { DailyReportForm } from "@/components/daily_reports/DailyReportForm";

export default function DailyReportEditPage() {
  const { projectId = "", reportId = "" } = useParams();
  return (
    <main className="page-main page-shell mx-auto max-w-6xl px-4 py-6">
      <DailyReportForm key={reportId} projectId={projectId} reportId={reportId} />
    </main>
  );
}
