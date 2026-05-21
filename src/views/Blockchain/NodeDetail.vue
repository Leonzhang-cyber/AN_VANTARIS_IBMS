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
        <div class="loading-tip">Blockchain Private Chain</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="simple-dashboard">
    <!-- Header -->
    <div class="dashboard-header">
      <div class="title-section">
        <h1>Blockchain Private Chain</h1>
        <div class="badges">
          <el-tag size="small" type="success">Clique PoA</el-tag>
          <el-tag size="small" type="info">Chain ID: 9527</el-tag>
          <el-tag size="small">Block Interval: 5s</el-tag>
        </div>
      </div>
      <div class="stats">
        <div class="stat">
          <div class="stat-value" :class="{ active: scheduler.isRunning }">
            {{ scheduler.isRunning ? 'Mining' : 'Idle' }}
          </div>
          <div class="stat-label">Mining Status</div>
        </div>
        <div class="stat">
          <div class="stat-value active">Enabled</div>
          <div class="stat-label">Production</div>
        </div>
        <div class="stat">
          <div class="stat-value">6/6</div>
          <div class="stat-label">Healthy Nodes</div>
        </div>
        <div class="stat">
          <div class="stat-value">#{{ currentBlockHeight }}</div>
          <div class="stat-label">Chain Height</div>
        </div>
      </div>
    </div>

    <!-- 拓扑图 - 节点关系可视化（可拖拽） -->
    <div class="topology-section">
      <div class="topology-header">
        <span>🔗 Blockchain Node Topology</span>
        <div class="topology-legend">
          <span class="legend-dot sealer"></span><span>Current Sealer</span>
          <span class="legend-dot peer"></span><span>P2P Connection</span>
          <span class="legend-dot mining"></span><span>Mining Node</span>
        </div>
        <div class="topology-controls">
          <el-button size="small" text @click="resetTopologyView">
            <el-icon><Refresh /></el-icon> Reset View
          </el-button>
        </div>
      </div>
      <div class="topology-canvas" ref="topologyRef">
        <VueFlow
            v-model="flowNodes"
            v-model:edges="flowEdges"
            class="vue-flow-wrapper"
            :default-viewport="{ zoom: 0.8, x: 50, y: 50 }"
            :fit-view-on-init="true"
            :nodes-draggable="true"
            :zoom-on-scroll="true"
            :pan-on-scroll="false"
            :min-zoom="0.5"
            :max-zoom="1.5"
            @node-drag-start="handleNodeDragStart"
            @node-drag-stop="handleNodeDragStop"
        >
          <template #node-custom="nodeProps">
            <div
                class="topology-node"
                :class="{
                  'is-sealer': nodeProps.data.isCurrentSealer,
                  'is-mining': nodeProps.data.isMining
                }"
            >
              <div class="node-icon">⛓️</div>
              <div class="node-name">{{ nodeProps.data.label }}</div>
              <div class="node-address">{{ shortenAddress(nodeProps.data.address, 8) }}</div>
              <div class="node-status">
                <span class="status-dot online"></span>
                <span>Online</span>
              </div>
              <div v-if="nodeProps.data.isCurrentSealer" class="sealer-badge">
                ⛏️ Sealing
              </div>
              <div v-else-if="nodeProps.data.isMining" class="mining-badge">
                ⚙️ Mining
              </div>
            </div>
          </template>
        </VueFlow>
      </div>
    </div>

    <!-- Six Nodes -->
    <div class="nodes-container">
      <el-card
          v-for="node in nodes"
          :key="node.id"
          class="node-card"
          :class="{ 'node-sealing': currentSealer === node.address && scheduler.isRunning }"
          shadow="hover"
      >
        <div class="node-header">
          <div class="node-name">
            <strong>{{ node.name }}</strong>
            <el-tag type="success" size="small">Online</el-tag>
          </div>
          <div class="node-ports">
            <span>RPC: {{ node.rpcPort }}</span>
            <span>P2P: {{ node.p2pPort }}</span>
          </div>
        </div>
        <div class="node-body">
          <div class="info-row">
            <span class="label">Signer</span>
            <span class="value mono">{{ shortenAddress(node.address) }}</span>
          </div>
          <div class="info-row">
            <span class="label">Balance</span>
            <span class="value">{{ node.balance }}</span>
          </div>
          <div class="info-row">
            <span class="label">Block Height</span>
            <span class="value">#{{ currentBlockHeight }}</span>
          </div>
          <div class="info-row">
            <span class="label">Peers</span>
            <span class="value">{{ node.peers }}/5</span>
          </div>
          <div class="info-row">
            <span class="label">Mining</span>
            <el-tag :type="node.isMining ? 'success' : 'info'" size="small">
              {{ node.isMining ? 'Yes' : 'No' }}
            </el-tag>
          </div>
        </div>
        <div v-if="currentSealer === node.address && scheduler.isRunning" class="sealing-badge">
          ⛏️ Sealing Now
        </div>
      </el-card>
    </div>

    <!-- Scheduler & Recent Blocks -->
    <div class="info-row-grid">
      <el-card class="scheduler-card">
        <template #header>
          <span>⛏️ Mining Scheduler</span>
        </template>
        <div class="scheduler-content">
          <div class="timer-section">
            <div class="timer-label">Idle Timer</div>
            <el-progress
                :percentage="scheduler.idleProgress"
                :format="() => `${scheduler.idleSeconds}s / 600s`"
                :color="scheduler.idleSeconds > 500 ? '#f56c6c' : '#67c23a'"
            />
          </div>
          <div class="scheduler-info">
            <div class="info-item">
              <span>Status:</span>
              <el-tag :type="scheduler.isRunning ? 'success' : 'info'" size="small">
                {{ scheduler.isRunning ? 'Running' : 'Stopped' }}
              </el-tag>
            </div>
            <div class="info-item">
              <span>Last Write Request:</span>
              <span class="mono">{{ scheduler.lastWriteRequest || 'None' }}</span>
            </div>
            <div class="info-item">
              <span>Auto-start:</span>
              <span>On write request</span>
            </div>
            <div class="info-item">
              <span>Auto-stop:</span>
              <span>After 10 minutes idle</span>
            </div>
          </div>
        </div>
      </el-card>

      <el-card class="blocks-card">
        <template #header>
          <span>🔄 Recent Blocks (Round-Robin)</span>
        </template>
        <div class="blocks-list">
          <div v-for="block in recentBlocks" :key="block.number" class="block-item">
            <div class="block-number">#{{ block.number }}</div>
            <div class="block-sealer">{{ block.sealerName }}</div>
            <div class="block-time">{{ block.time }}</div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Anchoring Records -->
    <el-card class="anchoring-card">
      <template #header>
        <span>📜 Anchoring Records · IBMSAnchor.sol</span>
      </template>
      <div class="records-list">
        <div v-for="(record, idx) in anchoringRecords" :key="idx" class="record-item">
          <div class="record-operation">{{ record.operation }}</div>
          <div class="record-details">
            <span class="record-tx">{{ shortenAddress(record.txHash, 12) }}</span>
            <span class="record-block">Block #{{ record.blockNumber }}</span>
          </div>
          <div class="record-time">{{ record.timestamp }}</div>
        </div>
      </div>
    </el-card>

    <!-- Blockchain Logs Console -->
    <el-card class="logs-card">
      <template #header>
        <div class="logs-header">
          <span>📋 Blockchain Private Chain Logs</span>
          <el-tag size="small" type="info">Live</el-tag>
        </div>
      </template>
      <div class="logs-container" ref="logsContainer">
        <div v-for="(log, idx) in blockchainLogs" :key="idx" class="log-entry" :class="log.type">
          <div class="log-header">
            <span class="log-time">{{ log.timestamp }}</span>
            <span class="log-level" :class="log.type">[{{ log.level }}]</span>
          </div>
          <div class="log-message">{{ log.message }}</div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { VueFlow, useVueFlow } from '@vue-flow/core'
