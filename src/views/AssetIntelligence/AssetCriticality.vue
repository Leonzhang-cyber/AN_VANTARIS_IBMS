<template>
  <!-- Keep Original Full Loading Screen -->
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
        <div class="loading-tip">IBMS Asset Intelligence Module</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Business Page After Loading Finish -->
  <div v-else class="ibms-criticality-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-title-group">
        <h1 class="main-title">Asset Criticality Management</h1>
        <span class="sub-desc">Classify & evaluate facility assets by critical risk tier for IBMS operation</span>
      </div>
      <div class="header-action-group">
        <el-button type="primary" @click="openCreateDialog">
          <el-icon><Plus /></el-icon> New Asset
        </el-button>
        <el-button @click="refreshAllData" :loading="refreshing">
          <el-icon><Refresh /></el-icon> Refresh Data
        </el-button>
        <el-button @click="exportCriticalData">
          <el-icon><Download /></el-icon> Export Report
        </el-button>
      </div>
    </div>

    <!-- KPI Stat Cards -->
    <div class="kpi-card-grid">
      <div class="kpi-card" v-for="item in kpiStats" :key="item.key" :class="item.cssClass">
        <div class="card-icon-box">
          <el-icon :size="26"><component :is="item.iconComp" /></el-icon>
        </div>
        <div class="card-content">
          <div class="kpi-value">{{ item.value }}</div>
          <div class="kpi-label">{{ item.label }}</div>
        </div>
      </div>
    </div>

    <!-- Dual Chart Area -->
    <div class="chart-row">
      <div class="chart-card">
        <div class="chart-header">Criticality Tier Distribution</div>
        <div ref="pieChartRef" class="echart-container"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">Asset Category Count By Risk Level</div>
        <div ref="barChartRef" class="echart-container"></div>
      </div>
    </div>

    <!-- Filter Search Bar -->
    <div class="filter-container">
      <div class="filter-left">
        <el-input
            v-model="searchKeyword"
            placeholder="Search Asset Name / Tag Code"
            clearable
            prefix-icon="Search"
            style="width:260px"
        />
        <el-select v-model="categoryFilter" placeholder="Asset Category" clearable style="width:190px">
          <el-option v-for="cat in categoryOptList" :key="cat" :label="cat" :value="cat"/>
        </el-select>
        <el-select v-model="riskFilter" placeholder="Criticality Level" clearable style="width:170px">
          <el-option label="High Critical" value="high"/>
          <el-option label="Medium Critical" value="medium"/>
          <el-option label="Low Critical" value="low"/>
        </el-select>
      </div>
      <div class="filter-right">
        <el-button @click="resetFilter">Reset Filter</el-button>
      </div>
    </div>

    <!-- Asset Data Table -->
    <div class="table-container">
      <el-table :data="pageDataList" border stripe height="auto">
        <el-table-column label="Asset ID" prop="assetId" width="100"/>
        <el-table-column label="Asset Name" prop="assetName" min-width="180"/>
        <el-table-column label="Category" prop="category" width="140"/>
        <el-table-column label="Location" prop="location" min-width="160"/>
        <el-table-column label="Critical Level" prop="criticalLevel" width="130">
          <template #default="{row}">
            <el-tag :type="getRiskTag(row.criticalLevel)">
              {{ getRiskName(row.criticalLevel) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Critical Score" prop="criticalScore" width="120"/>
        <el-table-column label="Install Date" prop="installDate" width="120"/>
        <el-table-column label="Operation Status" prop="runStatus" width="130">
          <template #default="{row}">
            <el-tag :type="row.runStatus==='Running'?'success':'danger'">
              {{ row.runStatus }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Operation" width="160" fixed="right">
          <template #default="{row}">
            <el-button text type="primary" @click="openEditDialog(row)">Edit</el-button>
            <el-button text type="danger" @click="handleDelete(row)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>
      <!-- Pagination -->
      <div class="pagination-wrap" v-if="totalCount>0">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :total="totalCount"
            :page-sizes="[8,12,20]"
            layout="total,sizes,prev,pager,next"
            background
        />
      </div>
    </div>

    <!-- Add / Edit Asset Dialog -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="720px">
      <el-form :model="assetForm" label-width="140px" :rules="formRules" ref="formRef">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Asset Name" prop="assetName">
              <el-input v-model="assetForm.assetName"/>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Asset Category" prop="category">
              <el-select v-model="assetForm.category" style="width:100%">
                <el-option v-for="c in categoryOptList" :key="c" :label="c" :value="c"/>
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Install Location" prop="location">
              <el-input v-model="assetForm.location"/>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Criticality Level" prop="criticalLevel">
              <el-select v-model="assetForm.criticalLevel" style="width:100%">
                <el-option label="High Critical" value="high"/>
                <el-option label="Medium Critical" value="medium"/>
                <el-option label="Low Critical" value="low"/>
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Critical Score" prop="criticalScore">
              <el-input-number v-model="assetForm.criticalScore" :min="0" :max="100" style="width:100%"/>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Install Date" prop="installDate">
              <el-date-picker v-model="assetForm.installDate" type="date" value-format="YYYY-MM-DD" style="width:100%"/>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="Running Status" prop="runStatus">
          <el-radio-group v-model="assetForm.runStatus">
            <el-radio label="Running"/>
            <el-radio label="Stop"/>
            <el-radio label="Maintenance"/>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="Remark">
          <el-input v-model="assetForm.remark" type="textarea" :rows="3"/>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible=false">Cancel</el-button>
        <el-button type="primary" @click="saveAssetForm">Save</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import {ref, computed, onMounted, nextTick, watch, onBeforeUnmount} from 'vue'
import {ElMessage, ElMessageBox} from 'element-plus'
import * as echarts from 'echarts'
import {Plus, Refresh, Download, Search, Warning, CircleCheck, Document, FolderOpened, View} from '@element-plus/icons-vue'

// ========== Original Loading Code (FULLY RESERVED) ==========
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Initializing...',
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
      // Init ECharts after page render complete
      nextTick(()=>{
        initPieChart()
        initBarChart()
      })
    }, 400)
  }, 2000)

  window.addEventListener('resize',resizeChart)
})

