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
        <div class="loading-tip">Fault Workflow</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- New Fault Page Content -->
  <div v-else class="new-fault-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-title">
        <div class="title-badge">
          <el-icon><WarningFilled /></el-icon>
          <span>FMS - Workflow</span>
        </div>
        <h1>Create New Fault</h1>
        <p class="subtitle">Register a new fault incident and initiate the resolution workflow</p>
      </div>
      <div class="header-actions">
        <button class="action-btn" @click="resetForm">
          <el-icon><Refresh /></el-icon>
          <span>Reset</span>
        </button>
        <button class="action-btn primary" @click="submitFault" :loading="submitting">
          <el-icon><Check /></el-icon>
          <span>Create Fault</span>
        </button>
      </div>
    </div>

    <!-- Workflow Steps -->
    <div class="workflow-steps">
      <div class="step" :class="{ active: currentStep >= 1, completed: currentStep > 1 }">
        <div class="step-number">1</div>
        <div class="step-label">Fault Details</div>
      </div>
      <div class="step-line" :class="{ active: currentStep > 1 }"></div>
      <div class="step" :class="{ active: currentStep >= 2, completed: currentStep > 2 }">
        <div class="step-number">2</div>
        <div class="step-label">Assign & Priority</div>
      </div>
      <div class="step-line" :class="{ active: currentStep > 2 }"></div>
      <div class="step" :class="{ active: currentStep >= 3, completed: currentStep > 3 }">
        <div class="step-number">3</div>
        <div class="step-label">Impact Analysis</div>
      </div>
      <div class="step-line" :class="{ active: currentStep > 3 }"></div>
      <div class="step" :class="{ active: currentStep >= 4 }">
        <div class="step-number">4</div>
        <div class="step-label">Review & Submit</div>
      </div>
    </div>

    <!-- Form Container with Tour Guide -->
    <div class="form-container">
      <!-- Step 1: Fault Details -->
      <div v-show="currentStep === 1" class="form-step">
