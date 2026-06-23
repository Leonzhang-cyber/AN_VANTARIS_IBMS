<template>
  <main class="access-plan">
    <section class="hero">
      <div>
        <p class="eyebrow">VANTARIS ONE</p>
        <h1>Server Access Window Plan</h1>
        <p class="subtitle">Approved read-only server access window plan before any actual observation of 192.168.60.21 and 192.168.60.22.</p>
      </div>
      <div class="badges"><span>Read-only</span><span>Planning-only</span><span>Access Window Plan</span></div>
    </section>

    <section class="cards-wrap">
      <p class="eyebrow">Summary cards</p>
      <div class="cards">
      <article v-for="card in cards" :key="card.label"><span>{{ card.label }}</span><strong>{{ card.value }}</strong></article>
      </div>
    </section>

    <section class="grid">
      <article>
        <p class="eyebrow">APP/DB target server cards</p>
        <h2>APP {{ summary.appServerIp }}</h2>
        <ul><li>APP / Web / Backend / Frontend / Console</li><li>UHMI / UCDE / UMMS / Reports</li><li>Asset Context / CODE / NexusAI Preview</li></ul>
      </article>
      <article>
        <p class="eyebrow">DB-only target</p>
        <h2>DB {{ summary.dbServerIp }}</h2>
        <ul><li>PostgreSQL DB only</li><li>Backup target planning</li><li>Restore target planning</li></ul>
      </article>
    </section>

    <section class="panel">
      <p class="eyebrow">Access window plan</p>
      <h2>{{ accessWindow.proposedWindowStatus }}</h2>
      <div class="grid plain">
        <article><h3>Approvers</h3><ul><li v-for="item in list(accessWindow.requiredApprovers)" :key="item">{{ item }}</li></ul></article>
        <article><h3>Access mode</h3><ul><li v-for="item in list(accessWindow.accessMode)" :key="item">{{ item }}</li></ul></article>
        <article><h3>Session evidence</h3><ul><li v-for="item in list(accessWindow.sessionEvidence)" :key="item">{{ item }}</li></ul></article>
      </div>
    </section>

    <section class="panel">
      <p class="eyebrow">Approval boundary table</p>
      <h2>Customer / Engineer / Security Approval Boundary</h2>
      <table><thead><tr><th>Approval</th><th>Role</th><th>Purpose</th><th>Status</th></tr></thead><tbody>
        <tr v-for="row in approvals" :key="String(row.approvalId)"><td>{{ row.approvalId }}</td><td>{{ row.approverRole }}</td><td>{{ row.approvalPurpose }}</td><td><span>{{ row.status }}</span></td></tr>
      </tbody></table>
    </section>

    <section class="panel">
      <p class="eyebrow">Allowed read-only command catalog</p>
      <h2>Planned read-only commands, not executed in R2</h2>
      <table><thead><tr><th>Group</th><th>Purpose</th><th>APP commands</th><th>DB commands</th><th>Forbidden variants</th></tr></thead><tbody>
        <tr v-for="row in commands" :key="String(row.commandGroup)"><td>{{ row.commandGroup }}</td><td>{{ row.commandPurpose }}</td><td>{{ list(row.appServerAllowedCommands).join(', ') }}</td><td>{{ list(row.dbServerAllowedCommands).join(', ') }}</td><td>{{ list(row.forbiddenVariants).join(', ') }}</td></tr>
      </tbody></table>
    </section>

    <section class="grid">
      <article>
        <p class="eyebrow">Evidence capture plan</p>
        <h2>{{ evidence.evidencePlanStatus }}</h2>
        <ul><li v-for="item in list(evidence.evidenceItems)" :key="item">{{ item }}</li></ul>
      </article>
      <article>
        <p class="eyebrow">R3 readiness panel</p>
        <h2>{{ r3.r3Candidate }}</h2>
        <ul><li v-for="item in list(r3.prerequisites)" :key="item">{{ item }}</li><li v-for="item in list(r3.blockers)" :key="item">{{ item }}</li></ul>
      </article>
    </section>

    <section class="panel">
      <p class="eyebrow">Stop / abort conditions</p>
      <h2>Stop conditions</h2>
      <table><thead><tr><th>Condition</th><th>Trigger</th><th>Action</th><th>Severity</th></tr></thead><tbody>
        <tr v-for="row in stops" :key="String(row.conditionId)"><td>{{ row.title }}</td><td>{{ row.trigger }}</td><td>{{ row.requiredAction }}</td><td><span>{{ row.severity }}</span></td></tr>
      </tbody></table>
    </section>

    <section class="grid">
      <article><p class="eyebrow">Read-only guardrails panel</p><h2>R2 boundaries</h2><ul><li v-for="item in guardrails" :key="item">{{ item }}</li></ul></article>
      <article><p class="eyebrow">Not Production GA note</p><h2>{{ summary.productionGaStatus }}</h2><ul><li>No SSH in R2.</li><li>No deployment, install, DB connection, or healthcheck runtime call.</li><li>SERVER-PRECHECK-R3 remains a future candidate.</li></ul></article>
    </section>
  </main>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { getAccessWindow, getApprovalBoundary, getEvidenceCapture, getR3Readiness, getReadonlyCommands, getServerAccessSummary, getStopConditions, listStrings, type ServerAccessSummary } from '@/services/api/serverAccessPlan'

