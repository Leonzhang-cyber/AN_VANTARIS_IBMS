<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ApiError } from '@/services/api/errors'
import {
  getConsoleHealth,
  getConsoleModules,
  getConsoleOperationsSummary,
  getConsoleReportsReadiness,
  type ConsoleHealth,
  type OperationsDashboardSummary,
  type PlatformModuleSummary,
  type ReportsReadinessSnapshot,
} from '@/services/api/console'

const router = useRouter()

const loading = ref(false)
const apiError = ref('')

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

const modules = ref<PlatformModuleSummary[]>([])
const summary = ref<OperationsDashboardSummary>({
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
    'No formal immutable evidence chain.',
    'No UCDE runtime integration.',
    'No IEC62443 certification claim.',
  ],
})

const hasModules = computed(() => modules.value.length > 0)

const fallbackModules: PlatformModuleSummary[] = [
  {
    moduleId: 'reports',
    moduleName: 'Reports',
    moduleType: 'platform-module',
    runtimeStatus: 'ready',
    readinessLevel: 'readiness-candidate',
    route: '/reports',
    frontendReady: true,
    backendReady: true,
    auditReadiness: true,
    permissionMode: 'placeholder-allow',
    dataPersistenceMode: 'local-jsonl-audit',
    securityNotes: 'Audit readiness foundation with placeholder permission mode.',
    certified: false,
    iec62443Certified: false,
  },
  {
    moduleId: 'uconsole',
    moduleName: 'UConsole / Platform Operations Dashboard',
    moduleType: 'platform-module',
    runtimeStatus: 'foundation',
    readinessLevel: 'r1-foundation',
    route: '/console/operations',
    frontendReady: true,
    backendReady: true,
    auditReadiness: false,
    permissionMode: 'placeholder-allow',
    dataPersistenceMode: 'none',
    securityNotes: 'Read-only dashboard foundation.',
    certified: false,
    iec62443Certified: false,
  },
]

function normalizeError(error: unknown): string {
  return error instanceof ApiError
    ? error.message
    : 'UConsole API unavailable. Showing local fallback summary.'
}

function buildFallbackSummary(items: PlatformModuleSummary[]): OperationsDashboardSummary {
  const readyModules = items.filter((item) => item.runtimeStatus === 'ready').length
  const foundationModules = items.filter((item) => item.runtimeStatus === 'foundation').length
  const plannedModules = items.filter((item) => item.runtimeStatus === 'planned').length
  const auditReadyModules = items.filter((item) => item.auditReadiness).length
  return {
    totals: {
      totalModules: items.length,
      readyModules,
      foundationModules,
      plannedModules,
      auditReadyModules,
      certifiedModules: 0,
      iec62443CertifiedModules: 0,
    },
    highlights: ['Reports readiness candidate', 'UConsole foundation'],
    warnings: [
      'Permission mode placeholder',
      'No IEC62443 certification claim',
      'No production RBAC integration',
      'Legacy docs may contain cross-system references but runtime is clean.',
    ],
    securityPosture: {
      auditReadinessFoundation: true,
      realRbacIntegrated: false,
      dbAuditIntegrated: false,
      siemIntegrated: false,
      ucdeRuntimeIntegrated: false,
      certified: false,
      iec62443Certified: false,
    },
  }
}

async function loadDashboard(): Promise<void> {
  loading.value = true
  apiError.value = ''
  try {
    const [healthResult, modulesResult, summaryResult, readinessResult] = await Promise.all([
      getConsoleHealth(),
      getConsoleModules(),
      getConsoleOperationsSummary(),
      getConsoleReportsReadiness(),
    ])
    health.value = healthResult
    modules.value = modulesResult
    summary.value = summaryResult
    reportsReadiness.value = readinessResult
  } catch (error) {
    apiError.value = normalizeError(error)
    modules.value = [...fallbackModules]
    summary.value = buildFallbackSummary(modules.value)
  } finally {
    loading.value = false
  }
}

function goToRoute(path: string): void {
  if (!path) {
    return
  }
  void router.push(path)
}
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
        <div class="section-title">Operations Summary</div>
      </template>
      <el-skeleton v-if="loading" :rows="3" animated />
      <el-descriptions v-else :column="4" border>
        <el-descriptions-item label="totalModules">{{ summary.totals.totalModules }}</el-descriptions-item>
        <el-descriptions-item label="readyModules">{{ summary.totals.readyModules }}</el-descriptions-item>
        <el-descriptions-item label="foundationModules">{{ summary.totals.foundationModules }}</el-descriptions-item>
        <el-descriptions-item label="plannedModules">{{ summary.totals.plannedModules }}</el-descriptions-item>
        <el-descriptions-item label="auditReadyModules">{{ summary.totals.auditReadyModules }}</el-descriptions-item>
        <el-descriptions-item label="certifiedModules">{{ summary.totals.certifiedModules }}</el-descriptions-item>
        <el-descriptions-item label="iec62443CertifiedModules">
          {{ summary.totals.iec62443CertifiedModules }}
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
        <div class="section-title">Module Status</div>
      </template>
      <el-skeleton v-if="loading" :rows="4" animated />
      <template v-else>
        <el-empty v-if="!hasModules" description="No module summary available." />
        <el-table v-else :data="modules" row-key="moduleId" empty-text="No module summary">
          <el-table-column prop="moduleId" label="moduleId" min-width="120" />
          <el-table-column prop="moduleName" label="moduleName" min-width="220" />
          <el-table-column prop="moduleType" label="moduleType" min-width="140" />
          <el-table-column prop="runtimeStatus" label="runtimeStatus" min-width="120" />
          <el-table-column prop="readinessLevel" label="readinessLevel" min-width="170" />
          <el-table-column prop="frontendReady" label="frontendReady" min-width="120" />
          <el-table-column prop="backendReady" label="backendReady" min-width="120" />
          <el-table-column prop="auditReadiness" label="auditReadiness" min-width="120" />
          <el-table-column prop="permissionMode" label="permissionMode" min-width="150" />
          <el-table-column prop="dataPersistenceMode" label="dataPersistenceMode" min-width="170" />
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
            {{ summary.securityPosture.realRbacIntegrated }}
          </el-descriptions-item>
          <el-descriptions-item label="dbAuditIntegrated">{{ summary.securityPosture.dbAuditIntegrated }}</el-descriptions-item>
          <el-descriptions-item label="siemIntegrated">{{ summary.securityPosture.siemIntegrated }}</el-descriptions-item>
          <el-descriptions-item label="ucdeRuntimeIntegrated">
            {{ summary.securityPosture.ucdeRuntimeIntegrated }}
          </el-descriptions-item>
          <el-descriptions-item label="certified">{{ summary.securityPosture.certified }}</el-descriptions-item>
          <el-descriptions-item label="iec62443Certified">
            {{ summary.securityPosture.iec62443Certified }}
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
            <li v-for="item in summary.highlights" :key="item">{{ item }}</li>
          </ul>
        </el-card>
        <el-card shadow="never">
          <template #header>Warnings</template>
          <ul class="inline-list">
            <li v-for="item in summary.warnings" :key="item">{{ item }}</li>
          </ul>
        </el-card>
      </template>
    </el-card>
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
</style>

