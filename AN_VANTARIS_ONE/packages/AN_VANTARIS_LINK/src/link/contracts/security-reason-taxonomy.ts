/**
 * LINK-C2-04 — security reason taxonomy.
 *
 * LINK-owned reason taxonomy for ingress security, schema validation,
 * EDGE production blocking, queue backpressure, and future DLQ routing.
 *
 * This taxonomy does not enable production delivery.
 */

export type LinkSecurityReasonSeverity = 'INFO' | 'WARN' | 'ERROR' | 'CRITICAL';

export type LinkSecurityReasonCategory =
  | 'INGRESS'
  | 'SECURITY'
  | 'SCHEMA'
  | 'PROTOCOL'
  | 'EDGE_STATE'
  | 'QUEUE'
  | 'DELIVERY'
  | 'DLQ'
  | 'POLICY';

export type LinkSecurityReasonCode =
  | 'LINK_INGRESS_RECEIVED'
  | 'LINK_INGRESS_VALIDATED'
  | 'LINK_INGRESS_QUEUED'
  | 'LINK_SECURITY_SIGNATURE_INVALID'
  | 'LINK_SECURITY_TIMESTAMP_SKEW'
  | 'LINK_SECURITY_REPLAY_DETECTED'
  | 'LINK_SECURITY_GATEWAY_MISSING'
  | 'LINK_SECURITY_GATEWAY_NOT_ALLOWED'
  | 'LINK_SCHEMA_INVALID'
  | 'LINK_PROTOCOL_UNSUPPORTED'
  | 'LINK_EDGE_RUNTIME_NOT_ENABLED'
  | 'LINK_EDGE_PILOT_NOT_APPROVED'
  | 'LINK_EDGE_PRODUCTION_NOT_APPROVED'
  | 'LINK_EDGE_PRODUCTION_BLOCKED'
  | 'LINK_EDGE_WRITEBACK_PROHIBITED'
  | 'LINK_QUEUE_BACKPRESSURE'
  | 'LINK_DELIVERY_BLOCKED'
  | 'LINK_DLQ_ROUTED'
  | 'LINK_POLICY_BLOCKED';

export interface LinkSecurityReasonDefinition {
  readonly code: LinkSecurityReasonCode;
  readonly category: LinkSecurityReasonCategory;
  readonly severity: LinkSecurityReasonSeverity;
  readonly retryable: boolean;
  readonly dlqEligible: boolean;
  readonly description: string;
}

export const LINK_SECURITY_REASON_DEFINITIONS: Readonly<
  Record<LinkSecurityReasonCode, LinkSecurityReasonDefinition>
