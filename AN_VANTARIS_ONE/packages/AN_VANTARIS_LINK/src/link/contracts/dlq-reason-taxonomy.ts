/**
 * LINK-C5-03 — DLQ reason taxonomy.
 *
 * LINK-owned DLQ taxonomy for security, schema, policy, delivery, retry,
 * replay, queue, and unknown failures.
 *
 * This contract does not enable production delivery.
 */

export type LinkDlqCategory =
  | 'SECURITY'
  | 'SCHEMA'
  | 'POLICY'
  | 'DELIVERY'
  | 'RETRY_EXHAUSTED'
  | 'REPLAY'
  | 'QUEUE'
  | 'UNKNOWN';

export type LinkDlqReasonCode =
  | 'LINK_SECURITY_SIGNATURE_INVALID'
  | 'LINK_SECURITY_TIMESTAMP_SKEW'
  | 'LINK_SECURITY_REPLAY_DETECTED'
  | 'LINK_SCHEMA_INVALID'
  | 'LINK_PROTOCOL_UNSUPPORTED'
  | 'LINK_POLICY_BLOCKED'
  | 'LINK_DELIVERY_PRODUCTION_BLOCKED'
  | 'LINK_DELIVERY_TARGET_UNAPPROVED'
  | 'LINK_DELIVERY_TARGET_REJECTED'
  | 'LINK_DELIVERY_TIMEOUT'
  | 'LINK_DELIVERY_5XX_RETRYABLE_EXHAUSTED'
  | 'LINK_DELIVERY_RETRY_EXHAUSTED'
  | 'LINK_REPLAY_WINDOW_EXCEEDED'
  | 'LINK_REPLAY_BUDGET_EXHAUSTED'
  | 'LINK_QUEUE_EXPIRED'
  | 'LINK_QUEUE_BACKPRESSURE'
  | 'LINK_DUPLICATE_FINAL'
  | 'LINK_UNKNOWN_FAILURE';

export type LinkDlqSeverity = 'INFO' | 'WARN' | 'ERROR' | 'CRITICAL';

export interface LinkDlqReasonDefinition {
  readonly code: LinkDlqReasonCode;
  readonly category: LinkDlqCategory;
  readonly severity: LinkDlqSeverity;
  readonly retryable: boolean;
  readonly replayEligible: boolean;
  readonly operatorActionRequired: boolean;
  readonly description: string;
}

export const LINK_DLQ_REASON_DEFINITIONS: Readonly<
  Record<LinkDlqReasonCode, LinkDlqReasonDefinition>
