/**
 * S02 LINK — Transport Layer (queue + retry + routing + DLQ + CORE delivery).
 */

export type {
  EdgeEvent,
  EdgeEventInput,
  WireErrorCode,
  WireEventSignPayload,
  WireEventV1,
} from '../generated/contracts/event-v1.js';
export {
  EDGE_EVENT_SCHEMA_VERSION,
  WIRE_ERROR_CODES,
  WIRE_PROTOCOL_VERSION,
  WireTransportError,
  parseWireEventJson,
  serializeWireEvent,
  serializeWireEventSignInput,
} from '../generated/contracts/event-v1.js';

export type { LinkHandoffEvent } from '../generated/protocol/edge-to-link.mapper.js';
export { mapEdgeToLink } from '../generated/protocol/edge-to-link.mapper.js';

export {
  attachWireEventSignature,
  buildEdgeLinkHeaders,
  computeWireEventSignature,
  signWireEventPayload,
  verifyWireEventSignature,
} from '../generated/security/edge-link-security-headers.js';

export {
  buildLinkSignaturePayload,
  extractLinkIngressHeaders,
  verifyLinkHmac,
  type EdgeLinkSecurityContext,
} from './link-hmac.js';
export type { EdgeLinkSecurityContext as LinkHmacContext } from './link-hmac.js';

export {
  createLinkIngressService,
  LinkIngressService,
  type LinkIngressLevel3BridgeConfig,
  type LinkIngressLevel3BridgeMetadata,
  type LinkIngressRequest,
  type LinkIngressResult,
} from './link-ingress.js';

export { freezeWireEvent, isWireEventFrozen } from '../generated/contracts/wire-event-immutability.js';
export {
  SECURITY_ZONES,
  ZONE_1_EDGE,
  ZONE_2_LINK,
  ZONE_3_CORE,
  assertLinkIngressZoneTransition,
  WireZoneViolationError,
  zoneName,
} from '../generated/security/zone-boundary.guard.js';

export type {
  CoreWireTraceResponse,
  WireEventLifecycle,
  WireEventMetrics,
  WireEventV1_1,
  WireTransportEvent,
} from '../generated/contracts/wire-event-v1.js';
export {
  WIRE_PROTOCOL_VERSION_V1_1,
  isSupportedWireProtocolVersion,
  isWireEventV1_1,
} from '../generated/contracts/wire-event-v1.js';
export { WireTraceError } from '../generated/contracts/wire-errors.js';

export type {
  TransportBackpressureSignal,
  TransportEnqueueResult,
  TransportEnvelope,
} from '../generated/contracts/transport-abstraction.js';

export type { KafkaWireEnvelope } from '../generated/contracts/kafka-envelope.js';
export { EDGELINK_KAFKA_TOPIC, serializeKafkaWireEnvelope } from '../generated/contracts/kafka-envelope.js';

export {
  createPartitionRouter,
  PartitionRouter,
  hashGatewayId,
  DEFAULT_PARTITION_COUNT,
  extractCanonicalRoutingContext,
  hasFullLevel3RoutingContext,
  routeCanonicalPartition,
  routeWithOptionalCanonicalPartition,
  type PartitionRouteResult,
  type ExtendedPartitionRouteResult,
  type OptionalCanonicalRouteOptions,
  type PartitionRoutingMode,
  type CanonicalRoutingContext,
} from './link-partition-router.js';
export {
  createLinkPartitionedQueues,
  LinkPartitionedQueues,
  LinkPartitionQueue,
  DEFAULT_MAX_PARTITION_QUEUE_SIZE,
  logLinkBackpressureDrop,
  type PartitionEnqueueAccepted,
  type PartitionBackpressureDrop,
  type PartitionPushResult,
  type PartitionPushWithRoutingResult,
  type PartitionLogEntry,
} from './link-partition-queues.js';

export {
  buildLevel3BridgeWarning,
  processLinkEventWithOptionalLevel3Bridge,
  shouldUseLevel3RuntimeBridge,
  type Level3BridgeProcessMode,
  type Level3BridgeProcessResult,
  type Level3RuntimeBridgeOptions,
} from './link-level3-runtime-bridge.js';

