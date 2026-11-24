import { useState } from "react";
import { useTranslation } from "react-i18next";
import { apiJson } from "@/app/lib/api-client";
import { useToast } from "@/components/ui/toast";

export function AttachmentCountLink({
  count,
  links,
  label,
}: {
  count: number;
  links: string[];
  label: string;
}) {
  const { t } = useTranslation();
  const toast = useToast();
  const [pending, setPending] = useState<string | null>(null);

  const download = async (href: string) => {
    setPending(href);
    try {
      const { download_url } = await apiJson<{ download_url: string }>(href.replace(/^\/api\//, "/"));
      window.location.assign(download_url);
    } catch {
      toast.error(t("dailyReports.referenceHeader.attachmentUnavailable"));
    } finally {
      setPending(null);
    }
  };

  return (
    <div className="text-sm" data-testid="attachment-count-link">
      <span>
        {label}: {count}
      </span>
      {links.slice(0, 3).map((href, index) => href.endsWith("/download/") ? (
        <button key={href} type="button" disabled={pending !== null}
          onClick={() => void download(href)} className="ms-2 text-primary underline">
          {t("dailyReports.referenceHeader.attachmentDownload", { number: index + 1 })}
        </button>
      ) : (
        <a key={href} href={href} className="ms-2 text-primary underline">
          مشاهده فهرست
        </a>
      ))}
    </div>
  );
}
