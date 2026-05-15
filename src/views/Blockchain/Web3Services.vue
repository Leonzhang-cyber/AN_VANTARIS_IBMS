<template>
  <div class="web3-service-page">
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

    <!-- Two Column Layout -->
    <el-row :gutter="16">
      <!-- Left Column: Architecture Tree -->
      <el-col :xs="24" :md="14">
        <el-card class="arch-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>🏗️ System Architecture</span>
              <el-tag size="small" type="info">Vertical Tree · Clique PoA</el-tag>
            </div>
          </template>
          <div ref="chartContainer" class="tree-chart-container"></div>
        </el-card>
      </el-col>

      <!-- Right Column: Technical Specifications -->
      <el-col :xs="24" :md="10">
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
      </el-col>
    </el-row>

    <!-- Smart Contracts & API Endpoints Row -->
    <el-row :gutter="16" style="margin-top: 16px;">
      <el-col :xs="24" :md="12">
        <el-card class="contracts-card" shadow="hover">
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
      </el-col>

      <el-col :xs="24" :md="12">
        <el-card class="api-card" shadow="hover">
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
      </el-col>
    </el-row>

    <!-- Features Section -->
    <el-card class="features-card" shadow="hover" style="margin-top: 16px;">
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
          <div class="feature-desc">Mining starts only when write requests exist, stops after 10min idle</div>
        </div>
        <div class="feature-item">
          <div class="feature-icon">🔄</div>
          <div class="feature-title">Round-Robin Sealing</div>
          <div class="feature-desc">Three signers rotate to seal blocks every 5 seconds</div>
        </div>
        <div class="feature-item">
          <div class="feature-icon">🛡️</div>
          <div class="feature-title">Fault Tolerance</div>
          <div class="feature-desc">Block production continues with ≥2 healthy nodes</div>
        </div>
        <div class="feature-item">
          <div class="feature-icon">🔗</div>
          <div class="feature-title">Data Anchoring</div>
          <div class="feature-desc">Critical operation hashes stored permanently on-chain</div>
        </div>
        <div class="feature-item">
          <div class="feature-icon">📋</div>
          <div class="feature-title">Event Tracing</div>
          <div class="feature-desc">All contract events automatically recorded and queryable</div>
        </div>
        <div class="feature-item">
          <div class="feature-icon">🌐</div>
          <div class="feature-title">RPC Gateway</div>
          <div class="feature-desc">Three node endpoints with load balancing support</div>
        </div>
      </div>
    </el-card>

    <!-- Recent Anchoring Records -->
    <el-card class="records-card" shadow="hover" style="margin-top: 16px;">
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
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'

// ============ Mock Data ============

// Stats data
const stats = ref({
  chainHeight: 247,
  didCount: 156,
  vcCount: 423,
  anchorCount: 89,
  miningActive: true,
  healthyNodes: 3,
})

// Smart contracts
const contracts = ref([
  { name: 'IMBSAnchor', address: '0x3a4Bc5De6f7G8h9I0j1K2l3M4n5O6p7Q8r9S0t', description: 'Data Anchoring' },
  { name: 'DIDRegistry', address: '0x4b5Cd6Ef7g8H9i0J1k2L3m4N5o6P7q8R9s0T1u', description: 'DID Management' },
  { name: 'VCManager', address: '0x5c6De7f8g9H0i1J2k3L4m5N6o7P8q9R0s1T2uV', description: 'VC Issuance & Verification' },
])

// API endpoints
const apiEndpoints = ref([
  { method: 'POST', endpoint: '/api/did/entity', description: 'Register DID entity' },
  { method: 'POST', endpoint: '/api/did/vc/issue', description: 'Issue VC' },
  { method: 'POST', endpoint: '/api/did/vp/verify', description: 'Verify VP' },
  { method: 'GET', endpoint: '/api/iot/device/register', description: 'Register IoT device' },
  { method: 'POST', endpoint: '/api/iot/device/command', description: 'Send device command' },
  { method: 'GET', endpoint: '/api/modeling/predict', description: 'Energy prediction' },
])

