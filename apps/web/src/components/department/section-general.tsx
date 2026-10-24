import type { CanonicalUnit, UnitReport } from "@/app/lib/api/unit-reports";
import { StructuredSection } from "./section-structured";

export function SectionGeneral({
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
      section="general-activities"
      titleKey="businessDepartment.unitReport.sections.general.title"
      emptyKey="businessDepartment.unitReport.sections.general.empty"
      addKey="businessDepartment.unitReport.sections.general.addRow"
      fields={["description"]}
    />
  );
}
