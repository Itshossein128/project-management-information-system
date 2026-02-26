import * as React from "react";
import {
  getStoredUser,
  getStoredAccessToken,
  setStoredAuth,
  clearStoredAuth,
} from "~/lib/auth-storage";
import type { AuthUser, AuthRole } from "~/lib/auth-types";
import { apiJson } from "~/lib/api-client";

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
  hasRole: (role: AuthRole) => boolean;
  restoreSession: () => void;
}

const AuthContext = React.createContext<AuthContextValue | null>(null);

const KNOWN_ROLES: AuthRole[] = ["visitor", "manager", "commentor", "business-setup"];

function normalizeRoles(roles: string[] | undefined): AuthRole[] {
  if (!Array.isArray(roles)) return [];
  return roles.filter((r): r is AuthRole =>
    KNOWN_ROLES.includes(r as AuthRole)
  );
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = React.useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = React.useState(true);

  const restoreSession = React.useCallback(() => {
    const token = getStoredAccessToken();
    const stored = getStoredUser();
    if (token && stored) {
      setUser({ ...stored, roles: normalizeRoles(stored.roles) });
    } else {
      setUser(null);
    }
    setIsLoading(false);
  }, []);

  React.useEffect(() => {
    restoreSession();
  }, [restoreSession]);

  const login = React.useCallback(async (creds: LoginCredentials) => {
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
  }, []);

  const logout = React.useCallback(() => {
    clearStoredAuth();
    setUser(null);
  }, []);

  const hasRole = React.useCallback(
    (role: AuthRole) => (user?.roles ?? []).includes(role),
    [user?.roles]
  );

  const value: AuthContextValue = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    logout,
    hasRole,
    restoreSession,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = React.useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
