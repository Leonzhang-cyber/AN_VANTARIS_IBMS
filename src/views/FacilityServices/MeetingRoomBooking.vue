<template>
  <!-- Loading Screen -->
  <div v-if="!isLoaded" class="loading-container">
    <div class="loading-overlay">
      <div class="loading-content">
        <div class="loading-spinner">
          <div class="spinner-ring"></div>
          <div class="spinner-ring"></div>
          <div class="spinner-ring"></div>
          <div class="spinner-ring"></div>
        </div>
        <div class="loading-text">
          <span class="loading-title">Meeting Room Booking</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Smart Meeting Room Management System</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="meeting-room-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">
          <div class="title-icon">
            <el-icon><OfficeBuilding /></el-icon>
          </div>
          Meeting Room Booking
        </h1>
        <div class="page-subtitle">Manage room reservations, schedules, and meeting resources</div>
      </div>
      <div class="header-actions">
        <el-button class="primary-btn" @click="openBookingDialog">
          <el-icon><Plus /></el-icon>
          <span>Book Room</span>
        </el-button>
        <el-button class="secondary-btn" @click="refreshData" :loading="refreshing">
          <el-icon><Refresh /></el-icon>
          <span>Refresh</span>
        </el-button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon blue">
          <el-icon><OfficeBuilding /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.totalRooms }}</div>
          <div class="stat-label">Total Rooms</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">
          <el-icon><CircleCheck /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.availableNow }}</div>
          <div class="stat-label">Available Now</div>
          <div class="stat-trend up">{{ stats.availablePercent }}% of total</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange">
          <el-icon><Calendar /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.todayBookings }}</div>
          <div class="stat-label">Today's Bookings</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon purple">
          <el-icon><User /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.totalBookings }}</div>
          <div class="stat-label">Total Bookings</div>
          <div class="stat-trend up">This month</div>
        </div>
      </div>
    </div>

    <!-- Section Header -->
    <div class="section-header">
      <div class="section-title-wrapper">
        <span class="section-icon">🏢</span>
        <h2 class="section-title">Meeting Rooms</h2>
      </div>
      <div class="section-actions">
        <el-radio-group v-model="viewMode" size="default" class="view-toggle">
          <el-radio-button value="grid">
            <el-icon><Grid /></el-icon> Grid
          </el-radio-button>
          <el-radio-button value="list">
            <el-icon><List /></el-icon> List
          </el-radio-button>
        </el-radio-group>
        <el-select v-model="floorFilter" placeholder="Floor" clearable class="filter-select" style="width: 120px">
          <el-option label="All Floors" value="" />
          <el-option label="Floor 1" value="1" />
          <el-option label="Floor 2" value="2" />
          <el-option label="Floor 3" value="3" />
          <el-option label="Floor 4" value="4" />
          <el-option label="Floor 5" value="5" />
        </el-select>
        <el-select v-model="capacityFilter" placeholder="Capacity" clearable class="filter-select" style="width: 120px">
          <el-option label="Any" value="" />
          <el-option label="2-4 People" value="2-4" />
          <el-option label="4-6 People" value="4-6" />
          <el-option label="6-10 People" value="6-10" />
          <el-option label="10+ People" value="10+" />
        </el-select>
      </div>
    </div>

    <!-- Grid View -->
    <div v-if="viewMode === 'grid'" class="rooms-grid">
      <div
          v-for="room in filteredRooms"
          :key="room.id"
          class="room-card"
          :class="{ available: room.status === 'available', occupied: room.status === 'occupied' }"
          @click="viewRoomDetail(room)"
      >
        <div class="room-card-header">
          <div class="room-name">{{ room.name }}</div>
          <div class="room-status" :class="room.status">
            {{ room.status === 'available' ? 'Available' : 'In Use' }}
          </div>
        </div>
        <div class="room-details">
          <div class="room-detail-item">
            <el-icon><User /></el-icon>
            <span>Capacity: {{ room.capacity }} people</span>
          </div>
          <div class="room-detail-item">
            <el-icon><Location /></el-icon>
            <span>Floor {{ room.floor }}</span>
          </div>
          <div class="room-detail-item">
            <el-icon><Monitor /></el-icon>
            <span>{{ room.equipment.join(', ') }}</span>
          </div>
        </div>
        <div class="room-current-booking" v-if="room.currentBooking">
          <div class="current-label">Current Booking</div>
          <div class="current-info">{{ room.currentBooking.title }}</div>
          <div class="current-time">{{ room.currentBooking.time }}</div>
        </div>
        <div class="room-actions">
          <el-button
              v-if="room.status === 'available'"
              class="book-btn"
              size="small"
              @click.stop="quickBook(room)"
          >
            Book Now
          </el-button>
          <el-button v-else class="view-btn" size="small" @click.stop="viewRoomDetail(room)">
            View Schedule
          </el-button>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="filteredRooms.length === 0" class="empty-state">
        <div class="empty-icon">🏢</div>
        <h3>No meeting rooms found</h3>
        <p>Try adjusting your filters</p>
      </div>
    </div>

    <!-- List View -->
    <div v-else class="rooms-list">
      <el-table :data="filteredRooms" stripe style="width: 100%" class="rooms-table">
        <el-table-column prop="name" label="Room Name" min-width="150">
          <template #default="{ row }">
            <div class="room-name-cell">
              <div class="room-icon" :class="row.status">{{ row.name.charAt(0) }}</div>
              <div>
                <div class="room-name-text">{{ row.name }}</div>
                <div class="room-location">Floor {{ row.floor }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="capacity" label="Capacity" width="120">
          <template #default="{ row }">
            <el-tag size="small">{{ row.capacity }} people</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="equipment" label="Equipment" min-width="200">
          <template #default="{ row }">
            <div class="equipment-tags">
              <el-tag v-for="eq in row.equipment.slice(0, 3)" :key="eq" size="small" effect="plain">{{ eq }}</el-tag>
              <span v-if="row.equipment.length > 3" class="more-equipment">+{{ row.equipment.length - 3 }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="120">
          <template #default="{ row }">
            <el-tag :type="row.status === 'available' ? 'success' : 'danger'" size="small">
              {{ row.status === 'available' ? 'Available' : 'In Use' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Current Booking" min-width="180">
          <template #default="{ row }">
            <div v-if="row.currentBooking">
              <div class="current-booking-title">{{ row.currentBooking.title }}</div>
              <div class="current-booking-time">{{ row.currentBooking.time }}</div>
            </div>
            <span v-else class="available-text">No current booking</span>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="120" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewRoomDetail(row)">Schedule</el-button>
            <el-button v-if="row.status === 'available'" link type="success" size="small" @click="quickBook(row)">Book</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- Today's Schedule -->
    <div class="schedule-section">
      <div class="section-header">
        <div class="section-title-wrapper">
          <span class="section-icon">📅</span>
          <h2 class="section-title">Today's Schedule</h2>
        </div>
        <el-button class="outline-btn" @click="exportSchedule">
          <el-icon><Download /></el-icon> Export
        </el-button>
      </div>
      <div class="schedule-timeline">
        <div class="timeline-header">
          <div class="time-label">Time</div>
          <div class="rooms-header">
            <div v-for="room in displayRooms" :key="room.id" class="room-header">
              {{ room.name }}
            </div>
          </div>
        </div>
        <div class="timeline-body">
          <div v-for="hour in businessHours" :key="hour" class="timeline-row">
            <div class="time-slot">{{ hour }}:00</div>
            <div class="bookings-row">
              <div v-for="room in displayRooms" :key="room.id" class="booking-cell" :class="getBookingClass(room, hour)">
                <span v-if="getBookingAtHour(room, hour)" class="booking-info">
                  {{ getBookingAtHour(room, hour)?.title }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Upcoming Bookings Table -->
    <div class="table-container">
      <div class="table-header">
        <span class="table-title">Upcoming Bookings</span>
        <el-button size="small" class="view-all-btn" @click="viewAllBookings">View All →</el-button>
      </div>
      <el-table :data="paginatedBookings" stripe style="width: 100%" v-loading="tableLoading" class="bookings-table">
        <el-table-column prop="id" label="ID" width="100" />
        <el-table-column prop="roomName" label="Room" width="140" />
        <el-table-column prop="title" label="Meeting Title" min-width="200" />
        <el-table-column prop="organizer" label="Organizer" width="140" />
        <el-table-column prop="date" label="Date" width="120" />
        <el-table-column prop="time" label="Time" width="160" />
        <el-table-column prop="attendees" label="Attendees" width="100">
          <template #default="{ row }">
            {{ row.attendees.length }} people
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="getBookingStatusType(row.status)" size="small">{{ getBookingStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="100" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewBookingDetail(row)">Details</el-button>
            <el-button link type="danger" size="small" @click="cancelBooking(row)">Cancel</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <div class="pagination-container">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50]"
            :total="totalBookings"
            layout="total, sizes, prev, pager, next"
            background
        />
      </div>
    </div>

    <!-- Booking Dialog -->
    <el-dialog v-model="bookingDialogVisible" title="Book Meeting Room" width="550px" class="booking-dialog">
      <div class="dialog-header-icon">📅</div>
      <el-form :model="bookingForm" :rules="bookingRules" ref="bookingFormRef" label-width="110px">
        <el-form-item label="Room" prop="roomId">
          <el-select v-model="bookingForm.roomId" placeholder="Select room" style="width: 100%" @change="onRoomChange">
            <el-option v-for="room in availableRooms" :key="room.id" :label="room.name" :value="room.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="Meeting Title" prop="title">
          <el-input v-model="bookingForm.title" placeholder="Enter meeting title" />
        </el-form-item>
        <el-form-item label="Date" prop="date">
          <el-date-picker v-model="bookingForm.date" type="date" placeholder="Select date" format="YYYY-MM-DD" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Start Time" prop="startTime">
          <el-time-picker v-model="bookingForm.startTime" placeholder="Select start time" format="HH:mm" value-format="HH:mm" style="width: 100%" />
        </el-form-item>
        <el-form-item label="End Time" prop="endTime">
          <el-time-picker v-model="bookingForm.endTime" placeholder="Select end time" format="HH:mm" value-format="HH:mm" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Organizer" prop="organizer">
          <el-input v-model="bookingForm.organizer" placeholder="Enter organizer name" />
        </el-form-item>
        <el-form-item label="Attendees">
          <el-select v-model="bookingForm.attendees" multiple filterable allow-create placeholder="Select or enter attendees" style="width: 100%">
            <el-option v-for="user in users" :key="user" :label="user" :value="user" />
          </el-select>
        </el-form-item>
        <el-form-item label="Equipment Needed">
          <el-checkbox-group v-model="bookingForm.equipment">
            <el-checkbox label="Projector">Projector</el-checkbox>
            <el-checkbox label="Whiteboard">Whiteboard</el-checkbox>
            <el-checkbox label="Video Conferencing">Video Conferencing</el-checkbox>
            <el-checkbox label="Conference Phone">Conference Phone</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        <el-form-item label="Notes">
          <el-input v-model="bookingForm.notes" type="textarea" :rows="2" placeholder="Additional notes..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button class="cancel-btn" @click="bookingDialogVisible = false">Cancel</el-button>
          <el-button class="submit-btn" @click="submitBooking">
            <el-icon><Plus /></el-icon> Book Room
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- Booking Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" :title="selectedBooking?.title" width="600px" class="detail-dialog">
      <div v-if="selectedBooking" class="booking-detail">
        <div class="detail-header">
          <div class="detail-room">{{ selectedBooking.roomName }}</div>
          <el-tag :type="getBookingStatusType(selectedBooking.status)" size="large">{{ getBookingStatusText(selectedBooking.status) }}</el-tag>
        </div>

        <el-descriptions :column="2" border>
          <el-descriptions-item label="Booking ID">{{ selectedBooking.id }}</el-descriptions-item>
          <el-descriptions-item label="Organizer">{{ selectedBooking.organizer }}</el-descriptions-item>
          <el-descriptions-item label="Date">{{ selectedBooking.date }}</el-descriptions-item>
          <el-descriptions-item label="Time">{{ selectedBooking.time }}</el-descriptions-item>
          <el-descriptions-item label="Attendees" :span="2">
            <div class="attendees-list">
              <el-tag v-for="a in selectedBooking.attendees" :key="a" size="small" effect="plain">{{ a }}</el-tag>
            </div>
          </el-descriptions-item>
          <el-descriptions-item label="Equipment" :span="2">
            <div class="equipment-list">
              <el-tag v-for="e in selectedBooking.equipment" :key="e" size="small" effect="plain">{{ e }}</el-tag>
              <span v-if="!selectedBooking.equipment?.length" class="empty-text">None</span>
            </div>
          </el-descriptions-item>
          <el-descriptions-item label="Notes" :span="2">{{ selectedBooking.notes || 'No notes' }}</el-descriptions-item>
        </el-descriptions>

        <div class="detail-actions" v-if="selectedBooking.status === 'confirmed'">
          <el-button type="success" @click="checkInBooking(selectedBooking)">Check In</el-button>
          <el-button type="warning" @click="rescheduleBooking(selectedBooking)">Reschedule</el-button>
          <el-button type="danger" @click="cancelBooking(selectedBooking)">Cancel Booking</el-button>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="sendReminder(selectedBooking)">Send Reminder</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  OfficeBuilding, Plus, Refresh, CircleCheck, Calendar, User, Grid, List,
  Location, Monitor, Download
} from '@element-plus/icons-vue'

// ==================== Helper Functions ====================
const getBookingStatusText = (status: string): string => {
  const map: Record<string, string> = { confirmed: 'Confirmed', completed: 'Completed', cancelled: 'Cancelled', 'no-show': 'No-Show' }
  return map[status] || status
}

const getBookingStatusType = (status: string): string => {
  const map: Record<string, string> = { confirmed: 'success', completed: 'info', cancelled: 'danger', 'no-show': 'warning' }
  return map[status] || 'info'
}

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading meeting room data...')
const refreshing = ref(false)
const tableLoading = ref(false)

const loadingMessages = [
  'Loading meeting rooms...',
  'Fetching schedules...',
  'Loading booking data...',
  'Almost ready...'
]

// ==================== Types ====================
interface Room {
  id: number
  name: string
  floor: number
  capacity: number
  equipment: string[]
  status: string
  currentBooking?: {
    title: string
    time: string
  }
  bookings: Booking[]
}

interface Booking {
  id: string
  roomId: number
  roomName: string
  title: string
  organizer: string
  date: string
  startTime: string
  endTime: string
  time: string
  attendees: string[]
  equipment: string[]
  notes: string
  status: string
}

// ==================== Mock Data ====================
const roomsData: Room[] = [
  { id: 1, name: 'Boardroom A', floor: 1, capacity: 12, equipment: ['Projector', 'Whiteboard', 'Video Conferencing', 'Conference Phone'], status: 'available', bookings: [] },
  { id: 2, name: 'Meeting Room B', floor: 1, capacity: 6, equipment: ['Projector', 'Whiteboard'], status: 'occupied', bookings: [], currentBooking: { title: 'Sales Team Meeting', time: '10:00 - 11:30' } },
  { id: 3, name: 'Conference Room C', floor: 2, capacity: 20, equipment: ['Projector', 'Video Conferencing', 'Sound System', 'Conference Phone'], status: 'available', bookings: [] },
  { id: 4, name: 'Huddle Room D', floor: 2, capacity: 4, equipment: ['Whiteboard', 'TV Screen'], status: 'available', bookings: [] },
  { id: 5, name: 'Training Room E', floor: 3, capacity: 30, equipment: ['Projector', 'Sound System', 'Whiteboard', 'Video Conferencing'], status: 'occupied', bookings: [], currentBooking: { title: 'Staff Training', time: '09:00 - 17:00' } },
  { id: 6, name: 'Executive Suite', floor: 3, capacity: 8, equipment: ['Projector', 'Video Conferencing', 'Conference Phone', 'Whiteboard'], status: 'available', bookings: [] },
  { id: 7, name: 'Collaboration Space', floor: 4, capacity: 10, equipment: ['Whiteboard', 'TV Screen', 'Video Conferencing'], status: 'available', bookings: [] },
  { id: 8, name: 'Focus Room F', floor: 4, capacity: 2, equipment: ['TV Screen'], status: 'occupied', bookings: [], currentBooking: { title: '1-on-1 Meeting', time: '11:00 - 12:00' } },
]

const generateBookings = (): Booking[] => {
  const bookings: Booking[] = []
  const today = new Date().toISOString().slice(0, 10)
  const tomorrow = new Date()
  tomorrow.setDate(tomorrow.getDate() + 1)
  const tomorrowStr = tomorrow.toISOString().slice(0, 10)

  const bookingData = [
    { roomId: 1, title: 'Weekly Review', organizer: 'John Tan', date: today, start: '10:00', end: '11:00', attendees: ['John Tan', 'Mike Chen', 'Sarah Koh'] },
    { roomId: 2, title: 'Product Planning', organizer: 'Mike Chen', date: today, start: '14:00', end: '15:30', attendees: ['Mike Chen', 'David Lee', 'Amy Wong'] },
    { roomId: 3, title: 'Client Presentation', organizer: 'Sarah Koh', date: today, start: '15:00', end: '16:30', attendees: ['Sarah Koh', 'John Tan', 'Client Team'] },
    { roomId: 4, title: 'Quick Sync', organizer: 'Lim Wei Ming', date: today, start: '11:30', end: '12:00', attendees: ['Lim Wei Ming', 'Ahmad Ibrahim'] },
    { roomId: 1, title: 'Strategy Meeting', organizer: 'David Lee', date: tomorrowStr, start: '09:30', end: '11:00', attendees: ['David Lee', 'John Tan', 'Mike Chen', 'Sarah Koh'] },
    { roomId: 3, title: 'All Hands', organizer: 'Management', date: tomorrowStr, start: '14:00', end: '16:00', attendees: ['All Staff'] },
    { roomId: 6, title: 'Executive Review', organizer: 'CEO Office', date: tomorrowStr, start: '10:00', end: '11:30', attendees: ['Executive Team'] },
    { roomId: 7, title: 'Team Brainstorm', organizer: 'Priya Sharma', date: tomorrowStr, start: '13:00', end: '15:00', attendees: ['Priya Sharma', 'Team Members'] },
  ]

  bookingData.forEach((b, i) => {
    bookings.push({
      id: `BK-${String(i + 1).padStart(6, '0')}`,
      roomId: b.roomId,
      roomName: roomsData.find(r => r.id === b.roomId)?.name || '',
      title: b.title,
      organizer: b.organizer,
      date: b.date,
      startTime: b.start,
      endTime: b.end,
      time: `${b.start} - ${b.end}`,
      attendees: b.attendees,
      equipment: ['Projector', 'Whiteboard'],
      notes: '',
      status: 'confirmed'
    })
  })

  return bookings
}

const bookings = ref<Booking[]>(generateBookings())
const rooms = ref<Room[]>(roomsData)

// Update rooms with bookings
rooms.value.forEach(room => {
  room.bookings = bookings.value.filter(b => b.roomId === room.id)
})

// ==================== State ====================
const viewMode = ref('grid')
const floorFilter = ref('')
const capacityFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const bookingDialogVisible = ref(false)
const detailDialogVisible = ref(false)
const selectedBooking = ref<Booking | null>(null)
const bookingFormRef = ref()

const users = ['John Tan', 'Mike Chen', 'Sarah Koh', 'Lim Wei Ming', 'Ahmad Ibrahim', 'David Lee', 'Priya Sharma', 'Amy Wong']

const businessHours = Array.from({ length: 12 }, (_, i) => i + 8) // 8:00 to 19:00

const bookingForm = ref({
  roomId: null as number | null,
  title: '',
  date: new Date().toISOString().slice(0, 10),
  startTime: '10:00',
  endTime: '11:00',
  organizer: '',
  attendees: [] as string[],
  equipment: [] as string[],
  notes: ''
})

const bookingRules = {
  roomId: [{ required: true, message: 'Please select a room', trigger: 'change' }],
  title: [{ required: true, message: 'Please enter meeting title', trigger: 'blur' }],
  date: [{ required: true, message: 'Please select date', trigger: 'change' }],
  startTime: [{ required: true, message: 'Please select start time', trigger: 'change' }],
  endTime: [{ required: true, message: 'Please select end time', trigger: 'change' }],
  organizer: [{ required: true, message: 'Please enter organizer name', trigger: 'blur' }]
}

// ==================== Computed ====================
const stats = computed(() => {
  const totalRooms = rooms.value.length
  const availableNow = rooms.value.filter(r => r.status === 'available').length
  const availablePercent = Math.round((availableNow / totalRooms) * 100)
  const today = new Date().toISOString().slice(0, 10)
  const todayBookings = bookings.value.filter(b => b.date === today).length
  const totalBookings = bookings.value.length

  return { totalRooms, availableNow, availablePercent, todayBookings, totalBookings }
})

const filteredRooms = computed(() => {
  let filtered = [...rooms.value]

  if (floorFilter.value) {
    filtered = filtered.filter(r => r.floor === parseInt(floorFilter.value))
  }

  if (capacityFilter.value === '2-4') {
    filtered = filtered.filter(r => r.capacity >= 2 && r.capacity <= 4)
  } else if (capacityFilter.value === '4-6') {
    filtered = filtered.filter(r => r.capacity >= 4 && r.capacity <= 6)
  } else if (capacityFilter.value === '6-10') {
    filtered = filtered.filter(r => r.capacity >= 6 && r.capacity <= 10)
  } else if (capacityFilter.value === '10+') {
    filtered = filtered.filter(r => r.capacity > 10)
  }

  return filtered
})

const displayRooms = computed(() => {
  return filteredRooms.value.slice(0, 6)
})

const upcomingBookings = computed(() => {
  const today = new Date().toISOString().slice(0, 10)
  return bookings.value.filter(b => b.date >= today).sort((a, b) => a.date.localeCompare(b.date))
})

const paginatedBookings = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return upcomingBookings.value.slice(start, end)
})

const totalBookings = computed(() => upcomingBookings.value.length)

const availableRooms = computed(() => {
  return rooms.value.filter(r => r.status === 'available')
})

// ==================== Helper Functions ====================
const getBookingClass = (room: Room, hour: number) => {
  const booking = room.bookings.find(b => {
    const startHour = parseInt(b.startTime.split(':')[0])
    const endHour = parseInt(b.endTime.split(':')[0])
    return hour >= startHour && hour < endHour
  })
  return booking ? 'booked' : ''
}

const getBookingAtHour = (room: Room, hour: number) => {
  return room.bookings.find(b => {
    const startHour = parseInt(b.startTime.split(':')[0])
    const endHour = parseInt(b.endTime.split(':')[0])
    return hour >= startHour && hour < endHour
  })
}

const onRoomChange = () => {}

const quickBook = (room: Room) => {
  bookingForm.value = {
    roomId: room.id,
    title: '',
    date: new Date().toISOString().slice(0, 10),
    startTime: '10:00',
    endTime: '11:00',
    organizer: '',
    attendees: [],
    equipment: [],
    notes: ''
  }
  bookingDialogVisible.value = true
}

const viewRoomDetail = (room: Room) => {
  ElMessage.info(`Viewing schedule for ${room.name}`)
}

const viewBookingDetail = (booking: Booking) => {
  selectedBooking.value = booking
  detailDialogVisible.value = true
}

const checkInBooking = (booking: Booking | null) => {
  if (booking) {
    ElMessage.success(`Checked in for ${booking.title}`)
  }
}

const rescheduleBooking = (booking: Booking | null) => {
  if (booking) {
    ElMessage.info(`Reschedule booking for ${booking.title}`)
  }
}

const cancelBooking = (booking: Booking | null) => {
  if (booking) {
    ElMessageBox.confirm(`Cancel booking for "${booking.title}"?`, 'Confirm Cancellation', {
      confirmButtonText: 'Yes, Cancel',
      cancelButtonText: 'No',
      type: 'warning'
    }).then(() => {
      const index = bookings.value.findIndex(b => b.id === booking.id)
      if (index !== -1) {
        bookings.value[index].status = 'cancelled'
        ElMessage.success('Booking cancelled successfully')
      }
      detailDialogVisible.value = false
    }).catch(() => {})
  }
}

const sendReminder = (booking: Booking | null) => {
  if (booking) {
    ElMessage.success(`Reminder sent for ${booking.title}`)
  }
}

const openBookingDialog = () => {
  quickBook(rooms.value[0])
}

const submitBooking = async () => {
  if (!bookingFormRef.value) return
  await bookingFormRef.value.validate((valid: boolean) => {
    if (valid) {
      const newBooking: Booking = {
        id: `BK-${String(bookings.value.length + 1).padStart(6, '0')}`,
        roomId: bookingForm.value.roomId!,
        roomName: rooms.value.find(r => r.id === bookingForm.value.roomId)?.name || '',
        title: bookingForm.value.title,
        organizer: bookingForm.value.organizer,
        date: bookingForm.value.date,
        startTime: bookingForm.value.startTime,
        endTime: bookingForm.value.endTime,
        time: `${bookingForm.value.startTime} - ${bookingForm.value.endTime}`,
        attendees: bookingForm.value.attendees,
        equipment: bookingForm.value.equipment,
        notes: bookingForm.value.notes,
        status: 'confirmed'
      }
      bookings.value.push(newBooking)
      ElMessage.success('Meeting room booked successfully')
      bookingDialogVisible.value = false
    }
  })
}

const exportSchedule = () => {
  ElMessage.success('Exporting schedule...')
  setTimeout(() => {
    ElMessage.success('Schedule exported successfully')
  }, 1000)
}

const viewAllBookings = () => {
  ElMessage.info('Viewing all bookings')
}

const refreshData = async () => {
  refreshing.value = true
  tableLoading.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  refreshing.value = false
  tableLoading.value = false
  ElMessage.success('Data refreshed')
}

// ==================== Loading Animation ====================
const startLoading = () => {
  let progress = 0
  let messageIndex = 0

  const messageInterval = setInterval(() => {
    if (messageIndex < loadingMessages.length - 1) {
      messageIndex++
      loadingMessage.value = loadingMessages[messageIndex]
    }
  }, 600)

  const progressInterval = setInterval(() => {
    if (progress < 90) {
      progress += Math.random() * 12
      loadingProgress.value = Math.min(progress, 90)
    }
  }, 100)

  setTimeout(() => {
    clearInterval(messageInterval)
    clearInterval(progressInterval)
    loadingProgress.value = 100
    loadingMessage.value = 'Ready!'

    setTimeout(() => {
      isLoaded.value = true
    }, 500)
  }, 2200)
}

onMounted(() => {
  startLoading()
})
</script>

<style scoped>
.meeting-room-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f0f9ff 0%, #e8f0fe 100%);
  padding: 28px;
}

* {
  scrollbar-width: thin;
}
*::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
*::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 10px;
}
*::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 10px;
}

