<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import {
  AIRPORT_HMI_MAP_ID,
  type AirportHmiMapContent,
  type AirportHmiMapPayload,
  getAirportHmiMapContent,
} from '@/services/api/airportHmiMap'
import { resolveL3ContentConfig, resolveL3RouteContentContext } from '@/services/menu/l3-content-registry'

type VisualMode = 'trend' | 'topology' | 'timeline' | 'workQueue' | 'evidence' | 'security' | 'hmi' | 'reportPack'

const route = useRoute()
const context = computed(() => {
  if (route.path === '/one/airport/assets-topology' && !route.query.menu) {
    return resolveL3RouteContentContext('floor-plan-hmi', route.query.l3)
  }
  return resolveL3RouteContentContext(route.query.menu, route.query.l3)
})
const content = computed(() => (context.value ? resolveL3ContentConfig(context.value) : undefined))
const dashboardWorkbench = computed(() => content.value?.dashboardWorkbench)
const isAirportHmiMap = computed(() => context.value?.l1Label === 'Assets & Locations' && context.value?.l2Id === 'floor-plan-hmi')
const defaultRelatedWorkspaces = ['Work Management', 'Assets & Locations', 'Faults & Events', 'Reports & Documents', 'Governance & Security', 'Integration & Partner Hub']
const sectionKicker = computed(() => {
  if (content.value?.sectionEyebrow) {
    return content.value.sectionEyebrow
  }
  if (context.value?.l2Id === 'workspace-overview') {
    return 'ROLE PRIORITY ENTRY'
  }
  return dashboardWorkbench.value ? 'DASHBOARD DECISION WORKSPACE' : 'Workspace content'
})
const dashboardTabs = computed(() => {
  if (content.value?.l3Tabs?.length) {
    return content.value.l3Tabs
  }

  return (dashboardWorkbench.value?.tabs ?? []).map((label) => ({
    key: label,
    label,
    active: false,
  }))
})
const connectedWorkspaces = computed(() =>
  content.value?.connectedWorkspaces
  ?? content.value?.relatedWorkspaces
  ?? defaultRelatedWorkspaces,
)
const signature = computed(() => `${context.value?.l1Label ?? ''} ${context.value?.l2Id ?? ''} ${context.value?.l2Label ?? ''} ${context.value?.item.label ?? ''}`.toLowerCase())

function score(seed: string, index: number, min = 18, span = 74): number {
  let total = 0
  for (const char of seed) {
    total += char.charCodeAt(0) * (index + 3)
  }
  return min + (total % span)
}

const visualMode = computed<VisualMode>(() => {
  const text = signature.value
  if (/(asset|building|zone|space|topology|graph|twin|edge|link|controller|gateway|system|device|hmi|model)/.test(text)) {
    return text.includes('hmi') ? 'hmi' : 'topology'
  }
  if (/(work|maintenance|sla|assignment|inventory|vendor|incident|remediation|shift)/.test(text)) {
    return 'workQueue'
  }
  if (/(event|alarm|fault|timeline|audit|decision|history|security|cyber|risk|policy|governance|permission|role)/.test(text)) {
    return /(security|cyber|policy|governance|permission|role|risk)/.test(text) ? 'security' : 'timeline'
  }
  if (/(evidence|ucde|document|handover|export|report|compliance|drawing|manual|package)/.test(text)) {
    return /(report|document|handover|export|package)/.test(text) ? 'reportPack' : 'evidence'
  }
  return 'trend'
})

const chartPoints = computed(() => [0, 1, 2, 3, 4, 5].map((index) => score(signature.value, index, 22, 70)))
const chartPolyline = computed(() =>
  chartPoints.value.map((value, index) => `${18 + index * 52},${116 - value}`).join(' '),
)
const barRows = computed(() => ['Normal', 'Watch', 'Action', 'Evidence'].map((label, index) => ({
  label,
  value: score(signature.value, index + 7, 28, 64),
})))
const topologyNodes = computed(() => {
  const l2 = context.value?.l2Label ?? 'Workspace'
  const l3 = context.value?.item.label ?? 'Section'
  return [
    { label: 'Source', x: 8, y: 34, tone: 'source' },
    { label: l2, x: 37, y: 12, tone: 'workspace' },
    { label: l3, x: 64, y: 40, tone: 'section' },
    { label: 'Evidence', x: 39, y: 68, tone: 'evidence' },
    { label: 'Report', x: 78, y: 70, tone: 'report' },
  ]
})
const queueColumns = computed(() => ['Intake', 'Review', 'Evidence', 'Handoff'].map((label, index) => ({
  label,
  count: score(signature.value, index + 11, 2, 9),
  risk: ['Low', 'Medium', 'High', 'Guarded'][index],
})))
const timelineItems = computed(() => ['Detected', 'Correlated', 'Reviewed', 'Evidence linked', 'Ready'].map((label, index) => ({
  label,
  value: score(signature.value, index + 17, 12, 76),
})))
const matrixRows = computed(() => ['Policy', 'Owner', 'Approval', 'Audit'].map((label, index) => ({
  label,
  state: ['Configured', 'Mapped', 'Review', 'Guarded'][index],
  value: score(signature.value, index + 23, 35, 58),
})))

const airportHmiMapContent = ref<AirportHmiMapContent>()
const airportHmiMapLoading = ref(false)
const airportHmiMapError = ref('')
const airportLayerSelections = ref([
  'Zone Layer',
  'Location Layer',
  'Asset Layer',
  'Point / Tag Layer',
  'Fault Layer',
  'Work Order Layer',
  'Evidence Layer',
])
const airportFilters = ref({
  terminal: 'Terminal 3',
  floor: 'Ground Floor',
  zone: 'All zones',
  system: 'All systems',
  deviceType: 'All device types',
  dataQualityStatus: 'pending_review',
  importBatch: 'Latest quality gate',
})

async function loadAirportHmiMapContent() {
  airportHmiMapLoading.value = true
  airportHmiMapError.value = ''
  try {
    airportHmiMapContent.value = await getAirportHmiMapContent(AIRPORT_HMI_MAP_ID)
  } catch {
    airportHmiMapError.value = 'Readonly airport map data is currently unavailable.'
  } finally {
    airportHmiMapLoading.value = false
  }
}

watch(
  isAirportHmiMap,
  (active) => {
    if (active && !airportHmiMapContent.value && !airportHmiMapLoading.value) {
      void loadAirportHmiMapContent()
    }
  },
  { immediate: true },
)

function payloadRows(payload?: AirportHmiMapPayload, limit = 6): Array<Record<string, unknown>> {
  return Array.isArray(payload?.data) ? payload.data.slice(0, limit) : []
}

function summaryValue(payload: AirportHmiMapPayload | undefined, key: string, defaultValue: string | number | boolean = '0') {
  const value = payload?.summary?.[key]
  return value === undefined || value === null || value === '' ? defaultValue : value
}

function fieldValue(row: Record<string, unknown> | undefined, key: string, defaultValue = 'Pending review') {
  const value = row?.[key]
  return value === undefined || value === null || value === '' ? defaultValue : String(value)
}

function firstField(row: Record<string, unknown> | undefined, keys: string[], defaultValue = 'Pending review') {
  for (const key of keys) {
    const value = row?.[key]
    if (value !== undefined && value !== null && value !== '') {
      return String(value)
    }
  }
  return defaultValue
}

function displayStatus(value: unknown, defaultValue = 'Pending review') {
  const raw = String(value ?? defaultValue)
  const labels: Record<string, string> = {
    blocked_by_data_quality: 'Blocked by asset data quality',
    pending_review: 'Pending review',
    pending_asset_import_clearance: 'Pending asset import clearance',
    not_ready_due_to_asset_quality_blockers: 'Not ready due to asset quality blockers',
    readonly_projection: 'Readonly projection',
    route_hint_only: 'Readonly route available',
    pending_closure_evidence: 'Pending closure evidence',
    blocked_by_asset_quality: 'Blocked by asset quality',
  }
  return labels[raw] ?? raw.replace(/_/g, ' ').replace(/\b\w/g, (char) => char.toUpperCase())
}

