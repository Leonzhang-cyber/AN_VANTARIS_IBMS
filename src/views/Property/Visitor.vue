<template>
  <!-- Loading 页面 -->
  <div v-if="!isBackgroundLoaded" class="loading-container">
    <div class="loading-overlay">
      <div class="loading-content">
        <div class="loading-spinner">
          <div class="spinner-ring"></div>
          <div class="spinner-ring"></div>
          <div class="spinner-ring"></div>
        </div>
        <div class="loading-text">
          <span class="loading-title">Loading Visitor System</span>
          <span class="loading-dots">...</span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Visitor Management System</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Page -->
  <div v-else class="visitor-page">
    <!-- Left Panel -->
    <div class="left-panel">
      <!-- 页面标题 -->
      <div class="page-header">
        <h1 class="page-title">👥 Visitor Management</h1>
        <div class="current-time" v-if="isFullscreen || isMobile">{{ currentTime }}</div>
      </div>

      <!-- 闸门控制区 -->
      <div class="gate-controls">
        <div class="gate-title">🚪 Access Control</div>
        <div class="gate-buttons">
          <div class="gate-card entrance" :class="{ active: entranceGateStatus === 'open' }">
            <div class="gate-icon">🚪➡️</div>
            <div class="gate-name">Main Entrance</div>
            <div class="gate-status" :class="entranceGateStatus">
              <span class="status-dot"></span>
              {{ entranceGateStatus === 'open' ? 'Opened' : 'Closed' }}
            </div>
            <el-button :type="entranceGateStatus === 'open' ? 'danger' : 'success'" size="small" @click="toggleEntranceGate" class="gate-btn">
              <span v-if="entranceGateStatus === 'open'">🔒 Close Gate</span>
              <span v-else>🔓 Open Gate</span>
            </el-button>
          </div>
          <div class="gate-card exit" :class="{ active: exitGateStatus === 'open' }">
            <div class="gate-icon">🚪⬅️</div>
            <div class="gate-name">VIP Entrance</div>
            <div class="gate-status" :class="exitGateStatus">
              <span class="status-dot"></span>
              {{ exitGateStatus === 'open' ? 'Opened' : 'Closed' }}
            </div>
            <el-button :type="exitGateStatus === 'open' ? 'danger' : 'success'" size="small" @click="toggleExitGate" class="gate-btn">
              <span v-if="exitGateStatus === 'open'">🔒 Close Gate</span>
              <span v-else>🔓 Open Gate</span>
            </el-button>
          </div>
        </div>
      </div>

      <!-- 今日访客统计卡片 -->
      <div class="visitor-stats-panel">
        <div class="panel-header">
          <span class="panel-title">👋 Today's Visitors</span>
          <el-tag size="small" type="success">Live</el-tag>
        </div>
        <div class="visitor-stats-summary">
          <div class="visitor-stat">
            <span class="visitor-stat-value">{{ todayStats.total }}</span>
            <span class="visitor-stat-label">Total</span>
          </div>
          <div class="visitor-stat">
            <span class="visitor-stat-value success">{{ todayStats.checkedIn }}</span>
            <span class="visitor-stat-label">Checked In</span>
          </div>
          <div class="visitor-stat">
            <span class="visitor-stat-value warning">{{ todayStats.checkedOut }}</span>
            <span class="visitor-stat-label">Checked Out</span>
          </div>
          <div class="visitor-stat">
            <span class="visitor-stat-value danger">{{ todayStats.pending }}</span>
            <span class="visitor-stat-label">Pending</span>
          </div>
        </div>
        <div class="visitor-progress">
          <div class="progress-label">Today's Check-in Progress</div>
          <el-progress :percentage="checkInProgress" :stroke-width="10" color="#10b981" />
        </div>
      </div>

      <!-- 当前访客列表 -->
      <div class="visitor-list">
        <div class="section-title">
          <span>📋 Current Visitors Inside</span>
          <el-tag size="small" type="success">{{ currentVisitors.length }} inside</el-tag>
        </div>
        <div class="visitors-list">
          <div v-for="visitor in currentVisitors" :key="visitor.id" class="visitor-item">
            <div class="visitor-avatar" :style="{ background: visitor.avatarColor }">
              <span>{{ visitor.name.charAt(0) }}</span>
            </div>
            <div class="visitor-info">
              <div class="visitor-name">{{ visitor.name }}</div>
              <div class="visitor-detail">{{ visitor.company }} · {{ visitor.purpose }}</div>
            </div>
            <div class="visitor-time">{{ visitor.checkInTime }}</div>
            <el-button size="small" type="danger" link @click="quickCheckOut(visitor)">Check Out</el-button>
          </div>
          <div v-if="currentVisitors.length === 0" class="empty-visitors">
            No visitors currently inside
          </div>
        </div>
      </div>

      <!-- 访客进出记录 -->
      <div class="visitor-records">
        <div class="section-title">
          <span>📋 Recent Entry/Exit Records</span>
          <el-tag size="small" type="info">Today</el-tag>
        </div>
        <div class="records-list">
          <div v-for="record in visitorRecords.slice(0, 8)" :key="record.id" class="record-item">
            <div class="record-direction" :class="record.type">
              <span v-if="record.type === 'entry'">ENTRY</span>
              <span v-else>EXIT</span>
            </div>
            <div class="record-info">
              <span class="record-name">{{ record.visitorName }}</span>
              <span class="record-time">{{ record.time }}</span>
            </div>
            <div class="record-host">
              <span>Host: {{ record.hostName }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Right Panel - 纯访客数据 -->
    <div class="right-panel">
      <!-- 大楼图片 -->
      <div class="image-container" ref="imageContainerRef">
        <el-image :src="buildingImageUrl" fit="contain" class="building-image" @load="onImageLoad" />
        <div class="image-overlay"></div>
      </div>

      <!-- 动态内容 - 纯访客数据 -->
      <div class="dynamic-content" :style="{ height: dynamicContentHeight + 'px' }">
        <!-- 访客欢迎卡片 -->
<!--        <div class="welcome-card">-->
<!--          <div class="welcome-icon">👋</div>-->
<!--          <div class="welcome-text">-->
<!--            <h3>Welcome to IBMS</h3>-->
<!--            <p>Visitor Management System</p>-->
<!--          </div>-->
<!--        </div>-->

        <!-- 实时访客统计 -->
        <div class="live-stats">
          <div class="live-stat">
            <div class="live-stat-value">{{ currentVisitors.length }}</div>
            <div class="live-stat-label">Visitors Inside Now</div>
          </div>
          <div class="live-stat">
            <div class="live-stat-value success">{{ todayStats.checkedIn }}</div>
            <div class="live-stat-label">Checked In Today</div>
          </div>
          <div class="live-stat">
            <div class="live-stat-value warning">{{ todayStats.checkedOut }}</div>
            <div class="live-stat-label">Checked Out Today</div>
          </div>
        </div>

        <!-- 今日访客趋势 -->
<!--        <div class="trend-card">-->
<!--          <div class="trend-header">-->
<!--            <span>📈 Hourly Visitor Trend</span>-->
<!--          </div>-->
<!--          <div ref="trendChartRef" class="trend-chart" style="height: 200px;"></div>-->
<!--        </div>-->

        <!-- 热门访问目的 -->
<!--        <div class="purposes-card">-->
<!--          <div class="purposes-header">-->
<!--            <span>🎯 Visitor Purposes</span>-->
<!--          </div>-->
<!--          <div class="purposes-list">-->
<!--            <div v-for="purpose in purposesStats" :key="purpose.name" class="purpose-item">-->
<!--              <span class="purpose-name">{{ purpose.name }}</span>-->
<!--              <span class="purpose-count">{{ purpose.count }}</span>-->
<!--              <div class="purpose-bar">-->
<!--                <div class="purpose-fill" :style="{ width: purpose.percentage + '%', background: purpose.color }"></div>-->
<!--              </div>-->
<!--            </div>-->
<!--          </div>-->
<!--        </div>-->

        <!-- 快速预约 -->
        <div class="quick-appointment">
          <div class="quick-header">
            <span>📅 Quick Appointment</span>
            <el-button type="primary" link size="small" @click="showAppointmentDialog = true">+ New</el-button>
          </div>
          <div class="appointment-list">
            <div v-for="apt in upcomingAppointments.slice(0, 3)" :key="apt.id" class="quick-appointment-item">
              <div class="apt-time">{{ apt.time }}</div>
              <div class="apt-name">{{ apt.visitorName }}</div>
              <div class="apt-host">{{ apt.hostName }}</div>
              <el-button size="small" type="primary" link @click="checkInAppointment(apt)">Check In</el-button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- 预约访客弹窗 -->
  <el-dialog v-model="appointmentDialogVisible" title="Schedule Appointment" width="500px">
    <el-form :model="appointmentForm" label-width="100px">
      <el-form-item label="Visitor Name" required>
        <el-input v-model="appointmentForm.visitorName" placeholder="Enter visitor name" />
      </el-form-item>
      <el-form-item label="Company" required>
        <el-input v-model="appointmentForm.company" placeholder="Enter company name" />
      </el-form-item>
      <el-form-item label="Host Name" required>
        <el-input v-model="appointmentForm.hostName" placeholder="Enter host name" />
      </el-form-item>
      <el-form-item label="Purpose">
        <el-select v-model="appointmentForm.purpose" style="width: 100%">
          <el-option label="Business Meeting" value="Business Meeting" />
          <el-option label="Interview" value="Interview" />
          <el-option label="Delivery" value="Delivery" />
          <el-option label="Maintenance" value="Maintenance" />
          <el-option label="Other" value="Other" />
        </el-select>
      </el-form-item>
      <el-form-item label="Date & Time">
        <el-date-picker v-model="appointmentForm.dateTime" type="datetime" placeholder="Select date and time" style="width: 100%" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="appointmentDialogVisible = false">Cancel</el-button>
      <el-button type="primary" @click="submitAppointment">Schedule</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, computed } from 'vue'
