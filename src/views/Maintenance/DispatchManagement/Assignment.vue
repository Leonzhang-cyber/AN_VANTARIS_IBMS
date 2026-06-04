<template>
  <!-- Loading Screen -->
  <div v-if="!isLoaded" class="loading-container">
    <div class="loading-overlay">
      <div class="loading-content">
        <div class="loading-spinner">
          <div class="spinner-ring"></div>
          <div class="spinner-ring"></div>
          <div class="spinner-ring"></div>
          <div class="spinner-ring"></div>
        </div>
        <div class="loading-text">
          <span class="loading-title">Assignment</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Dispatch Management System</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="ibms-dispatch-system">
    <!-- Header -->
    <div class="system-header">
      <div class="header-left">
        <h1 class="system-title">
          <el-icon><Setting /></el-icon>
          Assignment
        </h1>
        <div class="stats-row">
          <div class="stat-chip"><el-icon><Document /></el-icon> {{ allWorkOrders.length }} Total Orders</div>
          <div class="stat-chip"><el-icon><User /></el-icon> {{ technicians.length }} Technicians</div>
          <div class="stat-chip success"><el-icon><CircleCheck /></el-icon> {{ completedOrdersCount }} Completed</div>
          <div class="stat-chip warning"><el-icon><Clock /></el-icon> {{ pendingOrders.length }} Pending</div>
          <div class="stat-chip primary"><el-icon><MagicStick /></el-icon> Auto Dispatch Active</div>
        </div>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="triggerAutoDispatch" :loading="autoDispatching">
          <el-icon><MagicStick /></el-icon> Re-Dispatch
        </el-button>
        <el-button @click="resetSystem"><el-icon><Refresh /></el-icon> Reset</el-button>
      </div>
    </div>

    <!-- Main Layout -->
    <div class="main-layout">
      <!-- Left: Work Orders -->
      <div class="panel orders-panel">
        <div class="panel-header">
          <span class="panel-title"><el-icon><List /></el-icon> Work Orders</span>
          <el-input v-model="orderSearch" placeholder="Search orders..." size="small" style="width: 160px" clearable />
        </div>
        <div class="panel-content orders-container">
          <div
              v-for="order in filteredOrders"
              :key="order.id"
              class="order-item"
              :class="[`priority-${order.priority}`, { selected: selectedOrder?.id === order.id }]"
              @click="selectOrder(order)"
          >
            <div class="order-badge" :class="order.priority">{{ order.priority.toUpperCase() }}</div>
            <div class="order-info">
              <div class="order-title">{{ order.title }}</div>
              <div class="order-meta">
                <span><el-icon><Location /></el-icon> {{ order.location }}</span>
                <span><el-icon><Clock /></el-icon> {{ order.reportedTime }}</span>
              </div>
              <div class="order-skills">
                <el-tag v-for="skill in order.skills.slice(0, 2)" :key="skill" size="small" type="info">{{ skill }}</el-tag>
                <span v-if="order.skills.length > 2" class="more-skills">+{{ order.skills.length - 2 }}</span>
              </div>
              <div v-if="order.assignedTo" class="order-assigned">
                <el-icon><User /></el-icon> {{ order.assignedTo }}
                <span class="dispatch-badge">🤖 Auto</span>
              </div>
            </div>
            <div class="order-status" :class="order.status">{{ getStatusText(order.status) }}</div>
          </div>
          <div v-if="filteredOrders.length === 0" class="empty-orders">No work orders found</div>
        </div>
      </div>

      <!-- Center: Dynamic Topology Flow -->
      <div class="panel topology-panel">
        <div class="panel-header">
          <span class="panel-title">
            <el-icon><Share /></el-icon>
            <span v-if="activeViewType === 'order' && selectedOrder">Process Topology: {{ selectedOrder.title }}</span>
            <span v-else-if="activeViewType === 'tech' && selectedTechnician && !selectedTaskOrder">Task Topology: {{ selectedTechnician.name }}'s Orders</span>
            <span v-else-if="activeViewType === 'task' && selectedTaskOrder">Task Detail: {{ selectedTaskOrder.title }}</span>
            <span v-else>Process Topology</span>
          </span>
          <div class="topology-legend">
            <span><span class="legend-dot completed"></span> Completed</span>
            <span><span class="legend-dot active"></span> Active</span>
            <span><span class="legend-dot pending"></span> Pending</span>
            <span v-if="activeViewType === 'tech'" class="back-btn" @click="backToTechnicianView">← Back to Orders</span>
            <span v-if="activeViewType === 'task'" class="back-btn" @click="backToTechnicianView">← Back to Technician</span>
            <span><el-icon><FullScreen /></el-icon> Drag to pan</span>
          </div>
        </div>
        <div class="topology-container">
          <VueFlow
              v-model="flowElements"
              :default-viewport="{ zoom: 0.85, x: 20, y: 20 }"
              :min-zoom="0.4"
              :max-zoom="1.8"
              :edges-updatable="false"
              :nodes-draggable="true"
              :pan-on-scroll="true"
              :zoom-on-scroll="true"
              class="flowchart"
              @node-click="onFlowNodeClick"
          >
            <template #node-custom="nodeProps">
              <div class="flow-node" :class="`node-${nodeProps.data.status}`">
                <div class="flow-node-icon">
                  <el-icon v-if="nodeProps.data.icon === 'start'"><VideoPlay /></el-icon>
                  <el-icon v-else-if="nodeProps.data.icon === 'skill'"><Search /></el-icon>
                  <el-icon v-else-if="nodeProps.data.icon === 'dispatch'"><Share /></el-icon>
                  <el-icon v-else-if="nodeProps.data.icon === 'assign'"><Connection /></el-icon>
                  <el-icon v-else-if="nodeProps.data.icon === 'exec'"><Monitor /></el-icon>
                  <el-icon v-else-if="nodeProps.data.icon === 'order'"><Document /></el-icon>
                  <el-icon v-else-if="nodeProps.data.icon === 'tech'"><User /></el-icon>
                  <el-icon v-else><Setting /></el-icon>
                </div>
                <div class="flow-node-content">
                  <div class="flow-node-title">{{ nodeProps.data.label }}</div>
                  <div class="flow-node-status">{{ getFlowStatusText(nodeProps.data.status) }}</div>
                  <div v-if="nodeProps.data.detail" class="flow-node-detail">{{ nodeProps.data.detail }}</div>
                  <div v-if="nodeProps.data.subDetail" class="flow-node-subdetail">{{ nodeProps.data.subDetail }}</div>
                </div>
                <div v-if="nodeProps.data.status === 'active'" class="flow-node-pulse"></div>
                <div v-if="nodeProps.data.progress !== undefined" class="flow-node-progress">
                  <el-progress :percentage="nodeProps.data.progress" :stroke-width="3" :show-text="false" />
                </div>
                <div v-if="nodeProps.data.clickable" class="flow-node-click-hint">
                  <el-icon><Pointer /></el-icon>
                </div>
              </div>
            </template>
          </VueFlow>
        </div>
        <div class="topology-footer">
          <div class="info-banner" :class="{ 'order-info': activeViewType === 'order', 'tech-info': activeViewType === 'tech', 'task-info': activeViewType === 'task' }">
            <el-icon><InfoFilled /></el-icon>
            <span v-if="activeViewType === 'order' && selectedOrder">
              📋 {{ selectedOrder.title }} | Priority: {{ selectedOrder.priority.toUpperCase() }} |
              Status: {{ getStatusText(selectedOrder.status) }} | Stage: {{ getCurrentStageText(selectedOrder) }}
            </span>
            <span v-else-if="activeViewType === 'tech' && selectedTechnician && !selectedTaskOrder">
              👤 {{ selectedTechnician.name }} | {{ getTechnicianOrderCount(selectedTechnician.id) }} active orders |
              Load: {{ selectedTechnician.currentLoad }}% | Efficiency: {{ selectedTechnician.efficiency }}%
              <span class="hint-text">💡 Click on any order node to see its process flow</span>
            </span>
            <span v-else-if="activeViewType === 'task' && selectedTaskOrder">
              🔄 {{ selectedTaskOrder.title }} | Priority: {{ selectedTaskOrder.priority.toUpperCase() }} |
              Progress: {{ selectedTaskOrder.progress }}% | Stage: {{ getCurrentStageText(selectedTaskOrder) }}
            </span>
            <span v-else>Click on a technician to see their orders, then click an order for details</span>
          </div>
        </div>
      </div>

      <!-- Right: Technicians -->
      <div class="panel tech-panel">
        <div class="panel-header">
          <span class="panel-title"><el-icon><UserFilled /></el-icon> Technicians</span>
          <el-select v-model="skillFilter" placeholder="Filter skill" size="small" clearable style="width: 110px">
            <el-option label="All" value="all" />
            <el-option label="Electrical" value="electrical" />
            <el-option label="HVAC" value="hvac" />
            <el-option label="UPS" value="ups" />
            <el-option label="Plumbing" value="plumbing" />
            <el-option label="Network" value="network" />
          </el-select>
        </div>
        <div class="panel-content tech-container">
          <div
              v-for="tech in filteredTechs"
              :key="tech.id"
              class="tech-card"
              :class="{ selected: selectedTechnician?.id === tech.id }"
              @click="selectTechnician(tech)"
          >
            <div class="tech-avatar" :class="tech.status">
              <span>{{ tech.name.charAt(0) }}</span>
              <span class="tech-status-dot" :class="tech.status"></span>
            </div>
            <div class="tech-detail">
              <div class="tech-name">{{ tech.name }}</div>
              <div class="tech-skills">
                <el-tag v-for="s in tech.skills.slice(0, 2)" :key="s" size="small">{{ s }}</el-tag>
                <span v-if="tech.skills.length > 2" class="more">+{{ tech.skills.length - 2 }}</span>
              </div>
              <div class="tech-load">
                <span>Load: {{ tech.currentLoad }}%</span>
                <el-progress :percentage="tech.currentLoad" :stroke-width="4" :show-text="false" :color="getLoadColor(tech.currentLoad)" />
              </div>
              <div class="tech-orders">
                <el-icon><Document /></el-icon> {{ getTechnicianOrderCount(tech.id) }} active orders
              </div>
            </div>
            <div class="tech-efficiency">
              <span class="efficiency-badge" :class="getEfficiencyClass(tech.efficiency)">{{ tech.efficiency }}%</span>
            </div>
          </div>
          <div v-if="filteredTechs.length === 0" class="empty-techs">No technicians found</div>
        </div>

        <!-- Assignment Rules -->
        <div class="rules-card">
          <div class="rules-header"><span><el-icon><Setting /></el-icon> Dispatch Rules</span></div>
          <div class="rules-list">
            <div class="rule"><span>🎯 Skill Match</span><el-switch v-model="rules.skillMatch" /></div>
            <div class="rule"><span>⚖️ Load Balancing</span><el-switch v-model="rules.loadBalance" /></div>
            <div class="rule"><span>⭐ Priority First</span><el-switch v-model="rules.priorityFirst" /></div>
          </div>
        </div>

        <!-- Dispatch Log -->
        <div class="log-card">
          <div class="log-header"><span><el-icon><Document /></el-icon> Dispatch Log</span><el-button text @click="clearLogs">Clear</el-button></div>
          <div class="log-container">
            <div v-for="(log, idx) in dispatchLogs" :key="idx" class="log-item" :class="log.type">
              <span class="log-time">{{ log.time }}</span>
              <span class="log-msg">{{ log.message }}</span>
            </div>
            <div v-if="dispatchLogs.length === 0" class="log-empty">No dispatch records</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Assignment Dialog -->
    <el-dialog v-model="assignDialogVisible" title="Manual Assignment" width="500px">
      <div class="dialog-content">
        <p><strong>Order:</strong> {{ selectedOrder?.title }}</p>
        <p><strong>Required Skills:</strong> {{ selectedOrder?.skills.join(', ') }}</p>
        <el-divider />
        <el-radio-group v-model="selectedTechForAssign">
          <div v-for="tech in availableTechs" :key="tech.id" class="assign-option">
            <el-radio :label="tech.id">{{ tech.name }} (Load: {{ tech.currentLoad }}% | Orders: {{ getTechnicianOrderCount(tech.id) }})</el-radio>
          </div>
        </el-radio-group>
      </div>
      <template #footer>
        <el-button @click="assignDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="confirmAssignment">Assign</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { VueFlow } from '@vue-flow/core'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Setting, Document, User, MagicStick, Refresh, List, Location, Clock,
  Share, VideoPlay, Search, Connection, Monitor, UserFilled, InfoFilled,
  CircleCheck, FullScreen, Pointer
} from '@element-plus/icons-vue'
import '@vue-flow/core/dist/style.css'
import '@vue-flow/core/dist/theme-default.css'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading work orders...',
  'Loading technicians...',
  'Initializing topology...',
  'Almost ready...'
]

