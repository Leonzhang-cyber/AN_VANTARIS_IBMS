<template>
  <!-- Keep your original Loading -->
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
        <div class="loading-tip">IBMS Asset Risk Matrix Module</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <div v-else class="risk-page">
    <!-- Header -->
    <div class="page-head">
      <div class="head-left">
        <h2 class="page-title">Asset Risk Matrix</h2>
        <div class="page-desc">Risk assessment based on Probability & Impact scoring for IBMS assets</div>
      </div>
      <div class="head-btn">
        <el-button type="primary" @click="openAdd">
          <el-icon><Plus /></el-icon> New Risk Record
        </el-button>
        <el-button @click="refresh" :loading="loadRef">
          <el-icon><Refresh /></el-icon> Refresh
        </el-button>
        <el-button @click="exportData">
          <el-icon><Download /></el-icon> Export
        </el-button>
      </div>
    </div>

    <!-- Stats Card -->
    <div class="stat-grid">
      <div class="stat-card" v-for="item in statList" :key="item.key" :class="item.class">
        <div class="card-icon"><el-icon :size="24"><component :is="item.icon"/></el-icon></div>
        <div class="card-data">
          <div class="num">{{ item.value }}</div>
          <div class="lab">{{ item.label }}</div>
        </div>
      </div>
    </div>

    <!-- Risk Matrix Heatmap + Pie -->
    <div class="chart-row">
      <div class="chart-card">
        <div class="card-title">Risk Matrix Heatmap (Impact × Probability)</div>
        <div ref="matrixRef" class="ech-box"></div>
      </div>
      <div class="chart-card">
        <div class="card-title">Risk Level Distribution</div>
        <div ref="pieRef" class="ech-box"></div>
      </div>
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <div class="filter-left">
        <el-input v-model="search" placeholder="Search Asset Name/ID" clearable style="width:250px" prefix-icon="Search"/>
        <el-select v-model="riskFilter" placeholder="Risk Level" clearable style="width:160px">
          <el-option label="Critical" value="critical"/>
          <el-option label="High" value="high"/>
          <el-option label="Medium" value="medium"/>
          <el-option label="Low" value="low"/>
        </el-select>
        <el-select v-model="catFilter" placeholder="Asset Category" clearable style="width:180px">
          <el-option v-for="c in catArr" :key="c" :label="c" :value="c"/>
        </el-select>
      </div>
      <el-button @click="resetFilter">Reset Filter</el-button>
    </div>

    <!-- Table -->
    <div class="table-wrap">
      <el-table :data="tableData" border stripe>
        <el-table-column label="Asset ID" prop="assetId" width="100"/>
        <el-table-column label="Asset Name" prop="assetName" min-width="170"/>
        <el-table-column label="Category" prop="category" width="140"/>
        <el-table-column label="Probability Score" prop="probScore" width="130"/>
        <el-table-column label="Impact Score" prop="impactScore" width="130"/>
        <el-table-column label="Risk Score" prop="riskScore" width="120"/>
        <el-table-column label="Risk Level" prop="riskLevel" width="130">
          <template #default="{row}">
            <el-tag :type="getTag(row.riskLevel)">{{ getName(row.riskLevel) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Remark" prop="remark" min-width="180"/>
        <el-table-column label="Action" width="150" fixed="right">
          <template #default="{row}">
            <el-button text type="primary" @click="openEdit(row)">Edit</el-button>
            <el-button text type="danger" @click="delRow(row)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagi" v-if="total>0">
        <el-pagination v-model:current-page="page" v-model:page-size="size" :total="total" :page-sizes="[8,12,20]" background layout="total,sizes,prev,pager,next"/>
      </div>
    </div>

    <!-- Add/Edit Dialog -->
    <el-dialog v-model="dialogVis" :title="dialogTitle" width="680">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="135px">
        <el-row :gutter="18">
          <el-col :span="12">
            <el-form-item label="Asset Name" prop="assetName">
              <el-input v-model="form.assetName"/>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Asset Category" prop="category">
              <el-select v-model="form.category" style="width:100%">
                <el-option v-for="c in catArr" :key="c" :label="c" :value="c"/>
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="18">
          <el-col :span="12">
            <el-form-item label="Probability Score(1-5)" prop="probScore">
              <el-input-number v-model="form.probScore" :min="1" :max="5" style="width:100"/>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Impact Score(1-5)" prop="impactScore">
              <el-input-number v-model="form.impactScore" :min="1" :max="5" style="width:100"/>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="Remark">
          <el-input v-model="form.remark" type="textarea" :rows="3"/>
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
import {Plus,Refresh,Download,Search,Warning,Document,CircleCheck,DataLine} from '@element-plus/icons-vue'

// === 完全保留你的Loading代码 ===
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
      // 多等150ms保证dom完全渲染
      setTimeout(()=>{
        initMatrix()
        initPie()
      },150)
    }, 400)
  }, 2000)

  window.addEventListener('resize',resizeAllChart)
})

