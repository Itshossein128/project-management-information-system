import {
  Button,
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  Input,
  Label,
} from "@/components/form";
import { DataTable } from "@/components/grid";
import type { ColumnDef } from "@tanstack/react-table";
import { useCallback, useEffect, useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import { Link, useNavigate, useParams } from "react-router";
import { useAuth } from "src/app/contexts/auth-context";
import { apiJson } from "src/app/lib/api-client";
import { PATHS } from "src/app/routeVars";
import { ROLES } from "@/config/roles";

interface BusinessDetail {
  id: number;
  name: string;
  slug: string;
  created_at: string;
  updated_at: string;
}

interface TableItem {
  id: number;
  name: string;
  slug: string;
  ordering: number;
  created_at: string;
  updated_at: string;
}

interface TablesListResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: TableItem[];
}

export interface BusinessMembershipRow {
  id: number;
  user: number;
  phone_number: string;
  first_name: string;
  last_name: string;
  business_role: string;
  created_at: string;
  updated_at: string;
}

interface MembershipsListResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: BusinessMembershipRow[];
}

const BUSINESS_ROLE_OPTIONS = [
  { value: "worker", label: "Worker" },
  { value: "engineer", label: "Engineer" },
  { value: "manager", label: "Manager" },
  { value: "accountant", label: "Accountant" },
  { value: "site_engineer", label: "Site engineer" },
] as const;

function roleLabel(role: string): string {
  return BUSINESS_ROLE_OPTIONS.find((o) => o.value === role)?.label ?? role;
}