// ==================== Types ====================
interface WorkOrder {
  id: number
  title: string
  priority: 'critical' | 'high' | 'medium' | 'low'
  location: string
  skills: string[]
  reportedTime: string
  status: 'pending' | 'assigned' | 'in-progress' | 'completed'
  assignedTo: string | null
  assignedTechId: number | null
  progress: number
  stage: number
  estimatedHours: number
  actualHours?: number
}

interface Technician {
  id: number
  name: string
  skills: string[]
  status: 'online' | 'busy'
  currentLoad: number
  location: string
  efficiency: number
  totalAssigned: number
  completedOrders: number
}

interface FlowNode {
  id: string
  type: string
  position: { x: number; y: number }
  data: {
    label: string
    status: 'pending' | 'active' | 'completed'
    icon?: string
    detail?: string
    subDetail?: string
    progress?: number
    orderId?: number
    techId?: number
    clickable?: boolean
    isTaskNode?: boolean
  }
}

interface FlowEdge {
  id: string
  source: string
  target: string
  animated: boolean
  style?: any
}

// ==================== Active View State ====================
type ActiveViewType = 'order' | 'tech' | 'task' | null
const activeViewType = ref<ActiveViewType>(null)
const selectedTaskOrder = ref<WorkOrder | null>(null)

