<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import RouteL3ContentPanel from '@/components/RouteL3ContentPanel.vue'
import { ApiError } from '@/services/api/errors'
import {
  getUedgeHealth,
  getUedgeSetup,
  getUedgeSetupSteps,
  getUedgeSummary,
  type UedgeHealth,
  type UedgeSetupProfile,
  type UedgeSetupStep,
  type UedgeSummary,
} from '@/services/api/uedge'

const router = useRouter()
const loading = ref(false)
const apiError = ref('')

const health = ref<UedgeHealth>({
  status: 'unknown',
  moduleId: 'uedge',
  moduleName: 'UEDGE Setup & Diagnostics',
  runtimeMode: 'local-skeleton',
  provider: 'local-uedge-provider',
  readOnly: true,
  controlActionsEnabled: false,
  runtimeLinked: false,
  edgeRuntimeIntegrated: false,
  linkRuntimeIntegrated: false,
  certified: false,
  iec62443Certified: false,
})

const setupProfile = ref<UedgeSetupProfile>({
  setupMode: 'local-skeleton-setup',
  customerSetupReady: true,
  oneClickSetupEnabled: false,
  realDeviceRegistrationEnabled: false,
  certificateImportEnabled: false,
  tokenProvisioningEnabled: false,
  networkConfigEnabled: false,
  runtimeLinked: false,
  edgeRuntimeIntegrated: false,
  linkRuntimeIntegrated: false,
  readOnly: true,
  controlActionsEnabled: false,
  certified: false,
  iec62443Certified: false,
  lastUpdated: '',
})

const setupSteps = ref<UedgeSetupStep[]>([])
const summary = ref<UedgeSummary>({
  moduleId: 'uedge',
  moduleName: 'UEDGE Setup & Diagnostics',
  setupMode: 'local-skeleton-setup',
  diagnosticsMode: 'local-skeleton-diagnostics',
  customerSetupReady: true,
  engineerDiagnosticsReady: true,
  setupStepCount: 0,
  diagnosticsPanelCount: 0,
  oneClickSetupEnabled: false,
  runtimeConnected: false,
  runtimeLinked: false,
  readOnly: true,
  controlActionsEnabled: false,
  edgeRuntimeIntegrated: false,
  linkRuntimeIntegrated: false,
  certified: false,
  iec62443Certified: false,
})

const setupReadyCount = computed(() => setupSteps.value.filter((step) => step.status === 'ready').length)

async function loadData() {
  loading.value = true
  apiError.value = ''
  try {
    const [healthResult, setupResult, stepsResult, summaryResult] = await Promise.all([
      getUedgeHealth(),
      getUedgeSetup(),
      getUedgeSetupSteps(),
      getUedgeSummary(),
    ])
    health.value = healthResult
    setupProfile.value = setupResult
    setupSteps.value = stepsResult
    summary.value = summaryResult
  } catch (error) {
    apiError.value = error instanceof ApiError ? error.message : 'Failed to load UEDGE setup skeleton.'
    setupSteps.value = []
  } finally {
    loading.value = false
  }
}

function openDiagnostics() {
  void router.push('/uedge/diagnostics')
}

function backToConsole() {
  void router.push('/console/operations')
}

onMounted(() => {
  void loadData()
})
</script>

