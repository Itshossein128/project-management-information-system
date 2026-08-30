import { redirect, Outlet } from "react-router";
import { QueryClientProvider } from "@tanstack/react-query";
import { hasLoaderAuth } from "src/app/lib/auth-storage";
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
  return (
    <QueryClientProvider client={queryClient}>
      <Outlet />
    </QueryClientProvider>
  );
}
