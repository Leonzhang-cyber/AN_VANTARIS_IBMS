<template>
  <main class="nexus-audit">
    <RouteL3ContentPanel />

    <section class="hero">
      <div>
        <p class="eyebrow">VANTARIS ONE</p>
        <h1>NexusAI Branch Audit</h1>
        <p class="subtitle">
          Read-only branch diff audit for Reports GA-R13, Asset Context GA-R1, and CODE GA-R1 customer preview readiness.
        </p>
      </div>
      <div class="hero-badges">
        <span>Read-only Mode</span>
        <span>Branch Audit</span>
        <span>Customer Preview</span>
      </div>
    </section>

    <section class="cards">
      <article v-for="card in summaryCards" :key="card.label" class="metric-card">
        <span>{{ card.label }}</span>
        <strong>{{ card.value }}</strong>
      </article>
    </section>

    <section class="timeline-panel">
      <div class="section-head">
        <div>
          <p class="eyebrow">Branch diff timeline</p>
          <h2>{{ summary.branch }}</h2>
        </div>
        <span>remote aligned: {{ summary.remoteAligned ? 'yes' : 'no' }}</span>
      </div>
      <div class="timeline">
        <article v-for="commit in commits" :key="commit.commitHash">
          <strong>{{ commit.shortHash }} / {{ commit.title }}</strong>
          <span>{{ commit.remoteStatus }} / {{ commit.changeType }}</span>
          <p>{{ commit.customerDemoImpact }}</p>
          <small>{{ commit.validationMarker }}</small>
        </article>
      </div>
    </section>

    <section class="workspace">
      <article>
        <div class="section-head">
          <div>
            <p class="eyebrow">Module readiness impact matrix</p>
            <h2>Readiness by module</h2>
          </div>
          <span>{{ modules.length }} modules</span>
        </div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Module</th>
                <th>Before</th>
                <th>After</th>
                <th>Linkage</th>
                <th>Guardrail</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="module in modules" :key="module.moduleId">
                <td><strong>{{ module.moduleName }}</strong></td>
                <td>{{ module.readinessBefore }}</td>
                <td>{{ module.readinessAfter }}</td>
                <td>{{ module.linkageAdded }}</td>
                <td><span class="status">{{ module.productionGaStatus }}</span> {{ module.guardrails }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </article>
    </section>

    <section class="workspace">
      <article>
        <div class="section-head">
          <div>
            <p class="eyebrow">Risk boundary table</p>
            <h2>Open read-only risks</h2>
          </div>
          <span>{{ risks.length }} risks</span>
        </div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Risk</th>
                <th>Severity</th>
                <th>Affected</th>
                <th>Boundary</th>
                <th>Mitigation</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="risk in risks" :key="risk.riskId">
                <td><strong>{{ risk.title }}</strong><small>{{ risk.productionImpact }}</small></td>
                <td><span class="status">{{ risk.severity }}</span></td>
                <td>{{ risk.affectedModules.join(', ') }}</td>
                <td>{{ risk.boundary }}</td>
                <td>{{ risk.mitigation }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </article>
    </section>

    <section class="lower-grid">
      <article>
        <div class="section-head">
          <div>
            <p class="eyebrow">Evidence / Reports linkage panel</p>
            <h2>{{ evidence.auditMode }}</h2>
          </div>
        </div>
        <h3>Validation markers</h3>
        <ul>
          <li v-for="marker in evidence.validationMarkers" :key="marker">{{ marker }}</li>
        </ul>
        <h3>Registry references</h3>
        <ul>
          <li v-for="ref in evidence.registryReferences" :key="ref">{{ ref }}</li>
        </ul>
      </article>

      <article>
        <div class="section-head">
          <div>
            <p class="eyebrow">Customer demo impact panel</p>
            <h2>{{ summary.customerDemoReadinessImpact }}</h2>
          </div>
        </div>
        <h3>Positive impact</h3>
        <ul>
          <li v-for="item in customerImpact.positiveImpact" :key="item">{{ item }}</li>
        </ul>
        <h3>Remaining gaps</h3>
        <ul>
          <li v-for="item in customerImpact.remainingGaps" :key="item">{{ item }}</li>
        </ul>
      </article>

      <article>
        <div class="section-head">
          <div>
            <p class="eyebrow">Read-only guardrails panel</p>
            <h2>NexusAI R3 boundaries</h2>
          </div>
        </div>
        <ul>
          <li>No AI runtime</li>
          <li>No model API call</li>
          <li>No auto-fix</li>
          <li>No code mutation</li>
          <li>No DB write</li>
          <li>No deployment</li>
          <li>No EDGE/LINK command</li>
          <li>No device control</li>
          <li>No production activation</li>
        </ul>
      </article>

      <article>
        <div class="section-head">
          <div>
            <p class="eyebrow">Not Production GA note</p>
            <h2>{{ summary.productionGaStatus }}</h2>
          </div>
        </div>
        <ul>
          <li>NEXUS AI runtime not active.</li>
          <li>Server precheck not done.</li>
          <li>Real DB and deployment not done.</li>
          <li v-for="item in customerImpact.recommendation" :key="item">{{ item }}</li>
        </ul>
      </article>
    </section>
  </main>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import RouteL3ContentPanel from '@/components/RouteL3ContentPanel.vue'
import {
  getNexusBranchCommits,
  getNexusBranchModules,
  getNexusBranchRisks,
  getNexusBranchSummary,
  getNexusCustomerDemoImpact,
  getNexusEvidenceLinkage,
  type NexusBranchSummary,
  type NexusCommitItem,
  type NexusCustomerDemoImpact,
  type NexusEvidenceLinkage,
  type NexusModuleItem,
  type NexusRiskItem,
} from '@/services/api/nexusAi'

const emptySummary: NexusBranchSummary = {
  scope: 'NEXUSAI_GA_R3',
  moduleId: 'nexus-ai-branch-audit',
  readOnly: true,
  aiRuntimeEnabled: false,
  modelApiCallEnabled: false,
  autoFixEnabled: false,
  codeMutationEnabled: false,
  workflowExecutionEnabled: false,
  dbWriteEnabled: false,
  edgeCommandExecution: false,
  linkCommandExecution: false,
  deviceControlEnabled: false,
  productionActivation: false,
  visualStyle: 'VANTARIS_LIGHT_OPERATIONS_CONSOLE',
  branch: '',
  baselineRemoteHead: '',
  currentLocalHead: '',
  localCommitCountSinceRemote: 0,
  auditedCommits: 0,
  auditedModules: 0,
  riskCount: 0,
  customerDemoReadinessImpact: '',
  productionGaStatus: 'NOT_YET',
  remoteAligned: false,
  pushExecuted: false,
  deploymentExecuted: false,
  limitations: [],
}

const summary = ref<NexusBranchSummary>(emptySummary)
const commits = ref<NexusCommitItem[]>([])
const modules = ref<NexusModuleItem[]>([])
const risks = ref<NexusRiskItem[]>([])
const evidence = ref<NexusEvidenceLinkage>({ auditMode: 'read-only-branch-diff-preview', ucdeEvidenceReferences: [], reportsReferences: [], registryReferences: [], validationMarkers: [], localFreezeTags: [] })
const customerImpact = ref<NexusCustomerDemoImpact>({ positiveImpact: [], remainingGaps: [], recommendation: [] })

const summaryCards = computed(() => [
  { label: 'Audited Commits', value: summary.value.auditedCommits },
  { label: 'Audited Modules', value: summary.value.auditedModules },
  { label: 'Risk Count', value: summary.value.riskCount },
  { label: 'Local Commits', value: summary.value.localCommitCountSinceRemote },
  { label: 'Remote Aligned', value: summary.value.remoteAligned ? 'yes' : 'no' },
  { label: 'Production GA', value: summary.value.productionGaStatus },
])

onMounted(async () => {
  const [summaryData, commitData, moduleData, riskData, evidenceData, impactData] = await Promise.all([
    getNexusBranchSummary(),
    getNexusBranchCommits(),
    getNexusBranchModules(),
    getNexusBranchRisks(),
    getNexusEvidenceLinkage(),
    getNexusCustomerDemoImpact(),
  ])
  summary.value = summaryData
  commits.value = commitData
  modules.value = moduleData
  risks.value = riskData
  evidence.value = evidenceData
  customerImpact.value = impactData
})
</script>

<style scoped>
.nexus-audit {
  min-height: 100vh;
  background: #f7fbf9;
  color: #17211f;
  padding: 28px;
}

.hero,
.timeline-panel,
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

h3 {
  color: #31433e;
  font-size: 14px;
  margin: 16px 0 8px;
}

.subtitle {
  color: #596a65;
  max-width: 760px;
  margin-bottom: 0;
}

.hero-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.hero-badges span,
.status {
  background: #e8f5f0;
  border: 1px solid #c8e4d8;
  border-radius: 999px;
  color: #176255;
  font-size: 12px;
  font-weight: 700;
  padding: 6px 10px;
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
  font-size: 22px;
}

.timeline-panel,
.workspace > article,
.lower-grid > article {
  padding: 18px;
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

.timeline {
  display: grid;
  gap: 12px;
}

.timeline article {
  background: #f8fcfa;
  border: 1px solid #dce9e3;
  border-radius: 8px;
  padding: 14px;
}

.timeline span,
.timeline small {
  color: #60716c;
  display: block;
  font-size: 12px;
  margin-top: 6px;
}

.workspace,
.lower-grid {
  display: grid;
  gap: 18px;
  margin-top: 18px;
}

.lower-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.table-wrap {
  overflow-x: auto;
}

table {
  border-collapse: collapse;
  min-width: 980px;
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

  .lower-grid {
    grid-template-columns: 1fr;
  }
}
</style>