const airportData = computed(() => airportHmiMapContent.value)
const airportImportAudit = computed(() => airportData.value?.importAuditSummary)
const airportClosure = computed(() => airportData.value?.closureReadiness)
const airportAssetOverlay = computed(() => airportData.value?.assetOverlay)
const airportDecisionLens = computed(() => airportData.value?.decisionLens)
const airportReadiness = computed(() =>
  airportImportAudit.value?.asset_import_readiness
  ?? airportAssetOverlay.value?.asset_import_readiness
  ?? 'HOLD_BLOCKED',
)
const airportOverlayStatus = computed(() =>
  airportAssetOverlay.value?.asset_overlay_status
  ?? airportImportAudit.value?.asset_overlay_status
  ?? 'blocked_by_data_quality',
)
const airportClosureStatus = computed(() =>
  airportClosure.value?.closure_status
  ?? airportImportAudit.value?.closure_status
  ?? 'not_ready_due_to_asset_quality_blockers',
)
const airportSourceState = computed(() =>
  airportHmiMapError.value
  || airportData.value?.sourceState
  || 'Readonly airport map data is currently unavailable.',
)
const airportDecisionSignals = computed(() => [
  { label: 'Asset Import Readiness', value: airportReadiness.value },
  { label: 'Map Registration', value: 'T3 Ground Floor registered' },
  { label: 'Asset Overlay', value: displayStatus(airportOverlayStatus.value) },
  { label: 'Fault Location Overlay', value: 'Readonly projection active' },
  { label: 'Work Order Route', value: 'Available as readonly route' },
  { label: 'Evidence Closure', value: displayStatus(airportClosureStatus.value) },
])
const airportPanelCards = computed(() => [
  { title: 'Zone Summary', value: summaryValue(airportData.value?.zoneSummary, 'zone_count'), note: `${summaryValue(airportData.value?.zoneSummary, 'asset_records_seen', 5187)} records seen` },
  { title: 'Location Summary', value: summaryValue(airportData.value?.locationSummary, 'location_count'), note: `${summaryValue(airportData.value?.locationSummary, 'pending_review_locations', 0)} pending review` },
  { title: 'Asset Overlay Summary', value: summaryValue(airportData.value?.assetOverlay, 'overlay_markers'), note: 'Readonly projection' },
  { title: 'System Overlay Summary', value: summaryValue(airportData.value?.systemOverlay, 'system_count'), note: 'System-to-asset map' },
  { title: 'Fault Overlay', value: summaryValue(airportData.value?.faultOverlay, 'fault_count'), note: 'Blocked by asset data quality' },
  { title: 'Work Order Route', value: summaryValue(airportData.value?.workOrderOverlay, 'work_order_count'), note: 'Route hint only' },
  { title: 'Evidence Readiness', value: summaryValue(airportData.value?.evidenceOverlay, 'evidence_items_required'), note: 'Pending closure evidence' },
  { title: 'Import Audit Summary', value: summaryValue(airportData.value?.importAuditSummary, 'blocker_count', 2), note: 'Critical blockers' },
])
const airportZoneRows = computed(() => payloadRows(airportData.value?.zoneSummary, 6))
const airportLocationRows = computed(() => payloadRows(airportData.value?.locationSummary, 6))
const airportSystemRows = computed(() => payloadRows(airportData.value?.systemOverlay, 6))
const airportFaultRows = computed(() => payloadRows(airportData.value?.faultOverlay, 5))
const airportWorkOrderRows = computed(() => payloadRows(airportData.value?.workOrderOverlay, 5))
const airportEvidenceRows = computed(() => payloadRows(airportData.value?.evidenceOverlay, 5))
const airportNavigationRows = computed(() => payloadRows(airportData.value?.technicianNavigation, 6))
const airportWorkOrderEvidenceRows = computed(() => payloadRows(airportData.value?.workOrderEvidence, 5))
const airportClosureGateRows = computed(() => payloadRows({ data: airportData.value?.closureReadiness?.gates }, 6))
const airportSelectedContext = computed(() =>
  airportFaultRows.value[0]
  ?? airportWorkOrderRows.value[0]
  ?? airportLocationRows.value[0],
)
const airportOperationalContext = computed(() => airportDecisionLens.value?.operational_context ?? {})
const airportEvidenceContext = computed(() => airportDecisionLens.value?.evidence_context ?? {})
const airportFieldQuestionCards = computed(() => {
  const selected = airportSelectedContext.value
  const workOrder = airportWorkOrderRows.value[0]
  const fault = airportFaultRows.value[0]
  const evidence = airportEvidenceRows.value[0]
  const navigation = airportNavigationRows.value[0]
  return [
    { question: 'Where is the asset?', answer: firstField(selected, ['location', 'space', 'zone'], 'Terminal 3 / Ground Floor') },
    { question: 'What system is affected?', answer: firstField(selected, ['system', 'system_name'], firstField(airportOperationalContext.value, ['related_system'])) },
    { question: 'What fault / alarm / source event is linked?', answer: firstField(fault, ['event_id', 'source_event', 'alarm_id', 'fault_id']) },
    { question: 'Which work order is linked?', answer: firstField(workOrder, ['work_order_id', 'workOrderId']) },
    { question: 'How should the technician navigate?', answer: firstField(navigation, ['navigation_instruction', 'instruction', 'route_instruction', 'route_status'], 'Use readonly route after asset quality clearance') },
    { question: 'What evidence is missing?', answer: firstField(evidence, ['missing_evidence', 'evidence_type', 'status'], displayStatus(firstField(airportEvidenceContext.value, ['status']))) },
  ]
})
const airportLayerReadiness = computed(() => [
  { layer: 'Zone Overlay', state: `${summaryValue(airportData.value?.zoneSummary, 'zone_count')} zones`, note: displayStatus(summaryValue(airportData.value?.zoneSummary, 'data_quality_status', 'pending_review')) },
  { layer: 'Location Summary', state: `${summaryValue(airportData.value?.locationSummary, 'location_count')} locations`, note: displayStatus(summaryValue(airportData.value?.locationSummary, 'map_binding_status', 'pending_review')) },
  { layer: 'Asset Overlay', state: displayStatus(airportOverlayStatus.value), note: `${summaryValue(airportData.value?.assetOverlay, 'overlay_markers')} markers` },
  { layer: 'System Overlay', state: `${summaryValue(airportData.value?.systemOverlay, 'system_count')} systems`, note: 'System-to-asset overlay' },
  { layer: 'Fault Location Overlay', state: 'Readonly projection', note: `${summaryValue(airportData.value?.faultOverlay, 'fault_count')} linked events` },
  { layer: 'Work Order Location Route', state: 'Readonly route available', note: `${summaryValue(airportData.value?.workOrderOverlay, 'work_order_count')} work orders` },
  { layer: 'Technician Navigation', state: 'Route instructions available', note: `${airportNavigationRows.value.length} navigation rows` },
  { layer: 'Evidence Overlay', state: displayStatus(summaryValue(airportData.value?.evidenceOverlay, 'status', 'pending_closure_evidence')), note: `${summaryValue(airportData.value?.evidenceOverlay, 'evidence_items_required')} items required` },
])
const airportMmsFlow = [
  'Fault Location Overlay',
  'Work Order Location Route',
  'Technician Navigation',
  'Closure Evidence',
  'Customer Sign-off',
]
const airportEvidencePanels = computed(() => [
  { label: 'Evidence Overlay', value: summaryValue(airportData.value?.evidenceOverlay, 'evidence_items_required'), detail: displayStatus(summaryValue(airportData.value?.evidenceOverlay, 'status', 'pending_closure_evidence')) },
  { label: 'Work Order Evidence', value: summaryValue(airportData.value?.workOrderEvidence, 'evidence_required_count'), detail: `${summaryValue(airportData.value?.workOrderEvidence, 'work_order_count')} work orders` },
  { label: 'Closure Readiness', value: summaryValue(airportData.value?.closureReadiness, 'ready_to_close'), detail: displayStatus(airportClosureStatus.value) },
  { label: 'Import Audit Summary', value: summaryValue(airportData.value?.importAuditSummary, 'blocker_count', 2), detail: 'Asset Import Quality Gate' },
  { label: 'Export Evidence Center', value: airportData.value?.exportEvidenceCenter.export_ready ? 'Ready' : 'Blocked', detail: displayStatus(airportData.value?.exportEvidenceCenter.export_status ?? 'blocked_by_asset_quality') },
])
</script>

