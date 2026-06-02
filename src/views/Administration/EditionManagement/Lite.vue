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
        <div class="loading-tip">Lite Edition</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="edition-showcase">
    <!-- Hero Section -->
    <div class="hero-section">
      <div class="hero-content">
        <div class="version-badge">LITE EDITION</div>
        <h1 class="hero-title">
          Lite
          <span class="hero-subtitle">Edition</span>
        </h1>
        <p class="hero-description">
          Core device management & administration. Essential building blocks
          for intelligent building operations.
        </p>
        <div class="hero-stats">
          <div class="stat-item">
            <el-icon><Grid /></el-icon>
            <span>{{ moduleCount }} Core Modules</span>
          </div>
          <div class="stat-item">
            <el-icon><Connection /></el-icon>
            <span>{{ totalFeatures }} Features</span>
          </div>
          <div class="stat-item">
            <el-icon><DataLine /></el-icon>
            <span>{{ integrationCount }} Integrations</span>
          </div>
        </div>
      </div>
      <div class="hero-visual">
        <div class="floating-cards">
          <div class="float-card card-1">
            <el-icon><Monitor /></el-icon>
            <span>Device Mgmt</span>
          </div>
          <div class="float-card card-2">
            <el-icon><BellFilled /></el-icon>
            <span>Alarm System</span>
          </div>
          <div class="float-card card-3">
            <el-icon><Setting /></el-icon>
            <span>Admin Portal</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Statistics Cards -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon"><el-icon><FolderOpened /></el-icon></div>
        <div class="stat-number">{{ moduleCount }}</div>
        <div class="stat-label">Module Categories</div>
      </div>
      <div class="stat-card">
        <div class="stat-icon"><el-icon><List /></el-icon></div>
        <div class="stat-number">{{ totalFeatures }}</div>
        <div class="stat-label">Total Features</div>
      </div>
      <div class="stat-card">
        <div class="stat-icon"><el-icon><Connection /></el-icon></div>
        <div class="stat-number">{{ integrationCount }}</div>
        <div class="stat-label">Integrations</div>
      </div>
      <div class="stat-card">
        <div class="stat-icon"><el-icon><DataBoard /></el-icon></div>
        <div class="stat-number">{{ dashboardCount }}</div>
        <div class="stat-label">Dashboard Metrics</div>
      </div>
    </div>

    <!-- Version Description Article -->
    <div class="description-article">
      <div class="article-container">
        <div class="article-header">
          <h2>Why Choose Lite Edition?</h2>
          <p class="article-subtitle">
            The perfect starting point for intelligent building management
          </p>
        </div>

        <div class="article-grid">
          <!-- Left Column - Main Content -->
          <div class="article-main">
            <div class="article-section">
              <h3>The Foundation of Smart Building Operations</h3>
              <p>
                The <strong>Lite Edition</strong> serves as the foundational tier of our
                intelligent building management platform, designed specifically for
                organizations that need core building automation and management
                capabilities without the complexity of advanced analytics modules.
              </p>
              <p>
                With its comprehensive suite of device management, alarm monitoring,
                and administrative tools, Lite Edition provides everything you need
                to centralize control of your building infrastructure. From HVAC
                systems and lighting controls to security devices and energy meters,
                all your assets can be monitored and managed from a single, intuitive
                dashboard.
              </p>
            </div>

            <div class="article-section">
              <h3>Key Benefits at a Glance</h3>
              <div class="benefits-grid">
                <div class="benefit-item">
                  <el-icon><Check /></el-icon>
                  <div>
                    <h4>Reduced Operational Costs</h4>
                    <p>Automate routine tasks and optimize resource allocation</p>
                  </div>
                </div>
                <div class="benefit-item">
                  <el-icon><Check /></el-icon>
                  <div>
                    <h4>Improved Response Time</h4>
                    <p>Real-time alerts enable immediate action on critical events</p>
                  </div>
                </div>
                <div class="benefit-item">
                  <el-icon><Check /></el-icon>
                  <div>
                    <h4>Enhanced Visibility</h4>
                    <p>Complete overview of device status and building performance</p>
                  </div>
                </div>
                <div class="benefit-item">
                  <el-icon><Check /></el-icon>
                  <div>
                    <h4>Scalable Foundation</h4>
                    <p>Easily upgrade to Professional or Enterprise editions as needs grow</p>
                  </div>
                </div>
              </div>
            </div>

            <div class="article-section">
              <h3>Technical Specifications</h3>
              <div class="specs-list">
                <div class="spec-item">
                  <span class="spec-label">Deployment Options:</span>
                  <span class="spec-value">On-premise / Cloud / Hybrid</span>
                </div>
                <div class="spec-item">
                  <span class="spec-label">Supported Protocols:</span>
                  <span class="spec-value">BACnet, Modbus, MQTT, OPC-UA, SNMP, REST API</span>
                </div>
                <div class="spec-item">
                  <span class="spec-label">User Capacity:</span>
                  <span class="spec-value">Up to 500 concurrent users</span>
                </div>
                <div class="spec-item">
                  <span class="spec-label">Device Support:</span>
                  <span class="spec-value">10,000+ devices per instance</span>
                </div>
                <div class="spec-item">
                  <span class="spec-label">SLA Guarantee:</span>
                  <span class="spec-value">99.9% uptime with 24/7 monitoring</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Right Column - Sidebar -->
          <div class="article-sidebar">
            <div class="sidebar-card">
              <div class="sidebar-icon"><el-icon><Trophy /></el-icon></div>
              <h4>Trusted By</h4>
              <p>500+ organizations worldwide choose Lite Edition as their building management foundation</p>
            </div>

            <div class="sidebar-card">
              <div class="sidebar-icon"><el-icon><Timer /></el-icon></div>
              <h4>Quick Deployment</h4>
              <p>Average deployment time: 2-4 weeks from order to go-live</p>
            </div>

            <div class="sidebar-card">
              <div class="sidebar-icon"><el-icon><Headset /></el-icon></div>
              <h4>24/7 Global Support</h4>
              <p>Dedicated support team with <strong>15-minute response SLA</strong> for critical issues</p>
            </div>

            <div class="sidebar-card highlight">
              <h4>Ready to get started?</h4>
              <p>Schedule a free consultation with our solution architects</p>
              <el-button type="primary" size="small" round @click="openDemoForm">
                Book a Call
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modules Grid -->
    <div class="modules-section">
      <div class="section-header">
        <h2>Module Overview</h2>
        <p>Comprehensive suite of intelligent building management capabilities</p>
      </div>

      <div class="modules-grid">
        <div
            v-for="(module, idx) in modules"
            :key="module.title"
            class="module-card"
            :style="{ animationDelay: `${idx * 0.05}s` }"
        >
          <div class="card-header">
            <div class="card-icon">
              <el-icon><component :is="getIconComponent(module.icon)" /></el-icon>
            </div>
            <div class="card-title">{{ module.title }}</div>
          </div>
          <div class="card-features">
            <div
                v-for="feature in getTopFeatures(module)"
                :key="feature"
                class="feature-item"
            >
              <el-icon><Check /></el-icon>
              <span>{{ feature }}</span>
            </div>
            <div v-if="getFeatureCount(module) > 6" class="feature-more">
              +{{ getFeatureCount(module) - 6 }} more
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Feature Comparison Section -->
    <div class="comparison-section">
      <div class="section-header">
        <h2>What's Included</h2>
        <p>Detailed breakdown of features and capabilities</p>
      </div>

      <div class="comparison-grid">
        <div class="comparison-card" v-for="group in featureGroups" :key="group.title">
          <h3>{{ group.title }}</h3>
          <ul>
            <li v-for="item in group.items" :key="item">
              <el-icon><Check /></el-icon>
              <span>{{ item }}</span>
            </li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Use Cases Section -->
    <div class="usecases-section">
      <div class="section-header">
        <h2>Perfect For</h2>
        <p>Ideal use cases for Lite Edition deployment</p>
      </div>

      <div class="usecases-grid">
        <div class="usecase-card">
          <div class="usecase-icon"><el-icon><OfficeBuilding /></el-icon></div>
          <h4>Single Building Management</h4>
          <p>Perfect for standalone office buildings, retail stores, or small campuses</p>
        </div>
        <div class="usecase-card">
          <div class="usecase-icon"><el-icon><School /></el-icon></div>
          <h4>Educational Facilities</h4>
          <p>Manage classrooms, labs, and common areas efficiently</p>
        </div>
        <div class="usecase-card">
          <div class="usecase-icon"><el-icon><FirstAidKit /></el-icon></div>
          <h4>Healthcare Facilities</h4>
          <p>Ensure critical systems like HVAC and access control are always operational</p>
        </div>
        <div class="usecase-card">
          <div class="usecase-icon"><el-icon><ShoppingCart /></el-icon></div>
          <h4>Retail & Hospitality</h4>
          <p>Optimize energy usage while maintaining customer comfort</p>
        </div>
      </div>
    </div>

    <!-- CTA Section with Demo Form -->
    <div class="cta-section">
      <div class="cta-content">
        <h3>Ready to transform your building management?</h3>
        <p>Experience the power of intelligent building operations</p>

        <el-button
            type="primary"
            size="large"
            round
            @click="openDemoForm"
            :loading="formLoading"
        >
          Request Demo
        </el-button>
      </div>
    </div>

    <!-- Demo Request Dialog -->
    <el-dialog
        v-model="demoDialogVisible"
        title="Request a Demo"
        width="500px"
        :close-on-click-modal="false"
    >
      <el-form
          ref="demoFormRef"
          :model="demoForm"
          :rules="demoFormRules"
          label-width="100px"
      >
        <el-form-item label="Full Name" prop="name">
          <el-input
              v-model="demoForm.name"
              placeholder="Enter your full name"
              prefix-icon="User"
          />
        </el-form-item>
        <el-form-item label="Email Address" prop="email">
          <el-input
              v-model="demoForm.email"
              placeholder="you@company.com"
              prefix-icon="Message"
          />
        </el-form-item>
        <el-form-item label="Company" prop="company">
          <el-input
              v-model="demoForm.company"
              placeholder="Enter your company name"
              prefix-icon="OfficeBuilding"
          />
        </el-form-item>
        <el-form-item label="Phone (optional)" prop="phone">
          <el-input
              v-model="demoForm.phone"
              placeholder="Contact number"
              prefix-icon="Phone"
          />
        </el-form-item>
        <el-form-item label="Message" prop="message">
          <el-input
              v-model="demoForm.message"
              type="textarea"
              :rows="3"
              placeholder="Tell us about your requirements..."
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="demoDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="submitDemoRequest" :loading="submitting">
          Submit Request
        </el-button>
      </template>
    </el-dialog>

    <!-- Success Message Toast -->
    <div v-if="showSuccess" class="success-toast">
      <el-icon><CircleCheckFilled /></el-icon>
      <span>Demo request submitted! Our team will contact you within 24 hours.</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import {
  Grid,
  Connection,
  DataLine,
  Monitor,
  BellFilled,
  Setting,
  FolderOpened,
  List,
  DataBoard,
  Check,
  Cpu,
  Odometer,
  HomeFilled,
  Coordinate,
  OfficeBuilding,
  Printer,
  DocumentChecked,
  Key,
  Headset,
  Lock,
  Coin,
  Camera,
  Share,
  WarningFilled,
  House,
  Trophy,
  Timer,
  School,
  FirstAidKit,
  ShoppingCart,
  User,
  Message,
  Phone,
  CircleCheckFilled
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Building feature map...',
  'Calculating metrics...',
  'Almost ready...'
]

