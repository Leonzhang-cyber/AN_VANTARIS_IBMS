<template>
  <div class="quick-control">
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
          <div class="loading-tip">Quick Control Center</div>
          <div class="loading-subtip">{{ loadingMessage }}</div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <template v-else>
      <div class="page-header">
        <h1>Quick Control</h1>
        <span class="subtitle">Fast operations for daily management</span>
      </div>

      <!-- 场景模式卡片 -->
      <div class="section-title">
        <el-icon><MagicStick /></el-icon>
        <span>Scene Modes</span>
        <span class="section-tip">(Click to switch between modes)</span>
      </div>
      <div class="scene-grid">
        <div
            v-for="scene in scenes"
            :key="scene.name"
            class="scene-card"
            :class="{ active: currentScene === scene.name }"
            @click="activateScene(scene.name)"
        >
          <div class="scene-icon" :style="{ background: scene.color }">
            <el-icon :size="28"><component :is="scene.icon" /></el-icon>
          </div>
          <div class="scene-name">{{ scene.name }}</div>
          <div class="scene-desc">{{ scene.description }}</div>
          <div class="scene-status">
            <el-switch
                :model-value="currentScene === scene.name"
                @click.stop="activateScene(scene.name)"
            />
          </div>
        </div>
      </div>

      <!-- 设备快速控制 -->
      <div class="section-title">
        <el-icon><Cpu /></el-icon>
        <span>Device Quick Control</span>
      </div>
      <div class="control-grid">
        <!-- HVAC 控制 - 增强版 -->
        <div class="control-card hvac-card">
          <div class="card-header">
            <el-icon><ColdDrink /></el-icon>
            <span>HVAC System</span>
            <span class="device-status online">● Online</span>
          </div>

          <!-- 温度控制 -->
          <div class="temp-control">
            <el-button circle size="small" @click="adjustTemp(-1)">
              <el-icon><Remove /></el-icon>
            </el-button>
            <span class="temp-value">{{ hvacTemp }}°C</span>
            <el-button circle size="small" @click="adjustTemp(1)">
              <el-icon><Plus /></el-icon>
            </el-button>
          </div>

          <!-- 模式选择 -->
          <div class="mode-buttons">
            <el-button
                v-for="mode in hvacModes"
                :key="mode"
                :type="currentHvacMode === mode ? 'primary' : 'default'"
                size="small"
                @click="setHvacMode(mode)"
            >
              {{ mode }}
            </el-button>
          </div>

          <!-- 风速控制 -->
          <div class="fan-control">
            <span class="control-label">Fan Speed</span>
            <div class="fan-buttons">
              <el-button
                  v-for="speed in fanSpeeds"
                  :key="speed"
                  :type="fanSpeed === speed ? 'primary' : 'default'"
                  size="small"
                  @click="setFanSpeedPreset(speed)"
              >
                {{ speed }}
              </el-button>
            </div>
            <el-slider v-model="fanSpeedValue" :min="0" :max="100" @change="setFanSpeed" />
          </div>

          <!-- 高级功能按钮 -->
          <div class="advanced-features">
            <el-tooltip content="Swing up/down" placement="top">
              <el-button size="small" :type="swingVertical ? 'primary' : 'default'" @click="toggleSwing('vertical')">
                <el-icon><Refresh /></el-icon>
                Swing
              </el-button>
            </el-tooltip>
            <el-tooltip content="Timer" placement="top">
              <el-button size="small" @click="openTimer">
                <el-icon><Timer /></el-icon>
                Timer
              </el-button>
            </el-tooltip>
            <el-tooltip content="Sleep mode" placement="top">
              <el-button size="small" :type="sleepMode ? 'primary' : 'default'" @click="toggleSleepMode">
                <el-icon><Moon /></el-icon>
                Sleep
              </el-button>
            </el-tooltip>
            <el-tooltip content="Turbo mode" placement="top">
              <el-button size="small" :type="turboMode ? 'primary' : 'default'" @click="toggleTurboMode">
                <el-icon><Lightning /></el-icon>
                Turbo
              </el-button>
            </el-tooltip>
            <el-tooltip content="Health filter" placement="top">
              <el-button size="small" @click="openFilterSettings">
                <el-icon><Filter /></el-icon>
                Filter
              </el-button>
            </el-tooltip>
            <el-tooltip content="Energy info" placement="top">
              <el-button size="small" @click="showEnergyInfo">
                <el-icon><DataLine /></el-icon>
                Energy
              </el-button>
            </el-tooltip>
          </div>

          <!-- 快捷操作 -->
          <div class="hvac-actions">
            <el-button type="primary" plain size="small" @click="batchControl('hvac', 'eco')">Eco Mode</el-button>
            <el-button type="warning" plain size="small" @click="batchControl('hvac', 'off')">Turn Off All</el-button>
          </div>
        </div>

        <!-- 照明控制 -->
        <div class="control-card">
          <div class="card-header">
            <el-icon><Sunny /></el-icon>
            <span>Lighting Control</span>
            <span class="device-status online">● Online</span>
          </div>
          <div class="zone-list">
            <div v-for="zone in lightingZones" :key="zone.name" class="zone-item">
              <span>{{ zone.name }}</span>
              <el-switch v-model="zone.status" size="small" @change="toggleLighting(zone)" />
            </div>
          </div>
          <div class="lighting-actions">
            <el-button type="warning" plain size="small" @click="batchControl('lighting', 'all-on')">All On</el-button>
            <el-button type="info" plain size="small" @click="batchControl('lighting', 'all-off')">All Off</el-button>
          </div>
        </div>

        <!-- 门禁控制 -->
        <div class="control-card">
          <div class="card-header">
            <el-icon><Lock /></el-icon>
            <span>Access Control</span>
            <span class="device-status online">● Online</span>
          </div>
          <div class="door-grid">
            <div v-for="door in doors" :key="door.name" class="door-item" @click="toggleDoor(door)">
              <el-icon :size="24"><component :is="door.status ? 'Unlock' : 'Lock'" /></el-icon>
              <span>{{ door.name }}</span>
              <span class="door-status" :class="{ open: door.status }">
                {{ door.status ? 'Open' : 'Closed' }}
              </span>
            </div>
          </div>
          <div class="door-actions">
            <el-button type="success" plain size="small" @click="openAllDoors">Open All Doors</el-button>
            <el-button type="danger" plain size="small" @click="emergencyLockdown">Emergency Lockdown</el-button>
          </div>
        </div>

        <!-- 应急与快捷操作 -->
        <div class="control-card emergency-card">
          <div class="card-header">
            <el-icon><BellFilled /></el-icon>
            <span>Emergency & Quick Actions</span>
          </div>
          <div class="emergency-buttons">
            <el-button type="danger" @click="callSecurity">
              <el-icon><User /></el-icon>
              Call Security
            </el-button>
            <el-button type="danger" plain @click="callFire">
              <el-icon><WarningFilled /></el-icon>
              Fire Alert
            </el-button>
            <el-button type="warning" @click="dispatchRepair">
              <el-icon><Tools /></el-icon>
              Dispatch Repair
            </el-button>
            <el-button type="primary" @click="callAmbulance">
              <el-icon><FirstAidKit /></el-icon>
              Medical Emergency
            </el-button>
            <el-button type="info" @click="broadcastAlert">
              <el-icon><Microphone /></el-icon>
              Voice Broadcast
            </el-button>
            <el-button type="success" @click="exportReport">
              <el-icon><Download /></el-icon>
              Export Report
            </el-button>
            <el-button @click="switchSite">
              <el-icon><Location /></el-icon>
              Switch Site
            </el-button>
            <el-button type="primary" plain @click="openHelpDesk">
              <el-icon><Headset /></el-icon>
              Help Desk
            </el-button>
          </div>
        </div>
      </div>

      <!-- 最近操作记录 -->
      <div class="section-title">
        <el-icon><Timer /></el-icon>
        <span>Recent Operations</span>
      </div>
      <el-table :data="recentOperations" stripe size="small" style="width: 100%">
        <el-table-column prop="time" label="Time" width="160" />
        <el-table-column prop="operator" label="Operator" width="120" />
        <el-table-column prop="action" label="Action" min-width="200" />
        <el-table-column prop="target" label="Target" min-width="150" />
        <el-table-column prop="result" label="Result" width="100" />
      </el-table>
    </template>

    <!-- 定时器弹窗 -->
    <el-dialog v-model="timerDialogVisible" title="Timer Settings" width="300px">
      <el-input-number v-model="timerHours" :min="0" :max="24" size="small" /> hours
      <el-input-number v-model="timerMinutes" :min="0" :max="59" size="small" /> minutes
      <template #footer>
        <el-button @click="timerDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="setTimer">Confirm</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  MagicStick, Cpu, ColdDrink, Sunny, Lock, Unlock, Tools,
  Download, Microphone, Location, Timer, WarningFilled,
  User, BellFilled, Plus, Remove, FirstAidKit, Headset,
  Refresh, Moon, Lightning, Filter, DataLine
} from '@element-plus/icons-vue'