<template>
  <section v-if="content" class="route-l3-panel" aria-label="Menu section content">
    <div class="route-l3-panel__head">
      <div>
        <span class="route-l3-panel__kicker">{{ sectionKicker }}</span>
        <h2>{{ content.title }}</h2>
        <p>{{ content.subtitle }}</p>
      </div>
      <el-button type="primary" plain>{{ content.primaryAction }}</el-button>
    </div>

    <div v-if="dashboardWorkbench" class="route-l3-panel__decision-strip">
      <article>
        <span>Intent</span>
        <strong>{{ dashboardWorkbench.intent }}</strong>
      </article>
      <article>
        <span>Risk signal</span>
        <strong>{{ dashboardWorkbench.riskLabel }} / {{ dashboardWorkbench.riskValue }}</strong>
      </article>
      <article>
        <span>Owner</span>
        <strong>{{ dashboardWorkbench.owner }}</strong>
      </article>
      <article>
        <span>Next step</span>
        <strong>{{ dashboardWorkbench.nextStep }}</strong>
      </article>
      <article>
        <span>Workspace state</span>
        <strong>{{ dashboardWorkbench.workspaceState }}</strong>
      </article>
      <article>
        <span>Data state</span>
        <strong>{{ dashboardWorkbench.dataState }}</strong>
      </article>
    </div>

    <div class="route-l3-panel__metrics">
      <article v-for="metric in content.metrics" :key="metric.label" class="route-l3-panel__metric">
        <span>{{ metric.label }}</span>
        <strong>{{ metric.value }}</strong>
        <em>{{ metric.note }}</em>
      </article>
    </div>

    <div v-if="isAirportHmiMap" class="route-l3-panel__airport-hmi" v-loading="airportHmiMapLoading">
      <div class="route-l3-panel__airport-production-head">
        <div>
          <span>Assets & Locations / Field Operations</span>
          <strong>Floor Plan / HMI Map Operations</strong>
          <p>Field operations view for map readiness, asset location, system overlay, fault location, work order route, technician navigation and closure evidence.</p>
        </div>
        <el-tag type="warning" effect="plain">Asset Import Quality Gate: HOLD_BLOCKED</el-tag>
      </div>

      <div class="route-l3-panel__dashboard-tabs" aria-label="Floor Plan / HMI Map L3 workspace tabs">
        <span v-for="tab in dashboardTabs" :key="tab.key" :class="{ 'route-l3-panel__dashboard-tab--active': tab.active }">{{ tab.label }}</span>
      </div>

      <div class="route-l3-panel__airport-signals" aria-label="Airport HMI decision signals">
        <article v-for="signal in airportDecisionSignals" :key="signal.label">
          <span>{{ signal.label }}</span>
          <strong>{{ signal.value }}</strong>
        </article>
      </div>

      <div class="route-l3-panel__airport-alert" role="status">
        <strong>Asset import is currently HOLD_BLOCKED.</strong>
        <span>Asset overlay remains readonly until critical data quality blockers are resolved.</span>
        <em>Formal write disabled.</em>
        <small>{{ airportSourceState }}</small>
      </div>

      <div class="route-l3-panel__airport-question-grid" aria-label="Field operations questions">
        <article v-for="card in airportFieldQuestionCards" :key="card.question">
          <span>{{ card.question }}</span>
          <strong>{{ card.answer }}</strong>
        </article>
      </div>

      <div class="route-l3-panel__airport-filters" aria-label="Airport HMI filters">
        <label>
          <span>Terminal</span>
          <el-select v-model="airportFilters.terminal" size="small">
            <el-option label="Terminal 3" value="Terminal 3" />
          </el-select>
        </label>
        <label>
          <span>Floor</span>
          <el-select v-model="airportFilters.floor" size="small">
            <el-option label="Ground Floor" value="Ground Floor" />
          </el-select>
        </label>
        <label>
          <span>Zone</span>
          <el-select v-model="airportFilters.zone" size="small">
            <el-option label="All zones" value="All zones" />
            <el-option v-for="row in airportZoneRows" :key="fieldValue(row, 'zone')" :value="fieldValue(row, 'zone')">{{ fieldValue(row, 'zone') }}</el-option>
          </el-select>
        </label>
        <label>
          <span>System</span>
          <el-select v-model="airportFilters.system" size="small">
            <el-option label="All systems" value="All systems" />
            <el-option v-for="row in airportSystemRows" :key="fieldValue(row, 'system')" :value="fieldValue(row, 'system')">{{ fieldValue(row, 'system') }}</el-option>
          </el-select>
        </label>
        <label>
          <span>Device Type</span>
          <el-select v-model="airportFilters.deviceType" size="small">
            <el-option label="All device types" value="All device types" />
            <el-option label="Pending customer-approved map conversion" value="Pending customer-approved map conversion" />
          </el-select>
        </label>
        <label>
          <span>Data Quality Status</span>
          <el-select v-model="airportFilters.dataQualityStatus" size="small">
            <el-option label="Pending review" value="pending_review" />
            <el-option label="Pending asset import clearance" value="pending_asset_import_clearance" />
          </el-select>
        </label>
        <label>
          <span>Import Batch</span>
          <el-select v-model="airportFilters.importBatch" size="small">
            <el-option label="Latest quality gate" value="Latest quality gate" />
          </el-select>
        </label>
      </div>

      <div class="route-l3-panel__airport-workspace">
        <div class="route-l3-panel__map-shell">
          <div class="route-l3-panel__map-head">
            <div>
              <span>Terminal 3 / Ground Floor</span>
              <strong>Registered base layer</strong>
            </div>
            <el-tag type="warning" effect="plain">Pending customer-approved map conversion</el-tag>
          </div>
          <div class="route-l3-panel__map-body">
            <strong>Map base layer registered; vector/CAD tile binding pending customer-approved map conversion.</strong>
            <span>Readonly projection</span>
          </div>
          <div class="route-l3-panel__layer-controls" aria-label="Airport HMI layer controls">
            <el-checkbox-group v-model="airportLayerSelections">
              <el-checkbox label="Zone Layer" />
              <el-checkbox label="Location Layer" />
              <el-checkbox label="Asset Layer" />
              <el-checkbox label="Point / Tag Layer" />
              <el-checkbox label="Fault Layer" />
              <el-checkbox label="Work Order Layer" />
              <el-checkbox label="Evidence Layer" />
            </el-checkbox-group>
          </div>
        </div>

        <aside class="route-l3-panel__decision-lens" aria-label="Right-side Decision Lens">
          <span>Decision Lens</span>
          <strong>Selected location / fault / work order</strong>
          <dl>
            <div>
              <dt>Selected context</dt>
              <dd>{{ fieldValue(airportSelectedContext, 'location', fieldValue(airportSelectedContext, 'event_id', fieldValue(airportSelectedContext, 'work_order_id'))) }}</dd>
            </div>
            <div>
              <dt>Operational impact</dt>
              <dd>{{ fieldValue(airportOperationalContext, 'impact', 'Readonly projection blocked by asset data quality') }}</dd>
            </div>
            <div>
              <dt>Recommended action</dt>
              <dd>{{ fieldValue(airportOperationalContext, 'recommended_action', 'Resolve critical asset import blockers before formal registry write') }}</dd>
            </div>
            <div>
              <dt>Related system</dt>
              <dd>{{ fieldValue(airportOperationalContext, 'related_system', fieldValue(airportSelectedContext, 'system')) }}</dd>
            </div>
            <div>
              <dt>Evidence required</dt>
              <dd>{{ fieldValue(airportEvidenceContext, 'status', 'pending_closure_evidence') }}</dd>
            </div>
            <div>
              <dt>Closure status</dt>
              <dd>{{ airportClosureStatus }}</dd>
            </div>
          </dl>
        </aside>
      </div>

      <div class="route-l3-panel__layer-readiness" aria-label="Layer and map readiness">
        <article v-for="layer in airportLayerReadiness" :key="layer.layer">
          <span>{{ layer.layer }}</span>
          <strong>{{ layer.state }}</strong>
          <em>{{ layer.note }}</em>
        </article>
      </div>

      <div class="route-l3-panel__mms-flow" aria-label="Work Management linkage">
        <span>Work Management / MMS Control Center</span>
        <div>
          <strong v-for="step in airportMmsFlow" :key="step">{{ step }}</strong>
        </div>
      </div>

      <div class="route-l3-panel__airport-cards" aria-label="Airport HMI main panels">
        <article v-for="panel in airportPanelCards" :key="panel.title">
          <span>{{ panel.title }}</span>
          <strong>{{ panel.value }}</strong>
          <em>{{ panel.note }}</em>
        </article>
      </div>

      <div class="route-l3-panel__airport-tables">
        <article>
          <strong>Zone Summary</strong>
          <el-table :data="airportZoneRows" size="small" stripe>
            <el-table-column prop="zone" label="Zone" min-width="90" />
            <el-table-column prop="level" label="Level" min-width="110" />
            <el-table-column prop="asset_record_count" label="Records" min-width="100" />
            <el-table-column label="Quality" min-width="160">
              <template #default="{ row }">{{ displayStatus(row.data_quality_status) }}</template>
            </el-table-column>
          </el-table>
        </article>
        <article>
          <strong>Location Summary</strong>
          <el-table :data="airportLocationRows" size="small" stripe>
            <el-table-column prop="location" label="Location" min-width="180" />
            <el-table-column prop="zone" label="Zone" min-width="120" />
            <el-table-column prop="asset_record_count" label="Records" min-width="100" />
            <el-table-column label="Binding" min-width="170">
              <template #default="{ row }">{{ displayStatus(row.map_binding_status) }}</template>
            </el-table-column>
          </el-table>
        </article>
        <article>
          <strong>System Overlay Summary</strong>
          <el-table :data="airportSystemRows" size="small" stripe>
            <el-table-column prop="system" label="System" min-width="110" />
            <el-table-column prop="asset_record_count" label="Records" min-width="100" />
            <el-table-column label="Quality" min-width="160">
              <template #default="{ row }">{{ displayStatus(row.data_quality_status) }}</template>
            </el-table-column>
          </el-table>
        </article>
        <article>
          <strong>Fault Overlay</strong>
          <el-table :data="airportFaultRows" size="small" stripe>
            <el-table-column prop="event_id" label="Event" min-width="140" />
            <el-table-column prop="severity" label="Severity" min-width="100" />
            <el-table-column prop="location" label="Location" min-width="180" />
            <el-table-column label="Quality" min-width="180">
              <template #default="{ row }">{{ displayStatus(row.data_quality_status) }}</template>
            </el-table-column>
          </el-table>
        </article>
        <article>
          <strong>Work Order Route</strong>
          <el-table :data="airportWorkOrderRows" size="small" stripe>
            <el-table-column prop="work_order_id" label="Work Order" min-width="150" />
            <el-table-column prop="priority" label="Priority" min-width="90" />
            <el-table-column prop="assigned_team" label="Team" min-width="160" />
            <el-table-column label="Route" min-width="140">
              <template #default="{ row }">{{ displayStatus(row.route_status) }}</template>
            </el-table-column>
          </el-table>
        </article>
        <article>
          <strong>Technician Navigation</strong>
          <el-table :data="airportNavigationRows" size="small" stripe>
            <el-table-column label="Route / Step" min-width="150">
              <template #default="{ row }">{{ firstField(row, ['route', 'step', 'route_step', 'navigation_step']) }}</template>
            </el-table-column>
            <el-table-column label="Zone / Space" min-width="170">
              <template #default="{ row }">{{ firstField(row, ['zone', 'space', 'location']) }}</template>
            </el-table-column>
            <el-table-column label="Asset" min-width="170">
              <template #default="{ row }">{{ firstField(row, ['asset', 'asset_name', 'asset_id']) }}</template>
            </el-table-column>
            <el-table-column label="Work Order" min-width="150">
              <template #default="{ row }">{{ firstField(row, ['work_order_id', 'workOrderId']) }}</template>
            </el-table-column>
            <el-table-column label="Navigation Instruction" min-width="240">
              <template #default="{ row }">{{ firstField(row, ['navigation_instruction', 'instruction', 'route_instruction', 'route_status']) }}</template>
            </el-table-column>
            <el-table-column label="Evidence Requirement" min-width="190">
              <template #default="{ row }">{{ displayStatus(firstField(row, ['evidence_requirement', 'evidence_required', 'evidence_status'])) }}</template>
            </el-table-column>
          </el-table>
        </article>
        <article>
          <strong>Evidence Readiness</strong>
          <el-table :data="airportEvidenceRows" size="small" stripe>
            <el-table-column prop="evidence_id" label="Evidence" min-width="170" />
            <el-table-column prop="evidence_type" label="Type" min-width="130" />
            <el-table-column label="Status" min-width="170">
              <template #default="{ row }">{{ displayStatus(row.status) }}</template>
            </el-table-column>
            <el-table-column prop="audit_ready" label="Audit Ready" min-width="120" />
          </el-table>
        </article>
        <article>
          <strong>Work Order Evidence</strong>
          <el-table :data="airportWorkOrderEvidenceRows" size="small" stripe>
            <el-table-column label="Work Order" min-width="150">
              <template #default="{ row }">{{ firstField(row, ['work_order_id', 'workOrderId']) }}</template>
            </el-table-column>
            <el-table-column label="Evidence" min-width="170">
              <template #default="{ row }">{{ firstField(row, ['evidence_id', 'evidence_ref', 'ucde_evidence']) }}</template>
            </el-table-column>
            <el-table-column label="Requirement" min-width="190">
              <template #default="{ row }">{{ displayStatus(firstField(row, ['evidence_requirement', 'status'])) }}</template>
            </el-table-column>
          </el-table>
        </article>
        <article>
          <strong>Closure Readiness</strong>
          <el-table :data="airportClosureGateRows" size="small" stripe>
            <el-table-column prop="gate" label="Gate" min-width="180" />
            <el-table-column label="Status" min-width="130">
              <template #default="{ row }">{{ displayStatus(row.status) }}</template>
            </el-table-column>
            <el-table-column prop="reason" label="Reason" min-width="260" />
          </el-table>
        </article>
      </div>

      <div class="route-l3-panel__evidence-export" aria-label="Evidence closure and export center">
        <article v-for="panel in airportEvidencePanels" :key="panel.label">
          <span>{{ panel.label }}</span>
          <strong>{{ panel.value }}</strong>
          <em>{{ panel.detail }}</em>
        </article>
      </div>
    </div>

    <div v-else-if="dashboardWorkbench" class="route-l3-panel__dashboard-workbench">
      <div class="route-l3-panel__dashboard-tabs" aria-label="Dashboard L3 workspace tabs">
        <span v-for="tab in dashboardTabs" :key="tab.key" :class="{ 'route-l3-panel__dashboard-tab--active': tab.active }">{{ tab.label }}</span>
      </div>

      <div class="route-l3-panel__action-bar" aria-label="Dashboard primary action bar">
        <el-button v-for="action in dashboardWorkbench.actions" :key="action" type="primary" plain>{{ action }}</el-button>
      </div>

      <div v-if="connectedWorkspaces.length" class="route-l3-panel__connected-workspaces" aria-label="Connected Workspaces">
        <span>Connected Workspaces</span>
        <div>
          <strong v-for="workspace in connectedWorkspaces" :key="workspace">{{ workspace }}</strong>
        </div>
      </div>

      <div class="route-l3-panel__dashboard-main">
        <div class="route-l3-panel__dashboard-command">
          <span>Dashboard Command View</span>
          <strong>{{ dashboardWorkbench.persona }}</strong>
          <p>{{ dashboardWorkbench.commandFocus }}</p>
        </div>

        <div class="route-l3-panel__dashboard-signals">
          <article>
            <span>{{ dashboardWorkbench.signalLabel }}</span>
            <strong>{{ dashboardWorkbench.signalValue }}</strong>
          </article>
          <article>
            <span>{{ dashboardWorkbench.riskLabel }}</span>
            <strong>{{ dashboardWorkbench.riskValue }}</strong>
          </article>
          <article>
            <span>{{ dashboardWorkbench.evidenceLabel }}</span>
            <strong>{{ dashboardWorkbench.evidenceValue }}</strong>
          </article>
        </div>
      </div>

      <div class="route-l3-panel__signal-grid">
        <article v-for="card in dashboardWorkbench.signalCards" :key="card.label" :class="`route-l3-panel__signal--${card.severity}`">
          <span>{{ card.icon }}</span>
          <strong>{{ card.value }}</strong>
          <em>{{ card.label }}</em>
          <p>{{ card.note }}</p>
        </article>
      </div>

      <div class="route-l3-panel__visual-context">
        <div class="route-l3-panel__primary-board" :class="`route-l3-panel__primary-board--${dashboardWorkbench.visualType}`">
          <div class="route-l3-panel__board-head">
            <span>Primary Visual</span>
            <strong>{{ dashboardWorkbench.visualType }}</strong>
          </div>

          <div class="route-l3-panel__dashboard-cards">
            <article
              v-for="card in dashboardWorkbench.focusCards"
              :key="card.title"
              :class="`route-l3-panel__dashboard-card--${card.tone}`"
            >
              <span>{{ card.title }}</span>
              <strong>{{ card.value }}</strong>
              <em>{{ card.detail }}</em>
            </article>
          </div>

          <div class="route-l3-panel__dashboard-heatmap">
            <strong>Risk / Readiness Map</strong>
            <article v-for="cell in dashboardWorkbench.heatmap" :key="cell.label" :class="`route-l3-panel__heat--${cell.tone}`">
              <span>{{ cell.label }}</span>
              <i :style="{ width: `${cell.value}%` }"></i>
              <em>{{ cell.value }}%</em>
            </article>
          </div>
        </div>

        <div class="route-l3-panel__context-panel">
          <div class="route-l3-panel__board-head">
            <span>Context Panel</span>
            <strong>IBMS inheritance and operating object chain</strong>
          </div>
          <article v-for="row in dashboardWorkbench.contextRows" :key="`${row.label}-${row.value}`">
            <span>{{ row.label }}</span>
            <strong>{{ row.value }}</strong>
            <em>{{ row.note }}</em>
          </article>
        </div>
      </div>

      <div class="route-l3-panel__six-d-model">
        <article v-for="panel in dashboardWorkbench.productionPanels" :key="panel.dimension">
          <span>{{ panel.dimension }}</span>
          <strong>{{ panel.signal }}</strong>
          <p>{{ panel.detail }}</p>
          <em>{{ panel.owner }}</em>
        </article>
      </div>

      <div class="route-l3-panel__workflow-path">
        <article v-for="lane in dashboardWorkbench.lanes" :key="lane.dimension">
          <span>{{ lane.dimension }}</span>
          <strong>{{ lane.title }}</strong>
          <p>{{ lane.detail }}</p>
          <em>{{ lane.state }}</em>
        </article>
      </div>

      <div class="route-l3-panel__readiness">
        <article v-for="layer in dashboardWorkbench.readinessLayers" :key="layer.layer">
          <span>{{ layer.layer }}</span>
          <strong>{{ layer.health }}</strong>
          <p>{{ layer.risk }} / {{ layer.dataState }}</p>
          <em>{{ layer.owner }} / {{ layer.nextAction }}</em>
          <small>{{ layer.evidence }} / {{ layer.governanceNote }}</small>
        </article>
      </div>

      <div class="route-l3-panel__acceptance-footer">
        <article v-for="row in dashboardWorkbench.acceptanceFooter" :key="row.label">
          <span>{{ row.label }}</span>
          <strong>{{ row.value }}</strong>
        </article>
      </div>
    </div>

    <div v-else class="route-l3-panel__visual" :class="`route-l3-panel__visual--${visualMode}`">
      <div v-if="visualMode === 'trend'" class="route-l3-panel__chart">
        <div class="route-l3-panel__chart-head">
          <strong>Operational Trend</strong>
          <span>Operating signal over the review window</span>
        </div>
        <svg viewBox="0 0 300 130" role="img" aria-label="L3 trend chart">
          <line x1="18" y1="116" x2="286" y2="116" />
          <line x1="18" y1="18" x2="18" y2="116" />
          <polyline :points="chartPolyline" />
          <circle v-for="(point, index) in chartPoints" :key="index" :cx="18 + index * 52" :cy="116 - point" r="4" />
        </svg>
        <div class="route-l3-panel__bars">
          <div v-for="row in barRows" :key="row.label">
            <span>{{ row.label }}</span>
            <i :style="{ width: `${row.value}%` }"></i>
            <em>{{ row.value }}%</em>
          </div>
        </div>
      </div>

      <div v-else-if="visualMode === 'topology' || visualMode === 'hmi'" class="route-l3-panel__topology">
        <div class="route-l3-panel__canvas">
          <svg viewBox="0 0 100 86" role="img" aria-label="L3 topology graph">
            <path d="M16 40 L39 20 L66 45 L43 72 L81 73" />
            <path d="M39 20 L43 72" />
            <g v-for="node in topologyNodes" :key="node.label" :class="`node-${node.tone}`">
              <circle :cx="node.x" :cy="node.y" r="6" />
            </g>
          </svg>
          <div
            v-for="node in topologyNodes"
            :key="node.label"
            class="route-l3-panel__node-label"
            :style="{ left: `${node.x}%`, top: `${node.y}%` }"
          >
            {{ node.label }}
          </div>
        </div>
        <div class="route-l3-panel__flow">
          <strong>{{ visualMode === 'hmi' ? 'HMI Read-only Flow' : 'Operational Link Map' }}</strong>
          <span v-for="row in content.rows" :key="row.item">{{ row.item }}</span>
        </div>
      </div>

      <div v-else-if="visualMode === 'workQueue'" class="route-l3-panel__queue">
        <article v-for="column in queueColumns" :key="column.label">
          <span>{{ column.label }}</span>
          <strong>{{ column.count }}</strong>
          <em>{{ column.risk }}</em>
        </article>
      </div>

      <div v-else-if="visualMode === 'timeline' || visualMode === 'evidence'" class="route-l3-panel__timeline">
        <article v-for="item in timelineItems" :key="item.label">
          <span>{{ item.label }}</span>
          <strong>{{ item.value }}%</strong>
        </article>
      </div>

      <div v-else-if="visualMode === 'security'" class="route-l3-panel__matrix">
        <article v-for="row in matrixRows" :key="row.label">
          <span>{{ row.label }}</span>
          <strong>{{ row.state }}</strong>
          <i :style="{ width: `${row.value}%` }"></i>
        </article>
      </div>

      <div v-else class="route-l3-panel__report-pack">
        <article v-for="row in content.rows" :key="row.item">
          <span>{{ row.status }}</span>
          <strong>{{ row.item }}</strong>
          <em>{{ row.focus }}</em>
        </article>
      </div>
    </div>

    <el-table v-if="!isAirportHmiMap && dashboardWorkbench" :data="content.rows" stripe border class="route-l3-panel__table">
      <el-table-column prop="item" label="Action" min-width="240" />
      <el-table-column prop="owner" label="Owner" min-width="180" />
      <el-table-column prop="status" label="Status" min-width="130" />
      <el-table-column prop="priority" label="Priority" min-width="130" />
      <el-table-column prop="open" label="Open" min-width="220" />
    </el-table>

    <el-table v-else-if="!isAirportHmiMap" :data="content.rows" stripe border class="route-l3-panel__table">
      <el-table-column prop="item" label="Action" min-width="240" />
      <el-table-column prop="focus" label="Focus Area" min-width="280" />
      <el-table-column prop="status" label="Status" min-width="140" />
    </el-table>
  </section>