import type { Node, Edge } from '@vue-flow/core'
import '@vue-flow/core/dist/style.css'
import '@vue-flow/core/dist/theme-default.css'
import { Refresh } from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isPageLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing assets...')

const loadingMessages = [
  'Preparing assets...',
  'Initializing blockchain...',
  'Connecting to nodes...',
  'Starting consensus...',
  'Loading dashboard...',
  'Almost ready...'
]

// ==================== 6个节点数据 ====================
const nodeAddresses = [
  '0x9AA128582b17C0c0143690F24012C8DBCf24767f',
  '0x7f3a4BA632Bc3a88a9c3489613b1CF529C8371Ca',
  '0x1f2d638ebe2fB97082c804213f9ED4ddA423cA43',
  '0x3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b',
  '0x4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c',
  '0x5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d'
]
const nodeNames = [
  'geth-node1', 'geth-node2', 'geth-node3',
  'geth-node4', 'geth-node5', 'geth-node6'
]

interface NodeData {
  id: number
  name: string
  rpcPort: number
  p2pPort: number
  address: string
  balance: string
  isMining: boolean
  peers: number
}

interface BlockRecord {
  number: number
  sealer: string
  sealerName: string
  time: string
}

interface LogEntry {
  timestamp: string
  level: 'INFO' | 'WARN' | 'ERROR' | 'SUCCESS'
  message: string
  type: string
}

