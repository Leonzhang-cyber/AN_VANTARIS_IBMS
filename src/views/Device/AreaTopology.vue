<!-- src/views/device/AreaTopology.vue -->
<template>
  <div class="topology-page">
    <!-- 左侧区域拓扑树 -->
    <div class="topology-left-panel" :style="{ width: leftPanelWidth + 'px' }">
      <div class="panel-header">
        <el-icon><Connection /></el-icon>
        <span>Area Topology</span>
        <el-tooltip content="Toggle Panel" placement="bottom">
          <el-button
              :icon="ArrowLeft"
              circle
              size="small"
              class="toggle-btn"
              @click="toggleLeftPanel"
          />
        </el-tooltip>
      </div>

      <div class="search-box">
        <el-input
            v-model="searchKeyword"
            placeholder="Search area, system, device..."
            size="small"
            clearable
            :prefix-icon="Search"
        />
      </div>

      <div class="topology-tree">
        <el-tree
            ref="treeRef"
            :data="filteredTreeData"
            :props="treeProps"
            node-key="id"
            :default-expanded-keys="defaultExpandedKeys"
            :highlight-current="true"
            :expand-on-click-node="true"
            :filter-node-method="filterNode"
            @node-click="handleNodeClick"
        >
          <template #default="{ node, data }">
            <div class="tree-node-content">
              <el-avatar
                  v-if="data.type === 'device'"
                  :src="data.imageUrl"
                  :size="28"
                  shape="square"
                  class="device-thumb"
                  fit="cover"
              />
              <el-icon v-else-if="data.type === 'area'" class="node-icon area-icon">
                <OfficeBuilding />
              </el-icon>
              <el-icon v-else class="node-icon system-icon">
                <component :is="getSystemIcon(data.systemType)" />
              </el-icon>

              <span class="node-label" :class="{ 'is-selected': node.isCurrent }">
                {{ data.label || data.name }}
              </span>

              <span
                  v-if="data.type === 'device' || data.type === 'system'"
                  class="status-dot"
                  :class="`status-${data.status}`"
              ></span>

              <el-badge
                  v-if="data.type !== 'device'"
                  :value="getChildrenCount(data)"
                  class="count-badge"
                  type="info"
              />
            </div>
          </template>
        </el-tree>
      </div>

      <div class="stats-overview">
        <div class="stat-item">
          <span class="stat-value">{{ stats.totalAreas }}</span>
          <span class="stat-label">Areas</span>
        </div>
        <div class="stat-item">
          <span class="stat-value">{{ stats.totalSystems }}</span>
          <span class="stat-label">Systems</span>
        </div>
        <div class="stat-item">
          <span class="stat-value">{{ stats.totalDevices }}</span>
          <span class="stat-label">Devices</span>
        </div>
        <div class="stat-item">
          <span class="stat-value online">{{ stats.onlineDevices }}</span>
          <span class="stat-label">Online</span>
        </div>
      </div>
    </div>

    <div class="resize-handle" @mousedown="startResizeLeft"></div>

    <!-- 中间渲染画布 -->
    <div class="topology-canvas">
      <div class="canvas-toolbar">
        <div class="toolbar-left">
          <el-radio-group v-model="viewMode" size="small">
            <el-radio-button value="grid">
              <el-icon><Grid /></el-icon>
              Grid
            </el-radio-button>
            <el-radio-button value="list">
              <el-icon><List /></el-icon>
              List
            </el-radio-button>
          </el-radio-group>

          <el-divider direction="vertical" />

          <el-button-group size="small">
            <el-button
                :type="showHeatmap ? 'primary' : 'default'"
                @click="showHeatmap = !showHeatmap"
            >
              <el-icon><DataAnalysis /></el-icon>
              Heatmap
            </el-button>
          </el-button-group>
        </div>

        <div class="toolbar-right">
          <el-select
              v-model="currentFloor"
              size="small"
              style="width: 140px; margin-left: 8px"
              @change="changeFloor"
          >
            <el-option v-for="floor in floors" :key="floor" :label="floor" :value="floor" />
          </el-select>
        </div>
      </div>

      <div class="canvas-container">
        <!-- 设备网格视图 -->
        <div v-if="viewMode === 'grid'" class="device-grid-view">
          <div v-if="displayDevices.length === 0" class="empty-canvas-hint">
            <el-icon :size="48"><View /></el-icon>
            <p>Select an area or system to view devices</p>
          </div>

          <div v-else class="device-grid">
            <div
                v-for="device in displayDevices"
                :key="device.id"
                class="device-card"
                :class="{
                'is-selected': selectedDevice?.id === device.id,
                [`status-${device.status}`]: true
              }"
                @click="handleNodeClick(device)"
                @mouseenter="hoveredDevice = device"
                @mouseleave="hoveredDevice = null"
            >
              <div class="device-image-wrapper">
                <el-image
                    :src="device.imageUrl"
                    fit="contain"
                    class="device-image"
                    :alt="device.name"
                >
                  <template #error>
                    <div class="image-fallback">
                      <el-icon :size="40"><Cpu /></el-icon>
                      <span>No Image</span>
                    </div>
                  </template>
                  <template #placeholder>
                    <div class="image-loading">
                      <el-icon class="is-loading" :size="24"><Loading /></el-icon>
                    </div>
                  </template>
                </el-image>

                <el-tag
                    class="device-status-tag"
                    :type="getStatusType(device.status)"
                    size="small"
                    effect="dark"
                >
                  {{ device.status.toUpperCase() }}
                </el-tag>

                <div
                    v-if="showHeatmap"
                    class="heatmap-overlay"
                    :style="{ opacity: getHeatmapOpacity(device) }"
                ></div>
              </div>

              <div class="device-info">
                <h5 class="device-name">{{ device.name }}</h5>
                <span class="device-model">{{ device.model }}</span>
                <div class="device-metrics-mini">
                  <span class="metric-mini" :class="{ warning: device.metrics.temperature > 28 }">
                    {{ device.metrics.temperature }}°C
                  </span>
                  <span class="metric-mini" :class="{ warning: device.metrics.power > 20 }">
                    {{ device.metrics.power }} kW
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 设备列表视图 -->
        <div v-else class="device-list-view">
          <el-table
              :data="displayDevices"
              style="width: 100%"
              height="100%"
              highlight-current-row
              @row-click="handleNodeClick"
              :row-class-name="tableRowClassName"
          >
            <el-table-column width="60">
              <template #default="{ row }">
                <el-avatar :src="row.imageUrl" :size="40" shape="square" fit="cover">
                  <template #error>
                    <el-icon :size="24"><Cpu /></el-icon>
                  </template>
                </el-avatar>
              </template>
            </el-table-column>
            <el-table-column prop="name" label="Device Name" min-width="150">
              <template #default="{ row }">
                <span class="table-device-name">{{ row.name }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="model" label="Model" width="130" />
            <el-table-column prop="status" label="Status" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)" size="small" effect="dark">
                  {{ row.status.toUpperCase() }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="Temp" width="80">
              <template #default="{ row }">
                <span :class="{ 'text-warning': row.metrics.temperature > 28 }">
                  {{ row.metrics.temperature }}°C
                </span>
              </template>
            </el-table-column>
            <el-table-column label="Power" width="80">
              <template #default="{ row }">
                <span :class="{ 'text-warning': row.metrics.power > 20 }">
                  {{ row.metrics.power }} kW
                </span>
              </template>
            </el-table-column>
            <el-table-column label="Efficiency" width="90">
              <template #default="{ row }">
                <span :class="{ 'text-danger': row.metrics.efficiency < 80 }">
                  {{ row.metrics.efficiency }}%
                </span>
              </template>
            </el-table-column>
            <el-table-column label="Actions" width="120" fixed="right">
              <template #default="{ row }">
                <el-button size="small" :icon="Switch" @click.stop="handleDeviceControl(row)">
                  Control
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <div class="canvas-legend">
          <div class="legend-item"><span class="dot online"></span> Online</div>
          <div class="legend-item"><span class="dot warning"></span> Warning</div>
          <div class="legend-item"><span class="dot error"></span> Error</div>
          <div class="legend-item"><span class="dot offline"></span> Offline</div>
        </div>
      </div>
    </div>

    <div
        class="resize-handle right-handle"
        @mousedown="startResizeRight"
        v-if="selectedDevice"
    ></div>

    <!-- 右侧设备详情面板 -->
    <transition name="slide-right">
      <div
          v-if="selectedDevice"
          class="detail-panel"
          :style="{ width: rightPanelWidth + 'px' }"
      >
        <div class="panel-header">
          <el-icon><InfoFilled /></el-icon>
          <span>Device Details</span>
          <el-button
              :icon="Close"
              circle
              size="small"
              class="toggle-btn"
              @click="clearSelection"
          />
        </div>

        <!-- 设备大图 -->
        <div class="detail-section">
          <div class="device-hero-image">
            <el-image
                :src="selectedDevice.imageUrl"
                fit="contain"
                class="hero-image"
                :preview-src-list="[selectedDevice.imageUrl]"
                preview-teleported
                :initial-index="0"
            >
              <template #error>
                <div class="image-fallback large">
                  <el-icon :size="64"><Cpu /></el-icon>
                  <span>No Image Available</span>
                </div>
              </template>
            </el-image>
            <span class="image-hint">Click to preview full size</span>
          </div>
        </div>

        <!-- 基本信息 -->
        <div class="detail-section">
          <h4 class="section-title">
            <el-icon><Document /></el-icon>
            Basic Information
          </h4>
          <div class="info-grid">
            <div class="info-item">
              <label>Name</label>
              <span>{{ selectedDevice.name }}</span>
            </div>
            <div class="info-item">
              <label>Model</label>
              <span>{{ selectedDevice.model }}</span>
            </div>
            <div class="info-item">
              <label>Serial Number</label>
              <span class="mono">{{ selectedDevice.serialNumber }}</span>
            </div>
            <div class="info-item">
              <label>Manufacturer</label>
              <span>{{ selectedDevice.manufacturer }}</span>
            </div>
            <div class="info-item">
              <label>Status</label>
              <el-tag :type="getStatusType(selectedDevice.status)" size="small" effect="dark">
                {{ selectedDevice.status.toUpperCase() }}
              </el-tag>
            </div>
            <div class="info-item">
              <label>Installation</label>
              <span>{{ selectedDevice.installationDate }}</span>
            </div>
            <div class="info-item">
              <label>Last Maintenance</label>
              <span>{{ selectedDevice.lastMaintenance }}</span>
            </div>
            <div class="info-item">
              <label>Next Maintenance</label>
              <span :class="{ 'overdue': isMaintenanceOverdue }">
                {{ selectedDevice.nextMaintenance }}
                <el-tag v-if="isMaintenanceOverdue" type="danger" size="small">Overdue</el-tag>
              </span>
            </div>
          </div>
        </div>

        <!-- 实时指标 -->
        <div class="detail-section">
          <h4 class="section-title">
            <el-icon><Odometer /></el-icon>
            Real-time Metrics
            <el-tag size="small" type="info" class="refresh-tag">
              Updated {{ lastUpdateTime }}
            </el-tag>
          </h4>
          <div class="metrics-grid">
            <div
                v-for="metric in displayMetrics"
                :key="metric.key"
                class="metric-card"
                :class="{ 'metric-warning': metric.warning }"
            >
              <div class="metric-icon">
                <el-icon :size="18">
                  <component :is="metric.icon" />
                </el-icon>
              </div>
              <div class="metric-info">
                <span class="metric-value">
                  {{ metric.value }}
                  <span class="metric-unit">{{ metric.unit }}</span>
                </span>
                <span class="metric-label">{{ metric.label }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- ===== Trend Analysis Chart ===== -->
        <div class="detail-section">
          <h4 class="section-title">
            <el-icon><TrendCharts /></el-icon>
            Trend Analysis
            <span class="chart-subtitle">Last 24 Hours</span>
          </h4>
          <div ref="trendChartRef" class="chart-container trend-chart"></div>
        </div>

        <!-- 操作按钮 -->
        <div class="detail-actions">
          <el-button type="primary" :icon="Switch" @click="handleDeviceControl(selectedDevice)">
            Control
          </el-button>
          <el-button type="warning" :icon="Tools" @click="handleQuickRepair">
            Quick Repair
          </el-button>
          <el-button :icon="Download" @click="exportDeviceData">
            Export Data
          </el-button>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  Connection, ArrowLeft, Search, OfficeBuilding, Cpu, Grid, List,
  View, Loading, InfoFilled, Close, Document, Odometer, TrendCharts,
  Switch, Tools, Download, DataAnalysis, ColdDrink, Sunny, Lock,
  Bell, MagicStick
} from '@element-plus/icons-vue'

// ==================== Type Definitions ====================
interface DeviceMetrics {
  temperature: number
  humidity: number
  power: number
  energy: number
  uptime: number
  efficiency: number
  pressure?: number
  flowRate?: number
  co2Level?: number
  noiseLevel?: number
  vibration?: number
}

interface DeviceNode {
  id: string
  name: string
  type: 'device'
  status: 'online' | 'offline' | 'warning' | 'error'
  model: string
  manufacturer: string
  serialNumber: string
  systemType: string
  imageUrl: string
  metrics: DeviceMetrics
  lastMaintenance: string
  nextMaintenance: string
  installationDate: string
  position: { x: number; y: number; z: number }
}

interface SystemNode {
  id: string
  name: string
  label: string
  type: 'system'
  systemType: string
  status: 'online' | 'offline' | 'warning' | 'error'
  children: DeviceNode[]
}

interface AreaNode {
  id: string
  name: string
  label: string
  type: 'area'
  floor: string
  children: SystemNode[]
}

// ==================== Helper to create devices ====================
const createHVACDevice = (
    id: string, name: string, model: string, manufacturer: string,
    serial: string, status: DeviceNode['status'], imageIdx: number,
    metrics: Partial<DeviceMetrics>, maintenance: { last: string; next: string },
    install: string, pos: { x: number; y: number; z: number }
): DeviceNode => {
  const hvacImages = [
    'https://images.unsplash.com/photo-1585771724684-38269d6639fd?w=400&h=300&fit=crop',
    'https://images.unsplash.com/photo-1594322436404-5a0526db4d13?w=400&h=300&fit=crop',
    'https://images.unsplash.com/photo-1621905252507-b35492cc74b4?w=400&h=300&fit=crop',
    'https://images.unsplash.com/photo-1590959651373-a3db0f38c3d3?w=400&h=300&fit=crop',
    'https://images.unsplash.com/photo-1631545806604-3ba9d8e9a3f5?w=400&h=300&fit=crop'
  ]
  return {
    id, name, type: 'device', status, model, manufacturer,
    serialNumber: serial, systemType: 'hvac',
    imageUrl: hvacImages[imageIdx % hvacImages.length],
    metrics: {
      temperature: metrics.temperature ?? 24,
      humidity: metrics.humidity ?? 55,
      power: metrics.power ?? 10,
      energy: metrics.energy ?? 10000,
      uptime: metrics.uptime ?? 8760,
      efficiency: metrics.efficiency ?? 90,
      pressure: metrics.pressure,
      flowRate: metrics.flowRate,
      noiseLevel: metrics.noiseLevel,
      vibration: metrics.vibration
    },
    lastMaintenance: maintenance.last,
    nextMaintenance: maintenance.next,
    installationDate: install,
    position: pos
  }
}

const createLightingDevice = (
    id: string, name: string, model: string, manufacturer: string,
    serial: string, status: DeviceNode['status'], imageIdx: number,
    metrics: Partial<DeviceMetrics>, maintenance: { last: string; next: string },
    install: string, pos: { x: number; y: number; z: number }
): DeviceNode => {
  const lightingImages = [
    'https://images.unsplash.com/photo-1565814636199-ae8133055c1c?w=400&h=300&fit=crop',
    'https://images.unsplash.com/photo-1517999144091-3d9dca6d1e43?w=400&h=300&fit=crop',
    'https://images.unsplash.com/photo-1507477338202-487c5f0ed3d3?w=400&h=300&fit=crop'
  ]
  return {
    id, name, type: 'device', status, model, manufacturer,
    serialNumber: serial, systemType: 'lighting',
    imageUrl: lightingImages[imageIdx % lightingImages.length],
    metrics: {
      temperature: metrics.temperature ?? 27,
      humidity: metrics.humidity ?? 45,
      power: metrics.power ?? 3,
      energy: metrics.energy ?? 2500,
      uptime: metrics.uptime ?? 8760,
      efficiency: metrics.efficiency ?? 95
    },
    lastMaintenance: maintenance.last,
    nextMaintenance: maintenance.next,
    installationDate: install,
    position: pos
  }
}

const createSASDevice = (
    id: string, name: string, model: string, manufacturer: string,
    serial: string, status: DeviceNode['status'], imageIdx: number,
    metrics: Partial<DeviceMetrics>, maintenance: { last: string; next: string },
    install: string, pos: { x: number; y: number; z: number }
): DeviceNode => {
  const sasImages = [
    'https://images.unsplash.com/photo-1558002038-1055907df827?w=400&h=300&fit=crop',
    'https://images.unsplash.com/photo-1614064641938-3bbee52942c7?w=400&h=300&fit=crop'
  ]
  return {
    id, name, type: 'device', status, model, manufacturer,
    serialNumber: serial, systemType: 'sas',
    imageUrl: sasImages[imageIdx % sasImages.length],
    metrics: {
      temperature: metrics.temperature ?? 35,
      humidity: metrics.humidity ?? 40,
      power: metrics.power ?? 0.5,
      energy: metrics.energy ?? 400,
      uptime: metrics.uptime ?? 8760,
      efficiency: metrics.efficiency ?? 99
    },
    lastMaintenance: maintenance.last,
    nextMaintenance: maintenance.next,
    installationDate: install,
    position: pos
  }
}

const createFASDevice = (
    id: string, name: string, model: string, manufacturer: string,
    serial: string, status: DeviceNode['status'], imageIdx: number,
    metrics: Partial<DeviceMetrics>, maintenance: { last: string; next: string },
    install: string, pos: { x: number; y: number; z: number }
): DeviceNode => {
  const fasImages = [
    'https://images.unsplash.com/photo-1582139329536-e7284fece509?w=400&h=300&fit=crop',
    'https://images.unsplash.com/photo-1558618666-fcd25c85f82e?w=400&h=300&fit=crop'
  ]
  return {
    id, name, type: 'device', status, model, manufacturer,
    serialNumber: serial, systemType: 'fas',
    imageUrl: fasImages[imageIdx % fasImages.length],
    metrics: {
      temperature: metrics.temperature ?? 22,
      humidity: metrics.humidity ?? 65,
      power: metrics.power ?? 0.3,
      energy: metrics.energy ?? 240,
      uptime: metrics.uptime ?? 8760,
      efficiency: metrics.efficiency ?? 98,
      co2Level: metrics.co2Level,
      noiseLevel: metrics.noiseLevel
    },
    lastMaintenance: maintenance.last,
    nextMaintenance: maintenance.next,
    installationDate: install,
    position: pos
  }
}

const createPlumbingDevice = (
    id: string, name: string, model: string, manufacturer: string,
    serial: string, status: DeviceNode['status'], imageIdx: number,
    metrics: Partial<DeviceMetrics>, maintenance: { last: string; next: string },
    install: string, pos: { x: number; y: number; z: number }
): DeviceNode => {
  const plumbingImages = [
    'https://images.unsplash.com/photo-1604004555489-723a93d6ce74?w=400&h=300&fit=crop',
    'https://images.unsplash.com/photo-1624969862644-791f3dc98927?w=400&h=300&fit=crop'
  ]
  return {
    id, name, type: 'device', status, model, manufacturer,
    serialNumber: serial, systemType: 'plumbing',
    imageUrl: plumbingImages[imageIdx % plumbingImages.length],
    metrics: {
      temperature: metrics.temperature ?? 30,
      humidity: metrics.humidity ?? 60,
      power: metrics.power ?? 7,
      energy: metrics.energy ?? 5500,
      uptime: metrics.uptime ?? 8000,
      efficiency: metrics.efficiency ?? 91,
      pressure: metrics.pressure,
      flowRate: metrics.flowRate
    },
    lastMaintenance: maintenance.last,
    nextMaintenance: maintenance.next,
    installationDate: install,
    position: pos
  }
}

// ==================== Mock Data - All floors with all systems ====================
const generateMockData = (): AreaNode[] => {
  return [
    // ======== B2 - Basement 2 ========
    {
      id: 'area-b2',
      name: 'Basement B2',
      label: 'Basement B2',
      type: 'area',
      floor: 'B2',
      children: [
        {
          id: 'sys-hvac-b2', name: 'HVAC System', label: 'HVAC System',
          type: 'system', systemType: 'hvac', status: 'online',
          children: [
            createHVACDevice('dev-ahu-b2-01', 'AHU-B2-01 Air Handler', 'Carrier 39G', 'Carrier', 'CA-2024-B201', 'online', 0,
                { temperature: 23.0, humidity: 50, power: 18.5, energy: 15200, efficiency: 94, pressure: 280, flowRate: 15000, noiseLevel: 62 },
                { last: '2026-04-15', next: '2026-07-15' }, '2024-01-10', { x: 10, y: -6, z: 4 }),
            createHVACDevice('dev-fcu-b2-01', 'FCU-B2-01 Fan Coil', 'Daikin FXMQ', 'Daikin', 'DK-2024-B201', 'online', 1,
                { temperature: 22.5, humidity: 48, power: 6.8, energy: 5400, efficiency: 91, pressure: 160, flowRate: 1800, noiseLevel: 38 },
                { last: '2026-05-01', next: '2026-08-01' }, '2024-02-15', { x: 15, y: -5.5, z: 6 })
          ]
        },
        {
          id: 'sys-lighting-b2', name: 'Lighting System', label: 'Lighting System',
          type: 'system', systemType: 'lighting', status: 'online',
          children: [
            createLightingDevice('dev-light-b2-01', 'LIGHT-B2-01 Smart Controller', 'Philips Dynalite', 'Philips', 'PH-2024-B201', 'online', 0,
                { temperature: 26.5, humidity: 42, power: 4.2, energy: 3200, efficiency: 96 },
                { last: '2026-05-15', next: '2026-08-15' }, '2024-01-20', { x: 8, y: -5, z: 8 })
          ]
        },
        {
          id: 'sys-fas-b2', name: 'Fire Alarm System', label: 'Fire Alarm System',
          type: 'system', systemType: 'fas', status: 'online',
          children: [
            createFASDevice('dev-smoke-b2-01', 'SD-B2-01 Smoke Detector', 'Honeywell XLS', 'Honeywell', 'HW-2024-B201', 'online', 0,
                { temperature: 21.5, humidity: 62, power: 0.3, energy: 240, efficiency: 99, co2Level: 420, noiseLevel: 12 },
                { last: '2026-04-10', next: '2026-07-10' }, '2024-01-01', { x: 12, y: -5.8, z: 10 }),
            createFASDevice('dev-smoke-b2-02', 'SD-B2-02 Smoke Detector', 'Honeywell XLS', 'Honeywell', 'HW-2024-B202', 'online', 1,
                { temperature: 21.8, humidity: 63, power: 0.3, energy: 238, efficiency: 99, co2Level: 430, noiseLevel: 11 },
                { last: '2026-04-10', next: '2026-07-10' }, '2024-01-01', { x: 20, y: -5.8, z: 14 })
          ]
        },
        {
          id: 'sys-plumbing-b2', name: 'Plumbing System', label: 'Plumbing System',
          type: 'system', systemType: 'plumbing', status: 'warning',
          children: [
            createPlumbingDevice('dev-pump-b2-01', 'PUMP-B2-01 Sump Pump', 'Grundfos SE', 'Grundfos', 'GF-2024-B201', 'online', 0,
                { temperature: 32.0, humidity: 70, power: 11.0, energy: 8800, efficiency: 88, pressure: 380, flowRate: 60 },
                { last: '2026-03-20', next: '2026-06-20' }, '2023-12-15', { x: 5, y: -6.5, z: 12 }),
            createPlumbingDevice('dev-pump-b2-02', 'PUMP-B2-02 Booster Pump', 'Grundfos CR', 'Grundfos', 'GF-2024-B202', 'warning', 1,
                { temperature: 38.0, humidity: 72, power: 9.5, energy: 7600, efficiency: 76, pressure: 320, flowRate: 42, vibration: 3.8 },
                { last: '2024-02-28', next: '2026-04-28' }, '2023-11-20', { x: 5, y: -6.5, z: 14 })
          ]
        }
      ]
    },
    // ======== B1 - Basement 1 / Parking ========
    {
      id: 'area-b1',
      name: 'Parking B1',
      label: 'Parking B1',
      type: 'area',
      floor: 'B1',
      children: [
        {
          id: 'sys-hvac-b1', name: 'HVAC System', label: 'HVAC System',
          type: 'system', systemType: 'hvac', status: 'online',
          children: [
            createHVACDevice('dev-ahu-b1-01', 'AHU-B1-01 Ventilation Unit', 'Trane IntelliPak', 'Trane', 'TR-2024-B101', 'online', 3,
                { temperature: 25.0, humidity: 58, power: 20.0, energy: 16000, efficiency: 89, pressure: 260, flowRate: 18000, noiseLevel: 68 },
                { last: '2026-04-20', next: '2026-07-20' }, '2024-01-15', { x: 18, y: -3, z: 5 })
          ]
        },
        {
          id: 'sys-lighting-b1', name: 'Lighting System', label: 'Lighting System',
          type: 'system', systemType: 'lighting', status: 'online',
          children: [
            createLightingDevice('dev-light-b1-01', 'LIGHT-B1-01 Parking Control', 'Schneider KNX', 'Schneider Electric', 'SE-2024-B101', 'online', 1,
                { temperature: 28.0, humidity: 46, power: 5.5, energy: 4400, efficiency: 94 },
                { last: '2026-05-10', next: '2026-08-10' }, '2024-01-25', { x: 10, y: -2.5, z: 8 })
          ]
        },
        {
          id: 'sys-sas-b1', name: 'Security System', label: 'Security System',
          type: 'system', systemType: 'sas', status: 'online',
          children: [
            createSASDevice('dev-access-b1-01', 'ACS-B1-01 Gate Controller', 'HID VertX', 'HID Global', 'HD-2024-B101', 'online', 0,
                { temperature: 34.0, humidity: 42, power: 0.6, energy: 480, efficiency: 99 },
                { last: '2026-06-01', next: '2026-09-01' }, '2024-01-05', { x: 22, y: -2.8, z: 3 }),
            createSASDevice('dev-camera-b1-01', 'CAM-B1-01 PTZ Camera', 'Hikvision DS-2DE', 'Hikvision', 'HK-2024-B101', 'online', 1,
                { temperature: 36.0, humidity: 38, power: 1.2, energy: 960, efficiency: 98 },
                { last: '2026-05-20', next: '2026-08-20' }, '2024-02-01', { x: 24, y: -2.5, z: 5 })
          ]
        },
        {
          id: 'sys-fas-b1', name: 'Fire Alarm System', label: 'Fire Alarm System',
          type: 'system', systemType: 'fas', status: 'online',
          children: [
            createFASDevice('dev-smoke-b1-01', 'SD-B1-01 Smoke Detector', 'Honeywell XLS', 'Honeywell', 'HW-2024-B101', 'online', 1,
                { temperature: 22.2, humidity: 64, power: 0.3, energy: 240, efficiency: 98, co2Level: 480, noiseLevel: 14 },
                { last: '2026-04-10', next: '2026-07-10' }, '2024-01-01', { x: 8, y: -2.8, z: 10 })
          ]
        },
        {
          id: 'sys-plumbing-b1', name: 'Plumbing System', label: 'Plumbing System',
          type: 'system', systemType: 'plumbing', status: 'online',
          children: [
            createPlumbingDevice('dev-pump-b1-01', 'PUMP-B1-01 Drainage Pump', 'Grundfos CRE', 'Grundfos', 'GF-2024-B101', 'online', 0,
                { temperature: 31.0, humidity: 65, power: 8.0, energy: 6400, efficiency: 90, pressure: 340, flowRate: 50 },
                { last: '2026-05-15', next: '2026-08-15' }, '2023-12-20', { x: 6, y: -3, z: 12 })
          ]
        }
      ]
    },
    // ======== 1F - Lobby ========
    {
      id: 'area-1f',
      name: 'Lobby 1F',
      label: 'Lobby 1F',
      type: 'area',
      floor: '1F',
      children: [
        {
          id: 'sys-hvac-1f', name: 'HVAC System', label: 'HVAC System',
          type: 'system', systemType: 'hvac', status: 'online',
          children: [
            createHVACDevice('dev-ahu-1f-01', 'AHU-1F-01 Air Handler', 'Carrier 39G', 'Carrier', 'CA-2024-1F01', 'online', 0,
                { temperature: 23.5, humidity: 52, power: 12.8, energy: 10240, efficiency: 93, pressure: 245, flowRate: 11500, noiseLevel: 58 },
                { last: '2026-04-20', next: '2026-07-20' }, '2024-01-15', { x: 5, y: 2.5, z: 3 }),
            createHVACDevice('dev-fcu-1f-01', 'FCU-1F-01 Fan Coil', 'Daikin FXMQ', 'Daikin', 'DK-2024-1F01', 'warning', 1,
                { temperature: 25.8, humidity: 58, power: 8.2, energy: 6540, efficiency: 87, pressure: 180, flowRate: 2200, noiseLevel: 42 },
                { last: '2024-03-10', next: '2026-05-10' }, '2023-06-20', { x: 8, y: 2.8, z: 5 }),
            createHVACDevice('dev-vav-1f-01', 'VAV-1F-01 VAV Terminal', 'Johnson Controls VAV', 'Johnson Controls', 'JC-2024-1F01', 'online', 2,
                { temperature: 22.0, humidity: 50, power: 1.5, energy: 1200, efficiency: 96, pressure: 120, flowRate: 800 },
                { last: '2026-04-25', next: '2026-07-25' }, '2024-02-01', { x: 12, y: 2.5, z: 3 })
          ]
        },
        {
          id: 'sys-lighting-1f', name: 'Lighting System', label: 'Lighting System',
          type: 'system', systemType: 'lighting', status: 'online',
          children: [
            createLightingDevice('dev-light-1f-01', 'LIGHT-1F-01 Smart Control', 'Philips Dynalite', 'Philips', 'PH-2024-1F01', 'online', 0,
                { temperature: 28.0, humidity: 45, power: 3.5, energy: 2800, efficiency: 95 },
                { last: '2026-05-15', next: '2026-08-15' }, '2024-01-20', { x: 4, y: 3.2, z: 7 }),
            createLightingDevice('dev-light-1f-02', 'LIGHT-1F-02 Emergency Light', 'Schneider KNX', 'Schneider Electric', 'SE-2024-1F02', 'online', 1,
                { temperature: 27.0, humidity: 44, power: 1.2, energy: 960, efficiency: 98 },
                { last: '2026-05-20', next: '2026-08-20' }, '2024-01-25', { x: 16, y: 3.2, z: 7 })
          ]
        },
        {
          id: 'sys-sas-1f', name: 'Security System', label: 'Security System',
          type: 'system', systemType: 'sas', status: 'online',
          children: [
            createSASDevice('dev-access-1f-01', 'ACS-1F-01 Access Controller', 'HID VertX', 'HID Global', 'HD-2024-1F01', 'online', 0,
                { temperature: 35.0, humidity: 40, power: 0.5, energy: 400, efficiency: 99 },
                { last: '2026-06-01', next: '2026-09-01' }, '2024-01-05', { x: 3, y: 3.0, z: 2 }),
            createSASDevice('dev-camera-1f-01', 'CAM-1F-01 Dome Camera', 'Hikvision DS-2CD', 'Hikvision', 'HK-2024-1F01', 'online', 1,
                { temperature: 36.5, humidity: 38, power: 0.8, energy: 640, efficiency: 98 },
                { last: '2026-05-25', next: '2026-08-25' }, '2024-02-05', { x: 20, y: 3.2, z: 2 })
          ]
        },
        {
          id: 'sys-fas-1f', name: 'Fire Alarm System', label: 'Fire Alarm System',
          type: 'system', systemType: 'fas', status: 'online',
          children: [
            createFASDevice('dev-smoke-1f-01', 'SD-1F-01 Smoke Detector', 'Honeywell XLS', 'Honeywell', 'HW-2024-1F01', 'online', 0,
                { temperature: 22.0, humidity: 55, power: 0.3, energy: 240, efficiency: 99, co2Level: 440, noiseLevel: 13 },
                { last: '2026-04-10', next: '2026-07-10' }, '2024-01-01', { x: 10, y: 3.5, z: 10 }),
            createFASDevice('dev-heat-1f-01', 'HD-1F-01 Heat Detector', 'Siemens Cerberus', 'Siemens', 'SM-2024-1F01', 'online', 1,
                { temperature: 23.0, humidity: 54, power: 0.2, energy: 160, efficiency: 99, noiseLevel: 10 },
                { last: '2026-04-12', next: '2026-07-12' }, '2024-01-02', { x: 18, y: 3.5, z: 10 })
          ]
        }
      ]
    },
    // ======== 2F - Office ========
    {
      id: 'area-2f',
      name: 'Office 2F',
      label: 'Office 2F',
      type: 'area',
      floor: '2F',
      children: [
        {
          id: 'sys-hvac-2f', name: 'HVAC System', label: 'HVAC System',
          type: 'system', systemType: 'hvac', status: 'warning',
          children: [
            createHVACDevice('dev-ahu-2f-01', 'AHU-2F-01 Air Handler', 'Trane IntelliPak', 'Trane', 'TR-2024-2F01', 'error', 3,
                { temperature: 31.2, humidity: 72, power: 22.5, energy: 18500, efficiency: 72, pressure: 195, flowRate: 9800, noiseLevel: 78, vibration: 4.2 },
                { last: '2024-02-28', next: '2026-04-28' }, '2023-08-10', { x: 15, y: 5, z: 4 }),
            createHVACDevice('dev-fcu-2f-01', 'FCU-2F-01 Fan Coil', 'Daikin FXMQ', 'Daikin', 'DK-2024-2F01', 'online', 1,
                { temperature: 24.0, humidity: 55, power: 7.0, energy: 5600, efficiency: 90, pressure: 170, flowRate: 2000, noiseLevel: 40 },
                { last: '2026-05-05', next: '2026-08-05' }, '2024-02-10', { x: 20, y: 5.2, z: 6 })
          ]
        },
        {
          id: 'sys-lighting-2f', name: 'Lighting System', label: 'Lighting System',
          type: 'system', systemType: 'lighting', status: 'online',
          children: [
            createLightingDevice('dev-light-2f-01', 'LIGHT-2F-01 Office Control', 'Lutron Quantum', 'Lutron', 'LT-2024-2F01', 'online', 2,
                { temperature: 27.5, humidity: 43, power: 2.8, energy: 2240, efficiency: 97 },
                { last: '2026-05-18', next: '2026-08-18' }, '2024-01-22', { x: 8, y: 5.5, z: 8 })
          ]
        },
        {
          id: 'sys-sas-2f', name: 'Security System', label: 'Security System',
          type: 'system', systemType: 'sas', status: 'online',
          children: [
            createSASDevice('dev-access-2f-01', 'ACS-2F-01 Access Controller', 'HID VertX', 'HID Global', 'HD-2024-2F01', 'online', 0,
                { temperature: 34.5, humidity: 41, power: 0.5, energy: 400, efficiency: 99 },
                { last: '2026-06-05', next: '2026-09-05' }, '2024-01-08', { x: 2, y: 5.2, z: 2 }),
            createSASDevice('dev-camera-2f-01', 'CAM-2F-01 Bullet Camera', 'Hikvision DS-2CD', 'Hikvision', 'HK-2024-2F01', 'warning', 0,
                { temperature: 40.0, humidity: 35, power: 1.0, energy: 800, efficiency: 95 },
                { last: '2026-05-22', next: '2026-08-22' }, '2024-02-08', { x: 25, y: 5.5, z: 2 })
          ]
        },
        {
          id: 'sys-fas-2f', name: 'Fire Alarm System', label: 'Fire Alarm System',
          type: 'system', systemType: 'fas', status: 'online',
          children: [
            createFASDevice('dev-smoke-2f-01', 'SD-2F-01 Smoke Detector', 'Siemens Cerberus', 'Siemens', 'SM-2024-2F01', 'online', 0,
                { temperature: 22.5, humidity: 53, power: 0.2, energy: 160, efficiency: 99, co2Level: 460, noiseLevel: 11 },
                { last: '2026-04-15', next: '2026-07-15' }, '2024-01-03', { x: 10, y: 5.8, z: 10 })
          ]
        },
        {
          id: 'sys-plumbing-2f', name: 'Plumbing System', label: 'Plumbing System',
          type: 'system', systemType: 'plumbing', status: 'online',
          children: [
            createPlumbingDevice('dev-pump-2f-01', 'PUMP-2F-01 Water Supply', 'Grundfos CME', 'Grundfos', 'GF-2024-2F01', 'online', 0,
                { temperature: 30.5, humidity: 58, power: 5.5, energy: 4400, efficiency: 93, pressure: 300, flowRate: 30 },
                { last: '2026-05-12', next: '2026-08-12' }, '2023-12-18', { x: 4, y: 5.0, z: 12 })
          ]
        }
      ]
    },
    // ======== 3F - Executive Floor ========
    {
      id: 'area-3f',
      name: 'Executive 3F',
      label: 'Executive 3F',
      type: 'area',
      floor: '3F',
      children: [
        {
          id: 'sys-hvac-3f', name: 'HVAC System', label: 'HVAC System',
          type: 'system', systemType: 'hvac', status: 'online',
          children: [
            createHVACDevice('dev-ahu-3f-01', 'AHU-3F-01 Precision AC', 'Stulz CyberAir', 'Stulz', 'ST-2024-3F01', 'online', 4,
                { temperature: 22.0, humidity: 48, power: 25.0, energy: 20000, efficiency: 95, pressure: 300, flowRate: 20000, noiseLevel: 55 },
                { last: '2026-04-30', next: '2026-07-30' }, '2024-01-05', { x: 10, y: 8, z: 5 }),
            createHVACDevice('dev-vav-3f-01', 'VAV-3F-01 VAV Terminal', 'Johnson Controls VAV', 'Johnson Controls', 'JC-2024-3F01', 'online', 2,
                { temperature: 21.5, humidity: 47, power: 1.2, energy: 960, efficiency: 97, pressure: 110, flowRate: 700 },
                { last: '2026-05-02', next: '2026-08-02' }, '2024-02-05', { x: 15, y: 8, z: 7 })
          ]
        },
        {
          id: 'sys-lighting-3f', name: 'Lighting System', label: 'Lighting System',
          type: 'system', systemType: 'lighting', status: 'online',
          children: [
            createLightingDevice('dev-light-3f-01', 'LIGHT-3F-01 Exec Control', 'Lutron HomeWorks', 'Lutron', 'LT-2024-3F01', 'online', 2,
                { temperature: 26.0, humidity: 42, power: 2.0, energy: 1600, efficiency: 98 },
                { last: '2026-05-20', next: '2026-08-20' }, '2024-01-30', { x: 6, y: 8.5, z: 9 })
          ]
        },
        {
          id: 'sys-sas-3f', name: 'Security System', label: 'Security System',
          type: 'system', systemType: 'sas', status: 'online',
          children: [
            createSASDevice('dev-access-3f-01', 'ACS-3F-01 Biometric Access', 'HID Signo', 'HID Global', 'HD-2024-3F01', 'online', 0,
                { temperature: 33.0, humidity: 39, power: 0.8, energy: 640, efficiency: 99 },
                { last: '2026-06-10', next: '2026-09-10' }, '2024-01-10', { x: 2, y: 8.2, z: 2 }),
            createSASDevice('dev-camera-3f-01', 'CAM-3F-01 4K Camera', 'Axis P1448', 'Axis Communications', 'AX-2024-3F01', 'online', 1,
                { temperature: 35.0, humidity: 37, power: 1.5, energy: 1200, efficiency: 97 },
                { last: '2026-05-28', next: '2026-08-28' }, '2024-02-10', { x: 24, y: 8.5, z: 2 })
          ]
        },
        {
          id: 'sys-fas-3f', name: 'Fire Alarm System', label: 'Fire Alarm System',
          type: 'system', systemType: 'fas', status: 'online',
          children: [
            createFASDevice('dev-smoke-3f-01', 'SD-3F-01 Smoke Detector', 'Siemens Cerberus', 'Siemens', 'SM-2024-3F01', 'online', 0,
                { temperature: 21.8, humidity: 52, power: 0.2, energy: 160, efficiency: 99, co2Level: 450, noiseLevel: 10 },
                { last: '2026-04-18', next: '2026-07-18' }, '2024-01-05', { x: 8, y: 8.8, z: 11 })
          ]
        },
        {
          id: 'sys-plumbing-3f', name: 'Plumbing System', label: 'Plumbing System',
          type: 'system', systemType: 'plumbing', status: 'online',
          children: [
            createPlumbingDevice('dev-pump-3f-01', 'PUMP-3F-01 Hot Water Pump', 'Grundfos UPS', 'Grundfos', 'GF-2024-3F01', 'online', 1,
                { temperature: 45.0, humidity: 55, power: 4.0, energy: 3200, efficiency: 92, pressure: 280, flowRate: 25 },
                { last: '2026-05-08', next: '2026-08-08' }, '2023-12-22', { x: 4, y: 8.0, z: 13 })
          ]
        }
      ]
    },
    // ======== Roof - Mechanical ========
    {
      id: 'area-roof',
      name: 'Roof Mechanical',
      label: 'Roof Mechanical',
      type: 'area',
      floor: 'RF',
      children: [
        {
          id: 'sys-hvac-roof', name: 'HVAC System', label: 'HVAC System',
          type: 'system', systemType: 'hvac', status: 'online',
          children: [
            createHVACDevice('dev-chiller-roof-01', 'CH-RF-01 Chiller', 'Carrier AquaEdge', 'Carrier', 'CA-2024-RF01', 'online', 4,
                { temperature: 35.0, humidity: 75, power: 150.0, energy: 120000, efficiency: 88, pressure: 450, flowRate: 80000, noiseLevel: 85 },
                { last: '2026-04-01', next: '2026-07-01' }, '2024-01-01', { x: 10, y: 12, z: 5 }),
            createHVACDevice('dev-cooling-roof-01', 'CT-RF-01 Cooling Tower', 'BAC 3000', 'Baltimore Aircoil', 'BA-2024-RF01', 'online', 0,
                { temperature: 38.0, humidity: 80, power: 45.0, energy: 36000, efficiency: 85, pressure: 200, flowRate: 60000, noiseLevel: 90 },
                { last: '2026-04-05', next: '2026-07-05' }, '2024-01-01', { x: 20, y: 12, z: 5 })
          ]
        },
        {
          id: 'sys-fas-roof', name: 'Fire Alarm System', label: 'Fire Alarm System',
          type: 'system', systemType: 'fas', status: 'online',
          children: [
            createFASDevice('dev-smoke-roof-01', 'SD-RF-01 Smoke Detector', 'Honeywell XLS', 'Honeywell', 'HW-2024-RF01', 'online', 1,
                { temperature: 30.0, humidity: 70, power: 0.3, energy: 240, efficiency: 98, co2Level: 500, noiseLevel: 18 },
                { last: '2026-04-20', next: '2026-07-20' }, '2024-01-05', { x: 15, y: 12.5, z: 12 })
          ]
        },
        {
          id: 'sys-plumbing-roof', name: 'Plumbing System', label: 'Plumbing System',
          type: 'system', systemType: 'plumbing', status: 'online',
          children: [
            createPlumbingDevice('dev-tank-roof-01', 'TANK-RF-01 Water Tank', 'GRP Modular', 'ZCL Composites', 'ZC-2024-RF01', 'online', 0,
                { temperature: 28.0, humidity: 75, power: 2.0, energy: 1600, efficiency: 95, pressure: 150, flowRate: 100 },
                { last: '2026-05-01', next: '2026-08-01' }, '2024-01-01', { x: 5, y: 12, z: 15 })
          ]
        }
      ]
    }
  ]
}

// ==================== Generate Trend Data ====================
const generateTrendData = (device: DeviceNode) => {
  const now = new Date()
  const hours: string[] = []
  for (let i = 23; i >= 0; i--) {
    const d = new Date(now.getTime() - i * 3600000)
    hours.push(`${String(d.getHours()).padStart(2, '0')}:00`)
  }
  const baseTemp = device.metrics.temperature || 24
  const basePower = device.metrics.power || 10
  const baseHumidity = device.metrics.humidity || 50
  const baseEfficiency = device.metrics.efficiency || 90

  return {
    xAxis: hours,
    temperature: hours.map((_, i) => {
      const hourEffect = Math.sin(i * 0.5) * 3
      const random = (Math.random() - 0.5) * 2
      return +(baseTemp + hourEffect + random).toFixed(1)
    }),
    power: hours.map((_, i) => {
      // Power peaks during business hours (8-18)
      const hour = i
      const businessEffect = (hour >= 8 && hour <= 18) ? 5 : 0
      const random = (Math.random() - 0.5) * 3
      return +(basePower + businessEffect + random).toFixed(1)
    }),
    humidity: hours.map((_, i) => {
      const hourEffect = Math.cos(i * 0.4) * 6
      const random = (Math.random() - 0.5) * 4
      return Math.round(baseHumidity + hourEffect + random)
    }),
    efficiency: hours.map((_, i) => {
      const random = (Math.random() - 0.5) * 5
      const val = baseEfficiency + random
      return Math.min(100, Math.max(60, +val.toFixed(1)))
    })
  }
}

// ==================== Reactive State ====================
const searchKeyword = ref('')
const viewMode = ref<'grid' | 'list'>('grid')
const currentFloor = ref('All Floors')
const showHeatmap = ref(false)
const selectedDevice = ref<DeviceNode | null>(null)
const selectedSystem = ref<SystemNode | null>(null)
const hoveredDevice = ref<DeviceNode | null>(null)
const lastUpdateTime = ref('')

const leftPanelWidth = ref(300)
const rightPanelWidth = ref(380)
const isResizingLeft = ref(false)
const isResizingRight = ref(false)

const treeRef = ref()
const trendChartRef = ref<HTMLElement>()
let trendChartInstance: echarts.ECharts | null = null

const topologyData = ref<AreaNode[]>(generateMockData())

// ==================== Computed ====================
const floors = computed(() => {
  const floorSet = new Set<string>()
  topologyData.value.forEach(area => floorSet.add(area.floor))
  return ['All Floors', ...Array.from(floorSet).sort()]
})

const filteredTreeData = computed(() => {
  let data = topologyData.value
  if (currentFloor.value !== 'All Floors') {
    data = data.filter(area => area.floor === currentFloor.value)
  }
  if (searchKeyword.value) {
    return filterTreeData(data, searchKeyword.value.toLowerCase())
  }
  return data
})

const displayDevices = computed(() => {
  if (selectedSystem.value) {
    return selectedSystem.value.children || []
  }
  if (selectedDevice.value) {
    return [selectedDevice.value]
  }
  const devices: DeviceNode[] = []
  const currentData = currentFloor.value === 'All Floors'
      ? topologyData.value
      : topologyData.value.filter(area => area.floor === currentFloor.value)
  currentData.forEach(area => {
    area.children?.forEach(system => {
      system.children?.forEach(device => devices.push(device))
    })
  })
  return devices
})

const stats = computed(() => {
  let totalAreas = topologyData.value.length
  let totalSystems = 0
  let totalDevices = 0
  let onlineDevices = 0
  topologyData.value.forEach(area => {
    area.children?.forEach(system => {
      totalSystems++
      system.children?.forEach(device => {
        totalDevices++
        if (device.status === 'online') onlineDevices++
      })
    })
  })
  return { totalAreas, totalSystems, totalDevices, onlineDevices }
})

const defaultExpandedKeys = computed(() => {
  const keys: string[] = []
  topologyData.value.forEach(area => {
    keys.push(area.id)
    area.children?.forEach(system => keys.push(system.id))
  })
  return keys
})

const treeProps = { children: 'children', label: 'label' }

const displayMetrics = computed(() => {
  if (!selectedDevice.value) return []
  const m = selectedDevice.value.metrics
  return [
    { key: 'temperature', label: 'Temperature', value: m.temperature, unit: '°C', icon: ColdDrink, warning: m.temperature > 28 },
    { key: 'humidity', label: 'Humidity', value: m.humidity, unit: '%', icon: Sunny, warning: m.humidity > 65 },
    { key: 'power', label: 'Power', value: m.power, unit: 'kW', icon: Odometer, warning: m.power > 20 },
    { key: 'energy', label: 'Energy', value: m.energy.toLocaleString(), unit: 'kWh', icon: TrendCharts, warning: false },
    { key: 'efficiency', label: 'Efficiency', value: m.efficiency, unit: '%', icon: MagicStick, warning: m.efficiency < 80 },
    { key: 'uptime', label: 'Uptime', value: Math.floor(m.uptime / 24), unit: 'days', icon: Switch, warning: false }
  ]
})

const isMaintenanceOverdue = computed(() => {
  if (!selectedDevice.value) return false
  return new Date(selectedDevice.value.nextMaintenance) < new Date()
})

// ==================== Methods ====================
const getSystemIcon = (systemType: string) => {
  const icons: Record<string, any> = {
    hvac: ColdDrink, lighting: Sunny, sas: Lock, fas: Bell,
    plumbing: MagicStick, power: Odometer
  }
  return icons[systemType] || Cpu
}

const getStatusType = (status: string) => {
  const types: Record<string, string> = {
    online: 'success', offline: 'info', warning: 'warning', error: 'danger'
  }
  return types[status] || 'info'
}

const getChildrenCount = (data: any) => data.children?.length || 0

const getHeatmapOpacity = (device: DeviceNode) => {
  if (device.status === 'error') return 0.5
  if (device.status === 'warning') return 0.3
  if (device.metrics.temperature > 28) return 0.4
  if (device.metrics.power > 20) return 0.35
  return 0.1
}

const tableRowClassName = ({ row }: { row: DeviceNode }) => {
  return `row-${row.status}`
}

const filterTreeData = (data: AreaNode[], keyword: string): AreaNode[] => {
  return data.reduce((acc: AreaNode[], area) => {
    const matchedArea = area.name.toLowerCase().includes(keyword)
    const filteredSystems = area.children?.reduce((sysAcc: SystemNode[], system) => {
      const matchedSystem = system.name.toLowerCase().includes(keyword)
      const filteredDevices = system.children?.filter(
          device => device.name.toLowerCase().includes(keyword) ||
              device.model.toLowerCase().includes(keyword)
      ) || []
      if (matchedSystem || filteredDevices.length > 0) {
        sysAcc.push({ ...system, children: matchedSystem ? system.children : filteredDevices })
      }
      return sysAcc
    }, []) || []
    if (matchedArea || filteredSystems.length > 0) {
      acc.push({ ...area, children: matchedArea ? area.children : filteredSystems })
    }
    return acc
  }, [])
}

const filterNode = (value: string, data: any) => {
  if (!value) return true
  return data.name?.toLowerCase().includes(value.toLowerCase()) ||
      data.label?.toLowerCase().includes(value.toLowerCase())
}

const handleNodeClick = (data: any) => {
  if (data.type === 'device') {
    selectedDevice.value = data as DeviceNode
    selectedSystem.value = null
    nextTick(() => {
      initTrendChart()
    })
  } else if (data.type === 'system') {
    selectedSystem.value = data as SystemNode
    selectedDevice.value = null
    destroyChart()
  } else {
    selectedSystem.value = null
    selectedDevice.value = null
    destroyChart()
  }
}

const clearSelection = () => {
  selectedDevice.value = null
  selectedSystem.value = null
  destroyChart()
}

const destroyChart = () => {
  if (trendChartInstance) {
    trendChartInstance.dispose()
    trendChartInstance = null
  }
}

const toggleLeftPanel = () => {
  leftPanelWidth.value = leftPanelWidth.value > 0 ? 0 : 300
}

const startResizeLeft = (e: MouseEvent) => {
  isResizingLeft.value = true
  document.addEventListener('mousemove', handleResizeLeft)
  document.addEventListener('mouseup', stopResizeLeft)
}

const handleResizeLeft = (e: MouseEvent) => {
  if (!isResizingLeft.value) return
  leftPanelWidth.value = Math.max(200, Math.min(500, e.clientX))
}

const stopResizeLeft = () => {
  isResizingLeft.value = false
  document.removeEventListener('mousemove', handleResizeLeft)
  document.removeEventListener('mouseup', stopResizeLeft)
}

const startResizeRight = (e: MouseEvent) => {
  isResizingRight.value = true
  document.addEventListener('mousemove', handleResizeRight)
  document.addEventListener('mouseup', stopResizeRight)
}

const handleResizeRight = (e: MouseEvent) => {
  if (!isResizingRight.value) return
  rightPanelWidth.value = Math.max(280, Math.min(600, window.innerWidth - e.clientX))
}

const stopResizeRight = () => {
  isResizingRight.value = false
  document.removeEventListener('mousemove', handleResizeRight)
  document.removeEventListener('mouseup', stopResizeRight)
}

const changeFloor = (floor: string) => {
  ElMessage.success(`Switched to ${floor}`)
}

const handleDeviceControl = (device: DeviceNode) => {
  ElMessage.success(`Opening control panel for ${device.name}`)
}

const handleQuickRepair = () => {
  if (!selectedDevice.value) return
  ElMessage.warning(`Creating repair order for ${selectedDevice.value.name}`)
}

const exportDeviceData = () => {
  if (!selectedDevice.value) return
  ElMessage.success('Exporting device data to CSV...')
}

// ==================== ECharts Trend Chart ====================
const initTrendChart = () => {
  // Destroy previous instance
  destroyChart()

  if (!trendChartRef.value || !selectedDevice.value) return

  // Wait for DOM to be ready
  nextTick(() => {
    if (!trendChartRef.value || !selectedDevice.value) return

    try {
      trendChartInstance = echarts.init(trendChartRef.value, 'dark')
      const trendData = generateTrendData(selectedDevice.value)

      const option: echarts.EChartsOption = {
        backgroundColor: 'transparent',
        tooltip: {
          trigger: 'axis',
          backgroundColor: 'rgba(13, 25, 48, 0.95)',
          borderColor: 'rgba(64, 158, 255, 0.3)',
          textStyle: { color: '#e5eaf3', fontSize: 12 },
          axisPointer: {
            type: 'cross',
            crossStyle: { color: '#8899aa' },
            label: {
              backgroundColor: 'rgba(13, 25, 48, 0.9)',
              color: '#e5eaf3'
            }
          }
        },
        legend: {
          data: ['Temperature (°C)', 'Power (kW)', 'Humidity (%)', 'Efficiency (%)'],
          bottom: 0,
          textStyle: { color: '#8899aa', fontSize: 10 },
          icon: 'roundRect',
          itemWidth: 12,
          itemHeight: 6,
          itemGap: 12
        },
        grid: {
          top: 0,
          right: 0,
          bottom: 0,
          left: 0
        },
        xAxis: {
          type: 'category',
          data: trendData.xAxis,
          axisLine: { lineStyle: { color: 'rgba(255,255,255,0.15)' } },
          axisTick: { show: false },
          axisLabel: {
            color: '#8899aa',
            fontSize: 10,
            interval: 3
          },
          boundaryGap: false
        },
        yAxis: [
          {
            type: 'value',
            name: '°C / kW',
            nameTextStyle: { color: '#8899aa', fontSize: 10 },
            axisLine: { show: false },
            axisTick: { show: false },
            splitLine: { lineStyle: { color: 'rgba(255,255,255,0.06)' } },
            axisLabel: { color: '#8899aa', fontSize: 10 }
          },
          {
            type: 'value',
            name: '%',
            nameTextStyle: { color: '#8899aa', fontSize: 10 },
            axisLine: { show: false },
            axisTick: { show: false },
            splitLine: { show: false },
            axisLabel: { color: '#8899aa', fontSize: 10 },
            min: 0,
            max: 100
          }
        ],
        series: [
          {
            name: 'Temperature (°C)',
            type: 'line',
            data: trendData.temperature,
            smooth: true,
            symbol: 'circle',
            symbolSize: 4,
            lineStyle: { width: 2, color: '#f56c6c' },
            itemStyle: { color: '#f56c6c' },
            areaStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: 'rgba(245, 108, 108, 0.3)' },
                { offset: 1, color: 'rgba(245, 108, 108, 0.02)' }
              ])
            },
            markLine: {
              silent: true,
              symbol: 'none',
              data: [{ yAxis: 28, label: { formatter: 'High 28°C', fontSize: 9, color: '#f56c6c' }, lineStyle: { color: '#f56c6c', type: 'dashed', width: 1 } }]
            }
          },
          {
            name: 'Power (kW)',
            type: 'line',
            data: trendData.power,
            smooth: true,
            symbol: 'diamond',
            symbolSize: 4,
            lineStyle: { width: 2, color: '#e6a23c' },
            itemStyle: { color: '#e6a23c' },
            areaStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: 'rgba(230, 162, 60, 0.2)' },
                { offset: 1, color: 'rgba(230, 162, 60, 0.02)' }
              ])
            }
          },
          {
            name: 'Humidity (%)',
            type: 'line',
            yAxisIndex: 1,
            data: trendData.humidity,
            smooth: true,
            symbol: 'triangle',
            symbolSize: 4,
            lineStyle: { width: 2, color: '#409eff' },
            itemStyle: { color: '#409eff' },
            areaStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: 'rgba(64, 158, 255, 0.2)' },
                { offset: 1, color: 'rgba(64, 158, 255, 0.02)' }
              ])
            }
          },
          {
            name: 'Efficiency (%)',
            type: 'line',
            yAxisIndex: 1,
            data: trendData.efficiency,
            smooth: true,
            symbol: 'pin',
            symbolSize: 4,
            lineStyle: { width: 2, color: '#67c23a' },
            itemStyle: { color: '#67c23a' },
            areaStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: 'rgba(103, 194, 58, 0.2)' },
                { offset: 1, color: 'rgba(103, 194, 58, 0.02)' }
              ])
            },
            markLine: {
              silent: true,
              symbol: 'none',
              data: [{ yAxis: 80, label: { formatter: 'Min 80%', fontSize: 9, color: '#67c23a' }, lineStyle: { color: '#67c23a', type: 'dashed', width: 1 } }]
            }
          }
        ]
      }

      trendChartInstance.setOption(option)
    } catch (error) {
      console.error('Failed to initialize trend chart:', error)
    }
  })
}