</template>

<style scoped>
.route-l3-panel {
  margin-bottom: 18px;
  padding: 18px;
  border: 1px solid #d8e6e1;
  border-radius: 12px;
  background: #ffffff;
  box-shadow: 0 14px 32px rgba(15, 23, 42, 0.08);
}

.route-l3-panel__head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
}

.route-l3-panel__kicker {
  display: block;
  margin-bottom: 6px;
  color: #0f766e;
  font-size: 12px;
  font-weight: 800;
  text-transform: uppercase;
}

.route-l3-panel h2 {
  margin: 0;
  color: #10201d;
  font-size: 22px;
}

.route-l3-panel p {
  margin: 8px 0 0;
  max-width: 860px;
  color: #52615d;
  line-height: 1.55;
}

.route-l3-panel__metrics {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 16px;
}

.route-l3-panel__metric {
  min-width: 0;
  padding: 14px;
  border: 1px solid #e2ece8;
  border-radius: 10px;
  background: #f8fbfa;
}

.route-l3-panel__metric span,
.route-l3-panel__metric em {
  display: block;
  color: #64748b;
  font-size: 12px;
  font-style: normal;
}

.route-l3-panel__metric strong {
  display: block;
  margin: 6px 0;
  color: #0f766e;
  font-size: 18px;
}

