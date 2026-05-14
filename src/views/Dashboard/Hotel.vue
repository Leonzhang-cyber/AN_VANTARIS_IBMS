<template>
  <div v-if="isBackgroundLoaded" class="dashboard">
    <div class="top-header">
      <div class="header-left">
        <div class="button-group">
          <!-- 节能模式 -->
          <div class="switch-item">
            <span class="switch-label">Energy Saving</span>
            <el-switch
                v-model="isEnergySavingActive"
                size="large"
                :active-value="true"
                :inactive-value="false"
                @change="handleEnergySavingToggle"
                class="energy-saving-switch"
                active-color="#10b981"
                inactive-color="#475569"
            />
          </div>

          <!-- 报告 -->
          <div class="switch-item">
            <span class="switch-label">Report</span>
            <el-switch
                v-model="showEnergyReport"
                size="large"
                :active-value="true"
                :inactive-value="false"
                :disabled="!isEnergySavingActive"
                class="report-switch"
                active-color="#3b82f6"
                inactive-color="#475569"
            />
          </div>
        </div>
      </div>
      <div class="header-title">
        <div class="main-title">HOTEL<br></div>
      </div>
      <div class="datetime" v-if="isFullscreen">{{ currentTime }}</div>
      <div class="datetimeview1" v-if="!isFullscreen"></div>
    </div>

    <div class="content-area">
      <div class="left-panel">

        <!-- 客房入住率统计 -->
        <div class="glass-card occupancy-card">
          <div class="card-title">🛏️ Room Occupancy</div>
          <div class="occupancy-grid">
            <div class="occupancy-item">
              <div class="occupancy-icon">🏨</div>
              <div class="occupancy-info">
                <span class="occupancy-label">Occupancy Rate</span>
                <span class="occupancy-value">{{ occupancyRate }}%</span>
                <span class="occupancy-sub">{{ occupiedRooms }}/{{ totalRooms }} rooms</span>
              </div>
            </div>
            <div class="occupancy-item">
              <div class="occupancy-icon">🧹</div>
              <div class="occupancy-info">
                <span class="occupancy-label">Cleaning</span>
                <span class="occupancy-value">{{ cleaningRooms }}</span>
                <span class="occupancy-sub">in progress</span>
              </div>
            </div>
            <div class="occupancy-item">
              <div class="occupancy-icon">🔧</div>
              <div class="occupancy-info">
                <span class="occupancy-label">Maintenance</span>
                <span class="occupancy-value">{{ maintenanceRooms }}</span>
                <span class="occupancy-sub">rooms</span>
              </div>
            </div>
            <div class="occupancy-item">
              <div class="occupancy-icon">📅</div>
              <div class="occupancy-info">
                <span class="occupancy-label">Check-ins Today</span>
                <span class="occupancy-value">{{ checkInsToday }}</span>
                <span class="occupancy-sub">arrivals</span>
              </div>
            </div>
          </div>
          <div class="occupancy-footer">
            <span>🚪 {{ checkOutsToday }} check-outs today</span>
            <span>⭐ {{ avgRating }} ★ guest rating</span>
          </div>
        </div>

        <!-- 酒店能耗 -->
        <div class="glass-card resources">
          <div class="card-title">❄️ Hotel Energy & Environment</div>
          <div class="resource-grid">
            <div class="resource-item">
              <el-progress type="circle" :percentage="waterPercent" :width="70" :stroke-width="7" color="#3b82f6" />
              <div class="resource-label">Water</div>
              <div class="resource-value">{{ waterUsage }} m³</div>
              <div class="resource-cost">💰 ${{ waterCost }}</div>
            </div>
            <div class="resource-item">
              <el-progress type="circle" :percentage="elecPercent" :width="70" :stroke-width="7" color="#f59e0b" />
              <div class="resource-label">Electricity</div>
              <div class="resource-value">{{ elecUsage }} kWh</div>
              <div class="resource-cost">💰 ${{ elecCost }}</div>
            </div>
            <div class="resource-item">
              <el-progress type="circle" :percentage="gasPercent" :width="70" :stroke-width="7" color="#10b981" />
              <div class="resource-label">Gas</div>
              <div class="resource-value">{{ gasUsage }} m³</div>
              <div class="resource-cost">💰 ${{ gasCost }}</div>
            </div>
          </div>
          <div style="height: 20px"></div>
          <div class="env-dashboard-grid">
            <div class="env-dashboard-row">
              <div class="env-item">
                <el-progress type="circle" :percentage="tempPercent" :width="65" :stroke-width="6" color="#f97316" />
                <div class="env-label">Temperature</div>
                <div class="env-value">{{ avgTemp }} ℃</div>
                <div class="env-status" :class="tempStatusClass">{{ tempStatus }}</div>
              </div>
              <div class="env-item">
                <el-progress type="circle" :percentage="humidityPercent" :width="65" :stroke-width="6" color="#06b6d4" />
                <div class="env-label">Humidity</div>
                <div class="env-value">{{ currentHumidity }} %</div>
                <div class="env-status" :class="humidityStatusClass">{{ humidityStatus }}</div>
              </div>
              <div class="env-item">
                <el-progress type="circle" :percentage="airQualityPercent" :width="65" :stroke-width="6" color="#a855f7" />
                <div class="env-label">Air Quality</div>
                <div class="env-value">{{ airQualityIndex }}</div>
                <div class="env-status" :class="airQualityClass">{{ airQualityStatus }}</div>
              </div>
            </div>
          </div>
          <div class="env-footer">
            <span>🌡️ Lobby: {{ lobbyTemp }}℃</span>
            <span>🏊 Pool: {{ poolTemp }}℃</span>
            <span>💨 CO₂: {{ currentCo2 }} ppm</span>
          </div>
        </div>

        <!-- 餐厅/酒吧营业状态 -->
        <div class="glass-card restaurant-card">
          <div class="card-title">🍽️ F&B Outlets</div>
          <div class="restaurant-list">
            <div v-for="outlet in outlets" :key="outlet.name" class="restaurant-row">
              <span class="restaurant-name">{{ outlet.name }}</span>
              <div class="restaurant-progress">
                <div class="restaurant-fill" :style="{ width: outlet.occupancy + '%', background: outlet.color }"></div>
              </div>
              <span class="restaurant-occupancy">{{ outlet.occupancy }}%</span>
            </div>
          </div>
          <div class="restaurant-footer">
            <span>🍳 {{ totalDiningGuests }} guests dining</span>
            <span>📊 Avg F&B rev: ¥{{ avgFbRevenue }}k</span>
          </div>
        </div>

      </div>

      <div class="center-void"></div>

      <div class="right-panel">

        <!-- 酒店人流/车流统计 -->
        <div class="glass-card traffic-card">
          <div class="card-title">👥🚗 Hotel Traffic</div>
          <div class="traffic-stats">
            <div class="traffic-row">
              <span class="traffic-label">🚶 In-House Guests</span>
              <span class="traffic-value">{{ inHouseGuests }}</span>
            </div>
            <div class="traffic-row">
              <span class="traffic-label">🚗 Parking Occupancy</span>
              <div class="parking-progress">
                <div class="parking-fill" :style="{ width: parkingOccupancy + '%' }"></div>
                <span class="parking-percent">{{ parkingOccupancy }}%</span>
              </div>
            </div>
            <div class="traffic-row">
              <span class="traffic-label">🚕 Valet Requests</span>
              <span class="traffic-value">{{ valetRequests }} today</span>
            </div>
            <div class="traffic-row">
              <span class="traffic-label">🛄 Luggage Storage</span>
              <span class="traffic-value">{{ luggageStorage }} items</span>
            </div>
          </div>
          <div class="traffic-footer">
            <span>📊 {{ totalDailyGuests }} daily guests</span>
            <span>🚌 {{ shuttleTrips }} shuttle trips</span>
          </div>
        </div>

        <!-- 员工值班状态 -->
        <div class="glass-card staff-card">
          <div class="card-title">👔 Staff On Duty</div>
          <div class="staff-grid">
            <div class="staff-item">
              <span class="staff-role">🛎️ Front Desk</span>
              <span class="staff-count">{{ frontDeskStaff }}</span>
            </div>
            <div class="staff-item">
              <span class="staff-role">🧹 Housekeeping</span>
              <span class="staff-count">{{ housekeepingStaff }}</span>
            </div>
            <div class="staff-item">
              <span class="staff-role">🍽️ F&B Service</span>
              <span class="staff-count">{{ fbStaff }}</span>
            </div>
            <div class="staff-item">
              <span class="staff-role">🔧 Maintenance</span>
              <span class="staff-count">{{ maintenanceStaff }}</span>
            </div>
            <div class="staff-item">
              <span class="staff-role">🛡️ Security</span>
              <span class="staff-count">{{ securityStaff }}</span>
            </div>
            <div class="staff-item">
              <span class="staff-role">🚗 Valet</span>
              <span class="staff-count">{{ valetStaff }}</span>
            </div>
          </div>
          <div class="staff-footer">
            <span>👥 Total: {{ totalStaffOnDuty }} on duty</span>
            <span>📞 {{ serviceRequests }} requests pending</span>
          </div>
        </div>

        <!-- 房源详细信息 -->
        <div class="glass-card room-details-card">
          <div class="card-title">🏠 Room Type Details</div>
          <div class="room-details-list">
            <div v-for="room in roomTypes" :key="room.type" class="room-detail-row" @click="toggleRoomDetail(room.type)">
              <div class="room-header">
                <div class="room-info">
                  <span class="room-icon">{{ room.icon }}</span>
                  <span class="room-name">{{ room.type }}</span>
                  <span class="room-badge" :class="room.badgeClass">{{ room.badge }}</span>
                </div>
                <span class="room-arrow">{{ room.expanded ? '▲' : '▼' }}</span>
              </div>
              <div class="room-summary">
                <span class="room-stats">🛏️ {{ room.available }}/{{ room.total }} available</span>
                <span class="room-price">¥{{ room.price }}/night</span>
              </div>
              <div v-if="room.expanded" class="room-detail-expanded">
                <div class="detail-row">
                  <span class="detail-label">📍 Location:</span>
                  <span class="detail-value">{{ room.location }}</span>
                </div>
                <div class="detail-row">
                  <span class="detail-label">🛌 Beds:</span>
                  <span class="detail-value">{{ room.beds }}</span>
                </div>
                <div class="detail-row">
                  <span class="detail-label">🚭 Smoking:</span>
                  <span class="detail-value" :class="room.smoking ? 'smoking-allowed' : 'non-smoking'">
                    {{ room.smoking ? '🚬 Allowed' : '🚭 Non-Smoking' }}
                  </span>
                </div>
                <div class="detail-row">
                  <span class="detail-label">📏 Size:</span>
                  <span class="detail-value">{{ room.size }} m²</span>
                </div>
                <div class="detail-row">
                  <span class="detail-label">🪟 View:</span>
                  <span class="detail-value">{{ room.view }}</span>
                </div>
                <div class="detail-row">
                  <span class="detail-label">✨ Amenities:</span>
                  <span class="detail-value amenities">{{ room.amenities }}</span>
                </div>
                <div class="detail-row">
                  <span class="detail-label">📊 Status:</span>
                  <span class="detail-value status-badge" :class="room.statusClass">{{ room.status }}</span>
                </div>
              </div>
            </div>
          </div>
          <div class="room-footer">
            <span>🏨 Total: {{ totalRoomCount }} rooms</span>
            <span>🟢 {{ totalAvailable }} available today</span>
          </div>
        </div>

      </div>
    </div>

    <!-- KPI 栏 -->
    <div class="glass-card kpi-strip">
      <div class="kpi-item">
        <span class="kpi-label">🛏️ Total Rooms</span>
        <span class="kpi-value">{{ totalRooms }}</span>
      </div>
      <div class="kpi-item">
        <span class="kpi-label">📶 IoT Online</span>
        <span class="kpi-value">{{ onlineRate }}%</span>
      </div>
      <div class="kpi-item">
        <span class="kpi-label">⭐ Guest Rating</span>
        <span class="kpi-value">{{ avgRating }}</span>
      </div>
      <div class="kpi-item">
        <span class="kpi-label">💰 Daily Revenue</span>
        <span class="kpi-value">¥{{ dailyRevenue }}k</span>
      </div>
      <div class="kpi-item">
        <span class="kpi-label">🌿 Saved Cost</span>
        <span class="kpi-value">${{ savedCostDisplay }}</span>
      </div>
      <div class="kpi-item">
        <span class="kpi-label">💵 Carbon Revenue</span>
        <span class="kpi-value">${{ carbonRevenueDisplay }}</span>
      </div>
    </div>

    <!-- Energy Savings Report Drawer - Hotel Edition -->
    <el-drawer
        v-model="showEnergyReport"
        direction="rtl"
        size="400px"
        :with-header="true"
        class="energy-report-drawer"
        :close-on-click-modal="true"
    >
      <template #header>
        <div class="drawer-header">
          <div class="drawer-title-section">
            <span class="drawer-icon">🏨</span>
            <div class="drawer-title-wrapper">
              <span class="drawer-title">Hotel Energy Savings Report</span>
            </div>
          </div>
          <div class="drawer-location-wrapper">
            <div class="drawer-location">
              <el-tag type="success" size="small" effect="plain" round style="margin-right: 10px">Live Data</el-tag>
              <el-icon><Location /></el-icon>
              <span>Singapore</span>
            </div>
          </div>
        </div>
      </template>
      <div class="report-content">
        <!-- Core Stats -->
        <div class="report-core-stats">
          <div class="core-stat-card">
            <div class="stat-icon">⚡</div>
            <div class="stat-info">
              <div class="stat-label">Total Energy Saved</div>
              <div class="stat-value">{{ hotelSavedEnergy }} kWh</div>
            </div>
          </div>
          <div class="core-stat-card">
            <div class="stat-icon">💰</div>
            <div class="stat-info">
              <div class="stat-label">Cost Saved</div>
              <div class="stat-value">${{ hotelSavedCost }}</div>
              <div class="stat-rate">@ $0.238/kWh</div>
            </div>
          </div>
        </div>

        <!-- Carbon & Revenue Section -->
        <div class="carbon-section">
          <div class="section-title">🌍 Carbon Reduction & Revenue</div>
          <div class="carbon-grid">
            <div class="carbon-item">
              <div class="carbon-icon">🏨</div>
              <div class="carbon-info">
                <div class="carbon-label">CO₂ Reduction</div>
                <div class="carbon-value">{{ hotelCarbonReduction }} kg</div>
                <div class="carbon-sub">≈ {{ hotelTreesOffset }} trees/year</div>
              </div>
            </div>
            <div class="carbon-item">
              <div class="carbon-icon">💵</div>
              <div class="carbon-info">
                <div class="carbon-label">Carbon Credit Revenue</div>
                <div class="carbon-value">${{ hotelCarbonRevenue }}</div>
                <div class="carbon-sub">@ $50/ton CO₂</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Annual Goal Progress -->
        <div class="goal-section">
          <div class="goal-header">
            <span>🎯 Annual Savings Target</span>
            <span class="goal-percent">{{ hotelSavingPercent }}%</span>
          </div>
          <el-progress :percentage="hotelSavingPercent" :stroke-width="10" color="#10b981" :show-text="false" />
          <div class="goal-detail">
            <span>Achieved: {{ hotelSavedEnergy }} / {{ hotelAnnualTarget }} kWh</span>
            <span>Remaining: {{ hotelRemainingTarget }} kWh</span>
          </div>
          <div class="goal-days-info">Continuous operation: {{ hotelContinuousDays }} days</div>
        </div>

        <!-- Monthly Trend Chart -->
        <div class="trend-chart">
          <div class="trend-header">📈 Monthly Savings Trend</div>
          <div ref="hotelReportChartRef" style="height: 200px; width: 100%"></div>
        </div>

        <!-- Hotel System Contribution Ranking -->
        <div class="ranking-section">
          <div class="ranking-header">🏆 Top Energy Saving Systems</div>
          <div class="ranking-list">
            <div v-for="(item, idx) in hotelDeviceRanking" :key="idx" class="ranking-item">
              <div class="ranking-rank" :class="{ 'top-three': idx < 3 }">{{ idx + 1 }}</div>
              <div class="ranking-name">{{ item.name }}</div>
              <div class="ranking-bar-wrap">
                <div class="ranking-bar" :style="{ width: item.percent + '%', background: idx < 3 ? '#10b981' : '#3b82f6' }"></div>
              </div>
              <div class="ranking-value">{{ item.saved }} kWh</div>
            </div>
          </div>
        </div>
      </div>
    </el-drawer>
  </div>

  <!-- Loading 页面 -->
  <div v-else class="loading-container">
    <div class="loading-overlay">
      <div class="loading-content">
        <div class="loading-spinner">
          <div class="spinner-ring"></div>
          <div class="spinner-ring"></div>
          <div class="spinner-ring"></div>
        </div>
        <div class="loading-text">
          <span class="loading-title">Loading</span>
          <span class="loading-dots">...</span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Initializing Hotel IBMS System</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'
