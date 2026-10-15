import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { PATHS } from "../../apps/web/src/app/routeVars";

/** Read the live registry, fail closed when its declaration syntax changes. */
export function registeredRoutes() {
  const entries: Array<{ key: string; path: string }> = [];
  for (const name of ["routes.ts", "routes/business-setup.routes.ts"]) {
    const source = readFileSync(resolve("apps/web/src/app", name), "utf8").replace(/\/\*[\s\S]*?\*\/|\/\/[^\n]*/g, "");
    const matches = [...source.matchAll(/\broute\(\s*(`[^`]+`|PATHS\.\w+|"[^"]+")\s*,\s*ROUTES\.(\w+)/g)];
    if (matches.length !== [...source.matchAll(/\broute\s*\(/g)].length) throw new Error(`Unsupported route syntax in ${name}`);
    for (const [, expression, key] of matches) {
      const expand = (constant: string) => {
        const value = constant.split(".").reduce<unknown>((current, part) => (current as Record<string, unknown>)[part], PATHS);
        if (typeof value !== "string") throw new Error(`Unknown path constant ${constant}`);
        return value;
      };
      const value = expression.startsWith("PATHS.") ? expand(expression.slice(6))
        : expression.slice(1, -1).replace(/\$\{PATHS\.([\w.]+)\}/g, (_, constant) => expand(constant));
      if (value.includes("${")) throw new Error(`Unresolved route ${expression}`);
      entries.push({ key, path: `/${value}` });
    }
  }
  return [...entries, { key: "INDEX", path: "/" }];
}