<!--        <el-alert-->
<!--            title="Quick Guide"-->
<!--            type="info"-->
<!--            :closable="false"-->
<!--            show-icon-->
<!--            class="guide-alert"-->
<!--        >-->
<!--          <template #default>-->
<!--            <p>Fill in the basic fault information. Required fields are marked with <span class="required">*</span>. Use the example values as a reference.</p>-->
<!--            <ul>-->
<!--              <li><strong>Fault Title:</strong> A clear, descriptive name for the fault</li>-->
<!--              <li><strong>Category:</strong> Select the system category that matches the fault</li>-->
<!--              <li><strong>Description:</strong> Include what happened, when, and any error codes</li>-->
<!--            </ul>-->
<!--          </template>-->
<!--        </el-alert>-->

        <div class="form-section">
          <h3>Basic Information</h3>
          <div class="form-row">
            <div class="form-group">
              <label>Fault Title <span class="required">*</span></label>
              <el-input
                  v-model="faultData.title"
                  placeholder="e.g., Chiller-02 High Pressure Trip"
                  clearable
              />
              <div class="form-hint">Example: "AHU-101 Fan Motor Failure" or "UPS Battery Low Warning"</div>
            </div>
            <div class="form-group">
              <label>Category <span class="required">*</span></label>
              <el-select v-model="faultData.category" placeholder="Select Category" clearable style="width: 100%">
                <el-option label="HVAC" value="HVAC" />
                <el-option label="Electrical" value="Electrical" />
                <el-option label="Plumbing" value="Plumbing" />
                <el-option label="Security" value="Security" />
                <el-option label="DCIM" value="DCIM" />
                <el-option label="BMS" value="BMS" />
                <el-option label="Fire Safety" value="Fire Safety" />
              </el-select>
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Asset / Equipment</label>
              <el-input
                  v-model="faultData.asset"
                  placeholder="e.g., Chiller-02, AHU-101"
                  clearable
              />
              <div class="form-hint">Specific equipment identifier</div>
            </div>
            <div class="form-group">
              <label>Location</label>
              <el-input
                  v-model="faultData.location"
                  placeholder="e.g., Building A - Floor 1"
                  clearable
              />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group full">
              <label>Description <span class="required">*</span></label>
              <el-input
                  v-model="faultData.description"
                  type="textarea"
                  :rows="4"
                  placeholder="Describe the fault in detail, including observed symptoms, error codes, and any relevant context..."
              />
              <div class="form-hint">Example: "Chiller tripped on high pressure alarm at 08:23. Cooling tower fan not responding. Building temperature rising."</div>
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Detected Date/Time <span class="required">*</span></label>
              <el-date-picker
                  v-model="faultData.detectedAt"
                  type="datetime"
                  placeholder="Select date and time"
                  format="YYYY-MM-DD HH:mm:ss"
                  value-format="YYYY-MM-DD HH:mm:ss"
                  style="width: 100%"
              />
            </div>
            <div class="form-group">
              <label>Reported By</label>
              <el-input
                  v-model="faultData.reportedBy"
                  placeholder="e.g., John Smith"
                  clearable
              />
            </div>
          </div>
        </div>

        <div class="form-section">
          <h3>Symptoms & Evidence</h3>
          <div class="form-row">
            <div class="form-group full">
              <label>Symptoms</label>
              <el-input
                  v-model="faultData.symptoms"
                  type="textarea"
                  :rows="3"
                  placeholder="List observed symptoms..."
              />
              <div class="form-hint">Example: "High pressure alarm, cooling tower fan not running, building temperature rising"</div>
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Error Code</label>
              <el-input
                  v-model="faultData.errorCode"
                  placeholder="e.g., ERR-102"
                  clearable
              />
            </div>
            <div class="form-group">
              <label>Sensor Readings</label>
              <el-input
                  v-model="faultData.sensorReadings"
                  placeholder="e.g., Pressure: 220PSI"
                  clearable
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Step 2: Assign & Priority -->
      <div v-show="currentStep === 2" class="form-step">
        <el-alert
            title="Quick Guide"
            type="info"
            :closable="false"
            show-icon
            class="guide-alert"
        >
          <template #default>
            <p>Assign the fault to the appropriate technician or team, and set the priority level.</p>
            <ul>
              <li><strong>Critical:</strong> Immediate attention required (SLA: 1-2 hours)</li>
              <li><strong>Major:</strong> High impact, resolve within 4-8 hours</li>
              <li><strong>Minor:</strong> Low impact, resolve within 24-48 hours</li>
            </ul>
          </template>
        </el-alert>

        <div class="form-section">
          <h3>Assignment</h3>
          <div class="form-row">
            <div class="form-group">
              <label>Assign To</label>
              <el-select v-model="faultData.assignedTo" placeholder="Select Technician" clearable style="width: 100%">
                <el-option label="Mike Johnson - HVAC Specialist" value="Mike Johnson" />
                <el-option label="John Smith - Electrical Engineer" value="John Smith" />
                <el-option label="Sarah Chen - DCIM Engineer" value="Sarah Chen" />
                <el-option label="Lisa Wong - Lighting Tech" value="Lisa Wong" />
                <el-option label="Tom Davis - Plumbing Specialist" value="Tom Davis" />
                <el-option label="Security Team" value="Security Team" />
              </el-select>
            </div>
            <div class="form-group">
              <label>Team</label>
              <el-select v-model="faultData.team" placeholder="Select Team" clearable style="width: 100%">
                <el-option label="HVAC Team" value="HVAC Team" />
                <el-option label="Electrical Team" value="Electrical Team" />
                <el-option label="Facilities Team" value="Facilities Team" />
                <el-option label="IT Team" value="IT Team" />
                <el-option label="Security Team" value="Security Team" />
              </el-select>
            </div>
          </div>
        </div>

        <div class="form-section">
          <h3>Priority & Severity</h3>
          <div class="form-row">
            <div class="form-group">
              <label>Severity <span class="required">*</span></label>
              <div class="priority-buttons">
                <button type="button" class="priority-btn" :class="{ active: faultData.severity === 'critical' }" @click="faultData.severity = 'critical'">
                  <el-icon><CircleCloseFilled /></el-icon>
                  <span>Critical</span>
                </button>
                <button type="button" class="priority-btn" :class="{ active: faultData.severity === 'major' }" @click="faultData.severity = 'major'">
                  <el-icon><WarningFilled /></el-icon>
                  <span>Major</span>
                </button>
                <button type="button" class="priority-btn" :class="{ active: faultData.severity === 'minor' }" @click="faultData.severity = 'minor'">
                  <el-icon><InfoFilled /></el-icon>
                  <span>Minor</span>
                </button>
              </div>
              <div class="form-hint">Critical: Immediate action | Major: High priority | Minor: Standard priority</div>
            </div>
            <div class="form-group">
              <label>Priority Level</label>
              <el-slider v-model="faultData.priority" :min="1" :max="5" :marks="{ 1: 'Low', 3: 'Medium', 5: 'High' }" />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>SLA Target (hours)</label>
              <el-input-number v-model="faultData.slaTarget" :min="1" :max="72" :step="1" controls-position="right" style="width: 100%" />
              <div class="form-hint">Critical: 1-2h | Major: 4-8h | Minor: 24-48h</div>
            </div>
            <div class="form-group">
              <label>Expected Resolution</label>
              <el-date-picker
                  v-model="faultData.expectedResolution"
                  type="date"
                  placeholder="Select date"
                  format="YYYY-MM-DD"
                  value-format="YYYY-MM-DD"
                  style="width: 100%"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Step 3: Impact Analysis -->
      <div v-show="currentStep === 3" class="form-step">
        <el-alert
            title="Quick Guide"
            type="info"
            :closable="false"
            show-icon
            class="guide-alert"
        >
          <template #default>
            <p>Assess the impact of this fault on operations and infrastructure.</p>
            <ul>
              <li><strong>Affected Systems:</strong> Which systems are impacted?</li>
              <li><strong>Business Impact:</strong> How does this affect operations?</li>
              <li><strong>Estimated Downtime:</strong> Expected duration of disruption</li>
            </ul>
          </template>
        </el-alert>

        <div class="form-section">
          <h3>Impact Assessment</h3>
          <div class="form-row">
            <div class="form-group">
              <label>Affected Systems</label>
              <el-input
                  v-model="faultData.affectedSystems"
                  placeholder="e.g., Building A HVAC, Server Room Cooling"
                  clearable
              />
            </div>
            <div class="form-group">
              <label>Affected Zones</label>
              <el-input
                  v-model="faultData.affectedZones"
                  placeholder="e.g., Floor 1-3, Data Center Row A"
                  clearable
              />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Business Impact</label>
              <el-select v-model="faultData.businessImpact" placeholder="Select Impact Level" clearable style="width: 100%">
                <el-option label="Critical - Operations Stopped" value="Critical - Operations Stopped" />
                <el-option label="High - Major Disruption" value="High - Major Disruption" />
                <el-option label="Medium - Partial Impact" value="Medium - Partial Impact" />
                <el-option label="Low - Minor Impact" value="Low - Minor Impact" />
              </el-select>
            </div>
            <div class="form-group">
              <label>Estimated Downtime</label>
              <el-input
                  v-model="faultData.estimatedDowntime"
                  placeholder="e.g., 2 hours"
                  clearable
              />
              <div class="form-hint">e.g., "2 hours", "30 minutes", "Until repaired"</div>
            </div>
          </div>
        </div>

        <div class="form-section">
          <h3>Root Cause Analysis (Optional)</h3>
          <div class="form-row">
            <div class="form-group full">
              <label>Initial RCA Notes</label>
              <el-input
                  v-model="faultData.rcaNotes"
                  type="textarea"
                  :rows="3"
                  placeholder="Initial thoughts on possible root causes..."
              />
              <div class="form-hint">Example: "Cooling tower fan bearing failure suspected. Vibration levels elevated."</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Step 4: Review & Submit -->
      <div v-show="currentStep === 4" class="form-step">
        <el-alert
            title="Ready to Submit"
            type="success"
            :closable="false"
            show-icon
            class="guide-alert"
        >
          <template #default>
            <p>Please review all information before submitting. Click "Create Fault" to finalize.</p>
          </template>
        </el-alert>

        <div class="review-section">
          <h3>Review Fault Information</h3>
          <div class="review-card">
            <div class="review-header">
              <span class="review-title">Fault Details</span>
              <el-button link type="primary" size="small" @click="currentStep = 1">Edit</el-button>
            </div>
            <el-descriptions :column="2" border size="small">
              <el-descriptions-item label="Title">{{ faultData.title || '—' }}</el-descriptions-item>
              <el-descriptions-item label="Category">{{ faultData.category || '—' }}</el-descriptions-item>
              <el-descriptions-item label="Asset">{{ faultData.asset || '—' }}</el-descriptions-item>
              <el-descriptions-item label="Location">{{ faultData.location || '—' }}</el-descriptions-item>
              <el-descriptions-item label="Description" :span="2">{{ faultData.description || '—' }}</el-descriptions-item>
              <el-descriptions-item label="Detected">{{ formatDateTime(faultData.detectedAt) }}</el-descriptions-item>
              <el-descriptions-item label="Reported By">{{ faultData.reportedBy || '—' }}</el-descriptions-item>
              <el-descriptions-item label="Symptoms">{{ faultData.symptoms || '—' }}</el-descriptions-item>
              <el-descriptions-item label="Error Code">{{ faultData.errorCode || '—' }}</el-descriptions-item>
            </el-descriptions>
          </div>

          <div class="review-card">
            <div class="review-header">
              <span class="review-title">Assignment & Priority</span>
              <el-button link type="primary" size="small" @click="currentStep = 2">Edit</el-button>
            </div>
            <el-descriptions :column="2" border size="small">
              <el-descriptions-item label="Assigned To">{{ faultData.assignedTo || 'Unassigned' }}</el-descriptions-item>
              <el-descriptions-item label="Team">{{ faultData.team || '—' }}</el-descriptions-item>
              <el-descriptions-item label="Severity">
                <el-tag :type="getSeverityTagType(faultData.severity)" size="small">{{ faultData.severity?.toUpperCase() || '—' }}</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="Priority">Level {{ faultData.priority }}</el-descriptions-item>
              <el-descriptions-item label="SLA Target">{{ faultData.slaTarget }} hours</el-descriptions-item>
              <el-descriptions-item label="Expected Resolution">{{ faultData.expectedResolution || '—' }}</el-descriptions-item>
            </el-descriptions>
          </div>

          <div class="review-card">
            <div class="review-header">
              <span class="review-title">Impact Analysis</span>
              <el-button link type="primary" size="small" @click="currentStep = 3">Edit</el-button>
            </div>
            <el-descriptions :column="2" border size="small">
              <el-descriptions-item label="Affected Systems">{{ faultData.affectedSystems || '—' }}</el-descriptions-item>
              <el-descriptions-item label="Affected Zones">{{ faultData.affectedZones || '—' }}</el-descriptions-item>
              <el-descriptions-item label="Business Impact">{{ faultData.businessImpact || '—' }}</el-descriptions-item>
              <el-descriptions-item label="Est. Downtime">{{ faultData.estimatedDowntime || '—' }}</el-descriptions-item>
            </el-descriptions>
          </div>
        </div>
      </div>

      <!-- Navigation Buttons -->
      <div class="form-navigation">
        <el-button class="nav-btn prev" @click="prevStep" :disabled="currentStep === 1">
          <el-icon><ArrowLeft /></el-icon> Previous
        </el-button>
        <el-button v-if="currentStep < 4" type="primary" class="nav-btn next" @click="nextStep">
          Next <el-icon><ArrowRight /></el-icon>
        </el-button>
        <el-button v-if="currentStep === 4" type="success" class="nav-btn submit" @click="submitFault" :loading="submitting">
          <el-icon><Check /></el-icon> Create Fault
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import {
  Refresh, Check, WarningFilled, CircleCloseFilled, InfoFilled,
  ArrowLeft, ArrowRight
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'

const router = useRouter()

// Loading State
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const submitting = ref(false)
const loadingMessages = ['Preparing...', 'Loading workflow...', 'Initializing form...', 'Almost ready...']

// Current step
const currentStep = ref(1)

// Fault Data with default example values
const faultData = ref({
  title: 'Chiller-02 High Pressure Trip',
  category: 'HVAC',
  asset: 'Chiller-02',
  location: 'Building A - Plant Room',
  description: 'Chiller tripped on high pressure alarm at 08:23 this morning. Cooling tower fan was not running. Condenser water flow was 45% below normal. Building temperature is rising.',
  detectedAt: new Date(new Date().setHours(8, 23, 0)).toISOString().slice(0, 19),
  reportedBy: 'John Smith',
  symptoms: 'High pressure alarm, cooling tower fan not running, building temperature rising',
  errorCode: 'CH-102',
  sensorReadings: 'Pressure: 220PSI, Flow: 45%, Temperature: 38°C',
  assignedTo: 'Mike Johnson',
  team: 'HVAC Team',
  severity: 'critical',
  priority: 5,
  slaTarget: 4,
  expectedResolution: new Date(new Date().setDate(new Date().getDate() + 1)).toISOString().slice(0, 10),
  affectedSystems: 'Building A HVAC, Chilled Water System',
  affectedZones: 'Building A - All Floors',
  businessImpact: 'High - Major Disruption',
  estimatedDowntime: '4 hours',
  rcaNotes: 'Cooling tower fan bearing failure suspected. Vibration levels elevated.'
})

// Helper Functions
const formatDateTime = (dateTime: string) => {
  if (!dateTime) return '—'
  return dateTime.replace('T', ' ')
}

const getSeverityTagType = (severity: string) => {
  const map: Record<string, string> = {
    critical: 'danger',
    major: 'warning',
    minor: 'info'
  }
  return map[severity] || 'info'
}

// Validation
const validateStep1 = () => {
  if (!faultData.value.title) {
    ElMessage.warning('Please enter fault title')
    return false
  }
  if (!faultData.value.category) {
    ElMessage.warning('Please select category')
    return false
  }
  if (!faultData.value.description) {
    ElMessage.warning('Please enter fault description')
    return false
  }
  if (!faultData.value.detectedAt) {
    ElMessage.warning('Please select detected date/time')
    return false
  }
  return true
}

const validateStep2 = () => {
  if (!faultData.value.severity) {
    ElMessage.warning('Please select severity')
    return false
  }
  return true
}

// Navigation
const nextStep = () => {
  if (currentStep.value === 1 && !validateStep1()) return
  if (currentStep.value === 2 && !validateStep2()) return
  if (currentStep.value < 4) {
    currentStep.value++
  }
}

const prevStep = () => {
  if (currentStep.value > 1) {
    currentStep.value--
  }
}

const resetForm = () => {
  ElMessageBox.confirm('Reset all form fields?', 'Confirm', { type: 'warning' })
      .then(() => {
        faultData.value = {
          title: 'Chiller-02 High Pressure Trip',
          category: 'HVAC',
          asset: 'Chiller-02',
          location: 'Building A - Plant Room',
          description: 'Chiller tripped on high pressure alarm at 08:23 this morning. Cooling tower fan was not running. Condenser water flow was 45% below normal. Building temperature is rising.',
          detectedAt: new Date(new Date().setHours(8, 23, 0)).toISOString().slice(0, 19),
          reportedBy: 'John Smith',
          symptoms: 'High pressure alarm, cooling tower fan not running, building temperature rising',
          errorCode: 'CH-102',
          sensorReadings: 'Pressure: 220PSI, Flow: 45%, Temperature: 38°C',
          assignedTo: 'Mike Johnson',
          team: 'HVAC Team',
          severity: 'critical',
          priority: 5,
          slaTarget: 4,
          expectedResolution: new Date(new Date().setDate(new Date().getDate() + 1)).toISOString().slice(0, 10),
          affectedSystems: 'Building A HVAC, Chilled Water System',
          affectedZones: 'Building A - All Floors',
          businessImpact: 'High - Major Disruption',
          estimatedDowntime: '4 hours',
          rcaNotes: 'Cooling tower fan bearing failure suspected. Vibration levels elevated.'
        }
        currentStep.value = 1
        ElMessage.success('Form reset to example values')
      })
      .catch(() => {})
}

const submitFault = async () => {
  if (!validateStep1() || !validateStep2()) {
    currentStep.value = 1
    return
  }

  submitting.value = true
  await new Promise(resolve => setTimeout(resolve, 1500))

  const faultId = Math.floor(Math.random() * 9000) + 1000
  ElMessage.success(`Fault #${faultId} created successfully`)

  setTimeout(() => {
    router.push('/fault-management-system/active-faults')
  }, 1000)
}

// Lifecycle
onMounted(() => {
  let idx = 0
  const msgInterval = setInterval(() => {
    if (idx < loadingMessages.length - 1) {
      idx++
      loadingMessage.value = loadingMessages[idx]
    }
  }, 400)
  const progInterval = setInterval(() => {
    if (loadingProgress.value < 100) {
      loadingProgress.value += Math.random() * 15 + 5
      if (loadingProgress.value > 100) loadingProgress.value = 100
    }
  }, 200)
  setTimeout(() => {
    clearInterval(msgInterval)
    clearInterval(progInterval)
    loadingProgress.value = 100
    loadingMessage.value = 'Ready!'
    setTimeout(() => {
      isLoaded.value = true
    }, 400)
  }, 2000)
})
</script>

<style scoped>
/* Loading Screen - 保持不变 */
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

/* Main Content */
.new-fault-page {
  padding: 24px;
  background: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}
.title-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: linear-gradient(135deg, #ef4444, #dc2626);
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  color: white;
  margin-bottom: 12px;
}
.header-title h1 {
  font-size: 28px;
  font-weight: 700;
  color: #1a1a2e;
  margin: 0 0 8px 0;
}
.header-title .subtitle {
  font-size: 14px;
  color: #64748b;
  margin: 0;
}
.header-actions {
  display: flex;
  gap: 12px;
}
.action-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid #e2e8f0;
  background: white;
  color: #475569;
}
.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
.action-btn.primary {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  border: none;
  color: white;
}
.action-btn.primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(59, 130, 246, 0.3);
}