import { useCounterStore } from '@/stores/counter.js'
import { getCurrentInstance } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus } from '@element-plus/icons-vue'
import * as echarts from 'echarts'

const getStore = () => {
  const instance = getCurrentInstance()
  if (!instance) throw new Error('useStore() must be called within a setup function')
  const pinia = instance.appContext.config.globalProperties.$pinia
  if (!pinia) throw new Error('Pinia instance not found')
  return useCounterStore(pinia)
}
const counterStore = getStore()
const isFullscreen = computed(() => counterStore.isFullscreen)

// 图片URL
const buildingImageUrl = ref('https://aegisnx.com/wp-content/uploads/2026/05/5201314520123.jpg')

// 今日统计
const todayStats = ref({
  total: 156,
  checkedIn: 89,
  checkedOut: 45,
  pending: 22
})

const checkInProgress = computed(() => {
  return Math.round((todayStats.value.checkedIn / todayStats.value.total) * 100)
})

// 当前访客列表
const currentVisitors = ref([
  { id: 1, name: 'John Smith', company: 'Tech Solutions Inc.', purpose: 'Business Meeting', checkInTime: '09:30', avatarColor: '#409eff' },
  { id: 2, name: 'Sarah Johnson', company: 'Global Consulting', purpose: 'Interview', checkInTime: '10:15', avatarColor: '#67c23a' },
  { id: 3, name: 'Michael Chen', company: 'Logistics Co.', purpose: 'Delivery', checkInTime: '11:00', avatarColor: '#e6a23c' },
  { id: 4, name: 'David Wilson', company: 'Tech Corp', purpose: 'Interview', checkInTime: '09:45', avatarColor: '#409eff' }
])

