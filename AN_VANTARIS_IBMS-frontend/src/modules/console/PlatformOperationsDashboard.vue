<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ApiError } from '@/services/api/errors'
import {
  getConsoleAllModuleHealth,
  getConsoleHealth,
  getConsoleModuleHealth,
  getConsoleModules,
  getConsoleOperationsSummary,
  getConsoleReadinessRegistry,
  getConsoleReadinessSummary,
  getConsoleReportsReadiness,
  type ConsoleHealth,
  type ModuleReadinessRecord,
  type ModuleReadinessSummary,
  type OperationsDashboardSummary,
  type PlatformModuleSummary,
  type ReportsReadinessSnapshot,
} from '@/services/api/console'

const router = useRouter()

const loading = ref(false)
const loadingHealthDetail = ref(false)
const apiError = ref('')
const showHealthDrawer = ref(false)
const selectedHealthDetail = ref<ModuleReadinessRecord | null>(null)

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

const moduleFilters = reactive({
  runtimeStatus: '',
  lifecycleStage: '',
  auditReadiness: '',
  permissionMode: '',
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
    lastUpdated: '',
    readOnly: true,
    controlActionsEnabled: false,
    certified: false,
    iec62443Certified: false,
  },
]

const hasModules = computed(() => filteredModules.value.length > 0)

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

function normalizeError(error: unknown): string {
  return error instanceof ApiError
    ? error.message
    : 'Registry API unavailable. Showing local fallback summary.'
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
    lifecycleStage: item.runtimeStatus === 'ready' ? 'runnable-readiness' : 'planned',
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

async function loadDashboard(): Promise<void> {
  loading.value = true
  apiError.value = ''
  try {
    const [healthResult, readinessResult] = await Promise.all([
      getConsoleHealth(),
      getConsoleReportsReadiness(),
    ])
    health.value = healthResult
    reportsReadiness.value = readinessResult

    try {
      const [registryResult, summaryResult] = await Promise.all([
        getConsoleReadinessRegistry(),
        getConsoleReadinessSummary(),
      ])
      modules.value = registryResult.items
      registrySummary.value = summaryResult
      legacySummary.value = await getConsoleOperationsSummary()
      return
    } catch (registryError) {
      apiError.value = normalizeError(registryError)
      try {
        const modulesResult = await getConsoleModules()
        modules.value = modulesResult.map((item) => asReadinessRecord(item))
      } catch {
        modules.value = [...fallbackModules]
      }
      registrySummary.value = calculateFallbackSummary(modules.value)
      legacySummary.value = await getConsoleOperationsSummary()
    }
  } catch (error) {
    apiError.value = normalizeError(error)
    modules.value = [...fallbackModules]
    registrySummary.value = calculateFallbackSummary(modules.value)
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

    <el-drawer v-model="showHealthDrawer" title="Module Health Detail" size="42%">
      <el-skeleton v-if="loadingHealthDetail" :rows="8" animated />
      <el-empty v-else-if="!selectedHealthDetail" description="No module selected." />
      <template v-else>
        <el-descriptions :column="1" border class="block-space">
          <el-descriptions-item label="moduleId">{{ selectedHealthDetail.moduleId }}</el-descriptions-item>
          <el-descriptions-item label="moduleName">{{ selectedHealthDetail.moduleName }}</el-descriptions-item>
          <el-descriptions-item label="runtimeStatus">{{ selectedHealthDetail.runtimeStatus }}</el-descriptions-item>
          <el-descriptions-item label="readinessLevel">{{ selectedHealthDetail.readinessLevel }}</el-descriptions-item>
          <el-descriptions-item label="lifecycleStage">{{ selectedHealthDetail.lifecycleStage }}</el-descriptions-item>
          <el-descriptions-item label="healthStatus">{{ selectedHealthDetail.healthStatus }}</el-descriptions-item>
          <el-descriptions-item label="healthScore">{{ selectedHealthDetail.healthScore }}</el-descriptions-item>
          <el-descriptions-item label="readOnly">{{ selectedHealthDetail.readOnly }}</el-descriptions-item>
          <el-descriptions-item label="controlActionsEnabled">
            {{ selectedHealthDetail.controlActionsEnabled }}
          </el-descriptions-item>
          <el-descriptions-item label="certified">{{ selectedHealthDetail.certified }}</el-descriptions-item>
          <el-descriptions-item label="iec62443Certified">
            {{ selectedHealthDetail.iec62443Certified }}
          </el-descriptions-item>
        </el-descriptions>
        <el-card shadow="never" class="block-space">
          <template #header>Health Details</template>
          <el-descriptions :column="1" border>
            <el-descriptions-item
              v-for="(detail, key) in selectedHealthDetail.healthDetails"
              :key="key"
              :label="key"
            >
              {{ detail.status }} | {{ detail.label }} | score={{ detail.score }} | {{ detail.message }}
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
        <el-card shadow="never" class="block-space">
          <template #header>Security Flags</template>
          <pre class="summary-block">{{ JSON.stringify(selectedHealthDetail.securityFlags, null, 2) }}</pre>
        </el-card>
        <el-card shadow="never" class="block-space">
          <template #header>Limitations</template>
          <ul class="inline-list">
            <li v-for="item in selectedHealthDetail.limitations" :key="item">{{ item }}</li>
          </ul>
        </el-card>
        <el-card shadow="never">
          <template #header>Dependencies</template>
          <ul class="inline-list">
            <li v-for="item in selectedHealthDetail.dependencies" :key="item">{{ item }}</li>
          </ul>
        </el-card>
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

