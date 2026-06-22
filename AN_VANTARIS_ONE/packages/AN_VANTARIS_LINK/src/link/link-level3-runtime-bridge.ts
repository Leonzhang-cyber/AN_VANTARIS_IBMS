/**
 * Opt-in bridge from GA LINK hot path to Level 3 runtime adapter.
 *
 * LOCAL_DRY_RUN_ONLY — legacy behavior remains default; no production activation.
 */

import type { WireTransportEvent } from '../generated/contracts/wire-event-v1.js';
import type {
  Level3LinkRuntimeAdapter,
  MachineIdentityRef,
  ProcessLevel3IngressEventResult,
} from './link-level3-stubs.js';
import {
  buildSignedEdgeEventFromWireTransport,
  canUseCanonicalLevel3Routing,
  extractLegacyLevel3RoutingContext,
  validateSignedEdgeEvent,
} from './link-level3-stubs.js';
import {
  createPartitionRouter,
  type ExtendedPartitionRouteResult,
  type PartitionRouter,
  routeWithOptionalCanonicalPartition,
} from './link-partition-router.js';

export type Level3BridgeProcessMode = 'legacy' | 'level3' | 'legacy_fallback';

export interface Level3RuntimeBridgeOptions {
  readonly level3BridgeEnabled?: boolean;
  readonly localDryRunOnly?: boolean;
  readonly testOnlyMode?: boolean;
  readonly siteId?: string;
  readonly clusterId?: string;
  readonly linkNodeId?: string;
  readonly adapter?: Level3LinkRuntimeAdapter;
  readonly legacyRouter?: PartitionRouter;
  readonly canonicalRoutingEnabled?: boolean;
  readonly securityValidationEnabled?: boolean;
  readonly machineIdentity?: MachineIdentityRef;
  readonly testOnlySignatureValidation?: boolean;
  readonly allowedSchemaVersions?: readonly string[];
  readonly maxClockSkewMs?: number;
}

export interface Level3BridgeProcessResult {
  readonly mode: Level3BridgeProcessMode;
  readonly warnings: readonly string[];
  readonly legacyRoute?: ExtendedPartitionRouteResult;
  readonly level3Result?: ProcessLevel3IngressEventResult;
}

export function buildLevel3BridgeWarning(reason: string): string {
  return `LEVEL3_BRIDGE_WARNING: ${reason}`;
}

function extractConnectorId(event: WireTransportEvent): string | undefined {
  const connectorId = event.payload.connectorId;
  if (typeof connectorId !== 'string' || connectorId.trim() === '') {
    return undefined;
  }
  return connectorId.trim();
}

export function shouldUseLevel3RuntimeBridge(
  event: WireTransportEvent,
  options: Level3RuntimeBridgeOptions,
): boolean {
  if (options.level3BridgeEnabled !== true) {
    return false;
  }

  if (options.localDryRunOnly !== true && options.testOnlyMode !== true) {
    return false;
  }

  const extracted = extractLegacyLevel3RoutingContext(event);
  const siteId = extracted.siteId ?? options.siteId;
  const connectorId = extractConnectorId(event);

  if (siteId === undefined || siteId.trim() === '') {
    return false;
  }
  if (event.gatewayId.trim() === '') {
    return false;
  }
  if (extracted.sourceSystemId === undefined || extracted.sourceSystemId.trim() === '') {
    return false;
  }
  if (connectorId === undefined) {
    return false;
  }

  return canUseCanonicalLevel3Routing({
    siteId,
    gatewayId: event.gatewayId,
    sourceSystemId: extracted.sourceSystemId,
  });
}

