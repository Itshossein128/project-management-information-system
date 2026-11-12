import { useMutation } from "@tanstack/react-query";
import { FileUp, Upload } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { Link } from "react-router";
import {
  fetchMspImportStatus,
  fetchP6ImportStatus,
  isP6File,
  isScheduleImportFile,
  previewMspImport,
  previewP6Import,
  startMspImport,
  startP6Import,
  type MspPreviewResult,
} from "@/app/lib/api/msp";
import { PATHS } from "@/app/routeVars";
import { TemplateWBSPreviewTree } from "@/components/templates/template-wbs-preview-tree";
import { Modal } from "@/components/overlay/modal";
import { Button } from "@/components/ui/sprint-button";
import { useToast } from "@/components/ui/toast";

interface MspImportWizardProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  projectId: string;
  onComplete?: () => void;
}

type Step = 1 | 2 | 3;

export function MspImportWizard({
  open,
  onOpenChange,
  projectId,
  onComplete,
}: MspImportWizardProps) {
  const { t } = useTranslation();
  const toast = useToast();
  const [step, setStep] = useState<Step>(1);
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<MspPreviewResult | null>(null);
  const [replace, setReplace] = useState(false);
  const [taskId, setTaskId] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);
  const [summary, setSummary] = useState<{
    wbs_nodes_created: number;
    activities_created: number;
    warnings: string[];
    warning_items?: { code: string; row: string }[];
    nothing_changed?: boolean;
  } | null>(null);
  const [importError, setImportError] = useState<string | null>(null);
  const [failureItems, setFailureItems] = useState<{ code: string; row: string }[]>([]);

  const reset = useCallback(() => {
    setStep(1);
    setFile(null);
    setPreview(null);
    setReplace(false);
    setTaskId(null);
    setProgress(0);
    setSummary(null);
    setImportError(null);
    setFailureItems([]);
  }, []);

  useEffect(() => {
    if (!open) reset();
  }, [open, reset]);

  const previewMutation = useMutation({
    mutationFn: (f: File) =>
      isP6File(f) ? previewP6Import(projectId, f) : previewMspImport(projectId, f),
    onSuccess: (data) => {
      setPreview(data);
      setStep(2);
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const importMutation = useMutation({
    mutationFn: (opts: { file: File; replace: boolean }) =>
      isP6File(opts.file)
        ? startP6Import(projectId, opts.file, opts.replace)
        : startMspImport(projectId, opts.file, opts.replace),
    onSuccess: (data) => {
      setImportError(null);
      setTaskId(data.task_id);
      setStep(3);
    },
    onError: (e: Error) => {
      const message = e.message || t("scheduleImport.refused", "واردسازی رد شد.");
      setImportError(message);
      toast.error(message);
    },
  });

  useEffect(() => {
    if (step !== 3 || !taskId) return;
    let cancelled = false;

    const poll = async () => {
      try {
        const status = file && isP6File(file)
          ? await fetchP6ImportStatus(projectId, taskId)
          : await fetchMspImportStatus(projectId, taskId);
        if (cancelled) return;
        setProgress(status.progress_pct);
        if (status.status === "done" && status.result) {
          setSummary({
            wbs_nodes_created: status.result.wbs_nodes_created,
            activities_created: status.result.activities_created,
            warnings: status.result.warnings,
            warning_items: status.result.warning_items,
            nothing_changed: Boolean(status.result.nothing_changed),
          });
          onComplete?.();
          return;
        }
        if (status.status === "failed") {
          const blocking = status.blocking ?? [];
          if (blocking.length > 0) {
            setFailureItems(blocking);
          } else if (status.error_code) {
            setFailureItems([{ code: status.error_code, row: "" }]);
          } else {
            setImportError(status.error ?? t("scheduleImport.refused"));
          }
          return;
        }
        setTimeout(poll, 2000);
      } catch (e) {
        if (!cancelled) {
          setImportError(e instanceof Error ? e.message : "خطا در دریافت وضعیت");
        }
      }
    };

    void poll();
    return () => {
      cancelled = true;
    };
  }, [step, taskId, projectId, onComplete, file]);

  const onFileSelect = (f: File | null) => {
    if (!f) return;
    if (!isScheduleImportFile(f)) {
      toast.error("فقط فایل‌های Microsoft Project (.mpp یا .xml) یا Primavera P6 (.xer) پذیرفته می‌شوند");
      return;
    }
    setFile(f);
    setPreview(null);
    setImportError(null);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const dropped = e.dataTransfer.files[0];
    onFileSelect(dropped ?? null);
  };

  const isProcessing = previewMutation.isPending || importMutation.isPending;
  const showPreviewProcessing = previewMutation.isPending && step === 1;

  return (
    <Modal
      open={open}
      onOpenChange={onOpenChange}
      title="بارگذاری برنامه زمان‌بندی (MSP / P6)"
      idBase="mspImport"
      className="max-w-2xl"
    >
      <div className="mb-4 flex gap-2 text-sm">
        {([1, 2, 3] as const).map((s) => (
          <span
            key={s}
            className={`rounded px-2 py-1 ${step === s ? "bg-primary/10 font-medium" : "text-muted-foreground"}`}
          >
            {s === 1
              ? t("scheduleImport.stepUpload", "Upload")
              : s === 2
                ? t("scheduleImport.stepPreview", "Preview")
                : t("scheduleImport.stepProgress", "Progress")}
          </span>
        ))}
      </div>

      {step === 1 && (
        <div className="space-y-4">
          <div className="rounded-md border border-border bg-muted/40 p-3 text-sm text-muted-foreground">
            {t("scheduleImport.acceptedFormats", "Accepted formats: Microsoft Project (.mpp and .xml) and Primavera P6 (.xer).")}
          </div>

          <div
            className="flex flex-col items-center justify-center gap-3 rounded-lg border-2 border-dashed border-border p-8"
            onDragOver={(e) => e.preventDefault()}
            onDrop={handleDrop}
          >
            <Upload className="size-10 text-muted-foreground" />
            <p className="text-sm text-muted-foreground">
              {t("scheduleImport.dropFile", "Drop a .mpp, .xml, or .xer file here, or choose one")}
            </p>
            <label className="cursor-pointer">
              <input
                type="file"
                accept=".mpp,.xml,.xer,application/xml,text/xml,application/vnd.ms-project"
                className="peer sr-only"
                disabled={isProcessing}
                onChange={(e) => onFileSelect(e.target.files?.[0] ?? null)}
              />
              <span className="inline-flex items-center gap-2 rounded-md border border-border bg-muted px-3 py-2 text-sm hover:bg-muted/80 peer-focus-visible:outline-none peer-focus-visible:ring-2 peer-focus-visible:ring-ring peer-focus-visible:ring-offset-2">
                <FileUp className="size-4" />
                {t("scheduleImport.chooseFile", "Choose file")}
              </span>
            </label>
            {file ? (
              <p className="text-sm" data-testid="msp-import-filename">
                {file.name} — {(file.size / 1024).toFixed(1)} KB
              </p>
            ) : null}
          </div>

          {showPreviewProcessing ? (
            <div
              className="rounded-md border border-border bg-muted/30 p-3 text-sm text-muted-foreground"
              data-testid="msp-import-processing"
              role="status"
              aria-live="polite"
            >
              {t("scheduleImport.preparing", "Preparing preview…")}
            </div>
          ) : null}

          <div className="flex justify-end gap-2">
            <Button variant="ghost" onClick={() => onOpenChange(false)} disabled={isProcessing}>
              {t("scheduleImport.cancel", "Cancel")}
            </Button>
            <Button
              variant="primary"
              disabled={!file || isProcessing}
              loading={previewMutation.isPending}
              onClick={() => file && previewMutation.mutate(file)}
            >
              {t("scheduleImport.preview", "Preview")}
            </Button>
          </div>
        </div>
      )}

      {step === 2 && preview && (
        <div className="space-y-4">
          {(preview.blocking?.length ?? 0) > 0 && (
            <div className="rounded-md border border-destructive/40 bg-destructive/10 p-3 text-sm text-destructive" data-testid="msp-import-blocking">
              <ul className="list-inside list-disc">
                {preview.blocking?.map((item) => (
                  <li key={`${item.code}-${item.row}`}>
                    {t(`scheduleImport.codes.${item.code}`, item.code)}
                    {item.row ? ` (${item.row})` : ""}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {(preview.warning_items?.length ?? preview.warnings.length) > 0 && (
            <div
              className="rounded-md border border-warning-200 bg-warning-50 p-3 text-sm text-warning-900 dark:border-warning-900/50 dark:bg-warning-950/30 dark:text-warning-200"
              data-testid="msp-import-warnings"
            >
              <p className="font-medium">{t("scheduleImport.warnings", "Warnings")}</p>
              <ul className="mt-1 list-inside list-disc">
                {(preview.warning_items ?? []).map((item) => (
                  <li key={`${item.code}-${item.row}`}>
                    {t(`scheduleImport.codes.${item.code}`, item.code)}
                    {item.row ? ` (${item.row})` : ""}
                  </li>
                ))}
                {preview.warning_items ? null : preview.warnings.map((w) => (
                  <li key={w}>{w}</li>
                ))}
              </ul>
            </div>
          )}

          {file ? (
            <p className="text-xs text-muted-foreground" data-testid="msp-import-filename">
              {file.name}
            </p>
          ) : null}

          <TemplateWBSPreviewTree nodes={preview.wbs_tree} />

          <div className="space-y-2">
            <p className="text-sm font-medium">{t("scheduleImport.importMode", "How to import")}</p>
            <label className="flex cursor-pointer items-center gap-2 text-sm">
              <input
                type="radio"
                name="mspMode"
                checked={replace}
                onChange={() => setReplace(true)}
              />
              {t("scheduleImport.replace", "Replace the current schedule")}
            </label>
            <label className="flex cursor-pointer items-center gap-2 text-sm">
              <input
                type="radio"
                name="mspMode"
                checked={!replace}
                onChange={() => setReplace(false)}
              />
              {t("scheduleImport.append", "Add to the current schedule and skip duplicate codes")}
            </label>
          </div>

          {importError ? (
            <p className="text-destructive text-sm" data-testid="msp-import-refusal">
              {importError}
            </p>
          ) : null}

          <div className="flex justify-between gap-2">
            <Button variant="ghost" onClick={() => setStep(1)} disabled={isProcessing}>
              {t("scheduleImport.back", "Back")}
            </Button>
            <Button
              variant="primary"
              loading={importMutation.isPending}
              disabled={!file || isProcessing || (preview.blocking?.length ?? 0) > 0}
              onClick={() => file && importMutation.mutate({ file, replace })}
            >
              {t("scheduleImport.confirm", "Import")}
            </Button>
          </div>
        </div>
      )}

      {step === 3 && (
        <div className="space-y-4">
          {failureItems.length > 0 || importError ? (
            <div className="space-y-3" data-testid="msp-import-fatal-error">
              {failureItems.length > 0 ? (
                <ul className="list-inside list-disc text-sm text-destructive">
                  {failureItems.map((item) => (
                    <li key={`${item.code}-${item.row}`}>
                      {t(`scheduleImport.codes.${item.code}`, item.code)}
                      {item.row ? ` (${item.row})` : ""}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-destructive text-sm">{importError}</p>
              )}
              <div className="flex flex-wrap gap-2">
                <Button
                  variant="ghost"
                  onClick={() => {
                    setImportError(null);
                    setTaskId(null);
                    setProgress(0);
                    setSummary(null);
                    setStep(1);
                  }}
                >
                  {t("scheduleImport.chooseAnother", "Choose another file")}
                </Button>
                <Button variant="ghost" onClick={() => onOpenChange(false)}>
                  {t("scheduleImport.close", "Close")}
                </Button>
              </div>
            </div>
          ) : summary ? (
            <div className="space-y-2 text-sm">
              <p>
                {summary.nothing_changed
                  ? t("scheduleImport.nothingChanged", "برنامه تغییری نکرد.")
                  : t("scheduleImport.imported", "وارد کردن با موفقیت انجام شد.")}
              </p>
              <ul className="list-inside list-disc text-muted-foreground">
                <li>
                  {t("scheduleImport.wbsNodes", "{{count}} work packages", {
                    count: summary.wbs_nodes_created,
                  })}
                </li>
                <li>
                  {t("scheduleImport.activities", "{{count}} activities", {
                    count: summary.activities_created,
                  })}
                </li>
                {(summary.warning_items ?? []).map((item) => (
                  <li key={`${item.code}-${item.row}`}>
                    {t(`scheduleImport.codes.${item.code}`, item.code)}
                    {item.row ? ` (${item.row})` : ""}
                  </li>
                ))}
              </ul>
            </div>
          ) : (
            <div className="space-y-2">
              <p className="text-sm text-muted-foreground">{t("scheduleImport.importing", "Importing…")}</p>
              <div className="h-2 overflow-hidden rounded-full bg-muted">
                <div
                  className="h-full bg-primary transition-all"
                  style={{ width: `${progress}%` }}
                />
              </div>
              <p className="text-xs text-muted-foreground">{progress}%</p>
            </div>
          )}

          <div className="flex justify-end gap-2">
            {summary ? (
              <Link to={`/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_WBS}`}>
                <Button variant="primary" onClick={() => onOpenChange(false)}>
                  {t("scheduleImport.viewWbs", "View work breakdown")}
                </Button>
              </Link>
            ) : !importError ? (
              <Button variant="ghost" onClick={() => onOpenChange(false)}>
                {t("scheduleImport.close", "Close")}
              </Button>
            ) : null}
          </div>
        </div>
      )}
    </Modal>
  );
}
