<template>
  <!-- Loading Screen -->
  <div v-if="!isLoaded" class="loading-container">
    <div class="loading-overlay">
      <div class="loading-content">
        <div class="loading-spinner">
          <div class="spinner-ring"></div>
          <div class="spinner-ring"></div>
          <div class="spinner-ring"></div>
        </div>
        <div class="loading-text">
          <span class="loading-title">Loading Feature Toggle Registry</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
        <div class="loading-subtip">Manage Feature Flags and Gradual Rollouts</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="feature-toggle-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <h2 class="page-title">Feature Toggle Registry</h2>
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/' }">Home</el-breadcrumb-item>
          <el-breadcrumb-item>Developer Center</el-breadcrumb-item>
          <el-breadcrumb-item>Feature Toggle Registry</el-breadcrumb-item>
        </el-breadcrumb>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="createFeatureToggle">
          <el-icon><Plus /></el-icon>
          Create Feature Flag
        </el-button>
        <el-button type="success" plain @click="exportToggleConfig">
          <el-icon><Download /></el-icon>
          Export Config
        </el-button>
        <el-button type="info" plain @click="viewAuditLog">
          <el-icon><List /></el-icon>
          Audit Log
        </el-button>
      </div>
    </div>

    <!-- Feature Toggle Statistics -->
    <div class="stats-section">
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon"><el-icon :size="32"><Flag /></el-icon></div>
          <div class="stat-info">
            <div class="stat-value">{{ totalFlags }}</div>
            <div class="stat-label">Total Feature Flags</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon"><el-icon :size="32"><SuccessFilled /></el-icon></div>
          <div class="stat-info">
            <div class="stat-value">{{ activeFlags }}</div>
            <div class="stat-label">Active Flags</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon"><el-icon :size="32"><DataLine /></el-icon></div>
          <div class="stat-info">
            <div class="stat-value">{{ experimentalFlags }}</div>
            <div class="stat-label">Experimental</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon"><el-icon :size="32"><User /></el-icon></div>
          <div class="stat-info">
            <div class="stat-value">{{ rolloutPercentage }}%</div>
            <div class="stat-label">Avg Rollout</div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Feature Toggles Grid -->
    <div class="toggles-section">
      <el-card class="toggles-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span><el-icon><Grid /></el-icon> Feature Flags</span>
            <div class="toggle-filters">
              <el-select v-model="statusFilter" placeholder="Status" size="small" style="width: 120px" clearable>
                <el-option label="All" value="" />
                <el-option label="Active" value="active" />
                <el-option label="Inactive" value="inactive" />
                <el-option label="Experimental" value="experimental" />
              </el-select>
              <el-select v-model="moduleFilter" placeholder="Module" size="small" style="width: 140px" clearable>
                <el-option label="All Modules" value="" />
                <el-option label="Core" value="core" />
                <el-option label="AI" value="ai" />
                <el-option label="ESG" value="esg" />
                <el-option label="DCIM" value="dcim" />
                <el-option label="Security" value="security" />
              </el-select>
              <el-input v-model="searchFlag" placeholder="Search flags..." size="small" style="width: 200px" clearable />
              <el-button size="small" @click="refreshToggles">
                <el-icon><Refresh /></el-icon> Refresh
              </el-button>
            </div>
          </div>
        </template>
        <div class="toggles-list">
          <div v-for="toggle in filteredToggles" :key="toggle.id" class="toggle-item">
            <div class="toggle-header">
              <div class="toggle-info">
                <div class="toggle-name">
                  <span class="name">{{ toggle.name }}</span>
                  <el-tag :type="getFlagTypeTag(toggle.type)" size="small">{{ toggle.type }}</el-tag>
                  <el-tag v-if="toggle.deprecated" type="danger" size="small">Deprecated</el-tag>
                </div>
                <div class="toggle-description">{{ toggle.description }}</div>
                <div class="toggle-meta">
                  <span><el-icon><Monitor /></el-icon> Module: {{ toggle.module }}</span>
                  <span><el-icon><User /></el-icon> Owner: {{ toggle.owner }}</span>
                  <span><el-icon><Calendar /></el-icon> Created: {{ toggle.createdAt }}</span>
                </div>
              </div>
              <div class="toggle-actions">
                <el-button size="small" text type="primary" @click="editToggle(toggle)">
                  <el-icon><Edit /></el-icon> Edit
                </el-button>
                <el-button size="small" text type="danger" @click="deleteToggle(toggle)">
                  <el-icon><Delete /></el-icon> Delete
                </el-button>
                <el-switch v-model="toggle.enabled" @change="toggleFeature(toggle)" />
              </div>
            </div>
            <div class="toggle-rollout">
              <div class="rollout-info">
                <span class="rollout-label">Rollout Percentage:</span>
                <span class="rollout-value">{{ toggle.rollout }}%</span>
                <el-slider v-model="toggle.rollout" :min="0" :max="100" :step="5" size="small" style="width: 200px" @change="updateRollout(toggle)" />
              </div>
              <div class="targeting-info" v-if="toggle.targetingRules.length">
                <span class="targeting-label">Targeting Rules:</span>
                <div class="targeting-tags">
                  <el-tag v-for="rule in toggle.targetingRules" :key="rule" size="small" type="info">{{ rule }}</el-tag>
                </div>
              </div>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Recent Changes -->
    <div class="changes-section">
      <el-card class="changes-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span><el-icon><Clock /></el-icon> Recent Changes</span>
            <el-button text type="primary" @click="viewAllChanges">View All</el-button>
          </div>
        </template>
        <el-table :data="recentChanges" stripe style="width: 100%">
          <el-table-column prop="timestamp" label="Time" width="160" />
          <el-table-column prop="flagName" label="Feature Flag" width="200" />
          <el-table-column prop="action" label="Action" width="120">
            <template #default="{ row }">
              <el-tag :type="getActionTagType(row.action)" size="small">{{ row.action }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="oldValue" label="Old Value" width="150" />
          <el-table-column prop="newValue" label="New Value" width="150" />
          <el-table-column prop="user" label="User" width="140" />
          <el-table-column label="Actions" width="80">
            <template #default="{ row }">
              <el-button size="small" text type="primary" @click="viewChangeDetails(row)">Details</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>

    <!-- Rollout Analytics -->
    <div class="analytics-section">
      <el-card class="analytics-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span><el-icon><TrendCharts /></el-icon> Rollout Analytics</span>
            <el-button text type="primary" @click="refreshAnalytics">Refresh</el-button>
          </div>
        </template>
        <div class="analytics-grid">
          <div class="analytics-item">
            <div class="analytics-label">Active Feature Flags</div>
            <div class="analytics-value">{{ activeFlags }}</div>
            <el-progress :percentage="(activeFlags / totalFlags) * 100" :stroke-width="6" :color="'#10b981'" />
          </div>
          <div class="analytics-item">
            <div class="analytics-label">Average Rollout</div>
            <div class="analytics-value">{{ avgRollout }}%</div>
            <el-progress :percentage="avgRollout" :stroke-width="6" :color="avgRollout >= 70 ? '#10b981' : avgRollout >= 40 ? '#f59e0b' : '#ef4444'" />
          </div>
          <div class="analytics-item">
            <div class="analytics-label">Flags by Module</div>
            <div class="module-stats">
              <div v-for="stat in moduleStats" :key="stat.module" class="module-stat">
                <span>{{ stat.module }}</span>
                <span>{{ stat.count }}</span>
              </div>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Environment Overrides -->
    <div class="env-section">
      <el-card class="env-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span><el-icon><Setting /></el-icon> Environment Overrides</span>
            <el-button text type="primary" @click="addEnvironment">Add Environment</el-button>
          </div>
        </template>
        <div class="env-grid">
          <div class="env-header">
            <span>Environment</span>
            <span>Active Overrides</span>
            <span>Status</span>
            <span></span>
          </div>
          <div v-for="env in environments" :key="env.name" class="env-row">
            <div class="env-name">
              <el-tag :type="getEnvTagType(env.name)" size="small">{{ env.name }}</el-tag>
            </div>
            <div class="env-overrides">{{ env.overrideCount }} flags overridden</div>
            <div class="env-status">
              <el-tag :type="env.status === 'active' ? 'success' : 'info'" size="small">{{ env.status }}</el-tag>
            </div>
            <div class="env-actions">
              <el-button size="small" text type="primary" @click="editEnvironment(env)">Configure</el-button>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Quick Actions Footer -->
    <div class="footer-actions">
      <div class="action-group">
        <el-button type="primary" plain @click="bulkUpdate">
          <el-icon><Edit /></el-icon>
          Bulk Update
        </el-button>
        <el-button type="success" plain @click="scheduleRollout">
          <el-icon><Calendar /></el-icon>
          Schedule Rollout
        </el-button>
        <el-button type="warning" plain @click="runImpactAnalysis">
          <el-icon><DataAnalysis /></el-icon>
          Impact Analysis
        </el-button>
        <el-button type="info" plain @click="viewDocumentation">
          <el-icon><Document /></el-icon>
          Documentation
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Refresh, Setting, User, Clock, Warning, CircleCheck, TrendCharts, DataLine,
  Star, Share, CopyDocument, Delete, Mic, Picture, Document, Upload, Download,
  MagicStick, ChatDotRound, Message, Service, Search, Edit, Plus, VideoPlay,
  VideoPause, Operation, Headset, Monitor, Cpu, Connection, Lock, Key, Medal,
  Flag, DataAnalysis, EditPen, Tickets, Filter, SuccessFilled, List, Grid, Calendar
} from '@element-plus/icons-vue'