export function processLinkEventWithOptionalLevel3Bridge(
  event: WireTransportEvent,
  options: Level3RuntimeBridgeOptions,
): Level3BridgeProcessResult {
  const router = options.legacyRouter ?? createPartitionRouter();

  if (options.level3BridgeEnabled !== true) {
    const legacyRoute = router.route(event);
    return {
      mode: 'legacy',
      warnings: [buildLevel3BridgeWarning('BRIDGE_DISABLED')],
      legacyRoute: { ...legacyRoute, routingMode: 'legacy' },
    };
  }

  if (options.localDryRunOnly !== true && options.testOnlyMode !== true) {
    const legacyRoute = router.route(event);
    return {
      mode: 'legacy_fallback',
      warnings: [buildLevel3BridgeWarning('LOCAL_DRY_RUN_ONLY_REQUIRED')],
      legacyRoute: { ...legacyRoute, routingMode: 'legacy' },
    };
  }

  if (!shouldUseLevel3RuntimeBridge(event, options)) {
    const legacyRoute = routeWithOptionalCanonicalPartition(event, router, {
      ...(options.canonicalRoutingEnabled !== undefined
        ? { canonicalRoutingEnabled: options.canonicalRoutingEnabled }
        : {}),
      ...(options.siteId !== undefined ? { siteId: options.siteId } : {}),
    });
    const warnings = [
      buildLevel3BridgeWarning('INCOMPLETE_L3_CONTEXT'),
      ...(legacyRoute.warnings ?? []),
    ];
    return {
      mode: 'legacy_fallback',
      warnings,
      legacyRoute,
    };
  }

  const adapter = options.adapter;
  if (adapter === undefined) {
    const legacyRoute = router.route(event);
    return {
      mode: 'legacy_fallback',
      warnings: [buildLevel3BridgeWarning('ADAPTER_NOT_CONFIGURED')],
      legacyRoute: { ...legacyRoute, routingMode: 'legacy' },
    };
  }

  const extracted = extractLegacyLevel3RoutingContext(event);
  const siteId = extracted.siteId ?? options.siteId!;
  const connectorId = extractConnectorId(event)!;
  const mappingVersion =
    typeof event.payload.mappingVersion === 'string' ? event.payload.mappingVersion : '1.0.0';

  const ingressInput = {
    siteId,
    clusterId: options.clusterId ?? 'default-cluster',
    linkNodeId: options.linkNodeId ?? 'default-link-node',
    gatewayId: event.gatewayId,
    sourceSystemId: extracted.sourceSystemId!,
    connectorId,
    eventId: event.eventId,
    schemaVersion: '1.0',
    mappingVersion,
    timestamp: event.timestamp,
    payload: { ...event.payload, eventId: event.eventId },
    messageId: event.eventId,
  };

  if (options.securityValidationEnabled === true) {
    if (options.localDryRunOnly !== true && options.testOnlyMode !== true) {
      const legacyRoute = router.route(event);
      return {
        mode: 'legacy_fallback',
        warnings: [buildLevel3BridgeWarning('SECURITY_VALIDATION_REQUIRES_DRY_RUN')],
        legacyRoute: { ...legacyRoute, routingMode: 'legacy' },
      };
    }

    const signedEvent = buildSignedEdgeEventFromWireTransport(event, {
      siteId,
      clusterId: ingressInput.clusterId,
      linkNodeId: ingressInput.linkNodeId,
      sourceSystemId: ingressInput.sourceSystemId,
      connectorId,
      mappingVersion,
      ...(options.machineIdentity !== undefined
        ? { machineIdentityRef: options.machineIdentity.identityRef }
        : {}),
    });

    const securityValidation = validateSignedEdgeEvent(signedEvent, {
      testOnlySignatureValidation: options.testOnlySignatureValidation ?? true,
      ...(options.machineIdentity !== undefined ? { machineIdentity: options.machineIdentity } : {}),
      ...(options.allowedSchemaVersions !== undefined
        ? { allowedSchemaVersions: options.allowedSchemaVersions }
        : {}),
      ...(options.maxClockSkewMs !== undefined ? { maxClockSkewMs: options.maxClockSkewMs } : {}),
    });

    if (!securityValidation.valid) {
      const reason = securityValidation.issues[0]?.message ?? 'signed edge event validation failed';
      const level3Result = adapter.processSecurityRejectedIngressEvent(
        ingressInput,
        ingressInput.payload,
        reason,
      );
      return {
        mode: 'level3',
        warnings: [
          buildLevel3BridgeWarning('SECURITY_VALIDATION_FAILED'),
          ...level3Result.warnings,
        ],
        level3Result,
      };
    }
  }

  const level3Result = adapter.processLevel3IngressEvent(ingressInput);

  return {
    mode: 'level3',
    warnings: level3Result.warnings,
    level3Result,
  };
}
