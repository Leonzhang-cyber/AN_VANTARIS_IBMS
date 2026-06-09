<!-- src/views/device/AreaTopology.vue -->
<template>
  <!-- ==================== Loading Screen ==================== -->
  <div v-if="!isAssetsLoaded" class="loading-container">
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
        <div class="loading-tip">Initializing Area Topology</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- ==================== Main Content ==================== -->
  <div v-else class="topology-page">
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
    <div class="topology-canvas" :class="{ 'focused-mode': focusedDevice }">
      <!-- ===== 设备聚焦大屏模式 ===== -->
      <div v-if="focusedDevice" class="device-focus-screen">
        <!-- 背景图片层 -->
        <div class="focus-background">
          <el-image
              :src="focusedDevice.imageUrl"
              fit="cover"
              class="focus-bg-image"
          />
          <div class="focus-bg-overlay"></div>
        </div>

        <!-- 顶部导航 -->
        <div class="focus-top-bar">
          <el-button
              :icon="ArrowLeft"
              size="default"
              class="back-btn"
              @click="exitFocusMode"
          >
            Back to {{ selectedSystem?.name || 'Overview' }}
          </el-button>
          <div class="focus-breadcrumb">
            <el-breadcrumb separator="/">
              <el-breadcrumb-item>
                <span style="color: #8899aa; cursor: pointer" @click="exitFocusMode">Topology</span>
              </el-breadcrumb-item>
              <el-breadcrumb-item>
                <span style="color: #409eff">{{ focusedDevice.name }}</span>
              </el-breadcrumb-item>
            </el-breadcrumb>
          </div>
          <div class="focus-actions">
            <el-button-group>
              <el-button :icon="Switch" @click="handleDeviceControl(focusedDevice)">
                Control
              </el-button>
              <el-button :icon="Tools" type="warning" @click="handleQuickRepair">
                Repair
              </el-button>
              <el-button :icon="Download" @click="exportDeviceData">
                Export
              </el-button>
            </el-button-group>
          </div>
        </div>

        <!-- 主内容区域 -->
        <div class="focus-main-content">
          <!-- 左侧：设备大图 -->
          <div class="focus-image-section">
            <div class="focus-image-container">
              <el-image
                  :src="focusedDevice.imageUrl"
                  fit="contain"
                  class="focus-main-image"
                  :preview-src-list="[focusedDevice.imageUrl]"
                  preview-teleported
              >
                <template #error>
                  <div class="image-fallback focus-fallback">
                    <el-icon :size="80"><Cpu /></el-icon>
                    <span>No Image Available</span>
                  </div>
                </template>
              </el-image>
            </div>
            <div class="focus-image-info">
              <div class="focus-device-status">
                <span class="status-indicator" :class="`status-${focusedDevice.status}`"></span>
                <el-tag :type="getStatusType(focusedDevice.status)" size="large" effect="dark">
                  {{ focusedDevice.status.toUpperCase() }}
                </el-tag>
              </div>
              <h2 class="focus-device-name">{{ focusedDevice.name }}</h2>
              <p class="focus-device-model">{{ focusedDevice.model }} - {{ focusedDevice.manufacturer }}</p>
              <p class="focus-device-serial">S/N: {{ focusedDevice.serialNumber }}</p>
            </div>
          </div>

          <!-- 右侧：实时指标面板 -->
          <div class="focus-metrics-section">
            <div class="focus-metrics-grid">
              <div
                  v-for="metric in displayMetrics"
                  :key="metric.key"
                  class="focus-metric-card"
                  :class="{ 'metric-warning': metric.warning }"
              >
                <div class="focus-metric-icon">
                  <el-icon :size="24">
                    <component :is="metric.icon" />
                  </el-icon>
                </div>
                <div class="focus-metric-data">
                  <span class="focus-metric-value">
                    {{ metric.value }}
                    <span class="focus-metric-unit">{{ metric.unit }}</span>
                  </span>
                  <span class="focus-metric-label">{{ metric.label }}</span>
                </div>
                <div class="focus-metric-bar">
                  <div
                      class="focus-metric-fill"
                      :style="{ width: getMetricPercentage(metric) + '%' }"
                      :class="{ 'fill-warning': metric.warning }"
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 底部：趋势图 + 详细信息 -->
        <div class="focus-bottom-panel">
          <!-- 趋势图 -->
          <div class="focus-chart-section">
            <h4 class="focus-section-title">
              <el-icon><TrendCharts /></el-icon>
              Trend Analysis - Last 24 Hours
              <span class="chart-update-time">Updated {{ lastUpdateTime }}</span>
            </h4>
            <div ref="focusChartRef" class="focus-chart-container"></div>
          </div>

          <!-- 维护信息 -->
          <div class="focus-maintenance-section">
            <h4 class="focus-section-title">
              <el-icon><Document /></el-icon>
              Maintenance Info
            </h4>
            <div class="maintenance-timeline">
              <div class="timeline-item">
                <div class="timeline-dot installed"></div>
                <div class="timeline-content">
                  <span class="timeline-date">{{ focusedDevice.installationDate }}</span>
                  <span class="timeline-label">Installation Date</span>
                </div>
              </div>
              <div class="timeline-item">
                <div class="timeline-dot maintenance"></div>
                <div class="timeline-content">
                  <span class="timeline-date">{{ focusedDevice.lastMaintenance }}</span>
                  <span class="timeline-label">Last Maintenance</span>
                </div>
              </div>
              <div class="timeline-item" :class="{ overdue: isMaintenanceOverdue }">
                <div class="timeline-dot" :class="isMaintenanceOverdue ? 'overdue' : 'scheduled'"></div>
                <div class="timeline-content">
                  <span class="timeline-date">
                    {{ focusedDevice.nextMaintenance }}
                    <el-tag v-if="isMaintenanceOverdue" type="danger" size="small">Overdue</el-tag>
                  </span>
                  <span class="timeline-label">Next Maintenance</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ===== 普通模式 ===== -->
      <template v-else>
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
            <div v-if="groupedDevicesByArea.length === 0" class="empty-canvas-hint">
              <el-icon :size="48"><View /></el-icon>
              <p>Select an area or system to view devices</p>
            </div>

            <div v-else class="device-grid">
              <template v-for="(group, groupIndex) in groupedDevicesByArea" :key="group.areaId">
                <!-- 区域小标题 + 分割线 -->
                <div class="area-grid-header" :class="{ 'first-header': groupIndex === 0 }">
                  <div class="area-header-content">
                    <el-icon class="area-header-icon"><OfficeBuilding /></el-icon>
                    <span class="area-header-name">{{ group.areaName }}</span>
                    <span class="area-header-count">{{ group.devices.length }} devices</span>
                  </div>
                  <div class="area-header-divider"></div>
                </div>

                <!-- 该区域下的所有设备 -->
                <div
                    v-for="device in group.devices"
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
              </template>
            </div>
          </div>

          <!-- 设备列表视图 -->
          <!-- 设备列表视图 -->
          <div v-else class="device-list-view">
            <div v-if="groupedDevicesByArea.length === 0" class="empty-canvas-hint">
              <el-icon :size="48"><View /></el-icon>
              <p>Select an area or system to view devices</p>
            </div>

            <div v-else class="device-list-container">
              <template v-for="(group, groupIndex) in groupedDevicesByArea" :key="group.areaId">
                <!-- 区域小标题 + 分割线 -->
                <div class="area-list-header" :class="{ 'first-header': groupIndex === 0 }">
                  <div class="area-header-content">
                    <el-icon class="area-header-icon"><OfficeBuilding /></el-icon>
                    <span class="area-header-name">{{ group.areaName }}</span>
                    <span class="area-header-count">{{ group.devices.length }} devices</span>
                  </div>
                  <div class="area-header-divider"></div>
                </div>

                <!-- 该区域下的所有设备表格行 -->
                <el-table
                    :data="group.devices"
                    style="width: 100%"
                    :show-header="false"
                    highlight-current-row
                    @row-click="handleNodeClick"
                    :row-class-name="tableRowClassName"
                    class="area-sub-table"
                >
                  <el-table-column width="80">
                    <template #default="{ row }">
                      <el-avatar :src="row.imageUrl" :size="40" shape="square" fit="cover">
                        <template #error>
                          <el-icon :size="24"><Cpu /></el-icon>
                        </template>
                      </el-avatar>
                    </template>
                  </el-table-column>
                  <el-table-column prop="name" label="Device Name" width="250">
                    <template #default="{ row }">
                      <span class="table-device-name">{{ row.name }}</span>
                    </template>
                  </el-table-column>
                  <el-table-column prop="model" label="Model" width="200" />
                  <el-table-column prop="status" label="Status" width="130">
                    <template #default="{ row }">
                      <el-tag :type="getStatusType(row.status)" size="small" effect="dark">
                        {{ row.status.toUpperCase() }}
                      </el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column label="Temp" width="130">
                    <template #default="{ row }">
            <span :class="{ 'text-warning': row.metrics.temperature > 28 }">
              {{ row.metrics.temperature }}°C
            </span>
                    </template>
                  </el-table-column>
                  <el-table-column label="Power" width="130">
                    <template #default="{ row }">
            <span :class="{ 'text-warning': row.metrics.power > 20 }">
              {{ row.metrics.power }} kW
            </span>
                    </template>
                  </el-table-column>
                  <el-table-column label="Efficiency" width="130">
                    <template #default="{ row }">
            <span :class="{ 'text-danger': row.metrics.efficiency < 80 }">
              {{ row.metrics.efficiency }}%
            </span>
                    </template>
                  </el-table-column>
                  <el-table-column label="Actions" width="130" fixed="right">
                    <template #default="{ row }">
                      <el-button size="small" :icon="Switch" @click.stop="handleDeviceControl(row)">
                        Control
                      </el-button>
                    </template>
                  </el-table-column>
                </el-table>
              </template>
            </div>
          </div>

          <div class="canvas-legend">
            <div class="legend-item"><span class="dot online"></span> Online</div>
            <div class="legend-item"><span class="dot warning"></span> Warning</div>
            <div class="legend-item"><span class="dot error"></span> Error</div>
            <div class="legend-item"><span class="dot offline"></span> Offline</div>
          </div>
        </div>
      </template>
    </div>
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

// ==================== Loading State ====================
const isAssetsLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref<string>('Preparing assets...')

const loadingMessages = [
  'Preparing assets...',
  'Loading device images...',
  'Initializing topology tree...',
  'Configuring canvas...',
  'Starting real-time updates...',
  'Almost ready...'
]