import { Location } from '@element-plus/icons-vue'
import { useCounterStore } from '@/stores/counter.js'
import { getCurrentInstance } from 'vue'

const getStore = () => {
  const instance = getCurrentInstance()
  if (!instance) throw new Error('useStore() must be called within a setup function')
  const pinia = instance.appContext.config.globalProperties.$pinia
  if (!pinia) throw new Error('Pinia instance not found. Did you forget to call app.use(pinia)?')
  return useCounterStore(pinia)
}
const counterStore = getStore()
const isFullscreen = computed(() => counterStore.isFullscreen)

// ==================== 节能模式状态 ====================
const isEnergySavingActive = ref(true)
const showEnergyReport = ref(false)

// ==================== 酒店节能数据 ====================
let hotelSavingStartTime = null
let hotelBaselineHourlyConsumption = 0
let hotelActualConsumption = 0
let hotelLastTrackedElec = 0
const hotelStartSavedEnergy = 32500
const SGD_ELECTRICITY_RATE = 0.238
const CARBON_FACTOR = 0.4
const CARBON_CREDIT_PRICE_SGD = 50

const hotelSavedEnergy = ref(32500)
const hotelSavedCost = ref(7735.00)
const hotelCarbonReduction = ref(13000)
const hotelCarbonRevenue = ref(650.00)
const hotelSavingPercent = ref(6.50)
const hotelContinuousDays = ref(13)
const hotelAnnualTarget = ref(500000)

