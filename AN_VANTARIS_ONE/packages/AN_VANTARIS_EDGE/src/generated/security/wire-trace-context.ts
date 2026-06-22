// AUTO-GENERATED FROM AN_VANTARIS_Contracts. DO NOT EDIT.

import { randomUUID } from 'node:crypto';

export interface WireTraceContext {
  readonly traceId: string;
  readonly spanId: string;
  readonly parentSpanId?: string;
}

export function createTraceContext(existingTraceId?: string): WireTraceContext {
  return {
    traceId: existingTraceId?.trim() || randomUUID(),
    spanId: randomUUID(),
  };
}