// Loading state
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading Feature Toggle Registry...')

const loadingMessages = [
  'Loading Feature Toggle Registry...',
  'Fetching feature flags...',
  'Loading rollout configurations...',
  'Feature toggle registry ready!'
]

// Statistics
const totalFlags = ref(48)
const activeFlags = ref(32)
const experimentalFlags = ref(8)
const rolloutPercentage = ref(64)
const avgRollout = ref(64)

// Filters
const statusFilter = ref('')
const moduleFilter = ref('')
const searchFlag = ref('')

// Feature toggles data
const featureToggles = ref([
  {
    id: 1,
    name: 'ai-powered-analytics',
    type: 'release',
    description: 'Enable AI-powered analytics dashboard with predictive insights',
    module: 'ai',
    owner: 'Data Science Team',
    createdAt: '2024-01-10',
    enabled: true,
    rollout: 100,
    deprecated: false,
    targetingRules: ['internal_users', 'beta_testers']
  },
  {
    id: 2,
    name: 'new-esg-reporting-engine',
    type: 'experimental',
    description: 'New ESG reporting engine with enhanced compliance features',
    module: 'esg',
    owner: 'ESG Product Team',
    createdAt: '2024-01-08',
    enabled: true,
    rollout: 25,
    deprecated: false,
    targetingRules: ['esg_team', 'premium_tenants']
  },
  {
    id: 3,
    name: 'real-time-device-sync',
    type: 'release',
    description: 'Real-time device synchronization across all sites',
    module: 'core',
    owner: 'Core Platform Team',
    createdAt: '2024-01-05',
    enabled: true,
    rollout: 75,
    deprecated: false,
    targetingRules: ['high_bandwidth_sites']
  },
  {
    id: 4,
    name: 'legacy-bacnet-driver',
    type: 'deprecated',
    description: 'Legacy BACnet driver (use new driver instead)',
    module: 'core',
    owner: 'Integration Team',
    createdAt: '2023-06-15',
    enabled: false,
    rollout: 0,
    deprecated: true,
    targetingRules: []
  },
  {
    id: 5,
    name: 'dark-mode-ui',
    type: 'experimental',
    description: 'Dark mode theme for the IBMS dashboard',
    module: 'ui',
    owner: 'Frontend Team',
    createdAt: '2024-01-12',
    enabled: false,
    rollout: 0,
    deprecated: false,
    targetingRules: ['ui_testers']
  },
  {
    id: 6,
    name: 'digital-twin-3d-view',
    type: 'release',
    description: '3D visualization for digital twin integration',
    module: 'dcim',
    owner: 'DCIM Team',
    createdAt: '2023-12-20',
    enabled: true,
    rollout: 50,
    deprecated: false,
    targetingRules: ['enterprise_tier']
  },
  {
    id: 7,
    name: 'blockchain-evidence-anchoring',
    type: 'experimental',
    description: 'Blockchain-based evidence anchoring for compliance',
    module: 'security',
    owner: 'Security Team',
    createdAt: '2024-01-03',
    enabled: true,
    rollout: 10,
    deprecated: false,
    targetingRules: ['security_auditors']
  },
  {
    id: 8,
    name: 'mobile-push-notifications',
    type: 'release',
    description: 'Push notifications for mobile app users',
    module: 'core',
    owner: 'Mobile Team',
    createdAt: '2024-01-01',
    enabled: true,
    rollout: 90,
    deprecated: false,
    targetingRules: ['mobile_users']
  }
])

