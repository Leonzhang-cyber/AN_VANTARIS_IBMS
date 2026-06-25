<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import RouteL3ContentPanel from '@/components/RouteL3ContentPanel.vue'
import {
  getUhmiHealth,
  getUhmiMenuIa,
  getUhmiSection,
  getUhmiWorkspace,
  uhmiSections,
  type UhmiHealthPayload,
  type UhmiMenuIaPayload,
  type UhmiSectionKey,
  type UhmiSectionPayload,
  type UhmiWorkspacePayload,
} from '@/services/api/uhmi'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const health = ref<UhmiHealthPayload | null>(null)
const menuIa = ref<UhmiMenuIaPayload | null>(null)
const section = ref<UhmiSectionPayload | null>(null)
const workspace = ref<UhmiWorkspacePayload | null>(null)
const loadError = ref('')
const activeSectionKey = ref<UhmiSectionKey>('HMI_OVERVIEW')
const activeRole = ref<'Customer' | 'Engineer' | 'Admin' | 'Operator'>('Customer')

const fallbackSummaryCards = [
  { label: 'Systems Monitored', value: 6, tone: 'teal' },
  { label: 'Devices Visible', value: 180, tone: 'mint' },
  { label: 'Active Events', value: 21, tone: 'amber' },
  { label: 'Panels Available', value: 9, tone: 'blue' },
  { label: 'Evidence Records', value: 81, tone: 'violet' },
  { label: 'Guardrails Active', value: 8, tone: 'green' },
]

const fallbackR2bGuardrails = [
  { label: 'Read-only Mode', active: true },
  { label: 'No Direct Device Control', active: true },
  { label: 'No Runtime Activation', active: true },
  { label: 'No DB Write', active: true },
  { label: 'No EDGE Command Execution', active: true },
  { label: 'No LINK Command Execution', active: true },
  { label: 'Future Control Path', active: true },
]

const activeMenuItem = computed(() =>
  uhmiSections.find((item) => item.key === activeSectionKey.value) ?? uhmiSections[0],
)

const guardrailRows = computed(() => [
  { label: 'Read-only', value: section.value?.readOnly === true },
  { label: 'No direct device control', value: section.value?.directDeviceControl === false },
  { label: 'No direct DB write', value: section.value?.directDatabaseWrite === false },
  { label: 'No EDGE command', value: section.value?.edgeCommandEnabled === false },
  { label: 'No LINK command', value: section.value?.linkCommandEnabled === false },
  { label: 'No bypass CODE', value: section.value?.bypassCode === false },
])

const allGuardrailsPass = computed(() => guardrailRows.value.every((item) => item.value))
const summaryCards = computed(() => workspace.value?.summaryCards ?? fallbackSummaryCards)
const systemContexts = computed(() => workspace.value?.systemContexts ?? [])
const deviceContexts = computed(() => workspace.value?.deviceContexts ?? [])
const mimicPanels = computed(() => workspace.value?.mimicPanels ?? [])
const eventContexts = computed(() => workspace.value?.eventContexts ?? [])
const evidenceContexts = computed(() => workspace.value?.evidenceContexts ?? [])
const r2bGuardrails = computed(() => workspace.value?.guardrails ?? fallbackR2bGuardrails)
const futureControlPath = computed(() =>
  workspace.value?.futureControlPath
  ?? 'UHMI -> CODE -> Policy Gate -> Approval -> Audit / UCDE -> LINK -> EDGE -> Device',
)
const roleViews = computed(() => workspace.value?.roleViews ?? [])
const activeRoleView = computed(() =>
  roleViews.value.find((role) => role.roleName === activeRole.value) ?? roleViews.value[0],
)
const roleVisibilityMatrix = computed(() => workspace.value?.roleVisibilityMatrix ?? [])
const disabledActions = computed(() =>
  workspace.value?.disabledActions
  ?? ['Device Control', 'Runtime Activation', 'DB Write', 'EDGE Command', 'LINK Command', 'RBAC Mutation', 'Package State Mutation', 'Install/Rollback'],
)
const roleContextRows = computed(() => workspace.value?.roleContexts?.[activeRole.value] ?? [])
const styleTokens = computed(() =>
  workspace.value?.styleTokens
  ?? ['light app shell', 'white rounded cards', 'soft shadow', 'pale mint background', 'teal primary accent', 'pill tabs', 'pastel icon blocks', 'soft status badges', 'clean table layout'],
)

