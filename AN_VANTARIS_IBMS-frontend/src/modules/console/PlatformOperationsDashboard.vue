<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ApiError } from '@/services/api/errors'
import {
  getConsoleAllModuleHealth,
  getConsoleHealth,
  getConsoleModuleHealth,
  getConsoleModules,
  getConsoleNavigationModules,
  getConsoleOperationsSummary,
  getConsoleReadinessRegistry,
  getConsoleReadinessScore,
  getConsoleReadinessSummary,
  getConsoleReportsReadiness,
  getLockedPackages,
  getModulePackageDetail,
  getModulePackages,
  getPackageCenterHealth,
  getPackageEntries,
  getRoleEntries,
  getRoleMenuPreview,
  getRoleVisibility,
  getRoleVisibilitySummary,
  getSupportedPackageRoles,
  getPackageSummary,
  getPatchReadiness,
  type ConsoleRole,
  type ConsoleHealth,
  type ModulePackageRecord,
  type ModuleReadinessRecord,
  type ModuleReadinessSummary,
  type PackageCenterHealth,
  type PackageEntryCenter,
  type PackageSummary,
  type PatchReadiness,
  type RoleEntryView,
  type RoleMenuPreview,
  type RoleVisibilityPolicy,
  type RoleVisibilitySummary,
  type OperationsDashboardSummary,
  type PlatformModuleSummary,
  type PlatformNavigationItem,
  type PlatformNavigationModel,
  type PlatformReadinessScore,
  type ReportsReadinessSnapshot,
} from '@/services/api/console'

const router = useRouter()

const loading = ref(false)
const loadingHealthDetail = ref(false)
const apiError = ref('')
const scoreFallbackAlert = ref('')
const navigationFallbackAlert = ref('')
const showHealthDrawer = ref(false)
const selectedHealthDetail = ref<ModuleReadinessRecord | null>(null)
const loadingPackageDetail = ref(false)
const showPackageDrawer = ref(false)
const selectedPackageDetail = ref<ModulePackageRecord | null>(null)
const packageCenterError = ref('')
const roleVisibilityError = ref('')
const selectedRole = ref<ConsoleRole>('admin')

const health = ref<ConsoleHealth>({
  status: 'unknown',
  moduleId: 'uconsole',
  moduleName: 'UConsole / Platform Operations Dashboard',
  runtimeMode: 'skeleton',
  provider: 'local-platform-summary',
  sourceSemantics: 'ibms-neutral',
  readOnly: true,
  controlActionsEnabled: false,
  certified: false,
  iec62443Certified: false,
})

const modules = ref<ModuleReadinessRecord[]>([])
const reportsReadiness = ref<ReportsReadinessSnapshot>({
  routeReady: true,
  menuReady: true,
  queryReady: true,
  exportReady: true,
  manifestReady: true,
  auditStoreReady: true,
  auditVerifyReady: true,
  permissionPlaceholderReady: true,
  auditExportReady: true,
  certified: false,
  iec62443Certified: false,
  limitations: [
    'No real auth/RBAC integration.',
    'No DB audit table migration.',
    'No formal certified evidence protocol.',
    'No UCDE runtime integration.',
    'No IEC62443 certification claim.',
  ],
})

const legacySummary = ref<OperationsDashboardSummary>({
  totals: {
    totalModules: 0,
    readyModules: 0,
    foundationModules: 0,
    plannedModules: 0,
    auditReadyModules: 0,
    certifiedModules: 0,
    iec62443CertifiedModules: 0,
  },
  highlights: [],
  warnings: [],
  securityPosture: {
    auditReadinessFoundation: true,
    realRbacIntegrated: false,
    dbAuditIntegrated: false,
    siemIntegrated: false,
    ucdeRuntimeIntegrated: false,
    certified: false,
    iec62443Certified: false,
  },
})

const registrySummary = ref<ModuleReadinessSummary>({
  totalModules: 0,
  readyModules: 0,
  foundationModules: 0,
  plannedModules: 0,
  notIntegratedModules: 0,
  auditReadyModules: 0,
  certifiedModules: 0,
  iec62443CertifiedModules: 0,
  averageHealthScore: 0,
  lowestHealthModules: [],
  highestHealthModules: [],
})

const readinessScore = ref<PlatformReadinessScore>({
  overallScore: 0,
  scoreBand: 'early-foundation',
  scoreMode: 'frontend-local-fallback',
  certified: false,
  iec62443Certified: false,
  components: {
    moduleReadiness: { score: 0, weight: 0.35, basis: 'runtimeStatus, readinessLevel, frontendReady, backendReady, apiReady' },
    auditReadiness: { score: 0, weight: 0.25, basis: 'auditReadiness, audit storage, audit verification placeholders' },
    securityPosture: { score: 0, weight: 0.25, basis: 'permission mode, certified flags, RBAC/SIEM/UCDE integration status' },
    integrationReadiness: { score: 0, weight: 0.15, basis: 'integrationMode, edge/link runtime integration status' },
  },
  drivers: [],
  risks: [],
  recommendations: [],
})

const navigationModel = ref<PlatformNavigationModel>({
  navigationMode: 'read-only-module-launch',
  controlActionsEnabled: false,
  items: [],
})

const packageCenterHealth = ref<PackageCenterHealth>({
  status: 'unknown',
  moduleId: 'uconsole-package-center',
  moduleName: 'UConsole Module Package Center',
  runtimeMode: 'local-skeleton',
  provider: 'local-package-registry',
  readOnly: true,
  controlActionsEnabled: false,
  patchActionsEnabled: false,
  licenseServerIntegrated: false,
  entitlementRuntimeIntegrated: false,
  hotPlugArchitectureReady: true,
  roleEntryModelReady: true,
  certified: false,
  iec62443Certified: false,
})

const packageSummary = ref<PackageSummary>({
  totalPackages: 0,
  installedPackages: 0,
  entitledPackages: 0,
  enabledPackages: 0,
  visiblePackages: 0,
  lockedPackages: 0,
  customerEntryCount: 0,
  engineerEntryCount: 0,
  adminEntryCount: 0,
  patchReadyPackages: 0,
  upgradeRequiredPackages: 0,
  licenseServerIntegrated: false,
  patchActionsEnabled: false,
  controlActionsEnabled: false,
  roleEntryModelReady: true,
  hotPlugArchitectureReady: true,
  limitations: [],
  certified: false,
  iec62443Certified: false,
})

const packageEntries = ref<PackageEntryCenter>({
  customerApplications: [],
  engineerWorkspace: [],
  adminPackageCenter: [],
  lockedPackages: [],
  entryMode: 'local-skeleton-entry-center',
  roleAware: true,
  runtimeLinked: false,
  certified: false,
  iec62443Certified: false,
})

const patchReadiness = ref<PatchReadiness>({
  patchMode: 'local-skeleton-patch-readiness',
  patchActionsEnabled: false,
  packages: [],
  upgradeRequiredPackages: [],
  patchReadyPackages: [],
  licenseServerIntegrated: false,
  limitations: [],
  certified: false,
  iec62443Certified: false,
})

const packages = ref<ModulePackageRecord[]>([])
const lockedPackages = ref<ModulePackageRecord[]>([])
const supportedRoles = ref<ConsoleRole[]>(['customer', 'engineer', 'admin'])
const roleVisibilitySummary = ref<RoleVisibilitySummary>({
  supportedRoles: ['customer', 'engineer', 'admin'],
  roleVisibilityMode: 'local-skeleton-role-visibility',
  realRbacIntegrated: false,
  authIntegrated: false,
  routeGuardIntegrated: false,
  customerVisibleCount: 0,
  engineerVisibleCount: 0,
  adminVisibleCount: 0,
  lockedPackageCount: 0,
  hiddenPackageCount: 0,
  readOnly: true,
  controlActionsEnabled: false,
  certified: false,
  iec62443Certified: false,
})
const rolePolicy = ref<RoleVisibilityPolicy>({
  role: 'admin',
  roleLabel: 'Admin User',
  visibilityMode: 'local-skeleton-role-visibility',
  realRbacIntegrated: false,
  authIntegrated: false,
  routeGuardIntegrated: false,
  readOnly: true,
  allowedEntryModes: ['customer-application', 'engineer-diagnostics', 'admin-package-center'],
  hiddenEntryModes: [],
  visiblePackages: [],
  lockedPackages: [],
  hiddenPackages: [],
  menuPreview: [],
  hiddenOrLockedReasons: [],
  limitations: [],
  certified: false,
  iec62443Certified: false,
})
const roleEntries = ref<RoleEntryView>({
  role: 'admin',
  roleLabel: 'Admin User',
  entryMode: 'local-skeleton-role-entry-view',
  visiblePackages: [],
  lockedPackages: [],
  hiddenPackages: [],
  readOnly: true,
  controlActionsEnabled: false,
  realRbacIntegrated: false,
  authIntegrated: false,
  routeGuardIntegrated: false,
  certified: false,
  iec62443Certified: false,
})
const roleMenuPreview = ref<RoleMenuPreview>({
  role: 'admin',
  roleLabel: 'Admin User',
  menuPreviewMode: 'local-skeleton-role-menu-preview',
  items: [],
  readOnly: true,
  realRbacIntegrated: false,
  authIntegrated: false,
  routeGuardIntegrated: false,
  certified: false,
  iec62443Certified: false,
})