// ==================== Demo Form State ====================
const demoDialogVisible = ref(false)
const formLoading = ref(false)
const submitting = ref(false)
const showSuccess = ref(false)
const demoFormRef = ref<FormInstance>()

const demoForm = ref({
  name: '',
  email: '',
  company: '',
  phone: '',
  message: ''
})

const demoFormRules: FormRules = {
  name: [
    { required: true, message: 'Please enter your name', trigger: 'blur' },
    { min: 2, max: 50, message: 'Name must be between 2 and 50 characters', trigger: 'blur' }
  ],
  email: [
    { required: true, message: 'Please enter your email', trigger: 'blur' },
    { type: 'email', message: 'Please enter a valid email address', trigger: 'blur' }
  ],
  company: [
    { required: true, message: 'Please enter your company name', trigger: 'blur' }
  ]
}

// ==================== Menu Data Interface ====================
interface MenuItem {
  icon: string
  index: string
  title: string
  children?: MenuItem[]
}

const menuConfig = ref<MenuItem[]>([])

// ==================== Computed Properties ====================
const modules = computed(() => {
  const result: Array<{
    icon: string
    index: string
    title: string
    children: MenuItem[]
    allFeatures: string[]
  }> = []

  const processNode = (node: MenuItem) => {
    if (node.children && node.children.length > 0) {
      const features: string[] = []
      const collectFeatures = (item: MenuItem) => {
        if (item.children && item.children.length > 0) {
          item.children.forEach(collectFeatures)
        } else {
          features.push(item.title)
        }
      }
      node.children.forEach(collectFeatures)

      result.push({
        icon: node.icon || 'Folder',
        index: node.index,
        title: node.title,
        children: node.children,
        allFeatures: features
      })
    }
  }

  menuConfig.value.forEach(processNode)
  return result
})

