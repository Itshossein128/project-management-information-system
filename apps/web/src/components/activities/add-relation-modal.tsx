import { useMutation, useQuery } from "@tanstack/react-query";
import { useEffect, useMemo, useState } from "react";
import {
  createActivityRelation,
  fetchActivities,
  type Activity,
  type RelationType,
} from "@/app/lib/api/activities";
import { Modal } from "@/components/overlay/modal";
import { Input } from "@/components/form";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/sprint-button";

const RELATION_TYPES: { value: RelationType; label: string }[] = [
  { value: "FS", label: "پایان به شروع (FS)" },
  { value: "SS", label: "شروع به شروع (SS)" },
  { value: "FF", label: "پایان به پایان (FF)" },
  { value: "SF", label: "شروع به پایان (SF)" },
];

export interface AddRelationModalProps {
  projectId: string;
  anchor: Activity;
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export function AddRelationModal({
  projectId,
  anchor,
  isOpen,
  onClose,
  onSuccess,
}: AddRelationModalProps) {
  const [role, setRole] = useState<"predecessor" | "successor">("predecessor");
  const [search, setSearch] = useState("");
  const [otherId, setOtherId] = useState("");
  const [relationType, setRelationType] = useState<RelationType>("FS");
  const [lagDays, setLagDays] = useState("0");
  const [inlineError, setInlineError] = useState<string | null>(null);

  const { data } = useQuery({
    queryKey: ["activities-picker", projectId, search],
    queryFn: () => fetchActivities(projectId, { search, per_page: 50 }),
    enabled: isOpen,
  });

  const options = useMemo(() => {
    return (data?.results ?? []).filter((a) => a.activity_id !== anchor.activity_id);
  }, [data?.results, anchor.activity_id]);

  useEffect(() => {
    if (!isOpen) return;
    setRole("predecessor");
    setSearch("");
    setOtherId("");
    setRelationType("FS");
    setLagDays("0");
    setInlineError(null);
  }, [isOpen, anchor.activity_id]);

  const mutation = useMutation({
    mutationFn: () =>
      createActivityRelation(projectId, anchor.activity_id, {
        role,
        ...(role === "predecessor"
          ? { successor_id: otherId }
          : { predecessor_id: otherId }),
        relation_type: relationType,
        lag_days: parseInt(lagDays, 10) || 0,
      }),
    onSuccess: () => {
      onSuccess();
      onClose();
    },
    onError: (err: Error) => setInlineError(err.message),
  });

  return (
    <Modal
      open={isOpen}
      onOpenChange={(open) => { if (!open) onClose(); }}
      title="افزودن ارتباط"
      idBase="addActivityRelation"
    >
      <div className="space-y-4">
        <p className="text-sm text-muted-foreground">
          فعالیت مرجع: <span className="font-mono font-medium text-foreground">{anchor.activity_code}</span>
          {" — "}
          {anchor.activity_name}
        </p>

        <fieldset className="space-y-2">
          <legend className="text-sm font-medium">این فعالیت نقش:</legend>
          <div className="flex gap-4 text-sm">
            <label className="flex items-center gap-2">
              <input
                type="radio"
                name="role"
                checked={role === "predecessor"}
                onChange={() => setRole("predecessor")}
              />
              پیش‌نیاز (predecessor)
            </label>
            <label className="flex items-center gap-2">
              <input
                type="radio"
                name="role"
                checked={role === "successor"}
                onChange={() => setRole("successor")}
              />
              جانشین (successor)
            </label>
          </div>
        </fieldset>

        <div className="space-y-2">
          <Label>فعالیت مرتبط</Label>
          <Input
            placeholder="جستجو بر اساس کد یا نام…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <select
            className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
            value={otherId}
            onChange={(e) => setOtherId(e.target.value)}
          >
            <option value="">انتخاب فعالیت…</option>
            {options.map((a) => (
              <option key={a.activity_id} value={a.activity_id}>
                {a.activity_code} — {a.activity_name}
              </option>
            ))}
          </select>
        </div>

        <div className="space-y-2">
          <Label>نوع ارتباط</Label>
          <select
            className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
            value={relationType}
            onChange={(e) => setRelationType(e.target.value as RelationType)}
          >
            {RELATION_TYPES.map((r) => (
              <option key={r.value} value={r.value}>{r.label}</option>
            ))}
          </select>
        </div>

        <div className="space-y-2">
          <Label>تأخیر (روز)</Label>
          <Input
            type="number"
            value={lagDays}
            onChange={(e) => setLagDays(e.target.value)}
          />
        </div>

        {inlineError ? (
          <p className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700 dark:bg-red-950/40 dark:text-red-300">
            {inlineError}
          </p>
        ) : null}

        <div className="flex justify-end gap-2 pt-2">
          <Button variant="secondary" onClick={onClose}>لغو</Button>
          <Button
            disabled={!otherId || mutation.isPending}
            onClick={() => {
              setInlineError(null);
              mutation.mutate();
            }}
          >
            ذخیره
          </Button>
        </div>
      </div>
    </Modal>
  );
}