const moduleFilters = reactive({
  runtimeStatus: '',
  lifecycleStage: '',
  auditReadiness: '',
  permissionMode: '',
})

const packageFilters = reactive({
  moduleId: '',
  packageCategory: '',
  installed: '',
  entitled: '',
  enabled: '',
  visible: '',
  patchStatus: '',
  role: '',
})

const fallbackModules: ModuleReadinessRecord[] = [
  {
    moduleId: 'reports',
    moduleName: 'Reports',
    moduleType: 'platform-module',
    domain: 'platform-operations',
    route: '/reports',
    runtimeStatus: 'ready',
    readinessLevel: 'readiness-candidate',
    lifecycleStage: 'runnable-readiness',
    frontendReady: true,
    backendReady: true,
    apiReady: true,
    auditReadiness: 'ready',
    permissionMode: 'placeholder-allow',
    dataPersistenceMode: 'local-jsonl-audit',
    integrationMode: 'local-skeleton',
    healthStatus: 'ready',
    healthScore: 80,
    healthDetails: {},
    securityFlags: {
      realRbacIntegrated: false,
      dbAuditIntegrated: false,
      siemIntegrated: false,
      ucdeRuntimeIntegrated: false,
      edgeRuntimeIntegrated: false,
      linkRuntimeIntegrated: false,
      certified: false,
      iec62443Certified: false,
    },
    limitations: ['Fallback summary only.'],
    dependencies: [],
    nextActions: ['Maintain readiness candidate in read-only mode.'],
    readinessNotes: [],
    boundaryNotes: [],
    lastUpdated: '',
    readOnly: true,
    controlActionsEnabled: false,
    certified: false,
    iec62443Certified: false,
  },
  {
    moduleId: 'uconsole',
    moduleName: 'UConsole / Platform Operations Dashboard',
    moduleType: 'platform-module',
    domain: 'platform-operations',
    route: '/console/operations',
    runtimeStatus: 'foundation',
    readinessLevel: 'r2-foundation',
    lifecycleStage: 'platform-foundation',
    frontendReady: true,
    backendReady: true,
    apiReady: true,
    auditReadiness: 'limited',
    permissionMode: 'placeholder-allow',
    dataPersistenceMode: 'none',
    integrationMode: 'local-skeleton',
    healthStatus: 'foundation',
    healthScore: 70,
    healthDetails: {},
    securityFlags: {
      realRbacIntegrated: false,
      dbAuditIntegrated: false,
      siemIntegrated: false,
      ucdeRuntimeIntegrated: false,
      edgeRuntimeIntegrated: false,
      linkRuntimeIntegrated: false,
      certified: false,
      iec62443Certified: false,
    },
    limitations: ['Fallback summary only.'],
    dependencies: [],
    nextActions: ['Freeze UConsole foundation and maintain read-only entry.'],
    readinessNotes: [],
    boundaryNotes: [],
    lastUpdated: '',
    readOnly: true,
    controlActionsEnabled: false,
    certified: false,
    iec62443Certified: false,
  },
]

const hasModules = computed(() => filteredModules.value.length > 0)
const filteredPackages = computed(() => {
  return packages.value.filter((row) => {
    if (packageFilters.moduleId && row.moduleId !== packageFilters.moduleId) {
      return false
    }
    if (packageFilters.packageCategory && row.packageCategory !== packageFilters.packageCategory) {
      return false
    }
    if (packageFilters.installed && String(row.installed) !== packageFilters.installed) {
      return false
    }
    if (packageFilters.entitled && String(row.entitled) !== packageFilters.entitled) {
      return false
    }
    if (packageFilters.enabled && String(row.enabled) !== packageFilters.enabled) {
      return false
    }
    if (packageFilters.visible && String(row.visible) !== packageFilters.visible) {
      return false
    }
    if (packageFilters.patchStatus && row.patchStatus !== packageFilters.patchStatus) {
      return false
    }
    if (packageFilters.role && !row.roleVisibility[packageFilters.role as keyof typeof row.roleVisibility]) {
      return false
    }
    return true
  })
})

const roleVisibleCustomerApplications = computed(() => {
  return roleEntries.value.visiblePackages.filter((item) => item.entryMode === 'customer-application' && !item.contextOnly)
})

const roleVisibleEngineerWorkspace = computed(() => {
  const allEngineerRows = [...roleEntries.value.visiblePackages, ...roleEntries.value.lockedPackages, ...roleEntries.value.hiddenPackages]
  return allEngineerRows.filter((item) => item.entryMode === 'engineer-diagnostics')
})

const roleAdminPackageCenter = computed(() => {
  if (selectedRole.value !== 'admin') {
    return []
  }
  return packageEntries.value.adminPackageCenter
})

const filteredModules = computed(() => {
  return modules.value.filter((row) => {
    if (moduleFilters.runtimeStatus && row.runtimeStatus !== moduleFilters.runtimeStatus) {
      return false
    }
    if (moduleFilters.lifecycleStage && row.lifecycleStage !== moduleFilters.lifecycleStage) {
      return false
    }
    if (moduleFilters.auditReadiness && row.auditReadiness !== moduleFilters.auditReadiness) {
      return false
    }
    if (moduleFilters.permissionMode && row.permissionMode !== moduleFilters.permissionMode) {
      return false
    }
    return true
  })
})

function normalizeError(error: unknown, fallbackMessage: string): string {
  return error instanceof ApiError ? error.message : fallbackMessage
}

function asReadinessRecord(item: PlatformModuleSummary): ModuleReadinessRecord {
  return {
    moduleId: item.moduleId,
    moduleName: item.moduleName,
    moduleType: item.moduleType,
    domain: 'platform-operations',
    route: item.route,
    runtimeStatus: item.runtimeStatus,
    readinessLevel: item.readinessLevel,
    lifecycleStage: item.runtimeStatus === 'ready' ? 'runnable-readiness' : item.runtimeStatus === 'foundation' ? 'platform-foundation' : 'planned',
    frontendReady: item.frontendReady,
    backendReady: item.backendReady,
    apiReady: item.backendReady,
    auditReadiness: item.auditReadiness ? 'foundation' : 'planned',
    permissionMode: item.permissionMode,
    dataPersistenceMode: item.dataPersistenceMode,
    integrationMode: 'local-skeleton',
    healthStatus: item.runtimeStatus,
    healthScore: item.runtimeStatus === 'ready' ? 80 : 55,
    healthDetails: {},
    securityFlags: {
      realRbacIntegrated: false,
      dbAuditIntegrated: false,
      siemIntegrated: false,
      ucdeRuntimeIntegrated: false,
      edgeRuntimeIntegrated: false,
      linkRuntimeIntegrated: false,
      certified: false,
      iec62443Certified: false,
    },
    limitations: [item.securityNotes],
    dependencies: [],
    nextActions: [],
    readinessNotes: [],
    boundaryNotes: [],
    lastUpdated: '',
    readOnly: true,
    controlActionsEnabled: false,
    certified: item.certified,
    iec62443Certified: item.iec62443Certified,
  }
}

function calculateFallbackSummary(items: ModuleReadinessRecord[]): ModuleReadinessSummary {
  const readyModules = items.filter((item) => item.runtimeStatus === 'ready').length
  const foundationModules = items.filter((item) => item.runtimeStatus === 'foundation').length
  const plannedModules = items.filter((item) => item.runtimeStatus === 'planned').length
  const notIntegratedModules = items.filter((item) => item.runtimeStatus === 'not-integrated').length
  const auditReadyModules = items.filter((item) => ['ready', 'foundation', 'limited'].includes(item.auditReadiness)).length
  const averageHealthScore =
    items.length > 0 ? Number((items.reduce((acc, item) => acc + item.healthScore, 0) / items.length).toFixed(2)) : 0
  return {
    totalModules: items.length,
    readyModules,
    foundationModules,
    plannedModules,
    notIntegratedModules,
    auditReadyModules,
    certifiedModules: 0,
    iec62443CertifiedModules: 0,
    averageHealthScore,
    lowestHealthModules: [],
    highestHealthModules: [],
  }
}

