import { DepartmentPage } from "@/components/department/department-page";
import { PATHS } from "~/routeVars";

export default function BusinessElectricalRoute() {
  return <DepartmentPage slug={PATHS.BUSINESS_DEPT.ELECTRICAL} />;
}
