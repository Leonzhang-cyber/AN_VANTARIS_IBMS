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
        <div class="loading-tip">DALI / KNX Lighting Management</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="dali-knx-container">
    <!-- Page Header -->
    <div class="page-header">
      <h2>DALI / KNX Lighting</h2>
      <div class="header-actions">
        <el-button type="primary" @click="handleAddDevice">
          <el-icon><Plus /></el-icon>
          Add Device
        </el-button>
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>
          Export
        </el-button>
        <el-button @click="refreshData">
          <el-icon><Refresh /></el-icon>
          Refresh
        </el-button>
      </div>
    </div>

    <!-- Statistics Cards -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-info">
              <div class="stat-title">Total Devices</div>
              <div class="stat-value">{{ stats.total }}</div>
            </div>
            <div class="stat-icon total">
              <el-icon><Grid /></el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-info">
              <div class="stat-title">Online</div>
              <div class="stat-value online">{{ stats.online }}</div>
            </div>
            <div class="stat-icon online-bg">
              <el-icon><Link /></el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-info">
              <div class="stat-title">Active Scenes</div>
              <div class="stat-value scenes">{{ stats.activeScenes }}</div>
            </div>
            <div class="stat-icon scenes-bg">
              <el-icon><MagicStick /></el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-info">
              <div class="stat-title">Energy Saved (kW)</div>
              <div class="stat-value saved">{{ stats.energySaved }}</div>
            </div>
            <div class="stat-icon saved-bg">
              <el-icon><Lightning /></el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Protocol Tabs -->
    <el-card shadow="hover" class="protocol-card">
      <el-tabs v-model="activeProtocol" @tab-click="handleProtocolChange">
        <el-tab-pane label="DALI Devices" name="dali">
          <template #label>
            <span class="protocol-tab">
              <el-icon><Cpu /></el-icon>
              DALI Devices
            </span>
          </template>
        </el-tab-pane>
        <el-tab-pane label="KNX Devices" name="knx">
          <template #label>
            <span class="protocol-tab">
              <el-icon><Connection /></el-icon>
              KNX Devices
            </span>
          </template>
        </el-tab-pane>
        <el-tab-pane label="Lighting Scenes" name="scenes">
          <template #label>
            <span class="protocol-tab">
              <el-icon><Picture /></el-icon>
              Lighting Scenes
            </span>
          </template>
        </el-tab-pane>
        <el-tab-pane label="Schedules" name="schedules">
          <template #label>
            <span class="protocol-tab">
              <el-icon><Clock /></el-icon>
              Schedules
            </span>
          </template>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- DALI Devices Content -->
    <div v-show="activeProtocol === 'dali'">
      <!-- DALI Filters -->
      <el-card shadow="hover" class="filter-card">
        <el-form :inline="true" :model="daliFilters" class="filter-form">
          <el-form-item label="Device Name">
            <el-input v-model="daliFilters.deviceName" placeholder="Search by name" clearable />
          </el-form-item>
          <el-form-item label="Ballast Type">
            <el-select v-model="daliFilters.ballastType" placeholder="All Types" clearable>
              <el-option label="ECG" value="ECG" />
              <el-option label="CCG" value="CCG" />
              <el-option label="LED Driver" value="LED Driver" />
            </el-select>
          </el-form-item>
          <el-form-item label="Status">
            <el-select v-model="daliFilters.status" placeholder="All Status" clearable>
              <el-option label="Online" value="online" />
              <el-option label="Offline" value="offline" />
              <el-option label="Fault" value="fault" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleDaliSearch">
              <el-icon><Search /></el-icon>
              Search
            </el-button>
            <el-button @click="resetDaliFilters">Reset</el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <!-- DALI Devices Chart -->
      <el-row :gutter="20" class="charts-row">
        <el-col :xs="24" :md="12">
          <el-card shadow="hover" class="chart-card">
            <template #header>
              <div class="card-header">
                <span>DALI Bus Load</span>
              </div>
            </template>
            <div ref="daliChartRef" class="chart-container"></div>
          </el-card>
        </el-col>
        <el-col :xs="24" :md="12">
          <el-card shadow="hover" class="chart-card">
            <template #header>
              <div class="card-header">
                <span>Dimming Level Distribution</span>
              </div>
            </template>
            <div ref="dimmingChartRef" class="chart-container"></div>
          </el-card>
        </el-col>
      </el-row>

      <!-- DALI Devices Table -->
      <el-card shadow="hover" class="table-card">
        <template #header>
          <div class="card-header">
            <span>DALI Devices List</span>
            <el-button text @click="discoverDevices">
              <el-icon><Search /></el-icon>
              Discover Devices
            </el-button>
          </div>
        </template>

        <el-table :data="paginatedDaliDevices" stripe border style="width: 100%" v-loading="tableLoading">
          <el-table-column prop="shortAddress" label="Short Address" min-width="120" />
          <el-table-column prop="name" label="Device Name" min-width="150" />
          <el-table-column prop="location" label="Location" min-width="120" />
          <el-table-column prop="ballastType" label="Ballast Type" min-width="120">
            <template #default="{ row }">
              <el-tag :type="getBallastTypeTag(row.ballastType)">{{ row.ballastType }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="Status" min-width="100">
            <template #default="{ row }">
              <el-tag :type="getStatusTag(row.status)">
                {{ getStatusText(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="dimmingLevel" label="Dimming Level" min-width="140" sortable>
            <template #default="{ row }">
              <span>{{ row.dimmingLevel }}%</span>
              <el-slider v-model="row.dimmingLevel" :min="0" :max="100" :disabled="row.status !== 'online'" @change="(val) => updateDimming(row, val)" size="small" />
            </template>
          </el-table-column>
          <el-table-column prop="lampType" label="Lamp Type" min-width="120" />
          <el-table-column prop="power" label="Power (W)" min-width="100" sortable>
            <template #default="{ row }">{{ row.power.toFixed(1) }} W</template>
          </el-table-column>
          <el-table-column prop="lastUpdated" label="Last Updated" min-width="160" />
          <el-table-column label="Actions" fixed="right" min-width="180">
            <template #default="{ row }">
              <el-button type="primary" link @click="viewDeviceDetails(row)">
                <el-icon><View /></el-icon>
                View
              </el-button>
              <el-button type="success" link @click="controlDevice(row)">
                <el-icon><Operation /></el-icon>
                Control
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <div class="pagination-container">
          <el-pagination
              v-model:current-page="daliPagination.currentPage"
              v-model:page-size="daliPagination.pageSize"
              :page-sizes="[10, 20, 50]"
              :total="filteredDaliDevices.length"
              layout="total, sizes, prev, pager, next, jumper"
              @size-change="handleDaliSizeChange"
              @current-change="handleDaliCurrentChange"
          />
        </div>
      </el-card>
    </div>

    <!-- KNX Devices Content -->
    <div v-show="activeProtocol === 'knx'">
      <!-- KNX Filters -->
      <el-card shadow="hover" class="filter-card">
        <el-form :inline="true" :model="knxFilters" class="filter-form">
          <el-form-item label="Device Name">
            <el-input v-model="knxFilters.deviceName" placeholder="Search by name" clearable />
          </el-form-item>
          <el-form-item label="Group Address">
            <el-input v-model="knxFilters.groupAddress" placeholder="Search by group address" clearable />
          </el-form-item>
          <el-form-item label="Status">
            <el-select v-model="knxFilters.status" placeholder="All Status" clearable>
              <el-option label="Online" value="online" />
              <el-option label="Offline" value="offline" />
              <el-option label="Fault" value="fault" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleKnxSearch">
              <el-icon><Search /></el-icon>
              Search
            </el-button>
            <el-button @click="resetKnxFilters">Reset</el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <!-- KNX Devices Table -->
      <el-card shadow="hover" class="table-card">
        <template #header>
          <div class="card-header">
            <span>KNX Devices List</span>
            <el-button text @click="syncKnxDevices">
              <el-icon><Refresh /></el-icon>
              Sync Devices
            </el-button>
          </div>
        </template>

        <el-table :data="paginatedKnxDevices" stripe border style="width: 100%" v-loading="tableLoading">
          <el-table-column prop="individualAddress" label="Individual Address" min-width="130" />
          <el-table-column prop="name" label="Device Name" min-width="150" />
          <el-table-column prop="location" label="Location" min-width="120" />
          <el-table-column prop="deviceType" label="Device Type" min-width="130">
            <template #default="{ row }">
              <el-tag :type="getDeviceTypeTag(row.deviceType)">{{ row.deviceType }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="Status" min-width="100">
            <template #default="{ row }">
              <el-tag :type="getStatusTag(row.status)">
                {{ getStatusText(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="brightness" label="Brightness (%)" min-width="140" sortable>
            <template #default="{ row }">
              <span>{{ row.brightness }}%</span>
              <el-slider v-model="row.brightness" :min="0" :max="100" :disabled="row.status !== 'online'" @change="(val) => updateBrightness(row, val)" size="small" />
            </template>
          </el-table-column>
          <el-table-column prop="groupAddress" label="Group Address" min-width="130" />
          <el-table-column prop="lastUpdated" label="Last Updated" min-width="160" />
          <el-table-column label="Actions" fixed="right" min-width="180">
            <template #default="{ row }">
              <el-button type="primary" link @click="viewDeviceDetails(row)">
                <el-icon><View /></el-icon>
                View
              </el-button>
              <el-button type="success" link @click="controlDevice(row)">
                <el-icon><Operation /></el-icon>
                Control
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <div class="pagination-container">
          <el-pagination
              v-model:current-page="knxPagination.currentPage"
              v-model:page-size="knxPagination.pageSize"
              :page-sizes="[10, 20, 50]"
              :total="filteredKnxDevices.length"
              layout="total, sizes, prev, pager, next, jumper"
              @size-change="handleKnxSizeChange"
              @current-change="handleKnxCurrentChange"
          />
        </div>
      </el-card>
    </div>

    <!-- Lighting Scenes Content -->
    <div v-show="activeProtocol === 'scenes'">
      <el-card shadow="hover" class="table-card">
        <template #header>
          <div class="card-header">
            <span>Lighting Scenes</span>
            <el-button type="primary" @click="handleAddScene">
              <el-icon><Plus /></el-icon>
              Create Scene
            </el-button>
          </div>
        </template>

        <el-row :gutter="20" class="scenes-row">
          <el-col :xs="24" :sm="12" :md="8" v-for="scene in scenes" :key="scene.id">
            <el-card shadow="hover" class="scene-card" :class="{ 'scene-active': scene.isActive }">
              <div class="scene-content">
                <div class="scene-icon">
                  <el-icon :size="40"><Picture /></el-icon>
                </div>
                <div class="scene-info">
                  <div class="scene-name">{{ scene.name }}</div>
                  <div class="scene-description">{{ scene.description }}</div>
                  <div class="scene-devices">{{ scene.deviceCount }} devices</div>
                </div>
                <div class="scene-actions">
                  <el-button type="primary" circle @click="activateScene(scene)">
                    <el-icon><VideoPlay /></el-icon>
                  </el-button>
                  <el-button type="warning" circle @click="editScene(scene)">
                    <el-icon><Edit /></el-icon>
                  </el-button>
                  <el-button type="danger" circle @click="deleteScene(scene)">
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </el-card>
    </div>

    <!-- Schedules Content -->
    <div v-show="activeProtocol === 'schedules'">
      <el-card shadow="hover" class="table-card">
        <template #header>
          <div class="card-header">
            <span>Schedules</span>
            <el-button type="primary" @click="handleAddSchedule">
              <el-icon><Plus /></el-icon>
              Add Schedule
            </el-button>
          </div>
        </template>

        <el-table :data="schedules" stripe border style="width: 100%">
          <el-table-column prop="name" label="Schedule Name" min-width="150" />
          <el-table-column prop="time" label="Time" min-width="100" />
          <el-table-column prop="days" label="Days" min-width="200" />
          <el-table-column prop="action" label="Action" min-width="120">
            <template #default="{ row }">
              <el-tag :type="row.action === 'Activate Scene' ? 'primary' : 'success'">
                {{ row.action }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="target" label="Target" min-width="150" />
          <el-table-column prop="status" label="Status" min-width="100">
            <template #default="{ row }">
              <el-switch v-model="row.status" active-text="ON" inactive-text="OFF" @change="toggleSchedule(row)" />
            </template>
          </el-table-column>
          <el-table-column prop="lastExecuted" label="Last Executed" min-width="160" />
          <el-table-column label="Actions" fixed="right" min-width="150">
            <template #default="{ row }">
              <el-button type="primary" link @click="editSchedule(row)">
                <el-icon><Edit /></el-icon>
                Edit
              </el-button>
              <el-button type="danger" link @click="deleteSchedule(row)">
                <el-icon><Delete /></el-icon>
                Delete
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>

    <!-- Device Control Dialog -->
    <el-dialog v-model="controlDialogVisible" :title="`Control: ${selectedDevice?.name}`" width="450px">
      <div class="control-content" v-if="selectedDevice">
        <div class="current-status">
          <span>Current Status:</span>
          <el-tag :type="getStatusTag(selectedDevice.status)" size="large">
            {{ getStatusText(selectedDevice.status) }}
          </el-tag>
        </div>
        <el-divider />
        <div class="control-section">
          <div class="control-label">Brightness / Dimming Level:</div>
          <el-slider
              v-model="controlBrightness"
              :min="0"
              :max="100"
              @change="updateDeviceBrightness"
              :disabled="selectedDevice.status !== 'online'"
          />
          <div class="control-value">{{ controlBrightness }}%</div>
        </div>
        <el-divider />
        <div class="control-buttons">
          <el-button type="success" @click="sendControlCommand('on')" :disabled="selectedDevice.status !== 'online'">
            <el-icon><VideoPlay /></el-icon>
            Turn On
          </el-button>
          <el-button type="danger" @click="sendControlCommand('off')" :disabled="selectedDevice.status !== 'online'">
            <el-icon><VideoPause /></el-icon>
            Turn Off
          </el-button>
          <el-button type="warning" @click="sendControlCommand('max')" :disabled="selectedDevice.status !== 'online'">
            <el-icon><Sunny /></el-icon>
            Max Brightness
          </el-button>
        </div>
      </div>
    </el-dialog>

    <!-- Device Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" title="Device Details" width="650px">
      <el-descriptions :column="2" border v-if="selectedDevice">
        <el-descriptions-item label="Device Name">{{ selectedDevice.name }}</el-descriptions-item>
        <el-descriptions-item label="Location">{{ selectedDevice.location }}</el-descriptions-item>
        <el-descriptions-item label="Protocol">{{ activeProtocol === 'dali' ? 'DALI' : 'KNX' }}</el-descriptions-item>
        <el-descriptions-item label="Address">{{ activeProtocol === 'dali' ? selectedDevice.shortAddress : selectedDevice.individualAddress }}</el-descriptions-item>
        <el-descriptions-item label="Status">
          <el-tag :type="getStatusTag(selectedDevice.status)">{{ getStatusText(selectedDevice.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Brightness">{{ activeProtocol === 'dali' ? selectedDevice.dimmingLevel : selectedDevice.brightness }}%</el-descriptions-item>
        <el-descriptions-item label="Power">{{ selectedDevice.power?.toFixed(1) || 'N/A' }} W</el-descriptions-item>
        <el-descriptions-item label="Last Updated">{{ selectedDevice.lastUpdated }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>

    <!-- Add Scene Dialog -->
    <el-dialog v-model="sceneDialogVisible" :title="sceneDialogTitle" width="500px">
      <el-form :model="sceneForm" :rules="sceneRules" ref="sceneFormRef" label-width="120px">
        <el-form-item label="Scene Name" prop="name">
          <el-input v-model="sceneForm.name" placeholder="Enter scene name" />
        </el-form-item>
        <el-form-item label="Description" prop="description">
          <el-input v-model="sceneForm.description" type="textarea" placeholder="Enter description" />
        </el-form-item>
        <el-form-item label="Devices" prop="devices">
          <el-select v-model="sceneForm.devices" multiple placeholder="Select devices" style="width: 100%">
            <el-option
                v-for="device in allDevices"
                :key="device.id"
                :label="device.name"
                :value="device.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="Brightness Level" prop="brightness">
          <el-slider v-model="sceneForm.brightness" :min="0" :max="100" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="sceneDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="submitScene">Confirm</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import {
  Plus,
  Download,
  Refresh,
  Grid,
  Link,
  Lightning,
  Search,
  FullScreen,
  View,
  Operation,
  Delete,
  WarningFilled,
  VideoPlay,
  VideoPause,
  Edit,
  Picture,
  MagicStick,
  Cpu,
  Connection,
  Clock,
  Sunny
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Initializing DALI/KNX...',
  'Almost ready...'
]

// ==================== Data State ====================
const tableLoading = ref(false)
const activeProtocol = ref('dali')

const stats = ref({
  total: 0,
  online: 0,
  activeScenes: 0,
  energySaved: 0
})

// DALI Device Interface
interface DALIDevice {
  id: number
  shortAddress: string
  name: string
  location: string
  ballastType: string
  lampType: string
  status: 'online' | 'offline' | 'fault'
  dimmingLevel: number
  power: number
  lastUpdated: string
}

// KNX Device Interface
interface KNXDevice {
  id: number
  individualAddress: string
  name: string
  location: string
  deviceType: string
  status: 'online' | 'offline' | 'fault'
  brightness: number
  groupAddress: string
  lastUpdated: string
}

// Scene Interface
interface Scene {
  id: number
  name: string
  description: string
  deviceCount: number
  isActive: boolean
  devices?: number[]
  brightness?: number
}

// Schedule Interface
interface Schedule {
  id: number
  name: string
  time: string
  days: string
  action: string
  target: string
  status: boolean
  lastExecuted: string
}

const daliDevices = ref<DALIDevice[]>([])
const knxDevices = ref<KNXDevice[]>([])
const scenes = ref<Scene[]>([])
const schedules = ref<Schedule[]>([])

// Generate DALI mock data
const generateDaliData = (): DALIDevice[] => {
  const locations = ['Building A', 'Building B', 'Building C', 'Conference Room', 'Office Area']
  const ballastTypes = ['ECG', 'CCG', 'LED Driver']
  const lampTypes = ['LED', 'Fluorescent', 'Halogen']
  const statuses: ('online' | 'offline' | 'fault')[] = ['online', 'online', 'online', 'offline', 'fault']

  const data: DALIDevice[] = []
  for (let i = 0; i <= 63; i++) {
    const dimmingLevel = Math.floor(Math.random() * 101)
    data.push({
      id: i,
      shortAddress: `${Math.floor(i / 8)}/${i % 8}`,
      name: `DALI_${String(i).padStart(2, '0')}`,
      location: locations[Math.floor(Math.random() * locations.length)],
      ballastType: ballastTypes[Math.floor(Math.random() * ballastTypes.length)],
      lampType: lampTypes[Math.floor(Math.random() * lampTypes.length)],
      status: statuses[Math.floor(Math.random() * statuses.length)],
      dimmingLevel: dimmingLevel,
      power: parseFloat(((dimmingLevel / 100) * (20 + Math.random() * 30)).toFixed(1)),
      lastUpdated: new Date(Date.now() - Math.random() * 60 * 60 * 1000).toLocaleString()
    })
  }
  return data
}

// Generate KNX mock data
const generateKnxData = (): KNXDevice[] => {
  const locations = ['Building A', 'Building B', 'Building C', 'Meeting Room', 'Lobby']
  const deviceTypes = ['Dimmer', 'Switch Actuator', 'Blind Actuator', 'Lighting Controller']
  const statuses: ('online' | 'offline' | 'fault')[] = ['online', 'online', 'online', 'offline', 'fault']

  const data: KNXDevice[] = []
  for (let i = 1; i <= 48; i++) {
    data.push({
      id: i,
      individualAddress: `${Math.floor(i / 16)}.${Math.floor(i / 4) % 4}.${i % 4}`,
      name: `KNX_${String(i).padStart(2, '0')}`,
      location: locations[Math.floor(Math.random() * locations.length)],
      deviceType: deviceTypes[Math.floor(Math.random() * deviceTypes.length)],
      status: statuses[Math.floor(Math.random() * statuses.length)],
      brightness: Math.floor(Math.random() * 101),
      groupAddress: `${Math.floor(Math.random() * 7)}/${Math.floor(Math.random() * 7)}/${Math.floor(Math.random() * 255)}`,
      lastUpdated: new Date(Date.now() - Math.random() * 60 * 60 * 1000).toLocaleString()
    })
  }
  return data
}

// Generate scenes mock data
const generateScenesData = (): Scene[] => {
  return [
    { id: 1, name: 'Meeting', description: 'Optimal brightness for meetings', deviceCount: 12, isActive: false },
    { id: 2, name: 'Presentation', description: 'Dimmed lights for presentations', deviceCount: 12, isActive: false },
    { id: 3, name: 'Energy Saving', description: 'Reduced power consumption mode', deviceCount: 8, isActive: true },
    { id: 4, name: 'Cleaning', description: 'Full brightness for cleaning', deviceCount: 6, isActive: false },
    { id: 5, name: 'Emergency', description: 'Maximum visibility mode', deviceCount: 4, isActive: false },
    { id: 6, name: 'Evening', description: 'Warm and dimmed lighting', deviceCount: 10, isActive: false }
  ]
}

// Generate schedules mock data
const generateSchedulesData = (): Schedule[] => {
  return [
    { id: 1, name: 'Morning Turn On', time: '08:00', days: 'Mon-Fri', action: 'Activate Scene', target: 'Meeting', status: true, lastExecuted: '2024-01-15 08:00:00' },
    { id: 2, name: 'Evening Turn Off', time: '18:00', days: 'Mon-Fri', action: 'Activate Scene', target: 'Energy Saving', status: true, lastExecuted: '2024-01-15 18:00:00' },
    { id: 3, name: 'Weekend Mode', time: '10:00', days: 'Sat-Sun', action: 'Activate Scene', target: 'Energy Saving', status: false, lastExecuted: '2024-01-14 10:00:00' }
  ]
}

// Filters
const daliFilters = ref({
  deviceName: '',
  ballastType: '',
  status: ''
})

const knxFilters = ref({
  deviceName: '',
  groupAddress: '',
  status: ''
})

// Pagination
const daliPagination = ref({ currentPage: 1, pageSize: 10 })
const knxPagination = ref({ currentPage: 1, pageSize: 10 })

// Filtered data
const filteredDaliDevices = computed(() => {
  let filtered = daliDevices.value
  if (daliFilters.value.deviceName) {
    filtered = filtered.filter(d => d.name.toLowerCase().includes(daliFilters.value.deviceName.toLowerCase()))
  }
  if (daliFilters.value.ballastType) {
    filtered = filtered.filter(d => d.ballastType === daliFilters.value.ballastType)
  }
  if (daliFilters.value.status) {
    filtered = filtered.filter(d => d.status === daliFilters.value.status)
  }
  return filtered
})

const filteredKnxDevices = computed(() => {
  let filtered = knxDevices.value
  if (knxFilters.value.deviceName) {
    filtered = filtered.filter(k => k.name.toLowerCase().includes(knxFilters.value.deviceName.toLowerCase()))
  }
  if (knxFilters.value.groupAddress) {
    filtered = filtered.filter(k => k.groupAddress.includes(knxFilters.value.groupAddress))
  }
  if (knxFilters.value.status) {
    filtered = filtered.filter(k => k.status === knxFilters.value.status)
  }
  return filtered
})

const paginatedDaliDevices = computed(() => {
  const start = (daliPagination.value.currentPage - 1) * daliPagination.value.pageSize
  return filteredDaliDevices.value.slice(start, start + daliPagination.value.pageSize)
})

const paginatedKnxDevices = computed(() => {
  const start = (knxPagination.value.currentPage - 1) * knxPagination.value.pageSize
  return filteredKnxDevices.value.slice(start, start + knxPagination.value.pageSize)
})

const allDevices = computed(() => {
  return [
    ...daliDevices.value.map(d => ({ id: `dali_${d.id}`, name: d.name })),
    ...knxDevices.value.map(k => ({ id: `knx_${k.id}`, name: k.name }))
  ]
})

// Update stats
const updateStats = () => {
  stats.value.total = daliDevices.value.length + knxDevices.value.length
  stats.value.online = daliDevices.value.filter(d => d.status === 'online').length + knxDevices.value.filter(k => k.status === 'online').length
  stats.value.activeScenes = scenes.value.filter(s => s.isActive).length
  stats.value.energySaved = Math.round((stats.value.total * 15 * 0.3))
}

// ==================== Chart Functions ====================
const daliChartRef = ref<HTMLElement>()
const dimmingChartRef = ref<HTMLElement>()
let daliChart: echarts.ECharts | null = null
let dimmingChart: echarts.ECharts | null = null

const initCharts = () => {
  nextTick(() => {
    if (daliChartRef.value) {
      if (daliChart) daliChart.dispose()
      daliChart = echarts.init(daliChartRef.value)
      daliChart.setOption({
        tooltip: { trigger: 'axis' },
        xAxis: { type: 'category', data: ['0-20%', '20-40%', '40-60%', '60-80%', '80-100%'] },
        yAxis: { type: 'value', name: 'Device Count' },
        series: [{
          type: 'bar',
          data: [8, 15, 22, 12, 7],
          itemStyle: { borderRadius: [4, 4, 0, 0], color: '#409EFF' }
        }]
      })
    }

    if (dimmingChartRef.value) {
      if (dimmingChart) dimmingChart.dispose()
      dimmingChart = echarts.init(dimmingChartRef.value)
      dimmingChart.setOption({
        tooltip: { trigger: 'item' },
        legend: { orient: 'vertical', left: 'left' },
        series: [{
          type: 'pie',
          radius: '55%',
          data: [
            { value: 35, name: '0-25%', itemStyle: { color: '#67C23A' } },
            { value: 28, name: '25-50%', itemStyle: { color: '#409EFF' } },
            { value: 22, name: '50-75%', itemStyle: { color: '#E6A23C' } },
            { value: 15, name: '75-100%', itemStyle: { color: '#F56C6C' } }
          ]
        }]
      })
    }
  })
}

// ==================== Device Control ====================
const controlDialogVisible = ref(false)
const detailDialogVisible = ref(false)
const selectedDevice = ref<any>(null)
const controlBrightness = ref(0)

const controlDevice = (device: any) => {
  selectedDevice.value = device
  controlBrightness.value = activeProtocol.value === 'dali' ? device.dimmingLevel : device.brightness
  controlDialogVisible.value = true
}

const viewDeviceDetails = (device: any) => {
  selectedDevice.value = device
  detailDialogVisible.value = true
}

const updateDimming = (device: DALIDevice, value: number) => {
  device.dimmingLevel = value
  device.power = parseFloat(((value / 100) * 25).toFixed(1))
  device.lastUpdated = new Date().toLocaleString()
  ElMessage.success(`Dimming level updated to ${value}%`)
}

const updateBrightness = (device: KNXDevice, value: number) => {
  device.brightness = value
  device.lastUpdated = new Date().toLocaleString()
  ElMessage.success(`Brightness updated to ${value}%`)
}

const updateDeviceBrightness = (value: number) => {
  if (!selectedDevice.value) return
  if (activeProtocol.value === 'dali') {
    selectedDevice.value.dimmingLevel = value
    selectedDevice.value.power = parseFloat(((value / 100) * 25).toFixed(1))
  } else {
    selectedDevice.value.brightness = value
  }
  selectedDevice.value.lastUpdated = new Date().toLocaleString()
  ElMessage.info(`Brightness set to ${value}%`)
}

const sendControlCommand = (command: string) => {
  if (!selectedDevice.value) return

  if (command === 'on') {
    if (activeProtocol.value === 'dali') {
      selectedDevice.value.dimmingLevel = 80
      selectedDevice.value.power = parseFloat((80 / 100 * 25).toFixed(1))
    } else {
      selectedDevice.value.brightness = 80
    }
  } else if (command === 'off') {
    if (activeProtocol.value === 'dali') {
      selectedDevice.value.dimmingLevel = 0
      selectedDevice.value.power = 0
    } else {
      selectedDevice.value.brightness = 0
    }
  } else if (command === 'max') {
    if (activeProtocol.value === 'dali') {
      selectedDevice.value.dimmingLevel = 100
      selectedDevice.value.power = 25
    } else {
      selectedDevice.value.brightness = 100
    }
  }

  selectedDevice.value.lastUpdated = new Date().toLocaleString()
  controlBrightness.value = activeProtocol.value === 'dali' ? selectedDevice.value.dimmingLevel : selectedDevice.value.brightness
  ElMessage.success(`Command "${command}" executed`)
  controlDialogVisible.value = false
}

// ==================== Scene Management ====================
const sceneDialogVisible = ref(false)
const sceneDialogTitle = ref('Create Scene')
const sceneFormRef = ref()
const sceneForm = ref({
  name: '',
  description: '',
  devices: [],
  brightness: 70
})

const sceneRules = {
  name: [{ required: true, message: 'Please enter scene name', trigger: 'blur' }],
  devices: [{ required: true, message: 'Please select devices', trigger: 'change' }]
}

const handleAddScene = () => {
  sceneDialogTitle.value = 'Create Scene'
  sceneForm.value = { name: '', description: '', devices: [], brightness: 70 }
  sceneDialogVisible.value = true
}

const editScene = (scene: Scene) => {
  sceneDialogTitle.value = 'Edit Scene'
  sceneForm.value = {
    name: scene.name,
    description: scene.description,
    devices: scene.devices || [],
    brightness: scene.brightness || 70
  }
  sceneDialogVisible.value = true
}

const submitScene = async () => {
  try {
    await sceneFormRef.value?.validate()
    ElMessage.success('Scene saved successfully')
    sceneDialogVisible.value = false
  } catch (error) {
    ElMessage.error('Please fill in all required fields')
  }
}

const activateScene = (scene: Scene) => {
  scenes.value.forEach(s => s.isActive = false)
  scene.isActive = true
  stats.value.activeScenes = 1
  ElMessage.success(`Scene "${scene.name}" activated`)
}

const deleteScene = (scene: Scene) => {
  ElMessageBox.confirm(`Delete scene "${scene.name}"?`, 'Warning', {
    confirmButtonText: 'Confirm',
    cancelButtonText: 'Cancel',
    type: 'warning'
  }).then(() => {
    const index = scenes.value.findIndex(s => s.id === scene.id)
    if (index > -1) {
      scenes.value.splice(index, 1)
      ElMessage.success('Scene deleted')
    }
  }).catch(() => {})
}

// ==================== Schedule Management ====================
const handleAddSchedule = () => {
  ElMessage.info('Add schedule feature')
}

const editSchedule = (schedule: Schedule) => {
  ElMessage.info('Edit schedule feature')
}

const deleteSchedule = (schedule: Schedule) => {
  ElMessageBox.confirm(`Delete schedule "${schedule.name}"?`, 'Warning', {
    confirmButtonText: 'Confirm',
    cancelButtonText: 'Cancel',
    type: 'warning'
  }).then(() => {
    const index = schedules.value.findIndex(s => s.id === schedule.id)
    if (index > -1) {
      schedules.value.splice(index, 1)
      ElMessage.success('Schedule deleted')
    }
  }).catch(() => {})
}

const toggleSchedule = (schedule: Schedule) => {
  ElMessage.info(`Schedule "${schedule.name}" ${schedule.status ? 'enabled' : 'disabled'}`)
}

// ==================== Actions ====================
const handleProtocolChange = () => {
  initCharts()
}

const discoverDevices = () => {
  tableLoading.value = true
  setTimeout(() => {
    ElMessage.success('Device discovery completed: 64 devices found')
    tableLoading.value = false
  }, 2000)
}

const syncKnxDevices = () => {
  tableLoading.value = true
  setTimeout(() => {
    ElMessage.success('KNX devices synchronized')
    tableLoading.value = false
  }, 1500)
}

const refreshData = () => {
  tableLoading.value = true
  setTimeout(() => {
    daliDevices.value = generateDaliData()
    knxDevices.value = generateKnxData()
    scenes.value = generateScenesData()
    schedules.value = generateSchedulesData()
    updateStats()
    initCharts()
    tableLoading.value = false
    ElMessage.success('Data refreshed')
  }, 800)
}

const handleExport = () => {
  ElMessage.success('Export started')
}

const handleDaliSearch = () => {
  daliPagination.value.currentPage = 1
  ElMessage.success(`Found ${filteredDaliDevices.value.length} DALI devices`)
}

const resetDaliFilters = () => {
  daliFilters.value = { deviceName: '', ballastType: '', status: '' }
  daliPagination.value.currentPage = 1
}

const handleKnxSearch = () => {
  knxPagination.value.currentPage = 1
  ElMessage.success(`Found ${filteredKnxDevices.value.length} KNX devices`)
}

const resetKnxFilters = () => {
  knxFilters.value = { deviceName: '', groupAddress: '', status: '' }
  knxPagination.value.currentPage = 1
}

const handleDaliSizeChange = () => { daliPagination.value.currentPage = 1 }
const handleDaliCurrentChange = () => {}
const handleKnxSizeChange = () => { knxPagination.value.currentPage = 1 }
const handleKnxCurrentChange = () => {}

// Helper functions
const getStatusTag = (status: string) => {
  const map: Record<string, string> = { online: 'success', offline: 'info', fault: 'danger' }
  return map[status] || 'info'
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = { online: 'Online', offline: 'Offline', fault: 'Fault' }
  return map[status] || status
}

const getBallastTypeTag = (type: string) => {
  const map: Record<string, string> = { ECG: 'success', CCG: 'warning', 'LED Driver': 'primary' }
  return map[type] || 'info'
}

const getDeviceTypeTag = (type: string) => {
  const map: Record<string, string> = { Dimmer: 'primary', 'Switch Actuator': 'success', 'Blind Actuator': 'warning', 'Lighting Controller': 'danger' }
  return map[type] || 'info'
}

// ==================== Lifecycle ====================
onMounted(() => {
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

  setTimeout(() => {
    clearInterval(messageInterval)
    clearInterval(progressInterval)
    loadingProgress.value = 100
    loadingMessage.value = 'Ready!'

    setTimeout(() => {
      isLoaded.value = true
      daliDevices.value = generateDaliData()
      knxDevices.value = generateKnxData()
      scenes.value = generateScenesData()
      schedules.value = generateSchedulesData()
      updateStats()
      initCharts()
    }, 400)
  }, 2000)
})

watch([daliChartRef, dimmingChartRef], () => {
  window.addEventListener('resize', () => {
    daliChart?.resize()
    dimmingChart?.resize()
  })
})
</script>

<style scoped>
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

.spinner-ring:nth-child(1) {
  border-top-color: #3b82f6;
  animation-delay: 0s;
}

.spinner-ring:nth-child(2) {
  border-right-color: #f59e0b;
  animation-delay: 0.2s;
  width: 70%;
  height: 70%;
  top: 15%;
  left: 15%;
}

.spinner-ring:nth-child(3) {
  border-bottom-color: #10b981;
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

.dali-knx-container {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  background: white;
  padding: 16px 20px;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.page-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  cursor: pointer;
  transition: all 0.3s ease;
  border-radius: 12px;
}

.stat-card:hover {
  transform: translateY(-4px);
}

.stat-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-info {
  flex: 1;
}

.stat-title {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
}

.stat-value.online {
  color: #67C23A;
}

.stat-value.scenes {
  color: #E6A23C;
}

.stat-value.saved {
  color: #409EFF;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.stat-icon.total {
  background: rgba(64, 158, 255, 0.1);
  color: #409EFF;
}

.stat-icon.online-bg {
  background: rgba(103, 194, 58, 0.1);
  color: #67C23A;
}

.stat-icon.scenes-bg {
  background: rgba(230, 162, 60, 0.1);
  color: #E6A23C;
}

.stat-icon.saved-bg {
  background: rgba(64, 158, 255, 0.1);
  color: #409EFF;
}

.protocol-card {
  margin-bottom: 20px;
  border-radius: 12px;
}

.protocol-tab {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-card {
  margin-bottom: 20px;
  border-radius: 12px;
}

.filter-form {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.charts-row {
  margin-bottom: 20px;
}

.chart-card {
  border-radius: 12px;
}

.chart-container {
  width: 100%;
  height: 300px;
}

.table-card {
  border-radius: 12px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.scenes-row {
  margin-top: 10px;
}

.scene-card {
  cursor: pointer;
  transition: all 0.3s ease;
  border-radius: 12px;
  margin-bottom: 20px;
}

.scene-card:hover {
  transform: translateY(-4px);
}

.scene-active {
  border: 2px solid #67C23A;
  background: rgba(103, 194, 58, 0.05);
}

.scene-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.scene-icon {
  width: 60px;
  height: 60px;
  background: rgba(64, 158, 255, 0.1);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.scene-info {
  flex: 1;
}

.scene-name {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 4px;
}

.scene-description {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.scene-devices {
  font-size: 11px;
  color: #67C23A;
}

.scene-actions {
  display: flex;
  gap: 8px;
}

.control-content {
  padding: 10px;
}

.current-status {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
  font-weight: 500;
}

.control-section {
  margin: 15px 0;
}

.control-label {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 10px;
}

.control-value {
  text-align: center;
  margin-top: 10px;
  font-size: 18px;
  font-weight: 600;
  color: #409EFF;
}

.control-buttons {
  display: flex;
  gap: 12px;
  justify-content: center;
  margin-top: 15px;
}
</style>