// ==================== Mock Data ====================
// ==================== Mock Data ====================
const generateMockData = (): AreaNode[] => {
  return [
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
            createHVACDevice('dev-ahu-b2-01', 'AHU-B2-01 Air Handler', 'Carrier 39G', 'Carrier', 'CA-2024-B201', 'online',
                { temperature: 23.0, humidity: 50, power: 18.5, energy: 15200, efficiency: 94, pressure: 280, flowRate: 15000, noiseLevel: 62 },
                { last: '2026-04-15', next: '2026-07-15' }, '2024-01-10', { x: 10, y: -6, z: 4 }),
            createHVACDevice('dev-fcu-b2-01', 'FCU-B2-01 Fan Coil', 'Daikin FXMQ', 'Daikin', 'DK-2024-B201', 'online',
                { temperature: 22.5, humidity: 48, power: 6.8, energy: 5400, efficiency: 91, pressure: 160, flowRate: 1800, noiseLevel: 38 },
                { last: '2026-05-01', next: '2026-08-01' }, '2024-02-15', { x: 15, y: -5.5, z: 6 }),
            createHVACDevice('dev-chiller-b2-01', 'CH-B2-01 Chiller', 'Carrier AquaEdge', 'Carrier', 'CA-2024-B202', 'online',
                { temperature: 28.0, humidity: 65, power: 85.0, energy: 68000, efficiency: 92, pressure: 420, flowRate: 45000, noiseLevel: 72 },
                { last: '2026-04-10', next: '2026-07-10' }, '2024-01-05', { x: 5, y: -6.2, z: 3 }),
            createHVACDevice('dev-cooling-b2-01', 'CT-B2-01 Cooling Tower', 'BAC 3000', 'Baltimore Aircoil', 'BA-2024-B201', 'online',
                { temperature: 32.0, humidity: 70, power: 35.0, energy: 28000, efficiency: 88, pressure: 200, flowRate: 35000, noiseLevel: 85 },
                { last: '2026-04-20', next: '2026-07-20' }, '2024-01-20', { x: 25, y: -6.5, z: 8 }),
            createHVACDevice('dev-pump-hvac-b2-01', 'CHWP-B2-01 Chilled Water Pump', 'Grundfos CR', 'Grundfos', 'GF-2024-B202', 'online',
                { temperature: 29.0, humidity: 60, power: 22.0, energy: 17600, efficiency: 93, pressure: 350, flowRate: 8000, noiseLevel: 68 },
                { last: '2026-05-05', next: '2026-08-05' }, '2024-02-01', { x: 8, y: -5.8, z: 2 }),
            createHVACDevice('dev-pump-hvac-b2-02', 'CWP-B2-01 Condenser Water Pump', 'Grundfos CR', 'Grundfos', 'GF-2024-B203', 'online',
                { temperature: 30.5, humidity: 62, power: 28.0, energy: 22400, efficiency: 91, pressure: 380, flowRate: 9500, noiseLevel: 70 },
                { last: '2026-05-05', next: '2026-08-05' }, '2024-02-01', { x: 12, y: -6.0, z: 2 }),
            createHVACDevice('dev-vav-b2-01', 'VAV-B2-01 VAV Box', 'Johnson Controls VAV', 'Johnson Controls', 'JC-2024-B201', 'online',
                { temperature: 23.5, humidity: 52, power: 1.2, energy: 960, efficiency: 96, pressure: 120, flowRate: 1200, noiseLevel: 45 },
                { last: '2026-04-25', next: '2026-07-25' }, '2024-02-10', { x: 18, y: -5.5, z: 6 }),
            createHVACDevice('dev-vav-b2-02', 'VAV-B2-02 VAV Box', 'Johnson Controls VAV', 'Johnson Controls', 'JC-2024-B202', 'online',
                { temperature: 23.8, humidity: 53, power: 1.1, energy: 880, efficiency: 95, pressure: 115, flowRate: 1100, noiseLevel: 44 },
                { last: '2026-04-25', next: '2026-07-25' }, '2024-02-10', { x: 22, y: -5.5, z: 6 }),
            createHVACDevice('dev-vav-b2-03', 'VAV-B2-03 VAV Box', 'Johnson Controls VAV', 'Johnson Controls', 'JC-2024-B203', 'online',
                { temperature: 24.0, humidity: 54, power: 0.9, energy: 720, efficiency: 94, pressure: 110, flowRate: 900, noiseLevel: 42 },
                { last: '2026-04-25', next: '2026-07-25' }, '2024-02-10', { x: 28, y: -5.5, z: 6 }),
            createHVACDevice('dev-exhaust-b2-01', 'EF-B2-01 Exhaust Fan', 'Greenheck CUBE', 'Greenheck', 'GH-2024-B201', 'online',
                { temperature: 27.0, humidity: 55, power: 7.5, energy: 6000, efficiency: 89, pressure: 180, flowRate: 8000, noiseLevel: 65 },
                { last: '2026-05-12', next: '2026-08-12' }, '2024-01-25', { x: 30, y: -6.0, z: 5 }),
            createHVACDevice('dev-exhaust-b2-02', 'EF-B2-02 Exhaust Fan', 'Greenheck CUBE', 'Greenheck', 'GH-2024-B202', 'warning',
                { temperature: 29.5, humidity: 58, power: 8.2, energy: 6560, efficiency: 86, pressure: 195, flowRate: 8500, noiseLevel: 68 },
                { last: '2026-03-15', next: '2026-06-15' }, '2024-01-25', { x: 32, y: -6.0, z: 5 })
          ]
        },
        {
          id: 'sys-lighting-b2', name: 'Lighting System', label: 'Lighting System',
          type: 'system', systemType: 'lighting', status: 'online',
          children: [
            createLightingDevice('dev-light-b2-01', 'LIGHT-B2-01 Main Controller', 'Philips Dynalite', 'Philips', 'PH-2024-B201', 'online',
                { temperature: 26.5, humidity: 42, power: 4.2, energy: 3200, efficiency: 96 },
                { last: '2026-05-15', next: '2026-08-15' }, '2024-01-20', { x: 8, y: -5, z: 8 }),
            createLightingDevice('dev-light-b2-02', 'LIGHT-B2-02 Zone A', 'Philips Dynalite', 'Philips', 'PH-2024-B202', 'online',
                { temperature: 27.0, humidity: 43, power: 2.8, energy: 2240, efficiency: 95 },
                { last: '2026-05-15', next: '2026-08-15' }, '2024-01-20', { x: 12, y: -5, z: 8 }),
            createLightingDevice('dev-light-b2-03', 'LIGHT-B2-03 Zone B', 'Philips Dynalite', 'Philips', 'PH-2024-B203', 'online',
                { temperature: 26.8, humidity: 42, power: 3.1, energy: 2480, efficiency: 95 },
                { last: '2026-05-15', next: '2026-08-15' }, '2024-01-20', { x: 16, y: -5, z: 8 }),
            createLightingDevice('dev-light-b2-04', 'LIGHT-B2-04 Emergency Lighting', 'Schneider KNX', 'Schneider Electric', 'SE-2024-B201', 'online',
                { temperature: 26.0, humidity: 41, power: 1.5, energy: 1200, efficiency: 97 },
                { last: '2026-05-18', next: '2026-08-18' }, '2024-01-22', { x: 20, y: -5, z: 8 }),
            createLightingDevice('dev-light-b2-05', 'LIGHT-B2-05 Stairwell Lighting', 'Schneider KNX', 'Schneider Electric', 'SE-2024-B202', 'online',
                { temperature: 25.5, humidity: 40, power: 1.2, energy: 960, efficiency: 98 },
                { last: '2026-05-18', next: '2026-08-18' }, '2024-01-22', { x: 24, y: -5, z: 8 })
          ]
        },
        {
          id: 'sys-fas-b2', name: 'Fire Alarm System', label: 'Fire Alarm System',
          type: 'system', systemType: 'fas', status: 'online',
          children: [
            createFASDevice('dev-smoke-b2-01', 'SD-B2-01 Smoke Detector', 'Honeywell XLS', 'Honeywell', 'HW-2024-B201', 'online',
                { temperature: 21.5, humidity: 62, power: 0.3, energy: 240, efficiency: 99, co2Level: 420, noiseLevel: 12 },
                { last: '2026-04-10', next: '2026-07-10' }, '2024-01-01', { x: 12, y: -5.8, z: 10 }),
            createFASDevice('dev-smoke-b2-02', 'SD-B2-02 Smoke Detector', 'Honeywell XLS', 'Honeywell', 'HW-2024-B202', 'online',
                { temperature: 21.8, humidity: 63, power: 0.3, energy: 238, efficiency: 99, co2Level: 430, noiseLevel: 11 },
                { last: '2026-04-10', next: '2026-07-10' }, '2024-01-01', { x: 20, y: -5.8, z: 10 }),
            createFASDevice('dev-smoke-b2-03', 'SD-B2-03 Smoke Detector', 'Honeywell XLS', 'Honeywell', 'HW-2024-B203', 'online',
                { temperature: 22.0, humidity: 61, power: 0.3, energy: 240, efficiency: 99, co2Level: 425, noiseLevel: 12 },
                { last: '2026-04-10', next: '2026-07-10' }, '2024-01-01', { x: 28, y: -5.8, z: 10 }),
            createFASDevice('dev-smoke-b2-04', 'SD-B2-04 Smoke Detector', 'Siemens Cerberus', 'Siemens', 'SM-2024-B201', 'online',
                { temperature: 21.3, humidity: 60, power: 0.2, energy: 160, efficiency: 99, co2Level: 415, noiseLevel: 11 },
                { last: '2026-04-12', next: '2026-07-12' }, '2024-01-03', { x: 35, y: -5.8, z: 10 }),
            createFASDevice('dev-heat-b2-01', 'HD-B2-01 Heat Detector', 'Siemens Cerberus', 'Siemens', 'SM-2024-B202', 'online',
                { temperature: 22.5, humidity: 58, power: 0.2, energy: 160, efficiency: 99, noiseLevel: 10 },
                { last: '2026-04-12', next: '2026-07-12' }, '2024-01-03', { x: 15, y: -5.8, z: 12 }),
            createFASDevice('dev-pull-b2-01', 'PULL-B2-01 Manual Pull Station', 'Honeywell XLS', 'Honeywell', 'HW-2024-B204', 'online',
                { temperature: 21.0, humidity: 59, power: 0.1, energy: 80, efficiency: 100, noiseLevel: 8 },
                { last: '2026-03-20', next: '2026-06-20' }, '2024-01-05', { x: 40, y: -5.5, z: 4 })
          ]
        },
        {
          id: 'sys-plumbing-b2', name: 'Plumbing System', label: 'Plumbing System',
          type: 'system', systemType: 'plumbing', status: 'warning',
          children: [
            createPlumbingDevice('dev-pump-b2-01', 'PUMP-B2-01 Sump Pump', 'Grundfos SE', 'Grundfos', 'GF-2024-B201', 'online',
                { temperature: 32.0, humidity: 70, power: 11.0, energy: 8800, efficiency: 88, pressure: 380, flowRate: 60 },
                { last: '2026-03-20', next: '2026-06-20' }, '2023-12-15', { x: 5, y: -6.5, z: 12 }),
            createPlumbingDevice('dev-pump-b2-02', 'PUMP-B2-02 Booster Pump', 'Grundfos CR', 'Grundfos', 'GF-2024-B202', 'warning',
                { temperature: 38.0, humidity: 72, power: 9.5, energy: 7600, efficiency: 76, pressure: 320, flowRate: 42, vibration: 3.8 },
                { last: '2024-02-28', next: '2026-04-28' }, '2023-11-20', { x: 5, y: -6.5, z: 14 }),
            createPlumbingDevice('dev-pump-b2-03', 'PUMP-B2-03 Drain Pump', 'Grundfos SE', 'Grundfos', 'GF-2024-B203', 'online',
                { temperature: 33.5, humidity: 68, power: 8.5, energy: 6800, efficiency: 89, pressure: 350, flowRate: 55 },
                { last: '2026-04-01', next: '2026-07-01' }, '2023-12-20', { x: 5, y: -6.5, z: 16 }),
            createPlumbingDevice('dev-valve-b2-01', 'VALVE-B2-01 Main Isolation Valve', 'Belimo', 'Belimo', 'BE-2024-B201', 'online',
                { temperature: 28.0, humidity: 65, power: 0.5, energy: 400, efficiency: 98, pressure: 400, flowRate: 100 },
                { last: '2026-05-01', next: '2026-08-01' }, '2024-01-10', { x: 8, y: -6.2, z: 10 }),
            createPlumbingDevice('dev-valve-b2-02', 'VALVE-B2-02 Zone Control Valve', 'Belimo', 'Belimo', 'BE-2024-B202', 'online',
                { temperature: 29.0, humidity: 66, power: 0.4, energy: 320, efficiency: 97, pressure: 380, flowRate: 80 },
                { last: '2026-05-01', next: '2026-08-01' }, '2024-01-10', { x: 12, y: -6.2, z: 10 })
          ]
        }
      ]
    },
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
            createHVACDevice('dev-ahu-b1-01', 'AHU-B1-01 Ventilation Unit', 'Trane IntelliPak', 'Trane', 'TR-2024-B101', 'online',
                { temperature: 25.0, humidity: 58, power: 20.0, energy: 16000, efficiency: 89, pressure: 260, flowRate: 18000, noiseLevel: 68 },
                { last: '2026-04-20', next: '2026-07-20' }, '2024-01-15', { x: 18, y: -3, z: 5 }),
            createHVACDevice('dev-ahu-b1-02', 'AHU-B1-02 Parking Ventilation', 'Trane IntelliPak', 'Trane', 'TR-2024-B102', 'online',
                { temperature: 26.0, humidity: 60, power: 22.0, energy: 17600, efficiency: 88, pressure: 270, flowRate: 19000, noiseLevel: 70 },
                { last: '2026-04-22', next: '2026-07-22' }, '2024-01-20', { x: 25, y: -3, z: 5 }),
            createHVACDevice('dev-exhaust-b1-01', 'EF-B1-01 CO Exhaust Fan', 'Greenheck CUBE', 'Greenheck', 'GH-2024-B101', 'online',
                { temperature: 28.0, humidity: 62, power: 15.0, energy: 12000, efficiency: 87, pressure: 220, flowRate: 12000, noiseLevel: 72 },
                { last: '2026-05-10', next: '2026-08-10' }, '2024-01-25', { x: 30, y: -3, z: 5 }),
            createHVACDevice('dev-exhaust-b1-02', 'EF-B1-02 CO2 Exhaust Fan', 'Greenheck CUBE', 'Greenheck', 'GH-2024-B102', 'online',
                { temperature: 27.5, humidity: 61, power: 14.0, energy: 11200, efficiency: 88, pressure: 210, flowRate: 11500, noiseLevel: 71 },
                { last: '2026-05-10', next: '2026-08-10' }, '2024-01-25', { x: 35, y: -3, z: 5 }),
            createHVACDevice('dev-supply-b1-01', 'SF-B1-01 Supply Fan', 'Greenheck', 'Greenheck', 'GH-2024-B103', 'online',
                { temperature: 24.5, humidity: 56, power: 18.0, energy: 14400, efficiency: 90, pressure: 240, flowRate: 16000, noiseLevel: 66 },
                { last: '2026-05-12', next: '2026-08-12' }, '2024-02-01', { x: 15, y: -3.2, z: 5 })
          ]
        },
        {
          id: 'sys-lighting-b1', name: 'Lighting System', label: 'Lighting System',
          type: 'system', systemType: 'lighting', status: 'online',
          children: [
            createLightingDevice('dev-light-b1-01', 'LIGHT-B1-01 Parking Controller', 'Schneider KNX', 'Schneider Electric', 'SE-2024-B101', 'online',
                { temperature: 28.0, humidity: 46, power: 5.5, energy: 4400, efficiency: 94 },
                { last: '2026-05-10', next: '2026-08-10' }, '2024-01-25', { x: 10, y: -2.5, z: 8 }),
            createLightingDevice('dev-light-b1-02', 'LIGHT-B1-02 Zone A Lighting', 'Schneider KNX', 'Schneider Electric', 'SE-2024-B102', 'online',
                { temperature: 28.5, humidity: 47, power: 4.2, energy: 3360, efficiency: 93 },
                { last: '2026-05-10', next: '2026-08-10' }, '2024-01-25', { x: 15, y: -2.5, z: 8 }),
            createLightingDevice('dev-light-b1-03', 'LIGHT-B1-03 Zone B Lighting', 'Schneider KNX', 'Schneider Electric', 'SE-2024-B103', 'online',
                { temperature: 27.5, humidity: 45, power: 3.8, energy: 3040, efficiency: 94 },
                { last: '2026-05-10', next: '2026-08-10' }, '2024-01-25', { x: 20, y: -2.5, z: 8 }),
            createLightingDevice('dev-light-b1-04', 'LIGHT-B1-04 Emergency Lighting', 'Lutron Quantum', 'Lutron', 'LT-2024-B101', 'online',
                { temperature: 26.0, humidity: 44, power: 2.0, energy: 1600, efficiency: 96 },
                { last: '2026-05-15', next: '2026-08-15' }, '2024-01-28', { x: 25, y: -2.5, z: 8 })
          ]
        },
        {
          id: 'sys-sas-b1', name: 'Security System', label: 'Security System',
          type: 'system', systemType: 'sas', status: 'online',
          children: [
            createSASDevice('dev-access-b1-01', 'ACS-B1-01 Gate Controller', 'HID VertX', 'HID Global', 'HD-2024-B101', 'online',
                { temperature: 34.0, humidity: 42, power: 0.6, energy: 480, efficiency: 99 },
                { last: '2026-06-01', next: '2026-09-01' }, '2024-01-05', { x: 22, y: -2.8, z: 3 }),
            createSASDevice('dev-access-b1-02', 'ACS-B1-02 Pedestrian Gate', 'HID VertX', 'HID Global', 'HD-2024-B102', 'online',
                { temperature: 33.5, humidity: 41, power: 0.5, energy: 400, efficiency: 99 },
                { last: '2026-06-01', next: '2026-09-01' }, '2024-01-05', { x: 26, y: -2.8, z: 3 }),
            createSASDevice('dev-camera-b1-01', 'CAM-B1-01 PTZ Camera', 'Hikvision DS-2DE', 'Hikvision', 'HK-2024-B101', 'online',
                { temperature: 36.0, humidity: 38, power: 1.2, energy: 960, efficiency: 98 },
                { last: '2026-05-20', next: '2026-08-20' }, '2024-02-01', { x: 24, y: -2.5, z: 5 }),
            createSASDevice('dev-camera-b1-02', 'CAM-B1-02 Fixed Camera', 'Hikvision DS-2CD', 'Hikvision', 'HK-2024-B102', 'online',
                { temperature: 35.5, humidity: 37, power: 0.8, energy: 640, efficiency: 98 },
                { last: '2026-05-22', next: '2026-08-22' }, '2024-02-03', { x: 30, y: -2.5, z: 5 }),
            createSASDevice('dev-camera-b1-03', 'CAM-B1-03 Dome Camera', 'Axis P1448', 'Axis Communications', 'AX-2024-B101', 'online',
                { temperature: 34.0, humidity: 36, power: 0.9, energy: 720, efficiency: 97 },
                { last: '2026-05-25', next: '2026-08-25' }, '2024-02-05', { x: 35, y: -2.5, z: 5 })
          ]
        },
        {
          id: 'sys-fas-b1', name: 'Fire Alarm System', label: 'Fire Alarm System',
          type: 'system', systemType: 'fas', status: 'online',
          children: [
            createFASDevice('dev-smoke-b1-01', 'SD-B1-01 Smoke Detector', 'Honeywell XLS', 'Honeywell', 'HW-2024-B101', 'online',
                { temperature: 22.2, humidity: 64, power: 0.3, energy: 240, efficiency: 98, co2Level: 480, noiseLevel: 14 },
                { last: '2026-04-10', next: '2026-07-10' }, '2024-01-01', { x: 8, y: -2.8, z: 10 }),
            createFASDevice('dev-smoke-b1-02', 'SD-B1-02 Smoke Detector', 'Honeywell XLS', 'Honeywell', 'HW-2024-B102', 'online',
                { temperature: 22.5, humidity: 65, power: 0.3, energy: 240, efficiency: 98, co2Level: 485, noiseLevel: 13 },
                { last: '2026-04-10', next: '2026-07-10' }, '2024-01-01', { x: 14, y: -2.8, z: 10 }),
            createFASDevice('dev-smoke-b1-03', 'SD-B1-03 Smoke Detector', 'Siemens Cerberus', 'Siemens', 'SM-2024-B101', 'online',
                { temperature: 21.8, humidity: 62, power: 0.2, energy: 160, efficiency: 99, co2Level: 470, noiseLevel: 12 },
                { last: '2026-04-12', next: '2026-07-12' }, '2024-01-03', { x: 20, y: -2.8, z: 10 }),
            createFASDevice('dev-heat-b1-01', 'HD-B1-01 Heat Detector', 'Siemens Cerberus', 'Siemens', 'SM-2024-B102', 'online',
                { temperature: 23.0, humidity: 60, power: 0.2, energy: 160, efficiency: 99, noiseLevel: 11 },
                { last: '2026-04-12', next: '2026-07-12' }, '2024-01-03', { x: 28, y: -2.8, z: 12 })
          ]
        },
        {
          id: 'sys-plumbing-b1', name: 'Plumbing System', label: 'Plumbing System',
          type: 'system', systemType: 'plumbing', status: 'online',
          children: [
            createPlumbingDevice('dev-pump-b1-01', 'PUMP-B1-01 Drainage Pump', 'Grundfos CRE', 'Grundfos', 'GF-2024-B101', 'online',
                { temperature: 31.0, humidity: 65, power: 8.0, energy: 6400, efficiency: 90, pressure: 340, flowRate: 50 },
                { last: '2026-05-15', next: '2026-08-15' }, '2023-12-20', { x: 6, y: -3, z: 12 }),
            createPlumbingDevice('dev-pump-b1-02', 'PUMP-B1-02 Grey Water Pump', 'Grundfos CRE', 'Grundfos', 'GF-2024-B102', 'online',
                { temperature: 32.0, humidity: 66, power: 7.5, energy: 6000, efficiency: 91, pressure: 330, flowRate: 48 },
                { last: '2026-05-15', next: '2026-08-15' }, '2023-12-22', { x: 10, y: -3, z: 12 }),
            createPlumbingDevice('dev-backflow-b1-01', 'BACKFLOW-B1-01 Backflow Preventer', 'Watts', 'Watts', 'WT-2024-B101', 'online',
                { temperature: 27.0, humidity: 62, power: 0.3, energy: 240, efficiency: 99, pressure: 400, flowRate: 120 },
                { last: '2026-04-20', next: '2026-07-20' }, '2024-01-10', { x: 14, y: -3, z: 8 })
          ]
        }
      ]
    },
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
            createHVACDevice('dev-ahu-1f-01', 'AHU-1F-01 Air Handler', 'Carrier 39G', 'Carrier', 'CA-2024-1F01', 'online',
                { temperature: 23.5, humidity: 52, power: 12.8, energy: 10240, efficiency: 93, pressure: 245, flowRate: 11500, noiseLevel: 58 },
                { last: '2026-04-20', next: '2026-07-20' }, '2024-01-15', { x: 5, y: 2.5, z: 3 }),
            createHVACDevice('dev-fcu-1f-01', 'FCU-1F-01 Fan Coil Unit', 'Daikin FXMQ', 'Daikin', 'DK-2024-1F01', 'warning',
                { temperature: 25.8, humidity: 58, power: 8.2, energy: 6540, efficiency: 87, pressure: 180, flowRate: 2200, noiseLevel: 42 },
                { last: '2024-03-10', next: '2026-05-10' }, '2023-06-20', { x: 8, y: 2.8, z: 5 }),
            createHVACDevice('dev-fcu-1f-02', 'FCU-1F-02 Fan Coil Unit', 'Daikin FXMQ', 'Daikin', 'DK-2024-1F02', 'online',
                { temperature: 23.0, humidity: 53, power: 7.5, energy: 6000, efficiency: 92, pressure: 175, flowRate: 2100, noiseLevel: 40 },
                { last: '2026-05-01', next: '2026-08-01' }, '2024-02-10', { x: 12, y: 2.8, z: 5 }),
            createHVACDevice('dev-fcu-1f-03', 'FCU-1F-03 Fan Coil Unit', 'Daikin FXMQ', 'Daikin', 'DK-2024-1F03', 'online',
                { temperature: 22.5, humidity: 52, power: 7.0, energy: 5600, efficiency: 93, pressure: 170, flowRate: 2000, noiseLevel: 39 },
                { last: '2026-05-01', next: '2026-08-01' }, '2024-02-10', { x: 16, y: 2.8, z: 5 }),
            createHVACDevice('dev-vav-1f-01', 'VAV-1F-01 VAV Terminal', 'Johnson Controls VAV', 'Johnson Controls', 'JC-2024-1F01', 'online',
                { temperature: 22.0, humidity: 50, power: 1.5, energy: 1200, efficiency: 96, pressure: 120, flowRate: 800 },
                { last: '2026-04-25', next: '2026-07-25' }, '2024-02-01', { x: 20, y: 2.5, z: 3 }),
            createHVACDevice('dev-vav-1f-02', 'VAV-1F-02 VAV Terminal', 'Johnson Controls VAV', 'Johnson Controls', 'JC-2024-1F02', 'online',
                { temperature: 22.2, humidity: 51, power: 1.4, energy: 1120, efficiency: 95, pressure: 118, flowRate: 780 },
                { last: '2026-04-25', next: '2026-07-25' }, '2024-02-01', { x: 24, y: 2.5, z: 3 }),
            createHVACDevice('dev-vav-1f-03', 'VAV-1F-03 VAV Terminal', 'Johnson Controls VAV', 'Johnson Controls', 'JC-2024-1F03', 'online',
                { temperature: 22.4, humidity: 52, power: 1.3, energy: 1040, efficiency: 95, pressure: 115, flowRate: 750 },
                { last: '2026-04-25', next: '2026-07-25' }, '2024-02-01', { x: 28, y: 2.5, z: 3 })
          ]
        },
        {
          id: 'sys-lighting-1f', name: 'Lighting System', label: 'Lighting System',
          type: 'system', systemType: 'lighting', status: 'online',
          children: [
            createLightingDevice('dev-light-1f-01', 'LIGHT-1F-01 Main Controller', 'Philips Dynalite', 'Philips', 'PH-2024-1F01', 'online',
                { temperature: 28.0, humidity: 45, power: 3.5, energy: 2800, efficiency: 95 },
                { last: '2026-05-15', next: '2026-08-15' }, '2024-01-20', { x: 4, y: 3.2, z: 7 }),
            createLightingDevice('dev-light-1f-02', 'LIGHT-1F-02 Lobby Lighting', 'Philips Dynalite', 'Philips', 'PH-2024-1F02', 'online',
                { temperature: 27.5, humidity: 44, power: 4.0, energy: 3200, efficiency: 94 },
                { last: '2026-05-15', next: '2026-08-15' }, '2024-01-20', { x: 8, y: 3.2, z: 7 }),
            createLightingDevice('dev-light-1f-03', 'LIGHT-1F-03 Reception Lighting', 'Philips Dynalite', 'Philips', 'PH-2024-1F03', 'online',
                { temperature: 27.0, humidity: 44, power: 2.5, energy: 2000, efficiency: 96 },
                { last: '2026-05-15', next: '2026-08-15' }, '2024-01-20', { x: 12, y: 3.2, z: 7 }),
            createLightingDevice('dev-light-1f-04', 'LIGHT-1F-04 Emergency Light', 'Schneider KNX', 'Schneider Electric', 'SE-2024-1F01', 'online',
                { temperature: 26.5, humidity: 43, power: 1.2, energy: 960, efficiency: 97 },
                { last: '2026-05-20', next: '2026-08-20' }, '2024-01-25', { x: 16, y: 3.2, z: 7 }),
            createLightingDevice('dev-light-1f-05', 'LIGHT-1F-05 Accent Lighting', 'Schneider KNX', 'Schneider Electric', 'SE-2024-1F02', 'online',
                { temperature: 26.0, humidity: 42, power: 1.8, energy: 1440, efficiency: 96 },
                { last: '2026-05-20', next: '2026-08-20' }, '2024-01-25', { x: 20, y: 3.2, z: 7 })
          ]
        },
        {
          id: 'sys-sas-1f', name: 'Security System', label: 'Security System',
          type: 'system', systemType: 'sas', status: 'online',
          children: [
            createSASDevice('dev-access-1f-01', 'ACS-1F-01 Main Entrance', 'HID VertX', 'HID Global', 'HD-2024-1F01', 'online',
                { temperature: 35.0, humidity: 40, power: 0.5, energy: 400, efficiency: 99 },
                { last: '2026-06-01', next: '2026-09-01' }, '2024-01-05', { x: 3, y: 3.0, z: 2 }),
            createSASDevice('dev-access-1f-02', 'ACS-1F-02 Side Entrance', 'HID VertX', 'HID Global', 'HD-2024-1F02', 'online',
                { temperature: 34.5, humidity: 39, power: 0.5, energy: 400, efficiency: 99 },
                { last: '2026-06-01', next: '2026-09-01' }, '2024-01-05', { x: 7, y: 3.0, z: 2 }),
            createSASDevice('dev-camera-1f-01', 'CAM-1F-01 Dome Camera', 'Hikvision DS-2CD', 'Hikvision', 'HK-2024-1F01', 'online',
                { temperature: 36.5, humidity: 38, power: 0.8, energy: 640, efficiency: 98 },
                { last: '2026-05-25', next: '2026-08-25' }, '2024-02-05', { x: 20, y: 3.2, z: 2 }),
            createSASDevice('dev-camera-1f-02', 'CAM-1F-02 PTZ Camera', 'Hikvision DS-2DE', 'Hikvision', 'HK-2024-1F02', 'online',
                { temperature: 37.0, humidity: 37, power: 1.5, energy: 1200, efficiency: 97 },
                { last: '2026-05-28', next: '2026-08-28' }, '2024-02-08', { x: 25, y: 3.2, z: 2 }),
            createSASDevice('dev-camera-1f-03', 'CAM-1F-03 Fixed Camera', 'Axis P1448', 'Axis Communications', 'AX-2024-1F01', 'online',
                { temperature: 35.5, humidity: 36, power: 0.7, energy: 560, efficiency: 98 },
                { last: '2026-05-30', next: '2026-08-30' }, '2024-02-10', { x: 30, y: 3.2, z: 2 })
          ]
        },
        {
          id: 'sys-fas-1f', name: 'Fire Alarm System', label: 'Fire Alarm System',
          type: 'system', systemType: 'fas', status: 'online',
          children: [
            createFASDevice('dev-smoke-1f-01', 'SD-1F-01 Smoke Detector', 'Honeywell XLS', 'Honeywell', 'HW-2024-1F01', 'online',
                { temperature: 22.0, humidity: 55, power: 0.3, energy: 240, efficiency: 99, co2Level: 440, noiseLevel: 13 },
                { last: '2026-04-10', next: '2026-07-10' }, '2024-01-01', { x: 10, y: 3.5, z: 10 }),
            createFASDevice('dev-smoke-1f-02', 'SD-1F-02 Smoke Detector', 'Honeywell XLS', 'Honeywell', 'HW-2024-1F02', 'online',
                { temperature: 22.3, humidity: 56, power: 0.3, energy: 240, efficiency: 99, co2Level: 445, noiseLevel: 12 },
                { last: '2026-04-10', next: '2026-07-10' }, '2024-01-01', { x: 18, y: 3.5, z: 10 }),
            createFASDevice('dev-smoke-1f-03', 'SD-1F-03 Smoke Detector', 'Siemens Cerberus', 'Siemens', 'SM-2024-1F01', 'online',
                { temperature: 21.5, humidity: 54, power: 0.2, energy: 160, efficiency: 99, co2Level: 435, noiseLevel: 11 },
                { last: '2026-04-12', next: '2026-07-12' }, '2024-01-03', { x: 25, y: 3.5, z: 10 }),
            createFASDevice('dev-heat-1f-01', 'HD-1F-01 Heat Detector', 'Siemens Cerberus', 'Siemens', 'SM-2024-1F02', 'online',
                { temperature: 23.0, humidity: 54, power: 0.2, energy: 160, efficiency: 99, noiseLevel: 10 },
                { last: '2026-04-12', next: '2026-07-12' }, '2024-01-02', { x: 32, y: 3.5, z: 12 }),
            createFASDevice('dev-pull-1f-01', 'PULL-1F-01 Manual Pull Station', 'Honeywell XLS', 'Honeywell', 'HW-2024-1F03', 'online',
                { temperature: 21.0, humidity: 53, power: 0.1, energy: 80, efficiency: 100, noiseLevel: 8 },
                { last: '2026-03-25', next: '2026-06-25' }, '2024-01-05', { x: 5, y: 3.0, z: 4 })
          ]
        }
      ]
    },
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
            createHVACDevice('dev-ahu-2f-01', 'AHU-2F-01 Air Handler', 'Trane IntelliPak', 'Trane', 'TR-2024-2F01', 'error',
                { temperature: 31.2, humidity: 72, power: 22.5, energy: 18500, efficiency: 72, pressure: 195, flowRate: 9800, noiseLevel: 78, vibration: 4.2 },
                { last: '2024-02-28', next: '2026-04-28' }, '2023-08-10', { x: 15, y: 5, z: 4 }),
            createHVACDevice('dev-fcu-2f-01', 'FCU-2F-01 Fan Coil', 'Daikin FXMQ', 'Daikin', 'DK-2024-2F01', 'online',
                { temperature: 24.0, humidity: 55, power: 7.0, energy: 5600, efficiency: 90, pressure: 170, flowRate: 2000, noiseLevel: 40 },
                { last: '2026-05-05', next: '2026-08-05' }, '2024-02-10', { x: 20, y: 5.2, z: 6 }),
            createHVACDevice('dev-fcu-2f-02', 'FCU-2F-02 Fan Coil', 'Daikin FXMQ', 'Daikin', 'DK-2024-2F02', 'online',
                { temperature: 23.5, humidity: 54, power: 6.8, energy: 5440, efficiency: 91, pressure: 168, flowRate: 1950, noiseLevel: 39 },
                { last: '2026-05-05', next: '2026-08-05' }, '2024-02-10', { x: 25, y: 5.2, z: 6 }),
            createHVACDevice('dev-fcu-2f-03', 'FCU-2F-03 Fan Coil', 'Daikin FXMQ', 'Daikin', 'DK-2024-2F03', 'online',
                { temperature: 23.8, humidity: 56, power: 7.2, energy: 5760, efficiency: 90, pressure: 172, flowRate: 2050, noiseLevel: 41 },
                { last: '2026-05-05', next: '2026-08-05' }, '2024-02-10', { x: 30, y: 5.2, z: 6 }),
            createHVACDevice('dev-vav-2f-01', 'VAV-2F-01 VAV Box', 'Johnson Controls VAV', 'Johnson Controls', 'JC-2024-2F01', 'online',
                { temperature: 22.5, humidity: 52, power: 1.0, energy: 800, efficiency: 96, pressure: 105, flowRate: 650 },
                { last: '2026-04-28', next: '2026-07-28' }, '2024-02-05', { x: 35, y: 5.0, z: 4 }),
            createHVACDevice('dev-vav-2f-02', 'VAV-2F-02 VAV Box', 'Johnson Controls VAV', 'Johnson Controls', 'JC-2024-2F02', 'online',
                { temperature: 22.8, humidity: 53, power: 1.1, energy: 880, efficiency: 95, pressure: 108, flowRate: 680 },
                { last: '2026-04-28', next: '2026-07-28' }, '2024-02-05', { x: 40, y: 5.0, z: 4 })
          ]
        },
        {
          id: 'sys-lighting-2f', name: 'Lighting System', label: 'Lighting System',
          type: 'system', systemType: 'lighting', status: 'online',
          children: [
            createLightingDevice('dev-light-2f-01', 'LIGHT-2F-01 Office Controller', 'Lutron Quantum', 'Lutron', 'LT-2024-2F01', 'online',
                { temperature: 27.5, humidity: 43, power: 2.8, energy: 2240, efficiency: 97 },
                { last: '2026-05-18', next: '2026-08-18' }, '2024-01-22', { x: 8, y: 5.5, z: 8 }),
            createLightingDevice('dev-light-2f-02', 'LIGHT-2F-02 Office Lighting', 'Lutron Quantum', 'Lutron', 'LT-2024-2F02', 'online',
                { temperature: 27.0, humidity: 42, power: 3.5, energy: 2800, efficiency: 96 },
                { last: '2026-05-18', next: '2026-08-18' }, '2024-01-22', { x: 12, y: 5.5, z: 8 }),
            createLightingDevice('dev-light-2f-03', 'LIGHT-2F-03 Conference Lighting', 'Lutron Quantum', 'Lutron', 'LT-2024-2F03', 'online',
                { temperature: 26.5, humidity: 41, power: 2.2, energy: 1760, efficiency: 97 },
                { last: '2026-05-18', next: '2026-08-18' }, '2024-01-22', { x: 16, y: 5.5, z: 8 }),
            createLightingDevice('dev-light-2f-04', 'LIGHT-2F-04 Break Room Lighting', 'Schneider KNX', 'Schneider Electric', 'SE-2024-2F01', 'online',
                { temperature: 26.0, humidity: 40, power: 1.8, energy: 1440, efficiency: 98 },
                { last: '2026-05-20', next: '2026-08-20' }, '2024-01-25', { x: 20, y: 5.5, z: 8 })
          ]
        },
        {
          id: 'sys-sas-2f', name: 'Security System', label: 'Security System',
          type: 'system', systemType: 'sas', status: 'online',
          children: [
            createSASDevice('dev-access-2f-01', 'ACS-2F-01 Office Access', 'HID VertX', 'HID Global', 'HD-2024-2F01', 'online',
                { temperature: 34.5, humidity: 41, power: 0.5, energy: 400, efficiency: 99 },
                { last: '2026-06-05', next: '2026-09-05' }, '2024-01-08', { x: 2, y: 5.2, z: 2 }),
            createSASDevice('dev-access-2f-02', 'ACS-2F-02 Server Room Access', 'HID Signo', 'HID Global', 'HD-2024-2F02', 'online',
                { temperature: 35.0, humidity: 40, power: 0.6, energy: 480, efficiency: 98 },
                { last: '2026-06-05', next: '2026-09-05' }, '2024-01-08', { x: 6, y: 5.2, z: 2 }),
            createSASDevice('dev-camera-2f-01', 'CAM-2F-01 Bullet Camera', 'Hikvision DS-2CD', 'Hikvision', 'HK-2024-2F01', 'warning',
                { temperature: 40.0, humidity: 35, power: 1.0, energy: 800, efficiency: 95 },
                { last: '2026-05-22', next: '2026-08-22' }, '2024-02-08', { x: 25, y: 5.5, z: 2 }),
            createSASDevice('dev-camera-2f-02', 'CAM-2F-02 Dome Camera', 'Axis P1448', 'Axis Communications', 'AX-2024-2F01', 'online',
                { temperature: 36.0, humidity: 36, power: 0.9, energy: 720, efficiency: 97 },
                { last: '2026-05-24', next: '2026-08-24' }, '2024-02-10', { x: 30, y: 5.5, z: 2 }),
            createSASDevice('dev-camera-2f-03', 'CAM-2F-03 PTZ Camera', 'Hikvision DS-2DE', 'Hikvision', 'HK-2024-2F02', 'online',
                { temperature: 37.0, humidity: 34, power: 1.3, energy: 1040, efficiency: 96 },
                { last: '2026-05-26', next: '2026-08-26' }, '2024-02-12', { x: 35, y: 5.5, z: 2 })
          ]
        },
        {
          id: 'sys-fas-2f', name: 'Fire Alarm System', label: 'Fire Alarm System',
          type: 'system', systemType: 'fas', status: 'online',
          children: [
            createFASDevice('dev-smoke-2f-01', 'SD-2F-01 Smoke Detector', 'Siemens Cerberus', 'Siemens', 'SM-2024-2F01', 'online',
                { temperature: 22.5, humidity: 53, power: 0.2, energy: 160, efficiency: 99, co2Level: 460, noiseLevel: 11 },
                { last: '2026-04-15', next: '2026-07-15' }, '2024-01-03', { x: 10, y: 5.8, z: 10 }),
            createFASDevice('dev-smoke-2f-02', 'SD-2F-02 Smoke Detector', 'Siemens Cerberus', 'Siemens', 'SM-2024-2F02', 'online',
                { temperature: 22.8, humidity: 54, power: 0.2, energy: 160, efficiency: 99, co2Level: 465, noiseLevel: 11 },
                { last: '2026-04-15', next: '2026-07-15' }, '2024-01-03', { x: 18, y: 5.8, z: 10 }),
            createFASDevice('dev-smoke-2f-03', 'SD-2F-03 Smoke Detector', 'Honeywell XLS', 'Honeywell', 'HW-2024-2F01', 'online',
                { temperature: 22.0, humidity: 52, power: 0.3, energy: 240, efficiency: 99, co2Level: 455, noiseLevel: 12 },
                { last: '2026-04-12', next: '2026-07-12' }, '2024-01-02', { x: 26, y: 5.8, z: 10 }),
            createFASDevice('dev-heat-2f-01', 'HD-2F-01 Heat Detector', 'Siemens Cerberus', 'Siemens', 'SM-2024-2F03', 'online',
                { temperature: 23.5, humidity: 51, power: 0.2, energy: 160, efficiency: 99, noiseLevel: 10 },
                { last: '2026-04-18', next: '2026-07-18' }, '2024-01-05', { x: 32, y: 5.8, z: 12 })
          ]
        },
        {
          id: 'sys-plumbing-2f', name: 'Plumbing System', label: 'Plumbing System',
          type: 'system', systemType: 'plumbing', status: 'online',
          children: [
            createPlumbingDevice('dev-pump-2f-01', 'PUMP-2F-01 Water Supply', 'Grundfos CME', 'Grundfos', 'GF-2024-2F01', 'online',
                { temperature: 30.5, humidity: 58, power: 5.5, energy: 4400, efficiency: 93, pressure: 300, flowRate: 30 },
                { last: '2026-05-12', next: '2026-08-12' }, '2023-12-18', { x: 4, y: 5.0, z: 12 }),
            createPlumbingDevice('dev-pump-2f-02', 'PUMP-2F-02 Hot Water Circulator', 'Grundfos UPS', 'Grundfos', 'GF-2024-2F02', 'online',
                { temperature: 38.0, humidity: 60, power: 3.8, energy: 3040, efficiency: 91, pressure: 260, flowRate: 22 },
                { last: '2026-05-12', next: '2026-08-12' }, '2023-12-20', { x: 8, y: 5.0, z: 13 }),
            createPlumbingDevice('dev-valve-2f-01', 'VALVE-2F-01 Zone Valve', 'Belimo', 'Belimo', 'BE-2024-2F01', 'online',
                { temperature: 27.0, humidity: 55, power: 0.3, energy: 240, efficiency: 98, pressure: 350, flowRate: 45 },
                { last: '2026-05-20', next: '2026-08-20' }, '2024-01-15', { x: 12, y: 5.0, z: 10 })
          ]
        }
      ]
    },
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
            createHVACDevice('dev-ahu-3f-01', 'AHU-3F-01 Precision AC', 'Stulz CyberAir', 'Stulz', 'ST-2024-3F01', 'online',
                { temperature: 22.0, humidity: 48, power: 25.0, energy: 20000, efficiency: 95, pressure: 300, flowRate: 20000, noiseLevel: 55 },
                { last: '2026-04-30', next: '2026-07-30' }, '2024-01-05', { x: 10, y: 8, z: 5 }),
            createHVACDevice('dev-fcu-3f-01', 'FCU-3F-01 Fan Coil', 'Daikin FXMQ', 'Daikin', 'DK-2024-3F01', 'online',
                { temperature: 21.5, humidity: 47, power: 6.5, energy: 5200, efficiency: 92, pressure: 165, flowRate: 1900, noiseLevel: 38 },
                { last: '2026-05-03', next: '2026-08-03' }, '2024-02-08', { x: 15, y: 8.2, z: 6 }),
            createHVACDevice('dev-fcu-3f-02', 'FCU-3F-02 Fan Coil', 'Daikin FXMQ', 'Daikin', 'DK-2024-3F02', 'online',
                { temperature: 21.8, humidity: 48, power: 6.8, energy: 5440, efficiency: 91, pressure: 168, flowRate: 1950, noiseLevel: 39 },
                { last: '2026-05-03', next: '2026-08-03' }, '2024-02-08', { x: 20, y: 8.2, z: 6 }),
            createHVACDevice('dev-vav-3f-01', 'VAV-3F-01 VAV Terminal', 'Johnson Controls VAV', 'Johnson Controls', 'JC-2024-3F01', 'online',
                { temperature: 21.5, humidity: 47, power: 1.2, energy: 960, efficiency: 97, pressure: 110, flowRate: 700 },
                { last: '2026-05-02', next: '2026-08-02' }, '2024-02-05', { x: 25, y: 8.0, z: 7 }),
            createHVACDevice('dev-vav-3f-02', 'VAV-3F-02 VAV Terminal', 'Johnson Controls VAV', 'Johnson Controls', 'JC-2024-3F02', 'online',
                { temperature: 21.3, humidity: 46, power: 1.1, energy: 880, efficiency: 97, pressure: 108, flowRate: 680 },
                { last: '2026-05-02', next: '2026-08-02' }, '2024-02-05', { x: 30, y: 8.0, z: 7 })
          ]
        },
        {
          id: 'sys-lighting-3f', name: 'Lighting System', label: 'Lighting System',
          type: 'system', systemType: 'lighting', status: 'online',
          children: [
            createLightingDevice('dev-light-3f-01', 'LIGHT-3F-01 Executive Controller', 'Lutron HomeWorks', 'Lutron', 'LT-2024-3F01', 'online',
                { temperature: 26.0, humidity: 42, power: 2.0, energy: 1600, efficiency: 98 },
                { last: '2026-05-20', next: '2026-08-20' }, '2024-01-30', { x: 6, y: 8.5, z: 9 }),
            createLightingDevice('dev-light-3f-02', 'LIGHT-3F-02 Office Lighting', 'Lutron HomeWorks', 'Lutron', 'LT-2024-3F02', 'online',
                { temperature: 25.5, humidity: 41, power: 2.5, energy: 2000, efficiency: 97 },
                { last: '2026-05-20', next: '2026-08-20' }, '2024-01-30', { x: 10, y: 8.5, z: 9 }),
            createLightingDevice('dev-light-3f-03', 'LIGHT-3F-03 Conference Lighting', 'Lutron HomeWorks', 'Lutron', 'LT-2024-3F03', 'online',
                { temperature: 25.0, humidity: 40, power: 1.5, energy: 1200, efficiency: 98 },
                { last: '2026-05-20', next: '2026-08-20' }, '2024-01-30', { x: 14, y: 8.5, z: 9 })
          ]
        },
        {
          id: 'sys-sas-3f', name: 'Security System', label: 'Security System',
          type: 'system', systemType: 'sas', status: 'online',
          children: [
            createSASDevice('dev-access-3f-01', 'ACS-3F-01 Biometric Access', 'HID Signo', 'HID Global', 'HD-2024-3F01', 'online',
                { temperature: 33.0, humidity: 39, power: 0.8, energy: 640, efficiency: 99 },
                { last: '2026-06-10', next: '2026-09-10' }, '2024-01-10', { x: 2, y: 8.2, z: 2 }),
            createSASDevice('dev-access-3f-02', 'ACS-3F-02 Executive Access', 'HID Signo', 'HID Global', 'HD-2024-3F02', 'online',
                { temperature: 32.5, humidity: 38, power: 0.7, energy: 560, efficiency: 99 },
                { last: '2026-06-10', next: '2026-09-10' }, '2024-01-10', { x: 5, y: 8.2, z: 2 }),
            createSASDevice('dev-camera-3f-01', 'CAM-3F-01 4K Camera', 'Axis P1448', 'Axis Communications', 'AX-2024-3F01', 'online',
                { temperature: 35.0, humidity: 37, power: 1.5, energy: 1200, efficiency: 97 },
                { last: '2026-05-28', next: '2026-08-28' }, '2024-02-10', { x: 24, y: 8.5, z: 2 }),
            createSASDevice('dev-camera-3f-02', 'CAM-3F-02 PTZ Camera', 'Hikvision DS-2DE', 'Hikvision', 'HK-2024-3F01', 'online',
                { temperature: 36.0, humidity: 36, power: 1.2, energy: 960, efficiency: 97 },
                { last: '2026-05-30', next: '2026-08-30' }, '2024-02-12', { x: 28, y: 8.5, z: 2 })
          ]
        },
        {
          id: 'sys-fas-3f', name: 'Fire Alarm System', label: 'Fire Alarm System',
          type: 'system', systemType: 'fas', status: 'online',
          children: [
            createFASDevice('dev-smoke-3f-01', 'SD-3F-01 Smoke Detector', 'Siemens Cerberus', 'Siemens', 'SM-2024-3F01', 'online',
                { temperature: 21.8, humidity: 52, power: 0.2, energy: 160, efficiency: 99, co2Level: 450, noiseLevel: 10 },
                { last: '2026-04-18', next: '2026-07-18' }, '2024-01-05', { x: 8, y: 8.8, z: 11 }),
            createFASDevice('dev-smoke-3f-02', 'SD-3F-02 Smoke Detector', 'Siemens Cerberus', 'Siemens', 'SM-2024-3F02', 'online',
                { temperature: 22.0, humidity: 53, power: 0.2, energy: 160, efficiency: 99, co2Level: 455, noiseLevel: 10 },
                { last: '2026-04-18', next: '2026-07-18' }, '2024-01-05', { x: 15, y: 8.8, z: 11 }),
            createFASDevice('dev-smoke-3f-03', 'SD-3F-03 Smoke Detector', 'Honeywell XLS', 'Honeywell', 'HW-2024-3F01', 'online',
                { temperature: 21.5, humidity: 51, power: 0.3, energy: 240, efficiency: 99, co2Level: 448, noiseLevel: 12 },
                { last: '2026-04-15', next: '2026-07-15' }, '2024-01-03', { x: 22, y: 8.8, z: 11 }),
            createFASDevice('dev-heat-3f-01', 'HD-3F-01 Heat Detector', 'Siemens Cerberus', 'Siemens', 'SM-2024-3F03', 'online',
                { temperature: 23.0, humidity: 50, power: 0.2, energy: 160, efficiency: 99, noiseLevel: 9 },
                { last: '2026-04-20', next: '2026-07-20' }, '2024-01-06', { x: 28, y: 8.8, z: 13 })
          ]
        },
        {
          id: 'sys-plumbing-3f', name: 'Plumbing System', label: 'Plumbing System',
          type: 'system', systemType: 'plumbing', status: 'online',
          children: [
            createPlumbingDevice('dev-pump-3f-01', 'PUMP-3F-01 Hot Water Pump', 'Grundfos UPS', 'Grundfos', 'GF-2024-3F01', 'online',
                { temperature: 45.0, humidity: 55, power: 4.0, energy: 3200, efficiency: 92, pressure: 280, flowRate: 25 },
                { last: '2026-05-08', next: '2026-08-08' }, '2023-12-22', { x: 4, y: 8.0, z: 13 }),
            createPlumbingDevice('dev-pump-3f-02', 'PUMP-3F-02 Cold Water Pump', 'Grundfos CME', 'Grundfos', 'GF-2024-3F02', 'online',
                { temperature: 29.0, humidity: 52, power: 3.5, energy: 2800, efficiency: 94, pressure: 310, flowRate: 28 },
                { last: '2026-05-10', next: '2026-08-10' }, '2023-12-25', { x: 8, y: 8.0, z: 12 })
          ]
        }
      ]
    },
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
            createHVACDevice('dev-chiller-roof-01', 'CH-RF-01 Chiller', 'Carrier AquaEdge', 'Carrier', 'CA-2024-RF01', 'online',
                { temperature: 35.0, humidity: 75, power: 150.0, energy: 120000, efficiency: 88, pressure: 450, flowRate: 80000, noiseLevel: 85 },
                { last: '2026-04-01', next: '2026-07-01' }, '2024-01-01', { x: 10, y: 12, z: 5 }),
            createHVACDevice('dev-chiller-roof-02', 'CH-RF-02 Chiller', 'Carrier AquaEdge', 'Carrier', 'CA-2024-RF02', 'online',
                { temperature: 34.5, humidity: 74, power: 148.0, energy: 118400, efficiency: 88, pressure: 445, flowRate: 78000, noiseLevel: 84 },
                { last: '2026-04-01', next: '2026-07-01' }, '2024-01-01', { x: 15, y: 12, z: 5 }),
            createHVACDevice('dev-cooling-roof-01', 'CT-RF-01 Cooling Tower', 'BAC 3000', 'Baltimore Aircoil', 'BA-2024-RF01', 'online',
                { temperature: 38.0, humidity: 80, power: 45.0, energy: 36000, efficiency: 85, pressure: 200, flowRate: 60000, noiseLevel: 90 },
                { last: '2026-04-05', next: '2026-07-05' }, '2024-01-01', { x: 20, y: 12, z: 5 }),
            createHVACDevice('dev-cooling-roof-02', 'CT-RF-02 Cooling Tower', 'BAC 3000', 'Baltimore Aircoil', 'BA-2024-RF02', 'online',
                { temperature: 37.5, humidity: 79, power: 44.0, energy: 35200, efficiency: 85, pressure: 198, flowRate: 58000, noiseLevel: 89 },
                { last: '2026-04-05', next: '2026-07-05' }, '2024-01-01', { x: 25, y: 12, z: 5 }),
            createHVACDevice('dev-pump-roof-01', 'CHWP-RF-01 Primary Pump', 'Grundfos CR', 'Grundfos', 'GF-2024-RF01', 'online',
                { temperature: 36.0, humidity: 72, power: 55.0, energy: 44000, efficiency: 90, pressure: 420, flowRate: 25000, noiseLevel: 75 },
                { last: '2026-04-08', next: '2026-07-08' }, '2024-01-05', { x: 5, y: 12, z: 4 }),
            createHVACDevice('dev-pump-roof-02', 'CHWP-RF-02 Secondary Pump', 'Grundfos CR', 'Grundfos', 'GF-2024-RF02', 'online',
                { temperature: 35.5, humidity: 71, power: 52.0, energy: 41600, efficiency: 91, pressure: 415, flowRate: 24000, noiseLevel: 74 },
                { last: '2026-04-08', next: '2026-07-08' }, '2024-01-05', { x: 8, y: 12, z: 4 })
          ]
        },
        {
          id: 'sys-fas-roof', name: 'Fire Alarm System', label: 'Fire Alarm System',
          type: 'system', systemType: 'fas', status: 'online',
          children: [
            createFASDevice('dev-smoke-roof-01', 'SD-RF-01 Smoke Detector', 'Honeywell XLS', 'Honeywell', 'HW-2024-RF01', 'online',
                { temperature: 30.0, humidity: 70, power: 0.3, energy: 240, efficiency: 98, co2Level: 500, noiseLevel: 18 },
                { last: '2026-04-20', next: '2026-07-20' }, '2024-01-05', { x: 15, y: 12.5, z: 12 }),
            createFASDevice('dev-smoke-roof-02', 'SD-RF-02 Smoke Detector', 'Honeywell XLS', 'Honeywell', 'HW-2024-RF02', 'online',
                { temperature: 29.5, humidity: 69, power: 0.3, energy: 240, efficiency: 98, co2Level: 495, noiseLevel: 17 },
                { last: '2026-04-20', next: '2026-07-20' }, '2024-01-05', { x: 22, y: 12.5, z: 12 }),
            createFASDevice('dev-heat-roof-01', 'HD-RF-01 Heat Detector', 'Siemens Cerberus', 'Siemens', 'SM-2024-RF01', 'online',
                { temperature: 32.0, humidity: 68, power: 0.2, energy: 160, efficiency: 99, noiseLevel: 14 },
                { last: '2026-04-22', next: '2026-07-22' }, '2024-01-08', { x: 28, y: 12.5, z: 14 })
          ]
        },
        {
          id: 'sys-plumbing-roof', name: 'Plumbing System', label: 'Plumbing System',
          type: 'system', systemType: 'plumbing', status: 'online',
          children: [
            createPlumbingDevice('dev-tank-roof-01', 'TANK-RF-01 Water Tank', 'GRP Modular', 'ZCL Composites', 'ZC-2024-RF01', 'online',
                { temperature: 28.0, humidity: 75, power: 2.0, energy: 1600, efficiency: 95, pressure: 150, flowRate: 100 },
                { last: '2026-05-01', next: '2026-08-01' }, '2024-01-01', { x: 5, y: 12, z: 15 }),
            createPlumbingDevice('dev-tank-roof-02', 'TANK-RF-02 Boiler Feed Tank', 'GRP Modular', 'ZCL Composites', 'ZC-2024-RF02', 'online',
                { temperature: 32.0, humidity: 78, power: 1.8, energy: 1440, efficiency: 94, pressure: 160, flowRate: 90 },
                { last: '2026-05-01', next: '2026-08-01' }, '2024-01-01', { x: 10, y: 12, z: 15 }),
            createPlumbingDevice('dev-pump-roof-plumb-01', 'ROOF-PUMP-01 Pressure Booster', 'Grundfos Hydro', 'Grundfos', 'GF-2024-RF03', 'online',
                { temperature: 31.0, humidity: 70, power: 12.0, energy: 9600, efficiency: 89, pressure: 500, flowRate: 80 },
                { last: '2026-05-05', next: '2026-08-05' }, '2024-01-10', { x: 14, y: 12, z: 8 })
          ]
        }
      ]
    }
  ]
}