// 访客进出记录
const visitorRecords = ref([
  { id: 1, type: 'entry', visitorName: 'John Smith', time: '09:30:15', hostName: 'Robert Brown' },
  { id: 2, type: 'entry', visitorName: 'Sarah Johnson', time: '10:15:22', hostName: 'Lisa Wong' },
  { id: 3, type: 'exit', visitorName: 'Michael Chen', time: '11:25:10', hostName: 'David Lee' },
  { id: 4, type: 'entry', visitorName: 'Emily Davis', time: '10:45:33', hostName: 'Sarah Miller' },
  { id: 5, type: 'exit', visitorName: 'John Smith', time: '11:30:05', hostName: 'Robert Brown' },
  { id: 6, type: 'entry', visitorName: 'Emma Thompson', time: '11:45:20', hostName: 'James Wilson' },
  { id: 7, type: 'entry', visitorName: 'Daniel Kim', time: '12:10:15', hostName: 'Michael Park' }
])

// 访客目的统计
const purposesStats = ref([
  { name: 'Business Meeting', count: 45, percentage: 45, color: '#409eff' },
  { name: 'Interview', count: 28, percentage: 28, color: '#10b981' },
  { name: 'Delivery', count: 15, percentage: 15, color: '#f59e0b' },
  { name: 'Other', count: 12, percentage: 12, color: '#8b5cf6' }
])

// 即将到来的预约
const upcomingAppointments = ref([
  { id: 1, visitorName: 'Thomas Anderson', hostName: 'Neo Corp', time: '14:00' },
  { id: 2, visitorName: 'Alice Wonder', hostName: 'Tech Solutions', time: '15:30' },
  { id: 3, visitorName: 'Bob Marley', hostName: 'Music Records', time: '16:00' },
  { id: 4, visitorName: 'Charlie Brown', hostName: 'Design Studio', time: '17:00' }
])

// 闸门状态
const entranceGateStatus = ref('closed')
const exitGateStatus = ref('closed')

// 弹窗状态
const appointmentDialogVisible = ref(false)
const showAppointmentDialog = ref(false)
const appointmentForm = ref({
  visitorName: '',
  company: '',
  hostName: '',
  purpose: 'Business Meeting',
  dateTime: new Date()
})

// 图表
const trendChartRef = ref(null)
let trendChart = null

// 动态高度
const imageContainerRef = ref(null)
const imageHeight = ref(0)
const dynamicContentHeight = ref(300)

