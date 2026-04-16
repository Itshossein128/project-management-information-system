import type { AppRoute } from "src/types/navigation";
import { ROLES } from "src/config/roles";

import DashboardPage from "@/features/dashboard/pages/dashboard.page";
import ProjectsList from "@/features/projects/pages/projects-list.page";
import ProjectCreate from "@/features/projects/pages/project-create.page";
import CostAnalysis from "@/features/finance/pages/cost-analysis.page";

export const routeTree: AppRoute[] = [
    {
        path: "/dashboard",
        element: <DashboardPage />,
    meta: {
            label: "داشبورد",
            icon: "dashboard",
            showInMenu: true,
            roles: [ROLES.ADMIN, ROLES.MANAGER],
        },
    },

    {
        path: "/projects",
        element: <div />,
    meta: {
            label: "پروژه‌ها",
            icon: "building",
            showInMenu: true,
            roles: [ROLES.ADMIN, ROLES.MANAGER, ROLES.ENGINEER],
        },

        children: [
            {
                path: "list",
                element: <ProjectsList />,
        meta: {
                    label: "لیست پروژه‌ها",
                    showInMenu: true,
                },
            },
            {
                path: "create",
                element: <ProjectCreate />,
        meta: {
                    label: "ایجاد پروژه",
                    showInMenu: true,
                    roles: [ROLES.ADMIN, ROLES.MANAGER],
                },
            },
        ],
    },

    {
        path: "/finance",
        element: <div />,
    meta: {
            label: "مالی",
            icon: "dollar",
            showInMenu: true,
            roles: [ROLES.ADMIN, ROLES.ACCOUNTANT],
        },

        children: [
            {
                path: "cost-analysis",
                element: <CostAnalysis />,
        meta: {
                    label: "تحلیل هزینه",
                    showInMenu: true,
                },
            },
        ],
    },
];
