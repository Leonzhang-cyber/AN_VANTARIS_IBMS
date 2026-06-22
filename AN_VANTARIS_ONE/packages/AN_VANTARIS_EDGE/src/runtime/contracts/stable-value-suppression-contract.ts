/**
 * EDGE-C8-02 — Stable value suppression contract.
 *
 * EDGE-owned contract for reducing repeated unchanged telemetry before LINK.
 *
 * This contract does not enable runtime, pilot, production, writeback, or direct
 * UFMS DB access.
 */

export type EdgeStableSampleMode =
  | 'RAW_EVERY_SAMPLE'
  | 'CHANGE_ONLY'
  | 'DEADBAND'
  | 'HEARTBEAT'
  | 'AGGREGATED_REPEAT'
  | 'FULL_SNAPSHOT';

export type EdgeStableChangeReason =
  | 'FIRST_SAMPLE'
  | 'VALUE_CHANGED'
  | 'QUALITY_CHANGED'
  | 'STATUS_CHANGED'
  | 'DEADBAND_EXCEEDED'
  | 'HEARTBEAT_DUE'
  | 'RECONNECT_FIRST_SAMPLE'
  | 'FULL_SNAPSHOT_REQUESTED'
  | 'ALARM_NEW_ACTIVE'
  | 'ALARM_CLEARED'
  | 'ALARM_SEVERITY_CHANGED'
  | 'ALARM_ACK_CHANGED'
  | 'ALARM_REPEAT_AGGREGATED'
  | 'EVIDENCE_STATE_CHANGED'
  | 'CONFIG_VERSION_CHANGED'
  | 'SUPPRESSED_NO_CHANGE';

export type EdgeStableDeadbandMode = 'DISABLED' | 'ABSOLUTE' | 'PERCENT';

export type EdgeStableRecordType =
  | 'telemetry'
  | 'analog'
  | 'digital'
  | 'status'
  | 'alarm'
  | 'event'
  | 'health'
  | 'evidence'
  | 'audit'
  | 'config_version'
  | 'unknown';

export interface EdgeStableValueIdentity {
  readonly tenantId?: string;
  readonly siteId?: string;
  readonly gatewayId: string;
  readonly edgeId?: string;
  readonly deviceId: string;
  readonly pointId: string;
  readonly recordType: EdgeStableRecordType;
}

export interface EdgeStableDeadbandPolicy {
  readonly mode: EdgeStableDeadbandMode;
  readonly absolute?: number;
  readonly percent?: number;
}

export interface EdgeStableSuppressionPolicy {
  readonly sampleMode: EdgeStableSampleMode;
  readonly heartbeatIntervalMs: number;
  readonly aggregationWindowMs: number;
  readonly deadband: EdgeStableDeadbandPolicy;
  readonly suppressStableTelemetry: boolean;
  readonly aggregateRepeatedAlarm: boolean;
  readonly emitReconnectFirstSample: boolean;
  readonly emitFullSnapshot: boolean;
}

export interface EdgeStableValueSnapshot {
  readonly identity: EdgeStableValueIdentity;
  readonly value: unknown;
  readonly quality?: string;
  readonly status?: string;
  readonly firstSeenAt: string;
  readonly lastSeenAt: string;
  readonly lastEmittedAt?: string;
  readonly suppressedCount: number;
  readonly repeatCount: number;
  readonly payloadHash: string;
}

export interface EdgeStableSuppressionDecision {
  readonly emit: boolean;
  readonly dedupeKey: string;
  readonly sampleMode: EdgeStableSampleMode;
  readonly changeReason: EdgeStableChangeReason;
  readonly valueChanged: boolean;
  readonly qualityChanged: boolean;
  readonly statusChanged: boolean;
  readonly suppressedCount: number;
  readonly repeatCount: number;
  readonly firstSeenAt: string;
  readonly lastSeenAt: string;
  readonly lastEmittedAt?: string;
  readonly deadbandApplied: boolean;
  readonly deadbandValue?: number;
  readonly deadbandMode: EdgeStableDeadbandMode;
  readonly aggregationWindowMs: number;
  readonly heartbeatDue: boolean;
  readonly fullSnapshot: boolean;
  readonly reconnectFirstSample: boolean;
}

export function createEdgeStableDedupeKey(identity: EdgeStableValueIdentity): string {
  return [
    identity.tenantId ?? 'tenant-unknown',
    identity.siteId ?? 'site-unknown',
    identity.gatewayId,
    identity.edgeId ?? 'edge-unknown',
    identity.deviceId,
    identity.pointId,
    identity.recordType,
  ].join(':');
}

