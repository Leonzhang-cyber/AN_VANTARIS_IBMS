<template>
  <!-- Loading Screen -->
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
        <div class="loading-tip">OPC-UA Gateway Management</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="opcua-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <div class="breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>Integration Hub</el-breadcrumb-item>
            <el-breadcrumb-item>Protocol Gateway</el-breadcrumb-item>
            <el-breadcrumb-item>OPC-UA</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <h1>OPC-UA Gateway Management</h1>
        <p class="description">Manage OPC-UA server connections, browse address space, and subscribe to data points</p>
      </div>
      <div class="header-actions">
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>
          Export Config
        </el-button>
        <el-button type="primary" @click="openAddGatewayDialog">
          <el-icon><Plus /></el-icon>
          Add Connection
        </el-button>
      </div>
    </div>

    <!-- Stats Cards -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :lg="6" v-for="stat in statsCards" :key="stat.title">
        <el-card class="stat-card" shadow="hover" @click="handleCardClick(stat)">
          <div class="stat-content">
            <div class="stat-info">
              <div class="stat-title">{{ stat.title }}</div>
              <div class="stat-value">{{ stat.value }}</div>
              <div class="stat-trend" :class="stat.trend > 0 ? 'up' : 'down'">
                <el-icon><component :is="stat.trend > 0 ? 'ArrowUp' : 'ArrowDown'" /></el-icon>
                {{ Math.abs(stat.trend) }}%
                <span class="trend-label">vs last week</span>
              </div>
            </div>
            <div class="stat-icon" :style="{ background: stat.bgColor }">
              <el-icon :size="28" color="white">
                <component :is="stat.icon" />
              </el-icon>
            </div>
          </div>
          <div class="stat-footer">
            <span>{{ stat.subTitle }}</span>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Connection Status Overview -->
    <el-row :gutter="20" class="status-row">
      <el-col :xs="24" :lg="16">
        <el-card class="connection-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Connection Status</span>
              <el-button size="small" @click="refreshConnections">
                <el-icon><Refresh /></el-icon> Refresh
              </el-button>
            </div>
          </template>
          <div class="connection-stats">
            <div class="stat-badge online">
              <div class="stat-number">{{ onlineCount }}</div>
              <div class="stat-label">Online</div>
            </div>
            <div class="stat-badge offline">
              <div class="stat-number">{{ offlineCount }}</div>
              <div class="stat-label">Offline</div>
            </div>
            <div class="stat-badge warning">
              <div class="stat-number">{{ warningCount }}</div>
              <div class="stat-label">Warning</div>
            </div>
            <div class="stat-badge total">
              <div class="stat-number">{{ totalConnections }}</div>
              <div class="stat-label">Total</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="8">
        <el-card class="metrics-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Performance Metrics</span>
            </div>
          </template>
          <div class="metrics-list">
            <div class="metric-item">
              <span class="metric-label">Avg Response Time</span>
              <span class="metric-value">124 ms</span>
              <span class="metric-trend down">-8%</span>
            </div>
            <div class="metric-item">
              <span class="metric-label">Subscription Rate</span>
              <span class="metric-value">1,234/s</span>
              <span class="metric-trend up">+12%</span>
            </div>
            <div class="metric-item">
              <span class="metric-label">Data Change Rate</span>
              <span class="metric-value">856/s</span>
              <span class="metric-trend up">+5%</span>
            </div>
            <div class="metric-item">
              <span class="metric-label">Session Uptime</span>
              <span class="metric-value">99.95%</span>
              <span class="metric-trend up">+0.2%</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- OPC-UA Connections Table -->
    <el-card class="connections-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>OPC-UA Connections</span>
          <div class="table-actions">
            <el-input
                v-model="searchKeyword"
                placeholder="Search by name or URL"
                prefix-icon="Search"
                clearable
                style="width: 220px"
            />
            <el-select v-model="statusFilter" placeholder="Status" clearable style="width: 120px">
              <el-option label="Online" value="Online" />
              <el-option label="Offline" value="Offline" />
              <el-option label="Warning" value="Warning" />
            </el-select>
            <el-button :icon="Refresh" @click="fetchConnections" circle />
          </div>
        </div>
      </template>

      <el-table :data="paginatedConnections" stripe style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="name" label="Connection Name" min-width="180" show-overflow-tooltip />
        <el-table-column prop="endpointUrl" label="Endpoint URL" min-width="250" show-overflow-tooltip />
        <el-table-column prop="securityMode" label="Security" width="120">
          <template #default="{ row }">
            <el-tag :type="row.securityMode === 'None' ? 'info' : 'success'" size="small">{{ row.securityMode }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="nodeCount" label="Nodes" width="80" align="center" />
        <el-table-column prop="subscriptionCount" label="Subscriptions" width="110" align="center" />
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'Online' ? 'success' : row.status === 'Warning' ? 'warning' : 'danger'" size="small">
              <span class="status-dot" :class="row.status === 'Online' ? 'online' : 'offline'"></span>
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="lastSeen" label="Last Seen" width="150" />
        <el-table-column label="Actions" width="280" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="browseNodes(row)">Browse</el-button>
            <el-button link type="success" size="small" @click="viewSubscriptions(row)">Subscriptions</el-button>
            <el-button link type="info" size="small" @click="testConnection(row)">Test</el-button>
            <el-button link type="danger" size="small" @click="deleteConnection(row)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="filteredConnections.length"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- Node Browser Section -->
    <el-card class="browser-card" shadow="hover" v-if="selectedConnection">
      <template #header>
        <div class="card-header">
          <span>Address Space Browser - {{ selectedConnection.name }}</span>
          <div class="browser-actions">
            <el-input
                v-model="nodeSearch"
                placeholder="Search nodes"
                prefix-icon="Search"
                clearable
                size="small"
                style="width: 200px"
            />
            <el-button size="small" @click="refreshNodes">
              <el-icon><Refresh /></el-icon> Refresh
            </el-button>
          </div>
        </div>
      </template>

      <el-row :gutter="20">
        <el-col :span="12">
          <div class="node-tree">
            <el-tree
                ref="nodeTreeRef"
                :data="nodeTreeData"
                :props="treeProps"
                node-key="nodeId"
                default-expand-all
                highlight-current
                @node-click="handleNodeClick"
            >
              <template #default="{ node, data }">
                <span class="tree-node">
                  <el-icon :color="getNodeIconColor(data.nodeClass)">
                    <component :is="getNodeIcon(data.nodeClass)" />
                  </el-icon>
                  <span>{{ node.label }}</span>
                  <el-tag v-if="data.dataType" size="small" type="info" class="node-tag">{{ data.dataType }}</el-tag>
                </span>
              </template>
            </el-tree>
          </div>
        </el-col>

        <el-col :span="12">
          <div class="node-details" v-if="selectedNode">
            <el-descriptions :column="1" border size="small">
              <el-descriptions-item label="Node ID">{{ selectedNode.nodeId }}</el-descriptions-item>
              <el-descriptions-item label="Display Name">{{ selectedNode.displayName }}</el-descriptions-item>
              <el-descriptions-item label="Node Class">{{ selectedNode.nodeClass }}</el-descriptions-item>
              <el-descriptions-item label="Data Type" v-if="selectedNode.dataType">{{ selectedNode.dataType }}</el-descriptions-item>
              <el-descriptions-item label="Value" v-if="selectedNode.value !== undefined">
                <span class="node-value">{{ selectedNode.value }}</span>
              </el-descriptions-item>
              <el-descriptions-item label="Description">{{ selectedNode.description || 'N/A' }}</el-descriptions-item>
            </el-descriptions>
            <div class="node-actions" v-if="selectedNode.nodeClass === 'Variable'">
              <el-button type="primary" size="small" @click="subscribeToNode(selectedNode)">Subscribe</el-button>
              <el-button size="small" @click="readNodeValue(selectedNode)">Read Now</el-button>
              <el-button v-if="selectedNode.writable" size="small" @click="writeNodeValue(selectedNode)">Write</el-button>
            </div>
          </div>
          <div class="node-empty" v-else>
            <el-empty description="Select a node from the tree to view details" :image-size="80" />
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- Subscriptions Section -->
    <el-card class="subscriptions-card" shadow="hover" v-if="selectedConnection && showSubscriptions">
      <template #header>
        <div class="card-header">
          <span>Data Subscriptions - {{ selectedConnection.name }}</span>
          <div class="subscription-actions">
            <el-button size="small" type="primary" @click="openAddSubscriptionDialog">
              <el-icon><Plus /></el-icon> Add Subscription
            </el-button>
            <el-button size="small" @click="refreshSubscriptions">
              <el-icon><Refresh /></el-icon> Refresh
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="subscriptions" stripe style="width: 100%" v-loading="subscriptionsLoading">
        <el-table-column prop="nodeId" label="Node ID" min-width="200" show-overflow-tooltip />
        <el-table-column prop="displayName" label="Display Name" min-width="180" show-overflow-tooltip />
        <el-table-column prop="samplingInterval" label="Interval (ms)" width="110" align="center" />
        <el-table-column prop="currentValue" label="Current Value" width="150" align="right">
          <template #default="{ row }">
            <span class="subscription-value">{{ row.currentValue }} {{ row.unit || '' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'Active' ? 'success' : 'warning'" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="lastUpdate" label="Last Update" width="150" />
        <el-table-column label="Actions" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="editSubscription(row)">Edit</el-button>
            <el-button link type="danger" size="small" @click="deleteSubscription(row)">Unsubscribe</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Add/Edit OPC-UA Connection Dialog -->
    <el-dialog v-model="connectionDialogVisible" :title="dialogMode === 'add' ? 'Add OPC-UA Connection' : 'Edit OPC-UA Connection'" width="650px" destroy-on-close class="connection-dialog">
      <el-tabs v-model="activeConfigTab">
        <el-tab-pane label="Connection Settings" name="basic">
          <el-form :model="connectionForm" :rules="connectionRules" ref="connectionFormRef" label-width="130px">
            <el-form-item label="Connection Name" prop="name">
              <el-input v-model="connectionForm.name" placeholder="Enter connection name" />
            </el-form-item>
            <el-form-item label="Endpoint URL" prop="endpointUrl">
              <el-input v-model="connectionForm.endpointUrl" placeholder="opc.tcp://192.168.1.100:4840" />
            </el-form-item>
            <el-form-item label="Security Mode" prop="securityMode">
              <el-select v-model="connectionForm.securityMode" style="width: 100%">
                <el-option label="None" value="None" />
                <el-option label="Sign" value="Sign" />
                <el-option label="Sign and Encrypt" value="SignAndEncrypt" />
              </el-select>
            </el-form-item>
            <el-form-item label="Security Policy" prop="securityPolicy">
              <el-select v-model="connectionForm.securityPolicy" style="width: 100%">
                <el-option label="None" value="None" />
                <el-option label="Basic128Rsa15" value="Basic128Rsa15" />
                <el-option label="Basic256" value="Basic256" />
                <el-option label="Basic256Sha256" value="Basic256Sha256" />
              </el-select>
            </el-form-item>
            <el-form-item label="Authentication" prop="authType">
              <el-radio-group v-model="connectionForm.authType">
                <el-radio value="anonymous">Anonymous</el-radio>
                <el-radio value="username">Username/Password</el-radio>
                <el-radio value="certificate">Certificate</el-radio>
              </el-radio-group>
            </el-form-item>
            <template v-if="connectionForm.authType === 'username'">
              <el-form-item label="Username" prop="username">
                <el-input v-model="connectionForm.username" placeholder="Username" />
              </el-form-item>
              <el-form-item label="Password" prop="password">
                <el-input v-model="connectionForm.password" type="password" placeholder="Password" />
              </el-form-item>
            </template>
            <template v-if="connectionForm.authType === 'certificate'">
              <el-form-item label="Certificate File" prop="certificate">
                <el-upload action="#" :auto-upload="false" :on-change="handleCertUpload" :limit="1">
                  <el-button size="small">Select Certificate</el-button>
                </el-upload>
              </el-form-item>
              <el-form-item label="Private Key" prop="privateKey">
                <el-upload action="#" :auto-upload="false" :on-change="handleKeyUpload" :limit="1">
                  <el-button size="small">Select Private Key</el-button>
                </el-upload>
              </el-form-item>
            </template>
            <el-form-item label="Session Timeout (ms)" prop="sessionTimeout">
              <el-input-number v-model="connectionForm.sessionTimeout" :min="1000" :max="600000" :step="1000" style="width: 100%" />
            </el-form-item>
            <el-form-item label="Description" prop="description">
              <el-input v-model="connectionForm.description" type="textarea" :rows="2" placeholder="Enter description" />
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="Advanced" name="advanced">
          <el-form label-width="150px">
            <el-form-item label="Max Subscriptions">
              <el-input-number v-model="connectionForm.maxSubscriptions" :min="1" :max="1000" style="width: 100%" />
            </el-form-item>
            <el-form-item label="Max Subscription Interval">
              <el-input-number v-model="connectionForm.maxSubscriptionInterval" :min="100" :max="60000" style="width: 100%" />
            </el-form-item>
            <el-form-item label="Auto Reconnect">
              <el-switch v-model="connectionForm.autoReconnect" />
            </el-form-item>
            <el-form-item label="Enable Logging">
              <el-switch v-model="connectionForm.enableLogging" />
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>

      <template #footer>
        <el-button @click="connectionDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="testConnection" :loading="testing">
          Test Connection
        </el-button>
        <el-button type="success" @click="saveConnection">
          Save Connection
        </el-button>
      </template>
    </el-dialog>

    <!-- Add Subscription Dialog -->
    <el-dialog v-model="subscriptionDialogVisible" title="Add Subscription" width="550px" destroy-on-close>
      <el-form :model="subscriptionForm" :rules="subscriptionRules" ref="subscriptionFormRef" label-width="130px">
        <el-form-item label="Node ID" prop="nodeId">
          <el-input v-model="subscriptionForm.nodeId" placeholder="ns=2;s=Channel1.Device1.Temperature" />
        </el-form-item>
        <el-form-item label="Display Name" prop="displayName">
          <el-input v-model="subscriptionForm.displayName" placeholder="Enter display name" />
        </el-form-item>
        <el-form-item label="Sampling Interval (ms)" prop="samplingInterval">
          <el-input-number v-model="subscriptionForm.samplingInterval" :min="100" :max="60000" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Queue Size" prop="queueSize">
          <el-input-number v-model="subscriptionForm.queueSize" :min="1" :max="1000" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Deadband" prop="deadband">
          <el-input-number v-model="subscriptionForm.deadband" :min="0" :max="100" :step="0.1" style="width: 100%" />
          <span style="margin-left: 8px; color: #909399">% of value change to trigger update</span>
        </el-form-item>
        <el-form-item label="Unit" prop="unit">
          <el-input v-model="subscriptionForm.unit" placeholder="°C, kW, %" />
        </el-form-item>
        <el-form-item label="Description" prop="description">
          <el-input v-model="subscriptionForm.description" type="textarea" :rows="2" placeholder="Enter description" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="subscriptionDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="saveSubscription">Subscribe</el-button>
      </template>
    </el-dialog>

    <!-- Write Value Dialog -->
    <el-dialog v-model="writeDialogVisible" title="Write Value" width="450px" destroy-on-close>
      <el-form label-width="100px">
        <el-form-item label="Node ID">
          <span class="write-node-id">{{ writeNode?.nodeId }}</span>
        </el-form-item>
        <el-form-item label="Current Value">
          <span class="write-current-value">{{ writeNode?.value }} {{ writeNode?.unit || '' }}</span>
        </el-form-item>
        <el-form-item label="New Value">
          <el-input v-model="writeValue" placeholder="Enter new value" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="writeDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="submitWrite">Write</el-button>
      </template>
    </el-dialog>

    <!-- Test Result Dialog -->
    <el-dialog v-model="testDialogVisible" title="Connection Test Result" width="450px">
      <div class="test-result">
        <el-result
            :icon="testResult.success ? 'success' : 'error'"
            :title="testResult.success ? 'Connection Successful' : 'Connection Failed'"
            :sub-title="testResult.message"
        />
        <div v-if="testResult.success && testResult.details" class="test-details">
          <p><strong>Server:</strong> {{ testResult.details.serverName }}</p>
          <p><strong>Version:</strong> {{ testResult.details.version }}</p>
          <p><strong>Response Time:</strong> {{ testResult.details.responseTime }}ms</p>
          <p><strong>Available Nodes:</strong> {{ testResult.details.nodeCount }}</p>
        </div>
      </div>
      <template #footer>
        <el-button @click="testDialogVisible = false">Close</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, ArrowUp, ArrowDown, Document, Checked,
  Clock, TrendCharts, Refresh, Search, Download,
  Delete, Connection, Edit, Folder, DataAnalysis, Monitor
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const loadingMessages = ['Preparing...', 'Initializing OPC-UA gateway...', 'Loading connections...', 'Almost ready...']

// ==================== State ====================
const tableLoading = ref(false)
const subscriptionsLoading = ref(false)
const testing = ref(false)
const connectionDialogVisible = ref(false)
const subscriptionDialogVisible = ref(false)
const testDialogVisible = ref(false)
const writeDialogVisible = ref(false)
const dialogMode = ref<'add' | 'edit'>('add')
const selectedConnection = ref<any>(null)
const selectedNode = ref<any>(null)
const writeNode = ref<any>(null)
const showSubscriptions = ref(false)
const searchKeyword = ref('')
const nodeSearch = ref('')
const statusFilter = ref('')
const activeConfigTab = ref('basic')
const currentPage = ref(1)
const pageSize = ref(10)
const writeValue = ref('')
const testResult = reactive({ success: false, message: '', details: null as any })

const connectionFormRef = ref()
const subscriptionFormRef = ref()
const nodeTreeRef = ref()

// ==================== Mock Data ====================
const statsCards = ref([
  { title: 'Connections', value: '8', trend: 2, icon: 'Connection', bgColor: '#409eff', key: 'connections', subTitle: 'Active: 6' },
  { title: 'Subscriptions', value: '156', trend: 12, icon: 'Document', bgColor: '#67c23a', key: 'subscriptions', subTitle: 'Active: 148' },
  { title: 'Data Points', value: '2,345', trend: 18, icon: 'DataAnalysis', bgColor: '#e6a23c', key: 'points', subTitle: 'Updated: 2,210' },
  { title: 'Messages/sec', value: '1,234', trend: 8, icon: 'TrendCharts', bgColor: '#f56c6c', key: 'rate', subTitle: 'Peak: 1,567' }
])

const connections = ref([
  { id: 1, name: 'Factory PLC Server', endpointUrl: 'opc.tcp://192.168.1.100:4840', securityMode: 'SignAndEncrypt', nodeCount: 1250, subscriptionCount: 45, status: 'Online', lastSeen: '2024-01-20 10:30:00' },
  { id: 2, name: 'Simulation Server', endpointUrl: 'opc.tcp://192.168.1.101:4840', securityMode: 'None', nodeCount: 500, subscriptionCount: 23, status: 'Online', lastSeen: '2024-01-20 10:28:00' },
  { id: 3, name: 'Production Line OPC', endpointUrl: 'opc.tcp://192.168.1.102:4840', securityMode: 'Sign', nodeCount: 3200, subscriptionCount: 89, status: 'Online', lastSeen: '2024-01-20 10:32:00' },
  { id: 4, name: 'Quality Control Server', endpointUrl: 'opc.tcp://192.168.1.103:4840', securityMode: 'SignAndEncrypt', nodeCount: 890, subscriptionCount: 34, status: 'Warning', lastSeen: '2024-01-20 10:25:00' },
  { id: 5, name: 'Legacy OPC Server', endpointUrl: 'opc.tcp://192.168.1.104:4840', securityMode: 'None', nodeCount: 2100, subscriptionCount: 0, status: 'Offline', lastSeen: '2024-01-20 08:15:00' }
])

// Node tree mock data
const nodeTreeData = ref([
  {
    nodeId: 'ns=2;s=Root',
    displayName: 'Root',
    nodeClass: 'Folder',
    description: 'Root namespace',
    children: [
      {
        nodeId: 'ns=2;s=Objects',
        displayName: 'Objects',
        nodeClass: 'Folder',
        description: 'Objects folder',
        children: [
          {
            nodeId: 'ns=2;s=Objects.Channel1',
            displayName: 'Channel 1',
            nodeClass: 'Folder',
            children: [
              {
                nodeId: 'ns=2;s=Objects.Channel1.Device1',
                displayName: 'Device 1',
                nodeClass: 'Folder',
                children: [
                  { nodeId: 'ns=2;s=Objects.Channel1.Device1.Temperature', displayName: 'Temperature', nodeClass: 'Variable', dataType: 'Double', value: 22.5, unit: '°C', writable: false, description: 'Current temperature reading' },
                  { nodeId: 'ns=2;s=Objects.Channel1.Device1.Pressure', displayName: 'Pressure', nodeClass: 'Variable', dataType: 'Double', value: 101.3, unit: 'kPa', writable: false, description: 'Current pressure reading' },
                  { nodeId: 'ns=2;s=Objects.Channel1.Device1.Setpoint', displayName: 'Setpoint', nodeClass: 'Variable', dataType: 'Double', value: 22.0, unit: '°C', writable: true, description: 'Temperature setpoint' }
                ]
              }
            ]
          }
        ]
      },
      {
        nodeId: 'ns=2;s=Server',
        displayName: 'Server',
        nodeClass: 'Folder',
        children: [
          { nodeId: 'ns=2;s=Server.ServerStatus', displayName: 'Server Status', nodeClass: 'Variable', dataType: 'String', value: 'Running', description: 'Server status' }
        ]
      }
    ]
  }
])

const subscriptions = ref([
  { id: 1, nodeId: 'ns=2;s=Objects.Channel1.Device1.Temperature', displayName: 'Temperature', samplingInterval: 1000, currentValue: 22.5, unit: '°C', status: 'Active', lastUpdate: '2024-01-20 10:30:00' },
  { id: 2, nodeId: 'ns=2;s=Objects.Channel1.Device1.Pressure', displayName: 'Pressure', samplingInterval: 2000, currentValue: 101.3, unit: 'kPa', status: 'Active', lastUpdate: '2024-01-20 10:30:00' }
])

// Tree props
const treeProps = { children: 'children', label: 'displayName' }

// Forms
const connectionForm = reactive({
  id: null, name: '', endpointUrl: '', securityMode: 'None', securityPolicy: 'None',
  authType: 'anonymous', username: '', password: '', certificate: '', privateKey: '',
  sessionTimeout: 60000, description: '', maxSubscriptions: 100, maxSubscriptionInterval: 5000,
  autoReconnect: true, enableLogging: true
})

const subscriptionForm = reactive({
  nodeId: '', displayName: '', samplingInterval: 1000, queueSize: 100, deadband: 0, unit: '', description: ''
})

// Rules
const connectionRules = {
  name: [{ required: true, message: 'Please enter connection name', trigger: 'blur' }],
  endpointUrl: [{ required: true, message: 'Please enter endpoint URL', trigger: 'blur' }]
}

const subscriptionRules = {
  nodeId: [{ required: true, message: 'Please enter node ID', trigger: 'blur' }],
  displayName: [{ required: true, message: 'Please enter display name', trigger: 'blur' }]
}

// ==================== Computed ====================
const totalConnections = computed(() => connections.value.length)
const onlineCount = computed(() => connections.value.filter(c => c.status === 'Online').length)
const offlineCount = computed(() => connections.value.filter(c => c.status === 'Offline').length)
const warningCount = computed(() => connections.value.filter(c => c.status === 'Warning').length)

const filteredConnections = computed(() => {
  let filtered = [...connections.value]
  if (searchKeyword.value) filtered = filtered.filter(c => c.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) || c.endpointUrl.toLowerCase().includes(searchKeyword.value.toLowerCase()))
  if (statusFilter.value) filtered = filtered.filter(c => c.status === statusFilter.value)
  return filtered
})

const paginatedConnections = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredConnections.value.slice(start, end)
})