const savedCostDisplay = computed(() => hotelSavedCost.value.toFixed(2))
const carbonRevenueDisplay = computed(() => hotelCarbonRevenue.value.toFixed(2))

const hotelDeviceRanking = ref([
  { name: 'HVAC System', saved: 14250, percent: 44 },
  { name: 'Water Heating', saved: 9750, percent: 30 },
  { name: 'Lighting System', saved: 4880, percent: 15 },
  { name: 'Laundry System', saved: 2280, percent: 7 },
  { name: 'Other Systems', saved: 1340, percent: 4 }
])

const hotelRemainingTarget = computed(() => Math.max(0, Math.round(hotelAnnualTarget.value - hotelSavedEnergy.value)))
const hotelTreesOffset = computed(() => Math.round(hotelCarbonReduction.value / 22))

let hotelReportChart = null
const hotelReportChartRef = ref(null)

// ==================== 响应式数据 ====================
const currentTime = ref('')
const isBackgroundLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing assets...')

let timeTimer = null, dataInterval = null

const totalRooms = ref(328)
const occupiedRooms = ref(256)
const occupancyRate = ref(78.0)
const cleaningRooms = ref(18)
const maintenanceRooms = ref(6)
const checkInsToday = ref(124)
const checkOutsToday = ref(108)
const avgRating = ref(4.6)
const inHouseGuests = ref(412)

const onlineRate = ref(98.5)
const avgTemp = ref(23.5)
const currentHumidity = ref(52)
const currentCo2 = ref(420)
const lobbyTemp = ref(23.0)
const poolTemp = ref(28.5)
const waterUsage = ref(380)
const elecUsage = ref(18500)
const gasUsage = ref(1200)
const waterTarget = 500
const elecTarget = 25000
const gasTarget = 1800
const waterPercent = ref(76.0)
const elecPercent = ref(74.0)
const gasPercent = ref(66.7)
const waterCost = ref(0)
const elecCost = ref(0)
const gasCost = ref(0)

const tempPercent = ref(58)
const humidityPercent = ref(52)
const airQualityPercent = ref(85)
const airQualityIndex = ref(85)
const airQualityStatus = ref('Good')
const airQualityClass = ref('status-ideal')
const tempStatus = ref('Normal')
const tempStatusClass = ref('status-normal')
const humidityStatus = ref('Normal')
const humidityStatusClass = ref('status-normal')

const outlets = ref([
  { name: 'Main Restaurant', occupancy: 68, color: '#f59e0b' },
  { name: 'Lobby Bar', occupancy: 45, color: '#3b82f6' },
  { name: 'Chinese Cuisine', occupancy: 72, color: '#ef4444' },
  { name: 'Sky Lounge', occupancy: 38, color: '#10b981' },
  { name: 'Coffee Shop', occupancy: 52, color: '#8b5cf6' }
])
const totalDiningGuests = ref(186)
const avgFbRevenue = ref(28.5)

const parkingOccupancy = ref(68)
const valetRequests = ref(86)
const luggageStorage = ref(42)
const totalDailyGuests = ref(856)
const shuttleTrips = ref(24)

const frontDeskStaff = ref(12)
const housekeepingStaff = ref(28)
const fbStaff = ref(35)
const maintenanceStaff = ref(8)
const securityStaff = ref(10)
const valetStaff = ref(6)
const totalStaffOnDuty = ref(99)
const serviceRequests = ref(7)

const dailyRevenue = ref(186.5)

