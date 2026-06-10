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
        <div class="loading-tip">GraphQL API Management</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="graphql-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <div class="breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>Data Platform</el-breadcrumb-item>
            <el-breadcrumb-item>Data Services</el-breadcrumb-item>
            <el-breadcrumb-item>GraphQL API</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <h1>GraphQL API</h1>
        <p class="description">Manage GraphQL schema, queries, mutations, and subscriptions for flexible data access</p>
      </div>
      <div class="header-actions">
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>
          Export Schema
        </el-button>
        <el-button type="primary" @click="openPlayground">
          <el-icon><Monitor /></el-icon>
          GraphQL Playground
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
                <span class="trend-label">vs last week</span>
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

    <!-- Schema & Explorer Layout -->
    <el-row :gutter="20" class="main-row">
      <!-- Left: Schema Explorer -->
      <el-col :xs="24" :lg="8">
        <el-card class="schema-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Schema Explorer</span>
              <el-input
                  v-model="schemaFilter"
                  placeholder="Filter types"
                  prefix-icon="Search"
                  size="small"
                  clearable
                  style="width: 160px"
              />
            </div>
          </template>
          <div class="schema-tree">
            <el-tree
                :data="filteredSchemaTree"
                :props="treeProps"
                node-key="name"
                default-expand-all
                highlight-current
                @node-click="handleSchemaNodeClick"
            >
              <template #default="{ node, data }">
                <span class="schema-node">
                  <el-icon :color="getNodeColor(data.kind)">
                    <component :is="getNodeIcon(data.kind)" />
                  </el-icon>
                  <span>{{ node.label }}</span>
                  <el-tag v-if="data.deprecated" type="danger" size="small" class="node-tag">deprecated</el-tag>
                </span>
              </template>
            </el-tree>
          </div>
        </el-card>
      </el-col>

      <!-- Right: Type Details -->
      <el-col :xs="24" :lg="16">
        <el-card class="type-detail-card" shadow="hover" v-if="selectedType">
          <template #header>
            <div class="card-header">
              <div class="type-title">
                <el-icon :color="getNodeColor(selectedType.kind)">
                  <component :is="getNodeIcon(selectedType.kind)" />
                </el-icon>
                <span>{{ selectedType.name }}</span>
                <el-tag v-if="selectedType.kind" :type="getKindTag(selectedType.kind)" size="small">{{ selectedType.kind }}</el-tag>
                <el-tag v-if="selectedType.deprecated" type="danger" size="small">deprecated</el-tag>
              </div>
              <div class="type-actions">
                <el-button link type="primary" size="small" @click="copyTypeName">Copy Name</el-button>
              </div>
            </div>
          </template>

          <!-- Description -->
          <div class="type-description" v-if="selectedType.description">
            <el-alert :title="selectedType.description" type="info" :closable="false" show-icon />
          </div>

          <!-- Fields -->
          <div class="type-fields" v-if="selectedType.fields?.length">
            <h4>Fields</h4>
            <el-table :data="selectedType.fields" size="small" border>
              <el-table-column prop="name" label="Name" width="180">
                <template #default="{ row }">
                  <span class="field-name">{{ row.name }}</span>
                  <el-tag v-if="row.deprecated" type="danger" size="small" class="field-tag">deprecated</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="type" label="Type" width="180">
                <template #default="{ row }">
                  <code class="type-code">{{ row.type }}</code>
                </template>
              </el-table-column>
              <el-table-column prop="description" label="Description" min-width="200" show-overflow-tooltip />
              <el-table-column label="Args" width="100" align="center">
                <template #default="{ row }">
                  <el-tag v-if="row.args?.length" type="info" size="small">{{ row.args.length }} args</el-tag>
                  <span v-else>—</span>
                </template>
              </el-table-column>
            </el-table>
          </div>

          <!-- Arguments (for Queries/Mutations) -->
          <div class="type-args" v-if="selectedType.args?.length">
            <h4>Arguments</h4>
            <el-table :data="selectedType.args" size="small" border>
              <el-table-column prop="name" label="Name" width="180" />
              <el-table-column prop="type" label="Type" width="180">
                <template #default="{ row }">
                  <code class="type-code">{{ row.type }}</code>
                </template>
              </el-table-column>
              <el-table-column prop="description" label="Description" min-width="250" />
              <el-table-column label="Default" width="100">
                <template #default="{ row }">
                  <code v-if="row.defaultValue">{{ row.defaultValue }}</code>
                  <span v-else>—</span>
                </template>
              </el-table-column>
            </el-table>
          </div>

          <!-- Possible Types (for Interfaces/Unions) -->
          <div class="type-possible" v-if="selectedType.possibleTypes?.length">
            <h4>Possible Types</h4>
            <div class="possible-types">
              <el-tag
                  v-for="type in selectedType.possibleTypes"
                  :key="type"
                  size="default"
                  style="margin-right: 8px; cursor: pointer"
                  @click="navigateToType(type)"
              >
                {{ type }}
              </el-tag>
            </div>
          </div>

          <!-- Implements (for Interfaces) -->
          <div class="type-implements" v-if="selectedType.implements?.length">
            <h4>Implements</h4>
            <div class="implements-list">
              <el-tag
                  v-for="iface in selectedType.implements"
                  :key="iface"
                  type="primary"
                  size="default"
                  style="margin-right: 8px; cursor: pointer"
                  @click="navigateToType(iface)"
              >
                {{ iface }}
              </el-tag>
            </div>
          </div>
        </el-card>

        <!-- Empty State -->
        <el-card class="type-detail-card" shadow="hover" v-else>
          <div class="empty-state">
            <el-empty description="Select a type from the schema explorer" />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- GraphQL Playground Dialog -->
    <el-dialog v-model="playgroundVisible" title="GraphQL Playground" width="1000px" fullscreen destroy-on-close>
      <div class="playground-container">
        <div class="playground-editor">
          <div class="editor-header">
            <span class="editor-title">Query</span>
            <el-button-group size="small">
              <el-button @click="formatQuery">Format</el-button>
              <el-button type="primary" @click="executeQuery" :loading="executing">Execute</el-button>
            </el-button-group>
          </div>
          <el-input
              v-model="queryText"
              type="textarea"
              :rows="12"
              placeholder="query { devices { id name } }"
              class="query-editor"
              font-family="monospace"
          />
        </div>

        <div class="playground-variables">
          <div class="editor-header">
            <span class="editor-title">Variables (JSON)</span>
          </div>
          <el-input
              v-model="variablesText"
              type="textarea"
              :rows="6"
              placeholder='{"limit": 10}'
              class="variables-editor"
              font-family="monospace"
          />
        </div>

        <div class="playground-headers">
          <div class="editor-header">
            <span class="editor-title">Headers (JSON)</span>
          </div>
          <el-input
              v-model="headersText"
              type="textarea"
              :rows="4"
              placeholder='{"Authorization": "Bearer token"}'
              class="headers-editor"
              font-family="monospace"
          />
        </div>

        <div class="playground-response" v-if="queryResponse">
          <div class="editor-header">
            <span class="editor-title">Response</span>
            <div class="response-status">
              <el-tag :type="queryResponse.errors ? 'danger' : 'success'" size="small">
                {{ queryResponse.errors ? 'Error' : 'Success' }}
              </el-tag>
              <span class="response-time">{{ queryResponse.time }}ms</span>
            </div>
          </div>
          <pre class="response-body">{{ JSON.stringify(queryResponse.data, null, 2) }}</pre>
          <div class="response-errors" v-if="queryResponse.errors">
            <el-alert
                v-for="(error, idx) in queryResponse.errors"
                :key="idx"
                :title="error.message"
                type="error"
                :closable="false"
                show-icon
                style="margin-top: 8px"
            />
          </div>
        </div>

        <div class="playground-schema">
          <div class="editor-header">
            <span class="editor-title">Schema Documentation</span>
            <el-button size="small" @click="fetchSchema">Refresh Schema</el-button>
          </div>
          <div class="schema-docs" v-if="schemaDocs">
            <div class="schema-root">
              <div class="schema-section">
                <h4>Queries</h4>
                <div v-for="field in schemaDocs.queryFields" :key="field.name" class="schema-field" @click="navigateToTypeFromDocs(field.type)">
                  <code>{{ field.name }}</code>: {{ field.type }}
                  <span class="field-desc">{{ field.description }}</span>
                </div>
              </div>
              <div class="schema-section">
                <h4>Mutations</h4>
                <div v-for="field in schemaDocs.mutationFields" :key="field.name" class="schema-field" @click="navigateToTypeFromDocs(field.type)">
                  <code>{{ field.name }}</code>: {{ field.type }}
                  <span class="field-desc">{{ field.description }}</span>
                </div>
              </div>
              <div class="schema-section">
                <h4>Subscriptions</h4>
                <div v-for="field in schemaDocs.subscriptionFields" :key="field.name" class="schema-field" @click="navigateToTypeFromDocs(field.type)">
                  <code>{{ field.name }}</code>: {{ field.type }}
                  <span class="field-desc">{{ field.description }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="playgroundVisible = false">Close</el-button>
      </template>
    </el-dialog>

    <!-- Query History Dialog -->
    <el-dialog v-model="historyVisible" title="Query History" width="600px" destroy-on-close>
      <el-table :data="queryHistory" size="small" border>
        <el-table-column prop="timestamp" label="Time" width="160" />
        <el-table-column prop="query" label="Query" min-width="300" show-overflow-tooltip />
        <el-table-column label="Action" width="80">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="loadQuery(row)">Load</el-button>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="historyVisible = false">Close</el-button>
        <el-button @click="clearHistory">Clear History</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Plus, ArrowUp, ArrowDown, Document, Checked,
  Clock, TrendCharts, Refresh, Search, Download, Setting,
  Monitor, List, Key, Collection, Connection
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading GraphQL schema...',
  'Building type system...',
  'Almost ready...'
]

