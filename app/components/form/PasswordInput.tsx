import * as React from "react";
import { Input } from "~/components/ui/input";

/**
 * Form middleware: password input. Single place to swap the underlying component.
 * Forwards all input props; type is fixed to "password".
 */
function PasswordInput({
  type: _type,
  ...props
}: React.ComponentProps<"input">) {
  return <Input type="password" autoComplete="current-password" {...props} />;
}

export { PasswordInput };
