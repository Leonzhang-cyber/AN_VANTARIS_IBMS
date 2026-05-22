<template>
  <!-- Loading Screen -->
  <div v-if="!isPageLoaded" class="loading-container">
    <div class="loading-overlay">
      <div class="loading-content">
        <div class="loading-spinner">
          <div class="spinner-ring"></div>
          <div class="spinner-ring"></div>
          <div class="spinner-ring"></div>
        </div>
        <div class="loading-text">
          <span class="loading-title">Loading</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Web3.0 Technical Services</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="web3-service-page">
    <!-- Hero Section -->
    <div class="hero-section">
      <div class="hero-content">
        <div class="hero-icon">
          <div class="hex-bg"></div>
          <span class="icon">⛓️</span>
        </div>
        <h1>Web3.0 Technical Services</h1>
        <p class="subtitle">Private Blockchain · DID · Verifiable Credentials · Data Anchoring</p>
        <div class="badges">
          <el-tag type="success" effect="dark">Clique PoA</el-tag>
          <el-tag type="info" effect="dark">Chain ID: 9527</el-tag>
          <el-tag effect="dark">Block Interval: 5s</el-tag>
          <el-tag type="warning" effect="dark">3-Node Cluster</el-tag>
        </div>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon green">🔗</div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.chainHeight }}</div>
          <div class="stat-label">Chain Height</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon blue">🆔</div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.didCount }}</div>
          <div class="stat-label">DID Entities</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon purple">📜</div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.vcCount }}</div>
          <div class="stat-label">VC Issued</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange">🔐</div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.anchorCount }}</div>
          <div class="stat-label">Anchored Records</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon cyan">⛏️</div>
        <div class="stat-info">
          <div class="stat-value" :class="{ active: stats.miningActive }">
            {{ stats.miningActive ? 'Active' : 'Idle' }}
          </div>
          <div class="stat-label">Mining Status</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon red">❤️</div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.healthyNodes }}/3</div>
          <div class="stat-label">Healthy Nodes</div>
        </div>
      </div>
    </div>

    <!-- Two Column Layout - Balanced -->
    <el-row :gutter="20">
      <!-- Left Column -->
      <el-col :xs="24" :md="12">
        <!-- System Architecture -->
        <el-card class="arch-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>🏗️ System Architecture</span>
              <el-tag size="small" type="info">Modular Design</el-tag>
            </div>
          </template>

          <el-collapse v-model="activeCollapse" accordion>
            <el-collapse-item v-for="module in architectureModules" :key="module.name" :name="module.name">
              <template #title>
                <div class="module-title">
                  <span class="module-icon">{{ module.icon }}</span>
                  <span class="module-name">{{ module.name }}</span>
                  <el-tag :type="module.tagType" size="small" class="module-tag">{{ module.children?.length || 0 }} Components</el-tag>
                </div>
              </template>

              <div v-for="child in module.children" :key="child.name" class="sub-module-item">
                <div class="sub-module-header">
                  <span class="sub-module-icon">{{ child.icon }}</span>
                  <span class="sub-module-name">{{ child.name }}</span>
                  <el-tag v-if="child.children" size="small" type="info" plain>{{ child.children.length }} Nodes</el-tag>
                </div>
                <div v-if="child.children" class="grandchild-list">
                  <el-tag v-for="grand in child.children" :key="grand.name" size="small" effect="plain" class="grandchild-tag">
                    {{ grand.icon }} {{ grand.name }}
                  </el-tag>
                </div>
              </div>
            </el-collapse-item>
          </el-collapse>

          <div class="arch-summary">
            <div class="summary-title">Module Interaction Flow</div>
            <div class="flow-diagram">
              <div class="flow-step"><div class="flow-icon">📡</div><div class="flow-text">IoT</div></div>
              <div class="flow-arrow">→</div>
              <div class="flow-step"><div class="flow-icon">🔐</div><div class="flow-text">DID</div></div>
              <div class="flow-arrow">→</div>
              <div class="flow-step"><div class="flow-icon">📊</div><div class="flow-text">Model</div></div>
              <div class="flow-arrow">→</div>
              <div class="flow-step"><div class="flow-icon">⛓️</div><div class="flow-text">Chain</div></div>
              <div class="flow-arrow">→</div>
              <div class="flow-step"><div class="flow-icon">🌐</div><div class="flow-text">API</div></div>
            </div>
          </div>
        </el-card>

        <!-- Smart Contracts -->
        <el-card class="contracts-card" shadow="hover" style="margin-top: 20px;">
          <template #header>
            <div class="card-header">
              <span>📜 Smart Contracts</span>
              <el-tag size="small" type="warning">Verified</el-tag>
            </div>
          </template>
          <el-table :data="contracts" stripe size="small">
            <el-table-column prop="name" label="Contract" />
            <el-table-column prop="address" label="Address" :formatter="(row) => shortenAddress(row.address, 10)" />
            <el-table-column prop="description" label="Description" />
          </el-table>
        </el-card>

        <!-- Key Features -->
        <el-card class="features-card" shadow="hover" style="margin-top: 20px;">
          <template #header>
            <div class="card-header">
              <span>✨ Key Features</span>
              <el-tag size="small" type="primary">Web3.0 Ready</el-tag>
            </div>
          </template>
          <div class="features-grid">
            <div class="feature-item">
              <div class="feature-icon">⛏️</div>
              <div class="feature-title">On-Demand Mining</div>
              <div class="feature-desc">Mining starts only when write requests exist</div>
            </div>
            <div class="feature-item">
              <div class="feature-icon">🔄</div>
              <div class="feature-title">Round-Robin Sealing</div>
              <div class="feature-desc">Three signers rotate every 5 seconds</div>
            </div>
            <div class="feature-item">
              <div class="feature-icon">🛡️</div>
              <div class="feature-title">Fault Tolerance</div>
              <div class="feature-desc">≥2 healthy nodes required</div>
            </div>
            <div class="feature-item">
              <div class="feature-icon">🔗</div>
              <div class="feature-title">Data Anchoring</div>
              <div class="feature-desc">Hash stored permanently on-chain</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- Right Column -->
      <el-col :xs="24" :md="12">
        <!-- Technical Specifications -->
        <el-card class="specs-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>⚙️ Technical Specifications</span>
              <el-tag size="small" type="success">Production Ready</el-tag>
            </div>
          </template>
          <el-descriptions :column="1" border size="small">
            <el-descriptions-item label="Consensus">
              <el-tag size="small" type="success">Clique (PoA)</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="Block Interval">5 seconds</el-descriptions-item>
            <el-descriptions-item label="Chain ID">9527</el-descriptions-item>
            <el-descriptions-item label="Nodes">3 (expandable)</el-descriptions-item>
            <el-descriptions-item label="Initial Supply">300 ETH (100 ETH per signer)</el-descriptions-item>
            <el-descriptions-item label="Signer Threshold">≥2 healthy nodes</el-descriptions-item>
            <el-descriptions-item label="Gas Limit">8,000,000</el-descriptions-item>
            <el-descriptions-item label="Geth Version">v1.13.15</el-descriptions-item>
          </el-descriptions>
        </el-card>

        <!-- API Endpoints -->
        <el-card class="api-card" shadow="hover" style="margin-top: 20px;">
          <template #header>
            <div class="card-header">
              <span>🔌 API Endpoints</span>
              <el-tag size="small" type="info">RESTful · JSON-RPC</el-tag>
            </div>
          </template>
          <div class="api-list">
            <div v-for="(api, idx) in apiEndpoints" :key="idx" class="api-item">
              <el-tag :type="api.method === 'POST' ? 'success' : 'info'" size="small">{{ api.method }}</el-tag>
              <span class="api-endpoint">{{ api.endpoint }}</span>
              <span class="api-desc">{{ api.description }}</span>
            </div>
          </div>
        </el-card>

        <!-- Network Status -->
        <el-card class="network-card" shadow="hover" style="margin-top: 20px;">
          <template #header>
            <div class="card-header">
              <span>🌐 Network Status</span>
              <el-tag size="small" type="success">Live</el-tag>
            </div>
          </template>
          <div class="node-list">
            <div v-for="node in networkNodes" :key="node.name" class="node-item">
              <div class="node-status">
                <span :class="['status-dot', node.status]"></span>
                <span class="node-name">{{ node.name }}</span>
              </div>
              <div class="node-info">
                <span class="node-address">{{ node.address }}</span>
                <el-tag :type="node.syncStatus === 'Synced' ? 'success' : 'warning'" size="small">{{ node.syncStatus }}</el-tag>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Recent Anchoring Records - Full Width -->
    <el-card class="records-card" shadow="hover" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>📋 Recent Anchoring Records</span>
          <el-tag size="small" type="info">On-Chain Data</el-tag>
        </div>
      </template>
      <el-table :data="anchoringRecords" stripe size="small">
        <el-table-column prop="operation" label="Operation" />
        <el-table-column prop="entityId" label="Entity ID" />
        <el-table-column prop="txHash" label="Transaction Hash" :formatter="(row) => shortenAddress(row.txHash, 12)" />
        <el-table-column prop="blockNumber" label="Block" width="90" />
        <el-table-column prop="timestamp" label="Timestamp" width="170" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

