import { existsSync, readFileSync } from 'node:fs';
import { basename, resolve } from 'node:path';

import { runEdgeC1RuntimeEvidenceFlow } from './c1-runtime-foundation.js';

type CliCommand =
  | 'health'
  | 'ready'
  | 'identity'
  | 'outbox'
  | 'diagnostics'
  | 'package-integrity'
  | 'connectors'
  | 'plugins'
  | 'connector-poll-once'
  | 'normalize-once'
  | 'envelope-once'
  | 'pipeline-once'
  | 'buffer-ingest-once'
  | 'buffer-status'
  | 'buffer-list'
  | 'buffer-ack-dry-run'
  | 'buffer-fail-dry-run'
  | 'delivery-preview'
  | 'delivery-cursor'
  | 'delivery-mark-pending-dry-run'
  | 'delivery-mark-failed-dry-run'
  | 'delivery-mark-ack-dry-run'
  | 'audit-status'
  | 'audit-list'
  | 'audit-chain'
  | 'audit-integrity'
  | 'file-import-dry-run'
  | 'file-import-pipeline-once'
  | 'http-polling-dry-run'
  | 'http-polling-pipeline-once'
  | 'snmp-readonly-dry-run'
  | 'snmp-readonly-pipeline-once'
  | 'modbus-tcp-readonly-dry-run'
  | 'modbus-tcp-readonly-pipeline-once'
  | 'bacnet-ip-readonly-dry-run'
  | 'bacnet-ip-readonly-pipeline-once'
  | 'opc-ua-readonly-dry-run'
  | 'opc-ua-readonly-pipeline-once'
  | 'summary';

interface MinimalHealthLike {
  readonly status?: string;
  readonly runtimeMode?: string;
  readonly edgeId?: string;
  readonly siteId?: string;
  readonly hardwareKey?: {
    readonly required?: boolean;
    readonly status?: string;
    readonly provider?: string;
    readonly serial?: string;
    readonly present?: boolean;
  };
  readonly lockedReason?: string | null;
  readonly bufferPendingCount?: number;
  readonly bufferFailedCount?: number;
  readonly dlqCount?: number;
  readonly lastGeneratedAt?: string;
}

interface MinimalDiagnosticsLike {
  readonly generatedAt?: string;
  readonly edgeIdentity?: {
    readonly edgeId?: string;
    readonly siteId?: string;
  };
  readonly healthSnapshot?: MinimalHealthLike;
  readonly hardwareKey?: {
    readonly required?: boolean;
    readonly status?: string;
    readonly provider?: string;
    readonly serial?: string;
    readonly present?: boolean;
    readonly runtimeMode?: string;
    readonly lockedReason?: string | null;
  };
  readonly bufferSnapshot?: {
    readonly summary?: {
      readonly pending?: number;
      readonly failed?: number;
      readonly dlqCount?: number;
      readonly quarantineCount?: number;
    };
  };
  readonly quarantine?: {
    readonly quarantinedCount?: number;
  };
}

interface CliState {
  readonly edgeRoot: string;
  readonly healthPath: string;
  readonly diagnosticsPath: string;
  readonly connectorRegistryEvidencePath: string;
  readonly connectorHealthEvidencePath: string;
  readonly protocolPluginEvidencePath: string;
  readonly normalizationEnvelopeEvidencePath: string;
  readonly normalizedSampleSnapshotPath: string;
  readonly edgeEnvelopeSnapshotPath: string;
  readonly localBufferEvidencePath: string;
  readonly localBufferStatsPath: string;
  readonly localBufferLedgerPath: string;
  readonly localDeliveryEvidencePath: string;
  readonly localDeliveryBatchPreviewPath: string;
  readonly localDeliveryCursorPath: string;
  readonly deliveryAuditEvidencePath: string;
  readonly deliveryAuditIntegrityPath: string;
  readonly deliveryAuditLedgerPath: string;
  readonly fileImportEvidencePath: string;
  readonly fileImportParsePath: string;
  readonly fileImportPipelineSummaryPath: string;
  readonly httpPollingEvidencePath: string;
  readonly httpPollingParsePath: string;
  readonly httpPollingPipelineSummaryPath: string;
  readonly snmpReadonlyEvidencePath: string;
  readonly snmpReadonlyParsePath: string;
  readonly snmpReadonlyPipelineSummaryPath: string;
  readonly modbusReadonlyEvidencePath: string;
  readonly modbusReadonlyParsePath: string;
  readonly modbusReadonlyPipelineSummaryPath: string;
  readonly bacnetReadonlyEvidencePath: string;
  readonly bacnetReadonlyParsePath: string;
  readonly bacnetReadonlyPipelineSummaryPath: string;
  readonly opcUaReadonlyEvidencePath: string;
  readonly opcUaReadonlyParsePath: string;
  readonly opcUaReadonlyPipelineSummaryPath: string;
  readonly health: MinimalHealthLike;
  readonly diagnostics: MinimalDiagnosticsLike;
}

function parseJson<T>(path: string): T | null {
  if (!existsSync(path)) return null;
  return JSON.parse(readFileSync(path, 'utf8')) as T;
}

function deriveEdgeRootFromScriptPath(): string | null {
  const scriptPath = resolve(process.argv[1] ?? '');
  const marker = '/AN_VANTARIS_EDGE/';
  const markerIndex = scriptPath.indexOf(marker);
  if (markerIndex < 0) return null;
  return scriptPath.slice(0, markerIndex + '/AN_VANTARIS_EDGE'.length);
}

function resolveEdgeRoot(): string {
  const envRoot = process.env.EDGE_ROOT;
  if (envRoot) return resolve(envRoot);

  const cwd = resolve(process.cwd());
  if (basename(cwd) == 'AN_VANTARIS_EDGE') return cwd;
  if (existsSync(resolve(cwd, 'AN_VANTARIS_EDGE/src/runtime'))) return resolve(cwd, 'AN_VANTARIS_EDGE');

  const scriptRoot = deriveEdgeRootFromScriptPath();
  if (scriptRoot) return scriptRoot;

  return resolve(cwd, 'AN_VANTARIS_EDGE');
}

function edgeIdentity(state: CliState): { edgeId: string; siteId: string; zoneId: string; sourceSystemId: string } {
  const edgeId = state.health.edgeId ?? state.diagnostics.edgeIdentity?.edgeId ?? process.env.EDGE_ID ?? 'edge-c1-dryrun-001';
  const siteId = state.health.siteId ?? state.diagnostics.edgeIdentity?.siteId ?? process.env.SITE_ID ?? 'site-001';
  const zoneId = process.env.ZONE_ID ?? 'zone-not-set';
  const sourceSystemId = process.env.SOURCE_SYSTEM_ID ?? 'source-system-not-set';
  return { edgeId, siteId, zoneId, sourceSystemId };
}