// ==================== State ====================
const schemaFilter = ref('')
const selectedType = ref<any>(null)
const playgroundVisible = ref(false)
const historyVisible = ref(false)
const executing = ref(false)
const queryText = ref(`query {
  devices(limit: 10) {
    id
    name
    type
    status
    location
  }
}`)
const variablesText = ref('{}')
const headersText = ref('{}')
const queryResponse = ref<any>(null)
const queryHistory = ref<any[]>([])

const treeProps = {
  children: 'children',
  label: 'name'
}

// ==================== Mock Stats ====================
const statsCards = ref([
  { title: 'Total Types', value: 48, trend: 12, icon: 'Key', bgColor: '#409eff', key: 'types' },
  { title: 'Queries', value: 24, trend: 8, icon: 'Search', bgColor: '#67c23a', key: 'queries' },
  { title: 'Mutations', value: 16, trend: 5, icon: 'Edit', bgColor: '#e6a23c', key: 'mutations' },
  { title: 'Subscriptions', value: 8, trend: 15, icon: 'Connection', bgColor: '#f56c6c', key: 'subscriptions' }
])

// ==================== Mock Schema Data ====================
const schemaTypes = ref([
  {
    name: 'Query',
    kind: 'OBJECT',
    description: 'Root query type for fetching data',
    fields: [
      { name: 'devices', type: '[Device!]!', description: 'Get all devices with optional filters', args: [
          { name: 'limit', type: 'Int', description: 'Max number of results' },
          { name: 'offset', type: 'Int', description: 'Pagination offset' },
          { name: 'status', type: 'DeviceStatus', description: 'Filter by device status' }
        ] },
      { name: 'device', type: 'Device', description: 'Get a single device by ID', args: [
          { name: 'id', type: 'ID!', description: 'Device ID' }
        ] },
      { name: 'telemetry', type: '[TelemetryPoint!]!', description: 'Get telemetry data for a device', args: [
          { name: 'deviceId', type: 'ID!', description: 'Device ID' },
          { name: 'startTime', type: 'DateTime!', description: 'Start timestamp' },
          { name: 'endTime', type: 'DateTime!', description: 'End timestamp' }
        ] }
    ]
  },
  {
    name: 'Mutation',
    kind: 'OBJECT',
    description: 'Root mutation type for modifying data',
    fields: [
      { name: 'createDevice', type: 'Device!', description: 'Create a new device', args: [
          { name: 'input', type: 'CreateDeviceInput!', description: 'Device input data' }
        ] },
      { name: 'updateDevice', type: 'Device!', description: 'Update an existing device', args: [
          { name: 'id', type: 'ID!', description: 'Device ID' },
          { name: 'input', type: 'UpdateDeviceInput!', description: 'Update data' }
        ] },
      { name: 'deleteDevice', type: 'DeleteResult!', description: 'Delete a device', args: [
          { name: 'id', type: 'ID!', description: 'Device ID' }
        ] }
    ]
  },
  {
    name: 'Subscription',
    kind: 'OBJECT',
    description: 'Real-time subscriptions',
    fields: [
      { name: 'deviceTelemetry', type: 'TelemetryPoint!', description: 'Subscribe to real-time telemetry', args: [
          { name: 'deviceId', type: 'ID!', description: 'Device ID' }
        ] }
    ]
  },
  {
    name: 'Device',
    kind: 'OBJECT',
    description: 'A physical device or sensor',
    fields: [
      { name: 'id', type: 'ID!', description: 'Unique device identifier' },
      { name: 'name', type: 'String!', description: 'Device display name' },
      { name: 'type', type: 'DeviceType!', description: 'Type of device' },
      { name: 'status', type: 'DeviceStatus!', description: 'Current device status' },
      { name: 'location', type: 'String', description: 'Device location' },
      { name: 'manufacturer', type: 'String', description: 'Device manufacturer' },
      { name: 'model', type: 'String', description: 'Device model number' },
      { name: 'telemetry', type: '[TelemetryPoint!]', description: 'Telemetry data for this device', args: [
          { name: 'limit', type: 'Int', description: 'Max number of points' }
        ] }
    ]
  },
  {
    name: 'TelemetryPoint',
    kind: 'OBJECT',
    description: 'A single telemetry reading',
    fields: [
      { name: 'timestamp', type: 'DateTime!', description: 'Reading timestamp' },
      { name: 'metric', type: 'String!', description: 'Metric name' },
      { name: 'value', type: 'Float!', description: 'Reading value' },
      { name: 'unit', type: 'String', description: 'Unit of measurement' }
    ]
  },
  {
    name: 'CreateDeviceInput',
    kind: 'INPUT_OBJECT',
    description: 'Input for creating a device',
    fields: [
      { name: 'name', type: 'String!', description: 'Device name' },
      { name: 'type', type: 'DeviceType!', description: 'Device type' },
      { name: 'location', type: 'String', description: 'Device location' },
      { name: 'manufacturer', type: 'String', description: 'Device manufacturer' }
    ]
  },
  {
    name: 'UpdateDeviceInput',
    kind: 'INPUT_OBJECT',
    description: 'Input for updating a device',
    fields: [
      { name: 'name', type: 'String', description: 'Device name' },
      { name: 'location', type: 'String', description: 'Device location' },
      { name: 'status', type: 'DeviceStatus', description: 'Device status' }
    ]
  },
  {
    name: 'DeleteResult',
    kind: 'OBJECT',
    description: 'Result of a delete operation',
    fields: [
      { name: 'success', type: 'Boolean!', description: 'Whether deletion succeeded' },
      { name: 'message', type: 'String', description: 'Result message' }
    ]
  },
  {
    name: 'DeviceType',
    kind: 'ENUM',
    description: 'Possible device types',
    values: [
      { name: 'HVAC', description: 'Heating, ventilation, and air conditioning' },
      { name: 'LIGHTING', description: 'Lighting control' },
      { name: 'POWER', description: 'Power distribution' },
      { name: 'SENSOR', description: 'Environmental sensor' },
      { name: 'SECURITY', description: 'Security system' }
    ]
  },
  {
    name: 'DeviceStatus',
    kind: 'ENUM',
    description: 'Possible device statuses',
    values: [
      { name: 'ACTIVE', description: 'Device is operational' },
      { name: 'INACTIVE', description: 'Device is offline' },
      { name: 'MAINTENANCE', description: 'Device under maintenance' },
      { name: 'ERROR', description: 'Device has an error' }
    ]
  },
  {
    name: 'DateTime',
    kind: 'SCALAR',
    description: 'ISO 8601 datetime string'
  }
])

