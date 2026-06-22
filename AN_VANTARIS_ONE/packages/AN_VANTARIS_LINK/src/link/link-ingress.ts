/**
 * S02 LINK — ingress API (IEC62443 ZONE 2 validated transport boundary).
 * Kafka-style partitioned transport: zone gate → validate → route → partition push.
 */

import type { KafkaWireEnvelope } from '../generated/contracts/kafka-envelope.js';
import { EDGELINK_KAFKA_TOPIC } from '../generated/contracts/kafka-envelope.js';
import { freezeWireEvent } from '../generated/contracts/wire-event-immutability.js';
import { WIRE_ERROR_CODES, type WireErrorCode } from '../generated/contracts/wire-errors.js';
import type { WireTransportEvent } from '../generated/contracts/wire-event-v1.js';
import { isSupportedWireProtocolVersion } from '../generated/contracts/wire-event-v1.js';
import { parseWireEventJson, serializeWireEvent } from '../generated/contracts/wire-serializer-v1.js';
import {
  extractLinkIngressHeaders,
  verifyWireEventSignature,
  type EdgeLinkSecurityContext,
} from '../generated/security/edge-link-security-headers.js';
import {
  assertLinkIngressZoneTransition,
  WireZoneViolationError,
  ZONE_1_EDGE,
  ZONE_2_LINK,
} from '../generated/security/zone-boundary.guard.js';
import {
  createLinkPartitionedQueues,
  LinkPartitionedQueues,
  logLinkBackpressureDrop,
} from './link-partition-queues.js';
import { PartitionRouter } from './link-partition-router.js';
import {
  processLinkEventWithOptionalLevel3Bridge,
  type Level3BridgeProcessMode,
  type Level3RuntimeBridgeOptions,
} from './link-level3-runtime-bridge.js';
import type { Level3LinkRuntimeAdapter, MachineIdentityRef } from './link-level3-stubs.js';

export interface LinkIngressLevel3BridgeConfig {
  readonly level3BridgeEnabled?: boolean;
  readonly localDryRunOnly?: boolean;
  readonly testOnlyMode?: boolean;
  readonly siteId?: string;
  readonly clusterId?: string;
  readonly linkNodeId?: string;
  readonly adapter?: Level3LinkRuntimeAdapter;
  readonly canonicalRoutingEnabled?: boolean;
  readonly securityValidationEnabled?: boolean;
  readonly machineIdentity?: MachineIdentityRef;
  readonly testOnlySignatureValidation?: boolean;
  readonly allowedSchemaVersions?: readonly string[];
  readonly maxClockSkewMs?: number;
}

export interface LinkIngressLevel3BridgeMetadata {
  readonly mode: Level3BridgeProcessMode;
  readonly warnings: readonly string[];
  readonly level3Status?: string;
  readonly level3QueueId?: string;
}

export interface LinkIngressRequest {
  readonly headers: Record<string, string | undefined>;
  readonly body: string;
  readonly signingSecret: string;
}

export interface LinkIngressResult {
  readonly accepted: boolean;
  readonly queueId: string | null;
  readonly partition: number | null;
  readonly reason: string | null;
  readonly errorCode: WireErrorCode | null;
  readonly routedToDlq: boolean;
  readonly event: WireTransportEvent | null;
  readonly envelope: KafkaWireEnvelope | null;
  readonly level3Bridge?: LinkIngressLevel3BridgeMetadata;
}

const TIMESTAMP_SKEW_MS = 5 * 60 * 1000;

export class LinkIngressService {
  public constructor(
    private readonly partitionedQueues: LinkPartitionedQueues = createLinkPartitionedQueues(),
    private readonly now: () => number = Date.now,
    private readonly level3BridgeConfig?: LinkIngressLevel3BridgeConfig,
  ) {}

  public getLevel3BridgeConfig(): LinkIngressLevel3BridgeConfig | undefined {
    return this.level3BridgeConfig;
  }