// ==================== Simulation Data (All Auto-Dispatched) ====================
const workOrders = ref<WorkOrder[]>([
  { id: 1, title: 'UPS-01 Battery Replacement', priority: 'critical', location: 'Server Room A', skills: ['electrical', 'ups'], reportedTime: '08:23', status: 'in-progress', assignedTo: 'John Chen', assignedTechId: 1, progress: 65, stage: 4, estimatedHours: 2.5 },
  { id: 2, title: 'CRAC-01 Compressor Failure', priority: 'critical', location: 'Data Center', skills: ['hvac', 'crac'], reportedTime: '09:45', status: 'assigned', assignedTo: 'Sarah Wong', assignedTechId: 2, progress: 20, stage: 3, estimatedHours: 4 },
  { id: 3, title: 'PDU-A01 Firmware Update', priority: 'medium', location: 'Server Row A', skills: ['electrical'], reportedTime: '10:30', status: 'completed', assignedTo: 'John Chen', assignedTechId: 1, progress: 100, stage: 5, estimatedHours: 1.5 },
  { id: 4, title: 'Chiller-01 Water Leak', priority: 'high', location: 'Chiller Plant', skills: ['hvac', 'plumbing'], reportedTime: '11:15', status: 'in-progress', assignedTo: 'Sarah Wong', assignedTechId: 2, progress: 80, stage: 4, estimatedHours: 3 },
  { id: 5, title: 'Network Switch Configuration', priority: 'medium', location: 'Network Room', skills: ['network'], reportedTime: '13:00', status: 'assigned', assignedTo: 'Lisa Ng', assignedTechId: 5, progress: 45, stage: 4, estimatedHours: 1 },
  { id: 6, title: 'Generator Fuel Test', priority: 'low', location: 'Generator Room', skills: ['electrical', 'mechanical'], reportedTime: '14:30', status: 'assigned', assignedTo: 'Mike Lim', assignedTechId: 3, progress: 35, stage: 3, estimatedHours: 2 },
  { id: 7, title: 'UPS-02 Battery Test', priority: 'high', location: 'Server Room B', skills: ['electrical', 'ups'], reportedTime: '15:00', status: 'assigned', assignedTo: 'Kevin Lim', assignedTechId: 6, progress: 25, stage: 3, estimatedHours: 1.5 },
  { id: 8, title: 'HVAC Filter Replacement', priority: 'low', location: 'Data Center', skills: ['hvac'], reportedTime: '15:30', status: 'assigned', assignedTo: 'Ahmad Razak', assignedTechId: 7, progress: 15, stage: 3, estimatedHours: 1 },
  { id: 9, title: 'PDU Load Balancing', priority: 'high', location: 'Server Row B', skills: ['electrical', 'pdu'], reportedTime: '16:00', status: 'in-progress', assignedTo: 'John Chen', assignedTechId: 1, progress: 55, stage: 4, estimatedHours: 2 },
  { id: 10, title: 'CRAC-02 Temperature Calibration', priority: 'medium', location: 'Data Center', skills: ['hvac', 'crac'], reportedTime: '16:30', status: 'assigned', assignedTo: 'Sarah Wong', assignedTechId: 2, progress: 10, stage: 2, estimatedHours: 1.5 },
  { id: 11, title: 'Emergency Generator Test', priority: 'critical', location: 'Generator Room', skills: ['electrical', 'mechanical'], reportedTime: '17:00', status: 'assigned', assignedTo: 'Mike Lim', assignedTechId: 3, progress: 5, stage: 2, estimatedHours: 3 },
  { id: 12, title: 'BMS Server Maintenance', priority: 'high', location: 'Control Room', skills: ['network', 'electrical'], reportedTime: '17:30', status: 'assigned', assignedTo: 'Lisa Ng', assignedTechId: 5, progress: 30, stage: 3, estimatedHours: 2.5 },
  { id: 13, title: 'Cooling Tower Fan Repair', priority: 'high', location: 'Roof', skills: ['hvac', 'mechanical'], reportedTime: '18:00', status: 'in-progress', assignedTo: 'Ahmad Razak', assignedTechId: 7, progress: 50, stage: 4, estimatedHours: 5 },
  { id: 14, title: 'Fire Alarm System Test', priority: 'medium', location: 'All Floors', skills: ['electrical', 'security'], reportedTime: '18:30', status: 'assigned', assignedTo: 'David Tan', assignedTechId: 4, progress: 20, stage: 3, estimatedHours: 2 },
  { id: 15, title: 'UPS-03 Capacitor Replacement', priority: 'critical', location: 'Server Room C', skills: ['electrical', 'ups'], reportedTime: '19:00', status: 'assigned', assignedTo: 'Kevin Lim', assignedTechId: 6, progress: 8, stage: 2, estimatedHours: 3.5 }
])

const technicians = ref<Technician[]>([
  { id: 1, name: 'John Chen', skills: ['electrical', 'ups', 'pdu'], status: 'busy', currentLoad: 78, location: 'Server Room A', efficiency: 96, totalAssigned: 48, completedOrders: 46 },
  { id: 2, name: 'Sarah Wong', skills: ['hvac', 'crac', 'plumbing'], status: 'busy', currentLoad: 72, location: 'Data Center', efficiency: 98, totalAssigned: 42, completedOrders: 41 },
  { id: 3, name: 'Mike Lim', skills: ['electrical', 'mechanical', 'generator'], status: 'busy', currentLoad: 85, location: 'Generator Room', efficiency: 92, totalAssigned: 55, completedOrders: 50 },
  { id: 4, name: 'David Tan', skills: ['hvac', 'plumbing'], status: 'online', currentLoad: 45, location: 'Chiller Plant', efficiency: 94, totalAssigned: 32, completedOrders: 30 },
  { id: 5, name: 'Lisa Ng', skills: ['network', 'security'], status: 'busy', currentLoad: 68, location: 'Network Room', efficiency: 100, totalAssigned: 30, completedOrders: 30 },
  { id: 6, name: 'Kevin Lim', skills: ['electrical', 'ups', 'pdu'], status: 'busy', currentLoad: 75, location: 'Server Room B', efficiency: 95, totalAssigned: 38, completedOrders: 36 },
  { id: 7, name: 'Ahmad Razak', skills: ['hvac', 'mechanical'], status: 'busy', currentLoad: 65, location: 'Data Center', efficiency: 93, totalAssigned: 32, completedOrders: 29 },
  { id: 8, name: 'Tan Wei Ming', skills: ['electrical', 'generator'], status: 'online', currentLoad: 50, location: 'Generator Room', efficiency: 91, totalAssigned: 44, completedOrders: 40 }
])

// ==================== Base Flow Nodes (Order Process) ====================
const getOrderFlowNodes = (): FlowNode[] => [
  { id: 'stage1', type: 'custom', position: { x: 250, y: 20 }, data: { label: '1. Order Created', status: 'pending', icon: 'start' } },
  { id: 'stage2', type: 'custom', position: { x: 250, y: 130 }, data: { label: '2. Skill Matching', status: 'pending', icon: 'skill' } },
  { id: 'stage3', type: 'custom', position: { x: 250, y: 240 }, data: { label: '3. Dispatch Decision', status: 'pending', icon: 'dispatch' } },
  { id: 'stage4', type: 'custom', position: { x: 250, y: 350 }, data: { label: '4. Assignment', status: 'pending', icon: 'assign' } },
  { id: 'stage5', type: 'custom', position: { x: 250, y: 460 }, data: { label: '5. Execution & Tracking', status: 'pending', icon: 'exec' } }
]

