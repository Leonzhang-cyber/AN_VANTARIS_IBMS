import { randomUUID } from 'node:crypto';

import type { AuditPlaceholderEvent } from './types.js';

export class AuditPlaceholderStream {
  private readonly events: AuditPlaceholderEvent[] = [];

  public emit(input: {
    edgeId: string;
    eventType: string;
    action: string;
    result: 'ok' | 'error';
    details: Record<string, unknown>;
  }): AuditPlaceholderEvent {
    const event: AuditPlaceholderEvent = {
      eventId: randomUUID(),
      eventType: input.eventType,
      actor: 'edge-runtime',
      edgeId: input.edgeId,
      timestamp: new Date().toISOString(),
      action: input.action,
      result: input.result,
      details: input.details,
    };
    this.events.push(event);
    return event;
  }

  public list(): readonly AuditPlaceholderEvent[] {
    return [...this.events];
  }
}
