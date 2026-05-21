<template>
  <div v-if="isPageLoaded" class="smart-contracts-page">
    <div class="page-container">
      <!-- Page Header -->
      <div class="page-header">
        <div class="header-left">
          <h1>Smart Contracts</h1>
          <p>Manage and deploy smart contracts for automated business rules</p>
        </div>
        <div class="header-actions">
          <el-button type="primary" @click="openDeployWizard">
            <el-icon><Plus /></el-icon>
            Deploy New Contract
          </el-button>
        </div>
      </div>

      <!-- Stats Cards -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon blue"><el-icon><Document /></el-icon></div>
          <div class="stat-info">
            <span class="stat-value">{{ contractStats.total }}</span>
            <span class="stat-label">Total Contracts</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon green"><el-icon><Check /></el-icon></div>
          <div class="stat-info">
            <span class="stat-value">{{ contractStats.active }}</span>
            <span class="stat-label">Active Contracts</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon orange"><el-icon><Lightning /></el-icon></div>
          <div class="stat-info">
            <span class="stat-value">{{ contractStats.totalTriggers }}</span>
            <span class="stat-label">Total Triggers</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon purple"><el-icon><Coin /></el-icon></div>
          <div class="stat-info">
            <span class="stat-value">{{ contractStats.totalGas }} GWEI</span>
            <span class="stat-label">Gas Used</span>
          </div>
        </div>
      </div>

      <!-- Trigger Trend Chart -->
      <div class="chart-card">
        <div class="card-header">
          <span><el-icon><TrendCharts /></el-icon> Contract Trigger Trend (Last 7 Days)</span>
        </div>
        <div ref="trendChartRef" class="trend-chart" style="width: 100%; height: 320px;"></div>
      </div>

      <!-- Tab Navigation -->
      <el-tabs v-model="activeTab" class="custom-tabs">
        <!-- Template Library -->
        <el-tab-pane label="Template Library" name="templates">
          <div class="templates-grid">
            <div v-for="template in contractTemplates" :key="template.id" class="template-card">
              <div class="template-icon" :style="{ background: template.color }">
                <el-icon :size="28"><component :is="template.icon" /></el-icon>
              </div>
              <div class="template-info">
                <h3>{{ template.name }}</h3>
                <p>{{ template.description }}</p>
                <div class="template-params">
                  <el-tag v-for="param in template.params" :key="param" size="small" type="info">{{ param }}</el-tag>
                </div>
              </div>
              <div class="template-actions">
                <el-button type="primary" size="small" @click="useTemplate(template)">Use Template</el-button>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <!-- Deployed Contracts List -->
        <el-tab-pane label="Deployed Contracts" name="contracts">
          <el-table :data="deployedContracts" stripe style="width: 100%" class="equal-width-table">
            <el-table-column prop="name" label="Contract Name" min-width="120" show-overflow-tooltip />
            <el-table-column prop="address" label="Contract Address" min-width="160" show-overflow-tooltip>
              <template #default="{ row }">
                <span class="address-text">{{ row.address.slice(0, 10) }}...{{ row.address.slice(-6) }}</span>
                <el-icon class="copy-icon" @click="copyAddress(row.address)"><CopyDocument /></el-icon>
              </template>
            </el-table-column>
            <el-table-column prop="template" label="Template" min-width="120" show-overflow-tooltip />
            <el-table-column prop="status" label="Status" width="90" align="center">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)" size="small">{{ getStatusText(row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="triggerCount" label="Triggers" width="80" align="center" />
            <el-table-column prop="lastExecution" label="Last Execution" min-width="140" show-overflow-tooltip />
            <el-table-column label="Actions" width="260" fixed="right" align="center">
              <template #default="{ row }">
                <div class="action-buttons">
                  <el-button size="small" :type="row.status === 'active' ? 'warning' : 'success'" @click="toggleContractStatus(row)">
                    {{ row.status === 'active' ? 'Pause' : 'Start' }}
                  </el-button>
                  <el-button size="small" @click="viewContractDetail(row)">Details</el-button>
                  <el-button size="small" type="danger" @click="deleteContract(row)">Delete</el-button>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <!-- Oracle Config -->
        <el-tab-pane label="Oracle Configuration" name="oracle">
          <div class="oracle-config">
            <div class="oracle-header">
              <h3>External Data Sources</h3>
              <el-button type="primary" size="small" @click="addOracleSource">
                <el-icon><Plus /></el-icon> Add Data Source
              </el-button>
            </div>
            <div class="oracle-grid">
              <div v-for="source in oracleSources" :key="source.id" class="oracle-card">
                <div class="oracle-card-header">
                  <span class="oracle-name">{{ source.name }}</span>
                  <el-tag :type="source.status === 'online' ? 'success' : 'danger'" size="small">
                    {{ source.status }}
                  </el-tag>
                </div>
                <div class="oracle-url">{{ source.url }}</div>
                <div class="oracle-info">
                  <span>Update: {{ source.updateInterval }}</span>
                  <span>Last fetch: {{ source.lastFetch }}</span>
                </div>
                <div class="oracle-actions">
                  <el-button size="small" @click="testOracle(source)">Test Fetch</el-button>
                  <el-button size="small" type="danger" plain @click="deleteOracle(source.id)">Remove</el-button>
                </div>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <!-- Execution History -->
        <el-tab-pane label="Execution History" name="history">
          <div class="history-filters">
            <el-select v-model="historyFilterContract" placeholder="All Contracts" clearable style="width: 200px">
              <el-option v-for="c in deployedContracts" :key="c.id" :label="c.name" :value="c.id" />
            </el-select>
            <el-date-picker v-model="historyFilterDateRange" type="daterange" range-separator="-" start-placeholder="Start" end-placeholder="End" />
            <el-button type="primary" @click="exportHistory">Export CSV</el-button>
          </div>
          <el-table :data="filteredExecutionHistory" stripe style="width: 100%; margin-top: 16px" class="equal-width-table">
            <el-table-column prop="time" label="Time" min-width="140" show-overflow-tooltip />
            <el-table-column prop="contract" label="Contract" min-width="130" show-overflow-tooltip />
            <el-table-column prop="txHash" label="Transaction Hash" min-width="160" show-overflow-tooltip>
              <template #default="{ row }">
                <span class="address-text">{{ row.txHash.slice(0, 10) }}...{{ row.txHash.slice(-6) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="triggerCondition" label="Trigger Condition" min-width="160" show-overflow-tooltip />
            <el-table-column prop="result" label="Result" width="90" align="center">
              <template #default="{ row }">
                <el-tag :type="row.result === 'Success' ? 'success' : 'danger'" size="small">{{ row.result }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="gasFee" label="Gas Fee" width="90" align="center" />
            <el-table-column label="Details" width="80" align="center">
              <template #default="{ row }">
                <el-button size="small" text @click="viewTransactionDetail(row)">View</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </div>

    <!-- Deploy Wizard Dialog -->
    <el-dialog v-model="deployWizardVisible" title="Deploy New Contract" width="700px" destroy-on-close>
      <el-steps :active="deployStep" finish-status="success" align-center>
        <el-step title="Select Template" />
        <el-step title="Configure Parameters" />
        <el-step title="Network & Deploy" />
      </el-steps>

      <div class="wizard-content">
        <div v-if="deployStep === 0">
          <div class="template-select-grid">
            <div v-for="template in contractTemplates" :key="template.id" class="template-select-card" :class="{ selected: selectedTemplate?.id === template.id }" @click="selectedTemplate = template">
              <div class="template-select-icon" :style="{ background: template.color }">
                <el-icon :size="24"><component :is="template.icon" /></el-icon>
              </div>
              <div class="template-select-name">{{ template.name }}</div>
            </div>
          </div>
        </div>

        <div v-if="deployStep === 1 && selectedTemplate">
          <el-form :model="contractParams" label-width="140px">
            <el-form-item v-for="param in selectedTemplate.params" :key="param" :label="param">
              <el-input v-model="contractParams[param]" :placeholder="'Enter ' + param" />
            </el-form-item>
            <el-form-item label="Trigger Condition">
              <el-input type="textarea" v-model="contractParams.triggerCondition" rows="2" placeholder="e.g., electricity_price > 0.5 && battery_soc > 20" />
            </el-form-item>
            <el-form-item label="Execution Action">
              <el-input type="textarea" v-model="contractParams.action" rows="2" placeholder="e.g., discharge_battery(amount=100)" />
            </el-form-item>
          </el-form>
          <div class="simulate-section">
            <el-button type="success" plain @click="simulateContract">
              <el-icon><VideoPlay /></el-icon> Simulate Execution
            </el-button>
            <span v-if="simulateResultMsg" class="simulate-result" :class="simulateResultSuccess ? 'success' : 'error'">
              {{ simulateResultMsg }}
            </span>
          </div>
        </div>

        <div v-if="deployStep === 2">
          <el-form label-width="140px">
            <el-form-item label="Blockchain Network">
              <el-radio-group v-model="deployNetwork">
                <el-radio label="private">Private Chain (IBMS)</el-radio>
                <el-radio label="testnet">Testnet (Sepolia)</el-radio>
                <el-radio label="mainnet">Mainnet (Ethereum)</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="Deployer Address">
              <el-input v-model="deployerAddress" placeholder="0x..." />
            </el-form-item>
            <el-form-item label="Gas Limit">
              <el-input-number v-model="gasLimit" :min="100000" :max="5000000" />
            </el-form-item>
          </el-form>
          <div v-if="deployResultSuccess" class="deploy-result">
            <el-alert :title="deployResultSuccess ? 'Deployment Successful' : 'Deployment Failed'" :type="deployResultSuccess ? 'success' : 'error'" :description="deployResultMessage" show-icon />
            <div v-if="deployResultTxHash" class="tx-hash">
              Transaction Hash: <code>{{ deployResultTxHash }}</code>
              <el-icon class="copy-icon" @click="copyAddress(deployResultTxHash)"><CopyDocument /></el-icon>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <el-button @click="deployWizardVisible = false">Cancel</el-button>
        <el-button v-if="deployStep > 0" @click="deployStep--">Previous</el-button>
        <el-button v-if="deployStep < 2" type="primary" @click="nextStep">Next</el-button>
        <el-button v-if="deployStep === 2" type="success" @click="deployContract" :loading="deploying">Deploy</el-button>
      </template>
    </el-dialog>

    <!-- Contract Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" title="Contract Details" width="900px" destroy-on-close>
      <div v-if="selectedContract" class="contract-detail">
        <div class="detail-header">
          <h2>{{ selectedContract.name }}</h2>
          <el-tag :type="getStatusType(selectedContract.status)">{{ getStatusText(selectedContract.status) }}</el-tag>
        </div>
        <div class="detail-info">
          <div><strong>Address:</strong> <code>{{ selectedContract.address }}</code> <el-icon class="copy-icon" @click="copyAddress(selectedContract.address)"><CopyDocument /></el-icon></div>
          <div><strong>Template:</strong> {{ selectedContract.template }}</div>
          <div><strong>Deployed At:</strong> {{ selectedContract.deployedAt }}</div>
          <div><strong>Trigger Count:</strong> {{ selectedContract.triggerCount }}</div>
        </div>

        <el-tabs v-model="detailTab">
          <el-tab-pane label="ABI & Source Code" name="abi">
            <div class="code-block">
              <pre>{{ selectedContract.abi }}</pre>
            </div>
          </el-tab-pane>
          <el-tab-pane label="Contract Methods" name="methods">
            <div class="methods-list">
              <div v-for="method in selectedContract.methods" :key="method.name" class="method-item">
                <div class="method-signature">{{ method.signature }}</div>
                <div class="method-inputs">
                  <span v-for="input in method.inputs" :key="input.name" class="method-input">
                    {{ input.name }} ({{ input.type }}):
                    <el-input v-model="methodCallParams[method.name + '_' + input.name]" size="small" placeholder="value" style="width: 150px" />
                  </span>
                </div>
                <el-button size="small" type="primary" @click="callContractMethod(selectedContract, method)">Call</el-button>
              </div>
            </div>
          </el-tab-pane>
          <el-tab-pane label="Event Logs" name="events">
            <el-table :data="selectedContract.events" stripe size="small" style="width: 100%">
              <el-table-column prop="time" label="Time" min-width="140" />
              <el-table-column prop="event" label="Event" min-width="140" />
              <el-table-column prop="data" label="Data" min-width="200" />
              <el-table-column prop="txHash" label="Transaction" min-width="160">
                <template #default="{ row }">
                  <span class="address-text">{{ row.txHash.slice(0, 10) }}...</span>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>
          <el-tab-pane label="State Variables" name="state">
            <div class="state-vars">
              <div v-for="(value, key) in selectedContract.stateVariables" :key="key" class="state-var">
                <span class="var-key">{{ key }}:</span>
                <span class="var-value">{{ value }}</span>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-dialog>
  </div>

  <!-- Loading Screen - 深色科技感风格 (与FAS页面保持一致) -->
  <div v-else class="loading-container">
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
        <div class="loading-tip">Smart Contracts Module</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
import * as echarts from 'echarts'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, Document, Check, Lightning, Coin, TrendCharts,
  CopyDocument, VideoPlay, Connection
} from '@element-plus/icons-vue'

// ==================== Loading ====================
const isPageLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing assets...')

const loadingMessages = [
  'Preparing assets...',
  'Loading contract data...',
  'Initializing modules...',
  'Connecting to blockchain...',
  'Starting dashboard...',
  'Almost ready...'
]

// ==================== Statistics ====================
const contractStats = ref({
  total: 12,
  active: 8,
  totalTriggers: 1342,
  totalGas: 28450
})

// ==================== Contract Templates ====================
const contractTemplates = ref([
  {
    id: 1,
    name: 'Carbon Credit Settlement',
    description: 'Automatically settle carbon credit transactions based on emission data',
    icon: 'Money',
    color: '#10b981',
    params: ['carbon_price', 'emission_threshold', 'wallet_address', 'settlement_period']
  },
  {
    id: 2,
    name: 'Peak-Trough Electricity Pricing',
    description: 'Trigger energy storage discharge when electricity price exceeds threshold',
    icon: 'Lightning',
    color: '#f59e0b',
    params: ['price_threshold', 'battery_capacity', 'discharge_amount', 'time_window']
  },
  {
    id: 3,
    name: 'Device Interoperability Rule',
    description: 'Automated device coordination based on sensor data',
    icon: 'Connection',
    color: '#3b82f6',
    params: ['trigger_device', 'trigger_condition', 'target_device', 'target_action']
  },
  {
    id: 4,
    name: 'Automatic Alert Dispatch',
    description: 'Create work orders automatically when alarm conditions are met',
    icon: 'Bell',
    color: '#ef4444',
    params: ['alarm_level', 'alert_channel', 'assignee_role', 'escalation_timeout']
  }
])

// ==================== Deployed Contracts ====================
const deployedContracts = ref([
  {
    id: 1,
    name: 'Carbon Credit v1',
    address: '0x1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b',
    template: 'Carbon Credit Settlement',
    status: 'active',
    triggerCount: 234,
    lastExecution: '2026-05-21 09:32:15',
    deployedAt: '2026-04-15 10:00:00',
    abi: '[{"inputs":[],"name":"settle","outputs":[],"stateMutability":"nonpayable","type":"function"}]',
    methods: [
      { name: 'settle', signature: 'settle()', inputs: [] },
      { name: 'getBalance', signature: 'getBalance(address account)', inputs: [{ name: 'account', type: 'address' }] }
    ],
    events: [
      { time: '2026-05-21 09:32:15', event: 'SettlementExecuted', data: 'Amount: 100 CARBON', txHash: '0xabc...123' },
      { time: '2026-05-20 14:22:08', event: 'ThresholdReached', data: 'Value: 25.5 tons', txHash: '0xdef...456' }
    ],
    stateVariables: { totalSupply: '1,000,000', currentPrice: '$12.50', owner: '0x742...35b' }
  },
  {
    id: 2,
    name: 'PeakTrough V2',
    address: '0x2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c',
    template: 'Peak-Trough Electricity Pricing',
    status: 'active',
    triggerCount: 567,
    lastExecution: '2026-05-21 08:15:30',
    deployedAt: '2026-04-20 14:30:00',
    abi: '[{"inputs":[],"name":"discharge","outputs":[],"stateMutability":"nonpayable","type":"function"}]',
    methods: [
      { name: 'discharge', signature: 'discharge()', inputs: [] },
      { name: 'setPriceThreshold', signature: 'setPriceThreshold(uint256 threshold)', inputs: [{ name: 'threshold', type: 'uint256' }] }
    ],
    events: [
      { time: '2026-05-21 08:15:30', event: 'DischargeTriggered', data: 'Power: 100 kWh', txHash: '0xdef...789' }
    ],
    stateVariables: { priceThreshold: '0.52', batteryLevel: '78%', lastDischarge: '2026-05-21' }
  },
  {
    id: 3,
    name: 'Device Rule Engine',
    address: '0x3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d',
    template: 'Device Interoperability Rule',
    status: 'paused',
    triggerCount: 89,
    lastExecution: '2026-05-19 22:10:45',
    deployedAt: '2026-05-01 09:00:00',
    abi: '[{"inputs":[],"name":"execute","outputs":[],"stateMutability":"nonpayable","type":"function"}]',
    methods: [
      { name: 'execute', signature: 'execute()', inputs: [] },
      { name: 'addRule', signature: 'addRule(string condition, string action)', inputs: [{ name: 'condition', type: 'string' }, { name: 'action', type: 'string' }] }
    ],
    events: [],
    stateVariables: { activeRules: '3', lastExecutionResult: 'Success' }
  },
  {
    id: 4,
    name: 'Auto Alert Dispatcher',
    address: '0x4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e',
    template: 'Automatic Alert Dispatch',
    status: 'active',
    triggerCount: 452,
    lastExecution: '2026-05-21 07:05:20',
    deployedAt: '2026-05-10 11:15:00',
    abi: '[{"inputs":[],"name":"dispatch","outputs":[],"stateMutability":"nonpayable","type":"function"}]',
    methods: [
      { name: 'dispatch', signature: 'dispatch()', inputs: [] },
      { name: 'setAlertLevel', signature: 'setAlertLevel(uint8 level)', inputs: [{ name: 'level', type: 'uint8' }] }
    ],
    events: [
      { time: '2026-05-21 07:05:20', event: 'AlertDispatched', data: 'Work Order: WO-001', txHash: '0xabc...456' }
    ],
    stateVariables: { activeAlerts: '3', lastDispatchTime: '2026-05-21 07:05:20' }
  }
])

// ==================== Oracle Sources ====================
const oracleSources = ref([
  {
    id: 1,
    name: 'Electricity Price API',
    url: 'https://api.energyprice.com/v1/current',
    status: 'online',
    updateInterval: '5 min',
    lastFetch: '2026-05-21 09:30:00'
  },
  {
    id: 2,
    name: 'Weather Data',
    url: 'https://api.openweathermap.org/data/2.5/weather',
    status: 'online',
    updateInterval: '15 min',
    lastFetch: '2026-05-21 09:25:00'
  },
  {
    id: 3,
    name: 'Carbon Price Feed',
    url: 'https://api.carboncredits.com/price',
    status: 'offline',
    updateInterval: '1 hour',
    lastFetch: '2026-05-21 08:00:00'
  }
])

// ==================== Execution History ====================
const executionHistory = ref([
  { time: '2026-05-21 09:32:15', contract: 'Carbon Credit v1', txHash: '0x7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b', triggerCondition: 'emission > 100', result: 'Success', gasFee: '12,450' },
  { time: '2026-05-21 08:15:30', contract: 'PeakTrough V2', txHash: '0x8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7', triggerCondition: 'price > 0.52', result: 'Success', gasFee: '8,230' },
  { time: '2026-05-21 07:05:20', contract: 'Auto Alert Dispatcher', txHash: '0x9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8', triggerCondition: 'alarm_level >= 3', result: 'Success', gasFee: '5,120' },
  { time: '2026-05-20 22:10:45', contract: 'Device Rule Engine', txHash: '0x0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9', triggerCondition: 'temperature > 30 && humidity < 40', result: 'Failed', gasFee: '4,560' }
])

// 筛选后的执行历史
const filteredExecutionHistory = computed(() => {
  let result = executionHistory.value
  if (historyFilterContract.value) {
    const selectedContract = deployedContracts.value.find(c => c.id === historyFilterContract.value)
    if (selectedContract) {
      result = result.filter(h => h.contract === selectedContract.name)
    }
  }
  return result
})

// ==================== Chart ====================
const trendChartRef = ref(null)
let trendChart = null
let resizeObserver = null

const initChart = () => {
  if (!trendChartRef.value) return

  const container = trendChartRef.value
  const width = container.clientWidth
  const height = container.clientHeight

  if (width === 0 || height === 0) {
    setTimeout(initChart, 100)
    return
  }

  if (trendChart) {
    trendChart.dispose()
  }

  trendChart = echarts.init(container)
  trendChart.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis' },
    grid: { left: '8%', right: '5%', bottom: '5%', top: '8%', containLabel: true },
    xAxis: {
      type: 'category',
      data: ['05/15', '05/16', '05/17', '05/18', '05/19', '05/20', '05/21'],
      axisLabel: { color: '#6c757d', fontSize: 12 },
      axisLine: { lineStyle: { color: '#e9ecef' } }
    },
    yAxis: {
      type: 'value',
      name: 'Trigger Count',
      nameTextStyle: { color: '#6c757d' },
      axisLabel: { color: '#6c757d' },
      splitLine: { lineStyle: { color: '#e9ecef', type: 'dashed' } }
    },
    series: [{
      data: [145, 178, 192, 210, 188, 234, 195],
      type: 'line',
      smooth: true,
      lineStyle: { color: '#409eff', width: 3 },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: '#409eff40' },
          { offset: 1, color: '#409eff05' }
        ])
      },
      symbol: 'circle',
      symbolSize: 8,
      itemStyle: { color: '#409eff', borderColor: '#ffffff', borderWidth: 2 },
      label: { show: true, position: 'top', color: '#409eff', fontSize: 11 }
    }]
  })
}

