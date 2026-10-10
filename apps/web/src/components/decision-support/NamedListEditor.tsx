import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Button } from "@/components/form/Button";
import { Input } from "@/components/form/Input";
import { Label } from "@/components/form/Label";
import { addNamedItem, canAddNamedItem } from "./named-list-rules";
import { localizeIssueMessage } from "./validation-issues";

type Props = {
  label: string;
  values: string[];
  onChange: (next: string[]) => void;
  disabled?: boolean;
};

export function NamedListEditor({ label, values, onChange, disabled }: Props) {
  const { t } = useTranslation();
  const [draft, setDraft] = useState("");
  const [localError, setLocalError] = useState<string | null>(null);

  const onAdd = () => {
    const { next, issues } = addNamedItem(values, draft);
    if (issues.length) {
      const first = issues[0]!;
      setLocalError(
        localizeIssueMessage({ code: first.code, message: first.message }, t),
      );
      return;
    }
    setLocalError(null);
    setDraft("");
    onChange(next);
  };

  const onRemove = (index: number) => {
    onChange(values.filter((_, i) => i !== index));
  };

  return (
    <div className="space-y-2">
      <Label>{label}</Label>
      <ul className="space-y-1">
        {values.map((name, index) => (
          <li key={`${name}-${index}`} className="flex items-center gap-2 text-sm">
            <span className="flex-1 rounded border border-border px-2 py-1">{name}</span>
            <Button
              type="button"
              variant="ghost"
              size="sm"
              disabled={disabled}
              onClick={() => onRemove(index)}
            >
              {t("common.remove", "Remove")}
            </Button>
          </li>
        ))}
      </ul>
      <div className="flex gap-2">
        <Input
          value={draft}
          disabled={disabled || !canAddNamedItem(values)}
          onChange={(e) => setDraft(e.target.value)}
          placeholder={t("decisionSupport.addName", "Add name")}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              e.preventDefault();
              onAdd();
            }
          }}
        />
        <Button type="button" disabled={disabled || !canAddNamedItem(values)} onClick={onAdd}>
          {t("common.add", "Add")}
        </Button>
      </div>
      {localError ? <p className="text-sm text-destructive">{localError}</p> : null}
    </div>
  );
}
