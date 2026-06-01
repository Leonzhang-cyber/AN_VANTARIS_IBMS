<script setup lang="ts">
import { ref, onMounted, nextTick, watch, onUnmounted, computed } from 'vue'
import {
  Search, Document, Clock, View, Star,
  Collection, FolderOpened, Tickets,
  RefreshRight, Plus, Sort, Filter
} from "@element-plus/icons-vue"
import { ElMessage, ElMessageBox } from 'element-plus'

// Loading state
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading knowledge base...',
  'Indexing articles...',
  'Almost ready...'
]

// Search and filter
const searchKeyword = ref('')
const selectedCategory = ref('all')
const currentPage = ref(1)
const pageSize = ref(9)

// Categories
const categories = ref([
  { id: 'all', name: 'All Articles', icon: '📚', count: 48 },
  { id: 'hvac', name: 'HVAC Systems', icon: '❄️', count: 12 },
  { id: 'electrical', name: 'Electrical & Power', icon: '⚡', count: 10 },
  { id: 'plumbing', name: 'Plumbing', icon: '💧', count: 6 },
  { id: 'controls', name: 'Controls & BMS', icon: '🎮', count: 8 },
  { id: 'security', name: 'Security Systems', icon: '🔒', count: 5 },
  { id: 'network', name: 'Network & IT', icon: '🌐', count: 4 },
  { id: 'safety', name: 'Safety & Compliance', icon: '🛡️', count: 3 }
])

