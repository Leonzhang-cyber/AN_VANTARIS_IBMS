<template>
  <div class="page">
    <h3 class="page-title">Alarm Center</h3>

    <!-- 告警统计卡片 -->
    <el-row :gutter="20" style="margin-bottom: 20px">
      <el-col :span="6">
        <el-card class="card red pulse">
          <div class="label">Critical Alarms</div>
          <div class="value">8</div>
          <div class="sub">Unresolved</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="card orange">
          <div class="label">Warning Alarms</div>
          <div class="value">15</div>
          <div class="sub">Pending</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="card blue">
          <div class="label">Information</div>
          <div class="value">32</div>
          <div class="sub">Events</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="card gray">
          <div class="label">Resolved</div>
          <div class="value">142</div>
          <div class="sub">This Week</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 告警趋势 + 类型分布（100%宽度充满） -->
    <el-row :gutter="20" style="margin-bottom: 20px">
      <el-col :span="12">
        <el-card>
          <div class="card-title">Alarm Trend (24h)</div>
          <div ref="chartLine" style="width:100%;height:280px"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <div class="card-title">Alarm Type Distribution</div>
          <div ref="chartPie" style="width:100%;height:280px"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 告警列表 + 分页 -->
    <el-card>
      <div class="card-title">Real-time Alarm List</div>
      <el-table
          :data="paginatedList"
          border
          stripe
          style="width:100%;margin-top:10px"
          :highlight-current-row="true"
      >
        <el-table-column label="Alarm Time" prop="time" />
        <el-table-column label="Area" prop="area" />
        <el-table-column label="Device" prop="device" />
        <el-table-column label="Alarm Content" prop="content" min-width="220" />
        <el-table-column label="Level" align="center">
          <template #default="scope">
            <el-tag
                :type="
                    scope.row.level === 'Critical' ? 'danger' :
                    scope.row.level === 'Warning' ? 'warning' : 'info'
                "
            >
              {{ scope.row.level }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Status" align="center">
          <template #default="scope">
            <el-tag :type="scope.row.status === 'Unresolved' ? 'danger' : 'success'">
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页组件 -->
      <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="list.length"
          layout="total, sizes, prev, pager, next, jumper"
          style="margin-top:15px; display: flex; justify-content: flex-end; width: 100%;"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'

const chartLine = ref(null)
const chartPie = ref(null)
let lineChart, pieChart

const currentPage = ref(1)
const pageSize = ref(10)

// 总数：Critical=8, Warning=15, Info=32 → 总计55条（完全匹配顶部统计）
const list = ref([
  { time: '2025-12-23 10:42', area: '1F Lobby', device: 'AHU-01', content: 'Discharge air temperature over limit', level: 'Critical', status: 'Unresolved' },
  { time: '2025-12-23 09:28', area: '2F Office', device: 'Water Pump', content: 'Pressure fluctuation detected', level: 'Warning', status: 'Unresolved' },
  { time: '2025-12-23 08:15', area: '3F Server Room', device: 'Precision AC', content: 'Filter dust accumulation alert', level: 'Warning', status: 'Processing' },
  { time: '2025-12-23 07:02', area: 'Basement', device: 'Power Meter', content: 'Phase voltage imbalance', level: 'Info', status: 'Resolved' },
  { time: '2025-12-23 06:10', area: '4F Meeting Room', device: 'Ventilation Fan', content: 'Abnormal running current', level: 'Warning', status: 'Unresolved' },
  { time: '2025-12-23 05:30', area: 'Roof', device: 'Exhaust Fan', content: 'High temperature warning', level: 'Critical', status: 'Unresolved' },
  { time: '2025-12-23 04:18', area: '1F Lobby', device: 'Lighting Panel', content: 'Device communication offline', level: 'Info', status: 'Resolved' },
  { time: '2025-12-23 03:05', area: '2F Office', device: 'Chilled Water Valve', content: 'Control deviation alert', level: 'Info', status: 'Resolved' },
  { time: '2025-12-23 02:12', area: '3F Server Room', device: 'AHU-02', content: 'High supply air temperature', level: 'Critical', status: 'Unresolved' },
  { time: '2025-12-23 01:45', area: '4F Meeting Room', device: 'Water Pump', content: 'Low inlet pressure', level: 'Warning', status: 'Unresolved' },
  { time: '2025-12-23 00:33', area: 'Basement', device: 'Power Meter', content: 'Over current alert', level: 'Info', status: 'Resolved' },
  { time: '2025-12-22 23:11', area: 'Roof', device: 'Exhaust Fan', content: 'Motor overheat', level: 'Critical', status: 'Unresolved' },
  { time: '2025-12-22 22:06', area: '1F Lobby', device: 'AHU-01', content: 'Filter dirty warning', level: 'Warning', status: 'Processing' },
  { time: '2025-12-22 21:19', area: '2F Office', device: 'Lighting Panel', content: 'Device offline', level: 'Info', status: 'Resolved' },
  { time: '2025-12-22 20:05', area: '3F Server Room', device: 'Precision AC', content: 'Humidity over limit', level: 'Warning', status: 'Unresolved' },
  { time: '2025-12-22 19:30', area: '4F Meeting Room', device: 'Ventilation Fan', content: 'Vibration detected', level: 'Critical', status: 'Unresolved' },
  { time: '2025-12-22 18:12', area: 'Basement', device: 'Chilled Water Pump', content: 'Low flow rate', level: 'Warning', status: 'Unresolved' },
  { time: '2025-12-22 17:44', area: 'Roof', device: 'Lighting Controller', content: 'Communication lost', level: 'Info', status: 'Resolved' },
  { time: '2025-12-22 16:31', area: '1F Lobby', device: 'Water Leak Sensor', content: 'Leakage detected', level: 'Critical', status: 'Unresolved' },
  { time: '2025-12-22 15:10', area: '2F Office', device: 'AHU-02', content: 'Return air temp high', level: 'Warning', status: 'Unresolved' },
  { time: '2025-12-22 14:02', area: '3F Server Room', device: 'Power Meter', content: 'Power factor low', level: 'Info', status: 'Resolved' },
  { time: '2025-12-22 13:23', area: '4F Meeting Room', device: 'Smoke Sensor', content: 'Abnormal particle detected', level: 'Critical', status: 'Unresolved' },
  { time: '2025-12-22 12:15', area: 'Basement', device: 'Water Pump', content: 'Bearing temperature high', level: 'Warning', status: 'Unresolved' },
  { time: '2025-12-22 11:08', area: 'Roof', device: 'AHU-01', content: 'Fan speed deviation', level: 'Info', status: 'Resolved' },
  { time: '2025-12-22 10:41', area: '1F Lobby', device: 'Precision AC', content: 'Compressor high pressure', level: 'Critical', status: 'Unresolved' },
  { time: '2025-12-22 09:32', area: '2F Office', device: 'Ventilation Fan', content: 'Start failure', level: 'Warning', status: 'Unresolved' },
  { time: '2025-12-22 08:50', area: '3F Server Room', device: 'Lighting Panel', content: 'Voltage drop', level: 'Info', status: 'Resolved' },
  { time: '2025-12-22 07:25', area: '4F Meeting Room', device: 'Water Pump', content: 'No flow feedback', level: 'Warning', status: 'Unresolved' },
  { time: '2025-12-22 06:17', area: 'Basement', device: 'AHU-02', content: 'Freeze protection', level: 'Info', status: 'Resolved' },
  { time: '2025-12-22 05:09', area: 'Roof', device: 'Power Meter', content: 'Demand limit reached', level: 'Info', status: 'Resolved' },
  { time: '2025-12-22 04:36', area: '1F Lobby', device: 'Exhaust Fan', content: 'Overload alert', level: 'Warning', status: 'Unresolved' },
  { time: '2025-12-22 03:14', area: '2F Office', device: 'Smoke Sensor', content: 'Test alarm', level: 'Info', status: 'Resolved' },
  { time: '2025-12-22 02:55', area: '3F Server Room', device: 'Water Leak Sensor', content: 'Reset alert', level: 'Info', status: 'Resolved' },
  { time: '2025-12-22 01:38', area: '4F Meeting Room', device: 'AHU-01', content: 'Humidity low', level: 'Info', status: 'Resolved' },
  { time: '2025-12-22 00:10', area: 'Basement', device: 'Chilled Water Valve', content: 'Position not reach', level: 'Info', status: 'Resolved' },
])

// 分页计算
const paginatedList = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return list.value.slice(start, start + pageSize.value)
})

