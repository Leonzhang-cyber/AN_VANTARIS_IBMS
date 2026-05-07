<template>
  <div class="page">
    <h3 class="page-title">HVAC Energy Analysis</h3>

    <!-- 能耗总览卡片 -->
    <el-row :gutter="20" style="margin-bottom: 20px">
      <el-col :span="6">
        <el-card class="card blue">
          <div class="label">Current HVAC Power</div>
          <div class="value">48.6 kW</div>
          <div class="unit">Real-time Power</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="card green">
          <div class="label">Today HVAC Consumption</div>
          <div class="value">982.4 kWh</div>
          <div class="unit">↓ 12.2% WoW</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="card orange">
          <div class="label">Monthly HVAC Cost</div>
          <div class="value">$ 1,486.2</div>
          <div class="unit">Estimated</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="card purple">
          <div class="label">Energy Saving Rate</div>
          <div class="value">18.7 %</div>
          <div class="unit">Intelligent Control</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 负荷分布 & 分时用电 -->
    <el-row :gutter="20" style="margin-bottom: 20px">
      <el-col :span="12">
        <el-card>
          <div class="card-title">HVAC Load Distribution</div>
          <div ref="chartPie" style="width: 100%; height: 300px"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <div class="card-title">24h Hourly Power Consumption</div>
          <div ref="chartLine" style="width: 100%; height: 300px"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 周用电柱状图 -->
    <el-card style="margin-bottom: 20px">
      <div class="card-title">Weekly HVAC Energy Consumption</div>
      <div ref="chartBar" style="width: 100%; height: 320px"></div>
    </el-card>

    <!-- 设备能耗排行 -->
    <el-card>
      <div class="card-title">Top 6 HVAC Equipment Power Consumption</div>
      <el-table :data="equipData" border style="width: 100%">
        <el-table-column prop="name" label="Equipment"></el-table-column>
        <el-table-column prop="power" label="Real-time Power (kW)"></el-table-column>
        <el-table-column prop="today" label="Today Consumption (kWh)"></el-table-column>
        <el-table-column prop="status" label="Status">
          <template #default="scope">
            <el-tag :type="scope.row.status === 'Running' ? 'success' : 'info'">
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'

const chartBar = ref(null)
const chartLine = ref(null)
const chartPie = ref(null)

let bar, line, pie

// 设备能耗数据（真实HVAC设备）
const equipData = ref([
  { name: 'AHU-01', power: 15.2, today: 328.4, status: 'Running' },
  { name: 'AHU-02', power: 14.8, today: 310.6, status: 'Running' },
  { name: 'CHW Pump-01', power: 8.6, today: 172.9, status: 'Running' },
  { name: 'CHW Pump-02', power: 4.2, today: 89.2, status: 'Standby' },
  { name: 'Supply Fan', power: 3.8, today: 68.4, status: 'Running' },
  { name: 'Exhaust Fan', power: 2.0, today: 32.9, status: 'Running' },
])

onMounted(() => {
  bar = echarts.init(chartBar.value)
  line = echarts.init(chartLine.value)
  pie = echarts.init(chartPie.value)

  // 周能耗柱状图
  bar.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'] },
    yAxis: { type: 'value', name: 'kWh' },
    series: [{
      data: [986, 1042, 1128, 976, 1064, 726, 692],
      type: 'bar',
      itemStyle: { color: '#1979C9' }
    }]
  })

  // 24小时用电曲线
  line.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: {
      data: Array.from({ length: 24 }, (_, i) => `${i}:00`),
      axisLabel: { interval: 2 }
    },
    yAxis: { type: 'value', name: 'kW' },
    series: [{
      data: [42, 40, 38, 36, 44, 52, 68, 76, 78, 74, 66, 58,
        54, 56, 62, 68, 72, 70, 62, 56, 50, 48, 46, 44
      ],
      type: 'line',
      smooth: true,
      itemStyle: { color: '#00B42A' }
    }]
  })

  // 负荷分布饼图
  pie.setOption({
    tooltip: { trigger: 'item' },
    legend: { orient: 'vertical', left: 'left' },
    series: [{
      name: 'Load',
      type: 'pie',
      radius: ['40%', '70%'],
      data: [
        { value: 48, name: 'AHU' },
        { value: 26, name: 'Chilled Water Pump' },
        { value: 16, name: 'Supply Fan' },
        { value: 10, name: 'Exhaust Fan' }
      ]
    }]
  })
})

onUnmounted(() => {
  bar?.dispose()
  line?.dispose()
  pie?.dispose()
})
</script>

<style scoped>
.page {
  padding: 12px;
}

.page-title {
  font-size: 19px;
  font-weight: 600;
  margin-bottom: 20px;
}

.card {
  padding: 22px;
  border-radius: 12px;
  color: #fff;
}

.blue {
  background: #1979C9;
}

.green {
  background: #00B42A;
}

.orange {
  background: #FF7D00;
}

.purple {
  background: #722ED1;
}

.label {
  font-size: 14px;
  opacity: .9;
  margin-bottom: 6px;
}

.value {
  font-size: 26px;
  font-weight: bold;
  margin-bottom: 4px;
}

.unit {
  font-size: 12px;
  opacity: 0.8;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 15px;
}
</style>