const moduleCount = computed(() => modules.value.length)
const totalFeatures = computed(() => {
  return modules.value.reduce((sum, mod) => sum + mod.allFeatures.length, 0)
})
const integrationCount = ref(18)
const dashboardCount = ref(24)

const getTopFeatures = (module: { allFeatures: string[] }) => {
  return module.allFeatures.slice(0, 6)
}

const getFeatureCount = (module: { allFeatures: string[] }) => {
  return module.allFeatures.length
}

const getIconComponent = (iconName: string) => {
  const iconMap: Record<string, any> = {
    HomeFilled: House,
    Coordinate: Coordinate,
    Odometer: Odometer,
    Cpu: Cpu,
    BellFilled: BellFilled,
    DataLine: DataLine,
    Setting: Setting,
    Folder: FolderOpened,
    OfficeBuilding: OfficeBuilding,
    Printer: Printer,
    DocumentChecked: DocumentChecked,
    Key: Key,
    Headset: Headset,
    Lock: Lock,
    Coin: Coin,
    Camera: Camera,
    Share: Share,
    WarningFilled: WarningFilled,
    Monitor: Monitor,
    Connection: Connection
  }
  return iconMap[iconName] || FolderOpened
}

const featureGroups = computed(() => [
  {
    title: 'Core Infrastructure',
    items: ['Device Management', 'Site Management', 'Alarm System', 'User Administration']
  },
  {
    title: 'Operational Excellence',
    items: ['Quick Control', 'Scene Management', 'Emergency Response', 'Operations Logbook']
  },
  {
    title: 'Data & Reporting',
    items: ['KPI Dashboard', 'System Overview', 'Reports & BI', 'Data Export']
  },
  {
    title: 'Administration',
    items: ['User & Role Management', 'Permission Control', 'Audit Logs', 'System Settings']
  }
])

// ==================== Demo Form Functions ====================
const openDemoForm = () => {
  demoDialogVisible.value = true
}

const submitDemoRequest = async () => {
  if (!demoFormRef.value) return

  await demoFormRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true

      // Simulate API call - replace with actual API endpoint
      await new Promise(resolve => setTimeout(resolve, 1500))

      console.log('Demo request submitted:', demoForm.value)

      demoDialogVisible.value = false
      submitting.value = false

      demoForm.value = {
        name: '',
        email: '',
        company: '',
        phone: '',
        message: ''
      }

      showSuccess.value = true
      setTimeout(() => {
        showSuccess.value = false
      }, 5000)

      ElMessage.success('Demo request submitted successfully!')
    }
  })
}

