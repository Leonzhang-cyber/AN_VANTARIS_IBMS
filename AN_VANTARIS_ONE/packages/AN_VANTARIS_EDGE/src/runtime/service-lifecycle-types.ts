export type ServiceLifecycleState =
  | 'STOPPED'
  | 'STARTING'
  | 'RUNNING'
  | 'DEGRADED'
  | 'STOPPING'
  | 'FAILED'
  | 'RECOVERING'
  | 'CRASH_LOOP_BLOCKED'
  | 'MANUAL_INTERVENTION_REQUIRED';

export type ServiceLifecycleTransition = `${ServiceLifecycleState}->${ServiceLifecycleState}`;

export type ServiceLifecycleStateEntry = {
  readonly state: ServiceLifecycleState;
  readonly terminal: boolean;
  readonly healthy: boolean;
  readonly ready: boolean;
  readonly acceptsNewWork: boolean;
  readonly writableRuntimeState: boolean;
  readonly recoveryAllowed: boolean;
  readonly manualActionRequired: boolean;
  readonly notes: string;
};

export type ServiceLifecycleStateModel = {
  readonly schemaVersion: '1.0';
  readonly taskId: 'UFMS-EDGE-C4-05';
  readonly classification: 'SERVICE_LIFECYCLE_FOUNDATION_ONLY';
  readonly states: readonly ServiceLifecycleStateEntry[];
  readonly transitions: readonly ServiceLifecycleTransition[];
  readonly startupPrecheckRequirements: readonly string[];
  readonly gracefulShutdownModel: readonly string[];
  readonly readinessKey: 'UFMS_EDGE_C4_05_SERVICE_LIFECYCLE_RECOVERY_FOUNDATION_PASS';
};

export type StartupPrecheckResult = {
  readonly success: boolean;
  readonly failedChecks: readonly string[];
  readonly notes: readonly string[];
};

export type LifecycleSnapshot = {
  readonly serviceName: string;
  readonly instanceId: string;
  currentState: ServiceLifecycleState;
  previousState: ServiceLifecycleState;
  transitionReason: string;
  startedAt: string;
  stoppedAt: string;
  lastHealthyAt: string;
  lastReadyAt: string;
  restartCount: number;
  consecutiveFailureCount: number;
  recoveryAttemptCount: number;
  crashLoopDetected: boolean;
  manualInterventionRequired: boolean;
  mode: 'DRY_RUN';
  evidenceId: string;
};

export type FailureClass =
  | 'TRANSIENT_STARTUP_FAILURE'
  | 'TRANSIENT_RUNTIME_FAILURE'
  | 'CONFIGURATION_FAILURE'
  | 'RELEASE_INTEGRITY_FAILURE'
  | 'PERMISSION_FAILURE'
  | 'STORAGE_FAILURE'
  | 'BUFFER_CORRUPTION_RISK'
  | 'AUDIT_CHAIN_FAILURE'
  | 'DEPENDENCY_FAILURE'
  | 'CRASH_LOOP'
  | 'MANUAL_STOP'
  | 'UNKNOWN_FAILURE';

export type FailureSeverity = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';

export type RecoveryPolicyEntry = {
  readonly failureClass: FailureClass;
  readonly retryAllowed: boolean;
  readonly automaticRecoveryAllowed: boolean;
  readonly restartAllowed: boolean;
  readonly rollbackRecommended: boolean;
  readonly manualInterventionRequired: boolean;
  readonly preservesSharedState: boolean;
  readonly severity: FailureSeverity;
  readonly notes: string;
};

export type RecoveryPolicy = {
  readonly schemaVersion: '1.0';
  readonly taskId: 'UFMS-EDGE-C4-05';
  readonly classification: 'SERVICE_LIFECYCLE_FOUNDATION_ONLY';
  readonly failureClasses: readonly RecoveryPolicyEntry[];
  readonly preservationRequirements: readonly string[];
  readonly forbiddenRecoveryActions: readonly string[];
  readonly readinessKey: 'UFMS_EDGE_C4_05_SERVICE_LIFECYCLE_RECOVERY_FOUNDATION_PASS';
};

