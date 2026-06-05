import { ThemeSync } from "@/components/ThemeSync";
import { useTranslation } from "react-i18next";
import {
  isRouteErrorResponse,
  Links,
  Meta,
  Outlet,
  Scripts,
  ScrollRestoration,
} from "react-router";
import type { Route } from "./+types/root";
import "./app.css";
import { AuthProvider } from "./contexts/auth-context";
import "./lib/i18n";
import { isRTL } from "./lib/i18n";

const themeInitScript = `(function(){try{var t=localStorage.getItem("app-theme");var d=t==="dark";document.documentElement.classList.toggle("dark",d);document.documentElement.style.colorScheme=d?"dark":"light";}catch(e){}})();`;

export function Layout({ children }: { children: React.ReactNode }) {
  const { i18n } = useTranslation();
  const dir = isRTL(i18n.language) ? "rtl" : "ltr";

  return (
    <html lang={i18n.language} dir={dir} suppressHydrationWarning>
      <head>
        <meta charSet='utf-8' />
        <meta name='viewport' content='width=device-width, initial-scale=1' />
        <script dangerouslySetInnerHTML={{ __html: themeInitScript }} />
        <Meta />
        <Links />
      </head>
      <body>
        {children}
        <ScrollRestoration />
        <Scripts />
      </body>
    </html>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <ThemeSync />
      <Outlet />
    </AuthProvider>
  );
}

export function ErrorBoundary({ error }: Route.ErrorBoundaryProps) {
  const { t } = useTranslation();
  let message = t("error.oops");
  let details = t("error.unexpected");
  let stack: string | undefined;

  if (isRouteErrorResponse(error)) {
    message =
      error.status === 404 ? t("error.notFound") : t("error.genericTitle");
    details =
      error.status === 404
        ? t("error.pageNotFound")
        : error.statusText || details;
  } else if (import.meta.env.DEV && error && error instanceof Error) {
    details = error.message;
    stack = error.stack;
  }

  return (
    <main className='pt-16 p-4 container mx-auto'>
      <h1>{message}</h1>
      <p>{details}</p>
      {stack && (
        <pre className='w-full p-4 overflow-x-auto'>
          <code>{stack}</code>
        </pre>
      )}
    </main>
  );
}
