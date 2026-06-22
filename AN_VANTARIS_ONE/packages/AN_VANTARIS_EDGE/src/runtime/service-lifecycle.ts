import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';
import { dirname, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';

import type {
  CrashLoopPolicy,
  FailureClass,
  LifecycleHistoryEntry,
  LifecycleSnapshot,
  RecoveryPolicy,
  RestartBackoffPolicy,
  ServiceLifecycleAcceptanceResult,
  ServiceLifecycleState,
  ServiceLifecycleTransition,
  ServiceLifecycleStateModel,
  StartupPrecheckResult,
  SystemdLifecycleRecommendation,
  ValidationResult,
} from './service-lifecycle-types.js';

const READINESS_KEY = 'UFMS_EDGE_C4_05_SERVICE_LIFECYCLE_RECOVERY_FOUNDATION_PASS';
const runtimeDir = dirname(fileURLToPath(import.meta.url));
const EDGE_ROOT = resolve(runtimeDir, '..', '..');
const LIFECYCLE_ROOT = resolve(EDGE_ROOT, 'deploy', 'offline-bundle', 'service-lifecycle');

function assertInsideEdge(pathValue: string): string {
  const resolved = resolve(pathValue);
  if (!resolved.startsWith(EDGE_ROOT + sep) && resolved !== EDGE_ROOT) {
    throw new Error(`path outside EDGE root: ${pathValue}`);
  }
  return resolved;
}

function readJson<T>(pathValue: string): T {
  return JSON.parse(readFileSync(assertInsideEdge(pathValue), 'utf8')) as T;
}

const REQUIRED_STATES: readonly ServiceLifecycleState[] = [
  'STOPPED',
  'STARTING',
  'RUNNING',
  'DEGRADED',
  'STOPPING',
  'FAILED',
  'RECOVERING',
  'CRASH_LOOP_BLOCKED',
  'MANUAL_INTERVENTION_REQUIRED',
];

const REQUIRED_TRANSITIONS: readonly ServiceLifecycleTransition[] = [
  'STOPPED->STARTING',
  'STARTING->RUNNING',
  'STARTING->DEGRADED',
  'STARTING->FAILED',
  'RUNNING->DEGRADED',
  'RUNNING->STOPPING',
  'RUNNING->FAILED',
  'DEGRADED->RUNNING',
  'DEGRADED->STOPPING',
  'DEGRADED->FAILED',
  'FAILED->RECOVERING',
  'FAILED->MANUAL_INTERVENTION_REQUIRED',
  'RECOVERING->STARTING',
  'RECOVERING->CRASH_LOOP_BLOCKED',
  'RECOVERING->MANUAL_INTERVENTION_REQUIRED',
  'CRASH_LOOP_BLOCKED->MANUAL_INTERVENTION_REQUIRED',
  'STOPPING->STOPPED',
];

export function loadServiceLifecycleStateModel(
  pathValue: string = resolve(LIFECYCLE_ROOT, 'SERVICE_LIFECYCLE_STATE_MODEL.edge.json'),
): ServiceLifecycleStateModel {
  return readJson<ServiceLifecycleStateModel>(pathValue);
}

export function validateServiceLifecycleStateModel(model: unknown): ValidationResult {
  const errors: string[] = [];
  const row = model as ServiceLifecycleStateModel;
  if (row.schemaVersion !== '1.0') errors.push('schemaVersion mismatch');
  if (row.taskId !== 'UFMS-EDGE-C4-05') errors.push('taskId mismatch');
  if (row.classification !== 'SERVICE_LIFECYCLE_FOUNDATION_ONLY') errors.push('classification mismatch');
  if (row.readinessKey !== READINESS_KEY) errors.push('readinessKey mismatch');
  const states = new Set((row.states || []).map((s) => s.state));
  for (const required of REQUIRED_STATES) {
    if (!states.has(required)) errors.push(`missing state: ${required}`);
  }
  const transitions = new Set<ServiceLifecycleTransition>(row.transitions || []);
  for (const required of REQUIRED_TRANSITIONS) {
    if (!transitions.has(required)) errors.push(`missing transition: ${required}`);
  }
  const illegal = ['STOPPED->RUNNING', 'FAILED->RUNNING', 'CRASH_LOOP_BLOCKED->RUNNING', 'MANUAL_INTERVENTION_REQUIRED->RUNNING'];
  for (const bad of illegal) {
    if (transitions.has(bad as ServiceLifecycleTransition)) errors.push(`illegal transition present: ${bad}`);
  }
  return { ok: errors.length === 0, errors };
}

export function isValidLifecycleTransition(
  model: ServiceLifecycleStateModel,
  fromState: ServiceLifecycleState,
  toState: ServiceLifecycleState,
): boolean {
  return new Set(model.transitions).has(`${fromState}->${toState}`);
}

export function applyLifecycleTransition(
  model: ServiceLifecycleStateModel,
  snapshot: LifecycleSnapshot,
  toState: ServiceLifecycleState,
  reason: string,
): LifecycleSnapshot {
  if (!isValidLifecycleTransition(model, snapshot.currentState, toState)) {
    throw new Error(`invalid transition ${snapshot.currentState}->${toState}`);
  }
  const now = new Date().toISOString();
  const next: LifecycleSnapshot = {
    ...snapshot,
    previousState: snapshot.currentState,
    currentState: toState,
    transitionReason: reason,
  };
  if (toState === 'RUNNING') {
    next.lastHealthyAt = now;
    next.lastReadyAt = now;
  }
  if (toState === 'STOPPED') {
    next.stoppedAt = now;
  }
  if (toState === 'FAILED') {
    next.consecutiveFailureCount += 1;
  }
  if (toState === 'RECOVERING') {
    next.recoveryAttemptCount += 1;
  }
  if (toState === 'CRASH_LOOP_BLOCKED' || toState === 'MANUAL_INTERVENTION_REQUIRED') {
    next.manualInterventionRequired = true;
  }
  return next;
}

export function createInitialLifecycleSnapshot(serviceName: string, instanceId: string): LifecycleSnapshot {
  const now = new Date().toISOString();
  return {
    serviceName,
    instanceId,
    currentState: 'STOPPED',
    previousState: 'STOPPED',
    transitionReason: 'initialization',
    startedAt: '',
    stoppedAt: now,
    lastHealthyAt: '',
    lastReadyAt: '',
    restartCount: 0,
    consecutiveFailureCount: 0,
    recoveryAttemptCount: 0,
    crashLoopDetected: false,
    manualInterventionRequired: false,
    mode: 'DRY_RUN',
    evidenceId: `lifecycle-init-${createHash('sha256').update(`${serviceName}:${instanceId}:${now}`).digest('hex').slice(0, 12)}`,
  };
}

export function evaluateStartupPrecheck(checkResults: Record<string, boolean>): StartupPrecheckResult {
  const failedChecks = Object.entries(checkResults)
    .filter(([, ok]) => !ok)
    .map(([name]) => name);
  return {
    success: failedChecks.length === 0,
    failedChecks,
    notes: failedChecks.length === 0 ? ['all startup prechecks passed'] : ['startup blocked due to failed checks'],
  };
}

export function calculateRestartBackoff(
  policy: RestartBackoffPolicy,
  attempt: number,
): number {
  const boundedAttempt = Math.max(0, attempt);
  const base = policy.initialDelaySeconds * Math.pow(policy.multiplier, boundedAttempt);
  return Math.min(policy.maxDelaySeconds, Math.floor(base));
}

export function detectCrashLoop(
  policy: CrashLoopPolicy,
  failureTimestampsEpochSec: readonly number[],
  consecutiveFailureCount: number,
): boolean {
  if (consecutiveFailureCount >= policy.consecutiveFailureThreshold) {
    return true;
  }
  if (failureTimestampsEpochSec.length < policy.maxFailuresInWindow) {
    return false;
  }
  const sorted = [...failureTimestampsEpochSec].sort((a, b) => a - b);
  const latest = sorted[sorted.length - 1];
  const windowStart = latest - policy.windowSeconds;
  const inWindow = sorted.filter((t) => t >= windowStart).length;
  return inWindow >= policy.maxFailuresInWindow;
}

export function createLifecycleHistoryEntry(
  action: string,
  fromState: ServiceLifecycleState,
  toState: ServiceLifecycleState,
  reason: string,
  failureClass: FailureClass,
  restartAttempt: number,
  backoffSeconds: number,
  decision: string,
  result: string,
): LifecycleHistoryEntry {
  return {
    timestamp: new Date().toISOString(),
    action,
    fromState,
    toState,
    reason,
    failureClass,
    restartAttempt,
    backoffSeconds,
    decision,
    result,
    evidenceId: `history-${createHash('sha256').update(`${action}:${fromState}:${toState}:${reason}:${Date.now()}`).digest('hex').slice(0, 12)}`,
    mode: 'DRY_RUN',
  };
}

export function evaluateServiceLifecycleAcceptance(
  model: ServiceLifecycleStateModel,
  recoveryPolicy: RecoveryPolicy,
  backoffPolicy: RestartBackoffPolicy,
  crashLoopPolicy: CrashLoopPolicy,
  systemdRecommendation: SystemdLifecycleRecommendation,
): ServiceLifecycleAcceptanceResult {
  const modelValidation = validateServiceLifecycleStateModel(model);
  if (!modelValidation.ok) return 'SERVICE_LIFECYCLE_FOUNDATION_REJECTED';
  if (recoveryPolicy.failureClasses.length < 12) return 'SERVICE_LIFECYCLE_FOUNDATION_REJECTED';
  if (backoffPolicy.retryBudget <= 0 || backoffPolicy.maxAttempts <= 0) return 'SERVICE_LIFECYCLE_FOUNDATION_REJECTED';
  if (crashLoopPolicy.maxFailuresInWindow <= 0 || crashLoopPolicy.consecutiveFailureThreshold <= 0) {
    return 'SERVICE_LIFECYCLE_FOUNDATION_REJECTED';
  }
  if (systemdRecommendation.recommendations.some((row) => row.appliedByC4_05 !== false)) {
    return 'SERVICE_LIFECYCLE_FOUNDATION_REJECTED';
  }
  return 'SERVICE_LIFECYCLE_FOUNDATION_ACCEPTED_NOT_APPLIED';
}
