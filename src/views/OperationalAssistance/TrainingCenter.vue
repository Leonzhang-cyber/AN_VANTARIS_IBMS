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
          <span class="loading-title">Loading Training Center</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
        <div class="loading-subtip">IBMS Employee Training & Development Platform</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="training-center-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <h2 class="page-title">Training Center</h2>
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/' }">Home</el-breadcrumb-item>
          <el-breadcrumb-item>Operational Assistance</el-breadcrumb-item>
          <el-breadcrumb-item>Training Center</el-breadcrumb-item>
        </el-breadcrumb>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="handleCreateTraining">
          <el-icon><Plus /></el-icon>
          Create Training
        </el-button>
        <el-button type="info" plain @click="handleMyLearning">
          <el-icon><User /></el-icon>
          My Learning
        </el-button>
      </div>
    </div>

    <!-- Statistics Cards -->
    <div class="stats-grid">
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-info">
            <div class="stat-label">Total Courses</div>
            <div class="stat-value">{{ stats.totalCourses }}</div>
            <div class="stat-trend positive">+{{ stats.newCourses }} this month</div>
          </div>
          <div class="stat-icon">
            <el-icon :size="40"><Reading /></el-icon>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-info">
            <div class="stat-label">Active Learners</div>
            <div class="stat-value">{{ stats.activeLearners }}</div>
            <div class="stat-trend positive">+{{ stats.learnerGrowth }}%</div>
          </div>
          <div class="stat-icon">
            <el-icon :size="40"><UserFilled /></el-icon>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-info">
            <div class="stat-label">Completion Rate</div>
            <div class="stat-value">{{ stats.completionRate }}%</div>
            <div class="stat-trend positive">↑ {{ stats.rateGrowth }}%</div>
          </div>
          <div class="stat-icon">
            <el-icon :size="40"><CircleCheck /></el-icon>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-info">
            <div class="stat-label">Certifications</div>
            <div class="stat-value">{{ stats.certifications }}</div>
            <div class="stat-trend">+{{ stats.newCerts }} awarded</div>
          </div>
          <div class="stat-icon">
            <el-icon :size="40"><Medal /></el-icon>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Search and Filter Section -->
    <el-card class="search-card" shadow="never">
      <div class="search-section">
        <el-input
            v-model="searchKeyword"
            placeholder="Search courses, training programs, or certifications..."
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
          <el-option label="Technical Training" value="technical" />
          <el-option label="Safety & Compliance" value="safety" />
          <el-option label="Soft Skills" value="soft-skills" />
          <el-option label="Leadership" value="leadership" />
          <el-option label="ESG & Sustainability" value="esg" />
          <el-option label="Digital Transformation" value="digital" />
        </el-select>
        <el-select v-model="selectedLevel" placeholder="All Levels" clearable size="large" class="level-select">
          <el-option label="All Levels" value="" />
          <el-option label="Beginner" value="beginner" />
          <el-option label="Intermediate" value="intermediate" />
          <el-option label="Advanced" value="advanced" />
          <el-option label="Expert" value="expert" />
        </el-select>
        <el-button type="primary" size="large" @click="handleSearch">
          <el-icon><Search /></el-icon>
          Search
        </el-button>
      </div>
    </el-card>

    <!-- Training Progress Chart -->
    <el-card class="chart-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Training Progress Overview</span>
          <el-button text type="primary" @click="refreshChart">Refresh</el-button>
        </div>
      </template>
      <div ref="chartRef" class="chart-container"></div>
    </el-card>

    <!-- Featured Courses Section -->
    <div class="featured-section">
      <div class="section-header">
        <h3 class="section-title">Featured Courses</h3>
        <el-button text type="primary" @click="viewAllCourses">View All Courses</el-button>
      </div>
      <div class="courses-grid">
        <el-card v-for="course in featuredCourses" :key="course.id" class="course-card" shadow="hover" @click="viewCourse(course)">
          <div class="course-image" :style="{ backgroundImage: `url(${course.image})` }">
            <div class="course-level" :class="course.level">
              {{ course.level }}
            </div>
            <div class="course-duration">
              <el-icon><Clock /></el-icon> {{ course.duration }}
            </div>
          </div>
          <div class="course-info">
            <h4 class="course-title">{{ course.title }}</h4>
            <p class="course-description">{{ course.description }}</p>
            <div class="course-meta">
              <div class="course-instructor">
                <el-icon><User /></el-icon> {{ course.instructor }}
              </div>
              <div class="course-students">
                <el-icon><UserFilled /></el-icon> {{ course.students }} enrolled
              </div>
            </div>
            <div class="course-rating">
              <el-rate v-model="course.rating" disabled show-score text-color="#ff9900" score-template="({point})" />
            </div>
            <div class="course-progress" v-if="course.progress !== undefined">
              <el-progress :percentage="course.progress" :stroke-width="6" />
              <span class="progress-label">{{ course.progress }}% completed</span>
            </div>
            <el-button type="primary" plain class="enroll-btn">
              {{ course.enrolled ? 'Continue Learning' : 'Enroll Now' }}
            </el-button>
          </div>
        </el-card>
      </div>
    </div>

    <!-- Categories Section -->
    <div class="categories-section">
      <h3 class="section-title">Training Categories</h3>
      <div class="categories-grid">
        <div v-for="category in categories" :key="category.name" class="category-card" @click="filterByCategory(category.name)">
          <div class="category-icon" :style="{ backgroundColor: category.color }">
            <el-icon :size="32"><component :is="category.icon" /></el-icon>
          </div>
          <div class="category-info">
            <h4>{{ category.name }}</h4>
            <p>{{ category.count }} courses</p>
            <div class="category-progress">
              <el-progress :percentage="category.popularity" :show-text="false" :stroke-width="4" />
            </div>
          </div>
          <el-icon class="category-arrow"><ArrowRight /></el-icon>
        </div>
      </div>
    </div>

    <!-- Upcoming Trainings & Certifications -->
    <div class="trainings-grid">
      <!-- Upcoming Live Trainings -->
      <el-card class="trainings-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span><el-icon><Calendar /></el-icon> Upcoming Live Trainings</span>
            <el-button text type="primary" @click="viewAllTrainings">Schedule</el-button>
          </div>
        </template>
        <div class="trainings-list">
          <div v-for="training in upcomingTrainings" :key="training.id" class="training-item" @click="registerTraining(training)">
            <div class="training-date">
              <div class="date-day">{{ training.day }}</div>
              <div class="date-month">{{ training.month }}</div>
            </div>
            <div class="training-info">
              <div class="training-title">{{ training.title }}</div>
              <div class="training-meta">
                <span><el-icon><Trophy /></el-icon> {{ training.time }}</span>
                <span><el-icon><Location /></el-icon> {{ training.location }}</span>
              </div>
            </div>
            <el-button type="primary" size="small">Register</el-button>
          </div>
        </div>
      </el-card>

      <!-- Certifications -->
      <el-card class="certifications-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span><el-icon><Medal /></el-icon> Available Certifications</span>
            <el-button text type="primary" @click="viewAllCertifications">All Certifications</el-button>
          </div>
        </template>
        <div class="certifications-list">
          <div v-for="cert in certifications" :key="cert.id" class="cert-item" @click="viewCertification(cert)">
            <div class="cert-icon" :style="{ backgroundColor: cert.color }">
              <el-icon :size="24"><Medal /></el-icon>
            </div>
            <div class="cert-info">
              <div class="cert-title">{{ cert.title }}</div>
              <div class="cert-issuer">{{ cert.issuer }}</div>
            </div>
            <div class="cert-status">
              <el-tag v-if="cert.earned" type="success" size="small">Earned</el-tag>
              <el-tag v-else-if="cert.inProgress" type="warning" size="small">In Progress</el-tag>
              <el-button v-else type="primary" size="small" plain>Start</el-button>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Leaderboard -->
    <el-card class="leaderboard-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span><el-icon><Trophy /></el-icon> Learning Leaderboard</span>
          <el-select v-model="leaderboardPeriod" size="small" style="width: 120px">
            <el-option label="This Week" value="week" />
            <el-option label="This Month" value="month" />
            <el-option label="All Time" value="all" />
          </el-select>
        </div>
      </template>
      <div class="leaderboard">
        <div v-for="(learner, idx) in leaderboard" :key="learner.id" class="leaderboard-item">
          <div class="rank" :class="{ 'top-rank': idx < 3 }">{{ idx + 1 }}</div>
          <el-avatar :size="40" :src="learner.avatar" />
          <div class="learner-info">
            <div class="learner-name">{{ learner.name }}</div>
            <div class="learner-dept">{{ learner.department }}</div>
          </div>
          <div class="learner-stats">
            <div class="points">{{ learner.points }} pts</div>
            <div class="courses">{{ learner.coursesCompleted }} courses</div>
          </div>
          <div class="learner-badge" v-if="idx < 3">
            <el-icon><Trophy /></el-icon>
          </div>
        </div>
      </div>
    </el-card>

    <!-- Quick Actions -->
    <el-card class="quick-actions-card" shadow="never">
      <div class="quick-actions">
        <div class="quick-action-item" @click="handleBrowseCatalog">
          <el-icon :size="24"><Reading /></el-icon>
          <span>Browse Catalog</span>
        </div>
        <div class="quick-action-item" @click="handleMyProgress">
          <el-icon :size="24"><TrendCharts /></el-icon>
          <span>My Progress</span>
        </div>
        <div class="quick-action-item" @click="handleCertificates">
          <el-icon :size="24"><Medal /></el-icon>
          <span>Certificates</span>
        </div>
        <div class="quick-action-item" @click="handleRecommendations">
          <el-icon :size="24"><Star /></el-icon>
          <span>Recommendations</span>
        </div>
        <div class="quick-action-item" @click="handleLearningPath">
          <el-icon :size="24"><MapLocation /></el-icon>
          <span>Learning Path</span>
        </div>
        <div class="quick-action-item" @click="handleMentorship">
          <el-icon :size="24"><ChatDotRound /></el-icon>
          <span>Mentorship</span>
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
  Plus, User, Reading, UserFilled, CircleCheck, Medal, Search, Clock, Calendar,
  Location, Trophy, TrendCharts, Star, MapLocation, ChatDotRound, ArrowRight
} from '@element-plus/icons-vue'

