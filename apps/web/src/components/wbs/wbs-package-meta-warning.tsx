import { useTranslation } from "react-i18next";
import type { WBSFlatNode } from "@/app/lib/api/wbs";

export function isIncompleteWorkPackage(node: {
  responsible?: string | null;
  acceptance_criteria?: string;
}): boolean {
  const missingResponsible = !node.responsible;
  const missingAcceptance = !(node.acceptance_criteria ?? "").trim();
  return missingResponsible || missingAcceptance;
}

/** Non-blocking soft-warn for progress/budget when package metadata is incomplete (T036). */
export function WbsPackageMetaWarning({
  nodes,
  testId = "wbs-package-meta-warning",
}: {
  nodes: Pick<WBSFlatNode, "wbs_code" | "wbs_name" | "responsible" | "acceptance_criteria">[];
  testId?: string;
}) {
  const { t } = useTranslation();
  const incomplete = nodes.filter(isIncompleteWorkPackage);
  if (incomplete.length === 0) return null;

  const preview = incomplete
    .slice(0, 3)
    .map((n) => n.wbs_code)
    .join(", ");
  const more =
    incomplete.length > 3
      ? t("wbs.packageMetaMore", { count: incomplete.length - 3 })
      : "";

  return (
    <p
      className="rounded-md border border-warning-200 bg-warning-50 px-3 py-2 text-sm text-warning-900 dark:border-warning-800 dark:bg-warning-950/40 dark:text-warning-100"
      data-testid={testId}
    >
      {t("wbs.packageMetaWarning", { codes: preview, more })}
    </p>
  );
}