function syncActiveFromRoute(): void {
  const matched = uhmiSections.find((item) => item.route === route.path)
  activeSectionKey.value = matched?.key ?? 'HMI_OVERVIEW'
}

async function selectSection(key: UhmiSectionKey): Promise<void> {
  const item = uhmiSections.find((entry) => entry.key === key)
  if (item && item.route !== route.path) {
    await router.push(item.route)
  }
  activeSectionKey.value = key
  await loadSection()
}

async function loadSection(): Promise<void> {
  section.value = await getUhmiSection(activeSectionKey.value)
}

async function loadWorkspace(): Promise<void> {
  loading.value = true
  loadError.value = ''
  try {
    const [healthPayload, menuPayload, workspacePayload] = await Promise.all([
      getUhmiHealth(),
      getUhmiMenuIa(),
      getUhmiWorkspace(),
    ])
    health.value = healthPayload
    menuIa.value = menuPayload
    workspace.value = workspacePayload
    await loadSection()
  } catch (error) {
    loadError.value = error instanceof Error ? error.message : 'UHMI read-only API unavailable.'
  } finally {
    loading.value = false
  }
}

watch(
  () => route.path,
  async () => {
    syncActiveFromRoute()
    await loadSection()
  },
)

onMounted(() => {
  syncActiveFromRoute()
  void loadWorkspace()
})
</script>

