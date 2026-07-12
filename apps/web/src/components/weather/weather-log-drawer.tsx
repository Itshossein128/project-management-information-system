import { useEffect, useState } from "react";
import { Field, Input, JalaliDatePicker, Select } from "@/components/form";
import {
  WEATHER_CONDITIONS,
  formToPayload,
  type WeatherLog,
  type WeatherLogFormInput,
} from "@/app/lib/api/weather";
import { jalaliToIso } from "@/app/lib/jalali-utils";
import { Drawer } from "@/components/ui/drawer";
import { Button } from "@/components/ui/sprint-button";

const EMPTY_FORM: WeatherLogFormInput = {
  log_date_iso: "",
  temp_max: "",
  temp_min: "",
  weather_condition: "sunny",
  site_status: "active",
};

function logToForm(log: WeatherLog): WeatherLogFormInput {
  return {
    log_date_iso: jalaliToIso(log.log_date),
    temp_max: log.temp_max ?? "",
    temp_min: log.temp_min ?? "",
    weather_condition: log.weather_condition,
    site_status: log.site_status,
  };
}

export interface WeatherLogDrawerProps {
  open: boolean;
  onClose: () => void;
  initial?: WeatherLog | null;
  presetDateIso?: string;
  onSubmit: (form: WeatherLogFormInput) => Promise<void>;
  loading?: boolean;
}

export function WeatherLogDrawer({
  open,
  onClose,
  initial,
  presetDateIso,
  onSubmit,
  loading,
}: WeatherLogDrawerProps) {
  const [form, setForm] = useState<WeatherLogFormInput>(EMPTY_FORM);
  const [errors, setErrors] = useState<Partial<Record<keyof WeatherLogFormInput, string>>>({});

  useEffect(() => {
    if (!open) return;
    if (initial) {
      setForm(logToForm(initial));
    } else {
      setForm({ ...EMPTY_FORM, log_date_iso: presetDateIso ?? "" });
    }
    setErrors({});
  }, [open, initial, presetDateIso]);

  const validate = (): boolean => {
    const next: Partial<Record<keyof WeatherLogFormInput, string>> = {};
    if (!form.log_date_iso) next.log_date_iso = "تاریخ الزامی است";
    const max = form.temp_max.trim() ? Number(form.temp_max) : null;
    const min = form.temp_min.trim() ? Number(form.temp_min) : null;
    if (max !== null && Number.isNaN(max)) next.temp_max = "مقدار نامعتبر";
    if (min !== null && Number.isNaN(min)) next.temp_min = "مقدار نامعتبر";
    if (max !== null && min !== null && min > max) {
      next.temp_min = "حداقل دما نمی‌تواند بیشتر از حداکثر باشد";
    }
    setErrors(next);
    return Object.keys(next).length === 0;
  };

  const handleSubmit = async () => {
    if (!validate()) return;
    await onSubmit(form);
  };

  return (
    <Drawer
      isOpen={open}
      onClose={onClose}
      title={initial ? "ویرایش گزارش جوی" : "ثبت گزارش جوی"}
      footer={
        <div className="flex justify-end gap-2">
          <Button variant="secondary" onClick={onClose} disabled={loading}>
            لغو
          </Button>
          <Button variant="primary" loading={loading} onClick={() => void handleSubmit()}>
            ذخیره
          </Button>
        </div>
      }
    >
      <div className="space-y-4">
        <JalaliDatePicker
          name="log_date"
          label="تاریخ"
          required
          value={form.log_date_iso}
          onChange={(v) => setForm((f) => ({ ...f, log_date_iso: v }))}
          error={errors.log_date_iso}
        />
        <Field name="temp_max" label="حداکثر دما" error={errors.temp_max} htmlFor="weather-temp-max">
          {() => (
            <Input
              id="weather-temp-max"
              name="temp_max"
              type="number"
              step="0.1"
              value={form.temp_max}
              onChange={(e) => setForm((f) => ({ ...f, temp_max: e.target.value }))}
              aria-invalid={errors.temp_max != null || undefined}
            />
          )}
        </Field>
        <Field name="temp_min" label="حداقل دما" error={errors.temp_min} htmlFor="weather-temp-min">
          {() => (
            <Input
              id="weather-temp-min"
              name="temp_min"
              type="number"
              step="0.1"
              value={form.temp_min}
              onChange={(e) => setForm((f) => ({ ...f, temp_min: e.target.value }))}
              aria-invalid={errors.temp_min != null || undefined}
            />
          )}
        </Field>
        <Select
          name="weather_condition"
          label="وضعیت جوی"
          value={form.weather_condition}
          onChange={(e) =>
            setForm((f) => ({
              ...f,
              weather_condition: e.target.value as WeatherLogFormInput["weather_condition"],
            }))
          }
          options={WEATHER_CONDITIONS.map((c) => ({ value: c.value, label: c.label }))}
        />
        <Select
          name="site_status"
          label="وضعیت کارگاه"
          value={form.site_status}
          onChange={(e) =>
            setForm((f) => ({
              ...f,
              site_status: e.target.value as WeatherLogFormInput["site_status"],
            }))
          }
          options={[
            { value: "active", label: "فعال" },
            { value: "inactive", label: "غیرفعال" },
          ]}
        />
      </div>
    </Drawer>
  );
}

export { formToPayload };
