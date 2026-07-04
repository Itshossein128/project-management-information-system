import * as React from "react";

import { cn } from "src/app/lib/utils";

// Function to manage Card
function Card({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <div
      data-slot='card'
      className={cn(
        "bg-card text-card-foreground flex flex-col gap-4 rounded-xl border border-border/80 py-4 sm:gap-6 sm:py-6",
        "shadow-[var(--shadow-card)]",
        className,
      )}
      {...props}
    />
  );
}

// Function to manage CardHeader
function CardHeader({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <div
      data-slot='card-header'
      className={cn(
        "@container/card-header grid auto-rows-min grid-rows-[auto_auto] items-start gap-2 px-4 has-data-[slot=card-action]:grid-cols-1 has-data-[slot=card-action]:sm:grid-cols-[1fr_auto] sm:px-6 [.border-b]:pb-4 sm:[.border-b]:pb-6",
        className,
      )}
      {...props}
    />
  );
}

// Function to manage CardTitle
function CardTitle({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <div
      data-slot='card-title'
      className={cn("leading-none font-semibold", className)}
      {...props}
    />
  );
}

// Function to manage CardDescription
function CardDescription({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <div
      data-slot='card-description'
      className={cn("text-muted-foreground text-sm", className)}
      {...props}
    />
  );
}

// Function to manage CardAction
function CardAction({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <div
      data-slot='card-action'
      className={cn(
        "col-start-2 row-span-2 row-start-1 self-start justify-self-end",
        className,
      )}
      {...props}
    />
  );
}

// Function to manage CardContent
function CardContent({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <div
      data-slot='card-content'
      className={cn("px-4 sm:px-6", className)}
      {...props}
    />
  );
}

// Function to manage CardFooter
function CardFooter({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <div
      data-slot='card-footer'
      className={cn("flex items-center px-4 sm:px-6 [.border-t]:pt-4 sm:[.border-t]:pt-6", className)}
      {...props}
    />
  );
}

export {
  Card,
  CardAction,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
};