// ========= Business Page State =========
const refreshing = ref(false)
const dialogVisible = ref(false)
const dialogTitle = ref('New Critical Asset')
const formRef = ref()
const pieChartRef = ref<HTMLElement|null>(null)
const barChartRef = ref<HTMLElement|null>(null)
let pieIns:echarts.ECharts|null = null
let barIns:echarts.ECharts|null = null

const searchKeyword = ref('')
const categoryFilter = ref('')
const riskFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(8)

// Mock IBMS asset data
const rawAssetList = ref([
  {assetId:'AST001',assetName:'Main UPS Unit-01',category:'Power System',location:'B1-Floor Power Room',criticalLevel:'high',criticalScore:92,installDate:'2023-02-15',runStatus:'Running',remark:'Core backup power supply'},
  {assetId:'AST002',assetName:'Chiller Unit-A1',category:'HVAC System',location:'Roof Equipment Yard',criticalLevel:'high',criticalScore:89,installDate:'2023-03-22',runStatus:'Running',remark:'Building central cooling'},
  {assetId:'AST003',assetName:'CRAC-02 Cabinet',category:'HVAC System',location:'IDF Room-3F',criticalLevel:'medium',criticalScore:71,installDate:'2023-05-10',runStatus:'Maintenance',remark:'Data cabinet air conditioning'},
  {assetId:'AST004',assetName:'Emergency Diesel Gen',category:'Power System',location:'B2 Generator Room',criticalLevel:'high',criticalScore:95,installDate:'2022-11-08',runStatus:'Running',remark:'Emergency power source'},
  {assetId:'AST005',assetName:'Lighting Panel-L1',category:'Low-Voltage',location:'1F Distribution Room',criticalLevel:'low',criticalScore:32,installDate:'2023-07-19',runStatus:'Running',remark:'Public area lighting'},
  {assetId:'AST006',assetName:'Fire Pump Set',category:'Fire Protection',location:'B1 Pump Room',criticalLevel:'high',criticalScore:90,installDate:'2022-09-30',runStatus:'Stop',remark:'Fire water supply'},
  {assetId:'AST007',assetName:'Exhaust Fan-05',category:'HVAC System',location:'Basement Corridor',criticalLevel:'low',criticalScore:28,installDate:'2023-08-12',runStatus:'Running',remark:'Basement ventilation'},
  {assetId:'AST008',assetName:'ATS Switchgear',category:'Power System',location:'B1 Main Electric Room',criticalLevel:'medium',criticalScore:76,installDate:'2023-01-20',runStatus:'Running',remark:'Automatic transfer switch'},
  {assetId:'AST009',assetName:'Water Treatment Unit',category:'Water Supply',location:'B2 Water Room',criticalLevel:'medium',criticalScore:68,installDate:'2023-04-05',runStatus:'Maintenance',remark:'Domestic water processing'},
  {assetId:'AST010',assetName:'Public Drain Pump',category:'Water Supply',location:'B2 Sump Pit',criticalLevel:'low',criticalScore:35,installDate:'2023-06-18',runStatus:'Running',remark:'Basement drainage'},
])

