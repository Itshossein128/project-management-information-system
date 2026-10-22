/**
 * Inactive site activity confirmation guard (Spec 030, US5).
 */

export const INACTIVE_ACTIVITY_WARNING_FA =
  "کارگاه در این تاریخ تعطیل ثبت شده است؛ آیا از ثبت کارکرد اجرایی اطمینان دارید؟";

export const INACTIVE_ACTIVITY_WARNING_EN =
  "The worksite is marked inactive on this date. Are you sure you want to record execution progress?";

/**
 * Checks whether an activity edit/creation triggers the inactive site confirmation prompt.
 * Triggers when the worksite is inactive and the quantity is strictly positive (> 0).
 */
export function shouldWarnInactiveSiteActivity(
  siteStatus: string | null | undefined,
  quantity: unknown,
): boolean {
  if (siteStatus !== "inactive") return false;
  if (quantity === null || quantity === undefined || quantity === "") return false;

  const num = typeof quantity === "number" ? quantity : Number(quantity);
  if (Number.isNaN(num)) return false;
  return num > 0;
}
