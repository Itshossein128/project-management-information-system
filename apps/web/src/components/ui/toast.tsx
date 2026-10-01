import { createContext, useCallback, useContext, useMemo, useState } from "react";
import { X } from "lucide-react";
import { cn } from "src/app/lib/utils";

type ToastVariant = "success" | "error" | "warning";

interface ToastAction {
  label: string;
  onClick: () => void;
}

interface ToastOptions {
  action?: ToastAction;
  duration?: number;
}

interface ToastItem {
  id: number;
  message: string;
  variant: ToastVariant;
  action?: ToastAction;
  duration: number;
}

interface ToastContextValue {
  success: (message: string, options?: ToastOptions) => void;
  error: (message: string, options?: ToastOptions) => void;
  warning: (message: string, options?: ToastOptions) => void;
}

const ToastContext = createContext<ToastContextValue | null>(null);

const variantClass: Record<ToastVariant, string> = {
  success: "border-success-500/50 bg-success-50 text-success-900 dark:bg-success-950 dark:text-success-100",
  error: "border-danger-500/50 bg-danger-50 text-danger-900 dark:bg-danger-950 dark:text-danger-100",
  warning: "border-warning-500/50 bg-warning-50 text-warning-900 dark:bg-warning-950 dark:text-warning-100",
};

const DEFAULT_DURATION_MS = 4000;
const ACTION_DURATION_MS = 10000;

const UNDO_RING_SIZE = 22;
const UNDO_RING_STROKE = 2.5;
const UNDO_RING_RADIUS = (UNDO_RING_SIZE - UNDO_RING_STROKE) / 2;
const UNDO_RING_CIRCUMFERENCE = 2 * Math.PI * UNDO_RING_RADIUS;

function UndoCountdownButton({
  label,
  durationMs,
  onClick,
}: {
  label: string;
  durationMs: number;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      className="inline-flex shrink-0 items-center gap-1.5 rounded px-1.5 py-0.5 text-sm font-semibold underline-offset-2 hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
      onClick={onClick}
    >
      <svg
        width={UNDO_RING_SIZE}
        height={UNDO_RING_SIZE}
        viewBox={`0 0 ${UNDO_RING_SIZE} ${UNDO_RING_SIZE}`}
        className="-rotate-90"
        aria-hidden
      >
        <circle
          cx={UNDO_RING_SIZE / 2}
          cy={UNDO_RING_SIZE / 2}
          r={UNDO_RING_RADIUS}
          fill="none"
          stroke="currentColor"
          strokeOpacity={0.25}
          strokeWidth={UNDO_RING_STROKE}
        />
        <circle
          cx={UNDO_RING_SIZE / 2}
          cy={UNDO_RING_SIZE / 2}
          r={UNDO_RING_RADIUS}
          fill="none"
          stroke="currentColor"
          strokeWidth={UNDO_RING_STROKE}
          strokeLinecap="round"
          strokeDasharray={UNDO_RING_CIRCUMFERENCE}
          style={{
            strokeDashoffset: 0,
            animation: `toast-undo-countdown ${durationMs}ms linear forwards`,
          }}
        />
      </svg>
      <span>{label}</span>
    </button>
  );
}

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<ToastItem[]>([]);

  const dismiss = useCallback((id: number) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const push = useCallback((message: string, variant: ToastVariant, options?: ToastOptions) => {
    const id = Date.now() + Math.floor(Math.random() * 1000);
    const duration =
      options?.duration ??
      (options?.action ? ACTION_DURATION_MS : DEFAULT_DURATION_MS);
    setToasts((prev) => [
      ...prev,
      { id, message, variant, action: options?.action, duration },
    ]);
    window.setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, duration);
  }, []);

  const value = useMemo(
    () => ({
      success: (message: string, options?: ToastOptions) =>
        push(message, "success", options),
      error: (message: string, options?: ToastOptions) =>
        push(message, "error", options),
      warning: (message: string, options?: ToastOptions) =>
        push(message, "warning", options),
    }),
    [push],
  );

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div
        className="pointer-events-none fixed bottom-4 start-4 z-[100] flex max-w-sm flex-col gap-2"
        aria-live="polite"
        aria-relevant="additions text"
      >
        {toasts.map((t) => {
          const isAlert = t.variant === "error" || Boolean(t.action);
          return (
            <div
              key={t.id}
              className={cn(
                "pointer-events-auto flex items-start gap-2 rounded-lg border px-4 py-3 text-sm shadow-lg",
                variantClass[t.variant],
              )}
              role="alert"
              aria-live={isAlert ? "assertive" : "polite"}
            >
              <p className="flex-1">{t.message}</p>
              {t.action ? (
                <UndoCountdownButton
                  label={t.action.label}
                  durationMs={t.duration}
                  onClick={() => {
                    dismiss(t.id);
                    t.action?.onClick();
                  }}
                />
              ) : null}
              <button
                type="button"
                className="shrink-0 rounded p-0.5 opacity-70 hover:opacity-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                aria-label="بستن"
                onClick={() => dismiss(t.id)}
              >
                <X className="size-4" aria-hidden />
              </button>
            </div>
          );
        })}
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error("useToast must be used within ToastProvider");
  return ctx;
}
