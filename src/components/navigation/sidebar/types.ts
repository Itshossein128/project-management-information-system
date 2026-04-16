import type { ROLES } from "@/config/roles";

export interface NavigationItem {
    label: string;
    icon: string;
    path: string;
    roles?: ROLES[];
    children?: {
        label: string;
        path: string;
    }[];
}
