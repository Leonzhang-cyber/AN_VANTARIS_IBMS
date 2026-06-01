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
        <div class="loading-tip">Operator Notes System</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="operator-notes">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h2>Operator Notes</h2>
        <p class="subtitle">Centralized log for operational observations, issues, and important reminders</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="createNote">
          <el-icon><Plus /></el-icon> New Note
        </el-button>
        <el-button @click="refreshData">
          <el-icon><RefreshRight /></el-icon> Refresh
        </el-button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">📝</div>
        <div class="stat-info">
          <div class="stat-value">{{ notes.length }}</div>
          <div class="stat-label">Total Notes</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">⭐</div>
        <div class="stat-info">
          <div class="stat-value">{{ pinnedCount }}</div>
          <div class="stat-label">Pinned</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">📅</div>
        <div class="stat-info">
          <div class="stat-value">{{ todayCount }}</div>
          <div class="stat-label">Today's Notes</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">👥</div>
        <div class="stat-info">
          <div class="stat-value">{{ activeAuthors }}</div>
          <div class="stat-label">Active Authors</div>
        </div>
      </div>
    </div>

    <!-- Search and Filter Bar -->
    <div class="filter-section">
      <div class="search-wrapper">
        <el-input v-model="searchText" placeholder="Search notes by title or content..." clearable :prefix-icon="Search" />
      </div>
      <div class="filter-wrapper">
        <el-select v-model="filterCategory" placeholder="Category" clearable>
          <el-option label="All Categories" value="all" />
          <el-option label="General" value="general" />
          <el-option label="Maintenance" value="maintenance" />
          <el-option label="Alert" value="alert" />
          <el-option label="Reminder" value="reminder" />
          <el-option label="Task" value="task" />
        </el-select>
        <el-select v-model="filterPriority" placeholder="Priority" clearable>
          <el-option label="All Priorities" value="all" />
          <el-option label="High" value="high" />
          <el-option label="Medium" value="medium" />
          <el-option label="Low" value="low" />
        </el-select>
        <div class="view-toggle">
          <el-button :type="viewMode === 'grid' ? 'primary' : 'default'" @click="viewMode = 'grid'" size="default">
            <el-icon><Grid /></el-icon>
          </el-button>
          <el-button :type="viewMode === 'list' ? 'primary' : 'default'" @click="viewMode = 'list'" size="default">
            <el-icon><List /></el-icon>
          </el-button>
        </div>
      </div>
    </div>

    <!-- Create Note Modal -->
    <el-dialog v-model="showCreateForm" title="Create New Note" width="600px" class="note-dialog">
      <el-form :model="newNoteForm" label-width="100px">
        <el-form-item label="Title" required>
          <el-input v-model="newNoteForm.title" placeholder="Enter note title" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="Category">
              <el-select v-model="newNoteForm.category" style="width: 100%">
                <el-option label="General" value="general" />
                <el-option label="Maintenance" value="maintenance" />
                <el-option label="Alert" value="alert" />
                <el-option label="Reminder" value="reminder" />
                <el-option label="Task" value="task" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Priority">
              <el-select v-model="newNoteForm.priority" style="width: 100%">
                <el-option label="High" value="high" />
                <el-option label="Medium" value="medium" />
                <el-option label="Low" value="low" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="Tags">
          <el-select v-model="newNoteForm.tags" multiple filterable allow-create default-first-option placeholder="Add tags" style="width: 100%">
            <el-option label="urgent" value="urgent" />
            <el-option label="follow-up" value="follow-up" />
            <el-option label="completed" value="completed" />
            <el-option label="in-progress" value="in-progress" />
          </el-select>
        </el-form-item>
        <el-form-item label="Content" required>
          <el-input v-model="newNoteForm.content" type="textarea" :rows="5" placeholder="Write your note here..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateForm = false">Cancel</el-button>
        <el-button type="primary" @click="submitNote">Create Note</el-button>
      </template>
    </el-dialog>

    <!-- Grid View -->
    <div v-if="viewMode === 'grid'" class="notes-grid">
      <div v-for="note in filteredNotes" :key="note.id" class="note-card" :data-priority="note.priority">
        <div class="note-pin" @click="togglePin(note)">
          <el-icon v-if="note.pinned" class="pin-icon pinned"><StarFilled /></el-icon>
          <el-icon v-else class="pin-icon"><Star /></el-icon>
        </div>
        <div class="note-header">
          <h3 class="note-title">{{ note.title }}</h3>
          <el-dropdown trigger="click">
            <el-button type="text" class="more-btn">⋮</el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="togglePin(note)">
                  {{ note.pinned ? 'Unpin' : 'Pin' }}
                </el-dropdown-item>
                <el-dropdown-item divided @click="deleteNote(note)" style="color: #f56c6c">Delete</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
        <div class="note-meta">
          <span class="category-tag" :class="note.category">{{ getCategoryLabel(note.category) }}</span>
          <span class="priority-tag" :class="note.priority">{{ getPriorityLabel(note.priority) }}</span>
        </div>
        <div class="note-content-preview">{{ truncateContent(note.content, 120) }}</div>
        <div class="note-footer">
          <div class="note-author">
            <span class="author-avatar">{{ getInitials(note.author) }}</span>
            <span class="author-name">{{ note.author }}</span>
          </div>
          <div class="note-time">{{ formatTime(note.timestamp) }}</div>
        </div>
        <div v-if="note.tags && note.tags.length" class="note-tags">
          <span v-for="tag in note.tags.slice(0, 3)" :key="tag" class="tag">#{{ tag }}</span>
          <span v-if="note.tags.length > 3" class="tag-more">+{{ note.tags.length - 3 }}</span>
        </div>
      </div>
    </div>

    <!-- List View -->
    <div v-else class="list-view">
      <div v-for="note in filteredNotes" :key="note.id" class="list-item">
        <div class="list-item-pin" @click="togglePin(note)">
          <el-icon v-if="note.pinned" class="pin-icon pinned"><StarFilled /></el-icon>
          <el-icon v-else class="pin-icon"><Star /></el-icon>
        </div>
        <div class="list-item-content">
          <div class="list-item-header">
            <div class="list-item-title">{{ note.title }}</div>
            <div class="list-item-meta">
              <span class="category-tag small" :class="note.category">{{ getCategoryLabel(note.category) }}</span>
              <span class="priority-tag small" :class="note.priority">{{ getPriorityLabel(note.priority) }}</span>
            </div>
          </div>
          <div class="list-item-preview">{{ truncateContent(note.content, 80) }}</div>
          <div class="list-item-footer">
            <div class="list-item-author">
              <span class="author-avatar small">{{ getInitials(note.author) }}</span>
              <span>{{ note.author }}</span>
            </div>
            <div class="list-item-time">{{ formatTime(note.timestamp) }}</div>
          </div>
        </div>
        <div class="list-item-actions">
          <el-button type="text" @click="deleteNote(note)" class="delete-btn">
            <el-icon><Delete /></el-icon>
          </el-button>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="filteredNotes.length === 0 && !showCreateForm" class="empty-state">
      <div class="empty-icon">📋</div>
      <div class="empty-title">No notes found</div>
      <div class="empty-desc">Create your first note to start logging operational observations</div>
      <el-button type="primary" @click="createNote">Create Your First Note</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { Plus, RefreshRight, Search, Grid, List, Star, StarFilled, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// Loading state
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Loading operator notes...',
  'Fetching recent notes...',
  'Organizing by priority...',
  'Ready for use...'
]

