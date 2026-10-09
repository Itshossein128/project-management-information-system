import { useState } from "react";
import { useTranslation } from "react-i18next";
import type { ProjectMember } from "@/app/lib/api/members";
import type { WBSFlatNode } from "@/app/lib/api/wbs";
import type { Activity } from "@/app/lib/api/activities";
import { Button } from "@/components/ui/sprint-button";

type Props = {
  members: ProjectMember[];
  wbsNodes?: WBSFlatNode[];
  activities?: Activity[];
  pending?: boolean;
  onSubmit: (body: Record<string, unknown>) => void;
};

export function AllocationFormPanel({
  members,
  wbsNodes = [],
  activities = [],
  pending,
  onSubmit,
}: Props) {
  const { t } = useTranslation();
  const [form, setForm] = useState({
    person_id: "",
    start_date: "",
    end_date: "",
    role: "",
    capacity_percent: "50",
    capacity_hours: "",
    work_location: "",
    wbs_id: "",
    activity_id: "",
    supervisor_id: "",
    status: "planned",
  });

  const people = members.filter((m) => m.user_id);
  const scopedActivities = form.wbs_id
    ? activities.filter((a) => a.wbs_id === form.wbs_id)
    : activities;

  return (
    <form
      className="space-y-3 p-1"
      onSubmit={(e) => {
        e.preventDefault();
        const body: Record<string, unknown> = {
          person_id: form.person_id,
          start_date: form.start_date,
          end_date: form.end_date,
          role: form.role,
          work_location: form.work_location,
          status: form.status,
        };
        if (form.capacity_hours) {
          body.capacity_hours = form.capacity_hours;
        } else {
          body.capacity_percent = form.capacity_percent;
        }
        if (form.wbs_id) body.wbs_id = form.wbs_id;
        if (form.activity_id) body.activity_id = form.activity_id;
        if (form.supervisor_id) body.supervisor_id = form.supervisor_id;
        onSubmit(body);
      }}
    >
      <label className="block text-sm">
        <span className="mb-1 block">{t("hr.capacity.person")}</span>
        <select
          className="w-full rounded-md border bg-background px-2 py-1.5"
          required
          value={form.person_id}
          onChange={(e) => setForm((f) => ({ ...f, person_id: e.target.value }))}
        >
          <option value="">{t("hr.capacity.selectPerson")}</option>
          {people.map((m) => (
            <option key={m.user_id!} value={m.user_id!}>
              {m.full_name || m.email || m.user_id}
            </option>
          ))}
        </select>
      </label>
      <label className="block text-sm">
        <span className="mb-1 block">{t("hr.capacity.role")}</span>
        <input
          className="w-full rounded-md border bg-background px-2 py-1.5"
          required
          value={form.role}
          onChange={(e) => setForm((f) => ({ ...f, role: e.target.value }))}
        />
      </label>
      <div className="grid grid-cols-2 gap-2">
        <label className="block text-sm">
          <span className="mb-1 block">{t("common.fromDate")}</span>
          <input
            type="date"
            className="w-full rounded-md border bg-background px-2 py-1.5"
            required
            value={form.start_date}
            onChange={(e) => setForm((f) => ({ ...f, start_date: e.target.value }))}
          />
        </label>
        <label className="block text-sm">
          <span className="mb-1 block">{t("common.toDate")}</span>
          <input
            type="date"
            className="w-full rounded-md border bg-background px-2 py-1.5"
            required
            value={form.end_date}
            onChange={(e) => setForm((f) => ({ ...f, end_date: e.target.value }))}
          />
        </label>
      </div>
      <label className="block text-sm">
        <span className="mb-1 block">{t("hr.capacity.capacityPercent")}</span>
        <input
          type="number"
          min="0"
          step="0.01"
          className="w-full rounded-md border bg-background px-2 py-1.5"
          value={form.capacity_percent}
          disabled={!!form.capacity_hours}
          onChange={(e) => setForm((f) => ({ ...f, capacity_percent: e.target.value }))}
        />
      </label>
      <label className="block text-sm">
        <span className="mb-1 block">{t("hr.capacity.capacityHours")}</span>
        <input
          type="number"
          min="0"
          step="0.01"
          className="w-full rounded-md border bg-background px-2 py-1.5"
          value={form.capacity_hours}
          onChange={(e) => setForm((f) => ({ ...f, capacity_hours: e.target.value }))}
        />
      </label>
      <label className="block text-sm">
        <span className="mb-1 block">{t("hr.capacity.wbs")}</span>
        <select
          className="w-full rounded-md border bg-background px-2 py-1.5"
          value={form.wbs_id}
          onChange={(e) =>
            setForm((f) => ({ ...f, wbs_id: e.target.value, activity_id: "" }))
          }
        >
          <option value="">{t("hr.capacity.optional")}</option>
          {wbsNodes.map((n) => (
            <option key={n.wbs_id} value={n.wbs_id}>
              {n.wbs_code} — {n.wbs_name}
            </option>
          ))}
        </select>
      </label>
      <label className="block text-sm">
        <span className="mb-1 block">{t("hr.capacity.activity")}</span>
        <select
          className="w-full rounded-md border bg-background px-2 py-1.5"
          value={form.activity_id}
          onChange={(e) => setForm((f) => ({ ...f, activity_id: e.target.value }))}
        >
          <option value="">{t("hr.capacity.optional")}</option>
          {scopedActivities.map((a) => (
            <option key={a.activity_id} value={a.activity_id}>
              {a.activity_code} — {a.activity_name}
            </option>
          ))}
        </select>
      </label>
      <label className="block text-sm">
        <span className="mb-1 block">{t("hr.capacity.supervisor")}</span>
        <select
          className="w-full rounded-md border bg-background px-2 py-1.5"
          value={form.supervisor_id}
          onChange={(e) => setForm((f) => ({ ...f, supervisor_id: e.target.value }))}
        >
          <option value="">{t("hr.capacity.optional")}</option>
          {people.map((m) => (
            <option key={m.user_id!} value={m.user_id!}>
              {m.full_name || m.email || m.user_id}
            </option>
          ))}
        </select>
      </label>
      <label className="block text-sm">
        <span className="mb-1 block">{t("hr.capacity.location")}</span>
        <input
          className="w-full rounded-md border bg-background px-2 py-1.5"
          value={form.work_location}
          onChange={(e) => setForm((f) => ({ ...f, work_location: e.target.value }))}
        />
      </label>
      <Button type="submit" size="sm" disabled={pending} className="w-full">
        {t("common.save")}
      </Button>
    </form>
  );
}