// Build schema tree
const buildSchemaTree = () => {
  const rootTypes = ['Query', 'Mutation', 'Subscription']
  const tree: any[] = []

  // Add root operation types
  const rootNode = { name: 'Root Types', kind: 'ROOT', children: [] }
  rootTypes.forEach(typeName => {
    const type = schemaTypes.value.find(t => t.name === typeName)
    if (type) {
      rootNode.children.push({ ...type, kind: 'OBJECT' })
    }
  })
  tree.push(rootNode)

  // Add other types
  const otherTypes = schemaTypes.value.filter(t => !rootTypes.includes(t.name))
  const otherNode = { name: 'Other Types', kind: 'OTHER', children: [] }
  const objectsNode = { name: 'Objects', kind: 'CATEGORY', children: [] }
  const inputsNode = { name: 'Input Objects', kind: 'CATEGORY', children: [] }
  const enumsNode = { name: 'Enums', kind: 'CATEGORY', children: [] }
  const scalarsNode = { name: 'Scalars', kind: 'CATEGORY', children: [] }

  otherTypes.forEach(type => {
    if (type.kind === 'OBJECT') objectsNode.children.push(type)
    else if (type.kind === 'INPUT_OBJECT') inputsNode.children.push(type)
    else if (type.kind === 'ENUM') enumsNode.children.push(type)
    else if (type.kind === 'SCALAR') scalarsNode.children.push(type)
  })

  if (objectsNode.children.length) otherNode.children.push(objectsNode)
  if (inputsNode.children.length) otherNode.children.push(inputsNode)
  if (enumsNode.children.length) otherNode.children.push(enumsNode)
  if (scalarsNode.children.length) otherNode.children.push(scalarsNode)

  tree.push(otherNode)

  return tree
}

