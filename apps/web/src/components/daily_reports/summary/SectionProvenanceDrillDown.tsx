import { useState } from "react";
import { useTranslation } from "react-i18next";

import { apiJson, ApiRequestError } from "@/app/lib/api-client";

interface ProvenanceRow {
  source_unit?: string | null;
  href?: string | null;
  can_view_source?: boolean;
  source_row_id?: string;
}

export function SectionProvenanceDrillDown({
  projectId,
  reportId,
  derivedKind,
  derivedRowId,
}: {
  projectId: string;
  reportId: string;
  derivedKind: string;
  derivedRowId: string;
}) {
  const { t } = useTranslation();
  const [rows, setRows] = useState<ProvenanceRow[] | null>(null);
  const [denied, setDenied] = useState(false);

  async function open() {
    try {
      const payload = await apiJson<{ rows: ProvenanceRow[] }>(
        `/api/v1/projects/${projectId}/daily-reports/${reportId}/provenance/${derivedKind}/${derivedRowId}/`,
      );
      setRows(payload.rows);
      setDenied(false);
    } catch (err) {
      if (err instanceof ApiRequestError && (err.status === 403 || err.status === 404)) {
        setDenied(true);
        setRows(null);
      }
    }
  }

  return (
    <div>
      <button type="button" className="text-xs underline" onClick={() => void open()}>
        {t("businessDepartment.unitReport.sections.issues.tab", { defaultValue: "Source" })}
      </button>
      {denied ? (
        <p role="status" className="text-xs">
          {t("businessDepartment.unitReport.sections.attachments.errors.reference_not_in_project_scope")}
        </p>
      ) : null}
      {rows?.map((row) =>
        row.can_view_source && row.href ? (
          <a key={row.source_row_id} href={row.href} className="block text-xs underline">
            {row.source_unit}
          </a>
        ) : (
          <p key={row.source_row_id} className="text-xs">
            {t("businessDepartment.unitReport.sections.attachments.errors.reference_not_in_project_scope")}
          </p>
        ),
      )}
    </div>
  );
}
