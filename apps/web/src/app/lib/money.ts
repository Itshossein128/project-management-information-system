export type ProjectCurrency = "IRR" | "IRT";

export function currencyLabel(
  currency: ProjectCurrency | string,
  locale: "fa" | "en" = "fa",
): string {
  if (currency === "IRT") return locale === "fa" ? "تومان" : "Toman";
  return locale === "fa" ? "ریال" : "Rial";
}

export function formatMoney(
  amount: number | string,
  currency: ProjectCurrency | string = "IRR",
  locale: "fa" | "en" = "fa",
): string {
  const n = typeof amount === "string" ? Number(amount) : amount;
  const formatted = Number.isFinite(n)
    ? n.toLocaleString(locale === "fa" ? "fa-IR" : "en-US")
    : String(amount);
  return `${formatted} ${currencyLabel(currency, locale)}`;
}
