import { navigation } from "@/config/navigation.config";
import type { ROLES } from "@/config/roles";
import type { NavigationItem } from "@/types/navigation";

export function useNavigation(roles: ROLES[] | undefined): NavigationItem[] {
  return navigation.filter((item) => {
    if (!item.roles) return true;
    if (!roles) return false;

    return roles.some((role) => item.roles!.includes(role));
  });
}
