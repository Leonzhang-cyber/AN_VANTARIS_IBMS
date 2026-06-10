<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, Search, Refresh, View, Edit, Delete, Monitor, Connection,
  User, Warning, Clock, Cpu, DataLine, Message, Upload, Download,
  Setting, Document, Checked, Bell, TrendCharts, Chip, Microchip,
  List, Odometer, Location, Link, Share, VideoCamera, Lock,
  CopyDocument, Switch, Filter, MagicStick, Tickets, Right,
  Sort, FolderOpened, Files, DocumentAdd
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Initializing mapping engine...',
  'Loading transformation templates...',
  'Almost ready...'
]

// ==================== Chart Refs ====================
const mappingStatsChart = ref<HTMLElement | null>(null)
const transformationChart = ref<HTMLElement | null>(null)
const performanceChart = ref<HTMLElement | null>(null)

// ==================== State ====================
const activeTab = ref('mappings')
const searchKeyword = ref('')
const statusFilter = ref('')
const protocolFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(15)
const mappingDialogVisible = ref(false)
const testDialogVisible = ref(false)
const importDialogVisible = ref(false)
const exportDialogVisible = ref(false)
const templateDialogVisible = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')
const selectedMapping = ref<any>(null)
const mappingFormRef = ref()
const testing = ref(false)
const testResult = ref<any>(null)
const testPayload = ref('')
const importFile = ref<File | null>(null)

// ==================== Statistics ====================
const statistics = reactive({
  totalMappings: 24,
  activeMappings: 22,
  totalTransformations: 18,
  totalRules: 32,
  avgProcessingTime: 12.5,
  totalProcessed: 15680,
  successRate: 98.5
})

// ==================== Payload Mappings Data ====================
interface PayloadMapping {
  id: number
  name: string
  sourceProtocol: string
  targetProtocol: string
  sourceField: string
  targetField: string
  dataType: string
  transformation: string
  status: 'active' | 'inactive'
  priority: number
  createdAt: string
  updatedAt: string
  description: string
  example?: string
}

const payloadMappings = ref<PayloadMapping[]>([
  {
    id: 1,
    name: 'Temperature Conversion (C→F)',
    sourceProtocol: 'MQTT',
    targetProtocol: 'BACnet',
    sourceField: 'payload.temp_celsius',
    targetField: 'analog_input.temperature',
    dataType: 'number',
    transformation: 'value => value * 1.8 + 32',
    status: 'active',
    priority: 1,
    createdAt: '2024-01-10',
    updatedAt: '2024-01-15',
    description: 'Convert Celsius to Fahrenheit for HVAC system',
    example: '{"payload": {"temp_celsius": 25}} → {"temperature": 77}'
  },
  {
    id: 2,
    name: 'Humidity Mapping',
    sourceProtocol: 'MQTT',
    targetProtocol: 'BACnet',
    sourceField: 'payload.humidity',
    targetField: 'analog_input.humidity',
    dataType: 'number',
    transformation: 'value => value',
    status: 'active',
    priority: 1,
    createdAt: '2024-01-10',
    updatedAt: '2024-01-10',
    description: 'Direct humidity value mapping',
    example: '{"payload": {"humidity": 65}} → {"humidity": 65}'
  },
  {
    id: 3,
    name: 'Battery Level Normalization',
    sourceProtocol: 'BLE',
    targetProtocol: 'Modbus',
    sourceField: 'battery_raw',
    targetField: 'battery_percentage',
    dataType: 'number',
    transformation: 'value => Math.min(100, Math.max(0, value * 100 / 3.3))',
    status: 'active',
    priority: 2,
    createdAt: '2024-01-12',
    updatedAt: '2024-01-14',
    description: 'Convert raw ADC reading to battery percentage',
    example: '{"battery_raw": 2.8} → {"battery_percentage": 84.8}'
  },
  {
    id: 4,
    name: 'Occupancy Status Detection',
    sourceProtocol: 'BLE',
    targetProtocol: 'HTTP',
    sourceField: 'rssi',
    targetField: 'occupancy.status',
    dataType: 'string',
    transformation: 'value => value > -70 ? "occupied" : "vacant"',
    status: 'active',
    priority: 1,
    createdAt: '2024-01-11',
    updatedAt: '2024-01-11',
    description: 'Determine occupancy based on RSSI threshold',
    example: '{"rssi": -65} → {"status": "occupied"}'
  },
  {
    id: 5,
    name: 'Timestamp Format Conversion',
    sourceProtocol: 'LoRaWAN',
    targetProtocol: 'MQTT',
    sourceField: 'timestamp_epoch',
    targetField: 'timestamp_iso',
    dataType: 'string',
    transformation: 'value => new Date(value * 1000).toISOString()',
    status: 'active',
    priority: 3,
    createdAt: '2024-01-13',
    updatedAt: '2024-01-13',
    description: 'Convert Unix timestamp to ISO format',
    example: '{"timestamp_epoch": 1705310133} → {"timestamp_iso": "2024-01-15T10:15:33.000Z"}'
  },
  {
    id: 6,
    name: 'Pressure Unit Conversion',
    sourceProtocol: 'Modbus',
    targetProtocol: 'BACnet',
    sourceField: 'pressure_psi',
    targetField: 'pressure_kpa',
    dataType: 'number',
    transformation: 'value => value * 6.89476',
    status: 'inactive',
    priority: 2,
    createdAt: '2024-01-09',
    updatedAt: '2024-01-09',
    description: 'Convert PSI to kPa',
    example: '{"pressure_psi": 14.7} → {"pressure_kpa": 101.35}'
  },
  {
    id: 7,
    name: 'Device Type Mapping',
    sourceProtocol: 'HTTP',
    targetProtocol: 'MQTT',
    sourceField: 'device_type_code',
    targetField: 'device_category',
    dataType: 'string',
    transformation: `value => {
  const map = { '01': 'sensor', '02': 'actuator', '03': 'gateway' };
  return map[value] || 'unknown';
}`,
    status: 'active',
    priority: 1,
    createdAt: '2024-01-14',
    updatedAt: '2024-01-14',
    description: 'Map device type codes to categories',
    example: '{"device_type_code": "01"} → {"device_category": "sensor"}'
  },
  {
    id: 8,
    name: 'Array to CSV Conversion',
    sourceProtocol: 'MQTT',
    targetProtocol: 'HTTP',
    sourceField: 'data.values',
    targetField: 'csv_data',
    dataType: 'string',
    transformation: 'value => Array.isArray(value) ? value.join(",") : value',
    status: 'active',
    priority: 2,
    createdAt: '2024-01-15',
    updatedAt: '2024-01-15',
    description: 'Convert array of values to CSV string',
    example: '{"values": [1,2,3,4]} → {"csv_data": "1,2,3,4"}'
  },
  {
    id: 9,
    name: 'Energy Calculation',
    sourceProtocol: 'Modbus',
    targetProtocol: 'MQTT',
    sourceField: 'power_watts',
    targetField: 'energy_kwh',
    dataType: 'number',
    transformation: 'value => value * duration_hours / 1000',
    status: 'active',
    priority: 1,
    createdAt: '2024-01-16',
    updatedAt: '2024-01-16',
    description: 'Calculate energy consumption in kWh',
    example: '{"power_watts": 1500, "duration_hours": 2} → {"energy_kwh": 3}'
  }
])

