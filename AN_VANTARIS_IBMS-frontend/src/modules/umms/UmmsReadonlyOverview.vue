<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import RouteL3ContentPanel from '@/components/RouteL3ContentPanel.vue'
import {
  getUmmsReadonlyOverview,
  type UmmsReadonlyOverview,
} from '@/services/api/umms'

const loading = ref(false)
const overview = ref<UmmsReadonlyOverview | null>(null)

const fallbackCapabilities = [
  'Work Order Management',
  'Asset Registry',
  'Preventive Maintenance',
  'Spare Parts / Inventory',
  'Vendor / Contract / SLA',
  'UCDE Evidence Closure Alignment',
  'HMI Locator Binding',
  'Existing System Onboarding',
  'Engineer Commissioning Diagnostics',
  'Remote / Distributed Deployment Readiness',
]

const capabilityRows = computed(() => {
  const rows = overview.value?.customerCoreFunctions.customerCoreFunctions ?? []
  return rows.length > 0
    ? rows.map((item) => ({
      name: item.function,
      status: item.coverageStatus,
      readinessStage: item.readinessStage,
      runtimeEnabled: item.runtimeEnabled,
      remainingGap: item.remainingGap,
    }))
    : fallbackCapabilities.map((name) => ({
      name,
      status: 'read_only_fallback',
      readinessStage: 'UMMS-R12 fallback',
      runtimeEnabled: false,
      remainingGap: 'API data unavailable; fallback remains read-only.',
    }))
})

const readinessStages = computed(() => overview.value?.readinessSummary.readinessStages ?? [])
const safetyPosture = computed(() => overview.value?.safetyPosture.safetyPosture ?? {})

const safetyRows = computed(() => [
  { label: 'No DB write', value: safetyPosture.value.dbWrite === false },
  { label: 'No workflow', value: safetyPosture.value.workflowExecution === false },
  { label: 'No approval execution', value: safetyPosture.value.approvalExecution === false },
  { label: 'No runtime activation', value: safetyPosture.value.runtimeActivation === false },
  { label: 'No production activation', value: safetyPosture.value.productionActivation === false },
  { label: 'No EDGE/LINK runtime call', value: safetyPosture.value.edgeRuntimeCall === false && safetyPosture.value.linkRuntimeCall === false },
])

const packageEntry = computed(() => overview.value?.packageEntry)
const stakeholderReview = computed(() => overview.value?.stakeholderReview)
const fallbackMessage = computed(() => overview.value?.fallbackMessage || 'UMMS readiness data unavailable, read-only fallback active.')
const allRuntimeDisabled = computed(() => capabilityRows.value.every((item) => item.runtimeEnabled === false))

async function loadOverview(): Promise<void> {
  loading.value = true
  try {
    overview.value = await getUmmsReadonlyOverview()
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  void loadOverview()
})
</script>