// Anchoring records
const anchoringRecords = ref([
  { operation: 'DID Registration', entityId: 'did:imbs:system:root', txHash: '0x1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p', blockNumber: 124, timestamp: '2025-04-17 14:23:10' },
  { operation: 'VC Issuance', entityId: 'did:imbs:device:hvac_001', txHash: '0x2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q', blockNumber: 129, timestamp: '2025-04-17 14:25:30' },
  { operation: 'Device Metadata', entityId: 'did:imbs:device:hvac_002', txHash: '0x3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r', blockNumber: 135, timestamp: '2025-04-17 14:28:15' },
  { operation: 'DID Registration', entityId: 'did:imbs:person:admin', txHash: '0x4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s', blockNumber: 142, timestamp: '2025-04-17 14:32:40' },
  { operation: 'Data Anchoring', entityId: 'critical:alert:power_outage', txHash: '0x5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t', blockNumber: 148, timestamp: '2025-04-17 14:36:20' },
])

// ECharts 纵向树状图数据
const treeData = {
  name: '🏛️ System Root',
  symbolSize: 40,
  itemStyle: { color: '#409eff' },
  children: [
    {
      name: '🔐 DID Service',
      symbolSize: 32,
      itemStyle: { color: '#67c23a' },
      children: [
        { name: 'Entity Registration', symbolSize: 24, itemStyle: { color: '#e6a23c' } },
        { name: 'VC Issuance', symbolSize: 24, itemStyle: { color: '#e6a23c' } },
        { name: 'VP Verification', symbolSize: 24, itemStyle: { color: '#e6a23c' } },
        { name: 'Permission Inheritance', symbolSize: 24, itemStyle: { color: '#e6a23c' } }
      ]
    },
    {
      name: '📡 IoT Digital Base',
      symbolSize: 32,
      itemStyle: { color: '#f56c6c' },
      children: [
        { name: 'MQTT Driver', symbolSize: 24, itemStyle: { color: '#ffaa44' } },
        { name: 'HTTP Driver', symbolSize: 24, itemStyle: { color: '#ffaa44' } },
        { name: 'Modbus Driver', symbolSize: 24, itemStyle: { color: '#ffaa44' } },
        { name: 'Field/Method Mapping', symbolSize: 24, itemStyle: { color: '#ffaa44' } }
      ]
    },
    {
      name: '📊 Data Modeling',
      symbolSize: 32,
      itemStyle: { color: '#909399' },
      children: [
        { name: 'XGBoost Training', symbolSize: 24, itemStyle: { color: '#00d4ff' } },
        { name: 'Energy Prediction', symbolSize: 24, itemStyle: { color: '#00d4ff' } },
        { name: 'CSV Storage', symbolSize: 24, itemStyle: { color: '#00d4ff' } },
        { name: 'Savings Simulation', symbolSize: 24, itemStyle: { color: '#00d4ff' } }
      ]
    },
    {
      name: '⛓️ Blockchain',
      symbolSize: 32,
      itemStyle: { color: '#00ff88' },
      children: [
        {
          name: 'Geth Private Chain',
          symbolSize: 28,
          itemStyle: { color: '#00ff88' },
          children: [
            { name: 'Node 1 (RPC:8545)', symbolSize: 22, itemStyle: { color: '#67c23a' } },
            { name: 'Node 2 (RPC:8546)', symbolSize: 22, itemStyle: { color: '#67c23a' } },
            { name: 'Node 3 (RPC:8547)', symbolSize: 22, itemStyle: { color: '#67c23a' } }
          ]
        },
        { name: 'IMBSAnchor Contract', symbolSize: 24, itemStyle: { color: '#ffaa44' } },
        { name: 'Mining Scheduler', symbolSize: 24, itemStyle: { color: '#ffaa44' } }
      ]
    },
    {
      name: '🌐 API Layer',
      symbolSize: 32,
      itemStyle: { color: '#e6a23c' },
      children: [
        { name: 'DID API (15)', symbolSize: 24, itemStyle: { color: '#67c23a' } },
        { name: 'IoT API (27)', symbolSize: 24, itemStyle: { color: '#f56c6c' } },
        { name: 'Modeling API (6)', symbolSize: 24, itemStyle: { color: '#00d4ff' } },
        { name: 'SSE Push', symbolSize: 24, itemStyle: { color: '#e6a23c' } }
      ]
    }
  ]
}

const chartContainer = ref<HTMLElement | null>(null)
let chart: echarts.ECharts | null = null

// Helper functions
const shortenAddress = (addr: string, len = 6) => {
  if (!addr) return ''
  return `${addr.slice(0, len)}...${addr.slice(-4)}`
}

