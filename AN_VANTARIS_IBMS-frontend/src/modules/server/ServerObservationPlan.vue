<template>
  <main class="observation-plan">
    <section class="hero">
      <div>
        <p class="eyebrow">VANTARIS ONE</p>
        <h1>Server Observation Plan</h1>
        <p class="subtitle">Actual approved read-only server observation plan for 192.168.60.21 and 192.168.60.22 before any terminal execution.</p>
      </div>
      <div class="badges"><span>Read-only</span><span>Planning-only</span><span>Observation Plan</span></div>
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
        <ul><li>APP / Web / Backend / Frontend / Console</li><li>Read-only observation commands</li><li>Service status without restart</li></ul>
      </article>
      <article>
        <p class="eyebrow">DB target server cards</p>
        <h2>DB {{ summary.dbServerIp }}</h2>
        <ul><li>DB only</li><li>PostgreSQL package/status only</li><li>No DB session or mutation</li></ul>
      </article>
    </section>

    <section class="panel">
      <p class="eyebrow">Execution sequence timeline</p>
      <h2>Execution sequence</h2>
      <div class="timeline">
        <article v-for="step in sequence" :key="String(step.stepId)">
          <span>{{ step.stepId }}</span>
          <strong>{{ step.title }}</strong>
          <small>{{ step.targetServer }} | {{ step.evidenceOutput }}</small>
        </article>
      </div>
    </section>

    <section class="panel">
      <p class="eyebrow">APP server planned read-only command table</p>
      <h2>{{ targetLabel(appObservation.target) }}</h2>
      <table><thead><tr><th>Command</th><th>Purpose</th><th>Planned</th><th>Forbidden variants</th></tr></thead><tbody>
        <tr v-for="row in records(appObservation.plannedCommands)" :key="String(row.commandId)"><td>{{ row.command }}</td><td>{{ row.purpose }}</td><td>{{ row.executedInR3 === false ? 'not executed in R3' : row.executedInR3 }}</td><td>{{ list(row.forbiddenVariants).join(', ') }}</td></tr>
      </tbody></table>
    </section>

    <section class="panel">
      <p class="eyebrow">DB server planned read-only command table</p>
      <h2>{{ targetLabel(dbObservation.target) }}</h2>
      <table><thead><tr><th>Command</th><th>Purpose</th><th>DB mutation</th><th>Forbidden variants</th></tr></thead><tbody>
        <tr v-for="row in records(dbObservation.plannedCommands)" :key="String(row.commandId)"><td>{{ row.command }}</td><td>{{ row.purpose }}</td><td>{{ row.dbMutation }}</td><td>{{ list(row.forbiddenVariants).join(', ') }}</td></tr>
      </tbody></table>
    </section>

    <section class="grid">
      <article>
        <p class="eyebrow">Evidence package plan</p>
        <h2>{{ evidence.evidencePackageStatus }}</h2>
        <ul><li v-for="item in list(evidence.items)" :key="item">{{ item }}</li></ul>
      </article>
      <article>
        <p class="eyebrow">Approval checklist</p>
        <h2>Separate approval required</h2>
        <ul><li v-for="item in checklist" :key="String(item.checkId)">{{ item.title }} - {{ item.status }}</li></ul>
      </article>
    </section>

    <section class="panel">
      <p class="eyebrow">Stop / abort conditions</p>
      <h2>Stop conditions</h2>
      <table><thead><tr><th>Condition</th><th>Trigger</th><th>Action</th><th>Impact</th></tr></thead><tbody>
        <tr v-for="row in stops" :key="String(row.conditionId)"><td>{{ row.conditionId }}</td><td>{{ row.trigger }}</td><td>{{ row.requiredAction }}</td><td>{{ row.productionImpact }}</td></tr>
      </tbody></table>
    </section>

    <section class="grid">
      <article><p class="eyebrow">Read-only guardrails panel</p><h2>R3 boundaries</h2><ul><li v-for="item in guardrails" :key="item">{{ item }}</li></ul></article>
      <article><p class="eyebrow">Not Production GA note</p><h2>{{ summary.productionGaStatus }}</h2><ul><li>No SSH executed in R3 planning.</li><li>No deployment, install, DB connection, or runtime healthcheck.</li><li>Actual observation requires explicit separate approval.</li></ul></article>
    </section>
  </main>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { getAppServerObservation, getApprovalChecklist, getDbServerObservation, getExecutionSequence, getObservationEvidencePackage, getObservationGuardrails, getObservationStopConditions, getServerObservationSummary, listRecords, listStrings, type ServerObservationSummary } from '@/services/api/serverObservationPlan'

