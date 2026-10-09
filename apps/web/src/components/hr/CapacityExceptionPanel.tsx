import { useTranslation } from "react-i18next";
import type { CapacityException } from "@/app/lib/api/hr-capacity";
import { Button } from "@/components/ui/sprint-button";
import { Badge } from "@/components/ui/badge";

type Props = {
  projectId: string;
  exceptions: CapacityException[];
  canApprove: boolean;
  canEdit: boolean;
  onSubmit: (id: string) => Promise<unknown>;
  onApprove: (id: string) => Promise<unknown>;
  onReject: (id: string) => Promise<unknown>;
};

export function CapacityExceptionPanel({
  exceptions,
  canApprove,
  canEdit,
  onSubmit,
  onApprove,
  onReject,
}: Props) {
  const { t } = useTranslation();
  if (exceptions.length === 0) return null;

  return (
    <section className="space-y-2">
      <h2 className="text-lg font-semibold">{t("hr.capacity.exceptionsTitle")}</h2>
      <ul className="space-y-2">
        {exceptions.map((ex) => (
          <li
            key={ex.id}
            className="flex flex-wrap items-center justify-between gap-2 rounded-md border p-3 text-sm"
          >
            <div>
              <Badge variant="neutral" label={ex.status} />
              <p className="mt-1">
                {ex.start_date} → {ex.end_date} · {ex.requested_capacity_percent}%
              </p>
              <p className="text-muted-foreground">{ex.reason || "—"}</p>
            </div>
            <div className="flex flex-wrap gap-2">
              {canEdit && ex.status === "draft" && (
                <Button size="sm" variant="secondary" onClick={() => void onSubmit(ex.id)}>
                  {t("common.submit")}
                </Button>
              )}
              {canApprove && ex.status === "submitted" && (
                <>
                  <Button size="sm" onClick={() => void onApprove(ex.id)}>
                    {t("common.approve")}
                  </Button>
                  <Button size="sm" variant="secondary" onClick={() => void onReject(ex.id)}>
                    {t("common.reject")}
                  </Button>
                </>
              )}
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
}
