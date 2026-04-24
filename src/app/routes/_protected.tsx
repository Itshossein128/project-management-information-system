import { AppShellHeader } from "@/components/navigation/app-shell-header";
import { Sidebar } from "@/components/navigation/sidebar";
import { Outlet } from "react-router";

/**
 * Main app shell: sidebar + header for business-scoped and admin routes.
 * Auth is enforced by the parent `routes/_auth.tsx` layout.
 */
export default function ProtectedLayout() {
  return (
    <div className='grid min-h-screen grid-cols-[100px_1fr] grid-rows-[min-content_1fr]'>
      <Sidebar className='row-span-2 min-h-0' />
      <AppShellHeader />
      <div className='col-start-2'>
        <Outlet />
      </div>
    </div>
  );
}
