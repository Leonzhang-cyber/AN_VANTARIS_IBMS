<template>
  <div class="emergency-command-container">
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
            <span class="loading-title">Loading Emergency Command</span>
            <span class="loading-dots"><span>.</span><span>.</span><span>.</span></span>
          </div>
          <div class="loading-progress">
            <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
          </div>
          <div class="loading-tip">Emergency Command & Control Center</div>
          <div class="loading-subtip">{{ loadingMessage }}</div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div v-else class="ec-main">
      <!-- Page Header -->
      <div class="page-header">
        <div>
          <h1 class="page-title">Emergency Command</h1>
          <p class="page-subtitle">Centralized emergency response, resource dispatch, and incident command</p>
        </div>
        <div class="header-actions">
          <div class="emergency-status" :class="emergencyLevel">
            <span class="status-dot"></span>
            <span>{{ emergencyStatusText }}</span>
          </div>
          <el-button type="danger" @click="activateEmergency">
            <el-icon><WarningFilled /></el-icon>
            Activate Emergency
          </el-button>
          <el-button @click="deactivateEmergency" :disabled="emergencyLevel === 'normal'">
            <el-icon><CircleCheck /></el-icon>
            Stand Down
          </el-button>
          <el-button @click="exportCommandLog">
            <el-icon><Download /></el-icon>
            Export Log
          </el-button>
        </div>
      </div>

      <!-- Emergency Banner -->
      <div v-if="emergencyLevel !== 'normal'" class="emergency-banner" :class="emergencyLevel">
        <div class="banner-icon">
          <el-icon><WarningFilled /></el-icon>
        </div>
        <div class="banner-content">
          <div class="banner-title">{{ emergencyTitle }}</div>
          <div class="banner-description">{{ emergencyDescription }}</div>
        </div>
        <div class="banner-timer">
          <el-icon><Timer /></el-icon>
          <span>{{ emergencyElapsedTime }}</span>
        </div>
      </div>

      <!-- Command Center Layout -->
      <div class="command-layout">
        <!-- Left Panel - Incident Overview -->
        <div class="command-panel incident-panel">
          <div class="panel-header">
            <span class="panel-title">
              <el-icon><Flag /></el-icon>
              Active Incident
            </span>
            <el-tag v-if="activeIncident" :type="getIncidentTagType(activeIncident.severity)" size="large">
              {{ activeIncident.severity.toUpperCase() }}
            </el-tag>
          </div>

          <div v-if="activeIncident" class="incident-details">
            <h2>{{ activeIncident.title }}</h2>
            <p class="incident-location">
              <el-icon><Location /></el-icon>
              {{ activeIncident.location }}
            </p>
            <p class="incident-description">{{ activeIncident.description }}</p>

            <div class="incident-metrics">
              <div class="metric">
                <span class="label">Reported</span>
                <span class="value">{{ activeIncident.reportedTime }}</span>
              </div>
              <div class="metric">
                <span class="label">Response Time</span>
                <span class="value">{{ activeIncident.responseTime }}</span>
              </div>
              <div class="metric">
                <span class="label">Command Post</span>
                <span class="value">{{ activeIncident.commandPost }}</span>
              </div>
            </div>

            <div class="incident-timeline">
              <div class="timeline-header">Incident Timeline</div>
              <div class="timeline-events">
                <div v-for="event in activeIncident.timeline" :key="event.id" class="timeline-event">
                  <div class="event-time">{{ event.time }}</div>
                  <div class="event-dot"></div>
                  <div class="event-content">
                    <div class="event-title">{{ event.title }}</div>
                    <div class="event-description">{{ event.description }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div v-else class="no-incident">
            <el-icon><SuccessFilled /></el-icon>
            <p>No active emergency incidents</p>
            <el-button type="primary" @click="createEmergencyIncident">Create Incident</el-button>
          </div>
        </div>

        <!-- Center Panel - Emergency Map -->
        <div class="command-panel map-panel">
          <div class="panel-header">
            <span class="panel-title">
              <el-icon><Location /></el-icon>
              Emergency Map
            </span>
            <div class="map-controls">
              <el-button-group size="small">
                <el-button @click="mapZoomIn">
                  <el-icon><ZoomIn /></el-icon>
                </el-button>
                <el-button @click="mapZoomOut">
                  <el-icon><ZoomOut /></el-icon>
                </el-button>
                <el-button @click="resetMapView">
                  <el-icon><RefreshLeft /></el-icon>
                </el-button>
              </el-button-group>
            </div>
          </div>
          <div class="emergency-map">
            <div class="map-container" ref="mapContainer">
              <!-- Incident Location Marker -->
              <div class="incident-marker" :style="{ left: incidentX + '%', top: incidentY + '%' }">
                <div class="marker-pulse critical"></div>
                <div class="marker-icon critical">
                  <el-icon><WarningFilled /></el-icon>
                </div>
                <div class="marker-label">Incident</div>
              </div>

              <!-- Resource Markers -->
              <div v-for="resource in dispatchedResources" :key="resource.id" class="resource-marker" :style="{ left: resource.x + '%', top: resource.y + '%' }">
                <div class="marker-icon" :style="{ background: resource.color }">
                  <el-icon><component :is="resource.icon" /></el-icon>
                </div>
                <div class="marker-label">{{ resource.name }}</div>
                <div class="marker-eta">{{ resource.eta }}</div>
              </div>

              <!-- Evacuation Zones -->
              <div class="evacuation-zone" :style="{ left: '25%', top: '30%', width: '25%', height: '20%' }">
                <div class="zone-label">Evacuation Zone A</div>
              </div>
              <div class="evacuation-zone" :style="{ left: '55%', top: '45%', width: '20%', height: '25%' }">
                <div class="zone-label">Evacuation Zone B</div>
              </div>

              <!-- Assembly Point -->
              <div class="assembly-point" :style="{ left: '35%', top: '65%' }">
                <div class="assembly-icon">
                  <el-icon><Flag /></el-icon>
                </div>
                <div class="assembly-label">Assembly Point</div>
              </div>
            </div>
          </div>
          <div class="map-legend">
            <div class="legend-item"><span class="legend-dot critical"></span>Incident Location</div>
            <div class="legend-item"><span class="legend-dot resource"></span>Emergency Resource</div>
            <div class="legend-item"><span class="legend-dot zone"></span>Evacuation Zone</div>
            <div class="legend-item"><span class="legend-dot assembly"></span>Assembly Point</div>
          </div>
        </div>

        <!-- Right Panel - Resource Dispatch -->
        <div class="command-panel resource-panel">
          <div class="panel-header">
            <span class="panel-title">
              <el-icon><Van /></el-icon>
              Resource Dispatch
            </span>
            <el-button type="primary" size="small" @click="dispatchResource">
              <el-icon><Plus /></el-icon>
              Dispatch
            </el-button>
          </div>

          <div class="resource-categories">
            <el-tabs v-model="resourceTab" class="resource-tabs">
              <el-tab-pane label="Emergency Teams" name="teams">
                <div class="resource-list">
                  <div v-for="team in emergencyTeams" :key="team.id" class="resource-item">
                    <div class="resource-avatar" :style="{ background: team.color }">
                      <el-icon><User /></el-icon>
                    </div>
                    <div class="resource-info">
                      <div class="resource-name">{{ team.name }}</div>
                      <div class="resource-status" :class="team.status">{{ team.status }}</div>
                      <div class="resource-location">{{ team.location }}</div>
                    </div>
                    <div class="resource-actions">
                      <el-button v-if="team.status === 'available'" size="small" type="primary" @click="dispatchTeam(team)">Dispatch</el-button>
                      <el-button v-else size="small" @click="trackTeam(team)">Track</el-button>
                    </div>
                  </div>
                </div>
              </el-tab-pane>

              <el-tab-pane label="Equipment" name="equipment">
                <div class="resource-list">
                  <div v-for="equip in equipment" :key="equip.id" class="resource-item">
                    <div class="resource-avatar" :style="{ background: equip.color }">
                      <el-icon><Tools /></el-icon>
                    </div>
                    <div class="resource-info">
                      <div class="resource-name">{{ equip.name }}</div>
                      <div class="resource-status" :class="equip.status">{{ equip.status }}</div>
                      <div class="resource-location">{{ equip.location }}</div>
                    </div>
                    <div class="resource-actions">
                      <el-button v-if="equip.status === 'available'" size="small" type="primary" @click="dispatchEquipment(equip)">Dispatch</el-button>
                      <el-button v-else size="small" @click="trackEquipment(equip)">Track</el-button>
                    </div>
                  </div>
                </div>
              </el-tab-pane>

              <el-tab-pane label="Vehicles" name="vehicles">
                <div class="resource-list">
                  <div v-for="vehicle in vehicles" :key="vehicle.id" class="resource-item">
                    <div class="resource-avatar" :style="{ background: vehicle.color }">
                      <el-icon><Van /></el-icon>
                    </div>
                    <div class="resource-info">
                      <div class="resource-name">{{ vehicle.name }}</div>
                      <div class="resource-status" :class="vehicle.status">{{ vehicle.status }}</div>
                      <div class="resource-location">{{ vehicle.location }}</div>
                    </div>
                    <div class="resource-actions">
                      <el-button v-if="vehicle.status === 'available'" size="small" type="primary" @click="dispatchVehicle(vehicle)">Dispatch</el-button>
                      <el-button v-else size="small" @click="trackVehicle(vehicle)">Track</el-button>
                    </div>
                  </div>
                </div>
              </el-tab-pane>
            </el-tabs>
          </div>
        </div>
      </div>

      <!-- Bottom Section - Communication & Actions -->
      <div class="command-bottom">
        <el-row :gutter="20">
          <!-- Communication Channel -->
          <el-col :span="12">
            <el-card class="communication-card" shadow="hover">
              <template #header>
                <div class="card-header">
                  <span class="card-title">
                    <el-icon><ChatDotRound /></el-icon>
                    Emergency Communication
                  </span>
                  <el-radio-group v-model="commChannel" size="small">
                    <el-radio-button label="all">All</el-radio-button>
                    <el-radio-button label="command">Command</el-radio-button>
                    <el-radio-button label="teams">Teams</el-radio-button>
                  </el-radio-group>
                </div>
              </template>
              <div class="chat-messages">
                <div v-for="msg in filteredMessages" :key="msg.id" class="chat-message" :class="msg.type">
                  <div class="message-sender">{{ msg.sender }}</div>
                  <div class="message-content">{{ msg.message }}</div>
                  <div class="message-time">{{ msg.time }}</div>
                </div>
              </div>
              <div class="chat-input">
                <el-input v-model="newMessage" placeholder="Type emergency message..." @keyup.enter="sendEmergencyMessage">
                  <template #append>
                    <el-button type="primary" @click="sendEmergencyMessage">Send</el-button>
                  </template>
                </el-input>
              </div>
            </el-card>
          </el-col>

          <!-- Quick Actions & Checklists -->
          <el-col :span="12">
            <el-card class="actions-card" shadow="hover">
              <template #header>
                <div class="card-header">
                  <span class="card-title">
                    <el-icon><List /></el-icon>
                    Emergency Checklists
                  </span>
                  <el-button link @click="viewAllChecklists">View All →</el-button>
                </div>
              </template>
              <div class="checklist-container">
                <div v-for="checklist in emergencyChecklists" :key="checklist.id" class="checklist-item">
                  <div class="checklist-header">
                    <el-checkbox v-model="checklist.completed" @change="updateChecklist(checklist)">
                      {{ checklist.title }}
                    </el-checkbox>
                    <el-tag :type="getChecklistTagType(checklist.priority)" size="small">{{ checklist.priority }}</el-tag>
                  </div>
                  <div class="checklist-description">{{ checklist.description }}</div>
                </div>
              </div>
              <div class="quick-actions">
                <div class="section-title">Quick Actions</div>
                <div class="action-buttons-grid">
                  <el-button @click="broadcastEvacuation">
                    <el-icon><Bell /></el-icon>
                    Broadcast Evacuation
                  </el-button>
                  <el-button @click="requestBackup">
                    <el-icon><Plus /></el-icon>
                    Request Backup
                  </el-button>
                  <el-button @click="activateSiren">
                    <el-icon><Document /></el-icon>
                    Activate Siren
                  </el-button>
                  <el-button @click="notifyAuthorities">
                    <el-icon><Phone /></el-icon>
                    Notify Authorities
                  </el-button>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- Command Footer -->
      <div class="command-footer">
        <div class="footer-left">
          <span><el-icon><Connection /></el-icon> Incident Command Post: {{ commandPost }}</span>
          <span><el-icon><User /></el-icon> Incident Commander: {{ incidentCommander }}</span>
          <span><el-icon><Timer /></el-icon> Active Since: {{ activeSince }}</span>
        </div>
        <div class="footer-right">
          <el-button size="small" @click="generateSitRep">
            <el-icon><Document /></el-icon>
            Generate SitRep
          </el-button>
          <el-button size="small" type="primary" @click="endIncident" :disabled="emergencyLevel === 'normal'">
            <el-icon><CircleCheck /></el-icon>
            End Incident
          </el-button>
        </div>
      </div>
    </div>

    <!-- Dispatch Resource Dialog -->
    <el-dialog v-model="dispatchDialogVisible" title="Dispatch Resource" width="500px">
      <el-form>
        <el-form-item label="Resource">
          <span>{{ selectedResource?.name }}</span>
        </el-form-item>
        <el-form-item label="Destination">
          <el-input v-model="dispatchDestination" placeholder="Incident location" />
        </el-form-item>
        <el-form-item label="Priority">
          <el-select v-model="dispatchPriority" style="width: 100%">
            <el-option label="Critical - Immediate" value="critical" />
            <el-option label="High - Within 5 min" value="high" />
            <el-option label="Normal - Within 15 min" value="normal" />
          </el-select>
        </el-form-item>
        <el-form-item label="Instructions">
          <el-input type="textarea" v-model="dispatchInstructions" :rows="3" placeholder="Additional instructions..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dispatchDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="confirmDispatch">Dispatch</el-button>
      </template>
    </el-dialog>

    <!-- Create Incident Dialog -->
    <el-dialog v-model="createIncidentDialogVisible" title="Create Emergency Incident" width="600px">
      <el-form :model="newIncidentForm" label-width="120px">
        <el-form-item label="Incident Type" required>
          <el-select v-model="newIncidentForm.type" style="width: 100%">
            <el-option label="Fire" value="fire" />
            <el-option label="Medical Emergency" value="medical" />
            <el-option label="Security Threat" value="security" />
            <el-option label="Natural Disaster" value="disaster" />
            <el-option label="Technical Failure" value="technical" />
          </el-select>
        </el-form-item>
        <el-form-item label="Severity" required>
          <el-select v-model="newIncidentForm.severity" style="width: 100%">
            <el-option label="Critical" value="critical" />
            <el-option label="High" value="high" />
            <el-option label="Medium" value="medium" />
          </el-select>
        </el-form-item>
        <el-form-item label="Location" required>
          <el-input v-model="newIncidentForm.location" placeholder="Incident location" />
        </el-form-item>
        <el-form-item label="Description">
          <el-input type="textarea" v-model="newIncidentForm.description" :rows="3" placeholder="Describe the incident..." />
        </el-form-item>
        <el-form-item label="Command Post">
          <el-input v-model="newIncidentForm.commandPost" placeholder="Command post location" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createIncidentDialogVisible = false">Cancel</el-button>
        <el-button type="danger" @click="confirmCreateIncident">Activate Emergency</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage, ElNotification } from 'element-plus'
