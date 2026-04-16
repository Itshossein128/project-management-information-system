import {
  Button,
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
  Label,
  PasswordInput,
} from "@/components/form";
import { LanguageSwitcher } from "@/components/LanguageSwitcher";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Link, useSearchParams } from "react-router";
import { apiFetch } from "src/app/lib/api-client";

export default function ResetPassword() {
  const { t } = useTranslation();
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token") ?? "";

  const [password, setPassword] = useState("");
  const [passwordConfirm, setPasswordConfirm] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    if (password !== passwordConfirm) {
      setError(t("resetPassword.passwordsMismatch"));
      return;
    }
    if (!token) {
      setError(t("resetPassword.missingToken"));
      return;
    }
    setSubmitting(true);
    try {
      const res = await apiFetch("/auth/reset-password/", {
        method: "POST",
        body: JSON.stringify({
          token,
          new_password: password,
          new_password_confirm: passwordConfirm,
        }),
      });
      if (!res.ok) {
        const data = (await res.json().catch(() => ({}))) as { error?: string };
        setError(data.error ?? res.statusText ?? t("resetPassword.failed"));
        return;
      }
      setSuccess(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : t("resetPassword.failed"));
    } finally {
      setSubmitting(false);
    }
  }

  if (success) {
    return (
      <div className='flex min-h-svh items-center justify-center p-4'>
        <div className='absolute top-4 end-4'>
          <LanguageSwitcher />
        </div>
        <Card className='w-full max-w-sm'>
          <CardHeader>
            <CardTitle>{t("resetPassword.successTitle")}</CardTitle>
            <CardDescription>
              {t("resetPassword.successMessage")}
            </CardDescription>
          </CardHeader>
          <CardFooter>
            <Button asChild>
              <Link to='/login'>{t("common.signIn")}</Link>
            </Button>
          </CardFooter>
        </Card>
      </div>
    );
  }

  return (
    <div className='flex min-h-svh items-center justify-center p-4'>
      <div className='absolute top-4 end-4'>
        <LanguageSwitcher />
      </div>
      <Card className='w-full max-w-sm'>
        <CardHeader>
          <CardTitle>{t("resetPassword.title")}</CardTitle>
          <CardDescription>{t("resetPassword.description")}</CardDescription>
        </CardHeader>
        <form onSubmit={handleSubmit}>
          <CardContent className='flex flex-col gap-4'>
            {error && (
              <p className='text-sm text-destructive' role='alert'>
                {error}
              </p>
            )}
            <div className='grid gap-2'>
              <Label htmlFor='reset-password'>{t("common.newPassword")}</Label>
              <PasswordInput
                id='reset-password'
                name='new_password'
                autoComplete='new-password'
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
            <div className='grid gap-2'>
              <Label htmlFor='reset-password-confirm'>
                {t("common.confirmNewPassword")}
              </Label>
              <PasswordInput
                id='reset-password-confirm'
                name='new_password_confirm'
                autoComplete='new-password'
                value={passwordConfirm}
                onChange={(e) => setPasswordConfirm(e.target.value)}
                required
              />
            </div>
          </CardContent>
          <CardFooter className='flex flex-col gap-2'>
            <Button type='submit' className='w-full' disabled={submitting}>
              {submitting
                ? t("resetPassword.updating")
                : t("resetPassword.updatePassword")}
            </Button>
            <Button type='button' variant='link' asChild>
              <Link to='/login'>{t("resetPassword.backToSignIn")}</Link>
            </Button>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
}
