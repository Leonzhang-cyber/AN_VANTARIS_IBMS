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
    <el-row :gutter="24">
      <!-- Left Column: Architecture & Specs -->
      <el-col :xs="24" :md="12">
        <!-- Architecture Diagram -->
        <el-card class="arch-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>🏗️ System Architecture</span>
              <el-tag size="small" type="info">Clique PoA Consensus</el-tag>
            </div>
          </template>
          <div class="arch-diagram">
            <pre class="ascii-art">
┌─────────────────────────────────────────────────────────────┐
│                      Web3.0 Service Layer                    │
├─────────────────────────────────────────────────────────────┤
│   DID Service  │   VC Service   │   Anchor Service           │
├─────────────────────────────────────────────────────────────┤
│                 Blockchain Client (Web3.py)                  │
│                    RPC Connection Pool                       │
├─────────────────────────────────────────────────────────────┤
│              Geth Private Chain (3 Nodes)                    │
│            Clique PoA · Round-Robin Sealing                  │
│   Node1(RPC:8545)  Node2(RPC:8546)  Node3(RPC:8547)         │
└─────────────────────────────────────────────────────────────┘
            </pre>
            <div class="arch-note">
              <el-icon><Connection /></el-icon>
              <span>P2P Full-mesh · On-demand Mining · Auto-failover</span>
            </div>
          </div>
        </el-card>

        <!-- Technical Specifications -->
        <el-card class="specs-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>⚙️ Technical Specifications</span>
              <el-tag size="small" type="success">Production Ready</el-tag>
            </div>
          </template>
          <el-descriptions :column="1" border>
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

      <!-- Right Column: Contracts & API -->
      <el-col :xs="24" :md="12">
        <!-- Smart Contracts -->
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

        <!-- API Endpoints -->
        <el-card class="api-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>🔌 API Endpoints</span>
              <el-tag size="small" type="info">RESTful · JSON-RPC</el-tag>
            </div>
          </template>
          <el-table :data="apiEndpoints" stripe size="small">
            <el-table-column prop="method" label="Method" width="80">
              <template #default="{ row }">
                <el-tag :type="row.method === 'POST' ? 'success' : 'info'" size="small">{{ row.method }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="endpoint" label="Endpoint" />
            <el-table-column prop="description" label="Description" />
          </el-table>
        </el-card>

        <!-- Quick Start -->
        <el-card class="quickstart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>🚀 Quick Start</span>
              <el-tag size="small" type="success">Copy & Paste</el-tag>
            </div>
          </template>
          <div class="code-block">
            <pre><code># Connect to private chain RPC
export RPC_URL=http://your-server:8545

# Query chain status
curl -X POST $RPC_URL \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'

# Register a DID entity
curl -X POST /api/did/register \
  -H "Content-Type: application/json" \
  -d '{"entityId":"user123","publicKey":"0x..."}'</code></pre>
            <el-button size="small" text @click="copyCode">
              <el-icon><CopyDocument /></el-icon> Copy Code
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Features Section -->
    <el-card class="features-card" shadow="hover">
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
    <el-card class="records-card" shadow="hover">
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

    <!-- Footer -->
    <div class="footer">
      <p>© 2025 Web3.0 Technical Services | Private Blockchain · DID · Verifiable Credentials</p>
      <p class="version">Geth v1.13.15 | Clique PoA | Chain ID: 9527</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Connection, CopyDocument } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

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
  { method: 'POST', endpoint: '/api/did/register', description: 'Register a new DID entity' },
  { method: 'POST', endpoint: '/api/vc/issue', description: 'Issue a Verifiable Credential' },
  { method: 'POST', endpoint: '/api/vc/verify', description: 'Verify a Verifiable Credential' },
  { method: 'GET', endpoint: '/api/anchor/record', description: 'Query anchoring records' },
  { method: 'GET', endpoint: '/api/chain/status', description: 'Get blockchain status' },
  { method: 'POST', endpoint: '/api/contract/anchor', description: 'Anchor data hash to chain' },
])

// Anchoring records
const anchoringRecords = ref([
  { operation: 'DID Registration', entityId: 'did:example:alice123', txHash: '0x1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p', blockNumber: 124, timestamp: '2025-04-17 14:23:10' },
  { operation: 'VC Issuance', entityId: 'did:example:bob456', txHash: '0x2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q', blockNumber: 129, timestamp: '2025-04-17 14:25:30' },
  { operation: 'Entity Update', entityId: 'did:example:carol789', txHash: '0x3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r', blockNumber: 135, timestamp: '2025-04-17 14:28:15' },
  { operation: 'DID Registration', entityId: 'did:example:david012', txHash: '0x4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s', blockNumber: 142, timestamp: '2025-04-17 14:32:40' },
  { operation: 'Data Anchoring', entityId: 'document:hash:abc123', txHash: '0x5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t', blockNumber: 148, timestamp: '2025-04-17 14:36:20' },
])

