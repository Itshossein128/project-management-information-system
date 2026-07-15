interface Props {
  reasons: string[];
}

export function RiskBadge({ reasons }: Props) {
  return (
    <span
      title={reasons.join("\n")}
      className="cursor-help rounded bg-red-100 px-2 py-0.5 text-xs font-medium text-red-800"
    >
      در خطر
    </span>
  );
}