const nodes = ref<NodeData[]>([])
const currentSealer = ref('')
const currentBlockHeight = ref(148)
const recentBlocks = ref<BlockRecord[]>([])
const blockchainLogs = ref<LogEntry[]>([])
const logsContainer = ref<HTMLElement | null>(null)

// 拓扑图相关
const topologyRef = ref<HTMLElement | null>(null)
const flowNodes = ref<Node[]>([])
const flowEdges = ref<Edge[]>([])
const nodePositionsCache = ref<Map<string, { x: number; y: number }>>(new Map())

const scheduler = ref({
  isRunning: true,
  idleSeconds: 0,
  idleProgress: 0,
  lastWriteRequest: new Date().toLocaleTimeString(),
})

const anchoringRecords = ref([
  { operation: 'DID Entity Registration', txHash: '0x1a2b3c4d5e6f7g8h9i0j', blockNumber: 124, timestamp: '2025-04-17 14:23:10' },
  { operation: 'VC Issuance Anchor', txHash: '0x5e6f7g8h9i0j1k2l3m4n', blockNumber: 129, timestamp: '2025-04-17 14:25:30' },
  { operation: 'Entity Attribute Update', txHash: '0x9i0j1k2l3m4n5o6p7q8r', blockNumber: 135, timestamp: '2025-04-17 14:28:15' },
  { operation: 'DID Entity Registration', txHash: '0x2a3b4c5d6e7f8g9h0i1j', blockNumber: 141, timestamp: '2025-04-17 14:32:20' },
  { operation: 'VC Issuance Anchor', txHash: '0x3b4c5d6e7f8g9h0i1j2k', blockNumber: 147, timestamp: '2025-04-17 14:36:45' },
])

const shortenAddress = (addr: string, len = 6) => {
  if (!addr) return ''
  return `${addr.slice(0, len)}...${addr.slice(-4)}`
}

// 计算6个节点的圆形布局位置
const calculateCircularPositions = (centerX: number, centerY: number, radius: number, count: number) => {
  const positions = []
  const angleStep = (Math.PI * 2) / count
  for (let i = 0; i < count; i++) {
    const angle = i * angleStep - Math.PI / 2 // 从顶部开始
    positions.push({
      x: centerX + radius * Math.cos(angle),
      y: centerY + radius * Math.sin(angle)
    })
  }
  return positions
}

// 更新拓扑图节点和边
const updateTopology = () => {
  const count = nodes.value.length
  const positions = calculateCircularPositions(400, 200, 180, count)

  // 更新节点，保留用户拖拽过的位置
  flowNodes.value = nodes.value.map((node, idx) => {
    const cachedPos = nodePositionsCache.value.get(node.address)
    return {
      id: node.address,
      type: 'custom',
      position: cachedPos || positions[idx],
      data: {
        label: node.name,
        address: node.address,
        isCurrentSealer: currentSealer.value === node.address,
        isMining: scheduler.value.isRunning && currentSealer.value === node.address,
      }
    }
  })

  // 更新边（P2P 全连接：每对节点之间都有连接）
  const edges: Edge[] = []
  for (let i = 0; i < nodes.value.length; i++) {
    for (let j = i + 1; j < nodes.value.length; j++) {
      edges.push({
        id: `edge-${i}-${j}`,
        source: nodes.value[i].address,
        target: nodes.value[j].address,
        animated: true,
        style: { stroke: '#67c23a', strokeWidth: 2 },
        label: 'P2P',
        labelStyle: { fill: '#67c23a', fontSize: 10 }
      })
    }
  }
  flowEdges.value = edges
}