// Types
interface Note {
  id: number
  title: string
  content: string
  category: string
  priority: string
  author: string
  timestamp: string
  pinned: boolean
  tags: string[]
}

// Helper functions
const getCurrentTimestamp = () => {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  const hours = String(now.getHours()).padStart(2, '0')
  const minutes = String(now.getMinutes()).padStart(2, '0')
  return `${year}-${month}-${day} ${hours}:${minutes}`
}

const formatTime = (timestamp: string) => {
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 1) return 'Just now'
  if (minutes < 60) return `${minutes} min ago`
  if (hours < 24) return `${hours} hour${hours > 1 ? 's' : ''} ago`
  return `${days} day${days > 1 ? 's' : ''} ago`
}

const getCategoryLabel = (category: string) => {
  const labels: Record<string, string> = {
    general: 'General',
    maintenance: 'Maintenance',
    alert: 'Alert',
    reminder: 'Reminder',
    task: 'Task'
  }
  return labels[category] || category
}

const getPriorityLabel = (priority: string) => {
  const labels: Record<string, string> = {
    high: 'High',
    medium: 'Medium',
    low: 'Low'
  }
  return labels[priority] || priority
}

const getInitials = (name: string) => {
  return name.split(' ').map(n => n[0]).join('').toUpperCase()
}

