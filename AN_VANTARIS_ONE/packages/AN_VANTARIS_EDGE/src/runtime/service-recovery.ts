import type {
  FailureClass,
  RecoveryDecision,
  RecoveryPolicy,
  RecoveryPolicyEntry,
  RestartBackoffPolicy,
} from './service-lifecycle-types.js';

function findRecoveryPolicyEntry(policy: RecoveryPolicy, failureClass: FailureClass): RecoveryPolicyEntry {
  const row = policy.failureClasses.find((entry) => entry.failureClass === failureClass);
  if (!row) {
    throw new Error(`missing failure class policy: ${failureClass}`);
  }
  return row;
}

export function classifyServiceFailure(reason: string): FailureClass {
  const normalized = reason.toLowerCase();
  if (normalized.includes('integrity')) return 'RELEASE_INTEGRITY_FAILURE';
  if (normalized.includes('permission')) return 'PERMISSION_FAILURE';
  if (normalized.includes('manual stop')) return 'MANUAL_STOP';
  if (normalized.includes('crash loop')) return 'CRASH_LOOP';
  if (normalized.includes('buffer corruption')) return 'BUFFER_CORRUPTION_RISK';
  if (normalized.includes('audit')) return 'AUDIT_CHAIN_FAILURE';
  if (normalized.includes('config')) return 'CONFIGURATION_FAILURE';
  if (normalized.includes('startup')) return 'TRANSIENT_STARTUP_FAILURE';
  if (normalized.includes('runtime')) return 'TRANSIENT_RUNTIME_FAILURE';
  if (normalized.includes('dependency')) return 'DEPENDENCY_FAILURE';
  if (normalized.includes('storage')) return 'STORAGE_FAILURE';
  return 'UNKNOWN_FAILURE';
}

export function shouldRestartService(
  failureClass: FailureClass,
  policy: RecoveryPolicy,
  restartBackoff: RestartBackoffPolicy,
  attempt: number,
): boolean {
  const row = findRecoveryPolicyEntry(policy, failureClass);
  if (!row.restartAllowed || !row.retryAllowed || !row.automaticRecoveryAllowed) return false;
  if (attempt >= restartBackoff.maxAttempts) return false;
  if (attempt >= restartBackoff.retryBudget) return false;
  if (failureClass === 'MANUAL_STOP' && restartBackoff.restartOnManualStop === false) return false;
  if (failureClass === 'RELEASE_INTEGRITY_FAILURE' && restartBackoff.restartOnIntegrityFailure === false) return false;
  if (failureClass === 'PERMISSION_FAILURE' && restartBackoff.restartOnPermissionFailure === false) return false;
  if (failureClass === 'CRASH_LOOP' && restartBackoff.restartOnCrashLoop === false) return false;
  return true;
}

export function shouldRequireManualIntervention(
  failureClass: FailureClass,
  policy: RecoveryPolicy,
): boolean {
  return findRecoveryPolicyEntry(policy, failureClass).manualInterventionRequired;
}

export function shouldRecommendRollback(
  failureClass: FailureClass,
  policy: RecoveryPolicy,
): boolean {
  return findRecoveryPolicyEntry(policy, failureClass).rollbackRecommended;
}

export function validateStatePreservationPolicy(policy: RecoveryPolicy): boolean {
  const required = new Set([
    'shared/config',
    'shared/data',
    'shared/buffer',
    'shared/audit',
    'shared/evidence',
    'shared/logs',
    'shared/backups',
    'lifecycle history',
    'active release metadata',
    'previous release metadata',
  ]);
  for (const item of policy.preservationRequirements) {
    required.delete(item);
  }
  if (required.size !== 0) return false;
  const forbidden = new Set(policy.forbiddenRecoveryActions);
  return (
    forbidden.has('clear buffer') &&
    forbidden.has('delete audit') &&
    forbidden.has('delete evidence') &&
    forbidden.has('delete release history')
  );
}

export function evaluateRecoveryDecision(
  failureClass: FailureClass,
  policy: RecoveryPolicy,
  restartBackoff: RestartBackoffPolicy,
  attempt: number,
): RecoveryDecision {
  const restart = shouldRestartService(failureClass, policy, restartBackoff, attempt);
  const manual = shouldRequireManualIntervention(failureClass, policy);
  const rollback = shouldRecommendRollback(failureClass, policy);
  const row = findRecoveryPolicyEntry(policy, failureClass);
  const classification: RecoveryDecision['classification'] = restart
    ? 'AUTOMATIC_RECOVERY'
    : manual
      ? 'MANUAL_INTERVENTION'
      : 'BLOCKED';
  return {
    failureClass,
    shouldRestart: restart,
    shouldRequireManualIntervention: manual,
    shouldRecommendRollback: rollback,
    preservesSharedState: row.preservesSharedState,
    classification,
    reason: row.notes,
  };
}
