import { AppShell } from "@/components/navigation/app-shell";

/**
 * Main app shell: sidebar + header for business-scoped and admin routes.
 * Auth is enforced by the parent `routes/_auth.tsx` layout.
 */
export default function ProtectedLayout() {
  return <AppShell />;
}
