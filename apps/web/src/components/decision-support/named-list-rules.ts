/** Pure named-list rules for criteria / alternatives (max 10, unique, non-empty). */

export const MAX_NAMED_LIST = 10;

export type NamedListIssue = {
  code: "name_empty" | "name_duplicate" | "dimension_invalid";
  index?: number;
  message: string;
};

export function validateNamedList(names: string[]): NamedListIssue[] {
  const issues: NamedListIssue[] = [];
  if (names.length > MAX_NAMED_LIST) {
    issues.push({
      code: "dimension_invalid",
      message: `At most ${MAX_NAMED_LIST} names allowed.`,
    });
  }
  const seen = new Map<string, number>();
  names.forEach((raw, index) => {
    const text = raw.trim();
    if (!text) {
      issues.push({ code: "name_empty", index, message: "Name cannot be empty." });
      return;
    }
    if (seen.has(text)) {
      issues.push({ code: "name_duplicate", index, message: "Name must be unique." });
      return;
    }
    seen.set(text, index);
  });
  return issues;
}

export function canAddNamedItem(names: string[]): boolean {
  return names.length < MAX_NAMED_LIST;
}

export function addNamedItem(names: string[], candidate: string): { next: string[]; issues: NamedListIssue[] } {
  const trimmed = candidate.trim();
  if (!trimmed) {
    return { next: names, issues: [{ code: "name_empty", message: "Name cannot be empty." }] };
  }
  if (!canAddNamedItem(names)) {
    return {
      next: names,
      issues: [{ code: "dimension_invalid", message: `At most ${MAX_NAMED_LIST} names allowed.` }],
    };
  }
  if (names.some((n) => n.trim() === trimmed)) {
    return { next: names, issues: [{ code: "name_duplicate", message: "Name must be unique." }] };
  }
  return { next: [...names, trimmed], issues: [] };
}
