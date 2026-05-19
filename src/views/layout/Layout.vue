<template>
  <el-container style="height:100vh;overflow:hidden">
    <!-- 移动端遮罩层 -->
    <transition name="fade">
      <div
          v-if="isMobile && mobileSidebarVisible"
          class="mobile-mask"
          @click="closeMobileSidebar"
      ></div>
    </transition>

    <!-- 左侧菜单 -->
    <el-aside
        width="230px"
        class="sidebar"
        :class="{
        'mobile-sidebar': isMobile,
        'open': isMobile && mobileSidebarVisible
      }"
        :style="{ width: isFullscreen ? '0' : (isMobile ? '280px' : '260px'), opacity: isFullscreen ? 0 : 1 }"
    >
      <div class="logo-box">
        <img src="/favicon.ico" class="logo-img">
        <span class="logo-text">IBMS IoT Platform</span>
      </div>

      <div class="menu-scroll">
        <el-menu
            :key="route.path"
            background-color="#0a1629"
            text-color="#e5eaf3"
            active-text-color="#409eff"
            :default-active="activeMenu"
            v-model:default-openeds="openedMenus"
            @select="handleMenuSelect"
            style="border-right:none;"
            :collapse="false"
            :collapse-transition="true"
        >
          <el-sub-menu index="/sites">
            <template #title>
              <el-icon><Odometer /></el-icon>
              <span>Sites</span>
            </template>
            <el-menu-item index="/sites/Factory">
              <span>Factory</span>
            </el-menu-item>
            <el-menu-item index="/sites/Building">
              <span>Building</span>
            </el-menu-item>
            <el-menu-item index="/sites/Airport">
              <span>Airport</span>
            </el-menu-item>
            <el-menu-item index="/sites/Shopping">
              <span>Shopping Mall</span>
            </el-menu-item>
            <el-menu-item index="/sites/Hospital">
              <span>Hospital</span>
            </el-menu-item>
            <el-menu-item index="/sites/Hotel">
              <span>Hotel</span>
            </el-menu-item>
          </el-sub-menu>

          <el-sub-menu index="/device">
            <template #title>
              <el-icon><Cpu /></el-icon>
              <span>Device</span>
            </template>
            <el-menu-item index="/device/area-topology">
              <span>Area Device Topology</span>
            </el-menu-item>
            <el-menu-item index="/device/hvac">
              <span>HVAC</span>
            </el-menu-item>
            <el-menu-item index="/device/sas">
              <span>SAS (Security)</span>
            </el-menu-item>
            <el-menu-item index="/device/fas">
              <span>FAS (Fire)</span>
            </el-menu-item>
            <el-menu-item index="/device/lighting">
              <span>Lighting Control</span>
            </el-menu-item>
            <el-menu-item index="/device/plumbing">
              <span>Plumbing</span>
            </el-menu-item>
          </el-sub-menu>

          <el-sub-menu index="/energy">
            <template #title>
              <el-icon><TrendCharts /></el-icon>
              <span>Energy & Carbon</span>
            </template>
            <el-menu-item index="/energy/wind">
              <span>Wind Energy</span>
            </el-menu-item>
            <el-menu-item index="/energy/solar">
              <span>Solar Energy</span>
            </el-menu-item>
            <el-menu-item index="/energy/electricity">
              <span>Electricity Energy</span>
            </el-menu-item>
            <el-menu-item index="/energy/waste">
              <span>Waste to Energy</span>
            </el-menu-item>
            <el-menu-item index="/energy/hydrogen">
              <span>Hydrogen Energy</span>
            </el-menu-item>
            <el-menu-item index="/energy/storage">
              <span>Energy Storage</span>
            </el-menu-item>
            <el-menu-item index="/energy/geothermal">
              <span>Geothermal Energy</span>
            </el-menu-item>
          </el-sub-menu>

          <el-sub-menu index="/property">
            <template #title>
              <el-icon><House /></el-icon>
              <span>Smart Facility</span>
            </template>
            <el-menu-item index="/property/parking">
              <span>Parking Management</span>
            </el-menu-item>
            <el-menu-item index="/property/visitor">
              <span>Visitor Management</span>
            </el-menu-item>
            <el-menu-item index="/property/space">
              <span>Space Management</span>
            </el-menu-item>
            <el-menu-item index="/property/waste">
              <span>Waste Management</span>
            </el-menu-item>
          </el-sub-menu>

          <el-sub-menu index="/blockchain">
            <template #title>
              <el-icon><Connection /></el-icon>
              <span>Blockchain Services</span>
            </template>
            <el-menu-item index="/blockchain/node">
              <span>Node Management</span>
            </el-menu-item>
            <el-menu-item index="/blockchain/web3">
              <span>Web3 Services</span>
            </el-menu-item>
            <el-menu-item index="/blockchain/did">
              <span>DID Management</span>
            </el-menu-item>
            <el-menu-item index="/blockchain/introduction">
              <span>Introduction</span>
            </el-menu-item>
          </el-sub-menu>

          <el-sub-menu index="/maintain">
            <template #title>
              <el-icon><SetUp /></el-icon>
              <span>Maintenance</span>
            </template>
            <el-menu-item index="/maintain/predictive">
              <span>Predictive Maintenance</span>
            </el-menu-item>
          </el-sub-menu>

          <el-sub-menu index="/carbon">
            <template #title>
              <el-icon><PieChart /></el-icon>
              <span>Carbon Credit</span>
            </template>
            <el-menu-item index="/carbon/realtime">
              <span>Carbon Emission</span>
            </el-menu-item>
          </el-sub-menu>

          <el-sub-menu index="/alarm">
            <template #title>
              <el-icon><PieChart /></el-icon>
              <span>Alarm Center</span>
            </template>
            <el-menu-item index="/alarm/index">
              <span>Alarm Center</span>
            </el-menu-item>
            <el-menu-item index="/alarm/notify">
              <span>Multi‑dim Notification</span>
            </el-menu-item>
          </el-sub-menu>






          <el-menu-item index="/report">
            <el-icon><DataLine /></el-icon>
            <span>Data Reports</span>
          </el-menu-item>


          <el-sub-menu index="/support">
            <template #title>
              <el-icon><Headset /></el-icon>
              <span>Terminal</span>
            </template>
            <el-menu-item index="/support/mobile">
              <span>Mobile Terminal</span>
            </el-menu-item>

          </el-sub-menu>

          <el-sub-menu index="/settings">
            <template #title>
              <el-icon><Setting /></el-icon>
              <span>System Settings</span>
            </template>
            <el-menu-item index="/settings/voice-cmd">
              <span>Voice Command Settings</span>
            </el-menu-item>
            <el-menu-item index="/settings/tts-rule">
              <span>TTS Broadcast Rules</span>
            </el-menu-item>

            <el-menu-item index="/settings/lang">
              <span>Multi-language Pack</span>
            </el-menu-item>
            <el-menu-item index="/settings/voice-log">
              <span>Voice Training Logs</span>
            </el-menu-item>
          </el-sub-menu>
        </el-menu>
      </div>

      <div class="sidebar-footer">
        <span>© {{ new Date().getFullYear() }} AegisNexus All rights reserved.</span>
      </div>
    </el-aside>

    <el-container class="main-container">
      <!-- 顶部栏 -->
      <el-header
          class="header-bar"
          :style="{
      height: isFullscreen ? '0' : (isMobile ? '48px' : '60px'),
      opacity: isFullscreen ? 0 : 1,
      padding: isFullscreen ? 0 : (isMobile ? '0 8px' : '0 16px')
    }"
      >
        <!-- 移动端顶部 -->
        <div class="header-mobile" v-if="isMobile && !isFullscreen">
          <el-icon class="menu-icon" @click="toggleMobileSidebar">
            <Expand />
          </el-icon>
        </div>

        <!-- 快捷按钮组 - 动态显示/隐藏按钮 -->
        <div class="header-controls" ref="controlsRef">
          <!-- 语音助手 - 始终显示 -->
          <el-button
              size="small"
              :type="isListening ? 'danger' : ''"
              :icon="Microphone"
              class="control-btn voice-btn pill-btn"
              :class="{ 'is-recording': isListening }"
              @click="toggleVoiceAssistant"
          >
            <span v-if="!isMobile && visibleButtons.voice">Voice</span>
            <span v-if="isListening" class="recording-wave">
                <span class="wave-bar" v-for="i in 5" :key="i" :style="{ animationDelay: `${i * 0.1}s` }"></span>
            </span>
          </el-button>

          <!-- 告警中心 - 始终显示 -->
          <el-badge :value="unacknowledgedAlarms" :hidden="unacknowledgedAlarms === 0" class="control-badge">
            <el-button
                size="small"
                :icon="Bell"
                class="control-btn pill-btn"
                @click="openAlarmDrawer"
            >
              <span v-if="!isMobile && visibleButtons.alarm">Alarm</span>
            </el-button>
          </el-badge>

          <!-- 我的工单 - 始终显示 -->
          <el-badge :value="pendingWorkOrders" :hidden="pendingWorkOrders === 0" class="control-badge">
            <el-button
                size="small"
                :icon="Tickets"
                class="control-btn pill-btn"
                @click="openWorkOrderDialog"
            >
              <span v-if="!isMobile && visibleButtons.orders">Orders</span>
            </el-button>
          </el-badge>

          <!-- ===== 可折叠按钮组 ===== -->
          <!-- 扫码巡检 -->
          <el-button
              v-show="visibleButtons.inspection"
              size="small"
              :icon="Camera"
              class="control-btn pill-btn"
              @click="startScanInspection"
          >
            <span v-if="!isMobile">Inspection</span>
          </el-button>

          <!-- Door 高亮按钮 -->
          <el-dropdown
              v-show="visibleButtons.door"
              trigger="click"
              @command="handleDoorOpen"
          >
            <el-button size="small" class="highlight-btn highlight-door pill-btn" :icon="Lock">
              Door
              <el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="lobby">
                  <el-icon><OfficeBuilding /></el-icon>
                  Lobby Area
                </el-dropdown-item>
                <el-dropdown-item command="parking">
                  <el-icon><Van /></el-icon>
                  Parking Area
                </el-dropdown-item>
                <el-dropdown-item command="office">
                  <el-icon><Grid /></el-icon>
                  Office Area
                </el-dropdown-item>
                <el-dropdown-item divided command="all">
                  <el-icon><Key /></el-icon>
                  Open All Doors
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>

          <!-- Light 高亮按钮 -->
          <el-dropdown
              v-show="visibleButtons.light"
              trigger="click"
              @command="handleLightControl"
          >
            <el-button size="small" class="highlight-btn highlight-light pill-btn" :icon="Sunny">
              Light
              <el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="lobby-on">Lobby - Lights On</el-dropdown-item>
                <el-dropdown-item command="lobby-off">Lobby - Lights Off</el-dropdown-item>
                <el-dropdown-item command="parking-on">Parking - Lights On</el-dropdown-item>
                <el-dropdown-item command="parking-off">Parking - Lights Off</el-dropdown-item>
                <el-dropdown-item divided command="all-on">All Lights On</el-dropdown-item>
                <el-dropdown-item command="all-off">All Lights Off</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>

          <!-- HVAC 高亮按钮 -->
          <el-dropdown
              v-show="visibleButtons.hvac"
              trigger="click"
              @command="handleACControl"
          >
            <el-button size="small" class="highlight-btn highlight-hvac pill-btn" :icon="ColdDrink">
              HVAC
              <el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="temp-24">Temperature 24°C</el-dropdown-item>
                <el-dropdown-item command="temp-26">Temperature 26°C</el-dropdown-item>
                <el-dropdown-item command="temp-28">Temperature 28°C</el-dropdown-item>
                <el-dropdown-item divided command="mode-cool">Cooling Mode</el-dropdown-item>
                <el-dropdown-item command="mode-fan">Fan Mode</el-dropdown-item>
                <el-dropdown-item divided command="all-off">Turn Off All</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>

          <!-- Repair 高亮按钮 -->
          <el-button
              v-show="visibleButtons.repair"
              size="small"
              class="highlight-btn highlight-repair pill-btn"
              :icon="Tools"
              @click="openQuickRepair"
          >
            <span>Repair</span>
          </el-button>



          <!-- 通知中心 -->
          <el-badge
              v-show="visibleButtons.notify"
              :value="unreadNotifications"
              :hidden="unreadNotifications === 0"
              class="control-badge"
          >
            <el-button size="small" :icon="Message" class="control-btn pill-btn" @click="openNotificationCenter">
              <span v-if="!isMobile">Notify</span>
            </el-button>
          </el-badge>

          <!-- 紧急按钮 -->
          <el-button
              v-show="visibleButtons.emergency"
              size="small"
              type="danger"
              :icon="WarningFilled"
              class="control-btn emergency-btn pill-btn"
              @click="handleEmergency"
          >
            <span v-if="!isMobile">Emergency</span>
          </el-button>

          <!-- 全局搜索 -->
          <el-button
              v-show="visibleButtons.search"
              size="small"
              :icon="Search"
              class="control-btn pill-btn"
              @click="openGlobalSearch"
              style="margin-left: 0px;"
          >
            <span v-if="!isMobile">Search</span>
          </el-button>

          <!-- 节能模式下拉按钮组 - 紧凑版 -->
          <template v-if="isInDashboardChildren && !isMobile">
            <el-dropdown trigger="click" @command="handleEnergyCommand" class="energy-dropdown">
              <el-button size="small" class="energy-btn pill-btn">
                <span class="energy-icon">⚡</span>
                <span class="energy-text">Eco</span>
                <el-icon class="el-icon--right"><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu class="energy-dropdown-menu">
                  <div class="energy-dropdown-header">
                    <span>Energy Controls</span>
                  </div>

                  <el-dropdown-item command="toggle-saving" class="energy-item">
                    <div class="energy-item-content">
                      <span class="energy-item-icon">{{ isEnergySavingActive ? '🟢' : '⚪' }}</span>
                      <span class="energy-item-label">Energy Saving</span>
                      <span class="energy-item-status" :class="{ 'status-on': isEnergySavingActive }">
                        {{ isEnergySavingActive ? 'ON' : 'OFF' }}
                      </span>
                    </div>
                  </el-dropdown-item>

                  <el-dropdown-item
                      command="toggle-report"
                      :disabled="!isEnergySavingActive"
                      class="energy-item"
                      :class="{ 'disabled-item': !isEnergySavingActive }"
                  >
                    <div class="energy-item-content">
                      <span class="energy-item-icon">{{ showEnergyReport ? '🟢' : '⚪' }}</span>
                      <span class="energy-item-label">Report</span>
                      <span class="energy-item-status" :class="{ 'status-on': showEnergyReport }">
                        {{ showEnergyReport ? 'ON' : 'OFF' }}
                      </span>
                    </div>
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>

          <!-- 更多菜单 - 显示被折叠的按钮 -->
          <el-dropdown
              v-if="foldedButtonsList.length > 0"
              trigger="click"
              @command="handleMoreCommand"
          >
            <el-button size="small" :icon="MoreFilled" class="control-btn pill-btn">
              <span v-if="!isMobile">More ({{ foldedButtonsList.length }})</span>
              <el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <template v-for="btn in foldedButtonsList" :key="btn.key">
                  <el-dropdown-item :command="btn.key">
                    <el-icon v-if="btn.icon"><component :is="btn.icon" /></el-icon>
                    {{ btn.label }}
                  </el-dropdown-item>
                </template>
                <el-dropdown-item divided command="emergency" v-if="!visibleButtons.emergency">
                  <span style="color: #f56c6c">Emergency Lockdown</span>
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>

        <!-- 右侧工具 -->
        <div class="header-tools" v-if="!isFullscreen">
          <el-tooltip v-if="!isMobile" :content="isMuted ? 'Unmute' : 'Mute'" placement="bottom">
            <el-button
                size="small"
                :icon="isMuted ? Mute : Microphone"
                circle
                class="mute-btn pill-btn"
                @click="toggleMute"
            />
          </el-tooltip>

          <el-tooltip v-if="!isMobile" :content="isFullscreen ? 'Exit Fullscreen' : 'Fullscreen'" placement="bottom">
            <FullScreen class="fullscreen-icon hover-glow" @click="toggleFullScreen" />
          </el-tooltip>

          <!-- 时间显示 - 完整格式 -->
          <div class="singapore-time glass-time" v-if="!isMobile">{{ singaporeTime }}</div>
          <div class="singapore-time mobile-time glass-time" v-if="isMobile">{{ mobileTimeDisplay }}</div>



          <el-dropdown trigger="click" @command="handleUserCommand" class="user-dropdown">
            <span class="user-avatar glass-avatar">
                <el-avatar :size="isMobile ? 28 : 32" :src="userAvatar" />
              <!-- <span class="user-name" v-if="!isMobile">{{ userName }}</span> -->
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <div class="user-info-header">
                  <el-avatar :size="32" :src="userAvatar" />
                  <div>
                    <div class="user-display-name">{{ userName }}</div>
                    <div class="user-role">{{ userRole }}</div>
                  </div>
                </div>
                <el-dropdown-item divided command="changePassword">
                  <el-icon><Lock /></el-icon>
                  Change Password
                </el-dropdown-item>
                <el-dropdown-item command="switchRole" v-if="hasMultipleRoles">
                  <el-icon><Switch /></el-icon>
                  Switch Role
                </el-dropdown-item>
                <el-dropdown-item command="languageSettings">
                  <el-icon><ChatLineSquare /></el-icon>
                  Language
                </el-dropdown-item>
                <el-dropdown-item divided command="logout">
                  <el-icon><SwitchButton /></el-icon>
                  Logout
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- 弹窗组件保持不变 -->
      <el-drawer
          v-model="alarmDrawerVisible"
          title="Alarm Center"
          direction="rtl"
          :size="isMobile ? '100%' : '400px'"
      >
        <div class="alarm-list">
          <div v-for="alarm in recentAlarms" :key="alarm.id" class="alarm-item" :class="alarm.severity">
            <div class="alarm-header">
              <el-tag :type="getAlarmType(alarm.severity)" size="small">
                {{ alarm.severity.toUpperCase() }}
              </el-tag>
              <span class="alarm-time">{{ alarm.time }}</span>
            </div>
            <div class="alarm-message">{{ alarm.message }}</div>
            <div class="alarm-actions">
              <el-button size="small" @click="acknowledgeAlarm(alarm.id)">Acknowledge</el-button>
              <el-button size="small" type="primary" @click="viewAlarmDetail(alarm.id)">Details</el-button>
              <el-button size="small" type="success" @click="createWorkOrderFromAlarm(alarm.id)">Create WO</el-button>
            </div>
          </div>
        </div>
        <div class="alarm-footer">
          <el-button type="primary" @click="viewAllAlarms">View All Alarms</el-button>
        </div>
      </el-drawer>

      <el-dialog
          v-model="workOrderDialogVisible"
          title="My Work Orders"
          :width="isMobile ? '95%' : '600px'"
          :fullscreen="isMobile"
      >
        <div class="work-order-list">
          <div v-for="order in myWorkOrders" :key="order.id" class="work-order-item">
            <div class="wo-header">
              <span class="wo-id">#{{ order.id }}</span>
              <el-tag :type="order.priority === 'high' ? 'danger' : 'warning'" size="small">
                {{ order.priority }}
              </el-tag>
            </div>
            <div class="wo-title">{{ order.title }}</div>
            <div class="wo-meta">
              <span>{{ order.location }}</span>
              <span>{{ order.createdAt }}</span>
            </div>
            <div class="wo-actions">
              <el-button size="small" @click="startProcessing(order.id)">Start</el-button>
              <el-button size="small" type="success" @click="completeWorkOrder(order.id)">Complete</el-button>
            </div>
          </div>
        </div>
      </el-dialog>

      <el-dialog
          v-model="searchDialogVisible"
          title="Global Search"
          :width="isMobile ? '95%' : '500px'"
          :fullscreen="isMobile"
      >
        <div class="search-input-wrapper">
          <el-input
              v-model="searchKeyword"
              placeholder="Search devices, orders, sensors..."
              size="large"
              clearable
              @keyup.enter="performSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
            <template #append>
              <el-button :icon="Microphone" @click="startVoiceSearch" />
            </template>
          </el-input>
        </div>
        <div class="search-results" v-if="searchResults.length > 0">
          <div v-for="(group, type) in groupedResults" :key="type" class="result-group">
            <div class="result-type">{{ type }}</div>
            <div v-for="item in group" :key="item.id" class="result-item" @click="navigateToResult(item)">
              <span>{{ item.name || item.title }}</span>
              <span class="result-path">{{ item.location || item.path }}</span>
            </div>
          </div>
        </div>
      </el-dialog>

      <el-dialog
          v-model="quickRepairVisible"
          title="Quick Repair"
          :width="isMobile ? '95%' : '500px'"
          :fullscreen="isMobile"
      >
        <el-form :model="repairForm" label-position="top" size="default">
          <el-form-item label="Device Location" required>
            <el-select v-model="repairForm.location" placeholder="Select location" style="width: 100%">
              <el-option label="Lobby - HVAC Unit 1" value="lobby-hvac-1" />
              <el-option label="Parking B1 - Light Array" value="parking-light" />
              <el-option label="Office 3F - AC System" value="office-ac" />
            </el-select>
          </el-form-item>
          <el-form-item label="Description" required>
            <el-input v-model="repairForm.description" type="textarea" :rows="3" placeholder="Describe the issue..." />
            <el-button :icon="Microphone" size="small" @click="startVoiceInput" style="margin-top: 8px">Voice Input</el-button>
          </el-form-item>
          <el-form-item label="Photo Upload">
            <el-upload v-model:file-list="repairForm.photos" action="#" list-type="picture-card" :auto-upload="false" :limit="3">
              <el-icon><Plus /></el-icon>
            </el-upload>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="submitRepair" :loading="submittingRepair">Submit</el-button>
            <el-button @click="quickRepairVisible = false">Cancel</el-button>
          </el-form-item>
        </el-form>
      </el-dialog>

      <el-dialog
          v-model="scanDialogVisible"
          title="Scan Inspection"
          :width="isMobile ? '95%' : '450px'"
          :fullscreen="isMobile"
      >
        <div class="scan-container">
          <div class="camera-view" v-if="!scanResult">
            <el-icon :size="64"><Camera /></el-icon>
            <p>Point camera at NFC tag or QR code</p>
            <el-button type="primary" @click="simulateScan" :loading="scanning" size="large">Simulate Scan</el-button>
          </div>
          <div class="inspection-result" v-if="scanResult">
            <el-result
                :icon="scanResult.success ? 'success' : 'warning'"
                :title="scanResult.success ? 'Check-in Successful' : 'Inspection Alert'"
                :sub-title="scanResult.message"
            >
              <template #extra>
                <el-button v-if="!scanResult.success" type="primary" @click="createInspectionWorkOrder">Create Work Order</el-button>
                <el-button v-if="scanResult.success" @click="scanAgain">Scan Another</el-button>
              </template>
            </el-result>
          </div>
        </div>
      </el-dialog>

      <el-drawer
          v-model="notificationDrawerVisible"
          title="Notifications"
          direction="rtl"
          :size="isMobile ? '100%' : '400px'"
      >
        <div class="notification-list">
          <div v-for="notification in notifications" :key="notification.id"
               class="notification-item" :class="{ unread: !notification.read }">
            <div class="notif-content" @click="handleNotificationClick(notification)">
              <div class="notif-title">{{ notification.title }}</div>
              <div class="notif-message">{{ notification.message }}</div>
              <div class="notif-time">{{ notification.time }}</div>
            </div>
            <div class="notif-actions">
              <el-button size="small" text @click="markAsRead(notification.id)" v-if="!notification.read">Read</el-button>
              <el-button size="small" text type="danger" @click="deleteNotification(notification.id)">Delete</el-button>
            </div>
          </div>
        </div>
        <div class="notification-footer" v-if="notifications.length > 0">
          <el-button size="small" @click="markAllAsRead">Mark All Read</el-button>
          <el-button size="small" type="danger" @click="clearAllNotifications">Clear All</el-button>
        </div>
      </el-drawer>

      <el-main class="main-content" :style="{ padding: isFullscreen ? '0' : '0px' }">
        <div v-if="hasError" class="error-placeholder">
          <el-result icon="error" title="Page Load Failed" :sub-title="errorMessage">
            <template #extra>
              <el-button type="primary" @click="reloadRoute">Reload</el-button>
            </template>
          </el-result>
        </div>
        <router-view v-else :key="$route.fullPath" v-slot="{ Component }">
          <component :is="Component" />
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted, watch, onErrorCaptured, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Odometer, Cpu, TrendCharts, House, Connection, Bell, SetUp, PieChart,
  DataLine, Headset, Setting, FullScreen, Expand, Lock, ArrowDown,
  Sunny, ColdDrink, Microphone, Camera, Search, Message, Tickets,
  MoreFilled, User, Switch, ChatLineSquare, SwitchButton, Plus,
  Mute, Tools, WarningFilled, OfficeBuilding, Van, Grid, Key
} from '@element-plus/icons-vue'
import { useCounterStore } from '@/stores/counter.js'

