import { useCallback, useEffect, useRef } from "react";
import { driver, type Driver, type DriveStep } from "driver.js";
import { useTranslation } from "react-i18next";
import { isRTL } from "@/app/lib/i18n";

export interface TourStepConfig {
  element: string;
  popover: {
    title: string;
    description: string;
    side?: "top" | "right" | "bottom" | "left";
    align?: "start" | "center" | "end";
  };
}

interface UseProductTourOptions {
  tourId: string;
  steps: TourStepConfig[];
  autoStart?: boolean;
}

export function useProductTour({ tourId, steps, autoStart = true }: UseProductTourOptions) {
  const { t, i18n } = useTranslation();
  const driverObj = useRef<Driver | null>(null);

  const startTour = useCallback(() => {
    if (!steps || steps.length === 0) return;

    const rtl = isRTL(i18n.language);

    const formattedSteps: DriveStep[] = steps.map((step) => ({
      element: step.element,
      popover: {
        title: step.popover.title,
        description: step.popover.description,
        side: step.popover.side || "bottom",
        align: step.popover.align || "start",
      },
    }));

    const driverInstance = driver({
      showProgress: true,
      animate: true,
      overlayColor: "rgba(0, 0, 0, 0.6)",
      nextBtnText: t("tour.next", { defaultValue: rtl ? "بعدی ←" : "Next →" }),
      prevBtnText: t("tour.prev", { defaultValue: rtl ? "→ قبلی" : "← Prev" }),
      doneBtnText: t("tour.done", { defaultValue: "متوجه شدم / Done" }),
      steps: formattedSteps,
      onDestroyed: () => {
        try {
          localStorage.setItem(`tour_seen_${tourId}`, "true");
        } catch (e) {
          console.error("Failed to save tour status to localStorage", e);
        }
      },
    });

    driverObj.current = driverInstance;
    driverInstance.drive();
  }, [tourId, steps, i18n.language, t]);

  useEffect(() => {
    if (!autoStart) return;

    try {
      const hasSeen = localStorage.getItem(`tour_seen_${tourId}`);
      if (!hasSeen) {
        // Small delay to ensure DOM elements are fully mounted
        const timer = setTimeout(() => {
          startTour();
        }, 600);
        return () => clearTimeout(timer);
      }
    } catch (e) {
      console.error("Failed to check tour status from localStorage", e);
    }
  }, [tourId, autoStart, startTour]);

  return { startTour };
}
