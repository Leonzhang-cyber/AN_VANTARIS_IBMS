<template>
  <!-- Key Auth Screen -->
  <div v-if="!isAuthenticated" class="auth-container">
    <div class="auth-overlay">
      <div class="auth-content">
        <div class="auth-icon">🔐</div>
        <h2 class="auth-title">Access Required</h2>
        <p class="auth-desc">Please enter the access key to view IBMS Web3 documentation</p>
        <div class="auth-input-group">
          <input
              type="password"
              v-model="accessKey"
              placeholder="Enter access key"
              class="auth-input"
              @keyup.enter="verifyKey"
              autofocus
          />
          <button class="auth-btn" @click="verifyKey" :disabled="!accessKey">
            Verify Access
          </button>
        </div>
        <p v-if="authError" class="auth-error">❌ Invalid access key. Please try again.</p>
<!--        <div class="auth-loading" v-if="isLoadingImages">-->
<!--          <span class="loading-dot"></span>-->
<!--          <span class="loading-dot"></span>-->
<!--          <span class="loading-dot"></span>-->
<!--          <span class="loading-text">Loading Web3 modules in background...</span>-->
<!--        </div>-->
      </div>
    </div>
  </div>

  <!-- Loading Screen (after auth, waiting for images) -->
  <div v-else-if="!isLoaded" class="loading-container">
    <div class="loading-overlay">
      <div class="loading-content">
        <div class="loading-spinner">
          <div class="spinner-ring"></div>
          <div class="spinner-ring"></div>
          <div class="spinner-ring"></div>
        </div>
        <div class="loading-text">Web3 infrastructure</div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="web3-intro-page">
    <!-- Hero Section -->
    <section class="hero">
      <div class="hero-bg"></div>
      <div class="hero-container">
        <div class="hero-badge">
          <span class="badge-dot"></span>
          Enterprise Ready · Production Deployed
        </div>
        <h1 class="hero-title">
          Bridging IoT & Blockchain<br />
          <span class="gradient-text">with Enterprise-Grade Web3</span>
        </h1>
        <p class="hero-description">
          IBMS delivers a complete Web3 infrastructure for smart building management —
          combining decentralized identity, on-chain data anchoring, and seamless IoT integration.
          Built for enterprises requiring trust, transparency, and auditability.
        </p>
        <div class="hero-stats">
          <div class="stat">
            <span class="stat-number">500+</span>
            <span class="stat-label">Devices Supported</span>
          </div>
          <div class="stat">
            <span class="stat-number">3</span>
            <span class="stat-label">Geth Nodes</span>
          </div>
          <div class="stat">
            <span class="stat-number">5s</span>
            <span class="stat-label">Block Time</span>
          </div>
          <div class="stat">
            <span class="stat-number">24/7</span>
            <span class="stat-label">Real-time Sync</span>
          </div>
        </div>
      </div>
    </section>

    <!-- Architecture Section -->
    <section id="architecture" class="section architecture-section">
      <div class="container">
        <div class="section-header">
          <span class="section-tag">System Design</span>
          <h2 class="section-title">How IBMS Integrates Web3</h2>
          <p class="section-desc">
            Our architecture follows an "Off-Chain First" principle — keeping high-frequency
            business logic off-chain while anchoring cryptographic proofs on blockchain for
            maximum performance and trust.
          </p>
        </div>

        <div class="architecture-grid">
          <div class="arch-card" v-for="layer in layers" :key="layer.name">
            <div class="arch-card-icon" :style="{ background: layer.color }">
              <el-icon><component :is="layer.icon" /></el-icon>
            </div>
            <h3>{{ layer.name }}</h3>
            <p>{{ layer.description }}</p>
            <div class="arch-card-techs">
              <span v-for="tech in layer.techs" :key="tech">{{ tech }}</span>
            </div>
          </div>
        </div>

        <div class="architecture-image-wrapper">
          <div class="image-label">
            <span class="label-icon">📐</span>
            <span>System Architecture Diagram</span>
          </div>
          <img
              :src="images.architecture"
              alt="IBMS Web3 Architecture"
              class="architecture-image"
              @load="handleImageLoad"
              @error="handleImageError"
          />
        </div>

        <div class="architecture-explanation">
          <div class="exp-item">
            <div class="exp-icon">🎯</div>
            <div class="exp-content">
              <h4>Application Layer</h4>
              <p>DID Service handles decentralized identity management, VC issuance and verification. IoT Service manages device connectivity, protocol adaptation and data ingestion. Modeling Service provides AI-powered energy prediction and analytics.</p>
            </div>
          </div>
          <div class="exp-item">
            <div class="exp-icon">🔌</div>
            <div class="exp-content">
              <h4>Web3 Integration Layer</h4>
              <p>The Blockchain Unified Entry provides a single interface for all chain interactions. ContractManager routes smart contract calls with ABI management. MiningScheduler intelligently starts/stops mining nodes based on transaction demand.</p>
            </div>
          </div>
          <div class="exp-item">
            <div class="exp-icon">⛓️</div>
            <div class="exp-content">
              <h4>Blockchain Layer</h4>
              <p>Three Geth nodes running Clique PoA consensus, each with independent RPC endpoints. Nodes automatically rotate block production every 5 seconds, ensuring high availability and fault tolerance.</p>
            </div>
          </div>
          <div class="exp-item">
            <div class="exp-icon">📜</div>
            <div class="exp-content">
              <h4>Smart Contract Layer</h4>
              <p>IMBSAnchor contract provides immutable on-chain storage for entity metadata hashes and VC credentials. All anchoring operations emit events for complete audit trails.</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Registration Flow Section -->
    <section id="registration" class="section registration-section">
      <div class="container">
        <div class="section-header">
          <span class="section-tag">Identity Management</span>
          <h2 class="section-title">DID-Based Entity Registration</h2>
          <p class="section-desc">
            Every device and user in IBMS receives a unique Decentralized Identifier (DID)
            and Verifiable Credential (VC), anchored on blockchain for tamper-proof identity verification.
          </p>
        </div>

        <div class="flow-visual">
          <div class="flow-steps-horizontal">
            <div class="flow-step" v-for="(step, idx) in registrationSteps" :key="idx">
              <div class="step-circle">{{ idx + 1 }}</div>
              <div class="step-connector" v-if="idx < registrationSteps.length"></div>
            </div>
          </div>

          <div class="flow-details">
            <div class="flow-detail-card" v-for="(step, idx) in registrationSteps" :key="idx">
              <div class="detail-content">
                <h4 style="font-size: 16px">{{ step.title }}</h4>
                <p style="font-size: 13px">{{ step.description }}</p>
              </div>
            </div>
          </div>
        </div>

        <div class="flow-image-wrapper">
          <div class="image-label">
            <span class="label-icon">🔄</span>
            <span>Entity Registration Sequence Diagram</span>
          </div>
          <img
              :src="images.registration"
              alt="Entity Registration Flow"
              class="flow-image"
              @load="handleImageLoad"
              @error="handleImageError"
          />
        </div>

        <div class="registration-benefits">
          <div class="benefit" v-for="benefit in registrationBenefits" :key="benefit.title">
            <div class="benefit-icon">{{ benefit.icon }}</div>
            <h4>{{ benefit.title }}</h4>
            <p>{{ benefit.description }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Data Provenance Section -->
    <section id="provenance" class="section provenance-section">
      <div class="container">
        <div class="section-header">
          <span class="section-tag">Data Integrity</span>
          <h2 class="section-title">Critical Data Provenance</h2>
          <p class="section-desc">
            Not all data needs blockchain. IBMS intelligently identifies critical data points
            and anchors only their cryptographic hashes on-chain, balancing performance with auditability.
          </p>
        </div>

        <div class="provenance-pipeline">
          <div class="pipeline-stage" v-for="(stage, idx) in provenanceStages" :key="idx">
            <div class="stage-icon" :class="stage.type">
              <el-icon><component :is="stage.icon" /></el-icon>
            </div>
            <div class="stage-content">
              <h4 style="font-size: 16px">{{ stage.title }}</h4>
              <p style="font-size: 13px">{{ stage.description }}</p>
            </div>
            <div class="stage-arrow" v-if="idx < provenanceStages.length - 1">
              <el-icon><ArrowRight /></el-icon>
            </div>
          </div>
        </div>

        <div class="flow-image-wrapper">
          <div class="image-label">
            <span class="label-icon">📊</span>
            <span>Data Provenance Flow Diagram</span>
          </div>
          <img
              :src="images.dataProvenance"
              alt="Data Provenance Flow"
              class="flow-image"
              @load="handleImageLoad"
              @error="handleImageError"
          />
        </div>

        <div class="provenance-features">
          <div class="p-feature">
            <div class="p-feature-icon">⚡</div>
            <div class="p-feature-text">
              <strong>High Performance</strong>
              <span>99% of IoT data stored off-chain in CSV for fast querying</span>
            </div>
          </div>
          <div class="p-feature">
            <div class="p-feature-icon">🔒</div>
            <div class="p-feature-text">
              <strong>Selective Anchoring</strong>
              <span>Only critical data (alarms, thresholds) hash stored on blockchain</span>
            </div>
          </div>
          <div class="p-feature">
            <div class="p-feature-icon">📡</div>
            <div class="p-feature-text">
              <strong>Real-time Push</strong>
              <span>SSE streams deliver data to frontend with millisecond latency</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Tech Stack Section -->
    <section id="tech" class="section tech-section">
      <div class="container">
        <div class="section-header">
          <span class="section-tag">Technology</span>
          <h2 class="section-title">Enterprise Web3 Stack</h2>
          <p class="section-desc">
            Built on battle-tested technologies, our stack delivers production-grade reliability
            while maintaining flexibility for future expansions.
          </p>
        </div>

        <div class="tech-showcase">
          <div class="tech-showcase-item" v-for="tech in techStack" :key="tech.name">
            <div class="tech-showcase-icon" :style="{ background: tech.color }">
              <el-icon><component :is="tech.icon" /></el-icon>
            </div>
            <div class="tech-showcase-info">
              <h3>{{ tech.name }}</h3>
              <p>{{ tech.description }}</p>
              <span class="tech-version">{{ tech.version }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section id="features" class="section features-section">
      <div class="container">
        <div class="section-header">
          <span class="section-tag">Innovation</span>
          <h2 class="section-title">Why IBMS Web3 Stands Out</h2>
          <p class="section-desc">
            Six key innovations that make our Web3 integration uniquely suited for enterprise IoT.
          </p>
        </div>

        <div class="features-grid">
          <div class="feature-card" v-for="feature in features" :key="feature.title">
            <div class="feature-icon" :style="{ color: feature.color, background: feature.color + '08' }">
              <el-icon><component :is="feature.icon" /></el-icon>
            </div>
            <h3>{{ feature.title }}</h3>
            <p>{{ feature.description }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="cta-section">
      <div class="container">
        <div class="cta-content">
          <h2>Ready to Build Trust into Your IoT Infrastructure?</h2>
          <p>Schedule a demo to see how IBMS Web3 can transform your building management system.</p>
          <div class="cta-buttons">
            <button class="btn-primary-large">Request Demo</button>
            <button class="btn-secondary">Contact Sales</button>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import {
  Share, Document, DataLine, Cpu, Star,
  ArrowRight, Connection, Key, Lock, DataAnalysis,
  Monitor, Guide, Timer, Coin, User, Link
} from '@element-plus/icons-vue'

// ============ Access Key ============
const CORRECT_KEY = 'allen717'
const accessKey = ref('')
const isAuthenticated = ref(false)
const authError = ref(false)
const isLoadingImages = ref(false)

// ============ Image URLs ============
const IMAGE_URLS = {
  architecture: 'https://aegisnx.com/wp-content/uploads/2026/05/1779094789817.png',
  registration: 'https://aegisnx.com/wp-content/uploads/2026/05/1779094455062.png',
  dataProvenance: 'https://aegisnx.com/wp-content/uploads/2026/05/1779094802455.png'
}

const FALLBACK_IMAGES = {
  architecture: 'https://picsum.photos/id/104/1200/600?random=1',
  registration: 'https://picsum.photos/id/26/1200/600?random=2',
  dataProvenance: 'https://picsum.photos/id/30/1200/600?random=3'
}

// ============ Loading State ============
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Initializing Web3 modules...')
const imagesLoadedCount = ref(0)
const imageErrors = ref(0)
const totalImages = 3

const images = ref({
  architecture: IMAGE_URLS.architecture,
  registration: IMAGE_URLS.registration,
  dataProvenance: IMAGE_URLS.dataProvenance
})

const processedImages = ref({
  architecture: false,
  registration: false,
  dataProvenance: false
})

const loadingMessages = [
  'Connecting to blockchain network...',
  'Loading smart contracts...',
  'Initializing Web3 modules...',
  'Almost ready...'
]

let loadingTimeout: ReturnType<typeof setTimeout> | null = null
let progressInterval: ReturnType<typeof setInterval> | null = null

// ============ Key Verification ============
const verifyKey = () => {
  if (accessKey.value === CORRECT_KEY) {
    authError.value = false
    isAuthenticated.value = true

    // If images are not fully loaded yet, continue waiting
    if (imagesLoadedCount.value < totalImages) {
      isLoadingImages.value = true
    }
  } else {
    authError.value = true
    accessKey.value = ''
  }
}

// ============ Image Load Handlers ============
const updateLoadingProgress = () => {
  loadingProgress.value = (imagesLoadedCount.value / totalImages) * 100
  const idx = Math.min(Math.floor(imagesLoadedCount.value / totalImages * loadingMessages.length), loadingMessages.length - 1)
  loadingMessage.value = loadingMessages[idx]

  if (imagesLoadedCount.value === totalImages) {
    if (loadingTimeout) clearTimeout(loadingTimeout)
    if (progressInterval) clearInterval(progressInterval)
    // If authenticated, show main content after images load
    if (isAuthenticated.value) {
      setTimeout(() => { isLoaded.value = true }, 300)
    }
  }
}

const handleImageLoad = () => {
  imagesLoadedCount.value++
  updateLoadingProgress()
}

const handleImageError = () => {
  imageErrors.value++
  imagesLoadedCount.value++
  updateLoadingProgress()
}

const startProgressSimulation = () => {
  let progress = 0
  progressInterval = setInterval(() => {
    if (progress < 85 && imagesLoadedCount.value < totalImages) {
      progress += Math.random() * 8 + 2
      if (progress > 85) progress = 85
      loadingProgress.value = progress
    }
  }, 200)
}

const startLoadingTimeout = () => {
  loadingTimeout = setTimeout(() => {
    if (imagesLoadedCount.value < totalImages) {
      while (imagesLoadedCount.value < totalImages) imagesLoadedCount.value++
      updateLoadingProgress()
    }
  }, 15000)
}

const preloadImages = () => {
  Object.values(images.value).forEach((url) => {
    const img = new window.Image()
    img.src = url
  })
}

// ============ Initialize - Start loading images in background ============
onMounted(() => {
  // Start loading images immediately regardless of auth
  isLoadingImages.value = true
  startProgressSimulation()
  startLoadingTimeout()
  preloadImages()
})

onUnmounted(() => {
  if (loadingTimeout) clearTimeout(loadingTimeout)
  if (progressInterval) clearInterval(progressInterval)
})

// ============ Data ============
const layers = [
  { name: 'Application Layer', description: 'Business logic for DID, IoT and AI modeling', icon: 'Monitor', color: '#10b981', techs: ['DID Service', 'IoT Service', 'Modeling'] },
  { name: 'Web3 Integration', description: 'Unified blockchain interface and contract routing', icon: 'Connection', color: '#3b82f6', techs: ['Blockchain Entry', 'ContractManager', 'MiningScheduler'] },
  { name: 'Blockchain Layer', description: 'Three-node Geth cluster with PoA consensus', icon: 'Link', color: '#f59e0b', techs: ['Node-1', 'Node-2', 'Node-3'] },
  { name: 'Smart Contract', description: 'IMBSAnchor for immutable data anchoring', icon: 'Document', color: '#ef4444', techs: ['anchorEntity', 'anchorVC', 'Events'] }
]

const registrationSteps = [
  { title: 'Submit Request', description: 'Administrator submits device information via REST API' },
  { title: 'Generate Identity', description: 'DID module creates unique DID, keypair and VC' },
  { title: 'Start Mining', description: 'MiningScheduler activates Geth nodes if idle' },
  { title: 'Anchor on Chain', description: 'IMBSAnchor contract stores metadata hash' },
  { title: 'Store Proof', description: 'Transaction hash saved to MySQL for audit trail' }
]

const registrationBenefits = [
  { icon: '🆔', title: 'Universal Identity', description: 'Every entity gets a W3C-compliant DID that works across systems' },
  { icon: '📜', title: 'Verifiable Credentials', description: 'VCs provide tamper-proof proof of identity and permissions' },
  { icon: '⛓️', title: 'Immutable Record', description: 'All identity operations are permanently anchored on blockchain' },
  { icon: '🔐', title: 'Self-Sovereign', description: 'Private keys controlled by entity owner, not central authority' }
]

const provenanceStages = [
  { title: 'Data Ingestion', description: 'MQTT/HTTP data reception from IoT devices', icon: 'Download', type: 'ingest' },
  { title: 'Standardization', description: 'Field mapping and data transformation', icon: 'Refresh', type: 'process' },
  { title: 'Critical Check', description: 'Determine if data requires on-chain anchoring', icon: 'Warning', type: 'decision' },
  { title: 'Hash & Anchor', description: 'SHA256 hash stored on IMBSAnchor contract', icon: 'Lock', type: 'blockchain' },
  { title: 'Off-Chain Storage', description: 'Full time-series data saved to CSV', icon: 'Document', type: 'storage' },
  { title: 'Real-time Push', description: 'SSE streams data to frontend dashboards', icon: 'Share', type: 'output' }
]

const techStack = [
  { name: 'Geth', description: 'Go Ethereum client running private PoA network with three signer nodes', icon: 'Coin', version: 'v1.13.15', color: '#62688f' },
  { name: 'Web3.py', description: 'Python library for blockchain interaction, transaction signing and event monitoring', icon: 'Connection', version: '7.15.0', color: '#3b82f6' },
  { name: 'Clique PoA', description: 'Proof-of-Authority consensus with 5-second block time and no energy waste', icon: 'User', version: 'Clique', color: '#f59e0b' },
  { name: 'IMBSAnchor', description: 'Custom Solidity contract for entity and VC hash anchoring', icon: 'Document', version: 'Solidity 0.8', color: '#ef4444' },
  { name: 'MiningScheduler', description: 'Intelligent on-demand mining with 10-minute idle timeout', icon: 'Timer', version: 'Custom', color: '#8b5cf6' },
  { name: 'DID Module', description: 'W3C DID standard implementation with VC/VP support', icon: 'Key', version: 'DID Core', color: '#06b6d4' }
]

const features = [
  { title: 'Off-Chain First', description: 'High-frequency business logic stays off-chain for performance. Only cryptographic proofs are anchored on blockchain, reducing costs and latency.', icon: 'DataAnalysis', color: '#10b981' },
  { title: 'On-Demand Mining', description: 'Mining nodes activate only when transactions exist and automatically stop after 10 minutes idle, saving server resources.', icon: 'Timer', color: '#f59e0b' },
  { title: 'DID + VC Integration', description: 'Every device, user, and organization receives a unique DID and Verifiable Credential for trust establishment.', icon: 'Key', color: '#3b82f6' },
  { title: 'Critical Data Anchoring', description: 'Selective on-chain storage for alarms, threshold breaches, and compliance-critical data enables audit trails.', icon: 'Lock', color: '#ef4444' },
  { title: 'Hybrid Storage Architecture', description: 'MySQL for metadata, CSV for time-series data, Blockchain for immutable proofs — each optimized for its purpose.', icon: 'Coin', color: '#8b5cf6' },
  { title: 'Complete Audit Trail', description: 'All on-chain events are queryable via smart contract logs, providing full transaction history.', icon: 'Guide', color: '#06b6d4' }
]
</script>

<style scoped>
/* ==================== Auth Screen Styles ==================== */
.auth-container {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, #0a0b0f 0%, #1a1d2e 100%);
  z-index: 10000;
  display: flex;
  justify-content: center;
  align-items: center;
}

.auth-overlay {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  backdrop-filter: blur(2px);
}

.auth-content {
  text-align: center;
  padding: 48px;
  border-radius: 32px;
  background: rgba(15, 23, 42, 0.8);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(59, 130, 246, 0.3);
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
  animation: fadeInUp 0.6s ease-out;
  min-width: 380px;
}

.auth-icon {
  font-size: 56px;
  margin-bottom: 20px;
}

.auth-title {
  font-size: 28px;
  font-weight: 700;
  color: #e2e8f0;
  margin-bottom: 12px;
}

.auth-desc {
  font-size: 14px;
  color: #94a3b8;
  margin-bottom: 32px;
}

.auth-input-group {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.auth-input {
  flex: 1;
  padding: 14px 18px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  color: #e2e8f0;
  font-size: 14px;
  outline: none;
  transition: all 0.2s;
}

.auth-input:focus {
  border-color: #3b82f6;
  background: rgba(59, 130, 246, 0.05);
}

.auth-input::placeholder {
  color: #64748b;
}

.auth-btn {
  padding: 14px 28px;
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  border: none;
  border-radius: 12px;
  color: white;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s;
}

.auth-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.auth-btn:hover:not(:disabled) {
  opacity: 0.85;
}

.auth-error {
  color: #ef4444;
  font-size: 13px;
  margin-top: 12px;
}

.auth-loading {
  margin-top: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding-top: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.loading-dot {
  width: 6px;
  height: 6px;
  background: #3b82f6;
  border-radius: 50%;
  animation: dotPulse 1.4s infinite ease-in-out;
}

.loading-dot:nth-child(1) { animation-delay: 0s; }
.loading-dot:nth-child(2) { animation-delay: 0.2s; }
.loading-dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes dotPulse {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
  40% { transform: scale(1); opacity: 1; }
}

.loading-text {
  font-size: 12px;
  color: #64748b;
  margin-left: 8px;
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}

/* ==================== Your Original Styles Below ==================== */
/* ==================== Reset & Base ==================== */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html {
  scroll-behavior: smooth;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
}

.web3-intro-page {
  min-height: 100vh;
  background: #0a0b0f;
  color: #e5e7eb;
}

.container {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 40px;
}

/* ==================== Loading ==================== */
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

/* ==================== Navigation ==================== */
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  background: rgba(10, 11, 15, 0.95);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(255,255,255,0.05);
  z-index: 100;
  padding: 16px 0;
}

.nav-container {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 40px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.nav-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 20px;
  font-weight: 700;
}

.logo-icon {
  font-size: 24px;
}

.logo-text {
  background: linear-gradient(135deg, #e5e7eb, #9ca3af);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.logo-web3 {
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.nav-links {
  display: flex;
  gap: 32px;
}

.nav-links a {
  color: #9ca3af;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  transition: color 0.2s;
}

.nav-links a:hover {
  color: #e5e7eb;
}

.btn-primary {
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  border: none;
  color: white;
  padding: 8px 20px;
  border-radius: 30px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: opacity 0.2s;
}

.btn-primary:hover {
  opacity: 0.85;
}

/* ==================== Hero ==================== */
.hero {
  min-height: 100vh;
  display: flex;
  align-items: center;
  position: relative;
  overflow: hidden;
}

.hero-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(ellipse at 30% 40%, rgba(59,130,246,0.12), transparent 60%),
  radial-gradient(ellipse at 70% 60%, rgba(139,92,246,0.08), transparent 60%);
  pointer-events: none;
}

.hero-container {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 40px;
  position: relative;
  z-index: 1;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: rgba(59,130,246,0.12);
  border: 1px solid rgba(59,130,246,0.2);
  border-radius: 40px;
  padding: 6px 16px;
  font-size: 13px;
  margin-bottom: 32px;
}

.badge-dot {
  width: 6px;
  height: 6px;
  background: #3b82f6;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

.hero-title {
  font-size: 56px;
  font-weight: 700;
  line-height: 1.2;
  margin-bottom: 24px;
}

.gradient-text {
  background: linear-gradient(135deg, #3b82f6, #8b5cf6, #ec489a);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.hero-description {
  font-size: 18px;
  color: #9ca3af;
  line-height: 1.6;
  max-width: 600px;
  margin-bottom: 48px;
}

.hero-stats {
  display: flex;
  gap: 48px;
  flex-wrap: wrap;
}

.stat {
  display: flex;
  flex-direction: column;
}

.stat-number {
  font-size: 32px;
  font-weight: 700;
  background: linear-gradient(135deg, #e5e7eb, #9ca3af);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.stat-label {
  font-size: 13px;
  color: #ffffff;
  margin-top: 4px;
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(1.2); }
}

/* ==================== Sections ==================== */
.section {
  padding: 20px 0;
  border-top: 1px solid rgba(255,255,255,0.05);
}

.section-header {
  text-align: center;
  max-width: 700px;
  margin: 0 auto 60px;
}

.section-tag {
  display: inline-block;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 2px;
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  margin-bottom: 16px;
}

.section-title {
  font-size: 40px;
  font-weight: 700;
  margin-bottom: 20px;
}

.section-desc {
  font-size: 16px;
  color: #9ca3af;
  line-height: 1.6;
}

/* Architecture Grid */
.architecture-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 60px;
}

.arch-card {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.05);
  border-radius: 20px;
  padding: 24px;
  transition: all 0.3s;
}

.arch-card:hover {
  border-color: rgba(59,130,246,0.3);
  transform: translateY(-4px);
}

.arch-card-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
}

.arch-card-icon .el-icon {
  font-size: 24px;
  color: white;
}

.arch-card h3 {
  font-size: 18px;
  margin-bottom: 10px;
}

.arch-card p {
  font-size: 13px;
  color: #9ca3af;
  line-height: 1.5;
  margin-bottom: 16px;
}

.arch-card-techs {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.arch-card-techs span {
  font-size: 11px;
  padding: 3px 10px;
  background: rgba(255,255,255,0.05);
  border-radius: 20px;
  color: #ffffff;
}

/* Image Wrapper */
.architecture-image-wrapper,
.flow-image-wrapper {
  margin: 60px 0;
}

.image-label {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 20px;
  font-size: 13px;
  color: #9ca3af;
}

.label-icon {
  font-size: 16px;
}

.architecture-image,
.flow-image {
  width: 100%;
  height: auto;
  border-radius: 20px;
  border: 1px solid rgba(255,255,255,0.08);
  background: #0d0e12;
}

/* Architecture Explanation */
.architecture-explanation {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
  margin-top: 40px;
}

.exp-item {
  display: flex;
  gap: 16px;
  padding: 20px;
  background: rgba(255,255,255,0.02);
  border-radius: 16px;
}

.exp-icon {
  font-size: 28px;
}

.exp-content h4 {
  font-size: 16px;
  margin-bottom: 8px;
}

.exp-content p {
  font-size: 13px;
  color: #9ca3af;
  line-height: 1.5;
}

/* Flow Steps */
.flow-visual {
  margin-bottom: 60px;
}

.flow-steps-horizontal {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  padding-left: 100px;
  padding-right: 100px;
  position: relative;
}

.step-circle {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  position: relative;
  z-index: 2;
}

.step-connector {
  flex: 1;
  height: 2px;
  background: linear-gradient(90deg, #3b82f6, #8b5cf6);
  margin-top: 19px;
}

.flow-details {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 16px;
}

.flow-detail-card {
  text-align: center;
  padding: 20px;
  background: rgba(255,255,255,0.02);
  border-radius: 16px;
}

.detail-number {
  width: 28px;
  height: 28px;
  background: rgba(59,130,246,0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  margin: 0 auto 12px;
}

.flow-detail-card h4 {
  font-size: 14px;
  margin-bottom: 8px;
}

.flow-detail-card p {
  font-size: 11px;
  color: #9ca3af;
  line-height: 1.4;
}

/* Registration Benefits */
.registration-benefits {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
  margin-top: 40px;
}

.benefit {
  text-align: center;
  padding: 24px;
  background: rgba(255,255,255,0.02);
  border-radius: 20px;
}

.benefit-icon {
  font-size: 36px;
  margin-bottom: 16px;
}

.benefit h4 {
  font-size: 16px;
  margin-bottom: 8px;
}

.benefit p {
  font-size: 13px;
  color: #9ca3af;
  line-height: 1.5;
}

/* Provenance Pipeline */
.provenance-pipeline {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 60px;
}

.pipeline-stage {
  flex: 1;
  min-width: 150px;
  text-align: center;
  position: relative;
}

.stage-icon {
  width: 56px;
  height: 56px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
}

.stage-icon .el-icon {
  font-size: 26px;
  color: white;
}

.stage-icon.ingest { background: linear-gradient(135deg, #3b82f6, #2563eb); }
.stage-icon.process { background: linear-gradient(135deg, #f59e0b, #d97706); }
.stage-icon.decision { background: linear-gradient(135deg, #ef4444, #dc2626); }
.stage-icon.blockchain { background: linear-gradient(135deg, #8b5cf6, #7c3aed); }
.stage-icon.storage { background: linear-gradient(135deg, #10b981, #059669); }
.stage-icon.output { background: linear-gradient(135deg, #06b6d4, #0891b2); }

.pipeline-stage h4 {
  font-size: 14px;
  margin-bottom: 6px;
}

.pipeline-stage p {
  font-size: 11px;
  color: #9ca3af;
}

.stage-arrow {
  position: absolute;
  right: -20px;
  top: 20px;
  color: #2a2a35;
}

/* Provenance Features */
.provenance-features {
  display: flex;
  justify-content: center;
  gap: 48px;
  margin-top: 48px;
  flex-wrap: wrap;
}

.p-feature {
  display: flex;
  align-items: center;
  gap: 12px;
}

.p-feature-icon {
  font-size: 34px;
  margin-bottom: 10px;
}

.p-feature-text {
  display: flex;
  flex-direction: column;
}

.p-feature-text strong {
  font-size: 16px;
  margin-bottom: 4px;
}

.p-feature-text span {
  font-size: 14px;
  color: #9ca3af;
}

/* Tech Showcase */
.tech-showcase {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.tech-showcase-item {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 20px;
  background: rgba(255,255,255,0.02);
  border-radius: 16px;
  transition: all 0.3s;
}

.tech-showcase-item:hover {
  background: rgba(255,255,255,0.04);
}

.tech-showcase-icon {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.tech-showcase-icon .el-icon {
  font-size: 28px;
  color: white;
}

.tech-showcase-info {
  flex: 1;
}

.tech-showcase-info h3 {
  font-size: 18px;
  margin-bottom: 6px;
}

.tech-showcase-info p {
  font-size: 14px;
  color: #9ca3af;
  line-height: 1.5;
}

.tech-version {
  display: inline-block;
  margin-top: 8px;
  font-size: 13px;
  font-family: monospace;
  color: #60a5fa;
  background: rgba(59,130,246,0.15);
  padding: 3px 10px;
  border-radius: 20px;
}

/* Features Grid */
.features-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}

.feature-card {
  padding: 28px;
  background: rgba(255,255,255,0.02);
  border: 1px solid rgba(255,255,255,0.05);
  border-radius: 20px;
  transition: all 0.3s;
}

.feature-card:hover {
  border-color: rgba(59,130,246,0.3);
  transform: translateY(-4px);
}

.feature-icon {
  width: 52px;
  height: 52px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
  font-size: 26px;
}

.feature-card h3 {
  font-size: 18px;
  margin-bottom: 12px;
}

.feature-card p {
  font-size: 14px;
  color: #9ca3af;
  line-height: 1.6;
}

/* CTA Section */
.cta-section {
  background: linear-gradient(135deg, rgba(59,130,246,0.08), rgba(139,92,246,0.08));
  border-top: 1px solid rgba(255,255,255,0.05);
  border-bottom: 1px solid rgba(255,255,255,0.05);
  padding: 80px 0;
  text-align: center;
  margin-top: 30px;
}

.cta-content h2 {
  font-size: 32px;
  margin-bottom: 16px;
}

.cta-content p {
  font-size: 16px;
  color: #9ca3af;
  margin-bottom: 32px;
}

.cta-buttons {
  display: flex;
  gap: 16px;
  justify-content: center;
}

.btn-primary-large {
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  border: none;
  color: white;
  padding: 12px 32px;
  border-radius: 40px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: opacity 0.2s;
}

.btn-secondary {
  background: transparent;
  border: 1px solid rgba(255,255,255,0.2);
  color: #e5e7eb;
  padding: 12px 32px;
  border-radius: 40px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary:hover {
  border-color: #3b82f6;
  color: #3b82f6;
}

/* Footer */
.footer {
  padding: 60px 0 30px;
  background: #0a0b0f;
}

.footer-content {
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 40px;
  margin-bottom: 40px;
}

.footer-logo span {
  font-size: 20px;
  font-weight: 700;
}

.footer-web3 {
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.footer-logo p {
  font-size: 12px;
  color: #9ca3af;
  margin-top: 8px;
}

.footer-links {
  display: flex;
  gap: 60px;
  flex-wrap: wrap;
}

.footer-col h4 {
  font-size: 14px;
  margin-bottom: 16px;
}

.footer-col a {
  display: block;
  font-size: 13px;
  color: #9ca3af;
  color: #9ca3af;
  text-decoration: none;
  margin-bottom: 10px;
  transition: color 0.2s;
}

.footer-col a:hover {
  color: #e5e7eb;
}

.footer-bottom {
  text-align: center;
  padding-top: 30px;
  border-top: 1px solid rgba(255,255,255,0.05);
}

.footer-bottom p {
  font-size: 12px;
  color: #9ca3af;
}

/* Responsive */
@media (max-width: 1024px) {
  .architecture-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .flow-details {
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  }

  .registration-benefits {
    grid-template-columns: repeat(2, 1fr);
  }

  .features-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .hero-title {
    font-size: 42px;
  }

  .section-title {
    font-size: 32px;
  }
}

@media (max-width: 768px) {
  .nav-links {
    display: none;
  }

  .container {
    padding: 0 24px;
  }

  .architecture-grid {
    grid-template-columns: 1fr;
  }

  .architecture-explanation {
    grid-template-columns: 1fr;
  }

  .registration-benefits {
    grid-template-columns: 1fr;
  }

  .features-grid {
    grid-template-columns: 1fr;
  }

  .provenance-pipeline {
    flex-direction: column;
  }

  .stage-arrow {
    display: none;
  }

  .hero-title {
    font-size: 32px;
  }

  .hero-stats {
    gap: 24px;
  }

  .hero-stat {
    font-size: 24px;
  }

  .section-title {
    font-size: 28px;
  }

  .cta-buttons {
    flex-direction: column;
    align-items: center;
  }
}
</style>