const route = useRoute()
const router = useRouter()
const { locale } = useI18n()
const isFullscreen = ref(false)
const counterStore = useCounterStore()

const isMobile = ref(false)
const mobileSidebarVisible = ref(false)
const controlsRef = ref(null)

// 按钮可见性控制
const visibleButtons = ref({
  voice: true,
  alarm: true,
  orders: true,
  inspection: true,
  door: true,
  light: true,
  hvac: true,
  repair: true,
  search: true,
  notify: true,
  emergency: true
})

// 按钮配置列表（用于折叠排序）
const allButtons = [
  { key: 'inspection', label: 'Scan Inspection', icon: Camera, priority: 1 },
  { key: 'door', label: 'Door Control', icon: Lock, priority: 2 },
  { key: 'light', label: 'Lighting Control', icon: Sunny, priority: 3 },
  { key: 'hvac', label: 'HVAC Control', icon: ColdDrink, priority: 4 },
  { key: 'repair', label: 'Quick Repair', icon: Tools, priority: 5 },
  { key: 'search', label: 'Global Search', icon: Search, priority: 6 },
  { key: 'notify', label: 'Notifications', icon: Message, priority: 7 }
]

// 紧急按钮单独处理
const emergencyButton = { key: 'emergency', label: 'Emergency Lockdown', icon: WarningFilled, priority: 8 }

