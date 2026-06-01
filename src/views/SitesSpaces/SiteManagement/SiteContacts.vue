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
        <div class="loading-tip">Site Contacts Management</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="site-contacts">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h2>Site Contacts</h2>
        <p class="subtitle">Manage site personnel, emergency contacts, and key stakeholders</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="openAddContactDialog">
          <el-icon><Plus /></el-icon> Add Contact
        </el-button>
        <el-button @click="exportContacts">
          <el-icon><Download /></el-icon> Export
        </el-button>
        <el-button @click="refreshData">
          <el-icon><RefreshRight /></el-icon> Refresh
        </el-button>
      </div>
    </div>

    <!-- Statistics Cards -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">👥</div>
        <div class="stat-info">
          <div class="stat-value">{{ contacts.length }}</div>
          <div class="stat-label">Total Contacts</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">🚨</div>
        <div class="stat-info">
          <div class="stat-value">{{ emergencyContactsCount }}</div>
          <div class="stat-label">Emergency Contacts</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">🏢</div>
        <div class="stat-info">
          <div class="stat-value">{{ departmentCount }}</div>
          <div class="stat-label">Departments</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">📧</div>
        <div class="stat-info">
          <div class="stat-value">{{ activeCount }}</div>
          <div class="stat-label">Active</div>
        </div>
      </div>
    </div>

    <!-- Search and Filter Bar -->
    <div class="filter-section">
      <div class="search-wrapper">
        <el-input v-model="searchText" placeholder="Search by name, email, or department..." clearable :prefix-icon="Search" />
      </div>
      <div class="filter-wrapper">
        <el-select v-model="filterDepartment" placeholder="Department" clearable style="width: 160px">
          <el-option label="All Departments" value="all" />
          <el-option label="Facility Management" value="Facility Management" />
          <el-option label="Security" value="Security" />
          <el-option label="Maintenance" value="Maintenance" />
          <el-option label="Administration" value="Administration" />
          <el-option label="IT" value="IT" />
          <el-option label="Safety" value="Safety" />
        </el-select>
        <el-select v-model="filterType" placeholder="Contact Type" clearable style="width: 160px">
          <el-option label="All Types" value="all" />
          <el-option label="Primary" value="primary" />
          <el-option label="Emergency" value="emergency" />
          <el-option label="Technical" value="technical" />
          <el-option label="Administrative" value="administrative" />
        </el-select>
      </div>
    </div>

    <!-- Contacts Grid -->
    <div class="contacts-grid">
      <div v-for="contact in filteredContacts" :key="contact.id" class="contact-card">
        <div class="contact-header">
          <div class="contact-avatar" :style="{ background: getAvatarColor(contact.name) }">
            {{ getInitials(contact.name) }}
          </div>
          <div class="contact-badges">
            <el-tag v-if="contact.isPrimary" type="danger" size="small">Primary</el-tag>
            <el-tag v-if="contact.isEmergency" type="warning" size="small">Emergency</el-tag>
          </div>
        </div>
        <div class="contact-name">{{ contact.name }}</div>
        <div class="contact-title">{{ contact.title }}</div>
        <div class="contact-department">{{ contact.department }}</div>
        <div class="contact-details">
          <div class="detail-item">
            <el-icon><Phone /></el-icon>
            <span>{{ contact.phone }}</span>
          </div>
          <div class="detail-item">
            <el-icon><Message /></el-icon>
            <span>{{ contact.email }}</span>
          </div>
          <div class="detail-item" v-if="contact.mobile">
            <el-icon><Iphone /></el-icon>
            <span>{{ contact.mobile }}</span>
          </div>
        </div>
        <div class="contact-actions">
          <el-button size="small" type="primary" plain @click="editContact(contact)">
            <el-icon><Edit /></el-icon> Edit
          </el-button>
          <el-button size="small" type="danger" plain @click="deleteContact(contact)">
            <el-icon><Delete /></el-icon> Delete
          </el-button>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="filteredContacts.length === 0" class="empty-state">
      <div class="empty-icon">📋</div>
      <div class="empty-title">No contacts found</div>
      <div class="empty-desc">Add site contacts to get started</div>
      <el-button type="primary" @click="openAddContactDialog">Add Contact</el-button>
    </div>

    <!-- Add/Edit Contact Dialog -->
    <el-dialog v-model="showContactDialog" :title="dialogTitle" width="550px">
      <el-form :model="contactForm" label-width="110px">
        <el-form-item label="Full Name" required>
          <el-input v-model="contactForm.name" placeholder="Enter full name" />
        </el-form-item>
        <el-form-item label="Job Title" required>
          <el-input v-model="contactForm.title" placeholder="Enter job title" />
        </el-form-item>
        <el-form-item label="Department">
          <el-select v-model="contactForm.department" placeholder="Select department" style="width: 100%">
            <el-option label="Facility Management" value="Facility Management" />
            <el-option label="Security" value="Security" />
            <el-option label="Maintenance" value="Maintenance" />
            <el-option label="Administration" value="Administration" />
            <el-option label="IT" value="IT" />
            <el-option label="Safety" value="Safety" />
          </el-select>
        </el-form-item>
        <el-form-item label="Phone" required>
          <el-input v-model="contactForm.phone" placeholder="Enter phone number" />
        </el-form-item>
        <el-form-item label="Mobile">
          <el-input v-model="contactForm.mobile" placeholder="Enter mobile number" />
        </el-form-item>
        <el-form-item label="Email" required>
          <el-input v-model="contactForm.email" placeholder="Enter email address" />
        </el-form-item>
        <el-form-item label="Contact Type">
          <el-checkbox-group v-model="contactForm.types">
            <el-checkbox label="primary">Primary Contact</el-checkbox>
            <el-checkbox label="emergency">Emergency Contact</el-checkbox>
            <el-checkbox label="technical">Technical Contact</el-checkbox>
            <el-checkbox label="administrative">Administrative Contact</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        <el-form-item label="Notes">
          <el-input v-model="contactForm.notes" type="textarea" :rows="2" placeholder="Additional notes" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showContactDialog = false">Cancel</el-button>
        <el-button type="primary" @click="saveContact">Save Contact</el-button>
      </template>
    </el-dialog>

    <!-- Delete Confirmation Dialog -->
    <el-dialog v-model="showDeleteDialog" title="Delete Contact" width="400px">
      <p>Are you sure you want to delete contact <strong>{{ selectedContact?.name }}</strong>?</p>
      <p>This action cannot be undone.</p>
      <template #footer>
        <el-button @click="showDeleteDialog = false">Cancel</el-button>
        <el-button type="danger" @click="confirmDelete">Delete</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Plus, RefreshRight, Search, Phone, Message, Iphone, Edit, Delete, Download } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// Loading state
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Loading site contacts...',
  'Fetching contact information...',
  'Organizing by department...',
  'Almost ready...'
]