.route-l3-panel__visual {
  margin-bottom: 16px;
  padding: 16px;
  border: 1px solid #dfe9e5;
  border-radius: 12px;
  background: #f8fbfa;
}

.route-l3-panel__decision-strip {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 10px;
  margin-bottom: 16px;
}

.route-l3-panel__decision-strip article,
.route-l3-panel__signal-grid article,
.route-l3-panel__context-panel article,
.route-l3-panel__six-d-model article,
.route-l3-panel__workflow-path article,
.route-l3-panel__readiness article,
.route-l3-panel__acceptance-footer article {
  min-width: 0;
  border: 1px solid #dfe9e5;
  border-radius: 10px;
  background: #ffffff;
}

.route-l3-panel__decision-strip article {
  display: grid;
  gap: 6px;
  min-height: 96px;
  padding: 12px;
}

.route-l3-panel__decision-strip span,
.route-l3-panel__signal-grid span,
.route-l3-panel__context-panel span,
.route-l3-panel__six-d-model span,
.route-l3-panel__workflow-path span,
.route-l3-panel__readiness span,
.route-l3-panel__acceptance-footer span {
  color: #64748b;
  font-size: 11px;
  font-weight: 800;
  text-transform: uppercase;
}

.route-l3-panel__decision-strip strong {
  color: #10201d;
  font-size: 13px;
  line-height: 1.35;
}

