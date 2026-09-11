import type { Page } from "@playwright/test";
import { expect } from "@playwright/test";

/** Driver.js v1 renders a single popover; these are its stable class names. */
const POPOVER = ".driver-popover";
const TITLE = ".driver-popover-title";
const DESCRIPTION = ".driver-popover-description";
const PROGRESS = ".driver-popover-progress-text";
const NEXT_BTN = ".driver-popover-next-btn";
const PREV_BTN = ".driver-popover-prev-btn";
/** Driver.js adds this class to the next button only on the final step. */
const DONE_BTN = "driver-popover-done-btn";
/**
 * Driver.js points the highlighted element's `aria-controls` at its popover.
 * We track the current step through that rather than `.driver-active-element`:
 * steps with an `onHighlight` that re-renders their own anchor (the tab
 * switchers in the reports and alerts tours) lose the class, because React
 * rewrites `className` and does not know about it. React leaves `aria-controls`
 * alone, so it survives.
 */
const HIGHLIGHTED = '[aria-controls="driver-popover-content"]';

export interface TourStep {
  /** 1-based position reported by driver.js. */
  index: number;
  total: number;
  title: string;
  description: string;
  /** `data-tour` value of the highlighted element, or null when nothing is highlighted. */
  target: string | null;
}

export function tourPopover(page: Page) {
  return page.locator(POPOVER);
}

/**
 * Mark tours as already seen before the app boots, so `useProductTour` does not
 * auto-start them. Use this in any test that drives a tour manually.
 */
export async function markToursSeen(page: Page, ...tourIds: string[]) {
  await page.addInitScript((ids: string[]) => {
    for (const id of ids) {
      localStorage.setItem(`tour_seen_${id}`, "true");
    }
  }, tourIds);
}

export function readSeenFlag(page: Page, tourId: string) {
  return page.evaluate((id: string) => localStorage.getItem(`tour_seen_${id}`), tourId);
}

export async function startTourFromButton(page: Page) {
  const button = page.getByTestId("product-tour-button");
  await expect(button).toBeVisible();
  await button.click();
  await expect(tourPopover(page)).toBeVisible();
}

function parseProgress(text: string): { index: number; total: number } {
  const match = text.match(/(\d+)\s*of\s*(\d+)/i);
  if (!match) {
    throw new Error(`Unrecognised driver.js progress text: ${JSON.stringify(text)}`);
  }
  return { index: Number(match[1]), total: Number(match[2]) };
}

/**
 * Driver.js never clears the marker from the tour's first element, so once a
 * tour has moved on two elements carry it and DOM order cannot tell us which
 * step is current. Wiping the markers before advancing leaves exactly the
 * incoming step's element marked.
 */
async function clearHighlightMarkers(page: Page) {
  await page.evaluate((selector: string) => {
    for (const el of document.querySelectorAll(selector)) {
      el.removeAttribute("aria-controls");
    }
  }, HIGHLIGHTED);
}

export async function readCurrentStep(page: Page): Promise<TourStep> {
  const popover = tourPopover(page);
  await expect(popover).toBeVisible();
  const { index, total } = parseProgress(await popover.locator(PROGRESS).innerText());
  const highlighted = page.locator(HIGHLIGHTED);
  await expect(highlighted, `step ${index} highlighted no single element`).toHaveCount(1);
  return {
    index,
    total,
    title: (await popover.locator(TITLE).innerText()).trim(),
    description: (await popover.locator(DESCRIPTION).innerText()).trim(),
    target: await highlighted.getAttribute("data-tour"),
  };
}

export async function goToNextStep(page: Page, expectedIndex: number, total: number) {
  const popover = tourPopover(page);
  await clearHighlightMarkers(page);
  await popover.locator(NEXT_BTN).click();
  await expect(popover.locator(PROGRESS)).toContainText(`${expectedIndex} of ${total}`);
}

export async function goToPreviousStep(page: Page, expectedIndex: number, total: number) {
  const popover = tourPopover(page);
  await clearHighlightMarkers(page);
  await popover.locator(PREV_BTN).click();
  await expect(popover.locator(PROGRESS)).toContainText(`${expectedIndex} of ${total}`);
}

/**
 * Click through an open tour from its current step to the end, capturing each
 * step. Returns with the tour closed and its `tour_seen_*` flag written.
 */
export async function walkTourToEnd(page: Page): Promise<TourStep[]> {
  const popover = tourPopover(page);
  const first = await readCurrentStep(page);
  const steps: TourStep[] = [first];

  for (let next = first.index + 1; next <= first.total; next++) {
    await goToNextStep(page, next, first.total);
    steps.push(await readCurrentStep(page));
  }

  await expect(popover.locator(NEXT_BTN)).toHaveClass(new RegExp(DONE_BTN));
  await popover.locator(NEXT_BTN).click();
  await expect(popover).toHaveCount(0);
  return steps;
}
