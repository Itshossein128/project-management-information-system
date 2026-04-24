import { Button } from "@/components/form";
import { LanguageSwitcher } from "@/components/LanguageSwitcher";
import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router";
import { useAuth } from "~/contexts/auth-context";

/**
 * Top bar for the app shell. Sidebar is fixed (Home + HR); it does not reflect
 * the current business or project page.
 */
export function AppShellHeader() {
  const { user, logout } = useAuth();
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
    <header className='border-b bg-background px-5 py-4'>
      <div className='mx-auto flex items-center justify-between'>
        <h1 className='text-lg font-semibold' id='text-appHeaderTitle'>
          {t("home.headerTitle")}
        </h1>
        <div className='flex items-center gap-3'>
          <LanguageSwitcher />
          <span className='text-muted-foreground text-sm' id='text-appHeaderUser'>
            {displayName}
            {user?.roles?.length ? (
              <span className='ms-1 text-xs'>({user.roles.join(", ")})</span>
            ) : null}
          </span>
          <Button
            id='button-appHeaderSignOut'
            variant='outline'
            size='sm'
            onClick={handleLogout}
          >
            {t("common.signOut")}
          </Button>
        </div>
      </div>
    </header>
  );
}
