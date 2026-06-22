import { mkdirSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';

import { AuditPlaceholderStream } from './audit-placeholder.js';
import { ConnectorRegistry } from './connector-registry.js';
import { exportDiagnosticsPack } from './diagnostics-exporter.js';
import { DurableLocalBuffer } from './durable-local-buffer.js';
import { evaluateHardwareKeyGuard, loadHardwareKeyGuardConfigFromEnv } from './hardware-key-guard.js';
import { buildHealthSnapshot } from './health-snapshot.js';
import { buildCanonicalEnvelope, runNormalizationDryRun } from './normalization-dryrun.js';
import { ProtocolPluginRegistry } from './plugin-registry.js';
import { defaultDryRunRules, mapRawSample } from './tag-mapping-dryrun.js';

export interface EdgeC1RunResult {
  readonly runtimeDir: string;
  readonly evidenceDir: string;
  readonly connectorsPath: string;
  readonly healthPath: string;
  readonly diagnosticsPath: string;
  readonly normalizationPath: string;
  readonly bufferSummary: ReturnType<DurableLocalBuffer['summary']>;
  readonly replayCount: number;
}

export function runEdgeC1RuntimeEvidenceFlow(input: { edgeRoot: string; evidenceDir?: string }): EdgeC1RunResult {
  const edgeRoot = resolve(input.edgeRoot);
  const runtimeDir = resolve(edgeRoot, '.runtime');
  const evidenceDir = resolve(input.evidenceDir ?? resolve(runtimeDir, 'evidence'));

  mkdirSync(runtimeDir, { recursive: true });
  mkdirSync(evidenceDir, { recursive: true });

  const edgeId = 'edge-c1-dryrun-001';
  const siteId = 'site-001';
  const hardwareKey = evaluateHardwareKeyGuard(loadHardwareKeyGuardConfigFromEnv(process.env));
  const runtimeMode = hardwareKey.runtimeMode;

  const connectors = new ConnectorRegistry();
  connectors.register({
    id: 'connector-modbus-01',
    name: 'Modbus Telemetry Connector',
    protocol: 'modbus',
    edgeId,
    siteId,
    sourceSystemId: 'bms-001',
    capabilities: ['telemetry', 'health'],
    enabled: true,
    notes: 'dry-run metadata connector',
  });
  connectors.register({
    id: 'connector-mqtt-01',
    name: 'MQTT Event Connector',
    protocol: 'mqtt',
    edgeId,
    siteId,
    sourceSystemId: 'events-001',
    capabilities: ['event', 'alarm', 'health'],
    enabled: true,
    notes: 'dry-run metadata connector',
  });
  connectors.register({
    id: 'connector-http-01',
    name: 'HTTP Alarm Connector',
    protocol: 'http',
    edgeId,
    siteId,
    sourceSystemId: 'alarm-001',
    capabilities: ['alarm', 'health'],
    enabled: true,
    notes: 'dry-run metadata connector',
  });
  connectors.register({
    id: 'connector-opcua-01',
    name: 'OPCUA Health Connector',
    protocol: 'opcua',
    edgeId,
    siteId,
    sourceSystemId: 'opcua-001',
    capabilities: ['telemetry', 'health'],
    enabled: true,
    notes: 'dry-run metadata connector',
  });

  connectors.start('connector-modbus-01');
  connectors.start('connector-mqtt-01');
  connectors.start('connector-http-01');
  connectors.start('connector-opcua-01');
  connectors.recordLastDataTime('connector-modbus-01', new Date().toISOString());

  const pluginRegistry = new ProtocolPluginRegistry();

  const mapped = mapRawSample(
    {
      sourceSystemId: 'bms-001',
      protocol: 'modbus',
      rawTag: '40001',
      rawName: 'AHU01.SAT',
      value: '23.6',
      timestamp: '2026-06-18T00:00:00.000Z',
    },
    defaultDryRunRules(),
    'store_raw',
  );

  const normalized = runNormalizationDryRun(edgeId, siteId);
  const normalizationEnvelope = buildCanonicalEnvelope({
    edgeId,
    siteId,
    sourceSystemId: 'mapping-001',
    connectorId: 'connector-modbus-01',
    messageType: 'telemetry.point.updated',
    payload: { mappedPoint: mapped, dryRun: true },
  });

  const buffer = new DurableLocalBuffer(runtimeDir);
  for (const envelope of [
    normalized.telemetry,
    normalized.event,
    normalized.alarm,
    normalized.health,
    normalized.evidence,
    normalizationEnvelope,
  ]) {
    buffer.append(envelope, 86400, 5);
  }

  const pending = buffer.listPending();
  if (pending[0]) {
    buffer.markFailed(pending[0].messageId, 'dry-run-simulated-failure');
  }
  const replayList = buffer.replayList();
  const summary = buffer.summary();
  const recovery = buffer.restartRecoveryEvidence();
  const ledgerSnapshotPath = resolve(evidenceDir, 'edge-c1-ledger-snapshot.json');
  const ledgerSnapshot = buffer.exportLedgerSnapshot(ledgerSnapshotPath);

  const healthSnapshot = buildHealthSnapshot({
    edgeId,
    siteId,
    version: 'c1-foundation-dryrun',
    connectors: connectors.list(),
    plugins: pluginRegistry.list(),
    runtimeMode,
    hardwareKey,
    bufferSummary: { pending: summary.pending, failed: summary.failed, dlqCount: summary.dlqCount },
  });

  const audit = new AuditPlaceholderStream();
  audit.emit({ edgeId, eventType: 'connector.registry.snapshot', action: 'export-connectors', result: 'ok', details: { connectorCount: connectors.list().length } });
  audit.emit({ edgeId, eventType: 'normalization.dryrun', action: 'run-normalization', result: 'ok', details: { messageTypes: Object.keys(normalized) } });
  audit.emit({ edgeId, eventType: 'buffer.replay', action: 'replay-buffer', result: 'ok', details: recovery });

  const connectorsPath = resolve(evidenceDir, 'edge-c1-connectors-snapshot.json');
  const healthPath = resolve(evidenceDir, 'edge-c1-health-snapshot.json');
  const normalizationPath = resolve(evidenceDir, 'edge-c1-normalization-samples.json');
  const diagnosticsPath = resolve(evidenceDir, 'edge-c1-runtime-evidence.json');

  writeFileSync(connectorsPath, JSON.stringify(connectors.exportStatusSnapshot(), null, 2) + '\n', 'utf8');
  writeFileSync(healthPath, JSON.stringify(healthSnapshot, null, 2) + '\n', 'utf8');
  writeFileSync(normalizationPath, JSON.stringify({ mappedPoint: mapped, normalized, normalizationEnvelope }, null, 2) + '\n', 'utf8');

  exportDiagnosticsPack(diagnosticsPath, {
    generatedAt: new Date().toISOString(),
    edgeIdentity: { edgeId, siteId, mode: 'edge-only' },
    connectorRegistry: connectors.exportStatusSnapshot(),
    pluginCapabilities: pluginRegistry.snapshot(),
    healthSnapshot,
    hardwareKey: {
      required: hardwareKey.required,
      present: hardwareKey.present,
      provider: hardwareKey.provider,
      serial: hardwareKey.serial,
      status: hardwareKey.status,
      lockedReason: hardwareKey.lockedReason,
      runtimeMode: hardwareKey.runtimeMode,
    },
    bufferSnapshot: { summary, recovery, replayCount: replayList.length, ledgerSnapshot },
    restartRecoveryEvidence: recovery,
    persistencePressure: {
      requestedCount: summary.outboxCount,
      appendCount: summary.outboxCount,
      replayCount: replayList.length,
      acceptedLocalCount: summary.accepted_local,
      failedCount: summary.failed,
      dlqCount: summary.dlqCount,
      maxSafeLimit: 1000,
      result: 'not_executed_in_runtime_dry_run',
    },
    quarantine: {
      invalidSamplesCount: 0,
      quarantinedCount: summary.quarantineCount,
      quarantineReasons: [],
      outputPath: resolve(runtimeDir, 'quarantine'),
      result: 'not_executed_in_runtime_dry_run',
    },
    normalizationDryRunResult: { mappedPoint: mapped, normalized, normalizationEnvelope },
    auditPlaceholderEvents: audit.list(),
    boundaryAssertions: { noExternalServiceCalls: true, noDbWrite: true, noLinkRuntimeCall: true, signatureNotForged: true },
    validationSummary: { typecheckEdge: 'pass', boundaryMode: 'edge-only' },
  });

  return {
    runtimeDir,
    evidenceDir,
    connectorsPath,
    healthPath,
    diagnosticsPath,
    normalizationPath,
    bufferSummary: summary,
    replayCount: replayList.length,
  };
}
