import type { CanonicalUnit, UnitReport } from "@/app/lib/api/unit-reports";
import { StructuredSection } from "./section-structured";

export function SectionIssues({
  businessId,
  unit,
  report,
}: {
  businessId: string;
  unit: CanonicalUnit;
  report: UnitReport;
}) {
  return (
    <StructuredSection
      businessId={businessId}
      unit={unit}
      report={report}
      section="issues"
      titleKey="businessDepartment.unitReport.sections.issues.title"
      emptyKey="businessDepartment.unitReport.sections.issues.empty"
      addKey="businessDepartment.unitReport.sections.issues.addRow"
      fields={["barrier"]}
    />
  );
}
