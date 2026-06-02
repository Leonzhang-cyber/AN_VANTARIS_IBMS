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
        <div class="loading-tip">OPC UA POINT MODULE</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Page Content -->
  <div v-else class="opcua-point-container">
    <!-- 统计卡片 -->
    <div class="stats-cards">
      <div class="stat-card">
        <div class="stat-icon"><el-icon><Connection /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">{{ totalNodes }}</span>
          <span class="stat-label">Total Nodes</span>
        </div>
      </div>
      <div class="stat-card success">
        <div class="stat-icon"><el-icon><CircleCheckFilled /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">{{ onlineNodes }}</span>
          <span class="stat-label">Good</span>
        </div>
        <div class="stat-percent">{{ onlinePercent }}%</div>
      </div>
      <div class="stat-card warning">
        <div class="stat-icon"><el-icon><WarningFilled /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">{{ uncertainNodes }}</span>
          <span class="stat-label">Uncertain</span>
        </div>
      </div>
      <div class="stat-card info">
        <div class="stat-icon"><el-icon><DataLine /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">{{ subscribedNodes }}</span>
          <span class="stat-label">Subscribed</span>
        </div>
      </div>
    </div>

    <!-- 筛选卡片 -->
    <el-card class="filter-card" shadow="hover">
      <el-form :model="filterForm" inline>
        <el-form-item label="Server URL">
          <el-input v-model="filterForm.serverUrl" placeholder="opc.tcp://server:4840" clearable style="width: 200px" />
        </el-form-item>
        <el-form-item label="Namespace">
          <el-input v-model="filterForm.namespace" placeholder="Namespace URI" clearable style="width: 180px" />
        </el-form-item>
        <el-form-item label="Node Type">
          <el-select v-model="filterForm.nodeType" placeholder="Select Type" clearable style="width: 140px">
            <el-option label="Variable" value="variable" />
            <el-option label="Object" value="object" />
            <el-option label="Method" value="method" />
            <el-option label="Property" value="property" />
          </el-select>
        </el-form-item>
        <el-form-item label="Data Type">
          <el-select v-model="filterForm.dataType" placeholder="Data Type" clearable style="width: 120px">
            <el-option label="Double" value="double" />
            <el-option label="Float" value="float" />
            <el-option label="Int32" value="int32" />
            <el-option label="Boolean" value="boolean" />
            <el-option label="String" value="string" />
          </el-select>
        </el-form-item>
        <el-form-item label="Browse Name">
          <el-input v-model="filterForm.browseName" placeholder="Search..." clearable style="width: 160px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">Search</el-button>
          <el-button @click="resetFilter">Reset</el-button>
          <el-button :icon="Refresh" @click="refreshData" :loading="refreshing">Refresh</el-button>
          <el-button type="success" :icon="Plus" @click="openBrowseDialog">Browse Server</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 图表区域 -->
    <div class="charts-row">
      <el-card class="chart-card" shadow="hover">
        <template #header>
          <div class="card-header-title">
            <span>OPC UA Value Trend</span>
            <el-select v-model="trendNodeId" placeholder="Select Node" size="small" style="width: 250px" filterable @change="updateTrendChart">
              <el-option v-for="node in analogNodes" :key="node.id" :label="node.displayName" :value="node.id" />
            </el-select>
          </div>
        </template>
        <div ref="trendChartRef" class="chart-box"></div>
      </el-card>

      <el-card class="stats-chart-card" shadow="hover">
        <template #header>
          <div class="card-header-title">Status Code Distribution</div>
        </template>
        <div ref="pieChartRef" class="pie-chart-box"></div>
      </el-card>
    </div>

    <!-- OPC UA 节点树 -->
    <el-card shadow="hover" class="tree-card">
      <template #header>
        <div class="card-header-title">
          <span>OPC UA Address Space</span>
          <el-button size="small" @click="expandAll">Expand All</el-button>
        </div>
      </template>
      <div class="tree-container">
        <el-tree
            ref="treeRef"
            :data="nodeTree"
            :props="treeProps"
            node-key="nodeId"
            :default-expanded-keys="expandedKeys"
            :filter-node-method="filterNode"
            highlight-current
            @node-click="onNodeClick"
        >
          <template #default="{ node, data }">
            <div class="tree-node">
              <el-icon :class="getNodeIconClass(data.nodeClass)">
                <component :is="getNodeIcon(data.nodeClass)" />
              </el-icon>
              <span class="node-name">{{ data.displayName }}</span>
              <span class="node-id">{{ data.nodeId }}</span>
              <span v-if="data.status !== 'good'" class="status-badge">
                <el-tag :type="data.status === 'good' ? 'success' : data.status === 'uncertain' ? 'warning' : 'danger'" size="small">
                  {{ data.status }}
                </el-tag>
              </span>
              <span v-if="data.value !== undefined" class="node-value">
                {{ formatValue(data.value) }} {{ data.unit || '' }}
              </span>
            </div>
          </template>
        </el-tree>
      </div>
    </el-card>

    <!-- OPC UA 节点列表 -->
    <el-card shadow="hover">
      <template #header>
        <div class="card-header-title">OPC UA Variables List</div>
      </template>
      <el-table :data="paginatedTableData" border stripe height="400" v-loading="tableLoading">
        <el-table-column label="Browse Name" prop="browseName" min-width="180" show-overflow-tooltip />
        <el-table-column label="Display Name" prop="displayName" min-width="180" show-overflow-tooltip />
        <el-table-column label="Node ID" prop="nodeId" width="200" show-overflow-tooltip />
        <el-table-column label="Data Type" prop="dataType" width="100" />
        <el-table-column label="Value" prop="value" width="120">
          <template #default="scope">
            <span :class="getValueClass(scope.row)">{{ formatValue(scope.row.value) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="Unit" prop="unit" width="80" />
        <el-table-column label="Status" prop="status" width="100">
          <template #default="scope">
            <el-tag :type="getStatusTagType(scope.row.status)" size="small">{{ scope.row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Timestamp" prop="timestamp" width="160" />
        <el-table-column label="Operation" width="140" fixed="right" align="center">
          <template #default="scope">
            <el-button text type="primary" size="small" @click="viewDetail(scope.row)">Detail</el-button>
            <el-button text type="warning" size="small" @click="writeValue(scope.row)">Write</el-button>
            <el-button text type="success" size="small" @click="subscribeNode(scope.row)">Subscribe</el-button>
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

    <!-- 写入值对话框 -->
    <el-dialog v-model="writeDialogVisible" title="Write Value" width="400px">
      <el-form :model="writeForm" label-width="100px">
        <el-form-item label="Node Name">
          <span>{{ selectedNode?.displayName }}</span>
        </el-form-item>
        <el-form-item label="Current Value">
          <span>{{ formatValue(selectedNode?.value) }} {{ selectedNode?.unit }}</span>
        </el-form-item>
        <el-form-item label="New Value" required>
          <el-input-number
              v-if="selectedNode?.dataType === 'double' || selectedNode?.dataType === 'float'"
              v-model="writeForm.value"
              :step="0.1"
              style="width: 100%"
          />
          <el-input-number
              v-else-if="selectedNode?.dataType === 'int32'"
              v-model="writeForm.value"
              :step="1"
              style="width: 100%"
          />
          <el-switch v-else-if="selectedNode?.dataType === 'boolean'" v-model="writeForm.value" />
          <el-input v-else v-model="writeForm.value" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="writeDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="confirmWrite" :loading="writing">Write</el-button>
      </template>
    </el-dialog>

    <!-- 浏览服务器对话框 -->
    <el-dialog v-model="browseDialogVisible" title="Browse OPC UA Server" width="800px">
      <div class="browser-container">
        <div class="browser-tree">
          <el-tree
              ref="browserTreeRef"
              :data="browserTreeData"
              :props="{ children: 'children', label: 'displayName' }"
              node-key="nodeId"
              highlight-current
              @node-click="onBrowserNodeClick"
          >
            <template #default="{ data }">
              <div class="browser-node">
                <el-icon><component :is="getNodeIcon(data.nodeClass)" /></el-icon>
                <span>{{ data.displayName }}</span>
                <span class="node-id-browser">{{ data.nodeId }}</span>
              </div>
            </template>
          </el-tree>
        </div>
        <div class="browser-detail">
          <div v-if="selectedBrowserNode" class="node-detail">
            <h4>Node Details</h4>
            <el-descriptions :column="1" border size="small">
              <el-descriptions-item label="Browse Name">{{ selectedBrowserNode.browseName }}</el-descriptions-item>
              <el-descriptions-item label="Display Name">{{ selectedBrowserNode.displayName }}</el-descriptions-item>
              <el-descriptions-item label="Node ID">{{ selectedBrowserNode.nodeId }}</el-descriptions-item>
              <el-descriptions-item label="Node Class">{{ selectedBrowserNode.nodeClass }}</el-descriptions-item>
              <el-descriptions-item label="Data Type">{{ selectedBrowserNode.dataType || '-' }}</el-descriptions-item>
              <el-descriptions-item label="Value">{{ formatValue(selectedBrowserNode.value) }}</el-descriptions-item>
            </el-descriptions>
            <el-button type="primary" size="small" @click="importNode" style="margin-top: 12px">Import Node</el-button>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, nextTick, computed } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { Connection, CircleCheckFilled, WarningFilled, DataLine, Refresh, Plus, Folder, Document, Setting, Tools } from '@element-plus/icons-vue'

// ========== Loading State ==========
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const loadingMessages = [
  'Preparing...',
  'Loading OPC UA modules...',
  'Connecting to server...',
  'Browsing address space...',
  'Almost ready...'
]

// ========== Chart References ==========
const trendChartRef = ref<HTMLDivElement | null>(null)
const pieChartRef = ref<HTMLDivElement | null>(null)
let trendInstance: echarts.ECharts | null = null
let pieInstance: echarts.ECharts | null = null
let realtimeTimer: number | null = null
const refreshing = ref(false)
const tableLoading = ref(false)
const writing = ref(false)
const trendNodeId = ref('')
const treeRef = ref()
const browserTreeRef = ref()

// ========== Filter Form ==========
const filterForm = reactive({
  serverUrl: '',
  namespace: '',
  nodeType: '',
  dataType: '',
  browseName: ''
})

// ========== Pagination ==========
const pageInfo = reactive({
  pageNum: 1,
  pageSize: 15,
  total: 0
})

// ========== Dialog State ==========
const writeDialogVisible = ref(false)
const browseDialogVisible = ref(false)
const selectedNode = ref<any>(null)
const selectedBrowserNode = ref<any>(null)
const writeForm = ref({ value: 0 })

// ========== Tree Data ==========
const nodeTree = ref<any[]>([])
const browserTreeData = ref<any[]>([])
const expandedKeys = ref<string[]>([])

const treeProps = {
  children: 'children',
  label: 'displayName'
}

// ========== Table Data ==========
const allNodes = ref<any[]>([])

// 统计数据
const totalNodes = computed(() => allNodes.value.length)
const onlineNodes = computed(() => allNodes.value.filter(item => item.status === 'good').length)
const uncertainNodes = computed(() => allNodes.value.filter(item => item.status === 'uncertain').length)
const subscribedNodes = computed(() => allNodes.value.filter(item => item.subscribed).length)
const onlinePercent = computed(() => totalNodes.value ? Math.round(onlineNodes.value / totalNodes.value * 100) : 0)

// 模拟量节点（用于趋势图）
const analogNodes = computed(() =>
    allNodes.value.filter(n => (n.dataType === 'double' || n.dataType === 'float' || n.dataType === 'int32') && n.status === 'good')
)

// 分页数据
const paginatedTableData = computed(() => {
  let filtered = [...allNodes.value]

  if (filterForm.serverUrl) {
    filtered = filtered.filter(item => item.serverUrl?.toLowerCase().includes(filterForm.serverUrl.toLowerCase()))
  }
  if (filterForm.namespace) {
    filtered = filtered.filter(item => item.namespace?.toLowerCase().includes(filterForm.namespace.toLowerCase()))
  }
  if (filterForm.nodeType) {
    filtered = filtered.filter(item => item.nodeClass === filterForm.nodeType)
  }
  if (filterForm.dataType) {
    filtered = filtered.filter(item => item.dataType === filterForm.dataType)
  }
  if (filterForm.browseName) {
    filtered = filtered.filter(item => item.browseName?.toLowerCase().includes(filterForm.browseName.toLowerCase()))
  }

  pageInfo.total = filtered.length
  const start = (pageInfo.pageNum - 1) * pageInfo.pageSize
  return filtered.slice(start, start + pageInfo.pageSize)
})

// ========== 生成模拟数据 ==========
const generateNodeTree = () => {
  return [
    {
      nodeId: 'ns=2;s=Root',
      displayName: 'Root',
      browseName: 'Root',
      nodeClass: 'object',
      children: [
        {
          nodeId: 'ns=2;s=Objects',
          displayName: 'Objects',
          browseName: 'Objects',
          nodeClass: 'object',
          children: [
            {
              nodeId: 'ns=2;s=Server',
              displayName: 'Server',
              browseName: 'Server',
              nodeClass: 'object',
              status: 'good',
              children: [
                { nodeId: 'ns=2;s=ServerStatus', displayName: 'ServerStatus', browseName: 'ServerStatus', nodeClass: 'variable', dataType: 'string', value: 'Running', status: 'good' },
                { nodeId: 'ns=2;s=CurrentTime', displayName: 'CurrentTime', browseName: 'CurrentTime', nodeClass: 'variable', dataType: 'datetime', value: new Date().toISOString(), status: 'good' }
              ]
            },
            {
              nodeId: 'ns=2;s=HVAC',
              displayName: 'HVAC System',
              browseName: 'HVAC',
              nodeClass: 'object',
              children: [
                { nodeId: 'ns=2;s=AHU_Temp', displayName: 'AHU Supply Temp', browseName: 'AHU_Temp', nodeClass: 'variable', dataType: 'double', value: 22.5, unit: '°C', status: 'good' },
                { nodeId: 'ns=2;s=AHU_Humidity', displayName: 'AHU Humidity', browseName: 'AHU_Humidity', nodeClass: 'variable', dataType: 'double', value: 55.2, unit: '%', status: 'good' },
                { nodeId: 'ns=2;s=Chiller_Status', displayName: 'Chiller Status', browseName: 'Chiller_Status', nodeClass: 'variable', dataType: 'boolean', value: true, status: 'good' },
                { nodeId: 'ns=2;s=Chiller_Power', displayName: 'Chiller Power', browseName: 'Chiller_Power', nodeClass: 'variable', dataType: 'double', value: 85.3, unit: 'kW', status: 'uncertain' }
              ]
            },
            {
              nodeId: 'ns=2;s=Lighting',
              displayName: 'Lighting System',
              browseName: 'Lighting',
              nodeClass: 'object',
              children: [
                { nodeId: 'ns=2;s=Light_Level', displayName: 'Light Level', browseName: 'Light_Level', nodeClass: 'variable', dataType: 'double', value: 78.5, unit: '%', status: 'good' },
                { nodeId: 'ns=2;s=Light_Status', displayName: 'Light Status', browseName: 'Light_Status', nodeClass: 'variable', dataType: 'boolean', value: true, status: 'good' }
              ]
            },
            {
              nodeId: 'ns=2;s=Power',
              displayName: 'Power Monitoring',
              browseName: 'Power',
              nodeClass: 'object',
              children: [
                { nodeId: 'ns=2;s=Total_Power', displayName: 'Total Power', browseName: 'Total_Power', nodeClass: 'variable', dataType: 'double', value: 245.6, unit: 'kW', status: 'good' },
                { nodeId: 'ns=2;s=Voltage_L1', displayName: 'Voltage L1', browseName: 'Voltage_L1', nodeClass: 'variable', dataType: 'double', value: 230.1, unit: 'V', status: 'good' },
                { nodeId: 'ns=2;s=Current_L1', displayName: 'Current L1', browseName: 'Current_L1', nodeClass: 'variable', dataType: 'double', value: 32.5, unit: 'A', status: 'good' }
              ]
            }
          ]
        }
      ]
    }
  ]
}

const generateNodesList = () => {
  const nodes = [
    { id: 1, nodeId: 'ns=2;s=AHU_Temp', browseName: 'AHU_Temp', displayName: 'AHU Supply Temp', nodeClass: 'variable', dataType: 'double', value: 22.5, unit: '°C', status: 'good', timestamp: new Date().toLocaleString(), serverUrl: 'opc.tcp://server:4840', namespace: 'http://example.com/hvac', subscribed: true },
    { id: 2, nodeId: 'ns=2;s=AHU_Humidity', browseName: 'AHU_Humidity', displayName: 'AHU Humidity', nodeClass: 'variable', dataType: 'double', value: 55.2, unit: '%', status: 'good', timestamp: new Date().toLocaleString(), serverUrl: 'opc.tcp://server:4840', namespace: 'http://example.com/hvac', subscribed: true },
    { id: 3, nodeId: 'ns=2;s=Chiller_Status', browseName: 'Chiller_Status', displayName: 'Chiller Status', nodeClass: 'variable', dataType: 'boolean', value: true, unit: '', status: 'good', timestamp: new Date().toLocaleString(), serverUrl: 'opc.tcp://server:4840', namespace: 'http://example.com/hvac', subscribed: false },
    { id: 4, nodeId: 'ns=2;s=Chiller_Power', browseName: 'Chiller_Power', displayName: 'Chiller Power', nodeClass: 'variable', dataType: 'double', value: 85.3, unit: 'kW', status: 'uncertain', timestamp: new Date().toLocaleString(), serverUrl: 'opc.tcp://server:4840', namespace: 'http://example.com/hvac', subscribed: true },
    { id: 5, nodeId: 'ns=2;s=Light_Level', browseName: 'Light_Level', displayName: 'Light Level', nodeClass: 'variable', dataType: 'double', value: 78.5, unit: '%', status: 'good', timestamp: new Date().toLocaleString(), serverUrl: 'opc.tcp://server:4840', namespace: 'http://example.com/lighting', subscribed: false },
    { id: 6, nodeId: 'ns=2;s=Light_Status', browseName: 'Light_Status', displayName: 'Light Status', nodeClass: 'variable', dataType: 'boolean', value: true, unit: '', status: 'good', timestamp: new Date().toLocaleString(), serverUrl: 'opc.tcp://server:4840', namespace: 'http://example.com/lighting', subscribed: true },
    { id: 7, nodeId: 'ns=2;s=Total_Power', browseName: 'Total_Power', displayName: 'Total Power', nodeClass: 'variable', dataType: 'double', value: 245.6, unit: 'kW', status: 'good', timestamp: new Date().toLocaleString(), serverUrl: 'opc.tcp://server:4840', namespace: 'http://example.com/power', subscribed: true },
    { id: 8, nodeId: 'ns=2;s=Voltage_L1', browseName: 'Voltage_L1', displayName: 'Voltage L1', nodeClass: 'variable', dataType: 'double', value: 230.1, unit: 'V', status: 'good', timestamp: new Date().toLocaleString(), serverUrl: 'opc.tcp://server:4840', namespace: 'http://example.com/power', subscribed: false },
    { id: 9, nodeId: 'ns=2;s=ServerStatus', browseName: 'ServerStatus', displayName: 'Server Status', nodeClass: 'variable', dataType: 'string', value: 'Running', unit: '', status: 'good', timestamp: new Date().toLocaleString(), serverUrl: 'opc.tcp://server:4840', namespace: 'http://opcfoundation.org/UA/', subscribed: true }
  ]
  allNodes.value = nodes
  if (analogNodes.value.length > 0) {
    trendNodeId.value = analogNodes.value[0].id.toString()
  }
}

// 更新节点值
const updateNodeValues = () => {
  for (const node of allNodes.value) {
    if (node.status === 'good' && (node.dataType === 'double' || node.dataType === 'float')) {
      const change = (Math.random() - 0.5) * 1.5
      node.value = Number((node.value + change).toFixed(1))
      node.timestamp = new Date().toLocaleString()
    } else if (node.status === 'good' && node.dataType === 'boolean') {
      node.value = Math.random() > 0.9 ? !node.value : node.value
      node.timestamp = new Date().toLocaleString()
    }
    // 随机改变状态
    if (Math.random() > 0.98) {
      node.status = node.status === 'good' ? 'uncertain' : 'good'
    }
  }
}

// ========== Chart Data ==========
const trendHistory = ref<{ timestamps: string[]; values: number[] }>({
  timestamps: [],
  values: []
})

// 获取节点历史数据
const getNodeHistory = () => {
  const node = analogNodes.value.find(n => n.id.toString() === trendNodeId.value)
  if (!node) return

  const timestamps = []
  const values = []
  const now = new Date()
  const baseValue = typeof node.value === 'number' ? node.value : 50

  for (let i = 23; i >= 0; i--) {
    const time = new Date(now.getTime() - i * 3600000)
    timestamps.push(`${String(time.getHours()).padStart(2, '0')}:00`)
    const variation = Math.sin(i * 0.3) * 5 + (Math.random() - 0.5) * 2
    values.push(Number((baseValue + variation).toFixed(1)))
  }

  trendHistory.value = { timestamps, values }
}

// 添加新数据点
const appendTrendData = () => {
  const node = analogNodes.value.find(n => n.id.toString() === trendNodeId.value)
  if (!node) return

  const now = new Date()
  const timeStr = `${String(now.getHours()).padStart(2, '0')}:00`
  const newValue = typeof node.value === 'number' ? node.value : 50

  trendHistory.value.timestamps.push(timeStr)
  trendHistory.value.values.push(newValue)

  if (trendHistory.value.timestamps.length > 48) {
    trendHistory.value.timestamps.shift()
    trendHistory.value.values.shift()
  }

  updateTrendChart()
}

// 初始化趋势图
const initTrendChart = async () => {
  await nextTick()
  if (!trendChartRef.value) {
    setTimeout(() => initTrendChart(), 100)
    return
  }

  if (trendInstance) trendInstance.dispose()

  getNodeHistory()
  trendInstance = echarts.init(trendChartRef.value)
  updateTrendChart()
  window.addEventListener('resize', handleChartResize)
}

const updateTrendChart = () => {
  if (!trendInstance || !trendHistory.value.timestamps.length) return

  const node = analogNodes.value.find(n => n.id.toString() === trendNodeId.value)
  const unit = node?.unit || ''

  const option = {
    tooltip: { trigger: 'axis', formatter: (params: any) => `${params[0].axisValue}<br/>Value: ${params[0].value} ${unit}` },
    grid: { left: '8%', right: '5%', top: '12%', bottom: '8%', containLabel: true },
    xAxis: { type: 'category', data: trendHistory.value.timestamps, axisLabel: { rotate: 45, interval: 4, fontSize: 10 } },
    yAxis: { type: 'value', name: `Value (${unit})`, nameTextStyle: { fontSize: 12 } },
    series: [{
      name: node?.displayName || 'Value',
      type: 'line',
      data: trendHistory.value.values,
      smooth: true,
      lineStyle: { color: '#409eff', width: 2 },
      areaStyle: { opacity: 0.1, color: '#409eff' },
      symbol: 'circle',
      symbolSize: 5
    }]
  }
  trendInstance.setOption(option, true)
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

  const goodCount = allNodes.value.filter(n => n.status === 'good').length
  const uncertainCount = allNodes.value.filter(n => n.status === 'uncertain').length
  const badCount = allNodes.value.filter(n => n.status === 'bad').length

  const option = {
    tooltip: { trigger: 'item', formatter: '{b}: {d}% ({c})' },
    legend: { orient: 'vertical', left: 'left', data: ['Good', 'Uncertain', 'Bad'] },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      data: [
        { name: 'Good', value: goodCount, itemStyle: { color: '#67c23a' } },
        { name: 'Uncertain', value: uncertainCount, itemStyle: { color: '#e6a23c' } },
        { name: 'Bad', value: badCount, itemStyle: { color: '#f56c6c' } }
      ],
      emphasis: { scale: true },
      label: { show: true, formatter: '{b}', position: 'outside' }
    }]
  }
  pieInstance.setOption(option)
}

const updatePieChart = () => {
  if (!pieInstance) return
  const goodCount = allNodes.value.filter(n => n.status === 'good').length
  const uncertainCount = allNodes.value.filter(n => n.status === 'uncertain').length
  const badCount = allNodes.value.filter(n => n.status === 'bad').length
  pieInstance.setOption({ series: [{ data: [{ name: 'Good', value: goodCount }, { name: 'Uncertain', value: uncertainCount }, { name: 'Bad', value: badCount }] }] })
}

const handleChartResize = () => {
  if (trendInstance) trendInstance.resize()
  if (pieInstance) pieInstance.resize()
}

// ========== Helper Functions ==========
const getNodeIcon = (nodeClass: string) => {
  const icons: Record<string, any> = { object: Folder, variable: Document, method: Tools, property: Setting }
  return icons[nodeClass] || Document
}

const getNodeIconClass = (nodeClass: string) => {
  return `node-icon ${nodeClass}`
}

const getStatusTagType = (status: string) => {
  const map: Record<string, string> = { good: 'success', uncertain: 'warning', bad: 'danger' }
  return map[status] || 'info'
}

const getValueClass = (row: any) => {
  if (row.status === 'uncertain') return 'text-warning'
  if (row.status === 'bad') return 'text-danger'
  return ''
}

const formatValue = (value: any) => {
  if (typeof value === 'boolean') return value ? 'True' : 'False'
  if (typeof value === 'number') return value.toFixed(2)
  return value
}

const filterNode = (value: string, data: any) => {
  if (!value) return true
  return data.displayName?.toLowerCase().includes(value.toLowerCase())
}

const expandAll = () => {
  const allKeys: string[] = []
  const collectKeys = (nodes: any[]) => {
    nodes.forEach(node => {
      allKeys.push(node.nodeId)
      if (node.children) collectKeys(node.children)
    })
  }
  collectKeys(nodeTree.value)
  expandedKeys.value = allKeys
}

const onNodeClick = (data: any) => {
  if (data.nodeClass === 'variable') {
    const node = allNodes.value.find(n => n.nodeId === data.nodeId)
    if (node) viewDetail(node)
  }
}

// ========== Actions ==========
const handleSearch = () => { pageInfo.pageNum = 1 }
const resetFilter = () => {
  filterForm.serverUrl = ''
  filterForm.namespace = ''
  filterForm.nodeType = ''
  filterForm.dataType = ''
  filterForm.browseName = ''
  pageInfo.pageNum = 1
}

const refreshData = async () => {
  refreshing.value = true
  tableLoading.value = true
  await new Promise(resolve => setTimeout(resolve, 500))
  generateNodesList()
  nodeTree.value = generateNodeTree()
  updatePieChart()
  if (analogNodes.value.length > 0 && !trendNodeId.value) {
    trendNodeId.value = analogNodes.value[0].id.toString()
    getNodeHistory()
    updateTrendChart()
  }
  tableLoading.value = false
  refreshing.value = false
  ElMessage.success('Data refreshed')
}

const handlePageSizeChange = () => { pageInfo.pageNum = 1 }
const handlePageChange = () => {}

const viewDetail = (row: any) => {
  ElMessage.info(`Viewing details for node: ${row.displayName}`)
}

const writeValue = (row: any) => {
  selectedNode.value = row
  writeForm.value.value = row.value
  writeDialogVisible.value = true
}

const confirmWrite = async () => {
  writing.value = true
  await new Promise(resolve => setTimeout(resolve, 800))
  if (selectedNode.value) {
    selectedNode.value.value = writeForm.value.value
    selectedNode.value.timestamp = new Date().toLocaleString()
    ElMessage.success(`Value written to ${selectedNode.value.displayName}`)
  }
  writeDialogVisible.value = false
  writing.value = false
}

const subscribeNode = (row: any) => {
  row.subscribed = !row.subscribed
  ElMessage.success(row.subscribed ? `Subscribed to ${row.displayName}` : `Unsubscribed from ${row.displayName}`)
}

const openBrowseDialog = () => {
  browserTreeData.value = generateNodeTree()
  browseDialogVisible.value = true
}

const onBrowserNodeClick = (data: any) => {
  selectedBrowserNode.value = data
}

const importNode = () => {
  if (selectedBrowserNode.value && selectedBrowserNode.value.nodeClass === 'variable') {
    const existing = allNodes.value.find(n => n.nodeId === selectedBrowserNode.value.nodeId)
    if (!existing) {
      const newNode = {
        id: allNodes.value.length + 1,
        nodeId: selectedBrowserNode.value.nodeId,
        browseName: selectedBrowserNode.value.browseName,
        displayName: selectedBrowserNode.value.displayName,
        nodeClass: selectedBrowserNode.value.nodeClass,
        dataType: selectedBrowserNode.value.dataType || 'double',
        value: selectedBrowserNode.value.value || 0,
        unit: '',
        status: 'good',
        timestamp: new Date().toLocaleString(),
        serverUrl: 'opc.tcp://server:4840',
        namespace: 'http://example.com',
        subscribed: false
      }
      allNodes.value.push(newNode)
      ElMessage.success(`Node ${newNode.displayName} imported`)
    } else {
      ElMessage.warning('Node already exists')
    }
  }
  browseDialogVisible.value = false
}

// 实时更新
const startRealtimeUpdates = () => {
  realtimeTimer = window.setInterval(() => {
    updateNodeValues()
    appendTrendData()
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
      generateNodesList()
      nodeTree.value = generateNodeTree()
      isLoaded.value = true
      await nextTick()

      setTimeout(async () => {
        await initTrendChart()
        await initPieChart()
        startRealtimeUpdates()
      }, 200)
    }, 400)
  }, 2000)
})

