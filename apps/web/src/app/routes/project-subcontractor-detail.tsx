import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { Link, useParams } from "react-router";
import { ProjectProvider, usePermission, useProject } from "@/app/contexts/project-context";
import {
  computeOverallLive,
  createScore,
  createSubcontractor,
  createWarning,
  fetchSubcontractor,
  formatFaAmount,
  resolveWarning,
  scoreBg,
  scoreColor,
  STATUS_COLORS,
  STATUS_LABELS,
  type SubcontractorWarning,
  WARNING_TYPE_LABELS,
} from "@/app/lib/api/subcontractors";
import { fetchIPCs, IPC_STATUS_LABELS } from "@/app/lib/api/contracts";
import { PATHS } from "@/app/routeVars";
import { PerformanceRadarChart } from "@/components/subcontractors/PerformanceRadarChart";
import { RiskBadge } from "@/components/subcontractors/RiskBadge";
import { ScoreSlider } from "@/components/subcontractors/ScoreSlider";
import { WarningTimeline } from "@/components/subcontractors/WarningTimeline";
import { Breadcrumb, LoadingSkeleton, PageHeader } from "@/components/layout/page-header";
import { Drawer } from "@/components/ui/drawer";
import { Button } from "@/components/ui/sprint-button";
import { useToast } from "@/components/ui/toast";
import * as XLSX from "xlsx";

type Tab = "performance" | "financial" | "warnings" | "activities";

function trendIcon(trend: string) {
  if (trend === "improving") return "↑";
  if (trend === "declining") return "↓";
  return "→";
}