const handleResize = () => {
  if (trendChart) trendChart.resize()
}

const setupResizeObserver = () => {
  if (!trendChartRef.value) return
  resizeObserver = new ResizeObserver(() => {
    if (trendChart) trendChart.resize()
    else initChart()
  })
  resizeObserver.observe(trendChartRef.value)
}

// ==================== State Variables ====================
const activeTab = ref('templates')
const deployWizardVisible = ref(false)
const deployStep = ref(0)
const selectedTemplate = ref(null)
const contractParams = ref({ triggerCondition: '', action: '' })
const deployNetwork = ref('private')
const deployerAddress = ref('0x742d35Cc6634C0532925a3b844Bc9e7595f0b5a0')
const gasLimit = ref(500000)
const deploying = ref(false)
const deployResultSuccess = ref(false)
const deployResultMessage = ref('')
const deployResultTxHash = ref('')
const simulateResultMsg = ref('')
const simulateResultSuccess = ref(false)
const detailDialogVisible = ref(false)
const selectedContract = ref(null)
const detailTab = ref('abi')
const methodCallParams = ref({})
const historyFilterContract = ref(null)
const historyFilterDateRange = ref(null)

// ==================== Helper Functions ====================
const getStatusType = (status) => {
  const map = { active: 'success', paused: 'warning', error: 'danger' }
  return map[status] || 'info'
}

