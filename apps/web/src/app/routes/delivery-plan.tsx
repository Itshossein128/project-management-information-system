import { useMemo, useState } from "react";
import { CalendarDays, CheckCircle2, Circle, ListChecks, Search } from "lucide-react";
import { Input } from "@/components/ui/input";
import { deliveryPlan } from "@/app/data/delivery-plan";

export function meta() {
  return [{ title: "برنامه تحویل ولورا" }, { name: "robots", content: "noindex, nofollow" }];
}

const formatDate = (value: string) => new Intl.DateTimeFormat("fa-IR", {
  year: "numeric", month: "long", day: "numeric", timeZone: "UTC",
}).format(new Date(`${value}T12:00:00Z`));
const number = (value: number) => value.toLocaleString("fa-IR");
type Filter = "all" | "implemented" | "remaining";

export default function DeliveryPlanPage() {
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState<Filter>("all");
  const phases = useMemo(() => {
    const term = query.trim().replace(/ي/g, "ی").replace(/ك/g, "ک").toLocaleLowerCase("fa");
    return deliveryPlan.phases.map((phase) => ({
      ...phase,
      tasks: phase.tasks.filter((task) => (filter === "all" || task.status === filter) &&
        (!term || `${phase.id} ${phase.title} ${task.title}`.replace(/ي/g, "ی").replace(/ك/g, "ک").toLocaleLowerCase("fa").includes(term))),
    })).filter((phase) => phase.tasks.length);
  }, [query, filter]);
  const tasks = deliveryPlan.phases.flatMap((phase) => phase.tasks);
  const implemented = tasks.filter((task) => task.status === "implemented").length;

  return (
    <div id="delivery-plan-page" dir="rtl" className="mx-auto w-full max-w-6xl space-y-7 p-4 text-start sm:p-6 lg:p-8 print:p-0">
      <header className="space-y-3 border-b border-border pb-6">
        <div className="flex flex-wrap items-center gap-2 text-sm text-muted-foreground">
          <ListChecks className="size-4" aria-hidden="true" />
          <span>مراحل تحویل سامانه</span>
          <span className="rounded-full bg-primary/10 px-3 py-1 font-medium text-primary">سناریوی کمینه</span>
        </div>
        <h1 className="text-2xl font-semibold tracking-tight sm:text-3xl">برنامه تحویل ولورا</h1>
        <p className="max-w-3xl text-sm leading-7 text-muted-foreground">مراحل تحویل، قابلیت‌های پیاده‌سازی‌شده و کارهای باقی‌مانده تا تحویل نهایی سامانه.</p>
        <div className="flex flex-wrap gap-x-6 gap-y-2 text-sm">
          <span>شروع برنامه مبنا: <time dateTime={deliveryPlan.baselineStart}>{formatDate(deliveryPlan.baselineStart)}</time></span>
          <span className="font-medium">تحویل نهایی در سناریوی کمینه: <time dateTime={deliveryPlan.finish}>{formatDate(deliveryPlan.finish)}</time></span>
        </div>
        <p className="text-xs leading-6 text-muted-foreground">آخرین ثبت وضعیت: {formatDate(deliveryPlan.updatedAt)}. تاریخ‌ها مربوط به برنامه مبنا هستند و تکمیل هر مرحله به تأیید خروجی‌های آن وابسته است.</p>
      </header>

      <section aria-label="خلاصه مراحل تحویل" className="grid grid-cols-3 divide-x divide-x-reverse divide-border rounded-xl border border-border bg-card py-4">
        {[[deliveryPlan.phases.length, "مرحله تحویل"], [implemented, "قابلیت پیاده‌سازی‌شده"], [tasks.length - implemented, "کار نیازمند تکمیل"]].map(([count, label]) => (
          <div key={label} className="px-2 text-center sm:px-5"><div className="text-2xl font-semibold tabular-nums">{number(count as number)}</div><div className="mt-1 text-xs leading-6 text-muted-foreground sm:text-sm">{label}</div></div>
        ))}
      </section>

      <section aria-label="جست‌وجو و نمایش کارها" className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between print:hidden">
        <div className="relative w-full sm:max-w-sm">
          <label htmlFor="delivery-task-search" className="sr-only">جست‌وجوی مرحله یا ریزکار</label>
          <Search className="pointer-events-none absolute right-3 top-3 size-4 text-muted-foreground" aria-hidden="true" />
          <Input id="delivery-task-search" className="h-10 pr-9" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="جست‌وجوی مرحله یا ریزکار…" />
        </div>
        <div className="flex flex-wrap gap-2" role="group" aria-label="وضعیت کارها">
          {([['all', 'همه کارها'], ['implemented', 'پیاده‌سازی‌شده'], ['remaining', 'نیازمند تکمیل']] as const).map(([value, label]) => (
            <button key={value} type="button" aria-pressed={filter === value} onClick={() => setFilter(value)} className={`min-h-10 rounded-lg border px-3 text-sm transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring ${filter === value ? 'border-primary bg-primary text-primary-foreground' : 'border-border bg-background hover:bg-muted'}`}>{label}</button>
          ))}
        </div>
      </section>
      <p className="text-xs leading-6 text-muted-foreground">«پیاده‌سازی‌شده» نشان‌دهنده قابلیت موجود است؛ تأیید نهایی هر مرحله به بررسی خروجی‌ها و تکمیل موارد باز آن وابسته است.</p>

      <div className="space-y-5" aria-live="polite">
        {phases.map((phase) => (
          <section key={phase.id} id={`delivery-${phase.id.replaceAll('.', '-')}`} aria-labelledby={`phase-title-${phase.id}`} className="overflow-hidden rounded-xl border border-border bg-card print:break-inside-avoid">
            <header className="space-y-3 border-b border-border bg-muted/30 p-4 sm:p-5">
              <div className="flex items-start gap-3"><span className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-sm font-semibold text-primary">{number(deliveryPlan.phases.findIndex((item) => item.id === phase.id) + 1)}</span><div><span className="text-xs text-muted-foreground" dir="ltr">{phase.id}</span><h2 id={`phase-title-${phase.id}`} className="text-base font-semibold sm:text-lg">{phase.title}</h2></div></div>
              <div className="flex flex-wrap gap-x-6 gap-y-2 text-xs leading-6 text-muted-foreground sm:text-sm"><span className="inline-flex items-center gap-1.5"><CalendarDays className="size-4 shrink-0" aria-hidden="true" />{formatDate(phase.start)} تا {formatDate(phase.finish)}</span><span>موعد بررسی و تأیید: {formatDate(phase.acceptance)}</span></div>
              {phase.note && <p className="text-xs leading-6 text-muted-foreground">{phase.note}</p>}
            </header>
            <ul className="divide-y divide-border">
              {phase.tasks.map((task) => (
                <li key={task.id} data-delivery-status={task.status} className="flex items-start gap-3 px-4 py-4 sm:px-5">
                  {task.status === "implemented" ? <CheckCircle2 className="mt-0.5 size-5 shrink-0 text-primary" aria-hidden="true" /> : <Circle className="mt-0.5 size-5 shrink-0 text-muted-foreground" aria-hidden="true" />}
                  <div className="min-w-0 flex-1 space-y-1.5"><h3 className="text-sm font-medium leading-7">{task.title}</h3><div className="flex flex-wrap gap-x-4 gap-y-1 text-xs leading-6 text-muted-foreground"><span className={task.status === "implemented" ? "font-medium text-primary" : ""}>{task.status === "implemented" ? "پیاده‌سازی‌شده" : "نیازمند تکمیل"}</span>{task.start && task.finish && <span>{formatDate(task.start)} تا {formatDate(task.finish)}</span>}</div>{task.note && <p className="text-xs leading-6 text-muted-foreground">{task.note}</p>}</div>
                </li>
              ))}
            </ul>
          </section>
        ))}
        {!phases.length && <p role="status" className="rounded-xl border border-dashed border-border p-8 text-center text-sm text-muted-foreground">کاری با این جست‌وجو و وضعیت پیدا نشد.</p>}
      </div>
    </div>
  );
}
