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
        <div class="loading-tip">ESG / DCIM / AI Semantics</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="semantic-model-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <div class="breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>Data Platform</el-breadcrumb-item>
            <el-breadcrumb-item>Semantic Model</el-breadcrumb-item>
            <el-breadcrumb-item>ESG / DCIM / AI Semantics</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <h1>ESG / DCIM / AI Semantics</h1>
        <p class="description">Unified semantic model for ESG metrics, DCIM operations, and AI analytics</p>
      </div>
      <div class="header-actions">
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>
          Export Model
        </el-button>
        <el-button type="primary" @click="handleAddConcept">
          <el-icon><Plus /></el-icon>
          Add Concept
        </el-button>
      </div>
    </div>

    <!-- Stats Cards -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :lg="6" v-for="stat in statsCards" :key="stat.title">
        <el-card class="stat-card" shadow="hover" @click="handleCardClick(stat)">
          <div class="stat-content">
            <div class="stat-info">
              <div class="stat-title">{{ stat.title }}</div>
              <div class="stat-value">{{ stat.value }}</div>
              <div class="stat-trend" :class="stat.trend > 0 ? 'up' : 'down'">
                <el-icon><component :is="stat.trend > 0 ? 'ArrowUp' : 'ArrowDown'" /></el-icon>
                {{ Math.abs(stat.trend) }}%
                <span class="trend-label">vs last month</span>
              </div>
            </div>
            <div class="stat-icon" :style="{ background: stat.bgColor }">
              <el-icon :size="28" color="white">
                <component :is="stat.icon" />
              </el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Domain Tabs -->
    <el-card class="tabs-card" shadow="hover">
      <el-tabs v-model="activeDomain" @tab-click="handleDomainChange">
        <el-tab-pane label="ESG" name="esg">
          <template #label>
            <span><el-icon><TrendCharts /></el-icon> ESG</span>
          </template>
        </el-tab-pane>
        <el-tab-pane label="DCIM" name="dcim">
          <template #label>
            <span><el-icon><DataAnalysis /></el-icon> DCIM</span>
          </template>
        </el-tab-pane>
        <el-tab-pane label="AI" name="ai">
          <template #label>
            <span><el-icon><Cpu /></el-icon> AI</span>
          </template>
        </el-tab-pane>
        <el-tab-pane label="Cross-Domain" name="cross">
          <template #label>
            <span><el-icon><Connection /></el-icon> Cross-Domain</span>
          </template>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- Domain Content -->
    <div v-show="activeDomain === 'esg'">
      <el-row :gutter="20" class="domain-row">
        <el-col :xs="24" :lg="16">
          <el-card class="concept-graph-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span>ESG Concept Hierarchy</span>
              </div>
            </template>
            <div ref="esgGraphRef" class="graph-container"></div>
          </el-card>
        </el-col>
        <el-col :xs="24" :lg="8">
          <el-card class="metrics-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span>Key ESG Metrics</span>
              </div>
            </template>
            <div class="metrics-list">
              <div v-for="metric in esgMetrics" :key="metric.name" class="metric-item" @click="viewConcept(metric)">
                <div class="metric-header">
                  <span class="metric-name">{{ metric.name }}</span>
                  <el-tag :type="getMetricTrendTag(metric.trend)" size="small">{{ metric.trend }}%</el-tag>
                </div>
                <div class="metric-value">{{ metric.value }}</div>
                <div class="metric-desc">{{ metric.description }}</div>
                <div class="metric-tags">
                  <el-tag v-for="tag in metric.tags" :key="tag" size="small" type="info">{{ tag }}</el-tag>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <div v-show="activeDomain === 'dcim'">
      <el-row :gutter="20" class="domain-row">
        <el-col :xs="24" :lg="16">
          <el-card class="concept-graph-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span>DCIM Concept Hierarchy</span>
              </div>
            </template>
            <div ref="dcimGraphRef" class="graph-container"></div>
          </el-card>
        </el-col>
        <el-col :xs="24" :lg="8">
          <el-card class="metrics-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span>Key DCIM Metrics</span>
              </div>
            </template>
            <div class="metrics-list">
              <div v-for="metric in dcimMetrics" :key="metric.name" class="metric-item" @click="viewConcept(metric)">
                <div class="metric-header">
                  <span class="metric-name">{{ metric.name }}</span>
                  <el-tag :type="getMetricTrendTag(metric.trend)" size="small">{{ metric.trend }}%</el-tag>
                </div>
                <div class="metric-value">{{ metric.value }}</div>
                <div class="metric-desc">{{ metric.description }}</div>
                <div class="metric-tags">
                  <el-tag v-for="tag in metric.tags" :key="tag" size="small" type="info">{{ tag }}</el-tag>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <div v-show="activeDomain === 'ai'">
      <el-row :gutter="20" class="domain-row">
        <el-col :xs="24" :lg="16">
          <el-card class="concept-graph-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span>AI Concept Hierarchy</span>
              </div>
            </template>
            <div ref="aiGraphRef" class="graph-container"></div>
          </el-card>
        </el-col>
        <el-col :xs="24" :lg="8">
          <el-card class="metrics-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span>AI Model Performance</span>
              </div>
            </template>
            <div class="metrics-list">
              <div v-for="metric in aiMetrics" :key="metric.name" class="metric-item" @click="viewConcept(metric)">
                <div class="metric-header">
                  <span class="metric-name">{{ metric.name }}</span>
                  <el-tag :type="getMetricTrendTag(metric.trend)" size="small">{{ metric.trend }}%</el-tag>
                </div>
                <div class="metric-value">{{ metric.value }}</div>
                <div class="metric-desc">{{ metric.description }}</div>
                <div class="metric-tags">
                  <el-tag v-for="tag in metric.tags" :key="tag" size="small" type="info">{{ tag }}</el-tag>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <div v-show="activeDomain === 'cross'">
      <el-card class="cross-domain-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>Cross-Domain Relationships</span>
          </div>
        </template>
        <div ref="crossGraphRef" class="cross-graph-container"></div>
        <div class="cross-legend">
          <div class="legend-item">
            <span class="legend-color esg"></span>
            <span>ESG Concepts</span>
          </div>
          <div class="legend-item">
            <span class="legend-color dcim"></span>
            <span>DCIM Concepts</span>
          </div>
          <div class="legend-item">
            <span class="legend-color ai"></span>
            <span>AI Concepts</span>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Filters -->
    <el-card class="filter-card" shadow="hover">
      <div class="filter-container">
        <div class="filter-row">
          <el-input
              v-model="filters.keyword"
              placeholder="Search concepts"
              prefix-icon="Search"
              clearable
              style="width: 240px"
              @clear="handleSearch"
              @keyup.enter="handleSearch"
          />
          <el-select v-model="filters.domain" placeholder="Domain" clearable style="width: 120px">
            <el-option label="ESG" value="esg" />
            <el-option label="DCIM" value="dcim" />
            <el-option label="AI" value="ai" />
          </el-select>
          <el-select v-model="filters.category" placeholder="Category" clearable style="width: 140px">
            <el-option label="Metrics" value="metrics" />
            <el-option label="Models" value="models" />
            <el-option label="Policies" value="policies" />
            <el-option label="Standards" value="standards" />
          </el-select>
          <el-button type="primary" @click="handleSearch">Search</el-button>
          <el-button @click="handleResetFilters">Reset</el-button>
        </div>
      </div>
    </el-card>

    <!-- Concepts Table -->
    <el-card class="table-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Semantic Concepts ({{ filteredConcepts.length }} items)</span>
          <div class="table-actions">
            <el-button :icon="Refresh" @click="fetchConcepts" circle />
            <el-button :icon="Setting" @click="handleColumnSettings" circle />
          </div>
        </div>
      </template>

      <el-table :data="paginatedConcepts" stripe style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="name" label="Concept Name" min-width="180" show-overflow-tooltip />
        <el-table-column prop="domain" label="Domain" width="100">
          <template #default="{ row }">
            <el-tag :type="getDomainTag(row.domain)" size="small">{{ row.domain.toUpperCase() }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="category" label="Category" width="120">
          <template #default="{ row }">
            <el-tag type="info" size="small">{{ row.category }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="definition" label="Definition" min-width="250" show-overflow-tooltip />
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'Published' ? 'success' : 'warning'" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="version" label="Version" width="80" />
        <el-table-column label="Actions" width="180" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewConcept(row)">View</el-button>
            <el-button link type="success" size="small" @click="editConcept(row)">Edit</el-button>
            <el-button link type="danger" size="small" @click="deleteConcept(row)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[15, 30, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="filteredConcepts.length"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- Concept Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" :title="`Concept: ${currentConcept?.name}`" width="700px" destroy-on-close>
      <div class="concept-details" v-if="currentConcept">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Name">{{ currentConcept.name }}</el-descriptions-item>
          <el-descriptions-item label="Domain">
            <el-tag :type="getDomainTag(currentConcept.domain)" size="small">{{ currentConcept.domain.toUpperCase() }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Category">{{ currentConcept.category }}</el-descriptions-item>
          <el-descriptions-item label="Status">
            <el-tag :type="currentConcept.status === 'Published' ? 'success' : 'warning'" size="small">{{ currentConcept.status }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Version">{{ currentConcept.version }}</el-descriptions-item>
          <el-descriptions-item label="Last Updated">{{ currentConcept.updatedAt }}</el-descriptions-item>
          <el-descriptions-item label="Definition" :span="2">{{ currentConcept.definition }}</el-descriptions-item>
          <el-descriptions-item label="Business Context" :span="2">{{ currentConcept.businessContext || 'N/A' }}</el-descriptions-item>
        </el-descriptions>

        <!-- Related Concepts -->
        <div class="related-section" v-if="currentConcept.relatedConcepts?.length">
          <h4>Related Concepts</h4>
          <div class="related-tags">
            <el-tag
                v-for="rel in currentConcept.relatedConcepts"
                :key="rel"
                size="default"
                style="margin-right: 8px; margin-bottom: 8px; cursor: pointer"
                @click="navigateToConcept(rel)"
            >
              {{ rel }}
            </el-tag>
          </div>
        </div>

        <!-- Examples -->
        <div class="examples-section" v-if="currentConcept.examples">
          <h4>Examples</h4>
          <ul>
            <li v-for="ex in currentConcept.examples" :key="ex">{{ ex }}</li>
          </ul>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="editConcept(currentConcept)">Edit</el-button>
      </template>
    </el-dialog>

    <!-- Add/Edit Concept Dialog -->
    <el-dialog v-model="dialogVisible" :title="dialogMode === 'add' ? 'Add Concept' : 'Edit Concept'" width="600px" destroy-on-close>
      <el-form :model="formData" :rules="formRules" ref="formRef" label-width="120px">
        <el-form-item label="Concept Name" prop="name">
          <el-input v-model="formData.name" placeholder="Enter concept name" />
        </el-form-item>
        <el-form-item label="Domain" prop="domain">
          <el-select v-model="formData.domain" placeholder="Select domain" style="width: 100%">
            <el-option label="ESG" value="esg" />
            <el-option label="DCIM" value="dcim" />
            <el-option label="AI" value="ai" />
          </el-select>
        </el-form-item>
        <el-form-item label="Category" prop="category">
          <el-select v-model="formData.category" placeholder="Select category" style="width: 100%">
            <el-option label="Metrics" value="metrics" />
            <el-option label="Models" value="models" />
            <el-option label="Policies" value="policies" />
            <el-option label="Standards" value="standards" />
            <el-option label="Best Practices" value="best_practices" />
          </el-select>
        </el-form-item>
        <el-form-item label="Definition" prop="definition">
          <el-input v-model="formData.definition" type="textarea" :rows="3" placeholder="Enter definition" />
        </el-form-item>
        <el-form-item label="Business Context" prop="businessContext">
          <el-input v-model="formData.businessContext" type="textarea" :rows="2" placeholder="Enter business context" />
        </el-form-item>
        <el-form-item label="Related Concepts" prop="relatedConcepts">
          <el-select
              v-model="formData.relatedConcepts"
              multiple
              filterable
              allow-create
              default-first-option
              placeholder="Enter related concepts"
              style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="Examples" prop="examples">
          <el-select
              v-model="formData.examples"
              multiple
              filterable
              allow-create
              default-first-option
              placeholder="Enter examples"
              style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="Status" prop="status">
          <el-radio-group v-model="formData.status">
            <el-radio value="Draft">Draft</el-radio>
            <el-radio value="Published">Published</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="submitForm">Save Concept</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  Plus, ArrowUp, ArrowDown, Document, Checked,
  Clock, TrendCharts, Refresh, Search, Download, Setting,
  DataAnalysis, Cpu, Connection
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading semantic model...',
  'Building concept graphs...',
  'Almost ready...'
]

// ==================== Chart References ====================
const esgGraphRef = ref<HTMLElement>()
const dcimGraphRef = ref<HTMLElement>()
const aiGraphRef = ref<HTMLElement>()
const crossGraphRef = ref<HTMLElement>()
let esgGraph: echarts.ECharts | null = null
let dcimGraph: echarts.ECharts | null = null
let aiGraph: echarts.ECharts | null = null
let crossGraph: echarts.ECharts | null = null

// ==================== State ====================
const tableLoading = ref(false)
const dialogVisible = ref(false)
const detailDialogVisible = ref(false)
const dialogMode = ref<'add' | 'edit'>('add')
const currentConcept = ref<any>(null)
const activeDomain = ref('esg')
const formRef = ref()
const currentPage = ref(1)
const pageSize = ref(15)

const filters = reactive({
  keyword: '',
  domain: '',
  category: ''
})

const formData = reactive({
  id: null,
  name: '',
  domain: 'esg',
  category: 'metrics',
  definition: '',
  businessContext: '',
  relatedConcepts: [] as string[],
  examples: [] as string[],
  status: 'Draft',
  version: '1.0'
})

const formRules = {
  name: [{ required: true, message: 'Please enter concept name', trigger: 'blur' }],
  domain: [{ required: true, message: 'Please select domain', trigger: 'change' }],
  category: [{ required: true, message: 'Please select category', trigger: 'change' }],
  definition: [{ required: true, message: 'Please enter definition', trigger: 'blur' }]
}

// ==================== Mock Data ====================
const statsCards = ref([
  { title: 'Total Concepts', value: 86, trend: 12, icon: 'Document', bgColor: '#409eff', key: 'total' },
  { title: 'ESG Metrics', value: 32, trend: 8, icon: 'TrendCharts', bgColor: '#67c23a', key: 'esg' },
  { title: 'DCIM Metrics', value: 28, trend: 5, icon: 'DataAnalysis', bgColor: '#e6a23c', key: 'dcim' },
  { title: 'AI Models', value: 26, trend: 15, icon: 'Cpu', bgColor: '#f56c6c', key: 'ai' }
])

const esgMetrics = ref([
  { name: 'Carbon Footprint', value: '1,250 tCO₂e', trend: -8, description: 'Total greenhouse gas emissions', tags: ['Scope 1', 'Scope 2'], category: 'metrics' },
  { name: 'Energy Intensity', value: '0.85 kWh/m²', trend: -5, description: 'Energy consumption per square meter', tags: ['Efficiency'], category: 'metrics' },
  { name: 'Water Usage', value: '2.5M gallons', trend: -12, description: 'Total water consumption', tags: ['Water'], category: 'metrics' },
  { name: 'Waste Diversion Rate', value: '78%', trend: 6, description: 'Percentage of waste recycled', tags: ['Waste'], category: 'metrics' },
  { name: 'ESG Score', value: '86.5', trend: 4, description: 'Overall ESG performance score', tags: ['Composite'], category: 'metrics' }
])

const dcimMetrics = ref([
  { name: 'PUE', value: '1.45', trend: -3, description: 'Power Usage Effectiveness', tags: ['Efficiency'], category: 'metrics' },
  { name: 'DCiE', value: '68.9%', trend: 2, description: 'Data Center Infrastructure Efficiency', tags: ['Efficiency'], category: 'metrics' },
  { name: 'Rack Density', value: '8.5 kW/rack', trend: 12, description: 'Average power per rack', tags: ['Capacity'], category: 'metrics' },
  { name: 'Cooling Efficiency', value: '0.32 kW/ton', trend: -5, description: 'Cooling system efficiency', tags: ['HVAC'], category: 'metrics' },
  { name: 'IT Load', value: '1,850 kW', trend: 8, description: 'Total IT equipment load', tags: ['IT'], category: 'metrics' }
])

const aiMetrics = ref([
  { name: 'Prediction Accuracy', value: '94.2%', trend: 2, description: 'Overall model prediction accuracy', tags: ['Accuracy'], category: 'metrics' },
  { name: 'F1 Score', value: '0.91', trend: 3, description: 'Harmonic mean of precision and recall', tags: ['Performance'], category: 'metrics' },
  { name: 'Inference Latency', value: '45ms', trend: -8, description: 'Average prediction time', tags: ['Performance'], category: 'metrics' },
  { name: 'Model Uptime', value: '99.95%', trend: 0.5, description: 'Model availability', tags: ['Reliability'], category: 'metrics' },
  { name: 'Training Throughput', value: '1,250 samples/s', trend: 15, description: 'Model training speed', tags: ['Training'], category: 'metrics' }
])

const concepts = ref([
  { id: 1, name: 'Carbon Footprint', domain: 'esg', category: 'metrics', definition: 'Total greenhouse gas emissions caused directly and indirectly by an organization.', status: 'Published', version: '2.0', updatedAt: '2024-01-15', businessContext: 'ESG reporting and carbon reduction targets', relatedConcepts: ['Scope 1 Emissions', 'Scope 2 Emissions', 'Carbon Offset'], examples: ['Company carbon footprint reduced by 15% in 2023', 'Product carbon footprint labeling'] },
  { id: 2, name: 'PUE', domain: 'dcim', category: 'metrics', definition: 'Power Usage Effectiveness - ratio of total facility energy to IT equipment energy.', status: 'Published', version: '1.5', updatedAt: '2024-01-10', businessContext: 'Data center energy efficiency measurement', relatedConcepts: ['DCiE', 'Cooling Efficiency', 'IT Load'], examples: ['Data center achieved PUE of 1.35', 'Industry average PUE is 1.6'] },
  { id: 3, name: 'Predictive Maintenance', domain: 'ai', category: 'models', definition: 'AI-driven prediction of equipment failures before they occur.', status: 'Published', version: '2.1', updatedAt: '2024-01-12', businessContext: 'Reduce downtime and maintenance costs', relatedConcepts: ['Anomaly Detection', 'LSTM Networks', 'Equipment Health'], examples: ['Chiller failure predicted 7 days in advance', 'Vibration analysis for pump maintenance'] },
  { id: 4, name: 'Scope 1 Emissions', domain: 'esg', category: 'metrics', definition: 'Direct greenhouse gas emissions from owned or controlled sources.', status: 'Published', version: '1.2', updatedAt: '2024-01-08', businessContext: 'ESG reporting and compliance', relatedConcepts: ['Carbon Footprint', 'Fugitive Emissions'], examples: ['Natural gas combustion', 'Company vehicles'] },
  { id: 5, name: 'DCiE', domain: 'dcim', category: 'metrics', definition: 'Data Center Infrastructure Efficiency - inverse of PUE.', status: 'Published', version: '1.0', updatedAt: '2024-01-05', businessContext: 'Data center efficiency metric', relatedConcepts: ['PUE', 'IT Efficiency'], examples: ['DCiE of 69% equals PUE of 1.45'] },
  { id: 6, name: 'Anomaly Detection', domain: 'ai', category: 'models', definition: 'Identification of unusual patterns that do not conform to expected behavior.', status: 'Published', version: '2.0', updatedAt: '2024-01-14', businessContext: 'Fault detection and security monitoring', relatedConcepts: ['Predictive Maintenance', 'Isolation Forest', 'Statistical Process Control'], examples: ['Temperature spike detection', 'Unusual energy consumption pattern'] }
])

// ==================== Computed ====================
const filteredConcepts = computed(() => {
  let filtered = [...concepts.value]

  if (filters.keyword) {
    filtered = filtered.filter(c =>
        c.name.toLowerCase().includes(filters.keyword.toLowerCase()) ||
        c.definition.toLowerCase().includes(filters.keyword.toLowerCase())
    )
  }

  if (filters.domain) {
    filtered = filtered.filter(c => c.domain === filters.domain)
  }

  if (filters.category) {
    filtered = filtered.filter(c => c.category === filters.category)
  }

  return filtered
})

const paginatedConcepts = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredConcepts.value.slice(start, end)
})

// ==================== Helper Methods ====================
const getDomainTag = (domain: string) => {
  const map: Record<string, string> = {
    'esg': 'success',
    'dcim': 'primary',
    'ai': 'warning'
  }
  return map[domain] || 'info'
}

const getMetricTrendTag = (trend: number) => {
  if (trend > 0) return 'success'
  if (trend < 0) return 'danger'
  return 'info'
}

// ==================== Chart Initializations ====================
const initEsgGraph = () => {
  if (!esgGraphRef.value) return
  if (esgGraph) esgGraph.dispose()

  esgGraph = echarts.init(esgGraphRef.value)

  const nodes = [
    { name: 'ESG', category: 'root', symbolSize: 40 },
    { name: 'Environmental', category: 'pillar', symbolSize: 30 },
    { name: 'Social', category: 'pillar', symbolSize: 30 },
    { name: 'Governance', category: 'pillar', symbolSize: 30 },
    { name: 'Carbon Footprint', category: 'metric', symbolSize: 25 },
    { name: 'Energy Efficiency', category: 'metric', symbolSize: 25 },
    { name: 'Water Usage', category: 'metric', symbolSize: 25 },
    { name: 'Diversity & Inclusion', category: 'metric', symbolSize: 25 },
    { name: 'Board Diversity', category: 'metric', symbolSize: 25 },
    { name: 'Ethics Compliance', category: 'metric', symbolSize: 25 }
  ]

  const links = [
    { source: 'ESG', target: 'Environmental' },
    { source: 'ESG', target: 'Social' },
    { source: 'ESG', target: 'Governance' },
    { source: 'Environmental', target: 'Carbon Footprint' },
    { source: 'Environmental', target: 'Energy Efficiency' },
    { source: 'Environmental', target: 'Water Usage' },
    { source: 'Social', target: 'Diversity & Inclusion' },
    { source: 'Governance', target: 'Board Diversity' },
    { source: 'Governance', target: 'Ethics Compliance' }
  ]

  const categories = [
    { name: 'Root', itemStyle: { color: '#409eff' } },
    { name: 'Pillar', itemStyle: { color: '#67c23a' } },
    { name: 'Metric', itemStyle: { color: '#e6a23c' } }
  ]

  const option: echarts.EChartsOption = {
    tooltip: { trigger: 'item' },
    series: [{
      type: 'graph',
      layout: 'force',
      force: { repulsion: 500, edgeLength: 150, gravity: 0.1 },
      data: nodes,
      links: links,
      categories: categories,
      roam: true,
      label: { show: true, position: 'bottom', fontSize: 11 },
      edgeSymbol: ['none', 'arrow'],
      lineStyle: { color: '#c0c4cc', width: 2 }
    }]
  }

  esgGraph.setOption(option)
  window.addEventListener('resize', () => esgGraph?.resize())
}

const initDcimGraph = () => {
  if (!dcimGraphRef.value) return
  if (dcimGraph) dcimGraph.dispose()

  dcimGraph = echarts.init(dcimGraphRef.value)

  const nodes = [
    { name: 'DCIM', category: 'root', symbolSize: 40 },
    { name: 'Power', category: 'category', symbolSize: 30 },
    { name: 'Cooling', category: 'category', symbolSize: 30 },
    { name: 'Space', category: 'category', symbolSize: 30 },
    { name: 'PUE', category: 'metric', symbolSize: 25 },
    { name: 'DCiE', category: 'metric', symbolSize: 25 },
    { name: 'Cooling Efficiency', category: 'metric', symbolSize: 25 },
    { name: 'Rack Density', category: 'metric', symbolSize: 25 },
    { name: 'IT Load', category: 'metric', symbolSize: 25 }
  ]

  const links = [
    { source: 'DCIM', target: 'Power' },
    { source: 'DCIM', target: 'Cooling' },
    { source: 'DCIM', target: 'Space' },
    { source: 'Power', target: 'PUE' },
    { source: 'Power', target: 'DCiE' },
    { source: 'Power', target: 'IT Load' },
    { source: 'Cooling', target: 'Cooling Efficiency' },
    { source: 'Space', target: 'Rack Density' }
  ]

  const option: echarts.EChartsOption = {
    tooltip: { trigger: 'item' },
    series: [{
      type: 'graph',
      layout: 'force',
      force: { repulsion: 500, edgeLength: 150, gravity: 0.1 },
      data: nodes,
      links: links,
      roam: true,
      label: { show: true, position: 'bottom', fontSize: 11 },
      lineStyle: { color: '#c0c4cc', width: 2 }
    }]
  }

  dcimGraph.setOption(option)
  window.addEventListener('resize', () => dcimGraph?.resize())
}

const initAiGraph = () => {
  if (!aiGraphRef.value) return
  if (aiGraph) aiGraph.dispose()

  aiGraph = echarts.init(aiGraphRef.value)

  const nodes = [
    { name: 'AI/ML', category: 'root', symbolSize: 40 },
    { name: 'Predictive Maintenance', category: 'app', symbolSize: 30 },
    { name: 'Anomaly Detection', category: 'app', symbolSize: 30 },
    { name: 'Energy Optimization', category: 'app', symbolSize: 30 },
    { name: 'LSTM', category: 'model', symbolSize: 25 },
    { name: 'Random Forest', category: 'model', symbolSize: 25 },
    { name: 'XGBoost', category: 'model', symbolSize: 25 },
    { name: 'Reinforcement Learning', category: 'model', symbolSize: 25 }
  ]

  const links = [
    { source: 'AI/ML', target: 'Predictive Maintenance' },
    { source: 'AI/ML', target: 'Anomaly Detection' },
    { source: 'AI/ML', target: 'Energy Optimization' },
    { source: 'Predictive Maintenance', target: 'LSTM' },
    { source: 'Anomaly Detection', target: 'Isolation Forest' },
    { source: 'Energy Optimization', target: 'Reinforcement Learning' }
  ]

  const option: echarts.EChartsOption = {
    tooltip: { trigger: 'item' },
    series: [{
      type: 'graph',
      layout: 'force',
      force: { repulsion: 500, edgeLength: 150, gravity: 0.1 },
      data: nodes,
      links: links,
      roam: true,
      label: { show: true, position: 'bottom', fontSize: 11 },
      lineStyle: { color: '#c0c4cc', width: 2 }
    }]
  }

  aiGraph.setOption(option)
  window.addEventListener('resize', () => aiGraph?.resize())
}

const initCrossGraph = () => {
  if (!crossGraphRef.value) return
  if (crossGraph) crossGraph.dispose()

  crossGraph = echarts.init(crossGraphRef.value)

  const nodes = [
    { name: 'Carbon Footprint', category: 'esg', symbolSize: 30, itemStyle: { color: '#67c23a' } },
    { name: 'PUE', category: 'dcim', symbolSize: 30, itemStyle: { color: '#409eff' } },
    { name: 'Predictive Maintenance', category: 'ai', symbolSize: 30, itemStyle: { color: '#e6a23c' } },
    { name: 'Energy Efficiency', category: 'esg', symbolSize: 25, itemStyle: { color: '#67c23a' } },
    { name: 'Cooling Efficiency', category: 'dcim', symbolSize: 25, itemStyle: { color: '#409eff' } },
    { name: 'Anomaly Detection', category: 'ai', symbolSize: 25, itemStyle: { color: '#e6a23c' } }
  ]

  const links = [
    { source: 'Energy Efficiency', target: 'PUE' },
    { source: 'Carbon Footprint', target: 'Energy Efficiency' },
    { source: 'PUE', target: 'Cooling Efficiency' },
    { source: 'Predictive Maintenance', target: 'Anomaly Detection' },
    { source: 'Energy Efficiency', target: 'Predictive Maintenance' }
  ]

  const option: echarts.EChartsOption = {
    tooltip: { trigger: 'item' },
    series: [{
      type: 'graph',
      layout: 'force',
      force: { repulsion: 500, edgeLength: 180, gravity: 0.1 },
      data: nodes,
      links: links,
      roam: true,
      label: { show: true, position: 'bottom', fontSize: 11 },
      lineStyle: { color: '#c0c4cc', width: 2 },
      edgeSymbol: ['none', 'arrow']
    }]
  }

  crossGraph.setOption(option)
  window.addEventListener('resize', () => crossGraph?.resize())
}

// ==================== Interactive Methods ====================
const handleCardClick = (stat: any) => {
  ElMessage.info(`Viewing ${stat.title} details`)
}

const handleDomainChange = () => {
  // Refresh graph when domain changes
  if (activeDomain.value === 'esg') {
    initEsgGraph()
  } else if (activeDomain.value === 'dcim') {
    initDcimGraph()
  } else if (activeDomain.value === 'ai') {
    initAiGraph()
  } else if (activeDomain.value === 'cross') {
    initCrossGraph()
  }
}

const handleSearch = () => {
  currentPage.value = 1
}

const handleResetFilters = () => {
  filters.keyword = ''
  filters.domain = ''
  filters.category = ''
  currentPage.value = 1
  ElMessage.success('Filters reset')
}

const handleExport = () => {
  ElMessage.success(`Exporting ${filteredConcepts.value.length} concepts...`)
}

const handleColumnSettings = () => {
  ElMessage.info('Column settings dialog would open here')
}

const handleAddConcept = () => {
  dialogMode.value = 'add'
  Object.assign(formData, {
    id: null,
    name: '',
    domain: 'esg',
    category: 'metrics',
    definition: '',
    businessContext: '',
    relatedConcepts: [],
    examples: [],
    status: 'Draft',
    version: '1.0'
  })
  dialogVisible.value = true
}

const fetchConcepts = () => {
  tableLoading.value = true
  setTimeout(() => {
    tableLoading.value = false
    ElMessage.success('Data refreshed')
  }, 500)
}

const viewConcept = (concept: any) => {
  currentConcept.value = concept
  detailDialogVisible.value = true
}

const editConcept = (concept: any) => {
  dialogMode.value = 'edit'
  Object.assign(formData, concept)
  dialogVisible.value = true
}

const deleteConcept = (concept: any) => {
  ElMessageBox.confirm(`Delete concept "${concept.name}"?`, 'Confirm Delete', {
    confirmButtonText: 'Delete',
    cancelButtonText: 'Cancel',
    type: 'warning'
  }).then(() => {
    const index = concepts.value.findIndex(c => c.id === concept.id)
    if (index !== -1) {
      concepts.value.splice(index, 1)
      ElMessage.success(`Deleted: ${concept.name}`)
    }
  }).catch(() => {})
}

const navigateToConcept = (conceptName: string) => {
  const concept = concepts.value.find(c => c.name === conceptName)
  if (concept) {
    viewConcept(concept)
  }
}

const submitForm = async () => {
  if (!formRef.value) return
  await formRef.value.validate((valid: boolean) => {
    if (valid) {
      if (dialogMode.value === 'add') {
        const newConcept = {
          id: Date.now(),
          ...formData,
          status: formData.status,
          version: '1.0',
          updatedAt: new Date().toISOString().split('T')[0]
        }
        concepts.value.unshift(newConcept)
        ElMessage.success('Concept added successfully')
      } else {
        const index = concepts.value.findIndex(c => c.id === formData.id)
        if (index !== -1) {
          concepts.value[index] = { ...concepts.value[index], ...formData, updatedAt: new Date().toISOString().split('T')[0] }
          ElMessage.success('Concept updated successfully')
        }
      }
      dialogVisible.value = false
      formRef.value?.resetFields()
    }
  })
}

const handleSizeChange = () => {
  currentPage.value = 1
}

const handleCurrentChange = () => {}

// ==================== Loading Simulation ====================
const initCharts = async () => {
  await nextTick()
  setTimeout(() => {
    initEsgGraph()
    initDcimGraph()
    initAiGraph()
    initCrossGraph()
  }, 100)
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
      initCharts()
      fetchConcepts()
    }, 400)
  }, 2000)
})
</script>

