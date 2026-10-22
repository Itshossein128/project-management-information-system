import { Input, TextArea } from "@/components/form";
import { JalaliDatePicker } from "@/components/form/JalaliDatePicker";
import { useTranslation } from "react-i18next";
import { cn } from "@/app/lib/utils";
import {
  type HeaderPayload,
  type InactivityReason,
  type ReportShift,
  type SiteStatus,
  type WeatherCondition,
  INACTIVITY_REASONS,
  WEATHER_META,
} from "@/app/lib/api/daily-reports";
import { WeatherSelector } from "./WeatherSelector";
import { validateTemperatures } from "@/app/lib/temperatureValidation";

export interface HeaderState {
  report_date: string;
  shift: ReportShift;
  work_front: string;
  location_notes: string;
  site_status: SiteStatus;
  inactivity_reason?: InactivityReason | null;
  weather_condition: WeatherCondition | null;
  temp_max: string;
  temp_min: string;
  weather_impact_notes?: string;
  general_notes: string;
}

export function emptyHeaderState(): HeaderState {
  return {
    report_date: new Date().toISOString().slice(0, 10),
    shift: "full",
    work_front: "",
    location_notes: "",
    site_status: "active",
    inactivity_reason: null,
    weather_condition: "clear",
    temp_max: "",
    temp_min: "",
    weather_impact_notes: "",
    general_notes: "",
  };
}

export function headerToPayload(state: HeaderState): HeaderPayload {
  return {
    report_date: state.report_date,
    shift: state.shift,
    work_front: state.work_front,
    location_notes: state.location_notes,
    site_status: state.site_status,
    inactivity_reason: state.inactivity_reason ?? null,
    weather_condition: state.weather_condition,
    temp_max: state.temp_max === "" ? null : state.temp_max,
    temp_min: state.temp_min === "" ? null : state.temp_min,
    weather_impact_notes: state.weather_impact_notes ?? "",
    general_notes: state.general_notes,
  };
}

const SHIFTS: { value: ReportShift; label: string }[] = [
  { value: "day", label: "روز" },
  { value: "night", label: "شب" },
  { value: "full", label: "تمام‌روز" },
];

function Segmented<T extends string>({
  value,
  options,
  onChange,
  disabled,
  label,
}: {
  value: T;
  options: { value: T; label: string }[];
  onChange: (v: T) => void;
  disabled?: boolean;
  label: string;
}) {
  return (
    <div
      role="radiogroup"
      aria-label={label}
      className="inline-flex rounded-lg border border-border p-1"
    >
      {options.map((o) => {
        const selected = value === o.value;
        return (
          <button
            key={o.value}
            type="button"
            role="radio"
            aria-checked={selected}
            disabled={disabled}
            onClick={() => onChange(o.value)}
            className={cn(
              "rounded-md px-3 py-1 text-sm transition",
              selected
                ? "bg-primary text-primary-foreground"
                : "text-muted-foreground hover:bg-muted/40",
            )}
          >
            {o.label}
          </button>
        );
      })}
    </div>
  );
}

