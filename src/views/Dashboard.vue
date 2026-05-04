<template>
  <div class="dashboard">
    <h3 class="page-title">Dashboard Overview</h3>

    <el-row :gutter="20">
      <el-col :span="6" v-for="(item, i) in cards" :key="i">
        <el-card class="card-tech" :style="{ borderLeft: '4px solid ' + item.color }">
          <div class="card-top">
            <div class="label">{{ item.label }}</div>
            <div class="value">{{ item.value }}</div>
          </div>
          <div class="card-icon">
            <el-icon :color="item.color" size="36">
              <component :is="item.icon" />
            </el-icon>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card class="chart-card">
          <div class="chart-title">Energy Consumption Trend (24h)</div>
          <div ref="chart1" style="width: 100%; height: 300px"></div>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card class="chart-card">
          <div class="chart-title">Device Status Distribution</div>
          <div ref="chart2" style="width: 100%; height: 300px"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row style="margin-top:20px">
      <el-col :span="24">
        <el-card class="chart-card">
          <div class="chart-title">Real-Time Device Data</div>
          <el-table :data="deviceData" border stripe size="small">
            <el-table-column label="Device ID" prop="id" />
            <el-table-column label="Name" prop="name" />
            <el-table-column label="Type" prop="type" />
            <el-table-column label="Status" prop="status">
              <template #default="scope">
                <el-tag :type="scope.row.status === 'Online' ? 'success' : 'warning'">
                  {{ scope.row.status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="Value" prop="value" />
            <el-table-column label="Update Time" prop="time" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import * as echarts from 'echarts'

const chart1 = ref(null)
const chart2 = ref(null)

// 统计卡片（全英文）
const cards = [
  { label: 'Total Devices', value: '246', icon: 'Box', color: '#1979C9' },
  { label: 'Online Devices', value: '194', icon: 'Check', color: '#00B42A' },
  { label: 'Energy Usage', value: '6.88 kWh', icon: 'Lightning', color: '#FF7D00' },
  { label: 'Active Alarms', value: '12', icon: 'Warning', color: '#F53F3F' },
]

// 实时设备数据表
const deviceData = [
  { id: 'DEV-001', name: 'Air Conditioner', type: 'HVAC', status: 'Online', value: '24.5°C', time: '2025-12-22 18:00' },
  { id: 'DEV-002', name: 'Lighting Panel', type: 'Lighting', status: 'Online', value: 'On', time: '2025-12-22 18:00' },
  { id: 'DEV-003', name: 'Access Control', type: 'Security', status: 'Online', value: 'Normal', time: '2025-12-22 17:55' },
  { id: 'DEV-004', name: 'Water Pump', type: 'Plumbing', status: 'Warning', value: 'Abnormal', time: '2025-12-22 17:30' },
]

onMounted(() => {
  // 能耗趋势图
  const c1 = echarts.init(chart1.value)
  c1.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'category',
      data: ['00:00', '03:00', '06:00', '09:00', '12:00', '15:00', '18:00', '21:00'],
      axisLine: { lineStyle: { color: '#ccc' } }
    },
    yAxis: { type: 'value', axisLine: { lineStyle: { color: '#ccc' } } },
    series: [{
      data: [2.1, 2.4, 3.2, 5.6, 7.3, 6.1, 5.2, 4.1],
      type: 'line',
      smooth: true,
      lineStyle: { width: 3, color: '#1979C9' },
      itemStyle: { color: '#1979C9' },
      areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(25,121,201,0.3)' },
          { offset: 1, color: 'rgba(25,121,201,0.05)' }
        ]) }
    }]
  })

  // 设备状态饼图
  const c2 = echarts.init(chart2.value)
  c2.setOption({
    tooltip: { trigger: 'item' },
    legend: { orient: 'horizontal', bottom: 0 },
    series: [{
      type: 'pie',
      radius: ['45%', '70%'],
      data: [
        { value: 194, name: 'Online' },
        { value: 32, name: 'Offline' },
        { value: 20, name: 'Warning' },
      ],
      color: ['#00B42A', '#999', '#FF7D00']
    }]
  })
})
</script>

<style scoped>
.dashboard { padding: 12px; background: #F5F7FA; min-height: 100vh; }
.page-title { font-size: 19px; font-weight: 600; color: #1D2129; margin-bottom: 20px; }
.card-tech {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}
.label { font-size: 14px; color: #666; margin-bottom: 6px; }
.value { font-size: 28px; font-weight: bold; color: #111; }
.chart-card { padding: 22px; background: #fff; border-radius: 12px; }
.chart-title { font-size: 16px; font-weight: 600; color: #333; margin-bottom: 18px; }
</style>