const filteredToggles = computed(() => {
  let result = featureToggles.value
  if (statusFilter.value) {
    if (statusFilter.value === 'active') {
      result = result.filter(t => t.enabled === true && t.type !== 'deprecated')
    } else if (statusFilter.value === 'inactive') {
      result = result.filter(t => t.enabled === false && t.type !== 'deprecated')
    } else if (statusFilter.value === 'experimental') {
      result = result.filter(t => t.type === 'experimental')
    }
  }
  if (moduleFilter.value) {
    result = result.filter(t => t.module === moduleFilter.value)
  }
  if (searchFlag.value) {
    const search = searchFlag.value.toLowerCase()
    result = result.filter(t => t.name.toLowerCase().includes(search) || t.description.toLowerCase().includes(search))
  }
  return result
})

// Module stats
const moduleStats = computed(() => {
  const stats: Record<string, number> = {}
  featureToggles.value.forEach(t => {
    stats[t.module] = (stats[t.module] || 0) + 1
  })
  return Object.entries(stats).map(([module, count]) => ({ module, count }))
})

// Recent changes
const recentChanges = ref([
  { id: 1, timestamp: '2024-01-15 09:45:32', flagName: 'ai-powered-analytics', action: 'Rollout Updated', oldValue: '75%', newValue: '100%', user: 'john.doe@ibms.com' },
  { id: 2, timestamp: '2024-01-15 08:30:22', flagName: 'new-esg-reporting-engine', action: 'Targeting Updated', oldValue: '10% + esg_team', newValue: '25% + premium_tenants', user: 'sarah.chen@ibms.com' },
  { id: 3, timestamp: '2024-01-14 16:20:15', flagName: 'digital-twin-3d-view', action: 'Enabled', oldValue: 'Disabled', newValue: 'Enabled (50%)', user: 'mike.wilson@ibms.com' },
  { id: 4, timestamp: '2024-01-14 11:10:45', flagName: 'blockchain-evidence-anchoring', action: 'Created', oldValue: '-', newValue: 'Experimental', user: 'security.team@ibms.com' }
])

