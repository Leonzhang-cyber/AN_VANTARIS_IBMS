<template>
  <!-- Page Initial Loading Screen -->
  <div v-if="!isPageLoaded" class="loading-fullscreen">
    <div class="loading-content-center">
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
        <div class="progress-bar" :style="{ width: pageLoadingProgress + '%' }"></div>
      </div>
      <div class="loading-tip">Edition Menu Manager</div>
      <div class="loading-subtip">{{ pageLoadingMessage }}</div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="edition-manager">
    <div class="manager-header">
      <div class="header-title">
        <el-icon><Edit /></el-icon>
        <span>Edition Menu Manager</span>
      </div>
      <div class="header-actions">
        <el-button type="info" @click="openVersionManager">
          <el-icon><Setting /></el-icon>
          Version Management
        </el-button>
        <el-button type="success" @click="saveAllChanges" :loading="saving" :disabled="!hasChanges">
          <el-icon><Check /></el-icon>
          Save Config
        </el-button>
        <el-button @click="resetChanges" :disabled="!hasChanges">
          <el-icon><Refresh /></el-icon>
          Reset
        </el-button>
      </div>
    </div>

    <!-- Main Layout: Left Panel (Version Management) + Right Panel (All Menus Management) -->
    <div class="two-column-layout">
      <!-- Left Column: Version Selection -->
      <div class="left-panel">
        <div class="panel-header">
          <el-icon><Folder /></el-icon>
          <span>Version Selection</span>
          <div class="active-version-actions">
            <el-dropdown trigger="click" @command="handleSwitchActiveVersion">
              <el-button type="primary" size="small" :loading="switching">
                <el-icon><Switch /></el-icon>
                Switch Version
                <el-icon class="el-icon--right"><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item
                      v-for="version in allVersions"
                      :key="version.version_code"
                      :command="version.version_code"
                      :class="{ 'is-active': currentActiveVersion === version.version_code }"
                  >
                    <span class="version-option-icon">{{ version.icon || '📦' }}</span>
                    <span>{{ version.version_name }}</span>
                    <el-icon v-if="currentActiveVersion === version.version_code" class="check-icon"><Check /></el-icon>
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>

        <!-- Version Tabs -->
        <div class="version-tabs">
          <el-tabs v-model="currentEditVersion" type="card" @tab-click="handleTabChange">
            <el-tab-pane
                v-for="version in allVersions"
                :key="version.version_code"
                :name="version.version_code"
            >
              <template #label>
                <span class="tab-label" :class="{ 'is-system-active': currentActiveVersion === version.version_code }">
                  <span class="tab-icon">{{ version.icon || '📦' }}</span>
                  <span>{{ version.version_name }}</span>
                  <el-tag v-if="currentActiveVersion === version.version_code" size="small" type="primary" class="active-badge">Active</el-tag>
                </span>
              </template>
            </el-tab-pane>
          </el-tabs>
        </div>

        <!-- Version Info Bar -->
        <div class="version-info-bar">
          <div class="info-content">
            <el-icon><Edit /></el-icon>
            <span class="info-label">Editing:</span>
            <span class="version-name">{{ currentEditVersionName }}</span>
          </div>
          <div class="selection-info">
            <span>Selected: <strong>{{ currentSelectedCount }}</strong> / <strong>{{ totalMenuCount }}</strong></span>
            <el-button size="small" @click="selectAllMenus">
              <el-icon><Select /></el-icon>
              Select All
            </el-button>
            <el-button size="small" @click="deselectAllMenus">
              <el-icon><Close /></el-icon>
              Deselect All
            </el-button>
            <el-divider direction="vertical" />
            <el-button size="small" @click="expandAllVersionTree">
              <el-icon><Expand /></el-icon>
              Expand
            </el-button>
            <el-button size="small" @click="collapseAllVersionTree">
              <el-icon><Fold /></el-icon>
              Collapse
            </el-button>
          </div>
        </div>

        <!-- Menu Tree for Version (禁止拖拽排序) -->
        <div class="menu-tree-container">
          <div v-if="loading" class="loading-state">
            <el-icon class="is-loading"><Loading /></el-icon>
            <span>Loading...</span>
          </div>
          <div v-else-if="menuTree.length === 0" class="empty-state">
            <el-icon><FolderOpened /></el-icon>
            <span>No menu data</span>
          </div>
          <!--          <div v-else class="sort-hint">-->
          <!--            <el-icon><Menu /></el-icon>-->
          <!--            <span>Select menus to include in this version</span>-->
          <!--          </div>-->
          <el-tree
              ref="treeRef"
              :key="treeKey"
              :data="sortedMenuTree"
              node-key="menu_path"
              :expand-on-click-node="false"
              :highlight-current="false"
              :default-expanded-keys="expandedKeys"
          >
            <template #default="{ data }">
              <div class="tree-node">
                <div class="node-icon">
                  <el-icon v-if="data.children && data.children.length"><Folder /></el-icon>
                  <el-icon v-else><Document /></el-icon>
                </div>
                <div class="node-info">
                  <span class="node-title">{{ data.menu_title }}</span>
                  <span class="node-path">{{ data.menu_path }}</span>
                </div>
                <div class="node-checkbox">
                  <el-checkbox
                      :model-value="isMenuSelectedForCurrentVersion(data.menu_path)"
                      :disabled="isMenuItemDisabled(data)"
                      @change="(val) => toggleMenuSelection(data, val)"
                  />
                </div>
              </div>
            </template>
          </el-tree>
        </div>
      </div>

      <!-- Right Column: All Menus Management -->
      <div class="right-panel">
        <div class="panel-header">
          <el-icon><List /></el-icon>
          <span>All Menus Management</span>
          <div class="right-panel-actions">
            <el-button size="small" @click="expandAllMenusTree">
              <el-icon><Expand /></el-icon>
              Expand
            </el-button>
            <el-button size="small" @click="collapseAllMenusTree">
              <el-icon><Fold /></el-icon>
              Collapse
            </el-button>
            <el-button type="primary" size="small" @click="openMenuDialog(null)">
              <el-icon><Plus /></el-icon>
              Add Menu
            </el-button>
          </div>
        </div>

        <!-- All Menus Tree with Actions and Drag Sort -->
        <div class="all-menus-container">
          <div v-if="loading" class="loading-state">
            <el-icon class="is-loading"><Loading /></el-icon>
            <span>Loading...</span>
          </div>
          <div v-else-if="menuTree.length === 0" class="empty-state">
            <el-icon><FolderOpened /></el-icon>
            <span>No menu data</span>
          </div>
          <div v-else class="sort-hint">
            <el-icon><Rank /></el-icon>
            <span>Drag to sort menus</span>
          </div>
          <el-tree
              ref="allMenusTreeRef"
              :key="allMenusTreeKey"
              :data="allMenusTreeData"
              node-key="menu_path"
              :expand-on-click-node="false"
              :default-expanded-keys="allMenusExpandedKeys"
              draggable
              :allow-drop="allowDrop"
              @node-drag-start="handleAllMenusDragStart"
              @node-drag-end="handleAllMenusDragEnd"
          >
            <template #default="{ data }">
              <div class="all-menus-node" :class="{ 'drag-source': allMenusDraggingNode === data }">
                <div class="drag-handle">
                  <el-icon><Rank /></el-icon>
                </div>
                <div class="node-icon">
                  <el-icon v-if="data.children && data.children.length"><Folder /></el-icon>
                  <el-icon v-else><Document /></el-icon>
                </div>
                <div class="node-info">
                  <span class="node-title">{{ data.menu_title }}</span>
                  <span class="node-path">{{ data.menu_path }}</span>
                </div>
                <div class="node-actions">
                  <el-button size="small" text @click="openMenuDialog(data)">
                    <el-icon><Edit /></el-icon>
                  </el-button>
                  <el-button size="small" text type="danger" @click="handleDeleteMenu(data)">
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </div>
              </div>
            </template>
          </el-tree>
        </div>
      </div>
    </div>
  </div>

  <!-- Version Management Dialog -->
  <el-dialog
      v-model="versionDialogVisible"
      title="Version Management"
      width="700px"
      class="version-dialog"
  >
    <div class="version-list">
      <div class="version-list-header">
        <div class="header-cell">Icon</div>
        <div class="header-cell">Version Code</div>
        <div class="header-cell">Version Name</div>
        <div class="header-cell">Status</div>
        <div class="header-cell">Operations</div>
      </div>
      <div class="version-list-body">
        <div v-for="version in allVersions" :key="version.id" class="version-item">
          <div class="item-cell">{{ version.icon || '📦' }}</div>
          <div class="item-cell version-code">{{ version.version_code }}</div>
          <div class="item-cell">{{ version.version_name }}</div>
          <div class="item-cell">
            <el-tag v-if="version.version_code === currentActiveVersion" type="success" size="small">Active</el-tag>
            <el-tag v-else type="info" size="small">Inactive</el-tag>
          </div>
          <div class="item-cell actions">
            <el-button size="small" text @click="handleEditVersion(version)">
              <el-icon><Edit /></el-icon>
            </el-button>
            <el-button
                size="small"
                text
                type="danger"
                @click="handleDeleteVersion(version)"
                :disabled="version.version_code === currentActiveVersion"
            >
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
        </div>
      </div>
    </div>
    <div class="version-dialog-footer">
      <el-button type="primary" @click="handleAddVersion">
        <el-icon><Plus /></el-icon>
        Add Version
      </el-button>
    </div>
  </el-dialog>

  <!-- Version Edit Dialog -->
  <el-dialog
      v-model="versionFormDialogVisible"
      :title="versionForm.id ? 'Edit Version' : 'Add Version'"
      width="500px"
  >
    <el-form :model="versionForm" label-width="100px">
      <el-form-item label="Version Code" required>
        <el-input
            v-model="versionForm.version_code"
            placeholder="e.g., v1.0, v2.0"
            :disabled="!!versionForm.id"
        />
      </el-form-item>
      <el-form-item label="Version Name" required>
        <el-input v-model="versionForm.version_name" placeholder="e.g., Version 1.0" />
      </el-form-item>
      <el-form-item label="Icon">
        <el-input v-model="versionForm.icon" placeholder="e.g., 📦, 🚀, 💡" maxlength="2" />
      </el-form-item>
      <el-form-item label="Set as Active">
        <el-switch v-model="versionForm.is_default" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="versionFormDialogVisible = false">Cancel</el-button>
      <el-button type="primary" @click="handleSaveVersion" :loading="versionSaving">
        Save
      </el-button>
    </template>
  </el-dialog>

  <!-- Menu Edit Dialog -->
  <!-- Menu Edit Dialog -->
  <el-dialog
      v-model="menuDialogVisible"
      :title="editingMenu ? 'Edit Menu' : 'Add Menu'"
      width="550px"
  >
    <el-form :model="menuForm" label-width="100px">
      <el-form-item label="Parent Menu">
        <el-tree-select
            v-model="menuForm.parent_id"
            :data="menuTree"
            :props="{ label: 'menu_title', value: 'id' }"
            placeholder="Select parent menu (0 for root)"
            check-strictly
            clearable
            style="width: 100%"
        />
      </el-form-item>
      <el-form-item label="Menu Path" required>
        <el-input v-model="menuForm.menu_path" placeholder="e.g., /new-module" />
      </el-form-item>
      <el-form-item label="Menu Title" required>
        <el-input v-model="menuForm.menu_title" placeholder="Menu display name" />
      </el-form-item>

      <!-- 修改这里的 Icon 字段 -->
      <el-form-item label="Icon">
        <el-select
            v-model="menuForm.menu_icon"
            placeholder="Select icon"
            filterable
            clearable
            style="width: 100%"
            popper-class="icon-select-dropdown"
        >
          <template #prefix>
            <el-icon v-if="menuForm.menu_icon && getIconComponent(menuForm.menu_icon)">
              <component :is="getIconComponent(menuForm.menu_icon)" />
            </el-icon>
          </template>
          <el-option
              v-for="icon in iconList"
              :key="icon"
              :label="icon"
              :value="icon"
          >
            <div style="display: flex; align-items: center; gap: 8px;">
              <el-icon><component :is="getIconComponent(icon)" /></el-icon>
              <span>{{ icon }}</span>
            </div>
          </el-option>
        </el-select>
      </el-form-item>

      <el-form-item label="Menu Type">
        <el-select v-model="menuForm.menu_type" style="width: 100%">
          <el-option label="Menu (clickable)" value="menu" />
          <el-option label="Container (not clickable)" value="container" />
        </el-select>
      </el-form-item>
      <el-form-item label="Redirect Path">
        <el-input v-model="menuForm.redirect_path" placeholder="Redirect URL" />
      </el-form-item>
      <el-form-item label="Sort Order">
        <el-input-number v-model="menuForm.sort_order" :min="0" style="width: 100%" />
      </el-form-item>
      <el-form-item label="Visible">
        <el-switch v-model="menuForm.is_visible" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="menuDialogVisible = false">Cancel</el-button>
      <el-button type="primary" @click="handleSaveMenu" :loading="menuSaving">
        Save
      </el-button>
    </template>
  </el-dialog>

  <!-- Saving Loading Mask -->
  <div v-if="saving" class="loading-fullscreen">
    <div class="loading-content-center">
      <div class="loading-spinner-small">
        <div class="spinner-ring-small"></div>
        <div class="spinner-ring-small"></div>
        <div class="spinner-ring-small"></div>
      </div>
      <div class="loading-text-switch">
        <span>Saving Configuration</span>
        <span class="loading-dots">
          <span>.</span><span>.</span><span>.</span>
        </span>
      </div>
    </div>
  </div>

  <!-- Switching Version Loading Mask -->
  <div v-if="switching" class="loading-fullscreen">
    <div class="loading-content-center">
      <div class="loading-spinner-small">
        <div class="spinner-ring-small"></div>
        <div class="spinner-ring-small"></div>
        <div class="spinner-ring-small"></div>
      </div>
      <div class="loading-text-switch">
        <span>Switching Version</span>
        <span class="loading-dots">
          <span>.</span><span>.</span><span>.</span>
        </span>
      </div>
      <div class="loading-version-name">{{ switchingVersionName }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
// 图标完整导入
import {
  Plus, Minus, CirclePlus, Search, Female, Male, Aim, House, FullScreen, Loading, Link, Service, Pointer, Star, Notification, Connection, ChatDotRound, Setting, Clock, Position, Discount, Odometer, ChatSquare, ChatRound, ChatLineRound, ChatLineSquare, ChatDotSquare, View, Hide, Unlock, Lock, RefreshRight, RefreshLeft, Refresh, Bell, MuteNotification, User, Check, CircleCheck, Warning, CircleClose, Close, PieChart, More, Compass, Filter, Switch, Select, SemiSelect, CloseBold, EditPen, Edit, Message, MessageBox, TurnOff, Finished, Delete, Crop, SwitchButton, Operation, Open, Remove, ZoomOut, ZoomIn, InfoFilled, CircleCheckFilled, SuccessFilled, WarningFilled, CircleCloseFilled, QuestionFilled, WarnTriangleFilled, UserFilled, MoreFilled, Tools, HomeFilled, Menu, UploadFilled, Avatar, HelpFilled, Share, StarFilled, Comment, Histogram, Grid, Promotion, DeleteFilled, RemoveFilled, CirclePlusFilled, ArrowLeft, ArrowUp, ArrowRight, ArrowDown, ArrowLeftBold, ArrowUpBold, ArrowRightBold, ArrowDownBold, DArrowRight, DArrowLeft, Download, Upload, Top, Bottom, Back, Right, TopRight, TopLeft, BottomRight, BottomLeft, Sort, SortUp, SortDown, Rank, CaretLeft, CaretTop, CaretRight, CaretBottom, DCaret, Expand, Fold, Document, DocumentAdd, Notebook, Tickets, Memo, Collection, Postcard, ScaleToOriginal, SetUp, DocumentDelete, DocumentChecked, DataBoard, DataAnalysis, CopyDocument, FolderChecked, Files, Folder, FolderDelete, FolderRemove, FolderOpened, DocumentCopy, DocumentRemove, FolderAdd, FirstAidKit, Reading, DataLine, Management, Checked, Ticket, Failed, TrendCharts, List, Microphone, Mute, Mic, VideoPause, VideoCamera, VideoPlay, Headset, Monitor, Film, Camera, Picture, PictureRounded, Iphone, Cellphone, VideoCameraFilled, PictureFilled, Platform, CameraFilled, BellFilled, Location, LocationInformation, DeleteLocation, Coordinate, Bicycle, OfficeBuilding, School, Guide, AddLocation, MapLocation, Place, LocationFilled, Van, Food, Watermelon, Pear, NoSmoking, Smoking, Mug, GobletSquareFull, GobletFull, KnifeFork, Sugar, Bowl, MilkTea, Lollipop, Coffee, Chicken, Dish, IceTea, ColdDrink, CoffeeCup, DishDot, IceDrink, IceCream, Dessert, IceCreamSquare, ForkSpoon, IceCreamRound, HotWater, Grape, Fries, Apple, Burger, Goblet, GobletSquare, Orange, Cherry, Printer, Calendar, CreditCard, Box, Money, Refrigerator, Cpu, Football, Brush, Suitcase, SuitcaseLine, Umbrella, AlarmClock, Medal, GoldMedal, Present, Mouse, Watch, QuartzWatch, Magnet, Help, Soccer, ToiletPaper, ReadingLamp, Paperclip, MagicStick, Basketball, Baseball, Coin, Goods, Sell, SoldOut, Key, ShoppingCart, ShoppingCartFull, ShoppingTrolley, Phone, Scissor, Handbag, ShoppingBag, Trophy, TrophyBase, Stopwatch, Timer, CollectionTag, TakeawayBox, PriceTag, Wallet, Opportunity, PhoneFilled, WalletFilled, GoodsFilled, Flag, BrushFilled, Briefcase, Stamp, Sunrise, Sunny, Ship, MostlyCloudy, PartlyCloudy, Sunset, Drizzling, Pouring, Cloudy, Moon, MoonNight, Lightning, ChromeFilled, Eleme, ElemeFilled, ElementPlus, Shop, SwitchFilled, WindPower
} from '@element-plus/icons-vue'
import {
  listVersions,
  getMenuTree,
  getVersionMenus,
  getActiveVersionMenuConfig,
  switchActiveVersion,
  incrementalUpdateVersionMenus,
  createMenu,
  updateMenu,
  deleteMenu,
  batchUpdateMenuSort,
  createVersion,
  updateVersion,
  deleteVersion,
  getInitializationData  // 添加这一行
} from '@/api/system_api'
import { useCounterStore } from '@/stores/counter'

const counterStore = useCounterStore()



// icon
// ==================== Icon List for Selector ====================
// 从所有导入的图标中提取图标名称列表
const iconList = ref([
  'Plus', 'Minus', 'CirclePlus', 'Search', 'Female', 'Male', 'Aim', 'House',
  'FullScreen', 'Loading', 'Link', 'Service', 'Pointer', 'Star', 'Notification',
  'Connection', 'ChatDotRound', 'Setting', 'Clock', 'Position', 'Discount',
  'Odometer', 'ChatSquare', 'ChatRound', 'ChatLineRound', 'ChatLineSquare',
  'ChatDotSquare', 'View', 'Hide', 'Unlock', 'Lock', 'RefreshRight', 'RefreshLeft',
  'Refresh', 'Bell', 'MuteNotification', 'User', 'Check', 'CircleCheck', 'Warning',
  'CircleClose', 'Close', 'PieChart', 'More', 'Compass', 'Filter', 'Switch',
  'Select', 'SemiSelect', 'CloseBold', 'EditPen', 'Edit', 'Message', 'MessageBox',
  'TurnOff', 'Finished', 'Delete', 'Crop', 'SwitchButton', 'Operation', 'Open',
  'Remove', 'ZoomOut', 'ZoomIn', 'InfoFilled', 'CircleCheckFilled', 'SuccessFilled',
  'WarningFilled', 'CircleCloseFilled', 'QuestionFilled', 'WarnTriangleFilled',
  'UserFilled', 'MoreFilled', 'Tools', 'HomeFilled', 'Menu', 'UploadFilled',
  'Avatar', 'HelpFilled', 'Share', 'StarFilled', 'Comment', 'Histogram', 'Grid',
  'Promotion', 'DeleteFilled', 'RemoveFilled', 'CirclePlusFilled', 'ArrowLeft',
  'ArrowUp', 'ArrowRight', 'ArrowDown', 'ArrowLeftBold', 'ArrowUpBold',
  'ArrowRightBold', 'ArrowDownBold', 'DArrowRight', 'DArrowLeft', 'Download',
  'Upload', 'Top', 'Bottom', 'Back', 'Right', 'TopRight', 'TopLeft', 'BottomRight',
  'BottomLeft', 'Sort', 'SortUp', 'SortDown', 'Rank', 'CaretLeft', 'CaretTop',
  'CaretRight', 'CaretBottom', 'DCaret', 'Expand', 'Fold', 'Document',
  'DocumentAdd', 'Notebook', 'Tickets', 'Memo', 'Collection', 'Postcard',
  'ScaleToOriginal', 'SetUp', 'DocumentDelete', 'DocumentChecked', 'DataBoard',
  'DataAnalysis', 'CopyDocument', 'FolderChecked', 'Files', 'Folder',
  'FolderDelete', 'FolderRemove', 'FolderOpened', 'DocumentCopy', 'DocumentRemove',
  'FolderAdd', 'FirstAidKit', 'Reading', 'DataLine', 'Management', 'Checked',
  'Ticket', 'Failed', 'TrendCharts', 'List', 'Microphone', 'Mute', 'Mic',
  'VideoPause', 'VideoCamera', 'VideoPlay', 'Headset', 'Monitor', 'Film', 'Camera',
  'Picture', 'PictureRounded', 'Iphone', 'Cellphone', 'VideoCameraFilled',
  'PictureFilled', 'Platform', 'CameraFilled', 'BellFilled', 'Location',
  'LocationInformation', 'DeleteLocation', 'Coordinate', 'Bicycle', 'OfficeBuilding',
  'School', 'Guide', 'AddLocation', 'MapLocation', 'Place', 'LocationFilled', 'Van',
  'Food', 'Watermelon', 'Pear', 'NoSmoking', 'Smoking', 'Mug', 'GobletSquareFull',
  'GobletFull', 'KnifeFork', 'Sugar', 'Bowl', 'MilkTea', 'Lollipop', 'Coffee',
  'Chicken', 'Dish', 'IceTea', 'ColdDrink', 'CoffeeCup', 'DishDot', 'IceDrink',
  'IceCream', 'Dessert', 'IceCreamSquare', 'ForkSpoon', 'IceCreamRound', 'HotWater',
  'Grape', 'Fries', 'Apple', 'Burger', 'Goblet', 'GobletSquare', 'Orange', 'Cherry',
  'Printer', 'Calendar', 'CreditCard', 'Box', 'Money', 'Refrigerator', 'Cpu',
  'Football', 'Brush', 'Suitcase', 'SuitcaseLine', 'Umbrella', 'AlarmClock', 'Medal',
  'GoldMedal', 'Present', 'Mouse', 'Watch', 'QuartzWatch', 'Magnet', 'Help', 'Soccer',
  'ToiletPaper', 'ReadingLamp', 'Paperclip', 'MagicStick', 'Basketball', 'Baseball',
  'Coin', 'Goods', 'Sell', 'SoldOut', 'Key', 'ShoppingCart', 'ShoppingCartFull',
  'ShoppingTrolley', 'Phone', 'Scissor', 'Handbag', 'ShoppingBag', 'Trophy',
  'TrophyBase', 'Stopwatch', 'Timer', 'CollectionTag', 'TakeawayBox', 'PriceTag',
  'Wallet', 'Opportunity', 'PhoneFilled', 'WalletFilled', 'GoodsFilled', 'Flag',
  'BrushFilled', 'Briefcase', 'Stamp', 'Sunrise', 'Sunny', 'Ship', 'MostlyCloudy',
  'PartlyCloudy', 'Sunset', 'Drizzling', 'Pouring', 'Cloudy', 'Moon', 'MoonNight',
  'Lightning', 'ChromeFilled', 'Eleme', 'ElemeFilled', 'ElementPlus', 'Shop',
  'SwitchFilled', 'WindPower'
])

// 图标名称到组件的映射
const iconComponentMap = new Map()

// 动态获取图标组件
const getIconComponent = (iconName) => {
  if (!iconName) return null

  // 缓存已获取的组件
  if (iconComponentMap.has(iconName)) {
    return iconComponentMap.get(iconName)
  }

  // 动态查找导入的图标
  const allIcons = {
    Plus, Minus, CirclePlus, Search, Female, Male, Aim, House,
    FullScreen, Loading, Link, Service, Pointer, Star, Notification,
    Connection, ChatDotRound, Setting, Clock, Position, Discount,
    Odometer, ChatSquare, ChatRound, ChatLineRound, ChatLineSquare,
    ChatDotSquare, View, Hide, Unlock, Lock, RefreshRight, RefreshLeft,
    Refresh, Bell, MuteNotification, User, Check, CircleCheck, Warning,
    CircleClose, Close, PieChart, More, Compass, Filter, Switch,
    Select, SemiSelect, CloseBold, EditPen, Edit, Message, MessageBox,
    TurnOff, Finished, Delete, Crop, SwitchButton, Operation, Open,
    Remove, ZoomOut, ZoomIn, InfoFilled, CircleCheckFilled, SuccessFilled,
    WarningFilled, CircleCloseFilled, QuestionFilled, WarnTriangleFilled,
    UserFilled, MoreFilled, Tools, HomeFilled, Menu, UploadFilled,
    Avatar, HelpFilled, Share, StarFilled, Comment, Histogram, Grid,
    Promotion, DeleteFilled, RemoveFilled, CirclePlusFilled, ArrowLeft,
    ArrowUp, ArrowRight, ArrowDown, ArrowLeftBold, ArrowUpBold,
    ArrowRightBold, ArrowDownBold, DArrowRight, DArrowLeft, Download,
    Upload, Top, Bottom, Back, Right, TopRight, TopLeft, BottomRight,
    BottomLeft, Sort, SortUp, SortDown, Rank, CaretLeft, CaretTop,
    CaretRight, CaretBottom, DCaret, Expand, Fold, Document,
    DocumentAdd, Notebook, Tickets, Memo, Collection, Postcard,
    ScaleToOriginal, SetUp, DocumentDelete, DocumentChecked, DataBoard,
    DataAnalysis, CopyDocument, FolderChecked, Files, Folder,
    FolderDelete, FolderRemove, FolderOpened, DocumentCopy, DocumentRemove,
    FolderAdd, FirstAidKit, Reading, DataLine, Management, Checked,
    Ticket, Failed, TrendCharts, List, Microphone, Mute, Mic,
    VideoPause, VideoCamera, VideoPlay, Headset, Monitor, Film, Camera,
    Picture, PictureRounded, Iphone, Cellphone, VideoCameraFilled,
    PictureFilled, Platform, CameraFilled, BellFilled, Location,
    LocationInformation, DeleteLocation, Coordinate, Bicycle, OfficeBuilding,
    School, Guide, AddLocation, MapLocation, Place, LocationFilled, Van,
    Food, Watermelon, Pear, NoSmoking, Smoking, Mug, GobletSquareFull,
    GobletFull, KnifeFork, Sugar, Bowl, MilkTea, Lollipop, Coffee,
    Chicken, Dish, IceTea, ColdDrink, CoffeeCup, DishDot, IceDrink,
    IceCream, Dessert, IceCreamSquare, ForkSpoon, IceCreamRound, HotWater,
    Grape, Fries, Apple, Burger, Goblet, GobletSquare, Orange, Cherry,
    Printer, Calendar, CreditCard, Box, Money, Refrigerator, Cpu,
    Football, Brush, Suitcase, SuitcaseLine, Umbrella, AlarmClock, Medal,
    GoldMedal, Present, Mouse, Watch, QuartzWatch, Magnet, Help, Soccer,
    ToiletPaper, ReadingLamp, Paperclip, MagicStick, Basketball, Baseball,
    Coin, Goods, Sell, SoldOut, Key, ShoppingCart, ShoppingCartFull,
    ShoppingTrolley, Phone, Scissor, Handbag, ShoppingBag, Trophy,
    TrophyBase, Stopwatch, Timer, CollectionTag, TakeawayBox, PriceTag,
    Wallet, Opportunity, PhoneFilled, WalletFilled, GoodsFilled, Flag,
    BrushFilled, Briefcase, Stamp, Sunrise, Sunny, Ship, MostlyCloudy,
    PartlyCloudy, Sunset, Drizzling, Pouring, Cloudy, Moon, MoonNight,
    Lightning, ChromeFilled, Eleme, ElemeFilled, ElementPlus, Shop,
    SwitchFilled, WindPower
  }

  const component = allIcons[iconName]
  if (component) {
    iconComponentMap.set(iconName, component)
  }
  return component || null
}
//icon

// ==================== Page Loading State ====================
const isPageLoaded = ref(false)
const pageLoadingProgress = ref(0)
const pageLoadingMessage = ref('Preparing...')
const loadingMessages = [
  'Preparing...',
  'Loading versions...',
  'Loading menu tree...',
  'Loading menu configs...',
  'Almost ready...'
]

// ==================== Data State ====================
const loading = ref(true)
const saving = ref(false)
const switching = ref(false)
const menuSaving = ref(false)
const switchingVersionName = ref('')
const allVersions = ref([])
const menuTree = ref([])
const sortedMenuTree = ref([])
const allMenusTreeData = ref([])
const treeKey = ref(0)
const allMenusTreeKey = ref(0)
const allMenusExpandedKeys = ref([])

// Version management state
const versionDialogVisible = ref(false)
const versionFormDialogVisible = ref(false)
const versionForm = ref({
  id: null,
  version_code: '',
  version_name: '',
  icon: '📦',
  is_default: false
})
const versionSaving = ref(false)

// Drag state for all menus tree
const allMenusDraggingNode = ref(null)

// Version menu config storage
const versionSelections = ref({})

// UI state
const currentEditVersion = ref('')
const currentActiveVersion = ref('')
const expandedKeys = ref([])
const treeRef = ref()
const allMenusTreeRef = ref()
const hasChanges = ref(false)

// Menu dialog
const menuDialogVisible = ref(false)
const editingMenu = ref(null)
const menuForm = ref({
  parent_id: 0,
  menu_path: '',
  menu_title: '',
  menu_icon: '',
  menu_type: 'menu',
  has_children: false,
  redirect_path: '',
  sort_order: 0,
  is_visible: true
})

// Track sort changes (global, affects both trees)
let pendingSortChanges = []

// ==================== Computed Properties ====================
const activeVersionName = computed(() => {
  const version = allVersions.value.find(v => v.version_code === currentActiveVersion.value)
  return version?.version_name || 'Unknown'
})

const currentEditVersionName = computed(() => {
  const version = allVersions.value.find(v => v.version_code === currentEditVersion.value)
  return version?.version_name || 'Unknown'
})

const currentSelectedCount = computed(() => {
  return versionSelections.value[currentEditVersion.value]?.selected?.size || 0
})

const totalMenuCount = computed(() => {
  return getAllMenuPaths(menuTree.value).length
})

// ==================== Utility Functions ====================
const getAllMenuPaths = (nodes) => {
  let paths = []
  if (!nodes || !Array.isArray(nodes)) return paths
  for (const node of nodes) {
    if (node && node.menu_path) {
      paths.push(node.menu_path)
      if (node.children && Array.isArray(node.children) && node.children.length) {
        paths = paths.concat(getAllMenuPaths(node.children))
      }
    }
  }
  return paths
}

const getAllChildPaths = (menu) => {
  const paths = [menu.menu_path]
  if (menu.children && menu.children.length) {
    for (const child of menu.children) {
      paths.push(...getAllChildPaths(child))
    }
  }
  return paths
}

const isMenuItemDisabled = (menu) => {
  const versionData = versionSelections.value[currentEditVersion.value]
  if (!versionData) return false
  if (menu.parent_id === 0) return false

  const menuPathParts = menu.menu_path.split('/')
  let parentPath = menuPathParts.slice(0, -1).join('/')
  if (parentPath === '') parentPath = '/' + menuPathParts[1]

  const isParentSelected = versionData.selected.has(parentPath)
  return !isParentSelected
}

const getSelectedSetFromVersionMenus = (data) => {
  if (!data) return new Set()
  let menus = []
  if (data.menus && Array.isArray(data.menus)) {
    menus = data.menus
  } else if (Array.isArray(data)) {
    menus = data
  } else {
    return new Set()
  }
  return new Set(
      menus
          .filter(m => m.is_visible === true || m.is_visible === 1 || m.is_visible === 'true')
          .map(m => m.menu_path)
  )
}

const getAllMenuPathsFromConfig = (config) => {
  let paths = []
  const collect = (nodes) => {
    if (!nodes) return
    for (const node of nodes) {
      paths.push(node.index)
      if (node.children && node.children.length) {
        collect(node.children)
      }
    }
  }
  collect(config)
  return paths
}

const deepCopyMenuTree = (nodes) => {
  if (!nodes) return []
  return nodes.map(node => ({
    ...node,
    children: node.children ? deepCopyMenuTree(node.children) : []
  }))
}

const updateSortedMenuTreeSelection = () => {
  const selectedSet = versionSelections.value[currentEditVersion.value]?.selected || new Set()
  const updateNode = (nodes) => {
    if (!nodes) return
    for (const node of nodes) {
      if (node.children && node.children.length) {
        updateNode(node.children)
      }
    }
  }
  updateNode(sortedMenuTree.value)
}

// ==================== Drag & Drop Sort (Only for All Menus) ====================
const allowDrop = (draggingNode, dropNode, type) => {
  if (type === 'inner') return false
  if (draggingNode.parent?.data?.menu_path !== dropNode.parent?.data?.menu_path) {
    return false
  }
  return true
}

// All menus tree drag handlers
const handleAllMenusDragStart = (node, event) => {
  allMenusDraggingNode.value = node.data
}

const handleAllMenusDragEnd = () => {
  allMenusDraggingNode.value = null
  collectSortChangesFromTree(allMenusTreeData.value)
}

// Collect sort changes from any tree
const collectSortChangesFromTree = (treeData) => {
  const changes = []

  const extractSortOrder = (nodes) => {
    if (!nodes || !Array.isArray(nodes)) return
    nodes.forEach((node, index) => {
      const newSortOrder = index + 1
      if (node.sort_order !== newSortOrder) {
        changes.push({
          menu_path: node.menu_path,
          sort_order: newSortOrder
        })
        node.sort_order = newSortOrder
      }
      if (node.children && node.children.length) {
        extractSortOrder(node.children)
      }
    })
  }

  extractSortOrder(treeData)

  if (changes.length > 0) {
    // Merge with existing pending changes
    for (const change of changes) {
      const existingIndex = pendingSortChanges.findIndex(c => c.menu_path === change.menu_path)
      if (existingIndex !== -1) {
        pendingSortChanges[existingIndex] = change
      } else {
        pendingSortChanges.push(change)
      }
    }
    hasChanges.value = true
    console.log('Sort changes collected:', changes)
  }
}

// ==================== Menu Operations ====================
const isMenuSelectedForCurrentVersion = (menuPath) => {
  return versionSelections.value[currentEditVersion.value]?.selected?.has(menuPath) || false
}

const toggleMenuSelection = (menu, checked) => {
  const versionData = versionSelections.value[currentEditVersion.value]
  if (!versionData) return

  const newSelected = new Set(versionData.selected)
  const childPaths = getAllChildPaths(menu)

  if (checked) {
    childPaths.forEach(path => newSelected.add(path))
  } else {
    childPaths.forEach(path => newSelected.delete(path))
  }

  versionData.selected = newSelected
  updateSortedMenuTreeSelection()
  checkChanges()
}

const selectAllMenus = () => {
  const allPaths = getAllMenuPaths(menuTree.value)
  const versionData = versionSelections.value[currentEditVersion.value]
  if (versionData) {
    versionData.selected = new Set(allPaths)
    updateSortedMenuTreeSelection()
    checkChanges()
    ElMessage.success(`Selected all ${allPaths.length} menus`)
  }
}

const deselectAllMenus = () => {
  const versionData = versionSelections.value[currentEditVersion.value]
  if (versionData) {
    versionData.selected = new Set()
    updateSortedMenuTreeSelection()
    checkChanges()
    ElMessage.success('Deselected all menus')
  }
}

const checkChanges = () => {
  const versionData = versionSelections.value[currentEditVersion.value]
  if (!versionData) {
    hasChanges.value = false
    return
  }

  const isEqual = versionData.selected.size === versionData.original.size &&
      [...versionData.selected].every(v => versionData.original.has(v))

  hasChanges.value = !isEqual || pendingSortChanges.length > 0
}

const resetChanges = () => {
  const versionData = versionSelections.value[currentEditVersion.value]
  if (versionData) {
    versionData.selected = new Set(versionData.original)
    updateSortedMenuTreeSelection()
    pendingSortChanges = []
    syncSortOrderFromOriginal()
    checkChanges()
    ElMessage.success('Reset completed')
  }
}

const syncSortOrderFromOriginal = () => {
  const syncOrder = (targetNodes, sourceNodes) => {
    if (!targetNodes || !sourceNodes) return
    for (let i = 0; i < targetNodes.length && i < sourceNodes.length; i++) {
      if (targetNodes[i].menu_path === sourceNodes[i].menu_path) {
        targetNodes[i].sort_order = sourceNodes[i].sort_order
        if (targetNodes[i].children && sourceNodes[i].children) {
          syncOrder(targetNodes[i].children, sourceNodes[i].children)
        }
      }
    }
  }
  syncOrder(sortedMenuTree.value, menuTree.value)
  syncOrder(allMenusTreeData.value, menuTree.value)
  treeKey.value++
  allMenusTreeKey.value++
}

// Version tree expand/collapse
const expandAllVersionTree = () => {
  const allPaths = getAllMenuPaths(menuTree.value)
  expandedKeys.value = [...allPaths]
  treeKey.value++
  ElMessage.success(`Expanded ${allPaths.length} menus`)
}

const collapseAllVersionTree = () => {
  expandedKeys.value = []
  treeKey.value++
  ElMessage.success('All menus collapsed')
}

// All menus tree expand/collapse
const expandAllMenusTree = () => {
  const allPaths = getAllMenuPaths(menuTree.value)
  allMenusExpandedKeys.value = [...allPaths]
  allMenusTreeKey.value++
  ElMessage.success(`Expanded ${allPaths.length} menus`)
}

const collapseAllMenusTree = () => {
  allMenusExpandedKeys.value = []
  allMenusTreeKey.value++
  ElMessage.success('All menus collapsed')
}

// ==================== Menu CRUD Operations ====================
const openMenuDialog = (menu) => {
  editingMenu.value = menu
  if (menu) {
    menuForm.value = {
      parent_id: menu.parent_id,
      menu_path: menu.menu_path,
      menu_title: menu.menu_title,
      menu_icon: menu.menu_icon || '',
      menu_type: menu.menu_type || 'menu',
      has_children: menu.has_children || false,
      redirect_path: menu.redirect_path || '',
      sort_order: menu.sort_order || 0,
      is_visible: menu.is_visible !== false
    }
  } else {
    menuForm.value = {
      parent_id: 0,
      menu_path: '',
      menu_title: '',
      menu_icon: '',
      menu_type: 'menu',
      has_children: false,
      redirect_path: '',
      sort_order: 0,
      is_visible: true
    }
  }
  menuDialogVisible.value = true
}

const handleSaveMenu = async () => {
  if (!menuForm.value.menu_path || !menuForm.value.menu_title) {
    ElMessage.warning('Menu path and title are required')
    return
  }

  menuSaving.value = true
  try {
    if (editingMenu.value) {
      await updateMenu(editingMenu.value.id, menuForm.value)
      ElMessage.success('Menu updated successfully')
    } else {
      await createMenu(menuForm.value)
      ElMessage.success('Menu created successfully')
    }
    menuDialogVisible.value = false
    await refreshAllData()
// 如果你坚持要刷新页面，取消注释下面这行
    window.location.reload()
  } catch (error) {
    console.error('Save menu error:', error)
    if (error.message && error.message.includes('already exists')) {
      ElMessage.warning('Menu path already exists')
    } else {
      ElMessage.error('Failed to save menu')
    }
  } finally {
    menuSaving.value = false
  }
}

const handleDeleteMenu = async (menu) => {
  try {
    await ElMessageBox.confirm(
        `Are you sure you want to delete "${menu.menu_title}"? All submenus will also be deleted.`,
        'Confirm Delete',
        { confirmButtonText: 'Delete', cancelButtonText: 'Cancel', type: 'warning' }
    )
    await deleteMenu(menu.id)
    ElMessage.success('Menu deleted successfully')
    await refreshAllData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Delete menu error:', error)
      ElMessage.error('Failed to delete menu')
    }
  }
}

