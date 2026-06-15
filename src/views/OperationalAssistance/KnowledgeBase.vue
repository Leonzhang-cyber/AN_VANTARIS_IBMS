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
          <span class="loading-title">Loading Knowledge Base</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
        <div class="loading-subtip">IBMS Knowledge Management System</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="knowledge-base-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <h2 class="page-title">Knowledge Base</h2>
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/' }">Home</el-breadcrumb-item>
          <el-breadcrumb-item>Operational Assistance</el-breadcrumb-item>
          <el-breadcrumb-item>Knowledge Base</el-breadcrumb-item>
        </el-breadcrumb>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="handleCreateArticle">
          <el-icon><Plus /></el-icon>
          Create Article
        </el-button>
      </div>
    </div>

    <!-- Statistics Cards -->
    <div class="stats-grid">
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-info">
            <div class="stat-label">Total Documents</div>
            <div class="stat-value">{{ stats.totalDocs }}</div>
            <div class="stat-trend positive">+{{ stats.docGrowth }} this week</div>
          </div>
          <div class="stat-icon">
            <el-icon :size="40"><Document /></el-icon>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-info">
            <div class="stat-label">Total Views</div>
            <div class="stat-value">{{ stats.totalViews }}</div>
            <div class="stat-trend positive">+{{ stats.viewGrowth }}%</div>
          </div>
          <div class="stat-icon">
            <el-icon :size="40"><View /></el-icon>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-info">
            <div class="stat-label">Categories</div>
            <div class="stat-value">{{ stats.categories }}</div>
            <div class="stat-trend">{{ stats.activeCategories }} active</div>
          </div>
          <div class="stat-icon">
            <el-icon :size="40"><Folder /></el-icon>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-info">
            <div class="stat-label">Contributors</div>
            <div class="stat-value">{{ stats.contributors }}</div>
            <div class="stat-trend">+{{ stats.newContributors }} new</div>
          </div>
          <div class="stat-icon">
            <el-icon :size="40"><User /></el-icon>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Search and Filter Section -->
    <el-card class="search-card" shadow="never">
      <div class="search-section">
        <el-input
            v-model="searchKeyword"
            placeholder="Search knowledge base..."
            clearable
            size="large"
            class="search-input"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-select v-model="selectedCategory" placeholder="All Categories" clearable size="large" class="category-select">
          <el-option label="All Categories" value="" />
          <el-option label="Device Troubleshooting" value="troubleshooting" />
          <el-option label="Maintenance Guides" value="maintenance" />
          <el-option label="System Configuration" value="configuration" />
          <el-option label="Safety Protocols" value="safety" />
          <el-option label="SOP Documents" value="sop" />
          <el-option label="Video Tutorials" value="video" />
        </el-select>
        <el-button type="primary" size="large" @click="handleSearch">
          <el-icon><Search /></el-icon>
          Search
        </el-button>
      </div>
    </el-card>

    <!-- Knowledge Stats Chart -->
    <el-card class="chart-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Knowledge Usage Analytics</span>
          <el-button text type="primary" @click="refreshChart">Refresh</el-button>
        </div>
      </template>
      <div ref="chartRef" class="chart-container"></div>
    </el-card>

    <!-- Knowledge Categories Grid -->
    <div class="categories-section">
      <h3 class="section-title">Knowledge Categories</h3>
      <div class="categories-grid">
        <div v-for="category in categories" :key="category.name" class="category-card" @click="filterByCategory(category.name)">
          <div class="category-icon" :style="{ backgroundColor: category.color }">
            <el-icon :size="28"><component :is="category.icon" /></el-icon>
          </div>
          <div class="category-info">
            <h4>{{ category.name }}</h4>
            <p>{{ category.count }} articles</p>
          </div>
          <el-icon class="category-arrow"><ArrowRight /></el-icon>
        </div>
      </div>
    </div>

    <!-- Popular and Recent Articles -->
    <div class="articles-grid">
      <!-- Popular Articles -->
      <el-card class="articles-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span><el-icon><Star /></el-icon> Most Popular</span>
            <el-button text type="primary">View All</el-button>
          </div>
        </template>
        <div class="articles-list">
          <div v-for="article in popularArticles" :key="article.id" class="article-item" @click="viewArticle(article)">
            <div class="article-info">
              <div class="article-title">{{ article.title }}</div>
              <div class="article-meta">
                <span><el-icon><View /></el-icon> {{ article.views }} views</span>
                <span><el-icon><Clock /></el-icon> {{ article.date }}</span>
                <span class="article-category">{{ article.category }}</span>
              </div>
            </div>
            <el-icon class="article-arrow"><ArrowRight /></el-icon>
          </div>
        </div>
      </el-card>

      <!-- Recent Articles -->
      <el-card class="articles-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span><el-icon><Timer /></el-icon> Recently Updated</span>
            <el-button text type="primary">View All</el-button>
          </div>
        </template>
        <div class="articles-list">
          <div v-for="article in recentArticles" :key="article.id" class="article-item" @click="viewArticle(article)">
            <div class="article-info">
              <div class="article-title">{{ article.title }}</div>
              <div class="article-meta">
                <span><el-icon><User /></el-icon> {{ article.author }}</span>
                <span><el-icon><Clock /></el-icon> {{ article.updatedAt }}</span>
              </div>
            </div>
            <el-icon class="article-arrow"><ArrowRight /></el-icon>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Quick Actions -->
    <el-card class="quick-actions-card" shadow="never">
      <div class="quick-actions">
        <div class="quick-action-item" @click="handleCreateArticle">
          <el-icon :size="24"><Plus /></el-icon>
          <span>New Article</span>
        </div>
        <div class="quick-action-item" @click="handleUploadDocument">
          <el-icon :size="24"><Upload /></el-icon>
          <span>Upload Document</span>
        </div>
        <div class="quick-action-item" @click="handleExportData">
          <el-icon :size="24"><Download /></el-icon>
          <span>Export Knowledge Base</span>
        </div>
        <div class="quick-action-item" @click="handleGenerateReport">
          <el-icon :size="24"><DataAnalysis /></el-icon>
          <span>Generate Report</span>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  Plus, Document, View, Folder, User, Search, ArrowRight, Star, Clock, Timer, Upload, Download, DataAnalysis
} from '@element-plus/icons-vue'