const categoryOptList = computed(()=>{
  const set = new Set(rawAssetList.value.map(i=>i.category))
  return Array.from(set)
})

const filterAssetList = computed(()=>{
  let arr = [...rawAssetList.value]
  if(searchKeyword.value){
    const kw = searchKeyword.value.toLowerCase()
    arr = arr.filter(i=>i.assetName.toLowerCase().includes(kw)||i.assetId.toLowerCase().includes(kw))
  }
  if(categoryFilter.value) arr = arr.filter(i=>i.category===categoryFilter.value)
  if(riskFilter.value) arr = arr.filter(i=>i.criticalLevel===riskFilter.value)
  return arr
})

const totalCount = computed(()=>filterAssetList.value.length)
const pageDataList = computed(()=>{
  const s = (currentPage.value-1)*pageSize.value
  const e = s+pageSize.value
  return filterAssetList.value.slice(s,e)
})

const kpiStats = computed(()=>{
  const total = rawAssetList.value.length
  const high = rawAssetList.value.filter(i=>i.criticalLevel==='high').length
  const medium = rawAssetList.value.filter(i=>i.criticalLevel==='medium').length
  const low = rawAssetList.value.filter(i=>i.criticalLevel==='low').length
  return [
    {key:'total',label:'Total Assets',value:total,iconComp:Document,cssClass:'all'},
    {key:'high',label:'High Critical Assets',value:high,iconComp:Warning,cssClass:'high'},
    {key:'medium',label:'Medium Critical Assets',value:medium,iconComp:FolderOpened,cssClass:'medium'},
    {key:'low',label:'Low Critical Assets',value:low,iconComp:CircleCheck,cssClass:'low'},
  ]
})

const assetForm = ref({
  assetId:'',
  assetName:'',
  category:'',
  location:'',
  criticalLevel:'low',
  criticalScore:50,
  installDate:'',
  runStatus:'Running',
  remark:''
})
const formRules = {
  assetName:[{required:true,message:'Asset Name Required',trigger:'blur'}],
  category:[{required:true,message:'Select Asset Category',trigger:'change'}],
  location:[{required:true,message:'Fill Install Location',trigger:'blur'}],
  criticalLevel:[{required:true,message:'Select Critical Level',trigger:'change'}],
  installDate:[{required:true,message:'Select Install Date',trigger:'change'}]
}

// ECharts Init
const initPieChart = ()=>{
  if(!pieChartRef.value) return
  if(pieIns) pieIns.dispose()
  pieIns = echarts.init(pieChartRef.value)
  const highCnt = rawAssetList.value.filter(i=>i.criticalLevel==='high').length
  const medCnt = rawAssetList.value.filter(i=>i.criticalLevel==='medium').length
  const lowCnt = rawAssetList.value.filter(i=>i.criticalLevel==='low').length
  pieIns.setOption({
    tooltip:{trigger:'item',formatter:'{b}: {c} | {d}%'},
    series:[{
      type:'pie',
      radius:['35%','70%'],
      data:[
        {name:'High Critical',value:highCnt,itemStyle:{color:'#ef4444'}},
        {name:'Medium Critical',value:medCnt,itemStyle:{color:'#f59e0b'}},
        {name:'Low Critical',value:lowCnt,itemStyle:{color:'#22c55e'}}
      ],
      label:{show:true,formatter:'{b}: {c}'}
    }]
  })
}