// ==================== Transformation Templates ====================
const transformationTemplates = ref([
  { id: 1, name: 'Celsius to Fahrenheit', expression: 'value => value * 1.8 + 32', category: 'Temperature' },
  { id: 2, name: 'Fahrenheit to Celsius', expression: 'value => (value - 32) / 1.8', category: 'Temperature' },
  { id: 3, name: 'PSI to kPa', expression: 'value => value * 6.89476', category: 'Pressure' },
  { id: 4, name: 'kPa to PSI', expression: 'value => value / 6.89476', category: 'Pressure' },
  { id: 5, name: 'RSSI to Distance', expression: 'value => Math.pow(10, (-69 - value) / (10 * 2))', category: 'Signal' },
  { id: 6, name: 'Normalize 0-100', expression: 'value => Math.min(100, Math.max(0, value))', category: 'Normalization' },
  { id: 7, name: 'Scale 0-10 to 0-100', expression: 'value => value * 10', category: 'Scale' },
  { id: 8, name: 'Unix to ISO Date', expression: 'value => new Date(value * 1000).toISOString()', category: 'Date' },
  { id: 9, name: 'Round to 2 decimals', expression: 'value => Math.round(value * 100) / 100', category: 'Math' },
  { id: 10, name: 'Percentage Calculation', expression: 'value => (value / total) * 100', category: 'Math' }
])

// ==================== Mapping Rules ====================
const mappingRules = ref([
  { id: 1, name: 'Required Field Validation', condition: 'source_field exists', action: 'validate', enabled: true },
  { id: 2, name: 'Null Value Handler', condition: 'value !== null && value !== undefined', action: 'skip', enabled: true },
  { id: 3, name: 'Range Validation', condition: 'value >= min && value <= max', action: 'clamp', enabled: true },
  { id: 4, name: 'Type Validation', condition: 'typeof value === "number"', action: 'convert', enabled: false },
  { id: 5, name: 'String Truncation', condition: 'value.length > max_length', action: 'truncate', enabled: false }
])

// ==================== Processing History ====================
const processingHistory = ref([
  { id: 1, timestamp: '2024-01-15 10:23:45', mappingId: 1, mappingName: 'Temperature Conversion', source: '{"temp_celsius": 25}', output: '{"temperature": 77}', duration: 2.5, status: 'success' },
  { id: 2, timestamp: '2024-01-15 10:20:12', mappingId: 3, mappingName: 'Battery Level', source: '{"battery_raw": 2.8}', output: '{"battery_percentage": 84.8}', duration: 1.8, status: 'success' },
  { id: 3, timestamp: '2024-01-15 10:15:33', mappingId: 5, mappingName: 'Timestamp Format', source: '{"timestamp_epoch": 1705310133}', output: '{"timestamp_iso": "2024-01-15T10:15:33.000Z"}', duration: 1.2, status: 'success' },
  { id: 4, timestamp: '2024-01-15 10:10:22', mappingId: 2, mappingName: 'Humidity Mapping', source: '{"humidity": 65}', output: '{"humidity": 65}', duration: 0.8, status: 'error' },
  { id: 5, timestamp: '2024-01-15 10:05:18', mappingId: 7, mappingName: 'Device Type', source: '{"device_type_code": "01"}', output: '{"device_category": "sensor"}', duration: 1.5, status: 'success' }
])