// ==================== Device Image URL Map ====================
// ==================== Device Image URL Map ====================
// 按设备类型分组，相同类型的设备集中在一起
const deviceImageUrls: Record<string, string> = {
  // ==================== 空气处理机组 (AHU) ====================
  'dev-ahu-b2-01': 'https://aegisnx.com/wp-content/uploads/2026/05/5201314567.webp',        // AHU-B2-01 空气处理机组
  'dev-ahu-b1-01': 'https://aegisnx.com/wp-content/uploads/2026/05/5201314567.webp',        // AHU-B1-01 通风机组
  'dev-ahu-b1-02': 'https://aegisnx.com/wp-content/uploads/2026/05/5201314567.webp',        // AHU-B1-02 停车场通风机
  'dev-ahu-1f-01': 'https://aegisnx.com/wp-content/uploads/2026/05/5201314567.webp',        // AHU-1F-01 空气处理机组
  'dev-ahu-2f-01': 'https://aegisnx.com/wp-content/uploads/2026/05/5201314567.webp',        // AHU-2F-01 空气处理机组（故障）
  'dev-ahu-3f-01': 'https://aegisnx.com/wp-content/uploads/2026/05/5201314567.webp',        // AHU-3F-01 精密空调

  // ==================== 风机盘管 (FCU) ====================
  'dev-fcu-b2-01': 'https://aegisnx.com/wp-content/uploads/2026/05/52013141234431.webp',        // FCU-B2-01 风机盘管
  'dev-fcu-1f-01': 'https://aegisnx.com/wp-content/uploads/2026/05/52013141234431.webp',        // FCU-1F-01 风机盘管
  'dev-fcu-1f-02': 'https://aegisnx.com/wp-content/uploads/2026/05/52013141234431.webp',        // FCU-1F-02 风机盘管
  'dev-fcu-1f-03': 'https://aegisnx.com/wp-content/uploads/2026/05/52013141234431.webp',        // FCU-1F-03 风机盘管
  'dev-fcu-2f-01': 'https://aegisnx.com/wp-content/uploads/2026/05/52013141234431.webp',        // FCU-2F-01 风机盘管
  'dev-fcu-2f-02': 'https://aegisnx.com/wp-content/uploads/2026/05/52013141234431.webp',        // FCU-2F-02 风机盘管
  'dev-fcu-2f-03': 'https://aegisnx.com/wp-content/uploads/2026/05/52013141234431.webp',        // FCU-2F-03 风机盘管
  'dev-fcu-3f-01': 'https://aegisnx.com/wp-content/uploads/2026/05/52013141234431.webp',        // FCU-3F-01 风机盘管
  'dev-fcu-3f-02': 'https://aegisnx.com/wp-content/uploads/2026/05/52013141234431.webp',        // FCU-3F-02 风机盘管

  // ==================== 冷水机组 / 冷却塔 ====================
  'dev-chiller-b2-01': 'https://aegisnx.com/wp-content/uploads/2026/05/52013145678.jpg',    // CH-B2-01 冷水机组
  'dev-chiller-roof-01': 'https://aegisnx.com/wp-content/uploads/2026/05/52013145678.jpg',  // CH-RF-01 冷水机组
  'dev-chiller-roof-02': 'https://aegisnx.com/wp-content/uploads/2026/05/52013145678.jpg',  // CH-RF-02 冷水机组
  'dev-cooling-b2-01': 'https://aegisnx.com/wp-content/uploads/2026/05/52013145678.jpg',    // CT-B2-01 冷却塔
  'dev-cooling-roof-01': 'https://aegisnx.com/wp-content/uploads/2026/05/52013145678.jpg',  // CT-RF-01 冷却塔
  'dev-cooling-roof-02': 'https://aegisnx.com/wp-content/uploads/2026/05/52013145678.jpg',  // CT-RF-02 冷却塔

  // ==================== 水泵 ====================
  'dev-pump-hvac-b2-01': 'https://aegisnx.com/wp-content/uploads/2026/05/1779181211735.png', // CHWP-B2-01 冷冻水泵
  'dev-pump-hvac-b2-02': 'https://aegisnx.com/wp-content/uploads/2026/05/1779181211735.png',  // CWP-B2-01 冷却水泵
  'dev-pump-roof-01': 'https://aegisnx.com/wp-content/uploads/2026/05/1779181211735.png',   // CHWP-RF-01 一级泵
  'dev-pump-roof-02': 'https://aegisnx.com/wp-content/uploads/2026/05/1779181211735.png',    // CHWP-RF-02 二级泵
  'dev-pump-b2-01': 'https://aegisnx.com/wp-content/uploads/2026/05/1779181211735.png',      // PUMP-B2-01 污水泵
  'dev-pump-b2-02': 'https://aegisnx.com/wp-content/uploads/2026/05/1779181211735.png',       // PUMP-B2-02 增压泵
  'dev-pump-b2-03': 'https://aegisnx.com/wp-content/uploads/2026/05/1779181211735.png',      // PUMP-B2-03 排水泵
  'dev-pump-b1-01': 'https://aegisnx.com/wp-content/uploads/2026/05/1779181211735.png',       // PUMP-B1-01 排水泵
  'dev-pump-b1-02': 'https://aegisnx.com/wp-content/uploads/2026/05/1779181211735.png',       // PUMP-B1-02 灰水泵
  'dev-pump-2f-01': 'https://aegisnx.com/wp-content/uploads/2026/05/1779181211735.png',       // PUMP-2F-01 供水泵
  'dev-pump-2f-02': 'https://aegisnx.com/wp-content/uploads/2026/05/1779181211735.png',       // PUMP-2F-02 热水循环泵
  'dev-pump-3f-01': 'https://aegisnx.com/wp-content/uploads/2026/05/1779181211735.png',       // PUMP-3F-01 热水泵
  'dev-pump-3f-02': 'https://aegisnx.com/wp-content/uploads/2026/05/1779181211735.png',       // PUMP-3F-02 冷水泵
  'dev-pump-roof-plumb-01': 'https://aegisnx.com/wp-content/uploads/2026/05/1779181211735.png', // ROOF-PUMP-01 压力增压泵

  // ==================== 风机 (排风机/送风机) ====================
  'dev-exhaust-b2-01': 'https://aegisnx.com/wp-content/uploads/2026/05/520131452044.webp',    // EF-B2-01 排风机
  'dev-exhaust-b2-02': 'https://aegisnx.com/wp-content/uploads/2026/05/520131452044.webp',    // EF-B2-02 排风机
  'dev-exhaust-b1-01': 'https://aegisnx.com/wp-content/uploads/2026/05/520131452044.webp',    // EF-B1-01 CO排风机
  'dev-exhaust-b1-02': 'https://aegisnx.com/wp-content/uploads/2026/05/520131452044.webp',    // EF-B1-02 CO2排风机
  'dev-supply-b1-01': 'https://aegisnx.com/wp-content/uploads/2026/05/520131452044.webp',     // SF-B1-01 送风机

  // ==================== 变风量箱 (VAV) ====================
  'dev-vav-b2-01': 'https://aegisnx.com/wp-content/uploads/2026/05/5201314643.webp',        // VAV-B2-01 变风量箱
  'dev-vav-b2-02': 'https://aegisnx.com/wp-content/uploads/2026/05/5201314643.webp',        // VAV-B2-02 变风量箱
  'dev-vav-b2-03': 'https://aegisnx.com/wp-content/uploads/2026/05/5201314643.webp',        // VAV-B2-03 变风量箱
  'dev-vav-1f-01': 'https://aegisnx.com/wp-content/uploads/2026/05/5201314643.webp',        // VAV-1F-01 变风量箱
  'dev-vav-1f-02': 'https://aegisnx.com/wp-content/uploads/2026/05/5201314643.webp',        // VAV-1F-02 变风量箱
  'dev-vav-1f-03': 'https://aegisnx.com/wp-content/uploads/2026/05/5201314643.webp',        // VAV-1F-03 变风量箱
  'dev-vav-2f-01': 'https://aegisnx.com/wp-content/uploads/2026/05/5201314643.webp',        // VAV-2F-01 变风量箱
  'dev-vav-2f-02': 'https://aegisnx.com/wp-content/uploads/2026/05/5201314643.webp',        // VAV-2F-02 变风量箱
  'dev-vav-3f-01': 'https://aegisnx.com/wp-content/uploads/2026/05/5201314643.webp',        // VAV-3F-01 变风量箱
  'dev-vav-3f-02': 'https://aegisnx.com/wp-content/uploads/2026/05/5201314643.webp',        // VAV-3F-02 变风量箱

  // ==================== 照明设备 ====================
  'dev-light-b2-01': 'https://aegisnx.com/wp-content/uploads/2026/05/52013147890.webp',          // LIGHT-B2-01 主控制器
  'dev-light-b2-02': 'https://aegisnx.com/wp-content/uploads/2026/05/52013147890.webp',          // LIGHT-B2-02 A区照明
  'dev-light-b2-03': 'https://aegisnx.com/wp-content/uploads/2026/05/52013147890.webp',          // LIGHT-B2-03 B区照明
  'dev-light-b2-04': 'https://aegisnx.com/wp-content/uploads/2026/05/52013147890.webp',      // LIGHT-B2-04 应急照明
  'dev-light-b2-05': 'https://aegisnx.com/wp-content/uploads/2026/05/52013147890.webp',      // LIGHT-B2-05 楼梯间照明
  'dev-light-b1-01': 'https://aegisnx.com/wp-content/uploads/2026/05/52013147890.webp',      // LIGHT-B1-01 停车场控制器
  'dev-light-b1-02': 'https://aegisnx.com/wp-content/uploads/2026/05/52013147890.webp',      // LIGHT-B1-02 A区照明
  'dev-light-b1-03': 'https://aegisnx.com/wp-content/uploads/2026/05/52013147890.webp',      // LIGHT-B1-03 B区照明
  'dev-light-b1-04': 'https://aegisnx.com/wp-content/uploads/2026/05/52013147890.webp',      // LIGHT-B1-04 应急照明
  'dev-light-1f-01': 'https://aegisnx.com/wp-content/uploads/2026/05/52013147890.webp',      // LIGHT-1F-01 主控制器
  'dev-light-1f-02': 'https://aegisnx.com/wp-content/uploads/2026/05/52013147890.webp',      // LIGHT-1F-02 大厅照明
  'dev-light-1f-03': 'https://aegisnx.com/wp-content/uploads/2026/05/52013147890.webp',      // LIGHT-1F-03 前台照明
  'dev-light-1f-04': 'https://aegisnx.com/wp-content/uploads/2026/05/52013147890.webp',      // LIGHT-1F-04 应急照明
  'dev-light-1f-05': 'https://aegisnx.com/wp-content/uploads/2026/05/52013147890.webp',      // LIGHT-1F-05 氛围照明
  'dev-light-2f-01': 'https://aegisnx.com/wp-content/uploads/2026/05/52013147890.webp',      // LIGHT-2F-01 办公室控制器
  'dev-light-2f-02': 'https://aegisnx.com/wp-content/uploads/2026/05/52013147890.webp',      // LIGHT-2F-02 办公区照明
  'dev-light-2f-03': 'https://aegisnx.com/wp-content/uploads/2026/05/52013147890.webp',      // LIGHT-2F-03 会议室照明
  'dev-light-2f-04': 'https://aegisnx.com/wp-content/uploads/2026/05/52013147890.webp',      // LIGHT-2F-04 休息区照明
  'dev-light-3f-01': 'https://aegisnx.com/wp-content/uploads/2026/05/52013147890.webp',      // LIGHT-3F-01 高管控制器
  'dev-light-3f-02': 'https://aegisnx.com/wp-content/uploads/2026/05/52013147890.webp',      // LIGHT-3F-02 办公室照明
  'dev-light-3f-03': 'https://aegisnx.com/wp-content/uploads/2026/05/52013147890.webp',      // LIGHT-3F-03 会议室照明

  // ==================== 门禁设备 ====================
  'dev-access-b1-01': 'https://aegisnx.com/wp-content/uploads/2026/05/52013147643.jpg',      // ACS-B1-01 道闸控制器
  'dev-access-b1-02': 'https://aegisnx.com/wp-content/uploads/2026/05/52013147643.jpg',      // ACS-B1-02 人行闸机
  'dev-access-1f-01': 'https://aegisnx.com/wp-content/uploads/2026/05/52013147643.jpg',        // ACS-1F-01 主入口门禁
  'dev-access-1f-02': 'https://aegisnx.com/wp-content/uploads/2026/05/52013147643.jpg',        // ACS-1F-02 侧门门禁
  'dev-access-2f-01': 'https://aegisnx.com/wp-content/uploads/2026/05/52013147643.jpg',     // ACS-2F-01 办公室门禁
  'dev-access-2f-02': 'https://aegisnx.com/wp-content/uploads/2026/05/52013147643.jpg',     // ACS-2F-02 服务器房门禁
  'dev-access-3f-01': 'https://aegisnx.com/wp-content/uploads/2026/05/52013147643.jpg',     // ACS-3F-01 生物识别门禁
  'dev-access-3f-02': 'https://aegisnx.com/wp-content/uploads/2026/05/52013147643.jpg',     // ACS-3F-02 高管区门禁

  // ==================== 摄像头 ====================
  'dev-camera-b1-01': 'https://aegisnx.com/wp-content/uploads/2026/05/5201314234432.webp',        // CAM-B1-01 PTZ球机
  'dev-camera-b1-02': 'https://aegisnx.com/wp-content/uploads/2026/05/5201314234432.webp',        // CAM-B1-02 固定摄像机
  'dev-camera-b1-03': 'https://aegisnx.com/wp-content/uploads/2026/05/5201314234432.webp',        // CAM-B1-03 半球摄像机
  'dev-camera-1f-01': 'https://aegisnx.com/wp-content/uploads/2026/05/5201314234432.webp',        // CAM-1F-01 半球摄像机
  'dev-camera-1f-02': 'https://aegisnx.com/wp-content/uploads/2026/05/5201314234432.webp',        // CAM-1F-02 PTZ球机
  'dev-camera-1f-03': 'https://aegisnx.com/wp-content/uploads/2026/05/5201314234432.webp',        // CAM-1F-03 固定摄像机
  'dev-camera-2f-01': 'https://aegisnx.com/wp-content/uploads/2026/05/5201314234432.webp',     // CAM-2F-01 枪式摄像机
  'dev-camera-2f-02': 'https://aegisnx.com/wp-content/uploads/2026/05/5201314234432.webp',     // CAM-2F-02 半球摄像机
  'dev-camera-2f-03': 'https://aegisnx.com/wp-content/uploads/2026/05/5201314234432.webp',     // CAM-2F-03 PTZ球机
  'dev-camera-3f-01': 'https://aegisnx.com/wp-content/uploads/2026/05/5201314234432.webp',     // CAM-3F-01 4K摄像机
  'dev-camera-3f-02': 'https://aegisnx.com/wp-content/uploads/2026/05/5201314234432.webp',     // CAM-3F-02 PTZ球机

  // ==================== 烟感探测器 ====================
  'dev-smoke-b2-01': 'https://aegisnx.com/wp-content/uploads/2026/05/5201314567123.jpg',        // SD-B2-01 烟感探测器
  'dev-smoke-b2-02': 'https://aegisnx.com/wp-content/uploads/2026/05/5201314567123.jpg',         // SD-B2-02 烟感探测器
  'dev-smoke-b2-03': 'https://aegisnx.com/wp-content/uploads/2026/05/5201314567123.jpg',        // SD-B2-03 烟感探测器
  'dev-smoke-b2-04': 'https://aegisnx.com/wp-content/uploads/2026/05/5201314567123.jpg',        // SD-B2-04 烟感探测器
  'dev-smoke-b1-01': 'https://aegisnx.com/wp-content/uploads/2026/05/5201314567123.jpg',         // SD-B1-01 烟感探测器
  'dev-smoke-b1-02': 'https://aegisnx.com/wp-content/uploads/2026/05/5201314567123.jpg',         // SD-B1-02 烟感探测器
  'dev-smoke-b1-03': 'https://aegisnx.com/wp-content/uploads/2026/05/5201314567123.jpg',         // SD-B1-03 烟感探测器
  'dev-smoke-1f-01': 'https://aegisnx.com/wp-content/uploads/2026/05/5201314567123.jpg',      // SD-1F-01 烟感探测器
  'dev-smoke-1f-02': 'https://aegisnx.com/wp-content/uploads/2026/05/5201314567123.jpg',      // SD-1F-02 烟感探测器
  'dev-smoke-1f-03': 'https://aegisnx.com/wp-content/uploads/2026/05/5201314567123.jpg',      // SD-1F-03 烟感探测器
  'dev-smoke-2f-01': 'https://aegisnx.com/wp-content/uploads/2026/05/5201314567123.jpg',      // SD-2F-01 烟感探测器
  'dev-smoke-2f-02': 'https://aegisnx.com/wp-content/uploads/2026/05/5201314567123.jpg',      // SD-2F-02 烟感探测器
  'dev-smoke-2f-03': 'https://aegisnx.com/wp-content/uploads/2026/05/5201314567123.jpg',      // SD-2F-03 烟感探测器
  'dev-smoke-3f-01': 'https://aegisnx.com/wp-content/uploads/2026/05/5201314567123.jpg',      // SD-3F-01 烟感探测器
  'dev-smoke-3f-02': 'https://aegisnx.com/wp-content/uploads/2026/05/5201314567123.jpg',      // SD-3F-02 烟感探测器
  'dev-smoke-3f-03': 'https://aegisnx.com/wp-content/uploads/2026/05/5201314567123.jpg',      // SD-3F-03 烟感探测器
  'dev-smoke-roof-01': 'https://aegisnx.com/wp-content/uploads/2026/05/5201314567123.jpg',    // SD-RF-01 烟感探测器
  'dev-smoke-roof-02': 'https://aegisnx.com/wp-content/uploads/2026/05/5201314567123.jpg',    // SD-RF-02 烟感探测器

  // ==================== 温感探测器 ====================
  'dev-heat-b2-01': 'https://aegisnx.com/wp-content/uploads/2026/05/52013144312.webp',       // HD-B2-01 温感探测器
  'dev-heat-b1-01': 'https://aegisnx.com/wp-content/uploads/2026/05/52013144312.webp',       // HD-B1-01 温感探测器
  'dev-heat-1f-01': 'https://aegisnx.com/wp-content/uploads/2026/05/52013144312.webp',       // HD-1F-01 温感探测器
  'dev-heat-2f-01': 'https://aegisnx.com/wp-content/uploads/2026/05/52013144312.webp',       // HD-2F-01 温感探测器
  'dev-heat-3f-01': 'https://aegisnx.com/wp-content/uploads/2026/05/52013144312.webp',       // HD-3F-01 温感探测器
  'dev-heat-roof-01': 'https://aegisnx.com/wp-content/uploads/2026/05/52013144312.webp',     // HD-RF-01 温感探测器

  // ==================== 手动报警按钮 ====================
  'dev-pull-b2-01': 'https://aegisnx.com/wp-content/uploads/2026/05/520131478231.webp',          // PULL-B2-01 手动报警按钮
  'dev-pull-1f-01': 'https://aegisnx.com/wp-content/uploads/2026/05/520131478231.webp',          // PULL-1F-01 手动报警按钮

  // ==================== 阀门 ====================
  'dev-valve-b2-01': 'https://aegisnx.com/wp-content/uploads/2026/05/5201314434.webp',      // VALVE-B2-01 主隔离阀
  'dev-valve-b2-02': 'https://aegisnx.com/wp-content/uploads/2026/05/5201314434.webp',      // VALVE-B2-02 分区控制阀
  'dev-valve-2f-01': 'https://aegisnx.com/wp-content/uploads/2026/05/5201314434.webp',      // VALVE-2F-01 分区阀门

  // ==================== 其他设备 ====================
  'dev-backflow-b1-01': 'https://aegisnx.com/wp-content/uploads/2026/05/579793395.jpg',   // BACKFLOW-B1-01 防倒流器
  'dev-tank-roof-01': 'https://aegisnx.com/wp-content/uploads/2026/05/520131467123.webp',     // TANK-RF-01 水箱
  'dev-tank-roof-02': 'https://aegisnx.com/wp-content/uploads/2026/05/520131467123.webp'      // TANK-RF-02 锅炉补水水箱
}

