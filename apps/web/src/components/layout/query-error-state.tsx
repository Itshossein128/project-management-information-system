import { AlertCircle, Loader2 } from "lucide-react";
import { useTranslation } from "react-i18next";
import { useState } from "react";
import { cn } from "@/app/lib/utils";
import { Button } from "@/components/ui/sprint-button";
import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert";

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
  const [isRetrying, setIsRetrying] = useState(false);

  return (
    <Alert
      variant="destructive"
      className={cn(
        "flex flex-col items-center gap-3 border-destructive/30 bg-destructive/5 px-6 py-12 text-center",
        className,
      )}
    >
      <div className="flex justify-center">
        <AlertCircle className="size-10 text-destructive/70" aria-hidden />
      </div>
      <AlertTitle className="text-base font-medium">{t("common.error", "خطا")}</AlertTitle>
      <AlertDescription className="flex flex-col items-center gap-3">
        <p className="text-base font-medium text-foreground">
          {message ?? t("common.loadFailed")}
        </p>
        {onRetry ? (
          <Button
            variant="secondary"
            size="sm"
            disabled={isRetrying}
            aria-busy={isRetrying}
            className="inline-flex items-center gap-2"
            onClick={async () => {
              setIsRetrying(true);
              try {
                await Promise.resolve(onRetry());
              } finally {
                setIsRetrying(false);
              }
            }}
          >
            {isRetrying ? <Loader2 className="size-4 animate-spin" aria-hidden="true" /> : null}
            {t("common.retry")}
          </Button>
        ) : null}
      </AlertDescription>
    </Alert>
  );
}