// ==================== Version Management Operations ====================
const openVersionManager = () => {
  versionDialogVisible.value = true
}

const handleAddVersion = () => {
  versionForm.value = {
    id: null,
    version_code: '',
    version_name: '',
    icon: '📦',
    is_default: false
  }
  versionFormDialogVisible.value = true
}

const handleEditVersion = (version) => {
  versionForm.value = {
    id: version.id,
    version_code: version.version_code,
    version_name: version.version_name,
    icon: version.icon || '📦',
    is_default: version.version_code === currentActiveVersion.value
  }
  versionFormDialogVisible.value = true
}

const handleSaveVersion = async () => {
  if (!versionForm.value.version_code || !versionForm.value.version_name) {
    ElMessage.warning('Version code and name are required')
    return
  }

  versionSaving.value = true
  try {
    if (versionForm.value.id) {
      // Update version
      await updateVersion(versionForm.value.id, versionForm.value)
      ElMessage.success('Version updated successfully')
    } else {
      // Create version
      await createVersion(versionForm.value)
      ElMessage.success('Version created successfully')
    }

    versionFormDialogVisible.value = false
    await refreshVersions()
  } catch (error) {
    console.error('Save version error:', error)
    if (error.message && error.message.includes('already exists')) {
      ElMessage.warning('Version code already exists')
    } else {
      ElMessage.error('Failed to save version')
    }
  } finally {
    versionSaving.value = false
  }
}