// Knowledge base articles
const articles = ref([
  {
    id: 'KB-001',
    title: 'AHU-03 Temperature Fluctuation - Troubleshooting Guide',
    category: 'hvac',
    categoryName: 'HVAC Systems',
    summary: 'Step-by-step guide to diagnose and resolve AHU temperature fluctuation issues including sensor calibration, valve actuator testing, and control loop tuning.',
    content: '## Overview\nAHU temperature fluctuation is a common issue that can be caused by multiple factors...\n\n## Symptoms\n- Temperature swings of 5°C or more\n- Frequent actuator movement\n- Unstable discharge air temperature\n\n## Root Causes\n1. Sensor drift or failure\n2. Stuck or slow valve actuator\n3. PID tuning issues\n4. Ductwork restrictions\n\n## Resolution Steps\n1. Verify sensor reading with independent thermometer\n2. Check actuator response time\n3. Review control loop parameters\n4. Inspect ductwork for obstructions',
    author: 'John Zhang',
    authorAvatar: 'JZ',
    createdAt: '2025-01-10',
    updatedAt: '2025-01-15',
    views: 245,
    likes: 32,
    tags: ['AHU', 'Temperature', 'Troubleshooting'],
    isFeatured: true,
    isPopular: true
  },
  {
    id: 'KB-002',
    title: 'UPS Battery Replacement Procedure',
    category: 'electrical',
    categoryName: 'Electrical & Power',
    summary: 'Standard operating procedure for UPS battery replacement including safety precautions, step-by-step instructions, and post-replacement testing.',
    content: '## Safety First\n- Always wear appropriate PPE\n- Ensure UPS is in maintenance bypass mode\n- Verify batteries are disconnected before handling\n\n## Required Tools\n- Insulated tools\n- Battery terminal cleaner\n- Torque wrench\n- Multimeter\n\n## Steps\n1. Put UPS into maintenance bypass\n2. Open battery cabinet\n3. Disconnect battery strings\n4. Remove old batteries\n5. Install new batteries\n6. Reconnect and torque terminals\n7. Close cabinet\n8. Take UPS out of bypass\n9. Perform capacity test',
    author: 'Sarah Li',
    authorAvatar: 'SL',
    createdAt: '2025-01-08',
    updatedAt: '2025-01-12',
    views: 189,
    likes: 28,
    tags: ['UPS', 'Battery', 'Procedure'],
    isFeatured: false,
    isPopular: true
  },
  {
    id: 'KB-003',
    title: 'BACnet Communication Troubleshooting',
    category: 'controls',
    categoryName: 'Controls & BMS',
    summary: 'Comprehensive guide to diagnosing BACnet communication issues including network scanning, device discovery, and point mapping verification.',
    content: '## BACnet Basics\nBACnet uses MSTP or IP for communication. Common issues include wiring problems, addressing conflicts, and configuration errors.\n\n## Diagnostic Steps\n1. Check physical connections\n2. Verify MAC addresses are unique\n3. Test baud rate compatibility\n4. Use BACnet scan tool\n5. Check device instance numbers\n6. Verify COV subscriptions\n\n## Common Error Codes\n- Error Code 17: Device unreachable\n- Error Code 19: Property not supported\n- Error Code 24: Invalid parameter\n\n## Resolution\nMost issues are resolved by proper termination, unique addressing, and correct baud rate settings.',
    author: 'Mike Wang',
    authorAvatar: 'MW',
    createdAt: '2025-01-05',
    updatedAt: '2025-01-14',
    views: 312,
    likes: 41,
    tags: ['BACnet', 'Communication', 'BMS'],
    isFeatured: true,
    isPopular: true
  },
  {
    id: 'KB-004',
    title: 'VFD Parameter Setting Guide',
    category: 'electrical',
    categoryName: 'Electrical & Power',
    summary: 'Recommended parameter settings for common VFD applications including pumps, fans, and compressors with troubleshooting tips.',
    content: '## Basic Parameters\n- Acceleration time: 10-30 seconds\n- Deceleration time: 10-30 seconds\n- Minimum frequency: 20 Hz\n- Maximum frequency: 60 Hz\n\n## Application Specific\n### Pumps\n- Ramp time: 20 seconds\n- Skip frequencies to avoid resonance\n\n### Fans\n- Ramp time: 30 seconds\n- Enable flying start\n\n### Compressors\n- Ramp time: 15 seconds\n- Enable torque boost\n\n## Troubleshooting\n- Overcurrent: Check acceleration time\n- Overvoltage: Check deceleration time\n- Motor overheating: Check V/Hz settings',
    author: 'David Sun',
    authorAvatar: 'DS',
    createdAt: '2025-01-03',
    updatedAt: '2025-01-10',
    views: 156,
    likes: 19,
    tags: ['VFD', 'Parameters', 'Setup'],
    isFeatured: false,
    isPopular: false
  },
  {
    id: 'KB-005',
    title: 'Chiller Efficiency Optimization',
    category: 'hvac',
    categoryName: 'HVAC Systems',
    summary: 'Best practices for optimizing chiller performance including setpoint adjustment, condenser water management, and sequencing strategies.',
    content: '## Optimization Strategies\n1. Raise chilled water setpoint when possible\n2. Maintain proper condenser water flow\n3. Use optimal sequencing based on load\n4. Monitor approach temperatures\n\n## Performance Metrics\n- COP > 5.0 for modern chillers\n- Approach temperature < 2°C\n- kW/ton < 0.7\n\n## Maintenance Tips\n- Regular tube cleaning\n- Monitor refrigerant levels\n- Check oil quality\n- Calibrate sensors annually',
    author: 'Emma Zhao',
    authorAvatar: 'EZ',
    createdAt: '2025-01-01',
    updatedAt: '2025-01-09',
    views: 278,
    likes: 35,
    tags: ['Chiller', 'Optimization', 'Energy'],
    isFeatured: true,
    isPopular: true
  },
  {
    id: 'KB-006',
    title: 'Access Control System Diagnostics',
    category: 'security',
    categoryName: 'Security Systems',
    summary: 'Diagnostic procedures for access control system issues including reader failures, controller communication, and credential problems.',
    content: '## Common Issues\n1. Reader not beeping\n2. Door not unlocking\n3. Request to exit not working\n4. Communication timeout\n\n## Diagnostic Steps\n- Check power supply voltage\n- Test reader LED patterns\n- Verify controller online status\n- Review event logs\n- Test with known good credential\n\n## Resolution\n- Replace faulty readers\n- Reset controllers\n- Update firmware\n- Check wiring connections',
    author: 'Anna Wu',
    authorAvatar: 'AW',
    createdAt: '2024-12-28',
    updatedAt: '2025-01-05',
    views: 134,
    likes: 17,
    tags: ['Access Control', 'Security', 'Diagnostics'],
    isFeatured: false,
    isPopular: false
  },
  {
    id: 'KB-007',
    title: 'Sensor Calibration Best Practices',
    category: 'controls',
    categoryName: 'Controls & BMS',
    summary: 'Guidelines for calibrating temperature, humidity, pressure, and flow sensors in building management systems.',
    content: '## Calibration Frequency\n- Temperature: Annually\n- Humidity: Annually\n- Pressure: Semi-annually\n- Flow: Every 2 years\n\n## Equipment Needed\n- Reference standard (certified)\n- Calibration adapter\n- Multimeter\n- Communication tool\n\n## Procedure\n1. Isolate sensor from process\n2. Apply known reference value\n3. Record sensor reading\n4. Calculate offset\n5. Apply correction\n6. Verify accuracy\n\n## Documentation\n- Pre-calibration reading\n- Post-calibration reading\n- Offset applied\n- Date and technician\n- Next due date',
    author: 'Chris Liu',
    authorAvatar: 'CL',
    createdAt: '2024-12-25',
    updatedAt: '2025-01-02',
    views: 98,
    likes: 14,
    tags: ['Sensors', 'Calibration', 'BMS'],
    isFeatured: false,
    isPopular: false
  },
  {
    id: 'KB-008',
    title: 'Fire Alarm System Testing SOP',
    category: 'safety',
    categoryName: 'Safety & Compliance',
    summary: 'Standard operating procedure for monthly and annual fire alarm system testing including device testing, panel verification, and reporting.',
    content: '## Monthly Testing\n- Test one smoke detector per zone\n- Test one pull station\n- Verify strobe/horn operation\n- Check panel for trouble conditions\n- Review event logs\n\n## Annual Testing\n- Test ALL devices\n- Full panel functional test\n- Battery load test\n- Verify communication to monitoring\n- Generator transfer test\n\n## Documentation Requirements\n- Test date and time\n- Device locations tested\n- Pass/fail results\n- Repairs needed\n- Technician signature\n\n## Compliance Standards\n- NFPA 72\n- Local fire code\n- Insurance requirements',
    author: 'Rachel Guo',
    authorAvatar: 'RG',
    createdAt: '2024-12-20',
    updatedAt: '2024-12-28',
    views: 87,
    likes: 12,
    tags: ['Fire Alarm', 'Safety', 'SOP'],
    isFeatured: false,
    isPopular: false
  },
  {
    id: 'KB-009',
    title: 'Plumbing Leak Detection Methods',
    category: 'plumbing',
    categoryName: 'Plumbing',
    summary: 'Various methods for detecting and locating water leaks in commercial plumbing systems including acoustic detection, thermal imaging, and pressure testing.',
    content: '## Detection Methods\n- Acoustic listening\n- Thermal imaging\n- Moisture meters\n- Pressure decay test\n- Dye testing\n\n## Common Leak Locations\n- Pipe joints\n- Valve packing\n- Toilet flappers\n- Water heaters\n- Roof drains\n\n## Repair Procedures\n1. Isolate section\n2. Drain system\n3. Cut out damaged section\n4. Install new fitting\n5. Pressure test\n6. Document repair',
    author: 'Tom Chen',
    authorAvatar: 'TC',
    createdAt: '2024-12-18',
    updatedAt: '2024-12-22',
    views: 112,
    likes: 15,
    tags: ['Plumbing', 'Leak Detection', 'Maintenance'],
    isFeatured: false,
    isPopular: false
  },
  {
    id: 'KB-010',
    title: 'CRAC Unit Preventive Maintenance Checklist',
    category: 'hvac',
    categoryName: 'HVAC Systems',
    summary: 'Comprehensive preventive maintenance checklist for CRAC units including filters, belts, coils, drains, and control verification.',
    content: '## Monthly Tasks\n- Check/clean filters\n- Inspect belts for wear\n- Check condensate drain\n- Verify airflow\n- Log temperatures\n\n## Quarterly Tasks\n- Clean coils\n- Check refrigerant levels\n- Test safety controls\n- Inspect electrical connections\n- Calibrate sensors\n\n## Annual Tasks\n- Deep clean unit\n- Check all hardware\n- Test all alarms\n- Full performance test\n- Documentation review',
    author: 'John Zhang',
    authorAvatar: 'JZ',
    createdAt: '2024-12-15',
    updatedAt: '2024-12-20',
    views: 203,
    likes: 28,
    tags: ['CRAC', 'HVAC', 'Preventive Maintenance'],
    isFeatured: true,
    isPopular: true
  }
])

