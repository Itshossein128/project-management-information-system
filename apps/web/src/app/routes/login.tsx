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
        <div className='animate-aurora absolute -end-32 -top-32 h-96 w-96 rounded-full bg-brand-500/25 blur-3xl' />
        <div className='animate-aurora absolute -bottom-32 -start-32 h-[26rem] w-[26rem] rounded-full bg-gold-500/20 blur-3xl [animation-delay:-6s]' />
        <div className='animate-float absolute start-1/2 top-1/3 h-72 w-72 -translate-x-1/2 rounded-full bg-brand-400/10 blur-3xl' />
        <div className='absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-background/70' />
      </div>
      <div className='absolute end-3 top-3 z-10 sm:end-4 sm:top-4'>
        <AppPreferencesBar />
      </div>
      <Card className='animate-scale-in w-full max-w-md border-border/50 shadow-[var(--shadow-xl)] backdrop-blur-sm'>
        <CardHeader className='justify-items-center text-center'>
          <div
            aria-hidden='true'
            className='animate-float mb-3 flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-brand-400 via-brand-600 to-brand-700 text-xl font-bold tracking-tight text-white shadow-[var(--shadow-glow)] ring-1 ring-white/20'
          >
            BM
          </div>
          <CardTitle className='text-2xl font-bold tracking-tight'>{t("login.title")}</CardTitle>
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
