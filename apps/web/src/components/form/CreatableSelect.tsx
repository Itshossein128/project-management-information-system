import * as React from "react";
import { useTranslation } from "react-i18next";
import { Check, ChevronDown, Plus } from "lucide-react";

import { cn } from "@/app/lib/utils";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { Button } from "./Button";
import { Field, type FieldProps } from "./Field";
import { Input } from "./Input";
import type { SelectOption } from "./Select";

export type CreatableSelectProps = {
  name: string;
  value?: string;
  onChange?: (value: string) => void;
  options: SelectOption[];
  label?: FieldProps["label"];
  helpText?: FieldProps["helpText"];
  error?: FieldProps["error"];
  fieldClassName?: string;
  className?: string;
  placeholder?: string;
  searchPlaceholder?: string;
  addPlaceholder?: string;
  addLabel?: string;
  disabled?: boolean;
  required?: boolean;
  id?: string;
  sticky?: FieldProps["sticky"];
  onStickyChange?: FieldProps["onStickyChange"];
  stickyAriaLabel?: FieldProps["stickyAriaLabel"];
};

export function CreatableSelect({
  name,
  value = "",
  onChange,
  options,
  label,
  helpText,
  error,
  fieldClassName,
  className,
  placeholder,
  searchPlaceholder,
  addPlaceholder,
  addLabel,
  disabled,
  required,
  id,
  sticky,
  onStickyChange,
  stickyAriaLabel,
}: CreatableSelectProps) {
  const { i18n, t } = useTranslation();
  const dir = i18n.dir();

  const selectId =
    typeof id === "string" && id.trim() ? id.trim() : `select-${name}`;
  const searchInputId = `input-${name}Search`;
  const listboxId = `listbox-${name}`;

  const [open, setOpen] = React.useState(false);
  const [customOptions, setCustomOptions] = React.useState<SelectOption[]>([]);
  const [query, setQuery] = React.useState("");
  const searchRef = React.useRef<HTMLInputElement>(null);

  const allOptions = React.useMemo(() => {
    const byValue = new Map<string, SelectOption>();
    for (const opt of options) {
      byValue.set(opt.value, opt);
    }
    for (const opt of customOptions) {
      if (!byValue.has(opt.value)) {
        byValue.set(opt.value, opt);
      }
    }
    if (value.trim() && !byValue.has(value)) {
      byValue.set(value, { value, label: value });
    }
    return Array.from(byValue.values());
  }, [options, customOptions, value]);

  const normalizedQuery = query.trim().toLowerCase();

  const filteredOptions = React.useMemo(() => {
    if (!normalizedQuery) return allOptions;
    return allOptions.filter(
      (opt) =>
        opt.label.toLowerCase().includes(normalizedQuery) ||
        opt.value.toLowerCase().includes(normalizedQuery),
    );
  }, [allOptions, normalizedQuery]);

  const exactMatch = React.useMemo(
    () =>
      allOptions.some(
        (opt) =>
          opt.value.toLowerCase() === normalizedQuery ||
          opt.label.toLowerCase() === normalizedQuery,
      ),
    [allOptions, normalizedQuery],
  );

  const canAddCustom = query.trim() !== "" && !exactMatch;

  const selectedLabel =
    allOptions.find((opt) => opt.value === value)?.label ?? value;

  const selectOption = (next: string) => {
    onChange?.(next);
    setOpen(false);
    setQuery("");
  };

  const commitCustom = () => {
    const next = query.trim();
    if (!next || exactMatch) return;
    setCustomOptions((prev) =>
      prev.some((opt) => opt.value === next)
        ? prev
        : [...prev, { value: next, label: next }],
    );
    selectOption(next);
  };

  return (
    <Field
      name={name}
      label={label}
      helpText={helpText}
      error={error}
      htmlFor={selectId}
      className={fieldClassName}
      sticky={sticky}
      onStickyChange={onStickyChange}
      stickyAriaLabel={stickyAriaLabel}
    >
      {() => (
        <Popover
          open={open}
          onOpenChange={(next) => {
            if (disabled) return;
            setOpen(next);
            if (!next) setQuery("");
          }}
        >
          <PopoverTrigger asChild>
            <button
              id={selectId}
              type="button"
              role="combobox"
              aria-expanded={open}
              aria-controls={listboxId}
              aria-haspopup="listbox"
              aria-invalid={error != null || undefined}
              aria-required={required || undefined}
              disabled={disabled}
              dir={dir}
              className={cn(
                "border-input dark:bg-input/30 dark:hover:bg-input/50 flex h-9 w-full items-center justify-between gap-2 rounded-md border bg-transparent px-3 py-2 text-sm shadow-xs transition-[color,box-shadow] outline-none focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50 disabled:cursor-not-allowed disabled:opacity-50",
                !value && "text-muted-foreground",
                className,
              )}
            >
              <span className="truncate">
                {value ? selectedLabel : (placeholder ?? "")}
              </span>
              <ChevronDown className="size-4 shrink-0 opacity-50" aria-hidden />
            </button>
          </PopoverTrigger>

          <PopoverContent
            id={`popover-${name}`}
            align="start"
            dir={dir}
            className="w-(--radix-popover-trigger-width) p-0"
            onOpenAutoFocus={(e) => {
              e.preventDefault();
              searchRef.current?.focus();
            }}
          >
            <div className="border-b p-2">
              <Input
                ref={searchRef}
                id={searchInputId}
                name={`${name}Search`}
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder={
                  searchPlaceholder ??
                  addPlaceholder ??
                  t("form.creatableSelect.searchPlaceholder")
                }
                disabled={disabled}
                autoComplete="off"
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    e.preventDefault();
                    if (canAddCustom) {
                      commitCustom();
                      return;
                    }
                    const only = filteredOptions[0];
                    if (
                      filteredOptions.length === 1 &&
                      only &&
                      !only.disabled
                    ) {
                      selectOption(only.value);
                    }
                  }
                }}
              />
            </div>

            <ul
              id={listboxId}
              role="listbox"
              aria-label={typeof label === "string" ? label : name}
              className="max-h-48 overflow-y-auto p-1"
            >
              {filteredOptions.length === 0 ? (
                <li
                  id={`text-${name}NoResults`}
                  className="text-muted-foreground px-2 py-3 text-center text-sm"
                >
                  {t("form.creatableSelect.noResults")}
                </li>
              ) : (
                filteredOptions.map((opt) => {
                  const selected = opt.value === value;
                  return (
                    <li key={opt.value} role="option" aria-selected={selected}>
                      <button
                        type="button"
                        id={`option-${name}-${opt.value}`}
                        disabled={disabled || opt.disabled}
                        className={cn(
                          "hover:bg-accent hover:text-accent-foreground flex w-full items-center gap-2 rounded-sm px-2 py-1.5 text-sm outline-none disabled:pointer-events-none disabled:opacity-50",
                          selected && "bg-accent/60",
                        )}
                        onClick={() => selectOption(opt.value)}
                      >
                        <Check
                          className={cn(
                            "size-3.5 shrink-0",
                            selected ? "opacity-100" : "opacity-0",
                          )}
                          aria-hidden
                        />
                        <span className="truncate">{opt.label}</span>
                      </button>
                    </li>
                  );
                })
              )}
            </ul>

            <div className="border-t p-2">
              <Button
                id={`button-${name}AddCustom`}
                type="button"
                size="sm"
                variant="outline"
                disabled={disabled || !canAddCustom}
                onClick={commitCustom}
                className="w-full justify-start"
              >
                <Plus className="size-3.5" aria-hidden />
                {canAddCustom
                  ? `${addLabel ?? t("form.creatableSelect.add")} “${query.trim()}”`
                  : (addLabel ?? t("form.creatableSelect.add"))}
              </Button>
            </div>
          </PopoverContent>
        </Popover>
      )}
    </Field>
  );
}
