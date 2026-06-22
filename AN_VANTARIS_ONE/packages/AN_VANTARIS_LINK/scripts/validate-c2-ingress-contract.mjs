import assert from 'node:assert/strict';
import {
  createDefaultBlockedEdgeProductionState,
  validateEdgeHandoffIntakeContract,
} from '../dist-c2/src/link/contracts/edge-handoff-intake-contract.js';
import {
  assertEdgeProductionDeliveryBlockedForC2,
  evaluateEdgeProductionStateGuard,
} from '../dist-c2/src/link/contracts/edge-production-state-guard.js';
import {
  createProductionBlockedAck,
  createValidationAck,
} from '../dist-c2/src/link/contracts/ingress-ack-lifecycle-contract.js';
import {
  getLinkSecurityReasonDefinition,
  isLinkSecurityReasonDlqEligible,
  isLinkSecurityReasonRetryable,
} from '../dist-c2/src/link/contracts/security-reason-taxonomy.js';

function createValidIntake(overrides = {}) {
  const base = {
    protocolVersion: 'v1',
    eventId: 'edge-event-001',
    traceId: 'trace-001',
    correlationId: 'corr-001',
    recordType: 'telemetry',
    occurredAt: '2026-06-20T00:00:00.000Z',
    receivedAt: '2026-06-20T00:00:01.000Z',
    payloadHash: 'sha256:example',
    normalizedPayload: {
      pointId: 'P-001',
      value: 1,
      quality: 'GOOD',
    },
    source: {
      gatewayId: 'gw-001',
      edgeId: 'edge-001',
      siteId: 'site-001',
      tenantId: 'tenant-001',
      sourceSystem: 'synthetic',
      connectorType: 'file',
      adapterType: 'readonly',
    },
    decisionState: 'BLOCKED_PRODUCTION_NOT_APPROVED',
    productionState: createDefaultBlockedEdgeProductionState(),
    evidenceRefs: [
      {
        evidenceId: 'evidence-001',
        evidenceType: 'handoff',
        sourcePath: 'AN_VANTARIS_EDGE/evidence/EDGE_HANDOFF_00_FINAL_EDGE_CLOSURE_AND_LINK_HANDOFF.md',
      },
    ],
  };

  return {
    ...base,
    ...overrides,
    source: {
      ...base.source,
      ...(overrides.source ?? {}),
    },
    productionState: {
      ...base.productionState,
      ...(overrides.productionState ?? {}),
    },
  };
}

const validIntake = createValidIntake();
const validation = validateEdgeHandoffIntakeContract(validIntake);
assert.equal(validation.valid, true);
assert.deepEqual(validation.reasons, []);

const validationAck = createValidationAck(validIntake, validation);
assert.equal(validationAck.status, 'VALIDATED');
assert.equal(validationAck.reasonCode, 'LINK_INGRESS_VALIDATED');
assert.equal(validationAck.eventId, validIntake.eventId);
assert.equal(validationAck.traceId, validIntake.traceId);
assert.equal(validationAck.gatewayId, validIntake.source.gatewayId);

const defaultGuard = evaluateEdgeProductionStateGuard(validIntake.productionState);
assert.equal(defaultGuard.allowed, false);
assert.equal(defaultGuard.code, 'LINK_EDGE_RUNTIME_NOT_ENABLED');

const blockedAck = createProductionBlockedAck(validIntake, defaultGuard);
assert.equal(blockedAck.status, 'BLOCKED');
assert.equal(blockedAck.reasonCode, 'LINK_EDGE_RUNTIME_NOT_ENABLED');

const writebackIntake = createValidIntake({
  productionState: {
    runtimeEnabled: true,
    pilotApproved: true,
    productionApproved: true,
    writebackRequested: true,
    productionDeliveryAllowed: true,
    reason: 'EDGE_WRITEBACK_PROHIBITED',
  },
});
const writebackValidation = validateEdgeHandoffIntakeContract(writebackIntake);
assert.equal(writebackValidation.valid, false);
assert.ok(writebackValidation.reasons.includes('writeback is prohibited'));

const approvedLookingState = createValidIntake({
  productionState: {
    runtimeEnabled: true,
    pilotApproved: true,
    productionApproved: true,
    writebackRequested: false,
    productionDeliveryAllowed: true,
    reason: 'EDGE_PRODUCTION_DELIVERY_BLOCKED',
  },
});
const c2Guard = assertEdgeProductionDeliveryBlockedForC2(approvedLookingState.productionState);
assert.equal(c2Guard.allowed, false);
assert.equal(c2Guard.code, 'LINK_EDGE_PRODUCTION_DELIVERY_BLOCKED');

const missingGateway = createValidIntake({
  source: {
    gatewayId: '',
  },
});
const missingGatewayValidation = validateEdgeHandoffIntakeContract(missingGateway);
assert.equal(missingGatewayValidation.valid, false);
assert.ok(missingGatewayValidation.reasons.includes('source.gatewayId is required'));

const missingEventId = createValidIntake({
  eventId: '',
});
const missingEventIdValidation = validateEdgeHandoffIntakeContract(missingEventId);
assert.equal(missingEventIdValidation.valid, false);
assert.ok(missingEventIdValidation.reasons.includes('eventId is required'));

const missingTraceId = createValidIntake({
  traceId: '',
});
const missingTraceIdValidation = validateEdgeHandoffIntakeContract(missingTraceId);
assert.equal(missingTraceIdValidation.valid, false);
assert.ok(missingTraceIdValidation.reasons.includes('traceId is required'));

const signatureReason = getLinkSecurityReasonDefinition('LINK_SECURITY_SIGNATURE_INVALID');
assert.equal(signatureReason.severity, 'CRITICAL');
assert.equal(isLinkSecurityReasonDlqEligible('LINK_SECURITY_SIGNATURE_INVALID'), true);
assert.equal(isLinkSecurityReasonRetryable('LINK_SECURITY_SIGNATURE_INVALID'), false);

const backpressureReason = getLinkSecurityReasonDefinition('LINK_QUEUE_BACKPRESSURE');
assert.equal(backpressureReason.retryable, true);
assert.equal(backpressureReason.dlqEligible, true);

console.log('LINK_C2_05_INGRESS_CONTRACT_VALIDATION_HARNESS_PASS');