onUnmounted(() => {
  if (realtimeTimer) clearInterval(realtimeTimer)
  if (trendInstance) trendInstance.dispose()
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
.opcua-point-container {
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

.tree-card {
  margin-bottom: 20px;
  border-radius: 12px;
}

.tree-container {
  height: 300px;
  overflow-y: auto;
}

.tree-node {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 4px 0;
}

.node-name {
  font-weight: 500;
  color: #1e293b;
}

.node-id {
  font-size: 11px;
  color: #94a3b8;
}

.node-value {
  font-size: 12px;
  color: #409eff;
  margin-left: auto;
}

.node-icon.object { color: #f59e0b; }
.node-icon.variable { color: #409eff; }
.node-icon.method { color: #67c23a; }

.status-badge {
  margin-left: 8px;
}

.text-warning { color: #e6a23c; font-weight: 500; }
.text-danger { color: #f56c6c; font-weight: 500; }

.pagination-wrap {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

.browser-container {
  display: flex;
  gap: 20px;
  height: 500px;
}

.browser-tree {
  flex: 1;
  overflow-y: auto;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 8px;
}

.browser-detail {
  flex: 1;
  overflow-y: auto;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 16px;
}

.browser-node {
  display: flex;
  align-items: center;
  gap: 8px;
}

.node-id-browser {
  font-size: 11px;
  color: #94a3b8;
  margin-left: auto;
}

.node-detail h4 {
  margin: 0 0 16px 0;
}

@media (max-width: 1024px) {
  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
  }
  .charts-row {
    flex-direction: column;
  }
  .browser-container {
    flex-direction: column;
    height: auto;
  }
  .browser-tree, .browser-detail {
    max-height: 300px;
  }
}

@media (max-width: 768px) {
  .opcua-point-container {
    padding: 12px;
  }
  .stats-cards {
    grid-template-columns: 1fr;
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
  .tree-node {
    flex-wrap: wrap;
  }
  .node-value {
    margin-left: 0;
  }
}
</style>