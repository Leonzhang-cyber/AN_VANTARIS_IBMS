<template>
  <!-- Key Verification -->
  <div v-if="!isKeyVerified" class="key-verify-container">
    <div class="key-verify-card">
      <div class="key-verify-icon">🔐</div>
      <h2>Access Restricted</h2>
      <p>This page contains sensitive technical documentation.<br>Please enter the access key to continue.</p>
      <div class="key-input-wrapper">
        <el-input
            v-model="accessKey"
            type="password"
            placeholder="Enter access key"
            size="large"
            @keyup.enter="verifyKey"
            :disabled="keyVerifying"
            class="key-input"
        >
          <template #prefix>
            <el-icon><Lock /></el-icon>
          </template>
        </el-input>
        <el-button type="primary" size="large" @click="verifyKey" :loading="keyVerifying">
          <el-icon><Unlock /></el-icon> Verify Access
        </el-button>
      </div>
      <div v-if="keyError" class="key-error">
        <el-icon><CircleClose /></el-icon> Invalid access key. Please try again.
      </div>
    </div>
  </div>

  <!-- Loading Screen -->
  <div v-else-if="!isPageLoaded" class="loading-container">
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
        <div class="loading-tip">IBMS · Integrations & Web3 Introduction</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="introduction-page">
    <div class="page-container">
      <!-- Hero Section -->
      <div class="hero-section">
        <div class="hero-badge">📖 IBMS System Documentation</div>
        <h1>Integrations & Web3 Introduction</h1>
        <p class="hero-subtitle">Bridge the gap between traditional systems and blockchain technology</p>
        <div class="hero-stats">
          <div class="hero-stat"><span class="stat-number">67</span><span class="stat-label">Code Files</span></div>
          <div class="hero-stat"><span class="stat-number">48</span><span class="stat-label">API Endpoints</span></div>
          <div class="hero-stat"><span class="stat-number">6</span><span class="stat-label">Geth Nodes</span></div>
          <div class="hero-stat"><span class="stat-number">100%</span><span class="stat-label">On-Chain</span></div>
        </div>
      </div>

      <!-- 1. System Architecture -->
      <div class="section-card">
        <div class="section-header">
          <span class="section-icon">🏗️</span>
          <div>
            <h2>1. System Architecture Overview</h2>
            <p class="section-desc">Layered microservices architecture with decoupled components across 7 layers</p>
          </div>
          <el-tag size="small" type="success" style="margin-left: auto">7 Layers | 67 Files</el-tag>
        </div>
        <div class="topology-container" ref="archTopologyRef" style="height: 760px;">
          <VueFlow
              v-model="archNodes"
              v-model:edges="archEdges"
              class="vue-flow-wrapper"
              :default-viewport="{ zoom: 0.65, x: 80, y: 20 }"
              :fit-view-on-init="true"
              :nodes-draggable="true"
              :zoom-on-scroll="true"
              :min-zoom="0.4"
              :max-zoom="1.5"
          >
            <template #node-custom="nodeProps">
              <div class="arch-node" :style="{ borderColor: nodeProps.data.color, background: nodeProps.data.bg || '#ffffff' }">
                <div class="arch-node-icon">{{ nodeProps.data.icon }}</div>
                <div class="arch-node-name">{{ nodeProps.data.label }}</div>
                <div class="arch-node-desc">{{ nodeProps.data.desc }}</div>
                <div class="arch-node-tech">{{ nodeProps.data.tech }}</div>
              </div>
            </template>
          </VueFlow>
        </div>
      </div>

      <!-- 2. Blockchain Network Topology -->
      <div class="section-card">
        <div class="section-header">
          <span class="section-icon">⛓️</span>
          <div>
            <h2>2. Blockchain Network Topology</h2>
            <p class="section-desc">6-node Geth private chain cluster with Clique PoA consensus</p>
          </div>
          <el-tag size="small" type="danger" style="margin-left: auto">6-Node | Full-Mesh</el-tag>
        </div>
        <div class="topology-container" ref="blockchainTopologyRef" style="height: 520px;">
          <VueFlow
              v-model="blockchainNodes"
              v-model:edges="blockchainEdges"
              class="vue-flow-wrapper"
              :default-viewport="{ zoom: 0.7, x: 100, y: 50 }"
              :fit-view-on-init="true"
              :nodes-draggable="true"
              :zoom-on-scroll="true"
              :min-zoom="0.5"
              :max-zoom="1.5"
          >
            <template #node-custom="nodeProps">
              <div class="blockchain-node">
                <div class="node-icon">⛏️</div>
                <div class="node-name">{{ nodeProps.data.label }}</div>
                <div class="node-ports">RPC: {{ nodeProps.data.rpc }}<br>P2P: {{ nodeProps.data.p2p }}</div>
                <div class="node-status-badge online">● Online</div>
                <div class="node-balance">{{ nodeProps.data.balance }} ETH</div>
              </div>
            </template>
          </VueFlow>
        </div>
        <div class="blockchain-details">
          <div class="detail-item"><span class="detail-label">Consensus:</span><span>Clique (PoA) - Round-Robin Sealing</span></div>
          <div class="detail-item"><span class="detail-label">Chain ID:</span><span>9527</span></div>
          <div class="detail-item"><span class="detail-label">Block Interval:</span><span>5 seconds</span></div>
          <div class="detail-item"><span class="detail-label">Initial Supply:</span><span>600 ETH (100 ETH per signer)</span></div>
          <div class="detail-item"><span class="detail-label">Block Height:</span><span>1,247</span></div>
          <div class="detail-item"><span class="detail-label">Avg Gas Price:</span><span>1.2 Gwei</span></div>
        </div>
      </div>

      <!-- 3. DID + Blockchain Integration -->
      <div class="section-card">
        <div class="section-header">
          <span class="section-icon">🆔</span>
          <div>
            <h2>3. DID + Blockchain Integration</h2>
            <p class="section-desc">W3C-compliant decentralized identity with hierarchical DID and on-chain anchoring</p>
          </div>
          <el-tag size="small" type="primary" style="margin-left: auto">W3C Standard</el-tag>
        </div>
        <div class="topology-container" ref="didBlockchainTopologyRef" style="height: 480px;">
          <VueFlow
              v-model="didBlockchainNodes"
              v-model:edges="didBlockchainEdges"
              class="vue-flow-wrapper"
              :default-viewport="{ zoom: 0.7, x: 80, y: 40 }"
              :fit-view-on-init="true"
              :nodes-draggable="true"
              :zoom-on-scroll="true"
              :min-zoom="0.5"
              :max-zoom="1.5"
          >
            <template #node-custom="nodeProps">
              <div class="did-blockchain-node" :style="{ borderColor: nodeProps.data.color, background: nodeProps.data.bg || '#ffffff' }">
                <div class="node-icon">{{ nodeProps.data.icon }}</div>
                <div class="node-name">{{ nodeProps.data.label }}</div>
                <div class="node-desc">{{ nodeProps.data.desc }}</div>
              </div>
            </template>
          </VueFlow>
        </div>
        <div class="did-features">
          <div class="did-feature-item"><span class="did-feature-icon">📝</span>Hierarchical DID: <code>did:imbs:{type}:{id}:{suffix}</code></div>
          <div class="did-feature-item"><span class="did-feature-icon">🎫</span>VC Issuance · Verification · Revocation</div>
          <div class="did-feature-item"><span class="did-feature-icon">✅</span>VP Challenge-Response Authentication</div>
          <div class="did-feature-item"><span class="did-feature-icon">🔗</span>IMBSAnchor.sol Hash Anchoring</div>
        </div>
      </div>

      <!-- 4. Data Flow Pipeline -->
      <div class="section-card">
        <div class="section-header">
          <span class="section-icon">🌊</span>
          <div>
            <h2>4. Complete Data Flow Pipeline</h2>
            <p class="section-desc">End-to-end data flow from IoT devices to on-chain anchoring and real-time push</p>
          </div>
          <el-tag size="small" type="info" style="margin-left: auto">End-to-End Pipeline</el-tag>
        </div>
        <div class="topology-container" ref="dataFlowTopologyRef" style="height: 480px;">
          <VueFlow
              v-model="dataFlowNodes"
              v-model:edges="dataFlowEdges"
              class="vue-flow-wrapper"
              :default-viewport="{ zoom: 0.7, x: 60, y: 40 }"
              :fit-view-on-init="true"
              :nodes-draggable="true"
              :zoom-on-scroll="true"
              :min-zoom="0.5"
              :max-zoom="1.5"
          >
            <template #node-custom="nodeProps">
              <div class="dataflow-node" :style="{ background: nodeProps.data.color }">
                <div class="node-icon">{{ nodeProps.data.icon }}</div>
                <div class="node-name">{{ nodeProps.data.label }}</div>
                <div class="node-desc">{{ nodeProps.data.desc }}</div>
                <div class="node-tech">{{ nodeProps.data.tech }}</div>
              </div>
            </template>
          </VueFlow>
        </div>
        <div class="dataflow-stats">
          <div class="stat-item"><span>📡 Device Protocols:</span> MQTT · HTTP · Modbus</div>
          <div class="stat-item"><span>🔐 Auth Methods:</span> DID Auth · JWT · API Key</div>
          <div class="stat-item"><span>⛓️ Anchor Rate:</span> ~12 tx/hour</div>
          <div class="stat-item"><span>📨 Push Latency:</span> &lt; 500ms</div>
        </div>
      </div>

      <!-- 5. Mining Scheduler Workflow -->
      <div class="section-card">
        <div class="section-header">
          <span class="section-icon">⛏️</span>
          <div>
            <h2>5. Mining Scheduler Workflow</h2>
            <p class="section-desc">On-demand mining scheduler that starts on first write request and stops after idle timeout</p>
          </div>
          <el-tag size="small" type="warning" style="margin-left: auto">On-Demand Mining</el-tag>
        </div>
        <div class="topology-container" ref="miningSchedulerTopologyRef" style="height: 420px;">
          <VueFlow
              v-model="miningNodes"
              v-model:edges="miningEdges"
              class="vue-flow-wrapper"
              :default-viewport="{ zoom: 0.8, x: 80, y: 40 }"
              :fit-view-on-init="true"
              :nodes-draggable="true"
              :zoom-on-scroll="true"
              :min-zoom="0.5"
              :max-zoom="1.5"
          >
            <template #node-custom="nodeProps">
              <div class="mining-node" :class="nodeProps.data.type">
                <div class="node-icon">{{ nodeProps.data.icon }}</div>
                <div class="node-name">{{ nodeProps.data.label }}</div>
                <div class="node-desc">{{ nodeProps.data.desc }}</div>
              </div>
            </template>
          </VueFlow>
        </div>
        <div class="mining-stats">
          <div class="stat-card-mini"><span>⚡ Mining Trigger:</span> First write request</div>
          <div class="stat-card-mini"><span>⏰ Idle Timeout:</span> 10 minutes</div>
          <div class="stat-card-mini"><span>🔄 Scheduler Check:</span> Every 30 seconds</div>
          <div class="stat-card-mini"><span>💰 Energy Saved:</span> ~85%</div>
        </div>
      </div>

      <!-- 6. Module Dependency Graph -->
      <div class="section-card">
        <div class="section-header">
          <span class="section-icon">📦</span>
          <div>
            <h2>6. Module Dependency Graph</h2>
            <p class="section-desc">Dependency relationships between 5 core modules (67 source files)</p>
          </div>
          <el-tag size="small" type="info" style="margin-left: auto">67 Files | 5 Core Modules</el-tag>
        </div>
        <div class="topology-container" ref="dependencyTopologyRef" style="height: 480px;">
          <VueFlow
              v-model="dependencyNodes"
              v-model:edges="dependencyEdges"
              class="vue-flow-wrapper"
              :default-viewport="{ zoom: 0.7, x: 80, y: 40 }"
              :fit-view-on-init="true"
              :nodes-draggable="true"
              :zoom-on-scroll="true"
              :min-zoom="0.5"
              :max-zoom="1.5"
          >
            <template #node-custom="nodeProps">
              <div class="dependency-node" :style="{ borderColor: nodeProps.data.color, background: nodeProps.data.bg || '#ffffff' }">
                <div class="node-icon">{{ nodeProps.data.icon }}</div>
                <div class="node-name">{{ nodeProps.data.label }}</div>
                <div class="node-files">{{ nodeProps.data.files }} files</div>
                <div class="node-desc-small">{{ nodeProps.data.desc }}</div>
              </div>
            </template>
          </VueFlow>
        </div>
      </div>

      <!-- 7. Database Schema -->
      <div class="section-card">
        <div class="section-header">
          <span class="section-icon">🗄️</span>
          <div>
            <h2>7. Database Schema & ER Diagram</h2>
            <p class="section-desc">6 core tables supporting hierarchical relationships, permissions, and VC anchoring</p>
          </div>
          <el-tag size="small" type="success" style="margin-left: auto">6 Tables | MySQL 8.0</el-tag>
        </div>
        <div class="topology-container" ref="databaseTopologyRef" style="height: 580px;">
          <VueFlow
              v-model="databaseNodes"
              v-model:edges="databaseEdges"
              class="vue-flow-wrapper"
              :default-viewport="{ zoom: 0.65, x: 100, y: 40 }"
              :fit-view-on-init="true"
              :nodes-draggable="true"
              :zoom-on-scroll="true"
              :min-zoom="0.5"
              :max-zoom="1.5"
          >
            <template #node-custom="nodeProps">
              <div class="database-node">
                <div class="db-icon">🗄️</div>
                <div class="db-name">{{ nodeProps.data.label }}</div>
                <div class="db-fields">{{ nodeProps.data.fields }}</div>
                <div class="db-records">{{ nodeProps.data.records }} records</div>
              </div>
            </template>
          </VueFlow>
        </div>
        <div class="table-stats">
          <div class="table-stat"><span>imbs_entity_type:</span> 6 types</div>
          <div class="table-stat"><span>imbs_permission:</span> 24 permissions</div>
          <div class="table-stat"><span>imbs_users:</span> 50+ entities</div>
          <div class="table-stat"><span>imbs_vc_anchor:</span> 89 anchors</div>
        </div>
      </div>

      <!-- 8. API Gateway & Rate Limiting -->
      <div class="section-card">
        <div class="section-header">
          <span class="section-icon">🌐</span>
          <div>
            <h2>8. API Gateway & Rate Limiting</h2>
            <p class="section-desc">Unified API gateway with authentication, rate limiting, and request routing</p>
          </div>
          <el-tag size="small" type="info" style="margin-left: auto">48 Endpoints</el-tag>
        </div>
        <div class="topology-container" ref="apiGatewayTopologyRef" style="height: 460px;">
          <VueFlow
              v-model="apiGatewayNodes"
              v-model:edges="apiGatewayEdges"
              class="vue-flow-wrapper"
              :default-viewport="{ zoom: 0.7, x: 80, y: 40 }"
              :fit-view-on-init="true"
              :nodes-draggable="true"
              :zoom-on-scroll="true"
              :min-zoom="0.5"
              :max-zoom="1.5"
          >
            <template #node-custom="nodeProps">
              <div class="api-node" :style="{ background: nodeProps.data.color }">
                <div class="api-icon">{{ nodeProps.data.icon }}</div>
                <div class="api-name">{{ nodeProps.data.label }}</div>
                <div class="api-count">{{ nodeProps.data.count }} endpoints</div>
              </div>
            </template>
          </VueFlow>
        </div>
      </div>

      <!-- 9. Pluggable Driver Architecture -->
      <div class="section-card">
        <div class="section-header">
          <span class="section-icon">🔌</span>
          <div>
            <h2>9. Pluggable Driver Architecture</h2>
            <p class="section-desc">Plugin-based driver architecture supporting multiple IoT protocols</p>
          </div>
          <el-tag size="small" type="warning" style="margin-left: auto">3+ Protocols</el-tag>
        </div>
        <div class="topology-container" ref="driverTopologyRef" style="height: 440px;">
          <VueFlow
              v-model="driverNodes"
              v-model:edges="driverEdges"
              class="vue-flow-wrapper"
              :default-viewport="{ zoom: 0.7, x: 80, y: 40 }"
              :fit-view-on-init="true"
              :nodes-draggable="true"
              :zoom-on-scroll="true"
              :min-zoom="0.5"
              :max-zoom="1.5"
          >
            <template #node-custom="nodeProps">
              <div class="driver-node" :style="{ borderColor: nodeProps.data.color, background: nodeProps.data.bg || '#ffffff' }">
                <div class="driver-icon">{{ nodeProps.data.icon }}</div>
                <div class="driver-name">{{ nodeProps.data.label }}</div>
                <div class="driver-status">{{ nodeProps.data.status }}</div>
              </div>
            </template>
          </VueFlow>
        </div>
        <div class="field-mapping-table">
          <div class="table-title">📋 Field Mapping Example (HVAC Device)</div>
          <el-table :data="fieldMappingData" size="small" border stripe>
            <el-table-column prop="deviceField" label="Device Field" />
            <el-table-column prop="deviceValue" label="Device Value" />
            <el-table-column prop="standardField" label="Standard Field" />
            <el-table-column prop="standardValue" label="Standard Value" />
          </el-table>
        </div>
      </div>

      <!-- 10. XGBoost Data Modeling -->
      <div class="section-card">
        <div class="section-header">
          <span class="section-icon">🤖</span>
          <div>
            <h2>10. XGBoost Data Modeling</h2>
            <p class="section-desc">Energy consumption prediction using XGBoost machine learning model</p>
          </div>
          <el-tag size="small" type="success" style="margin-left: auto">Energy Prediction</el-tag>
        </div>
        <div class="topology-container" ref="modelingTopologyRef" style="height: 400px;">
          <VueFlow
              v-model="modelingNodes"
              v-model:edges="modelingEdges"
              class="vue-flow-wrapper"
              :default-viewport="{ zoom: 0.7, x: 80, y: 40 }"
              :fit-view-on-init="true"
              :nodes-draggable="true"
              :zoom-on-scroll="true"
              :min-zoom="0.5"
              :max-zoom="1.5"
          >
            <template #node-custom="nodeProps">
              <div class="modeling-node" :style="{ background: nodeProps.data.color }">
                <div class="node-icon">{{ nodeProps.data.icon }}</div>
                <div class="node-name">{{ nodeProps.data.label }}</div>
              </div>
            </template>
          </VueFlow>
        </div>
        <div class="prediction-table">
          <div class="table-title">📊 Energy Prediction Results (Next 7 Days)</div>
          <el-table :data="predictionData" size="small" border stripe>
            <el-table-column prop="date" label="Date" width="120" />
            <el-table-column prop="predicted" label="Predicted (kWh)" />
            <el-table-column prop="baseline" label="Baseline (kWh)" />
            <el-table-column prop="savings" label="Savings (kWh)" />
            <el-table-column prop="savingsPercent" label="Savings %" />
          </el-table>
        </div>
      </div>

      <!-- Core Concepts -->
      <div class="section-card">
        <div class="section-header">
          <span class="section-icon">🧠</span>
          <div><h2>Core Concepts</h2><p class="section-desc">Click cards to navigate to management pages</p></div>
          <el-tag size="small" type="info" style="margin-left: auto">Click to navigate</el-tag>
        </div>
        <div class="concepts-grid">
          <div v-for="concept in coreConcepts" :key="concept.name" class="concept-card" @click="navigateTo(concept.route)">
            <div class="concept-icon" :style="{ background: concept.color }">{{ concept.icon }}</div>
            <div class="concept-info">
              <h3>{{ concept.name }}</h3>
              <p>{{ concept.description }}</p>
              <span class="concept-link">Manage →</span>
            </div>
          </div>
        </div>
      </div>

      <!-- FAQ Section -->
      <div class="section-card">
        <div class="section-header">
          <span class="section-icon">❓</span>
          <div><h2>Frequently Asked Questions</h2></div>
        </div>
        <el-collapse v-model="activeFaq" accordion>
          <el-collapse-item v-for="faq in faqItems" :key="faq.question" :name="faq.question">
            <template #title><div class="faq-title">{{ faq.question }}</div></template>
            <div class="faq-answer">{{ faq.answer }}</div>
          </el-collapse-item>
        </el-collapse>
      </div>

      <!-- Submit Feedback -->
      <div class="feedback-card">
        <div class="feedback-icon">💬</div>
        <div class="feedback-content">
          <h3>Help Us Improve</h3>
          <p>Your feedback helps us make the documentation better.</p>
          <el-button type="primary" @click="showFeedbackDialog = true"><el-icon><Edit /></el-icon> Submit Feedback</el-button>
        </div>
      </div>
    </div>

    <!-- Feedback Dialog -->
    <el-dialog v-model="showFeedbackDialog" title="Submit Feedback" width="500px">
      <el-form :model="feedbackForm" label-width="80px">
        <el-form-item label="Title" required>
          <el-input v-model="feedbackForm.title" placeholder="Brief summary" />
        </el-form-item>
        <el-form-item label="Description" required>
          <el-input v-model="feedbackForm.description" type="textarea" rows="4" placeholder="Please describe in detail" />
        </el-form-item>
        <el-form-item label="Screenshot">
          <el-upload action="#" :auto-upload="false" :show-file-list="true" :limit="1">
            <el-button size="small"><el-icon><Upload /></el-icon> Upload Screenshot</el-button>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showFeedbackDialog = false">Cancel</el-button>
        <el-button type="primary" @click="submitFeedback">Submit</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { VueFlow } from '@vue-flow/core'
