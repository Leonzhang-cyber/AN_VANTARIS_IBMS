<template>
  <div class="page">
    <h3 class="page-title">Data Reports</h3>

    <el-row :gutter="20" style="margin-bottom:20px">
      <el-col :span="8"><el-card class="card blue"><div class="label">Device Report</div><div class="btn">Export</div></el-card></el-col>
      <el-col :span="8"><el-card class="card green"><div class="label">Energy Report</div><div class="btn">Export</div></el-card></el-col>
      <el-col :span="8"><el-card class="card orange"><div class="label">Alarm Report</div><div class="btn">Export</div></el-card></el-col>
    </el-row>

    <el-card>
      <div class="card-title">Monthly Report Overview</div>
      <div style="text-align:center;padding:40px;font-size:16px;color:#666">
        Monthly statistics including device status, energy consumption, alarm trends, and maintenance KPI.
      </div>
    </el-card>
  </div>
</template>

<script setup></script>

<style scoped>
.page{padding:12px}
.page-title{font-size:19px;font-weight:600;margin-bottom:20px}
.card{padding:22px;border-radius:12px;color:#fff;display:flex;justify-content:space-between;align-items:center}
.blue{background:#1979C9}
.green{background:#00B42A}
.orange{background:#FF7D00}
.label{font-size:16px;font-weight:500}
.btn{padding:6px 12px;background:#fff;color:#333;border-radius:6px;font-size:14px}
.card-title{font-size:16px;font-weight:600;margin-bottom:15px}
</style>