import * as React from "react";

import { Switch, SwitchTrack } from "@/components/ui/switch";
import { cn } from "@/app/lib/utils";

export interface ToggleSwitchProps
  extends Omit<React.ComponentProps<"input">, "type" | "role"> {
  name: string;
  label?: React.ReactNode;
  containerClassName?: string;
}

export function ToggleSwitch({
  name,
  label,
  id,
  containerClassName,
  className,
  ...props
}: ToggleSwitchProps) {
  const inputId = typeof id === "string" && id.trim() ? id.trim() : `toggle-${name}`;
  return (
    <div
      id={`container-${name}Toggle`}
      className={cn("flex items-center gap-2", containerClassName)}
    >
      <Switch id={inputId} className={className} {...props} />
      <SwitchTrack id={`toggle-${name}Track`} htmlFor={inputId} />
      {label ? (
        <span id={`text-${name}ToggleLabel`} className="text-sm">
          {label}
        </span>
      ) : null}
    </div>
  );
}