function outboxSummary(state: CliState): { pending: number; failed: number; dlq: number; quarantine: number } {
  const pending = state.health.bufferPendingCount ?? state.diagnostics.bufferSnapshot?.summary?.pending ?? 0;
  const failed = state.health.bufferFailedCount ?? state.diagnostics.bufferSnapshot?.summary?.failed ?? 0;
  const dlq = state.health.dlqCount ?? state.diagnostics.bufferSnapshot?.summary?.dlqCount ?? 0;
  const quarantine =
    state.diagnostics.quarantine?.quarantinedCount ?? state.diagnostics.bufferSnapshot?.summary?.quarantineCount ?? 0;
  return { pending, failed, dlq, quarantine };
}

function runtimeMode(state: CliState): string {
  return state.health.runtimeMode ?? state.diagnostics.hardwareKey?.runtimeMode ?? process.env.EDGE_RUNTIME_MODE ?? 'production';
}

function status(state: CliState): string {
  return state.health.status ?? 'unknown';
}

function lockedReason(state: CliState): string | null {
  return state.health.lockedReason ?? state.diagnostics.hardwareKey?.lockedReason ?? null;
}

function hardwareKey(state: CliState): {
  required: boolean;
  status: string;
  provider: string;
  serial: string;
  present: boolean;
} {
  return {
    required: state.health.hardwareKey?.required ?? state.diagnostics.hardwareKey?.required ?? false,
    status: state.health.hardwareKey?.status ?? state.diagnostics.hardwareKey?.status ?? 'unknown',
    provider: state.health.hardwareKey?.provider ?? state.diagnostics.hardwareKey?.provider ?? 'not-set',
    serial: state.health.hardwareKey?.serial ?? state.diagnostics.hardwareKey?.serial ?? 'not-set',
    present: state.health.hardwareKey?.present ?? state.diagnostics.hardwareKey?.present ?? false,
  };
}

function packageIntegrityStatus(edgeRoot: string): 'pass' | 'missing_files' {
  const required = [
    'deploy/offline-bundle/MANIFEST.edge.json',
    'deploy/offline-bundle/PACKAGE_INTEGRITY.edge.md',
    'deploy/offline-bundle/SHA256SUMS.edge.template',
    'deploy/offline-bundle/install-evidence-template.edge.json',
    'deploy/offline-bundle/PRODUCTION_EXCLUDE.edge.txt',
  ];
  const missing = required.filter((path) => !existsSync(resolve(edgeRoot, path)));
  return missing.length == 0 ? 'pass' : 'missing_files';
}

function ensureLocalEvidence(edgeRoot: string): CliState {
  const healthPath = resolve(edgeRoot, '.runtime/evidence/edge-c1-health-snapshot.json');
  const diagnosticsPath = resolve(edgeRoot, '.runtime/evidence/edge-c1-runtime-evidence.json');
  const connectorRegistryEvidencePath = resolve(edgeRoot, '.runtime/evidence/edge-c2-connector-registry-evidence.json');
  const connectorHealthEvidencePath = resolve(edgeRoot, '.runtime/evidence/edge-c2-connector-health-snapshot.json');
  const protocolPluginEvidencePath = resolve(edgeRoot, '.runtime/evidence/edge-c2-protocol-plugin-runtime-evidence.json');
  const normalizationEnvelopeEvidencePath = resolve(
    edgeRoot,
    '.runtime/evidence/edge-c2-normalization-envelope-evidence.json',
  );
  const normalizedSampleSnapshotPath = resolve(edgeRoot, '.runtime/evidence/edge-c2-normalized-sample-snapshot.json');
  const edgeEnvelopeSnapshotPath = resolve(edgeRoot, '.runtime/evidence/edge-c2-edge-envelope-snapshot.json');
  const localBufferEvidencePath = resolve(edgeRoot, '.runtime/evidence/edge-c2-local-buffer-staging-evidence.json');
  const localBufferStatsPath = resolve(edgeRoot, '.runtime/evidence/edge-c2-local-buffer-stats.json');
  const localBufferLedgerPath = resolve(edgeRoot, '.runtime/buffer/edge-envelope-buffer.jsonl');
  const localDeliveryEvidencePath = resolve(edgeRoot, '.runtime/evidence/edge-c2-local-delivery-orchestrator-evidence.json');
  const localDeliveryBatchPreviewPath = resolve(edgeRoot, '.runtime/evidence/edge-c2-local-delivery-batch-preview.json');
  const localDeliveryCursorPath = resolve(edgeRoot, '.runtime/evidence/edge-c2-local-delivery-cursor.json');
  const deliveryAuditEvidencePath = resolve(edgeRoot, '.runtime/evidence/edge-c2-delivery-audit-chain-evidence.json');
  const deliveryAuditIntegrityPath = resolve(edgeRoot, '.runtime/evidence/edge-c2-delivery-audit-integrity-summary.json');
  const deliveryAuditLedgerPath = resolve(edgeRoot, '.runtime/audit/edge-delivery-audit-ledger.jsonl');
  const fileImportEvidencePath = resolve(edgeRoot, '.runtime/evidence/edge-c3-file-import-connector-evidence.json');
  const fileImportParsePath = resolve(edgeRoot, '.runtime/evidence/edge-c3-file-import-sample-parse.json');
  const fileImportPipelineSummaryPath = resolve(edgeRoot, '.runtime/evidence/edge-c3-file-import-pipeline-summary.json');
  const httpPollingEvidencePath = resolve(edgeRoot, '.runtime/evidence/edge-c3-http-polling-connector-evidence.json');
  const httpPollingParsePath = resolve(edgeRoot, '.runtime/evidence/edge-c3-http-polling-fixture-parse.json');
  const httpPollingPipelineSummaryPath = resolve(edgeRoot, '.runtime/evidence/edge-c3-http-polling-pipeline-summary.json');
  const snmpReadonlyEvidencePath = resolve(edgeRoot, '.runtime/evidence/edge-c3-snmp-readonly-connector-evidence.json');
  const snmpReadonlyParsePath = resolve(edgeRoot, '.runtime/evidence/edge-c3-snmp-readonly-fixture-parse.json');
  const snmpReadonlyPipelineSummaryPath = resolve(edgeRoot, '.runtime/evidence/edge-c3-snmp-readonly-pipeline-summary.json');
  const modbusReadonlyEvidencePath = resolve(edgeRoot, '.runtime/evidence/edge-c3-modbus-tcp-readonly-connector-evidence.json');
  const modbusReadonlyParsePath = resolve(edgeRoot, '.runtime/evidence/edge-c3-modbus-tcp-readonly-fixture-parse.json');
  const modbusReadonlyPipelineSummaryPath = resolve(
    edgeRoot,
    '.runtime/evidence/edge-c3-modbus-tcp-readonly-pipeline-summary.json',
  );
  const bacnetReadonlyEvidencePath = resolve(edgeRoot, '.runtime/evidence/edge-c3-bacnet-ip-readonly-connector-evidence.json');
  const bacnetReadonlyParsePath = resolve(edgeRoot, '.runtime/evidence/edge-c3-bacnet-ip-readonly-fixture-parse.json');
  const bacnetReadonlyPipelineSummaryPath = resolve(edgeRoot, '.runtime/evidence/edge-c3-bacnet-ip-readonly-pipeline-summary.json');
  const opcUaReadonlyEvidencePath = resolve(edgeRoot, '.runtime/evidence/edge-c3-opc-ua-readonly-connector-evidence.json');
  const opcUaReadonlyParsePath = resolve(edgeRoot, '.runtime/evidence/edge-c3-opc-ua-readonly-fixture-parse.json');
  const opcUaReadonlyPipelineSummaryPath = resolve(edgeRoot, '.runtime/evidence/edge-c3-opc-ua-readonly-pipeline-summary.json');

  let health = parseJson<MinimalHealthLike>(healthPath);
  let diagnostics = parseJson<MinimalDiagnosticsLike>(diagnosticsPath);

  if (!health || !diagnostics) {
    runEdgeC1RuntimeEvidenceFlow({
      edgeRoot,
      evidenceDir: resolve(edgeRoot, '.runtime/evidence'),
    });
    health = parseJson<MinimalHealthLike>(healthPath) ?? {};
    diagnostics = parseJson<MinimalDiagnosticsLike>(diagnosticsPath) ?? {};
  }

  return {
    edgeRoot,
    healthPath,
    diagnosticsPath,
    connectorRegistryEvidencePath,
    connectorHealthEvidencePath,
    protocolPluginEvidencePath,
    normalizationEnvelopeEvidencePath,
    normalizedSampleSnapshotPath,
    edgeEnvelopeSnapshotPath,
    localBufferEvidencePath,
    localBufferStatsPath,
    localBufferLedgerPath,
    localDeliveryEvidencePath,
    localDeliveryBatchPreviewPath,
    localDeliveryCursorPath,
    deliveryAuditEvidencePath,
    deliveryAuditIntegrityPath,
    deliveryAuditLedgerPath,
    fileImportEvidencePath,
    fileImportParsePath,
    fileImportPipelineSummaryPath,
    httpPollingEvidencePath,
    httpPollingParsePath,
    httpPollingPipelineSummaryPath,
    snmpReadonlyEvidencePath,
    snmpReadonlyParsePath,
    snmpReadonlyPipelineSummaryPath,
    modbusReadonlyEvidencePath,
    modbusReadonlyParsePath,
    modbusReadonlyPipelineSummaryPath,
    bacnetReadonlyEvidencePath,
    bacnetReadonlyParsePath,
    bacnetReadonlyPipelineSummaryPath,
    opcUaReadonlyEvidencePath,
    opcUaReadonlyParsePath,
    opcUaReadonlyPipelineSummaryPath,
    health: health ?? {},
    diagnostics: diagnostics ?? {},
  };
}

