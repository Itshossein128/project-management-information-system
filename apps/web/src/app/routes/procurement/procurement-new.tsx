import { useProductTour } from "@/components/tour/useProductTour";
import { ProductTourButton } from "@/components/tour/ProductTourButton";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Link, useNavigate, useParams, useSearchParams } from "react-router";
import { useTranslation } from "react-i18next";
import { Button } from "@/components/ui/button";
import { PageHeader, Breadcrumb } from "@/components/layout/page-header";
import { ProjectProvider, useProject } from "~/contexts/project-context";
import { fetchBlocks, createRequisition, type RequisitionScope } from "~/lib/api/procurement";
import { fetchMaterials } from "~/lib/api/materials";
import { PATHS } from "~/routeVars";
import { useToast } from "@/components/ui/toast";

function ProcurementNewContent() {
  const { t } = useTranslation();
  const { startTour } = useProductTour({
    tourId: "procurement-new",
    steps: [
      {
        element: "[data-tour='requisition-scope']",
        popover: {
          title: t("tour.procurementNew.step1Title"),
          description: t("tour.procurementNew.step1Desc"),
        },
      },
      {
        element: "[data-tour='requisition-context']",
        popover: {
          title: t("tour.procurementNew.step3Title"),
          description: t("tour.procurementNew.step3Desc"),
        },
      },
      {
        element: "[data-tour='material-blocks']",
        popover: {
          title: t("tour.procurementNew.step2Title"),
          description: t("tour.procurementNew.step2Desc"),
        },
      },
      {
        element: "[data-tour='requisition-type']",
        popover: {
          title: t("tour.procurementNew.step9Title"),
          description: t("tour.procurementNew.step9Desc"),
        },
      },
      {
        element: "[data-tour='requisition-priority']",
        popover: {
          title: t("tour.procurementNew.step10Title"),
          description: t("tour.procurementNew.step10Desc"),
        },
      },
      {
        element: "[data-tour='required-by-date']",
        popover: {
          title: t("tour.procurementNew.step8Title"),
          description: t("tour.procurementNew.step8Desc"),
        },
      },
      {
        element: "[data-tour='provisional-grn']",
        popover: {
          title: t("tour.procurementNew.step4Title"),
          description: t("tour.procurementNew.step4Desc"),
        },
      },
      {
        element: "[data-tour='items-table']",
        popover: {
          title: t("tour.procurementNew.step5Title"),
          description: t("tour.procurementNew.step5Desc"),
        },
      },
      {
        element: "[data-tour='requisition-notes']",
        popover: {
          title: t("tour.procurementNew.step6Title"),
          description: t("tour.procurementNew.step6Desc"),
        },
      },
      {
        element: "[data-tour='submit-requisition']",
        popover: {
          title: t("tour.procurementNew.step7Title"),
          description: t("tour.procurementNew.step7Desc"),
        },
      },
    ],
  });

  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const toast = useToast();
  const qc = useQueryClient();
  const { projectId, project } = useProject();

  const initialScope = (searchParams.get("scope") === "workshop" ? "workshop" : "block") as RequisitionScope;
  const [scope, setScope] = useState<RequisitionScope>(initialScope);
  const [block, setBlock] = useState("");
  const [reqType, setReqType] = useState("planned");
  const [priority, setPriority] = useState("normal");
  const [requiredByDate, setRequiredByDate] = useState("");
  const [urgency, setUrgency] = useState("");
  const [notes, setNotes] = useState("");
  const [isGrnProvisional, setIsGrnProvisional] = useState(false);
  const [items, setItems] = useState([{ material: "", requested_qty: "", notes: "" }]);

  const { data: blocks = [] } = useQuery({
    queryKey: ["blocks", projectId, "standard"],
    queryFn: () => fetchBlocks(projectId, { standardOnly: true }),
  });

  const { data: rawMaterials = [] } = useQuery({
    queryKey: ["materials", projectId],
    queryFn: () => fetchMaterials(projectId),
  });

  const materials = Array.isArray(rawMaterials) ? rawMaterials : ((rawMaterials as any)?.results ?? []);

  const createMut = useMutation({
    mutationFn: (payload: any) => createRequisition(projectId, payload),
    onSuccess: () => {
      toast.success(t("pages.procurement.workshop.createSuccess"));
      void qc.invalidateQueries({ queryKey: ["procurement", projectId] });
      navigate(`/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_PROCUREMENT}`);
    },
    onError: (e: any) => toast.error(e.message || t("pages.procurement.workshop.createError")),
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (scope === "block" && !block) {
      return toast.error(t("pages.procurement.workshop.blockRequired"));
    }

    const validItems = items.filter((i: any) => i.material && i.requested_qty);
    if (validItems.length === 0) {
      return toast.error(t("pages.procurement.workshop.itemsRequired"));
    }

    const payload: Record<string, unknown> = {
      project: projectId,
      scope,
      requisition_type: reqType,
      priority,
      urgency,
      request_date: new Date().toISOString().split("T")[0],
      required_by_date: requiredByDate || null,
      is_grn_provisional: isGrnProvisional,
      notes,
      items: validItems.map((i: any) => ({
        material: i.material,
        requested_qty: parseFloat(i.requested_qty),
        notes: i.notes,
      })),
    };

    if (scope === "block") {
      payload.block = block;
    }

    createMut.mutate(payload);
  };

  const addItem = () => setItems([...items, { material: "", requested_qty: "", notes: "" }]);
  const removeItem = (idx: number) => setItems(items.filter((_, i) => i !== idx));

  if (!project) return null;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <PageHeader
          title={
            scope === "workshop"
              ? t("pages.procurement.workshop.newTitle")
              : t("pages.procurement.workshop.newBlockTitle")
          }
          subtitle={project.project_name}
        />
        <ProductTourButton onClick={startTour} />
      </div>

      <form onSubmit={handleSubmit} className="space-y-8 rounded-lg border border-border bg-card p-6">
        <fieldset className="space-y-3" data-tour="requisition-scope">
          <legend className="text-sm font-medium">{t("pages.procurement.workshop.scopeLabel")}</legend>
          <div className="flex flex-wrap gap-4">
            <label className="flex items-center gap-2 text-sm">
              <input
                type="radio"
                name="scope"
                value="block"
                checked={scope === "block"}
                onChange={() => setScope("block")}
              />
              {t("pages.procurement.workshop.scopeBlock")}
            </label>
            <label className="flex items-center gap-2 text-sm">
              <input
                type="radio"
                name="scope"
                value="workshop"
                checked={scope === "workshop"}
                onChange={() => setScope("workshop")}
              />
              {t("pages.procurement.workshop.scopeWorkshop")}
            </label>
          </div>
        </fieldset>

        {scope === "workshop" ? (
          <div
            className="rounded-lg border border-info-200 bg-info-50 p-4 text-sm text-info-900"
            data-tour="requisition-context"
          >
            {t("pages.procurement.workshop.workshopInfo")}
          </div>
        ) : blocks.length === 0 ? (
          <div
            className="rounded-lg border border-warning-200 bg-warning-50 p-4 text-sm text-warning-800"
            data-tour="requisition-context"
          >
            <p className="mb-2">{t("pages.procurement.blocks.noBlocksHint")}</p>
            <Link
              to={`/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_PROCUREMENT_BLOCKS}`}
              className="font-medium underline"
            >
              {t("pages.procurement.blocks.manage")}
            </Link>
          </div>
        ) : null}

        <div className="grid grid-cols-1 gap-6 md:grid-cols-2" data-tour="material-blocks">
          {scope === "block" && (
            <label className="flex flex-col gap-1 text-sm">
              <span>{t("pages.procurement.workshop.blockField")}</span>
              <select
                className="rounded-md border px-3 py-2"
                value={block}
                onChange={(e: any) => setBlock(e.target.value)}
                required
              >
                <option value="">{t("pages.procurement.workshop.selectBlock")}</option>
                {blocks.map((b: any) => (
                  <option key={b.id} value={b.id}>
                    {b.block_code} - {b.block_name}
                  </option>
                ))}
              </select>
            </label>
          )}
          <label className="flex flex-col gap-1 text-sm" data-tour="requisition-type">
            <span>{t("pages.procurement.workshop.reqType")}</span>
            <select
              className="rounded-md border px-3 py-2"
              value={reqType}
              onChange={(e) => {
                const nextType = e.target.value;
                setReqType(nextType);
                setPriority(
                  nextType === "fast_track" ? "high" : nextType === "post_facto" ? "emergency" : "normal",
                );
                if (nextType === "post_facto") setIsGrnProvisional(true);
              }}
            >
              <option value="planned">{t("pages.procurement.workshop.typePlanned")}</option>
              <option value="fast_track">{t("pages.procurement.workshop.typeFastTrack")}</option>
              <option value="post_facto">{t("pages.procurement.workshop.typePostFacto")}</option>
            </select>
          </label>
          <label className="flex flex-col gap-1 text-sm" data-tour="requisition-priority">
            <span>{t("pages.procurement.workshop.priority")}</span>
            <select className="rounded-md border px-3 py-2" value={priority} onChange={(e: any) => setPriority(e.target.value)}>
              <option value="normal">{t("pages.procurement.workshop.priorityNormal")}</option>
              <option value="high">{t("pages.procurement.workshop.priorityHigh")}</option>
              <option value="emergency">{t("pages.procurement.workshop.priorityEmergency")}</option>
            </select>
          </label>
          <label className="flex flex-col gap-1 text-sm">
            <span>{t("pages.procurement.workshop.urgency")}</span>
            <input
              type="text"
              className="rounded-md border px-3 py-2"
              value={urgency}
              onChange={(e: any) => setUrgency(e.target.value)}
              placeholder={t("pages.procurement.workshop.urgencyPlaceholder")}
            />
          </label>
          <label className="flex flex-col gap-1 text-sm" data-tour="required-by-date">
            <span>{t("pages.procurement.workshop.requiredByDate")}</span>
            <input
              type="date"
              className="rounded-md border px-3 py-2"
              value={requiredByDate}
              onChange={(e) => setRequiredByDate(e.target.value)}
            />
          </label>
        </div>

        {reqType === "post_facto" && (
          <label
            className="flex items-center gap-2 rounded border border-warning-200 bg-warning-50 p-3 text-sm text-warning-600"
            data-tour="provisional-grn"
          >
            <input type="checkbox" checked={isGrnProvisional} onChange={(e: any) => setIsGrnProvisional(e.target.checked)} />
            <span>{t("pages.procurement.workshop.provisionalGrn")}</span>
          </label>
        )}

        <div data-tour="items-table">
          <h3 className="mb-4 text-lg font-medium">{t("pages.procurement.workshop.itemsTitle")}</h3>
          <div className="space-y-4">
            {items.map((item, idx) => (
              <div key={idx} className="flex flex-wrap items-start gap-4 rounded border bg-muted/20 p-4">
                <label className="flex min-w-[200px] flex-1 flex-col gap-1 text-sm">
                  <span>{t("pages.procurement.workshop.material")}</span>
                  <select
                    className="rounded-md border px-3 py-2"
                    value={item.material}
                    onChange={(e: any) => {
                      const newItems = [...items];
                      newItems[idx].material = e.target.value;
                      setItems(newItems);
                    }}
                    required
                  >
                    <option value="">{t("pages.procurement.workshop.selectMaterial")}</option>
                    {materials.map((m: any) => (
                      <option key={m.id} value={m.id}>
                        {m.material_code} - {m.material_name}
                      </option>
                    ))}
                  </select>
                </label>
                <label className="flex w-32 flex-col gap-1 text-sm">
                  <span>{t("pages.procurement.workshop.quantity")}</span>
                  <input
                    type="number"
                    step="any"
                    min="0.0001"
                    className="rounded-md border px-3 py-2"
                    value={item.requested_qty}
                    onChange={(e: any) => {
                      const newItems = [...items];
                      newItems[idx].requested_qty = e.target.value;
                      setItems(newItems);
                    }}
                    required
                  />
                </label>
                <label className="flex min-w-[200px] flex-1 flex-col gap-1 text-sm">
                  <span>{t("pages.procurement.workshop.itemNotes")}</span>
                  <input
                    type="text"
                    className="rounded-md border px-3 py-2"
                    value={item.notes}
                    onChange={(e: any) => {
                      const newItems = [...items];
                      newItems[idx].notes = e.target.value;
                      setItems(newItems);
                    }}
                  />
                </label>
                <div className="pt-6">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => removeItem(idx)}
                    disabled={items.length === 1}
                    className="text-danger-500 hover:text-danger-700"
                  >
                    {t("common.delete")}
                  </Button>
                </div>
              </div>
            ))}
          </div>
          <Button type="button" variant="outline" className="mt-4" onClick={addItem}>
            {t("pages.procurement.workshop.addItem")}
          </Button>
        </div>

        <label className="flex flex-col gap-1 text-sm" data-tour="requisition-notes">
          <span>{t("pages.procurement.workshop.notes")}</span>
          <textarea className="rounded-md border px-3 py-2" rows={3} value={notes} onChange={(e: any) => setNotes(e.target.value)} />
        </label>

        <div className="flex gap-4 border-t border-border pt-4" data-tour="submit-requisition">
          <Button type="submit" variant="default" disabled={createMut.isPending}>
            {t("pages.procurement.workshop.saveDraft")}
          </Button>
          <Link to={`/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_PROCUREMENT}`}>
            <Button type="button" variant="outline">
              {t("common.cancel")}
            </Button>
          </Link>
        </div>
      </form>
    </div>
  );
}

export default function ProcurementNewPage() {
  const { projectId } = useParams();
  const { t } = useTranslation();

  return (
    <ProjectProvider projectId={projectId!}>
      <main className="page-main page-shell mx-auto px-4 py-8">
        <Breadcrumb
          items={[
            { label: t("project.title"), href: `/${PATHS.PROJECT}` },
            { label: t("pages.procurement.title"), href: `/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_PROCUREMENT}` },
            { label: t("pages.procurement.workshop.newBreadcrumb") },
          ]}
        />
        <ProcurementNewContent />
      </main>
    </ProjectProvider>
  );
}
