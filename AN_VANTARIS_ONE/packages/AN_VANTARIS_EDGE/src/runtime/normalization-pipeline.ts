import { mkdirSync, writeFileSync } from 'node:fs';
import { dirname } from 'node:path';

import type { ConnectorProtocol } from './connector-types.js';
import type { NormalizedSamplePlaceholder, ProtocolPluginPollResult } from './protocol-plugin-types.js';
import type {
  NormalizationError,
  NormalizationResult,
  NormalizationWarning,
  NormalizedEventSample,
  NormalizedPointSample,
  NormalizedQuality,
  NormalizedSampleMetadata,
  NormalizedSampleSource,
} from './normalization-types.js';

function nowIso(): string {
  return new Date().toISOString();
}

function asNumber(value: unknown, fallback = 0): number {
  return typeof value == 'number' && Number.isFinite(value) ? value : fallback;
}

function asString(value: unknown, fallback = ''): string {
  return typeof value == 'string' ? value : fallback;
}

function detectQuality(payload: Record<string, unknown>): NormalizedQuality {
  const quality = asString(payload.quality, 'good').toLowerCase();
  if (quality == 'bad') return 'bad';
  if (quality == 'uncertain') return 'uncertain';
  return 'good';
}

function buildSource(pluginId: string, sample: NormalizedSamplePlaceholder): NormalizedSampleSource {
  return {
    connectorId: sample.connectorId,
    sourceSystemId: sample.sourceSystemId,
    protocol: sample.protocol,
    pluginId,
    sampleId: sample.sampleId,
  };
}

function buildMetadata(payload: Record<string, unknown>, sequence: number): NormalizedSampleMetadata {
  return {
    normalizedAt: nowIso(),
    synthetic: true,
    sequence,
    tags: [asString(payload.synthetic, 'true') == 'true' ? 'synthetic' : 'normalized'],
  };
}

export function normalizeSyntheticSample(
  pluginId: string,
  sample: NormalizedSamplePlaceholder,
  sequence: number,
): { point?: NormalizedPointSample; event?: NormalizedEventSample; warning?: NormalizationWarning } {
  const payload = sample.payload;
  const source = buildSource(pluginId, sample);
  const metadata = buildMetadata(payload, sequence);
  const quality = detectQuality(payload);

  if (sample.sampleType == 'event' || sample.sampleType == 'alarm') {
    return {
      event: {
        sampleId: sample.sampleId,
        eventType: sample.sampleType == 'alarm' ? 'alarm.raised' : 'event.created',
        severity: sample.sampleType == 'alarm' ? 'critical' : 'info',
        message: asString(payload.message, `${sample.sampleType}.synthetic`),
        quality,
        timestamp: sample.timestamp,
        source,
        metadata,
      },
    };
  }

  if (sample.sampleType == 'health') {
    return {
      event: {
        sampleId: sample.sampleId,
        eventType: 'device.health.updated',
        severity: 'warning',
        message: asString(payload.message, 'synthetic health update'),
        quality,
        timestamp: sample.timestamp,
        source,
        metadata,
      },
      warning: {
        code: 'health_sample_normalized_as_event',
        message: 'health sample normalized to event envelope class',
        sampleId: sample.sampleId,
      },
    };
  }

  if (sample.sampleType == 'evidence') {
    return {
      event: {
        sampleId: sample.sampleId,
        eventType: 'evidence.captured',
        severity: 'info',
        message: asString(payload.message, 'synthetic evidence sample'),
        quality,
        timestamp: sample.timestamp,
        source,
        metadata,
      },
    };
  }

  const rawValue = payload.value;
  const numberValue = asNumber(rawValue, NaN);
  const hasNumeric = Number.isFinite(numberValue);

  return {
    point: {
      sampleId: sample.sampleId,
      pointRef: asString(payload.pointRef, `${sample.connectorId}.synthetic.point`),
      value: hasNumeric ? numberValue : asString(rawValue, 'synthetic'),
      valueType: hasNumeric ? 'float' : 'string',
      unit: asString(payload.unit, 'synthetic-unit'),
      quality,
      timestamp: sample.timestamp,
      source,
      metadata,
    },
  };
}

export function validateNormalizedPointSample(sample: NormalizedPointSample): { valid: boolean; errors: readonly string[] } {
  const errors: string[] = [];
  if (!sample.sampleId) errors.push('sampleId is required');
  if (!sample.pointRef) errors.push('pointRef is required');
  if (!sample.timestamp) errors.push('timestamp is required');
  if (!sample.source.connectorId) errors.push('source.connectorId is required');
  if (!sample.source.pluginId) errors.push('source.pluginId is required');
  return { valid: errors.length == 0, errors };
}

export function validateNormalizedEventSample(sample: NormalizedEventSample): { valid: boolean; errors: readonly string[] } {
  const errors: string[] = [];
  if (!sample.sampleId) errors.push('sampleId is required');
  if (!sample.eventType) errors.push('eventType is required');
  if (!sample.message) errors.push('message is required');
  if (!sample.timestamp) errors.push('timestamp is required');
  if (!sample.source.connectorId) errors.push('source.connectorId is required');
  if (!sample.source.pluginId) errors.push('source.pluginId is required');
  return { valid: errors.length == 0, errors };
}

export function normalizeProtocolPollResult(pollResult: ProtocolPluginPollResult): NormalizationResult {
  const normalizedPoints: NormalizedPointSample[] = [];
  const normalizedEvents: NormalizedEventSample[] = [];
  const warnings: NormalizationWarning[] = [];
  const errors: NormalizationError[] = [];

  pollResult.samples.forEach((sample, index) => {
    const normalized = normalizeSyntheticSample(pollResult.pluginId, sample, index + 1);
    if (normalized.warning) warnings.push(normalized.warning);
    if (normalized.point) {
      const check = validateNormalizedPointSample(normalized.point);
      if (!check.valid) {
        errors.push({
          code: 'invalid_normalized_point',
          message: check.errors.join('; '),
          sampleId: normalized.point.sampleId,
        });
      } else {
        normalizedPoints.push(normalized.point);
      }
    }
    if (normalized.event) {
      const check = validateNormalizedEventSample(normalized.event);
      if (!check.valid) {
        errors.push({
          code: 'invalid_normalized_event',
          message: check.errors.join('; '),
          sampleId: normalized.event.sampleId,
        });
      } else {
        normalizedEvents.push(normalized.event);
      }
    }
  });

  return {
    pluginId: pollResult.pluginId,
    connectorId: pollResult.connectorId,
    protocol: pollResult.protocol as ConnectorProtocol,
    normalizedPoints,
    normalizedEvents,
    warnings,
    errors,
    generatedAt: nowIso(),
    sourcePollResult: {
      connectorId: pollResult.connectorId,
      protocol: pollResult.protocol,
    },
  };
}

export function exportNormalizationSnapshot(path: string, payload: NormalizationResult): void {
  mkdirSync(dirname(path), { recursive: true });
  writeFileSync(path, JSON.stringify(payload, null, 2) + '\n', 'utf8');
}
