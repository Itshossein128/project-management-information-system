import { cva, type VariantProps } from "class-variance-authority";
import { Loader2 } from "lucide-react";
import * as React from "react";
import { Button as ShadcnButton } from "src/components/ui/button";
import { cn } from "src/app/lib/utils";

const sprintButtonVariants = cva("", {
  variants: {
    variant: {
      primary: "",
      secondary: "",
      ghost: "",
      danger: "",
    },
  },
  defaultVariants: { variant: "primary" },
});

type SprintVariant = NonNullable<VariantProps<typeof sprintButtonVariants>["variant"]>;

const variantMap: Record<SprintVariant, React.ComponentProps<typeof ShadcnButton>["variant"]> = {
  primary: "default",
  secondary: "secondary",
  ghost: "ghost",
  danger: "destructive",
};

export interface SprintButtonProps extends Omit<React.ComponentProps<typeof ShadcnButton>, "variant"> {
  variant?: SprintVariant;
  loading?: boolean;
}

export function SprintButton({
  variant = "primary",
  loading = false,
  disabled,
  children,
  className,
  size = "default",
  ...props
}: SprintButtonProps) {
  return (
    <ShadcnButton
      variant={variantMap[variant]}
      size={size}
      disabled={disabled || loading}
      aria-busy={loading}
      className={cn(className)}
      {...props}
    >
      {loading ? <Loader2 className="size-4 animate-spin" aria-hidden="true" /> : null}
      {children}
    </ShadcnButton>
  );
}

export { SprintButton as Button };