function getNextActionLabel(item: ModuleReadinessRecord): string {
  if (item.runtimeStatus === 'ready' || item.readinessLevel === 'readiness-candidate') {
    return 'Continue hardening'
  }
  if (item.runtimeStatus === 'foundation') {
    return 'Freeze foundation'
  }
  if (item.runtimeStatus === 'planned') {
    return 'Build runtime foundation'
  }
  if (item.runtimeStatus === 'not-integrated') {
    return 'Keep boundary separated'
  }
  return 'Review readiness'
}

function getGeneratedNextActions(item: ModuleReadinessRecord): string[] {
  if (item.nextActions.length > 0) {
    return item.nextActions
  }
  const label = getNextActionLabel(item)
  if (label === 'Continue hardening') {
    return ['Maintain readiness, continue hardening.']
  }
  if (label === 'Freeze foundation') {
    return ['Complete module freeze and expand details.']
  }
  if (label === 'Build runtime foundation') {
    return ['Create runtime foundation before launch.']
  }
  if (label === 'Keep boundary separated') {
    return ['Keep boundary separated until integration is explicitly approved.']
  }
  return ['Review readiness assumptions and update registry details.']
}

function getScoreMeaning(score: number): string {
  if (score >= 75) {
    return 'strong readiness for current staged scope'
  }
  if (score >= 50) {
    return 'moderate readiness with remaining limitations'
  }
  if (score >= 25) {
    return 'foundation established but major work remains'
  }
  return 'early foundation and planning-heavy stage'
}

function computeLocalScore(items: ModuleReadinessRecord[]): PlatformReadinessScore {
  const summary = calculateFallbackSummary(items)
  const total = Math.max(summary.totalModules, 1)
  const moduleScore = Number(((summary.readyModules * 80 + summary.foundationModules * 55 + summary.plannedModules * 25 + summary.notIntegratedModules * 10) / total).toFixed(2))
  const auditScore = Number(((summary.auditReadyModules * 60 + (total - summary.auditReadyModules) * 18) / total).toFixed(2))
  const securityScore = 32
  const integrationScore = Number(((summary.notIntegratedModules > 0 ? 12 : 36) + (summary.readyModules > 0 ? 8 : 0)).toFixed(2))
  const overall = Number((moduleScore * 0.35 + auditScore * 0.25 + securityScore * 0.25 + integrationScore * 0.15).toFixed(2))
  const band: PlatformReadinessScore['scoreBand'] =
    overall <= 24 ? 'early-foundation' : overall <= 49 ? 'foundation' : overall <= 74 ? 'readiness-candidate' : 'operational-candidate'
  return {
    overallScore: overall,
    scoreBand: band,
    scoreMode: 'frontend-local-fallback',
    certified: false,
    iec62443Certified: false,
    components: {
      moduleReadiness: {
        score: moduleScore,
        weight: 0.35,
        basis: 'runtimeStatus, readinessLevel, frontendReady, backendReady, apiReady',
      },
      auditReadiness: {
        score: auditScore,
        weight: 0.25,
        basis: 'auditReadiness, audit storage, audit verification placeholders',
      },
      securityPosture: {
        score: securityScore,
        weight: 0.25,
        basis: 'permission mode, certified flags, RBAC/SIEM/UCDE integration status',
      },
      integrationReadiness: {
        score: integrationScore,
        weight: 0.15,
        basis: 'integrationMode, edge/link runtime integration status',
      },
    },
    drivers: ['Local registry fallback is available.'],
    risks: ['Most modules are planned or not integrated.'],
    recommendations: ['Keep certification claims disabled and continue module foundations.'],
  }
}

function fallbackNavigationFromRegistry(items: ModuleReadinessRecord[]): PlatformNavigationModel {
  const rows: PlatformNavigationItem[] = items.map((item) => {
    const route = item.route || null
    const launchEnabled = Boolean(route) && (item.runtimeStatus === 'ready' || item.runtimeStatus === 'foundation')
    const status = item.runtimeStatus
    let launchLabel = launchEnabled ? 'Open Module' : 'Planned'
    let disabledReason: string | null = null
    let boundaryNote: string | null = null
    if (item.moduleId === 'reports') {
      launchLabel = 'Open Reports'
    } else if (item.moduleId === 'uconsole') {
      launchLabel = 'Current Dashboard'
    } else if (status === 'not-integrated') {
      launchLabel = 'Not Integrated'
      disabledReason = 'Module runtime is not integrated in current stage.'
      boundaryNote =
        item.moduleId === 'edge-fleet'
          ? 'EDGE remains a separate shared foundation boundary.'
          : item.moduleId === 'link-gateway'
            ? 'LINK remains a separate shared foundation boundary.'
            : 'This module remains a separate shared foundation boundary.'
    } else if (!launchEnabled) {
      launchLabel = 'Planned'
      disabledReason = 'Module route is not available in current stage.'
      boundaryNote = 'No runtime integration is performed from UConsole.'
    }
    return {
      moduleId: item.moduleId,
      moduleName: item.moduleName,
      route,
      launchEnabled,
      launchLabel,
      status,
      disabledReason,
      boundaryNote,
      readOnly: true,
      controlActionsEnabled: false,
      certified: false,
      iec62443Certified: false,
    }
  })
  return {
    navigationMode: 'read-only-module-launch',
    controlActionsEnabled: false,
    items: rows,
  }
}

async function loadRoleVisibilityPreview(role: ConsoleRole): Promise<void> {
  roleVisibilityError.value = ''
  try {
    const [rolesResult, summaryResult, policyResult, entriesResult, menuResult] = await Promise.all([
      getSupportedPackageRoles(),
      getRoleVisibilitySummary(),
      getRoleVisibility(role),
      getRoleEntries(role),
      getRoleMenuPreview(role),
    ])
    supportedRoles.value = rolesResult.length > 0 ? rolesResult : ['customer', 'engineer', 'admin']
    roleVisibilitySummary.value = summaryResult
    rolePolicy.value = policyResult
    roleEntries.value = entriesResult
    roleMenuPreview.value = menuResult
  } catch (error) {
    roleVisibilityError.value = normalizeError(error, 'Role visibility preview API unavailable. Showing empty role preview.')
    rolePolicy.value = {
      role,
      roleLabel: role === 'customer' ? 'Customer User' : role === 'engineer' ? 'Engineer User' : 'Admin User',
      visibilityMode: 'local-skeleton-role-visibility',
      realRbacIntegrated: false,
      authIntegrated: false,
      routeGuardIntegrated: false,
      readOnly: true,
      allowedEntryModes: role === 'customer' ? ['customer-application'] : role === 'engineer' ? ['engineer-diagnostics'] : ['admin-package-center'],
      hiddenEntryModes: [],
      visiblePackages: [],
      lockedPackages: [],
      hiddenPackages: [],
      menuPreview: [],
      hiddenOrLockedReasons: [],
      limitations: ['Role visibility preview fallback is active.'],
      certified: false,
      iec62443Certified: false,
    }
    roleEntries.value = {
      role,
      roleLabel: rolePolicy.value.roleLabel,
      entryMode: 'local-skeleton-role-entry-view',
      visiblePackages: [],
      lockedPackages: [],
      hiddenPackages: [],
      readOnly: true,
      controlActionsEnabled: false,
      realRbacIntegrated: false,
      authIntegrated: false,
      routeGuardIntegrated: false,
      certified: false,
      iec62443Certified: false,
    }
    roleMenuPreview.value = {
      role,
      roleLabel: rolePolicy.value.roleLabel,
      menuPreviewMode: 'local-skeleton-role-menu-preview',
      items: [],
      readOnly: true,
      realRbacIntegrated: false,
      authIntegrated: false,
      routeGuardIntegrated: false,
      certified: false,
      iec62443Certified: false,
    }
  }
}