import {
  WarningFilled, Download, Timer, Flag, Location, ZoomIn, ZoomOut,
  RefreshLeft, Van, Plus, User, Tools, ChatDotRound, List, Bell,
  Phone, Connection, Document, CircleCheck, SuccessFilled,
  Check, Close, Setting, Search, ArrowRight, Clock, Grid
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Initializing emergency command system...')

// ==================== Emergency State ====================
const emergencyLevel = ref('normal') // normal, warning, critical
const emergencyElapsedTime = ref('00:00:00')
let emergencyTimer: ReturnType<typeof setInterval> | null = null
let emergencyStartTime: Date | null = null

const emergencyStatusText = computed(() => {
  const map: Record<string, string> = {
    normal: 'Normal Operations',
    warning: 'WARNING - Emergency Active',
    critical: 'CRITICAL - Major Emergency'
  }
  return map[emergencyLevel.value]
})

const emergencyTitle = computed(() => {
  if (activeIncident.value) {
    return `${activeIncident.value.severity.toUpperCase()} EMERGENCY: ${activeIncident.value.title}`
  }
  return 'EMERGENCY ACTIVE'
})

const emergencyDescription = computed(() => {
  if (activeIncident.value) {
    return activeIncident.value.description
  }
  return 'Emergency response in progress'
})

// Active Incident
const activeIncident = ref<any>({
  id: 'EM-001',
  title: 'Cooling System Critical Failure',
  severity: 'critical',
  location: 'Data Center East - Floor 2',
  description: 'Complete cooling system failure detected. Temperature rising rapidly. Critical IT equipment at risk of overheating.',
  reportedTime: '08:23:45',
  responseTime: '2 min',
  commandPost: 'East Wing - Room 101',
  timeline: [
    { id: 1, time: '08:23:45', title: 'Alert Triggered', description: 'Cooling system failure detected' },
    { id: 2, time: '08:24:30', title: 'Emergency Activated', description: 'Emergency protocol initiated' },
    { id: 3, time: '08:25:15', title: 'Teams Dispatched', description: 'ERT en route to location' },
    { id: 4, time: '08:27:00', title: 'Command Post Established', description: 'Incident command operational' }
  ]
})

// Map Position
const incidentX = ref(35)
const incidentY = ref(42)

// Dispatched Resources
const dispatchedResources = ref([
  { id: 1, name: 'ERT Alpha', x: 28, y: 38, eta: '5 min', color: '#ef4444', icon: 'User' },
  { id: 2, name: 'ERT Bravo', x: 45, y: 50, eta: '8 min', color: '#f59e0b', icon: 'User' },
  { id: 3, name: 'Ambulance Unit', x: 32, y: 55, eta: '12 min', color: '#10b981', icon: 'Van' }
])

// Emergency Teams
const emergencyTeams = ref([
  { id: 1, name: 'ERT Alpha', status: 'dispatched', location: 'En route', color: '#ef4444', members: 6 },
  { id: 2, name: 'ERT Bravo', status: 'available', location: 'Station B', color: '#f59e0b', members: 4 },
  { id: 3, name: 'ERT Charlie', status: 'available', location: 'Station C', color: '#3b82f6', members: 5 },
  { id: 4, name: 'Medical Response', status: 'dispatched', location: 'En route', color: '#10b981', members: 3 }
])

// Equipment
const equipment = ref([
  { id: 1, name: 'Portable Generator', status: 'available', location: 'Warehouse A', color: '#8b5cf6' },
  { id: 2, name: 'Pump Unit', status: 'in-use', location: 'Site B', color: '#f59e0b' },
  { id: 3, name: 'Light Tower', status: 'available', location: 'Warehouse A', color: '#06b6d4' },
  { id: 4, name: 'Communications Kit', status: 'dispatched', location: 'En route', color: '#10b981' }
])

// Vehicles
const vehicles = ref([
  { id: 1, name: 'Ambulance 01', status: 'dispatched', location: 'En route', color: '#ef4444' },
  { id: 2, name: 'Fire Truck 01', status: 'available', location: 'Station A', color: '#f59e0b' },
  { id: 3, name: 'Support Vehicle', status: 'available', location: 'Depot', color: '#3b82f6' }
])

// Communication Messages
const chatMessages = ref([
  { id: 1, sender: 'Command Center', message: 'EMERGENCY ALERT: Cooling system failure at DC East', time: '08:23:45', type: 'command' },
  { id: 2, sender: 'ERT Alpha', message: 'Received. En route, ETA 5 minutes', time: '08:24:12', type: 'team' },
  { id: 3, sender: 'Command Center', message: 'Copy that. Establish command post upon arrival', time: '08:24:30', type: 'command' },
  { id: 4, sender: 'ERT Bravo', message: 'Standing by for additional instructions', time: '08:25:00', type: 'team' }
])

// Emergency Checklists
const emergencyChecklists = ref([
  { id: 1, title: 'Evacuation Protocol', description: 'Ensure all personnel evacuated from affected area', priority: 'critical', completed: false },
  { id: 2, title: 'Resource Dispatch', description: 'Deploy emergency response teams to location', priority: 'critical', completed: true },
  { id: 3, title: 'Communication Plan', description: 'Notify stakeholders and establish communication channels', priority: 'high', completed: false },
  { id: 4, title: 'Medical Response', description: 'Prepare medical teams and equipment', priority: 'high', completed: false },
  { id: 5, title: 'Damage Assessment', description: 'Conduct initial damage assessment', priority: 'medium', completed: false }
])

// Form State
const dispatchDialogVisible = ref(false)
const createIncidentDialogVisible = ref(false)
const selectedResource = ref<any>(null)
const dispatchDestination = ref('')
const dispatchPriority = ref('critical')
const dispatchInstructions = ref('')
const resourceTab = ref('teams')
const commChannel = ref('all')
const newMessage = ref('')
const commandPost = ref('East Wing - Room 101')
const incidentCommander = ref('Commander John Smith')
const activeSince = ref('08:25:00')

// New Incident Form
const newIncidentForm = ref({
  type: 'fire',
  severity: 'critical',
  location: '',
  description: '',
  commandPost: ''
})

// Computed
const filteredMessages = computed(() => {
  if (commChannel.value === 'all') return chatMessages.value
  return chatMessages.value.filter(m => m.type === commChannel.value || m.type === 'command')
})

// Helper Functions
const getIncidentTagType = (severity: string) => {
  const types: Record<string, string> = {
    critical: 'danger',
    high: 'danger',
    medium: 'warning'
  }
  return types[severity] || 'info'
}

const getChecklistTagType = (priority: string) => {
  const types: Record<string, string> = {
    critical: 'danger',
    high: 'warning',
    medium: 'info'
  }
  return types[priority] || 'info'
}

// Actions
const activateEmergency = () => {
  createIncidentDialogVisible.value = true
}

const deactivateEmergency = () => {
  ElMessage.warning('Stand down initiated. Confirm incident resolution.')
  setTimeout(() => {
    emergencyLevel.value = 'normal'
    if (emergencyTimer) {
      clearInterval(emergencyTimer)
      emergencyTimer = null
    }
    ElNotification({
      title: 'Emergency Stand Down',
      message: 'Incident has been resolved. Returning to normal operations.',
      type: 'success'
    })
  }, 2000)
}

const exportCommandLog = () => {
  ElMessage.success('Command log exported')
}

const createEmergencyIncident = () => {
  createIncidentDialogVisible.value = true
}

const confirmCreateIncident = () => {
  activeIncident.value = {
    id: `EM-${Math.floor(Math.random() * 1000)}`,
    title: newIncidentForm.value.type.toUpperCase() + ' Emergency',
    severity: newIncidentForm.value.severity,
    location: newIncidentForm.value.location,
    description: newIncidentForm.value.description,
    reportedTime: new Date().toLocaleTimeString(),
    responseTime: '0 min',
    commandPost: newIncidentForm.value.commandPost || 'Command Post',
    timeline: [
      { id: 1, time: new Date().toLocaleTimeString(), title: 'Emergency Activated', description: 'Emergency protocol initiated' }
    ]
  }
  emergencyLevel.value = newIncidentForm.value.severity === 'critical' ? 'critical' : 'warning'
  emergencyStartTime = new Date()
  startEmergencyTimer()
  createIncidentDialogVisible.value = false
  ElNotification({
    title: 'EMERGENCY ACTIVATED',
    message: `${newIncidentForm.value.severity.toUpperCase()} level emergency response initiated`,
    type: 'error',
    duration: 0
  })
}

const mapZoomIn = () => {
  ElMessage.info('Map zoom in')
}

const mapZoomOut = () => {
  ElMessage.info('Map zoom out')
}

const resetMapView = () => {
  ElMessage.info('Map view reset')
}

const dispatchResource = () => {
  ElMessage.info('Resource dispatch interface')
}

const dispatchTeam = (team: any) => {
  selectedResource.value = team
  dispatchDialogVisible.value = true
}

const dispatchEquipment = (equip: any) => {
  selectedResource.value = equip
  dispatchDialogVisible.value = true
}

const dispatchVehicle = (vehicle: any) => {
  selectedResource.value = vehicle
  dispatchDialogVisible.value = true
}

const trackTeam = (team: any) => {
  ElMessage.info(`Tracking ${team.name}`)
}

const trackEquipment = (equip: any) => {
  ElMessage.info(`Tracking ${equip.name}`)
}

const trackVehicle = (vehicle: any) => {
  ElMessage.info(`Tracking ${vehicle.name}`)
}

const confirmDispatch = () => {
  if (selectedResource.value) {
    selectedResource.value.status = 'dispatched'
    selectedResource.value.location = 'En route'
    dispatchedResources.value.push({
      id: dispatchedResources.value.length + 1,
      name: selectedResource.value.name,
      x: 30 + Math.random() * 20,
      y: 35 + Math.random() * 20,
      eta: `${Math.floor(Math.random() * 15 + 5)} min`,
      color: selectedResource.value.color,
      icon: selectedResource.value.name.includes('Ambulance') || selectedResource.value.name.includes('Truck') ? 'Van' : 'User'
    })
    chatMessages.value.push({
      id: chatMessages.value.length + 1,
      sender: 'Command Center',
      message: `${selectedResource.value.name} dispatched to incident location. ETA ${Math.floor(Math.random() * 15 + 5)} minutes.`,
      time: new Date().toLocaleTimeString(),
      type: 'command'
    })
    ElMessage.success(`${selectedResource.value.name} dispatched successfully`)
  }
  dispatchDialogVisible.value = false
}

const sendEmergencyMessage = () => {
  if (newMessage.value.trim()) {
    chatMessages.value.push({
      id: chatMessages.value.length + 1,
      sender: 'Command Center',
      message: newMessage.value,
      time: new Date().toLocaleTimeString(),
      type: 'command'
    })
    newMessage.value = ''
  }
}

const updateChecklist = (item: any) => {
  ElMessage.success(`${item.title} ${item.completed ? 'completed' : 'marked incomplete'}`)
}

const viewAllChecklists = () => {
  ElMessage.info('Viewing all checklists')
}

const broadcastEvacuation = () => {
  ElMessage.warning('EVACUATION BROADCAST: All personnel evacuate the affected area')
  chatMessages.value.push({
    id: chatMessages.value.length + 1,
    sender: 'Command Center',
    message: '⚠️ EVACUATION ORDER: All personnel in affected zone evacuate immediately to assembly point',
    time: new Date().toLocaleTimeString(),
    type: 'command'
  })
}

const requestBackup = () => {
  ElMessage.info('Backup requested - additional resources en route')
  chatMessages.value.push({
    id: chatMessages.value.length + 1,
    sender: 'Command Center',
    message: 'BACKUP REQUESTED: Additional resources dispatched to incident location',
    time: new Date().toLocaleTimeString(),
    type: 'command'
  })
}

const activateSiren = () => {
  ElMessage.warning('Emergency siren activated')
}

const notifyAuthorities = () => {
  ElMessage.info('Authorities notified - Police/Fire/EMS alerted')
}

const generateSitRep = () => {
  ElMessage.success('Situation report generated')
}

const endIncident = () => {
  ElMessage.warning('End incident? This will stand down all resources.')
  setTimeout(() => {
    deactivateEmergency()
  }, 2000)
}

// Timer Functions
const startEmergencyTimer = () => {
  if (emergencyTimer) clearInterval(emergencyTimer)
  emergencyTimer = setInterval(() => {
    if (emergencyStartTime) {
      const diff = Math.floor((new Date().getTime() - emergencyStartTime.getTime()) / 1000)
      const hours = Math.floor(diff / 3600)
      const minutes = Math.floor((diff % 3600) / 60)
      const seconds = diff % 60
      emergencyElapsedTime.value = `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`
      activeSince.value = emergencyStartTime.toLocaleTimeString()
    }
  }, 1000)
}

// Simulate real-time updates
let dataInterval: ReturnType<typeof setInterval> | null = null

const startDataSimulation = () => {
  dataInterval = setInterval(() => {
    if (emergencyLevel.value !== 'normal') {
      // Randomly update resource ETAs
      dispatchedResources.value.forEach(resource => {
        const etaMatch = resource.eta.match(/\d+/)
        if (etaMatch) {
          let minutes = parseInt(etaMatch[0])
          if (minutes > 1) {
            minutes--
            resource.eta = `${minutes} min`
          }
        }
      })

      // Random new messages
      if (Math.random() > 0.8) {
        const messages = [
          'Update: Situation under control',
          'Additional resources requested',
          'Evacuation in progress',
          'Medical teams on standby'
        ]
        chatMessages.value.push({
          id: chatMessages.value.length + 1,
          sender: 'ERT Alpha',
          message: messages[Math.floor(Math.random() * messages.length)],
          time: new Date().toLocaleTimeString(),
          type: 'team'
        })
        if (chatMessages.value.length > 50) chatMessages.value.shift()
      }
    }
  }, 10000)
}

// Loading simulation
const startLoading = () => {
  const interval = setInterval(() => {
    if (loadingProgress.value < 90) loadingProgress.value += Math.random() * 10
  }, 200)
  return interval
}

onMounted(() => {
  const interval = startLoading()
  setTimeout(() => {
    clearInterval(interval)
    loadingProgress.value = 100
    loadingMessage.value = 'Ready!'
    setTimeout(() => {
      isLoaded.value = true
      nextTick(() => {
        startDataSimulation()
      })
    }, 400)
  }, 2800)
})

onUnmounted(() => {
  if (emergencyTimer) clearInterval(emergencyTimer)
  if (dataInterval) clearInterval(dataInterval)
})
</script>

<style scoped>
/* ==================== Loading Screen ==================== */
.emergency-command-container {
  min-height: 100vh;
  background: #f0f2f6;
}

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

.spinner-ring:nth-child(1) { border-top-color: #3b82f6; }
.spinner-ring:nth-child(2) { border-right-color: #f59e0b; animation-delay: 0.2s; width: 70%; height: 70%; top: 15%; left: 15%; }
.spinner-ring:nth-child(3) { border-bottom-color: #10b981; animation-delay: 0.4s; width: 40%; height: 40%; top: 30%; left: 30%; }

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  margin-bottom: 24px;
  font-size: 24px;
  font-weight: 700;
  color: #e2e8f0;
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
  width: 320px;
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
}

.loading-subtip {
  font-size: 11px;
  color: #64748b;
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

/* ==================== Main Content ==================== */
.ec-main {
  padding: 24px 32px;
  min-height: 100vh;
}

/* Page Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 4px 0;
}

.page-subtitle {
  font-size: 14px;
  color: #64748b;
  margin: 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.emergency-status {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 20px;
  font-weight: 600;
  font-size: 13px;
}

.emergency-status.normal {
  background: #ecfdf5;
  color: #10b981;
}

.emergency-status.warning {
  background: #fffbeb;
  color: #f59e0b;
}

.emergency-status.critical {
  background: #fef2f2;
  color: #ef4444;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.emergency-status.normal .status-dot { background: #10b981; }
.emergency-status.warning .status-dot { background: #f59e0b; }
.emergency-status.critical .status-dot { background: #ef4444; }

/* Emergency Banner */
.emergency-banner {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 20px 24px;
  border-radius: 20px;
  margin-bottom: 24px;
  animation: bannerPulse 1s infinite;
}

@keyframes bannerPulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.95; }
}

.emergency-banner.critical {
  background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
  border-left: 4px solid #ef4444;
}

.emergency-banner.warning {
  background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
  border-left: 4px solid #f59e0b;
}

.banner-icon {
  font-size: 32px;
}
.emergency-banner.critical .banner-icon { color: #ef4444; }
.emergency-banner.warning .banner-icon { color: #f59e0b; }

.banner-content {
  flex: 1;
}

.banner-title {
  font-size: 20px;
  font-weight: 700;
  color: #1e293b;
}

.banner-description {
  font-size: 13px;
  color: #64748b;
  margin-top: 4px;
}

.banner-timer {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 24px;
  font-weight: 700;
  font-family: monospace;
  color: #1e293b;
}

/* Command Layout */
.command-layout {
  display: grid;
  grid-template-columns: 320px 1fr 360px;
  gap: 20px;
  margin-bottom: 24px;
}

.command-panel {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
}

.panel-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #1e293b;
}

/* Incident Panel */
.incident-panel {
  overflow-y: auto;
  max-height: calc(100vh - 280px);
}

.incident-details {
  padding: 20px;
}

.incident-details h2 {
  margin: 0 0 12px 0;
  font-size: 18px;
  color: #1e293b;
}

.incident-location {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #64748b;
  margin-bottom: 12px;
}

.incident-description {
  font-size: 14px;
  color: #475569;
  line-height: 1.5;
  margin-bottom: 20px;
}

.incident-metrics {
  display: flex;
  gap: 16px;
  padding: 12px;
  background: #f8fafc;
  border-radius: 12px;
  margin-bottom: 20px;
}

.incident-metrics .metric {
  flex: 1;
  text-align: center;
}

.incident-metrics .metric .label {
  display: block;
  font-size: 11px;
  color: #64748b;
  margin-bottom: 4px;
}

.incident-metrics .metric .value {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
}

.incident-timeline {
  margin-top: 8px;
}

.timeline-header {
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 16px;
}

.timeline-events {
  position: relative;
  padding-left: 24px;
}

.timeline-event {
  position: relative;
  margin-bottom: 16px;
}

.event-time {
  font-size: 10px;
  color: #94a3b8;
  margin-bottom: 4px;
}

.event-dot {
  position: absolute;
  left: -18px;
  top: 2px;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #3b82f6;
  box-shadow: 0 0 0 2px #dbeafe;
}

.event-title {
  font-weight: 600;
  font-size: 13px;
  color: #1e293b;
}

.event-description {
  font-size: 11px;
  color: #64748b;
}

.no-incident {
  text-align: center;
  padding: 60px 20px;
  color: #94a3b8;
}

.no-incident .el-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

/* Map Panel */
.map-panel {
  display: flex;
  flex-direction: column;
}

.emergency-map {
  flex: 1;
  min-height: 400px;
  position: relative;
}

.map-container {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #0a0e27 0%, #1a1a3e 100%);
  border-radius: 12px;
  position: relative;
  overflow: hidden;
}

.incident-marker {
  position: absolute;
  transform: translate(-50%, -50%);
  z-index: 10;
}

.marker-pulse {
  position: absolute;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  animation: markerPulse 1.5s infinite;
}

.marker-pulse.critical { background: rgba(239, 68, 68, 0.4); }

@keyframes markerPulse {
  0% { transform: translate(-50%, -50%) scale(0.8); opacity: 1; }
  100% { transform: translate(-50%, -50%) scale(1.5); opacity: 0; }
}

.marker-icon {
  position: relative;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 16px;
  z-index: 2;
}

.marker-icon.critical { background: #ef4444; }
.marker-label {
  position: absolute;
  top: -25px;
  left: 50%;
  transform: translateX(-50%);
  white-space: nowrap;
  font-size: 10px;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 2px 6px;
  border-radius: 10px;
}

.resource-marker {
  position: absolute;
  transform: translate(-50%, -50%);
  z-index: 10;
}

.resource-marker .marker-icon {
  width: 24px;
  height: 24px;
  font-size: 12px;
  animation: resourceBounce 2s infinite;
}

@keyframes resourceBounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-5px); }
}

.marker-eta {
  position: absolute;
  top: -20px;
  left: 50%;
  transform: translateX(-50%);
  white-space: nowrap;
  font-size: 9px;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 2px 4px;
  border-radius: 8px;
}

.evacuation-zone {
  position: absolute;
  border: 2px dashed #f59e0b;
  border-radius: 12px;
  background: rgba(245, 158, 11, 0.1);
}

.zone-label {
  position: absolute;
  top: -20px;
  left: 8px;
  font-size: 10px;
  color: #f59e0b;
  font-weight: 600;
}

.assembly-point {
  position: absolute;
  transform: translate(-50%, -50%);
  text-align: center;
}

.assembly-icon {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #10b981;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 14px;
}

.assembly-label {
  font-size: 9px;
  color: white;
  background: rgba(0, 0, 0, 0.7);
  padding: 2px 4px;
  border-radius: 8px;
  margin-top: 4px;
  white-space: nowrap;
}

.map-legend {
  display: flex;
  gap: 20px;
  padding: 12px;
  background: #f8fafc;
  border-radius: 12px;
  margin-top: 12px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 11px;
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.legend-dot.critical { background: #ef4444; }
.legend-dot.resource { background: #3b82f6; }
.legend-dot.zone { background: #f59e0b; }
.legend-dot.assembly { background: #10b981; }

/* Resource Panel */
.resource-panel {
  overflow-y: auto;
  max-height: calc(100vh - 280px);
}

.resource-tabs :deep(.el-tabs__header) {
  margin: 0 0 12px 0;
  padding: 0 12px;
}

.resource-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 0 12px 12px;
}

.resource-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #f8fafc;
  border-radius: 12px;
}

.resource-avatar {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 20px;
}

.resource-info {
  flex: 1;
}

.resource-name {
  font-weight: 600;
  font-size: 14px;
  color: #1e293b;
}

.resource-status {
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 10px;
  display: inline-block;
  margin-top: 2px;
}

.resource-status.available { background: #d1fae5; color: #10b981; }
.resource-status.dispatched { background: #fef3c7; color: #f59e0b; }
.resource-status.in-use { background: #fee2e2; color: #ef4444; }

.resource-location {
  font-size: 10px;
  color: #94a3b8;
  margin-top: 2px;
}

/* Bottom Section */
.command-bottom {
  margin-bottom: 20px;
}

.communication-card, .actions-card {
  border-radius: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.chat-messages {
  height: 280px;
  overflow-y: auto;
  padding: 12px;
  background: #f8fafc;
  border-radius: 12px;
  margin-bottom: 12px;
}

.chat-message {
  margin-bottom: 12px;
  padding: 8px 12px;
  border-radius: 12px;
}

.chat-message.command {
  background: #eff6ff;
  border-left: 3px solid #3b82f6;
}

.chat-message.team {
  background: #f1f5f9;
  border-left: 3px solid #10b981;
}

.message-sender {
  font-size: 11px;
  font-weight: 600;
  color: #64748b;
  margin-bottom: 4px;
}

.message-content {
  font-size: 13px;
  color: #1e293b;
}

.message-time {
  font-size: 10px;
  color: #94a3b8;
  margin-top: 4px;
}

.chat-input {
  margin-top: 12px;
}

.checklist-container {
  max-height: 180px;
  overflow-y: auto;
  margin-bottom: 16px;
}

.checklist-item {
  padding: 12px;
  background: #f8fafc;
  border-radius: 12px;
  margin-bottom: 8px;
}

.checklist-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.checklist-description {
  font-size: 11px;
  color: #64748b;
  margin-left: 24px;
}

.section-title {
  font-weight: 600;
  font-size: 13px;
  color: #1e293b;
  margin-bottom: 12px;
}

.action-buttons-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
}

/* Command Footer */
.command-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.footer-left {
  display: flex;
  gap: 24px;
  font-size: 12px;
  color: #64748b;
}

.footer-left .el-icon {
  margin-right: 6px;
}

.footer-right {
  display: flex;
  gap: 12px;
}

/* Responsive */
@media (max-width: 1200px) {
  .ec-main { padding: 16px; }
  .command-layout { grid-template-columns: 280px 1fr 300px; }
}

@media (max-width: 900px) {
  .command-layout { grid-template-columns: 1fr; gap: 16px; }
  .command-panel { max-height: none; }
  .emergency-banner { flex-wrap: wrap; }
  .banner-timer { font-size: 18px; }
  .command-footer { flex-direction: column; gap: 12px; text-align: center; }
  .footer-left { flex-wrap: wrap; justify-content: center; }
}
</style>