<template>
  <main class="code-policy">
    <RouteL3ContentPanel />

    <section class="hero">
      <div>
        <p class="eyebrow">VANTARIS ONE</p>
        <h1>CODE Policy Gate</h1>
        <p class="subtitle">
          Read-only execution boundary preview for future UHMI / UMMS / Asset Context control intent paths.
        </p>
      </div>
      <div class="hero-badges">
        <span>Read-only Mode</span>
        <span>Customer Preview</span>
        <span>Skeleton Runtime</span>
      </div>
    </section>

    <section class="cards">
      <article v-for="card in summaryCards" :key="card.label" class="metric-card">
        <span>{{ card.label }}</span>
        <strong>{{ card.value }}</strong>
      </article>
    </section>

    <section class="path-panel">
      <div class="section-head">
        <div>
          <p class="eyebrow">Required control path visualization</p>
          <h2>UHMI / UMMS / Asset Context to CODE Policy Gate</h2>
        </div>
        <span>{{ controlPath.graphMode }}</span>
      </div>
      <div class="path">
        <template v-for="(node, index) in controlNodes" :key="node">
          <span>{{ node }}</span>
          <b v-if="index < controlNodes.length - 1">→</b>
        </template>
      </div>
    </section>

    <section class="workspace">
      <article class="table-panel">
        <div class="section-head">
          <div>
            <p class="eyebrow">Policy gate table</p>
            <h2>Preview-only gates</h2>
          </div>
          <span>{{ gates.length }} gates</span>
        </div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Gate</th>
                <th>Source</th>
                <th>Protected action</th>
                <th>Decision mode</th>
                <th>States</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="gate in gates" :key="gate.gateId">
                <td>
                  <strong>{{ gate.gateName }}</strong>
                  <small>{{ gate.purpose }}</small>
                </td>
                <td>{{ gate.sourceModule }}</td>
                <td>{{ gate.protectedActionType }}</td>
                <td><span class="status">{{ gate.decisionMode }}</span></td>
                <td>{{ gate.allowedDecisionStates.join(', ') }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </article>

      <article class="timeline-panel">
        <div class="section-head">
          <div>
            <p class="eyebrow">Approval boundary timeline</p>
            <h2>Approval remains non-executable</h2>
          </div>
        </div>
        <ol class="timeline">
          <li v-for="stage in approvalStages" :key="String(stage.stageId)">
            <strong>{{ stage.stageName }}</strong>
            <span>{{ stage.stageState }}</span>
          </li>
        </ol>
      </article>
    </section>

    <section class="lower-grid">
      <article>
        <div class="section-head">
          <div>
            <p class="eyebrow">Evidence linkage matrix</p>
            <h2>Audit / UCDE Evidence preview</h2>
          </div>
          <span>{{ evidence.evidenceMode }}</span>
        </div>
        <ul>
          <li v-for="link in evidence.links" :key="String(link.source) + String(link.target)">
            {{ link.source }} → {{ link.target }} / {{ link.relationship }}
          </li>
        </ul>
      </article>

      <article>
        <div class="section-head">
          <div>
            <p class="eyebrow">Blocked direct paths panel</p>
            <h2>Direct execution edges absent</h2>
          </div>
          <span>{{ execution.executionBoundaryStatus }}</span>
        </div>
        <ul>
          <li v-for="path in execution.directPathsBlocked" :key="path">{{ path }}</li>
        </ul>
      </article>

      <article>
        <div class="section-head">
          <div>
            <p class="eyebrow">Read-only guardrails panel</p>
            <h2>Execution boundary controls</h2>
          </div>
        </div>
        <ul>
          <li v-for="item in summary.guardrails" :key="item">{{ item }}</li>
        </ul>
      </article>

      <article>
        <div class="section-head">
          <div>
            <p class="eyebrow">Not Production GA note</p>
            <h2>Preview-only boundary explanation</h2>
          </div>
        </div>
        <ul>
          <li>Approval execution is disabled.</li>
          <li>Policy mutation is disabled.</li>
          <li>Workflow execution is disabled.</li>
          <li>EDGE / LINK command execution is disabled.</li>
          <li>Device control is disabled.</li>
          <li v-for="item in summary.limitations" :key="item">{{ item }}</li>
        </ul>
      </article>
    </section>
  </main>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import RouteL3ContentPanel from '@/components/RouteL3ContentPanel.vue'
import {
  getCodePolicyApprovalBoundary,
  getCodePolicyControlPath,
  getCodePolicyEvidenceLinkage,
  getCodePolicyExecutionBoundary,
  getCodePolicyGates,
  getCodePolicySummary,
  type CodePolicyApprovalBoundary,
  type CodePolicyControlPath,
  type CodePolicyEvidenceLinkage,
  type CodePolicyExecutionBoundary,
  type CodePolicyGateItem,
  type CodePolicySummary,
} from '@/services/api/codePolicy'

const emptySummary: CodePolicySummary = {
  scope: 'CODE_GA_R1',
  moduleId: 'code-policy',
  readOnly: true,
  runtimeEnabled: false,
  approvalExecutionEnabled: false,
  policyMutationEnabled: false,
  workflowExecutionEnabled: false,
  commandExecutionEnabled: false,
  dbWriteEnabled: false,
  edgeCommandExecution: false,
  linkCommandExecution: false,
  deviceControlEnabled: false,
  productionActivation: false,
  visualStyle: 'VANTARIS_LIGHT_OPERATIONS_CONSOLE',
  policyGateCount: 0,
  controlPathStageCount: 0,
  blockedDirectPathCount: 0,
  evidenceLinkCount: 0,
  approvalBoundaryCount: 0,
  executionBoundaryStatus: 'preview-only-not-executable',
  integrationStatus: 'available',
  limitations: [],
  guardrails: [],
}

const summary = ref<CodePolicySummary>(emptySummary)
const gates = ref<CodePolicyGateItem[]>([])
const controlPath = ref<CodePolicyControlPath>({ graphMode: 'local-readonly-code-policy-projection', nodes: [], edges: [], directToDeviceEdgesAbsent: true })
const approval = ref<CodePolicyApprovalBoundary>({ approvalStages: [], approvalExecutionEnabled: false })
const execution = ref<CodePolicyExecutionBoundary>({ directPathsBlocked: [], requiredPath: '', r1Status: {}, executionBoundaryStatus: 'preview-only-not-executable' })
const evidence = ref<CodePolicyEvidenceLinkage>({ sourceObjectTypes: [], evidenceMode: 'read-only-preview', evidenceWriteEnabled: false, hashOnlyLocalPreview: true, links: [] })

const summaryCards = computed(() => [
  { label: 'Policy Gates', value: summary.value.policyGateCount },
  { label: 'Control Path Stages', value: summary.value.controlPathStageCount },
  { label: 'Blocked Direct Paths', value: summary.value.blockedDirectPathCount },
  { label: 'Evidence Links', value: summary.value.evidenceLinkCount },
  { label: 'Approval Boundary', value: summary.value.approvalBoundaryCount },
  { label: 'Runtime Enabled', value: summary.value.runtimeEnabled ? 'yes' : 'no' },
])

const controlNodes = computed(() => controlPath.value.nodes.map((node) => String(node.label || node.nodeId || 'Node')))
const approvalStages = computed(() => approval.value.approvalStages)

onMounted(async () => {
  const [summaryData, gatesData, pathData, approvalData, executionData, evidenceData] = await Promise.all([
    getCodePolicySummary(),
    getCodePolicyGates(),
    getCodePolicyControlPath(),
    getCodePolicyApprovalBoundary(),
    getCodePolicyExecutionBoundary(),
    getCodePolicyEvidenceLinkage(),
  ])
  summary.value = summaryData
  gates.value = gatesData
  controlPath.value = pathData
  approval.value = approvalData
  execution.value = executionData
  evidence.value = evidenceData
})
</script>

<style scoped>
.code-policy {
  min-height: 100vh;
  background: #f7fbf9;
  color: #17211f;
  padding: 28px;
}

.hero,
.path-panel,
.workspace > article,
.lower-grid > article {
  background: #ffffff;
  border: 1px solid #dce9e3;
  border-radius: 8px;
  box-shadow: 0 12px 28px rgba(24, 57, 48, 0.08);
}

.hero {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  padding: 28px;
}

.eyebrow {
  color: #247668;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0;
  margin: 0 0 8px;
  text-transform: uppercase;
}

h1,
h2,
h3,
p {
  margin-top: 0;
}

h1 {
  font-size: 34px;
  margin-bottom: 10px;
}

h2 {
  font-size: 18px;
  margin-bottom: 0;
}

.subtitle {
  color: #596a65;
  max-width: 760px;
  margin-bottom: 0;
}

.hero-badges,
.path {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.hero-badges span,
.path span,
.status {
  background: #e8f5f0;
  border: 1px solid #c8e4d8;
  border-radius: 999px;
  color: #176255;
  font-size: 12px;
  font-weight: 700;
  padding: 6px 10px;
}

.path b {
  color: #6d7d78;
  padding: 6px 0;
}

.cards {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 14px;
  margin: 18px 0;
}

.metric-card {
  background: #ffffff;
  border: 1px solid #dce9e3;
  border-radius: 8px;
  padding: 18px;
}

.metric-card span {
  color: #66736f;
  display: block;
  font-size: 12px;
  margin-bottom: 8px;
}

.metric-card strong {
  font-size: 24px;
}

.path-panel,
.workspace > article,
.lower-grid > article {
  padding: 18px;
}

.workspace,
.lower-grid {
  display: grid;
  gap: 18px;
  margin-top: 18px;
}

.workspace {
  grid-template-columns: minmax(0, 1.45fr) minmax(320px, 0.75fr);
}

.lower-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.section-head {
  align-items: flex-start;
  display: flex;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
}

.section-head > span {
  color: #247668;
  font-size: 12px;
  font-weight: 800;
}

.table-wrap {
  overflow-x: auto;
}

table {
  border-collapse: collapse;
  min-width: 920px;
  width: 100%;
}

th,
td {
  border-bottom: 1px solid #e3ede8;
  padding: 12px;
  text-align: left;
}

th {
  color: #60716c;
  font-size: 12px;
  text-transform: uppercase;
}

td small {
  color: #71827d;
  display: block;
  margin-top: 4px;
}

.timeline {
  border-left: 2px solid #c8e4d8;
  margin: 0;
  padding-left: 18px;
}

.timeline li {
  margin: 0 0 14px;
}

.timeline span {
  color: #247668;
  display: block;
  font-size: 12px;
  font-weight: 800;
  margin-top: 4px;
}

ul {
  margin: 0;
  padding-left: 18px;
}

li {
  color: #4e625c;
  margin: 8px 0;
}

@media (max-width: 1200px) {
  .cards {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .workspace,
  .lower-grid {
    grid-template-columns: 1fr;
  }
}
</style>