// ==================== Load Menu Data ====================
const loadMenuData = () => {
  menuConfig.value = [
    {
      children: [
        {
          children: [
            { icon: "", index: "/home/system-overview/total-devices-online-rate", title: "Total Devices / Online Rate" },
            { icon: "", index: "/home/system-overview/active-alarms", title: "Active Alarms" },
            { icon: "", index: "/home/system-overview/open-work-orders", title: "Open Work Orders" },
            { icon: "", index: "/home/system-overview/system-health", title: "System Health" }
          ],
          icon: "", index: "/home/system-overview", title: "System Overview"
        },
        {
          children: [
            {
              children: [
                { icon: "", index: "/home/kpi-dashboard/operational-kpi/availability", title: "Availability" },
                { icon: "", index: "/home/kpi-dashboard/operational-kpi/sla-compliance", title: "SLA Compliance" },
                { icon: "", index: "/home/kpi-dashboard/operational-kpi/response-time", title: "Response Time" }
              ],
              icon: "", index: "/home/kpi-dashboard/operational-kpi", title: "Operational KPI"
            },
            {
              children: [
                { icon: "", index: "/home/kpi-dashboard/energy-kpi/energy-intensity", title: "Energy Intensity" },
                { icon: "", index: "/home/kpi-dashboard/energy-kpi/peak-demand", title: "Peak Demand" },
                { icon: "", index: "/home/kpi-dashboard/energy-kpi/savings-progress", title: "Savings Progress" }
              ],
              icon: "", index: "/home/kpi-dashboard/energy-kpi", title: "Energy KPI"
            },
            {
              children: [
                { icon: "", index: "/home/kpi-dashboard/esg-kpi/carbon-intensity", title: "Carbon Intensity" },
                { icon: "", index: "/home/kpi-dashboard/esg-kpi/esg-score", title: "ESG Score" },
                { icon: "", index: "/home/kpi-dashboard/esg-kpi/compliance-gap", title: "Compliance Gap" }
              ],
              icon: "", index: "/home/kpi-dashboard/esg-kpi", title: "ESG KPI"
            },
            {
              children: [
                { icon: "", index: "/home/kpi-dashboard/facility-kpi/occupancy", title: "Occupancy" },
                { icon: "", index: "/home/kpi-dashboard/facility-kpi/service-requests", title: "Service Requests" },
                { icon: "", index: "/home/kpi-dashboard/facility-kpi/customer-satisfaction", title: "Customer Satisfaction" }
              ],
              icon: "", index: "/home/kpi-dashboard/facility-kpi", title: "Facility KPI"
            }
          ],
          icon: "", index: "/home/kpi-dashboard", title: "KPI Dashboard"
        },
        {
          children: [
            { icon: "", index: "/home/alarm-summary/critical", title: "Critical" },
            { icon: "", index: "/home/alarm-summary/major", title: "Major" },
            { icon: "", index: "/home/alarm-summary/warning", title: "Warning" },
            { icon: "", index: "/home/alarm-summary/information", title: "Information" }
          ],
          icon: "", index: "/home/alarm-summary", title: "Alarm Summary"
        },
        { icon: "", index: "/home/energy-overview", title: "Energy Overview" },
        { icon: "", index: "/home/site-health-dashboard", title: "Site Health Dashboard" },
        { icon: "", index: "/home/esg-dashboard", title: "ESG Dashboard" },
        { icon: "", index: "/home/portfolio-dashboard", title: "Portfolio Dashboard" },
        { icon: "", index: "/home/data-center", title: "Data Center Dashboard" },
        { icon: "", index: "/home/sustainability-summary", title: "Sustainability Summary" },
        { icon: "", index: "/home/ai-insights", title: "AI Insights" }
      ],
      icon: "HomeFilled", index: "/home", title: "Home"
    },
    {
      children: [
        {
          children: [
            {
              children: [
                { icon: "", index: "/operations/quick-control/hvac-control/temperature-setpoint", title: "Temperature Setpoint" },
                { icon: "", index: "/operations/quick-control/hvac-control/mode-control", title: "Mode Control" },
                { icon: "", index: "/operations/quick-control/hvac-control/fan-speed", title: "Fan Speed" }
              ],
              icon: "", index: "/operations/quick-control/hvac-control", title: "HVAC Control"
            },
            {
              children: [
                { icon: "", index: "/operations/quick-control/lighting-control/all-on-all-off", title: "All On / All Off" },
                { icon: "", index: "/operations/quick-control/lighting-control/zone-control", title: "Zone Control" },
                { icon: "", index: "/operations/quick-control/lighting-control/schedule-override", title: "Schedule Override" }
              ],
              icon: "", index: "/operations/quick-control/lighting-control", title: "Lighting Control"
            },
            {
              children: [
                { icon: "", index: "/operations/quick-control/access-control/door-open-close", title: "Door Open / Close" },
                { icon: "", index: "/operations/quick-control/access-control/lockdown", title: "Lockdown" },
                { icon: "", index: "/operations/quick-control/access-control/access-status", title: "Access Status" }
              ],
              icon: "", index: "/operations/quick-control/access-control", title: "Access Control"
            },
            {
              children: [
                { icon: "", index: "/operations/quick-control/cctv-control/live-view", title: "Live View" },
                { icon: "", index: "/operations/quick-control/cctv-control/snapshot", title: "Snapshot" },
                { icon: "", index: "/operations/quick-control/cctv-control/ptz-preset", title: "PTZ Preset" }
              ],
              icon: "", index: "/operations/quick-control/cctv-control", title: "CCTV Control"
            },
            {
              children: [
                { icon: "", index: "/operations/quick-control/emergency-devices/emergency-lighting", title: "Emergency Lighting" },
                { icon: "", index: "/operations/quick-control/emergency-devices/pa-broadcast", title: "PA Broadcast" },
                { icon: "", index: "/operations/quick-control/emergency-devices/panic-button", title: "Panic Button" }
              ],
              icon: "", index: "/operations/quick-control/emergency-devices", title: "Emergency Devices"
            }
          ],
          icon: "", index: "/operations/quick-control", title: "Quick Control"
        },
        {
          children: [
            { icon: "", index: "/operations/scene-management/normal-mode", title: "Normal Mode" },
            { icon: "", index: "/operations/scene-management/energy-saving-mode", title: "Energy Saving Mode" },
            { icon: "", index: "/operations/scene-management/maintenance-mode", title: "Maintenance Mode" },
            { icon: "", index: "/operations/scene-management/emergency-mode", title: "Emergency Mode" },
            { icon: "", index: "/operations/scene-management/custom-scenes", title: "Custom Scenes" }
          ],
          icon: "", index: "/operations/scene-management", title: "Scene Management"
        },
        {
          children: [
            { icon: "", index: "/operations/emergency-response/fire-emergency", title: "Fire Emergency" },
            { icon: "", index: "/operations/emergency-response/security-emergency", title: "Security Emergency" },
            { icon: "", index: "/operations/emergency-response/medical-emergency", title: "Medical Emergency" },
            { icon: "", index: "/operations/emergency-response/power-outage", title: "Power Outage" }
          ],
          icon: "", index: "/operations/emergency-response", title: "Emergency Response"
        },
        { icon: "", index: "/operations/operations-logbook", title: "Operations Logbook" },
        { icon: "", index: "/operations/shift-handover", title: "Shift Handover" },
        { icon: "", index: "/operations/operator-notes", title: "Operator Notes" },
        { icon: "", index: "/operations/incident-reporting", title: "Incident Reporting" },
        { icon: "", index: "/operations/daily-checklist", title: "Daily Checklist" }
      ],
      icon: "Coordinate", index: "/operations", title: "Operations"
    },
    {
      children: [
        {
          children: [
            { icon: "", index: "/sites-spaces/site-management/site-profile", title: "Site Profile" },
            { icon: "", index: "/sites-spaces/site-management/site-boundary", title: "Site Boundary" },
            { icon: "", index: "/sites-spaces/site-management/site-contacts", title: "Site Contacts" },
            { icon: "", index: "/sites-spaces/site-management/factory", title: "Factory" },
            { icon: "", index: "/sites-spaces/site-management/building", title: "Building" },
            { icon: "", index: "/sites-spaces/site-management/airport", title: "Airport" },
            { icon: "", index: "/sites-spaces/site-management/hotel", title: "Hotel" },
            { icon: "", index: "/sites-spaces/site-management/hospital", title: "Hospital" },
            { icon: "", index: "/sites-spaces/site-management/shopping", title: "Shopping" }
          ],
          icon: "", index: "/sites-spaces/site-management", title: "Site Management"
        },
        { icon: "", index: "/sites-spaces/building-management", title: "Building Management" },
        { icon: "", index: "/sites-spaces/floor-management", title: "Floor Management" },
        { icon: "", index: "/sites-spaces/zone-management", title: "Zone Management" },
        {
          children: [
            { icon: "", index: "/sites-spaces/space-management/room-area-registry", title: "Room / Area Registry" },
            { icon: "", index: "/sites-spaces/space-management/space-type", title: "Space Type" },
            { icon: "", index: "/sites-spaces/space-management/occupancy-mapping", title: "Occupancy Mapping" }
          ],
          icon: "", index: "/sites-spaces/space-management", title: "Space Management"
        },
        { icon: "", index: "/sites-spaces/campus-management", title: "Campus Management" },
        { icon: "", index: "/sites-spaces/multi-site-management", title: "Multi-Site Management" },
        {
          children: [
            { icon: "", index: "/sites-spaces/data-center-rooms/data-hall", title: "Data Hall" },
            { icon: "", index: "/sites-spaces/data-center-rooms/ups-room", title: "UPS Room" },
            { icon: "", index: "/sites-spaces/data-center-rooms/battery-room", title: "Battery Room" },
            { icon: "", index: "/sites-spaces/data-center-rooms/network-room", title: "Network Room" }
          ],
          icon: "", index: "/sites-spaces/data-center-rooms", title: "Data Center Rooms"
        },
        { icon: "", index: "/sites-spaces/white-space-management", title: "White Space Management" },
        { icon: "", index: "/sites-spaces/technical-rooms", title: "Technical Rooms" },
        { icon: "", index: "/sites-spaces/capacity-zones", title: "Capacity Zones" }
      ],
      icon: "Odometer", index: "/sites-spaces", title: "Sites & Spaces"
    },
    {
      children: [
        {
          children: [
            { icon: "", index: "/systems-devices/device-inventory/device-list", title: "Device List" },
            { icon: "", index: "/systems-devices/device-inventory/device-details", title: "Device Details" },
            { icon: "", index: "/systems-devices/device-inventory/device-import", title: "Device Import" },
            { icon: "", index: "/systems-devices/device-inventory/device-lifecycle", title: "Device Lifecycle" }
          ],
          icon: "", index: "/systems-devices/device-inventory", title: "Device Inventory"
        },
        {
          children: [
            { icon: "", index: "/systems-devices/device-monitoring/real-time-status", title: "Real-Time Status" },
            { icon: "", index: "/systems-devices/device-monitoring/telemetry-trends", title: "Telemetry Trends" },
            { icon: "", index: "/systems-devices/device-monitoring/online-offline", title: "Online / Offline" },
            { icon: "", index: "/systems-devices/device-monitoring/device-health", title: "Device Health" }
          ],
          icon: "", index: "/systems-devices/device-monitoring", title: "Device Monitoring"
        },
        { icon: "", index: "/systems-devices/device-groups", title: "Device Groups" },
        {
          children: [
            { icon: "", index: "/systems-devices/device-templates/standard-template", title: "Standard Template" },
            { icon: "", index: "/systems-devices/device-templates/vendor-template", title: "Vendor Template" },
            { icon: "", index: "/systems-devices/device-templates/custom-template", title: "Custom Template" }
          ],
          icon: "", index: "/systems-devices/device-templates", title: "Device Templates"
        },
        {
          children: [
            { icon: "", index: "/systems-devices/point-management/bacnet-points", title: "BACnet Points" },
            { icon: "", index: "/systems-devices/point-management/modbus-points", title: "Modbus Points" },
            { icon: "", index: "/systems-devices/point-management/mqtt-points", title: "MQTT Points" },
            { icon: "", index: "/systems-devices/point-management/opc-ua-points", title: "OPC-UA Points" },
            { icon: "", index: "/systems-devices/point-management/snmp-points", title: "SNMP Points" },
            { icon: "", index: "/systems-devices/point-management/virtual-points", title: "Virtual Points" },
            { icon: "", index: "/systems-devices/point-management/calculated-points", title: "Calculated Points" }
          ],
          icon: "", index: "/systems-devices/point-management", title: "Point Management"
        },
        { icon: "", index: "/systems-devices/area-topology", title: "Area Topology" },
        { icon: "", index: "/systems-devices/asset-tag-management", title: "Asset Tag Management" },
        {
          children: [
            { icon: "", index: "/systems-devices/hvac-systems/chillers", title: "Chillers" },
            { icon: "", index: "/systems-devices/hvac-systems/cooling-towers", title: "Cooling Towers" },
            { icon: "", index: "/systems-devices/hvac-systems/pumps", title: "Pumps" },
            { icon: "", index: "/systems-devices/hvac-systems/ahu", title: "AHU" },
            { icon: "", index: "/systems-devices/hvac-systems/fcu", title: "FCU" },
            { icon: "", index: "/systems-devices/hvac-systems/vav", title: "VAV" },
            { icon: "", index: "/systems-devices/hvac-systems/ventilation", title: "Ventilation" },
            { icon: "", index: "/systems-devices/hvac-systems/thermostats", title: "Thermostats" }
          ],
          icon: "", index: "/systems-devices/hvac-systems", title: "HVAC Systems"
        },
        {
          children: [
            { icon: "", index: "/systems-devices/lighting-systems/lighting-panels", title: "Lighting Panels" },
            { icon: "", index: "/systems-devices/lighting-systems/lighting-circuits", title: "Lighting Circuits" },
            { icon: "", index: "/systems-devices/lighting-systems/motion-sensors", title: "Motion Sensors" },
            { icon: "", index: "/systems-devices/lighting-systems/dali-knx-lighting", title: "DALI/KNX Lighting" }
          ],
          icon: "", index: "/systems-devices/lighting-systems", title: "Lighting Systems"
        },
        {
          children: [
            { icon: "", index: "/systems-devices/electrical-systems/main-switchboard", title: "Main Switchboard" },
            { icon: "", index: "/systems-devices/electrical-systems/distribution-board", title: "Distribution Board" },
            { icon: "", index: "/systems-devices/electrical-systems/power-meter", title: "Power Meter" },
            { icon: "", index: "/systems-devices/electrical-systems/power-quality", title: "Power Quality" },
            { icon: "", index: "/systems-devices/electrical-systems/transformer", title: "Transformer" }
          ],
          icon: "", index: "/systems-devices/electrical-systems", title: "Electrical Systems"
        },
        {
          children: [
            { icon: "", index: "/systems-devices/plumbing-systems/pumps", title: "Pumps" },
            { icon: "", index: "/systems-devices/plumbing-systems/tanks", title: "Tanks" },
            { icon: "", index: "/systems-devices/plumbing-systems/valves", title: "Valves" },
            { icon: "", index: "/systems-devices/plumbing-systems/leak-detection", title: "Leak Detection" }
          ],
          icon: "", index: "/systems-devices/plumbing-systems", title: "Plumbing Systems"
        },
        {
          children: [
            { icon: "", index: "/systems-devices/fire-alarm-systems/fire-panel", title: "Fire Panel" },
            { icon: "", index: "/systems-devices/fire-alarm-systems/smoke-heat-detectors", title: "Smoke / Heat Detectors" },
            { icon: "", index: "/systems-devices/fire-alarm-systems/fire-pumps", title: "Fire Pumps" },
            { icon: "", index: "/systems-devices/fire-alarm-systems/fire-impairment-status", title: "Fire Impairment Status" }
          ],
          icon: "", index: "/systems-devices/fire-alarm-systems", title: "Fire Alarm Systems"
        },
        { icon: "", index: "/systems-devices/security-alarm-systems", title: "Security Alarm Systems" },
        { icon: "", index: "/systems-devices/access-control-systems", title: "Access Control Systems" },
        {
          children: [
            { icon: "", index: "/systems-devices/cctv-systems/cameras", title: "Cameras" },
            { icon: "", index: "/systems-devices/cctv-systems/nvr-vms", title: "NVR / VMS" },
            { icon: "", index: "/systems-devices/cctv-systems/recording-status", title: "Recording Status" },
            { icon: "", index: "/systems-devices/cctv-systems/video-loss-status", title: "Video Loss Status" }
          ],
          icon: "", index: "/systems-devices/cctv-systems", title: "CCTV Systems"
        },
        { icon: "", index: "/systems-devices/ev-charging-systems", title: "EV Charging Systems" },
        { icon: "", index: "/systems-devices/renewable-energy-systems", title: "Renewable Energy Systems" },
        {
          children: [
            { icon: "", index: "/systems-devices/data-center-systems/ups-systems", title: "UPS Systems" },
            { icon: "", index: "/systems-devices/data-center-systems/pdu-systems", title: "PDU Systems" },
            { icon: "", index: "/systems-devices/data-center-systems/battery-systems", title: "Battery Systems" },
            { icon: "", index: "/systems-devices/data-center-systems/generator-systems", title: "Generator Systems" },
            { icon: "", index: "/systems-devices/data-center-systems/crac-systems", title: "CRAC Systems" },
            { icon: "", index: "/systems-devices/data-center-systems/crah-systems", title: "CRAH Systems" },
            { icon: "", index: "/systems-devices/data-center-systems/chiller-systems", title: "Chiller Systems" },
            { icon: "", index: "/systems-devices/data-center-systems/cooling-tower-systems", title: "Cooling Tower Systems" },
            { icon: "", index: "/systems-devices/data-center-systems/rack-sensors", title: "Rack Sensors" },
            { icon: "", index: "/systems-devices/data-center-systems/environmental-sensors", title: "Environmental Sensors" },
            { icon: "", index: "/systems-devices/data-center-systems/leak-detection", title: "Leak Detection" },
            { icon: "", index: "/systems-devices/data-center-systems/network-devices", title: "Network Devices" },
            { icon: "", index: "/systems-devices/data-center-systems/server-infrastructure", title: "Server Infrastructure" }
          ],
          icon: "", index: "/systems-devices/data-center-systems", title: "Data Center Systems"
        }
      ],
      icon: "Cpu", index: "/systems-devices", title: "Systems & Devices"
    },
    {
      children: [
        {
          children: [
            { icon: "", index: "/alarms-events/live-alarms/critical-alarms", title: "Critical Alarms" },
            { icon: "", index: "/alarms-events/live-alarms/major-alarms", title: "Major Alarms" },
            { icon: "", index: "/alarms-events/live-alarms/warning-alarms", title: "Warning Alarms" },
            { icon: "", index: "/alarms-events/live-alarms/information-events", title: "Information Events" }
          ],
          icon: "", index: "/alarms-events/live-alarms", title: "Live Alarms"
        },
        { icon: "", index: "/alarms-events/alarm-history", title: "Alarm History" },
        {
          children: [
            { icon: "", index: "/alarms-events/alarm-rules/threshold-rules", title: "Threshold Rules" },
            { icon: "", index: "/alarms-events/alarm-rules/status-rules", title: "Status Rules" },
            { icon: "", index: "/alarms-events/alarm-rules/time-delay-rules", title: "Time Delay Rules" },
            { icon: "", index: "/alarms-events/alarm-rules/composite-rules", title: "Composite Rules" }
          ],
          icon: "", index: "/alarms-events/alarm-rules", title: "Alarm Rules"
        },
        { icon: "", index: "/alarms-events/alarm-correlation", title: "Alarm Correlation" },
        { icon: "", index: "/alarms-events/escalation-rules", title: "Escalation Rules" },
        { icon: "", index: "/alarms-events/notification-center", title: "Notification Center" },
        { icon: "", index: "/alarms-events/event-analytics", title: "Event Analytics" },
        {
          children: [
            { icon: "", index: "/alarms-events/data-center-alarms/ups-alarms", title: "UPS Alarms" },
            { icon: "", index: "/alarms-events/data-center-alarms/battery-alarms", title: "Battery Alarms" },
            { icon: "", index: "/alarms-events/data-center-alarms/cooling-alarms", title: "Cooling Alarms" },
            { icon: "", index: "/alarms-events/data-center-alarms/environmental-alarms", title: "Environmental Alarms" },
            { icon: "", index: "/alarms-events/data-center-alarms/rack-alarms", title: "Rack Alarms" }
          ],
          icon: "", index: "/alarms-events/data-center-alarms", title: "Data Center Alarms"
        },
        { icon: "", index: "/alarms-events/alarm-sla", title: "Alarm SLA" }
      ],
      icon: "BellFilled", index: "/alarms-events", title: "Alarms & Events"
    },
    {
      children: [
        { icon: "", index: "/reports-bi/daily-reports", title: "Daily Reports" },
        { icon: "", index: "/reports-bi/weekly-reports", title: "Weekly Reports" },
        { icon: "", index: "/reports-bi/monthly-reports", title: "Monthly Reports" },
        { icon: "", index: "/reports-bi/annual-reports", title: "Annual Reports" },
        { icon: "", index: "/reports-bi/scheduled-reports", title: "Scheduled Reports" },
        { icon: "", index: "/reports-bi/custom-reports", title: "Custom Reports" },
        { icon: "", index: "/reports-bi/bi-reports", title: "BI Reports" },
        { icon: "", index: "/reports-bi/pdf-export", title: "PDF Export" },
        { icon: "", index: "/reports-bi/excel-export", title: "Excel Export" },
        {
          children: [
            { icon: "", index: "/reports-bi/report-governance/report-template", title: "Report Template" },
            { icon: "", index: "/reports-bi/report-governance/report-approval", title: "Report Approval" },
            { icon: "", index: "/reports-bi/report-governance/report-evidence-hash", title: "Report Evidence Hash" },
            { icon: "", index: "/reports-bi/report-governance/report-access-log", title: "Report Access Log" }
          ],
          icon: "", index: "/reports-bi/report-governance", title: "Report Governance"
        }
      ],
      icon: "DataLine", index: "/reports-bi", title: "Reports & BI"
    },
    {
      children: [
        { icon: "", index: "/administration/user-management", title: "User Management" },
        { icon: "", index: "/administration/role-management", title: "Role Management" },
        { icon: "", index: "/administration/permission-management", title: "Permission Management" },
        {
          children: [
            { icon: "", index: "/administration/edition-management/menu", title: "Menu" },
            { icon: "", index: "/administration/edition-management/lite", title: "Lite" },
            { icon: "", index: "/administration/edition-management/professional", title: "Professional" },
            { icon: "", index: "/administration/edition-management/enterprise", title: "Enterprise" },
            { icon: "", index: "/administration/edition-management/ai-enterprise", title: "AI Enterprise" }
          ],
          icon: "", index: "/administration/edition-management", title: "Edition Management"
        },
        { icon: "", index: "/administration/license-management", title: "License Management" },
        {
          children: [
            { icon: "", index: "/administration/feature-toggle-management/core-modules", title: "Core Modules" },
            { icon: "", index: "/administration/feature-toggle-management/esg-modules", title: "ESG Modules" },
            { icon: "", index: "/administration/feature-toggle-management/dcim-modules", title: "DCIM Modules" },
            { icon: "", index: "/administration/feature-toggle-management/ai-modules", title: "AI Modules" },
            { icon: "", index: "/administration/feature-toggle-management/digital-twin-modules", title: "Digital Twin Modules" },
            { icon: "", index: "/administration/feature-toggle-management/trust-modules", title: "Trust Modules" },
            { icon: "", index: "/administration/feature-toggle-management/security-modules", title: "Security Modules" },
            { icon: "", index: "/administration/feature-toggle-management/experimental-features", title: "Experimental Features" }
          ],
          icon: "", index: "/administration/feature-toggle-management", title: "Feature Toggle Management"
        },
        { icon: "", index: "/administration/tenant-management", title: "Tenant Management" },
        { icon: "", index: "/administration/integration-settings", title: "Integration Settings" },
        { icon: "", index: "/administration/notification-settings", title: "Notification Settings" },
        { icon: "", index: "/administration/system-settings", title: "System Settings" },
        { icon: "", index: "/administration/audit-logs", title: "Audit Logs" },
        { icon: "", index: "/administration/oem-branding", title: "OEM Branding" }
      ],
      icon: "Setting", index: "/administration", title: "Administration"
    }
  ]
}

