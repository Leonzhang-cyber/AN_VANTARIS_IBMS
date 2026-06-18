import type { ConnectorRegistryEntry } from "./connector-registry.types.js";

type ConnectorFixture = Omit<ConnectorRegistryEntry, "createdAt" | "updatedAt" | "lastError" | "lastDataAt"> & {
  lastError?: string;
};

export const demoHttpConnector: ConnectorFixture = {
  connectorId: "demo-http-001",
  connectorName: "Demo HTTP Connector",
  protocolCode: "http",
  tenantId: "tenant-demo",
  projectId: "project-demo",
  siteId: "site-demo",
  sourceSystemId: "demo-bms",
  gatewayId: "edge-demo-001",
  status: "configured",
  capabilities: ["polling", "telemetry"]
};

export const demoModbusConnector: ConnectorFixture = {
  connectorId: "demo-modbus-001",
  connectorName: "Demo Modbus Connector",
  protocolCode: "modbus",
  tenantId: "tenant-demo",
  projectId: "project-demo",
  siteId: "site-demo",
  sourceSystemId: "demo-bms",
  gatewayId: "edge-demo-001",
  status: "configured",
  capabilities: ["polling", "telemetry"]
};

export const demoMqttConnector: ConnectorFixture = {
  connectorId: "demo-mqtt-001",
  connectorName: "Demo MQTT Connector",
  protocolCode: "mqtt",
  tenantId: "tenant-demo",
  projectId: "project-demo",
  siteId: "site-demo",
  sourceSystemId: "demo-bms",
  gatewayId: "edge-demo-001",
  status: "configured",
  capabilities: ["pubsub", "telemetry"]
};

export const demoIsapiConnector: ConnectorFixture = {
  connectorId: "demo-isapi-001",
  connectorName: "Demo ISAPI Connector",
  protocolCode: "isapi",
  tenantId: "tenant-demo",
  projectId: "project-demo",
  siteId: "site-demo",
  sourceSystemId: "demo-video",
  gatewayId: "edge-demo-001",
  status: "configured",
  capabilities: ["control", "event"]
};

export const demoIsupConnector: ConnectorFixture = {
  connectorId: "demo-isup-001",
  connectorName: "Demo ISUP Connector",
  protocolCode: "isup",
  tenantId: "tenant-demo",
  projectId: "project-demo",
  siteId: "site-demo",
  sourceSystemId: "demo-video",
  gatewayId: "edge-demo-001",
  status: "configured",
  capabilities: ["ingress", "event"]
};

export const demoRtspConnector: ConnectorFixture = {
  connectorId: "demo-rtsp-001",
  connectorName: "Demo RTSP Connector",
  protocolCode: "rtsp",
  tenantId: "tenant-demo",
  projectId: "project-demo",
  siteId: "site-demo",
  sourceSystemId: "demo-video",
  gatewayId: "edge-demo-001",
  status: "configured",
  capabilities: ["stream", "telemetry"]
};

export const demoOpcuaConnector: ConnectorFixture = {
  connectorId: "demo-opcua-001",
  connectorName: "Demo OPCUA Connector",
  protocolCode: "opcua",
  tenantId: "tenant-demo",
  projectId: "project-demo",
  siteId: "site-demo",
  sourceSystemId: "demo-opcua-source",
  gatewayId: "edge-demo-001",
  status: "disabled",
  capabilities: ["placeholder"]
};

export const demoConnectorFixtures: ConnectorFixture[] = [
  demoHttpConnector,
  demoModbusConnector,
  demoMqttConnector,
  demoIsapiConnector,
  demoIsupConnector,
  demoRtspConnector,
  demoOpcuaConnector
];