const roomTypes = ref([
  { type: 'Standard King', icon: '🛌', badge: 'Most Popular', badgeClass: 'badge-popular', total: 85, available: 23, price: 188, location: 'Tower A, Floors 8-15', beds: '1 King Bed (180cm)', smoking: false, size: 35, view: 'City View', amenities: 'WiFi, TV, Minibar, AC, Safe', status: 'Available', statusClass: 'status-available', expanded: false },
  { type: 'Deluxe Twin', icon: '🛌🛌', badge: 'Family Choice', badgeClass: 'badge-family', total: 62, available: 15, price: 228, location: 'Tower A, Floors 16-22', beds: '2 Twin Beds (120cm each)', smoking: true, size: 42, view: 'Park View', amenities: 'WiFi, TV, Minibar, AC, Bathtub, Coffee Machine', status: 'Available', statusClass: 'status-available', expanded: false },
  { type: 'Executive Suite', icon: '👑', badge: 'VIP', badgeClass: 'badge-vip', total: 28, available: 6, price: 458, location: 'Tower B, Floors 20-25', beds: '1 King Bed + Sofa Bed', smoking: false, size: 68, view: 'Panoramic Ocean View', amenities: 'WiFi, 65" TV, Minibar, Bathtub, Lounge Access, Butler Service', status: 'Limited', statusClass: 'status-limited', expanded: false },
  { type: 'Family Suite', icon: '👨‍👩‍👧', badge: 'Hot Deal', badgeClass: 'badge-hot', total: 42, available: 8, price: 388, location: 'Tower B, Floors 10-18', beds: '1 King + 2 Twin Beds', smoking: false, size: 75, view: 'Mountain View', amenities: 'WiFi, TV, Kitchenette, Bathtub, Kids Play Area', status: 'Available', statusClass: 'status-available', expanded: false },
  { type: 'Presidential Suite', icon: '✨', badge: 'Luxury', badgeClass: 'badge-luxury', total: 8, available: 1, price: 1288, location: 'Tower B, Floors 26-28', beds: '1 King Bed + 2 Twin + Study', smoking: false, size: 180, view: '360° Panoramic View', amenities: 'Private Pool, Gym, Kitchen, Piano, 24h Butler, Limo Service', status: 'Limited', statusClass: 'status-limited', expanded: false },
  { type: 'Accessible Room', icon: '♿', badge: 'ADA Compliant', badgeClass: 'badge-ada', total: 18, available: 5, price: 198, location: 'Tower A, Floors 3-5', beds: '1 King Bed (accessible)', smoking: false, size: 42, view: 'Garden View', amenities: 'Wide Doorways, Roll-in Shower, Grab Bars, Emergency Call', status: 'Available', statusClass: 'status-available', expanded: false }
])

const totalRoomCount = computed(() => roomTypes.value.reduce((sum, room) => sum + room.total, 0))
const totalAvailable = computed(() => roomTypes.value.reduce((sum, room) => sum + room.available, 0))

// ==================== 节能模式逻辑 ====================
function handleEnergySavingToggle(val) {
  if (val) {
    startHotelEnergySavingModel()
    ElMessage.success({ message: '🏨 Hotel energy saving mode activated', duration: 2000, type: 'success' })
  } else {
    stopHotelEnergySavingModel()
    showEnergyReport.value = false
    ElMessage.info({ message: 'Hotel energy saving mode deactivated', duration: 2000, type: 'info' })
  }
}

function startHotelEnergySavingModel() {
  hotelBaselineHourlyConsumption = elecUsage.value + gasUsage.value * 10 + waterUsage.value * 5
  hotelSavingStartTime = Date.now()
  hotelActualConsumption = 0
  hotelLastTrackedElec = elecUsage.value + gasUsage.value * 10 + waterUsage.value * 5
  window._hotelEnergySavingBoost = 0.83

  hotelSavedEnergy.value = hotelStartSavedEnergy
  hotelSavedCost.value = parseFloat((hotelStartSavedEnergy * SGD_ELECTRICITY_RATE).toFixed(2))
  hotelCarbonReduction.value = Math.round(hotelStartSavedEnergy * CARBON_FACTOR)
  hotelCarbonRevenue.value = parseFloat(((hotelCarbonReduction.value / 1000) * CARBON_CREDIT_PRICE_SGD).toFixed(2))

  const dailyAvgSaving = hotelStartSavedEnergy / hotelContinuousDays.value
  hotelAnnualTarget.value = Math.round(dailyAvgSaving * 360)
  hotelSavingPercent.value = Math.min(100, Math.round((hotelStartSavedEnergy / hotelAnnualTarget.value) * 100 * 10) / 10)
}

function stopHotelEnergySavingModel() {
  hotelSavingStartTime = null
  window._hotelEnergySavingBoost = null
  hotelActualConsumption = 0
  hotelLastTrackedElec = 0
  hotelSavedEnergy.value = 0; hotelSavedCost.value = 0
  hotelCarbonReduction.value = 0; hotelCarbonRevenue.value = 0
  hotelSavingPercent.value = 0; hotelContinuousDays.value = 0; hotelAnnualTarget.value = 0
}

function updateHotelEnergySavings() {
  if (!isEnergySavingActive.value || !hotelSavingStartTime) return
  const hoursElapsed = (Date.now() - hotelSavingStartTime) / (1000 * 60 * 60)
  const baselineTotal = hotelBaselineHourlyConsumption * hoursElapsed
  const actualTotal = hotelActualConsumption || 0
  hotelContinuousDays.value = Math.max(hotelContinuousDays.value, Math.floor(hoursElapsed / 24) + 13)
  const newSavedEnergy = hotelStartSavedEnergy + Math.max(0, baselineTotal - actualTotal)
  hotelSavedEnergy.value = Math.round(newSavedEnergy * 10) / 10
  hotelSavedCost.value = parseFloat((hotelSavedEnergy.value * SGD_ELECTRICITY_RATE).toFixed(2))
  hotelCarbonReduction.value = Math.round(hotelSavedEnergy.value * CARBON_FACTOR * 10) / 10
  hotelCarbonRevenue.value = parseFloat(((hotelCarbonReduction.value / 1000) * CARBON_CREDIT_PRICE_SGD).toFixed(2))
  const dailyAvgSaving = hotelSavedEnergy.value / hotelContinuousDays.value
  hotelAnnualTarget.value = Math.round(dailyAvgSaving * 360)
  hotelSavingPercent.value = Math.min(100, Math.round((hotelSavedEnergy.value / hotelAnnualTarget.value) * 100 * 10) / 10)
}

function trackHotelEnergyConsumption() {
  if (!isEnergySavingActive.value || !hotelSavingStartTime) return
  const currentTotal = elecUsage.value + gasUsage.value * 10 + waterUsage.value * 5
  if (hotelLastTrackedElec === 0) { hotelLastTrackedElec = currentTotal; hotelActualConsumption = 0; return }
  const delta = Math.max(0, currentTotal - hotelLastTrackedElec)
  if (delta > 0) hotelActualConsumption += delta
  hotelLastTrackedElec = currentTotal
}

function initHotelReportChart() {
  if (hotelReportChartRef.value) {
    if (hotelReportChart) hotelReportChart.dispose()
    hotelReportChart = echarts.init(hotelReportChartRef.value)
    const currentWeekSaving = Math.max(0, Math.round(hotelSavedEnergy.value - hotelStartSavedEnergy))
    hotelReportChart.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      grid: { top: 20, left: 45, right: 10, bottom: 20 },
      xAxis: { type: 'category', data: ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'This Week'], axisLabel: { color: '#94a3b8', fontSize: 10 } },
      yAxis: { type: 'value', name: 'Saved Energy (kWh)', nameTextStyle: { color: '#94a3b8', fontSize: 10 }, axisLabel: { color: '#94a3b8' } },
      series: [{ type: 'bar', data: [5480, 7820, 9650, 11200, currentWeekSaving > 0 ? currentWeekSaving : 1680], itemStyle: { borderRadius: [8, 8, 0, 0], color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: '#10b981' }, { offset: 1, color: '#34d399' }] } }, label: { show: true, position: 'top', color: '#94a3b8', fontSize: 10 } }]
    })
  }
}

