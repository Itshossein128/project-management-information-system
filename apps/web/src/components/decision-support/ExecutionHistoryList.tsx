import { useTranslation } from "react-i18next";
import { EmptyState } from "@/components/layout/empty-state";
import type { DecisionRunSummary } from "@/app/lib/api/decision-support";

type Props = {
  runs: DecisionRunSummary[];
  filtered?: boolean;
  onSelect?: (runId: string) => void;
};

export function ExecutionHistoryList({
  runs,
  onSelect,
  filtered = false,
}: Props) {
  const { t, i18n } = useTranslation();
  if (!runs.length) {
    return (
      <EmptyState
        title={t(
          filtered
            ? "decisionSupport.historyNoMatches"
            : "decisionSupport.historyEmpty",
        )}
        description={t(
          filtered
            ? "decisionSupport.historyNoMatchesHint"
            : "decisionSupport.historyEmptyHint",
        )}
      />
    );
  }
  return (
    <ul className="divide-y divide-border rounded-md border border-border">
      {runs.map((run) => (
        <li key={run.id}>
          <button
            type="button"
            data-run-id={run.id}
            className="flex w-full flex-col gap-0.5 px-3 py-2 text-start text-sm hover:bg-muted/40"
            onClick={() => onSelect?.(run.id)}
          >
            <span className="font-medium uppercase">{run.method}</span>
            <span className="text-muted-foreground">
              {new Date(run.extracted_at).toLocaleString(i18n.language)} ·{" "}
              {run.extracted_by_name || run.extracted_by}
            </span>
          </button>
        </li>
      ))}
    </ul>
  );
}