const handleDeleteVersion = async (version) => {
  // Check if it's the currently active version
  if (version.version_code === currentActiveVersion.value) {
    ElMessage.warning('Cannot delete the currently active version')
    return
  }

  try {
    await ElMessageBox.confirm(
        `Are you sure you want to delete version "${version.version_name}"? This action cannot be undone.`,
        'Confirm Delete',
        { confirmButtonText: 'Delete', cancelButtonText: 'Cancel', type: 'warning' }
    )

    await deleteVersion(version.version_code)
    ElMessage.success('Version deleted successfully')
    await refreshVersions()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Delete version error:', error)
      ElMessage.error('Failed to delete version')
    }
  }
}

const refreshVersions = async () => {
  try {
    // 使用统一接口刷新所有数据
    const initData = await getInitializationData()
    const { versions, version_menus, active_version } = initData

    allVersions.value = versions || []

    // 更新激活版本
    if (active_version) {
      currentActiveVersion.value = active_version.version_code
    }

    // 更新版本选择集合
    for (const version of versions) {
      const versionCode = version.version_code
      const selectedPaths = version_menus[versionCode] || []

      if (versionSelections.value[versionCode]) {
        versionSelections.value[versionCode].selected = new Set(selectedPaths)
        versionSelections.value[versionCode].original = new Set(selectedPaths)
      } else {
        versionSelections.value[versionCode] = {
          selected: new Set(selectedPaths),
          original: new Set(selectedPaths)
        }
      }
    }

    // If current editing version was deleted, switch to first version
    if (!versions.find(v => v.version_code === currentEditVersion.value) && versions.length > 0) {
      currentEditVersion.value = versions[0].version_code
    }

    updateSortedMenuTreeSelection()
    treeKey.value++
  } catch (error) {
    console.error('Refresh versions error:', error)
    ElMessage.error('Failed to refresh versions')
  }
}