// ==================== Helper Methods ====================
const getNodeIcon = (nodeClass: string) => {
  const map: Record<string, string> = { 'Folder': 'Folder', 'Variable': 'DataAnalysis', 'Method': 'Monitor', 'Object': 'Document' }
  return map[nodeClass] || 'Document'
}

const getNodeIconColor = (nodeClass: string) => {
  const map: Record<string, string> = { 'Folder': '#e6a23c', 'Variable': '#409eff', 'Method': '#67c23a', 'Object': '#909399' }
  return map[nodeClass] || '#909399'
}

// ==================== Connection Methods ====================
const handleCardClick = (stat: any) => ElMessage.info(`Viewing ${stat.title} details`)
const handleExport = () => ElMessage.success('Exporting OPC-UA configuration...')
const fetchConnections = () => { tableLoading.value = true; setTimeout(() => { tableLoading.value = false; ElMessage.success('Connections refreshed') }, 500) }
const refreshConnections = () => fetchConnections()

const openAddGatewayDialog = () => {
  dialogMode.value = 'add'
  Object.assign(connectionForm, {
    id: null, name: '', endpointUrl: '', securityMode: 'None', securityPolicy: 'None',
    authType: 'anonymous', username: '', password: '', certificate: '', privateKey: '',
    sessionTimeout: 60000, description: '', maxSubscriptions: 100, maxSubscriptionInterval: 5000,
    autoReconnect: true, enableLogging: true
  })
  connectionDialogVisible.value = true
}

