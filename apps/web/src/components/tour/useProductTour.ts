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
  onHighlight?: () => void;
}

interface UseProductTourOptions {
  tourId: string;
  steps: TourStepConfig[];
  autoStart?: boolean;
}

export function useProductTour({ tourId, steps, autoStart = true }: UseProductTourOptions) {
  const { t, i18n } = useTranslation();
  const driverObj = useRef<Driver | null>(null);
  const stepsRef = useRef(steps);
  stepsRef.current = steps;

  const startTour = useCallback(() => {
    const currentSteps = stepsRef.current;
    if (!currentSteps || currentSteps.length === 0) return;

    // Skip steps whose targets are not in the DOM yet (avoids empty popovers).
    const availableSteps = currentSteps.filter((step) => {
      try {
        return Boolean(document.querySelector(step.element));
      } catch {
        return false;
      }
    });
    if (availableSteps.length === 0) return;

    const rtl = isRTL(i18n.language);

    const formattedSteps: DriveStep[] = availableSteps.map((step) => ({
      element: step.element,
      popover: {
        title: step.popover.title,
        description: step.popover.description,
        side: step.popover.side || "bottom",
        align: step.popover.align || "start",
      },
    }));

    if (driverObj.current) {
      driverObj.current.destroy();
    }

    const driverInstance = driver({
      showProgress: true,
      animate: true,
      overlayColor: "rgba(0, 0, 0, 0.6)",
      nextBtnText: t("tour.next", { defaultValue: rtl ? "بعدی ←" : "Next →" }),
      prevBtnText: t("tour.prev", { defaultValue: rtl ? "→ قبلی" : "← Prev" }),
      doneBtnText: t("tour.done", { defaultValue: "متوجه شدم / Done" }),
      steps: formattedSteps,
      onHighlightStarted: (_element, _step, { state }) => {
        const index = state.activeIndex ?? 0;
        availableSteps[index]?.onHighlight?.();
      },
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
  }, [tourId, i18n.language, t]);

  useEffect(() => {
    if (!autoStart) return;

    try {
      const hasSeen = localStorage.getItem(`tour_seen_${tourId}`);
      if (hasSeen) return;

      let attempts = 0;
      const maxAttempts = 20;
      const timer = window.setInterval(() => {
        attempts += 1;
        const hasAvailableTarget = stepsRef.current.some((step) => {
          try {
            return Boolean(document.querySelector(step.element));
          } catch {
            return false;
          }
        });

        if (hasAvailableTarget) {
          window.clearInterval(timer);
          startTour();
        } else if (attempts >= maxAttempts) {
          window.clearInterval(timer);
        }
      }, 300);

      return () => window.clearInterval(timer);
    } catch (e) {
      console.error("Failed to check tour status from localStorage", e);
    }
  }, [tourId, autoStart, startTour]);

  useEffect(() => {
    return () => {
      driverObj.current?.destroy();
    };
  }, []);

  return { startTour };
}
