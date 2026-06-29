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

const activeDataRows = computed(() => toDisplayRows(activeSection.value.payload?.data))
const activeSummaryRows = computed(() => toDisplayRows(activeSection.value.payload?.summary))
const activeSource = computed(() => activeSection.value.payload?.source ?? null)
const isAlarmOperations = computed(() => activeEndpointKey.value === 'ALARMS_EVENTS')
const isFaultOperations = computed(() => activeEndpointKey.value === 'FAULT_CASES')
const isOperationalChain = computed(() => isAlarmOperations.value || isFaultOperations.value)

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

function asRecord(value: unknown): Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value) ? value as Record<string, unknown> : {}
}

function asRecordArray(value: unknown): Record<string, unknown>[] {
  if (Array.isArray(value)) {
    return value.filter((item) => typeof item === 'object' && item !== null).map((item) => item as Record<string, unknown>)
  }
  if (typeof value === 'object' && value !== null) {
    const record = value as Record<string, unknown>
    const nested = Object.values(record).find((item) => Array.isArray(item))
    if (Array.isArray(nested)) {
      return asRecordArray(nested)
    }
    return [record]
  }
  return []
}

function pick(row: Record<string, unknown> | undefined, keys: string[], defaultValue = 'Not provided by readonly data'): string {
  for (const key of keys) {
    const value = row?.[key]
    if (value !== undefined && value !== null && value !== '') {
      return formatValue(value)
    }
  }
  return defaultValue
}

function statusLabel(value: unknown, defaultValue = 'Not provided by readonly data'): string {
  const raw = String(value ?? defaultValue)
  const mapped: Record<string, string> = {
    active: 'Active',
    critical: 'Critical',
    high: 'High',
    open: 'Open',
    acknowledged: 'Acknowledged',
    unacknowledged: 'Unacknowledged',
    escalated: 'Escalated',
    not_escalated: 'Not escalated',
    linked: 'Linked',
    not_linked: 'Not linked',
    missing: 'Missing',
    blocked: 'Blocked',
    ready: 'Ready',
    pending: 'Pending',
    pending_evidence: 'Pending evidence',
    closure_blocked: 'Closure blocked',
    in_progress: 'In progress',
  }
  return mapped[raw.toLowerCase()] ?? raw.replace(/_/g, ' ').replace(/\b\w/g, (char) => char.toUpperCase())
}