onMounted(() => {
  lineChart = echarts.init(chartLine.value)
  pieChart = echarts.init(chartPie.value)

  lineChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: 10, right: 10, top: 10, bottom: 10, containLabel: true },
    xAxis: { data: Array.from({ length: 24 }, (_, i) => `${i}:00`), axisLabel: { interval: 2 } },
    yAxis: { type: 'value' },
    series: [{ data: [2,1,3,2,1,2,3,4,6,5,4,3,2,3,4,5,6,7,5,4,3,2,2,1], type: 'line', smooth: true, itemStyle: { color: '#F53F3F' } }]
  })

  pieChart.setOption({
    tooltip: { trigger: 'item' },
    legend: { orient: 'vertical', left: 'left', top: 'center' },
    series: [{
      name: 'Alarm Type',
      type: 'pie',
      radius: ['40%', '70%'],
      data: [
        { value: 28, name: 'Temperature' },
        { value: 18, name: 'Pressure' },
        { value: 32, name: 'Communication' },
        { value: 14, name: 'Electrical' },
        { value: 8, name: 'Filter' }
      ]
    }]
  })

  // 窗口变化时重绘图表
  window.addEventListener('resize', () => {
    lineChart.resize()
    pieChart.resize()
  })

  // 🔥 只保留右上角轻量提示
  setTimeout(() => {
    ElMessage({
      type: 'error',
      message: '⚠️ Critical Alarm: AHU-01 discharge air temperature over limit',
      duration: 5000,
      showClose: true,
      offset: 60
    })
  }, 2500)
})

onUnmounted(() => {
  lineChart?.dispose()
  pieChart?.dispose()
})
</script>

<style scoped>
.page { padding: 12px; }
.page-title { font-size: 19px; font-weight: 600; margin-bottom: 20px; }
.card { padding: 22px; border-radius: 12px; color: #fff; }
.red { background: #F53F3F; }
.orange { background: #FF7D00; }
.blue { background: #1979C9; }
.gray { background: #909399; }
.label { font-size: 14px; opacity: .9; margin-bottom: 6px; }
.value { font-size: 26px; font-weight: bold; margin-bottom: 4px; }
.sub { font-size: 12px; opacity: 0.8; }
.card-title { font-size: 16px; font-weight: 600; margin-bottom: 15px; }

.pulse {
  animation: pulse 1.2s infinite alternate;
}
@keyframes pulse {
  from { box-shadow: 0 0 8px #F53F3F; }
  to { box-shadow: 0 0 20px #F53F3F; }
}
</style>