// Loading state
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing Training Center...')

const loadingMessages = [
  'Preparing Training Center...',
  'Loading course catalog...',
  'Syncing learner data...',
  'Almost ready...'
]

// Statistics
const stats = ref({
  totalCourses: 156,
  newCourses: 8,
  activeLearners: 1247,
  learnerGrowth: 15.3,
  completionRate: 78,
  rateGrowth: 5.2,
  certifications: 342,
  newCerts: 28
})

// Search filters
const searchKeyword = ref('')
const selectedCategory = ref('')
const selectedLevel = ref('')
const leaderboardPeriod = ref('week')

// Chart reference
const chartRef = ref<HTMLElement>()

// Featured courses
const featuredCourses = ref([
  {
    id: 1,
    title: 'IBMS System Architecture Masterclass',
    description: 'Comprehensive training on IBMS architecture, components, and integration strategies.',
    instructor: 'Dr. Sarah Johnson',
    students: 1245,
    duration: '8 hours',
    level: 'intermediate',
    rating: 4.8,
    enrolled: true,
    progress: 65,
    image: ''
  },
  {
    id: 2,
    title: 'HVAC Optimization & Energy Efficiency',
    description: 'Learn advanced techniques for HVAC optimization and energy savings in buildings.',
    instructor: 'Prof. Michael Chen',
    students: 892,
    duration: '6 hours',
    level: 'advanced',
    rating: 4.9,
    enrolled: false,
    image: ''
  },
  {
    id: 3,
    title: 'ESG Reporting & Compliance Fundamentals',
    description: 'Master ESG frameworks, reporting standards, and compliance requirements.',
    instructor: 'Emma Williams',
    students: 2103,
    duration: '5 hours',
    level: 'beginner',
    rating: 4.7,
    enrolled: true,
    progress: 30,
    image: ''
  },
  {
    id: 4,
    title: 'Data Center Operations & DCIM',
    description: 'Complete guide to data center operations, DCIM tools, and best practices.',
    instructor: 'James Rodriguez',
    students: 756,
    duration: '10 hours',
    level: 'intermediate',
    rating: 4.6,
    enrolled: false,
    image: ''
  }
])

