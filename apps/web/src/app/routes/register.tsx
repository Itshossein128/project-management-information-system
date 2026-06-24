import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Link, useNavigate } from "react-router";
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
import { apiFetch } from "~/lib/api-client";

export default function Register() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    phone_number: "",
    first_name: "",
    last_name: "",
    password: "",
    password_confirm: "",
  });
  const [error, setError] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setFieldErrors({});
    setSubmitting(true);
    try {
      const res = await apiFetch("/auth/register/", {
        method: "POST",
        body: JSON.stringify({
          phone_number: form.phone_number,
          first_name: form.first_name,
          last_name: form.last_name,
          password: form.password,
          password_confirm: form.password_confirm,
        }),
      });
      if (!res.ok) {
        const data = (await res.json().catch(() => ({}))) as Record<
          string,
          string[] | string
        >;
        if (data && typeof data === "object" && !Array.isArray(data)) {
          const next: Record<string, string> = {};
          for (const [k, v] of Object.entries(data)) {
            next[k] = Array.isArray(v) ? (v[0] ?? "") : String(v);
          }
          setFieldErrors(next);
          if (data.error && typeof data.error === "string")
            setError(data.error);
        } else {
          setError(res.statusText || t("register.failed"));
        }
        return;
      }
      navigate("/login", { replace: true });
    } catch (err) {
      setError(err instanceof Error ? err.message : t("register.failed"));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className='flex min-h-svh items-center justify-center p-4'>
      <div className='absolute end-3 top-3 z-10 sm:end-4 sm:top-4'>
        <AppPreferencesBar />
      </div>
      <Card className='w-full max-w-sm'>
        <CardHeader>
          <CardTitle>{t("register.title")}</CardTitle>
          <CardDescription>{t("register.description")}</CardDescription>
        </CardHeader>
        <form onSubmit={handleSubmit}>
          <CardContent className='flex flex-col gap-4'>
            {error && (
              <p className='text-sm text-destructive' role='alert'>
                {error}
              </p>
            )}
            <div className='grid gap-2'>
              <Label htmlFor='reg-phone'>{t("common.phoneNumber")}</Label>
              <Input
                id='reg-phone'
                name='phone_number'
                type='tel'
                autoComplete='tel'
                placeholder='+989123456789'
                value={form.phone_number}
                onChange={(e) =>
                  setForm((f) => ({ ...f, phone_number: e.target.value }))
                }
                required
              />
              {fieldErrors.phone_number && (
                <p className='text-sm text-destructive'>
                  {fieldErrors.phone_number}
                </p>
              )}
            </div>
            <div className='grid grid-cols-1 gap-2 sm:grid-cols-2'>
              <div className='grid gap-2'>
                <Label htmlFor='reg-first'>{t("common.firstName")}</Label>
                <Input
                  id='reg-first'
                  name='first_name'
                  value={form.first_name}
                  onChange={(e) =>
                    setForm((f) => ({ ...f, first_name: e.target.value }))
                  }
                  required
                />
                {fieldErrors.first_name && (
                  <p className='text-sm text-destructive'>
                    {fieldErrors.first_name}
                  </p>
                )}
              </div>
              <div className='grid gap-2'>
                <Label htmlFor='reg-last'>{t("common.lastName")}</Label>
                <Input
                  id='reg-last'
                  name='last_name'
                  value={form.last_name}
                  onChange={(e) =>
                    setForm((f) => ({ ...f, last_name: e.target.value }))
                  }
                  required
                />
                {fieldErrors.last_name && (
                  <p className='text-sm text-destructive'>
                    {fieldErrors.last_name}
                  </p>
                )}
              </div>
            </div>
            <div className='grid gap-2'>
              <Label htmlFor='reg-password'>{t("common.password")}</Label>
              <PasswordInput
                id='reg-password'
                name='password'
                value={form.password}
                onChange={(e) =>
                  setForm((f) => ({ ...f, password: e.target.value }))
                }
                required
              />
              {fieldErrors.password && (
                <p className='text-sm text-destructive'>
                  {fieldErrors.password}
                </p>
              )}
            </div>
            <div className='grid gap-2'>
              <Label htmlFor='reg-password-confirm'>
                {t("common.confirmPassword")}
              </Label>
              <PasswordInput
                id='reg-password-confirm'
                name='password_confirm'
                value={form.password_confirm}
                onChange={(e) =>
                  setForm((f) => ({ ...f, password_confirm: e.target.value }))
                }
                required
              />
              {fieldErrors.password_confirm && (
                <p className='text-sm text-destructive'>
                  {fieldErrors.password_confirm}
                </p>
              )}
            </div>
          </CardContent>
          <CardFooter className='flex flex-col gap-2'>
            <Button type='submit' className='w-full' disabled={submitting}>
              {submitting ? t("register.creating") : t("common.register")}
            </Button>
            <Button type='button' variant='link' asChild>
              <Link to='/login'>
                {t("register.hasAccount")} {t("register.signInLink")}
              </Link>
            </Button>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
}
