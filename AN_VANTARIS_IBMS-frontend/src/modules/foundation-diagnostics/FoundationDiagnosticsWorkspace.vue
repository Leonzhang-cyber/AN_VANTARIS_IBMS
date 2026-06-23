<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { getFoundationDiagnosticsWorkspace, type FoundationDiagnosticsWorkspace } from '@/services/api/foundationDiagnostics'

const tabs = ['Overview', 'Server Plan', 'Package Readiness', 'EDGE', 'LINK', 'DB Foundation', 'Contracts', 'Healthcheck Preview', 'Package Integrity', 'Rollback Readiness', 'Guardrails']
const activeTab = ref('Overview')
const loading = ref(false)
const error = ref('')
const workspace = ref<FoundationDiagnosticsWorkspace | null>(null)

const badges = computed(() => workspace.value ? ['Engineer Diagnostics', 'Read-only Mode', workspace.value.visualStyle] : [])

async function loadWorkspace() {
  loading.value = true
  error.value = ''
  try {
    workspace.value = await getFoundationDiagnosticsWorkspace()
  } catch {
    error.value = 'Foundation Diagnostics Workspace data unavailable.'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  void loadWorkspace()
})
</script>

<template>
  <section class="foundation-page" v-loading="loading">
    <header class="workspace-head">
      <div>
        <p class="eyebrow">UConsole / Engineer Workspace</p>
        <h1>Foundation Diagnostics Workspace</h1>
        <p class="summary">Engineer Diagnostics read-only preview for EDGE / LINK / DB / Contracts readiness, server planning, offline verification, and rollback readiness.</p>
      </div>
      <div class="badge-stack">
        <el-tag v-for="badge in badges" :key="badge" round>{{ badge }}</el-tag>
      </div>
    </header>

    <el-alert v-if="error" class="section-gap" type="warning" show-icon :closable="false" :title="error" />

    <template v-if="workspace">
      <section class="target-strip section-gap">
        <strong>APP / non-DB target: {{ workspace.appNonDbTarget }}</strong>
        <strong>DB-only target: {{ workspace.dbOnlyTarget }}</strong>
        <span>{{ workspace.futureExecutionPath }}</span>
      </section>

      <section class="card-grid section-gap">
        <article v-for="card in workspace.overviewCards" :key="card.label" class="metric-card">
          <span>{{ card.label }}</span>
          <strong>{{ card.value }}</strong>
          <em>{{ card.status }}</em>
        </article>
      </section>

      <el-tabs v-model="activeTab" type="card" class="workspace-tabs section-gap">
        <el-tab-pane v-for="tab in tabs" :key="tab" :label="tab" :name="tab">
          <template v-if="tab === 'Overview'">
            <div class="section-title">Offline Package Readiness</div>
            <el-descriptions :column="3" border>
              <el-descriptions-item label="scope">{{ workspace.scope }}</el-descriptions-item>
              <el-descriptions-item label="mode">{{ workspace.mode }}</el-descriptions-item>
              <el-descriptions-item label="readiness">{{ workspace.readinessLevel }}</el-descriptions-item>
              <el-descriptions-item label="Engineer Diagnostics">{{ workspace.engineerDiagnosticsWorkspace }}</el-descriptions-item>
              <el-descriptions-item label="No SSH">{{ workspace.sshExecuted }}</el-descriptions-item>
              <el-descriptions-item label="No Production Activation">{{ workspace.productionActivation }}</el-descriptions-item>
            </el-descriptions>
          </template>

          <template v-else-if="tab === 'Server Plan'">
            <div class="section-title">Server Plan</div>
            <el-descriptions :column="2" border>
              <el-descriptions-item label="APP / non-DB target">192.168.60.21</el-descriptions-item>
              <el-descriptions-item label="DB-only target">192.168.60.22</el-descriptions-item>
              <el-descriptions-item label="APP role">{{ workspace.serverPlan.appNonDb?.role }}</el-descriptions-item>
              <el-descriptions-item label="DB role">{{ workspace.serverPlan.dbOnly?.role }}</el-descriptions-item>
            </el-descriptions>
          </template>

          <template v-else-if="tab === 'Package Readiness'">
            <div class="section-title">Package Readiness</div>
            <el-table :data="workspace.packageReadiness" stripe border>
              <el-table-column prop="packageName" label="Package" min-width="190" />
              <el-table-column prop="category" label="Category" min-width="150" />
              <el-table-column prop="targetServer" label="Target" min-width="150" />
              <el-table-column prop="readinessStatus" label="Readiness" min-width="180" />
              <el-table-column prop="diagnosticState" label="Diagnostics" min-width="150" />
              <el-table-column prop="rollbackState" label="Rollback" min-width="150" />
              <el-table-column prop="readOnly" label="Read-only" min-width="110" />
            </el-table>
          </template>

          <template v-else-if="tab === 'EDGE'">
            <div class="section-title">EDGE Readiness</div>
            <el-descriptions :column="2" border>
              <el-descriptions-item v-for="(value, key) in workspace.edgeReadiness" :key="key" :label="String(key)">{{ value }}</el-descriptions-item>
            </el-descriptions>
          </template>

          <template v-else-if="tab === 'LINK'">
            <div class="section-title">LINK Readiness</div>
            <el-descriptions :column="2" border>
              <el-descriptions-item v-for="(value, key) in workspace.linkReadiness" :key="key" :label="String(key)">{{ value }}</el-descriptions-item>
            </el-descriptions>
          </template>

          <template v-else-if="tab === 'DB Foundation'">
            <div class="section-title">DB Foundation Readiness</div>
            <el-descriptions :column="2" border>
              <el-descriptions-item v-for="(value, key) in workspace.dbReadiness" :key="key" :label="String(key)">{{ value }}</el-descriptions-item>
            </el-descriptions>
          </template>

          <template v-else-if="tab === 'Contracts'">
            <div class="section-title">Contracts Readiness</div>
            <el-descriptions :column="2" border>
              <el-descriptions-item v-for="(value, key) in workspace.contractsReadiness" :key="key" :label="String(key)">{{ value }}</el-descriptions-item>
            </el-descriptions>
          </template>

          <template v-else-if="tab === 'Healthcheck Preview'">
            <div class="section-title">Healthcheck Preview</div>
            <el-table :data="workspace.healthcheckPreview" stripe border>
              <el-table-column prop="checkId" label="Check" min-width="130" />
              <el-table-column prop="checkName" label="Name" min-width="220" />
              <el-table-column prop="packageName" label="Package" min-width="180" />
              <el-table-column prop="targetServer" label="Target" min-width="150" />
              <el-table-column prop="executionState" label="Execution" min-width="150" />
              <el-table-column prop="previewStatus" label="Preview" min-width="150" />
            </el-table>
          </template>

          <template v-else-if="tab === 'Package Integrity'">
            <div class="section-title">Package Integrity Preview</div>
            <el-table :data="workspace.packageIntegrityPreview" stripe border>
              <el-table-column prop="packageName" label="Package" min-width="210" />
              <el-table-column prop="targetServer" label="Target" min-width="150" />
              <el-table-column prop="manifestReferenced" label="Manifest" min-width="120" />
              <el-table-column prop="checksumPreview" label="Checksum" min-width="160" />
              <el-table-column prop="integrityState" label="State" min-width="160" />
            </el-table>
          </template>

          <template v-else-if="tab === 'Rollback Readiness'">
            <div class="section-title">Rollback Readiness</div>
            <el-table :data="workspace.rollbackReadiness" stripe border>
              <el-table-column prop="rollbackItem" label="Rollback Item" min-width="260" />
              <el-table-column prop="packageName" label="Package" min-width="180" />
              <el-table-column prop="targetServer" label="Target" min-width="150" />
              <el-table-column prop="rollbackPlanReferenced" label="Plan" min-width="110" />
              <el-table-column prop="rollbackExecuted" label="Executed" min-width="120" />
            </el-table>
          </template>

          <template v-else>
            <div class="section-title">Guardrails</div>
            <div class="guardrail-grid">
              <el-tag v-for="item in workspace.guardrails" :key="item" round type="info">{{ item }}</el-tag>
            </div>
            <el-descriptions class="inner-gap" :column="3" border>
              <el-descriptions-item label="No Install">{{ workspace.installExecuted }}</el-descriptions-item>
              <el-descriptions-item label="No DB Migration">{{ workspace.dbMigrationExecuted }}</el-descriptions-item>
              <el-descriptions-item label="No EDGE Command Execution">{{ workspace.edgeCommandExecution }}</el-descriptions-item>
              <el-descriptions-item label="No LINK Command Execution">{{ workspace.linkCommandExecution }}</el-descriptions-item>
              <el-descriptions-item label="No Runtime Activation">{{ workspace.runtimeActivation }}</el-descriptions-item>
              <el-descriptions-item label="No Device Control">{{ workspace.deviceControl }}</el-descriptions-item>
            </el-descriptions>
          </template>
        </el-tab-pane>
      </el-tabs>
    </template>
  </section>
