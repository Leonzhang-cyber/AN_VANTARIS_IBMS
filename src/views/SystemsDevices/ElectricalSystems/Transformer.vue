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
        <div class="loading-tip">Transformer Monitoring</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="transformer-container">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h2>Transformer</h2>
        <p class="header-subtitle">Power Transformer | 11kV / 400V | 2.5 MVA</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="handleExport">
          <el-icon><Download /></el-icon>
          Export Report
        </el-button>
        <el-button @click="refreshData">
          <el-icon><Refresh /></el-icon>
          Refresh
        </el-button>
      </div>
    </div>

    <!-- Transformer Info Cards -->
    <el-row :gutter="20" class="info-row">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="info-card">
          <div class="info-icon">
            <el-icon :size="28"><OfficeBuilding /></el-icon>
          </div>
          <div class="info-content">
            <div class="info-label">Transformer ID</div>
            <div class="info-value">TFR-001</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="info-card">
          <div class="info-icon">
            <el-icon :size="28"><Grid /></el-icon>
          </div>
          <div class="info-content">
            <div class="info-label">Type</div>
            <div class="info-value">Oil-Immersed</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="info-card">
          <div class="info-icon">
            <el-icon :size="28"><Lightning /></el-icon>
          </div>
          <div class="info-content">
            <div class="info-label">Rating</div>
            <div class="info-value">2.5 MVA</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="info-card">
          <div class="info-icon">
            <el-icon :size="28"><Location /></el-icon>
          </div>
          <div class="info-content">
            <div class="info-label">Location</div>
            <div class="info-value">Main Substation</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Main Metrics Row -->
    <el-row :gutter="20" class="metrics-row">
      <el-col :xs="24" :sm="12" :md="6">
        <div class="metric-card load">
          <div class="metric-icon">
            <el-icon :size="28"><Lightning /></el-icon>
          </div>
          <div class="metric-info">
            <div class="metric-label">Current Load</div>
            <div class="metric-value">{{ metrics.currentLoad }} <span class="unit">kW</span></div>
            <el-progress :percentage="metrics.loadPercent" :color="getLoadColor(metrics.loadPercent)" :stroke-width="8" />
            <div class="metric-sub">Rated: {{ metrics.ratedPower }} kW</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <div class="metric-card temperature">
          <div class="metric-icon">
            <el-icon :size="28"><Warning /></el-icon>
          </div>
          <div class="metric-info">
            <div class="metric-label">Top Oil Temp</div>
            <div class="metric-value">{{ metrics.topOilTemp }} <span class="unit">°C</span></div>
            <el-progress :percentage="metrics.oilTempPercent" :color="getTempColor(metrics.topOilTemp)" :stroke-width="8" />
            <div class="metric-sub">Limit: 95°C</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <div class="metric-card efficiency">
          <div class="metric-icon">
            <el-icon :size="28"><TrendCharts /></el-icon>
          </div>
          <div class="metric-info">
            <div class="metric-label">Efficiency</div>
            <div class="metric-value">{{ metrics.efficiency }} <span class="unit">%</span></div>
            <el-progress :percentage="metrics.efficiency" :color="'#67C23A'" :stroke-width="8" />
            <div class="metric-sub">Losses: {{ metrics.losses }} kW</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <div class="metric-card aging">
          <div class="metric-icon">
            <el-icon :size="28"><Timer /></el-icon>
          </div>
          <div class="metric-info">
            <div class="metric-label">Insulation Aging</div>
            <div class="metric-value">{{ metrics.agingFactor }} <span class="unit">p.u.</span></div>
            <el-progress :percentage="metrics.agingPercent" :color="getAgingColor(metrics.agingPercent)" :stroke-width="8" />
            <div class="metric-sub">Remaining: {{ metrics.remainingLife }} years</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Voltage & Current Row -->
    <el-row :gutter="20" class="voltage-row">
      <el-col :xs="24" :md="12">
        <el-card shadow="hover" class="voltage-card">
          <template #header>
            <div class="card-header">
              <span>Primary Side (11kV)</span>
              <el-tag type="danger">High Voltage</el-tag>
            </div>
          </template>
          <div class="phase-values">
            <div class="phase-item">
              <span class="phase-label">R-Y</span>
              <span class="phase-value">{{ primary.voltageRY }} <span class="unit">kV</span></span>
              <el-tag :type="getVoltageStatus(primary.voltageRY, 11)" size="small">{{ getVoltageStatusText(primary.voltageRY, 11) }}</el-tag>
            </div>
            <div class="phase-item">
              <span class="phase-label">Y-B</span>
              <span class="phase-value">{{ primary.voltageYB }} <span class="unit">kV</span></span>
              <el-tag :type="getVoltageStatus(primary.voltageYB, 11)" size="small">{{ getVoltageStatusText(primary.voltageYB, 11) }}</el-tag>
            </div>
            <div class="phase-item">
              <span class="phase-label">B-R</span>
              <span class="phase-value">{{ primary.voltageBR }} <span class="unit">kV</span></span>
              <el-tag :type="getVoltageStatus(primary.voltageBR, 11)" size="small">{{ getVoltageStatusText(primary.voltageBR, 11) }}</el-tag>
            </div>
            <div class="phase-item">
              <span class="phase-label">Current (R)</span>
              <span class="phase-value">{{ primary.currentR }} <span class="unit">A</span></span>
              <el-progress :percentage="primary.currentRPercent" :stroke-width="6" :show-text="false" style="width: 80px" />
            </div>
            <div class="phase-item">
              <span class="phase-label">Current (Y)</span>
              <span class="phase-value">{{ primary.currentY }} <span class="unit">A</span></span>
              <el-progress :percentage="primary.currentYPercent" :stroke-width="6" :show-text="false" style="width: 80px" />
            </div>
            <div class="phase-item">
              <span class="phase-label">Current (B)</span>
              <span class="phase-value">{{ primary.currentB }} <span class="unit">A</span></span>
              <el-progress :percentage="primary.currentBPercent" :stroke-width="6" :show-text="false" style="width: 80px" />
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :md="12">
        <el-card shadow="hover" class="voltage-card">
          <template #header>
            <div class="card-header">
              <span>Secondary Side (400V)</span>
              <el-tag type="success">Low Voltage</el-tag>
            </div>
          </template>
          <div class="phase-values">
            <div class="phase-item">
              <span class="phase-label">R-Y</span>
              <span class="phase-value">{{ secondary.voltageRY }} <span class="unit">V</span></span>
              <el-tag :type="getVoltageStatus(secondary.voltageRY, 400)" size="small">{{ getVoltageStatusText(secondary.voltageRY, 400) }}</el-tag>
            </div>
            <div class="phase-item">
              <span class="phase-label">Y-B</span>
              <span class="phase-value">{{ secondary.voltageYB }} <span class="unit">V</span></span>
              <el-tag :type="getVoltageStatus(secondary.voltageYB, 400)" size="small">{{ getVoltageStatusText(secondary.voltageYB, 400) }}</el-tag>
            </div>
            <div class="phase-item">
              <span class="phase-label">B-R</span>
              <span class="phase-value">{{ secondary.voltageBR }} <span class="unit">V</span></span>
              <el-tag :type="getVoltageStatus(secondary.voltageBR, 400)" size="small">{{ getVoltageStatusText(secondary.voltageBR, 400) }}</el-tag>
            </div>
            <div class="phase-item">
              <span class="phase-label">Current (R)</span>
              <span class="phase-value">{{ secondary.currentR }} <span class="unit">A</span></span>
              <el-progress :percentage="secondary.currentRPercent" :stroke-width="6" :show-text="false" style="width: 80px" />
            </div>
            <div class="phase-item">
              <span class="phase-label">Current (Y)</span>
              <span class="phase-value">{{ secondary.currentY }} <span class="unit">A</span></span>
              <el-progress :percentage="secondary.currentYPercent" :stroke-width="6" :show-text="false" style="width: 80px" />
            </div>
            <div class="phase-item">
              <span class="phase-label">Current (B)</span>
              <span class="phase-value">{{ secondary.currentB }} <span class="unit">A</span></span>
              <el-progress :percentage="secondary.currentBPercent" :stroke-width="6" :show-text="false" style="width: 80px" />
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Temperature & Gas Monitoring -->
    <el-row :gutter="20" class="monitoring-row">
      <el-col :xs="24" :md="8">
        <el-card shadow="hover" class="temp-card">
          <template #header>
            <div class="card-header">
              <span>Temperature Monitoring</span>
              <el-icon><Warning /></el-icon>
            </div>
          </template>
          <div class="temp-grid">
            <div class="temp-item">
              <div class="temp-label">Top Oil</div>
              <div class="temp-value" :class="getTempClass(metrics.topOilTemp)">{{ metrics.topOilTemp }}°C</div>
              <el-progress :percentage="metrics.oilTempPercent" :color="getTempColor(metrics.topOilTemp)" :stroke-width="6" />
            </div>
            <div class="temp-item">
              <div class="temp-label">Winding Hotspot</div>
              <div class="temp-value" :class="getTempClass(metrics.windingTemp)">{{ metrics.windingTemp }}°C</div>
              <el-progress :percentage="metrics.windingTempPercent" :color="getTempColor(metrics.windingTemp)" :stroke-width="6" />
            </div>
            <div class="temp-item">
              <div class="temp-label">Ambient</div>
              <div class="temp-value">{{ metrics.ambientTemp }}°C</div>
              <el-progress :percentage="metrics.ambientPercent" :color="'#909399'" :stroke-width="6" />
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :md="8">
        <el-card shadow="hover" class="gas-card">
          <template #header>
            <div class="card-header">
              <span>Dissolved Gas Analysis (DGA)</span>
              <el-icon><DataAnalysis /></el-icon>
            </div>
          </template>
          <div class="gas-list">
            <div class="gas-item">
              <span class="gas-label">H₂ (Hydrogen)</span>
              <span class="gas-value" :class="getGasClass(gas.h2)">{{ gas.h2 }} ppm</span>
              <el-progress :percentage="gas.h2Percent" :color="getGasColor(gas.h2Percent)" :stroke-width="6" />
            </div>
            <div class="gas-item">
              <span class="gas-label">C₂H₂ (Acetylene)</span>
              <span class="gas-value" :class="getGasClass(gas.c2h2)">{{ gas.c2h2 }} ppm</span>
              <el-progress :percentage="gas.c2h2Percent" :color="getGasColor(gas.c2h2Percent)" :stroke-width="6" />
            </div>
            <div class="gas-item">
              <span class="gas-label">CH₄ (Methane)</span>
              <span class="gas-value">{{ gas.ch4 }} ppm</span>
              <el-progress :percentage="gas.ch4Percent" :color="getGasColor(gas.ch4Percent)" :stroke-width="6" />
            </div>
            <div class="gas-item">
              <span class="gas-label">C₂H₄ (Ethylene)</span>
              <span class="gas-value">{{ gas.c2h4 }} ppm</span>
              <el-progress :percentage="gas.c2h4Percent" :color="getGasColor(gas.c2h4Percent)" :stroke-width="6" />
            </div>
            <div class="gas-item">
              <span class="gas-label">C₂H₆ (Ethane)</span>
              <span class="gas-value">{{ gas.c2h6 }} ppm</span>
              <el-progress :percentage="gas.c2h6Percent" :color="getGasColor(gas.c2h6Percent)" :stroke-width="6" />
            </div>
            <div class="gas-item">
              <span class="gas-label">CO (Carbon Monoxide)</span>
              <span class="gas-value">{{ gas.co }} ppm</span>
              <el-progress :percentage="gas.coPercent" :color="getGasColor(gas.coPercent)" :stroke-width="6" />
            </div>
            <div class="gas-item">
              <span class="gas-label">CO₂ (Carbon Dioxide)</span>
              <span class="gas-value">{{ gas.co2 }} ppm</span>
              <el-progress :percentage="gas.co2Percent" :color="getGasColor(gas.co2Percent)" :stroke-width="6" />
            </div>
          </div>
          <div class="gas-footer">
            <el-tag :type="gas.overallStatus" size="large">{{ gas.overallStatusText }}</el-tag>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :md="8">
        <el-card shadow="hover" class="status-card">
          <template #header>
            <div class="card-header">
              <span>Transformer Health</span>
              <el-icon><Monitor /></el-icon>
            </div>
          </template>
          <div class="health-content">
            <div class="health-score">
              <el-progress
                  type="circle"
                  :percentage="healthScore"
                  :color="getHealthColor(healthScore)"
                  :width="140"
                  :stroke-width="12"
              >
                <template #default>
                  <div class="health-text">
                    <span class="health-value">{{ healthScore }}</span>
                    <span class="health-unit">%</span>
                  </div>
                </template>
              </el-progress>
              <div class="health-status">
                <el-tag :type="getHealthTag(healthScore)" size="large">
                  {{ getHealthStatus(healthScore) }}
                </el-tag>
              </div>
            </div>
            <div class="health-metrics">
              <div class="health-metric">
                <span>Last Maintenance</span>
                <span>{{ lastMaintenance }}</span>
              </div>
              <div class="health-metric">
                <span>Next Due</span>
                <span>{{ nextMaintenance }}</span>
              </div>
              <div class="health-metric">
                <span>Oil Level</span>
                <span :class="oilLevel === 'Normal' ? 'normal' : 'warning'">{{ oilLevel }}</span>
              </div>
              <div class="health-metric">
                <span>Bushing Condition</span>
                <span>{{ bushingCondition }}</span>
              </div>
            </div>
          </div>
          <div class="health-actions">
            <el-button type="primary" plain size="small" @click="showMaintenanceHistory">Maintenance History</el-button>
            <el-button type="warning" plain size="small" @click="scheduleTest">Schedule Test</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Load & Efficiency Charts -->
    <el-row :gutter="20" class="charts-row">
      <el-col :xs="24" :md="14">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>Load & Temperature Trend (Last 24 Hours)</span>
              <el-radio-group v-model="chartPeriod" size="small" @change="updateTrendChart">
                <el-radio-button label="hour">Hourly</el-radio-button>
                <el-radio-button label="day">Daily</el-radio-button>
                <el-radio-button label="week">Weekly</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div ref="trendChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :xs="24" :md="10">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>Efficiency & Losses</span>
            </div>
          </template>
          <div ref="efficiencyChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Alarms & Events -->
    <el-card shadow="hover" class="alarms-card">
      <template #header>
        <div class="card-header">
          <span>Recent Alarms & Events</span>
          <el-badge :value="alarms.length" type="danger" v-if="alarms.length > 0" />
        </div>
      </template>
      <el-table :data="alarms" stripe border style="width: 100%">
        <el-table-column prop="time" label="Time" width="160" />
        <el-table-column prop="type" label="Type" width="120">
          <template #default="{ row }">
            <el-tag :type="row.severity" size="small">{{ row.type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="message" label="Message" />
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'Acknowledged' ? 'success' : 'warning'" size="small">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Action" width="100">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="acknowledgeAlarm(row)">Acknowledge</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import {
  Download,
  Refresh,
  OfficeBuilding,
  Grid,
  Lightning,
  Location,
  Warning,
  TrendCharts,
  Timer,
  DataAnalysis,
  Monitor
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Initializing transformer monitoring...',
  'Reading DGA sensors...',
  'Almost ready...'
]

// ==================== Data State ====================
const chartPeriod = ref('hour')

// Metrics
const metrics = ref({
  currentLoad: 0,
  loadPercent: 0,
  ratedPower: 2500,
  topOilTemp: 0,
  oilTempPercent: 0,
  windingTemp: 0,
  windingTempPercent: 0,
  ambientTemp: 0,
  ambientPercent: 0,
  efficiency: 0,
  losses: 0,
  agingFactor: 0,
  agingPercent: 0,
  remainingLife: 0
})

// Primary Side (11kV)
const primary = ref({
  voltageRY: 0,
  voltageYB: 0,
  voltageBR: 0,
  currentR: 0,
  currentY: 0,
  currentB: 0,
  currentRPercent: 0,
  currentYPercent: 0,
  currentBPercent: 0
})

// Secondary Side (400V)
const secondary = ref({
  voltageRY: 0,
  voltageYB: 0,
  voltageBR: 0,
  currentR: 0,
  currentY: 0,
  currentB: 0,
  currentRPercent: 0,
  currentYPercent: 0,
  currentBPercent: 0
})

// Dissolved Gas Analysis
const gas = ref({
  h2: 0,
  h2Percent: 0,
  c2h2: 0,
  c2h2Percent: 0,
  ch4: 0,
  ch4Percent: 0,
  c2h4: 0,
  c2h4Percent: 0,
  c2h6: 0,
  c2h6Percent: 0,
  co: 0,
  coPercent: 0,
  co2: 0,
  co2Percent: 0,
  overallStatus: 'success',
  overallStatusText: 'Normal'
})

// Health
const healthScore = ref(92)
const lastMaintenance = ref('2024-01-10')
const nextMaintenance = ref('2024-04-10')
const oilLevel = ref('Normal')
const bushingCondition = ref('Good')

// Alarms
interface Alarm {
  id: number
  time: string
  type: string
  message: string
  severity: string
  status: string
}

const alarms = ref<Alarm[]>([
  { id: 1, time: '2024-01-15 08:23:15', type: 'Temperature', message: 'Winding temperature exceeded 105°C', severity: 'warning', status: 'Active' },
  { id: 2, time: '2024-01-14 14:30:22', type: 'Gas', message: 'Hydrogen level elevated', severity: 'warning', status: 'Acknowledged' },
  { id: 3, time: '2024-01-13 22:15:03', type: 'Overload', message: 'Transformer overload for 5 minutes', severity: 'danger', status: 'Active' },
  { id: 4, time: '2024-01-12 09:45:30', type: 'Oil', message: 'Oil level low', severity: 'warning', status: 'Acknowledged' }
])

// Generate mock data
const generateMetrics = () => {
  const load = Math.floor(800 + Math.random() * 1200)
  metrics.value.currentLoad = load
  metrics.value.loadPercent = parseFloat(((load / metrics.value.ratedPower) * 100).toFixed(1))

  const oilTemp = 65 + Math.random() * 20
  metrics.value.topOilTemp = parseFloat(oilTemp.toFixed(1))
  metrics.value.oilTempPercent = parseFloat(((oilTemp / 95) * 100).toFixed(1))

  const windingTemp = oilTemp + 15 + Math.random() * 10
  metrics.value.windingTemp = parseFloat(windingTemp.toFixed(1))
  metrics.value.windingTempPercent = parseFloat(((windingTemp / 120) * 100).toFixed(1))

  metrics.value.ambientTemp = parseFloat((25 + Math.random() * 10).toFixed(1))
  metrics.value.ambientPercent = parseFloat(((metrics.value.ambientTemp / 50) * 100).toFixed(1))

  metrics.value.efficiency = parseFloat((97.5 - (load / metrics.value.ratedPower) * 0.5 + Math.random() * 0.5).toFixed(1))
  metrics.value.losses = parseFloat((metrics.value.currentLoad * (100 - metrics.value.efficiency) / 100).toFixed(1))

  metrics.value.agingFactor = parseFloat((0.5 + Math.random() * 0.8).toFixed(2))
  metrics.value.agingPercent = parseFloat((metrics.value.agingFactor * 100).toFixed(1))
  metrics.value.remainingLife = Math.max(5, Math.floor(25 - (metrics.value.agingFactor * 20) + Math.random() * 5))
}

const generateVoltageCurrent = () => {
  // Primary (11kV)
  primary.value.voltageRY = parseFloat((10.8 + Math.random() * 0.4).toFixed(1))
  primary.value.voltageYB = parseFloat((10.9 + Math.random() * 0.4).toFixed(1))
  primary.value.voltageBR = parseFloat((10.85 + Math.random() * 0.4).toFixed(1))

  const baseCurrent = metrics.value.currentLoad / 11 / 1.732
  primary.value.currentR = parseFloat((baseCurrent * (0.95 + Math.random() * 0.1)).toFixed(1))
  primary.value.currentY = parseFloat((baseCurrent * (0.95 + Math.random() * 0.1)).toFixed(1))
  primary.value.currentB = parseFloat((baseCurrent * (0.95 + Math.random() * 0.1)).toFixed(1))

  primary.value.currentRPercent = parseFloat(((primary.value.currentR / 150) * 100).toFixed(1))
  primary.value.currentYPercent = parseFloat(((primary.value.currentY / 150) * 100).toFixed(1))
  primary.value.currentBPercent = parseFloat(((primary.value.currentB / 150) * 100).toFixed(1))

  // Secondary (400V)
  secondary.value.voltageRY = parseFloat((390 + Math.random() * 20).toFixed(1))
  secondary.value.voltageYB = parseFloat((392 + Math.random() * 18).toFixed(1))
  secondary.value.voltageBR = parseFloat((388 + Math.random() * 22).toFixed(1))

  const baseSecCurrent = metrics.value.currentLoad * 1000 / 400 / 1.732
  secondary.value.currentR = parseFloat((baseSecCurrent * (0.95 + Math.random() * 0.1)).toFixed(1))
  secondary.value.currentY = parseFloat((baseSecCurrent * (0.95 + Math.random() * 0.1)).toFixed(1))
  secondary.value.currentB = parseFloat((baseSecCurrent * (0.95 + Math.random() * 0.1)).toFixed(1))

  secondary.value.currentRPercent = parseFloat(((secondary.value.currentR / 4000) * 100).toFixed(1))
  secondary.value.currentYPercent = parseFloat(((secondary.value.currentY / 4000) * 100).toFixed(1))
  secondary.value.currentBPercent = parseFloat(((secondary.value.currentB / 4000) * 100).toFixed(1))
}

const generateGasData = () => {
  gas.value.h2 = parseFloat((50 + Math.random() * 100).toFixed(1))
  gas.value.h2Percent = parseFloat(((gas.value.h2 / 200) * 100).toFixed(1))

  gas.value.c2h2 = parseFloat((2 + Math.random() * 5).toFixed(1))
  gas.value.c2h2Percent = parseFloat(((gas.value.c2h2 / 10) * 100).toFixed(1))

  gas.value.ch4 = parseFloat((30 + Math.random() * 50).toFixed(1))
  gas.value.ch4Percent = parseFloat(((gas.value.ch4 / 100) * 100).toFixed(1))

  gas.value.c2h4 = parseFloat((20 + Math.random() * 40).toFixed(1))
  gas.value.c2h4Percent = parseFloat(((gas.value.c2h4 / 80) * 100).toFixed(1))

  gas.value.c2h6 = parseFloat((15 + Math.random() * 30).toFixed(1))
  gas.value.c2h6Percent = parseFloat(((gas.value.c2h6 / 60) * 100).toFixed(1))

  gas.value.co = parseFloat((100 + Math.random() * 200).toFixed(1))
  gas.value.coPercent = parseFloat(((gas.value.co / 500) * 100).toFixed(1))

  gas.value.co2 = parseFloat((1000 + Math.random() * 1000).toFixed(1))
  gas.value.co2Percent = parseFloat(((gas.value.co2 / 3000) * 100).toFixed(1))

  // Determine overall status
  const highValues = [gas.value.h2, gas.value.c2h2, gas.value.ch4, gas.value.c2h4]
  const maxHigh = Math.max(...highValues)
  if (maxHigh > 150 || gas.value.c2h2 > 8) {
    gas.value.overallStatus = 'danger'
    gas.value.overallStatusText = 'Critical - Immediate Action Required'
  } else if (maxHigh > 80 || gas.value.c2h2 > 4) {
    gas.value.overallStatus = 'warning'
    gas.value.overallStatusText = 'Abnormal - Investigate'
  } else {
    gas.value.overallStatus = 'success'
    gas.value.overallStatusText = 'Normal - OK'
  }
}

// Helper functions for colors and status
const getLoadColor = (percent: number) => {
  if (percent < 60) return '#67C23A'
  if (percent < 85) return '#E6A23C'
  return '#F56C6C'
}

const getTempColor = (temp: number) => {
  if (temp < 80) return '#67C23A'
  if (temp < 95) return '#E6A23C'
  return '#F56C6C'
}

const getTempClass = (temp: number) => {
  if (temp < 80) return ''
  if (temp < 95) return 'warning'
  return 'danger'
}

const getAgingColor = (percent: number) => {
  if (percent < 50) return '#67C23A'
  if (percent < 80) return '#E6A23C'
  return '#F56C6C'
}

const getVoltageStatus = (voltage: number, nominal: number) => {
  const percent = (voltage / nominal) * 100
  if (percent >= 95 && percent <= 105) return 'success'
  if (percent >= 90 && percent <= 110) return 'warning'
  return 'danger'
}

const getVoltageStatusText = (voltage: number, nominal: number) => {
  const percent = (voltage / nominal) * 100
  if (percent >= 95 && percent <= 105) return 'Normal'
  if (percent >= 90 && percent <= 110) return 'Margin'
  return 'Abnormal'
}

const getGasClass = (value: number) => {
  if (value < 100) return ''
  if (value < 200) return 'warning'
  return 'danger'
}

const getGasColor = (percent: number) => {
  if (percent < 50) return '#67C23A'
  if (percent < 80) return '#E6A23C'
  return '#F56C6C'
}

const getHealthColor = (score: number) => {
  if (score >= 85) return '#67C23A'
  if (score >= 70) return '#E6A23C'
  return '#F56C6C'
}

const getHealthTag = (score: number) => {
  if (score >= 85) return 'success'
  if (score >= 70) return 'warning'
  return 'danger'
}

const getHealthStatus = (score: number) => {
  if (score >= 85) return 'Healthy'
  if (score >= 70) return 'Fair'
  return 'Critical'
}

// ==================== Chart Functions ====================
const trendChartRef = ref<HTMLElement>()
const efficiencyChartRef = ref<HTMLElement>()
let trendChart: echarts.ECharts | null = null
let efficiencyChart: echarts.ECharts | null = null

const initCharts = () => {
  nextTick(() => {
    if (trendChartRef.value) {
      if (trendChart) trendChart.dispose()
      trendChart = echarts.init(trendChartRef.value)
      updateTrendChart()
    }

    if (efficiencyChartRef.value) {
      if (efficiencyChart) efficiencyChart.dispose()
      efficiencyChart = echarts.init(efficiencyChartRef.value)
      updateEfficiencyChart()
    }
  })
}

const updateTrendChart = () => {
  let loadData: number[] = []
  let tempData: number[] = []
  let xAxisData: string[] = []

  if (chartPeriod.value === 'hour') {
    xAxisData = Array.from({ length: 24 }, (_, i) => `${i}:00`)
    loadData = Array.from({ length: 24 }, () => Math.floor(800 + Math.random() * 1000))
    tempData = Array.from({ length: 24 }, () => parseFloat((60 + Math.random() * 25).toFixed(1)))
  } else if (chartPeriod.value === 'day') {
    xAxisData = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    loadData = [1200, 1350, 1280, 1450, 1580, 1350, 1120]
    tempData = [72, 75, 73, 78, 82, 76, 68]
  } else {
    xAxisData = ['Week 1', 'Week 2', 'Week 3', 'Week 4']
    loadData = [1250, 1380, 1320, 1450]
    tempData = [73, 76, 74, 79]
  }

  trendChart?.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Load (kW)', 'Top Oil Temp (°C)'] },
    xAxis: { type: 'category', data: xAxisData },
    yAxis: [{ type: 'value', name: 'Load (kW)' }, { type: 'value', name: 'Temperature (°C)' }],
    series: [
      {
        name: 'Load (kW)',
        type: 'line',
        data: loadData,
        smooth: true,
        lineStyle: { color: '#409EFF', width: 3 },
        areaStyle: { opacity: 0.1 }
      },
      {
        name: 'Top Oil Temp (°C)',
        type: 'line',
        data: tempData,
        smooth: true,
        lineStyle: { color: '#F56C6C', width: 3 },
        yAxisIndex: 1,
        markLine: { data: [{ yAxis: 95, name: 'Limit', lineStyle: { color: '#F56C6C', type: 'dashed' } }] }
      }
    ]
  })
}

