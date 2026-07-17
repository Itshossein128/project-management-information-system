import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { createWBSNode } from "@/app/lib/api/wbs";
import { Input, Label } from "@/components/form";
import { Button } from "@/components/ui/sprint-button";
import { useToast } from "@/components/ui/toast";

interface WbsEmptyStateProps {
  projectId: string;
  onCreated: () => void;
}

export function WbsEmptyState({ projectId, onCreated }: WbsEmptyStateProps) {
  const toast = useToast();
  const qc = useQueryClient();
  const [code, setCode] = useState("1");
  const [name, setName] = useState("");

  const createMutation = useMutation({
    mutationFn: () =>
      createWBSNode(projectId, {
        wbs_code: code.trim(),
        wbs_name: name.trim(),
      }),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ["wbs", projectId] });
      onCreated();
    },
    onError: (err: Error) => toast.error(err.message),
  });

  return (
    <div className='mx-auto max-w-md space-y-4 rounded-lg border border-border p-6'>
      <p className='text-muted-foreground text-sm'>
        هنوز گره WBS ایجاد نشده است. اولین گره ریشه را اضافه کنید یا از MSP /
        P6 بارگذاری کنید.
      </p>
      <div>
        <Label htmlFor='input-rootWbsCode'>کد WBS</Label>
        <Input
          id='input-rootWbsCode'
          value={code}
          onChange={(e) => setCode(e.target.value)}
        />
      </div>
      <div>
        <Label htmlFor='input-rootWbsName'>نام *</Label>
        <Input
          id='input-rootWbsName'
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
        />
      </div>
      <Button
        type='button'
        variant='primary'
        disabled={!name.trim() || !code.trim()}
        loading={createMutation.isPending}
        onClick={() => createMutation.mutate()}
      >
        افزودن گره ریشه
      </Button>
    </div>
  );
}
