import type { WeatherCondition } from "@/app/lib/api/weather";

interface IconProps {
  className?: string;
}

export function WeatherIcon({ condition, className }: { condition: WeatherCondition; className?: string }) {
  switch (condition) {
    case "sunny":
      return <SunIcon className={className} />;
    case "cloudy":
    case "partly_cloudy":
    case "foggy":
      return <CloudIcon className={className} />;
    case "rainy":
      return <RainIcon className={className} />;
    case "stormy":
      return <StormIcon className={className} />;
    case "snowy":
      return <SnowIcon className={className} />;
    default:
      return <CloudIcon className={className} />;
  }
}

export const WEATHER_CALENDAR_COLORS: Record<WeatherCondition, string> = {
  sunny: "bg-warning-200 text-warning-900 dark:bg-warning-900/50 dark:text-warning-200",
  cloudy: "bg-neutral-200 text-neutral-800 dark:bg-neutral-700 dark:text-neutral-200",
  partly_cloudy: "bg-info-200 text-info-900 dark:bg-info-900/50 dark:text-info-200",
  rainy: "bg-info-300 text-info-900 dark:bg-info-900/50 dark:text-info-200",
  stormy: "bg-brand-300 text-brand-900 dark:bg-brand-900/50 dark:text-brand-200",
  snowy: "bg-info-100 text-info-900 dark:bg-info-900/50 dark:text-info-200",
  foggy: "bg-neutral-300 text-neutral-800 dark:bg-neutral-700 dark:text-neutral-200",
};

function SunIcon({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className={className} aria-hidden>
      <circle cx="12" cy="12" r="4" />
      <path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41" />
    </svg>
  );
}

function CloudIcon({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className={className} aria-hidden>
      <path d="M18 10a4 4 0 0 0-7.9-1A4.5 4.5 0 1 0 6 19h11a3 3 0 0 0 0-6z" />
    </svg>
  );
}

function RainIcon({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className={className} aria-hidden>
      <path d="M18 10a4 4 0 0 0-7.9-1A4.5 4.5 0 1 0 6 19h11a3 3 0 0 0 0-6z" />
      <path d="M8 19v2M12 19v3M16 19v2" />
    </svg>
  );
}

function StormIcon({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className={className} aria-hidden>
      <path d="M18 10a4 4 0 0 0-7.9-1A4.5 4.5 0 1 0 6 19h11a3 3 0 0 0 0-6z" />
      <path d="M13 16l-2 4h3l-2 4" />
    </svg>
  );
}

function SnowIcon({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className={className} aria-hidden>
      <path d="M12 2v20M4.5 7.5l15 9M19.5 7.5l-15 9M4.5 16.5l15-9M19.5 16.5l-15-9" />
    </svg>
  );
}
