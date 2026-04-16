import { useEffect } from "react";
import { Outlet, redirect, useNavigate } from "react-router";
import { useAuth } from "src/app/contexts/auth-context";
import { getAccessTokenFromRequest } from "src/app/lib/auth-storage";

export async function loader({ request }: { request: Request }) {
  const token = getAccessTokenFromRequest(request);
  if (!token) {
    const url = new URL(request.url);
    throw redirect(`/login?redirectTo=${encodeURIComponent(url.pathname)}`);
  }
  return {};
}

export default function BusinessSetupLayout() {
  const { hasRole, isLoading } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (isLoading) return;
    if (!hasRole("business-setup")) {
      navigate("/home", { replace: true });
    }
  }, [isLoading, hasRole, navigate]);

  if (isLoading || !hasRole("business-setup")) {
    return null;
  }

  return <Outlet />;
}
