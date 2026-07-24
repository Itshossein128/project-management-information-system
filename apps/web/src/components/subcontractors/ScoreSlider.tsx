import { Slider } from "@/components/ui/slider";

interface Props {
  label: string;
  value: number;
  onChange: (v: number) => void;
}

export function ScoreSlider({ label, value, onChange }: Props) {
  return (
    <div className="space-y-1 group">
      <div className="flex items-center justify-between text-sm">
        <span className="group-hover:text-warning-600 transition-colors font-medium">{label}</span>
        <span className="font-semibold tabular-nums px-2 py-0.5 bg-warning-100 text-warning-800 rounded-md">{value.toFixed(1)}</span>
      </div>
      <Slider
        min={0}
        max={10}
        step={0.5}
        value={[value]}
        onValueChange={(vals) => onChange(vals[0])}
        className="pt-2 [&_[data-slot=slider-range]]:bg-warning-600 [&_[data-slot=slider-thumb]]:border-warning-600 [&_[data-slot=slider-thumb]]:hover:ring-warning-200 [&_[data-slot=slider-thumb]]:focus-visible:ring-warning-200"
      />
    </div>
  );
}
