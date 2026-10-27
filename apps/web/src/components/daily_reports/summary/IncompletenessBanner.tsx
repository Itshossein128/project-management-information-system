import { useTranslation } from "react-i18next";
import { Link } from "react-router";
import type { AggregationMeta } from "@/app/lib/api/daily-reports";
import { PATHS } from "@/app/routeVars";
import {
  BUSINESS_DEPARTMENTS,
  findDepartmentBySlug,
} from "@/config/business-departments.config";

const LEGACY_DISCIPLINE_LABELS: Record<string, string> = {
  civil: "ابنیه",
  electrical: "برق",
  mechanical: "مکانیک",
  plumbing: "لوله‌کشی",
  hvac: "تهویه",
  finishing: "نازک‌کاری",
};

interface IncompletenessBannerProps {
  aggregation?: AggregationMeta;
  projectId?: string;
  reportDate?: string;
}

export function IncompletenessBanner({
  aggregation,
  projectId,
  reportDate,
}: IncompletenessBannerProps) {
  const { t } = useTranslation();

  if (!aggregation) return null;

  const completeness = aggregation.completeness;

  const renderCompleteBanner = () => (
    <div
      role='status'
      className='mb-4 rounded-lg border border-emerald-300 bg-emerald-50 p-4 text-sm text-emerald-950 dark:border-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-100'
      data-testid='daily-report-complete-banner'
    >
      <div className='font-semibold flex items-center gap-2'>
        <span>
          {t(
            "dailyReports.summary.completeTitle",
            "تمام گزارش‌های دیسیپلین دریافت و تجمیع شدند",
          )}
        </span>
      </div>
    </div>
  );

  // Modern canonical completeness handling (Feature 032, US3)
  if (completeness) {
    if (completeness.state === "complete") {
      return renderCompleteBanner();
    }

    if (completeness.state === "configuration_incomplete") {
      return (
        <div
          role='alert'
          className='mb-4 rounded-lg border border-amber-300 bg-amber-50 p-4 text-sm text-amber-950 dark:border-amber-700 dark:bg-amber-950/40 dark:text-amber-100'
          data-testid='daily-report-config-incomplete-banner'
        >
          <div className='font-semibold'>
            {t(
              "dailyReports.summary.configIncompleteTitle",
              "الگوی گزارش روزانه فعال نشده است",
            )}
          </div>
          <p className='mt-1 text-xs text-amber-800 dark:text-amber-200'>
            {t(
              "dailyReports.summary.configIncompleteDesc",
              "برای این پروژه و تاریخ، هنوز الگوی واحد‌های الزامی فعال نشده است؛ وضعیت روز تا زمان فعال‌سازی ناقص می‌ماند.",
            )}
          </p>
        </div>
      );
    }

    // state === "partial"
    const getUnitLabel = (slug: string) => {
      const dept = findDepartmentBySlug(slug);
      return dept ? t(dept.labelI18nKey, slug) : slug;
    };

    return (
      <div
        role='status'
        className='mb-4 rounded-lg border border-amber-300 bg-amber-50 p-4 text-sm text-amber-950 dark:border-amber-700 dark:bg-amber-950/40 dark:text-amber-100'
        data-testid='daily-report-partial-banner'
      >
        <div className='font-semibold'>
          {t("dailyReports.summary.partialTitle", "جمع‌بندی روزانه ناقص است")}
        </div>

        <div className='mt-2 flex flex-wrap gap-2 items-center text-xs'>
          <span className='font-medium text-amber-900 dark:text-amber-200'>
            {t("dailyReports.summary.contributingUnits", "واحدهای ارسال‌شده:")}
          </span>
          {completeness.contributing_units.length === 0 ? (
            <span className='text-muted-foreground'>—</span>
          ) : (
            completeness.contributing_units.map((unit) => (
              <span
                key={unit}
                className='inline-flex items-center rounded-full bg-emerald-100 px-2.5 py-0.5 font-medium text-emerald-800 dark:bg-emerald-900/50 dark:text-emerald-200'
              >
                {getUnitLabel(unit)}
              </span>
            ))
          )}
        </div>

        <div className='mt-2 flex flex-wrap gap-2 items-center text-xs'>
          <span className='font-medium text-rose-900 dark:text-rose-200'>
            {t("dailyReports.summary.missingUnits", "واحدهای الزامی ارسال‌نشده:")}
          </span>
          {completeness.missing_units.map((unit) => {
            const label = getUnitLabel(unit);
            const targetUrl =
              projectId && reportDate
                ? `${PATHS.BUSINESS}/${projectId}/${unit}?date=${reportDate}`
                : null;

            return targetUrl ? (
              <Link
                key={unit}
                to={targetUrl}
                className='inline-flex items-center rounded-full border border-rose-300 bg-rose-100 px-2.5 py-0.5 font-medium text-rose-800 underline decoration-rose-400 hover:bg-rose-200 dark:border-rose-700 dark:bg-rose-950/60 dark:text-rose-200'
                title={t("dailyReports.summary.goToUnitReport", "ثبت گزارش {{unit}}", {
                  unit: label,
                })}
              >
                {label}
              </Link>
            ) : (
              <span
                key={unit}
                className='inline-flex items-center rounded-full bg-rose-100 px-2.5 py-0.5 font-medium text-rose-800 dark:bg-rose-900/50 dark:text-rose-200'
              >
                {label}
              </span>
            );
          })}
        </div>
      </div>
    );
  }

  // Fallback for legacy format
  if (!aggregation.is_partial) return renderCompleteBanner();
  const missing = (aggregation.missing_disciplines || [])
    .map((d) => LEGACY_DISCIPLINE_LABELS[d] ?? d)
    .join("، ");
  const contributing = (aggregation.contributing_disciplines || []).length;

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
