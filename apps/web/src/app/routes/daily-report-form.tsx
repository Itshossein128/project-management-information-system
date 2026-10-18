import { Navigate, useParams } from "react-router";
import { PATHS } from "@/app/routeVars";

/** Blank project daily-report create is retired; summaries are auto-built from specialty reports. */
export default function DailyReportNewPage() {
  const { projectId = "" } = useParams();
  return (
    <Navigate
      to={`/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_DAILY_REPORTS}`}
      replace
    />
  );
}
