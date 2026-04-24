import { Button } from "@/components/form";
import { cn } from "@/app/lib/utils";
import { useEffect } from "react";

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
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
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
          "w-full max-w-3xl rounded-xl border border-border bg-background shadow-lg",
          className,
        )}
      >
        <div
          id={`modal-${idBase}Header`}
          className="flex items-start justify-between gap-3 border-b border-border px-4 py-3"
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
            size="sm"
            onClick={() => onOpenChange(false)}
          >
            ×
          </Button>
        </div>
        <div id={`modal-${idBase}Content`} className="p-4">
          {children}
        </div>
      </div>
    </div>
  );
}

