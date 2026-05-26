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
      <!-- Header with Voice -->
      <div class="page-header">
        <div class="header-left">
          <h1>Quick Control</h1>
          <p>Fast operations for daily management</p>
        </div>
        <div class="voice-area">
          <el-button
              :type="isListening ? 'danger' : 'primary'"
              :icon="Microphone"
              circle
              size="large"
              class="voice-btn"
              :class="{ 'is-listening': isListening }"
              @click="toggleVoiceInput"
          />
          <div class="voice-hint">
            <el-icon><Promotion /></el-icon>
            <span>Click and speak, e.g. "Turn off all lights"</span>
          </div>
        </div>
      </div>

      <!-- Recording Status -->
      <div v-if="isListening" class="recording-tip">
        <div class="recording-wave">
          <span v-for="i in 5" :key="i" class="wave-bar"></span>
        </div>
        <span class="recording-text">{{ interimTranscript || 'Listening...' }}</span>
        <el-button size="small" @click="stopListening">Cancel</el-button>
      </div>

      <!-- Quick Actions Section -->
      <div class="section-title">
        <el-icon><Star /></el-icon>
        <span>My Quick Actions</span>
        <el-button size="small" type="primary" plain @click="openAddQuickAction" style="margin-left: auto;">
          <el-icon><Plus /></el-icon>
          Add Action
        </el-button>
      </div>

      <div class="quick-actions-grid">
        <div
            v-for="(action, index) in quickActions"
            :key="action.id"
            class="quick-action-card"
            :style="{ borderLeftColor: action.color }"
            @click="executeQuickAction(action)"
        >
          <div class="action-icon" :style="{ background: action.color }">
            <el-icon :size="20"><component :is="action.icon" /></el-icon>
          </div>
          <div class="action-info">
            <div class="action-name">{{ action.name }}</div>
            <div class="action-desc">{{ action.description }}</div>
          </div>
          <div class="action-drag" @click.stop>
            <el-icon @click="moveAction(index, index - 1)" :class="{ disabled: index === 0 }"><Top /></el-icon>
            <el-icon @click="moveAction(index, index + 1)" :class="{ disabled: index === quickActions.length - 1 }"><Bottom /></el-icon>
            <el-icon @click="deleteQuickAction(action.id)" style="color: #f56c6c;"><Delete /></el-icon>
          </div>
        </div>

        <div class="quick-action-card add-card" @click="openAddQuickAction">
          <div class="action-icon add-icon">
            <el-icon :size="24"><Plus /></el-icon>
          </div>
          <div class="action-info">
            <div class="action-name">Add New</div>
            <div class="action-desc">Create custom shortcut</div>
          </div>
        </div>
      </div>

      <!-- Device Control -->
      <div class="section-title">
        <el-icon><Cpu /></el-icon>
        <span>Device Control</span>
      </div>

      <div class="device-dashboard">
        <!-- HVAC Card -->
        <div class="device-card hvac-card">
          <div class="device-card-header">
            <div class="device-icon"><el-icon :size="28"><ColdDrink /></el-icon></div>
            <div class="device-title"><h3>HVAC System</h3><span class="device-badge online">Online</span></div>
          </div>
          <div class="temp-display">
            <span class="temp-value">{{ hvacTemp }}°</span>
            <div class="temp-controls">
              <el-button circle size="small" @click="adjustTemp(-1)"><el-icon><Minus /></el-icon></el-button>
              <el-button circle size="small" @click="adjustTemp(1)"><el-icon><Plus /></el-icon></el-button>
            </div>
          </div>
          <div class="mode-selector">
            <button v-for="mode in ['Cool', 'Heat', 'Fan', 'Auto']" :key="mode" class="mode-btn" :class="{ active: currentHvacMode === mode }" @click="setHvacMode(mode)">{{ mode }}</button>
          </div>
          <div class="fan-slider">
            <el-slider v-model="fanSpeedValue" :min="0" :max="100" @change="setFanSpeed" />
            <span class="fan-label">Fan: {{ fanSpeedValue }}%</span>
          </div>
        </div>

        <!-- Lighting Card -->
        <div class="device-card lighting-card">
          <div class="device-card-header">
            <div class="device-icon"><el-icon :size="28"><Sunny /></el-icon></div>
            <div class="device-title"><h3>Lighting Control</h3><span class="device-badge online">Online</span></div>
          </div>
          <div class="zone-grid">
            <div v-for="zone in lightingZones" :key="zone.name" class="zone-item-card" @click="toggleLighting(zone)">
              <div class="zone-icon" :class="{ active: zone.status }"><el-icon><Sunny /></el-icon></div>
              <div class="zone-name">{{ zone.name }}</div>
              <div class="zone-status" :class="{ on: zone.status }">{{ zone.status ? 'ON' : 'OFF' }}</div>
            </div>
          </div>
          <div class="card-actions">
            <button class="action-btn primary" @click="batchControl('lighting', 'all-on')">All On</button>
            <button class="action-btn secondary" @click="batchControl('lighting', 'all-off')">All Off</button>
          </div>
        </div>

        <!-- Access Card -->
        <div class="device-card access-card">
          <div class="device-card-header">
            <div class="device-icon"><el-icon :size="28"><Lock /></el-icon></div>
            <div class="device-title"><h3>Access Control</h3><span class="device-badge online">Online</span></div>
          </div>
          <div class="door-grid">
            <div v-for="door in doors" :key="door.name" class="door-item-card" @click="toggleDoor(door)">
              <div class="door-icon" :class="{ unlocked: door.status }"><el-icon :size="24"><component :is="door.status ? 'Unlock' : 'Lock'" /></el-icon></div>
              <div class="door-name">{{ door.name }}</div>
              <div class="door-status-badge" :class="{ open: door.status }">{{ door.status ? 'Open' : 'Closed' }}</div>
            </div>
          </div>
          <div class="card-actions">
            <button class="action-btn success" @click="openAllDoors">Open All</button>
            <button class="action-btn danger" @click="emergencyLockdown">Lockdown</button>
          </div>
        </div>

        <!-- Emergency Card -->
        <div class="device-card emergency-card">
          <div class="device-card-header">
            <div class="device-icon"><el-icon :size="28"><BellFilled /></el-icon></div>
            <div class="device-title"><h3>Emergency</h3><span class="device-badge warning">Alert</span></div>
          </div>
          <div class="emergency-grid">
            <button class="emergency-btn danger" @click="callSecurity"><el-icon><User /></el-icon><span>Security</span></button>
            <button class="emergency-btn fire" @click="callFire"><el-icon><WarningFilled /></el-icon><span>Fire</span></button>
            <button class="emergency-btn warning" @click="dispatchRepair"><el-icon><Tools /></el-icon><span>Repair</span></button>
            <button class="emergency-btn medical" @click="callAmbulance"><el-icon><FirstAidKit /></el-icon><span>Medical</span></button>
            <button class="emergency-btn evacuation" @click="evacuationAlert"><el-icon><Bell /></el-icon><span>Evacuation</span></button>
            <button class="emergency-btn power" @click="powerOutage"><el-icon><Lightning /></el-icon><span>Power Outage</span></button>
          </div>
        </div>
      </div>

      <!-- Recent Operations -->
      <div class="section-title"><el-icon><List /></el-icon><span>Recent Operations</span></div>
      <el-table :data="recentOperations" stripe size="small" style="width: 100%">
        <el-table-column prop="time" label="Time" width="150" />
        <el-table-column prop="action" label="Action" />
        <el-table-column prop="result" label="Result" width="80" />
      </el-table>
    </template>

    <!-- Add Quick Action Dialog -->
    <el-dialog v-model="addActionDialogVisible" title="Add Quick Action" width="400px">
      <el-form :model="newActionForm" label-width="80px">
        <el-form-item label="Name"><el-input v-model="newActionForm.name" placeholder="e.g., All Lights Off" /></el-form-item>
        <el-form-item label="Action">
          <el-select v-model="newActionForm.actionType" style="width: 100%">
            <el-option label="All Lights Off" value="lighting_all_off" />
            <el-option label="All Lights On" value="lighting_all_on" />
            <el-option label="Set Temp 26°C" value="hvac_temp_26" />
            <el-option label="Energy Saving Mode" value="energy_saving" />
            <el-option label="Comfort Mode" value="comfort_mode" />
            <el-option label="All Doors Close" value="doors_all_close" />
            <el-option label="Off Duty Mode" value="off_duty" />
          </el-select>
        </el-form-item>
        <el-form-item label="Color"><el-color-picker v-model="newActionForm.color" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addActionDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="addQuickAction">Confirm</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Microphone, Plus, Minus, Sunny, Lock, Unlock, ColdDrink, BellFilled,
  Top, Bottom, Delete, Promotion, Star, Timer, Cpu, List, User,
  WarningFilled, Tools, FirstAidKit, Bell, Lightning
} from '@element-plus/icons-vue'

