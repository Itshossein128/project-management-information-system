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
  variant?: "form" | "filter";
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
  variant = "form",
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
    queryFn: async () => asList(await fetchProjectContractors(projectId)),
    enabled: Boolean(projectId),
  });

  const options = asList(data ?? []).map((row) => ({
    value: String(row.id),
    label: row.organization_name
      ? `${row.name} (${row.organization_name})`
      : row.name,
  }));

  const isEmpty = !isLoading && options.length === 0;
  const emptyHelp =
    isEmpty
      ? t(
          "contractors.emptyHelp",
          "No contractors yet. Add them on the stakeholders (ذینفعان) page.",
        )
      : helpText;

  return (
    <Field
      name={name}
      label={variant === "filter" ? <span className="sr-only">{label}</span> : label}
      helpText={variant === "filter" ? helpText : emptyHelp}
      error={error}
      htmlFor={selectId}
      className={fieldClassName}
      sticky={sticky}
      onStickyChange={onStickyChange}
      stickyAriaLabel={stickyAriaLabel}
    >
      {({ helpId, errorId }) => (
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
            aria-label={variant === "filter" && typeof label === "string" ? label : undefined}
            aria-invalid={error != null || undefined}
            aria-describedby={[
              (variant === "filter" ? helpText : emptyHelp) != null ? helpId : null,
              error != null ? errorId : null,
            ].filter(Boolean).join(" ") || undefined}
          >
            <SelectValue
              placeholder={
                variant === "filter" && isEmpty
                  ? t("contractors.emptyPlaceholder", "No contractors yet")
                  : placeholder ?? t("contractors.selectPlaceholder", "Select contractor")
              }
            />
          </SelectTrigger>
          <SelectContent position={variant === "filter" ? "popper" : "item-aligned"}>
            {variant === "filter" && isEmpty ? (
              <p className="max-w-64 px-3 py-2 text-start text-sm leading-6 text-muted-foreground" dir={dir}>
                {emptyHelp}
              </p>
            ) : null}
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