const truncateContent = (content: string, maxLength: number) => {
  if (content.length <= maxLength) return content
  return content.substring(0, maxLength) + '...'
}

// Sample notes data
const notes = ref<Note[]>([
  {
    id: 1,
    title: 'Chiller Efficiency Alert',
    content: 'Chiller CH-01 showing decreased efficiency. COP dropped from 5.2 to 4.8. Schedule maintenance for condenser cleaning.',
    category: 'alert',
    priority: 'high',
    author: 'John Zhang',
    timestamp: getCurrentTimestamp(),
    pinned: true,
    tags: ['urgent', 'hvac']
  },
  {
    id: 2,
    title: 'UPS Battery Replacement',
    content: 'UPS-01 batteries are reaching end of life. Battery health at 72%. Plan replacement within 2 weeks.',
    category: 'maintenance',
    priority: 'high',
    author: 'Sarah Li',
    timestamp: getCurrentTimestamp(),
    pinned: true,
    tags: ['urgent', 'power']
  },
  {
    id: 3,
    title: 'Weekly Fire Drill Reminder',
    content: 'Fire drill scheduled for Friday at 10:00 AM. Ensure all fire wardens are notified and evacuation routes are clear.',
    category: 'reminder',
    priority: 'medium',
    author: 'Mike Wang',
    timestamp: getCurrentTimestamp(),
    pinned: false,
    tags: ['follow-up', 'safety']
  },
  {
    id: 4,
    title: 'AHU-03 Fan Noise',
    content: 'AHU-03 fan making unusual noise. Investigate during next maintenance window. Possibly bearing wear.',
    category: 'task',
    priority: 'medium',
    author: 'Emma Zhao',
    timestamp: getCurrentTimestamp(),
    pinned: false,
    tags: ['in-progress']
  },
  {
    id: 5,
    title: 'Generator Test Passed',
    content: 'Weekly generator test completed successfully. Fuel level at 92%, runtime 15 minutes. No issues detected.',
    category: 'general',
    priority: 'low',
    author: 'David Sun',
    timestamp: getCurrentTimestamp(),
    pinned: false,
    tags: ['completed']
  },
  {
    id: 6,
    title: 'BMS Communication Issue',
    content: 'Intermittent communication loss with BACnet devices on floor 3. Investigating root cause. Network team notified.',
    category: 'alert',
    priority: 'high',
    author: 'Lisa Chen',
    timestamp: getCurrentTimestamp(),
    pinned: false,
    tags: ['urgent', 'in-progress']
  }
])

// UI State
const viewMode = ref<'grid' | 'list'>('grid')
const showCreateForm = ref(false)
const searchText = ref('')
const filterCategory = ref('all')
const filterPriority = ref('all')

const newNoteForm = ref({
  title: '',
  content: '',
  category: 'general',
  priority: 'medium',
  tags: [] as string[]
})