// Contact interface
interface Contact {
  id: number
  name: string
  title: string
  department: string
  phone: string
  mobile: string
  email: string
  isPrimary: boolean
  isEmergency: boolean
  isTechnical: boolean
  isAdministrative: boolean
  notes: string
  avatar?: string
}

// Sample contacts data
const contacts = ref<Contact[]>([
  {
    id: 1,
    name: 'Johnathan Lee',
    title: 'Facility Manager',
    department: 'Facility Management',
    phone: '+65 6789 0123',
    mobile: '+65 9123 4567',
    email: 'johnathan.lee@ibms.com',
    isPrimary: true,
    isEmergency: true,
    isTechnical: false,
    isAdministrative: false,
    notes: 'Primary point of contact for all facility matters'
  },
  {
    id: 2,
    name: 'Sarah Chen',
    title: 'Security Supervisor',
    department: 'Security',
    phone: '+65 6789 0124',
    mobile: '+65 9234 5678',
    email: 'sarah.chen@ibms.com',
    isPrimary: false,
    isEmergency: true,
    isTechnical: false,
    isAdministrative: false,
    notes: '24/7 security emergency contact'
  },
  {
    id: 3,
    name: 'Michael Tan',
    title: 'Chief Engineer',
    department: 'Maintenance',
    phone: '+65 6789 0125',
    mobile: '+65 9345 6789',
    email: 'michael.tan@ibms.com',
    isPrimary: false,
    isEmergency: false,
    isTechnical: true,
    isAdministrative: false,
    notes: 'Lead engineer for building systems'
  },
  {
    id: 4,
    name: 'Lisa Wong',
    title: 'Safety Officer',
    department: 'Safety',
    phone: '+65 6789 0126',
    mobile: '+65 9456 7890',
    email: 'lisa.wong@ibms.com',
    isPrimary: false,
    isEmergency: true,
    isTechnical: false,
    isAdministrative: false,
    notes: 'Safety compliance and emergency response'
  },
  {
    id: 5,
    name: 'David Lim',
    title: 'IT Manager',
    department: 'IT',
    phone: '+65 6789 0127',
    mobile: '+65 9567 8901',
    email: 'david.lim@ibms.com',
    isPrimary: false,
    isEmergency: false,
    isTechnical: true,
    isAdministrative: false,
    notes: 'BMS and network systems'
  },
  {
    id: 6,
    name: 'Amanda Ng',
    title: 'Administrative Coordinator',
    department: 'Administration',
    phone: '+65 6789 0128',
    mobile: '+65 9678 9012',
    email: 'amanda.ng@ibms.com',
    isPrimary: false,
    isEmergency: false,
    isTechnical: false,
    isAdministrative: true,
    notes: 'Office administration and scheduling'
  },
  {
    id: 7,
    name: 'Robert Goh',
    title: 'HVAC Specialist',
    department: 'Maintenance',
    phone: '+65 6789 0129',
    mobile: '+65 9789 0123',
    email: 'robert.goh@ibms.com',
    isPrimary: false,
    isEmergency: false,
    isTechnical: true,
    isAdministrative: false,
    notes: 'HVAC systems specialist'
  }
])