import type { Node, Edge } from '@vue-flow/core'
import '@vue-flow/core/dist/style.css'
import '@vue-flow/core/dist/theme-default.css'
import { ElMessage } from 'element-plus'
import { Lock, Unlock, CircleClose, Edit, Upload } from '@element-plus/icons-vue'

// ==================== Key Verification ====================
const REQUIRED_KEY = 'Leon88509998'
const isKeyVerified = ref(false)
const accessKey = ref('')
const keyVerifying = ref(false)
const keyError = ref(false)

const verifyKey = () => {
  if (!accessKey.value.trim()) { keyError.value = true; return }
  keyVerifying.value = true
  setTimeout(() => {
    if (accessKey.value === REQUIRED_KEY) {
      isKeyVerified.value = true
      keyError.value = false
      startLoading()
    } else {
      keyError.value = true
      accessKey.value = ''
    }
    keyVerifying.value = false
  }, 500)
}

// ==================== Loading ====================
const isPageLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing documentation...')
const loadingMessages = ['Preparing documentation...', 'Loading architecture diagrams...', 'Initializing topology graphs...', 'Gathering technical data...', 'Almost ready...']

// ==================== Table Data ====================
const fieldMappingData = ref([
  { deviceField: 'temp', deviceValue: '23.5', standardField: 'temperature', standardValue: '23.5' },
  { deviceField: 'hmt', deviceValue: '56', standardField: 'humidity', standardValue: '56' },
  { deviceField: 'pwr', deviceValue: '1250', standardField: 'power_consumption', standardValue: '1250' },
  { deviceField: 'stat', deviceValue: '1', standardField: 'device_status', standardValue: 'running' }
])

