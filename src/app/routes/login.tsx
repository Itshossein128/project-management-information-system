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
import { LanguageSwitcher } from "@/components/LanguageSwitcher";
import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
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
  console.log("isLoading", isLoading);
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
    console.log("fired");
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await login({ phone_number: phoneNumber, password });
    } catch (err) {
      console.log("injas");
      setError(err instanceof Error ? err.message : t("login.failed"));
      setSubmitting(false);
    }
  }

  if (isLoading) {
    return null;
  }

  if (isAuthenticated) {
    return null;
  }

  return (
    <div className='flex min-h-svh items-center justify-center p-4'>
      <div className='absolute top-4 end-4'>
        <LanguageSwitcher />
      </div>
      <Card className='w-full max-w-sm'>
        <CardHeader>
          <CardTitle>{t("login.title")}</CardTitle>
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
              <p className='text-sm text-destructive' role='alert'>
                {error}
              </p>
            )}
            <div className='grid gap-2'>
              <Label htmlFor='login-phone'>{t("common.phoneNumber")}</Label>
              <Input
                id='login-phone'
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
                id='login-password'
                name='password'
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
          </CardContent>
          <CardFooter className='flex flex-col gap-2 mt-6'>
            <Button type='submit' className='w-full' disabled={submitting}>
              {submitting ? t("login.signingIn") : t("common.signIn")}
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
