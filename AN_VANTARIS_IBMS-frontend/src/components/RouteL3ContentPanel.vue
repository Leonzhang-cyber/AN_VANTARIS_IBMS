<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { resolveL3ContentConfig, resolveL3RouteContentContext } from '@/services/menu/l3-content-registry'

type VisualMode = 'trend' | 'topology' | 'timeline' | 'workQueue' | 'evidence' | 'security' | 'hmi' | 'reportPack'

const route = useRoute()
const context = computed(() => resolveL3RouteContentContext(route.query.menu, route.query.l3))
const content = computed(() => (context.value ? resolveL3ContentConfig(context.value) : undefined))
const dashboardWorkbench = computed(() => content.value?.dashboardWorkbench)
const elvTopology = computed(() => content.value?.elvTopology)
const visualOnlyMode = computed(() => content.value?.visualOnlyMode === true)
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
</script>

<template>
  <section
    v-if="content"
    class="route-l3-panel"
    :class="{ 'route-l3-panel--visual-only': visualOnlyMode }"
    aria-label="Menu section content"
  >
    <div v-if="elvTopology" class="route-l3-panel__command-strip" aria-label="Industry connectors decision command strip">
      <div class="route-l3-panel__command-copy">
        <span class="route-l3-panel__command-breadcrumb">Integration & Partner Hub / Industry Connectors</span>
        <span class="route-l3-panel__command-kicker">INTEGRATION VISUAL WORKBENCH</span>
        <h2>{{ content.title }}</h2>
        <p>{{ elvTopology.commandSummary }}</p>
        <div class="route-l3-panel__command-chips" aria-label="Connector status chips">
          <span v-for="chip in elvTopology.statusChips" :key="chip">{{ chip }}</span>
        </div>
      </div>
      <el-button class="route-l3-panel__primary-action route-l3-panel__command-action" type="primary" plain>{{ content.primaryAction }}</el-button>
    </div>

    <div v-else class="route-l3-panel__head">
      <div>
        <span class="route-l3-panel__kicker">{{ sectionKicker }}</span>
        <h2>{{ content.title }}</h2>
        <p>{{ content.subtitle }}</p>
      </div>
      <el-button class="route-l3-panel__primary-action" type="primary" plain>{{ content.primaryAction }}</el-button>
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

    <div v-if="!elvTopology" class="route-l3-panel__metrics">
      <article v-for="metric in content.metrics" :key="metric.label" class="route-l3-panel__metric">
        <span>{{ metric.label }}</span>
        <strong>{{ metric.value }}</strong>
        <em>{{ metric.note }}</em>
      </article>
    </div>

    <div v-if="dashboardWorkbench" class="route-l3-panel__dashboard-workbench">
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

    <div v-else-if="elvTopology" class="route-l3-panel__elv-workbench">
      <div class="route-l3-panel__elv-signals" aria-label="Industry connectors signal strip">
        <article v-for="signal in elvTopology.signals" :key="signal.label" :class="`route-l3-panel__elv-status--${signal.status}`">
          <span>{{ signal.label }}</span>
          <strong>{{ signal.value }}</strong>
          <em>{{ signal.note }}</em>
        </article>
      </div>

      <div class="route-l3-panel__elv-main">
        <div class="route-l3-panel__elv-topology" aria-label="ELV Source System Topology">
          <div class="route-l3-panel__elv-topology-title">
            <span>Primary Visual</span>
            <strong>ELV Source System Topology</strong>
          </div>
          <svg viewBox="0 0 100 100" role="img" aria-label="Hub and spoke topology">
            <line
              v-for="node in elvTopology.nodes"
              :key="`line-${node.system}`"
              x1="50"
              y1="50"
              :x2="node.x"
              :y2="node.y"
            />
          </svg>
          <div class="route-l3-panel__elv-hub">
            <strong>VANTARIS ONE</strong>
            <span>Integration Hub</span>
          </div>
          <article
            v-for="node in elvTopology.nodes"
            :key="node.system"
            class="route-l3-panel__elv-node"
            :class="`route-l3-panel__elv-status--${node.health}`"
            :style="{ left: `${node.x}%`, top: `${node.y}%` }"
          >
            <div>
              <b>{{ node.badge }}</b>
              <i></i>
            </div>
            <strong>{{ node.system }}</strong>
            <span>{{ node.protocol }}</span>
            <em>{{ node.freshness }}</em>
          </article>
        </div>

        <aside class="route-l3-panel__elv-side">
          <div class="route-l3-panel__elv-legend">
            <div class="route-l3-panel__board-head">
              <span>Protocol Legend</span>
              <strong>Protocol readiness</strong>
            </div>
            <article v-for="protocol in elvTopology.protocolLegend" :key="protocol.protocol">
              <strong>{{ protocol.protocol }}</strong>
              <span>{{ protocol.status }}</span>
            </article>
          </div>

          <div class="route-l3-panel__elv-context">
            <div class="route-l3-panel__board-head">
              <span>Context Panel</span>
              <strong>Risk and ownership</strong>
            </div>
            <article v-for="row in elvTopology.context" :key="row.label">
              <span>{{ row.label }}</span>
              <strong>{{ row.value }}</strong>
              <em>{{ row.status }}</em>
            </article>
          </div>
        </aside>
      </div>

      <div class="route-l3-panel__elv-matrix" aria-label="Connector Health Matrix">
        <div class="route-l3-panel__board-head">
          <span>Connector Health Matrix</span>
          <strong>System readiness by protocol, freshness, owner, and evidence</strong>
        </div>
        <div class="route-l3-panel__elv-matrix-head">
          <span>System</span>
          <span>Protocol</span>
          <span>Health</span>
          <span>Freshness</span>
          <span>Owner</span>
          <span>Evidence</span>
        </div>
        <article v-for="node in elvTopology.nodes" :key="`matrix-${node.system}`" :class="`route-l3-panel__elv-status--${node.health}`">
          <strong>{{ node.system }}</strong>
          <span>{{ node.protocol }}</span>
          <span>{{ node.health }}</span>
          <span>{{ node.freshness }}</span>
          <span>{{ node.owner }}</span>
          <span>{{ node.evidence }}</span>
        </article>
      </div>

      <div class="route-l3-panel__elv-flow" aria-label="Industry connectors action flow">
        <article v-for="step in elvTopology.flow" :key="step">
          <strong>{{ step }}</strong>
        </article>
      </div>

      <div class="route-l3-panel__elv-acceptance">
        {{ elvTopology.acceptance }}
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

    <el-table v-if="dashboardWorkbench" :data="content.rows" stripe border class="route-l3-panel__table">
      <el-table-column prop="item" label="Action" min-width="240" />
      <el-table-column prop="owner" label="Owner" min-width="180" />
      <el-table-column prop="status" label="Status" min-width="130" />
      <el-table-column prop="priority" label="Priority" min-width="130" />
      <el-table-column prop="open" label="Open" min-width="220" />
    </el-table>

    <el-table v-else-if="!elvTopology" :data="content.rows" stripe border class="route-l3-panel__table">
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

