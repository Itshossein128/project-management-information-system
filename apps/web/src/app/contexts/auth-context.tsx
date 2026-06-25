import { ROLES } from "@/config/roles";
import * as React from "react";
import { apiJson, restoreSessionFromServer } from "src/app/lib/api-client";
import {
  clearStoredAuth,
  getStoredAccessToken,
  getStoredRefreshToken,
  getStoredUser,
  setStoredAuth,
} from "src/app/lib/auth-storage";
import type { AuthUser } from "src/app/lib/auth-types";

interface LoginCredentials {
  phone_number: string;
  password: string;
}

interface AuthApiResponse {
  access: string;
  refresh: string;
  user: AuthUser;
}

interface AuthContextValue {
  user: AuthUser | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (creds: LoginCredentials) => Promise<void>;
  logout: () => Promise<void>;
  hasRole: (role: ROLES) => boolean;
  restoreSession: () => Promise<void>;
}

const AuthContext = React.createContext<AuthContextValue | null>(null);

function normalizeRoles(roles: string[] | undefined): ROLES[] {
  if (!roles) return [];
  const validRoles = Object.values(ROLES);
  return roles.filter((r): r is ROLES => validRoles.includes(r as ROLES));
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = React.useState<AuthUser | null>(() => {
    const token = getStoredAccessToken();
    const stored = getStoredUser();
    if (token && stored) {
      return { ...stored, roles: normalizeRoles(stored.roles) };
    }
    return null;
  });

  const [isLoading, setIsLoading] = React.useState(false);

  const login = React.useCallback(async (creds: LoginCredentials) => {
    setIsLoading(true);
    try {
      const data = await apiJson<AuthApiResponse>("/auth/login/", {
        method: "POST",
        body: JSON.stringify(creds),
      });
      const raw = data.user as AuthUser & { groups?: string[] };
      const userWithRoles: AuthUser = {
        ...data.user,
        roles: normalizeRoles(raw.roles ?? raw.groups ?? []),
      };
      setStoredAuth({ access: data.access, refresh: data.refresh }, userWithRoles);
      setUser(userWithRoles);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const logout = React.useCallback(async () => {
    const refresh = getStoredRefreshToken();
    if (refresh) {
      try {
        await apiJson("/auth/logout/", {
          method: "POST",
          body: JSON.stringify({ refresh }),
        });
      } catch {
        /* ignore */
      }
    }
    clearStoredAuth();
    setUser(null);
  }, []);

  const hasRole = React.useCallback(
    (role: ROLES) => (user?.roles ?? []).includes(role),
    [user?.roles],
  );

  const restoreSession = React.useCallback(async () => {
    const profile = await restoreSessionFromServer();
    if (profile) {
      const withRoles = {
        ...profile,
        roles: normalizeRoles(profile.roles ?? (profile as AuthUser & { groups?: string[] }).groups),
      };
      setUser(withRoles);
      const access = getStoredAccessToken();
      const refresh = getStoredRefreshToken();
      if (access && refresh) {
        setStoredAuth({ access, refresh }, withRoles);
      }
    } else {
      setUser(null);
    }
  }, []);

  React.useEffect(() => {
    if (getStoredAccessToken() && !user) {
      void restoreSession();
    }
  }, [restoreSession, user]);

  const value: AuthContextValue = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    logout,
    hasRole,
    restoreSession,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = React.useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