const getStatusText = (status) => {
  const map = { active: 'Active', paused: 'Paused', error: 'Error' }
  return map[status] || status
}

const copyAddress = (text) => {
  navigator.clipboard.writeText(text)
  ElMessage.success('Copied to clipboard')
}

const useTemplate = (template) => {
  selectedTemplate.value = template
  contractParams.value = { triggerCondition: '', action: '' }
  deployStep.value = 0
  deployWizardVisible.value = true
}

const openDeployWizard = () => {
  selectedTemplate.value = null
  contractParams.value = { triggerCondition: '', action: '' }
  deployStep.value = 0
  deployResultSuccess.value = false
  deployResultMessage.value = ''
  deployResultTxHash.value = ''
  deployWizardVisible.value = true
}

const nextStep = () => {
  if (deployStep.value === 0 && !selectedTemplate.value) {
    ElMessage.warning('Please select a template')
    return
  }
  deployStep.value++
}

const simulateContract = () => {
  const isSuccess = Math.random() > 0.2
  simulateResultSuccess.value = isSuccess
  simulateResultMsg.value = isSuccess
      ? 'Simulation successful. Contract will execute as configured.'
      : 'Simulation failed: Invalid parameters or condition not met.'
  setTimeout(() => { simulateResultMsg.value = '' }, 3000)
}