// ==================== Form Models ====================
const newMapping = ref({
  name: '',
  sourceProtocol: '',
  targetProtocol: '',
  sourceField: '',
  targetField: '',
  dataType: 'number',
  transformation: '',
  priority: 1,
  description: ''
})

const testMapping = ref({
  mappingId: null as number | null,
  sourcePayload: ''
})

// ==================== Form Rules ====================
const mappingRulesForm = {
  name: [{ required: true, message: 'Please enter mapping name', trigger: 'blur' }],
  sourceProtocol: [{ required: true, message: 'Please select source protocol', trigger: 'change' }],
  targetProtocol: [{ required: true, message: 'Please select target protocol', trigger: 'change' }],
  sourceField: [{ required: true, message: 'Please enter source field', trigger: 'blur' }],
  targetField: [{ required: true, message: 'Please enter target field', trigger: 'blur' }]
}

// ==================== Protocols ====================
const protocols = ['MQTT', 'HTTP', 'CoAP', 'LoRaWAN', 'Modbus', 'BACnet', 'BLE', 'OPC-UA', 'SNMP']

// ==================== Data Types ====================
const dataTypes = ['number', 'string', 'boolean', 'object', 'array', 'integer']

// ==================== Computed ====================
const filteredMappings = computed(() => {
  let filtered = payloadMappings.value
  if (searchKeyword.value) {
    filtered = filtered.filter(m =>
        m.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        m.sourceField.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        m.targetField.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        m.description.toLowerCase().includes(searchKeyword.value.toLowerCase())
    )
  }
  if (statusFilter.value) {
    filtered = filtered.filter(m => m.status === statusFilter.value)
  }
  if (protocolFilter.value) {
    filtered = filtered.filter(m => m.sourceProtocol === protocolFilter.value || m.targetProtocol === protocolFilter.value)
  }
  return filtered
})

const paginatedMappings = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredMappings.value.slice(start, end)
})

const activeCount = computed(() => payloadMappings.value.filter(m => m.status === 'active').length)
const inactiveCount = computed(() => payloadMappings.value.filter(m => m.status === 'inactive').length)

// ==================== Methods ====================
const getStatusTagType = (status: string) => {
  return status === 'active' ? 'success' : 'info'
}

const getProtocolColor = (protocol: string) => {
  const colors: Record<string, string> = {
    'MQTT': 'primary',
    'HTTP': 'success',
    'CoAP': 'warning',
    'LoRaWAN': 'danger',
    'Modbus': 'info',
    'BACnet': '',
    'BLE': 'primary',
    'OPC-UA': 'warning',
    'SNMP': 'info'
  }
  return colors[protocol] || ''
}

const formatDate = (date: string) => {
  if (!date) return 'N/A'
  return date
}

const handleCreateMapping = () => {
  dialogMode.value = 'create'
  newMapping.value = {
    name: '',
    sourceProtocol: '',
    targetProtocol: '',
    sourceField: '',
    targetField: '',
    dataType: 'number',
    transformation: '',
    priority: 1,
    description: ''
  }
  mappingDialogVisible.value = true
}

const handleEditMapping = (mapping: PayloadMapping) => {
  dialogMode.value = 'edit'
  newMapping.value = { ...mapping }
  selectedMapping.value = mapping
  mappingDialogVisible.value = true
}

const handleSaveMapping = async () => {
  await mappingFormRef.value?.validate()
  if (dialogMode.value === 'create') {
    const mapping: PayloadMapping = {
      id: Math.max(...payloadMappings.value.map(m => m.id)) + 1,
      name: newMapping.value.name,
      sourceProtocol: newMapping.value.sourceProtocol,
      targetProtocol: newMapping.value.targetProtocol,
      sourceField: newMapping.value.sourceField,
      targetField: newMapping.value.targetField,
      dataType: newMapping.value.dataType,
      transformation: newMapping.value.transformation,
      status: 'active',
      priority: newMapping.value.priority,
      createdAt: new Date().toISOString().split('T')[0],
      updatedAt: new Date().toISOString().split('T')[0],
      description: newMapping.value.description
    }
    payloadMappings.value.push(mapping)
    ElMessage.success('Payload mapping created successfully')
    statistics.totalMappings++
    statistics.activeMappings++
  } else if (selectedMapping.value) {
    const index = payloadMappings.value.findIndex(m => m.id === selectedMapping.value.id)
    if (index !== -1) {
      payloadMappings.value[index] = {
        ...payloadMappings.value[index],
        ...newMapping.value,
        updatedAt: new Date().toISOString().split('T')[0]
      }
      ElMessage.success('Payload mapping updated successfully')
    }
  }
  mappingDialogVisible.value = false
}

const handleDeleteMapping = (mapping: PayloadMapping) => {
  ElMessageBox.confirm(
      `Are you sure you want to delete mapping "${mapping.name}"? This action cannot be undone.`,
      'Confirm Delete',
      { type: 'warning' }
  ).then(() => {
    const index = payloadMappings.value.findIndex(m => m.id === mapping.id)
    if (index !== -1) {
      payloadMappings.value.splice(index, 1)
      if (mapping.status === 'active') {
        statistics.activeMappings--
      }
      statistics.totalMappings--
      ElMessage.success('Mapping deleted successfully')
    }
  }).catch(() => {})
}

