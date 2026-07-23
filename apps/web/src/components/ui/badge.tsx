import type { HTMLAttributes } from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "src/app/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium",
  {
    variants: {
      variant: {
        success: "bg-success-100 text-success-800 dark:bg-success-900/40 dark:text-success-300",
        warning: "bg-warning-100 text-warning-800 dark:bg-warning-900/40 dark:text-warning-300",
        danger: "bg-danger-100 text-danger-800 dark:bg-danger-900/40 dark:text-danger-300",
        info: "bg-info-100 text-info-800 dark:bg-info-900/40 dark:text-info-300",
        neutral: "bg-muted text-muted-foreground",
      },
    },
    defaultVariants: { variant: "neutral" },
  },
);

export interface BadgeProps
  extends VariantProps<typeof badgeVariants>,
    HTMLAttributes<HTMLSpanElement> {
  label: string;
  className?: string;
}

export function Badge({ variant, label, className, ...props }: BadgeProps) {
  return (
    <span className={cn(badgeVariants({ variant }), className)} {...props}>
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