const updateEfficiencyChart = () => {
  const loads = Array.from({ length: 20 }, (_, i) => (i + 1) * 125)
  const efficiencies = loads.map(l => {
    if (l < 500) return 96 + (l / 500) * 1.5
    if (l > 2000) return 98.5 - ((l - 2000) / 500) * 1.5
    return 97.5 + (l - 500) / 1500 * 1
  })

  efficiencyChart?.setOption({
    tooltip: { trigger: 'axis', formatter: 'Load: {c} kW<br>Efficiency: {c}%' },
    xAxis: { type: 'value', name: 'Load (kW)' },
    yAxis: { type: 'value', name: 'Efficiency (%)', min: 95, max: 99.5 },
    series: [{
      type: 'line',
      data: loads.map((load, idx) => [load, parseFloat(efficiencies[idx].toFixed(2))]),
      smooth: true,
      lineStyle: { color: '#67C23A', width: 3 },
      areaStyle: { opacity: 0.1, color: '#67C23A' },
      markPoint: {
        data: [{ type: 'max', name: 'Max Efficiency' }]
      }
    }]
  })
}

// ==================== Actions ====================
const refreshData = () => {
  generateMetrics()
  generateVoltageCurrent()
  generateGasData()
  healthScore.value = Math.floor(70 + Math.random() * 25)
  updateTrendChart()
  updateEfficiencyChart()
  ElMessage.success('Data refreshed')
}

