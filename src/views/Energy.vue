<template>
  <div class="page">
    <h3 class="page-title">Energy Analysis</h3>

    <el-row :gutter="20" style="margin-bottom:20px">
      <el-col :span="6">
        <el-card class="card blue"><div class="label">Today Consumption</div><div class="value">6.88 kWh</div></el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="card green"><div class="label">Month Consumption</div><div class="value">186.4 kWh</div></el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="card orange"><div class="label">Cost</div><div class="value">$ 92.6</div></el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="card purple"><div class="label">Saving Rate</div><div class="value">12.5%</div></el-card>
      </el-col>
    </el-row>

    <el-card style="margin-bottom:20px">
      <div class="card-title">Weekly Energy Consumption</div>
      <div ref="chart" style="width:100%;height:320px"></div>
    </el-card>
  </div>
</template>

<script setup>
import { ref,onMounted } from 'vue'
import * as echarts from 'echarts'
const chart = ref(null)

onMounted(()=>{
  const c = echarts.init(chart.value)
  c.setOption({
    tooltip:{},
    xAxis:{data:['Mon','Tue','Wed','Thu','Fri','Sat','Sun']},
    yAxis:{type:'value'},
    series:[{
      data:[3.2,4.1,5.6,3.9,6.2,2.8,4.5],
      type:'bar',
      itemStyle:{color:'#1979C9'}
    }]
  })
})
</script>

<style scoped>
.page{padding:12px}
.page-title{font-size:19px;font-weight:600;margin-bottom:20px}
.card{padding:22px;border-radius:12px;color:#fff}
.blue{background:#1979C9}
.green{background:#00B42A}
.orange{background:#FF7D00}
.purple{background:#722ED1}
.label{font-size:14px;opacity:.9;margin-bottom:6px}
.value{font-size:26px;font-weight:bold}
.card-title{font-size:16px;font-weight:600;margin-bottom:15px}
</style>