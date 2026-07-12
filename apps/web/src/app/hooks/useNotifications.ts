import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  type AppNotification,
  fetchNotifications,
  fetchUnreadCount,
  markAllNotificationsRead,
  markNotificationRead,
} from "@/app/lib/api/notifications";

const UNREAD_KEY = ["notifications", "unread-count"] as const;
const LIST_KEY = ["notifications", "list"] as const;

/** Poll the unread notification count every 60s. */
export function useUnreadCount(enabled = true) {
  return useQuery({
    queryKey: UNREAD_KEY,
    enabled,
    queryFn: fetchUnreadCount,
    refetchInterval: 60_000,
    refetchOnWindowFocus: true,
    select: (d) => d.unread,
  });
}

/** Fetch the most recent notifications (for the dropdown panel). */
export function useNotificationList(enabled: boolean) {
  return useQuery({
    queryKey: LIST_KEY,
    enabled,
    queryFn: () => fetchNotifications({ page_size: 20 }),
    select: (d): AppNotification[] => d.results,
  });
}

export function useNotificationActions() {
  const qc = useQueryClient();
  const invalidate = () => {
    void qc.invalidateQueries({ queryKey: ["notifications"] });
  };

  const markRead = useMutation({
    mutationFn: (id: string) => markNotificationRead(id),
    onSuccess: invalidate,
  });

  const markAllRead = useMutation({
    mutationFn: () => markAllNotificationsRead(),
    onSuccess: invalidate,
  });

  return { markRead, markAllRead };
}
