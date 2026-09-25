import { Loader2 } from "lucide-react";
import { useEffect } from "react";
import { redirect, Outlet, useLocation, useNavigate } from "react-router";
import { QueryClientProvider } from "@tanstack/react-query";
import { useAuth } from "src/app/contexts/auth-context";
import { hasLoaderAuth, hasStoredSession } from "src/app/lib/auth-storage";
import { queryClient } from "src/app/lib/react-query";

export async function loader({ request }: { request: Request }) {
  // Client: localStorage (Request Cookie is often absent on soft navigations).
  // Server: auth_token cookie for SSR document requests.
  if (!hasLoaderAuth(request)) {
    const url = new URL(request.url);
    throw redirect(`/login?redirectTo=${encodeURIComponent(url.pathname)}`);
  }
  return {};
}

export default function AuthLayout() {
  const { isAuthenticated, isLoading } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    if (isLoading) return;
    if (isAuthenticated || hasStoredSession()) return;
    const redirectTo = encodeURIComponent(`${location.pathname}${location.search}`);
    navigate(`/login?redirectTo=${redirectTo}`, { replace: true });
  }, [isAuthenticated, isLoading, location.pathname, location.search, navigate]);

  if (isLoading) {
    return (
      <div className="flex min-h-svh items-center justify-center p-4">
        <Loader2
          className="h-8 w-8 animate-spin text-muted-foreground"
          aria-hidden="true"
        />
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return (
    <QueryClientProvider client={queryClient}>
      <Outlet />
    </QueryClientProvider>
  );
}
