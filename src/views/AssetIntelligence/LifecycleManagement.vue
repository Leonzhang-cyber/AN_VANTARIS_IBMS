<template>
  <!-- Fixed Original Loading Animation Keep -->
  <div v-if="!isLoaded" class="loading-container">
    <div class="loading-overlay">
      <div class="loading-content">
        <div class="loading-spinner">
          <div class="spinner-ring"></div>
          <div class="spinner-ring"></div>
          <div class="spinner-ring"></div>
        </div>
        <div class="loading-text">
          <span class="loading-title">Loading</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">IBMS Asset Lifecycle Management Module</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Page Content -->
  <div v-else class="lifecycle-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">Asset Lifecycle Management</h1>
        <span class="page-desc">Full lifecycle tracking: Procurement → Deployment → Operation → Maintenance → Disposal</span>
      </div>
      <div class="header-action">
        <el-button type="primary" @click="openAdd">
          <el-icon><Plus /></el-icon> New Asset
        </el-button>
        <el-button @click="refreshData" :loading="refreshLoading">
          <el-icon><Refresh /></el-icon> Refresh
        </el-button>
        <el-button @click="exportReport">
          <el-icon><Download /></el-icon> Export Report
        </el-button>
      </div>
    </div>

    <!-- Lifecycle Stage Stat Cards -->
    <div class="stat-grid">
      <div class="stat-card" v-for="item in statList" :key="item.key" :class="item.class">
        <div class="card-icon"><el-icon :size="24"><component :is="item.icon"/></el-icon></div>
        <div class="card-info">
          <div class="stat-num">{{ item.value }}</div>
          <div class="stat-name">{{ item.label }}</div>
        </div>
      </div>
    </div>

    <!-- Dual Chart Area -->
    <div class="chart-row">
      <div class="chart-card">
        <div class="chart-title">Asset Distribution By Lifecycle Stage</div>
        <div ref="pieRef" class="ech-container"></div>
      </div>
      <div class="chart-card">
        <div class="chart-title">Monthly Asset In/Out Trend</div>
        <div ref="lineRef" class="ech-container"></div>
      </div>
    </div>

    <!-- Filter Bar -->
    <div class="filter-wrap">
      <div class="filter-left">
        <el-input v-model="searchKey" placeholder="Search Asset Name / SN Code" clearable prefix-icon="Search" style="width:250px"/>
        <el-select v-model="stageFilter" placeholder="Lifecycle Stage" clearable style="width:180px">
          <el-option label="Procurement" value="procurement"/>
          <el-option label="Deployment" value="deployment"/>
          <el-option label="Operation" value="operation"/>
          <el-option label="Maintenance" value="maintenance"/>
          <el-option label="Disposal" value="disposal"/>
        </el-select>
        <el-select v-model="catFilter" placeholder="Asset Category" clearable style="180px">
          <el-option v-for="cat in categoryArr" :key="cat" :label="cat" :value="cat"/>
        </el-select>
      </div>
      <el-button @click="resetFilter">Reset All</el-button>
    </div>

    <!-- Asset Table -->
    <div class="table-box">
      <el-table :data="pageList" border stripe>
        <el-table-column label="Asset SN" prop="sn" width="110"/>
        <el-table-column label="Asset Name" prop="name" min-width="160"/>
        <el-table-column label="Category" prop="category" width="140"/>
        <el-table-column label="Lifecycle Stage" prop="stage" width="150">
          <template #default="{row}">
            <el-tag :type="getStageTag(row.stage)">{{ getStageName(row.stage) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Purchase Date" prop="buyDate" width="120"/>
        <el-table-column label="Useful Life(Yr)" prop="lifeYear" width="130"/>
        <el-table-column label="Remaining Life(Yr)" prop="remainLife" width="130"/>
        <el-table-column label="Cost($)" prop="cost" width="120"/>
        <el-table-column label="Operation" width="150" fixed="right">
          <template #default="{row}">
            <el-button text type="primary" @click="openEdit(row)">Edit</el-button>
            <el-button text type="danger" @click="delAsset(row)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagi-wrap" v-if="total>0">
        <el-pagination v-model:current-page="currentPage" v-model:page-size="pageSize" :total="total" :page-sizes="[8,12,20]" background layout="total,sizes,prev,pager,next"/>
      </div>
    </div>

    <!-- Add/Edit Dialog -->
    <el-dialog v-model="dialogVis" :title="dialogTitle" width="720">
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="140">
        <el-row :gutter="18">
          <el-col :span="12">
            <el-form-item label="Asset Name" prop="name">
              <el-input v-model="formData.name"/>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Asset Category" prop="category">
              <el-select v-model="formData.category" style="width:100%">
                <el-option v-for="c in categoryArr" :key="c" :label="c" :value="c"/>
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="18">
          <el-col :span="12">
            <el-form-item label="Lifecycle Stage" prop="stage">
              <el-select v-model="formData.stage" style="width:100%">
                <el-option label="Procurement" value="procurement"/>
                <el-option label="Deployment" value="deployment"/>
                <el-option label="Operation"/>
                <el-option label="Maintenance" value="maintenance"/>
                <el-option label="Disposal" value="disposal"/>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Purchase Date" prop="buyDate">
              <el-date-picker v-model="formData.buyDate" type="date" value-format="YYYY-MM-DD" style="width:100%"/>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="18">
          <el-col :span="12">
            <el-form-item label="Expected Life(Yr)" prop="lifeYear">
              <el-input-number v-model="formData.lifeYear" :min="1" :max="30" style="width:100"/>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Purchase Cost($)" prop="cost">
              <el-input-number v-model="formData.cost" :min="0" :step="10" style="width:100"/>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="Remark">
          <el-input v-model="formData.remark" type="textarea" :rows="3"/>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVis=false">Cancel</el-button>
        <el-button type="primary" @click="saveForm">Save</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import {ref,computed,onMounted,nextTick,onBeforeUnmount,watch} from 'vue'
import {ElMessage,ElMessageBox} from 'element-plus'
import * as echarts from 'echarts'
import {Plus,Refresh,Download,Search,Document,Box,Setting,Delete,Wallet} from '@element-plus/icons-vue'

// =========== Fixed Original Loading Code Unchanged ===========
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const loadingMessages = [
  'Preparing...',
  'Loading asset lifecycle data...',
  'Calculate lifecycle stats...',
  'Almost ready...'
]

onMounted(() => {
  let messageIndex = 0
  const messageInterval = setInterval(() => {
    if (messageIndex < loadingMessages.length - 1) {
      messageIndex++
      loadingMessage.value = loadingMessages[messageIndex]
    }
  }, 400)

  const progressInterval = setInterval(() => {
    if (loadingProgress.value < 100) {
      loadingProgress.value += Math.random() * 15 + 5
      if (loadingProgress.value > 100) loadingProgress.value = 100
    }
  }, 200)

  setTimeout(() => {
    clearInterval(messageInterval)
    clearInterval(progressInterval)
    loadingProgress.value = 100
    loadingMessage.value = 'Ready!'
    setTimeout(() => {
      isLoaded.value = true
      nextTick(()=>setTimeout(initAllChart,120))
    }, 400)
  }, 2000)

  window.addEventListener('resize',resizeChart)
})

// Page Base Var
const refreshLoading = ref(false)
const dialogVis = ref(false)
const dialogTitle = ref('Create New Asset')
const formRef = ref()
const pieRef = ref<HTMLElement|null>(null)
const lineRef = ref<HTMLElement|null>(null)
let pieIns:echarts.ECharts|null=null
let lineIns:echarts.ECharts|null=null

// Filter Var
const searchKey = ref('')
const stageFilter = ref('')
const catFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(8)

// Mock Lifecycle Asset Data
const originAsset = ref([
  {sn:'AST-LC001',name:'Main UPS Unit',category:'Power System',stage:'operation',buyDate:'2022-03-12',lifeYear:10,remainLife:7,cost:12500,remark:'Core backup power'},
  {sn:'AST-LC002',name:'Chiller A-01',category:'HVAC',stage:'operation',buyDate:'2021-09-22',lifeYear:15,remainLife:10,cost:28600,remark:'Central cooling'},
  {sn:'AST-LC003',name:'Emergency Gen',category:'Power System',stage:'maintenance',buyDate:'2020-05-18',lifeYear:12,remainLife:5,cost:35200,remark:'Annual overhaul needed'},
  {sn:'AST-LC004',name:'Fire Pump',category:'Fire Protection',stage:'procurement',buyDate:'2025-01-08',lifeYear:8,remainLife:8,cost:8900,remark:'New purchase pending install'},
  {sn:'AST-LC005',name:'Basement Fan',category:'HVAC',stage:'disposal',buyDate:'2015-04-11',lifeYear:8,remainLife:0,cost:2300,remark:'End of service life'},
  {sn:'AST-LC006',name:'ATS Switch',category:'Power System',stage:'deployment',buyDate:'2025-02-20',lifeYear:9,remainLife:9,cost:7800,remark:'New installed Q2'},
  {sn:'AST-LC007',name:'CRAC Cabinet',category:'HVAC',stage:'operation',buyDate:'2023-06-05',lifeYear:12,remainLife:10,cost:9200,remark:'ID room aircon'},
  {sn:'AST-LC008',name:'Lighting Panel',category:'Low Voltage',stage:'maintenance',buyDate:'2019-11-30',lifeYear:10,remainLife:4,cost:3600,remark:'Circuit inspection required'},
])

// Category List
const categoryArr = computed(()=>[...new Set(originAsset.value.map(item=>item.category))])

// Filter Compute
const filterList = computed(()=>{
  let arr = [...originAsset.value]
  if(searchKey.value){
    const kw = searchKey.toLowerCase()
    arr = arr.filter(i=>i.name.toLowerCase().includes(kw)||i.sn.toLowerCase().includes(kw))
  }
  if(stageFilter.value) arr = arr.filter(i=>i.stage === stageFilter.value)
  if(catFilter.value) arr = arr.filter(i=>i.category === catFilter.value)
  return arr
})
const total = computed(()=>filterList.value.length)
const pageList = computed(()=>{
  const s = (currentPage.value-1)*pageSize.value
  return filterList.value.slice(s,s+pageSize.value)
})

// Stat Card
const statList = computed(()=>{
  const pro = originAsset.value.filter(i=>i.stage==='procurement').length
  const dep = originAsset.value.filter(i=>i.stage==='deployment').length
  const opt = originAsset.value.filter(i=>i.stage==='operation').length
  const main = originAsset.value.filter(i=>i.stage==='maintenance').length
  const dis = originAsset.value.filter(i=>i.stage==='disposal').length
  return [
    {key:'pro',label:'Procurement',value:pro,icon:Wallet,class:'blue'},
    {key:'dep',label:'Deployment',value:dep,icon:Box,class:'green'},
    {key:'opt',label:'In Operation',value:opt,icon:Document,class:'primary'},
    {key:'main',label:'Maintenance',value:main,icon:Setting,class:'orange'},
    {key:'dis',label:'Disposed',value:dis,icon:Delete,class:'red'},
  ]
})

// Form Init
const formData = ref({
  sn:'',name:'',category:'',stage:'procurement',buyDate:'',lifeYear:5,remainLife:0,cost:0,remark:''
})
const formRules = {
  name:[{required:true,message:'Asset name required',trigger:'blur'}],
  category:[{required:true,message:'Select category',trigger:'change'}],
  stage:[{required:true,message:'Select lifecycle stage',trigger:'change'}],
  buyDate:[{required:true,message:'Select purchase date',trigger:'change'}]
}

// Stage Helper
const getStageTag = (s:string)=>{
  const map:Record<string,string> = {procurement:'info',deployment:'primary',operation:'success',maintenance:'warning',disposal:'danger'}
  return map[s]||''
}
const getStageName = (s:string)=>{
  const map:Record<string,string> = {procurement:'Procurement',deployment:'Deployment',operation:'Operation',maintenance:'Maintenance',disposal:'Disposal'}
  return map[s]||s
}

// ECharts Init
const initAllChart = ()=>{
  initPieChart()
  initLineChart()
}
const initPieChart = ()=>{
  if(!pieRef.value) return
  if(pieIns) pieIns.dispose()
  pieIns = echarts.init(pieRef.value)
  const pro = originAsset.value.filter(i=>i.stage==='procurement').length
  const dep = originAsset.value.filter(i=>i.stage==='deployment').length
  const opt = originAsset.value.filter(i=>i.stage==='operation').length
  const main = originAsset.value.filter(i=>i.stage==='maintenance').length
  const dis = originAsset.value.filter(i=>i.stage==='disposal').length
  pieIns.setOption({
    tooltip:{trigger:'item'},
    series:[{
      type:'pie',radius:'62%',
      data:[
        {name:'Procurement',value:pro,itemStyle:{color:'#3b82f6'}},
        {name:'Deployment',value:dep,itemStyle:{color:'#22c55e'}},
        {name:'Operation',value:opt,itemStyle:{color:'#10b981'}},
        {name:'Maintenance',value:main,itemStyle:{color:'#f59e0b'}},
        {name:'Disposal',value:dis,itemStyle:{color:'#ef4444'}},
      ],label:{show:true}
    }]
  })
}
const initLineChart = ()=>{
  if(!lineRef.value) return
  if(lineIns) lineIns.dispose()
  lineIns = echarts.init(lineRef.value)
  const months = ['Jan','Feb','Mar','Apr','May','Jun']
  const inData = [3,2,5,4,3,6]
  const outData = [1,2,1,3,2,2]
  lineIns.setOption({
    tooltip:{trigger:'axis'},
    legend:{data:['New In','Disposed Out'],bottom:10},
    grid:{left:45,right:20,top:30,bottom:55},
    xAxis:{type:'category',data:months},
    yAxis:{type:'value'},
    series:[
      {name:'New In',type:'line',data:inData,smooth:true,lineStyle:{color:'#3b82f6',width:3}},
      {name:'Disposed Out',type:'line',data:outData,smooth:true,lineStyle:{color:'#ef4444',width:3}}
    ]
  })
}
const resizeChart = ()=>{
  pieIns?.resize()
  lineIns?.resize()
}
const refreshChart = ()=>nextTick(initAllChart)

// Methods
const openAdd = ()=>{
  dialogTitle.value = 'Create New Asset'
  formData.value = {sn:'',name:'',category:'',stage:'procurement',buyDate:'',lifeYear:5,remainLife:5,cost:0,remark:''}
  dialogVis.value = true
}
const openEdit = (row:any)=>{
  dialogTitle.value = 'Edit Asset Info'
  formData.value = {...row}
  dialogVis.value = true
}
const saveForm = async()=>{
  await formRef.value.validate((valid:boolean)=>{
    if(!valid) return
    // calc remain life auto
    const buyY = new Date(formData.buyDate).getFullYear()
    const now = new Date().getFullYear()
    formData.remainLife = Number((formData.lifeYear - (now-buyY)).toFixed(1))
    if(formData.sn){
      const idx = originAsset.value.findIndex(i=>i.sn===formData.sn)
      originAsset.value[idx]={...formData}
      ElMessage.success('Asset updated successfully')
    }else{
      const maxNo = originAsset.value.reduce((n,item)=>{
        const num = Number(item.sn.replace('AST-LC',''))
        return num>n?num:n
      },0)
      formData.sn = `AST-LC${String(maxNo+1).padStart(3,'0')}`
      originAsset.value.push({...formData})
      ElMessage.success('New asset created')
    }
    dialogVis.value = false;
    refreshChart()
  })
}
const delAsset = (row:any)=>{
  ElMessageBox.confirm('Confirm to delete this asset?','Warning',{type:'warning'}).then(()=>{
    const idx = originAsset.value.findIndex(i=>i.sn===row.sn)
    originAsset.value.splice(idx,1)
    ElMessage.success('Deleted')
    refreshChart()
  })
}
const refreshData = async()=>{
  refreshLoading.value=true
  await new Promise(r=>setTimeout(r,800))
  refreshChart()
  refreshLoading.value=false
  ElMessage.success('Data refreshed')
}
const resetFilter = ()=>{
  searchKey.value=''
  stageFilter.value=''
  catFilter.value=''
  currentPage.value=1
}
const exportReport = ()=>ElMessage.success('Lifecycle report generating...')

watch([searchKey,stageFilter,catFilter],()=>currentPage.value=1)
onBeforeUnmount(()=>{
  pieIns?.dispose()
  lineIns?.dispose()
  window.removeEventListener('resize',resizeChart)
})
</script>

<style scoped>
/* ========== Original Loading CSS Keep Full ========== */
.loading-container {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  z-index: 9999;
  display: flex;
  justify-content: center;
  align-items: center;
}
.loading-overlay {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  backdrop-filter: blur(2px);
}
.loading-content {
  text-align: center;
  padding: 40px;
  border-radius: 32px;
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(59, 130, 246, 0.3);
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
  animation: fadeInUp 0.6s ease-out;
}
.loading-spinner {
  position: relative;
  width: 80px;
  height: 80px;
  margin: 0 auto 24px;
}
.spinner-ring {
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  border: 3px solid transparent;
  animation: spin 1.5s cubic-bezier(0.68, -0.55, 0.265, 1.55) infinite;
}
.spinner-ring:nth-child(1) {border-top-color: #3b82f6;}
.spinner-ring:nth-child(2) {border-right-color: #f59e0b;width:70%;height:70%;top:15%;left:15%;animation-delay:0.2s;}
.spinner-ring:nth-child(3) {border-bottom-color: #10b981;width:40%;height:40%;top:30%;left:30%;animation-delay:0.4s;}
@keyframes spin {0%{transform:rotate(0deg)}100%{transform:rotate(360deg)}}
.loading-text {
  margin-bottom:24px;font-size:28px;font-weight:700;color:#e2e8f0;display:flex;align-items:baseline;justify-content:center;gap:4px;
}
.loading-dots {display:inline-flex;gap:2px;}
.loading-dots span {animation:bounce 1.4s infinite ease-in-out;}
.loading-dots span:nth-child(1){animation-delay:-0.32s}
.loading-dots span:nth-child(2){animation-delay:-0.16s}
@keyframes bounce {0%,80%,100%{transform:scale(0);opacity:0.3}40%{transform:scale(1);opacity:1}}
.loading-progress {width:280px;height:4px;background:rgba(255,255,255,0.1);border-radius:4px;margin:0 auto 16px;overflow:hidden;}
.progress-bar {height:100%;background:linear-gradient(90deg,#3b82f6,#8b5cf6,#ec489a);background-size:200% auto;animation:shimmer 2s infinite;border-radius:4px;transition:0.3s;}
@keyframes shimmer {0%{background-position:0}100%{background-position:200%}}
.loading-tip {font-size:13px;color:#94a3b;letter-spacing:1px;margin-bottom:8px;font-weight:500;}
.loading-subtip {font-size:11px;color:#64748b;animation:pulse 2s infinite;}
@keyframes pulse {0%,100%{opacity:0.6}50%{opacity:1}}
@keyframes fadeInUp {from{opacity:0;transform:translateY(30px)}to{opacity:1;transform:translateY(0)}}

/* Page CSS */
.lifecycle-page{padding:24px;background:#f6f8fa;min-height:100vh;}
.page-header{display:flex;justify-content:space-between;align-items:flex-end;flex-wrap:wrap;gap:16px;margin-bottom:22px;}
.page-title{font-size:24px;font-weight:700;color:#1e293b;margin:0 0 5px;}
.page-desc{font-size:13px;color:#64748b;}
.header-action{display:flex;gap:12px;}

.stat-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:18px;margin-bottom:22px;}
.stat-card{background:#fff;border-radius:18px;padding:20px;display:flex;align-items:center;gap:16px;box-shadow:0 1px 4px #0000000a;transition:0.25s;}
.stat-card:hover{transform:translateY(-3px);box-shadow:0 8px 20px #00000012;}
.stat-card.blue{border-left:4px solid #3b82f6;}
.stat-card.green{border-left:4px solid #22c55e;}
.stat-card.primary{border-left:4px solid #10b981;}
.stat-card.orange{border-left:4px solid #f59e0b;}
.stat-card.red{border-left:4px solid #ef4444;}
.card-icon{width:50px;height:50px;border-radius:14px;display:flex;align-items:center;justify-content:center;}
.stat-card.blue .card-icon{background:#eff6ff;color:#3b82f6;}
.stat-card.green .card-icon{background:#dcfce7;color:#22c55e;}
.stat-card.primary .card-icon{background:#dcfce7;color:#10b981;}
.stat-card.orange .card-icon{background:#fef3c7;color:#f59e0b;}
.stat-card.red .card-icon{background:#fee2e2;color:#ef4444;}
.stat-num{font-size:28px;font-weight:700;color:#1e293b;}
.stat-name{font-size:13px;color:#64748b;margin-top:4px;}

.chart-row{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:20px;}
.chart-card{background:#fff;border-radius:18px;padding:20px;box-shadow:0 1px 4px #0000000a;}
.chart-title{font-size:16px;font-weight:600;color:#1e293b;margin-bottom:16px;}
.ech-container{height:270px;width:100%;}

.filter-wrap{background:#fff;border-radius:14px;padding:16px 20px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:14px;margin-bottom:20px;}
.filter-left{display:flex;gap:12px;flex-wrap:wrap;}

.table-box{background:#fff;border-radius:18px;padding:20px;}
.pagi-wrap{margin-top:16px;display:flex;justify-content:flex-end;}

/* Responsive */
@media(max-width:1100px){
  .stat-grid{grid-template-columns:repeat(3,1fr)}
  .chart-row{grid-template-columns:1fr}
}
@media(max-width:768px){
  .stat-grid{grid-template-columns:repeat(2,1fr)}
  .page-header{flex-direction:column;align-items:flex-start}
  .filter-left{width:100%;flex-direction:column}
}
@media(max-width:520px){
  .stat-grid{grid-template-columns:1fr}
}
</style>