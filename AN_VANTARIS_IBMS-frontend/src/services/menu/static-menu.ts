import type { AppMenuItem, AppMenuL3Item } from './types'

type MenuDomainInput = {
  id: string
  label: string
  path: string
  icon: string
  children: Array<{
    id: string
    label: string
    path: string
    status?: AppMenuL3Item['status']
    l3: string[]
    mappedExistingModule?: string
  }>
}

function l3Items(labels: string[], mappedExistingModule?: string, status: AppMenuL3Item['status'] = 'planned'): AppMenuL3Item[] {
  return labels.map((label, index) => ({
    id: `${label.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '')}-${index + 1}`,
    label,
    status,
    mappedExistingModule,
    disabled: status !== 'implemented' && status !== 'mapped',
  }))
}

const domains: MenuDomainInput[] = [
  {
    id: 'dashboard',
    label: 'Dashboard',
    path: '/dashboard',
    icon: 'D',
    children: [
      { id: 'dashboard-executive', label: 'Executive Dashboard', path: '/dashboard', status: 'mapped', l3: ['Portfolio Overview', 'Site Health', 'Critical Alarms', 'Open Faults', 'Open Work Orders', 'Energy Exceptions', 'ESG Snapshot', 'Service Risk', 'Customer Demo View'] },
      { id: 'dashboard-operations', label: 'Operations Dashboard', path: '/dashboard', status: 'mapped', l3: ["Today's Operations", 'Live Situation', 'Risk Summary', 'System Availability', 'Fault Impact', 'Maintenance Status', 'Energy Status', 'Compliance Status'] },
      { id: 'dashboard-my', label: 'My Dashboard', path: '/dashboard', status: 'planned', l3: ['My Tasks', 'My Alarms', 'My Work Orders', 'My Approvals', 'My Reports', 'My Evidence', 'Recent Activity'] },
      { id: 'dashboard-scenario', label: 'Scenario Dashboard', path: '/dashboard', status: 'mapped', l3: ['UMMS Overview', 'UFMS Overview', 'UESG Overview', 'Airport Scenario', 'Data Center Scenario', 'Customer Demo Scenario'] },
    ],
  },
  {
    id: 'operations-command',
    label: 'Operations Command',
    path: '/console/operations',
    icon: 'O',
    children: [
      { id: 'operations-command-center', label: 'Command Center', path: '/console/operations', status: 'mapped', l3: ['Live Situation', 'Site Map', 'Alarm Heatmap', 'Fault Heatmap', 'Critical Assets', 'Active Incidents', 'Operator Notes', 'Shift Handover'] },
      { id: 'operations-console', label: 'Operations Console', path: '/console/operations', status: 'implemented', l3: ['Operations Board', 'Event Stream', 'Active Tasks', 'Escalations', 'Service Impact', 'Evidence Timeline', 'Decision Log'], mappedExistingModule: 'PlatformOperationsDashboard' },
      { id: 'incident-management', label: 'Incident Management', path: '/console/operations', status: 'planned', l3: ['Active Incidents', 'Incident Details', 'Related Alarms', 'Related Faults', 'Impacted Assets', 'Response Actions', 'Communications', 'Closure Evidence'] },
      { id: 'shift-management', label: 'Shift Management', path: '/console/operations', status: 'planned', l3: ['Shift Dashboard', 'Handover Notes', 'Open Items', 'Critical Watchlist', 'Operator Assignments', 'Shift Evidence'] },
    ],
  },
  {
    id: 'sites-spaces',
    label: 'Sites & Spaces',
    path: '/assets/topology',
    icon: 'S',
    children: [
      { id: 'site-portfolio', label: 'Site Portfolio', path: '/assets/topology', status: 'mapped', l3: ['Portfolio List', 'Site Health', 'Site Risk', 'Site Energy', 'Site Compliance', 'Site Reports'] },
      { id: 'buildings', label: 'Buildings', path: '/assets/topology', status: 'planned', l3: ['Building List', 'Building Overview', 'Building Systems', 'Building Alarms', 'Building Faults', 'Building Energy', 'Building Evidence'] },
      { id: 'floors-zones', label: 'Floors & Zones', path: '/assets/topology', status: 'planned', l3: ['Floor Plan', 'Zone List', 'Zone Conditions', 'Zone Assets', 'Zone Alarms', 'Zone Energy', 'Occupancy View'] },
      { id: 'rooms-areas', label: 'Rooms & Areas', path: '/assets/topology', status: 'planned', l3: ['Room List', 'Room Conditions', 'Room Equipment', 'Room Events', 'Room Comfort', 'Room Maintenance'] },
      { id: 'space-mapping', label: 'Space Mapping', path: '/assets/topology', status: 'mapped', l3: ['Asset-to-Space Mapping', 'System-to-Space Mapping', 'Tag-to-Space Mapping', 'Floor Plan Binding', 'Mapping Gaps', 'Mapping Evidence'] },
    ],
  },
  {
    id: 'systems-assets',
    label: 'Systems & Assets',
    path: '/assets/topology',
    icon: 'A',
    children: [
      { id: 'system-registry', label: 'System Registry', path: '/assets/topology', status: 'mapped', l3: ['System List', 'System Topology', 'System Health', 'System Alarms', 'System Faults', 'System Evidence', 'System Reports'] },
      { id: 'asset-registry', label: 'Asset Registry', path: '/one/assets/context', status: 'implemented', l3: ['Asset List', 'Asset Detail', 'Asset Context', 'Asset Relationships', 'Asset Health', 'Asset History', 'Asset Evidence'], mappedExistingModule: 'AssetContext' },
      { id: 'equipment', label: 'Equipment', path: '/assets/topology', status: 'mapped', l3: ['Equipment List', 'Equipment Detail', 'Runtime Status', 'Maintenance History', 'Fault History', 'Spare / Vendor Info', 'Evidence'] },
      { id: 'points-tags', label: 'Points & Tags', path: '/assets/topology', status: 'planned', l3: ['Point List', 'Tag Mapping', 'Live Values', 'Point Quality', 'Point Trends', 'Mapping Gaps', 'Import / Export'] },
      { id: 'controllers-gateways', label: 'Controllers & Gateways', path: '/uedge/diagnostics', status: 'mapped', l3: ['Controller List', 'Gateway List', 'Connectivity Status', 'Protocol Status', 'Edge Gateway Mapping', 'Link Gateway Mapping', 'Diagnostics'] },
      { id: 'asset-graph', label: 'Asset Graph', path: '/one/assets/context', status: 'implemented', l3: ['Relationship Graph', 'Dependency View', 'Impact Path', 'Upstream / Downstream', 'Asset Context Projection', 'Evidence Links', 'Data Quality'], mappedExistingModule: 'AssetContext' },
    ],
  },
  {
    id: 'alarms-events',
    label: 'Alarms & Events',
    path: '/one/airport/alarms-events',
    icon: 'E',
    children: [
      { id: 'alarm-console', label: 'Alarm Console', path: '/one/airport/alarms-events', status: 'mapped', l3: ['Active Alarms', 'Critical Alarms', 'Acknowledgement', 'Shelving', 'Suppression', 'Escalation', 'Operator Notes'] },
      { id: 'event-timeline', label: 'Event Timeline', path: '/one/airport/alarms-events', status: 'mapped', l3: ['Event Stream', 'Event Filters', 'Event Detail', 'Related Assets', 'Related Faults', 'Related Work Orders', 'Evidence Timeline'] },
      { id: 'alarm-rules', label: 'Alarm Rules', path: '/one/airport/alarms-events', status: 'planned', l3: ['Priority Rules', 'Escalation Rules', 'Notification Rules', 'Suppression Rules', 'Routing Rules', 'Rule Evidence', 'Rule Audit'] },
      { id: 'alarm-analytics', label: 'Alarm Analytics', path: '/one/airport/alarms-events', status: 'planned', l3: ['Alarm Volume', 'Alarm Flood', 'Repeated Alarms', 'Nuisance Alarms', 'Top Assets', 'Top Systems', 'SLA Impact'] },
      { id: 'event-evidence', label: 'Event Evidence', path: '/ucde/evidence', status: 'mapped', l3: ['Evidence Chain', 'UCDE Trace', 'Operator Actions', 'Export Package', 'Audit Trail'] },
    ],
  },
  {
    id: 'ufms',
    label: 'UFMS - Fault Management',
    path: '/one/airport/fault-cases',
    icon: 'F',
    children: [
      { id: 'fault-console', label: 'Fault Console', path: '/one/airport/fault-cases', status: 'mapped', l3: ['Active Faults', 'Critical Faults', 'Fault Detail', 'Correlation', 'Root Cause Analysis', 'Recommended Actions', 'Fault Evidence'] },
      { id: 'detection-correlation', label: 'Detection & Correlation', path: '/one/airport/fault-cases', status: 'planned', l3: ['Detection Rules', 'Correlation Rules', 'Event Clustering', 'Related Alarms', 'Related Assets', 'Confidence Score', 'Rule Evidence'] },
      { id: 'diagnostics', label: 'Diagnostics', path: '/console/foundation-diagnostics/workspace', status: 'mapped', l3: ['Diagnostic Queue', 'System Diagnostics', 'Asset Diagnostics', 'OT / Network Diagnostics', 'Hardware Diagnostics', 'Diagnostic Evidence', 'Diagnostic History'] },
      { id: 'remediation', label: 'Remediation', path: '/one/airport/fault-cases', status: 'planned', l3: ['Recommended Actions', 'Manual Actions', 'Work Order Creation', 'Escalation', 'SLA Tracking', 'Closure Notes', 'Closure Evidence'] },
      { id: 'fault-analytics', label: 'Fault Analytics', path: '/one/airport/fault-cases', status: 'planned', l3: ['Fault Trends', 'Top Fault Types', 'Repeat Faults', 'MTTR', 'Downtime Impact', 'Reliability Score', 'Improvement Actions'] },
      { id: 'ufms-configuration', label: 'UFMS Configuration', path: '/one/airport/fault-cases', status: 'planned', l3: ['Fault Categories', 'Severity Model', 'Correlation Model', 'Escalation Matrix', 'Notification Policy', 'Evidence Policy', 'Integration Mapping'] },
    ],
  },
  {
    id: 'umms',
    label: 'UMMS - Maintenance Management',
    path: '/one/umms/workspace',
    icon: 'M',
    children: [
      { id: 'work-orders', label: 'Work Orders', path: '/one/umms/workspace', status: 'implemented', l3: ['Open Work Orders', 'Assigned Work Orders', 'Emergency Work Orders', 'Fault-linked Work Orders', 'Preventive Work Orders', 'Corrective Work Orders', 'Work Order Detail', 'Closure Evidence'], mappedExistingModule: 'UmmsMaintenance' },
      { id: 'preventive-maintenance', label: 'Preventive Maintenance', path: '/one/umms/workspace', status: 'implemented', l3: ['PM Calendar', 'PM Templates', 'PM Schedule', 'PM Checklist', 'PM Completion', 'PM Evidence', 'PM Reports'], mappedExistingModule: 'UmmsMaintenance' },
      { id: 'corrective-maintenance', label: 'Corrective Maintenance', path: '/one/umms/workspace', status: 'implemented', l3: ['Fault-linked Work Orders', 'Manual Work Orders', 'Technician Assignment', 'Action Tracking', 'Parts / Vendor Notes', 'Closure Review', 'History'], mappedExistingModule: 'UmmsMaintenance' },
      { id: 'sla-escalation', label: 'SLA & Escalation', path: '/one/umms/workspace', status: 'implemented', l3: ['SLA Dashboard', 'Breach Risk', 'Escalation Queue', 'Supervisor Review', 'Customer Impact', 'SLA Evidence', 'Aging Buckets'], mappedExistingModule: 'UmmsMaintenance' },
      { id: 'maintenance-analytics', label: 'Maintenance Analytics', path: '/one/umms/workspace', status: 'implemented', l3: ['MTTR', 'MTBF', 'Repeated Failures', 'Technician Load', 'Asset Reliability', 'Predictive Risk', 'Improvement Plan'], mappedExistingModule: 'UmmsMaintenance' },
      { id: 'maintenance-configuration', label: 'Maintenance Configuration', path: '/one/umms/workspace', status: 'implemented', l3: ['Work Order Types', 'Priority Matrix', 'Assignment Rules', 'Checklist Templates', 'SLA Rules', 'Vendor / Team Setup', 'Evidence Rules'], mappedExistingModule: 'UmmsMaintenance' },
    ],
  },
  {
    id: 'uesg',
    label: 'UESG - Energy & Sustainability',
    path: '/uesg/sustainability',
    icon: 'G',
    children: [
      { id: 'energy-dashboard', label: 'Energy Dashboard', path: '/uesg/sustainability', status: 'implemented', l3: ['Consumption Overview', 'Demand / Peak', 'Energy Intensity', 'Meter Health', 'Energy Exceptions', 'Energy Forecast', 'Energy Reports'], mappedExistingModule: 'UesgSustainability' },
      { id: 'metering', label: 'Metering', path: '/uesg/sustainability', status: 'planned', l3: ['Meter List', 'Meter Mapping', 'Meter Readings', 'Meter Quality', 'Meter Trends', 'Meter Faults', 'Import / Export'] },
      { id: 'energy-faults', label: 'Energy Faults', path: '/uesg/sustainability', status: 'planned', l3: ['High Consumption', 'Unoccupied Consumption', 'Weekend Consumption', 'Peak Demand', 'Meter Offline', 'Meter Flatline', 'Energy Fault Evidence'] },
      { id: 'sustainability', label: 'Sustainability', path: '/uesg/sustainability', status: 'implemented', l3: ['Carbon Overview', 'ESG Metrics', 'Green Mark Support', 'Utility Baseline', 'Reduction Initiatives', 'Sustainability Evidence', 'ESG Reports'], mappedExistingModule: 'UesgSustainability' },
      { id: 'optimization', label: 'Optimization', path: '/uesg/sustainability', status: 'planned', l3: ['Energy Opportunities', 'Setpoint Review', 'Schedule Review', 'Equipment Efficiency', 'Anomaly Detection', 'Savings Estimate', 'Action Plan'] },
      { id: 'compliance', label: 'Compliance', path: '/uesg/sustainability', status: 'mapped', l3: ['Energy Compliance', 'ESG Compliance', 'Audit Evidence', 'Report Export', 'Submission Package', 'Historical Records'] },
    ],
  },
  {
    id: 'reports-compliance',
    label: 'Reports & Compliance',
    path: '/reports',
    icon: 'R',
    children: [
      { id: 'report-center', label: 'Report Center', path: '/reports', status: 'implemented', l3: ['Operations Reports', 'Alarm Reports', 'Fault Reports', 'Maintenance Reports', 'Energy Reports', 'Compliance Reports', 'Customer Demo Reports'], mappedExistingModule: 'ReportsView' },
      { id: 'export-center', label: 'Export Center', path: '/reports', status: 'implemented', l3: ['PDF Export', 'Excel Export', 'Evidence Bundle', 'Customer Handoff Package', 'Scheduled Exports', 'Export History', 'Export Audit'], mappedExistingModule: 'ReportsView' },
      { id: 'compliance-center', label: 'Compliance Center', path: '/reports', status: 'mapped', l3: ['IEC 62443 Evidence', 'ESG Evidence', 'Green Mark Evidence', 'Customer Acceptance', 'Audit Checklist', 'Compliance Gap', 'Compliance Reports'] },
      { id: 'evidence-library', label: 'Evidence Library', path: '/ucde/evidence', status: 'mapped', l3: ['UCDE Evidence', 'Decision Evidence', 'Fault Evidence', 'Maintenance Evidence', 'Server Precheck Evidence', 'Customer Delivery Evidence', 'Evidence Export'] },
    ],
  },
  {
    id: 'decision-evidence',
    label: 'Decision & Evidence',
    path: '/ucde/evidence',
    icon: 'V',
    children: [
      { id: 'decision-log', label: 'Decision Log', path: '/ucde/evidence', status: 'mapped', l3: ['Active Decisions', 'Decision Detail', 'Decision Owner', 'Decision Evidence', 'Approval Chain', 'Export'] },
      { id: 'ucde', label: 'UCDE', path: '/ucde/evidence', status: 'implemented', l3: ['Evidence Chain', 'Evidence Detail', 'Evidence Hash', 'Evidence Source', 'Evidence Validation', 'Evidence Export', 'Evidence Audit'], mappedExistingModule: 'EvidenceCenter' },
      { id: 'approval-center', label: 'Approval Center', path: '/ucde/evidence', status: 'planned', l3: ['Pending Approvals', 'Approved Items', 'Rejected Items', 'Approval Evidence', 'Approval Matrix', 'Approval History'] },
      { id: 'audit-trail', label: 'Audit Trail', path: '/system/audit-logs', status: 'implemented', l3: ['User Actions', 'System Actions', 'Configuration Changes', 'Evidence Changes', 'Export History', 'Audit Reports'], mappedExistingModule: 'AuditLogsView' },
    ],
  },
  {
    id: 'intelligence',
    label: 'Intelligence',
    path: '/one/nexus-ai/branch-audit',
    icon: 'I',
    children: [
      { id: 'nexusai', label: 'NexusAI', path: '/one/nexus-ai/branch-audit', status: 'implemented', l3: ['Insight Overview', 'Fault Insights', 'Energy Insights', 'Maintenance Insights', 'Risk Insights', 'Branch Audit', 'AI Evidence'], mappedExistingModule: 'NexusBranchAudit' },
      { id: 'recommendations', label: 'Recommendations', path: '/one/nexus-ai/branch-audit', status: 'innovation', l3: ['Recommended Actions', 'Prioritized Risks', 'Operational Suggestions', 'Maintenance Suggestions', 'Energy Suggestions', 'Decision Support', 'Confidence Evidence'] },
      { id: 'forecasting', label: 'Forecasting', path: '/one/nexus-ai/branch-audit', status: 'innovation', l3: ['Fault Forecast', 'Energy Forecast', 'Maintenance Forecast', 'Risk Forecast', 'Capacity Forecast', 'Model Evidence'] },
      { id: 'ai-governance', label: 'AI Governance', path: '/one/code/policy-gate', status: 'implemented', l3: ['AI Policy Gate', 'CODE Policy Gate', 'Model Usage', 'Human Approval', 'AI Audit', 'AI Limitations'], mappedExistingModule: 'CodePolicyGate' },
    ],
  },
  {
    id: 'digital-twin-graphics',
    label: 'Digital Twin & Graphics',
    path: '/one/airport/assets-topology',
    icon: 'T',
    children: [
      { id: 'graphics', label: 'Graphics', path: '/one/airport/assets-topology', status: 'planned', l3: ['Graphic Library', 'System Graphics', 'Equipment Graphics', 'Alarm Overlay', 'Trend Overlay', 'Graphic Evidence'] },
      { id: 'floor-plan', label: 'Floor Plan', path: '/one/airport/assets-topology', status: 'mapped', l3: ['Site Plan', 'Building Plan', 'Floor Plan', 'Zone Overlay', 'Asset Overlay', 'Alarm Overlay', 'Energy Overlay'] },
      { id: 'digital-twin', label: 'Digital Twin', path: '/one/airport/assets-topology', status: 'planned', l3: ['Twin Overview', 'Asset Twin', 'System Twin', 'Space Twin', 'Fault Impact Path', 'Scenario View', 'Twin Evidence'] },
      { id: 'topology', label: 'Topology', path: '/assets/topology', status: 'implemented', l3: ['System Topology', 'Network Topology', 'Asset Dependency', 'Edge / Link Topology', 'Data Flow', 'Impact Analysis'], mappedExistingModule: 'AssetsTopology' },
    ],
  },
  {
    id: 'security-life-safety',
    label: 'Security & Life Safety',
    path: '/one/airport/overview',
    icon: 'L',
    children: [
      { id: 'access-control', label: 'Access Control', path: '/one/airport/overview', status: 'planned', l3: ['Access Events', 'Door Status', 'Access Alarms', 'Access Exceptions', 'Access Evidence', 'Access Reports'] },
      { id: 'video-events', label: 'Video Events', path: '/one/airport/overview', status: 'planned', l3: ['CCTV Events', 'AI Video Events', 'Camera Health', 'Video-linked Alarms', 'Video Evidence', 'Event Review'] },
      { id: 'fire-life-safety', label: 'Fire & Life Safety', path: '/one/airport/overview', status: 'planned', l3: ['Fire Alarms', 'Fire System Status', 'Life Safety Events', 'Emergency Response', 'Fire Evidence', 'Compliance Reports'] },
      { id: 'security-incidents', label: 'Security Incidents', path: '/one/airport/overview', status: 'planned', l3: ['Active Security Incidents', 'Incident Detail', 'Related Access Events', 'Related Video Events', 'Response Actions', 'Closure Evidence'] },
    ],
  },
  {
    id: 'data-center-operations',
    label: 'Data Center Operations',
    path: '/one/airport/overview',
    icon: 'C',
    children: [
      { id: 'idc-overview', label: 'IDC Overview', path: '/one/airport/overview', status: 'planned', l3: ['Data Hall Health', 'Power Chain', 'Cooling Chain', 'Environmental Status', 'Capacity Risk', 'Critical Alarms', 'IDC Reports'] },
      { id: 'power', label: 'Power', path: '/one/airport/overview', status: 'planned', l3: ['UPS', 'PDU', 'Switchgear', 'Generator', 'Power Metering', 'Power Alarms', 'Power Trends'] },
      { id: 'cooling', label: 'Cooling', path: '/one/airport/overview', status: 'planned', l3: ['CRAH / CRAC', 'Chiller', 'Pump', 'Temperature Map', 'Humidity Map', 'Cooling Alarms', 'Cooling Efficiency'] },
      { id: 'capacity', label: 'Capacity', path: '/one/airport/overview', status: 'planned', l3: ['Rack Capacity', 'Power Capacity', 'Cooling Capacity', 'Space Capacity', 'Capacity Forecast', 'Capacity Reports'] },
      { id: 'idc-faults', label: 'IDC Faults', path: '/one/airport/fault-cases', status: 'planned', l3: ['Active IDC Faults', 'Impacted Racks', 'Impacted Systems', 'RCA', 'Recommended Actions', 'Evidence'] },
    ],
  },
  {
    id: 'integration-foundation',
    label: 'Integration Foundation',
    path: '/uedge/setup',
    icon: 'N',
    children: [
      { id: 'connectors', label: 'Connectors', path: '/uedge/setup', status: 'mapped', l3: ['Connector Registry', 'Protocol Mapping', 'OPC UA', 'BACnet', 'Modbus', 'API Connectors', 'Connector Evidence'] },
      { id: 'edge', label: 'EDGE', path: '/uedge/diagnostics', status: 'implemented', l3: ['Edge Gateway List', 'Edge Health', 'Edge Buffer', 'Edge Diagnostics', 'Edge Package Readiness', 'Edge Evidence'], mappedExistingModule: 'UedgeDiagnostics' },
      { id: 'link', label: 'LINK', path: '/uedge/diagnostics', status: 'mapped', l3: ['Link Gateway List', 'Link Queue', 'Link Delivery', 'Link DLQ', 'Link Diagnostics', 'Link Evidence'] },
      { id: 'contracts', label: 'Contracts', path: '/console/foundation-diagnostics/workspace', status: 'mapped', l3: ['API Contracts', 'DTO Schemas', 'Handoff Envelope', 'Versioning', 'Contract Evidence', 'Integration Checklist'] },
      { id: 'data-quality', label: 'Data Quality', path: '/assets/topology', status: 'planned', l3: ['Tag Quality', 'Mapping Quality', 'Missing Data', 'Duplicate Data', 'Stale Data', 'Quality Evidence', 'Correction Plan'] },
    ],
  },
  {
    id: 'engineer-workspace',
    label: 'Engineer Workspace',
    path: '/console/foundation-diagnostics/workspace',
    icon: 'W',
    children: [
      { id: 'deployment-readiness', label: 'Deployment Readiness', path: '/console/foundation-diagnostics/workspace', status: 'mapped', l3: ['Server Precheck Audit', 'Access Window Plan', 'Observation Plan', 'Remote Access Approval Packet', 'R5 Entry Gate', 'Deployment Blockers', 'Evidence Package'] },
      { id: 'foundation-diagnostics', label: 'Foundation Diagnostics', path: '/console/foundation-diagnostics/workspace', status: 'implemented', l3: ['Platform Diagnostics', 'Package Diagnostics', 'EDGE / LINK / DB Diagnostics', 'Contract Diagnostics', 'Healthcheck Preview', 'Risk Guardrails', 'Diagnostics Evidence'], mappedExistingModule: 'FoundationDiagnosticsWorkspace' },
      { id: 'customer-delivery', label: 'Customer Delivery', path: '/console/foundation-diagnostics/workspace', status: 'mapped', l3: ['Package Readiness', 'Offline Handoff', 'Acceptance Checklist', 'Customer Demo Pack', 'Installer Console', 'Handoff Decision', 'Delivery Evidence'] },
      { id: 'release-management', label: 'Release Management', path: '/console/foundation-diagnostics/workspace', status: 'mapped', l3: ['Local Release Index', 'Release Chain', 'Commit / Tag Registry', 'Validator Markers', 'Freeze Evidence', 'Release Gaps', 'Release Notes'] },
      { id: 'package-management', label: 'Package Management', path: '/console/operations', status: 'mapped', l3: ['Installed Packages', 'Entitled Packages', 'Enabled Packages', 'Visible Packages', 'Locked Packages', 'Package Health', 'Package Evidence'] },
      { id: 'server-precheck', label: 'Server Precheck', path: '/one/server/precheck', status: 'implemented', l3: ['R1 Environment Audit', 'R2 Access Window', 'R3 Observation Plan', 'R4 Remote Access Approval', 'R5 Actual Read-only Observation', 'Stop Conditions', 'Server Evidence'], mappedExistingModule: 'EngineerWorkspaceServerPrecheck' },
    ],
  },
  {
    id: 'administration',
    label: 'Administration',
    path: '/system',
    icon: 'X',
    children: [
      { id: 'users-roles', label: 'Users & Roles', path: '/system/permissions', status: 'implemented', l3: ['Users', 'Roles', 'Permissions', 'Teams', 'Role Mapping', 'Access Review', 'User Audit'], mappedExistingModule: 'PermissionListView' },
      { id: 'system-settings', label: 'System Settings', path: '/system/settings', status: 'implemented', l3: ['Site Settings', 'System Settings', 'Notification Settings', 'Evidence Settings', 'Report Settings', 'Feature Flags', 'Configuration Audit'], mappedExistingModule: 'SystemSettingsView' },
      { id: 'license-edition', label: 'License & Edition', path: '/system', status: 'planned', l3: ['Edition', 'Licensed Modules', 'Package Entitlement', 'Usage Limits', 'Expiry / Renewal', 'License Evidence'] },
      { id: 'audit-security', label: 'Audit & Security', path: '/system/audit-logs', status: 'implemented', l3: ['Login Audit', 'Action Audit', 'Configuration Audit', 'API Audit', 'Export Audit', 'Security Policy', 'Compliance Evidence'], mappedExistingModule: 'AuditLogsView' },
      { id: 'backup-recovery', label: 'Backup & Recovery', path: '/system', status: 'planned', l3: ['Backup Plan', 'Restore Plan', 'Recovery Evidence', 'Rollback Plan', 'DR Readiness', 'Recovery Reports'] },
    ],
  },
  {
    id: 'scenario-modules',
    label: 'Scenario Modules',
    path: '/one/airport/overview',
    icon: 'Q',
    children: [
      { id: 'umms-scenario', label: 'UMMS Scenario', path: '/one/umms/workspace', status: 'mapped', l3: ['Maintenance Overview', 'Work Order Flow', 'PM Flow', 'Fault-linked Maintenance', 'SLA Flow', 'Technician View', 'Maintenance Reports'] },
      { id: 'ufms-scenario', label: 'UFMS Scenario', path: '/one/airport/fault-cases', status: 'mapped', l3: ['Fault Overview', 'Alarm-to-Fault Flow', 'Correlation Flow', 'RCA Flow', 'Remediation Flow', 'Fault Evidence', 'Fault Reports'] },
      { id: 'uesg-scenario', label: 'UESG Scenario', path: '/uesg/sustainability', status: 'mapped', l3: ['Energy Overview', 'Meter-to-ESG Flow', 'Energy Fault Flow', 'Carbon Flow', 'Green Mark Evidence', 'ESG Reports', 'Optimization Actions'] },
      { id: 'airport-scenario', label: 'Airport Scenario', path: '/one/airport/overview', status: 'mapped', l3: ['Airport Operations', 'System Integration', 'Asset Context', 'Fault & Maintenance Flow', 'Energy & ESG Flow', 'Customer Demo Reports', 'Acceptance Evidence'] },
      { id: 'data-center-scenario', label: 'Data Center Scenario', path: '/one/airport/overview', status: 'mapped', l3: ['IDC Operations', 'Power Chain', 'Cooling Chain', 'Capacity Chain', 'IDC Fault Flow', 'IDC Maintenance Flow', 'IDC Evidence'] },
    ],
  },
]

export const fallbackMenuItems: AppMenuItem[] = domains.map((domain) => ({
  id: domain.id,
  label: domain.label,
  path: domain.path,
  icon: domain.icon,
  source: 'static',
  children: domain.children.map((child) => ({
    id: child.id,
    label: child.label,
    path: child.path,
    source: 'static',
    l3Items: l3Items(child.l3, child.mappedExistingModule, child.status),
  })),
}))