// ==================== Lifecycle ====================
onMounted(() => {
  loadMenuData()

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
    }, 400)
  }, 2000)
})
</script>

<style scoped>
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

/* ==================== Main Content ==================== */
.edition-showcase {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #eef2f6 100%);
  overflow-x: hidden;
}

/* Hero Section */
.hero-section {
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  color: white;
  padding: 60px 80px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 40px;
}

.hero-content {
  flex: 1;
  min-width: 300px;
}

.version-badge {
  display: inline-block;
  padding: 4px 12px;
  background: rgba(59, 130, 246, 0.2);
  border: 1px solid rgba(59, 130, 246, 0.5);
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 1px;
  margin-bottom: 20px;
}

.hero-title {
  font-size: 48px;
  font-weight: 700;
  margin: 0 0 16px 0;
}

.hero-subtitle {
  font-size: 32px;
  font-weight: 400;
  color: #94a3b8;
}

.hero-description {
  font-size: 18px;
  color: #cbd5e1;
  line-height: 1.6;
  max-width: 500px;
  margin-bottom: 32px;
}

.hero-stats {
  display: flex;
  gap: 32px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #cbd5e1;
  font-size: 14px;
}

.stat-item .el-icon {
  font-size: 18px;
  color: #3b82f6;
}

.hero-visual {
  flex: 1;
  min-width: 280px;
  display: flex;
  justify-content: center;
}

