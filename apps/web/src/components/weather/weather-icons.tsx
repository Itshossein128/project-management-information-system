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
  sunny: "bg-amber-200 text-amber-900 dark:bg-amber-900/50 dark:text-amber-200",
  cloudy: "bg-slate-200 text-slate-800 dark:bg-slate-700 dark:text-slate-200",
  partly_cloudy: "bg-sky-200 text-sky-900 dark:bg-sky-900/50 dark:text-sky-200",
  rainy: "bg-blue-300 text-blue-900 dark:bg-blue-900/50 dark:text-blue-200",
  stormy: "bg-violet-300 text-violet-900 dark:bg-violet-900/50 dark:text-violet-200",
  snowy: "bg-cyan-200 text-cyan-900 dark:bg-cyan-900/50 dark:text-cyan-200",
  foggy: "bg-gray-300 text-gray-800 dark:bg-gray-700 dark:text-gray-200",
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
