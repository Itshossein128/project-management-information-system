import type { Business, BusinessJobPosition, UserBusinessAssignment } from "./api-types";

function getBusinessName(business: Business | number | undefined): string | null {
  if (!business) return null;
  if (typeof business === "number") return null;
  return business.name ?? null;
}

function getJobLabel(job: BusinessJobPosition | number | undefined): string | null {
  if (!job) return null;
  if (typeof job === "number") return null;
  return job.label ?? null;
}

export function splitAssignmentsForTablePreview(
  assignments: UserBusinessAssignment[] | undefined,
  max = 2,
): { lines: string[]; overflowCount: number } {
  const list = assignments ?? [];
  const display = list
    .map((a) => {
      const businessName = getBusinessName(a.business as Business | number | undefined);
      const jobLabel = getJobLabel(a.job_position as BusinessJobPosition | number | undefined);
      if (!businessName && !jobLabel) return null;
      if (!businessName) return jobLabel;
      if (!jobLabel) return businessName;
      return `${businessName} – ${jobLabel}`;
    })
    .filter((x): x is string => Boolean(x));

  return {
    lines: display.slice(0, max),
    overflowCount: Math.max(0, display.length - max),
  };
}

