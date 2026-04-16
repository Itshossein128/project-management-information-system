import { ROLES } from "@/config/roles";
import * as React from "react";
import { apiJson } from "src/app/lib/api-client";
import {
  clearStoredAuth,
  getStoredAccessToken,
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
  logout: () => void;
  hasRole: (role: ROLES) => boolean;
  restoreSession: () => void;
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

    const data = await apiJson<AuthApiResponse>("/auth/login/", {
      method: "POST",
      body: JSON.stringify(creds),
    });

    const raw = data.user as AuthUser & { groups?: string[] };

    const userWithRoles: AuthUser = {
      ...data.user,
      roles: normalizeRoles(raw.roles ?? raw.groups ?? []),
    };

    setStoredAuth(
      { access: data.access, refresh: data.refresh },
      userWithRoles,
    );

    setUser(userWithRoles);
    setIsLoading(false);
  }, []);

  const logout = React.useCallback(() => {
    clearStoredAuth();
    setUser(null);
  }, []);

  const hasRole = React.useCallback(
    (role: ROLES) => (user?.roles ?? []).includes(role),
    [user?.roles],
  );

  const value: AuthContextValue = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    logout,
    hasRole,
    restoreSession: () => {},
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = React.useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
