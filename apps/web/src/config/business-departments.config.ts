import { PATHS } from "@/app/routeVars";
import type { IconName } from "@/components/icons";
import type { NavigationItem } from "@/types/navigation";

export interface BusinessDepartmentDef {
  slug: string;
  labelI18nKey: string;
  icon: IconName;
}

export const BUSINESS_DEPARTMENTS = [
  {
    slug: PATHS.BUSINESS_DEPT.BUILDINGS,
    labelI18nKey: "nav.deptBuildings",
    icon: "building",
  },
  {
    slug: PATHS.BUSINESS_DEPT.MECHANICAL,
    labelI18nKey: "nav.deptMechanical",
    icon: "wrench",
  },
  {
    slug: PATHS.BUSINESS_DEPT.SECURITY,
    labelI18nKey: "nav.deptSecurity",
    icon: "shield",
  },
  {
    slug: PATHS.BUSINESS_DEPT.MACHINERY,
    labelI18nKey: "nav.deptMachinery",
    icon: "truck",
  },
  {
    slug: PATHS.BUSINESS_DEPT.WAREHOUSE,
    labelI18nKey: "nav.deptWarehouse",
    icon: "warehouse",
  },
  {
    slug: PATHS.BUSINESS_DEPT.ELECTRICAL,
    labelI18nKey: "nav.deptElectrical",
    icon: "bolt",
  },
] as const satisfies readonly BusinessDepartmentDef[];

// Function to manage buildBusinessNavItems
export function buildBusinessNavItems(businessId: string): NavigationItem[] {
  return BUSINESS_DEPARTMENTS.map((dept) => {
    // Variable holding base
    const base = `${PATHS.BUSINESS}/${businessId}/${dept.slug}`;
    return {
      label: dept.slug,
      labelI18nKey: dept.labelI18nKey,
      icon: dept.icon,
      path: base,
      activePathPrefix: base,
    };
  });
}

// Function to manage findDepartmentBySlug
export function findDepartmentBySlug(
  slug: string | undefined,
): (typeof BUSINESS_DEPARTMENTS)[number] | undefined {
  if (!slug) return undefined;
  return BUSINESS_DEPARTMENTS.find((d) => d.slug === slug);
}
