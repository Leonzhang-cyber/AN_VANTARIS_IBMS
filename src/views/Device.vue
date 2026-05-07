<template>
  <div class="device-dashboard" :style="{ backgroundImage: `url(${bgImage})` }">
    <!-- 左侧分类导航 -->
    <div class="sidebar">
      <div class="logo-area">
        <span class="logo">IBMS</span>
        <span class="sub">Digital Twin</span>
      </div>
      <div class="category-list">
        <div
            v-for="cat in categories"
            :key="cat.key"
            class="category-item"
            :class="{ active: activeCategory === cat.key }"
            @click="activeCategory = cat.key"
        >
          <el-icon :size="22"><component :is="cat.icon" /></el-icon>
          <span>{{ cat.label }}</span>
        </div>
      </div>
    </div>

    <!-- 右侧内容区 -->
    <div class="main-content">
      <!-- 顶部关键指标 -->
      <div class="kpi-row">
        <div class="kpi-card">
          <div class="kpi-title">Total Devices</div>
          <div class="kpi-value">{{ currentDevices.length }}</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-title">Online Rate</div>
          <div class="kpi-value">{{ onlineRate }}%</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-title">Energy (kWh)</div>
          <div class="kpi-value">{{ totalEnergy }}</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-title">Active Alerts</div>
          <div class="kpi-value">{{ activeAlerts }}</div>
        </div>
      </div>

      <!-- 当前分类标题 + 3D 示意 -->
      <div class="section-header">
        <div class="title-section">
          <span class="category-badge">{{ currentCategoryLabel }}</span>
          <span class="system-name">System Overview</span>
        </div>
        <div class="model-hint">3D Digital Twin Preview</div>
      </div>

      <!-- 设备统计卡片 (实时) -->
      <div class="stats-grid">
        <div class="stat-card blue">
          <div class="stat-label">Total</div>
          <div class="stat-number">{{ currentStats.total }}</div>
        </div>
        <div class="stat-card green">
          <div class="stat-label">Online</div>
          <div class="stat-number">{{ currentStats.online }}</div>
        </div>
        <div class="stat-card orange">
          <div class="stat-label">Warning</div>
          <div class="stat-number">{{ currentStats.warning }}</div>
        </div>
        <div class="stat-card gray">
          <div class="stat-label">Offline</div>
          <div class="stat-number">{{ currentStats.offline }}</div>
        </div>
      </div>

      <!-- 设备列表表格 -->
      <div class="data-table-wrapper">
        <div class="table-header">
          <span>📋 Device Inventory</span>
          <el-input v-model="searchKeyword" placeholder="Search device..." prefix-icon="Search" size="small" style="width: 240px" clearable />
        </div>
        <el-table :data="filteredDevices" stripe border style="width: 100%" :header-cell-style="{ background: 'rgba(0,0,0,0.3)', color: '#e2e8f0', borderColor: 'rgba(255,255,255,0.1)' }" :row-style="{ background: 'rgba(0,0,0,0.2)', color: '#f1f5f9' }">
          <el-table-column prop="id" label="Device ID" width="130" />
          <el-table-column prop="name" label="Device Name" min-width="160" />
          <el-table-column prop="location" label="Location" min-width="140" />
          <el-table-column prop="type" label="Type" width="120" />
          <el-table-column label="Status" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="row.status === 'Online' ? 'success' : row.status === 'Warning' ? 'warning' : 'danger'" effect="dark" size="small">
                {{ row.status }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="Action" width="140" align="center">
            <template #default>
              <el-button link type="primary" size="small">Detail</el-button>
              <el-button link type="warning" size="small">Control</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import {
  OfficeBuilding, Monitor, Lock, BellFilled, Connection, Lightning, Warning
} from '@element-plus/icons-vue'

// 背景图片（可替换为真实3D图）
const bgImage = new URL('@/assets/3d-building-bg.jpg', import.meta.url).href || 'https://picsum.photos/id/104/1920/1080'

// 设备分类数据
const categories = [
  { key: 'hvac', label: 'HVAC', icon: 'OfficeBuilding' },
  { key: 'sas', label: 'SAS (Security)', icon: 'Lock' },
  { key: 'fas', label: 'FAS (Fire)', icon: 'BellFilled' },
  { key: 'lighting', label: 'Lighting Control', icon: 'Monitor' },
  { key: 'plumbing', label: 'Plumbing', icon: 'Connection' },
  { key: 'energy', label: 'Energy', icon: 'Lightning' }
]

const activeCategory = ref('hvac')

// 模拟设备数据（按分类）
const deviceDataMap = {
  hvac: [
    { id: 'HVAC-001', name: 'Chiller Plant', location: 'Machine Room', type: 'HVAC', status: 'Online' },
    { id: 'HVAC-002', name: 'AHU-1F', location: '1F Ceiling', type: 'HVAC', status: 'Online' },
    { id: 'HVAC-003', name: 'FCU-201', location: '2F Office', type: 'HVAC', status: 'Warning' },
    { id: 'HVAC-004', name: 'Cooling Tower', location: 'Rooftop', type: 'HVAC', status: 'Online' },
    { id: 'HVAC-005', name: 'VRF Outdoor', location: 'External Wall', type: 'HVAC', status: 'Offline' },
  ],
  sas: [
    { id: 'SAS-011', name: 'Door Reader A1', location: 'Main Entrance', type: 'Access', status: 'Online' },
    { id: 'SAS-012', name: 'IP Camera Lobby', location: '1F Lobby', type: 'CCTV', status: 'Online' },
    { id: 'SAS-013', name: 'Biometric Scanner', location: 'Server Room', type: 'Access', status: 'Warning' },
    { id: 'SAS-014', name: 'Gate Barrier', location: 'Parking', type: 'Access', status: 'Online' },
  ],
  fas: [
    { id: 'FAS-021', name: 'Smoke Detector H1', location: 'Corridor A', type: 'Detection', status: 'Online' },
    { id: 'FAS-022', name: 'Manual Call Point', location: 'Stairwell', type: 'Alarm', status: 'Online' },
    { id: 'FAS-023', name: 'Fire Alarm Panel', location: 'Security Room', type: 'Panel', status: 'Warning' },
    { id: 'FAS-024', name: 'Sprinkler Valve', location: 'Basement', type: 'Suppression', status: 'Online' },
  ],
  lighting: [
    { id: 'LGT-031', name: 'DALI Gateway 1', location: 'Electrical Room', type: 'Controller', status: 'Online' },
    { id: 'LGT-032', name: 'Light Sensor Lobby', location: '1F Lobby', type: 'Sensor', status: 'Online' },
    { id: 'LGT-033', name: 'LED Driver Zone1', location: 'Open Office', type: 'Driver', status: 'Warning' },
    { id: 'LGT-034', name: 'Scene Panel', location: 'Conference Room', type: 'Control', status: 'Online' },
  ],
  plumbing: [
    { id: 'PLM-041', name: 'Water Pump 1', location: 'Basement', type: 'Pump', status: 'Online' },
    { id: 'PLM-042', name: 'Flow Meter Inlet', location: 'Utility Room', type: 'Meter', status: 'Online' },
    { id: 'PLM-043', name: 'Sump Pump', location: 'Basement Pit', type: 'Pump', status: 'Warning' },
  ],
  energy: [
    { id: 'ENE-051', name: 'Main Power Meter', location: 'Electrical Room', type: 'Meter', status: 'Online' },
    { id: 'ENE-052', name: 'PV Inverter', location: 'Rooftop', type: 'Solar', status: 'Online' },
    { id: 'ENE-053', name: 'Battery Storage', location: 'Energy Center', type: 'Storage', status: 'Offline' },
    { id: 'ENE-054', name: 'Sub Meter HVAC', location: 'Machine Room', type: 'Submeter', status: 'Online' },
  ]
}

// 当前设备列表
const currentDevices = computed(() => deviceDataMap[activeCategory.value] || [])

// 搜索关键词
const searchKeyword = ref('')
const filteredDevices = computed(() => {
  const keyword = searchKeyword.value.toLowerCase().trim()
  if (!keyword) return currentDevices.value
  return currentDevices.value.filter(device =>
      device.id.toLowerCase().includes(keyword) ||
      device.name.toLowerCase().includes(keyword) ||
      device.location.toLowerCase().includes(keyword)
  )
})

// 统计数据
const currentStats = computed(() => {
  const devices = currentDevices.value
  const total = devices.length
  const online = devices.filter(d => d.status === 'Online').length
  const warning = devices.filter(d => d.status === 'Warning').length
  const offline = devices.filter(d => d.status === 'Offline').length
  return { total, online, warning, offline }
})

// 顶部 KPI (模拟全局数据)
const onlineRate = computed(() => {
  const total = currentStats.value.total
  if (total === 0) return 0
  return ((currentStats.value.online / total) * 100).toFixed(1)
})
const totalEnergy = ref(12480) // 示例
const activeAlerts = computed(() => currentStats.value.warning)

// 当前分类的标签
const currentCategoryLabel = computed(() => {
  const cat = categories.find(c => c.key === activeCategory.value)
  return cat ? cat.label : ''
})

// 图标映射
const iconComponents = {
  OfficeBuilding, Monitor, Lock, BellFilled, Connection, Lightning, Warning
}
</script>

<style scoped>
.device-dashboard {
  display: flex;
  min-height: 100vh;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  background-attachment: fixed;
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
}

/* 左侧边栏 - 半透明玻璃质感 */
.sidebar {
  width: 260px;
  background: rgba(10, 20, 30, 0.7);
  backdrop-filter: blur(12px);
  border-right: 1px solid rgba(59, 130, 246, 0.3);
  padding: 24px 16px;
  display: flex;
  flex-direction: column;
}

.logo-area {
  text-align: center;
  margin-bottom: 40px;
  padding-bottom: 20px;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}
.logo {
  display: block;
  font-size: 28px;
  font-weight: 800;
  background: linear-gradient(135deg, #a5f3fc, #2dd4bf);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  letter-spacing: 1px;
}
.sub {
  font-size: 12px;
  color: #94a3b8;
  letter-spacing: 2px;
}

.category-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.category-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 12px 16px;
  border-radius: 16px;
  color: #cbd5e1;
  cursor: pointer;
  transition: all 0.2s;
  font-weight: 500;
}
.category-item:hover {
  background: rgba(59, 130, 246, 0.2);
  color: #f1f5f9;
  transform: translateX(4px);
}
.category-item.active {
  background: rgba(59, 130, 246, 0.35);
  color: #fff;
  border-left: 3px solid #3b82f6;
}

/* 右侧主内容 */
.main-content {
  flex: 1;
  padding: 24px 32px;
  overflow-y: auto;
  background: rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(4px);
}

/* KPI 卡片行 */
.kpi-row {
  display: flex;
  gap: 20px;
  margin-bottom: 28px;
}
.kpi-card {
  background: rgba(15, 25, 35, 0.65);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(59,130,246,0.3);
  border-radius: 28px;
  padding: 14px 24px;
  flex: 1;
  transition: 0.2s;
}
.kpi-card:hover {
  background: rgba(15, 25, 35, 0.85);
  transform: translateY(-2px);
}
.kpi-title {
  font-size: 14px;
  color: #94a3b8;
  margin-bottom: 8px;
}
.kpi-value {
  font-size: 32px;
  font-weight: 700;
  color: #facc15;
  font-family: monospace;
}

/* 分类头部 */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 20px;
}
.title-section {
  display: flex;
  gap: 12px;
  align-items: baseline;
}
.category-badge {
  font-size: 24px;
  font-weight: 700;
  background: linear-gradient(135deg, #f0f9ff, #bae6fd);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}
.system-name {
  font-size: 16px;
  color: #cbd5e1;
  opacity: 0.8;
}
.model-hint {
  font-size: 12px;
  color: #3b82f6;
  background: rgba(59,130,246,0.2);
  padding: 4px 12px;
  border-radius: 40px;
}

/* 统计卡片 */
.stats-grid {
  display: flex;
  gap: 20px;
  margin-bottom: 28px;
}
.stat-card {
  flex: 1;
  padding: 16px 20px;
  border-radius: 24px;
  transition: 0.2s;
}
.stat-card.blue { background: linear-gradient(135deg, #1979C9, #0f4c81); }
.stat-card.green { background: linear-gradient(135deg, #00B42A, #0a6e1a); }
.stat-card.orange { background: linear-gradient(135deg, #FF7D00, #b45a00); }
.stat-card.gray { background: linear-gradient(135deg, #6c757d, #495057); }
.stat-label { font-size: 14px; color: rgba(255,255,255,0.8); margin-bottom: 6px; }
.stat-number { font-size: 28px; font-weight: 700; color: white; }

/* 表格区域 */
.data-table-wrapper {
  background: rgba(10, 20, 30, 0.5);
  backdrop-filter: blur(8px);
  border-radius: 28px;
  padding: 20px;
  border: 1px solid rgba(59,130,246,0.2);
}
.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  color: #e2e8f0;
  font-weight: 600;
}
:deep(.el-table) {
  background: transparent;
  font-size: 13px;
}
:deep(.el-table th.el-table__cell) {
  background: rgba(0,0,0,0.4);
  color: #f1f5f9;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}
:deep(.el-table tr) {
  background: rgba(0,0,0,0.2);
}
:deep(.el-table td.el-table__cell) {
  border-bottom: 1px solid rgba(255,255,255,0.05);
  color: #cbd5e6;
}
:deep(.el-button.is-link) {
  font-weight: 500;
}
:deep(.el-input__wrapper) {
  background: rgba(0,0,0,0.4);
  box-shadow: none;
  border: 1px solid rgba(255,255,255,0.2);
}
:deep(.el-input__inner) {
  color: #fff;
}
</style>