/* Workflow Steps */
.workflow-steps {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 32px;
  padding: 20px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}
.step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}
.step-number {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #e2e8f0;
  color: #64748b;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  transition: all 0.3s;
}
.step.active .step-number {
  background: #3b82f6;
  color: white;
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.2);
}
.step.completed .step-number {
  background: #10b981;
  color: white;
}
.step-label {
  font-size: 12px;
  color: #64748b;
}
.step.active .step-label {
  color: #1a1a2e;
  font-weight: 500;
}
.step-line {
  width: 80px;
  height: 2px;
  background: #e2e8f0;
  margin: 0 8px;
  transition: all 0.3s;
}
.step-line.active {
  background: #10b981;
}

/* Form Container */
.form-container {
  background: white;
  border-radius: 20px;
  padding: 28px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

/* Guide Alert */
.guide-alert {
  margin-bottom: 24px;
}
.guide-alert ul {
  margin: 8px 0 0 20px;
  padding: 0;
}
.guide-alert li {
  margin: 4px 0;
  font-size: 13px;
}

.form-section {
  margin-bottom: 32px;
  padding-bottom: 24px;
  border-bottom: 1px solid #e2e8f0;
}
.form-section:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}
.form-section h3 {
  font-size: 16px;
  font-weight: 600;
  color: #1a1a2e;
  margin: 0 0 20px 0;
}
.form-row {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}
.form-group {
  flex: 1;
  min-width: 200px;
}
.form-group.full {
  width: 100%;
}
.form-group label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: #475569;
  margin-bottom: 6px;
}
.required {
  color: #ef4444;
}
.form-hint {
  font-size: 11px;
  color: #94a3b8;
  margin-top: 4px;
}

