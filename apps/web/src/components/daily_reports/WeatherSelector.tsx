import React from "react";
import { useTranslation } from "react-i18next";
import { type WeatherCondition, WEATHER_META } from "@/app/lib/api/daily-reports";
import { cn } from "@/app/lib/utils";

export const ORDERED_WEATHER_CONDITIONS: WeatherCondition[] = [
  "clear",
  "cloudy",
  "rainy",
  "snowy",
  "stormy",
];

interface WeatherSelectorProps {
  value: WeatherCondition | null;
  onChange: (value: WeatherCondition) => void;
  disabled?: boolean;
  className?: string;
  id?: string;
}

export function WeatherSelector({
  value,
  onChange,
  disabled = false,
  className,
  id = "weather-selector",
}: WeatherSelectorProps) {
  const { t } = useTranslation();

  const handleKeyDown = (e: React.KeyboardEvent, index: number) => {
    if (disabled) return;
    let nextIndex = index;
    if (e.key === "ArrowRight" || e.key === "ArrowDown") {
      e.preventDefault();
      nextIndex = (index + 1) % ORDERED_WEATHER_CONDITIONS.length;
    } else if (e.key === "ArrowLeft" || e.key === "ArrowUp") {
      e.preventDefault();
      nextIndex = (index - 1 + ORDERED_WEATHER_CONDITIONS.length) % ORDERED_WEATHER_CONDITIONS.length;
    }
    if (nextIndex !== index) {
      onChange(ORDERED_WEATHER_CONDITIONS[nextIndex]);
      const nextBtn = document.getElementById(`${id}-option-${ORDERED_WEATHER_CONDITIONS[nextIndex]}`);
      nextBtn?.focus();
    }
  };

  return (
    <div
      id={id}
      role="radiogroup"
      aria-label={t("weather.title", "وضعیت جوی")}
      className={cn("flex flex-wrap gap-2", className)}
      data-testid="weather-selector-radiogroup"
    >
      {ORDERED_WEATHER_CONDITIONS.map((cond, index) => {
        const isSelected = value === cond;
        const localizedLabel = t(`weather.conditions.${cond}`, WEATHER_META[cond]?.label ?? cond);
        const icon = WEATHER_META[cond]?.icon ?? "";

        return (
          <button
            key={cond}
            id={`${id}-option-${cond}`}
            type="button"
            role="radio"
            aria-checked={isSelected}
            tabIndex={isSelected || (!value && index === 0) ? 0 : -1}
            disabled={disabled}
            data-testid={`weather-option-${cond}`}
            onClick={() => onChange(cond)}
            onKeyDown={(e) => handleKeyDown(e, index)}
            className={cn(
              "flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-sm font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-primary/40",
              isSelected
                ? "border-primary bg-primary/10 text-primary dark:bg-primary/20"
                : "border-border text-muted-foreground hover:bg-muted/40",
              disabled && "cursor-not-allowed opacity-50"
            )}
          >
            <span aria-hidden="true" className="text-base leading-none">
              {icon}
            </span>
            <span>{localizedLabel}</span>
          </button>
        );
      })}
    </div>
  );
}