const handleExport = () => {
  ElMessage.success('Report export started')
}

const acknowledgeAlarm = (alarm: Alarm) => {
  alarm.status = 'Acknowledged'
  ElMessage.success(`Alarm "${alarm.type}" acknowledged`)
}

const showMaintenanceHistory = () => {
  ElMessage.info('Maintenance history feature')
}

const scheduleTest = () => {
  ElMessage.info('Schedule test feature')
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
      generateMetrics()
      generateVoltageCurrent()
      generateGasData()
      initCharts()
    }, 400)
  }, 2000)
})

watch([trendChartRef, efficiencyChartRef], () => {
  window.addEventListener('resize', () => {
    trendChart?.resize()
    efficiencyChart?.resize()
  })
})
</script>

<style scoped>
/* Loading Screen */
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

.loading-dots { display: inline-flex; gap: 2px; }
.loading-dots span { animation: bounce 1.4s infinite ease-in-out both; }
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

.loading-tip { font-size: 13px; color: #94a3b8; letter-spacing: 1px; margin-bottom: 8px; font-weight: 500; }
.loading-subtip { font-size: 11px; color: #64748b; letter-spacing: 0.5px; animation: pulse 2s ease-in-out infinite; }

@keyframes pulse {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Main Container */
.transformer-container {
  padding: 20px;
  background: #f0f2f5;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  background: white;
  padding: 20px 24px;
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.page-header h2 {
  margin: 0 0 4px 0;
  font-size: 24px;
  font-weight: 600;
  color: #1f2f3d;
}

.header-subtitle {
  margin: 0;
  font-size: 13px;
  color: #909399;
}

.header-actions {
  display: flex;
  gap: 12px;
}

/* Info Cards */
.info-row {
  margin-bottom: 20px;
}

.info-card {
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
}

.info-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: rgba(64, 158, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #409EFF;
}

.info-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.info-value {
  font-size: 16px;
  font-weight: 600;
  color: #1f2f3d;
}

/* Metric Cards */
.metrics-row {
  margin-bottom: 20px;
}

.metric-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  display: flex;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  transition: all 0.3s ease;
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.1);
}

.metric-icon {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.metric-card.load .metric-icon { background: rgba(64, 158, 255, 0.1); color: #409EFF; }
.metric-card.temperature .metric-icon { background: rgba(245, 108, 108, 0.1); color: #F56C6C; }
.metric-card.efficiency .metric-icon { background: rgba(103, 194, 58, 0.1); color: #67C23A; }
.metric-card.aging .metric-icon { background: rgba(230, 162, 60, 0.1); color: #E6A23C; }

.metric-info {
  flex: 1;
}

.metric-label {
  font-size: 13px;
  color: #909399;
  margin-bottom: 4px;
}

.metric-value {
  font-size: 28px;
  font-weight: 700;
  color: #1f2f3d;
}

.metric-value .unit {
  font-size: 12px;
  font-weight: normal;
  color: #909399;
}

.metric-sub {
  font-size: 11px;
  color: #909399;
  margin-top: 6px;
}

/* Voltage Cards */
.voltage-row {
  margin-bottom: 20px;
}

.voltage-card {
  border-radius: 16px;
}

.phase-values {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.phase-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #f5f7fa;
  border-radius: 8px;
}

.phase-label {
  font-size: 13px;
  color: #606266;
  font-weight: 500;
}

.phase-value {
  font-size: 16px;
  font-weight: 600;
  color: #1f2f3d;
}

.phase-value .unit {
  font-size: 11px;
  font-weight: normal;
  color: #909399;
}

/* Monitoring Cards */
.monitoring-row {
  margin-bottom: 20px;
}

.temp-card, .gas-card, .status-card {
  border-radius: 16px;
}

.temp-grid {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.temp-item {
  text-align: center;
}

.temp-label {
  font-size: 13px;
  color: #909399;
  margin-bottom: 6px;
}

.temp-value {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 8px;
}

.temp-value.warning { color: #E6A23C; }
.temp-value.danger { color: #F56C6C; }

.gas-list {
  max-height: 300px;
  overflow-y: auto;
}

.gas-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 0;
  border-bottom: 1px solid #e4e7ed;
}

.gas-label {
  font-size: 12px;
  color: #606266;
  width: 100px;
}

.gas-value {
  font-size: 13px;
  font-weight: 500;
  width: 60px;
  text-align: right;
}

.gas-value.warning { color: #E6A23C; }
.gas-value.danger { color: #F56C6C; }

.gas-footer {
  margin-top: 16px;
  text-align: center;
}

.health-content {
  display: flex;
  gap: 20px;
  align-items: center;
}

.health-score {
  text-align: center;
}

.health-text {
  text-align: center;
}

.health-value {
  font-size: 24px;
  font-weight: 700;
  color: #1f2f3d;
}

.health-unit {
  font-size: 12px;
  color: #909399;
}

.health-status {
  margin-top: 8px;
}

.health-metrics {
  flex: 1;
}

.health-metric {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
  font-size: 13px;
  border-bottom: 1px solid #e4e7ed;
}

.health-metric span:first-child { color: #909399; }
.health-metric span:last-child { font-weight: 500; }
.health-metric span:last-child.normal { color: #67C23A; }
.health-metric span:last-child.warning { color: #E6A23C; }

.health-actions {
  margin-top: 16px;
  display: flex;
  gap: 12px;
  justify-content: center;
}

/* Charts */
.charts-row {
  margin-bottom: 20px;
}

.chart-card {
  border-radius: 16px;
}

.chart-container {
  width: 100%;
  height: 350px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* Alarms */
.alarms-card {
  border-radius: 16px;
}
</style>