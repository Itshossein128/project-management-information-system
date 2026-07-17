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
        <span className="group-hover:text-amber-600 transition-colors font-medium">{label}</span>
        <span className="font-semibold tabular-nums px-2 py-0.5 bg-amber-100 text-amber-800 rounded-md">{value.toFixed(1)}</span>
      </div>
      <Slider
        min={0}
        max={10}
        step={0.5}
        value={[value]}
        onValueChange={(vals) => onChange(vals[0])}
        className="pt-2 [&_[data-slot=slider-range]]:bg-amber-600 [&_[data-slot=slider-thumb]]:border-amber-600 [&_[data-slot=slider-thumb]]:hover:ring-amber-200 [&_[data-slot=slider-thumb]]:focus-visible:ring-amber-200"
      />
    </div>
  );
}