watch(showEnergyReport, (newVal) => {
  if (newVal) { nextTick(() => { initHotelReportChart() }) }
  else if (hotelReportChart) { hotelReportChart.dispose(); hotelReportChart = null }
})

// ==================== 辅助函数 ====================
function toggleRoomDetail(type) { const room = roomTypes.value.find(r => r.type === type); if (room) room.expanded = !room.expanded }

function randomVariation(base, range = 0.08) { const change = base * (Math.random() - 0.5) * range * 2; return Math.max(0, base + change) }

function updateCosts() { waterCost.value = (waterUsage.value * 0.8).toFixed(1); elecCost.value = (elecUsage.value * 0.12).toFixed(1); gasCost.value = (gasUsage.value * 0.45).toFixed(1) }

function updateEnvironmentStatus() {
  if (avgTemp.value < 20) { tempStatus.value = 'Too Cold'; tempStatusClass.value = 'status-warning' } else if (avgTemp.value > 26) { tempStatus.value = 'Too Hot'; tempStatusClass.value = 'status-warning' } else if (avgTemp.value >= 22 && avgTemp.value <= 24) { tempStatus.value = 'Ideal'; tempStatusClass.value = 'status-ideal' } else { tempStatus.value = 'Normal'; tempStatusClass.value = 'status-normal' }
  tempPercent.value = parseFloat(Math.min(95, Math.max(5, 50 + (avgTemp.value - 22) * 25)).toFixed(1))
  if (currentHumidity.value < 35) { humidityStatus.value = 'Too Dry'; humidityStatusClass.value = 'status-warning' } else if (currentHumidity.value > 65) { humidityStatus.value = 'Too Humid'; humidityStatusClass.value = 'status-warning' } else if (currentHumidity.value >= 45 && currentHumidity.value <= 55) { humidityStatus.value = 'Ideal'; humidityStatusClass.value = 'status-ideal' } else { humidityStatus.value = 'Normal'; humidityStatusClass.value = 'status-normal' }
  humidityPercent.value = parseFloat(currentHumidity.value.toFixed(1))
  airQualityIndex.value = Math.floor(50 + Math.random() * 40)
  if (airQualityIndex.value >= 80) { airQualityStatus.value = 'Excellent'; airQualityClass.value = 'status-ideal' } else if (airQualityIndex.value >= 60) { airQualityStatus.value = 'Good'; airQualityClass.value = 'status-normal' } else { airQualityStatus.value = 'Moderate'; airQualityClass.value = 'status-moderate' }
  airQualityPercent.value = airQualityIndex.value
}

function updateRoomDetails() {
  roomTypes.value.forEach(room => {
    let variation = (Math.random() - 0.5) * 0.15
    let newAvailable = Math.floor(room.total * (room.available / room.total + variation))
    newAvailable = Math.min(room.total, Math.max(0, newAvailable))
    room.available = newAvailable
    const availableRate = (room.available / room.total) * 100
    if (availableRate <= 10) { room.status = 'Almost Full'; room.statusClass = 'status-warning' } else if (availableRate <= 30) { room.status = 'Limited'; room.statusClass = 'status-limited' } else { room.status = 'Available'; room.statusClass = 'status-available' }
    let priceVariation = (Math.random() - 0.5) * 0.08
    room.price = Math.floor(Math.max(room.price * 0.9, Math.min(room.price * 1.15, room.price * (1 + priceVariation))))
  })
}

function updateOccupancyData() { occupiedRooms.value = Math.floor(randomVariation(256, 0.06)); occupancyRate.value = parseFloat(((occupiedRooms.value / totalRooms.value) * 100).toFixed(1)); cleaningRooms.value = Math.floor(randomVariation(18, 0.15)); maintenanceRooms.value = Math.floor(randomVariation(6, 0.2)); checkInsToday.value = Math.floor(randomVariation(124, 0.1)); checkOutsToday.value = Math.floor(randomVariation(108, 0.1)); inHouseGuests.value = Math.floor(occupiedRooms.value * 1.6); avgRating.value = parseFloat((4.2 + Math.random() * 0.8).toFixed(1)) }

function updateOutletData() { outlets.value.forEach(outlet => { let variation = (Math.random() - 0.5) * 0.15; let newOcc = outlet.occupancy * (1 + variation); newOcc = Math.min(95, Math.max(15, newOcc)); outlet.occupancy = Math.floor(newOcc); if (outlet.occupancy >= 70) outlet.color = '#ef4444'; else if (outlet.occupancy >= 50) outlet.color = '#f59e0b'; else if (outlet.occupancy >= 30) outlet.color = '#3b82f6'; else outlet.color = '#10b981' }); totalDiningGuests.value = Math.floor(randomVariation(186, 0.1)); avgFbRevenue.value = parseFloat(randomVariation(28.5, 0.08).toFixed(1)) }

function updateTrafficData() { parkingOccupancy.value = Math.floor(randomVariation(68, 0.1)); valetRequests.value = Math.floor(randomVariation(86, 0.12)); luggageStorage.value = Math.floor(randomVariation(42, 0.1)); totalDailyGuests.value = Math.floor(randomVariation(856, 0.06)); shuttleTrips.value = Math.floor(randomVariation(24, 0.1)) }

function updateStaffData() { frontDeskStaff.value = Math.floor(randomVariation(12, 0.1)); housekeepingStaff.value = Math.floor(randomVariation(28, 0.08)); fbStaff.value = Math.floor(randomVariation(35, 0.1)); maintenanceStaff.value = Math.floor(randomVariation(8, 0.12)); securityStaff.value = Math.floor(randomVariation(10, 0.08)); valetStaff.value = Math.floor(randomVariation(6, 0.1)); totalStaffOnDuty.value = frontDeskStaff.value + housekeepingStaff.value + fbStaff.value + maintenanceStaff.value + securityStaff.value + valetStaff.value; serviceRequests.value = Math.floor(randomVariation(7, 0.2)) }

function updateEnergyData() { waterUsage.value = Math.floor(randomVariation(380, 0.08)); waterPercent.value = parseFloat(((waterUsage.value / waterTarget) * 100).toFixed(1)); elecUsage.value = Math.floor(randomVariation(18500, 0.06)); elecPercent.value = parseFloat(((elecUsage.value / elecTarget) * 100).toFixed(1)); gasUsage.value = Math.floor(randomVariation(1200, 0.07)); gasPercent.value = parseFloat(((gasUsage.value / gasTarget) * 100).toFixed(1)); updateCosts() }

function updateEnvironmentData() { avgTemp.value = parseFloat((22 + Math.random() * 3).toFixed(1)); currentHumidity.value = Math.floor(45 + Math.random() * 20); currentCo2.value = Math.floor(400 + Math.random() * 100); lobbyTemp.value = parseFloat((22.5 + Math.random() * 1.5).toFixed(1)); poolTemp.value = parseFloat((27 + Math.random() * 2).toFixed(1)); onlineRate.value = parseFloat((97 + Math.random() * 2.5).toFixed(1)); dailyRevenue.value = parseFloat((160 + Math.random() * 50).toFixed(1)) }