// ==================== Loading State ====================
const isPageLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing assets...')

const loadingMessages = [
  'Preparing assets...',
  'Loading modules...',
  'Initializing blockchain...',
  'Connecting to nodes...',
  'Loading dashboard...',
  'Almost ready...'
]

// ==================== Stats data ====================
const stats = ref({
  chainHeight: 247,
  didCount: 156,
  vcCount: 423,
  anchorCount: 89,
  miningActive: true,
  healthyNodes: 3,
})

// ==================== Architecture modules data ====================
const activeCollapse = ref('')
const architectureModules = ref([
  {
    name: 'DID Service',
    icon: '🔐',
    tagType: 'success',
    children: [
      { name: 'Entity Registration', icon: '📝', children: null },
      { name: 'VC Issuance', icon: '🎫', children: null },
      { name: 'VP Verification', icon: '✅', children: null },
      { name: 'Permission Inheritance', icon: '🔑', children: null }
    ]
  },
  {
    name: 'IoT Digital Base',
    icon: '📡',
    tagType: 'warning',
    children: [
      { name: 'MQTT Driver', icon: '📨', children: null },
      { name: 'HTTP Driver', icon: '🌐', children: null },
      { name: 'Modbus Driver', icon: '🔌', children: null },
      { name: 'Field/Method Mapping', icon: '🗺️', children: null }
    ]
  },
  {
    name: 'Data Modeling',
    icon: '📊',
    tagType: 'primary',
    children: [
      { name: 'XGBoost Training', icon: '🤖', children: null },
      { name: 'Energy Prediction', icon: '⚡', children: null },
      { name: 'CSV Storage', icon: '💾', children: null },
      { name: 'Savings Simulation', icon: '💰', children: null }
    ]
  },
  {
    name: 'Blockchain',
    icon: '⛓️',
    tagType: 'info',
    children: [
      {
        name: 'Geth Private Chain',
        icon: '⛏️',
        children: [
          { name: 'Node 1 (RPC:8545)', icon: '🖥️' },
          { name: 'Node 2 (RPC:8546)', icon: '🖥️' },
          { name: 'Node 3 (RPC:8547)', icon: '🖥️' }
        ]
      },
      { name: 'IBMSAnchor Contract', icon: '📜', children: null },
      { name: 'Mining Scheduler', icon: '⏰', children: null }
    ]
  },
  {
    name: 'API Layer',
    icon: '🌐',
    tagType: 'danger',
    children: [
      { name: 'DID API (15 endpoints)', icon: '🆔', children: null },
      { name: 'IoT API (27 endpoints)', icon: '📡', children: null },
      { name: 'Modeling API (6 endpoints)', icon: '📊', children: null },
      { name: 'SSE Push', icon: '📨', children: null }
    ]
  }
])