<template>
  <section class="uedge-page">
    <RouteL3ContentPanel />

    <div class="hero-row">
      <div>
        <h2>UEDGE Customer Setup</h2>
        <p>One-click edge setup preview for VANTARIS ONE.</p>
      </div>
      <div class="hero-tags">
        <el-tag type="info">setupMode: {{ setupProfile.setupMode }}</el-tag>
        <el-tag type="success">customerSetupReady: {{ setupProfile.customerSetupReady }}</el-tag>
        <el-tag>oneClickSetupEnabled: {{ setupProfile.oneClickSetupEnabled }}</el-tag>
        <el-tag>realDeviceRegistrationEnabled: {{ setupProfile.realDeviceRegistrationEnabled }}</el-tag>
        <el-tag>certificateImportEnabled: {{ setupProfile.certificateImportEnabled }}</el-tag>
        <el-tag>tokenProvisioningEnabled: {{ setupProfile.tokenProvisioningEnabled }}</el-tag>
        <el-tag>networkConfigEnabled: {{ setupProfile.networkConfigEnabled }}</el-tag>
        <el-tag>runtimeLinked: {{ setupProfile.runtimeLinked }}</el-tag>
        <el-tag>certified: {{ setupProfile.certified }}</el-tag>
      </div>
    </div>

    <el-alert
      type="info"
      show-icon
      :closable="false"
      title="UEDGE setup is a local skeleton preview. Real device registration, certificate import, token provisioning, network configuration and EDGE/LINK runtime integration are not integrated."
      class="block-space"
    />

    <el-alert v-if="apiError" type="warning" show-icon :closable="false" :title="apiError" class="block-space" />

    <el-card class="block-space">
      <template #header>Setup Readiness Cards</template>
      <el-descriptions :column="3" border>
        <el-descriptions-item label="customerSetupReady">{{ setupProfile.customerSetupReady }}</el-descriptions-item>
        <el-descriptions-item label="setupSteps">{{ setupSteps.length }}</el-descriptions-item>
        <el-descriptions-item label="readySteps">{{ setupReadyCount }}</el-descriptions-item>
        <el-descriptions-item label="actionEnabled">{{ false }}</el-descriptions-item>
        <el-descriptions-item label="runtimeLinked">{{ setupProfile.runtimeLinked }}</el-descriptions-item>
        <el-descriptions-item label="readOnly">{{ setupProfile.readOnly }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <el-card class="block-space">
      <template #header>Setup Steps</template>
      <el-table :data="setupSteps" row-key="stepId" v-loading="loading">
        <el-table-column prop="stepOrder" label="stepOrder" min-width="110" />
        <el-table-column prop="stepName" label="stepName" min-width="220" />
        <el-table-column prop="status" label="status" min-width="120" />
        <el-table-column prop="required" label="required" min-width="100" />
        <el-table-column prop="actionEnabled" label="actionEnabled" min-width="130" />
        <el-table-column prop="notes" label="notes" min-width="360" />
      </el-table>
    </el-card>

    <el-card class="block-space">
      <template #header>Placeholder Configuration Summary</template>
      <el-descriptions :column="1" border>
        <el-descriptions-item label="site selection placeholder">
          Local site selection placeholder only.
        </el-descriptions-item>
        <el-descriptions-item label="gateway template placeholder">
          Gateway template preview is static metadata.
        </el-descriptions-item>
        <el-descriptions-item label="certificate/token placeholder">
          Certificate and token placeholders are display-only.
        </el-descriptions-item>
        <el-descriptions-item label="connector template placeholder">
          Connector template review is local skeleton metadata.
        </el-descriptions-item>
        <el-descriptions-item label="dry-run readiness placeholder">
          Dry-run readiness indicates local checklist completeness only.
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <el-card class="block-space">
      <template #header>No Action Area</template>
      <el-alert type="warning" show-icon :closable="false" title="Actions are disabled in R1." />
      <el-alert
        type="info"
        show-icon
        :closable="false"
        title="No real device registration, no real certificate/token import, and no network configuration changes."
        class="block-space"
      />
      <el-space wrap>
        <el-button plain>View Details</el-button>
        <el-button type="primary" plain @click="openDiagnostics">Open Diagnostics</el-button>
        <el-button @click="backToConsole">Back to Console</el-button>
      </el-space>
    </el-card>

    <el-card class="block-space">
      <template #header>Skeleton Summary</template>
      <el-descriptions :column="3" border>
        <el-descriptions-item label="setupStepCount">{{ summary.setupStepCount }}</el-descriptions-item>
        <el-descriptions-item label="diagnosticsPanelCount">{{ summary.diagnosticsPanelCount }}</el-descriptions-item>
        <el-descriptions-item label="runtimeConnected">{{ summary.runtimeConnected }}</el-descriptions-item>
      </el-descriptions>
    </el-card>
  </section>
</template>

<style scoped>
.uedge-page {
  padding: 16px;
}

.hero-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.hero-tags {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.block-space {
  margin-top: 12px;
}
</style>