function connectorSummary(state: CliState): {
  connectorCount: number;
  runningCount: number;
  disabledCount: number;
  failedCount: number;
  quarantineCount: number;
  protocols: readonly string[];
  evidencePath: string | null;
} {
  const fromHealth = parseJson<{
    connectorCount?: number;
    runningCount?: number;
    disabledCount?: number;
    failedCount?: number;
    quarantineCount?: number;
    protocols?: readonly string[];
  }>(state.connectorHealthEvidencePath);

  if (fromHealth) {
    return {
      connectorCount: fromHealth.connectorCount ?? 0,
      runningCount: fromHealth.runningCount ?? 0,
      disabledCount: fromHealth.disabledCount ?? 0,
      failedCount: fromHealth.failedCount ?? 0,
      quarantineCount: fromHealth.quarantineCount ?? 0,
      protocols: fromHealth.protocols ?? [],
      evidencePath: state.connectorHealthEvidencePath,
    };
  }

  return {
    connectorCount: 0,
    runningCount: 0,
    disabledCount: 0,
    failedCount: 0,
    quarantineCount: 0,
    protocols: [],
    evidencePath: null,
  };
}

function protocolPluginSummary(state: CliState): {
  pluginCount: number;
  protocols: readonly string[];
  registeredPluginIds: readonly string[];
  compatibilityChecked: number;
  compatibleCount: number;
  generatedAt: string | null;
  evidencePath: string | null;
} {
  const evidence = parseJson<{
    pluginRegistry?: {
      pluginCount?: number;
      protocols?: readonly string[];
      plugins?: ReadonlyArray<{ pluginId?: string }>;
      generatedAt?: string;
    };
    compatibilityChecks?: readonly { compatible?: boolean }[];
  }>(state.protocolPluginEvidencePath);

  if (!evidence?.pluginRegistry) {
    return {
      pluginCount: 0,
      protocols: [],
      registeredPluginIds: [],
      compatibilityChecked: 0,
      compatibleCount: 0,
      generatedAt: null,
      evidencePath: null,
    };
  }

  const compatibilityChecks = evidence.compatibilityChecks ?? [];
  return {
    pluginCount: evidence.pluginRegistry.pluginCount ?? 0,
    protocols: evidence.pluginRegistry.protocols ?? [],
    registeredPluginIds: (evidence.pluginRegistry.plugins ?? []).map((item) => item.pluginId ?? 'unknown'),
    compatibilityChecked: compatibilityChecks.length,
    compatibleCount: compatibilityChecks.filter((item) => item.compatible).length,
    generatedAt: evidence.pluginRegistry.generatedAt ?? null,
    evidencePath: state.protocolPluginEvidencePath,
  };
}

function localPollOnceSnapshot(state: CliState, connectorIdArg: string | undefined): {
  connectorId: string;
  sampleCount: number;
  protocol: string;
  sample: Record<string, unknown>;
  evidencePath: string | null;
} {
  const connectorId = connectorIdArg ?? 'connector-simulator-example-01';
  const evidence = parseJson<{
    pollResult?: {
      connectorId?: string;
      protocol?: string;
      samples?: readonly Record<string, unknown>[];
    };
  }>(state.protocolPluginEvidencePath);

  if (evidence?.pollResult && evidence.pollResult.connectorId == connectorId) {
    const samples = evidence.pollResult.samples ?? [];
    return {
      connectorId,
      sampleCount: samples.length,
      protocol: evidence.pollResult.protocol ?? 'simulator',
      sample: (samples[0] ?? {}) as Record<string, unknown>,
      evidencePath: state.protocolPluginEvidencePath,
    };
  }

  return {
    connectorId,
    sampleCount: 1,
    protocol: 'simulator',
    sample: {
      sampleId: `${connectorId}-synthetic-fallback`,
      synthetic: true,
      value: 21,
      quality: 'good',
      generatedAt: new Date().toISOString(),
    },
    evidencePath: null,
  };
}

