import { Button } from "@/components/form";
import { cn } from "@/app/lib/utils";
import { useEffect } from "react";
import { X } from "lucide-react";

export interface ModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  title: string;
  /** Base ID like `allAssignments` → modal-allAssignments, text-allAssignmentsTitle, ... */
  idBase: string;
  children: React.ReactNode;
  className?: string;
}

export function Modal({
  open,
  onOpenChange,
  title,
  idBase,
  children,
  className,
}: ModalProps) {
  useEffect(() => {
    if (!open) return;
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") onOpenChange(false);
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [open, onOpenChange]);

  if (!open) return null;

  return (
    <div
      id={`modal-${idBase}`}
      className="fixed inset-0 z-50 flex items-end justify-center bg-overlay p-0 sm:items-center sm:p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby={`text-${idBase}ModalTitle`}
      onMouseDown={(e) => {
        if (e.target === e.currentTarget) onOpenChange(false);
      }}
    >
      <div
        id={`modal-${idBase}Body`}
        className={cn(
          "flex max-h-[min(90dvh,100%)] w-full max-w-3xl flex-col rounded-t-xl border border-border bg-background shadow-lg sm:max-h-[90dvh] sm:rounded-xl",
          className,
        )}
      >
        <div
          id={`modal-${idBase}Header`}
          className="flex shrink-0 flex-wrap items-start justify-between gap-3 border-b border-border px-4 py-3"
        >
          <h2
            id={`text-${idBase}ModalTitle`}
            className="text-base font-semibold"
          >
            {title}
          </h2>
          <Button
            id={`button-close${idBase.charAt(0).toUpperCase() + idBase.slice(1)}Modal`}
            type="button"
            variant="ghost"
            size="icon-sm"
            aria-label="Close"
            onClick={() => onOpenChange(false)}
          >
            <X className="size-4" aria-hidden />
          </Button>
        </div>
        <div id={`modal-${idBase}Content`} className="min-h-0 flex-1 overflow-y-auto p-4">
          {children}
        </div>
      </div>
    </div>
  );
}

