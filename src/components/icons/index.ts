import { MdDashboard } from "react-icons/md";
import { FaUsers } from "react-icons/fa";
import { FaBusinessTime } from "react-icons/fa";

export const ICONS = {
  dashboard: MdDashboard,
  users: FaUsers,
  business: FaBusinessTime,
} as const;

export type IconName = keyof typeof ICONS;

