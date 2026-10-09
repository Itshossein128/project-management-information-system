import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Link } from "react-router";
import { useTranslation } from "react-i18next";
import {
  fetchPeriodReport,
  fetchPeriodReports,
  generatePeriodReport,
  overridePeriodReportFigure,
  type PeriodReport,
} from "@/app/lib/api/progress";
import { Button } from "@/components/ui/sprint-button";
import { useToast } from "@/components/ui/toast";
import { Input } from "@/components/form";

function mondayOf(d = new Date()) {
  const x = new Date(d);
  const day = x.getDay();
  const diff = day === 0 ? -6 : 1 - day;
  x.setDate(x.getDate() + diff);
  return x.toISOString().slice(0, 10);
}

function sundayOf(d = new Date()) {
  const mon = new Date(mondayOf(d));
  mon.setDate(mon.getDate() + 6);
  return mon.toISOString().slice(0, 10);
}

function monthBounds(d = new Date()) {
  const start = new Date(d.getFullYear(), d.getMonth(), 1);
  const end = new Date(d.getFullYear(), d.getMonth() + 1, 0);
  return {
    start: start.toISOString().slice(0, 10),
    end: end.toISOString().slice(0, 10),
  };
}

export function PeriodReportsPanel({ projectId }: { projectId: string }) {
  const { t } = useTranslation();
  const toast = useToast();
  const qc = useQueryClient();
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [overrideFigureId, setOverrideFigureId] = useState<string | null>(null);
  const [overrideValue, setOverrideValue] = useState("");
  const [overrideReason, setOverrideReason] = useState("");

  const { data: reports = [] } = useQuery({
    queryKey: ["progress-reports", projectId],
    queryFn: () => fetchPeriodReports(projectId),
  });

  const { data: detail } = useQuery({
    queryKey: ["progress-report", projectId, selectedId],
    queryFn: () => fetchPeriodReport(projectId, selectedId!),
    enabled: Boolean(selectedId),
  });

  const generateMutation = useMutation({
    mutationFn: (kind: "weekly" | "monthly") => {
      if (kind === "weekly") {
        return generatePeriodReport(projectId, {
          kind,
          period_start: mondayOf(),
          period_end: sundayOf(),
        });
      }
      const m = monthBounds();
      return generatePeriodReport(projectId, {
        kind,
        period_start: m.start,
        period_end: m.end,
      });
    },
    onSuccess: (report) => {
      toast.success(t("progressReports.generated"));
      setSelectedId(report.id);
      void qc.invalidateQueries({ queryKey: ["progress-reports", projectId] });
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const overrideMutation = useMutation({
    mutationFn: () =>
      overridePeriodReportFigure(projectId, overrideFigureId!, {
        new_value: overrideValue,
        reason: overrideReason.trim(),
      }),
    onSuccess: () => {
      toast.success(t("progressReports.overrideSaved"));
      setOverrideFigureId(null);
      setOverrideValue("");
      setOverrideReason("");
      void qc.invalidateQueries({ queryKey: ["progress-report", projectId, selectedId] });
    },
    onError: (e: Error) => toast.error(e.message),
  });

  return (
    <section
      className="space-y-3 rounded-xl border border-border bg-card p-4"
      data-testid="period-reports-panel"
    >
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h2 className="text-lg font-semibold">{t("progressReports.title")}</h2>
        <div className="flex flex-wrap gap-2">
          <Button
            size="sm"
            variant="secondary"
            loading={generateMutation.isPending}
            onClick={() => generateMutation.mutate("weekly")}
            data-testid="generate-weekly-report"
          >
            {t("progressReports.generateWeekly")}
          </Button>
          <Button
            size="sm"
            variant="secondary"
            loading={generateMutation.isPending}
            onClick={() => generateMutation.mutate("monthly")}
            data-testid="generate-monthly-report"
          >
            {t("progressReports.generateMonthly")}
          </Button>
        </div>
      </div>

      <div className="flex flex-wrap gap-2">
        {reports.length === 0 ? (
          <p className="text-sm text-muted-foreground">{t("progressReports.empty")}</p>
        ) : (
          reports.map((r: PeriodReport) => (
            <Button
              key={r.id}
              size="sm"
              variant={selectedId === r.id ? "primary" : "ghost"}
              onClick={() => setSelectedId(r.id)}
            >
              {r.kind === "weekly"
                ? t("progressReports.weekly")
                : t("progressReports.monthly")}{" "}
              {r.period_start} → {r.period_end}
            </Button>
          ))
        )}
      </div>

      {detail?.figures ? (
        <div className="overflow-x-auto rounded-lg border">
          <table className="w-full min-w-[640px] text-sm">
            <thead className="bg-muted/40">
              <tr>
                <th className="px-3 py-2 text-start">{t("progressReports.section")}</th>
                <th className="px-3 py-2 text-start">{t("progressReports.value")}</th>
                <th className="px-3 py-2 text-start">{t("progressReports.source")}</th>
                <th className="px-3 py-2 text-start">{t("progressReports.updated")}</th>
                <th className="px-3 py-2 text-start">{t("common.actions")}</th>
              </tr>
            </thead>
            <tbody>
              {detail.figures.map((f) => (
                <tr key={f.id} className="border-t">
                  <td className="px-3 py-2">{f.section}</td>
                  <td className="px-3 py-2">
                    {f.value_status === "not_recorded"
                      ? t("progressReports.notRecorded")
                      : typeof f.value === "object"
                        ? JSON.stringify(f.value)
                        : String(f.value ?? "—")}
                  </td>
                  <td className="px-3 py-2">
                    {f.source_path ? (
                      <Link className="text-primary underline" to={f.source_path}>
                        {f.source_type}
                        {f.source_approved ? ` (${t("progressReports.approved")})` : ""}
                      </Link>
                    ) : (
                      f.source_type || "—"
                    )}
                  </td>
                  <td className="px-3 py-2 text-xs text-muted-foreground">
                    {f.last_updated_at
                      ? new Date(f.last_updated_at).toLocaleString()
                      : "—"}
                  </td>
                  <td className="px-3 py-2">
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => {
                        setOverrideFigureId(f.id);
                        setOverrideValue(
                          typeof f.value === "string" || typeof f.value === "number"
                            ? String(f.value)
                            : "",
                        );
                      }}
                    >
                      {t("progressReports.override")}
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}

      {overrideFigureId ? (
        <div className="space-y-2 rounded-md border border-warning-200 bg-warning-50 p-3 dark:bg-warning-950/30">
          <p className="text-sm font-medium">{t("progressReports.overrideTitle")}</p>
          <Input
            value={overrideValue}
            onChange={(e) => setOverrideValue(e.target.value)}
            placeholder={t("progressReports.newValue")}
          />
          <Input
            value={overrideReason}
            onChange={(e) => setOverrideReason(e.target.value)}
            placeholder={t("progressReports.reasonRequired")}
          />
          <div className="flex gap-2">
            <Button
              size="sm"
              variant="primary"
              disabled={!overrideReason.trim()}
              loading={overrideMutation.isPending}
              onClick={() => overrideMutation.mutate()}
            >
              {t("common.save")}
            </Button>
            <Button size="sm" variant="secondary" onClick={() => setOverrideFigureId(null)}>
              {t("common.cancel")}
            </Button>
          </div>
        </div>
      ) : null}
    </section>
  );
}