// ====== Page Data =====
const loadRef = ref(false)
const dialogVis = ref(false)
const dialogTitle = ref('Add Risk Record')
const formRef = ref()
const matrixRef = ref<HTMLElement|null>(null)
const pieRef = ref<HTMLElement|null>(null)
let matrixIns:echarts.ECharts|null=null
let pieIns:echarts.ECharts|null=null

const search = ref('')
const riskFilter = ref('')
const catFilter = ref('')
const page = ref(1)
const size = ref(8)

// Mock data
const originData = ref([
  {assetId:'RIS001',assetName:'Main UPS',category:'Power System',probScore:4,impactScore:5,riskScore:20,riskLevel:'critical',remark:'Core power failure risk'},
  {assetId:'RIS002',assetName:'Building Chiller',category:'HVAC',probScore:3,impactScore:4,riskScore:12,riskLevel:'high',remark:'Summer overload risk'},
  {assetId:'RIS003',assetName:'Basement Fan',category:'HVAC',probScore:2,impactScore:2,riskScore:4,riskLevel:'low',remark:'Minor wear'},
  {assetId:'RIS004',assetName:'Fire Water Pump',category:'Fire',probScore:3,impactScore:5,riskScore:15,riskLevel:'critical',remark:'Fire safety core'},
  {assetId:'RIS005',assetName:'Lighting Panel',category:'Low Volt',probScore:2,impactScore:3,riskScore:6,riskLevel:'medium',remark:'Local short risk'},
  {assetId:'RIS006',assetName:'Diesel Generator',category:'Power',probScore:3,impactScore:4,riskScore:12,riskLevel:'high',remark:'Fuel supply risk'},
  {assetId:'RIS007',assetName:'Drain Pump',category:'Water',probScore:2,impactScore:2,riskScore:4,riskLevel:'low',remark:'Basement flooding minor'},
  {assetId:'RIS008',assetName:'CRAC Aircon',category:'HVAC',probScore:3,impactScore:3,riskScore:9,riskLevel:'medium',remark:'ID room temp risk'},
])

const catArr = computed(()=>[...new Set(originData.value.map(i=>i.category))])

// Filter table
const allFilter = computed(()=>{
  let arr = [...originData.value]
  if(search.value){
    const kw = search.value.toLowerCase()
    arr = arr.filter(x=>x.assetName.toLowerCase().includes(kw)||x.assetId.toLowerCase().includes(kw))
  }
  if(riskFilter.value) arr = arr.filter(x=>x.riskLevel===riskFilter.value)
  if(catFilter.value) arr = arr.filter(x=>x.category===catFilter.value)
  return arr
})
const total = computed(()=>allFilter.value.length)
const tableData = computed(()=>{
  const s=(page.value-1)*size.value
  return allFilter.value.slice(s,s+size.value)
})

// Stat card
const statList = computed(()=>{
  const totalAll = originData.value.length
  const critical = originData.value.filter(i=>i.riskLevel==='critical').length
  const high = originData.value.filter(i=>i.riskLevel==='high').length
  const mid = originData.value.filter(i=>i.riskLevel==='medium').length
  const low = originData.value.filter(i=>i.riskLevel==='low').length
  return [
    {key:'all',label:'Total Assets',value:totalAll,icon:Document,class:'all'},
    {key:'crt',label:'Critical Risk',value:critical,icon:Warning,class:'crt'},
    {key:'h',label:'High Risk',value:high,icon:DataLine,class:'high'},
    {key:'m',label:'Medium+Low',value:mid+low,icon:CircleCheck,class:'norm'},
  ]
})