function normalizationSummary(state: CliState): {
  normalizedPointCount: number;
  normalizedEventCount: number;
  warningCount: number;
  errorCount: number;
  generatedAt: string | null;
  evidencePath: string | null;
} {
  const evidence = parseJson<{
    pipelineSummary?: {
      normalizedPointCount?: number;
      normalizedEventCount?: number;
      normalizationWarningCount?: number;
      normalizationErrorCount?: number;
    };
    generatedAt?: string;
  }>(state.normalizationEnvelopeEvidencePath);
  if (!evidence?.pipelineSummary) {
    return {
      normalizedPointCount: 0,
      normalizedEventCount: 0,
      warningCount: 0,
      errorCount: 0,
      generatedAt: null,
      evidencePath: null,
    };
  }
  return {
    normalizedPointCount: evidence.pipelineSummary.normalizedPointCount ?? 0,
    normalizedEventCount: evidence.pipelineSummary.normalizedEventCount ?? 0,
    warningCount: evidence.pipelineSummary.normalizationWarningCount ?? 0,
    errorCount: evidence.pipelineSummary.normalizationErrorCount ?? 0,
    generatedAt: evidence.generatedAt ?? null,
    evidencePath: state.normalizedSampleSnapshotPath,
  };
}

function envelopeSummary(state: CliState): {
  envelopeValid: boolean;
  envelopeId: string | null;
  payloadPointCount: number;
  payloadEventCount: number;
  generatedAt: string | null;
  evidencePath: string | null;
} {
  const envelope = parseJson<{
    header?: { envelopeId?: string; createdAt?: string };
    payload?: { points?: readonly unknown[]; events?: readonly unknown[] };
  }>(state.edgeEnvelopeSnapshotPath);
  const evidence = parseJson<{
    envelopeValidation?: { valid?: boolean };
    generatedAt?: string;
  }>(state.normalizationEnvelopeEvidencePath);
  if (!envelope) {
    return {
      envelopeValid: false,
      envelopeId: null,
      payloadPointCount: 0,
      payloadEventCount: 0,
      generatedAt: null,
      evidencePath: null,
    };
  }
  return {
    envelopeValid: evidence?.envelopeValidation?.valid ?? false,
    envelopeId: envelope.header?.envelopeId ?? null,
    payloadPointCount: envelope.payload?.points?.length ?? 0,
    payloadEventCount: envelope.payload?.events?.length ?? 0,
    generatedAt: envelope.header?.createdAt ?? evidence?.generatedAt ?? null,
    evidencePath: state.edgeEnvelopeSnapshotPath,
  };
}

function localBufferSummary(state: CliState): {
  total: number;
  staged: number;
  pending: number;
  failed: number;
  acknowledged: number;
  quarantined: number;
  generatedAt: string | null;
  evidencePath: string | null;
} {
  const stats = parseJson<{
    total?: number;
    staged?: number;
    pending?: number;
    failed?: number;
    acknowledged?: number;
    quarantined?: number;
    generatedAt?: string;
  }>(state.localBufferStatsPath);
  if (!stats) {
    return {
      total: 0,
      staged: 0,
      pending: 0,
      failed: 0,
      acknowledged: 0,
      quarantined: 0,
      generatedAt: null,
      evidencePath: null,
    };
  }
  return {
    total: stats.total ?? 0,
    staged: stats.staged ?? 0,
    pending: stats.pending ?? 0,
    failed: stats.failed ?? 0,
    acknowledged: stats.acknowledged ?? 0,
    quarantined: stats.quarantined ?? 0,
    generatedAt: stats.generatedAt ?? null,
    evidencePath: state.localBufferStatsPath,
  };
}

function localBufferList(state: CliState): {
  count: number;
  records: readonly Record<string, unknown>[];
  ledgerPath: string;
  evidencePath: string | null;
} {
  const evidence = parseJson<{
    records?: readonly Record<string, unknown>[];
  }>(state.localBufferEvidencePath);
  const records = evidence?.records ?? [];
  return {
    count: records.length,
    records: records.slice(-10),
    ledgerPath: state.localBufferLedgerPath,
    evidencePath: evidence ? state.localBufferEvidencePath : null,
  };
}

function localDeliverySummary(state: CliState): {
  selectedRecords: number;
  readyCount: number;
  deferredCount: number;
  exhaustedCount: number;
  skippedCount: number;
  generatedAt: string | null;
  evidencePath: string | null;
} {
  const evidence = parseJson<{
    stats?: {
      selectedRecords?: number;
      readyCount?: number;
      deferredCount?: number;
      exhaustedCount?: number;
      skippedCount?: number;
      generatedAt?: string;
    };
  }>(state.localDeliveryEvidencePath);
  if (!evidence?.stats) {
    return {
      selectedRecords: 0,
      readyCount: 0,
      deferredCount: 0,
      exhaustedCount: 0,
      skippedCount: 0,
      generatedAt: null,
      evidencePath: null,
    };
  }
  return {
    selectedRecords: evidence.stats.selectedRecords ?? 0,
    readyCount: evidence.stats.readyCount ?? 0,
    deferredCount: evidence.stats.deferredCount ?? 0,
    exhaustedCount: evidence.stats.exhaustedCount ?? 0,
    skippedCount: evidence.stats.skippedCount ?? 0,
    generatedAt: evidence.stats.generatedAt ?? null,
    evidencePath: state.localDeliveryEvidencePath,
  };
}

function deliveryAuditSummary(state: CliState): {
  valid: boolean;
  recordCount: number;
  firstHash: string | null;
  lastHash: string | null;
  brokenAtSequence: number | null;
  generatedAt: string | null;
  evidencePath: string | null;
} {
  const integrity = parseJson<{
    valid?: boolean;
    recordCount?: number;
    firstHash?: string | null;
    lastHash?: string | null;
    brokenAtSequence?: number | null;
    generatedAt?: string;
  }>(state.deliveryAuditIntegrityPath);
  if (!integrity) {
    return {
      valid: false,
      recordCount: 0,
      firstHash: null,
      lastHash: null,
      brokenAtSequence: null,
      generatedAt: null,
      evidencePath: null,
    };
  }
  return {
    valid: integrity.valid ?? false,
    recordCount: integrity.recordCount ?? 0,
    firstHash: integrity.firstHash ?? null,
    lastHash: integrity.lastHash ?? null,
    brokenAtSequence: integrity.brokenAtSequence ?? null,
    generatedAt: integrity.generatedAt ?? null,
    evidencePath: state.deliveryAuditIntegrityPath,
  };
}