// Environments
const environments = ref([
  { name: 'Development', overrideCount: 12, status: 'active' },
  { name: 'Staging', overrideCount: 8, status: 'active' },
  { name: 'Production', overrideCount: 3, status: 'active' },
  { name: 'Disaster Recovery', overrideCount: 0, status: 'inactive' }
])

// Helper functions
const getFlagTypeTag = (type: string) => {
  switch (type) {
    case 'release': return 'success'
    case 'experimental': return 'warning'
    case 'deprecated': return 'danger'
    default: return 'info'
  }
}

const getActionTagType = (action: string) => {
  switch (action) {
    case 'Created': return 'success'
    case 'Enabled': return 'success'
    case 'Rollout Updated': return 'warning'
    case 'Targeting Updated': return 'info'
    default: return 'info'
  }
}

const getEnvTagType = (env: string) => {
  switch (env) {
    case 'Development': return 'info'
    case 'Staging': return 'warning'
    case 'Production': return 'danger'
    default: return 'info'
  }
}

// Event handlers
const createFeatureToggle = () => {
  ElMessageBox.prompt('Enter feature flag name', 'Create Feature Flag', {
    confirmButtonText: 'Create',
    cancelButtonText: 'Cancel',
    inputPlaceholder: 'e.g., new-dashboard-ui'
  }).then(({ value }) => {
    if (value) {
      ElMessage.success(`Feature flag "${value}" created. Configure rollout and targeting next.`)
    }
  }).catch(() => {})
}

const exportToggleConfig = () => {
  ElMessage.info('Exporting feature toggle configuration...')
  setTimeout(() => {
    ElMessage.success('Configuration exported')
  }, 1000)
}

const viewAuditLog = () => {
  ElMessage.info('Viewing audit log')
}

const refreshToggles = () => {
  ElMessage.info('Refreshing feature toggles...')
  setTimeout(() => {
    ElMessage.success('Feature toggles refreshed')
  }, 800)
}

const editToggle = (toggle: any) => {
  ElMessage.info(`Editing feature flag: ${toggle.name}`)
}

const deleteToggle = (toggle: any) => {
  ElMessageBox.confirm(`Delete feature flag "${toggle.name}"? This action cannot be undone.`, 'Confirm Delete', {
    confirmButtonText: 'Delete',
    cancelButtonText: 'Cancel',
    type: 'danger'
  }).then(() => {
    featureToggles.value = featureToggles.value.filter(t => t.id !== toggle.id)
    ElMessage.success(`Feature flag "${toggle.name}" deleted`)
  }).catch(() => {})
}

