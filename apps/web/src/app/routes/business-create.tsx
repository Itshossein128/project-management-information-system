/**
 * Create business — `/businesses/create`. Requires `business-setup` group (parent layout).
 */
import {
  Button,
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  Input,
  Label,
} from "@/components/form";
import { useState } from "react";
import { Link, useNavigate } from "react-router";
import { useAuth } from "@/app/contexts/auth-context";
import { apiJson } from "@/app/lib/api-client";
import { PATHS } from "@/app/routeVars";
import { ROLES } from "@/config/roles";

export default function BusinessCreate() {
  const { hasRole, isLoading } = useAuth();
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [slug, setSlug] = useState("");
  const [formError, setFormError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);
    const payload = {
      name: name.trim(),
      slug: slug.trim().toLowerCase().replace(/\s+/g, "_"),
    };
    if (!payload.slug || !/^[a-z][a-z0-9_]*$/.test(payload.slug)) {
      setFormError(
        "Slug must start with a letter, then only lowercase letters, numbers, underscores.",
      );
      return;
    }
    try {
      await apiJson(`/${PATHS.API_PROJECTS}/`, {
        method: "POST",
        body: JSON.stringify(payload),
      });
      navigate(`/${PATHS.BUSINESS}`, { replace: true });
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Request failed";
      setFormError(typeof msg === "string" ? msg : "Request failed");
      if (
        err &&
        typeof err === "object" &&
        "errors" in err &&
        typeof (err as { errors: unknown }).errors === "object"
      ) {
        const errors = (err as { errors: Record<string, string[]> }).errors;
        const first = Object.values(errors).flat()[0];
        if (first) setFormError(first);
      }
    }
  };

  if (isLoading || !hasRole(ROLES.BUSINESS_SETUP)) return null;

  return (
    <div className="page-shell-padded">
      <div className="page-main mx-auto max-w-lg !p-0">
        <div className="mb-4">
          <Link
            id="button-backToBusinessesList"
            to={`/${PATHS.BUSINESS}`}
            className="text-muted-foreground text-sm hover:text-foreground"
          >
            ← Back to businesses
          </Link>
        </div>
        <Card id="container-businessCreateForm">
          <CardHeader>
            <CardTitle id="text-businessCreateTitle" className="text-lg">
              New business
            </CardTitle>
          </CardHeader>
          <CardContent>
            <form
              id="form-businessCreate"
              onSubmit={handleSubmit}
              className="space-y-4"
            >
              {formError && (
                <p id="text-businessCreateError" className="text-destructive text-sm">
                  {formError}
                </p>
              )}
              <div>
                <Label id="text-businessCreateNameLabel" htmlFor="input-businessCreateName">
                  Name
                </Label>
                <Input
                  id="input-businessCreateName"
                  name="businessCreateName"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                  placeholder="e.g. Main Warehouse"
                />
              </div>
              <div>
                <Label id="text-businessCreateSlugLabel" htmlFor="input-businessCreateSlug">
                  Slug
                </Label>
                <Input
                  id="input-businessCreateSlug"
                  name="businessCreateSlug"
                  value={slug}
                  onChange={(e) => setSlug(e.target.value)}
                  required
                  placeholder="e.g. main_warehouse"
                />
                <p
                  id="text-businessCreateSlugHelper"
                  className="mt-1 text-muted-foreground text-xs"
                >
                  Lowercase letters, numbers, underscores only. Cannot change
                  after create.
                </p>
              </div>
              <div id="container-businessCreateActions" className="flex gap-2">
                <Button id="button-submitBusinessCreate" type="submit">
                  Create
                </Button>
                <Button type="button" variant="outline" asChild>
                  <Link id="button-cancelBusinessCreate" to={`/${PATHS.BUSINESS}`}>
                    Cancel
                  </Link>
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