const schemaTree = ref(buildSchemaTree())

const filteredSchemaTree = computed(() => {
  if (!schemaFilter.value) return schemaTree.value

  const filterNode = (node: any): any => {
    if (node.name?.toLowerCase().includes(schemaFilter.value.toLowerCase())) {
      return node
    }
    if (node.children) {
      const filteredChildren = node.children.map(filterNode).filter(Boolean)
      if (filteredChildren.length) {
        return { ...node, children: filteredChildren }
      }
    }
    return null
  }

  return schemaTree.value.map(filterNode).filter(Boolean)
})

// ==================== Helper Methods ====================
const getNodeIcon = (kind: string) => {
  const map: Record<string, string> = {
    'OBJECT': 'Key',
    'INPUT_OBJECT': 'Edit',
    'ENUM': 'List',
    'SCALAR': 'Document',
    'ROOT': 'Collection',
    'OTHER': 'Folder',
    'CATEGORY': 'Folder'
  }
  return map[kind] || 'Document'
}

const getNodeColor = (kind: string) => {
  const map: Record<string, string> = {
    'OBJECT': '#409eff',
    'INPUT_OBJECT': '#67c23a',
    'ENUM': '#e6a23c',
    'SCALAR': '#909399',
    'ROOT': '#f56c6c',
    'OTHER': '#909399',
    'CATEGORY': '#909399'
  }
  return map[kind] || '#909399'
}