const toggleFeature = (toggle: any) => {
  const action = toggle.enabled ? 'enabled' : 'disabled'
  ElMessage.success(`Feature flag "${toggle.name}" ${action}`)
}

const updateRollout = (toggle: any) => {
  ElMessage.success(`Rollout for "${toggle.name}" updated to ${toggle.rollout}%`)
}

const viewAllChanges = () => {
  ElMessage.info('Viewing all changes')
}

const viewChangeDetails = (change: any) => {
  ElMessageBox.alert(
      `Flag: ${change.flagName}\nAction: ${change.action}\nOld Value: ${change.oldValue}\nNew Value: ${change.newValue}\nUser: ${change.user}\nTime: ${change.timestamp}`,
      'Change Details',
      { confirmButtonText: 'OK', type: 'info' }
  )
}

const refreshAnalytics = () => {
  ElMessage.info('Refreshing analytics...')
  setTimeout(() => {
    ElMessage.success('Analytics refreshed')
  }, 800)
}

const addEnvironment = () => {
  ElMessage.info('Add environment dialog opened')
}

const editEnvironment = (env: any) => {
  ElMessage.info(`Configuring environment: ${env.name}`)
}

const bulkUpdate = () => {
  ElMessage.info('Bulk update dialog opened')
}

const scheduleRollout = () => {
  ElMessage.info('Schedule rollout dialog opened')
}

const runImpactAnalysis = () => {
  ElMessage.info('Running impact analysis...')
  setTimeout(() => {
    ElMessage.success('Impact analysis completed. No breaking changes detected.')
  }, 2000)
}

const viewDocumentation = () => {
  ElMessage.info('Opening feature toggle documentation')
}

// Loading animation
onMounted(() => {
  let messageIndex = 0
  const messageInterval = setInterval(() => {
    if (messageIndex < loadingMessages.length - 1) {
      messageIndex++
      loadingMessage.value = loadingMessages[messageIndex]
    }
  }, 400)

  const progressInterval = setInterval(() => {
    if (loadingProgress.value < 100) {
      loadingProgress.value += Math.random() * 15 + 5
      if (loadingProgress.value > 100) loadingProgress.value = 100
    }
  }, 200)

  setTimeout(() => {
    clearInterval(messageInterval)
    clearInterval(progressInterval)
    loadingProgress.value = 100
    loadingMessage.value = 'Ready!'

    setTimeout(() => {
      isLoaded.value = true
    }, 400)
  }, 2500)
})
</script>

<style scoped>
/* ==================== Loading Screen ==================== */
.loading-container {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  z-index: 9999;
  display: flex;
  justify-content: center;
  align-items: center;
}

.loading-overlay {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  backdrop-filter: blur(2px);
}

.loading-content {
  text-align: center;
  padding: 40px;
  border-radius: 32px;
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(59, 130, 246, 0.3);
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
  animation: fadeInUp 0.6s ease-out;
}

.loading-spinner {
  position: relative;
  width: 80px;
  height: 80px;
  margin: 0 auto 24px;
}

.spinner-ring {
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  border: 3px solid transparent;
  animation: spin 1.5s cubic-bezier(0.68, -0.55, 0.265, 1.55) infinite;
}

.spinner-ring:nth-child(1) {
  border-top-color: #3b82f6;
  animation-delay: 0s;
}

.spinner-ring:nth-child(2) {
  border-right-color: #f59e0b;
  animation-delay: 0.2s;
  width: 70%;
  height: 70%;
  top: 15%;
  left: 15%;
}

.spinner-ring:nth-child(3) {
  border-bottom-color: #10b981;
  animation-delay: 0.4s;
  width: 40%;
  height: 40%;
  top: 30%;
  left: 30%;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  margin-bottom: 24px;
  font-size: 24px;
  font-weight: 700;
  color: #e2e8f0;
  display: flex;
  justify-content: center;
  align-items: baseline;
  gap: 4px;
}

.loading-dots {
  display: inline-flex;
  gap: 2px;
}

.loading-dots span {
  animation: bounce 1.4s infinite ease-in-out both;
}

.loading-dots span:nth-child(1) { animation-delay: -0.32s; }
.loading-dots span:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); opacity: 0.3; }
  40% { transform: scale(1); opacity: 1; }
}

.loading-progress {
  width: 280px;
  height: 4px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  overflow: hidden;
  margin: 0 auto 16px;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #8b5cf6, #ec489a);
  border-radius: 4px;
  transition: width 0.3s ease;
  background-size: 200% auto;
  animation: shimmer 2s linear infinite;
}

