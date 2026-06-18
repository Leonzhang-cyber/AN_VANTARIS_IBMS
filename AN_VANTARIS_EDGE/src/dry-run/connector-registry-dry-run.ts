import { ConnectorRegistry } from "../connectors/connector-registry.js";
import {
  demoConnectorFixtures,
  demoModbusConnector,
  demoMqttConnector,
  demoIsapiConnector,
  demoIsupConnector,
  demoRtspConnector
} from "../connectors/connector-fixtures.js";
import type { EdgeDryRunResult } from "./dry-run.types.js";

const result = (caseId: string, success: boolean, notes: string[]): EdgeDryRunResult => ({
  caseId,
  success,
  checkedAt: new Date().toISOString(),
  notes
});

export const runConnectorRegistryDryRun = (): EdgeDryRunResult[] => {
  const registry = new ConnectorRegistry();
  const outputs: EdgeDryRunResult[] = [];

  // CASE 1 — register all demo connectors
  const registerResults = demoConnectorFixtures.map((entry) => registry.register(entry));
  outputs.push(
    result(
      "CASE_1_REGISTER_ALL",
      registerResults.every((r) => r.success),
      [`registered=${registerResults.filter((r) => r.success).length}/${registerResults.length}`]
    )
  );

  // CASE 2 — list connectors
  const list = registry.list();
  outputs.push(result("CASE_2_LIST_CONNECTORS", list.length === demoConnectorFixtures.length, [`listCount=${list.length}`]));

  // CASE 3 — start modbus connector
  const startModbus = registry.start(demoModbusConnector.connectorId);
  outputs.push(result("CASE_3_START_MODBUS", startModbus.success, [JSON.stringify(startModbus)]));

  // CASE 4 — stop modbus connector
  const stopModbus = registry.stop(demoModbusConnector.connectorId);
  outputs.push(result("CASE_4_STOP_MODBUS", stopModbus.success, [JSON.stringify(stopModbus)]));

  // CASE 5 — restart mqtt connector
  const restartMqtt = registry.restart(demoMqttConnector.connectorId);
  outputs.push(result("CASE_5_RESTART_MQTT", restartMqtt.success, [JSON.stringify(restartMqtt)]));

  // CASE 6 — mark isapi degraded
  const degradeIsapi = registry.markDegraded(demoIsapiConnector.connectorId, "dry-run warning");
  outputs.push(result("CASE_6_MARK_ISAPI_DEGRADED", degradeIsapi.success, [JSON.stringify(degradeIsapi)]));

  // CASE 7 — mark isup failed
  const failIsup = registry.markFailed(demoIsupConnector.connectorId, "dry-run failure");
  outputs.push(result("CASE_7_MARK_ISUP_FAILED", failIsup.success, [JSON.stringify(failIsup)]));

  // CASE 8 — disable rtsp connector
  const disableRtsp = registry.disable(demoRtspConnector.connectorId);
  outputs.push(result("CASE_8_DISABLE_RTSP", disableRtsp.success, [JSON.stringify(disableRtsp)]));

  // CASE 9 — duplicate register rejected
  const duplicate = registry.register(demoMqttConnector);
  outputs.push(
    result(
      "CASE_9_DUPLICATE_REGISTER_REJECTED",
      !duplicate.success && duplicate.error?.code === "CONNECTOR_ALREADY_EXISTS",
      [JSON.stringify(duplicate)]
    )
  );

  // CASE 10 — snapshot generated
  const snapshot = registry.snapshot();
  outputs.push(
    result("CASE_10_SNAPSHOT_GENERATED", snapshot.total === demoConnectorFixtures.length, [JSON.stringify(snapshot.byStatus)])
  );

  return outputs;
};