const router = useRouter()

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading modules...')
const loadingMessages = [
  'Loading modules...',
  'Initializing controls...',
  'Connecting to devices...',
  'Almost ready...'
]

// 防抖函数
const debounce = (fn, delay = 300) => {
  let timer = null
  return function(...args) {
    if (timer) clearTimeout(timer)
    timer = setTimeout(() => fn.apply(this, args), delay)
  }
}

// ==================== 场景模式 ====================
const currentScene = ref('Comfort')
const scenes = ref([
  { name: 'Energy Saving', icon: 'MagicStick', color: '#10b981', description: 'Optimize energy consumption' },
  { name: 'Comfort', icon: 'Sunny', color: '#f59e0b', description: 'Priority on comfort' },
  { name: 'Holiday', icon: 'Timer', color: '#8b5cf6', description: 'Low power mode' },
  { name: 'Emergency', icon: 'WarningFilled', color: '#ef4444', description: 'Highest security' }
])

const activateScene = (sceneName) => {
  if (currentScene.value === sceneName) return

  switch(sceneName) {
    case 'Energy Saving':
      hvacTemp.value = 26
      currentHvacMode.value = 'Auto'
      fanSpeedValue.value = 40
      fanSpeed.value = 'Low'
      lightingZones.value.forEach(zone => zone.status = false)
      ElMessage.success('Energy Saving mode activated')
      break
    case 'Comfort':
      hvacTemp.value = 24
      currentHvacMode.value = 'Cool'
      fanSpeedValue.value = 70
      fanSpeed.value = 'Medium'
      lightingZones.value.forEach(zone => zone.status = true)
      ElMessage.success('Comfort mode activated')
      break
    case 'Holiday':
      hvacTemp.value = 18
      currentHvacMode.value = 'Heat'
      fanSpeedValue.value = 30
      fanSpeed.value = 'Low'
      lightingZones.value.forEach(zone => zone.status = false)
      doors.value.forEach(door => door.status = false)
      ElMessage.success('Holiday mode activated')
      break
    case 'Emergency':
      hvacTemp.value = 22
      currentHvacMode.value = 'Fan'
      fanSpeedValue.value = 100
      fanSpeed.value = 'High'
      lightingZones.value.forEach(zone => zone.status = true)
      doors.value.forEach(door => door.status = false)
      ElMessage.error('EMERGENCY mode activated!')
      break
  }

  currentScene.value = sceneName
  addOperationRecord('Scene Changed', `Switched to ${sceneName} mode`, 'Success')
}

