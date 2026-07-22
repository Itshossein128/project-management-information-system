import type { HTMLAttributes } from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "src/app/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ring-inset transition-colors",
  {
    variants: {
      variant: {
        success:
          "bg-emerald-500/12 text-emerald-700 ring-emerald-500/25 dark:bg-emerald-400/12 dark:text-emerald-300 dark:ring-emerald-400/25",
        warning:
          "bg-amber-500/12 text-amber-700 ring-amber-500/25 dark:bg-amber-400/12 dark:text-amber-300 dark:ring-amber-400/25",
        danger:
          "bg-red-500/12 text-red-700 ring-red-500/25 dark:bg-red-400/12 dark:text-red-300 dark:ring-red-400/25",
        info:
          "bg-brand-500/12 text-brand-700 ring-brand-500/25 dark:bg-brand-400/12 dark:text-brand-300 dark:ring-brand-400/25",
        neutral:
          "bg-muted text-muted-foreground ring-border/70",
      },
    },
    defaultVariants: { variant: "neutral" },
  },
);

const dotVariants = cva("size-1.5 rounded-full", {
  variants: {
    variant: {
      success: "bg-emerald-500",
      warning: "bg-amber-500",
      danger: "bg-red-500",
      info: "bg-brand-500",
      neutral: "bg-muted-foreground/60",
    },
  },
  defaultVariants: { variant: "neutral" },
});

export interface BadgeProps
  extends VariantProps<typeof badgeVariants>,
    HTMLAttributes<HTMLSpanElement> {
  label: string;
  className?: string;
}

export function Badge({ variant, label, className, ...props }: BadgeProps) {
  return (
    <span className={cn(badgeVariants({ variant }), className)} {...props}>
      <span aria-hidden className={dotVariants({ variant })} />
      {label}
    </span>
  );
}

export const projectStatusBadge: Record<string, BadgeProps["variant"]> = {
  active: "success",
  suspended: "warning",
  completed: "info",
  handed_over: "neutral",
};

export const projectStatusLabels: Record<string, string> = {
  active: "فعال",
  suspended: "معلق",
  completed: "تکمیل‌شده",
  handed_over: "تحویل‌شده",
};