function fileImportSummary(state: CliState): {
  parseOk: boolean;
  recordsRead: number;
  recordsValid: number;
  recordsInvalid: number;
  sourcePath: string | null;
  generatedAt: string | null;
  evidencePath: string | null;
} {
  const parse = parseJson<{
    parseResult?: {
      ok?: boolean;
      sourcePath?: string;
      records?: readonly unknown[];
      validationErrors?: readonly unknown[];
    };
    stats?: {
      recordsRead?: number;
      recordsValid?: number;
      recordsInvalid?: number;
      generatedAt?: string;
    };
    generatedAt?: string;
  }>(state.fileImportEvidencePath);
  if (!parse) {
    return {
      parseOk: false,
      recordsRead: 0,
      recordsValid: 0,
      recordsInvalid: 0,
      sourcePath: null,
      generatedAt: null,
      evidencePath: null,
    };
  }
  return {
    parseOk: parse.parseResult?.ok ?? false,
    recordsRead: parse.stats?.recordsRead ?? parse.parseResult?.records?.length ?? 0,
    recordsValid: parse.stats?.recordsValid ?? parse.parseResult?.records?.length ?? 0,
    recordsInvalid: parse.stats?.recordsInvalid ?? parse.parseResult?.validationErrors?.length ?? 0,
    sourcePath: parse.parseResult?.sourcePath ?? null,
    generatedAt: parse.stats?.generatedAt ?? parse.generatedAt ?? null,
    evidencePath: state.fileImportEvidencePath,
  };
}

function httpPollingSummary(state: CliState): {
  connectorId: string | null;
  protocol: string | null;
  networkEnabled: boolean;
  sampleCount: number;
  validationSummary: { valid: boolean; errorCount: number };
  evidencePath: string | null;
} {
  const evidence = parseJson<{
    config?: {
      connectorId?: string;
      networkEnabled?: boolean;
    };
    validation?: {
      valid?: boolean;
      errors?: readonly unknown[];
    };
    parse?: {
      records?: readonly unknown[];
    };
    pipelineSummary?: {
      pollResult?: {
        protocol?: string;
        sampleCount?: number;
      };
    };
  }>(state.httpPollingEvidencePath);
  if (!evidence) {
    return {
      connectorId: null,
      protocol: null,
      networkEnabled: false,
      sampleCount: 0,
      validationSummary: { valid: false, errorCount: 0 },
      evidencePath: null,
    };
  }
  return {
    connectorId: evidence.config?.connectorId ?? null,
    protocol: evidence.pipelineSummary?.pollResult?.protocol ?? 'http',
    networkEnabled: evidence.config?.networkEnabled ?? false,
    sampleCount: evidence.pipelineSummary?.pollResult?.sampleCount ?? evidence.parse?.records?.length ?? 0,
    validationSummary: {
      valid: evidence.validation?.valid ?? false,
      errorCount: evidence.validation?.errors?.length ?? 0,
    },
    evidencePath: state.httpPollingEvidencePath,
  };
}

function snmpReadonlySummary(state: CliState): {
  connectorId: string | null;
  protocol: string;
  networkEnabled: boolean;
  supportsWriteback: boolean;
  varbindCount: number;
  sampleCount: number;
  validationSummary: { valid: boolean; errorCount: number };
  evidencePath: string | null;
} {
  const evidence = parseJson<{
    config?: {
      connectorId?: string;
      networkEnabled?: boolean;
      supportsWriteback?: boolean;
    };
    validation?: {
      valid?: boolean;
      errors?: readonly unknown[];
    };
    parse?: {
      varbinds?: readonly unknown[];
    };
    pipelineSummary?: {
      pollResult?: {
        sampleCount?: number;
      };
    };
  }>(state.snmpReadonlyEvidencePath);
  if (!evidence) {
    return {
      connectorId: null,
      protocol: 'snmp',
      networkEnabled: false,
      supportsWriteback: false,
      varbindCount: 0,
      sampleCount: 0,
      validationSummary: { valid: false, errorCount: 0 },
      evidencePath: null,
    };
  }
  return {
    connectorId: evidence.config?.connectorId ?? null,
    protocol: 'snmp',
    networkEnabled: evidence.config?.networkEnabled ?? false,
    supportsWriteback: evidence.config?.supportsWriteback ?? false,
    varbindCount: evidence.parse?.varbinds?.length ?? 0,
    sampleCount: evidence.pipelineSummary?.pollResult?.sampleCount ?? 0,
    validationSummary: {
      valid: evidence.validation?.valid ?? false,
      errorCount: evidence.validation?.errors?.length ?? 0,
    },
    evidencePath: state.snmpReadonlyEvidencePath,
  };
}

function modbusReadonlySummary(state: CliState): {
  connectorId: string | null;
  protocol: string;
  networkEnabled: boolean;
  supportsWriteback: boolean;
  unitId: number | null;
  registerCount: number;
  sampleCount: number;
  validationSummary: { valid: boolean; errorCount: number };
  evidencePath: string | null;
} {
  const evidence = parseJson<{
    config?: {
      connectorId?: string;
      networkEnabled?: boolean;
      supportsWriteback?: boolean;
      unitId?: number;
    };
    validation?: {
      valid?: boolean;
      errors?: readonly unknown[];
    };
    parse?: {
      registers?: readonly unknown[];
    };
    pipelineSummary?: {
      pollResult?: {
        sampleCount?: number;
      };
    };
  }>(state.modbusReadonlyEvidencePath);
  if (!evidence) {
    return {
      connectorId: null,
      protocol: 'modbus',
      networkEnabled: false,
      supportsWriteback: false,
      unitId: null,
      registerCount: 0,
      sampleCount: 0,
      validationSummary: { valid: false, errorCount: 0 },
      evidencePath: null,
    };
  }
  return {
    connectorId: evidence.config?.connectorId ?? null,
    protocol: 'modbus',
    networkEnabled: evidence.config?.networkEnabled ?? false,
    supportsWriteback: evidence.config?.supportsWriteback ?? false,
    unitId: evidence.config?.unitId ?? null,
    registerCount: evidence.parse?.registers?.length ?? 0,
    sampleCount: evidence.pipelineSummary?.pollResult?.sampleCount ?? 0,
    validationSummary: {
      valid: evidence.validation?.valid ?? false,
      errorCount: evidence.validation?.errors?.length ?? 0,
    },
    evidencePath: state.modbusReadonlyEvidencePath,
  };
}