// Popular articles (most viewed)
const popularArticles = computed(() => {
  return [...articles.value]
      .sort((a, b) => b.views - a.views)
      .slice(0, 5)
})

// Recent articles
const recentArticles = computed(() => {
  return [...articles.value]
      .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
      .slice(0, 5)
})

// Featured articles
const featuredArticles = computed(() => {
  return articles.value.filter(a => a.isFeatured)
})

// Filtered articles based on search and category
const filteredArticles = computed(() => {
  let filtered = articles.value

  if (selectedCategory.value !== 'all') {
    filtered = filtered.filter(a => a.category === selectedCategory.value)
  }

  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    filtered = filtered.filter(a =>
        a.title.toLowerCase().includes(keyword) ||
        a.summary.toLowerCase().includes(keyword) ||
        a.tags.some(tag => tag.toLowerCase().includes(keyword))
    )
  }

  return filtered
})

// Paginated articles
const paginatedArticles = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredArticles.value.slice(start, end)
})

const totalPages = computed(() => {
  return Math.ceil(filteredArticles.value.length / pageSize.value)
})

const handleSizeChange = (val: number) => {
  pageSize.value = val
  currentPage.value = 1
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
}

const selectCategory = (categoryId: string) => {
  selectedCategory.value = categoryId
  currentPage.value = 1
}