const predictionData = ref([
  { date: '2025-05-22', predicted: 12450, baseline: 13800, savings: 1350, savingsPercent: '9.8%' },
  { date: '2025-05-23', predicted: 11890, baseline: 13200, savings: 1310, savingsPercent: '9.9%' },
  { date: '2025-05-24', predicted: 11230, baseline: 12500, savings: 1270, savingsPercent: '10.2%' },
  { date: '2025-05-25', predicted: 10870, baseline: 12100, savings: 1230, savingsPercent: '10.2%' },
  { date: '2025-05-26', predicted: 11560, baseline: 12800, savings: 1240, savingsPercent: '9.7%' },
  { date: '2025-05-27', predicted: 12180, baseline: 13500, savings: 1320, savingsPercent: '9.8%' },
  { date: '2025-05-28', predicted: 12740, baseline: 14100, savings: 1360, savingsPercent: '9.6%' }
])

// ==================== Core Concepts ====================
const coreConcepts = ref([
  { name: 'DID (Decentralized Identity)', icon: '🆔', color: '#3b82f6', description: 'Hierarchical DID: did:imbs:{type}:{id}:{suffix}', route: '/did-management' },
  { name: 'Smart Contracts', icon: '📜', color: '#8b5cf6', description: 'IMBSAnchor.sol for data anchoring', route: '/smart-contracts' },
  { name: 'Data Anchoring', icon: '🔗', color: '#10b981', description: 'SHA256 hash stored on-chain', route: '/data-anchoring' },
  { name: 'Edge Nodes', icon: '⚡', color: '#f59e0b', description: '6 edge gateways in Singapore & Hong Kong', route: '/edge-nodes' },
  { name: 'Geth Private Chain', icon: '⛓️', color: '#ef4444', description: '6-node cluster, Chain ID 9527', route: '/blockchain-dashboard' },
  { name: 'Verifiable Credentials', icon: '🎫', color: '#06b6d4', description: 'VC issuance, verification, revocation', route: '/did-management' }
])