<style scoped lang="scss">
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

/* ==================== Main Page Styles ==================== */
.semantic-model-page {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;

  .breadcrumb {
    margin-bottom: 8px;
  }

  h1 {
    font-size: 28px;
    font-weight: 600;
    color: #303133;
    margin: 0 0 8px 0;
  }

  .description {
    color: #909399;
    font-size: 14px;
    margin: 0;
  }

  .header-actions {
    display: flex;
    gap: 12px;
  }
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  cursor: pointer;
  transition: all 0.3s;

  &:hover {
    transform: translateY(-4px);
  }

  .stat-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .stat-info {
    flex: 1;
  }

  .stat-title {
    font-size: 14px;
    color: #909399;
    margin-bottom: 8px;
  }

  .stat-value {
    font-size: 28px;
    font-weight: 600;
    color: #303133;
    margin-bottom: 8px;
  }

  .stat-trend {
    font-size: 12px;
    display: flex;
    align-items: center;
    gap: 4px;

    &.up { color: #67c23a; }
    &.down { color: #f56c6c; }

    .trend-label {
      color: #909399;
      margin-left: 4px;
    }
  }

  .stat-icon {
    width: 56px;
    height: 56px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

.tabs-card {
  margin-bottom: 20px;
}

.domain-row {
  margin-bottom: 20px;
}

.concept-graph-card, .metrics-card {
  .card-header {
    font-weight: 600;
  }
}

.graph-container {
  width: 100%;
  height: 450px;
  background: #fff;
  border-radius: 8px;
}

.cross-graph-container {
  width: 100%;
  height: 450px;
  background: #fff;
  border-radius: 8px;
}

.cross-legend {
  display: flex;
  justify-content: center;
  gap: 24px;
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid #ebeef5;

  .legend-item {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 13px;

    .legend-color {
      width: 16px;
      height: 16px;
      border-radius: 4px;

      &.esg { background-color: #67c23a; }
      &.dcim { background-color: #409eff; }
      &.ai { background-color: #e6a23c; }
    }
  }
}

.metrics-list {
  max-height: 450px;
  overflow-y: auto;

  .metric-item {
    padding: 12px;
    border-bottom: 1px solid #ebeef5;
    cursor: pointer;
    transition: background 0.2s;

    &:hover {
      background: #f5f7fa;
    }

    .metric-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;

      .metric-name {
        font-weight: 600;
        color: #303133;
      }
    }

    .metric-value {
      font-size: 18px;
      font-weight: 600;
      color: #409eff;
      margin-bottom: 4px;
    }

    .metric-desc {
      font-size: 12px;
      color: #909399;
      margin-bottom: 8px;
    }

    .metric-tags {
      display: flex;
      flex-wrap: wrap;
      gap: 4px;
    }
  }
}

.filter-card {
  margin-bottom: 20px;

  .filter-container {
    .filter-row {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      align-items: center;
    }
  }
}

.table-card {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;
  }

  .table-actions {
    display: flex;
    gap: 8px;
    align-items: center;
  }
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.concept-details {
  .related-section, .examples-section {
    margin-top: 20px;

    h4 {
      margin-bottom: 12px;
      color: #303133;
    }
  }

  .related-tags {
    display: flex;
    flex-wrap: wrap;
  }

  ul {
    margin: 0;
    padding-left: 20px;

    li {
      color: #606266;
      line-height: 1.8;
    }
  }
}

:deep(.el-table) {
  font-size: 13px;
}

:deep(.el-dialog__body) {
  max-height: 60vh;
  overflow-y: auto;
}
</style>