const summary = ref<ServerAccessSummary>({ appServerIp: '192.168.60.21', dbServerIp: '192.168.60.22', accessWindowStatus: 'PLANNING_ONLY', approvalsRequired: 0, allowedCommandCount: 0, forbiddenActionCount: 0, evidenceCaptureItems: 0, stopConditionCount: 0, readyForR3: false, readyForSSH: false, readyForDeployment: false, productionGaStatus: 'NOT_YET' })
const accessWindow = ref<Record<string, unknown>>({})
const approvals = ref<Record<string, unknown>[]>([])
const commands = ref<Record<string, unknown>[]>([])
const evidence = ref<Record<string, unknown>>({})
const stops = ref<Record<string, unknown>[]>([])
const r3 = ref<Record<string, unknown>>({})
const guardrails = ['No SSH in R2', 'No deployment', 'No install', 'No DB connection', 'No DB migration', 'No DB write', 'No runtime healthcheck', 'No Nginx/PM2/systemd setup', 'No EDGE/LINK command', 'No device control', 'No production activation']

const cards = computed(() => [
  { label: 'APP Server', value: summary.value.appServerIp },
  { label: 'DB Server', value: summary.value.dbServerIp },
  { label: 'Approvals', value: summary.value.approvalsRequired },
  { label: 'Commands', value: summary.value.allowedCommandCount },
  { label: 'Evidence Items', value: summary.value.evidenceCaptureItems },
  { label: 'Stop Conditions', value: summary.value.stopConditionCount },
  { label: 'Ready R3', value: summary.value.readyForR3 ? 'yes' : 'no' },
  { label: 'Production GA', value: summary.value.productionGaStatus },
])

function list(value: unknown): string[] {
  return listStrings(value)
}

onMounted(async () => {
  const [s, aw, ab, cmd, ev, sc, r] = await Promise.all([getServerAccessSummary(), getAccessWindow(), getApprovalBoundary(), getReadonlyCommands(), getEvidenceCapture(), getStopConditions(), getR3Readiness()])
  summary.value = s
  accessWindow.value = aw
  approvals.value = ab
  commands.value = cmd
  evidence.value = ev
  stops.value = sc
  r3.value = r
})
</script>

<style scoped>
.access-plan{min-height:100vh;background:#f7fbf9;color:#17211f;padding:28px}.hero,.panel,.grid>article,.cards>article{background:#fff;border:1px solid #dce9e3;border-radius:8px;box-shadow:0 12px 28px rgba(24,57,48,.08)}.hero{display:flex;justify-content:space-between;gap:24px;padding:28px}.eyebrow{color:#247668;font-size:12px;font-weight:800;letter-spacing:0;margin:0 0 8px;text-transform:uppercase}h1,h2,h3,p{margin-top:0}h1{font-size:34px;margin-bottom:10px}h2{font-size:18px}.subtitle{color:#596a65;max-width:820px;margin-bottom:0}.badges{display:flex;flex-wrap:wrap;gap:8px}.badges span,td span{background:#e8f5f0;border:1px solid #c8e4d8;border-radius:999px;color:#176255;font-size:12px;font-weight:700;padding:6px 10px}.cards-wrap{margin:18px 0}.cards{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px}.cards article,.panel,.grid>article{padding:18px}.cards span{color:#66736f;display:block;font-size:12px;margin-bottom:8px}.cards strong{font-size:22px}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px;margin-top:18px}.plain{margin-top:0}.panel{margin-top:18px;overflow-x:auto}table{border-collapse:collapse;min-width:900px;width:100%}th,td{border-bottom:1px solid #e3ede8;padding:12px;text-align:left}th{color:#60716c;font-size:12px;text-transform:uppercase}ul{margin:0;padding-left:18px}li{color:#4e625c;margin:8px 0}@media(max-width:1200px){.cards,.grid{grid-template-columns:1fr}}
</style>