// 被折叠的按钮列表
const foldedButtonsList = computed(() => {
  return allButtons.filter(btn => !visibleButtons.value[btn.key])
})

const userName = ref('AegisNexus')
const userRole = ref('Maintenance Engineer')
const userAvatar = ref('https://aegisnx.com/wp-content/uploads/2026/05/favicon.ico')
const hasMultipleRoles = ref(true)

const currentScene = ref('Factory')
const scenes = [
  { name: 'Factory', path: '/Factory' },
  { name: 'Building', path: '/Building' },
  { name: 'Airport', path: '/Airport' },
  { name: 'Shopping Mall', path: '/Shopping' },
  { name: 'Hospital', path: '/Hospital' },
  { name: 'Hotel', path: '/Hotel' }
]

const hasError = ref(false)
const errorMessage = ref('')

// ===== 时间 - 保留完整年月日毫秒 =====
const singaporeTime = ref('')
let timeTimer = null

const mobileTimeDisplay = computed(() => {
  if (isMobile.value) {
    const parts = singaporeTime.value.split(' ')
    if (parts.length >= 2) {
      return parts[1]
    }
  }
  return singaporeTime.value
})

// 从 store 中获取状态
const isEnergySavingActive = computed({
  get: () => counterStore.isEnergySavingActive,
  set: (val) => counterStore.setEnergySavingActive(val)
})