function toDisplayRows(value: unknown): Array<Record<string, string>> {
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

const operationalRows = computed(() => {
  const payload = activeSection.value.payload
  const rows = asRecordArray(payload?.data)
  if (rows.length > 0) return rows
  const summary = asRecord(payload?.summary)
  return Object.keys(summary).length > 0 ? [summary] : []
})

const primaryOperationalRow = computed(() => operationalRows.value[0] ?? {})

const alarmRows = computed(() => operationalRows.value.map((row, index) => ({
  alarmId: pick(row, ['alarmId', 'alarm_id', 'id', 'eventId', 'event_id'], `Alarm ${index + 1}`),
  severity: statusLabel(pick(row, ['severity', 'alarmSeverity', 'priority'])),
  priority: statusLabel(pick(row, ['priority', 'alarmPriority', 'riskPriority'])),
  affectedAsset: pick(row, ['affectedAsset', 'assetName', 'asset', 'asset_name']),
  affectedSystem: pick(row, ['affectedSystem', 'systemName', 'system', 'system_name']),
  location: pick(row, ['zoneLocation', 'location', 'zone', 'space']),
  sourceEvent: pick(row, ['sourceEvent', 'source_event', 'eventId', 'event_id']),
  acknowledgementState: statusLabel(pick(row, ['acknowledgementState', 'ackState', 'ack_status', 'acknowledged'])),
  escalationState: statusLabel(pick(row, ['escalationState', 'escalation_status', 'escalated'])),
  linkedFaultCase: pick(row, ['linkedFaultCase', 'faultCaseId', 'fault_case_id', 'faultId', 'fault_id']),
  linkedWorkOrder: pick(row, ['linkedWorkOrder', 'workOrderId', 'work_order_id']),
  evidenceState: statusLabel(pick(row, ['evidenceState', 'evidence_status', 'evidence'])),
  closureReadiness: statusLabel(pick(row, ['closureReadiness', 'closure_readiness', 'closureStatus', 'closure_status'])),
})))

const faultRows = computed(() => operationalRows.value.map((row, index) => ({
  faultCase: pick(row, ['faultCaseId', 'fault_case_id', 'faultId', 'fault_id', 'id'], `Fault Case ${index + 1}`),
  severity: statusLabel(pick(row, ['severity', 'faultSeverity', 'priority'])),
  detail: pick(row, ['faultDetail', 'detail', 'title', 'description']),
  rootCause: pick(row, ['rootCause', 'root_cause', 'correlation', 'rca']),
  recommendedAction: pick(row, ['recommendedAction', 'recommended_action', 'action']),
  linkedAlarm: pick(row, ['linkedAlarm', 'alarmId', 'alarm_id', 'sourceAlarm']),
  sourceEvent: pick(row, ['sourceEvent', 'source_event', 'eventId', 'event_id']),
  affectedAsset: pick(row, ['affectedAsset', 'assetName', 'asset', 'asset_name']),
  affectedSystem: pick(row, ['affectedSystem', 'systemName', 'system', 'system_name']),
  location: pick(row, ['zoneLocation', 'location', 'zone', 'space']),
  linkedWorkOrder: pick(row, ['linkedWorkOrder', 'workOrderId', 'work_order_id']),
  evidenceTimeline: pick(row, ['evidenceTimeline', 'evidence_timeline', 'evidenceId', 'evidence_id']),
  closureReadiness: statusLabel(pick(row, ['closureReadiness', 'closure_readiness', 'closureStatus', 'closure_status'])),
})))

function countMatching(rows: Record<string, string>[], keys: string[], values: string[]): number {
  const normalizedValues = values.map((value) => value.toLowerCase())
  return rows.filter((row) => keys.some((key) => normalizedValues.includes(String(row[key] ?? '').toLowerCase()))).length
}

const alarmDecisionSignals = computed(() => [
  { label: 'Active Alarms', value: alarmRows.value.length || Number(asRecord(activeSection.value.payload?.summary).activeAlarms ?? 0) },
  { label: 'Critical / High Severity', value: countMatching(alarmRows.value, ['severity', 'priority'], ['Critical', 'High']) },
  { label: 'Unacknowledged', value: countMatching(alarmRows.value, ['acknowledgementState'], ['Unacknowledged', 'Open', 'Pending']) },
  { label: 'Escalated', value: countMatching(alarmRows.value, ['escalationState'], ['Escalated']) },
  { label: 'Fault-linked', value: alarmRows.value.filter((row) => !row.linkedFaultCase.startsWith('Not provided')).length },
  { label: 'Work Order-linked', value: alarmRows.value.filter((row) => !row.linkedWorkOrder.startsWith('Not provided')).length },
  { label: 'Evidence Missing', value: countMatching(alarmRows.value, ['evidenceState'], ['Missing', 'Pending Evidence']) },
  { label: 'Closure Blocked', value: countMatching(alarmRows.value, ['closureReadiness'], ['Blocked', 'Closure Blocked']) },
])

const faultDecisionSignals = computed(() => [
  { label: 'Active Faults', value: faultRows.value.length || Number(asRecord(activeSection.value.payload?.summary).activeFaults ?? 0) },
  { label: 'Critical Faults', value: countMatching(faultRows.value, ['severity'], ['Critical']) },
  { label: 'Fault Detail', value: pick(primaryOperationalRow.value, ['faultDetail', 'detail', 'title']) },
  { label: 'Root Cause / Correlation', value: pick(primaryOperationalRow.value, ['rootCause', 'root_cause', 'correlation', 'rca']) },
  { label: 'Recommended Actions', value: pick(primaryOperationalRow.value, ['recommendedAction', 'recommended_action', 'action']) },
  { label: 'Linked Work Order', value: pick(primaryOperationalRow.value, ['linkedWorkOrder', 'workOrderId', 'work_order_id']) },
  { label: 'Evidence Timeline', value: pick(primaryOperationalRow.value, ['evidenceTimeline', 'evidence_timeline', 'evidenceId', 'evidence_id']) },
  { label: 'Closure Readiness', value: statusLabel(pick(primaryOperationalRow.value, ['closureReadiness', 'closure_readiness', 'closureStatus', 'closure_status'])) },
])

const eventTimelineRows = computed(() => operationalRows.value.map((row, index) => ({
  sourceEvent: pick(row, ['sourceEvent', 'source_event', 'eventId', 'event_id'], `Event ${index + 1}`),
  eventTime: pick(row, ['eventTime', 'event_time', 'timestamp', 'time']),
  stateTransition: pick(row, ['stateTransition', 'state_transition', 'state', 'status']),
  operatorAction: pick(row, ['operatorAction', 'operator_action', 'action']),
  evidenceReference: pick(row, ['evidenceReference', 'evidence_reference', 'evidenceId', 'evidence_id']),
})))

const alarmOperationalChain = ['Alarm Intake', 'Event Timeline', 'Fault Case', 'Root Cause / Correlation', 'Work Order', 'Evidence Timeline', 'Closure Readiness']

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
          Readonly airport operational data across airport overview, assets, alarms, faults, work orders, evidence, and reports.
          No actions, writes, approvals, device connections, or runtime control are exposed here.
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
            <p>Readonly airport operational data</p>
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

        <div v-if="isAlarmOperations" class="ops-workspace">
          <header class="ops-head">
            <div>
              <p class="eyebrow">Faults & Events</p>
              <h2>Alarm / Fault Operations Console</h2>
              <p>Operational chain for alarm intake, event timeline, fault linkage, work order handoff, evidence timeline and closure readiness.</p>
            </div>
          </header>

          <section class="ops-signals" aria-label="Alarm decision signals">
            <article v-for="signal in alarmDecisionSignals" :key="signal.label">
              <span>{{ signal.label }}</span>
              <strong>{{ signal.value }}</strong>
            </article>
          </section>

          <section class="ops-chain" aria-label="Alarm operational chain">
            <strong v-for="step in alarmOperationalChain" :key="step">{{ step }}</strong>
          </section>

          <section class="ops-grid">
            <article class="ops-card ops-card--wide">
              <h3>Alarm Context</h3>
              <el-table :data="alarmRows" size="small" stripe>
                <el-table-column prop="alarmId" label="Alarm ID" min-width="130" fixed />
                <el-table-column prop="severity" label="Severity" min-width="110" />
                <el-table-column prop="priority" label="Priority" min-width="110" />
                <el-table-column prop="affectedAsset" label="Affected Asset" min-width="180" />
                <el-table-column prop="affectedSystem" label="Affected System" min-width="170" />
                <el-table-column prop="location" label="Zone / Location" min-width="190" />
                <el-table-column prop="sourceEvent" label="Source Event" min-width="150" />
                <el-table-column prop="acknowledgementState" label="Acknowledgement State" min-width="190" />
                <el-table-column prop="escalationState" label="Escalation State" min-width="160" />
                <el-table-column prop="linkedFaultCase" label="Linked Fault Case" min-width="170" />
                <el-table-column prop="linkedWorkOrder" label="Linked Work Order" min-width="170" />
                <el-table-column prop="evidenceState" label="Evidence State" min-width="150" />
                <el-table-column prop="closureReadiness" label="Closure Readiness" min-width="170" />
              </el-table>
            </article>

            <article class="ops-card">
              <h3>Event Timeline</h3>
              <el-table :data="eventTimelineRows" size="small" stripe>
                <el-table-column prop="sourceEvent" label="Source Event" min-width="140" />
                <el-table-column prop="eventTime" label="Event Time" min-width="150" />
                <el-table-column prop="stateTransition" label="State Transition" min-width="170" />
                <el-table-column prop="operatorAction" label="Operator Action" min-width="170" />
                <el-table-column prop="evidenceReference" label="Evidence Reference" min-width="180" />
              </el-table>
            </article>

            <article class="ops-card ops-list">
              <h3>Work Management / MMS Control Center</h3>
              <p><strong>Assignment / Dispatch</strong>{{ pick(primaryOperationalRow, ['assignmentDispatch', 'assignedTeam', 'assigned_team', 'owner']) }}</p>
              <p><strong>SLA Risk</strong>{{ statusLabel(pick(primaryOperationalRow, ['slaRisk', 'sla_risk', 'priority'])) }}</p>
              <p><strong>Closure Evidence</strong>{{ statusLabel(pick(primaryOperationalRow, ['closureEvidence', 'closure_evidence', 'evidenceState', 'evidence_status'])) }}</p>
            </article>

            <article class="ops-card ops-list">
              <h3>Floor Plan / HMI Map Operations</h3>
              <p><strong>Affected Zone</strong>{{ pick(primaryOperationalRow, ['zone', 'location', 'space']) }}</p>
              <p><strong>Fault Location Overlay</strong>{{ pick(primaryOperationalRow, ['faultLocation', 'fault_location', 'location']) }}</p>
              <p><strong>Work Order Location Route</strong>{{ pick(primaryOperationalRow, ['workOrderRoute', 'work_order_route', 'route']) }}</p>
              <p><strong>Technician Navigation</strong>{{ pick(primaryOperationalRow, ['technicianNavigation', 'technician_navigation', 'navigation']) }}</p>
            </article>

            <article class="ops-card ops-list">
              <h3>Evidence / Closure</h3>
              <p><strong>Evidence Timeline</strong>{{ pick(primaryOperationalRow, ['evidenceTimeline', 'evidence_timeline', 'evidenceId', 'evidence_id']) }}</p>
              <p><strong>Missing Evidence</strong>{{ statusLabel(pick(primaryOperationalRow, ['missingEvidence', 'missing_evidence', 'evidenceState', 'evidence_status'])) }}</p>
              <p><strong>Closure Readiness</strong>{{ statusLabel(pick(primaryOperationalRow, ['closureReadiness', 'closure_readiness', 'closureStatus', 'closure_status'])) }}</p>
              <p><strong>Export Evidence Center</strong>{{ pick(primaryOperationalRow, ['exportEvidenceCenter', 'export_evidence_center', 'exportStatus', 'export_status']) }}</p>
            </article>
          </section>
        </div>

        <div v-else-if="isFaultOperations" class="ops-workspace">
          <header class="ops-head">
            <div>
              <p class="eyebrow">Faults & Events</p>
              <h2>Fault Operations Console</h2>
              <p>Operational workspace for active faults, root cause correlation, recommended actions, linked alarms, work orders, evidence timeline and closure readiness.</p>
            </div>
          </header>

          <section class="ops-signals" aria-label="Fault decision signals">
            <article v-for="signal in faultDecisionSignals" :key="signal.label">
              <span>{{ signal.label }}</span>
              <strong>{{ signal.value }}</strong>
            </article>
          </section>

          <section class="ops-chain" aria-label="Fault operational chain">
            <strong v-for="step in alarmOperationalChain" :key="step">{{ step }}</strong>
          </section>

          <section class="ops-grid">
            <article class="ops-card ops-card--wide">
              <h3>Fault Detail</h3>
              <el-table :data="faultRows" size="small" stripe>
                <el-table-column prop="faultCase" label="Fault Case" min-width="150" fixed />
                <el-table-column prop="severity" label="Severity" min-width="110" />
                <el-table-column prop="detail" label="Fault Detail" min-width="220" />
                <el-table-column prop="rootCause" label="Root Cause / Correlation" min-width="230" />
                <el-table-column prop="recommendedAction" label="Recommended Actions" min-width="210" />
                <el-table-column prop="linkedAlarm" label="Linked Alarm" min-width="150" />
                <el-table-column prop="sourceEvent" label="Source Event" min-width="150" />
                <el-table-column prop="affectedAsset" label="Affected Asset" min-width="180" />
                <el-table-column prop="affectedSystem" label="Affected System" min-width="170" />
                <el-table-column prop="location" label="Zone / Location" min-width="190" />
                <el-table-column prop="linkedWorkOrder" label="Linked Work Order" min-width="170" />
                <el-table-column prop="evidenceTimeline" label="Evidence Timeline" min-width="170" />
                <el-table-column prop="closureReadiness" label="Closure Readiness" min-width="170" />
              </el-table>
            </article>

            <article class="ops-card ops-list">
              <h3>Root Cause / Correlation</h3>
              <p><strong>Correlation</strong>{{ pick(primaryOperationalRow, ['correlation', 'rootCause', 'root_cause', 'rca']) }}</p>
              <p><strong>Recommended Actions</strong>{{ pick(primaryOperationalRow, ['recommendedAction', 'recommended_action', 'action']) }}</p>
              <p><strong>Linked Alarm</strong>{{ pick(primaryOperationalRow, ['linkedAlarm', 'alarmId', 'alarm_id']) }}</p>
            </article>

            <article class="ops-card ops-list">
              <h3>Work Management / MMS Control Center</h3>
              <p><strong>Linked Work Order</strong>{{ pick(primaryOperationalRow, ['linkedWorkOrder', 'workOrderId', 'work_order_id']) }}</p>
              <p><strong>Assignment / Dispatch</strong>{{ pick(primaryOperationalRow, ['assignmentDispatch', 'assignedTeam', 'assigned_team', 'owner']) }}</p>
              <p><strong>Closure Evidence</strong>{{ statusLabel(pick(primaryOperationalRow, ['closureEvidence', 'closure_evidence', 'evidenceState', 'evidence_status'])) }}</p>
            </article>

            <article class="ops-card ops-list">
              <h3>Evidence / Closure</h3>
              <p><strong>Evidence Timeline</strong>{{ pick(primaryOperationalRow, ['evidenceTimeline', 'evidence_timeline', 'evidenceId', 'evidence_id']) }}</p>
              <p><strong>Closure Readiness</strong>{{ statusLabel(pick(primaryOperationalRow, ['closureReadiness', 'closure_readiness', 'closureStatus', 'closure_status'])) }}</p>
              <p><strong>Export Evidence Center</strong>{{ pick(primaryOperationalRow, ['exportEvidenceCenter', 'export_evidence_center', 'exportStatus', 'export_status']) }}</p>
            </article>
          </section>
        </div>

        <template v-else>
        <el-descriptions v-if="activeSection.payload" :column="3" border>
          <el-descriptions-item label="Platform">{{ activeSection.payload.platform }}</el-descriptions-item>
          <el-descriptions-item label="Industry">{{ activeSection.payload.industryProjection }}</el-descriptions-item>
          <el-descriptions-item label="Section">{{ activeSection.endpoint.title }}</el-descriptions-item>
          <el-descriptions-item label="Read only">{{ activeSection.payload.readOnly }}</el-descriptions-item>
          <el-descriptions-item label="Production activation">{{ activeSection.payload.productionActivation }}</el-descriptions-item>
          <el-descriptions-item label="Runtime control">{{ activeSection.payload.runtimeActivation }}</el-descriptions-item>
          <el-descriptions-item label="DB write">{{ activeSection.payload.dbWrite }}</el-descriptions-item>
          <el-descriptions-item label="Approval execution">{{ activeSection.payload.approvalExecution }}</el-descriptions-item>
          <el-descriptions-item label="Customer identifier leakage">{{ activeSection.payload.customerIdentifierLeakage }}</el-descriptions-item>
        </el-descriptions>

        <el-row v-if="activeSource" :gutter="16" class="detail-row">
          <el-col :span="12">
            <el-card shadow="never">
              <template #header>Readonly airport operational data</template>
              <p><strong>Type:</strong> {{ activeSource.type }}</p>
              <p><strong>Source Reference:</strong> {{ activeSource.path }}</p>
              <p><strong>Data Domain:</strong> {{ activeSource.rootKey }}</p>
              <p><strong>Authority:</strong> {{ activeSource.authority }}</p>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card shadow="never">
              <template #header>Summary</template>
              <el-table :data="activeSummaryRows" size="small" max-height="260">
                <el-table-column v-for="key in Object.keys(activeSummaryRows[0] ?? {})" :key="key" :prop="key" :label="key" />
              </el-table>
            </el-card>
          </el-col>
        </el-row>

        <el-card shadow="never" class="detail-row">
          <template #header>Data</template>
          <el-table :data="activeDataRows" size="small" max-height="360">
            <el-table-column v-for="key in Object.keys(activeDataRows[0] ?? {})" :key="key" :prop="key" :label="key" />
          </el-table>
        </el-card>
        </template>
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

.ops-workspace {
  display: grid;
  gap: 1rem;
}

.ops-head {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  padding: 1.25rem;
  border: 1px solid #d8e6e1;
  border-radius: 12px;
  background: #f8fbfa;
}

.ops-head h2 {
  margin: 0.2rem 0 0.4rem;
  color: #10201d;
  font-size: 1.45rem;
}

.ops-head p:last-child {
  max-width: 920px;
  color: #52615d;
}

.ops-signals {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0.75rem;
}

.ops-signals article,
.ops-card {
  min-width: 0;
  border: 1px solid #dfe9e5;
  border-radius: 10px;
  background: #ffffff;
}

.ops-signals article {
  display: grid;
  gap: 0.3rem;
  padding: 0.8rem;
}

.ops-signals span,
.ops-list strong {
  color: #64748b;
  font-size: 0.72rem;
  font-weight: 800;
  text-transform: uppercase;
}

.ops-signals strong {
  color: #10201d;
  font-size: 1.15rem;
  line-height: 1.25;
  overflow-wrap: anywhere;
}

.ops-chain {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  padding: 0.85rem;
  border: 1px solid #d8e6e1;
  border-radius: 10px;
  background: #f8fbfa;
}

.ops-chain strong {
  padding: 0.5rem 0.7rem;
  border: 1px solid #cfe4dd;
  border-radius: 999px;
  background: #ffffff;
  color: #10201d;
  font-size: 0.78rem;
}

.ops-chain strong:not(:last-child)::after {
  content: '->';
  margin-left: 0.65rem;
  color: #0f766e;
}

.ops-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1rem;
}

.ops-card {
  display: grid;
  gap: 0.75rem;
  padding: 0.9rem;
  overflow: hidden;
}

.ops-card--wide {
  grid-column: 1 / -1;
}

.ops-card h3 {
  margin: 0;
  color: #10201d;
  font-size: 1rem;
}

.ops-list p {
  display: grid;
  gap: 0.25rem;
  margin: 0;
  color: #10201d;
  line-height: 1.35;
}

@media (max-width: 1100px) {
  .ops-signals,
  .ops-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 720px) {
  .ops-signals,
  .ops-grid {
    grid-template-columns: 1fr;
  }
}
</style>
