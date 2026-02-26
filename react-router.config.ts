import path from "node:path";
import type { Config } from "@react-router/dev/config";

export default {
  appDirectory: path.resolve(__dirname, "app"),
  ssr: true,
} satisfies Config;