const deployContract = async () => {
  deploying.value = true
  await new Promise(resolve => setTimeout(resolve, 2000))
  const networkName = deployNetwork.value === 'private' ? 'Private Chain' : deployNetwork.value === 'testnet' ? 'Sepolia Testnet' : 'Ethereum Mainnet'
  deployResultSuccess.value = true
  deployResultMessage.value = `Contract deployed successfully to ${networkName}`
  deployResultTxHash.value = '0x' + Math.random().toString(36).substring(2, 42)
  deployedContracts.value.unshift({
    id: Date.now(),
    name: (selectedTemplate.value?.name || 'New Contract') + ' ' + (deployedContracts.value.length + 1),
    address: '0x' + Math.random().toString(36).substring(2, 42),
    template: selectedTemplate.value?.name || 'Custom',
    status: 'active',
    triggerCount: 0,
    lastExecution: 'Never',
    deployedAt: new Date().toLocaleString(),
    abi: '[]',
    methods: [],
    events: [],
    stateVariables: {}
  })
  deploying.value = false
  setTimeout(() => {
    deployWizardVisible.value = false
    activeTab.value = 'contracts'
  }, 1500)
}

const toggleContractStatus = (contract) => {
  contract.status = contract.status === 'active' ? 'paused' : 'active'
  ElMessage.success(`Contract ${contract.status === 'active' ? 'resumed' : 'paused'}`)
}