export type RestartBackoffPolicy = {
  readonly schemaVersion: '1.0';
  readonly taskId: 'UFMS-EDGE-C4-05';
  readonly classification: 'SERVICE_LIFECYCLE_FOUNDATION_ONLY';
  readonly initialDelaySeconds: number;
  readonly multiplier: number;
  readonly maxDelaySeconds: number;
  readonly maxAttempts: number;
  readonly resetWindowSeconds: number;
  readonly jitterEnabled: boolean;
  readonly jitterMode: 'DETERMINISTIC_FIXTURE_ONLY';
  readonly retryBudget: number;
  readonly restartOnManualStop: false;
  readonly restartOnIntegrityFailure: false;
  readonly restartOnPermissionFailure: false;
  readonly restartOnCrashLoop: false;
  readonly readinessKey: 'UFMS_EDGE_C4_05_SERVICE_LIFECYCLE_RECOVERY_FOUNDATION_PASS';
};

export type CrashLoopPolicy = {
  readonly schemaVersion: '1.0';
  readonly taskId: 'UFMS-EDGE-C4-05';
  readonly classification: 'SERVICE_LIFECYCLE_FOUNDATION_ONLY';
  readonly windowSeconds: number;
  readonly maxFailuresInWindow: number;
  readonly consecutiveFailureThreshold: number;
  readonly blockDurationSeconds: number;
  readonly automaticUnblock: false;
  readonly requiresManualReview: true;
  readonly preserveState: true;
  readonly preserveBuffer: true;
  readonly preserveAudit: true;
  readonly preserveEvidence: true;
  readonly readinessKey: 'UFMS_EDGE_C4_05_SERVICE_LIFECYCLE_RECOVERY_FOUNDATION_PASS';
};

export type LifecycleHistoryEntry = {
  readonly timestamp: string;
  readonly action: string;
  readonly fromState: ServiceLifecycleState;
  readonly toState: ServiceLifecycleState;
  readonly reason: string;
  readonly failureClass: FailureClass;
  readonly restartAttempt: number;
  readonly backoffSeconds: number;
  readonly decision: string;
  readonly result: string;
  readonly evidenceId: string;
  readonly mode: 'DRY_RUN';
};

export type SystemdLifecycleRecommendationEntry = {
  readonly setting: string;
  readonly recommendedValue: string;
  readonly appliedByC4_05: false;
  readonly compatibilityReviewRequired: boolean;
  readonly riskAddressed: string;
  readonly notes: string;
};

export type SystemdLifecycleRecommendation = {
  readonly schemaVersion: '1.0';
  readonly taskId: 'UFMS-EDGE-C4-05';
  readonly classification: 'SERVICE_LIFECYCLE_FOUNDATION_ONLY';
  readonly recommendations: readonly SystemdLifecycleRecommendationEntry[];
  readonly readinessKey: 'UFMS_EDGE_C4_05_SERVICE_LIFECYCLE_RECOVERY_FOUNDATION_PASS';
};

export type ServiceLifecycleAcceptanceResult =
  | 'SERVICE_LIFECYCLE_FOUNDATION_ACCEPTED_NOT_APPLIED'
  | 'SERVICE_LIFECYCLE_FOUNDATION_REJECTED';

export type RecoveryDecision = {
  readonly failureClass: FailureClass;
  readonly shouldRestart: boolean;
  readonly shouldRequireManualIntervention: boolean;
  readonly shouldRecommendRollback: boolean;
  readonly preservesSharedState: boolean;
  readonly classification: 'AUTOMATIC_RECOVERY' | 'MANUAL_INTERVENTION' | 'BLOCKED';
  readonly reason: string;
};

export type ValidationResult = {
  readonly ok: boolean;
  readonly errors: readonly string[];
};
