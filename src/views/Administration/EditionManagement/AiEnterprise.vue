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
        <div class="loading-tip">AI Edition</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="edition-showcase">
    <!-- Hero Section -->
    <div class="hero-section">
      <div class="hero-content">
        <div class="version-badge">AI EDITION</div>
        <h1 class="hero-title">
          AI
          <span class="hero-subtitle">Edition</span>
        </h1>
        <p class="hero-description">
          AI analytics, video intelligence & digital twin. Next-generation cognitive building platform
          for autonomous operations.
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
            <el-icon><Cpu /></el-icon>
            <span>AI Analytics</span>
          </div>
          <div class="float-card card-2">
            <el-icon><Share /></el-icon>
            <span>Digital Twin</span>
          </div>
          <div class="float-card card-3">
            <el-icon><Key /></el-icon>
            <span>Trust Identity</span>
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
          <h2>Why Choose AI Edition?</h2>
          <p class="article-subtitle">
            Next-generation cognitive building platform for autonomous operations
          </p>
        </div>

        <div class="article-grid">
          <div class="article-main">
            <div class="article-section">
              <h3>The Ultimate Cognitive Building Platform</h3>
              <p>
                The <strong>AI Edition</strong> represents the pinnacle of intelligent building
                technology, combining artificial intelligence, computer vision, digital twin
                simulation, and blockchain-based trust infrastructure. Designed for forward-thinking
                organizations ready to embrace autonomous building operations.
              </p>
              <p>
                From AI-powered video analytics that detect safety violations in real-time to
                digital twin simulations that predict energy savings before implementation,
                AI Edition transforms buildings from reactive to predictive to truly autonomous.
                With built-in trust infrastructure using decentralized identity and blockchain
                anchoring, every decision is verifiable and auditable.
              </p>
            </div>

            <div class="article-section">
              <h3>Key Benefits at a Glance</h3>
              <div class="benefits-grid">
                <div class="benefit-item">
                  <el-icon><Check /></el-icon>
                  <div>
                    <h4>Autonomous Operations</h4>
                    <p>AI-driven decisions reduce manual intervention by up to 80%</p>
                  </div>
                </div>
                <div class="benefit-item">
                  <el-icon><Check /></el-icon>
                  <div>
                    <h4>Predictive Intelligence</h4>
                    <p>Anticipate issues before they occur with machine learning</p>
                  </div>
                </div>
                <div class="benefit-item">
                  <el-icon><Check /></el-icon>
                  <div>
                    <h4>Digital Twin Simulation</h4>
                    <p>Test scenarios virtually before real-world implementation</p>
                  </div>
                </div>
                <div class="benefit-item">
                  <el-icon><Check /></el-icon>
                  <div>
                    <h4>Trust & Compliance</h4>
                    <p>Blockchain-anchored evidence for regulatory compliance</p>
                  </div>
                </div>
              </div>
            </div>

            <div class="article-section">
              <h3>Technical Specifications</h3>
              <div class="specs-list">
                <div class="spec-item">
                  <span class="spec-label">Deployment Options:</span>
                  <span class="spec-value">Cloud-native / Hybrid / On-premise with AI accelerators</span>
                </div>
                <div class="spec-item">
                  <span class="spec-label">AI Models:</span>
                  <span class="spec-value">Computer Vision, NLP, Predictive Analytics, Generative AI</span>
                </div>
                <div class="spec-item">
                  <span class="spec-label">Video Analytics:</span>
                  <span class="spec-value">Real-time processing up to 10,000 camera streams</span>
                </div>
                <div class="spec-item">
                  <span class="spec-label">Digital Twin:</span>
                  <span class="spec-value">OpenBIM compliant, real-time synchronization</span>
                </div>
                <div class="spec-item">
                  <span class="spec-label">Blockchain:</span>
                  <span class="spec-value">Ethereum, Hyperledger, or private chain support</span>
                </div>
              </div>
            </div>
          </div>

          <div class="article-sidebar">
            <div class="sidebar-card">
              <div class="sidebar-icon"><el-icon><Trophy /></el-icon></div>
              <h4>Industry First</h4>
              <p>First building management platform with integrated AI + Digital Twin + Blockchain</p>
            </div>

            <div class="sidebar-card">
              <div class="sidebar-icon"><el-icon><Timer /></el-icon></div>
              <h4>Rapid AI ROI</h4>
              <p>Average 300% ROI within 6 months through predictive maintenance and energy optimization</p>
            </div>

            <div class="sidebar-card">
              <div class="sidebar-icon"><el-icon><Headset /></el-icon></div>
              <h4>AI Success Team</h4>
              <p>Dedicated AI engineers and data scientists for model optimization</p>
            </div>

            <div class="sidebar-card highlight">
              <h4>Ready for the future?</h4>
              <p>Schedule an AI innovation briefing with our cognitive building experts</p>
              <el-button type="primary" size="small" round @click="openDemoForm">
                Contact AI Team
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
        <p>Complete AI-powered suite for cognitive building management</p>
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
        <p>Complete AI-powered feature set for cognitive building management</p>
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
        <p>Ideal use cases for AI Edition deployment</p>
      </div>

      <div class="usecases-grid">
        <div class="usecase-card">
          <div class="usecase-icon"><el-icon><DataBoard /></el-icon></div>
          <h4>Hyperscale Data Centers</h4>
          <p>AI-optimized cooling and predictive maintenance</p>
        </div>
        <div class="usecase-card">
          <div class="usecase-icon"><el-icon><OfficeBuilding /></el-icon></div>
          <h4>Smart Headquarters</h4>
          <p>Fully autonomous building operations with AI concierge</p>
        </div>
        <div class="usecase-card">
          <div class="usecase-icon"><el-icon><FirstAidKit /></el-icon></div>
          <h4>Smart Hospitals</h4>
          <p>Patient safety monitoring and regulatory compliance</p>
        </div>
        <div class="usecase-card">
          <div class="usecase-icon"><el-icon><Share /></el-icon></div>
          <h4>Smart Cities</h4>
          <p>City-scale digital twin and AI video analytics</p>
        </div>
      </div>
    </div>

    <!-- CTA Section -->
    <div class="cta-section">
      <div class="cta-content">
        <h3>Ready to embrace cognitive building operations?</h3>
        <p>Experience the power of AI-driven building management</p>

        <el-button
            type="primary"
            size="large"
            round
            @click="openDemoForm"
            :loading="formLoading"
        >
          Request AI Demo
        </el-button>
      </div>
    </div>

    <!-- Demo Request Dialog -->
    <el-dialog
        v-model="demoDialogVisible"
        title="AI Edition Demo Request"
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
              placeholder="Tell us about your AI requirements..."
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
      <span>Demo request submitted! Our AI team will contact you within 24 hours.</span>
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
  CircleCheckFilled,
  Tools,
  Orange,
  TrendCharts,
  Rank
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading AI modules...',
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
const integrationCount = ref(75)
const dashboardCount = ref(120)

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
    Connection: Connection,
    Tools: Tools,
    Orange: Orange,
    TrendCharts: TrendCharts,
    Rank: Rank
  }
  return iconMap[iconName] || FolderOpened
}

