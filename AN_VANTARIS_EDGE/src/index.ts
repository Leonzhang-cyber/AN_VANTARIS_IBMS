export const EDGE_PACKAGE_STATUS = {
  packageName: "AN_VANTARIS_EDGE",
  status: "SKELETON_ONLY",
  runtimeReady: false,
  gaReady: false
} as const;

export * as connectors from "./connectors/index.js";
export { runConnectorRegistryDryRun } from "./dry-run/connector-registry-dry-run.js";