function refreshData() {
  updateEnergyData(); updateOccupancyData(); updateOutletData(); updateTrafficData(); updateStaffData(); updateEnvironmentData(); updateEnvironmentStatus(); updateRoomDetails()
  if (isEnergySavingActive.value) { trackHotelEnergyConsumption(); updateHotelEnergySavings() }
}

const loadingMessages = ['Preparing assets...', 'Loading background...', 'Initializing modules...', 'Establishing connection...', 'Starting dashboard...']

const preloadBackground = () => new Promise((resolve) => {
  const img = new Image(); img.src = 'https://aegisnx.com/wp-content/uploads/2026/05/1778552359468.png'
  let progress = 0, msgIdx = 0
  const msgInterval = setInterval(() => { if (msgIdx < loadingMessages.length - 1) loadingMessage.value = loadingMessages[++msgIdx] }, 800)
  const progInterval = setInterval(() => { if (progress < 90) loadingProgress.value = Math.min(progress += Math.random() * 10, 90) }, 100)
  img.onload = () => { clearInterval(msgInterval); clearInterval(progInterval); loadingMessage.value = 'Ready!'; loadingProgress.value = 100; setTimeout(resolve, 500) }
  img.onerror = () => { clearInterval(msgInterval); clearInterval(progInterval); loadingProgress.value = 100; setTimeout(resolve, 300) }
})

const updateTime = () => {
  const now = new Date()
  const utc = now.getTime() + (now.getTimezoneOffset() * 60000)
  const sgTime = new Date(utc + (8 * 3600000))
  currentTime.value = `${sgTime.getFullYear()}-${String(sgTime.getMonth() + 1).padStart(2, '0')}-${String(sgTime.getDate()).padStart(2, '0')} ${String(sgTime.getHours()).padStart(2, '0')}:${String(sgTime.getMinutes()).padStart(2, '0')}:${String(sgTime.getSeconds()).padStart(2, '0')}.${String(sgTime.getMilliseconds()).padStart(3, '0')} SGT`
}

function resizeCharts() { if (hotelReportChart) hotelReportChart.resize() }

onMounted(async () => {
  updateTime(); timeTimer = setInterval(updateTime, 1000)
  await preloadBackground(); isBackgroundLoaded.value = true; await nextTick()
  setTimeout(() => { refreshData(); if (isEnergySavingActive.value) startHotelEnergySavingModel(); dataInterval = setInterval(refreshData, 5000) }, 100)
  window.addEventListener('resize', resizeCharts)
})

onBeforeUnmount(() => { clearInterval(timeTimer); clearInterval(dataInterval); window.removeEventListener('resize', resizeCharts); if (hotelReportChart) hotelReportChart.dispose() })
</script>

