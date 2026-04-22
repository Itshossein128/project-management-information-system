import type { ReactNode } from "react";
import type { IconName } from "@/components/icons";
import { ROLES } from "src/config/roles";

export type AppRoute = {
    path: string;
    element: ReactNode;

    meta?: {
        label?: string;
        icon?: string;
        showInMenu?: boolean;
        roles?: ROLES[];
    };

    children?: AppRoute[];
};

export interface NavigationChildItem {
  label: string;
  /** Route segment(s), e.g. `businesses/3/tables`. If it contains `:param`, it is not a direct link. */
  path: string;
}

export interface NavigationItem {
  label: string;
  icon: IconName;
  /** URL path segment(s) without leading slash, used as NavLink `to` target. */
  path: string;
  roles?: ROLES[];
  /**
   * When set, this item is active if the location pathname starts with `/${activePathPrefix}`.
   * Use when the link target differs from where the section is "current" (e.g. business hub links to home but business routes live under `/businesses/...`).
   */
  activePathPrefix?: string;
  /**
   * When `activePathPrefix` matches, treat as inactive if pathname matches this regex (string form, no delimiters).
   * Example: `^/businesses/\\d+$` excludes `/businesses/123` (detail) but keeps `/businesses`, `/businesses/create`, `/businesses/123/setup`.
   */
  activePathExclude?: string;
  /** If true, active only when pathname matches `/${path}` exactly (no sub-routes). */
  activeExact?: boolean;
  children?: NavigationChildItem[];
}