const defaultDeviceImage = 'https://aegisnx.com/wp-content/uploads/2026/05/1779084477643.png'

// ==================== Preload All Device Images ====================
const preloadAllImages = (): Promise<void> => {
  return new Promise((resolve) => {
    const allUrls = [...new Set([
      ...Object.values(deviceImageUrls),
      defaultDeviceImage
    ])]

    const totalImages = allUrls.length
    let loadedCount = 0
    let messageIndex = 0

    const messageInterval = setInterval(() => {
      if (messageIndex < loadingMessages.length - 1) {
        messageIndex++
        const msg = loadingMessages[messageIndex]
        if (msg) {
          loadingMessage.value = msg
        }
      }
    }, 600)

    if (totalImages === 0) {
      clearInterval(messageInterval)
      loadingProgress.value = 100
      loadingMessage.value = 'Ready!'
      setTimeout(() => resolve(), 400)
      return
    }

    allUrls.forEach((url) => {
      const img = new Image()

      img.onload = () => {
        loadedCount++
        loadingProgress.value = Math.round((loadedCount / totalImages) * 100)

        if (loadingProgress.value > 80) {
          loadingMessage.value = loadingMessages[4] || ''
        } else if (loadingProgress.value > 60) {
          loadingMessage.value = loadingMessages[3] || ''
        } else if (loadingProgress.value > 40) {
          loadingMessage.value = loadingMessages[2] || ''
        } else if (loadingProgress.value > 20) {
          loadingMessage.value = loadingMessages[1] || ''
        }

        if (loadedCount >= totalImages) {
          clearInterval(messageInterval)
          loadingMessage.value = 'Ready!'
          loadingProgress.value = 100
          setTimeout(() => resolve(), 500)
        }
      }

      img.onerror = () => {
        loadedCount++
        loadingProgress.value = Math.round((loadedCount / totalImages) * 100)

        if (loadedCount >= totalImages) {
          clearInterval(messageInterval)
          loadingMessage.value = 'Loading complete'
          loadingProgress.value = 100
          setTimeout(() => resolve(), 300)
        }
      }

      img.src = url
    })
  })
}

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