// ==================== FAQ ====================
const activeFaq = ref('')
const faqItems = ref([
  { question: 'How do I verify that my data has not been tampered with?', answer: 'Use the Verification Tool in the Data Anchoring page. The system will compare the computed hash with the on-chain stored hash via IMBSAnchor.sol contract.' },
  { question: 'What happens when an edge node goes offline?', answer: 'It continues to collect data locally using configured drivers (MQTT/HTTP/Modbus). Once restored, it automatically syncs cached data with retry mechanism (up to 3 retries).' },
  { question: 'How can I call the APIs from my application?', answer: 'Register an application to obtain Client ID and Secret, then generate an API key. Use it in the `X-API-Key` header of your HTTP requests.' },
  { question: 'What is the difference between DID and VC?', answer: 'DID is a unique identifier for an entity. VC is a cryptographically signed credential issued by one DID to another, proving claims about the subject.' },
  { question: 'How many nodes does the private chain have?', answer: '6 Geth nodes in full-mesh topology with Clique PoA consensus. All 6 are signers in round-robin block sealing (5-second interval).' },
  { question: 'What is the mining scheduler?', answer: 'On-demand mining: starts on first write request, automatically stops after 10 minutes idle to save resources.' }
])

const showFeedbackDialog = ref(false)
const feedbackForm = ref({ title: '', description: '' })

const submitFeedback = () => {
  if (!feedbackForm.value.title || !feedbackForm.value.description) {
    ElMessage.warning('Please fill in all fields')
    return
  }
  ElMessage.success('Thank you for your feedback!')
  showFeedbackDialog.value = false
  feedbackForm.value = { title: '', description: '' }
}

const navigateTo = (route: string) => {
  ElMessage.info(`Navigate to: ${route}`)
}

// ==================== Generate Full Mesh Edges Helper ====================
const generateFullMeshEdges = (ids: string[]): Edge[] => {
  const edges: Edge[] = []
  for (let i = 0; i < ids.length; i++) {
    for (let j = i + 1; j < ids.length; j++) {
      edges.push({
        id: `${ids[i]}-${ids[j]}`,
        source: ids[i],
        target: ids[j],
        animated: true,
        style: { stroke: '#52c41a', strokeWidth: 2 }
      })
    }
  }
  return edges
}

// ==================== 1. System Architecture ====================
const archNodes = ref<Node[]>([
  { id: 'app', type: 'custom', position: { x: 500, y: 30 }, data: { label: 'Application Layer', icon: '📱', desc: 'Frontend · Third-party', tech: 'Vue 3 / React', color: '#3b82f6', bg: '#eff6ff' } },
  { id: 'api', type: 'custom', position: { x: 250, y: 130 }, data: { label: 'API Gateway', icon: '🚪', desc: 'Entry · Rate Limit', tech: 'Flask · Nginx', color: '#8b5cf6', bg: '#f5f3ff' } },
  { id: 'sse', type: 'custom', position: { x: 750, y: 130 }, data: { label: 'SSE Push', icon: '📨', desc: 'Real-time Push', tech: 'Server-Sent Events', color: '#06b6d4', bg: '#ecfeff' } },
  { id: 'service', type: 'custom', position: { x: 500, y: 160 }, data: { label: 'Service Layer', icon: '⚙️', desc: 'DID · IoT · Modeling', tech: 'Python Services', color: '#f59e0b', bg: '#fffbeb' } },
  { id: 'core', type: 'custom', position: { x: 500, y: 280 }, data: { label: 'Core Layer', icon: '🔧', desc: 'Drivers · Mapping', tech: 'Plugin Architecture', color: '#10b981', bg: '#ecfdf5' } },
  { id: 'data', type: 'custom', position: { x: 300, y: 400 }, data: { label: 'Data Layer', icon: '💾', desc: 'MySQL · CSV', tech: 'SQLAlchemy', color: '#3b82f6', bg: '#eff6ff' } },
  { id: 'blockchain', type: 'custom', position: { x: 700, y: 400 }, data: { label: 'Blockchain Layer', icon: '⛓️', desc: '6 Geth Nodes', tech: 'Web3.py', color: '#ef4444', bg: '#fef2f2' } },
  { id: 'device', type: 'custom', position: { x: 500, y: 520 }, data: { label: 'Device Layer', icon: '📡', desc: 'MQTT · HTTP', tech: 'IoT Devices', color: '#64748b', bg: '#f8fafc' } }
])

