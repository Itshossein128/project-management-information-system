/**
 * Static checks on tour definitions. These read the source tree rather than the
 * browser, so they catch wiring mistakes (missing translations, anchors that no
 * longer exist) that a running tour would only reveal as an empty popover.
 */
import { readdirSync, readFileSync, statSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { expect, test } from "@playwright/test";

const SRC = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../src");
const LOCALES = path.join(SRC, "app/locales");

function sourceFiles(dir: string): string[] {
  return readdirSync(dir).flatMap((entry) => {
    const full = path.join(dir, entry);
    if (statSync(full).isDirectory()) return sourceFiles(full);
    return /\.tsx?$/.test(entry) ? [full] : [];
  });
}

function matchAll(pattern: RegExp, text: string): string[] {
  return [...text.matchAll(pattern)].map((m) => m[1]);
}

/** `data-tour={`reports-${tab.id}-tab`}` matches any of its runtime values. */
function templateToRegExp(template: string): RegExp {
  const escaped = template
    .split(/\$\{[^}]*\}/)
    .map((chunk) => chunk.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"))
    .join(".+");
  return new RegExp(`^${escaped}$`);
}

function flattenKeys(value: unknown, prefix = ""): string[] {
  if (typeof value !== "object" || value === null) return [prefix];
  return Object.entries(value as Record<string, unknown>).flatMap(([key, child]) =>
    flattenKeys(child, prefix ? `${prefix}.${key}` : key),
  );
}

function lookup(root: unknown, dotted: string): unknown {
  return dotted.split(".").reduce<unknown>((node, part) => {
    if (typeof node !== "object" || node === null) return undefined;
    return (node as Record<string, unknown>)[part];
  }, root);
}

const files = sourceFiles(SRC).map((file) => ({ file, text: readFileSync(file, "utf8") }));
const locales = {
  fa: JSON.parse(readFileSync(path.join(LOCALES, "fa.json"), "utf8")) as Record<string, unknown>,
  en: JSON.parse(readFileSync(path.join(LOCALES, "en.json"), "utf8")) as Record<string, unknown>,
};

/** Keys the tour runtime resolves itself, outside any step definition. */
const RUNTIME_KEYS = new Set([
  "tour.next",
  "tour.prev",
  "tour.done",
  "tour.buttonLabel",
  "tour.buttonTitle",
]);

const usedKeys = new Set(
  files.flatMap(({ text }) => matchAll(/t\(\s*"(tour\.[^"]+)"/g, text)),
);

const stepAnchors = files.flatMap(({ file, text }) =>
  matchAll(/element:\s*"\[data-tour='([^']+)'\]"/g, text).map((anchor) => ({ anchor, file })),
);

const declaredAnchors = files.flatMap(({ text }) => [
  ...matchAll(/\bdata-tour="([^"]+)"/g, text),
  ...matchAll(/"data-tour":\s*"([^"]+)"/g, text),
]);

const templatedAnchors = files.flatMap(({ text }) =>
  matchAll(/\bdata-tour=\{`([^`]+)`\}/g, text).map(templateToRegExp),
);

test.describe("Tour wiring", () => {
  test("every tour step key is translated in both locales", () => {
    const missing: string[] = [];
    for (const key of [...usedKeys].sort()) {
      for (const [locale, bundle] of Object.entries(locales)) {
        const value = lookup(bundle, key);
        if (typeof value !== "string" || value.trim() === "") {
          missing.push(`${locale}: ${key}`);
        }
      }
    }
    expect(usedKeys.size).toBeGreaterThan(0);
    expect(missing, "tour keys used in code but missing from a locale").toEqual([]);
  });

  test("fa and en define exactly the same tour keys", () => {
    const fa = flattenKeys(lookup(locales.fa, "tour")).sort();
    const en = flattenKeys(lookup(locales.en, "tour")).sort();
    expect(en).toEqual(fa);
  });

  test("no tour copy is defined without a step using it", () => {
    const defined = flattenKeys(lookup(locales.fa, "tour")).map((key) => `tour.${key}`);
    const orphans = defined
      .filter((key) => !usedKeys.has(key) && !RUNTIME_KEYS.has(key))
      // `<tour>.title` names the tour itself and is not rendered as a step.
      .filter((key) => !key.endsWith(".title"));
    expect(orphans, "unused tour translations").toEqual([]);
  });

  test("every step anchor exists as a data-tour attribute in markup", () => {
    const dangling = stepAnchors
      .filter(
        ({ anchor }) =>
          !declaredAnchors.includes(anchor) &&
          !templatedAnchors.some((pattern) => pattern.test(anchor)),
      )
      .map(({ anchor, file }) => `${anchor} (${path.relative(SRC, file)})`);

    expect(stepAnchors.length).toBeGreaterThan(0);
    expect(dangling, "tour steps pointing at anchors that no longer exist").toEqual([]);
  });

  test("tour ids are unique across pages", () => {
    const ids = files.flatMap(({ text }) => matchAll(/tourId:\s*"([^"]+)"/g, text));
    expect(ids.length).toBeGreaterThan(0);
    expect([...ids].sort()).toEqual([...new Set(ids)].sort());
  });
});
