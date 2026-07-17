import { Input, TextArea } from "@/components/form";
import { JalaliDatePicker } from "@/components/form/JalaliDatePicker";
import { cn } from "@/app/lib/utils";
import {
  type HeaderPayload,
  type ReportShift,
  type SiteStatus,
  type WeatherCondition,
  WEATHER_META,
} from "@/app/lib/api/daily-reports";

export interface HeaderState {
  report_date: string;
  shift: ReportShift;
  site_status: SiteStatus;
  weather_condition: WeatherCondition | null;
  temp_max: string;
  temp_min: string;
  general_notes: string;
}

export function emptyHeaderState(): HeaderState {
  return {
    report_date: new Date().toISOString().slice(0, 10),
    shift: "full",
    site_status: "active",
    weather_condition: "sunny",
    temp_max: "",
    temp_min: "",
    general_notes: "",
  };
}

export function headerToPayload(state: HeaderState): HeaderPayload {
  return {
    report_date: state.report_date,
    shift: state.shift,
    site_status: state.site_status,
    weather_condition: state.weather_condition,
    temp_max: state.temp_max === "" ? null : state.temp_max,
    temp_min: state.temp_min === "" ? null : state.temp_min,
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
          <Segmented
            label="شیفت"
            value={value.shift}
            options={SHIFTS}
            onChange={(v) => set("shift", v)}
            disabled={readOnly}
          />
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
            onChange={(v) => set("site_status", v)}
            disabled={readOnly}
          />
        </div>
        <div className="flex items-end gap-2">
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
              value={value.temp_max}
              disabled={readOnly}
              onChange={(e) => set("temp_max", e.target.value)}
            />
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
              value={value.temp_min}
              disabled={readOnly}
              onChange={(e) => set("temp_min", e.target.value)}
            />
          </div>
        </div>
      </div>

      <div>
        <p className="mb-1 text-sm text-muted-foreground" id="weather-label">
          وضعیت جوی
        </p>
        <div
          role="radiogroup"
          aria-labelledby="weather-label"
          className="flex flex-wrap gap-2"
        >
          {(Object.keys(WEATHER_META) as WeatherCondition[]).map((w) => {
            const selected = value.weather_condition === w;
            return (
              <button
                key={w}
                type="button"
                role="radio"
                aria-checked={selected}
                aria-label={WEATHER_META[w].label}
                disabled={readOnly}
                onClick={() => set("weather_condition", w)}
                className={cn(
                  "rounded-full border px-3 py-1 text-sm transition",
                  selected
                    ? "border-primary bg-primary/10 text-primary"
                    : "border-border text-muted-foreground hover:bg-muted/40",
                )}
              >
                <span className="me-1" aria-hidden>
                  {WEATHER_META[w].icon}
                </span>
                {WEATHER_META[w].label}
              </button>
            );
          })}
        </div>
      </div>

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