const archEdges = ref<Edge[]>([
  { id: 'e1', source: 'app', target: 'api', animated: true, label: 'HTTP/HTTPS', style: { stroke: '#3b82f6' } },
  { id: 'e2', source: 'app', target: 'sse', animated: true, label: 'SSE', style: { stroke: '#06b6d4' } },
  { id: 'e3', source: 'api', target: 'service', animated: true, label: 'REST API', style: { stroke: '#8b5cf6' } },
  { id: 'e4', source: 'sse', target: 'service', animated: true, label: 'Subscribe', style: { stroke: '#06b6d4' } },
  { id: 'e5', source: 'service', target: 'core', animated: true, label: 'Call', style: { stroke: '#f59e0b' } },
  { id: 'e6', source: 'core', target: 'data', animated: true, label: 'CRUD', style: { stroke: '#10b981' } },
  { id: 'e7', source: 'core', target: 'blockchain', animated: true, label: 'RPC', style: { stroke: '#ef4444' } },
  { id: 'e8', source: 'device', target: 'core', animated: true, label: 'MQTT/HTTP', style: { stroke: '#64748b' } }
])

// ==================== 2. Blockchain Network ====================
const blockchainNodes = ref<Node[]>([
  { id: 'n1', type: 'custom', position: { x: 250, y: 100 }, data: { label: 'Geth Node 1', rpc: '8545', p2p: '30303', balance: '98.5' } },
  { id: 'n2', type: 'custom', position: { x: 450, y: 50 }, data: { label: 'Geth Node 2', rpc: '8546', p2p: '30304', balance: '97.2' } },
  { id: 'n3', type: 'custom', position: { x: 650, y: 100 }, data: { label: 'Geth Node 3', rpc: '8547', p2p: '30305', balance: '99.1' } },
  { id: 'n4', type: 'custom', position: { x: 650, y: 280 }, data: { label: 'Geth Node 4', rpc: '8548', p2p: '30306', balance: '96.8' } },
  { id: 'n5', type: 'custom', position: { x: 450, y: 330 }, data: { label: 'Geth Node 5', rpc: '8549', p2p: '30307', balance: '98.0' } },
  { id: 'n6', type: 'custom', position: { x: 250, y: 280 }, data: { label: 'Geth Node 6', rpc: '8550', p2p: '30308', balance: '97.5' } }
])
const blockchainEdges = ref<Edge[]>(generateFullMeshEdges(['n1', 'n2', 'n3', 'n4', 'n5', 'n6']))

// ==================== 3. DID + Blockchain Integration ====================
const didBlockchainNodes = ref<Node[]>([
  { id: 'entity', type: 'custom', position: { x: 150, y: 100 }, data: { label: 'Entity', icon: '👤', desc: 'User/Device/Org', color: '#f59e0b', bg: '#fffbeb' } },
  { id: 'did', type: 'custom', position: { x: 380, y: 80 }, data: { label: 'DID Registry', icon: '🆔', desc: 'DID Registration', color: '#3b82f6', bg: '#eff6ff' } },
  { id: 'vc', type: 'custom', position: { x: 600, y: 80 }, data: { label: 'VC Manager', icon: '📜', desc: 'Issue/Verify VC', color: '#8b5cf6', bg: '#f5f3ff' } },
  { id: 'vp', type: 'custom', position: { x: 380, y: 220 }, data: { label: 'VP Verifier', icon: '✅', desc: 'Presentation Verify', color: '#10b981', bg: '#ecfdf5' } },
  { id: 'anchor', type: 'custom', position: { x: 600, y: 220 }, data: { label: 'IMBSAnchor', icon: '🔗', desc: 'Hash Anchoring', color: '#ef4444', bg: '#fef2f2' } },
  { id: 'chain', type: 'custom', position: { x: 780, y: 150 }, data: { label: 'Geth Chain', icon: '⛓️', desc: '6 Nodes PoA', color: '#64748b', bg: '#f8fafc' } }
])

const didBlockchainEdges = ref<Edge[]>([
  { id: 'e1', source: 'entity', target: 'did', label: 'Register', animated: true, style: { stroke: '#f59e0b' } },
  { id: 'e2', source: 'did', target: 'vc', label: 'Issue', animated: true, style: { stroke: '#3b82f6' } },
  { id: 'e3', source: 'did', target: 'vp', label: 'Challenge', animated: true, style: { stroke: '#10b981' } },
  { id: 'e4', source: 'vc', target: 'anchor', label: 'Anchor Hash', animated: true, style: { stroke: '#8b5cf6' } },
  { id: 'e5', source: 'anchor', target: 'chain', label: 'Store', style: { stroke: '#ef4444' } }
])

// ==================== 4. Data Flow Pipeline ====================
const dataFlowNodes = ref<Node[]>([
  { id: 'iot', type: 'custom', position: { x: 80, y: 100 }, data: { label: 'IoT Device', icon: '📡', desc: 'Data Source', tech: 'MQTT/HTTP', color: '#3b82f6' } },
  { id: 'auth', type: 'custom', position: { x: 240, y: 100 }, data: { label: 'DID Auth', icon: '🔐', desc: 'Identity Verify', tech: 'DID/JWT', color: '#8b5cf6' } },
  { id: 'mapping', type: 'custom', position: { x: 400, y: 100 }, data: { label: 'Field Map', icon: '🗺️', desc: 'Data Normalize', tech: 'Mapper', color: '#f59e0b' } },
  { id: 'anchor', type: 'custom', position: { x: 560, y: 100 }, data: { label: 'On-Chain', icon: '⛓️', desc: 'Hash Store', tech: 'Web3.py', color: '#10b981' } },
  { id: 'csv', type: 'custom', position: { x: 720, y: 100 }, data: { label: 'Data Store', icon: '💾', desc: 'Time Series', tech: 'Pandas', color: '#ef4444' } },
  { id: 'sse', type: 'custom', position: { x: 880, y: 100 }, data: { label: 'SSE/API', icon: '📨', desc: 'Real-time Push', tech: 'EventStream', color: '#06b6d4' } }
])

const dataFlowEdges = ref<Edge[]>([
  { id: 'e1', source: 'iot', target: 'auth', animated: true, label: 'Auth' },
  { id: 'e2', source: 'auth', target: 'mapping', animated: true, label: 'Process' },
  { id: 'e3', source: 'mapping', target: 'anchor', animated: true, label: 'Anchor' },
  { id: 'e4', source: 'anchor', target: 'csv', animated: true, label: 'Store' },
  { id: 'e5', source: 'csv', target: 'sse', animated: true, label: 'Push' }
])

// ==================== 5. Mining Scheduler ====================
const miningNodes = ref<Node[]>([
  { id: 'idle', type: 'custom', position: { x: 120, y: 100 }, data: { label: 'Idle State', icon: '⏰', desc: 'Mining Stopped', type: 'idle' } },
  { id: 'write', type: 'custom', position: { x: 320, y: 100 }, data: { label: 'Write Request', icon: '📝', desc: 'DID/VC/Anchor', type: 'trigger' } },
  { id: 'mining', type: 'custom', position: { x: 520, y: 100 }, data: { label: 'Mining Active', icon: '⛏️', desc: 'Block Sealing', type: 'active' } },
  { id: 'timer', type: 'custom', position: { x: 520, y: 250 }, data: { label: 'Idle Timer', icon: '⏱️', desc: '10 min countdown', type: 'timer' } }
])