// ==================== HVAC 控制 - 增强版 ====================
const hvacTemp = ref(24)
const currentHvacMode = ref('Cool')
const fanSpeedValue = ref(60)
const fanSpeed = ref('Medium')
const fanSpeeds = ['Low', 'Medium', 'High', 'Auto']
const hvacModes = ['Cool', 'Heat', 'Fan', 'Auto', 'Dry']
const swingVertical = ref(false)
const sleepMode = ref(false)
const turboMode = ref(false)

// 定时器相关
const timerDialogVisible = ref(false)
const timerHours = ref(0)
const timerMinutes = ref(0)
let timerInterval = null

const adjustTemp = debounce((delta) => {
  const newTemp = hvacTemp.value + delta
  if (newTemp >= 16 && newTemp <= 30) {
    hvacTemp.value = newTemp
    ElMessage.success(`Temperature set to ${hvacTemp.value}°C`)
    addOperationRecord('HVAC Control', `Temperature set to ${hvacTemp.value}°C`, 'Success')
  }
}, 200)

const setHvacMode = (mode) => {
  if (currentHvacMode.value === mode) return
  currentHvacMode.value = mode
  ElMessage.success(`HVAC mode changed to ${mode}`)
  addOperationRecord('HVAC Control', `Mode changed to ${mode}`, 'Success')
}

const setFanSpeed = (value) => {
  fanSpeedValue.value = value
  if (value <= 30) fanSpeed.value = 'Low'
  else if (value <= 70) fanSpeed.value = 'Medium'
  else fanSpeed.value = 'High'
  ElMessage.success(`Fan speed set to ${value}%`)
  addOperationRecord('HVAC Control', `Fan speed set to ${value}%`, 'Success')
}