// ==================== API Operations ====================
const loadVersionMenus = async (versionCode) => {
  try {
    const data = await getVersionMenus(versionCode)
    const selectedSet = getSelectedSetFromVersionMenus(data)

    if (!versionSelections.value[versionCode]) {
      versionSelections.value[versionCode] = {
        selected: new Set(),
        original: new Set()
      }
    }
    versionSelections.value[versionCode].selected = new Set(selectedSet)
    versionSelections.value[versionCode].original = new Set(selectedSet)

    if (versionCode === currentEditVersion.value) {
      updateSortedMenuTreeSelection()
    }

    console.log(`Version ${versionCode} loaded, selected ${selectedSet.size} menus`)
  } catch (error) {
    console.error(`Failed to load version ${versionCode}:`, error)
    const allPaths = getAllMenuPaths(menuTree.value)
    if (!versionSelections.value[versionCode]) {
      versionSelections.value[versionCode] = {
        selected: new Set(),
        original: new Set()
      }
    }
    versionSelections.value[versionCode].selected = new Set(allPaths)
    versionSelections.value[versionCode].original = new Set(allPaths)
    if (versionCode === currentEditVersion.value) {
      updateSortedMenuTreeSelection()
    }
  }
}

const saveAllChanges = async () => {
  saving.value = true
  try {
    const versionData = versionSelections.value[currentEditVersion.value]
    if (!versionData) return

    const originalSet = versionData.original
    const currentSet = versionData.selected

    const addList = []
    const removeList = []

    currentSet.forEach(path => {
      if (!originalSet.has(path)) addList.push(path)
    })

    originalSet.forEach(path => {
      if (!currentSet.has(path)) removeList.push(path)
    })

    if (pendingSortChanges.length > 0) {
      console.log('Saving sort changes:', pendingSortChanges)
      await batchUpdateMenuSort(pendingSortChanges)
    }

    if (addList.length > 0 || removeList.length > 0) {
      console.log('Saving selection changes:', { add: addList.length, remove: removeList.length })
      await incrementalUpdateVersionMenus(currentEditVersion.value, {
        add: addList,
        remove: removeList
      })
    }

    if (addList.length === 0 && removeList.length === 0 && pendingSortChanges.length === 0) {
      ElMessage.info('No changes to save')
      saving.value = false
      return
    }

    versionData.original = new Set(versionData.selected)

    if (pendingSortChanges.length > 0) {
      const syncOrderToOriginal = (nodes) => {
        if (!nodes) return
        for (const node of nodes) {
          const change = pendingSortChanges.find(c => c.menu_path === node.menu_path)
          if (change) {
            node.sort_order = change.sort_order
          }
          if (node.children) {
            syncOrderToOriginal(node.children)
          }
        }
      }
      syncOrderToOriginal(menuTree.value)
      syncOrderToOriginal(sortedMenuTree.value)
      syncOrderToOriginal(allMenusTreeData.value)
      pendingSortChanges = []
    }

    checkChanges()

    if (currentEditVersion.value === currentActiveVersion.value) {
      counterStore.setMenuVersion(currentEditVersion.value)
      setTimeout(() => {
        window.location.reload()
      }, 1000)
    } else {
      ElMessage.success(`Configuration saved for ${currentEditVersionName.value}`)
    }
  } catch (error) {
    console.error('Save error:', error)
    ElMessage.error('Failed to save configuration')
  } finally {
    saving.value = false
  }
}