const resetFilters = () => {
  searchKeyword.value = ''
  selectedCategory.value = 'all'
  currentPage.value = 1
}

// Article detail dialog
const detailVisible = ref(false)
const selectedArticle = ref<any>(null)

const viewArticle = (article: any) => {
  selectedArticle.value = article
  article.views++
  detailVisible.value = true
}

const likeArticle = (article: any) => {
  article.likes++
  ElMessage.success('Article added to favorites')
}

const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}

// Get initials for avatar
const getInitials = (name: string) => {
  return name.split(' ').map(n => n[0]).join('').toUpperCase()
}

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
    }, 400)
  }, 2000)
})
</script>

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
        <div class="loading-tip">Knowledge Base</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="knowledge-base">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h2>Knowledge Base</h2>
        <p class="subtitle">Troubleshooting guides, SOPs, and technical documentation</p>
      </div>
      <div class="header-actions">
        <el-input
            v-model="searchKeyword"
            placeholder="Search articles..."
            clearable
            style="width: 280px"
            :prefix-icon="Search"
        />
        <el-button type="primary">
          <el-icon><Plus /></el-icon> New Article
        </el-button>
      </div>
    </div>

    <!-- Stats Overview -->
    <div class="stats-row">
      <div class="stat-badge">
        <span class="stat-value">{{ articles.length }}</span>
        <span class="stat-label">Total Articles</span>
      </div>
      <div class="stat-badge">
        <span class="stat-value">{{ categories.reduce((sum, c) => sum + c.count, 0) }}</span>
        <span class="stat-label">Total Categories</span>
      </div>
      <div class="stat-badge">
        <span class="stat-value">{{ articles.reduce((sum, a) => sum + a.views, 0) }}</span>
        <span class="stat-label">Total Views</span>
      </div>
      <div class="stat-badge">
        <span class="stat-value">{{ articles.reduce((sum, a) => sum + a.likes, 0) }}</span>
        <span class="stat-label">Total Likes</span>
      </div>
    </div>

    <div class="main-layout">
      <!-- Sidebar - Categories -->
      <div class="sidebar">
        <el-card class="category-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Categories</span>
              <el-icon><FolderOpened /></el-icon>
            </div>
          </template>
          <div class="category-list">
            <div
                v-for="cat in categories"
                :key="cat.id"
                :class="['category-item', { active: selectedCategory === cat.id }]"
                @click="selectCategory(cat.id)"
            >
              <span class="category-icon">{{ cat.icon }}</span>
              <span class="category-name">{{ cat.name }}</span>
              <span class="category-count">{{ cat.count }}</span>
            </div>
          </div>
        </el-card>

        <el-card class="popular-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>🔥 Popular Articles</span>
              <el-icon><TrendCharts /></el-icon>
            </div>
          </template>
          <div class="popular-list">
            <div
                v-for="article in popularArticles"
                :key="article.id"
                class="popular-item"
                @click="viewArticle(article)"
            >
              <div class="popular-title">{{ article.title }}</div>
              <div class="popular-meta">
                <span><el-icon><View /></el-icon> {{ article.views }}</span>
                <span><el-icon><Star /></el-icon> {{ article.likes }}</span>
              </div>
            </div>
          </div>
        </el-card>

        <el-card class="recent-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>📅 Recently Added</span>
              <el-icon><Clock /></el-icon>
            </div>
          </template>
          <div class="recent-list">
            <div
                v-for="article in recentArticles"
                :key="article.id"
                class="recent-item"
                @click="viewArticle(article)"
            >
              <div class="recent-title">{{ article.title }}</div>
              <div class="recent-date">{{ formatDate(article.createdAt) }}</div>
            </div>
          </div>
        </el-card>
      </div>

      <!-- Main Content - Articles Grid -->
      <div class="articles-container">
        <!-- Featured Banner -->
        <div v-if="featuredArticles.length > 0 && selectedCategory === 'all' && !searchKeyword" class="featured-banner">
          <div class="featured-header">
            <span class="featured-icon">⭐</span>
            <span>Featured Articles</span>
          </div>
          <div class="featured-grid">
            <div
                v-for="article in featuredArticles.slice(0, 3)"
                :key="article.id"
                class="featured-card"
                @click="viewArticle(article)"
            >
              <div class="featured-tag">{{ article.categoryName }}</div>
              <div class="featured-title">{{ article.title }}</div>
              <div class="featured-summary">{{ article.summary.slice(0, 80) }}...</div>
              <div class="featured-footer">
                <span class="featured-author">{{ article.author }}</span>
                <span class="featured-views">{{ article.views }} views</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Articles Grid -->
        <div class="articles-header">
          <h3>
            <span v-if="selectedCategory !== 'all'">
              {{ categories.find(c => c.id === selectedCategory)?.name }}
            </span>
            <span v-else>All Articles</span>
            <span class="article-count">({{ filteredArticles.length }} results)</span>
          </h3>
          <el-button v-if="searchKeyword || selectedCategory !== 'all'" link @click="resetFilters">
            <el-icon><RefreshRight /></el-icon> Clear Filters
          </el-button>
        </div>

        <div v-if="filteredArticles.length === 0" class="empty-state">
          <el-empty description="No articles found matching your criteria">
            <el-button type="primary" @click="resetFilters">Clear Filters</el-button>
          </el-empty>
        </div>

        <div v-else class="articles-grid">
          <el-card
              v-for="article in paginatedArticles"
              :key="article.id"
              class="article-card"
              shadow="hover"
              @click="viewArticle(article)"
          >
            <div class="article-tags">
              <el-tag size="small" :type="article.isFeatured ? 'warning' : 'info'">
                {{ article.categoryName }}
              </el-tag>
              <el-tag v-if="article.isFeatured" size="small" type="danger">Featured</el-tag>
            </div>
            <div class="article-title">{{ article.title }}</div>
            <div class="article-summary">{{ article.summary.slice(0, 100) }}...</div>
            <div class="article-meta">
              <div class="author-info">
                <div class="author-avatar">{{ getInitials(article.author) }}</div>
                <span class="author-name">{{ article.author }}</span>
              </div>
              <div class="article-stats">
                <span><el-icon><View /></el-icon> {{ article.views }}</span>
                <span><el-icon><Star /></el-icon> {{ article.likes }}</span>
                <span><el-icon><Clock /></el-icon> {{ formatDate(article.updatedAt) }}</span>
              </div>
            </div>
          </el-card>
        </div>

        <!-- Pagination -->
        <div v-if="filteredArticles.length > 0" class="pagination-wrapper">
          <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :page-sizes="[9, 18, 27]"
              :total="filteredArticles.length"
              layout="total, sizes, prev, pager, next"
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
          />
        </div>
      </div>
    </div>

    <!-- Article Detail Dialog -->
    <el-dialog v-model="detailVisible" :title="selectedArticle?.title" width="800px" class="article-dialog">
      <div v-if="selectedArticle" class="article-detail">
        <div class="article-detail-header">
          <div class="article-detail-tags">
            <el-tag type="info">{{ selectedArticle.categoryName }}</el-tag>
            <el-tag v-for="tag in selectedArticle.tags" :key="tag" size="small" effect="plain">
              {{ tag }}
            </el-tag>
          </div>
          <div class="article-detail-meta">
            <div class="author-info-large">
              <div class="author-avatar-large">{{ getInitials(selectedArticle.author) }}</div>
              <div>
                <div class="author-name-large">{{ selectedArticle.author }}</div>
                <div class="article-date">Updated: {{ formatDate(selectedArticle.updatedAt) }}</div>
              </div>
            </div>
            <div class="article-stats-large">
              <span><el-icon><View /></el-icon> {{ selectedArticle.views }} views</span>
              <span><el-icon><Star /></el-icon> {{ selectedArticle.likes }} likes</span>
            </div>
          </div>
        </div>
        <div class="article-detail-content">
          <div class="markdown-content">
            <pre>{{ selectedArticle.content }}</pre>
          </div>
        </div>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="likeArticle(selectedArticle)">
            <el-icon><Star /></el-icon> Like ({{ selectedArticle?.likes }})
          </el-button>
          <el-button type="primary" @click="detailVisible = false">Close</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

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

