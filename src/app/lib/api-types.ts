export type Id = number;

export interface ListResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface Business {
  id: Id;
  name: string;
  slug: string;
  created_at: string;
  updated_at: string;
}

export interface BusinessJobPosition {
  id: Id;
  business: Id;
  slug: string;
  label: string;
  ordering: number;
}

export type AssignmentStatus = "active" | "suspended" | "archived" | string;

export interface UserMini {
  id: Id;
  phone_number: string;
  full_name: string;
}

export interface UserBusinessAssignment {
  id: Id;
  user: UserMini | Id;
  business: Business | Id;
  job_position: BusinessJobPosition | Id;
  wage?: string | null;
  weekly_total?: string | null;
  monthly_total?: string | null;
  tools?: string[];
  start_date?: string | null;
  end_date?: string | null;
  status?: AssignmentStatus;
  created_at?: string;
  updated_at?: string;
}