const getOrderFlowEdges = (): FlowEdge[] => [
  { id: 'e1-2', source: 'stage1', target: 'stage2', animated: false, style: { stroke: '#94a3b8', strokeWidth: 2 } },
  { id: 'e2-3', source: 'stage2', target: 'stage3', animated: false, style: { stroke: '#94a3b8', strokeWidth: 2 } },
  { id: 'e3-4', source: 'stage3', target: 'stage4', animated: false, style: { stroke: '#94a3b8', strokeWidth: 2 } },
  { id: 'e4-5', source: 'stage4', target: 'stage5', animated: false, style: { stroke: '#94a3b8', strokeWidth: 2 } }
]

// ==================== Technician Task Flow Nodes ====================
const getTechFlowNodes = (tech: Technician, orders: WorkOrder[]): FlowNode[] => {
  const startY = 140
  const spacing = 110

  const nodes: FlowNode[] = [
    {
      id: 'tech-center',
      type: 'custom',
      position: { x: 250, y: 20 },
      data: {
        label: tech.name,
        status: 'active',
        icon: 'tech',
        detail: `${tech.efficiency}% efficiency`,
        subDetail: `Load: ${tech.currentLoad}%`,
        clickable: false
      }
    }
  ]

  const orderNodes = orders.map((order, idx) => ({
    id: `order-${order.id}`,
    type: 'custom',
    position: { x: 250, y: startY + idx * spacing },
    data: {
      label: order.title.length > 28 ? order.title.substring(0, 25) + '...' : order.title,
      status: order.status === 'completed' ? 'completed' : (order.status === 'in-progress' ? 'active' : 'pending'),
      icon: 'order',
      detail: `Priority: ${order.priority.toUpperCase()} | Progress: ${order.progress}%`,
      subDetail: `Location: ${order.location} | Est: ${order.estimatedHours}h`,
      progress: order.progress,
      orderId: order.id,
      techId: tech.id,
      clickable: true,
      isTaskNode: true
    }
  }))

  return [...nodes, ...orderNodes]
}

const getTechFlowEdges = (orders: WorkOrder[]): FlowEdge[] => {
  const edges: FlowEdge[] = []
  orders.forEach((order) => {
    edges.push({
      id: `e-tech-order-${order.id}`,
      source: 'tech-center',
      target: `order-${order.id}`,
      animated: order.status === 'in-progress',
      style: { stroke: order.status === 'completed' ? '#10b981' : (order.status === 'in-progress' ? '#f59e0b' : '#94a3b8'), strokeWidth: 2 }
    })
  })
  return edges
}

// ==================== Single Task Flow Nodes ====================
const getTaskFlowNodes = (order: WorkOrder): FlowNode[] => {
  const baseNodes = getOrderFlowNodes()

  let activeStage = order.stage
  if (order.status === 'pending') activeStage = 0
  else if (order.status === 'assigned') activeStage = 3
  else if (order.status === 'in-progress') activeStage = 4
  else if (order.status === 'completed') activeStage = 5

  const updatedNodes = baseNodes.map((node, idx) => {
    const nodeId = idx + 1
    let status: 'pending' | 'active' | 'completed' = 'pending'

    if (nodeId < activeStage) status = 'completed'
    else if (nodeId === activeStage) status = 'active'
    else status = 'pending'

    let detail = ''
    let subDetail = ''
    if (nodeId === 2) detail = `Skills: ${order.skills.join(', ')}`
    if (nodeId === 3) detail = `Priority: ${order.priority.toUpperCase()}`
    if (nodeId === 4 && order.assignedTo) detail = `Assigned to: ${order.assignedTo} 🤖 Auto`
    if (nodeId === 5 && order.progress > 0) {
      detail = `${order.progress}% complete`
      subDetail = `Est. ${order.estimatedHours}h`
    }

    return {
      ...node,
      data: {
        ...node.data,
        status,
        detail: detail || undefined,
        subDetail: subDetail || undefined,
        progress: nodeId === 5 ? order.progress : undefined,
        orderId: order.id,
        clickable: false
      }
    }
  })

  return updatedNodes
}

const getTaskFlowEdges = (order: WorkOrder): FlowEdge[] => {
  const baseEdges = getOrderFlowEdges()

  let activeStage = order.stage
  if (order.status === 'pending') activeStage = 0
  else if (order.status === 'assigned') activeStage = 3
  else if (order.status === 'in-progress') activeStage = 4
  else if (order.status === 'completed') activeStage = 5

  return baseEdges.map((edge, idx) => {
    const isCompleted = idx + 1 < activeStage
    return {
      ...edge,
      animated: isCompleted || (idx + 1 === activeStage - 1 && activeStage <= 5),
      style: { stroke: isCompleted ? '#10b981' : (idx + 1 === activeStage - 1 ? '#f59e0b' : '#94a3b8'), strokeWidth: 2 }
    }
  })
}

// ==================== State ====================
const orderSearch = ref('')
const skillFilter = ref('all')
const selectedOrder = ref<WorkOrder | null>(null)
const selectedTechnician = ref<Technician | null>(null)
const assignDialogVisible = ref(false)
const selectedTechForAssign = ref<number | null>(null)
const autoDispatching = ref(false)
const flowElements = ref<(FlowNode | FlowEdge)[]>([...getOrderFlowNodes(), ...getOrderFlowEdges()])

const rules = ref({ skillMatch: true, loadBalance: true, priorityFirst: true })
const dispatchLogs = ref<Array<{ time: string; message: string; type: string }>>([])

// ==================== Computed ====================
const allWorkOrders = computed(() => workOrders.value)
const pendingOrders = computed(() => workOrders.value.filter(o => o.status === 'pending'))
const completedOrdersCount = computed(() => workOrders.value.filter(o => o.status === 'completed').length)

const filteredOrders = computed(() => {
  let filtered = workOrders.value
  if (orderSearch.value) {
    filtered = filtered.filter(o => o.title.toLowerCase().includes(orderSearch.value.toLowerCase()))
  }
  return filtered
})

const filteredTechs = computed(() => {
  if (skillFilter.value === 'all') return technicians.value
  return technicians.value.filter(t => t.skills.includes(skillFilter.value))
})

const availableTechs = computed(() => technicians.value)

// ==================== Helper Functions ====================
const getStatusText = (status: string) => {
  const map: Record<string, string> = { pending: 'Pending', assigned: 'Assigned', 'in-progress': 'In Progress', completed: 'Completed' }
  return map[status] || status
}

const getFlowStatusText = (status: string) => {
  const map: Record<string, string> = { pending: 'Pending', active: 'Active', completed: 'Completed' }
  return map[status] || status
}

