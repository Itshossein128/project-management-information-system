import { useMutation } from "@tanstack/react-query";
import { FileUp, Upload } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { Link } from "react-router";
import { useAuth } from "@/app/contexts/auth-context";
import { ApiRequestError } from "@/app/lib/api-client";
import {
  readImportAttempt,
  saveImportAttempt,
  clearImportAttempt,
  type ImportAttemptSession,
} from "@/app/lib/import-attempt-session";
import {
  fetchMspImportStatus,
  fetchP6ImportStatus,
  isP6File,
  isScheduleImportFile,
  previewMspImport,
  previewP6Import,
  startMspImport,
  startP6Import,
  type ImportCounts,
  type MspImportStatusResult,
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

type PreviewRequest = {
  file: File;
  projectId: string;
  userId: string;
  generation: number;
};
type StartRequest = PreviewRequest & { replace: boolean; recognizedKind: string };

interface ImportSummary {
  wbs_nodes_created: number;
  activities_created: number;
  relations_created: number;
  relationships_kept?: number;
  rows_read?: number;
  duplicate_count?: number;
  rows_omitted?: number;
  wbs_nodes_removed?: number;
  activities_removed?: number;
  relations_removed?: number;
  warning_items?: { code: string; row: string }[];
  nothing_changed?: boolean;
}

function fileIdentity(file: File) {
  return `${file.name}:${file.size}:${file.lastModified}`;
}

export function MspImportWizard({
  open,
  onOpenChange,
  projectId,
  onComplete,
}: MspImportWizardProps) {
  const { t } = useTranslation();
  const toast = useToast();
  const { user } = useAuth();
  const userId = user?.id != null ? String(user.id) : undefined;
  const onCompleteRef = useRef(onComplete);
  onCompleteRef.current = onComplete;
  const scope = useRef({ open, projectId, userId, generation: 0 });
  if (scope.current.open !== open || scope.current.projectId !== projectId || scope.current.userId !== userId) {
    scope.current = { open, projectId, userId, generation: scope.current.generation + 1 };
  }
  const requestLock = useRef(false);
  const isCurrentRequest = (request: PreviewRequest) =>
    scope.current.open && scope.current.generation === request.generation &&
    scope.current.projectId === request.projectId && scope.current.userId === request.userId;
  const headingRef = useRef<HTMLDivElement>(null);
  const previewKey = useRef("");
  const [step, setStep] = useState<Step>(1);
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<MspPreviewResult | null>(null);
  const [replace, setReplace] = useState(false);
  const [taskId, setTaskId] = useState<string | null>(null);
  const [attempt, setAttempt] = useState<ImportAttemptSession | null>(null);
  const [progress, setProgress] = useState(0);
  const [summary, setSummary] = useState<ImportSummary | null>(null);
  const [failureItems, setFailureItems] = useState<{ code: string; row: string }[]>([]);
  const [interrupted, setInterrupted] = useState(false);
  const [retryNonce, setRetryNonce] = useState(0);

  const codeMessage = useCallback(
    (code: string) =>
      t(`scheduleImport.codes.${code}`, {
        defaultValue: t("scheduleImport.unknownCode"),
      }),
    [t],
  );

  const clearScreen = useCallback(() => {
    previewKey.current = "";
    setStep(1);
    setFile(null);
    setPreview(null);
    setReplace(false);
    setTaskId(null);
    setAttempt(null);
    setProgress(0);
    setSummary(null);
    setFailureItems([]);
    setInterrupted(false);
  }, []);

  useEffect(() => {
    clearScreen();
    if (!open) return;
    const saved = readImportAttempt(userId, projectId);
    if (saved) {
      setAttempt(saved);
      setTaskId(saved.task_id);
      setReplace(saved.replace);
      setStep(3);
    }
  }, [open, userId, projectId, clearScreen]);

  useEffect(() => {
    if (!open) return;
    headingRef.current?.focus();
  }, [open, step]);

  const previewMutation = useMutation({
    mutationFn: (request: PreviewRequest) =>
      isP6File(request.file)
        ? previewP6Import(request.projectId, request.file)
        : previewMspImport(request.projectId, request.file),
    onSuccess: (data, request) => {
      if (!isCurrentRequest(request) || fileIdentity(request.file) !== previewKey.current) return;
      setPreview(data);
      setFailureItems([]);
      setStep(2);
    },
    onError: (e: Error, request) => {
      if (!isCurrentRequest(request)) return;
      const code = e instanceof ApiRequestError ? e.code : undefined;
      toast.error(code ? codeMessage(code) : t("scheduleImport.unknownCode"));
    },
    onSettled: () => { requestLock.current = false; },
  });

  const importMutation = useMutation({
    mutationFn: (opts: StartRequest) =>
      isP6File(opts.file)
        ? startP6Import(opts.projectId, opts.file, opts.replace)
        : startMspImport(opts.projectId, opts.file, opts.replace),
    onSuccess: (data, opts) => {
      const saved: ImportAttemptSession = {
        user_id: opts.userId,
        project_id: opts.projectId,
        task_id: data.task_id,
        file_name: opts.file.name,
        recognized_kind: opts.recognizedKind,
        replace: opts.replace,
      };
      saveImportAttempt(saved);
      if (!scope.current.open || scope.current.projectId !== opts.projectId || scope.current.userId !== opts.userId) return;
      setAttempt(saved);
      setTaskId(data.task_id);
      setFailureItems([]);
      setInterrupted(false);
      setSummary(null);
      setStep(3);
    },
    onError: (e: Error, request) => {
      if (!isCurrentRequest(request)) return;
      const code = e instanceof ApiRequestError ? e.code : undefined;
      if (code) setFailureItems([{ code, row: "" }]);
      else toast.error(t("scheduleImport.unknownCode"));
    },
    onSettled: () => { requestLock.current = false; },
  });

  const busy = previewMutation.isPending || importMutation.isPending;

  useEffect(() => {
    if (!open || step !== 3 || !taskId || !userId) return;
    if (attempt && (attempt.user_id !== userId || attempt.project_id !== projectId || attempt.task_id !== taskId)) {
      return;
    }
    let cancelled = false;
    let timer: number | undefined;
    const kind = attempt?.recognized_kind;
    const useP6 = kind === "xer" || (!kind && file != null && isP6File(file));

    const poll = async () => {
      if (cancelled) return;
      try {
        const status: MspImportStatusResult = useP6
          ? await fetchP6ImportStatus(projectId, taskId)
          : await fetchMspImportStatus(projectId, taskId);
        if (cancelled) return;
        if (attempt && (attempt.user_id !== userId || attempt.project_id !== projectId)) return;
        setInterrupted(false);
        setProgress(status.progress_pct);
        if (status.status === "done" && status.result) {
          setSummary(status.result);
          setFailureItems([]);
          onCompleteRef.current?.();
          return;
        }
        if (status.status === "failed") {
          const blocking = status.blocking ?? [];
          if (blocking.length > 0) setFailureItems(blocking);
          else if (status.error_code) setFailureItems([{ code: status.error_code, row: "" }]);
          else setFailureItems([{ code: "import_failed", row: "" }]);
          return;
        }
        timer = window.setTimeout(poll, 2000);
      } catch (e) {
        if (cancelled) return;
        if (e instanceof ApiRequestError && (e.status === 401 || e.status === 403)) {
          setInterrupted(false);
          setFailureItems([{ code: e.code || "import_not_permitted", row: "" }]);
          return;
        }
        setInterrupted(true);
      }
    };

    void poll();
    return () => {
      cancelled = true;
      window.clearTimeout(timer);
    };
  }, [open, step, taskId, projectId, userId, attempt, file, retryNonce]);

  const onFileSelect = (f: File | null) => {
    if (!f || busy || requestLock.current || step === 3) return;
    if (!isScheduleImportFile(f)) {
      toast.error(t("scheduleImport.wrongExtension"));
      return;
    }
    setFile(f);
    setPreview(null);
    setFailureItems([]);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (busy || requestLock.current || step === 3) return;
    onFileSelect(e.dataTransfer.files[0] ?? null);
  };

  const requestPreview = () => {
    if (!file || !userId || busy || requestLock.current) return;
    requestLock.current = true;
    previewKey.current = fileIdentity(file);
    previewMutation.mutate({ file, userId, projectId, generation: scope.current.generation });
  };

  const confirmImport = () => {
    if (!file || !preview || !userId || busy || requestLock.current) return;
    if (fileIdentity(file) !== previewKey.current) return;
    if ((preview.blocking?.length ?? 0) > 0) return;
    if (replace && preview.replacement?.blocked) return;
    requestLock.current = true;
    importMutation.mutate({ file, replace, userId, projectId,
      generation: scope.current.generation, recognizedKind: preview.recognized_kind ?? (isP6File(file) ? "xer" : "xml") });
  };

  const chooseAnother = () => {
    if (userId) clearImportAttempt(userId, projectId);
    clearScreen();
  };

  const activeCounts: ImportCounts | undefined =
    replace && !preview?.replacement?.blocked ? preview?.counts_if_replaced : preview?.counts;
  const removed = replace
    ? preview?.replacement
    : { wbs_nodes_removed: 0, activities_removed: 0, relations_removed: 0, blocked: null };
  const confirmDisabled =
    !file ||
    busy ||
    fileIdentity(file) !== previewKey.current ||
    (preview?.blocking?.length ?? 0) > 0 ||
    Boolean(replace && preview?.replacement?.blocked);
  const shownFileName = file?.name ?? attempt?.file_name ?? "";
  const shownKind = preview?.recognized_kind ?? attempt?.recognized_kind;

  return (
    <Modal
      open={open}
      onOpenChange={onOpenChange}
      title={t("scheduleImport.title")}
      idBase="mspImport"
      className="w-[calc(100vw-1.5rem)] max-w-2xl"
    >
      <div ref={headingRef} tabIndex={-1} role="heading" aria-level={2} aria-label={t(step === 1 ? "scheduleImport.stepUpload" : step === 2 ? "scheduleImport.stepPreview" : "scheduleImport.stepProgress")} className="mb-4 flex flex-wrap gap-2 text-sm outline-none">
        {([1, 2, 3] as const).map((s) => (
          <span
            key={s}
            className={`rounded px-2 py-1 ${step === s ? "bg-primary/10 font-medium" : "text-muted-foreground"}`}
          >
            {s === 1
              ? t("scheduleImport.stepUpload")
              : s === 2
                ? t("scheduleImport.stepPreview")
                : t("scheduleImport.stepProgress")}
          </span>
        ))}
      </div>

      {step === 1 && (
        <div className="space-y-4">
          <div className="rounded-md border border-border bg-muted/40 p-3 text-sm text-muted-foreground">
            {t("scheduleImport.acceptedFormats")}
          </div>
          <div
            className="flex flex-col items-center justify-center gap-3 rounded-lg border-2 border-dashed border-border p-8"
            onDragOver={(e) => e.preventDefault()}
            onDrop={handleDrop}
          >
            <Upload className="size-10 text-muted-foreground" />
            <p className="text-center text-sm text-muted-foreground">{t("scheduleImport.dropFile")}</p>
            <label className="cursor-pointer">
              <input
                type="file"
                accept=".mpp,.xml,.xer,application/xml,text/xml,application/vnd.ms-project"
                className="peer sr-only"
                disabled={busy}
                aria-label={t("scheduleImport.fileLabel")}
                onChange={(e) => onFileSelect(e.target.files?.[0] ?? null)}
              />
              <span className="inline-flex items-center gap-2 rounded-md border border-border bg-muted px-3 py-2 text-sm hover:bg-muted/80 peer-focus-visible:outline-none peer-focus-visible:ring-2 peer-focus-visible:ring-ring peer-focus-visible:ring-offset-2">
                <FileUp className="size-4" />
                {t("scheduleImport.chooseFile")}
              </span>
            </label>
            {file ? (
              <p className="break-all text-sm" data-testid="msp-import-filename">
                {file.name} — {(file.size / 1024).toFixed(1)} KB
              </p>
            ) : null}
          </div>
          {previewMutation.isPending ? (
            <div
              className="rounded-md border border-border bg-muted/30 p-3 text-sm text-muted-foreground"
              data-testid="msp-import-processing"
              role="status"
              aria-live="polite"
            >
              {t("scheduleImport.preparing")}
            </div>
          ) : null}
          <div className="flex justify-end gap-2">
            <Button variant="ghost" onClick={() => onOpenChange(false)} disabled={busy}>
              {t("scheduleImport.cancel")}
            </Button>
            <Button variant="primary" disabled={!file || busy} loading={previewMutation.isPending} onClick={requestPreview}>
              {t("scheduleImport.preview")}
            </Button>
          </div>
        </div>
      )}

      {step === 2 && preview && (
        <div className="space-y-4">
          {shownFileName ? (
            <p className="break-all text-sm" data-testid="msp-import-filename">
              <span className="text-muted-foreground">{t("scheduleImport.fileLabel")}: </span>
              {shownFileName}
            </p>
          ) : null}
          {shownKind ? (
            <p className="text-sm">
              <span className="text-muted-foreground">{t("scheduleImport.kindLabel")}: </span>
              {t(`scheduleImport.kinds.${shownKind}`, { defaultValue: t("scheduleImport.unknownCode") })}
            </p>
          ) : null}
          {(preview.blocking?.length ?? 0) > 0 && (
            <div className="rounded-md border border-destructive/40 bg-destructive/10 p-3 text-sm text-destructive" data-testid="msp-import-blocking">
              <ul className="max-h-48 list-inside list-disc overflow-y-auto break-words">
                {preview.blocking?.map((item) => (
                  <li key={`${item.code}-${item.row}`}>
                    {codeMessage(item.code)}
                    {item.row ? ` (${item.row})` : ""}
                  </li>
                ))}
              </ul>
            </div>
          )}
          {(preview.warning_items?.length ?? 0) > 0 && (
            <div
              className="rounded-md border border-warning-200 bg-warning-50 p-3 text-sm text-warning-900 dark:border-warning-900/50 dark:bg-warning-950/30 dark:text-warning-200"
              data-testid="msp-import-warnings"
            >
              <p className="font-medium">{t("scheduleImport.warnings")}</p>
              <ul className="mt-1 max-h-48 list-inside list-disc overflow-y-auto break-words">
                {preview.warning_items?.map((item) => (
                  <li key={`${item.code}-${item.row}`}>
                    {codeMessage(item.code)}
                    {item.row ? ` (${item.row})` : ""}
                  </li>
                ))}
              </ul>
            </div>
          )}
          <TemplateWBSPreviewTree nodes={preview.wbs_tree} />
          {activeCounts ? (
            <ul className="list-inside list-disc text-sm text-muted-foreground">
              <li>{t("scheduleImport.rowsRead", { count: activeCounts.rows_read })}</li>
              <li>{t("scheduleImport.wbsNodes", { count: activeCounts.created_packages })}</li>
              <li>{t("scheduleImport.activities", { count: activeCounts.created_activities })}</li>
              <li>{t("scheduleImport.relationshipsKept", { count: activeCounts.relationships_kept })}</li>
              <li>{t("scheduleImport.duplicates", { count: activeCounts.duplicate_count })}</li>
              <li>{t("scheduleImport.rowsOmitted", { count: activeCounts.rows_omitted })}</li>
              <li>{t("scheduleImport.removedPackages", { count: removed?.wbs_nodes_removed ?? 0 })}</li>
              <li>{t("scheduleImport.removedActivities", { count: removed?.activities_removed ?? 0 })}</li>
              <li>{t("scheduleImport.removedRelations", { count: removed?.relations_removed ?? 0 })}</li>
            </ul>
          ) : null}
          <div className="space-y-2">
            <p className="text-sm font-medium" id="msp-import-mode">
              {t("scheduleImport.importMode")}
            </p>
            <label className="flex cursor-pointer items-center gap-2 text-sm">
              <input
                type="radio"
                name="mspMode"
                checked={replace}
                disabled={busy}
                onChange={() => setReplace(true)}
              />
              {t("scheduleImport.replace")}
            </label>
            <label className="flex cursor-pointer items-center gap-2 text-sm">
              <input
                type="radio"
                name="mspMode"
                checked={!replace}
                disabled={busy}
                onChange={() => setReplace(false)}
              />
              {t("scheduleImport.append")}
            </label>
          </div>
          {replace && preview.replacement?.blocked ? (
            <p className="text-destructive text-sm" data-testid="msp-import-refusal">
              {codeMessage(preview.replacement.blocked)}
            </p>
          ) : null}
          {failureItems.length > 0 ? (
            <ul className="list-inside list-disc text-sm text-destructive">
              {failureItems.map((item) => (
                <li key={`${item.code}-${item.row}`}>{codeMessage(item.code)}</li>
              ))}
            </ul>
          ) : null}
          <div className="flex justify-between gap-2">
            <Button
              variant="ghost"
              onClick={() => {
                setPreview(null);
                setStep(1);
              }}
              disabled={busy}
            >
              {t("scheduleImport.back")}
            </Button>
            <Button variant="primary" loading={importMutation.isPending} disabled={confirmDisabled} onClick={confirmImport}>
              {t("scheduleImport.confirm")}
            </Button>
          </div>
        </div>
      )}

      {step === 3 && (
        <div className="space-y-4">
          {shownFileName ? (
            <p className="break-all text-sm" data-testid="msp-import-filename">
              {shownFileName}
            </p>
          ) : null}
          {failureItems.length > 0 ? (
            <div className="space-y-3" data-testid="msp-import-fatal-error">
              <ul className="max-h-48 list-inside list-disc overflow-y-auto break-words text-sm text-destructive">
                {failureItems.map((item) => (
                  <li key={`${item.code}-${item.row}`}>
                    {codeMessage(item.code)}
                    {item.row ? ` (${item.row})` : ""}
                  </li>
                ))}
              </ul>
              <div className="flex flex-wrap gap-2">
                <Button variant="ghost" onClick={chooseAnother}>
                  {t("scheduleImport.chooseAnother")}
                </Button>
                <Button variant="ghost" onClick={() => onOpenChange(false)}>
                  {t("scheduleImport.close")}
                </Button>
              </div>
            </div>
          ) : interrupted ? (
            <div className="space-y-3" role="status" data-testid="msp-import-interrupted">
              <p className="text-sm">{t("scheduleImport.stillWorking")}</p>
              <Button variant="primary" onClick={() => setRetryNonce((value) => value + 1)}>
                {t("scheduleImport.retryStatus")}
              </Button>
            </div>
          ) : summary ? (
            <div className="space-y-2 text-sm">
              <p>
                {summary.nothing_changed
                  ? t("scheduleImport.nothingChanged")
                  : t("scheduleImport.imported")}
              </p>
              <ul className="list-inside list-disc text-muted-foreground">
                <li>{t("scheduleImport.rowsRead", { count: summary.rows_read ?? 0 })}</li>
                <li>{t("scheduleImport.wbsNodes", { count: summary.wbs_nodes_created })}</li>
                <li>{t("scheduleImport.activities", { count: summary.activities_created })}</li>
                <li>
                  {t("scheduleImport.relationshipsKept", {
                    count: summary.relationships_kept ?? summary.relations_created,
                  })}
                </li>
                <li>{t("scheduleImport.duplicates", { count: summary.duplicate_count ?? 0 })}</li>
                <li>{t("scheduleImport.rowsOmitted", { count: summary.rows_omitted ?? 0 })}</li>
                <li>{t("scheduleImport.removedPackages", { count: summary.wbs_nodes_removed ?? 0 })}</li>
                <li>{t("scheduleImport.removedActivities", { count: summary.activities_removed ?? 0 })}</li>
                <li>{t("scheduleImport.removedRelations", { count: summary.relations_removed ?? 0 })}</li>
              </ul>
              {(summary.warning_items?.length ?? 0) > 0 && (
                <ul className="max-h-48 list-inside list-disc overflow-y-auto break-words text-warning-900 dark:text-warning-200">
                  {summary.warning_items?.map((item) => (
                    <li key={`${item.code}-${item.row}`}>
                      {codeMessage(item.code)}
                      {item.row ? ` (${item.row})` : ""}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          ) : (
            <div className="space-y-2" role="status" aria-live="polite">
              <p className="text-sm text-muted-foreground">{t("scheduleImport.importing")}</p>
              <div className="h-2 overflow-hidden rounded-full bg-muted">
                <div className="h-full bg-primary transition-all" style={{ width: `${progress}%` }} />
              </div>
              <p className="text-xs text-muted-foreground">{progress}%</p>
            </div>
          )}
          <div className="flex flex-wrap justify-end gap-2">
            {summary ? (
              <>
                <Button variant="ghost" onClick={chooseAnother}>{t("scheduleImport.chooseAnother")}</Button>
                <Link to={`/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_WBS}`}>
                  <Button variant="primary" onClick={() => onOpenChange(false)}>
                    {t("scheduleImport.viewWbs")}
                  </Button>
                </Link>
                <Link to={`/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_ACTIVITIES}`}>
                  <Button variant="secondary" onClick={() => onOpenChange(false)}>
                    {t("scheduleImport.viewActivities")}
                  </Button>
                </Link>
              </>
            ) : null}
          </div>
        </div>
      )}
    </Modal>
  );
}