// Loading state
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing Knowledge Base...')

const loadingMessages = [
  'Preparing Knowledge Base...',
  'Loading articles and documents...',
  'Indexing content...',
  'Almost ready...'
]

// Statistics data
const stats = ref({
  totalDocs: 342,
  docGrowth: 12,
  totalViews: 15842,
  viewGrowth: 8.5,
  categories: 8,
  activeCategories: 6,
  contributors: 24,
  newContributors: 3
})

// Search and filter
const searchKeyword = ref('')
const selectedCategory = ref('')

// Chart reference
const chartRef = ref<HTMLElement>()

// Categories data
const categories = ref([
  { name: 'Device Troubleshooting', icon: 'Tools', count: 86, color: '#3b82f6' },
  { name: 'Maintenance Guides', icon: 'Setting', count: 54, color: '#10b981' },
  { name: 'System Configuration', icon: 'Cpu', count: 42, color: '#8b5cf6' },
  { name: 'Safety Protocols', icon: 'Warning', count: 38, color: '#ef4444' },
  { name: 'SOP Documents', icon: 'Document', count: 67, color: '#f59e0b' },
  { name: 'Video Tutorials', icon: 'VideoCamera', count: 23, color: '#ec489a' },
  { name: 'FAQs', icon: 'ChatDotRound', count: 45, color: '#06b6d4' },
  { name: 'Best Practices', icon: 'Medal', count: 31, color: '#84cc16' }
])

// Popular articles
const popularArticles = ref([
  { id: 1, title: 'HVAC System Troubleshooting Guide', views: 1245, date: '2024-01-15', category: 'Troubleshooting' },
  { id: 2, title: 'BACnet Integration Best Practices', views: 987, date: '2024-01-10', category: 'Configuration' },
  { id: 3, title: 'Preventive Maintenance Schedule Template', views: 876, date: '2024-01-08', category: 'Maintenance' },
  { id: 4, title: 'Energy Optimization Techniques', views: 765, date: '2024-01-05', category: 'Best Practices' },
  { id: 5, title: 'Emergency Response Protocol', views: 654, date: '2024-01-03', category: 'Safety' }
])

// Recent articles
const recentArticles = ref([
  { id: 101, title: 'New Modbus Integration Setup Guide', author: 'John Smith', updatedAt: '2024-01-14' },
  { id: 102, title: 'Chiller Efficiency Optimization', author: 'Sarah Chen', updatedAt: '2024-01-13' },
  { id: 103, title: 'Fire Alarm System Maintenance', author: 'Mike Johnson', updatedAt: '2024-01-12' },
  { id: 104, title: 'Dashboard Customization Tutorial', author: 'Emma Wilson', updatedAt: '2024-01-11' },
  { id: 105, title: 'AI Insights Usage Guide', author: 'David Kim', updatedAt: '2024-01-10' }
])

