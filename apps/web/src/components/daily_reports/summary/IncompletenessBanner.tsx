import { useTranslation } from "react-i18next";
import type { AggregationMeta } from "@/app/lib/api/daily-reports";

const DISCIPLINE_LABELS: Record<string, string> = {
  civil: "ابنیه",
  electrical: "برق",
  mechanical: "مکانیک",
  plumbing: "لوله‌کشی",
  hvac: "تهویه",
  finishing: "نازک‌کاری",
};

export function IncompletenessBanner({ aggregation }: { aggregation?: AggregationMeta }) {
  const { t } = useTranslation();
  if (!aggregation?.is_partial) return null;
  const missing = aggregation.missing_disciplines
    .map((d) => DISCIPLINE_LABELS[d] ?? d)
    .join("، ");
  const contributing = aggregation.contributing_disciplines.length;
  return (
    <div
      role='status'
      className='mb-4 rounded-lg border border-amber-300 bg-amber-50 px-4 py-3 text-sm text-amber-950 dark:border-amber-700 dark:bg-amber-950/40 dark:text-amber-100'
      data-testid='daily-report-partial-banner'
    >
      {contributing === 0
        ? t(
            "dailyReports.summary.noSpecialty",
            "هنوز گزارش واحد تخصصی برای این روز ثبت نشده است.",
          )
        : t(
            "dailyReports.summary.partial",
            "جمع‌بندی ناقص است. واحدهای ارسال‌نشده: {{missing}}",
            { missing: missing || "—" },
          )}
    </div>
  );
}