const getTechnicianOrderCount = (techId: number) => {
  return workOrders.value.filter(o => o.assignedTechId === techId && o.status !== 'completed').length
}

const getLoadColor = (load: number) => {
  if (load < 50) return '#67c23a'
  if (load < 75) return '#e6a23c'
  return '#f56c6c'
}

const getEfficiencyClass = (efficiency: number) => {
  if (efficiency >= 95) return 'high'
  if (efficiency >= 85) return 'medium'
  return 'low'
}

const getCurrentStageText = (order: WorkOrder) => {
  const stages = ['Created', 'Skill Matching', 'Dispatch Decision', 'Assignment', 'Execution']
  return stages[order.stage] || stages[0]
}

const addLog = (message: string, type: string = 'info') => {
  const now = new Date().toLocaleTimeString()
  dispatchLogs.value.unshift({ time: now, message, type })
  if (dispatchLogs.value.length > 40) dispatchLogs.value.pop()
}

// ==================== Update Flow Topology ====================
const updateFlowForOrder = (order: WorkOrder | null) => {
  if (!order) {
    flowElements.value = [...getOrderFlowNodes(), ...getOrderFlowEdges()]
    activeViewType.value = null
    selectedTaskOrder.value = null
    return
  }

  activeViewType.value = 'order'
  selectedTaskOrder.value = null
  const updatedNodes = getTaskFlowNodes(order)
  const updatedEdges = getTaskFlowEdges(order)

  flowElements.value = [...updatedNodes, ...updatedEdges]
}

const updateFlowForTechnician = (tech: Technician | null) => {
  if (!tech) {
    if (selectedOrder.value) updateFlowForOrder(selectedOrder.value)
    else flowElements.value = [...getOrderFlowNodes(), ...getOrderFlowEdges()]
    activeViewType.value = selectedOrder.value ? 'order' : null
    selectedTaskOrder.value = null
    return
  }

  activeViewType.value = 'tech'
  selectedTaskOrder.value = null
  const techOrders = workOrders.value.filter(o => o.assignedTechId === tech.id)

  const nodes = getTechFlowNodes(tech, techOrders)
  const edges = getTechFlowEdges(techOrders)

  flowElements.value = [...nodes, ...edges]
}

const updateFlowForTask = (order: WorkOrder, tech: Technician) => {
  activeViewType.value = 'task'
  selectedTaskOrder.value = order

  const techNode: FlowNode = {
    id: 'tech-center',
    type: 'custom',
    position: { x: 250, y: 20 },
    data: {
      label: tech.name,
      status: 'active',
      icon: 'tech',
      detail: `${tech.efficiency}% efficiency`,
      subDetail: `Load: ${tech.currentLoad}%`,
      clickable: false
    }
  }

  const taskFlowNodes = getTaskFlowNodes(order)
  const shiftedTaskNodes = taskFlowNodes.map(node => ({
    ...node,
    position: { x: node.position.x, y: node.position.y + 100 }
  }))

  const taskEdges = getTaskFlowEdges(order)

  const connectionEdge: FlowEdge = {
    id: 'e-tech-to-task',
    source: 'tech-center',
    target: 'stage1',
    animated: true,
    style: { stroke: '#8b5cf6', strokeWidth: 2, strokeDasharray: '5,5' }
  }

  flowElements.value = [techNode, ...shiftedTaskNodes, ...taskEdges, connectionEdge]
}

// ==================== Selection Handlers ====================
const selectOrder = (order: WorkOrder) => {
  selectedOrder.value = order
  selectedTechnician.value = null
  selectedTaskOrder.value = null
  updateFlowForOrder(order)
  addLog(`📋 Selected order: ${order.title} (Stage: ${getCurrentStageText(order)})`, 'info')
}

const selectTechnician = (tech: Technician) => {
  selectedTechnician.value = tech
  selectedOrder.value = null
  selectedTaskOrder.value = null
  updateFlowForTechnician(tech)
  addLog(`👤 Selected technician: ${tech.name} - ${getTechnicianOrderCount(tech.id)} active orders`, 'info')
}

const onFlowNodeClick = (event: any) => {
  const node = event.node || event
  if (node?.data) {
    if (node.data.clickable && node.data.isTaskNode && node.data.orderId && selectedTechnician.value) {
      const order = workOrders.value.find(o => o.id === node.data.orderId)
      if (order && selectedTechnician.value) {
        addLog(`🔍 Drilling down into order: ${order.title}`, 'info')
        updateFlowForTask(order, selectedTechnician.value)
      }
    } else {
      addLog(`📍 Clicked on topology node: ${node.data.label} (${getFlowStatusText(node.data.status)})`, 'info')
    }
  }
}

const backToTechnicianView = () => {
  if (selectedTechnician.value) {
    updateFlowForTechnician(selectedTechnician.value)
    addLog(`← Returned to ${selectedTechnician.value.name}'s orders view`, 'info')
  }
}

// ==================== Auto Dispatch Algorithm ====================
const triggerAutoDispatch = async () => {
  if (pendingOrders.value.length === 0) {
    ElMessage.warning('No pending orders to dispatch')
    return
  }

  autoDispatching.value = true
  addLog('🤖 Re-dispatching pending orders...', 'info')

  let ordersToDispatch = [...pendingOrders.value]

  if (rules.value.priorityFirst) {
    const priorityOrder = { critical: 0, high: 1, medium: 2, low: 3 }
    ordersToDispatch.sort((a, b) => priorityOrder[a.priority] - priorityOrder[b.priority])
  }

  for (const order of ordersToDispatch) {
    await new Promise(resolve => setTimeout(resolve, 500))

    let candidates = [...technicians.value]

    if (rules.value.skillMatch) {
      candidates = candidates.filter(t => order.skills.some(s => t.skills.includes(s)))
    }

    if (candidates.length === 0) {
      addLog(`⚠️ No suitable technician for ${order.title}`, 'warning')
      continue
    }

    if (rules.value.loadBalance) {
      candidates.sort((a, b) => a.currentLoad - b.currentLoad)
    }

    const bestTech = candidates[0]
    const orderIndex = workOrders.value.findIndex(o => o.id === order.id)

    if (orderIndex !== -1) {
      workOrders.value[orderIndex].assignedTo = bestTech.name
      workOrders.value[orderIndex].assignedTechId = bestTech.id
      workOrders.value[orderIndex].status = 'assigned'
      workOrders.value[orderIndex].stage = 3
      workOrders.value[orderIndex].progress = 15

      const techIndex = technicians.value.findIndex(t => t.id === bestTech.id)
      if (techIndex !== -1) {
        technicians.value[techIndex].currentLoad = Math.min(100, technicians.value[techIndex].currentLoad + 10)
        technicians.value[techIndex].totalAssigned++
        if (technicians.value[techIndex].currentLoad > 70) technicians.value[techIndex].status = 'busy'
      }

      addLog(`🤖 Auto-dispatched ${order.title} → ${bestTech.name} (Priority: ${order.priority})`, 'success')
    }
  }

  if (selectedOrder.value) {
    const updatedOrder = workOrders.value.find(o => o.id === selectedOrder.value?.id)
    if (updatedOrder) updateFlowForOrder(updatedOrder)
  }

  if (selectedTechnician.value) {
    const updatedTech = technicians.value.find(t => t.id === selectedTechnician.value?.id)
    if (updatedTech) updateFlowForTechnician(updatedTech)
  }

  addLog(`🎉 Re-dispatch completed. ${ordersToDispatch.length} orders processed`, 'success')
  ElMessage.success(`Re-dispatched ${ordersToDispatch.length} orders`)
  autoDispatching.value = false
}

