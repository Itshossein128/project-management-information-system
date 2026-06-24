import { DepartmentPage } from "@/components/department/department-page";
import { PATHS } from "~/routeVars";

export default function BusinessMechanicalRoute() {
  return <DepartmentPage slug={PATHS.BUSINESS_DEPT.MECHANICAL} />;
}
