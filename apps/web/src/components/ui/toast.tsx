import { createContext, useCallback, useContext, useMemo, useState } from "react";
import { X } from "lucide-react";
import { useTranslation } from "react-i18next";
import { cn } from "src/app/lib/utils";

type ToastVariant = "success" | "error" | "warning";

interface ToastItem {
  id: number;
  message: string;
  variant: ToastVariant;
}

interface ToastContextValue {
  success: (message: string) => void;
  error: (message: string) => void;
  warning: (message: string) => void;
}

const ToastContext = createContext<ToastContextValue | null>(null);

const variantClass: Record<ToastVariant, string> = {
  success: "border-success-500/50 bg-success-50 text-success-900 dark:bg-success-950 dark:text-success-100",
  error: "border-danger-500/50 bg-danger-50 text-danger-900 dark:bg-danger-950 dark:text-danger-100",
  warning: "border-warning-500/50 bg-warning-50 text-warning-900 dark:bg-warning-950 dark:text-warning-100",
};

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const { t } = useTranslation();
  const [toasts, setToasts] = useState<ToastItem[]>([]);

  const dismiss = useCallback((id: number) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const push = useCallback((message: string, variant: ToastVariant) => {
    const id = Date.now() + Math.floor(Math.random() * 1000);
    setToasts((prev) => [...prev, { id, message, variant }]);
    window.setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 4000);
  }, []);

  const value = useMemo(
    () => ({
      success: (message: string) => push(message, "success"),
      error: (message: string) => push(message, "error"),
      warning: (message: string) => push(message, "warning"),
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
        {toasts.map((toast) => (
          <div
            key={toast.id}
            className={cn(
              "pointer-events-auto flex items-start gap-2 rounded-lg border px-4 py-3 text-sm shadow-lg",
              variantClass[toast.variant],
            )}
            role={toast.variant === "error" ? "alert" : "status"}
            aria-live={toast.variant === "error" ? "assertive" : "polite"}
          >
            <p className="flex-1">{toast.message}</p>
            <button
              type="button"
              className="shrink-0 rounded p-0.5 opacity-70 hover:opacity-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              aria-label={t("common.close")}
              onClick={() => dismiss(toast.id)}
            >
              <X className="size-4" aria-hidden />
            </button>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error("useToast must be used within ToastProvider");
  return ctx;
}
