import {
  readStickyFormState,
  writeStickyFormState,
} from "@/app/lib/sticky-field-storage";
import { useCallback, useEffect, useState } from "react";

type StickyDefaults<T extends Record<string, string>> =
  | boolean
  | Partial<Record<keyof T, boolean>>;

function resolveDefaultLocked<T extends Record<string, string>>(
  key: keyof T,
  defaultSticky: StickyDefaults<T>,
): boolean {
  if (typeof defaultSticky === "boolean") return defaultSticky;
  return defaultSticky[key] ?? false;
}

function buildInitialState<T extends Record<string, string>>(
  scope: string,
  initialValues: T,
  defaultSticky: StickyDefaults<T>,
): { values: T; locked: Record<keyof T, boolean> } {
  const persisted = readStickyFormState(scope);
  const keys = Object.keys(initialValues) as (keyof T)[];
  const values = { ...initialValues };
  const locked = {} as Record<keyof T, boolean>;

  for (const key of keys) {
    const fieldKey = String(key);
    const isLocked =
      persisted?.locked[fieldKey] ??
      resolveDefaultLocked(key, defaultSticky);
    locked[key] = isLocked;

    if (isLocked) {
      const persistedValue = persisted?.values[fieldKey];
      if (persistedValue !== undefined) {
        values[key] = persistedValue as T[keyof T];
      }
    }
  }

  return { values, locked };
}

export function useStickyFormFields<T extends Record<string, string>>({
  scope,
  initialValues,
  defaultSticky = false,
}: {
  scope: string;
  initialValues: T;
  defaultSticky?: StickyDefaults<T>;
}) {
  const [state, setState] = useState(() =>
    buildInitialState(scope, initialValues, defaultSticky),
  );

  useEffect(() => {
    setState(buildInitialState(scope, initialValues, defaultSticky));
  }, [scope, initialValues, defaultSticky]);

  const persist = useCallback(
    (values: T, locked: Record<keyof T, boolean>) => {
      writeStickyFormState(scope, {
        values: Object.fromEntries(
          Object.entries(values).map(([key, value]) => [
            key,
            typeof value === "string" ? value : "",
          ]),
        ),
        locked: Object.fromEntries(
          Object.entries(locked).map(([key, value]) => [
            key,
            Boolean(value),
          ]),
        ),
      });
    },
    [scope],
  );

  const setField = useCallback(
    (key: keyof T, value: string) => {
      setState((prev) => {
        const values = { ...prev.values, [key]: value };
        if (prev.locked[key]) {
          persist(values, prev.locked);
        }
        return { ...prev, values };
      });
    },
    [persist],
  );

  const setSticky = useCallback(
    (key: keyof T, sticky: boolean) => {
      setState((prev) => {
        const locked = { ...prev.locked, [key]: sticky };
        persist(prev.values, locked);
        return { ...prev, locked };
      });
    },
    [persist],
  );

  const resetUnlocked = useCallback(() => {
    setState((prev) => {
      const values = { ...prev.values };
      for (const key of Object.keys(initialValues) as (keyof T)[]) {
        if (!prev.locked[key]) {
          values[key] = initialValues[key];
        }
      }
      persist(values, prev.locked);
      return { ...prev, values };
    });
  }, [initialValues, persist]);

  return {
    values: state.values,
    setField,
    sticky: state.locked,
    setSticky,
    resetUnlocked,
  };
}