// ==================== Network nodes ====================
const networkNodes = ref([
  { name: 'Signer Node 1', address: '0x8a3f...d4e5', status: 'online', syncStatus: 'Synced' },
  { name: 'Signer Node 2', address: '0x7b2e...c3d4', status: 'online', syncStatus: 'Synced' },
  { name: 'Signer Node 3', address: '0x6c1d...b2c3', status: 'online', syncStatus: 'Synced' },
])

// ==================== Smart contracts ====================
const contracts = ref([
  { name: 'IBMSAnchor', address: '0x3a4Bc5De6f7G8h9I0j1K2l3M4n5O6p7Q8r9S0t', description: 'Data Anchoring' },
  { name: 'DIDRegistry', address: '0x4b5Cd6Ef7g8H9i0J1k2L3m4N5o6P7q8R9s0T1u', description: 'DID Management' },
  { name: 'VCManager', address: '0x5c6De7f8g9H0i1J2k3L4m5N6o7P8q9R0s1T2uV', description: 'VC Issuance' },
])

// ==================== API endpoints ====================
const apiEndpoints = ref([
  { method: 'POST', endpoint: '/api/did/entity', description: 'Register DID entity' },
  { method: 'POST', endpoint: '/api/did/vc/issue', description: 'Issue VC' },
  { method: 'POST', endpoint: '/api/did/vp/verify', description: 'Verify VP' },
  { method: 'GET', endpoint: '/api/iot/device/register', description: 'Register IoT device' },
  { method: 'POST', endpoint: '/api/iot/device/command', description: 'Send command' },
  { method: 'GET', endpoint: '/api/modeling/predict', description: 'Energy prediction' },
])

