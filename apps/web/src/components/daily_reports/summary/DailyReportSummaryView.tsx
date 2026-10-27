import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Link, useParams } from "react-router";
import type {
  DailyReportDetail,
  DerivedSourceItem,
  MaterialReconciliationStatus,
} from "@/app/lib/api/daily-reports";
import { formatDisplayDate } from "@/app/lib/jalali-utils";
import { PATHS } from "@/app/routeVars";
import { findDepartmentBySlug } from "@/config/business-departments.config";
import { IncompletenessBanner } from "./IncompletenessBanner";
import { AttachmentCountLink } from "./AttachmentCountLink";
import { UnsetQuantityBadge } from "../UnsetQuantityBadge";

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

function ProvenanceCell({
  provenance,
  projectId,
  reportDate,
}: {
  provenance?: DerivedSourceItem[];
  projectId?: string;
  reportDate?: string;
}) {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);

  if (!provenance || provenance.length === 0) {
    return <span className='text-xs text-muted-foreground'>—</span>;
  }

  const count = provenance.length;

  return (
    <div className='relative inline-block text-xs'>
      <button
        type='button'
        onClick={() => setOpen((prev) => !prev)}
        className='inline-flex items-center gap-1 rounded border border-border bg-muted/60 px-2 py-0.5 font-medium hover:bg-muted focus:outline-none focus:ring-1 focus:ring-ring'
        aria-expanded={open}
        aria-label={t("dailyReports.summary.viewSources", "منابع ({{count}})", {
          count,
        })}
      >
        <span>
          {t("dailyReports.summary.viewSources", "منابع ({{count}})", {
            count,
          })}
        </span>
      </button>

      {open && (
        <div className='absolute left-0 z-20 mt-1 min-w-[200px] max-w-[280px] rounded-md border border-border bg-popover p-2 shadow-md text-popover-foreground'>
          <div className='mb-1 text-[11px] font-semibold text-muted-foreground'>
            {t("dailyReports.summary.sourceListTitle", "واحدهای مبدأ:")}
          </div>
          <ul className='space-y-1.5'>
            {provenance.map((src, idx) => {
              const dept = findDepartmentBySlug(src.unit);
              const deptLabel = dept ? t(dept.labelI18nKey, src.unit) : src.unit;
              const targetUrl =
                src.can_view_source && projectId && reportDate
                  ? `${PATHS.BUSINESS}/${projectId}/${src.unit}?date=${reportDate}`
                  : null;

              return (
                <li
                  key={idx}
                  className='flex items-center justify-between gap-2 border-b border-border/40 pb-1 text-xs last:border-0 last:pb-0'
                >
                  {targetUrl ? (
                    <Link
                      to={targetUrl}
                      className='font-medium text-primary underline hover:text-primary/80'
                      title={t(
                        "dailyReports.summary.goToSource",
                        "مشاهده گزارش واحد",
                      )}
                    >
                      {deptLabel}{" "}
                      <span className='text-[10px] opacity-75'>
                        (v{src.report_version})
                      </span>
                    </Link>
                  ) : (
                    <span className='text-muted-foreground'>
                      {deptLabel}{" "}
                      <span className='text-[10px] opacity-75'>
                        (v{src.report_version})
                      </span>
                    </span>
                  )}
                  {src.contribution_value != null && (
                    <span className='font-mono text-[11px] text-muted-foreground'>
                      {src.contribution_value}
                    </span>
                  )}
                </li>
              );
            })}
          </ul>
        </div>
      )}
    </div>
  );
}

