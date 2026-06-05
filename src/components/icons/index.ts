import {
  FaBuilding,
  FaBusinessTime,
  FaShieldAlt,
  FaTruck,
  FaUsers,
  FaWrench,
} from "react-icons/fa";
import { MdBolt, MdDashboard, MdSettings, MdWarehouse } from "react-icons/md";

export const ICONS = {
  dashboard: MdDashboard,
  users: FaUsers,
  business: FaBusinessTime,
  settings: MdSettings,
  building: FaBuilding,
  wrench: FaWrench,
  shield: FaShieldAlt,
  truck: FaTruck,
  warehouse: MdWarehouse,
  bolt: MdBolt,
} as const;

export type IconName = keyof typeof ICONS;