const setFanSpeedPreset = (speed) => {
  fanSpeed.value = speed
  if (speed === 'Low') fanSpeedValue.value = 30
  else if (speed === 'Medium') fanSpeedValue.value = 60
  else if (speed === 'High') fanSpeedValue.value = 100
  else fanSpeedValue.value = 50
  ElMessage.success(`Fan speed set to ${speed}`)
  addOperationRecord('HVAC Control', `Fan speed set to ${speed}`, 'Success')
}

const toggleSwing = (direction) => {
  if (direction === 'vertical') {
    swingVertical.value = !swingVertical.value
    ElMessage.info(`Swing ${swingVertical.value ? 'enabled' : 'disabled'}`)
    addOperationRecord('HVAC Control', `Swing ${swingVertical.value ? 'enabled' : 'disabled'}`, 'Success')
  }
}

const toggleSleepMode = () => {
  sleepMode.value = !sleepMode.value
  if (sleepMode.value) {
    turboMode.value = false
    ElMessage.info('Sleep mode activated. Temperature will adjust gradually.')
  } else {
    ElMessage.info('Sleep mode deactivated')
  }
  addOperationRecord('HVAC Control', `Sleep mode ${sleepMode.value ? 'activated' : 'deactivated'}`, 'Success')
}

const toggleTurboMode = () => {
  turboMode.value = !turboMode.value
  if (turboMode.value) {
    sleepMode.value = false
    fanSpeedValue.value = 100
    fanSpeed.value = 'High'
    ElMessage.info('Turbo mode activated. Maximum cooling/heating.')
  } else {
    ElMessage.info('Turbo mode deactivated')
  }
  addOperationRecord('HVAC Control', `Turbo mode ${turboMode.value ? 'activated' : 'deactivated'}`, 'Success')
}

const openTimer = () => {
  timerHours.value = 0
  timerMinutes.value = 0
  timerDialogVisible.value = true
}

const setTimer = () => {
  const totalMinutes = timerHours.value * 60 + timerMinutes.value
  if (totalMinutes === 0) {
    ElMessage.warning('Please set a valid time')
    return
  }
  ElMessage.success(`Timer set for ${timerHours.value}h ${timerMinutes.value}m`)
  addOperationRecord('HVAC Control', `Timer set for ${timerHours.value}h ${timerMinutes.value}m`, 'Success')
  timerDialogVisible.value = false

  // 模拟定时器
  if (timerInterval) clearTimeout(timerInterval)
  timerInterval = setTimeout(() => {
    ElMessage.info('Timer: HVAC system turning off')
    addOperationRecord('HVAC Control', 'Timer: HVAC turned off automatically', 'Info')
  }, totalMinutes * 60 * 1000)
}

const openFilterSettings = () => {
  ElMessage.info('Filter settings panel opened')
  addOperationRecord('HVAC Control', 'Filter settings opened', 'Info')
}

const showEnergyInfo = () => {
  ElMessage.info(`Current energy consumption: ${Math.floor(Math.random() * 5) + 2} kWh/h`)
  addOperationRecord('HVAC Control', 'Energy info viewed', 'Info')
}

// ==================== 照明控制 ====================
const lightingZones = ref([
  { name: 'Lobby', status: true },
  { name: 'Parking B1', status: false },
  { name: 'Office Area', status: true },
  { name: 'Corridor', status: false },
  { name: 'Meeting Room', status: true },
  { name: 'Restroom', status: false }
])

const toggleLighting = (zone) => {
  const status = zone.status ? 'On' : 'Off'
  ElMessage.info(`${zone.name} lights turned ${status}`)
  addOperationRecord('Lighting Control', `${zone.name} lights turned ${status}`, 'Success')
}

// ==================== 门禁控制 ====================
const doors = ref([
  { name: 'Main Gate', status: false },
  { name: 'North Gate', status: false },
  { name: 'South Gate', status: true },
  { name: 'Emergency Exit', status: false }
])

const toggleDoor = (door) => {
  door.status = !door.status
  const action = door.status ? 'Opened' : 'Closed'
  ElMessage.info(`${door.name} ${action}`)
  addOperationRecord('Access Control', `${door.name} ${action}`, 'Success')
}