// 初始化图表
const initChart = () => {
  if (!trendChartRef.value) return
  if (trendChart) trendChart.dispose()
  trendChart = echarts.init(trendChartRef.value)
  trendChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: '5%', right: '5%', top: 20, bottom: 0, containLabel: true },
    xAxis: { type: 'category', data: ['08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00'], axisLabel: { color: '#94a3b8', fontSize: 10 } },
    yAxis: { type: 'value', name: 'Visitors', nameTextStyle: { color: '#94a3b8', fontSize: 10 }, axisLabel: { color: '#94a3b8' }, splitLine: { lineStyle: { color: '#334155' } } },
    series: [{
      data: [12, 18, 25, 32, 28, 35, 42, 38, 30, 22],
      type: 'line',
      smooth: true,
      lineStyle: { width: 3, color: '#10b981' },
      areaStyle: { opacity: 0.3, color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: '#10b981' }, { offset: 1, color: '#0f172a' }]) },
      symbol: 'circle',
      symbolSize: 8,
      itemStyle: { color: '#10b981', borderColor: '#fff', borderWidth: 2 }
    }]
  })
}

// 快速签出
const quickCheckOut = (visitor) => {
  const index = currentVisitors.value.findIndex(v => v.id === visitor.id)
  if (index !== -1) {
    currentVisitors.value.splice(index, 1)
    todayStats.value.checkedOut++
    todayStats.value.checkedIn--
    visitorRecords.value.unshift({
      id: Date.now(),
      type: 'exit',
      visitorName: visitor.name,
      time: new Date().toLocaleTimeString(),
      hostName: 'System'
    })
    ElMessage.success(`${visitor.name} checked out`)
  }
}

const checkInAppointment = (apt) => {
  const newVisitor = {
    id: Date.now(),
    name: apt.visitorName,
    company: apt.hostName,
    purpose: 'Appointment',
    checkInTime: new Date().toLocaleTimeString().slice(0, 5),
    avatarColor: '#409eff'
  }
  currentVisitors.value.unshift(newVisitor)
  todayStats.value.checkedIn++
  todayStats.value.total++
  visitorRecords.value.unshift({
    id: Date.now(),
    type: 'entry',
    visitorName: apt.visitorName,
    time: new Date().toLocaleTimeString(),
    hostName: apt.hostName
  })
  ElMessage.success(`${apt.visitorName} checked in`)
}

const submitAppointment = () => {
  if (!appointmentForm.value.visitorName || !appointmentForm.value.hostName) {
    ElMessage.warning('Please fill required fields')
    return
  }
  upcomingAppointments.value.unshift({
    id: Date.now(),
    visitorName: appointmentForm.value.visitorName,
    hostName: appointmentForm.value.hostName,
    time: new Date(appointmentForm.value.dateTime).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  })
  ElMessage.success('Appointment scheduled')
  appointmentDialogVisible.value = false
  showAppointmentDialog.value = false
  appointmentForm.value = { visitorName: '', company: '', hostName: '', purpose: 'Business Meeting', dateTime: new Date() }
}

// 图片加载
const onImageLoad = (e) => {
  const img = e?.target
  if (img) {
    const naturalWidth = img.naturalWidth
    const naturalHeight = img.naturalHeight
    const containerWidth = imageContainerRef.value?.clientWidth || window.innerWidth - 520 - 48
    if (containerWidth && naturalWidth) imageHeight.value = (naturalHeight / naturalWidth) * containerWidth
  }
  setTimeout(() => updateLayoutHeights(), 100)
}

const updateLayoutHeights = () => {
  const rightPanel = document.querySelector('.right-panel')
  if (!rightPanel) return
  const panelHeight = rightPanel.clientHeight
  const calculatedHeight = panelHeight - imageHeight.value - 32
  dynamicContentHeight.value = Math.max(calculatedHeight, 280)
}

const handleWindowResize = () => {
  const containerWidth = imageContainerRef.value?.clientWidth || window.innerWidth - 520 - 48
  if (containerWidth) {
    const imgElement = document.querySelector('.building-image')
    if (imgElement && imgElement.naturalWidth) imageHeight.value = (imgElement.naturalHeight / imgElement.naturalWidth) * containerWidth
  }
  setTimeout(() => updateLayoutHeights(), 150)
  setTimeout(() => trendChart?.resize(), 200)
}

// 当前时间
const currentTime = ref('')
let timeInterval = null
let dataInterval = null

