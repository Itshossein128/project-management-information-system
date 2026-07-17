import { Button } from "@/components/form";
import { cn } from "@/app/lib/utils";
import { X } from "lucide-react";
import { useTranslation } from "react-i18next";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

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
  const { t } = useTranslation();

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent
        id={`modal-${idBase}Body`}
        showCloseButton={false}
        className={cn(
          "flex max-h-[95dvh] w-full max-w-3xl flex-col p-0 sm:max-h-[90dvh]",
          className
        )}
        aria-describedby={undefined}
      >
        <DialogHeader
          id={`modal-${idBase}Header`}
          className="flex shrink-0 flex-row items-center justify-between gap-3 border-b border-border px-4 py-3"
        >
          <DialogTitle
            id={`text-${idBase}ModalTitle`}
            className="text-base font-semibold text-start"
          >
            {title}
          </DialogTitle>
          <Button
            id={`button-close${idBase.charAt(0).toUpperCase() + idBase.slice(1)}Modal`}
            type="button"
            variant="ghost"
            size="icon-sm"
            aria-label={t("common.close")}
            onClick={() => onOpenChange(false)}
          >
            <X className="size-4" aria-hidden />
          </Button>
        </DialogHeader>
        <div
          id={`modal-${idBase}Content`}
          className="min-h-0 flex-1 overflow-y-auto p-4"
        >
          {children}
        </div>
      </DialogContent>
    </Dialog>
  );
}
