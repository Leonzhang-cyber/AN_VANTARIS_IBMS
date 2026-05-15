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

    <!-- Three Nodes - All show SAME block height -->
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
    <el-row :gutter="20" class="info-row">
      <el-col :span="12">
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
      </el-col>
      <el-col :span="12">
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
      </el-col>
    </el-row>

    <!-- Anchoring Records -->
    <el-card class="anchoring-card">
      <template #header>
        <span>📜 Anchoring Records · IMBSAnchor.sol</span>
      </template>
      <el-table :data="anchoringRecords" stripe size="small">
        <el-table-column prop="operation" label="Operation" />
        <el-table-column prop="txHash" label="Transaction Hash" :formatter="(row) => shortenAddress(row.txHash, 12)" />
        <el-table-column prop="blockNumber" label="Block" width="100" />
        <el-table-column prop="timestamp" label="Timestamp" width="170" />
      </el-table>
    </el-card>

    <!-- Blockchain Logs Console - White background -->
    <el-card class="logs-card">
      <template #header>
        <div class="logs-header">
          <span>📋 Blockchain Private Chain Logs</span>
          <el-tag size="small" type="info">Live</el-tag>
        </div>
      </template>
      <div class="logs-container-white" ref="logsContainer">
        <div v-for="(log, idx) in blockchainLogs" :key="idx" class="log-entry-white" :class="log.type">
          <span class="log-time-white">{{ log.timestamp }}</span>
          <span class="log-level-white" :class="log.type">[{{ log.level }}]</span>
          <span class="log-message-white">{{ log.message }}</span>
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
  isRunning: true,  // 默认运行，模拟正常挖矿
  idleSeconds: 0,
  idleProgress: 0,
  lastWriteRequest: new Date().toLocaleTimeString(),
})

// 所有节点正常，始终可出块
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

// 轮流出块
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

// 模拟写请求
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
}

// 空闲计时器
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

  // 自动出块（每6秒）
  miningInterval = setInterval(() => {
    if (scheduler.value.isRunning) {
      sealNewBlock()
    }
  }, 6000)

  // 模拟写请求（每35秒）
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
  padding: 24px;
  background: #ffffff;
  min-height: 100vh;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.title-section h1 {
  margin: 0 0 8px 0;
  font-size: 24px;
  color: #303133;
}

.badges {
  display: flex;
  gap: 8px;
}

.stats {
  display: flex;
  gap: 32px;
  background: #f5f7fa;
  padding: 12px 24px;
  border-radius: 8px;
}

.stat {
  text-align: center;
}

.stat-value {
  font-size: 20px;
  font-weight: 600;
  color: #909399;
}

.stat-value.active {
  color: #67c23a;
}

.stat-label {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.nodes-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.node-card {
  border-top: 3px solid #67c23a;
  transition: all 0.2s;
}

.node-card.node-sealing {
  border-top-color: #409eff;
  box-shadow: 0 2px 12px 0 rgba(64, 158, 255, 0.2);
}

.node-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 8px;
}

.node-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.node-ports {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: #909399;
}

.node-body {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.label {
  font-size: 13px;
  color: #606266;
}

.value {
  font-size: 13px;
  color: #303133;
}

.mono {
  font-family: monospace;
}

.sealing-badge {
  margin-top: 12px;
  text-align: center;
  font-size: 12px;
  color: #409eff;
  font-weight: 500;
  padding: 4px;
  background: #ecf5ff;
  border-radius: 4px;
}

.scheduler-card, .blocks-card, .anchoring-card, .logs-card {
  margin-bottom: 20px;
}

.scheduler-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-height: 180px;
  max-height: 180px;
}

.timer-section {
  width: 100%;
}

.timer-label {
  font-size: 13px;
  color: #606266;
  margin-bottom: 8px;
}

.scheduler-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
}

.info-item span:first-child {
  color: #909399;
}

.mono {
  font-family: monospace;
  color: #303133;
}

.blocks-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 180px;
  min-height: 180px;
  overflow-y: auto;
}

/* 隐藏滚动条但保留滚动功能 - WebKit浏览器 (Chrome, Safari, Edge) */
.blocks-list::-webkit-scrollbar {
  width: 0;
  height: 0;
  display: none;
}

.block-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #f5f7fa;
  border-radius: 6px;
}

.block-number {
  font-weight: 600;
  color: #409eff;
  font-family: monospace;
}

.block-sealer {
  font-size: 13px;
  color: #606266;
}

.block-time {
  font-size: 12px;
  color: #909399;
}

/* Logs Console - White Background Styles */
.logs-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logs-container-white {
  height: 280px;
  overflow-y: auto;
  background: #ffffff;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  padding: 12px;
  font-family: 'Courier New', 'Fira Code', monospace;
  font-size: 12px;
}

.log-entry-white {
  display: flex;
  gap: 12px;
  padding: 6px 8px;
  border-bottom: 1px solid #f0f0f0;
  font-family: monospace;
  font-size: 12px;
}

.log-entry-white:last-child {
  border-bottom: none;
}

.log-time-white {
  color: #909399;
  min-width: 70px;
  flex-shrink: 0;
}

.log-level-white {
  min-width: 60px;
  flex-shrink: 0;
  font-weight: 600;
}

.log-message-white {
  color: #303133;
  word-break: break-all;
  flex: 1;
}

.log-entry-white.log-info .log-level-white {
  color: #409eff;
}

.log-entry-white.log-success .log-level-white {
  color: #67c23a;
}

.log-entry-white.log-warn .log-level-white {
  color: #e6a23c;
}

.log-entry-white.log-error .log-level-white {
  color: #f56c6c;
}

.log-message-white {
  color: #606266;
}

.log-entry-white.log-success .log-message-white {
  color: #529b2e;
}

.log-entry-white.log-warn .log-message-white {
  color: #c28c1f;
}

.log-entry-white.log-error .log-message-white {
  color: #c45656;
}

/* Custom scrollbar for logs */
.logs-container-white::-webkit-scrollbar {
  width: 6px;
}

.logs-container-white::-webkit-scrollbar-track {
  background: #f0f0f0;
  border-radius: 3px;
}

.logs-container-white::-webkit-scrollbar-thumb {
  background: #c0c4cc;
  border-radius: 3px;
}

.logs-container-white::-webkit-scrollbar-thumb:hover {
  background: #909399;
}
</style>