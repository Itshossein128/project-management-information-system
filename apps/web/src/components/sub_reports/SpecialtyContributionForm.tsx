import { useState } from "react";
import { Button } from "@/components/ui/sprint-button";
import { JalaliDatePicker } from "@/components/form/JalaliDatePicker";

export type SpecialtyContributionPayload = {
  report_date: string;
  weather_condition: string;
  site_status: string;
  form_code: string;
  activities: Record<string, unknown>[];
  labor_entries: Record<string, unknown>[];
  material_entries: Record<string, unknown>[];
  concrete_entries: Record<string, unknown>[];
  general_activities: Record<string, unknown>[];
  notes: Record<string, unknown>[];
};

const emptyPayload = (): SpecialtyContributionPayload => ({
  report_date: "",
  weather_condition: "sunny",
  site_status: "active",
  form_code: "",
  activities: [
    {
      row_number: 1,
      shift: "shift_1",
      crew_name: "",
      activity_description: "",
      worker_count: 1,
    },
  ],
  labor_entries: [],
  material_entries: [],
  concrete_entries: [],
  general_activities: [],
  notes: [],
});

type Props = {
  onSubmit: (payload: SpecialtyContributionPayload) => void;
  loading?: boolean;
};

function FieldRow({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <label className='block space-y-1 text-sm'>
      <span className='text-muted-foreground'>{label}</span>
      {children}
    </label>
  );
}

const inputClass = "w-full rounded border border-border bg-background px-2 py-1 text-sm";

