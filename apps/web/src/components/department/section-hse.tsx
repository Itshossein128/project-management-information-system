import type { CanonicalUnit, UnitReport } from "@/app/lib/api/unit-reports";
import { StructuredSection } from "./section-structured";

export function SectionHse({
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
      section="hse-incidents"
      titleKey="businessDepartment.unitReport.sections.hse.title"
      emptyKey="businessDepartment.unitReport.sections.hse.empty"
      addKey="businessDepartment.unitReport.sections.hse.addRow"
      fields={["hse"]}
    />
  );
}
