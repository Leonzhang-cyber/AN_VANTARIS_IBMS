/**
 * S02 LINK — deterministic partition routing (hash-only, no validation).
 *
 * Legacy GA hot path: gatewayId-only hash. Level 3 canonical router uses
 * siteId + gatewayId + sourceSystemId via `level3/partition/partition-router.ts`.
 *
 * Canonical Level 3 routing is opt-in (`canonicalRoutingEnabled`) and LOCAL_DRY_RUN_ONLY safe.
 */

import type { WireTransportEvent } from '../generated/contracts/wire-event-v1.js';

export const DEFAULT_PARTITION_COUNT = 16;

export type PartitionRoutingMode = 'legacy' | 'canonical';

export interface PartitionRouteResult {
  readonly partition: number;
  readonly key: string;
  readonly payload: WireTransportEvent;
  /** Informational only — partition owner from control plane (no routing impact). */
  readonly partitionOwner?: string;
}

export interface ExtendedPartitionRouteResult extends PartitionRouteResult {
  readonly routingMode: PartitionRoutingMode;
  readonly warnings?: readonly string[];
}

export interface OptionalCanonicalRouteOptions {
  readonly canonicalRoutingEnabled?: boolean;
  readonly siteId?: string;
  readonly partitionCount?: number;
}

export interface CanonicalRoutingContext {
  readonly siteId?: string;
  readonly sourceSystemId?: string;
  readonly connectorId?: string;
}

export interface ClusterState {
  readonly partitionMap: Record<number, string>;
}

/** FNV-1a 32-bit — deterministic, allocation-free hot path. */
export function hashGatewayId(gatewayId: string): number {
  let hash = 2_166_136_261;
  const normalized = gatewayId.trim();

  for (let index = 0; index < normalized.length; index += 1) {
    hash ^= normalized.charCodeAt(index);
    hash = Math.imul(hash, 16_777_619);
  }

  return hash >>> 0;
}

export interface PartitionRouterOptions {
  readonly partitionCount?: number;
  /** Optional control-plane state — ownership is informational only. */
  readonly clusterState?: ClusterState;
}

function buildPartitionKey(input: {
  siteId: string;
  gatewayId: string;
  sourceSystemId: string;
}): string {
  return `${input.siteId}::${input.gatewayId}::${input.sourceSystemId}`;
}

function hashPartitionKey(partitionKey: string): number {
  let hash = 2_166_136_261;
  for (let index = 0; index < partitionKey.length; index += 1) {
    hash ^= partitionKey.charCodeAt(index);
    hash = Math.imul(hash, 16_777_619);
  }
  return hash >>> 0;
}

export class PartitionRouter {
  public constructor(
    private readonly partitionCount: number = DEFAULT_PARTITION_COUNT,
    private readonly clusterState?: ClusterState,
  ) {
    if (!Number.isInteger(partitionCount) || partitionCount < 1) {
      throw new Error('partitionCount must be a positive integer');
    }
  }

  public getPartitionCount(): number {
    return this.partitionCount;
  }

  public getPartition(event: WireTransportEvent): number {
    return hashGatewayId(event.gatewayId) % this.partitionCount;
  }

  public getPartitionForKey(gatewayId: string): number {
    return hashGatewayId(gatewayId) % this.partitionCount;
  }

  public route(event: WireTransportEvent): PartitionRouteResult {
    const partition = this.getPartition(event);
    const partitionOwner = this.clusterState?.partitionMap[partition];

    return {
      partition,
      key: event.gatewayId,
      payload: event,
      ...(partitionOwner !== undefined ? { partitionOwner } : {}),
    };
  }
}

export function createPartitionRouter(
  partitionCount?: number,
  clusterState?: ClusterState,
): PartitionRouter {
  return new PartitionRouter(partitionCount, clusterState);
}

export function createPartitionRouterWithOptions(
  options: PartitionRouterOptions = {},
): PartitionRouter {
  return new PartitionRouter(options.partitionCount, options.clusterState);
}

export function extractCanonicalRoutingContext(event: WireTransportEvent): CanonicalRoutingContext {
  const siteId = typeof event.payload.siteId === 'string' ? event.payload.siteId : undefined;
  const sourceSystemId =
    typeof event.payload.sourceSystemId === 'string' ? event.payload.sourceSystemId : undefined;
  const connectorId =
    typeof event.payload.connectorId === 'string' ? event.payload.connectorId : undefined;

  return {
    ...(siteId !== undefined ? { siteId } : {}),
    ...(sourceSystemId !== undefined ? { sourceSystemId } : {}),
    ...(connectorId !== undefined ? { connectorId } : {}),
  };
}

export function hasFullLevel3RoutingContext(
  event: WireTransportEvent,
  siteIdFallback?: string,
): boolean {
  const context = extractCanonicalRoutingContext(event);
  const siteId = context.siteId ?? siteIdFallback;
  return (
    siteId !== undefined &&
    siteId.trim() !== '' &&
    event.gatewayId.trim() !== '' &&
    context.sourceSystemId !== undefined &&
    context.sourceSystemId.trim() !== ''
  );
}

export function routeCanonicalPartition(
  event: WireTransportEvent,
  input: {
    siteId: string;
    sourceSystemId: string;
    partitionCount: number;
  },
): Pick<PartitionRouteResult, 'partition' | 'key'> {
  const partitionKey = buildPartitionKey({
    siteId: input.siteId,
    gatewayId: event.gatewayId,
    sourceSystemId: input.sourceSystemId,
  });
  const partition = hashPartitionKey(partitionKey) % input.partitionCount;
  return { partition, key: partitionKey };
}

export function routeWithOptionalCanonicalPartition(
  event: WireTransportEvent,
  router: PartitionRouter,
  options: OptionalCanonicalRouteOptions = {},
): ExtendedPartitionRouteResult {
  const context = extractCanonicalRoutingContext(event);
  const siteId = context.siteId ?? options.siteId;
  const partitionCount = options.partitionCount ?? router.getPartitionCount();

  if (
    options.canonicalRoutingEnabled !== true ||
    siteId === undefined ||
    siteId.trim() === '' ||
    context.sourceSystemId === undefined ||
    context.sourceSystemId.trim() === ''
  ) {
    const legacy = router.route(event);
    const warnings =
      options.canonicalRoutingEnabled === true &&
      (context.sourceSystemId === undefined || context.sourceSystemId.trim() === '')
        ? (['MISSING_SOURCE_SYSTEM_ID — legacy gateway-only routing remains active'] as const)
        : undefined;

    return {
      ...legacy,
      routingMode: 'legacy',
      ...(warnings !== undefined ? { warnings } : {}),
    };
  }

  const canonical = routeCanonicalPartition(event, {
    siteId,
    sourceSystemId: context.sourceSystemId,
    partitionCount,
  });

  return {
    partition: canonical.partition,
    key: canonical.key,
    payload: event,
    routingMode: 'canonical',
  };
}
