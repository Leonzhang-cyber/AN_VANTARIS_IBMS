import type {
  ConnectorCapability,
  ConnectorDefinition,
  ConnectorManagerHealthSnapshot,
  ConnectorProtocol,
  ConnectorRuntimeState,
  ConnectorValidationResult,
} from './connector-types.js';
import { DeliveryAuditChain } from './delivery-audit-chain.js';
import type { ProtocolPluginPollResult, ProtocolPluginRuntimeContext } from './protocol-plugin-types.js';
import type { ProtocolPluginRuntimeRegistry } from './protocol-plugin-registry.js';
import { buildEdgeEnvelopeFromNormalizedSamples, validateEdgeEnvelope } from './edge-envelope-builder.js';
import { LocalDeliveryOrchestrator } from './delivery-orchestrator.js';
import { LocalBufferStore } from './local-buffer-store.js';
import { normalizeProtocolPollResult } from './normalization-pipeline.js';
import type { LocalDeliveryPreviewResult, LocalRetryPolicy } from './delivery-orchestrator-types.js';
import type { EdgeEnvelope, EdgeEnvelopeValidationResult } from './edge-envelope-types.js';
import type { LocalBufferStats } from './local-buffer-types.js';
import type { NormalizationResult } from './normalization-types.js';

const SUPPORTED_PROTOCOLS: readonly ConnectorProtocol[] = [
  'snmp',
  'modbus',
  'bacnet',
  'opcua',
  'opc-tcp',
  'http',
  'file',
  'simulator',
];

function nowIso(): string {
  return new Date().toISOString();
}

function isObject(value: unknown): value is Record<string, unknown> {
  return typeof value == 'object' && value != null;
}

function asString(value: unknown): string {
  return typeof value == 'string' ? value : '';
}

function asNumber(value: unknown): number {
  return typeof value == 'number' && Number.isFinite(value) ? value : 0;
}

function asBoolean(value: unknown): boolean {
  return value === true;
}

function asRecord(value: unknown): Record<string, unknown> {
  return isObject(value) ? value : {};
}

function asRetryPolicy(value: unknown): { maxRetries: number; backoffMs: number } {
  const raw = asRecord(value);
  return {
    maxRetries: asNumber(raw.maxRetries),
    backoffMs: asNumber(raw.backoffMs),
  };
}

function capabilityForProtocol(protocol: string): ConnectorCapability {
  const normalized = protocol as ConnectorProtocol;
  const common = {
    supportsWriteback: false,
    supportsDiscovery: true,
    supportsHealthCheck: true,
    supportsTimeSync: false,
  } as const;
  if (normalized == 'snmp') {
    return {
      protocol: normalized,
      supportsPolling: true,
      supportsSubscription: false,
      supportsTraps: true,
      outputTypes: ['telemetry', 'alarm', 'health'],
      ...common,
    };
  }
  if (normalized == 'modbus') {
    return {
      protocol: normalized,
      supportsPolling: true,
      supportsSubscription: false,
      supportsTraps: false,
      outputTypes: ['telemetry', 'health'],
      ...common,
    };
  }
  if (normalized == 'bacnet') {
    return {
      protocol: normalized,
      supportsPolling: true,
      supportsSubscription: true,
      supportsTraps: false,
      outputTypes: ['telemetry', 'event', 'health'],
      ...common,
    };
  }
  if (normalized == 'opcua') {
    return {
      protocol: normalized,
      supportsPolling: true,
      supportsSubscription: true,
      supportsTraps: false,
      outputTypes: ['telemetry', 'event', 'health'],
      ...common,
    };
  }
  if (normalized == 'opc-tcp') {
    return {
      protocol: normalized,
      supportsPolling: true,
      supportsSubscription: false,
      supportsTraps: false,
      outputTypes: ['telemetry', 'health'],
      ...common,
    };
  }
  if (normalized == 'http') {
    return {
      protocol: normalized,
      supportsPolling: true,
      supportsSubscription: false,
      supportsTraps: false,
      outputTypes: ['event', 'alarm', 'health'],
      ...common,
    };
  }
  if (normalized == 'file') {
    return {
      protocol: normalized,
      supportsPolling: true,
      supportsSubscription: false,
      supportsTraps: false,
      outputTypes: ['evidence', 'event'],
      ...common,
    };
  }
  return {
    protocol: 'simulator',
    supportsPolling: true,
    supportsSubscription: true,
    supportsTraps: false,
    outputTypes: ['telemetry', 'event', 'alarm', 'health'],
    ...common,
  };
}

