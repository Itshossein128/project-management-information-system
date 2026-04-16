import { Eye, EyeOff } from "lucide-react";
import * as React from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

/**
 * Form middleware: password input with visibility toggle.
 * Forwards all input props; type is controlled internally.
 */
function PasswordInput({
  type: _type,
  className,
  ...props
}: React.ComponentProps<"input">) {
  const [visible, setVisible] = React.useState(false);

  return (
    <div className='relative'>
      <Input
        dir='ltr'
        type={visible ? "text" : "password"}
        autoComplete='current-password'
        className={className}
        {...props}
      />
      <Button

        type='button'
        variant='ghost'
        size='icon'
        aria-label={visible ? "Hide password" : "Show password"}
        className='absolute right-1 top-1/2 -translate-y-1/2 h-7 w-7 text-muted-foreground hover:text-foreground'
        onClick={() => setVisible((v) => !v)}
      >
        {visible ? <EyeOff size={16} /> : <Eye size={16} />}
      </Button>
    </div>
  );
}

export { PasswordInput };