const initBarChart = ()=>{
  if(!barChartRef.value) return
  if(barIns) barIns.dispose()
  barIns = echarts.init(barChartRef.value)
  const group:Record<string,{high:number,medium:number,low:number}> = {}
  rawAssetList.value.forEach(item=>{
    if(!group[item.category]) group[item.category]={high:0,medium:0,low:0}
    group[item.category][item.criticalLevel]++
  })
  const cats = Object.keys(group)
  const highData = cats.map(k=>group[k].high)
  const medData = cats.map(k=>group[k].medium)
  const lowData = cats.map(k=>group[k].low)
  barIns.setOption({
    tooltip:{trigger:'axis'},
    legend:{data:['High','Medium','Low'],bottom:10},
    grid:{left:45,right:20,top:30,bottom:70},
    xAxis:{type:'category',data:cats,axisLabel:{rotate:35}},
    yAxis:{type:'value'},
    series:[
      {name:'High',type:'bar',data:highData,itemStyle:{color:'#ef4444'}},
      {name:'Medium',type:'bar',data:medData,itemStyle:{color:'#f59e0b'}},
      {name:'Low',type:'bar',data:lowData,itemStyle:{color:'#22c55e'}}
    ]
  })
}

const resizeChart = ()=>{
  pieIns?.resize()
  barIns?.resize()
}

// Methods
const getRiskTag = (lev:string)=>{
  if(lev==='high') return 'danger'
  if(lev==='medium') return 'warning'
  return 'success'
}
const getRiskName = (lev:string)=>{
  if(lev==='high') return 'High Critical'
  if(lev==='medium') return 'Medium Critical'
  return 'Low Critical'
}

const openCreateDialog = ()=>{
  dialogTitle.value = 'New Critical Asset'
  assetForm.value = {assetId:'',assetName:'',category:'',location:'',criticalLevel:'low',criticalScore:50,installDate:'',runStatus:'Running',remark:''}
  dialogVisible.value = true
}
const openEditDialog = (row:any)=>{
  dialogTitle.value = 'Edit Critical Asset'
  assetForm.value = {...row}
  dialogVisible.value = true
}
const saveAssetForm = async()=>{
  await formRef.value.validate((valid:boolean)=>{
    if(!valid) return
    if(assetForm.value.assetId){
      const idx = rawAssetList.value.findIndex(i=>i.assetId===assetForm.value.assetId)
      rawAssetList.value[idx] = {...assetForm.value}
      ElMessage.success('Asset data updated successfully')
    }else{
      const maxId = rawAssetList.value.reduce((max,item)=>{
        const num = Number(item.assetId.replace('AST',''))
        return num>max?num:max
      },0)
      const newId = `AST${String(maxId+1).padStart(3,'0')}`
      rawAssetList.value.push({...assetForm.value,assetId:newId})
      ElMessage.success('New asset created successfully')
    }
    dialogVisible.value = false
    refreshChart()
  })
}
const handleDelete = (row:any)=>{
  ElMessageBox.confirm('Confirm to delete this asset data?','Warning',{type:'warning'}).then(()=>{
    const idx = rawAssetList.value.findIndex(i=>i.assetId===row.assetId)
    rawAssetList.value.splice(idx,1)
    ElMessage.success('Deleted successfully')
    refreshChart()
  })
}
const refreshAllData = async()=>{
  refreshing.value = true
  await new Promise(r=>setTimeout(r,800))
  refreshChart()
  refreshing.value = false
  ElMessage.success('IBMS asset data refreshed')
}
const resetFilter = ()=>{
  searchKeyword.value=''
  categoryFilter.value=''
  riskFilter.value=''
  currentPage.value=1
}
const exportCriticalData = ()=>{
  ElMessage.success('Critical asset report generating...')
}
const refreshChart = ()=>{
  nextTick(()=>{
    initPieChart()
    initBarChart()
  })
}

watch([searchKeyword,categoryFilter,riskFilter],()=>{
  currentPage.value=1
},{immediate:false})

onBeforeUnmount(()=>{
  pieIns?.dispose()
  barIns?.dispose()
  window.removeEventListener('resize',resizeChart)
})
</script>

<style scoped>
/* ========== Original Loading CSS FULL RETAINED ========== */
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

.spinner-ring:nth-child(1) {
  border-top-color: #3b82f6;
  animation-delay: 0s;
}

.spinner-ring:nth-child(2) {
  border-right-color: #f59e0b;
  animation-delay: 0.2s;
  width: 70%;
  height: 70%;
  top: 15%;
  left: 15%;
}

.spinner-ring:nth-child(3) {
  border-bottom-color: #10b981;
  animation-delay: 0.4s;
  width: 40%;
  height: 40%;
  top: 30%;
  left: 30%;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  margin-bottom: 24px;
  font-size: 28px;
  font-weight: 700;
  color: #e2e8f0;
  display: flex;
  justify-content: center;
  align-items: baseline;
  gap: 4px;
}

