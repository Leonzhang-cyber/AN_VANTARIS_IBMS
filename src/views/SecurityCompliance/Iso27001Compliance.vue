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
          <span class="loading-title">Loading ISO27001 Compliance</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
        <div class="loading-subtip">ISO/IEC 27001 Information Security Management System</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="iso-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <h2 class="page-title">ISO 27001 Compliance</h2>
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/' }">Home</el-breadcrumb-item>
          <el-breadcrumb-item>Security & Compliance</el-breadcrumb-item>
          <el-breadcrumb-item>ISO 27001 Compliance</el-breadcrumb-item>
        </el-breadcrumb>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="runInternalAudit">
          <el-icon><Refresh /></el-icon>
          Run Internal Audit
        </el-button>
        <el-button type="success" plain @click="exportComplianceReport">
          <el-icon><Download /></el-icon>
          Export Report
        </el-button>
        <el-button type="info" plain @click="viewCertificationStatus">
          <el-icon><Medal /></el-icon>
          Certification Status
        </el-button>
      </div>
    </div>

    <!-- Certification Status Banner -->
    <el-card class="cert-banner" shadow="hover">
      <div class="cert-content">
        <div class="cert-icon">
          <el-icon :size="48"><Medal /></el-icon>
        </div>
        <div class="cert-info">
          <div class="cert-title">ISO 27001:2022 Certification</div>
          <div class="cert-status">
            <el-tag type="success" size="large">Certified</el-tag>
            <span class="cert-dates">Valid until: December 31, 2025</span>
          </div>
          <div class="cert-details">Certification Body: BSI Group | Certificate No: IS 123456</div>
        </div>
        <el-button type="primary" plain @click="downloadCertificate">Download Certificate</el-button>
      </div>
    </el-card>

    <!-- Overall Compliance Score -->
    <div class="score-section">
      <el-card class="score-card" shadow="hover">
        <div class="score-content">
          <div class="score-gauge">
            <el-progress type="circle" :percentage="overallCompliance" :width="160" :stroke-width="12" :color="getScoreColor(overallCompliance)">
              <template #default>
                <div class="score-text">
                  <span class="score-value">{{ overallCompliance }}%</span>
                  <span class="score-label">Overall Compliance</span>
                </div>
              </template>
            </el-progress>
          </div>
          <div class="score-details">
            <div class="detail-item">
              <div class="detail-label">Controls Implemented</div>
              <div class="detail-value">{{ controlsImplemented }}/{{ totalControls }}</div>
            </div>
            <div class="detail-item">
              <div class="detail-label">Risk Assessment Score</div>
              <div class="detail-value">{{ riskScore }}%</div>
            </div>
            <div class="detail-item">
              <div class="detail-label">Last Surveillance Audit</div>
              <div class="detail-value">{{ lastAuditDate }}</div>
            </div>
            <div class="detail-item">
              <div class="detail-label">Next Recertification</div>
              <div class="detail-value">{{ nextRecertDate }}</div>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- ISO 27001:2022 Control Clauses -->
    <div class="clauses-section">
      <h3 class="section-title">ISO 27001:2022 Control Clauses</h3>
      <div class="clauses-grid">
        <el-card v-for="clause in clauses" :key="clause.id" class="clause-card" shadow="hover" @click="viewClauseDetails(clause)">
          <div class="clause-header">
            <div class="clause-number">{{ clause.number }}</div>
            <el-tag :type="getClauseStatusType(clause.status)" size="small">{{ clause.status }}</el-tag>
          </div>
          <h4 class="clause-title">{{ clause.title }}</h4>
          <div class="clause-progress">
            <el-progress :percentage="clause.progress" :stroke-width="8" :color="getScoreColor(clause.progress)" />
          </div>
          <div class="clause-stats">{{ clause.compliant }}/{{ clause.total }} controls implemented</div>
        </el-card>
      </div>
    </div>

    <!-- Annex A Controls by Domain -->
    <div class="controls-section">
      <h3 class="section-title">Annex A Controls by Domain</h3>
      <el-tabs v-model="activeDomain" type="border-card" class="domain-tabs">
        <el-tab-pane v-for="domain in annexDomains" :key="domain.id" :name="domain.id">
          <template #label>
            <div class="domain-tab-label">
              <el-icon><component :is="domain.icon" /></el-icon>
              <span>{{ domain.name }}</span>
              <el-tag :type="domain.compliance >= 80 ? 'success' : domain.compliance >= 60 ? 'warning' : 'danger'" size="small">
                {{ domain.compliance }}%
              </el-tag>
            </div>
          </template>
          <div class="domain-content">
            <div class="domain-description">{{ domain.description }}</div>
            <div class="controls-table">
              <el-table :data="domain.controls" stripe style="width: 100%">
                <el-table-column prop="ref" label="Control Ref" width="120" />
                <el-table-column prop="name" label="Control Name" min-width="250" />
                <el-table-column prop="status" label="Status" width="120" align="center">
                  <template #default="{ row }">
                    <el-tag :type="getStatusType(row.status)" size="small">{{ row.status }}</el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="implementation" label="Implementation" width="150" align="center">
                  <template #default="{ row }">
                    <el-progress :percentage="row.implementation" :stroke-width="6" :show-text="true" :format="(p) => `${p}%`" />
                  </template>
                </el-table-column>
                <el-table-column label="Evidence" width="100" align="center">
                  <template #default="{ row }">
                    <el-button v-if="row.evidence" text type="primary" size="small" @click="viewEvidence(row)">View</el-button>
                    <el-button v-else text type="info" size="small" @click="uploadEvidence(row)">Upload</el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>

    <!-- Risk Assessment & Treatment -->
    <div class="risk-section">
      <el-card class="risk-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span><el-icon><Warning /></el-icon> Risk Assessment & Treatment</span>
            <el-button type="primary" size="small" @click="newRiskAssessment">New Assessment</el-button>
          </div>
        </template>
        <div class="risk-matrix">
          <div class="risk-summary">
            <div class="risk-stats">
              <div class="risk-stat">
                <div class="stat-number critical">{{ riskSummary.critical }}</div>
                <div class="stat-label">Critical Risks</div>
              </div>
              <div class="risk-stat">
                <div class="stat-number high">{{ riskSummary.high }}</div>
                <div class="stat-label">High Risks</div>
              </div>
              <div class="risk-stat">
                <div class="stat-number medium">{{ riskSummary.medium }}</div>
                <div class="stat-label">Medium Risks</div>
              </div>
              <div class="risk-stat">
                <div class="stat-number low">{{ riskSummary.low }}</div>
                <div class="stat-label">Low Risks</div>
              </div>
            </div>
            <div ref="riskChartRef" class="risk-chart"></div>
          </div>
          <div class="risk-list">
            <div v-for="risk in topRisks" :key="risk.id" class="risk-item">
              <div class="risk-level" :class="risk.level">
                {{ risk.level }}
              </div>
              <div class="risk-info">
                <div class="risk-title">{{ risk.title }}</div>
                <div class="risk-description">{{ risk.description }}</div>
                <div class="risk-meta">
                  <span>Likelihood: {{ risk.likelihood }}</span>
                  <span>Impact: {{ risk.impact }}</span>
                  <span>Residual Score: {{ risk.residualScore }}</span>
                </div>
              </div>
              <div class="risk-status">
                <el-tag :type="getRiskStatusType(risk.treatment)" size="small">{{ risk.treatment }}</el-tag>
              </div>
              <el-button size="small" type="primary" plain @click="treatRisk(risk)">Treat</el-button>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Statement of Applicability & Audit Trail -->
    <div class="soa-section">
      <el-card class="soa-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span><el-icon><Document /></el-icon> Statement of Applicability (SoA)</span>
            <el-button text type="primary" @click="viewFullSoA">View Full SoA</el-button>
          </div>
        </template>
        <div class="soa-content">
          <div class="soa-summary">
            <div class="soa-item">
              <span class="soa-label">Total Annex A Controls:</span>
              <span class="soa-value">93</span>
            </div>
            <div class="soa-item">
              <span class="soa-label">Applicable Controls:</span>
              <span class="soa-value">{{ applicableControls }}</span>
            </div>
            <div class="soa-item">
              <span class="soa-label">Implemented:</span>
              <span class="soa-value">{{ implementedControls }}</span>
            </div>
            <div class="soa-item">
              <span class="soa-label">Justified Exclusions:</span>
              <span class="soa-value">{{ justifiedExclusions }}</span>
            </div>
          </div>
          <el-table :data="soaControls" stripe style="width: 100%" max-height="300">
            <el-table-column prop="ref" label="Control" width="100" />
            <el-table-column prop="name" label="Control Name" min-width="200" />
            <el-table-column prop="applicable" label="Applicable" width="100" align="center">
              <template #default="{ row }">
                <el-tag :type="row.applicable ? 'success' : 'info'" size="small">{{ row.applicable ? 'Yes' : 'No' }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="justification" label="Justification" min-width="200" show-overflow-tooltip />
            <el-table-column label="Evidence" width="80" align="center">
              <template #default="{ row }">
                <el-link v-if="row.evidence" type="primary" @click="viewSoaEvidence(row)">Link</el-link>
                <span v-else>-</span>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-card>
    </div>

    <!-- Audit Timeline -->
    <div class="audit-section">
      <el-card class="audit-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span><el-icon><Clock /></el-icon> Internal Audit Timeline</span>
            <el-button text type="primary" @click="scheduleAudit">Schedule Audit</el-button>
          </div>
        </template>
        <div class="audit-timeline">
          <el-timeline>
            <el-timeline-item v-for="audit in auditHistory" :key="audit.id" :type="audit.type" :timestamp="audit.date" placement="top" size="large">
              <el-card shadow="hover" class="audit-item-card">
                <div class="audit-header">
                  <span class="audit-title">{{ audit.title }}</span>
                  <el-tag :type="audit.result === 'Pass' ? 'success' : audit.result === 'Fail' ? 'danger' : 'warning'" size="small">
                    {{ audit.result }}
                  </el-tag>
                </div>
                <div class="audit-scope">Scope: {{ audit.scope }}</div>
                <div class="audit-findings" v-if="audit.findings">
                  <span>Findings: {{ audit.findings }}</span>
                  <span>Non-conformities: {{ audit.ncCount }}</span>
                </div>
                <div class="audit-auditor">Auditor: {{ audit.auditor }}</div>
              </el-card>
            </el-timeline-item>
          </el-timeline>
        </div>
      </el-card>
    </div>

    <!-- Management Review & Continuous Improvement -->
    <div class="management-section">
      <el-card class="management-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span><el-icon><TrendCharts /></el-icon> Management Review & Improvement</span>
            <el-button type="primary" size="small" @click="newManagementReview">New Review</el-button>
          </div>
        </template>
        <div class="management-content">
          <div class="review-stats">
            <div class="review-item">
              <div class="review-label">Last Management Review</div>
              <div class="review-value">{{ lastManagementReview }}</div>
            </div>
            <div class="review-item">
              <div class="review-label">Review Frequency</div>
              <div class="review-value">Quarterly</div>
            </div>
            <div class="review-item">
              <div class="review-label">Open Action Items</div>
              <div class="review-value critical">{{ openActionItems }}</div>
            </div>
            <div class="review-item">
              <div class="review-label">Completed Actions (YTD)</div>
              <div class="review-value success">{{ completedActions }}</div>
            </div>
          </div>
          <div class="action-items">
            <h4>Open Action Items</h4>
            <div v-for="item in actionItems" :key="item.id" class="action-item">
              <el-checkbox :value="item.completed" @change="(val) => updateActionItem(item, val)">
                {{ item.description }}
              </el-checkbox>
              <div class="action-meta">
                <span>Due: {{ item.dueDate }}</span>
                <span>Owner: {{ item.owner }}</span>
                <span class="action-priority" :class="item.priority">{{ item.priority }}</span>
              </div>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Quick Actions Footer -->
    <div class="footer-actions">
      <div class="action-group">
        <el-button type="primary" plain @click="uploadDocumentation">
          <el-icon><Upload /></el-icon>
          Upload Documentation
        </el-button>
        <el-button type="success" plain @click="generateSoa">
          <el-icon><Document /></el-icon>
          Generate SoA
        </el-button>
        <el-button type="warning" plain @click="conductRiskAssessment">
          <el-icon><Warning /></el-icon>
          Conduct Risk Assessment
        </el-button>
        <el-button type="info" plain @click="viewTrainingRecords">
          <el-icon><Reading /></el-icon>
          Training Records
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import {
  Refresh, Download, Medal, Warning, Document, Clock, TrendCharts,
  Upload, Reading, Lock, Key, Monitor, Setting, Grid, Share, Files, User, Search
} from '@element-plus/icons-vue'

// Loading state
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading ISO27001 Compliance Framework...')

const loadingMessages = [
  'Loading ISO27001 Compliance Framework...',
  'Analyzing controls implementation...',
  'Reviewing risk assessment...',
  'ISMS dashboard ready!'
]

// Compliance data
const overallCompliance = ref(87)
const controlsImplemented = ref(81)
const totalControls = ref(93)
const riskScore = ref(78)
const lastAuditDate = ref('2024-01-15')
const nextRecertDate = ref('2025-12-31')
const applicableControls = ref(89)
const implementedControls = ref(81)
const justifiedExclusions = ref(4)
const lastManagementReview = ref('2024-01-20')
const openActionItems = ref(8)
const completedActions = ref(24)

// ISO 27001:2022 Clauses
const clauses = ref([
  { id: 1, number: '4', title: 'Context of the Organization', progress: 95, compliant: 5, total: 5, status: 'Compliant' },
  { id: 2, number: '5', title: 'Leadership', progress: 100, compliant: 3, total: 3, status: 'Compliant' },
  { id: 3, number: '6', title: 'Planning', progress: 88, compliant: 7, total: 8, status: 'Compliant' },
  { id: 4, number: '7', title: 'Support', progress: 85, compliant: 11, total: 13, status: 'Partial' },
  { id: 5, number: '8', title: 'Operation', progress: 82, compliant: 18, total: 22, status: 'Partial' },
  { id: 6, number: '9', title: 'Performance Evaluation', progress: 90, compliant: 7, total: 8, status: 'Compliant' },
  { id: 7, number: '10', title: 'Improvement', progress: 75, compliant: 6, total: 8, status: 'Partial' }
])

// Annex A Domains
const annexDomains = ref([
  {
    id: 'domain-1',
    name: 'Organizational Controls',
    icon: 'User',
    description: 'Information security policies, roles, responsibilities, and awareness',
    compliance: 85,
    controls: [
      { ref: 'A.5.1', name: 'Policies for information security', status: 'Implemented', implementation: 100, evidence: 'policy.pdf' },
      { ref: 'A.5.2', name: 'Information security roles and responsibilities', status: 'Implemented', implementation: 100, evidence: 'roles.pdf' },
      { ref: 'A.5.3', name: 'Segregation of duties', status: 'Implemented', implementation: 95, evidence: 'sod_matrix.pdf' },
      { ref: 'A.5.4', name: 'Management responsibilities', status: 'Partial', implementation: 70, evidence: null },
      { ref: 'A.5.5', name: 'Contact with authorities', status: 'Implemented', implementation: 100, evidence: 'contacts.pdf' },
      { ref: 'A.5.6', name: 'Contact with special interest groups', status: 'Implemented', implementation: 90, evidence: null },
      { ref: 'A.5.7', name: 'Threat intelligence', status: 'Partial', implementation: 65, evidence: null },
      { ref: 'A.5.8', name: 'Information security in project management', status: 'Not Implemented', implementation: 30, evidence: null }
    ]
  },
  {
    id: 'domain-2',
    name: 'People Controls',
    icon: 'UserFilled',
    description: 'Employee screening, termination, awareness, and remote work',
    compliance: 82,
    controls: [
      { ref: 'A.6.1', name: 'Screening', status: 'Implemented', implementation: 100, evidence: 'screening_policy.pdf' },
      { ref: 'A.6.2', name: 'Terms and conditions of employment', status: 'Implemented', implementation: 100, evidence: 'employment_contracts.pdf' },
      { ref: 'A.6.3', name: 'Information security awareness', status: 'Partial', implementation: 75, evidence: 'training_records.pdf' },
      { ref: 'A.6.4', name: 'Disciplinary process', status: 'Implemented', implementation: 95, evidence: 'disciplinary_policy.pdf' },
      { ref: 'A.6.5', name: 'Responsibilities after termination', status: 'Implemented', implementation: 100, evidence: 'offboarding.pdf' },
      { ref: 'A.6.6', name: 'Remote working', status: 'Partial', implementation: 60, evidence: null }
    ]
  },
  {
    id: 'domain-3',
    name: 'Physical Controls',
    icon: 'Lock',
    description: 'Physical security, equipment security, and secure areas',
    compliance: 90,
    controls: [
      { ref: 'A.7.1', name: 'Physical security perimeter', status: 'Implemented', implementation: 100, evidence: 'perimeter_diagram.pdf' },
      { ref: 'A.7.2', name: 'Physical entry controls', status: 'Implemented', implementation: 100, evidence: 'access_control.pdf' },
      { ref: 'A.7.3', name: 'Securing offices, rooms and facilities', status: 'Implemented', implementation: 95, evidence: null },
      { ref: 'A.7.4', name: 'Protecting against external threats', status: 'Implemented', implementation: 100, evidence: 'security_assessment.pdf' },
      { ref: 'A.7.5', name: 'Working in secure areas', status: 'Implemented', implementation: 90, evidence: 'secure_area_policy.pdf' },
      { ref: 'A.7.6', name: 'Delivery and loading areas', status: 'Partial', implementation: 70, evidence: null },
      { ref: 'A.7.7', name: 'Clear desk and clear screen', status: 'Implemented', implementation: 85, evidence: 'clear_desk_policy.pdf' }
    ]
  },
  {
    id: 'domain-4',
    name: 'Technological Controls',
    icon: 'Monitor',
    description: 'User access, malware, backups, logging, and network security',
    compliance: 74,
    controls: [
      { ref: 'A.8.1', name: 'User endpoint devices', status: 'Implemented', implementation: 90, evidence: 'endpoint_policy.pdf' },
      { ref: 'A.8.2', name: 'Privileged access rights', status: 'Partial', implementation: 65, evidence: null },
      { ref: 'A.8.3', name: 'Information access restriction', status: 'Implemented', implementation: 85, evidence: 'access_control_policy.pdf' },
      { ref: 'A.8.4', name: 'Access to source code', status: 'Partial', implementation: 60, evidence: null },
      { ref: 'A.8.5', name: 'Secure authentication', status: 'Implemented', implementation: 80, evidence: 'mfa_policy.pdf' },
      { ref: 'A.8.6', name: 'Capacity management', status: 'Implemented', implementation: 75, evidence: null },
      { ref: 'A.8.7', name: 'Protection against malware', status: 'Implemented', implementation: 95, evidence: 'antivirus_config.pdf' },
      { ref: 'A.8.8', name: 'Management of technical vulnerabilities', status: 'Partial', implementation: 55, evidence: null },
      { ref: 'A.8.9', name: 'Configuration management', status: 'Partial', implementation: 50, evidence: null }
    ]
  }
])

const activeDomain = ref('domain-1')

// Risk data
const riskSummary = ref({
  critical: 3,
  high: 7,
  medium: 12,
  low: 18
})

const topRisks = ref([
  { id: 1, level: 'critical', title: 'Ransomware Attack Vulnerability', description: 'Current backup strategy may not protect against sophisticated ransomware', likelihood: 'High', impact: 'High', residualScore: 16, treatment: 'Mitigation' },
  { id: 2, level: 'high', title: 'Privileged Account Misuse', description: 'Lack of monitoring for privileged user activities', likelihood: 'Medium', impact: 'High', residualScore: 12, treatment: 'Mitigation' },
  { id: 3, level: 'high', title: 'Third-Party Data Breach', description: 'Insufficient vendor security assessments', likelihood: 'High', impact: 'Medium', residualScore: 12, treatment: 'Transfer' },
  { id: 4, level: 'medium', title: 'Social Engineering Attacks', description: 'Insufficient employee awareness training', likelihood: 'Medium', impact: 'Medium', residualScore: 9, treatment: 'Mitigation' },
  { id: 5, level: 'medium', title: 'Data Leakage via Cloud', description: 'Cloud storage policies not fully enforced', likelihood: 'Low', impact: 'High', residualScore: 8, treatment: 'Accept' }
])

// SoA Controls
const soaControls = ref([
  { ref: 'A.5.1', name: 'Policies for information security', applicable: true, justification: 'Mandatory for ISMS', evidence: 'policy_v3.pdf' },
  { ref: 'A.5.2', name: 'Information security roles and responsibilities', applicable: true, justification: 'Required for accountability', evidence: 'roles_matrix.pdf' },
  { ref: 'A.5.3', name: 'Segregation of duties', applicable: true, justification: 'Prevents conflict of interest', evidence: 'sod_policy.pdf' },
  { ref: 'A.5.4', name: 'Management responsibilities', applicable: true, justification: 'Leadership commitment required', evidence: null },
  { ref: 'A.8.10', name: 'Information deletion', applicable: false, justification: 'Not applicable - no sensitive data on removable media', evidence: null },
  { ref: 'A.8.11', name: 'Data masking', applicable: false, justification: 'Not required - no production data in non-production', evidence: null }
])

// Audit history
const auditHistory = ref([
  { id: 1, title: 'Surveillance Audit - Stage 1', date: '2024-01-15', scope: 'ISMS documentation and management review', findings: '2 minor non-conformities', ncCount: 2, auditor: 'BSI Group', result: 'Pass', type: 'success' },
  { id: 2, title: 'Internal Audit - Q4 2023', date: '2023-12-10', scope: 'All Annex A controls', findings: '5 observations', ncCount: 0, auditor: 'Internal Audit Team', result: 'Pass', type: 'success' },
  { id: 3, title: 'Internal Audit - Q3 2023', date: '2023-09-15', scope: 'Operational controls (Clause 8)', findings: '3 minor non-conformities', ncCount: 3, auditor: 'Internal Audit Team', result: 'Pass with NCs', type: 'warning' },
  { id: 4, title: 'Internal Audit - Q2 2023', date: '2023-06-20', scope: 'Leadership and Planning (Clauses 5-6)', findings: '0 findings', ncCount: 0, auditor: 'Internal Audit Team', result: 'Pass', type: 'success' }
])

// Action items
const actionItems = ref([
  { id: 1, description: 'Update incident response playbook to include ransomware scenarios', dueDate: '2024-02-15', owner: 'Security Team', priority: 'high', completed: false },
  { id: 2, description: 'Implement MFA for all remote access users', dueDate: '2024-01-30', owner: 'IT Operations', priority: 'critical', completed: false },
  { id: 3, description: 'Conduct vendor security assessments for top 10 suppliers', dueDate: '2024-03-01', owner: 'Procurement', priority: 'high', completed: false },
  { id: 4, description: 'Update asset inventory with cloud resources', dueDate: '2024-02-28', owner: 'Asset Management', priority: 'medium', completed: false },
  { id: 5, description: 'Schedule annual information security awareness training', dueDate: '2024-06-01', owner: 'HR', priority: 'medium', completed: true }
])

// Chart refs
const riskChartRef = ref<HTMLElement>()
let riskChart: echarts.ECharts | null = null

// Helper functions
const getScoreColor = (score: number) => {
  if (score >= 80) return '#10b981'
  if (score >= 60) return '#3b82f6'
  if (score >= 40) return '#f59e0b'
  return '#ef4444'
}

const getClauseStatusType = (status: string) => {
  switch (status) {
    case 'Compliant': return 'success'
    case 'Partial': return 'warning'
    case 'Non-Compliant': return 'danger'
    default: return 'info'
  }
}

const getStatusType = (status: string) => {
  switch (status) {
    case 'Implemented': return 'success'
    case 'Partial': return 'warning'
    case 'Not Implemented': return 'danger'
    default: return 'info'
  }
}

const getRiskStatusType = (treatment: string) => {
  switch (treatment) {
    case 'Mitigation': return 'warning'
    case 'Transfer': return 'info'
    case 'Accept': return 'success'
    default: return 'info'
  }
}

// Initialize risk chart
const initRiskChart = () => {
  if (!riskChartRef.value) return
  riskChart = echarts.init(riskChartRef.value)
  const option = {
    tooltip: { trigger: 'item' },
    legend: { orient: 'vertical', left: 'left' },
    series: [{
      type: 'pie',
      radius: '55%',
      data: [
        { value: riskSummary.value.critical, name: 'Critical', itemStyle: { color: '#ef4444' } },
        { value: riskSummary.value.high, name: 'High', itemStyle: { color: '#f59e0b' } },
        { value: riskSummary.value.medium, name: 'Medium', itemStyle: { color: '#eab308' } },
        { value: riskSummary.value.low, name: 'Low', itemStyle: { color: '#10b981' } }
      ],
      label: { formatter: '{b}: {d}%' },
      emphasis: { scale: true }
    }]
  }
  riskChart.setOption(option)
}

// Event handlers
const runInternalAudit = () => {
  ElMessage.info('Internal audit initiated. Checking all controls...')
  setTimeout(() => {
    ElMessage.success('Internal audit completed. 2 minor non-conformities found.')
  }, 3000)
}

const exportComplianceReport = () => {
  ElMessage.info('Exporting compliance report...')
  setTimeout(() => {
    ElMessage.success('Report exported successfully')
  }, 2000)
}

const viewCertificationStatus = () => {
  ElMessage.info('Viewing certification status details')
}

const downloadCertificate = () => {
  ElMessage.info('Downloading certificate...')
}

const viewClauseDetails = (clause: any) => {
  ElMessage.info(`Viewing details for Clause ${clause.number}: ${clause.title}`)
}

const viewEvidence = (control: any) => {
  ElMessage.info(`Viewing evidence: ${control.evidence}`)
}

const uploadEvidence = (control: any) => {
  ElMessage.info(`Upload evidence for control: ${control.ref}`)
}

const newRiskAssessment = () => {
  ElMessage.info('Starting new risk assessment')
}

const treatRisk = (risk: any) => {
  ElMessageBox.confirm(`Initiate treatment for: ${risk.title}?`, 'Risk Treatment', {
    confirmButtonText: 'Proceed',
    cancelButtonText: 'Cancel',
    type: 'warning'
  }).then(() => {
    ElMessage.success(`Risk treatment plan created for ${risk.title}`)
  }).catch(() => {})
}

const viewFullSoA = () => {
  ElMessage.info('Viewing full Statement of Applicability')
}

const viewSoaEvidence = (control: any) => {
  ElMessage.info(`Viewing SoA evidence for ${control.ref}`)
}

const scheduleAudit = () => {
  ElMessage.info('Schedule audit dialog opened')
}

const newManagementReview = () => {
  ElMessage.info('Starting new management review')
}

const updateActionItem = (item: any, completed: boolean) => {
  item.completed = completed
  if (completed) {
    completedActions.value++
    openActionItems.value--
  } else {
    completedActions.value--
    openActionItems.value++
  }
  ElMessage.success(`Action item updated: ${item.description}`)
}

const uploadDocumentation = () => {
  ElMessage.info('Upload documentation dialog opened')
}

const generateSoa = () => {
  ElMessage.info('Generating Statement of Applicability...')
}

const conductRiskAssessment = () => {
  ElMessage.info('Conducting risk assessment')
}

const viewTrainingRecords = () => {
  ElMessage.info('Viewing training records')
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
        initRiskChart()
      }, 100)
    }, 400)
  }, 2500)
})

