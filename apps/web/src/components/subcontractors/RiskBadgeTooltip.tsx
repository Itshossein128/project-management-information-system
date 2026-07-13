import { RiskBadge } from "./RiskBadge";

interface Props {
  riskFlag: boolean;
  reasons: string[];
}

export function RiskBadgeTooltip({ riskFlag, reasons }: Props) {
  if (!riskFlag) return <span className="text-muted-foreground">—</span>;
  return <RiskBadge reasons={reasons} />;
}
