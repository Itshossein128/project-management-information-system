import { Button } from "@/components/form";
import { LanguageSwitcher } from "@/components/LanguageSwitcher";
import { Sidebar } from "@/components/navigation/sidebar";
import { useTranslation } from "react-i18next";
import { Outlet, redirect, useNavigate } from "react-router";
import { getAccessTokenFromRequest } from "src/app/lib/auth-storage";
import { useAuth } from "~/contexts/auth-context";

export async function loader({ request }: { request: Request }) {
  const token = getAccessTokenFromRequest(request);
  if (!token) {
    const url = new URL(request.url);
    throw redirect(`/login?redirectTo=${encodeURIComponent(url.pathname)}`);
  }
  return {};
}

export default function ProtectedLayout() {
  const { user, logout, hasRole, isAuthenticated, isLoading } = useAuth();
  const navigate = useNavigate();
  const { t } = useTranslation();
  const displayName =
    user?.full_name ||
    `${user?.first_name ?? ""} ${user?.last_name ?? ""}`.trim() ||
    user?.phone_number ||
    "User";
  function handleLogout() {
    logout();
    navigate("/login", { replace: true });
  }

  return (
    <div className='grid min-h-screen grid-cols-[100px_1fr]'>
      <Sidebar className='row-span-2 min-h-0' />
      <header className='border-b bg-background px-5 py-4'>
        <div className='mx-auto flex items-center justify-between'>
          <h1 className='text-lg font-semibold'>{t("home.headerTitle")}</h1>
          <div className='flex items-center gap-3'>
            <LanguageSwitcher />
            <span className='text-muted-foreground text-sm'>
              {displayName}
              {user?.roles?.length ? (
                <span className='ms-1 text-xs'>({user.roles.join(", ")})</span>
              ) : null}
            </span>
            <Button variant='outline' size='sm' onClick={handleLogout}>
              {t("common.signOut")}
            </Button>
          </div>
        </div>
      </header>
      <div className='col-start-2'>
        <Outlet />
      </div>
    </div>
  );
}