  public ingest(request: LinkIngressRequest): LinkIngressResult {
    try {
      assertLinkIngressZoneTransition(ZONE_1_EDGE, ZONE_2_LINK, null);
    } catch (error) {
      if (error instanceof WireZoneViolationError) {
        logLinkZoneViolation(error);
        return reject(WIRE_ERROR_CODES.WIRE_ZONE_VIOLATION, error.message);
      }
      throw error;
    }

    const headers = extractLinkIngressHeaders(request.headers);
    if (headers === null) {
      return reject(WIRE_ERROR_CODES.WIRE_FORMAT_INVALID, 'missing transport headers');
    }

    const parsed = parseWireEventJson(request.body);
    if (parsed === null) {
      return reject(WIRE_ERROR_CODES.WIRE_FORMAT_INVALID, 'invalid wire json');
    }

    if (!hasProtocolVersion(parsed)) {
      return reject(WIRE_ERROR_CODES.WIRE_PROTOCOL_MISSING, 'protocolVersion is required', parsed);
    }

    if (!parsed.gatewayId?.trim()) {
      return reject(WIRE_ERROR_CODES.MISSING_GATEWAY_ID, 'gatewayId is required', parsed);
    }

    if (!isSupportedWireProtocolVersion(parsed.protocolVersion)) {
      return this.routeUnsupportedProtocol(parsed, headers);
    }

    if (!isTimestampWithinSkew(parsed.timestamp, this.now())) {
      return reject(WIRE_ERROR_CODES.TIMESTAMP_SKEW, 'timestamp outside ±5 minute window', parsed);
    }

    if (!verifyWireEventSignature(parsed, request.signingSecret)) {
      return reject(WIRE_ERROR_CODES.INVALID_SIGNATURE, 'wire event signature mismatch', parsed);
    }

    if (headers.signature !== parsed.signature) {
      return reject(WIRE_ERROR_CODES.INVALID_SIGNATURE, 'transport header signature mismatch', parsed);
    }

    const immutableEvent = freezeWireEvent(parsed);

    let legacyFallbackBridge: LinkIngressLevel3BridgeMetadata | undefined;
    if (this.level3BridgeConfig?.level3BridgeEnabled === true) {
      const bridgeAttempt = this.attemptLevel3BridgeIngress(immutableEvent);
      if (bridgeAttempt.kind === 'handled') {
        return bridgeAttempt.result;
      }
      if (bridgeAttempt.kind === 'legacy_fallback') {
        legacyFallbackBridge = bridgeAttempt.metadata;
      }
    }

    const routed = this.partitionedQueues.getRouter().route(immutableEvent);
    const pushResult = this.partitionedQueues.getPartition(routed.partition).push(immutableEvent);

    if (!pushResult.accepted) {
      logLinkBackpressureDrop(immutableEvent, pushResult.partition);
      return {
        accepted: false,
        queueId: null,
        partition: pushResult.partition,
        reason: WIRE_ERROR_CODES.LINK_BACKPRESSURE_DROP,
        errorCode: WIRE_ERROR_CODES.LINK_BACKPRESSURE_DROP,
        routedToDlq: false,
        event: null,
        envelope: null,
        ...(legacyFallbackBridge !== undefined ? { level3Bridge: legacyFallbackBridge } : {}),
      };
    }

    const envelope = buildKafkaEnvelope(routed.partition, routed.key, immutableEvent);

    return {
      accepted: true,
      queueId: pushResult.queueId,
      partition: pushResult.partition,
      reason: null,
      errorCode: null,
      routedToDlq: false,
      event: immutableEvent,
      envelope,
      ...(legacyFallbackBridge !== undefined ? { level3Bridge: legacyFallbackBridge } : {}),
    };
  }

  public ingestWireEvent(
    request: LinkIngressRequest & { readonly event: WireTransportEvent },
  ): LinkIngressResult {
    return this.ingest({
      headers: request.headers,
      body: serializeWireEvent(request.event),
      signingSecret: request.signingSecret,
    });
  }

