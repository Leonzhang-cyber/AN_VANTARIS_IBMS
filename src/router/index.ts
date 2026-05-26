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
    redirect: '/home/system-overview',  // 直接重定向，不要嵌套 children 的重定向
    children: [
      //   05-26 newest
      {
        path: 'home',
        name: 'Home',
        children: [
          {
            path: 'system-overview',
            name: 'SystemOverview',
            component: () => import('@/views/Home/System.vue'),
            meta: { title: 'System Overview' }
          },
          {
            path: 'kpi-dashboard',
            name: 'KPIDashboard',
            component: () => import('@/views/Home/KPI.vue'),
            meta: { title: 'KPI Dashboard' }
          },
          {
            path: 'alarm-summary',
            name: 'AlarmSummary',
            component: () => import('@/views/Home/Alarm.vue'),
            meta: { title: 'Alarm Summary' }
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
            path: 'ai-insights',
            name: 'AIInsights',
            component: () => import('@/views/Home/AI.vue'),
            meta: { title: 'AI Insights' }
          }
        ]
      },
      {
        path: 'operations',
        name: 'Operations',
        children: [
          {
            path: 'quick-control',
            name: 'QuickControl',
            component: () => import('@/views/Operations/Control.vue'),
            meta: { title: 'Quick Control' }
          },
          {
            path: 'scene-management',
            name: 'SceneManagement',
            component: () => import('@/views/Operations/Scene.vue'),
            meta: { title: 'Scene Management' }
          },
          {
            path: 'emergency-response',
            name: 'EmergencyResponse',
            component: () => import('@/views/Operations/Emergency.vue'),
            meta: { title: 'Emergency Response' }
          },
          {
            path: 'operations-logbook',
            name: 'OperationsLogbook',
            component: () => import('@/views/Operations/Logbook.vue'),
            meta: { title: 'Operations Logbook' }
          },
          {
            path: 'shift-handover',
            name: 'ShiftHandover',
            component: () => import('@/views/Operations/Shift.vue'),
            meta: { title: 'Shift Handover' }
          }
        ]
      },
      // ==================== Sites & Spaces ====================
      {
        path: 'sites-spaces',
        name: 'SitesSpaces',
        redirect: '/sites-spaces/site-management',
        children: [
          {
            path: 'site-management',
            name: 'SiteManagement',
            component: () => import('@/views/Sites/SiteManagement.vue'),
            meta: { title: 'Site Management' }
          },
          {
            path: 'building-management',
            name: 'BuildingManagement',
            component: () => import('@/views/Sites/BuildingManagement.vue'),
            meta: { title: 'Building Management' }
          },
          {
            path: 'floor-management',
            name: 'FloorManagement',
            component: () => import('@/views/Sites/FloorManagement.vue'),
            meta: { title: 'Floor Management' }
          },
          {
            path: 'zone-management',
            name: 'ZoneManagement',
            component: () => import('@/views/Sites/ZoneManagement.vue'),
            meta: { title: 'Zone Management' }
          },
          {
            path: 'space-management',
            name: 'SpaceManagement',
            component: () => import('@/views/Sites/SpaceManagement.vue'),
            meta: { title: 'Space Management' }
          },
          {
            path: 'multi-site-management',
            name: 'MultiSiteManagement',
            component: () => import('@/views/Sites/MultiSiteManagement.vue'),
            meta: { title: 'Multi-Site Management' }
          }
        ]
      },
      // ==================== Systems & Devices ====================
      {
        path: 'systems-devices',
        name: 'SystemsDevices',
        redirect: '/systems-devices/device-inventory',
        children: [
          // Device Management
          {
            path: 'device-inventory',
            name: 'DeviceInventory',
            component: () => import('@/views/Device/DeviceInventory.vue'),
            meta: { title: 'Device Inventory' }
          },
          {
            path: 'device-monitoring',
            name: 'DeviceMonitoring',
            component: () => import('@/views/Device/DeviceMonitoring.vue'),
            meta: { title: 'Device Monitoring' }
          },
          {
            path: 'device-groups',
            name: 'DeviceGroups',
            component: () => import('@/views/Device/DeviceGroups.vue'),
            meta: { title: 'Device Groups' }
          },
          {
            path: 'device-templates',
            name: 'DeviceTemplates',
            component: () => import('@/views/Device/DeviceTemplates.vue'),
            meta: { title: 'Device Templates' }
          },
          {
            path: 'point-management',
            name: 'PointManagement',
            component: () => import('@/views/Device/PointManagement.vue'),
            meta: { title: 'Point Management' }
          },
          {
            path: 'area-topology',
            name: 'AreaTopology',
            component: () => import('@/views/Device/AreaTopology.vue'),
            meta: { title: 'Area Topology' }
          },
          // Specific Systems
          {
            path: 'hvac-systems',
            name: 'HVACSystems',
            component: () => import('@/views/Device/DeviceHVAC.vue'),
            meta: { title: 'HVAC Systems' }
          },
          {
            path: 'lighting-systems',
            name: 'LightingSystems',
            component: () => import('@/views/Device/DeviceLighting.vue'),
            meta: { title: 'Lighting Systems' }
          },
          {
            path: 'electrical-systems',
            name: 'ElectricalSystems',
            component: () => import('@/views/Device/ElectricalSystems.vue'),
            meta: { title: 'Electrical Systems' }
          },
          {
            path: 'plumbing-systems',
            name: 'PlumbingSystems',
            component: () => import('@/views/Device/DevicePlumbing.vue'),
            meta: { title: 'Plumbing Systems' }
          },
          {
            path: 'fire-alarm-systems',
            name: 'FireAlarmSystems',
            component: () => import('@/views/Device/DeviceFAS.vue'),
            meta: { title: 'Fire Alarm Systems' }
          },
          {
            path: 'security-alarm-systems',
            name: 'SecurityAlarmSystems',
            component: () => import('@/views/Device/DeviceSAS.vue'),
            meta: { title: 'Security Alarm Systems' }
          },
          {
            path: 'access-control-systems',
            name: 'AccessControlSystems',
            component: () => import('@/views/Device/DeviceAccess.vue'),
            meta: { title: 'Access Control Systems' }
          },
          {
            path: 'cctv-systems',
            name: 'CCTVSystems',
            component: () => import('@/views/Device/DeviceCCTV.vue'),
            meta: { title: 'CCTV Systems' }
          },
          {
            path: 'ev-charging-systems',
            name: 'EVChargingSystems',
            component: () => import('@/views/Device/EVChargingSystems.vue'),
            meta: { title: 'EV Charging Systems' }
          },
          {
            path: 'renewable-energy-systems',
            name: 'RenewableEnergySystems',
            component: () => import('@/views/Device/RenewableEnergySystems.vue'),
            meta: { title: 'Renewable Energy Systems' }
          }
        ]
      },

      // ==================== Alarms & Events ====================
      {
        path: 'alarms-events',
        name: 'AlarmsEvents',
        redirect: '/alarms-events/live-alarms',
        children: [
          {
            path: 'live-alarms',
            name: 'LiveAlarms',
            component: () => import('@/views/Alarm/LiveAlarms.vue'),
            meta: { title: 'Live Alarms' }
          },
          {
            path: 'alarm-history',
            name: 'AlarmHistory',
            component: () => import('@/views/Alarm/AlarmHistory.vue'),
            meta: { title: 'Alarm History' }
          },
          {
            path: 'alarm-rules',
            name: 'AlarmRules',
            component: () => import('@/views/Alarm/AlarmRules.vue'),
            meta: { title: 'Alarm Rules' }
          },
          {
            path: 'alarm-correlation',
            name: 'AlarmCorrelation',
            component: () => import('@/views/Alarm/AlarmCorrelation.vue'),
            meta: { title: 'Alarm Correlation' }
          },
          {
            path: 'escalation-rules',
            name: 'EscalationRules',
            component: () => import('@/views/Alarm/EscalationRules.vue'),
            meta: { title: 'Escalation Rules' }
          },
          {
            path: 'notification-center',
            name: 'NotificationCenter',
            component: () => import('@/views/Alarm/NotificationCenter.vue'),
            meta: { title: 'Notification Center' }
          },
          {
            path: 'event-analytics',
            name: 'EventAnalytics',
            component: () => import('@/views/Alarm/EventAnalytics.vue'),
            meta: { title: 'Event Analytics' }
          }
        ]
      },

      // ==================== Fault Management ====================
      {
        path: 'fault-management',
        name: 'FaultManagement',
        redirect: '/fault-management/fault-dashboard',
        children: [
          {
            path: 'fault-dashboard',
            name: 'FaultDashboard',
            component: () => import('@/views/FaultManagement/FaultDashboard.vue'),
            meta: { title: 'Fault Dashboard' }
          },
          {
            path: 'active-faults',
            name: 'ActiveFaults',
            component: () => import('@/views/FaultManagement/ActiveFaults.vue'),
            meta: { title: 'Active Faults' }
          },
          {
            path: 'fault-history',
            name: 'FaultHistory',
            component: () => import('@/views/FaultManagement/FaultHistory.vue'),
            meta: { title: 'Fault History' }
          },
          {
            path: 'fault-correlation',
            name: 'FaultCorrelation',
            component: () => import('@/views/FaultManagement/FaultCorrelation.vue'),
            meta: { title: 'Fault Correlation' }
          },
          {
            path: 'root-cause-analysis',
            name: 'RootCauseAnalysis',
            component: () => import('@/views/FaultManagement/RootCauseAnalysis.vue'),
            meta: { title: 'Root Cause Analysis' }
          },
          {
            path: 'fault-rules-engine',
            name: 'FaultRulesEngine',
            component: () => import('@/views/FaultManagement/FaultRulesEngine.vue'),
            meta: { title: 'Fault Rules Engine' }
          },
          {
            path: 'fault-workflow',
            name: 'FaultWorkflow',
            component: () => import('@/views/FaultManagement/FaultWorkflow.vue'),
            meta: { title: 'Fault Workflow' }
          },
          {
            path: 'fault-analytics',
            name: 'FaultAnalytics',
            component: () => import('@/views/FaultManagement/FaultAnalytics.vue'),
            meta: { title: 'Fault Analytics' }
          },
          {
            path: 'knowledge-base',
            name: 'KnowledgeBase',
            component: () => import('@/views/FaultManagement/KnowledgeBase.vue'),
            meta: { title: 'Knowledge Base' }
          },
          {
            path: 'ai-fault-diagnosis',
            name: 'AIFaultDiagnosis',
            component: () => import('@/views/FaultManagement/AIFaultDiagnosis.vue'),
            meta: { title: 'AI Fault Diagnosis' }
          }
        ]
      },

      // ==================== Maintenance ====================
      {
        path: 'maintenance',
        name: 'Maintenance',
        redirect: '/maintenance/work-orders',
        children: [
          {
            path: 'work-orders',
            name: 'WorkOrders',
            component: () => import('@/views/Maintenance/WorkOrders.vue'),
            meta: { title: 'Work Orders' }
          },
          {
            path: 'dispatch-management',
            name: 'DispatchManagement',
            component: () => import('@/views/Maintenance/DispatchManagement.vue'),
            meta: { title: 'Dispatch Management' }
          },
          {
            path: 'inspection-management',
            name: 'InspectionManagement',
            component: () => import('@/views/Maintenance/InspectionManagement.vue'),
            meta: { title: 'Inspection Management' }
          },
          {
            path: 'preventive-maintenance',
            name: 'PreventiveMaintenance',
            component: () => import('@/views/Maintenance/PreventiveMaintenance.vue'),
            meta: { title: 'Preventive Maintenance' }
          },
          {
            path: 'predictive-maintenance',
            name: 'PredictiveMaintenance',
            component: () => import('@/views/Maintenance/PredictiveMaintenance.vue'),
            meta: { title: 'Predictive Maintenance' }
          },
          {
            path: 'asset-management',
            name: 'AssetManagement',
            component: () => import('@/views/Maintenance/AssetManagement.vue'),
            meta: { title: 'Asset Management' }
          },
          {
            path: 'spare-parts-management',
            name: 'SparePartsManagement',
            component: () => import('@/views/Maintenance/SparePartsManagement.vue'),
            meta: { title: 'Spare Parts Management' }
          },
          {
            path: 'vendor-management',
            name: 'VendorManagement',
            component: () => import('@/views/Maintenance/VendorManagement.vue'),
            meta: { title: 'Vendor Management' }
          },
          {
            path: 'sla-management',
            name: 'SLAManagement',
            component: () => import('@/views/Maintenance/SLAManagement.vue'),
            meta: { title: 'SLA Management' }
          },
          {
            path: 'maintenance-analytics',
            name: 'MaintenanceAnalytics',
            component: () => import('@/views/Maintenance/MaintenanceAnalytics.vue'),
            meta: { title: 'Maintenance Analytics' }
          }
        ]
      },

      // ==================== Energy & Sustainability ====================
      {
        path: 'energy-sustainability',
        name: 'EnergySustainability',
        redirect: '/energy-sustainability/electricity-monitoring',
        children: [
          {
            path: 'electricity-monitoring',
            name: 'ElectricityMonitoring',
            component: () => import('@/views/EnergySustainability/ElectricityMonitoring.vue'),
            meta: { title: 'Electricity Monitoring' }
          },
          {
            path: 'water-monitoring',
            name: 'WaterMonitoring',
            component: () => import('@/views/EnergySustainability/WaterMonitoring.vue'),
            meta: { title: 'Water Monitoring' }
          },
          {
            path: 'gas-monitoring',
            name: 'GasMonitoring',
            component: () => import('@/views/EnergySustainability/GasMonitoring.vue'),
            meta: { title: 'Gas Monitoring' }
          },
          {
            path: 'thermal-energy-monitoring',
            name: 'ThermalEnergyMonitoring',
            component: () => import('@/views/EnergySustainability/ThermalEnergyMonitoring.vue'),
            meta: { title: 'Thermal Energy Monitoring' }
          },
          {
            path: 'solar-monitoring',
            name: 'SolarMonitoring',
            component: () => import('@/views/EnergySustainability/SolarMonitoring.vue'),
            meta: { title: 'Solar Monitoring' }
          },
          {
            path: 'battery-storage',
            name: 'BatteryStorage',
            component: () => import('@/views/EnergySustainability/BatteryStorage.vue'),
            meta: { title: 'Battery Storage' }
          },
          {
            path: 'utility-billing',
            name: 'UtilityBilling',
            component: () => import('@/views/EnergySustainability/UtilityBilling.vue'),
            meta: { title: 'Utility Billing' }
          },
          {
            path: 'energy-analytics',
            name: 'EnergyAnalytics',
            component: () => import('@/views/EnergySustainability/EnergyAnalytics.vue'),
            meta: { title: 'Energy Analytics' }
          },
          {
            path: 'carbon-analytics',
            name: 'CarbonAnalytics',
            component: () => import('@/views/EnergySustainability/CarbonAnalytics.vue'),
            meta: { title: 'Carbon Analytics' }
          },
          {
            path: 'esg-dashboard-energy',
            name: 'ESGDashboardEnergy',
            component: () => import('@/views/EnergySustainability/ESGDashboard.vue'),
            meta: { title: 'ESG Dashboard' }
          }
        ]
      },

      // ==================== Facility Services ====================
      {
        path: 'facility-services',
        name: 'FacilityServices',
        redirect: '/facility-services/parking-management',
        children: [
          {
            path: 'parking-management',
            name: 'ParkingManagement',
            component: () => import('@/views/FacilityServices/ParkingManagement.vue'),
            meta: { title: 'Parking Management' }
          },
          {
            path: 'visitor-management',
            name: 'VisitorManagement',
            component: () => import('@/views/FacilityServices/VisitorManagement.vue'),
            meta: { title: 'Visitor Management' }
          },
          {
            path: 'meeting-room-booking',
            name: 'MeetingRoomBooking',
            component: () => import('@/views/FacilityServices/MeetingRoomBooking.vue'),
            meta: { title: 'Meeting Room Booking' }
          },
          {
            path: 'housekeeping-management',
            name: 'HousekeepingManagement',
            component: () => import('@/views/FacilityServices/HousekeepingManagement.vue'),
            meta: { title: 'Housekeeping Management' }
          },
          {
            path: 'waste-management',
            name: 'WasteManagement',
            component: () => import('@/views/FacilityServices/WasteManagement.vue'),
            meta: { title: 'Waste Management' }
          },
          {
            path: 'occupancy-analytics',
            name: 'OccupancyAnalytics',
            component: () => import('@/views/FacilityServices/OccupancyAnalytics.vue'),
            meta: { title: 'Occupancy Analytics' }
          },
          {
            path: 'facility-requests',
            name: 'FacilityRequests',
            component: () => import('@/views/FacilityServices/FacilityRequests.vue'),
            meta: { title: 'Facility Requests' }
          }
        ]
      },

      // ==================== Decision & Evidence ====================
      {
        path: 'decision-evidence',
        name: 'DecisionEvidence',
        redirect: '/decision-evidence/decision-dashboard',
        children: [
          {
            path: 'decision-dashboard',
            name: 'DecisionDashboard',
            component: () => import('@/views/DecisionEvidence/DecisionDashboard.vue'),
            meta: { title: 'Decision Dashboard' }
          },
          {
            path: 'decision-register',
            name: 'DecisionRegister',
            component: () => import('@/views/DecisionEvidence/DecisionRegister.vue'),
            meta: { title: 'Decision Register' }
          },
          {
            path: 'workflow-management',
            name: 'WorkflowManagement',
            component: () => import('@/views/DecisionEvidence/WorkflowManagement.vue'),
            meta: { title: 'Workflow Management' }
          },
          {
            path: 'decision-timeline',
            name: 'DecisionTimeline',
            component: () => import('@/views/DecisionEvidence/DecisionTimeline.vue'),
            meta: { title: 'Decision Timeline' }
          },
          {
            path: 'evidence-repository',
            name: 'EvidenceRepository',
            component: () => import('@/views/DecisionEvidence/EvidenceRepository.vue'),
            meta: { title: 'Evidence Repository' }
          },
          {
            path: 'audit-trail',
            name: 'AuditTrail',
            component: () => import('@/views/DecisionEvidence/AuditTrail.vue'),
            meta: { title: 'Audit Trail' }
          },
          {
            path: 'digital-signatures',
            name: 'DigitalSignatures',
            component: () => import('@/views/DecisionEvidence/DigitalSignatures.vue'),
            meta: { title: 'Digital Signatures' }
          },
          {
            path: 'lessons-learned',
            name: 'LessonsLearned',
            component: () => import('@/views/DecisionEvidence/LessonsLearned.vue'),
            meta: { title: 'Lessons Learned' }
          },
          {
            path: 'ai-recommendation-log',
            name: 'AIRecommendationLog',
            component: () => import('@/views/DecisionEvidence/AIRecommendationLog.vue'),
            meta: { title: 'AI Recommendation Log' }
          }
        ]
      },

      // ==================== Command Center ====================
      {
        path: 'command-center',
        name: 'CommandCenter',
        redirect: '/command-center/operations-dashboard',
        children: [
          {
            path: 'operations-dashboard',
            name: 'OperationsDashboard',
            component: () => import('@/views/CommandCenter/OperationsDashboard.vue'),
            meta: { title: 'Operations Dashboard' }
          },
          {
            path: 'gis-map',
            name: 'GISMap',
            component: () => import('@/views/CommandCenter/GISMap.vue'),
            meta: { title: 'GIS Map' }
          },
          {
            path: 'situation-awareness',
            name: 'SituationAwareness',
            component: () => import('@/views/CommandCenter/SituationAwareness.vue'),
            meta: { title: 'Situation Awareness' }
          },
          {
            path: 'incident-center',
            name: 'IncidentCenter',
            component: () => import('@/views/CommandCenter/IncidentCenter.vue'),
            meta: { title: 'Incident Center' }
          },
          {
            path: 'emergency-command',
            name: 'EmergencyCommand',
            component: () => import('@/views/CommandCenter/EmergencyCommand.vue'),
            meta: { title: 'Emergency Command' }
          },
          {
            path: 'resource-dispatch',
            name: 'ResourceDispatch',
            component: () => import('@/views/CommandCenter/ResourceDispatch.vue'),
            meta: { title: 'Resource Dispatch' }
          },
          {
            path: 'executive-dashboard',
            name: 'ExecutiveDashboard',
            component: () => import('@/views/CommandCenter/ExecutiveDashboard.vue'),
            meta: { title: 'Executive Dashboard' }
          }
        ]
      },

      // ==================== Intelligence ====================
      {
        path: 'intelligence',
        name: 'Intelligence',
        redirect: '/intelligence/ai-assistant',
        children: [
          {
            path: 'ai-assistant',
            name: 'AIAssistant',
            component: () => import('@/views/Intelligence/AIAssistant.vue'),
            meta: { title: 'AI Assistant' }
          },
          {
            path: 'predictive-maintenance-intel',
            name: 'PredictiveMaintenanceIntel',
            component: () => import('@/views/Intelligence/PredictiveMaintenance.vue'),
            meta: { title: 'Predictive Maintenance' }
          },
          {
            path: 'fault-diagnostics',
            name: 'FaultDiagnostics',
            component: () => import('@/views/Intelligence/FaultDiagnostics.vue'),
            meta: { title: 'Fault Diagnostics' }
          },
          {
            path: 'anomaly-detection',
            name: 'AnomalyDetection',
            component: () => import('@/views/Intelligence/AnomalyDetection.vue'),
            meta: { title: 'Anomaly Detection' }
          },
          {
            path: 'energy-optimization',
            name: 'EnergyOptimization',
            component: () => import('@/views/Intelligence/EnergyOptimization.vue'),
            meta: { title: 'Energy Optimization' }
          },
          {
            path: 'occupancy-forecast',
            name: 'OccupancyForecast',
            component: () => import('@/views/Intelligence/OccupancyForecast.vue'),
            meta: { title: 'Occupancy Forecast' }
          },
          {
            path: 'recommendation-center',
            name: 'RecommendationCenter',
            component: () => import('@/views/Intelligence/RecommendationCenter.vue'),
            meta: { title: 'Recommendation Center' }
          },
          {
            path: 'knowledge-graph',
            name: 'KnowledgeGraph',
            component: () => import('@/views/Intelligence/KnowledgeGraph.vue'),
            meta: { title: 'Knowledge Graph' }
          },
          {
            path: 'digital-operator',
            name: 'DigitalOperator',
            component: () => import('@/views/Intelligence/DigitalOperator.vue'),
            meta: { title: 'Digital Operator' }
          }
        ]
      },

      // ==================== AI Video Analytics ====================
      {
        path: 'ai-video-analytics',
        name: 'AIVideoAnalytics',
        redirect: '/ai-video-analytics/ppe-compliance',
        children: [
          {
            path: 'ppe-compliance',
            name: 'PPECompliance',
            component: () => import('@/views/AIVideoAnalytics/PPECompliance.vue'),
            meta: { title: 'PPE Compliance' }
          },
          {
            path: 'helmet-detection',
            name: 'HelmetDetection',
            component: () => import('@/views/AIVideoAnalytics/HelmetDetection.vue'),
            meta: { title: 'Helmet Detection' }
          },
          {
            path: 'fall-detection',
            name: 'FallDetection',
            component: () => import('@/views/AIVideoAnalytics/FallDetection.vue'),
            meta: { title: 'Fall Detection' }
          },
          {
            path: 'intrusion-detection',
            name: 'IntrusionDetection',
            component: () => import('@/views/AIVideoAnalytics/IntrusionDetection.vue'),
            meta: { title: 'Intrusion Detection' }
          },
          {
            path: 'smoke-detection',
            name: 'SmokeDetection',
            component: () => import('@/views/AIVideoAnalytics/SmokeDetection.vue'),
            meta: { title: 'Smoke Detection' }
          },
          {
            path: 'fire-detection',
            name: 'FireDetection',
            component: () => import('@/views/AIVideoAnalytics/FireDetection.vue'),
            meta: { title: 'Fire Detection' }
          },
          {
            path: 'vehicle-analytics',
            name: 'VehicleAnalytics',
            component: () => import('@/views/AIVideoAnalytics/VehicleAnalytics.vue'),
            meta: { title: 'Vehicle Analytics' }
          },
          {
            path: 'crowd-analytics',
            name: 'CrowdAnalytics',
            component: () => import('@/views/AIVideoAnalytics/CrowdAnalytics.vue'),
            meta: { title: 'Crowd Analytics' }
          },
          {
            path: 'anpr',
            name: 'ANPR',
            component: () => import('@/views/AIVideoAnalytics/ANPR.vue'),
            meta: { title: 'ANPR' }
          },
          {
            path: 'video-event-center',
            name: 'VideoEventCenter',
            component: () => import('@/views/AIVideoAnalytics/VideoEventCenter.vue'),
            meta: { title: 'Video Event Center' }
          }
        ]
      },

      // ==================== Digital Twin ====================
      {
        path: 'digital-twin',
        name: 'DigitalTwin',
        redirect: '/digital-twin/bim-viewer',
        children: [
          {
            path: 'bim-viewer',
            name: 'BIMViewer',
            component: () => import('@/views/DigitalTwin/BIMViewer.vue'),
            meta: { title: 'BIM Viewer' }
          },
          {
            path: 'asset-localization',
            name: 'AssetLocalization',
            component: () => import('@/views/DigitalTwin/AssetLocalization.vue'),
            meta: { title: 'Asset Localization' }
          },
          {
            path: '3d-navigation',
            name: 'ThreeDNavigation',
            component: () => import('@/views/DigitalTwin/ThreeDNavigation.vue'),
            meta: { title: '3D Navigation' }
          },
          {
            path: 'real-time-twin',
            name: 'RealTimeTwin',
            component: () => import('@/views/DigitalTwin/RealTimeTwin.vue'),
            meta: { title: 'Real-Time Twin' }
          },
          {
            path: 'scenario-simulation',
            name: 'ScenarioSimulation',
            component: () => import('@/views/DigitalTwin/ScenarioSimulation.vue'),
            meta: { title: 'Scenario Simulation' }
          },
          {
            path: 'energy-simulation',
            name: 'EnergySimulation',
            component: () => import('@/views/DigitalTwin/EnergySimulation.vue'),
            meta: { title: 'Energy Simulation' }
          },
          {
            path: 'emergency-simulation',
            name: 'EmergencySimulation',
            component: () => import('@/views/DigitalTwin/EmergencySimulation.vue'),
            meta: { title: 'Emergency Simulation' }
          },
          {
            path: 'twin-analytics',
            name: 'TwinAnalytics',
            component: () => import('@/views/DigitalTwin/TwinAnalytics.vue'),
            meta: { title: 'Twin Analytics' }
          }
        ]
      },

      // ==================== Reports ====================
      {
        path: 'reports',
        name: 'Reports',
        redirect: '/reports/daily-reports',
        children: [
          {
            path: 'daily-reports',
            name: 'DailyReports',
            component: () => import('@/views/Report/DailyReports.vue'),
            meta: { title: 'Daily Reports' }
          },
          {
            path: 'weekly-reports',
            name: 'WeeklyReports',
            component: () => import('@/views/Report/WeeklyReports.vue'),
            meta: { title: 'Weekly Reports' }
          },
          {
            path: 'monthly-reports',
            name: 'MonthlyReports',
            component: () => import('@/views/Report/MonthlyReports.vue'),
            meta: { title: 'Monthly Reports' }
          },
          {
            path: 'annual-reports',
            name: 'AnnualReports',
            component: () => import('@/views/Report/AnnualReports.vue'),
            meta: { title: 'Annual Reports' }
          },
          {
            path: 'scheduled-reports',
            name: 'ScheduledReports',
            component: () => import('@/views/Report/ScheduledReports.vue'),
            meta: { title: 'Scheduled Reports' }
          },
          {
            path: 'custom-reports',
            name: 'CustomReports',
            component: () => import('@/views/Report/CustomReports.vue'),
            meta: { title: 'Custom Reports' }
          },
          {
            path: 'bi-reports',
            name: 'BIReports',
            component: () => import('@/views/Report/BIReports.vue'),
            meta: { title: 'BI Reports' }
          },
          {
            path: 'pdf-export',
            name: 'PDFExport',
            component: () => import('@/views/Report/PDFExport.vue'),
            meta: { title: 'PDF Export' }
          },
          {
            path: 'excel-export',
            name: 'ExcelExport',
            component: () => import('@/views/Report/ExcelExport.vue'),
            meta: { title: 'Excel Export' }
          }
        ]
      },

      // ==================== Trust & Identity ====================
      {
        path: 'trust-identity',
        name: 'TrustIdentity',
        redirect: '/trust-identity/did-identity-center',
        children: [
          {
            path: 'did-identity-center',
            name: 'DIDIdentityCenter',
            component: () => import('@/views/TrustIdentity/DIDIdentityCenter.vue'),
            meta: { title: 'DID Identity Center' }
          },
          {
            path: 'credential-center',
            name: 'CredentialCenter',
            component: () => import('@/views/TrustIdentity/CredentialCenter.vue'),
            meta: { title: 'Credential Center' }
          },
          {
            path: 'verifiable-credentials',
            name: 'VerifiableCredentials',
            component: () => import('@/views/TrustIdentity/VerifiableCredentials.vue'),
            meta: { title: 'Verifiable Credentials' }
          },
          {
            path: 'blockchain-anchoring',
            name: 'BlockchainAnchoring',
            component: () => import('@/views/TrustIdentity/BlockchainAnchoring.vue'),
            meta: { title: 'Blockchain Anchoring' }
          },
          {
            path: 'smart-contracts',
            name: 'SmartContracts',
            component: () => import('@/views/TrustIdentity/SmartContracts.vue'),
            meta: { title: 'Smart Contracts' }
          },
          {
            path: 'decision-traceability',
            name: 'DecisionTraceability',
            component: () => import('@/views/TrustIdentity/DecisionTraceability.vue'),
            meta: { title: 'Decision Traceability' }
          },
          {
            path: 'trust-audit-logs',
            name: 'TrustAuditLogs',
            component: () => import('@/views/TrustIdentity/TrustAuditLogs.vue'),
            meta: { title: 'Trust Audit Logs' }
          }
        ]
      },

      // ==================== Administration ====================
      {
        path: 'administration',
        name: 'Administration',
        redirect: '/administration/user-management',
        children: [
          {
            path: 'user-management',
            name: 'UserManagement',
            component: () => import('@/views/Administration/UserManagement.vue'),
            meta: { title: 'User Management' }
          },
          {
            path: 'role-management',
            name: 'RoleManagement',
            component: () => import('@/views/Administration/RoleManagement.vue'),
            meta: { title: 'Role Management' }
          },
          {
            path: 'permission-management',
            name: 'PermissionManagement',
            component: () => import('@/views/Administration/PermissionManagement.vue'),
            meta: { title: 'Permission Management' }
          },
          {
            path: 'edition-management',
            name: 'EditionManagement',
            component: () => import('@/views/Administration/EditionManagement.vue'),
            meta: { title: 'Edition Management' }
          },
          {
            path: 'license-management',
            name: 'LicenseManagement',
            component: () => import('@/views/Administration/LicenseManagement.vue'),
            meta: { title: 'License Management' }
          },
          {
            path: 'integration-settings',
            name: 'IntegrationSettings',
            component: () => import('@/views/Administration/IntegrationSettings.vue'),
            meta: { title: 'Integration Settings' }
          },
          {
            path: 'notification-settings',
            name: 'NotificationSettings',
            component: () => import('@/views/Administration/NotificationSettings.vue'),
            meta: { title: 'Notification Settings' }
          },
          {
            path: 'system-settings',
            name: 'SystemSettings',
            component: () => import('@/views/Administration/SystemSettings.vue'),
            meta: { title: 'System Settings' }
          },
          {
            path: 'audit-logs',
            name: 'AuditLogs',
            component: () => import('@/views/Administration/AuditLogs.vue'),
            meta: { title: 'Audit Logs' }
          },
          {
            path: 'oem-branding',
            name: 'OEMBranding',
            component: () => import('@/views/Administration/OEMBranding.vue'),
            meta: { title: 'OEM Branding' }
          }
        ]
      },

      //   05-26 newest
      // {
      //   path: '',
      //   name: 'Dashboard',
      //   component: () => import('../views/Home/System.vue'),
      //   meta: { title: 'Dashboard' }
      // },
      // {
      //   path: 'control',
      //   name: 'QuickControl',
      //   component: () => import('../views/Operations/Control.vue'),
      //   meta: { title: 'Quick Control' }
      // },
      // {
      //   path: 'sites',
      //   name: 'Sites',
      //   redirect: '/sites/Factory',
      //   children: [
      //     {
      //       path: 'Factory',
      //       name: 'Factory',
      //       component: () => import('@/views/Sites/Factory.vue'),
      //       meta: { title: 'Factory Sites' }
      //     },
      //     {
      //       path: 'Building',
      //       name: 'Building',
      //       component: () => import('@/views/Sites/Building.vue'),
      //       meta: { title: 'Building Sites' }
      //     },
      //     {
      //       path: 'Airport',
      //       name: 'Airport',
      //       component: () => import('@/views/Sites/Airport.vue'),
      //       meta: { title: 'Airport Sites' }
      //     },
      //     {
      //       path: 'Shopping',
      //       name: 'Shopping',
      //       component: () => import('@/views/Sites/Shopping.vue'),
      //       meta: { title: 'Shopping Sites' }
      //     },
      //     {
      //       path: 'Hospital',
      //       name: 'Hospital',
      //       component: () => import('@/views/Sites/Hospital.vue'),
      //       meta: { title: 'Hospital Sites' }
      //     },
      //     {
      //       path: 'Hotel',
      //       name: 'Hotel',
      //       component: () => import('@/views/Sites/Hotel.vue'),
      //       meta: { title: 'Hotel Sites' }
      //     }
      //   ]
      // },
      // {
      //   path: 'device',
      //   name: 'Device',
      //   redirect: '/device/area-topology',
      //   children: [
      //     {
      //       path: 'area-topology',
      //       name: 'AreaTopology',
      //       component: () => import('../views/Device/AreaTopology.vue'),
      //       meta: { title: 'Area Topology' }
      //     },
      //     {
      //       path: 'protocol',
      //       name: 'Protocol Hub',
      //       component: () => import('../views/Device/ProtocolHub.vue'),
      //       meta: { title: 'Protocol Hub' }
      //     },
      //     {
      //       path: 'cctv',
      //       name: 'DeviceCCTV',
      //       component: () => import('../views/Device/DeviceCCTV.vue'),
      //       meta: { title: 'DeviceCCTV Management' }
      //     },
      //     {
      //       path: 'hvac',
      //       name: 'DeviceHVAC',
      //       component: () => import('../views/Device/DeviceHVAC.vue'),
      //       meta: { title: 'HVAC Management' }
      //     },
      //     {
      //       path: 'access',
      //       name: 'Access',
      //       component: () => import('../views/Device/DeviceAccess.vue'),
      //       meta: { title: 'Access Management' }
      //     },
      //     {
      //       path: 'sas',
      //       name: 'DeviceSAS',
      //       component: () => import('../views/Device/DeviceSAS.vue'),
      //       meta: { title: 'Security Access System' }
      //     },
      //     {
      //       path: 'fas',
      //       name: 'DeviceFAS',
      //       component: () => import('../views/Device/DeviceFAS.vue'),
      //       meta: { title: 'Fire Alarm System' }
      //     },
      //     {
      //       path: 'lighting',
      //       name: 'DeviceLighting',
      //       component: () => import('../views/Device/DeviceLighting.vue'),
      //       meta: { title: 'Lighting Control System' }
      //     },
      //     {
      //       path: 'plumbing',
      //       name: 'DevicePlumbing',
      //       component: () => import('../views/Device/DevicePlumbing.vue'),
      //       meta: { title: 'Plumbing System' }
      //     }
      //   ]
      // },
      // {
      //   path: 'energy',
      //   name: 'Energy',
      //   redirect: '/energy/wind',
      //   children: [
      //
      //     {
      //       path: 'overview',
      //       name: 'Energy Overview',
      //       component: () => import('../views/Energy/Overview.vue'),
      //       meta: { title: 'Energy Overview' }
      //     },
      //     {
      //       path: 'wind',
      //       name: 'Wind',
      //       component: () => import('../views/Energy/Wind.vue'),
      //       meta: { title: 'Wind Energy Analysis' }
      //     },
      //     {
      //       path: 'solar',
      //       name: 'Solar',
      //       component: () => import('../views/Energy/Solar.vue'),
      //       meta: { title: 'Solar Energy Analysis' }
      //     },
      //     {
      //       path: 'electricity',
      //       name: 'Electricity',
      //       component: () => import('../views/Energy/Electricity.vue'),
      //       meta: { title: 'Power Grid & Consumption' }
      //     },
      //     {
      //       path: 'waste',
      //       name: 'WasteToEnergy',
      //       component: () => import('../views/Energy/WasteToEnergy.vue'),
      //       meta: { title: 'Waste-to-Energy Recovery' }
      //     },
      //     {
      //       path: 'hydrogen',
      //       name: 'Hydrogen',
      //       component: () => import('../views/Energy/Hydrogen.vue'),
      //       meta: { title: 'Hydrogen Energy Production' }
      //     },
      //     {
      //       path: 'storage',
      //       name: 'Storage',
      //       component: () => import('../views/Energy/EnergyStorage.vue'),
      //       meta: { title: 'Energy Storage Systems' }
      //     },
      //     {
      //       path: 'geothermal',
      //       name: 'Geothermal',
      //       component: () => import('../views/Energy/Geothermal.vue'),
      //       meta: { title: 'Geothermal Energy' }
      //     },
      //     {
      //       path: 'carbon',
      //       name: 'Carbon Emission',
      //       component: () => import('../views/Energy/Carbon.vue'),
      //       meta: { title: 'Carbon Emission' }
      //     },
      //     {
      //       path: 'savings',
      //       name: 'Energy Savings',
      //       component: () => import('../views/Energy/Savings.vue'),
      //       meta: { title: 'Energy Savings' }
      //     }
      //   ]
      // },
      // {
      //   path: 'property',
      //   name: 'Smart Property',
      //   redirect: '/property/parking',
      //   children: [
      //     {
      //       path: 'parking',
      //       name: 'Parking',
      //       component: () => import('../views/Property/Parking.vue'),
      //       meta: { title: 'Parking Management' }
      //     },
      //     {
      //       path: 'visitor',
      //       name: 'Visitor',
      //       component: () => import('../views/Property/Visitor.vue'),
      //       meta: { title: 'Visitor Management' }
      //     },
      //     {
      //       path: 'space',
      //       name: 'Space',
      //       component: () => import('../views/Property/Space.vue'),
      //       meta: { title: 'Space & Workspace Management' }
      //     },
      //     {
      //       path: 'waste',
      //       name: 'Waste',
      //       component: () => import('../views/Property/Waste.vue'),
      //       meta: { title: 'Waste Collection Management' }
      //     }
      //   ]
      // },
      // {
      //   path: 'blockchain',
      //   name: 'Blockchain Services',
      //   redirect: '/blockchain/node',
      //   children: [
      //     {
      //       path: 'node',
      //       name: 'NodeDetail',
      //       component: () => import('../views/Blockchain/NodeDetail.vue'),
      //       meta: { title: 'Node Management' }
      //     },
      //     {
      //       path: 'web3',
      //       name: 'Web3Services',
      //       component: () => import('../views/Blockchain/Web3Services.vue'),
      //       meta: { title: 'Web3 Services' }
      //     },
      //     {
      //       path: 'did',
      //       name: 'DIDManagement',
      //       component: () => import('../views/Blockchain/DIDManagement.vue'),
      //       meta: { title: 'DID Management' }
      //     },
      //     {
      //       path: 'introduction',
      //       name: 'Introduction',
      //       component: () => import('../views/Blockchain/Introduction.vue'),
      //       meta: { title: 'Web3 Introduction' }
      //     },
      //     {
      //       path: 'contracts',
      //       name: 'Smart Contracts',
      //       component: () => import('../views/Blockchain/Contracts.vue'),
      //       meta: { title: 'Smart Contracts' }
      //     },
      //     {
      //       path: 'anchoring',
      //       name: 'Blockchain Anchoring',
      //       component: () => import('../views/Blockchain/Anchoring.vue'),
      //       meta: { title: 'Blockchain Anchoring' }
      //     },
      //     {
      //       path: 'api',
      //       name: 'API Management',
      //       component: () => import('../views/Blockchain/APIManagement.vue'),
      //       meta: { title: 'API Management' }
      //     },
      //     {
      //       path: 'edge-nodes',
      //       name: 'Edge Nodes',
      //       component: () => import('../views/Blockchain/EdgeNodes.vue'),
      //       meta: { title: 'Edge Nodes' }
      //     }
      //   ]
      // },
      // {
      //   path: 'alarm',
      //   name: 'Alarm Center',
      //   redirect: '/maintain/predictive',
      //   children: [
      //     {
      //       path: 'index',
      //       name: 'Alarm',
      //       component: () => import('../views/Alarm/Alarm.vue'),
      //       meta: { title: 'Alarm Center' }
      //     },
      //     {
      //       path: 'notify',
      //       name: 'Notify',
      //       component: () => import('../views/Alarm/Notification.vue'),
      //       meta: { title: 'Multi‑dim Notification' }
      //     },
      //     {
      //       path: 'history',
      //       name: 'History',
      //       component: () => import('../views/Alarm/History.vue'),
      //       meta: { title: 'History' }
      //     }
      //   ]
      // },
      // {
      //   path: 'maintain',
      //   name: 'Maintenance Management',
      //   redirect: '/maintain/predictive',
      //   children: [
      //     {
      //       path: 'predictive',
      //       name: 'Predictive',
      //       component: () => import('../views/Maintain/Predictive.vue'),
      //       meta: { title: 'Predictive Maintenance' }
      //     }
      //   ]
      // },
      // {
      //   path: 'report',
      //   name: 'Report',
      //   redirect: '/report/energy',
      //   children: [
      //     {
      //       path: 'data',
      //       name: 'Data Reports',
      //       component: () => import('../views/Report/Report.vue'),
      //       meta: { title: 'Data Reports' }
      //     },
      //     {
      //       path: 'energy',
      //       name: 'Energy Reports',
      //       component: () => import('../views/Report/Energy.vue'),
      //       meta: { title: 'Energy Reports' }
      //     },
      //     {
      //       path: 'device',
      //       name: 'Device Reports',
      //       component: () => import('../views/Report/Device.vue'),
      //       meta: { title: 'Device Reports' }
      //     },
      //     {
      //       path: 'maintenance',
      //       name: ' Maintenance Reports',
      //       component: () => import('../views/Report/Maintenance.vue'),
      //       meta: { title: 'Maintenance Reports' }
      //     },
      //     {
      //       path: 'carbon',
      //       name: 'Carbon Reports',
      //       component: () => import('../views/Report/Carbon.vue'),
      //       meta: { title: 'Carbon Reports' }
      //     }
      //   ]
      // },
      // {
      //   path: 'support',
      //   name: 'System Support',
      //   redirect: '/support/mobile',
      //   children: [
      //     {
      //       path: 'mobile',
      //       name: 'Mobile Terminal',
      //       component: () => import('../views/Support/Mobile.vue'),
      //       meta: { title: 'Mobile Terminal' }
      //     }
      //   ]
      // },
      // {
      //   path: 'administration1',
      //   name: 'Administration',
      //   redirect: '/administration/user',
      //   children: [
      //     {
      //       path: 'user',
      //       name: 'User Management',
      //       component: () => import('../views/Administration/UserManagement.vue'),
      //       meta: { title: 'User Management' }
      //     },
      //     {
      //       path: 'role',
      //       name: 'Role Management',
      //       component: () => import('../views/Administration/RoleManagement.vue'),
      //       meta: { title: 'Role Management' }
      //     },
      //     {
      //       path: 'permission',
      //       name: 'Permission Management',
      //       component: () => import('../views/Administration/PermissionManagement.vue'),
      //       meta: { title: 'Permission Management' }
      //     },
      //     {
      //       path: 'system',
      //       name: 'System Configuration',
      //       component: () => import('../views/Administration/System.vue'),
      //       meta: { title: 'System Configuration' }
      //     },
      //     {
      //       path: 'license',
      //       name: 'License Management',
      //       component: () => import('../views/Administration/LicenseManagement.vue'),
      //       meta: { title: 'License Management' }
      //     },
      //     {
      //       path: 'edition',
      //       name: 'Edition Management',
      //       component: () => import('../views/Administration/EditionManagement.vue'),
      //       meta: { title: 'Edition Management' }
      //     }
      //   ]
      // },
      // {
      //   path: 'prediction',
      //   name: 'AI Prediction',
      //   redirect: '/prediction/hvac',
      //   children: [
      //     {
      //       path: 'hvac',
      //       name: 'Hvac Prediction',
      //       component: () => import('../views/Prediction/Hvac.vue'),
      //       meta: { title: 'Hvac Prediction' }
      //     },
      //     {
      //       path: 'lighting',
      //       name: 'Lighting Prediction',
      //       component: () => import('../views/Prediction/Lighting.vue'),
      //       meta: { title: 'Lighting Prediction' }
      //     },
      //     {
      //       path: 'power-socket',
      //       name: 'Power & Socket',
      //       component: () => import('../views/Prediction/Power.vue'),
      //       meta: { title: 'Power & Socket' }
      //     },
      //     {
      //       path: 'ev-charging',
      //       name: 'EV Charging',
      //       component: () => import('../views/Prediction/EVCharging.vue'),
      //       meta: { title: 'EV Charging' }
      //     },
      //     {
      //       path: 'renewable',
      //       name: 'Renewable Generation',
      //       component: () => import('../views/Prediction/Renewable.vue'),
      //       meta: { title: 'Renewable Generation' }
      //     },
      //     {
      //       path: 'storage',
      //       name: 'Storage Strategy',
      //       component: () => import('../views/Prediction/Storage.vue'),
      //       meta: { title: 'Storage Strategy' }
      //     }
      //   ]
      // },
      // {
      //   path: 'settings',
      //   name: 'System Settings',
      //   redirect: '/settings/voice-cmd',
      //   children: [
      //     {
      //       path: 'voice-cmd',
      //       name: 'Voice Command Settings',
      //       component: () => import('../views/Settings/Voice.vue'),
      //       meta: { title: 'Voice Command Settings' }
      //     },
      //     {
      //       path: 'tts-rule',
      //       name: 'TTS Broadcast Rules',
      //       component: () => import('../views/Settings/Rules.vue'),
      //       meta: { title: 'TTS Broadcast Rulesn' }
      //     },
      //     {
      //       path: 'lang',
      //       name: 'Multi-language Pack',
      //       component: () => import('../views/Settings/Language.vue'),
      //       meta: { title: 'Multi-language Pack' }
      //     },
      //     {
      //       path: 'voice-log',
      //       name: 'Voice Training Logs',
      //       component: () => import('../views/Settings/VoiceTraining.vue'),
      //       meta: { title: 'Voice Training Logs' }
      //     }
      //   ]
      // },
      // {
      //   path: 'settings',
      //   name: 'Settings',
      //   component: () => import('../views/Settings/Settings.vue'),
      //   meta: { title: 'System Settings' }
      // },
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