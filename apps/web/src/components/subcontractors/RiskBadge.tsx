import { AlertTriangle } from "lucide-react";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";

interface Props {
  reasons: string[];
}

export function RiskBadge({ reasons }: Props) {
  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <span
          className="cursor-help inline-flex items-center gap-1 rounded bg-danger-100 px-2 py-0.5 text-xs font-medium text-danger-800"
        >
          <AlertTriangle className="size-3" aria-hidden />
          در خطر
        </span>
      </TooltipTrigger>
      <TooltipContent className="max-w-[300px]" side="top">
        <ul className="list-disc pr-4 space-y-1 text-xs">
          {reasons.map((reason, i) => (
            <li key={i}>{reason}</li>
          ))}
        </ul>
      </TooltipContent>
    </Tooltip>
  );
}
