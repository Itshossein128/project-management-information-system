import { Outlet, redirect, useNavigate } from "react-router";
import { useEffect } from "react";
import { getAccessTokenFromRequest } from "~/lib/auth-storage";
import { useAuth } from "~/contexts/auth-context";

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