export function loadConnectorDefinitions(input: unknown): ConnectorDefinition[] {
  let source: unknown = input;
  if (typeof input == 'string') {
    source = JSON.parse(input);
  }

  const rawList = Array.isArray(source)
    ? source
    : isObject(source) && Array.isArray(source.connectors)
      ? source.connectors
      : [];

  return rawList.map((item, index) => {
    const raw = asRecord(item);
    return {
      connectorId: asString(raw.connectorId) || `connector-${index + 1}`,
      name: asString(raw.name),
      protocol: asString(raw.protocol),
      enabled: asBoolean(raw.enabled),
      siteId: asString(raw.siteId),
      zoneId: asString(raw.zoneId),
      sourceSystemId: asString(raw.sourceSystemId),
      endpointRef: asString(raw.endpointRef),
      mappingRef: asString(raw.mappingRef),
      capabilityProfile: asString(raw.capabilityProfile),
      pollIntervalSec: asNumber(raw.pollIntervalSec),
      timeoutMs: asNumber(raw.timeoutMs),
      retryPolicy: asRetryPolicy(raw.retryPolicy),
      metadata: asRecord(raw.metadata),
    };
  });
}

export class ConnectorManager {
  private readonly definitions = new Map<string, ConnectorDefinition>();
  private readonly states = new Map<string, ConnectorRuntimeState>();
  private readonly validations = new Map<string, ConnectorValidationResult>();
  private readonly connectorPluginBindings = new Map<string, string>();
  private readonly pluginPollHistory = new Map<string, ProtocolPluginPollResult>();
  private readonly normalizationHistory = new Map<string, NormalizationResult>();
  private readonly envelopeHistory = new Map<string, EdgeEnvelope>();
  private readonly deliveryPreviewHistory = new Map<string, LocalDeliveryPreviewResult>();

  public constructor(
    private readonly options: {
      protocolPluginRegistry?: ProtocolPluginRuntimeRegistry;
      runtimeDefaults?: {
        edgeId?: string;
        siteId?: string;
      };
      runtimeRoot?: string;
      deliveryAuditChain?: DeliveryAuditChain;
    } = {},
  ) {
    this.deliveryAuditChain =
      this.options.deliveryAuditChain ?? new DeliveryAuditChain(this.options.runtimeRoot ?? './AN_VANTARIS_EDGE/.runtime');
    this.localBufferStore = new LocalBufferStore(this.options.runtimeRoot ?? './AN_VANTARIS_EDGE/.runtime', {
      deliveryAuditChain: this.deliveryAuditChain,
    });
    this.localDeliveryOrchestrator = new LocalDeliveryOrchestrator({
      deliveryAuditChain: this.deliveryAuditChain,
    });
  }

  private readonly localBufferStore: LocalBufferStore;
  private readonly localDeliveryOrchestrator: LocalDeliveryOrchestrator;
  private readonly deliveryAuditChain: DeliveryAuditChain;

