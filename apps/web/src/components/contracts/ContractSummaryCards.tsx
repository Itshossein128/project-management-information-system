import {
  CONTRACT_TYPE_LABELS,
  formatFaAmount,
  type ContractDetail,
} from "@/app/lib/api/contracts";

export function ContractSummaryCards({ contract }: { contract: ContractDetail }) {
  const billed = contract.change_orders.reduce((s, co) => s + co.amount_change, 0);
  const effective = contract.effective_amount;

  return (
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      <div className="rounded-lg border p-4">
        <p className="text-sm text-muted-foreground">نوع قرارداد</p>
        <p className="text-lg font-semibold">
          {CONTRACT_TYPE_LABELS[contract.contract_type] ?? contract.contract_type}
        </p>
      </div>
      <div className="rounded-lg border p-4">
        <p className="text-sm text-muted-foreground">مبلغ قرارداد</p>
        <p className="text-lg font-semibold">{formatFaAmount(effective)}</p>
      </div>
      <div className="rounded-lg border p-4">
        <p className="text-sm text-muted-foreground">پیش‌پرداخت</p>
        <p className="text-lg font-semibold">{formatFaAmount(contract.advance_amount)}</p>
      </div>
      <div className="rounded-lg border p-4">
        <p className="text-sm text-muted-foreground">تغییرات تأییدشده</p>
        <p className="text-lg font-semibold">{formatFaAmount(billed)}</p>
      </div>
    </div>
  );
}
