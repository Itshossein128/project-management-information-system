export interface StickyFormPersistedState {
  values: Record<string, string>;
  locked: Record<string, boolean>;
}

const STORAGE_PREFIX = "sticky-form:";

function storageKey(scope: string): string {
  return `${STORAGE_PREFIX}${scope}`;
}

export function readStickyFormState(
  scope: string,
): StickyFormPersistedState | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = window.localStorage.getItem(storageKey(scope));
    if (!raw) return null;
    const parsed = JSON.parse(raw) as StickyFormPersistedState;
    if (
      parsed &&
      typeof parsed === "object" &&
      parsed.values &&
      typeof parsed.values === "object" &&
      parsed.locked &&
      typeof parsed.locked === "object"
    ) {
      return parsed;
    }
    return null;
  } catch {
    return null;
  }
}

export function writeStickyFormState(
  scope: string,
  state: StickyFormPersistedState,
): void {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(storageKey(scope), JSON.stringify(state));
  } catch {
    // Ignore quota / private-mode errors.
  }
}
