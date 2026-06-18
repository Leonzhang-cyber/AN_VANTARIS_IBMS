export type EdgeRuntimeCapability =
  | "connector-manager"
  | "protocol-plugin-runtime"
  | "normalization"
  | "durable-buffer"
  | "health"
  | "diagnostics"
  | "security"
  | "dry-run";

export interface EdgePackageStatus {
  packageName: "AN_VANTARIS_EDGE";
  status: "SKELETON_ONLY";
  runtimeReady: false;
  gaReady: false;
  sourceMigration: "NOT_STARTED";
}

export interface EdgeRuntimeStatus {
  status: "starting" | "stopped" | "unknown";
  capabilities: EdgeRuntimeCapability[];
}