// ==================== Loading ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading...')

// ==================== Voice Recognition (模拟) ====================
const isListening = ref(false)
const interimTranscript = ref('')
let listenTimer = null

// 模拟语音识别
const toggleVoiceInput = () => {
  if (isListening.value) {
    stopListening()
    return
  }

  startListening()
}

const startListening = () => {
  isListening.value = true
  interimTranscript.value = ''

  // 模拟识别过程
  let currentText = ''
  const mockPhrases = [
    'turn',
    'turn off',
    'turn off all',
    'turn off all lights'
  ]

  let step = 0
  listenTimer = setInterval(() => {
    if (step < mockPhrases.length) {
      currentText = mockPhrases[step]
      interimTranscript.value = currentText
      step++
    } else {
      // 识别完成
      clearInterval(listenTimer)
      listenTimer = null

      // 执行命令
      processVoiceCommand(currentText)

      // 停止监听状态
      setTimeout(() => {
        isListening.value = false
        interimTranscript.value = ''
      }, 500)
    }
  }, 600)
}

const stopListening = () => {
  if (listenTimer) {
    clearInterval(listenTimer)
    listenTimer = null
  }
  isListening.value = false
  interimTranscript.value = ''
  ElMessage.info('Voice input cancelled')
}

const speakText = (text) => {
  if (!window.speechSynthesis) return
  try {
    window.speechSynthesis.cancel()
    const utterance = new SpeechSynthesisUtterance(text)
    utterance.lang = 'en-US'
    utterance.rate = 0.9
    window.speechSynthesis.speak(utterance)
  } catch (error) {
    console.warn('Speech synthesis error:', error)
  }
}

