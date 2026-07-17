import type { ReactNode } from "react";
import { cn } from "@/app/lib/utils";

export function KPICard({
  title,
  value,
  subtitle,
  trend,
  footer,
  children,
}: {
  title: string;
  value: string;
  subtitle?: string;
  trend?: { label: string; positive: boolean } | null;
  footer?: ReactNode;
  children?: ReactNode;
}) {
  return (
    <div className="rounded-xl border border-border bg-card p-4 shadow-sm">
      <p className="text-sm text-muted-foreground">{title}</p>
      <p className="mt-2 text-3xl font-bold tracking-tight">{value}</p>
      {subtitle ? <p className="mt-1 text-sm text-muted-foreground">{subtitle}</p> : null}
      {trend ? (
        <p
          className={cn(
            "mt-2 text-sm font-medium",
            trend.positive ? "text-emerald-600" : "text-red-600",
          )}
        >
          {trend.label}
        </p>
      ) : null}
      {children}
      {footer ? <div className="mt-2 text-xs text-muted-foreground">{footer}</div> : null}
    </div>
  );
}