export function ReportHeader({
  value,
  onChange,
  readOnly,
}: {
  value: HeaderState;
  onChange: (next: HeaderState) => void;
  readOnly?: boolean;
}) {
  const set = <K extends keyof HeaderState>(key: K, v: HeaderState[K]) =>
    onChange({ ...value, [key]: v });

  const { t } = useTranslation();
  const tempValidation = validateTemperatures(value.temp_min, value.temp_max, { isBlurOrSubmit: false });
  const formatTempError = (code: string | null) => {
    if (!code) return null;
    if (code === "temp_max_must_be_gte_temp_min") {
      return t("errors.temp_max_must_be_gte_temp_min", "دمای بیشینه باید بزرگتر یا مساوی دمای کمینه باشد.");
    }
    if (code === "min_value" || code === "max_value") {
      return t("errors.temp_range", "دما باید بین ۴۰- تا ۶۰+ باشد");
    }
    if (code === "invalid_number") {
      return t("errors.invalid_number", "مقدار دما معتبر نیست");
    }
    return code;
  };
  const tempMinError = formatTempError(tempValidation.tempMinError);
  const tempMaxError = formatTempError(tempValidation.tempMaxError);

  return (
    <div className="space-y-4 rounded-xl border border-border bg-card p-4">
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <JalaliDatePicker
          name="report_date"
          label="تاریخ گزارش"
          value={value.report_date}
          onChange={(iso) => set("report_date", iso)}
          disabled={readOnly}
        />
        <div>
          <p className="mb-1 text-sm text-muted-foreground">شیفت</p>
          <div className="inline-flex h-9 items-center rounded-lg border border-border bg-muted/30 px-3 text-sm font-medium text-foreground">
            تمام‌روز (۲۴ ساعته)
          </div>
        </div>
        <div>
          <p className="mb-1 text-sm text-muted-foreground">وضعیت کارگاه</p>
          <Segmented<SiteStatus>
            label="وضعیت کارگاه"
            value={value.site_status}
            options={[
              { value: "active", label: "فعال" },
              { value: "inactive", label: "تعطیل" },
            ]}
            onChange={(v) => {
              if (v === "active") {
                onChange({ ...value, site_status: v, inactivity_reason: null });
              } else {
                onChange({ ...value, site_status: v });
              }
            }}
            disabled={readOnly}
          />
        </div>
        <div className="flex items-start gap-2">
          <div className="flex-1">
            <label
              htmlFor="report-temp-max"
              className="mb-1 block text-sm text-muted-foreground"
            >
              حداکثر دما
            </label>
            <Input
              id="report-temp-max"
              type="number"
              step="0.1"
              min={-40}
              max={60}
              value={value.temp_max}
              disabled={readOnly}
              onChange={(e) => set("temp_max", e.target.value)}
              aria-invalid={tempMaxError != null || undefined}
              aria-describedby={tempMaxError ? "temp-max-error" : undefined}
            />
            {tempMaxError ? (
              <p id="temp-max-error" role="alert" className="mt-1 text-xs text-destructive">{tempMaxError}</p>
            ) : null}
          </div>
          <div className="flex-1">
            <label
              htmlFor="report-temp-min"
              className="mb-1 block text-sm text-muted-foreground"
            >
              حداقل دما
            </label>
            <Input
              id="report-temp-min"
              type="number"
              step="0.1"
              min={-40}
              max={60}
              value={value.temp_min}
              disabled={readOnly}
              onChange={(e) => set("temp_min", e.target.value)}
              aria-invalid={tempMinError != null || undefined}
              aria-describedby={tempMinError ? "temp-min-error" : undefined}
            />
            {tempMinError ? (
              <p id="temp-min-error" role="alert" className="mt-1 text-xs text-destructive">{tempMinError}</p>
            ) : null}
          </div>
        </div>
      </div>

      {value.site_status === "inactive" ? (
        <div>
          <label htmlFor="report-inactivity-reason" className="mb-1 block text-sm text-muted-foreground">
            {t("dailyReports.inactivityReason", "علت تعطیلی کارگاه")} <span className="text-destructive">*</span>
          </label>
          <select
            id="report-inactivity-reason"
            className="w-full rounded-md border border-border bg-background p-2 text-sm"
            value={value.inactivity_reason ?? ""}
            disabled={readOnly}
            onChange={(e) =>
              set("inactivity_reason", (e.target.value || null) as InactivityReason | null)
            }
          >
            <option value="">{t("dailyReports.selectInactivityReason", "-- انتخاب علت تعطیلی --")}</option>
            {INACTIVITY_REASONS.map((r) => (
              <option key={r.value} value={r.value}>
                {t(`dailyReports.inactivityReasons.${r.value}`, r.label)}
              </option>
            ))}
          </select>
        </div>
      ) : null}

      <div className="grid gap-4 sm:grid-cols-2">
        <div>
          <label htmlFor="report-work-front" className="mb-1 block text-sm text-muted-foreground">
            محل / جبهه کاری
          </label>
          <Input
            id="report-work-front"
            name="work_front"
            value={value.work_front}
            disabled={readOnly}
            onChange={(e) => set("work_front", e.target.value)}
          />
        </div>
        <div>
          <label htmlFor="report-location-notes" className="mb-1 block text-sm text-muted-foreground">
            توضیح محل
          </label>
          <Input
            id="report-location-notes"
            name="location_notes"
            value={value.location_notes}
            disabled={readOnly}
            onChange={(e) => set("location_notes", e.target.value)}
          />
        </div>
      </div>

      <div>
        <p className="mb-1 text-sm text-muted-foreground" id="weather-label">
          وضعیت جوی
        </p>
        <WeatherSelector
          value={value.weather_condition}
          onChange={(w) => set("weather_condition", w)}
          disabled={readOnly}
          id="header-weather"
        />
      </div>

      <TextArea
        name="weather_impact_notes"
        label={t("dailyReports.weatherImpactNotes", t("weatherImpactNotes", "توضیحات و اثرات شرایط جوی"))}
        placeholder={t("dailyReports.weatherImpactNotesPlaceholder", "توضیح اثر شرایط جوی بر روند پیشرفت کارگاه...")}
        dir="auto"
        rows={2}
        value={value.weather_impact_notes ?? ""}
        disabled={readOnly}
        onChange={(e) => set("weather_impact_notes", e.target.value)}
      />

      <TextArea
        name="general_notes"
        label="توضیحات کلی"
        rows={3}
        value={value.general_notes}
        disabled={readOnly}
        onChange={(e) => set("general_notes", e.target.value)}
      />
    </div>
  );
}
