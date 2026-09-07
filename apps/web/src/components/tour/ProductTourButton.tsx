import { HelpCircle } from "lucide-react";
import { useTranslation } from "react-i18next";
import { Button } from "@/components/ui/button";

interface ProductTourButtonProps {
  onClick: () => void;
  className?: string;
  variant?: "outline" | "ghost" | "default" | "secondary";
  size?: "default" | "sm" | "lg" | "icon";
}

export function ProductTourButton({
  onClick,
  className = "",
  variant = "outline",
  size = "sm",
}: ProductTourButtonProps) {
  const { t } = useTranslation();

  return (
    <Button
      type="button"
      variant={variant}
      size={size}
      onClick={onClick}
      className={`gap-1.5 text-xs font-medium ${className}`}
      data-testid="product-tour-button"
      title={t("tour.buttonTitle", { defaultValue: "راهنمای صفحه / Product Tour" })}
    >
      <HelpCircle className="size-3.5 text-brand-600 dark:text-brand-400" />
      <span>{t("tour.buttonLabel", { defaultValue: "راهنما / Tour" })}</span>
    </Button>
  );
}
