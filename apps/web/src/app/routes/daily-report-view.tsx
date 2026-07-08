import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useParams } from "react-router";
import { Download } from "lucide-react";
import { useToast } from "@/components/ui/toast";
import { usePermission } from "@/app/contexts/project-context";
import { PATHS } from "@/app/routeVars";
import { fetchActivities } from "@/app/lib/api/activities";
import {
  approveReport,
  fetchDailyReport,
  fetchReportPdf,
  rejectReport,
  reviewReport,
  submitReport,
} from "@/app/lib/api/daily-reports";
import { formatDisplayDate } from "@/app/lib/jalali-utils";
import { Breadcrumb, LoadingSkeleton, PageHeader } from "@/components/layout/page-header";
import { ActivityTab } from "@/components/daily_reports/ActivityTab";
import { ApprovalStatusBar } from "@/components/daily_reports/ApprovalStatusBar";
import { ConcreteTab } from "@/components/daily_reports/ConcreteTab";
import { EquipmentTab } from "@/components/daily_reports/EquipmentTab";
import { IncidentsTab } from "@/components/daily_reports/IncidentsTab";
import { LaborCampTab } from "@/components/daily_reports/LaborCampTab";
import { LaborTab } from "@/components/daily_reports/LaborTab";
import { MaterialsTab } from "@/components/daily_reports/MaterialsTab";

export default function DailyReportViewPage() {
  const { projectId = "", reportId = "" } = useParams();
  const toast = useToast();
  const queryClient = useQueryClient();
  const { has } = usePermission(projectId);
  const canApprove = has("approve_reports");
  const [downloading, setDownloading] = useState(false);

  const reportQuery = useQuery({
    queryKey: ["daily-report", projectId, reportId],
    queryFn: () => fetchDailyReport(projectId, reportId),
  });
  const report = reportQuery.data ?? null;

  const activitiesQuery = useQuery({
    queryKey: ["activities-lite", projectId],
    queryFn: () => fetchActivities(projectId, { per_page: 500 }),
  });
  const activityOptions = useMemo(
    () =>
      (activitiesQuery.data?.results ?? []).map((a) => ({
        value: a.activity_id,
        label: `${a.activity_code} - ${a.activity_name}`,
      })),
    [activitiesQuery.data],
  );

  const refetch = () =>
    queryClient.invalidateQueries({ queryKey: ["daily-report", projectId, reportId] });

  const workflow = useMutation({
    mutationFn: async (action: { type: "submit" | "review" | "approve" | "reject"; reason?: string }) => {
      if (action.type === "submit") return submitReport(projectId, reportId);
      if (action.type === "review") return reviewReport(projectId, reportId);
      if (action.type === "approve") return approveReport(projectId, reportId);
      return rejectReport(projectId, reportId, action.reason ?? "");
    },
    onSuccess: () => {
      toast.success("عملیات انجام شد");
      void refetch();
    },
    onError: (e) => toast.error((e as Error).message),
  });

  const exportPdf = async () => {
    setDownloading(true);
    try {
      const blob = await fetchReportPdf(projectId, reportId);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `daily-report-${reportId}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    } catch (e) {
      toast.error((e as Error).message);
    } finally {
      setDownloading(false);
    }
  };

  if (reportQuery.isLoading || !report) {
    return (
      <main className="mx-auto max-w-6xl px-4 py-6">
        <LoadingSkeleton rows={8} />
      </main>
    );
  }

  const base = `/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_DAILY_REPORTS}`;
  const tabProps = {
    projectId,
    reportId,
    report,
    readOnly: true,
    onChanged: () => {},
    activityOptions,
    subcontractorOptions: [],
  };

  return (
    <main className="page-main page-shell mx-auto max-w-6xl px-4 py-6">
      <Breadcrumb
        items={[
          { label: "گزارش‌های روزانه", href: base },
          { label: `گزارش ${formatDisplayDate(report.report_date)}` },
        ]}
      />
      <PageHeader
        title={`گزارش روزانه — ${formatDisplayDate(report.report_date)} (${report.day_of_week})`}
        subtitle={report.prepared_by_name ? `تهیه‌کننده: ${report.prepared_by_name}` : undefined}
        actions={
          <div className="flex gap-2">
            {report.status === "draft" || report.status === "rejected" ? (
              <Link
                to={`${base}/${reportId}/edit`}
                className="rounded-md border border-border px-4 py-2 text-sm hover:bg-muted/40"
              >
                ویرایش
              </Link>
            ) : null}
            <button
              type="button"
              onClick={exportPdf}
              disabled={downloading}
              className="inline-flex items-center gap-1 rounded-md bg-primary px-4 py-2 text-sm text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
            >
              <Download className="size-4" />
              خروجی PDF
            </button>
          </div>
        }
      />

      <div className="space-y-5">
        <ApprovalStatusBar
          report={report}
          canApprove={canApprove}
          busy={workflow.isPending}
          onSubmit={() => workflow.mutate({ type: "submit" })}
          onReview={() => workflow.mutate({ type: "review" })}
          onApprove={() => workflow.mutate({ type: "approve" })}
          onReject={(reason) => workflow.mutate({ type: "reject", reason })}
        />

        <div className="grid gap-3 rounded-xl border border-border bg-card p-4 sm:grid-cols-2 lg:grid-cols-4">
          <Info label="شیفت" value={report.shift} />
          <Info label="وضعیت کارگاه" value={report.site_status_label} />
          <Info label="وضعیت جوی" value={report.weather_condition_label ?? "—"} />
          <Info
            label="دما"
            value={
              report.temp_max || report.temp_min
                ? `${report.temp_max ?? "—"} / ${report.temp_min ?? "—"}`
                : "—"
            }
          />
        </div>

        {report.general_notes ? (
          <div className="rounded-xl border border-border bg-card p-4">
            <p className="mb-1 text-sm text-muted-foreground">توضیحات کلی</p>
            <p className="text-sm">{report.general_notes}</p>
          </div>
        ) : null}

        <Section title="فعالیت‌های اجرایی">
          <ActivityTab {...tabProps} />
        </Section>
        <Section title="نیروی انسانی">
          <LaborTab {...tabProps} />
        </Section>
        <Section title="ماشین‌آلات">
          <EquipmentTab {...tabProps} />
        </Section>
        <Section title="مصالح">
          <MaterialsTab {...tabProps} />
        </Section>
        <Section title="بتن‌ریزی">
          <ConcreteTab {...tabProps} />
        </Section>
        <Section title="کمپ کارگری">
          <LaborCampTab {...tabProps} />
        </Section>
        <Section title="حوادث و موانع">
          <IncidentsTab {...tabProps} />
        </Section>
      </div>
    </main>
  );
}

function Info({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="text-sm font-medium">{value}</p>
    </div>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="rounded-xl border border-border bg-card p-4">
      <h3 className="mb-3 text-base font-semibold">{title}</h3>
      {children}
    </div>
  );
}