// Computed
const pinnedCount = computed(() => notes.value.filter(n => n.pinned).length)
const todayCount = computed(() => {
  const today = new Date().toISOString().split('T')[0]
  return notes.value.filter(n => n.timestamp.startsWith(today)).length
})
const activeAuthors = computed(() => {
  return new Set(notes.value.map(n => n.author)).size
})

const filteredNotes = computed(() => {
  let filtered = [...notes.value]

  if (searchText.value) {
    const keyword = searchText.value.toLowerCase()
    filtered = filtered.filter(n =>
        n.title.toLowerCase().includes(keyword) ||
        n.content.toLowerCase().includes(keyword)
    )
  }

  if (filterCategory.value !== 'all') {
    filtered = filtered.filter(n => n.category === filterCategory.value)
  }

  if (filterPriority.value !== 'all') {
    filtered = filtered.filter(n => n.priority === filterPriority.value)
  }

  return filtered.sort((a, b) => {
    if (a.pinned && !b.pinned) return -1
    if (!a.pinned && b.pinned) return 1
    return new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
  })
})

// Methods
const createNote = () => {
  newNoteForm.value = {
    title: '',
    content: '',
    category: 'general',
    priority: 'medium',
    tags: []
  }
  showCreateForm.value = true
}

const submitNote = () => {
  if (!newNoteForm.value.title.trim()) {
    ElMessage.warning('Please enter a title')
    return
  }
  if (!newNoteForm.value.content.trim()) {
    ElMessage.warning('Please enter content')
    return
  }

  const newNote: Note = {
    id: Date.now(),
    title: newNoteForm.value.title,
    content: newNoteForm.value.content,
    category: newNoteForm.value.category,
    priority: newNoteForm.value.priority,
    author: 'Current User',
    timestamp: getCurrentTimestamp(),
    pinned: false,
    tags: newNoteForm.value.tags
  }

  notes.value.unshift(newNote)
  ElMessage.success('Note created successfully')
  showCreateForm.value = false
}

const togglePin = (note: Note) => {
  note.pinned = !note.pinned
  ElMessage.success(note.pinned ? 'Note pinned' : 'Note unpinned')
}

const deleteNote = (note: Note) => {
  ElMessageBox.confirm(
      `Delete note "${note.title}"? This action cannot be undone.`,
      'Delete Note',
      {
        confirmButtonText: 'Delete',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
  ).then(() => {
    const index = notes.value.findIndex(n => n.id === note.id)
    if (index !== -1) {
      notes.value.splice(index, 1)
      ElMessage.success('Note deleted')
    }
  }).catch(() => {})
}

const refreshData = () => {
  ElMessage.success('Data refreshed')
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
    }, 400)
  }, 2000)
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
@keyframes pulse { 0%, 100% { opacity: 0.6; } 50% { opacity: 1; } }
@keyframes fadeInUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }

/* Main Content */
.operator-notes {
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
  flex-wrap: wrap;
}

/* Stats Cards */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  font-size: 36px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
  line-height: 1.2;
}

.stat-label {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}

/* Filter Section */
.filter-section {
  background: white;
  border-radius: 20px;
  padding: 16px 20px;
  margin-bottom: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}

.search-wrapper {
  flex: 1;
  min-width: 250px;
}

.filter-wrapper {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.filter-wrapper .el-select {
  width: 140px;
}

.view-toggle {
  display: flex;
  gap: 0;
  border-radius: 8px;
  overflow: hidden;
}

.view-toggle .el-button {
  border-radius: 0;
  margin: 0;
}

/* Notes Grid */
.notes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: 20px;
}

