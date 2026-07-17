import { redirect } from "react-router";
import {
  getAccessTokenFromRequest,
  hasStoredSession,
} from "src/app/lib/auth-storage";

export async function loader({ request }: { request: Request }) {
  // Client: use localStorage
  if (typeof window !== "undefined") {
    if (hasStoredSession()) throw redirect("/projects");
    throw redirect("/login");
  }
  // Server: use cookie so SSR respects auth
  if (getAccessTokenFromRequest(request)) throw redirect("/projects");
  throw redirect("/login");
}

export default function Index() {
  return null;
}