const miningEdges = ref<Edge[]>([
  { id: 'e1', source: 'idle', target: 'write', label: 'Trigger', animated: true, style: { stroke: '#f59e0b' } },
  { id: 'e2', source: 'write', target: 'mining', label: 'Start', animated: true, style: { stroke: '#52c41a' } },
  { id: 'e3', source: 'mining', target: 'timer', label: 'Reset', style: { stroke: '#3b82f6' } },
  { id: 'e4', source: 'timer', target: 'idle', label: 'Timeout → Stop', animated: true, style: { stroke: '#ef4444' } }
])

// ==================== 6. Module Dependency ====================
const dependencyNodes = ref<Node[]>([
  { id: 'did', type: 'custom', position: { x: 150, y: 100 }, data: { label: 'DID Module', icon: '🆔', files: '7', desc: 'Identity Management', color: '#3b82f6', bg: '#eff6ff' } },
  { id: 'iot', type: 'custom', position: { x: 350, y: 100 }, data: { label: 'IoT Module', icon: '📡', files: '18', desc: 'Device Management', color: '#8b5cf6', bg: '#f5f3ff' } },
  { id: 'model', type: 'custom', position: { x: 550, y: 100 }, data: { label: 'Modeling', icon: '📊', files: '8', desc: 'XGBoost', color: '#f59e0b', bg: '#fffbeb' } },
  { id: 'blockchain', type: 'custom', position: { x: 350, y: 250 }, data: { label: 'Blockchain', icon: '⛓️', files: '9', desc: 'Web3.py', color: '#ef4444', bg: '#fef2f2' } },
  { id: 'common', type: 'custom', position: { x: 150, y: 250 }, data: { label: 'Common', icon: '🔧', files: '8', desc: 'Config/DB', color: '#10b981', bg: '#ecfdf5' } }
])

const dependencyEdges = ref<Edge[]>([
  { id: 'e1', source: 'did', target: 'blockchain', animated: true },
  { id: 'e2', source: 'iot', target: 'blockchain', animated: true },
  { id: 'e3', source: 'model', target: 'iot', animated: true },
  { id: 'e4', source: 'did', target: 'common', animated: true },
  { id: 'e5', source: 'iot', target: 'common', animated: true },
  { id: 'e6', source: 'blockchain', target: 'common', animated: true }
])

// ==================== 7. Database Schema ====================
const databaseNodes = ref<Node[]>([
  { id: 't1', type: 'custom', position: { x: 150, y: 80 }, data: { label: 'imbs_entity_type', fields: 'type_code, type_name', records: '6' } },
  { id: 't2', type: 'custom', position: { x: 450, y: 80 }, data: { label: 'imbs_permission', fields: 'perm_code, desc', records: '24' } },
  { id: 't3', type: 'custom', position: { x: 300, y: 200 }, data: { label: 'imbs_relationship', fields: 'parent_did, child_did', records: '120' } },
  { id: 't4', type: 'custom', position: { x: 150, y: 320 }, data: { label: 'imbs_users', fields: 'did, name, pubkey', records: '52' } },
  { id: 't5', type: 'custom', position: { x: 450, y: 320 }, data: { label: 'imbs_vc_anchor', fields: 'vc_id, vc_hash', records: '89' } },
  { id: 't6', type: 'custom', position: { x: 300, y: 440 }, data: { label: 'imbs_vc_revocation', fields: 'vc_id, revoked_by', records: '3' } }
])

const databaseEdges = ref<Edge[]>([
  // entity_type → users (类型关联)
  { id: 'e1', source: 't1', target: 't4', label: 'entity_type_id', animated: true, style: { stroke: '#3b82f6' } },
  // users → relationship (层级关系)
  { id: 'e2', source: 't4', target: 't3', label: 'parent_did/child_did', style: { stroke: '#8b5cf6' } },
  // users → vc_anchor (VC持有者)
  { id: 'e3', source: 't4', target: 't5', label: 'subject_did', style: { stroke: '#f59e0b' } },
  // users → permission (权限关联 - 通过 permission_codes JSON字段)
  { id: 'e4', source: 't4', target: 't2', label: 'permission_codes → perm_code', style: { stroke: '#10b981', type: 'dashed' } },
  // vc_anchor → vc_revocation (撤销记录)
  { id: 'e5', source: 't5', target: 't6', label: 'vc_id', style: { stroke: '#ef4444' } }
])

// ==================== 8. API Gateway ====================
const apiGatewayNodes = ref<Node[]>([
  { id: 'client', type: 'custom', position: { x: 120, y: 100 }, data: { label: 'Client', icon: '🌐', count: '-', color: '#8b5cf6' } },
  { id: 'gateway', type: 'custom', position: { x: 300, y: 100 }, data: { label: 'API Gateway', icon: '🚪', count: '-', color: '#3b82f6' } },
  { id: 'did', type: 'custom', position: { x: 120, y: 250 }, data: { label: 'DID API', icon: '🆔', count: '15', color: '#10b981' } },
  { id: 'iot', type: 'custom', position: { x: 300, y: 250 }, data: { label: 'IoT API', icon: '📡', count: '27', color: '#f59e0b' } },
  { id: 'model', type: 'custom', position: { x: 480, y: 250 }, data: { label: 'Modeling API', icon: '📊', count: '6', color: '#ef4444' } },
  { id: 'sse', type: 'custom', position: { x: 480, y: 100 }, data: { label: 'SSE Stream', icon: '📨', count: '-', color: '#06b6d4' } }
])

const apiGatewayEdges = ref<Edge[]>([
  { id: 'e1', source: 'client', target: 'gateway', animated: true, label: 'Request' },
  { id: 'e2', source: 'gateway', target: 'did', animated: true, label: 'Route' },
  { id: 'e3', source: 'gateway', target: 'iot', animated: true, label: 'Route' },
  { id: 'e4', source: 'gateway', target: 'model', animated: true, label: 'Route' },
  { id: 'e5', source: 'gateway', target: 'sse', animated: true, label: 'Stream' }
])

// ==================== 9. Driver Architecture ====================
const driverNodes = ref<Node[]>([
  { id: 'registry', type: 'custom', position: { x: 300, y: 100 }, data: { label: 'Driver Registry', icon: '⚙️', status: 'Active', color: '#3b82f6', bg: '#eff6ff' } },
  { id: 'mqtt', type: 'custom', position: { x: 100, y: 250 }, data: { label: 'MQTT Driver', icon: '📨', status: 'Connected', color: '#10b981', bg: '#ecfdf5' } },
  { id: 'http', type: 'custom', position: { x: 300, y: 250 }, data: { label: 'HTTP Driver', icon: '🌐', status: 'Connected', color: '#f59e0b', bg: '#fffbeb' } },
  { id: 'modbus', type: 'custom', position: { x: 500, y: 250 }, data: { label: 'Modbus Driver', icon: '🔧', status: 'Standby', color: '#ef4444', bg: '#fef2f2' } },
  { id: 'field', type: 'custom', position: { x: 300, y: 400 }, data: { label: 'Field Mapping', icon: '🗺️', status: 'Active', color: '#8b5cf6', bg: '#f5f3ff' } }
])

