import path from "node:path";
import type { Config } from "@react-router/dev/config";

/**
 * Default configuration object for React Router v7 execution.
 * Configures the base application directory and enables Server Side Rendering (SSR).
 */
export default {
  appDirectory: path.resolve(__dirname, "src/app"),
  ssr: true,
} satisfies Config;
