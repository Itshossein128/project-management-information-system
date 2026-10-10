import { useTranslation } from "react-i18next";
import type { ValidationIssue } from "./validation-issues";
import { formatIssueLabel } from "./validation-issues";

type Props = {
  issues: ValidationIssue[];
};

export function ValidationIssueList({ issues }: Props) {
  const { t } = useTranslation();
  if (!issues.length) return null;
  return (
    <div
      className="rounded-md border border-destructive/40 bg-destructive/5 px-3 py-2 text-sm"
      role="alert"
    >
      <p className="mb-1 font-medium text-destructive">{t("decisionSupport.validation")}</p>
      <ul className="list-disc space-y-1 ps-5">
        {issues.map((issue) => (
          <li key={`${issue.path}-${issue.code}-${issue.message}`}>
            {formatIssueLabel(issue, t)}
          </li>
        ))}
      </ul>
    </div>
  );
}
