import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";

import { asList, fetchProjectContractors } from "@/app/lib/api/central-data";
import { cn } from "@/app/lib/utils";
import { Field, type FieldProps } from "@/components/form/Field";
import {
  Select as ShadcnSelect,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

export type ContractorSelectProps = {
  projectId: string;
  name: string;
  value?: string;
  onChange?: (value: string) => void;
  label?: FieldProps["label"];
  helpText?: FieldProps["helpText"];
  error?: FieldProps["error"];
  fieldClassName?: string;
  className?: string;
  placeholder?: string;
  disabled?: boolean;
  id?: string;
  sticky?: FieldProps["sticky"];
  onStickyChange?: FieldProps["onStickyChange"];
  stickyAriaLabel?: FieldProps["stickyAriaLabel"];
};

export function ContractorSelect({
  projectId,
  name,
  value = "",
  onChange,
  label,
  helpText,
  error,
  fieldClassName,
  className,
  placeholder,
  disabled,
  id,
  sticky,
  onStickyChange,
  stickyAriaLabel,
}: ContractorSelectProps) {
  const { t, i18n } = useTranslation();
  const dir = i18n.dir();
  const selectId =
    typeof id === "string" && id.trim() ? id.trim() : `select-${name}`;

  const { data, isLoading } = useQuery({
    queryKey: ["project-contractors", projectId],
    queryFn: () => fetchProjectContractors(projectId),
    enabled: Boolean(projectId),
  });

  const options = asList(data ?? []).map((row) => ({
    value: String(row.id),
    label: row.organization_name
      ? `${row.name} (${row.organization_name})`
      : row.name,
  }));

  const emptyHelp =
    !isLoading && options.length === 0
      ? t(
          "contractors.emptyHelp",
          "No contractors yet. Add them on the stakeholders (ذینفعان) page.",
        )
      : helpText;

  return (
    <Field
      name={name}
      label={label}
      helpText={emptyHelp}
      error={error}
      htmlFor={selectId}
      className={fieldClassName}
      sticky={sticky}
      onStickyChange={onStickyChange}
      stickyAriaLabel={stickyAriaLabel}
    >
      {() => (
        <ShadcnSelect
          name={name}
          value={value || undefined}
          onValueChange={(next) => onChange?.(next)}
          disabled={disabled || isLoading}
          dir={dir}
        >
          <SelectTrigger
            id={selectId}
            className={cn("w-full", className)}
            data-testid={selectId}
          >
            <SelectValue
              placeholder={
                placeholder ??
                t("contractors.selectPlaceholder", "Select contractor")
              }
            />
          </SelectTrigger>
          <SelectContent>
            {options.map((opt) => (
              <SelectItem key={opt.value} value={opt.value}>
                {opt.label}
              </SelectItem>
            ))}
          </SelectContent>
        </ShadcnSelect>
      )}
    </Field>
  );
}