const showEnergyReport = computed({
  get: () => counterStore.showEnergyReport,
  set: (val) => counterStore.setShowEnergyReport(val)
})

// 添加判断是否在 Sites 子页面的计算属性
const isInDashboardChildren = computed(() => {
  const dashboardChildren = [
    '/Factory',
    '/Building',
    '/Airport',
    '/Shopping',
    '/Hospital',
    '/Hotel'
  ]
  return dashboardChildren.includes(route.path)
})

// 节能模式切换处理
const handleEnergySavingToggle = (value) => {
  ElMessage.success(`Energy Saving mode ${value ? 'activated' : 'deactivated'}`)
  if (!value) {
    showEnergyReport.value = false
  }
}

// 处理节能模式下拉命令
const handleEnergyCommand = (command) => {
  switch (command) {
    case 'toggle-saving':
      isEnergySavingActive.value = !isEnergySavingActive.value
      handleEnergySavingToggle(isEnergySavingActive.value)
      break
    case 'toggle-report':
      if (isEnergySavingActive.value) {
        showEnergyReport.value = !showEnergyReport.value
        ElMessage.success(`Report ${showEnergyReport.value ? 'enabled' : 'disabled'}`)
      }
      break
  }
}

const updateSingaporeTime = () => {
  const now = new Date()
  const utc = now.getTime() + (now.getTimezoneOffset() * 60000)
  const sgTime = new Date(utc + (8 * 3600000))

  const year = sgTime.getFullYear()
  const month = String(sgTime.getMonth() + 1).padStart(2, '0')
  const day = String(sgTime.getDate()).padStart(2, '0')
  const hours = String(sgTime.getHours()).padStart(2, '0')
  const minutes = String(sgTime.getMinutes()).padStart(2, '0')
  const seconds = String(sgTime.getSeconds()).padStart(2, '0')
  const ms = String(sgTime.getMilliseconds()).padStart(3, '0')

  singaporeTime.value = `${year}-${month}-${day} ${hours}:${minutes}:${seconds}.${ms} SGT`
}

const isListening = ref(false)
const isMuted = ref(false)

