<template>
  <!-- Loading Screen -->
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
        <div class="loading-tip">Trust & Identity - Smart Contracts</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="smart-contracts-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h1>Smart Contracts</h1>
        <p>Deploy, manage, and interact with blockchain smart contracts</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="openDeployDialog">
          <el-icon><Plus /></el-icon>
          Deploy Contract
        </el-button>
        <el-button @click="importContract">
          <el-icon><Upload /></el-icon>
          Import Contract
        </el-button>
        <el-button @click="refreshContracts">
          <el-icon><Refresh /></el-icon>
          Refresh
        </el-button>
      </div>
    </div>

    <!-- Stats Cards -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon primary-bg">
            <el-icon><Document /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.totalContracts }}</div>
            <div class="stat-label">Total Contracts</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon success-bg">
            <el-icon><CircleCheck /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.activeContracts }}</div>
            <div class="stat-label">Active</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon warning-bg">
            <el-icon><TrendCharts /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.totalTransactions }}</div>
            <div class="stat-label">Total Transactions</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon info-bg">
            <el-icon><Connection /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.networkName }}</div>
            <div class="stat-label">Network</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Blockchain Network Status -->
    <div class="network-status">
      <div class="status-left">
        <div class="status-indicator" :class="networkStatus"></div>
        <span class="status-text">Network: {{ networkStatus === 'connected' ? 'Connected' : 'Disconnected' }}</span>
        <span class="network-name">{{ networkName }}</span>
      </div>
      <div class="status-right">
        <span>Chain ID: {{ chainId }}</span>
        <span>Block: {{ currentBlock }}</span>
        <span>Gas Price: {{ gasPrice }} Gwei</span>
      </div>
      <el-button size="small" @click="switchNetwork">Switch Network</el-button>
    </div>

    <!-- Search & Filter -->
    <div class="filter-bar">
      <el-input
          v-model="filters.search"
          placeholder="Search by contract name or address..."
          clearable
          style="width: 280px"
          :prefix-icon="Search"
      />
      <el-select v-model="filters.status" placeholder="Status" clearable style="width: 130px">
        <el-option label="All" value="" />
        <el-option label="Active" value="active" />
        <el-option label="Paused" value="paused" />
        <el-option label="Deprecated" value="deprecated" />
      </el-select>
      <el-select v-model="filters.type" placeholder="Type" clearable style="width: 140px">
        <el-option label="All Types" value="" />
        <el-option label="ERC-20" value="erc20" />
        <el-option label="ERC-721" value="erc721" />
        <el-option label="Access Control" value="access" />
        <el-option label="Registry" value="registry" />
      </el-select>
      <el-button type="primary" @click="handleSearch">
        <el-icon><Search /></el-icon>
        Apply
      </el-button>
      <el-button @click="resetFilters">
        <el-icon><RefreshLeft /></el-icon>
        Reset
      </el-button>
    </div>

    <!-- Contracts Table -->
    <div class="contracts-table-wrapper">
      <el-table :data="filteredContracts" stripe v-loading="tableLoading" style="width: 100%">
        <el-table-column prop="name" label="Contract Name" min-width="180" />
        <el-table-column prop="address" label="Contract Address" width="280" show-overflow-tooltip>
          <template #default="{ row }">
            <code class="address-code">{{ row.address }}</code>
            <el-button link size="small" @click="copyAddress(row.address)">
              <el-icon><CopyDocument /></el-icon>
            </el-button>
          </template>
        </el-table-column>
        <el-table-column prop="type" label="Type" width="120">
          <template #default="{ row }">
            <el-tag size="small">{{ formatContractType(row.type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="network" label="Network" width="100" />
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)" size="small">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="deployedAt" label="Deployed At" width="160" />
        <el-table-column prop="deployedBy" label="Deployed By" width="160" />
        <el-table-column label="Actions" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewContract(row)">
              View
            </el-button>
            <el-button link type="success" size="small" @click="interactContract(row)">
              Interact
            </el-button>
            <el-dropdown trigger="click" @command="(cmd) => handleDropdown(cmd, row)">
              <el-button link size="small">
                <el-icon><MoreFilled /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="verify">Verify on Explorer</el-dropdown-item>
                  <el-dropdown-item command="export">Export ABI</el-dropdown-item>
                  <el-dropdown-item v-if="row.status === 'active'" command="pause">Pause</el-dropdown-item>
                  <el-dropdown-item v-if="row.status === 'paused'" command="resume">Resume</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination
            v-model:current-page="pagination.currentPage"
            v-model:page-size="pagination.pageSize"
            :page-sizes="[10, 20, 50]"
            :total="pagination.total"
            layout="total, sizes, prev, pager, next"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- Deploy Contract Dialog -->
    <el-dialog v-model="deployDialog.visible" title="Deploy Smart Contract" width="700px" class="deploy-dialog">
      <el-steps :active="deployStep" finish-status="success" align-center style="margin-bottom: 24px">
        <el-step title="Contract Info" />
        <el-step title="ABI and Bytecode" />
        <el-step title="Deploy" />
      </el-steps>

      <div class="deploy-content">
        <!-- Step 1: Contract Info -->
        <div v-show="deployStep === 0" class="step-panel">
          <el-form :model="deployForm" label-width="120px">
            <el-form-item label="Contract Name" required>
              <el-input v-model="deployForm.name" placeholder="e.g., CredentialRegistry" />
            </el-form-item>
            <el-form-item label="Contract Type" required>
              <el-select v-model="deployForm.type" style="width: 100%">
                <el-option label="ERC-20 Token" value="erc20" />
                <el-option label="ERC-721 NFT" value="erc721" />
                <el-option label="Access Control" value="access" />
                <el-option label="Credential Registry" value="registry" />
                <el-option label="Custom" value="custom" />
              </el-select>
            </el-form-item>
            <el-form-item label="Network" required>
              <el-select v-model="deployForm.network" style="width: 100%">
                <el-option label="Ethereum Mainnet" value="ethereum" />
                <el-option label="Sepolia Testnet" value="sepolia" />
                <el-option label="Polygon Mainnet" value="polygon" />
                <el-option label="Polygon Mumbai" value="mumbai" />
                <el-option label="BNB Chain" value="bsc" />
              </el-select>
            </el-form-item>
            <el-form-item label="Constructor Args">
              <el-input
                  v-model="deployForm.constructorArgs"
                  type="textarea"
                  :rows="2"
                  placeholder='["arg1", "arg2", 100]'
              />
              <div class="form-hint">JSON array of constructor arguments</div>
            </el-form-item>
            <el-form-item label="Description">
              <el-input v-model="deployForm.description" type="textarea" :rows="2" placeholder="Contract description" />
            </el-form-item>
          </el-form>
        </div>

        <!-- Step 2: ABI and Bytecode -->
        <div v-show="deployStep === 1" class="step-panel">
          <el-form label-width="100px">
            <el-form-item label="Contract ABI">
              <el-input
                  v-model="deployForm.abi"
                  type="textarea"
                  :rows="6"
                  placeholder='[{"inputs":[],"name":"getName","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"}]'
              />
              <div class="form-hint">JSON array of contract ABI</div>
            </el-form-item>
            <el-form-item label="Bytecode">
              <el-input
                  v-model="deployForm.bytecode"
                  type="textarea"
                  :rows="4"
                  placeholder="0x6080604052348015610010..."
              />
              <div class="form-hint">Contract bytecode starting with 0x</div>
            </el-form-item>
          </el-form>
        </div>

        <!-- Step 3: Deploy -->
        <div v-show="deployStep === 2" class="step-panel">
          <div class="deploy-summary">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="Contract Name">{{ deployForm.name || 'Not specified' }}</el-descriptions-item>
              <el-descriptions-item label="Type">{{ formatContractType(deployForm.type) }}</el-descriptions-item>
              <el-descriptions-item label="Network">{{ deployForm.network }}</el-descriptions-item>
              <el-descriptions-item label="Gas Estimate">~{{ estimatedGas }} gas</el-descriptions-item>
            </el-descriptions>
          </div>

          <div class="deploy-warning">
            <el-alert
                title="Deployment Warning"
                type="warning"
                description="Deploying a contract will consume gas fees. Please ensure you have sufficient funds in your wallet."
                show-icon
                :closable="false"
            />
          </div>

          <div class="account-info">
            <div class="info-row">
              <span class="label">Deployer Address:</span>
              <code>{{ deployerAddress }}</code>
              <el-button link size="small" @click="copyAddress(deployerAddress)">Copy</el-button>
            </div>
            <div class="info-row">
              <span class="label">Balance:</span>
              <span>{{ deployerBalance }} ETH</span>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <el-button v-if="deployStep > 0" @click="deployStep--">Back</el-button>
        <el-button v-if="deployStep < 2" type="primary" @click="deployStep++" :disabled="!canProceedDeploy">
          Next
        </el-button>
        <el-button v-if="deployStep === 2" type="success" @click="deployContract" :loading="isDeploying">
          <el-icon><Link /></el-icon>
          Deploy Contract
        </el-button>
        <el-button @click="deployDialog.visible = false">Cancel</el-button>
      </template>
    </el-dialog>

    <!-- Contract View Dialog -->
    <el-dialog v-model="viewDialog.visible" :title="viewDialog.contract?.name" width="800px" class="contract-dialog">
      <div v-if="viewDialog.contract">
        <el-tabs v-model="contractTab">
          <el-tab-pane label="Overview" name="overview">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="Contract Name">{{ viewDialog.contract.name }}</el-descriptions-item>
              <el-descriptions-item label="Type">{{ formatContractType(viewDialog.contract.type) }}</el-descriptions-item>
              <el-descriptions-item label="Address" :span="2">
                <code>{{ viewDialog.contract.address }}</code>
                <el-button link size="small" @click="copyAddress(viewDialog.contract.address)">Copy</el-button>
              </el-descriptions-item>
              <el-descriptions-item label="Network">{{ viewDialog.contract.network }}</el-descriptions-item>
              <el-descriptions-item label="Status">
                <el-tag :type="getStatusTagType(viewDialog.contract.status)">{{ viewDialog.contract.status }}</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="Deployed At">{{ viewDialog.contract.deployedAt }}</el-descriptions-item>
              <el-descriptions-item label="Deployed By">{{ viewDialog.contract.deployedBy }}</el-descriptions-item>
              <el-descriptions-item label="Transaction Hash" :span="2">
                <code>{{ viewDialog.contract.txHash }}</code>
                <el-button link size="small" @click="viewOnExplorer(viewDialog.contract.txHash)">View</el-button>
              </el-descriptions-item>
              <el-descriptions-item label="Description" :span="2">{{ viewDialog.contract.description || 'No description' }}</el-descriptions-item>
            </el-descriptions>
          </el-tab-pane>

          <el-tab-pane label="Read Contract" name="read">
            <div class="read-functions">
              <div v-for="func in readFunctions" :key="func.name" class="function-card">
                <div class="function-header">
                  <span class="function-name">{{ func.name }}</span>
                  <el-button size="small" @click="callReadFunction(func)">Query</el-button>
                </div>
                <div v-if="func.inputs.length > 0" class="function-inputs">
                  <div v-for="input in func.inputs" :key="input.name" class="input-field">
                    <label>{{ input.name }} ({{ input.type }})</label>
                    <el-input v-model="funcInputValues[func.name + input.name]" size="small" :placeholder="'Enter ' + input.name" />
                  </div>
                </div>
                <div v-if="func.result" class="function-result">
                  <span class="result-label">Result:</span>
                  <code>{{ func.result }}</code>
                </div>
              </div>
            </div>
          </el-tab-pane>

          <el-tab-pane label="Write Contract" name="write">
            <div class="write-functions">
              <div v-for="func in writeFunctions" :key="func.name" class="function-card">
                <div class="function-header">
                  <span class="function-name">{{ func.name }}</span>
                  <el-button type="primary" size="small" @click="callWriteFunction(func)">Execute</el-button>
                </div>
                <div v-if="func.inputs.length > 0" class="function-inputs">
                  <div v-for="input in func.inputs" :key="input.name" class="input-field">
                    <label>{{ input.name }} ({{ input.type }})</label>
                    <el-input v-model="writeInputValues[func.name + input.name]" size="small" :placeholder="'Enter ' + input.name" />
                  </div>
                </div>
                <div v-if="func.payable" class="payable-info">
                  <label>Value (ETH):</label>
                  <el-input-number v-model="func.payableValue" :min="0" :step="0.01" size="small" />
                </div>
              </div>
            </div>
          </el-tab-pane>

          <el-tab-pane label="Events" name="events">
            <div class="events-list">
              <div v-for="event in contractEvents" :key="event.name" class="event-card">
                <div class="event-header">
                  <span class="event-name">{{ event.name }}</span>
                  <el-button size="small" @click="subscribeEvent(event)">Subscribe</el-button>
                </div>
                <div class="event-inputs">
                  <div v-for="input in event.inputs" :key="input.name" class="event-param">
                    <span class="param-name">{{ input.name }}:</span>
                    <span class="param-type">{{ input.type }}</span>
                    <span v-if="input.indexed" class="param-indexed">indexed</span>
                  </div>
                </div>
              </div>
            </div>
            <div class="event-logs" v-if="eventLogs.length > 0">
              <h4>Recent Events</h4>
              <div v-for="log in eventLogs" :key="log.id" class="event-log">
                <div class="log-time">{{ log.time }}</div>
                <div class="log-name">{{ log.event }}</div>
                <pre class="log-data">{{ JSON.stringify(log.data, null, 2) }}</pre>
              </div>
            </div>
          </el-tab-pane>

          <el-tab-pane label="Code" name="code">
            <div class="code-viewer">
              <div class="code-header">
                <span>ABI</span>
                <el-button size="small" @click="copyABI">Copy ABI</el-button>
              </div>
              <pre class="code-content">{{ JSON.stringify(viewDialog.contract.abi, null, 2) }}</pre>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-dialog>

    <!-- Interact Dialog -->
    <el-dialog v-model="interactDialog.visible" :title="'Interact with ' + interactDialog.contract?.name" width="600px">
      <div v-if="interactDialog.contract">
        <el-tabs>
          <el-tab-pane label="Read">
            <div class="read-functions">
              <div v-for="func in interactReadFunctions" :key="func.name" class="function-card">
                <div class="function-header">
                  <span class="function-name">{{ func.name }}</span>
                  <el-button size="small" @click="callInteractRead(func)">Query</el-button>
                </div>
                <div v-if="func.result" class="function-result">
                  <span class="result-label">Result:</span>
                  <code>{{ func.result }}</code>
                </div>
              </div>
            </div>
          </el-tab-pane>
          <el-tab-pane label="Write">
            <div class="write-functions">
              <div v-for="func in interactWriteFunctions" :key="func.name" class="function-card">
                <div class="function-header">
                  <span class="function-name">{{ func.name }}</span>
                  <el-button type="primary" size="small" @click="callInteractWrite(func)">Execute</el-button>
                </div>
                <div v-if="func.inputs.length > 0" class="function-inputs">
                  <div v-for="input in func.inputs" :key="input.name" class="input-field">
                    <label>{{ input.name }} ({{ input.type }})</label>
                    <el-input v-model="interactWriteValues[func.name + input.name]" size="small" :placeholder="'Enter ' + input.name" />
                  </div>
                </div>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-dialog>

    <!-- Transaction Dialog -->
    <el-dialog v-model="txDialog.visible" title="Transaction Submitted" width="450px">
      <div class="tx-content">
        <el-icon class="tx-icon" :class="txResult.success ? 'success' : 'error'">
          <component :is="txResult.success ? 'CircleCheck' : 'CircleClose'" />
        </el-icon>
        <h3>{{ txResult.success ? 'Transaction Submitted' : 'Transaction Failed' }}</h3>
        <p>{{ txResult.message }}</p>
        <div v-if="txResult.txHash" class="tx-hash">
          <strong>Transaction Hash:</strong>
          <code>{{ txResult.txHash }}</code>
          <el-button link size="small" @click="viewOnExplorer(txResult.txHash)">View</el-button>
        </div>
      </div>
      <template #footer>
        <el-button @click="txDialog.visible = false">Close</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Plus,
  Upload,
  Refresh,
  Document,
  CircleCheck,
  TrendCharts,
  Connection,
  Search,
  RefreshLeft,
  CopyDocument,
  MoreFilled,
  Link,
  CircleClose
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const tableLoading = ref(false)

const loadingMessages = [
  'Preparing...',
  'Connecting to blockchain...',
  'Loading contract registry...',
  'Almost ready...'
]

// ==================== 类型定义 ====================
interface Contract {
  id: string
  name: string
  address: string
  type: string
  network: string
  status: 'active' | 'paused' | 'deprecated'
  deployedAt: string
  deployedBy: string
  txHash: string
  description: string
  abi: any[]
  bytecode?: string
}

// ==================== 模拟数据 ====================
const stats = reactive({
  totalContracts: 24,
  activeContracts: 18,
  totalTransactions: 1248,
  networkName: 'Ethereum Mainnet'
})

const networkStatus = ref('connected')
const networkName = ref('Ethereum Mainnet')
const chainId = ref('1')
const currentBlock = ref('18,234,567')
const gasPrice = ref('28')

const deployerAddress = ref('0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0')
const deployerBalance = ref('2.45')
const estimatedGas = ref('245,000')

const contracts = ref<Contract[]>([
  {
    id: '1',
    name: 'CredentialRegistry',
    address: '0x1234...5678',
    type: 'registry',
    network: 'Ethereum',
    status: 'active',
    deployedAt: '2024-06-10 14:30:00',
    deployedBy: '0x742d...bEb0',
    txHash: '0x7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2d1e0f9a8b7c6d5e4f3a2b1c0d9e8f7a6b',
    description: 'Verifiable credential registry contract',
    abi: [
      { name: 'getCredential', inputs: [{ name: 'id', type: 'uint256' }], outputs: [{ type: 'string' }], stateMutability: 'view', type: 'function' },
      { name: 'issueCredential', inputs: [{ name: 'to', type: 'address' }, { name: 'hash', type: 'bytes32' }], outputs: [], stateMutability: 'nonpayable', type: 'function' }
    ]
  },
  {
    id: '2',
    name: 'AccessControl',
    address: '0x5678...9012',
    type: 'access',
    network: 'Polygon',
    status: 'active',
    deployedAt: '2024-06-08 09:15:00',
    deployedBy: '0x742d...bEb0',
    txHash: '0x8b7a6c5d4e3f2a1b0c9d8e7f6a5b4c3d2e1f0a9b8c7d6e5f4a3b2c1d0e9f8a7b',
    description: 'Role-based access control contract',
    abi: [
      { name: 'hasRole', inputs: [{ name: 'role', type: 'bytes32' }, { name: 'account', type: 'address' }], outputs: [{ type: 'bool' }], stateMutability: 'view', type: 'function' },
      { name: 'grantRole', inputs: [{ name: 'role', type: 'bytes32' }, { name: 'account', type: 'address' }], outputs: [], stateMutability: 'nonpayable', type: 'function' }
    ]
  },
  {
    id: '3',
    name: 'ESGAnchor',
    address: '0x9012...3456',
    type: 'registry',
    network: 'Ethereum',
    status: 'active',
    deployedAt: '2024-06-05 16:45:00',
    deployedBy: '0x742d...bEb0',
    txHash: '0x9c8b7a6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2d1e0f9a8c',
    description: 'ESG data anchoring contract',
    abi: [
      { name: 'getAnchor', inputs: [{ name: 'id', type: 'uint256' }], outputs: [{ type: 'bytes32' }], stateMutability: 'view', type: 'function' },
      { name: 'anchorData', inputs: [{ name: 'hash', type: 'bytes32' }, { name: 'metadata', type: 'string' }], outputs: [], stateMutability: 'nonpayable', type: 'function' }
    ]
  }
])

const filters = reactive({
  search: '',
  status: '',
  type: ''
})

const pagination = reactive({
  currentPage: 1,
  pageSize: 10,
  total: 0
})

const deployDialog = reactive({
  visible: false
})

const viewDialog = reactive({
  visible: false,
  contract: null as Contract | null
})

const interactDialog = reactive({
  visible: false,
  contract: null as Contract | null
})

const txDialog = reactive({
  visible: false,
  result: { success: false, message: '', txHash: '' }
})

const deployStep = ref(0)
const isDeploying = ref(false)
const contractTab = ref('overview')

const deployForm = reactive({
  name: '',
  type: '',
  network: 'sepolia',
  constructorArgs: '',
  description: '',
  abi: '',
  bytecode: ''
})

const readFunctions = ref<any[]>([])
const writeFunctions = ref<any[]>([])
const contractEvents = ref<any[]>([])
const eventLogs = ref<any[]>([])
const funcInputValues = ref<Record<string, string>>({})
const writeInputValues = ref<Record<string, string>>({})
const interactWriteValues = ref<Record<string, string>>({})
const interactReadFunctions = ref<any[]>([])
const interactWriteFunctions = ref<any[]>([])

// ==================== 计算属性 ====================
const filteredContracts = computed(() => {
  let filtered = [...contracts.value]

  if (filters.search) {
    const searchLower = filters.search.toLowerCase()
    filtered = filtered.filter(c =>
        c.name.toLowerCase().includes(searchLower) ||
        c.address.toLowerCase().includes(searchLower)
    )
  }

  if (filters.status) {
    filtered = filtered.filter(c => c.status === filters.status)
  }

  if (filters.type) {
    filtered = filtered.filter(c => c.type === filters.type)
  }

  pagination.total = filtered.length
  const start = (pagination.currentPage - 1) * pagination.pageSize
  const end = start + pagination.pageSize
  return filtered.slice(start, end)
})

const canProceedDeploy = computed(() => {
  if (deployStep.value === 0) {
    return deployForm.name.trim() !== '' && deployForm.type !== ''
  }
  if (deployStep.value === 1) {
    return deployForm.abi.trim() !== '' && deployForm.bytecode.trim() !== ''
  }
  return true
})

// ==================== 辅助函数 ====================
const formatContractType = (type: string) => {
  const map: Record<string, string> = {
    'erc20': 'ERC-20 Token',
    'erc721': 'ERC-721 NFT',
    'access': 'Access Control',
    'registry': 'Credential Registry',
    'custom': 'Custom'
  }
  return map[type] || type
}

const getStatusTagType = (status: string) => {
  const map: Record<string, string> = {
    'active': 'success',
    'paused': 'warning',
    'deprecated': 'info'
  }
  return map[status] || 'info'
}

const copyAddress = async (address: string) => {
  try {
    await navigator.clipboard.writeText(address)
    ElMessage.success('Address copied to clipboard')
  } catch {
    ElMessage.error('Failed to copy')
  }
}

const viewOnExplorer = (hash: string) => {
  window.open(`https://etherscan.io/tx/${hash}`, '_blank')
}

const handleSearch = () => {
  pagination.currentPage = 1
}

const resetFilters = () => {
  filters.search = ''
  filters.status = ''
  filters.type = ''
  pagination.currentPage = 1
}

const handleSizeChange = (size: number) => {
  pagination.pageSize = size
  pagination.currentPage = 1
}

const handleCurrentChange = (page: number) => {
  pagination.currentPage = page
}

const openDeployDialog = () => {
  deployStep.value = 0
  deployForm.name = ''
  deployForm.type = ''
  deployForm.network = 'sepolia'
  deployForm.constructorArgs = ''
  deployForm.description = ''
  deployForm.abi = ''
  deployForm.bytecode = ''
  deployDialog.visible = true
}

const importContract = () => {
  ElMessage.info('Import contract - select JSON file')
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = '.json'
  input.onchange = (e: any) => {
    if (e.target.files?.[0]) {
      const reader = new FileReader()
      reader.onload = (ev) => {
        try {
          const imported = JSON.parse(ev.target?.result as string)
          if (imported.name && imported.address) {
            contracts.value.unshift({
              ...imported,
              id: String(contracts.value.length + 1),
              deployedAt: new Date().toLocaleString(),
              deployedBy: deployerAddress
            })
            stats.totalContracts++
            ElMessage.success('Contract imported successfully')
          } else {
            ElMessage.error('Invalid contract file')
          }
        } catch {
          ElMessage.error('Failed to parse contract file')
        }
      }
      reader.readAsText(e.target.files[0])
    }
  }
  input.click()
}

const refreshContracts = () => {
  tableLoading.value = true
  setTimeout(() => {
    tableLoading.value = false
    ElMessage.success('Contracts refreshed')
  }, 500)
}

const switchNetwork = () => {
  ElMessage.info('Network switching - would connect to different network')
}

const deployContract = async () => {
  isDeploying.value = true

  await new Promise(resolve => setTimeout(resolve, 3000))

  const newContract: Contract = {
    id: String(contracts.value.length + 1),
    name: deployForm.name,
    address: `0x${Math.random().toString(36).substring(2, 10)}...${Math.random().toString(36).substring(2, 6)}`,
    type: deployForm.type,
    network: deployForm.network === 'sepolia' ? 'Sepolia' : deployForm.network,
    status: 'active',
    deployedAt: new Date().toLocaleString(),
    deployedBy: deployerAddress,
    txHash: `0x${Array.from({ length: 64 }, () => Math.random().toString(16)[2]).join('')}`,
    description: deployForm.description,
    abi: JSON.parse(deployForm.abi || '[]'),
    bytecode: deployForm.bytecode
  }

  contracts.value.unshift(newContract)
  stats.totalContracts++
  stats.activeContracts++

  isDeploying.value = false
  deployDialog.visible = false

  txDialog.result = {
    success: true,
    message: `Contract ${deployForm.name} deployed successfully!`,
    txHash: newContract.txHash
  }
  txDialog.visible = true

  deployForm.name = ''
  deployForm.type = ''
  deployForm.constructorArgs = ''
  deployForm.description = ''
  deployForm.abi = ''
  deployForm.bytecode = ''
  deployStep.value = 0
}

const viewContract = (contract: Contract) => {
  viewDialog.contract = contract

  // Parse functions from ABI
  const functions = contract.abi.filter((item: any) => item.type === 'function')
  readFunctions.value = functions.filter((f: any) => f.stateMutability === 'view' || f.stateMutability === 'pure')
  writeFunctions.value = functions.filter((f: any) => f.stateMutability === 'nonpayable' || f.stateMutability === 'payable')
  contractEvents.value = contract.abi.filter((item: any) => item.type === 'event')

  funcInputValues.value = {}
  writeInputValues.value = {}

  viewDialog.visible = true
}

const interactContract = (contract: Contract) => {
  interactDialog.contract = contract
  const functions = contract.abi.filter((item: any) => item.type === 'function')
  interactReadFunctions.value = functions.filter((f: any) => f.stateMutability === 'view' || f.stateMutability === 'pure')
  interactWriteFunctions.value = functions.filter((f: any) => f.stateMutability === 'nonpayable' || f.stateMutability === 'payable')
  interactWriteValues.value = {}
  interactDialog.visible = true
}

const callReadFunction = async (func: any) => {
  await new Promise(resolve => setTimeout(resolve, 500))
  func.result = `0x${Math.random().toString(36).substring(2, 10)}`
  ElMessage.success(`Called ${func.name}`)
}

const callWriteFunction = async (func: any) => {
  await new Promise(resolve => setTimeout(resolve, 1500))
  const txHash = `0x${Array.from({ length: 64 }, () => Math.random().toString(16)[2]).join('')}`
  txDialog.result = {
    success: true,
    message: `Transaction submitted for ${func.name}`,
    txHash: txHash
  }
  txDialog.visible = true
  ElMessage.success(`Executed ${func.name}`)
}

const callInteractRead = async (func: any) => {
  await new Promise(resolve => setTimeout(resolve, 500))
  func.result = `0x${Math.random().toString(36).substring(2, 10)}`
  ElMessage.success(`Called ${func.name}`)
}

const callInteractWrite = async (func: any) => {
  await new Promise(resolve => setTimeout(resolve, 1500))
  const txHash = `0x${Array.from({ length: 64 }, () => Math.random().toString(16)[2]).join('')}`
  txDialog.result = {
    success: true,
    message: `Transaction submitted for ${func.name}`,
    txHash: txHash
  }
  txDialog.visible = true
  ElMessage.success(`Executed ${func.name}`)
}

const subscribeEvent = (event: any) => {
  ElMessage.success(`Subscribed to ${event.name} events`)
  // Simulate event
  setTimeout(() => {
    eventLogs.value.unshift({
      id: Date.now(),
      time: new Date().toLocaleString(),
      event: event.name,
      data: { param1: 'value1', param2: 'value2' }
    })
  }, 2000)
}

const copyABI = () => {
  if (viewDialog.contract) {
    copyAddress(JSON.stringify(viewDialog.contract.abi))
  }
}

const handleDropdown = (command: string, contract: Contract) => {
  if (command === 'verify') {
    viewOnExplorer(contract.txHash)
  } else if (command === 'export') {
    const data = JSON.stringify({ name: contract.name, abi: contract.abi }, null, 2)
    const blob = new Blob([data], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${contract.name}.json`
    a.click()
    URL.revokeObjectURL(url)
    ElMessage.success('ABI exported')
  } else if (command === 'pause') {
    contract.status = 'paused'
    ElMessage.success(`Contract ${contract.name} paused`)
  } else if (command === 'resume') {
    contract.status = 'active'
    ElMessage.success(`Contract ${contract.name} resumed`)
  }
}

// ==================== 数据加载 ====================
const loadData = () => {
  tableLoading.value = true
  setTimeout(() => {
    tableLoading.value = false
  }, 500)
}

// ==================== 生命周期 ====================
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
      loadData()
    }, 400)
  }, 2000)
})
</script>

<style scoped>
/* ==================== Loading Screen ==================== */
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

/* ==================== Main Content Styles ==================== */
.smart-contracts-page {
  padding: 24px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.page-header h1 {
  margin: 0 0 8px 0;
  font-size: 28px;
  font-weight: 600;
  color: #1f2f3d;
}

.page-header p {
  margin: 0;
  color: #5e6e82;
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

/* Stats Cards */
.stats-row {
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.primary-bg { background-color: #ecf5ff; color: #409eff; }
.success-bg { background-color: #f0f9eb; color: #67c23a; }
.warning-bg { background-color: #fff3e0; color: #e6a23c; }
.info-bg { background-color: #f5f7fa; color: #8c9aab; }

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1f2f3d;
  line-height: 1.2;
}

.stat-label {
  font-size: 13px;
  color: #8c9aab;
  margin-top: 4px;
}

/* Network Status */
.network-status {
  background: white;
  border-radius: 12px;
  padding: 16px 20px;
  margin-bottom: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.status-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.status-indicator.connected {
  background-color: #67c23a;
  box-shadow: 0 0 0 2px rgba(103, 194, 58, 0.2);
}

.status-indicator.disconnected {
  background-color: #f56c6c;
}

.status-right {
  display: flex;
  gap: 24px;
  font-size: 13px;
  color: #5e6e82;
}

/* Filter Bar */
.filter-bar {
  background: white;
  border-radius: 12px;
  padding: 16px 20px;
  margin-bottom: 24px;
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

/* Contracts Table */
.contracts-table-wrapper {
  background: white;
  border-radius: 12px;
  padding: 0;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.address-code, .tx-hash {
  font-family: monospace;
  font-size: 12px;
  background: #f5f7fa;
  padding: 2px 6px;
  border-radius: 4px;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  padding: 16px 20px;
  border-top: 1px solid #ebeef5;
}

/* Deploy Dialog */
.deploy-dialog :deep(.el-dialog__body) {
  max-height: 60vh;
  overflow-y: auto;
}

.form-hint {
  font-size: 11px;
  color: #8c9aab;
  margin-top: 4px;
}

.deploy-summary {
  margin-bottom: 20px;
}

.deploy-warning {
  margin-bottom: 20px;
}

.account-info {
  background: #f5f7fa;
  padding: 16px;
  border-radius: 8px;
}

.info-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
  font-size: 13px;
}

.info-row .label {
  color: #8c9aab;
  width: 120px;
}

/* Contract Dialog */
.contract-dialog :deep(.el-dialog__body) {
  max-height: 65vh;
  overflow-y: auto;
}

.function-card, .event-card {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
}

.function-header, .event-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.function-name, .event-name {
  font-weight: 600;
  font-family: monospace;
  font-size: 14px;
}

.function-inputs, .event-inputs {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #e4e7ed;
}

.input-field, .event-param {
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.input-field label, .event-param .param-name {
  width: 120px;
  font-size: 12px;
  color: #5e6e82;
}

.event-param .param-type {
  font-size: 11px;
  color: #8c9aab;
}

.event-param .param-indexed {
  color: #409eff;
  font-size: 10px;
}

.function-result {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #e4e7ed;
}

.result-label {
  font-weight: 500;
  margin-right: 8px;
}

.payable-info {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  gap: 12px;
}

.event-logs {
  margin-top: 20px;
}

.event-logs h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
}

.event-log {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 12px;
}

.log-time {
  font-size: 11px;
  color: #8c9aab;
  margin-bottom: 4px;
}

.log-name {
  font-weight: 600;
  font-family: monospace;
  margin-bottom: 8px;
}

.log-data {
  font-size: 11px;
  background: white;
  padding: 8px;
  border-radius: 4px;
  overflow-x: auto;
  margin: 0;
}

.code-viewer {
  background: #1e1e2e;
  border-radius: 8px;
  overflow: hidden;
}

.code-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #2d2d3d;
  color: white;
}

.code-content {
  margin: 0;
  padding: 16px;
  font-size: 12px;
  overflow-x: auto;
  max-height: 400px;
}

/* Transaction Dialog */
.tx-content {
  text-align: center;
  padding: 20px;
}

.tx-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.tx-icon.success { color: #67c23a; }
.tx-icon.error { color: #f56c6c; }

.tx-hash {
  margin-top: 16px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 8px;
  word-break: break-all;
}

:deep(.el-table th) {
  background-color: #fafbfc;
  font-weight: 600;
}

:deep(.el-step__title) {
  font-size: 12px;
}
</style>