const handleToggleStatus = (mapping: PayloadMapping) => {
  const index = payloadMappings.value.findIndex(m => m.id === mapping.id)
  if (index !== -1) {
    const newStatus = payloadMappings.value[index].status === 'active' ? 'inactive' : 'active'
    payloadMappings.value[index].status = newStatus
    if (newStatus === 'active') {
      statistics.activeMappings++
    } else {
      statistics.activeMappings--
    }
    ElMessage.success(`Mapping ${newStatus === 'active' ? 'activated' : 'deactivated'}`)
  }
}

const handleTestMapping = (mapping: PayloadMapping) => {
  selectedMapping.value = mapping
  // Generate example payload based on source field
  const fieldName = mapping.sourceField.split('.').pop() || 'value'
  testPayload.value = JSON.stringify({
    [fieldName]: mapping.dataType === 'number' ? 25 : mapping.dataType === 'string' ? 'test_value' : true
  }, null, 2)
  testResult.value = null
  testDialogVisible.value = true
}

const handleRunTest = async () => {
  testing.value = true
  setTimeout(() => {
    try {
      const sourceData = JSON.parse(testPayload.value)
      const mapping = selectedMapping.value

      // Extract value from nested object
      let inputValue = sourceData
      const fieldParts = mapping.sourceField.split('.')
      for (const part of fieldParts) {
        if (inputValue && typeof inputValue === 'object') {
          inputValue = inputValue[part]
        } else {
          break
        }
      }

      // Apply transformation
      let transformedValue = inputValue
      if (mapping.transformation && inputValue !== undefined) {
        try {
          // Safe evaluation for demo
          const fn = new Function('value', `return (${mapping.transformation})(value)`)
          transformedValue = fn(inputValue)
        } catch (e) {
          transformedValue = inputValue
        }
      }

      testResult.value = {
        success: true,
        input: sourceData,
        inputValue: inputValue,
        output: {
          [mapping.targetField.split('.').pop() || mapping.targetField]: transformedValue
        },
        processingTime: (Math.random() * 5 + 0.5).toFixed(2),
        transformationApplied: !!mapping.transformation
      }
      ElMessage.success('Test completed successfully')
    } catch (e) {
      testResult.value = {
        success: false,
        error: 'Invalid JSON payload',
        details: (e as Error).message
      }
      ElMessage.error('Invalid JSON payload')
    }
    testing.value = false
  }, 1000)
}

const handleDuplicateMapping = (mapping: PayloadMapping) => {
  const newMap = {
    ...mapping,
    id: Math.max(...payloadMappings.value.map(m => m.id)) + 1,
    name: `${mapping.name} (Copy)`,
    createdAt: new Date().toISOString().split('T')[0],
    updatedAt: new Date().toISOString().split('T')[0]
  }
  payloadMappings.value.push(newMap)
  statistics.totalMappings++
  if (newMap.status === 'active') statistics.activeMappings++
  ElMessage.success('Mapping duplicated successfully')
}

const handleRefresh = () => {
  ElMessage.info('Refreshing data...')
  setTimeout(() => {
    statistics.totalProcessed += Math.floor(Math.random() * 100)
    ElMessage.success('Data refreshed')
  }, 500)
}

const handleExportMappings = () => {
  const exportData = {
    mappings: payloadMappings.value,
    rules: mappingRules.value,
    exportDate: new Date().toISOString(),
    version: '1.0'
  }
  const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `payload_mappings_${new Date().toISOString().split('T')[0]}.json`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('Mappings exported successfully')
}

const handleImportMappings = () => {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = '.json'
  input.onchange = (e: any) => {
    const file = e.target.files[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (event: any) => {
        try {
          const data = JSON.parse(event.target.result)
          if (data.mappings && Array.isArray(data.mappings)) {
            for (const mapping of data.mappings) {
              if (!payloadMappings.value.find(m => m.id === mapping.id)) {
                payloadMappings.value.push(mapping)
              }
            }
            statistics.totalMappings = payloadMappings.value.length
            statistics.activeMappings = payloadMappings.value.filter(m => m.status === 'active').length
            ElMessage.success(`Imported ${data.mappings.length} mappings successfully`)
          }
        } catch (error) {
          ElMessage.error('Invalid import file')
        }
      }
      reader.readAsText(file)
    }
  }
  input.click()
}

const handleApplyTemplate = (template: any) => {
  newMapping.value.transformation = template.expression
  templateDialogVisible.value = false
  ElMessage.success(`Template "${template.name}" applied`)
}

const handleShowTemplateSelector = () => {
  templateDialogVisible.value = true
}

