import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Button } from "@/components/form/Button";
import { Input } from "@/components/form/Input";
import { Label } from "@/components/form/Label";
import { addNamedItem, canAddNamedItem, changeNamedList, type NamedListOperation } from "./named-list-rules";
import { localizeIssueMessage } from "./validation-issues";

type Props = {
  label: string;
  values: string[];
  onChange: (next: string[], operation?: NamedListOperation) => void;
  disabled?: boolean;
  editable?: boolean;
};

export function NamedListEditor({ label, values, onChange, disabled, editable = false }: Props) {
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
    onChange(next, {kind:'add',index:values.length,name:next[values.length]!});
  };

  const onRemove = (index: number) => {
    const change=changeNamedList(values,{kind:'remove',index}); onChange(change.next,change.operation);
  };

  return (
    <div className="space-y-2">
      <Label>{label}</Label>
      <ul className="space-y-1">
        {values.map((name, index) => (
          <li key={index} className="flex items-center gap-2 text-sm">
            {editable ? <>
              <Input aria-label={t("decisionSupport.criterionName", { index: index + 1 })}
                value={name} disabled={disabled} onChange={event => {
                  const change=changeNamedList(values,{kind:'rename',index,name:event.target.value});onChange(change.next,change.operation);
                }} />
              <Button type="button" size="sm" variant="ghost" disabled={disabled || index === 0}
                aria-label={t("decisionSupport.moveCriterionUp", { index: index + 1 })}
                onClick={() => { const change=changeNamedList(values,{kind:'move',from:index,to:index-1});onChange(change.next,change.operation); }}>↑</Button>
            </> : <span className="flex-1 rounded border border-border px-2 py-1">{name}</span>}
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