const updateCurrentTime = () => {
  const now = new Date()
  const utc = now.getTime() + (now.getTimezoneOffset() * 60000)
  const sgTime = new Date(utc + (8 * 3600000))
  currentTime.value = `${sgTime.getFullYear()}-${String(sgTime.getMonth()+1).padStart(2,'0')}-${String(sgTime.getDate()).padStart(2,'0')} ${String(sgTime.getHours()).padStart(2,'0')}:${String(sgTime.getMinutes()).padStart(2,'0')}:${String(sgTime.getSeconds()).padStart(2,'0')}.${String(sgTime.getMilliseconds()).padStart(3,'0')} SGT`
}

// 模拟实时更新
const updateRealTimeData = () => {
  if (Math.random() > 0.7) {
    const names = ['James Wilson', 'Emma Thompson', 'Daniel Kim', 'Olivia Martinez', 'William Taylor']
    const companies = ['Tech Corp', 'Global Inc', 'Solutions Ltd', 'Partners Group']
    const isEntry = Math.random() > 0.5

    if (isEntry) {
      const newVisitor = {
        id: Date.now(),
        name: names[Math.floor(Math.random() * names.length)],
        company: companies[Math.floor(Math.random() * companies.length)],
        purpose: ['Business Meeting', 'Interview', 'Delivery'][Math.floor(Math.random() * 3)],
        checkInTime: new Date().toLocaleTimeString().slice(0, 5),
        avatarColor: ['#409eff', '#67c23a', '#e6a23c'][Math.floor(Math.random() * 3)]
      }
      currentVisitors.value.unshift(newVisitor)
      todayStats.value.checkedIn++
      todayStats.value.total++
      visitorRecords.value.unshift({
        id: Date.now(),
        type: 'entry',
        visitorName: newVisitor.name,
        time: new Date().toLocaleTimeString(),
        hostName: ['Robert Brown', 'Lisa Wong', 'David Lee'][Math.floor(Math.random() * 3)]
      })
    } else {
      if (currentVisitors.value.length > 0) {
        const exitingVisitor = currentVisitors.value.pop()
        todayStats.value.checkedOut++
        todayStats.value.checkedIn--
        visitorRecords.value.unshift({
          id: Date.now(),
          type: 'exit',
          visitorName: exitingVisitor.name,
          time: new Date().toLocaleTimeString(),
          hostName: 'System'
        })
      }
    }

    if (currentVisitors.value.length > 15) currentVisitors.value.pop()
    if (visitorRecords.value.length > 20) visitorRecords.value.pop()
  }

  todayStats.value.pending = Math.max(0, todayStats.value.total - todayStats.value.checkedIn - todayStats.value.checkedOut)

  // 更新图表数据
  if (trendChart) {
    const newData = [12 + Math.floor(Math.random() * 10), 18 + Math.floor(Math.random() * 10), 25 + Math.floor(Math.random() * 10), 32 + Math.floor(Math.random() * 10), 28 + Math.floor(Math.random() * 10), 35 + Math.floor(Math.random() * 10), 42 + Math.floor(Math.random() * 10), 38 + Math.floor(Math.random() * 10), 30 + Math.floor(Math.random() * 10), 22 + Math.floor(Math.random() * 10)]
    trendChart.setOption({ series: [{ data: newData }] })
  }
}

// 闸门控制
const toggleEntranceGate = async () => {
  const action = entranceGateStatus.value === 'open' ? 'close' : 'open'
  await ElMessageBox.confirm(`${action === 'open' ? 'Open' : 'Close'} main entrance?`, 'Access Control', { confirmButtonText: 'Confirm', cancelButtonText: 'Cancel', type: 'warning' })
  entranceGateStatus.value = entranceGateStatus.value === 'open' ? 'closed' : 'open'
  ElMessage.success(`Main entrance ${entranceGateStatus.value === 'open' ? 'opened' : 'closed'}`)
}

const toggleExitGate = async () => {
  const action = exitGateStatus.value === 'open' ? 'close' : 'open'
  await ElMessageBox.confirm(`${action === 'open' ? 'Open' : 'Close'} VIP entrance?`, 'Access Control', { confirmButtonText: 'Confirm', cancelButtonText: 'Cancel', type: 'warning' })
  exitGateStatus.value = exitGateStatus.value === 'open' ? 'closed' : 'open'
  ElMessage.success(`VIP entrance ${exitGateStatus.value === 'open' ? 'opened' : 'closed'}`)
}

// 加载动画
const isBackgroundLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing assets...')
const loadingMessages = ['Preparing assets...', 'Loading visitor data...', 'Initializing access system...', 'Establishing connection...', 'Starting dashboard...', 'Almost ready...']