function SimpleTable({
  headers,
  rows,
}: {
  headers: string[];
  rows: React.ReactNode[][];
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

export function DailyReportSummaryView({
  report,
  projectId,
  projectName,
  contractNumber,
  employer,
}: {
  report: DailyReportDetail;
  projectId?: string;
  projectName?: string;
  contractNumber?: string;
  employer?: string;
}) {
  const { t, i18n } = useTranslation();
  const params = useParams();
  const resolvedProjectId =
    projectId ?? params.projectId ?? params.businessId ?? params.id;

  const indirect = report.labor.filter((r) => r.labor_category === "indirect");
  const direct = report.labor.filter((r) => r.labor_category === "direct");
  const machineryRows = report.machinery?.rows ?? report.machinery_rows ?? [];
  const mainMaterials =
    report.materials_summary?.main_table ??
    report.materials.filter(
      (r) => r.transaction_type === "receipt" && r.receipt_resolved === true,
    );
  const detailMaterials =
    report.materials_summary?.details ??
    report.materials.filter(
      (r) => !(r.transaction_type === "receipt" && r.receipt_resolved === true),
    );
  const [showMaterialDetails, setShowMaterialDetails] = useState(false);
  const generalActivities = report.general_activities ?? [];
  const issues = report.issues ?? report.incidents.filter((row) => row.incident_type === "issue" || row.incident_type === "barrier");
  const visits = report.visits ?? [];
  const hseIncidents = report.hse_incidents ?? report.incidents.filter((row) => row.incident_type === "safety");

  function renderReconciliationPill(
    status: MaterialReconciliationStatus | undefined,
    rowId: string,
  ) {
    const normalized: MaterialReconciliationStatus =
      status === "match" ||
      status === "mismatch" ||
      status === "insufficient_data"
        ? status
        : "insufficient_data";

    const label =
      normalized === "match"
        ? t("dailyReports.summary.reconciliationMatch", "مطابق با سند انبار")
        : normalized === "mismatch"
          ? t(
              "dailyReports.summary.reconciliationMismatch",
              "مغایر با سند انبار",
            )
          : t(
              "dailyReports.summary.reconciliationInsufficientData",
              "اطلاعات ناکافی (فاقد سند منطبق)",
            );

    const badgeClass =
      normalized === "match"
        ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-700 dark:text-emerald-300"
        : normalized === "mismatch"
          ? "border-destructive/40 bg-destructive/10 text-destructive"
          : "border-amber-500/30 bg-amber-500/10 text-amber-700 dark:text-amber-300";

    return (
      <span
        key={`reconcile-${rowId}`}
        data-testid={`summary-material-reconciliation-${rowId}`}
        data-reconciliation-status={normalized}
        aria-label={label}
        className={`inline-flex items-center rounded-md border px-2 py-0.5 text-[11px] font-medium ${badgeClass}`}
      >
        {label}
      </span>
    );
  }

  const shiftLabel =
    report.shift === "full"
      ? t("dailyReports.summary.shiftFull", "کامل (روز)")
      : report.shift;

  return (
    <div data-testid='daily-report-summary-view'>
      <IncompletenessBanner
        aggregation={report.aggregation}
        projectId={resolvedProjectId}
        reportDate={report.report_date}
      />

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
              {report.site_status === "inactive" && report.inactivity_reason_label
                ? ` (${report.inactivity_reason_label})`
                : ""}
              {report.aggregation?.site_status_source === "override"
                ? ` (${t("dailyReports.summary.override", "لغو خودکار")})`
                : ""}
            </dd>
          </div>
          <div>
            <dt className='text-muted-foreground'>شرایط جوی</dt>
            <dd className='flex items-center gap-1.5 flex-wrap'>
              <span>{report.weather_condition_label ?? "—"}</span>
              {report.aggregation?.weather_source === "overridden_by_manager" ||
              report.aggregation?.weather_source === "override" ||
              report.weather_override ? (
                <span
                  data-testid='weather-manager-override-badge'
                  className='inline-flex items-center rounded-full bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-800 dark:bg-amber-900/50 dark:text-amber-200'
                >
                  {t("dailyReports.summary.managerOverrideBadge", "بازنویسی توسط مدیر")}
                </span>
              ) : null}
            </dd>
          </div>
          <div>
            <dt className='text-muted-foreground'>دما</dt>
            <dd>
              {report.temp_max != null || report.temp_min != null
                ? `${report.temp_max ?? "—"} / ${report.temp_min ?? "—"} °C`
                : "—"}
            </dd>
          </div>
          {report.weather_impact_notes ? (
            <div className='sm:col-span-2'>
              <dt className='text-muted-foreground'>تأثیر شرایط جوی</dt>
              <dd className='whitespace-pre-wrap'>{report.weather_impact_notes}</dd>
            </div>
          ) : null}
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

      <Section
        title={t("dailyReports.summary.indirectLabor", "نیروی انسانی غیرمستقیم (ستادی)")}
        testId='summary-indirect-labor'
      >
        <SimpleTable
          headers={[
            t("dailyReports.summary.colJobTitle", "عنوان شغلی"),
            t("dailyReports.summary.colContractor", "پیمانکار"),
            t("dailyReports.summary.colPresent", "حاضر"),
            t("dailyReports.summary.colLeave", "مرخصی"),
            t("dailyReports.summary.colOvertime", "اضافه‌کاری (ساعت)"),
            t("dailyReports.summary.colManHours", "نفر-ساعت"),
            t("dailyReports.summary.colDiscipline", "رشته"),
            t("dailyReports.summary.colSources", "منابع"),
          ]}
          rows={indirect.map((r) => [
            r.job_title,
            r.contractor_name || "—",
            r.present_count ?? r.shift_1_count,
            r.leave_count ?? r.absence_count ?? 0,
            r.overtime_hours ?? 0,
            r.man_hours ?? r.work_hours ?? "—",
            r.has_multiple_sources
              ? t("dailyReports.summary.multiUnit", "چند واحدی ({{count}})", {
                  count: r.source_count ?? r.provenance?.length ?? 2,
                })
              : (r.source_discipline ?? ""),
            <ProvenanceCell
              key={`prov-${r.id}`}
              provenance={r.provenance}
              projectId={resolvedProjectId}
              reportDate={report.report_date}
            />,
          ])}
        />
        {report.labor_summary?.totals?.indirect ? (
          <div
            className='mt-2 flex flex-wrap gap-4 border-t border-border/60 pt-2 text-xs text-muted-foreground'
            data-testid='summary-indirect-labor-totals'
          >
            <span>
              {t("dailyReports.summary.colPresent", "حاضر")}:{" "}
              <strong className='font-mono text-foreground'>
                {report.labor_summary.totals.indirect?.present_count ?? 0}
              </strong>
            </span>
            <span>
              {t("dailyReports.summary.colLeave", "مرخصی")}:{" "}
              <strong className='font-mono text-foreground'>
                {report.labor_summary.totals.indirect?.leave_count ?? 0}
              </strong>
            </span>
            <span>
              {t("dailyReports.summary.colOvertime", "اضافه‌کاری (ساعت)")}:{" "}
              <strong className='font-mono text-foreground'>
                {report.labor_summary.totals.indirect?.overtime_hours ?? "0.00"}
              </strong>
            </span>
            <span>
              {t("dailyReports.summary.colManHours", "نفر-ساعت")}:{" "}
              <strong className='font-mono text-foreground'>
                {report.labor_summary.totals.indirect?.man_hours ?? "0.00"}
              </strong>
            </span>
          </div>
        ) : null}
      </Section>

      <Section
        title={t("dailyReports.summary.directLabor", "نیروی انسانی مستقیم")}
        testId='summary-direct-labor'
      >
        <SimpleTable
          headers={[
            t("dailyReports.summary.colJobTitle", "عنوان شغلی"),
            t("dailyReports.summary.colContractor", "پیمانکار"),
            t("dailyReports.summary.colPresent", "حاضر"),
            t("dailyReports.summary.colLeave", "مرخصی"),
            t("dailyReports.summary.colOvertime", "اضافه‌کاری (ساعت)"),
            t("dailyReports.summary.colManHours", "نفر-ساعت"),
            t("dailyReports.summary.colDiscipline", "رشته"),
            t("dailyReports.summary.colSources", "منابع"),
          ]}
          rows={direct.map((r) => [
            r.job_title,
            r.contractor_name || "—",
            r.present_count ?? r.shift_1_count,
            r.leave_count ?? r.absence_count ?? 0,
            r.overtime_hours ?? 0,
            r.man_hours ?? r.work_hours ?? "—",
            r.has_multiple_sources
              ? t("dailyReports.summary.multiUnit", "چند واحدی ({{count}})", {
                  count: r.source_count ?? r.provenance?.length ?? 2,
                })
              : (r.source_discipline ?? ""),
            <ProvenanceCell
              key={`prov-${r.id}`}
              provenance={r.provenance}
              projectId={resolvedProjectId}
              reportDate={report.report_date}
            />,
          ])}
        />
        {report.labor_summary?.totals ? (
          <div
            className='mt-2 flex flex-wrap gap-6 border-t border-border/60 pt-2 text-xs text-muted-foreground'
            data-testid='summary-direct-and-overall-labor-totals'
          >
            <div>
              <span className='font-medium text-foreground'>
                {t("dailyReports.summary.directTotal", "جمع مستقیم")}:{" "}
              </span>
              {t("dailyReports.summary.colPresent", "حاضر")}{" "}
              <strong className='font-mono text-foreground'>
                {report.labor_summary.totals.direct?.present_count ?? 0}
              </strong>{" "}
              · {t("dailyReports.summary.colLeave", "مرخصی")}{" "}
              <strong className='font-mono text-foreground'>
                {report.labor_summary.totals.direct?.leave_count ?? 0}
              </strong>{" "}
              · {t("dailyReports.summary.colManHours", "نفر-ساعت")}{" "}
              <strong className='font-mono text-foreground'>
                {report.labor_summary.totals.direct?.man_hours ?? "0.00"}
              </strong>
            </div>
            <div>
              <span className='font-medium text-foreground'>
                {t("dailyReports.summary.overallLaborTotal", "جمع کل نیروی انسانی")}:{" "}
              </span>
              {t("dailyReports.summary.colPresent", "حاضر")}{" "}
              <strong className='font-mono text-foreground'>
                {report.labor_summary.totals.overall?.present_count ?? 0}
              </strong>{" "}
              · {t("dailyReports.summary.colLeave", "مرخصی")}{" "}
              <strong className='font-mono text-foreground'>
                {report.labor_summary.totals.overall?.leave_count ?? 0}
              </strong>{" "}
              · {t("dailyReports.summary.colManHours", "نفر-ساعت")}{" "}
              <strong className='font-mono text-foreground'>
                {report.labor_summary.totals.overall?.man_hours ?? "0.00"}
              </strong>
            </div>
          </div>
        ) : null}
      </Section>

      <Section
        title={t("dailyReports.summary.machinery", "وضعیت ماشین‌آلات و تجهیزات")}
        testId='summary-machinery'
      >
        <SimpleTable
          headers={[
            t("dailyReports.summary.colEquipmentType", "نوع ماشین‌آلات"),
            t("dailyReports.summary.colEquipmentRef", "شناسه تجهیز"),
            t("dailyReports.summary.colStatusTotal", "کل"),
            t("dailyReports.summary.colStatusActive", "فعال"),
            t("dailyReports.summary.colStatusReady", "آماده به کار"),
            t("dailyReports.summary.colStatusInactive", "غیرفعال"),
            t("dailyReports.summary.colStatusUnderRepair", "در حال تعمیر"),
            t("dailyReports.summary.colOperatingHours", "ساعت کارکرد"),
            t("dailyReports.summary.colStoppageHours", "ساعت توقف"),
            t("dailyReports.summary.colRepairHours", "ساعت تعمیر"),
            t("dailyReports.summary.colStoppageReason", "علت توقف"),
            t("dailyReports.summary.colSources", "منابع"),
          ]}
          rows={machineryRows.map((r) => {
            const isFa = (i18n.language || "fa").startsWith("fa");
            const reasonLabel = r.stoppage_reason
              ? isFa
                ? r.stoppage_reason.label_fa || r.stoppage_reason.label
                : r.stoppage_reason.label || r.stoppage_reason.label_fa
              : isFa
                ? r.stoppage_reason_label_fa ||
                  r.stoppage_reason_label ||
                  r.stoppage_reason_code
                : r.stoppage_reason_label ||
                  r.stoppage_reason_label_fa ||
                  r.stoppage_reason_code;

            const eqLabel = r.equipment_code
              ? `${r.equipment_code}${r.equipment_name ? ` — ${r.equipment_name}` : ""}`
              : r.equipment_ref || "—";

            return [
              r.equipment_type,
              eqLabel,
              r.status_total,
              r.status_active,
              r.status_ready,
              r.status_inactive,
              r.status_under_repair,
              r.operating_hours ?? "0.00",
              r.stoppage_hours ?? "0.00",
              r.repair_hours ?? "0.00",
              reasonLabel || "—",
              <ProvenanceCell
                key={`prov-${r.id}`}
                provenance={r.provenance}
                projectId={resolvedProjectId}
                reportDate={report.report_date}
              />,
            ];
          })}
        />
      </Section>

      <Section
        title={t("dailyReports.summary.materials", "مصالح وارده (دارای سند انبار)")}
        testId='summary-materials'
      >
        <SimpleTable
          headers={[
            t("dailyReports.summary.colDescription", "شرح"),
            t("dailyReports.summary.colQuantity", "مقدار"),
            t("dailyReports.summary.colUnit", "واحد"),
            t("dailyReports.summary.colSupplier", "تأمین‌کننده"),
            t("dailyReports.summary.colWarehouseDocument", "شماره سند انبار"),
            t("dailyReports.summary.colReconciliationStatus", "وضعیت تطبیق"),
            t("dailyReports.summary.colSources", "منابع"),
          ]}
          rows={mainMaterials.map((r) => [
            r.material_code
              ? `${r.material_code} — ${r.material_description}`
              : r.material_description,
            r.quantity,
            r.unit,
            r.supplier || "—",
            r.warehouse_document_reference || "—",
            renderReconciliationPill(r.reconciliation_status, r.id),
            <ProvenanceCell
              key={`prov-${r.id}`}
              provenance={r.provenance}
              projectId={resolvedProjectId}
              reportDate={report.report_date}
            />,
          ])}
        />

        <div className='mt-3 border-t border-border/60 pt-3'>
          <button
            type='button'
            data-testid='summary-materials-details-toggle'
            aria-expanded={showMaterialDetails}
            onClick={() => setShowMaterialDetails((prev) => !prev)}
            className='inline-flex items-center gap-1.5 rounded-md border border-border bg-muted/30 px-2.5 py-1 text-xs font-medium text-foreground hover:bg-muted/60'
          >
            <span>
              {showMaterialDetails
                ? t(
                    "dailyReports.summary.hideMaterialDetails",
                    "بستن جزئیات مصرف مصالح و رسیدهای فاقد سند",
                  )
                : t(
                    "dailyReports.summary.showMaterialDetails",
                    "مشاهده جزئیات مصرف مصالح و سایر تراکنش‌ها ({{count}})",
                    { count: detailMaterials.length },
                  )}
            </span>
          </button>

          {showMaterialDetails ? (
            <div
              className='mt-3 space-y-2 rounded-lg border border-border/60 bg-muted/15 p-3'
              data-testid='summary-materials-details-panel'
            >
              <SimpleTable
                headers={[
                  t("dailyReports.summary.colTransactionType", "نوع تراکنش"),
                  t("dailyReports.summary.colDescription", "شرح"),
                  t("dailyReports.summary.colQuantity", "مقدار"),
                  t("dailyReports.summary.colUnit", "واحد"),
                  t("dailyReports.summary.colConsumptionLocation", "محل مصرف"),
                  t("dailyReports.summary.colWarehouseDocument", "شماره سند انبار"),
                  t("dailyReports.summary.colReconciliationStatus", "وضعیت تطبیق"),
                  t("dailyReports.summary.colSources", "منابع"),
                ]}
                rows={detailMaterials.map((r) => [
                  r.transaction_type === "receipt"
                    ? t("dailyReports.summary.txReceipt", "ورود (فاقد سند منطبق)")
                    : t("dailyReports.summary.txConsumption", "مصرف"),
                  r.material_code
                    ? `${r.material_code} — ${r.material_description}`
                    : r.material_description,
                  r.quantity,
                  r.unit,
                  r.consumption_location || "—",
                  r.warehouse_document_reference || "—",
                  renderReconciliationPill(r.reconciliation_status, r.id),
                  <ProvenanceCell
                    key={`prov-detail-${r.id}`}
                    provenance={r.provenance}
                    projectId={resolvedProjectId}
                    reportDate={report.report_date}
                  />,
                ])}
              />
            </div>
          ) : null}
        </div>
      </Section>

      <Section title={t("dailyReports.summary.concrete", "حجم بتن ریخته‌شده")} testId='summary-section-concrete'>
        <SimpleTable
          headers={[
            t("dailyReports.summary.colDescription", "شرح"),
            t("dailyReports.summary.colQuantity", "حجم (م۳)"),
            t("dailyReports.summary.concreteElement", "عضو سازه‌ای"),
            t("dailyReports.summary.colParcel", "پلاک / محدوده"),
            t("dailyReports.summary.concreteDelivery", "بچینگ / حواله"),
            t("dailyReports.summary.concreteSampling", "نمونه‌گیری / آزمون"),
            t("dailyReports.summary.concreteQc", "کنترل کیفیت"),
            t("dailyReports.summary.colSources", "منابع"),
          ]}
          rows={report.concrete_logs.map((r) => [
            r.concrete_description,
            r.volume_m3,
            r.structural_element || [r.zone, r.block, r.floor].filter(Boolean).join(" / "),
            [r.parcel, r.zone, r.block, r.floor].filter(Boolean).join(" / ") || "—",
            [r.batching_plant, r.truck_delivery_note_number].filter(Boolean).join(" / ") || "—",
            [r.sampling_state, r.lab_sample_code, r.test_sheet_count != null ? `${r.test_sheet_count}` : ""]
              .filter(Boolean).join(" / ") || "—",
            r.qc_link ? <a className='underline text-primary' href={r.qc_link.href}>{t("dailyReports.summary.openQc", "مشاهده کنترل کیفیت")}</a> : "—",
            <ProvenanceCell
              key={`prov-${r.id}`}
              provenance={r.provenance}
              projectId={resolvedProjectId}
              reportDate={report.report_date}
            />,
          ])}
        />
      </Section>

      <Section
        title={t("dailyReports.summary.activities", "فعالیت‌های اجرا شده کارگاه")}
        testId='summary-activities'
      >
        <SimpleTable
          headers={[
            t("dailyReports.summary.colDescription", "شرح"),
            t("dailyReports.summary.colShift", "شیفت"),
            t("dailyReports.summary.colContractor", "پیمانکار"),
            t("dailyReports.summary.colCrewName", "اکیپ"),
            t("dailyReports.summary.colHeadcount", "نفر"),
            t("dailyReports.summary.colParcel", "پلاک"),
            t("dailyReports.summary.colLocation", "محل"),
            t("dailyReports.summary.colQuantity", "مقدار"),
            t("dailyReports.summary.colUnit", "واحد"),
            t("dailyReports.summary.colDiscipline", "رشته"),
            t("dailyReports.summary.colSources", "منابع"),
          ]}
          rows={report.activities.map((r) => [
            r.activity_code
              ? `${r.activity_code} — ${r.activity_description}`
              : r.activity_description,
            r.shift,
            r.contractor ?? (r.subcontractor_name || "—"),
            r.crew_name || "—",
            r.headcount ?? "—",
            r.parcel || "—",
            [r.location ?? r.zone, r.block, r.floor].filter(Boolean).join(" / ") || "—",
            <UnsetQuantityBadge
              key={`quantity-${r.id}`}
              quantity={r.quantity}
              quantityMeasured={r.quantity_measured}
            />,
            r.unit || "—",
            r.source_discipline ?? "",
            <ProvenanceCell
              key={`prov-${r.id}`}
              provenance={r.provenance}
              projectId={resolvedProjectId}
              reportDate={report.report_date}
            />,
          ])}
        />
      </Section>

      <Section
        title={t("dailyReports.summary.generalActivities", "فعالیت‌های عمومی کارگاه")}
        testId='summary-section-general'
      >
        <SimpleTable
          headers={[
            t("dailyReports.summary.colDescription", "شرح"),
            t("dailyReports.summary.colLocation", "محل"),
            t("dailyReports.summary.colQuantity", "مقدار"),
            t("dailyReports.summary.colUnit", "واحد"),
            t("dailyReports.summary.notes", "توضیحات"),
            t("dailyReports.summary.colSources", "منابع"),
          ]}
          rows={generalActivities.map((row) => [
            row.activity_description,
            row.location || "—",
            // General activities carry no measurable flag: nullability only.
            <UnsetQuantityBadge
              key={`general-quantity-${row.id}`}
              quantity={row.quantity}
              quantityMeasured={undefined}
            />,
            row.unit ?? "—",
            row.notes || "—",
            <ProvenanceCell key={`general-${row.id}`} provenance={row.provenance} projectId={resolvedProjectId} reportDate={report.report_date} />,
          ])}
        />
      </Section>

      <Section
        title={t("dailyReports.summary.issues", "ملاحظات / مسائل")}
        testId='summary-section-issues'
      >
        <SimpleTable
          headers={[
            t("dailyReports.summary.issueKind", "نوع"), t("dailyReports.summary.colDescription", "شرح"),
            t("dailyReports.summary.issueOwner", "مسئول پیگیری"), t("dailyReports.summary.issueDue", "مهلت"),
            t("dailyReports.summary.colSources", "منابع"),
          ]}
          rows={issues.map((row) => [
            row.incident_type, row.description, row.follow_up_owner_name || "—", row.due_date || "—",
            <ProvenanceCell key={`issue-${row.id}`} provenance={row.provenance} projectId={resolvedProjectId} reportDate={report.report_date} />,
          ])}
        />
      </Section>

      <Section
        title={t("dailyReports.summary.visits", "بازدیدها")}
        testId='summary-section-visits'
      >
        <SimpleTable
          headers={[t("dailyReports.summary.colDescription", "شرح بازدید"), t("dailyReports.summary.colSources", "منابع")]}
          rows={visits.map((row) => [
            row.text,
            <ProvenanceCell key={`visit-${row.id}`} provenance={row.provenance} projectId={resolvedProjectId} reportDate={report.report_date} />,
          ])}
        />
      </Section>

      <Section title={t("dailyReports.summary.hse", "رخدادهای HSE")} testId='summary-section-hse'>
        <SimpleTable
          headers={[
            t("dailyReports.summary.colDescription", "شرح"), t("dailyReports.summary.hseSeverity", "شدت"),
            t("dailyReports.summary.hseAction", "اقدام فوری"), t("dailyReports.summary.hseNotification", "شناسه اعلان"),
            t("dailyReports.summary.colSources", "منابع"),
          ]}
          rows={hseIncidents.map((row) => [
            row.description, row.severity || "—", row.corrective_action || "—", row.notification_id || "—",
            <ProvenanceCell key={`hse-${row.id}`} provenance={row.provenance} projectId={resolvedProjectId} reportDate={report.report_date} />,
          ])}
        />
      </Section>

      {(report.attachment_counts ?? []).length > 0 ? (
        <Section title={t("dailyReports.summary.attachments", "تصاویر فعالیت‌ها")} testId='summary-section-attachments'>
          <div className='space-y-2'>
            {(report.attachment_counts ?? []).map((entry) => (
              <AttachmentCountLink
                key={entry.section}
                count={entry.count}
                links={entry.first_links}
                label={t("dailyReports.summary.attachmentsForSection", "تصاویر {{section}}", { section: entry.section })}
              />
            ))}
          </div>
        </Section>
      ) : null}

      <Section title={t("dailyReports.summary.managementOpinion", "نظر مدیریت")}>
        <pre className='whitespace-pre-wrap text-sm'>
          {report.management_opinion || "—"}
        </pre>
      </Section>
    </div>
  );
}