function bacnetReadonlySummary(state: CliState): {
  connectorId: string | null;
  protocol: string;
  networkEnabled: boolean;
  supportsWriteback: boolean;
  pointCount: number;
  sampleCount: number;
  validationSummary: { valid: boolean; errorCount: number };
  evidencePath: string | null;
} {
  const evidence = parseJson<{
    config?: {
      connectorId?: string;
      networkEnabled?: boolean;
      supportsWriteback?: boolean;
    };
    validation?: {
      valid?: boolean;
      errors?: readonly unknown[];
    };
    parse?: {
      points?: readonly unknown[];
    };
    pipelineSummary?: {
      pollResult?: {
        sampleCount?: number;
      };
    };
  }>(state.bacnetReadonlyEvidencePath);
  if (!evidence) {
    return {
      connectorId: null,
      protocol: 'bacnet-ip-readonly',
      networkEnabled: false,
      supportsWriteback: false,
      pointCount: 0,
      sampleCount: 0,
      validationSummary: { valid: false, errorCount: 0 },
      evidencePath: null,
    };
  }
  return {
    connectorId: evidence.config?.connectorId ?? null,
    protocol: 'bacnet-ip-readonly',
    networkEnabled: evidence.config?.networkEnabled ?? false,
    supportsWriteback: evidence.config?.supportsWriteback ?? false,
    pointCount: evidence.parse?.points?.length ?? 0,
    sampleCount: evidence.pipelineSummary?.pollResult?.sampleCount ?? 0,
    validationSummary: {
      valid: evidence.validation?.valid ?? false,
      errorCount: evidence.validation?.errors?.length ?? 0,
    },
    evidencePath: state.bacnetReadonlyEvidencePath,
  };
}

function opcUaReadonlySummary(state: CliState): {
  connectorId: string | null;
  protocol: string;
  networkEnabled: boolean;
  supportsWriteback: boolean;
  nodeCount: number;
  sampleCount: number;
  validationSummary: { valid: boolean; errorCount: number };
  evidencePath: string | null;
} {
  const evidence = parseJson<{
    config?: {
      connectorId?: string;
      networkEnabled?: boolean;
      supportsWriteback?: boolean;
    };
    validation?: {
      valid?: boolean;
      errors?: readonly unknown[];
    };
    parse?: {
      nodes?: readonly unknown[];
    };
    pipelineSummary?: {
      pollResult?: {
        sampleCount?: number;
      };
    };
  }>(state.opcUaReadonlyEvidencePath);
  if (!evidence) {
    return {
      connectorId: null,
      protocol: 'opc-ua-readonly',
      networkEnabled: false,
      supportsWriteback: false,
      nodeCount: 0,
      sampleCount: 0,
      validationSummary: { valid: false, errorCount: 0 },
      evidencePath: null,
    };
  }
  return {
    connectorId: evidence.config?.connectorId ?? null,
    protocol: 'opc-ua-readonly',
    networkEnabled: evidence.config?.networkEnabled ?? false,
    supportsWriteback: evidence.config?.supportsWriteback ?? false,
    nodeCount: evidence.parse?.nodes?.length ?? 0,
    sampleCount: evidence.pipelineSummary?.pollResult?.sampleCount ?? 0,
    validationSummary: {
      valid: evidence.validation?.valid ?? false,
      errorCount: evidence.validation?.errors?.length ?? 0,
    },
    evidencePath: state.opcUaReadonlyEvidencePath,
  };
}

function buildBase(state: CliState): {
  status: string;
  ready: boolean;
  runtimeMode: string;
  edgeId: string;
  siteId: string;
  zoneId: string;
  sourceSystemId: string;
  hardwareKey: ReturnType<typeof hardwareKey>;
  lockedReason: string | null;
  outbox: { pending: number; failed: number; dlq: number };
  quarantine: { count: number };
  diagnosticsEvidencePath: string;
  packageIntegrityStatus: 'pass' | 'missing_files';
  generatedAt: string;
} {
  const identity = edgeIdentity(state);
  const queue = outboxSummary(state);
  const currentStatus = status(state);
  return {
    status: currentStatus,
    ready: currentStatus != 'locked' && currentStatus != 'failed' && currentStatus != 'unknown',
    runtimeMode: runtimeMode(state),
    edgeId: identity.edgeId,
    siteId: identity.siteId,
    zoneId: identity.zoneId,
    sourceSystemId: identity.sourceSystemId,
    hardwareKey: hardwareKey(state),
    lockedReason: lockedReason(state),
    outbox: {
      pending: queue.pending,
      failed: queue.failed,
      dlq: queue.dlq,
    },
    quarantine: {
      count: queue.quarantine,
    },
    diagnosticsEvidencePath: state.diagnosticsPath,
    packageIntegrityStatus: packageIntegrityStatus(state.edgeRoot),
    generatedAt: new Date().toISOString(),
  };
}