// ==================== Manual Assignment ====================
const confirmAssignment = () => {
  if (!selectedTechForAssign.value || !selectedOrder.value) {
    ElMessage.warning('Please select a technician')
    return
  }

  const tech = technicians.value.find(t => t.id === selectedTechForAssign.value)
  const order = selectedOrder.value
  const orderIndex = workOrders.value.findIndex(o => o.id === order.id)

  if (tech && orderIndex !== -1) {
    workOrders.value[orderIndex].assignedTo = tech.name
    workOrders.value[orderIndex].assignedTechId = tech.id
    workOrders.value[orderIndex].status = 'assigned'
    workOrders.value[orderIndex].stage = 3
    workOrders.value[orderIndex].progress = 15

    const techIndex = technicians.value.findIndex(t => t.id === tech.id)
    if (techIndex !== -1) {
      technicians.value[techIndex].currentLoad = Math.min(100, technicians.value[techIndex].currentLoad + 10)
      technicians.value[techIndex].totalAssigned++
    }

    addLog(`🔧 Manual override: ${order.title} → ${tech.name}`, 'success')
    ElMessage.success(`Assigned to ${tech.name}`)
    assignDialogVisible.value = false
    updateFlowForOrder(workOrders.value[orderIndex])
    selectedOrder.value = null
  }
}

// ==================== Reset System ====================
const resetSystem = () => {
  workOrders.value = [
    { id: 1, title: 'UPS-01 Battery Replacement', priority: 'critical', location: 'Server Room A', skills: ['electrical', 'ups'], reportedTime: '08:23', status: 'in-progress', assignedTo: 'John Chen', assignedTechId: 1, progress: 65, stage: 4, estimatedHours: 2.5 },
    { id: 2, title: 'CRAC-01 Compressor Failure', priority: 'critical', location: 'Data Center', skills: ['hvac', 'crac'], reportedTime: '09:45', status: 'assigned', assignedTo: 'Sarah Wong', assignedTechId: 2, progress: 20, stage: 3, estimatedHours: 4 },
    { id: 3, title: 'PDU-A01 Firmware Update', priority: 'medium', location: 'Server Row A', skills: ['electrical'], reportedTime: '10:30', status: 'completed', assignedTo: 'John Chen', assignedTechId: 1, progress: 100, stage: 5, estimatedHours: 1.5 },
    { id: 4, title: 'Chiller-01 Water Leak', priority: 'high', location: 'Chiller Plant', skills: ['hvac', 'plumbing'], reportedTime: '11:15', status: 'in-progress', assignedTo: 'Sarah Wong', assignedTechId: 2, progress: 80, stage: 4, estimatedHours: 3 },
    { id: 5, title: 'Network Switch Configuration', priority: 'medium', location: 'Network Room', skills: ['network'], reportedTime: '13:00', status: 'assigned', assignedTo: 'Lisa Ng', assignedTechId: 5, progress: 45, stage: 4, estimatedHours: 1 },
    { id: 6, title: 'Generator Fuel Test', priority: 'low', location: 'Generator Room', skills: ['electrical', 'mechanical'], reportedTime: '14:30', status: 'assigned', assignedTo: 'Mike Lim', assignedTechId: 3, progress: 35, stage: 3, estimatedHours: 2 },
    { id: 7, title: 'UPS-02 Battery Test', priority: 'high', location: 'Server Room B', skills: ['electrical', 'ups'], reportedTime: '15:00', status: 'assigned', assignedTo: 'Kevin Lim', assignedTechId: 6, progress: 25, stage: 3, estimatedHours: 1.5 },
    { id: 8, title: 'HVAC Filter Replacement', priority: 'low', location: 'Data Center', skills: ['hvac'], reportedTime: '15:30', status: 'assigned', assignedTo: 'Ahmad Razak', assignedTechId: 7, progress: 15, stage: 3, estimatedHours: 1 },
    { id: 9, title: 'PDU Load Balancing', priority: 'high', location: 'Server Row B', skills: ['electrical', 'pdu'], reportedTime: '16:00', status: 'in-progress', assignedTo: 'John Chen', assignedTechId: 1, progress: 55, stage: 4, estimatedHours: 2 },
    { id: 10, title: 'CRAC-02 Temperature Calibration', priority: 'medium', location: 'Data Center', skills: ['hvac', 'crac'], reportedTime: '16:30', status: 'assigned', assignedTo: 'Sarah Wong', assignedTechId: 2, progress: 10, stage: 2, estimatedHours: 1.5 },
    { id: 11, title: 'Emergency Generator Test', priority: 'critical', location: 'Generator Room', skills: ['electrical', 'mechanical'], reportedTime: '17:00', status: 'assigned', assignedTo: 'Mike Lim', assignedTechId: 3, progress: 5, stage: 2, estimatedHours: 3 },
    { id: 12, title: 'BMS Server Maintenance', priority: 'high', location: 'Control Room', skills: ['network', 'electrical'], reportedTime: '17:30', status: 'assigned', assignedTo: 'Lisa Ng', assignedTechId: 5, progress: 30, stage: 3, estimatedHours: 2.5 },
    { id: 13, title: 'Cooling Tower Fan Repair', priority: 'high', location: 'Roof', skills: ['hvac', 'mechanical'], reportedTime: '18:00', status: 'in-progress', assignedTo: 'Ahmad Razak', assignedTechId: 7, progress: 50, stage: 4, estimatedHours: 5 },
    { id: 14, title: 'Fire Alarm System Test', priority: 'medium', location: 'All Floors', skills: ['electrical', 'security'], reportedTime: '18:30', status: 'assigned', assignedTo: 'David Tan', assignedTechId: 4, progress: 20, stage: 3, estimatedHours: 2 },
    { id: 15, title: 'UPS-03 Capacitor Replacement', priority: 'critical', location: 'Server Room C', skills: ['electrical', 'ups'], reportedTime: '19:00', status: 'assigned', assignedTo: 'Kevin Lim', assignedTechId: 6, progress: 8, stage: 2, estimatedHours: 3.5 }
  ]

  technicians.value = [
    { id: 1, name: 'John Chen', skills: ['electrical', 'ups', 'pdu'], status: 'busy', currentLoad: 78, location: 'Server Room A', efficiency: 96, totalAssigned: 48, completedOrders: 46 },
    { id: 2, name: 'Sarah Wong', skills: ['hvac', 'crac', 'plumbing'], status: 'busy', currentLoad: 72, location: 'Data Center', efficiency: 98, totalAssigned: 42, completedOrders: 41 },
    { id: 3, name: 'Mike Lim', skills: ['electrical', 'mechanical', 'generator'], status: 'busy', currentLoad: 85, location: 'Generator Room', efficiency: 92, totalAssigned: 55, completedOrders: 50 },
    { id: 4, name: 'David Tan', skills: ['hvac', 'plumbing'], status: 'online', currentLoad: 45, location: 'Chiller Plant', efficiency: 94, totalAssigned: 32, completedOrders: 30 },
    { id: 5, name: 'Lisa Ng', skills: ['network', 'security'], status: 'busy', currentLoad: 68, location: 'Network Room', efficiency: 100, totalAssigned: 30, completedOrders: 30 },
    { id: 6, name: 'Kevin Lim', skills: ['electrical', 'ups', 'pdu'], status: 'busy', currentLoad: 75, location: 'Server Room B', efficiency: 95, totalAssigned: 38, completedOrders: 36 },
    { id: 7, name: 'Ahmad Razak', skills: ['hvac', 'mechanical'], status: 'busy', currentLoad: 65, location: 'Data Center', efficiency: 93, totalAssigned: 32, completedOrders: 29 },
    { id: 8, name: 'Tan Wei Ming', skills: ['electrical', 'generator'], status: 'online', currentLoad: 50, location: 'Generator Room', efficiency: 91, totalAssigned: 44, completedOrders: 40 }
  ]

  selectedOrder.value = null
  selectedTechnician.value = null
  selectedTaskOrder.value = null
  activeViewType.value = null
  flowElements.value = [...getOrderFlowNodes(), ...getOrderFlowEdges()]
  addLog('🔄 System reset to initial state', 'info')
  ElMessage.success('System reset')
}

