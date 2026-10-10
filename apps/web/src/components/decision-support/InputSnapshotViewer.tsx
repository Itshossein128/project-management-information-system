import { useTranslation } from "react-i18next";
import type { DecisionRun } from "@/app/lib/api/decision-support";

type Props = {
  run: DecisionRun | null;
};

export function InputSnapshotViewer({ run }: Props) {
  const { t } = useTranslation();
  if (!run) return null;
  return (
    <div className="space-y-2 rounded-md border border-border p-3 text-sm">
      <p className="font-medium">{t("decisionSupport.snapshotTitle")}</p>
      <pre className="max-h-64 overflow-auto whitespace-pre-wrap break-words text-xs text-muted-foreground">
        {JSON.stringify(run.input_snapshot, null, 2)}
      </pre>
    </div>
  );
}