async function loadDashboard(): Promise<void> {
  loading.value = true
  apiError.value = ''
  scoreFallbackAlert.value = ''
  navigationFallbackAlert.value = ''
  packageCenterError.value = ''
  try {
    const [healthResult, readinessResult] = await Promise.all([getConsoleHealth(), getConsoleReportsReadiness()])
    health.value = healthResult
    reportsReadiness.value = readinessResult

    try {
      const [registryResult, summaryResult] = await Promise.all([getConsoleReadinessRegistry(), getConsoleReadinessSummary()])
      modules.value = registryResult.items
      registrySummary.value = summaryResult
    } catch (registryError) {
      apiError.value = normalizeError(registryError, 'Registry API unavailable. Showing local fallback summary.')
      try {
        const modulesResult = await getConsoleModules()
        modules.value = modulesResult.map((item) => asReadinessRecord(item))
      } catch {
        modules.value = [...fallbackModules]
      }
      registrySummary.value = calculateFallbackSummary(modules.value)
    }

    try {
      readinessScore.value = await getConsoleReadinessScore()
    } catch (scoreError) {
      scoreFallbackAlert.value = normalizeError(scoreError, 'Readiness score API unavailable. Using frontend local score.')
      readinessScore.value = computeLocalScore(modules.value)
    }

    try {
      navigationModel.value = await getConsoleNavigationModules()
    } catch (navigationError) {
      navigationFallbackAlert.value = normalizeError(navigationError, 'Navigation API unavailable. Using registry-derived navigation.')
      navigationModel.value = fallbackNavigationFromRegistry(modules.value)
    }

    legacySummary.value = await getConsoleOperationsSummary()

    try {
      const [packageHealth, packageList, packageSummaryResult, entryCenter, patchResult, lockedResult] = await Promise.all([
        getPackageCenterHealth(),
        getModulePackages(),
        getPackageSummary(),
        getPackageEntries(),
        getPatchReadiness(),
        getLockedPackages(),
      ])
      packageCenterHealth.value = packageHealth
      packages.value = packageList.items
      packageSummary.value = packageSummaryResult
      packageEntries.value = entryCenter
      patchReadiness.value = patchResult
      lockedPackages.value = lockedResult
      await loadRoleVisibilityPreview(selectedRole.value)
    } catch (packageError) {
      packageCenterError.value = normalizeError(packageError, 'Package Center API unavailable. Using local fallback package state.')
      packages.value = []
      packageEntries.value = {
        customerApplications: [],
        engineerWorkspace: [],
        adminPackageCenter: [],
        lockedPackages: [],
        entryMode: 'local-skeleton-entry-center',
        roleAware: true,
        runtimeLinked: false,
        certified: false,
        iec62443Certified: false,
      }
      patchReadiness.value = {
        patchMode: 'local-skeleton-patch-readiness',
        patchActionsEnabled: false,
        packages: [],
        upgradeRequiredPackages: [],
        patchReadyPackages: [],
        licenseServerIntegrated: false,
        limitations: ['Package Center fallback active.'],
        certified: false,
        iec62443Certified: false,
      }
      lockedPackages.value = []
      await loadRoleVisibilityPreview(selectedRole.value)
    }
  } catch (error) {
    apiError.value = normalizeError(error, 'UConsole API unavailable. Showing local fallback summary.')
    modules.value = [...fallbackModules]
    registrySummary.value = calculateFallbackSummary(modules.value)
    readinessScore.value = computeLocalScore(modules.value)
    navigationModel.value = fallbackNavigationFromRegistry(modules.value)
    packageCenterError.value = 'Package Center API unavailable. Using local fallback package state.'
    await loadRoleVisibilityPreview(selectedRole.value)
  } finally {
    loading.value = false
  }
}

async function openHealthDetail(moduleId: string): Promise<void> {
  const current = modules.value.find((item) => item.moduleId === moduleId) || null
  selectedHealthDetail.value = current
  showHealthDrawer.value = true
  loadingHealthDetail.value = true
  try {
    selectedHealthDetail.value = await getConsoleModuleHealth(moduleId)
  } catch {
    selectedHealthDetail.value = current
  } finally {
    loadingHealthDetail.value = false
  }
}

async function refreshAllHealthDetails(): Promise<void> {
  try {
    const payload = await getConsoleAllModuleHealth()
    modules.value = payload.items
    registrySummary.value = calculateFallbackSummary(payload.items)
    if (readinessScore.value.scoreMode === 'frontend-local-fallback') {
      readinessScore.value = computeLocalScore(payload.items)
    }
    if (navigationFallbackAlert.value) {
      navigationModel.value = fallbackNavigationFromRegistry(payload.items)
    }
  } catch {
    // keep non-blocking read-only fallback behavior
  }
}

function goToRoute(path: string): void {
  if (!path) {
    return
  }
  void router.push(path)
}

function launchModule(item: PlatformNavigationItem): void {
  if (!item.launchEnabled || !item.route) {
    return
  }
  void router.push(item.route)
}

async function openPackageDetail(packageIdOrModuleId: string): Promise<void> {
  showPackageDrawer.value = true
  loadingPackageDetail.value = true
  selectedPackageDetail.value = packages.value.find((item) => item.packageId === packageIdOrModuleId || item.moduleId === packageIdOrModuleId) || null
  try {
    const detail = await getModulePackageDetail(packageIdOrModuleId)
    selectedPackageDetail.value = detail.item
  } catch {
    // keep fallback detail from list.
  } finally {
    loadingPackageDetail.value = false
  }
}

function openPackageEntry(route: string, enabled: boolean, visible: boolean): void {
  if (!enabled || !visible || !route) {
    return
  }
  void router.push(route)
}

function resetPackageFilters(): void {
  packageFilters.moduleId = ''
  packageFilters.packageCategory = ''
  packageFilters.installed = ''
  packageFilters.entitled = ''
  packageFilters.enabled = ''
  packageFilters.visible = ''
  packageFilters.patchStatus = ''
  packageFilters.role = ''
}

watch(
  () => selectedRole.value,
  (role) => {
    void loadRoleVisibilityPreview(role)
  }
)

onMounted(() => {
  void loadDashboard()
})
</script>