// 重置拓扑图视图
const resetTopologyView = () => {
  nodePositionsCache.value.clear()
  updateTopology()
}

// 拖拽事件：保存节点位置
const handleNodeDragStart = (event: any) => {
  // 拖拽开始时的处理
}

const handleNodeDragStop = (event: any) => {
  if (event.node) {
    nodePositionsCache.value.set(event.node.id, {
      x: event.node.position.x,
      y: event.node.position.y
    })
  }
}

// 监听 currentSealer 变化，更新拓扑图高亮
watch(currentSealer, () => {
  updateTopology()
})

// 监听 scheduler.isRunning 变化
watch(() => scheduler.value.isRunning, () => {
  updateTopology()
})

const addLog = (level: 'INFO' | 'WARN' | 'ERROR' | 'SUCCESS', message: string) => {
  const now = new Date()
  const timestamp = now.toLocaleTimeString()
  let type = ''
  if (level === 'INFO') type = 'log-info'
  else if (level === 'WARN') type = 'log-warn'
  else if (level === 'ERROR') type = 'log-error'
  else if (level === 'SUCCESS') type = 'log-success'

  blockchainLogs.value.unshift({
    timestamp,
    level,
    message,
    type,
  })

  if (blockchainLogs.value.length > 100) {
    blockchainLogs.value.pop()
  }

  nextTick(() => {
    if (logsContainer.value) {
      logsContainer.value.scrollTop = 0
    }
  })
}

const addRecentBlock = (blockNum: number, sealerAddr: string, sealerName: string) => {
  recentBlocks.value.unshift({
    number: blockNum,
    sealer: sealerAddr,
    sealerName,
    time: new Date().toLocaleTimeString(),
  })
  if (recentBlocks.value.length > 12) recentBlocks.value.pop()
}

const sealNewBlock = () => {
  const runningNodes = nodes.value
  const currentIdx = runningNodes.findIndex(n => n.address === currentSealer.value)
  const nextIdx = (currentIdx + 1) % runningNodes.length
  const nextNode = runningNodes[nextIdx]

  currentBlockHeight.value++
  currentSealer.value = nextNode.address

  // 更新节点的挖矿状态
  nodes.value.forEach(node => {
    node.isMining = (node.address === currentSealer.value)
  })

  addRecentBlock(currentBlockHeight.value, nextNode.address, nextNode.name)
  addLog('SUCCESS', `Block #${currentBlockHeight.value} sealed by ${nextNode.name} (${shortenAddress(nextNode.address)})`)

  scheduler.value.idleSeconds = 0
  scheduler.value.idleProgress = 0
  updateTopology()
}

const simulateWriteRequest = async () => {
  if (!scheduler.value.isRunning) {
    scheduler.value.isRunning = true
    addLog('INFO', 'Mining scheduler ACTIVATED by write request')
    updateTopology()
  }

  scheduler.value.idleSeconds = 0
  scheduler.value.idleProgress = 0
  scheduler.value.lastWriteRequest = new Date().toLocaleTimeString()

  addLog('INFO', `Write request received: DID Entity Registration (tx: 0x${Math.random().toString(36).substring(2, 10)}...)`)

  await new Promise(resolve => setTimeout(resolve, 800))

  const runningNodes = nodes.value
  const sealerNode = runningNodes.find(n => n.address === currentSealer.value) || runningNodes[0]

  currentBlockHeight.value++
  addRecentBlock(currentBlockHeight.value, sealerNode.address, sealerNode.name)
  addLog('SUCCESS', `Transaction confirmed. Block #${currentBlockHeight.value} sealed by ${sealerNode.name}`)

  const nextIdx = (runningNodes.findIndex(n => n.address === currentSealer.value) + 1) % runningNodes.length
  currentSealer.value = runningNodes[nextIdx].address

  // 更新节点的挖矿状态
  nodes.value.forEach(node => {
    node.isMining = (node.address === currentSealer.value)
  })

  updateTopology()

  anchoringRecords.value.unshift({
    operation: 'DID Entity Registration (TX)',
    txHash: `0x${Math.random().toString(36).substring(2, 14)}`,
    blockNumber: currentBlockHeight.value,
    timestamp: new Date().toLocaleString(),
  })

  if (anchoringRecords.value.length > 10) anchoringRecords.value.pop()
}

