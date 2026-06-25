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
      { id: 'dashboard-executive', label: 'Executive Dashboard', path: '/dashboard', status: 'mapped', l3: ['Portfolio Overview', 'Site Health', 'Critical Alarms', 'Open Faults', 'Open Work Orders', 'Energy Exceptions', 'ESG Snapshot', 'Service Risk', 'Customer Delivery View'] },
      { id: 'dashboard-operations', label: 'Operations Dashboard', path: '/dashboard', status: 'mapped', l3: ["Today's Operations", 'Live Situation', 'Risk Summary', 'System Availability', 'Fault Impact', 'Maintenance Status', 'Energy Status', 'Compliance Status'] },
      { id: 'dashboard-my', label: 'My Dashboard', path: '/dashboard', status: 'mapped', l3: ['My Tasks', 'My Alarms', 'My Work Orders', 'My Approvals', 'My Reports', 'My Evidence', 'Recent Activity'] },
      { id: 'dashboard-scenario', label: 'Scenario Dashboard', path: '/dashboard', status: 'mapped', l3: ['UMMS Overview', 'UFMS Overview', 'UESG Overview', 'Airport Scenario', 'Data Center Scenario', 'Customer Acceptance Flow'] },
    ],
  },
  {
    id: 'command-center',
    label: 'Command Center',
    path: '/console/operations',
    icon: 'C',
    children: [
      { id: 'operations-command-center', label: 'Operations Console', path: '/console/operations', status: 'implemented', l3: ['Operations Board', 'Live Situation', 'Event Stream', 'Active Tasks', 'Escalations', 'Service Impact', 'Evidence Timeline', 'Decision Log'], mappedExistingModule: 'PlatformOperationsDashboard' },
      { id: 'incident-management', label: 'Incident Management', path: '/console/operations', status: 'mapped', l3: ['Active Incidents', 'Incident Detail', 'Related Alarms', 'Related Faults', 'Impacted Assets', 'Response Actions', 'Communications', 'Closure Evidence'], mappedExistingModule: 'PlatformOperationsDashboard' },
      { id: 'shift-management', label: 'Shift Management', path: '/console/operations', status: 'mapped', l3: ['Shift Dashboard', 'Handover Notes', 'Open Items', 'Critical Watchlist', 'Operator Assignments', 'Shift Evidence'], mappedExistingModule: 'PlatformOperationsDashboard' },
      { id: 'service-impact', label: 'Service Impact', path: '/console/operations', status: 'mapped', l3: ['Customer Impact', 'Operational Impact', 'Affected Systems', 'Affected Assets', 'SLA Exposure', 'Recovery Priority', 'Impact Evidence'], mappedExistingModule: 'PlatformOperationsDashboard' },
      { id: 'decision-log', label: 'Decision Log', path: '/ucde/evidence', status: 'mapped', l3: ['Active Decisions', 'Decision Detail', 'Decision Owner', 'Decision Evidence', 'Approval Chain', 'Export'], mappedExistingModule: 'EvidenceCenter' },
    ],
  },
  {
    id: 'assets-locations',
    label: 'Assets & Locations',
    path: '/assets/topology',
    icon: 'A',
    children: [
      { id: 'site-portfolio', label: 'Site Portfolio', path: '/assets/topology', status: 'mapped', l3: ['Portfolio List', 'Site Health', 'Site Risk', 'Site Energy', 'Site Compliance', 'Site Reports'], mappedExistingModule: 'AssetsTopology' },
      { id: 'buildings-zones', label: 'Buildings / Floors / Zones', path: '/assets/topology', status: 'mapped', l3: ['Building List', 'Building Overview', 'Floor Plan', 'Zone List', 'Zone Conditions', 'Zone Assets', 'Occupancy View'], mappedExistingModule: 'AssetsTopology' },
      { id: 'space-mapping', label: 'Space Mapping', path: '/assets/topology', status: 'mapped', l3: ['Asset-to-Space Mapping', 'System-to-Space Mapping', 'Tag-to-Space Mapping', 'Floor Plan Binding', 'Mapping Gaps', 'Mapping Evidence'], mappedExistingModule: 'AssetsTopology' },
      { id: 'system-registry', label: 'System Registry', path: '/assets/topology', status: 'mapped', l3: ['System List', 'System Topology', 'System Health', 'System Alarms', 'System Faults', 'System Evidence', 'System Reports'], mappedExistingModule: 'AssetsTopology' },
      { id: 'asset-registry', label: 'Asset Registry', path: '/one/assets/context', status: 'implemented', l3: ['Asset List', 'Asset Detail', 'Asset Context', 'Asset Relationships', 'Asset Health', 'Asset History', 'Asset Evidence'], mappedExistingModule: 'AssetContext' },
      { id: 'equipment', label: 'Equipment', path: '/assets/topology', status: 'mapped', l3: ['Equipment List', 'Equipment Detail', 'Runtime Status', 'Maintenance History', 'Fault History', 'Spare / Vendor Info', 'Evidence'], mappedExistingModule: 'AssetsTopology' },
      { id: 'points-tags', label: 'Points & Tags', path: '/assets/topology', status: 'mapped', l3: ['Point List', 'Tag Mapping', 'Live Values', 'Point Quality', 'Point Trends', 'Mapping Gaps', 'Import / Export'], mappedExistingModule: 'AssetsTopology' },
      { id: 'controllers-gateways', label: 'Controllers & Gateways', path: '/uedge/diagnostics', status: 'mapped', l3: ['Controller List', 'Gateway List', 'Connectivity Status', 'Protocol Status', 'Edge Gateway Mapping', 'Link Gateway Mapping', 'Diagnostics'], mappedExistingModule: 'UedgeDiagnostics' },
      { id: 'asset-graph', label: 'Asset Graph', path: '/one/assets/context', status: 'implemented', l3: ['Relationship Graph', 'Dependency View', 'Impact Path', 'Upstream / Downstream', 'Asset Context Projection', 'Evidence Links', 'Data Quality'], mappedExistingModule: 'AssetContext' },
      { id: 'floor-plan-hmi', label: 'Floor Plan / HMI Map', path: '/one/airport/assets-topology', status: 'mapped', l3: ['Site Plan', 'Building Plan', 'Floor Plan', 'Zone Overlay', 'Asset Overlay', 'Alarm Overlay', 'Energy Overlay'] },
      { id: 'digital-twin', label: 'Digital Twin', path: '/one/airport/assets-topology', status: 'mapped', l3: ['Twin Overview', 'Asset Twin', 'System Twin', 'Space Twin', 'Fault Impact Path', 'Scenario View', 'Twin Evidence'] },
      { id: 'security-life-safety-assets', label: 'Security & Life Safety Assets', path: '/one/airport/overview', status: 'mapped', l3: ['Access Events', 'Door Status', 'CCTV Events', 'Fire System Status', 'Life Safety Events', 'Security Evidence', 'Compliance Reports'] },
      { id: 'data-center-assets', label: 'Data Center Assets', path: '/one/airport/overview', status: 'mapped', l3: ['Data Hall Health', 'Power Chain', 'Cooling Chain', 'Environmental Status', 'Capacity Risk', 'Critical Alarms', 'IDC Reports'] },
    ],
  },
  {
    id: 'work-management',
    label: 'Work Management',
    path: '/one/umms/workspace',
    icon: 'W',
    children: [
      { id: 'work-orders', label: 'Work Orders', path: '/one/umms/workspace', status: 'implemented', l3: ['Open Work Orders', 'Assigned Work Orders', 'Emergency Work Orders', 'Fault-linked Work Orders', 'Preventive Work Orders', 'Corrective Work Orders', 'Work Order Detail', 'Closure Evidence'], mappedExistingModule: 'UmmsMaintenance' },
      { id: 'preventive-maintenance', label: 'Preventive Maintenance', path: '/one/umms/workspace', status: 'implemented', l3: ['PM Calendar', 'PM Templates', 'PM Schedule', 'PM Checklist', 'PM Completion', 'PM Evidence', 'PM Reports'], mappedExistingModule: 'UmmsMaintenance' },
      { id: 'corrective-maintenance', label: 'Corrective Maintenance', path: '/one/umms/workspace', status: 'implemented', l3: ['Fault-linked Work Orders', 'Manual Work Orders', 'Technician Assignment', 'Action Tracking', 'Parts / Vendor Notes', 'Closure Review', 'History'], mappedExistingModule: 'UmmsMaintenance' },
      { id: 'engineer-workload', label: 'Engineer Workload', path: '/one/umms/workspace', status: 'implemented', l3: ['Engineer Calendar', 'Assignment Load', 'Skill / Discipline', 'Shift Availability', 'Escalation Owner', 'Next Due', 'Workload Evidence'], mappedExistingModule: 'UmmsMaintenance' },
      { id: 'sla-escalation', label: 'SLA & Escalation', path: '/one/umms/workspace', status: 'implemented', l3: ['SLA Dashboard', 'Breach Risk', 'Escalation Queue', 'Supervisor Review', 'Customer Impact', 'SLA Evidence', 'Aging Buckets'], mappedExistingModule: 'UmmsMaintenance' },
      { id: 'maintenance-analytics', label: 'Maintenance Analytics', path: '/one/umms/workspace', status: 'implemented', l3: ['MTTR', 'MTBF', 'Repeated Failures', 'Technician Load', 'Asset Reliability', 'Predictive Risk', 'Improvement Plan'], mappedExistingModule: 'UmmsMaintenance' },
      { id: 'inventory', label: 'Inventory', path: '/one/umms/workspace', status: 'mapped', l3: ['Spare Parts', 'Stock Availability', 'Material Requests', 'Critical Spares', 'Vendor Supply', 'Inventory Evidence'], mappedExistingModule: 'UmmsMaintenance' },
      { id: 'vendors', label: 'Vendors', path: '/one/umms/workspace', status: 'mapped', l3: ['Vendor List', 'Contract Coverage', 'Service Level', 'Warranty', 'Vendor Performance', 'Vendor Evidence'], mappedExistingModule: 'UmmsMaintenance' },
      { id: 'maintenance-configuration', label: 'Maintenance Configuration', path: '/one/umms/workspace', status: 'implemented', l3: ['Work Order Types', 'Priority Matrix', 'Assignment Rules', 'Checklist Templates', 'SLA Rules', 'Vendor / Team Setup', 'Evidence Rules'], mappedExistingModule: 'UmmsMaintenance' },
    ],
  },
  {
    id: 'faults-events',
    label: 'Faults & Events',
    path: '/one/airport/alarms-events',
    icon: 'F',
    children: [
      { id: 'alarm-console', label: 'Alarm Console', path: '/one/airport/alarms-events', status: 'mapped', l3: ['Active Alarms', 'Critical Alarms', 'Acknowledgement', 'Shelving', 'Suppression', 'Escalation', 'Operator Notes'] },
      { id: 'event-timeline', label: 'Event Timeline', path: '/one/airport/alarms-events', status: 'mapped', l3: ['Event Stream', 'Event Filters', 'Event Detail', 'Related Assets', 'Related Faults', 'Related Work Orders', 'Evidence Timeline'] },
      { id: 'alarm-rules', label: 'Alarm Rules', path: '/one/airport/alarms-events', status: 'mapped', l3: ['Priority Rules', 'Escalation Rules', 'Notification Rules', 'Suppression Rules', 'Routing Rules', 'Rule Evidence', 'Rule Audit'] },
      { id: 'alarm-analytics', label: 'Alarm Analytics', path: '/one/airport/alarms-events', status: 'mapped', l3: ['Alarm Volume', 'Alarm Flood', 'Repeated Alarms', 'Nuisance Alarms', 'Top Assets', 'Top Systems', 'SLA Impact'] },
      { id: 'fault-console', label: 'Fault Console', path: '/one/airport/fault-cases', status: 'mapped', l3: ['Active Faults', 'Critical Faults', 'Fault Detail', 'Correlation', 'Root Cause Analysis', 'Recommended Actions', 'Fault Evidence'] },
      { id: 'detection-correlation', label: 'Detection & Correlation', path: '/one/airport/fault-cases', status: 'mapped', l3: ['Detection Rules', 'Correlation Rules', 'Event Clustering', 'Related Alarms', 'Related Assets', 'Confidence Score', 'Rule Evidence'] },
      { id: 'diagnostics', label: 'Diagnostics', path: '/console/foundation-diagnostics/workspace', status: 'mapped', l3: ['Diagnostic Queue', 'System Diagnostics', 'Asset Diagnostics', 'OT / Network Diagnostics', 'Hardware Diagnostics', 'Diagnostic Evidence', 'Diagnostic History'] },
      { id: 'remediation', label: 'Remediation', path: '/one/airport/fault-cases', status: 'mapped', l3: ['Recommended Actions', 'Manual Actions', 'Work Order Creation', 'Escalation', 'SLA Tracking', 'Closure Notes', 'Closure Evidence'] },
      { id: 'fault-analytics', label: 'Fault Analytics', path: '/one/airport/fault-cases', status: 'mapped', l3: ['Fault Trends', 'Top Fault Types', 'Repeat Faults', 'MTTR', 'Downtime Impact', 'Reliability Score', 'Improvement Actions'] },
      { id: 'event-evidence', label: 'Event Evidence', path: '/ucde/evidence', status: 'mapped', l3: ['Evidence Chain', 'UCDE Trace', 'Operator Actions', 'Export Package', 'Audit Trail'], mappedExistingModule: 'EvidenceCenter' },
    ],
  },
  {
    id: 'energy-sustainability',
    label: 'Energy & Sustainability',
    path: '/uesg/sustainability',
    icon: 'E',
    children: [
      { id: 'energy-dashboard', label: 'Energy Dashboard', path: '/uesg/sustainability', status: 'implemented', l3: ['Consumption Overview', 'Demand / Peak', 'Energy Intensity', 'Meter Health', 'Energy Exceptions', 'Energy Forecast', 'Energy Reports'], mappedExistingModule: 'UesgSustainability' },
      { id: 'metering', label: 'Metering', path: '/uesg/sustainability', status: 'mapped', l3: ['Meter List', 'Meter Mapping', 'Meter Readings', 'Meter Quality', 'Meter Trends', 'Meter Faults', 'Import / Export'], mappedExistingModule: 'UesgSustainability' },
      { id: 'energy-faults', label: 'Energy Faults', path: '/uesg/sustainability', status: 'mapped', l3: ['High Consumption', 'Unoccupied Consumption', 'Weekend Consumption', 'Peak Demand', 'Meter Offline', 'Meter Flatline', 'Energy Fault Evidence'], mappedExistingModule: 'UesgSustainability' },
      { id: 'sustainability', label: 'Sustainability', path: '/uesg/sustainability', status: 'implemented', l3: ['Carbon Overview', 'ESG Metrics', 'Green Mark Support', 'Utility Baseline', 'Reduction Initiatives', 'Sustainability Evidence', 'ESG Reports'], mappedExistingModule: 'UesgSustainability' },
      { id: 'optimization', label: 'Optimization', path: '/uesg/sustainability', status: 'mapped', l3: ['Energy Opportunities', 'Setpoint Review', 'Schedule Review', 'Equipment Efficiency', 'Anomaly Detection', 'Savings Estimate', 'Action Plan'], mappedExistingModule: 'UesgSustainability' },
      { id: 'energy-compliance', label: 'Compliance', path: '/uesg/sustainability', status: 'mapped', l3: ['Energy Compliance', 'ESG Compliance', 'Audit Evidence', 'Report Export', 'Submission Package', 'Historical Records'], mappedExistingModule: 'UesgSustainability' },
      { id: 'data-center-energy', label: 'Data Center Energy', path: '/uesg/sustainability', status: 'mapped', l3: ['UPS', 'PDU', 'Switchgear', 'Generator', 'Power Metering', 'Power Alarms', 'Power Trends'], mappedExistingModule: 'UesgSustainability' },
    ],
  },
  {
    id: 'data-intelligence',
    label: 'Data & Intelligence',
    path: '/one/assets/context',
    icon: 'I',
    children: [
      { id: 'data-model', label: 'Data Model', path: '/assets/topology', status: 'mapped', l3: ['Canonical Object Model', 'Site / Building / Floor Model', 'System Model', 'Equipment Model', 'Point / Tag Model', 'Event Model', 'Work Order Model', 'Evidence Model', 'Data Dictionary', 'Schema Versioning'], mappedExistingModule: 'AssetsTopology' },
      { id: 'data-lake', label: 'Data Lake', path: '/console/foundation-diagnostics/workspace', status: 'mapped', l3: ['Raw Data Landing', 'Event Store', 'Time-series Store', 'File / Document Store', 'Evidence Store', 'Data Retention', 'Data Quality', 'Import / Export', 'Data Lineage'], mappedExistingModule: 'FoundationDiagnosticsWorkspace' },
      { id: 'asset-graph-intelligence', label: 'Asset Graph Intelligence', path: '/one/assets/context', status: 'implemented', l3: ['Relationship Graph', 'Dependency View', 'Impact Path', 'System-to-Asset Mapping', 'Asset-to-Point Mapping', 'Fault Impact Graph', 'Maintenance Impact Graph', 'Evidence-linked Graph'], mappedExistingModule: 'AssetContext' },
      { id: 'knowledge-base', label: 'Knowledge Base', path: '/one/nexus-ai/branch-audit', status: 'mapped', l3: ['Fault Knowledge', 'Maintenance Knowledge', 'Energy Knowledge', 'Asset Manuals', 'SOP Library', 'RCA Library', 'Troubleshooting Guides', 'Vendor Knowledge', 'Knowledge Evidence'], mappedExistingModule: 'NexusBranchAudit' },
      { id: 'ai-model-hub', label: 'AI Model Hub', path: '/one/nexus-ai/branch-audit', status: 'mapped', l3: ['Model Registry', 'Model Versioning', 'Fault Models', 'Energy Models', 'Maintenance Models', 'Risk Models', 'Model Evaluation', 'Human Approval', 'Model Evidence'], mappedExistingModule: 'NexusBranchAudit' },
      { id: 'nexusai', label: 'NexusAI Insights', path: '/one/nexus-ai/branch-audit', status: 'implemented', l3: ['Insight Overview', 'Fault Insights', 'Energy Insights', 'Maintenance Insights', 'Risk Insights', 'Branch Audit', 'AI Evidence'], mappedExistingModule: 'NexusBranchAudit' },
      { id: 'recommendations', label: 'Recommendations', path: '/one/nexus-ai/branch-audit', status: 'innovation', l3: ['Recommended Actions', 'Prioritized Risks', 'Operational Suggestions', 'Maintenance Suggestions', 'Energy Suggestions', 'Decision Support', 'Confidence Evidence'], mappedExistingModule: 'NexusBranchAudit' },
      { id: 'forecasting', label: 'Forecasting', path: '/one/nexus-ai/branch-audit', status: 'innovation', l3: ['Fault Forecast', 'Energy Forecast', 'Maintenance Forecast', 'Risk Forecast', 'Capacity Forecast', 'Model Evidence'], mappedExistingModule: 'NexusBranchAudit' },
      { id: 'data-evidence-center', label: 'Evidence Center', path: '/ucde/evidence', status: 'implemented', l3: ['Evidence Chain', 'Source Evidence', 'Decision Evidence', 'Fault Evidence', 'Maintenance Evidence', 'Energy Evidence', 'Report Evidence', 'Hash / Signature', 'Export Evidence'], mappedExistingModule: 'EvidenceCenter' },
      { id: 'data-governance', label: 'Data Governance', path: '/system/audit-logs', status: 'mapped', l3: ['Data Ownership', 'Data Classification', 'Data Quality Rules', 'Access Policy', 'Retention Policy', 'Lineage Review', 'Data Audit', 'Governance Evidence'], mappedExistingModule: 'AuditLogsView' },
    ],
  },
  {
    id: 'reports-documents',
    label: 'Reports & Documents',
    path: '/reports',
    icon: 'R',
    children: [
      { id: 'report-center', label: 'Report Center', path: '/reports', status: 'implemented', l3: ['Operations Reports', 'Alarm Reports', 'Fault Reports', 'Maintenance Reports', 'Energy Reports', 'Compliance Reports', 'Customer Delivery Reports'], mappedExistingModule: 'ReportsView' },
      { id: 'export-center', label: 'Export Center', path: '/reports', status: 'implemented', l3: ['PDF Export', 'Excel Export', 'Evidence Bundle', 'Customer Handoff Package', 'Scheduled Exports', 'Export History', 'Export Audit'], mappedExistingModule: 'ReportsView' },
      { id: 'compliance-center', label: 'Compliance Center', path: '/reports', status: 'mapped', l3: ['IEC 62443 Evidence', 'ESG Evidence', 'Green Mark Evidence', 'Customer Acceptance', 'Audit Checklist', 'Compliance Gap', 'Compliance Reports'], mappedExistingModule: 'ReportsView' },
      { id: 'document-library', label: 'Document Library', path: '/reports', status: 'mapped', l3: ['Document Register', 'Drawing Library', 'O&M Manuals', 'Method Statements', 'Test Reports', 'Vendor Documents', 'Revision History', 'Document Evidence'], mappedExistingModule: 'ReportsView' },
      { id: 'drawing-bim-documents', label: 'Drawing & BIM Documents', path: '/one/airport/assets-topology', status: 'mapped', l3: ['As-built Drawings', 'Single Line Diagrams', 'Control Schematics', 'Floor Plans', 'BIM References', 'Drawing Approval', 'Drawing Evidence'] },
      { id: 'asset-document-binding', label: 'Asset Document Binding', path: '/one/assets/context', status: 'mapped', l3: ['Asset-linked Documents', 'System-linked Documents', 'Equipment Manuals', 'Warranty Certificates', 'Spare Parts Documents', 'Maintenance Procedures', 'Document-to-Asset Evidence'], mappedExistingModule: 'AssetContext' },
      { id: 'handover-package-docs', label: 'Handover Package', path: '/reports', status: 'mapped', l3: ['Customer Handover Index', 'FAT / SAT Records', 'Commissioning Records', 'Training Records', 'Acceptance Checklist', 'Export Package', 'Handover Evidence'], mappedExistingModule: 'ReportsView' },
      { id: 'document-governance', label: 'Document Governance', path: '/ucde/evidence', status: 'mapped', l3: ['Version Control', 'Approval Workflow', 'Access Control', 'Retention Policy', 'Change Request', 'Document Audit Trail', 'Signature / Hash'], mappedExistingModule: 'EvidenceCenter' },
    ],
  },
  {
    id: 'governance-administration',
    label: 'Governance & Administration',
    path: '/system',
    icon: 'G',
    children: [
      { id: 'security-overview', label: 'Security Overview', path: '/console/operations', status: 'mapped', l3: ['Security Dashboard', 'Login Risk', 'Active Sessions', 'Privileged Users', 'Security Events', 'Policy Violations', 'Security Evidence'], mappedExistingModule: 'PlatformOperationsDashboard' },
      { id: 'identity-access', label: 'Identity & Access', path: '/system/permissions', status: 'implemented', l3: ['Users', 'Roles', 'Permissions', 'Teams', 'MFA / 2FA Policy', 'Session Policy', 'Access Review', 'Identity Audit'], mappedExistingModule: 'PermissionListView' },
      { id: 'users-roles', label: 'Users & Roles', path: '/system/permissions', status: 'implemented', l3: ['Users', 'Roles', 'Permissions', 'Teams', 'Role Mapping', 'Access Review', 'User Audit'], mappedExistingModule: 'PermissionListView' },
      { id: 'policy-governance', label: 'Policy Governance', path: '/one/code/policy-gate', status: 'implemented', l3: ['Security Policies', 'Approval Policies', 'Data Access Policies', 'AI Usage Policies', 'Evidence Policies', 'Retention Policies', 'Policy Exceptions', 'Policy Audit'], mappedExistingModule: 'CodePolicyGate' },
      { id: 'compliance-control', label: 'Compliance Control', path: '/reports', status: 'mapped', l3: ['IEC 62443 Control Mapping', 'ISO 27001 Mapping', 'Cybersecurity Checklist', 'OT Security Baseline', 'Data Protection Review', 'Audit Readiness', 'Compliance Evidence'], mappedExistingModule: 'ReportsView' },
      { id: 'governance-audit-trail', label: 'Audit Trail', path: '/system/audit-logs', status: 'implemented', l3: ['Login Audit', 'User Action Audit', 'Configuration Audit', 'Data Access Audit', 'Report Export Audit', 'AI Decision Audit', 'Evidence Audit', 'Tamper Review'], mappedExistingModule: 'AuditLogsView' },
      { id: 'risk-control-register', label: 'Risk & Control Register', path: '/console/operations', status: 'mapped', l3: ['Risk Register', 'Control Register', 'Open Findings', 'Mitigation Actions', 'Responsible Owners', 'Review Schedule', 'Risk Evidence'], mappedExistingModule: 'PlatformOperationsDashboard' },
      { id: 'cybersecurity-operations', label: 'Cybersecurity Operations', path: '/uedge/diagnostics', status: 'mapped', l3: ['Asset Vulnerability', 'Network Exposure', 'OT Security Events', 'Security Incident Queue', 'Threat Intelligence', 'Remediation Tracking', 'Cyber Evidence'], mappedExistingModule: 'UedgeDiagnostics' },
      { id: 'system-settings', label: 'System Settings', path: '/system/settings', status: 'implemented', l3: ['Site Settings', 'System Settings', 'Notification Settings', 'Evidence Settings', 'Report Settings', 'Feature Flags', 'Configuration Audit'], mappedExistingModule: 'SystemSettingsView' },
      { id: 'license-edition', label: 'License & Edition', path: '/system', status: 'mapped', l3: ['Edition', 'Licensed Modules', 'Package Entitlement', 'Usage Limits', 'Expiry / Renewal', 'License Evidence'] },
      { id: 'backup-recovery', label: 'Backup & Recovery', path: '/system', status: 'mapped', l3: ['Backup Plan', 'Restore Plan', 'Recovery Evidence', 'Rollback Plan', 'DR Readiness', 'Recovery Reports'] },
      { id: 'integration-foundation', label: 'Integration Foundation', path: '/uedge/setup', status: 'mapped', l3: ['Connectors', 'EDGE', 'LINK', 'Contracts', 'Data Quality', 'Connector Evidence', 'Integration Checklist'], mappedExistingModule: 'UedgeDiagnostics' },
      { id: 'engineer-tools', label: 'Engineer Tools', path: '/console/foundation-diagnostics/workspace', status: 'mapped', l3: ['Deployment Readiness', 'Foundation Diagnostics', 'Offline Handoff', 'Installer Console', 'Package Management', 'Server Precheck', 'Diagnostics Evidence'], mappedExistingModule: 'FoundationDiagnosticsWorkspace' },
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
