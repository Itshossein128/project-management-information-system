import * as React from "react";

import { cn } from "src/app/lib/utils";

export interface CheckboxProps
  extends Omit<React.ComponentProps<"input">, "type"> {
  indeterminate?: boolean;
}

// Function to manage Checkbox
function Checkbox({ className, indeterminate, ...props }: CheckboxProps) {
  // Variable holding ref
  const ref = React.useRef<HTMLInputElement | null>(null);

  React.useEffect(() => {
    if (!ref.current) return;
    ref.current.indeterminate = Boolean(indeterminate);
  }, [indeterminate]);

  return (
    <input
      ref={ref}
      type="checkbox"
      data-slot="checkbox"
      className={cn(
        "border-input text-primary focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px] dark:bg-input/30 h-4 w-4 rounded-sm border bg-transparent shadow-xs outline-none disabled:pointer-events-none disabled:cursor-not-allowed disabled:opacity-50",
        "accent-primary",
        className,
      )}
      {...props}
    />
  );
}

export { Checkbox };