export default function BusinessPage() {
  const { t } = useTranslation();
  const { businessId } = useParams();
  const navigate = useNavigate();
  const { isAuthenticated, isLoading, hasRole } = useAuth();
  const [business, setBusiness] = useState<BusinessDetail | null>(null);
  const [tables, setTables] = useState<TableItem[]>([]);
  const [members, setMembers] = useState<BusinessMembershipRow[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [membersError, setMembersError] = useState<string | null>(null);
  const [showAddMember, setShowAddMember] = useState(false);
  const [addPhone, setAddPhone] = useState("");
  const [addFirst, setAddFirst] = useState("");
  const [addLast, setAddLast] = useState("");
  const [addRole, setAddRole] = useState<string>("worker");
  const [addSubmitting, setAddSubmitting] = useState(false);
  const [addFormError, setAddFormError] = useState<string | null>(null);

  const canManageMembers =
    hasRole(ROLES.MANAGER) || hasRole(ROLES.HR);

  const loadMembers = useCallback(
    (id: number) => {
      apiJson<MembershipsListResponse>(`/${PATHS.BUSINESS}/${id}/users/`)
        .then((data) => {
          setMembers(data.results);
          setMembersError(null);
        })
        .catch((e) =>
          setMembersError(
            e instanceof Error ? e.message : "Failed to load team",
          ),
        );
    },
    [],
  );

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      navigate("/login", { replace: true });
    }
  }, [isLoading, isAuthenticated, navigate]);

  useEffect(() => {
    if (!isAuthenticated || !businessId) return;
    const id = Number(businessId);
    if (Number.isNaN(id)) {
      setError("Invalid business");
      return;
    }
    Promise.all([
      apiJson<BusinessDetail>(`/${PATHS.BUSINESS}/${id}/`),
      apiJson<TablesListResponse>(`/${PATHS.BUSINESS}/${id}/tables/`),
    ])
      .then(([b, tListData]) => {
        setBusiness(b);
        setTables(tListData.results);
        setError(null);
        loadMembers(id);
      })
      .catch((e) =>
        setError(e instanceof Error ? e.message : "Failed to load"),
      );
  }, [isAuthenticated, businessId, loadMembers]);

  const handleAddMember = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!businessId || !canManageMembers) return;
    const id = Number(businessId);
    setAddFormError(null);
    setAddSubmitting(true);
    try {
      await apiJson(`/${PATHS.BUSINESS}/${id}/users/`, {
        method: "POST",
        body: JSON.stringify({
          phone_number: addPhone.trim(),
          first_name: addFirst.trim(),
          last_name: addLast.trim(),
          business_role: addRole,
        }),
      });
      setShowAddMember(false);
      setAddPhone("");
      setAddFirst("");
      setAddLast("");
      setAddRole("worker");
      loadMembers(id);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Request failed";
      setAddFormError(msg);
      if (
        err &&
        typeof err === "object" &&
        "errors" in err &&
        typeof (err as { errors: unknown }).errors === "object"
      ) {
        const errors = (err as { errors: Record<string, string[]> }).errors;
        const first = Object.values(errors).flat()[0];
        if (first) setAddFormError(first);
      }
    } finally {
      setAddSubmitting(false);
    }
  };

  const updateMemberRole = useCallback(
    async (membershipId: number, business_role: string) => {
      if (!businessId || !canManageMembers) return;
      const id = Number(businessId);
      try {
        await apiJson(`/${PATHS.BUSINESS}/${id}/users/${membershipId}/`, {
          method: "PATCH",
          body: JSON.stringify({ business_role }),
        });
        loadMembers(id);
      } catch {
        /* surface via toast in future */
      }
    },
    [businessId, canManageMembers, loadMembers],
  );

  const removeMember = useCallback(
    async (membershipId: number) => {
      if (!businessId || !canManageMembers) return;
      const id = Number(businessId);
      if (!window.confirm("Remove this user from the business?")) return;
      try {
        await apiJson(`/${PATHS.BUSINESS}/${id}/users/${membershipId}/`, {
          method: "DELETE",
        });
        loadMembers(id);
      } catch {
        /* ignore */
      }
    },
    [businessId, canManageMembers, loadMembers],
  );

  const memberColumns = useMemo<ColumnDef<BusinessMembershipRow>[]>(() => {
    return [
      {
        accessorKey: "phone_number",
        header: "Phone",
        cell: ({ row }) => (
          <span id={`text-memberPhone-${row.index}`}>{row.original.phone_number}</span>
        ),
      },
      {
        id: "name",
        header: "Name",
        cell: ({ row }) => (
          <span id={`text-memberName-${row.index}`}>
            {`${row.original.first_name} ${row.original.last_name}`.trim() ||
              "—"}
          </span>
        ),
      },
      {
        accessorKey: "business_role",
        header: "Role",
        cell: ({ row }) => (
          <span id={`container-memberRole-${row.index}`}>
            {canManageMembers ? (
              <select
                id={`select-memberRole-${row.index}`}
                className="border-input bg-background ring-offset-background focus-visible:ring-ring max-w-[180px] rounded-md border px-2 py-1 text-sm focus-visible:ring-2 focus-visible:outline-none"
                value={row.original.business_role}
                onChange={(e) =>
                  updateMemberRole(row.original.id, e.target.value)
                }
              >
                {BUSINESS_ROLE_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            ) : (
              <span id={`text-memberRoleLabel-${row.index}`}>
                {roleLabel(row.original.business_role)}
              </span>
            )}
          </span>
        ),
      },
      ...(canManageMembers
        ? [
            {
              id: "actions",
              header: "Actions",
              cell: ({ row }) => (
                <Button
                  id={`button-removeMember-${row.index}`}
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => removeMember(row.original.id)}
                >
                  Remove
                </Button>
              ),
            } satisfies ColumnDef<BusinessMembershipRow>,
          ]
        : []),
    ];
  }, [canManageMembers, updateMemberRole, removeMember]);

  if (isLoading || !isAuthenticated) return null;

  return (
    <div className="min-h-svh bg-muted/30">
      <header className="border-b bg-background px-4 py-3">
        <div className="mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Button
              id="button-backFromBusiness"
              variant="ghost"
              size="sm"
              type="button"
              onClick={() => navigate(`/${PATHS.HOME}`)}
            >
              {t("common.back")}
            </Button>
            <h1 id="text-businessTitle" className="text-lg font-semibold">
              {business?.name ?? "Business"}
            </h1>
          </div>
        </div>
      </header>

      <main className="mx-auto p-4">
        {error && (
          <p id="text-businessError" className="mb-4 text-destructive text-sm">
            {error}
          </p>
        )}
        {business && (
          <>
            <section
              id="container-businessTeam"
              className="mb-10"
              aria-labelledby="text-teamHeading"
            >
              <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
                <h2 id="text-teamHeading" className="text-xl font-medium">
                  Team
                </h2>
                {canManageMembers && (
                  <Button
                    id="button-addTeamMember"
                    type="button"
                    size="sm"
                    onClick={() => {
                      setShowAddMember((v) => !v);
                      setAddFormError(null);
                    }}
                  >
                    Add user
                  </Button>
                )}
              </div>
              {membersError && (
                <p
                  id="text-teamLoadError"
                  className="mb-2 text-destructive text-sm"
                >
                  {membersError}
                </p>
              )}
              {canManageMembers && showAddMember && (
                <Card id="container-addMemberForm" className="mb-4">
                  <CardHeader>
                    <CardTitle id="text-addMemberTitle" className="text-base">
                      Add user to business
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <form
                      id="form-addMember"
                      className="grid max-w-xl gap-4 sm:grid-cols-2"
                      onSubmit={handleAddMember}
                    >
                      {addFormError && (
                        <p
                          id="text-addMemberError"
                          className="text-destructive text-sm sm:col-span-2"
                        >
                          {addFormError}
                        </p>
                      )}
                      <div className="sm:col-span-2">
                        <Label
                          id="text-addMemberPhoneLabel"
                          htmlFor="input-addMemberPhone"
                        >
                          Phone number
                        </Label>
                        <Input
                          id="input-addMemberPhone"
                          name="addMemberPhone"
                          type="tel"
                          required
                          value={addPhone}
                          onChange={(e) => setAddPhone(e.target.value)}
                          placeholder="+989123456789"
                        />
                      </div>
                      <div>
                        <Label
                          id="text-addMemberFirstLabel"
                          htmlFor="input-addMemberFirst"
                        >
                          First name
                        </Label>
                        <Input
                          id="input-addMemberFirst"
                          name="addMemberFirst"
                          value={addFirst}
                          onChange={(e) => setAddFirst(e.target.value)}
                        />
                      </div>
                      <div>
                        <Label
                          id="text-addMemberLastLabel"
                          htmlFor="input-addMemberLast"
                        >
                          Last name
                        </Label>
                        <Input
                          id="input-addMemberLast"
                          name="addMemberLast"
                          value={addLast}
                          onChange={(e) => setAddLast(e.target.value)}
                        />
                      </div>
                      <div className="sm:col-span-2">
                        <Label
                          id="text-addMemberRoleLabel"
                          htmlFor="select-addMemberRole"
                        >
                          Business role
                        </Label>
                        <select
                          id="select-addMemberRole"
                          className="border-input bg-background ring-offset-background focus-visible:ring-ring max-w-xs rounded-md border px-3 py-2 text-sm focus-visible:ring-2 focus-visible:outline-none"
                          value={addRole}
                          onChange={(e) => setAddRole(e.target.value)}
                        >
                          {BUSINESS_ROLE_OPTIONS.map((opt) => (
                            <option key={opt.value} value={opt.value}>
                              {opt.label}
                            </option>
                          ))}
                        </select>
                      </div>
                      <div
                        id="container-addMemberActions"
                        className="flex gap-2 sm:col-span-2"
                      >
                        <Button
                          id="button-submitAddMember"
                          type="submit"
                          disabled={addSubmitting}
                        >
                          {addSubmitting ? "Saving…" : "Add"}
                        </Button>
                        <Button
                          id="button-cancelAddMember"
                          type="button"
                          variant="outline"
                          onClick={() => setShowAddMember(false)}
                        >
                          Cancel
                        </Button>
                      </div>
                    </form>
                  </CardContent>
                </Card>
              )}
              <DataTable
                name="businessMembers"
                columns={memberColumns}
                data={members}
                emptyMessage="No users linked to this business yet."
              />
            </section>

            <h2 id="text-tablesHeading" className="mb-4 text-xl font-medium">
              Tables
            </h2>
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {tables.map((table) => (
                <Card key={table.id} id={`container-tableCard-${table.id}`}>
                  <CardHeader>
                    <CardTitle className="text-base">{table.name}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="mb-3 text-muted-foreground text-sm">
                      Slug: {table.slug}
                    </p>
                    <Link
                      id={`link-tableRows-${table.id}`}
                      to={`/${PATHS.BUSINESS}/${businessId}/tables/${table.slug}`}
                    >
                      <Button variant="outline" size="sm" type="button">
                        View rows
                      </Button>
                    </Link>
                  </CardContent>
                </Card>
              ))}
            </div>
            {tables.length === 0 && (
              <p className="text-muted-foreground text-sm">
                No tables defined for this business.
              </p>
            )}
          </>
        )}
      </main>
    </div>
  );
}
