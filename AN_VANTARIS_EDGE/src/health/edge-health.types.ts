export type EdgeHealthStatus =
  | "healthy"
  | "degraded"
  | "failed"
  | "starting"
  | "stopped"
  | "unknown";

export interface EdgeHealthSnapshot {
  status: EdgeHealthStatus;
  checkedAt: string;
  components: Record<string, EdgeHealthStatus>;
}