  public getPartitionedQueues(): LinkPartitionedQueues {
    return this.partitionedQueues;
  }

  public getRouter(): PartitionRouter {
    return this.partitionedQueues.getRouter();
  }

  private attemptLevel3BridgeIngress(
    event: WireTransportEvent,
  ):
    | { kind: 'handled'; result: LinkIngressResult }
    | { kind: 'legacy_fallback'; metadata: LinkIngressLevel3BridgeMetadata }
    | { kind: 'skip' } {
    const bridgeOptions: Level3RuntimeBridgeOptions = {
      level3BridgeEnabled: true,
      ...(this.level3BridgeConfig?.localDryRunOnly !== undefined
        ? { localDryRunOnly: this.level3BridgeConfig.localDryRunOnly }
        : {}),
      ...(this.level3BridgeConfig?.testOnlyMode !== undefined
        ? { testOnlyMode: this.level3BridgeConfig.testOnlyMode }
        : {}),
      ...(this.level3BridgeConfig?.siteId !== undefined ? { siteId: this.level3BridgeConfig.siteId } : {}),
      ...(this.level3BridgeConfig?.clusterId !== undefined
        ? { clusterId: this.level3BridgeConfig.clusterId }
        : {}),
      ...(this.level3BridgeConfig?.linkNodeId !== undefined
        ? { linkNodeId: this.level3BridgeConfig.linkNodeId }
        : {}),
      ...(this.level3BridgeConfig?.adapter !== undefined ? { adapter: this.level3BridgeConfig.adapter } : {}),
      ...(this.level3BridgeConfig?.canonicalRoutingEnabled !== undefined
        ? { canonicalRoutingEnabled: this.level3BridgeConfig.canonicalRoutingEnabled }
        : {}),
      ...(this.level3BridgeConfig?.securityValidationEnabled !== undefined
        ? { securityValidationEnabled: this.level3BridgeConfig.securityValidationEnabled }
        : {}),
      ...(this.level3BridgeConfig?.machineIdentity !== undefined
        ? { machineIdentity: this.level3BridgeConfig.machineIdentity }
        : {}),
      ...(this.level3BridgeConfig?.testOnlySignatureValidation !== undefined
        ? { testOnlySignatureValidation: this.level3BridgeConfig.testOnlySignatureValidation }
        : {}),
      ...(this.level3BridgeConfig?.allowedSchemaVersions !== undefined
        ? { allowedSchemaVersions: this.level3BridgeConfig.allowedSchemaVersions }
        : {}),
      ...(this.level3BridgeConfig?.maxClockSkewMs !== undefined
        ? { maxClockSkewMs: this.level3BridgeConfig.maxClockSkewMs }
        : {}),
      legacyRouter: this.partitionedQueues.getRouter(),
    };

    const bridgeResult = processLinkEventWithOptionalLevel3Bridge(event, bridgeOptions);
    const bridgeMetadata: LinkIngressLevel3BridgeMetadata = {
      mode: bridgeResult.mode,
      warnings: bridgeResult.warnings,
    };

    if (bridgeResult.mode === 'level3' && bridgeResult.level3Result !== undefined) {
      const level3Result = bridgeResult.level3Result;
      const partition =
        level3Result.partitionAssignment?.partitionId ??
        this.partitionedQueues.getRouter().getPartition(event);

      if (level3Result.status === 'accepted_queued') {
        const envelope = buildKafkaEnvelope(
          partition,
          level3Result.message?.queueId ?? event.gatewayId,
          event,
        );
        return {
          kind: 'handled',
          result: {
            accepted: true,
            queueId: level3Result.message?.messageId ?? level3Result.message?.queueId ?? null,
            partition,
            reason: null,
            errorCode: null,
            routedToDlq: false,
            event,
            envelope,
            level3Bridge: {
              ...bridgeMetadata,
              level3Status: level3Result.status,
              ...(level3Result.message?.queueId !== undefined
                ? { level3QueueId: level3Result.message.queueId }
                : {}),
            },
          },
        };
      }

      return {
        kind: 'handled',
        result: {
          accepted: false,
          queueId: null,
          partition,
          reason: level3Result.context.rejectionReason ?? 'LEVEL3_INGRESS_REJECTED',
          errorCode: null,
          routedToDlq: level3Result.status === 'rejected_dead_lettered',
          event,
          envelope: null,
          level3Bridge: {
            ...bridgeMetadata,
            level3Status: level3Result.status,
          },
        },
      };
    }

    if (bridgeResult.mode === 'legacy_fallback') {
      return { kind: 'legacy_fallback', metadata: bridgeMetadata };
    }

    return { kind: 'skip' };
  }