// Initialize chart
const initChart = () => {
  if (!chartRef.value) return

  const chart = echarts.init(chartRef.value)
  const option = {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', data: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'] },
    yAxis: { type: 'value', name: 'Article Views (K)' },
    series: [
      {
        name: 'Knowledge Views',
        type: 'line',
        smooth: true,
        data: [12, 15, 18, 22, 28, 35, 42, 48, 52, 58, 65, 72],
        lineStyle: { width: 3, color: '#3b82f6' },
        areaStyle: { opacity: 0.3, color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#3b82f6' }, { offset: 1, color: '#93c5fd' }
          ]) },
        symbol: 'circle',
        symbolSize: 8,
        itemStyle: { color: '#3b82f6', borderColor: '#fff', borderWidth: 2 }
      },
      {
        name: 'New Articles',
        type: 'bar',
        barWidth: '30%',
        data: [8, 10, 12, 15, 18, 22, 25, 28, 30, 32, 35, 38],
        itemStyle: { borderRadius: [4, 4, 0, 0], color: '#10b981' }
      }
    ],
    legend: { top: 0, right: 0, itemWidth: 25, itemHeight: 14 },
    color: ['#3b82f6', '#10b981']
  }
  chart.setOption(option)
  window.addEventListener('resize', () => chart.resize())
}

const refreshChart = () => {
  initChart()
  ElMessage.success('Chart refreshed successfully')
}

// Event handlers
const handleCreateArticle = () => {
  ElMessage.info('Create article feature will be available soon')
}

const handleUploadDocument = () => {
  ElMessage.info('Document upload feature will be available soon')
}

const handleExportData = () => {
  ElMessage.info('Export feature will be available soon')
}

const handleGenerateReport = () => {
  ElMessage.info('Report generation feature will be available soon')
}

const handleSearch = () => {
  ElMessage.info(`Searching for: ${searchKeyword.value} in category: ${selectedCategory.value || 'All'}`)
}

const filterByCategory = (categoryName: string) => {
  selectedCategory.value = categoryName
  handleSearch()
}

const viewArticle = (article: any) => {
  ElMessage.info(`Opening article: ${article.title}`)
}

// Loading animation
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
      setTimeout(() => {
        initChart()
      }, 100)
    }, 400)
  }, 2500)
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
  font-size: 24px;
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

/* ==================== Main Content Styles ==================== */
.knowledge-base-container {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 8px 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  border-radius: 12px;
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.stat-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-info {
  flex: 1;
}

.stat-label {
  font-size: 14px;
  color: #64748b;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 4px;
}

.stat-trend {
  font-size: 12px;
}

.stat-trend.positive {
  color: #10b981;
}

.stat-trend.negative {
  color: #ef4444;
}

.stat-icon {
  color: #cbd5e1;
}

.search-card {
  margin-bottom: 24px;
  border-radius: 12px;
}

.search-section {
  display: flex;
  gap: 16px;
  align-items: center;
}

.search-input {
  flex: 1;
}

.category-select {
  width: 200px;
}

.chart-card {
  margin-bottom: 24px;
  border-radius: 12px;
}

.chart-container {
  height: 350px;
  width: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  color: #1e293b;
}

.categories-section {
  margin-bottom: 32px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 16px;
}

.categories-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.category-card {
  display: flex;
  align-items: center;
  padding: 16px;
  background: white;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.category-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.category-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin-right: 12px;
}

.category-info {
  flex: 1;
}

.category-info h4 {
  margin: 0 0 4px 0;
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
}

.category-info p {
  margin: 0;
  font-size: 12px;
  color: #64748b;
}

.category-arrow {
  color: #cbd5e1;
}

.articles-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.articles-card {
  border-radius: 12px;
}

.articles-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.article-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
}

.article-item:hover {
  background: #f8fafc;
}

.article-info {
  flex: 1;
}

.article-title {
  font-size: 14px;
  font-weight: 500;
  color: #1e293b;
  margin-bottom: 8px;
}

.article-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #94a3b8;
}

.article-meta span {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.article-category {
  padding: 2px 8px;
  background: #e2e8f0;
  border-radius: 4px;
  color: #475569;
}

.article-arrow {
  color: #cbd5e1;
}

.quick-actions-card {
  border-radius: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.quick-actions {
  display: flex;
  justify-content: space-around;
  padding: 16px;
}

.quick-action-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: white;
  transition: transform 0.2s;
}

.quick-action-item:hover {
  transform: translateY(-2px);
}

.quick-action-item span {
  font-size: 14px;
}

/* Responsive */
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .categories-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .articles-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .search-section {
    flex-direction: column;
  }

  .search-input,
  .category-select {
    width: 100%;
  }

  .categories-grid {
    grid-template-columns: 1fr;
  }
}
</style>