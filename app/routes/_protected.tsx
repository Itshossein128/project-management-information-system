import { Outlet, redirect } from "react-router";
import { getAccessTokenFromRequest } from "~/lib/auth-storage";

export async function loader({ request }: { request: Request }) {
  const token = getAccessTokenFromRequest(request);
  if (!token) {
    const url = new URL(request.url);
    throw redirect(`/login?redirectTo=${encodeURIComponent(url.pathname)}`);
  }
  return {};
}

export default function ProtectedLayout() {
  return <Outlet />;
}
