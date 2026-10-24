import type { CanonicalUnit, UnitReport } from "@/app/lib/api/unit-reports";
import { StructuredSection } from "./section-structured";

export function SectionVisits({
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
      section="visits"
      titleKey="businessDepartment.unitReport.sections.visits.title"
      emptyKey="businessDepartment.unitReport.sections.visits.empty"
      addKey="businessDepartment.unitReport.sections.visits.addRow"
      fields={["text"]}
    />
  );
}