// Handle window resize for chart
const handleResize = () => {
  if (trendChartInstance) {
    try {
      trendChartInstance.resize()
    } catch (e) {
      // ignore resize errors during disposal
    }
  }
}

// Real-time data updates
let updateTimer: number
const startRealtimeUpdates = () => {
  updateTimer = window.setInterval(() => {
    lastUpdateTime.value = new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' })

    if (selectedDevice.value) {
      const m = selectedDevice.value.metrics
      m.temperature += (Math.random() - 0.5) * 0.3
      m.power += (Math.random() - 0.5) * 0.5
      m.temperature = Math.round(m.temperature * 10) / 10
      m.power = Math.round(m.power * 10) / 10

      // Update chart with new data point
      if (trendChartInstance && !trendChartInstance.isDisposed()) {
        try {
          const now = new Date()
          const timeStr = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`
          const option = trendChartInstance.getOption()
          if (option && (option.xAxis as any[])?.[0]?.data) {
            const xData = [...(option.xAxis as any[])[0].data, timeStr]
            if (xData.length > 24) xData.shift()

            const series = option.series as any[]
            const tempData = [...series[0].data, +(m.temperature + (Math.random() - 0.5) * 0.5).toFixed(1)]
            if (tempData.length > 24) tempData.shift()

            const powerData = [...series[1].data, +(m.power + (Math.random() - 0.5) * 1).toFixed(1)]
            if (powerData.length > 24) powerData.shift()

            trendChartInstance.setOption({
              xAxis: [{ data: xData }],
              series: [{ data: tempData }, { data: powerData }]
            })
          }
        } catch (e) {
          // ignore update errors
        }
      }
    }
  }, 3000)
}

// ==================== Lifecycle ====================
onMounted(() => {
  startRealtimeUpdates()
  window.addEventListener('resize', handleResize)
  lastUpdateTime.value = new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
})

onUnmounted(() => {
  clearInterval(updateTimer)
  window.removeEventListener('resize', handleResize)
  destroyChart()
  document.removeEventListener('mousemove', handleResizeLeft)
  document.removeEventListener('mouseup', stopResizeLeft)
  document.removeEventListener('mousemove', handleResizeRight)
  document.removeEventListener('mouseup', stopResizeRight)
})

watch(searchKeyword, async (val) => {
  if (treeRef.value) {
    treeRef.value.filter(val)
  }
})

// Watch for device selection to init chart
watch(selectedDevice, (newVal) => {
  if (newVal) {
    nextTick(() => {
      initTrendChart()
    })
  }
})

// Watch view mode for chart resize
watch(viewMode, () => {
  nextTick(() => {
    handleResize()
  })
})
</script>

<style scoped>
/* ==================== Layout ==================== */
.topology-page {
  display: flex;
  height: 100%;
  background: #0a1629;
  overflow: hidden;
  position: relative;
}

/* ==================== Left Panel ==================== */
.topology-left-panel {
  display: flex;
  flex-direction: column;
  background: rgba(13, 25, 48, 0.95);
  border-right: 1px solid rgba(64, 158, 255, 0.15);
  backdrop-filter: blur(10px);
  transition: width 0.3s ease;
  overflow: hidden;
  flex-shrink: 0;
}

.panel-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  color: #e5eaf3;
  font-weight: 600;
  font-size: 14px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.panel-header .el-icon {
  color: #409eff;
  font-size: 18px;
}

.toggle-btn {
  margin-left: auto;
  width: 28px;
  height: 28px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #e5eaf3;
}

.search-box {
  padding: 12px;
}

.search-box :deep(.el-input__wrapper) {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: none;
}

.search-box :deep(.el-input__inner) {
  color: #e5eaf3;
}

/* ==================== Topology Tree ==================== */
.topology-tree {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 0 4px;
}

.topology-tree::-webkit-scrollbar {
  width: 4px;
}

.topology-tree::-webkit-scrollbar-thumb {
  background: rgba(64, 158, 255, 0.3);
  border-radius: 2px;
}

.topology-tree :deep(.el-tree) {
  background: transparent;
  color: #e5eaf3;
}

.topology-tree :deep(.el-tree-node__content) {
  height: 40px;
  border-radius: 6px;
  margin: 2px 4px;
  transition: all 0.2s;
}

.topology-tree :deep(.el-tree-node__content:hover) {
  background: rgba(64, 158, 255, 0.1);
}

.topology-tree :deep(.el-tree-node.is-current > .el-tree-node__content) {
  background: rgba(64, 158, 255, 0.2);
  border: 1px solid rgba(64, 158, 255, 0.3);
}

.tree-node-content {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  padding-right: 8px;
}

.device-thumb {
  flex-shrink: 0;
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 4px;
}

.node-icon {
  font-size: 16px;
  flex-shrink: 0;
}

.area-icon { color: #409eff; }
.system-icon { color: #67c23a; }

.node-label {
  flex: 1;
  font-size: 13px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.node-label.is-selected {
  color: #409eff;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.status-dot.status-online { background: #67c23a; box-shadow: 0 0 6px rgba(103, 194, 58, 0.6); }
.status-dot.status-warning { background: #e6a23c; box-shadow: 0 0 6px rgba(230, 162, 60, 0.6); animation: pulse 2s infinite; }
.status-dot.status-error { background: #f56c6c; box-shadow: 0 0 6px rgba(245, 108, 108, 0.6); animation: pulse 1s infinite; }
.status-dot.status-offline { background: #909399; }

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.count-badge :deep(.el-badge__content) {
  background: rgba(64, 158, 255, 0.3);
  border: none;
  font-size: 10px;
  height: 16px;
  line-height: 16px;
}

/* ==================== Stats Overview ==================== */
.stats-overview {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 4px;
  padding: 8px 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(0, 0, 0, 0.2);
}

.stat-item {
  text-align: center;
  padding: 6px 4px;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.04);
}

.stat-value {
  display: block;
  font-size: 16px;
  font-weight: 700;
  color: #409eff;
}

.stat-value.online { color: #67c23a; }

.stat-label {
  font-size: 10px;
  color: #8899aa;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* ==================== Resize Handle ==================== */
.resize-handle {
  width: 4px;
  background: rgba(64, 158, 255, 0.1);
  cursor: col-resize;
  transition: background 0.2s;
  flex-shrink: 0;
}

.resize-handle:hover {
  background: rgba(64, 158, 255, 0.4);
}

/* ==================== Canvas ==================== */
.topology-canvas {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
}

.canvas-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 16px;
  background: rgba(13, 25, 48, 0.9);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.toolbar-left,
.toolbar-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.toolbar-left :deep(.el-radio-button__inner),
.toolbar-right :deep(.el-button),
.canvas-toolbar :deep(.el-button) {
  background: rgba(255, 255, 255, 0.06);
  border-color: rgba(255, 255, 255, 0.15);
  color: #e5eaf3;
}

.toolbar-left :deep(.el-radio-button__inner:hover),
.toolbar-right :deep(.el-button:hover),
.canvas-toolbar :deep(.el-button:hover) {
  background: rgba(64, 158, 255, 0.2);
  border-color: rgba(64, 158, 255, 0.4);
}

.canvas-container {
  flex: 1;
  position: relative;
  overflow: hidden;
  background: radial-gradient(ellipse at center, #0d1930 0%, #070e1a 100%);
}

/* ==================== Device Grid View ==================== */
.device-grid-view {
  height: 100%;
  overflow-y: auto;
  padding: 16px;
}

.device-grid-view::-webkit-scrollbar {
  width: 4px;
}

.device-grid-view::-webkit-scrollbar-thumb {
  background: rgba(64, 158, 255, 0.3);
  border-radius: 2px;
}

.empty-canvas-hint {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  color: #8899aa;
  z-index: 5;
}

.empty-canvas-hint p {
  margin-top: 12px;
  font-size: 14px;
}

.device-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 16px;
}

.device-card {
  background: rgba(13, 25, 48, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
}

.device-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
  border-color: rgba(64, 158, 255, 0.3);
}

.device-card.is-selected {
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.4);
  background: rgba(64, 158, 255, 0.08);
}

.device-card.status-warning {
  border-left: 3px solid #e6a23c;
}

.device-card.status-error {
  border-left: 3px solid #f56c6c;
}

.device-card.status-offline {
  opacity: 0.6;
}

.device-image-wrapper {
  position: relative;
  width: 100%;
  height: 160px;
  background: rgba(0, 0, 0, 0.3);
  overflow: hidden;
}

.device-image {
  width: 100%;
  height: 100%;
}

.device-image :deep(.el-image__inner) {
  object-fit: contain;
  transition: transform 0.3s ease;
}

.device-card:hover .device-image :deep(.el-image__inner) {
  transform: scale(1.05);
}

.image-fallback {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.5);
  color: #8899aa;
  gap: 8px;
  font-size: 12px;
}

.image-loading {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.3);
  color: #8899aa;
}

.device-status-tag {
  position: absolute;
  top: 8px;
  right: 8px;
}

.heatmap-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(245, 108, 108, 0.5), rgba(230, 162, 60, 0.3));
  pointer-events: none;
  transition: opacity 0.3s ease;
}

.device-info {
  padding: 12px;
}

.device-name {
  margin: 0 0 4px 0;
  font-size: 13px;
  color: #e5eaf3;
  font-weight: 600;
}

.device-model {
  font-size: 11px;
  color: #8899aa;
  display: block;
  margin-bottom: 8px;
}

.device-metrics-mini {
  display: flex;
  gap: 12px;
}

.metric-mini {
  font-size: 11px;
  color: #8899aa;
  font-family: 'JetBrains Mono', monospace;
}

.metric-mini.warning {
  color: #e6a23c;
}

/* ==================== Device List View ==================== */
.device-list-view {
  height: 100%;
  overflow: hidden;
}

.device-list-view :deep(.el-table) {
  background: transparent;
  --el-table-bg-color: transparent;
  --el-table-tr-bg-color: transparent;
  --el-table-header-bg-color: rgba(13, 25, 48, 0.95);
  --el-table-border-color: rgba(255, 255, 255, 0.06);
  --el-table-text-color: #e5eaf3;
  --el-table-header-text-color: #8899aa;
}

.device-list-view :deep(.el-table th) {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.device-list-view :deep(.el-table tr) {
  cursor: pointer;
  transition: background 0.2s;
}

.device-list-view :deep(.el-table tr:hover > td) {
  background: rgba(64, 158, 255, 0.08) !important;
}

.device-list-view :deep(.el-table .row-warning) {
  border-left: 3px solid #e6a23c;
}

.device-list-view :deep(.el-table .row-error) {
  border-left: 3px solid #f56c6c;
  background: rgba(245, 108, 108, 0.05) !important;
}

.device-list-view :deep(.el-table .row-offline) {
  opacity: 0.5;
}

.table-device-name {
  font-weight: 500;
}

.text-warning { color: #e6a23c; }
.text-danger { color: #f56c6c; }

/* ==================== Legend ==================== */
.canvas-legend {
  position: absolute;
  bottom: 16px;
  left: 16px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  background: rgba(13, 25, 48, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 10px 14px;
  z-index: 10;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 11px;
  color: #8899aa;
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.dot.online { background: #67c23a; box-shadow: 0 0 8px rgba(103, 194, 58, 0.5); }
.dot.warning { background: #e6a23c; box-shadow: 0 0 8px rgba(230, 162, 60, 0.5); }
.dot.error { background: #f56c6c; box-shadow: 0 0 8px rgba(245, 108, 108, 0.5); }
.dot.offline { background: #909399; }

/* ==================== Right Detail Panel ==================== */
.detail-panel {
  display: flex;
  flex-direction: column;
  background: rgba(13, 25, 48, 0.95);
  border-left: 1px solid rgba(64, 158, 255, 0.15);
  backdrop-filter: blur(10px);
  overflow-y: auto;
  flex-shrink: 0;
}

.detail-panel::-webkit-scrollbar {
  width: 4px;
}

.detail-panel::-webkit-scrollbar-thumb {
  background: rgba(64, 158, 255, 0.3);
  border-radius: 2px;
}

.slide-right-enter-active,
.slide-right-leave-active {
  transition: all 0.3s ease;
}

.slide-right-enter-from,
.slide-right-leave-to {
  width: 0 !important;
  opacity: 0;
}

.detail-section {
  padding: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.section-title {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #e5eaf3;
  font-size: 14px;
  margin: 0 0 12px 0;
  font-weight: 600;
}

.section-title .el-icon {
  color: #409eff;
}

.refresh-tag {
  margin-left: auto;
  font-size: 10px;
}

.chart-subtitle {
  margin-left: auto;
  font-size: 10px;
  color: #8899aa;
  font-weight: 400;
}

/* Device Hero Image */
.device-hero-image {
  position: relative;
  width: 100%;
  height: 200px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
}

.hero-image {
  width: 100%;
  height: 100%;
}

.hero-image :deep(.el-image__inner) {
  object-fit: contain;
  transition: transform 0.3s ease;
}

.device-hero-image:hover .hero-image :deep(.el-image__inner) {
  transform: scale(1.05);
}

.image-fallback.large {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.5);
  color: #8899aa;
  gap: 12px;
  font-size: 14px;
}

.image-hint {
  display: block;
  text-align: center;
  font-size: 10px;
  color: #8899aa;
  margin-top: 6px;
}

/* Info Grid */
.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.info-item label {
  font-size: 10px;
  color: #8899aa;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-item span {
  font-size: 12px;
  color: #e5eaf3;
}

.info-item .mono {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  color: #409eff;
}

.info-item .overdue {
  color: #f56c6c;
  display: flex;
  align-items: center;
  gap: 4px;
}

/* Metrics Grid */
.metrics-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.metric-card {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  background: rgba(255, 255, 255, 0.04);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.06);
  transition: all 0.3s;
}

.metric-card:hover {
  background: rgba(64, 158, 255, 0.08);
  border-color: rgba(64, 158, 255, 0.2);
}

.metric-card.metric-warning {
  border-color: rgba(245, 108, 108, 0.3);
  background: rgba(245, 108, 108, 0.05);
}

.metric-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(64, 158, 255, 0.15);
  border-radius: 8px;
  color: #409eff;
  flex-shrink: 0;
}

.metric-warning .metric-icon {
  background: rgba(245, 108, 108, 0.15);
  color: #f56c6c;
}

.metric-info {
  flex: 1;
  min-width: 0;
}

.metric-value {
  display: block;
  font-size: 16px;
  font-weight: 700;
  color: #e5eaf3;
}

.metric-unit {
  font-size: 10px;
  color: #8899aa;
  font-weight: 400;
  margin-left: 2px;
}

.metric-label {
  font-size: 10px;
  color: #8899aa;
}

/* Chart Container */
.chart-container {
  width: 100%;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.trend-chart {
  height: 260px;
  min-height: 260px;
}

/* Action Buttons */
.detail-actions {
  padding: 16px;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.detail-actions .el-button {
  flex: 1;
  min-width: 80px;
}

/* ==================== Responsive ==================== */
@media (max-width: 1200px) {
  .device-grid {
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: 12px;
  }

  .device-image-wrapper {
    height: 130px;
  }

  .metrics-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .topology-left-panel {
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    z-index: 100;
    width: 280px !important;
  }

  .detail-panel {
    position: absolute;
    right: 0;
    top: 0;
    bottom: 0;
    z-index: 100;
    width: 320px !important;
  }

  .device-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 10px;
  }

  .device-image-wrapper {
    height: 120px;
  }

  .info-grid {
    grid-template-columns: 1fr;
  }

  .canvas-toolbar {
    flex-direction: column;
    gap: 8px;
    padding: 8px;
  }

  .toolbar-left,
  .toolbar-right {
    width: 100%;
    justify-content: center;
  }

  .trend-chart {
    height: 220px;
    min-height: 220px;
  }
}
</style>