:global(.uedge-page > .route-l3-panel--visual-only ~ *) {
  display: none !important;
}

.route-l3-panel__head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
}

.route-l3-panel__command-strip {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 16px;
  padding: 22px 26px;
  border: 1px solid #d8e6e1;
  border-radius: 14px;
  background: linear-gradient(180deg, #ffffff 0%, #f8fbfa 100%);
  box-shadow: 0 16px 34px rgba(15, 23, 42, 0.08);
}

.route-l3-panel__command-copy {
  display: grid;
  gap: 8px;
  min-width: 0;
}

.route-l3-panel__command-breadcrumb {
  color: #52615d;
  font-size: 12px;
  font-weight: 800;
}

.route-l3-panel__command-kicker {
  width: fit-content;
  padding: 5px 9px;
  border-radius: 999px;
  background: #e8f5f1;
  color: #0f766e;
  font-size: 11px;
  font-weight: 900;
  text-transform: uppercase;
}

.route-l3-panel__command-strip h2 {
  margin: 0;
  color: #10201d;
  font-size: 26px;
  line-height: 1.16;
}

.route-l3-panel__command-strip p {
  margin: 0;
  max-width: none;
  color: #334155;
  font-size: 14px;
  font-weight: 700;
  line-height: 1.35;
}

.route-l3-panel__command-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 2px;
}

.route-l3-panel__command-chips span {
  padding: 7px 10px;
  border: 1px solid #cfe0dc;
  border-radius: 999px;
  background: #ffffff;
  color: #10201d;
  font-size: 12px;
  font-weight: 800;
}