const processVoiceCommand = (cmd) => {
  // 模拟处理命令
  if (cmd.includes('turn off') || cmd.includes('off all lights')) {
    executeQuickActionById('all_lights_off')
  } else if (cmd.includes('turn on') || cmd.includes('on all lights')) {
    executeQuickActionById('all_lights_on')
  } else if (cmd.includes('26')) {
    executeQuickActionById('set_temp_26')
  } else if (cmd.includes('energy saving')) {
    executeQuickActionById('energy_saving')
  } else if (cmd.includes('comfort')) {
    executeQuickActionById('comfort_mode')
  } else if (cmd.includes('off duty')) {
    executeQuickActionById('off_duty')
  } else if (cmd.includes('close all doors')) {
    executeQuickActionById('doors_all_close')
  } else {
    ElMessage.info(`Command: "${cmd}"`)
    speakText(`Command ${cmd} received`)
  }
}

// ==================== Quick Actions ====================
const quickActions = ref([
  { id: 'all_lights_off', name: 'All Lights Off', icon: 'Sunny', description: 'Turn off all lights', color: '#f59e0b', action: 'lighting_all_off' },
  { id: 'all_lights_on', name: 'All Lights On', icon: 'Sunny', description: 'Turn on all lights', color: '#10b981', action: 'lighting_all_on' },
  { id: 'set_temp_26', name: 'Set Temp 26°C', icon: 'ColdDrink', description: 'Set HVAC to 26°C', color: '#3b82f6', action: 'hvac_temp_26' },
  { id: 'off_duty', name: 'Off Duty', icon: 'Timer', description: 'Turn off all devices', color: '#8b5cf6', action: 'off_duty' },
  { id: 'energy_saving', name: 'Energy Saving', icon: 'Star', description: 'Eco mode activation', color: '#10b981', action: 'energy_saving' },
  { id: 'comfort_mode', name: 'Comfort Mode', icon: 'Sunny', description: 'Optimal comfort settings', color: '#f59e0b', action: 'comfort_mode' },
  { id: 'doors_all_close', name: 'All Doors Close', icon: 'Lock', description: 'Secure all access points', color: '#ef4444', action: 'doors_all_close' }
])

