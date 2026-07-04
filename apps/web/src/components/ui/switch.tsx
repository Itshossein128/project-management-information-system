import * as React from "react";

import { cn } from "src/app/lib/utils";

export interface SwitchProps
  extends Omit<React.ComponentProps<"input">, "type"> {}

// Function to manage Switch
function Switch({ className, ...props }: SwitchProps) {
  return (
    <input
      type="checkbox"
      role="switch"
      data-slot="switch"
      className={cn(
        "peer sr-only",
        className,
      )}
      {...props}
    />
  );
}

/**
 * Visual wrapper for `Switch`.\n+ * Use:\n+ *  <Switch id=\"toggle-x\" ... />\n+ *  <SwitchTrack htmlFor=\"toggle-x\" />\n+ */
// Function to manage SwitchTrack
function SwitchTrack({
  className,
  ...props
}: React.ComponentProps<"label">) {
  return (
    <label
      data-slot="switch-track"
      className={cn(
        "border-input bg-muted inline-flex h-5 w-9 cursor-pointer items-center rounded-full border shadow-xs transition-colors",
        "peer-checked:bg-primary peer-checked:border-primary",
        "peer-focus-visible:ring-ring/50 peer-focus-visible:ring-[3px] peer-focus-visible:outline-none",
        "peer-disabled:cursor-not-allowed peer-disabled:opacity-50",
        className,
      )}
      {...props}
    >
      <span
        data-slot="switch-thumb"
        className={cn(
          "bg-background block h-4 w-4 translate-x-0.5 rounded-full shadow transition-transform",
          "peer-checked:translate-x-[1.1rem]",
        )}
      />
    </label>
  );
}

export { Switch, SwitchTrack };
