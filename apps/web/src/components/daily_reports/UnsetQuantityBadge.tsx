import { useTranslation } from "react-i18next";
import { Badge } from "@/components/ui/badge";

export function isUnsetQuantity(
  quantity: string | number | null | undefined,
  quantityMeasured: boolean | null | undefined,
) {
  return quantity == null || quantityMeasured === false;
}

export function UnsetQuantityBadge({
  quantity,
  quantityMeasured,
}: {
  quantity: string | number | null | undefined;
  quantityMeasured: boolean | null | undefined;
}) {
  const { t } = useTranslation();
  if (!isUnsetQuantity(quantity, quantityMeasured)) return <>{quantity}</>;
  // Snapshot (feature 036): unset quantity earns a local caution outline over
  // the shared neutral Badge styling — the muted background/compact text stay,
  // only this badge gains the warning-colored ring in both themes.
  return (
    <Badge
      variant="neutral"
      label={t("dailyReports.unsetQuantity", "ثبت‌نشده")}
      data-testid="unset-quantity-badge"
      className="ring-2 ring-inset ring-warning-500 dark:ring-warning-400 border-0"
    />
  );
}
