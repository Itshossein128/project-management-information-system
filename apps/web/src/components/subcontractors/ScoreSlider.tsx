interface Props {
  label: string;
  value: number;
  onChange: (v: number) => void;
}

export function ScoreSlider({ label, value, onChange }: Props) {
  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between text-sm">
        <span>{label}</span>
        <span className="font-medium tabular-nums">{value.toFixed(1)}</span>
      </div>
      <input
        type="range"
        min={0}
        max={10}
        step={0.5}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="w-full accent-amber-600"
      />
    </div>
  );
}