/* Priority Buttons */
.priority-buttons {
  display: flex;
  gap: 12px;
}
.priority-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px;
  border: 2px solid #e2e8f0;
  background: white;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 13px;
  font-weight: 500;
  color: #64748b;
}
.priority-btn.active {
  border-color: #3b82f6;
  background: #eff6ff;
  color: #2563eb;
}
.priority-btn:first-child.active { border-color: #ef4444; background: #fef2f2; color: #dc2626; }
.priority-btn:last-child.active { border-color: #10b981; background: #ecfdf5; color: #059669; }

/* Review Section */
.review-section h3 {
  font-size: 16px;
  font-weight: 600;
  color: #1a1a2e;
  margin: 0 0 20px 0;
}
.review-card {
  background: #f8fafc;
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 20px;
}
.review-card:last-child {
  margin-bottom: 0;
}
.review-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e2e8f0;
}
.review-title {
  font-weight: 600;
  color: #1a1a2e;
}

/* Navigation Buttons */
.form-navigation {
  display: flex;
  justify-content: space-between;
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid #e2e8f0;
}
.nav-btn {
  display: flex;
  align-items: center;
  gap: 8px;
}
.nav-btn.prev {
  background: #f1f5f9;
  color: #475569;
}
.nav-btn.prev:hover:not(:disabled) {
  background: #e2e8f0;
}

:deep(.el-descriptions) {
  margin-top: 8px;
}
:deep(.el-descriptions__label) {
  width: 120px;
}
</style>