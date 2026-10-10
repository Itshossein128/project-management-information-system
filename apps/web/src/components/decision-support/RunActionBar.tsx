import { useTranslation } from "react-i18next";
import { Button } from "@/components/form/Button";

type Props = {
  methodLabel: string;
  disabled?: boolean;
  pending?: boolean;
  onValidate: () => void;
  onRun: () => void;
};

export function RunActionBar({
  methodLabel,
  disabled,
  pending,
  onValidate,
  onRun,
}: Props) {
  const { t } = useTranslation();

  return (
    <div className="flex flex-wrap gap-2">
      <Button type="button" variant="outline" disabled={disabled || pending} onClick={onValidate}>
        {t("decisionSupport.validate")}
      </Button>
      <Button type="button" disabled={disabled || pending} onClick={onRun}>
        {pending ? t("decisionSupport.running") : t("decisionSupport.runMethod", { method: methodLabel })}
      </Button>
    </div>
  );
}
