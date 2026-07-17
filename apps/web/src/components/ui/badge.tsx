import type { HTMLAttributes } from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "src/app/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium",
  {
    variants: {
      variant: {
        success: "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300",
        warning: "bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300",
        danger: "bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-300",
        info: "bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300",
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
