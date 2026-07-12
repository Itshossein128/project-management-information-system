import { useMutation } from "@tanstack/react-query";
import { FileUp, Upload } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router";
import {
  fetchMspImportStatus,
  fetchP6ImportStatus,
  isP6File,
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
  } | null>(null);
  const [importError, setImportError] = useState<string | null>(null);

  const reset = useCallback(() => {
    setStep(1);
    setFile(null);
    setPreview(null);
    setReplace(false);
    setTaskId(null);
    setProgress(0);
    setSummary(null);
    setImportError(null);
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
      setTaskId(data.task_id);
      setStep(3);
    },
    onError: (e: Error) => toast.error(e.message),
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
          });
          onComplete?.();
          return;
        }
        if (status.status === "failed") {
          setImportError(status.error ?? "Import failed");
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
    const lower = f.name.toLowerCase();
    if (!lower.endsWith(".xml") && !lower.endsWith(".xer")) {
      toast.error("فقط فایل‌های XML (MSP) یا XER (P6) پذیرفته می‌شوند");
      return;
    }
    setFile(f);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const dropped = e.dataTransfer.files[0];
    onFileSelect(dropped ?? null);
  };

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
            {s === 1 ? "بارگذاری" : s === 2 ? "پیش‌نمایش" : "پیشرفت"}
          </span>
        ))}
      </div>

      {step === 1 && (
        <div className="space-y-4">
          <div className="rounded-md border border-amber-200 bg-amber-50 p-3 text-sm text-amber-900 dark:border-amber-900/50 dark:bg-amber-950/30 dark:text-amber-200">
            Microsoft Project: File → Save As → XML (.xml). Primavera P6: Export → XER (.xer).
            فایل‌های باینری .mpp پشتیبانی نمی‌شوند.
          </div>

          <div
            className="flex flex-col items-center justify-center gap-3 rounded-lg border-2 border-dashed border-border p-8"
            onDragOver={(e) => e.preventDefault()}
            onDrop={handleDrop}
          >
            <Upload className="size-10 text-muted-foreground" />
            <p className="text-sm text-muted-foreground">فایل XML را اینجا رها کنید یا انتخاب کنید</p>
            <label className="cursor-pointer">
              <input
                type="file"
                accept=".xml,.xer,application/xml,text/xml"
                className="sr-only"
                onChange={(e) => onFileSelect(e.target.files?.[0] ?? null)}
              />
              <span className="inline-flex items-center gap-2 rounded-md border border-border bg-muted px-3 py-2 text-sm hover:bg-muted/80">
                <FileUp className="size-4" />
                انتخاب فایل
              </span>
            </label>
            {file ? (
              <p className="text-sm">
                {file.name} — {(file.size / 1024).toFixed(1)} KB
              </p>
            ) : null}
          </div>

          <div className="flex justify-end gap-2">
            <Button variant="ghost" onClick={() => onOpenChange(false)}>
              انصراف
            </Button>
            <Button
              variant="primary"
              disabled={!file}
              loading={previewMutation.isPending}
              onClick={() => file && previewMutation.mutate(file)}
            >
              پیش‌نمایش
            </Button>
          </div>
        </div>
      )}

      {step === 2 && preview && (
        <div className="space-y-4">
          {preview.warnings.length > 0 && (
            <div className="rounded-md border border-amber-200 bg-amber-50 p-3 text-sm text-amber-900 dark:border-amber-900/50 dark:bg-amber-950/30 dark:text-amber-200">
              <p className="font-medium">هشدارها</p>
              <ul className="mt-1 list-inside list-disc">
                {preview.warnings.map((w) => (
                  <li key={w}>{w}</li>
                ))}
              </ul>
            </div>
          )}

          <TemplateWBSPreviewTree nodes={preview.wbs_tree} />

          <div className="space-y-2">
            <p className="text-sm font-medium">نحوه وارد کردن</p>
            <label className="flex cursor-pointer items-center gap-2 text-sm">
              <input
                type="radio"
                name="mspMode"
                checked={replace}
                onChange={() => setReplace(true)}
              />
              جایگزینی کامل — حذف WBS و فعالیت‌های موجود
            </label>
            <label className="flex cursor-pointer items-center gap-2 text-sm">
              <input
                type="radio"
                name="mspMode"
                checked={!replace}
                onChange={() => setReplace(false)}
              />
              افزودن به ساختار موجود — رد کردن کدهای تکراری
            </label>
          </div>

          <div className="flex justify-between gap-2">
            <Button variant="ghost" onClick={() => setStep(1)}>
              قبلی
            </Button>
            <Button
              variant="primary"
              loading={importMutation.isPending}
              disabled={!file}
              onClick={() => file && importMutation.mutate({ file, replace })}
            >
              وارد کردن
            </Button>
          </div>
        </div>
      )}

      {step === 3 && (
        <div className="space-y-4">
          {importError ? (
            <p className="text-destructive text-sm">{importError}</p>
          ) : summary ? (
            <div className="space-y-2 text-sm">
              <p>وارد کردن با موفقیت انجام شد.</p>
              <ul className="list-inside list-disc text-muted-foreground">
                <li>{summary.wbs_nodes_created} گره WBS</li>
                <li>{summary.activities_created} فعالیت</li>
                {summary.warnings.length > 0 ? (
                  <li>{summary.warnings.length} هشدار</li>
                ) : null}
              </ul>
            </div>
          ) : (
            <div className="space-y-2">
              <p className="text-sm text-muted-foreground">در حال وارد کردن...</p>
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
                  مشاهده WBS
                </Button>
              </Link>
            ) : (
              <Button variant="ghost" onClick={() => onOpenChange(false)}>
                بستن
              </Button>
            )}
          </div>
        </div>
      )}
    </Modal>
  );
}
