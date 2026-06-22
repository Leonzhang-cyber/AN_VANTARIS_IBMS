// AUTO-GENERATED FROM AN_VANTARIS_Contracts. DO NOT EDIT.

export interface TransportEnvelope {
  readonly messageId: string;
  readonly protocolVersion: string;
  readonly signature: string;
}

export interface TransportEnqueueResult {
  readonly accepted: boolean;
  readonly queueId?: string;
}

export interface TransportBackpressureSignal {
  readonly reason: string;
  readonly retryAfterMs?: number;
}