  public validateConnectorDefinition(definition: ConnectorDefinition): ConnectorValidationResult {
    const errors: string[] = [];
    if (!definition.connectorId) errors.push('connectorId is required');
    if (!definition.name) errors.push('name is required');
    if (!definition.siteId) errors.push('siteId is required');
    if (!definition.zoneId) errors.push('zoneId is required');
    if (!definition.sourceSystemId) errors.push('sourceSystemId is required');
    if (!definition.endpointRef) errors.push('endpointRef is required');
    if (!definition.mappingRef) errors.push('mappingRef is required');
    if (!definition.capabilityProfile) errors.push('capabilityProfile is required');
    if (definition.pollIntervalSec <= 0) errors.push('pollIntervalSec must be > 0');
    if (definition.timeoutMs <= 0) errors.push('timeoutMs must be > 0');
    if (definition.retryPolicy.maxRetries < 0) errors.push('retryPolicy.maxRetries must be >= 0');
    if (definition.retryPolicy.backoffMs < 0) errors.push('retryPolicy.backoffMs must be >= 0');
    if (!SUPPORTED_PROTOCOLS.includes(definition.protocol as ConnectorProtocol)) {
      errors.push(`unsupported protocol: ${definition.protocol}`);
    }
    const result: ConnectorValidationResult = {
      connectorId: definition.connectorId,
      valid: errors.length == 0,
      errors,
    };
    this.validations.set(definition.connectorId, result);
    return result;
  }

  public registerConnector(definition: ConnectorDefinition): ConnectorRuntimeState {
    this.definitions.set(definition.connectorId, definition);
    const validation = this.validateConnectorDefinition(definition);
    const runtimeState: ConnectorRuntimeState = {
      connectorId: definition.connectorId,
      protocol: definition.protocol,
      lifecycleState: validation.valid ? (definition.enabled ? 'validated' : 'disabled') : 'quarantine',
      healthStatus: validation.valid ? (definition.enabled ? 'unknown' : 'disabled') : 'failed',
      lastStartedAt: null,
      lastStoppedAt: null,
      lastSeenAt: null,
      lastError: validation.valid ? null : validation.errors.join('; '),
      messageCount: 0,
      errorCount: validation.valid ? 0 : 1,
      quarantineCount: validation.valid ? 0 : 1,
      capabilitySummary: capabilityForProtocol(definition.protocol),
    };
    this.states.set(definition.connectorId, runtimeState);
    return runtimeState;
  }

  public listConnectors(): readonly ConnectorRuntimeState[] {
    return Array.from(this.states.values()).sort((a, b) => a.connectorId.localeCompare(b.connectorId));
  }

  public getConnector(connectorId: string): ConnectorRuntimeState | null {
    return this.states.get(connectorId) ?? null;
  }

  public startConnector(connectorId: string): ConnectorRuntimeState {
    const state = this.requireConnectorState(connectorId);
    const definition = this.requireDefinition(connectorId);
    const validation = this.validations.get(connectorId) ?? this.validateConnectorDefinition(definition);

    if (!validation.valid) {
      return this.markQuarantine(state, `validation_failed: ${validation.errors.join('; ')}`);
    }
    if (!definition.enabled) {
      state.lifecycleState = 'disabled';
      state.healthStatus = 'disabled';
      state.lastError = 'connector_disabled';
      state.errorCount += 1;
      return state;
    }

    const boundPluginId = this.connectorPluginBindings.get(connectorId);
    if (boundPluginId && this.options.protocolPluginRegistry) {
      const plugin = this.options.protocolPluginRegistry.getProtocolPlugin(boundPluginId);
      if (!plugin) {
        return this.markQuarantine(state, `protocol_plugin_not_found: ${boundPluginId}`);
      }
      const compatibility = this.options.protocolPluginRegistry.validateProtocolPluginCompatibility(definition, plugin);
      if (!compatibility.compatible) {
        return this.markQuarantine(state, `protocol_plugin_incompatible: ${compatibility.reasons.join('; ')}`);
      }
      const context = this.buildPluginRuntimeContext(definition);
      plugin.initialize(context);
      plugin.start(context);
    }

    state.lifecycleState = 'starting';
    state.lastStartedAt = nowIso();
    state.lifecycleState = 'running';
    state.healthStatus = 'healthy';
    state.lastSeenAt = nowIso();
    state.lastError = null;
    return state;
  }