const refreshAllData = async () => {
  loading.value = true
  try {
    // 使用统一接口刷新数据
    const initData = await getInitializationData()

    const { versions, menu_tree, version_menus, active_version } = initData

    // 更新数据
    allVersions.value = versions || []
    menuTree.value = menu_tree || []
    sortedMenuTree.value = deepCopyMenuTree(menu_tree)
    allMenusTreeData.value = deepCopyMenuTree(menu_tree)

    // 更新激活版本
    if (active_version) {
      currentActiveVersion.value = active_version.version_code
    }

    // 重新构建版本选择集合
    for (const version of versions) {
      const versionCode = version.version_code
      const selectedPaths = version_menus[versionCode] || []

      versionSelections.value[versionCode] = {
        selected: new Set(selectedPaths),
        original: new Set(selectedPaths)
      }
    }

    // 如果当前编辑版本在刷新后仍然存在，保持它，否则切换到第一个
    if (!versions.find(v => v.version_code === currentEditVersion.value) && versions.length > 0) {
      currentEditVersion.value = versions[0].version_code
    }

    updateSortedMenuTreeSelection()

    allMenusExpandedKeys.value = []
    expandedKeys.value = []
    treeKey.value++
    allMenusTreeKey.value++

    ElMessage.success('Data refreshed successfully')
  } catch (error) {
    console.error('Refresh error:', error)
    ElMessage.error('Failed to refresh data')
  } finally {
    loading.value = false
  }
}

