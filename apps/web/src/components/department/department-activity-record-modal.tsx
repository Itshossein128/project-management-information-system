import { useStickyFormFields } from "@/app/hooks/use-sticky-form-fields";
import { useCreateDepartmentActivityRecord } from "@/app/hooks/queries";
import type {
  DepartmentActivityRecordPayload,
  DepartmentSlug,
} from "@/app/lib/api-types";
import { departmentUsesUnit, isWarehouseDepartment } from "@/app/lib/api-types";
import { CONSTRUCTION_UNIT_OPTIONS } from "@/app/lib/construction-units";
import {
  Button,
  CreatableSelect,
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

const EMPTY_FORM: {
  date: string;
  location: string;
  activity_description: string;
  contractor: string;
  unit: string;
  description: string;
  material_type: string;
  quantity_in: string;
  quantity_out: string;
  consumption_location: string;
  supplier: string;
} = {
  date: "",
  location: "",
  activity_description: "",
  contractor: "",
  unit: "",
  description: "",
  material_type: "",
  quantity_in: "",
  quantity_out: "",
  consumption_location: "",
  supplier: "",
};

type FormField = keyof typeof EMPTY_FORM;

function parseNonNegativeQuantity(raw: string | number): number | null {
  const text = String(raw ?? "").trim();
  if (text === "") return 0;
  const value = Number(text);
  if (!Number.isFinite(value) || value < 0) return null;
  return value;
}

export function DepartmentActivityRecordModal({
  open,
  onOpenChange,
  businessId,
  department,
}: DepartmentActivityRecordModalProps) {
  const { t } = useTranslation();
  const createMutation = useCreateDepartmentActivityRecord(businessId);
  const isWarehouse = isWarehouseDepartment(department);
  const showsUnit = departmentUsesUnit(department);

  const stickyScope = `department-activity:${businessId}:${department}`;

  const {
    values: form,
    setField,
    sticky,
    setSticky,
    resetUnlocked,
  } = useStickyFormFields({
    scope: stickyScope,
    initialValues: EMPTY_FORM,
    defaultSticky: true,
  });

  const [submitError, setSubmitError] = useState<string | null>(null);

  const closeAndReset = () => {
    resetUnlocked();
    onOpenChange(false);
    setSubmitError(null);
  };

  const stickyFieldProps = (field: FormField) => ({
    sticky: sticky[field],
    onStickyChange: (next: boolean) => setSticky(field, next),
    stickyAriaLabel: sticky[field]
      ? t("form.sticky.unlockField")
      : t("form.sticky.lockField"),
  });

  const payload = useMemo<DepartmentActivityRecordPayload>(() => {
    if (isWarehouse) {
      return {
        department,
        date: form.date,
        material_type: form.material_type,
        quantity_in: form.quantity_in === "" ? "0" : form.quantity_in,
        quantity_out: form.quantity_out === "" ? "0" : form.quantity_out,
        unit: form.unit,
        consumption_location: form.consumption_location,
        supplier: form.supplier,
        description: form.description,
        location: "",
        activity_description: "",
        contractor: "",
      };
    }
    return {
      department,
      date: form.date,
      location: form.location,
      activity_description: form.activity_description,
      contractor: form.contractor,
      unit: showsUnit ? form.unit : "",
      description: form.description,
      material_type: "",
      quantity_in: "0",
      quantity_out: "0",
      consumption_location: "",
      supplier: "",
    };
  }, [department, form, isWarehouse, showsUnit]);

  const quantityIn = parseNonNegativeQuantity(form.quantity_in);
  const quantityOut = parseNonNegativeQuantity(form.quantity_out);

  const canSubmit = isWarehouse
    ? payload.date.trim() !== "" &&
      payload.material_type.trim() !== "" &&
      payload.unit.trim() !== "" &&
      payload.consumption_location.trim() !== "" &&
      payload.supplier.trim() !== "" &&
      quantityIn !== null &&
      quantityOut !== null &&
      (quantityIn > 0 || quantityOut > 0)
    : payload.date.trim() !== "" &&
      payload.location.trim() !== "" &&
      payload.activity_description.trim() !== "" &&
      payload.contractor.trim() !== "" &&
      (!showsUnit || payload.unit.trim() !== "");

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
            if (
              isWarehouse &&
              (quantityIn === null ||
                quantityOut === null ||
                (quantityIn <= 0 && quantityOut <= 0))
            ) {
              setSubmitError(
                t("businessDepartment.activityLog.validationQuantityRequired"),
              );
            } else {
              setSubmitError(
                t("businessDepartment.activityLog.validationRequired"),
              );
            }
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
              onChange={(next) => setField("date", next)}
              required
              {...stickyFieldProps("date")}
            />
          </div>

          {isWarehouse ? (
            <>
              <div
                id="container-departmentActivityMaterialType"
                className="sm:col-span-1"
              >
                <Field
                  name="departmentActivityMaterialType"
                  label={t("businessDepartment.activityLog.fields.materialType")}
                  htmlFor="input-departmentActivityMaterialType"
                  {...stickyFieldProps("material_type")}
                >
                  {() => (
                    <Input
                      id="input-departmentActivityMaterialType"
                      name="departmentActivityMaterialType"
                      value={form.material_type}
                      onChange={(e) => setField("material_type", e.target.value)}
                      required
                    />
                  )}
                </Field>
              </div>

              <div
                id="container-departmentActivityQuantityIn"
                className="sm:col-span-1"
              >
                <Field
                  name="departmentActivityQuantityIn"
                  label={t("businessDepartment.activityLog.fields.quantityIn")}
                  htmlFor="input-departmentActivityQuantityIn"
                  {...stickyFieldProps("quantity_in")}
                >
                  {() => (
                    <Input
                      id="input-departmentActivityQuantityIn"
                      name="departmentActivityQuantityIn"
                      type="number"
                      min={0}
                      step="any"
                      value={String(form.quantity_in)}
                      onChange={(e) => setField("quantity_in", e.target.value)}
                    />
                  )}
                </Field>
              </div>

              <div
                id="container-departmentActivityUnit"
                className="sm:col-span-1"
              >
                <CreatableSelect
                  id="input-departmentActivityUnit"
                  name="departmentActivityUnit"
                  label={t("businessDepartment.activityLog.fields.unit")}
                  value={form.unit}
                  onChange={(next) => setField("unit", next)}
                  options={CONSTRUCTION_UNIT_OPTIONS}
                  placeholder={t(
                    "businessDepartment.activityLog.fields.unitPlaceholder",
                  )}
                  addPlaceholder={t(
                    "businessDepartment.activityLog.fields.unitCustomPlaceholder",
                  )}
                  addLabel={t("businessDepartment.activityLog.fields.unitAdd")}
                  required
                  {...stickyFieldProps("unit")}
                />
              </div>

              <div
                id="container-departmentActivityQuantityOut"
                className="sm:col-span-1"
              >
                <Field
                  name="departmentActivityQuantityOut"
                  label={t("businessDepartment.activityLog.fields.quantityOut")}
                  htmlFor="input-departmentActivityQuantityOut"
                  {...stickyFieldProps("quantity_out")}
                >
                  {() => (
                    <Input
                      id="input-departmentActivityQuantityOut"
                      name="departmentActivityQuantityOut"
                      type="number"
                      min={0}
                      step="any"
                      value={String(form.quantity_out)}
                      onChange={(e) => setField("quantity_out", e.target.value)}
                    />
                  )}
                </Field>
              </div>

              <div
                id="container-departmentActivityConsumptionLocation"
                className="sm:col-span-1"
              >
                <Field
                  name="departmentActivityConsumptionLocation"
                  label={t(
                    "businessDepartment.activityLog.fields.consumptionLocation",
                  )}
                  htmlFor="input-departmentActivityConsumptionLocation"
                  {...stickyFieldProps("consumption_location")}
                >
                  {() => (
                    <Input
                      id="input-departmentActivityConsumptionLocation"
                      name="departmentActivityConsumptionLocation"
                      value={form.consumption_location}
                      onChange={(e) =>
                        setField("consumption_location", e.target.value)
                      }
                      required
                    />
                  )}
                </Field>
              </div>

              <div
                id="container-departmentActivitySupplier"
                className="sm:col-span-1"
              >
                <Field
                  name="departmentActivitySupplier"
                  label={t("businessDepartment.activityLog.fields.supplier")}
                  htmlFor="input-departmentActivitySupplier"
                  {...stickyFieldProps("supplier")}
                >
                  {() => (
                    <Input
                      id="input-departmentActivitySupplier"
                      name="departmentActivitySupplier"
                      value={form.supplier}
                      onChange={(e) => setField("supplier", e.target.value)}
                      required
                    />
                  )}
                </Field>
              </div>
            </>
          ) : (
            <>
              {showsUnit ? (
                <div
                  id="container-departmentActivityUnit"
                  className="sm:col-span-1"
                >
                  <CreatableSelect
                    id="input-departmentActivityUnit"
                    name="departmentActivityUnit"
                    label={t("businessDepartment.activityLog.fields.unit")}
                    value={form.unit}
                    onChange={(next) => setField("unit", next)}
                    options={CONSTRUCTION_UNIT_OPTIONS}
                    placeholder={t(
                      "businessDepartment.activityLog.fields.unitPlaceholder",
                    )}
                    addPlaceholder={t(
                      "businessDepartment.activityLog.fields.unitCustomPlaceholder",
                    )}
                    addLabel={t("businessDepartment.activityLog.fields.unitAdd")}
                    required
                    {...stickyFieldProps("unit")}
                  />
                </div>
              ) : null}

              <div
                id="container-departmentActivityLocation"
                className="sm:col-span-1"
              >
                <Field
                  name="departmentActivityLocation"
                  label={t("businessDepartment.activityLog.fields.location")}
                  htmlFor="input-departmentActivityLocation"
                  {...stickyFieldProps("location")}
                >
                  {() => (
                    <Input
                      id="input-departmentActivityLocation"
                      name="departmentActivityLocation"
                      value={form.location}
                      onChange={(e) => setField("location", e.target.value)}
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
                  {...stickyFieldProps("contractor")}
                >
                  {() => (
                    <Input
                      id="input-departmentActivityContractor"
                      name="departmentActivityContractor"
                      value={form.contractor}
                      onChange={(e) => setField("contractor", e.target.value)}
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
                  {...stickyFieldProps("activity_description")}
                >
                  {() => (
                    <Input
                      id="input-departmentActivityActivityDescription"
                      name="departmentActivityActivityDescription"
                      value={form.activity_description}
                      onChange={(e) =>
                        setField("activity_description", e.target.value)
                      }
                      required
                    />
                  )}
                </Field>
              </div>
            </>
          )}

          <div
            id="container-departmentActivityDescription"
            className="sm:col-span-2"
          >
            <TextArea
              id="input-departmentActivityDescription"
              name="departmentActivityDescription"
              label={t("businessDepartment.activityLog.fields.description")}
              value={form.description}
              onChange={(e) => setField("description", e.target.value)}
              rows={4}
              {...stickyFieldProps("description")}
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