const unacknowledgedAlarms = ref(3)
const alarmDrawerVisible = ref(false)
const recentAlarms = ref([
  { id: 1, severity: 'critical', time: '2026-05-14 10:23:15', message: 'Fire alarm triggered in Warehouse B2' },
  { id: 2, severity: 'major', time: '2026-05-14 10:15:42', message: 'HVAC system failure in Office 3F' },
  { id: 3, severity: 'major', time: '2026-05-14 10:05:18', message: 'Power fluctuation detected in Server Room' },
  { id: 4, severity: 'minor', time: '2026-05-14 09:58:33', message: 'Temperature elevated in Data Center' },
  { id: 5, severity: 'minor', time: '2026-05-14 09:45:21', message: 'Door sensor offline - Parking Entrance' }
])

const getAlarmType = (severity) => {
  if (severity === 'critical') return 'danger'
  if (severity === 'major') return 'warning'
  return 'info'
}

const pendingWorkOrders = ref(2)
const workOrderDialogVisible = ref(false)
const myWorkOrders = ref([
  { id: 'WO-2026-0042', title: 'Fix HVAC Unit in Office 3F', priority: 'high', location: 'Office 3F - Rm 301', createdAt: '2026-05-14 08:30' },
  { id: 'WO-2026-0038', title: 'Replace light fixtures in Parking B1', priority: 'medium', location: 'Parking B1 - Section A', createdAt: '2026-05-13 14:20' }
])

const searchDialogVisible = ref(false)
const searchKeyword = ref('')
const searchResults = ref([])
const groupedResults = computed(() => {
  const groups = {}
  searchResults.value.forEach(item => {
    if (!groups[item.type]) groups[item.type] = []
    groups[item.type].push(item)
  })
  return groups
})

const quickRepairVisible = ref(false)
const submittingRepair = ref(false)
const repairForm = ref({ location: '', description: '', photos: [] })

const scanDialogVisible = ref(false)
const scanResult = ref(null)
const scanning = ref(false)

const unreadNotifications = ref(5)
const notificationDrawerVisible = ref(false)
const notifications = ref([
  { id: 1, title: 'Work Order Updated', message: 'WO-2026-0042 status changed to In Progress', time: '5 min ago', read: false },
  { id: 2, title: 'Maintenance Reminder', message: 'Quarterly HVAC inspection due in 3 days', time: '1 hour ago', read: false },
  { id: 3, title: 'Carbon Report Ready', message: 'May carbon emission report generated', time: '3 hours ago', read: false }
])

// 方法
const handleSceneChange = (scene) => {
  const target = scenes.find(s => s.name === scene)
  if (target) {
    router.push(target.path)
    ElMessage.success(`Switched to ${scene}`)
  }
}

const toggleVoiceAssistant = () => {
  if (!isListening.value) {
    isListening.value = true
    ElMessage.info('Listening...')
    setTimeout(() => {
      isListening.value = false
      ElMessage.success('Command executed')
    }, 2000)
  } else {
    isListening.value = false
  }
}

const openAlarmDrawer = () => { alarmDrawerVisible.value = true }
const acknowledgeAlarm = (id) => {
  ElMessage.success(`Alarm #${id} acknowledged`)
  unacknowledgedAlarms.value = Math.max(0, unacknowledgedAlarms.value - 1)
}
const viewAlarmDetail = () => {
  router.push('/alarm')
  alarmDrawerVisible.value = false
}
const createWorkOrderFromAlarm = () => {
  alarmDrawerVisible.value = false
  quickRepairVisible.value = true
}
const viewAllAlarms = () => {
  router.push('/alarm')
  alarmDrawerVisible.value = false
}

const openWorkOrderDialog = () => { workOrderDialogVisible.value = true }
const startProcessing = (id) => { ElMessage.success(`Started #${id}`) }
const completeWorkOrder = (id) => {
  ElMessage.success(`Completed #${id}`)
  pendingWorkOrders.value = Math.max(0, pendingWorkOrders.value - 1)
}

const openGlobalSearch = () => {
  searchDialogVisible.value = true
  searchKeyword.value = ''
  searchResults.value = []
}
const performSearch = () => {
  if (!searchKeyword.value.trim()) return
  searchResults.value = [
    { id: 1, type: 'Devices', name: 'HVAC Unit - Office 3F', path: '/device/hvac' },
    { id: 2, type: 'Work Orders', title: 'WO-2026-0042', path: '/maintain' }
  ]
}
const startVoiceSearch = () => { ElMessage.info('Voice search activated') }
const navigateToResult = (item) => {
  if (item.path) router.push(item.path)
  searchDialogVisible.value = false
}

const handleDoorOpen = async (area) => {
  const names = { lobby: 'Lobby', parking: 'Parking', office: 'Office', all: 'All Areas' }
  try {
    await ElMessageBox.confirm(`Open doors for ${names[area]}?`, 'Confirm', {
      confirmButtonText: 'Open', cancelButtonText: 'Cancel', type: 'warning'
    })
    ElMessage.success(`Doors opened: ${names[area]}`)
  } catch {}
}

const handleLightControl = (command) => {
  const map = { 'lobby-on': 'Lobby On', 'lobby-off': 'Lobby Off', 'all-on': 'All On', 'all-off': 'All Off',
    'parking-on': 'Parking On', 'parking-off': 'Parking Off' }
  if (map[command]) ElMessage.success(map[command])
}

const handleACControl = (command) => {
  if (command.startsWith('temp-')) ElMessage.success(`Set to ${command.split('-')[1]}°C`)
  else if (command === 'mode-cool') ElMessage.success('Cooling mode')
  else if (command === 'mode-fan') ElMessage.success('Fan mode')
  else if (command === 'all-off') ElMessage.success('All AC off')
}

const handleEmergency = async () => {
  try {
    await ElMessageBox.confirm('Activate emergency protocol?', 'Emergency', {
      confirmButtonText: 'Activate', cancelButtonText: 'Cancel', type: 'error'
    })
    ElMessage({ message: 'Emergency activated!', type: 'error', duration: 5000 })
  } catch {}
}

const openQuickRepair = () => { quickRepairVisible.value = true }
const submitRepair = () => {
  if (!repairForm.value.location || !repairForm.value.description) {
    ElMessage.warning('Fill all fields')
    return
  }
  submittingRepair.value = true
  setTimeout(() => {
    submittingRepair.value = false
    ElMessage.success('Repair submitted!')
    quickRepairVisible.value = false
    repairForm.value = { location: '', description: '', photos: [] }
  }, 1000)
}
const startVoiceInput = () => { ElMessage.info('Voice input') }

const startScanInspection = () => {
  scanDialogVisible.value = true
  scanResult.value = null
}
const simulateScan = () => {
  scanning.value = true
  setTimeout(() => {
    scanning.value = false
    scanResult.value = {
      success: Math.random() > 0.3,
      message: Math.random() > 0.3 ? 'Check-in successful' : 'Temperature anomaly detected'
    }
  }, 1500)
}
const createInspectionWorkOrder = () => {
  scanDialogVisible.value = false
  quickRepairVisible.value = true
}
const scanAgain = () => { scanResult.value = null }

const openNotificationCenter = () => { notificationDrawerVisible.value = true }
const markAsRead = (id) => {
  const n = notifications.value.find(x => x.id === id)
  if (n) { n.read = true; unreadNotifications.value = Math.max(0, unreadNotifications.value - 1) }
}
const markAllAsRead = () => {
  notifications.value.forEach(n => n.read = true)
  unreadNotifications.value = 0
}
const deleteNotification = (id) => {
  notifications.value = notifications.value.filter(n => n.id !== id)
}
const clearAllNotifications = () => {
  notifications.value = []
  unreadNotifications.value = 0
}
const handleNotificationClick = () => {}

const toggleMute = () => {
  isMuted.value = !isMuted.value
  ElMessage.info(isMuted.value ? 'Muted' : 'Unmuted')
}