/* ==================== Main Content ==================== */
.knowledge-base {
  padding: 24px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e9ecef 100%);
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.page-header h2 {
  margin: 0 0 4px 0;
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(135deg, #303133, #606266);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.subtitle {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

/* Stats Row */
.stats-row {
  display: flex;
  gap: 20px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.stat-badge {
  background: white;
  padding: 12px 24px;
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 24px;
  font-weight: 700;
  color: #303133;
}

.stat-label {
  font-size: 12px;
  color: #909399;
}

/* Main Layout */
.main-layout {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 24px;
}

/* Sidebar */
.sidebar {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.category-card,
.popular-card,
.recent-card {
  border-radius: 16px;
}

.category-card :deep(.el-card__body),
.popular-card :deep(.el-card__body),
.recent-card :deep(.el-card__body) {
  padding: 12px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.category-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.category-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.category-item:hover {
  background: #f0f2f5;
}

.category-item.active {
  background: linear-gradient(135deg, #e6f7ff, #f0f5ff);
  color: #409eff;
  font-weight: 500;
}

.category-icon {
  font-size: 20px;
}

.category-name {
  flex: 1;
  font-size: 14px;
}

.category-count {
  font-size: 12px;
  color: #909399;
}

.popular-list,
.recent-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.popular-item,
.recent-item {
  padding: 8px 0;
  cursor: pointer;
  transition: all 0.2s ease;
  border-bottom: 1px solid #f0f0f0;
}

.popular-item:hover,
.recent-item:hover {
  color: #409eff;
}

.popular-title,
.recent-title {
  font-size: 13px;
  font-weight: 500;
  margin-bottom: 4px;
}

.popular-meta {
  display: flex;
  gap: 12px;
  font-size: 11px;
  color: #909399;
}

.popular-meta .el-icon {
  font-size: 11px;
}

.recent-date {
  font-size: 10px;
  color: #c0c4cc;
}

/* Articles Container */
.articles-container {
  flex: 1;
}

/* Featured Banner */
.featured-banner {
  background: linear-gradient(135deg, #fff9e6, #fff5d9);
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 24px;
}

.featured-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 16px;
  margin-bottom: 16px;
}

.featured-icon {
  font-size: 20px;
}

.featured-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.featured-card {
  background: white;
  border-radius: 12px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.featured-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

.featured-tag {
  font-size: 11px;
  color: #e6a23c;
  margin-bottom: 8px;
}

.featured-title {
  font-weight: 600;
  font-size: 14px;
  margin-bottom: 8px;
  line-height: 1.4;
}

.featured-summary {
  font-size: 12px;
  color: #909399;
  margin-bottom: 12px;
  line-height: 1.4;
}

.featured-footer {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: #c0c4cc;
}

/* Articles Header */
.articles-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.articles-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.article-count {
  font-size: 14px;
  color: #909399;
  margin-left: 8px;
}

/* Articles Grid */
.articles-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

.article-card {
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.article-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
}

.article-card :deep(.el-card__body) {
  padding: 16px;
}

.article-tags {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.article-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 8px;
  line-height: 1.4;
  color: #303133;
}

.article-summary {
  font-size: 13px;
  color: #606266;
  line-height: 1.5;
  margin-bottom: 16px;
}

.article-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid #ebeef5;
}

.author-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.author-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
}

.author-name {
  font-size: 12px;
  color: #606266;
}

.article-stats {
  display: flex;
  gap: 12px;
  font-size: 11px;
  color: #909399;
}

.article-stats .el-icon {
  font-size: 11px;
}

/* Pagination */
.pagination-wrapper {
  margin-top: 24px;
  display: flex;
  justify-content: flex-end;
}

/* Article Dialog */
.article-dialog :deep(.el-dialog__body) {
  padding: 20px;
  max-height: 60vh;
  overflow-y: auto;
}

.article-detail-header {
  margin-bottom: 20px;
}

.article-detail-tags {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.article-detail-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #ebeef5;
}

.author-info-large {
  display: flex;
  align-items: center;
  gap: 12px;
}

.author-avatar-large {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: 600;
}

.author-name-large {
  font-weight: 600;
  font-size: 14px;
}

.article-date {
  font-size: 11px;
  color: #909399;
}

.article-stats-large {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: #909399;
}

.article-detail-content {
  margin-top: 20px;
}

.markdown-content pre {
  background: #f5f7fa;
  padding: 16px;
  border-radius: 8px;
  white-space: pre-wrap;
  font-family: monospace;
  font-size: 13px;
  line-height: 1.5;
  color: #303133;
}

.dialog-footer {
  display: flex;
  justify-content: space-between;
}

/* Empty State */
.empty-state {
  padding: 60px 20px;
  text-align: center;
  background: white;
  border-radius: 16px;
}

/* Responsive */
@media (max-width: 1024px) {
  .main-layout {
    grid-template-columns: 1fr;
  }

  .featured-grid {
    grid-template-columns: 1fr;
  }

  .articles-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .knowledge-base {
    padding: 16px;
  }

  .page-header {
    flex-direction: column;
    align-items: stretch;
  }

  .header-actions {
    flex-direction: column;
  }

  .header-actions .el-input,
  .header-actions .el-button {
    width: 100%;
  }

  .stats-row {
    justify-content: center;
  }
}
</style>