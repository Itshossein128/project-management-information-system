import path from "node:path";
import { createRequire } from "node:module";
import { reactRouter } from "@react-router/dev/vite";
import tailwindcss from "@tailwindcss/vite";
import { defineConfig } from "vite";
import { VitePWA } from "vite-plugin-pwa";
import tsconfigPaths from "vite-tsconfig-paths";

const require = createRequire(import.meta.url);
const frappeGanttCss = path.join(
  path.dirname(require.resolve("frappe-gantt")),
  "frappe-gantt.css",
);

export default defineConfig({
  plugins: [
    tailwindcss(),
    reactRouter(),
    tsconfigPaths(),
    VitePWA({
      registerType: "autoUpdate",
      // The service worker is registered manually from the client (SSR app has
      // no static index.html for auto-injection).
      injectRegister: false,
      includeAssets: ["favicon.ico", "robots.txt"],
      manifest: {
        name: "IPCAS — کنترل پروژه",
        short_name: "IPCAS",
        description: "سیستم اتوماسیون یکپارچه کنترل پروژه",
        theme_color: "#1e40af",
        background_color: "#ffffff",
        display: "standalone",
        orientation: "portrait",
        lang: "fa",
        dir: "rtl",
        icons: [
          { src: "/icons/icon-192.png", sizes: "192x192", type: "image/png" },
          { src: "/icons/icon-512.png", sizes: "512x512", type: "image/png" },
        ],
      },
      workbox: {
        globPatterns: ["**/*.{js,css,html,ico,png,svg,woff2}"],
        runtimeCaching: [
          {
            urlPattern: /^https:\/\/.*\/api\/v1\/projects\/.*\/wbs\//,
            handler: "StaleWhileRevalidate",
            options: {
              cacheName: "wbs-cache",
              expiration: { maxAgeSeconds: 86400 },
            },
          },
          {
            urlPattern: /^https:\/\/.*\/api\/v1\/projects\/.*\/activities\//,
            handler: "StaleWhileRevalidate",
            options: {
              cacheName: "activities-cache",
              expiration: { maxAgeSeconds: 86400 },
            },
          },
          {
            urlPattern: /^https:\/\/.*\/api\/v1\/projects\/.*\/manpower\/job-titles\//,
            handler: "CacheFirst",
            options: {
              cacheName: "reference-data-cache",
              expiration: { maxAgeSeconds: 604800 },
            },
          },
        ],
      },
    }),
  ],
  resolve: {
    dedupe: ["react", "react-dom"],
    alias: {
      "@": path.resolve(__dirname, "./src"),
      // Package exports omit a CSS subpath; alias so Vite can resolve the stylesheet.
      "frappe-gantt/dist/frappe-gantt.css": frappeGanttCss,
    },
  },
  optimizeDeps: {
    include: ["react", "react-dom", "@tanstack/react-query"],
  },
});
