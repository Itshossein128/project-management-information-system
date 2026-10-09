import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import {
  createCalendarException,
  createWorkingCalendar,
  deleteCalendarException,
  deleteWorkingCalendar,
  fetchCalendarExceptions,
  fetchWorkingCalendars,
  updateWorkingCalendar,
  type WorkingCalendar,
} from "@/app/lib/api/schedule";
import { usePermission } from "@/app/contexts/project-context";
import { JalaliDatePicker } from "@/components/form/JalaliDatePicker";
import { Checkbox, Input } from "@/components/form";
import { Button } from "@/components/ui/sprint-button";
import { useToast } from "@/components/ui/toast";

const WEEKDAYS = [
  "work_monday",
  "work_tuesday",
  "work_wednesday",
  "work_thursday",
  "work_friday",
  "work_saturday",
  "work_sunday",
] as const;

type WeekdayKey = (typeof WEEKDAYS)[number];

const DEFAULT_WEEKDAYS: Record<WeekdayKey, boolean> = {
  work_monday: true,
  work_tuesday: true,
  work_wednesday: true,
  work_thursday: true,
  work_friday: true,
  work_saturday: false,
  work_sunday: false,
};

export function WorkingCalendarPanel({ projectId }: { projectId: string }) {
  const { t } = useTranslation();
  const toast = useToast();
  const qc = useQueryClient();
  const { has } = usePermission(projectId);
  const canEdit = has("edit_activities");

  const [name, setName] = useState("");
  const [isDefault, setIsDefault] = useState(false);
  const [weekdays, setWeekdays] = useState(DEFAULT_WEEKDAYS);
  const [selectedId, setSelectedId] = useState<string>("");
  const [exceptionDate, setExceptionDate] = useState("");
  const [exceptionWorking, setExceptionWorking] = useState(false);
  const [exceptionName, setExceptionName] = useState("");

  const { data: calendars = [] } = useQuery({
    queryKey: ["working-calendars", projectId],
    queryFn: () => fetchWorkingCalendars(projectId),
  });

  const { data: exceptions = [] } = useQuery({
    queryKey: ["calendar-exceptions", projectId, selectedId],
    queryFn: () => fetchCalendarExceptions(projectId, selectedId),
    enabled: Boolean(selectedId),
  });

  const invalidate = () => {
    void qc.invalidateQueries({ queryKey: ["working-calendars", projectId] });
    void qc.invalidateQueries({ queryKey: ["calendar-exceptions", projectId] });
  };

  const createMut = useMutation({
    mutationFn: () =>
      createWorkingCalendar(projectId, {
        name: name.trim(),
        is_default: isDefault,
        ...weekdays,
      }),
    onSuccess: () => {
      toast.success(t("common.success"));
      setName("");
      setIsDefault(false);
      setWeekdays(DEFAULT_WEEKDAYS);
      invalidate();
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const setDefaultMut = useMutation({
    mutationFn: (cal: WorkingCalendar) =>
      updateWorkingCalendar(projectId, cal.id, { is_default: true }),
    onSuccess: () => {
      toast.success(t("common.success"));
      invalidate();
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const deleteMut = useMutation({
    mutationFn: (id: string) => deleteWorkingCalendar(projectId, id),
    onSuccess: () => {
      toast.success(t("common.success"));
      if (selectedId) setSelectedId("");
      invalidate();
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const addExcMut = useMutation({
    mutationFn: () =>
      createCalendarException(projectId, selectedId, {
        exception_date: exceptionDate,
        is_working: exceptionWorking,
        name: exceptionName.trim() || undefined,
      }),
    onSuccess: () => {
      toast.success(t("common.success"));
      setExceptionDate("");
      setExceptionName("");
      setExceptionWorking(false);
      invalidate();
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const delExcMut = useMutation({
    mutationFn: (exceptionId: string) =>
      deleteCalendarException(projectId, selectedId, exceptionId),
    onSuccess: () => {
      toast.success(t("common.success"));
      invalidate();
    },
    onError: (e: Error) => toast.error(e.message),
  });

  return (
    <section
      className="space-y-4 rounded-lg border p-4"
      data-testid="working-calendar-panel"
    >
      <h2 className="text-base font-medium">{t("schedule.calendarManagement")}</h2>

      <ul className="divide-y rounded-md border text-sm">
        {calendars.length === 0 ? (
          <li className="px-3 py-2 text-muted-foreground">{t("schedule.calendarEmpty")}</li>
        ) : (
          calendars.map((cal) => (
            <li key={cal.id} className="flex flex-wrap items-center gap-2 px-3 py-2">
              <button
                type="button"
                className={`text-start font-medium underline-offset-2 hover:underline ${
                  selectedId === cal.id ? "text-primary" : ""
                }`}
                onClick={() => setSelectedId(cal.id === selectedId ? "" : cal.id)}
              >
                {cal.name}
                {cal.is_default ? ` (${t("schedule.calendarDefault")})` : ""}
              </button>
              {canEdit && !cal.is_default ? (
                <Button
                  size="sm"
                  variant="secondary"
                  onClick={() => setDefaultMut.mutate(cal)}
                >
                  {t("schedule.setDefault")}
                </Button>
              ) : null}
              {canEdit ? (
                <Button
                  size="sm"
                  variant="secondary"
                  onClick={() => deleteMut.mutate(cal.id)}
                >
                  {t("common.delete")}
                </Button>
              ) : null}
            </li>
          ))
        )}
      </ul>

      {canEdit ? (
        <div className="space-y-3 rounded-md border border-dashed p-3">
          <h3 className="text-sm font-medium">{t("schedule.calendarCreate")}</h3>
          <Input
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder={t("schedule.calendarName")}
          />
          <div className="flex flex-wrap gap-3">
            {WEEKDAYS.map((key) => (
              <Checkbox
                key={key}
                name={key}
                label={t(`schedule.weekdays.${key}`)}
                checked={weekdays[key]}
                onChange={(e) =>
                  setWeekdays((prev) => ({
                    ...prev,
                    [key]: Boolean((e.target as unknown as { value: boolean }).value),
                  }))
                }
              />
            ))}
          </div>
          <Checkbox
            name="is_default_cal"
            label={t("schedule.calendarDefault")}
            checked={isDefault}
            onChange={(e) =>
              setIsDefault(Boolean((e.target as unknown as { value: boolean }).value))
            }
          />
          <Button
            size="sm"
            disabled={!name.trim() || createMut.isPending}
            onClick={() => createMut.mutate()}
          >
            {t("schedule.calendarCreate")}
          </Button>
        </div>
      ) : null}

      {selectedId ? (
        <div className="space-y-3 rounded-md border p-3">
          <h3 className="text-sm font-medium">{t("schedule.calendarExceptions")}</h3>
          <ul className="divide-y text-sm">
            {exceptions.length === 0 ? (
              <li className="py-1 text-muted-foreground">{t("common.empty")}</li>
            ) : (
              exceptions.map((exc) => (
                <li key={exc.id} className="flex items-center justify-between gap-2 py-1">
                  <span>
                    {exc.exception_date}
                    {exc.name ? ` — ${exc.name}` : ""}
                    {exc.is_working
                      ? ` (${t("schedule.exceptionWorking")})`
                      : ` (${t("schedule.exceptionHoliday")})`}
                  </span>
                  {canEdit ? (
                    <Button
                      size="sm"
                      variant="secondary"
                      onClick={() => delExcMut.mutate(exc.id)}
                    >
                      {t("common.delete")}
                    </Button>
                  ) : null}
                </li>
              ))
            )}
          </ul>
          {canEdit ? (
            <div className="grid gap-2 sm:grid-cols-2">
              <JalaliDatePicker
                name="exception_date"
                value={exceptionDate}
                onChange={setExceptionDate}
              />
              <Input
                value={exceptionName}
                onChange={(e) => setExceptionName(e.target.value)}
                placeholder={t("schedule.exceptionName")}
              />
              <Checkbox
                name="exc_working"
                label={t("schedule.exceptionWorking")}
                checked={exceptionWorking}
                onChange={(e) =>
                  setExceptionWorking(
                    Boolean((e.target as unknown as { value: boolean }).value),
                  )
                }
              />
              <Button
                size="sm"
                disabled={!exceptionDate || addExcMut.isPending}
                onClick={() => addExcMut.mutate()}
              >
                {t("schedule.addException")}
              </Button>
            </div>
          ) : null}
        </div>
      ) : null}
    </section>
  );
}