<template>
  <div class="operations-page">
    <el-card shadow="never" class="hero-card block-space">
      <div class="page-header">
        <div>
          <h1>UConsole / Platform Operations Dashboard</h1>
          <p>Read-only platform operations overview for VANTARIS ONE modules.</p>
        </div>
        <el-space wrap>
          <el-tag type="info">runtimeMode: {{ health.runtimeMode }}</el-tag>
          <el-tag type="success">provider: {{ health.provider }}</el-tag>
          <el-tag>sourceSemantics: {{ health.sourceSemantics }}</el-tag>
          <el-tag type="warning">readOnly: {{ health.readOnly }}</el-tag>
          <el-tag>controlActionsEnabled: {{ health.controlActionsEnabled }}</el-tag>
          <el-tag>certified: {{ health.certified }}</el-tag>
          <el-tag>iec62443Certified: {{ health.iec62443Certified }}</el-tag>
        </el-space>
      </div>
    </el-card>

    <el-alert
      v-if="apiError"
      type="warning"
      show-icon
      :closable="false"
      :title="apiError"
      class="block-space"
    />

    <el-alert
      v-if="scoreFallbackAlert"
      type="warning"
      show-icon
      :closable="false"
      :title="scoreFallbackAlert"
      class="block-space"
    />

    <el-alert
      v-if="navigationFallbackAlert"
      type="warning"
      show-icon
      :closable="false"
      :title="navigationFallbackAlert"
      class="block-space"
    />

    <el-card shadow="never" class="block-space">
      <template #header>
        <div class="section-title">Platform Readiness Score</div>
      </template>
      <el-skeleton v-if="loading" :rows="4" animated />
      <template v-else>
        <el-descriptions :column="3" border class="block-space">
          <el-descriptions-item label="overallScore">{{ readinessScore.overallScore }}</el-descriptions-item>
          <el-descriptions-item label="scoreBand">{{ readinessScore.scoreBand }}</el-descriptions-item>
          <el-descriptions-item label="scoreMode">{{ readinessScore.scoreMode }}</el-descriptions-item>
          <el-descriptions-item label="certified">{{ readinessScore.certified }}</el-descriptions-item>
          <el-descriptions-item label="iec62443Certified">{{ readinessScore.iec62443Certified }}</el-descriptions-item>
        </el-descriptions>
        <el-alert
          type="info"
          show-icon
          :closable="false"
          title="Readiness score is derived from the local registry. It is not a certification result."
          description="The score is an operational planning signal for local readiness, not a compliance or certification outcome."
        />
      </template>
    </el-card>

    <el-card shadow="never" class="block-space">
      <template #header>
        <div class="section-title">Score Breakdown</div>
      </template>
      <el-skeleton v-if="loading" :rows="4" animated />
      <el-table v-else :data="[
        { key: 'moduleReadiness', value: readinessScore.components.moduleReadiness },
        { key: 'auditReadiness', value: readinessScore.components.auditReadiness },
        { key: 'securityPosture', value: readinessScore.components.securityPosture },
        { key: 'integrationReadiness', value: readinessScore.components.integrationReadiness },
      ]" row-key="key" empty-text="No score breakdown">
        <el-table-column prop="key" label="component" min-width="180" />
        <el-table-column label="score" min-width="100">
          <template #default="{ row }">{{ row.value.score }}</template>
        </el-table-column>
        <el-table-column label="weight" min-width="100">
          <template #default="{ row }">{{ row.value.weight }}</template>
        </el-table-column>
        <el-table-column label="basis" min-width="300">
          <template #default="{ row }">{{ row.value.basis }}</template>
        </el-table-column>
        <el-table-column label="score meaning" min-width="280">
          <template #default="{ row }">{{ getScoreMeaning(row.value.score) }}</template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-card shadow="never" class="block-space">
      <template #header>
        <div class="section-title">Drivers / Risks / Recommendations</div>
      </template>
      <el-skeleton v-if="loading" :rows="4" animated />
      <template v-else>
        <el-card shadow="never" class="block-space">
          <template #header>Drivers (improves score)</template>
          <ul class="inline-list">
            <li v-for="item in readinessScore.drivers" :key="item">{{ item }}</li>
          </ul>
        </el-card>
        <el-card shadow="never" class="block-space">
          <template #header>Risks (lowers score)</template>
          <ul class="inline-list">
            <li v-for="item in readinessScore.risks" :key="item">{{ item }}</li>
          </ul>
        </el-card>
        <el-card shadow="never">
          <template #header>Recommendations (next work)</template>
          <ul class="inline-list">
            <li v-for="item in readinessScore.recommendations" :key="item">{{ item }}</li>
          </ul>
        </el-card>
      </template>
    </el-card>

    <el-card shadow="never" class="block-space">
      <template #header>
        <div class="section-title">Registry Summary</div>
      </template>
      <el-skeleton v-if="loading" :rows="3" animated />
      <el-descriptions v-else :column="4" border>
        <el-descriptions-item label="totalModules">{{ registrySummary.totalModules }}</el-descriptions-item>
        <el-descriptions-item label="readyModules">{{ registrySummary.readyModules }}</el-descriptions-item>
        <el-descriptions-item label="foundationModules">{{ registrySummary.foundationModules }}</el-descriptions-item>
        <el-descriptions-item label="plannedModules">{{ registrySummary.plannedModules }}</el-descriptions-item>
        <el-descriptions-item label="notIntegratedModules">{{ registrySummary.notIntegratedModules }}</el-descriptions-item>
        <el-descriptions-item label="auditReadyModules">{{ registrySummary.auditReadyModules }}</el-descriptions-item>
        <el-descriptions-item label="averageHealthScore">{{ registrySummary.averageHealthScore }}</el-descriptions-item>
        <el-descriptions-item label="certifiedModules">{{ registrySummary.certifiedModules }}</el-descriptions-item>
        <el-descriptions-item label="iec62443CertifiedModules">
          {{ registrySummary.iec62443CertifiedModules }}
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <el-card shadow="never" class="block-space">
      <template #header>
        <div class="section-title">Platform Module Navigation</div>
      </template>
      <el-skeleton v-if="loading" :rows="4" animated />
      <el-table v-else :data="navigationModel.items" row-key="moduleId" empty-text="No navigation data">
        <el-table-column prop="moduleName" label="moduleName" min-width="220" />
        <el-table-column prop="status" label="status" min-width="130" />
        <el-table-column prop="launchEnabled" label="launchEnabled" min-width="130" />
        <el-table-column label="route" min-width="170">
          <template #default="{ row }">
            <span v-if="row.route">{{ row.route }}</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="launchLabel" label="launchLabel" min-width="170" />
        <el-table-column prop="disabledReason" label="disabledReason" min-width="260" />
        <el-table-column prop="boundaryNote" label="boundaryNote" min-width="280" />
        <el-table-column label="launch" min-width="140" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" plain :disabled="!row.launchEnabled" @click="launchModule(row)">
              {{ row.launchLabel }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-alert
      type="info"
      show-icon
      :closable="false"
      title="Module Package Center uses local skeleton package states. License server, patch installer and runtime enable/disable actions are not integrated."
      class="block-space"
    />

    <el-alert
      v-if="packageCenterError"
      type="warning"
      show-icon
      :closable="false"
      :title="packageCenterError"
      class="block-space"
    />

    <el-card shadow="never" class="block-space">
      <template #header>
        <div class="section-title">Module Package & Entry Center</div>
      </template>
      <el-descriptions :column="4" border>
        <el-descriptions-item label="totalPackages">{{ packageSummary.totalPackages }}</el-descriptions-item>
        <el-descriptions-item label="installedPackages">{{ packageSummary.installedPackages }}</el-descriptions-item>
        <el-descriptions-item label="entitledPackages">{{ packageSummary.entitledPackages }}</el-descriptions-item>
        <el-descriptions-item label="enabledPackages">{{ packageSummary.enabledPackages }}</el-descriptions-item>
        <el-descriptions-item label="visiblePackages">{{ packageSummary.visiblePackages }}</el-descriptions-item>
        <el-descriptions-item label="lockedPackages">{{ packageSummary.lockedPackages }}</el-descriptions-item>
        <el-descriptions-item label="customerEntryCount">{{ packageSummary.customerEntryCount }}</el-descriptions-item>
        <el-descriptions-item label="engineerEntryCount">{{ packageSummary.engineerEntryCount }}</el-descriptions-item>
        <el-descriptions-item label="adminEntryCount">{{ packageSummary.adminEntryCount }}</el-descriptions-item>
        <el-descriptions-item label="patchReadyPackages">{{ packageSummary.patchReadyPackages }}</el-descriptions-item>
        <el-descriptions-item label="upgradeRequiredPackages">{{ packageSummary.upgradeRequiredPackages }}</el-descriptions-item>
        <el-descriptions-item label="patchActionsEnabled">{{ packageCenterHealth.patchActionsEnabled }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <el-card shadow="never" class="block-space">
      <template #header>
        <div class="section-title">Package State Table</div>
      </template>
      <div class="filter-row block-space">
        <el-input v-model="packageFilters.moduleId" placeholder="moduleId" clearable class="filter-field" />
        <el-input v-model="packageFilters.packageCategory" placeholder="packageCategory" clearable class="filter-field" />
        <el-select v-model="packageFilters.installed" placeholder="installed" clearable class="filter-field">
          <el-option label="true" value="true" />
          <el-option label="false" value="false" />
        </el-select>
        <el-select v-model="packageFilters.entitled" placeholder="entitled" clearable class="filter-field">
          <el-option label="true" value="true" />
          <el-option label="false" value="false" />
        </el-select>
        <el-select v-model="packageFilters.enabled" placeholder="enabled" clearable class="filter-field">
          <el-option label="true" value="true" />
          <el-option label="false" value="false" />
        </el-select>
        <el-select v-model="packageFilters.visible" placeholder="visible" clearable class="filter-field">
          <el-option label="true" value="true" />
          <el-option label="false" value="false" />
        </el-select>
        <el-input v-model="packageFilters.patchStatus" placeholder="patchStatus" clearable class="filter-field" />
        <el-select v-model="packageFilters.role" placeholder="role" clearable class="filter-field">
          <el-option label="customer" value="customer" />
          <el-option label="engineer" value="engineer" />
          <el-option label="admin" value="admin" />
        </el-select>
        <el-button @click="resetPackageFilters">Reset</el-button>
      </div>
      <el-table :data="filteredPackages" row-key="packageId" empty-text="No package state data">
        <el-table-column prop="packageCode" label="packageCode" min-width="150" />
        <el-table-column prop="packageName" label="packageName" min-width="180" />
        <el-table-column prop="moduleId" label="moduleId" min-width="130" />
        <el-table-column prop="installed" label="installed" min-width="100" />
        <el-table-column prop="entitled" label="entitled" min-width="100" />
        <el-table-column prop="enabled" label="enabled" min-width="100" />
        <el-table-column prop="visible" label="visible" min-width="100" />
        <el-table-column prop="installedVersion" label="installedVersion" min-width="140" />
        <el-table-column prop="availableVersion" label="availableVersion" min-width="140" />
        <el-table-column prop="patchStatus" label="patchStatus" min-width="140" />
        <el-table-column prop="lockedReason" label="lockedReason" min-width="220" />
        <el-table-column label="actions" min-width="320" fixed="right">
          <template #default="{ row }">
            <el-space wrap>
              <el-button link type="primary" @click="openPackageDetail(row.packageId)">View Package Detail</el-button>
              <el-button
                link
                type="primary"
                :disabled="!(row.customerEntry.visible && row.customerEntry.enabled)"
                @click="openPackageEntry(row.customerEntry.route, row.customerEntry.enabled, row.customerEntry.visible)"
              >
                Open Customer Entry
              </el-button>
              <el-button
                link
                type="primary"
                :disabled="!(row.engineerEntry.visible && row.engineerEntry.enabled)"
                @click="openPackageEntry(row.engineerEntry.route, row.engineerEntry.enabled, row.engineerEntry.visible)"
              >
                Open Engineer Entry
              </el-button>
            </el-space>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-card shadow="never" class="block-space">
      <template #header>
        <div class="section-title">Role-Based Module Visibility Preview</div>
      </template>
      <el-alert
        type="info"
        show-icon
        :closable="false"
        title="Role-based visibility is a local skeleton preview. Real RBAC, auth enforcement and route guards are not integrated."
        class="block-space"
      />
      <el-alert
        v-if="roleVisibilityError"
        type="warning"
        show-icon
        :closable="false"
        :title="roleVisibilityError"
        class="block-space"
      />
      <div class="filter-row block-space">
        <el-select v-model="selectedRole" placeholder="role selector" class="filter-field">
          <el-option
            v-for="role in supportedRoles"
            :key="role"
            :label="role === 'customer' ? 'Customer' : role === 'engineer' ? 'Engineer' : 'Admin'"
            :value="role"
          />
        </el-select>
      </div>
      <el-descriptions :column="4" border class="block-space">
        <el-descriptions-item label="supportedRoles">{{ roleVisibilitySummary.supportedRoles.join(', ') }}</el-descriptions-item>
        <el-descriptions-item label="customerVisibleCount">{{ roleVisibilitySummary.customerVisibleCount }}</el-descriptions-item>
        <el-descriptions-item label="engineerVisibleCount">{{ roleVisibilitySummary.engineerVisibleCount }}</el-descriptions-item>
        <el-descriptions-item label="adminVisibleCount">{{ roleVisibilitySummary.adminVisibleCount }}</el-descriptions-item>
        <el-descriptions-item label="lockedPackageCount">{{ roleVisibilitySummary.lockedPackageCount }}</el-descriptions-item>
        <el-descriptions-item label="hiddenPackageCount">{{ roleVisibilitySummary.hiddenPackageCount }}</el-descriptions-item>
        <el-descriptions-item label="realRbacIntegrated">{{ roleVisibilitySummary.realRbacIntegrated }}</el-descriptions-item>
        <el-descriptions-item label="routeGuardIntegrated">{{ roleVisibilitySummary.routeGuardIntegrated }}</el-descriptions-item>
      </el-descriptions>
      <el-descriptions :column="2" border class="block-space">
        <el-descriptions-item label="role">{{ rolePolicy.role }}</el-descriptions-item>
        <el-descriptions-item label="visibilityMode">{{ rolePolicy.visibilityMode }}</el-descriptions-item>
        <el-descriptions-item label="allowedEntryModes">{{ rolePolicy.allowedEntryModes.join(', ') || '-' }}</el-descriptions-item>
        <el-descriptions-item label="hiddenEntryModes">{{ rolePolicy.hiddenEntryModes.join(', ') || '-' }}</el-descriptions-item>
        <el-descriptions-item label="realRbacIntegrated">{{ rolePolicy.realRbacIntegrated }}</el-descriptions-item>
        <el-descriptions-item label="authIntegrated">{{ rolePolicy.authIntegrated }}</el-descriptions-item>
        <el-descriptions-item label="routeGuardIntegrated">{{ rolePolicy.routeGuardIntegrated }}</el-descriptions-item>
        <el-descriptions-item label="readOnly">{{ rolePolicy.readOnly }}</el-descriptions-item>
      </el-descriptions>
      <el-text>{{ rolePolicy.limitations.join(' | ') }}</el-text>
    </el-card>

    <el-card shadow="never" class="block-space">
      <template #header><div class="section-title">Role Entries</div></template>
      <el-descriptions :column="3" border class="block-space">
        <el-descriptions-item label="visiblePackages">{{ roleEntries.visiblePackages.length }}</el-descriptions-item>
        <el-descriptions-item label="lockedPackages">{{ roleEntries.lockedPackages.length }}</el-descriptions-item>
        <el-descriptions-item label="hiddenPackages">{{ roleEntries.hiddenPackages.length }}</el-descriptions-item>
      </el-descriptions>
      <el-table :data="roleEntries.visiblePackages" row-key="packageCode" empty-text="No visible entries for selected role">
        <el-table-column prop="packageCode" label="packageCode" min-width="150" />
        <el-table-column prop="moduleId" label="moduleId" min-width="130" />
        <el-table-column prop="entryMode" label="entryMode" min-width="170" />
        <el-table-column prop="label" label="label" min-width="180" />
        <el-table-column prop="route" label="route" min-width="170" />
        <el-table-column prop="visible" label="visible" min-width="100" />
        <el-table-column prop="enabled" label="enabled" min-width="100" />
      </el-table>
    </el-card>

    <el-card shadow="never" class="block-space">
      <template #header><div class="section-title">Menu Preview Table</div></template>
      <el-table :data="roleMenuPreview.items" row-key="packageCode" empty-text="No menu preview data">
        <el-table-column prop="label" label="label" min-width="180" />
        <el-table-column prop="route" label="route" min-width="170" />
        <el-table-column prop="packageCode" label="packageCode" min-width="150" />
        <el-table-column prop="moduleId" label="moduleId" min-width="130" />
        <el-table-column prop="entryMode" label="entryMode" min-width="170" />
        <el-table-column prop="visible" label="visible" min-width="100" />
        <el-table-column prop="enabled" label="enabled" min-width="100" />
        <el-table-column prop="lockedReason" label="lockedReason" min-width="220" />
      </el-table>
    </el-card>

    <el-card shadow="never" class="block-space">
      <template #header><div class="section-title">Hidden / Locked Reasons</div></template>
      <el-table :data="rolePolicy.hiddenOrLockedReasons" row-key="packageCode" empty-text="No hidden or locked reasons">
        <el-table-column prop="packageCode" label="packageCode" min-width="150" />
        <el-table-column prop="moduleName" label="moduleName" min-width="220" />
        <el-table-column prop="role" label="role" min-width="120" />
        <el-table-column prop="reason" label="reason" min-width="260" />
      </el-table>
    </el-card>

    <el-card shadow="never" class="block-space">
      <template #header><div class="section-title">Customer Applications</div></template>
      <el-table :data="roleVisibleCustomerApplications" row-key="packageCode" empty-text="No customer applications for selected role">
        <el-table-column prop="moduleName" label="label" min-width="200" />
        <el-table-column label="route" min-width="180">
          <template #default="{ row }">{{ row.route || '-' }}</template>
        </el-table-column>
        <el-table-column label="enabled/visible" min-width="140">
          <template #default="{ row }">{{ row.enabled }} / {{ row.visible }}</template>
        </el-table-column>
        <el-table-column prop="lockedReason" label="lockedReason" min-width="240" />
      </el-table>
    </el-card>

    <el-card shadow="never" class="block-space">
      <template #header><div class="section-title">Engineer Workspace</div></template>
      <el-alert
        type="info"
        show-icon
        :closable="false"
        title="Engineer workspace entries are placeholder-only and do not connect to EDGE/LINK runtime in this stage."
        class="block-space"
      />
      <el-table :data="roleVisibleEngineerWorkspace" row-key="packageCode" empty-text="No engineer entries for selected role">
        <el-table-column prop="moduleName" label="label" min-width="220" />
        <el-table-column label="route" min-width="180">
          <template #default="{ row }">{{ row.route || '-' }}</template>
        </el-table-column>
        <el-table-column label="enabled/visible" min-width="140">
          <template #default="{ row }">{{ row.enabled }} / {{ row.visible }}</template>
        </el-table-column>
        <el-table-column label="lockedReason" min-width="240">
          <template #default="{ row }">{{ row.lockedReason || '-' }}</template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-card shadow="never" class="block-space">
      <template #header><div class="section-title">Admin Package Center</div></template>
      <el-table :data="roleAdminPackageCenter" row-key="packageId" empty-text="No admin entries for selected role">
        <el-table-column prop="moduleName" label="moduleName" min-width="220" />
        <el-table-column label="entryLabel" min-width="170">
          <template #default="{ row }">{{ row.entry.label }}</template>
        </el-table-column>
        <el-table-column prop="patchStatus" label="patchStatus" min-width="140" />
        <el-table-column prop="upgradeRequired" label="upgradeRequired" min-width="130" />
        <el-table-column label="entitled/enabled/visible" min-width="170">
          <template #default="{ row }">{{ row.entitled }} / {{ row.enabled }} / {{ row.visible }}</template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-card shadow="never" class="block-space">
      <template #header><div class="section-title">Locked Packages</div></template>
      <el-table :data="lockedPackages" row-key="packageId" empty-text="No locked packages">
        <el-table-column prop="packageCode" label="packageCode" min-width="150" />
        <el-table-column prop="moduleName" label="moduleName" min-width="220" />
        <el-table-column prop="lockedReason" label="lockedReason" min-width="260" />
        <el-table-column prop="patchStatus" label="patchStatus" min-width="130" />
      </el-table>
    </el-card>

    <el-card shadow="never" class="block-space">
      <template #header><div class="section-title">Patch Readiness</div></template>
      <el-descriptions :column="3" border class="block-space">
        <el-descriptions-item label="patchMode">{{ patchReadiness.patchMode }}</el-descriptions-item>
        <el-descriptions-item label="patchActionsEnabled">{{ patchReadiness.patchActionsEnabled }}</el-descriptions-item>
        <el-descriptions-item label="licenseServerIntegrated">{{ patchReadiness.licenseServerIntegrated }}</el-descriptions-item>
      </el-descriptions>
      <el-descriptions :column="1" border class="block-space">
        <el-descriptions-item label="upgradeRequiredPackages">{{ patchReadiness.upgradeRequiredPackages.join(', ') || '-' }}</el-descriptions-item>
        <el-descriptions-item label="patchReadyPackages">{{ patchReadiness.patchReadyPackages.join(', ') || '-' }}</el-descriptions-item>
      </el-descriptions>
      <el-text>{{ patchReadiness.limitations.join(' | ') }}</el-text>
    </el-card>

    <el-card shadow="never" class="block-space">
      <template #header>
        <div class="section-title">Reports Readiness</div>
      </template>
      <el-skeleton v-if="loading" :rows="4" animated />
      <template v-else>
        <el-descriptions :column="3" border class="block-space">
          <el-descriptions-item label="routeReady">{{ reportsReadiness.routeReady }}</el-descriptions-item>
          <el-descriptions-item label="menuReady">{{ reportsReadiness.menuReady }}</el-descriptions-item>
          <el-descriptions-item label="queryReady">{{ reportsReadiness.queryReady }}</el-descriptions-item>
          <el-descriptions-item label="exportReady">{{ reportsReadiness.exportReady }}</el-descriptions-item>
          <el-descriptions-item label="manifestReady">{{ reportsReadiness.manifestReady }}</el-descriptions-item>
          <el-descriptions-item label="auditStoreReady">{{ reportsReadiness.auditStoreReady }}</el-descriptions-item>
          <el-descriptions-item label="auditVerifyReady">{{ reportsReadiness.auditVerifyReady }}</el-descriptions-item>
          <el-descriptions-item label="permissionPlaceholderReady">
            {{ reportsReadiness.permissionPlaceholderReady }}
          </el-descriptions-item>
          <el-descriptions-item label="auditExportReady">{{ reportsReadiness.auditExportReady }}</el-descriptions-item>
          <el-descriptions-item label="certified">{{ reportsReadiness.certified }}</el-descriptions-item>
          <el-descriptions-item label="iec62443Certified">{{ reportsReadiness.iec62443Certified }}</el-descriptions-item>
        </el-descriptions>
        <el-button type="primary" plain @click="goToRoute('/reports')">Go to Reports</el-button>
      </template>
    </el-card>

    <el-card shadow="never" class="block-space">
      <template #header>
        <div class="section-title">Module Readiness Registry</div>
      </template>
      <el-skeleton v-if="loading" :rows="4" animated />
      <template v-else>
        <div class="filter-row block-space">
          <el-select v-model="moduleFilters.runtimeStatus" placeholder="runtimeStatus" clearable class="filter-field">
            <el-option label="ready" value="ready" />
            <el-option label="foundation" value="foundation" />
            <el-option label="planned" value="planned" />
            <el-option label="not-integrated" value="not-integrated" />
          </el-select>
          <el-select v-model="moduleFilters.lifecycleStage" placeholder="lifecycleStage" clearable class="filter-field">
            <el-option label="runnable-readiness" value="runnable-readiness" />
            <el-option label="platform-foundation" value="platform-foundation" />
            <el-option label="planned" value="planned" />
            <el-option label="not-integrated" value="not-integrated" />
          </el-select>
          <el-select v-model="moduleFilters.auditReadiness" placeholder="auditReadiness" clearable class="filter-field">
            <el-option label="ready" value="ready" />
            <el-option label="foundation" value="foundation" />
            <el-option label="limited" value="limited" />
            <el-option label="planned" value="planned" />
            <el-option label="not-integrated" value="not-integrated" />
          </el-select>
          <el-select v-model="moduleFilters.permissionMode" placeholder="permissionMode" clearable class="filter-field">
            <el-option label="placeholder-allow" value="placeholder-allow" />
            <el-option label="not-integrated" value="not-integrated" />
          </el-select>
        </div>
        <el-empty v-if="!hasModules" description="No module summary available." />
        <el-table v-else :data="filteredModules" row-key="moduleId" empty-text="No module summary">
          <el-table-column prop="moduleId" label="moduleId" min-width="120" />
          <el-table-column prop="moduleName" label="moduleName" min-width="220" />
          <el-table-column prop="moduleType" label="moduleType" min-width="140" />
          <el-table-column prop="domain" label="domain" min-width="150" />
          <el-table-column prop="runtimeStatus" label="runtimeStatus" min-width="120" />
          <el-table-column prop="readinessLevel" label="readinessLevel" min-width="170" />
          <el-table-column prop="lifecycleStage" label="lifecycleStage" min-width="170" />
          <el-table-column prop="healthScore" label="healthScore" min-width="110" />
          <el-table-column label="limitationsCount" min-width="130">
            <template #default="{ row }">{{ row.limitations.length }}</template>
          </el-table-column>
          <el-table-column label="dependencyCount" min-width="130">
            <template #default="{ row }">{{ row.dependencies.length }}</template>
          </el-table-column>
          <el-table-column label="nextActionLabel" min-width="180">
            <template #default="{ row }">{{ getNextActionLabel(row) }}</template>
          </el-table-column>
          <el-table-column prop="frontendReady" label="frontendReady" min-width="120" />
          <el-table-column prop="backendReady" label="backendReady" min-width="120" />
          <el-table-column prop="apiReady" label="apiReady" min-width="100" />
          <el-table-column prop="auditReadiness" label="auditReadiness" min-width="120" />
          <el-table-column prop="permissionMode" label="permissionMode" min-width="150" />
          <el-table-column prop="dataPersistenceMode" label="dataPersistenceMode" min-width="170" />
          <el-table-column prop="integrationMode" label="integrationMode" min-width="160" />
          <el-table-column label="health" min-width="120">
            <template #default="{ row }">
              <el-button link type="primary" @click="openHealthDetail(row.moduleId)">View Health</el-button>
            </template>
          </el-table-column>
          <el-table-column label="route" min-width="150">
            <template #default="{ row }">
              <el-button v-if="row.route" link type="primary" @click="goToRoute(row.route)">
                {{ row.route }}
              </el-button>
              <span v-else>-</span>
            </template>
          </el-table-column>
        </el-table>
      </template>
    </el-card>

    <el-card shadow="never" class="block-space">
      <template #header>
        <div class="section-title">Security Posture / Limitations</div>
      </template>
      <el-skeleton v-if="loading" :rows="3" animated />
      <template v-else>
        <el-descriptions :column="2" border class="block-space">
          <el-descriptions-item label="realRbacIntegrated">
            {{ legacySummary.securityPosture.realRbacIntegrated }}
          </el-descriptions-item>
          <el-descriptions-item label="dbAuditIntegrated">
            {{ legacySummary.securityPosture.dbAuditIntegrated }}
          </el-descriptions-item>
          <el-descriptions-item label="siemIntegrated">{{ legacySummary.securityPosture.siemIntegrated }}</el-descriptions-item>
          <el-descriptions-item label="ucdeRuntimeIntegrated">
            {{ legacySummary.securityPosture.ucdeRuntimeIntegrated }}
          </el-descriptions-item>
          <el-descriptions-item label="edgeRuntimeIntegrated">
            {{ false }}
          </el-descriptions-item>
          <el-descriptions-item label="linkRuntimeIntegrated">
            {{ false }}
          </el-descriptions-item>
          <el-descriptions-item label="certified">{{ legacySummary.securityPosture.certified }}</el-descriptions-item>
          <el-descriptions-item label="iec62443Certified">
            {{ legacySummary.securityPosture.iec62443Certified }}
          </el-descriptions-item>
        </el-descriptions>
        <el-alert
          type="info"
          show-icon
          :closable="false"
          title="Read-only dashboard foundation."
          description="Permission placeholder only; no production RBAC integration."
          class="block-space"
        />
        <el-card shadow="never" class="block-space">
          <template #header>Highlights</template>
          <ul class="inline-list">
            <li v-for="item in legacySummary.highlights" :key="item">{{ item }}</li>
          </ul>
        </el-card>
        <el-card shadow="never" class="block-space">
          <template #header>Warnings</template>
          <ul class="inline-list">
            <li v-for="item in legacySummary.warnings" :key="item">{{ item }}</li>
          </ul>
        </el-card>
        <el-button plain @click="refreshAllHealthDetails">Refresh Health Details</el-button>
      </template>
    </el-card>

    <el-drawer v-model="showHealthDrawer" title="Module Health Detail" size="52%">
      <el-skeleton v-if="loadingHealthDetail" :rows="8" animated />
      <el-empty v-else-if="!selectedHealthDetail" description="No module selected." />
      <template v-else>
        <el-card shadow="never" class="block-space">
          <template #header>Module Overview</template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="moduleId">{{ selectedHealthDetail.moduleId }}</el-descriptions-item>
            <el-descriptions-item label="moduleName">{{ selectedHealthDetail.moduleName }}</el-descriptions-item>
            <el-descriptions-item label="moduleType">{{ selectedHealthDetail.moduleType }}</el-descriptions-item>
            <el-descriptions-item label="domain">{{ selectedHealthDetail.domain }}</el-descriptions-item>
            <el-descriptions-item label="runtimeStatus">{{ selectedHealthDetail.runtimeStatus }}</el-descriptions-item>
            <el-descriptions-item label="readinessLevel">{{ selectedHealthDetail.readinessLevel }}</el-descriptions-item>
            <el-descriptions-item label="lifecycleStage">{{ selectedHealthDetail.lifecycleStage }}</el-descriptions-item>
            <el-descriptions-item label="healthScore">{{ selectedHealthDetail.healthScore }}</el-descriptions-item>
            <el-descriptions-item label="route">{{ selectedHealthDetail.route || '-' }}</el-descriptions-item>
            <el-descriptions-item label="integrationMode">{{ selectedHealthDetail.integrationMode }}</el-descriptions-item>
            <el-descriptions-item label="dataPersistenceMode">{{ selectedHealthDetail.dataPersistenceMode }}</el-descriptions-item>
          </el-descriptions>
        </el-card>

        <el-card shadow="never" class="block-space">
          <template #header>Readiness Flags</template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="frontendReady">{{ selectedHealthDetail.frontendReady }}</el-descriptions-item>
            <el-descriptions-item label="backendReady">{{ selectedHealthDetail.backendReady }}</el-descriptions-item>
            <el-descriptions-item label="apiReady">{{ selectedHealthDetail.apiReady }}</el-descriptions-item>
            <el-descriptions-item label="auditReadiness">{{ selectedHealthDetail.auditReadiness }}</el-descriptions-item>
            <el-descriptions-item label="permissionMode">{{ selectedHealthDetail.permissionMode }}</el-descriptions-item>
            <el-descriptions-item label="readOnly">{{ selectedHealthDetail.readOnly }}</el-descriptions-item>
            <el-descriptions-item label="controlActionsEnabled">{{ selectedHealthDetail.controlActionsEnabled }}</el-descriptions-item>
            <el-descriptions-item label="certified">{{ selectedHealthDetail.certified }}</el-descriptions-item>
            <el-descriptions-item label="iec62443Certified">{{ selectedHealthDetail.iec62443Certified }}</el-descriptions-item>
          </el-descriptions>
        </el-card>

        <el-card shadow="never" class="block-space">
          <template #header>Health Details</template>
          <el-table
            :data="Object.entries(selectedHealthDetail.healthDetails).map(([key, value]) => ({ key, ...value }))"
            row-key="key"
            empty-text="No health details"
          >
            <el-table-column prop="key" label="key" min-width="130" />
            <el-table-column prop="status" label="status" min-width="120" />
            <el-table-column prop="label" label="label" min-width="150" />
            <el-table-column prop="score" label="score" min-width="90" />
            <el-table-column prop="message" label="message" min-width="280" />
          </el-table>
        </el-card>
        <el-card shadow="never" class="block-space">
          <template #header>Security Flags</template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="realRbacIntegrated">
              {{ selectedHealthDetail.securityFlags.realRbacIntegrated }}
            </el-descriptions-item>
            <el-descriptions-item label="dbAuditIntegrated">
              {{ selectedHealthDetail.securityFlags.dbAuditIntegrated }}
            </el-descriptions-item>
            <el-descriptions-item label="siemIntegrated">{{ selectedHealthDetail.securityFlags.siemIntegrated }}</el-descriptions-item>
            <el-descriptions-item label="ucdeRuntimeIntegrated">
              {{ selectedHealthDetail.securityFlags.ucdeRuntimeIntegrated }}
            </el-descriptions-item>
            <el-descriptions-item label="edgeRuntimeIntegrated">
              {{ selectedHealthDetail.securityFlags.edgeRuntimeIntegrated }}
            </el-descriptions-item>
            <el-descriptions-item label="linkRuntimeIntegrated">
              {{ selectedHealthDetail.securityFlags.linkRuntimeIntegrated }}
            </el-descriptions-item>
            <el-descriptions-item label="certified">{{ selectedHealthDetail.securityFlags.certified }}</el-descriptions-item>
            <el-descriptions-item label="iec62443Certified">
              {{ selectedHealthDetail.securityFlags.iec62443Certified }}
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
        <el-card shadow="never" class="block-space">
          <template #header>Limitations</template>
          <template v-if="selectedHealthDetail.limitations.length > 0">
            <ul class="inline-list">
              <li v-for="item in selectedHealthDetail.limitations" :key="item">{{ item }}</li>
            </ul>
          </template>
          <el-text v-else>
            No additional limitations declared for this readiness record.
          </el-text>
        </el-card>
        <el-card shadow="never" class="block-space">
          <template #header>Dependencies</template>
          <template v-if="selectedHealthDetail.dependencies.length > 0">
            <ul class="inline-list">
              <li v-for="item in selectedHealthDetail.dependencies" :key="item">{{ item }}</li>
            </ul>
          </template>
          <el-text v-else>
            No runtime dependencies are invoked by UConsole in this stage.
          </el-text>
        </el-card>
        <el-card shadow="never" class="block-space">
          <template #header>Next Actions</template>
          <ul class="inline-list">
            <li v-for="item in getGeneratedNextActions(selectedHealthDetail)" :key="item">{{ item }}</li>
          </ul>
          <template v-if="selectedHealthDetail.boundaryNotes.length > 0">
            <el-divider />
            <ul class="inline-list">
              <li v-for="item in selectedHealthDetail.boundaryNotes" :key="item">{{ item }}</li>
            </ul>
          </template>
        </el-card>
      </template>
    </el-drawer>

    <el-drawer v-model="showPackageDrawer" title="Package Detail" size="52%">
      <el-skeleton v-if="loadingPackageDetail" :rows="8" animated />
      <el-empty v-else-if="!selectedPackageDetail" description="No package selected." />
      <template v-else>
        <el-descriptions :column="1" border>
          <el-descriptions-item label="packageOverview">
            {{ selectedPackageDetail.packageCode }} | {{ selectedPackageDetail.packageName }} | {{ selectedPackageDetail.moduleId }}
          </el-descriptions-item>
          <el-descriptions-item label="stateFlags">
            installed={{ selectedPackageDetail.installed }}, entitled={{ selectedPackageDetail.entitled }}, enabled={{ selectedPackageDetail.enabled }}, visible={{ selectedPackageDetail.visible }}
          </el-descriptions-item>
          <el-descriptions-item label="customerEntry">{{ selectedPackageDetail.customerEntry }}</el-descriptions-item>
          <el-descriptions-item label="engineerEntry">{{ selectedPackageDetail.engineerEntry }}</el-descriptions-item>
          <el-descriptions-item label="adminEntry">{{ selectedPackageDetail.adminEntry }}</el-descriptions-item>
          <el-descriptions-item label="roleVisibility">{{ selectedPackageDetail.roleVisibility }}</el-descriptions-item>
          <el-descriptions-item label="patch/version">
            {{ selectedPackageDetail.patchStatus }} | {{ selectedPackageDetail.installedVersion }} -> {{ selectedPackageDetail.availableVersion }}
          </el-descriptions-item>
          <el-descriptions-item label="limitations">{{ selectedPackageDetail.limitations.join(' | ') }}</el-descriptions-item>
          <el-descriptions-item label="nextActions">{{ selectedPackageDetail.nextActions.join(' | ') }}</el-descriptions-item>
        </el-descriptions>
      </template>
    </el-drawer>
  </div>
</template>

<style scoped>
.operations-page {
  padding: 16px;
}

.hero-card {
  border-left: 4px solid var(--el-color-primary);
}

.page-header h1 {
  margin: 0 0 4px;
  font-size: 1.25rem;
  font-weight: 600;
}

.page-header p {
  margin: 0;
  color: var(--el-text-color-secondary);
  font-size: 0.875rem;
}

.block-space {
  margin-bottom: 16px;
}

.section-title {
  font-weight: 600;
}

.inline-list {
  margin: 0;
  padding-left: 18px;
}

.filter-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
}

.filter-field {
  width: 220px;
}

.summary-block {
  margin: 0;
  font-size: 0.8125rem;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-word;
}
</style>

