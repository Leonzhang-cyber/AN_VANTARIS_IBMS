<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  getUhmiHealth,
  getUhmiMenuIa,
  getUhmiSection,
  uhmiSections,
  type UhmiHealthPayload,
  type UhmiMenuIaPayload,
  type UhmiSectionKey,
  type UhmiSectionPayload,
} from '@/services/api/uhmi'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const health = ref<UhmiHealthPayload | null>(null)
const menuIa = ref<UhmiMenuIaPayload | null>(null)
const section = ref<UhmiSectionPayload | null>(null)
const loadError = ref('')
const activeSectionKey = ref<UhmiSectionKey>('HMI_OVERVIEW')

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
    const [healthPayload, menuPayload] = await Promise.all([
      getUhmiHealth(),
      getUhmiMenuIa(),
    ])
    health.value = healthPayload
    menuIa.value = menuPayload
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
  <section class="uhmi-page">
    <header class="uhmi-hero">
      <div>
        <p class="eyebrow">VANTARIS ONE / UConsole</p>
        <h1>UHMI Workspace</h1>
        <p class="hero-copy">
          Unified Human-Machine Interface read-only workspace for cross-industry operations context.
          Device/System data flows through EDGE, LINK, and CODE before reaching UConsole/UHMI.
        </p>
      </div>
      <div class="status-stack">
        <el-tag type="success">GET only</el-tag>
        <el-tag type="success">Read-only</el-tag>
        <el-tag type="info">UConsole workspace</el-tag>
      </div>
    </header>

    <el-alert
      v-if="loadError"
      type="error"
      show-icon
      :closable="false"
      :title="loadError"
      class="block-space"
    />

    <el-row :gutter="16" class="block-space">
      <el-col :span="6">
        <el-card shadow="never">
          <div class="metric-value">{{ health?.status || 'PASS' }}</div>
          <div class="metric-label">Workspace status</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="never">
          <div class="metric-value">{{ menuIa?.menuItems.length || uhmiSections.length }}</div>
          <div class="metric-label">L3 page views</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="never">
          <div class="metric-value">{{ allGuardrailsPass ? 'PASS' : 'REVIEW' }}</div>
          <div class="metric-label">Boundary guardrails</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="never">
          <div class="metric-value">0</div>
          <div class="metric-label">Runtime actions</div>
        </el-card>
      </el-col>
    </el-row>

    <el-card v-loading="loading" shadow="never" class="block-space">
      <template #header>
        <div class="card-header">
          <span>UHMI workspace sections</span>
          <el-tag type="success">L1/L2 sidebar, L3 inside page</el-tag>
        </div>
      </template>

      <el-tabs :model-value="activeSectionKey" @tab-change="(name: unknown) => selectSection(name as UhmiSectionKey)">
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

    <el-card shadow="never" class="block-space">
      <template #header>Read-only projection rows</template>
      <el-table :data="section?.rows || []" border>
        <el-table-column prop="name" label="Name" min-width="220" />
        <el-table-column prop="state" label="State" min-width="150" />
        <el-table-column prop="source" label="Source" min-width="220" />
        <el-table-column prop="actionEnabled" label="Action enabled" width="160" />
      </el-table>
    </el-card>

    <el-card shadow="never" class="block-space">
      <template #header>Boundary guardrails</template>
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
  </section>
</template>

<style scoped>
.uhmi-page {
  padding: 24px;
}

.uhmi-hero,
.card-header,
.section-heading {
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
  text-transform: uppercase;
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

.guardrail-pill {
  display: flex;
  min-height: 48px;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  background: #fff;
}
</style>

