import { useMutation } from "@tanstack/react-query";
import { useState } from "react";
import {
  projectTypeLabels,
  saveProjectAsTemplate,
  type ProjectType,
} from "@/app/lib/api/templates";
import { Modal } from "@/components/overlay/modal";
import { Button } from "@/components/ui/sprint-button";
import { Input } from "@/components/form";
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
      toast.success("قالب با موفقیت ذخیره شد");
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
      title="ذخیره به‌عنوان قالب"
      idBase="saveAsTemplate"
      className="max-w-lg"
    >
      <div className="space-y-4">
        <div>
          <Label>نام قالب *</Label>
          <Input
            value={templateName}
            onChange={(e) => setTemplateName(e.target.value)}
            placeholder="مثلاً پروژه مسکونی نوع ۲"
          />
        </div>
        <div>
          <Label>توضیحات</Label>
          <Input
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
        </div>
        <div>
          <Label>نوع پروژه</Label>
          <select
            className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
            value={projectType}
            onChange={(e) => setProjectType(e.target.value as ProjectType)}
          >
            {PROJECT_TYPES.map((t) => (
              <option key={t} value={t}>
                {projectTypeLabels[t]}
              </option>
            ))}
          </select>
        </div>
        <div className="flex justify-end gap-2 pt-2">
          <Button variant="ghost" onClick={() => onOpenChange(false)}>
            انصراف
          </Button>
          <Button
            variant="primary"
            loading={saveMutation.isPending}
            disabled={!templateName.trim()}
            onClick={() => saveMutation.mutate()}
          >
            ذخیره
          </Button>
        </div>
      </div>
    </Modal>
  );
}