.note-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  position: relative;
  transition: all 0.3s ease;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.note-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.note-card[data-priority="high"] { border-top: 4px solid #f56c6c; }
.note-card[data-priority="medium"] { border-top: 4px solid #e6a23c; }
.note-card[data-priority="low"] { border-top: 4px solid #67c23a; }

.note-pin {
  position: absolute;
  top: 16px;
  right: 16px;
  cursor: pointer;
}

.pin-icon {
  font-size: 18px;
  color: #c0c4cc;
  transition: all 0.2s ease;
}

.pin-icon.pinned {
  color: #e6a23c;
}

.pin-icon:hover {
  transform: scale(1.1);
}

.note-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
  padding-right: 24px;
}

.note-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.more-btn {
  font-size: 20px;
  padding: 0;
  color: #909399;
}

.note-meta {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.category-tag {
  padding: 2px 10px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 500;
}

.category-tag.general { background: #e6f7ff; color: #409eff; }
.category-tag.maintenance { background: #fff7e6; color: #e6a23c; }
.category-tag.alert { background: #ffefef; color: #f56c6c; }
.category-tag.reminder { background: #e8f5e9; color: #67c23a; }
.category-tag.task { background: #f3e5f5; color: #9c27b0; }

.priority-tag {
  padding: 2px 10px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 500;
}

.priority-tag.high { background: #ffefef; color: #f56c6c; }
.priority-tag.medium { background: #fff7e6; color: #e6a23c; }
.priority-tag.low { background: #e8f5e9; color: #67c23a; }

.note-content-preview {
  font-size: 13px;
  color: #606266;
  line-height: 1.5;
  margin-bottom: 16px;
}

.note-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.note-author {
  display: flex;
  align-items: center;
  gap: 8px;
}

.author-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea, #764ba2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  color: white;
}

.author-name {
  font-size: 12px;
  color: #606266;
}

.note-time {
  font-size: 11px;
  color: #c0c4cc;
}

.note-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}

.tag {
  font-size: 11px;
  color: #409eff;
  background: #ecf5ff;
  padding: 2px 8px;
  border-radius: 12px;
}

.tag-more {
  font-size: 11px;
  color: #909399;
}

/* List View */
.list-view {
  background: white;
  border-radius: 20px;
  overflow: hidden;
}

.list-item {
  display: flex;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #f0f0f0;
  transition: background 0.2s ease;
}

.list-item:hover {
  background: #f8f9fa;
}

.list-item-pin {
  cursor: pointer;
  margin-right: 16px;
}

.list-item-content {
  flex: 1;
}

.list-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
  flex-wrap: wrap;
  gap: 8px;
}

.list-item-title {
  font-weight: 600;
  font-size: 15px;
  color: #303133;
}

.list-item-meta {
  display: flex;
  gap: 8px;
}

.category-tag.small, .priority-tag.small {
  padding: 2px 8px;
  font-size: 10px;
}

.list-item-preview {
  font-size: 13px;
  color: #909399;
  margin-bottom: 8px;
}

.list-item-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.list-item-author {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #606266;
}

.author-avatar.small {
  width: 22px;
  height: 22px;
  font-size: 10px;
}

.list-item-time {
  font-size: 11px;
  color: #c0c4cc;
}

.list-item-actions {
  margin-left: 16px;
}

.delete-btn {
  color: #f56c6c;
}

.delete-btn:hover {
  color: #f78989;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 60px;
  background: white;
  border-radius: 20px;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.empty-title {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}

.empty-desc {
  font-size: 14px;
  color: #909399;
  margin-bottom: 24px;
}

/* Dialog */
.note-dialog :deep(.el-dialog__body) {
  padding: 20px;
}

/* Responsive */
@media (max-width: 768px) {
  .operator-notes { padding: 16px; }
  .page-header { flex-direction: column; align-items: stretch; }
  .header-actions { flex-direction: column; }
  .header-actions .el-button { width: 100%; }
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .filter-section { flex-direction: column; }
  .search-wrapper { width: 100%; }
  .filter-wrapper { width: 100%; justify-content: space-between; }
  .notes-grid { grid-template-columns: 1fr; }
  .list-item { flex-wrap: wrap; }
  .list-item-pin { order: 1; }
  .list-item-content { order: 2; width: calc(100% - 40px); }
  .list-item-actions { order: 3; margin-left: 40px; margin-top: 8px; }
  .list-item-header { flex-direction: column; align-items: flex-start; }
}
</style>