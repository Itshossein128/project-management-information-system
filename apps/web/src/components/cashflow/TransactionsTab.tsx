import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Plus, Trash2 } from "lucide-react";
import { useMemo, useState } from "react";
import { isoRangeToJalali, formatDisplayDate } from "@/app/lib/jalali-utils";
import {
  categoryLabel,
  createCashTransaction,
  deleteCashTransaction,
  fetchCashFlowList,
  formatFaAmount,
  INFLOW_CATEGORIES,
  OUTFLOW_CATEGORIES,
  type CashTransactionRow,
  type TxType,
} from "@/app/lib/api/cashflow";
import { JalaliDatePicker } from "@/components/form/JalaliDatePicker";
import { JalaliDateRangePicker } from "@/components/form/JalaliDateRangePicker";
import { Drawer } from "@/components/ui/drawer";
import { Button } from "@/components/ui/sprint-button";
import { useToast } from "@/components/ui/toast";
import { KPICard } from "@/components/progress/KPICard";

function TxTypeBadge({ type }: { type: TxType }) {
  return (
    <span
      className={
        type === "in"
          ? "inline-flex rounded-full bg-emerald-100 px-2 py-0.5 text-xs text-emerald-800"
          : "inline-flex rounded-full bg-red-100 px-2 py-0.5 text-xs text-red-800"
      }
    >
      {type === "in" ? "دریافت" : "پرداخت"}
    </span>
  );
}

function AddTransactionDrawer({
  projectId,
  open,
  onClose,
}: {
  projectId: string;
  open: boolean;
  onClose: () => void;
}) {
  const toast = useToast();
  const qc = useQueryClient();
  const [txDate, setTxDate] = useState("");
  const [txType, setTxType] = useState<TxType>("in");
  const [category, setCategory] = useState("other_income");
  const [amount, setAmount] = useState("");
  const [description, setDescription] = useState("");
  const [counterparty, setCounterparty] = useState("");
  const [documentRef, setDocumentRef] = useState("");
  const [isForecast, setIsForecast] = useState(false);
  const [dueDate, setDueDate] = useState("");

  const categories = txType === "in" ? INFLOW_CATEGORIES : OUTFLOW_CATEGORIES;

  const save = useMutation({
    mutationFn: () =>
      createCashTransaction(projectId, {
        tx_date: txDate,
        tx_type: txType,
        category,
        amount: Number(amount),
        description,
        counterparty,
        document_ref: documentRef,
        is_forecast: isForecast,
        due_date: isForecast && dueDate ? dueDate : null,
      }),
    onSuccess: () => {
      toast.success("تراکنش ثبت شد");
      qc.invalidateQueries({ queryKey: ["cash-flow", projectId] });
      onClose();
    },
    onError: (e: Error) => toast.error(e.message),
  });

  return (
    <Drawer
      isOpen={open}
      onClose={onClose}
      title="افزودن تراکنش"
      footer={
        <Button
          variant="primary"
          disabled={!txDate || !amount || save.isPending}
          loading={save.isPending}
          onClick={() => save.mutate()}
        >
          ذخیره
        </Button>
      }
    >
      <div className="flex flex-col gap-4">
        <JalaliDatePicker name="tx_date" label="تاریخ" value={txDate} onChange={setTxDate} />
        <fieldset className="flex gap-4">
          <label className="flex items-center gap-2">
            <input
              type="radio"
              checked={txType === "in"}
              onChange={() => {
                setTxType("in");
                setCategory("other_income");
              }}
            />
            دریافت
          </label>
          <label className="flex items-center gap-2">
            <input
              type="radio"
              checked={txType === "out"}
              onChange={() => {
                setTxType("out");
                setCategory("other_expense");
              }}
            />
            پرداخت
          </label>
        </fieldset>
        <label className="flex flex-col gap-1 text-sm">
          <span>دسته</span>
          <select
            className="rounded-md border border-input bg-background px-3 py-2"
            value={category}
            onChange={(e) => setCategory(e.target.value)}
          >
            {categories.map((c) => (
              <option key={c.value} value={c.value}>
                {c.label}
              </option>
            ))}
          </select>
        </label>
        <label className="flex flex-col gap-1 text-sm">
          <span>مبلغ (ریال)</span>
          <input
            type="number"
            className="rounded-md border border-input bg-background px-3 py-2"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
          />
        </label>
        <label className="flex flex-col gap-1 text-sm">
          <span>طرف مقابل</span>
          <input
            className="rounded-md border border-input bg-background px-3 py-2"
            value={counterparty}
            onChange={(e) => setCounterparty(e.target.value)}
          />
        </label>
        <label className="flex flex-col gap-1 text-sm">
          <span>توضیحات</span>
          <textarea
            className="rounded-md border border-input bg-background px-3 py-2"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
        </label>
        <label className="flex flex-col gap-1 text-sm">
          <span>شماره سند</span>
          <input
            className="rounded-md border border-input bg-background px-3 py-2"
            value={documentRef}
            onChange={(e) => setDocumentRef(e.target.value)}
          />
        </label>
        <label className="flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={isForecast}
            onChange={(e) => setIsForecast(e.target.checked)}
          />
          پیش‌بینی (forecast)
        </label>
        {isForecast && (
          <JalaliDatePicker name="due_date" label="موعد پرداخت" value={dueDate} onChange={setDueDate} />
        )}
      </div>
    </Drawer>
  );
}

