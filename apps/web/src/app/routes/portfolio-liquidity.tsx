import { useTranslation } from "react-i18next";
import { AllocationWorkbench } from "@/components/cashflow/allocation/AllocationWorkbench";
import { Breadcrumb, PageHeader } from "@/components/layout/page-header";
import { PATHS } from "@/app/routeVars";

export default function PortfolioLiquidityPage() {
  const { t } = useTranslation();

  return (
    <main className="page-main page-shell mx-auto max-w-7xl px-4 py-8">
      <Breadcrumb
        items={[
          { label: t("nav.projects", "پروژه‌ها"), href: `/${PATHS.PROJECT}` },
          { label: t("pages.portfolioLiquidity.title") },
        ]}
      />
      <PageHeader
        title={t("pages.portfolioLiquidity.title")}
        subtitle={t("pages.portfolioLiquidity.subtitle")}
      />
      <AllocationWorkbench />
    </main>
  );
}
