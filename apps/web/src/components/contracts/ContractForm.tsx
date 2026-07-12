import type { ReactNode } from "react";
import { Input, JalaliDatePicker, Select, TextArea } from "@/components/form";
import { Label } from "@/components/ui/label";
import { CONTRACT_TYPE_LABELS } from "@/app/lib/api/contracts";

export interface ContractFormValues {
  contract_number: string;
  contract_type: string;
  counterparty: string;
  start_date: string;
  finish_date: string;
  original_amount: string;
  adjusted_amount: string;
  advance_payment_pct: string;
  retention_pct: string;
  insurance_pct: string;
  tax_pct: string;
  performance_guarantee_amount: string;
  performance_guarantee_expiry: string;
  advance_guarantee_amount: string;
  advance_guarantee_expiry: string;
  status: string;
  file_url: string;
  notes: string;
}

export const EMPTY_CONTRACT_FORM: ContractFormValues = {
  contract_number: "",
  contract_type: "main",
  counterparty: "",
  start_date: "",
  finish_date: "",
  original_amount: "",
  adjusted_amount: "",
  advance_payment_pct: "0",
  retention_pct: "0",
  insurance_pct: "0",
  tax_pct: "0",
  performance_guarantee_amount: "",
  performance_guarantee_expiry: "",
  advance_guarantee_amount: "",
  advance_guarantee_expiry: "",
  status: "active",
  file_url: "",
  notes: "",
};

const TYPE_OPTIONS = Object.entries(CONTRACT_TYPE_LABELS).map(([value, label]) => ({
  value,
  label,
}));

const STATUS_OPTIONS = [
  { value: "draft", label: "پیش‌نویس" },
  { value: "active", label: "فعال" },
  { value: "suspended", label: "معلق" },
  { value: "completed", label: "تکمیل‌شده" },
  { value: "terminated", label: "فسخ‌شده" },
];

function FormField({
  label,
  children,
  className,
}: {
  label: string;
  children: ReactNode;
  className?: string;
}) {
  return (
    <div className={className}>
      <Label className="mb-1 block text-sm">{label}</Label>
      {children}
    </div>
  );
}

export function ContractForm({
  values,
  onChange,
  disabled,
}: {
  values: ContractFormValues;
  onChange: (patch: Partial<ContractFormValues>) => void;
  disabled?: boolean;
}) {
  return (
    <div className="grid gap-4 md:grid-cols-2">
      <FormField label="شماره قرارداد">
        <Input
          name="contract_number"
          value={values.contract_number}
          disabled={disabled}
          onChange={(e) => onChange({ contract_number: e.target.value })}
        />
      </FormField>
      <Select
        name="contract_type"
        label="نوع"
        value={values.contract_type}
        disabled={disabled}
        options={TYPE_OPTIONS}
        onChange={(e) => onChange({ contract_type: e.target.value })}
      />
      <FormField label="طرف مقابل">
        <Input
          name="counterparty"
          value={values.counterparty}
          disabled={disabled}
          onChange={(e) => onChange({ counterparty: e.target.value })}
        />
      </FormField>
      <Select
        name="status"
        label="وضعیت"
        value={values.status}
        disabled={disabled}
        options={STATUS_OPTIONS}
        onChange={(e) => onChange({ status: e.target.value })}
      />
      <JalaliDatePicker
        name="start_date"
        label="تاریخ شروع"
        value={values.start_date}
        disabled={disabled}
        onChange={(v) => onChange({ start_date: v })}
      />
      <JalaliDatePicker
        name="finish_date"
        label="تاریخ پایان"
        value={values.finish_date}
        disabled={disabled}
        onChange={(v) => onChange({ finish_date: v })}
      />
      <FormField label="مبلغ اولیه">
        <Input
          name="original_amount"
          type="number"
          value={values.original_amount}
          disabled={disabled}
          onChange={(e) => onChange({ original_amount: e.target.value })}
        />
      </FormField>
      <FormField label="مبلغ تعدیل‌شده">
        <Input
          name="adjusted_amount"
          type="number"
          value={values.adjusted_amount}
          disabled={disabled}
          onChange={(e) => onChange({ adjusted_amount: e.target.value })}
        />
      </FormField>
      <FormField label="درصد پیش‌پرداخت">
        <Input
          name="advance_payment_pct"
          type="number"
          value={values.advance_payment_pct}
          disabled={disabled}
          onChange={(e) => onChange({ advance_payment_pct: e.target.value })}
        />
      </FormField>
      <FormField label="درصد سپرده">
        <Input
          name="retention_pct"
          type="number"
          value={values.retention_pct}
          disabled={disabled}
          onChange={(e) => onChange({ retention_pct: e.target.value })}
        />
      </FormField>
      <FormField label="درصد مالیات">
        <Input
          name="tax_pct"
          type="number"
          value={values.tax_pct}
          disabled={disabled}
          onChange={(e) => onChange({ tax_pct: e.target.value })}
        />
      </FormField>
      <FormField label="درصد بیمه">
        <Input
          name="insurance_pct"
          type="number"
          value={values.insurance_pct}
          disabled={disabled}
          onChange={(e) => onChange({ insurance_pct: e.target.value })}
        />
      </FormField>
      <FormField label="مبلغ ضمانت حسن انجام">
        <Input
          name="performance_guarantee_amount"
          type="number"
          value={values.performance_guarantee_amount}
          disabled={disabled}
          onChange={(e) => onChange({ performance_guarantee_amount: e.target.value })}
        />
      </FormField>
      <JalaliDatePicker
        name="performance_guarantee_expiry"
        label="انقضای ضمانت حسن انجام"
        value={values.performance_guarantee_expiry}
        disabled={disabled}
        onChange={(v) => onChange({ performance_guarantee_expiry: v })}
      />
      <FormField label="مبلغ ضمانت پیش‌پرداخت">
        <Input
          name="advance_guarantee_amount"
          type="number"
          value={values.advance_guarantee_amount}
          disabled={disabled}
          onChange={(e) => onChange({ advance_guarantee_amount: e.target.value })}
        />
      </FormField>
      <JalaliDatePicker
        name="advance_guarantee_expiry"
        label="انقضای ضمانت پیش‌پرداخت"
        value={values.advance_guarantee_expiry}
        disabled={disabled}
        onChange={(v) => onChange({ advance_guarantee_expiry: v })}
      />
      <FormField label="پیوست (URL)" className="md:col-span-2">
        <Input
          name="file_url"
          value={values.file_url}
          disabled={disabled}
          onChange={(e) => onChange({ file_url: e.target.value })}
        />
      </FormField>
      <FormField label="یادداشت" className="md:col-span-2">
        <TextArea
          name="notes"
          value={values.notes}
          disabled={disabled}
          rows={3}
          onChange={(e) => onChange({ notes: e.target.value })}
        />
      </FormField>
    </div>
  );
}