<style scoped>
/* Loading 样式 */
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
.progress-bar { height: 100%; background: linear-gradient(90deg, #3b82f6, #8b5cf6, #ec489a); transition: width 0.3s; background-size: 200% auto; animation: shimmer 2s linear infinite; }
@keyframes shimmer { 0% { background-position: 0% 0%; } 100% { background-position: 200% 0%; } }
.loading-tip { font-size: 13px; color: #94a3b8; margin-bottom: 8px; }
.loading-subtip { font-size: 11px; color: #64748b; animation: pulse 2s infinite; }
@keyframes pulse { 0%,100% { opacity: 0.6; } 50% { opacity: 1; } }
@keyframes fadeInUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

/* 主页面 */
.dashboard { height: 100%; width: 100%; display: flex; flex-direction: column; background-image: url('https://aegisnx.com/wp-content/uploads/2026/05/1778552359468.png'); background-size: cover; background-position: center; background-attachment: fixed; animation: fadeIn 0.5s; font-family: 'Inter', 'Segoe UI', system-ui, sans-serif; }
.top-header { display: flex; justify-content: space-between; align-items: center; padding: 20px 28px 8px; margin: 0 24px; }
.header-left { width: auto; display: flex; align-items: center; }
.header-title { text-align: center; flex: 1; }
.main-title { font-size: 44px; font-weight: 800; background: linear-gradient(135deg, #e0f2fe, #bae6fd); -webkit-background-clip: text; background-clip: text; color: transparent; letter-spacing: 3px; text-shadow: 0 0 30px rgba(96,165,250,0.5); }
.datetime { font-size: 15px; color: #a5f3fc; font-weight: 600; background: transparent; backdrop-filter: blur(8px); padding: 8px 20px; border-radius: 12px; min-width: 280px; text-align: center; font-family: monospace; border: 1px solid rgba(165,243,252,0.3); text-shadow: 0 0 5px #a5f3fc; }
.kpi-strip { display: flex; justify-content: space-around; gap: 20px; margin: 10px 24px 20px; padding: 12px 20px; flex-wrap: wrap; }
.kpi-item { display: flex; gap: 12px; align-items: baseline; font-size: 15px; }
.kpi-label { color: #ffffff; font-weight: 500; }
.kpi-value { font-size: 24px; font-weight: 800; color: #facc15; font-family: monospace; text-shadow: 0 0 5px rgba(250,204,21,0.5); }
.content-area { flex: 1; display: flex; padding: 0 24px 24px; gap: 32px; overflow-y: auto; }
.left-panel { width: 340px; flex-shrink: 0; }
.right-panel { width: 420px; flex-shrink: 0; }
.center-void { flex: 1; }

/* 开关组 */
.button-group { display: flex; align-items: center; justify-content: center;gap: 10px }
.switch-item { display: flex; align-items: center; gap: 5px; }
.switch-label { font-size: 14px; font-weight: 600; color: #fff; white-space: nowrap; font-weight: bold; }
.energy-saving-switch { --el-switch-on-color: #10b981; --el-switch-off-color: #475569; }
.report-switch { --el-switch-on-color: #3b82f6; --el-switch-off-color: #475569; }
:deep(.el-switch__label) { display: none !important; }

.glass-card { background: transparent; border-radius: 28px; border: 1px solid rgba(59,130,246,0.4); box-shadow: 0 20px 35px -12px rgba(0,0,0,0.6); padding: 16px; transition: all 0.3s; margin-bottom: 20px; }
.glass-card:hover { background: rgba(8,16,28,0.5); backdrop-filter: blur(8px); transform: translateY(-3px); border-color: rgba(59,130,246,0.6); }
.card-title { font-size: 16px; font-weight: 800; color: #f0f9ff; margin-bottom: 12px; padding-left: 10px; border-left: 4px solid #3b82f6; text-shadow: 0 0 4px rgba(59,130,246,0.5); }

.occupancy-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.occupancy-item { display: flex; align-items: center; gap: 10px; background: rgba(255,255,255,0.05); border-radius: 12px; padding: 0px; }
.occupancy-icon { font-size: 28px; }
.occupancy-info { display: flex; flex-direction: column; }
.occupancy-label { font-size: 14px; color: #343e4c; font-weight: bold; }
.occupancy-value { font-size: 22px; font-weight: 800; color: #facc15; line-height: 1.2; }
.occupancy-sub { font-size: 10px; color: #64748b; }
.occupancy-footer { display: flex; justify-content: space-between; margin-top: 12px; padding-top: 10px; border-top: 1px solid rgba(59,130,246,0.35); font-size: 11px; font-weight: 600; color: #94a3b8; }

.resource-grid { display: flex; justify-content: space-around; text-align: center; }
.resource-item .resource-label { margin-top: 8px; font-size: 11px; font-weight: 600; color: #cbd5e1; }
.resource-value { font-size: 12px; font-weight: 800; color: #facc15; }
.resource-cost { font-size: 10px; font-weight: 600; color: #a5f3fc; margin-top: 4px; }

.restaurant-list { display: flex; flex-direction: column; gap: 10px; }
.restaurant-row { display: flex; align-items: center; gap: 10px; padding: 6px 0; }
.restaurant-name { width: 105px; font-size: 12px; font-weight: 600; color: #cbd5e1; }
.restaurant-progress { flex: 1; height: 6px; background: rgba(255,255,255,0.1); border-radius: 3px; overflow: hidden; }
.restaurant-fill { height: 100%; border-radius: 3px; transition: width 0.3s; }
.restaurant-occupancy { width: 40px; font-size: 11px; font-weight: 700; color: #facc15; text-align: right; }
.restaurant-footer { display: flex; justify-content: space-between; margin-top: 10px; padding-top: 8px; border-top: 1px solid rgba(59,130,246,0.35); font-size: 11px; font-weight: 600; color: #94a3b8; }

.traffic-stats { display: flex; flex-direction: column; gap: 12px; }
.traffic-row { display: flex; justify-content: space-between; align-items: center; padding: 6px 0; border-bottom: 1px solid rgba(255,255,255,0.05); }
.traffic-label { font-size: 12px; font-weight: 600; color: #cbd5e1; }
.traffic-value { font-size: 18px; font-weight: 800; color: #facc15; font-family: monospace; }
.parking-progress { display: flex; align-items: center; gap: 10px; width: 150px; }
.parking-fill { height: 6px; background: linear-gradient(90deg, #f59e0b, #ef4444); border-radius: 3px; transition: width 0.3s; flex: 1; }
.parking-percent { font-size: 12px; font-weight: 700; color: #f59e0b; width: 40px; text-align: right; }
.traffic-footer { display: flex; justify-content: space-between; margin-top: 10px; padding-top: 8px; border-top: 1px solid rgba(59,130,246,0.35); font-size: 11px; font-weight: 600; color: #94a3b8; }

.env-dashboard-grid { display: flex; flex-direction: column; gap: 12px; }
.env-dashboard-row { display: flex; justify-content: space-around; text-align: center; }
.env-item { text-align: center; }
.env-label { margin-top: 6px; font-size: 10px; font-weight: 600; color: #cbd5e1; }
.env-value { font-size: 13px; font-weight: 800; color: #facc15; font-family: monospace; }
.env-status { font-size: 9px; font-weight: 700; margin-top: 4px; padding: 2px 6px; border-radius: 12px; display: inline-block; }
.status-ideal { background: rgba(16,185,129,0.2); color: #34d399; }
.status-normal { background: rgba(59,130,246,0.2); color: #60a5fa; }
.status-warning { background: rgba(239,68,68,0.2); color: #f87171; }
.status-moderate { background: rgba(245,158,11,0.2); color: #fbbf24; }
.env-footer { display: flex; justify-content: space-between; margin-top: 12px; padding-top: 8px; border-top: 1px solid rgba(59,130,246,0.35); font-size: 10px; font-weight: 600; color: #94a3b8; }

.staff-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.staff-item { display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.05); }
.staff-role { font-size: 11px; font-weight: 600; color: #cbd5e1; }
.staff-count { font-size: 16px; font-weight: 800; color: #facc15; font-family: monospace; }
.staff-footer { display: flex; justify-content: space-between; margin-top: 10px; padding-top: 8px; border-top: 1px solid rgba(59,130,246,0.35); font-size: 11px; font-weight: 600; color: #94a3b8; }

.room-details-list { display: flex; flex-direction: column; gap: 8px; max-height: 350px; overflow-y: auto; padding-right: 4px; }
.room-details-list::-webkit-scrollbar { width: 3px; }
.room-detail-row { background: rgba(255,255,255,0.04); border-radius: 12px; padding: 10px; cursor: pointer; transition: all 0.2s; }
.room-detail-row:hover { background: rgba(59,130,246,0.15); }
.room-header { display: flex; justify-content: space-between; align-items: center; }
.room-info { display: flex; align-items: center; gap: 8px; }
.room-icon { font-size: 20px; }
.room-name { font-size: 14px; font-weight: 700; color: #e2e8f0; }
.room-badge { font-size: 9px; font-weight: 700; padding: 2px 8px; border-radius: 12px; }
.badge-popular { background: linear-gradient(135deg, #f59e0b, #d97706); color: #1e293b; }
.badge-family { background: linear-gradient(135deg, #10b981, #059669); color: #fff; }
.badge-vip { background: linear-gradient(135deg, #8b5cf6, #6d28d9); color: #fff; }
.badge-hot { background: linear-gradient(135deg, #ef4444, #dc2626); color: #fff; }
.badge-luxury { background: linear-gradient(135deg, #fbbf24, #f59e0b); color: #1e293b; }
.badge-ada { background: linear-gradient(135deg, #06b6d4, #0891b2); color: #fff; }
.room-arrow { font-size: 12px; color: #94a3b8; }
.room-summary { display: flex; justify-content: space-between; margin-top: 8px; padding-top: 6px; border-top: 1px solid rgba(255,255,255,0.05); }
.room-stats { font-size: 11px; font-weight: 600; color: #94a3b8; }
.room-price { font-size: 13px; font-weight: 800; color: #facc15; }
.room-detail-expanded { margin-top: 10px; padding-top: 8px; border-top: 1px solid rgba(59,130,246,0.3); }
.detail-row { display: flex; padding: 4px 0; font-size: 11px; }
.detail-label { width: 75px; font-weight: 600; color: #64748b; }
.detail-value { flex: 1; color: #cbd5e1; }
.detail-value.amenities { font-size: 10px; color: #94a3b8; }
.smoking-allowed { color: #f59e0b; }
.non-smoking { color: #10b981; }
.status-badge { padding: 2px 8px; border-radius: 12px; display: inline-block; font-size: 10px; font-weight: 700; width: auto; }
.status-available { background: rgba(16,185,129,0.2); color: #34d399; }
.status-limited { background: rgba(245,158,11,0.2); color: #fbbf24; }
.room-footer { display: flex; justify-content: space-between; margin-top: 12px; padding-top: 10px; border-top: 1px solid rgba(59,130,246,0.35); font-size: 11px; font-weight: 600; color: #94a3b8; }

.content-area::-webkit-scrollbar { width: 5px; }
.content-area::-webkit-scrollbar-track { background: rgba(15,23,42,0.5); border-radius: 4px; }
.content-area::-webkit-scrollbar-thumb { background: #3b82f6; border-radius: 4px; }
:deep(.el-progress-circle__track) { stroke: rgba(255,255,255,0.2); }
:deep(.el-progress__text) { color: #fff !important; font-weight: 700 !important; font-size: 12px !important; }

/* Drawer 样式 */
.energy-report-drawer :deep(.el-drawer__header) { margin-bottom: 0; padding: 16px 20px; border-bottom: 1px solid rgba(16, 185, 129, 0.2); background: rgba(8, 16, 28, 0.95); }
.energy-report-drawer :deep(.el-drawer__body) { padding: 0; background: linear-gradient(180deg, #0f172a 0%, #0a0f1a 100%); overflow: hidden; scrollbar-width: none; }
.drawer-header { display: flex; flex-direction: column; width: 100%; flex-wrap: wrap; gap: 12px; }
.drawer-title-section { display: flex; align-items: center; gap: 10px; }
.drawer-title-wrapper { display: flex; flex-direction: column; gap: 4px; }
.drawer-title-wrapper .drawer-title { font-size: 18px; font-weight: 700; color: green; letter-spacing: 1px; }
.drawer-location-wrapper { text-align: right; }
.drawer-location { display: flex; align-items: center; gap: 4px; font-size: 15px; color: #94a3b8; font-weight: bold; }
.drawer-icon { font-size: 22px; }
.report-content { padding: 0px; display: flex; flex-direction: column; gap: 20px; max-height: calc(100vh - 70px); overflow-y: auto; }
.report-content::-webkit-scrollbar { width: 4px; display: none; }

.report-core-stats { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.core-stat-card { background: rgba(16, 185, 129, 0.08); border-radius: 20px; padding: 6px; display: flex; align-items: center; gap: 12px; border: 1px solid rgba(16, 185, 129, 0.2); }
.stat-icon { font-size: 32px; }
.stat-info { flex: 1; }
.stat-label { font-size: 11px; color: #94a3b8; display: block; margin-bottom: 4px; font-weight: bold; }
.stat-value { font-size: 22px; font-weight: 800; color: #facc15; font-family: monospace; }
.stat-rate { font-size: 11px; color: green; margin-top: 4px; font-weight: bold; }

.carbon-section { background: rgba(16, 185, 129, 0.08); border-radius: 20px; padding: 14px 16px; border: 1px solid rgba(59, 130, 246, 0.2); }
.section-title { font-size: 14px; color: #94a3b8; font-weight: bold; margin-bottom: 12px; }
.carbon-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.carbon-item { display: flex; align-items: center; gap: 10px; background: rgba(16, 185, 129, 0.08); border-radius: 16px; padding: 5px; }
.carbon-icon { font-size: 24px; }
.carbon-info { flex: 1; }
.carbon-label { font-size: 11px; font-weight: bold; color: #94a3b8; display: block; }
.carbon-value { font-size: 16px; font-weight: 700; color: #facc15; font-family: monospace; }
.carbon-sub { font-size: 11px; color: green; font-weight: bold; }

.goal-section { background: rgba(16, 185, 129, 0.08); border-radius: 20px; padding: 14px 16px; border: 1px solid rgba(16, 185, 129, 0.2); }
.goal-header { display: flex; justify-content: space-between; font-size: 13px; color: #94a3b8; font-weight: bold; margin-bottom: 10px; }
.goal-percent { font-size: 18px; font-weight: 700; color: #10b981; }
.goal-detail { display: flex; justify-content: space-between; font-size: 10px; color: #94a3b8; font-weight: bold; margin-top: 8px; }
.goal-days-info { font-size: 11px; color: #10b981; margin-top: 8px; text-align: center; font-weight: bold; }

.trend-chart { background: rgba(16, 185, 129, 0.08); border-radius: 20px; padding: 12px; }
.trend-header { font-size: 13px; font-weight: 600; color: #94a3b8; margin-bottom: 12px; font-weight: bold; }

.ranking-section { background: rgba(16, 185, 129, 0.08); border-radius: 20px; padding: 14px; }
.ranking-header { font-size: 13px; font-weight: 600; color: #94a3b8; margin-bottom: 12px; font-weight: bold; }
.ranking-list { display: flex; flex-direction: column; gap: 10px; }
.ranking-item { display: flex; align-items: center; gap: 10px; }
.ranking-rank { width: 26px; height: 26px; background: rgba(255, 255, 255, 0.08); border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 600; color: #94a3b8; }
.ranking-rank.top-three { background: rgba(16, 185, 129, 0.2); color: #10b981; }
.ranking-name { width: 120px; font-size: 11px; color: #cbd5e1; font-weight: bold; }
.ranking-bar-wrap { flex: 1; height: 6px; background: rgba(255, 255, 255, 0.1); border-radius: 10px; overflow: hidden; background-color: #1e293b; }
.ranking-bar { height: 100%; border-radius: 10px; }
.ranking-value { width: 65px; font-size: 12px; font-family: monospace; color: #facc15; font-weight: bold; text-align: right; }
.datetimeview1 {
  font-size: 16px;
  color: #0ff;
  font-weight: 600;
  background: transparent;
  padding: 8px 20px;
  border-radius: 12px;
  backdrop-filter: blur(8px);
  width: auto;
  min-width: 280px;
  text-align: center;
  font-family: 'JetBrains Mono', 'Courier New', monospace;
  letter-spacing: 1px;
}
/* 移动端 */
@media (max-width: 768px) {
  .top-header { flex-direction: column; padding: 12px 16px 8px; margin: 0 12px; gap: 8px; }
  .header-left { width: 100%; justify-content: center; }
  .main-title { font-size: 28px; letter-spacing: 1px; }
  .datetime { font-size: 11px; padding: 4px 12px; min-width: auto; width: auto; border-radius: 20px; }
  .kpi-strip { flex-wrap: wrap; gap: 12px; margin: 8px 16px 16px; padding: 12px; justify-content: center; }
  .kpi-item { flex: 1 1 40%; justify-content: space-between; gap: 8px; }
  .kpi-label { font-size: 12px; }
  .kpi-value { font-size: 18px; }
  .content-area { flex-direction: column; padding: 0 16px 16px; gap: 0; }
  .left-panel, .right-panel { width: 100%; flex-shrink: 1; }
  .center-void { display: none; }
  .glass-card { border-radius: 20px; padding: 14px; margin-bottom: 16px; }
  .glass-card:hover { transform: none; }
  .card-title { font-size: 15px; }
  .occupancy-grid { gap: 8px; }
  .occupancy-item { padding: 6px; gap: 6px; }
  .occupancy-icon { font-size: 22px; }
  .occupancy-value { font-size: 18px; }
  .resource-grid { flex-wrap: wrap; gap: 12px; justify-content: center; }
  .resource-item { flex: 1 1 30%; min-width: 90px; }
  :deep(.el-progress-circle) { width: 70px !important; height: 70px !important; }
  :deep(.el-progress__text) { font-size: 10px !important; }
  .restaurant-name { width: 85px; font-size: 11px; }
  .restaurant-occupancy { font-size: 10px; }
  .traffic-label { font-size: 11px; }
  .traffic-value { font-size: 16px; }
  .parking-progress { width: 110px; }
  .parking-percent { font-size: 11px; }
  .env-dashboard-row { flex-wrap: wrap; gap: 12px; justify-content: center; }
  .env-item { flex: 1 1 30%; min-width: 90px; }
  .env-label { font-size: 9px; }
  .env-value { font-size: 12px; }
  .env-status { font-size: 8px; }
  .env-footer { font-size: 9px; flex-wrap: wrap; gap: 6px; justify-content: center; }
  .staff-grid { gap: 8px; }
  .staff-role { font-size: 10px; }
  .staff-count { font-size: 14px; }
  .room-details-list { max-height: 300px; }
  .room-icon { font-size: 18px; }
  .room-name { font-size: 13px; }
  .room-badge { font-size: 8px; padding: 1px 6px; }
  .room-stats { font-size: 10px; }
  .room-price { font-size: 12px; }
  .detail-label { width: 65px; font-size: 10px; }
  .detail-value { font-size: 10px; }
  .detail-value.amenities { font-size: 9px; }
  .room-footer { font-size: 10px; }
  .energy-report-drawer :deep(.el-drawer) { width: 100% !important; }
  .report-core-stats { grid-template-columns: 1fr; }
  .carbon-grid { grid-template-columns: 1fr; }
  .ranking-name { width: 100px; font-size: 10px; }
}
</style>

<style>
.el-drawer__body {
  scrollbar-width: none; /* Firefox */
}
.el-drawer__header {
  margin-bottom: 5px;
}
</style>