// UI State
const searchText = ref('')
const filterDepartment = ref('all')
const filterType = ref('all')
const showContactDialog = ref(false)
const showDeleteDialog = ref(false)
const isEditing = ref(false)
const selectedContact = ref<Contact | null>(null)
const editingId = ref<number | null>(null)

// Contact form
const contactForm = ref({
  name: '',
  title: '',
  department: '',
  phone: '',
  mobile: '',
  email: '',
  types: [] as string[],
  notes: ''
})

// Computed
const dialogTitle = computed(() => isEditing.value ? 'Edit Contact' : 'Add Contact')

const emergencyContactsCount = computed(() => contacts.value.filter(c => c.isEmergency).length)
const departmentCount = computed(() => {
  const depts = new Set(contacts.value.map(c => c.department))
  return depts.size
})
const activeCount = computed(() => contacts.value.length)

const filteredContacts = computed(() => {
  let filtered = [...contacts.value]

  if (searchText.value) {
    const keyword = searchText.value.toLowerCase()
    filtered = filtered.filter(c =>
        c.name.toLowerCase().includes(keyword) ||
        c.email.toLowerCase().includes(keyword) ||
        c.department.toLowerCase().includes(keyword)
    )
  }

  if (filterDepartment.value !== 'all') {
    filtered = filtered.filter(c => c.department === filterDepartment.value)
  }

  if (filterType.value !== 'all') {
    switch (filterType.value) {
      case 'primary':
        filtered = filtered.filter(c => c.isPrimary)
        break
      case 'emergency':
        filtered = filtered.filter(c => c.isEmergency)
        break
      case 'technical':
        filtered = filtered.filter(c => c.isTechnical)
        break
      case 'administrative':
        filtered = filtered.filter(c => c.isAdministrative)
        break
    }
  }

  return filtered
})

// Helper functions
const getInitials = (name: string) => {
  return name.split(' ').map(n => n[0]).join('').toUpperCase()
}

const getAvatarColor = (name: string) => {
  const colors = ['#409eff', '#67c23a', '#e6a23c', '#f56c6c', '#909399', '#9c27b0']
  const index = name.length % colors.length
  return colors[index]
}

// Contact CRUD operations
const openAddContactDialog = () => {
  isEditing.value = false
  editingId.value = null
  contactForm.value = {
    name: '',
    title: '',
    department: '',
    phone: '',
    mobile: '',
    email: '',
    types: [],
    notes: ''
  }
  showContactDialog.value = true
}