// ==================== Initialize Charts ====================
const initCharts = () => {
  if (!mappingStatsChart.value) return

  // Protocol Distribution Chart (Bar)
  const protocolData: Record<string, number> = {}
  payloadMappings.value.forEach(m => {
    protocolData[m.sourceProtocol] = (protocolData[m.sourceProtocol] || 0) + 1
  })

  const statsChart = echarts.init(mappingStatsChart.value)
  statsChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    xAxis: { type: 'category', data: Object.keys(protocolData), axisLabel: { rotate: 45 } },
    yAxis: { type: 'value', name: 'Number of Mappings' },
    series: [{
      data: Object.values(protocolData),
      type: 'bar',
      itemStyle: { borderRadius: [4, 4, 0, 0], color: '#1890ff' }
    }]
  })

  // Transformation Types Chart (Pie)
  const transChart = echarts.init(transformationChart.value)
  transChart.setOption({
    tooltip: { trigger: 'item' },
    legend: { top: 'bottom', orient: 'vertical', left: 'left' },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      data: [
        { value: 8, name: 'Direct Mapping', itemStyle: { color: '#52c41a' } },
        { value: 6, name: 'Unit Conversion', itemStyle: { color: '#1890ff' } },
        { value: 4, name: 'Conditional Logic', itemStyle: { color: '#faad14' } },
        { value: 3, name: 'Date Formatting', itemStyle: { color: '#ff4d4f' } },
        { value: 3, name: 'Array Operations', itemStyle: { color: '#722ed1' } }
      ],
      label: { show: true, formatter: '{b}: {d}%' }
    }]
  })

  // Performance Chart (Line)
  const perfChart = echarts.init(performanceChart.value)
  perfChart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'] },
    yAxis: { type: 'value', name: 'Processing Time (ms)' },
    series: [{
      data: [12.5, 11.8, 13.2, 14.1, 12.9, 11.5],
      type: 'line',
      smooth: true,
      areaStyle: { opacity: 0.3 },
      lineStyle: { color: '#faad14', width: 2 },
      itemStyle: { color: '#faad14' }
    }]
  })

  // Handle resize
  window.addEventListener('resize', () => {
    statsChart.resize()
    transChart.resize()
    perfChart.resize()
  })
}

// ==================== Watch for Tab Changes ====================
watch(activeTab, (newTab) => {
  if (newTab === 'analytics') {
    nextTick(() => {
      initCharts()
    })
  }
})

