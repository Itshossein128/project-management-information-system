import { useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import { Modal } from "@/components/overlay/modal";
import { Button, Input, Label, PasswordInput } from "@/components/form";
import type { CreateHrUserPayload } from "@/app/hooks/queries";

export interface CreateHrUserModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (payload: CreateHrUserPayload) => void;
  submitting: boolean;
  submitError: string | null;
}

export function CreateHrUserModal({
  open,
  onOpenChange,
  onSubmit,
  submitting,
  submitError,
}: CreateHrUserModalProps) {
  const { t } = useTranslation();

  const [phone_number, setPhoneNumber] = useState("");
  const [first_name, setFirstName] = useState("");
  const [last_name, setLastName] = useState("");
  const [password, setPassword] = useState("");
  const [password_confirm, setPasswordConfirm] = useState("");

  const canSubmit = useMemo(() => {
    return (
      phone_number.trim().length > 0 &&
      first_name.trim().length > 0 &&
      last_name.trim().length > 0 &&
      password.length > 0 &&
      password_confirm.length > 0
    );
  }, [first_name, last_name, password, password_confirm, phone_number]);

  return (
    <Modal
      open={open}
      onOpenChange={onOpenChange}
      title={t("hrUsers.newUserTitle")}
      idBase="createHrUser"
      className="max-w-xl"
    >
      <form
        id="form-createHrUser"
        className="space-y-4"
        onSubmit={(e) => {
          e.preventDefault();
          onSubmit({
            phone_number: phone_number.trim(),
            first_name: first_name.trim(),
            last_name: last_name.trim(),
            password,
            password_confirm,
          });
        }}
      >
        {submitError && (
          <p id="text-createHrUserSubmitError" className="text-destructive text-sm">
            {submitError}
          </p>
        )}

        <div id="container-createHrUserPhone">
          <Label id="text-createHrUserPhoneLabel" htmlFor="input-createHrUserPhone">
            {t("common.phoneNumber")}
          </Label>
          <Input
            id="input-createHrUserPhone"
            dir="ltr"
            value={phone_number}
            onChange={(e) => setPhoneNumber(e.target.value)}
            placeholder={t("login.phonePlaceholder")}
            autoComplete="tel"
          />
        </div>

        <div id="container-createHrUserName" className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div id="container-createHrUserFirstName">
            <Label id="text-createHrUserFirstNameLabel" htmlFor="input-createHrUserFirstName">
              {t("common.firstName")}
            </Label>
            <Input
              id="input-createHrUserFirstName"
              value={first_name}
              onChange={(e) => setFirstName(e.target.value)}
              autoComplete="given-name"
            />
          </div>
          <div id="container-createHrUserLastName">
            <Label id="text-createHrUserLastNameLabel" htmlFor="input-createHrUserLastName">
              {t("common.lastName")}
            </Label>
            <Input
              id="input-createHrUserLastName"
              value={last_name}
              onChange={(e) => setLastName(e.target.value)}
              autoComplete="family-name"
            />
          </div>
        </div>

        <div id="container-createHrUserPassword">
          <Label id="text-createHrUserPasswordLabel" htmlFor="input-createHrUserPassword">
            {t("common.password")}
          </Label>
          <PasswordInput
            id="input-createHrUserPassword"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="new-password"
          />
        </div>

        <div id="container-createHrUserPasswordConfirm">
          <Label id="text-createHrUserPasswordConfirmLabel" htmlFor="input-createHrUserPasswordConfirm">
            {t("common.confirmPassword")}
          </Label>
          <PasswordInput
            id="input-createHrUserPasswordConfirm"
            value={password_confirm}
            onChange={(e) => setPasswordConfirm(e.target.value)}
            autoComplete="new-password"
          />
        </div>

        <div id="container-createHrUserActions" className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
          <Button
            id="button-cancelCreateHrUser"
            type="button"
            variant="outline"
            onClick={() => onOpenChange(false)}
            disabled={submitting}
          >
            {t("common.cancel")}
          </Button>
          <Button
            id="button-submitCreateHrUser"
            type="submit"
            disabled={!canSubmit || submitting}
          >
            {submitting ? t("common.loading") : t("hrUsers.createUser")}
          </Button>
        </div>
      </form>
    </Modal>
  );
}