export function TransactionsTab({
  projectId,
  canEdit,
}: {
  projectId: string;
  canEdit: boolean;
}) {
  const toast = useToast();
  const qc = useQueryClient();
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [txType, setTxType] = useState("");
  const [category, setCategory] = useState("");
  const [isForecast, setIsForecast] = useState("");
  const [counterparty, setCounterparty] = useState("");
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [sortKey, setSortKey] = useState<keyof CashTransactionRow>("tx_date");
  const [sortAsc, setSortAsc] = useState(false);

  const params = useMemo(() => {
    const jalali = isoRangeToJalali(dateFrom, dateTo);
    return {
      ...jalali,
      tx_type: txType || undefined,
      category: category || undefined,
      is_forecast: isForecast || undefined,
      counterparty: counterparty || undefined,
    };
  }, [dateFrom, dateTo, txType, category, isForecast, counterparty]);

  const { data, isLoading } = useQuery({
    queryKey: ["cash-flow", projectId, params],
    queryFn: () => fetchCashFlowList(projectId, params),
  });

  const rows = useMemo(() => {
    const list = [...(data?.results ?? [])];
    list.sort((a, b) => {
      const av = a[sortKey] ?? "";
      const bv = b[sortKey] ?? "";
      const cmp = String(av).localeCompare(String(bv), "fa");
      return sortAsc ? cmp : -cmp;
    });
    return list;
  }, [data?.results, sortKey, sortAsc]);

  const withBalance = useMemo(() => {
    const sorted = [...rows].sort((a, b) => a.tx_date.localeCompare(b.tx_date));
    let balance = 0;
    const map = new Map<string, number>();
    for (const row of sorted) {
      if (!row.is_forecast) {
        const amt = Number(row.amount);
        balance += row.tx_type === "in" ? amt : -amt;
      }
      map.set(row.id, balance);
    }
    return map;
  }, [rows]);

  const remove = useMutation({
    mutationFn: (id: string) => deleteCashTransaction(projectId, id),
    onSuccess: () => {
      toast.success("حذف شد");
      qc.invalidateQueries({ queryKey: ["cash-flow", projectId] });
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const toggleSort = (key: keyof CashTransactionRow) => {
    if (sortKey === key) setSortAsc(!sortAsc);
    else {
      setSortKey(key);
      setSortAsc(true);
    }
  };

  const summary = data?.summary;

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-end gap-3">
        <JalaliDateRangePicker
          name="dateRange"
          value={{ from: dateFrom, to: dateTo }}
          onChange={(v) => {
            if (v && v.from) setDateFrom(v.from);
            if (v && v.to) setDateTo(v.to);
          }}
        />
        <select
          className="rounded-md border border-input bg-background px-3 py-2 text-sm"
          value={txType}
          onChange={(e) => setTxType(e.target.value)}
        >
          <option value="">همه انواع</option>
          <option value="in">دریافت</option>
          <option value="out">پرداخت</option>
        </select>
        <input
          placeholder="جستجوی طرف مقابل"
          className="rounded-md border border-input bg-background px-3 py-2 text-sm"
          value={counterparty}
          onChange={(e) => setCounterparty(e.target.value)}
        />
        <select
          className="rounded-md border border-input bg-background px-3 py-2 text-sm"
          value={isForecast}
          onChange={(e) => setIsForecast(e.target.value)}
        >
          <option value="">همه</option>
          <option value="false">واقعی</option>
          <option value="true">پیش‌بینی</option>
        </select>
        {canEdit && (
          <Button variant="primary" onClick={() => setDrawerOpen(true)}>
            <Plus className="ms-1 size-4" />
            افزودن تراکنش
          </Button>
        )}
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <KPICard title="دریافتی کل" value={formatFaAmount(summary?.total_inflow)} />
        <KPICard title="پرداختی کل" value={formatFaAmount(summary?.total_outflow)} />
        <KPICard title="خالص" value={formatFaAmount(summary?.net_balance)} />
        <KPICard
          title="مانده تجمعی"
          value={formatFaAmount(
            rows.filter((r) => !r.is_forecast).reduce((acc, r) => {
              const amt = Number(r.amount);
              return acc + (r.tx_type === "in" ? amt : -amt);
            }, 0),
          )}
        />
      </div>

      {isLoading ? (
        <p className="text-muted-foreground">در حال بارگذاری...</p>
      ) : rows.length === 0 ? (
        <p className="rounded-lg border border-dashed p-8 text-center text-muted-foreground">
          تراکنشی یافت نشد
        </p>
      ) : (
        <div className="overflow-x-auto rounded-lg border">
          <table className="w-full min-w-[900px] text-sm">
            <thead className="bg-muted/50">
              <tr>
                {[
                  ["tx_date", "تاریخ"],
                  ["tx_type", "نوع"],
                  ["category", "دسته"],
                  ["amount", "مبلغ"],
                  ["counterparty", "طرف مقابل"],
                  ["description", "توضیحات"],
                  ["document_ref", "سند"],
                  ["source", "منبع"],
                  ["balance", "مانده"],
                ].map(([key, label]) => (
                  <th
                    key={key}
                    className="cursor-pointer px-3 py-2 text-start font-medium"
                    onClick={() => key !== "balance" && toggleSort(key as keyof CashTransactionRow)}
                  >
                    {label}
                  </th>
                ))}
                {canEdit && <th className="px-3 py-2">عملیات</th>}
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.id} className="border-t">
                  <td className="px-3 py-2">{formatDisplayDate(row.tx_date)}</td>
                  <td className="px-3 py-2">
                    <TxTypeBadge type={row.tx_type} />
                  </td>
                  <td className="px-3 py-2">{categoryLabel(row.category, row.tx_type)}</td>
                  <td
                    className={`px-3 py-2 font-medium ${row.tx_type === "in" ? "text-emerald-600" : "text-red-600"}`}
                  >
                    {row.amount_display}
                  </td>
                  <td className="px-3 py-2">{row.counterparty || "—"}</td>
                  <td className="max-w-[200px] truncate px-3 py-2">{row.description || "—"}</td>
                  <td className="px-3 py-2">{row.document_ref || "—"}</td>
                  <td className="px-3 py-2">{row.source === "ipc" ? "صدور موقت" : "مستقیم"}</td>
                  <td className="px-3 py-2">{formatFaAmount(withBalance.get(row.id))}</td>
                  {canEdit && (
                    <td className="px-3 py-2">
                      <button
                        type="button"
                        className="text-red-600"
                        onClick={() => remove.mutate(row.id)}
                        aria-label="حذف"
                      >
                        <Trash2 className="size-4" />
                      </button>
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <AddTransactionDrawer
        projectId={projectId}
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
      />
    </div>
  );
}