const editConnection = (conn: any) => {
  dialogMode.value = 'edit'
  Object.assign(connectionForm, conn)
  connectionDialogVisible.value = true
}

const testConnection = () => {
  testing.value = true
  setTimeout(() => {
    testing.value = false
    testResult.success = true
    testResult.message = 'Successfully connected to OPC-UA server'
    testResult.details = { serverName: 'OPC-UA Simulation Server', version: '1.04', responseTime: 45, nodeCount: 1250 }
    testDialogVisible.value = true
  }, 1500)
}

const saveConnection = async () => {
  if (!connectionFormRef.value) return
  await connectionFormRef.value.validate((valid: boolean) => {
    if (valid) {
      ElMessage.success(dialogMode.value === 'add' ? 'Connection added successfully' : 'Connection updated successfully')
      connectionDialogVisible.value = false
    }
  })
}

const deleteConnection = (conn: any) => {
  ElMessageBox.confirm(`Delete connection "${conn.name}"? This will also remove all subscriptions.`, 'Confirm Delete', {
    confirmButtonText: 'Delete', cancelButtonText: 'Cancel', type: 'warning'
  }).then(() => {
    const index = connections.value.findIndex(c => c.id === conn.id)
    if (index !== -1) { connections.value.splice(index, 1); if (selectedConnection.value?.id === conn.id) { selectedConnection.value = null; selectedNode.value = null } ElMessage.success(`Deleted: ${conn.name}`) }
  }).catch(() => {})
}

