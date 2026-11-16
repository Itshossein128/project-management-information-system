import { useMutation } from "@tanstack/react-query";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import {
  getProjectTypeLabel,
  saveProjectAsTemplate,
  type ProjectType,
} from "@/app/lib/api/templates";
import { Modal } from "@/components/overlay/modal";
import { Button } from "@/components/ui/sprint-button";
import { Input, Select } from "@/components/form";
import { Label } from "@/components/ui/label";
import { useToast } from "@/components/ui/toast";

const PROJECT_TYPES: ProjectType[] = [
  "residential",
  "road",
  "commercial",
  "industrial",
  "epc",
  "other",
];

interface SaveAsTemplateModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  projectId: string;
}

export function SaveAsTemplateModal({
  open,
  onOpenChange,
  projectId,
}: SaveAsTemplateModalProps) {
  const { t } = useTranslation();
  const toast = useToast();
  const [templateName, setTemplateName] = useState("");
  const [description, setDescription] = useState("");
  const [projectType, setProjectType] = useState<ProjectType>("other");

  const saveMutation = useMutation({
    mutationFn: () =>
      saveProjectAsTemplate(projectId, {
        template_name: templateName,
        description,
        project_type: projectType,
      }),
    onSuccess: () => {
      toast.success(t("wbs.templateSaved"));
      onOpenChange(false);
      setTemplateName("");
      setDescription("");
      setProjectType("other");
    },
    onError: (e: Error) => toast.error(e.message),
  });

  return (
    <Modal
      open={open}
      onOpenChange={onOpenChange}
      title={t("wbs.saveAsTemplate")}
      idBase="saveAsTemplate"
      className="max-w-lg"
    >
      <div className="space-y-4">
        <div>
          <Label htmlFor="template-name">{t("wbs.templateName")} *</Label>
          <Input
            id="template-name"
            value={templateName}
            onChange={(e) => setTemplateName(e.target.value)}
            placeholder={t("wbs.templateNamePlaceholder")}
          />
        </div>
        <div>
          <Label htmlFor="template-description">{t("wbs.templateDescription")}</Label>
          <Input
            id="template-description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
        </div>
        <div>
          <Label htmlFor="template-type">{t("wbs.templateType")}</Label>
          <Select
            id="template-type"
            name="projectType"
            value={projectType}
            onChange={(e) => setProjectType(e.target.value as ProjectType)}
            options={PROJECT_TYPES.map((type) => ({
              value: type,
              label: getProjectTypeLabel(type, t),
            }))}
          />
        </div>
        <div className="flex justify-end gap-2 pt-2">
          <Button variant="ghost" onClick={() => onOpenChange(false)}>
            {t("common.cancel")}
          </Button>
          <Button
            variant="primary"
            loading={saveMutation.isPending}
            disabled={!templateName.trim()}
            onClick={() => saveMutation.mutate()}
          >
            {t("common.save")}
          </Button>
        </div>
      </div>
    </Modal>
  );
}