const handleSwitchActiveVersion = async (versionCode) => {
  if (versionCode === currentActiveVersion.value) {
    ElMessage.info('This version is already active')
    return
  }

  const targetVersion = allVersions.value.find(v => v.version_code === versionCode)
  switchingVersionName.value = targetVersion?.version_name || versionCode
  switching.value = true

  try {
    const result = await switchActiveVersion(versionCode)

    currentActiveVersion.value = result.version_code
    counterStore.setMenuVersion(result.version_code)

    allVersions.value = allVersions.value.map(v => ({
      ...v,
      is_default: v.version_code === result.version_code
    }))

    if (currentEditVersion.value === result.version_code) {
      const selectedPaths = getAllMenuPathsFromConfig(result.menu_config)
      if (versionSelections.value[result.version_code]) {
        versionSelections.value[result.version_code].selected = new Set(selectedPaths)
        versionSelections.value[result.version_code].original = new Set(selectedPaths)
      }
      updateSortedMenuTreeSelection()
      checkChanges()
    }

    ElMessage.success(`Switched to ${result.version_name}`)

    setTimeout(() => {
      window.location.reload()
    }, 800)
  } catch (error) {
    console.error('Switch version error:', error)
    ElMessage.error('Failed to switch version')
    switching.value = false
  }
}