const testConn = (conn: any) => {
  ElMessage.info(`Testing connection to ${conn.name}...`)
  setTimeout(() => { ElMessage.success(`Connection to ${conn.name} is ${conn.status}`) }, 1000)
}

const browseNodes = (conn: any) => {
  selectedConnection.value = conn
  selectedNode.value = null
  showSubscriptions.value = false
}

const viewSubscriptions = (conn: any) => {
  selectedConnection.value = conn
  showSubscriptions.value = true
  refreshSubscriptions()
}

const refreshSubscriptions = () => {
  subscriptionsLoading.value = true
  setTimeout(() => { subscriptionsLoading.value = false; ElMessage.success('Subscriptions refreshed') }, 500)
}

const refreshNodes = () => { ElMessage.success('Node tree refreshed') }

// ==================== Node Browser Methods ====================
const handleNodeClick = (data: any) => {
  selectedNode.value = data
}

const readNodeValue = (node: any) => {
  ElMessage.info(`Reading value from ${node.displayName}...`)
  setTimeout(() => { ElMessage.success(`${node.displayName} = ${node.value} ${node.unit || ''}`) }, 500)
}

const writeNodeValue = (node: any) => {
  writeNode.value = node
  writeValue.value = node.value?.toString() || ''
  writeDialogVisible.value = true
}