  public stopConnector(connectorId: string): ConnectorRuntimeState {
    const state = this.requireConnectorState(connectorId);
    const wasDisabled = state.lifecycleState == 'disabled';
    state.lifecycleState = 'stopped';
    state.healthStatus = wasDisabled ? 'disabled' : 'unknown';
    state.lastStoppedAt = nowIso();
    return state;
  }

  public disableConnector(connectorId: string): ConnectorRuntimeState {
    const state = this.requireConnectorState(connectorId);
    state.lifecycleState = 'disabled';
    state.healthStatus = 'disabled';
    state.lastStoppedAt = nowIso();
    state.lastError = null;
    return state;
  }

  public markConnectorFailed(connectorId: string, reason: string): ConnectorRuntimeState {
    const state = this.requireConnectorState(connectorId);
    state.lifecycleState = 'failed';
    state.healthStatus = 'failed';
    state.lastError = reason;
    state.errorCount += 1;
    return state;
  }

  public bindConnectorProtocolPlugin(connectorId: string, pluginId: string): {
    readonly connectorId: string;
    readonly pluginId: string;
    readonly compatible: boolean;
    readonly reasons: readonly string[];
  } {
    const definition = this.requireDefinition(connectorId);
    const registry = this.options.protocolPluginRegistry;
    if (!registry) {
      return {
        connectorId,
        pluginId,
        compatible: false,
        reasons: ['protocol plugin registry is not configured'],
      };
    }
    const plugin = registry.getProtocolPlugin(pluginId);
    if (!plugin) {
      return {
        connectorId,
        pluginId,
        compatible: false,
        reasons: ['plugin not found'],
      };
    }
    const compatibility = registry.validateProtocolPluginCompatibility(definition, plugin);
    if (!compatibility.compatible) {
      return compatibility;
    }
    this.connectorPluginBindings.set(connectorId, pluginId);
    return compatibility;
  }

  public pollConnectorOnce(connectorId: string): ProtocolPluginPollResult {
    const definition = this.requireDefinition(connectorId);
    const state = this.requireConnectorState(connectorId);
    const registry = this.options.protocolPluginRegistry;
    if (!registry) {
      throw new Error('protocol plugin registry is not configured');
    }
    const pluginId = this.connectorPluginBindings.get(connectorId);
    if (!pluginId) {
      throw new Error(`no protocol plugin binding for connector: ${connectorId}`);
    }
    const plugin = registry.getProtocolPlugin(pluginId);
    if (!plugin) {
      throw new Error(`protocol plugin not found: ${pluginId}`);
    }
    const context = this.buildPluginRuntimeContext(definition);
    const result = plugin.pollOnce(context);
    state.lastSeenAt = result.health.lastPollAt;
    state.messageCount += result.samples.length;
    state.healthStatus = result.health.status == 'healthy' ? 'healthy' : 'degraded';
    state.lastError = result.health.lastError;
    this.pluginPollHistory.set(connectorId, result);
    return result;
  }

  public getConnectorHealthSnapshot(): ConnectorManagerHealthSnapshot {
    const connectors = this.listConnectors();
    const protocols = Array.from(new Set(connectors.map((item) => item.protocol))).sort();
    return {
      connectorCount: connectors.length,
      runningCount: connectors.filter((item) => item.lifecycleState == 'running').length,
      disabledCount: connectors.filter((item) => item.lifecycleState == 'disabled').length,
      failedCount: connectors.filter((item) => item.lifecycleState == 'failed').length,
      quarantineCount: connectors.filter((item) => item.lifecycleState == 'quarantine').length,
      protocols,
      generatedAt: nowIso(),
    };
  }