/* Loading Screen */
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
  padding: 48px;
  border-radius: 40px;
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
.spinner-ring:nth-child(4) { border-left-color: #ec489a; animation-delay: 0.6s; width: 20%; height: 20%; top: 40%; left: 40%; }

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  margin-bottom: 24px;
  font-size: 24px;
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

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes pulse {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}

/* Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 28px;
  flex-wrap: wrap;
  gap: 16px;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 14px;
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 8px 0;
}

.title-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.page-subtitle {
  font-size: 14px;
  color: #64748b;
  margin-left: 62px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.primary-btn {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  border: none;
  color: white;
  padding: 10px 20px;
  border-radius: 12px;
  font-weight: 500;
  transition: all 0.3s;
}

.primary-btn:hover {
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}

.secondary-btn {
  background: white;
  border: 1px solid #e2e8f0;
  color: #475569;
  padding: 10px 20px;
  border-radius: 12px;
  transition: all 0.3s;
}

.secondary-btn:hover {
  border-color: #3b82f6;
  color: #3b82f6;
  transform: translateY(-2px);
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 28px;
}

.stat-card {
  background: white;
  border-radius: 24px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26px;
}

.stat-icon.blue { background: linear-gradient(135deg, #eef2ff, #dbeafe); color: #3b82f6; }
.stat-icon.green { background: linear-gradient(135deg, #dcfce7, #bbf7d0); color: #22c55e; }
.stat-icon.orange { background: linear-gradient(135deg, #fef3c7, #fde68a); color: #f59e0b; }
.stat-icon.purple { background: linear-gradient(135deg, #f3e8ff, #e9d5ff); color: #8b5cf6; }

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #1e293b;
}

.stat-unit {
  font-size: 14px;
  font-weight: normal;
  color: #64748b;
  margin-left: 4px;
}

.stat-label {
  font-size: 13px;
  color: #64748b;
  margin-top: 4px;
}

.stat-trend {
  font-size: 11px;
  margin-top: 6px;
}

.stat-trend.up { color: #22c55e; }

/* Section Header */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 16px;
}