.floating-cards {
  position: relative;
  width: 280px;
  height: 280px;
}

.float-card {
  position: absolute;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  padding: 12px 20px;
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
  font-weight: 500;
  white-space: nowrap;
  animation: float 3s ease-in-out infinite;
}

.float-card .el-icon {
  font-size: 20px;
  color: #3b82f6;
}

.card-1 { top: 20px; left: 20px; animation-delay: 0s; }
.card-2 { top: 100px; right: 0; animation-delay: 0.5s; }
.card-3 { bottom: 20px; left: 40px; animation-delay: 1s; }

@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-15px); }
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
  padding: 60px 80px;
  background: white;
  margin: 0;
}

.stat-card {
  text-align: center;
  padding: 24px;
  background: #f8fafc;
  border-radius: 20px;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px -8px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  border-radius: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
}

.stat-icon .el-icon {
  font-size: 24px;
  color: white;
}

.stat-number {
  font-size: 36px;
  font-weight: 700;
  color: #1e293b;
}

.stat-label {
  font-size: 14px;
  color: #64748b;
  margin-top: 8px;
}

/* Description Article Section */
.description-article {
  padding: 60px 80px;
  background: white;
}

.article-container {
  max-width: 1400px;
  margin: 0 auto;
}

.article-header {
  text-align: center;
  margin-bottom: 48px;
}

