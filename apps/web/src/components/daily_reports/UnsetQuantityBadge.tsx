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
  return <Badge variant="neutral" label={t("dailyReports.unsetQuantity", "ثبت‌نشده")} data-testid="unset-quantity-badge" />;
}
