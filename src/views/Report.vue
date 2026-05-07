<template>
  <div class="page">
    <h3 class="page-title">Data Reports</h3>

    <!-- 纯 Element Plus 卡片布局 → 美观、标准 -->
    <el-row :gutter="20" style="margin-bottom: 20px">
      <el-col :span="8">
        <el-card class="export-card">
          <div class="top">
            <div class="label">Device Status Report</div>
            <div class="sub-label">Equipment operation & status data</div>
          </div>
          <el-button type="primary" block @click="exportExcel('device')">
            <el-icon><Download /></el-icon> Export Excel
          </el-button>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="export-card green">
          <div class="top">
            <div class="label">Energy Consumption Report</div>
            <div class="sub-label">Power & load statistics</div>
          </div>
          <el-button type="success" block @click="exportExcel('energy')">
            <el-icon><Download /></el-icon> Export Excel
          </el-button>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="export-card orange">
          <div class="top">
            <div class="label">Alarm & Event Report</div>
            <div class="sub-label">Alarm records & event logs</div>
          </div>
          <el-button type="warning" block @click="exportExcel('alarm')">
            <el-icon><Download /></el-icon> Export Excel
          </el-button>
        </el-card>
      </el-col>
    </el-row>

    <!-- 筛选栏 -->
    <el-card style="margin-bottom: 20px">
      <div class="card-title">Report Filter</div>
      <el-form :inline="true" :model="filter">
        <el-form-item label="Report Type">
          <el-select v-model="filter.type" placeholder="Select">
            <el-option label="Device Status" value="device" />
            <el-option label="Energy Consumption" value="energy" />
            <el-option label="Alarm Event" value="alarm" />
          </el-select>
        </el-form-item>
        <el-form-item label="Time Range">
          <el-date-picker
              v-model="filter.date"
              type="month"
              placeholder="Select month"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="search">Search</el-button>
          <el-button @click="reset">Reset</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 图表 -->
    <el-card style="margin-bottom: 20px">
      <div class="card-title">Monthly Report Trend</div>
      <div ref="chart" style="width:100%;height:300px"></div>
    </el-card>

    <!-- 数据表格 -->
    <el-card>
      <div class="card-title">Report Data List</div>
      <el-table :data="tableData" border stripe style="width:100%">
        <el-table-column label="Date" prop="date" />
        <el-table-column label="System" prop="system" />
        <el-table-column label="Device" prop="device" />
        <el-table-column label="Data Item" prop="item" />
        <el-table-column label="Value" prop="value" />
        <el-table-column label="Unit" prop="unit" />
        <el-table-column label="Status" align="center">
          <template #default="scope">
            <el-tag :type="scope.row.status === 'Normal' ? 'success' : 'warning'">
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="50"
          layout="total, sizes, prev, pager, next, jumper"
          style="margin-top:15px; display:flex; justify-content:flex-end; width:100%;"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'

const chart = ref(null)
let myChart

const currentPage = ref(1)
const pageSize = ref(10)

const filter = ref({
  type: 'device',
  date: ''
})

const tableData = ref([
  { date: '2025-06-01', system: 'HVAC', device: 'AHU-01', item: 'Running Time', value: '22.5', unit: 'h', status: 'Normal' },
  { date: '2025-06-01', system: 'HVAC', device: 'Water Pump-01', item: 'Power Consumption', value: '48.6', unit: 'kWh', status: 'Normal' },
  { date: '2025-06-01', system: 'Power', device: 'Power Meter', item: 'Total Consumption', value: '1280.4', unit: 'kWh', status: 'Normal' },
  { date: '2025-06-01', system: 'Lighting', device: 'Floor-1 Panel', item: 'On Time', value: '16.8', unit: 'h', status: 'Normal' },
  { date: '2025-06-02', system: 'HVAC', device: 'AHU-02', item: 'Running Time', value: '21.9', unit: 'h', status: 'Normal' },
  { date: '2025-06-02', system: 'HVAC', device: 'Water Pump-02', item: 'Power Consumption', value: '42.3', unit: 'kWh', status: 'Abnormal' },
  { date: '2025-06-02', system: 'Power', device: 'Transformer', item: 'Load Rate', value: '68.2', unit: '%', status: 'Normal' },
  { date: '2025-06-02', system: 'Security', device: 'Camera-01', item: 'Online Duration', value: '24.0', unit: 'h', status: 'Normal' },
  { date: '2025-06-03', system: 'HVAC', device: 'AHU-01', item: 'Filter Usage', value: '76.4', unit: '%', status: 'Normal' },
  { date: '2025-06-03', system: 'Water', device: 'Chilled Valve', item: 'Open Duration', value: '12.3', unit: 'h', status: 'Normal' },
])

const search = () => {
  ElMessage.success('Filter applied successfully')
}
const reset = () => {
  filter.value.type = 'device'
  filter.value.date = ''
  ElMessage.info('Filter reset')
}

const exportExcel = (type) => {
  const name = {
    device: 'Device_Status_Report',
    energy: 'Energy_Consumption_Report',
    alarm: 'Alarm_Event_Report'
  }[type] || 'Report'

  const blob = new Blob(
      [`Report Data\nGenerated Time: ${new Date().toLocaleString()}`],
      { type: 'application/vnd.ms-excel' }
  )
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${name}_${new Date().getTime()}.xlsx`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('Exported successfully')
}

onMounted(() => {
  myChart = echarts.init(chart.value)
  myChart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { data: ['1st', '2nd', '3rd', '4th', '5th', '6th', '7th'] },
    yAxis: { type: 'value' },
    series: [
      { data: [1280, 1340, 1290, 1380, 1420, 1350, 1390], type: 'line', name: 'Energy' },
      { data: [86, 92, 88, 94, 96, 90, 95], type: 'bar', name: 'Device', itemStyle: { color: '#1979C9' } }
    ]
  })
})

onUnmounted(() => {
  myChart?.dispose()
})
</script>

<style scoped>
.page { padding: 12px; }
.page-title { font-size: 19px; font-weight: 600; margin-bottom: 20px; }
.card-title { font-size: 16px; font-weight: 600; margin-bottom: 15px; }

/* 导出卡片样式 */
.export-card {
  background: #1979C9;
  color: #fff;
  border-radius: 12px;
  padding: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}
.export-card.green { background: #00B42A; }
.export-card.orange { background: #FF7D00; }

.export-card .top {
  margin-bottom: 16px;
}
.export-card .label {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 6px;
}
.export-card .sub-label {
  font-size: 12px;
  opacity: 0.85;
}
</style>