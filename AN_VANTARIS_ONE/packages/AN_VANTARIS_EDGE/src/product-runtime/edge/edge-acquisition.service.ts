/**
 * S01 EDGE — Acquisition Layer (untrusted ingestion boundary).
 * Ingestion + buffer + HMAC + heartbeat. All incoming events are untrusted.
 * Structural sanitization only — no business-field validation.
 * Zone transition enforcement is owned exclusively by S02 LINK ingress.
 * OUTPUT → S02 LINK as WireEvent v1.0 or v1.1.
 */

import { randomUUID } from 'node:crypto';

import { freezeWireEvent } from '../../generated/contracts/wire-event-immutability.js';
import type {
  WireEventInput,
  WireEventV1,
  WireEventV1_1,
  WireTransportEvent,
} from '../../generated/contracts/wire-event-v1.js';
import { WIRE_PROTOCOL_VERSION, WIRE_PROTOCOL_VERSION_V1_1 } from '../../generated/contracts/wire-event-v1.js';
import { normalizeWireTimestampUtc, serializeWireEvent } from '../../generated/contracts/wire-serializer-v1.js';
import { mapEdgeToLink } from '../../generated/protocol/edge-to-link.mapper.js';
import type { LinkHandoffEvent } from '../../generated/protocol/edge-to-link.mapper.js';
import { buildLifecycle, wireObserver, type WireObserver } from './edge-observability.stub.js';
import { attachWireEventSignature, buildEdgeLinkHeaders } from '../../generated/security/edge-link-security-headers.js';
import { createTraceContext } from '../../generated/security/wire-trace-context.js';
import { createEdgeWalBuffer, EdgeWalBuffer } from './edge-buffer.service.js';
import {
  createNoopEdgeHandoffPublisher,
  type EdgeHandoffPublishEnvelope,
  type EdgeHandoffPublisher,
  type EdgeHandoffPublishResult,
} from './edge-handoff-publisher.js';

export type EdgeEvent = WireTransportEvent;
export type EdgeEventInput = WireEventInput;

export interface EdgeAcquisitionContext {
  readonly machineId: string;
  readonly credentialRef: string;
  readonly signingSecret: string;
}

export class EdgeAcquisitionService {
  public constructor(
    private readonly handoffPublisher: EdgeHandoffPublisher<EdgeHandoffPublishEnvelope> =
      createNoopEdgeHandoffPublisher(),
    private readonly wal: EdgeWalBuffer = createEdgeWalBuffer(),
    private readonly context: EdgeAcquisitionContext,
    private readonly observer: WireObserver = wireObserver,
  ) {}

  public ingest(input: WireEventInput): WireEventV1 {
    this.assertStructuralGatewayId(input.gatewayId);

    const timestamp = normalizeWireTimestampUtc(input.timestamp);
    const unsigned = {
      protocolVersion: WIRE_PROTOCOL_VERSION,
      eventId: randomUUID(),
      gatewayId: input.gatewayId.trim(),
      eventType: input.eventType,
      timestamp,
      payload: input.payload,
      ...(input.dedupeKey !== undefined ? { dedupeKey: input.dedupeKey } : {}),
      ...(input.traceId !== undefined ? { traceId: input.traceId } : {}),
    } as Omit<WireEventV1, 'signature'>;

    const signed = attachWireEventSignature(unsigned, this.context.signingSecret) as WireEventV1;
    const event = freezeWireEvent(signed);
    this.observer.observeEdge(event);
    this.wal.append(event);
    return event;
  }

  public ingestObserved(input: WireEventInput): WireEventV1_1 {
    this.assertStructuralGatewayId(input.gatewayId);

    const edgeReceivedAt = new Date().toISOString();
    const timestamp = normalizeWireTimestampUtc(input.timestamp ?? edgeReceivedAt);
    const trace = createTraceContext(input.traceId);

    const unsigned = {
      protocolVersion: WIRE_PROTOCOL_VERSION_V1_1,
      eventId: randomUUID(),
      gatewayId: input.gatewayId.trim(),
      eventType: input.eventType,
      timestamp,
      payload: input.payload,
      traceId: trace.traceId,
      spanId: trace.spanId,
      lifecycle: buildLifecycle(edgeReceivedAt),
      ...(input.dedupeKey !== undefined ? { dedupeKey: input.dedupeKey } : {}),
      ...(trace.parentSpanId !== undefined ? { parentSpanId: trace.parentSpanId } : {}),
    } as Omit<WireEventV1_1, 'signature'>;

    const signed = attachWireEventSignature(unsigned, this.context.signingSecret) as WireEventV1_1;
    const event = freezeWireEvent(signed);
    this.observer.observeEdge(event);
    this.wal.append(event);
    return event;
  }

  public async forwardToLink(event: WireTransportEvent): Promise<EdgeHandoffPublishResult> {
    const handoff = mapEdgeToLink(event);
    const body = serializeWireEvent(handoff);
    const headers = buildEdgeLinkHeaders(
      this.context.machineId,
      this.context.credentialRef,
      handoff.timestamp,
      handoff.signature,
    );

    const result = await this.handoffPublisher.publish({
      event,
      handoff,
      headers,
      body,
    });

    if (result.status === 'accepted') {
      this.observer.observeLink(handoff);
    }

    return result;
  }

  public async ingestAndForward(input: WireEventInput): Promise<{
    readonly event: WireEventV1;
    readonly handoff: LinkHandoffEvent;
    readonly linkResult: EdgeHandoffPublishResult;
  }> {
    const event = this.ingest(input);
    const handoff = mapEdgeToLink(event);
    const linkResult = await this.forwardToLink(event);
    return { event, handoff, linkResult };
  }

  public async ingestObservedAndForward(input: WireEventInput): Promise<{
    readonly event: WireEventV1_1;
    readonly handoff: LinkHandoffEvent;
    readonly linkResult: EdgeHandoffPublishResult;
  }> {
    const event = this.ingestObserved(input);
    const handoff = mapEdgeToLink(event);
    const linkResult = await this.forwardToLink(event);
    return { event, handoff, linkResult };
  }

  public replayWal(): readonly WireTransportEvent[] {
    return this.wal.replay().map((entry) => entry.event);
  }

  /** Structural boundary check only — no business-field validation. */
  private assertStructuralGatewayId(gatewayId: string): void {
    if (!gatewayId.trim()) {
      throw new Error('gatewayId is required at S01 EDGE boundary.');
    }
  }
}

export function createEdgeAcquisitionService(
  context: EdgeAcquisitionContext,
  handoffPublisher?: EdgeHandoffPublisher<EdgeHandoffPublishEnvelope>,
  observer?: WireObserver,
): EdgeAcquisitionService {
  return new EdgeAcquisitionService(
    handoffPublisher ?? createNoopEdgeHandoffPublisher(),
    createEdgeWalBuffer(),
    context,
    observer ?? wireObserver,
  );
}