// ==================== Helper function to get device image ====================
const getDeviceImageUrl = (deviceId: string): string => {
  return deviceImageUrls[deviceId] || defaultDeviceImage
}

// ==================== Helper to create devices ====================
const createHVACDevice = (
    id: string, name: string, model: string, manufacturer: string,
    serial: string, status: DeviceNode['status'],
    metrics: Partial<DeviceMetrics>, maintenance: { last: string; next: string },
    install: string, pos: { x: number; y: number; z: number }
): DeviceNode => {
  return {
    id, name, type: 'device', status, model, manufacturer,
    serialNumber: serial, systemType: 'hvac',
    imageUrl: getDeviceImageUrl(id),
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
    serial: string, status: DeviceNode['status'],
    metrics: Partial<DeviceMetrics>, maintenance: { last: string; next: string },
    install: string, pos: { x: number; y: number; z: number }
): DeviceNode => {
  return {
    id, name, type: 'device', status, model, manufacturer,
    serialNumber: serial, systemType: 'lighting',
    imageUrl: getDeviceImageUrl(id),
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
    serial: string, status: DeviceNode['status'],
    metrics: Partial<DeviceMetrics>, maintenance: { last: string; next: string },
    install: string, pos: { x: number; y: number; z: number }
): DeviceNode => {
  return {
    id, name, type: 'device', status, model, manufacturer,
    serialNumber: serial, systemType: 'sas',
    imageUrl: getDeviceImageUrl(id),
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
    serial: string, status: DeviceNode['status'],
    metrics: Partial<DeviceMetrics>, maintenance: { last: string; next: string },
    install: string, pos: { x: number; y: number; z: number }
): DeviceNode => {
  return {
    id, name, type: 'device', status, model, manufacturer,
    serialNumber: serial, systemType: 'fas',
    imageUrl: getDeviceImageUrl(id),
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
    serial: string, status: DeviceNode['status'],
    metrics: Partial<DeviceMetrics>, maintenance: { last: string; next: string },
    install: string, pos: { x: number; y: number; z: number }
): DeviceNode => {
  return {
    id, name, type: 'device', status, model, manufacturer,
    serialNumber: serial, systemType: 'plumbing',
    imageUrl: getDeviceImageUrl(id),
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

const focusedDevice = ref<DeviceNode | null>(null)
const focusChartRef = ref<HTMLElement>()
let focusChartInstance: echarts.ECharts | null = null

const leftPanelWidth = ref(300)
const isResizingLeft = ref(false)

const treeRef = ref()
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

// 按区域分组的设备列表（用于网格视图和列表视图）
const groupedDevicesByArea = computed(() => {
  const devicesByArea: { areaId: string; areaName: string; devices: DeviceNode[] }[] = []

  // 如果选择了具体的系统，则只显示该系统下的设备，但按区域分组（该系统的设备可能来自多个区域？）
  // 实际上一个系统只属于一个区域，但为了保持一致，仍然按区域分组
  if (selectedSystem.value) {
    // 找到该系统所属的区域
    let parentArea: AreaNode | undefined
    const currentData = currentFloor.value === 'All Floors'
        ? topologyData.value
        : topologyData.value.filter(area => area.floor === currentFloor.value)

    for (const area of currentData) {
      const found = area.children?.find(sys => sys.id === selectedSystem.value?.id)
      if (found) {
        parentArea = area
        break
      }
    }

    if (parentArea && selectedSystem.value.children && selectedSystem.value.children.length > 0) {
      devicesByArea.push({
        areaId: parentArea.id,
        areaName: parentArea.name,
        devices: [...selectedSystem.value.children]
      })
    }
  } else {
    // 没有选择系统时，显示所有设备，按区域分组
    const areaMap = new Map<string, { areaId: string; areaName: string; devices: DeviceNode[] }>()
    const currentData = currentFloor.value === 'All Floors'
        ? topologyData.value
        : topologyData.value.filter(area => area.floor === currentFloor.value)

    for (const area of currentData) {
      if (!areaMap.has(area.id)) {
        areaMap.set(area.id, { areaId: area.id, areaName: area.name, devices: [] })
      }
      for (const system of area.children || []) {
        for (const device of system.children || []) {
          areaMap.get(area.id)!.devices.push(device)
        }
      }
    }

    // 转换为数组，并过滤掉没有设备的区域
    for (const [_, group] of areaMap) {
      if (group.devices.length > 0) {
        devicesByArea.push(group)
      }
    }
  }

  return devicesByArea
})

const displayDevices = computed(() => {
  if (selectedSystem.value) {
    return selectedSystem.value.children || []
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
  const device = focusedDevice.value || selectedDevice.value
  if (!device) return []
  const m = device.metrics
  return [
    { key: 'temperature', label: 'Temperature', value: m.temperature, unit: '°C', icon: ColdDrink, warning: m.temperature > 28, max: 50 },
    { key: 'humidity', label: 'Humidity', value: m.humidity, unit: '%', icon: Sunny, warning: m.humidity > 65, max: 100 },
    { key: 'power', label: 'Power', value: m.power, unit: 'kW', icon: Odometer, warning: m.power > 20, max: 200 },
    { key: 'energy', label: 'Energy', value: m.energy.toLocaleString(), unit: 'kWh', icon: TrendCharts, warning: false, max: 200000 },
    { key: 'efficiency', label: 'Efficiency', value: m.efficiency, unit: '%', icon: MagicStick, warning: m.efficiency < 80, max: 100 },
    { key: 'uptime', label: 'Uptime', value: Math.floor(m.uptime / 24), unit: 'days', icon: Switch, warning: false, max: 365 }
  ]
})

const isMaintenanceOverdue = computed(() => {
  const device = focusedDevice.value || selectedDevice.value
  if (!device) return false
  return new Date(device.nextMaintenance) < new Date()
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

const getMetricPercentage = (metric: any) => {
  if (!metric.max) return 50
  return Math.min(100, (metric.value / metric.max) * 100)
}

const getHeatmapOpacity = (device: DeviceNode) => {
  if (device.status === 'error') return 0.5
  if (device.status === 'warning') return 0.3
  if (device.metrics.temperature > 28) return 0.4
  if (device.metrics.power > 20) return 0.35
  return 0.1
}

const tableRowClassName = ({ row }: { row: DeviceNode }) => `row-${row.status}`

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
    focusedDevice.value = data as DeviceNode
    selectedDevice.value = data as DeviceNode
    nextTick(() => {
      initFocusChart()
    })
  } else if (data.type === 'system') {
    selectedSystem.value = data as SystemNode
    selectedDevice.value = null
    focusedDevice.value = null
    destroyFocusChart()
  } else {
    selectedSystem.value = null
    selectedDevice.value = null
    focusedDevice.value = null
    destroyFocusChart()
  }
}

const exitFocusMode = () => {
  focusedDevice.value = null
  selectedDevice.value = null
  destroyFocusChart()
}

const clearSelection = () => {
  selectedDevice.value = null
  selectedSystem.value = null
  focusedDevice.value = null
  destroyFocusChart()
}

const destroyFocusChart = () => {
  if (focusChartInstance) {
    focusChartInstance.dispose()
    focusChartInstance = null
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

const changeFloor = (floor: string) => {
  ElMessage.success(`Switched to ${floor}`)
}

const handleDeviceControl = (device: DeviceNode) => {
  ElMessage.success(`Opening control panel for ${device.name}`)
}

const handleQuickRepair = () => {
  if (!focusedDevice.value) return
  ElMessage.warning(`Creating repair order for ${focusedDevice.value.name}`)
}

const exportDeviceData = () => {
  if (!focusedDevice.value) return
  ElMessage.success('Exporting device data to CSV...')
}

// ==================== ECharts Focus Chart ====================
const initFocusChart = () => {
  destroyFocusChart()

  if (!focusChartRef.value || !focusedDevice.value) return

  nextTick(() => {
    if (!focusChartRef.value || !focusedDevice.value) return

    try {
      focusChartInstance = echarts.init(focusChartRef.value, 'dark')
      const trendData = generateTrendData(focusedDevice.value)

      const option: echarts.EChartsOption = {
        backgroundColor: 'transparent',
        tooltip: {
          trigger: 'axis',
          backgroundColor: 'rgba(13, 25, 48, 0.95)',
          borderColor: 'rgba(64, 158, 255, 0.3)',
          textStyle: { color: '#e5eaf3', fontSize: 12 }
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
          top: 8,
          right: 55,
          bottom: 35,
          left: 50
        },
        xAxis: {
          type: 'category',
          data: trendData.xAxis,
          axisLine: { lineStyle: { color: 'rgba(255,255,255,0.15)' } },
          axisTick: { show: false },
          axisLabel: { color: '#8899aa', fontSize: 10, interval: 3 },
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

      focusChartInstance.setOption(option)
    } catch (error) {
      console.error('Failed to initialize focus chart:', error)
    }
  })
}

const handleResize = () => {
  if (focusChartInstance) {
    try { focusChartInstance.resize() } catch (e) {}
  }
}

let updateTimer: number
const startRealtimeUpdates = () => {
  updateTimer = window.setInterval(() => {
    lastUpdateTime.value = new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' })

    const device = focusedDevice.value
    if (device) {
      const m = device.metrics
      m.temperature += (Math.random() - 0.5) * 0.3
      m.power += (Math.random() - 0.5) * 0.5
      m.temperature = Math.round(m.temperature * 10) / 10
      m.power = Math.round(m.power * 10) / 10

      if (focusChartInstance && !focusChartInstance.isDisposed()) {
        try {
          const now = new Date()
          const timeStr = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`
          const option = focusChartInstance.getOption()
          if (option && (option.xAxis as any[])?.[0]?.data) {
            const xData = [...(option.xAxis as any[])[0].data, timeStr]
            if (xData.length > 24) xData.shift()
            const series = option.series as any[]
            const tempData = [...series[0].data, +(m.temperature + (Math.random() - 0.5) * 0.5).toFixed(1)]
            if (tempData.length > 24) tempData.shift()
            const powerData = [...series[1].data, +(m.power + (Math.random() - 0.5) * 1).toFixed(1)]
            if (powerData.length > 24) powerData.shift()
            focusChartInstance.setOption({
              xAxis: [{ data: xData }],
              series: [{ data: tempData }, { data: powerData }]
            })
          }
        } catch (e) {}
      }
    }
  }, 3000)
}

watch(focusedDevice, (newVal) => {
  if (newVal) {
    nextTick(() => initFocusChart())
  }
})

// ==================== Lifecycle ====================
onMounted(async () => {
  await preloadAllImages()
  isAssetsLoaded.value = true
  await nextTick()

  startRealtimeUpdates()
  window.addEventListener('resize', handleResize)
  lastUpdateTime.value = new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
})

onUnmounted(() => {
  clearInterval(updateTimer)
  window.removeEventListener('resize', handleResize)
  destroyFocusChart()
  document.removeEventListener('mousemove', handleResizeLeft)
  document.removeEventListener('mouseup', stopResizeLeft)
})

watch(searchKeyword, async (val) => {
  if (treeRef.value) treeRef.value.filter(val)
})

watch(viewMode, () => {
  nextTick(() => handleResize())
})
</script>

<style scoped>
/* ==================== Loading Screen Styles ==================== */
.loading-container {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, #0a1629 0%, #0d1930 100%);
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
  background: rgba(13, 25, 48, 0.6);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(64, 158, 255, 0.3);
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

.spinner-ring:nth-child(1) {
  border-top-color: #409eff;
  animation-delay: 0s;
}

.spinner-ring:nth-child(2) {
  border-right-color: #e6a23c;
  animation-delay: 0.2s;
  width: 70%;
  height: 70%;
  top: 15%;
  left: 15%;
}

.spinner-ring:nth-child(3) {
  border-bottom-color: #67c23a;
  animation-delay: 0.4s;
  width: 40%;
  height: 40%;
  top: 30%;
  left: 30%;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  margin-bottom: 24px;
  font-size: 28px;
  font-weight: 700;
  color: #e5eaf3;
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
  color: #409eff;
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
  background: linear-gradient(90deg, #409eff, #67c23a, #e6a23c);
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
  font-size: 14px;
  color: #8899aa;
  letter-spacing: 1px;
  margin-bottom: 8px;
  font-weight: 500;
}

.loading-subtip {
  font-size: 12px;
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

/* ==================== Main Page Fade In ==================== */
.topology-page {
  display: flex;
  height: 100%;
  background: #0a1629;
  overflow: hidden;
  position: relative;
  animation: fadeIn 0.5s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
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
  z-index: 10;
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

.panel-header .el-icon { color: #409eff; font-size: 18px; }

.toggle-btn {
  margin-left: auto;
  width: 28px;
  height: 28px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #e5eaf3;
}

.search-box { padding: 12px; }
.search-box :deep(.el-input__wrapper) {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: none;
}
.search-box :deep(.el-input__inner) { color: #e5eaf3; }

/* ==================== Topology Tree ==================== */
.topology-tree {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 0 4px;
}
.topology-tree::-webkit-scrollbar { width: 4px; }
.topology-tree::-webkit-scrollbar-thumb { background: rgba(64, 158, 255, 0.3); border-radius: 2px; }

.topology-tree :deep(.el-tree) { background: transparent; color: #e5eaf3; }
.topology-tree :deep(.el-tree-node__content) {
  height: 40px; border-radius: 6px; margin: 2px 4px; transition: all 0.2s;
}
.topology-tree :deep(.el-tree-node__content:hover) { background: rgba(64, 158, 255, 0.1); }
.topology-tree :deep(.el-tree-node.is-current > .el-tree-node__content) {
  background: rgba(64, 158, 255, 0.2); border: 1px solid rgba(64, 158, 255, 0.3);
}

.tree-node-content { display: flex; align-items: center; gap: 8px; flex: 1; padding-right: 8px; }
.device-thumb { flex-shrink: 0; border: 1px solid rgba(255, 255, 255, 0.15); border-radius: 4px; }
.node-icon { font-size: 16px; flex-shrink: 0; }
.area-icon { color: #409eff; }
.system-icon { color: #67c23a; }
.node-label { flex: 1; font-size: 13px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.node-label.is-selected { color: #409eff; }

.status-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.status-dot.status-online { background: #67c23a; box-shadow: 0 0 6px rgba(103, 194, 58, 0.6); }
.status-dot.status-warning { background: #e6a23c; box-shadow: 0 0 6px rgba(230, 162, 60, 0.6); animation: pulse 2s infinite; }
.status-dot.status-error { background: #f56c6c; box-shadow: 0 0 6px rgba(245, 108, 108, 0.6); animation: pulse 1s infinite; }
.status-dot.status-offline { background: #909399; }

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.count-badge :deep(.el-badge__content) {
  background: rgba(64, 158, 255, 0.3); border: none; font-size: 10px; height: 16px; line-height: 16px;
}

/* ==================== Stats ==================== */
.stats-overview {
  display: grid; grid-template-columns: repeat(4, 1fr); gap: 4px;
  padding: 8px 12px; border-top: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(0, 0, 0, 0.2);
}
.stat-item { text-align: center; padding: 6px 4px; border-radius: 6px; background: rgba(255, 255, 255, 0.04); }
.stat-value { display: block; font-size: 16px; font-weight: 700; color: #409eff; }
.stat-value.online { color: #67c23a; }
.stat-label { font-size: 10px; color: #8899aa; text-transform: uppercase; letter-spacing: 0.5px; }

/* ==================== Resize Handle ==================== */
.resize-handle {
  width: 4px; background: rgba(64, 158, 255, 0.1); cursor: col-resize;
  transition: background 0.2s; flex-shrink: 0; z-index: 10;
}
.resize-handle:hover { background: rgba(64, 158, 255, 0.4); }

/* ==================== Canvas ==================== */
.topology-canvas {
  flex: 1; display: flex; flex-direction: column; overflow: hidden; position: relative;
}
.topology-canvas.focused-mode { overflow: hidden; }

.canvas-toolbar {
  display: flex; align-items: center; justify-content: space-between;
  padding: 8px 16px; background: rgba(13, 25, 48, 0.9);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}
.toolbar-left, .toolbar-right { display: flex; align-items: center; gap: 8px; }
.toolbar-left :deep(.el-radio-button__inner),
.toolbar-right :deep(.el-button),
.canvas-toolbar :deep(.el-button) {
  background: rgba(255, 255, 255, 0.06); border-color: rgba(255, 255, 255, 0.15); color: #e5eaf3;
}
.toolbar-left :deep(.el-radio-button__inner:hover),
.toolbar-right :deep(.el-button:hover),
.canvas-toolbar :deep(.el-button:hover) {
  background: rgba(64, 158, 255, 0.2); border-color: rgba(64, 158, 255, 0.4);
}

.canvas-container {
  flex: 1; position: relative; overflow: hidden;
  background: radial-gradient(ellipse at center, #0d1930 0%, #070e1a 100%);
}

/* ==================== Device Grid View ==================== */
.device-grid-view { height: 100%; overflow-y: auto; padding: 16px; }
.device-grid-view::-webkit-scrollbar { width: 4px; }
.device-grid-view::-webkit-scrollbar-thumb { background: rgba(64, 158, 255, 0.3); border-radius: 2px; }

.empty-canvas-hint {
  position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
  text-align: center; color: #8899aa; z-index: 5;
}
.empty-canvas-hint p { margin-top: 12px; font-size: 14px; }

.device-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 16px; }

/* ==================== 区域小标题样式 ==================== */
.area-grid-header,
.area-list-header {
  grid-column: 1 / -1;
  margin-top: 8px;
  margin-bottom: 8px;
}

.area-grid-header.first-header,
.area-list-header.first-header {
  margin-top: 0;
}

.area-header-content {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.area-header-icon {
  font-size: 16px;
  color: #409eff;
}

.area-header-name {
  font-size: 14px;
  font-weight: 600;
  color: #e5eaf3;
  letter-spacing: 0.5px;
}

.area-header-count {
  font-size: 11px;
  color: #8899aa;
  background: rgba(64, 158, 255, 0.15);
  padding: 2px 8px;
  border-radius: 12px;
  margin-left: 6px;
}

.area-header-divider {
  height: 1px;
  background: linear-gradient(90deg, rgba(64, 158, 255, 0.3), rgba(64, 158, 255, 0.05), transparent);
  width: 100%;
}

.device-card {
  background: rgba(13, 25, 48, 0.8); border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px; overflow: hidden; cursor: pointer; transition: all 0.3s ease;
}
.device-card:hover {
  transform: translateY(-4px); box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
  border-color: rgba(64, 158, 255, 0.3);
}
.device-card.is-selected {
  border-color: #409eff; box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.4);
  background: rgba(64, 158, 255, 0.08);
}
.device-card.status-warning { border-left: 3px solid #e6a23c; }
.device-card.status-error { border-left: 3px solid #f56c6c; }
.device-card.status-offline { opacity: 0.6; }

.device-image-wrapper { position: relative; width: 100%; height: 160px; background: rgba(0, 0, 0, 0.3); overflow: hidden; }
.device-image { width: 100%; height: 100%; }
.device-image :deep(.el-image__inner) { object-fit: contain; transition: transform 0.3s ease; }
.device-card:hover .device-image :deep(.el-image__inner) { transform: scale(1.05); }

.image-fallback {
  width: 100%; height: 100%; display: flex; flex-direction: column;
  align-items: center; justify-content: center; background: rgba(0, 0, 0, 0.5);
  color: #8899aa; gap: 8px; font-size: 12px;
}
.image-loading {
  width: 100%; height: 100%; display: flex; align-items: center;
  justify-content: center; background: rgba(0, 0, 0, 0.3); color: #8899aa;
}

.device-status-tag { position: absolute; top: 8px; right: 8px; }

.heatmap-overlay {
  position: absolute; top: 0; left: 0; right: 0; bottom: 0;
  background: linear-gradient(135deg, rgba(245, 108, 108, 0.5), rgba(230, 162, 60, 0.3));
  pointer-events: none; transition: opacity 0.3s ease;
}

.device-info { padding: 12px; }
.device-name { margin: 0 0 4px 0; font-size: 13px; color: #e5eaf3; font-weight: 600; }
.device-model { font-size: 11px; color: #8899aa; display: block; margin-bottom: 8px; }
.device-metrics-mini { display: flex; gap: 12px; }
.metric-mini { font-size: 11px; color: #8899aa; font-family: 'JetBrains Mono', monospace; }
.metric-mini.warning { color: #e6a23c; }

/* ==================== Device List View ==================== */
.device-list-view {
  height: 100%;
  overflow-y: auto;
  padding: 16px;
}

.device-list-view::-webkit-scrollbar { width: 4px; }
.device-list-view::-webkit-scrollbar-thumb { background: rgba(64, 158, 255, 0.3); border-radius: 2px; }

.device-list-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.area-sub-table {
  margin-bottom: 8px;
}

.device-list-view :deep(.el-table) {
  background: transparent; --el-table-bg-color: transparent; --el-table-tr-bg-color: transparent;
  --el-table-header-bg-color: rgba(13, 25, 48, 0.95); --el-table-border-color: rgba(255, 255, 255, 0.06);
  --el-table-text-color: #e5eaf3; --el-table-header-text-color: #8899aa;
}
.device-list-view :deep(.el-table th) { font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; }
.device-list-view :deep(.el-table tr) { cursor: pointer; transition: background 0.2s; }
.device-list-view :deep(.el-table tr:hover > td) { background: rgba(64, 158, 255, 0.08) !important; }
.device-list-view :deep(.el-table .row-warning) { border-left: 3px solid #e6a23c; }
.device-list-view :deep(.el-table .row-error) { border-left: 3px solid #f56c6c; background: rgba(245, 108, 108, 0.05) !important; }
.device-list-view :deep(.el-table .row-offline) { opacity: 0.5; }
.table-device-name { font-weight: 500; }
.text-warning { color: #e6a23c; }
.text-danger { color: #f56c6c; }

/* ==================== Legend ==================== */
.canvas-legend {
  position: absolute; bottom: 16px; right: 16px; display: flex; flex-direction: column;
  gap: 6px; background: rgba(13, 25, 48, 0.8); border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px; padding: 10px 14px; z-index: 10;
}
.legend-item { display: flex; align-items: center; gap: 8px; font-size: 11px; color: #8899aa; }
.dot { width: 10px; height: 10px; border-radius: 50%; }
.dot.online { background: #67c23a; box-shadow: 0 0 8px rgba(103, 194, 58, 0.5); }
.dot.warning { background: #e6a23c; box-shadow: 0 0 8px rgba(230, 162, 60, 0.5); }
.dot.error { background: #f56c6c; box-shadow: 0 0 8px rgba(245, 108, 108, 0.5); }
.dot.offline { background: #909399; }

/* ==================== FOCUS SCREEN MODE ==================== */
.device-focus-screen {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  z-index: 20;
  animation: focusIn 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes focusIn {
  from { opacity: 0; transform: scale(1.05); }
  to { opacity: 1; transform: scale(1); }
}

.focus-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  overflow: hidden;
}

.focus-bg-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: blur(20px) brightness(0.15);
  transform: scale(1.1);
}

.focus-bg-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(10, 22, 41, 0.85) 0%, rgba(10, 22, 41, 0.6) 50%, rgba(10, 22, 41, 0.85) 100%);
}

.focus-top-bar {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 20px;
  background: rgba(13, 25, 48, 0.7);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  z-index: 2;
}

.back-btn {
  background: rgba(255, 255, 255, 0.08) !important;
  border: 1px solid rgba(255, 255, 255, 0.15) !important;
  color: #e5eaf3 !important;
  font-weight: 500;
}

.back-btn:hover {
  background: rgba(64, 158, 255, 0.2) !important;
  border-color: rgba(64, 158, 255, 0.4) !important;
}

.focus-breadcrumb {
  flex: 1;
  margin: 0 24px;
}

.focus-breadcrumb :deep(.el-breadcrumb__inner) { color: #8899aa; }
.focus-breadcrumb :deep(.el-breadcrumb__separator) { color: rgba(255,255,255,0.2); }

.focus-actions :deep(.el-button) {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.2);
  color: #e5eaf3;
}
.focus-actions :deep(.el-button:hover) {
  background: rgba(64, 158, 255, 0.2);
  border-color: rgba(64, 158, 255, 0.4);
}

.focus-main-content {
  position: relative;
  flex: 1;
  display: flex;
  gap: 24px;
  padding: 24px;
  z-index: 2;
  overflow: hidden;
}

.focus-image-section {
  flex: 0 0 45%;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.focus-image-container {
  flex: 1;
  background: rgba(0, 0, 0, 0.4);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  overflow: hidden;
  position: relative;
  min-height: 300px;
}

.focus-main-image {
  width: 100%;
  height: 100%;
}

.focus-main-image :deep(.el-image__inner) {
  object-fit: contain;
  cursor: pointer;
}

.focus-fallback {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  color: #8899aa;
}

.focus-image-info {
  padding: 0 8px;
}

.focus-device-status {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.status-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

.status-indicator.status-online { background: #67c23a; box-shadow: 0 0 12px rgba(103, 194, 58, 0.6); }
.status-indicator.status-warning { background: #e6a23c; box-shadow: 0 0 12px rgba(230, 162, 60, 0.6); }
.status-indicator.status-error { background: #f56c6c; box-shadow: 0 0 12px rgba(245, 108, 108, 0.6); }
.status-indicator.status-offline { background: #909399; }

.focus-device-name {
  font-size: 28px;
  font-weight: 700;
  color: #ffffff;
  margin: 0 0 6px 0;
  letter-spacing: -0.5px;
}

.focus-device-model {
  font-size: 14px;
  color: #8899aa;
  margin: 0 0 4px 0;
}

.focus-device-serial {
  font-size: 12px;
  color: #409eff;
  font-family: 'JetBrains Mono', monospace;
  margin: 0;
}

.focus-metrics-section {
  flex: 1;
  display: flex;
  align-items: stretch;
}

.focus-metrics-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: 1fr 1fr 1fr;
  gap: 12px;
  width: 100%;
}

.focus-metric-card {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 16px;
  background: rgba(13, 25, 48, 0.6);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  transition: all 0.3s;
}

.focus-metric-card:hover {
  background: rgba(64, 158, 255, 0.1);
  border-color: rgba(64, 158, 255, 0.3);
}

.focus-metric-card.metric-warning {
  border-color: rgba(245, 108, 108, 0.3);
  background: rgba(245, 108, 108, 0.08);
}

.focus-metric-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(64, 158, 255, 0.15);
  border-radius: 10px;
  color: #409eff;
}

.metric-warning .focus-metric-icon {
  background: rgba(245, 108, 108, 0.15);
  color: #f56c6c;
}

.focus-metric-data {
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.focus-metric-value {
  font-size: 26px;
  font-weight: 700;
  color: #ffffff;
}

.focus-metric-unit {
  font-size: 12px;
  color: #8899aa;
  font-weight: 400;
}

.focus-metric-label {
  font-size: 11px;
  color: #8899aa;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.focus-metric-bar {
  height: 4px;
  background: rgba(255, 255, 255, 0.06);
  border-radius: 2px;
  overflow: hidden;
}

.focus-metric-fill {
  height: 100%;
  background: linear-gradient(90deg, #409eff, #67c23a);
  border-radius: 2px;
  transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.focus-metric-fill.fill-warning {
  background: linear-gradient(90deg, #e6a23c, #f56c6c);
}

.focus-bottom-panel {
  position: relative;
  display: flex;
  gap: 24px;
  padding: 0 24px 24px;
  z-index: 2;
}

.focus-chart-section {
  flex: 1;
  background: rgba(13, 25, 48, 0.6);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 16px;
}

.focus-maintenance-section {
  width: 280px;
  flex-shrink: 0;
  background: rgba(13, 25, 48, 0.6);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 16px;
}

.focus-section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #e5eaf3;
  font-size: 14px;
  margin: 0 0 14px 0;
  font-weight: 600;
}

.focus-section-title .el-icon { color: #409eff; }

.chart-update-time {
  margin-left: auto;
  font-size: 10px;
  color: #8899aa;
  font-weight: 400;
}

.focus-chart-container {
  width: 100%;
  height: 220px;
}

.maintenance-timeline {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding-left: 8px;
}

.timeline-item {
  display: flex;
  gap: 12px;
  position: relative;
}

.timeline-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin-top: 4px;
  flex-shrink: 0;
}

.timeline-dot.installed { background: #409eff; box-shadow: 0 0 8px rgba(64, 158, 255, 0.5); }
.timeline-dot.maintenance { background: #67c23a; box-shadow: 0 0 8px rgba(103, 194, 58, 0.5); }
.timeline-dot.scheduled { background: #e6a23c; box-shadow: 0 0 8px rgba(230, 162, 60, 0.5); }
.timeline-dot.overdue { background: #f56c6c; box-shadow: 0 0 8px rgba(245, 108, 108, 0.5); animation: pulse 1s infinite; }

.timeline-content {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.timeline-date {
  font-size: 12px;
  color: #e5eaf3;
  font-family: 'JetBrains Mono', monospace;
  display: flex;
  align-items: center;
  gap: 6px;
}

.timeline-label {
  font-size: 10px;
  color: #8899aa;
  text-transform: uppercase;
}

.timeline-item.overdue .timeline-date {
  color: #f56c6c;
}

/* ==================== Responsive ==================== */
@media (max-width: 1200px) {
  .device-grid { grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 12px; }
  .device-image-wrapper { height: 130px; }
  .focus-main-content { flex-direction: column; }
  .focus-image-section { flex: 0 0 auto; }
  .focus-image-container { min-height: 250px; max-height: 350px; }
  .focus-metrics-grid { grid-template-columns: 1fr 1fr 1fr; grid-template-rows: 1fr 1fr; }
  .focus-bottom-panel { flex-direction: column; }
  .focus-maintenance-section { width: 100%; }
  .focus-chart-container { height: 200px; }
}

@media (max-width: 768px) {
  .topology-left-panel { position: absolute; left: 0; top: 0; bottom: 0; z-index: 100; width: 280px !important; }
  .device-grid { grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 10px; }
  .device-image-wrapper { height: 120px; }
  .canvas-toolbar { flex-direction: column; gap: 8px; padding: 8px; }
  .toolbar-left, .toolbar-right { width: 100%; justify-content: center; }
  .focus-top-bar { flex-direction: column; gap: 10px; padding: 10px 14px; }
  .focus-breadcrumb { margin: 0; }
  .focus-main-content { padding: 14px; gap: 14px; }
  .focus-image-container { min-height: 200px; max-height: 280px; }
  .focus-device-name { font-size: 22px; }
  .focus-metrics-grid { grid-template-columns: 1fr 1fr; grid-template-rows: auto; }
  .focus-metric-value { font-size: 20px; }
  .focus-bottom-panel { padding: 0 14px 14px; gap: 14px; }
  .focus-chart-container { height: 180px; }
}
</style>

<style scoped>
/* ==================== Loading Screen Styles (保持不变) ==================== */
.loading-container {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, #0a1629 0%, #0d1930 100%);
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
  background: rgba(13, 25, 48, 0.6);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(64, 158, 255, 0.3);
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

.spinner-ring:nth-child(1) {
  border-top-color: #409eff;
  animation-delay: 0s;
}

.spinner-ring:nth-child(2) {
  border-right-color: #e6a23c;
  animation-delay: 0.2s;
  width: 70%;
  height: 70%;
  top: 15%;
  left: 15%;
}

.spinner-ring:nth-child(3) {
  border-bottom-color: #67c23a;
  animation-delay: 0.4s;
  width: 40%;
  height: 40%;
  top: 30%;
  left: 30%;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  margin-bottom: 24px;
  font-size: 28px;
  font-weight: 700;
  color: #e5eaf3;
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
  color: #409eff;
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
  background: linear-gradient(90deg, #409eff, #67c23a, #e6a23c);
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
  font-size: 14px;
  color: #94a3b8;
  letter-spacing: 1px;
  margin-bottom: 8px;
  font-weight: 500;
}

.loading-subtip {
  font-size: 12px;
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

/* ==================== 主内容区 - 柔和浅色系 ==================== */
.topology-page {
  display: flex;
  height: 100%;
  background: #f5f7fa;
  overflow: hidden;
  position: relative;
  animation: fadeIn 0.5s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* 左侧面板 - 柔和白色 */
.topology-left-panel {
  display: flex;
  flex-direction: column;
  background: #ffffff;
  border-right: 1px solid #e8edf2;
  transition: width 0.3s ease;
  overflow: hidden;
  flex-shrink: 0;
  z-index: 10;
}

.panel-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  color: #1f2d3d;
  font-weight: 600;
  font-size: 14px;
  border-bottom: 1px solid #e8edf2;
}

.panel-header .el-icon { color: #409eff; font-size: 18px; }

.toggle-btn {
  margin-left: auto;
  width: 28px;
  height: 28px;
  background: #f5f7fa;
  border: 1px solid #e4e7ed;
  color: #606266;
}

.search-box { padding: 12px; }
.search-box :deep(.el-input__wrapper) {
  background: #f5f7fa;
  border: 1px solid #e4e7ed;
  box-shadow: none;
}
.search-box :deep(.el-input__inner) { color: #1f2d3d; }

/* 树形组件 */
.topology-tree {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 0 4px;
}
.topology-tree::-webkit-scrollbar { width: 4px; }
.topology-tree::-webkit-scrollbar-thumb { background: #d9e1e8; border-radius: 2px; }

.topology-tree :deep(.el-tree) { background: transparent; color: #1f2d3d; }
.topology-tree :deep(.el-tree-node__content) {
  height: 40px; border-radius: 6px; margin: 2px 4px; transition: all 0.2s;
}
.topology-tree :deep(.el-tree-node__content:hover) { background: #f0f4f9; }
.topology-tree :deep(.el-tree-node.is-current > .el-tree-node__content) {
  background: #ecf5ff;
  border: 1px solid #d9ecff;
}

.tree-node-content { display: flex; align-items: center; gap: 8px; flex: 1; padding-right: 8px; }
.device-thumb { flex-shrink: 0; border: 1px solid #e8edf2; border-radius: 4px; }
.node-icon { font-size: 16px; flex-shrink: 0; }
.area-icon { color: #409eff; }
.system-icon { color: #67c23a; }
.node-label { flex: 1; font-size: 13px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: #1f2d3d; }
.node-label.is-selected { color: #409eff; }

.status-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.status-dot.status-online { background: #67c23a; box-shadow: 0 0 6px rgba(103, 194, 58, 0.4); }
.status-dot.status-warning { background: #e6a23c; box-shadow: 0 0 6px rgba(230, 162, 60, 0.4); animation: pulse 2s infinite; }
.status-dot.status-error { background: #f56c6c; box-shadow: 0 0 6px rgba(245, 108, 108, 0.4); animation: pulse 1s infinite; }
.status-dot.status-offline { background: #c0c4cc; }

.count-badge :deep(.el-badge__content) {
  background: #ecf5ff; border: none; font-size: 10px; height: 16px; line-height: 16px; color: #409eff;
}

/* 统计区域 */
.stats-overview {
  display: grid; grid-template-columns: repeat(4, 1fr); gap: 4px;
  padding: 8px 12px; border-top: 1px solid #e8edf2;
  background: #fafcfd;
}
.stat-item { text-align: center; padding: 6px 4px; border-radius: 6px; background: #ffffff; box-shadow: 0 1px 2px rgba(0,0,0,0.02); }
.stat-value { display: block; font-size: 16px; font-weight: 700; color: #409eff; }
.stat-value.online { color: #67c23a; }
.stat-label { font-size: 10px; color: #8a9aa8; text-transform: uppercase; letter-spacing: 0.5px; }

/* 拖拽手柄 */
.resize-handle {
  width: 4px; background: #e8edf2; cursor: col-resize;
  transition: background 0.2s; flex-shrink: 0; z-index: 10;
}
.resize-handle:hover { background: #409eff; }

/* 画布区域 */
.topology-canvas {
  flex: 1; display: flex; flex-direction: column; overflow: hidden; position: relative;
}
.topology-canvas.focused-mode { overflow: hidden; }

.canvas-toolbar {
  display: flex; align-items: center; justify-content: space-between;
  padding: 8px 16px; background: #ffffff;
  border-bottom: 1px solid #e8edf2;
}
.toolbar-left, .toolbar-right { display: flex; align-items: center; gap: 8px; }
.toolbar-left :deep(.el-radio-button__inner),
.toolbar-right :deep(.el-button),
.canvas-toolbar :deep(.el-button) {
  background: #ffffff; border-color: #dcdfe6; color: #606266;
}
.toolbar-left :deep(.el-radio-button__inner:hover),
.toolbar-right :deep(.el-button:hover),
.canvas-toolbar :deep(.el-button:hover) {
  background: #ecf5ff; border-color: #c6e2ff; color: #409eff;
}

.canvas-container {
  flex: 1; position: relative; overflow: hidden;
  background: #f8fafc;
}

/* 设备网格视图 */
.device-grid-view { height: 100%; overflow-y: auto; padding: 16px; }
.device-grid-view::-webkit-scrollbar { width: 4px; }
.device-grid-view::-webkit-scrollbar-thumb { background: #d9e1e8; border-radius: 2px; }

.empty-canvas-hint {
  position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
  text-align: center; color: #8a9aa8; z-index: 5;
}
.empty-canvas-hint p { margin-top: 12px; font-size: 14px; }

.device-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 16px; }

/* 区域小标题 */
.area-grid-header,
.area-list-header {
  grid-column: 1 / -1;
  margin-top: 8px;
  margin-bottom: 8px;
}

.area-grid-header.first-header,
.area-list-header.first-header {
  margin-top: 0;
}

.area-header-content {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.area-header-icon {
  font-size: 16px;
  color: #409eff;
}

.area-header-name {
  font-size: 14px;
  font-weight: 600;
  color: #1f2d3d;
  letter-spacing: 0.5px;
}

.area-header-count {
  font-size: 11px;
  color: #8a9aa8;
  background: #f0f4f9;
  padding: 2px 8px;
  border-radius: 12px;
  margin-left: 6px;
}

.area-header-divider {
  height: 1px;
  background: linear-gradient(90deg, #c0d4e8, #e8edf2, transparent);
  width: 100%;
}

/* 设备卡片 */
.device-card {
  background: #ffffff; border: 1px solid #e8edf2;
  border-radius: 12px; overflow: hidden; cursor: pointer; transition: all 0.3s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
}
.device-card:hover {
  transform: translateY(-4px); box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  border-color: #c0d4e8;
}
.device-card.is-selected {
  border-color: #409eff; box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.15);
  background: #f0f9ff;
}
.device-card.status-warning { border-left: 3px solid #e6a23c; }
.device-card.status-error { border-left: 3px solid #f56c6c; }
.device-card.status-offline { opacity: 0.6; }

.device-image-wrapper { position: relative; width: 100%; height: 160px; background: #f0f4f9; overflow: hidden; }
.device-image { width: 100%; height: 100%; }
.device-image :deep(.el-image__inner) { object-fit: contain; transition: transform 0.3s ease; }
.device-card:hover .device-image :deep(.el-image__inner) { transform: scale(1.05); }

.image-fallback {
  width: 100%; height: 100%; display: flex; flex-direction: column;
  align-items: center; justify-content: center; background: #f0f4f9;
  color: #8a9aa8; gap: 8px; font-size: 12px;
}
.image-loading {
  width: 100%; height: 100%; display: flex; align-items: center;
  justify-content: center; background: #f0f4f9; color: #8a9aa8;
}

.device-status-tag { position: absolute; top: 8px; right: 8px; }

.heatmap-overlay {
  position: absolute; top: 0; left: 0; right: 0; bottom: 0;
  background: linear-gradient(135deg, rgba(245, 108, 108, 0.25), rgba(230, 162, 60, 0.15));
  pointer-events: none; transition: opacity 0.3s ease;
}

.device-info { padding: 12px; }
.device-name { margin: 0 0 4px 0; font-size: 13px; color: #1f2d3d; font-weight: 600; }
.device-model { font-size: 11px; color: #8a9aa8; display: block; margin-bottom: 8px; }
.device-metrics-mini { display: flex; gap: 12px; }
.metric-mini { font-size: 11px; color: #8a9aa8; font-family: 'JetBrains Mono', monospace; }
.metric-mini.warning { color: #e6a23c; }

/* 设备列表视图 */
.device-list-view {
  height: 100%;
  overflow-y: auto;
  padding: 16px;
}

.device-list-view::-webkit-scrollbar { width: 4px; }
.device-list-view::-webkit-scrollbar-thumb { background: #d9e1e8; border-radius: 2px; }

.device-list-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.area-sub-table {
  margin-bottom: 8px;
}

.device-list-view :deep(.el-table) {
  background: transparent; --el-table-bg-color: transparent; --el-table-tr-bg-color: transparent;
  --el-table-header-bg-color: #f8fafc; --el-table-border-color: #e8edf2;
  --el-table-text-color: #1f2d3d; --el-table-header-text-color: #5a6e7c;
}
.device-list-view :deep(.el-table th) { font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; background: #f8fafc; }
.device-list-view :deep(.el-table tr) { cursor: pointer; transition: background 0.2s; }
.device-list-view :deep(.el-table tr:hover > td) { background: #f0f9ff !important; }
.device-list-view :deep(.el-table .row-warning) { border-left: 3px solid #e6a23c; }
.device-list-view :deep(.el-table .row-error) { border-left: 3px solid #f56c6c; background: #fef6f6 !important; }
.device-list-view :deep(.el-table .row-offline) { opacity: 0.5; }
.table-device-name { font-weight: 500; }
.text-warning { color: #e6a23c; }
.text-danger { color: #f56c6c; }

/* 图例 */
.canvas-legend {
  position: absolute; bottom: 16px; right: 16px; display: flex; flex-direction: column;
  gap: 6px; background: #ffffff; border: 1px solid #e8edf2;
  border-radius: 8px; padding: 10px 14px; z-index: 10;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}
.legend-item { display: flex; align-items: center; gap: 8px; font-size: 11px; color: #5a6e7c; }
.dot { width: 10px; height: 10px; border-radius: 50%; }
.dot.online { background: #67c23a; }
.dot.warning { background: #e6a23c; }
.dot.error { background: #f56c6c; }
.dot.offline { background: #c0c4cc; }

/* ==================== 聚焦模式 - 柔和浅色 ==================== */
.device-focus-screen {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  z-index: 20;
  animation: focusIn 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes focusIn {
  from { opacity: 0; transform: scale(1.02); }
  to { opacity: 1; transform: scale(1); }
}

.focus-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  overflow: hidden;
}

.focus-bg-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: blur(20px) brightness(1.05);
  transform: scale(1.1);
}

.focus-bg-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(248, 250, 252, 0.92);
}

.focus-top-bar {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 20px;
  background: rgba(255, 255, 255, 0.96);
  border-bottom: 1px solid #e8edf2;
  z-index: 2;
  backdrop-filter: blur(4px);
}

.back-btn {
  background: #f5f7fa !important;
  border: 1px solid #e4e7ed !important;
  color: #5a6e7c !important;
  font-weight: 500;
}

.back-btn:hover {
  background: #ecf5ff !important;
  border-color: #c6e2ff !important;
  color: #409eff !important;
}

.focus-breadcrumb {
  flex: 1;
  margin: 0 24px;
}

.focus-breadcrumb :deep(.el-breadcrumb__inner) { color: #5a6e7c; }
.focus-breadcrumb :deep(.el-breadcrumb__separator) { color: #c0c4cc; }

.focus-actions :deep(.el-button) {
  background: #ffffff;
  border-color: #e4e7ed;
  color: #5a6e7c;
}
.focus-actions :deep(.el-button:hover) {
  background: #ecf5ff;
  border-color: #c6e2ff;
  color: #409eff;
}

.focus-main-content {
  position: relative;
  flex: 1;
  display: flex;
  gap: 24px;
  padding: 24px;
  z-index: 2;
  overflow: hidden;
}

.focus-image-section {
  flex: 0 0 45%;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.focus-image-container {
  flex: 1;
  background: #f0f4f9;
  border-radius: 16px;
  border: 1px solid #e8edf2;
  overflow: hidden;
  position: relative;
  min-height: 300px;
}

.focus-main-image {
  width: 100%;
  height: 100%;
}

.focus-main-image :deep(.el-image__inner) {
  object-fit: contain;
  cursor: pointer;
}

.focus-fallback {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  color: #8a9aa8;
}

.focus-image-info {
  padding: 0 8px;
}

.focus-device-status {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.status-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

.status-indicator.status-online { background: #67c23a; }
.status-indicator.status-warning { background: #e6a23c; }
.status-indicator.status-error { background: #f56c6c; }
.status-indicator.status-offline { background: #c0c4cc; }

.focus-device-name {
  font-size: 28px;
  font-weight: 700;
  color: #1f2d3d;
  margin: 0 0 6px 0;
  letter-spacing: -0.5px;
}

.focus-device-model {
  font-size: 14px;
  color: #5a6e7c;
  margin: 0 0 4px 0;
}

.focus-device-serial {
  font-size: 12px;
  color: #409eff;
  font-family: 'JetBrains Mono', monospace;
  margin: 0;
}

.focus-metrics-section {
  flex: 1;
  display: flex;
  align-items: stretch;
}

.focus-metrics-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: 1fr 1fr 1fr;
  gap: 12px;
  width: 100%;
}

.focus-metric-card {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid #e8edf2;
  border-radius: 12px;
  transition: all 0.3s;
  backdrop-filter: blur(4px);
}

.focus-metric-card:hover {
  background: #ffffff;
  border-color: #c0d4e8;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
}

.focus-metric-card.metric-warning {
  border-color: #f5c6c6;
  background: rgba(254, 246, 246, 0.9);
}

.focus-metric-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f0f4f9;
  border-radius: 10px;
  color: #409eff;
}

.metric-warning .focus-metric-icon {
  background: #fef0f0;
  color: #f56c6c;
}

.focus-metric-data {
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.focus-metric-value {
  font-size: 26px;
  font-weight: 700;
  color: #1f2d3d;
}

.focus-metric-unit {
  font-size: 12px;
  color: #8a9aa8;
  font-weight: 400;
}

.focus-metric-label {
  font-size: 11px;
  color: #8a9aa8;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.focus-metric-bar {
  height: 4px;
  background: #e8edf2;
  border-radius: 2px;
  overflow: hidden;
}

.focus-metric-fill {
  height: 100%;
  background: linear-gradient(90deg, #409eff, #67c23a);
  border-radius: 2px;
  transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.focus-metric-fill.fill-warning {
  background: linear-gradient(90deg, #e6a23c, #f56c6c);
}

.focus-bottom-panel {
  position: relative;
  display: flex;
  gap: 24px;
  padding: 0 24px 24px;
  z-index: 2;
}

.focus-chart-section {
  flex: 1;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid #e8edf2;
  border-radius: 12px;
  padding: 16px;
  backdrop-filter: blur(4px);
}

.focus-maintenance-section {
  width: 280px;
  flex-shrink: 0;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid #e8edf2;
  border-radius: 12px;
  padding: 16px;
  backdrop-filter: blur(4px);
}

.focus-section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #1f2d3d;
  font-size: 14px;
  margin: 0 0 14px 0;
  font-weight: 600;
}

.focus-section-title .el-icon { color: #409eff; }

.chart-update-time {
  margin-left: auto;
  font-size: 10px;
  color: #8a9aa8;
  font-weight: 400;
}

.focus-chart-container {
  width: 100%;
  height: 220px;
}

.maintenance-timeline {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding-left: 8px;
}

.timeline-item {
  display: flex;
  gap: 12px;
  position: relative;
}

.timeline-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin-top: 4px;
  flex-shrink: 0;
}

.timeline-dot.installed { background: #409eff; }
.timeline-dot.maintenance { background: #67c23a; }
.timeline-dot.scheduled { background: #e6a23c; }
.timeline-dot.overdue { background: #f56c6c; animation: pulse 1s infinite; }

.timeline-content {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.timeline-date {
  font-size: 12px;
  color: #1f2d3d;
  font-family: 'JetBrains Mono', monospace;
  display: flex;
  align-items: center;
  gap: 6px;
}

.timeline-label {
  font-size: 10px;
  color: #8a9aa8;
  text-transform: uppercase;
}

.timeline-item.overdue .timeline-date {
  color: #f56c6c;
}

/* ==================== 响应式 ==================== */
@media (max-width: 1200px) {
  .device-grid { grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 12px; }
  .device-image-wrapper { height: 130px; }
  .focus-main-content { flex-direction: column; }
  .focus-image-section { flex: 0 0 auto; }
  .focus-image-container { min-height: 250px; max-height: 350px; }
  .focus-metrics-grid { grid-template-columns: 1fr 1fr 1fr; grid-template-rows: 1fr 1fr; }
  .focus-bottom-panel { flex-direction: column; }
  .focus-maintenance-section { width: 100%; }
  .focus-chart-container { height: 200px; }
}

@media (max-width: 768px) {
  .topology-left-panel { position: absolute; left: 0; top: 0; bottom: 0; z-index: 100; width: 280px !important; }
  .device-grid { grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 10px; }
  .device-image-wrapper { height: 120px; }
  .canvas-toolbar { flex-direction: column; gap: 8px; padding: 8px; }
  .toolbar-left, .toolbar-right { width: 100%; justify-content: center; }
  .focus-top-bar { flex-direction: column; gap: 10px; padding: 10px 14px; }
  .focus-breadcrumb { margin: 0; }
  .focus-main-content { padding: 14px; gap: 14px; }
  .focus-image-container { min-height: 200px; max-height: 280px; }
  .focus-device-name { font-size: 22px; }
  .focus-metrics-grid { grid-template-columns: 1fr 1fr; grid-template-rows: auto; }
  .focus-metric-value { font-size: 20px; }
  .focus-bottom-panel { padding: 0 14px 14px; gap: 14px; }
  .focus-chart-container { height: 180px; }
}
</style>
