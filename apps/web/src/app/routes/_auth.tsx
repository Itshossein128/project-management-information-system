import { redirect, Outlet } from "react-router";
import { QueryClientProvider } from "@tanstack/react-query";
import { getAccessTokenFromRequest } from "src/app/lib/auth-storage";
import { queryClient } from "src/app/lib/react-query";

export async function loader({ request }: { request: Request }) {
  // Variable holding token
  const token = getAccessTokenFromRequest(request);
  if (!token) {
    // Variable holding url
    const url = new URL(request.url);
    throw redirect(`/login?redirectTo=${encodeURIComponent(url.pathname)}`);
  }
  return {};
}

export default function AuthLayout() {
  return (
    <QueryClientProvider client={queryClient}>
      <Outlet />
    </QueryClientProvider>
  );
}