.article-header h2 {
  font-size: 32px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 12px;
}

.article-subtitle {
  font-size: 18px;
  color: #64748b;
}

.article-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 48px;
}

.article-main {
  display: flex;
  flex-direction: column;
  gap: 40px;
}

.article-section h3 {
  font-size: 20px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 2px solid #3b82f6;
  display: inline-block;
}

.article-section p {
  font-size: 16px;
  line-height: 1.7;
  color: #475569;
  margin-bottom: 20px;
}

.benefits-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
}

.benefit-item {
  display: flex;
  gap: 16px;
  padding: 16px;
  background: #f8fafc;
  border-radius: 16px;
  transition: all 0.3s ease;
}

.benefit-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px -6px rgba(0, 0, 0, 0.1);
}

.benefit-item .el-icon {
  font-size: 24px;
  color: #10b981;
  flex-shrink: 0;
}

.benefit-item h4 {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 6px;
}

.benefit-item p {
  font-size: 13px;
  color: #64748b;
  margin-bottom: 0;
}

.specs-list {
  background: #f8fafc;
  border-radius: 16px;
  overflow: hidden;
}

.spec-item {
  display: flex;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid #e2e8f0;
}

.spec-item:last-child {
  border-bottom: none;
}

.spec-label {
  font-weight: 600;
  color: #1e293b;
}