// Form
const form = ref({
  assetId:'',assetName:'',category:'',probScore:3,impactScore:3,riskScore:0,riskLevel:'low',remark:''
})
const rules = {
  assetName:[{required:true,message:'Required',trigger:'blur'}],
  category:[{required:true,message:'Select category',trigger:'change'}],
  probScore:[{required:true,message:'Required',trigger:'change'}],
  impactScore:[{required:true,message:'Required',trigger:'change'}]
}

// Risk helper
const calcRisk = (p:number,i:number)=>{
  const score = p*i
  if(score>=16) return 'critical'
  else if(score>=9) return 'high'
  else if(score>=5) return 'medium'
  return 'low'
}
const getTag = (s:string)=>{
  if(s==='critical') return 'danger'
  if(s==='high') return 'warning'
  if(s==='medium') return ''
  return 'success'
}
const getName = (s:string)=>{
  if(s==='critical') return 'Critical'
  if(s==='high') return 'High'
  if(s==='medium') return 'Medium'
  return 'Low'
}

// Chart
const initMatrix = ()=>{
  if(!matrixRef.value) return
  if(matrixIns) matrixIns.dispose()
  matrixIns = echarts.init(matrixRef.value)
  const xAxis = ['1-Low Impact','2','3','4','5-High Impact']
  const yAxis = ['5-High Prob','4','3','2','1-Low Prob']
  const heatData: any[] = []
  originData.value.forEach(item=>{
    // x:impact 0~4，y:prob 0~5 修正坐标计算
    const yIdx = 5 - item.probScore
    const xIdx = item.impactScore - 1
    heatData.push([xIdx, yIdx, item.riskScore])
  })
  const option = {
    tooltip:{formatter:'Impact:{b}<br>Prob:{a}<br>Risk Score:{c}'},
    grid:{top:30,left:55,right:30,bottom:40},
    xAxis:{type:'category',data:xAxis},
    yAxis:{type:'category',data:yAxis},
    visualMap:{
      min:1,max:25,calculable:true,
      inRange:{color:['#91cf60','#ffffbf','#fd9e58','#de2d26']}
    },
    series:[{
      type:'heatmap',
      data:heatData,
      label:{show:true,fontSize:12}
    }]
  }
  matrixIns.setOption(option)
}

const initPie = ()=>{
  if(!pieRef.value) return
  if(pieIns) pieIns.dispose()
  pieIns = echarts.init(pieRef.value)
  const crt = originData.value.filter(i=>i.riskLevel==='critical').length
  const h = originData.value.filter(i=>i.riskLevel==='high').length
  const m = originData.value.filter(i=>i.riskLevel==='medium').length
  const l = originData.value.filter(i=>i.riskLevel==='low').length
  const option = {
    tooltip:{trigger:'item'},
    series:[{
      type:'pie',radius:'65%',
      data:[
        {name:'Critical',value:crt,itemStyle:{color:'#de2d26'}},
        {name:'High',value:h,itemStyle:{color:'#fd9e58'}},
        {name:'Medium',value:m,itemStyle:{color:'#ffffbf'}},
        {name:'Low',value:l,itemStyle:{color:'#91cf60'}},
      ],
      label:{show:true}
    }]
  }
  pieIns.setOption(option)
}
const resizeAllChart = ()=>{
  matrixIns?.resize()
  pieIns?.resize()
}
const refreshChart = ()=>{
  nextTick(()=>{initMatrix();initPie()})
}

// Methods
const openAdd = ()=>{
  dialogTitle.value = 'Add Risk Record'
  form.value = {assetId:'',assetName:'',category:'',probScore:3,impactScore:3,riskScore:0,riskLevel:'low',remark:''}
  dialogVis.value = true
}
const openEdit = (row:any)=>{
  dialogTitle.value = 'Edit Risk Record'
  form.value = {...row}
  dialogVis.value = true
}
const saveForm = async()=>{
  await formRef.value.validate((valid:boolean)=>{
    if(!valid) return
    const score = form.value.probScore*form.value.impactScore
    const lev = calcRisk(form.value.probScore,form.value.impactScore)
    form.value.riskScore = score
    form.value.riskLevel = lev
    if(form.value.assetId){
      const idx = originData.value.findIndex(x=>x.assetId===form.value.assetId)
      originData.value[idx]={...form.value}
      ElMessage.success('Updated')
    }else{
      const maxId = originData.value.reduce((n,i)=>Math.max(n,Number(i.assetId.replace('RIS',''))),0)
      form.value.assetId = `RIS${String(maxId+1).padStart(3,'0')}`
      originData.value.push({...form.value})
      ElMessage.success('Created')
    }
    dialogVis.value = false;
    refreshChart()
  })
}
const delRow = (row:any)=>{
  ElMessageBox.confirm('Delete this risk data?','Warning',{type:'warning'}).then(()=>{
    const idx = originData.value.findIndex(x=>x.assetId===row.assetId)
    originData.value.splice(idx,1)
    ElMessage.success('Deleted')
    refreshChart()
  })
}
const refresh = async()=>{
  loadRef.value=true
  await new Promise(r=>setTimeout(r,800))
  refreshChart()
  loadRef.value=false
  ElMessage.success('Data refreshed')
}
const resetFilter = ()=>{
  search.value=''
  riskFilter.value=''
  catFilter.value=''
  page.value=1
}
const exportData = ()=>ElMessage.success('Export task started')

