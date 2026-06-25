<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import RouteL3ContentPanel from '@/components/RouteL3ContentPanel.vue'
import {
  airportGaReadonlyEndpoints,
  getAirportGaReadonlySections,
  type AirportEndpointKey,
  type AirportGaReadonlyEndpointDefinition,
  type AirportGaReadonlyPayload,
} from '@/services/api/airportGaReadonly'

interface SectionState {
  endpoint: AirportGaReadonlyEndpointDefinition
  payload: AirportGaReadonlyPayload | null
  status: 'idle' | 'loading' | 'ready' | 'error'
  error: string
}

const route = useRoute()
const router = useRouter()

const sections = ref<SectionState[]>(
  airportGaReadonlyEndpoints.map((endpoint) => ({
    endpoint,
    payload: null,
    status: 'idle',
    error: '',
  })),
)
const loading = ref(false)
const lastLoaded = ref('')

const activeEndpointKey = ref<AirportEndpointKey>('AIRPORT_OVERVIEW')

const activeSection = computed(() =>
  sections.value.find((section) => section.endpoint.key === activeEndpointKey.value) ?? sections.value[0],
)

const readyCount = computed(() => sections.value.filter((section) => section.status === 'ready').length)
const errorCount = computed(() => sections.value.filter((section) => section.status === 'error').length)
const allReadOnly = computed(() =>
  sections.value.every((section) =>
    !section.payload
      || (
        section.payload.readOnly === true
        && section.payload.productionActivation === false
        && section.payload.runtimeActivation === false
        && section.payload.dbWrite === false
        && section.payload.approvalExecution === false
        && section.payload.customerIdentifierLeakage === false
      ),
  ),
)

const activeDataPreview = computed(() => toPreviewRows(activeSection.value.payload?.data))
const activeSummaryRows = computed(() => toPreviewRows(activeSection.value.payload?.summary))
const activeSource = computed(() => activeSection.value.payload?.source ?? null)

function syncActiveFromRoute(): void {
  const matched = airportGaReadonlyEndpoints.find((endpoint) => endpoint.frontendPath === route.path)
  activeEndpointKey.value = matched?.key ?? 'AIRPORT_OVERVIEW'
}

function onSelectSection(key: AirportEndpointKey): void {
  const endpoint = airportGaReadonlyEndpoints.find((item) => item.key === key)
  if (endpoint && endpoint.frontendPath !== route.path) {
    void router.push(endpoint.frontendPath)
  }
  activeEndpointKey.value = key
}

async function loadSections(): Promise<void> {
  loading.value = true
  sections.value = sections.value.map((section) => ({ ...section, status: 'loading', error: '' }))

  try {
    const payloads = await getAirportGaReadonlySections()
    const payloadByKey = new Map(payloads.map((payload) => [payload.endpointKey, payload]))
    sections.value = sections.value.map((section) => ({
      ...section,
      payload: payloadByKey.get(section.endpoint.key) ?? null,
      status: payloadByKey.has(section.endpoint.key) ? 'ready' : 'error',
      error: payloadByKey.has(section.endpoint.key) ? '' : 'No payload returned for endpoint.',
    }))
    lastLoaded.value = new Date().toLocaleString()
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Airport read-only API unavailable.'
    sections.value = sections.value.map((section) => ({
      ...section,
      status: 'error',
      error: message,
    }))
  } finally {
    loading.value = false
  }
}

function isSafeDisplayKey(key: string): boolean {
  const normalized = key.toLowerCase()
  return !['customerassetidentifier', 'assetid', 'deviceid'].includes(normalized)
}

function isSafeDisplayValue(value: unknown): boolean {
  return !(typeof value === 'string' && value.startsWith('/') && !value.startsWith('/api/') && !value.startsWith('/one/'))
}

function formatValue(value: unknown): string {
  if (!isSafeDisplayValue(value)) {
    return '[redacted]'
  }
  if (value === null || value === undefined) {
    return '—'
  }
  if (typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean') {
    return String(value)
  }
  if (Array.isArray(value)) {
    return `${value.length} item${value.length === 1 ? '' : 's'}`
  }
  if (typeof value === 'object') {
    return `${Object.keys(value as Record<string, unknown>).length} fields`
  }
  return String(value)
}

function toPreviewRows(value: unknown): Array<Record<string, string>> {
  if (Array.isArray(value)) {
    return value.slice(0, 8).map((item, index) => {
      if (typeof item !== 'object' || item === null) {
        return { row: String(index + 1), value: formatValue(item) }
      }
      const source = item as Record<string, unknown>
      const row: Record<string, string> = { row: String(index + 1) }
      for (const [key, itemValue] of Object.entries(source).slice(0, 6)) {
        if (isSafeDisplayKey(key)) {
          row[key] = formatValue(itemValue)
        }
      }
      return row
    })
  }
  if (typeof value === 'object' && value !== null) {
    return Object.entries(value as Record<string, unknown>)
      .filter(([key, itemValue]) => isSafeDisplayKey(key) && isSafeDisplayValue(itemValue))
      .slice(0, 12)
      .map(([key, itemValue]) => ({ field: key, value: formatValue(itemValue) }))
  }
  return [{ field: 'value', value: formatValue(value) }]
}

watch(
  () => route.path,
  () => syncActiveFromRoute(),
  { immediate: true },
)

onMounted(() => {
  void loadSections()
})
</script>