function commandPayload(command: CliCommand, state: CliState, connectorIdArg?: string): Record<string, unknown> {
  const base = buildBase(state);
  if (command == 'health') {
    return {
      command,
      ...base,
      healthSnapshotPath: state.healthPath,
    };
  }
  if (command == 'ready') {
    return {
      command,
      ...base,
      readinessReason: base.ready ? 'local_checks_passed' : base.lockedReason ?? 'status_not_ready',
    };
  }
  if (command == 'identity') {
    return {
      command,
      ...base,
    };
  }
  if (command == 'outbox') {
    return {
      command,
      ...base,
      outboxPendingPath: resolve(state.edgeRoot, '.runtime/outbox/messages.jsonl'),
      quarantinePath: resolve(state.edgeRoot, '.runtime/quarantine'),
    };
  }
  if (command == 'diagnostics') {
    const connectors = connectorSummary(state);
    const plugins = protocolPluginSummary(state);
    const normalization = normalizationSummary(state);
    const envelope = envelopeSummary(state);
    const buffer = localBufferSummary(state);
    const delivery = localDeliverySummary(state);
    const audit = deliveryAuditSummary(state);
    const fileImport = fileImportSummary(state);
    const httpPolling = httpPollingSummary(state);
    const snmpReadonly = snmpReadonlySummary(state);
    const modbusReadonly = modbusReadonlySummary(state);
    const bacnetReadonly = bacnetReadonlySummary(state);
    const opcUaReadonly = opcUaReadonlySummary(state);
    return {
      command,
      ...base,
      diagnosticsGeneratedAt: state.diagnostics.generatedAt ?? null,
      diagnosticsHealthEmbedded: state.diagnostics.healthSnapshot != null,
      connectorSummary: connectors,
      pluginRegistrySummary: plugins,
      normalizationSummary: normalization,
      envelopeSummary: envelope,
      localBufferSummary: buffer,
      localDeliverySummary: delivery,
      deliveryAuditSummary: audit,
      fileImportSummary: fileImport,
      httpPollingSummary: httpPolling,
      snmpReadonlySummary: snmpReadonly,
      modbusReadonlySummary: modbusReadonly,
      bacnetReadonlySummary: bacnetReadonly,
      opcUaReadonlySummary: opcUaReadonly,
    };
  }
  if (command == 'package-integrity') {
    return {
      command,
      ...base,
      packageIntegrity: {
        status: base.packageIntegrityStatus,
        manifestPath: resolve(state.edgeRoot, 'deploy/offline-bundle/MANIFEST.edge.json'),
      },
    };
  }
  if (command == 'connectors') {
    const connectors = connectorSummary(state);
    return {
      command,
      ...base,
      connectorCount: connectors.connectorCount,
      runningCount: connectors.runningCount,
      disabledCount: connectors.disabledCount,
      failedCount: connectors.failedCount,
      quarantineCount: connectors.quarantineCount,
      protocols: connectors.protocols,
      evidencePath: connectors.evidencePath,
    };
  }
  if (command == 'plugins') {
    const plugins = protocolPluginSummary(state);
    return {
      command,
      ...base,
      ...plugins,
    };
  }
  if (command == 'connector-poll-once') {
    const poll = localPollOnceSnapshot(state, connectorIdArg);
    return {
      command,
      ...base,
      connectorId: poll.connectorId,
      protocol: poll.protocol,
      sampleCount: poll.sampleCount,
      sample: poll.sample,
      evidencePath: poll.evidencePath,
    };
  }
  if (command == 'normalize-once') {
    const normalization = normalizationSummary(state);
    return {
      command,
      ...base,
      ...normalization,
    };
  }
  if (command == 'envelope-once') {
    const envelope = envelopeSummary(state);
    return {
      command,
      ...base,
      ...envelope,
    };
  }
  if (command == 'pipeline-once') {
    const normalization = normalizationSummary(state);
    const envelope = envelopeSummary(state);
    return {
      command,
      ...base,
      normalizationSummary: normalization,
      envelopeSummary: envelope,
      evidencePath: state.normalizationEnvelopeEvidencePath,
    };
  }
  if (command == 'buffer-ingest-once') {
    const buffer = localBufferSummary(state);
    return {
      command,
      ...base,
      ...buffer,
      evidencePath: state.localBufferEvidencePath,
      note: 'local buffer ingestion evidence is produced by c2-04 dry-run script',
    };
  }
  if (command == 'buffer-status') {
    const buffer = localBufferSummary(state);
    return {
      command,
      ...base,
      ...buffer,
    };
  }
  if (command == 'buffer-list') {
    const list = localBufferList(state);
    return {
      command,
      ...base,
      ...list,
    };
  }
  if (command == 'buffer-ack-dry-run') {
    const list = localBufferList(state);
    return {
      command,
      ...base,
      ok: true,
      dryRun: true,
      action: 'acknowledge',
      simulatedRecordId: (list.records.at(-1)?.recordId as string | undefined) ?? null,
      note: 'no mutation performed by CLI command; use validation dry-run script for state transitions',
    };
  }
  if (command == 'buffer-fail-dry-run') {
    const list = localBufferList(state);
    return {
      command,
      ...base,
      ok: true,
      dryRun: true,
      action: 'mark_failed',
      simulatedRecordId: (list.records.at(-1)?.recordId as string | undefined) ?? null,
      note: 'no mutation performed by CLI command; use validation dry-run script for state transitions',
    };
  }
  if (command == 'delivery-preview') {
    const preview = parseJson<Record<string, unknown>>(state.localDeliveryBatchPreviewPath);
    const summary = localDeliverySummary(state);
    return {
      command,
      ...base,
      ...summary,
      preview,
      evidencePath: preview ? state.localDeliveryBatchPreviewPath : null,
    };
  }
  if (command == 'delivery-cursor') {
    const cursor = parseJson<Record<string, unknown>>(state.localDeliveryCursorPath);
    return {
      command,
      ...base,
      cursor,
      evidencePath: cursor ? state.localDeliveryCursorPath : null,
    };
  }
  if (command == 'delivery-mark-pending-dry-run') {
    return {
      command,
      ...base,
      ok: true,
      dryRun: true,
      action: 'delivery_mark_pending',
      note: 'use c2-05 dry-run script for actual local state transitions',
    };
  }
  if (command == 'delivery-mark-failed-dry-run') {
    return {
      command,
      ...base,
      ok: true,
      dryRun: true,
      action: 'delivery_mark_failed',
      note: 'use c2-05 dry-run script for actual local state transitions',
    };
  }
  if (command == 'delivery-mark-ack-dry-run') {
    return {
      command,
      ...base,
      ok: true,
      dryRun: true,
      action: 'delivery_mark_acknowledged',
      note: 'use c2-05 dry-run script for actual local state transitions',
    };
  }
  if (command == 'audit-status' || command == 'audit-integrity') {
    const summary = deliveryAuditSummary(state);
    return {
      command,
      ...base,
      ...summary,
    };
  }
  if (command == 'audit-list') {
    const evidence = parseJson<{ records?: readonly Record<string, unknown>[] }>(state.deliveryAuditEvidencePath);
    const records = evidence?.records ?? [];
    return {
      command,
      ...base,
      count: records.length,
      records: records.slice(-20),
      evidencePath: evidence ? state.deliveryAuditEvidencePath : null,
      ledgerPath: state.deliveryAuditLedgerPath,
    };
  }
  if (command == 'audit-chain') {
    const evidence = parseJson<Record<string, unknown>>(state.deliveryAuditEvidencePath);
    return {
      command,
      ...base,
      chain: evidence,
      evidencePath: evidence ? state.deliveryAuditEvidencePath : null,
      ledgerPath: state.deliveryAuditLedgerPath,
    };
  }
  if (command == 'file-import-dry-run') {
    const summary = fileImportSummary(state);
    const parse = parseJson<Record<string, unknown>>(state.fileImportParsePath);
    return {
      command,
      ...base,
      ...summary,
      parseEvidence: parse,
      parseEvidencePath: parse ? state.fileImportParsePath : null,
    };
  }
  if (command == 'file-import-pipeline-once') {
    const summary = fileImportSummary(state);
    const pipeline = parseJson<Record<string, unknown>>(state.fileImportPipelineSummaryPath);
    return {
      command,
      ...base,
      fileImportSummary: summary,
      pipelineSummary: pipeline,
      pipelineEvidencePath: pipeline ? state.fileImportPipelineSummaryPath : null,
    };
  }
  if (command == 'http-polling-dry-run') {
    const summary = httpPollingSummary(state);
    const parse = parseJson<Record<string, unknown>>(state.httpPollingParsePath);
    return {
      command,
      ...base,
      ...summary,
      parseEvidence: parse,
      parseEvidencePath: parse ? state.httpPollingParsePath : null,
    };
  }
  if (command == 'http-polling-pipeline-once') {
    const summary = httpPollingSummary(state);
    const pipeline = parseJson<Record<string, unknown>>(state.httpPollingPipelineSummaryPath);
    return {
      command,
      ...base,
      ...summary,
      pipelineSummary: pipeline,
      pipelineEvidencePath: pipeline ? state.httpPollingPipelineSummaryPath : null,
    };
  }
  if (command == 'snmp-readonly-dry-run') {
    const summary = snmpReadonlySummary(state);
    const parse = parseJson<Record<string, unknown>>(state.snmpReadonlyParsePath);
    return {
      command,
      ...base,
      ...summary,
      parseEvidence: parse,
      parseEvidencePath: parse ? state.snmpReadonlyParsePath : null,
    };
  }
  if (command == 'snmp-readonly-pipeline-once') {
    const summary = snmpReadonlySummary(state);
    const pipeline = parseJson<Record<string, unknown>>(state.snmpReadonlyPipelineSummaryPath);
    return {
      command,
      ...base,
      ...summary,
      pipelineSummary: pipeline,
      pipelineEvidencePath: pipeline ? state.snmpReadonlyPipelineSummaryPath : null,
    };
  }
  if (command == 'modbus-tcp-readonly-dry-run') {
    const summary = modbusReadonlySummary(state);
    const parse = parseJson<Record<string, unknown>>(state.modbusReadonlyParsePath);
    return {
      command,
      ...base,
      ...summary,
      parseEvidence: parse,
      parseEvidencePath: parse ? state.modbusReadonlyParsePath : null,
    };
  }
  if (command == 'modbus-tcp-readonly-pipeline-once') {
    const summary = modbusReadonlySummary(state);
    const pipeline = parseJson<Record<string, unknown>>(state.modbusReadonlyPipelineSummaryPath);
    return {
      command,
      ...base,
      ...summary,
      pipelineSummary: pipeline,
      pipelineEvidencePath: pipeline ? state.modbusReadonlyPipelineSummaryPath : null,
    };
  }
  if (command == 'bacnet-ip-readonly-dry-run') {
    const summary = bacnetReadonlySummary(state);
    const parse = parseJson<Record<string, unknown>>(state.bacnetReadonlyParsePath);
    return {
      command,
      ...base,
      ...summary,
      parseEvidence: parse,
      parseEvidencePath: parse ? state.bacnetReadonlyParsePath : null,
    };
  }
  if (command == 'bacnet-ip-readonly-pipeline-once') {
    const summary = bacnetReadonlySummary(state);
    const pipeline = parseJson<Record<string, unknown>>(state.bacnetReadonlyPipelineSummaryPath);
    return {
      command,
      ...base,
      ...summary,
      pipelineSummary: pipeline,
      pipelineEvidencePath: pipeline ? state.bacnetReadonlyPipelineSummaryPath : null,
    };
  }
  if (command == 'opc-ua-readonly-dry-run') {
    const summary = opcUaReadonlySummary(state);
    const parse = parseJson<Record<string, unknown>>(state.opcUaReadonlyParsePath);
    return {
      command,
      ...base,
      ...summary,
      parseEvidence: parse,
      parseEvidencePath: parse ? state.opcUaReadonlyParsePath : null,
    };
  }
  if (command == 'opc-ua-readonly-pipeline-once') {
    const summary = opcUaReadonlySummary(state);
    const pipeline = parseJson<Record<string, unknown>>(state.opcUaReadonlyPipelineSummaryPath);
    return {
      command,
      ...base,
      ...summary,
      pipelineSummary: pipeline,
      pipelineEvidencePath: pipeline ? state.opcUaReadonlyPipelineSummaryPath : null,
    };
  }
  return {
    command: 'summary',
    ...base,
  };
}

