import { Navigate } from "react-router";
import { PATHS } from "@/app/routeVars";

/**
 * Legacy `/home` route — redirects to the canonical project list at `/projects`.
 */
export default function Home() {
  return <Navigate to={`/${PATHS.PROJECT}`} replace />;
}
