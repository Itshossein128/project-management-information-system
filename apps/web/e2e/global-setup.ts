import { execSync } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../..");

export default async function globalSetup() {
  execSync("bash ./django.sh migrate --noinput && bash ./django.sh seed_e2e", {
    cwd: path.join(repoRoot, "apps/api"),
    stdio: "inherit",
    env: process.env,
  });
}