.loading-dots {
  display: inline-flex;
  gap: 2px;
}

.loading-dots span {
  animation: bounce 1.4s infinite ease-in-out both;
}

.loading-dots span:nth-child(1) { animation-delay: -0.32s; }
.loading-dots span:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); opacity: 0.3; }
  40% { transform: scale(1); opacity: 1; }
}

.loading-progress {
  width: 280px;
  height: 4px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  overflow: hidden;
  margin: 0 auto 16px;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #8b5cf6, #ec489a);
  border-radius: 4px;
  transition: width 0.3s ease;
  background-size: 200% auto;
  animation: shimmer 2s linear infinite;
}

@keyframes shimmer {
  0% { background-position: 0% 0%; }
  100% { background-position: 200% 0%; }
}

.loading-tip {
  font-size: 13px;
  color: #94a3b8;
  letter-spacing: 1px;
  margin-bottom: 8px;
  font-weight: 500;
}

.loading-subtip {
  font-size: 11px;
  color: #64748b;
  letter-spacing: 0.5px;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}

/* ===== IBMS Business Page CSS ===== */
.ibms-criticality-page{
  padding:24px;
  background:#f6f8fa;
  min-height:100vh;
}
.page-header{
  display:flex;
  justify-content:space-between;
  align-items:flex-end;
  margin-bottom:24px;
  flex-wrap:wrap;
  gap:16px;
}
.main-title{
  font-size:24px;
  font-weight:700;
  color:#1e293b;
  margin:0 0 6px;
}
.sub-desc{
  font-size:13px;
  color:#64748b;
}
.header-action-group{
  display:flex;
  gap:12px;
}
.kpi-card-grid{
  display:grid;
  grid-template-columns:repeat(4,1fr);
  gap:20px;
  margin-bottom:24px;
}
.kpi-card{
  background:#fff;
  border-radius:18px;
  padding:20px;
  display:flex;
  align-items:center;
  gap:16px;
  box-shadow:0 1px 4px #0000000a;
  transition:0.25s;
}
.kpi-card:hover{transform:translateY(-3px);box-shadow:0 8px 22px #00000012;}
.kpi-card.high{border-left:4px solid #ef4444;}
.kpi-card.medium{border-left:4px solid #f59e0b;}
.kpi-card.low{border-left:4px solid #22c55e;}
.kpi-card.all{border-left:4px solid #3b82f6;}
.card-icon-box{
  width:50px;height:50px;
  border-radius:14px;
  display:flex;align-items:center;justify-content:center;
}
.kpi-card.all .card-icon-box{background:#eff6ff;color:#3b82f6;}
.kpi-card.high .card-icon-box{background:#fee2e2;color:#ef4444;}
.kpi-card.medium .card-icon-box{background:#fef3c7;color:#f59e0b;}
.kpi-card.low .card-icon-box{background:#dcfce7;color:#22c55e;}
.kpi-value{font-size:28px;font-weight:700;color:#1e293b;}
.kpi-label{font-size:13px;color:#64748b;margin-top:4px;}
.chart-row{
  display:grid;
  grid-template-columns:1fr 1fr;
  gap:20px;
  margin-bottom:20px;
}
.chart-card{
  background:#fff;
  border-radius:18px;
  padding:20px;
  box-shadow:0 1px 4px #0000000a;
}
.chart-header{
  font-size:16px;
  font-weight:600;
  color:#1e293b;
  margin-bottom:16px;
}
.echart-container{height:270px;width:100%;}
.filter-container{
  background:#fff;
  border-radius:14px;
  padding:16px 20px;
  display:flex;
  justify-content:space-between;
  align-items:center;
  flex-wrap:wrap;gap:14px;
  margin-bottom:20px;
}
.filter-left{display:flex;gap:12px;flex-wrap:wrap;}
.table-container{background:#fff;border-radius:18px;padding:20px;}
.pagination-wrap{margin-top:16px;display:flex;justify-content:flex-end;}
@media(max-width:1100px){
  .kpi-card-grid{grid-template-columns:repeat(2,1fr);}
  .chart-row{grid-template-columns:1fr;}
}
@media(max-width:640px){
  .kpi-card-grid{grid-template-columns:1fr;}
  .page-header{flex-direction:column;align-items:flex-start;}
}
</style>