<template>
  <section class="umms-readonly-page">
    <RouteL3ContentPanel />

    <header class="hero">
      <div>
        <p class="eyebrow">VANTARIS ONE / UMMS</p>
        <h1>UMMS Stakeholder Review Card</h1>
        <p class="hero-copy">
          Read-only UConsole entry consuming the UMMS-R11 GET-only endpoints. No write, approval,
          activation, deployment, workflow, runtime, HMI, inventory, PM, vendor, or evidence-closure actions are exposed.
        </p>
      </div>
      <div class="status-stack">
        <el-tag type="success">GET only</el-tag>
        <el-tag type="success">Read-only</el-tag>
        <el-tag type="info">Projection-backed</el-tag>
      </div>
    </header>

    <el-alert
      v-if="overview?.fallbackActive"
      type="warning"
      show-icon
      :closable="false"
      :title="fallbackMessage"
      class="block-space"
    />

    <el-card v-loading="loading" shadow="never" class="block-space umms-card">
      <template #header>
        <div class="card-header">
          <span>UMMS package readiness</span>
          <el-tag type="success">Stakeholder Review Ready</el-tag>
        </div>
      </template>

      <el-descriptions :column="3" border>
        <el-descriptions-item label="Package name">{{ packageEntry?.packageDisplayName || 'UMMS' }}</el-descriptions-item>
        <el-descriptions-item label="Full name">
          {{ packageEntry?.packageName || 'Unified Maintenance Management System' }}
        </el-descriptions-item>
        <el-descriptions-item label="Status">Stakeholder Review Ready</el-descriptions-item>
        <el-descriptions-item label="Mode">Read-only</el-descriptions-item>
        <el-descriptions-item label="Runtime">Disabled</el-descriptions-item>
        <el-descriptions-item label="Latest archived tag">
          {{ packageEntry?.latestTag || 'umms-r11-readonly-api-entry-skeleton-local-freeze-20260621' }}
        </el-descriptions-item>
        <el-descriptions-item label="Review package">
          {{ packageEntry?.stakeholderReviewPackage || 'ONE_UMMS_R10_STAKEHOLDER_REVIEW_PACKAGE.md' }}
        </el-descriptions-item>
        <el-descriptions-item label="Review id">
          {{ stakeholderReview?.reviewPackageId || 'umms-stakeholder-review-package.v1' }}
        </el-descriptions-item>
        <el-descriptions-item label="Runtime disabled">{{ allRuntimeDisabled }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <el-row :gutter="16" class="block-space">
      <el-col :span="8">
        <el-card shadow="never">
          <div class="metric-value">{{ capabilityRows.length }}</div>
          <div class="metric-label">Covered capabilities</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="never">
          <div class="metric-value">{{ readinessStages.length }}</div>
          <div class="metric-label">Readiness stages</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="never">
          <div class="metric-value">0</div>
          <div class="metric-label">Runtime actions</div>
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="never" class="block-space">
      <template #header>Covered capabilities</template>
      <el-table :data="capabilityRows" border>
        <el-table-column prop="name" label="Capability" min-width="220" />
        <el-table-column prop="status" label="Status" min-width="170" />
        <el-table-column prop="readinessStage" label="Readiness stage" min-width="180" />
        <el-table-column prop="runtimeEnabled" label="Runtime enabled" width="150" />
        <el-table-column prop="remainingGap" label="Remaining gap" min-width="260" />
      </el-table>
    </el-card>

    <el-card shadow="never" class="block-space">
      <template #header>Safety posture</template>
      <el-row :gutter="12">
        <el-col v-for="item in safetyRows" :key="item.label" :span="8">
          <div class="safety-pill">
            <span>{{ item.label }}</span>
            <el-tag :type="item.value ? 'success' : 'danger'">{{ item.value ? 'PASS' : 'REVIEW' }}</el-tag>
          </div>
        </el-col>
      </el-row>
      <el-alert
        type="success"
        show-icon
        :closable="false"
        title="No write, approval, activation, deployment, workflow, runtime, PM, inventory, vendor, evidence closure, HMI, connector, EDGE, LINK, or ONE Adapter actions are exposed."
        class="block-space"
      />
    </el-card>

    <el-card shadow="never" class="block-space">
      <template #header>Recommended next step</template>
      <p>UMMS read-only frontend freeze / archive</p>
    </el-card>
  </section>
</template>

<style scoped>
.umms-readonly-page {
  padding: 24px;
}

.hero,
.card-header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
}

.eyebrow {
  margin: 0 0 8px;
  color: #64748b;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.hero h1 {
  margin: 0;
}

.hero-copy {
  max-width: 900px;
  color: #475569;
}

.status-stack {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.block-space {
  margin-top: 16px;
}

.metric-value {
  font-size: 28px;
  font-weight: 800;
}

.metric-label {
  color: #64748b;
  margin-top: 4px;
}

.safety-pill {
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 12px;
  margin-bottom: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
