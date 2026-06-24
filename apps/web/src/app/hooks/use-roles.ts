import { ROLES } from "@/config/roles";
import { useAuth } from "@/app/contexts/auth-context";

export function useRoles(): {
  roles: ROLES[];
  hasRole: (role: ROLES) => boolean;
  hasAnyRole: (roles: readonly ROLES[]) => boolean;
} {
  const { user, hasRole } = useAuth();
  const roles = (user?.roles ?? []) as ROLES[];

  return {
    roles,
    hasRole,
    hasAnyRole: (rs) => rs.some((r) => hasRole(r)),
  };
}

export type Permission =
  | "assignments:read"
  | "assignments:write"
  | "job-positions:read"
  | "job-positions:write"
  | "users:read";

export function usePermission(): {
  can: (permission: Permission) => boolean;
} {
  const { hasRole } = useAuth();

  const isAdmin = hasRole(ROLES.ADMIN);
  const isHr = hasRole(ROLES.HR);
  const isVisitor = hasRole(ROLES.VISITOR);

  return {
    can: (permission) => {
      if (isAdmin) return true;
      if (isVisitor) {
        return (
          permission === "assignments:read" ||
          permission === "job-positions:read" ||
          permission === "users:read"
        );
      }

      switch (permission) {
        case "users:read":
          return isHr;
        case "assignments:read":
        case "assignments:write":
        case "job-positions:read":
        case "job-positions:write":
          return isHr;
        default:
          return false;
      }
    },
  };
}

