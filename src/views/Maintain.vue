<template>
  <div class="page">
    <h3 class="page-title">Maintenance Management</h3>

    <!-- 统计卡片 -->
    <el-row :gutter="20" style="margin-bottom: 20px">
      <el-col :span="6">
        <el-card class="card blue">
          <div class="label">Total Orders</div>
          <div class="value">86</div>
          <div class="sub">This Month</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="card green">
          <div class="label">Completed</div>
          <div class="value">64</div>
          <div class="sub">74.4% Rate</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="card orange">
          <div class="label">Processing</div>
          <div class="value">18</div>
          <div class="sub">In Service</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="card gray">
          <div class="label">Pending</div>
          <div class="value">4</div>
          <div class="sub">Wait Assign</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表 -->
    <el-row :gutter="20" style="margin-bottom: 20px">
      <el-col :span="12">
        <el-card>
          <div class="card-title">Maintenance Type</div>
          <div ref="chartPie" style="width:100%;height:280px"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <div class="card-title">Monthly Trend</div>
          <div ref="chartBar" style="width:100%;height:280px"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 工单列表 -->
    <el-card>
      <div class="card-title">Work Order List</div>
      <el-table
          :data="paginatedList"
          border
          stripe
          style="width:100%;margin-top:10px"
      >
        <el-table-column label="Order ID" prop="id" />
        <el-table-column label="Device" prop="device" />
        <el-table-column label="Content" prop="content" min-width="220" />
        <el-table-column label="Engineer" prop="engineer" />
        <el-table-column label="Create Time" prop="time" />
        <el-table-column label="Status" align="center">
          <template #default="scope">
            <el-tag
                :type="
                    scope.row.status === 'Completed' ? 'success' :
                    scope.row.status === 'Processing' ? 'warning' : 'info'
                "
            >
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页（靠右） -->
      <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="list.length"
          layout="total, sizes, prev, pager, next, jumper"
          style="margin-top:15px;display:flex;justify-content:flex-end;width:100%;"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import * as echarts from 'echarts'

const chartPie = ref(null)
const chartBar = ref(null)
let pie, bar

const currentPage = ref(1)
const pageSize = ref(10)

// 真实业务数据 总数 86 = 64+18+4
const list = ref([
  { id: 'MNT-20250601-001', device: 'AHU-01', content: 'Filter cleaning and replacement', engineer: 'Zhang San', time: '2025-06-01 08:30', status: 'Completed' },
  { id: 'MNT-20250601-002', device: 'Water Pump-01', content: 'Leakage inspection and maintenance', engineer: 'Li Si', time: '2025-06-01 09:15', status: 'Processing' },
  { id: 'MNT-20250601-003', device: 'Precision AC', content: 'Temperature calibration', engineer: 'Wang Wu', time: '2025-06-01 10:00', status: 'Pending' },
  { id: 'MNT-20250601-004', device: 'Lighting Panel', content: 'Circuit inspection', engineer: 'Zhao Liu', time: '2025-06-01 11:20', status: 'Completed' },
  { id: 'MNT-20250601-005', device: 'Ventilation Fan', content: 'Belt tension adjustment', engineer: 'Sun Qi', time: '2025-06-01 14:10', status: 'Processing' },
  { id: 'MNT-20250601-006', device: 'Chilled Water Valve', content: 'Action performance test', engineer: 'Zhou Ba', time: '2025-06-01 15:30', status: 'Completed' },
  { id: 'MNT-20250601-007', device: 'Power Meter', content: 'Meter accuracy calibration', engineer: 'Wu Jiu', time: '2025-06-01 16:20', status: 'Completed' },
  { id: 'MNT-20250601-008', device: 'Access Control', content: 'Card reader replacement', engineer: 'Zheng Shi', time: '2025-06-01 17:10', status: 'Processing' },
  { id: 'MNT-20250602-001', device: 'Exhaust Fan', content: 'Lubrication and maintenance', engineer: 'Zhang San', time: '2025-06-02 08:45', status: 'Completed' },
  { id: 'MNT-20250602-002', device: 'AHU-02', content: 'Coil cleaning', engineer: 'Li Si', time: '2025-06-02 10:20', status: 'Pending' },
  { id: 'MNT-20250602-003', device: 'Water Pump-02', content: 'Mechanical parts inspection', engineer: 'Wang Wu', time: '2025-06-02 13:30', status: 'Processing' },
  { id: 'MNT-20250602-004', device: 'Camera', content: 'Lens cleaning', engineer: 'Zhao Liu', time: '2025-06-02 15:15', status: 'Completed' },
  { id: 'MNT-20250602-005', device: 'Fire Alarm', content: 'System self-test', engineer: 'Sun Qi', time: '2025-06-02 16:40', status: 'Completed' },
])

const paginatedList = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return list.value.slice(start, start + pageSize.value)
})

onMounted(() => {
  pie = echarts.init(chartPie.value)
  bar = echarts.init(chartBar.value)

  // 修复 Maintenance Type 饼图
  pie.setOption({
    tooltip: { trigger: 'item' },
    legend: {
      orient: 'vertical',
      left: 'left',
      top: 'center'
    },
    series: [{
      name: 'Maintenance Type',
      type: 'pie',
      radius: ['40%', '70%'],
      data: [
        { value: 32, name: 'Cleaning' },
        { value: 24, name: 'Calibration' },
        { value: 18, name: 'Replacement' },
        { value: 12, name: 'Inspection' }
      ],
      label: {
        show: true,
        formatter: '{b}: {c}'
      }
    }]
  })

  // 月度趋势柱状图
  bar.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: 10, right: 10, top: 10, bottom: 10, containLabel: true },
    xAxis: { data: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'] },
    yAxis: { type: 'value' },
    series: [{
      data: [58, 65, 72, 79, 81, 86],
      type: 'bar',
      itemStyle: { color: '#1979C9' }
    }]
  })

  window.addEventListener('resize', () => {
    pie.resize()
    bar.resize()
  })
})

onUnmounted(() => {
  pie?.dispose()
  bar?.dispose()
})
</script>

<style scoped>
.page { padding: 12px; }
.page-title { font-size: 19px; font-weight: 600; margin-bottom: 20px; }
.card { padding: 22px; border-radius: 12px; color: #fff; }
.blue { background: #1979C9; }
.green { background: #00B42A; }
.orange { background: #FF7D00; }
.gray { background: #909399; }
.label { font-size: 14px; opacity: .9; margin-bottom: 6px; }
.value { font-size: 26px; font-weight: bold; margin-bottom: 4px; }
.sub { font-size: 12px; opacity: 0.8; }
.card-title { font-size: 16px; font-weight: 600; margin-bottom: 15px; }
</style>