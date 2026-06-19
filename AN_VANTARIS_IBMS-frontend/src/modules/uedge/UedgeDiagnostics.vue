<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ApiError } from '@/services/api/errors'
import {
  getUedgeDiagnostics,
  getUedgeDiagnosticsPanels,
  getUedgeHealth,
  type UedgeDiagnosticsPanel,
  type UedgeDiagnosticsSummary,
  type UedgeHealth,
} from '@/services/api/uedge'

const router = useRouter()
const loading = ref(false)
const apiError = ref('')
const showDrawer = ref(false)
const selectedPanel = ref<UedgeDiagnosticsPanel | null>(null)

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

const diagnostics = ref<UedgeDiagnosticsSummary>({
  diagnosticsMode: 'local-skeleton-diagnostics',
  engineerDiagnosticsReady: true,
  runtimeConnected: false,
  connectorDiagnosticsEnabled: false,
  protocolDiagnosticsEnabled: false,
  mappingReviewEnabled: false,
  bufferInspectionEnabled: false,
  deliveryInspectionEnabled: false,
  edgeRuntimeIntegrated: false,
  linkRuntimeIntegrated: false,
  runtimeLinked: false,
  readOnly: true,
  controlActionsEnabled: false,
  certified: false,
  iec62443Certified: false,
  lastUpdated: '',
})

const panels = ref<UedgeDiagnosticsPanel[]>([])

async function loadData() {
  loading.value = true
  apiError.value = ''
  try {
    const [healthResult, diagnosticsResult, panelsResult] = await Promise.all([
      getUedgeHealth(),
      getUedgeDiagnostics(),
      getUedgeDiagnosticsPanels(),
    ])
    health.value = healthResult
    diagnostics.value = diagnosticsResult
    panels.value = panelsResult
  } catch (error) {
    apiError.value = error instanceof ApiError ? error.message : 'Failed to load UEDGE diagnostics skeleton.'
    panels.value = []
  } finally {
    loading.value = false
  }
}

function openPanel(panel: UedgeDiagnosticsPanel) {
  selectedPanel.value = panel
  showDrawer.value = true
}

function openSetup() {
  void router.push('/uedge/setup')
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
    <div class="hero-row">
      <div>
        <h2>UEDGE Engineer Diagnostics</h2>
        <p>Engineer-facing diagnostics preview for edge setup and connectivity.</p>
      </div>
      <div class="hero-tags">
        <el-tag type="info">diagnosticsMode: {{ diagnostics.diagnosticsMode }}</el-tag>
        <el-tag type="success">engineerDiagnosticsReady: {{ diagnostics.engineerDiagnosticsReady }}</el-tag>
        <el-tag>runtimeConnected: {{ diagnostics.runtimeConnected }}</el-tag>
        <el-tag>connectorDiagnosticsEnabled: {{ diagnostics.connectorDiagnosticsEnabled }}</el-tag>
        <el-tag>protocolDiagnosticsEnabled: {{ diagnostics.protocolDiagnosticsEnabled }}</el-tag>
        <el-tag>mappingReviewEnabled: {{ diagnostics.mappingReviewEnabled }}</el-tag>
        <el-tag>bufferInspectionEnabled: {{ diagnostics.bufferInspectionEnabled }}</el-tag>
        <el-tag>deliveryInspectionEnabled: {{ diagnostics.deliveryInspectionEnabled }}</el-tag>
        <el-tag>edgeRuntimeIntegrated: {{ diagnostics.edgeRuntimeIntegrated }}</el-tag>
        <el-tag>linkRuntimeIntegrated: {{ diagnostics.linkRuntimeIntegrated }}</el-tag>
      </div>
    </div>

    <el-alert
      type="info"
      show-icon
      :closable="false"
      title="UEDGE diagnostics are local skeleton views. Connector checks, protocol tests, mapping review, buffer inspection and EDGE/LINK runtime diagnostics are not integrated."
      class="block-space"
    />

    <el-alert v-if="apiError" type="warning" show-icon :closable="false" :title="apiError" class="block-space" />

    <el-card class="block-space">
      <template #header>Diagnostics Summary Cards</template>
      <el-descriptions :column="3" border>
        <el-descriptions-item label="diagnosticsPanels">{{ panels.length }}</el-descriptions-item>
        <el-descriptions-item label="runtimeConnected">{{ diagnostics.runtimeConnected }}</el-descriptions-item>
        <el-descriptions-item label="actionEnabled">{{ false }}</el-descriptions-item>
        <el-descriptions-item label="runtimeLinked">{{ diagnostics.runtimeLinked }}</el-descriptions-item>
        <el-descriptions-item label="readOnly">{{ diagnostics.readOnly }}</el-descriptions-item>
        <el-descriptions-item label="certified">{{ diagnostics.certified }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <el-card class="block-space">
      <template #header>Diagnostics Panels</template>
      <el-table :data="panels" row-key="panelId" v-loading="loading">
        <el-table-column prop="panelName" label="panelName" min-width="250" />
        <el-table-column prop="panelType" label="panelType" min-width="150" />
        <el-table-column prop="status" label="status" min-width="120" />
        <el-table-column prop="runtimeLinked" label="runtimeLinked" min-width="130" />
        <el-table-column prop="actionEnabled" label="actionEnabled" min-width="130" />
        <el-table-column prop="summary" label="summary" min-width="340" />
        <el-table-column label="actions" min-width="140" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openPanel(row)">View Panel</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-card class="block-space">
      <template #header>No Action Area</template>
      <el-space wrap>
        <el-button plain>View Panel</el-button>
        <el-button type="primary" plain @click="openSetup">Open Setup</el-button>
        <el-button @click="backToConsole">Back to Console</el-button>
      </el-space>
    </el-card>

    <el-drawer v-model="showDrawer" title="Panel Detail" size="45%">
      <el-empty v-if="!selectedPanel" description="No panel selected." />
      <template v-else>
        <el-descriptions :column="1" border class="block-space">
          <el-descriptions-item label="panel">{{ selectedPanel.panelName }}</el-descriptions-item>
          <el-descriptions-item label="panelType">{{ selectedPanel.panelType }}</el-descriptions-item>
          <el-descriptions-item label="status">{{ selectedPanel.status }}</el-descriptions-item>
          <el-descriptions-item label="runtimeLinked">{{ selectedPanel.runtimeLinked }}</el-descriptions-item>
          <el-descriptions-item label="summary">{{ selectedPanel.summary }}</el-descriptions-item>
          <el-descriptions-item label="limitations">
            {{ selectedPanel.limitations.join(' | ') }}
          </el-descriptions-item>
        </el-descriptions>
      </template>
    </el-drawer>
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

