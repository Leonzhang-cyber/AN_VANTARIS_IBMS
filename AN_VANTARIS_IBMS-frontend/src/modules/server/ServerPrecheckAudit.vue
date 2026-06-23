<template>
  <main class="server-precheck">
    <section class="hero">
      <div>
        <p class="eyebrow">VANTARIS ONE</p>
        <h1>Server Precheck</h1>
        <p class="subtitle">
          Dual-server read-only environment audit for APP/Web stack planning on 192.168.60.21 and DB-only planning on 192.168.60.22.
        </p>
      </div>
      <div class="hero-badges">
        <span>Read-only Mode</span>
        <span>Planning-only</span>
        <span>Server Precheck</span>
      </div>
    </section>

    <section class="cards">
      <article v-for="card in summaryCards" :key="card.label" class="metric-card">
        <span>{{ card.label }}</span>
        <strong>{{ card.value }}</strong>
      </article>
    </section>

    <section class="plan-grid">
      <article>
        <div class="section-head">
          <div>
            <p class="eyebrow">APP/DB dual-server plan</p>
            <h2>APP server {{ summary.appServerIp }}</h2>
          </div>
          <span>{{ appServer.status || 'planning-only' }}</span>
        </div>
        <ul>
          <li v-for="role in appRoles" :key="role">{{ role }}</li>
        </ul>
      </article>
      <article>
        <div class="section-head">
          <div>
            <p class="eyebrow">DB-only server</p>
            <h2>DB server {{ summary.dbServerIp }}</h2>
          </div>
          <span>{{ dbServer.status || 'planning-only' }}</span>
        </div>
        <ul>
          <li v-for="role in dbRoles" :key="role">{{ role }}</li>
        </ul>
      </article>
    </section>

    <section class="plan-grid">
      <article>
        <div class="section-head">
          <div>
            <p class="eyebrow">APP server readiness panel</p>
            <h2>Runtime planning only</h2>
          </div>
        </div>
        <dl>
          <div><dt>OS</dt><dd>{{ appServer.osRequirement }}</dd></div>
          <div><dt>CPU/RAM/Disk</dt><dd>{{ appServer.cpuRamDiskRecommendation }}</dd></div>
          <div><dt>Ports</dt><dd>{{ appPorts.join(', ') }}</dd></div>
          <div><dt>TLS</dt><dd>{{ appServer.sslTlsPlanning }}</dd></div>
        </dl>
      </article>
      <article>
        <div class="section-head">
          <div>
            <p class="eyebrow">DB server readiness panel</p>
            <h2>DB activation not executed</h2>
          </div>
        </div>
        <dl>
          <div><dt>PostgreSQL</dt><dd>{{ dbServer.postgresqlRequirement }}</dd></div>
          <div><dt>Roles</dt><dd>{{ dbServer.dbUserRolePlanning }}</dd></div>
          <div><dt>Migration</dt><dd>{{ dbServer.schemaMigrationPlanning }}</dd></div>
          <div><dt>Backup</dt><dd>{{ dbServer.backupRestorePlanning }}</dd></div>
        </dl>
      </article>
    </section>

    <section class="table-panel">
      <div class="section-head">
        <div>
          <p class="eyebrow">Precheck checklist table</p>
          <h2>Checklist evidence required before GA</h2>
        </div>
        <span>{{ checklist.length }} items</span>
      </div>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Item</th>
              <th>Category</th>
              <th>Evidence</th>
              <th>Status</th>
              <th>Owner</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in checklist" :key="item.itemId">
              <td><strong>{{ item.title }}</strong></td>
              <td>{{ item.category }}</td>
              <td>{{ item.expectedEvidence }}</td>
              <td><span class="status">{{ item.currentStatus }}</span> / {{ item.executionStatus }}</td>
              <td>{{ item.ownerRole }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <section class="table-panel">
      <div class="section-head">
        <div>
          <p class="eyebrow">Blockers table</p>
          <h2>Deployment blockers / risk boundary</h2>
        </div>
        <span>{{ blockers.length }} blockers</span>
      </div>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Blocker</th>
              <th>Severity</th>
              <th>Server</th>
              <th>Reason</th>
              <th>Required action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="blocker in blockers" :key="blocker.blockerId">
              <td><strong>{{ blocker.title }}</strong></td>
              <td><span class="status">{{ blocker.severity }}</span></td>
              <td>{{ blocker.affectedServer }}</td>
              <td>{{ blocker.reason }}</td>
              <td>{{ blocker.requiredActionBeforeGA }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <section class="lower-grid">
      <article>
        <div class="section-head">
          <div>
            <p class="eyebrow">Handoff readiness panel</p>
            <h2>{{ handoff.customerHandoffStatus }}</h2>
          </div>
        </div>
        <ul>
          <li>Server precheck: {{ handoff.serverPrecheckStatus }}</li>
          <li>Deployment: {{ handoff.deploymentStatus }}</li>
          <li>DB activation: {{ handoff.dbActivationStatus }}</li>
          <li>Next: {{ handoff.nextRecommendedStep }}</li>
          <li v-for="module in handoff.linkedModules" :key="module">{{ module }}</li>
        </ul>
      </article>
      <article>
        <div class="section-head">
          <div>
            <p class="eyebrow">Read-only guardrails panel</p>
            <h2>Precheck boundaries</h2>
          </div>
        </div>
        <ul>
          <li v-for="item in guardrails" :key="item">{{ item }}</li>
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
          <li>No SSH/server access performed.</li>
          <li>No deployment performed.</li>
          <li>No DB connection or migration executed.</li>
          <li>No runtime healthcheck executed.</li>
        </ul>
      </article>
      <article>
        <div class="section-head">
          <div>
            <p class="eyebrow">Reports / UCDE / NexusAI linkage</p>
            <h2>Customer handoff readiness</h2>
          </div>
        </div>
        <ul>
          <li>Reports: delivery evidence reference</li>
          <li>UCDE: evidence readiness reference</li>
          <li>NexusAI: branch audit readiness reference</li>
          <li>Foundation Diagnostics: engineer diagnostics reference</li>
        </ul>
      </article>
    </section>
  </main>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import {
  getServerPrecheckAppServer,
  getServerPrecheckBlockers,
  getServerPrecheckChecklist,
  getServerPrecheckDbServer,
  getServerPrecheckHandoff,
  getServerPrecheckPlan,
  getServerPrecheckSummary,
  type BlockerItem,
  type ChecklistItem,
  type HandoffReadiness,
  type ServerPlan,
  type ServerPrecheckSummary,
} from '@/services/api/serverPrecheck'

const emptySummary: ServerPrecheckSummary = {
  scope: 'SERVER_PRECHECK_R1',
  moduleId: 'server-precheck',
  readOnly: true,
  sshExecuted: false,
  deploymentExecuted: false,
  installExecuted: false,
  dbConnectionExecuted: false,
  dbMigrationExecuted: false,
  dbWriteEnabled: false,
  healthcheckRuntimeExecuted: false,
  nginxSetupExecuted: false,
  pm2SetupExecuted: false,
  systemdSetupExecuted: false,
  edgeCommandExecution: false,
  linkCommandExecution: false,
  deviceControlEnabled: false,
  productionActivation: false,
  visualStyle: 'VANTARIS_LIGHT_OPERATIONS_CONSOLE',
  appServerIp: '192.168.60.21',
  dbServerIp: '192.168.60.22',
  appServerRoleCount: 0,
  dbServerRoleCount: 0,
  checklistTotal: 0,
  blockersTotal: 0,
  readyForServerAccess: false,
  readyForDeployment: false,
  productionGaStatus: 'NOT_YET',
  pushExecuted: false,
  remoteAligned: false,
  limitations: [],
}

const summary = ref<ServerPrecheckSummary>(emptySummary)
const plan = ref<ServerPlan>({ appServer: {}, dbServer: {}, networkAssumption: [] })
const appServer = ref<Record<string, unknown>>({})
const dbServer = ref<Record<string, unknown>>({})
const checklist = ref<ChecklistItem[]>([])
const blockers = ref<BlockerItem[]>([])
const handoff = ref<HandoffReadiness>({
  customerHandoffStatus: '',
  serverPrecheckStatus: '',
  deploymentStatus: '',
  dbActivationStatus: '',
  productionGaStatus: 'NOT_YET',
  nextRecommendedStep: '',
  linkedModules: [],
})

const summaryCards = computed(() => [
  { label: 'APP Server', value: summary.value.appServerIp },
  { label: 'DB Server', value: summary.value.dbServerIp },
  { label: 'APP Roles', value: summary.value.appServerRoleCount },
  { label: 'DB Roles', value: summary.value.dbServerRoleCount },
  { label: 'Checklist', value: summary.value.checklistTotal },
  { label: 'Blockers', value: summary.value.blockersTotal },
  { label: 'Ready Deploy', value: summary.value.readyForDeployment ? 'yes' : 'no' },
  { label: 'Production GA', value: summary.value.productionGaStatus },
])

const appRoles = computed(() => Array.isArray(plan.value.appServer.roles) ? plan.value.appServer.roles.map(String) : [])
const dbRoles = computed(() => Array.isArray(plan.value.dbServer.roles) ? plan.value.dbServer.roles.map(String) : [])
const appPorts = computed(() => Array.isArray(appServer.value.portsPlanning) ? appServer.value.portsPlanning.map(String) : [])
const guardrails = [
  'No SSH',
  'No deployment',
  'No install',
  'No DB connection',
  'No DB migration',
  'No DB write',
  'No runtime healthcheck',
  'No Nginx/PM2/systemd setup',
  'No EDGE/LINK command',
  'No device control',
  'No production activation',
]

onMounted(async () => {
  const [summaryData, planData, appData, dbData, checklistData, blockerData, handoffData] = await Promise.all([
    getServerPrecheckSummary(),
    getServerPrecheckPlan(),
    getServerPrecheckAppServer(),
    getServerPrecheckDbServer(),
    getServerPrecheckChecklist(),
    getServerPrecheckBlockers(),
    getServerPrecheckHandoff(),
  ])
  summary.value = summaryData
  plan.value = planData
  appServer.value = appData
  dbServer.value = dbData
  checklist.value = checklistData
  blockers.value = blockerData
  handoff.value = handoffData
})
</script>

<style scoped>
.server-precheck {
  min-height: 100vh;
  background: #f7fbf9;
  color: #17211f;
  padding: 28px;
}

.hero,
.plan-grid > article,
.table-panel,
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
  max-width: 820px;
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
  grid-template-columns: repeat(4, minmax(0, 1fr));
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

.plan-grid,
.lower-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
  margin-top: 18px;
}

.plan-grid > article,
.table-panel,
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

dl div {
  border-bottom: 1px solid #e3ede8;
  padding: 10px 0;
}

dt {
  color: #60716c;
  font-size: 12px;
}

dd {
  font-weight: 700;
  margin: 4px 0 0;
}

.table-wrap {
  overflow-x: auto;
}

table {
  border-collapse: collapse;
  min-width: 960px;
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

ul {
  margin: 0;
  padding-left: 18px;
}

li {
  color: #4e625c;
  margin: 8px 0;
}

@media (max-width: 1200px) {
  .cards,
  .plan-grid,
  .lower-grid {
    grid-template-columns: 1fr;
  }
}
</style>