const getKindTag = (kind: string) => {
  const map: Record<string, string> = {
    'OBJECT': 'primary',
    'INPUT_OBJECT': 'success',
    'ENUM': 'warning',
    'SCALAR': 'info'
  }
  return map[kind] || 'info'
}

const handleSchemaNodeClick = (data: any) => {
  if (data.fields || data.values) {
    selectedType.value = data
  }
}

const copyTypeName = () => {
  if (selectedType.value) {
    navigator.clipboard.writeText(selectedType.value.name)
    ElMessage.success('Type name copied')
  }
}

const navigateToType = (typeName: string) => {
  const type = schemaTypes.value.find(t => t.name === typeName)
  if (type) {
    selectedType.value = type
  }
}

const navigateToTypeFromDocs = (typeName: string) => {
  // Extract base type name (remove [] and !)
  const baseName = typeName.replace(/[\[\]!]/g, '')
  navigateToType(baseName)
}

// ==================== Playground Methods ====================
const openPlayground = () => {
  playgroundVisible.value = true
  fetchSchema()
}

const formatQuery = () => {
  try {
    // Simple formatting - prettify JSON-like structure
    const formatted = queryText.value
        .replace(/\{/g, '{\n  ')
        .replace(/\}/g, '\n}')
        .replace(/  /g, '  ')
    queryText.value = formatted
  } catch (e) {
    ElMessage.warning('Could not format query')
  }
}

const executeQuery = () => {
  executing.value = true
  setTimeout(() => {
    executing.value = false

    // Mock response based on query
    const isError = queryText.value.includes('error') || queryText.value.includes('invalid')

    if (isError) {
      queryResponse.value = {
        data: null,
        errors: [{ message: 'Invalid query syntax or field not found' }],
        time: Math.floor(Math.random() * 150) + 50
      }
    } else {
      queryResponse.value = {
        data: {
          devices: [
            { id: 'DEV-001', name: 'Chiller-01', type: 'HVAC', status: 'ACTIVE', location: 'Building A' },
            { id: 'DEV-002', name: 'AHU-03', type: 'HVAC', status: 'ACTIVE', location: 'Building A' },
            { id: 'DEV-003', name: 'Lighting Panel LP1', type: 'LIGHTING', status: 'ACTIVE', location: 'Floor 2' }
          ]
        },
        time: Math.floor(Math.random() * 100) + 20
      }
    }

    // Save to history
    queryHistory.value.unshift({
      timestamp: new Date().toLocaleString(),
      query: queryText.value.substring(0, 100) + (queryText.value.length > 100 ? '...' : '')
    })
    if (queryHistory.value.length > 20) queryHistory.value.pop()

  }, 800)
}