const summary = ref<ServerObservationSummary>({ appServerIp: '192.168.60.21', dbServerIp: '192.168.60.22', observationStatus: 'PLANNING_ONLY', executionSequenceCount: 0, appObservationCommandCount: 0, dbObservationCommandCount: 0, evidencePackageItemCount: 0, stopConditionCount: 0, approvalChecklistCount: 0, readyForActualSSH: false, readyForDeployment: false, productionGaStatus: 'NOT_YET' })
const sequence = ref<Record<string, unknown>[]>([])
const appObservation = ref<Record<string, unknown>>({})
const dbObservation = ref<Record<string, unknown>>({})
const evidence = ref<Record<string, unknown>>({})
const stops = ref<Record<string, unknown>[]>([])
const checklist = ref<Record<string, unknown>[]>([])
const guardrails = ref<string[]>([])

const cards = computed(() => [
  { label: 'Observation', value: summary.value.observationStatus },
  { label: 'APP Commands', value: summary.value.appObservationCommandCount },
  { label: 'DB Commands', value: summary.value.dbObservationCommandCount },
  { label: 'Sequence', value: summary.value.executionSequenceCount },
  { label: 'Evidence Items', value: summary.value.evidencePackageItemCount },
  { label: 'Stop Conditions', value: summary.value.stopConditionCount },
  { label: 'Approvals', value: summary.value.approvalChecklistCount },
  { label: 'Production GA', value: summary.value.productionGaStatus },
])

function list(value: unknown): string[] {
  return listStrings(value)
}

function records(value: unknown): Record<string, unknown>[] {
  return listRecords(value)
}

function targetLabel(value: unknown): string {
  const target = typeof value === 'object' && value !== null ? (value as Record<string, unknown>) : {}
  return `${String(target.role ?? 'target')} ${String(target.ip ?? '')}`
}

onMounted(async () => {
  const [s, seq, app, db, ev, stopRows, checks, rails] = await Promise.all([getServerObservationSummary(), getExecutionSequence(), getAppServerObservation(), getDbServerObservation(), getObservationEvidencePackage(), getObservationStopConditions(), getApprovalChecklist(), getObservationGuardrails()])
  summary.value = s
  sequence.value = seq
  appObservation.value = app
  dbObservation.value = db
  evidence.value = ev
  stops.value = stopRows
  checklist.value = checks
  guardrails.value = rails
})
</script>

<style scoped>
.observation-plan{min-height:100vh;background:#f7fbf9;color:#17211f;padding:28px}.hero,.panel,.grid>article,.cards>article,.timeline>article{background:#fff;border:1px solid #dce9e3;border-radius:8px;box-shadow:0 12px 28px rgba(24,57,48,.08)}.hero{display:flex;justify-content:space-between;gap:24px;padding:28px}.eyebrow{color:#247668;font-size:12px;font-weight:800;letter-spacing:0;margin:0 0 8px;text-transform:uppercase}h1,h2,h3,p{margin-top:0}h1{font-size:34px;margin-bottom:10px}h2{font-size:18px}.subtitle{color:#596a65;max-width:840px;margin-bottom:0}.badges{display:flex;flex-wrap:wrap;gap:8px}.badges span{background:#e8f5f0;border:1px solid #c8e4d8;border-radius:999px;color:#176255;font-size:12px;font-weight:700;padding:6px 10px}.cards-wrap{margin:18px 0}.cards{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px}.cards article,.panel,.grid>article,.timeline article{padding:18px}.cards span,.timeline span{color:#66736f;display:block;font-size:12px;margin-bottom:8px}.cards strong{font-size:22px}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px;margin-top:18px}.panel{margin-top:18px;overflow-x:auto}.timeline{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}.timeline strong,.timeline small{display:block}table{border-collapse:collapse;min-width:900px;width:100%}th,td{border-bottom:1px solid #e3ede8;padding:12px;text-align:left}th{color:#60716c;font-size:12px;text-transform:uppercase}ul{margin:0;padding-left:18px}li{color:#4e625c;margin:8px 0}@media(max-width:1200px){.cards,.grid,.timeline{grid-template-columns:1fr}}
</style>
