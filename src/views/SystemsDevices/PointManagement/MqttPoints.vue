<template>
  <!-- Global Pre Loading Screen -->
  <div v-if="!isLoaded" class="loading-container">
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
        <div class="loading-tip">MQTT POINT MODULE</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Page Content -->
  <div v-else class="mqtt-point-container">
    <!-- 统计卡片 -->
    <div class="stats-cards">
      <div class="stat-card">
        <div class="stat-icon"><el-icon><Connection /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">{{ totalTopics }}</span>
          <span class="stat-label">Total Topics</span>
        </div>
      </div>
      <div class="stat-card success">
        <div class="stat-icon"><el-icon><CircleCheckFilled /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">{{ activeTopics }}</span>
          <span class="stat-label">Active</span>
        </div>
        <div class="stat-percent">{{ activePercent }}%</div>
      </div>
      <div class="stat-card warning">
        <div class="stat-icon"><el-icon><WarningFilled /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">{{ messageRate }}</span>
          <span class="stat-label">Msg Rate</span>
        </div>
      </div>
      <div class="stat-card info">
        <div class="stat-icon"><el-icon><DataLine /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">{{ totalMessages }}</span>
          <span class="stat-label">Total Msgs</span>
        </div>
      </div>
    </div>

    <!-- 连接状态和筛选 -->
    <el-card class="connection-card" shadow="hover">
      <div class="connection-status">
        <div class="status-indicator">
          <span class="status-dot" :class="{ connected: mqttConnected, disconnected: !mqttConnected }"></span>
          <span class="status-text">{{ mqttConnected ? 'Connected to MQTT Broker' : 'Disconnected' }}</span>
          <span class="broker-info">{{ brokerUrl }}</span>
        </div>
        <div class="connection-actions">
          <el-button v-if="!mqttConnected" type="primary" size="small" @click="connectBroker">Connect</el-button>
          <el-button v-else type="danger" size="small" @click="disconnectBroker">Disconnect</el-button>
          <el-button size="small" :icon="Refresh" @click="refreshData" :loading="refreshing">Refresh</el-button>
        </div>
      </div>
    </el-card>

    <!-- 筛选卡片 -->
    <el-card class="filter-card" shadow="hover">
      <el-form :model="filterForm" inline>
        <el-form-item label="Topic">
          <el-input v-model="filterForm.topic" placeholder="e.g., building/sensor/+" clearable style="width: 220px" />
        </el-form-item>
        <el-form-item label="QoS">
          <el-select v-model="filterForm.qos" placeholder="QoS" clearable style="width: 100px">
            <el-option label="QoS 0" value="0" />
            <el-option label="QoS 1" value="1" />
            <el-option label="QoS 2" value="2" />
          </el-select>
        </el-form-item>
        <el-form-item label="Data Type">
          <el-select v-model="filterForm.dataType" placeholder="Data Type" clearable style="width: 120px">
            <el-option label="JSON" value="json" />
            <el-option label="Number" value="number" />
            <el-option label="String" value="string" />
            <el-option label="Boolean" value="boolean" />
          </el-select>
        </el-form-item>
        <el-form-item label="Device ID">
          <el-input v-model="filterForm.deviceId" placeholder="Device ID" clearable style="width: 150px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">Search</el-button>
          <el-button @click="resetFilter">Reset</el-button>
          <el-button type="success" :icon="Plus" @click="openSubscribeDialog">Subscribe Topic</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 图表区域 -->
    <div class="charts-row">
      <el-card class="chart-card" shadow="hover">
        <template #header>
          <div class="card-header-title">
            <span>Message Rate (msg/s)</span>
            <el-select v-model="rateTopic" placeholder="Select Topic" size="small" style="width: 200px" filterable @change="updateRateChart">
              <el-option v-for="topic in topicList" :key="topic.id" :label="topic.topic" :value="topic.id" />
            </el-select>
          </div>
        </template>
        <div ref="rateChartRef" class="chart-box"></div>
      </el-card>

      <el-card class="stats-chart-card" shadow="hover">
        <template #header>
          <div class="card-header-title">QoS Distribution</div>
        </template>
        <div ref="pieChartRef" class="pie-chart-box"></div>
      </el-card>
    </div>

    <!-- MQTT Topics 列表 -->
    <el-card shadow="hover">
      <template #header>
        <div class="card-header-title">Subscribed Topics</div>
      </template>
      <el-table :data="paginatedTableData" border stripe height="400" v-loading="tableLoading">
        <el-table-column label="Topic" prop="topic" min-width="250" show-overflow-tooltip />
        <el-table-column label="Device ID" prop="deviceId" width="140" />
        <el-table-column label="QoS" prop="qos" width="80">
          <template #default="scope">
            <el-tag size="small">QoS {{ scope.row.qos }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Data Type" prop="dataType" width="100" />
        <el-table-column label="Last Value" prop="lastValue" width="150">
          <template #default="scope">
            <span :class="getValueClass(scope.row)">{{ formatValue(scope.row.lastValue) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="Timestamp" prop="timestamp" width="160" />
        <el-table-column label="Rate" prop="messageRate" width="100">
          <template #default="scope">
            <span class="rate-value">{{ scope.row.messageRate }} msg/s</span>
          </template>
        </el-table-column>
        <el-table-column label="Status" prop="status" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.status === 'active' ? 'success' : 'danger'" size="small">{{ scope.row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Operation" width="140" fixed="right">
          <template #default="scope">
            <el-button text type="primary" size="small" @click="viewDetail(scope.row)">Detail</el-button>
            <el-button text type="warning" size="small" @click="publishMessage(scope.row)">Publish</el-button>
            <el-button text type="danger" size="small" @click="unsubscribe(scope.row)">Unsub</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-wrap">
        <el-pagination
            v-model:current-page="pageInfo.pageNum"
            v-model:page-size="pageInfo.pageSize"
            :page-sizes="[15, 30, 50, 100]"
            :total="pageInfo.total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handlePageSizeChange"
            @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- 发布消息对话框 -->
    <el-dialog v-model="publishDialogVisible" title="Publish Message" width="500px">
      <el-form :model="publishForm" label-width="100px">
        <el-form-item label="Topic">
          <span>{{ selectedTopic?.topic }}</span>
        </el-form-item>
        <el-form-item label="QoS">
          <el-radio-group v-model="publishForm.qos">
            <el-radio label="0">QoS 0 (At most once)</el-radio>
            <el-radio label="1">QoS 1 (At least once)</el-radio>
            <el-radio label="2">QoS 2 (Exactly once)</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="Payload">
          <el-input
              v-model="publishForm.payload"
              type="textarea"
              :rows="5"
              placeholder='{"temperature": 23.5, "humidity": 55}'
          />
        </el-form-item>
        <el-form-item label="Retain">
          <el-switch v-model="publishForm.retain" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="publishDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="confirmPublish" :loading="publishing">Publish</el-button>
      </template>
    </el-dialog>

    <!-- 订阅主题对话框 -->
    <el-dialog v-model="subscribeDialogVisible" title="Subscribe to Topic" width="450px">
      <el-form :model="subscribeForm" label-width="100px">
        <el-form-item label="Topic" required>
          <el-input v-model="subscribeForm.topic" placeholder="e.g., building/sensor/+/temperature" />
        </el-form-item>
        <el-form-item label="QoS">
          <el-radio-group v-model="subscribeForm.qos">
            <el-radio label="0">QoS 0</el-radio>
            <el-radio label="1">QoS 1</el-radio>
            <el-radio label="2">QoS 2</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="Device ID">
          <el-input v-model="subscribeForm.deviceId" placeholder="Device identifier" />
        </el-form-item>
        <el-form-item label="Data Type">
          <el-select v-model="subscribeForm.dataType" style="width: 100%">
            <el-option label="JSON" value="json" />
            <el-option label="Number" value="number" />
            <el-option label="String" value="string" />
            <el-option label="Boolean" value="boolean" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="subscribeDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="confirmSubscribe" :loading="subscribing">Subscribe</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, nextTick, computed } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { Connection, CircleCheckFilled, WarningFilled, DataLine, Refresh, Plus } from '@element-plus/icons-vue'

// ========== Loading State ==========
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const loadingMessages = [
  'Preparing...',
  'Loading MQTT modules...',
  'Connecting to broker...',
  'Subscribing to topics...',
  'Almost ready...'
]

// ========== Connection State ==========
const mqttConnected = ref(true)
const brokerUrl = ref('mqtt://mqtt.example.com:1883')
const refreshing = ref(false)
const tableLoading = ref(false)
const publishing = ref(false)
const subscribing = ref(false)

// ========== Chart References ==========
const rateChartRef = ref<HTMLDivElement | null>(null)
const pieChartRef = ref<HTMLDivElement | null>(null)
let rateInstance: echarts.ECharts | null = null
let pieInstance: echarts.ECharts | null = null
let realtimeTimer: number | null = null
const rateTopic = ref('')

// ========== Filter Form ==========
const filterForm = reactive({
  topic: '',
  qos: '',
  dataType: '',
  deviceId: ''
})

// ========== Pagination ==========
const pageInfo = reactive({
  pageNum: 1,
  pageSize: 15,
  total: 0
})

// ========== Dialog State ==========
const publishDialogVisible = ref(false)
const subscribeDialogVisible = ref(false)
const selectedTopic = ref<any>(null)
const publishForm = reactive({
  qos: '1',
  payload: '',
  retain: false
})

const subscribeForm = reactive({
  topic: '',
  qos: '1',
  deviceId: '',
  dataType: 'json'
})

// ========== Table Data ==========
const allTopics = ref<any[]>([])

// 统计数据
const totalTopics = computed(() => allTopics.value.length)
const activeTopics = computed(() => allTopics.value.filter(item => item.status === 'active').length)
const activePercent = computed(() => totalTopics.value ? Math.round(activeTopics.value / totalTopics.value * 100) : 0)
const messageRate = computed(() => {
  const sum = allTopics.value.reduce((s, t) => s + (t.messageRate || 0), 0)
  return Math.round(sum)
})
const totalMessages = computed(() => {
  const sum = allTopics.value.reduce((s, t) => s + (t.totalMessages || 0), 0)
  return sum
})

const topicList = computed(() => allTopics.value)

// 分页数据
const paginatedTableData = computed(() => {
  let filtered = [...allTopics.value]

  if (filterForm.topic) {
    filtered = filtered.filter(item => item.topic?.toLowerCase().includes(filterForm.topic.toLowerCase()))
  }
  if (filterForm.qos) {
    filtered = filtered.filter(item => item.qos === filterForm.qos)
  }
  if (filterForm.dataType) {
    filtered = filtered.filter(item => item.dataType === filterForm.dataType)
  }
  if (filterForm.deviceId) {
    filtered = filtered.filter(item => item.deviceId?.toLowerCase().includes(filterForm.deviceId.toLowerCase()))
  }

  pageInfo.total = filtered.length
  const start = (pageInfo.pageNum - 1) * pageInfo.pageSize
  return filtered.slice(start, start + pageInfo.pageSize)
})

// ========== 生成模拟数据 ==========
const generateTopics = () => {
  const topics = [
    { id: 1, topic: 'building/b2/hvac/ahu/temperature', deviceId: 'AHU-B2-01', qos: '1', dataType: 'number', lastValue: 23.5, unit: '°C', timestamp: new Date().toLocaleString(), messageRate: 2.3, totalMessages: 12450, status: 'active' },
    { id: 2, topic: 'building/b2/hvac/ahu/humidity', deviceId: 'AHU-B2-01', qos: '1', dataType: 'number', lastValue: 55.2, unit: '%', timestamp: new Date().toLocaleString(), messageRate: 2.3, totalMessages: 12448, status: 'active' },
    { id: 3, topic: 'building/b2/hvac/ahu/fan_speed', deviceId: 'AHU-B2-01', qos: '0', dataType: 'number', lastValue: 68, unit: '%', timestamp: new Date().toLocaleString(), messageRate: 1.1, totalMessages: 5620, status: 'active' },
    { id: 4, topic: 'building/b2/power/main/voltage', deviceId: 'POWER-01', qos: '1', dataType: 'number', lastValue: 230.1, unit: 'V', timestamp: new Date().toLocaleString(), messageRate: 0.5, totalMessages: 2580, status: 'active' },
    { id: 5, topic: 'building/b2/power/main/current', deviceId: 'POWER-01', qos: '1', dataType: 'number', lastValue: 32.5, unit: 'A', timestamp: new Date().toLocaleString(), messageRate: 0.5, totalMessages: 2578, status: 'active' },
    { id: 6, topic: 'building/b2/power/main/power', deviceId: 'POWER-01', qos: '1', dataType: 'number', lastValue: 7.48, unit: 'kW', timestamp: new Date().toLocaleString(), messageRate: 0.5, totalMessages: 2575, status: 'active' },
    { id: 7, topic: 'building/1f/lighting/status', deviceId: 'LIGHT-1F', qos: '0', dataType: 'boolean', lastValue: true, unit: '', timestamp: new Date().toLocaleString(), messageRate: 0.1, totalMessages: 890, status: 'active' },
    { id: 8, topic: 'building/1f/lighting/brightness', deviceId: 'LIGHT-1F', qos: '0', dataType: 'number', lastValue: 78, unit: '%', timestamp: new Date().toLocaleString(), messageRate: 0.2, totalMessages: 1230, status: 'active' },
    { id: 9, topic: 'building/2f/security/door_status', deviceId: 'SEC-2F', qos: '1', dataType: 'boolean', lastValue: false, unit: '', timestamp: new Date().toLocaleString(), messageRate: 0.3, totalMessages: 2340, status: 'active' },
    { id: 10, topic: 'building/3f/security/camera_motion', deviceId: 'SEC-3F', qos: '2', dataType: 'boolean', lastValue: false, unit: '', timestamp: new Date().toLocaleString(), messageRate: 0.8, totalMessages: 5670, status: 'inactive' },
    { id: 11, topic: 'building/roof/weather/temperature', deviceId: 'WEATHER-01', qos: '1', dataType: 'number', lastValue: 18.2, unit: '°C', timestamp: new Date().toLocaleString(), messageRate: 0.2, totalMessages: 1890, status: 'active' },
    { id: 12, topic: 'building/roof/weather/humidity', deviceId: 'WEATHER-01', qos: '1', dataType: 'number', lastValue: 65, unit: '%', timestamp: new Date().toLocaleString(), messageRate: 0.2, totalMessages: 1888, status: 'active' }
  ]
  allTopics.value = topics
  if (topicList.value.length > 0) {
    rateTopic.value = topicList.value[0].id.toString()
  }
}

// 更新消息值
const updateMessageValues = () => {
  for (const topic of allTopics.value) {
    if (topic.status === 'active') {
      if (topic.dataType === 'number') {
        const change = (Math.random() - 0.5) * 2
        if (topic.unit === '°C') {
          topic.lastValue = Number((topic.lastValue + change).toFixed(1))
        } else if (topic.unit === '%') {
          let newVal = topic.lastValue + change
          newVal = Math.max(0, Math.min(100, newVal))
          topic.lastValue = Math.round(newVal)
        } else {
          topic.lastValue = Number((topic.lastValue + change * 0.1).toFixed(1))
        }
      } else if (topic.dataType === 'boolean') {
        topic.lastValue = Math.random() > 0.95 ? !topic.lastValue : topic.lastValue
      }
      topic.timestamp = new Date().toLocaleString()
      topic.totalMessages = (topic.totalMessages || 0) + Math.floor(Math.random() * 3) + 1
      topic.messageRate = Number((topic.messageRate + (Math.random() - 0.5) * 0.5).toFixed(1))
    }
  }
}

// ========== 消息速率历史数据 ==========
const rateHistory = ref<{ timestamps: string[]; rates: number[] }>({
  timestamps: [],
  rates: []
})

// 获取主题消息速率历史
const getTopicRateHistory = () => {
  const topic = topicList.value.find(t => t.id.toString() === rateTopic.value)
  if (!topic) return

  const timestamps = []
  const rates = []
  const now = new Date()
  const baseRate = topic.messageRate || 2

  for (let i = 23; i >= 0; i--) {
    const time = new Date(now.getTime() - i * 3600000)
    timestamps.push(`${String(time.getHours()).padStart(2, '0')}:00`)
    const variation = Math.sin(i * 0.5) * 1.5 + (Math.random() - 0.5) * 1
    rates.push(Number(Math.max(0, baseRate + variation).toFixed(1)))
  }

  rateHistory.value = { timestamps, rates }
}

// 添加新数据点
const appendRateData = () => {
  const topic = topicList.value.find(t => t.id.toString() === rateTopic.value)
  if (!topic) return

  const now = new Date()
  const timeStr = `${String(now.getHours()).padStart(2, '0')}:00`
  const newRate = topic.messageRate || 2

  rateHistory.value.timestamps.push(timeStr)
  rateHistory.value.rates.push(newRate)

  if (rateHistory.value.timestamps.length > 48) {
    rateHistory.value.timestamps.shift()
    rateHistory.value.rates.shift()
  }

  updateRateChart()
}

// 初始化速率图
const initRateChart = async () => {
  await nextTick()
  if (!rateChartRef.value) {
    setTimeout(() => initRateChart(), 100)
    return
  }

  if (rateInstance) rateInstance.dispose()

  getTopicRateHistory()
  rateInstance = echarts.init(rateChartRef.value)
  updateRateChart()
  window.addEventListener('resize', handleChartResize)
}

const updateRateChart = () => {
  if (!rateInstance || !rateHistory.value.timestamps.length) return

  const topic = topicList.value.find(t => t.id.toString() === rateTopic.value)

  const option = {
    tooltip: { trigger: 'axis', formatter: (params: any) => `${params[0].axisValue}<br/>Message Rate: ${params[0].value} msg/s` },
    grid: { left: '8%', right: '5%', top: '12%', bottom: '8%', containLabel: true },
    xAxis: { type: 'category', data: rateHistory.value.timestamps, axisLabel: { rotate: 45, interval: 4, fontSize: 10 } },
    yAxis: { type: 'value', name: 'Messages per second', nameTextStyle: { fontSize: 12 } },
    series: [{
      name: topic?.topic || 'Message Rate',
      type: 'line',
      data: rateHistory.value.rates,
      smooth: true,
      lineStyle: { color: '#409eff', width: 2 },
      areaStyle: { opacity: 0.1, color: '#409eff' },
      symbol: 'circle',
      symbolSize: 5
    }]
  }
  rateInstance.setOption(option, true)
}

// 初始化饼图
const initPieChart = async () => {
  await nextTick()
  if (!pieChartRef.value) {
    setTimeout(() => initPieChart(), 100)
    return
  }

  if (pieInstance) pieInstance.dispose()
  pieInstance = echarts.init(pieChartRef.value)

  const qos0 = allTopics.value.filter(t => t.qos === '0').length
  const qos1 = allTopics.value.filter(t => t.qos === '1').length
  const qos2 = allTopics.value.filter(t => t.qos === '2').length

  const option = {
    tooltip: { trigger: 'item', formatter: '{b}: {d}% ({c})' },
    legend: { orient: 'vertical', left: 'left', data: ['QoS 0', 'QoS 1', 'QoS 2'] },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      data: [
        { name: 'QoS 0', value: qos0, itemStyle: { color: '#67c23a' } },
        { name: 'QoS 1', value: qos1, itemStyle: { color: '#409eff' } },
        { name: 'QoS 2', value: qos2, itemStyle: { color: '#e6a23c' } }
      ],
      emphasis: { scale: true },
      label: { show: true, formatter: '{b}', position: 'outside' }
    }]
  }
  pieInstance.setOption(option)
}

const updatePieChart = () => {
  if (!pieInstance) return
  const qos0 = allTopics.value.filter(t => t.qos === '0').length
  const qos1 = allTopics.value.filter(t => t.qos === '1').length
  const qos2 = allTopics.value.filter(t => t.qos === '2').length
  pieInstance.setOption({ series: [{ data: [{ name: 'QoS 0', value: qos0 }, { name: 'QoS 1', value: qos1 }, { name: 'QoS 2', value: qos2 }] }] })
}

const handleChartResize = () => {
  if (rateInstance) rateInstance.resize()
  if (pieInstance) pieInstance.resize()
}

// ========== Helper Functions ==========
const formatValue = (value: any) => {
  if (typeof value === 'boolean') return value ? 'True' : 'False'
  if (typeof value === 'number') return value.toFixed(2)
  return value
}

const getValueClass = (row: any) => {
  if (row.status === 'inactive') return 'text-danger'
  return ''
}

// ========== Actions ==========
const connectBroker = () => {
  mqttConnected.value = true
  ElMessage.success('Connected to MQTT broker')
}

const disconnectBroker = () => {
  mqttConnected.value = false
  ElMessage.warning('Disconnected from MQTT broker')
}

const handleSearch = () => { pageInfo.pageNum = 1 }
const resetFilter = () => {
  filterForm.topic = ''
  filterForm.qos = ''
  filterForm.dataType = ''
  filterForm.deviceId = ''
  pageInfo.pageNum = 1
}

const refreshData = async () => {
  refreshing.value = true
  tableLoading.value = true
  await new Promise(resolve => setTimeout(resolve, 500))
  generateTopics()
  updatePieChart()
  if (topicList.value.length > 0 && !rateTopic.value) {
    rateTopic.value = topicList.value[0].id.toString()
    getTopicRateHistory()
    updateRateChart()
  }
  tableLoading.value = false
  refreshing.value = false
  ElMessage.success('Data refreshed')
}

const handlePageSizeChange = () => { pageInfo.pageNum = 1 }
const handlePageChange = () => {}

const viewDetail = (row: any) => {
  ElMessage.info(`Viewing details for topic: ${row.topic}`)
}

const publishMessage = (row: any) => {
  selectedTopic.value = row
  publishForm.payload = JSON.stringify({ value: row.lastValue, timestamp: new Date().toISOString() }, null, 2)
  publishForm.qos = row.qos
  publishForm.retain = false
  publishDialogVisible.value = true
}

const confirmPublish = async () => {
  publishing.value = true
  await new Promise(resolve => setTimeout(resolve, 800))
  ElMessage.success(`Message published to ${selectedTopic.value.topic}`)
  publishDialogVisible.value = false
  publishing.value = false
}

const unsubscribe = (row: any) => {
  allTopics.value = allTopics.value.filter(t => t.id !== row.id)
  updatePieChart()
  ElMessage.success(`Unsubscribed from ${row.topic}`)
}

const openSubscribeDialog = () => {
  subscribeForm.topic = ''
  subscribeForm.qos = '1'
  subscribeForm.deviceId = ''
  subscribeForm.dataType = 'json'
  subscribeDialogVisible.value = true
}

const confirmSubscribe = async () => {
  if (!subscribeForm.topic) {
    ElMessage.warning('Please enter topic')
    return
  }
  subscribing.value = true
  await new Promise(resolve => setTimeout(resolve, 800))

  const newTopic = {
    id: allTopics.value.length + 1,
    topic: subscribeForm.topic,
    deviceId: subscribeForm.deviceId || 'UNKNOWN',
    qos: subscribeForm.qos,
    dataType: subscribeForm.dataType,
    lastValue: null,
    unit: '',
    timestamp: new Date().toLocaleString(),
    messageRate: 0,
    totalMessages: 0,
    status: 'active'
  }
  allTopics.value.unshift(newTopic)
  updatePieChart()
  subscribeDialogVisible.value = false
  subscribing.value = false
  ElMessage.success(`Subscribed to ${subscribeForm.topic}`)
}

// 实时更新
const startRealtimeUpdates = () => {
  realtimeTimer = window.setInterval(() => {
    updateMessageValues()
    appendRateData()
  }, 3000)
}

// ========== Lifecycle ==========
onMounted(async () => {
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

  setTimeout(async () => {
    clearInterval(messageInterval)
    clearInterval(progressInterval)
    loadingProgress.value = 100
    loadingMessage.value = 'Ready!'

    setTimeout(async () => {
      generateTopics()
      isLoaded.value = true
      await nextTick()

      setTimeout(async () => {
        await initRateChart()
        await initPieChart()
        startRealtimeUpdates()
      }, 200)
    }, 400)
  }, 2000)
})

onUnmounted(() => {
  if (realtimeTimer) clearInterval(realtimeTimer)
  if (rateInstance) rateInstance.dispose()
  if (pieInstance) pieInstance.dispose()
  window.removeEventListener('resize', handleChartResize)
})
</script>

<style scoped lang="scss">
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

.spinner-ring:nth-child(1) { border-top-color: #3b82f6; animation-delay: 0s; }
.spinner-ring:nth-child(2) { border-right-color: #f59e0b; animation-delay: 0.2s; width: 70%; height: 70%; top: 15%; left: 15%; }
.spinner-ring:nth-child(3) { border-bottom-color: #10b981; animation-delay: 0.4s; width: 40%; height: 40%; top: 30%; left: 30%; }

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

/* Page Content */
.mqtt-point-container {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100%;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 20px;
}

.stat-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-icon .el-icon {
  font-size: 32px;
  color: #3b82f6;
}

.stat-card.success .stat-icon .el-icon { color: #67c23a; }
.stat-card.warning .stat-icon .el-icon { color: #e6a23c; }
.stat-card.info .stat-icon .el-icon { color: #409eff; }

.stat-info { flex: 1; }
.stat-value { font-size: 28px; font-weight: 700; color: #1e293b; }
.stat-label { font-size: 13px; color: #64748b; }
.stat-percent { font-size: 20px; font-weight: 600; color: #67c23a; }

.connection-card {
  margin-bottom: 20px;
  border-radius: 12px;
}

.connection-status {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.status-dot.connected {
  background: #67c23a;
  box-shadow: 0 0 6px #67c23a;
  animation: pulse 2s infinite;
}

.status-dot.disconnected {
  background: #f56c6c;
}

.status-text {
  font-weight: 500;
  color: #1e293b;
}

.broker-info {
  font-size: 12px;
  color: #64748b;
}

.filter-card {
  margin-bottom: 20px;
  border-radius: 12px;
}

.filter-card :deep(.el-card__body) {
  padding: 20px;
}

.filter-card :deep(.el-form) {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  gap: 16px;
}

.filter-card :deep(.el-form-item) {
  margin-bottom: 0;
}

.filter-card :deep(.el-form-item__label) {
  font-size: 13px;
  font-weight: 500;
  padding-bottom: 4px;
}

.charts-row {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.chart-card, .stats-chart-card {
  flex: 1;
  border-radius: 12px;
}

.card-header-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  color: #1e293b;
  font-size: 16px;
  flex-wrap: wrap;
  gap: 12px;
}

.chart-box, .pie-chart-box {
  width: 100%;
  height: 320px;
}

.rate-value {
  font-family: monospace;
  font-weight: 500;
  color: #409eff;
}

.text-danger { color: #f56c6c; font-weight: 500; }

.pagination-wrap {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

@media (max-width: 1024px) {
  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
  }
  .charts-row {
    flex-direction: column;
  }
}

@media (max-width: 768px) {
  .mqtt-point-container {
    padding: 12px;
  }
  .stats-cards {
    grid-template-columns: 1fr;
  }
  .connection-status {
    flex-direction: column;
    align-items: flex-start;
  }
  .filter-card :deep(.el-form) {
    flex-direction: column;
    align-items: stretch;
  }
  .filter-card :deep(.el-form-item) {
    width: 100%;
  }
  .filter-card :deep(.el-input),
  .filter-card :deep(.el-select) {
    width: 100% !important;
  }
  .chart-box, .pie-chart-box {
    height: 250px;
  }
}
</style>