export function contractDetailToForm(c: {
  contract_number: string;
  contract_type: string;
  counterparty: string;
  start_date: string | null;
  finish_date: string | null;
  original_amount: number | null;
  adjusted_amount: number | null;
  advance_payment_pct: number;
  retention_pct: number;
  insurance_pct: number;
  tax_pct: number;
  performance_guarantee_amount: number | null;
  performance_guarantee_expiry: string | null;
  advance_guarantee_amount: number | null;
  advance_guarantee_expiry: string | null;
  status: string;
  file_url: string;
  notes: string;
}): ContractFormValues {
  return {
    contract_number: c.contract_number ?? "",
    contract_type: c.contract_type ?? "main",
    counterparty: c.counterparty ?? "",
    start_date: c.start_date ?? "",
    finish_date: c.finish_date ?? "",
    original_amount: c.original_amount != null ? String(c.original_amount) : "",
    adjusted_amount: c.adjusted_amount != null ? String(c.adjusted_amount) : "",
    advance_payment_pct: String(c.advance_payment_pct ?? 0),
    retention_pct: String(c.retention_pct ?? 0),
    insurance_pct: String(c.insurance_pct ?? 0),
    tax_pct: String(c.tax_pct ?? 0),
    performance_guarantee_amount:
      c.performance_guarantee_amount != null ? String(c.performance_guarantee_amount) : "",
    performance_guarantee_expiry: c.performance_guarantee_expiry ?? "",
    advance_guarantee_amount:
      c.advance_guarantee_amount != null ? String(c.advance_guarantee_amount) : "",
    advance_guarantee_expiry: c.advance_guarantee_expiry ?? "",
    status: c.status ?? "active",
    file_url: c.file_url ?? "",
    notes: c.notes ?? "",
  };
}

export function formToContractPayload(values: ContractFormValues): Record<string, unknown> {
  const num = (v: string) => (v.trim() === "" ? null : Number(v));
  return {
    contract_number: values.contract_number,
    contract_type: values.contract_type,
    counterparty: values.counterparty,
    start_date: values.start_date || null,
    finish_date: values.finish_date || null,
    original_amount: num(values.original_amount),
    adjusted_amount: num(values.adjusted_amount),
    advance_payment_pct: num(values.advance_payment_pct) ?? 0,
    retention_pct: num(values.retention_pct) ?? 0,
    insurance_pct: num(values.insurance_pct) ?? 0,
    tax_pct: num(values.tax_pct) ?? 0,
    performance_guarantee_amount: num(values.performance_guarantee_amount),
    performance_guarantee_expiry: values.performance_guarantee_expiry || null,
    advance_guarantee_amount: num(values.advance_guarantee_amount),
    advance_guarantee_expiry: values.advance_guarantee_expiry || null,
    status: values.status,
    file_url: values.file_url,
    notes: values.notes,
  };
}
