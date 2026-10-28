import { getStoredActorId, requireStoredActorId } from "@/app/lib/auth-storage";
import { useEffect, useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import { useSearchParams } from "react-router";
import { Download } from "lucide-react";
import {
  fetchSubReportExcel,
  type CanonicalUnit,
  type UnitReport,
  type UnitReportStatus,
  unitSupportsActivitiesSection,
  unitSupportsConcreteSection,
  unitSupportsGeneralSection,
  unitSupportsHseSection,
  unitSupportsIssuesSection,
  unitSupportsLaborSection,
  unitSupportsMachinerySection,
  unitSupportsMaterialsSection,
  unitSupportsVisitsSection,
} from "@/app/lib/api/unit-reports";
import {
  useApproveUnitReport,
  useCorrectUnitReport,
  useCurrentUnitReportQuery,
  useDeleteUnitReport,
  useOpenUnitReport,
  useRejectUnitReport,
  useSubmitUnitReport,
  useUnitReportHistoryQuery,
} from "@/app/hooks/queries";
import { ApiRequestError } from "@/app/lib/api-client";
import { Button, TextArea } from "@/components/form";
import { JalaliDatePicker } from "@/components/form/JalaliDatePicker";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Modal } from "@/components/overlay/modal";
import { queueUnitReportOperation } from "@/app/lib/offlineWrite";
import {
  getLocalSnapshotsByProject,
  type LocalReportSnapshot,
} from "@/app/lib/offlineDB";
import { SectionActivities } from "./section-activities";
import { SectionConcrete } from "./section-concrete";
import { SectionGeneral } from "./section-general";
import { SectionHse } from "./section-hse";
import { SectionIssues } from "./section-issues";
import { SectionLabor } from "./section-labor";
import { SectionMachinery } from "./section-machinery";
import { SectionMaterials } from "./section-materials";
import { SectionVisits } from "./section-visits";

export interface UnitDailyReportPanelProps {
  businessId: string;
  unit: CanonicalUnit;
  onReportChange?: (report: UnitReport | null) => void;
  selectedDate?: string;
  onDateChange?: (date: string) => void;
}

function statusToVariant(status: UnitReportStatus | string): "neutral" | "info" | "success" | "danger" {
  switch (status) {
    case "draft":
      return "neutral";
    case "submitted":
      return "info";
    case "approved":
      return "success";
    case "rejected":
      return "danger";
    default:
      return "neutral";
  }
}

function statusToLabelKey(status: UnitReportStatus | string): string {
  switch (status) {
    case "draft":
      return "businessDepartment.unitReport.statusDraft";
    case "submitted":
      return "businessDepartment.unitReport.statusSubmitted";
    case "approved":
      return "businessDepartment.unitReport.statusApproved";
    case "rejected":
      return "businessDepartment.unitReport.statusRejected";
    default:
      return "status.draft";
  }
}

const SUB_DISCIPLINE_OPTIONS: Record<string, { value: string; labelKey: string }[]> = {
  mechanical: [
    { value: "MECHANICAL", labelKey: "businessDepartment.unitReport.subDisciplines.mechanical" },
    { value: "PLUMBING", labelKey: "businessDepartment.unitReport.subDisciplines.plumbing" },
    { value: "HVAC", labelKey: "businessDepartment.unitReport.subDisciplines.hvac" },
  ],
  buildings: [
    { value: "CIVIL", labelKey: "businessDepartment.unitReport.subDisciplines.civil" },
    { value: "FINISHING", labelKey: "businessDepartment.unitReport.subDisciplines.finishing" },
  ],
};