const driverEdges = ref<Edge[]>([
  { id: 'e1', source: 'registry', target: 'mqtt', animated: true },
  { id: 'e2', source: 'registry', target: 'http', animated: true },
  { id: 'e3', source: 'registry', target: 'modbus', animated: true },
  { id: 'e4', source: 'mqtt', target: 'field', animated: true },
  { id: 'e5', source: 'http', target: 'field', animated: true },
  { id: 'e6', source: 'modbus', target: 'field', animated: true }
])

// ==================== 10. XGBoost Modeling ====================
const modelingNodes = ref<Node[]>([
  { id: 'csv', type: 'custom', position: { x: 100, y: 100 }, data: { label: 'CSV Data', icon: '📊', color: '#3b82f6' } },
  { id: 'preprocess', type: 'custom', position: { x: 280, y: 100 }, data: { label: 'Preprocess', icon: '🔄', color: '#8b5cf6' } },
  { id: 'train', type: 'custom', position: { x: 460, y: 100 }, data: { label: 'XGBoost Train', icon: '🤖', color: '#f59e0b' } },
  { id: 'predict', type: 'custom', position: { x: 640, y: 100 }, data: { label: 'Predict', icon: '⚡', color: '#10b981' } },
  { id: 'saving', type: 'custom', position: { x: 820, y: 100 }, data: { label: 'Savings', icon: '💰', color: '#ef4444' } }
])

const modelingEdges = ref<Edge[]>([
  { id: 'e1', source: 'csv', target: 'preprocess', animated: true },
  { id: 'e2', source: 'preprocess', target: 'train', animated: true },
  { id: 'e3', source: 'train', target: 'predict', animated: true },
  { id: 'e4', source: 'predict', target: 'saving', animated: true }
])

// ==================== Loading Animation ====================
const startLoading = () => {
  let progress = 0, msgIndex = 0
  const msgInterval = setInterval(() => {
    if (msgIndex < loadingMessages.length - 1) { msgIndex++; loadingMessage.value = loadingMessages[msgIndex] }
  }, 800)
  const progressInterval = setInterval(() => {
    if (progress < 90) { progress += Math.random() * 10; loadingProgress.value = Math.min(progress, 90) }
  }, 100)
  setTimeout(() => {
    clearInterval(msgInterval); clearInterval(progressInterval)
    loadingProgress.value = 100; loadingMessage.value = 'Ready!'
    setTimeout(() => { isPageLoaded.value = true }, 500)
  }, 2500)
}

onMounted(() => { startLoading() })
</script>

