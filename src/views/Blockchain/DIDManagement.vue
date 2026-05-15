<template>
  <div class="did-management-page">
    <!-- Header -->
    <div class="page-header">
      <div class="header-title">
        <h2>🆔 DID Management</h2>
        <p class="subtitle">Decentralized Identity · Verifiable Credentials · On-Chain Anchoring</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" size="small" @click="refreshData" :loading="refreshing">
          <el-icon><Refresh /></el-icon> Refresh
        </el-button>
        <el-button type="success" size="small" plain @click="showCreateDialog">
          <el-icon><Plus /></el-icon> Register
        </el-button>
      </div>
    </div>

    <!-- Stats Cards - 响应式网格 -->
    <div class="stats-grid">
      <div class="stat-card" v-for="stat in statCards" :key="stat.key">
        <div class="stat-icon" :class="stat.color">{{ stat.icon }}</div>
        <div class="stat-info">
          <div class="stat-number">{{ stats[stat.key] }}</div>
          <div class="stat-label">{{ stat.label }}</div>
        </div>
      </div>
    </div>

    <!-- 主要区域 -->
    <div class="main-layout">
      <!-- 左侧：DID 实体列表（带层次结构） -->
      <div class="left-panel">
        <el-card class="entity-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>📋 DID Entity Hierarchy</span>
              <div class="header-controls">
                <el-input
                    v-model="searchKeyword"
                    placeholder="Search DID or Name"
                    size="small"
                    clearable
                    style="width: 180px"
                    :prefix-icon="Search"
                />
                <el-button size="small" @click="expandAll" text>Expand All</el-button>
                <el-button size="small" @click="collapseAll" text>Collapse All</el-button>
              </div>
            </div>
          </template>

          <!-- 树形表格 - 展示层次结构 -->
          <el-table
              :data="tableData"
              row-key="id"
              :tree-props="{ children: 'children', hasChildren: 'hasChildren' }"
              stripe
              size="small"
              @row-click="viewEntityDetail"
              class="hierarchy-table"
              default-expand-all
          >
            <el-table-column label="Entity" min-width="220" prop="name">
              <template #default="{ row }">
                <div class="entity-cell" :style="{ paddingLeft: (row.level * 24) + 'px' }">
                  <span class="entity-icon">{{ getEntityIcon(row.type) }}</span>
                  <span class="entity-name">{{ row.name }}</span>
                  <el-tag v-if="row.type === 'system'" size="small" type="danger" effect="dark">Root</el-tag>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="DID" min-width="200">
              <template #default="{ row }">
                <span class="mono did-text">{{ shortenDid(row.did) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="Type" width="100">
              <template #default="{ row }">
                <el-tag :type="getTypeTag(row.type)" size="small">{{ row.typeDisplay || row.type }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="Status" width="85">
              <template #default="{ row }">
                <el-tag :type="row.status === 'active' ? 'success' : 'danger'" size="small">
                  {{ row.status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="Balance" width="100">
              <template #default="{ row }">
                <span class="balance">{{ row.balance }} ETH</span>
              </template>
            </el-table-column>
            <el-table-column label="VC" width="70" align="center">
              <template #default="{ row }">
                <el-icon v-if="row.vcId" color="#67c23a"><SuccessFilled /></el-icon>
                <el-icon v-else color="#c0c4cc"><RemoveFilled /></el-icon>
              </template>
            </el-table-column>
            <el-table-column label="Action" width="80" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" size="small" @click.stop="viewEntityDetail(row)">
                  Details
                </el-button>
              </template>
            </el-table-column>
          </el-table>

<!--          <div class="pagination-wrapper">-->
<!--            <el-pagination-->
<!--                v-model:current-page="currentPage"-->
<!--                v-model:page-size="pageSize"-->
<!--                :page-sizes="[10, 20, 50]"-->
<!--                :total="filteredTotal"-->
<!--                layout="total, sizes, prev, pager, next"-->
<!--                small-->
<!--                background-->
<!--            />-->
<!--          </div>-->
        </el-card>
      </div>

      <!-- 右侧面板 -->
      <div class="right-panel">
        <!-- 统计概览卡片 -->
        <el-card class="overview-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>📊 Overview</span>
              <el-tag size="small" type="info">Real-time</el-tag>
            </div>
          </template>
          <div class="overview-stats">
            <div class="overview-item">
              <div class="overview-value">{{ stats.totalEntities }}</div>
              <div class="overview-label">Total Entities</div>
            </div>
            <div class="overview-item">
              <div class="overview-value">{{ stats.hierarchyDepth }}</div>
              <div class="overview-label">Max Depth</div>
            </div>
            <div class="overview-item">
              <div class="overview-value">{{ stats.deviceCount }}</div>
              <div class="overview-label">Devices</div>
            </div>
            <div class="overview-item">
              <div class="overview-value">{{ stats.companyCount }}</div>
              <div class="overview-label">Companies</div>
            </div>
          </div>
        </el-card>

        <!-- VC 凭证列表 -->
        <el-card class="vc-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>📜 Verifiable Credentials</span>
              <el-tag size="small" type="success" effect="light">{{ vcList.length }} issued</el-tag>
            </div>
          </template>
          <div class="vc-list">
            <div v-for="vc in vcList.slice(0, 5)" :key="vc.vcId" class="vc-item" @click="viewVcDetail(vc)">
              <div class="vc-header">
                <span class="vc-icon">📄</span>
                <span class="vc-id">{{ shortenVcId(vc.vcId) }}</span>
                <el-tag :type="vc.status === 'valid' ? 'success' : 'danger'" size="small">{{ vc.status }}</el-tag>
              </div>
              <div class="vc-body">
                <div class="vc-row"><span class="vc-label">Type:</span><span>{{ vc.credentialType }}</span></div>
                <div class="vc-row"><span class="vc-label">Subject:</span><span class="mono">{{ shortenDid(vc.subjectDid) }}</span></div>
                <div class="vc-row"><span class="vc-label">Issued:</span><span>{{ vc.issuedAt }}</span></div>
              </div>
            </div>
            <div v-if="vcList.length > 5" class="view-more" @click="showAllVcDialog = true">
              + {{ vcList.length - 5 }} more credentials
            </div>
            <div v-if="vcList.length === 0" class="empty-placeholder">No VC records</div>
          </div>
        </el-card>

        <!-- 链上锚定记录 -->
        <el-card class="anchor-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>⛓️ On-Chain Anchoring</span>
              <el-tag size="small" type="warning" effect="light">Blockchain Verified</el-tag>
            </div>
          </template>
          <div class="anchor-list">
            <div v-for="record in anchorRecords.slice(0, 4)" :key="record.txHash" class="anchor-item">
              <div class="anchor-icon">🔗</div>
              <div class="anchor-info">
                <div class="anchor-operation">{{ record.operation }}</div>
                <div class="anchor-entity mono">{{ shortenDid(record.entityId) }}</div>
              </div>
              <div class="anchor-meta">
                <div class="anchor-block">#{{ record.blockNumber }}</div>
                <div class="anchor-time">{{ record.timestamp.split(' ')[1] }}</div>
              </div>
            </div>
            <div v-if="anchorRecords.length > 4" class="view-more" @click="showAllAnchorDialog = true">
              + {{ anchorRecords.length - 4 }} more records
            </div>
          </div>
        </el-card>
      </div>
    </div>

    <!-- 实体详情对话框 -->
    <el-dialog v-model="detailDialogVisible" :title="selectedEntity?.name || 'Entity Details'" width="480px" class="detail-dialog">
      <div v-if="selectedEntity" class="entity-detail">
        <div class="detail-header" :class="selectedEntity.type">
          <span class="detail-icon">{{ getEntityIcon(selectedEntity.type) }}</span>
          <div class="detail-title">
            <h3>{{ selectedEntity.name }}</h3>
            <el-tag :type="getTypeTag(selectedEntity.type)" size="small">{{ selectedEntity.typeDisplay || selectedEntity.type }}</el-tag>
          </div>
        </div>
        <el-descriptions :column="1" border size="small">
          <el-descriptions-item label="DID"><span class="mono">{{ selectedEntity.did }}</span></el-descriptions-item>
          <el-descriptions-item label="Status">
            <el-tag :type="selectedEntity.status === 'active' ? 'success' : 'danger'" size="small">{{ selectedEntity.status }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Public Key"><span class="mono">{{ shortenAddress(selectedEntity.publicKey, 12) }}</span></el-descriptions-item>
          <el-descriptions-item label="Balance">{{ selectedEntity.balance }} ETH</el-descriptions-item>
          <el-descriptions-item label="Created At">{{ selectedEntity.createdAt }}</el-descriptions-item>
          <el-descriptions-item label="Parent DID" v-if="selectedEntity.parentDid"><span class="mono">{{ shortenDid(selectedEntity.parentDid) }}</span></el-descriptions-item>
          <el-descriptions-item label="VC Bound" v-if="selectedEntity.vcId"><span class="mono">{{ shortenVcId(selectedEntity.vcId) }}</span></el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>

    <!-- 注册实体对话框 -->
    <el-dialog v-model="createDialogVisible" title="Register New DID Entity" width="420px">
      <el-form :model="newEntity" label-width="100px" size="small">
        <el-form-item label="Entity Name" required>
          <el-input v-model="newEntity.name" placeholder="e.g., New Device" />
        </el-form-item>
        <el-form-item label="Entity Type" required>
          <el-select v-model="newEntity.type" placeholder="Select type" style="width: 100%">
            <el-option label="🏢 Company" value="company" />
            <el-option label="👤 Employee" value="employee" />
            <el-option label="📍 Zone / Area" value="zone" />
            <el-option label="⚙️ Device System" value="systemGroup" />
            <el-option label="📱 IoT Device" value="device" />
          </el-select>
        </el-form-item>
        <el-form-item label="Parent DID">
          <el-select v-model="newEntity.parentDid" placeholder="Select parent entity" clearable filterable style="width: 100%">
            <el-option v-for="entity in parentOptions" :key="entity.did" :label="entity.name" :value="entity.did" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="registerEntity" :loading="registering">Register</el-button>
      </template>
    </el-dialog>

    <!-- 全部VC对话框 -->
    <el-dialog v-model="showAllVcDialog" title="All Verifiable Credentials" width="700px">
      <el-table :data="vcList" stripe size="small" max-height="400">
        <el-table-column prop="vcId" label="VC ID" min-width="200" :formatter="(r) => shortenVcId(r.vcId)" />
        <el-table-column prop="credentialType" label="Type" width="120" />
        <el-table-column prop="subjectDid" label="Subject" min-width="180" :formatter="(r) => shortenDid(r.subjectDid)" />
        <el-table-column prop="issuedAt" label="Issued" width="140" />
        <el-table-column label="Status" width="80">
          <template #default="{ row }"><el-tag :type="row.status === 'valid' ? 'success' : 'danger'" size="small">{{ row.status }}</el-tag></template>
        </el-table-column>
      </el-table>
    </el-dialog>

    <!-- 全部锚定记录对话框 -->
    <el-dialog v-model="showAllAnchorDialog" title="All On-Chain Anchoring Records" width="800px">
      <el-table :data="anchorRecords" stripe size="small" max-height="400">
        <el-table-column prop="operation" label="Operation" width="120" />
        <el-table-column prop="entityId" label="Entity ID" min-width="200" :formatter="(r) => shortenDid(r.entityId)" />
        <el-table-column prop="txHash" label="Tx Hash" min-width="220" :formatter="(r) => shortenAddress(r.txHash, 12)" />
        <el-table-column prop="blockNumber" label="Block" width="80" />
        <el-table-column prop="timestamp" label="Time" width="150" />
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, Plus, Search, SuccessFilled, RemoveFilled } from '@element-plus/icons-vue'

// ============ 统计数据 ============
const stats = ref({
  totalEntities: 14,
  totalVCs: 7,
  totalAnchors: 6,
  activeEntities: 14,
  hierarchyDepth: 4,
  deviceCount: 5,
  companyCount: 2
})

const statCards = [
  { key: 'totalEntities', icon: '🆔', color: 'blue', label: 'Total DID Entities' },
  { key: 'totalVCs', icon: '📜', color: 'green', label: 'VCs Issued' },
  { key: 'totalAnchors', icon: '🔗', color: 'orange', label: 'On-Chain Anchors' },
  { key: 'activeEntities', icon: '✅', color: 'purple', label: 'Active Entities' }
]

// ============ 层次化数据（树形结构）============
interface EntityNode {
  id: number
  name: string
  did: string
  type: string
  typeDisplay: string
  status: string
  balance: string
  publicKey: string
  createdAt: string
  vcId: string | null
  parentDid: string | null
  level: number
  children?: EntityNode[]
}

const buildHierarchyData = (): EntityNode[] => {
  const flatData: any[] = [
    // ========== 系统根 ==========
    { id: 1, name: 'IMBS System Root', did: 'did:imbs:system:root', type: 'system', typeDisplay: 'System Root', status: 'active', balance: '500.00', publicKey: '0x9AA128582b17C0c0143690F24012C8DBCf24767f', createdAt: '2025-01-01 00:00:00', vcId: null, parentDid: null, level: 0 },

    // ========== 公司 A：IMBS Technology ==========
    { id: 2, name: 'IMBS Technology Co., Ltd.', did: 'did:imbs:company:tech', type: 'company', typeDisplay: 'Company', status: 'active', balance: '200.00', publicKey: '0x7f3a4BA632Bc3a88a9c3489613b1CF529C8371Ca', createdAt: '2025-01-15 10:30:00', vcId: 'vc:imbs:company:tech:001', parentDid: 'did:imbs:system:root', level: 1 },

    // 公司A - 上海总部区域
    { id: 3, name: 'Shanghai HQ - 1F Lobby', did: 'did:imbs:zone:shanghai_1f', type: 'zone', typeDisplay: 'Zone', status: 'active', balance: '15.00', publicKey: '0x1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r', createdAt: '2025-02-10 09:00:00', vcId: null, parentDid: 'did:imbs:company:tech', level: 2 },
    { id: 4, name: 'Shanghai HQ - 2F Office', did: 'did:imbs:zone:shanghai_2f', type: 'zone', typeDisplay: 'Zone', status: 'active', balance: '12.00', publicKey: '0x2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s', createdAt: '2025-02-10 09:15:00', vcId: null, parentDid: 'did:imbs:company:tech', level: 2 },
    { id: 5, name: 'Shanghai HQ - 3F R&D Center', did: 'did:imbs:zone:shanghai_3f', type: 'zone', typeDisplay: 'Zone', status: 'active', balance: '18.00', publicKey: '0x3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t', createdAt: '2025-02-10 09:30:00', vcId: null, parentDid: 'did:imbs:company:tech', level: 2 },
    { id: 6, name: 'Shanghai HQ - B1 Parking', did: 'did:imbs:zone:shanghai_b1', type: 'zone', typeDisplay: 'Zone', status: 'active', balance: '5.00', publicKey: '0x4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t1u', createdAt: '2025-02-10 10:00:00', vcId: null, parentDid: 'did:imbs:company:tech', level: 2 },

    // 1F 区域 - 设备系统
    { id: 7, name: '1F Access Control System', did: 'did:imbs:system:access_1f', type: 'systemGroup', typeDisplay: 'Device System', status: 'active', balance: '3.00', publicKey: '0x5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t1u2v', createdAt: '2025-02-20 08:00:00', vcId: null, parentDid: 'did:imbs:zone:shanghai_1f', level: 3 },
    { id: 8, name: '️1F HVAC System', did: 'did:imbs:system:hvac_1f', type: 'systemGroup', typeDisplay: 'Device System', status: 'active', balance: '4.00', publicKey: '0x6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t1u2v3w', createdAt: '2025-02-20 08:30:00', vcId: null, parentDid: 'did:imbs:zone:shanghai_1f', level: 3 },
    { id: 9, name: '1F Lighting System', did: 'did:imbs:system:lighting_1f', type: 'systemGroup', typeDisplay: 'Device System', status: 'active', balance: '2.50', publicKey: '0x7g8h9i0j1k2l3m4n5o6p7q8r9s0t1u2v3w4x', createdAt: '2025-02-20 09:00:00', vcId: null, parentDid: 'did:imbs:zone:shanghai_1f', level: 3 },

    // 1F 设备
    { id: 10, name: 'Main Entrance Camera', did: 'did:imbs:device:camera_main', type: 'device', typeDisplay: 'IoT Device', status: 'active', balance: '0.10', publicKey: '0x8h9i0j1k2l3m4n5o6p7q8r9s0t1u2v3w4x5y', createdAt: '2025-03-01 10:00:00', vcId: 'vc:imbs:device:camera_main', parentDid: 'did:imbs:system:access_1f', level: 4 },
    { id: 11, name: '1F Card Reader #01', did: 'did:imbs:device:reader_101', type: 'device', typeDisplay: 'IoT Device', status: 'active', balance: '0.05', publicKey: '0x9i0j1k2l3m4n5o6p7q8r9s0t1u2v3w4x5y6z', createdAt: '2025-03-01 10:15:00', vcId: 'vc:imbs:device:reader_101', parentDid: 'did:imbs:system:access_1f', level: 4 },
    { id: 12, name: '1F Card Reader #02', did: 'did:imbs:device:reader_102', type: 'device', typeDisplay: 'IoT Device', status: 'active', balance: '0.05', publicKey: '0x0j1k2l3m4n5o6p7q8r9s0t1u2v3w4x5y6z7a', createdAt: '2025-03-01 10:30:00', vcId: null, parentDid: 'did:imbs:system:access_1f', level: 4 },
    { id: 13, name: '1F Temperature Sensor #01', did: 'did:imbs:device:temp_101', type: 'device', typeDisplay: 'IoT Device', status: 'active', balance: '0.08', publicKey: '0x1k2l3m4n5o6p7q8r9s0t1u2v3w4x5y6z7a8b', createdAt: '2025-03-02 09:00:00', vcId: 'vc:imbs:device:temp_101', parentDid: 'did:imbs:system:hvac_1f', level: 4 },
    { id: 14, name: '1F Humidity Sensor', did: 'did:imbs:device:humi_101', type: 'device', typeDisplay: 'IoT Device', status: 'active', balance: '0.08', publicKey: '0x2l3m4n5o6p7q8r9s0t1u2v3w4x5y6z7a8b9c', createdAt: '2025-03-02 09:15:00', vcId: null, parentDid: 'did:imbs:system:hvac_1f', level: 4 },
    { id: 15, name: '1F Smart Light #01', did: 'did:imbs:device:light_101', type: 'device', typeDisplay: 'IoT Device', status: 'active', balance: '0.03', publicKey: '0x3m4n5o6p7q8r9s0t1u2v3w4x5y6z7a8b9c0d', createdAt: '2025-03-03 11:00:00', vcId: null, parentDid: 'did:imbs:system:lighting_1f', level: 4 },
    { id: 16, name: '1F Smart Light #02', did: 'did:imbs:device:light_102', type: 'device', typeDisplay: 'IoT Device', status: 'active', balance: '0.03', publicKey: '0x4n5o6p7q8r9s0t1u2v3w4x5y6z7a8b9c0d1e', createdAt: '2025-03-03 11:15:00', vcId: null, parentDid: 'did:imbs:system:lighting_1f', level: 4 },
    { id: 17, name: '1F Smart Light #03', did: 'did:imbs:device:light_103', type: 'device', typeDisplay: 'IoT Device', status: 'active', balance: '0.03', publicKey: '0x5o6p7q8r9s0t1u2v3w4x5y6z7a8b9c0d1e2f', createdAt: '2025-03-03 11:30:00', vcId: null, parentDid: 'did:imbs:system:lighting_1f', level: 4 },

    // 2F 区域 - 设备系统
    { id: 18, name: '2F Access Control System', did: 'did:imbs:system:access_2f', type: 'systemGroup', typeDisplay: 'Device System', status: 'active', balance: '2.50', publicKey: '0x6p7q8r9s0t1u2v3w4x5y6z7a8b9c0d1e2f3g', createdAt: '2025-02-21 08:00:00', vcId: null, parentDid: 'did:imbs:zone:shanghai_2f', level: 3 },
    { id: 19, name: '2F HVAC System', did: 'did:imbs:system:hvac_2f', type: 'systemGroup', typeDisplay: 'Device System', status: 'active', balance: '3.50', publicKey: '0x7q8r9s0t1u2v3w4x5y6z7a8b9c0d1e2f3g4h', createdAt: '2025-02-21 08:30:00', vcId: null, parentDid: 'did:imbs:zone:shanghai_2f', level: 3 },
    { id: 20, name: '2F Lighting System', did: 'did:imbs:system:lighting_2f', type: 'systemGroup', typeDisplay: 'Device System', status: 'active', balance: '2.00', publicKey: '0x8r9s0t1u2v3w4x5y6z7a8b9c0d1e2f3g4h5i', createdAt: '2025-02-21 09:00:00', vcId: null, parentDid: 'did:imbs:zone:shanghai_2f', level: 3 },

    // 2F 设备
    { id: 21, name: '2F Card Reader #01', did: 'did:imbs:device:reader_201', type: 'device', typeDisplay: 'IoT Device', status: 'active', balance: '0.05', publicKey: '0x9s0t1u2v3w4x5y6z7a8b9c0d1e2f3g4h5i6j', createdAt: '2025-03-04 10:00:00', vcId: 'vc:imbs:device:reader_201', parentDid: 'did:imbs:system:access_2f', level: 4 },
    { id: 22, name: '2F Card Reader #02', did: 'did:imbs:device:reader_202', type: 'device', typeDisplay: 'IoT Device', status: 'active', balance: '0.05', publicKey: '0x0t1u2v3w4x5y6z7a8b9c0d1e2f3g4h5i6j7k', createdAt: '2025-03-04 10:15:00', vcId: null, parentDid: 'did:imbs:system:access_2f', level: 4 },
    { id: 23, name: '2F Temperature Sensor #01', did: 'did:imbs:device:temp_201', type: 'device', typeDisplay: 'IoT Device', status: 'active', balance: '0.08', publicKey: '0x1u2v3w4x5y6z7a8b9c0d1e2f3g4h5i6j7k8l', createdAt: '2025-03-05 09:00:00', vcId: null, parentDid: 'did:imbs:system:hvac_2f', level: 4 },
    { id: 24, name: '2F Temperature Sensor #02', did: 'did:imbs:device:temp_202', type: 'device', typeDisplay: 'IoT Device', status: 'active', balance: '0.08', publicKey: '0x2v3w4x5y6z7a8b9c0d1e2f3g4h5i6j7k8l9m', createdAt: '2025-03-05 09:15:00', vcId: null, parentDid: 'did:imbs:system:hvac_2f', level: 4 },
    { id: 25, name: '2F Smart Light #01', did: 'did:imbs:device:light_201', type: 'device', typeDisplay: 'IoT Device', status: 'active', balance: '0.03', publicKey: '0x3w4x5y6z7a8b9c0d1e2f3g4h5i6j7k8l9m0n', createdAt: '2025-03-06 11:00:00', vcId: null, parentDid: 'did:imbs:system:lighting_2f', level: 4 },
    { id: 26, name: '2F Smart Light #02', did: 'did:imbs:device:light_202', type: 'device', typeDisplay: 'IoT Device', status: 'active', balance: '0.03', publicKey: '0x4x5y6z7a8b9c0d1e2f3g4h5i6j7k8l9m0n1o', createdAt: '2025-03-06 11:15:00', vcId: null, parentDid: 'did:imbs:system:lighting_2f', level: 4 },

    // 3F 区域 - 设备系统
    { id: 27, name: '3F R&D Lab System', did: 'did:imbs:system:lab_3f', type: 'systemGroup', typeDisplay: 'Device System', status: 'active', balance: '8.00', publicKey: '0x5y6z7a8b9c0d1e2f3g4h5i6j7k8l9m0n1o2p', createdAt: '2025-02-22 10:00:00', vcId: null, parentDid: 'did:imbs:zone:shanghai_3f', level: 3 },
    { id: 28, name: '3F HVAC System', did: 'did:imbs:system:hvac_3f', type: 'systemGroup', typeDisplay: 'Device System', status: 'active', balance: '4.00', publicKey: '0x6z7a8b9c0d1e2f3g4h5i6j7k8l9m0n1o2p3q', createdAt: '2025-02-22 10:30:00', vcId: null, parentDid: 'did:imbs:zone:shanghai_3f', level: 3 },

    // 3F 设备
    { id: 29, name: 'ab Equipment #01', did: 'did:imbs:device:lab_301', type: 'device', typeDisplay: 'IoT Device', status: 'active', balance: '0.50', publicKey: '0x7a8b9c0d1e2f3g4h5i6j7k8l9m0n1o2p3q4r', createdAt: '2025-03-07 14:00:00', vcId: 'vc:imbs:device:lab_301', parentDid: 'did:imbs:system:lab_3f', level: 4 },
    { id: 30, name: 'ab Equipment #02', did: 'did:imbs:device:lab_302', type: 'device', typeDisplay: 'IoT Device', status: 'active', balance: '0.50', publicKey: '0x8b9c0d1e2f3g4h5i6j7k8l9m0n1o2p3q4r5s', createdAt: '2025-03-07 14:15:00', vcId: null, parentDid: 'did:imbs:system:lab_3f', level: 4 },
    { id: 31, name: '3F Temp/Humidity Sensor', did: 'did:imbs:device:env_301', type: 'device', typeDisplay: 'IoT Device', status: 'active', balance: '0.08', publicKey: '0x9c0d1e2f3g4h5i6j7k8l9m0n1o2p3q4r5s6t', createdAt: '2025-03-08 09:00:00', vcId: null, parentDid: 'did:imbs:system:hvac_3f', level: 4 },

    // B1 区域 - 设备
    { id: 32, name: 'B1 Parking System', did: 'did:imbs:system:parking_b1', type: 'systemGroup', typeDisplay: 'Device System', status: 'active', balance: '3.00', publicKey: '0x0d1e2f3g4h5i6j7k8l9m0n1o2p3q4r5s6t7u', createdAt: '2025-02-23 09:00:00', vcId: null, parentDid: 'did:imbs:zone:shanghai_b1', level: 3 },
    { id: 33, name: 'Parking Gate Barrier', did: 'did:imbs:device:barrier_b1', type: 'device', typeDisplay: 'IoT Device', status: 'active', balance: '0.20', publicKey: '0x1e2f3g4h5i6j7k8l9m0n1o2p3q4r5s6t7u8v', createdAt: '2025-03-09 10:00:00', vcId: 'vc:imbs:device:barrier_b1', parentDid: 'did:imbs:system:parking_b1', level: 4 },
    { id: 34, name: 'Parking Camera #01', did: 'did:imbs:device:park_cam_01', type: 'device', typeDisplay: 'IoT Device', status: 'active', balance: '0.10', publicKey: '0x2f3g4h5i6j7k8l9m0n1o2p3q4r5s6t7u8v9w', createdAt: '2025-03-09 10:30:00', vcId: null, parentDid: 'did:imbs:system:parking_b1', level: 4 },

    // ========== 公司 B：IMBS Energy Solutions（工厂） ==========
    { id: 35, name: 'IMBS Energy Solutions', did: 'did:imbs:company:energy', type: 'company', typeDisplay: 'Company', status: 'active', balance: '150.00', publicKey: '0x0a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r', createdAt: '2025-01-20 10:00:00', vcId: 'vc:imbs:company:energy:001', parentDid: 'did:imbs:system:root', level: 1 },

    // 工厂 - 东区厂房
    { id: 36, name: 'East Factory - Production Line A', did: 'did:imbs:zone:east_line_a', type: 'zone', typeDisplay: 'Zone', status: 'active', balance: '20.00', publicKey: '0x3g4h5i6j7k8l9m0n1o2p3q4r5s6t7u8v9w0x', createdAt: '2025-02-15 09:00:00', vcId: null, parentDid: 'did:imbs:company:energy', level: 2 },
    { id: 37, name: 'East Factory - Production Line B', did: 'did:imbs:zone:east_line_b', type: 'zone', typeDisplay: 'Zone', status: 'active', balance: '18.00', publicKey: '0x4h5i6j7k8l9m0n1o2p3q4r5s6t7u8v9w0x1y', createdAt: '2025-02-15 09:15:00', vcId: null, parentDid: 'did:imbs:company:energy', level: 2 },
    { id: 38, name: 'West Factory - Warehouse', did: 'did:imbs:zone:west_warehouse', type: 'zone', typeDisplay: 'Zone', status: 'active', balance: '12.00', publicKey: '0x5i6j7k8l9m0n1o2p3q4r5s6t7u8v9w0x1y2z', createdAt: '2025-02-16 10:00:00', vcId: null, parentDid: 'did:imbs:company:energy', level: 2 },

    // 东区 A线 - 设备系统
    { id: 39, name: 'Production Line A Control', did: 'did:imbs:system:prod_line_a', type: 'systemGroup', typeDisplay: 'Device System', status: 'active', balance: '10.00', publicKey: '0x6j7k8l9m0n1o2p3q4r5s6t7u8v9w0x1y2z3a', createdAt: '2025-02-25 08:00:00', vcId: null, parentDid: 'did:imbs:zone:east_line_a', level: 3 },
    { id: 40, name: 'East Factory HVAC System', did: 'did:imbs:system:hvac_east', type: 'systemGroup', typeDisplay: 'Device System', status: 'active', balance: '6.00', publicKey: '0x7k8l9m0n1o2p3q4r5s6t7u8v9w0x1y2z3a4b', createdAt: '2025-02-25 09:00:00', vcId: null, parentDid: 'did:imbs:zone:east_line_a', level: 3 },

    // 东区 A线 - 设备
    { id: 41, name: 'Robot Arm #01', did: 'did:imbs:device:robot_a01', type: 'device', typeDisplay: 'IoT Device', status: 'active', balance: '1.00', publicKey: '0x8l9m0n1o2p3q4r5s6t7u8v9w0x1y2z3a4b5c', createdAt: '2025-03-10 08:00:00', vcId: 'vc:imbs:device:robot_a01', parentDid: 'did:imbs:system:prod_line_a', level: 4 },
    { id: 42, name: 'Robot Arm #02', did: 'did:imbs:device:robot_a02', type: 'device', typeDisplay: 'IoT Device', status: 'active', balance: '1.00', publicKey: '0x9m0n1o2p3q4r5s6t7u8v9w0x1y2z3a4b5c6d', createdAt: '2025-03-10 08:15:00', vcId: null, parentDid: 'did:imbs:system:prod_line_a', level: 4 },
    { id: 43, name: 'Conveyor Belt #01', did: 'did:imbs:device:conveyor_a01', type: 'device', typeDisplay: 'IoT Device', status: 'active', balance: '0.60', publicKey: '0x0n1o2p3q4r5s6t7u8v9w0x1y2z3a4b5c6d7e', createdAt: '2025-03-10 08:30:00', vcId: null, parentDid: 'did:imbs:system:prod_line_a', level: 4 },
    { id: 44, name: 'Conveyor Belt #02', did: 'did:imbs:device:conveyor_a02', type: 'device', typeDisplay: 'IoT Device', status: 'active', balance: '0.60', publicKey: '0x1o2p3q4r5s6t7u8v9w0x1y2z3a4b5c6d7e8f', createdAt: '2025-03-10 08:45:00', vcId: null, parentDid: 'did:imbs:system:prod_line_a', level: 4 },
    { id: 45, name: 'Power Monitor #01', did: 'did:imbs:device:power_a01', type: 'device', typeDisplay: 'IoT Device', status: 'active', balance: '0.30', publicKey: '0x2p3q4r5s6t7u8v9w0x1y2z3a4b5c6d7e8f9g', createdAt: '2025-03-11 09:00:00', vcId: 'vc:imbs:device:power_a01', parentDid: 'did:imbs:system:prod_line_a', level: 4 },

    // 东区 B线 - 设备系统
    { id: 46, name: '⚙Production Line B Control', did: 'did:imbs:system:prod_line_b', type: 'systemGroup', typeDisplay: 'Device System', status: 'active', balance: '9.00', publicKey: '0x3q4r5s6t7u8v9w0x1y2z3a4b5c6d7e8f9g0h', createdAt: '2025-02-26 08:00:00', vcId: null, parentDid: 'did:imbs:zone:east_line_b', level: 3 },

    // 东区 B线 - 设备
    { id: 47, name: 'Robot Arm #B01', did: 'did:imbs:device:robot_b01', type: 'device', typeDisplay: 'IoT Device', status: 'active', balance: '1.00', publicKey: '0x4r5s6t7u8v9w0x1y2z3a4b5c6d7e8f9g0h1i', createdAt: '2025-03-12 08:00:00', vcId: 'vc:imbs:device:robot_b01', parentDid: 'did:imbs:system:prod_line_b', level: 4 },
    { id: 48, name: 'Robot Arm #B02', did: 'did:imbs:device:robot_b02', type: 'device', typeDisplay: 'IoT Device', status: 'active', balance: '1.00', publicKey: '0x5s6t7u8v9w0x1y2z3a4b5c6d7e8f9g0h1i2j', createdAt: '2025-03-12 08:15:00', vcId: null, parentDid: 'did:imbs:system:prod_line_b', level: 4 },
    { id: 49, name: 'Conveyor Belt #B01', did: 'did:imbs:device:conveyor_b01', type: 'device', typeDisplay: 'IoT Device', status: 'active', balance: '0.60', publicKey: '0x6t7u8v9w0x1y2z3a4b5c6d7e8f9g0h1i2j3k', createdAt: '2025-03-12 08:30:00', vcId: null, parentDid: 'did:imbs:system:prod_line_b', level: 4 },
    { id: 50, name: 'Power Monitor #B01', did: 'did:imbs:device:power_b01', type: 'device', typeDisplay: 'IoT Device', status: 'active', balance: '0.30', publicKey: '0x7u8v9w0x1y2z3a4b5c6d7e8f9g0h1i2j3k4l', createdAt: '2025-03-13 09:00:00', vcId: null, parentDid: 'did:imbs:system:prod_line_b', level: 4 },

    // 西区仓库 - 设备
    { id: 51, name: 'Warehouse Management System', did: 'did:imbs:system:warehouse_west', type: 'systemGroup', typeDisplay: 'Device System', status: 'active', balance: '5.00', publicKey: '0x8v9w0x1y2z3a4b5c6d7e8f9g0h1i2j3k4l5m', createdAt: '2025-02-27 09:00:00', vcId: null, parentDid: 'did:imbs:zone:west_warehouse', level: 3 },
    { id: 52, name: 'Warehouse Camera #01', did: 'did:imbs:device:wh_cam_01', type: 'device', typeDisplay: 'IoT Device', status: 'active', balance: '0.10', publicKey: '0x9w0x1y2z3a4b5c6d7e8f9g0h1i2j3k4l5m6n', createdAt: '2025-03-14 10:00:00', vcId: 'vc:imbs:device:wh_cam_01', parentDid: 'did:imbs:system:warehouse_west', level: 4 },
    { id: 53, name: 'Warehouse Camera #02', did: 'did:imbs:device:wh_cam_02', type: 'device', typeDisplay: 'IoT Device', status: 'active', balance: '0.10', publicKey: '0x0x1y2z3a4b5c6d7e8f9g0h1i2j3k4l5m6n7o', createdAt: '2025-03-14 10:15:00', vcId: null, parentDid: 'did:imbs:system:warehouse_west', level: 4 },
    { id: 54, name: 'Warehouse Power Meter', did: 'did:imbs:device:wh_power', type: 'device', typeDisplay: 'IoT Device', status: 'active', balance: '0.25', publicKey: '0x1y2z3a4b5c6d7e8f9g0h1i2j3k4l5m6n7o8p', createdAt: '2025-03-15 11:00:00', vcId: null, parentDid: 'did:imbs:system:warehouse_west', level: 4 },
    { id: 55, name: 'Warehouse Gate Control', did: 'did:imbs:device:wh_gate', type: 'device', typeDisplay: 'IoT Device', status: 'active', balance: '0.15', publicKey: '0x2z3a4b5c6d7e8f9g0h1i2j3k4l5m6n7o8p9q', createdAt: '2025-03-15 11:30:00', vcId: null, parentDid: 'did:imbs:system:warehouse_west', level: 4 }
  ]

  const buildTree = (items: any[], parentDid: string | null = null): any[] => {
    return items
        .filter(item => item.parentDid === parentDid)
        .map(item => ({ ...item, children: buildTree(items, item.did) }))
        .sort((a, b) => {
          const order: Record<string, number> = { system: 0, company: 1, zone: 2, systemGroup: 3, employee: 4, device: 5 }
          return (order[a.type] || 99) - (order[b.type] || 99)
        })
  }

  return buildTree(flatData, null)
}

const tableData = ref<EntityNode[]>(buildHierarchyData())

// VC 列表
const vcList = ref([
  { vcId: 'vc:imbs:company:a:001', issuerDid: 'did:imbs:system:root', subjectDid: 'did:imbs:company:a', credentialType: 'CompanyCredential', issuedAt: '2025-01-15 10:30:00', expiresAt: '2026-01-15', status: 'valid' },
  { vcId: 'vc:imbs:alice:001', issuerDid: 'did:imbs:company:a', subjectDid: 'did:imbs:employee:alice', credentialType: 'EmployeeCredential', issuedAt: '2025-02-01 09:00:00', expiresAt: '2026-02-01', status: 'valid' },
  { vcId: 'vc:imbs:bob:001', issuerDid: 'did:imbs:company:a', subjectDid: 'did:imbs:employee:bob', credentialType: 'EmployeeCredential', issuedAt: '2025-02-10 14:20:00', expiresAt: '2026-02-10', status: 'valid' },
  { vcId: 'vc:imbs:device:gate_001', issuerDid: 'did:imbs:system:gate', subjectDid: 'did:imbs:device:gate_camera_01', credentialType: 'DeviceCredential', issuedAt: '2025-03-10 10:00:00', expiresAt: '2026-03-10', status: 'valid' },
  { vcId: 'vc:imbs:hvac:001', issuerDid: 'did:imbs:system:hvac', subjectDid: 'did:imbs:device:hvac_001', credentialType: 'DeviceCredential', issuedAt: '2025-03-12 14:00:00', expiresAt: '2026-03-12', status: 'valid' },
  { vcId: 'vc:imbs:company:b:001', issuerDid: 'did:imbs:system:root', subjectDid: 'did:imbs:company:b', credentialType: 'CompanyCredential', issuedAt: '2025-01-20 10:00:00', expiresAt: '2026-01-20', status: 'valid' },
  { vcId: 'vc:imbs:solar:001', issuerDid: 'did:imbs:system:solar', subjectDid: 'did:imbs:device:solar_001', credentialType: 'DeviceCredential', issuedAt: '2025-03-20 08:00:00', expiresAt: '2026-03-20', status: 'valid' }
])

// 锚定记录
const anchorRecords = ref([
  { operation: 'DID Registration', entityId: 'did:imbs:company:a', txHash: '0x1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p', blockNumber: 124, timestamp: '2025-01-15 10:35:00' },
  { operation: 'VC Issuance', entityId: 'vc:imbs:alice:001', txHash: '0x2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q', blockNumber: 129, timestamp: '2025-02-01 09:05:00' },
  { operation: 'Device Registration', entityId: 'did:imbs:device:gate_camera_01', txHash: '0x3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r', blockNumber: 135, timestamp: '2025-03-10 10:05:00' },
  { operation: 'VC Issuance', entityId: 'vc:imbs:device:gate_001', txHash: '0x4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s', blockNumber: 136, timestamp: '2025-03-10 10:10:00' },
  { operation: 'DID Registration', entityId: 'did:imbs:company:b', txHash: '0x5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t', blockNumber: 142, timestamp: '2025-01-20 10:05:00' },
  { operation: 'Device Registration', entityId: 'did:imbs:device:solar_001', txHash: '0x6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t1u', blockNumber: 148, timestamp: '2025-03-20 08:05:00' }
])

// 搜索和分页
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(10)

const filteredTotal = computed(() => {
  if (!searchKeyword.value) return flattenData.value.length
  const keyword = searchKeyword.value.toLowerCase()
  return flattenData.value.filter(e => e.name.toLowerCase().includes(keyword) || e.did.toLowerCase().includes(keyword)).length
})

const flattenData = computed(() => {
  const flatten = (nodes: EntityNode[]): EntityNode[] => {
    let result: EntityNode[] = []
    for (const node of nodes) {
      result.push(node)
      if (node.children) result = result.concat(flatten(node.children))
    }
    return result
  }
  return flatten(tableData.value)
})

const parentOptions = computed(() => flattenData.value.filter(e => e.type !== 'device' && e.type !== 'employee'))

// 对话框状态
const detailDialogVisible = ref(false)
const selectedEntity = ref<any>(null)
const createDialogVisible = ref(false)
const registering = ref(false)
const refreshing = ref(false)
const showAllVcDialog = ref(false)
const showAllAnchorDialog = ref(false)

const newEntity = ref({ name: '', type: 'device', parentDid: '' })

// 辅助函数
const shortenDid = (did: string) => {
  if (!did) return ''
  if (did.length <= 24) return did
  return `${did.slice(0, 20)}...${did.slice(-8)}`
}

const shortenAddress = (addr: string, len = 6) => addr ? `${addr.slice(0, len)}...${addr.slice(-4)}` : ''
const shortenVcId = (vcId: string) => vcId?.length > 28 ? `${vcId.slice(0, 24)}...` : vcId || ''

const getEntityIcon = (type: string) => {
  const icons: Record<string, string> = { system: '🏛️', company: '🏢', employee: '👤', zone: '📍', systemGroup: '⚙️', device: '📱' }
  return icons[type] || '🔗'
}

const getTypeTag = (type: string) => {
  const types: Record<string, string> = { system: 'danger', company: 'warning', employee: 'info', zone: 'success', systemGroup: 'primary', device: 'info' }
  return types[type] || 'info'
}

const expandAll = () => { /* 树形表格展开逻辑 */ }
const collapseAll = () => { /* 树形表格收起逻辑 */ }

const viewEntityDetail = (entity: any) => { selectedEntity.value = entity; detailDialogVisible.value = true }
const viewVcDetail = (vc: any) => ElMessage.info(`VC: ${vc.vcId}`)

const showCreateDialog = () => { newEntity.value = { name: '', type: 'device', parentDid: '' }; createDialogVisible.value = true }

const registerEntity = async () => {
  if (!newEntity.value.name) { ElMessage.warning('Please enter entity name'); return }
  registering.value = true
  await new Promise(resolve => setTimeout(resolve, 1500))
  ElMessage.success(`Entity "${newEntity.value.name}" registered!`)
  registering.value = false
  createDialogVisible.value = false
}

const refreshData = async () => {
  refreshing.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  ElMessage.success('Data refreshed')
  refreshing.value = false
}

onMounted(() => console.log('DID Management Page Loaded'))
</script>

<style scoped>
.did-management-page {
  background: #f5f7fa;
  min-height: 100vh;
  padding: 16px;
}

/* Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
}

.header-title h2 { margin: 0 0 4px; font-size: 22px; color: #1e293b; }
.subtitle { font-size: 12px; color: #64748b; margin: 0; }
.header-actions { display: flex; gap: 10px; }

/* Stats Grid - 响应式 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 14px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.08);
  transition: transform 0.2s;
}
.stat-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.1); }

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}
.stat-icon.blue { background: #dbeafe; }
.stat-icon.green { background: #dcfce7; }
.stat-icon.orange { background: #ffedd5; }
.stat-icon.purple { background: #ede9fe; }

.stat-number { font-size: 24px; font-weight: 700; color: #1e293b; }
.stat-label { font-size: 11px; color: #64748b; margin-top: 4px; }

/* 主布局 - 两栏响应式 */
.main-layout {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.left-panel { flex: 1.6; min-width: 0; }
.right-panel { flex: 1; min-width: 280px; display: flex; flex-direction: column; gap: 16px; }

/* 卡片通用 */
.entity-card, .vc-card, .anchor-card, .overview-card {
  border-radius: 12px;
  background: white;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  color: #1e293b;
  flex-wrap: wrap;
  gap: 10px;
}
.header-controls { display: flex; gap: 8px; align-items: center; }

/* 树形表格 */
/* 树形表格 - 添加固定高度和隐藏滚动条 */
.hierarchy-table {
  height: 935px;
  overflow-y: auto;
  scrollbar-width: none;  /* Firefox */
  -ms-overflow-style: none;  /* IE/Edge */
}

.hierarchy-table::-webkit-scrollbar {
  display: none;  /* Chrome, Safari, Edge */
  width: 0;
  height: 0;
}

/* 保持表格头部固定，内容滚动 */
.hierarchy-table :deep(.el-table__header-wrapper) {
  position: sticky;
  top: 0;
  z-index: 10;
  background: white;
}

.hierarchy-table :deep(.el-table__body-wrapper) {
  overflow: visible;
}

.hierarchy-table :deep(.el-table__row) { cursor: pointer; }
.entity-cell { display: flex; align-items: center; gap: 8px; }
.entity-icon { font-size: 16px; }
.entity-name { font-weight: 500; }
.mono { font-family: monospace; font-size: 12px; }
.did-text { color: #3b82f6; }
.balance { color: #16a34a; font-weight: 500; }

/* 概览统计 */
.overview-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}
.overview-item { text-align: center; padding: 8px; background: #f8fafc; border-radius: 8px; }
.overview-value { font-size: 22px; font-weight: 700; color: #1e293b; }
.overview-label { font-size: 11px; color: #64748b; }

/* VC 列表 */
.vc-list { max-height: 320px; overflow-y: auto;overflow-x: hidden; scrollbar-width: none; -ms-overflow-style: none; }
.vc-item {
  background: #f8fafc;
  border-radius: 8px;
  padding: 10px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid #e2e8f0;
}
.vc-item:hover { background: #f1f5f9; transform: translateX(2px); }
.vc-header { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.vc-id { font-family: monospace; font-size: 11px; font-weight: 500; flex: 1; }
.vc-body { display: flex; flex-direction: column; gap: 4px; }
.vc-row { display: flex; font-size: 11px; }
.vc-label { width: 42px; color: #64748b; }

/* 锚定记录 */
.anchor-list { display: flex; flex-direction: column; gap: 8px; }
.anchor-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px;
  background: #f8fafc;
  border-radius: 8px;
}
.anchor-icon { font-size: 18px; }
.anchor-info { flex: 1; }
.anchor-operation { font-size: 12px; font-weight: 500; }
.anchor-entity { font-size: 10px; color: #64748b; }
.anchor-meta { text-align: right; }
.anchor-block { font-size: 11px; font-weight: 500; color: #3b82f6; }
.anchor-time { font-size: 10px; color: #94a3b8; }

.view-more {
  text-align: center;
  padding: 10px;
  font-size: 12px;
  color: #3b82f6;
  cursor: pointer;
  border-top: 1px solid #e2e8f0;
  margin-top: 4px;
}
.view-more:hover { background: #f1f5f9; }

.empty-placeholder { text-align: center; padding: 30px; color: #94a3b8; }

.pagination-wrapper {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

/* 详情对话框 */
.detail-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  border-radius: 12px;
  margin-bottom: 16px;
}
.detail-header.system { background: linear-gradient(135deg, #1a3a5c, #0f2a4a); color: white; }
.detail-header.company { background: linear-gradient(135deg, #3b82f6, #1d4ed8); color: white; }
.detail-header.zone { background: linear-gradient(135deg, #f59e0b, #d97706); color: white; }
.detail-icon { font-size: 32px; }
.detail-title h3 { margin: 0; font-size: 18px; }

/* 响应式 */
@media (max-width: 1024px) {
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .main-layout { flex-direction: column; }
  .left-panel, .right-panel { width: 100%; }
}

@media (max-width: 768px) {
  .did-management-page { padding: 12px; }
  .page-header { flex-direction: column; align-items: flex-start; }
  .stats-grid { grid-template-columns: repeat(2, 1fr); gap: 12px; }
  .stat-card { padding: 12px; }
  .stat-number { font-size: 20px; }
  .card-header { flex-direction: column; align-items: flex-start; }
  .header-controls { width: 100%; justify-content: space-between; }
  .hierarchy-table :deep(.el-table__header) { display: none; }
  .hierarchy-table :deep(.el-table__row) { display: block; margin-bottom: 12px; border: 1px solid #e2e8f0; border-radius: 8px; }
  .overview-stats { grid-template-columns: repeat(2, 1fr); }
}
</style>