// Categories
const categories = ref([
  { name: 'Technical Training', icon: 'Cpu', count: 48, color: '#3b82f6', popularity: 85 },
  { name: 'Safety & Compliance', icon: 'Warning', count: 32, color: '#ef4444', popularity: 92 },
  { name: 'Soft Skills', icon: 'ChatDotRound', count: 24, color: '#10b981', popularity: 70 },
  { name: 'Leadership', icon: 'Trophy', count: 18, color: '#f59e0b', popularity: 65 },
  { name: 'ESG & Sustainability', icon: 'Orange', count: 22, color: '#8b5cf6', popularity: 88 },
  { name: 'Digital Transformation', icon: 'DataAnalysis', count: 12, color: '#ec489a', popularity: 75 }
])

// Upcoming trainings
const upcomingTrainings = ref([
  { id: 1, title: 'Advanced BACnet Integration Workshop', day: '15', month: 'JAN', time: '10:00 AM - 2:00 PM', location: 'Online' },
  { id: 2, title: 'Emergency Response & Safety Training', day: '22', month: 'JAN', time: '9:00 AM - 5:00 PM', location: 'Training Room A' },
  { id: 3, title: 'Energy Auditing Techniques', day: '29', month: 'JAN', time: '1:00 PM - 4:00 PM', location: 'Online' },
  { id: 4, title: 'Leadership in Facility Management', day: '05', month: 'FEB', time: '10:00 AM - 3:00 PM', location: 'Conference Hall' }
])

