import * as React from "react";

import { Switch } from "@/components/ui/switch";
import { cn } from "@/app/lib/utils";

export interface ToggleSwitchProps
  extends Omit<React.ComponentProps<typeof Switch>, "onChange" | "onCheckedChange" | "checked" | "type" | "role" | "value"> {
  name: string;
  label?: React.ReactNode;
  containerClassName?: string;
  checked?: boolean;
  value?: string | boolean | number | readonly string[];
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
}

export function ToggleSwitch({
  name,
  label,
  id,
  containerClassName,
  className,
  checked,
  value,
  onChange,
  ...props
}: ToggleSwitchProps) {
  const inputId = typeof id === "string" && id.trim() ? id.trim() : `toggle-${name}`;

  // Radix Switch takes an `onCheckedChange` and `checked`.
  // We need to bridge react-hook-form or traditional onChange to Radix.
  const isChecked = checked !== undefined ? checked : (value === true || value === "true");

  return (
    <div
      id={`container-${name}Toggle`}
      className={cn("flex items-center gap-2 group", containerClassName)}
    >
      <Switch
        id={inputId}
        name={name}
        className={className}
        checked={isChecked}
        onCheckedChange={(newChecked: boolean) => {
          if (onChange) {
             onChange({
               target: { name, value: newChecked, checked: newChecked, type: "checkbox" },
             } as unknown as React.ChangeEvent<HTMLInputElement>);
          }
        }}
        {...props}
      />
      {label ? (
        <label id={`text-${name}ToggleLabel`} htmlFor={inputId} className="text-sm leading-none cursor-pointer group-hover:text-primary transition-colors">
          {label}
        </label>
      ) : null}
    </div>
  );
}
