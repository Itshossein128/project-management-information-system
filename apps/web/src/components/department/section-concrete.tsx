import type { CanonicalUnit, UnitReport } from "@/app/lib/api/unit-reports";
import { StructuredSection } from "./section-structured";

export function SectionConcrete({
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
      section="concrete"
      titleKey="businessDepartment.unitReport.sections.concrete.title"
      emptyKey="businessDepartment.unitReport.sections.concrete.empty"
      addKey="businessDepartment.unitReport.sections.concrete.addRow"
      fields={["concrete"]}
    />
  );
}