const submitWrite = () => {
  ElMessage.success(`Wrote value ${writeValue.value} to ${writeNode.value?.displayName}`)
  writeDialogVisible.value = false
  if (selectedNode.value) selectedNode.value.value = writeValue.value
}

const subscribeToNode = (node: any) => {
  subscriptionForm.nodeId = node.nodeId
  subscriptionForm.displayName = node.displayName
  subscriptionForm.unit = node.unit || ''
  subscriptionDialogVisible.value = true
}

// ==================== Subscription Methods ====================
const openAddSubscriptionDialog = () => {
  Object.assign(subscriptionForm, { nodeId: '', displayName: '', samplingInterval: 1000, queueSize: 100, deadband: 0, unit: '', description: '' })
  subscriptionDialogVisible.value = true
}

const editSubscription = (sub: any) => {
  Object.assign(subscriptionForm, sub)
  subscriptionDialogVisible.value = true
  dialogMode.value = 'edit'
}

const saveSubscription = async () => {
  if (!subscriptionFormRef.value) return
  await subscriptionFormRef.value.validate((valid: boolean) => {
    if (valid) {
      ElMessage.success(dialogMode.value === 'add' ? 'Subscription added successfully' : 'Subscription updated successfully')
      subscriptionDialogVisible.value = false
      refreshSubscriptions()
    }
  })
}