function SubcontractorDetailContent() {
  const { projectId, project, isLoading: projectLoading } = useProject();
  const { subId = "" } = useParams();
  const qc = useQueryClient();
  const toast = useToast();
  const { has } = usePermission(projectId);
  const canView = has("view_contracts");
  const canEdit = has("edit_contracts");

  const [tab, setTab] = useState<Tab>("performance");
  const [scoreDrawer, setScoreDrawer] = useState(false);
  const [warningDrawer, setWarningDrawer] = useState(false);
  const [resolveModal, setResolveModal] = useState<SubcontractorWarning | null>(null);
  const [activityFrom, setActivityFrom] = useState("");
  const [activityTo, setActivityTo] = useState("");

  const [scoreForm, setScoreForm] = useState({
    score_date: new Date().toISOString().slice(0, 10),
    progress_score: 7,
    quality_score: 7,
    hse_score: 7,
    payment_compliance_score: 7,
    cooperation_score: 7,
    notes: "",
  });

  const [warningForm, setWarningForm] = useState({
    warning_date: new Date().toISOString().slice(0, 10),
    warning_type: "written",
    reason: "",
  });

  const [resolveForm, setResolveForm] = useState({
    resolved_date: new Date().toISOString().slice(0, 10),
    resolution_notes: "",
  });

  const { data: sub, isLoading } = useQuery({
    queryKey: ["subcontractor", projectId, subId],
    queryFn: () => fetchSubcontractor(projectId, subId),
    enabled: canView && Boolean(subId),
  });

  const { data: ipcs } = useQuery({
    queryKey: ["ipcs", projectId, sub?.contract],
    queryFn: () => fetchIPCs(projectId, { contract_id: sub!.contract! }),
    enabled: Boolean(sub?.contract),
  });

  const liveOverall = useMemo(
    () =>
      computeOverallLive({
        progress_score: scoreForm.progress_score,
        quality_score: scoreForm.quality_score,
        hse_score: scoreForm.hse_score,
        payment_compliance_score: scoreForm.payment_compliance_score,
        cooperation_score: scoreForm.cooperation_score,
      }),
    [scoreForm],
  );

  const saveScore = useMutation({
    mutationFn: () => createScore(projectId, subId, scoreForm),
    onSuccess: () => {
      toast.success("ارزیابی ثبت شد");
      setScoreDrawer(false);
      void qc.invalidateQueries({ queryKey: ["subcontractor", projectId, subId] });
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const saveWarning = useMutation({
    mutationFn: () => createWarning(projectId, subId, warningForm),
    onSuccess: () => {
      toast.success("اخطار ثبت شد");
      setWarningDrawer(false);
      void qc.invalidateQueries({ queryKey: ["subcontractor", projectId, subId] });
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const saveResolve = useMutation({
    mutationFn: () =>
      resolveWarning(projectId, subId, resolveModal!.id, {
        resolved: true,
        ...resolveForm,
      }),
    onSuccess: () => {
      toast.success("رفع اخطار ثبت شد");
      setResolveModal(null);
      void qc.invalidateQueries({ queryKey: ["subcontractor", projectId, subId] });
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const filteredActivities = useMemo(() => {
    if (!sub?.recent_activities) return [];
    return sub.recent_activities.filter((a) => {
      if (activityFrom && a.report_date < activityFrom) return false;
      if (activityTo && a.report_date > activityTo) return false;
      return true;
    });
  }, [sub?.recent_activities, activityFrom, activityTo]);

  const exportExcel = () => {
    const rows = filteredActivities.map((a) => ({
      تاریخ: a.report_date,
      شیفت: a.shift,
      قطعه: a.zone ?? "",
      بلوک: a.block ?? "",
      طبقه: a.floor ?? "",
      شرح: a.activity_description,
      نفر: a.headcount ?? "",
      مقدار: a.quantity ?? "",
      واحد: a.unit ?? "",
    }));
    const ws = XLSX.utils.json_to_sheet(rows);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "فعالیت‌ها");
    XLSX.writeFile(wb, `sub-${sub?.company_name ?? subId}.xlsx`);
  };

  if (projectLoading || isLoading) return <LoadingSkeleton rows={12} />;
  if (!project || !sub) return <p>پیمانکار یافت نشد</p>;
  if (!canView) return <p className="p-8 text-center text-muted-foreground">دسترسی ندارید.</p>;

  const latest = sub.performance_history[0] ?? null;
  const fin = sub.financial_status;

  return (
    <div className="space-y-6">
      <Breadcrumb
        items={[
          { label: "پروژه‌ها", href: `/${PATHS.PROJECT}` },
          { label: project.project_name, href: `/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_OVERVIEW}` },
          { label: "پیمانکاران فرعی", href: `/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_SUBCONTRACTORS}` },
          { label: sub.company_name },
        ]}
      />

      <div className="rounded-lg border p-6">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold">{sub.company_name}</h1>
            <div className="mt-2 flex flex-wrap gap-2">
              {sub.discipline ? (
                <span className="rounded bg-muted px-2 py-0.5 text-sm">{sub.discipline}</span>
              ) : null}
              <span className={`rounded px-2 py-0.5 text-sm ${STATUS_COLORS[sub.status] ?? ""}`}>
                {STATUS_LABELS[sub.status] ?? sub.status}
              </span>
              {sub.risk_flag ? <RiskBadge reasons={sub.risk_reasons} /> : null}
            </div>
          </div>
        </div>
        <div className="mt-4 grid gap-4 md:grid-cols-2 text-sm">
          <div className="space-y-1">
            <p>مسئول: {sub.responsible_person || "—"}</p>
            <p>تلفن: {sub.phone || "—"}</p>
          </div>
          <div className="space-y-1">
            {sub.contract_summary ? (
              <>
                <p>قرارداد: {sub.contract_summary.contract_number || sub.contract_summary.counterparty}</p>
                <p>مبلغ: {formatFaAmount(sub.contract_summary.adjusted_amount)} ریال</p>
              </>
            ) : (
              <p className="text-muted-foreground">قراردادی متصل نیست</p>
            )}
          </div>
        </div>
      </div>

      <div className="flex flex-wrap gap-2">
        {(
          [
            ["performance", "عملکرد"],
            ["financial", "وضعیت مالی"],
            ["warnings", "هشدارها"],
            ["activities", "گزارش فعالیت‌ها"],
          ] as const
        ).map(([key, label]) => (
          <Button
            key={key}
            variant={tab === key ? "primary" : "secondary"}
            size="sm"
            onClick={() => setTab(key)}
          >
            {label}
          </Button>
        ))}
      </div>

      {tab === "performance" ? (
        <div className="space-y-6">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <span className={`text-4xl font-bold ${scoreColor(latest?.overall_score)}`}>
                {latest?.overall_score?.toFixed(1) ?? "—"}
              </span>
              <span className="text-2xl text-muted-foreground">{trendIcon(sub.trend)}</span>
            </div>
            {canEdit ? (
              <Button variant="primary" onClick={() => setScoreDrawer(true)}>
                ثبت ارزیابی جدید
              </Button>
            ) : null}
          </div>
          <PerformanceRadarChart latest={latest} history={sub.performance_history} />
          <div className="overflow-x-auto rounded-lg border">
            <table className="w-full text-sm">
              <thead className="bg-muted/50">
                <tr>
                  {["تاریخ", "پیشرفت", "کیفیت", "HSE", "پرداخت", "همکاری", "نمره کل"].map((h) => (
                    <th key={h} className="px-3 py-2 text-start">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {sub.performance_history.map((s) => (
                  <tr key={s.id} className="border-t">
                    <td className="px-3 py-2">{s.score_date}</td>
                    <td className="px-3 py-2">{s.progress_score ?? "—"}</td>
                    <td className="px-3 py-2">{s.quality_score ?? "—"}</td>
                    <td className="px-3 py-2">{s.hse_score ?? "—"}</td>
                    <td className="px-3 py-2">{s.payment_compliance_score ?? "—"}</td>
                    <td className="px-3 py-2">{s.cooperation_score ?? "—"}</td>
                    <td className={`px-3 py-2 font-medium ${scoreBg(s.overall_score)} ${scoreColor(s.overall_score)}`}>
                      {s.overall_score?.toFixed(1) ?? "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : null}

      {tab === "financial" ? (
        <div className="space-y-6">
          {!sub.contract ? (
            <p className="rounded-lg border p-6 text-muted-foreground">
              این پیمانکار به قراردادی متصل نیست. برای مشاهده وضعیت مالی، ابتدا قرارداد را انتخاب کنید.
            </p>
          ) : (
            <>
              <div className="grid gap-4 md:grid-cols-4">
                {[
                  ["صورت وضعیت ارسالی", fin.total_billed],
                  ["پرداخت شده", fin.total_paid],
                  ["طلب معوق", fin.outstanding],
                  ["سپرده نگه‌داشته", fin.retention_held],
                ].map(([label, val]) => (
                  <div key={String(label)} className="rounded-lg border p-4">
                    <p className="text-sm text-muted-foreground">{label}</p>
                    <p className="text-lg font-semibold">{formatFaAmount(Number(val))}</p>
                  </div>
                ))}
              </div>
              <div className="rounded-lg border p-4">
                <p className="mb-2 text-sm">
                  پیش‌پرداخت: {formatFaAmount(fin.advance_paid)} — استهلاک: {formatFaAmount(fin.advance_recovered)} — مانده: {formatFaAmount(fin.advance_remaining)}
                </p>
                <div className="h-3 overflow-hidden rounded-full bg-muted">
                  <div
                    className="h-full bg-amber-500"
                    style={{
                      width: `${fin.advance_paid > 0 ? (fin.advance_recovered / fin.advance_paid) * 100 : 0}%`,
                    }}
                  />
                </div>
              </div>
              <div className="overflow-x-auto rounded-lg border">
                <table className="w-full text-sm">
                  <thead className="bg-muted/50">
                    <tr>
                      {["شماره IPC", "ناخالص", "خالص", "وضعیت", "تأخیر"].map((h) => (
                        <th key={h} className="px-3 py-2 text-start">{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {(ipcs?.results ?? []).map((ipc) => (
                      <tr key={ipc.id} className="border-t">
                        <td className="px-3 py-2">{ipc.ipc_number}</td>
                        <td className="px-3 py-2">{formatFaAmount(ipc.gross_amount)}</td>
                        <td className="px-3 py-2">{formatFaAmount(ipc.net_amount ?? 0)}</td>
                        <td className="px-3 py-2">{IPC_STATUS_LABELS[ipc.status] ?? ipc.status}</td>
                        <td className={`px-3 py-2 ${ipc.days_overdue ? "text-red-600" : ""}`}>
                          {ipc.days_overdue ? `${ipc.days_overdue} روز` : "—"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          )}
        </div>
      ) : null}

      {tab === "warnings" ? (
        <div className="space-y-4">
          <div className="flex justify-end">
            {canEdit ? (
              <Button variant="primary" onClick={() => setWarningDrawer(true)}>
                صدور اخطار
              </Button>
            ) : null}
          </div>
          <WarningTimeline
            warnings={sub.warnings}
            canEdit={canEdit}
            onResolve={(w) => setResolveModal(w)}
          />
        </div>
      ) : null}

      {tab === "activities" ? (
        <div className="space-y-4">
          <div className="flex flex-wrap items-end gap-3">
            <label className="text-sm">
              از
              <input type="date" className="ms-2 rounded border px-2 py-1" value={activityFrom} onChange={(e) => setActivityFrom(e.target.value)} />
            </label>
            <label className="text-sm">
              تا
              <input type="date" className="ms-2 rounded border px-2 py-1" value={activityTo} onChange={(e) => setActivityTo(e.target.value)} />
            </label>
            <Button variant="secondary" onClick={exportExcel}>
              خروجی اکسل
            </Button>
          </div>
          <div className="overflow-x-auto rounded-lg border">
            <table className="w-full text-sm">
              <thead className="bg-muted/50">
                <tr>
                  {["تاریخ", "شیفت", "شرح", "نفر", "مقدار", "گزارش"].map((h) => (
                    <th key={h} className="px-3 py-2 text-start">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {filteredActivities.map((a) => (
                  <tr key={a.id} className="border-t">
                    <td className="px-3 py-2">{a.report_date}</td>
                    <td className="px-3 py-2">{a.shift}</td>
                    <td className="px-3 py-2">{a.activity_description}</td>
                    <td className="px-3 py-2">{a.headcount ?? "—"}</td>
                    <td className="px-3 py-2">{a.quantity != null ? `${a.quantity} ${a.unit ?? ""}` : "—"}</td>
                    <td className="px-3 py-2">
                      <Link
                        to={`/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_DAILY_REPORTS}/${a.report_id}/view`}
                        className="text-primary underline"
                      >
                        مشاهده
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : null}

      <Drawer
        isOpen={scoreDrawer}
        onClose={() => setScoreDrawer(false)}
        title="ثبت ارزیابی جدید"
        footer={
          <Button variant="primary" onClick={() => saveScore.mutate()} disabled={saveScore.isPending}>
            ذخیره
          </Button>
        }
      >
        <div className="space-y-4">
          <label className="block text-sm">
            تاریخ
            <input
              type="date"
              className="mt-1 w-full rounded border px-3 py-2"
              value={scoreForm.score_date}
              onChange={(e) => setScoreForm({ ...scoreForm, score_date: e.target.value })}
            />
          </label>
          <ScoreSlider label="پیشرفت کاری" value={scoreForm.progress_score} onChange={(v) => setScoreForm({ ...scoreForm, progress_score: v })} />
          <ScoreSlider label="کیفیت اجرا" value={scoreForm.quality_score} onChange={(v) => setScoreForm({ ...scoreForm, quality_score: v })} />
          <ScoreSlider label="HSE" value={scoreForm.hse_score} onChange={(v) => setScoreForm({ ...scoreForm, hse_score: v })} />
          <ScoreSlider label="پرداخت" value={scoreForm.payment_compliance_score} onChange={(v) => setScoreForm({ ...scoreForm, payment_compliance_score: v })} />
          <ScoreSlider label="همکاری" value={scoreForm.cooperation_score} onChange={(v) => setScoreForm({ ...scoreForm, cooperation_score: v })} />
          {liveOverall != null ? (
            <div className="rounded-lg bg-amber-50 p-4 text-center">
              <p className="text-sm text-amber-800">نمره کل محاسبه شده</p>
              <p className="text-2xl font-bold text-amber-900">{liveOverall.toFixed(1)}</p>
            </div>
          ) : null}
          <textarea
            className="w-full rounded border px-3 py-2 text-sm"
            placeholder="یادداشت"
            rows={3}
            value={scoreForm.notes}
            onChange={(e) => setScoreForm({ ...scoreForm, notes: e.target.value })}
          />
        </div>
      </Drawer>

      <Drawer
        isOpen={warningDrawer}
        onClose={() => setWarningDrawer(false)}
        title="صدور اخطار"
        footer={
          <Button
            variant="primary"
            onClick={() => saveWarning.mutate()}
            disabled={saveWarning.isPending || warningForm.reason.length < 20}
          >
            ثبت
          </Button>
        }
      >
        <div className="space-y-4">
          <input type="date" className="w-full rounded border px-3 py-2" value={warningForm.warning_date} onChange={(e) => setWarningForm({ ...warningForm, warning_date: e.target.value })} />
          <div className="space-y-2">
            {Object.entries(WARNING_TYPE_LABELS).map(([k, label]) => (
              <label key={k} className="flex items-center gap-2 text-sm">
                <input type="radio" name="wtype" checked={warningForm.warning_type === k} onChange={() => setWarningForm({ ...warningForm, warning_type: k })} />
                {label}
              </label>
            ))}
          </div>
          <textarea
            className="w-full rounded border px-3 py-2 text-sm"
            placeholder="دلیل (حداقل 20 کاراکتر)"
            rows={4}
            value={warningForm.reason}
            onChange={(e) => setWarningForm({ ...warningForm, reason: e.target.value })}
          />
        </div>
      </Drawer>

      {resolveModal ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
          <div className="w-full max-w-md rounded-lg bg-background p-6 shadow-xl">
            <h3 className="text-lg font-semibold">ثبت رفع مشکل</h3>
            <div className="mt-4 space-y-3">
              <input type="date" className="w-full rounded border px-3 py-2" value={resolveForm.resolved_date} onChange={(e) => setResolveForm({ ...resolveForm, resolved_date: e.target.value })} />
              <textarea className="w-full rounded border px-3 py-2 text-sm" rows={3} placeholder="یادداشت رفع" value={resolveForm.resolution_notes} onChange={(e) => setResolveForm({ ...resolveForm, resolution_notes: e.target.value })} />
            </div>
            <div className="mt-4 flex justify-end gap-2">
              <Button variant="secondary" onClick={() => setResolveModal(null)}>انصراف</Button>
              <Button variant="primary" onClick={() => saveResolve.mutate()} disabled={saveResolve.isPending}>ثبت رفع مشکل</Button>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}

export default function ProjectSubcontractorDetailPage() {
  const { projectId = "" } = useParams();
  return (
    <ProjectProvider projectId={projectId}>
      <SubcontractorDetailContent />
    </ProjectProvider>
  );
}