  public exportConnectorRegistrySnapshot(): {
    readonly generatedAt: string;
    readonly connectors: readonly ConnectorRuntimeState[];
    readonly validations: readonly ConnectorValidationResult[];
  } {
    return {
      generatedAt: nowIso(),
      connectors: this.listConnectors(),
      validations: Array.from(this.validations.values()).sort((a, b) => a.connectorId.localeCompare(b.connectorId)),
    };
  }

  public exportConnectorEvidence(): {
    readonly registry: ReturnType<ConnectorManager['exportConnectorRegistrySnapshot']>;
    readonly health: ConnectorManagerHealthSnapshot;
    readonly pluginSummary: ReturnType<ConnectorManager['getPluginRuntimeSummary']>;
  } {
    return {
      registry: this.exportConnectorRegistrySnapshot(),
      health: this.getConnectorHealthSnapshot(),
      pluginSummary: this.getPluginRuntimeSummary(),
    };
  }

  public getPluginRuntimeSummary(): {
    readonly pluginRegistryConfigured: boolean;
    readonly pluginCount: number;
    readonly boundConnectorCount: number;
    readonly pollHistoryCount: number;
    readonly pluginIds: readonly string[];
    readonly generatedAt: string;
  } {
    const registrySnapshot = this.options.protocolPluginRegistry?.exportProtocolPluginRegistrySnapshot();
    return {
      pluginRegistryConfigured: Boolean(this.options.protocolPluginRegistry),
      pluginCount: registrySnapshot?.pluginCount ?? 0,
      boundConnectorCount: this.connectorPluginBindings.size,
      pollHistoryCount: this.pluginPollHistory.size,
      pluginIds: registrySnapshot?.plugins.map((plugin) => plugin.pluginId) ?? [],
      generatedAt: nowIso(),
    };
  }

  public getLastPollResult(connectorId: string): ProtocolPluginPollResult | null {
    return this.pluginPollHistory.get(connectorId) ?? null;
  }

  public pollNormalizeOnce(connectorId: string): {
    readonly connectorId: string;
    readonly protocol: string;
    readonly pollResult: ProtocolPluginPollResult;
    readonly normalizationResult: NormalizationResult;
    readonly envelope: EdgeEnvelope;
    readonly envelopeValidation: EdgeEnvelopeValidationResult;
    readonly summary: {
      readonly sampleCount: number;
      readonly normalizedPointCount: number;
      readonly normalizedEventCount: number;
      readonly normalizationWarningCount: number;
      readonly normalizationErrorCount: number;
      readonly envelopeValid: boolean;
    };
    readonly generatedAt: string;
  } {
    const definition = this.requireDefinition(connectorId);
    const pollResult = this.pollConnectorOnce(connectorId);
    const normalizationResult = normalizeProtocolPollResult(pollResult);
    const envelope = buildEdgeEnvelopeFromNormalizedSamples({
      edgeNodeId: this.options.runtimeDefaults?.edgeId ?? 'edge-c2-runtime',
      connectorId,
      protocol: definition.protocol as ConnectorProtocol,
      sourceRef: definition.sourceSystemId,
      points: normalizationResult.normalizedPoints,
      events: normalizationResult.normalizedEvents,
    });
    const envelopeValidation = validateEdgeEnvelope(envelope);
    this.normalizationHistory.set(connectorId, normalizationResult);
    this.envelopeHistory.set(connectorId, envelope);
    return {
      connectorId,
      protocol: pollResult.protocol,
      pollResult,
      normalizationResult,
      envelope,
      envelopeValidation,
      summary: {
        sampleCount: pollResult.samples.length,
        normalizedPointCount: normalizationResult.normalizedPoints.length,
        normalizedEventCount: normalizationResult.normalizedEvents.length,
        normalizationWarningCount: normalizationResult.warnings.length,
        normalizationErrorCount: normalizationResult.errors.length,
        envelopeValid: envelopeValidation.valid,
      },
      generatedAt: nowIso(),
    };
  }

  public getLastNormalizationResult(connectorId: string): NormalizationResult | null {
    return this.normalizationHistory.get(connectorId) ?? null;
  }