// ==================== Loading on Mount ====================
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
      if (activeTab.value === 'analytics') {
        initCharts()
      }
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
          <span class="loading-title">Loading Payload Mapping</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="payload-mapping">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <h2>Payload Mapping</h2>
        <p>Configure data transformations between different protocols, map source fields to target fields, and manage transformation rules</p>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="handleCreateMapping">
          <el-icon><Plus /></el-icon>
          New Mapping
        </el-button>
        <el-button @click="handleImportMappings">
          <el-icon><Upload /></el-icon>
          Import
        </el-button>
        <el-button @click="handleExportMappings">
          <el-icon><Download /></el-icon>
          Export
        </el-button>
        <el-button @click="handleRefresh">
          <el-icon><Refresh /></el-icon>
          Refresh
        </el-button>
      </div>
    </div>

    <!-- Statistics Cards -->
    <div class="stats-cards">
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon" style="background: #e8f4ff">
            <el-icon color="#1890ff" size="28"><Tickets /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ statistics.totalMappings }}</div>
            <div class="stat-label">Total Mappings</div>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon" style="background: #e6f7e6">
            <el-icon color="#52c41a" size="28"><Checked /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ statistics.activeMappings }}</div>
            <div class="stat-label">Active</div>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon" style="background: #fff7e6">
            <el-icon color="#faad14" size="28"><MagicStick /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ statistics.totalTransformations }}</div>
            <div class="stat-label">Transformations</div>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon" style="background: #fdf0e8">
            <el-icon color="#ff7a45" size="28"><DataLine /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ (statistics.totalProcessed / 1000).toFixed(1) }}k</div>
            <div class="stat-label">Messages Processed</div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Main Tabs -->
    <el-tabs v-model="activeTab" class="mapping-tabs">
      <!-- Mappings List Tab -->
      <el-tab-pane label="Mappings" name="mappings">
        <div class="toolbar">
          <div class="toolbar-left">
            <el-input
                v-model="searchKeyword"
                placeholder="Search by name or field..."
                clearable
                style="width: 260px"
                :prefix-icon="Search"
            />
            <el-select v-model="statusFilter" placeholder="Status" clearable style="width: 120px">
              <el-option label="All" value="" />
              <el-option label="Active" value="active" />
              <el-option label="Inactive" value="inactive" />
            </el-select>
            <el-select v-model="protocolFilter" placeholder="Protocol" clearable style="width: 140px">
              <el-option label="All Protocols" value="" />
              <el-option v-for="p in protocols" :key="p" :label="p" :value="p" />
            </el-select>
          </div>
          <div class="toolbar-right">
            <el-button type="info" @click="handleRefresh">
              <el-icon><Refresh /></el-icon>
              Refresh
            </el-button>
          </div>
        </div>

        <el-table :data="paginatedMappings" style="width: 100%; margin-top: 16px" stripe>
          <el-table-column prop="name" label="Mapping Name" min-width="200">
            <template #default="{ row }">
              <div class="mapping-name">
                <span class="name">{{ row.name }}</span>
                <el-tag :type="getStatusTagType(row.status)" size="small" style="margin-left: 8px">
                  {{ row.status.toUpperCase() }}
                </el-tag>
              </div>
              <div class="mapping-desc">{{ row.description }}</div>
            </template>
          </el-table-column>
          <el-table-column label="Source → Target" min-width="220">
            <template #default="{ row }">
              <div class="field-mapping">
                <code class="source">{{ row.sourceField }}</code>
                <el-icon class="arrow-icon"><Right /></el-icon>
                <code class="target">{{ row.targetField }}</code>
              </div>
              <div class="protocol-badge">
                <el-tag :type="getProtocolColor(row.sourceProtocol)" size="small">{{ row.sourceProtocol }}</el-tag>
                <el-icon style="margin: 0 4px"><Right /></el-icon>
                <el-tag :type="getProtocolColor(row.targetProtocol)" size="small">{{ row.targetProtocol }}</el-tag>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="dataType" label="Type" width="100">
            <template #default="{ row }">
              <el-tag effect="plain" size="small">{{ row.dataType }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="priority" label="Priority" width="80" align="center">
            <template #default="{ row }">
              <el-tag :type="row.priority === 1 ? 'danger' : row.priority === 2 ? 'warning' : 'info'" size="small">
                P{{ row.priority }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="updatedAt" label="Updated" width="100" />
          <el-table-column label="Actions" width="300" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" size="small" @click="handleTestMapping(row)">
                <el-icon><Monitor /></el-icon>
                Test
              </el-button>
              <el-button link type="primary" size="small" @click="handleEditMapping(row)">
                <el-icon><Edit /></el-icon>
                Edit
              </el-button>
              <el-button link type="primary" size="small" @click="handleDuplicateMapping(row)">
                <el-icon><CopyDocument /></el-icon>
                Copy
              </el-button>
              <el-button link type="warning" size="small" @click="handleToggleStatus(row)">
                <el-icon><Switch /></el-icon>
                {{ row.status === 'active' ? 'Disable' : 'Enable' }}
              </el-button>
              <el-button link type="danger" size="small" @click="handleDeleteMapping(row)">
                <el-icon><Delete /></el-icon>
                Delete
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- Pagination -->
        <div class="pagination-wrapper">
          <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :page-sizes="[15, 30, 50, 100]"
              :total="filteredMappings.length"
              layout="total, sizes, prev, pager, next, jumper"
          />
        </div>
      </el-tab-pane>

      <!-- Transformation Templates Tab -->
      <el-tab-pane label="Templates" name="templates">
        <div class="templates-container">
          <div class="templates-header">
            <h3>Transformation Templates</h3>
            <el-button type="primary" @click="handleCreateMapping">
              <el-icon><Plus /></el-icon>
              New Template
            </el-button>
          </div>

          <div class="templates-grid">
            <el-card
                v-for="template in transformationTemplates"
                :key="template.id"
                class="template-card"
                shadow="hover"
            >
              <div class="template-header">
                <div class="template-name">
                  <el-icon><MagicStick /></el-icon>
                  <span>{{ template.name }}</span>
                </div>
                <el-tag size="small">{{ template.category }}</el-tag>
              </div>
              <div class="template-expression">
                <code>{{ template.expression }}</code>
              </div>
              <div class="template-actions">
                <el-button size="small" type="primary" @click="handleApplyTemplate(template)">
                  Apply
                </el-button>
                <el-button size="small" @click="handleTestMapping(template)">
                  Preview
                </el-button>
              </div>
            </el-card>
          </div>
        </div>
      </el-tab-pane>

      <!-- Rules Tab -->
      <el-tab-pane label="Mapping Rules" name="rules">
        <div class="rules-header">
          <h3>Validation & Transformation Rules</h3>
          <el-button type="primary">
            <el-icon><Plus /></el-icon>
            Add Rule
          </el-button>
        </div>

        <el-table :data="mappingRules" style="width: 100%; margin-top: 16px" stripe>
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="name" label="Rule Name" min-width="200" />
          <el-table-column prop="condition" label="Condition" min-width="250">
            <template #default="{ row }">
              <code>{{ row.condition }}</code>
            </template>
          </el-table-column>
          <el-table-column prop="action" label="Action" width="120">
            <template #default="{ row }">
              <el-tag size="small">{{ row.action }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="Status" width="100">
            <template #default="{ row }">
              <el-switch v-model="row.enabled" />
            </template>
          </el-table-column>
          <el-table-column label="Actions" width="150">
            <template #default="{ row }">
              <el-button link type="primary" size="small">
                <el-icon><Edit /></el-icon>
                Edit
              </el-button>
              <el-button link type="danger" size="small">
                <el-icon><Delete /></el-icon>
                Delete
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- Analytics Tab -->
      <el-tab-pane label="Analytics" name="analytics">
        <div class="analytics-container">
          <el-row :gutter="16">
            <el-col :xs="24" :lg="14">
              <el-card class="analytics-card" header="Mappings by Protocol">
                <div ref="mappingStatsChart" style="height: 350px"></div>
              </el-card>
            </el-col>
            <el-col :xs="24" :lg="10">
              <el-card class="analytics-card" header="Transformation Types">
                <div ref="transformationChart" style="height: 350px"></div>
              </el-card>
            </el-col>
          </el-row>

          <el-row :gutter="16" style="margin-top: 16px">
            <el-col :span="24">
              <el-card class="analytics-card" header="Average Processing Time Trend">
                <div ref="performanceChart" style="height: 300px"></div>
              </el-card>
            </el-col>
          </el-row>

          <el-row :gutter="16" style="margin-top: 16px">
            <el-col :span="24">
              <el-card class="analytics-card" header="Recent Processing History">
                <el-table :data="processingHistory" style="width: 100%" stripe>
                  <el-table-column prop="timestamp" label="Timestamp" width="180" />
                  <el-table-column prop="mappingName" label="Mapping" min-width="180" />
                  <el-table-column prop="source" label="Source" min-width="200">
                    <template #default="{ row }">
                      <code class="small-code">{{ row.source }}</code>
                    </template>
                  </el-table-column>
                  <el-table-column prop="output" label="Output" min-width="200">
                    <template #default="{ row }">
                      <code class="small-code">{{ row.output }}</code>
                    </template>
                  </el-table-column>
                  <el-table-column prop="duration" label="Duration" width="100" align="center">
                    <template #default="{ row }">
                      <span>{{ row.duration }} ms</span>
                    </template>
                  </el-table-column>
                  <el-table-column prop="status" label="Status" width="100">
                    <template #default="{ row }">
                      <el-tag :type="row.status === 'success' ? 'success' : 'danger'" size="small">
                        {{ row.status.toUpperCase() }}
                      </el-tag>
                    </template>
                  </el-table-column>
                </el-table>
              </el-card>
            </el-col>
          </el-row>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- Create/Edit Mapping Dialog -->
    <el-dialog
        v-model="mappingDialogVisible"
        :title="dialogMode === 'create' ? 'Create Payload Mapping' : 'Edit Payload Mapping'"
        width="750px"
    >
      <el-form :model="newMapping" :rules="mappingRulesForm" ref="mappingFormRef" label-width="140px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Mapping Name" prop="name">
              <el-input v-model="newMapping.name" placeholder="e.g., Temperature Conversion" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Priority">
              <el-select v-model="newMapping.priority" style="width: 100%">
                <el-option label="High (1)" :value="1" />
                <el-option label="Medium (2)" :value="2" />
                <el-option label="Low (3)" :value="3" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Source Protocol" prop="sourceProtocol">
              <el-select v-model="newMapping.sourceProtocol" placeholder="Select protocol" style="width: 100%">
                <el-option v-for="p in protocols" :key="p" :label="p" :value="p" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Target Protocol" prop="targetProtocol">
              <el-select v-model="newMapping.targetProtocol" placeholder="Select protocol" style="width: 100%">
                <el-option v-for="p in protocols" :key="p" :label="p" :value="p" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Source Field" prop="sourceField">
              <el-input v-model="newMapping.sourceField" placeholder="e.g., payload.temp_celsius" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Target Field" prop="targetField">
              <el-input v-model="newMapping.targetField" placeholder="e.g., analog_input.temperature" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Data Type">
              <el-select v-model="newMapping.dataType" style="width: 100%">
                <el-option v-for="dt in dataTypes" :key="dt" :label="dt" :value="dt" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Transformation">
              <div class="transformation-input">
                <el-input
                    v-model="newMapping.transformation"
                    type="textarea"
                    :rows="2"
                    placeholder="value => value * 1.8 + 32"
                />
                <el-button size="small" @click="handleShowTemplateSelector" style="margin-top: 4px">
                  <el-icon><MagicStick /></el-icon>
                  Use Template
                </el-button>
              </div>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="Description">
          <el-input
              v-model="newMapping.description"
              type="textarea"
              :rows="2"
              placeholder="Describe the purpose of this mapping"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="mappingDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="handleSaveMapping">Save</el-button>
      </template>
    </el-dialog>

    <!-- Test Mapping Dialog -->
    <el-dialog v-model="testDialogVisible" :title="`Test Mapping - ${selectedMapping?.name}`" width="750px">
      <div class="test-container">
        <div class="test-input">
          <h4>Input Payload:</h4>
          <el-input
              v-model="testPayload"
              type="textarea"
              :rows="5"
              placeholder='{"value": 25}'
          />
        </div>
        <div class="test-actions" style="margin: 16px 0">
          <el-button type="primary" @click="handleRunTest" :loading="testing">
            <el-icon><Play /></el-icon>
            Run Test
          </el-button>
        </div>
        <div v-if="testResult" class="test-result">
          <h4>Test Result:</h4>
          <div v-if="testResult.success" class="result-success">
            <el-alert type="success" :closable="false" show-icon>
              <template #title>
                Processing completed in {{ testResult.processingTime }} ms
              </template>
            </el-alert>
            <div class="result-details">
              <div class="detail-section">
                <strong>Input:</strong>
                <pre>{{ JSON.stringify(testResult.input, null, 2) }}</pre>
              </div>
              <div class="detail-section">
                <strong>Output:</strong>
                <pre>{{ JSON.stringify(testResult.output, null, 2) }}</pre>
              </div>
              <div v-if="testResult.transformationApplied" class="detail-section">
                <strong>Transformation Applied:</strong>
                <code>{{ selectedMapping?.transformation }}</code>
              </div>
            </div>
          </div>
          <div v-else class="result-error">
            <el-alert type="error" :closable="false" show-icon>
              <template #title>{{ testResult.error }}</template>
              <template #default>{{ testResult.details }}</template>
            </el-alert>
          </div>
        </div>
      </div>
    </el-dialog>

    <!-- Template Selector Dialog -->
    <el-dialog v-model="templateDialogVisible" title="Select Transformation Template" width="600px">
      <div class="template-selector">
        <div class="template-categories">
          <el-input placeholder="Search templates..." clearable style="margin-bottom: 16px">
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <div class="template-list">
            <div
                v-for="template in transformationTemplates"
                :key="template.id"
                class="template-item"
                @click="handleApplyTemplate(template)"
            >
              <div class="template-item-header">
                <span class="template-name">{{ template.name }}</span>
                <el-tag size="small">{{ template.category }}</el-tag>
              </div>
              <div class="template-expr">
                <code>{{ template.expression }}</code>
              </div>
            </div>
          </div>
        </div>
      </div>
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
  font-size: 20px;
  font-weight: 600;
  color: #e2e8f0;
  display: flex;
  justify-content: center;
  align-items: baseline;
  gap: 4px;
}

.loading-title {
  font-size: 20px;
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
  font-weight: 500;
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
.payload-mapping {
  padding: 20px;
  background-color: #f5f5f5;
  min-height: calc(100vh - 60px);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
}

.header-left h2 {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
}

.header-left p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.header-right {
  display: flex;
  gap: 12px;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  cursor: pointer;
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1a1a1a;
}

.stat-label {
  font-size: 14px;
  color: #8c8c8c;
  margin-top: 4px;
}

.mapping-tabs {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.toolbar-left {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.toolbar-right {
  display: flex;
  gap: 12px;
}

.mapping-name {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 4px;
}

.mapping-name .name {
  font-weight: 500;
}

.mapping-desc {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}

.field-mapping {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.field-mapping code {
  background: #f5f5f5;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
}

.field-mapping .source {
  color: #1890ff;
}

.field-mapping .target {
  color: #52c41a;
}

.arrow-icon {
  color: #999;
}

.protocol-badge {
  display: flex;
  align-items: center;
  gap: 4px;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

/* Templates */
.templates-container {
  padding: 16px 0;
}

.templates-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.templates-header h3 {
  margin: 0;
}

.templates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

.template-card {
  cursor: pointer;
  transition: all 0.3s ease;
}

.template-card:hover {
  transform: translateY(-2px);
}

.template-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.template-name {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
}

.template-expression {
  background: #f5f5f5;
  padding: 12px;
  border-radius: 6px;
  margin-bottom: 16px;
  overflow-x: auto;
}

.template-expression code {
  font-size: 12px;
  color: #d4380d;
}

.template-actions {
  display: flex;
  gap: 8px;
}

/* Rules */
.rules-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.rules-header h3 {
  margin: 0;
}

/* Analytics */
.analytics-container {
  padding: 16px 0;
}

.analytics-card {
  height: 100%;
}

/* Test Dialog */
.test-container {
  padding: 8px 0;
}

.test-input h4, .test-result h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
  font-weight: 600;
}

.result-success {
  margin-top: 16px;
}

.result-details {
  margin-top: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.detail-section {
  background: #f9f9f9;
  padding: 12px;
  border-radius: 8px;
}

.detail-section pre {
  margin: 8px 0 0 0;
  background: #f0f0f0;
  padding: 8px;
  border-radius: 4px;
  overflow-x: auto;
  font-size: 12px;
}

.detail-section code {
  display: block;
  margin-top: 8px;
  background: #f0f0f0;
  padding: 8px;
  border-radius: 4px;
  font-size: 12px;
}

.result-error {
  margin-top: 16px;
}

.small-code {
  font-size: 11px;
  background: #f5f5f5;
  padding: 2px 4px;
  border-radius: 3px;
}

/* Template Selector */
.template-selector {
  max-height: 500px;
  overflow-y: auto;
}

.template-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.template-item {
  padding: 12px;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.template-item:hover {
  border-color: #1890ff;
  background: #f0f7ff;
}

.template-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.template-item-header .template-name {
  font-weight: 500;
}

.template-expr code {
  font-size: 11px;
  color: #d4380d;
}

.transformation-input {
  width: 100%;
}

/* Responsive */
@media (max-width: 1200px) {
  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
  }

  .templates-grid {
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  }
}

@media (max-width: 768px) {
  .stats-cards {
    grid-template-columns: 1fr;
  }

  .page-header {
    flex-direction: column;
  }

  .header-right {
    margin-top: 16px;
    width: 100%;
    flex-wrap: wrap;
  }

  .toolbar {
    flex-direction: column;
    gap: 12px;
  }

  .toolbar-left {
    width: 100%;
  }

  .toolbar-right {
    width: 100%;
  }

  .templates-grid {
    grid-template-columns: 1fr;
  }

  .field-mapping {
    flex-wrap: wrap;
  }
}

:deep(.el-card__header) {
  font-weight: 600;
  background-color: #fafafa;
  border-bottom: 1px solid #f0f0f0;
}

:deep(.el-tabs__header) {
  margin-bottom: 20px;
}

:deep(.el-table) {
  font-size: 13px;
}
</style>