// 处理更多菜单的命令
const handleMoreCommand = (command) => {
  switch (command) {
    case 'inspection': startScanInspection(); break
    case 'door': handleDoorOpen('lobby'); break
    case 'light': handleLightControl('all-on'); break
    case 'hvac': handleACControl('temp-24'); break
    case 'repair': openQuickRepair(); break
    case 'search': openGlobalSearch(); break
    case 'notify': openNotificationCenter(); break
    case 'emergency': handleEmergency(); break
    default: break
  }
}

const handleUserCommand = (command) => {
  switch (command) {
    case 'logout':
      ElMessageBox.confirm('Logout?', 'Confirm', {
        confirmButtonText: 'Logout', type: 'warning'
      }).then(() => ElMessage.success('Logged out'))
      break
    default: ElMessage.info(`${command} opened`)
  }
}

const toggleMobileSidebar = () => {
  mobileSidebarVisible.value = !mobileSidebarVisible.value
  document.body.style.overflow = mobileSidebarVisible.value ? 'hidden' : ''
}
const closeMobileSidebar = () => {
  mobileSidebarVisible.value = false
  document.body.style.overflow = ''
}

// 响应式布局检测和按钮折叠逻辑
const checkResponsiveLayout = () => {
  const width = window.innerWidth
  const wasMobile = isMobile.value
  isMobile.value = width < 768

  // 根据宽度决定按钮可见性 - 所有宽度都会触发折叠
  if (width >= 850) {
    // 较大屏幕：显示所有按钮
    visibleButtons.value = {
      voice: true, alarm: true, orders: true,
      inspection: true, door: true, light: true, hvac: true,
      repair: true, search: true, notify: true, emergency: true
    }
  } else if (width >= 768) {
    // 平板横屏：隐藏部分按钮
    visibleButtons.value = {
      voice: true, alarm: true, orders: true,
      inspection: false, door: true, light: true, hvac: true,
      repair: false, search: false, notify: false, emergency: false
    }
  } else {
    // 移动端：只显示语音、告警、工单
    visibleButtons.value = {
      voice: true, alarm: true, orders: true,
      inspection: false, door: false, light: false, hvac: false,
      repair: false, search: false, notify: false, emergency: false
    }
  }

  if (!isMobile.value && wasMobile) {
    closeMobileSidebar()
  }
}

onErrorCaptured((err) => {
  hasError.value = true
  errorMessage.value = err.message || 'Error'
  return false
})

const reloadRoute = async () => {
  hasError.value = false
  try { await router.replace({ path: route.fullPath }) } catch {}
}

const activeMenu = computed(() => route.path)
const openedMenus = ref([])

const getParentMenuForPath = (path) => {
  const children = ['/Factory','/Building','/Airport','/Shopping','/Hospital','/Hotel']
  if (children.includes(path)) return '/'
  if (path.startsWith('/device/')) return '/device'
  if (path.startsWith('/energy/')) return '/energy'
  return null
}

const updateOpenedMenus = async () => {
  const parent = getParentMenuForPath(route.path)
  openedMenus.value = []
  await nextTick()
  openedMenus.value = parent ? [parent] : []
}

watch(() => route.path, () => {
  updateOpenedMenus()
  if (isMobile.value) closeMobileSidebar()
}, { immediate: true })

const handleMenuSelect = (index) => {
  if (index && index !== route.path) {
    router.push(index).catch(() => {})
  }
  if (isMobile.value) closeMobileSidebar()
}

const setLang = (l) => { locale.value = l }

const toggleFullScreen = () => {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen().catch(() => {})
  } else {
    document.exitFullscreen()
  }
}

const onFullScreenChange = () => {
  isFullscreen.value = !!document.fullscreenElement
  counterStore.setFullscreen(isFullscreen.value)
}

const onKeydown = (e) => {
  if (!isFullscreen.value || isMobile.value) return
  const menuPaths = [
    '/Factory','/Building','/Airport','/Shopping','/Hospital','/Hotel',
    '/device/area-topology','/device/hvac','/device/sas','/device/fas','/device/lighting','/device/plumbing',
    '/property/parking','/property/visitor','/property/space','/property/waste',
    '/blockchain/node','/blockchain/web3','/blockchain/did',
    '/maintain/predictive',
    '/energy/wind','/energy/solar','/energy/electricity','/energy/waste','/energy/hydrogen','/energy/storage','/energy/geothermal',
    '/carbon/realtime','/alarm','/maintain','/report','/settings'
  ]
  const idx = menuPaths.findIndex(p => p === route.path)
  if (idx === -1) return
  if (e.key === 'ArrowUp') {
    e.preventDefault()
    router.push(menuPaths[idx <= 0 ? menuPaths.length - 1 : idx - 1]).catch(() => {})
  } else if (e.key === 'ArrowDown') {
    e.preventDefault()
    router.push(menuPaths[idx >= menuPaths.length - 1 ? 0 : idx + 1]).catch(() => {})
  }
}

const handleResize = () => {
  // 使用 requestAnimationFrame 优化性能
  requestAnimationFrame(() => {
    checkResponsiveLayout()
  })
}

onMounted(() => {
  updateSingaporeTime()
  timeTimer = setInterval(updateSingaporeTime, 100)
  document.addEventListener('fullscreenchange', onFullScreenChange)
  window.addEventListener('keydown', onKeydown)
  window.addEventListener('resize', handleResize)
  checkResponsiveLayout()

  // 添加延迟检查，确保初始加载时正确
  setTimeout(() => {
    checkResponsiveLayout()
  }, 100)
})

onUnmounted(() => {
  clearInterval(timeTimer)
  document.removeEventListener('fullscreenchange', onFullScreenChange)
  window.removeEventListener('keydown', onKeydown)
  window.removeEventListener('resize', handleResize)
  document.body.style.overflow = ''
})
</script>

<style scoped>
/* ============ 侧边栏 ============ */
.sidebar {
  background: #0a1629;
  transition: all 0.3s;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.logo-box {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: left;
  color: #fff;
  gap: 10px;
  font-weight: bold;
  flex-shrink: 0;
  padding: 0 16px;
}

.logo-img {
  width: 28px;
  height: 28px;
  flex-shrink: 0;
}

.logo-text {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: 15px;
}

.menu-scroll {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.sidebar-footer {
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #0a1629;
  border-top: 1px solid rgba(255,255,255,0.08);
  color: #8899aa;
  font-size: 11px;
  flex-shrink: 0;
}

/* ============ 顶部栏 ============ */
.header-bar {
  display: flex;
  align-items: center;
  background: #0a1629;
  border-bottom: 1px solid rgba(255,255,255,0.1);
  transition: all 0.3s;
  gap: 6px;
  overflow: hidden;
}

.header-mobile {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.menu-icon {
  font-size: 22px;
  color: #fff;
  cursor: pointer;
  padding: 4px;
}

/* ===== 快捷按钮组 ===== */
.header-controls {
  display: flex;
  align-items: center;
  gap: 6px;
  flex: 1;
  overflow-x: auto;
  overflow-y: hidden;
  -webkit-overflow-scrolling: touch;
  height: 100%;
  padding-left: 0px;
  scrollbar-width:thin;
  scrollbar-color:rgba(255, 255, 255, 0.2) transparent;
}

/* Chrome / Edge / Safari 横向滚动条美化 */
.header-controls::-webkit-scrollbar {
  height: 1px;
}
.header-controls::-webkit-scrollbar-track {
  background: transparent;
}
.header-controls::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 4px;
}
.header-controls::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.35);
}

/* 普通按钮 */
.control-btn {
  border: 1px solid rgba(255,255,255,0.2);
  background: rgba(255,255,255,0.08);
  color: #e5eaf3;
  white-space: nowrap;
  font-size: 12px;
  padding: 5px 8px;
  flex-shrink: 0;
  min-height: 30px;
  transition: all 0.3s ease;
}

