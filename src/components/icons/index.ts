import { FaBusinessTime, FaUsers } from "react-icons/fa";
import { MdDashboard, MdSettings } from "react-icons/md";

export const ICONS = {
  dashboard: MdDashboard,
  users: FaUsers,
  business: FaBusinessTime,
  settings: MdSettings,
} as const;

export type IconName = keyof typeof ICONS;