  private routeUnsupportedProtocol(
    event: WireTransportEvent,
    _headers: EdgeLinkSecurityContext,
  ): LinkIngressResult {
    const partition = this.partitionedQueues.getRouter().getPartition(event);
    const partitionQueue = this.partitionedQueues.getPartition(partition);

    partitionQueue.dlq.move(
      {
        queueId: `link-dlq-p${partition}-${event.eventId || 'unknown'}`,
        state: 'FAILED',
        attempts: 0,
        enqueuedAt: new Date().toISOString(),
        lastAttemptAt: new Date().toISOString(),
        dlqReason: WIRE_ERROR_CODES.UNSUPPORTED_PROTOCOL,
      },
      event,
      WIRE_ERROR_CODES.UNSUPPORTED_PROTOCOL,
    );

    return {
      accepted: false,
      queueId: null,
      partition,
      reason: WIRE_ERROR_CODES.UNSUPPORTED_PROTOCOL,
      errorCode: WIRE_ERROR_CODES.UNSUPPORTED_PROTOCOL,
      routedToDlq: true,
      event,
      envelope: null,
    };
  }
}

function buildKafkaEnvelope(
  partition: number,
  key: string,
  event: WireTransportEvent,
): KafkaWireEnvelope {
  return {
    topic: EDGELINK_KAFKA_TOPIC,
    partition,
    key,
    timestamp: event.timestamp,
    value: event,
  };
}

function logLinkZoneViolation(error: WireZoneViolationError): void {
  console.error(
    JSON.stringify({
      layer: 'LINK',
      action: 'zone_violation',
      code: error.code,
      fromZone: error.fromZone,
      toZone: error.toZone,
      eventId: error.eventId,
      message: error.message,
      timestamp: new Date().toISOString(),
    }),
  );
}

function hasProtocolVersion(event: WireTransportEvent): boolean {
  return typeof event.protocolVersion === 'string' && event.protocolVersion.trim().length > 0;
}

function isTimestampWithinSkew(timestamp: string, nowMs: number): boolean {
  const parsed = new Date(timestamp);
  if (Number.isNaN(parsed.getTime())) {
    return false;
  }

  return Math.abs(parsed.getTime() - nowMs) <= TIMESTAMP_SKEW_MS;
}

function reject(code: WireErrorCode, reason: string, _event?: WireTransportEvent): LinkIngressResult {
  return {
    accepted: false,
    queueId: null,
    partition: null,
    reason,
    errorCode: code,
    routedToDlq: false,
    event: null,
    envelope: null,
  };
}

export function createLinkIngressService(
  partitionedQueues?: LinkPartitionedQueues,
  level3BridgeOrNow?: LinkIngressLevel3BridgeConfig | (() => number),
): LinkIngressService {
  if (typeof level3BridgeOrNow === 'function') {
    return new LinkIngressService(partitionedQueues, level3BridgeOrNow);
  }
  return new LinkIngressService(partitionedQueues, Date.now, level3BridgeOrNow);
}

export type { EdgeLinkSecurityContext };