  public getLastEnvelope(connectorId: string): EdgeEnvelope | null {
    return this.envelopeHistory.get(connectorId) ?? null;
  }

  public bufferIngestOnce(connectorId: string): {
    readonly connectorId: string;
    readonly protocol: string;
    readonly envelopeId: string;
    readonly recordId: string | null;
    readonly ingestOk: boolean;
    readonly bufferStats: LocalBufferStats;
    readonly generatedAt: string;
  } {
    const pipeline = this.pollNormalizeOnce(connectorId);
    const ingest = this.localBufferStore.ingestEdgeEnvelope(pipeline.envelope);
    return {
      connectorId,
      protocol: pipeline.protocol,
      envelopeId: pipeline.envelope.header.envelopeId,
      recordId: ingest.recordId,
      ingestOk: ingest.ok,
      bufferStats: this.localBufferStore.getLocalBufferStats(),
      generatedAt: nowIso(),
    };
  }

  public getLocalBufferStore(): LocalBufferStore {
    return this.localBufferStore;
  }

  public deliveryPreviewOnce(
    connectorId: string,
    policy: LocalRetryPolicy = {
      maxAttempts: 3,
      baseDelayMs: 1000,
      maxDelayMs: 30000,
      batchSize: 10,
    },
  ): {
    readonly connectorId: string;
    readonly bufferIngestResult: ReturnType<ConnectorManager['bufferIngestOnce']>;
    readonly deliveryPreview: LocalDeliveryPreviewResult;
    readonly deliveryStats: ReturnType<LocalDeliveryOrchestrator['getDeliveryOrchestratorStats']>;
    readonly generatedAt: string;
  } {
    const bufferIngestResult = this.bufferIngestOnce(connectorId);
    const sourceRecords = this.localBufferStore.listBufferRecordsByStatuses(['staged', 'pending', 'failed']).records;
    const deliveryPreview = this.localDeliveryOrchestrator.createDeliveryBatchPreview(sourceRecords, policy);
    this.deliveryPreviewHistory.set(connectorId, deliveryPreview);
    return {
      connectorId,
      bufferIngestResult,
      deliveryPreview,
      deliveryStats: this.localDeliveryOrchestrator.getDeliveryOrchestratorStats(deliveryPreview),
      generatedAt: nowIso(),
    };
  }

  public fileImportPipelineOnce(
    connectorId: string,
    policy: LocalRetryPolicy = {
      maxAttempts: 3,
      baseDelayMs: 1000,
      maxDelayMs: 30000,
      batchSize: 10,
    },
  ): ReturnType<ConnectorManager['deliveryPreviewOnce']> {
    const definition = this.requireDefinition(connectorId);
    if (definition.protocol != 'file') {
      throw new Error(`connector is not file protocol: ${connectorId}`);
    }
    return this.deliveryPreviewOnce(connectorId, policy);
  }

  public httpPollingPipelineOnce(
    connectorId: string,
    policy: LocalRetryPolicy = {
      maxAttempts: 3,
      baseDelayMs: 1000,
      maxDelayMs: 30000,
      batchSize: 10,
    },
  ): ReturnType<ConnectorManager['deliveryPreviewOnce']> {
    const definition = this.requireDefinition(connectorId);
    if (definition.protocol != 'http') {
      throw new Error(`connector is not http protocol: ${connectorId}`);
    }
    return this.deliveryPreviewOnce(connectorId, policy);
  }

  public snmpReadonlyPipelineOnce(
    connectorId: string,
    policy: LocalRetryPolicy = {
      maxAttempts: 3,
      baseDelayMs: 1000,
      maxDelayMs: 30000,
      batchSize: 10,
    },
  ): ReturnType<ConnectorManager['deliveryPreviewOnce']> {
    const definition = this.requireDefinition(connectorId);
    if (definition.protocol != 'snmp') {
      throw new Error(`connector is not snmp protocol: ${connectorId}`);
    }
    return this.deliveryPreviewOnce(connectorId, policy);
  }