const featureGroups = computed(() => [
  {
    title: 'AI Video Analytics',
    items: ['PPE Compliance Detection', 'Safety Monitoring', 'Vehicle Analytics', 'Crowd Analytics', 'Behavioral Analytics']
  },
  {
    title: 'Digital Twin & OpenBIM',
    items: ['BIM Management', 'Real-Time Twin', 'Scenario Simulation', 'Energy Simulation', 'Twin Analytics']
  },
  {
    title: 'Intelligence Suite',
    items: ['AI Assistant', 'Predictive Maintenance', 'Energy Optimization', 'Knowledge Graph', 'Digital Operator']
  },
  {
    title: 'Trust & Identity',
    items: ['DID Identity Center', 'Verifiable Credentials', 'Blockchain Anchoring', 'Smart Contracts', 'Decision Traceability']
  },
  {
    title: 'Fault Management',
    items: ['AI Fault Diagnosis', 'Root Cause Analysis', 'Fault Workflow', 'Fault Analytics']
  },
  {
    title: 'Integration Hub',
    items: ['Protocol Gateway', 'Device Drivers', 'Third-Party Systems', 'API Management']
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

      await new Promise(resolve => setTimeout(resolve, 1500))

      console.log('AI Edition demo request submitted:', demoForm.value)

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
        { icon: "", index: "/fault-management-system/fault-dashboard", title: "Fault Dashboard" },
        { icon: "", index: "/fault-management-system/active-faults", title: "Active Faults" },
        { icon: "", index: "/fault-management-system/fault-history", title: "Fault History" },
        { icon: "", index: "/fault-management-system/fault-correlation", title: "Fault Correlation" },
        {
          children: [
            { icon: "", index: "/fault-management-system/root-cause-analysis/rule-based-rca", title: "Rule-Based RCA" },
            { icon: "", index: "/fault-management-system/root-cause-analysis/historical-similarity", title: "Historical Similarity" },
            { icon: "", index: "/fault-management-system/root-cause-analysis/ai-rca", title: "AI RCA" },
            { icon: "", index: "/fault-management-system/root-cause-analysis/evidence-link", title: "Evidence Link" }
          ],
          icon: "", index: "/fault-management-system/root-cause-analysis", title: "Root Cause Analysis"
        },
        { icon: "", index: "/fault-management-system/fault-rules-engine", title: "Fault Rules Engine" },
        {
          children: [
            { icon: "", index: "/fault-management-system/fault-workflow/new", title: "New" },
            { icon: "", index: "/fault-management-system/fault-workflow/assigned", title: "Assigned" },
            { icon: "", index: "/fault-management-system/fault-workflow/investigating", title: "Investigating" },
            { icon: "", index: "/fault-management-system/fault-workflow/resolved", title: "Resolved" },
            { icon: "", index: "/fault-management-system/fault-workflow/closed", title: "Closed" }
          ],
          icon: "", index: "/fault-management-system/fault-workflow", title: "Fault Workflow"
        },
        { icon: "", index: "/fault-management-system/fault-analytics", title: "Fault Analytics" },
        { icon: "", index: "/fault-management-system/knowledge-base", title: "Knowledge Base" },
        {
          children: [
            { icon: "", index: "/fault-management-system/data-center-faults/ups-faults", title: "UPS Faults" },
            { icon: "", index: "/fault-management-system/data-center-faults/battery-faults", title: "Battery Faults" },
            { icon: "", index: "/fault-management-system/data-center-faults/cooling-faults", title: "Cooling Faults" },
            { icon: "", index: "/fault-management-system/data-center-faults/power-chain-faults", title: "Power Chain Faults" },
            { icon: "", index: "/fault-management-system/data-center-faults/rack-faults", title: "Rack Faults" },
            { icon: "", index: "/fault-management-system/data-center-faults/network-faults", title: "Network Faults" }
          ],
          icon: "", index: "/fault-management-system/data-center-faults", title: "Data Center Faults"
        },
        {
          children: [
            { icon: "", index: "/fault-management-system/fault-kpi/mtbf", title: "MTBF" },
            { icon: "", index: "/fault-management-system/fault-kpi/mttr", title: "MTTR" },
            { icon: "", index: "/fault-management-system/fault-kpi/failure-rate", title: "Failure Rate" },
            { icon: "", index: "/fault-management-system/fault-kpi/top-fault-assets", title: "Top Fault Assets" }
          ],
          icon: "", index: "/fault-management-system/fault-kpi", title: "Fault KPI"
        },
        { icon: "", index: "/fault-management-system/ai-fault-diagnosis", title: "AI Fault Diagnosis" }
      ],
      icon: "WarningFilled", index: "/fault-management-system", title: "Fault Management"
    },
    {
      children: [
        {
          children: [
            { icon: "", index: "/maintenance/work-orders/corrective", title: "Corrective" },
            { icon: "", index: "/maintenance/work-orders/preventive", title: "Preventive" },
            { icon: "", index: "/maintenance/work-orders/predictive", title: "Predictive" },
            { icon: "", index: "/maintenance/work-orders/emergency", title: "Emergency" }
          ],
          icon: "", index: "/maintenance/work-orders", title: "Work Orders"
        },
        {
          children: [
            { icon: "", index: "/maintenance/dispatch-management/assignment", title: "Assignment" },
            { icon: "", index: "/maintenance/dispatch-management/engineer-schedule", title: "Engineer Schedule" },
            { icon: "", index: "/maintenance/dispatch-management/mobile-dispatch", title: "Mobile Dispatch" }
          ],
          icon: "", index: "/maintenance/dispatch-management", title: "Dispatch Management"
        },
        {
          children: [
            { icon: "", index: "/maintenance/inspection-management/inspection-plan", title: "Inspection Plan" },
            { icon: "", index: "/maintenance/inspection-management/inspection-checklist", title: "Inspection Checklist" },
            { icon: "", index: "/maintenance/inspection-management/inspection-result", title: "Inspection Result" }
          ],
          icon: "", index: "/maintenance/inspection-management", title: "Inspection Management"
        },
        { icon: "", index: "/maintenance/preventive-maintenance", title: "Preventive Maintenance" },
        { icon: "", index: "/maintenance/predictive-maintenance", title: "Predictive Maintenance" },
        {
          children: [
            { icon: "", index: "/maintenance/asset-management/asset-register", title: "Asset Register" },
            { icon: "", index: "/maintenance/asset-management/asset-health", title: "Asset Health" },
            { icon: "", index: "/maintenance/asset-management/lifecycle-tracking", title: "Lifecycle Tracking" },
            { icon: "", index: "/maintenance/asset-management/replacement-planning", title: "Replacement Planning" }
          ],
          icon: "", index: "/maintenance/asset-management", title: "Asset Management"
        },
        { icon: "", index: "/maintenance/spare-parts-management", title: "Spare Parts Management" },
        { icon: "", index: "/maintenance/vendor-management", title: "Vendor Management" },
        { icon: "", index: "/maintenance/contract-management", title: "Contract Management" },
        { icon: "", index: "/maintenance/sla-management", title: "SLA Management" },
        { icon: "", index: "/maintenance/maintenance-analytics", title: "Maintenance Analytics" },
        {
          children: [
            { icon: "", index: "/maintenance/data-center-maintenance/ups-maintenance", title: "UPS Maintenance" },
            { icon: "", index: "/maintenance/data-center-maintenance/battery-maintenance", title: "Battery Maintenance" },
            { icon: "", index: "/maintenance/data-center-maintenance/cooling-maintenance", title: "Cooling Maintenance" },
            { icon: "", index: "/maintenance/data-center-maintenance/rack-maintenance", title: "Rack Maintenance" },
            { icon: "", index: "/maintenance/data-center-maintenance/generator-maintenance", title: "Generator Maintenance" }
          ],
          icon: "", index: "/maintenance/data-center-maintenance", title: "Data Center Maintenance"
        }
      ],
      icon: "Tools", index: "/maintenance", title: "Maintenance"
    },
    {
      children: [
        { icon: "", index: "/asset-intelligence/asset-register", title: "Asset Register" },
        { icon: "", index: "/asset-intelligence/asset-health-index", title: "Asset Health Index" },
        { icon: "", index: "/asset-intelligence/asset-criticality", title: "Asset Criticality" },
        { icon: "", index: "/asset-intelligence/asset-risk-matrix", title: "Asset Risk Matrix" },
        { icon: "", index: "/asset-intelligence/lifecycle-management", title: "Lifecycle Management" },
        { icon: "", index: "/asset-intelligence/replacement-planning", title: "Replacement Planning" },
        { icon: "", index: "/asset-intelligence/capex-planning", title: "CAPEX Planning" },
        { icon: "", index: "/asset-intelligence/asset-benchmark", title: "Asset Benchmark" },
        { icon: "", index: "/asset-intelligence/asset-analytics", title: "Asset Analytics" }
      ],
      icon: "TrendCharts", index: "/asset-intelligence", title: "Asset Intelligence"
    },
    {
      children: [
        { icon: "", index: "/energy-sustainability/electricity-monitoring", title: "Electricity Monitoring" },
        { icon: "", index: "/energy-sustainability/water-monitoring", title: "Water Monitoring" },
        { icon: "", index: "/energy-sustainability/gas-monitoring", title: "Gas Monitoring" },
        { icon: "", index: "/energy-sustainability/thermal-energy-monitoring", title: "Thermal Energy Monitoring" },
        { icon: "", index: "/energy-sustainability/solar-monitoring", title: "Solar Monitoring" },
        { icon: "", index: "/energy-sustainability/battery-storage", title: "Battery Storage" },
        { icon: "", index: "/energy-sustainability/utility-billing", title: "Utility Billing" },
        {
          children: [
            { icon: "", index: "/energy-sustainability/energy-analytics/consumption-analysis", title: "Consumption Analysis" },
            { icon: "", index: "/energy-sustainability/energy-analytics/peak-demand", title: "Peak Demand" },
            { icon: "", index: "/energy-sustainability/energy-analytics/benchmark-analysis", title: "Benchmark Analysis" },
            { icon: "", index: "/energy-sustainability/energy-analytics/savings-opportunities", title: "Savings Opportunities" }
          ],
          icon: "", index: "/energy-sustainability/energy-analytics", title: "Energy Analytics"
        },
        {
          children: [
            { icon: "", index: "/energy-sustainability/carbon-analytics/scope-1", title: "Scope 1" },
            { icon: "", index: "/energy-sustainability/carbon-analytics/scope-2", title: "Scope 2" },
            { icon: "", index: "/energy-sustainability/carbon-analytics/scope-3", title: "Scope 3" },
            { icon: "", index: "/energy-sustainability/carbon-analytics/carbon-intensity", title: "Carbon Intensity" }
          ],
          icon: "", index: "/energy-sustainability/carbon-analytics", title: "Carbon Analytics"
        },
        { icon: "", index: "/energy-sustainability/esg-dashboard", title: "ESG Dashboard" },
        { icon: "", index: "/energy-sustainability/green-finance-metrics", title: "Green Finance Metrics" },
        {
          children: [
            { icon: "", index: "/energy-sustainability/data-center-energy/pue-analytics", title: "PUE Analytics" },
            { icon: "", index: "/energy-sustainability/data-center-energy/cue-analytics", title: "CUE Analytics" },
            { icon: "", index: "/energy-sustainability/data-center-energy/wue-analytics", title: "WUE Analytics" },
            { icon: "", index: "/energy-sustainability/data-center-energy/cooling-efficiency", title: "Cooling Efficiency" },
            { icon: "", index: "/energy-sustainability/data-center-energy/power-utilization", title: "Power Utilization" },
            { icon: "", index: "/energy-sustainability/data-center-energy/renewable-energy-ratio", title: "Renewable Energy Ratio" },
            { icon: "", index: "/energy-sustainability/data-center-energy/benchmark-comparison", title: "Benchmark Comparison" }
          ],
          icon: "", index: "/energy-sustainability/data-center-energy", title: "Data Center Energy"
        },
        {
          children: [
            { icon: "", index: "/energy-sustainability/sustainability-reporting/esg-reports", title: "ESG Reports" },
            { icon: "", index: "/energy-sustainability/sustainability-reporting/carbon-reports", title: "Carbon Reports" },
            { icon: "", index: "/energy-sustainability/sustainability-reporting/energy-reports", title: "Energy Reports" },
            { icon: "", index: "/energy-sustainability/sustainability-reporting/green-finance-evidence", title: "Green Finance Evidence" }
          ],
          icon: "", index: "/energy-sustainability/sustainability-reporting", title: "Sustainability Reporting"
        }
      ],
      icon: "Orange", index: "/energy-sustainability", title: "Energy & Sustainability"
    },
    {
      children: [
        {
          children: [
            { icon: "", index: "/facility-services/parking-management/parking-dashboard", title: "Parking Dashboard" },
            { icon: "", index: "/facility-services/parking-management/parking-space-status", title: "Parking Space Status" },
            { icon: "", index: "/facility-services/parking-management/anpr-records", title: "ANPR Records" },
            { icon: "", index: "/facility-services/parking-management/parking-violation", title: "Parking Violation" },
            { icon: "", index: "/facility-services/parking-management/parking-reports", title: "Parking Reports" }
          ],
          icon: "", index: "/facility-services/parking-management", title: "Parking Management"
        },
        { icon: "", index: "/facility-services/visitor-management", title: "Visitor Management" },
        { icon: "", index: "/facility-services/meeting-room-booking", title: "Meeting Room Booking" },
        {
          children: [
            { icon: "", index: "/facility-services/housekeeping-management/cleaning-task", title: "Cleaning Task" },
            { icon: "", index: "/facility-services/housekeeping-management/smart-toilet-monitoring", title: "Smart Toilet Monitoring" },
            { icon: "", index: "/facility-services/housekeeping-management/odor-occupancy-consumables", title: "Odor / Occupancy / Consumables" },
            { icon: "", index: "/facility-services/housekeeping-management/cleaning-reports", title: "Cleaning Reports" }
          ],
          icon: "", index: "/facility-services/housekeeping-management", title: "Housekeeping Management"
        },
        { icon: "", index: "/facility-services/waste-management", title: "Waste Management" },
        { icon: "", index: "/facility-services/occupancy-analytics", title: "Occupancy Analytics" },
        { icon: "", index: "/facility-services/facility-requests", title: "Facility Requests" },
        { icon: "", index: "/facility-services/service-desk", title: "Service Desk" }
      ],
      icon: "OfficeBuilding", index: "/facility-services", title: "Facility Services"
    },
    {
      children: [
        {
          children: [
            { icon: "", index: "/data-center-operations/introduction/industry-benchmark", title: "Industry Benchmark" },
            { icon: "", index: "/data-center-operations/introduction/esg-compliance-overview", title: "ESG Compliance Overview" },
            { icon: "", index: "/data-center-operations/introduction/optimization-potential", title: "Optimization Potential" },
            { icon: "", index: "/data-center-operations/introduction/roi-calculator", title: "ROI Calculator" },
            { icon: "", index: "/data-center-operations/introduction/executive-summary", title: "Executive Summary" }
          ],
          icon: "", index: "/data-center-operations/introduction", title: "Introduction"
        },
        { icon: "", index: "/data-center-operations/data-center-dashboard", title: "Data Center Dashboard" },
        {
          children: [
            { icon: "", index: "/data-center-operations/esg-compliance-center/ifrs-s2", title: "IFRS S2" },
            { icon: "", index: "/data-center-operations/esg-compliance-center/issb", title: "ISSB" },
            { icon: "", index: "/data-center-operations/esg-compliance-center/gri", title: "GRI" },
            { icon: "", index: "/data-center-operations/esg-compliance-center/tcfd", title: "TCFD" },
            { icon: "", index: "/data-center-operations/esg-compliance-center/csrd", title: "CSRD" },
            { icon: "", index: "/data-center-operations/esg-compliance-center/sgx-hkex-mas", title: "SGX / HKEX / MAS" },
            { icon: "", index: "/data-center-operations/esg-compliance-center/gap-analysis", title: "Gap Analysis" },
            { icon: "", index: "/data-center-operations/esg-compliance-center/compliance-roadmap", title: "Compliance Roadmap" }
          ],
          icon: "", index: "/data-center-operations/esg-compliance-center", title: "ESG Compliance Center"
        },
        {
          children: [
            { icon: "", index: "/data-center-operations/cooling-optimization/chiller-optimization", title: "Chiller Optimization" },
            { icon: "", index: "/data-center-operations/cooling-optimization/crac-optimization", title: "CRAC Optimization" },
            { icon: "", index: "/data-center-operations/cooling-optimization/crah-optimization", title: "CRAH Optimization" },
            { icon: "", index: "/data-center-operations/cooling-optimization/free-cooling", title: "Free Cooling" },
            { icon: "", index: "/data-center-operations/cooling-optimization/hybrid-cooling", title: "Hybrid Cooling" },
            { icon: "", index: "/data-center-operations/cooling-optimization/dynamic-setpoint-control", title: "Dynamic Setpoint Control" },
            { icon: "", index: "/data-center-operations/cooling-optimization/cooling-benchmark", title: "Cooling Benchmark" }
          ],
          icon: "", index: "/data-center-operations/cooling-optimization", title: "Cooling Optimization"
        },
        {
          children: [
            { icon: "", index: "/data-center-operations/airflow-optimization/thermal-map", title: "Thermal Map" },
            { icon: "", index: "/data-center-operations/airflow-optimization/hotspot-detection", title: "Hotspot Detection" },
            { icon: "", index: "/data-center-operations/airflow-optimization/cfd-simulation", title: "CFD Simulation" },
            { icon: "", index: "/data-center-operations/airflow-optimization/airflow-analysis", title: "Airflow Analysis" },
            { icon: "", index: "/data-center-operations/airflow-optimization/containment-analysis", title: "Containment Analysis" }
          ],
          icon: "", index: "/data-center-operations/airflow-optimization", title: "Airflow Optimization"
        },
        {
          children: [
            { icon: "", index: "/data-center-operations/power-optimization/ups-optimization", title: "UPS Optimization" },
            { icon: "", index: "/data-center-operations/power-optimization/pdu-optimization", title: "PDU Optimization" },
            { icon: "", index: "/data-center-operations/power-optimization/generator-strategy", title: "Generator Strategy" },
            { icon: "", index: "/data-center-operations/power-optimization/battery-strategy", title: "Battery Strategy" },
            { icon: "", index: "/data-center-operations/power-optimization/load-balancing", title: "Load Balancing" },
            { icon: "", index: "/data-center-operations/power-optimization/power-quality", title: "Power Quality" }
          ],
          icon: "", index: "/data-center-operations/power-optimization", title: "Power Optimization"
        },
        {
          children: [
            { icon: "", index: "/data-center-operations/capacity-management/rack-capacity", title: "Rack Capacity" },
            { icon: "", index: "/data-center-operations/capacity-management/power-capacity", title: "Power Capacity" },
            { icon: "", index: "/data-center-operations/capacity-management/cooling-capacity", title: "Cooling Capacity" },
            { icon: "", index: "/data-center-operations/capacity-management/space-capacity", title: "Space Capacity" },
            { icon: "", index: "/data-center-operations/capacity-management/capacity-forecast", title: "Capacity Forecast" }
          ],
          icon: "", index: "/data-center-operations/capacity-management", title: "Capacity Management"
        },
        {
          children: [
            { icon: "", index: "/data-center-operations/rack-management/rack-layout", title: "Rack Layout" },
            { icon: "", index: "/data-center-operations/rack-management/rack-inventory", title: "Rack Inventory" },
            { icon: "", index: "/data-center-operations/rack-management/u-space-management", title: "U Space Management" },
            { icon: "", index: "/data-center-operations/rack-management/rack-utilization", title: "Rack Utilization" }
          ],
          icon: "", index: "/data-center-operations/rack-management", title: "Rack Management"
        },
        { icon: "", index: "/data-center-operations/environmental-monitoring", title: "Environmental Monitoring" },
        { icon: "", index: "/data-center-operations/carbon-optimization", title: "Carbon Optimization" },
        {
          children: [
            { icon: "", index: "/data-center-operations/scenario-simulation/baseline", title: "Baseline" },
            { icon: "", index: "/data-center-operations/scenario-simulation/free-cooling-simulation", title: "Free Cooling" },
            { icon: "", index: "/data-center-operations/scenario-simulation/hybrid-cooling-simulation", title: "Hybrid Cooling" },
            { icon: "", index: "/data-center-operations/scenario-simulation/supply-air-optimization", title: "Supply Air Optimization" },
            { icon: "", index: "/data-center-operations/scenario-simulation/containment-upgrade", title: "Containment Upgrade" },
            { icon: "", index: "/data-center-operations/scenario-simulation/roi-simulation", title: "ROI Simulation" }
          ],
          icon: "", index: "/data-center-operations/scenario-simulation", title: "Scenario Simulation"
        },
        { icon: "", index: "/data-center-operations/recommendation-center", title: "Recommendation Center" },
        { icon: "", index: "/data-center-operations/savings-verification", title: "Savings Verification" },
        { icon: "", index: "/data-center-operations/asset-lifecycle", title: "Asset Lifecycle" },
        { icon: "", index: "/data-center-operations/digital-twin-integration", title: "Digital Twin Integration" },
        { icon: "", index: "/data-center-operations/sustainability-reports", title: "Sustainability Reports" }
      ],
      icon: "Printer", index: "/data-center-operations", title: "Data Center Operations"
    },
    {
      children: [
        { icon: "", index: "/decision-evidence/decision-dashboard", title: "Decision Dashboard" },
        {
          children: [
            { icon: "", index: "/decision-evidence/decision-register/fault-decisions", title: "Fault Decisions" },
            { icon: "", index: "/decision-evidence/decision-register/maintenance-decisions", title: "Maintenance Decisions" },
            { icon: "", index: "/decision-evidence/decision-register/esg-decisions", title: "ESG Decisions" },
            { icon: "", index: "/decision-evidence/decision-register/energy-decisions", title: "Energy Decisions" },
            { icon: "", index: "/decision-evidence/decision-register/ai-recommendations", title: "AI Recommendations" }
          ],
          icon: "", index: "/decision-evidence/decision-register", title: "Decision Register"
        },
        {
          children: [
            { icon: "", index: "/decision-evidence/workflow-management/approval-matrix", title: "Approval Matrix" },
            { icon: "", index: "/decision-evidence/workflow-management/approval-steps", title: "Approval Steps" },
            { icon: "", index: "/decision-evidence/workflow-management/delegation", title: "Delegation" },
            { icon: "", index: "/decision-evidence/workflow-management/exception-handling", title: "Exception Handling" }
          ],
          icon: "", index: "/decision-evidence/workflow-management", title: "Workflow Management"
        },
        { icon: "", index: "/decision-evidence/decision-timeline", title: "Decision Timeline" },
        {
          children: [
            { icon: "", index: "/decision-evidence/evidence-repository/photos", title: "Photos" },
            { icon: "", index: "/decision-evidence/evidence-repository/videos", title: "Videos" },
            { icon: "", index: "/decision-evidence/evidence-repository/documents", title: "Documents" },
            { icon: "", index: "/decision-evidence/evidence-repository/reports", title: "Reports" },
            { icon: "", index: "/decision-evidence/evidence-repository/data-snapshots", title: "Data Snapshots" }
          ],
          icon: "", index: "/decision-evidence/evidence-repository", title: "Evidence Repository"
        },
        { icon: "", index: "/decision-evidence/audit-trail", title: "Audit Trail" },
        { icon: "", index: "/decision-evidence/digital-signatures", title: "Digital Signatures" },
        { icon: "", index: "/decision-evidence/approval-matrix", title: "Approval Matrix" },
        { icon: "", index: "/decision-evidence/lessons-learned", title: "Lessons Learned" },
        { icon: "", index: "/decision-evidence/ai-recommendation-log", title: "AI Recommendation Log" }
      ],
      icon: "DocumentChecked", index: "/decision-evidence", title: "Decision & Evidence"
    },
    {
      children: [
        { icon: "", index: "/command-center/operations-dashboard", title: "Operations Dashboard" },
        { icon: "", index: "/command-center/gis-map", title: "GIS Map" },
        { icon: "", index: "/command-center/situation-awareness", title: "Situation Awareness" },
        { icon: "", index: "/command-center/incident-center", title: "Incident Center" },
        { icon: "", index: "/command-center/emergency-command", title: "Emergency Command" },
        { icon: "", index: "/command-center/resource-dispatch", title: "Resource Dispatch" },
        { icon: "", index: "/command-center/executive-dashboard", title: "Executive Dashboard" }
      ],
      icon: "Monitor", index: "/command-center", title: "Command Center"
    },
    {
      children: [
        { icon: "", index: "/data-platform/data-sources", title: "Data Sources" },
        {
          children: [
            { icon: "", index: "/data-platform/data-quality/quality-rules", title: "Quality Rules" },
            { icon: "", index: "/data-platform/data-quality/missing-data", title: "Missing Data" },
            { icon: "", index: "/data-platform/data-quality/outlier-detection", title: "Outlier Detection" },
            { icon: "", index: "/data-platform/data-quality/data-correction-log", title: "Data Correction Log" }
          ],
          icon: "", index: "/data-platform/data-quality", title: "Data Quality"
        },
        { icon: "", index: "/data-platform/data-catalog", title: "Data Catalog" },
        {
          children: [
            { icon: "", index: "/data-platform/historian/raw-telemetry", title: "Raw Telemetry" },
            { icon: "", index: "/data-platform/historian/clean-telemetry", title: "Clean Telemetry" },
            { icon: "", index: "/data-platform/historian/aggregated-data", title: "Aggregated Data" },
            { icon: "", index: "/data-platform/historian/retention-policy", title: "Retention Policy" }
          ],
          icon: "", index: "/data-platform/historian", title: "Historian"
        },
        { icon: "", index: "/data-platform/data-lake", title: "Data Lake" },
        { icon: "", index: "/data-platform/etl-management", title: "ETL Management" },
        {
          children: [
            { icon: "", index: "/data-platform/semantic-model/site-building-space", title: "Site / Building / Space" },
            { icon: "", index: "/data-platform/semantic-model/asset-device-point", title: "Asset / Device / Point" },
            { icon: "", index: "/data-platform/semantic-model/event-fault-work-order", title: "Event / Fault / Work Order" },
            { icon: "", index: "/data-platform/semantic-model/esg-dcim-ai-semantics", title: "ESG / DCIM / AI Semantics" }
          ],
          icon: "", index: "/data-platform/semantic-model", title: "Semantic Model"
        },
        { icon: "", index: "/data-platform/metadata-management", title: "Metadata Management" },
        { icon: "", index: "/data-platform/data-governance", title: "Data Governance" },
        {
          children: [
            { icon: "", index: "/data-platform/data-services/rest-api", title: "REST API" },
            { icon: "", index: "/data-platform/data-services/graphql-api", title: "GraphQL API" },
            { icon: "", index: "/data-platform/data-services/websocket", title: "WebSocket" },
            { icon: "", index: "/data-platform/data-services/data-export-api", title: "Data Export API" }
          ],
          icon: "", index: "/data-platform/data-services", title: "Data Services"
        }
      ],
      icon: "Coin", index: "/data-platform", title: "Data Platform"
    },
    {
      children: [
        {
          children: [
            { icon: "", index: "/integration-hub/protocol-gateway/bacnet", title: "BACnet" },
            { icon: "", index: "/integration-hub/protocol-gateway/modbus", title: "Modbus" },
            { icon: "", index: "/integration-hub/protocol-gateway/opc-ua", title: "OPC-UA" },
            { icon: "", index: "/integration-hub/protocol-gateway/mqtt", title: "MQTT" },
            { icon: "", index: "/integration-hub/protocol-gateway/snmp", title: "SNMP" },
            { icon: "", index: "/integration-hub/protocol-gateway/knx", title: "KNX" },
            { icon: "", index: "/integration-hub/protocol-gateway/iec61850", title: "IEC61850" },
            { icon: "", index: "/integration-hub/protocol-gateway/onvif", title: "ONVIF" },
            { icon: "", index: "/integration-hub/protocol-gateway/rest-api", title: "REST API" }
          ],
          icon: "", index: "/integration-hub/protocol-gateway", title: "Protocol Gateway"
        },
        {
          children: [
            { icon: "", index: "/integration-hub/device-drivers/siemens", title: "Siemens" },
            { icon: "", index: "/integration-hub/device-drivers/schneider", title: "Schneider" },
            { icon: "", index: "/integration-hub/device-drivers/abb", title: "ABB" },
            { icon: "", index: "/integration-hub/device-drivers/honeywell", title: "Honeywell" },
            { icon: "", index: "/integration-hub/device-drivers/johnson-controls", title: "Johnson Controls" },
            { icon: "", index: "/integration-hub/device-drivers/vertiv", title: "Vertiv" },
            { icon: "", index: "/integration-hub/device-drivers/huawei", title: "Huawei" },
            { icon: "", index: "/integration-hub/device-drivers/delta", title: "Delta" },
            { icon: "", index: "/integration-hub/device-drivers/daikin", title: "Daikin" },
            { icon: "", index: "/integration-hub/device-drivers/carrier", title: "Carrier" },
            { icon: "", index: "/integration-hub/device-drivers/mitsubishi", title: "Mitsubishi" }
          ],
          icon: "", index: "/integration-hub/device-drivers", title: "Device Drivers"
        },
        {
          children: [
            { icon: "", index: "/integration-hub/custom-protocols/custom-iot-adapter", title: "Custom IoT Adapter" },
            { icon: "", index: "/integration-hub/custom-protocols/smart-toilet-adapter", title: "Smart Toilet Adapter" },
            { icon: "", index: "/integration-hub/custom-protocols/esp32-adapter", title: "ESP32 Adapter" },
            { icon: "", index: "/integration-hub/custom-protocols/ble-gateway-adapter", title: "BLE Gateway Adapter" },
            { icon: "", index: "/integration-hub/custom-protocols/payload-mapping", title: "Payload Mapping" }
          ],
          icon: "", index: "/integration-hub/custom-protocols", title: "Private / Custom Protocols"
        },
        {
          children: [
            { icon: "", index: "/integration-hub/third-party-systems/erp", title: "ERP" },
            { icon: "", index: "/integration-hub/third-party-systems/cmms", title: "CMMS" },
            { icon: "", index: "/integration-hub/third-party-systems/bim", title: "BIM" },
            { icon: "", index: "/integration-hub/third-party-systems/gis", title: "GIS" },
            { icon: "", index: "/integration-hub/third-party-systems/scada", title: "SCADA" },
            { icon: "", index: "/integration-hub/third-party-systems/ems", title: "EMS" }
          ],
          icon: "", index: "/integration-hub/third-party-systems", title: "Third Party Systems"
        },
        {
          children: [
            { icon: "", index: "/integration-hub/vendor-platform-adapter/hikvision-platform", title: "Hikvision Platform" },
            { icon: "", index: "/integration-hub/vendor-platform-adapter/dahua-platform", title: "Dahua Platform" },
            { icon: "", index: "/integration-hub/vendor-platform-adapter/vms-platform", title: "VMS Platform" },
            { icon: "", index: "/integration-hub/vendor-platform-adapter/parking-platform", title: "Parking Platform" },
            { icon: "", index: "/integration-hub/vendor-platform-adapter/access-platform", title: "Access Platform" },
            { icon: "", index: "/integration-hub/vendor-platform-adapter/bms-platform", title: "BMS Platform" }
          ],
          icon: "", index: "/integration-hub/vendor-platform-adapter", title: "Vendor Platform Adapter"
        },
        {
          children: [
            { icon: "", index: "/integration-hub/protocol-health-check/connectivity-test", title: "Connectivity Test" },
            { icon: "", index: "/integration-hub/protocol-health-check/point-read-test", title: "Point Read Test" },
            { icon: "", index: "/integration-hub/protocol-health-check/command-write-test", title: "Command Write Test" },
            { icon: "", index: "/integration-hub/protocol-health-check/latency-test", title: "Latency Test" },
            { icon: "", index: "/integration-hub/protocol-health-check/baseline-comparison", title: "Baseline Comparison" },
            { icon: "", index: "/integration-hub/protocol-health-check/health-reports", title: "Health Reports" }
          ],
          icon: "", index: "/integration-hub/protocol-health-check", title: "Protocol Health Check"
        },
        {
          children: [
            { icon: "", index: "/integration-hub/compatibility-center/firmware-matrix", title: "Firmware Matrix" },
            { icon: "", index: "/integration-hub/compatibility-center/driver-matrix", title: "Driver Matrix" },
            { icon: "", index: "/integration-hub/compatibility-center/protocol-matrix", title: "Protocol Matrix" },
            { icon: "", index: "/integration-hub/compatibility-center/upgrade-assessment", title: "Upgrade Assessment" },
            { icon: "", index: "/integration-hub/compatibility-center/rollback-center", title: "Rollback Center" }
          ],
          icon: "", index: "/integration-hub/compatibility-center", title: "Compatibility Center"
        },
        {
          children: [
            { icon: "", index: "/integration-hub/security-monitoring/unknown-device-detection", title: "Unknown Device Detection" },
            { icon: "", index: "/integration-hub/security-monitoring/protocol-attack-detection", title: "Protocol Attack Detection" },
            { icon: "", index: "/integration-hub/security-monitoring/abnormal-command-detection", title: "Abnormal Command Detection" },
            { icon: "", index: "/integration-hub/security-monitoring/auto-isolation", title: "Auto Isolation" }
          ],
          icon: "", index: "/integration-hub/security-monitoring", title: "Security Monitoring"
        },
        { icon: "", index: "/integration-hub/device-drift-detection", title: "Device Drift Detection" },
        { icon: "", index: "/integration-hub/api-management", title: "API Management" },
        { icon: "", index: "/integration-hub/webhook-services", title: "Webhook Services" },
        { icon: "", index: "/integration-hub/connector-marketplace", title: "Connector Marketplace" },
        { icon: "", index: "/integration-hub/integration-monitoring", title: "Integration Monitoring" }
      ],
      icon: "Connection", index: "/integration-hub", title: "Integration Hub"
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
        { icon: "", index: "/intelligence/ai-assistant", title: "AI Assistant" },
        {
          children: [
            { icon: "", index: "/intelligence/predictive-maintenance/equipment-health", title: "Equipment Health" },
            { icon: "", index: "/intelligence/predictive-maintenance/failure-prediction", title: "Failure Prediction" },
            { icon: "", index: "/intelligence/predictive-maintenance/maintenance-recommendation", title: "Maintenance Recommendation" },
            { icon: "", index: "/intelligence/predictive-maintenance/risk-ranking", title: "Risk Ranking" }
          ],
          icon: "", index: "/intelligence/predictive-maintenance", title: "Predictive Maintenance"
        },
        {
          children: [
            { icon: "", index: "/intelligence/fault-diagnostics/root-cause-analysis", title: "Root Cause Analysis" },
            { icon: "", index: "/intelligence/fault-diagnostics/similar-fault-search", title: "Similar Fault Search" },
            { icon: "", index: "/intelligence/fault-diagnostics/fault-correlation", title: "Fault Correlation" },
            { icon: "", index: "/intelligence/fault-diagnostics/ai-diagnostic-workflow", title: "AI Diagnostic Workflow" }
          ],
          icon: "", index: "/intelligence/fault-diagnostics", title: "Fault Diagnostics"
        },
        {
          children: [
            { icon: "", index: "/intelligence/energy-optimization/hvac-optimization", title: "HVAC Optimization" },
            { icon: "", index: "/intelligence/energy-optimization/lighting-optimization", title: "Lighting Optimization" },
            { icon: "", index: "/intelligence/energy-optimization/demand-response", title: "Demand Response" },
            { icon: "", index: "/intelligence/energy-optimization/carbon-optimization", title: "Carbon Optimization" },
            { icon: "", index: "/intelligence/energy-optimization/utility-cost-optimization", title: "Utility Cost Optimization" }
          ],
          icon: "", index: "/intelligence/energy-optimization", title: "Energy Optimization"
        },
        { icon: "", index: "/intelligence/occupancy-intelligence", title: "Occupancy Intelligence" },
        { icon: "", index: "/intelligence/recommendation-center-ai", title: "Recommendation Center" },
        { icon: "", index: "/intelligence/knowledge-graph", title: "Knowledge Graph" },
        { icon: "", index: "/intelligence/digital-operator", title: "Digital Operator" },
        {
          children: [
            { icon: "", index: "/intelligence/ai-governance/ai-policies", title: "AI Policies" },
            { icon: "", index: "/intelligence/ai-governance/model-registry", title: "Model Registry" },
            { icon: "", index: "/intelligence/ai-governance/prompt-management", title: "Prompt Management" },
            { icon: "", index: "/intelligence/ai-governance/approval-rules", title: "Approval Rules" },
            { icon: "", index: "/intelligence/ai-governance/ai-audit-logs", title: "AI Audit Logs" }
          ],
          icon: "", index: "/intelligence/ai-governance", title: "AI Governance"
        }
      ],
      icon: "Cpu", index: "/intelligence", title: "Intelligence"
    },
    {
      children: [
        {
          children: [
            { icon: "", index: "/ai-video-analytics/ppe-compliance/helmet-detection", title: "Helmet Detection" },
            { icon: "", index: "/ai-video-analytics/ppe-compliance/safety-vest-detection", title: "Safety Vest Detection" },
            { icon: "", index: "/ai-video-analytics/ppe-compliance/gloves-detection", title: "Gloves Detection" },
            { icon: "", index: "/ai-video-analytics/ppe-compliance/goggles-detection", title: "Goggles Detection" },
            { icon: "", index: "/ai-video-analytics/ppe-compliance/ppe-reports", title: "PPE Reports" }
          ],
          icon: "", index: "/ai-video-analytics/ppe-compliance", title: "PPE Compliance"
        },
        {
          children: [
            { icon: "", index: "/ai-video-analytics/safety-monitoring/fall-detection", title: "Fall Detection" },
            { icon: "", index: "/ai-video-analytics/safety-monitoring/intrusion-detection", title: "Intrusion Detection" },
            { icon: "", index: "/ai-video-analytics/safety-monitoring/smoke-detection", title: "Smoke Detection" },
            { icon: "", index: "/ai-video-analytics/safety-monitoring/fire-detection", title: "Fire Detection" },
            { icon: "", index: "/ai-video-analytics/safety-monitoring/restricted-area-detection", title: "Restricted Area Detection" },
            { icon: "", index: "/ai-video-analytics/safety-monitoring/loitering-detection", title: "Loitering Detection" }
          ],
          icon: "", index: "/ai-video-analytics/safety-monitoring", title: "Safety Monitoring"
        },
        {
          children: [
            { icon: "", index: "/ai-video-analytics/vehicle-analytics/anpr", title: "ANPR" },
            { icon: "", index: "/ai-video-analytics/vehicle-analytics/illegal-parking", title: "Illegal Parking" },
            { icon: "", index: "/ai-video-analytics/vehicle-analytics/vehicle-counting", title: "Vehicle Counting" },
            { icon: "", index: "/ai-video-analytics/vehicle-analytics/vehicle-tracking", title: "Vehicle Tracking" },
            { icon: "", index: "/ai-video-analytics/vehicle-analytics/fleet-analytics", title: "Fleet Analytics" }
          ],
          icon: "", index: "/ai-video-analytics/vehicle-analytics", title: "Vehicle Analytics"
        },
        {
          children: [
            { icon: "", index: "/ai-video-analytics/crowd-analytics/occupancy-counting", title: "Occupancy Counting" },
            { icon: "", index: "/ai-video-analytics/crowd-analytics/queue-detection", title: "Queue Detection" },
            { icon: "", index: "/ai-video-analytics/crowd-analytics/density-monitoring", title: "Density Monitoring" },
            { icon: "", index: "/ai-video-analytics/crowd-analytics/flow-analytics", title: "Flow Analytics" }
          ],
          icon: "", index: "/ai-video-analytics/crowd-analytics", title: "Crowd Analytics"
        },
        { icon: "", index: "/ai-video-analytics/behavioral-analytics", title: "Behavioral Analytics" },
        { icon: "", index: "/ai-video-analytics/video-event-center", title: "Video Event Center" },
        { icon: "", index: "/ai-video-analytics/ai-evidence-repository", title: "AI Evidence Repository" },
        { icon: "", index: "/ai-video-analytics/video-health-monitoring", title: "Video Health Monitoring" }
      ],
      icon: "Camera", index: "/ai-video-analytics", title: "AI Video Analytics"
    },
    {
      children: [
        {
          children: [
            { icon: "", index: "/digital-twin-openbim/bim-management/ifc-import", title: "IFC Import" },
            { icon: "", index: "/digital-twin-openbim/bim-management/cobie-import", title: "COBie Import" },
            { icon: "", index: "/digital-twin-openbim/bim-management/bcf-issues", title: "BCF Issues" },
            { icon: "", index: "/digital-twin-openbim/bim-management/model-validation", title: "Model Validation" },
            { icon: "", index: "/digital-twin-openbim/bim-management/model-federation", title: "Model Federation" }
          ],
          icon: "", index: "/digital-twin-openbim/bim-management", title: "BIM Management"
        },
        { icon: "", index: "/digital-twin-openbim/asset-localization", title: "Asset Localization" },
        { icon: "", index: "/digital-twin-openbim/3d-navigation", title: "3D Navigation" },
        { icon: "", index: "/digital-twin-openbim/real-time-twin", title: "Real-Time Twin" },
        { icon: "", index: "/digital-twin-openbim/scenario-simulation", title: "Scenario Simulation" },
        { icon: "", index: "/digital-twin-openbim/energy-simulation", title: "Energy Simulation" },
        { icon: "", index: "/digital-twin-openbim/emergency-simulation", title: "Emergency Simulation" },
        { icon: "", index: "/digital-twin-openbim/twin-analytics", title: "Twin Analytics" },
        {
          children: [
            { icon: "", index: "/digital-twin-openbim/openbim-integration/ifc-mapping", title: "IFC Mapping" },
            { icon: "", index: "/digital-twin-openbim/openbim-integration/cobie-mapping", title: "COBie Mapping" },
            { icon: "", index: "/digital-twin-openbim/openbim-integration/bsdd-dictionary", title: "bSDD Dictionary" },
            { icon: "", index: "/digital-twin-openbim/openbim-integration/iso19650-cde-link", title: "ISO19650 CDE Link" }
          ],
          icon: "", index: "/digital-twin-openbim/openbim-integration", title: "OpenBIM Integration"
        },
        { icon: "", index: "/digital-twin-openbim/digital-construction", title: "Digital Construction" }
      ],
      icon: "Share", index: "/digital-twin-openbim", title: "Digital Twin & OpenBIM"
    },
    {
      children: [
        { icon: "", index: "/trust-identity/did-identity-center", title: "DID Identity Center" },
        {
          children: [
            { icon: "", index: "/trust-identity/credential-center/issue-vc", title: "Issue VC" },
            { icon: "", index: "/trust-identity/credential-center/verify-vc", title: "Verify VC" },
            { icon: "", index: "/trust-identity/credential-center/revoke-vc", title: "Revoke VC" },
            { icon: "", index: "/trust-identity/credential-center/credential-templates", title: "Credential Templates" }
          ],
          icon: "", index: "/trust-identity/credential-center", title: "Credential Center"
        },
        {
          children: [
            { icon: "", index: "/trust-identity/blockchain-anchoring/evidence-anchor", title: "Evidence Anchor" },
            { icon: "", index: "/trust-identity/blockchain-anchoring/decision-anchor", title: "Decision Anchor" },
            { icon: "", index: "/trust-identity/blockchain-anchoring/esg-anchor", title: "ESG Anchor" },
            { icon: "", index: "/trust-identity/blockchain-anchoring/credential-anchor", title: "Credential Anchor" }
          ],
          icon: "", index: "/trust-identity/blockchain-anchoring", title: "Blockchain Anchoring"
        },
        { icon: "", index: "/trust-identity/smart-contracts", title: "Smart Contracts" },
        { icon: "", index: "/trust-identity/decision-traceability", title: "Decision Traceability" },
        { icon: "", index: "/trust-identity/evidence-chain", title: "Evidence Chain" },
        { icon: "", index: "/trust-identity/compliance-certificates", title: "Compliance Certificates" },
        { icon: "", index: "/trust-identity/trust-audit-logs", title: "Trust Audit Logs" }
      ],
      icon: "Key", index: "/trust-identity", title: "Trust & Identity"
    },
    {
      children: [
        {
          children: [
            { icon: "", index: "/operational-assistance/device-discovery/bacnet-scan", title: "BACnet Scan" },
            { icon: "", index: "/operational-assistance/device-discovery/modbus-scan", title: "Modbus Scan" },
            { icon: "", index: "/operational-assistance/device-discovery/onvif-scan", title: "ONVIF Scan" },
            { icon: "", index: "/operational-assistance/device-discovery/snmp-scan", title: "SNMP Scan" },
            { icon: "", index: "/operational-assistance/device-discovery/mqtt-discovery", title: "MQTT Discovery" },
            { icon: "", index: "/operational-assistance/device-discovery/custom-device-discovery", title: "Custom Device Discovery" }
          ],
          icon: "", index: "/operational-assistance/device-discovery", title: "Device Discovery"
        },
        {
          children: [
            { icon: "", index: "/operational-assistance/commissioning-center/device-commissioning", title: "Device Commissioning" },
            { icon: "", index: "/operational-assistance/commissioning-center/point-verification", title: "Point Verification" },
            { icon: "", index: "/operational-assistance/commissioning-center/loop-check", title: "Loop Check" },
            { icon: "", index: "/operational-assistance/commissioning-center/command-test", title: "Command Test" },
            { icon: "", index: "/operational-assistance/commissioning-center/protocol-validation", title: "Protocol Validation" },
            { icon: "", index: "/operational-assistance/commissioning-center/commissioning-report", title: "Commissioning Report" }
          ],
          icon: "", index: "/operational-assistance/commissioning-center", title: "Commissioning Center"
        },
        {
          children: [
            { icon: "", index: "/operational-assistance/diagnostic-center/protocol-diagnostics", title: "Protocol Diagnostics" },
            { icon: "", index: "/operational-assistance/diagnostic-center/device-diagnostics", title: "Device Diagnostics" },
            { icon: "", index: "/operational-assistance/diagnostic-center/network-diagnostics", title: "Network Diagnostics" },
            { icon: "", index: "/operational-assistance/diagnostic-center/fault-diagnostics", title: "Fault Diagnostics" },
            { icon: "", index: "/operational-assistance/diagnostic-center/ai-diagnostics", title: "AI Diagnostics" }
          ],
          icon: "", index: "/operational-assistance/diagnostic-center", title: "Diagnostic Center"
        },
        { icon: "", index: "/operational-assistance/knowledge-base", title: "Knowledge Base" },
        { icon: "", index: "/operational-assistance/ai-qa-assistant", title: "AI Q&A Assistant" },
        { icon: "", index: "/operational-assistance/training-center", title: "Training Center" },
        {
          children: [
            { icon: "", index: "/operational-assistance/mobile-operations/mobile-worker-app", title: "Mobile Worker App" },
            { icon: "", index: "/operational-assistance/mobile-operations/qr-scan", title: "QR Scan" },
            { icon: "", index: "/operational-assistance/mobile-operations/voice-input", title: "Voice Input" },
            { icon: "", index: "/operational-assistance/mobile-operations/offline-sync", title: "Offline Sync" },
            { icon: "", index: "/operational-assistance/mobile-operations/push-notifications", title: "Push Notifications" }
          ],
          icon: "", index: "/operational-assistance/mobile-operations", title: "Mobile Operations"
        },
        { icon: "", index: "/operational-assistance/tablet-engineering-console", title: "Tablet Engineering Console" },
        { icon: "", index: "/operational-assistance/on-site-terminal", title: "On-Site Terminal" }
      ],
      icon: "Headset", index: "/operational-assistance", title: "Operational Assistance"
    },
    {
      children: [
        { icon: "", index: "/security-compliance/cybersecurity-dashboard", title: "Cybersecurity Dashboard" },
        { icon: "", index: "/security-compliance/iec62443-compliance", title: "IEC62443 Compliance" },
        { icon: "", index: "/security-compliance/iso27001-compliance", title: "ISO27001 Compliance" },
        { icon: "", index: "/security-compliance/nist-framework", title: "NIST Framework" },
        { icon: "", index: "/security-compliance/security-monitor", title: "Security Monitoring" },
        { icon: "", index: "/security-compliance/threat-detection", title: "Threat Detection" },
        { icon: "", index: "/security-compliance/vulnerability-management", title: "Vulnerability Management" },
        { icon: "", index: "/security-compliance/device-security", title: "Device Security" },
        { icon: "", index: "/security-compliance/command-security", title: "Command Security" },
        { icon: "", index: "/security-compliance/audit-management", title: "Audit Management" },
        { icon: "", index: "/security-compliance/compliance-reports", title: "Compliance Reports" }
      ],
      icon: "Lock", index: "/security-compliance", title: "Security & Compliance"
    },
    {
      children: [
        { icon: "", index: "/developer-center/api-gateway", title: "API Gateway" },
        { icon: "", index: "/developer-center/api-documentation", title: "API Documentation" },
        { icon: "", index: "/developer-center/sdk-management", title: "SDK Management" },
        { icon: "", index: "/developer-center/protocol-registry", title: "Protocol Registry" },
        { icon: "", index: "/developer-center/device-templates", title: "Device Templates" },
        { icon: "", index: "/developer-center/driver-marketplace", title: "Driver Marketplace" },
        { icon: "", index: "/developer-center/integration-sandbox", title: "Integration Sandbox" },
        { icon: "", index: "/developer-center/webhook-management", title: "Webhook Management" },
        { icon: "", index: "/developer-center/feature-toggle-registry", title: "Feature Toggle Registry" },
        { icon: "", index: "/developer-center/system-health-api", title: "System Health API" }
      ],
      icon: "Monitor", index: "/developer-center", title: "Developer Center"
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