> = {
  LINK_INGRESS_RECEIVED: {
    code: 'LINK_INGRESS_RECEIVED',
    category: 'INGRESS',
    severity: 'INFO',
    retryable: false,
    dlqEligible: false,
    description: 'LINK ingress received the event.',
  },
  LINK_INGRESS_VALIDATED: {
    code: 'LINK_INGRESS_VALIDATED',
    category: 'INGRESS',
    severity: 'INFO',
    retryable: false,
    dlqEligible: false,
    description: 'LINK ingress validated the event contract.',
  },
  LINK_INGRESS_QUEUED: {
    code: 'LINK_INGRESS_QUEUED',
    category: 'QUEUE',
    severity: 'INFO',
    retryable: false,
    dlqEligible: false,
    description: 'LINK ingress queued the event.',
  },
  LINK_SECURITY_SIGNATURE_INVALID: {
    code: 'LINK_SECURITY_SIGNATURE_INVALID',
    category: 'SECURITY',
    severity: 'CRITICAL',
    retryable: false,
    dlqEligible: true,
    description: 'LINK rejected the event because the signature is invalid.',
  },
  LINK_SECURITY_TIMESTAMP_SKEW: {
    code: 'LINK_SECURITY_TIMESTAMP_SKEW',
    category: 'SECURITY',
    severity: 'ERROR',
    retryable: true,
    dlqEligible: true,
    description: 'LINK rejected the event because timestamp skew exceeds policy.',
  },
  LINK_SECURITY_REPLAY_DETECTED: {
    code: 'LINK_SECURITY_REPLAY_DETECTED',
    category: 'SECURITY',
    severity: 'CRITICAL',
    retryable: false,
    dlqEligible: true,
    description: 'LINK rejected the event because replay was detected.',
  },
  LINK_SECURITY_GATEWAY_MISSING: {
    code: 'LINK_SECURITY_GATEWAY_MISSING',
    category: 'SECURITY',
    severity: 'ERROR',
    retryable: false,
    dlqEligible: true,
    description: 'LINK rejected the event because gateway identity is missing.',
  },
  LINK_SECURITY_GATEWAY_NOT_ALLOWED: {
    code: 'LINK_SECURITY_GATEWAY_NOT_ALLOWED',
    category: 'POLICY',
    severity: 'ERROR',
    retryable: false,
    dlqEligible: true,
    description: 'LINK rejected the event because gateway identity is not allowed.',
  },
  LINK_SCHEMA_INVALID: {
    code: 'LINK_SCHEMA_INVALID',
    category: 'SCHEMA',
    severity: 'ERROR',
    retryable: false,
    dlqEligible: true,
    description: 'LINK rejected the event because schema validation failed.',
  },
  LINK_PROTOCOL_UNSUPPORTED: {
    code: 'LINK_PROTOCOL_UNSUPPORTED',
    category: 'PROTOCOL',
    severity: 'ERROR',
    retryable: false,
    dlqEligible: true,
    description: 'LINK rejected the event because protocol version is unsupported.',
  },
  LINK_EDGE_RUNTIME_NOT_ENABLED: {
    code: 'LINK_EDGE_RUNTIME_NOT_ENABLED',
    category: 'EDGE_STATE',
    severity: 'WARN',
    retryable: false,
    dlqEligible: false,
    description: 'LINK blocked the event because EDGE runtime is not enabled.',
  },
  LINK_EDGE_PILOT_NOT_APPROVED: {
    code: 'LINK_EDGE_PILOT_NOT_APPROVED',
    category: 'EDGE_STATE',
    severity: 'WARN',
    retryable: false,
    dlqEligible: false,
    description: 'LINK blocked the event because EDGE pilot is not approved.',
  },
  LINK_EDGE_PRODUCTION_NOT_APPROVED: {
    code: 'LINK_EDGE_PRODUCTION_NOT_APPROVED',
    category: 'EDGE_STATE',
    severity: 'WARN',
    retryable: false,
    dlqEligible: false,
    description: 'LINK blocked the event because EDGE production is not approved.',
  },
  LINK_EDGE_PRODUCTION_BLOCKED: {
    code: 'LINK_EDGE_PRODUCTION_BLOCKED',
    category: 'EDGE_STATE',
    severity: 'WARN',
    retryable: false,
    dlqEligible: false,
    description: 'LINK blocked production delivery by EDGE state policy.',
  },
  LINK_EDGE_WRITEBACK_PROHIBITED: {
    code: 'LINK_EDGE_WRITEBACK_PROHIBITED',
    category: 'EDGE_STATE',
    severity: 'CRITICAL',
    retryable: false,
    dlqEligible: true,
    description: 'LINK blocked the event because writeback is prohibited.',
  },
  LINK_QUEUE_BACKPRESSURE: {
    code: 'LINK_QUEUE_BACKPRESSURE',
    category: 'QUEUE',
    severity: 'ERROR',
    retryable: true,
    dlqEligible: true,
    description: 'LINK rejected or dropped the event because queue backpressure was reached.',
  },
  LINK_DELIVERY_BLOCKED: {
    code: 'LINK_DELIVERY_BLOCKED',
    category: 'DELIVERY',
    severity: 'WARN',
    retryable: false,
    dlqEligible: false,
    description: 'LINK blocked delivery because production delivery is not approved.',
  },
  LINK_DLQ_ROUTED: {
    code: 'LINK_DLQ_ROUTED',
    category: 'DLQ',
    severity: 'ERROR',
    retryable: false,
    dlqEligible: true,
    description: 'LINK routed the event to DLQ.',
  },
  LINK_POLICY_BLOCKED: {
    code: 'LINK_POLICY_BLOCKED',
    category: 'POLICY',
    severity: 'ERROR',
    retryable: false,
    dlqEligible: true,
    description: 'LINK blocked the event by policy.',
  },
};

export function getLinkSecurityReasonDefinition(
  code: LinkSecurityReasonCode,
): LinkSecurityReasonDefinition {
  return LINK_SECURITY_REASON_DEFINITIONS[code];
}

export function isLinkSecurityReasonDlqEligible(code: LinkSecurityReasonCode): boolean {
  return getLinkSecurityReasonDefinition(code).dlqEligible;
}

export function isLinkSecurityReasonRetryable(code: LinkSecurityReasonCode): boolean {
  return getLinkSecurityReasonDefinition(code).retryable;
}