export function SpecialtyContributionForm({ onSubmit, loading }: Props) {
  const [form, setForm] = useState(emptyPayload);

  const labor = form.labor_entries[0] as
    | { labor_category?: string; job_title?: string; present_count?: number; leave_count?: number }
    | undefined;
  const material = form.material_entries[0] as
    | { material_description?: string; quantity?: number; unit?: string }
    | undefined;
  const concrete = form.concrete_entries[0] as
    | { concrete_description?: string; volume_m3?: number }
    | undefined;
  const general = form.general_activities[0] as
    | { activity_description?: string; location?: string }
    | undefined;
  const issue = form.notes.find((n) => n.note_type === "issue") as
    | { text?: string }
    | undefined;
  const visit = form.notes.find((n) => n.note_type === "visit") as
    | { text?: string }
    | undefined;
  const activity = form.activities[0] as {
    activity_description?: string;
    crew_name?: string;
    worker_count?: number;
  };

  return (
    <div className='space-y-4 p-4' data-testid='specialty-contribution-form'>
      <JalaliDatePicker
        name='report_date'
        label='تاریخ'
        value={form.report_date}
        onChange={(v) => setForm((f) => ({ ...f, report_date: v }))}
      />
      <FieldRow label='کد فرم'>
        <input
          className={inputClass}
          value={form.form_code}
          onChange={(e) => setForm((f) => ({ ...f, form_code: e.target.value }))}
        />
      </FieldRow>
      <div className='grid gap-3 sm:grid-cols-2'>
        <FieldRow label='وضعیت جوی'>
          <select
            className={inputClass}
            value={form.weather_condition}
            onChange={(e) =>
              setForm((f) => ({ ...f, weather_condition: e.target.value }))
            }
          >
            <option value='sunny'>آفتابی</option>
            <option value='partly_cloudy'>نیمه‌ابری</option>
            <option value='cloudy'>ابری</option>
            <option value='rainy'>بارانی</option>
            <option value='stormy'>طوفانی</option>
            <option value='snowy'>برفی</option>
            <option value='foggy'>مه</option>
          </select>
        </FieldRow>
        <FieldRow label='وضعیت کارگاه'>
          <select
            className={inputClass}
            value={form.site_status}
            onChange={(e) => setForm((f) => ({ ...f, site_status: e.target.value }))}
          >
            <option value='active'>فعال</option>
            <option value='inactive'>غیرفعال</option>
          </select>
        </FieldRow>
      </div>

      <fieldset className='space-y-2 rounded-lg border border-border p-3'>
        <legend className='px-1 text-sm font-medium'>فعالیت اجرایی</legend>
        <FieldRow label='شرح'>
          <input
            className={inputClass}
            value={activity.activity_description ?? ""}
            onChange={(e) =>
              setForm((f) => ({
                ...f,
                activities: [
                  {
                    ...f.activities[0],
                    activity_description: e.target.value,
                    row_number: 1,
                    shift: "shift_1",
                  },
                ],
              }))
            }
          />
        </FieldRow>
        <div className='grid gap-2 sm:grid-cols-2'>
          <FieldRow label='گروه'>
            <input
              className={inputClass}
              value={activity.crew_name ?? ""}
              onChange={(e) =>
                setForm((f) => ({
                  ...f,
                  activities: [{ ...f.activities[0], crew_name: e.target.value }],
                }))
              }
            />
          </FieldRow>
          <FieldRow label='نفرات'>
            <input
              type='number'
              min={0}
              className={inputClass}
              value={activity.worker_count ?? 1}
              onChange={(e) =>
                setForm((f) => ({
                  ...f,
                  activities: [
                    { ...f.activities[0], worker_count: Number(e.target.value) || 0 },
                  ],
                }))
              }
            />
          </FieldRow>
        </div>
      </fieldset>

      <fieldset className='space-y-2 rounded-lg border border-border p-3'>
        <legend className='px-1 text-sm font-medium'>نیروی انسانی</legend>
        <div className='grid gap-2 sm:grid-cols-2'>
          <FieldRow label='دسته'>
            <select
              className={inputClass}
              value={labor?.labor_category ?? "direct"}
              onChange={(e) =>
                setForm((f) => ({
                  ...f,
                  labor_entries: [
                    {
                      labor_category: e.target.value,
                      job_title: labor?.job_title ?? "",
                      present_count: labor?.present_count ?? 0,
                      leave_count: labor?.leave_count ?? 0,
                    },
                  ],
                }))
              }
            >
              <option value='direct'>مستقیم</option>
              <option value='indirect'>غیرمستقیم (ستادی)</option>
            </select>
          </FieldRow>
          <FieldRow label='عنوان شغلی'>
            <input
              className={inputClass}
              value={labor?.job_title ?? ""}
              onChange={(e) =>
                setForm((f) => ({
                  ...f,
                  labor_entries: [
                    {
                      labor_category: labor?.labor_category ?? "direct",
                      job_title: e.target.value,
                      present_count: labor?.present_count ?? 0,
                      leave_count: labor?.leave_count ?? 0,
                    },
                  ],
                }))
              }
            />
          </FieldRow>
          <FieldRow label='حاضر'>
            <input
              type='number'
              min={0}
              className={inputClass}
              value={labor?.present_count ?? 0}
              onChange={(e) =>
                setForm((f) => ({
                  ...f,
                  labor_entries: [
                    {
                      labor_category: labor?.labor_category ?? "direct",
                      job_title: labor?.job_title ?? "",
                      present_count: Number(e.target.value) || 0,
                      leave_count: labor?.leave_count ?? 0,
                    },
                  ],
                }))
              }
            />
          </FieldRow>
          <FieldRow label='مرخصی'>
            <input
              type='number'
              min={0}
              className={inputClass}
              value={labor?.leave_count ?? 0}
              onChange={(e) =>
                setForm((f) => ({
                  ...f,
                  labor_entries: [
                    {
                      labor_category: labor?.labor_category ?? "direct",
                      job_title: labor?.job_title ?? "",
                      present_count: labor?.present_count ?? 0,
                      leave_count: Number(e.target.value) || 0,
                    },
                  ],
                }))
              }
            />
          </FieldRow>
        </div>
      </fieldset>

      <fieldset className='space-y-2 rounded-lg border border-border p-3'>
        <legend className='px-1 text-sm font-medium'>مصالح وارده</legend>
        <FieldRow label='شرح'>
          <input
            className={inputClass}
            value={material?.material_description ?? ""}
            onChange={(e) =>
              setForm((f) => ({
                ...f,
                material_entries: e.target.value
                  ? [
                      {
                        material_description: e.target.value,
                        quantity: material?.quantity ?? 1,
                        unit: material?.unit ?? "عدد",
                      },
                    ]
                  : [],
              }))
            }
          />
        </FieldRow>
        <div className='grid gap-2 sm:grid-cols-2'>
          <FieldRow label='مقدار'>
            <input
              type='number'
              className={inputClass}
              value={material?.quantity ?? ""}
              onChange={(e) =>
                setForm((f) => ({
                  ...f,
                  material_entries: [
                    {
                      material_description: material?.material_description ?? "",
                      quantity: Number(e.target.value) || 0,
                      unit: material?.unit ?? "عدد",
                    },
                  ],
                }))
              }
            />
          </FieldRow>
          <FieldRow label='واحد'>
            <input
              className={inputClass}
              value={material?.unit ?? ""}
              onChange={(e) =>
                setForm((f) => ({
                  ...f,
                  material_entries: [
                    {
                      material_description: material?.material_description ?? "",
                      quantity: material?.quantity ?? 0,
                      unit: e.target.value,
                    },
                  ],
                }))
              }
            />
          </FieldRow>
        </div>
      </fieldset>

      <fieldset className='space-y-2 rounded-lg border border-border p-3'>
        <legend className='px-1 text-sm font-medium'>بتن‌ریزی</legend>
        <FieldRow label='شرح'>
          <input
            className={inputClass}
            value={concrete?.concrete_description ?? ""}
            onChange={(e) =>
              setForm((f) => ({
                ...f,
                concrete_entries: e.target.value
                  ? [
                      {
                        concrete_description: e.target.value,
                        volume_m3: concrete?.volume_m3 ?? 1,
                      },
                    ]
                  : [],
              }))
            }
          />
        </FieldRow>
        <FieldRow label='حجم (م۳)'>
          <input
            type='number'
            className={inputClass}
            value={concrete?.volume_m3 ?? ""}
            onChange={(e) =>
              setForm((f) => ({
                ...f,
                concrete_entries: [
                  {
                    concrete_description: concrete?.concrete_description ?? "",
                    volume_m3: Number(e.target.value) || 0,
                  },
                ],
              }))
            }
          />
        </FieldRow>
      </fieldset>

      <fieldset className='space-y-2 rounded-lg border border-border p-3'>
        <legend className='px-1 text-sm font-medium'>فعالیت عمومی کارگاه</legend>
        <FieldRow label='شرح'>
          <input
            className={inputClass}
            value={general?.activity_description ?? ""}
            onChange={(e) =>
              setForm((f) => ({
                ...f,
                general_activities: e.target.value
                  ? [
                      {
                        activity_description: e.target.value,
                        location: general?.location ?? "",
                      },
                    ]
                  : [],
              }))
            }
          />
        </FieldRow>
        <FieldRow label='محل'>
          <input
            className={inputClass}
            value={general?.location ?? ""}
            onChange={(e) =>
              setForm((f) => ({
                ...f,
                general_activities: [
                  {
                    activity_description: general?.activity_description ?? "",
                    location: e.target.value,
                  },
                ],
              }))
            }
          />
        </FieldRow>
      </fieldset>

      <fieldset className='space-y-2 rounded-lg border border-border p-3'>
        <legend className='px-1 text-sm font-medium'>ملاحظات و بازدیدها</legend>
        <FieldRow label='ملاحظات / مسائل'>
          <textarea
            className={`${inputClass} min-h-16`}
            value={issue?.text ?? ""}
            onChange={(e) => {
              const text = e.target.value;
              setForm((f) => {
                const others = f.notes.filter((n) => n.note_type !== "issue");
                return {
                  ...f,
                  notes: text
                    ? [...others, { note_type: "issue", text, row_number: 1 }]
                    : others,
                };
              });
            }}
          />
        </FieldRow>
        <FieldRow label='بازدید'>
          <textarea
            className={`${inputClass} min-h-16`}
            value={visit?.text ?? ""}
            onChange={(e) => {
              const text = e.target.value;
              setForm((f) => {
                const others = f.notes.filter((n) => n.note_type !== "visit");
                return {
                  ...f,
                  notes: text
                    ? [...others, { note_type: "visit", text, row_number: 2 }]
                    : others,
                };
              });
            }}
          />
        </FieldRow>
      </fieldset>

      <Button
        data-testid='specialty-contribution-save'
        onClick={() => {
          const payload = { ...form };
          if (!(labor?.job_title || "").trim()) payload.labor_entries = [];
          if (!(material?.material_description || "").trim()) payload.material_entries = [];
          if (!(concrete?.concrete_description || "").trim()) payload.concrete_entries = [];
          if (!(general?.activity_description || "").trim()) payload.general_activities = [];
          onSubmit(payload);
        }}
        loading={loading}
      >
        ذخیره
      </Button>
    </div>
  );
}