// ==================== Initialization ====================
const initData = async () => {
  try {
    let messageIndex = 0
    const messageInterval = setInterval(() => {
      if (messageIndex < loadingMessages.length - 1) {
        messageIndex++
        pageLoadingMessage.value = loadingMessages[messageIndex]
      }
    }, 400)

    const progressInterval = setInterval(() => {
      if (pageLoadingProgress.value < 90) {
        pageLoadingProgress.value += Math.random() * 15 + 5
        if (pageLoadingProgress.value > 90) pageLoadingProgress.value = 90
      }
    }, 200)

    console.log('=== Starting initialization (optimized) ===')

    pageLoadingProgress.value = 30
    pageLoadingMessage.value = 'Loading initialization data...'

    // 一次性获取所有初始化数据
    const initData = await getInitializationData()
    console.log('Initialization data received:', initData)

    if (!initData || !initData.active_version) {
      throw new Error('Failed to get initialization data')
    }

    pageLoadingProgress.value = 60
    pageLoadingMessage.value = 'Processing menu tree...'

    // 解构数据
    const {
      active_version,
      versions,
      menu_tree,
      version_menus
    } = initData

    pageLoadingProgress.value = 75
    pageLoadingMessage.value = 'Building menu structures...'

    // 设置基础数据
    allVersions.value = versions || []
    menuTree.value = menu_tree || []
    sortedMenuTree.value = deepCopyMenuTree(menu_tree)
    allMenusTreeData.value = deepCopyMenuTree(menu_tree)

    // 设置激活版本和当前编辑版本
    currentActiveVersion.value = active_version.version_code
    currentEditVersion.value = active_version.version_code

    pageLoadingProgress.value = 85
    pageLoadingMessage.value = 'Loading version configurations...'

    // 构建所有版本的菜单选择集合
    if (versions && versions.length > 0) {
      for (const version of versions) {
        const versionCode = version.version_code
        // 从返回的数据中获取该版本的菜单路径列表
        const selectedPaths = version_menus[versionCode] || []

        // 如果是激活版本，还需要处理 menu_config（如果需要的话）
        if (versionCode === active_version.version_code && active_version.menu_config) {
          // 如果后端返回了完整的 menu_config，可以使用它
          // 否则使用 version_menus 的数据
          const configPaths = getAllMenuPathsFromConfig(active_version.menu_config)
          if (configPaths.length > 0) {
            versionSelections.value[versionCode] = {
              selected: new Set(configPaths),
              original: new Set(configPaths)
            }
            continue
          }
        }

        // 使用 version_menus 的数据
        versionSelections.value[versionCode] = {
          selected: new Set(selectedPaths),
          original: new Set(selectedPaths)
        }
      }
    }

    // 更新当前版本的选中状态
    updateSortedMenuTreeSelection()

    // 清空展开状态
    expandedKeys.value = []
    allMenusExpandedKeys.value = []
    loading.value = false
    pendingSortChanges = []

    console.log('=== Initialization complete ===')
    console.log('Loaded versions:', allVersions.value.length)
    console.log('Menu tree nodes:', getAllMenuPaths(menuTree.value).length)
    console.log('Version selections:', Object.keys(versionSelections.value).length)

    clearInterval(messageInterval)
    clearInterval(progressInterval)
    pageLoadingProgress.value = 100
    pageLoadingMessage.value = 'Ready!'

    setTimeout(() => {
      isPageLoaded.value = true
    }, 400)

  } catch (error) {
    console.error('Initialization error:', error)
    ElMessage.error('Failed to initialize data: ' + (error.message || 'Unknown error'))
    isPageLoaded.value = true
    loading.value = false
  }
}