<template>
  <section class="airport-page">
    <RouteL3ContentPanel />

    <header class="airport-page__hero">
      <div>
        <p class="eyebrow">VANTARIS ONE Airport Solution Package</p>
        <h1>Airport GA Read-Only Operations Console</h1>
        <p class="hero-copy">
          Projection-backed view consuming the eight GA-R1 validated GET endpoints. No actions, writes,
          approvals, device connections, or runtime activation are exposed here.
        </p>
      </div>
      <el-button type="primary" plain :loading="loading" @click="loadSections">
        Refresh read-only data
      </el-button>
    </header>

    <el-row :gutter="16" class="metric-row">
      <el-col :span="6">
        <el-card shadow="never">
          <div class="metric-value">{{ readyCount }}/8</div>
          <div class="metric-label">GET sections ready</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="never">
          <div class="metric-value">{{ errorCount }}</div>
          <div class="metric-label">Load errors</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="never">
          <div class="metric-value">{{ allReadOnly ? 'PASS' : 'REVIEW' }}</div>
          <div class="metric-label">Read-only flags</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="never">
          <div class="metric-value">GET only</div>
          <div class="metric-label">API client mode</div>
        </el-card>
      </el-col>
    </el-row>

    <el-alert
      title="GA-R3 guardrail: this page is read-only and has no POST, PUT, PATCH, DELETE, approval, DB write, or device-control path."
      type="success"
      :closable="false"
      show-icon
    />

    <el-card shadow="never" class="section-card">
      <template #header>
        <div class="section-card__header">
          <span>Airport console sections</span>
          <span class="muted">Last loaded: {{ lastLoaded || 'not loaded yet' }}</span>
        </div>
      </template>

      <el-tabs :model-value="activeEndpointKey" @tab-change="(name: unknown) => onSelectSection(name as AirportEndpointKey)">
        <el-tab-pane
          v-for="section in sections"
          :key="section.endpoint.key"
          :label="section.endpoint.title"
          :name="section.endpoint.key"
        />
      </el-tabs>

      <div class="active-section">
        <div class="active-section__title">
          <div>
            <h2>{{ activeSection.endpoint.title }}</h2>
            <p>{{ activeSection.endpoint.frontendPath }}</p>
          </div>
          <el-tag :type="activeSection.status === 'ready' ? 'success' : activeSection.status === 'error' ? 'danger' : 'info'">
            {{ activeSection.status }}
          </el-tag>
        </div>

        <el-alert
          v-if="activeSection.error"
          :title="activeSection.error"
          type="error"
          :closable="false"
          show-icon
        />

        <el-descriptions v-if="activeSection.payload" :column="3" border>
          <el-descriptions-item label="Platform">{{ activeSection.payload.platform }}</el-descriptions-item>
          <el-descriptions-item label="Industry">{{ activeSection.payload.industryProjection }}</el-descriptions-item>
          <el-descriptions-item label="Endpoint">{{ activeSection.payload.endpointKey }}</el-descriptions-item>
          <el-descriptions-item label="Read only">{{ activeSection.payload.readOnly }}</el-descriptions-item>
          <el-descriptions-item label="Production activation">{{ activeSection.payload.productionActivation }}</el-descriptions-item>
          <el-descriptions-item label="Runtime activation">{{ activeSection.payload.runtimeActivation }}</el-descriptions-item>
          <el-descriptions-item label="DB write">{{ activeSection.payload.dbWrite }}</el-descriptions-item>
          <el-descriptions-item label="Approval execution">{{ activeSection.payload.approvalExecution }}</el-descriptions-item>
          <el-descriptions-item label="Customer identifier leakage">{{ activeSection.payload.customerIdentifierLeakage }}</el-descriptions-item>
        </el-descriptions>

        <el-row v-if="activeSource" :gutter="16" class="detail-row">
          <el-col :span="12">
            <el-card shadow="never">
              <template #header>Projection source</template>
              <p><strong>Type:</strong> {{ activeSource.type }}</p>
              <p><strong>Artifact:</strong> {{ activeSource.path }}</p>
              <p><strong>Root key:</strong> {{ activeSource.rootKey }}</p>
              <p><strong>Authority:</strong> {{ activeSource.authority }}</p>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card shadow="never">
              <template #header>Summary preview</template>
              <el-table :data="activeSummaryRows" size="small" max-height="260">
                <el-table-column v-for="key in Object.keys(activeSummaryRows[0] ?? {})" :key="key" :prop="key" :label="key" />
              </el-table>
            </el-card>
          </el-col>
        </el-row>

        <el-card shadow="never" class="detail-row">
          <template #header>Data preview</template>
          <el-table :data="activeDataPreview" size="small" max-height="360">
            <el-table-column v-for="key in Object.keys(activeDataPreview[0] ?? {})" :key="key" :prop="key" :label="key" />
          </el-table>
        </el-card>
      </div>
    </el-card>
  </section>
</template>

<style scoped>
.airport-page {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.airport-page__hero {
  display: flex;
  justify-content: space-between;
  gap: 1.5rem;
  padding: 1.5rem;
  color: #f8fafc;
  background: linear-gradient(135deg, #0f172a, #1e3a8a);
  border-radius: 16px;
}

.airport-page__hero h1 {
  margin: 0.2rem 0 0.5rem;
  font-size: 1.75rem;
}

.eyebrow {
  margin: 0;
  color: #bfdbfe;
  font-size: 0.8rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.hero-copy {
  max-width: 820px;
  margin: 0;
  color: #dbeafe;
}

.metric-row {
  row-gap: 1rem;
}

.metric-value {
  font-size: 1.4rem;
  font-weight: 700;
  color: #0f172a;
}

.metric-label,
.muted {
  color: #64748b;
  font-size: 0.85rem;
}

.section-card,
.detail-row {
  margin-top: 1rem;
}

.section-card__header,
.active-section__title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.active-section {
  margin-top: 1rem;
}

.active-section h2 {
  margin: 0;
  font-size: 1.25rem;
}

.active-section p {
  margin: 0.25rem 0;
  color: #475569;
}
</style>
