import { useEffect, useMemo, useRef, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router";
import { CloudOff, Save } from "lucide-react";
import { useToast } from "@/components/ui/toast";
import { useDailyReportForm } from "@/app/hooks/useDailyReportForm";
import { usePermission } from "@/app/contexts/project-context";
import { PATHS } from "@/app/routeVars";
import { apiJson } from "@/app/lib/api-client";
import { fetchActivities } from "@/app/lib/api/activities";
import {
  approveReport,
  type DailyReportDetail,
  fetchDailyReport,
  rejectReport,
  reviewReport,
  submitReport,
} from "@/app/lib/api/daily-reports";
import { getCachedActivities, getCachedSubcontractors } from "@/app/lib/offlineDB";
import { warmProjectCache } from "@/app/lib/offlineCache";
import { isNetworkError } from "@/app/lib/offlineWrite";
import { isoToJalali, jalaliToIso } from "@/app/lib/jalali-utils";
import { Breadcrumb, LoadingSkeleton } from "@/components/layout/page-header";
import { Tabs, TabsContent as ShadcnTabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ActivityTab } from "./ActivityTab";
import { ApprovalStatusBar } from "./ApprovalStatusBar";
import { ConcreteTab } from "./ConcreteTab";
import { EquipmentTab } from "./EquipmentTab";
import { IncidentsTab } from "./IncidentsTab";
import { LaborCampTab } from "./LaborCampTab";
import { LaborTab } from "./LaborTab";
import { MaterialsTab } from "./MaterialsTab";
import {
  emptyHeaderState,
  type HeaderState,
  headerToPayload,
  ReportHeader,
} from "./ReportHeader";

type TabKey =
  | "activities"
  | "labor"
  | "equipment"
  | "materials"
  | "concrete"
  | "labor_camp"
  | "incidents";

const TABS: { key: TabKey; label: string }[] = [
  { key: "activities", label: "فعالیت‌ها" },
  { key: "labor", label: "نیروی انسانی" },
  { key: "equipment", label: "ماشین‌آلات" },
  { key: "materials", label: "مصالح" },
  { key: "concrete", label: "بتن‌ریزی" },
  { key: "labor_camp", label: "کمپ کارگری" },
  { key: "incidents", label: "حوادث" },
];

// Detail serializer returns report_date already in Jalali (YYYY/MM/DD); the
// datepicker needs ISO Gregorian, so convert back.
function headerFromDetail(d: DailyReportDetail): HeaderState {
  const iso = d.report_date ? jalaliToIso(d.report_date) : "";
  return {
    report_date: iso || emptyHeaderState().report_date,
    shift: d.shift,
    site_status: d.site_status,
    weather_condition: d.weather_condition,
    temp_max: d.temp_max ?? "",
    temp_min: d.temp_min ?? "",
    general_notes: d.general_notes ?? "",
  };
}

export function DailyReportForm({
  projectId,
  reportId: initialReportId,
}: {
  projectId: string;
  reportId?: string;
}) {
  const navigate = useNavigate();
  const toast = useToast();
  const queryClient = useQueryClient();
  const { has } = usePermission(projectId);
  const canApprove = has("approve_reports");

  const [reportId, setReportId] = useState<string | undefined>(initialReportId);
  const [header, setHeader] = useState<HeaderState>(emptyHeaderState());
  const [activeTab, setActiveTab] = useState<TabKey>("activities");
  const { saveHeader: saveHeaderOffline, isOnline } = useDailyReportForm(projectId, reportId);
  const lastSavedHeaderRef = useRef(JSON.stringify(headerToPayload(emptyHeaderState())));
  const headerAutosaveTimerRef = useRef<number | null>(null);

  const reportQuery = useQuery({
    queryKey: ["daily-report", projectId, reportId],
    queryFn: () => fetchDailyReport(projectId, reportId!),
    enabled: Boolean(reportId),
  });
  const report = reportQuery.data ?? null;

  useEffect(() => {
    if (report) {
      const nextHeader = headerFromDetail(report);
      setHeader(nextHeader);
      lastSavedHeaderRef.current = JSON.stringify(headerToPayload(nextHeader));
    }
  }, [report]);

  useEffect(() => {
    if (projectId) void warmProjectCache(projectId);
  }, [projectId]);

  const activitiesQuery = useQuery({
    queryKey: ["activities-lite", projectId],
    queryFn: async () => {
      if (isNetworkError()) {
        const cached = await getCachedActivities(projectId);
        return {
          results: cached.map((a) => ({
            activity_id: String(a.activity_id),
            activity_code: String(a.activity_code ?? ""),
            activity_name: String(a.activity_name ?? ""),
          })),
        };
      }
      return fetchActivities(projectId, { per_page: 500 });
    },
  });
  const subcontractorsQuery = useQuery({
    queryKey: ["subcontractors", projectId],
    queryFn: async () => {
      if (isNetworkError()) {
        return getCachedSubcontractors(projectId);
      }
      try {
        const data = await apiJson<{ results?: unknown[] } | unknown[]>(
          `/${PATHS.API_PROJECTS}/${projectId}/contracts/`,
        );
        return Array.isArray(data) ? data : (data.results ?? []);
      } catch {
        return [];
      }
    },
  });

  const activityOptions = useMemo(
    () =>
      (activitiesQuery.data?.results ?? []).map((a) => ({
        value: a.activity_id,
        label: `${a.activity_code} - ${a.activity_name}`,
      })),
    [activitiesQuery.data],
  );
  const subcontractorOptions = useMemo(
    () =>
      (Array.isArray(subcontractorsQuery.data) ? subcontractorsQuery.data : []).map(
        (c: any) => ({
          value: String(c.id ?? c.contract_id ?? ""),
          label: String(c.counterparty ?? c.name ?? c.contract_number ?? ""),
        }),
      ),
    [subcontractorsQuery.data],
  );

  const editable = !report || report.status === "draft" || report.status === "rejected";

  const refetch = () => {
    void queryClient.invalidateQueries({ queryKey: ["daily-report", projectId, reportId] });
  };

  const saveHeader = useMutation({
    mutationFn: () => saveHeaderOffline(headerToPayload(header)),
    onSuccess: ({ reportId: savedId, offline }) => {
      toast.success(offline ? "به صورت آفلاین ذخیره شد" : "هدر گزارش ذخیره شد");
      if (!reportId) {
        setReportId(savedId);
        navigate(
          `/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_DAILY_REPORTS}/${savedId}/edit`,
          { replace: true },
        );
      } else if (!offline) {
        refetch();
      }
    },
    onError: (e) => toast.error((e as Error).message),
  });

  useEffect(() => {
    if (!editable || saveHeader.isPending || !header.report_date) return;
    const payload = headerToPayload(header);
    const payloadKey = JSON.stringify(payload);
    if (payloadKey === lastSavedHeaderRef.current) return;
    if (headerAutosaveTimerRef.current) {
      window.clearTimeout(headerAutosaveTimerRef.current);
    }
    headerAutosaveTimerRef.current = window.setTimeout(async () => {
      try {
        const { reportId: savedId, offline } = await saveHeaderOffline(payload);
        lastSavedHeaderRef.current = payloadKey;
        if (!reportId) {
          setReportId(savedId);
          navigate(`/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_DAILY_REPORTS}/${savedId}/edit`, {
            replace: true,
          });
          return;
        }
        if (!offline) {
          refetch();
        }
      } catch {
        // Keep autosave silent; manual save button still surfaces explicit errors.
      }
    }, 900);
    return () => {
      if (headerAutosaveTimerRef.current) {
        window.clearTimeout(headerAutosaveTimerRef.current);
      }
    };
  }, [editable, header, navigate, projectId, refetch, reportId, saveHeader.isPending, saveHeaderOffline]);

  const workflow = useMutation({
    mutationFn: async (action: { type: "submit" | "review" | "approve" | "reject"; reason?: string }) => {
      if (!reportId) throw new Error("no report");
      if (action.type === "submit") return submitReport(projectId, reportId);
      if (action.type === "review") return reviewReport(projectId, reportId);
      if (action.type === "approve") return approveReport(projectId, reportId);
      return rejectReport(projectId, reportId, action.reason ?? "");
    },
    onSuccess: () => {
      toast.success("عملیات انجام شد");
      refetch();
    },
    onError: (e) => toast.error((e as Error).message),
  });

  const tabProps = {
    projectId,
    reportId: reportId ?? null,
    report,
    readOnly: !editable,
    onChanged: refetch,
    activityOptions,
    subcontractorOptions,
  };

  const counts: Record<TabKey, number> = {
    activities: report?.activities.length ?? 0,
    labor: report?.labor.length ?? 0,
    equipment: report?.equipment.length ?? 0,
    materials: report?.materials.length ?? 0,
    concrete: report?.concrete_logs.length ?? 0,
    labor_camp: report?.labor_camp.length ?? 0,
    incidents: report?.incidents.length ?? 0,
  };

  if (reportId && reportQuery.isLoading) return <LoadingSkeleton rows={8} />;

  const listHref = `/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_DAILY_REPORTS}`;

  return (
    <div className="space-y-5" data-testid="daily-report-form">
      <Breadcrumb
        items={[
          { label: "گزارش‌های روزانه", href: listHref },
          { label: reportId ? `گزارش ${isoToJalali(header.report_date)}` : "گزارش جدید" },
        ]}
      />

      {!isOnline ? (
        <div className="flex items-center gap-2 rounded-lg border border-warning-300 bg-warning-50 px-4 py-2 text-sm text-warning-900 dark:bg-warning-950/30 dark:text-warning-200">
          <CloudOff className="size-4" />
          حالت آفلاین — تغییرات به صورت محلی ذخیره و پس از اتصال همگام‌سازی می‌شوند.
        </div>
      ) : null}

      {report ? (
        <ApprovalStatusBar
          report={report}
          canApprove={canApprove}
          busy={workflow.isPending}
          onSubmit={() => workflow.mutate({ type: "submit" })}
          onReview={() => workflow.mutate({ type: "review" })}
          onApprove={() => workflow.mutate({ type: "approve" })}
          onReject={(reason) => workflow.mutate({ type: "reject", reason })}
        />
      ) : null}

      <ReportHeader value={header} onChange={setHeader} readOnly={!editable} />

      {editable ? (
        <div className="flex justify-end">
          <button
            type="button"
            onClick={() => saveHeader.mutate()}
            disabled={saveHeader.isPending || !header.report_date}
            data-testid="daily-report-save-header"
            className="inline-flex items-center gap-1 rounded-md bg-primary px-5 py-2 text-sm text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
          >
            <Save className="size-4" />
            {reportId ? "ذخیره هدر" : "ایجاد گزارش"}
          </button>
        </div>
      ) : (
        <p className="rounded-md bg-muted p-3 text-sm text-muted-foreground">
          این گزارش قابل ویرایش نیست. برای مشاهده جزئیات از حالت نمایش استفاده کنید.
        </p>
      )}

      <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as TabKey)} className="w-full" dir="rtl">
        <div className="rounded-xl border border-border bg-card">
          <TabsList className="flex h-auto flex-wrap justify-start gap-1 rounded-none border-b border-border bg-transparent p-2">
            {TABS.map((t) => (
              <TabsTrigger
                key={t.key}
                value={t.key}
                data-testid={`report-tab-${t.key}`}
                className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground"
              >
                {t.label}
                {counts[t.key] > 0 ? (
                  <span className="ms-1 rounded-full bg-black/10 px-1.5 text-xs dark:bg-white/10">
                    {counts[t.key]}
                  </span>
                ) : null}
              </TabsTrigger>
            ))}
          </TabsList>
          <div className="p-4">
            <ShadcnTabsContent value="activities" className="mt-0"><ActivityTab {...tabProps} /></ShadcnTabsContent>
            <ShadcnTabsContent value="labor" className="mt-0"><LaborTab {...tabProps} /></ShadcnTabsContent>
            <ShadcnTabsContent value="equipment" className="mt-0"><EquipmentTab {...tabProps} /></ShadcnTabsContent>
            <ShadcnTabsContent value="materials" className="mt-0"><MaterialsTab {...tabProps} /></ShadcnTabsContent>
            <ShadcnTabsContent value="concrete" className="mt-0"><ConcreteTab {...tabProps} /></ShadcnTabsContent>
            <ShadcnTabsContent value="labor_camp" className="mt-0"><LaborCampTab {...tabProps} /></ShadcnTabsContent>
            <ShadcnTabsContent value="incidents" className="mt-0"><IncidentsTab {...tabProps} /></ShadcnTabsContent>
          </div>
        </div>
      </Tabs>
    </div>
  );
}