// Helper functions
const shortenAddress = (addr: string, len = 6) => {
  if (!addr) return ''
  return `${addr.slice(0, len)}...${addr.slice(-4)}`
}

const copyCode = async () => {
  const code = `# Connect to private chain RPC
export RPC_URL=http://your-server:8545

# Query chain status
curl -X POST $RPC_URL \\
  -H "Content-Type: application/json" \\
  -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'

# Register a DID entity
curl -X POST /api/did/register \\
  -H "Content-Type: application/json" \\
  -d '{"entityId":"user123","publicKey":"0x..."}'`

  try {
    await navigator.clipboard.writeText(code)
    ElMessage.success('Code copied to clipboard!')
  } catch {
    ElMessage.error('Failed to copy')
  }
}

// Simulate dynamic data updates
let updateInterval: ReturnType<typeof setInterval>

onMounted(() => {
  // Simulate real-time stats updates
  updateInterval = setInterval(() => {
    stats.value.chainHeight += Math.floor(Math.random() * 3) + 1
    stats.value.miningActive = !stats.value.miningActive
    // Randomly toggle mining status for demo
    setTimeout(() => {
      stats.value.miningActive = true
    }, 5000)
  }, 30000)
})

// Cleanup
import { onUnmounted } from 'vue'
onUnmounted(() => {
  if (updateInterval) clearInterval(updateInterval)
})
</script>

<style scoped>
.web3-service-page {
  background: #f5f7fa;
  min-height: 100vh;
  padding: 24px;
}

/* Hero Section */
.hero-section {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
  border-radius: 20px;
  padding: 48px 32px;
  margin-bottom: 32px;
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
  margin-bottom: 20px;
}

.hex-bg {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #00d4ff, #00ff88);
  clip-path: polygon(25% 0%, 75% 0%, 100% 25%, 100% 75%, 75% 100%, 25% 100%, 0% 75%, 0% 25%);
  opacity: 0.3;
  position: absolute;
  top: 0;
  left: 0;
}

.hero-icon .icon {
  font-size: 40px;
  line-height: 80px;
  display: inline-block;
  width: 80px;
  position: relative;
  z-index: 1;
}

.hero-section h1 {
  font-size: 32px;
  font-weight: 700;
  color: #ffffff;
  margin-bottom: 12px;
  letter-spacing: 1px;
}

.subtitle {
  font-size: 16px;
  color: #a0aec0;
  margin-bottom: 20px;
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
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 16px;
  margin-bottom: 32px;
}

.stat-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  font-size: 32px;
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
  border-radius: 14px;
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
  font-size: 28px;
  font-weight: 700;
  color: #303133;
  line-height: 1.2;
}

.stat-value.active {
  color: #67c23a;
}

.stat-label {
  font-size: 12px;
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
}

/* Architecture Card */
.arch-card, .specs-card, .contracts-card, .api-card, .quickstart-card, .features-card, .records-card {
  margin-bottom: 24px;
}

.arch-diagram {
  text-align: center;
}

.ascii-art {
  font-family: monospace;
  font-size: 10px;
  background: #1a1e24;
  color: #6e8f6e;
  padding: 16px;
  border-radius: 8px;
  margin: 0 0 12px 0;
  text-align: left;
  line-height: 1.4;
  overflow-x: auto;
}

.arch-note {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 12px;
  color: #606266;
  padding-top: 8px;
  border-top: 1px solid #e4e7ed;
}

/* Code Block */
.code-block {
  background: #1a1e24;
  border-radius: 8px;
  padding: 16px;
  position: relative;
}

.code-block pre {
  margin: 0 0 12px 0;
  overflow-x: auto;
}

.code-block code {
  font-family: 'Courier New', 'Fira Code', monospace;
  font-size: 12px;
  color: #e2e8f0;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-all;
}

/* Features Grid */
.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}

.feature-item {
  text-align: center;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 12px;
  transition: all 0.2s;
}

.feature-item:hover {
  transform: translateY(-2px);
  background: #ecf5ff;
}

.feature-icon {
  font-size: 36px;
  margin-bottom: 12px;
}

.feature-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}

.feature-desc {
  font-size: 12px;
  color: #909399;
  line-height: 1.5;
}

/* Footer */
.footer {
  text-align: center;
  padding: 24px 0 16px;
  border-top: 1px solid #e4e7ed;
  margin-top: 16px;
}

.footer p {
  font-size: 12px;
  color: #909399;
  margin: 4px 0;
}

.version {
  font-family: monospace;
  font-size: 11px;
}

/* Responsive */
@media (max-width: 768px) {
  .web3-service-page {
    padding: 16px;
  }

  .hero-section {
    padding: 32px 20px;
  }

  .hero-section h1 {
    font-size: 24px;
  }

  .subtitle {
    font-size: 13px;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .features-grid {
    grid-template-columns: 1fr;
  }
}
</style>