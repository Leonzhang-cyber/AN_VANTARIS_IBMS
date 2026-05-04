<template>
  <div class="device-page">
    <h3 class="page-title">Device Management</h3>

    <el-row :gutter="20" style="margin-bottom:20px">
      <el-col :span="6">
        <el-card class="stat-card blue">
          <div class="label">Total Devices</div>
          <div class="value">246</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card green">
          <div class="label">Online</div>
          <div class="value">194</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card orange">
          <div class="label">Warning</div>
          <div class="value">20</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card gray">
          <div class="label">Offline</div>
          <div class="value">32</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 3D 数字孪生区域 -->
    <el-card style="margin-bottom:20px; padding:20px">
      <div class="card-title">Equipment 3D Digital Twin</div>
      <div class="twin-wrapper">
        <Device3DTwin />
        <Device3DTwin />
        <Device3DTwin />
      </div>
    </el-card>

    <el-card style="margin-bottom:20px">
      <div class="card-title">Device Type Distribution</div>
      <div ref="chartRef" style="width:100%;height:260px"></div>
    </el-card>

    <el-card>
      <div class="card-title">Device List</div>
      <el-table :data="deviceList" border stripe size="default" style="width:100%;margin-top:10px">
        <el-table-column label="Device ID" prop="id" />
        <el-table-column label="Device Name" prop="name" />
        <el-table-column label="Location" prop="location" />
        <el-table-column label="Type" prop="type" />
        <el-table-column label="Status" align="center">
          <template #default="scope">
            <el-tag :type="scope.row.status === 'Online' ? 'success' :
                           scope.row.status === 'Warning' ? 'warning' : 'danger'">
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Action" align="center">
          <el-button type="primary" size="small">Detail</el-button>
          <el-button type="warning" size="small">Control</el-button>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'
import Device3DTwin from '@/components/Device3DTwin.vue'

const chartRef = ref(null)

const deviceList = [
  { id: 'DEV-0001', name: 'Air Conditioner Unit', location: '1st Floor Lobby', type: 'HVAC', status: 'Online' },
  { id: 'DEV-0002', name: 'Lighting Control Panel', location: '2nd Floor Corridor', type: 'Lighting', status: 'Online' },
  { id: 'DEV-0003', name: 'Access Controller', location: 'Main Entrance', type: 'Security', status: 'Warning' },
  { id: 'DEV-0004', name: 'Water Pump System', location: 'Basement', type: 'Plumbing', status: 'Online' },
  { id: 'DEV-0005', name: 'Ventilation Fan', location: '3rd Floor', type: 'HVAC', status: 'Offline' },
  { id: 'DEV-0006', name: 'Power Meter', location: 'Electrical Room', type: 'Energy', status: 'Online' },
  { id: 'DEV-0007', name: 'Fire Alarm Panel', location: 'Security Room', type: 'Safety', status: 'Warning' },
]

onMounted(() => {
  const chart = echarts.init(chartRef.value)
  chart.setOption({
    tooltip: { trigger: 'item' },
    legend: { bottom: 0 },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      data: [
        { value: 86, name: 'HVAC' },
        { value: 62, name: 'Lighting' },
        { value: 45, name: 'Security' },
        { value: 31, name: 'Plumbing' },
        { value: 22, name: 'Energy' },
      ],
      color: ['#1979C9', '#00B42A', '#FF7D00', '#722ED1', '#F53F3F']
    }]
  })
})
</script>

<style scoped>
.device-page { padding: 12px; }
.page-title { font-size: 19px; font-weight: 600; margin-bottom: 20px; color: #1d2129; }
.stat-card { padding: 22px; border-radius: 12px; color: #fff; }
.stat-card.blue { background: #1979C9; }
.stat-card.green { background: #00B42A; }
.stat-card.orange { background: #FF7D00; }
.stat-card.gray { background: #909399; }
.label { font-size: 14px; opacity: 0.9; margin-bottom: 6px; }
.value { font-size: 26px; font-weight: bold; }
.card-title { font-size: 16px; font-weight: 600; margin-bottom: 15px; }

.twin-wrapper {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 20px;
}
</style>