let idleInterval: ReturnType<typeof setInterval>
let miningInterval: ReturnType<typeof setInterval>
let writeRequestInterval: ReturnType<typeof setInterval>

const startIdleTimer = () => {
  idleInterval = setInterval(() => {
    if (scheduler.value.isRunning) {
      scheduler.value.idleSeconds += 2
      scheduler.value.idleProgress = (scheduler.value.idleSeconds / 600) * 100
      if (scheduler.value.idleSeconds >= 600) {
        scheduler.value.isRunning = false
        addLog('INFO', 'Idle timeout reached (10 minutes). Mining scheduler STOPPED automatically.')

        // 停止挖矿时，清除所有节点的挖矿状态
        nodes.value.forEach(node => {
          node.isMining = false
        })
        updateTopology()
      }
    } else if (!scheduler.value.isRunning && scheduler.value.idleSeconds > 0) {
      scheduler.value.idleSeconds = Math.max(0, scheduler.value.idleSeconds - 1)
      scheduler.value.idleProgress = (scheduler.value.idleSeconds / 600) * 100
    }
  }, 2000)
}

const initData = () => {
  // 初始化6个节点
  nodes.value = nodeAddresses.map((addr, idx) => ({
    id: idx + 1,
    name: nodeNames[idx],
    rpcPort: 8545 + idx,
    p2pPort: 30303 + idx,
    address: addr,
    balance: '100.00 ETH',
    isMining: idx === 0,
    peers: 5,
  }))

  currentSealer.value = nodeAddresses[0]
  currentBlockHeight.value = 178

  // 初始化最近区块记录
  recentBlocks.value = []
  for (let i = 0; i < 12; i++) {
    const sealerIdx = (i % 6)
    recentBlocks.value.push({
      number: currentBlockHeight.value - i,
      sealer: nodeAddresses[sealerIdx],
      sealerName: nodeNames[sealerIdx],
      time: new Date(Date.now() - i * 6000).toLocaleTimeString(),
    })
  }

  // 初始化拓扑图
  updateTopology()

  addLog('INFO', 'Blockchain Private Chain initialized (Clique PoA, Chain ID: 9527)')
  addLog('INFO', 'Six Geth nodes running in full mesh topology')
  addLog('INFO', 'Genesis block loaded with 6 signers (100 ETH each)')
  addLog('INFO', 'P2P connections established: all nodes have 5 peers')
  addLog('INFO', 'Mining scheduler running in ACTIVE mode')
  addLog('INFO', 'Round-robin sealing in progress - blocks sealed every 6 seconds')
}

// ==================== Loading ====================
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
      nextTick(() => {
        setTimeout(() => {
          initData()
        }, 100)
      })
    }, 500)
  }, 2500)
}

onMounted(() => {
  startLoading()
  startIdleTimer()
  miningInterval = setInterval(() => {
    if (scheduler.value.isRunning) {
      sealNewBlock()
    }
  }, 6000)
  writeRequestInterval = setInterval(() => {
    simulateWriteRequest()
  }, 35000)
})