// ==================== Anchoring records ====================
const anchoringRecords = ref([
  { operation: 'DID Registration', entityId: 'did:imbs:system:root', txHash: '0x1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p', blockNumber: 124, timestamp: '2025-04-17 14:23:10' },
  { operation: 'VC Issuance', entityId: 'did:imbs:device:hvac_001', txHash: '0x2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q', blockNumber: 129, timestamp: '2025-04-17 14:25:30' },
  { operation: 'Device Metadata', entityId: 'did:imbs:device:hvac_002', txHash: '0x3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r', blockNumber: 135, timestamp: '2025-04-17 14:28:15' },
  { operation: 'DID Registration', entityId: 'did:imbs:person:admin', txHash: '0x4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s', blockNumber: 142, timestamp: '2025-04-17 14:32:40' },
  { operation: 'Data Anchoring', entityId: 'critical:alert:power', txHash: '0x5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t', blockNumber: 148, timestamp: '2025-04-17 14:36:20' },
])

// ==================== Helper functions ====================
const shortenAddress = (addr: string, len = 6) => {
  if (!addr) return ''
  return `${addr.slice(0, len)}...${addr.slice(-4)}`
}

// ==================== Loading Animation ====================
const startLoading = () => {
  let progress = 0
  let msgIndex = 0

  const msgInterval = setInterval(() => {
    if (msgIndex < loadingMessages.length - 1) {
      msgIndex++
      loadingMessage.value = loadingMessages[msgIndex]
    }
  }, 800)

  const progressInterval = setInterval(() => {
    if (progress < 90) {
      progress += Math.random() * 10
      loadingProgress.value = Math.min(progress, 90)

      if (progress > 80 && loadingMessage.value !== loadingMessages[5]) {
        loadingMessage.value = loadingMessages[5]
      } else if (progress > 60 && loadingMessage.value !== loadingMessages[4]) {
        loadingMessage.value = loadingMessages[4]
      } else if (progress > 40 && loadingMessage.value !== loadingMessages[3]) {
        loadingMessage.value = loadingMessages[3]
      } else if (progress > 20 && loadingMessage.value !== loadingMessages[2]) {
        loadingMessage.value = loadingMessages[2]
      } else if (progress > 10 && loadingMessage.value !== loadingMessages[1]) {
        loadingMessage.value = loadingMessages[1]
      }
    }
  }, 100)

  setTimeout(() => {
    clearInterval(msgInterval)
    clearInterval(progressInterval)
    loadingMessage.value = 'Ready!'
    loadingProgress.value = 100

    setTimeout(() => {
      isPageLoaded.value = true
    }, 500)
  }, 2500)
}

// ==================== Auto update data ====================
let updateInterval: ReturnType<typeof setInterval>

onMounted(() => {
  startLoading()

  updateInterval = setInterval(() => {
    stats.value.chainHeight += Math.floor(Math.random() * 3) + 1
  }, 30000)
})

onUnmounted(() => {
  clearInterval(updateInterval)
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
  font-size: 28px;
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

/* ==================== Main Content Styles ==================== */
.web3-service-page {
  background: #f5f7fa;
  min-height: 100vh;
  padding: 24px;
}

/* Hero Section */
.hero-section {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
  border-radius: 16px;
  padding: 32px 24px;
  margin-bottom: 24px;
  text-align: center;
  position: relative;
  overflow: hidden;
}

.hero-section::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(0, 212, 255, 0.1) 0%, transparent 70%);
  pointer-events: none;
}

.hero-icon {
  position: relative;
  display: inline-block;
  margin-bottom: 16px;
}

