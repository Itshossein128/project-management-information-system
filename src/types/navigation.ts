import type { ReactNode } from "react";
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
