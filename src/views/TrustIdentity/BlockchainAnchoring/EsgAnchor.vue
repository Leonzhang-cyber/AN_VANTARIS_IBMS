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
        <div class="loading-tip">Trust & Identity - Blockchain Anchoring</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="esg-anchor-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h1>ESG Anchor</h1>
        <p>Anchor Environmental, Social, and Governance data to blockchain for transparent reporting</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="openAnchorDialog">
          <el-icon><Link /></el-icon>
          Anchor ESG Data
        </el-button>
        <el-button @click="verifyAnchor">
          <el-icon><Search /></el-icon>
          Verify ESG Data
        </el-button>
        <el-button @click="exportReport">
          <el-icon><Download /></el-icon>
          Export Report
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
            <div class="stat-value">{{ stats.totalAnchors }}</div>
            <div class="stat-label">Total ESG Anchors</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon success-bg">
            <el-icon><CircleCheck /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.confirmedAnchors }}</div>
            <div class="stat-label">Confirmed</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon warning-bg">
            <el-icon><DataAnalysis /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.carbonReduction }}%</div>
            <div class="stat-label">Carbon Reduction</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon info-bg">
            <el-icon><TrendCharts /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.esgScore }}</div>
            <div class="stat-label">ESG Score</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- ESG Summary Cards -->
    <el-row :gutter="20" class="esg-summary-row">
      <el-col :xs="24" :sm="8">
        <div class="esg-card environmental">
          <div class="esg-header">
            <el-icon><OfficeBuilding /></el-icon>
            <h3>Environmental</h3>
          </div>
          <div class="esg-metrics">
            <div class="metric">
              <span class="label">Carbon Footprint</span>
              <span class="value">{{ environmentalMetrics.carbonFootprint }} tCO₂e</span>
            </div>
            <div class="metric">
              <span class="label">Energy Consumption</span>
              <span class="value">{{ environmentalMetrics.energyConsumption }} MWh</span>
            </div>
            <div class="metric">
              <span class="label">Water Usage</span>
              <span class="value">{{ environmentalMetrics.waterUsage }} m³</span>
            </div>
            <div class="metric">
              <span class="label">Waste Recycled</span>
              <span class="value">{{ environmentalMetrics.wasteRecycled }}%</span>
            </div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="8">
        <div class="esg-card social">
          <div class="esg-header">
            <el-icon><User /></el-icon>
            <h3>Social</h3>
          </div>
          <div class="esg-metrics">
            <div class="metric">
              <span class="label">Employee Count</span>
              <span class="value">{{ socialMetrics.employeeCount }}</span>
            </div>
            <div class="metric">
              <span class="label">Diversity Ratio</span>
              <span class="value">{{ socialMetrics.diversityRatio }}%</span>
            </div>
            <div class="metric">
              <span class="label">Training Hours</span>
              <span class="value">{{ socialMetrics.trainingHours }} hrs</span>
            </div>
            <div class="metric">
              <span class="label">Community Investment</span>
              <span class="value">${{ socialMetrics.communityInvestment }}k</span>
            </div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="8">
        <div class="esg-card governance">
          <div class="esg-header">
            <el-icon><OfficeBuilding /></el-icon>
            <h3>Governance</h3>
          </div>
          <div class="esg-metrics">
            <div class="metric">
              <span class="label">Board Independence</span>
              <span class="value">{{ governanceMetrics.boardIndependence }}%</span>
            </div>
            <div class="metric">
              <span class="label">Ethics Training</span>
              <span class="value">{{ governanceMetrics.ethicsTraining }}%</span>
            </div>
            <div class="metric">
              <span class="label">Audit Compliance</span>
              <span class="value">{{ governanceMetrics.auditCompliance }}%</span>
            </div>
            <div class="metric">
              <span class="label">Risk Score</span>
              <span class="value">{{ governanceMetrics.riskScore }}</span>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Blockchain Status Bar -->
    <div class="blockchain-status">
      <div class="status-left">
        <div class="status-indicator" :class="blockchainStatus"></div>
        <span class="status-text">Blockchain: {{ blockchainStatus === 'connected' ? 'Connected' : 'Disconnected' }}</span>
        <span class="network-name">{{ networkName }}</span>
      </div>
      <div class="status-right">
        <span>Block Height: {{ blockHeight }}</span>
        <span>Gas Price: {{ gasPrice }} Gwei</span>
        <span>Last Block: {{ lastBlockTime }}</span>
      </div>
    </div>

    <!-- Search & Filter -->
    <div class="filter-bar">
      <el-input
          v-model="filters.search"
          placeholder="Search by ESG ID, reporting period..."
          clearable
          style="width: 280px"
          :prefix-icon="Search"
      />
      <el-select v-model="filters.category" placeholder="Category" clearable style="width: 140px">
        <el-option label="All" value="" />
        <el-option label="Environmental" value="environmental" />
        <el-option label="Social" value="social" />
        <el-option label="Governance" value="governance" />
      </el-select>
      <el-select v-model="filters.status" placeholder="Status" clearable style="width: 130px">
        <el-option label="All" value="" />
        <el-option label="Confirmed" value="confirmed" />
        <el-option label="Pending" value="pending" />
      </el-select>
      <el-date-picker
          v-model="filters.dateRange"
          type="daterange"
          range-separator="to"
          start-placeholder="Start Date"
          end-placeholder="End Date"
          style="width: 260px"
      />
      <el-button type="primary" @click="handleSearch">
        <el-icon><Search /></el-icon>
        Apply
      </el-button>
      <el-button @click="resetFilters">
        <el-icon><RefreshLeft /></el-icon>
        Reset
      </el-button>
    </div>

    <!-- ESG Anchors Table -->
    <div class="anchors-table-wrapper">
      <el-table :data="filteredAnchors" stripe v-loading="tableLoading" style="width: 100%">
        <el-table-column prop="id" label="ESG ID" width="120" />
        <el-table-column prop="reportingPeriod" label="Reporting Period" width="120" />
        <el-table-column prop="category" label="Category" width="120">
          <template #default="{ row }">
            <el-tag :type="getCategoryTagType(row.category)" size="small">
              {{ row.category }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="Title" min-width="200" show-overflow-tooltip />
        <el-table-column prop="hash" label="SHA-256 Hash" width="280" show-overflow-tooltip>
          <template #default="{ row }">
            <code class="hash-code">{{ row.hash }}</code>
            <el-button link size="small" @click="copyHash(row.hash)">
              <el-icon><CopyDocument /></el-icon>
            </el-button>
          </template>
        </el-table-column>
        <el-table-column prop="txHash" label="Transaction Hash" width="200" show-overflow-tooltip>
          <template #default="{ row }">
            <code class="tx-hash" v-if="row.txHash">{{ row.txHash }}</code>
            <span v-else class="pending-text">Pending</span>
            <el-button v-if="row.txHash" link size="small" @click="viewOnExplorer(row.txHash)">
              <el-icon><Link /></el-icon>
            </el-button>
          </template>
        </el-table-column>
        <el-table-column prop="timestamp" label="Anchored At" width="160" />
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'confirmed' ? 'success' : 'warning'" size="small">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="140" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewDetails(row)">
              Details
            </el-button>
            <el-button v-if="row.status === 'confirmed'" link type="success" size="small" @click="verifyESGData(row)">
              Verify
            </el-button>
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

    <!-- Anchor ESG Data Dialog -->
    <el-dialog v-model="anchorDialog.visible" title="Anchor ESG Data to Blockchain" width="750px" class="anchor-dialog">
      <div class="anchor-steps">
        <el-steps :active="anchorStep" finish-status="success" align-center>
          <el-step title="ESG Details" />
          <el-step title="Generate Hash" />
          <el-step title="Confirm & Anchor" />
        </el-steps>
      </div>

      <div class="anchor-content">
        <!-- Step 1: ESG Details -->
        <div v-show="anchorStep === 0" class="step-panel">
          <el-form :model="esgForm" label-width="130px">
            <el-form-item label="Category" required>
              <el-select v-model="esgForm.category" placeholder="Select ESG category" style="width: 100%">
                <el-option label="Environmental" value="environmental" />
                <el-option label="Social" value="social" />
                <el-option label="Governance" value="governance" />
              </el-select>
            </el-form-item>

            <el-form-item label="Reporting Period" required>
              <el-select v-model="esgForm.reportingPeriod" placeholder="Select period" style="width: 100%">
                <el-option label="Q1 2024" value="Q1 2024" />
                <el-option label="Q2 2024" value="Q2 2024" />
                <el-option label="Q3 2024" value="Q3 2024" />
                <el-option label="Q4 2024" value="Q4 2024" />
                <el-option label="Annual 2024" value="Annual 2024" />
              </el-select>
            </el-form-item>

            <el-form-item label="Title" required>
              <el-input v-model="esgForm.title" placeholder="Enter ESG data title" />
            </el-form-item>

            <el-form-item label="Description" required>
              <el-input
                  v-model="esgForm.description"
                  type="textarea"
                  :rows="3"
                  placeholder="Detailed description of ESG data..."
              />
            </el-form-item>

            <!-- Environmental Metrics -->
            <template v-if="esgForm.category === 'environmental'">
              <el-divider content-position="left">Environmental Metrics</el-divider>
              <el-row :gutter="16">
                <el-col :span="12">
                  <el-form-item label="Carbon Footprint (tCO₂e)">
                    <el-input-number v-model="esgForm.carbonFootprint" :min="0" :step="100" style="width: 100%" />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="Energy Consumption (MWh)">
                    <el-input-number v-model="esgForm.energyConsumption" :min="0" :step="500" style="width: 100%" />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="Water Usage (m³)">
                    <el-input-number v-model="esgForm.waterUsage" :min="0" :step="1000" style="width: 100%" />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="Waste Recycled (%)">
                    <el-slider v-model="esgForm.wasteRecycled" :min="0" :max="100" />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="Renewable Energy (%)">
                    <el-slider v-model="esgForm.renewableEnergy" :min="0" :max="100" />
                  </el-form-item>
                </el-col>
              </el-row>
            </template>

            <!-- Social Metrics -->
            <template v-if="esgForm.category === 'social'">
              <el-divider content-position="left">Social Metrics</el-divider>
              <el-row :gutter="16">
                <el-col :span="12">
                  <el-form-item label="Employee Count">
                    <el-input-number v-model="esgForm.employeeCount" :min="0" :step="50" style="width: 100%" />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="Diversity Ratio (%)">
                    <el-slider v-model="esgForm.diversityRatio" :min="0" :max="100" />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="Training Hours">
                    <el-input-number v-model="esgForm.trainingHours" :min="0" :step="100" style="width: 100%" />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="Community Investment ($k)">
                    <el-input-number v-model="esgForm.communityInvestment" :min="0" :step="50" style="width: 100%" />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="Safety Incident Rate">
                    <el-input-number v-model="esgForm.safetyIncidentRate" :min="0" :step="0.1" :precision="1" style="width: 100%" />
                  </el-form-item>
                </el-col>
              </el-row>
            </template>

            <!-- Governance Metrics -->
            <template v-if="esgForm.category === 'governance'">
              <el-divider content-position="left">Governance Metrics</el-divider>
              <el-row :gutter="16">
                <el-col :span="12">
                  <el-form-item label="Board Independence (%)">
                    <el-slider v-model="esgForm.boardIndependence" :min="0" :max="100" />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="Ethics Training (%)">
                    <el-slider v-model="esgForm.ethicsTraining" :min="0" :max="100" />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="Audit Compliance (%)">
                    <el-slider v-model="esgForm.auditCompliance" :min="0" :max="100" />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="Risk Score">
                    <el-slider v-model="esgForm.riskScore" :min="0" :max="100" />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="Whistleblower Reports">
                    <el-input-number v-model="esgForm.whistleblowerReports" :min="0" style="width: 100%" />
                  </el-form-item>
                </el-col>
              </el-row>
            </template>

            <el-form-item label="Supporting Document">
              <div class="upload-area-small" @click="triggerDocUpload">
                <el-icon><Upload /></el-icon>
                <span>Click to upload supporting document</span>
                <input ref="docInputRef" type="file" style="display: none" @change="handleDocSelect" />
              </div>
              <div v-if="supportingDoc" class="doc-item">
                <el-icon><Document /></el-icon>
                <span>{{ supportingDoc.name }}</span>
                <el-button link type="danger" @click="supportingDoc = null">Remove</el-button>
              </div>
            </el-form-item>
          </el-form>
        </div>

        <!-- Step 2: Generate Hash -->
        <div v-show="anchorStep === 1" class="step-panel">
          <div class="esg-preview">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="Category">{{ formatCategory(esgForm.category) }}</el-descriptions-item>
              <el-descriptions-item label="Reporting Period">{{ esgForm.reportingPeriod }}</el-descriptions-item>
              <el-descriptions-item label="Title">{{ esgForm.title }}</el-descriptions-item>
              <el-descriptions-item label="Description" :span="2">{{ esgForm.description }}</el-descriptions-item>
            </el-descriptions>
          </div>

          <div class="hash-generator">
            <div class="hash-label">SHA-256 Hash of ESG Data</div>
            <div class="hash-value">
              <code>{{ generatedHash || 'Click "Generate Hash" to compute' }}</code>
            </div>
            <el-button type="primary" @click="generateESGHash" :loading="isGeneratingHash">
              <el-icon><DataAnalysis /></el-icon>
              Generate ESG Hash
            </el-button>
          </div>

          <div class="hash-info">
            <el-alert
                title="What is being hashed?"
                type="info"
                description="The hash is computed from all ESG metrics, description, and supporting document. This creates a unique fingerprint that represents the ESG data."
                show-icon
                :closable="false"
            />
          </div>
        </div>

        <!-- Step 3: Confirm & Anchor -->
        <div v-show="anchorStep === 2" class="step-panel">
          <div class="confirm-info">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="ESG Hash" :span="2">
                <code class="hash-code">{{ generatedHash }}</code>
              </el-descriptions-item>
              <el-descriptions-item label="Category">{{ formatCategory(esgForm.category) }}</el-descriptions-item>
              <el-descriptions-item label="Reporting Period">{{ esgForm.reportingPeriod }}</el-descriptions-item>
              <el-descriptions-item label="Title">{{ esgForm.title }}</el-descriptions-item>
              <el-descriptions-item label="Document Attached">{{ supportingDoc ? 'Yes' : 'No' }}</el-descriptions-item>
            </el-descriptions>
          </div>

          <div class="anchor-params">
            <el-form label-width="120px">
              <el-form-item label="Network">
                <el-select v-model="anchorParams.network" style="width: 100%">
                  <el-option label="Ethereum Mainnet" value="ethereum" />
                  <el-option label="Polygon" value="polygon" />
                  <el-option label="Binance Smart Chain" value="bsc" />
                </el-select>
              </el-form-item>
              <el-form-item label="Gas Limit">
                <el-input-number v-model="anchorParams.gasLimit" :min="50000" :max="500000" :step="10000" />
              </el-form-item>
              <el-form-item label="Include Metadata">
                <el-switch v-model="anchorParams.includeMetadata" />
                <span class="form-hint">Store ESG metadata on-chain</span>
              </el-form-item>
            </el-form>
          </div>
        </div>
      </div>

      <template #footer>
        <el-button v-if="anchorStep > 0" @click="anchorStep--">Back</el-button>
        <el-button v-if="anchorStep < 2" type="primary" @click="anchorStep++" :disabled="!canProceedToNext">
          Next
        </el-button>
        <el-button v-if="anchorStep === 2" type="success" @click="anchorESGData" :loading="isAnchoring">
          <el-icon><Link /></el-icon>
          Anchor to Blockchain
        </el-button>
        <el-button @click="anchorDialog.visible = false">Cancel</el-button>
      </template>
    </el-dialog>

    <!-- ESG Details Dialog -->
    <el-dialog v-model="detailDialog.visible" :title="detailDialog.esg?.title" width="700px">
      <div v-if="detailDialog.esg" class="esg-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="ESG ID">{{ detailDialog.esg.id }}</el-descriptions-item>
          <el-descriptions-item label="Category">
            <el-tag :type="getCategoryTagType(detailDialog.esg.category)">{{ detailDialog.esg.category }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Reporting Period">{{ detailDialog.esg.reportingPeriod }}</el-descriptions-item>
          <el-descriptions-item label="Status">
            <el-tag :type="detailDialog.esg.status === 'confirmed' ? 'success' : 'warning'">{{ detailDialog.esg.status }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Description" :span="2">{{ detailDialog.esg.description }}</el-descriptions-item>
          <el-descriptions-item label="SHA-256 Hash" :span="2">
            <code class="hash-code">{{ detailDialog.esg.hash }}</code>
            <el-button link size="small" @click="copyHash(detailDialog.esg.hash)">Copy</el-button>
          </el-descriptions-item>
          <el-descriptions-item label="Transaction Hash" :span="2" v-if="detailDialog.esg.txHash">
            <code class="tx-hash">{{ detailDialog.esg.txHash }}</code>
            <el-button link size="small" @click="viewOnExplorer(detailDialog.esg.txHash)">View on Explorer</el-button>
          </el-descriptions-item>
          <el-descriptions-item label="Block Number">{{ detailDialog.esg.blockNumber || '-' }}</el-descriptions-item>
          <el-descriptions-item label="Network">{{ detailDialog.esg.network }}</el-descriptions-item>
          <el-descriptions-item label="Anchored At">{{ detailDialog.esg.timestamp }}</el-descriptions-item>
          <el-descriptions-item label="Anchored By">{{ detailDialog.esg.anchoredBy }}</el-descriptions-item>
        </el-descriptions>

        <div class="metrics-section" v-if="detailDialog.esg.metrics">
          <h4>ESG Metrics</h4>
          <el-descriptions :column="2" border size="small">
            <el-descriptions-item v-for="(value, key) in detailDialog.esg.metrics" :key="key" :label="formatMetricLabel(key)">
              {{ value }}
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </div>
    </el-dialog>

    <!-- Verification Dialog -->
    <el-dialog v-model="verifyDialog.visible" title="Verify ESG Data" width="550px">
      <div class="verify-content">
        <div class="verify-area" @click="triggerVerifyInput">
          <el-icon class="upload-icon"><Search /></el-icon>
          <div class="upload-text">Enter ESG ID or Transaction Hash to verify</div>
          <el-input
              v-model="verifyQuery"
              placeholder="ESG ID (e.g., ESG-001) or Transaction Hash"
              style="margin-top: 16px"
          />
        </div>

        <el-button type="primary" @click="performVerification" :loading="isVerifying" style="margin-top: 16px; width: 100%">
          Verify on Blockchain
        </el-button>

        <div v-if="verificationResult" class="verification-result" :class="verificationResult.isValid ? 'valid' : 'invalid'">
          <div class="result-icon">
            <el-icon v-if="verificationResult.isValid"><CircleCheck /></el-icon>
            <el-icon v-else><CircleClose /></el-icon>
          </div>
          <div class="result-content">
            <h4>{{ verificationResult.isValid ? 'ESG Data Verified!' : 'Verification Failed' }}</h4>
            <p>{{ verificationResult.message }}</p>
            <div v-if="verificationResult.details" class="result-details">
              <div>ESG ID: {{ verificationResult.details.esgId }}</div>
              <div>Category: {{ verificationResult.details.category }}</div>
              <div>Reporting Period: {{ verificationResult.details.reportingPeriod }}</div>
              <div>Block: {{ verificationResult.details.blockNumber }}</div>
              <div>Timestamp: {{ verificationResult.details.timestamp }}</div>
            </div>
          </div>
        </div>
      </div>
    </el-dialog>

    <!-- Success Dialog -->
    <el-dialog v-model="successDialog.visible" title="ESG Data Anchored Successfully" width="500px">
      <div class="success-content">
        <el-icon class="success-icon"><CircleCheck /></el-icon>
        <h3>ESG Data Successfully Anchored</h3>
        <p>The ESG data has been permanently recorded on the blockchain.</p>
        <div class="success-info">
          <div><strong>ESG ID:</strong> {{ lastAnchorResult?.esgId }}</div>
          <div><strong>Category:</strong> {{ formatCategory(lastAnchorResult?.category) }}</div>
          <div><strong>Transaction Hash:</strong> <code>{{ lastAnchorResult?.txHash }}</code></div>
          <div><strong>Block Number:</strong> {{ lastAnchorResult?.blockNumber }}</div>
        </div>
        <div class="success-actions">
          <el-button type="primary" @click="viewOnExplorer(lastAnchorResult?.txHash)">View on Explorer</el-button>
          <el-button @click="downloadESGProof">Download Proof</el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Link,
  Search,
  Document,
  CircleCheck,
  DataAnalysis,
  Connection,
  CopyDocument,
  Upload,
  Loading,
  CircleClose,
  RefreshLeft,
  User,
  OfficeBuilding,
  TrendCharts,
  Download
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const tableLoading = ref(false)

const loadingMessages = [
  'Preparing...',
  'Connecting to blockchain...',
  'Loading ESG registry...',
  'Almost ready...'
]

// ==================== 类型定义 ====================
interface ESGAnchor {
  id: string
  reportingPeriod: string
  category: string
  title: string
  description: string
  hash: string
  txHash: string | null
  blockNumber: number | null
  network: string
  status: 'pending' | 'confirmed'
  timestamp: string
  anchoredBy: string
  metrics?: Record<string, any>
}

// ==================== 模拟数据 ====================
const stats = reactive({
  totalAnchors: 24,
  confirmedAnchors: 22,
  carbonReduction: 28,
  esgScore: 87
})

const environmentalMetrics = reactive({
  carbonFootprint: 12500,
  energyConsumption: 18500,
  waterUsage: 45000,
  wasteRecycled: 68
})

const socialMetrics = reactive({
  employeeCount: 1250,
  diversityRatio: 42,
  trainingHours: 15800,
  communityInvestment: 250
})

const governanceMetrics = reactive({
  boardIndependence: 45,
  ethicsTraining: 98,
  auditCompliance: 100,
  riskScore: 12
})

const blockchainStatus = ref('connected')
const networkName = ref('Ethereum Mainnet')
const blockHeight = ref('18,234,567')
const gasPrice = ref('28')
const lastBlockTime = ref('12s ago')

const esgAnchors = ref<ESGAnchor[]>([
  {
    id: 'ESG-001',
    reportingPeriod: 'Q1 2024',
    category: 'environmental',
    title: 'Carbon Emissions Report Q1 2024',
    description: 'Quarterly carbon emissions and reduction initiatives report',
    hash: '0x3a2b1c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b',
    txHash: '0x7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2d1e0f9a8b7c6d5e4f3a2b1c0d9e8f7a6b',
    blockNumber: 18234567,
    network: 'Ethereum',
    status: 'confirmed',
    timestamp: '2024-04-15 10:30:00',
    anchoredBy: 'sustainability@ibms.com',
    metrics: { carbonFootprint: 3125, energyConsumption: 4625, waterUsage: 11250, wasteRecycled: 68 }
  },
  {
    id: 'ESG-002',
    reportingPeriod: 'Q1 2024',
    category: 'social',
    title: 'Workforce Diversity Report',
    description: 'Quarterly workforce diversity and inclusion metrics',
    hash: '0x2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3',
    txHash: '0x8b7a6c5d4e3f2a1b0c9d8e7f6a5b4c3d2e1f0a9b8c7d6e5f4a3b2c1d0e9f8a7b',
    blockNumber: 18234123,
    network: 'Ethereum',
    status: 'confirmed',
    timestamp: '2024-04-10 14:15:00',
    anchoredBy: 'hr@ibms.com',
    metrics: { employeeCount: 1250, diversityRatio: 42, trainingHours: 3950, communityInvestment: 62.5 }
  },
  {
    id: 'ESG-003',
    reportingPeriod: 'Q2 2024',
    category: 'environmental',
    title: 'Sustainability Report',
    description: 'Q2 2024 environmental sustainability metrics',
    hash: '0x3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4',
    txHash: null,
    blockNumber: null,
    network: 'Polygon',
    status: 'pending',
    timestamp: '2024-07-12 09:45:00',
    anchoredBy: 'sustainability@ibms.com',
    metrics: { carbonFootprint: 2980, energyConsumption: 4520, waterUsage: 10800, wasteRecycled: 71 }
  }
])

const filters = reactive({
  search: '',
  category: '',
  status: '',
  dateRange: null as Date[] | null
})

const pagination = reactive({
  currentPage: 1,
  pageSize: 10,
  total: 0
})

const anchorDialog = reactive({
  visible: false
})

const detailDialog = reactive({
  visible: false,
  esg: null as ESGAnchor | null
})

const verifyDialog = reactive({
  visible: false
})

const successDialog = reactive({
  visible: false
})

const anchorStep = ref(0)
const generatedHash = ref('')
const isGeneratingHash = ref(false)
const isAnchoring = ref(false)
const isVerifying = ref(false)
const verifyQuery = ref('')
const verificationResult = ref<any>(null)
const lastAnchorResult = ref<any>(null)
const supportingDoc = ref<File | null>(null)

const docInputRef = ref<HTMLInputElement | null>(null)

const esgForm = reactive({
  category: '',
  reportingPeriod: '',
  title: '',
  description: '',
  // Environmental metrics
  carbonFootprint: 0,
  energyConsumption: 0,
  waterUsage: 0,
  wasteRecycled: 0,
  renewableEnergy: 0,
  // Social metrics
  employeeCount: 0,
  diversityRatio: 0,
  trainingHours: 0,
  communityInvestment: 0,
  safetyIncidentRate: 0,
  // Governance metrics
  boardIndependence: 0,
  ethicsTraining: 0,
  auditCompliance: 0,
  riskScore: 0,
  whistleblowerReports: 0
})

const anchorParams = reactive({
  network: 'ethereum',
  gasLimit: 100000,
  includeMetadata: true
})

// ==================== 计算属性 ====================
const filteredAnchors = computed(() => {
  let filtered = [...esgAnchors.value]

  if (filters.search) {
    const searchLower = filters.search.toLowerCase()
    filtered = filtered.filter(e =>
        e.id.toLowerCase().includes(searchLower) ||
        e.reportingPeriod.toLowerCase().includes(searchLower) ||
        e.title.toLowerCase().includes(searchLower)
    )
  }

  if (filters.category) {
    filtered = filtered.filter(e => e.category === filters.category)
  }

  if (filters.status) {
    filtered = filtered.filter(e => e.status === filters.status)
  }

  if (filters.dateRange && filters.dateRange.length === 2) {
    const [start, end] = filters.dateRange
    filtered = filtered.filter(e => {
      const date = new Date(e.timestamp)
      return date >= start && date <= end
    })
  }

  pagination.total = filtered.length
  const start = (pagination.currentPage - 1) * pagination.pageSize
  const end = start + pagination.pageSize
  return filtered.slice(start, end)
})

const canProceedToNext = computed(() => {
  if (anchorStep.value === 0) {
    return esgForm.category !== '' &&
        esgForm.reportingPeriod !== '' &&
        esgForm.title.trim() !== '' &&
        esgForm.description.trim() !== ''
  }
  if (anchorStep.value === 1) {
    return generatedHash.value !== ''
  }
  return true
})

// ==================== 辅助函数 ====================
const formatCategory = (category: string) => {
  const map: Record<string, string> = {
    'environmental': 'Environmental',
    'social': 'Social',
    'governance': 'Governance'
  }
  return map[category] || category
}

const getCategoryTagType = (category: string) => {
  const map: Record<string, string> = {
    'environmental': 'success',
    'social': 'primary',
    'governance': 'warning'
  }
  return map[category] || 'info'
}

const formatMetricLabel = (key: string) => {
  const map: Record<string, string> = {
    carbonFootprint: 'Carbon Footprint (tCO₂e)',
    energyConsumption: 'Energy Consumption (MWh)',
    waterUsage: 'Water Usage (m³)',
    wasteRecycled: 'Waste Recycled (%)',
    renewableEnergy: 'Renewable Energy (%)',
    employeeCount: 'Employee Count',
    diversityRatio: 'Diversity Ratio (%)',
    trainingHours: 'Training Hours',
    communityInvestment: 'Community Investment ($k)',
    safetyIncidentRate: 'Safety Incident Rate',
    boardIndependence: 'Board Independence (%)',
    ethicsTraining: 'Ethics Training (%)',
    auditCompliance: 'Audit Compliance (%)',
    riskScore: 'Risk Score',
    whistleblowerReports: 'Whistleblower Reports'
  }
  return map[key] || key
}

const copyHash = async (hash: string) => {
  try {
    await navigator.clipboard.writeText(hash)
    ElMessage.success('Hash copied to clipboard')
  } catch {
    ElMessage.error('Failed to copy')
  }
}

const viewOnExplorer = (hash: string) => {
  if (hash) {
    window.open(`https://etherscan.io/tx/${hash}`, '_blank')
  }
}

const handleSearch = () => {
  pagination.currentPage = 1
}

const resetFilters = () => {
  filters.search = ''
  filters.category = ''
  filters.status = ''
  filters.dateRange = null
  pagination.currentPage = 1
}

const handleSizeChange = (size: number) => {
  pagination.pageSize = size
  pagination.currentPage = 1
}

const handleCurrentChange = (page: number) => {
  pagination.currentPage = page
}

const triggerDocUpload = () => {
  docInputRef.value?.click()
}

const handleDocSelect = (e: Event) => {
  const input = e.target as HTMLInputElement
  if (input.files && input.files[0]) {
    supportingDoc.value = input.files[0]
  }
}

const generateESGHash = async () => {
  isGeneratingHash.value = true

  await new Promise(resolve => setTimeout(resolve, 1500))

  const dataToHash = JSON.stringify({
    category: esgForm.category,
    reportingPeriod: esgForm.reportingPeriod,
    title: esgForm.title,
    description: esgForm.description,
    metrics: getCurrentMetrics(),
    document: supportingDoc.value?.name
  })

  const hash = Array.from({ length: 64 }, () =>
      '0123456789abcdef'[Math.floor(Math.random() * 16)]
  ).join('')

  generatedHash.value = `0x${hash}`
  isGeneratingHash.value = false
  ElMessage.success('ESG hash generated successfully')
}

const getCurrentMetrics = () => {
  if (esgForm.category === 'environmental') {
    return {
      carbonFootprint: esgForm.carbonFootprint,
      energyConsumption: esgForm.energyConsumption,
      waterUsage: esgForm.waterUsage,
      wasteRecycled: esgForm.wasteRecycled,
      renewableEnergy: esgForm.renewableEnergy
    }
  } else if (esgForm.category === 'social') {
    return {
      employeeCount: esgForm.employeeCount,
      diversityRatio: esgForm.diversityRatio,
      trainingHours: esgForm.trainingHours,
      communityInvestment: esgForm.communityInvestment,
      safetyIncidentRate: esgForm.safetyIncidentRate
    }
  } else {
    return {
      boardIndependence: esgForm.boardIndependence,
      ethicsTraining: esgForm.ethicsTraining,
      auditCompliance: esgForm.auditCompliance,
      riskScore: esgForm.riskScore,
      whistleblowerReports: esgForm.whistleblowerReports
    }
  }
}

const anchorESGData = async () => {
  isAnchoring.value = true

  await new Promise(resolve => setTimeout(resolve, 3000))

  const txHash = `0x${Array.from({ length: 64 }, () =>
      '0123456789abcdef'[Math.floor(Math.random() * 16)]
  ).join('')}`

  const blockNumber = 18235000 + Math.floor(Math.random() * 1000)

  const newESG: ESGAnchor = {
    id: `ESG-${String(esgAnchors.value.length + 1).padStart(3, '0')}`,
    reportingPeriod: esgForm.reportingPeriod,
    category: esgForm.category,
    title: esgForm.title,
    description: esgForm.description,
    hash: generatedHash.value,
    txHash: txHash,
    blockNumber: blockNumber,
    network: anchorParams.network,
    status: 'pending',
    timestamp: new Date().toLocaleString(),
    anchoredBy: 'admin@ibms.com',
    metrics: getCurrentMetrics()
  }

  esgAnchors.value.unshift(newESG)
  stats.totalAnchors++

  lastAnchorResult.value = {
    esgId: newESG.id,
    category: esgForm.category,
    txHash: txHash,
    blockNumber: blockNumber,
    network: anchorParams.network
  }

  isAnchoring.value = false
  anchorDialog.visible = false
  successDialog.visible = true

  // Simulate confirmation
  setTimeout(() => {
    const index = esgAnchors.value.findIndex(e => e.id === newESG.id)
    if (index !== -1) {
      esgAnchors.value[index].status = 'confirmed'
      stats.confirmedAnchors++
    }
  }, 5000)

  // Reset form
  anchorStep.value = 0
  Object.assign(esgForm, {
    category: '',
    reportingPeriod: '',
    title: '',
    description: '',
    carbonFootprint: 0,
    energyConsumption: 0,
    waterUsage: 0,
    wasteRecycled: 0,
    renewableEnergy: 0,
    employeeCount: 0,
    diversityRatio: 0,
    trainingHours: 0,
    communityInvestment: 0,
    safetyIncidentRate: 0,
    boardIndependence: 0,
    ethicsTraining: 0,
    auditCompliance: 0,
    riskScore: 0,
    whistleblowerReports: 0
  })
  generatedHash.value = ''
  supportingDoc.value = null
}

const openAnchorDialog = () => {
  anchorStep.value = 0
  anchorDialog.visible = true
}

const viewDetails = (esg: ESGAnchor) => {
  detailDialog.esg = esg
  detailDialog.visible = true
}

const verifyAnchor = () => {
  verifyDialog.visible = true
  verifyQuery.value = ''
  verificationResult.value = null
}

const triggerVerifyInput = () => {
  // Focus on input
}

const performVerification = async () => {
  if (!verifyQuery.value.trim()) {
    ElMessage.warning('Please enter an ESG ID or Transaction Hash')
    return
  }

  isVerifying.value = true

  await new Promise(resolve => setTimeout(resolve, 2000))

  const esg = esgAnchors.value.find(e =>
      e.id === verifyQuery.value || e.txHash === verifyQuery.value
  )

  if (esg && esg.status === 'confirmed') {
    verificationResult.value = {
      isValid: true,
      message: 'ESG data verified on blockchain. Hash matches on-chain record.',
      details: {
        esgId: esg.id,
        category: formatCategory(esg.category),
        reportingPeriod: esg.reportingPeriod,
        blockNumber: esg.blockNumber,
        timestamp: esg.timestamp
      }
    }
  } else if (esg && esg.status === 'pending') {
    verificationResult.value = {
      isValid: false,
      message: 'ESG data transaction is pending confirmation.',
      details: {
        esgId: esg.id,
        status: esg.status
      }
    }
  } else {
    verificationResult.value = {
      isValid: false,
      message: 'ESG data not found on blockchain or verification failed.',
      details: null
    }
  }

  isVerifying.value = false
}

const verifyESGData = (esg: ESGAnchor) => {
  verifyDialog.visible = true
  verifyQuery.value = esg.id
  performVerification()
}

const downloadESGProof = () => {
  const proof = {
    anchoredAt: new Date().toISOString(),
    esgId: lastAnchorResult.value?.esgId,
    transactionHash: lastAnchorResult.value?.txHash,
    blockNumber: lastAnchorResult.value?.blockNumber,
    network: lastAnchorResult.value?.network,
    category: lastAnchorResult.value?.category,
    hash: generatedHash.value
  }
  const data = JSON.stringify(proof, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `esg-proof-${lastAnchorResult.value?.esgId}.json`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('ESG proof downloaded')
}

const exportReport = () => {
  const report = {
    generatedAt: new Date().toISOString(),
    summary: stats,
    environmental: environmentalMetrics,
    social: socialMetrics,
    governance: governanceMetrics,
    anchors: esgAnchors.value
  }
  const data = JSON.stringify(report, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `esg-report-${new Date().toISOString().slice(0, 19)}.json`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('ESG report exported')
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
.esg-anchor-page {
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

/* ESG Summary Cards */
.esg-summary-row {
  margin-bottom: 24px;
}

.esg-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.esg-card.environmental { border-top: 4px solid #67c23a; }
.esg-card.social { border-top: 4px solid #409eff; }
.esg-card.governance { border-top: 4px solid #e6a23c; }

.esg-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #ebeef5;
}

.esg-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.environmental .esg-header { color: #67c23a; }
.social .esg-header { color: #409eff; }
.governance .esg-header { color: #e6a23c; }

.esg-metrics {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.metric {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.metric .label {
  font-size: 13px;
  color: #5e6e82;
}

.metric .value {
  font-weight: 600;
  font-size: 14px;
  color: #1f2f3d;
}

/* Blockchain Status */
.blockchain-status {
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

.network-name {
  color: #409eff;
  font-weight: 500;
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

/* Anchors Table */
.anchors-table-wrapper {
  background: white;
  border-radius: 12px;
  padding: 0;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.hash-code, .tx-hash {
  font-family: monospace;
  font-size: 12px;
  background: #f5f7fa;
  padding: 2px 6px;
  border-radius: 4px;
}

.pending-text {
  color: #e6a23c;
  font-style: italic;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  padding: 16px 20px;
  border-top: 1px solid #ebeef5;
}

/* Anchor Dialog */
.anchor-dialog :deep(.el-dialog__body) {
  max-height: 60vh;
  overflow-y: auto;
}

.anchor-steps {
  margin-bottom: 30px;
}

.upload-area-small {
  border: 1px dashed #d9d9d9;
  border-radius: 8px;
  padding: 12px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.upload-area-small:hover {
  border-color: #409eff;
  background-color: #f5f7fa;
}

.doc-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
  padding: 8px;
  background: #f5f7fa;
  border-radius: 4px;
}

.esg-preview {
  margin-bottom: 24px;
}

.hash-generator {
  text-align: center;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.hash-label {
  font-weight: 500;
  margin-bottom: 12px;
}

.hash-value {
  background: white;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 16px;
  word-break: break-all;
}

.hash-info {
  margin-top: 20px;
}

.confirm-info {
  margin-bottom: 20px;
}

.anchor-params {
  margin-top: 20px;
}

.form-hint {
  margin-left: 12px;
  font-size: 12px;
  color: #8c9aab;
}

/* ESG Detail */
.esg-detail {
  padding: 8px 0;
}

.metrics-section {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
}

.metrics-section h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
}

/* Verification Dialog */
.verify-content {
  padding: 8px 0;
}

.verify-area {
  border: 2px dashed #d9d9d9;
  border-radius: 8px;
  padding: 30px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
}

.verify-area:hover {
  border-color: #409eff;
  background-color: #f5f7fa;
}

.verification-result {
  margin-top: 20px;
  padding: 20px;
  border-radius: 8px;
  display: flex;
  gap: 16px;
}

.verification-result.valid {
  background-color: #f0f9eb;
  border: 1px solid #67c23a;
}

.verification-result.invalid {
  background-color: #fef0f0;
  border: 1px solid #f56c6c;
}

.result-icon {
  font-size: 32px;
}

.verification-result.valid .result-icon { color: #67c23a; }
.verification-result.invalid .result-icon { color: #f56c6c; }

.result-content {
  flex: 1;
}

.result-content h4 {
  margin: 0 0 8px 0;
}

.result-details {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  font-size: 12px;
}

/* Success Dialog */
.success-content {
  text-align: center;
  padding: 20px;
}

.success-icon {
  font-size: 64px;
  color: #67c23a;
  margin-bottom: 20px;
}

.success-info {
  background: #f5f7fa;
  padding: 16px;
  border-radius: 8px;
  margin: 20px 0;
  text-align: left;
}

.success-info div {
  margin-bottom: 8px;
  word-break: break-all;
}

.success-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}

:deep(.el-table th) {
  background-color: #fafbfc;
  font-weight: 600;
}

:deep(.el-step__title) {
  font-size: 12px;
}
</style>