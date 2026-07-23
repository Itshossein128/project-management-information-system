import {
  Button,
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
  Input,
  Label,
  PasswordInput,
} from "@/components/form";
import { AppPreferencesBar } from "@/components/AppPreferencesBar";
import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { Loader2 } from "lucide-react";
import { redirect, useNavigate, useSearchParams } from "react-router";
import { useAuth } from "src/app/contexts/auth-context";
import { getAccessTokenFromRequest } from "src/app/lib/auth-storage";

export async function loader({ request }: { request: Request }) {
  if (typeof window === "undefined" && getAccessTokenFromRequest(request)) {
    throw redirect("/home");
  }
  return {};
}

export default function Login() {
  const { t } = useTranslation();
  const { login, isAuthenticated, isLoading } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const redirectTo = searchParams.get("redirectTo") ?? "/home";
  const [phoneNumber, setPhoneNumber] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      navigate(redirectTo, { replace: true });
    }
  }, [isLoading, isAuthenticated, navigate, redirectTo]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await login({ phone_number: phoneNumber, password });
    } catch (err) {
      setError(err instanceof Error ? err.message : t("login.failed"));
      setSubmitting(false);
    }
  }

  const busy = submitting || isLoading;

  if (isAuthenticated) {
    return (
      <div className='flex min-h-svh items-center justify-center p-4'>
        <Loader2
          className='h-8 w-8 animate-spin text-muted-foreground'
          aria-hidden='true'
        />
        <span className='sr-only'>{t("login.signingIn")}</span>
      </div>
    );
  }

  return (
    <div className='relative flex min-h-svh items-center justify-center overflow-hidden bg-background p-4'>
      <div aria-hidden='true' className='pointer-events-none absolute inset-0 -z-10'>
        <div className='absolute -end-24 -top-24 h-72 w-72 rounded-full bg-brand-500/20 blur-3xl' />
        <div className='absolute -bottom-24 -start-24 h-80 w-80 rounded-full bg-safety-500/25 blur-3xl' />
        <div className='absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-background/60' />
      </div>
      <div className='absolute end-3 top-3 z-10 sm:end-4 sm:top-4'>
        <AppPreferencesBar />
      </div>
      <Card className='w-full max-w-md border-border/60 shadow-lg'>
        <CardHeader className='justify-items-center text-center'>
          <div
            aria-hidden='true'
            className='mb-3 flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-brand-600 via-brand-700 to-safety-600 text-lg font-bold tracking-tight text-white shadow-md'
          >
            BM
          </div>
          <CardTitle className='text-xl'>{t("login.title")}</CardTitle>
          <CardDescription>{t("login.description")}</CardDescription>
        </CardHeader>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSubmit(e);
          }}
        >
          <CardContent className='flex flex-col gap-4'>
            {error && (
              <p className='text-sm text-destructive' role='alert' data-testid='login-global-error'>
                {error}
              </p>
            )}
            <div className='grid gap-2'>
              <Label htmlFor='login-phone'>{t("common.phoneNumber")}</Label>
              <Input
                id='login-phone' data-testid='login-phone-input'
                name='phone_number'
                type='tel'
                autoComplete='tel'
                placeholder={t("login.phonePlaceholder")}
                value={phoneNumber}
                onChange={(e) => setPhoneNumber(e.target.value)}
                required
              />
            </div>
            <div className='grid gap-2'>
              <Label htmlFor='login-password'>{t("common.password")}</Label>
              <PasswordInput
                id='login-password' data-testid='login-password-input'
                name='password'
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
          </CardContent>
          <CardFooter className='flex flex-col gap-2 mt-6'>
            <Button type='submit' data-testid='login-submit-btn' className='w-full' disabled={busy}>
              {busy && (
                <Loader2 className='h-4 w-4 animate-spin' aria-hidden='true' />
              )}
              {busy ? t("login.signingIn") : t("common.signIn")}
            </Button>
            <Button
              type='button'
              variant='link'
              className='text-sm'
              onClick={() => navigate("/register")}
            >
              {t("login.noAccount")} {t("login.registerLink")}
            </Button>
            <Button
              type='button'
              variant='link'
              className='text-sm'
              onClick={() => navigate("/forgot-password")}
            >
              {t("login.forgotPassword")}
            </Button>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
}
