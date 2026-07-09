import path from "node:path";
import type { Config } from "@react-router/dev/config";

/**
 * Configuration object for React Router v7.
 * Sets the base directory for the application source and enables Server-Side Rendering (SSR).
 */
export default {
  appDirectory: path.resolve(__dirname, "src/app"),
  ssr: true,
} satisfies Config;
