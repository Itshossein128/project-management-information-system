import { apiBlob, apiJson } from "@/app/lib/api-client";
import { PATHS } from "@/app/routeVars";

const base = (projectId: string) => `/${PATHS.API_PROJECTS}/${projectId}`;
export interface ConcreteBatch {
  id: string;
  date: string;
  volume_m3: string;
  cement_kg: string;
  sand_kg: string;
  aggregate_kg: string;
  water_l: string;
  plasticizer_l: string;
}
export interface ReadyMixDelivery {
  id: string;
  date: string;
  volume_m3: string;
  supplier: string;
  supplier_name: string;
  ticket_number: string;
}
export interface ConcreteTotals {
  produced_m3: string;
  delivered_m3: string;
  poured_m3: string;
}
export interface Page<T> { count: number; results: T[] }
export interface DateFilter { date_from?: string; date_to?: string }
const params = (filter: DateFilter) => {
  const search = new URLSearchParams();
  if (filter.date_from) search.set("date_from", filter.date_from);
  if (filter.date_to) search.set("date_to", filter.date_to);
  return search.toString();
};
export const fetchConcreteBatches = (id: string) => apiJson<Page<ConcreteBatch>>(`${base(id)}/concrete-batches/`);
export const fetchReadyMixDeliveries = (id: string) => apiJson<Page<ReadyMixDelivery>>(`${base(id)}/ready-mix-deliveries/`);
export const fetchConcreteTotals = (id: string, filter: DateFilter) => apiJson<ConcreteTotals>(`${base(id)}/concrete-operations/summary/?${params(filter)}`);
export const exportConcreteOperations = (id: string, filter: DateFilter) => apiBlob(`${base(id)}/concrete-operations/export/?${params(filter)}`);
export const createConcreteBatch = (id: string, body: Omit<ConcreteBatch, "id">) => apiJson<ConcreteBatch>(`${base(id)}/concrete-batches/`, { method: "POST", body: JSON.stringify(body) });
export const createReadyMixDelivery = (id: string, body: Omit<ReadyMixDelivery, "id" | "supplier_name">) => apiJson<ReadyMixDelivery>(`${base(id)}/ready-mix-deliveries/`, { method: "POST", body: JSON.stringify(body) });
export const deleteConcreteBatch = (id: string, rowId: string) => apiJson<void>(`${base(id)}/concrete-batches/${rowId}/`, { method: "DELETE" });
export const deleteReadyMixDelivery = (id: string, rowId: string) => apiJson<void>(`${base(id)}/ready-mix-deliveries/${rowId}/`, { method: "DELETE" });
