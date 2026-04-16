import { useAuth } from "~/contexts/auth-context";
import { isRTL } from "~/lib/i18n";
import { useNavigation } from "../hooks/useNavigation";
import { SidebarItem } from "./components/sidebarItem";

export const Sidebar = ({ className }) => {
  const { user } = useAuth();
  const items = useNavigation(user?.roles);
  console.log(items, "inja item");
  return (
    <nav
      className={`bg-sidebar ${isRTL() ? "border-l" : "border-r"} ${className} shadow`}
    >
      <ul className="flex flex-col">
        {items.map((item) => (
          <li key={item.path}>
            <SidebarItem {...item} />
          </li>
        ))}
      </ul>
    </nav>
  );
};