@keyframes shimmer {
  0% { background-position: 0% 0%; }
  100% { background-position: 200% 0%; }
}

.loading-tip {
  font-size: 13px;
  color: #94a3b8;
  letter-spacing: 1px;
  margin-bottom: 8px;
  font-weight: 500;
}

.loading-subtip {
  font-size: 11px;
  color: #64748b;
  letter-spacing: 0.5px;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}

/* ==================== Main Content ==================== */
.feature-toggle-container {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 8px 0;
}

.header-right {
  display: flex;
  gap: 12px;
}

/* Stats Section */
.stats-section {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  border-radius: 12px;
  background: white;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
}

.stat-icon {
  width: 56px;
  height: 56px;
  background: #f8fafc;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #3b82f6;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
}

.stat-label {
  font-size: 12px;
  color: #64748b;
}

/* Toggles Section */
.toggles-section {
  margin-bottom: 24px;
}

.toggles-card {
  border-radius: 12px;
  background: white;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  color: #1e293b;
}

.toggle-filters {
  display: flex;
  gap: 12px;
}

.toggles-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.toggle-item {
  padding: 16px;
  background: #f8fafc;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
}

.toggle-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.toggle-name {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
  flex-wrap: wrap;
}

.toggle-name .name {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  font-family: monospace;
}

.toggle-description {
  font-size: 13px;
  color: #64748b;
  margin-bottom: 8px;
}

.toggle-meta {
  display: flex;
  gap: 20px;
  font-size: 12px;
  color: #94a3b8;
}

.toggle-meta span {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.toggle-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.toggle-rollout {
  padding-top: 12px;
  border-top: 1px solid #e2e8f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}

.rollout-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.rollout-label {
  font-size: 12px;
  color: #64748b;
}

.rollout-value {
  font-size: 14px;
  font-weight: 600;
  color: #3b82f6;
}

.targeting-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.targeting-label {
  font-size: 12px;
  color: #64748b;
}

.targeting-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

/* Changes Section */
.changes-section {
  margin-bottom: 24px;
}

.changes-card {
  border-radius: 12px;
  background: white;
}

/* Analytics Section */
.analytics-section {
  margin-bottom: 24px;
}

.analytics-card {
  border-radius: 12px;
  background: white;
}

.analytics-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.analytics-item {
  padding: 12px;
  background: #f8fafc;
  border-radius: 10px;
}

.analytics-label {
  font-size: 12px;
  color: #64748b;
  margin-bottom: 8px;
}

.analytics-value {
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 12px;
}

.module-stats {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.module-stat {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  color: #475569;
}

/* Env Section */
.env-section {
  margin-bottom: 24px;
}

.env-card {
  border-radius: 12px;
  background: white;
}

.env-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.env-header {
  display: grid;
  grid-template-columns: 150px 1fr 100px 100px;
  padding: 10px 12px;
  background: #f8fafc;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  color: #64748b;
}

.env-row {
  display: grid;
  grid-template-columns: 150px 1fr 100px 100px;
  align-items: center;
  padding: 12px;
  background: #f8fafc;
  border-radius: 8px;
}

.env-name {
  font-weight: 500;
}

.env-overrides {
  font-size: 13px;
  color: #475569;
}

/* Footer Actions */
.footer-actions {
  margin-top: 8px;
}

.action-group {
  display: flex;
  gap: 16px;
  justify-content: flex-end;
  padding: 16px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

/* Responsive */
@media (max-width: 1200px) {
  .stats-section {
    grid-template-columns: repeat(2, 1fr);
  }

  .analytics-grid {
    grid-template-columns: 1fr;
  }

  .env-header,
  .env-row {
    grid-template-columns: 1fr;
    gap: 8px;
  }
}

@media (max-width: 768px) {
  .stats-section {
    grid-template-columns: 1fr;
  }

  .page-header {
    flex-direction: column;
    gap: 16px;
  }

  .header-right {
    flex-wrap: wrap;
  }

  .toggle-header {
    flex-direction: column;
    gap: 12px;
  }

  .toggle-rollout {
    flex-direction: column;
    align-items: flex-start;
  }

  .rollout-info {
    flex-wrap: wrap;
  }

  .action-group {
    flex-wrap: wrap;
    justify-content: center;
  }

  .toggle-filters {
    flex-wrap: wrap;
  }
}
</style>