> = {
  LINK_SECURITY_SIGNATURE_INVALID: {
    code: 'LINK_SECURITY_SIGNATURE_INVALID',
    category: 'SECURITY',
    severity: 'CRITICAL',
    retryable: false,
    replayEligible: false,
    operatorActionRequired: true,
    description: 'Invalid signature at LINK ingress.',
  },
  LINK_SECURITY_TIMESTAMP_SKEW: {
    code: 'LINK_SECURITY_TIMESTAMP_SKEW',
    category: 'SECURITY',
    severity: 'ERROR',
    retryable: false,
    replayEligible: true,
    operatorActionRequired: true,
    description: 'Timestamp skew exceeded allowed policy.',
  },
  LINK_SECURITY_REPLAY_DETECTED: {
    code: 'LINK_SECURITY_REPLAY_DETECTED',
    category: 'SECURITY',
    severity: 'CRITICAL',
    retryable: false,
    replayEligible: false,
    operatorActionRequired: true,
    description: 'Replay attempt detected at LINK ingress.',
  },
  LINK_SCHEMA_INVALID: {
    code: 'LINK_SCHEMA_INVALID',
    category: 'SCHEMA',
    severity: 'ERROR',
    retryable: false,
    replayEligible: false,
    operatorActionRequired: true,
    description: 'Payload failed schema validation.',
  },
  LINK_PROTOCOL_UNSUPPORTED: {
    code: 'LINK_PROTOCOL_UNSUPPORTED',
    category: 'SCHEMA',
    severity: 'ERROR',
    retryable: false,
    replayEligible: false,
    operatorActionRequired: true,
    description: 'Unsupported protocol or contract version.',
  },
  LINK_POLICY_BLOCKED: {
    code: 'LINK_POLICY_BLOCKED',
    category: 'POLICY',
    severity: 'ERROR',
    retryable: false,
    replayEligible: false,
    operatorActionRequired: true,
    description: 'Delivery or ingress was blocked by policy.',
  },
  LINK_DELIVERY_PRODUCTION_BLOCKED: {
    code: 'LINK_DELIVERY_PRODUCTION_BLOCKED',
    category: 'POLICY',
    severity: 'WARN',
    retryable: false,
    replayEligible: false,
    operatorActionRequired: false,
    description: 'Production delivery remains blocked by current stage.',
  },
  LINK_DELIVERY_TARGET_UNAPPROVED: {
    code: 'LINK_DELIVERY_TARGET_UNAPPROVED',
    category: 'POLICY',
    severity: 'ERROR',
    retryable: false,
    replayEligible: false,
    operatorActionRequired: true,
    description: 'Delivery target is not approved.',
  },
  LINK_DELIVERY_TARGET_REJECTED: {
    code: 'LINK_DELIVERY_TARGET_REJECTED',
    category: 'DELIVERY',
    severity: 'ERROR',
    retryable: false,
    replayEligible: false,
    operatorActionRequired: true,
    description: 'Delivery target rejected the event.',
  },
  LINK_DELIVERY_TIMEOUT: {
    code: 'LINK_DELIVERY_TIMEOUT',
    category: 'DELIVERY',
    severity: 'WARN',
    retryable: true,
    replayEligible: true,
    operatorActionRequired: false,
    description: 'Delivery attempt timed out.',
  },
  LINK_DELIVERY_5XX_RETRYABLE_EXHAUSTED: {
    code: 'LINK_DELIVERY_5XX_RETRYABLE_EXHAUSTED',
    category: 'RETRY_EXHAUSTED',
    severity: 'ERROR',
    retryable: false,
    replayEligible: true,
    operatorActionRequired: true,
    description: 'Retryable 5xx delivery failure exhausted retry policy.',
  },
  LINK_DELIVERY_RETRY_EXHAUSTED: {
    code: 'LINK_DELIVERY_RETRY_EXHAUSTED',
    category: 'RETRY_EXHAUSTED',
    severity: 'ERROR',
    retryable: false,
    replayEligible: true,
    operatorActionRequired: true,
    description: 'Delivery retry attempts were exhausted.',
  },
  LINK_REPLAY_WINDOW_EXCEEDED: {
    code: 'LINK_REPLAY_WINDOW_EXCEEDED',
    category: 'REPLAY',
    severity: 'ERROR',
    retryable: false,
    replayEligible: false,
    operatorActionRequired: true,
    description: 'Replay request exceeded permitted replay window.',
  },
  LINK_REPLAY_BUDGET_EXHAUSTED: {
    code: 'LINK_REPLAY_BUDGET_EXHAUSTED',
    category: 'REPLAY',
    severity: 'ERROR',
    retryable: false,
    replayEligible: false,
    operatorActionRequired: true,
    description: 'Replay retry budget was exhausted.',
  },
  LINK_QUEUE_EXPIRED: {
    code: 'LINK_QUEUE_EXPIRED',
    category: 'QUEUE',
    severity: 'ERROR',
    retryable: false,
    replayEligible: false,
    operatorActionRequired: true,
    description: 'Queue item expired before delivery.',
  },
  LINK_QUEUE_BACKPRESSURE: {
    code: 'LINK_QUEUE_BACKPRESSURE',
    category: 'QUEUE',
    severity: 'ERROR',
    retryable: true,
    replayEligible: true,
    operatorActionRequired: false,
    description: 'Queue backpressure prevented normal processing.',
  },
  LINK_DUPLICATE_FINAL: {
    code: 'LINK_DUPLICATE_FINAL',
    category: 'POLICY',
    severity: 'INFO',
    retryable: false,
    replayEligible: false,
    operatorActionRequired: false,
    description: 'Duplicate event was finalized without replay.',
  },
  LINK_UNKNOWN_FAILURE: {
    code: 'LINK_UNKNOWN_FAILURE',
    category: 'UNKNOWN',
    severity: 'ERROR',
    retryable: false,
    replayEligible: false,
    operatorActionRequired: true,
    description: 'Unknown LINK failure.',
  },
};

export function getLinkDlqReasonDefinition(code: LinkDlqReasonCode): LinkDlqReasonDefinition {
  return LINK_DLQ_REASON_DEFINITIONS[code];
}

export function isLinkDlqReasonRetryable(code: LinkDlqReasonCode): boolean {
  return getLinkDlqReasonDefinition(code).retryable;
}

export function isLinkDlqReasonReplayEligible(code: LinkDlqReasonCode): boolean {
  return getLinkDlqReasonDefinition(code).replayEligible;
}

export function isLinkDlqReasonOperatorActionRequired(code: LinkDlqReasonCode): boolean {
  return getLinkDlqReasonDefinition(code).operatorActionRequired;
}
