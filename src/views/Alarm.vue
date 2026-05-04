<template>
  <div class="page">
    <h3 class="page-title">Alarm Center</h3>

    <el-row :gutter="20" style="margin-bottom:20px">
      <el-col :span="6"><el-card class="card red"><div class="label">Critical</div><div class="value">8</div></el-card></el-col>
      <el-col :span="6"><el-card class="card orange"><div class="label">Warning</div><div class="value">15</div></el-card></el-col>
      <el-col :span="6"><el-card class="card blue"><div class="label">Info</div><div class="value">32</div></el-card></el-col>
      <el-col :span="6"><el-card class="card gray"><div class="label">Resolved</div><div class="value">142</div></el-card></el-col>
    </el-row>

    <el-card>
      <div class="card-title">Alarm List</div>
      <el-table :data="list" border stripe style="margin-top:10px">
        <el-table-column label="Time" prop="time" />
        <el-table-column label="Device" prop="device" />
        <el-table-column label="Content" prop="content" />
        <el-table-column label="Level" align="center">
          <template #default="scope">
            <el-tag :type="scope.row.level === 'Critical' ? 'danger' : scope.row.level === 'Warning' ? 'warning' : 'info'">
              {{ scope.row.level }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
const list = [
  { time: '2025-12-22 18:00', device: 'Air Conditioner', content: 'Overheating alert', level: 'Critical' },
  { time: '2025-12-22 17:30', device: 'Water Pump', content: 'Abnormal pressure', level: 'Warning' },
  { time: '2025-12-22 16:15', device: 'Lighting Panel', content: 'Offline', level: 'Warning' },
  { time: '2025-12-22 15:00', device: 'Power Meter', content: 'Power consumption high', level: 'Info' },
]
</script>

<style scoped>
.page{padding:12px}
.page-title{font-size:19px;font-weight:600;margin-bottom:20px}
.card{padding:22px;border-radius:12px;color:#fff}
.red{background:#F53F3F}
.orange{background:#FF7D00}
.blue{background:#1979C9}
.gray{background:#909399}
.label{font-size:14px;opacity:.9;margin-bottom:6px}
.value{font-size:26px;font-weight:bold}
.card-title{font-size:16px;font-weight:600;margin-bottom:15px}
</style>