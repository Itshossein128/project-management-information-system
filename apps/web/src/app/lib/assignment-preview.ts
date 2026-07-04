import type { Business, BusinessJobPosition, UserBusinessAssignment } from "./api-types";

// Function to manage getBusinessName
function getBusinessName(business: Business | number | undefined): string | null {
  if (!business) return null;
  if (typeof business === "number") return null;
  return business.name ?? null;
}

// Function to manage getJobLabel
function getJobLabel(job: BusinessJobPosition | number | undefined): string | null {
  if (!job) return null;
  if (typeof job === "number") return null;
  return job.label ?? null;
}

// Function to manage splitAssignmentsForTablePreview
export function splitAssignmentsForTablePreview(
  assignments: UserBusinessAssignment[] | undefined,
  max = 2,
): { lines: string[]; overflowCount: number } {
  // Variable holding list
  const list = assignments ?? [];
  // Variable holding display
  const display = list
    .map((a) => {
      // Variable holding businessName
      const businessName = getBusinessName(a.business as Business | number | undefined);
      // Variable holding jobLabel
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

