import { useCreateDepartmentActivityRecord } from "@/app/hooks/queries";
import type {
  DepartmentActivityRecordPayload,
  DepartmentSlug,
} from "@/app/lib/api-types";
import {
  Button,
  Field,
  Input,
  JalaliDatePicker,
  TextArea,
} from "@/components/form";
import { Modal } from "@/components/overlay/modal";
import { useMemo, useState } from "react";
import { useTranslation } from "react-i18next";

export interface DepartmentActivityRecordModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  businessId: number | string;
  department: DepartmentSlug;
}

const EMPTY_PAYLOAD: Omit<DepartmentActivityRecordPayload, "department"> = {
  date: "",
  location: "",
  activity_description: "",
  contractor: "",
  unit: "",
  description: "",
};

export function DepartmentActivityRecordModal({
  open,
  onOpenChange,
  businessId,
  department,
}: DepartmentActivityRecordModalProps) {
  const { t } = useTranslation();
  const createMutation = useCreateDepartmentActivityRecord(businessId);

  const [form, setForm] = useState(EMPTY_PAYLOAD);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const closeAndReset = () => {
    onOpenChange(false);
    setSubmitError(null);
    setForm(EMPTY_PAYLOAD);
  };

  const payload = useMemo<DepartmentActivityRecordPayload>(
    () => ({
      department,
      ...form,
    }),
    [department, form],
  );

  const canSubmit =
    payload.date.trim() !== "" &&
    payload.location.trim() !== "" &&
    payload.activity_description.trim() !== "" &&
    payload.contractor.trim() !== "" &&
    payload.unit.trim() !== "";

  return (
    <Modal
      open={open}
      onOpenChange={(next) => (next ? onOpenChange(true) : closeAndReset())}
      title={t("businessDepartment.activityLog.addTitle")}
      idBase="departmentActivityRecord"
      className="max-w-2xl"
    >
      <form
        id="form-departmentActivityRecordCreate"
        className="space-y-4"
        onSubmit={(e) => {
          e.preventDefault();
          setSubmitError(null);
          if (!canSubmit) {
            setSubmitError(t("businessDepartment.activityLog.validationRequired"));
            return;
          }
          void createMutation
            .mutateAsync(payload)
            .then(() => closeAndReset())
            .catch((err) => {
              setSubmitError(
                err instanceof Error
                  ? err.message
                  : t("businessDepartment.activityLog.createFailed"),
              );
            });
        }}
      >
        {submitError ? (
          <p
            id="text-departmentActivityRecordCreateError"
            className="text-destructive text-sm"
          >
            {submitError}
          </p>
        ) : null}

        <div
          id="container-departmentActivityRecordCreateFields"
          className="grid grid-cols-1 gap-4 sm:grid-cols-2"
        >
          <div id="container-departmentActivityDate" className="sm:col-span-1">
            <JalaliDatePicker
              name="departmentActivityDate"
              id="input-departmentActivityDate"
              label={t("businessDepartment.activityLog.fields.date")}
              value={form.date}
              onChange={(next) => setForm((p) => ({ ...p, date: next }))}
              required
            />
          </div>

          <div
            id="container-departmentActivityUnit"
            className="sm:col-span-1"
          >
            <Field
              name="departmentActivityUnit"
              label={t("businessDepartment.activityLog.fields.unit")}
              htmlFor="input-departmentActivityUnit"
            >
              {() => (
                <Input
                  id="input-departmentActivityUnit"
                  name="departmentActivityUnit"
                  value={form.unit}
                  onChange={(e) =>
                    setForm((p) => ({ ...p, unit: e.target.value }))
                  }
                  required
                />
              )}
            </Field>
          </div>

          <div
            id="container-departmentActivityLocation"
            className="sm:col-span-1"
          >
            <Field
              name="departmentActivityLocation"
              label={t("businessDepartment.activityLog.fields.location")}
              htmlFor="input-departmentActivityLocation"
            >
              {() => (
                <Input
                  id="input-departmentActivityLocation"
                  name="departmentActivityLocation"
                  value={form.location}
                  onChange={(e) =>
                    setForm((p) => ({ ...p, location: e.target.value }))
                  }
                  required
                />
              )}
            </Field>
          </div>

          <div
            id="container-departmentActivityContractor"
            className="sm:col-span-1"
          >
            <Field
              name="departmentActivityContractor"
              label={t("businessDepartment.activityLog.fields.contractor")}
              htmlFor="input-departmentActivityContractor"
            >
              {() => (
                <Input
                  id="input-departmentActivityContractor"
                  name="departmentActivityContractor"
                  value={form.contractor}
                  onChange={(e) =>
                    setForm((p) => ({ ...p, contractor: e.target.value }))
                  }
                  required
                />
              )}
            </Field>
          </div>

          <div
            id="container-departmentActivityActivityDescription"
            className="sm:col-span-2"
          >
            <Field
              name="departmentActivityActivityDescription"
              label={t(
                "businessDepartment.activityLog.fields.activityDescription",
              )}
              htmlFor="input-departmentActivityActivityDescription"
            >
              {() => (
                <Input
                  id="input-departmentActivityActivityDescription"
                  name="departmentActivityActivityDescription"
                  value={form.activity_description}
                  onChange={(e) =>
                    setForm((p) => ({
                      ...p,
                      activity_description: e.target.value,
                    }))
                  }
                  required
                />
              )}
            </Field>
          </div>

          <div
            id="container-departmentActivityDescription"
            className="sm:col-span-2"
          >
            <TextArea
              id="input-departmentActivityDescription"
              name="departmentActivityDescription"
              label={t("businessDepartment.activityLog.fields.description")}
              value={form.description}
              onChange={(e) =>
                setForm((p) => ({ ...p, description: e.target.value }))
              }
              rows={4}
            />
          </div>
        </div>

        <div
          id="container-departmentActivityRecordCreateActions"
          className="flex flex-wrap items-center justify-end gap-2 border-t pt-4"
        >
          <Button
            id="button-cancelDepartmentActivityRecordCreate"
            type="button"
            variant="outline"
            onClick={() => closeAndReset()}
          >
            {t("common.cancel")}
          </Button>
          <Button
            id="button-submitDepartmentActivityRecordCreate"
            type="submit"
            disabled={createMutation.isPending}
          >
            {createMutation.isPending
              ? t("businessDepartment.activityLog.creating")
              : t("businessDepartment.activityLog.create")}
          </Button>
        </div>
      </form>
    </Modal>
  );
}