const showToast = (msg) => {
  ElMessage.success(msg)
  speakText(msg)
}

const executeQuickAction = (action) => {
  switch (action.action) {
    case 'lighting_all_off': lightingZones.value.forEach(z => z.status = false); showToast('All lights turned off'); break
    case 'lighting_all_on': lightingZones.value.forEach(z => z.status = true); showToast('All lights turned on'); break
    case 'hvac_temp_26': hvacTemp.value = 26; showToast('Temperature set to 26°C'); break
    case 'off_duty': lightingZones.value.forEach(z => z.status = false); hvacTemp.value = 18; fanSpeedValue.value = 30; doors.value.forEach(d => d.status = false); showToast('Off duty mode activated'); break
    case 'energy_saving': hvacTemp.value = 26; currentHvacMode.value = 'Auto'; fanSpeedValue.value = 40; lightingZones.value.forEach(z => z.status = false); showToast('Energy saving mode activated'); break
    case 'comfort_mode': hvacTemp.value = 24; currentHvacMode.value = 'Cool'; fanSpeedValue.value = 70; lightingZones.value.forEach(z => z.status = true); showToast('Comfort mode activated'); break
    case 'doors_all_close': doors.value.forEach(d => d.status = false); showToast('All doors closed'); break
  }
  addOperationRecord(action.name, 'Success')
}

const executeQuickActionById = (id) => { const a = quickActions.value.find(a => a.id === id); if (a) executeQuickAction(a) }

const addActionDialogVisible = ref(false)
const newActionForm = ref({ name: '', actionType: 'lighting_all_off', color: '#409eff' })

const openAddQuickAction = () => { newActionForm.value = { name: '', actionType: 'lighting_all_off', color: '#409eff' }; addActionDialogVisible.value = true }

const addQuickAction = () => {
  if (!newActionForm.value.name) { ElMessage.warning('Please enter action name'); return }
  const map = {
    lighting_all_off: { icon: 'Sunny', action: 'lighting_all_off', desc: 'Turn off all lights' },
    lighting_all_on: { icon: 'Sunny', action: 'lighting_all_on', desc: 'Turn on all lights' },
    hvac_temp_26: { icon: 'ColdDrink', action: 'hvac_temp_26', desc: 'Set HVAC to 26°C' },
    energy_saving: { icon: 'Star', action: 'energy_saving', desc: 'Eco mode' },
    comfort_mode: { icon: 'Sunny', action: 'comfort_mode', desc: 'Comfort settings' },
    doors_all_close: { icon: 'Lock', action: 'doors_all_close', desc: 'Close all doors' },
    off_duty: { icon: 'Timer', action: 'off_duty', desc: 'Turn off all' }
  }
  const preset = map[newActionForm.value.actionType]
  quickActions.value.push({ id: Date.now().toString(), name: newActionForm.value.name, icon: preset.icon, description: preset.desc, color: newActionForm.value.color, action: newActionForm.value.actionType })
  addActionDialogVisible.value = false; showToast(`Added: ${newActionForm.value.name}`)
}

const deleteQuickAction = (id) => { quickActions.value = quickActions.value.filter(a => a.id !== id); ElMessage.info('Deleted') }

