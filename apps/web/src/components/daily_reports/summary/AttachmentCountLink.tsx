export function AttachmentCountLink({
  count,
  links,
  label,
}: {
  count: number;
  links: string[];
  label: string;
}) {
  return (
    <div className="text-sm" data-testid="attachment-count-link">
      <span>
        {label}: {count}
      </span>
      {links.slice(0, 3).map((href) => (
        <a key={href} href={href} className="ms-2 underline">
          {href}
        </a>
      ))}
    </div>
  );
}