.section-title-wrapper {
  display: flex;
  align-items: center;
  gap: 10px;
}

.section-icon {
  font-size: 24px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.view-toggle :deep(.el-radio-button__inner) {
  border-radius: 40px;
  padding: 6px 16px;
}

.filter-select :deep(.el-input__wrapper) {
  border-radius: 40px;
}

/* Rooms Grid */
.rooms-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 20px;
  margin-bottom: 28px;
}

.room-card {
  background: white;
  border-radius: 24px;
  padding: 20px;
  transition: all 0.3s;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  cursor: pointer;
  position: relative;
  overflow: hidden;
}

.room-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #3b82f6, #22c55e);
  opacity: 0;
  transition: opacity 0.3s;
}

.room-card:hover::before {
  opacity: 1;
}

.room-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
}

.room-card.available .room-status { background: #dcfce7; color: #16a34a; }
.room-card.occupied .room-status { background: #fee2e2; color: #dc2626; }

.room-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.room-name {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
}

.room-status {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.room-details {
  margin-bottom: 16px;
}

.room-detail-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #64748b;
  margin-bottom: 8px;
}

.room-current-booking {
  background: #f8fafc;
  border-radius: 16px;
  padding: 12px;
  margin-bottom: 16px;
}

.current-label {
  font-size: 11px;
  color: #94a3b8;
  margin-bottom: 4px;
}

.current-info {
  font-size: 14px;
  font-weight: 500;
  color: #1e293b;
}

.current-time {
  font-size: 11px;
  color: #64748b;
  margin-top: 4px;
}

.room-actions {
  display: flex;
  gap: 12px;
}

.book-btn, .view-btn {
  flex: 1;
  border-radius: 40px;
}

.book-btn {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
  border: none;
}

.view-btn {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
}

/* Rooms List */
.rooms-list {
  background: white;
  border-radius: 24px;
  padding: 20px;
  margin-bottom: 28px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.rooms-table :deep(.el-table__row) {
  cursor: pointer;
}

.room-name-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.room-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 18px;
}

.room-icon.available { background: #dcfce7; color: #16a34a; }
.room-icon.occupied { background: #fee2e2; color: #dc2626; }

.room-name-text {
  font-weight: 500;
  color: #1e293b;
}

.room-location {
  font-size: 11px;
  color: #94a3b8;
}

.equipment-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.more-equipment {
  font-size: 12px;
  color: #94a3b8;
}

.current-booking-title {
  font-size: 13px;
  font-weight: 500;
}

.current-booking-time {
  font-size: 11px;
  color: #94a3b8;
}

.available-text {
  color: #94a3b8;
  font-size: 13px;
}

/* Schedule Section */
.schedule-section {
  background: white;
  border-radius: 24px;
  padding: 20px;
  margin-bottom: 28px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.outline-btn {
  background: transparent;
  border: 1px solid #e2e8f0;
  border-radius: 40px;
  padding: 6px 16px;
}

.schedule-timeline {
  overflow-x: auto;
}

.timeline-header {
  display: flex;
  border-bottom: 2px solid #e2e8f0;
  padding-bottom: 12px;
  margin-bottom: 12px;
}

.time-label {
  width: 80px;
  font-weight: 600;
  color: #1e293b;
}

.rooms-header {
  display: flex;
  flex: 1;
}

.room-header {
  flex: 1;
  text-align: center;
  font-weight: 500;
  font-size: 13px;
  color: #64748b;
}

.timeline-body {
  display: flex;
  flex-direction: column;
}

.timeline-row {
  display: flex;
  border-bottom: 1px solid #f0f0f0;
}

.time-slot {
  width: 80px;
  padding: 12px 0;
  font-size: 12px;
  color: #64748b;
}

.bookings-row {
  display: flex;
  flex: 1;
}

.booking-cell {
  flex: 1;
  padding: 12px 4px;
  text-align: center;
  font-size: 11px;
  border-left: 1px solid #f0f0f0;
  min-height: 50px;
}

.booking-cell.booked {
  background: #eef2ff;
  color: #3b82f6;
}

.booking-info {
  display: block;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Table Container */
.table-container {
  background: white;
  border-radius: 24px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.table-title {
  font-weight: 600;
  font-size: 16px;
  color: #1e293b;
}

.view-all-btn {
  background: transparent;
  border: none;
  color: #3b82f6;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

/* Booking Detail */
.booking-detail {
  padding: 8px;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.detail-room {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
}

.attendees-list, .equipment-list {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.empty-text {
  color: #94a3b8;
}

.detail-actions {
  margin-top: 20px;
  display: flex;
  gap: 12px;
  justify-content: center;
}

/* Dialogs */
.booking-dialog :deep(.el-dialog__header),
.detail-dialog :deep(.el-dialog__header) {
  border-bottom: 1px solid #eef2f8;
  padding: 20px 24px;
}

.dialog-header-icon {
  text-align: center;
  font-size: 48px;
  margin-bottom: 16px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.cancel-btn {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 40px;
  padding: 8px 20px;
}

.submit-btn {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  border: none;
  color: white;
  border-radius: 40px;
  padding: 8px 20px;
}

/* Empty State */
.empty-state {
  grid-column: 1 / -1;
  text-align: center;
  padding: 60px;
  background: white;
  border-radius: 24px;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.empty-state h3 {
  font-size: 18px;
  color: #1e293b;
  margin: 0 0 8px 0;
}

.empty-state p {
  font-size: 14px;
  color: #64748b;
  margin-bottom: 20px;
}

/* Responsive */
@media (max-width: 1000px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .rooms-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }
  .section-header {
    flex-direction: column;
    align-items: flex-start;
  }
  .schedule-timeline {
    font-size: 10px;
  }
  .time-label, .time-slot {
    width: 60px;
  }
}

/* Element Plus Overrides */
:deep(.el-table) {
  border-radius: 16px;
  overflow: hidden;
}
:deep(.el-table th.el-table__cell) {
  background-color: #f8fafc;
  color: #1e293b;
  font-weight: 600;
}
:deep(.el-table .el-table__row:hover > td.el-table__cell) {
  background-color: #f0f7ff;
}
:deep(.el-button--primary) {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  border: none;
}
:deep(.el-pagination.is-background .el-pager li.is-active) {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
}
:deep(.el-dialog__body) {
  padding: 20px;
}
</style>