const moveAction = (from, to) => { if (to < 0 || to >= quickActions.value.length) return; [quickActions.value[from], quickActions.value[to]] = [quickActions.value[to], quickActions.value[from]] }

// ==================== Device Data ====================
const hvacTemp = ref(24)
const currentHvacMode = ref('Cool')
const fanSpeedValue = ref(60)

const adjustTemp = (d) => {
  let t = hvacTemp.value + d
  if (t >= 16 && t <= 30) {
    hvacTemp.value = t
    showToast(`Temperature set to ${hvacTemp.value}°C`)
    addOperationRecord(`Temperature set to ${hvacTemp.value}°C`, 'Success')
  }
}

const setHvacMode = (m) => {
  currentHvacMode.value = m
  showToast(`Mode changed to ${m}`)
  addOperationRecord(`Mode changed to ${m}`, 'Success')
}

const setFanSpeed = (v) => addOperationRecord(`Fan speed set to ${v}%`, 'Success')

const lightingZones = ref([
  { name: 'Lobby', status: true },
  { name: 'Office', status: true },
  { name: 'Parking', status: false },
  { name: 'Corridor', status: false },
  { name: 'Meeting Room', status: true },
  { name: 'Restroom', status: false }
])

const toggleLighting = (z) => {
  z.status = !z.status
  let s = z.status ? 'ON' : 'OFF'
  showToast(`${z.name} lights ${s}`)
  addOperationRecord(`${z.name} lights ${s}`, 'Success')
}

const doors = ref([
  { name: 'Main Gate', status: false },
  { name: 'North Gate', status: false },
  { name: 'South Gate', status: true },
  { name: 'East Gate', status: false },
  { name: 'West Gate', status: false },
  { name: 'Emergency Exit', status: false },
  { name: 'Loading Dock', status: true },
  { name: 'Roof Access', status: false }
])

const toggleDoor = (d) => {
  d.status = !d.status
  let a = d.status ? 'Opened' : 'Closed'
  showToast(`${d.name} ${a}`)
  addOperationRecord(`${d.name} ${a}`, 'Success')
}

const openAllDoors = () => {
  doors.value.forEach(d => d.status = true)
  showToast('All doors opened')
  addOperationRecord('All doors opened', 'Success')
}

const emergencyLockdown = async () => {
  try {
    await ElMessageBox.confirm('Close all doors immediately?', 'Emergency Lockdown', {
      confirmButtonText: 'Lockdown',
      type: 'error'
    })
    doors.value.forEach(d => d.status = false)
    showToast('Emergency lockdown activated!')
    addOperationRecord('Emergency lockdown', 'Critical')
  } catch {}
}

const callSecurity = () => { showToast('Security team dispatched'); addOperationRecord('Security dispatched', 'Critical') }
const callFire = () => { showToast('Fire alert activated! Fire department notified.'); addOperationRecord('Fire alert', 'Critical') }
const dispatchRepair = () => { showToast('Repair technician dispatched'); addOperationRecord('Repair dispatched', 'Pending') }
const callAmbulance = () => { showToast('Ambulance dispatched. ETA: 5 minutes'); addOperationRecord('Ambulance dispatched', 'Critical') }
const evacuationAlert = () => { showToast('Evacuation alert triggered! Please proceed to nearest exit.'); addOperationRecord('Evacuation alert', 'Critical') }
const powerOutage = () => { showToast('Power outage protocol activated. Backup generators online.'); addOperationRecord('Power outage', 'Critical') }

const batchControl = (type, action) => {
  if (type === 'lighting') {
    if (action === 'all-on') { lightingZones.value.forEach(z => z.status = true); showToast('All lights on'); addOperationRecord('All lights on', 'Success') }
    else if (action === 'all-off') { lightingZones.value.forEach(z => z.status = false); showToast('All lights off'); addOperationRecord('All lights off', 'Success') }
  }
}

const recentOperations = ref([{ time: new Date().toLocaleTimeString(), action: 'System Ready', result: 'Success' }])

