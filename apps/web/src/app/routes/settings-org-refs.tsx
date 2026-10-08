import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import {
  asList,
  createContractType,
  createOrganizationUnit,
  fetchContractTypes,
  fetchOrganizationUnits,
} from "@/app/lib/api/central-data";
import { Breadcrumb, PageHeader } from "@/components/layout/page-header";
import { Button } from "@/components/ui/sprint-button";
import { Input } from "@/components/form";
import { Label } from "@/components/ui/label";
import { useToast } from "@/components/ui/toast";

export default function SettingsOrgRefsPage() {
  const { t } = useTranslation();
  const toast = useToast();
  const qc = useQueryClient();

  const [unitCode, setUnitCode] = useState("");
  const [unitName, setUnitName] = useState("");
  const [typeCode, setTypeCode] = useState("");
  const [typeNameFa, setTypeNameFa] = useState("");
  const [typeNameEn, setTypeNameEn] = useState("");

  const { data: unitsRaw, isLoading: unitsLoading } = useQuery({
    queryKey: ["organization-units"],
    queryFn: fetchOrganizationUnits,
  });
  const units = asList(unitsRaw ?? []);

  const { data: typesRaw, isLoading: typesLoading } = useQuery({
    queryKey: ["contract-types"],
    queryFn: fetchContractTypes,
  });
  const types = asList(typesRaw ?? []);

  const createUnit = useMutation({
    mutationFn: () =>
      createOrganizationUnit({ code: unitCode.trim(), name: unitName.trim() }),
    onSuccess: () => {
      toast.success(t("centralData.unitCreated", "واحد سازمانی ایجاد شد"));
      setUnitCode("");
      setUnitName("");
      void qc.invalidateQueries({ queryKey: ["organization-units"] });
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const createType = useMutation({
    mutationFn: () =>
      createContractType({
        code: typeCode.trim(),
        name_fa: typeNameFa.trim(),
        name_en: typeNameEn.trim() || typeNameFa.trim(),
        is_active: true,
      }),
    onSuccess: () => {
      toast.success(t("centralData.typeCreated", "نوع قرارداد ایجاد شد"));
      setTypeCode("");
      setTypeNameFa("");
      setTypeNameEn("");
      void qc.invalidateQueries({ queryKey: ["contract-types"] });
    },
    onError: (e: Error) => toast.error(e.message),
  });

  return (
    <main
      className="page-main page-shell mx-auto max-w-4xl px-4 py-8"
      data-testid="org-refs-page"
    >
      <Breadcrumb
        items={[
          { label: t("nav.settings", "تنظیمات") },
          { label: t("centralData.orgRefs", "مراجع سازمانی") },
        ]}
      />
      <PageHeader
        title={t("centralData.orgRefs", "مراجع سازمانی")}
        subtitle={t(
          "centralData.orgRefsSubtitle",
          "واحدهای سازمانی و انواع قرارداد مدیریت‌شده",
        )}
      />

      <section className="mb-10 space-y-4">
        <h2 className="text-base font-semibold">
          {t("centralData.organizationUnits", "واحدهای سازمانی")}
        </h2>
        <form
          className="grid gap-3 sm:grid-cols-3"
          onSubmit={(e) => {
            e.preventDefault();
            if (!unitCode.trim() || !unitName.trim()) return;
            createUnit.mutate();
          }}
        >
          <div>
            <Label htmlFor="org-unit-code">{t("centralData.code", "کد")}</Label>
            <Input
              id="org-unit-code"
              data-testid="org-unit-code"
              value={unitCode}
              onChange={(e) => setUnitCode(e.target.value)}
              required
            />
          </div>
          <div>
            <Label htmlFor="org-unit-name">{t("centralData.name", "نام")}</Label>
            <Input
              id="org-unit-name"
              data-testid="org-unit-name"
              value={unitName}
              onChange={(e) => setUnitName(e.target.value)}
              required
            />
          </div>
          <div className="flex items-end">
            <Button
              type="submit"
              data-testid="org-unit-create-btn"
              loading={createUnit.isPending}
            >
              {t("common.create", "ایجاد")}
            </Button>
          </div>
        </form>
        {unitsLoading ? (
          <p className="text-sm text-muted-foreground">{t("common.loading")}</p>
        ) : (
          <ul
            className="divide-y divide-border rounded-lg border border-border"
            data-testid="org-unit-list"
          >
            {units.map((u) => (
              <li key={u.id} className="px-4 py-2 text-sm">
                {u.code} — {u.name}
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="space-y-4">
        <h2 className="text-base font-semibold">
          {t("centralData.contractTypes", "انواع قرارداد")}
        </h2>
        <form
          className="grid gap-3 sm:grid-cols-4"
          onSubmit={(e) => {
            e.preventDefault();
            if (!typeCode.trim() || !typeNameFa.trim()) return;
            createType.mutate();
          }}
        >
          <div>
            <Label htmlFor="contract-type-code">{t("centralData.code", "کد")}</Label>
            <Input
              id="contract-type-code"
              data-testid="contract-type-code"
              value={typeCode}
              onChange={(e) => setTypeCode(e.target.value)}
              required
            />
          </div>
          <div>
            <Label htmlFor="contract-type-name-fa">
              {t("centralData.nameFa", "نام فارسی")}
            </Label>
            <Input
              id="contract-type-name-fa"
              data-testid="contract-type-name-fa"
              value={typeNameFa}
              onChange={(e) => setTypeNameFa(e.target.value)}
              required
            />
          </div>
          <div>
            <Label htmlFor="contract-type-name-en">
              {t("centralData.nameEn", "نام انگلیسی")}
            </Label>
            <Input
              id="contract-type-name-en"
              data-testid="contract-type-name-en"
              value={typeNameEn}
              onChange={(e) => setTypeNameEn(e.target.value)}
            />
          </div>
          <div className="flex items-end">
            <Button
              type="submit"
              data-testid="contract-type-create-btn"
              loading={createType.isPending}
            >
              {t("common.create", "ایجاد")}
            </Button>
          </div>
        </form>
        {typesLoading ? (
          <p className="text-sm text-muted-foreground">{t("common.loading")}</p>
        ) : (
          <ul
            className="divide-y divide-border rounded-lg border border-border"
            data-testid="contract-type-list"
          >
            {types.map((ct) => (
              <li key={ct.id} className="px-4 py-2 text-sm">
                {ct.code} — {ct.name_fa || ct.name_en}
              </li>
            ))}
          </ul>
        )}
      </section>
    </main>
  );
}