const deleteContract = async (contract) => {
  await ElMessageBox.confirm(`Delete contract "${contract.name}"?`, 'Confirm', { type: 'warning' })
  const index = deployedContracts.value.findIndex(c => c.id === contract.id)
  deployedContracts.value.splice(index, 1)
  ElMessage.success('Contract deleted')
}

const viewContractDetail = (contract) => {
  selectedContract.value = contract
  detailDialogVisible.value = true
}

const callContractMethod = (contract, method) => {
  ElMessage.success(`Called ${method.name} on ${contract.name}`)
}

const addOracleSource = () => {
  ElMessage.info('Add data source dialog would open here')
}

const testOracle = (source) => {
  ElMessage.info(`Testing connection to ${source.name}...`)
  setTimeout(() => {
    source.status = Math.random() > 0.3 ? 'online' : 'offline'
    source.lastFetch = new Date().toLocaleString()
    ElMessage[source.status === 'online' ? 'success' : 'error'](`${source.name} is ${source.status}`)
  }, 1000)
}

const deleteOracle = (id) => {
  const index = oracleSources.value.findIndex(s => s.id === id)
  oracleSources.value.splice(index, 1)
  ElMessage.success('Data source removed')
}

const exportHistory = () => {
  ElMessage.success('Export started')
}