onUnmounted(() => {
  if (riskChart) riskChart.dispose()
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

/* ==================== Main Content - White Background ==================== */
.iso-container {
  padding: 20px;
  background: #ffffff;
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

/* Certification Banner */
.cert-banner {
  margin-bottom: 24px;
  border-radius: 12px;
  background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
  border-color: #bbf7d0;
}

.cert-content {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 16px;
}

.cert-icon {
  color: #10b981;
}

.cert-info {
  flex: 1;
}

.cert-title {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 8px;
}

.cert-status {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 6px;
}

.cert-dates {
  font-size: 13px;
  color: #64748b;
}

.cert-details {
  font-size: 12px;
  color: #94a3b8;
}

/* Score Section */
.score-section {
  margin-bottom: 24px;
}

.score-card {
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.score-content {
  display: flex;
  align-items: center;
  gap: 48px;
  padding: 20px;
}

.score-gauge {
  flex-shrink: 0;
}

.score-text {
  text-align: center;
}

.score-value {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
  display: block;
}

.score-label {
  font-size: 12px;
  color: #64748b;
}

.score-details {
  display: flex;
  gap: 32px;
  flex-wrap: wrap;
}

.detail-item {
  min-width: 160px;
}

.detail-label {
  font-size: 12px;
  color: #64748b;
  margin-bottom: 4px;
}

.detail-value {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
}

/* Clauses Section */
.clauses-section {
  margin-bottom: 32px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 16px;
}

.clauses-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.clause-card {
  border-radius: 12px;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.clause-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.clause-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.clause-number {
  font-size: 24px;
  font-weight: 700;
  color: #3b82f6;
}

.clause-title {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 12px 0;
}

.clause-progress {
  margin-bottom: 8px;
}

.clause-stats {
  font-size: 11px;
  color: #64748b;
}

/* Controls Section */
.controls-section {
  margin-bottom: 32px;
}

.domain-tabs {
  border-radius: 12px;
}

.domain-tab-label {
  display: flex;
  align-items: center;
  gap: 8px;
}

.domain-content {
  padding: 20px;
}

.domain-description {
  background: #f8fafc;
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 13px;
  color: #475569;
  margin-bottom: 20px;
}

.controls-table {
  overflow-x: auto;
}

/* Risk Section */
.risk-section {
  margin-bottom: 32px;
}

.risk-card {
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  color: #1e293b;
}

.risk-matrix {
  padding: 8px;
}

.risk-summary {
  margin-bottom: 20px;
}

.risk-stats {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.risk-stat {
  text-align: center;
  padding: 12px 20px;
  background: #f8fafc;
  border-radius: 10px;
  flex: 1;
}

.stat-number {
  font-size: 28px;
  font-weight: 700;
}

.stat-number.critical { color: #ef4444; }
.stat-number.high { color: #f59e0b; }
.stat-number.medium { color: #eab308; }
.stat-number.low { color: #10b981; }

.stat-label {
  font-size: 12px;
  color: #64748b;
  margin-top: 4px;
}

.risk-chart {
  height: 250px;
  width: 100%;
}

.risk-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 20px;
}

.risk-item {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 16px;
  background: #f8fafc;
  border-radius: 10px;
}

.risk-level {
  width: 70px;
  padding: 4px 8px;
  border-radius: 6px;
  text-align: center;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
}

.risk-level.critical { background: #ef444420; color: #ef4444; }
.risk-level.high { background: #f59e0b20; color: #f59e0b; }
.risk-level.medium { background: #eab30820; color: #eab308; }
.risk-level.low { background: #10b98120; color: #10b981; }

.risk-info {
  flex: 1;
}

.risk-title {
  font-size: 15px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 4px;
}

.risk-description {
  font-size: 12px;
  color: #64748b;
  margin-bottom: 6px;
}

.risk-meta {
  display: flex;
  gap: 16px;
  font-size: 11px;
  color: #94a3b8;
}

/* SoA Section */
.soa-section {
  margin-bottom: 32px;
}

.soa-card {
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.soa-content {
  padding: 8px;
}

.soa-summary {
  display: flex;
  gap: 30px;
  margin-bottom: 20px;
  padding: 12px;
  background: #f8fafc;
  border-radius: 10px;
  flex-wrap: wrap;
}

.soa-item {
  display: flex;
  gap: 8px;
}

.soa-label {
  font-size: 13px;
  color: #64748b;
}

.soa-value {
  font-size: 13px;
  font-weight: 600;
  color: #1e293b;
}

/* Audit Section */
.audit-section {
  margin-bottom: 32px;
}

.audit-card {
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.audit-timeline {
  max-height: 450px;
  overflow-y: auto;
  padding: 8px;
}

.audit-item-card {
  margin-bottom: 12px;
  border-radius: 8px;
}

.audit-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.audit-title {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
}

.audit-scope {
  font-size: 12px;
  color: #64748b;
  margin-bottom: 6px;
}

.audit-findings {
  font-size: 12px;
  color: #475569;
  margin-bottom: 6px;
  display: flex;
  gap: 20px;
}

.audit-auditor {
  font-size: 11px;
  color: #94a3b8;
}

/* Management Section */
.management-section {
  margin-bottom: 24px;
}

.management-card {
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.management-content {
  padding: 8px;
}

.review-stats {
  display: flex;
  gap: 20px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.review-item {
  flex: 1;
  text-align: center;
  padding: 12px;
  background: #f8fafc;
  border-radius: 10px;
}

.review-label {
  font-size: 12px;
  color: #64748b;
  margin-bottom: 6px;
}

.review-value {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
}

.review-value.critical { color: #ef4444; }
.review-value.success { color: #10b981; }

.action-items h4 {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 12px;
}

.action-item {
  padding: 12px;
  background: #f8fafc;
  border-radius: 8px;
  margin-bottom: 10px;
}

.action-meta {
  display: flex;
  gap: 16px;
  margin-top: 8px;
  margin-left: 24px;
  font-size: 11px;
  color: #94a3b8;
}

.action-priority {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 600;
}

.action-priority.critical { background: #ef444420; color: #ef4444; }
.action-priority.high { background: #f59e0b20; color: #f59e0b; }
.action-priority.medium { background: #eab30820; color: #eab308; }

/* Footer Actions */
.footer-actions {
  margin-top: 8px;
}

.action-group {
  display: flex;
  gap: 16px;
  justify-content: flex-end;
  padding: 16px;
  background: #f8fafc;
  border-radius: 12px;
}

/* Responsive */
@media (max-width: 1200px) {
  .clauses-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .score-content {
    flex-direction: column;
    text-align: center;
  }

  .score-details {
    justify-content: center;
  }
}

@media (max-width: 768px) {
  .clauses-grid {
    grid-template-columns: 1fr;
  }

  .page-header {
    flex-direction: column;
    gap: 16px;
  }

  .cert-content {
    flex-direction: column;
    text-align: center;
  }

  .header-right {
    flex-wrap: wrap;
  }

  .risk-item {
    flex-direction: column;
  }

  .action-group {
    flex-wrap: wrap;
    justify-content: center;
  }

  .soa-summary {
    flex-direction: column;
    gap: 8px;
  }
}
</style>