const openAllDoors = () => {
  doors.value.forEach(door => door.status = true)
  ElMessage.success('All doors opened')
  addOperationRecord('Access Control', 'All doors opened', 'Success')
}

const emergencyLockdown = async () => {
  try {
    await ElMessageBox.confirm('Emergency lockdown will close all doors. Continue?', 'Emergency', { confirmButtonText: 'Lockdown', type: 'error' })
    doors.value.forEach(door => door.status = false)
    ElMessage.error('Emergency lockdown activated! All doors closed.')
    addOperationRecord('Emergency', 'Emergency lockdown activated', 'Critical')
  } catch {}
}

// ==================== 应急操作 ====================
const callSecurity = () => {
  ElMessage.success('Security team dispatched. ETA: 2 minutes')
  addOperationRecord('Emergency', 'Security team dispatched', 'Critical')
}

const callFire = () => {
  ElMessage.error('Fire alert activated! Fire department notified.')
  addOperationRecord('Emergency', 'Fire alert activated', 'Critical')
}

const dispatchRepair = () => {
  ElMessage.info('Repair technician dispatched')
  addOperationRecord('Maintenance', 'Repair technician dispatched', 'Pending')
}

const callAmbulance = () => {
  ElMessage.success('Ambulance dispatched. ETA: 5 minutes')
  addOperationRecord('Emergency', 'Medical assistance requested', 'Critical')
}

const broadcastAlert = () => {
  ElMessage.info('Voice broadcast panel opened')
  addOperationRecord('Broadcast', 'Voice broadcast initiated', 'Pending')
}

const exportReport = () => {
  ElMessage.success('Report exported successfully')
  addOperationRecord('Quick Action', 'Exported daily report', 'Success')
}

const switchSite = () => {
  router.push('/sites')
}

const openHelpDesk = () => {
  ElMessage.info('Help desk connected')
  addOperationRecord('Support', 'Help desk contacted', 'Info')
}

// ==================== 批量控制 ====================
const batchControl = (type, action) => {
  if (type === 'hvac') {
    if (action === 'eco') {
      hvacTemp.value = 26
      currentHvacMode.value = 'Auto'
      fanSpeedValue.value = 40
      fanSpeed.value = 'Low'
      ElMessage.success('Eco mode activated')
      addOperationRecord('Batch Control', 'HVAC Eco mode activated', 'Success')
    } else if (action === 'off') {
      ElMessage.success('All HVAC units turned off')
      addOperationRecord('Batch Control', 'All HVAC units turned off', 'Success')
    }
  }
  if (type === 'lighting') {
    if (action === 'all-on') {
      lightingZones.value.forEach(zone => zone.status = true)
      ElMessage.success('All lights turned on')
      addOperationRecord('Batch Control', 'All lights on', 'Success')
    } else if (action === 'all-off') {
      lightingZones.value.forEach(zone => zone.status = false)
      ElMessage.success('All lights turned off')
      addOperationRecord('Batch Control', 'All lights off', 'Success')
    }
  }
}

// ==================== 操作记录 ====================
const recentOperations = ref([
  { time: '10:23:15', operator: 'System', action: 'System Ready', target: 'Quick Control initialized', result: 'Success' }
])

const addOperationRecord = (action, target, result) => {
  recentOperations.value.unshift({
    time: new Date().toLocaleTimeString(),
    operator: 'Current User',
    action,
    target,
    result
  })
  if (recentOperations.value.length > 10) recentOperations.value.pop()
}

// ==================== Loading ====================
let progressInterval = null, messageInterval = null

const startLoading = () => {
  let messageIndex = 0
  messageInterval = setInterval(() => {
    if (messageIndex < loadingMessages.length - 1) {
      messageIndex++
      loadingMessage.value = loadingMessages[messageIndex]
    }
  }, 600)
  progressInterval = setInterval(() => {
    if (loadingProgress.value < 100) {
      loadingProgress.value += Math.random() * 12 + 4
      if (loadingProgress.value > 100) loadingProgress.value = 100
    }
  }, 150)
  setTimeout(() => {
    clearInterval(messageInterval)
    clearInterval(progressInterval)
    loadingProgress.value = 100
    loadingMessage.value = 'Ready!'
    setTimeout(() => {
      isLoaded.value = true
      addOperationRecord('System', 'Quick Control initialized', 'Success')
    }, 400)
  }, 2500)
}