export {
  createPartitionLogStore,
  PartitionLogStore,
  type PartitionLogRecordKind,
} from './log-kernel/partition-log-store.js';
export type { ILogStorage, LogRecord, LogRecordKind } from './log-kernel/storage/ilog-storage.js';
export {
  createMemoryLogStorage,
  MemoryLogStorage,
} from './log-kernel/storage/memory-storage.js';
export {
  createFileLogStorage,
  FileLogStorage,
} from './log-kernel/storage/file-storage.js';
export {
  createRocksDbLogStorage,
  RocksDbLogStorage,
} from './log-kernel/storage/rocksdb-storage.js';
export {
  createPartitionDlqLogStore,
  PartitionDlqLogStore,
  type PartitionDlqLogEntry,
} from './log-kernel/partition-dlq-log-store.js';
export {
  createLinkReplayEngine,
  recoverPartitionedQueuesOnStartup,
  recoverUncommittedQueuesOnStartup,
  LinkReplayEngine,
  type LinkReplayResult,
} from './recovery/link-replay-engine.js';

export type { DeliveryAck, DeliveryAckStatus } from '../generated/contracts/delivery-ack.js';
export { createDeliveryAck, DELIVERY_ACK_PROTOCOL_VERSION } from '../generated/contracts/delivery-ack.js';
export type { IOffsetCommitStore, OffsetCommit, OffsetCommitStatus } from './log-kernel/offset/offset-commit.js';
export {
  createMemoryOffsetCommitStore,
  MemoryOffsetCommitStore,
} from './log-kernel/offset/memory-offset-commit-store.js';

export { createLinkQueue, LinkQueue } from './link-queue.js';
export { evaluateLinkRetry, type LinkRetryDecision } from './link-retry.js';
export { createLinkDlq, LinkDlq, type LinkDlqEntry } from './link-dlq.js';
export { routeToCoreSystem, type CoreSystemRoute } from './link-router.js';
export {
  createLinkDeliveryService,
  LinkDeliveryService,
  type CoreSystemDeliverer,
  type LinkDeliveryResult,
} from './link-delivery.js';

export {
  transitionLinkState,
  type LinkDeliveryState,
  type LinkQueueRecord,
} from './link-state.js';

export { createLinkQueue as createIntegrationLinkQueue, LinkQueue as IntegrationLinkQueue } from './link-queue.js';
export { evaluateLinkRetry as evaluateIntegrationRetry } from './link-retry.js';
export { routeToCoreSystem as routeIntegrationEvent } from './link-router.js';
export type { CoreSystemRoute as IntegrationRoute } from './link-router.js';
export type { LinkHandoffEvent as EdgeToLinkHandoffEvent } from '../generated/protocol/edge-to-link.mapper.js';
export * from './contracts/edge-handoff-intake-contract.js';
export * from './contracts/edge-production-state-guard.js';
export * from './contracts/ingress-ack-lifecycle-contract.js';
export * from './contracts/security-reason-taxonomy.js';
export * from './contracts/queue-state-contract.js';
export * from './contracts/queue-item-contract.js';
export * from './contracts/partition-priority-contract.js';
export * from './contracts/durable-queue-contract.js';
export * from './contracts/delivery-target-contract.js';
export * from './contracts/delivery-idempotency-contract.js';
export * from './contracts/edge-link-reliability-contract.js';
export * from './contracts/delivery-attempt-receipt-contract.js';
export * from './contracts/production-delivery-block-guard.js';
export * from './contracts/retry-policy-contract.js';
export * from './contracts/retry-decision-contract.js';
export * from './contracts/dlq-reason-taxonomy.js';
export * from './contracts/dlq-movement-contract.js';
export * from './contracts/audit-event-contract.js';
export * from './contracts/evidence-chain-contract.js';
export * from './contracts/runtime-health-snapshot-contract.js';
export * from './contracts/runtime-diagnostics-bundle-contract.js';