.route-l3-panel__command-action {
  flex: 0 0 auto;
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


.route-l3-panel__primary-action {
  border-color: #0f766e !important;
  background: #ecfdf5 !important;
  color: #0f766e !important;
  font-weight: 800 !important;
  box-shadow: 0 10px 24px rgba(15, 118, 110, 0.12);
}

.route-l3-panel__primary-action:hover,
.route-l3-panel__primary-action:focus {
  border-color: #0b5f59 !important;
  background: #dff8ef !important;
  color: #0b5f59 !important;
}

.route-l3-panel__primary-action.is-disabled,
.route-l3-panel__primary-action.is-disabled:hover,
.route-l3-panel__primary-action.is-disabled:focus {
  border-color: #cbd5e1 !important;
  background: #f1f5f9 !important;
  color: #64748b !important;
  opacity: 1 !important;
  box-shadow: none;
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

.route-l3-panel__elv-workbench {
  display: grid;
  gap: 16px;
  margin-bottom: 16px;
  padding: 16px;
  border: 1px solid #dfe9e5;
  border-radius: 12px;
  background: linear-gradient(180deg, #f8fbfa 0%, #ffffff 100%);
}

.route-l3-panel__elv-signals {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 10px;
}

.route-l3-panel__elv-signals article,
.route-l3-panel__elv-side > div,
.route-l3-panel__elv-matrix,
.route-l3-panel__elv-flow article,
.route-l3-panel__elv-acceptance {
  min-width: 0;
  border: 1px solid #dfe9e5;
  border-radius: 12px;
  background: #ffffff;
  box-shadow: 0 10px 22px rgba(15, 23, 42, 0.06);
}

.route-l3-panel__elv-signals article {
  display: grid;
  gap: 6px;
  min-height: 112px;
  padding: 12px;
}

.route-l3-panel__elv-signals span,
.route-l3-panel__elv-context span,
.route-l3-panel__elv-matrix-head span,
.route-l3-panel__elv-legend .route-l3-panel__board-head span,
.route-l3-panel__elv-context .route-l3-panel__board-head span,
.route-l3-panel__elv-matrix .route-l3-panel__board-head span {
  color: #64748b;
  font-size: 11px;
  font-weight: 800;
  text-transform: uppercase;
}

.route-l3-panel__elv-signals strong {
  color: #10201d;
  font-size: 24px;
}

.route-l3-panel__elv-signals em,
.route-l3-panel__elv-context em {
  color: #52615d;
  font-size: 12px;
  font-style: normal;
  line-height: 1.4;
}

.route-l3-panel__elv-status--ready {
  border-color: #b9e2d7 !important;
}

.route-l3-panel__elv-status--mapped {
  border-color: #bfdbfe !important;
}

.route-l3-panel__elv-status--watch {
  border-color: #f6d88f !important;
}

.route-l3-panel__elv-status--degraded {
  border-color: #fecaca !important;
}

.route-l3-panel__elv-main {
  display: grid;
  grid-template-columns: minmax(0, 1.35fr) minmax(300px, 0.65fr);
  gap: 14px;
}

.route-l3-panel__elv-topology {
  position: relative;
  min-height: 480px;
  border: 1px solid #d6e2de;
  border-radius: 12px;
  background:
    linear-gradient(90deg, rgba(15, 118, 110, 0.08) 1px, transparent 1px),
    linear-gradient(180deg, rgba(15, 118, 110, 0.08) 1px, transparent 1px),
    #fbfefd;
  background-size: 28px 28px;
  overflow: hidden;
}

.route-l3-panel__elv-topology svg {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}

.route-l3-panel__elv-topology line {
  stroke: #94a3b8;
  stroke-width: 1.2;
  stroke-dasharray: 4 4;
}

.route-l3-panel__elv-topology-title {
  position: absolute;
  left: 18px;
  top: 16px;
  z-index: 2;
  display: grid;
  gap: 3px;
  padding: 10px 12px;
  border: 1px solid #cfe0dc;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.92);
  box-shadow: 0 10px 22px rgba(15, 23, 42, 0.08);
}

.route-l3-panel__elv-topology-title span {
  color: #64748b;
  font-size: 10px;
  font-weight: 900;
  text-transform: uppercase;
}

.route-l3-panel__elv-topology-title strong {
  color: #10201d;
  font-size: 14px;
}

.route-l3-panel__elv-hub {
  position: absolute;
  left: 50%;
  top: 50%;
  display: grid;
  place-items: center;
  width: 178px;
  height: 96px;
  transform: translate(-50%, -50%);
  border: 2px solid #0f766e;
  border-radius: 14px;
  background: #ffffff;
  box-shadow: 0 18px 34px rgba(15, 23, 42, 0.16);
  text-align: center;
}

.route-l3-panel__elv-hub strong {
  color: #10201d;
  font-size: 16px;
}

.route-l3-panel__elv-hub span {
  color: #0f766e;
  font-size: 12px;
  font-weight: 800;
}

.route-l3-panel__elv-node {
  position: absolute;
  display: grid;
  gap: 5px;
  width: 138px;
  padding: 10px;
  transform: translate(-50%, -50%);
  border: 1px solid #dfe9e5;
  border-radius: 12px;
  background: #ffffff;
  box-shadow: 0 12px 24px rgba(15, 23, 42, 0.12);
}

.route-l3-panel__elv-node div {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.route-l3-panel__elv-node b {
  padding: 4px 6px;
  border-radius: 6px;
  background: #10201d;
  color: #ffffff;
  font-size: 10px;
}

.route-l3-panel__elv-node i {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #0f766e;
}

.route-l3-panel__elv-status--watch .route-l3-panel__elv-node i,
.route-l3-panel__elv-node.route-l3-panel__elv-status--watch i {
  background: #d97706;
}

.route-l3-panel__elv-status--degraded .route-l3-panel__elv-node i,
.route-l3-panel__elv-node.route-l3-panel__elv-status--degraded i {
  background: #dc2626;
}

.route-l3-panel__elv-node strong {
  color: #10201d;
  font-size: 13px;
}

.route-l3-panel__elv-node span,
.route-l3-panel__elv-node em {
  width: fit-content;
  padding: 4px 6px;
  border-radius: 999px;
  background: #eef6f4;
  color: #52615d;
  font-size: 11px;
  font-style: normal;
}

.route-l3-panel__elv-side {
  display: grid;
  gap: 14px;
}

.route-l3-panel__elv-legend,
.route-l3-panel__elv-context,
.route-l3-panel__elv-matrix {
  display: grid;
  gap: 10px;
  padding: 14px;
}

.route-l3-panel__elv-legend article,
.route-l3-panel__elv-context article {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 8px;
  align-items: center;
  padding: 9px;
  border: 1px solid #e2ece8;
  border-radius: 10px;
  background: #f8fbfa;
}

.route-l3-panel__elv-context article {
  grid-template-columns: 1fr;
}

.route-l3-panel__elv-legend strong,
.route-l3-panel__elv-context strong,
.route-l3-panel__elv-matrix strong {
  color: #10201d;
  font-size: 13px;
}

.route-l3-panel__elv-legend article > span {
  padding: 4px 7px;
  border-radius: 999px;
  background: #e8f5f1;
  color: #0f766e;
  font-size: 11px;
  font-weight: 800;
}

.route-l3-panel__elv-matrix-head,
.route-l3-panel__elv-matrix article {
  display: grid;
  grid-template-columns: 1fr 0.85fr 0.75fr 0.75fr 1.2fr 0.8fr;
  gap: 10px;
  align-items: center;
}

.route-l3-panel__elv-matrix article {
  padding: 10px;
  border: 1px solid #e2ece8;
  border-radius: 10px;
  background: #f8fbfa;
}

.route-l3-panel__elv-matrix article span {
  color: #52615d;
  font-size: 12px;
}

.route-l3-panel__elv-flow {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 10px;
}

.route-l3-panel__elv-flow article {
  position: relative;
  min-height: 72px;
  padding: 12px;
}

.route-l3-panel__elv-flow article:not(:last-child)::after {
  content: '>';
  position: absolute;
  right: -10px;
  top: 50%;
  transform: translateY(-50%);
  color: #0f766e;
  font-weight: 900;
}

.route-l3-panel__elv-flow strong {
  color: #10201d;
  font-size: 13px;
}

.route-l3-panel__elv-acceptance {
  padding: 14px;
  color: #10201d;
  font-weight: 800;
  line-height: 1.5;
}

@media (max-width: 1100px) {
  .route-l3-panel__head {
    flex-direction: column;
  }

  .route-l3-panel__command-strip {
    align-items: flex-start;
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
  .route-l3-panel__elv-signals,
  .route-l3-panel__elv-main,
  .route-l3-panel__elv-flow {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .route-l3-panel__six-d-model,
  .route-l3-panel__workflow-path,
  .route-l3-panel__readiness {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .route-l3-panel__chart,
  .route-l3-panel__topology,
  .route-l3-panel__elv-matrix-head,
  .route-l3-panel__elv-matrix article {
    grid-template-columns: 1fr;
  }

  .route-l3-panel__elv-flow article::after {
    display: none;
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
  .route-l3-panel__elv-signals,
  .route-l3-panel__elv-main,
  .route-l3-panel__elv-flow {
    grid-template-columns: 1fr;
  }
}
</style>