const addOperationRecord = (action, result) => {
  recentOperations.value.unshift({ time: new Date().toLocaleTimeString(), action, result })
  if (recentOperations.value.length > 10) recentOperations.value.pop()
}

// ==================== Loading ====================
const startLoading = () => {
  let p = 0
  const interval = setInterval(() => {
    p += Math.random() * 20
    if (p >= 100) {
      p = 100
      clearInterval(interval)
      setTimeout(() => { isLoaded.value = true }, 300)
    }
    loadingProgress.value = Math.min(p, 100)
  }, 200)
  setTimeout(() => { loadingMessage.value = 'Ready!' }, 1500)
}

onMounted(() => {
  startLoading()
})

onBeforeUnmount(() => {
  if (listenTimer) {
    clearInterval(listenTimer)
  }
  if (window.speechSynthesis) window.speechSynthesis.cancel()
})
</script>

<style scoped>
.quick-control { padding: 24px; background: #f0f2f5; min-height: 100%; }

.loading-container { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); z-index: 9999; display: flex; justify-content: center; align-items: center; }
.loading-content { text-align: center; padding: 40px; border-radius: 32px; background: rgba(15,23,42,0.6); backdrop-filter: blur(20px); border: 1px solid rgba(59,130,246,0.3); }
.loading-spinner { position: relative; width: 80px; height: 80px; margin: 0 auto 24px; }
.spinner-ring { position: absolute; width: 100%; height: 100%; border-radius: 50%; border: 3px solid transparent; animation: spin 1.5s infinite; }
.spinner-ring:nth-child(1) { border-top-color: #3b82f6; }
.spinner-ring:nth-child(2) { border-right-color: #f59e0b; animation-delay: 0.2s; width: 70%; height: 70%; top: 15%; left: 15%; }
.spinner-ring:nth-child(3) { border-bottom-color: #10b981; animation-delay: 0.4s; width: 40%; height: 40%; top: 30%; left: 30%; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
.loading-text { font-size: 28px; font-weight: 700; color: #e2e8f0; margin-bottom: 20px; }
.loading-dots { display: inline-flex; gap: 2px; }
.loading-dots span { animation: bounce 1.4s infinite; }
@keyframes bounce { 0%,80%,100% { transform: scale(0); } 40% { transform: scale(1); } }
.loading-progress { width: 280px; height: 4px; background: rgba(255,255,255,0.1); border-radius: 4px; margin: 0 auto 16px; overflow: hidden; }
.progress-bar { height: 100%; background: linear-gradient(90deg, #3b82f6, #8b5cf6); transition: width 0.3s; }
.loading-tip { font-size: 13px; color: #94a3b8; }
.loading-subtip { font-size: 11px; color: #64748b; margin-top: 8px; }

.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 28px; flex-wrap: wrap; gap: 16px; }
.header-left h1 { margin: 0; font-size: 28px; font-weight: 700; color: #1a2c3e; }
.header-left p { margin: 4px 0 0; font-size: 13px; color: #6c757d; }

.voice-area { display: flex; align-items: center; gap: 12px; background: linear-gradient(135deg, #667eea, #764ba2); padding: 8px 20px; border-radius: 50px; }
.voice-btn { animation: pulse 2s infinite; }
.voice-btn.is-listening { animation: pulse-fast 1s infinite; background-color: #f56c6c; border-color: #f56c6c; }
@keyframes pulse { 0%,100% { box-shadow: 0 0 0 0 rgba(102,126,234,0.4); } 50% { box-shadow: 0 0 0 8px rgba(102,126,234,0); } }
@keyframes pulse-fast { 0%,100% { box-shadow: 0 0 0 0 rgba(245,108,108,0.4); } 50% { box-shadow: 0 0 0 8px rgba(245,108,108,0); } }
.voice-hint { display: flex; align-items: center; gap: 6px; color: white; font-size: 13px; }

.recording-tip { position: fixed; bottom: 30px; left: 50%; transform: translateX(-50%); background: rgba(0,0,0,0.85); backdrop-filter: blur(10px); padding: 12px 24px; border-radius: 50px; display: flex; align-items: center; gap: 16px; z-index: 1000; color: white; }
.recording-wave { display: flex; gap: 3px; align-items: center; }
.wave-bar { width: 4px; height: 20px; background: #f56c6c; border-radius: 2px; animation: wave 0.8s ease-in-out infinite; }
.wave-bar:nth-child(1) { animation-delay: 0s; height: 15px; }
.wave-bar:nth-child(2) { animation-delay: 0.1s; height: 25px; }
.wave-bar:nth-child(3) { animation-delay: 0.2s; height: 30px; }
.wave-bar:nth-child(4) { animation-delay: 0.3s; height: 25px; }
.wave-bar:nth-child(5) { animation-delay: 0.4s; height: 15px; }
@keyframes wave { 0%,100% { height: 15px; } 50% { height: 30px; } }
.recording-text { font-size: 14px; }

.section-title { display: flex; align-items: center; gap: 10px; font-size: 18px; font-weight: 600; color: #1a2c3e; margin: 28px 0 16px 0; }
.section-title:first-of-type { margin-top: 0; }

/* Quick Actions Grid - 响应式网格布局，自动换行整齐 */
.quick-actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 12px;
  margin-bottom: 8px;
}
.quick-action-card {
  display: flex;
  align-items: center;
  gap: 14px;
  background: white;
  border-radius: 14px;
  padding: 12px 16px;
  cursor: pointer;
  border-left: 4px solid;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  transition: all 0.2s;
}
.quick-action-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0,0,0,0.1);
}
.action-icon { width: 38px; height: 38px; border-radius: 12px; display: flex; align-items: center; justify-content: center; color: white; flex-shrink: 0; }
.action-info { flex: 1; min-width: 0; }
.action-name { font-size: 14px; font-weight: 600; }
.action-desc { font-size: 11px; color: #6c757d; margin-top: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.action-drag { display: flex; gap: 6px; opacity: 0.4; flex-shrink: 0; }
.action-drag .el-icon { cursor: pointer; font-size: 14px; }
.action-drag .disabled { opacity: 0.2; cursor: not-allowed; }
.add-card { border-left-color: #adb5bd; background: #f8f9fa; }
.add-icon { background: #e9ecef; color: #6c757d; }

/* Device Dashboard */
.device-dashboard { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 8px; }
.device-card { background: white; border-radius: 20px; padding: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.06); transition: all 0.3s; }
.device-card:hover { transform: translateY(-4px); box-shadow: 0 12px 28px rgba(0,0,0,0.12); }
.device-card-header { display: flex; align-items: center; gap: 14px; margin-bottom: 20px; }
.device-icon { width: 48px; height: 48px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 16px; display: flex; align-items: center; justify-content: center; color: white; }
.device-title h3 { margin: 0; font-size: 16px; font-weight: 600; }
.device-badge { font-size: 10px; padding: 2px 8px; border-radius: 20px; margin-top: 4px; display: inline-block; }
.device-badge.online { background: #d4edda; color: #155724; }
.device-badge.warning { background: #fff3cd; color: #856404; }

.temp-display { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;margin-top:50px }
.temp-value { font-size: 48px; font-weight: 700; color: #1a2c3e; }
.temp-controls { display: flex; gap: 8px; }
.mode-selector { display: flex; gap: 8px; margin-bottom: 16px; }
.mode-btn { flex: 1; padding: 8px; border: 1px solid #e9ecef; background: #f8f9fa; border-radius: 10px; cursor: pointer; font-size: 12px; font-weight: 500; transition: all 0.2s; }
.mode-btn.active { background: #3b82f6; border-color: #3b82f6; color: white; }
.fan-slider { margin-top: 12px; }
.fan-label { display: block; font-size: 11px; color: #6c757d; margin-top: 8px; text-align: center; }

/* Lighting Grid - 2列 */
.zone-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; margin-bottom: 18px; }
.zone-item-card { display: flex; align-items: center; gap: 10px; padding: 10px; background: #f8f9fa; border-radius: 12px; cursor: pointer; transition: all 0.2s; }
.zone-item-card:hover { background: #e9ecef; }
.zone-icon { width: 32px; height: 32px; background: #e9ecef; border-radius: 10px; display: flex; align-items: center; justify-content: center; color: #f59e0b; }
.zone-icon.active { background: #fef3c7; color: #d97706; }
.zone-name { flex: 1; font-size: 13px; font-weight: 500; }
.zone-status { font-size: 10px; padding: 2px 6px; border-radius: 10px; background: #e9ecef; }
.zone-status.on { background: #d4edda; color: #155724; }

/* Access Grid */
.door-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-bottom: 18px; }
.door-item-card { display: flex; align-items: center; gap: 8px; padding: 8px 10px; background: #f8f9fa; border-radius: 12px; cursor: pointer; transition: all 0.2s; }
.door-item-card:hover { background: #e9ecef; }
.door-icon { width: 34px; height: 34px; background: #e9ecef; border-radius: 10px; display: flex; align-items: center; justify-content: center; color: #6c757d; }
.door-icon.unlocked { background: #d4edda; color: #28a745; }
.door-name { flex: 1; font-size: 11px; font-weight: 500; }
.door-status-badge { font-size: 9px; padding: 2px 6px; border-radius: 10px; background: #e9ecef; }
.door-status-badge.open { background: #d4edda; color: #155724; }

.card-actions { display: flex; gap: 10px; margin-top: 8px; }
.action-btn { flex: 1; padding: 8px; border: none; border-radius: 10px; font-size: 12px; font-weight: 500; cursor: pointer; transition: all 0.2s; }
.action-btn.primary { background: #3b82f6; color: white; }
.action-btn.primary:hover { background: #2563eb; }
.action-btn.secondary { background: #e9ecef; color: #495057; }
.action-btn.secondary:hover { background: #dee2e6; }
.action-btn.success { background: #10b981; color: white; }
.action-btn.success:hover { background: #059669; }
.action-btn.danger { background: #ef4444; color: white; }
.action-btn.danger:hover { background: #dc2626; }

/* Emergency Grid */
.emergency-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }
.emergency-btn { display: flex; flex-direction: column; align-items: center; gap: 6px; padding: 12px; border: none; border-radius: 14px; font-size: 12px; font-weight: 600; cursor: pointer; transition: all 0.2s; }
.emergency-btn.danger { background: #fee2e2; color: #dc2626; }
.emergency-btn.danger:hover { background: #fecaca; transform: scale(1.02); }
.emergency-btn.fire { background: #fff3cd; color: #d97706; }
.emergency-btn.fire:hover { background: #ffeaa7; transform: scale(1.02); }
.emergency-btn.warning { background: #e0f2fe; color: #0284c7; }
.emergency-btn.warning:hover { background: #bae6fd; transform: scale(1.02); }
.emergency-btn.medical { background: #dcfce7; color: #16a34a; }
.emergency-btn.medical:hover { background: #bbf7d0; transform: scale(1.02); }
.emergency-btn.evacuation { background: #fef3c7; color: #d97706; }
.emergency-btn.evacuation:hover { background: #fde68a; transform: scale(1.02); }
.emergency-btn.power { background: #e0e7ff; color: #4338ca; }
.emergency-btn.power:hover { background: #c7d2fe; transform: scale(1.02); }

@media (max-width: 1400px) { .device-dashboard { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 768px) {
  .quick-control { padding: 16px; }
  .page-header { flex-direction: column; align-items: stretch; }
  .voice-area { justify-content: center; }
  .device-dashboard { grid-template-columns: 1fr; }
  .zone-grid, .door-grid { grid-template-columns: 1fr; }
  .emergency-grid { grid-template-columns: repeat(2, 1fr); }
}
:deep(.el-table .el-table__cell) { text-align: center !important; }
</style>