const editContact = (contact: Contact) => {
  isEditing.value = true
  editingId.value = contact.id
  const types: string[] = []
  if (contact.isPrimary) types.push('primary')
  if (contact.isEmergency) types.push('emergency')
  if (contact.isTechnical) types.push('technical')
  if (contact.isAdministrative) types.push('administrative')

  contactForm.value = {
    name: contact.name,
    title: contact.title,
    department: contact.department,
    phone: contact.phone,
    mobile: contact.mobile,
    email: contact.email,
    types: types,
    notes: contact.notes
  }
  showContactDialog.value = true
}

const saveContact = () => {
  if (!contactForm.value.name.trim()) {
    ElMessage.warning('Please enter contact name')
    return
  }
  if (!contactForm.value.title.trim()) {
    ElMessage.warning('Please enter job title')
    return
  }
  if (!contactForm.value.phone.trim()) {
    ElMessage.warning('Please enter phone number')
    return
  }
  if (!contactForm.value.email.trim()) {
    ElMessage.warning('Please enter email address')
    return
  }

  const newContact: Contact = {
    id: isEditing.value ? editingId.value! : Date.now(),
    name: contactForm.value.name,
    title: contactForm.value.title,
    department: contactForm.value.department || 'General',
    phone: contactForm.value.phone,
    mobile: contactForm.value.mobile,
    email: contactForm.value.email,
    isPrimary: contactForm.value.types.includes('primary'),
    isEmergency: contactForm.value.types.includes('emergency'),
    isTechnical: contactForm.value.types.includes('technical'),
    isAdministrative: contactForm.value.types.includes('administrative'),
    notes: contactForm.value.notes
  }

  if (isEditing.value) {
    const index = contacts.value.findIndex(c => c.id === editingId.value)
    if (index !== -1) {
      contacts.value[index] = newContact
      ElMessage.success('Contact updated successfully')
    }
  } else {
    contacts.value.unshift(newContact)
    ElMessage.success('Contact added successfully')
  }

  showContactDialog.value = false
}

const deleteContact = (contact: Contact) => {
  selectedContact.value = contact
  showDeleteDialog.value = true
}

const confirmDelete = () => {
  if (selectedContact.value) {
    const index = contacts.value.findIndex(c => c.id === selectedContact.value!.id)
    if (index !== -1) {
      contacts.value.splice(index, 1)
      ElMessage.success('Contact deleted successfully')
    }
  }
  showDeleteDialog.value = false
  selectedContact.value = null
}

const exportContacts = () => {
  const data = JSON.stringify(filteredContacts.value, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `site_contacts_${new Date().toISOString().split('T')[0]}.json`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('Contacts exported successfully')
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
.site-contacts {
  padding: 24px;
  background: linear-gradient(135deg, #f0f5ff 0%, #e8f0fe 100%);
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
  background: linear-gradient(135deg, #1565c0, #1976d2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.subtitle {
  margin: 0;
  color: #1565c0;
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

/* Stats Grid */
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

/* Contacts Grid */
.contacts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: 20px;
}

.contact-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.contact-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.contact-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.contact-avatar {
  width: 60px;
  height: 60px;
  border-radius: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: 600;
  color: white;
}

.contact-badges {
  display: flex;
  gap: 8px;
}

.contact-name {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.contact-title {
  font-size: 13px;
  color: #67c23a;
  margin-bottom: 4px;
}

.contact-department {
  font-size: 12px;
  color: #909399;
  margin-bottom: 16px;
}

.contact-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #606266;
}

.detail-item .el-icon {
  color: #409eff;
}

.contact-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
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
:deep(.el-dialog__body) {
  padding: 20px;
}

/* Responsive */
@media (max-width: 768px) {
  .site-contacts { padding: 16px; }
  .page-header { flex-direction: column; align-items: stretch; }
  .header-actions { flex-direction: column; }
  .header-actions .el-button { width: 100%; }
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .filter-section { flex-direction: column; }
  .search-wrapper { width: 100%; }
  .filter-wrapper { width: 100%; justify-content: space-between; }
  .contacts-grid { grid-template-columns: 1fr; }
}
</style>