// Certifications
const certifications = ref([
  { id: 1, title: 'Certified IBMS Professional', issuer: 'IBMS Institute', color: '#3b82f6', earned: true, inProgress: false },
  { id: 2, title: 'Energy Management Certificate', issuer: 'ASHRAE', color: '#10b981', earned: false, inProgress: true },
  { id: 3, title: 'ESG Reporting Specialist', issuer: 'GRI', color: '#8b5cf6', earned: false, inProgress: false },
  { id: 4, title: 'Data Center Operations Expert', issuer: 'Uptime Institute', color: '#f59e0b', earned: false, inProgress: false }
])

// Leaderboard
const leaderboard = ref([
  { id: 1, name: 'Alice Zhang', department: 'Facility Operations', points: 2840, coursesCompleted: 24, avatar: '' },
  { id: 2, name: 'Bob Smith', department: 'Energy Management', points: 2750, coursesCompleted: 22, avatar: '' },
  { id: 3, name: 'Carol Davis', department: 'Sustainability', points: 2680, coursesCompleted: 21, avatar: '' },
  { id: 4, name: 'David Lee', department: 'Technical Services', points: 2450, coursesCompleted: 19, avatar: '' },
  { id: 5, name: 'Eva Martinez', department: 'Compliance', points: 2320, coursesCompleted: 18, avatar: '' }
])

// Initialize chart
const initChart = () => {
  if (!chartRef.value) return

  const chart = echarts.init(chartRef.value)
  const option = {
    tooltip: { trigger: 'axis' },
    legend: { top: 0, right: 0, itemWidth: 25, itemHeight: 14 },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', data: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'] },
    yAxis: { type: 'value', name: 'Number of Learners' },
    series: [
      {
        name: 'New Enrollments',
        type: 'line',
        smooth: true,
        data: [85, 92, 108, 125, 142, 168, 195, 210, 228, 245, 268, 292],
        lineStyle: { width: 3, color: '#3b82f6' },
        areaStyle: { opacity: 0.3, color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#3b82f6' }, { offset: 1, color: '#93c5fd' }
          ]) },
        symbol: 'circle',
        symbolSize: 8,
        itemStyle: { color: '#3b82f6', borderColor: '#fff', borderWidth: 2 }
      },
      {
        name: 'Course Completions',
        type: 'bar',
        barWidth: '30%',
        data: [62, 68, 75, 82, 91, 98, 112, 125, 138, 152, 168, 185],
        itemStyle: { borderRadius: [4, 4, 0, 0], color: '#10b981' }
      }
    ]
  }
  chart.setOption(option)
  window.addEventListener('resize', () => chart.resize())
}

const refreshChart = () => {
  initChart()
  ElMessage.success('Chart refreshed successfully')
}

// Event handlers
const handleCreateTraining = () => {
  ElMessage.info('Create training feature will be available soon')
}

const handleMyLearning = () => {
  ElMessage.info('My learning dashboard coming soon')
}

const handleSearch = () => {
  ElMessage.info(`Searching for: ${searchKeyword.value} in ${selectedCategory.value || 'All'} categories, ${selectedLevel.value || 'All'} levels`)
}

const filterByCategory = (categoryName: string) => {
  selectedCategory.value = categoryName
  handleSearch()
}

const viewCourse = (course: any) => {
  ElMessage.info(`Opening course: ${course.title}`)
}

const viewAllCourses = () => {
  ElMessage.info('View all courses catalog')
}

const registerTraining = (training: any) => {
  ElMessage.success(`Registered for: ${training.title}`)
}

const viewAllTrainings = () => {
  ElMessage.info('View full training schedule')
}

const viewCertification = (cert: any) => {
  ElMessage.info(`Viewing certification: ${cert.title}`)
}

const viewAllCertifications = () => {
  ElMessage.info('View all certifications')
}

const handleBrowseCatalog = () => {
  ElMessage.info('Browse course catalog')
}

const handleMyProgress = () => {
  ElMessage.info('View my learning progress')
}

const handleCertificates = () => {
  ElMessage.info('View my certificates')
}

const handleRecommendations = () => {
  ElMessage.info('View personalized recommendations')
}

const handleLearningPath = () => {
  ElMessage.info('View learning path')
}