const fetchSchema = () => {
  // Mock schema docs
  const schemaDocs = {
    queryFields: [
      { name: 'devices', type: '[Device!]!', description: 'Get all devices with optional filters' },
      { name: 'device', type: 'Device', description: 'Get a single device by ID' },
      { name: 'telemetry', type: '[TelemetryPoint!]!', description: 'Get telemetry data for a device' }
    ],
    mutationFields: [
      { name: 'createDevice', type: 'Device!', description: 'Create a new device' },
      { name: 'updateDevice', type: 'Device!', description: 'Update an existing device' },
      { name: 'deleteDevice', type: 'DeleteResult!', description: 'Delete a device' }
    ],
    subscriptionFields: [
      { name: 'deviceTelemetry', type: 'TelemetryPoint!', description: 'Subscribe to real-time telemetry' }
    ]
  }
  // Would set schemaDocs in real implementation
}

const loadQuery = (historyItem: any) => {
  queryText.value = historyItem.query
  historyVisible.value = false
  ElMessage.success('Query loaded')
}

const clearHistory = () => {
  queryHistory.value = []
  ElMessage.success('History cleared')
}

// ==================== Other Methods ====================
const handleCardClick = (stat: any) => {
  ElMessage.info(`Viewing ${stat.title} details`)
}

const handleExport = () => {
  ElMessage.success('Exporting GraphQL schema...')
}

// ==================== Loading Simulation ====================
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
      // Auto-select Query type
      selectedType.value = schemaTypes.value.find(t => t.name === 'Query')
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
.graphql-page {
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

.main-row {
  .schema-card, .type-detail-card {
    height: calc(100vh - 280px);
    overflow-y: auto;

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-weight: 600;
    }
  }
}

.schema-tree {
  .schema-node {
    display: flex;
    align-items: center;
    gap: 8px;

    .el-icon {
      flex-shrink: 0;
    }

    .node-tag {
      margin-left: auto;
    }
  }
}

.type-detail-card {
  .type-title {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 18px;
    font-weight: 600;
  }

  .type-description {
    margin-bottom: 16px;
  }

  .type-fields, .type-args, .type-possible, .type-implements {
    margin-top: 20px;

    h4 {
      margin-bottom: 12px;
      color: #303133;
    }
  }

  .field-name {
    font-family: monospace;
    font-weight: 500;
  }

  .field-tag {
    margin-left: 8px;
  }

  .type-code {
    font-family: monospace;
    background: #f5f7fa;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 12px;
  }

  .possible-types, .implements-list {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  .empty-state {
    height: 500px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

.playground-container {
  .playground-editor, .playground-variables, .playground-headers, .playground-response, .playground-schema {
    margin-bottom: 16px;

    .editor-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;
      padding: 8px;
      background: #f5f7fa;
      border-radius: 4px;

      .editor-title {
        font-weight: 600;
        font-size: 14px;
      }

      .response-status {
        display: flex;
        align-items: center;
        gap: 8px;

        .response-time {
          font-size: 12px;
          color: #909399;
        }
      }
    }

    .query-editor, .variables-editor, .headers-editor {
      font-family: monospace;
    }

    .response-body {
      background: #1e1e1e;
      color: #d4d4d4;
      padding: 12px;
      border-radius: 4px;
      font-family: monospace;
      font-size: 12px;
      overflow-x: auto;
      max-height: 300px;
    }
  }

  .schema-docs {
    .schema-root {
      .schema-section {
        margin-bottom: 16px;

        h4 {
          margin-bottom: 8px;
          color: #409eff;
        }

        .schema-field {
          padding: 4px 0;
          cursor: pointer;

          &:hover {
            background: #f5f7fa;
          }

          code {
            font-family: monospace;
            color: #e6a23c;
          }

          .field-desc {
            margin-left: 8px;
            color: #909399;
            font-size: 12px;
          }
        }
      }
    }
  }
}

:deep(.el-tree-node__content) {
  height: 32px;
}

:deep(.el-dialog__body) {
  padding: 20px;
  max-height: 80vh;
  overflow-y: auto;
}
</style>