onUnmounted(() => {
  if (idleInterval) clearInterval(idleInterval)
  if (miningInterval) clearInterval(miningInterval)
  if (writeRequestInterval) clearInterval(writeRequestInterval)
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

/* ==================== Main Dashboard Styles ==================== */
.simple-dashboard {
  padding: 12px;
  background: #ffffff;
  min-height: 100vh;
}

/* Header */
.dashboard-header {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 16px;
}

.title-section h1 {
  margin: 0 0 6px 0;
  font-size: 20px;
  color: #303133;
}

.badges {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.stats {
  display: flex;
  justify-content: space-around;
  background: #f5f7fa;
  padding: 10px 12px;
  border-radius: 8px;
}

.stat {
  text-align: center;
}

.stat-value {
  font-size: 16px;
  font-weight: 600;
  color: #909399;
}

.stat-value.active {
  color: #67c23a;
}

.stat-label {
  font-size: 10px;
  color: #909399;
  margin-top: 2px;
}

/* ========== 拓扑图样式 ========== */
.topology-section {
  background: #f5f7fa;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 20px;
  border: 1px solid #e4e7ed;
}

.topology-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  flex-wrap: wrap;
  gap: 12px;
}

.topology-legend {
  display: flex;
  gap: 16px;
  font-size: 12px;
  font-weight: normal;
}

.legend-dot {
  display: inline-block;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  margin-right: 4px;
  vertical-align: middle;
}

.legend-dot.sealer {
  background: #409eff;
  box-shadow: 0 0 6px #409eff;
}

.legend-dot.peer {
  background: #67c23a;
}

.legend-dot.mining {
  background: #e6a23c;
  animation: pulse 1.5s infinite;
}

.topology-controls {
  display: flex;
  gap: 8px;
}

.topology-canvas {
  min-height: 600px;
  width: 100%;
  background: #ffffff;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
  overflow: hidden;
}

.vue-flow-wrapper {
  width: 100%;
  height: 100%;
}

/* 拓扑图节点样式 */
.topology-node {
  width: 140px;
  padding: 12px;
  background: #ffffff;
  border: 2px solid #e4e7ed;
  border-radius: 12px;
  text-align: center;
  transition: all 0.3s ease;
  cursor: grab;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.topology-node:active {
  cursor: grabbing;
}

.topology-node:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.topology-node.is-sealer {
  border-color: #409eff;
  background: linear-gradient(135deg, #ecf5ff 0%, #ffffff 100%);
  box-shadow: 0 0 12px rgba(64, 158, 255, 0.3);
}

.topology-node.is-mining {
  border-color: #e6a23c;
  background: linear-gradient(135deg, #fdf6ec 0%, #ffffff 100%);
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(64, 158, 255, 0.4); }
  50% { box-shadow: 0 0 0 8px rgba(64, 158, 255, 0); }
}

.node-icon {
  font-size: 28px;
  margin-bottom: 6px;
}

.node-name {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.node-address {
  font-size: 10px;
  font-family: monospace;
  color: #909399;
  margin-bottom: 6px;
}

.node-status {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  font-size: 10px;
  color: #67c23a;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #67c23a;
  animation: blink 1s infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.sealer-badge, .mining-badge {
  margin-top: 8px;
  font-size: 10px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 12px;
  display: inline-block;
}

.sealer-badge {
  color: #409eff;
  background: #ecf5ff;
}

.mining-badge {
  color: #e6a23c;
  background: #fdf6ec;
}

/* 节点卡片样式 */
.nodes-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 16px;
}

.node-card {
  border-top: 3px solid #67c23a;
  transition: all 0.2s;
}

.node-card.node-sealing {
  border-top-color: #409eff;
  box-shadow: 0 2px 8px 0 rgba(64, 158, 255, 0.2);
}

.node-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  flex-wrap: wrap;
  gap: 6px;
}

.node-name {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
}

.node-ports {
  display: flex;
  gap: 8px;
  font-size: 10px;
  color: #909399;
}

.node-body {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
}

.label {
  font-size: 12px;
  color: #606266;
}

.value {
  font-size: 12px;
  color: #303133;
}

.mono {
  font-family: monospace;
  font-size: 10px;
}

.sealing-badge {
  margin-top: 10px;
  text-align: center;
  font-size: 11px;
  color: #409eff;
  font-weight: 500;
  padding: 4px;
  background: #ecf5ff;
  border-radius: 4px;
}

.info-row-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 16px;
}

.scheduler-card, .blocks-card, .anchoring-card, .logs-card {
  margin-bottom: 0;
}

.scheduler-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.timer-label {
  font-size: 12px;
  color: #606266;
  margin-bottom: 6px;
}

.scheduler-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  flex-wrap: wrap;
  gap: 6px;
}

.info-item span:first-child {
  color: #909399;
}

.blocks-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  max-height: 200px;
  overflow-y: auto;
}

.blocks-list::-webkit-scrollbar {
  width: 3px;
}

.block-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 10px;
  background: #f5f7fa;
  border-radius: 6px;
  font-size: 11px;
}