.control-btn:hover {
  background: rgba(255,255,255,0.15);
  border-color: rgba(255,255,255,0.4);
}

/* ===== 高亮按钮通用样式 ===== */
.highlight-btn {
  position: relative;
  font-weight: 600;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  border: 2px solid transparent;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  flex-shrink: 0;
}

.highlight-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
  transition: left 0.5s;
}

.highlight-btn:hover::before {
  left: 100%;
}

.highlight-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0,0,0,0.3);
}

.highlight-btn:active {
  transform: translateY(0);
}

/* ===== Door 按钮 - 翠绿色 ===== */
.highlight-door {
  background: linear-gradient(135deg, #00b894, #00cec9) !important;
  border-color: #00b894 !important;
  color: #fff !important;
  text-shadow: 0 1px 2px rgba(0,0,0,0.2);
}

.highlight-door:hover {
  background: linear-gradient(135deg, #00cec9, #00b894) !important;
  box-shadow: 0 4px 20px rgba(0, 184, 148, 0.5);
  border-color: #00dfa2 !important;
}

/* ===== Light 按钮 - 琥珀金橙色 ===== */
.highlight-light {
  background: linear-gradient(135deg, #f39c12, #f1c40f) !important;
  border-color: #f39c12 !important;
  color: #fff !important;
  text-shadow: 0 1px 2px rgba(0,0,0,0.2);
}

.highlight-light:hover {
  background: linear-gradient(135deg, #f1c40f, #f39c12) !important;
  box-shadow: 0 4px 20px rgba(243, 156, 18, 0.5);
  border-color: #ffbe76 !important;
}

/* ===== HVAC 按钮 - 科技蓝 ===== */
.highlight-hvac {
  background: linear-gradient(135deg, #0984e3, #74b9ff) !important;
  border-color: #0984e3 !important;
  color: #fff !important;
  text-shadow: 0 1px 2px rgba(0,0,0,0.2);
}

.highlight-hvac:hover {
  background: linear-gradient(135deg, #74b9ff, #0984e3) !important;
  box-shadow: 0 4px 20px rgba(9, 132, 227, 0.5);
  border-color: #6c5ce7 !important;
}

/* ===== Repair 按钮 - 紫罗兰渐变 ===== */
.highlight-repair {
  background: linear-gradient(135deg, #6c5ce7, #a29bfe) !important;
  border-color: #6c5ce7 !important;
  color: #fff !important;
  text-shadow: 0 1px 2px rgba(0,0,0,0.2);
}

.highlight-repair:hover {
  background: linear-gradient(135deg, #a29bfe, #6c5ce7) !important;
  box-shadow: 0 4px 20px rgba(108, 92, 231, 0.5);
  border-color: #fd79a8 !important;
}

/* 语音按钮录音状态 */
.voice-btn.is-recording {
  background: rgba(255,59,48,0.2);
  border-color: #ff3b30;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%,100% { box-shadow: 0 0 0 0 rgba(255,59,48,0.4); }
  50% { box-shadow: 0 0 0 6px rgba(255,59,48,0); }
}

.recording-wave {
  display: inline-flex;
  gap: 2px;
  margin-left: 3px;
  align-items: flex-end;
}

.wave-bar {
  width: 3px;
  height: 10px;
  background: #ff3b30;
  border-radius: 2px;
  animation: wave 1s ease-in-out infinite;
}

@keyframes wave {
  0%,100% { height: 5px; }
  50% { height: 14px; }
}

.control-badge { flex-shrink: 0; }
.control-badge :deep(.el-badge__content) {
  background: #ff3b30;
  border: none;
  font-size: 10px;
  height: 16px;
  line-height: 16px;
  padding: 0 4px;
}

.emergency-btn {
  background: rgba(255,59,48,0.15) !important;
  border-color: rgba(255,59,48,0.3) !important;
  animation: emergencyGlow 2s infinite;
}

@keyframes emergencyGlow {
  0%, 100% { box-shadow: 0 0 5px rgba(255,59,48,0.3); }
  50% { box-shadow: 0 0 15px rgba(255,59,48,0.5); }
}

/* ============ 节能模式下拉按钮 ============ */

/* 紧凑的下拉按钮 */
.energy-btn {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(5, 150, 105, 0.1)) !important;
  border: 1px solid rgba(16, 185, 129, 0.3) !important;
  color: #10b981 !important;
  font-weight: 600;
  font-size: 11px;
  padding: 4px 10px;
  min-height: 30px;
  transition: all 0.3s ease;
  letter-spacing: 0.5px;
}

.energy-btn:hover {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.25), rgba(5, 150, 105, 0.2)) !important;
  border-color: rgba(16, 185, 129, 0.5) !important;
  box-shadow: 0 0 12px rgba(16, 185, 129, 0.3);
  transform: translateY(-1px);
}

.energy-icon {
  font-size: 13px;
  margin-right: 3px;
}

.energy-text {
  font-size: 11px;
  text-transform: uppercase;
  font-weight: 600;
}

/* 下拉菜单样式 */
.energy-dropdown-menu {
  min-width: 220px !important;
  padding: 4px 0 !important;
}

.energy-dropdown-header {
  padding: 8px 16px 6px;
  font-size: 11px;
  font-weight: 600;
  color: #909399;
  text-transform: uppercase;
  letter-spacing: 1px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  margin-bottom: 4px;
}

.energy-item {
  padding: 0 !important;
}

.energy-item-content {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 16px;
  width: 100%;
  transition: all 0.2s ease;
}

.energy-item:hover .energy-item-content {
  background: rgba(16, 185, 129, 0.05);
}

.energy-item-icon {
  font-size: 12px;
  flex-shrink: 0;
}

.energy-item-label {
  flex: 1;
  font-size: 13px;
  font-weight: 500;
  color: #303133;
}

.energy-item-status {
  font-size: 11px;
  font-weight: 700;
  padding: 3px 10px;
  border-radius: 10px;
  background: rgba(144, 147, 153, 0.1);
  color: #909399;
  min-width: 36px;
  text-align: center;
}

.energy-item-status.status-on {
  background: rgba(16, 185, 129, 0.15);
  color: #10b981;
  box-shadow: 0 0 8px rgba(16, 185, 129, 0.2);
}

/* 禁用状态 */
.disabled-item {
  opacity: 0.45;
  cursor: not-allowed !important;
}

.disabled-item:hover {
  background: none !important;
}

.disabled-item .energy-item-content {
  cursor: not-allowed;
}

.disabled-item .energy-item-status {
  background: rgba(144, 147, 153, 0.08) !important;
  color: #909399 !important;
  box-shadow: none !important;
}

/* ===== 右侧工具 ===== */
.header-tools {
  display: flex;
  gap: 6px;
  align-items: center;
  flex-shrink: 0;
}

.mute-btn {
  border: 1px solid rgba(255,255,255,0.2);
  background: rgba(255,255,255,0.08);
  color: #e5eaf3;
  width: 30px;
  height: 30px;
  padding: 0;
}

/* ===== 时间显示 ===== */
.singapore-time {
  font-family: 'JetBrains Mono', 'Consolas', 'Monaco', monospace;
  font-size: 12px;
  color: #00ffcc;
  background: rgba(0, 255, 204, 0.08);
  padding: 4px 10px;
  border-radius: 6px;
  border: 1px solid rgba(0, 255, 204, 0.2);
  white-space: nowrap;
  letter-spacing: 0.5px;
  text-shadow: 0 0 8px rgba(0, 255, 204, 0.3);
  animation: timeGlow 3s ease-in-out infinite;
}

@keyframes timeGlow {
  0%, 100% {
    box-shadow: 0 0 5px rgba(0, 255, 204, 0.2);
    border-color: rgba(0, 255, 204, 0.2);
  }
  50% {
    box-shadow: 0 0 15px rgba(0, 255, 204, 0.4);
    border-color: rgba(0, 255, 204, 0.4);
  }
}

.mobile-time {
  font-size: 10px;
  padding: 2px 5px;
}

.fullscreen-icon {
  width: 28px;
  height: 28px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  transition: all 0.3s;
}

.fullscreen-icon:hover {
  color: #409eff;
  transform: scale(1.1);
}

.user-dropdown { cursor: pointer; }

.user-avatar {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 2px 6px;
  border-radius: 20px;
  background: rgba(255,255,255,0.1);
  white-space: nowrap;
  transition: all 0.3s;
  margin-left: 10px;
}

.user-avatar:hover {
  background: rgba(255,255,255,0.2);
}

.user-name {
  color: #fff;
  font-size: 12px;
  max-width: 80px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-info-header {
  padding: 6px 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  border-bottom: 1px solid #eee;
  margin-bottom: 4px;
}

.user-display-name { font-weight: 600; font-size: 12px; }
.user-role { font-size: 10px; color: #909399; }

/* ============ 弹窗样式 ============ */
.alarm-list {
  max-height: calc(100vh - 140px);
  overflow-y: auto;
}

.alarm-item {
  padding: 10px;
  border-bottom: 1px solid #eee;
  border-left: 3px solid transparent;
  margin-bottom: 6px;
  border-radius: 4px;
}

.alarm-item.critical { border-left-color: #f56c6c; background: #fef0f0; }
.alarm-item.major { border-left-color: #e6a23c; background: #fdf6ec; }
.alarm-item.minor { border-left-color: #409eff; background: #ecf5ff; }

.alarm-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.alarm-time { font-size: 11px; color: #909399; }
.alarm-message { margin-bottom: 6px; font-size: 13px; }
.alarm-actions { display: flex; gap: 4px; flex-wrap: wrap; }
.alarm-footer { padding: 10px 0; text-align: center; border-top: 1px solid #eee; }

.work-order-list { max-height: 400px; overflow-y: auto; }

.work-order-item {
  padding: 10px;
  border: 1px solid #eee;
  border-radius: 8px;
  margin-bottom: 10px;
}

.wo-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
}

.wo-id { font-weight: 600; color: #409eff; }
.wo-title { font-size: 13px; margin-bottom: 4px; }
.wo-meta { font-size: 11px; color: #909399; display: flex; gap: 12px; margin-bottom: 6px; }
.wo-actions { display: flex; gap: 6px; }

.search-input-wrapper { margin-bottom: 14px; }
.search-results { max-height: 350px; overflow-y: auto; }

.result-group { margin-bottom: 14px; }

.result-type {
  font-weight: 600;
  color: #909399;
  font-size: 11px;
  text-transform: uppercase;
  margin-bottom: 6px;
  padding-bottom: 4px;
  border-bottom: 1px solid #eee;
}

.result-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 7px 10px;
  cursor: pointer;
  border-radius: 4px;
  font-size: 13px;
}

.result-item:hover { background: #f5f7fa; }
.result-path { font-size: 11px; color: #909399; }

.notification-list { max-height: calc(100vh - 140px); overflow-y: auto; }

.notification-item {
  display: flex;
  justify-content: space-between;
  padding: 10px;
  border-bottom: 1px solid #eee;
  align-items: flex-start;
}

.notification-item.unread { background: #ecf5ff; }

.notif-content { flex: 1; cursor: pointer; margin-right: 8px; }
.notif-title { font-weight: 600; font-size: 13px; }
.notif-message { font-size: 12px; color: #666; margin: 3px 0; }
.notif-time { font-size: 11px; color: #999; }

.notif-actions {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex-shrink: 0;
}

.notification-footer {
  padding: 10px 0;
  text-align: center;
  border-top: 1px solid #eee;
  display: flex;
  justify-content: center;
  gap: 8px;
}

.scan-container { text-align: center; padding: 20px; }

.camera-view {
  padding: 24px;
  background: #f5f7fa;
  border-radius: 8px;
  border: 2px dashed #dcdfe6;
}

.camera-view p { margin: 12px 0; color: #909399; }

.main-container {
  position: relative;
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-content {
  background: #f5f7fa;
  overflow: auto;
  padding: 0 !important;
  flex: 1;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.error-placeholder {
  padding: 20px;
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
}

.mobile-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  z-index: 1999;
  backdrop-filter: blur(2px);
}

.fade-enter-active,
.fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from,
.fade-leave-to { opacity: 0; }

:deep(.el-menu .el-sub-menu__title),
:deep(.el-menu-item) {
  transition: all 0.25s ease !important;
}

:deep(.el-sub-menu .el-menu) {
  transition: height 0.28s cubic-bezier(0.2, 0.7, 0.3, 1) !important;
}

:deep(.el-menu) {
  -webkit-font-smoothing: antialiased;
  backface-visibility: hidden;
  transform: translateZ(0);
}

.sidebar,
.menu-scroll {
  transform: translateZ(0);
  backface-visibility: hidden;
  perspective: 1000px;
}

/* 通用圆角药丸形状 */
.pill-btn {
  border-radius: 20px !important;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

/* 普通按钮增加立体投影和背景 */
.control-btn.pill-btn {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.12) 0%, rgba(255, 255, 255, 0.02) 100%) !important;
  backdrop-filter: blur(4px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  font-weight: 500;
}

.control-btn.pill-btn:hover {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.22) 0%, rgba(255, 255, 255, 0.08) 100%) !important;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.2);
  transform: translateY(-1px);
  border-color: rgba(255, 255, 255, 0.4);
}

.control-btn.pill-btn:active {
  transform: translateY(1px);
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.2);
}

/* ============ 响应式 ============ */
@media (max-width: 767px) {
  .sidebar.mobile-sidebar {
    position: fixed;
    left: 0;
    top: 0;
    bottom: 0;
    width: 280px !important;
    z-index: 2000;
    transform: translateX(-100%);
    transition: transform 0.28s cubic-bezier(0.2, 0.7, 0.3, 1) !important;
    box-shadow: 2px 0 12px rgba(0,0,0,0.3);
  }

  .sidebar.mobile-sidebar.open { transform: translateX(0); }

  .logo-box {
    height: 48px;
    padding: 0 12px;
  }

  .logo-img {
    width: 24px;
    height: 24px;
  }

  .logo-text { font-size: 13px; }

  .header-bar {
    padding: 0 8px !important;
    height: 48px !important;
    gap: 4px;
  }

  .header-controls {
    gap: 3px;
    justify-content: flex-start;
    padding-left: 5px;
  }

  .control-btn {
    font-size: 11px;
    padding: 4px 7px;
    min-height: 28px;
  }

  .header-tools { gap: 4px; }

  .singapore-time {
    font-size: 10px;
    padding: 2px 4px;
  }

  .user-avatar { padding: 1px 4px; }

  .sidebar-footer {
    font-size: 10px;
    height: 32px;
  }

  .energy-btn {
    font-size: 10px;
    padding: 3px 8px;
    min-height: 26px;
  }

  .energy-icon {
    font-size: 11px;
  }

  .energy-text {
    font-size: 10px;
  }

  .energy-dropdown-menu {
    min-width: 200px !important;
  }
}
</style>


<style>
/* 全局字体统一为 Arial */
* {
  font-family: Arial, "Helvetica Neue", Helvetica, sans-serif !important;
  font-weight: bold;
}
</style>