<template>
  <div class="page">
    <h3 class="page-title">Maintenance Management</h3>

    <el-row :gutter="20" style="margin-bottom:20px">
      <el-col :span="6"><el-card class="card blue"><div class="label">Total Orders</div><div class="value">86</div></el-card></el-col>
      <el-col :span="6"><el-card class="card green"><div class="label">Completed</div><div class="value">64</div></el-card></el-col>
      <el-col :span="6"><el-card class="card orange"><div class="label">Processing</div><div class="value">18</div></el-card></el-col>
      <el-col :span="6"><el-card class="card gray"><div class="label">Pending</div><div class="value">4</div></el-card></el-col>
    </el-row>

    <el-card>
      <div class="card-title">Work Order List</div>
      <el-table :data="list" border stripe style="margin-top:10px">
        <el-table-column label="Order ID" prop="id" />
        <el-table-column label="Device" prop="device" />
        <el-table-column label="Content" prop="content" />
        <el-table-column label="Status" prop="status" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
const list = [
  { id: 'MNT-001', device: 'Access Control', content: 'Battery replacement', status: 'Completed' },
  { id: 'MNT-002', device: 'Air Conditioner', content: 'Clean filter', status: 'Processing' },
  { id: 'MNT-003', device: 'Water Pump', content: 'Leakage inspection', status: 'Pending' },
  { id: 'MNT-004', device: 'Lighting System', content: 'Lamp replacement', status: 'Completed' },
]
</script>

<style scoped>
.page{padding:12px}
.page-title{font-size:19px;font-weight:600;margin-bottom:20px}
.card{padding:22px;border-radius:12px;color:#fff}
.blue{background:#1979C9}
.green{background:#00B42A}
.orange{background:#FF7D00}
.gray{background:#909399}
.label{font-size:14px;opacity:.9;margin-bottom:6px}
.value{font-size:26px;font-weight:bold}
.card-title{font-size:16px;font-weight:600;margin-bottom:15px}
</style>