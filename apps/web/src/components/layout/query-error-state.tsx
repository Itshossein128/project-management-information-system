import { AlertCircle } from "lucide-react";
import { useTranslation } from "react-i18next";
import { cn } from "@/app/lib/utils";
import { Button } from "@/components/ui/sprint-button";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

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
          {message ?? t("common.loadFailed")}
        </AlertTitle>
        {onRetry ? (
          <Button variant="secondary" size="sm" onClick={onRetry} className="mt-2">
            {t("common.retry")}
          </Button>
        ) : null}
      </div>
    </Alert>
  );
}