const handleMentorship = () => {
  ElMessage.info('Mentorship program information')
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
.training-center-container {
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

.header-right {
  display: flex;
  gap: 12px;
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

.category-select,
.level-select {
  width: 180px;
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

.featured-section {
  margin-bottom: 32px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.courses-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.course-card {
  border-radius: 12px;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  overflow: hidden;
}

.course-card:hover {
  transform: translateY(-4px);
}

.course-image {
  height: 140px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  background-size: cover;
  background-position: center;
  position: relative;
  padding: 12px;
}

.course-level {
  position: absolute;
  top: 12px;
  left: 12px;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  color: white;
}

.course-level.beginner { background: #10b981; }
.course-level.intermediate { background: #f59e0b; }
.course-level.advanced { background: #ef4444; }
.course-level.expert { background: #8b5cf6; }

.course-duration {
  position: absolute;
  bottom: 12px;
  right: 12px;
  background: rgba(0, 0, 0, 0.7);
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 11px;
  color: white;
  display: flex;
  align-items: center;
  gap: 4px;
}

.course-info {
  padding: 16px;
}

.course-title {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 8px 0;
}

.course-description {
  font-size: 13px;
  color: #64748b;
  margin-bottom: 12px;
  line-height: 1.4;
}

.course-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #94a3b8;
  margin-bottom: 8px;
}

.course-meta .el-icon {
  margin-right: 4px;
}

.course-rating {
  margin-bottom: 12px;
}

.course-progress {
  margin-bottom: 12px;
}

.progress-label {
  font-size: 11px;
  color: #64748b;
  margin-top: 4px;
  display: block;
}

.enroll-btn {
  width: 100%;
}

.categories-section {
  margin-bottom: 32px;
}

.categories-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
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
  width: 56px;
  height: 56px;
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
  margin: 0 0 8px 0;
  font-size: 12px;
  color: #64748b;
}

.category-progress {
  width: 80px;
}

.category-arrow {
  color: #cbd5e1;
}

.trainings-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.trainings-card,
.certifications-card {
  border-radius: 12px;
}

.trainings-list,
.certifications-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.training-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
}

.training-item:hover {
  background: #f8fafc;
}

.training-date {
  text-align: center;
  min-width: 60px;
  padding: 8px;
  background: #f1f5f9;
  border-radius: 8px;
}

.date-day {
  font-size: 24px;
  font-weight: 700;
  color: #3b82f6;
}

.date-month {
  font-size: 11px;
  color: #64748b;
  text-transform: uppercase;
}

.training-info {
  flex: 1;
}

.training-title {
  font-size: 14px;
  font-weight: 500;
  color: #1e293b;
  margin-bottom: 4px;
}

.training-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #94a3b8;
}

.training-meta .el-icon {
  margin-right: 4px;
}

.cert-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
}

.cert-item:hover {
  background: #f8fafc;
}

.cert-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.cert-info {
  flex: 1;
}

.cert-title {
  font-size: 14px;
  font-weight: 500;
  color: #1e293b;
  margin-bottom: 4px;
}

.cert-issuer {
  font-size: 11px;
  color: #64748b;
}

.leaderboard-card {
  margin-bottom: 24px;
  border-radius: 12px;
}

.leaderboard {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.leaderboard-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px;
  border-radius: 8px;
  transition: background 0.2s;
}

.leaderboard-item:hover {
  background: #f8fafc;
}

.rank {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  color: #64748b;
  border-radius: 50%;
}

.rank.top-rank {
  background: #fef3c7;
  color: #d97706;
}

.learner-info {
  flex: 1;
}

.learner-name {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 2px;
}

.learner-dept {
  font-size: 11px;
  color: #64748b;
}

.learner-stats {
  text-align: right;
}

.points {
  font-size: 14px;
  font-weight: 600;
  color: #3b82f6;
}

.courses {
  font-size: 11px;
  color: #64748b;
}

.learner-badge {
  color: #f59e0b;
}

.quick-actions-card {
  border-radius: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.quick-actions {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 8px;
  padding: 20px;
}

.quick-action-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: white;
  transition: transform 0.2s;
  padding: 8px;
}

.quick-action-item:hover {
  transform: translateY(-2px);
}

.quick-action-item span {
  font-size: 12px;
  text-align: center;
}

/* Responsive */
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .courses-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .categories-grid {
    grid-template-columns: repeat(3, 1fr);
  }

  .trainings-grid {
    grid-template-columns: 1fr;
  }

  .quick-actions {
    grid-template-columns: repeat(3, 1fr);
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
  .category-select,
  .level-select {
    width: 100%;
  }

  .courses-grid {
    grid-template-columns: 1fr;
  }

  .categories-grid {
    grid-template-columns: 1fr;
  }
}
</style>