watch([search,riskFilter,catFilter],()=>page.value=1)
onBeforeUnmount(()=>{
  matrixIns?.dispose()
  pieIns?.dispose()
  window.removeEventListener('resize',resizeAllChart)
})
</script>

<style scoped>
/* ========== 原样保留Loading样式 ========== */
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
.loading-tip {font-size:13px;color:#94a3b8;letter-spacing:1px;margin-bottom:8px;font-weight:500;}
.loading-subtip {font-size:11px;color:#64748b;animation:pulse 2s infinite;}
@keyframes pulse {0%,100%{opacity:0.6}50%{opacity:1}}
@keyframes fadeInUp {from{opacity:0;transform:translateY(30px)}to{opacity:1;transform:translateY(0)}}

/* Page CSS */
.risk-page{padding:24px;background:#f6f8fa;min-height:100vh;}
.page-head{display:flex;justify-content:space-between;align-items:flex-end;flex-wrap:wrap;gap:16px;margin-bottom:22px;}
.page-title{font-size:24px;font-weight:700;color:#1e293b;margin:0 0 5px;}
.page-desc{font-size:13px;color:#64748b;}
.head-btn{display:flex;gap:12px;}

.stat-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:20px;margin-bottom:22px;}
.stat-card{background:#fff;border-radius:18px;padding:20px;display:flex;align-items:center;gap:16px;box-shadow:0 1px 4px #0000000a;transition:0.25s;}
.stat-card:hover{transform:translateY(-3px);box-shadow:0 8px 20px #00000012;}
.stat-card.all{border-left:4px #3b82f6 solid;}
.stat-card.crt{border-left:4px #de2d26 solid;}
.stat-card.high{border-left:4px #fd9e58 solid;}
.stat-card.norm{border-left:4px #91cf60 solid;}
.card-icon{width:50px;height:50px;border-radius:14px;display:flex;align-items:center;justify-content: center;}
.stat-card.all .card-icon{background:#eff6ff;color:#3b82f6;}
.stat-card.crt .card-icon{background:#fee2e2;color:#de2d26;}
.stat-card.high .card-icon{background:#fff2e2;color:#fd9e58;}
.stat-card.norm .card-icon{background:#e6f9e9;color:#2da950;}
.num{font-size:28px;font-weight:700;color:#1e293b;}
.lab{font-size:13px;color:#64748b;margin-top:4px;}

.chart-row{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:20px;}
.chart-card{background:#fff;border-radius:18px;padding:20px;box-shadow:0 1px 4px #0000000a;}
.card-title{font-size:16px;font-weight:600;color:#1e293b;margin-bottom:16px;}
.ech-box{height:270px;width:100%;}

.filter-bar{background:#fff;border-radius:14px;padding:16px 20px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:14px;margin-bottom:20px;}
.filter-left{display:flex;gap:12px;flex-wrap:wrap;}

.table-wrap{background:#fff;border-radius:18px;padding:20px;}
.pagi{margin-top:16px;display:flex;justify-content:flex-end;}

/* Responsive */
@media(max-width:1080px){
  .stat-grid{grid-template-columns:repeat(2,1fr)}
  .chart-row{grid-template-columns:1fr}
}
@media(max-width:640px){
  .stat-grid,.page-head{grid-template-columns:1fr;flex-direction:column;align-items:flex-start}
  .filter-left{width:100%;flex-direction:column}
}
</style>