/**
 * LINK-C2-02 — EDGE production state guard contract.
 *
 * This LINK-owned guard blocks production delivery unless EDGE runtime,
 * pilot, production, and no-writeback conditions are explicitly approved.
 *
 * During LINK-C2 the expected/default result is BLOCKED.
 */

import type { EdgeBlockedProductionState } from './edge-handoff-intake-contract.js';
import { isProductionDeliveryAllowed } from './edge-handoff-intake-contract.js';

export type EdgeProductionStateGuardCode =
  | 'LINK_EDGE_RUNTIME_NOT_ENABLED'
  | 'LINK_EDGE_PILOT_NOT_APPROVED'
  | 'LINK_EDGE_PRODUCTION_NOT_APPROVED'
  | 'LINK_EDGE_WRITEBACK_PROHIBITED'
  | 'LINK_EDGE_PRODUCTION_DELIVERY_BLOCKED'
  | 'LINK_EDGE_PRODUCTION_DELIVERY_ALLOWED';

export interface EdgeProductionStateGuardResult {
  readonly allowed: boolean;
  readonly code: EdgeProductionStateGuardCode;
  readonly reason: string;
}

export function evaluateEdgeProductionStateGuard(
  state: EdgeBlockedProductionState,
): EdgeProductionStateGuardResult {
  if (state.runtimeEnabled !== true) {
    return {
      allowed: false,
      code: 'LINK_EDGE_RUNTIME_NOT_ENABLED',
      reason: 'EDGE runtime is not enabled',
    };
  }

  if (state.pilotApproved !== true) {
    return {
      allowed: false,
      code: 'LINK_EDGE_PILOT_NOT_APPROVED',
      reason: 'EDGE pilot is not approved',
    };
  }

  if (state.productionApproved !== true) {
    return {
      allowed: false,
      code: 'LINK_EDGE_PRODUCTION_NOT_APPROVED',
      reason: 'EDGE production is not approved',
    };
  }

  if (state.writebackRequested === true) {
    return {
      allowed: false,
      code: 'LINK_EDGE_WRITEBACK_PROHIBITED',
      reason: 'EDGE writeback is prohibited',
    };
  }

  if (!isProductionDeliveryAllowed(state)) {
    return {
      allowed: false,
      code: 'LINK_EDGE_PRODUCTION_DELIVERY_BLOCKED',
      reason: 'EDGE production delivery is blocked by policy',
    };
  }

  return {
    allowed: true,
    code: 'LINK_EDGE_PRODUCTION_DELIVERY_ALLOWED',
    reason: 'EDGE production delivery is allowed by approved state',
  };
}

export function assertEdgeProductionDeliveryBlockedForC2(
  state: EdgeBlockedProductionState,
): EdgeProductionStateGuardResult {
  const result = evaluateEdgeProductionStateGuard(state);

  if (result.allowed) {
    return {
      allowed: false,
      code: 'LINK_EDGE_PRODUCTION_DELIVERY_BLOCKED',
      reason: 'LINK-C2 does not allow production delivery even when state appears approved',
    };
  }

  return result;
}
