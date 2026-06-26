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
} from "@/components/form";
import { AppPreferencesBar } from "@/components/AppPreferencesBar";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Loader2 } from "lucide-react";
import { Link } from "react-router";
import { apiFetch } from "~/lib/api-client";

export default function ForgotPassword() {
  const { t } = useTranslation();
  const [phoneNumber, setPhoneNumber] = useState("");
  const [sent, setSent] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      const res = await apiFetch("/auth/forgot-password/", {
        method: "POST",
        body: JSON.stringify({ phone_number: phoneNumber }),
      });
      if (!res.ok) {
        const data = (await res.json().catch(() => ({}))) as {
          phone_number?: string[];
        };
        setError(
          data.phone_number?.[0] ??
            res.statusText ??
            t("forgotPassword.failed"),
        );
        return;
      }
      setSent(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : t("forgotPassword.failed"));
    } finally {
      setSubmitting(false);
    }
  }

  if (sent) {
    return (
      <div className='flex min-h-svh items-center justify-center p-4'>
        <div className='absolute end-3 top-3 z-10 sm:end-4 sm:top-4'>
          <AppPreferencesBar />
        </div>
        <Card className='w-full max-w-sm'>
          <CardHeader>
            <CardTitle>{t("forgotPassword.checkEmail")}</CardTitle>
            <CardDescription>
              {t("forgotPassword.emailSent", { email: phoneNumber })}
            </CardDescription>
          </CardHeader>
          <CardFooter>
            <Button asChild>
              <Link to='/login'>{t("forgotPassword.backToSignIn")}</Link>
            </Button>
          </CardFooter>
        </Card>
      </div>
    );
  }

  return (
    <div className='flex min-h-svh items-center justify-center p-4'>
      <div className='absolute end-3 top-3 z-10 sm:end-4 sm:top-4'>
        <AppPreferencesBar />
      </div>
      <Card className='w-full max-w-sm'>
        <CardHeader>
          <CardTitle>{t("forgotPassword.title")}</CardTitle>
          <CardDescription>{t("forgotPassword.description")}</CardDescription>
        </CardHeader>
        <form onSubmit={handleSubmit}>
          <CardContent className='flex flex-col gap-4'>
            {error && (
              <p className='text-sm text-destructive' role='alert'>
                {error}
              </p>
            )}
            <div className='grid gap-2'>
              <Label htmlFor='forgot-phone'>{t("common.phoneNumber")}</Label>
              <Input
                id='forgot-phone'
                name='phone_number'
                type='tel'
                autoComplete='tel'
                placeholder='+989123456789'
                value={phoneNumber}
                onChange={(e) => setPhoneNumber(e.target.value)}
                required
              />
            </div>
          </CardContent>
          <CardFooter className='flex flex-col gap-2'>
            <Button type='submit' className='w-full' disabled={submitting}>
              {submitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" aria-hidden="true" />}
              {submitting
                ? t("forgotPassword.sending")
                : t("forgotPassword.sendLink")}
            </Button>
            <Button type='button' variant='link' asChild>
              <Link to='/login'>{t("forgotPassword.backToSignIn")}</Link>
            </Button>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
}
