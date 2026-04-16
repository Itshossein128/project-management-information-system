import { navigation } from "@/config/navigation.config";
import type { ROLES } from "@/config/roles";

export function useNavigation(roles: ROLES[] | undefined) {
  return navigation.filter((item) => {
    if (!item.roles) return true;
    if (!roles) return false;

    return roles.some((role) => item.roles!.includes(role));
  });
}