// 初始化纵向树状图
const initTreeChart = () => {
  if (!chartContainer.value) return

  chart = echarts.init(chartContainer.value)

  const option = {
    tooltip: {
      trigger: 'item',
      triggerOn: 'mousemove',
      formatter: (params: any) => {
        return `<strong>${params.name}</strong>`
      },
      backgroundColor: 'rgba(50,50,50,0.9)',
      borderColor: '#00d4ff',
      borderWidth: 1,
      textStyle: { color: '#fff', fontSize: 11 }
    },
    series: [{
      type: 'tree',
      data: [treeData],
      left: '8%',
      right: '8%',
      top: '5%',
      bottom: '5%',
      symbol: 'circle',
      symbolSize: 16,
      orient: 'TB',  // 纵向布局：从上到下
      expandAndCollapse: true,
      initialTreeDepth: 2,
      lineStyle: {
        color: '#00d4ff',
        width: 1.5,
        curveness: 0.5,
        type: 'solid'
      },
      label: {
        position: 'bottom',
        verticalAlign: 'middle',
        align: 'center',
        fontSize: 10,
        fontWeight: '500',
        color: '#303133',
        offset: [0, 8]
      },
      leaves: {
        label: {
          position: 'bottom',
          verticalAlign: 'middle',
          align: 'center',
          offset: [0, 8]
        }
      },
      itemStyle: {
        borderColor: '#00d4ff',
        borderWidth: 1.5
      },
      emphasis: {
        focus: 'descendant',
        lineStyle: {
          color: '#00ff88',
          width: 2
        }
      },
      roam: true,
      animationDuration: 550,
      animationDurationUpdate: 750
    }]
  }

  chart.setOption(option)

  window.addEventListener('resize', () => {
    chart?.resize()
  })
}

// Simulate dynamic data updates
let updateInterval: ReturnType<typeof setInterval>

onMounted(() => {
  nextTick(() => {
    initTreeChart()
  })

  updateInterval = setInterval(() => {
    stats.value.chainHeight += Math.floor(Math.random() * 3) + 1
    stats.value.miningActive = !stats.value.miningActive
    setTimeout(() => {
      stats.value.miningActive = true
    }, 5000)
  }, 30000)
})

onUnmounted(() => {
  if (updateInterval) clearInterval(updateInterval)
  if (chart) {
    chart.dispose()
    chart = null
  }
})
</script>

<style scoped>
.web3-service-page {
  background: #f5f7fa;
  min-height: 100vh;
  padding: 20px;
}

/* Hero Section */
.hero-section {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
  border-radius: 16px;
  padding: 32px 24px;
  margin-bottom: 20px;
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
  gap: 8px;
  justify-content: center;
  flex-wrap: wrap;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 12px;
  margin-bottom: 20px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 14px 16px;
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
  border-radius: 12px;
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
.arch-card, .specs-card, .contracts-card, .api-card, .features-card, .records-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
}

:deep(.el-card__header) {
  padding: 12px 16px;
  border-bottom: 1px solid #e4e7ed;
  background: #fafafa;
}

:deep(.el-card__body) {
  padding: 16px;
}

.tree-chart-container {
  width: 100%;
  height: 460px;
  background: #ffffff;
}

/* Technical Specifications */
.specs-card :deep(.el-descriptions) {
  --el-descriptions-title-color: #303133;
}

.specs-card :deep(.el-descriptions__label) {
  width: 120px;
  background: #f5f7fa;
  font-size: 12px;
}

.specs-card :deep(.el-descriptions__content) {
  font-size: 12px;
}

/* API List */
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

/* Features Grid */
.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 16px;
}

.feature-item {
  text-align: center;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 10px;
  transition: all 0.2s;
}

.feature-item:hover {
  transform: translateY(-2px);
  background: #ecf5ff;
}

.feature-icon {
  font-size: 32px;
  margin-bottom: 8px;
}

.feature-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 6px;
}

.feature-desc {
  font-size: 11px;
  color: #909399;
  line-height: 1.4;
}

/* Table Styles */
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

/* Responsive */
@media (max-width: 768px) {
  .web3-service-page {
    padding: 12px;
  }

  .hero-section {
    padding: 24px 16px;
  }

  .hero-section h1 {
    font-size: 22px;
  }

  .subtitle {
    font-size: 12px;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
  }

  .stat-card {
    padding: 10px 12px;
  }

  .stat-value {
    font-size: 20px;
  }

  .features-grid {
    grid-template-columns: 1fr;
  }

  .api-endpoint {
    min-width: 120px;
    font-size: 10px;
  }

  .tree-chart-container {
    height: 380px;
  }
}
</style>