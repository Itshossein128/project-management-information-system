import { AlertCircle } from "lucide-react";
import { useTranslation } from "react-i18next";
import { ApiRequestError } from "@/app/lib/api-client";
import { cn } from "@/app/lib/utils";
import { Button } from "@/components/ui/sprint-button";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

export interface QueryErrorStateProps {
  message?: string;
  error?: unknown;
  onRetry?: () => void;
  className?: string;
}

export function QueryErrorState({
  message,
  error,
  onRetry,
  className,
}: QueryErrorStateProps) {
  const { t } = useTranslation();
  const isForbidden = error instanceof ApiRequestError && error.status === 403;
  const resolvedMessage =
    message ?? (isForbidden ? t("common.accessDenied") : t("common.loadFailed"));

  return (
    <Alert
      variant="destructive"
      className={cn(
        "flex flex-col items-center justify-center gap-3 px-6 py-12 text-center bg-destructive/5",
        className,
      )}
    >
      <div className="flex flex-col items-center justify-center gap-3 w-full">
        <div className="text-destructive/70 [&>svg]:size-10"><AlertCircle aria-hidden /></div>
        <AlertTitle className="text-base font-medium">
          {resolvedMessage}
        </AlertTitle>
        {onRetry && !isForbidden ? (
          <Button variant="secondary" size="sm" onClick={onRetry} className="mt-2">
            {t("common.retry")}
          </Button>
        ) : null}
      </div>
    </Alert>
  );
}