const viewTransactionDetail = (row) => {
  ElMessage.info(`Viewing transaction: ${row.txHash}`)
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
          initChart()
          setupResizeObserver()
        }, 200)
      })
    }, 500)
  }, 2500)
}

onMounted(() => {
  startLoading()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  if (resizeObserver) resizeObserver.disconnect()
  if (trendChart) trendChart.dispose()
})

watch(activeTab, () => {
  nextTick(() => setTimeout(() => trendChart?.resize(), 100))
})
</script>

<style scoped>
.smart-contracts-page {
  background: #ffffff;
  min-height: 100%;
  padding: 24px;
}

.page-container {
  max-width: 1600px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h1 {
  font-size: 28px;
  font-weight: 700;
  color: #1a2c3e;
  margin: 0;
}

.page-header p {
  color: #6c757d;
  margin: 4px 0 0;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 20px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  transition: all 0.3s;
}
.stat-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}
.stat-icon.blue { background: #e3f2fd; color: #2196f3; }
.stat-icon.green { background: #e8f5e9; color: #4caf50; }
.stat-icon.orange { background: #fff3e0; color: #ff9800; }
.stat-icon.purple { background: #f3e5f5; color: #9c27b0; }

.stat-info { display: flex; flex-direction: column; }
.stat-value { font-size: 28px; font-weight: 700; color: #1a2c3e; }
.stat-label { font-size: 13px; color: #6c757d; }

/* Chart Card */
.chart-card {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 20px;
  padding: 20px;
  margin-bottom: 24px;
}

.chart-card .card-header {
  font-size: 16px;
  font-weight: 600;
  color: #1a2c3e;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.trend-chart { width: 100%; height: 320px; }

/* Custom Tabs */
.custom-tabs :deep(.el-tabs__header) {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 4px;
  margin: 0 0 20px 0;
}
.custom-tabs :deep(.el-tabs__item) { color: #6c757d; }
.custom-tabs :deep(.el-tabs__item.is-active) { color: #409eff; }
.custom-tabs :deep(.el-tabs__active-bar) { background: #409eff; }

/* Templates Grid */
.templates-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.template-card {
  background: #ffffff;
  border: 1px solid #e9ecef;
  border-radius: 16px;
  padding: 20px;
  display: flex;
  gap: 16px;
  transition: all 0.3s;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}
.template-card:hover {
  border-color: #409eff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.template-icon {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.template-info { flex: 1; }
.template-info h3 { margin: 0 0 8px; color: #1a2c3e; font-size: 16px; }
.template-info p { margin: 0 0 12px; color: #6c757d; font-size: 13px; }
.template-params { display: flex; flex-wrap: wrap; gap: 6px; }

/* 表格列宽样式 */
.equal-width-table {
  width: 100%;
}
.equal-width-table :deep(.el-table__header-wrapper) {
  width: 100%;
}
.equal-width-table :deep(.el-table__header) {
  width: 100% !important;
}
.equal-width-table :deep(.el-table__body) {
  width: 100% !important;
}

.action-buttons {
  display: flex;
  gap: 6px;
  justify-content: center;
  flex-wrap: wrap;
}

/* Oracle Config */
.oracle-config { background: #f8f9fa; border-radius: 16px; padding: 20px; }
.oracle-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.oracle-header h3 { margin: 0; color: #1a2c3e; }
.oracle-grid { display: grid; gap: 16px; }
.oracle-card {
  background: #ffffff;
  border: 1px solid #e9ecef;
  border-radius: 12px;
  padding: 16px;
}
.oracle-card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.oracle-name { font-weight: 600; color: #1a2c3e; }
.oracle-url { font-size: 12px; color: #6c757d; font-family: monospace; margin-bottom: 8px; }
.oracle-info { display: flex; gap: 16px; font-size: 11px; color: #6c757d; margin-bottom: 12px; }
.oracle-actions { display: flex; gap: 8px; }

/* History Filters */
.history-filters { display: flex; gap: 12px; align-items: center; flex-wrap: wrap; margin-bottom: 16px; }

/* Wizard */
.wizard-content { margin: 24px 0; min-height: 300px; }
.template-select-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }
.template-select-card {
  background: #f8f9fa;
  border: 2px solid #e9ecef;
  border-radius: 16px;
  padding: 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
}
.template-select-card.selected { border-color: #409eff; background: #ecf5ff; }
.template-select-card:hover { border-color: #409eff; }
.template-select-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 12px;
  color: white;
}
.template-select-name { font-size: 14px; font-weight: 500; color: #1a2c3e; }

.simulate-section { margin-top: 16px; display: flex; align-items: center; gap: 16px; flex-wrap: wrap; }
.simulate-result { font-size: 13px; padding: 4px 12px; border-radius: 8px; }
.simulate-result.success { background: #e8f5e9; color: #4caf50; }
.simulate-result.error { background: #ffebee; color: #f44336; }

.deploy-result { margin-top: 16px; }
.tx-hash { margin-top: 12px; font-size: 12px; color: #6c757d; word-break: break-all; }

/* Contract Detail */
.contract-detail .detail-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.contract-detail .detail-header h2 { margin: 0; color: #1a2c3e; }
.detail-info { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; margin-bottom: 24px; }
.detail-info div { color: #6c757d; font-size: 13px; }
.detail-info code { color: #409eff; }

.code-block { background: #f8f9fa; border-radius: 12px; padding: 16px; overflow-x: auto; }
.code-block pre { margin: 0; color: #1a2c3e; font-family: monospace; font-size: 12px; white-space: pre-wrap; }

.methods-list { display: flex; flex-direction: column; gap: 16px; }
.method-item { background: #f8f9fa; border-radius: 12px; padding: 16px; display: flex; align-items: center; gap: 16px; flex-wrap: wrap; }
.method-signature { font-family: monospace; font-size: 13px; color: #409eff; }
.method-inputs { display: flex; gap: 12px; flex-wrap: wrap; flex: 1; }

.state-vars { display: grid; gap: 12px; }
.state-var { display: flex; gap: 12px; padding: 8px 0; border-bottom: 1px solid #e9ecef; }
.var-key { font-weight: 600; color: #6c757d; width: 200px; }
.var-value { color: #1a2c3e; }

/* Common */
.address-text { font-family: monospace; font-size: 12px; color: #409eff; }
.copy-icon { margin-left: 6px; cursor: pointer; opacity: 0.6; }
.copy-icon:hover { opacity: 1; }

/* ============================================
   Loading Screen - 深色科技感风格
   (与 FAS 页面完全一致，页面内容加载完成后消失)
   ============================================ */
.loading-container {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, #0a1620 0%, #03060c 100%);
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
  background: rgba(15, 25, 45, 0.6);
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

/* Responsive */
@media (max-width: 1200px) {
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .templates-grid { grid-template-columns: 1fr; }
}
@media (max-width: 768px) {
  .smart-contracts-page { padding: 16px; }
  .page-header { flex-direction: column; align-items: flex-start; gap: 12px; }
  .stats-grid { grid-template-columns: 1fr; }
  .template-card { flex-direction: column; }
  .detail-info { grid-template-columns: 1fr; }
  .action-buttons { flex-direction: column; align-items: center; }
  .action-buttons .el-button { width: 100%; margin: 2px 0; }
}

:deep(.el-table) {
  --el-table-bg-color: #ffffff;
  --el-table-tr-bg-color: #ffffff;
  --el-table-header-bg-color: #f8f9fa;
}
:deep(.el-table th) {
  background-color: #f8f9fa;
  font-weight: 600;
  color: #1a2c3e;
}
:deep(.el-table td) {
  color: #495057;
}
</style>