export function UnitDailyReportPanel({
  businessId,
  unit,
  onReportChange,
  selectedDate: propDate,
  onDateChange,
}: UnitDailyReportPanelProps) {
  const { t, i18n } = useTranslation();
  const [searchParams, setSearchParams] = useSearchParams();

  const urlDate = searchParams.get("date");
  const fallbackDate = useMemo(() => new Date().toISOString().slice(0, 10), []);
  const activeDate = propDate || urlDate || fallbackDate;

  useEffect(() => {
    if (!searchParams.get("date") && activeDate) {
      setSearchParams(
        (prev) => {
          const next = new URLSearchParams(prev);
          next.set("date", activeDate);
          return next;
        },
        { replace: true },
      );
      onDateChange?.(activeDate);
    }
  }, [searchParams, setSearchParams, activeDate, onDateChange]);

  const handleDateChange = (newDate: string) => {
    setActionError(null);
    setActionErrorCode(null);
    setSearchParams(
      (prev) => {
        const next = new URLSearchParams(prev);
        if (newDate) {
          next.set("date", newDate);
        } else {
          next.delete("date");
        }
        return next;
      },
      { replace: true },
    );
    onDateChange?.(newDate);
  };

  const currentQuery = useCurrentUnitReportQuery(businessId, unit, activeDate);
  const report = currentQuery.data ?? null;

  useEffect(() => {
    onReportChange?.(report);
  }, [report, onReportChange]);

  const openMutation = useOpenUnitReport(businessId, unit);
  const submitMutation = useSubmitUnitReport(businessId, unit);
  const approveMutation = useApproveUnitReport(businessId, unit);
  const rejectMutation = useRejectUnitReport(businessId, unit);
  const correctMutation = useCorrectUnitReport(businessId, unit);
  const deleteMutation = useDeleteUnitReport(businessId, unit);

  const [rejectModalOpen, setRejectModalOpen] = useState(false);
  const [rejectionReason, setRejectionReason] = useState("");
  const [rejectionError, setRejectionError] = useState<string | null>(null);

  const [historyModalOpen, setHistoryModalOpen] = useState(false);
  const historyQuery = useUnitReportHistoryQuery(
    businessId,
    unit,
    report?.id,
    historyModalOpen && Boolean(report?.id),
  );

  const [actionError, setActionError] = useState<string | null>(null);
  const [actionErrorCode, setActionErrorCode] = useState<string | null>(null);
  const [rejectionErrorCode, setRejectionErrorCode] = useState<string | null>(null);
  const [selectedSubDiscipline, setSelectedSubDiscipline] = useState<string>("");

  const [headerNotes, setHeaderNotes] = useState("");
  useEffect(() => {
    if (report && "notes" in report && typeof (report as any).notes === "string") {
      setHeaderNotes((report as any).notes);
    }
  }, [report]);

  const [downloadingExcel, setDownloadingExcel] = useState(false);

  const handleExportExcel = async () => {
    if (!report?.id) return;
    setDownloadingExcel(true);
    try {
      const blob = await fetchSubReportExcel(businessId, unit, report.id);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      const fileLabel =
        unit === "buildings"
          ? "civil-subreport"
          : unit === "electrical"
            ? "electrical-subreport"
            : `${unit}-subreport`;
      a.download = `${fileLabel}-${report.report_date || report.id}.xlsx`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    } catch {
      setActionError("خطا در دانلود فایل اکسل ساب‌ریپورت");
    } finally {
      setDownloadingExcel(false);
    }
  };

  const handleSaveHeaderNotes = async () => {
    if (!report) return;
    setActionError(null);
    try {
      const actorId = requireStoredActorId();
      await queueUnitReportOperation({
        actorId,
        projectId: String(businessId),
        unit,
        reportDate: activeDate,
        localReportId: report.id,
        operationKind: "header_update",
        targetType: "header",
        payload: { notes: headerNotes },
      });
      void currentQuery.refetch();
    } catch (e) {
      setActionError(formatError(e));
    }
  };

  const getErrorCode = (err: unknown): string | null => {
    if (err instanceof ApiRequestError && err.code) {
      return err.code;
    }
    return null;
  };

  const formatError = (err: unknown): string => {
    if (err instanceof ApiRequestError) {
      if (err.code) {
        const key = `errors.${err.code}`;
        const translated = t(key);
        if (translated !== key) {
          return translated;
        }
      }
      return err.message;
    }
    if (err instanceof Error) {
      return err.message;
    }
    return String(err);
  };

  const formatDateTime = (iso: string | null | undefined): string => {
    if (!iso) return "—";
    const d = new Date(iso);
    if (Number.isNaN(d.getTime())) return iso;
    return d.toLocaleString(i18n.language.startsWith("fa") ? "fa-IR" : "en-US");
  };

  const handleCreateDraft = async () => {
    setActionError(null);
    setActionErrorCode(null);
    try {
      await openMutation.mutateAsync({
        reportDate: activeDate,
        subDiscipline: selectedSubDiscipline || undefined,
      });
    } catch (e) {
      setActionErrorCode(getErrorCode(e));
      setActionError(formatError(e));
    }
  };

  const handleSubmit = async () => {
    if (!report) return;
    setActionError(null);
    setActionErrorCode(null);
    try {
      await submitMutation.mutateAsync(report.id);
    } catch (e) {
      setActionErrorCode(getErrorCode(e));
      setActionError(formatError(e));
    }
  };

  const handleApprove = async () => {
    if (!report) return;
    setActionError(null);
    setActionErrorCode(null);
    try {
      await approveMutation.mutateAsync(report.id);
    } catch (e) {
      setActionErrorCode(getErrorCode(e));
      setActionError(formatError(e));
    }
  };

  const handleConfirmReject = async () => {
    if (!report) return;
    if (!rejectionReason.trim()) {
      setRejectionErrorCode("rejection_reason_required");
      setRejectionError(t("businessDepartment.unitReport.rejectReasonRequired"));
      return;
    }
    setRejectionError(null);
    setRejectionErrorCode(null);
    try {
      await rejectMutation.mutateAsync({
        reportId: report.id,
        reason: rejectionReason.trim(),
      });
      setRejectModalOpen(false);
      setRejectionReason("");
    } catch (e) {
      setRejectionErrorCode(getErrorCode(e));
      setRejectionError(formatError(e));
    }
  };

  const handleCorrect = async () => {
    if (!report) return;
    setActionError(null);
    setActionErrorCode(null);
    try {
      await correctMutation.mutateAsync(report.id);
    } catch (e) {
      setActionErrorCode(getErrorCode(e));
      setActionError(formatError(e));
    }
  };

  const handleDelete = async () => {
    if (!report) return;
    setActionError(null);
    setActionErrorCode(null);
    try {
      await deleteMutation.mutateAsync({ reportId: report.id, date: activeDate });
    } catch (e) {
      setActionErrorCode(getErrorCode(e));
      setActionError(formatError(e));
    }
  };

  return (
    <section
      id="container-unitDailyReportPanel"
      aria-labelledby="text-unitDailyReportTitle"
      className="space-y-4 rounded-xl border border-border bg-card p-4 sm:p-6"
    >
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <h2 id="text-unitDailyReportTitle" className="text-lg font-semibold tracking-tight">
            {t("businessDepartment.unitReport.title")}
          </h2>
          {report ? (
            <div className="flex items-center gap-2">
              <Badge
                id="badge-unitReportStatus"
                variant={statusToVariant(report.status)}
                label={t(statusToLabelKey(report.status))}
              />
              {report.sub_discipline ? (
                <Badge
                  id="badge-unitReportSubDiscipline"
                  data-testid="badge-unit-report-sub-discipline"
                  variant="neutral"
                  label={t(
                    `businessDepartment.unitReport.subDisciplines.${report.sub_discipline.toLowerCase()}`,
                    report.sub_discipline,
                  )}
                />
              ) : null}
              <span id="text-unitReportVersion" className="text-xs font-mono text-muted-foreground">
                {t("businessDepartment.unitReport.version")} {report.version_number}
              </span>
            </div>
          ) : null}
        </div>
        {currentQuery.isFetching ? (
          <span className="text-xs text-muted-foreground">{t("common.loading")}</span>
        ) : null}
      </div>

      <LocalDraftList
        businessId={businessId}
        unit={unit}
        activeDate={activeDate}
        onOpen={handleDateChange}
      />

      <div className="flex flex-wrap items-end gap-3">
        <div className="w-full sm:w-64">
          <JalaliDatePicker
            id="input-unitReportDate"
            name="unitReportDate"
            label={t("businessDepartment.unitReport.selectDate")}
            value={activeDate}
            onChange={handleDateChange}
          />
        </div>

        {report === null && !currentQuery.isLoading ? (
          <div className="flex flex-wrap items-center gap-2">
            <span id="text-noUnitReport" className="text-sm text-muted-foreground">
              {t("businessDepartment.unitReport.noReport")}
            </span>
            {SUB_DISCIPLINE_OPTIONS[unit] ? (
              <select
                id="select-unitReportSubDiscipline"
                data-testid="select-sub-discipline"
                value={selectedSubDiscipline}
                onChange={(e) => setSelectedSubDiscipline(e.target.value)}
                className="flex h-9 rounded-md border border-input bg-background px-3 py-1 text-xs shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
              >
                <option value="">
                  {t(
                    "businessDepartment.unitReport.selectSubDisciplineDefault",
                    "انتخاب زیررشته (اختیاری)",
                  )}
                </option>
                {SUB_DISCIPLINE_OPTIONS[unit]?.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {t(opt.labelKey, opt.value)}
                  </option>
                ))}
              </select>
            ) : null}
            <Button
              id="button-createUnitReportDraft"
              type="button"
              size="sm"
              disabled={openMutation.isPending || !activeDate}
              onClick={() => void handleCreateDraft()}
            >
              {openMutation.isPending
                ? t("common.loading")
                : t("businessDepartment.unitReport.createDraft")}
            </Button>
          </div>
        ) : null}
      </div>

      {actionError ? (
        <div
          id="alert-unitReportActionError"
          role="alert"
          data-error-code={actionErrorCode || undefined}
          className="rounded-md border border-destructive/40 bg-destructive/10 p-3 text-sm text-destructive"
        >
          <div className="flex items-center justify-between gap-2">
            <span>{actionError}</span>
            {actionErrorCode ? (
              <span className="font-mono text-xs opacity-75">
                ({actionErrorCode})
              </span>
            ) : null}
          </div>
        </div>
      ) : null}

      {report ? (
        <div className="space-y-4">
          <div className="space-y-2 rounded-lg border border-border/40 p-3 bg-muted/10">
            <TextArea
              id="input-unitReportGeneralNotes"
              data-testid="unit-report-general-notes"
              name="unitReportNotes"
              label={t("businessDepartment.unitReport.generalNotes", "یادداشت‌های عمومی واحد")}
              value={headerNotes}
              onChange={(e) => setHeaderNotes(e.target.value)}
              rows={2}
            />
            <div className="flex justify-end">
              <Button
                id="button-saveUnitReportNotes"
                data-testid="unit-report-save-btn"
                size="sm"
                type="button"
                onClick={() => void handleSaveHeaderNotes()}
              >
                {t("common.save", "ذخیره")}
              </Button>
            </div>
          </div>

          <dl
            id="dl-unitReportAudit"
            className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4 rounded-lg border border-border/60 bg-muted/20 p-4"
          >
            <div className="space-y-0.5">
              <dt className="text-xs text-muted-foreground">
                {t("businessDepartment.unitReport.preparer")}
              </dt>
              <dd id="text-unitReportPreparer" className="text-sm font-medium">
                {report.audit.prepared_by?.display_name || "—"}
              </dd>
            </div>
            <div className="space-y-0.5">
              <dt className="text-xs text-muted-foreground">
                {t("businessDepartment.unitReport.lastChange")}
              </dt>
              <dd id="text-unitReportLastChange" className="text-sm font-medium">
                {report.last_changed_at ? (
                  <time dateTime={report.last_changed_at}>
                    {formatDateTime(report.last_changed_at)}
                  </time>
                ) : (
                  "—"
                )}
              </dd>
            </div>
            <div className="space-y-0.5">
              <dt className="text-xs text-muted-foreground">
                {t("businessDepartment.unitReport.submitter")}
              </dt>
              <dd id="text-unitReportSubmitter" className="text-sm font-medium">
                {report.audit.submitted_by?.display_name || "—"}
                {report.audit.submitted_at ? (
                  <span className="block text-xs text-muted-foreground">
                    <time dateTime={report.audit.submitted_at}>
                      {formatDateTime(report.audit.submitted_at)}
                    </time>
                  </span>
                ) : null}
              </dd>
            </div>
            {report.status === "approved" ? (
              <div className="space-y-0.5">
                <dt className="text-xs text-muted-foreground">
                  {t("businessDepartment.unitReport.approver")}
                </dt>
                <dd id="text-unitReportApprover" className="text-sm font-medium">
                  {report.audit.approved_by?.display_name || "—"}
                  {report.audit.approved_at ? (
                    <span className="block text-xs text-muted-foreground">
                      <time dateTime={report.audit.approved_at}>
                        {formatDateTime(report.audit.approved_at)}
                      </time>
                    </span>
                  ) : null}
                </dd>
              </div>
            ) : null}
            {report.status === "rejected" ? (
              <div className="space-y-0.5">
                <dt className="text-xs text-muted-foreground">
                  {t("businessDepartment.unitReport.rejector")}
                </dt>
                <dd id="text-unitReportRejector" className="text-sm font-medium">
                  {report.audit.rejected_by?.display_name || "—"}
                  {report.audit.rejected_at ? (
                    <span className="block text-xs text-muted-foreground">
                      <time dateTime={report.audit.rejected_at}>
                        {formatDateTime(report.audit.rejected_at)}
                      </time>
                    </span>
                  ) : null}
                </dd>
              </div>
            ) : null}
          </dl>

          {report.status === "rejected" && report.audit.rejection_reason ? (
            <div
              id="container-unitReportRejectionReason"
              className="rounded-lg border border-destructive/30 bg-destructive/10 p-3 space-y-1"
            >
              <div className="text-xs font-semibold text-destructive">
                {t("businessDepartment.unitReport.rejectionReason")}
              </div>
              <p
                id="text-unitReportRejectionReason"
                dir="auto"
                className="text-sm text-foreground whitespace-pre-wrap"
              >
                {report.audit.rejection_reason}
              </p>
            </div>
          ) : null}

          {!report.capabilities.can_edit &&
          report.status !== "draft" &&
          report.status !== "rejected" ? (
            <p id="text-unitReportReadonlyNotice" className="text-xs text-muted-foreground">
              {t("businessDepartment.unitReport.readonlyState")}
            </p>
          ) : null}

          <div id="container-unitReportActions" className="flex flex-wrap items-center gap-2">
            {report.capabilities.can_submit ? (
              <Button
                id="button-submitUnitReport"
                type="button"
                size="sm"
                disabled={submitMutation.isPending}
                onClick={() => void handleSubmit()}
              >
                {submitMutation.isPending
                  ? t("common.loading")
                  : t("businessDepartment.unitReport.actionSubmit")}
              </Button>
            ) : null}

            {report.capabilities.can_approve ? (
              <Button
                id="button-approveUnitReport"
                type="button"
                size="sm"
                variant="default"
                disabled={approveMutation.isPending}
                onClick={() => void handleApprove()}
              >
                {approveMutation.isPending
                  ? t("common.loading")
                  : t("businessDepartment.unitReport.actionApprove")}
              </Button>
            ) : null}

            {report.capabilities.can_reject ? (
              <Button
                id="button-openRejectUnitReportModal"
                type="button"
                size="sm"
                variant="outline"
                onClick={() => {
                  setRejectionReason("");
                  setRejectionError(null);
                  setRejectionErrorCode(null);
                  setRejectModalOpen(true);
                }}
              >
                {t("businessDepartment.unitReport.actionReject")}
              </Button>
            ) : null}

            {report.capabilities.can_correct ? (
              <Button
                id="button-correctUnitReport"
                type="button"
                size="sm"
                variant="outline"
                disabled={correctMutation.isPending}
                onClick={() => void handleCorrect()}
              >
                {correctMutation.isPending
                  ? t("common.loading")
                  : t("businessDepartment.unitReport.actionCorrect")}
              </Button>
            ) : null}

            {report.capabilities.can_delete ? (
              <Button
                id="button-deleteUnitReport"
                type="button"
                size="sm"
                variant="destructive"
                disabled={deleteMutation.isPending}
                onClick={() => void handleDelete()}
              >
                {deleteMutation.isPending
                  ? t("common.loading")
                  : t("businessDepartment.unitReport.actionDelete")}
              </Button>
            ) : null}

            {report.capabilities.can_view_history ? (
              <Button
                id="button-viewUnitReportHistory"
                type="button"
                size="sm"
                variant="ghost"
                onClick={() => setHistoryModalOpen(true)}
              >
                {t("businessDepartment.unitReport.actionHistory")}
              </Button>
            ) : null}

            <Button
              id="button-exportUnitReportExcel"
              type="button"
              size="sm"
              variant="outline"
              disabled={downloadingExcel}
              onClick={() => void handleExportExcel()}
            >
              <Download className="size-4 ml-1" />
              {unit === "buildings"
                ? "خروجی اکسل ابنیه (FILE 5)"
                : unit === "electrical"
                  ? "خروجی اکسل برق (FILE 6)"
                  : "خروجی اکسل ساب‌ریپورت"}
            </Button>
          </div>

          {unitSupportsActivitiesSection(unit) ||
          unitSupportsLaborSection(unit) ||
          unitSupportsMachinerySection(unit) ||
          unitSupportsMaterialsSection(unit) ? (
            <Tabs
              defaultValue={
                unitSupportsActivitiesSection(unit)
                  ? "activities"
                  : unitSupportsLaborSection(unit)
                    ? "labor"
                    : unitSupportsMachinerySection(unit)
                      ? "machinery"
                      : "materials"
              }
              dir={i18n.dir()}
              className="w-full pt-2"
              data-testid="unit-report-sections-tabs"
            >
              <TabsList
                id="tablist-unitReportSections"
                className="flex h-auto flex-wrap justify-start gap-1"
              >
                {unitSupportsActivitiesSection(unit) ? (
                  <TabsTrigger
                    id="tab-unitReportSection-activities"
                    data-testid="unit-section-tab-activities"
                    value="activities"
                  >
                    {t("businessDepartment.unitReport.sections.activities.tab")}
                  </TabsTrigger>
                ) : null}
                {unitSupportsLaborSection(unit) ? (
                  <TabsTrigger
                    id="tab-unitReportSection-labor"
                    data-testid="unit-section-tab-labor"
                    value="labor"
                  >
                    {t("businessDepartment.unitReport.sections.labor.tab")}
                  </TabsTrigger>
                ) : null}
                {unitSupportsMachinerySection(unit) ? (
                  <TabsTrigger
                    id="tab-unitReportSection-machinery"
                    data-testid="unit-section-tab-machinery"
                    value="machinery"
                  >
                    {t("businessDepartment.unitReport.sections.machinery.tab")}
                  </TabsTrigger>
                ) : null}
                {unitSupportsMaterialsSection(unit) ? (
                  <TabsTrigger
                    id="tab-unitReportSection-materials"
                    data-testid="unit-section-tab-materials"
                    value="materials"
                  >
                    {t("businessDepartment.unitReport.sections.materials.tab")}
                  </TabsTrigger>
                ) : null}
                {unitSupportsConcreteSection(unit) ? (
                  <TabsTrigger id="tab-unitReportSection-concrete" value="concrete">
                    {t("businessDepartment.unitReport.sections.concrete.tab")}
                  </TabsTrigger>
                ) : null}
                {unitSupportsGeneralSection(unit) ? (
                  <TabsTrigger id="tab-unitReportSection-general" value="general">
                    {t("businessDepartment.unitReport.sections.general.tab")}
                  </TabsTrigger>
                ) : null}
                {unitSupportsIssuesSection(unit) ? (
                  <TabsTrigger id="tab-unitReportSection-issues" value="issues">
                    {t("businessDepartment.unitReport.sections.issues.tab")}
                  </TabsTrigger>
                ) : null}
                {unitSupportsVisitsSection(unit) ? (
                  <TabsTrigger id="tab-unitReportSection-visits" value="visits">
                    {t("businessDepartment.unitReport.sections.visits.tab")}
                  </TabsTrigger>
                ) : null}
                {unitSupportsHseSection(unit) ? (
                  <TabsTrigger id="tab-unitReportSection-hse" value="hse">
                    {t("businessDepartment.unitReport.sections.hse.tab")}
                  </TabsTrigger>
                ) : null}
              </TabsList>
              {unitSupportsActivitiesSection(unit) ? (
                <TabsContent value="activities" data-testid="unit-section-activities" className="mt-3">
                  <SectionActivities
                    businessId={businessId}
                    unit={unit}
                    report={report}
                  />
                </TabsContent>
              ) : null}
              {unitSupportsLaborSection(unit) ? (
                <TabsContent value="labor" data-testid="unit-section-labor" className="mt-3">
                  <SectionLabor
                    businessId={businessId}
                    unit={unit}
                    report={report}
                  />
                </TabsContent>
              ) : null}
              {unitSupportsMachinerySection(unit) ? (
                <TabsContent value="machinery" data-testid="unit-section-machinery" className="mt-3">
                  <SectionMachinery
                    businessId={businessId}
                    unit={unit}
                    report={report}
                  />
                </TabsContent>
              ) : null}
              {unitSupportsMaterialsSection(unit) ? (
                <TabsContent value="materials" data-testid="unit-section-materials" className="mt-3">
                  <SectionMaterials
                    businessId={businessId}
                    unit={unit}
                    report={report}
                  />
                </TabsContent>
              ) : null}
              {unitSupportsConcreteSection(unit) ? (
                <TabsContent value="concrete" data-testid="unit-section-concrete" className="mt-3">
                  <SectionConcrete businessId={businessId} unit={unit} report={report} />
                </TabsContent>
              ) : null}
              {unitSupportsGeneralSection(unit) ? (
                <TabsContent value="general" data-testid="unit-section-general" className="mt-3">
                  <SectionGeneral businessId={businessId} unit={unit} report={report} />
                </TabsContent>
              ) : null}
              {unitSupportsIssuesSection(unit) ? (
                <TabsContent value="issues" data-testid="unit-section-issues" className="mt-3">
                  <SectionIssues businessId={businessId} unit={unit} report={report} />
                </TabsContent>
              ) : null}
              {unitSupportsVisitsSection(unit) ? (
                <TabsContent value="visits" data-testid="unit-section-visits" className="mt-3">
                  <SectionVisits businessId={businessId} unit={unit} report={report} />
                </TabsContent>
              ) : null}
              {unitSupportsHseSection(unit) ? (
                <TabsContent value="hse" data-testid="unit-section-hse" className="mt-3">
                  <SectionHse businessId={businessId} unit={unit} report={report} />
                </TabsContent>
              ) : null}
            </Tabs>
          ) : null}
        </div>
      ) : null}

      <Modal
        open={rejectModalOpen}
        onOpenChange={setRejectModalOpen}
        title={t("businessDepartment.unitReport.rejectionModalTitle")}
        idBase="rejectUnitReport"
      >
        <div className="p-4 space-y-4">
          <div className="space-y-1">
            <label htmlFor="input-rejectReason" className="text-sm font-medium">
              {t("businessDepartment.unitReport.rejectionReason")}{" "}
              <span className="text-destructive">*</span>
            </label>
            <TextArea
              id="input-rejectReason"
              name="rejectionReason"
              dir="auto"
              rows={4}
              value={rejectionReason}
              onChange={(e) => {
                setRejectionReason(e.target.value);
                setRejectionError(null);
                setRejectionErrorCode(null);
              }}
              placeholder={t("businessDepartment.unitReport.rejectionReasonPlaceholder")}
            />
            {rejectionError ? (
              <p
                id="alert-unitReportRejectionError"
                className="text-xs text-destructive"
                role="alert"
                data-error-code={rejectionErrorCode || undefined}
              >
                {rejectionError}
                {rejectionErrorCode ? (
                  <span className="font-mono text-[11px] opacity-75 ms-1">
                    ({rejectionErrorCode})
                  </span>
                ) : null}
              </p>
            ) : null}
          </div>
          <div className="flex justify-end gap-2">
            <Button
              id="button-cancelRejectUnitReport"
              variant="ghost"
              type="button"
              onClick={() => setRejectModalOpen(false)}
            >
              {t("common.cancel")}
            </Button>
            <Button
              id="button-confirmRejectUnitReport"
              variant="destructive"
              type="button"
              disabled={rejectMutation.isPending}
              onClick={() => void handleConfirmReject()}
            >
              {rejectMutation.isPending
                ? t("common.loading")
                : t("businessDepartment.unitReport.actionReject")}
            </Button>
          </div>
        </div>
      </Modal>

      <Modal
        open={historyModalOpen}
        onOpenChange={setHistoryModalOpen}
        title={t("businessDepartment.unitReport.historyTitle")}
        idBase="unitReportHistory"
      >
        <div className="p-4 space-y-5 max-h-[70vh] overflow-y-auto">
          {historyQuery.isLoading ? (
            <p className="text-sm text-muted-foreground">{t("common.loading")}</p>
          ) : historyQuery.error ? (
            <p className="text-sm text-destructive">{formatError(historyQuery.error)}</p>
          ) : (
            <>
              <section className="space-y-2">
                <h4 className="text-sm font-semibold">
                  {t("businessDepartment.unitReport.version")}
                </h4>
                <div className="overflow-x-auto rounded-md border border-border">
                  <table className="w-full text-start text-xs">
                    <caption className="sr-only">
                      {t("businessDepartment.unitReport.historyTitle")}
                    </caption>
                    <thead>
                      <tr className="border-b bg-muted/40 text-muted-foreground">
                        <th className="p-2 text-start">
                          {t("businessDepartment.unitReport.version")}
                        </th>
                        <th className="p-2 text-start">{t("common.status")}</th>
                        <th className="p-2 text-start">
                          {t("businessDepartment.unitReport.lastChange")}
                        </th>
                        <th className="p-2 text-start">
                          {t("businessDepartment.unitReport.preparer")}
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {historyQuery.data?.versions?.map((ver) => (
                        <tr key={ver.id} className="border-b last:border-b-0">
                          <td className="p-2 font-mono">v{ver.version_number}</td>
                          <td className="p-2">
                            <Badge
                              variant={statusToVariant(ver.status)}
                              label={t(statusToLabelKey(ver.status))}
                            />
                          </td>
                          <td className="p-2">
                            <time dateTime={ver.created_at}>
                              {formatDateTime(ver.created_at)}
                            </time>
                          </td>
                          <td className="p-2">
                            {ver.is_current ? (
                              <span className="font-semibold text-primary">
                                {t("status.active")}
                              </span>
                            ) : (
                              <span className="text-muted-foreground">—</span>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </section>

              <section className="space-y-2">
                <h4 className="text-sm font-semibold">
                  {t("businessDepartment.unitReport.events")}
                </h4>
                <div className="overflow-x-auto rounded-md border border-border">
                  <table className="w-full text-start text-xs">
                    <caption className="sr-only">
                      {t("businessDepartment.unitReport.events")}
                    </caption>
                    <thead>
                      <tr className="border-b bg-muted/40 text-muted-foreground">
                        <th className="p-2 text-start">
                          {t("businessDepartment.unitReport.event")}
                        </th>
                        <th className="p-2 text-start">
                          {t("businessDepartment.unitReport.actor")}
                        </th>
                        <th className="p-2 text-start">
                          {t("businessDepartment.unitReport.time")}
                        </th>
                        <th className="p-2 text-start">
                          {t("businessDepartment.unitReport.reason")}
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {historyQuery.data?.events?.map((ev, idx) => (
                        <tr key={idx} className="border-b last:border-b-0">
                          <td className="p-2 font-mono">
                            {ev.event_type} ({ev.from_status} → {ev.to_status})
                          </td>
                          <td className="p-2">{ev.actor?.display_name || "—"}</td>
                          <td className="p-2">
                            <time dateTime={ev.occurred_at}>
                              {formatDateTime(ev.occurred_at)}
                            </time>
                          </td>
                          <td className="p-2" dir="auto">
                            {ev.reason || "—"}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </section>

              {report?.capabilities?.can_correct ? (
                <div className="flex justify-end pt-2 border-t border-border">
                  <Button
                    id="button-correctUnitReportModal"
                    type="button"
                    size="sm"
                    variant="outline"
                    disabled={correctMutation.isPending}
                    onClick={async () => {
                      await handleCorrect();
                      setHistoryModalOpen(false);
                    }}
                  >
                    {correctMutation.isPending
                      ? t("common.loading")
                      : t("businessDepartment.unitReport.actionCorrect")}
                  </Button>
                </div>
              ) : null}
            </>
          )}
        </div>
      </Modal>
    </section>
  );
}

function LocalDraftList({
  businessId,
  unit,
  activeDate,
  onOpen,
}: {
  businessId: string;
  unit: CanonicalUnit;
  activeDate: string;
  onOpen: (date: string) => void;
}) {
  const { t } = useTranslation();
  const [drafts, setDrafts] = useState<LocalReportSnapshot[]>([]);

  useEffect(() => {
    let cancelled = false;
    const actorId = getStoredActorId() ?? "";
    void getLocalSnapshotsByProject(businessId, actorId || undefined)
      .then((rows) => {
        if (cancelled) return;
        setDrafts(rows.filter((row) => row.unit === unit));
      })
      .catch(() => {
        if (!cancelled) setDrafts([]);
      });
    return () => {
      cancelled = true;
    };
  }, [businessId, unit, activeDate]);

  if (drafts.length === 0) return null;

  return (
    <nav aria-label={t("offline.localDrafts", "Local drafts")} data-testid="local-draft-list">
      <ul className="flex flex-wrap gap-2">
        {drafts.map((draft) => (
          <li key={draft.local_report_id}>
            <button
              type="button"
              data-testid={`local-draft-${draft.report_date}`}
              className="rounded-md border px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
              aria-current={draft.report_date === activeDate ? "date" : undefined}
              onClick={() => onOpen(draft.report_date)}
            >
              {draft.report_date}
            </button>
          </li>
        ))}
      </ul>
    </nav>
  );
}