.hex-bg {
  width: 70px;
  height: 70px;
  background: linear-gradient(135deg, #00d4ff, #00ff88);
  clip-path: polygon(25% 0%, 75% 0%, 100% 25%, 100% 75%, 75% 100%, 25% 100%, 0% 75%, 0% 25%);
  opacity: 0.3;
  position: absolute;
  top: 0;
  left: 0;
}

.hero-icon .icon {
  font-size: 36px;
  line-height: 70px;
  display: inline-block;
  width: 70px;
  position: relative;
  z-index: 1;
}

.hero-section h1 {
  font-size: 28px;
  font-weight: 700;
  color: #ffffff;
  margin-bottom: 8px;
  letter-spacing: 1px;
}

.subtitle {
  font-size: 14px;
  color: #a0aec0;
  margin-bottom: 16px;
}

.badges {
  display: flex;
  gap: 10px;
  justify-content: center;
  flex-wrap: wrap;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  font-size: 28px;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
  border-radius: 10px;
}

.stat-icon.green { background: #e6f7e6; }
.stat-icon.blue { background: #e6f0ff; }
.stat-icon.purple { background: #f0e6ff; }
.stat-icon.orange { background: #fff0e6; }
.stat-icon.cyan { background: #e6f7ff; }
.stat-icon.red { background: #ffe6e6; }

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #303133;
  line-height: 1.2;
}

.stat-value.active {
  color: #67c23a;
}

.stat-label {
  font-size: 11px;
  color: #909399;
  margin-top: 4px;
}

/* Card Header */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  color: #303133;
  font-size: 14px;
}

/* Architecture Card */
.arch-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
}

:deep(.el-card__header) {
  padding: 14px 16px;
  border-bottom: 1px solid #e4e7ed;
  background: #fafafa;
}

:deep(.el-card__body) {
  padding: 16px;
}

.module-title {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
}

.module-icon {
  font-size: 18px;
}

.module-name {
  font-weight: 600;
  font-size: 14px;
}

.module-tag {
  margin-left: auto;
}

.sub-module-item {
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
}

.sub-module-item:last-child {
  border-bottom: none;
}

.sub-module-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.sub-module-icon {
  font-size: 14px;
}

.sub-module-name {
  font-size: 13px;
  font-weight: 500;
  color: #606266;
}

.grandchild-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 8px;
  padding-left: 24px;
}

.grandchild-tag {
  font-size: 11px;
}

/* Architecture Summary */
.arch-summary {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 16px;
  margin-top: 16px;
}

.summary-title {
  font-size: 12px;
  font-weight: 600;
  color: #606266;
  margin-bottom: 12px;
  text-align: center;
}

.flow-diagram {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.flow-step {
  text-align: center;
  flex: 1;
}

.flow-icon {
  font-size: 24px;
  margin-bottom: 4px;
}

.flow-text {
  font-size: 10px;
  font-weight: 600;
  color: #606266;
}

.flow-arrow {
  font-size: 16px;
  color: #c0c4cc;
}

/* Smart Contracts */
.contracts-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
}

:deep(.el-table) {
  font-size: 12px;
}

:deep(.el-table th) {
  background: #f5f7fa;
  font-size: 12px;
}

:deep(.el-table td) {
  font-size: 11px;
}

/* Features Grid */
.features-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.feature-item {
  text-align: center;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 8px;
  transition: all 0.2s;
}

.feature-item:hover {
  background: #ecf5ff;
}

.feature-icon {
  font-size: 28px;
  margin-bottom: 8px;
}

.feature-title {
  font-size: 12px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.feature-desc {
  font-size: 10px;
  color: #909399;
  line-height: 1.3;
}

/* Technical Specifications */
.specs-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
}

.specs-card :deep(.el-descriptions__label) {
  width: 130px;
  background: #f5f7fa;
  font-size: 12px;
}

.specs-card :deep(.el-descriptions__content) {
  font-size: 12px;
}

/* API List */
.api-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
}

.api-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.api-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.api-item:last-child {
  border-bottom: none;
}

.api-endpoint {
  font-family: monospace;
  font-size: 12px;
  color: #409eff;
  min-width: 160px;
}

.api-desc {
  font-size: 12px;
  color: #606266;
  flex: 1;
}

/* Network Status */
.network-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
}

.node-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.node-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  background: #f5f7fa;
  border-radius: 8px;
}

.node-status {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

.status-dot.online {
  background: #67c23a;
  box-shadow: 0 0 4px #67c23a;
}

.status-dot.offline {
  background: #f56c6c;
}

.node-name {
  font-size: 13px;
  font-weight: 500;
  color: #303133;
}

.node-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.node-address {
  font-family: monospace;
  font-size: 11px;
  color: #909399;
}

/* Records Card */
.records-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
}

/* Responsive */
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 768px) {
  .web3-service-page {
    padding: 16px;
  }

  .hero-section {
    padding: 24px 16px;
  }

  .hero-section h1 {
    font-size: 22px;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }

  .stat-card {
    padding: 12px;
  }

  .stat-value {
    font-size: 20px;
  }

  .features-grid {
    grid-template-columns: 1fr;
  }

  .api-endpoint {
    min-width: 100px;
    font-size: 10px;
  }

  .flow-diagram {
    flex-wrap: wrap;
    justify-content: center;
  }

  .flow-arrow {
    display: none;
  }
}
</style>