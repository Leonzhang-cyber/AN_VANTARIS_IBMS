export type ProtocolCode =
  | "http"
  | "isapi"
  | "isup"
  | "modbus"
  | "mqtt"
  | "opcua"
  | "rtsp";

export type ExtractabilityStatus =
  | "READY_TO_WRAP"
  | "NEEDS_ADAPTER"
  | "NEEDS_REWRITE"
  | "SIMULATOR_ONLY"
  | "UNKNOWN";

export interface ProtocolPluginCapability {
  protocol: ProtocolCode;
  dryRunSupported: boolean;
}

export interface ProtocolPluginDescriptor {
  id: string;
  protocol: ProtocolCode;
  version: string;
  extractability: ExtractabilityStatus;
  capabilities: ProtocolPluginCapability[];
}
