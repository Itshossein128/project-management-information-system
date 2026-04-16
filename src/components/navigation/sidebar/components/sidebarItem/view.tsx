import { useState } from "react";
import { NavLink, useLocation } from "react-router";
import { ICONS } from "@/components/icons";

export interface SidebarItemProps {
  label: string;
  icon?: React.ReactNode;
  path?: string;
}

export const SidebarItem = ({ label, icon, path }: SidebarItemProps) => {
  const location = useLocation();
  const Icon = ICONS[icon];
  const isActive = path && location.pathname.slice(1).startsWith(path);

  return (
    <NavLink
      to={path!}
      className={`sidebar-item ${isActive ? "bg-blue-300" : ""} flex flex-col items-center text-center px-1 py-2 [&:not(.active)]:hover:bg-blue-100 transition`}
    >
      <Icon className='w-9 h-9' />
      <span className='label'>{label}</span>
    </NavLink>
  );
};
