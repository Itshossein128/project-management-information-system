import { X } from "lucide-react";
import { useEffect } from "react";
import { cn } from "src/app/lib/utils";
import { Button } from "src/components/ui/sprint-button";

export interface DrawerProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
}

export function Drawer({ isOpen, onClose, title, children, footer }: DrawerProps) {
  useEffect(() => {
    if (!isOpen) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex">
      <button
        type="button"
        className="absolute inset-0 bg-black/40 transition-opacity"
        aria-label="Close drawer"
        onClick={onClose}
      />
      <aside
        role="dialog"
        aria-modal="true"
        aria-labelledby="drawer-title"
        className={cn(
          "relative ms-auto flex h-full w-full max-w-md flex-col border-border bg-background shadow-xl",
          "animate-in slide-in-from-start duration-300",
          "border-s",
        )}
      >
        <div className="flex items-center justify-between border-b border-border px-4 py-3">
          <h2 id="drawer-title" className="text-base font-semibold">{title}</h2>
          <Button variant="ghost" size="icon-sm" onClick={onClose} aria-label="Close">
            <X className="size-4" aria-hidden />
          </Button>
        </div>
        <div className="min-h-0 flex-1 overflow-y-auto p-4">{children}</div>
        {footer ? <div className="border-t border-border p-4">{footer}</div> : null}
      </aside>
    </div>
  );
}
