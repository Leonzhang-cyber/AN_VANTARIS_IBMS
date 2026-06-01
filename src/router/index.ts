import { createRouter, createWebHistory } from 'vue-router'
import Layout from '@/views/layout/Layout.vue'
import Login from '@/views/Login/Login.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: Layout,
    redirect: 'home/system-overview/total-devices-online-rate',  // 直接重定向，不要嵌套 children 的重定向
    children: [
      //   1 home
      {
        path: 'home',
        name: 'Home',
        children: [
          // 1.1 系统概览
          {
            path: 'system-overview',
            name: 'SystemOverview',
            children: [
              // 1.1.1 设备总数/在线率
              {
                path: 'total-devices-online-rate',
                name: 'TotalDevicesOnlineRate',
                component: () => import('@/views/Home/SystemOverview/TotalDevicesOnlineRate.vue'),
                meta: { title: 'Total Devices / Online Rate' }
              },
              // 1.1.2 活跃告警
              {
                path: 'active-alarms',
                name: 'ActiveAlarms',
                component: () => import('@/views/Home/SystemOverview/ActiveAlarms.vue'),
                meta: { title: 'Active Alarms' }
              },
              // 1.1.3 未结工单
              {
                path: 'open-work-orders',
                name: 'OpenWorkOrders',
                component: () => import('@/views/Home/SystemOverview/OpenWorkOrders.vue'),
                meta: { title: 'Open Work Orders' }
              },
              // 1.1.4 系统健康度
              {
                path: 'system-health',
                name: 'SystemHealth',
                component: () => import('@/views/Home/SystemOverview/SystemHealth.vue'),
                meta: { title: 'System Health' }
              }
            ]
          },
          // =============== 1.2 KPI Dashboard (四级路由) ===============
          {
            path: 'kpi-dashboard',
            name: 'KpiDashboard',
            children: [
              // 1.2.1 Operational KPI
              {
                path: 'operational-kpi',
                name: 'OperationalKpi',
                children: [
                  {
                    path: 'availability',
                    name: 'Availability',
                    component: () => import('@/views/Home/KpiDashboard/OperationalKpi/Availability.vue'),
                    meta: { title: 'Availability' }
                  },
                  {
                    path: 'sla-compliance',
                    name: 'SlaCompliance',
                    component: () => import('@/views/Home/KpiDashboard/OperationalKpi/SlaCompliance.vue'),
                    meta: { title: 'SLA Compliance' }
                  },
                  {
                    path: 'response-time',
                    name: 'ResponseTime',
                    component: () => import('@/views/Home/KpiDashboard/OperationalKpi/ResponseTime.vue'),
                    meta: { title: 'Response Time' }
                  }
                ]
              },
              // 1.2.2 Energy KPI
              {
                path: 'energy-kpi',
                name: 'EnergyKpi',
                children: [
                  {
                    path: 'energy-intensity',
                    name: 'EnergyIntensity',
                    component: () => import('@/views/Home/KpiDashboard/EnergyKpi/EnergyIntensity.vue'),
                    meta: { title: 'Energy Intensity' }
                  },
                  {
                    path: 'peak-demand',
                    name: 'PeakDemandView',
                    component: () => import('@/views/Home/KpiDashboard/EnergyKpi/PeakDemand.vue'),
                    meta: { title: 'Peak Demand' }
                  },
                  {
                    path: 'savings-progress',
                    name: 'SavingsProgress',
                    component: () => import('@/views/Home/KpiDashboard/EnergyKpi/SavingsProgress.vue'),
                    meta: { title: 'Savings Progress' }
                  }
                ]
              },
              // 1.2.3 ESG KPI
              {
                path: 'esg-kpi',
                name: 'EsgKpi',
                children: [
                  {
                    path: 'carbon-intensity',
                    name: 'CarbonIntensityView',
                    component: () => import('@/views/Home/KpiDashboard/EsgKpi/CarbonIntensity.vue'),
                    meta: { title: 'Carbon Intensity' }
                  },
                  {
                    path: 'esg-score',
                    name: 'EsgScore',
                    component: () => import('@/views/Home/KpiDashboard/EsgKpi/EsgScore.vue'),
                    meta: { title: 'ESG Score' }
                  },
                  {
                    path: 'compliance-gap',
                    name: 'ComplianceGap',
                    component: () => import('@/views/Home/KpiDashboard/EsgKpi/ComplianceGap.vue'),
                    meta: { title: 'Compliance Gap' }
                  }
                ]
              },
              // 1.2.4 Facility KPI
              {
                path: 'facility-kpi',
                name: 'FacilityKpi',
                children: [
                  {
                    path: 'occupancy',
                    name: 'Occupancy',
                    component: () => import('@/views/Home/KpiDashboard/FacilityKpi/Occupancy.vue'),
                    meta: { title: 'Occupancy' }
                  },
                  {
                    path: 'service-requests',
                    name: 'ServiceRequests',
                    component: () => import('@/views/Home/KpiDashboard/FacilityKpi/ServiceRequests.vue'),
                    meta: { title: 'Service Requests' }
                  },
                  {
                    path: 'customer-satisfaction',
                    name: 'CustomerSatisfaction',
                    component: () => import('@/views/Home/KpiDashboard/FacilityKpi/CustomerSatisfaction.vue'),
                    meta: { title: 'Customer Satisfaction' }
                  }
                ]
              }
            ]
          },
          // =============== 1.3 Alarm Summary ===============
          {
            path: 'alarm-summary',
            name: 'AlarmSummary',
            children: [
              {
                path: 'critical',
                name: 'CriticalAlarm',
                component: () => import('@/views/Home/AlarmSummary/Critical.vue'),
                meta: { title: 'Critical' }
              },
              {
                path: 'major',
                name: 'MajorAlarm',
                component: () => import('@/views/Home/AlarmSummary/Major.vue'),
                meta: { title: 'Major' }
              },
              {
                path: 'warning',
                name: 'WarningAlarm',
                component: () => import('@/views/Home/AlarmSummary/Warning.vue'),
                meta: { title: 'Warning' }
              },
              {
                path: 'information',
                name: 'InformationAlarm',
                component: () => import('@/views/Home/AlarmSummary/Information.vue'),
                meta: { title: 'Information' }
              }
            ]
          },
          {
            path: 'energy-overview',
            name: 'EnergyOverview',
            component: () => import('@/views/Home/Energy.vue'),
            meta: { title: 'Energy Overview' }
          },
          {
            path: 'site-health-dashboard',
            name: 'SiteHealthDashboard',
            component: () => import('@/views/Home/Site.vue'),
            meta: { title: 'Site Health Dashboard' }
          },
          {
            path: 'esg-dashboard',
            name: 'ESGDashboard',
            component: () => import('@/views/Home/ESG.vue'),
            meta: { title: 'ESG Dashboard' }
          },
          {
            path: 'portfolio-dashboard',
            name: 'PortfolioDashboard',
            component: () => import('@/views/Home/Portfolio.vue'),
            meta: { title: 'Portfolio Dashboard' }
          },
          {
            path: 'data-center',
            name: 'DataCenter',
            component: () => import('@/views/Home/DataCenter.vue'),
            meta: { title: 'Data Center Dashboard' }
          },
          {
            path: 'sustainability-summary',
            name: 'SustainabilitySummary',
            component: () => import('@/views/Home/SustainabilitySummary.vue'),
            meta: { title: 'Sustainability Summary' }
          },
          {
            path: 'ai-insights',
            name: 'AIInsights',
            component: () => import('@/views/Home/AI.vue'),
            meta: { title: 'AI Insights' }
          }
        ]
      },
      //   2 operations
      {
        path: 'operations',
        name: 'Operations',
        children: [
          // 2.1 Quick Control
          {
            path: 'quick-control',
            name: 'QuickControl',
            children: [
              // 2.1.1 HVAC Control
              {
                path: 'hvac-control',
                name: 'HvacControl',
                children: [
                  {
                    path: 'temperature-setpoint',
                    name: 'TemperatureSetpoint',
                    component: () => import('@/views/Operations/QuickControl/HvacControl/TemperatureSetpoint.vue'),
                    meta: { title: 'Temperature Setpoint' }
                  },
                  {
                    path: 'mode-control',
                    name: 'ModeControl',
                    component: () => import('@/views/Operations/QuickControl/HvacControl/ModeControl.vue'),
                    meta: { title: 'Mode Control' }
                  },
                  {
                    path: 'fan-speed',
                    name: 'FanSpeed',
                    component: () => import('@/views/Operations/QuickControl/HvacControl/FanSpeed.vue'),
                    meta: { title: 'Fan Speed' }
                  }
                ]
              },
              // 2.1.2 Lighting Control
              {
                path: 'lighting-control',
                name: 'LightingControl',
                children: [
                  {
                    path: 'all-on-all-off',
                    name: 'AllOnAllOff',
                    component: () => import('@/views/Operations/QuickControl/LightingControl/AllOnAllOff.vue'),
                    meta: { title: 'All On / All Off' }
                  },
                  {
                    path: 'zone-control',
                    name: 'ZoneControl',
                    component: () => import('@/views/Operations/QuickControl/LightingControl/ZoneControl.vue'),
                    meta: { title: 'Zone Control' }
                  },
                  {
                    path: 'schedule-override',
                    name: 'ScheduleOverride',
                    component: () => import('@/views/Operations/QuickControl/LightingControl/ScheduleOverride.vue'),
                    meta: { title: 'Schedule Override' }
                  }
                ]
              },
              // 2.1.3 Access Control
              {
                path: 'access-control',
                name: 'AccessControl',
                children: [
                  {
                    path: 'door-open-close',
                    name: 'DoorOpenClose',
                    component: () => import('@/views/Operations/QuickControl/AccessControl/DoorOpenClose.vue'),
                    meta: { title: 'Door Open / Close' }
                  },
                  {
                    path: 'lockdown',
                    name: 'Lockdown',
                    component: () => import('@/views/Operations/QuickControl/AccessControl/Lockdown.vue'),
                    meta: { title: 'Lockdown' }
                  },
                  {
                    path: 'access-status',
                    name: 'AccessStatus',
                    component: () => import('@/views/Operations/QuickControl/AccessControl/AccessStatus.vue'),
                    meta: { title: 'Access Status' }
                  }
                ]
              },
              // 2.1.4 CCTV Control
              {
                path: 'cctv-control',
                name: 'CctvControl',
                children: [
                  {
                    path: 'live-view',
                    name: 'LiveView',
                    component: () => import('@/views/Operations/QuickControl/CctvControl/LiveView.vue'),
                    meta: { title: 'Live View' }
                  },
                  {
                    path: 'snapshot',
                    name: 'Snapshot',
                    component: () => import('@/views/Operations/QuickControl/CctvControl/Snapshot.vue'),
                    meta: { title: 'Snapshot' }
                  },
                  {
                    path: 'ptz-preset',
                    name: 'PtzPreset',
                    component: () => import('@/views/Operations/QuickControl/CctvControl/PtzPreset.vue'),
                    meta: { title: 'PTZ Preset' }
                  }
                ]
              },
              // 2.1.5 Emergency Devices
              {
                path: 'emergency-devices',
                name: 'EmergencyDevices',
                children: [
                  {
                    path: 'emergency-lighting',
                    name: 'EmergencyLighting',
                    component: () => import('@/views/Operations/QuickControl/EmergencyDevices/EmergencyLighting.vue'),
                    meta: { title: 'Emergency Lighting' }
                  },
                  {
                    path: 'pa-broadcast',
                    name: 'PaBroadcast',
                    component: () => import('@/views/Operations/QuickControl/EmergencyDevices/PaBroadcast.vue'),
                    meta: { title: 'PA Broadcast' }
                  },
                  {
                    path: 'panic-button',
                    name: 'PanicButton',
                    component: () => import('@/views/Operations/QuickControl/EmergencyDevices/PanicButton.vue'),
                    meta: { title: 'Panic Button' }
                  }
                ]
              }
            ]
          },
          // 2.2 Scene Management
          {
            path: 'scene-management',
            name: 'SceneManagement',
            children: [
              {
                path: 'normal-mode',
                name: 'NormalMode',
                component: () => import('@/views/Operations/SceneManagement/NormalMode.vue'),
                meta: { title: 'Normal Mode' }
              },
              {
                path: 'energy-saving-mode',
                name: 'EnergySavingMode',
                component: () => import('@/views/Operations/SceneManagement/EnergySavingMode.vue'),
                meta: { title: 'Energy Saving Mode' }
              },
              {
                path: 'maintenance-mode',
                name: 'MaintenanceMode',
                component: () => import('@/views/Operations/SceneManagement/MaintenanceMode.vue'),
                meta: { title: 'Maintenance Mode' }
              },
              {
                path: 'emergency-mode',
                name: 'EmergencyMode',
                component: () => import('@/views/Operations/SceneManagement/EmergencyMode.vue'),
                meta: { title: 'Emergency Mode' }
              },
              {
                path: 'custom-scenes',
                name: 'CustomScenes',
                component: () => import('@/views/Operations/SceneManagement/CustomScenes.vue'),
                meta: { title: 'Custom Scenes' }
              }
            ]
          },
          // 2.3 Emergency Response
          {
            path: 'emergency-response',
            name: 'EmergencyResponse',
            children: [
              {
                path: 'fire-emergency',
                name: 'FireEmergency',
                component: () => import('@/views/Operations/EmergencyResponse/FireEmergency.vue'),
                meta: { title: 'Fire Emergency' }
              },
              {
                path: 'security-emergency',
                name: 'SecurityEmergency',
                component: () => import('@/views/Operations/EmergencyResponse/SecurityEmergency.vue'),
                meta: { title: 'Security Emergency' }
              },
              {
                path: 'medical-emergency',
                name: 'MedicalEmergency',
                component: () => import('@/views/Operations/EmergencyResponse/MedicalEmergency.vue'),
                meta: { title: 'Medical Emergency' }
              },
              {
                path: 'power-outage',
                name: 'PowerOutage',
                component: () => import('@/views/Operations/EmergencyResponse/PowerOutage.vue'),
                meta: { title: 'Power Outage' }
              }
            ]
          },
          // 2.4 Operations Logbook
          {
            path: 'operations-logbook',
            name: 'OperationsLogbook',
            component: () => import('@/views/Operations/OperationsLogbook.vue'),
            meta: { title: 'Operations Logbook' }
          },
          // 2.5 Shift Handover
          {
            path: 'shift-handover',
            name: 'ShiftHandover',
            component: () => import('@/views/Operations/ShiftHandover.vue'),
            meta: { title: 'Shift Handover' }
          },
          // 2.6 Operator Notes
          {
            path: 'operator-notes',
            name: 'OperatorNotes',
            component: () => import('@/views/Operations/OperatorNotes.vue'),
            meta: { title: 'Operator Notes' }
          },
          // 2.7 Incident Reporting
          {
            path: 'incident-reporting',
            name: 'IncidentReporting',
            component: () => import('@/views/Operations/IncidentReporting.vue'),
            meta: { title: 'Incident Reporting' }
          },
          // 2.8 Daily Checklist
          {
            path: 'daily-checklist',
            name: 'DailyChecklist',
            component: () => import('@/views/Operations/DailyChecklist.vue'),
            meta: { title: 'Daily Checklist' }
          }
        ]
      },
      // 3. Sites & Spaces
      {
        path: 'sites-spaces',
        name: 'SitesSpaces',
        children: [
          // 3.1 Site Management
          {
            path: 'site-management',
            name: 'SiteManagement',
            children: [
              {
                path: 'site-profile',
                name: 'SiteProfile',
                component: () => import('@/views/SitesSpaces/SiteManagement/SiteProfile.vue'),
                meta: { title: 'Site Profile' }
              },
              {
                path: 'site-boundary',
                name: 'SiteBoundary',
                component: () => import('@/views/SitesSpaces/SiteManagement/SiteBoundary.vue'),
                meta: { title: 'Site Boundary' }
              },
              {
                path: 'site-contacts',
                name: 'SiteContacts',
                component: () => import('@/views/SitesSpaces/SiteManagement/SiteContacts.vue'),
                meta: { title: 'Site Contacts' }
              },
              {
                path: 'airport',
                name: 'Airport',
                component: () => import('@/views/SitesSpaces/SiteManagement/Airport.vue'),
                meta: { title: 'Site Airport' }
              },
              {
                path: 'building',
                name: 'Building',
                component: () => import('@/views/SitesSpaces/SiteManagement/Building.vue'),
                meta: { title: 'Site Building' }
              },
              {
                path: 'factory',
                name: 'Factory',
                component: () => import('@/views/SitesSpaces/SiteManagement/Factory.vue'),
                meta: { title: 'Site Factory' }
              },
              {
                path: 'hospital',
                name: 'Hospital',
                component: () => import('@/views/SitesSpaces/SiteManagement/Hospital.vue'),
                meta: { title: 'Site Hospital' }
              },
              {
                path: 'hotel',
                name: 'Hotel',
                component: () => import('@/views/SitesSpaces/SiteManagement/Hotel.vue'),
                meta: { title: 'Site Hotel' }
              },
              {
                path: 'shopping',
                name: 'Shopping',
                component: () => import('@/views/SitesSpaces/SiteManagement/Shopping.vue'),
                meta: { title: 'Site Shopping' }
              }
            ]
          },
          // 3.2 Building Management
          {
            path: 'building-management',
            name: 'BuildingManagement',
            component: () => import('@/views/SitesSpaces/BuildingManagement.vue'),
            meta: { title: 'Building Management' }
          },
          // 3.3 Floor Management
          {
            path: 'floor-management',
            name: 'FloorManagement',
            component: () => import('@/views/SitesSpaces/FloorManagement.vue'),
            meta: { title: 'Floor Management' }
          },
          // 3.4 Zone Management
          {
            path: 'zone-management',
            name: 'ZoneManagement',
            component: () => import('@/views/SitesSpaces/ZoneManagement.vue'),
            meta: { title: 'Zone Management' }
          },
          // 3.5 Space Management
          {
            path: 'space-management',
            name: 'SpaceManagement',
            children: [
              {
                path: 'room-area-registry',
                name: 'RoomAreaRegistry',
                component: () => import('@/views/SitesSpaces/SpaceManagement/RoomAreaRegistry.vue'),
                meta: { title: 'Room / Area Registry' }
              },
              {
                path: 'space-type',
                name: 'SpaceType',
                component: () => import('@/views/SitesSpaces/SpaceManagement/SpaceType.vue'),
                meta: { title: 'Space Type' }
              },
              {
                path: 'occupancy-mapping',
                name: 'OccupancyMapping',
                component: () => import('@/views/SitesSpaces/SpaceManagement/OccupancyMapping.vue'),
                meta: { title: 'Occupancy Mapping' }
              }
            ]
          },
          // 3.6 Campus Management
          {
            path: 'campus-management',
            name: 'CampusManagement',
            component: () => import('@/views/SitesSpaces/CampusManagement.vue'),
            meta: { title: 'Campus Management' }
          },
          // 3.7 Multi-Site Management
          {
            path: 'multi-site-management',
            name: 'MultiSiteManagement',
            component: () => import('@/views/SitesSpaces/MultiSiteManagement.vue'),
            meta: { title: 'Multi-Site Management' }
          },
          // 3.8 Data Center Rooms
          {
            path: 'data-center-rooms',
            name: 'DataCenterRooms',
            children: [
              {
                path: 'data-hall',
                name: 'DataHall',
                component: () => import('@/views/SitesSpaces/DataCenterRooms/DataHall.vue'),
                meta: { title: 'Data Hall' }
              },
              {
                path: 'ups-room',
                name: 'UpsRoom',
                component: () => import('@/views/SitesSpaces/DataCenterRooms/UpsRoom.vue'),
                meta: { title: 'UPS Room' }
              },
              {
                path: 'battery-room',
                name: 'BatteryRoom',
                component: () => import('@/views/SitesSpaces/DataCenterRooms/BatteryRoom.vue'),
                meta: { title: 'Battery Room' }
              },
              {
                path: 'network-room',
                name: 'NetworkRoom',
                component: () => import('@/views/SitesSpaces/DataCenterRooms/NetworkRoom.vue'),
                meta: { title: 'Network Room' }
              }
            ]
          },
          // 3.9 White Space Management
          {
            path: 'white-space-management',
            name: 'WhiteSpaceManagement',
            component: () => import('@/views/SitesSpaces/WhiteSpaceManagement.vue'),
            meta: { title: 'White Space Management' }
          },
          // 3.10 Technical Rooms
          {
            path: 'technical-rooms',
            name: 'TechnicalRooms',
            component: () => import('@/views/SitesSpaces/TechnicalRooms.vue'),
            meta: { title: 'Technical Rooms' }
          },
          // 3.11 Capacity Zones
          {
            path: 'capacity-zones',
            name: 'CapacityZones',
            component: () => import('@/views/SitesSpaces/CapacityZones.vue'),
            meta: { title: 'Capacity Zones' }
          }
        ]
      },
      // 4. Systems & Devices
      {
        path: 'systems-devices',
        name: 'SystemsDevices',
        children: [
          // 4.1 Device Inventory
          {
            path: 'device-inventory',
            name: 'DeviceInventory',
            children: [
              {
                path: 'device-list',
                name: 'DeviceList',
                component: () => import('@/views/SystemsDevices/DeviceInventory/DeviceList.vue'),
                meta: { title: 'Device List' }
              },
              {
                path: 'device-details',
                name: 'DeviceDetails',
                component: () => import('@/views/SystemsDevices/DeviceInventory/DeviceDetails.vue'),
                meta: { title: 'Device Details' }
              },
              {
                path: 'device-import',
                name: 'DeviceImport',
                component: () => import('@/views/SystemsDevices/DeviceInventory/DeviceImport.vue'),
                meta: { title: 'Device Import' }
              },
              {
                path: 'device-lifecycle',
                name: 'DeviceLifecycle',
                component: () => import('@/views/SystemsDevices/DeviceInventory/DeviceLifecycle.vue'),
                meta: { title: 'Device Lifecycle' }
              }
            ]
          },
          // 4.2 Device Monitoring
          {
            path: 'device-monitoring',
            name: 'DeviceMonitoring',
            children: [
              {
                path: 'real-time-status',
                name: 'RealTimeStatus',
                component: () => import('@/views/SystemsDevices/DeviceMonitoring/RealTimeStatus.vue'),
                meta: { title: 'Real-Time Status' }
              },
              {
                path: 'telemetry-trends',
                name: 'TelemetryTrends',
                component: () => import('@/views/SystemsDevices/DeviceMonitoring/TelemetryTrends.vue'),
                meta: { title: 'Telemetry Trends' }
              },
              {
                path: 'online-offline',
                name: 'OnlineOffline',
                component: () => import('@/views/SystemsDevices/DeviceMonitoring/OnlineOffline.vue'),
                meta: { title: 'Online / Offline' }
              },
              {
                path: 'device-health',
                name: 'DeviceHealth',
                component: () => import('@/views/SystemsDevices/DeviceMonitoring/DeviceHealth.vue'),
                meta: { title: 'Device Health' }
              }
            ]
          },
          // 4.3 Device Groups
          {
            path: 'device-groups',
            name: 'DeviceGroups',
            component: () => import('@/views/SystemsDevices/DeviceGroups.vue'),
            meta: { title: 'Device Groups' }
          },
          // 4.4 Device Templates
          {
            path: 'device-templates',
            name: 'DeviceTemplates',
            children: [
              {
                path: 'standard-template',
                name: 'StandardTemplate',
                component: () => import('@/views/SystemsDevices/DeviceTemplates/StandardTemplate.vue'),
                meta: { title: 'Standard Template' }
              },
              {
                path: 'vendor-template',
                name: 'VendorTemplate',
                component: () => import('@/views/SystemsDevices/DeviceTemplates/VendorTemplate.vue'),
                meta: { title: 'Vendor Template' }
              },
              {
                path: 'custom-template',
                name: 'CustomTemplate',
                component: () => import('@/views/SystemsDevices/DeviceTemplates/CustomTemplate.vue'),
                meta: { title: 'Custom Template' }
              }
            ]
          },
          // 4.5 Point Management
          {
            path: 'point-management',
            name: 'PointManagement',
            children: [
              {
                path: 'bacnet-points',
                name: 'BacnetPoints',
                component: () => import('@/views/SystemsDevices/PointManagement/BacnetPoints.vue'),
                meta: { title: 'BACnet Points' }
              },
              {
                path: 'modbus-points',
                name: 'ModbusPoints',
                component: () => import('@/views/SystemsDevices/PointManagement/ModbusPoints.vue'),
                meta: { title: 'Modbus Points' }
              },
              {
                path: 'mqtt-points',
                name: 'MqttPoints',
                component: () => import('@/views/SystemsDevices/PointManagement/MqttPoints.vue'),
                meta: { title: 'MQTT Points' }
              },
              {
                path: 'opc-ua-points',
                name: 'OpcUaPoints',
                component: () => import('@/views/SystemsDevices/PointManagement/OpcUaPoints.vue'),
                meta: { title: 'OPC-UA Points' }
              },
              {
                path: 'snmp-points',
                name: 'SnmpPoints',
                component: () => import('@/views/SystemsDevices/PointManagement/SnmpPoints.vue'),
                meta: { title: 'SNMP Points' }
              },
              {
                path: 'virtual-points',
                name: 'VirtualPoints',
                component: () => import('@/views/SystemsDevices/PointManagement/VirtualPoints.vue'),
                meta: { title: 'Virtual Points' }
              },
              {
                path: 'calculated-points',
                name: 'CalculatedPoints',
                component: () => import('@/views/SystemsDevices/PointManagement/CalculatedPoints.vue'),
                meta: { title: 'Calculated Points' }
              }
            ]
          },
          // 4.6 Area Topology
          {
            path: 'area-topology',
            name: 'AreaTopology',
            component: () => import('@/views/SystemsDevices/AreaTopology.vue'),
            meta: { title: 'Area Topology' }
          },
          // 4.7 Asset Tag Management
          {
            path: 'asset-tag-management',
            name: 'AssetTagManagement',
            component: () => import('@/views/SystemsDevices/AssetTagManagement.vue'),
            meta: { title: 'Asset Tag Management' }
          },
          // 4.8 HVAC Systems
          {
            path: 'hvac-systems',
            name: 'HvacSystems',
            children: [
              {
                path: 'chillers',
                name: 'Chillers',
                component: () => import('@/views/SystemsDevices/HvacSystems/Chillers.vue'),
                meta: { title: 'Chillers' }
              },
              {
                path: 'cooling-towers',
                name: 'CoolingTowers',
                component: () => import('@/views/SystemsDevices/HvacSystems/CoolingTowers.vue'),
                meta: { title: 'Cooling Towers' }
              },
              {
                path: 'pumps',
                name: 'Pumps',
                component: () => import('@/views/SystemsDevices/HvacSystems/Pumps.vue'),
                meta: { title: 'Pumps' }
              },
              {
                path: 'ahu',
                name: 'Ahu',
                component: () => import('@/views/SystemsDevices/HvacSystems/Ahu.vue'),
                meta: { title: 'AHU' }
              },
              {
                path: 'fcu',
                name: 'Fcu',
                component: () => import('@/views/SystemsDevices/HvacSystems/Fcu.vue'),
                meta: { title: 'FCU' }
              },
              {
                path: 'vav',
                name: 'Vav',
                component: () => import('@/views/SystemsDevices/HvacSystems/Vav.vue'),
                meta: { title: 'VAV' }
              },
              {
                path: 'ventilation',
                name: 'Ventilation',
                component: () => import('@/views/SystemsDevices/HvacSystems/Ventilation.vue'),
                meta: { title: 'Ventilation' }
              },
              {
                path: 'thermostats',
                name: 'Thermostats',
                component: () => import('@/views/SystemsDevices/HvacSystems/Thermostats.vue'),
                meta: { title: 'Thermostats' }
              }
            ]
          },
          // 4.9 Lighting Systems
          {
            path: 'lighting-systems',
            name: 'LightingSystems',
            children: [
              {
                path: 'lighting-panels',
                name: 'LightingPanels',
                component: () => import('@/views/SystemsDevices/LightingSystems/LightingPanels.vue'),
                meta: { title: 'Lighting Panels' }
              },
              {
                path: 'lighting-circuits',
                name: 'LightingCircuits',
                component: () => import('@/views/SystemsDevices/LightingSystems/LightingCircuits.vue'),
                meta: { title: 'Lighting Circuits' }
              },
              {
                path: 'motion-sensors',
                name: 'MotionSensors',
                component: () => import('@/views/SystemsDevices/LightingSystems/MotionSensors.vue'),
                meta: { title: 'Motion Sensors' }
              },
              {
                path: 'dali-knx-lighting',
                name: 'DaliKnxLighting',
                component: () => import('@/views/SystemsDevices/LightingSystems/DaliKnxLighting.vue'),
                meta: { title: 'DALI/KNX Lighting' }
              }
            ]
          },
          // 4.10 Electrical Systems
          {
            path: 'electrical-systems',
            name: 'ElectricalSystems',
            children: [
              {
                path: 'main-switchboard',
                name: 'MainSwitchboard',
                component: () => import('@/views/SystemsDevices/ElectricalSystems/MainSwitchboard.vue'),
                meta: { title: 'Main Switchboard' }
              },
              {
                path: 'distribution-board',
                name: 'DistributionBoard',
                component: () => import('@/views/SystemsDevices/ElectricalSystems/DistributionBoard.vue'),
                meta: { title: 'Distribution Board' }
              },
              {
                path: 'power-meter',
                name: 'PowerMeter',
                component: () => import('@/views/SystemsDevices/ElectricalSystems/PowerMeter.vue'),
                meta: { title: 'Power Meter' }
              },
              {
                path: 'power-quality',
                name: 'PowerQuality',
                component: () => import('@/views/SystemsDevices/ElectricalSystems/PowerQuality.vue'),
                meta: { title: 'Power Quality' }
              },
              {
                path: 'transformer',
                name: 'Transformer',
                component: () => import('@/views/SystemsDevices/ElectricalSystems/Transformer.vue'),
                meta: { title: 'Transformer' }
              }
            ]
          },
          // 4.11 Plumbing Systems
          {
            path: 'plumbing-systems',
            name: 'PlumbingSystems',
            children: [
              {
                path: 'pumps',
                name: 'PlumbingPumps',
                component: () => import('@/views/SystemsDevices/PlumbingSystems/Pumps.vue'),
                meta: { title: 'Pumps' }
              },
              {
                path: 'tanks',
                name: 'Tanks',
                component: () => import('@/views/SystemsDevices/PlumbingSystems/Tanks.vue'),
                meta: { title: 'Tanks' }
              },
              {
                path: 'valves',
                name: 'Valves',
                component: () => import('@/views/SystemsDevices/PlumbingSystems/Valves.vue'),
                meta: { title: 'Valves' }
              },
              {
                path: 'leak-detection',
                name: 'PlumbingLeakDetection',
                component: () => import('@/views/SystemsDevices/PlumbingSystems/LeakDetection.vue'),
                meta: { title: 'Leak Detection' }
              }
            ]
          },
          // 4.12 Fire Alarm Systems
          {
            path: 'fire-alarm-systems',
            name: 'FireAlarmSystems',
            children: [
              {
                path: 'fire-panel',
                name: 'FirePanel',
                component: () => import('@/views/SystemsDevices/FireAlarmSystems/FirePanel.vue'),
                meta: { title: 'Fire Panel' }
              },
              {
                path: 'smoke-heat-detectors',
                name: 'SmokeHeatDetectors',
                component: () => import('@/views/SystemsDevices/FireAlarmSystems/SmokeHeatDetectors.vue'),
                meta: { title: 'Smoke / Heat Detectors' }
              },
              {
                path: 'fire-pumps',
                name: 'FirePumps',
                component: () => import('@/views/SystemsDevices/FireAlarmSystems/FirePumps.vue'),
                meta: { title: 'Fire Pumps' }
              },
              {
                path: 'fire-impairment-status',
                name: 'FireImpairmentStatus',
                component: () => import('@/views/SystemsDevices/FireAlarmSystems/FireImpairmentStatus.vue'),
                meta: { title: 'Fire Impairment Status' }
              }
            ]
          },
          // 4.13 Security Alarm Systems
          {
            path: 'security-alarm-systems',
            name: 'SecurityAlarmSystems',
            component: () => import('@/views/SystemsDevices/SecurityAlarmSystems.vue'),
            meta: { title: 'Security Alarm Systems' }
          },
          // 4.14 Access Control Systems
          {
            path: 'access-control-systems',
            name: 'AccessControlSystems',
            component: () => import('@/views/SystemsDevices/AccessControlSystems.vue'),
            meta: { title: 'Access Control Systems' }
          },
          // 4.15 CCTV Systems
          {
            path: 'cctv-systems',
            name: 'CctvSystems',
            children: [
              {
                path: 'cameras',
                name: 'Cameras',
                component: () => import('@/views/SystemsDevices/CctvSystems/Cameras.vue'),
                meta: { title: 'Cameras' }
              },
              {
                path: 'nvr-vms',
                name: 'NvrVms',
                component: () => import('@/views/SystemsDevices/CctvSystems/NvrVms.vue'),
                meta: { title: 'NVR / VMS' }
              },
              {
                path: 'recording-status',
                name: 'RecordingStatus',
                component: () => import('@/views/SystemsDevices/CctvSystems/RecordingStatus.vue'),
                meta: { title: 'Recording Status' }
              },
              {
                path: 'video-loss-status',
                name: 'VideoLossStatus',
                component: () => import('@/views/SystemsDevices/CctvSystems/VideoLossStatus.vue'),
                meta: { title: 'Video Loss Status' }
              }
            ]
          },
          // 4.16 EV Charging Systems
          {
            path: 'ev-charging-systems',
            name: 'EvChargingSystems',
            component: () => import('@/views/SystemsDevices/EvChargingSystems.vue'),
            meta: { title: 'EV Charging Systems' }
          },
          // 4.17 Renewable Energy Systems
          {
            path: 'renewable-energy-systems',
            name: 'RenewableEnergySystems',
            component: () => import('@/views/SystemsDevices/RenewableEnergySystems.vue'),
            meta: { title: 'Renewable Energy Systems' }
          },
          // 4.18 Data Center Systems
          {
            path: 'data-center-systems',
            name: 'DataCenterSystems',
            children: [
              {
                path: 'ups-systems',
                name: 'UpsSystems',
                component: () => import('@/views/SystemsDevices/DataCenterSystems/UpsSystems.vue'),
                meta: { title: 'UPS Systems' }
              },
              {
                path: 'pdu-systems',
                name: 'PduSystems',
                component: () => import('@/views/SystemsDevices/DataCenterSystems/PduSystems.vue'),
                meta: { title: 'PDU Systems' }
              },
              {
                path: 'battery-systems',
                name: 'BatterySystems',
                component: () => import('@/views/SystemsDevices/DataCenterSystems/BatterySystems.vue'),
                meta: { title: 'Battery Systems' }
              },
              {
                path: 'generator-systems',
                name: 'GeneratorSystems',
                component: () => import('@/views/SystemsDevices/DataCenterSystems/GeneratorSystems.vue'),
                meta: { title: 'Generator Systems' }
              },
              {
                path: 'crac-systems',
                name: 'CracSystems',
                component: () => import('@/views/SystemsDevices/DataCenterSystems/CracSystems.vue'),
                meta: { title: 'CRAC Systems' }
              },
              {
                path: 'crah-systems',
                name: 'CrahSystems',
                component: () => import('@/views/SystemsDevices/DataCenterSystems/CrahSystems.vue'),
                meta: { title: 'CRAH Systems' }
              },
              {
                path: 'chiller-systems',
                name: 'ChillerSystems',
                component: () => import('@/views/SystemsDevices/DataCenterSystems/ChillerSystems.vue'),
                meta: { title: 'Chiller Systems' }
              },
              {
                path: 'cooling-tower-systems',
                name: 'CoolingTowerSystems',
                component: () => import('@/views/SystemsDevices/DataCenterSystems/CoolingTowerSystems.vue'),
                meta: { title: 'Cooling Tower Systems' }
              },
              {
                path: 'rack-sensors',
                name: 'RackSensors',
                component: () => import('@/views/SystemsDevices/DataCenterSystems/RackSensors.vue'),
                meta: { title: 'Rack Sensors' }
              },
              {
                path: 'environmental-sensors',
                name: 'EnvironmentalSensors',
                component: () => import('@/views/SystemsDevices/DataCenterSystems/EnvironmentalSensors.vue'),
                meta: { title: 'Environmental Sensors' }
              },
              {
                path: 'leak-detection',
                name: 'DcLeakDetection',
                component: () => import('@/views/SystemsDevices/DataCenterSystems/LeakDetection.vue'),
                meta: { title: 'Leak Detection' }
              },
              {
                path: 'network-devices',
                name: 'NetworkDevices',
                component: () => import('@/views/SystemsDevices/DataCenterSystems/NetworkDevices.vue'),
                meta: { title: 'Network Devices' }
              },
              {
                path: 'server-infrastructure',
                name: 'ServerInfrastructure',
                component: () => import('@/views/SystemsDevices/DataCenterSystems/ServerInfrastructure.vue'),
                meta: { title: 'Server Infrastructure' }
              }
            ]
          }
        ]
      },
      // 5. Alarms & Events
      {
        path: 'alarms-events',
        name: 'AlarmsEvents',
        children: [
          // 5.1 Live Alarms
          {
            path: 'live-alarms',
            name: 'LiveAlarms',
            children: [
              {
                path: 'critical-alarms',
                name: 'CriticalAlarms',
                component: () => import('@/views/AlarmsEvents/LiveAlarms/CriticalAlarms.vue'),
                meta: { title: 'Critical Alarms' }
              },
              {
                path: 'major-alarms',
                name: 'MajorAlarms',
                component: () => import('@/views/AlarmsEvents/LiveAlarms/MajorAlarms.vue'),
                meta: { title: 'Major Alarms' }
              },
              {
                path: 'warning-alarms',
                name: 'WarningAlarms',
                component: () => import('@/views/AlarmsEvents/LiveAlarms/WarningAlarms.vue'),
                meta: { title: 'Warning Alarms' }
              },
              {
                path: 'information-events',
                name: 'InformationEvents',
                component: () => import('@/views/AlarmsEvents/LiveAlarms/InformationEvents.vue'),
                meta: { title: 'Information Events' }
              }
            ]
          },
          // 5.2 Alarm History
          {
            path: 'alarm-history',
            name: 'AlarmHistory',
            component: () => import('@/views/AlarmsEvents/AlarmHistory.vue'),
            meta: { title: 'Alarm History' }
          },
          // 5.3 Alarm Rules
          {
            path: 'alarm-rules',
            name: 'AlarmRules',
            children: [
              {
                path: 'threshold-rules',
                name: 'ThresholdRules',
                component: () => import('@/views/AlarmsEvents/AlarmRules/ThresholdRules.vue'),
                meta: { title: 'Threshold Rules' }
              },
              {
                path: 'status-rules',
                name: 'StatusRules',
                component: () => import('@/views/AlarmsEvents/AlarmRules/StatusRules.vue'),
                meta: { title: 'Status Rules' }
              },
              {
                path: 'time-delay-rules',
                name: 'TimeDelayRules',
                component: () => import('@/views/AlarmsEvents/AlarmRules/TimeDelayRules.vue'),
                meta: { title: 'Time Delay Rules' }
              },
              {
                path: 'composite-rules',
                name: 'CompositeRules',
                component: () => import('@/views/AlarmsEvents/AlarmRules/CompositeRules.vue'),
                meta: { title: 'Composite Rules' }
              }
            ]
          },
          // 5.4 Alarm Correlation
          {
            path: 'alarm-correlation',
            name: 'AlarmCorrelation',
            component: () => import('@/views/AlarmsEvents/AlarmCorrelation.vue'),
            meta: { title: 'Alarm Correlation' }
          },
          // 5.5 Escalation Rules
          {
            path: 'escalation-rules',
            name: 'EscalationRules',
            component: () => import('@/views/AlarmsEvents/EscalationRules.vue'),
            meta: { title: 'Escalation Rules' }
          },
          // 5.6 Notification Center
          {
            path: 'notification-center',
            name: 'NotificationCenter',
            component: () => import('@/views/AlarmsEvents/NotificationCenter.vue'),
            meta: { title: 'Notification Center' }
          },
          // 5.7 Event Analytics
          {
            path: 'event-analytics',
            name: 'EventAnalytics',
            component: () => import('@/views/AlarmsEvents/EventAnalytics.vue'),
            meta: { title: 'Event Analytics' }
          },
          // 5.8 Data Center Alarms
          {
            path: 'data-center-alarms',
            name: 'DataCenterAlarms',
            children: [
              {
                path: 'ups-alarms',
                name: 'UpsAlarms',
                component: () => import('@/views/AlarmsEvents/DataCenterAlarms/UpsAlarms.vue'),
                meta: { title: 'UPS Alarms' }
              },
              {
                path: 'battery-alarms',
                name: 'BatteryAlarms',
                component: () => import('@/views/AlarmsEvents/DataCenterAlarms/BatteryAlarms.vue'),
                meta: { title: 'Battery Alarms' }
              },
              {
                path: 'cooling-alarms',
                name: 'CoolingAlarms',
                component: () => import('@/views/AlarmsEvents/DataCenterAlarms/CoolingAlarms.vue'),
                meta: { title: 'Cooling Alarms' }
              },
              {
                path: 'environmental-alarms',
                name: 'EnvironmentalAlarms',
                component: () => import('@/views/AlarmsEvents/DataCenterAlarms/EnvironmentalAlarms.vue'),
                meta: { title: 'Environmental Alarms' }
              },
              {
                path: 'rack-alarms',
                name: 'RackAlarms',
                component: () => import('@/views/AlarmsEvents/DataCenterAlarms/RackAlarms.vue'),
                meta: { title: 'Rack Alarms' }
              }
            ]
          },
          // 5.9 Alarm SLA
          {
            path: 'alarm-sla',
            name: 'AlarmSla',
            component: () => import('@/views/AlarmsEvents/AlarmSla.vue'),
            meta: { title: 'Alarm SLA' }
          }
        ]
      },
      // 6. Fault Management System (FMS)
      {
        path: 'fault-management-system',
        name: 'FaultManagementSystem',
        children: [
          // 6.1 Fault Dashboard
          {
            path: 'fault-dashboard',
            name: 'FaultDashboard',
            component: () => import('@/views/FaultManagementSystem/FaultDashboard.vue'),
            meta: { title: 'Fault Dashboard' }
          },
          // 6.2 Active Faults
          {
            path: 'active-faults',
            name: 'ActiveFaults',
            component: () => import('@/views/FaultManagementSystem/ActiveFaults.vue'),
            meta: { title: 'Active Faults' }
          },
          // 6.3 Fault History
          {
            path: 'fault-history',
            name: 'FaultHistory',
            component: () => import('@/views/FaultManagementSystem/FaultHistory.vue'),
            meta: { title: 'Fault History' }
          },
          // 6.4 Fault Correlation
          {
            path: 'fault-correlation',
            name: 'FaultCorrelation',
            component: () => import('@/views/FaultManagementSystem/FaultCorrelation.vue'),
            meta: { title: 'Fault Correlation' }
          },
          // 6.5 Root Cause Analysis
          {
            path: 'root-cause-analysis',
            name: 'RootCauseAnalysis',
            children: [
              {
                path: 'rule-based-rca',
                name: 'RuleBasedRca',
                component: () => import('@/views/FaultManagementSystem/RootCauseAnalysis/RuleBasedRca.vue'),
                meta: { title: 'Rule-Based RCA' }
              },
              {
                path: 'historical-similarity',
                name: 'HistoricalSimilarity',
                component: () => import('@/views/FaultManagementSystem/RootCauseAnalysis/HistoricalSimilarity.vue'),
                meta: { title: 'Historical Similarity' }
              },
              {
                path: 'ai-rca',
                name: 'AiRca',
                component: () => import('@/views/FaultManagementSystem/RootCauseAnalysis/AiRca.vue'),
                meta: { title: 'AI RCA' }
              },
              {
                path: 'evidence-link',
                name: 'EvidenceLink',
                component: () => import('@/views/FaultManagementSystem/RootCauseAnalysis/EvidenceLink.vue'),
                meta: { title: 'Evidence Link' }
              }
            ]
          },
          // 6.6 Fault Rules Engine
          {
            path: 'fault-rules-engine',
            name: 'FaultRulesEngine',
            component: () => import('@/views/FaultManagementSystem/FaultRulesEngine.vue'),
            meta: { title: 'Fault Rules Engine' }
          },
          // 6.7 Fault Workflow
          {
            path: 'fault-workflow',
            name: 'FaultWorkflow',
            children: [
              {
                path: 'new',
                name: 'FaultNew',
                component: () => import('@/views/FaultManagementSystem/FaultWorkflow/New.vue'),
                meta: { title: 'New' }
              },
              {
                path: 'assigned',
                name: 'FaultAssigned',
                component: () => import('@/views/FaultManagementSystem/FaultWorkflow/Assigned.vue'),
                meta: { title: 'Assigned' }
              },
              {
                path: 'investigating',
                name: 'FaultInvestigating',
                component: () => import('@/views/FaultManagementSystem/FaultWorkflow/Investigating.vue'),
                meta: { title: 'Investigating' }
              },
              {
                path: 'resolved',
                name: 'FaultResolved',
                component: () => import('@/views/FaultManagementSystem/FaultWorkflow/Resolved.vue'),
                meta: { title: 'Resolved' }
              },
              {
                path: 'closed',
                name: 'FaultClosed',
                component: () => import('@/views/FaultManagementSystem/FaultWorkflow/Closed.vue'),
                meta: { title: 'Closed' }
              }
            ]
          },
          // 6.8 Fault Analytics
          {
            path: 'fault-analytics',
            name: 'FaultAnalytics',
            component: () => import('@/views/FaultManagementSystem/FaultAnalytics.vue'),
            meta: { title: 'Fault Analytics' }
          },
          // 6.9 Knowledge Base
          {
            path: 'knowledge-base',
            name: 'KnowledgeBase',
            component: () => import('@/views/FaultManagementSystem/KnowledgeBase.vue'),
            meta: { title: 'Knowledge Base' }
          },
          // 6.10 Data Center Faults
          {
            path: 'data-center-faults',
            name: 'DataCenterFaults',
            children: [
              {
                path: 'ups-faults',
                name: 'UpsFaults',
                component: () => import('@/views/FaultManagementSystem/DataCenterFaults/UpsFaults.vue'),
                meta: { title: 'UPS Faults' }
              },
              {
                path: 'battery-faults',
                name: 'BatteryFaults',
                component: () => import('@/views/FaultManagementSystem/DataCenterFaults/BatteryFaults.vue'),
                meta: { title: 'Battery Faults' }
              },
              {
                path: 'cooling-faults',
                name: 'CoolingFaults',
                component: () => import('@/views/FaultManagementSystem/DataCenterFaults/CoolingFaults.vue'),
                meta: { title: 'Cooling Faults' }
              },
              {
                path: 'power-chain-faults',
                name: 'PowerChainFaults',
                component: () => import('@/views/FaultManagementSystem/DataCenterFaults/PowerChainFaults.vue'),
                meta: { title: 'Power Chain Faults' }
              },
              {
                path: 'rack-faults',
                name: 'RackFaults',
                component: () => import('@/views/FaultManagementSystem/DataCenterFaults/RackFaults.vue'),
                meta: { title: 'Rack Faults' }
              },
              {
                path: 'network-faults',
                name: 'NetworkFaults',
                component: () => import('@/views/FaultManagementSystem/DataCenterFaults/NetworkFaults.vue'),
                meta: { title: 'Network Faults' }
              }
            ]
          },
          // 6.11 Fault KPI
          {
            path: 'fault-kpi',
            name: 'FaultKpi',
            children: [
              {
                path: 'mtbf',
                name: 'Mtbf',
                component: () => import('@/views/FaultManagementSystem/FaultKpi/Mtbf.vue'),
                meta: { title: 'MTBF' }
              },
              {
                path: 'mttr',
                name: 'Mttr',
                component: () => import('@/views/FaultManagementSystem/FaultKpi/Mttr.vue'),
                meta: { title: 'MTTR' }
              },
              {
                path: 'failure-rate',
                name: 'FailureRate',
                component: () => import('@/views/FaultManagementSystem/FaultKpi/FailureRate.vue'),
                meta: { title: 'Failure Rate' }
              },
              {
                path: 'top-fault-assets',
                name: 'TopFaultAssets',
                component: () => import('@/views/FaultManagementSystem/FaultKpi/TopFaultAssets.vue'),
                meta: { title: 'Top Fault Assets' }
              }
            ]
          },
          // 6.12 AI Fault Diagnosis
          {
            path: 'ai-fault-diagnosis',
            name: 'AiFaultDiagnosis',
            component: () => import('@/views/FaultManagementSystem/AiFaultDiagnosis.vue'),
            meta: { title: 'AI Fault Diagnosis' }
          }
        ]
      },
      // 7. Maintenance
      {
        path: 'maintenance',
        name: 'Maintenance',
        children: [
          // 7.1 Work Orders
          {
            path: 'work-orders',
            name: 'WorkOrders',
            children: [
              {
                path: 'corrective',
                name: 'Corrective',
                component: () => import('@/views/Maintenance/WorkOrders/Corrective.vue'),
                meta: { title: 'Corrective' }
              },
              {
                path: 'preventive',
                name: 'Preventive',
                component: () => import('@/views/Maintenance/WorkOrders/Preventive.vue'),
                meta: { title: 'Preventive' }
              },
              {
                path: 'predictive',
                name: 'Predictive',
                component: () => import('@/views/Maintenance/WorkOrders/Predictive.vue'),
                meta: { title: 'Predictive' }
              },
              {
                path: 'emergency',
                name: 'Emergency',
                component: () => import('@/views/Maintenance/WorkOrders/Emergency.vue'),
                meta: { title: 'Emergency' }
              }
            ]
          },
          // 7.2 Dispatch Management
          {
            path: 'dispatch-management',
            name: 'DispatchManagement',
            children: [
              {
                path: 'assignment',
                name: 'Assignment',
                component: () => import('@/views/Maintenance/DispatchManagement/Assignment.vue'),
                meta: { title: 'Assignment' }
              },
              {
                path: 'engineer-schedule',
                name: 'EngineerSchedule',
                component: () => import('@/views/Maintenance/DispatchManagement/EngineerSchedule.vue'),
                meta: { title: 'Engineer Schedule' }
              },
              {
                path: 'mobile-dispatch',
                name: 'MobileDispatch',
                component: () => import('@/views/Maintenance/DispatchManagement/MobileDispatch.vue'),
                meta: { title: 'Mobile Dispatch' }
              }
            ]
          },
          // 7.3 Inspection Management
          {
            path: 'inspection-management',
            name: 'InspectionManagement',
            children: [
              {
                path: 'inspection-plan',
                name: 'InspectionPlan',
                component: () => import('@/views/Maintenance/InspectionManagement/InspectionPlan.vue'),
                meta: { title: 'Inspection Plan' }
              },
              {
                path: 'inspection-checklist',
                name: 'InspectionChecklist',
                component: () => import('@/views/Maintenance/InspectionManagement/InspectionChecklist.vue'),
                meta: { title: 'Inspection Checklist' }
              },
              {
                path: 'inspection-result',
                name: 'InspectionResult',
                component: () => import('@/views/Maintenance/InspectionManagement/InspectionResult.vue'),
                meta: { title: 'Inspection Result' }
              }
            ]
          },
          // 7.4 Preventive Maintenance
          {
            path: 'preventive-maintenance',
            name: 'PreventiveMaintenance',
            component: () => import('@/views/Maintenance/PreventiveMaintenance.vue'),
            meta: { title: 'Preventive Maintenance' }
          },
          // 7.5 Predictive Maintenance
          {
            path: 'predictive-maintenance',
            name: 'PredictiveMaintenance',
            component: () => import('@/views/Maintenance/PredictiveMaintenance.vue'),
            meta: { title: 'Predictive Maintenance' }
          },
          // 7.6 Asset Management
          {
            path: 'asset-management',
            name: 'AssetManagement',
            children: [
              {
                path: 'asset-register',
                name: 'AssetRegister',
                component: () => import('@/views/Maintenance/AssetManagement/AssetRegister.vue'),
                meta: { title: 'Asset Register' }
              },
              {
                path: 'asset-health',
                name: 'AssetHealth',
                component: () => import('@/views/Maintenance/AssetManagement/AssetHealth.vue'),
                meta: { title: 'Asset Health' }
              },
              {
                path: 'lifecycle-tracking',
                name: 'LifecycleTracking',
                component: () => import('@/views/Maintenance/AssetManagement/LifecycleTracking.vue'),
                meta: { title: 'Lifecycle Tracking' }
              },
              {
                path: 'replacement-planning',
                name: 'ReplacementPlanning',
                component: () => import('@/views/Maintenance/AssetManagement/ReplacementPlanning.vue'),
                meta: { title: 'Replacement Planning' }
              }
            ]
          },
          // 7.7 Spare Parts Management
          {
            path: 'spare-parts-management',
            name: 'SparePartsManagement',
            component: () => import('@/views/Maintenance/SparePartsManagement.vue'),
            meta: { title: 'Spare Parts Management' }
          },
          // 7.8 Vendor Management
          {
            path: 'vendor-management',
            name: 'VendorManagement',
            component: () => import('@/views/Maintenance/VendorManagement.vue'),
            meta: { title: 'Vendor Management' }
          },
          // 7.9 Contract Management
          {
            path: 'contract-management',
            name: 'ContractManagement',
            component: () => import('@/views/Maintenance/ContractManagement.vue'),
            meta: { title: 'Contract Management' }
          },
          // 7.10 SLA Management
          {
            path: 'sla-management',
            name: 'SlaManagement',
            component: () => import('@/views/Maintenance/SlaManagement.vue'),
            meta: { title: 'SLA Management' }
          },
          // 7.11 Maintenance Analytics
          {
            path: 'maintenance-analytics',
            name: 'MaintenanceAnalytics',
            component: () => import('@/views/Maintenance/MaintenanceAnalytics.vue'),
            meta: { title: 'Maintenance Analytics' }
          },
          // 7.12 Data Center Maintenance
          {
            path: 'data-center-maintenance',
            name: 'DataCenterMaintenance',
            children: [
              {
                path: 'ups-maintenance',
                name: 'UpsMaintenance',
                component: () => import('@/views/Maintenance/DataCenterMaintenance/UpsMaintenance.vue'),
                meta: { title: 'UPS Maintenance' }
              },
              {
                path: 'battery-maintenance',
                name: 'BatteryMaintenance',
                component: () => import('@/views/Maintenance/DataCenterMaintenance/BatteryMaintenance.vue'),
                meta: { title: 'Battery Maintenance' }
              },
              {
                path: 'cooling-maintenance',
                name: 'CoolingMaintenance',
                component: () => import('@/views/Maintenance/DataCenterMaintenance/CoolingMaintenance.vue'),
                meta: { title: 'Cooling Maintenance' }
              },
              {
                path: 'rack-maintenance',
                name: 'RackMaintenance',
                component: () => import('@/views/Maintenance/DataCenterMaintenance/RackMaintenance.vue'),
                meta: { title: 'Rack Maintenance' }
              },
              {
                path: 'generator-maintenance',
                name: 'GeneratorMaintenance',
                component: () => import('@/views/Maintenance/DataCenterMaintenance/GeneratorMaintenance.vue'),
                meta: { title: 'Generator Maintenance' }
              }
            ]
          }
        ]
      },
      // 8. Asset Intelligence
      {
        path: 'asset-intelligence',
        name: 'AssetIntelligence',
        children: [
          // 8.1 Asset Register
          {
            path: 'asset-register',
            name: 'AssetRegisterIntelligence',
            component: () => import('@/views/AssetIntelligence/AssetRegister.vue'),
            meta: { title: 'Asset Register' }
          },
          // 8.2 Asset Health Index
          {
            path: 'asset-health-index',
            name: 'AssetHealthIndex',
            component: () => import('@/views/AssetIntelligence/AssetHealthIndex.vue'),
            meta: { title: 'Asset Health Index' }
          },
          // 8.3 Asset Criticality
          {
            path: 'asset-criticality',
            name: 'AssetCriticality',
            component: () => import('@/views/AssetIntelligence/AssetCriticality.vue'),
            meta: { title: 'Asset Criticality' }
          },
          // 8.4 Asset Risk Matrix
          {
            path: 'asset-risk-matrix',
            name: 'AssetRiskMatrix',
            component: () => import('@/views/AssetIntelligence/AssetRiskMatrix.vue'),
            meta: { title: 'Asset Risk Matrix' }
          },
          // 8.5 Lifecycle Management
          {
            path: 'lifecycle-management',
            name: 'LifecycleManagement',
            component: () => import('@/views/AssetIntelligence/LifecycleManagement.vue'),
            meta: { title: 'Lifecycle Management' }
          },
          // 8.6 Replacement Planning
          {
            path: 'replacement-planning',
            name: 'ReplacementPlanningAsset',
            component: () => import('@/views/AssetIntelligence/ReplacementPlanning.vue'),
            meta: { title: 'Replacement Planning' }
          },
          // 8.7 CAPEX Planning
          {
            path: 'capex-planning',
            name: 'CapexPlanning',
            component: () => import('@/views/AssetIntelligence/CapexPlanning.vue'),
            meta: { title: 'CAPEX Planning' }
          },
          // 8.8 Asset Benchmark
          {
            path: 'asset-benchmark',
            name: 'AssetBenchmark',
            component: () => import('@/views/AssetIntelligence/AssetBenchmark.vue'),
            meta: { title: 'Asset Benchmark' }
          },
          // 8.9 Asset Analytics
          {
            path: 'asset-analytics',
            name: 'AssetAnalytics',
            component: () => import('@/views/AssetIntelligence/AssetAnalytics.vue'),
            meta: { title: 'Asset Analytics' }
          }
        ]
      },
      // 9. Energy & Sustainability
      {
        path: 'energy-sustainability',
        name: 'EnergySustainability',
        children: [
          // 9.1 Electricity Monitoring
          {
            path: 'electricity-monitoring',
            name: 'ElectricityMonitoring',
            component: () => import('@/views/EnergySustainability/ElectricityMonitoring.vue'),
            meta: { title: 'Electricity Monitoring' }
          },
          // 9.2 Water Monitoring
          {
            path: 'water-monitoring',
            name: 'WaterMonitoring',
            component: () => import('@/views/EnergySustainability/WaterMonitoring.vue'),
            meta: { title: 'Water Monitoring' }
          },
          // 9.3 Gas Monitoring
          {
            path: 'gas-monitoring',
            name: 'GasMonitoring',
            component: () => import('@/views/EnergySustainability/GasMonitoring.vue'),
            meta: { title: 'Gas Monitoring' }
          },
          // 9.4 Thermal Energy Monitoring
          {
            path: 'thermal-energy-monitoring',
            name: 'ThermalEnergyMonitoring',
            component: () => import('@/views/EnergySustainability/ThermalEnergyMonitoring.vue'),
            meta: { title: 'Thermal Energy Monitoring' }
          },
          // 9.5 Solar Monitoring
          {
            path: 'solar-monitoring',
            name: 'SolarMonitoring',
            component: () => import('@/views/EnergySustainability/SolarMonitoring.vue'),
            meta: { title: 'Solar Monitoring' }
          },
          // 9.6 Battery Storage
          {
            path: 'battery-storage',
            name: 'BatteryStorage',
            component: () => import('@/views/EnergySustainability/BatteryStorage.vue'),
            meta: { title: 'Battery Storage' }
          },
          // 9.7 Utility Billing
          {
            path: 'utility-billing',
            name: 'UtilityBilling',
            component: () => import('@/views/EnergySustainability/UtilityBilling.vue'),
            meta: { title: 'Utility Billing' }
          },
          // 9.8 Energy Analytics
          {
            path: 'energy-analytics',
            name: 'EnergyAnalytics',
            children: [
              {
                path: 'consumption-analysis',
                name: 'ConsumptionAnalysis',
                component: () => import('@/views/EnergySustainability/EnergyAnalytics/ConsumptionAnalysis.vue'),
                meta: { title: 'Consumption Analysis' }
              },
              {
                path: 'peak-demand',
                name: 'PeakDemand',
                component: () => import('@/views/EnergySustainability/EnergyAnalytics/PeakDemand.vue'),
                meta: { title: 'Peak Demand' }
              },
              {
                path: 'benchmark-analysis',
                name: 'BenchmarkAnalysis',
                component: () => import('@/views/EnergySustainability/EnergyAnalytics/BenchmarkAnalysis.vue'),
                meta: { title: 'Benchmark Analysis' }
              },
              {
                path: 'savings-opportunities',
                name: 'SavingsOpportunities',
                component: () => import('@/views/EnergySustainability/EnergyAnalytics/SavingsOpportunities.vue'),
                meta: { title: 'Savings Opportunities' }
              }
            ]
          },
          // 9.9 Carbon Analytics
          {
            path: 'carbon-analytics',
            name: 'CarbonAnalytics',
            children: [
              {
                path: 'scope-1',
                name: 'Scope1',
                component: () => import('@/views/EnergySustainability/CarbonAnalytics/Scope1.vue'),
                meta: { title: 'Scope 1' }
              },
              {
                path: 'scope-2',
                name: 'Scope2',
                component: () => import('@/views/EnergySustainability/CarbonAnalytics/Scope2.vue'),
                meta: { title: 'Scope 2' }
              },
              {
                path: 'scope-3',
                name: 'Scope3',
                component: () => import('@/views/EnergySustainability/CarbonAnalytics/Scope3.vue'),
                meta: { title: 'Scope 3' }
              },
              {
                path: 'carbon-intensity',
                name: 'CarbonIntensity',
                component: () => import('@/views/EnergySustainability/CarbonAnalytics/CarbonIntensity.vue'),
                meta: { title: 'Carbon Intensity' }
              }
            ]
          },
          // 9.10 ESG Dashboard
          {
            path: 'esg-dashboard',
            name: 'EsgDashboard',
            component: () => import('@/views/EnergySustainability/EsgDashboard.vue'),
            meta: { title: 'ESG Dashboard' }
          },
          // 9.11 Green Finance Metrics
          {
            path: 'green-finance-metrics',
            name: 'GreenFinanceMetrics',
            component: () => import('@/views/EnergySustainability/GreenFinanceMetrics.vue'),
            meta: { title: 'Green Finance Metrics' }
          },
          // 9.12 Data Center Energy
          {
            path: 'data-center-energy',
            name: 'DataCenterEnergy',
            children: [
              {
                path: 'pue-analytics',
                name: 'PueAnalytics',
                component: () => import('@/views/EnergySustainability/DataCenterEnergy/PueAnalytics.vue'),
                meta: { title: 'PUE Analytics' }
              },
              {
                path: 'cue-analytics',
                name: 'CueAnalytics',
                component: () => import('@/views/EnergySustainability/DataCenterEnergy/CueAnalytics.vue'),
                meta: { title: 'CUE Analytics' }
              },
              {
                path: 'wue-analytics',
                name: 'WueAnalytics',
                component: () => import('@/views/EnergySustainability/DataCenterEnergy/WueAnalytics.vue'),
                meta: { title: 'WUE Analytics' }
              },
              {
                path: 'cooling-efficiency',
                name: 'CoolingEfficiency',
                component: () => import('@/views/EnergySustainability/DataCenterEnergy/CoolingEfficiency.vue'),
                meta: { title: 'Cooling Efficiency' }
              },
              {
                path: 'power-utilization',
                name: 'PowerUtilization',
                component: () => import('@/views/EnergySustainability/DataCenterEnergy/PowerUtilization.vue'),
                meta: { title: 'Power Utilization' }
              },
              {
                path: 'renewable-energy-ratio',
                name: 'RenewableEnergyRatio',
                component: () => import('@/views/EnergySustainability/DataCenterEnergy/RenewableEnergyRatio.vue'),
                meta: { title: 'Renewable Energy Ratio' }
              },
              {
                path: 'benchmark-comparison',
                name: 'BenchmarkComparison',
                component: () => import('@/views/EnergySustainability/DataCenterEnergy/BenchmarkComparison.vue'),
                meta: { title: 'Benchmark Comparison' }
              }
            ]
          },
          // 9.13 Sustainability Reporting
          {
            path: 'sustainability-reporting',
            name: 'SustainabilityReporting',
            children: [
              {
                path: 'esg-reports',
                name: 'EsgReports',
                component: () => import('@/views/EnergySustainability/SustainabilityReporting/EsgReports.vue'),
                meta: { title: 'ESG Reports' }
              },
              {
                path: 'carbon-reports',
                name: 'CarbonReports',
                component: () => import('@/views/EnergySustainability/SustainabilityReporting/CarbonReports.vue'),
                meta: { title: 'Carbon Reports' }
              },
              {
                path: 'energy-reports',
                name: 'EnergyReports',
                component: () => import('@/views/EnergySustainability/SustainabilityReporting/EnergyReports.vue'),
                meta: { title: 'Energy Reports' }
              },
              {
                path: 'green-finance-evidence',
                name: 'GreenFinanceEvidence',
                component: () => import('@/views/EnergySustainability/SustainabilityReporting/GreenFinanceEvidence.vue'),
                meta: { title: 'Green Finance Evidence' }
              }
            ]
          }
        ]
      },
      // 10. Facility Services
      {
        path: 'facility-services',
        name: 'FacilityServices',
        children: [
          // 10.1 Parking Management
          {
            path: 'parking-management',
            name: 'ParkingManagement',
            children: [
              {
                path: 'parking-dashboard',
                name: 'ParkingDashboard',
                component: () => import('@/views/FacilityServices/ParkingManagement/ParkingDashboard.vue'),
                meta: { title: 'Parking Dashboard' }
              },
              {
                path: 'parking-space-status',
                name: 'ParkingSpaceStatus',
                component: () => import('@/views/FacilityServices/ParkingManagement/ParkingSpaceStatus.vue'),
                meta: { title: 'Parking Space Status' }
              },
              {
                path: 'anpr-records',
                name: 'AnprRecords',
                component: () => import('@/views/FacilityServices/ParkingManagement/AnprRecords.vue'),
                meta: { title: 'ANPR Records' }
              },
              {
                path: 'parking-violation',
                name: 'ParkingViolation',
                component: () => import('@/views/FacilityServices/ParkingManagement/ParkingViolation.vue'),
                meta: { title: 'Parking Violation' }
              },
              {
                path: 'parking-reports',
                name: 'ParkingReports',
                component: () => import('@/views/FacilityServices/ParkingManagement/ParkingReports.vue'),
                meta: { title: 'Parking Reports' }
              }
            ]
          },
          // 10.2 Visitor Management
          {
            path: 'visitor-management',
            name: 'VisitorManagement',
            component: () => import('@/views/FacilityServices/VisitorManagement.vue'),
            meta: { title: 'Visitor Management' }
          },
          // 10.3 Meeting Room Booking
          {
            path: 'meeting-room-booking',
            name: 'MeetingRoomBooking',
            component: () => import('@/views/FacilityServices/MeetingRoomBooking.vue'),
            meta: { title: 'Meeting Room Booking' }
          },
          // 10.4 Housekeeping Management
          {
            path: 'housekeeping-management',
            name: 'HousekeepingManagement',
            children: [
              {
                path: 'cleaning-task',
                name: 'CleaningTask',
                component: () => import('@/views/FacilityServices/HousekeepingManagement/CleaningTask.vue'),
                meta: { title: 'Cleaning Task' }
              },
              {
                path: 'smart-toilet-monitoring',
                name: 'SmartToiletMonitoring',
                component: () => import('@/views/FacilityServices/HousekeepingManagement/SmartToiletMonitoring.vue'),
                meta: { title: 'Smart Toilet Monitoring' }
              },
              {
                path: 'odor-occupancy-consumables',
                name: 'OdorOccupancyConsumables',
                component: () => import('@/views/FacilityServices/HousekeepingManagement/OdorOccupancyConsumables.vue'),
                meta: { title: 'Odor / Occupancy / Consumables' }
              },
              {
                path: 'cleaning-reports',
                name: 'CleaningReports',
                component: () => import('@/views/FacilityServices/HousekeepingManagement/CleaningReports.vue'),
                meta: { title: 'Cleaning Reports' }
              }
            ]
          },
          // 10.5 Waste Management
          {
            path: 'waste-management',
            name: 'WasteManagement',
            component: () => import('@/views/FacilityServices/WasteManagement.vue'),
            meta: { title: 'Waste Management' }
          },
          // 10.6 Occupancy Analytics
          {
            path: 'occupancy-analytics',
            name: 'OccupancyAnalytics',
            component: () => import('@/views/FacilityServices/OccupancyAnalytics.vue'),
            meta: { title: 'Occupancy Analytics' }
          },
          // 10.7 Facility Requests
          {
            path: 'facility-requests',
            name: 'FacilityRequests',
            component: () => import('@/views/FacilityServices/FacilityRequests.vue'),
            meta: { title: 'Facility Requests' }
          },
          // 10.8 Service Desk
          {
            path: 'service-desk',
            name: 'ServiceDesk',
            component: () => import('@/views/FacilityServices/ServiceDesk.vue'),
            meta: { title: 'Service Desk' }
          }
        ]
      },
      // 11. Data Center Operations (DCIM)
      {
        path: 'data-center-operations',
        name: 'DataCenterOperations',
        children: [
          // 11.1 Introduction
          {
            path: 'introduction',
            name: 'Introduction',
            children: [
              {
                path: 'industry-benchmark',
                name: 'IndustryBenchmark',
                component: () => import('@/views/DataCenterOperations/Introduction/IndustryBenchmark.vue'),
                meta: { title: 'Industry Benchmark' }
              },
              {
                path: 'esg-compliance-overview',
                name: 'EsgComplianceOverview',
                component: () => import('@/views/DataCenterOperations/Introduction/EsgComplianceOverview.vue'),
                meta: { title: 'ESG Compliance Overview' }
              },
              {
                path: 'optimization-potential',
                name: 'OptimizationPotential',
                component: () => import('@/views/DataCenterOperations/Introduction/OptimizationPotential.vue'),
                meta: { title: 'Optimization Potential' }
              },
              {
                path: 'roi-calculator',
                name: 'RoiCalculator',
                component: () => import('@/views/DataCenterOperations/Introduction/RoiCalculator.vue'),
                meta: { title: 'ROI Calculator' }
              },
              {
                path: 'executive-summary',
                name: 'ExecutiveSummary',
                component: () => import('@/views/DataCenterOperations/Introduction/ExecutiveSummary.vue'),
                meta: { title: 'Executive Summary' }
              }
            ]
          },
          // 11.2 Data Center Dashboard
          {
            path: 'data-center-dashboard',
            name: 'DataCenterDashboard',
            component: () => import('@/views/DataCenterOperations/DataCenterDashboard.vue'),
            meta: { title: 'Data Center Dashboard' }
          },
          // 11.3 ESG Compliance Center
          {
            path: 'esg-compliance-center',
            name: 'EsgComplianceCenter',
            children: [
              {
                path: 'ifrs-s2',
                name: 'IfrsS2',
                component: () => import('@/views/DataCenterOperations/EsgComplianceCenter/IfrsS2.vue'),
                meta: { title: 'IFRS S2' }
              },
              {
                path: 'issb',
                name: 'Issb',
                component: () => import('@/views/DataCenterOperations/EsgComplianceCenter/Issb.vue'),
                meta: { title: 'ISSB' }
              },
              {
                path: 'gri',
                name: 'Gri',
                component: () => import('@/views/DataCenterOperations/EsgComplianceCenter/Gri.vue'),
                meta: { title: 'GRI' }
              },
              {
                path: 'tcfd',
                name: 'Tcfd',
                component: () => import('@/views/DataCenterOperations/EsgComplianceCenter/Tcfd.vue'),
                meta: { title: 'TCFD' }
              },
              {
                path: 'csrd',
                name: 'Csrd',
                component: () => import('@/views/DataCenterOperations/EsgComplianceCenter/Csrd.vue'),
                meta: { title: 'CSRD' }
              },
              {
                path: 'sgx-hkex-mas',
                name: 'SgxHkexMas',
                component: () => import('@/views/DataCenterOperations/EsgComplianceCenter/SgxHkexMas.vue'),
                meta: { title: 'SGX / HKEX / MAS' }
              },
              {
                path: 'gap-analysis',
                name: 'GapAnalysis',
                component: () => import('@/views/DataCenterOperations/EsgComplianceCenter/GapAnalysis.vue'),
                meta: { title: 'Gap Analysis' }
              },
              {
                path: 'compliance-roadmap',
                name: 'ComplianceRoadmap',
                component: () => import('@/views/DataCenterOperations/EsgComplianceCenter/ComplianceRoadmap.vue'),
                meta: { title: 'Compliance Roadmap' }
              }
            ]
          },
          // 11.4 Cooling Optimization
          {
            path: 'cooling-optimization',
            name: 'CoolingOptimization',
            children: [
              {
                path: 'chiller-optimization',
                name: 'ChillerOptimization',
                component: () => import('@/views/DataCenterOperations/CoolingOptimization/ChillerOptimization.vue'),
                meta: { title: 'Chiller Optimization' }
              },
              {
                path: 'crac-optimization',
                name: 'CracOptimization',
                component: () => import('@/views/DataCenterOperations/CoolingOptimization/CracOptimization.vue'),
                meta: { title: 'CRAC Optimization' }
              },
              {
                path: 'crah-optimization',
                name: 'CrahOptimization',
                component: () => import('@/views/DataCenterOperations/CoolingOptimization/CrahOptimization.vue'),
                meta: { title: 'CRAH Optimization' }
              },
              {
                path: 'free-cooling',
                name: 'FreeCooling',
                component: () => import('@/views/DataCenterOperations/CoolingOptimization/FreeCooling.vue'),
                meta: { title: 'Free Cooling' }
              },
              {
                path: 'hybrid-cooling',
                name: 'HybridCooling',
                component: () => import('@/views/DataCenterOperations/CoolingOptimization/HybridCooling.vue'),
                meta: { title: 'Hybrid Cooling' }
              },
              {
                path: 'dynamic-setpoint-control',
                name: 'DynamicSetpointControl',
                component: () => import('@/views/DataCenterOperations/CoolingOptimization/DynamicSetpointControl.vue'),
                meta: { title: 'Dynamic Setpoint Control' }
              },
              {
                path: 'cooling-benchmark',
                name: 'CoolingBenchmark',
                component: () => import('@/views/DataCenterOperations/CoolingOptimization/CoolingBenchmark.vue'),
                meta: { title: 'Cooling Benchmark' }
              }
            ]
          },
          // 11.5 Airflow Optimization
          {
            path: 'airflow-optimization',
            name: 'AirflowOptimization',
            children: [
              {
                path: 'thermal-map',
                name: 'ThermalMap',
                component: () => import('@/views/DataCenterOperations/AirflowOptimization/ThermalMap.vue'),
                meta: { title: 'Thermal Map' }
              },
              {
                path: 'hotspot-detection',
                name: 'HotspotDetection',
                component: () => import('@/views/DataCenterOperations/AirflowOptimization/HotspotDetection.vue'),
                meta: { title: 'Hotspot Detection' }
              },
              {
                path: 'cfd-simulation',
                name: 'CfdSimulation',
                component: () => import('@/views/DataCenterOperations/AirflowOptimization/CfdSimulation.vue'),
                meta: { title: 'CFD Simulation' }
              },
              {
                path: 'airflow-analysis',
                name: 'AirflowAnalysis',
                component: () => import('@/views/DataCenterOperations/AirflowOptimization/AirflowAnalysis.vue'),
                meta: { title: 'Airflow Analysis' }
              },
              {
                path: 'containment-analysis',
                name: 'ContainmentAnalysis',
                component: () => import('@/views/DataCenterOperations/AirflowOptimization/ContainmentAnalysis.vue'),
                meta: { title: 'Containment Analysis' }
              }
            ]
          },
          // 11.6 Power Optimization
          {
            path: 'power-optimization',
            name: 'PowerOptimization',
            children: [
              {
                path: 'ups-optimization',
                name: 'UpsOptimization',
                component: () => import('@/views/DataCenterOperations/PowerOptimization/UpsOptimization.vue'),
                meta: { title: 'UPS Optimization' }
              },
              {
                path: 'pdu-optimization',
                name: 'PduOptimization',
                component: () => import('@/views/DataCenterOperations/PowerOptimization/PduOptimization.vue'),
                meta: { title: 'PDU Optimization' }
              },
              {
                path: 'generator-strategy',
                name: 'GeneratorStrategy',
                component: () => import('@/views/DataCenterOperations/PowerOptimization/GeneratorStrategy.vue'),
                meta: { title: 'Generator Strategy' }
              },
              {
                path: 'battery-strategy',
                name: 'BatteryStrategy',
                component: () => import('@/views/DataCenterOperations/PowerOptimization/BatteryStrategy.vue'),
                meta: { title: 'Battery Strategy' }
              },
              {
                path: 'load-balancing',
                name: 'LoadBalancing',
                component: () => import('@/views/DataCenterOperations/PowerOptimization/LoadBalancing.vue'),
                meta: { title: 'Load Balancing' }
              },
              {
                path: 'power-quality',
                name: 'PowerQuality',
                component: () => import('@/views/DataCenterOperations/PowerOptimization/PowerQuality.vue'),
                meta: { title: 'Power Quality' }
              }
            ]
          },
          // 11.7 Capacity Management
          {
            path: 'capacity-management',
            name: 'CapacityManagement',
            children: [
              {
                path: 'rack-capacity',
                name: 'RackCapacity',
                component: () => import('@/views/DataCenterOperations/CapacityManagement/RackCapacity.vue'),
                meta: { title: 'Rack Capacity' }
              },
              {
                path: 'power-capacity',
                name: 'PowerCapacity',
                component: () => import('@/views/DataCenterOperations/CapacityManagement/PowerCapacity.vue'),
                meta: { title: 'Power Capacity' }
              },
              {
                path: 'cooling-capacity',
                name: 'CoolingCapacity',
                component: () => import('@/views/DataCenterOperations/CapacityManagement/CoolingCapacity.vue'),
                meta: { title: 'Cooling Capacity' }
              },
              {
                path: 'space-capacity',
                name: 'SpaceCapacity',
                component: () => import('@/views/DataCenterOperations/CapacityManagement/SpaceCapacity.vue'),
                meta: { title: 'Space Capacity' }
              },
              {
                path: 'capacity-forecast',
                name: 'CapacityForecast',
                component: () => import('@/views/DataCenterOperations/CapacityManagement/CapacityForecast.vue'),
                meta: { title: 'Capacity Forecast' }
              }
            ]
          },
          // 11.8 Rack Management
          {
            path: 'rack-management',
            name: 'RackManagement',
            children: [
              {
                path: 'rack-layout',
                name: 'RackLayout',
                component: () => import('@/views/DataCenterOperations/RackManagement/RackLayout.vue'),
                meta: { title: 'Rack Layout' }
              },
              {
                path: 'rack-inventory',
                name: 'RackInventory',
                component: () => import('@/views/DataCenterOperations/RackManagement/RackInventory.vue'),
                meta: { title: 'Rack Inventory' }
              },
              {
                path: 'u-space-management',
                name: 'USpaceManagement',
                component: () => import('@/views/DataCenterOperations/RackManagement/USpaceManagement.vue'),
                meta: { title: 'U Space Management' }
              },
              {
                path: 'rack-utilization',
                name: 'RackUtilization',
                component: () => import('@/views/DataCenterOperations/RackManagement/RackUtilization.vue'),
                meta: { title: 'Rack Utilization' }
              }
            ]
          },
          // 11.9 Environmental Monitoring
          {
            path: 'environmental-monitoring',
            name: 'EnvironmentalMonitoring',
            component: () => import('@/views/DataCenterOperations/EnvironmentalMonitoring.vue'),
            meta: { title: 'Environmental Monitoring' }
          },
          // 11.10 Carbon Optimization
          {
            path: 'carbon-optimization',
            name: 'CarbonOptimization',
            component: () => import('@/views/DataCenterOperations/CarbonOptimization.vue'),
            meta: { title: 'Carbon Optimization' }
          },
          // 11.11 Scenario Simulation
          {
            path: 'scenario-simulation',
            name: 'ScenarioSimulation',
            children: [
              {
                path: 'baseline',
                name: 'Baseline',
                component: () => import('@/views/DataCenterOperations/ScenarioSimulation/Baseline.vue'),
                meta: { title: 'Baseline' }
              },
              {
                path: 'free-cooling-simulation',
                name: 'FreeCoolingSimulation',
                component: () => import('@/views/DataCenterOperations/ScenarioSimulation/FreeCoolingSimulation.vue'),
                meta: { title: 'Free Cooling' }
              },
              {
                path: 'hybrid-cooling-simulation',
                name: 'HybridCoolingSimulation',
                component: () => import('@/views/DataCenterOperations/ScenarioSimulation/HybridCoolingSimulation.vue'),
                meta: { title: 'Hybrid Cooling' }
              },
              {
                path: 'supply-air-optimization',
                name: 'SupplyAirOptimization',
                component: () => import('@/views/DataCenterOperations/ScenarioSimulation/SupplyAirOptimization.vue'),
                meta: { title: 'Supply Air Optimization' }
              },
              {
                path: 'containment-upgrade',
                name: 'ContainmentUpgrade',
                component: () => import('@/views/DataCenterOperations/ScenarioSimulation/ContainmentUpgrade.vue'),
                meta: { title: 'Containment Upgrade' }
              },
              {
                path: 'roi-simulation',
                name: 'RoiSimulation',
                component: () => import('@/views/DataCenterOperations/ScenarioSimulation/RoiSimulation.vue'),
                meta: { title: 'ROI Simulation' }
              }
            ]
          },
          // 11.12 Recommendation Center
          {
            path: 'recommendation-center',
            name: 'RecommendationCenter',
            component: () => import('@/views/DataCenterOperations/RecommendationCenter.vue'),
            meta: { title: 'Recommendation Center' }
          },
          // 11.13 Savings Verification
          {
            path: 'savings-verification',
            name: 'SavingsVerification',
            component: () => import('@/views/DataCenterOperations/SavingsVerification.vue'),
            meta: { title: 'Savings Verification' }
          },
          // 11.14 Asset Lifecycle
          {
            path: 'asset-lifecycle',
            name: 'AssetLifecycle',
            component: () => import('@/views/DataCenterOperations/AssetLifecycle.vue'),
            meta: { title: 'Asset Lifecycle' }
          },
          // 11.15 Digital Twin Integration
          {
            path: 'digital-twin-integration',
            name: 'DigitalTwinIntegration',
            component: () => import('@/views/DataCenterOperations/DigitalTwinIntegration.vue'),
            meta: { title: 'Digital Twin Integration' }
          },
          // 11.16 Sustainability Reports
          {
            path: 'sustainability-reports',
            name: 'SustainabilityReports',
            component: () => import('@/views/DataCenterOperations/SustainabilityReports.vue'),
            meta: { title: 'Sustainability Reports' }
          }
        ]
      },
      // 12. Decision & Evidence (CDE)
      {
        path: 'decision-evidence',
        name: 'DecisionEvidence',
        children: [
          // 12.1 Decision Dashboard
          {
            path: 'decision-dashboard',
            name: 'DecisionDashboard',
            component: () => import('@/views/DecisionEvidence/DecisionDashboard.vue'),
            meta: { title: 'Decision Dashboard' }
          },
          // 12.2 Decision Register
          {
            path: 'decision-register',
            name: 'DecisionRegister',
            children: [
              {
                path: 'fault-decisions',
                name: 'FaultDecisions',
                component: () => import('@/views/DecisionEvidence/DecisionRegister/FaultDecisions.vue'),
                meta: { title: 'Fault Decisions' }
              },
              {
                path: 'maintenance-decisions',
                name: 'MaintenanceDecisions',
                component: () => import('@/views/DecisionEvidence/DecisionRegister/MaintenanceDecisions.vue'),
                meta: { title: 'Maintenance Decisions' }
              },
              {
                path: 'esg-decisions',
                name: 'EsgDecisions',
                component: () => import('@/views/DecisionEvidence/DecisionRegister/EsgDecisions.vue'),
                meta: { title: 'ESG Decisions' }
              },
              {
                path: 'energy-decisions',
                name: 'EnergyDecisions',
                component: () => import('@/views/DecisionEvidence/DecisionRegister/EnergyDecisions.vue'),
                meta: { title: 'Energy Decisions' }
              },
              {
                path: 'ai-recommendations',
                name: 'AiRecommendations',
                component: () => import('@/views/DecisionEvidence/DecisionRegister/AiRecommendations.vue'),
                meta: { title: 'AI Recommendations' }
              }
            ]
          },
          // 12.3 Workflow Management
          {
            path: 'workflow-management',
            name: 'WorkflowManagement',
            children: [
              {
                path: 'approval-matrix',
                name: 'ApprovalMatrixWorkflow',
                component: () => import('@/views/DecisionEvidence/WorkflowManagement/ApprovalMatrix.vue'),
                meta: { title: 'Approval Matrix' }
              },
              {
                path: 'approval-steps',
                name: 'ApprovalSteps',
                component: () => import('@/views/DecisionEvidence/WorkflowManagement/ApprovalSteps.vue'),
                meta: { title: 'Approval Steps' }
              },
              {
                path: 'delegation',
                name: 'Delegation',
                component: () => import('@/views/DecisionEvidence/WorkflowManagement/Delegation.vue'),
                meta: { title: 'Delegation' }
              },
              {
                path: 'exception-handling',
                name: 'ExceptionHandling',
                component: () => import('@/views/DecisionEvidence/WorkflowManagement/ExceptionHandling.vue'),
                meta: { title: 'Exception Handling' }
              }
            ]
          },
          // 12.4 Decision Timeline
          {
            path: 'decision-timeline',
            name: 'DecisionTimeline',
            component: () => import('@/views/DecisionEvidence/DecisionTimeline.vue'),
            meta: { title: 'Decision Timeline' }
          },
          // 12.5 Evidence Repository
          {
            path: 'evidence-repository',
            name: 'EvidenceRepository',
            children: [
              {
                path: 'photos',
                name: 'Photos',
                component: () => import('@/views/DecisionEvidence/EvidenceRepository/Photos.vue'),
                meta: { title: 'Photos' }
              },
              {
                path: 'videos',
                name: 'Videos',
                component: () => import('@/views/DecisionEvidence/EvidenceRepository/Videos.vue'),
                meta: { title: 'Videos' }
              },
              {
                path: 'documents',
                name: 'Documents',
                component: () => import('@/views/DecisionEvidence/EvidenceRepository/Documents.vue'),
                meta: { title: 'Documents' }
              },
              {
                path: 'reports',
                name: 'Reports',
                component: () => import('@/views/DecisionEvidence/EvidenceRepository/Reports.vue'),
                meta: { title: 'Reports' }
              },
              {
                path: 'data-snapshots',
                name: 'DataSnapshots',
                component: () => import('@/views/DecisionEvidence/EvidenceRepository/DataSnapshots.vue'),
                meta: { title: 'Data Snapshots' }
              }
            ]
          },
          // 12.6 Audit Trail
          {
            path: 'audit-trail',
            name: 'AuditTrail',
            component: () => import('@/views/DecisionEvidence/AuditTrail.vue'),
            meta: { title: 'Audit Trail' }
          },
          // 12.7 Digital Signatures
          {
            path: 'digital-signatures',
            name: 'DigitalSignatures',
            component: () => import('@/views/DecisionEvidence/DigitalSignatures.vue'),
            meta: { title: 'Digital Signatures' }
          },
          // 12.8 Approval Matrix
          {
            path: 'approval-matrix',
            name: 'ApprovalMatrix',
            component: () => import('@/views/DecisionEvidence/ApprovalMatrix.vue'),
            meta: { title: 'Approval Matrix' }
          },
          // 12.9 Lessons Learned
          {
            path: 'lessons-learned',
            name: 'LessonsLearned',
            component: () => import('@/views/DecisionEvidence/LessonsLearned.vue'),
            meta: { title: 'Lessons Learned' }
          },
          // 12.10 AI Recommendation Log
          {
            path: 'ai-recommendation-log',
            name: 'AiRecommendationLog',
            component: () => import('@/views/DecisionEvidence/AiRecommendationLog.vue'),
            meta: { title: 'AI Recommendation Log' }
          }
        ]
      },
      // 13. Command Center
      {
        path: 'command-center',
        name: 'CommandCenter',
        children: [
          // 13.1 Operations Dashboard
          {
            path: 'operations-dashboard',
            name: 'OperationsDashboard',
            component: () => import('@/views/CommandCenter/OperationsDashboard.vue'),
            meta: { title: 'Operations Dashboard' }
          },
          // 13.2 GIS Map
          {
            path: 'gis-map',
            name: 'GisMap',
            component: () => import('@/views/CommandCenter/GisMap.vue'),
            meta: { title: 'GIS Map' }
          },
          // 13.3 Situation Awareness
          {
            path: 'situation-awareness',
            name: 'SituationAwareness',
            component: () => import('@/views/CommandCenter/SituationAwareness.vue'),
            meta: { title: 'Situation Awareness' }
          },
          // 13.4 Incident Center
          {
            path: 'incident-center',
            name: 'IncidentCenter',
            component: () => import('@/views/CommandCenter/IncidentCenter.vue'),
            meta: { title: 'Incident Center' }
          },
          // 13.5 Emergency Command
          {
            path: 'emergency-command',
            name: 'EmergencyCommand',
            component: () => import('@/views/CommandCenter/EmergencyCommand.vue'),
            meta: { title: 'Emergency Command' }
          },
          // 13.6 Resource Dispatch
          {
            path: 'resource-dispatch',
            name: 'ResourceDispatch',
            component: () => import('@/views/CommandCenter/ResourceDispatch.vue'),
            meta: { title: 'Resource Dispatch' }
          },
          // 13.7 Executive Dashboard
          {
            path: 'executive-dashboard',
            name: 'ExecutiveDashboard',
            component: () => import('@/views/CommandCenter/ExecutiveDashboard.vue'),
            meta: { title: 'Executive Dashboard' }
          }
        ]
      },
      // 14. Data Platform
      {
        path: 'data-platform',
        name: 'DataPlatform',
        children: [
          // 14.1 Data Sources
          {
            path: 'data-sources',
            name: 'DataSources',
            component: () => import('@/views/DataPlatform/DataSources.vue'),
            meta: { title: 'Data Sources' }
          },
          // 14.2 Data Quality
          {
            path: 'data-quality',
            name: 'DataQuality',
            children: [
              {
                path: 'quality-rules',
                name: 'QualityRules',
                component: () => import('@/views/DataPlatform/DataQuality/QualityRules.vue'),
                meta: { title: 'Quality Rules' }
              },
              {
                path: 'missing-data',
                name: 'MissingData',
                component: () => import('@/views/DataPlatform/DataQuality/MissingData.vue'),
                meta: { title: 'Missing Data' }
              },
              {
                path: 'outlier-detection',
                name: 'OutlierDetection',
                component: () => import('@/views/DataPlatform/DataQuality/OutlierDetection.vue'),
                meta: { title: 'Outlier Detection' }
              },
              {
                path: 'data-correction-log',
                name: 'DataCorrectionLog',
                component: () => import('@/views/DataPlatform/DataQuality/DataCorrectionLog.vue'),
                meta: { title: 'Data Correction Log' }
              }
            ]
          },
          // 14.3 Data Catalog
          {
            path: 'data-catalog',
            name: 'DataCatalog',
            component: () => import('@/views/DataPlatform/DataCatalog.vue'),
            meta: { title: 'Data Catalog' }
          },
          // 14.4 Historian
          {
            path: 'historian',
            name: 'Historian',
            children: [
              {
                path: 'raw-telemetry',
                name: 'RawTelemetry',
                component: () => import('@/views/DataPlatform/Historian/RawTelemetry.vue'),
                meta: { title: 'Raw Telemetry' }
              },
              {
                path: 'clean-telemetry',
                name: 'CleanTelemetry',
                component: () => import('@/views/DataPlatform/Historian/CleanTelemetry.vue'),
                meta: { title: 'Clean Telemetry' }
              },
              {
                path: 'aggregated-data',
                name: 'AggregatedData',
                component: () => import('@/views/DataPlatform/Historian/AggregatedData.vue'),
                meta: { title: 'Aggregated Data' }
              },
              {
                path: 'retention-policy',
                name: 'RetentionPolicy',
                component: () => import('@/views/DataPlatform/Historian/RetentionPolicy.vue'),
                meta: { title: 'Retention Policy' }
              }
            ]
          },
          // 14.5 Data Lake
          {
            path: 'data-lake',
            name: 'DataLake',
            component: () => import('@/views/DataPlatform/DataLake.vue'),
            meta: { title: 'Data Lake' }
          },
          // 14.6 ETL Management
          {
            path: 'etl-management',
            name: 'EtlManagement',
            component: () => import('@/views/DataPlatform/EtlManagement.vue'),
            meta: { title: 'ETL Management' }
          },
          // 14.7 Semantic Model
          {
            path: 'semantic-model',
            name: 'SemanticModel',
            children: [
              {
                path: 'site-building-space',
                name: 'SiteBuildingSpace',
                component: () => import('@/views/DataPlatform/SemanticModel/SiteBuildingSpace.vue'),
                meta: { title: 'Site / Building / Space' }
              },
              {
                path: 'asset-device-point',
                name: 'AssetDevicePoint',
                component: () => import('@/views/DataPlatform/SemanticModel/AssetDevicePoint.vue'),
                meta: { title: 'Asset / Device / Point' }
              },
              {
                path: 'event-fault-work-order',
                name: 'EventFaultWorkOrder',
                component: () => import('@/views/DataPlatform/SemanticModel/EventFaultWorkOrder.vue'),
                meta: { title: 'Event / Fault / Work Order' }
              },
              {
                path: 'esg-dcim-ai-semantics',
                name: 'EsgDcimAiSemantics',
                component: () => import('@/views/DataPlatform/SemanticModel/EsgDcimAiSemantics.vue'),
                meta: { title: 'ESG / DCIM / AI Semantics' }
              }
            ]
          },
          // 14.8 Metadata Management
          {
            path: 'metadata-management',
            name: 'MetadataManagement',
            component: () => import('@/views/DataPlatform/MetadataManagement.vue'),
            meta: { title: 'Metadata Management' }
          },
          // 14.9 Data Governance
          {
            path: 'data-governance',
            name: 'DataGovernance',
            component: () => import('@/views/DataPlatform/DataGovernance.vue'),
            meta: { title: 'Data Governance' }
          },
          // 14.10 Data Services
          {
            path: 'data-services',
            name: 'DataServices',
            children: [
              {
                path: 'rest-api',
                name: 'RestApi',
                component: () => import('@/views/DataPlatform/DataServices/RestApi.vue'),
                meta: { title: 'REST API' }
              },
              {
                path: 'graphql-api',
                name: 'GraphqlApi',
                component: () => import('@/views/DataPlatform/DataServices/GraphqlApi.vue'),
                meta: { title: 'GraphQL API' }
              },
              {
                path: 'websocket',
                name: 'Websocket',
                component: () => import('@/views/DataPlatform/DataServices/Websocket.vue'),
                meta: { title: 'WebSocket' }
              },
              {
                path: 'data-export-api',
                name: 'DataExportApi',
                component: () => import('@/views/DataPlatform/DataServices/DataExportApi.vue'),
                meta: { title: 'Data Export API' }
              }
            ]
          }
        ]
      },
      // 15. Integration Hub
      {
        path: 'integration-hub',
        name: 'IntegrationHub',
        children: [
          // 15.1 Protocol Gateway
          {
            path: 'protocol-gateway',
            name: 'ProtocolGateway',
            children: [
              {
                path: 'bacnet',
                name: 'Bacnet',
                component: () => import('@/views/IntegrationHub/ProtocolGateway/Bacnet.vue'),
                meta: { title: 'BACnet' }
              },
              {
                path: 'modbus',
                name: 'Modbus',
                component: () => import('@/views/IntegrationHub/ProtocolGateway/Modbus.vue'),
                meta: { title: 'Modbus' }
              },
              {
                path: 'opc-ua',
                name: 'OpcUa',
                component: () => import('@/views/IntegrationHub/ProtocolGateway/OpcUa.vue'),
                meta: { title: 'OPC-UA' }
              },
              {
                path: 'mqtt',
                name: 'Mqtt',
                component: () => import('@/views/IntegrationHub/ProtocolGateway/Mqtt.vue'),
                meta: { title: 'MQTT' }
              },
              {
                path: 'snmp',
                name: 'Snmp',
                component: () => import('@/views/IntegrationHub/ProtocolGateway/Snmp.vue'),
                meta: { title: 'SNMP' }
              },
              {
                path: 'knx',
                name: 'Knx',
                component: () => import('@/views/IntegrationHub/ProtocolGateway/Knx.vue'),
                meta: { title: 'KNX' }
              },
              {
                path: 'iec61850',
                name: 'Iec61850',
                component: () => import('@/views/IntegrationHub/ProtocolGateway/Iec61850.vue'),
                meta: { title: 'IEC61850' }
              },
              {
                path: 'onvif',
                name: 'Onvif',
                component: () => import('@/views/IntegrationHub/ProtocolGateway/Onvif.vue'),
                meta: { title: 'ONVIF' }
              },
              {
                path: 'rest-api',
                name: 'RestApiGateway',
                component: () => import('@/views/IntegrationHub/ProtocolGateway/RestApi.vue'),
                meta: { title: 'REST API' }
              }
            ]
          },
          // 15.2 Device Drivers
          {
            path: 'device-drivers',
            name: 'DeviceDrivers',
            children: [
              {
                path: 'siemens',
                name: 'Siemens',
                component: () => import('@/views/IntegrationHub/DeviceDrivers/Siemens.vue'),
                meta: { title: 'Siemens' }
              },
              {
                path: 'schneider',
                name: 'Schneider',
                component: () => import('@/views/IntegrationHub/DeviceDrivers/Schneider.vue'),
                meta: { title: 'Schneider' }
              },
              {
                path: 'abb',
                name: 'Abb',
                component: () => import('@/views/IntegrationHub/DeviceDrivers/Abb.vue'),
                meta: { title: 'ABB' }
              },
              {
                path: 'honeywell',
                name: 'Honeywell',
                component: () => import('@/views/IntegrationHub/DeviceDrivers/Honeywell.vue'),
                meta: { title: 'Honeywell' }
              },
              {
                path: 'johnson-controls',
                name: 'JohnsonControls',
                component: () => import('@/views/IntegrationHub/DeviceDrivers/JohnsonControls.vue'),
                meta: { title: 'Johnson Controls' }
              },
              {
                path: 'vertiv',
                name: 'Vertiv',
                component: () => import('@/views/IntegrationHub/DeviceDrivers/Vertiv.vue'),
                meta: { title: 'Vertiv' }
              },
              {
                path: 'huawei',
                name: 'Huawei',
                component: () => import('@/views/IntegrationHub/DeviceDrivers/Huawei.vue'),
                meta: { title: 'Huawei' }
              },
              {
                path: 'delta',
                name: 'Delta',
                component: () => import('@/views/IntegrationHub/DeviceDrivers/Delta.vue'),
                meta: { title: 'Delta' }
              },
              {
                path: 'daikin',
                name: 'Daikin',
                component: () => import('@/views/IntegrationHub/DeviceDrivers/Daikin.vue'),
                meta: { title: 'Daikin' }
              },
              {
                path: 'carrier',
                name: 'Carrier',
                component: () => import('@/views/IntegrationHub/DeviceDrivers/Carrier.vue'),
                meta: { title: 'Carrier' }
              },
              {
                path: 'mitsubishi',
                name: 'Mitsubishi',
                component: () => import('@/views/IntegrationHub/DeviceDrivers/Mitsubishi.vue'),
                meta: { title: 'Mitsubishi' }
              }
            ]
          },
          // 15.3 Private / Custom Protocols
          {
            path: 'custom-protocols',
            name: 'CustomProtocols',
            children: [
              {
                path: 'custom-iot-adapter',
                name: 'CustomIotAdapter',
                component: () => import('@/views/IntegrationHub/CustomProtocols/CustomIotAdapter.vue'),
                meta: { title: 'Custom IoT Adapter' }
              },
              {
                path: 'smart-toilet-adapter',
                name: 'SmartToiletAdapter',
                component: () => import('@/views/IntegrationHub/CustomProtocols/SmartToiletAdapter.vue'),
                meta: { title: 'Smart Toilet Adapter' }
              },
              {
                path: 'esp32-adapter',
                name: 'Esp32Adapter',
                component: () => import('@/views/IntegrationHub/CustomProtocols/Esp32Adapter.vue'),
                meta: { title: 'ESP32 Adapter' }
              },
              {
                path: 'ble-gateway-adapter',
                name: 'BleGatewayAdapter',
                component: () => import('@/views/IntegrationHub/CustomProtocols/BleGatewayAdapter.vue'),
                meta: { title: 'BLE Gateway Adapter' }
              },
              {
                path: 'payload-mapping',
                name: 'PayloadMapping',
                component: () => import('@/views/IntegrationHub/CustomProtocols/PayloadMapping.vue'),
                meta: { title: 'Payload Mapping' }
              }
            ]
          },
          // 15.4 Third Party Systems
          {
            path: 'third-party-systems',
            name: 'ThirdPartySystems',
            children: [
              {
                path: 'erp',
                name: 'Erp',
                component: () => import('@/views/IntegrationHub/ThirdPartySystems/Erp.vue'),
                meta: { title: 'ERP' }
              },
              {
                path: 'cmms',
                name: 'Cmms',
                component: () => import('@/views/IntegrationHub/ThirdPartySystems/Cmms.vue'),
                meta: { title: 'CMMS' }
              },
              {
                path: 'bim',
                name: 'Bim',
                component: () => import('@/views/IntegrationHub/ThirdPartySystems/Bim.vue'),
                meta: { title: 'BIM' }
              },
              {
                path: 'gis',
                name: 'Gis',
                component: () => import('@/views/IntegrationHub/ThirdPartySystems/Gis.vue'),
                meta: { title: 'GIS' }
              },
              {
                path: 'scada',
                name: 'Scada',
                component: () => import('@/views/IntegrationHub/ThirdPartySystems/Scada.vue'),
                meta: { title: 'SCADA' }
              },
              {
                path: 'ems',
                name: 'Ems',
                component: () => import('@/views/IntegrationHub/ThirdPartySystems/Ems.vue'),
                meta: { title: 'EMS' }
              }
            ]
          },
          // 15.5 Vendor Platform Adapter
          {
            path: 'vendor-platform-adapter',
            name: 'VendorPlatformAdapter',
            children: [
              {
                path: 'hikvision-platform',
                name: 'HikvisionPlatform',
                component: () => import('@/views/IntegrationHub/VendorPlatformAdapter/HikvisionPlatform.vue'),
                meta: { title: 'Hikvision Platform' }
              },
              {
                path: 'dahua-platform',
                name: 'DahuaPlatform',
                component: () => import('@/views/IntegrationHub/VendorPlatformAdapter/DahuaPlatform.vue'),
                meta: { title: 'Dahua Platform' }
              },
              {
                path: 'vms-platform',
                name: 'VmsPlatform',
                component: () => import('@/views/IntegrationHub/VendorPlatformAdapter/VmsPlatform.vue'),
                meta: { title: 'VMS Platform' }
              },
              {
                path: 'parking-platform',
                name: 'ParkingPlatform',
                component: () => import('@/views/IntegrationHub/VendorPlatformAdapter/ParkingPlatform.vue'),
                meta: { title: 'Parking Platform' }
              },
              {
                path: 'access-platform',
                name: 'AccessPlatform',
                component: () => import('@/views/IntegrationHub/VendorPlatformAdapter/AccessPlatform.vue'),
                meta: { title: 'Access Platform' }
              },
              {
                path: 'bms-platform',
                name: 'BmsPlatform',
                component: () => import('@/views/IntegrationHub/VendorPlatformAdapter/BmsPlatform.vue'),
                meta: { title: 'BMS Platform' }
              }
            ]
          },
          // 15.6 Protocol Health Check
          {
            path: 'protocol-health-check',
            name: 'ProtocolHealthCheck',
            children: [
              {
                path: 'connectivity-test',
                name: 'ConnectivityTest',
                component: () => import('@/views/IntegrationHub/ProtocolHealthCheck/ConnectivityTest.vue'),
                meta: { title: 'Connectivity Test' }
              },
              {
                path: 'point-read-test',
                name: 'PointReadTest',
                component: () => import('@/views/IntegrationHub/ProtocolHealthCheck/PointReadTest.vue'),
                meta: { title: 'Point Read Test' }
              },
              {
                path: 'command-write-test',
                name: 'CommandWriteTest',
                component: () => import('@/views/IntegrationHub/ProtocolHealthCheck/CommandWriteTest.vue'),
                meta: { title: 'Command Write Test' }
              },
              {
                path: 'latency-test',
                name: 'LatencyTest',
                component: () => import('@/views/IntegrationHub/ProtocolHealthCheck/LatencyTest.vue'),
                meta: { title: 'Latency Test' }
              },
              {
                path: 'baseline-comparison',
                name: 'BaselineComparison',
                component: () => import('@/views/IntegrationHub/ProtocolHealthCheck/BaselineComparison.vue'),
                meta: { title: 'Baseline Comparison' }
              },
              {
                path: 'health-reports',
                name: 'HealthReports',
                component: () => import('@/views/IntegrationHub/ProtocolHealthCheck/HealthReports.vue'),
                meta: { title: 'Health Reports' }
              }
            ]
          },
          // 15.7 Compatibility Center
          {
            path: 'compatibility-center',
            name: 'CompatibilityCenter',
            children: [
              {
                path: 'firmware-matrix',
                name: 'FirmwareMatrix',
                component: () => import('@/views/IntegrationHub/CompatibilityCenter/FirmwareMatrix.vue'),
                meta: { title: 'Firmware Matrix' }
              },
              {
                path: 'driver-matrix',
                name: 'DriverMatrix',
                component: () => import('@/views/IntegrationHub/CompatibilityCenter/DriverMatrix.vue'),
                meta: { title: 'Driver Matrix' }
              },
              {
                path: 'protocol-matrix',
                name: 'ProtocolMatrix',
                component: () => import('@/views/IntegrationHub/CompatibilityCenter/ProtocolMatrix.vue'),
                meta: { title: 'Protocol Matrix' }
              },
              {
                path: 'upgrade-assessment',
                name: 'UpgradeAssessment',
                component: () => import('@/views/IntegrationHub/CompatibilityCenter/UpgradeAssessment.vue'),
                meta: { title: 'Upgrade Assessment' }
              },
              {
                path: 'rollback-center',
                name: 'RollbackCenter',
                component: () => import('@/views/IntegrationHub/CompatibilityCenter/RollbackCenter.vue'),
                meta: { title: 'Rollback Center' }
              }
            ]
          },
          // 15.8 Security Monitoring
          {
            path: 'security-monitoring',
            name: 'SecurityMonitoring',
            children: [
              {
                path: 'unknown-device-detection',
                name: 'UnknownDeviceDetection',
                component: () => import('@/views/IntegrationHub/SecurityMonitoring/UnknownDeviceDetection.vue'),
                meta: { title: 'Unknown Device Detection' }
              },
              {
                path: 'protocol-attack-detection',
                name: 'ProtocolAttackDetection',
                component: () => import('@/views/IntegrationHub/SecurityMonitoring/ProtocolAttackDetection.vue'),
                meta: { title: 'Protocol Attack Detection' }
              },
              {
                path: 'abnormal-command-detection',
                name: 'AbnormalCommandDetection',
                component: () => import('@/views/IntegrationHub/SecurityMonitoring/AbnormalCommandDetection.vue'),
                meta: { title: 'Abnormal Command Detection' }
              },
              {
                path: 'auto-isolation',
                name: 'AutoIsolation',
                component: () => import('@/views/IntegrationHub/SecurityMonitoring/AutoIsolation.vue'),
                meta: { title: 'Auto Isolation' }
              }
            ]
          },
          // 15.9 Device Drift Detection
          {
            path: 'device-drift-detection',
            name: 'DeviceDriftDetection',
            component: () => import('@/views/IntegrationHub/DeviceDriftDetection.vue'),
            meta: { title: 'Device Drift Detection' }
          },
          // 15.10 API Management
          {
            path: 'api-management',
            name: 'ApiManagement',
            component: () => import('@/views/IntegrationHub/ApiManagement.vue'),
            meta: { title: 'API Management' }
          },
          // 15.11 Webhook Services
          {
            path: 'webhook-services',
            name: 'WebhookServices',
            component: () => import('@/views/IntegrationHub/WebhookServices.vue'),
            meta: { title: 'Webhook Services' }
          },
          // 15.12 Connector Marketplace
          {
            path: 'connector-marketplace',
            name: 'ConnectorMarketplace',
            component: () => import('@/views/IntegrationHub/ConnectorMarketplace.vue'),
            meta: { title: 'Connector Marketplace' }
          },
          // 15.13 Integration Monitoring
          {
            path: 'integration-monitoring',
            name: 'IntegrationMonitoring',
            component: () => import('@/views/IntegrationHub/IntegrationMonitoring.vue'),
            meta: { title: 'Integration Monitoring' }
          }
        ]
      },
      // 16. Reports & BI
      {
        path: 'reports-bi',
        name: 'ReportsBi',
        children: [
          // 16.1 Daily Reports
          {
            path: 'daily-reports',
            name: 'DailyReports',
            component: () => import('@/views/ReportsBi/DailyReports.vue'),
            meta: { title: 'Daily Reports' }
          },
          // 16.2 Weekly Reports
          {
            path: 'weekly-reports',
            name: 'WeeklyReports',
            component: () => import('@/views/ReportsBi/WeeklyReports.vue'),
            meta: { title: 'Weekly Reports' }
          },
          // 16.3 Monthly Reports
          {
            path: 'monthly-reports',
            name: 'MonthlyReports',
            component: () => import('@/views/ReportsBi/MonthlyReports.vue'),
            meta: { title: 'Monthly Reports' }
          },
          // 16.4 Annual Reports
          {
            path: 'annual-reports',
            name: 'AnnualReports',
            component: () => import('@/views/ReportsBi/AnnualReports.vue'),
            meta: { title: 'Annual Reports' }
          },
          // 16.5 Scheduled Reports
          {
            path: 'scheduled-reports',
            name: 'ScheduledReports',
            component: () => import('@/views/ReportsBi/ScheduledReports.vue'),
            meta: { title: 'Scheduled Reports' }
          },
          // 16.6 Custom Reports
          {
            path: 'custom-reports',
            name: 'CustomReports',
            component: () => import('@/views/ReportsBi/CustomReports.vue'),
            meta: { title: 'Custom Reports' }
          },
          // 16.7 BI Reports
          {
            path: 'bi-reports',
            name: 'BiReports',
            component: () => import('@/views/ReportsBi/BiReports.vue'),
            meta: { title: 'BI Reports' }
          },
          // 16.8 PDF Export
          {
            path: 'pdf-export',
            name: 'PdfExport',
            component: () => import('@/views/ReportsBi/PdfExport.vue'),
            meta: { title: 'PDF Export' }
          },
          // 16.9 Excel Export
          {
            path: 'excel-export',
            name: 'ExcelExport',
            component: () => import('@/views/ReportsBi/ExcelExport.vue'),
            meta: { title: 'Excel Export' }
          },
          // 16.10 Report Governance
          {
            path: 'report-governance',
            name: 'ReportGovernance',
            children: [
              {
                path: 'report-template',
                name: 'ReportTemplate',
                component: () => import('@/views/ReportsBi/ReportGovernance/ReportTemplate.vue'),
                meta: { title: 'Report Template' }
              },
              {
                path: 'report-approval',
                name: 'ReportApproval',
                component: () => import('@/views/ReportsBi/ReportGovernance/ReportApproval.vue'),
                meta: { title: 'Report Approval' }
              },
              {
                path: 'report-evidence-hash',
                name: 'ReportEvidenceHash',
                component: () => import('@/views/ReportsBi/ReportGovernance/ReportEvidenceHash.vue'),
                meta: { title: 'Report Evidence Hash' }
              },
              {
                path: 'report-access-log',
                name: 'ReportAccessLog',
                component: () => import('@/views/ReportsBi/ReportGovernance/ReportAccessLog.vue'),
                meta: { title: 'Report Access Log' }
              }
            ]
          }
        ]
      },
      // 17. Intelligence
      {
        path: 'intelligence',
        name: 'Intelligence',
        children: [
          // 17.1 AI Assistant
          {
            path: 'ai-assistant',
            name: 'AiAssistant',
            component: () => import('@/views/Intelligence/AiAssistant.vue'),
            meta: { title: 'AI Assistant' }
          },
          // 17.2 Predictive Maintenance
          {
            path: 'predictive-maintenance',
            name: 'PredictiveMaintenanceAI',
            children: [
              {
                path: 'equipment-health',
                name: 'EquipmentHealth',
                component: () => import('@/views/Intelligence/PredictiveMaintenance/EquipmentHealth.vue'),
                meta: { title: 'Equipment Health' }
              },
              {
                path: 'failure-prediction',
                name: 'FailurePrediction',
                component: () => import('@/views/Intelligence/PredictiveMaintenance/FailurePrediction.vue'),
                meta: { title: 'Failure Prediction' }
              },
              {
                path: 'maintenance-recommendation',
                name: 'MaintenanceRecommendation',
                component: () => import('@/views/Intelligence/PredictiveMaintenance/MaintenanceRecommendation.vue'),
                meta: { title: 'Maintenance Recommendation' }
              },
              {
                path: 'risk-ranking',
                name: 'RiskRanking',
                component: () => import('@/views/Intelligence/PredictiveMaintenance/RiskRanking.vue'),
                meta: { title: 'Risk Ranking' }
              }
            ]
          },
          // 17.3 Fault Diagnostics
          {
            path: 'fault-diagnostics',
            name: 'FaultDiagnostics',
            children: [
              {
                path: 'root-cause-analysis',
                name: 'RootCauseAnalysisAI',
                component: () => import('@/views/Intelligence/FaultDiagnostics/RootCauseAnalysis.vue'),
                meta: { title: 'Root Cause Analysis' }
              },
              {
                path: 'similar-fault-search',
                name: 'SimilarFaultSearch',
                component: () => import('@/views/Intelligence/FaultDiagnostics/SimilarFaultSearch.vue'),
                meta: { title: 'Similar Fault Search' }
              },
              {
                path: 'fault-correlation',
                name: 'FaultCorrelationAI',
                component: () => import('@/views/Intelligence/FaultDiagnostics/FaultCorrelation.vue'),
                meta: { title: 'Fault Correlation' }
              },
              {
                path: 'ai-diagnostic-workflow',
                name: 'AiDiagnosticWorkflow',
                component: () => import('@/views/Intelligence/FaultDiagnostics/AiDiagnosticWorkflow.vue'),
                meta: { title: 'AI Diagnostic Workflow' }
              }
            ]
          },
          // 17.4 Energy Optimization
          {
            path: 'energy-optimization',
            name: 'EnergyOptimization',
            children: [
              {
                path: 'hvac-optimization',
                name: 'HvacOptimizationAI',
                component: () => import('@/views/Intelligence/EnergyOptimization/HvacOptimization.vue'),
                meta: { title: 'HVAC Optimization' }
              },
              {
                path: 'lighting-optimization',
                name: 'LightingOptimizationAI',
                component: () => import('@/views/Intelligence/EnergyOptimization/LightingOptimization.vue'),
                meta: { title: 'Lighting Optimization' }
              },
              {
                path: 'demand-response',
                name: 'DemandResponse',
                component: () => import('@/views/Intelligence/EnergyOptimization/DemandResponse.vue'),
                meta: { title: 'Demand Response' }
              },
              {
                path: 'carbon-optimization',
                name: 'CarbonOptimizationAI',
                component: () => import('@/views/Intelligence/EnergyOptimization/CarbonOptimization.vue'),
                meta: { title: 'Carbon Optimization' }
              },
              {
                path: 'utility-cost-optimization',
                name: 'UtilityCostOptimization',
                component: () => import('@/views/Intelligence/EnergyOptimization/UtilityCostOptimization.vue'),
                meta: { title: 'Utility Cost Optimization' }
              }
            ]
          },
          // 17.5 Occupancy Intelligence
          {
            path: 'occupancy-intelligence',
            name: 'OccupancyIntelligence',
            component: () => import('@/views/Intelligence/OccupancyIntelligence.vue'),
            meta: { title: 'Occupancy Intelligence' }
          },
          // 17.6 Recommendation Center
          {
            path: 'recommendation-center-ai',
            name: 'RecommendationCenterAI',
            component: () => import('@/views/Intelligence/RecommendationCenter.vue'),
            meta: { title: 'Recommendation Center' }
          },
          // 17.7 Knowledge Graph
          {
            path: 'knowledge-graph',
            name: 'KnowledgeGraph',
            component: () => import('@/views/Intelligence/KnowledgeGraph.vue'),
            meta: { title: 'Knowledge Graph' }
          },
          // 17.8 Digital Operator
          {
            path: 'digital-operator',
            name: 'DigitalOperator',
            component: () => import('@/views/Intelligence/DigitalOperator.vue'),
            meta: { title: 'Digital Operator' }
          },
          // 17.9 AI Governance
          {
            path: 'ai-governance',
            name: 'AiGovernance',
            children: [
              {
                path: 'ai-policies',
                name: 'AiPolicies',
                component: () => import('@/views/Intelligence/AiGovernance/AiPolicies.vue'),
                meta: { title: 'AI Policies' }
              },
              {
                path: 'model-registry',
                name: 'ModelRegistry',
                component: () => import('@/views/Intelligence/AiGovernance/ModelRegistry.vue'),
                meta: { title: 'Model Registry' }
              },
              {
                path: 'prompt-management',
                name: 'PromptManagement',
                component: () => import('@/views/Intelligence/AiGovernance/PromptManagement.vue'),
                meta: { title: 'Prompt Management' }
              },
              {
                path: 'approval-rules',
                name: 'ApprovalRulesAI',
                component: () => import('@/views/Intelligence/AiGovernance/ApprovalRules.vue'),
                meta: { title: 'Approval Rules' }
              },
              {
                path: 'ai-audit-logs',
                name: 'AiAuditLogs',
                component: () => import('@/views/Intelligence/AiGovernance/AiAuditLogs.vue'),
                meta: { title: 'AI Audit Logs' }
              }
            ]
          }
        ]
      },
      // 18. AI Video Analytics
      {
        path: 'ai-video-analytics',
        name: 'AiVideoAnalytics',
        children: [
          // 18.1 PPE Compliance
          {
            path: 'ppe-compliance',
            name: 'PpeCompliance',
            children: [
              {
                path: 'helmet-detection',
                name: 'HelmetDetection',
                component: () => import('@/views/AiVideoAnalytics/PpeCompliance/HelmetDetection.vue'),
                meta: { title: 'Helmet Detection' }
              },
              {
                path: 'safety-vest-detection',
                name: 'SafetyVestDetection',
                component: () => import('@/views/AiVideoAnalytics/PpeCompliance/SafetyVestDetection.vue'),
                meta: { title: 'Safety Vest Detection' }
              },
              {
                path: 'gloves-detection',
                name: 'GlovesDetection',
                component: () => import('@/views/AiVideoAnalytics/PpeCompliance/GlovesDetection.vue'),
                meta: { title: 'Gloves Detection' }
              },
              {
                path: 'goggles-detection',
                name: 'GogglesDetection',
                component: () => import('@/views/AiVideoAnalytics/PpeCompliance/GogglesDetection.vue'),
                meta: { title: 'Goggles Detection' }
              },
              {
                path: 'ppe-reports',
                name: 'PpeReports',
                component: () => import('@/views/AiVideoAnalytics/PpeCompliance/PpeReports.vue'),
                meta: { title: 'PPE Reports' }
              }
            ]
          },
          // 18.2 Safety Monitoring
          {
            path: 'safety-monitoring',
            name: 'SafetyMonitoring',
            children: [
              {
                path: 'fall-detection',
                name: 'FallDetection',
                component: () => import('@/views/AiVideoAnalytics/SafetyMonitoring/FallDetection.vue'),
                meta: { title: 'Fall Detection' }
              },
              {
                path: 'intrusion-detection',
                name: 'IntrusionDetection',
                component: () => import('@/views/AiVideoAnalytics/SafetyMonitoring/IntrusionDetection.vue'),
                meta: { title: 'Intrusion Detection' }
              },
              {
                path: 'smoke-detection',
                name: 'SmokeDetection',
                component: () => import('@/views/AiVideoAnalytics/SafetyMonitoring/SmokeDetection.vue'),
                meta: { title: 'Smoke Detection' }
              },
              {
                path: 'fire-detection',
                name: 'FireDetection',
                component: () => import('@/views/AiVideoAnalytics/SafetyMonitoring/FireDetection.vue'),
                meta: { title: 'Fire Detection' }
              },
              {
                path: 'restricted-area-detection',
                name: 'RestrictedAreaDetection',
                component: () => import('@/views/AiVideoAnalytics/SafetyMonitoring/RestrictedAreaDetection.vue'),
                meta: { title: 'Restricted Area Detection' }
              },
              {
                path: 'loitering-detection',
                name: 'LoiteringDetection',
                component: () => import('@/views/AiVideoAnalytics/SafetyMonitoring/LoiteringDetection.vue'),
                meta: { title: 'Loitering Detection' }
              }
            ]
          },
          // 18.3 Vehicle Analytics
          {
            path: 'vehicle-analytics',
            name: 'VehicleAnalytics',
            children: [
              {
                path: 'anpr',
                name: 'AnprVideo',
                component: () => import('@/views/AiVideoAnalytics/VehicleAnalytics/Anpr.vue'),
                meta: { title: 'ANPR' }
              },
              {
                path: 'illegal-parking',
                name: 'IllegalParking',
                component: () => import('@/views/AiVideoAnalytics/VehicleAnalytics/IllegalParking.vue'),
                meta: { title: 'Illegal Parking' }
              },
              {
                path: 'vehicle-counting',
                name: 'VehicleCounting',
                component: () => import('@/views/AiVideoAnalytics/VehicleAnalytics/VehicleCounting.vue'),
                meta: { title: 'Vehicle Counting' }
              },
              {
                path: 'vehicle-tracking',
                name: 'VehicleTracking',
                component: () => import('@/views/AiVideoAnalytics/VehicleAnalytics/VehicleTracking.vue'),
                meta: { title: 'Vehicle Tracking' }
              },
              {
                path: 'fleet-analytics',
                name: 'FleetAnalytics',
                component: () => import('@/views/AiVideoAnalytics/VehicleAnalytics/FleetAnalytics.vue'),
                meta: { title: 'Fleet Analytics' }
              }
            ]
          },
          // 18.4 Crowd Analytics
          {
            path: 'crowd-analytics',
            name: 'CrowdAnalytics',
            children: [
              {
                path: 'occupancy-counting',
                name: 'OccupancyCounting',
                component: () => import('@/views/AiVideoAnalytics/CrowdAnalytics/OccupancyCounting.vue'),
                meta: { title: 'Occupancy Counting' }
              },
              {
                path: 'queue-detection',
                name: 'QueueDetection',
                component: () => import('@/views/AiVideoAnalytics/CrowdAnalytics/QueueDetection.vue'),
                meta: { title: 'Queue Detection' }
              },
              {
                path: 'density-monitoring',
                name: 'DensityMonitoring',
                component: () => import('@/views/AiVideoAnalytics/CrowdAnalytics/DensityMonitoring.vue'),
                meta: { title: 'Density Monitoring' }
              },
              {
                path: 'flow-analytics',
                name: 'FlowAnalytics',
                component: () => import('@/views/AiVideoAnalytics/CrowdAnalytics/FlowAnalytics.vue'),
                meta: { title: 'Flow Analytics' }
              }
            ]
          },
          // 18.5 Behavioral Analytics
          {
            path: 'behavioral-analytics',
            name: 'BehavioralAnalytics',
            component: () => import('@/views/AiVideoAnalytics/BehavioralAnalytics.vue'),
            meta: { title: 'Behavioral Analytics' }
          },
          // 18.6 Video Event Center
          {
            path: 'video-event-center',
            name: 'VideoEventCenter',
            component: () => import('@/views/AiVideoAnalytics/VideoEventCenter.vue'),
            meta: { title: 'Video Event Center' }
          },
          // 18.7 AI Evidence Repository
          {
            path: 'ai-evidence-repository',
            name: 'AiEvidenceRepository',
            component: () => import('@/views/AiVideoAnalytics/AiEvidenceRepository.vue'),
            meta: { title: 'AI Evidence Repository' }
          },
          // 18.8 Video Health Monitoring
          {
            path: 'video-health-monitoring',
            name: 'VideoHealthMonitoring',
            component: () => import('@/views/AiVideoAnalytics/VideoHealthMonitoring.vue'),
            meta: { title: 'Video Health Monitoring' }
          }
        ]
      },
      // 19. Digital Twin & OpenBIM
      {
        path: 'digital-twin-openbim',
        name: 'DigitalTwinOpenbim',
        children: [
          // 19.1 BIM Management
          {
            path: 'bim-management',
            name: 'BimManagement',
            children: [
              {
                path: 'ifc-import',
                name: 'IfcImport',
                component: () => import('@/views/DigitalTwinOpenbim/BimManagement/IfcImport.vue'),
                meta: { title: 'IFC Import' }
              },
              {
                path: 'cobie-import',
                name: 'CobieImport',
                component: () => import('@/views/DigitalTwinOpenbim/BimManagement/CobieImport.vue'),
                meta: { title: 'COBie Import' }
              },
              {
                path: 'bcf-issues',
                name: 'BcfIssues',
                component: () => import('@/views/DigitalTwinOpenbim/BimManagement/BcfIssues.vue'),
                meta: { title: 'BCF Issues' }
              },
              {
                path: 'model-validation',
                name: 'ModelValidation',
                component: () => import('@/views/DigitalTwinOpenbim/BimManagement/ModelValidation.vue'),
                meta: { title: 'Model Validation' }
              },
              {
                path: 'model-federation',
                name: 'ModelFederation',
                component: () => import('@/views/DigitalTwinOpenbim/BimManagement/ModelFederation.vue'),
                meta: { title: 'Model Federation' }
              }
            ]
          },
          // 19.2 Asset Localization
          {
            path: 'asset-localization',
            name: 'AssetLocalization',
            component: () => import('@/views/DigitalTwinOpenbim/AssetLocalization.vue'),
            meta: { title: 'Asset Localization' }
          },
          // 19.3 3D Navigation
          {
            path: '3d-navigation',
            name: 'ThreeDNavigation',
            component: () => import('@/views/DigitalTwinOpenbim/ThreeDNavigation.vue'),
            meta: { title: '3D Navigation' }
          },
          // 19.4 Real-Time Twin
          {
            path: 'real-time-twin',
            name: 'RealTimeTwin',
            component: () => import('@/views/DigitalTwinOpenbim/RealTimeTwin.vue'),
            meta: { title: 'Real-Time Twin' }
          },
          // 19.5 Scenario Simulation
          {
            path: 'scenario-simulation',
            name: 'ScenarioSimulationTwin',
            component: () => import('@/views/DigitalTwinOpenbim/ScenarioSimulation.vue'),
            meta: { title: 'Scenario Simulation' }
          },
          // 19.6 Energy Simulation
          {
            path: 'energy-simulation',
            name: 'EnergySimulation',
            component: () => import('@/views/DigitalTwinOpenbim/EnergySimulation.vue'),
            meta: { title: 'Energy Simulation' }
          },
          // 19.7 Emergency Simulation
          {
            path: 'emergency-simulation',
            name: 'EmergencySimulation',
            component: () => import('@/views/DigitalTwinOpenbim/EmergencySimulation.vue'),
            meta: { title: 'Emergency Simulation' }
          },
          // 19.8 Twin Analytics
          {
            path: 'twin-analytics',
            name: 'TwinAnalytics',
            component: () => import('@/views/DigitalTwinOpenbim/TwinAnalytics.vue'),
            meta: { title: 'Twin Analytics' }
          },
          // 19.9 OpenBIM Integration
          {
            path: 'openbim-integration',
            name: 'OpenbimIntegration',
            children: [
              {
                path: 'ifc-mapping',
                name: 'IfcMapping',
                component: () => import('@/views/DigitalTwinOpenbim/OpenbimIntegration/IfcMapping.vue'),
                meta: { title: 'IFC Mapping' }
              },
              {
                path: 'cobie-mapping',
                name: 'CobieMapping',
                component: () => import('@/views/DigitalTwinOpenbim/OpenbimIntegration/CobieMapping.vue'),
                meta: { title: 'COBie Mapping' }
              },
              {
                path: 'bsdd-dictionary',
                name: 'BsddDictionary',
                component: () => import('@/views/DigitalTwinOpenbim/OpenbimIntegration/BsddDictionary.vue'),
                meta: { title: 'bSDD Dictionary' }
              },
              {
                path: 'iso19650-cde-link',
                name: 'Iso19650CdeLink',
                component: () => import('@/views/DigitalTwinOpenbim/OpenbimIntegration/Iso19650CdeLink.vue'),
                meta: { title: 'ISO19650 CDE Link' }
              }
            ]
          },
          // 19.10 Digital Construction
          {
            path: 'digital-construction',
            name: 'DigitalConstruction',
            component: () => import('@/views/DigitalTwinOpenbim/DigitalConstruction.vue'),
            meta: { title: 'Digital Construction' }
          }
        ]
      },
      // 20. Trust & Identity
      {
        path: 'trust-identity',
        name: 'TrustIdentity',
        children: [
          // 20.1 DID Identity Center
          {
            path: 'did-identity-center',
            name: 'DidIdentityCenter',
            component: () => import('@/views/TrustIdentity/DidIdentityCenter.vue'),
            meta: { title: 'DID Identity Center' }
          },
          // 20.2 Credential Center
          {
            path: 'credential-center',
            name: 'CredentialCenter',
            children: [
              {
                path: 'issue-vc',
                name: 'IssueVc',
                component: () => import('@/views/TrustIdentity/CredentialCenter/IssueVc.vue'),
                meta: { title: 'Issue VC' }
              },
              {
                path: 'verify-vc',
                name: 'VerifyVc',
                component: () => import('@/views/TrustIdentity/CredentialCenter/VerifyVc.vue'),
                meta: { title: 'Verify VC' }
              },
              {
                path: 'revoke-vc',
                name: 'RevokeVc',
                component: () => import('@/views/TrustIdentity/CredentialCenter/RevokeVc.vue'),
                meta: { title: 'Revoke VC' }
              },
              {
                path: 'credential-templates',
                name: 'CredentialTemplates',
                component: () => import('@/views/TrustIdentity/CredentialCenter/CredentialTemplates.vue'),
                meta: { title: 'Credential Templates' }
              }
            ]
          },
          // 20.3 Blockchain Anchoring
          {
            path: 'blockchain-anchoring',
            name: 'BlockchainAnchoring',
            children: [
              {
                path: 'evidence-anchor',
                name: 'EvidenceAnchor',
                component: () => import('@/views/TrustIdentity/BlockchainAnchoring/EvidenceAnchor.vue'),
                meta: { title: 'Evidence Anchor' }
              },
              {
                path: 'decision-anchor',
                name: 'DecisionAnchor',
                component: () => import('@/views/TrustIdentity/BlockchainAnchoring/DecisionAnchor.vue'),
                meta: { title: 'Decision Anchor' }
              },
              {
                path: 'esg-anchor',
                name: 'EsgAnchor',
                component: () => import('@/views/TrustIdentity/BlockchainAnchoring/EsgAnchor.vue'),
                meta: { title: 'ESG Anchor' }
              },
              {
                path: 'credential-anchor',
                name: 'CredentialAnchor',
                component: () => import('@/views/TrustIdentity/BlockchainAnchoring/CredentialAnchor.vue'),
                meta: { title: 'Credential Anchor' }
              }
            ]
          },
          // 20.4 Smart Contracts
          {
            path: 'smart-contracts',
            name: 'SmartContracts',
            component: () => import('@/views/TrustIdentity/SmartContracts.vue'),
            meta: { title: 'Smart Contracts' }
          },
          // 20.5 Decision Traceability
          {
            path: 'decision-traceability',
            name: 'DecisionTraceability',
            component: () => import('@/views/TrustIdentity/DecisionTraceability.vue'),
            meta: { title: 'Decision Traceability' }
          },
          // 20.6 Evidence Chain
          {
            path: 'evidence-chain',
            name: 'EvidenceChain',
            component: () => import('@/views/TrustIdentity/EvidenceChain.vue'),
            meta: { title: 'Evidence Chain' }
          },
          // 20.7 Compliance Certificates
          {
            path: 'compliance-certificates',
            name: 'ComplianceCertificates',
            component: () => import('@/views/TrustIdentity/ComplianceCertificates.vue'),
            meta: { title: 'Compliance Certificates' }
          },
          // 20.8 Trust Audit Logs
          {
            path: 'trust-audit-logs',
            name: 'TrustAuditLogs',
            component: () => import('@/views/TrustIdentity/TrustAuditLogs.vue'),
            meta: { title: 'Trust Audit Logs' }
          }
        ]
      },
      // 21. Operational Assistance
      {
        path: 'operational-assistance',
        name: 'OperationalAssistance',
        children: [
          // 21.1 Device Discovery
          {
            path: 'device-discovery',
            name: 'DeviceDiscovery',
            children: [
              {
                path: 'bacnet-scan',
                name: 'BacnetScan',
                component: () => import('@/views/OperationalAssistance/DeviceDiscovery/BacnetScan.vue'),
                meta: { title: 'BACnet Scan' }
              },
              {
                path: 'modbus-scan',
                name: 'ModbusScan',
                component: () => import('@/views/OperationalAssistance/DeviceDiscovery/ModbusScan.vue'),
                meta: { title: 'Modbus Scan' }
              },
              {
                path: 'onvif-scan',
                name: 'OnvifScan',
                component: () => import('@/views/OperationalAssistance/DeviceDiscovery/OnvifScan.vue'),
                meta: { title: 'ONVIF Scan' }
              },
              {
                path: 'snmp-scan',
                name: 'SnmpScan',
                component: () => import('@/views/OperationalAssistance/DeviceDiscovery/SnmpScan.vue'),
                meta: { title: 'SNMP Scan' }
              },
              {
                path: 'mqtt-discovery',
                name: 'MqttDiscovery',
                component: () => import('@/views/OperationalAssistance/DeviceDiscovery/MqttDiscovery.vue'),
                meta: { title: 'MQTT Discovery' }
              },
              {
                path: 'custom-device-discovery',
                name: 'CustomDeviceDiscovery',
                component: () => import('@/views/OperationalAssistance/DeviceDiscovery/CustomDeviceDiscovery.vue'),
                meta: { title: 'Custom Device Discovery' }
              }
            ]
          },
          // 21.2 Commissioning Center
          {
            path: 'commissioning-center',
            name: 'CommissioningCenter',
            children: [
              {
                path: 'device-commissioning',
                name: 'DeviceCommissioning',
                component: () => import('@/views/OperationalAssistance/CommissioningCenter/DeviceCommissioning.vue'),
                meta: { title: 'Device Commissioning' }
              },
              {
                path: 'point-verification',
                name: 'PointVerification',
                component: () => import('@/views/OperationalAssistance/CommissioningCenter/PointVerification.vue'),
                meta: { title: 'Point Verification' }
              },
              {
                path: 'loop-check',
                name: 'LoopCheck',
                component: () => import('@/views/OperationalAssistance/CommissioningCenter/LoopCheck.vue'),
                meta: { title: 'Loop Check' }
              },
              {
                path: 'command-test',
                name: 'CommandTest',
                component: () => import('@/views/OperationalAssistance/CommissioningCenter/CommandTest.vue'),
                meta: { title: 'Command Test' }
              },
              {
                path: 'protocol-validation',
                name: 'ProtocolValidation',
                component: () => import('@/views/OperationalAssistance/CommissioningCenter/ProtocolValidation.vue'),
                meta: { title: 'Protocol Validation' }
              },
              {
                path: 'commissioning-report',
                name: 'CommissioningReport',
                component: () => import('@/views/OperationalAssistance/CommissioningCenter/CommissioningReport.vue'),
                meta: { title: 'Commissioning Report' }
              }
            ]
          },
          // 21.3 Diagnostic Center
          {
            path: 'diagnostic-center',
            name: 'DiagnosticCenter',
            children: [
              {
                path: 'protocol-diagnostics',
                name: 'ProtocolDiagnostics',
                component: () => import('@/views/OperationalAssistance/DiagnosticCenter/ProtocolDiagnostics.vue'),
                meta: { title: 'Protocol Diagnostics' }
              },
              {
                path: 'device-diagnostics',
                name: 'DeviceDiagnostics',
                component: () => import('@/views/OperationalAssistance/DiagnosticCenter/DeviceDiagnostics.vue'),
                meta: { title: 'Device Diagnostics' }
              },
              {
                path: 'network-diagnostics',
                name: 'NetworkDiagnostics',
                component: () => import('@/views/OperationalAssistance/DiagnosticCenter/NetworkDiagnostics.vue'),
                meta: { title: 'Network Diagnostics' }
              },
              {
                path: 'fault-diagnostics',
                name: 'FaultDiagnostics',
                component: () => import('@/views/OperationalAssistance/DiagnosticCenter/FaultDiagnostics.vue'),
                meta: { title: 'Fault Diagnostics' }
              },
              {
                path: 'ai-diagnostics',
                name: 'AiDiagnostics',
                component: () => import('@/views/OperationalAssistance/DiagnosticCenter/AiDiagnostics.vue'),
                meta: { title: 'AI Diagnostics' }
              }
            ]
          },
          // 21.4 Knowledge Base
          {
            path: 'knowledge-base',
            name: 'KnowledgeBaseOps',
            component: () => import('@/views/OperationalAssistance/KnowledgeBase.vue'),
            meta: { title: 'Knowledge Base' }
          },
          // 21.5 AI Q&A Assistant
          {
            path: 'ai-qa-assistant',
            name: 'AiQaAssistant',
            component: () => import('@/views/OperationalAssistance/AiQaAssistant.vue'),
            meta: { title: 'AI Q&A Assistant' }
          },
          // 21.6 Training Center
          {
            path: 'training-center',
            name: 'TrainingCenter',
            component: () => import('@/views/OperationalAssistance/TrainingCenter.vue'),
            meta: { title: 'Training Center' }
          },
          // 21.7 Mobile Operations
          {
            path: 'mobile-operations',
            name: 'MobileOperations',
            children: [
              {
                path: 'mobile-worker-app',
                name: 'MobileWorkerApp',
                component: () => import('@/views/OperationalAssistance/MobileOperations/MobileWorkerApp.vue'),
                meta: { title: 'Mobile Worker App' }
              },
              {
                path: 'qr-scan',
                name: 'QrScan',
                component: () => import('@/views/OperationalAssistance/MobileOperations/QrScan.vue'),
                meta: { title: 'QR Scan' }
              },
              {
                path: 'voice-input',
                name: 'VoiceInput',
                component: () => import('@/views/OperationalAssistance/MobileOperations/VoiceInput.vue'),
                meta: { title: 'Voice Input' }
              },
              {
                path: 'offline-sync',
                name: 'OfflineSync',
                component: () => import('@/views/OperationalAssistance/MobileOperations/OfflineSync.vue'),
                meta: { title: 'Offline Sync' }
              },
              {
                path: 'push-notifications',
                name: 'PushNotifications',
                component: () => import('@/views/OperationalAssistance/MobileOperations/PushNotifications.vue'),
                meta: { title: 'Push Notifications' }
              }
            ]
          },
          // 21.8 Tablet Engineering Console
          {
            path: 'tablet-engineering-console',
            name: 'TabletEngineeringConsole',
            component: () => import('@/views/OperationalAssistance/TabletEngineeringConsole.vue'),
            meta: { title: 'Tablet Engineering Console' }
          },
          // 21.9 On-Site Terminal
          {
            path: 'on-site-terminal',
            name: 'OnSiteTerminal',
            component: () => import('@/views/OperationalAssistance/OnSiteTerminal.vue'),
            meta: { title: 'On-Site Terminal' }
          }
        ]
      },
      // 22. Security & Compliance
      {
        path: 'security-compliance',
        name: 'SecurityCompliance',
        children: [
          // 22.1 Cybersecurity Dashboard
          {
            path: 'cybersecurity-dashboard',
            name: 'CybersecurityDashboard',
            component: () => import('@/views/SecurityCompliance/CybersecurityDashboard.vue'),
            meta: { title: 'Cybersecurity Dashboard' }
          },
          // 22.2 IEC62443 Compliance
          {
            path: 'iec62443-compliance',
            name: 'Iec62443Compliance',
            component: () => import('@/views/SecurityCompliance/Iec62443Compliance.vue'),
            meta: { title: 'IEC62443 Compliance' }
          },
          // 22.3 ISO27001 Compliance
          {
            path: 'iso27001-compliance',
            name: 'Iso27001Compliance',
            component: () => import('@/views/SecurityCompliance/Iso27001Compliance.vue'),
            meta: { title: 'ISO27001 Compliance' }
          },
          // 22.4 NIST Framework
          {
            path: 'nist-framework',
            name: 'NistFramework',
            component: () => import('@/views/SecurityCompliance/NistFramework.vue'),
            meta: { title: 'NIST Framework' }
          },
          // 22.5 Security Monitoring
          {
            path: 'security-monitor',
            name: 'SecurityMonitor',
            component: () => import('@/views/SecurityCompliance/SecurityMonitor.vue'),
            meta: { title: 'Security Monitoring' }
          },
          // 22.6 Threat Detection
          {
            path: 'threat-detection',
            name: 'ThreatDetection',
            component: () => import('@/views/SecurityCompliance/ThreatDetection.vue'),
            meta: { title: 'Threat Detection' }
          },
          // 22.7 Vulnerability Management
          {
            path: 'vulnerability-management',
            name: 'VulnerabilityManagement',
            component: () => import('@/views/SecurityCompliance/VulnerabilityManagement.vue'),
            meta: { title: 'Vulnerability Management' }
          },
          // 22.8 Device Security
          {
            path: 'device-security',
            name: 'DeviceSecurity',
            component: () => import('@/views/SecurityCompliance/DeviceSecurity.vue'),
            meta: { title: 'Device Security' }
          },
          // 22.9 Command Security
          {
            path: 'command-security',
            name: 'CommandSecurity',
            component: () => import('@/views/SecurityCompliance/CommandSecurity.vue'),
            meta: { title: 'Command Security' }
          },
          // 22.10 Audit Management
          {
            path: 'audit-management',
            name: 'AuditManagement',
            component: () => import('@/views/SecurityCompliance/AuditManagement.vue'),
            meta: { title: 'Audit Management' }
          },
          // 22.11 Compliance Reports
          {
            path: 'compliance-reports',
            name: 'ComplianceReports',
            component: () => import('@/views/SecurityCompliance/ComplianceReports.vue'),
            meta: { title: 'Compliance Reports' }
          }
        ]
      },
      // 23. Developer Center
      {
        path: 'developer-center',
        name: 'DeveloperCenter',
        children: [
          // 23.1 API Gateway
          {
            path: 'api-gateway',
            name: 'ApiGatewayDev',
            component: () => import('@/views/DeveloperCenter/ApiGateway.vue'),
            meta: { title: 'API Gateway' }
          },
          // 23.2 API Documentation
          {
            path: 'api-documentation',
            name: 'ApiDocumentation',
            component: () => import('@/views/DeveloperCenter/ApiDocumentation.vue'),
            meta: { title: 'API Documentation' }
          },
          // 23.3 SDK Management
          {
            path: 'sdk-management',
            name: 'SdkManagement',
            component: () => import('@/views/DeveloperCenter/SdkManagement.vue'),
            meta: { title: 'SDK Management' }
          },
          // 23.4 Protocol Registry
          {
            path: 'protocol-registry',
            name: 'ProtocolRegistry',
            component: () => import('@/views/DeveloperCenter/ProtocolRegistry.vue'),
            meta: { title: 'Protocol Registry' }
          },
          // 23.5 Device Templates
          {
            path: 'device-templates',
            name: 'DeviceTemplates',
            component: () => import('@/views/DeveloperCenter/DeviceTemplates.vue'),
            meta: { title: 'Device Templates' }
          },
          // 23.6 Driver Marketplace
          {
            path: 'driver-marketplace',
            name: 'DriverMarketplace',
            component: () => import('@/views/DeveloperCenter/DriverMarketplace.vue'),
            meta: { title: 'Driver Marketplace' }
          },
          // 23.7 Integration Sandbox
          {
            path: 'integration-sandbox',
            name: 'IntegrationSandbox',
            component: () => import('@/views/DeveloperCenter/IntegrationSandbox.vue'),
            meta: { title: 'Integration Sandbox' }
          },
          // 23.8 Webhook Management
          {
            path: 'webhook-management',
            name: 'WebhookManagementDev',
            component: () => import('@/views/DeveloperCenter/WebhookManagement.vue'),
            meta: { title: 'Webhook Management' }
          },
          // 23.9 Feature Toggle Registry
          {
            path: 'feature-toggle-registry',
            name: 'FeatureToggleRegistry',
            component: () => import('@/views/DeveloperCenter/FeatureToggleRegistry.vue'),
            meta: { title: 'Feature Toggle Registry' }
          },
          // 23.10 System Health API
          {
            path: 'system-health-api',
            name: 'SystemHealthApi',
            component: () => import('@/views/DeveloperCenter/SystemHealthApi.vue'),
            meta: { title: 'System Health API' }
          }
        ]
      },
      // 24. Administration
      {
        path: 'administration',
        name: 'Administration',
        children: [
          // 24.1 User Management
          {
            path: 'user-management',
            name: 'UserManagement',
            component: () => import('@/views/Administration/UserManagement.vue'),
            meta: { title: 'User Management' }
          },
          // 24.2 Role Management
          {
            path: 'role-management',
            name: 'RoleManagement',
            component: () => import('@/views/Administration/RoleManagement.vue'),
            meta: { title: 'Role Management' }
          },
          // 24.3 Permission Management
          {
            path: 'permission-management',
            name: 'PermissionManagement',
            component: () => import('@/views/Administration/PermissionManagement.vue'),
            meta: { title: 'Permission Management' }
          },
          // 24.4 Edition Management
          {
            path: 'edition-management',
            name: 'EditionManagement',
            children: [
              {
                path: 'menu',
                name: 'MenuManagement',
                component: () => import('@/views/Administration/EditionManagement/MenuManagement.vue'),
                meta: { title: 'Menu Management' }
              },
              {
                path: 'lite',
                name: 'Lite',
                component: () => import('@/views/Administration/EditionManagement/Lite.vue'),
                meta: { title: 'Lite' }
              },
              {
                path: 'professional',
                name: 'Professional',
                component: () => import('@/views/Administration/EditionManagement/Professional.vue'),
                meta: { title: 'Professional' }
              },
              {
                path: 'enterprise',
                name: 'Enterprise',
                component: () => import('@/views/Administration/EditionManagement/Enterprise.vue'),
                meta: { title: 'Enterprise' }
              },
              {
                path: 'ai-enterprise',
                name: 'AiEnterprise',
                component: () => import('@/views/Administration/EditionManagement/AiEnterprise.vue'),
                meta: { title: 'AI Enterprise' }
              }
            ]
          },
          // 24.5 License Management
          {
            path: 'license-management',
            name: 'LicenseManagement',
            component: () => import('@/views/Administration/LicenseManagement.vue'),
            meta: { title: 'License Management' }
          },
          // 24.6 Feature Toggle Management
          {
            path: 'feature-toggle-management',
            name: 'FeatureToggleManagement',
            children: [
              {
                path: 'core-modules',
                name: 'CoreModules',
                component: () => import('@/views/Administration/FeatureToggleManagement/CoreModules.vue'),
                meta: { title: 'Core Modules' }
              },
              {
                path: 'esg-modules',
                name: 'EsgModules',
                component: () => import('@/views/Administration/FeatureToggleManagement/EsgModules.vue'),
                meta: { title: 'ESG Modules' }
              },
              {
                path: 'dcim-modules',
                name: 'DcimModules',
                component: () => import('@/views/Administration/FeatureToggleManagement/DcimModules.vue'),
                meta: { title: 'DCIM Modules' }
              },
              {
                path: 'ai-modules',
                name: 'AiModules',
                component: () => import('@/views/Administration/FeatureToggleManagement/AiModules.vue'),
                meta: { title: 'AI Modules' }
              },
              {
                path: 'digital-twin-modules',
                name: 'DigitalTwinModules',
                component: () => import('@/views/Administration/FeatureToggleManagement/DigitalTwinModules.vue'),
                meta: { title: 'Digital Twin Modules' }
              },
              {
                path: 'trust-modules',
                name: 'TrustModules',
                component: () => import('@/views/Administration/FeatureToggleManagement/TrustModules.vue'),
                meta: { title: 'Trust Modules' }
              },
              {
                path: 'security-modules',
                name: 'SecurityModules',
                component: () => import('@/views/Administration/FeatureToggleManagement/SecurityModules.vue'),
                meta: { title: 'Security Modules' }
              },
              {
                path: 'experimental-features',
                name: 'ExperimentalFeatures',
                component: () => import('@/views/Administration/FeatureToggleManagement/ExperimentalFeatures.vue'),
                meta: { title: 'Experimental Features' }
              }
            ]
          },
          // 24.7 Tenant Management
          {
            path: 'tenant-management',
            name: 'TenantManagement',
            component: () => import('@/views/Administration/TenantManagement.vue'),
            meta: { title: 'Tenant Management' }
          },
          // 24.8 Integration Settings
          {
            path: 'integration-settings',
            name: 'IntegrationSettings',
            component: () => import('@/views/Administration/IntegrationSettings.vue'),
            meta: { title: 'Integration Settings' }
          },
          // 24.9 Notification Settings
          {
            path: 'notification-settings',
            name: 'NotificationSettings',
            component: () => import('@/views/Administration/NotificationSettings.vue'),
            meta: { title: 'Notification Settings' }
          },
          // 24.10 System Settings
          {
            path: 'system-settings',
            name: 'SystemSettings',
            component: () => import('@/views/Administration/SystemSettings.vue'),
            meta: { title: 'System Settings' }
          },
          // 24.11 Audit Logs
          {
            path: 'audit-logs',
            name: 'AuditLogsAdmin',
            component: () => import('@/views/Administration/AuditLogs.vue'),
            meta: { title: 'Audit Logs' }
          },
          // 24.12 OEM Branding
          {
            path: 'oem-branding',
            name: 'OemBranding',
            component: () => import('@/views/Administration/OemBranding.vue'),
            meta: { title: 'OEM Branding' }
          }
        ]
      },
      // 404 处理 - 必须放在最后
      {
        path: '/:pathMatch(.*)*',
        name: 'NotFound',
        redirect: '/Factory'
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL || '/'),
  routes,
  // 滚动行为
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// 路由错误处理
router.onError((error) => {
  console.error('Router error:', error)
  const pattern = /Loading chunk (\d)+ failed/g
  const isChunkLoadFailed = error.message.match(pattern)
  if (isChunkLoadFailed) {
    // 加载失败时刷新页面
    window.location.reload()
  }
})

// 导航守卫 - 处理加载失败
router.beforeEach(async (to, from, next) => {
  // 设置页面标题
  if (to.meta?.title) {
    document.title = `${to.meta.title} - IBMS IoT Platform`
  } else {
    document.title = 'IBMS IoT Platform'
  }

  next()
})

// 路由完成后处理
router.afterEach((to, from, failure) => {
  if (failure) {
    console.warn('Navigation failed:', failure)
  }
})

export default router