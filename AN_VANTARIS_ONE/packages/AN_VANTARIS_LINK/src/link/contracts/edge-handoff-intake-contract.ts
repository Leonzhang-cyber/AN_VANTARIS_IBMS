/**
 * LINK-C2-01 — EDGE handoff intake contract.
 *
 * This contract is LINK-owned and consumes frozen EDGE handoff concepts.
 * It must not modify or redefine AN_VANTARIS_EDGE runtime behavior.
 *
 * Production delivery remains blocked unless a later controlled pilot /
 * production approval gate explicitly enables it.
 */

export type EdgeHandoffDecisionState =
  | 'ACCEPTED_READ_ONLY'
  | 'BLOCKED_RUNTIME_NOT_ENABLED'
  | 'BLOCKED_PILOT_NOT_APPROVED'
  | 'BLOCKED_PRODUCTION_NOT_APPROVED'
  | 'BLOCKED_WRITEBACK_PROHIBITED'
  | 'BLOCKED_POLICY';

export type EdgeHandoffRecordType =
  | 'telemetry'
  | 'event'
  | 'alarm'
  | 'health'
  | 'evidence'
  | 'throughput'
  | 'sync_batch'
  | 'audit'
  | 'config_version'
  | 'unknown';

export interface EdgeBlockedProductionState {
  readonly runtimeEnabled: boolean;
  readonly pilotApproved: boolean;
  readonly productionApproved: boolean;
  readonly writebackRequested: boolean;
  readonly productionDeliveryAllowed: boolean;
  readonly reason:
    | 'EDGE_RUNTIME_NOT_ENABLED'
    | 'EDGE_PILOT_NOT_APPROVED'
    | 'EDGE_PRODUCTION_NOT_APPROVED'
    | 'EDGE_WRITEBACK_PROHIBITED'
    | 'EDGE_PRODUCTION_DELIVERY_BLOCKED';
}

export interface EdgeHandoffEvidenceRef {
  readonly evidenceId: string;
  readonly evidenceType:
    | 'adapter'
    | 'connector_decision'
    | 'pilot_approval'
    | 'endpoint_approval'
    | 'credential_reference'
    | 'rollback_plan'
    | 'operator_authorization'
    | 'collection'
    | 'handoff'
    | 'unknown';
  readonly sourcePath?: string;
  readonly hash?: string;
}

export interface EdgeHandoffSourceMetadata {
  readonly gatewayId: string;
  readonly edgeId?: string;
  readonly siteId?: string;
  readonly tenantId?: string;
  readonly sourceSystem?: string;
  readonly connectorType?: string;
  readonly adapterType?: string;
}

export interface EdgeHandoffIntakeContract {
  readonly protocolVersion: string;
  readonly eventId: string;
  readonly traceId: string;
  readonly correlationId?: string;
  readonly recordType: EdgeHandoffRecordType;
  readonly occurredAt: string;
  readonly receivedAt: string;
  readonly payloadHash: string;
  readonly normalizedPayload: unknown;
  readonly source: EdgeHandoffSourceMetadata;
  readonly decisionState: EdgeHandoffDecisionState;
  readonly productionState: EdgeBlockedProductionState;
  readonly evidenceRefs: readonly EdgeHandoffEvidenceRef[];
}

export interface EdgeHandoffIntakeValidationResult {
  readonly valid: boolean;
  readonly reasons: readonly string[];
}

export function createDefaultBlockedEdgeProductionState(): EdgeBlockedProductionState {
  return {
    runtimeEnabled: false,
    pilotApproved: false,
    productionApproved: false,
    writebackRequested: false,
    productionDeliveryAllowed: false,
    reason: 'EDGE_PRODUCTION_DELIVERY_BLOCKED',
  };
}

export function isProductionDeliveryAllowed(
  state: EdgeBlockedProductionState,
): boolean {
  return (
    state.runtimeEnabled === true &&
    state.pilotApproved === true &&
    state.productionApproved === true &&
    state.writebackRequested === false &&
    state.productionDeliveryAllowed === true
  );
}

export function validateEdgeHandoffIntakeContract(
  intake: EdgeHandoffIntakeContract,
): EdgeHandoffIntakeValidationResult {
  const reasons: string[] = [];

  if (!intake.protocolVersion.trim()) {
    reasons.push('protocolVersion is required');
  }

  if (!intake.eventId.trim()) {
    reasons.push('eventId is required');
  }

  if (!intake.traceId.trim()) {
    reasons.push('traceId is required');
  }

  if (!intake.occurredAt.trim()) {
    reasons.push('occurredAt is required');
  }

  if (!intake.receivedAt.trim()) {
    reasons.push('receivedAt is required');
  }

  if (!intake.payloadHash.trim()) {
    reasons.push('payloadHash is required');
  }

  if (!intake.source.gatewayId.trim()) {
    reasons.push('source.gatewayId is required');
  }

  if (intake.productionState.writebackRequested === true) {
    reasons.push('writeback is prohibited');
  }

  if (isProductionDeliveryAllowed(intake.productionState)) {
    reasons.push('production delivery is not allowed during LINK-C2');
  }

  return {
    valid: reasons.length === 0,
    reasons,
  };
}
