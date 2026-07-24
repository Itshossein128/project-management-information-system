import type { ReactNode } from "react";
import { Lock } from "lucide-react";
import { cn } from "@/app/lib/utils";

export interface EmptyStateProps {
  icon?: ReactNode;
  title: string;
  description?: string;
  action?: ReactNode;
  className?: string;
}

export function EmptyState({
  icon,
  title,
  description,
  action,
  className,
}: EmptyStateProps) {
  return (
    <div
      className={cn(
        "flex flex-col items-center gap-3 rounded-lg border border-dashed border-border px-6 py-16 text-center",
        className,
      )}
      role="status"
    >
      {icon ? (
        <div className="text-muted-foreground/50 [&_svg]:size-12">{icon}</div>
      ) : null}
      <p className="text-base font-medium text-foreground">{title}</p>
      {description ? (
        <p className="max-w-sm text-sm text-muted-foreground">{description}</p>
      ) : null}
      {action ? <div className="mt-2">{action}</div> : null}
    </div>
  );
}

/** Consistent "you don't have permission" state. */
export function AccessDenied({
  description = "برای مشاهده این بخش به مجوز مربوطه نیاز است.",
  title = "دسترسی ندارید",
  className,
}: {
  description?: string;
  title?: string;
  className?: string;
}) {
  return (
    <EmptyState
      icon={<Lock />}
      title={title}
      description={description}
      className={className}
    />
  );
}

/** Consistent "not found" state (e.g. missing project/record). */
export function NotFoundState({
  title = "یافت نشد",
  description,
  className,
}: {
  title?: string;
  description?: string;
  className?: string;
}) {
  return <EmptyState title={title} description={description} className={className} />;
}