.spec-value {
  color: #3b82f6;
  font-family: monospace;
  font-size: 14px;
}

/* Article Sidebar */
.article-sidebar {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.sidebar-card {
  background: #f8fafc;
  border-radius: 20px;
  padding: 24px;
  text-align: center;
  transition: all 0.3s ease;
}

.sidebar-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px -8px rgba(0, 0, 0, 0.1);
}

.sidebar-icon {
  width: 56px;
  height: 56px;
  background: linear-gradient(135deg, #e0f2fe, #dbeafe);
  border-radius: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
}

.sidebar-icon .el-icon {
  font-size: 28px;
  color: #3b82f6;
}

.sidebar-card h4 {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 12px;
}

.sidebar-card p {
  font-size: 14px;
  color: #64748b;
  line-height: 1.6;
}

.sidebar-card.highlight {
  background: linear-gradient(135deg, #0f172a, #1e293b);
  color: white;
}

.sidebar-card.highlight h4 {
  color: white;
}

.sidebar-card.highlight p {
  color: #cbd5e1;
  margin-bottom: 20px;
}

/* Modules Section */
.modules-section {
  padding: 60px 80px;
  background: #f8fafc;
}

.section-header {
  text-align: center;
  margin-bottom: 48px;
}

.section-header h2 {
  font-size: 32px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 12px;
}

.section-header p {
  font-size: 16px;
  color: #64748b;
}

.modules-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 24px;
}

.module-card {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  transition: all 0.3s ease;
  animation: fadeInUp 0.5s ease-out forwards;
  opacity: 0;
}

.module-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 20px 40px -12px rgba(0, 0, 0, 0.15);
}

.card-header {
  background: linear-gradient(135deg, #0f172a, #1e293b);
  padding: 20px 24px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.card-icon {
  width: 40px;
  height: 40px;
  background: rgba(59, 130, 246, 0.2);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-icon .el-icon {
  font-size: 22px;
  color: #3b82f6;
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: white;
}

.card-features {
  padding: 20px 24px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 0;
  border-bottom: 1px solid #f1f5f9;
  font-size: 14px;
  color: #334155;
}

.feature-item:last-child {
  border-bottom: none;
}

.feature-item .el-icon {
  color: #10b981;
  font-size: 16px;
}

.feature-more {
  margin-top: 12px;
  padding-top: 8px;
  font-size: 13px;
  color: #3b82f6;
  text-align: center;
}

/* Comparison Section */
.comparison-section {
  padding: 60px 80px;
  background: white;
}

.comparison-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
}

.comparison-card {
  background: #f8fafc;
  border-radius: 16px;
  padding: 24px;
}

.comparison-card h3 {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 2px solid #3b82f6;
  display: inline-block;
}

.comparison-card ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.comparison-card li {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 0;
  font-size: 14px;
  color: #475569;
}

.comparison-card li .el-icon {
  color: #10b981;
  font-size: 14px;
}

/* Use Cases Section */
.usecases-section {
  padding: 60px 80px;
  background: #f1f5f9;
}

.usecases-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
}

.usecase-card {
  background: white;
  border-radius: 20px;
  padding: 32px 24px;
  text-align: center;
  transition: all 0.3s ease;
}

.usecase-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 20px 40px -12px rgba(0, 0, 0, 0.15);
}

.usecase-icon {
  width: 64px;
  height: 64px;
  background: linear-gradient(135deg, #e0f2fe, #dbeafe);
  border-radius: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
}

.usecase-icon .el-icon {
  font-size: 32px;
  color: #3b82f6;
}

.usecase-card h4 {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 12px;
}

.usecase-card p {
  font-size: 14px;
  color: #64748b;
  line-height: 1.6;
}

/* CTA Section */
.cta-section {
  padding: 80px;
  background: linear-gradient(135deg, #0f172a, #1e293b);
  text-align: center;
}

.cta-content h3 {
  font-size: 28px;
  font-weight: 700;
  color: white;
  margin-bottom: 12px;
}

.cta-content p {
  font-size: 16px;
  color: #94a3b8;
  margin-bottom: 32px;
}

/* Success Toast */
.success-toast {
  position: fixed;
  bottom: 30px;
  right: 30px;
  background: #10b981;
  color: white;
  padding: 14px 24px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
  font-weight: 500;
  z-index: 10000;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
  animation: slideInRight 0.3s ease-out;
}

.success-toast .el-icon {
  font-size: 20px;
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(100px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* Responsive */
@media (max-width: 1024px) {
  .hero-section {
    padding: 40px 40px;
  }
  .stats-grid, .description-article, .modules-section, .comparison-section, .usecases-section, .cta-section {
    padding: 40px 40px;
  }
  .article-grid {
    grid-template-columns: 1fr;
    gap: 32px;
  }
  .benefits-grid {
    grid-template-columns: 1fr;
  }
  .usecases-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .modules-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 32px;
  }
  .hero-stats {
    flex-direction: column;
    gap: 12px;
  }
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .usecases-grid {
    grid-template-columns: 1fr;
  }
  .spec-item {
    flex-direction: column;
    gap: 8px;
  }
}
</style>