<template>
  <section class="uhmi-page light-app-shell pale-mint-background clean-table-layout">
    <RouteL3ContentPanel />

    <header class="uhmi-hero white-rounded-card soft-shadow teal-accent-card">
      <div>
        <p class="eyebrow">VANTARIS ONE / UConsole</p>
        <h1>UHMI Workspace</h1>
        <p class="style-chip">VANTARIS_LIGHT_OPERATIONS_CONSOLE</p>
        <p class="hero-copy">
          Unified Human-Machine Interface read-only workspace for cross-industry operations context.
          Device/System data flows through EDGE, LINK, and CODE before reaching UConsole/UHMI.
        </p>
      </div>
      <div class="status-stack">
        <el-tag type="success">GET only</el-tag>
        <el-tag type="success">Read-only Mode</el-tag>
        <el-tag type="success">No Direct Device Control</el-tag>
        <el-tag type="info">No Runtime Activation</el-tag>
        <el-tag type="info">No DB Write</el-tag>
        <el-tag type="info">UConsole workspace</el-tag>
      </div>
    </header>

    <div class="style-token-row">
      <span v-for="token in styleTokens" :key="token" class="style-token">{{ token }}</span>
    </div>

    <el-alert
      v-if="loadError"
      type="error"
      show-icon
      :closable="false"
      :title="loadError"
      class="block-space"
    />

    <el-row :gutter="16" class="block-space">
      <el-col v-for="card in summaryCards" :key="card.label" :span="4">
        <el-card shadow="never" class="metric-card white-rounded-card soft-shadow pastel-icon-blocks soft-status-badges">
          <div class="metric-card__icon" :class="`metric-card__icon--${card.tone}`">{{ card.label.slice(0, 1) }}</div>
          <div>
            <div class="metric-value">{{ card.value }}</div>
            <div class="metric-label">{{ card.label }}</div>
          </div>
          <el-tag size="small" type="success" class="metric-card__badge">read-only</el-tag>
        </el-card>
      </el-col>
    </el-row>

    <el-card v-loading="loading" shadow="never" class="block-space white-rounded-card soft-shadow">
      <template #header>
        <div class="card-header">
          <span>UHMI workspace sections</span>
          <el-tag type="success">L1/L2 sidebar, L3 inside page</el-tag>
        </div>
      </template>

      <el-tabs class="pill-tabs l3-pill-tabs" :model-value="activeSectionKey" @tab-change="(name: unknown) => selectSection(name as UhmiSectionKey)">
        <el-tab-pane
          v-for="item in uhmiSections"
          :key="item.key"
          :label="item.label"
          :name="item.key"
        />
      </el-tabs>

      <div class="section-heading">
        <div>
          <h2>{{ section?.sectionLabel || activeMenuItem.label }}</h2>
          <p>{{ section?.purpose }}</p>
        </div>
        <el-tag type="success">{{ section?.method || 'GET' }}</el-tag>
      </div>

      <el-descriptions :column="2" border>
        <el-descriptions-item label="Placement">{{ section?.placement || 'UConsole / UHMI Workspace' }}</el-descriptions-item>
        <el-descriptions-item label="Route">{{ section?.route || activeMenuItem.route }}</el-descriptions-item>
        <el-descriptions-item label="Data flow">{{ section?.dataFlow }}</el-descriptions-item>
        <el-descriptions-item label="Future action">{{ section?.futureControlledActionStatus }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <el-card shadow="never" class="block-space white-rounded-card soft-shadow table-shell">
      <template #header>Read-only projection rows</template>
      <el-table class="operations-table" :data="section?.rows || []" border>
        <el-table-column prop="name" label="Name" min-width="220" />
        <el-table-column prop="state" label="State" min-width="150" />
        <el-table-column prop="source" label="Source" min-width="220" />
        <el-table-column prop="actionEnabled" label="Action enabled" width="160" />
      </el-table>
    </el-card>

    <el-card shadow="never" class="block-space white-rounded-card soft-shadow">
      <template #header>
        <div class="card-header">
          <span>System Context</span>
          <el-tag type="success">read-only</el-tag>
        </div>
      </template>
      <div class="system-grid">
        <div v-for="item in systemContexts" :key="item.systemId" class="system-card white-rounded-card soft-shadow">
          <div class="system-card__title">
            <span>{{ item.systemName }}</span>
            <el-tag type="success">{{ item.healthStatus }}</el-tag>
          </div>
          <div class="system-card__meta">{{ item.systemId }} / {{ item.category }}</div>
          <div class="system-card__metrics">
            <span>{{ item.visibleDevices }} devices</span>
            <span>{{ item.activeEvents }} events</span>
            <span>{{ item.panelCount }} panels</span>
            <span>{{ item.evidenceCount }} evidence</span>
          </div>
          <el-tag size="small" type="success" class="block-space">read-only</el-tag>
        </div>
      </div>
    </el-card>

    <el-card shadow="never" class="block-space white-rounded-card soft-shadow table-shell">
      <template #header>Device Context</template>
      <el-table class="operations-table" :data="deviceContexts" border>
        <el-table-column prop="deviceId" label="deviceId" min-width="180" />
        <el-table-column prop="deviceName" label="deviceName" min-width="180" />
        <el-table-column prop="systemName" label="systemName" min-width="170" />
        <el-table-column prop="location" label="location" min-width="180" />
        <el-table-column prop="status" label="status" width="120" />
        <el-table-column prop="lastSeen" label="lastSeen" min-width="180" />
        <el-table-column prop="eventCount" label="eventCount" width="120" />
        <el-table-column prop="panelAvailable" label="panelAvailable" width="150" />
        <el-table-column prop="controlState" label="controlState" min-width="170" />
      </el-table>
    </el-card>

    <el-card shadow="never" class="block-space white-rounded-card soft-shadow">
      <template #header>Mimic Panel Preview</template>
      <div class="mimic-grid">
        <div v-for="item in mimicPanels" :key="item.panelId" class="mimic-card white-rounded-card soft-shadow">
          <div class="mimic-card__bar"></div>
          <h3>{{ item.panelName }}</h3>
          <p>{{ item.systemName }}</p>
          <div class="mimic-card__footer">
            <el-tag type="info">{{ item.previewType }}</el-tag>
            <el-tag type="success">{{ item.readOnly ? 'readOnly' : 'review' }}</el-tag>
            <el-tag type="success">{{ item.controlsDisabled ? 'controls disabled' : 'review' }}</el-tag>
          </div>
          <el-button type="primary" disabled class="block-space">future-only disabled control placeholder</el-button>
        </div>
      </div>
    </el-card>

    <el-card shadow="never" class="block-space white-rounded-card soft-shadow table-shell">
      <template #header>Event Context</template>
      <el-table class="operations-table" :data="eventContexts" border>
        <el-table-column prop="eventId" label="eventId" min-width="150" />
        <el-table-column prop="severity" label="severity" width="120" />
        <el-table-column prop="title" label="title" min-width="220" />
        <el-table-column prop="sourceSystem" label="sourceSystem" min-width="170" />
        <el-table-column prop="linkedDevice" label="linkedDevice" min-width="180" />
        <el-table-column prop="timestamp" label="timestamp" min-width="180" />
        <el-table-column prop="status" label="status" width="130" />
        <el-table-column prop="evidenceLinked" label="evidenceLinked" width="150" />
      </el-table>
    </el-card>

    <el-card shadow="never" class="block-space white-rounded-card soft-shadow table-shell">
      <template #header>Evidence Context</template>
      <el-table class="operations-table" :data="evidenceContexts" border>
        <el-table-column prop="evidenceId" label="evidenceId" min-width="150" />
        <el-table-column prop="type" label="type" min-width="150" />
        <el-table-column prop="linkedObject" label="linkedObject" min-width="190" />
        <el-table-column prop="source" label="source" min-width="180" />
        <el-table-column prop="timestamp" label="timestamp" min-width="180" />
        <el-table-column prop="integrityStatus" label="integrityStatus" min-width="150" />
        <el-table-column prop="viewOnly" label="viewOnly" width="120" />
      </el-table>
    </el-card>

    <el-card shadow="never" class="block-space white-rounded-card soft-shadow">
      <template #header>Guardrails</template>
      <div class="guardrail-grid">
        <div v-for="item in r2bGuardrails" :key="item.label" class="guardrail-pill">
          <span>{{ item.label }}</span>
          <el-tag :type="item.active ? 'success' : 'danger'">{{ item.active ? 'PASS' : 'REVIEW' }}</el-tag>
        </div>
      </div>
      <el-row :gutter="12">
        <el-col v-for="item in guardrailRows" :key="item.label" :span="8">
          <div class="guardrail-pill">
            <span>{{ item.label }}</span>
            <el-tag :type="item.value ? 'success' : 'danger'">{{ item.value ? 'PASS' : 'REVIEW' }}</el-tag>
          </div>
        </el-col>
      </el-row>
      <el-alert
        type="success"
        show-icon
        :closable="false"
        title="No direct device control, direct DB write, EDGE command, LINK command, NEXUS AI execution, bypass CODE, runtime activation, or future controlled action execution is exposed."
        class="block-space"
      />
    </el-card>

    <el-card shadow="never" class="block-space white-rounded-card soft-shadow">
      <template #header>Future Control Path</template>
      <div class="future-path">
        <span v-for="step in futureControlPath.split(' -> ')" :key="step">{{ step }}</span>
      </div>
      <el-button type="primary" disabled class="block-space">Future-only / Requires Policy Approval</el-button>
    </el-card>

    <el-card shadow="never" class="block-space white-rounded-card soft-shadow">
      <template #header>
        <div class="card-header">
          <span>Role-based Workspace Views</span>
          <div class="status-stack">
            <el-tag type="success">Read-only role context</el-tag>
            <el-tag type="success">No Real RBAC Mutation</el-tag>
            <el-tag type="success">No Permission Write</el-tag>
            <el-tag type="success">No Direct Device Control</el-tag>
          </div>
        </div>
      </template>

      <el-tabs v-model="activeRole" class="pill-tabs role-selector" type="card">
        <el-tab-pane label="Customer" name="Customer" />
        <el-tab-pane label="Engineer" name="Engineer" />
        <el-tab-pane label="Admin" name="Admin" />
        <el-tab-pane label="Operator" name="Operator" />
      </el-tabs>

      <div v-if="activeRoleView" class="role-card">
        <div>
          <p class="eyebrow">{{ activeRoleView.roleId }}</p>
          <h2>{{ activeRoleView.roleName }}</h2>
          <p>{{ activeRoleView.purpose }}</p>
        </div>
        <el-tag type="success">{{ activeRoleView.readOnly ? 'readOnly = true' : 'review' }}</el-tag>
      </div>

      <el-row :gutter="12" class="block-space">
        <el-col :span="12">
          <el-card shadow="never" class="nested-panel">
            <template #header>Visible Panels</template>
            <el-tag v-for="item in activeRoleView?.visiblePanels || []" :key="item" class="tag-gap" type="success">
              {{ item }}
            </el-tag>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card shadow="never" class="nested-panel">
            <template #header>Hidden Panels / Guardrails</template>
            <el-tag v-for="item in activeRoleView?.hiddenPanels || []" :key="item" class="tag-gap" type="info">
              {{ item }}
            </el-tag>
            <el-tag v-for="item in activeRoleView?.guardrails || []" :key="item" class="tag-gap" type="success">
              {{ item }}
            </el-tag>
          </el-card>
        </el-col>
      </el-row>
    </el-card>

    <el-card shadow="never" class="block-space white-rounded-card soft-shadow table-shell">
      <template #header>Role Visibility Matrix</template>
      <el-table class="operations-table" :data="roleVisibilityMatrix" border>
        <el-table-column prop="workspaceArea" label="Workspace Area" min-width="190" />
        <el-table-column prop="Customer" label="Customer" width="120" />
        <el-table-column prop="Engineer" label="Engineer" width="120" />
        <el-table-column prop="Admin" label="Admin" width="120" />
        <el-table-column prop="Operator" label="Operator" width="120" />
        <el-table-column prop="notes" label="Notes" min-width="260" />
      </el-table>
    </el-card>

    <el-card shadow="never" class="block-space white-rounded-card soft-shadow">
      <template #header>Disabled Actions</template>
      <div class="guardrail-grid">
        <div v-for="item in disabledActions" :key="item" class="guardrail-pill">
          <span>{{ item }}</span>
          <el-tag type="success">Disabled</el-tag>
        </div>
      </div>
      <el-alert
        type="success"
        show-icon
        :closable="false"
        title="No Runtime Activation, No DB Write, No RBAC Mutation, No Package State Mutation, No EDGE Command Execution, and No LINK Command Execution are exposed."
        class="block-space"
      />
    </el-card>

    <el-card shadow="never" class="block-space white-rounded-card soft-shadow table-shell">
      <template #header>{{ activeRole }} Context</template>
      <el-table class="operations-table" :data="roleContextRows" border>
        <el-table-column prop="name" label="Context" min-width="220" />
        <el-table-column prop="status" label="Status" min-width="180" />
        <el-table-column prop="readOnly" label="readOnly" width="120" />
      </el-table>
      <div class="role-context-labels">
        <span>Customer Context: Delivery Status / Acceptance Checklist / Evidence Records / Reports Snapshot</span>
        <span>Engineer Context: Package Diagnostics / API Health / EDGE / LINK Health / DB Readiness / Offline Verification</span>
        <span>Admin Context: Menu Visibility / Package Visibility / Role Matrix / Locked Modules / Entitlement Snapshot</span>
        <span>Operator Context: Live Operations / Active Events / Device Status / Shift Handover / Event Context</span>
      </div>
    </el-card>
  </section>
</template>

<style scoped>
.uhmi-page {
  padding: 24px;
  min-height: 100%;
  background:
    radial-gradient(circle at top left, rgba(204, 251, 241, 0.55), transparent 32%),
    linear-gradient(180deg, #f8fafc 0%, #f1f5f4 100%);
}

.light-app-shell {
  color: #1f2937;
}

.pale-mint-background {
  background-color: #f4fbf8;
}

.white-rounded-card {
  border: 1px solid #dbe8e3;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.96);
}

.soft-shadow {
  box-shadow: 0 12px 30px rgba(15, 118, 110, 0.08);
}

.teal-accent-card {
  border-left: 4px solid #14b8a6;
}

.clean-table-layout {
  --uhmi-table-border: #e2e8f0;
  --uhmi-table-header: #f8fafc;
}

.uhmi-hero,
.card-header,
.section-heading {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
}

.uhmi-hero {
  padding: 20px;
}

.eyebrow {
  margin: 0 0 8px;
  color: #64748b;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
}

.style-chip {
  display: inline-flex;
  margin: 10px 0 0;
  padding: 6px 10px;
  border-radius: 999px;
  background: #ecfeff;
  color: #0f766e;
  border: 1px solid #99f6e4;
  font-size: 12px;
  font-weight: 700;
}

.style-token-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 14px;
}

.style-token {
  padding: 6px 10px;
  border-radius: 999px;
  border: 1px solid #dbe8e3;
  background: #ffffff;
  color: #475569;
  font-size: 12px;
}

.uhmi-hero h1,
.section-heading h2 {
  margin: 0;
}

.hero-copy,
.section-heading p {
  max-width: 920px;
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
  font-size: 24px;
  font-weight: 700;
  color: #111827;
}

.metric-label {
  margin-top: 4px;
  color: #64748b;
  font-size: 13px;
}

.metric-card {
  min-height: 92px;
  position: relative;
  overflow: hidden;
}

.metric-card :deep(.el-card__body) {
  display: flex;
  gap: 12px;
  align-items: center;
}

.metric-card__badge {
  position: absolute;
  top: 10px;
  right: 10px;
}

.pastel-icon-blocks {
  background: linear-gradient(180deg, #ffffff, #fbfefd);
}

.soft-status-badges :deep(.el-tag) {
  border-radius: 999px;
}

.metric-card__icon {
  width: 38px;
  height: 38px;
  border-radius: 8px;
  display: grid;
  place-items: center;
  font-weight: 800;
  color: #0f766e;
  background: #ccfbf1;
}

.metric-card__icon--amber {
  color: #92400e;
  background: #fef3c7;
}

.metric-card__icon--blue {
  color: #1d4ed8;
  background: #dbeafe;
}

.metric-card__icon--violet {
  color: #6d28d9;
  background: #ede9fe;
}

.metric-card__icon--green,
.metric-card__icon--mint,
.metric-card__icon--teal {
  color: #047857;
  background: #d1fae5;
}

.pill-tabs :deep(.el-tabs__header) {
  margin-bottom: 14px;
}

.pill-tabs :deep(.el-tabs__nav) {
  border: 0;
  gap: 8px;
}

.pill-tabs :deep(.el-tabs__item) {
  border: 1px solid #dbe8e3;
  border-radius: 999px;
  background: #ffffff;
  color: #475569;
  height: 34px;
  line-height: 34px;
  margin-right: 8px;
}

.pill-tabs :deep(.el-tabs__item.is-active) {
  background: #ccfbf1;
  color: #0f766e;
  border-color: #5eead4;
  font-weight: 700;
}

.l3-pill-tabs,
.role-selector {
  --el-color-primary: #0f766e;
}

.system-grid,
.mimic-grid,
.guardrail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 12px;
}

.system-card,
.mimic-card,
.role-card,
.nested-panel {
  padding: 14px;
}

.role-card {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
}

.role-card h2 {
  margin: 0;
}

.role-card p {
  color: #475569;
}

.tag-gap {
  margin: 0 8px 8px 0;
}

.system-card__title,
.mimic-card__footer {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  align-items: center;
}

.system-card__title {
  font-weight: 700;
  color: #0f172a;
}

.system-card__meta,
.mimic-card p {
  margin: 8px 0;
  color: #64748b;
  font-size: 13px;
}

.system-card__metrics {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
  color: #334155;
  font-size: 13px;
}

.mimic-card__bar {
  height: 56px;
  border-radius: 6px;
  background: linear-gradient(90deg, #ecfeff, #f0fdf4);
  border: 1px solid #ccfbf1;
}

.table-shell :deep(.el-card__body) {
  padding-top: 12px;
}

.operations-table {
  border-radius: 10px;
  overflow: hidden;
  border: 1px solid var(--uhmi-table-border);
}

.operations-table :deep(th.el-table__cell) {
  background: var(--uhmi-table-header);
  color: #334155;
  font-weight: 700;
}

.operations-table :deep(td.el-table__cell) {
  padding: 10px 0;
}

.guardrail-pill {
  display: flex;
  min-height: 48px;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  background: #fff;
}

.future-path {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.future-path span {
  padding: 8px 10px;
  border-radius: 999px;
  background: #f8fafc;
  border: 1px solid #dbe4ea;
  color: #334155;
  font-size: 13px;
}

.role-context-labels {
  display: grid;
  gap: 8px;
  margin-top: 14px;
  color: #475569;
  font-size: 13px;
}
</style>