const preloadBackground = () => new Promise((resolve) => {
  const img = new Image()
  img.src = buildingImageUrl.value
  let progress = 0, msgIdx = 0
  const msgInterval = setInterval(() => { if (msgIdx < loadingMessages.length - 1) loadingMessage.value = loadingMessages[++msgIdx] }, 800)
  const progInterval = setInterval(() => { if (progress < 90) { progress += Math.random() * 10; loadingProgress.value = Math.min(progress, 90) } }, 100)
  img.onload = () => { clearInterval(msgInterval); clearInterval(progInterval); loadingMessage.value = 'Ready!'; loadingProgress.value = 100; setTimeout(resolve, 500) }
  img.onerror = () => { clearInterval(msgInterval); clearInterval(progInterval); loadingProgress.value = 100; setTimeout(resolve, 300) }
})

// 移动端检测
const isMobile = ref(false)
const checkMobile = () => { isMobile.value = window.innerWidth < 768; setTimeout(() => updateLayoutHeights(), 100) }
const observeRightPanel = () => {
  const rightPanel = document.querySelector('.right-panel')
  if (rightPanel && window.ResizeObserver) {
    const resizeObserver = new ResizeObserver(() => updateLayoutHeights())
    resizeObserver.observe(rightPanel)
  }
}

onMounted(async () => {
  checkMobile()
  await preloadBackground()
  isBackgroundLoaded.value = true
  await nextTick()
  setTimeout(() => { initChart(); updateLayoutHeights(); observeRightPanel() }, 200)
  updateCurrentTime()
  timeInterval = setInterval(updateCurrentTime, 100)
  dataInterval = setInterval(updateRealTimeData, 8000)
  window.addEventListener('resize', handleWindowResize)
  window.addEventListener('resize', checkMobile)
})

onUnmounted(() => {
  if (timeInterval) clearInterval(timeInterval)
  if (dataInterval) clearInterval(dataInterval)
  window.removeEventListener('resize', handleWindowResize)
  window.removeEventListener('resize', checkMobile)
  if (trendChart) trendChart.dispose()
})
</script>