<style scoped>
/* ==================== Key Verification ==================== */
.key-verify-container {
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
.key-verify-card {
  text-align: center;
  padding: 48px;
  border-radius: 32px;
  background: rgba(15, 23, 42, 0.8);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(59, 130, 246, 0.3);
  max-width: 480px;
  width: 90%;
}
.key-verify-icon { font-size: 64px; margin-bottom: 20px; }
.key-verify-card h2 { font-size: 28px; font-weight: 700; color: #fff; margin-bottom: 12px; }
.key-verify-card p { color: #94a3b8; font-size: 14px; margin-bottom: 32px; }
.key-input-wrapper { display: flex; gap: 12px; margin-bottom: 20px; }
.key-input { flex: 1; }
.key-input :deep(.el-input__wrapper) { background: rgba(255,255,255,0.1); border-color: rgba(59,130,246,0.3); box-shadow: none; }
.key-input :deep(.el-input__inner) { color: #fff; }
.key-error { color: #f56c6c; font-size: 13px; display: flex; align-items: center; justify-content: center; gap: 6px; }

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
.loading-content {
  text-align: center;
  padding: 40px;
  border-radius: 32px;
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(59, 130, 246, 0.3);
  animation: fadeInUp 0.6s ease-out;
}
.loading-spinner { position: relative; width: 80px; height: 80px; margin: 0 auto 24px; }
.spinner-ring { position: absolute; width: 100%; height: 100%; border-radius: 50%; border: 3px solid transparent; animation: spin 1.5s infinite; }
.spinner-ring:nth-child(1) { border-top-color: #3b82f6; }
.spinner-ring:nth-child(2) { border-right-color: #f59e0b; width: 70%; height: 70%; top: 15%; left: 15%; animation-delay: 0.2s; }
.spinner-ring:nth-child(3) { border-bottom-color: #10b981; width: 40%; height: 40%; top: 30%; left: 30%; animation-delay: 0.4s; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
.loading-text { margin-bottom: 24px; font-size: 28px; font-weight: 700; color: #e2e8f0; display: flex; justify-content: center; gap: 4px; }
.loading-dots { display: inline-flex; gap: 2px; }
.loading-dots span { animation: bounce 1.4s infinite; }
@keyframes bounce { 0%,80%,100% { transform: scale(0); opacity: 0.3; } 40% { transform: scale(1); opacity: 1; } }
.loading-progress { width: 280px; height: 4px; background: rgba(255,255,255,0.1); border-radius: 4px; margin: 0 auto 16px; overflow: hidden; }
.progress-bar { height: 100%; background: linear-gradient(90deg, #3b82f6, #8b5cf6, #ec489a); transition: width 0.3s; }
.loading-tip { font-size: 13px; color: #94a3b8; margin-bottom: 8px; }
.loading-subtip { font-size: 11px; color: #64748b; animation: pulse 2s infinite; }
@keyframes pulse { 0%,100% { opacity: 0.6; } 50% { opacity: 1; } }
@keyframes fadeInUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }

/* ==================== Main Content ==================== */
.introduction-page { background: #f5f7fa; min-height: 100vh; padding: 24px; }
.page-container { max-width: 1400px; margin: 0 auto; }

/* Hero Section */
.hero-section {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
  border-radius: 24px;
  padding: 48px 32px;
  margin-bottom: 24px;
  text-align: center;
}
.hero-badge { display: inline-block; padding: 4px 12px; background: rgba(59,130,246,0.2); border-radius: 20px; font-size: 12px; color: #60a5fa; margin-bottom: 16px; }
.hero-section h1 { font-size: 36px; font-weight: 700; color: #fff; margin-bottom: 12px; }
.hero-subtitle { font-size: 16px; color: #a0aec0; margin-bottom: 32px; }
.hero-stats { display: flex; justify-content: center; gap: 48px; flex-wrap: wrap; }
.hero-stat { text-align: center; }
.hero-stat .stat-number { display: block; font-size: 32px; font-weight: 700; color: #60a5fa; }
.hero-stat .stat-label { font-size: 12px; color: #94a3b8; }

/* Section Card */
.section-card { background: #fff; border-radius: 20px; padding: 24px; margin-bottom: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
.section-header { display: flex; align-items: flex-start; gap: 12px; margin-bottom: 20px; flex-wrap: wrap; }
.section-icon { font-size: 28px; }
.section-header h2 { font-size: 20px; font-weight: 600; color: #1e293b; margin: 0; }
.section-desc { font-size: 13px; color: #64748b; margin-top: 4px; max-width: 600px; }





/* Topology Containers */
.topology-container { height: 560px; width: 100%; background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); border-radius: 16px; overflow: hidden; margin-bottom: 16px; border: 1px solid #e2e8f0; }
.vue-flow-wrapper { width: 100%; height: 100%; }

/* Node Styles */
.arch-node { width: 160px; padding: 12px; background: #ffffff; border-radius: 12px; text-align: center; border-left: 4px solid; box-shadow: 0 2px 8px rgba(0,0,0,0.15); }
.arch-node-icon { font-size: 28px; margin-bottom: 6px; }
.arch-node-name { font-size: 14px; font-weight: 700; color: #1e293b; }
.arch-node-desc { font-size: 10px; color: #64748b; margin-top: 4px; }
.arch-node-tech { font-size: 9px; color: #94a3b8; margin-top: 4px; }

.blockchain-node { width: 130px; padding: 10px; background: #ffffff; border-radius: 12px; text-align: center; border: 2px solid #52c41a; box-shadow: 0 2px 8px rgba(0,0,0,0.15); }
.blockchain-node .node-icon { font-size: 24px; margin-bottom: 6px; }
.blockchain-node .node-name { font-size: 12px; font-weight: 700; color: #1e293b; }
.blockchain-node .node-ports { font-size: 9px; color: #64748b; margin: 4px 0; }
.node-status-badge { font-size: 9px; padding: 2px 6px; border-radius: 12px; display: inline-block; }
.node-status-badge.online { color: #52c41a; background: #f6ffed; }
.node-balance { font-size: 9px; color: #f59e0b; margin-top: 4px; }

.did-blockchain-node { width: 150px; padding: 12px; background: #ffffff; border-radius: 12px; text-align: center; border-left: 4px solid; box-shadow: 0 2px 8px rgba(0,0,0,0.15); }
.dataflow-node { width: 120px; padding: 12px; border-radius: 12px; text-align: center; color: white; box-shadow: 0 2px 8px rgba(0,0,0,0.15); }
.mining-node { width: 140px; padding: 12px; border-radius: 12px; text-align: center; color: white; box-shadow: 0 2px 8px rgba(0,0,0,0.15); }
.mining-node.idle { background: #64748b; }
.mining-node.trigger { background: #f59e0b; }
.mining-node.active { background: #10b981; animation: pulse 1.5s infinite; }
.mining-node.timer { background: #3b82f6; }
@keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.7; } }

.dependency-node { width: 140px; padding: 12px; background: #ffffff; border-radius: 12px; text-align: center; border-left: 4px solid; box-shadow: 0 2px 8px rgba(0,0,0,0.15); }
.dependency-node .node-files { font-size: 10px; color: #64748b; margin-top: 4px; }
.dependency-node .node-desc-small { font-size: 9px; color: #64748b; margin-top: 4px; }

.database-node { width: 160px; padding: 10px; background: #ffffff; border-radius: 8px; text-align: center; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
.db-icon { font-size: 20px; margin-bottom: 4px; }
.db-name { font-size: 11px; font-weight: 600; font-family: monospace; color: #3b82f6; }
.db-fields { font-size: 9px; color: #64748b; margin-top: 4px; }
.db-records { font-size: 9px; color: #10b981; margin-top: 2px; }

.api-node { width: 130px; padding: 12px; border-radius: 12px; text-align: center; color: white; box-shadow: 0 2px 8px rgba(0,0,0,0.15); }
.api-icon { font-size: 24px; margin-bottom: 6px; }
.api-name { font-size: 12px; font-weight: 600; }
.api-count { font-size: 10px; opacity: 0.8; margin-top: 4px; }

.driver-node { width: 140px; padding: 12px; background: #ffffff; border-radius: 12px; text-align: center; border-left: 4px solid; box-shadow: 0 2px 8px rgba(0,0,0,0.15); }
.driver-icon { font-size: 28px; margin-bottom: 6px; }
.driver-name { font-size: 13px; font-weight: 600; color: #1e293b; }
.driver-status { font-size: 9px; color: #52c41a; margin-top: 4px; }

.modeling-node { width: 130px; padding: 12px; border-radius: 12px; text-align: center; color: white; box-shadow: 0 2px 8px rgba(0,0,0,0.15); }
.node-icon { font-size: 24px; margin-bottom: 6px; }
.node-name { font-size: 12px; font-weight: 600; }
.node-desc { font-size: 10px; opacity: 0.9; margin-top: 4px; }
.node-tech { font-size: 9px; opacity: 0.7; margin-top: 4px; }

/* Detail Sections */
.blockchain-details, .dataflow-stats, .mining-stats, .table-stats { display: flex; flex-wrap: wrap; gap: 16px; margin-top: 16px; padding: 12px; background: #f8fafc; border-radius: 12px; }
.detail-item, .stat-item, .stat-card-mini, .table-stat { font-size: 12px; color: #475569; }
.detail-label, .stat-item span, .stat-card-mini span, .table-stat span { font-weight: 600; color: #1e293b; margin-right: 8px; }

.did-features { display: flex; flex-wrap: wrap; gap: 16px; margin-top: 16px; }
.did-feature-item { display: flex; align-items: center; gap: 8px; padding: 8px 12px; background: #f8fafc; border-radius: 8px; font-size: 12px; }
.did-feature-icon { font-size: 18px; }
.did-feature-item code { background: #e2e8f0; padding: 2px 6px; border-radius: 4px; font-size: 11px; }

.field-mapping-table, .prediction-table { margin-top: 16px; }
.table-title { font-size: 13px; font-weight: 600; color: #1e293b; margin-bottom: 12px; }
:deep(.el-table) { font-size: 12px; }
:deep(.el-table th) { background: #f8fafc; }

/* Core Concepts */
.concepts-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
.concept-card { background: #f8fafc; border-radius: 16px; padding: 16px; display: flex; gap: 14px; cursor: pointer; transition: all 0.3s; border: 1px solid #e2e8f0; }
.concept-card:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(0,0,0,0.1); border-color: #3b82f6; }
.concept-icon { width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 24px; color: white; }
.concept-info h3 { font-size: 14px; font-weight: 600; color: #1e293b; margin: 0 0 4px; }
.concept-info p { font-size: 11px; color: #64748b; margin: 0 0 6px; }
.concept-link { font-size: 11px; color: #3b82f6; font-weight: 500; }

/* FAQ */
.faq-title { font-weight: 500; color: #1e293b; }
.faq-answer { color: #475569; font-size: 13px; line-height: 1.5; padding: 8px 0; }

/* Feedback Card */
.feedback-card { background: linear-gradient(135deg, #3b82f6, #8b5cf6); border-radius: 20px; padding: 28px; display: flex; align-items: center; gap: 24px; flex-wrap: wrap; }
.feedback-icon { font-size: 48px; }
.feedback-content h3 { font-size: 20px; font-weight: 600; color: white; margin: 0 0 6px; }
.feedback-content p { color: rgba(255,255,255,0.8); font-size: 13px; margin-bottom: 14px; }
.feedback-content .el-button { background: white; color: #3b82f6; border: none; }

/* VueFlow Overrides */
:deep(.vue-flow__edge-path) { stroke-dasharray: 5; }
:deep(.vue-flow__edge-label) { font-size: 10px; fill: #fff; background: #1890ff; padding: 2px 8px; border-radius: 12px; }

/* Responsive */
@media (max-width: 1024px) {
  .concepts-grid { grid-template-columns: repeat(2, 1fr); }
  .topology-container { height: 500px; }
}
@media (max-width: 768px) {
  .introduction-page { padding: 16px; }
  .hero-section { padding: 32px 20px; }
  .hero-section h1 { font-size: 24px; }
  .hero-stats { gap: 24px; }
  .concepts-grid { grid-template-columns: 1fr; }
  .topology-container { height: 400px; }
  .section-header { flex-direction: column; }
}
</style>