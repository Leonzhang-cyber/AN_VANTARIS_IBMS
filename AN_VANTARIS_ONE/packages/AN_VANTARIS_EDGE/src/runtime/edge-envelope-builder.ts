import { mkdirSync, writeFileSync } from 'node:fs';
import { dirname } from 'node:path';

import type {
  EdgeEnvelope,
  EdgeEnvelopeBuildInput,
  EdgeEnvelopeExportResult,
  EdgeEnvelopeValidationResult,
  QualityCounter,
} from './edge-envelope-types.js';

function nowIso(): string {
  return new Date().toISOString();
}

function buildEnvelopeId(connectorId: string): string {
  return `env-${connectorId}-${Date.now()}`;
}

function countQuality(input: EdgeEnvelopeBuildInput): QualityCounter {
  const counter: QualityCounter = {
    good: 0,
    uncertain: 0,
    bad: 0,
  };
  for (const point of input.points) {
    counter[point.quality] += 1;
  }
  for (const event of input.events) {
    counter[event.quality] += 1;
  }
  return counter;
}

export function buildEdgeEnvelopeFromNormalizedSamples(input: EdgeEnvelopeBuildInput): EdgeEnvelope {
  const quality = countQuality(input);
  return {
    header: {
      envelopeId: buildEnvelopeId(input.connectorId),
      schemaVersion: 'edge-envelope.v1',
      edgeNodeId: input.edgeNodeId,
      connectorId: input.connectorId,
      protocol: input.protocol,
      sourceRef: input.sourceRef,
      createdAt: nowIso(),
      payloadType: 'normalized.samples',
    },
    payload: {
      points: input.points,
      events: input.events,
    },
    trace: {
      traceId: `trace-${input.connectorId}-${Date.now()}`,
      spanId: `span-${Math.random().toString(16).slice(2, 10)}`,
      generatedBy: 'edge-envelope-builder',
      stage: 'local-normalization-envelope',
    },
    qualitySummary: {
      totalPoints: input.points.length,
      totalEvents: input.events.length,
      good: quality.good,
      uncertain: quality.uncertain,
      bad: quality.bad,
    },
  };
}

export function validateEdgeEnvelope(envelope: EdgeEnvelope): EdgeEnvelopeValidationResult {
  const errors: string[] = [];
  const warnings: string[] = [];
  if (!envelope.header.envelopeId) errors.push('header.envelopeId is required');
  if (!envelope.header.schemaVersion) errors.push('header.schemaVersion is required');
  if (!envelope.header.edgeNodeId) errors.push('header.edgeNodeId is required');
  if (!envelope.header.connectorId) errors.push('header.connectorId is required');
  if (!envelope.header.protocol) errors.push('header.protocol is required');
  if (!envelope.header.createdAt) errors.push('header.createdAt is required');
  if (envelope.payload.points.length == 0 && envelope.payload.events.length == 0) {
    warnings.push('envelope payload is empty');
  }
  return {
    valid: errors.length == 0,
    errors,
    warnings,
  };
}

export function exportEdgeEnvelopeEvidence(path: string, envelope: EdgeEnvelope): EdgeEnvelopeExportResult {
  mkdirSync(dirname(path), { recursive: true });
  const content = JSON.stringify(envelope, null, 2) + '\n';
  writeFileSync(path, content, 'utf8');
  return {
    path,
    bytes: Buffer.byteLength(content, 'utf8'),
    exportedAt: nowIso(),
  };
}