const deleteSubscription = (sub: any) => {
  ElMessageBox.confirm(`Unsubscribe from "${sub.displayName}"?`, 'Confirm', {
    confirmButtonText: 'Unsubscribe', cancelButtonText: 'Cancel', type: 'warning'
  }).then(() => {
    const index = subscriptions.value.findIndex(s => s.id === sub.id)
    if (index !== -1) subscriptions.value.splice(index, 1)
    ElMessage.success(`Unsubscribed from ${sub.displayName}`)
  }).catch(() => {})
}

const handleCertUpload = (file: any) => { connectionForm.certificate = file.name }
const handleKeyUpload = (file: any) => { connectionForm.privateKey = file.name }

const handleSizeChange = () => { currentPage.value = 1 }
const handleCurrentChange = () => {}

// ==================== Mounted ====================
onMounted(() => {
  let messageIndex = 0
  const messageInterval = setInterval(() => { if (messageIndex < loadingMessages.length - 1) messageIndex++; loadingMessage.value = loadingMessages[messageIndex] }, 400)
  const progressInterval = setInterval(() => { if (loadingProgress.value < 100) { loadingProgress.value += Math.random() * 15 + 5; if (loadingProgress.value > 100) loadingProgress.value = 100 } }, 200)
  setTimeout(() => {
    clearInterval(messageInterval); clearInterval(progressInterval); loadingProgress.value = 100; loadingMessage.value = 'Ready!'
    setTimeout(() => { isLoaded.value = true; fetchConnections() }, 400)
  }, 2000)
})
</script>