.block-number {
  font-weight: 600;
  color: #409eff;
  font-family: monospace;
}

.block-sealer {
  font-size: 11px;
  color: #606266;
}

.block-time {
  font-size: 10px;
  color: #909399;
}

.records-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.record-item {
  padding: 10px;
  background: #f5f7fa;
  border-radius: 8px;
}

.record-operation {
  font-weight: 600;
  font-size: 12px;
  color: #303133;
  margin-bottom: 6px;
}

.record-details {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
  font-size: 10px;
}

.record-tx {
  font-family: monospace;
  color: #409eff;
}

.record-block {
  color: #909399;
}

.record-time {
  font-size: 10px;
  color: #c0c4cc;
}

.logs-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logs-container {
  height: 260px;
  overflow-y: auto;
  background: #ffffff;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  padding: 10px;
  font-size: 11px;
}

.log-entry {
  padding: 8px;
  border-bottom: 1px solid #f0f0f0;
}

.log-entry:last-child {
  border-bottom: none;
}

.log-header {
  display: flex;
  gap: 10px;
  margin-bottom: 4px;
  flex-wrap: wrap;
}

.log-time {
  color: #909399;
  font-size: 10px;
  font-family: monospace;
}

.log-level {
  font-weight: 600;
  font-size: 11px;
}

.log-message {
  color: #606266;
  word-break: break-all;
  line-height: 1.4;
  font-size: 11px;
}

.log-entry.log-info .log-level {
  color: #409eff;
}
.log-entry.log-success .log-level {
  color: #67c23a;
}
.log-entry.log-warn .log-level {
  color: #e6a23c;
}
.log-entry.log-error .log-level {
  color: #f56c6c;
}

.log-entry.log-success .log-message {
  color: #529b2e;
}
.log-entry.log-warn .log-message {
  color: #c28c1f;
}
.log-entry.log-error .log-message {
  color: #c45656;
}

.logs-container::-webkit-scrollbar {
  width: 4px;
}

/* Desktop 样式 */
@media (min-width: 768px) {
  .simple-dashboard {
    padding: 24px;
  }

  .dashboard-header {
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
  }

  .stats {
    gap: 32px;
    padding: 12px 24px;
  }

  .stat-value {
    font-size: 20px;
  }

  .nodes-container {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
  }

  .info-row-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 20px;
    flex-direction: row;
  }

  .node-ports {
    font-size: 12px;
  }

  .mono {
    font-size: 12px;
  }

  .info-item {
    font-size: 13px;
  }

  .record-operation {
    font-size: 13px;
  }

  .record-details {
    font-size: 12px;
  }

  .log-entry {
    display: flex;
    gap: 12px;
    align-items: flex-start;
  }

  .log-header {
    flex-shrink: 0;
    min-width: 130px;
    margin-bottom: 0;
  }

  .log-message {
    flex: 1;
  }

  .topology-canvas {
    height: 420px;
  }
}

/* 移动端拓扑图高度调整 */
@media (max-width: 768px) {
  .topology-canvas {
    height: 320px;
  }

  .topology-node {
    width: 110px;
    padding: 8px;
  }

  .node-name {
    font-size: 11px;
  }

  .node-icon {
    font-size: 22px;
  }

  .nodes-container {
    gap: 12px;
  }
}

/* VueFlow 样式覆盖 */
:deep(.vue-flow__edge-path) {
  stroke-dasharray: 5;
}

:deep(.vue-flow__edge-label) {
  font-size: 10px;
  fill: #67c23a;
}

:deep(.vue-flow__minimap) {
  background-color: #f5f7fa;
  border: 1px solid #e4e7ed;
}
</style>