.route-l3-panel__dashboard-workbench {
  display: grid;
  gap: 16px;
  margin-bottom: 16px;
  padding: 16px;
  border: 1px solid #dfe9e5;
  border-radius: 12px;
  background: linear-gradient(180deg, #f8fbfa 0%, #ffffff 100%);
}

.route-l3-panel__dashboard-tabs,
.route-l3-panel__action-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.route-l3-panel__dashboard-tabs span {
  padding: 7px 10px;
  border: 1px solid #cfe0dc;
  border-radius: 999px;
  background: #ffffff;
  color: #0f766e;
  font-size: 12px;
  font-weight: 800;
}

.route-l3-panel__dashboard-tabs .route-l3-panel__dashboard-tab--active {
  border-color: #0f766e;
  background: #e8f5f1;
  color: #10201d;
}

.route-l3-panel__action-bar {
  padding: 10px;
  border: 1px solid #dfe9e5;
  border-radius: 12px;
  background: #ffffff;
}

.route-l3-panel__connected-workspaces {
  display: grid;
  gap: 10px;
  padding: 12px;
  border: 1px solid #dfe9e5;
  border-radius: 12px;
  background: #ffffff;
}

.route-l3-panel__connected-workspaces > span {
  color: #64748b;
  font-size: 11px;
  font-weight: 800;
  text-transform: uppercase;
}

.route-l3-panel__connected-workspaces > div {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.route-l3-panel__connected-workspaces strong {
  padding: 8px 10px;
  border: 1px solid #cfe0dc;
  border-radius: 10px;
  background: #f8fbfa;
  color: #10201d;
  font-size: 12px;
}

.route-l3-panel__dashboard-main {
  display: grid;
  grid-template-columns: minmax(260px, 1fr) minmax(320px, 0.9fr);
  gap: 14px;
}

.route-l3-panel__dashboard-command,
.route-l3-panel__dashboard-signals article,
.route-l3-panel__six-d article,
.route-l3-panel__dashboard-cards article,
.route-l3-panel__dashboard-heatmap {
  border: 1px solid #dfe9e5;
  border-radius: 12px;
  background: #ffffff;
  box-shadow: 0 10px 22px rgba(15, 23, 42, 0.06);
}

.route-l3-panel__dashboard-command {
  padding: 16px;
}

.route-l3-panel__dashboard-command span,
.route-l3-panel__dashboard-signals span,
.route-l3-panel__six-d span,
.route-l3-panel__dashboard-cards span,
.route-l3-panel__dashboard-heatmap span {
  color: #64748b;
  font-size: 12px;
  font-weight: 800;
  text-transform: uppercase;
}

.route-l3-panel__dashboard-command strong {
  display: block;
  margin-top: 8px;
  color: #10201d;
  font-size: 24px;
}

.route-l3-panel__dashboard-command p,
.route-l3-panel__six-d p {
  margin: 8px 0 0;
  color: #52615d;
  line-height: 1.5;
}

.route-l3-panel__dashboard-signals {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.route-l3-panel__dashboard-signals article,
.route-l3-panel__dashboard-cards article {
  display: grid;
  gap: 8px;
  min-width: 0;
  padding: 14px;
}

.route-l3-panel__dashboard-signals strong {
  color: #0f766e;
  font-size: 28px;
}

.route-l3-panel__signal-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
}

.route-l3-panel__signal-grid article {
  display: grid;
  gap: 6px;
  padding: 12px;
}

.route-l3-panel__signal-grid strong {
  color: #10201d;
  font-size: 24px;
}

.route-l3-panel__signal-grid em,
.route-l3-panel__context-panel em,
.route-l3-panel__six-d-model em,
.route-l3-panel__workflow-path em,
.route-l3-panel__readiness em,
.route-l3-panel__acceptance-footer strong {
  color: #52615d;
  font-size: 12px;
  font-style: normal;
  line-height: 1.4;
}

.route-l3-panel__signal-grid p,
.route-l3-panel__context-panel p,
.route-l3-panel__six-d-model p,
.route-l3-panel__workflow-path p,
.route-l3-panel__readiness p {
  margin: 0;
  color: #52615d;
  font-size: 12px;
  line-height: 1.45;
}

.route-l3-panel__signal--good {
  border-color: #b9e2d7;
}

.route-l3-panel__signal--watch {
  border-color: #f6d88f;
}

.route-l3-panel__signal--risk {
  border-color: #fecaca;
}

.route-l3-panel__visual-context {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(320px, 0.8fr);
  gap: 14px;
}

.route-l3-panel__primary-board,
.route-l3-panel__context-panel {
  display: grid;
  gap: 12px;
  padding: 14px;
  border: 1px solid #dfe9e5;
  border-radius: 12px;
  background: #ffffff;
  box-shadow: 0 10px 22px rgba(15, 23, 42, 0.06);
}

.route-l3-panel__board-head {
  display: grid;
  gap: 5px;
}

.route-l3-panel__board-head span {
  color: #0f766e;
  font-size: 12px;
  font-weight: 800;
  text-transform: uppercase;
}

.route-l3-panel__board-head strong {
  color: #10201d;
  font-size: 18px;
}

.route-l3-panel__context-panel article {
  display: grid;
  gap: 5px;
  padding: 10px;
}

.route-l3-panel__context-panel strong {
  color: #10201d;
  font-size: 14px;
}

.route-l3-panel__six-d-model,
.route-l3-panel__workflow-path {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 10px;
}

.route-l3-panel__six-d-model article,
.route-l3-panel__workflow-path article {
  position: relative;
  min-height: 184px;
  padding: 14px;
  overflow: hidden;
}

.route-l3-panel__six-d-model article::before,
.route-l3-panel__workflow-path article::before {
  content: '';
  position: absolute;
  inset: 0 auto 0 0;
  width: 4px;
  background: #0f766e;
}

.route-l3-panel__six-d-model strong,
.route-l3-panel__workflow-path strong {
  display: block;
  margin-top: 8px;
  color: #10201d;
  font-size: 15px;
}

.route-l3-panel__six-d-model em,
.route-l3-panel__workflow-path em {
  position: absolute;
  left: 14px;
  bottom: 12px;
  color: #0f766e;
  font-size: 12px;
  font-style: normal;
  font-weight: 800;
}

.route-l3-panel__readiness {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  gap: 10px;
}

.route-l3-panel__readiness article {
  display: grid;
  gap: 6px;
  min-height: 210px;
  padding: 12px;
}

.route-l3-panel__readiness strong {
  color: #0f766e;
  font-size: 22px;
}

.route-l3-panel__readiness small {
  color: #64748b;
  font-size: 11px;
  line-height: 1.35;
}

.route-l3-panel__acceptance-footer {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
}

.route-l3-panel__acceptance-footer article {
  display: grid;
  gap: 6px;
  min-height: 82px;
  padding: 10px;
}

.route-l3-panel__dashboard-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(260px, 0.72fr);
  gap: 14px;
}

.route-l3-panel__dashboard-cards {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.route-l3-panel__dashboard-cards strong {
  color: #10201d;
  font-size: 26px;
}

.route-l3-panel__dashboard-cards em {
  color: #52615d;
  font-size: 12px;
  font-style: normal;
  line-height: 1.4;
}

.route-l3-panel__dashboard-card--good {
  border-color: #b9e2d7;
}

.route-l3-panel__dashboard-card--watch {
  border-color: #f6d88f;
}

.route-l3-panel__dashboard-card--risk {
  border-color: #fecaca;
}

.route-l3-panel__dashboard-heatmap {
  display: grid;
  gap: 10px;
  padding: 14px;
}

.route-l3-panel__dashboard-heatmap > strong {
  color: #10201d;
}

.route-l3-panel__dashboard-heatmap article {
  display: grid;
  grid-template-columns: 86px 1fr 44px;
  align-items: center;
  gap: 10px;
}

.route-l3-panel__dashboard-heatmap i {
  display: block;
  height: 10px;
  border-radius: 999px;
}

.route-l3-panel__dashboard-heatmap em {
  color: #52615d;
  font-size: 12px;
  font-style: normal;
  text-align: right;
}

.route-l3-panel__heat--good i {
  background: #0f766e;
}

.route-l3-panel__heat--watch i {
  background: #d97706;
}

.route-l3-panel__heat--risk i {
  background: #dc2626;
}

.route-l3-panel__chart {
  display: grid;
  grid-template-columns: minmax(280px, 1.1fr) minmax(240px, 0.9fr);
  gap: 16px;
}

.route-l3-panel__chart-head {
  grid-column: 1 / -1;
  display: flex;
  justify-content: space-between;
  gap: 12px;
  color: #334155;
}

.route-l3-panel__chart svg {
  width: 100%;
  min-height: 180px;
}

.route-l3-panel__chart line {
  stroke: #cbd5e1;
  stroke-width: 1;
}

.route-l3-panel__chart polyline {
  fill: none;
  stroke: #0f766e;
  stroke-width: 4;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.route-l3-panel__chart circle {
  fill: #2563eb;
  stroke: #ffffff;
  stroke-width: 2;
}

.route-l3-panel__bars {
  display: grid;
  gap: 12px;
  align-content: center;
}

.route-l3-panel__bars div {
  display: grid;
  grid-template-columns: 82px 1fr 42px;
  align-items: center;
  gap: 10px;
  color: #475569;
  font-size: 12px;
}

.route-l3-panel__bars i,
.route-l3-panel__matrix i {
  display: block;
  height: 10px;
  border-radius: 999px;
  background: linear-gradient(90deg, #0f766e, #2563eb);
}

.route-l3-panel__topology {
  display: grid;
  grid-template-columns: minmax(320px, 1fr) minmax(240px, 0.75fr);
  gap: 16px;
}

.route-l3-panel__canvas {
  position: relative;
  min-height: 260px;
  border: 1px solid #d6e2de;
  border-radius: 12px;
  background: #ffffff;
  overflow: hidden;
}

.route-l3-panel__canvas svg {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}

.route-l3-panel__canvas path {
  fill: none;
  stroke: #94a3b8;
  stroke-width: 1.4;
  stroke-dasharray: 4 4;
}

.route-l3-panel__canvas circle {
  fill: #0f766e;
  stroke: #ffffff;
  stroke-width: 2;
}

.route-l3-panel__canvas .node-workspace circle {
  fill: #2563eb;
}

.route-l3-panel__canvas .node-section circle {
  fill: #b45309;
}

.route-l3-panel__canvas .node-evidence circle {
  fill: #7c3aed;
}

.route-l3-panel__node-label {
  position: absolute;
  transform: translate(-50%, 12px);
  max-width: 120px;
  padding: 6px 8px;
  border-radius: 8px;
  background: #ffffff;
  box-shadow: 0 8px 20px rgba(15, 23, 42, 0.1);
  color: #334155;
  font-size: 12px;
  font-weight: 700;
  text-align: center;
}

.route-l3-panel__flow,
.route-l3-panel__report-pack {
  display: grid;
  gap: 10px;
}

.route-l3-panel__flow span,
.route-l3-panel__report-pack article,
.route-l3-panel__queue article,
.route-l3-panel__timeline article,
.route-l3-panel__matrix article {
  padding: 12px;
  border: 1px solid #dfe9e5;
  border-radius: 10px;
  background: #ffffff;
}

.route-l3-panel__queue {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.route-l3-panel__queue article,
.route-l3-panel__timeline article,
.route-l3-panel__matrix article,
.route-l3-panel__report-pack article {
  display: grid;
  gap: 6px;
}

.route-l3-panel__queue span,
.route-l3-panel__timeline span,
.route-l3-panel__matrix span,
.route-l3-panel__report-pack span {
  color: #64748b;
  font-size: 12px;
  font-weight: 700;
}

.route-l3-panel__queue strong,
.route-l3-panel__timeline strong,
.route-l3-panel__matrix strong,
.route-l3-panel__report-pack strong {
  color: #10201d;
  font-size: 20px;
}

.route-l3-panel__queue em,
.route-l3-panel__report-pack em {
  color: #52615d;
  font-size: 12px;
  font-style: normal;
}

.route-l3-panel__timeline {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 10px;
}

.route-l3-panel__timeline article {
  position: relative;
  min-height: 96px;
}

.route-l3-panel__timeline article::before {
  content: '';
  display: block;
  width: 12px;
  height: 12px;
  margin-bottom: 10px;
  border-radius: 50%;
  background: #0f766e;
}

.route-l3-panel__matrix {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.route-l3-panel__report-pack {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.route-l3-panel__airport-hmi {
  display: grid;
  gap: 16px;
  margin-bottom: 16px;
}

.route-l3-panel__airport-production-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14px;
  padding: 16px;
  border: 1px solid #cfe4dd;
  border-radius: 10px;
  background: #f8fbfa;
}

.route-l3-panel__airport-production-head div {
  display: grid;
  gap: 6px;
}

.route-l3-panel__airport-production-head span,
.route-l3-panel__mms-flow > span {
  color: #0f766e;
  font-size: 11px;
  font-weight: 800;
  text-transform: uppercase;
}

.route-l3-panel__airport-production-head strong {
  color: #10201d;
  font-size: 24px;
  line-height: 1.2;
}

.route-l3-panel__airport-production-head p {
  max-width: 820px;
  margin: 0;
  color: #52615d;
  font-size: 13px;
  line-height: 1.45;
}

.route-l3-panel__airport-signals,
.route-l3-panel__airport-cards,
.route-l3-panel__airport-question-grid,
.route-l3-panel__layer-readiness,
.route-l3-panel__evidence-export {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.route-l3-panel__airport-signals article,
.route-l3-panel__airport-cards article,
.route-l3-panel__airport-question-grid article,
.route-l3-panel__layer-readiness article,
.route-l3-panel__evidence-export article,
.route-l3-panel__decision-lens,
.route-l3-panel__airport-tables article,
.route-l3-panel__map-shell,
.route-l3-panel__mms-flow {
  min-width: 0;
  border: 1px solid #dfe9e5;
  border-radius: 10px;
  background: #ffffff;
}

.route-l3-panel__airport-signals article,
.route-l3-panel__airport-cards article,
.route-l3-panel__airport-question-grid article,
.route-l3-panel__layer-readiness article,
.route-l3-panel__evidence-export article {
  display: grid;
  gap: 6px;
  padding: 12px;
}

.route-l3-panel__airport-signals span,
.route-l3-panel__airport-cards span,
.route-l3-panel__airport-question-grid span,
.route-l3-panel__layer-readiness span,
.route-l3-panel__evidence-export span,
.route-l3-panel__decision-lens > span,
.route-l3-panel__map-head span,
.route-l3-panel__airport-filters span {
  color: #64748b;
  font-size: 11px;
  font-weight: 800;
  text-transform: uppercase;
}

.route-l3-panel__airport-signals strong,
.route-l3-panel__airport-cards strong,
.route-l3-panel__airport-question-grid strong,
.route-l3-panel__layer-readiness strong,
.route-l3-panel__evidence-export strong {
  color: #10201d;
  font-size: 18px;
  line-height: 1.3;
  overflow-wrap: anywhere;
}

.route-l3-panel__airport-cards strong {
  color: #0f766e;
  font-size: 24px;
}

.route-l3-panel__airport-cards em,
.route-l3-panel__layer-readiness em,
.route-l3-panel__evidence-export em {
  color: #52615d;
  font-size: 12px;
  font-style: normal;
  line-height: 1.4;
}

.route-l3-panel__airport-alert {
  display: grid;
  gap: 6px;
  padding: 14px;
  border: 1px solid #f6d88f;
  border-radius: 10px;
  background: #fffbeb;
  color: #713f12;
}

.route-l3-panel__airport-alert strong,
.route-l3-panel__airport-alert span,
.route-l3-panel__airport-alert em,
.route-l3-panel__airport-alert small {
  line-height: 1.4;
}

.route-l3-panel__airport-alert em {
  font-style: normal;
  font-weight: 800;
}

.route-l3-panel__airport-alert small {
  color: #8a5a17;
}

.route-l3-panel__mms-flow {
  display: grid;
  gap: 10px;
  padding: 14px;
  background: #f8fbfa;
}

.route-l3-panel__mms-flow div {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.route-l3-panel__mms-flow strong {
  position: relative;
  padding: 8px 12px;
  border: 1px solid #cfe4dd;
  border-radius: 999px;
  background: #ffffff;
  color: #10201d;
  font-size: 12px;
}

.route-l3-panel__mms-flow strong:not(:last-child)::after {
  content: '->';
  margin-left: 10px;
  color: #0f766e;
}

.route-l3-panel__airport-filters {
  display: grid;
  grid-template-columns: repeat(7, minmax(120px, 1fr));
  gap: 10px;
  padding: 12px;
  border: 1px solid #dfe9e5;
  border-radius: 10px;
  background: #f8fbfa;
}

.route-l3-panel__airport-filters label {
  display: grid;
  gap: 6px;
  min-width: 0;
}

.route-l3-panel__airport-workspace {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(300px, 0.36fr);
  gap: 14px;
}

.route-l3-panel__map-shell {
  display: grid;
  gap: 14px;
  padding: 14px;
  background:
    linear-gradient(90deg, rgba(15, 118, 110, 0.08) 1px, transparent 1px),
    linear-gradient(180deg, rgba(15, 118, 110, 0.08) 1px, transparent 1px),
    #ffffff;
  background-size: 32px 32px;
}

.route-l3-panel__map-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.route-l3-panel__map-head div {
  display: grid;
  gap: 6px;
}

.route-l3-panel__map-head strong {
  color: #10201d;
  font-size: 20px;
}

.route-l3-panel__map-body {
  display: grid;
  place-items: center;
  min-height: 260px;
  padding: 24px;
  border: 1px dashed #9ccac1;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.78);
  text-align: center;
}

.route-l3-panel__map-body strong {
  max-width: 680px;
  color: #10201d;
  font-size: 18px;
  line-height: 1.45;
}

.route-l3-panel__map-body span {
  margin-top: 8px;
  color: #0f766e;
  font-size: 12px;
  font-weight: 800;
  text-transform: uppercase;
}

.route-l3-panel__layer-controls {
  padding: 10px;
  border: 1px solid #dfe9e5;
  border-radius: 10px;
  background: #ffffff;
}

.route-l3-panel__layer-controls :deep(.el-checkbox-group) {
  display: flex;
  flex-wrap: wrap;
  gap: 4px 14px;
}

.route-l3-panel__decision-lens {
  display: grid;
  align-content: start;
  gap: 10px;
  padding: 14px;
}

.route-l3-panel__decision-lens > strong {
  color: #10201d;
  font-size: 18px;
}

.route-l3-panel__decision-lens dl {
  display: grid;
  gap: 10px;
  margin: 0;
}

.route-l3-panel__decision-lens div {
  display: grid;
  gap: 4px;
  padding: 10px;
  border: 1px solid #e2ece8;
  border-radius: 8px;
  background: #f8fbfa;
}

.route-l3-panel__decision-lens dt {
  color: #64748b;
  font-size: 11px;
  font-weight: 800;
  text-transform: uppercase;
}

.route-l3-panel__decision-lens dd {
  margin: 0;
  color: #10201d;
  font-size: 13px;
  line-height: 1.4;
  overflow-wrap: anywhere;
}

.route-l3-panel__airport-tables {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.route-l3-panel__airport-tables article {
  display: grid;
  gap: 10px;
  padding: 12px;
  overflow: hidden;
}

.route-l3-panel__airport-tables article > strong {
  color: #10201d;
  font-size: 15px;
}

@media (max-width: 1100px) {
  .route-l3-panel__head {
    flex-direction: column;
  }

  .route-l3-panel__metrics,
  .route-l3-panel__decision-strip,
  .route-l3-panel__queue,
  .route-l3-panel__timeline,
  .route-l3-panel__matrix,
  .route-l3-panel__report-pack,
  .route-l3-panel__dashboard-main,
  .route-l3-panel__dashboard-grid,
  .route-l3-panel__signal-grid,
  .route-l3-panel__visual-context,
  .route-l3-panel__acceptance-footer,
  .route-l3-panel__airport-signals,
  .route-l3-panel__airport-cards,
  .route-l3-panel__airport-question-grid,
  .route-l3-panel__layer-readiness,
  .route-l3-panel__evidence-export,
  .route-l3-panel__airport-tables {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .route-l3-panel__airport-production-head {
    flex-direction: column;
  }

  .route-l3-panel__airport-filters {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .route-l3-panel__airport-workspace {
    grid-template-columns: 1fr;
  }

  .route-l3-panel__six-d-model,
  .route-l3-panel__workflow-path,
  .route-l3-panel__readiness {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .route-l3-panel__chart,
  .route-l3-panel__topology {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 720px) {
  .route-l3-panel__metrics,
  .route-l3-panel__decision-strip,
  .route-l3-panel__queue,
  .route-l3-panel__timeline,
  .route-l3-panel__matrix,
  .route-l3-panel__report-pack,
  .route-l3-panel__dashboard-main,
  .route-l3-panel__dashboard-signals,
  .route-l3-panel__signal-grid,
  .route-l3-panel__six-d-model,
  .route-l3-panel__workflow-path,
  .route-l3-panel__readiness,
  .route-l3-panel__dashboard-grid,
  .route-l3-panel__dashboard-cards,
  .route-l3-panel__visual-context,
  .route-l3-panel__acceptance-footer,
  .route-l3-panel__airport-signals,
  .route-l3-panel__airport-cards,
  .route-l3-panel__airport-question-grid,
  .route-l3-panel__layer-readiness,
  .route-l3-panel__evidence-export,
  .route-l3-panel__airport-filters,
  .route-l3-panel__airport-tables {
    grid-template-columns: 1fr;
  }
}
</style>