<style scoped lang="scss">
/* Loading screen styles (same as previous) */
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
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
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
@keyframes bounce { 0%,80%,100% { transform: scale(0); opacity: 0.3; } 40% { transform: scale(1); opacity: 1; } }
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
@keyframes shimmer { 0% { background-position: 0% 0%; } 100% { background-position: 200% 0%; } }
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
@keyframes pulse { 0%,100% { opacity: 0.6; } 50% { opacity: 1; } }
@keyframes fadeInUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }

/* Main page styles */
.opcua-page {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}
.page-header .breadcrumb { margin-bottom: 8px; }
.page-header h1 { font-size: 28px; font-weight: 600; color: #303133; margin: 0 0 8px 0; }
.page-header .description { color: #909399; font-size: 14px; margin: 0; }
.page-header .header-actions { display: flex; gap: 12px; }

.stats-row { margin-bottom: 20px; }
.stat-card { cursor: pointer; transition: all 0.3s; }
.stat-card:hover { transform: translateY(-4px); }
.stat-card .stat-content { display: flex; justify-content: space-between; align-items: center; }
.stat-card .stat-info { flex: 1; }
.stat-card .stat-title { font-size: 14px; color: #909399; margin-bottom: 8px; }
.stat-card .stat-value { font-size: 28px; font-weight: 600; color: #303133; margin-bottom: 8px; }
.stat-card .stat-trend { font-size: 12px; display: flex; align-items: center; gap: 4px; }
.stat-card .stat-trend.up { color: #67c23a; }
.stat-card .stat-trend.down { color: #f56c6c; }
.stat-card .stat-trend .trend-label { color: #909399; margin-left: 4px; }
.stat-card .stat-icon { width: 56px; height: 56px; border-radius: 12px; display: flex; align-items: center; justify-content: center; }
.stat-card .stat-footer { margin-top: 12px; padding-top: 8px; border-top: 1px solid #ebeef5; font-size: 12px; color: #909399; }

.status-row { margin-bottom: 20px; }
.connection-card .card-header, .metrics-card .card-header { display: flex; justify-content: space-between; align-items: center; font-weight: 600; }
.connection-stats { display: flex; gap: 16px; justify-content: space-around; }
.connection-stats .stat-badge { text-align: center; padding: 16px; border-radius: 12px; background: #f5f7fa; flex: 1; }
.connection-stats .stat-badge.online .stat-number { color: #67c23a; }
.connection-stats .stat-badge.offline .stat-number { color: #f56c6c; }
.connection-stats .stat-badge.warning .stat-number { color: #e6a23c; }
.connection-stats .stat-badge.total .stat-number { color: #409eff; }
.connection-stats .stat-number { font-size: 32px; font-weight: 600; }
.connection-stats .stat-label { font-size: 12px; color: #909399; margin-top: 4px; }

.metrics-list .metric-item { display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-bottom: 1px solid #ebeef5; }
.metrics-list .metric-item:last-child { border-bottom: none; }
.metrics-list .metric-label { font-size: 13px; color: #606266; }
.metrics-list .metric-value { font-size: 16px; font-weight: 600; color: #303133; }
.metrics-list .metric-trend { font-size: 12px; padding: 2px 6px; border-radius: 4px; }
.metrics-list .metric-trend.up { color: #67c23a; background: rgba(103,194,58,0.1); }
.metrics-list .metric-trend.down { color: #f56c6c; background: rgba(245,108,108,0.1); }

.connections-card, .browser-card, .subscriptions-card { margin-bottom: 20px; }
.connections-card .card-header, .browser-card .card-header, .subscriptions-card .card-header { display: flex; justify-content: space-between; align-items: center; font-weight: 600; }
.connections-card .table-actions, .browser-card .browser-actions, .subscriptions-card .subscription-actions { display: flex; gap: 12px; align-items: center; }
.pagination-container { margin-top: 20px; display: flex; justify-content: flex-end; }

.node-tree { height: 500px; overflow-y: auto; border: 1px solid #ebeef5; border-radius: 8px; padding: 8px; }
.tree-node { display: flex; align-items: center; gap: 8px; }
.tree-node .node-tag { margin-left: auto; }
.node-details { padding: 16px; background: #f5f7fa; border-radius: 8px; }
.node-actions { margin-top: 16px; display: flex; gap: 8px; }
.node-value { font-size: 18px; font-weight: 600; color: #409eff; }
.node-empty { padding: 40px; text-align: center; }
.subscription-value { font-weight: 500; color: #67c23a; }
.status-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 6px; }
.status-dot.online { background-color: #67c23a; box-shadow: 0 0 4px #67c23a; }
.status-dot.offline { background-color: #909399; }

.connection-dialog :deep(.el-dialog__body) { max-height: 60vh; overflow-y: auto; }
.test-details { margin-top: 16px; padding: 16px; background: #f5f7fa; border-radius: 8px; }
.test-details p { margin: 8px 0; }
.write-node-id, .write-current-value { font-family: monospace; font-size: 13px; }

:deep(.el-table) { font-size: 13px; }
:deep(.el-dialog__body) { max-height: 60vh; overflow-y: auto; }
:deep(.el-tabs__header) { margin-bottom: 0; }
</style>