const handleTabChange = () => {
  checkChanges()
}

watch(currentEditVersion, () => {
  checkChanges()
})

onMounted(() => {
  initData()
})
</script>

<style scoped>
.loading-fullscreen {
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

.loading-content-center {
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

.spinner-ring:nth-child(1) { border-top-color: #3b82f6; animation-delay: 0s; }
.spinner-ring:nth-child(2) { border-right-color: #f59e0b; animation-delay: 0.2s; width: 70%; height: 70%; top: 15%; left: 15%; }
.spinner-ring:nth-child(3) { border-bottom-color: #10b981; animation-delay: 0.4s; width: 40%; height: 40%; top: 30%; left: 30%; }

.loading-spinner-small {
  position: relative;
  width: 50px;
  height: 50px;
  margin: 0 auto 20px;
}

.spinner-ring-small {
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  border: 2px solid transparent;
  animation: spin 1s cubic-bezier(0.68, -0.55, 0.265, 1.55) infinite;
}

.spinner-ring-small:nth-child(1) { border-top-color: #3b82f6; }
.spinner-ring-small:nth-child(2) { border-right-color: #f59e0b; animation-delay: 0.15s; width: 70%; height: 70%; top: 15%; left: 15%; }
.spinner-ring-small:nth-child(3) { border-bottom-color: #10b981; animation-delay: 0.3s; width: 40%; height: 40%; top: 30%; left: 30%; }

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

.loading-text-switch {
  font-size: 18px;
  font-weight: 600;
  color: #e2e8f0;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
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

.loading-version-name {
  font-size: 14px;
  color: #94a3b8;
  margin-top: 8px;
}

@keyframes pulse {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}

.edition-manager {
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
  overflow: hidden;
}

.manager-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.header-title .el-icon {
  font-size: 22px;
  color: #409eff;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.two-column-layout {
  display: flex;
  flex: 1;
  gap: 20px;
  padding: 20px;
  overflow: hidden;
}

.left-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.right-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.panel-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: #f0f2f5;
  border-bottom: 1px solid #e4e7ed;
  font-weight: 600;
  color: #303133;
}

.active-version-actions {
  margin-left: auto;
}

.right-panel-actions {
  display: flex;
  gap: 8px;
  margin-left: auto;
}

.version-tabs {
  background: #fff;
  padding: 0 16px;
  border-bottom: 1px solid #e4e7ed;
}

.tab-label {
  display: flex;
  align-items: center;
  gap: 8px;
}

.tab-icon {
  font-size: 16px;
}

.active-badge {
  margin-left: 6px;
}

.version-info-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f0f7ff;
  border-bottom: 1px solid #d9ecff;
}

.info-content {
  display: flex;
  align-items: center;
  gap: 10px;
}

.info-content .el-icon {
  font-size: 18px;
  color: #409eff;
}

.info-label {
  font-size: 13px;
  font-weight: 500;
  color: #606266;
}

.version-name {
  font-size: 14px;
  font-weight: 600;
  color: #1a1a2e;
}

.selection-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.selection-info span {
  font-size: 13px;
  color: #606266;
}

.selection-info strong {
  color: #409eff;
}

.menu-tree-container {
  flex: 1;
  overflow: auto;
  padding: 16px;
}

.all-menus-container {
  flex: 1;
  overflow: auto;
  padding: 16px;
}

.sort-hint {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  padding: 8px 16px;
  background: #f0f7ff;
  border-bottom: 1px solid #d9ecff;
  font-size: 12px;
  color: #606266;
  margin-bottom: 12px;
}

.sort-hint .el-icon {
  color: #409eff;
}

.loading-state, .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: #909399;
  gap: 12px;
}

.loading-state .el-icon, .empty-state .el-icon {
  font-size: 48px;
}

.tree-node {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.tree-node:hover {
  background: #f5f7fa;
}

.node-icon {
  width: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #909399;
}

.node-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  margin-left: 8px;
}

.node-title {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.node-path {
  font-size: 11px;
  color: #c0c4cc;
  margin-top: 2px;
}

.node-checkbox {
  margin: 0 12px;
}

.all-menus-node {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.all-menus-node.drag-source {
  opacity: 0.5;
}

.all-menus-node:hover {
  background: #f5f7fa;
}

.drag-handle {
  width: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: grab;
  color: #c0c4cc;
}

.drag-handle:hover {
  color: #409eff;
}

.node-actions {
  display: flex;
  gap: 4px;
  margin-right: 12px;
}

:deep(.el-tree-node__content) {
  height: auto;
  padding: 0;
}

:deep(.el-tree-node__content:hover) {
  background: transparent;
}

:deep(.el-tree) {
  --el-tree-node-hover-bg-color: transparent;
}

.el-divider--vertical {
  height: 20px;
  margin: 0 4px;
}

.is-loading {
  animation: rotating 2s linear infinite;
}

@keyframes rotating {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Version Dialog Styles */
.version-dialog :deep(.el-dialog__body) {
  padding: 0;
}

.version-list {
  max-height: 400px;
  overflow-y: auto;
}

.version-list-header {
  display: grid;
  grid-template-columns: 60px 150px 1fr 100px 120px;
  background: #f5f7fa;
  padding: 12px 16px;
  font-weight: 600;
  color: #606266;
  border-bottom: 1px solid #e4e7ed;
}

.version-list-body {
  max-height: 350px;
  overflow-y: auto;
}

.version-item {
  display: grid;
  grid-template-columns: 60px 150px 1fr 100px 120px;
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
  align-items: center;
}

.version-item:hover {
  background: #f5f7fa;
}

.item-cell {
  display: flex;
  align-items: center;
}

.version-code {
  font-family: monospace;
  font-weight: 500;
  color: #409eff;
}

.actions {
  gap: 8px;
}

.version-dialog-footer {
  padding: 16px;
  border-top: 1px solid #e4e7ed;
  text-align: right;
}

.version-option-icon {
  margin-right: 8px;
}

.check-icon {
  margin-left: auto;
  color: #409eff;
}

.is-active {
  background-color: #ecf5ff;
}



/* 正确写法：修改 el-tree 内部的滚动条容器 */
.menu-tree-container::-webkit-scrollbar {
  width: 4px;
}
.menu-tree-container::-webkit-scrollbar-thumb {
  background: #dcdfe6;
  border-radius: 10px;
}
.menu-tree-container::-webkit-scrollbar-track {
  background: transparent;
}


.all-menus-container::-webkit-scrollbar {
  width: 4px;
}
.all-menus-container::-webkit-scrollbar-thumb {
  background: #dcdfe6;
  border-radius: 10px;
}
.all-menus-container::-webkit-scrollbar-track {
  background: transparent;
}

/* Icon 下拉选择器样式 */
:deep(.icon-select-dropdown .el-select-dropdown__item) {
  padding: 8px 12px;
}

:deep(.icon-select-dropdown .el-select-dropdown__item:hover) {
  background-color: #ecf5ff;
}

:deep(.el-select .el-input__prefix) {
  display: flex;
  align-items: center;
  margin-right: 8px;
}
</style>