export function createDefaultEdgeStableSuppressionPolicy(
  recordType: EdgeStableRecordType,
): EdgeStableSuppressionPolicy {
  if (recordType === 'alarm' || recordType === 'event') {
    return {
      sampleMode: 'AGGREGATED_REPEAT',
      heartbeatIntervalMs: 300000,
      aggregationWindowMs: 60000,
      deadband: { mode: 'DISABLED' },
      suppressStableTelemetry: false,
      aggregateRepeatedAlarm: true,
      emitReconnectFirstSample: true,
      emitFullSnapshot: true,
    };
  }

  if (recordType === 'analog' || recordType === 'telemetry') {
    return {
      sampleMode: 'DEADBAND',
      heartbeatIntervalMs: 300000,
      aggregationWindowMs: 60000,
      deadband: { mode: 'ABSOLUTE', absolute: 0.1 },
      suppressStableTelemetry: true,
      aggregateRepeatedAlarm: false,
      emitReconnectFirstSample: true,
      emitFullSnapshot: true,
    };
  }

  if (recordType === 'digital' || recordType === 'status') {
    return {
      sampleMode: 'CHANGE_ONLY',
      heartbeatIntervalMs: 300000,
      aggregationWindowMs: 60000,
      deadband: { mode: 'DISABLED' },
      suppressStableTelemetry: true,
      aggregateRepeatedAlarm: false,
      emitReconnectFirstSample: true,
      emitFullSnapshot: true,
    };
  }

  return {
    sampleMode: 'HEARTBEAT',
    heartbeatIntervalMs: 300000,
    aggregationWindowMs: 60000,
    deadband: { mode: 'DISABLED' },
    suppressStableTelemetry: false,
    aggregateRepeatedAlarm: false,
    emitReconnectFirstSample: true,
    emitFullSnapshot: true,
  };
}

export function isAnalogDeadbandExceeded(input: {
  readonly previousValue: number;
  readonly nextValue: number;
  readonly deadband: EdgeStableDeadbandPolicy;
}): boolean {
  if (input.deadband.mode === 'DISABLED') {
    return input.previousValue !== input.nextValue;
  }

  const difference = Math.abs(input.nextValue - input.previousValue);

  if (input.deadband.mode === 'ABSOLUTE') {
    return difference >= (input.deadband.absolute ?? 0);
  }

  const base = Math.abs(input.previousValue);
  if (base === 0) {
    return difference > 0;
  }

  return difference / base >= (input.deadband.percent ?? 0);
}

export function isHeartbeatDue(input: {
  readonly nowMs: number;
  readonly lastEmittedAtMs?: number;
  readonly heartbeatIntervalMs: number;
}): boolean {
  if (input.lastEmittedAtMs === undefined) {
    return true;
  }

  return input.nowMs - input.lastEmittedAtMs >= input.heartbeatIntervalMs;
}

export function createSuppressedNoChangeDecision(input: {
  readonly identity: EdgeStableValueIdentity;
  readonly snapshot: EdgeStableValueSnapshot;
  readonly policy: EdgeStableSuppressionPolicy;
  readonly now: string;
  readonly heartbeatDue?: boolean;
}): EdgeStableSuppressionDecision {
  return {
    emit: input.heartbeatDue === true,
    dedupeKey: createEdgeStableDedupeKey(input.identity),
    sampleMode: input.heartbeatDue === true ? 'HEARTBEAT' : input.policy.sampleMode,
    changeReason: input.heartbeatDue === true ? 'HEARTBEAT_DUE' : 'SUPPRESSED_NO_CHANGE',
    valueChanged: false,
    qualityChanged: false,
    statusChanged: false,
    suppressedCount: input.snapshot.suppressedCount + (input.heartbeatDue === true ? 0 : 1),
    repeatCount: input.snapshot.repeatCount,
    firstSeenAt: input.snapshot.firstSeenAt,
    lastSeenAt: input.now,
    ...(input.snapshot.lastEmittedAt !== undefined ? { lastEmittedAt: input.snapshot.lastEmittedAt } : {}),
    deadbandApplied: input.policy.deadband.mode !== 'DISABLED',
    deadbandValue: input.policy.deadband.absolute ?? input.policy.deadband.percent,
    deadbandMode: input.policy.deadband.mode,
    aggregationWindowMs: input.policy.aggregationWindowMs,
    heartbeatDue: input.heartbeatDue === true,
    fullSnapshot: false,
    reconnectFirstSample: false,
  };
}