  public modbusTcpReadonlyPipelineOnce(
    connectorId: string,
    policy: LocalRetryPolicy = {
      maxAttempts: 3,
      baseDelayMs: 1000,
      maxDelayMs: 30000,
      batchSize: 10,
    },
  ): ReturnType<ConnectorManager['deliveryPreviewOnce']> {
    const definition = this.requireDefinition(connectorId);
    if (definition.protocol != 'modbus') {
      throw new Error(`connector is not modbus protocol: ${connectorId}`);
    }
    return this.deliveryPreviewOnce(connectorId, policy);
  }

  public bacnetIpReadonlyPipelineOnce(
    connectorId: string,
    policy: LocalRetryPolicy = {
      maxAttempts: 3,
      baseDelayMs: 1000,
      maxDelayMs: 30000,
      batchSize: 10,
    },
  ): ReturnType<ConnectorManager['deliveryPreviewOnce']> {
    const definition = this.requireDefinition(connectorId);
    if (definition.protocol != 'bacnet') {
      throw new Error(`connector is not bacnet protocol: ${connectorId}`);
    }
    return this.deliveryPreviewOnce(connectorId, policy);
  }

  public opcUaReadonlyPipelineOnce(
    connectorId: string,
    policy: LocalRetryPolicy = {
      maxAttempts: 3,
      baseDelayMs: 1000,
      maxDelayMs: 30000,
      batchSize: 10,
    },
  ): ReturnType<ConnectorManager['deliveryPreviewOnce']> {
    const definition = this.requireDefinition(connectorId);
    if (definition.protocol != 'opcua') {
      throw new Error(`connector is not opcua protocol: ${connectorId}`);
    }
    return this.deliveryPreviewOnce(connectorId, policy);
  }

  public getLocalDeliveryOrchestrator(): LocalDeliveryOrchestrator {
    return this.localDeliveryOrchestrator;
  }

  public getLastDeliveryPreview(connectorId: string): LocalDeliveryPreviewResult | null {
    return this.deliveryPreviewHistory.get(connectorId) ?? null;
  }

  public getDeliveryAuditChain(): DeliveryAuditChain {
    return this.deliveryAuditChain;
  }

  public getDeliveryAuditSummary(): {
    readonly valid: boolean;
    readonly recordCount: number;
    readonly firstHash: string | null;
    readonly lastHash: string | null;
    readonly brokenAtSequence: number | null;
    readonly generatedAt: string;
  } {
    return this.deliveryAuditChain.getDeliveryAuditIntegritySummary();
  }

  private requireDefinition(connectorId: string): ConnectorDefinition {
    const definition = this.definitions.get(connectorId);
    if (!definition) throw new Error(`connector definition not registered: ${connectorId}`);
    return definition;
  }

  private requireConnectorState(connectorId: string): ConnectorRuntimeState {
    const state = this.states.get(connectorId);
    if (!state) throw new Error(`connector state not registered: ${connectorId}`);
    return state;
  }

  private markQuarantine(state: ConnectorRuntimeState, reason: string): ConnectorRuntimeState {
    state.lifecycleState = 'quarantine';
    state.healthStatus = 'failed';
    state.lastError = reason;
    state.errorCount += 1;
    state.quarantineCount += 1;
    return state;
  }

  private buildPluginRuntimeContext(definition: ConnectorDefinition): ProtocolPluginRuntimeContext {
    return {
      edgeId: this.options.runtimeDefaults?.edgeId ?? 'edge-c2-runtime',
      siteId: definition.siteId || this.options.runtimeDefaults?.siteId || 'site-001',
      connectorId: definition.connectorId,
      sourceSystemId: definition.sourceSystemId,
      protocol: definition.protocol as ConnectorProtocol,
      now: nowIso(),
      metadata: definition.metadata,
    };
  }
}
