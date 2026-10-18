import { useTranslation } from "react-i18next";
import type { DailyReportDetail } from "@/app/lib/api/daily-reports";
import { formatDisplayDate } from "@/app/lib/jalali-utils";
import { IncompletenessBanner } from "./IncompletenessBanner";

function Section({
  title,
  children,
  testId,
}: {
  title: string;
  children: React.ReactNode;
  testId?: string;
}) {
  return (
    <section
      className='mb-6 rounded-xl border border-border bg-card p-4'
      data-testid={testId}
    >
      <h2 className='mb-3 text-base font-semibold'>{title}</h2>
      {children}
    </section>
  );
}

function SimpleTable({
  headers,
  rows,
}: {
  headers: string[];
  rows: (string | number | null | undefined)[][];
}) {
  if (rows.length === 0) {
    return <p className='text-sm text-muted-foreground'>—</p>;
  }
  return (
    <div className='overflow-x-auto'>
      <table className='w-full min-w-[480px] text-sm'>
        <thead>
          <tr className='text-muted-foreground'>
            {headers.map((h) => (
              <th key={h} className='px-2 py-1 text-right font-medium'>
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={i} className='border-t border-border'>
              {row.map((cell, j) => (
                <td key={j} className='px-2 py-1'>
                  {cell ?? "—"}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function parseAutoNotes(generalNotes: string | null | undefined): {
  issues: string;
  visits: string;
  general: string;
  rest: string;
} {
  const raw = generalNotes ?? "";
  const markerStart = "<!--auto-summary-notes-->";
  const markerEnd = "<!--/auto-summary-notes-->";
  let auto = "";
  let rest = raw;
  if (raw.includes(markerStart) && raw.includes(markerEnd)) {
    const before = raw.split(markerStart)[0] ?? "";
    const mid = raw.split(markerStart)[1]?.split(markerEnd)[0] ?? "";
    const after = raw.split(markerEnd)[1] ?? "";
    auto = mid.trim();
    rest = `${before}${after}`.trim();
  }
  const pick = (label: string) => {
    const re = new RegExp(`${label}:\\n([\\s\\S]*?)(?=\\n\\n[\\u0600-\\u06FF]+:|$)`);
    const m = auto.match(re);
    return m?.[1]?.trim() ?? "";
  };
  return {
    general: pick("فعالیت‌های عمومی"),
    issues: pick("ملاحظات"),
    visits: pick("بازدیدها"),
    rest,
  };
}

export function DailyReportSummaryView({
  report,
  projectName,
  contractNumber,
  employer,
}: {
  report: DailyReportDetail;
  projectName?: string;
  contractNumber?: string;
  employer?: string;
}) {
  const { t } = useTranslation();
  const indirect = report.labor.filter((r) => r.labor_category === "indirect");
  const direct = report.labor.filter((r) => r.labor_category === "direct");
  const notes = parseAutoNotes(report.general_notes);

  const shiftLabel =
    report.shift === "full"
      ? t("dailyReports.summary.shiftFull", "کامل (روز)")
      : report.shift;

  return (
    <div data-testid='daily-report-summary-view'>
      <IncompletenessBanner aggregation={report.aggregation} />

      <Section
        title={t("dailyReports.summary.header", "سربرگ گزارش روزانه")}
        testId='summary-section-header'
      >
        <dl className='grid gap-2 text-sm sm:grid-cols-2'>
          <div>
            <dt className='text-muted-foreground'>عنوان</dt>
            <dd>{t("dailyReports.summary.title", "گزارش روزانه")}</dd>
          </div>
          <div>
            <dt className='text-muted-foreground'>تاریخ</dt>
            <dd>
              {formatDisplayDate(report.report_date)} — {report.day_of_week}
            </dd>
          </div>
          <div>
            <dt className='text-muted-foreground'>پروژه</dt>
            <dd>{projectName ?? "—"}</dd>
          </div>
          <div>
            <dt className='text-muted-foreground'>
              {t("dailyReports.summary.contractNumber", "شماره قرارداد")}
            </dt>
            <dd>{contractNumber || "—"}</dd>
          </div>
          <div>
            <dt className='text-muted-foreground'>
              {t("dailyReports.summary.employer", "کارفرما")}
            </dt>
            <dd>{employer || "—"}</dd>
          </div>
          <div>
            <dt className='text-muted-foreground'>وضعیت کارگاه</dt>
            <dd>
              {report.site_status_label}
              {report.aggregation?.site_status_source === "override"
                ? ` (${t("dailyReports.summary.override", "لغو خودکار")})`
                : ""}
            </dd>
          </div>
          <div>
            <dt className='text-muted-foreground'>شرایط جوی</dt>
            <dd>
              {report.weather_condition_label ?? "—"}
              {report.aggregation?.weather_source === "override"
                ? ` (${t("dailyReports.summary.override", "لغو خودکار")})`
                : ""}
            </dd>
          </div>
        </dl>
      </Section>

      <Section
        title={t("dailyReports.summary.workHours", "ساعات کار / شیفت‌ها")}
        testId='summary-section-shifts'
      >
        <dl className='grid gap-2 text-sm sm:grid-cols-3'>
          <div>
            <dt className='text-muted-foreground'>شیفت</dt>
            <dd>{shiftLabel}</dd>
          </div>
          <div>
            <dt className='text-muted-foreground'>جبهه کار</dt>
            <dd>{report.work_front || "—"}</dd>
          </div>
          <div>
            <dt className='text-muted-foreground'>محل</dt>
            <dd>{report.location_notes || "—"}</dd>
          </div>
        </dl>
      </Section>

      <Section title={t("dailyReports.summary.indirectLabor", "نیروی انسانی غیرمستقیم (ستادی)")}>
        <SimpleTable
          headers={["عنوان شغلی", "حاضر", "مرخصی", "رشته"]}
          rows={indirect.map((r) => [
            r.job_title,
            r.shift_1_count,
            r.absence_count ?? 0,
            r.source_discipline ?? "",
          ])}
        />
      </Section>

      <Section title={t("dailyReports.summary.directLabor", "نیروی انسانی مستقیم")}>
        <SimpleTable
          headers={["عنوان شغلی", "حاضر", "مرخصی", "رشته"]}
          rows={direct.map((r) => [
            r.job_title,
            r.shift_1_count,
            r.absence_count ?? 0,
            r.source_discipline ?? "",
          ])}
        />
      </Section>

      <Section title={t("dailyReports.summary.materials", "مصالح وارده")}>
        <SimpleTable
          headers={["شرح", "مقدار", "واحد"]}
          rows={report.materials.map((r) => [
            r.material_description,
            r.quantity,
            r.unit,
          ])}
        />
      </Section>

      <Section title={t("dailyReports.summary.concrete", "حجم بتن ریخته‌شده")}>
        <SimpleTable
          headers={["شرح", "حجم (م۳)", "قطعه/بلوک/طبقه"]}
          rows={report.concrete_logs.map((r) => [
            r.concrete_description,
            r.volume_m3,
            [r.zone, r.block, r.floor].filter(Boolean).join(" / "),
          ])}
        />
      </Section>

      <Section title={t("dailyReports.summary.activities", "فعالیت‌های اجرا شده کارگاه")}>
        <SimpleTable
          headers={[
            "شرح",
            "شیفت",
            "پیمانکار",
            "نفر",
            "محل",
            "مقدار",
            "واحد",
            "رشته",
          ]}
          rows={report.activities.map((r) => [
            r.activity_description,
            r.shift,
            r.subcontractor_name,
            r.headcount,
            [r.zone, r.block, r.floor].filter(Boolean).join(" / "),
            r.quantity,
            r.unit,
            r.source_discipline ?? "",
          ])}
        />
      </Section>

      <Section
        title={t("dailyReports.summary.generalActivities", "فعالیت‌های عمومی کارگاه")}
        testId='summary-section-general'
      >
        <pre className='whitespace-pre-wrap text-sm'>{notes.general || "—"}</pre>
      </Section>

      <Section
        title={t("dailyReports.summary.issues", "ملاحظات / مسائل")}
        testId='summary-section-issues'
      >
        <pre className='whitespace-pre-wrap text-sm'>
          {[notes.issues, notes.rest].filter(Boolean).join("\n\n") || "—"}
        </pre>
      </Section>

      <Section
        title={t("dailyReports.summary.visits", "بازدیدها")}
        testId='summary-section-visits'
      >
        <pre className='whitespace-pre-wrap text-sm'>{notes.visits || "—"}</pre>
      </Section>

      <Section title={t("dailyReports.summary.managementOpinion", "نظر مدیریت")}>
        <pre className='whitespace-pre-wrap text-sm'>
          {report.management_opinion || "—"}
        </pre>
      </Section>
    </div>
  );
}
