import { useTranslation } from "react-i18next";
import type { ValidationIssue } from "./validation-issues";
import { formatIssueLabel } from "./validation-issues";

type Props = {
  issues: ValidationIssue[];
  criterionNames?: string[];
  alternativeNames?: string[];
  onFocusIssue?: (issue: ValidationIssue) => void;
};

export function ValidationIssueList({
  issues,
  onFocusIssue,
  criterionNames,
  alternativeNames,
}: Props) {
  const { t } = useTranslation();
  if (!issues.length) return null;
  const label = (issue: ValidationIssue) => {
    const match = /^ism_matrix\.(\d+)\.(\d+)$/.exec(issue.path);
    const from = match ? criterionNames?.[Number(match[1])] : undefined;
    const to = match ? criterionNames?.[Number(match[2])] : undefined;
    const matrix = /^(performance_matrix)\.(\d+)\.(\d+)$/.exec(issue.path);
    const vector = /^(weights|types|criteria)\.(\d+)$/.exec(issue.path);
    const row = matrix
      ? (matrix[1] === "performance_matrix"
          ? alternativeNames
          : criterionNames)?.[Number(matrix[2])]
      : undefined;
    const column = matrix ? criterionNames?.[Number(matrix[3])] : undefined;
    const name = vector ? criterionNames?.[Number(vector[2])] : undefined;
    if (row !== undefined && column !== undefined)
      return `${row} × ${column}: ${formatIssueLabel(issue, t)}`;
    if (name !== undefined) return `${name}: ${formatIssueLabel(issue, t)}`;
    return from !== undefined && to !== undefined
      ? t("decisionSupport.ismCell", { from, to }) +
          ": " +
          formatIssueLabel(issue, t)
      : formatIssueLabel(issue, t);
  };
  return (
    <div
      className="rounded-md border border-destructive/40 bg-destructive/5 px-3 py-2 text-sm"
      role="alert"
    >
      <p className="mb-1 font-medium text-destructive">
        {t("decisionSupport.validation")}
      </p>
      <ul className="list-disc space-y-1 ps-5">
        {issues.map((issue) => (
          <li key={`${issue.path}-${issue.code}-${issue.message}`}>
            {onFocusIssue &&
            /^(ahp_matrix|ism_matrix)\.\d+\.\d+$/.test(issue.path) ? (
              <button
                type="button"
                className="text-start underline"
                onClick={() => onFocusIssue(issue)}
              >
                {label(issue)}
              </button>
            ) : (
              label(issue)
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}
