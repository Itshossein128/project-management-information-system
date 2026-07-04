import { ROLES } from "@/config/roles";
import { useAuth } from "@/app/contexts/auth-context";

// Function to manage useRoles
export function useRoles(): {
  roles: ROLES[];
  hasRole: (role: ROLES) => boolean;
  hasAnyRole: (roles: readonly ROLES[]) => boolean;
} {
  const { user, hasRole } = useAuth();
  // Function to manage roles
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

// Function to manage usePermission
export function usePermission(): {
  can: (permission: Permission) => boolean;
} {
  const { hasRole } = useAuth();

  // Variable holding isAdmin
  const isAdmin = hasRole(ROLES.ADMIN);
  // Variable holding isHr
  const isHr = hasRole(ROLES.HR);
  // Variable holding isVisitor
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

