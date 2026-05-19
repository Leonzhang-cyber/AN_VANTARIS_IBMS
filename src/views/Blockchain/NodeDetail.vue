<template>
  <div class="simple-dashboard">
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
          <div class="stat-value">3/3</div>
          <div class="stat-label">Healthy Nodes</div>
        </div>
        <div class="stat">
          <div class="stat-value">#{{ currentBlockHeight }}</div>
          <div class="stat-label">Chain Height</div>
        </div>
      </div>
    </div>

    <!-- Three Nodes -->
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
            <span class="value">{{ node.peers }}</span>
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
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'

interface Node {
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

const nodeAddresses = [
  '0x9AA128582b17C0c0143690F24012C8DBCf24767f',
  '0x7f3a4BA632Bc3a88a9c3489613b1CF529C8371Ca',
  '0x1f2d638ebe2fB97082c804213f9ED4ddA423cA43',
]
const nodeNames = ['geth-node1', 'geth-node2', 'geth-node3']

const nodes = ref<Node[]>([])
const currentSealer = ref('')
const currentBlockHeight = ref(121)
const recentBlocks = ref<BlockRecord[]>([])
const blockchainLogs = ref<LogEntry[]>([])
const logsContainer = ref<HTMLElement | null>(null)

const scheduler = ref({
  isRunning: true,
  idleSeconds: 0,
  idleProgress: 0,
  lastWriteRequest: new Date().toLocaleTimeString(),
})

const canProduceBlocks = computed(() => true)

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
  if (recentBlocks.value.length > 8) recentBlocks.value.pop()
}

const sealNewBlock = () => {
  const runningNodes = nodes.value
  const currentIdx = runningNodes.findIndex(n => n.address === currentSealer.value)
  const nextIdx = (currentIdx + 1) % runningNodes.length
  const nextNode = runningNodes[nextIdx]

  currentBlockHeight.value++
  currentSealer.value = nextNode.address
  addRecentBlock(currentBlockHeight.value, nextNode.address, nextNode.name)
  addLog('SUCCESS', `Block #${currentBlockHeight.value} sealed by ${nextNode.name} (${shortenAddress(nextNode.address)})`)

  scheduler.value.idleSeconds = 0
  scheduler.value.idleProgress = 0
}

const simulateWriteRequest = async () => {
  if (!scheduler.value.isRunning) {
    scheduler.value.isRunning = true
    addLog('INFO', 'Mining scheduler ACTIVATED by write request')
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
      }
    } else if (!scheduler.value.isRunning && scheduler.value.idleSeconds > 0) {
      scheduler.value.idleSeconds = Math.max(0, scheduler.value.idleSeconds - 1)
      scheduler.value.idleProgress = (scheduler.value.idleSeconds / 600) * 100
    }
  }, 2000)
}

const initData = () => {
  nodes.value = nodeAddresses.map((addr, idx) => ({
    id: idx + 1,
    name: nodeNames[idx],
    rpcPort: 8545 + idx,
    p2pPort: 30303 + idx,
    address: addr,
    balance: '100.00 ETH',
    isMining: idx === 0,
    peers: 2,
  }))
  currentSealer.value = nodeAddresses[0]
  currentBlockHeight.value = 148
  recentBlocks.value = [
    { number: 147, sealer: nodeAddresses[1], sealerName: 'geth-node2', time: '14:36:45' },
    { number: 146, sealer: nodeAddresses[0], sealerName: 'geth-node1', time: '14:36:40' },
    { number: 145, sealer: nodeAddresses[2], sealerName: 'geth-node3', time: '14:36:35' },
    { number: 144, sealer: nodeAddresses[1], sealerName: 'geth-node2', time: '14:36:30' },
    { number: 143, sealer: nodeAddresses[0], sealerName: 'geth-node1', time: '14:36:25' },
    { number: 142, sealer: nodeAddresses[2], sealerName: 'geth-node3', time: '14:36:20' },
    { number: 141, sealer: nodeAddresses[1], sealerName: 'geth-node2', time: '14:36:15' },
    { number: 140, sealer: nodeAddresses[0], sealerName: 'geth-node1', time: '14:36:10' },
  ]

  addLog('INFO', 'Blockchain Private Chain initialized (Clique PoA, Chain ID: 9527)')
  addLog('INFO', 'Three Geth nodes running: geth-node1 (RPC:8545), geth-node2 (RPC:8546), geth-node3 (RPC:8547)')
  addLog('INFO', 'Genesis block loaded with 3 signers (100 ETH each)')
  addLog('INFO', 'P2P connections established: all nodes have 2 peers')
  addLog('INFO', 'Mining scheduler running in ACTIVE mode')
  addLog('INFO', 'Round-robin sealing in progress - blocks sealed every 6 seconds')
}

onMounted(() => {
  initData()
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

/* Nodes Container */
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

/* Info Row Grid */
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

/* Blocks List */
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

/* Records List */
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

/* Logs */
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

/* Desktop */
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
}
</style>