const clearLogs = () => {
  dispatchLogs.value = []
  addLog('📋 Dispatch log cleared', 'info')
}

// ==================== Loading Animation ====================
const startLoading = () => {
  let progress = 0
  let messageIndex = 0

  const messageInterval = setInterval(() => {
    if (messageIndex < loadingMessages.length - 1) {
      messageIndex++
      loadingMessage.value = loadingMessages[messageIndex]
    }
  }, 600)

  const progressInterval = setInterval(() => {
    if (progress < 90) {
      progress += Math.random() * 12
      loadingProgress.value = Math.min(progress, 90)
    }
  }, 100)

  setTimeout(() => {
    clearInterval(messageInterval)
    clearInterval(progressInterval)
    loadingProgress.value = 100
    loadingMessage.value = 'Ready!'

    setTimeout(() => {
      isLoaded.value = true
      // Initialize default view after loading
      if (workOrders.value.length > 0) {
        const firstOrder = workOrders.value[0]
        selectedOrder.value = firstOrder
        updateFlowForOrder(firstOrder)
        addLog(`📋 Default view: ${firstOrder.title}`, 'info')
      }
      addLog('🚀 IBMS Dispatch System initialized', 'success')
      addLog('🤖 All work orders auto-dispatched', 'success')
      addLog('📊 15 work orders assigned, 8 technicians available', 'info')
      addLog('💡 Tip: Click technician → then click any order node to see its process flow', 'info')
    }, 500)
  }, 2200)
}

