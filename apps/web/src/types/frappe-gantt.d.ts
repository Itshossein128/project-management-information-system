declare module "frappe-gantt" {
  export type GanttViewMode = "Quarter Day" | "Half Day" | "Day" | "Week" | "Month" | "Year";

  export interface GanttTask {
    id: string;
    name: string;
    start: string;
    end: string;
    progress?: number;
    dependencies?: string;
    custom_class?: string;
  }

  export interface GanttOptions {
    view_mode?: GanttViewMode;
    language?: string;
    readonly?: boolean;
    bar_height?: number;
    padding?: number;
    on_click?: (task: GanttTask) => void;
  }

  export default class Gantt {
    constructor(wrapper: HTMLElement, tasks: GanttTask[], options?: GanttOptions);
    change_view_mode(mode: GanttViewMode): void;
    scroll_current?(): void;
  }
}