onMounted(() => { startLoading() })
onBeforeUnmount(() => {
  if (progressInterval) clearInterval(progressInterval)
  if (messageInterval) clearInterval(messageInterval)
  if (timerInterval) clearTimeout(timerInterval)
})
</script>

<style scoped>
.quick-control {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100%;
}

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

.loading-dots { display: inline-flex; gap: 2px; }
.loading-dots span { animation: bounce 1.4s infinite ease-in-out both; }
.loading-dots span:nth-child(1) { animation-delay: -0.32s; }
.loading-dots span:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce { 0%, 80%, 100% { transform: scale(0); opacity: 0.3; } 40% { transform: scale(1); opacity: 1; } }

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

.loading-tip { font-size: 13px; color: #94a3b8; letter-spacing: 1px; margin-bottom: 8px; font-weight: 500; }
.loading-subtip { font-size: 11px; color: #64748b; letter-spacing: 0.5px; animation: pulse 2s ease-in-out infinite; }
@keyframes pulse { 0%, 100% { opacity: 0.6; } 50% { opacity: 1; } }
@keyframes fadeInUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }

/* ==================== Main Content ==================== */
.page-header {
  margin-bottom: 24px;
}
.page-header h1 {
  margin: 0 0 4px 0;
  font-size: 24px;
  font-weight: 600;
  color: #1a2c3e;
}
.subtitle {
  font-size: 13px;
  color: #6c757d;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #1a2c3e;
  margin: 20px 0 16px 0;
}
.section-title:first-of-type { margin-top: 0; }
.section-tip {
  font-size: 11px;
  font-weight: normal;
  color: #909399;
}

/* 场景卡片 */
.scene-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 8px;
}
.scene-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  border: 2px solid transparent;
}
.scene-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}
.scene-card.active {
  border-color: #409eff;
  background: #ecf5ff;
}
.scene-icon {
  width: 56px;
  height: 56px;
  border-radius: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 12px;
  color: white;
}
.scene-name {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 6px;
}
.scene-desc {
  font-size: 11px;
  color: #6c757d;
  margin-bottom: 12px;
}
.scene-status {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

/* 控制卡片网格 */
.control-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 8px;
}
.control-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}
.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e9ecef;
}
.device-status {
  margin-left: auto;
  font-size: 11px;
  font-weight: normal;
  color: #909399;
}
.device-status.online { color: #67c23a; }

/* HVAC 控制 - 增强版 */
.temp-control {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
  margin-bottom: 16px;
}
.temp-value {
  font-size: 32px;
  font-weight: 700;
  color: #1a2c3e;
}
.mode-buttons {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
  justify-content: center;
  flex-wrap: wrap;
}
.control-label {
  font-size: 12px;
  color: #6c757d;
  display: block;
  margin-bottom: 8px;
}
.fan-control {
  margin-bottom: 16px;
}
.fan-buttons {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
  justify-content: center;
}
.advanced-features {
  display: flex;
  gap: 8px;
  justify-content: center;
  flex-wrap: wrap;
  margin-bottom: 16px;
  padding: 12px 0;
  border-top: 1px solid #e9ecef;
  border-bottom: 1px solid #e9ecef;
}
.hvac-actions {
  display: flex;
  gap: 8px;
  justify-content: center;
  flex-wrap: wrap;
  margin-top: 8px;
}

/* 照明控制 */
.zone-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 16px;
}
.zone-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 0;
}
.lighting-actions, .door-actions {
  display: flex;
  gap: 8px;
  justify-content: center;
  flex-wrap: wrap;
}

/* 门禁控制 */
.door-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 16px;
}
.door-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px;
  background: #f8fafc;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
}
.door-item:hover { background: #f1f5f9; }
.door-status {
  margin-left: auto;
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 10px;
  background: #e9ecef;
}
.door-status.open {
  background: #d4edda;
  color: #155724;
}

/* 应急按钮 */
.emergency-buttons {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}
.emergency-buttons .el-button { margin: 0; }
.emergency-card { border-left: 3px solid #ef4444; }

/* 操作记录表格 */
.el-table .el-table__cell { text-align: center !important; }

/* 响应式 */
@media (max-width: 1024px) {
  .control-grid { grid-template-columns: 1fr; }
  .scene-grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 768px) {
  .scene-grid { grid-template-columns: 1fr; }
  .door-grid { grid-template-columns: 1fr; }
  .emergency-buttons { grid-template-columns: 1fr; }
  .advanced-features { gap: 4px; }
}
</style>