function parseCommand(raw: string | undefined): CliCommand {
  const command = (raw ?? 'summary').toLowerCase();
  if (
    command == 'health' ||
    command == 'ready' ||
    command == 'identity' ||
    command == 'outbox' ||
    command == 'diagnostics' ||
    command == 'package-integrity' ||
    command == 'connectors' ||
    command == 'plugins' ||
    command == 'connector-poll-once' ||
    command == 'normalize-once' ||
    command == 'envelope-once' ||
    command == 'pipeline-once' ||
    command == 'buffer-ingest-once' ||
    command == 'buffer-status' ||
    command == 'buffer-list' ||
    command == 'buffer-ack-dry-run' ||
    command == 'buffer-fail-dry-run' ||
    command == 'delivery-preview' ||
    command == 'delivery-cursor' ||
    command == 'delivery-mark-pending-dry-run' ||
    command == 'delivery-mark-failed-dry-run' ||
    command == 'delivery-mark-ack-dry-run' ||
    command == 'audit-status' ||
    command == 'audit-list' ||
    command == 'audit-chain' ||
    command == 'audit-integrity' ||
    command == 'file-import-dry-run' ||
    command == 'file-import-pipeline-once' ||
    command == 'http-polling-dry-run' ||
    command == 'http-polling-pipeline-once' ||
    command == 'snmp-readonly-dry-run' ||
    command == 'snmp-readonly-pipeline-once' ||
    command == 'modbus-tcp-readonly-dry-run' ||
    command == 'modbus-tcp-readonly-pipeline-once' ||
    command == 'bacnet-ip-readonly-dry-run' ||
    command == 'bacnet-ip-readonly-pipeline-once' ||
    command == 'opc-ua-readonly-dry-run' ||
    command == 'opc-ua-readonly-pipeline-once' ||
    command == 'summary'
  ) {
    return command;
  }
  throw new Error(`unsupported command: ${raw ?? ''}`);
}

function main(): void {
  try {
    const command = parseCommand(process.argv[2]);
    const connectorIdArg = process.argv[3];
    const edgeRoot = resolveEdgeRoot();
    const state = ensureLocalEvidence(edgeRoot);
    const payload = commandPayload(command, state, connectorIdArg);
    process.stdout.write(JSON.stringify(payload, null, 2) + '\n');
  } catch (error) {
    const message = error instanceof Error ? error.message : 'unknown error';
    process.stdout.write(
      JSON.stringify(
        {
          status: 'failed',
          ready: false,
          runtimeMode: process.env.EDGE_RUNTIME_MODE ?? 'unknown',
          edgeId: process.env.EDGE_ID ?? 'unknown',
          siteId: process.env.SITE_ID ?? 'unknown',
          zoneId: process.env.ZONE_ID ?? 'unknown',
          sourceSystemId: process.env.SOURCE_SYSTEM_ID ?? 'unknown',
          hardwareKey: {
            required: false,
            status: 'unknown',
          },
          lockedReason: message,
          outbox: { pending: 0, failed: 0, dlq: 0 },
          quarantine: { count: 0 },
          diagnosticsEvidencePath: null,
          packageIntegrityStatus: 'missing_files',
          generatedAt: new Date().toISOString(),
          error: message,
        },
        null,
        2,
      ) + '\n',
    );
    process.exitCode = 1;
  }
}

main();