</template>

<style scoped>
.foundation-page {
  min-height: 100%;
  padding: 20px;
  background: #f4fbf8;
  color: #203331;
}

.workspace-head,
.target-strip,
.metric-card,
.workspace-tabs {
  border: 1px solid #d6ebe5;
  border-radius: 8px;
  background: #fff;
  box-shadow: 0 12px 28px rgb(34 82 73 / 8%);
}

.workspace-head {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  padding: 20px;
}

.workspace-head h1 {
  margin: 4px 0 8px;
  font-size: 28px;
  line-height: 1.2;
  letter-spacing: 0;
}

.eyebrow,
.summary,
.metric-card span,
.metric-card em {
  margin: 0;
  color: #647b76;
}

.eyebrow {
  font-size: 13px;
  font-weight: 700;
  text-transform: uppercase;
}

.badge-stack,
.guardrail-grid {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 8px;
}

.section-gap {
  margin-top: 16px;
}

.inner-gap {
  margin-top: 16px;
}

.target-strip {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  padding: 14px;
}

.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
  gap: 12px;
}

.metric-card {
  padding: 14px;
}

.metric-card strong {
  display: block;
  margin: 8px 0 4px;
  color: #007f73;
  font-size: 22px;
}

.metric-card em {
  font-style: normal;
}

.workspace-tabs {
  padding: 14px;
}

.section-title {
  margin: 0 0 12px;
  color: #123f3a;
  font-size: 18px;
  font-weight: 700;
}

@media (max-width: 820px) {
  .workspace-head,
  .target-strip {
    display: block;
  }

  .badge-stack {
    justify-content: flex-start;
    margin-top: 12px;
  }
}
</style>
