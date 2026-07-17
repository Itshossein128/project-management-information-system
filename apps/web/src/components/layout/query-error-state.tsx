import { AlertCircle } from "lucide-react";
import { useTranslation } from "react-i18next";
import { cn } from "@/app/lib/utils";
import { Button } from "@/components/ui/sprint-button";

export interface QueryErrorStateProps {
  message?: string;
  onRetry?: () => void;
  className?: string;
}

export function QueryErrorState({
  message,
  onRetry,
  className,
}: QueryErrorStateProps) {
  const { t } = useTranslation();

  return (
    <div
      className={cn(
        "flex flex-col items-center gap-3 rounded-lg border border-destructive/30 bg-destructive/5 px-6 py-12 text-center",
        className,
      )}
      role="alert"
    >
      <AlertCircle className="size-10 text-destructive/70" aria-hidden />
      <p className="text-base font-medium text-foreground">
        {message ?? t("common.loadFailed")}
      </p>
      {onRetry ? (
        <Button variant="secondary" size="sm" onClick={onRetry}>
          {t("common.retry")}
        </Button>
      ) : null}
    </div>
  );
}