<style scoped>
/* Loading样式（保持不变） */
.loading-container { position: fixed; inset: 0; background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); z-index: 9999; display: flex; justify-content: center; align-items: center; }
.loading-content { text-align: center; padding: 40px; border-radius: 32px; background: rgba(15,23,42,0.6); backdrop-filter: blur(20px); border: 1px solid rgba(59,130,246,0.3); animation: fadeInUp 0.6s; }
.loading-spinner { position: relative; width: 80px; height: 80px; margin: 0 auto 24px; }
.spinner-ring { position: absolute; width: 100%; height: 100%; border-radius: 50%; border: 3px solid transparent; animation: spin 1.5s infinite; }
.spinner-ring:nth-child(1) { border-top-color: #3b82f6; }
.spinner-ring:nth-child(2) { border-right-color: #f59e0b; width: 70%; height: 70%; top: 15%; left: 15%; animation-delay: 0.2s; }
.spinner-ring:nth-child(3) { border-bottom-color: #10b981; width: 40%; height: 40%; top: 30%; left: 30%; animation-delay: 0.4s; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
.loading-text { font-size: 28px; font-weight: 700; color: #e2e8f0; margin-bottom: 24px; }
.loading-progress { width: 280px; height: 4px; background: rgba(255,255,255,0.1); border-radius: 4px; margin: 0 auto 16px; overflow: hidden; }
.progress-bar { height: 100%; background: linear-gradient(90deg, #3b82f6, #8b5cf6, #ec489a); transition: width 0.3s; }
.loading-tip { font-size: 13px; color: #94a3b8; margin-bottom: 8px; }
.loading-subtip { font-size: 11px; color: #64748b; animation: pulse 2s infinite; }
@keyframes pulse { 0%,100% { opacity: 0.6; } 50% { opacity: 1; } }
@keyframes fadeInUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }

/* 主页面 */
.visitor-page { display: flex; width: 100%; height: 100%; background: linear-gradient(135deg, #0a0f1a 0%, #0f172a 100%); overflow: hidden; }

/* 左侧面板 */
.left-panel { width: 620px; padding: 20px; background: rgba(15,23,42,0.75); backdrop-filter: blur(12px); border-right: 1px dashed rgba(59,130,246,0.3); display: flex; flex-direction: column; height: 100%; overflow-y: auto; }

/* 右侧面板 */
.right-panel { flex: 1; display: flex; flex-direction: column; height: 100%; padding: 20px 24px; overflow-y: auto; }

/* 页面头部 */
.page-header { display: flex; justify-content: space-between; align-items: baseline; padding-bottom: 12px; border-bottom: 1px solid rgba(59,130,246,0.3); flex-shrink: 0; }
.page-title { font-size: 22px; font-weight: 800; background: linear-gradient(135deg, #e0f2fe, #bae6fd); -webkit-background-clip: text; background-clip: text; color: transparent; margin: 0; }
.current-time { font-size: 16px; font-family: monospace; color: #a5f3c3; background: rgba(0,0,0,0.5); padding: 4px 10px; border-radius: 20px; border: 1px solid rgba(16,185,129,0.3); }

/* 闸门控制 */
.gate-controls { background: linear-gradient(135deg, rgba(0,0,0,0.4), rgba(0,0,0,0.2)); border-radius: 20px; padding: 16px; margin: 16px 0; border: 1px solid rgba(59,130,246,0.2); }
.gate-title { font-size: 14px; font-weight: 600; color: #e2e8f0; margin-bottom: 12px; display: flex; align-items: center; gap: 8px; }
.gate-title::before { content: '🚪'; font-size: 16px; }
.gate-buttons { display: flex; gap: 20px; }
.gate-card { flex: 1; background: rgba(0,0,0,0.4); border-radius: 16px; padding: 16px; text-align: center; transition: all 0.3s; border: 1px solid rgba(255,255,255,0.05); }
.gate-card.entrance.active, .gate-card.exit.active { background: linear-gradient(135deg, rgba(16,185,129,0.15), rgba(16,185,129,0.05)); border-color: #10b981; box-shadow: 0 4px 15px rgba(16,185,129,0.2); }
.gate-icon { font-size: 28px; margin-bottom: 8px; }
.gate-name { font-size: 14px; font-weight: 600; color: #e2e8f0; margin-bottom: 8px; }
.gate-status { font-size: 12px; display: inline-flex; align-items: center; gap: 6px; padding: 4px 12px; border-radius: 20px; margin-bottom: 12px; }
.gate-status.open { background: rgba(16,185,129,0.2); color: #34d399; }
.gate-status.closed { background: rgba(239,68,68,0.2); color: #f87171; }
.status-dot { width: 6px; height: 6px; border-radius: 50%; display: inline-block; }
.gate-status.open .status-dot { background: #10b981; box-shadow: 0 0 5px #10b981; }
.gate-status.closed .status-dot { background: #ef4444; }
.gate-btn { width: 100%; margin-top: 4px; }

/* 访客统计面板 */
.visitor-stats-panel { background: rgba(0,0,0,0.3); border-radius: 20px; padding: 16px; margin-bottom: 16px; }
.panel-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.panel-title { font-size: 15px; font-weight: 700; color: #e2e8f0; }
.visitor-stats-summary { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 16px; }
.visitor-stat { text-align: center; }
.visitor-stat-value { font-size: 24px; font-weight: 700; color: #facc15; display: block; }
.visitor-stat-value.success { color: #10b981; }
.visitor-stat-value.warning { color: #f59e0b; }
.visitor-stat-value.danger { color: #ef4444; }
.visitor-stat-label { font-size: 10px; color: #94a3b8; }
.visitor-progress { margin-top: 16px; }

/* 当前访客列表 */
.visitor-list { background: rgba(0,0,0,0.3); border-radius: 16px; padding: 16px; margin-top: 8px; }
.section-title { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; font-size: 14px; font-weight: 600; color: #e2e8f0; }
.visitors-list { max-height: 280px; overflow-y: auto; display: flex; flex-direction: column; gap: 8px; }
.visitor-item { background: rgba(0,0,0,0.2); border-radius: 12px; padding: 10px 12px; display: flex; align-items: center; gap: 12px; transition: all 0.2s; }
.visitor-item:hover { background: rgba(59,130,246,0.1); }
.visitor-avatar { width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; color: white; }
.visitor-info { flex: 1; }
.visitor-name { font-size: 13px; font-weight: 700; color: #e2e8f0; }
.visitor-detail { font-size: 10px; color: #94a3b8; }
.visitor-time { font-size: 10px; color: #94a3b8; }
.empty-visitors { text-align: center; padding: 30px; color: #94a3b8; font-size: 12px; }

/* 访客进出记录 */
.visitor-records { background: rgba(0,0,0,0.3); border-radius: 16px; padding: 16px; margin-top: 8px; }
.records-list { max-height: 220px; overflow-y: auto; display: flex; flex-direction: column; gap: 8px; }
.record-item { background: rgba(0,0,0,0.2); border-radius: 12px; padding: 8px 12px; display: flex; align-items: center; gap: 12px; transition: all 0.2s; }
.record-direction { width: 70px; font-size: 10px; font-weight: 600; padding: 3px 6px; border-radius: 20px; text-align: center; }
.record-direction.entry { background: rgba(16,185,129,0.2); color: #34d399; }
.record-direction.exit { background: rgba(239,68,68,0.2); color: #f87171; }
.record-info { flex: 1; display: flex; flex-direction: column; }
.record-name { font-size: 12px; font-weight: 700; color: #facc15; }
.record-time { font-size: 9px; color: #94a3b8; }
.record-host { font-size: 10px; color: #94a3b8; }

/* 右侧图片容器 */
.image-container { width: 100%; border-radius: 20px; overflow: hidden; margin-bottom: 16px; box-shadow: 0 20px 35px -12px rgba(0,0,0,0.5); flex-shrink: 0; }
.building-image { width: 100%; height: auto; display: block; object-fit: contain; }
.image-overlay { position: absolute; inset: 0; background: linear-gradient(135deg, rgba(15,23,42,0.2) 0%, rgba(15,23,42,0.05) 100%); pointer-events: none; }

/* 动态内容 */
.dynamic-content { display: flex; flex-direction: column; gap: 20px; overflow-y: auto; margin-top: 20px; }

/* 欢迎卡片 */
.welcome-card { display: flex; align-items: center; gap: 16px; background: linear-gradient(135deg, rgba(59,130,246,0.15), rgba(139,92,246,0.1)); border-radius: 20px; padding: 20px; border: 1px solid rgba(59,130,246,0.2); }
.welcome-icon { font-size: 48px; }
.welcome-text h3 { font-size: 18px; font-weight: 700; color: #e2e8f0; margin: 0; }
.welcome-text p { font-size: 12px; color: #94a3b8; margin: 4px 0 0; }

/* 实时统计 */
.live-stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
.live-stat { background: rgba(0,0,0,0.3); border-radius: 16px; padding: 16px; text-align: center; }
.live-stat-value { font-size: 32px; font-weight: 800; color: #facc15; }
.live-stat-value.success { color: #10b981; }
.live-stat-value.warning { color: #f59e0b; }
.live-stat-label { font-size: 11px; color: #94a3b8; margin-top: 6px; }

/* 趋势卡片 */
.trend-card { background: rgba(0,0,0,0.3); border-radius: 16px; padding: 16px; }
.trend-header { font-size: 14px; font-weight: 600; color: #e2e8f0; margin-bottom: 12px; }
.trend-chart { width: 100%; }

/* 热门目的卡片 */
.purposes-card { background: rgba(0,0,0,0.3); border-radius: 16px; padding: 16px; }
.purposes-header { font-size: 14px; font-weight: 600; color: #e2e8f0; margin-bottom: 12px; }
.purposes-list { display: flex; flex-direction: column; gap: 10px; }
.purpose-item { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.purpose-name { width: 100px; font-size: 12px; color: #e2e8f0; }
.purpose-count { width: 40px; font-size: 12px; font-weight: 600; color: #facc15; }
.purpose-bar { flex: 1; height: 6px; background: rgba(255,255,255,0.1); border-radius: 3px; overflow: hidden; }
.purpose-fill { height: 100%; border-radius: 3px; }

/* 快速预约 */
.quick-appointment { background: rgba(0,0,0,0.3); border-radius: 16px; padding: 16px; }
.quick-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; font-size: 14px; font-weight: 600; color: #e2e8f0; }
.appointment-list { display: flex; flex-direction: column; gap: 8px; }
.quick-appointment-item { background: rgba(0,0,0,0.2); border-radius: 12px; padding: 10px 12px; display: flex; align-items: center; gap: 12px; }
.quick-appointment-item:hover { background: rgba(59,130,246,0.1); }
.apt-time { font-size: 12px; font-weight: 600; color: #10b981; min-width: 55px; }
.apt-name { flex: 1; font-size: 13px; font-weight: 600; color: #e2e8f0; }
.apt-host { font-size: 11px; color: #94a3b8; }

/* 滚动条 */
.left-panel::-webkit-scrollbar, .right-panel::-webkit-scrollbar, .dynamic-content::-webkit-scrollbar, .records-list::-webkit-scrollbar, .visitors-list::-webkit-scrollbar { width: 4px; }
.left-panel::-webkit-scrollbar-track, .right-panel::-webkit-scrollbar-track { background: rgba(59,130,246,0.1); border-radius: 4px; }
.left-panel::-webkit-scrollbar-thumb, .right-panel::-webkit-scrollbar-thumb { background: rgba(59,130,246,0.3); border-radius: 4px; }

/* 移动端 */
@media (max-width: 768px) {
  .visitor-page { flex-direction: column; overflow-y: auto; }
  .left-panel { width: 100%; border-right: none; border-bottom: 1px dashed rgba(59,130,246,0.3); }
  .right-panel { width: 100%; }
  .gate-buttons { flex-direction: column; gap: 12px; }
  .visitor-stats-summary { grid-template-columns: repeat(2, 1fr); }
  .live-stats { grid-template-columns: repeat(2, 1fr); }
  .record-item { flex-wrap: wrap; }
  .record-direction { width: 60px; font-size: 9px; }
  .quick-appointment-item { flex-wrap: wrap; }
}
</style>