// ==================== Lifecycle ====================
onMounted(() => {
  startLoading()
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

.spinner-ring:nth-child(1) { border-top-color: #3b82f6; animation-delay: 0s; }
.spinner-ring:nth-child(2) { border-right-color: #f59e0b; animation-delay: 0.2s; width: 70%; height: 70%; top: 15%; left: 15%; }
.spinner-ring:nth-child(3) { border-bottom-color: #10b981; animation-delay: 0.4s; width: 40%; height: 40%; top: 30%; left: 30%; }
.spinner-ring:nth-child(4) { border-left-color: #ec489a; animation-delay: 0.6s; width: 20%; height: 20%; top: 40%; left: 40%; }

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

/* ==================== Main Page Styles ==================== */
* {
  scrollbar-width: none;
  -ms-overflow-style: none;
}
*::-webkit-scrollbar {
  display: none;
}

.ibms-dispatch-system {
  min-height: 100vh;
  background: #f0f2f6;
  padding: 20px;
  font-family: 'Segoe UI', system-ui, sans-serif;
}

/* Header */
.system-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  padding: 16px 24px;
  border-radius: 20px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.system-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 20px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 8px 0;
}

.stats-row {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.stat-chip {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #5b6e8c;
  background: #f1f5f9;
  padding: 4px 14px;
  border-radius: 20px;
}

.stat-chip.success { background: #e6f7e6; color: #2e7d32; }
.stat-chip.warning { background: #fef3c7; color: #d97706; }
.stat-chip.primary { background: #e8f4fd; color: #1890ff; }

.header-right { display: flex; gap: 12px; }

/* Main Layout */
.main-layout {
  display: flex;
  gap: 20px;
}

.panel {
  background: white;
  border-radius: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  max-height: 750px;
}

.panel-header {
  padding: 16px 20px;
  border-bottom: 1px solid #eef2f8;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  color: #1e293b;
  flex-wrap: wrap;
  gap: 12px;
}

.panel-title { display: flex; align-items: center; gap: 8px; font-size: 14px; }

.orders-panel { flex: 1.1; min-width: 320px; }
.topology-panel { flex: 2; min-width: 550px; }
.tech-panel { flex: 0.9; min-width: 280px; }

.panel-content {
  flex: 1;
  overflow-y: auto;
}

/* Orders */
.orders-container { padding: 12px; }

.order-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  margin-bottom: 10px;
  background: #fafcff;
  border-radius: 14px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid #eef2f8;
}

.order-item:hover { background: #f1f5f9; transform: translateX(3px); }
.order-item.selected { background: #eef2ff; border-color: #3b82f6; }
.order-item.priority-critical { border-left: 3px solid #ef4444; }
.order-item.priority-high { border-left: 3px solid #f97316; }
.order-item.priority-medium { border-left: 3px solid #eab308; }
.order-item.priority-low { border-left: 3px solid #22c55e; }

.order-badge {
  font-size: 10px;
  font-weight: 700;
  padding: 4px 8px;
  border-radius: 20px;
  min-width: 65px;
  text-align: center;
}

.order-badge.critical { background: #fee2e2; color: #dc2626; }
.order-badge.high { background: #fff3e3; color: #ea580c; }
.order-badge.medium { background: #fef9c3; color: #ca8a04; }
.order-badge.low { background: #dcfce7; color: #16a34a; }

.order-info { flex: 1; }
.order-title { font-weight: 600; font-size: 13px; color: #1e293b; margin-bottom: 4px; }
.order-meta { display: flex; gap: 12px; font-size: 10px; color: #64748b; margin-bottom: 4px; }
.order-meta span { display: inline-flex; align-items: center; gap: 4px; }
.order-skills { display: flex; gap: 4px; flex-wrap: wrap; margin-bottom: 4px; }
.more-skills { font-size: 10px; color: #64748b; margin-left: 4px; }
.order-assigned { font-size: 10px; color: #3b82f6; display: flex; align-items: center; gap: 4px; }

.order-status {
  font-size: 10px;
  padding: 4px 10px;
  border-radius: 20px;
  font-weight: 500;
}

.order-status.pending { background: #fef3c7; color: #d97706; }
.order-status.assigned { background: #dbeafe; color: #2563eb; }
.order-status.in-progress { background: #e0e7ff; color: #4f46e5; }
.order-status.completed { background: #d1fae5; color: #059669; }

.empty-orders, .empty-techs {
  text-align: center;
  padding: 40px;
  color: #94a3b8;
  font-size: 13px;
}

/* Topology */
.topology-container {
  height: 720px;
  width: 100%;
  background: #fafcff;
}

.flowchart {
  height: 100%;
  width: 100%;
}

.flow-node {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: white;
  border-radius: 16px;
  border: 2px solid #e2e8f0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
  min-width: 220px;
  max-width: 280px;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}

.flow-node:hover { transform: scale(1.02); box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1); }

.flow-node.node-completed { border-color: #10b981; background: linear-gradient(135deg, #f0fdf4, #ffffff); }
.flow-node.node-active { border-color: #f59e0b; background: linear-gradient(135deg, #fffbeb, #ffffff); animation: pulseGlow 1.5s ease-in-out infinite; }
.flow-node.node-pending { border-color: #cbd5e1; background: #f8fafc; opacity: 0.8; }

@keyframes pulseGlow {
  0%, 100% { box-shadow: 0 0 0 0 rgba(245, 158, 11, 0.3); }
  50% { box-shadow: 0 0 0 8px rgba(245, 158, 11, 0.1); }
}

.flow-node-icon {
  width: 40px;
  height: 40px;
  background: #eef2ff;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #4f46e5;
  font-size: 20px;
  flex-shrink: 0;
}

.flow-node-content { flex: 1; min-width: 0; }
.flow-node-title { font-weight: 700; font-size: 13px; color: #1e293b; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.flow-node-status { font-size: 10px; color: #64748b; margin-top: 2px; }
.flow-node-detail { font-size: 10px; color: #3b82f6; margin-top: 4px; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.flow-node-subdetail { font-size: 9px; color: #8b5cf6; margin-top: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.flow-node-progress { margin-top: 6px; }
.flow-node-pulse {
  position: absolute;
  right: -6px;
  top: -6px;
  width: 14px;
  height: 14px;
  background: #f59e0b;
  border-radius: 50%;
  animation: pulseDot 1s infinite;
  border: 2px solid white;
}

@keyframes pulseDot {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.6); opacity: 0.5; }
}

.topology-footer { padding: 12px 20px; background: #f8fafc; border-top: 1px solid #eef2f8; }
.info-banner { display: flex; align-items: center; gap: 8px; font-size: 12px; padding: 10px 14px; border-radius: 12px; }
.info-banner.order-info { background: #eef2ff; color: #4338ca; }
.info-banner.tech-info { background: #f3e8ff; color: #6b21a5; }
.info-banner.task-info { background: #fef3c7; color: #d97706; }

.topology-legend { display: flex; gap: 16px; font-size: 11px; align-items: center; }
.legend-dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; margin-right: 4px; }
.legend-dot.completed { background: #10b981; }
.legend-dot.active { background: #f59e0b; }
.legend-dot.pending { background: #94a3b8; }

.back-btn {
  cursor: pointer;
  color: #3b82f6;
  background: #eef2ff;
  padding: 2px 10px;
  border-radius: 16px;
  font-size: 11px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  transition: all 0.2s;
}

.back-btn:hover {
  background: #dbeafe;
  transform: translateX(-2px);
}

.hint-text {
  font-size: 10px;
  color: #8b5cf6;
  margin-left: 12px;
  font-style: italic;
}

.flow-node-click-hint {
  position: absolute;
  bottom: -8px;
  right: -8px;
  background: #8b5cf6;
  border-radius: 50%;
  width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 10px;
  opacity: 0.8;
  animation: bounceHint 2s ease-in-out infinite;
}

@keyframes bounceHint {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-3px); }
}

.dispatch-badge {
  font-size: 9px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 2px 6px;
  border-radius: 12px;
  margin-left: 6px;
  display: inline-block;
}

/* Technicians */
.tech-container { padding: 12px; }

.tech-card {
  display: flex;
  gap: 12px;
  padding: 12px;
  margin-bottom: 10px;
  background: #fafcff;
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid #eef2f8;
  position: relative;
}

.tech-card:hover { background: #f1f5f9; transform: translateX(2px); }
.tech-card.selected { background: #eef2ff; border-color: #3b82f6; }

.tech-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 700;
  font-size: 18px;
  position: relative;
  flex-shrink: 0;
}

.tech-status-dot {
  position: absolute;
  bottom: 2px;
  right: 2px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 2px solid white;
}

.tech-status-dot.online { background: #22c55e; }
.tech-status-dot.busy { background: #ef4444; }

.tech-detail { flex: 1; }
.tech-name { font-weight: 700; font-size: 14px; color: #1e293b; margin-bottom: 4px; }
.tech-skills { display: flex; gap: 4px; flex-wrap: wrap; margin-bottom: 6px; }
.tech-skills .more { font-size: 10px; color: #64748b; margin-left: 4px; }
.tech-load { font-size: 10px; color: #5b6e8c; margin-bottom: 4px; }
.tech-orders { font-size: 10px; color: #3b82f6; display: flex; align-items: center; gap: 4px; margin-top: 4px; }

.tech-efficiency {
  display: flex;
  align-items: center;
}

.efficiency-badge {
  font-size: 11px;
  font-weight: 600;
  padding: 4px 8px;
  border-radius: 20px;
}

.efficiency-badge.high { background: #d1fae5; color: #059669; }
.efficiency-badge.medium { background: #fef3c7; color: #d97706; }
.efficiency-badge.low { background: #fee2e2; color: #dc2626; }

/* Rules Card */
.rules-card {
  background: white;
  border-radius: 16px;
  margin-top: 12px;
  padding: 0 16px;
  border: 1px solid #eef2f8;
}

.rules-header { font-weight: 600; padding: 12px 0; display: flex; align-items: center; gap: 8px; border-bottom: 1px solid #eef2f8; }
.rule { display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid #f0f2f5; font-size: 13px; }

/* Log Card */
.log-card {
  background: white;
  border-radius: 16px;
  margin-top: 12px;
  border: 1px solid #eef2f8;
}

.log-header {
  padding: 10px 16px;
  border-bottom: 1px solid #eef2f8;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  font-size: 13px;
}

.log-container {
  height: 140px;
  overflow-y: auto;
  padding: 8px;
}

.log-item {
  padding: 6px 10px;
  border-bottom: 1px solid #f0f2f5;
  font-size: 10px;
  display: flex;
  gap: 10px;
}

.log-time { font-family: monospace; font-size: 9px; color: #94a3b8; min-width: 65px; }
.log-msg { flex: 1; word-break: break-word; }
.log-item.success .log-msg { color: #16a34a; }
.log-item.warning .log-msg { color: #d97706; }
.log-empty { text-align: center; padding: 20px; color: #94a3b8; font-size: 11px; }

/* Dialog */
.assign-option { margin: 12px 0; }

/* Responsive */
@media (max-width: 1200px) {
  .main-layout { flex-direction: column; }
  .topology-panel { min-width: auto; }
  .topology-container { height: 420px; }
}
</style>