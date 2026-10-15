import {
  Banknote, Bolt, BriefcaseBusiness, Building2, ClipboardList, FolderKanban,
  LayoutDashboard, Layers3, Network, Settings2, ShieldCheck, Truck,
  UsersRound, Warehouse, Wrench,
} from "lucide-react";

export const ICONS = {
  dashboard: LayoutDashboard,
  users: UsersRound,
  business: BriefcaseBusiness,
  settings: Settings2,
  building: Building2,
  projects: FolderKanban,
  wrench: Wrench,
  shield: ShieldCheck,
  truck: Truck,
  warehouse: Warehouse,
  bolt: Bolt,
  clipboard: ClipboardList,
  cashflow: Banknote,
  organization: Network,
  templates: Layers3,
} as const;

export type IconName = keyof typeof ICONS;
